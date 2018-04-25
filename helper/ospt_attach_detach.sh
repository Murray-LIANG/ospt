#!/usr/bin/env bash

ospt_cmd='ospt --os_auth_ip 172.16.1.5 --os_project admin --username admin --password welcome'

set -x
for num in 10 15 20 25 30 40; do
    for i in 1; do
        $ospt_cmd --log attach-$num-$i.log attach --tag liangr --count $num \
        && $ospt_cmd --log detach-$num-$i.log detach --tag liangr --count $num
    done
done
set +x
