import sys
import os
sys.path.append(os.path.split(__file__)[0])

print('installing environment into blender')

# import env_managment.envs.pytorch_blender as pytorch_blender
# pytorch_blender.register()
import env_managment.envs.tensorflow_blender as tensorflow_blender
tensorflow_blender.register()

print('installed environment into blender')

import tensorflow
import tensorflow_datasets

print('imported environment packages')

import pynodes
import pynodes.nodes

print('registering pynodes')

pynodes.register()

print('pynodes was registered')
