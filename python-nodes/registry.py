'''
Global list of registered classes with search names.
'''

__registry__ = {}

def register(clazz, full_name):
    
    registry[clazz] = full_name
