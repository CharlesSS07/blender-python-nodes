bl_info = {
    "name": "Python Nodes",
    "description": "The power of python, brought to you through blender nodes.",
    "author": "Charles M. S. Strauss<charles.s.strauss@gmail.com>, and Robert R. Strauss<robert.r.strauss@icloud.com>",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "Console",
    "warning": "Requires user has tensorflow, pytorch installed using blender python environment manager TODO: include link", # used for warning icon and text in addons panel
    "support": "COMMUNITY",
    "category": "Nodes",
}

import bpy
from bpy.types import NodeTree, Node, NodeSocket
import numpy as np

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

def get_node_execution_scope():
    '''
    Returns the scope to be used when evaluating python node inputs.
    Quickly get a bunch of constants, can be extracted and modified to
    have more constants or packages later. Note that many python
    builtins are already in the scope by default, such as int or str.
    '''
    import numpy as np
    import bpy
    import os
    import sys
    # tensorflow, ffmpeg, gmic qt, osl, PIL...
    return {
        'pi':np.pi,
        'tau':np.pi*2,
        'e':np.e,
        'np':np,
        'bpy':bpy,
        'os':os,
        'sys':sys
    }

node_execution_scope = get_node_execution_scope()

# Custom socket type
class AbstractPyObjectSocket(NodeSocket):
    # Description string
    '''General python node socket type'''


    # for storing the inputs and outputs of nodes without overriding default_value
    # we can't change value of _value_, but we can set what it points to if its a list
    _value_ = [None,]#: bpy.props.PointerProperty(type=bpy.types.Object, name='value', description='Pointer to object contained by the socket')

    # blender properties have to be wrapped in this so they are inherited in a way that blender properties can access them
    class Properties:
        argvalue : bpy.props.StringProperty(
            name = 'argvalue',
            description = 'manually input value to argument for function',
            default = '',
            update = lambda s,c: s.argvalue_updated()
        )

    def argvalue_updated(self):
        pass

    def get_value(self):
        if self.is_linked:
            return self._value_[0]
        else:
            return eval(self.argvalue, node_execution_scope)

    def set_value(self, value):
        self._value_[0] = value

    def is_empty(self):
        return (not self.is_linked) and (self.argvalue=='')

    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)

    def draw(self, context, layout, node, text):
        layout.label(text=text)
        # give default value selector when not linked
        if not self.is_linked and not self.is_output:
            layout.prop(self, 'argvalue', text='')

class PyObjectSocket(AbstractPyObjectSocket.Properties, AbstractPyObjectSocket):
    ''' Python node socket type for normal function arguments and outputs '''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PyObjectSocketType'
    # Label for nice name display
    bl_label = "Python Object Socket"

class PyObjectVarArgSocket(AbstractPyObjectSocket.Properties, AbstractPyObjectSocket):
    # Description string
    '''Python node socket type for variable arguments (varargs, *args)'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PyObjectVarArgSocketType'
    # Label for nice name display
    bl_label = 'Python *args Object Socket'

    def __init__(self):
        super().__init__()
        # pin shape
        self.display_shape = 'DIAMOND'
        self.name = self.identifier
        # socket must be indexible using name.
        # therefore force name to be unique like identifier
        self.node.subscribe_to_update(self.node_updated)
        # subscribe socket to node update events

    # var args nodes automatically remove or add more of themselves as they are used
    def node_updated(self):
        # print('node_updated', self.node, self)
        self.update()

    def argvalue_updated(self):
        # print('argvalue_updated', self.node, self)
        self.update()

    def update(self):
        emptyvarargpins = 0
        # count the number of non-linked, empty sibling vararg pins
        for input in self.node.inputs:
            if input.bl_idname == PyObjectVarArgSocket.bl_idname:
                if input.is_empty():
                    emptyvarargpins+=1

        # there is at least one other empty non-linked one (other than self)
        if emptyvarargpins > 1:
            # remove self if empty and not linked
            self.node.unsubscribe_to_update(self)
            self.node.inputs.remove(self)
        # create new pin if there is not enough
        elif emptyvarargpins < 1:
            self.node.inputs.new(PyObjectVarArgSocket.bl_idname, '*arg')

class PyObjectKWArgSocket(AbstractPyObjectSocket.Properties, AbstractPyObjectSocket):
    # Description string
    '''Python node socket type for keyword argumnets'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PyObjectKWArgSocketType'
    # Label for nice name display
    bl_label = 'Python *kwargs Object Socket'

    def __init__(self):
        super().__init__()
        # pin shape
        self.display_shape = 'SQUARE'

    # method to set the default value defined by the kwargs
    def set_default(self, value):
        self.argvalue = value

### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type

class PythonCompositorNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == PythonCompositorTree.bl_idname

class PythonCompositorOperator(bpy.types.Operator):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == PythonCompositorTree.bl_idname

class NODE_MT_add_test_node_tree(PythonCompositorOperator):
    """Programmatically create node tree for testing, if it dosen't already exist."""
    bl_idname = "node.add_test_node_tree"
    bl_label = "Add test node tree."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        if bpy.data.node_groups.get('Python Node Tree Test', False)==False:
            bpy.ops.node.new_node_tree(
                type='PythonCompositorTreeType',
                name='Python Node Tree Test'
            )
            test_node_tree = bpy.data.node_groups.get('Python Node Tree Test', False)
            load_image = test_node_tree.nodes.new('PythonLoadImageNode')
            save_image = test_node_tree.nodes.new('PythonSaveImageBaseNode')
            test_node_tree.links.new(
                input=save_image.inputs[0],
                output=load_image.outputs[0]
            )
            return {'FINISHED'}

def add_test_node_tree(self, context):
    self.layout.separator()
    self.layout.operator(
        NODE_MT_add_test_node_tree.bl_idname,
        text="Add Test Node Tree")


from pynodes import registry
from pynodes import helpers

def register():

    registry.registerAll()

    from bpy.utils import register_class
    # register the essentials to building a PythonNode
    register_class(PythonCompositorTree)
    register_class(PyObjectSocket)

    register_class(PyObjectVarArgSocket)
    register_class(PyObjectKWArgSocket)


    register_class(NODE_MT_add_test_node_tree)
    bpy.types.NODE_MT_node.append(add_test_node_tree)
    bpy.data.screens['Compositing'].areas[3].ui_type = 'PythonCompositorTreeType'
    """
    # register every single PythonNode derivative
    for cls in node_classes:
        print('registering node class', cls)
        register_class(cls)

    # create the python node editor
    nodeitems_utils.register_node_categories('CUSTOM_NODES', node_categories)

    # register dropdown menues in node editor
    """

def unregister():
    registry.unregisterAll()
    """
    nodeitems_utils.unregister_node_categories('CUSTOM_NODES')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    """
    unregister_class(PythonCompositorTree)
    unregister_class(PyObjectSocket)
