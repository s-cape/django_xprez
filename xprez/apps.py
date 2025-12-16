from django.apps import AppConfig, apps

from xprez.conf import settings


class XprezConfig(AppConfig):
    name = "xprez"

    def ready(self):
        self.autoregister_modules()

    def autoregister_modules(self):
        if settings.XPREZ_MODULES_AUTOREGISTER:
            from xprez.models import Module

            builtins = []
            custom = []
            for cls in apps.get_models():
                if issubclass(cls, Module) and cls != Module and not cls._meta.abstract:
                    if cls._meta.app_label == "xprez":
                        builtins += [cls]
                    else:
                        custom += [cls]

            self._register(builtins, settings.XPREZ_MODULES_AUTOREGISTER_BUILTINS)
            self._register(custom, settings.XPREZ_MODULES_AUTOREGISTER_CUSTOM)

    @staticmethod
    def _register(modules, config):
        from xprez import module_type_manager

        if config == "__all__":
            for module in modules:
                module_type_manager.register(module)
        else:
            modules_dict = {module.class_module_type(): module for module in modules}
            for module_type in config:
                module_type_manager.register(modules_dict[module_type])
