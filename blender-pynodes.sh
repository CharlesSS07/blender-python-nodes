#!/usr/bin/env bash

BLENDER_EXECUTABLE='flatpak run org.blender.Blender'

$BLENDER_EXECUTABLE $PWD/.tmp.blend -P $PWD/install-pynodes.py
