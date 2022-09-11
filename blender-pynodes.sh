#!/usr/bin/env bash

BLENDER_EXECUTABLE='/Applications/Blender.app/Contents/MacOS/Blender'

$BLENDER_EXECUTABLE $PWD/.tmp.blend -P $PWD/install-pynodes.py
