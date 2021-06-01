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

            # check if varargs (...) are in the signature
            if '...' in argstr:
                args.append(('...', ''))
                print(qname, 'has varargs')
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
        bl_idname = mmod + '.' + qname
        # Label for nice name display
        bl_label = mmod + '.' + qname


        def init(self, context):
            super().init(context)

            # add each of the function arguments as pins
            for i, arg in enumerate(args):
                # add varargs socket
                if arg[0] == '...':
                    self.inputs.new(pynodes.PyObjectVarArgSocket.bl_idname, '*arg{}'.format(i))
                # add normal argument socket, if it doesn't have default (not a kwarg)
                elif arg[1] == '':
                    self.inputs.new(pynodes.PyObjectSocket.bl_idname, arg[0])
                # add keyword argument socket, with default value
                else:
                    self.inputs.new(pynodes.PyObjectKWArgSocket.bl_idname, arg[0])
                    self.inputs[arg[0]].set_default(arg[1])



            # add the output pin
            self.outputs.new(pynodes.PyObjectSocket.bl_idname, qname)

        def run(self):
            # collect the inputs
            funcargs = dict({
                arg[0]: self.get_input(arg[0], lambda:None)
                for arg in args
            })

            # pass inputs to the function and run it
            output = func(*funcargs) # TODO: should this be ran in a scope somehow?

            # send the output of the function to the output socket
            self.set_output(pynodes.PyObjectSocket.bl_idname, qname)

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
