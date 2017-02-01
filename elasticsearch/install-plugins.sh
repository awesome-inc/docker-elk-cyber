#!/bin/bash
set -e

source /config-proxy.sh

bin/elasticsearch-plugin install ingest-attachment

nlp_version=${ELASTICSEARCH_VERSION}.1
bin/elasticsearch-plugin install https://oss.sonatype.org/content/repositories/releases/de/spinscale/elasticsearch/plugin/ingest/ingest-opennlp/${nlp_version}/ingest-opennlp-${nlp_version}.zip 

# fix some strange configuration conflicts between elasticsearch, elasticsearch-plugin & opennlp-plugin
mv /etc/elasticsearch/ingest-opennlp /usr/share/elasticsearch/config
chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config