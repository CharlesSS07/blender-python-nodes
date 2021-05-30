'''
Global list of registered classes with search names.
'''

__registry__ = {}

def register(clazz, full_name=None):
    global __registry__

    if full_name==None:
        full_name = clazz.bl_idname or 'unnamed:'+str(clazz)

    __registry__[full_name] = clazz

print('pynodes python node registry initialized')
