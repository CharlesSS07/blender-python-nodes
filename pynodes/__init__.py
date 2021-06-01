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
class AbstractPyObjectSocket(NodeSocket):
    # Description string
    '''General python node socket type'''


    # for storing the inputs and outputs of nodes without overriding default_value
    # we can't change value of _value_, but we can set what it points to if its a list
    _value_ = [None,]#: bpy.props.PointerProperty(type=bpy.types.Object, name='value', description='Pointer to object contained by the socket')

    class Properties:
        argvalue : bpy.props.StringProperty(
            name = 'argvalue',
            description = 'manually input value to argument for function',
            default = '',
            update = lambda s,c: self.manual_set(self.argvalue)#update_filename
        )

    def argvalue_update(self, value):
        pass

    def get_value(self):
        if self.is_linked:
            return self._value_[0]
        else:
            return self.argvalue

    def set_value(self, value):
        self._value_[0] = value


    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)

    def draw(self, context, layout, node, text):
        layout.label(text=text)
        # give default value selector when not linked
        if not self.is_linked:
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

    def init(self, context):
        # pin shape
        self.display_shape = 'DIAMOND'

    def argvalue_update(self, value):
        self.node.inputs.new(PyObjectVarArgSocket.bl_idname, '*arg')





class PyObjectKWArgSocket(AbstractPyObjectSocket.Properties, AbstractPyObjectSocket):
    # Description string
    '''Python node socket type for keyword argumnets'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PyObjectKWArgSocketType'
    # Label for nice name display
    bl_label = 'Python *kwargs Object Socket'

    def init(self, context):
        # pin shape
        self.display_shape = 'SQUARE'

    # method to set the initial value of an argument
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
