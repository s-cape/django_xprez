from sorl.thumbnail.base import ThumbnailBackend

from xprez.contrib.sorl_thumbnail.lazy.backend import (
    LazyThumbnailBackend,
    LazyThumbnailBackendMixin,
)
from xprez.contrib.sorl_thumbnail.naming import (
    NamingThumbnailBackend,
    NamingThumbnailBackendMixin,
)


class LazyNamingThumbnailBackend(
    LazyThumbnailBackendMixin, NamingThumbnailBackendMixin, ThumbnailBackend
):
    pass


__all__ = [
    "LazyNamingThumbnailBackend",
    "LazyThumbnailBackend",
    "LazyThumbnailBackendMixin",
    "NamingThumbnailBackend",
    "NamingThumbnailBackendMixin",
]
