FROM logstash:5

# Add your logstash plugins setup here
# Example: RUN logstash-plugin install logstash-filter-json 

RUN rm /etc/logstash/log4j2.properties

EXPOSE 5000
CMD ["-f", "/etc/logstash/conf.d"]
