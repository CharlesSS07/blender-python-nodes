bl_info = {
    "name": "Python Nodes",
    "description": "The power of python, brought to you through blender nodes.",
    "author": "Charles M. S. Strauss<charles.s.strauss@gmail.com>, and Robert R. Strauss<robert.r.strauss@icloud.com>",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "Console",
    "warning": "Will run arbitrary code.",
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
    _value_ = [{},]#: bpy.props.PointerProperty(type=bpy.types.Object, name='value', description='Pointer to object contained by the socket')

    # blender properties have to be wrapped in this so they are inherited in a way that blender properties can access them
    class Properties:
    
        argvalue : bpy.props.StringProperty(
            name = 'argvalue',
            description = 'manually input value to argument for function',
            default = '',
            maxlen= 1024,
            update = lambda s,c: s.argvalue_updated()
        )
        
        argvalue_hidden : bpy.props.BoolProperty(
            default=False
        )

    def argvalue_updated(self):
        pass
        
    def node_updated(self):
        pass

    def get_value(self):
        if (self.is_linked or self.is_output) and self.identifier in self._value_[0]:
            return self._value_[0][self.identifier]
        else:
            return self.argvalue # eval(self.argvalue, node_execution_scope)

    def set_value(self, value):
        self._value_[0][self.identifier] = value
    
    def hide_text_input(self):
        self.argvalue_hidden = True
    
    def show_text_input(self):
        self.argvalue_hidden = False

    def is_empty(self):
        return (not self.is_linked) and (self.argvalue=='' or self.argvalue==None)

    # Socket color
    def draw_color(self, context, node):
        return (0.7, 0.7, 0.7, 0.5)

    def draw(self, context, layout, node, text):
        if text!='':
            layout.label(text=text)
        # give default value selector when not linked
        if not self.argvalue_hidden and not self.is_linked and not self.is_output:
            layout.prop(self, 'argvalue', text='')

class PyObjectSocket(AbstractPyObjectSocket.Properties, AbstractPyObjectSocket):
    ''' Python node socket type for normal function arguments and outputs '''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PyObjectSocketType'
    # Label for nice name display
    bl_label = "Python Object Socket"

class AbstractPyObjectVarArgSocket(AbstractPyObjectSocket.Properties, AbstractPyObjectSocket):
    # Description string
    '''PyNodes node socket type for variable arguments (varargs, *args)'''
    
    class Properties:
        socket_index : bpy.props.IntProperty(
            name = 'socket_index',
            default = -1
        )
    
        socket_index_valid : bpy.props.BoolProperty(
            name = 'socket_index_valid',
            default = True
        )

    def __init__(self):
        super().__init__()
        self.name = self.identifier
        if not self.socket_index_valid:
            self.node.inputs.move(self.node.inputs.find(self.identifier), self.socket_index)
            self.socket_index_valid = True

    # var args nodes automatically remove or add more of themselves as they are used
    def node_updated(self):
        self.update()
    
    def argvalue_updated(self):
        self.update()
        
    def socket_init(self):
        pass
    
    def update(self):
    
        if self.is_output:
            socket_collection = self.node.outputs
        else:
            socket_collection = self.node.inputs
        
        emptypins = 0
        # count the number of non-linked, empty sibling vararg pins
        for i in socket_collection:
            if i.bl_idname == self.bl_idname:
                if i.is_empty():
                    emptypins+=1
                    last_empty_socket = i
                last_socket = i

        # there is at least one other empty non-linked one (other than self)
        if emptypins > 1:
            # remove self if empty and not linked
            self.node.unsubscribe_to_update(last_empty_socket.node_updated)
            socket_collection.remove(last_empty_socket)
        # create new pin if there is not enough
        elif emptypins < 1:
            new_socket = socket_collection.new(
                self.bl_idname,
                '',
                identifier=self.identifier
            )
            
            if last_socket.socket_index==-1:
                new_socket.socket_index = socket_collection.find(last_socket.identifier)+1
            else:
                new_socket.socket_index = last_socket.socket_index+1
            new_socket.socket_index_valid = False
            
            new_socket.socket_init()

class PyObjectVarArgSocket(AbstractPyObjectVarArgSocket.Properties, AbstractPyObjectVarArgSocket):
    # Description string
    '''PyNodes node socket type for variable arguments (varargs, *args)'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PyObjectVarArgSocketType'
    # Label for nice name display
    bl_label = 'Expanding Socket'
    
    def __init__(self):
        super().__init__()
        # pin shape
        self.display_shape = 'DIAMOND'

# class PyObjectVarArgSocket(AbstractPyObjectSocket.Properties, AbstractPyObjectSocket):
#     # Description string
#     '''Python node socket type for variable arguments (varargs, *args)'''
#     # Optional identifier string. If not explicitly defined, the python class name is used.
#     bl_idname = 'PyObjectVarArgSocketType'
#     # Label for nice name display
#     bl_label = 'Python *args Object Socket'
# 
#     def __init__(self):
#         super().__init__()
#         # pin shape
#         self.display_shape = 'DIAMOND'
#         self.name = self.identifier
#         # socket must be indexible using name.
#         # therefore force name to be unique like identifier
#         self.node.subscribe_to_update(self.node_updated)
#         # subscribe socket to node update events
# 
#     # var args nodes automatically remove or add more of themselves as they are used
#     def node_updated(self):
#         # print('node_updated', self.node, self)
#         self.update()
# 
#     def argvalue_updated(self):
#         # print('argvalue_updated', self.node, self)
#         self.update()
# 
#     def update(self):
#         emptyvarargpins = 0
#         # count the number of non-linked, empty sibling vararg pins
#         for input in self.node.inputs:
#             if input.bl_idname == PyObjectVarArgSocket.bl_idname:
#                 if input.is_empty():
#                     emptyvarargpins+=1
# 
#         # there is at least one other empty non-linked one (other than self)
#         if emptyvarargpins > 1:
#             # remove self if empty and not linked
#             self.node.unsubscribe_to_update(self)
#             self.node.inputs.remove(self)
#         # create new pin if there is not enough
#         elif emptyvarargpins < 1:
#             self.node.inputs.new(PyObjectVarArgSocket.bl_idname, '*arg')

# class PyObjectKwArgSocket(AbstractPyObjectVarArgSocket.Properties, AbstractPyObjectVarArgSocket):
#     # Description string
#     '''PyNodes socket type for variable arguments (varargs, *args)'''
#     # Optional identifier string. If not explicitly defined, the python class name is used.
#     bl_idname = 'PyObjectKwArgSocket'
#     # Label for nice name display
#     bl_label = 'Expanding Socket for Optional Attributes'
#     
#     attribute : bpy.props.StringProperty(
#         name='Attribute',
#         description="An attribute to set.",
#         update=lambda s,c:s.node.update()
#     )
#     
#     attribute_collection : bpy.props.CollectionProperty(
#         name='Attribute Selector',
#         type=bpy.types.PropertyGroup
#     )
#     
#     def update_attribute_collection(self):
#         self.attribute_collection.clear()
#         for a in self.get_display_attributes():
#             self.attribute_collection.add().name = a
#     
#     def node_updated(self):
#         super().node_updated()
#         self.update_attribute_collection()
#     
#     def socket_init(self):
#         super().socket_init()
#         self.update_attribute_collection()
#     
#     def get_display_attributes(self):
#         unused_attributes = self.node.unused_attributes()
#         if not self.attribute is None:
#         	unused_attributes+=[self.attribute,]
#         unused_attributes = sorted(unused_attributes)
#         return unused_attributes
# 
#     def draw(self, context, layout, node, text):
#         if text!='':
#             layout.label(text=text)
#         layout.prop_search(self, 'attribute', self, 'attribute_collection', text='')
#         if not self.is_linked and not self.is_output:
#             layout.prop(self, 'argvalue', text='')
#         
#     def __init__(self):
#         super().__init__()
#         # pin shape
#         self.display_shape = 'SQUARE'

class PyObjectKwArgSocket(AbstractPyObjectSocket.Properties, AbstractPyObjectSocket):
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

# Have to add grouping behavior manually:

def group_make(self, new_group_name):
    self.node_tree = bpy.data.node_groups.new(new_group_name, PythonCompositorTree.bl_idname)
    self.group_name = self.node_tree.name

    nodes = self.node_tree.nodes
    inputnode = nodes.new('PyNodesGroupInputsNode')
    outputnode = nodes.new('PyNodesGroupOutputsNode')
    inputnode.location = (-300, 0)
    outputnode.location = (300, 0)
    return self.node_tree

class PyNodesGroupEdit(PythonCompositorOperator):
    bl_idname = "node.pynodes_group_edit"
    bl_label = "edits an pynodes node group"

    group_name : bpy.props.StringProperty(default='Node Group')

    def execute(self, context):
        node = context.active_node
        ng = bpy.data.node_groups
        
        print(self.group_name)

        group_node = ng.get(self.group_name)
        if not group_node:
            group_node = group_make(node, new_group_name=self.group_name)

        bpy.ops.node.pynodes_switch_layout(layout_name=self.group_name)
#         print(context.space_data, context.space_data.node_tree)
#         context.space_data.node_tree = ng[self.group_name] # does the same

        # by switching, space_data is now different
        parent_tree_name = node.id_data.name
        path = context.space_data.path
        path.clear()
        path.append(ng[parent_tree_name]) # below the green opacity layer
        path.append(ng[self.group_name])  # top level

        return {"FINISHED"}

class PyNodesTreePathParent(PythonCompositorOperator):
    '''Go to parent node tree'''
    bl_idname = "node.pynodes_tree_path_parent"
    bl_label = "Parent PyNodes Node Tree"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return super() and len(space.path) > 1

    def execute(self, context):
        space = context.space_data
        space.path.pop()
        context.space_data.node_tree = space.path[0].node_tree
        return {'FINISHED'}

def pynodes_group_edit(self, context):
    self.layout.separator()
    self.layout.operator(
        PyNodesGroupEdit.bl_idname,
        text="Edit Group (pynodes)")
    self.layout.operator(
        PyNodesTreePathParent.bl_idname,
        text="Exit/Enter Group (pynodes)")
        
class PyNodesSwitchToLayout(bpy.types.Operator):
    """Switch to exact layout, user friendly way"""
    bl_idname = "node.pynodes_switch_layout"
    bl_label = "switch layouts"
    bl_options = {'REGISTER', 'UNDO'}

    layout_name: bpy.props.StringProperty(
        default='', name='layout_name',
        description='layout name to change layout by button')

    @classmethod
    def poll(cls, context):
        if context.space_data.type == 'NODE_EDITOR':
            if bpy.context.space_data.tree_type == PythonCompositorTree.bl_idname:
                return True
        else:
            return False

    def execute(self, context):
        ng = bpy.data.node_groups.get(self.layout_name)
        if ng:
            context.space_data.path.start(ng)
        else:
            return {'CANCELLED'}
        return {'FINISHED'}

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
    register_class(PyObjectKwArgSocket)
    
    register_class(PyNodesGroupEdit)
    register_class(PyNodesTreePathParent)
    register_class(PyNodesSwitchToLayout)
    bpy.types.NODE_MT_node.append(pynodes_group_edit)

    register_class(NODE_MT_add_test_node_tree)
    bpy.types.NODE_MT_node.append(add_test_node_tree)

def unregister():
    registry.unregisterAll()

    unregister_class(PythonCompositorTree)
    unregister_class(PyObjectSocket)
    unregister_class(PyObjectVarArgSocket)
    unregister_class(PyObjectKwArgSocket)
    
    unregister_class(PyNodesGroupEdit)
    unregister_class(PyNodesTreePathParent)
    unregister_class(PyNodesSwitchToLayout)
