import pynodes
from pynodes import nodes
import time
import bpy
import inspect
import traceback

class APIEndpointInterface:
    
    def get_signature():
        pass

    def get_documentation():
        pass

class BlenderPythonAPIEndpoint(APIEndpointInterface):
    
    def __init__(self, api_endpoint_string):
        self.api_endpoint_string = api_endpoint_string
        self.api = eval(self.api_endpoint_string)
    
    def get_signature(self):
        try:
            return inspect.signature(self.api)
        except:
            return inspect.Signature(
                [
                    inspect.Parameter('unknown_posarg', inspect.Parameter.VAR_POSITIONAL, default=inspect.Parameter.empty, annotation=inspect.Parameter.empty),
                    inspect.Parameter('unknown_keyarg', inspect.Parameter.VAR_KEYWORD, default=inspect.Parameter.empty, annotation=inspect.Parameter.empty)
                ],
                return_annotation=inspect.Signature.empty
            )
    
    def get_documentation(self):
        return inspect.getdoc(self.api)

class AnyNode(nodes.PythonNode):
    # === Basics ===
    # Description string
    '''A node which takes on the form of the specified API.'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'AnyNode'
    # Label for nice name display
    bl_label = "Any Node"

    api_endpoint_string : bpy.props.StringProperty(
        name='',
        description="Callable API endpoint.",
        update=lambda s,c:s.update_api(c)
    )
    
    api_documentation : bpy.props.StringProperty(
        description='Documentation for the API endpoint.'
    )

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "api_endpoint_string")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        # maybe add a label to say its the api string
        
        layout.prop(self, "api_endpoint_string")
        
        layout.label(text=self.api_documentation) # show the documentation for this api
        # perhaps make this multiline

    def init(self, context):
        super().init(context)
    
    def run(self):
        super().run(eval(self.label))

    def update(self):
        print(f'node {self.name} updated')
    
    def update_api(self, context):
        # can force the api string to be auto-corrected, etc.
        self.label = self.api_endpoint_string
        self.set_no_color()
        
        try:
            api = BlenderPythonAPIEndpoint(self.api_endpoint_string)
        except:
            self.set_color([1,0,0])
            print(traceback.format_exc())
            return
        
        try:
            self.api_documentation = api.get_documentation()
        except:
            self.api_documentation = 'No documentation found!'
            print(traceback.format_exc())
        
        self.inputs.clear()
        self.outputs.clear()
        
        try:
            sig = api.get_signature()
            includes_varargs = False
            includes_kwargs = False
            for param_name in sig.parameters:
                param = sig.parameters[param_name]
                
                if param.kind==inspect.Parameter.POSITIONAL_OR_KEYWORD or param.kind==inspect.Parameter.POSITIONAL_ONLY:
                    if param.annotation!=inspect.Parameter.empty:
                        key = param_name + ': ' + param.annotation
                    else:
                        key = param_name
                    
                    self.inputs.new(pynodes.PyObjectSocket.bl_idname, key)
                    
                    if param.default!=inspect.Parameter.empty:
                        self.inputs[key].argvalue = str(param.default)
                    
                elif param.kind==inspect.Parameter.VAR_POSITIONAL:
                    includes_varargs = True
                else:
                    includes_kwargs = True
            
            if includes_varargs:
                self.inputs.new(pynodes.PyObjectSocket.bl_idname, '*args')
            if includes_kwargs:
                self.inputs.new(pynodes.PyObjectSocket.bl_idname, '**kwargs')
            
            if sig.return_annotation!=inspect.Signature.empty:
                self.outputs.new(pynodes.PyObjectSocket.bl_idname, sig.return_annotation)
            else:
                self.outputs.new(pynodes.PyObjectSocket.bl_idname, 'Any')
        except:
            self.set_color([1,0,0])
            print(traceback.format_exc())
            # self.inputs.clear()
            # self.outputs.clear()
            return
        

from pynodes import registry
registry.registerNodeType(AnyNode)
