#!/usr/bin/env bash

set -e

find pat-mat \
	-type d -name migrations -prune -o \
	-type f -name "*.py" \
	-exec "$@" {} +
