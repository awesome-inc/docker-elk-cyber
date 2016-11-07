#!/bin/bash

set -e

# check proxy
if [[ -v http_proxy ]]; then
	echo
	echo "Configure proxy '${http_proxy}' ..."
	proxyHost=${http_proxy//"http://"} 
	proxyPort=${proxyHost##*:} 
	proxyHost=${proxyHost//:*} 
	proxyPort=${proxyPort//"/"} 
	# note: assuming same for http/s
	export LS_JAVA_OPTS="-Dhttp.proxyHost=${proxyHost} -Dhttp.proxyPort=${proxyPort} -Dhttps.proxyHost=${proxyHost} -Dhttps.proxyPort=${proxyPort} -Dhttp.nonProxyHosts=$no_proxy -Dhttps.nonProxyHosts=$no_proxy"
fi 

# Add logstash as command if needed
if [ "${1:0:1}" = '-' ]; then
	set -- logstash "$@"
fi

# Run as user "logstash" if the command is "logstash"
if [ "$1" = 'logstash' ]; then
	set -- gosu logstash "$@"
fi

exec "$@"
