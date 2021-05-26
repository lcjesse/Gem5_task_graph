#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 [model directory]" >&2
    exit 1
fi
for i in 1 2 3 4
do
    python Traffic_Generator.py -f ${1}/Application_0${i}.info
done

exit 0