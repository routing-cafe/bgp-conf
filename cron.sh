#!/bin/bash

set -ex

./gen_filter_irr.sh
./gen_prefix_limits.py

birdc configure
