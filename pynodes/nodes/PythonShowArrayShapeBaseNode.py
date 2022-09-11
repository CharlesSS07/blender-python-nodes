import pynodes
from pynodes import nodes
# from pynodes.nodes.PythonBaseNode import PythonBaseNodeProperties
import numpy as np
import bpy

class PythonShowArrayShapeBaseNode(nodes.PythonBaseNode.Properties, nodes.PythonBaseNode):
    # === Basics ===
    # Description string
    '''Print the shape of given array to the nodes text'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonShowArrayShapeBaseNode'
    # Label for nice name display
    bl_label = "Show Array Shape"

    def init(self, context):
        super().init(context)
        self.outputs.new(pynodes.PyObjectSocket.bl_idname, "Shape")
        self.inputs.new(pynodes.PyObjectSocket.bl_idname, "Array")

    def draw_buttons(self, context, layout):
        layout.operator('node.evaluate_python_node_tree', icon='PLAY')
        row = layout.row()
        row.label(text=self.outputs["Shape"].get_value().__str__())

    def run(self):
        a = self.get_input("Array", lambda:self.empty)
        output = np.shape(a)
        self.set_output("Shape", output)
        print('Result:\n', np.shape(a))

from pynodes import registry
registry.registerNodeType(PythonShowArrayShapeBaseNode)
