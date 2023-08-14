# Blender Python Environment Manager
Ever wanted to install extra python packages for use in blender addons?

Blender Python Environment Manager allows you to add python packages like tensorflow directly to blender witout directly modifying its own environment. It does this by creating a custom python environment with the desired packages in it using conda, and adding the correct paths from that environment to blenders sys.paths insance.

By Charles M. S. Strauss

# Dependencies:
	1. bash
	2. conda

# How to:
	1. Edit ./install-environment.sh to include desired packages on conda line.
	2. `./install-environment.sh <environment-name>`
	3. `./prepare-blender-addon.sh <environment-name>`

