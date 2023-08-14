'''
Global list of registered classes with search names.
'''

import bpy

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

import pynodes

node_registry_dict = {}

node_classes = []

operator_classes = []

def registerNodeType(clazz):

    try:
        category = clazz.mmod
    except AttributeError as ae:
        category = 'Custom'

    if category.startswith('_'):
        return

    if not category in node_registry_dict.keys():
        node_registry_dict[category] = []
    node_registry_dict[category].append(clazz)

    if not clazz in node_classes:
        node_classes.append(clazz)

def registerOperator(clazz):

    if clazz not in operator_classes:
        operator_classes.append(clazz)

def unregisterAll():
    try:
        nodeitems_utils.unregister_node_categories('pythonGlobalFuncs')
        for cls in reversed(node_classes):
            bpy.utils.unregister_class(cls)
        for cls in reversed(operator_classes):
            bpy.utils.unregister_class(cls)
    except RuntimeError as re:
        print('re', re, 'caught')

def registerAll():
    node_categories = []

    for cls in operator_classes:
        bpy.utils.register_class(cls)

    i = 0
    for category, clazzes in sorted(node_registry_dict.items()):
        cat = pynodes.PythonCompositorNodeCategory(
            f'PythonNode_{i:09d}',# category.replace('.', '_'),
            category,
            items=
            [
                NodeItem(clazz.bl_idname)
                for clazz in clazzes if not clazz.bl_idname.split('.')[-1].startswith('_')
            ]
        )
        
        node_categories.append(cat)
        i+=1

    for cls in node_classes:
        bpy.utils.register_class(cls)

    nodeitems_utils.register_node_categories('pythonGlobalFuncs', node_categories)
