#!/usr/bin/env bash

# This is not necessary for production; This script simply automates the process of starting blender and installing the newest version of the addon.
# In production, the user would install this addon from pynodes.zip and never need to resinstall it, whereas development requires reinstalling constantly.

BLENDER_EXECUTABLE='/Applications/Blender.app/Contents/MacOS/Blender'

$BLENDER_EXECUTABLE $PWD/.tmp.blend -P $PWD/install-pynodes.py
