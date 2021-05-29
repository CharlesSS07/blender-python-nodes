'''
Global list of registered classes with search names.
'''

__registry__ = {}

def register(clazz, full_name):
    
    registry[full_name] = clazz

print('pynodes python node registry initialized')
