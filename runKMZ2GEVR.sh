#!/bin/bash

export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
python kmz2gevr/kmz2gevr.py "$@"
