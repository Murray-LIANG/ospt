#!/usr/bin/env bash

ospt_cmd='ospt --os_auth_ip 172.16.1.5 --os_auth_version v3 --os_project admin --username admin --password welcome'

set -x
$ospt_cmd --log create-volumes.log create-volumes --tag liangr --count 40 \
&& $ospt_cmd --log create-servers.log create-servers --tag liangr --count 40
set +x
