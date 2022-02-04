from collections import OrderedDict

from django.utils.module_loading import autodiscover_modules


class ContentTypeManager:

    def get(self, content_type):
        return self._registry[content_type]

    def all_as_list(self):
        return [content_type for key, content_type in self._registry.items()]

    def get_urls(self):
        urls = []
        for key, content in self._registry.items():
            urls += content.get_urls()
        return urls

    def _collect_media(self, media_class_name):
        from .utils import remove_duplicates

        js = []
        css = []
        for key, content in self._registry.items():
            media_class = getattr(content, media_class_name)
            js += list(getattr(media_class, 'js', []))
            css += list(getattr(media_class, 'css', []))
        return {
            'js': remove_duplicates(js),
            'css': remove_duplicates(css),
        }

    def admin_media(self):
        return self._collect_media('AdminMedia')

    def front_media(self):
        return self._collect_media('FrontMedia')

    def __init__(self):
        self._registry = OrderedDict()

    def register(self, content_class):
        self._registry[content_class.identifier()] = content_class

    def unregister(self, content_class):
        del self._registry[content_class.identifier()]


contents_manager = ContentTypeManager()


def autodiscover():
    autodiscover_modules('models', register_to=contents_manager)
