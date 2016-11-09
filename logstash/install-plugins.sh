#!/bin/bash
set -e

source /config-proxy.sh

PATH=${PATH}:/usr/share/logstash/vendor/jruby/bin gem install bundle
cd /usr/share/logstash-input-rss2
PATH=${PATH}:/usr/share/logstash/vendor/jruby/bin bundle install

cd /usr/share/logstash
echo 'gem "logstash-input-rss2", :path => "/usr/share/logstash-input-rss2"' >> Gemfile
logstash-plugin install --no-verify
