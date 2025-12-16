import warnings
from collections import OrderedDict

from django.forms import Media
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.module_loading import autodiscover_modules

from xprez.conf import settings


class ModuleTypeManager:
    def get(self, module_type):
        return self._registry[module_type]

    def all_as_list(self):
        return [module_type for key, module_type in self._registry.items()]

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

    def _collect_media(self, media_class_name, initial=None, module_types=None):
        media = initial or Media()
        modules = self._get_allowed_modules(allowed_modules=module_types)
        for module in modules:
            media += ModuleTypeManager._get_class_media(module, media_class_name)
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

    def front_media(self, module_types=None):
        return self._collect_media("FrontMedia", module_types=module_types)

    def __init__(self):
        self._registry = OrderedDict()

    def register(self, module_class):
        self._registry[module_class.class_module_type()] = module_class

    def unregister(self, module_class):
        del self._registry[module_class.class_module_type()]

    def _get_allowed_modules(
        self,
        allowed_modules=None,
        excluded_modules=None,
    ):
        if allowed_modules is None:
            allowed_modules = settings.XPREZ_DEFAULT_ALLOWED_MODULES
        if excluded_modules is None:
            excluded_modules = settings.XPREZ_DEFAULT_EXCLUDED_MODULES

        module_types = []
        if allowed_modules == "__all__":
            module_types = self.all_as_list()
        else:
            for mt in allowed_modules:
                module_types.append(self.get(mt))
        if excluded_modules:
            for mt in excluded_modules:
                mt = self.get(mt)
                if mt in module_types:
                    module_types.remove(mt)
        return module_types


module_type_manager = ModuleTypeManager()
modules_manager = module_type_manager  # Alias for consistency


def autodiscover():
    autodiscover_modules("models", register_to=module_type_manager)
