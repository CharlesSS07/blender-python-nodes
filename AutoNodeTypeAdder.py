import types

import inspect

import bpy
import sys
import os

fdir = os.path.dirname(bpy.data.filepath)
if not fdir in sys.path:
    sys.path.append(fdir)

print('fd', bpy.data.filepath)
print(os.listdir())
print(sys.path)

pythonnodes = __import__("python-nodes")

# this next part forces a reload in case you edit the source after you first start the blender session
import imp
imp.reload(generate)




"""

copy pasted from python-nodes.py cause import wasn't working. figure out later and remove

"""

import bpy
from bpy.types import NodeTree, Node, NodeSocket
import numpy as np


# Implementation of custom nodes from Python

# TODO ideas:
# 1. autorename sockets based off of return type, numpy array could show dtype, shape

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class PythonCompositorTree(NodeTree):
    # Description string
    '''A custom node tree type that will show up in the editor type list'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonCompositorTreeType'
    # Label for nice name display
    bl_label = "Python Compositor Tree"
    # Icon identifier
    bl_icon = 'NODETREE'

# Custom socket type
class PyObjectSocket(NodeSocket):
    # Description string
    '''Python node socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PyObjectSocketType'
    # Label for nice name display
    bl_label = "Python Object Socket"
    
    # for storing the inputs and outputs of nodes without overriding default_value
    # we can't change value of _value_, but we can set what it points to if its a list
    _value_ = [None,]#: bpy.props.PointerProperty(type=bpy.types.Object, name='value', description='Pointer to object contained by the socket')
    
    def get_value(self):
        return self._value_[0]
    
    def set_value(self, value):
        self._value_[0] = value
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)
    

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class PythonCompositorTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == PythonCompositorTree.bl_idname

# Derived from the Node base type.
# Defines functionality of python node to only require that call is overloaded
class PythonNode(Node, PythonCompositorTreeNode):
    # === Basics ===
    # Description string
    '''Abstract python node.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonNode'
    # Label for nice name display
    bl_label = "Python Node"
    # Icon identifier
    bl_icon = 'SCRIPT'
    
    def is_connected_to_base(self):
        '''
        Return true if this node is connected to a node which is a "base" node.
        '''
        for k in self.outputs.keys():
            out = self.outputs[k]
            if out.is_linked:
                for o in out.links:
                    if o.is_valid and o.to_socket.node.is_connected_to_base():
                        return True
        return False
    
    def run(self):
        '''
        Do whatever calculations this node does. Take input from self.get_input
        and set outpus using self.set_output.
        '''
        pass
    
    def get_input(self, k, default_func):
        v = self.inputs[k]
        if v.is_linked and len(v.links)>0 and v.links[0].is_valid:
            o = v.links[0].from_socket
            value = o.get_value()
            return value
        v.set_value(None)
        return default_func()
    
    def set_output(self, k, v):
        self.outputs[k].set_value(v)
    
    def update_value(self):
        '''
        Called when a value changes (links, or node settings). Runs node unless
        this node is not connected to a base node. Propagates the nodes outputs
        to the linked nodes, and calls update_value on them.
        '''
        if self.is_connected_to_base():
            self.run()
            self.propagate()
    
    def update(self):
        '''
        Called when the node tree changes.
        '''
        self.update_value()
    
    def propagate(self):
        '''
        Pass this nodes outputs to nodes liked to outputs. Call update_value on
        them after passing.
        '''
        outputs = [self.outputs[k] for k in self.outputs.keys()]
        for out in outputs:
            if out.is_linked:
                for o in out.links:
                    if o.is_valid:
                        o.to_socket.set_value(out.get_value())
                        o.to_socket.node.update_value()

class PythonBaseNode(PythonNode):
    # === Basics ===
    # Description string
    '''Abstract python base node. Connected nodes will be run. Unconnected nodes are not run.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonBaseNode'
    # Label for nice name display
    bl_label = "Python Base Node"
    
    def is_connected_to_base(self):
        return True









def addNodeType(func):
    docstr = func.__doc__
    
    class nodeType(PythonNode):
        # === Basics ===
        # Description string
        ''' %s ''' % docstr
        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = func.__qualname__
        # Label for nice name display
        bl_label = func.__qualname__
        # Call signature
        try:
            sig = inspect.signature(func)
        except ValueError as ve:
            print('ignoring', ve)
            sig = 'temp'
        
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
    
    return nodeType





def addScope(scope):
    for key, obj in scope.copy().items():
        if callable(obj):
            print('callable', key, obj)
            addNodeType(obj)
        elif isinstance(obj, types.ModuleType):
            print('module', key, obj)
            addScope(vars(obj))
        else:
            print('other', key, obj)


addScope(vars())
