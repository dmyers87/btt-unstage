#!/bin/sh
# PLACE IN .git/hooks

current_branch=$(git branch --show-current)

if [[ $current_branch == "master" ]]; then
	./build-and-push-image.sh
fi


