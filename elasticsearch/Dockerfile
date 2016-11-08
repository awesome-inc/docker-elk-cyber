FROM elasticsearch:5

COPY *.sh /
RUN chmod +x /*.sh
RUN /install-plugins.sh

COPY elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["elasticsearch"]
