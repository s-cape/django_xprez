from django.conf import settings as django_settings

DEFAULT_ALLOWED_CONTENTS = [
    'mediumeditor',
    'quotecontent',
    'gallery',
    'downloadcontent',
    'video',
    'numberscontent',
    'featureboxes',
    'codeinput',
    'codetemplate',
    'textimage',
]

XPREZ_DEFAULT_ALLOWED_CONTENTS = getattr(django_settings, 'XPREZ_DEFAULT_ALLOWED_CONTENTS', DEFAULT_ALLOWED_CONTENTS)
XPREZ_DEFAULT_EXCLUDED_CONTENTS = getattr(django_settings, 'XPREZ_DEFAULT_EXCLUDED_CONTENTS', None)

XPREZ_CONTAINER_MODEL_CLASS = getattr(django_settings, 'XPREZ_CONTAINER_MODEL_CLASS', 'xprez.ContentsContainer')

XPREZ_CODE_TEMPLATES_DIR = getattr(django_settings, 'XPREZ_CODE_TEMPLATES_DIR', '')
XPREZ_CODE_TEMPLATES_PREFIX = getattr(django_settings, 'XPREZ_CODE_TEMPLATES_PREFIX', '')
XPREZ_USE_ABSOLUTE_URI = getattr(django_settings, 'XPREZ_USE_ABSOLUTE_URI', False)
XPREZ_BASE_URL = getattr(django_settings, 'XPREZ_BASE_URL', '')
