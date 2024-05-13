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
from bpy.types import (
    Operator,
    PropertyGroup,
)
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatVectorProperty,
    StringProperty,
)

# TODO ideas:
# 1. autorename sockets based off of return type, numpy array could show dtype, shape

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class PythonCompositorTree(NodeTree):
    # Description string
    '''A custom node tree type that will show up in the editor type list'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonCompositorTreeType'
    # Label for nice name display
    bl_label = "PyNodes Compositor Tree"
    # Icon identifier
    bl_icon = 'NODETREE'

# Custom socket type
class AbstractPyObjectSocket(NodeSocket):
    # Description string
    '''General python node socket type'''


    # for storing the inputs and outputs of nodes without overriding default_value
    # we can't change value of _value_, but we can set what it points to if its a list
    # _value_ = [{},]#: bpy.props.PointerProperty(type=bpy.types.Object, name='value', description='Pointer to object contained by the socket')

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

def get_override(area_type):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        
        for area in screen.areas:
            if area.type == area_type:
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'window': window,
                                    'screen': screen,
                                    'area': area,
                                    'region': region,
                                    'blend_data': bpy.context.blend_data}
                        
                        return override

# Have to add node grouping behavior manually:
class PyNodesGroupEdit(PythonCompositorOperator):
    bl_idname = "node.pynodes_group_edit"
    bl_label = "edits a pynodes node group"

    group_name : bpy.props.StringProperty(default='Node Group')
    
    def group_make(self, node, new_group_name):
        self.node_tree = bpy.data.node_groups.new(new_group_name, PythonCompositorTree.bl_idname)
        self.group_name = self.node_tree.name

        nodes = self.node_tree.nodes
        inputnode = nodes.new('PyNodesGroupInputsNode')
        outputnode = nodes.new('PyNodesGroupOutputsNode')
        inputnode.location = (-300, 0)
        outputnode.location = (300, 0)
        return self.node_tree
    
    def execute(self, context):
        node = context.active_node
        parent_tree_name = node.id_data.name
        ng = bpy.data.node_groups
        
        print(self.group_name)

        node_group = ng.get(self.group_name)
        if not node_group:
            node_group = self.group_make(node, new_group_name=self.group_name)
        
        bpy.ops.node.pynodes_switch_layout(layout_name=self.group_name)

        # by switching, space_data is now different
        # parent_tree_name = node.id_data.name
        path = context.space_data.path
        path.clear() #?
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

class NODE_MT_add_python_node(PythonCompositorOperator):
    """Allow user to search for the exact function they wish to run in a node."""
    bl_idname = "node.add_python_node"
    bl_label = "Add python node by search"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        if bpy.data.node_groups.get('Python Node Tree Test', False)==False:
            bpy.ops.node.new_node_tree(
                type=PythonCompositorTree.bl_idname,
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

# NodeAddOperator, NodeSetting from https://raw.githubusercontent.com/blender/blender/main/scripts/startup/bl_operators/node.py

class NodeSetting(PropertyGroup):
    value: StringProperty(
        name="Value",
        description="Python expression to be evaluated "
        "as the initial node setting",
        default="",
    )

# Base class for node "Add" operators.
class NodeAddOperator:

    use_transform: BoolProperty(
        name="Use Transform",
        description="Start transform operator after inserting the node",
        default=False,
    )
    settings: CollectionProperty(
        name="Settings",
        description="Settings to be applied on the newly created node",
        type=NodeSetting,
        options={'SKIP_SAVE'},
    )

    @staticmethod
    def store_mouse_cursor(context, event):
        space = context.space_data
        tree = space.edit_tree

        # convert mouse position to the View2D for later node placement
        if context.region.type == 'WINDOW':
            # convert mouse position to the View2D for later node placement
            space.cursor_location_from_region(
                event.mouse_region_x, event.mouse_region_y)
        else:
            space.cursor_location = tree.view_center

    # Deselect all nodes in the tree.
    @staticmethod
    def deselect_nodes(context):
        space = context.space_data
        tree = space.edit_tree
        for n in tree.nodes:
            n.select = False

    def create_node(self, context, node_type):
        space = context.space_data
        tree = space.edit_tree

        try:
            node = tree.nodes.new(type=node_type)
        except RuntimeError as ex:
            self.report({'ERROR'}, str(ex))
            return None

        for setting in self.settings:
            # XXX catch exceptions here?
            value = eval(setting.value)
            node_data = node
            node_attr_name = setting.name

            # Support path to nested data.
            if '.' in node_attr_name:
                node_data_path, node_attr_name = node_attr_name.rsplit(".", 1)
                node_data = node.path_resolve(node_data_path)

            try:
                setattr(node_data, node_attr_name, value)
            except AttributeError as ex:
                self.report(
                    {'ERROR_INVALID_INPUT'},
                    tip_("Node has no attribute %s") % setting.name)
                print(str(ex))
                # Continue despite invalid attribute

        node.select = True
        tree.nodes.active = node
        node.location = space.cursor_location
        return node

    @classmethod
    def poll(cls, context):
        space = context.space_data
        # needs active node editor and a tree to add nodes to
        return (space and (space.type == 'NODE_EDITOR') and
                space.edit_tree and not space.edit_tree.library)

    # Default invoke stores the mouse position to place the node correctly
    # and optionally invokes the transform operator
    def invoke(self, context, event):
        self.store_mouse_cursor(context, event)
        result = self.execute(context)

        if self.use_transform and ('FINISHED' in result):
            # removes the node again if transform is canceled
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return result

# NODE_OT_add_node from https://raw.githubusercontent.com/jesterKing/blender/143ccc8c44cbd1a630c4f02d8c6eb26e26c63757/blender/release/scripts/startup/bl_operators/node.py

class NODE_OT_add_search_pynodes(NodeAddOperator, Operator):
    '''Add a node to the active tree'''
    bl_idname = "node.add_search_pynodes"
    bl_label = "Search and Add Node"
    bl_options = {'REGISTER', 'UNDO'}
    bl_property = "node_item"

    _enum_item_hack = []

    # Create an enum list from node items
    def node_enum_items(self, context):
        enum_items = NODE_OT_add_search._enum_item_hack
        enum_items.clear()
        
        

        return enum_items

    # Look up the item based on index
    def find_node_item(self, context):
        node_item = int(self.node_item)
        for index, item in enumerate(nodeitems_utils.node_items_iter(context)):
            if index == node_item:
                return item
        return None

    node_item = EnumProperty(
            name="Node Type",
            description="Node type",
            items=node_enum_items,
            )

    def execute(self, context):
        item = self.find_node_item(context)

        # no need to keep
        self._enum_item_hack.clear()

        if item:
            # apply settings from the node item
            for setting in item.settings.items():
                ops = self.settings.add()
                ops.name = setting[0]
                ops.value = setting[1]

            n = self.create_node(context, 'AnyNode')
            n.api_endpoint_string = item.label

            if self.use_transform:
                bpy.ops.transform.translate('INVOKE_DEFAULT', remove_on_cancel=True)

            return {'FINISHED'}
        else:
            return {'CANCELLED'}

    def invoke(self, context, event):
        self.store_mouse_cursor(context, event)
        # Delayed execution in the search popup
        context.window_manager.invoke_search_popup(self)
        return {'CANCELLED'}

from pynodes import registry
from pynodes import helpers

def register():

    registry.registerAll()

    from bpy.utils import register_class
    # register the essentials to building a PythonNode
    register_class(PythonCompositorTree)
    register_class(PyObjectSocket)
    
    register_class(PyNodesGroupEdit)
    register_class(PyNodesTreePathParent)
    register_class(PyNodesSwitchToLayout)
    bpy.types.NODE_MT_node.append(pynodes_group_edit)

    # register_class(NODE_MT_add_test_node_tree)
    # bpy.types.NODE_MT_node.append(add_test_node_tree)

def unregister():
    registry.unregisterAll()

    unregister_class(PythonCompositorTree)
    unregister_class(PyObjectSocket)
    
    unregister_class(PyNodesGroupEdit)
    unregister_class(PyNodesTreePathParent)
    unregister_class(PyNodesSwitchToLayout)
