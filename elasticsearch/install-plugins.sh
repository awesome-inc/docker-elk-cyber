#!/bin/bash
set -e

source ./config-proxy.sh

#bin/elasticsearch-plugin install ingest-attachment

nlp_version=${ELASTICSEARCH_VERSION}.1
nlp_file=ingest-opennlp-${nlp_version}.zip
nlp_url=https://github.com/spinscale/elasticsearch-ingest-opennlp/releases/download/${nlp_version}/${nlp_file}
if [ -e "${PWD}/${nlp_file}" ]; then nlp_url=file://${PWD}/${nlp_file}; fi
bin/elasticsearch-plugin install ${nlp_url} 
