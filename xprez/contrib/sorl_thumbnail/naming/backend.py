from pathlib import Path

from django.utils.text import slugify
from sorl.thumbnail.base import EXTENSIONS, ThumbnailBackend
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import serialize, tokey


class NamingThumbnailBackendMixin:
    def _get_thumbnail_filename(self, source, geometry_string, options):
        """Computes a human-readable destination filename using filename_stem."""
        key = tokey(source.key, geometry_string, serialize(options))
        path = "{}/{}/{}".format(key[:2], key[2:4], key)
        filename_stem = slugify(options.get("filename_stem") or Path(source.name).stem)
        return "{}{}/{}.{}".format(
            settings.THUMBNAIL_PREFIX,
            path,
            filename_stem,
            EXTENSIONS[options["format"]],
        )


class NamingThumbnailBackend(NamingThumbnailBackendMixin, ThumbnailBackend):
    pass
