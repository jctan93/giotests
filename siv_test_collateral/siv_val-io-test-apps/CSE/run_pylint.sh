#!/bin/bash

#TODO:
# 1. get baseline and diff against it

for f in $(git log -1 --format="" --name-only HEAD); do
	if  [ "${f##*.}" == "py" ] ; then
		pylint --reports=no --output-format=parseable $f;
	fi
done
