from django.conf import settings as django_settings

XPREZ_CONTAINER_MODEL_CLASS = getattr(django_settings, 'XPREZ_CONTAINER_MODEL_CLASS', 'xprez.ContentsContainer')

XPREZ_CODE_TEMPLATES_DIR = getattr(django_settings, 'XPREZ_CODE_TEMPLATES_DIR', '')
XPREZ_CODE_TEMPLATES_PREFIX = getattr(django_settings, 'XPREZ_CODE_TEMPLATES_PREFIX', '')
XPREZ_USE_ABSOLUTE_URI = getattr(django_settings, 'XPREZ_USE_ABSOLUTE_URI', False)
XPREZ_BASE_URL = getattr(django_settings, 'XPREZ_BASE_URL', '')

