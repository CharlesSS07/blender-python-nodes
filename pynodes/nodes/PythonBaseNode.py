import bpy
import traceback
from pynodes import nodes
# from pynodes.nodes import PythonNode

class PythonBaseNode(nodes.PythonNode):
    # === Basics ===
    # Description string
    '''Abstract python base node. Connected nodes will be run. Unconnected nodes are not run.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonBaseNode'
    # Label for nice name display
    bl_label = "Python Base Node"

    class Properties:
        is_current : bpy.props.BoolProperty(
            name='Updated Checkbox',
            description="Check to compute output. Automatically unchecked when value is out of date.",
            default=False,
            update=lambda s,c:s.compute_output()
        )

    def mark_dirty(self):
        self.is_current = False
        super().mark_dirty()

    def compute_output(self):
        print('compute_output run')
        try:
            super().compute_output()
        except nodes.PythonNode.PythonNodeRunError as e:
            traceback.print_exc()

    def draw_buttons(self, context, layout):
        # print(dir(layout))
        layout.prop(self, 'is_current')

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'is_current')

    def is_connected_to_base(self):
        return True
