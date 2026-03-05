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
        keys = {m.module_key for m in self._registry.values()}

        if module_class.module_key in keys:
            raise ValueError(
                f"Module key '{module_class.module_key}' is already registered. "
            )

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

    def _collect_media(self, media_class_name, initial=None):
        media = initial or Media()
        for module in self.module_classes():
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
                css={"all": ("xprez/styles/xprez_backend.css",)},
            ),
        )

    def front_media(self, container=None):
        return self._collect_media("FrontMedia")

    def modules(self, include=None, exclude=None):
        if include in ["__all__", None]:
            result = list(self._registry.keys())
        else:
            result = list(include)
        if exclude:
            excluded = set(exclude)
            result = [ct for ct in result if ct not in excluded]
        return result

    def module_classes(self, include=None, exclude=None):
        return [self._registry[ct] for ct in self.modules(include, exclude)]

    def allowed_modules(self):
        return self.modules(
            include=settings.XPREZ_MODULES_ALLOWED,
            exclude=settings.XPREZ_MODULES_ALLOWED_EXCLUDE,
        )

    def allowed_module_classes(self):
        return self.module_classes(
            include=settings.XPREZ_MODULES_ALLOWED,
            exclude=settings.XPREZ_MODULES_ALLOWED_EXCLUDE,
        )

    def _add_menu_include_exclude(self):
        include = settings.XPREZ_MODULES_ADD_MENU
        if include is None:
            return settings.XPREZ_MODULES_ALLOWED, (
                list(settings.XPREZ_MODULES_ALLOWED_EXCLUDE)
                + list(settings.XPREZ_MODULES_ADD_MENU_EXCLUDE)
            )
        else:
            return include, settings.XPREZ_MODULES_ADD_MENU_EXCLUDE

    def add_menu_modules(self):
        include, exclude = self._add_menu_include_exclude()
        return self.modules(include=include, exclude=exclude)

    def add_menu_module_classes(self):
        include, exclude = self._add_menu_include_exclude()
        return self.module_classes(include=include, exclude=exclude)


module_registry = ModuleRegistry()
