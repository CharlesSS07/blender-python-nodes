#!/usr/bin/env bash

# This prepares a production-ready file for distributing pynodes, in the form of pynodes.zip
# pynodes.zip can be added to blender by the consumer.

rm pynodes.zip
zip -r pynodes.zip pynodes --exclude *__pycache__*
