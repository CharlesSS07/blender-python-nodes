import types

import inspect

import bpy

import numpy

pythonnodes = bpy.data.texts['python-nodes.py'].as_module()



def addNodeType(func):
    docstr = func.__doc__
    
    try: 
        qname = func.__qualname__
    except AttributeError as ae:
        qname = func.__class__.__name__
    
    class nodeType(pythonnodes.PythonNode):
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
        
        print('sig', sig)
        
        def init(self, context):
            for param in sig.parameters:
                self.inputs.new(param.name, param.annotation)
            
            self.outputs.new(func.__name__, sig.return_annotation)
            
            self.setup_post_init_hooks()
        
        def run(self):
            funcargs = {}
            
            for param in sig.parameters:
                funcargs[param.name] = self.getinput(param.name)
            
            output = func(*funcargs)
            
            self.set_output(sig.return_annotation, output)
    
#    pythonnodes.register(nodeType)



added = []

def addScope(scope):
    for key, obj in scope.copy().items():
        if any([obj is elem for elem in added]):
            print('skip')
        else: 
            added.append(obj)
        
            if callable(obj):
                print('callable', key)
                addNodeType(obj)
            elif isinstance(obj, types.ModuleType):
                print('module', key)
                addScope(vars(obj))
            else:
                print('other', key)


addScope(vars())
