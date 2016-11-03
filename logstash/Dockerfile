FROM logstash:5

# Add your logstash plugins setup here
# Copy source files
COPY logstash-input-rss2/ /usr/share/logstash-input-rss2/

# Install dependencies
RUN PATH=${PATH}:/usr/share/logstash/vendor/jruby/bin gem install bundle && \
	cd /usr/share/logstash-input-rss2 && \
	PATH=${PATH}:/usr/share/logstash/vendor/jruby/bin bundle install

# Install to logstash
RUN cd /usr/share/logstash && \
	echo 'gem "logstash-input-rss2", :path => "/usr/share/logstash-input-rss2"' >> Gemfile && \
	logstash-plugin install --no-verify

RUN rm /etc/logstash/log4j2.properties

EXPOSE 5044
CMD ["-f", "/etc/logstash/conf.d"]
