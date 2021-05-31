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
        sig = inspect.signature(func)
        # list of arguments: [ (argument name, default value), ... ]
        args = list([ (arg.name, arg.default) for arg in sig.parameters.values()])
    except ValueError as ve:
        # parse docstring with regex to find call signature
        sigmatch = re.match(r'(\w+)\((.*)\)', docstr)
        if sigmatch is not None:
            qname = sigmatch.group(1)
            argstr = sigmatch.group(2)
            # list of arguments: [ (argument name, default value), ... ]
            args = re.findall(r'(\w+)=?([^,]+)?', argstr)
        else:
            args = [
                ('...', '')
            ]

    class nodeType(PythonNode):
        # === Basics ===
        # Description string
        ''' %s ''' % docstr

        # module
        mmod = mod

        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = qname
        # Label for nice name display
        bl_label = qname


        def init(self, context):
            super().init(context)

            # add each of the function arguments as pins
            for arg in args:
                self.inputs.new(pynodes.PyObjectSocketType, arg[0])

            # add the output pin
            self.outputs.new(pynodes.PyObjectSocketType, qname)

        def run(self):
            # collect the inputs
            funcargs = dict({
                arg[0]: self.getinput(arg[0])
                for arg in args
            })

            # pass inputs to the function and run it
            output = func(*funcargs) # TODO: should this be ran in a scope somehow?

            # send the output of the function to the output socket
            self.set_output(pynodes.PyObjectSocketType, qname)

    # register this node function
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
