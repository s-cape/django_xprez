import warnings
from collections import OrderedDict

from django.forms import Media
from django.utils.module_loading import autodiscover_modules
from xprez.conf import settings


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

    @staticmethod
    def _get_class_media(content_class, media_class_name):
        data = getattr(content_class, media_class_name)
        css = getattr(data, "css", {})
        js = getattr(data, "js", [])
        if isinstance(css, tuple) or isinstance(css, list):
            warnings.warn(
                "{}.{}.css should be a dict, not list/tuple".format(
                    content_class,
                    media_class_name,
                ),
                DeprecationWarning,
            )
            css = {"all": css}
        return Media(css=css, js=js)

    def _collect_media(self, media_class_name, initial=Media(), content_types=None):
        media = initial
        contents = self._get_allowed_contents(allowed_contents=content_types)
        for content in contents:
            media += ContentTypeManager._get_class_media(content, media_class_name)
        return media

    def admin_media(self):
        return self._collect_media(
            "AdminMedia",
            initial=Media(
                js=tuple(settings.XPREZ_JQUERY_INIT_MEDIA_JS)
                + (
                    "xprez/admin/libs/jquery-sortable/source/js/jquery-sortable-min.js",
                    "xprez/admin/libs/jquery_ui/jquery-ui.min.js",
                    "xprez/admin/js/contents.js",
                ),
                css={"all": ("xprez/styles/xprez-backend.css",)},
            ),
        )

    def front_media(self, content_types=None):
        return self._collect_media("FrontMedia", content_types=content_types)

    def __init__(self):
        self._registry = OrderedDict()

    def register(self, content_class):
        self._registry[content_class.identifier()] = content_class

    def unregister(self, content_class):
        del self._registry[content_class.identifier()]

    def _get_allowed_contents(
        self,
        allowed_contents=None,
        excluded_contents=None,
    ):
        if allowed_contents is None:
            allowed_contents = settings.XPREZ_DEFAULT_ALLOWED_CONTENTS
        if excluded_contents is None:
            excluded_contents = settings.XPREZ_DEFAULT_EXCLUDED_CONTENTS

        content_types = []
        if allowed_contents == "__all__":
            content_types = self.all_as_list()
        else:
            for ct in allowed_contents:
                content_types.append(self.get(ct))
        if excluded_contents:
            for ct in excluded_contents:
                ct = self.get(ct)
                if ct in content_types:
                    content_types.remove(ct)
        return content_types


contents_manager = ContentTypeManager()


def autodiscover():
    autodiscover_modules("models", register_to=contents_manager)
