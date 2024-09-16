import pynodes
from pynodes import nodes
import time
import bpy
import requests

class PythonRequestURLNode(nodes.PythonNode):
    # === Basics ===
    # Description string
    '''Hold thread of execution on this node for specified number of seconds.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonRequestURLNode'
    # Label for nice name display
    bl_label = "Get URL / Download"

    url : bpy.props.StringProperty(
        name='URL',
        default='https://1000logos.net/wp-content/uploads/2021/10/Batman-Logo.png',
        update=lambda s,c:s.update()
    )

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "url")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "url")

    def init(self, context):
        super().init(context)
        self.outputs.new(pynodes.PyObjectSocket.bl_idname, "Request")
        self.outputs.new(pynodes.PyObjectSocket.bl_idname, "Content")

    def run(self):

        r = requests.get(self.url)
        self.set_output("Request", r)
        self.set_output('Content', r.content)

from pynodes import registry
registry.registerNodeType(PythonRequestURLNode)
