import warnings
from collections import OrderedDict

from django.forms import Media
from django.templatetags.static import static
from django.utils.html import format_html

from xprez.conf import settings


class ModuleRegistry:
    def __init__(self):
        self._registry = OrderedDict()

    def get(self, content_type):
        return self._registry[content_type]

    def register(self, module_class):
        self._registry[module_class.class_content_type()] = module_class

    def unregister(self, module_class):
        del self._registry[module_class.class_content_type()]

    def get_admin_urls(self):
        urls = []
        for module in self._registry.values():
            urls += module.get_admin_urls()
        return urls

    @staticmethod
    def _get_class_media(module_class, media_class_name):
        data = getattr(module_class, media_class_name)
        css = getattr(data, "css", {})
        js = getattr(data, "js", [])
        if isinstance(css, tuple) or isinstance(css, list):
            warnings.warn(
                "{}.{}.css should be a dict, not list/tuple".format(
                    module_class,
                    media_class_name,
                ),
                DeprecationWarning,
                stacklevel=2,
            )
            css = {"all": css}
        return Media(css=css, js=js)

    def _collect_media(self, media_class_name, initial=None, modules=None):
        media = initial or Media()
        for module in self._get_available_modules(available_modules=modules):
            media += ModuleRegistry._get_class_media(module, media_class_name)
        return media

    def admin_media(self):
        return self._collect_media(
            "AdminMedia",
            initial=Media(
                js=(
                    "xprez/admin/libs/sortablejs/sortable-1.15.6.min.js",
                    format_html(
                        '<script type="module" src="{}"></script>',
                        static("xprez/admin/js/xprez.js"),
                    ),
                ),
                css={"all": ("xprez/styles/xprez-backend.css",)},
            ),
        )

    def front_media(self, container=None):
        if container is None:
            modules = None
        else:
            modules = None  # TODO: optimize
            # modules = {module.content_type for module in modules}

        return self._collect_media("FrontMedia", modules=modules)

    def _get_available_modules(self, available_modules=None):
        if available_modules is None:
            available_modules = settings.XPREZ_DEFAULT_AVAILABLE_MODULES
        if available_modules == "__all__":
            return self._registry.values()
        else:
            return [self.get(module) for module in available_modules]


module_registry = ModuleRegistry()
