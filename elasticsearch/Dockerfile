FROM elasticsearch:5

ENV ES_JAVA_OPTS="-Des.path.conf=/etc/elasticsearch"

RUN /usr/share/elasticsearch/bin/plugin-install https://bintray.com/awesome-inc/generic/download_file?file_path=ingest-opennlp-0.0.1-SNAPSHOT.zip

CMD ["-E", "network.host=0.0.0.0", "-E", "discovery.zen.minimum_master_nodes=1"]
