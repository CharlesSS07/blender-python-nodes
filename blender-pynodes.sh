#!/usr/bin/env bash

# ./prepare-blender-addon.sh

BLENDER_EXECUTABLE='flatpak run org.blender.Blender'

$BLENDER_EXECUTABLE $PWD/.tmp.blend -P $PWD/pynodes/__init__.py
