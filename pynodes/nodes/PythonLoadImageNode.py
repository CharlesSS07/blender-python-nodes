import pynodes
from pynodes import nodes
# from pynodes.nodes import PythonNode
import numpy as np
import bpy

class PythonLoadImageNode(nodes.PythonNode):
    # === Basics ===
    # Description string
    '''Load Image Data'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonLoadImageNode'
    # Label for nice name display
    bl_label = "Python Image Loader"

    # filename : bpy.props.StringProperty(
    #     name='Filename',
    #     description="Filepath of image.",
    #     default='/home/cs/Resources/textures/000001_1k_color.png',
    #     update=lambda s,c:s.update()#update_filename
    # )
    #
    # # Additional buttons displayed on the node.
    # def draw_buttons(self, context, layout):
    #     layout.prop(self, "filename")
    #
    # # Detail buttons in the sidebar.
    # # If this function is not defined, the draw_buttons function is used instead
    # def draw_buttons_ext(self, context, layout):
    #     layout.prop(self, "filename")

    def init(self, context):
        super().init(context)
        self.outputs.new(pynodes.PyObjectSocket.bl_idname, "Image")
        self.inputs.new('NodeSocketImage', "Image")
        bpy.data.images.load('/home/cs/Resources/textures/000001_1k_color.png', check_existing=True)

    def run(self):
        img = self.inputs["Image"].default_value
        img_arr = np.array(img.pixels).reshape([*img.size, img.channels])
        self.set_output("Image", img_arr)



from pynodes import registry
registry.registerNodeType(PythonLoadImageNode)
