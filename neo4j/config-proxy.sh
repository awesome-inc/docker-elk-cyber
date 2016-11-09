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
	# NOTE:neo4j does not consider JAVA_OPTS but we can inject JAVA_CMD, cf.
	# https://github.com/neo4j/neo4j/blob/124d6ac1d3de96738aa62afb68832781d2b52d8a/packaging/standalone/src/main/distribution/shell-scripts/bin/neo4j#L113
	# https://github.com/neo4j/neo4j/blob/124d6ac1d3de96738aa62afb68832781d2b52d8a/packaging/standalone/src/main/distribution/shell-scripts/bin/neo4j-shared.sh#L90
	export JAVA_OPTS="-Dhttp.proxyHost=${proxyHost} -Dhttp.proxyPort=${proxyPort} -Dhttps.proxyHost=${proxyHost} -Dhttps.proxyPort=${proxyPort} -Dhttp.nonProxyHosts=$no_proxy -Dhttps.nonProxyHosts=$no_proxy"
fi 
