#!/usr/bin/env bash

# ./prepare-blender-addon.sh

BLENDER_EXECUTABLE='flatpak run org.blender.Blender'

<<<<<<< HEAD
$BLENDER_EXECUTABLE $PWD/.tmp.blend -P $PWD/install-pynodes.py

#-P $PWD/pynodes/__init__.py
=======
$BLENDER_EXECUTABLE $PWD/.tmp.blend -P $PWD/pynodes/__init__.py
>>>>>>> main
