#!/bin/bash

set -e

# check proxy
if ! [[ -v http_proxy ]]; then exit 0; fi

echo
echo "Configure proxy '${http_proxy}' ..."
proxyHost=${http_proxy//"http://"} 
proxyPort=${proxyHost##*:} 
proxyHost=${proxyHost//:*} 
proxyPort=${proxyPort//"/"}
mkdir /root/.m2/ 
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
