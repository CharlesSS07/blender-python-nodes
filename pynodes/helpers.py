
class list(object):

    @staticmethod
    def create(*args):
        return [*args]

    @staticmethod
    def append(list, *args):
        lst = list.copy()
        for e in args:
            lst.append(e)
        return lst

    @staticmethod
    def insert(list, index, object):
        lst = list.copy()
        lst.insert(index, object)
        return lst

    @staticmethod
    def pop(list, index):
        lst = list.copy()
        return lst.pop(index)

class dict(object):

    @staticmethod
    def create(**kwargs):
        return kwargs

    @staticmethod
    def set(dict, k, v):
        lst = dict.copy()
        lst[k] = v
        return lst

    @staticmethod
    def get(dict, k):
        return dict[k]

    @staticmethod
    def keys(dict):
        return dict.keys()

class array(object):

    @staticmethod
    def get(array, index):
        return array[index]
