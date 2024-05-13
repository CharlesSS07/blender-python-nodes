import pynodes
from pynodes import nodes
import numpy as np
import bpy
import networkx as nx

from pynodes.nodes.AnyNode import BlenderPythonAPIEndpoint

def blender_python_kernel(code):
    eval(code)

class AnyBaseNode(nodes.PythonBaseNode.Properties, nodes.PythonBaseNode):
    # === Basics ===
    # Description string
    '''Execute connected AnyNodes'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'AnyBaseNode'
    # Label for nice name display
    bl_label = "Execute connected AnyNodes"
    
    _cache_ = [{}] # immutable lookup of node names to variables names in some kernel

    def init(self, context):
        super().init(context)
        self.inputs.new(pynodes.PyObjectSocket.bl_idname, "Result")

    def run(self):
        G = nx.DiGraph()
        
        # BFS to find all connected nodes, add connectsion to dependency graph G
        leaves = []
        branches = [self]
        while len(branches)>0:
            for branch in branches:
                for input_socket in branch.inputs:
                    if len(input_socket.links)==0:
                        continue
                    node = input_socket.links[0].from_socket.node
                    G.add_edge(node.name, branch.name)
                    leaves.append(node)
            branches = leaves
            leaves = []
            print(len(branches), len(leaves))
        
        # use the dependency graph to determine execution order of the nodes
        print(G.edges)
        # if nx.is_directed_acyclic_graph(G)>0:
        #     raise Exception('Cycles detected in node graph!')
        
        # should be a Directed Acyclic Graph
        print(list(nx.topological_sort(G)))
        
        while len(G)>0:
            
            # ignoring all caching, and just recomputing whole graph upon every run
            
            leaves = [x for x in G.nodes() if G.out_degree(x)==0 and G.in_degree(x)==1]
            
            for leave in leaves:
                api = BlenderPythonAPIEndpoint(leave.api_endpoint_string)
                # get parameters, and composite an execution of the function with corresponding filled in variables from kernel

from pynodes import registry
registry.registerNodeType(AnyBaseNode)
