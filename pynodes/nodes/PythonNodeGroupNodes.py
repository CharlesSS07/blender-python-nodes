import pynodes
from pynodes import nodes
import time
import bpy
import numpy as np

from pynodes import registry
from bpy.utils import register_class

class PythonNodeGroupIOSocket(pynodes.AbstractPyObjectSocket.Properties, pynodes.AbstractPyObjectSocket):
    ''' PyNodes node socket type for group input and output nodes'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonNodeGroupIOSocket'
    # Label for nice name display
    bl_label = "PyNodes Node Group Input/Output Object Socket"
    
#     def __init__(self):
#         super().__init__()
#         # pin shape
#         self.display_shape = 'CIRCLE'
    
    def argvalue_updated(self):
        super().argvalue_updated()
        print('updated')
    
    def get_value(self):
        if self.identifier in self._value_[0]:
            return self._value_[0][self.identifier]
        else:
            return None
        
    def draw(self, context, layout, node, text):
        layout.prop(self, 'argvalue', text='')

register_class(PythonNodeGroupIOSocket)

class AbstractPyNodesGroupIONode(nodes.PythonNode):
    '''A socket that is matched to sockets on an input or output node, and has a name associated with it'''
    bl_category = 'Groups'

    def run(self):
        pass
    
    def update(self):
        super().update()
        ng = self.id_data.nodes.id_data
        for ang in bpy.data.node_groups:
            if ang!=ng:
                for n in ang.nodes:
                    if n!=self: # might not be required
                        if n.bl_idname==PythonNodeGroupNode.bl_idname and n.node_group==ng.name:
                            n.setup_sockets()

class PyNodesGroupInputsNode(AbstractPyNodesGroupIONode):
    # === Basics ===
    # Description string
    '''Input to node group. Exposes inputs from a group node using this node group.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PyNodesGroupInputsNode'
    # Label for nice name display
    bl_label = "Group Input"

    def init(self, context):
        super().init(context)
        self.outputs.new(PythonNodeGroupIOSocket.bl_idname, "Inputs")

registry.registerNodeType(PyNodesGroupInputsNode)

class PyNodesGroupOutputsNode(AbstractPyNodesGroupIONode):
    # === Basics ===
    # Description string
    '''Output to node group. Exposes outputs to a group node using this node group.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PyNodesGroupOutputsNode'
    # Label for nice name display
    bl_label = "Group Output"

    def init(self, context):
        super().init(context)
        self.inputs.new(PythonNodeGroupIOSocket.bl_idname, "Outputs")

registry.registerNodeType(PyNodesGroupOutputsNode)

class PythonNodeGroupNode(nodes.PythonNode):
    # === Basics ===
    # Description string
    '''A group node, which executes nodes in a node group.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'PythonNodeGroupNode'
    # Label for nice name display
    bl_label = "Node Group"
    bl_category = 'Groups'
    
    node_group : bpy.props.StringProperty(
        name='Node Group',
        description="Stores the node group to execute.",
        update=lambda s,c:s.node_group_changed()
    )
    
    node_group_collection : bpy.props.CollectionProperty(
        name='Node Group Selector',
        type=bpy.types.PropertyGroup
    )
    
    def update(self):
        super().update()
        self.update_node_group_collection()
    
    def node_group_changed(self):
        self.setup_sockets()
        self.update()
    
    def update_node_group_collection(self):
        self.node_group_collection.clear()
        for a in bpy.data.node_groups:
            self.node_group_collection.add().name = a.name
    
    def get_input_node_sockets(self):
        ng = bpy.data.node_groups[self.node_group]
        input_nodes = [
            n
            for n in ng.nodes
            if n.bl_idname==PyNodesGroupInputsNode.bl_idname
        ]
        if len(input_nodes)>=1:
            return input_nodes[0].outputs
        else:
            return []
    
    def get_output_node_sockets(self):
        ng = bpy.data.node_groups[self.node_group]
        output_nodes = [
            n
            for n in ng.nodes
            if n.bl_idname==PyNodesGroupOutputsNode.bl_idname
        ]
        if len(output_nodes)>=1:
            return output_nodes[0].inputs
        else:
            return []
    
    def setup_sockets(self):
        
        if self.node_group=='':
            # for the case where the node group selector was just cleared
            self.label = 'Node Group'
            self.inputs.clear()
            self.outputs.clear()
            return
        
        self.label = self.node_group
    
        ng = bpy.data.node_groups[self.node_group]
        
        input_node_outputs = self.get_input_node_sockets()
        # needs a behavior when there is no input node. should be own function
        output_node_inputs = self.get_output_node_sockets()
        # needs a behavior when there is no output node. should be own function
        
        # remove the sockets that are not going to be re-used from inputs
        input_keys = [s.argvalue for s in input_node_outputs]
        for in_socket in self.inputs:
            if in_socket.identifier not in input_keys:
                self.inputs.remove(in_socket)
        
        # add sockets we don't already have to self.inputs
        for i, in_socket in enumerate(input_node_outputs):
            if in_socket.argvalue in self.inputs.keys(): # skip all the ones we already have
                print('moving', in_socket.argvalue, i)
                self.inputs.move(self.inputs.find(in_socket.identifier), i)
                continue
            if not in_socket.is_empty():
                self.inputs.new(pynodes.PyObjectSocket.bl_idname, in_socket.argvalue)
        
        # remove the sockets that are not going to be re-used from outputs
        output_keys = [s.argvalue for s in output_node_inputs]
        for out_socket in self.outputs:
            if out_socket.identifier not in output_keys:
                self.outputs.remove(out_socket)
        
        # add sockets we don't already have to self.outputs
        for i, out_socket in enumerate(output_node_inputs):
            if out_socket.argvalue in self.outputs.keys(): # skip all the ones we already have
                print('moving', out_socket.argvalue, i)
                self.outputs.move(self.outputs.find(out_socket.identifier), i)
                continue
            if not out_socket.is_empty():
                self.outputs.new(pynodes.PyObjectSocket.bl_idname, out_socket.argvalue)
        
    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'node_group', self, 'node_group_collection', text='')

    def init(self, context):
        super().init(context)
        self.update_node_group_collection()

    def run(self):
        
        ng = bpy.data.node_groups[self.node_group]
        
        input_node = [n for n in ng.nodes if n.bl_idname==PyNodesGroupInputsNode.bl_idname ][0]
        output_node= [n for n in ng.nodes if n.bl_idname==PyNodesGroupOutputsNode.bl_idname][0]
        
        for in_socket in self.inputs:
            if not in_socket.is_empty():
                for out_socket in input_node.outputs:
                    if out_socket.argvalue==in_socket.identifier:
                        input_node.set_output(out_socket.identifier, in_socket.get_value())
                        break
            
        # run computations between input and output nodes for given inputs
        
        output_node.compute_output()
        
        for out_socket in output_node.inputs:
            if not out_socket.is_empty():
                self.set_output(out_socket.argvalue, output_node.get_input(out_socket.identifier))

registry.registerNodeType(PythonNodeGroupNode)
