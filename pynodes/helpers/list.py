import numpy as np

def create(*args):
    return [*args]

def append(list, *args):
    lst = list.copy()
    for e in args:
        lst.append(e)
    return lst

def insert(list, index, object):
    lst = list.copy()
    lst.insert(index, object)
    return lst

def pop(list, index):
    lst = list.copy()
    return lst.pop(index)
