from django.apps import AppConfig, apps

from xprez.conf import settings


class XprezConfig(AppConfig):
    name = "xprez"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        self.autoregister_modules()
        self._register_builtin_admins()

    @staticmethod
    def _register_builtin_admins():
        # Registered here (not via @admin.register) to avoid import-time cycles
        if not apps.is_installed("django.contrib.admin"):
            return

        from django.contrib import admin

        from xprez import models
        from xprez.admin.admin import TemplateContainerAdmin

        admin.site.register(models.TemplateContainer, TemplateContainerAdmin)

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
        from xprez import module_registry

        if config == "__all__":
            for module in modules:
                module_registry.register(module)
        else:
            modules_dict = {module.class_content_type(): module for module in modules}
            for module in config:
                if module in modules_dict:
                    module_registry.register(modules_dict[module])
