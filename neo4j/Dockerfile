FROM neo4j:3.0.6

ENV APOC_VERSION 3.0.4.2

ADD https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/${APOC_VERSION}/apoc-${APOC_VERSION}-all.jar /var/lib/neo4j/plugins

COPY *.sh /

ENTRYPOINT ["/docker-entrypoint2.sh"]
CMD ["neo4j"]