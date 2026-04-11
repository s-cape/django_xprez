import copy
import random

from .conf import settings


def copy_model(instance):
    """Return an unsaved shallow copy of a model instance, ready for insert."""
    inst = copy.copy(instance)
    inst.pk = None
    inst.id = None
    inst._state.adding = True
    return inst


def import_class(cls):
    """Import a class from a dotted path string, or return cls if already a class."""
    if isinstance(cls, str):
        dot = cls.rfind(".")
        if dot == -1:
            raise ImportError(f"import_class requires a dotted path, got: {cls!r}")
        module_path, classname = cls[:dot], cls[dot + 1 :]
        m = __import__(module_path, globals(), locals(), [classname])
        return getattr(m, classname)
    return cls


def class_content_type(cls):
    return f"{cls._meta.app_label}.{cls._meta.object_name}"


def build_absolute_uri(location, request=None):
    if settings.XPREZ_USE_ABSOLUTE_URI:
        if not location.lower().startswith(("http://", "https://", "//")):
            if request:
                return request.build_absolute_uri(location)
            return f"{settings.XPREZ_BASE_URL}{location}"
    return location


def random_string(length, include_special_chars=False):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    if include_special_chars:
        chars += "!@#$%^&*(-_=+)"
    return "".join([random.choice(chars) for i in range(length)])


def truncate_with_ellipsis(string, length):
    if len(string) > length:
        return string[: length - 3] + "..."
    return string
