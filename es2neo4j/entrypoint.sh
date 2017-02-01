#!/bin/bash

set -e

if [ "${1:0:1}" = '-' ]; then
	set -- python3 import_es_data.py "$@"
fi

exec "$@"
