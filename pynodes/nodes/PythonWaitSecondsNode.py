import pynodes
from pynodes import nodes
import time
import bpy

class PythonWaitSecondsNode(nodes.PythonNode):
    # === Basics ===
    # Description string
    '''Hold thread of execution on this node for specified number of seconds.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonWaitSecondsNode'
    # Label for nice name display
    bl_label = "Pause"

    seconds : bpy.props.FloatProperty(
        name='Seconds',
        description="Seconds to wait",
        default=6.9,
        update=lambda s,c:s.update()
    )

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "seconds")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "seconds")

    def init(self, context):
        super().init(context)
        self.inputs.new('PyObjectSocketType', "Anything")
        self.outputs.new('PyObjectSocketType', "Anything")

    def run(self):
        inp = self.get_input("Anything", lambda:None)
        time.sleep(self.seconds)
        self.set_output("Anything", inp)

from pynodes import registry
registry.registerNodeType(PythonWaitSecondsNode)
