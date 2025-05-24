#!/bin/bash

set -ex

SCRIPT_DIR=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
cd $SCRIPT_DIR

source ../envvars

./gen_filters.py

birdc configure
