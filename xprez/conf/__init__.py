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
    MERGE_SETTINGS = {
        "XPREZ_DEFAULTS",
        "XPREZ_CSS",
    }

    def __getattr__(self, name):
        default_value = getattr(defaults, name, None)
        user_value = getattr(user_settings, name, None)

        if name in self.MERGE_SETTINGS:
            if default_value is None:
                result = user_value or {}
            elif user_value is None:
                result = default_value
            else:
                result = deep_merge(default_value, user_value)
        elif user_value is not None:
            result = user_value
        else:
            result = default_value

        # Pre-merge XPREZ_CSS config keys with default
        if name == "XPREZ_CSS":
            result = self._preprocess_xprez_css(result)

        # Cache for next access
        setattr(self, name, result)
        return result

    def _preprocess_xprez_css(self, css_config):
        """Pre-merge module-specific keys with module.default fallback."""
        for config_key in ["module", "module_config"]:
            module_config = css_config.get(config_key, {})
            defaults = module_config.get("default", {})
            for key in list(module_config.keys()):
                if key == "default":
                    continue
                # Merge default into each module type
                for attr in defaults:
                    if attr not in module_config[key]:
                        module_config[key][attr] = defaults[attr]
                    else:
                        module_config[key][attr] = deep_merge(
                            defaults[attr], module_config[key][attr]
                        )
        return css_config


settings = SettingsLoader()
