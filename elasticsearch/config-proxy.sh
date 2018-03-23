#!/bin/bash

set -e

if [[ ${http_proxy:+1} ]]; then 
	echo
	echo "Configure proxy '${http_proxy}' ..."
	proxyHost=${http_proxy//"http://"} 
	proxyPort=${proxyHost##*:} 
	proxyHost=${proxyHost//:*} 
	proxyPort=${proxyPort//"/"} 
	# note: assuming same for http/s
	export ES_JAVA_OPTS="-DproxyHost=${proxyHost} -DproxyPort=${proxyPort} ${ES_JAVA_OPTS}"   
fi 
