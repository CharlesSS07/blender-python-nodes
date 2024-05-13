import bpy
import traceback
from pynodes import nodes
# from pynodes.nodes import PythonNode

class EvaluateNodesOperator(bpy.types.Operator):
    """Cause active python node tree to evaluate results."""
    bl_idname = "node.evaluate_python_node_tree"
    bl_label = ""
    bl_icon = "PLAY"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        context.node.run()
        return {'FINISHED'}

from pynodes import registry
registry.registerOperator(EvaluateNodesOperator)

class PythonBaseNode(nodes.PythonNode):
    # === Basics ===
    # Description string
    '''Abstract python base node. Connected nodes will be run. Unconnected nodes are not run.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonBaseNode'
    # Label for nice name display
    bl_label = "Python Base Node"

    class Properties:
        pass

    def mark_dirty(self):
        self.is_current = False
        super().mark_dirty()

    def draw_buttons(self, context, layout):
        layout.operator('node.evaluate_python_node_tree', icon='PLAY')

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.operator('node.evaluate_python_node_tree', icon='PLAY')

    def is_connected_to_base(self):
        return True
