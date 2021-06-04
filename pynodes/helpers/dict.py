
def create(**kwargs):
    return kwargs

def set(dict, k, v):
    lst = dict.copy()
    lst[k] = v
    return lst

def get(dict, k):
    return dict[k]

def keys(dict):
    return dict.keys()
