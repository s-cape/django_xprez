import logging

from django.http import Http404, HttpResponseRedirect
from sorl.thumbnail import default

from xprez.contrib.sorl_thumbnail.lazy.backend import (
    LazyThumbnailBackendMixin,
    decode_thumbnail_payload,
    rebuild_source,
)

logger = logging.getLogger(__name__)


def lazy_thumbnail(request, payload, sig):
    try:
        args, kwargs = decode_thumbnail_payload(payload, sig)
    except (TypeError, ValueError) as e:
        raise Http404 from e

    args = list(args)
    if args:
        args[0] = rebuild_source(args[0])

    backend = default.backend
    try:
        if isinstance(backend, LazyThumbnailBackendMixin):
            thumbnail = backend.generate_thumbnail(*args, **kwargs)
        else:
            thumbnail = backend.get_thumbnail(*args, **kwargs)
    except Exception:
        logger.exception("Lazy thumbnail generation failed for %s", args)
        raise Http404 from None

    return HttpResponseRedirect(thumbnail.url)
