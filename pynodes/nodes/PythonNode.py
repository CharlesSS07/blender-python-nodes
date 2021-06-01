import pynodes
import traceback
import bpy

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class PythonCompositorTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == pynodes.PythonCompositorTree.bl_idname

class ColorfulNode(bpy.types.Node):
    # === Basics ===
    # Description string
    '''Abstract node that can change colors.'''

    def init(self, context):
        pass

    def set_color(self, color):
        self.use_custom_color = True
        self.color = color

    def set_no_color(self):
        self.use_custom_color = False

# Derived from the Node base type.
# Defines functionality of python node to only require that call is overloaded
class PythonNode(ColorfulNode, PythonCompositorTreeNode):
    # === Basics ===
    # Description string
    '''Abstract python node.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonNode'
    # Label for nice name display
    bl_label = "Python Node"
    # Icon identifier
    bl_icon = 'SCRIPT'

    # class Properties:
    is_dirty = True
    # bpy.props.BoolProperty(
    #     name='dirty',
    #     default=True
    # )

    class PythonNodeRunError(Exception):
        '''
        raised when a node has an error.
        '''
        def __init__(self, node, e):
            self.node = node
            self.ex = e
            super().__init__(
                f'Exception raised by node {node.bl_idname}:\n{e}'
            )

    def mark_dirty(self):
        '''
        Propogate to all downstream nodes that this nodes is not up to date.
        '''
        print('is_dirty', self.is_dirty)
        self.is_dirty = True
        print(self.is_dirty)
        self.set_no_color()
        for k in self.outputs.keys():
            out = self.outputs[k]
            if out.is_linked:
                for o in out.links:
                    node = o.to_socket.node
                    #if not node is self and o.is_valid and not node.get_dirty():
                    if not node is self:
                        node.mark_dirty()


    def get_dirty(self):
        return self.is_dirty

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
        and set outputs using self.set_output.
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

    # def update_value(self):
    #     '''
    #     Called when a value changes (links, or node settings). Runs node unless
    #     this node is not connected to a base node. Propagates the nodes outputs
    #     to the linked nodes, and calls update_value on them.
    #     '''
    #     if self.is_connected_to_base():
    #         try:
    #             self.run()
    #             self.set_color([0.0, 0.5, 0.0])
    #         except Exception as e:
    #             print(f'Node "{self.bl_label}" raised an exception:')
    #             print(e)
    #             self.set_color([0.5, 0.0, 0.0])
    #         self.propagate()

    def update(self):
        '''
        Called when the node tree changes.
        '''
        self.mark_dirty()
        # mark node, and downstream nodes as dirty/not current
        # self.update_value()

    def interrupt_execution(self, e):
        raise PythonNode.PythonNodeRunError(self, e)

    def compute_output(self):
        for k in self.inputs.keys():
            inp = self.inputs[k]
            if inp.is_linked:
                for i in inp.links:
                    node = i.from_socket.node
                    if not node is self and i.is_valid and node.get_dirty():
                        node.compute_output()
        try:
            self.run()
            self.is_dirty = False
            print('is_dirty', self.is_dirty)
            self.propagate()
            self.set_color([0.0, 0.5, 0.0])
        except Exception as e:
            # self.mark_dirty()
            self.set_color([0.5, 0.0, 0.0])
            traceback.print_exc()
            self.interrupt_execution(e)

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
                        # o.to_socket.node.update_value()
