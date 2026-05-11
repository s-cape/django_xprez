from django.utils.module_loading import autodiscover_modules

from xprez import constants
from xprez.conf import settings
from xprez.registry import module_registry

__all__ = ["constants", "settings", "module_registry"]


def autodiscover():
    autodiscover_modules("models", register_to=module_registry)
