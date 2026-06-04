import base64
import binascii
import hashlib
import hmac
import json
import logging

from django.conf import settings as django_settings
from django.urls import reverse
from sorl.thumbnail import default
from sorl.thumbnail.base import ThumbnailBackend
from sorl.thumbnail.conf import defaults as default_settings
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import get_module_class, toint
from sorl.thumbnail.images import BaseImageFile, ImageFile
from sorl.thumbnail.parsers import parse_geometry

logger = logging.getLogger(__name__)


def _sign_payload(payload_str):
    return hmac.new(
        django_settings.SECRET_KEY.encode("utf-8"),
        payload_str.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:16]


def _b64_encode(s):
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode("ascii").rstrip("=")


def _b64_decode(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)).decode("utf-8")


def encode_thumbnail_payload(*args, **kwargs):
    """Encode args/kwargs into a signed (payload, sig) pair for use in a URL."""
    payload_str = json.dumps(
        {"args": list(args), "kwargs": kwargs},
        sort_keys=True,
        separators=(",", ":"),
    )
    return _b64_encode(payload_str), _sign_payload(payload_str)


def decode_thumbnail_payload(payload, sig):
    """Verify signature and decode URL payload back into (args, kwargs)."""
    try:
        payload_str = _b64_decode(payload)
    except (ValueError, UnicodeDecodeError, binascii.Error) as e:
        raise ValueError("Invalid thumbnail payload encoding.") from e

    if not hmac.compare_digest(_sign_payload(payload_str), sig):
        raise ValueError("Invalid thumbnail signature.")

    try:
        data = json.loads(payload_str)
        return data["args"], data["kwargs"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
        raise ValueError("Invalid thumbnail payload.") from e


def encode_source_ref(source):
    """Serialize an ImageFile to a (name, storage) ref that survives the URL."""
    return {"name": source.name, "storage": source.serialize_storage()}


def rebuild_source(source_ref):
    """Rebuild the source ImageFile with its storage; pass legacy string refs through."""
    if isinstance(source_ref, dict):
        storage = get_module_class(source_ref["storage"])()
        return ImageFile(source_ref["name"], storage)
    return source_ref


class LazyImageFile(BaseImageFile):
    """Placeholder for a not-yet-generated thumbnail; URL defers generation."""

    def __init__(self, url, size):
        self._url = url
        self.size = list(size)

    def exists(self):
        return False

    @property
    def url(self):
        return self._url


class LazyThumbnailBackendMixin:
    def get_thumbnail(self, file_, geometry_string, **options):
        if not file_:
            raise ValueError("falsey file_ argument in get_thumbnail()")

        source = ImageFile(file_)
        normalized = self._normalize_options(source, options)

        name = self._get_thumbnail_filename(source, geometry_string, normalized)
        thumbnail = ImageFile(name, default.storage)
        cached = default.kvstore.get(thumbnail)
        if cached:
            return cached

        size = self._predict_size(source, geometry_string, normalized)
        url = self._build_lazy_url(source, geometry_string, normalized)
        return LazyImageFile(url, size)

    def generate_thumbnail(self, file_, geometry_string, **options):
        return super(LazyThumbnailBackendMixin, self).get_thumbnail(
            file_, geometry_string, **options
        )

    def _normalize_options(self, source, options):
        # Keep this aligned with sorl.thumbnail.base.ThumbnailBackend.get_thumbnail().
        normalized_options = options.copy()

        if settings.THUMBNAIL_PRESERVE_FORMAT:
            normalized_options.setdefault("format", self._get_format(source))

        for key, value in self.default_options.items():
            normalized_options.setdefault(key, value)

        for key, attr in self.extra_options:
            value = getattr(settings, attr)
            if value != getattr(default_settings, attr):
                normalized_options.setdefault(key, value)

        return normalized_options

    def _build_lazy_url(self, source, geometry_string, options):
        payload, sig = encode_thumbnail_payload(
            encode_source_ref(source), geometry_string, **options
        )
        return reverse(
            "xprez:sorl_thumbnail_lazy:lazy_thumbnail",
            kwargs={"payload": payload, "sig": sig},
        )

    def _predict_size(self, source, geometry_string, options):
        try:
            src_w, src_h = self._get_source_dimensions(source)
        except Exception:
            logger.exception("Could not read dimensions for %s", source.name)
            geom = parse_geometry(geometry_string, 1.0)
            return [geom[0], geom[1]]

        ratio = src_w / src_h
        geom = parse_geometry(geometry_string, ratio)
        crop = options.get("crop")
        upscale = options.get("upscale", True)

        if crop:
            return [geom[0], geom[1]]

        factor = min(geom[0] / src_w, geom[1] / src_h)
        if not upscale:
            factor = min(factor, 1.0)

        if factor < 1 or upscale:
            return [toint(src_w * factor), toint(src_h * factor)]
        else:
            return [src_w, src_h]

    def _get_source_dimensions(self, source):
        cached = default.kvstore.get(source)
        if cached and cached.size:
            return cached.size

        source.set_size()
        return source.size


class LazyThumbnailBackend(LazyThumbnailBackendMixin, ThumbnailBackend):
    pass
