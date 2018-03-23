ARG VERSION=6.2.3
FROM docker.elastic.co/elasticsearch/elasticsearch-oss:${VERSION}

COPY *.sh /
RUN /install-plugins.sh

COPY elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["elasticsearch"]
