
'''
import os

nodes_dir, _ = os.path.split(__file__)

import glob

files = glob.glob(os.path.join(nodes_dir, '*py'))

for fn in files:
    if not '__' in os.path.basename(fn):
        print('importing', os.path.basename(fn))
        __import__(os.path.basename(fn))
'''

from pynodes.nodes.PythonNode import PythonNode
from pynodes.nodes.PythonBaseNode import PythonBaseNode

from pynodes.nodes.PythonLoadImageNode import PythonLoadImageNode
from pynodes.nodes.PythonSaveImageBaseNode import PythonSaveImageBaseNode
from pynodes.nodes.PythonPrintResultBaseNode import PythonPrintResultBaseNode
from pynodes.nodes.PythonWaitSecondsNode import PythonWaitSecondsNode

from pynodes.nodes.AutoNodeTypeAdder import add_basics
add_basics()
