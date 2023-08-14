#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

ENV_NAME=tensorflow_blender

ENV_PATH="$SCRIPT_DIR/envs/$ENV_NAME/"

echo $ENV_PATH

mkdir -p $ENV_PATH

# create locally installed tensorflow environment
# use blender's current python version
# install certifi correctly (blender python does not have all required files I think)
conda create \
	--prefix $ENV_PATH \
	--yes \
	python=3.10

conda install \
	--yes \
	--prefix $ENV_PATH \
	-c conda-forge \
	tensorflow \
	tensorflow-datasets

# conda install \
# 	--yes \
# 	--prefix $ENV_PATH \
#	pytorch::pytorch torchvision torchaudio -c pytorch

echo Created environment $ENV_NAME
