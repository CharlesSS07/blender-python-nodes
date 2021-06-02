import pynodes
from pynodes import nodes
# from pynodes.nodes.PythonBaseNode import PythonBaseNodeProperties
import numpy as np
import bpy

class PythonSaveImageBaseNode(nodes.PythonBaseNode.Properties, nodes.PythonBaseNode):
    # === Basics ===
    # Description string
    '''Save image to image viewer.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonSaveImageBaseNode'
    # Label for nice name display
    bl_label = "Python Image Result"

    empty = np.zeros([6, 9, 4], dtype=np.float32)

    def init(self, context):
        super().init(context)
        self.inputs.new(pynodes.PyObjectSocket.bl_idname, "Image")

    def run(self):
        array = self.get_input("Image")
        alpha = array.shape[2]==4
        print(array.shape, array.min(), array.max())
        if self.bl_label in bpy.data.images.keys():
            bpy.data.images.remove(bpy.data.images[self.bl_label])
        image = bpy.data.images.new(self.bl_label, alpha=alpha, width=array.shape[1], height=array.shape[0])
#        image.pixels = array.ravel()
        bgr = np.stack([array[:,:,0], array[:,:,1], array[:,:,2], array[:,:,3]], axis=-1)
        print(bgr.shape)
        image.pixels = bgr.ravel()

from pynodes import registry
registry.registerNodeType(PythonSaveImageBaseNode)
