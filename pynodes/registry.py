'''
Global list of registered classes with search names.
'''

import bpy

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
<<<<<<< HEAD
=======
<<<<<<< HEAD

import pynodes

registryDict = {}

classes = []

def registerNodeType(clazz):


    category = clazz.bl_idname.split('.')[0]

    if not category in registryDict.keys():
        registryDict[category] = []
    registryDict[category].append(clazz)

    if not clazz in classes:
        classes.append(clazz)



def unregisterAll():
    try:
        nodeitems_utils.unregister_node_categories('pythonGlobalFuncs')
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
    except RuntimeError as re:
        print('re', re, 'caught')

def registerAll():
    node_categories = []

    for category, clazzes in registryDict.items():
        cat = pynodes.PythonCompositorNodeCategory(category, category, items=
                list([
                    NodeItem(clazz.bl_idname)
                for clazz in clazzes])
            )
        node_categories.append(cat)

    for cls in classes:
        bpy.utils.register_class(cls)

=======
>>>>>>> 49e4c650ea426d707e98ccd2725d5f4d6b2ff6a6

from pynodes import pythonnodes

registryDict = {}

classes = []

def registerNodeType(clazz, full_name):


    category = full_name.split('.')[0]

    if not category in registryDict.keys():
        registryDict[category] = []
    registryDict[category].append(clazz)

    if not clazz in classes:
        classes.append(clazz)



def unregisterAll():
    try:
        nodeitems_utils.unregister_node_categories('pythonGlobalFuncs')
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
    except RuntimeError as re:
        print('re', re, 'caught')

def registerAll():
    node_categories = []
    
    for category, clazzes in registryDict.items():
        cat = pythonnodes.PythonCompositorNodeCategory('test', 'test2', items=
                list([
                    NodeItem(clazz.bl_idname)
                for clazz in clazzes])
            )
        node_categories.append(cat)

    for cls in classes:
        bpy.utils.register_class(cls)

<<<<<<< HEAD
=======
>>>>>>> main
>>>>>>> 49e4c650ea426d707e98ccd2725d5f4d6b2ff6a6
    nodeitems_utils.register_node_categories('pythonGlobalFuncs', node_categories)
