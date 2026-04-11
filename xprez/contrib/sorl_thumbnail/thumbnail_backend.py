from pathlib import Path

from django.utils.text import slugify
from sorl.thumbnail.base import EXTENSIONS, ThumbnailBackend
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import serialize, tokey


class NamingThumbnailBackendMixin:
    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        key = tokey(source.key, geometry_string, serialize(options))

        # make some subdirs
        subpath = f"{key[:2]}/{key[2:4]}/{key}"

        filename_stem = slugify(options.get("filename_stem") or Path(source.name).stem)
        ext = EXTENSIONS[options["format"]]

        return f"{settings.THUMBNAIL_PREFIX}{subpath}/{filename_stem}.{ext}"


class NamingThumbnailBackend(NamingThumbnailBackendMixin, ThumbnailBackend):
    pass
