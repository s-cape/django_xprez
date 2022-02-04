from django.conf import settings as django_settings

from . import settings_default

XPREZ_DEFAULT_ALLOWED_CONTENTS = getattr(django_settings, 'XPREZ_DEFAULT_ALLOWED_CONTENTS', settings_default.DEFAULT_ALLOWED_CONTENTS)
XPREZ_DEFAULT_EXCLUDED_CONTENTS = getattr(django_settings, 'XPREZ_DEFAULT_EXCLUDED_CONTENTS', None)

XPREZ_CONTAINER_MODEL_CLASS = getattr(django_settings, 'XPREZ_CONTAINER_MODEL_CLASS', 'xprez.ContentsContainer')

XPREZ_CODE_TEMPLATES_DIR = getattr(django_settings, 'XPREZ_CODE_TEMPLATES_DIR', '')
XPREZ_CODE_TEMPLATES_PREFIX = getattr(django_settings, 'XPREZ_CODE_TEMPLATES_PREFIX', '')
XPREZ_USE_ABSOLUTE_URI = getattr(django_settings, 'XPREZ_USE_ABSOLUTE_URI', False)
XPREZ_BASE_URL = getattr(django_settings, 'XPREZ_BASE_URL', '')

XPREZ_CKEDITOR_CONFIG_SIMPLE = getattr(django_settings, 'XPREZ_CKEDITOR_CONFIG_SIMPLE', settings_default.XPREZ_CKEDITOR_CONFIG_SIMPLE)
XPREZ_CKEDITOR_CONFIG_FULL = getattr(django_settings, 'XPREZ_CKEDITOR_CONFIG_FULL', settings_default.XPREZ_CKEDITOR_CONFIG_FULL)
XPREZ_CKEDITOR_CONFIG_FULL_NO_INSERT_PLUGIN = getattr(django_settings, 'XPREZ_CKEDITOR_CONFIG_FULL_NO_INSERT_PLUGIN ', settings_default.XPREZ_CKEDITOR_CONFIG_FULL_NO_INSERT_PLUGIN)
