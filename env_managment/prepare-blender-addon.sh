#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

ENV_NAME=$1

# cp $SCRIPT_DIR/__init__.py $SCRIPT_DIR/envs/$ENV_NAME/
cat > $SCRIPT_DIR/envs/$ENV_NAME.py <<- EOM
bl_info = {
    "name": "$ENV_NAME Python Environment",
    "description": "Allows installation of custom python environments without directly modifying blenders python environment. Useful for installing tensorflow in an encapsulated manner.",
    "author": "Charles M. S. Strauss",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "Console",
    "warning": "Only tested on linux, and Mac, not built for windows.", # used for warning icon and text in addons panel
    "support": "COMMUNITY",
    "category": "Console",
}

def register():

    import sys
    import os

    script_dir = "$SCRIPT_DIR/envs/$ENV_NAME/"

    sys.path.append(os.path.join(script_dir, 'bin'))
    sys.path.append(os.path.join(script_dir, 'lib', 'python3.10'))
    sys.path.append(os.path.join(script_dir, 'lib', 'python3.10', 'site-packages'))
    
    print('Registered $ENV_NAME Python Environment')

def unregister():
    print('$ENV_NAME Python Environment not unregistered. Restart blender witout addon enabled to fully unregister')

register()
EOM

# cd $SCRIPT_DIR/envs/
# zip -r $ENV_NAME.zip $ENV_NAME
