import types

import inspect

import bpy

import numpy

import pynodes
from pynodes import registry
from pynodes.nodes import PythonNode

import re

def add_node_type(func):
    # Doc string
    docstr = str(func.__doc__)

    # get the module and function name, for the category and node name
    if hasattr(func, '__module__') and hasattr(func, '__name__'):
        mod   = str(func.__module__)  # module name
        qname = str(func.__name__) # function name
    else: # its an object
        mod   = str(func.__class__.__module__) # module name
        qname = str(func.__class__.__name__ + ' object') # function name



    # getting the arguments to the function
    try:
        # use inspect to get call signature
        argstr = inspect.signature(func).__str__()[1:-1]

    except ValueError as ve:
        # parse docstring with regex to find call signature
        sigmatch = re.match(r'(\w+)\((.*)\)', docstr)
        if sigmatch is not None:
            qname = sigmatch.group(1)
            argstr = sigmatch.group(2)
        else:
            argstr = '...'

    arglist = argstr.split(',')

    class nodeType(PythonNode):
        docstr

        # module
        mmod = mod

        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = mmod + '.' + qname
        # Label for nice name display
        bl_label = mmod + '.' + qname


        def init(self, context):
            super().init(context)

            # add each of the function arguments as pins
            for i, arg in enumerate(arglist):
                if '=' in arg:
                    key, value = arg.split('=')
                    self.inputs.new(pynodes.PyObjectKWArgSocket.bl_idname, key.strip())
                    self.inputs[key.strip()].set_default(value.strip())
                elif arg.strip() == '...' or arg.strip()[0] == '*':
                    self.inputs.new(pynodes.PyObjectVarArgSocket.bl_idname, '*arg')
                else:
                    self.inputs.new(pynodes.PyObjectSocket.bl_idname, arg.strip())

            # add the output pin
            self.outputs.new(pynodes.PyObjectSocket.bl_idname, qname)

        def run(self):
            # collect the inputs
            posargs = list(filter( # get all the input pins that are var args or normal args
                        lambda input:
                            input.bl_idname  == pynodes.PyObjectVarArgSocket.bl_idname or
                            input.bl_idname == pynodes.PyObjectSocket.bl_idname,
                        self.inputs
                    ))
            kwargs = list(filter( # get all the input pins that are kwargs
                        lambda input: input.bl_idname == pynodes.PyObjectKWArgSocket.bl_idname,
                        self.inputs
                    ))

            # get the values
            posvals = list([input.get_value() for input in posargs])

            kwdict = dict({
                input.name: input.get_value()
                for input in kwargs
            })

            # pass inputs to the function and run it
            output = func(*posvals, **kwdict) # TODO: should this be ran in a scope somehow?

            # send the output of the function to the output socket
            self.set_output(qname, output)

    # register this node function
    registry.registerNodeType(nodeType)



added = []

def add_scope(scope):
    for key, obj in scope.copy().items():
        if any([obj is elem for elem in added]):
            pass
        else:
            added.append(obj)

            if callable(obj):
                add_node_type(obj)
            elif isinstance(obj, types.ModuleType):
                add_scope(vars(obj))
            else:
                pass # TODO: do something about constants or non-module non-callables?



def add_all_globals():
    add_scope(globals())
