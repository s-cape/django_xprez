from django.conf import settings as django_settings

XPREZ_CONTAINER_MODEL_CLASS = getattr(django_settings, 'XPREZ_CONTAINER_MODEL_CLASS', 'xprez.ContentsContainer')
XPREZ_CODE_TEMPLATES_DIRS = getattr(django_settings, 'XPREZ_CODE_TEMPLATES_DIRS', [])
