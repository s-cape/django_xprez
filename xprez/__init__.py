import warnings
from collections import OrderedDict

from django.forms import Media
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.module_loading import autodiscover_modules

from xprez.conf import settings


class ModuleManager:
    def get(self, content_type):
        return self._registry[content_type]

    def all_as_list(self):
        return [content_type for key, content_type in self._registry.items()]

    def get_urls(self):
        urls = []
        for module in self._registry.values():
            urls += module.get_urls()
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
        for module in self._get_allowed_modules(allowed_modules=modules):
            media += ModuleManager._get_class_media(module, media_class_name)
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

    def front_media(self, modules=None):
        return self._collect_media("FrontMedia", modules=modules)

    def __init__(self):
        self._registry = OrderedDict()

    def register(self, module_class):
        self._registry[module_class.class_content_type()] = module_class

    def unregister(self, module_class):
        del self._registry[module_class.class_content_type()]

    def _get_allowed_modules(
        self,
        allowed_modules=None,
        excluded_modules=None,
    ):
        if allowed_modules is None:
            allowed_modules = settings.XPREZ_DEFAULT_ALLOWED_MODULES
        if excluded_modules is None:
            excluded_modules = settings.XPREZ_DEFAULT_EXCLUDED_MODULES

        modules = []
        if allowed_modules == "__all__":
            modules = self.all_as_list()
        else:
            for module in allowed_modules:
                modules.append(self.get(module))
        if excluded_modules:
            for module in excluded_modules:
                module = self.get(module)
                if module in modules:
                    modules.remove(module)
        return modules


module_manager = ModuleManager()
modules_manager = module_manager  # Alias for consistency


def autodiscover():
    autodiscover_modules("models", register_to=module_manager)
