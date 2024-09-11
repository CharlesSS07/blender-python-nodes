
from pynodes.nodes.PythonNode import PythonNode
from pynodes.nodes.PythonBaseNode import PythonBaseNode

from pynodes.nodes.PythonLoadImageNode import PythonLoadImageNode
from pynodes.nodes.PythonSaveImageBaseNode import PythonSaveImageBaseNode
from pynodes.nodes.PythonPrintResultBaseNode import PythonPrintResultBaseNode
from pynodes.nodes.PythonWaitSecondsNode import PythonWaitSecondsNode
from pynodes.nodes.PythonShowArrayShapeBaseNode import PythonShowArrayShapeBaseNode
from pynodes.nodes.PythonNodeGroupNodes import *

from pynodes.nodes.AutoNodeTypeAdder import add_basic_nodes

add_basic_nodes()
