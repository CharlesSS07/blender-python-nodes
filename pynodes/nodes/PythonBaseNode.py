# import pynodes
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

    def is_connected_to_base(self):
        return True
