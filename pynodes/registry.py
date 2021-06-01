'''
Global list of registered classes with search names.
'''

import bpy

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

import pynodes

registryDict = {}

classes = []

def registerNodeType(clazz):

    try:
        category = clazz.mmod
    except AttributeError as ae:
        category = 'Custom'

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

    for category, clazzes in sorted(registryDict.items()):
        cat = pynodes.PythonCompositorNodeCategory(category.replace('.', '_'), category, items=
                list([
                    NodeItem(clazz.bl_idname)
                for clazz in clazzes])
            )
        node_categories.append(cat)

    for cls in classes:
        bpy.utils.register_class(cls)

    nodeitems_utils.register_node_categories('pythonGlobalFuncs', node_categories)
