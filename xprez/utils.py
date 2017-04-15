def import_class(cl):
    d = cl.rfind(".")
    classname = cl[d+1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname)


def remove_duplicates(list_):
    seen = set()
    seen_add = seen.add
    return [x for x in list_ if not (x in seen or seen_add(x))]