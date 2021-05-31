import types

import inspect

import bpy

import numpy

from pynodes import registry
from pynodes.nodes import PythonNode


def add_node_type(func):
    # Doc string
    docstr = func.__doc__


    if hasattr(func, '__module__') and hasattr(func, '__name__'):
        mod   = str(func.__module__)  # module name
        qname = str(func.__name__) # function name
    else: # its an object
        mod   = str(func.__class__.__module__) # module name
        qname = str(func.__class__.__name__ + ' object') # function name

    # Call signature
    try:
        sig = inspect.signature(func)
    except ValueError as ve:
        print('ignoring', ve)
        sig = type('obj', (object,), {'parameters': [], 'return_annotation': type(func)})


    # print('sig', sig)

    class nodeType(PythonNode):
        # === Basics ===
        # Description string
        ''' %s ''' % docstr
        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = qname
        # Label for nice name display
        bl_label = qname

        # module
        mmod = mod


        def init(self, context):
            for param in sig.parameters:
                self.inputs.new(param.name, param.annotation)

            self.outputs.new(func.__name__, sig.return_annotation)

        def run(self):
            funcargs = {}

            for param in sig.parameters:
                funcargs[param.name] = self.getinput(param.name)

            output = func(*funcargs)

            self.set_output(sig.return_annotation, output)

    registry.registerNodeType(nodeType)



added = []

def add_scope(scope):
    for key, obj in scope.copy().items():
        if any([obj is elem for elem in added]):
            # print('skip')
            pass
        else:
            added.append(obj)

            if callable(obj):
                # print('callable', key)
                add_node_type(obj)
            elif isinstance(obj, types.ModuleType):
                # print('module', key)
                add_scope(vars(obj))
            else:
                # print('other', key)
                pass



def add_all_globals():
    add_scope(globals())
