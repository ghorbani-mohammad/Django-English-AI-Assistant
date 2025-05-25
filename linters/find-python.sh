#!/usr/bin/env bash

set -e

find english-assistant \
	-type d -name migrations -prune -o \
	-type f -name "*.py" \
	-exec "$@" {} +
