import types

import inspect

import urllib.parse

import bpy

import numpy as np

import pynodes
from pynodes import registry
from pynodes.nodes import PythonNode

import re

def add_node_type(func):
    try:
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
            try:
                # basically find a word with a (, and if there is a matching () inside of it, ignore that ) and find the next )
                sigmatch = re.findall(r'(\w+)\((.*?\(.*?\).*?|.*?)\)', docstr)[0]
                qname = sigmatch[0]
                i = 0
                def count_repl(_):
                    nonlocal i
                    i+=1
                    return f'tuple_arg_{int(i):03d}'
                argstr = re.sub(r'\(.*?\)', count_repl, sigmatch[1])
            except Exception as e:
                argstr = '...'
            # r'(\w+)\((.*?)(\)\\n)', docstr) # worked for test cases
            # r'(\w+)\(((?:[^)(]+|(?P<R>))*)\)', docstr)
            # r'(\w+)\((.*)\)', docstr)
            # r'(\w+)\((.*)\)\\n', docstr)
            # r'(\w+)\((.*)\)', docstr) # original regex

        arglist = argstr.split(',')
    
        class nodeType(PythonNode):
            docstr

            # module
            mmod = mod

            # Optional identifier string. If not explicitly defined, the python class name is used.
            bl_idname = (mmod + '.' + qname)[:64]
            # Label for nice name display
            bl_label = mmod + '.' + qname

            def init(self, context):
                super().init(context)

                # add each of the function arguments as pins
                for i, arg in enumerate(arglist):
                    if '=' in arg:
                        key, value = arg.split('=')
                        self.inputs.new(pynodes.PyObjectKwArgSocket.bl_idname, key.strip())
                        self.inputs[key.strip()].set_default(value.strip())
                    elif arg.strip() == '...' or arg.strip().startswith('*'):
                        self.inputs.new(pynodes.PyObjectVarArgSocket.bl_idname, '*arg')
                    else:
                        self.inputs.new(pynodes.PyObjectSocket.bl_idname, arg.strip())

                # add the output pin
                self.outputs.new(pynodes.PyObjectSocket.bl_idname, qname)

            def draw_buttons_ext(self, context, layout):
                # open a link to documentation for this command on google (best I could hack together)
                row = layout.column()

                row.label(text='Documentation')

                google_search = f'documentation for {self.bl_label} (python)'

                row.operator(
                    "wm.url_open",
                    text="Google Documentation"
                ).url = f'http://www.google.com?q={urllib.parse.quote_plus(google_search)}'

                chatgpt_prompt = f'Explain how to use {self.bl_label} in python.'

                row.operator(
                    "wm.url_open",
                    text="ChatGPT Help"
                ).url = f'http://chat.openai.com?q={urllib.parse.quote_plus(chatgpt_prompt)}'

            def run(self):
                # collect the inputs
                posargs = [
                    input
                    for input in self.inputs if
                        input.bl_idname  == pynodes.PyObjectVarArgSocket.bl_idname or
                        input.bl_idname == pynodes.PyObjectSocket.bl_idname
                ]
                kwargs = [
                    input
                     for input in self.inputs if input.bl_idname == pynodes.PyObjectKwArgSocket.bl_idname
                ]

                # get the values
                posvals = [
                    self.get_input(input.name)
                    for input in posargs if not input.is_empty()
                ]

                kwdict = dict({
                    input.name: self.get_input(input.name)
                    for input in kwargs if not input.is_empty()
                })

                # pass inputs to the function and run it
                # print(posvals)
                # print(kwdict)
                output = func(*posvals, **kwdict) # TODO: should this be ran in a scope somehow?

                # send the output of the function to the output socket
                self.set_output(qname, output)

        # register this node function
        registry.registerNodeType(nodeType)
    except Exception as e:
        print(f'Could not register {func} as a node, skipping: ')
        print(e)

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
                # make nodes that are just for a modules constants, no inputs just outputs

def add_basic_nodes(): # adds recursivley, getting into all globals
    import numpy as np
    import bpy
    import os
    import sys
    import requests
    import pynodes.helpers
    scope = {
        'np':np,
        'bpy':bpy,
        'os':os,
        'sys':sys,
        'helpers':pynodes.helpers,
        'requests': requests
    }
    print(scope)
    add_scope(scope)

# def add_all_globals():
#     import sys
#     add_scope(sys.modules)
