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


from pynodes import registry
from pynodes import nodes

classes = sorted(registry.__registry__.keys())

# all categories in a list
node_categories = [
    # identifier, label, items list
    PythonCompositorNodeCategory(
        'ALLNODES',
        "All Nodes",
        items=[
            NodeItem(registry.__registry__[cls].bl_idname)
            for cls in classes
        ]
    )
]

classes = [
    PythonCompositorTree,
    PyObjectSocket,
    *[
        registry.__registry__[cls]
        for cls in classes
    ]
]

def register():
    from bpy.utils import register_class
    for cls in classes:
        print('registering class', cls)
        register_class(cls)

    nodeitems_utils.register_node_categories('CUSTOM_NODES', node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories('CUSTOM_NODES')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    try:
        unregister()
    except Exception as e:
        print('Unregister error:', e)
    register()
