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


LazyNamingThumbnailBackend = LazyNamingThumbnailBackend

__all__ = [
    "LazyNamingThumbnailBackend",
    "LazyNamingThumbnailBackend",
    "LazyThumbnailBackend",
    "NamingThumbnailBackend",
]
