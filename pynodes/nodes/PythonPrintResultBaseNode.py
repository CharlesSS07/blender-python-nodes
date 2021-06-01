import pynodes
from pynodes import nodes
# from pynodes.nodes.PythonBaseNode import PythonBaseNodeProperties
import numpy as np
import bpy

class PythonPrintResultBaseNode(nodes.PythonBaseNode.Properties, nodes.PythonBaseNode):
    # === Basics ===
    # Description string
    '''Print Result of Connected Nodes'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonPrintResultBaseNode'
    # Label for nice name display
    bl_label = "Print Result of Connected Nodes"

    def init(self, context):
        super().init(context)
        self.inputs.new(pynodes.PyObjectSocket.bl_idname, "Result")

    def run(self):
        a = self.get_input("Result", lambda:self.empty)
        print('Result:\n', a)

from pynodes import registry
registry.registerNodeType(PythonPrintResultBaseNode)
