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

import registry

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
    
class PythonSaveImageBaseNode(PythonBaseNode):
    # === Basics ===
    # Description string
    '''Save image to image viewer.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonSaveImageBaseNode'
    # Label for nice name display
    bl_label = "Python Image Result"
    
    empty = np.zeros([6, 9, 4], dtype=np.float32)
    
    def init(self, context):
        self.inputs.new('PyObjectSocketType', "Image")
        self.setup_post_init_hooks()
    
    def run(self):
        array = self.get_input("Image", lambda:self.empty)
        alpha = array.shape[2]==4
        print(array.shape, array.min(), array.max())
        if self.bl_label in bpy.data.images.keys():
            bpy.data.images.remove(bpy.data.images[self.bl_label])
        image = bpy.data.images.new(self.bl_label, alpha=alpha, width=array.shape[1], height=array.shape[0])
#        image.pixels = array.ravel()
        bgr = np.stack([array[:,:,0], array[:,:,1], array[:,:,2], array[:,:,3]], axis=-1)
        print(bgr.shape)
        image.pixels = bgr.ravel()

class PythonLoadImageNode(PythonNode):
    # === Basics ===
    # Description string
    '''Load Image Data'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonLoadImageNode'
    # Label for nice name display
    bl_label = "Python Image Loader"
    
#    def update_filename(self, context):
#        print('running set', self.filename)
#        self.update_value()
#        print('ran set')
    
    filename : bpy.props.StringProperty(
        name='Filename',
        description="Filepath of image.",
        default='/home/cs/Resources/textures/000001_1k_color.png',
        update=lambda s,c:s.update()#update_filename
    )
    
    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "filename")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "filename")
    
    def init(self, context):
        self.outputs.new('PyObjectSocketType', "Image")
        self.setup_post_init_hooks()
    
    def run(self):
        img = bpy.data.images.load(self.filename, check_existing=True)
        img_arr = np.array(img.pixels).reshape([*img.size, img.channels])
        self.set_output("Image", img_arr)

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


# all categories in a list
node_categories = [
    # identifier, label, items list
    PythonCompositorNodeCategory('SOMENODES', "Some Nodes", items=[
        # our basic node
        NodeItem("PythonSaveImageBaseNode"),
        NodeItem("PythonLoadImageNode"),
    ])
]

classes = (
    PythonCompositorTree,
    PyObjectSocket,
    PythonSaveImageBaseNode,
    PythonLoadImageNode,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
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
