#!/bin/bash

set -e

echo "-> Waiting for ElasticSearch to come up"
while true; do
	nc -q 1 elasticsearch 9200 2>/dev/null && break
done

# ES is running here
# Check if initial import already took place

if [[ -d /initial_import && ! -f /initial_import/import_done ]]; then
	echo "-> Initial import about to be started, waiting another 5s to be sure ES is running"
	sleep 5
	
	pushd /initial_import
	find . -name "*.json" | while IFS= read -r fname; do
		name=${fname%.json}
		name=${name:2}
		name=${name//_x_/*}
		echo
		echo "-> PUTting '${name}' ..."
		curl -s -X PUT "http://elasticsearch:9200/${name}" -T $fname
	done
	popd
	
	touch /initial_import/import_done
fi
