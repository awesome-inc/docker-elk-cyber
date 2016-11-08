FROM logstash:5

# Add your logstash plugins setup here
# Copy source files
COPY logstash-input-rss2/ /usr/share/logstash-input-rss2/

# Install dependencies
COPY *.sh /
RUN chmod +x /*.sh
RUN /install-plugins.sh

COPY log4j2.properties /etc/logstash/log4j2.properties

EXPOSE 5044

ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["-f", "/etc/logstash/conf.d"]
