from sorl.thumbnail.base import ThumbnailBackend

from xprez.contrib.sorl_thumbnail.lazy.backend import LazyThumbnailBackendMixin
from xprez.contrib.sorl_thumbnail.naming import NamingThumbnailBackendMixin


class LazyNamingThumbnailBackend(
    LazyThumbnailBackendMixin, NamingThumbnailBackendMixin, ThumbnailBackend
):
    pass
