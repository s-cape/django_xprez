import random

from .conf import settings


def import_class(cl):
    d = cl.rfind(".")
    classname = cl[d + 1 : len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname)


def remove_duplicates(list_):
    seen = set()
    seen_add = seen.add
    return [x for x in list_ if not (x in seen or seen_add(x))]


def build_absolute_uri(location, request=None):
    if settings.XPREZ_USE_ABSOLUTE_URI:
        if "http" not in location:
            if request:
                return request.build_absolute_uri(location)
            return "{}{}".format(settings.XPREZ_BASE_URL, location)
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
