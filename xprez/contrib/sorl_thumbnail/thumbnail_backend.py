from pathlib import Path

from django.utils.text import slugify
from sorl.thumbnail.base import EXTENSIONS, ThumbnailBackend
from sorl.thumbnail.conf import settings
from sorl.thumbnail.helpers import serialize, tokey


class NamingThumbnailBackendMixin(object):
    def _get_thumbnail_filename(self, source, geometry_string, options):
        """
        Computes the destination filename.
        """
        key = tokey(source.key, geometry_string, serialize(options))
        # make some subdirs
        path = '%s/%s/%s' % (key[:2], key[2:4], key)
        # get filename_stem from options or use source name
        filename_stem = slugify(options.get('filename_stem') or Path(source.name).stem)
        # print('stem', filename_stem, Path(source.name).stem)
        return '%s%s/%s.%s' % (settings.THUMBNAIL_PREFIX, path, filename_stem, EXTENSIONS[options['format']])


class NamingThumbnailBackend(NamingThumbnailBackendMixin, ThumbnailBackend):
    pass
