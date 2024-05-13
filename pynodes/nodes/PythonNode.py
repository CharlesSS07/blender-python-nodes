import pynodes
import traceback
import bpy
import numpy as np

from pynodes import PythonCompositorTree

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class PythonCompositorTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == pynodes.PythonCompositorTree.bl_idname

class ColorfulNode(bpy.types.Node):
    # === Basics ===
    # Description string
    '''Abstract node that can change colors.'''

    def init(self, context):
        pass

    def set_color(self, color):
        self.use_custom_color = True
        self.color = color
        # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)

    def set_no_color(self):
        self.use_custom_color = False
        # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)

# Derived from the Node base type.
# Defines functionality of python node to only require that call is overloaded
class PythonNode(ColorfulNode, PythonCompositorTreeNode):
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

    def update(self):
        '''
        Called when the node tree changes.
        '''
        
        for socket in self.inputs: # TODO: check that socket is updatable
            socket.node_updated()
