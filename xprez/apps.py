from django.apps import AppConfig, apps
from xprez.conf import settings


class XprezConfig(AppConfig):
    name = "xprez"

    def ready(self):
        self.autoregister_contents()

    def autoregister_contents(self):
        if settings.XPREZ_CONTENTS_AUTOREGISTER:
            from xprez.models import Content

            builtins = []
            custom = []
            for cls in apps.get_models():
                if (
                    issubclass(cls, Content)
                    and cls != Content
                    and not cls._meta.abstract
                ):
                    if cls._meta.app_label == "xprez":
                        builtins += [cls]
                    else:
                        custom += [cls]

            self._register(builtins, settings.XPREZ_CONTENTS_AUTOREGISTER_BUILTINS)
            self._register(custom, settings.XPREZ_CONTENTS_AUTOREGISTER_CUSTOM)

    @staticmethod
    def _register(contents, config):
        from xprez import contents_manager

        if config == "__all__":
            for content in contents:
                contents_manager.register(content)
        else:
            contents_dict = {content.identifier(): content for content in contents}
            for identifier in config:
                contents_manager.register(contents_dict[identifier])
