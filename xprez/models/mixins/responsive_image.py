import io
import urllib.request
from contextlib import ExitStack, contextmanager
from urllib.parse import urlparse

from django.conf import settings as django_settings
from django.core.files.storage import default_storage
from django.utils.functional import cached_property
from PIL import Image

from xprez import constants
from xprez.conf import settings


class ResponsiveImageParentMixin:
    """
    Mixin for modules that own a section and provide responsive widths and sizes.
    (E.g. GalleryModule)
    """

    def get_section_max_width_px(self):
        """Section max-width in px, or None for full-width."""
        width_choice = self.section.max_width_choice
        if width_choice == constants.MAX_WIDTH_FULL:
            return None
        elif width_choice == constants.MAX_WIDTH_CUSTOM:
            return self.section.max_width_custom or None
        else:
            max_width_values = settings.XPREZ_CSS["section"]["max_width"]["values"]
            return max_width_values.get(width_choice, {}).get(0)

    def get_own_columns(self, config):
        """
        Number of image columns this module lays out within a single section cell
        at the given module config. Default is 1 (single-image modules).
        Multi-item modules like GalleryModule override to return config.columns.
        """
        return 1

    def get_breakpoint_ranges(self):
        """
        Return [(max_width, effective_columns), ...] per breakpoint, combining
        section columns, module own columns, and module colspan.
        """
        breakpoints = settings.XPREZ_BREAKPOINTS
        section_configs = {
            c.css_breakpoint: c for c in self.section.get_configs_front()
        }
        own_configs = {c.css_breakpoint: c for c in self.get_configs_front()}
        current_section_cols = 1
        current_own_cols = 1
        current_colspan = 1
        result = []
        for bp_id in breakpoints:
            if bp_id in section_configs:
                current_section_cols = section_configs[bp_id].columns
            if bp_id in own_configs:
                current_own_cols = self.get_own_columns(own_configs[bp_id])
                current_colspan = own_configs[bp_id].colspan
            effective_columns = max(
                1,
                current_section_cols * current_own_cols // current_colspan,
            )
            result += [(breakpoints[bp_id]["max_width"], effective_columns)]
        return result

    def get_column_ranges(self):
        """
        Return (max_width_px, [(max_width, effective_columns), ...])
        collapsing consecutive duplicates.
        """
        max_width = self.get_section_max_width_px()
        ranges = []
        for bp_max_width, effective_columns in self.get_breakpoint_ranges():
            if not ranges or ranges[-1][1] != effective_columns:
                ranges += [(bp_max_width, effective_columns)]
        return max_width, ranges

    @cached_property
    def image_sizes(self):
        """HTML sizes attribute string for responsive images."""
        max_width, column_ranges = self.get_column_ranges()
        return self.build_image_sizes(max_width, column_ranges)

    @staticmethod
    def parse_crop_string(crop_str):
        """Parse a crop string like '3/2' into (3, 2), or return None if absent/invalid."""
        if not crop_str or "/" not in crop_str:
            return None
        try:
            num, den = crop_str.split("/", 1)
            return (int(num.strip()), int(den.strip()))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def build_image_sizes(max_width, column_ranges):
        """Build HTML sizes string from (max_width_px, [(max_width, cols), ...])."""

        def slot_value(effective_columns, bp_max_width):
            pct = round(100 / effective_columns, 2)
            vw_size = f"{int(pct) if pct == int(pct) else pct}vw"
            if max_width is None:
                return vw_size
            if bp_max_width is None or bp_max_width >= max_width:
                return f"{round(max_width / effective_columns)}px"
            return vw_size

        default_value = None
        media = []
        for bp_max_width, effective_columns in column_ranges:
            v = slot_value(effective_columns, bp_max_width)
            if bp_max_width is None:
                default_value = v
            else:
                media += [(bp_max_width, v)]

        # First matching media in the attribute wins. Sort (max-width: N) ascending
        # so the tightest (smallest N) is checked first; otherwise 1199 matches
        # before 767 and understates e.g. mobile width.
        media.sort(key=lambda t: t[0])
        parts = [f"(max-width: {bp}px) {v}" for bp, v in media]
        if default_value is not None:
            parts += [default_value]
        return ", ".join(parts)


class ResponsiveImageItemMixin:
    """
    Mixin for individual image items that produce srcset geometry strings.
    (E.g. GalleryItem)
    """

    def get_image_field(self):
        """Return the ImageField instance for this item (e.g. self.file)."""
        raise NotImplementedError

    def get_image_aspect_ratio(self):
        """Return (numerator, denominator) for the image aspect ratio."""
        raise NotImplementedError

    @cached_property
    def srcset_geometries(self):
        """List of 'WxH' geometry strings for srcset, capped at image's natural width."""
        try:
            cap_width = self.get_image_field().width or None
        except (AttributeError, OSError):
            cap_width = None
        numerator, denominator = self.get_image_aspect_ratio()
        return self.build_srcset_geometries(
            settings.XPREZ_SRCSET_WIDTHS, numerator, denominator, cap_width
        )

    @staticmethod
    def build_srcset_geometries(
        widths, aspect_numerator, aspect_denominator, cap_width=None
    ):
        """Return list of 'WxH' geometry strings, capped at cap_width if given."""
        if cap_width is None:
            final = list(widths)
        else:
            final = [w for w in widths if w < cap_width] + [cap_width]
        return [
            f"{w}x{round(w * aspect_denominator / aspect_numerator)}" for w in final
        ]


