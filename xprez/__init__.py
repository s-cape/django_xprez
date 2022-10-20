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

    def _collect_media(self, media_class_name, js_initial=[], css_initial=[]):
        from .utils import remove_duplicates

        js = list(js_initial)
        css = list(css_initial)

        for content in self._get_allowed_contents():
            media_class = getattr(content, media_class_name)
            js += list(getattr(media_class, "js", []))
            css += list(getattr(media_class, "css", []))
        return {
            "js": remove_duplicates(js),
            "css": remove_duplicates(css),
        }

    def admin_media(self):
        return self._collect_media(
            "AdminMedia",
            js_initial=[
                "xprez/admin/libs/jquery-sortable/source/js/jquery-sortable-min.js",
                "xprez/admin/libs/jquery_ui/jquery-ui.min.js",
                "xprez/admin/js/contents.js",
            ],
            css_initial=[
                "xprez/styles/xprez-backend.css",
            ],
        )

    def front_media(self):
        return self._collect_media("FrontMedia")

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
            from .settings import XPREZ_DEFAULT_ALLOWED_CONTENTS

            allowed_contents = XPREZ_DEFAULT_ALLOWED_CONTENTS
        if excluded_contents is None:
            from .settings import XPREZ_DEFAULT_EXCLUDED_CONTENTS

            excluded_contents = XPREZ_DEFAULT_EXCLUDED_CONTENTS

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
