#!/bin/bash
set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: stop_net_console.sh <stack name> <partition name>"
    ech
    echo " e.g. ./stop_net_console.sh dev08cell001 titusagent-dev08cell001-m4.16xlarge.001-v003"
    echo
    echo "The monitoring host will have console logs in the home directory."
    echo "WARNING: Assumes us-east-1"
    exit 1
fi

stack=$1
partition=$2

echo "Stack: " $stack
echo "Partition: " $partition

echo "Fetching hosts"
http --cert=$HOME/.metatron/user.crt \
     --cert-key=$HOME/.metatron/user.key \
     --verify=$HOME/.metatron/metatronClient.trust.pem \
     --verify=no \
     https://titusapi.$stack.us-east-1.dyntest.netflix.net:7004/api/v3/agent/instances | \
     jq -r ".agentInstances[] | select(.instanceGroupId == \"$partition\") | .ipAddress" > hosts
cat hosts

target_dir=/sys/kernel/config/netconsole/t0
while read ip; do
    echo "*** STOP FORWARDING KERNEL LOGS ON: $ip ***"
    ssh -n -t root@$ip "echo 0 > $target_dir/enabled"
done <hosts


