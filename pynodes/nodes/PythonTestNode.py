import pynodes
from pynodes import nodes
import numpy as np
import bpy

class PythonTestNode(nodes.PythonNode):
    # === Basics ===
    # Description string
    '''Load Image Data'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonTestNode'
    # Label for nice name display
    bl_label = "Python Test Node"

    def init(self, context):
        super().init(context)
        self.outputs.new(pynodes.PyObjectSocket.bl_idname, "Random Matrix")

    def run(self):
        r = np.random.uniform(size=(50,2), low=-5, high=5)
        r[r>1] = 0
        self.set_output("Random Matrix", r)



from pynodes import registry
registry.registerNodeType(PythonTestNode)
