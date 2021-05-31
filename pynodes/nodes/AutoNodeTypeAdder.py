import types

import inspect

import bpy

import numpy

<<<<<<< HEAD:pynodes/AutoNodeTypeAdder.py
=======
<<<<<<< HEAD:pynodes/nodes/AutoNodeTypeAdder.py
from pynodes import registry
from pynodes.nodes import PythonNode
=======
>>>>>>> 49e4c650ea426d707e98ccd2725d5f4d6b2ff6a6:pynodes/nodes/AutoNodeTypeAdder.py
from pynodes import pythonnodes, registry

>>>>>>> main:pynodes/AutoNodeTypeAdder.py


def addNodeType(func):
    docstr = func.__doc__

    try:
        qname = func.__qualname__
    except AttributeError as ae:
        qname = func.__class__.__name__

<<<<<<< HEAD:pynodes/AutoNodeTypeAdder.py
=======
<<<<<<< HEAD:pynodes/nodes/AutoNodeTypeAdder.py
    class nodeType(PythonNode):
=======
>>>>>>> 49e4c650ea426d707e98ccd2725d5f4d6b2ff6a6:pynodes/nodes/AutoNodeTypeAdder.py
    class nodeType(pythonnodes.PythonNode):
>>>>>>> main:pynodes/AutoNodeTypeAdder.py
        # === Basics ===
        # Description string
        ''' %s ''' % docstr
        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = qname
        # Label for nice name display
        bl_label = qname
        # Call signature
        try:
            sig = inspect.signature(func)
        except ValueError as ve:
            print('ignoring', ve)
            sig = type('obj', (object,), {'parameters': [], 'return_annotation': type(func)})

        # print('sig', sig)

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

<<<<<<< HEAD:pynodes/AutoNodeTypeAdder.py
    registry.registerNodeType(nodeType, qname)
=======
<<<<<<< HEAD:pynodes/nodes/AutoNodeTypeAdder.py
    registry.registerNodeType(nodeType)
=======
    registry.registerNodeType(nodeType, qname)
>>>>>>> main:pynodes/AutoNodeTypeAdder.py
>>>>>>> 49e4c650ea426d707e98ccd2725d5f4d6b2ff6a6:pynodes/nodes/AutoNodeTypeAdder.py



added = []

def addScope(scope):
    for key, obj in scope.copy().items():
        if any([obj is elem for elem in added]):
            # print('skip')
            pass
        else:
            added.append(obj)

            if callable(obj):
                # print('callable', key)
                addNodeType(obj)
            elif isinstance(obj, types.ModuleType):
                # print('module', key)
                addScope(vars(obj))
            else:
                # print('other', key)
                pass



def addAllGlobals():
    addScope(globals())
