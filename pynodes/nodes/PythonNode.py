from typing import overload

from setuptools.sandbox import override_temp

import pynodes
import traceback
import bpy
import numpy as np

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class PythonCompositorTreeNode:
    @classmethod
    def poll(cls, ntree):
        # classes extending this will only appear in the python node tree
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
        # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)

    def set_no_color(self):
        self.use_custom_color = False
        # bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)

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
        self.is_dirty = True
        self.set_no_color()
        for k in self.outputs.keys():
            out = self.outputs[k]
            if out.is_linked:
                for o in out.links:
                    node = o.to_socket.node
                    if not node is self and o.is_valid and not node.get_dirty():
                        node.mark_dirty()


    def get_dirty(self):
        return self.is_dirty

    def is_connected_to_base(self):
        '''
        Return true if this node is connected to a node which is a "base" node.
        '''
        # BFS in direction of output nodes; find the first base node

        if isinstance(self, pynodes.nodes.PythonBaseNode):
            return True

        not_explored = [self]
        explored = set()

        while len(not_explored)>0:
            n = not_explored.pop()

            # explore n
            for k in n.outputs.keys():
                out = n.outputs[k]
                if out.is_linked:
                    for link in out.links:
                        if link.to_socket.node in explored:
                            continue

                        if link.is_valid and isinstance(link, pynodes.nodes.PythonBaseNode):
                            return True

                        not_explored.append(link.to_socket.node)

            explored.add(n)

        return False

    def run(self):
        '''
        Do whatever calculations this node does. Take input from self.get_input
        and set outputs using self.set_output.
        '''
        pass

    def get_input(self, k, default_func=lambda:None):
        '''
        Called by run to get value stored behind socket.
        '''
        v = self.inputs[k]
        if v.is_linked and len(v.links)>0 and v.links[0].is_valid:
            o = v.links[0].from_socket
            # from sockets are always the first link; don't ever want to have more than one for simplicity
            value = o.get_value()
            return value

        return v.get_value() # gets value from argval input box

    def set_output(self, k, v):
        self.outputs[k].set_value(v)

    update_subscribers = []

    def subscribe_to_update(self, callback):
        self.update_subscribers.append(callback)

    def unsubscribe_to_update(self, callback):
        if callback in self.update_subscribers:
        	self.update_subscribers.remove(callback)

    def update(self):
        '''
        Called when the node tree changes.
        '''
        if not self.get_dirty():
        	self.mark_dirty()
            # mark node, and downstream nodes as dirty/not current
        
        for socket in self.inputs:
            if isinstance(socket, pynodes.AbstractPyObjectSocket):
                socket.node_updated()
        # call all socket callbacks and other subscribers
        for callback in self.update_subscribers:
            try:
                callback()
            except Exception as e:
                print('Encountered error while executing node update callback.')
                traceback.print_exc()
                # self.unsubscribe_to_update(callback)

    def interrupt_execution(self, e):
        raise PythonNode.PythonNodeRunError(self, e)

    def compute_output(self):
        # print(self, 'compute_output')
        try:
            if self.get_dirty():
                self.set_color([0.0, 0.0, 0.5])
                self.run()
                self.is_dirty = False
            # self.propagate()
            self.set_color([0.0, 0.5, 0.0])
        except Exception as e:
            self.mark_dirty()
            self.set_color([0.5, 0.0, 0.0])
            traceback.print_exc()
            self.interrupt_execution(e)

    # def propagate(self):
    #     '''
    #     Pass this nodes outputs to nodes linked to outputs.
    #     '''
    #     for out in self.outputs:
    #         if out.is_linked:
    #             for link in out.links:
    #                 if link.is_valid:
    #                     link.to_socket.set_value(out.get_value())