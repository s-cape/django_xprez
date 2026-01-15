from django.conf import settings as user_settings

from . import defaults


def deep_merge(base, override):
    """Deep merge two dicts. Override values take precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class SettingsLoader:
    MERGE_SETTINGS = {"XPREZ_SECTION_CONFIG_DEFAULTS", "XPREZ_MODULE_CONFIG_DEFAULTS"}

    def __getattr__(self, name):
        default_value = getattr(defaults, name, None)
        user_value = getattr(user_settings, name, None)

        if name in self.MERGE_SETTINGS:
            if default_value is None:
                return user_value or {}
            if user_value is None:
                return default_value
            return deep_merge(default_value, user_value)

        if user_value is not None:
            return user_value
        return default_value


settings = SettingsLoader()
