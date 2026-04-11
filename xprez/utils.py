import copy
import secrets
import string

from .conf import settings


def copy_model(instance):
    """Return an unsaved shallow copy of a model instance, ready for insert."""
    inst = copy.copy(instance)
    inst.pk = None
    inst.id = None
    inst._state.adding = True
    return inst


def import_class(cls):
    if isinstance(cls, str):
        d = cls.rfind(".")
        classname = cls[d + 1 : len(cls)]
        m = __import__(cls[0:d], globals(), locals(), [classname])
        return getattr(m, classname)
    else:
        return cls


def class_content_type(cls):
    return "{}.{}".format(
        cls._meta.app_label,
        cls._meta.object_name,
    )


def build_absolute_uri(location, request=None):
    if settings.XPREZ_USE_ABSOLUTE_URI:
        if location.lower().startswith(("http://", "https://", "//")):
            if request:
                return request.build_absolute_uri(location)
            return "{}{}".format(settings.XPREZ_BASE_URL, location)
    return location


def random_string(length):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def truncate_with_ellipsis(string, length):
    if len(string) > length:
        return string[: length - 3] + "..."
    return string
