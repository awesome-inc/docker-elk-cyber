ARG ELK_VERSION
FROM docker.elastic.co/elasticsearch/elasticsearch-oss:${ELK_VERSION}

ARG ELK_VERSION
ENV ELK_VERSION $ELK_VERSION
COPY ingest-opennlp-*.zip *.sh ./
RUN ./install-plugins.sh

