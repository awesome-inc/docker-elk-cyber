#!/bin/bash

set -e

configureProxy() 
{
  echo
  echo "Configure proxy '${http_proxy}' ..."
  proxyHost=${http_proxy//"http://"} 
  proxyPort=${proxyHost##*:} 
  proxyHost=${proxyHost//:*} 
  proxyPort=${proxyPort//"/"}
  # note: assuming same for http/s
  export LS_JAVA_OPTS="-Dhttp.proxyHost=${proxyHost} -Dhttp.proxyPort=${proxyPort} -Dhttps.proxyHost=${proxyHost} -Dhttps.proxyPort=${proxyPort} -Dhttp.nonProxyHosts=$no_proxy -Dhttps.nonProxyHosts=$no_proxy"

  if [ -e "/root/.m2/settings.xml" ]; then return 0; fi
  mkdir -p /root/.m2/ 
  cat >/root/.m2/settings.xml <<EOF
<settings>
  <proxies>
   <proxy>
      <id>example-proxy</id>
      <active>true</active>
      <protocol>http</protocol>
      <host>${proxyHost}</host>
      <port>${proxyPort}</port>
    </proxy>
  </proxies>
</settings>
EOF
}

if [[ ${http_proxy:+1} ]]; then configureProxy; fi
