import pynodes
from pynodes import nodes
import numpy as np
import bpy

class PythonEvalStatementNode(nodes.PythonNode):
    # === Basics ===
    # Description string
    '''Evaluates a Python statement (one-liner), returns object from return'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonEvalFunctionNode'
    # Label for nice name display
    bl_label = "Eval Statement"

    arbitrary_code : bpy.props.StringProperty(
        name='',#'Code to Evaluate',
        description='Evaluates string as python, and returns object.',
        default="f'Hello World'",
        update=lambda s,c:s.update()
    )

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "arbitrary_code")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "arbitrary_code")

    def init(self, context):
        super().init(context)
        self.outputs.new(pynodes.PyObjectSocket.bl_idname, "Python Object")
        self.width *= 3 # make this thing big so you can type in big statements.

    def run(self):
        self.set_output("Python Object", eval(self.arbitrary_code))



from pynodes import registry
registry.registerNodeType(PythonEvalStatementNode)
