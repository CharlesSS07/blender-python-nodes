bl_info = {
    "name": "Python Nodes",
    "description": "The power of python, brought to you through blender nodes.",
    "author": "Charles M. S. Strauss<charles.s.strauss@gmail.com>, and Robert R. Strauss<robert.r.strauss@icloud.com>",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "Console",
    "warning": "Requires user has tensorflow, pytorch installed using blender python environment manager TODO: include link", # used for warning icon and text in addons panel
    "support": "COMMUNITY",
    "category": "Nodes",
}

from pynodes import pythonnodes

from pynodes import AutoNodeTypeAdder

from pynodes import registry





def register():
    AutoNodeTypeAdder.addAllGlobals()
    registry.registerAll()

def unregister():
    registry.unregisterAll()

if __name__ == '__main__':
    try:
        unregister()
    except Exception as e:
        print('no unregistering needed (problem?) e:', e)
        register()
