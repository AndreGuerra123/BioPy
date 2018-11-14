
def rgetattr(obj, attr, sep='.', default=None):
    attributes = attr.split(sep)
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            return default           
    return obj

def minNum(lst):
    return min((b for b in lst if b is not None),default=None)
   
def maxNum(lst):
    return max((b for b in lst if b is not None),default=None)

def deltaEpoch(new,old):
    if None in [new,old]:
        return None
    else:
        return float((new-old).total_seconds())
    
