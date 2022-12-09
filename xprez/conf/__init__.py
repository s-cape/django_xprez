from django.conf import settings as user_settings

from . import defaults


class SettingsLoader:
    def __getattr__(self, name):
        try:
            return getattr(user_settings, name)
        except AttributeError:
            return getattr(defaults, name)


settings = SettingsLoader()
