
def rgetattr(obj, attr, sep='.', default=None):
    attributes = attr.split(sep)
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            return default           
    return obj