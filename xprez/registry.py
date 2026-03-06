from collections import OrderedDict

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
