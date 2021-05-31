import pynodes
import bpy

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class PythonCompositorTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == pynodes.PythonCompositorTree.bl_idname

class FlashingNode(bpy.types.Node):
    # === Basics ===
    # Description string
    '''Abstract node that can change colors.'''

    flash_on_color = [1.0,0.0,0.0]
    flash_off_color = [0.0,0.0,0.0]
    flash_on = False

    def set_flash_color(self, color):
        self.flash_on_color = color

    def set_color_flash_on(self):
        if not self.flash_on:
            self.flash_off_color = self.color
            self.color = self.flash_on_color
            print(self.flash_off_color, self.flash_off_color is self.color, self.flash_off_color == self.color)
        else:
            self.flash_on = True

    def set_color_flash_off(self):
        if self.flash_on:
            self.color = self.flash_off_color
        else:
            self.flash_on = False



# Derived from the Node base type.
# Defines functionality of python node to only require that call is overloaded
class PythonNode(FlashingNode, PythonCompositorTreeNode):
    # === Basics ===
    # Description string
    '''Abstract python node.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonNode'
    # Label for nice name display
    bl_label = "Python Node"
    # Icon identifier
    bl_icon = 'SCRIPT'

    def is_connected_to_base(self):
        '''
        Return true if this node is connected to a node which is a "base" node.
        '''
        for k in self.outputs.keys():
            out = self.outputs[k]
            if out.is_linked:
                for o in out.links:
                    if o.is_valid and o.to_socket.node.is_connected_to_base():
                        return True
        return False

    def run(self):
        '''
        Do whatever calculations this node does. Take input from self.get_input
        and set outpus using self.set_output.
        '''
        pass

    def get_input(self, k, default_func):
        v = self.inputs[k]
        if v.is_linked and len(v.links)>0 and v.links[0].is_valid:
            o = v.links[0].from_socket
            value = o.get_value()
            return value
        v.set_value(None)
        return default_func()

    def set_output(self, k, v):
        self.outputs[k].set_value(v)

    def update_value(self):
        '''
        Called when a value changes (links, or node settings). Runs node unless
        this node is not connected to a base node. Propagates the nodes outputs
        to the linked nodes, and calls update_value on them.
        '''
        if self.is_connected_to_base():
            self.set_color_flash_off()
            self.set_flash_color([0.0, 1.0, 0.0])
            self.set_color_flash_on()
            try:
                self.run()
                self.set_color_flash_off()
            except Exception as e:
                print(f'Node "{self.bl_label}" raised an exception:')
                print(e)
                self.set_color_flash_off()
                self.set_flash_color([1.0, 0.0, 0.0])
                self.set_color_flash_on()
            self.propagate()

    def update(self):
        '''
        Called when the node tree changes.
        '''
        self.update_value()

    def propagate(self):
        '''
        Pass this nodes outputs to nodes liked to outputs. Call update_value on
        them after passing.
        '''
        outputs = [self.outputs[k] for k in self.outputs.keys()]
        for out in outputs:
            if out.is_linked:
                for o in out.links:
                    if o.is_valid:
                        o.to_socket.set_value(out.get_value())
                        o.to_socket.node.update_value()
