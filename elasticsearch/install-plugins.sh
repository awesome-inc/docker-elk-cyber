#!/bin/bash
set -e

source /config-proxy.sh

bin/elasticsearch-plugin install https://bintray.com/awesome-inc/generic/download_file?file_path=ingest-opennlp-0.0.1-SNAPSHOT.zip

# fix some strange configuration conflicts between elasticsearch, elasticsearch-plugin & opennlp-plugin
mv /etc/elasticsearch/ingest-opennlp /usr/share/elasticsearch/config
chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config