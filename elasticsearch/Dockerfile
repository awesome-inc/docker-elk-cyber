ARG VERSION=6.2.3
FROM docker.elastic.co/elasticsearch/elasticsearch-oss:${VERSION}

ARG VERSION=6.2.3
ENV ELASTICSEARCH_VERSION $VERSION
COPY ingest-opennlp-*.zip *.sh ./
RUN ./install-plugins.sh