class ResponsiveImageSourcesMixin:
    """
    Mixin for modules whose breakpoint configs each carry a crop string.
    Produces the source list for <picture>/<img> art-direction rendering.

    Requires build_srcset_geometries (from ResponsiveImageItemMixin).
    Subclasses must implement get_config_crop(config).
    """

    def get_config_crop(self, config):
        """Return the crop string (e.g. '3/2') for a config instance, or None."""
        raise NotImplementedError

    @cached_property
    def media_image_sources(self):
        """
        Return a list of dicts for <picture> rendering, ordered for correct browser
        matching (smallest max_width first; base/fallback last with max_width=None).

        Each dict: max_width (int or None), thumbnail_crop (str), geometries (list).
        Non-base entries with a crop differing from the base become <source> elements;
        the final entry (max_width=None) is always the <img> fallback.
        """
        breakpoints = settings.XPREZ_BREAKPOINTS
        saved = {c.css_breakpoint: c for c in self.get_configs_front()}

        base_config = saved.get(0)
        base_crop_str = self.get_config_crop(base_config) if base_config else None
        base_crop = self.parse_crop_string(base_crop_str)

        non_base_bp_ids = sorted(
            [bp_id for bp_id in saved if bp_id != 0],
            key=lambda bp_id: breakpoints[bp_id]["max_width"],
        )

        sources = []
        for bp_id in non_base_bp_ids:
            config = saved[bp_id]
            crop = self.parse_crop_string(self.get_config_crop(config))
            if crop == base_crop:
                continue
            num, den = crop if crop else (1, 1)
            sources += [
                {
                    "max_width": breakpoints[bp_id]["max_width"],
                    "thumbnail_crop": "center" if crop else "",
                    "geometries": self.build_srcset_geometries(
                        settings.XPREZ_SRCSET_WIDTHS, num, den
                    ),
                }
            ]

        num, den = base_crop if base_crop else (1, 1)
        sources += [
            {
                "max_width": None,
                "thumbnail_crop": "center" if base_crop else "",
                "geometries": self.build_srcset_geometries(
                    settings.XPREZ_SRCSET_WIDTHS, num, den
                ),
            }
        ]
        return sources


class ResponsiveImageMixin(ResponsiveImageParentMixin, ResponsiveImageItemMixin):
    """
    Combined mixin for when parent and item are the same object.
    (E.g. TextModule, VideoModule)
    """


class _NaturalSize:
    """Adapter exposing .width for ResponsiveImageItemMixin."""

    def __init__(self, width):
        self.width = width


class InlineResponsiveImage(ResponsiveImageItemMixin):
    """Responsive geometry for an image referenced by URL (e.g. a CKEditor inline
    image). Borrows image_sizes from a parent ResponsiveImageParentMixin module.
    """

    def __init__(self, src, responsive_image_parent):
        self.src = src
        self.responsive_image_parent = responsive_image_parent

    @cached_property
    def local_storage_path(self):
        """Relative storage path for local media URLs, or None for remote URLs."""
        media_url = django_settings.MEDIA_URL
        path = urlparse(self.src).path
        if not media_url or not path.startswith(media_url):
            return None
        return path[len(media_url) :]

    @property
    def sorl_src(self):
        """Source to pass to sorl-thumbnail: storage path for local, URL for remote."""
        return self.local_storage_path or self.src

    @cached_property
    def natural_size(self):
        """(width, height) of the source image, or (None, None) if unavailable."""
        try:
            with self.open_source() as f:
                with Image.open(f) as im:
                    return im.size
        except Exception:
            return (None, None)

    @property
    def image_sizes(self):
        return self.responsive_image_parent.image_sizes

    def get_image_field(self):
        width, _ = self.natural_size
        if width is None:
            raise AttributeError("natural size unavailable")
        return _NaturalSize(width)

    def get_image_aspect_ratio(self):
        width, height = self.natural_size
        return (width or 1, height or 1)

    @contextmanager
    def open_source(self):
        """Open the source image as a file-like, trying local storage then HTTP.
        Raises FileNotFoundError if neither source can be opened.
        """
        with ExitStack() as stack:
            for opener in (self._open_local, self._open_remote):
                try:
                    f = stack.enter_context(opener())
                    break
                except Exception:
                    pass
            else:
                raise FileNotFoundError(f"Cannot open {self.src!r}")
            yield f

    @contextmanager
    def _open_local(self):
        """Open via Django storage. Raises if URL isn't local media."""
        rel_path = self.local_storage_path
        if rel_path is None:
            raise ValueError(f"{self.src!r} is not a local media URL")
        with default_storage.open(rel_path) as f:
            yield f

    @contextmanager
    def _open_remote(self):
        """Open via HTTP. Raises if URL isn't HTTP(S)."""
        if not self.src.lower().startswith(("http://", "https://")):
            raise ValueError(f"{self.src!r} is not an HTTP(S) URL")
        req = urllib.request.Request(self.src, headers={"User-agent": ""})
        with urllib.request.urlopen(req) as resp:
            yield io.BytesIO(resp.read())
