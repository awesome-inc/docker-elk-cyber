#!/bin/bash

set -e

if [[ ${http_proxy:+1} ]]; then 
  echo
  echo "Configure proxy '${http_proxy}' ..."
  proxyHost=${http_proxy//"http://"}
  proxyPort=${proxyHost##*:}
  proxyHost=${proxyHost//:*}
  proxyPort=${proxyPort//"/"}
  nonProxyHosts=${no_proxy//,/|}
  # note: assuming same for http/s
  # NOTE:neo4j does not consider JAVA_OPTS but we can use 'dbms_jvm_additional', cf.
  # https://github.com/neo4j-contrib/neo4j-apoc-procedures/issues/207#issuecomment-260083568
  export dbms_jvm_additional="-Dhttp.proxyHost=${proxyHost} -Dhttp.proxyPort=${proxyPort} -Dhttps.proxyHost=${proxyHost} -Dhttps.proxyPort=${proxyPort} -Dhttp.nonProxyHosts=${nonProxyHosts} -Dhttps.nonProxyHosts=${nonProxyHosts}"
  echo "dbms_jvm_additional = ${dbms_jvm_additional}"
fi 
