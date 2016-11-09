FROM neo4j:3.0.6

ENV APOC_VERSION 3.0.4.2

ADD https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/${APOC_VERSION}/apoc-${APOC_VERSION}-all.jar /var/lib/neo4j/plugins

COPY *.sh /

# customized neo4j shell script to support JAVA_OPTS (proxy)
COPY bin/neo4j.sh bin/neo4j

ENTRYPOINT ["/docker-entrypoint2.sh"]
CMD ["neo4j"]