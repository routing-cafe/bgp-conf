#!/bin/bash

set -ex

SCRIPT_DIR=$(dirname -- "$(readlink -f -- "$BASH_SOURCE")")
cd $SCRIPT_DIR

set -a
source ../envvars
set +a

./gen_filters.py

birdc configure
