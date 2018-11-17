#!/bin/bash
set -e

if [ "$#" -ne 3 ]; then
    echo "Usage: start_net_console.sh <stack name> <partition name> <monitor ip>"
    ech
    echo " e.g. ./start_net_console.sh dev08cell001 titusagent-dev08cell001-m4.16xlarge.001-v003 100.122.174.123"
    echo
    echo "The monitoring host will have console logs in the home directory."
    echo "WARNING: Assumes us-east-1"
    exit 1
fi

stack=$1
partition=$2
monitor_ip=$3

echo "Stack: " $stack
echo "Monitor IP: " $monitor_ip

echo "Fetching hosts"
http --cert=$HOME/.metatron/user.crt \
     --cert-key=$HOME/.metatron/user.key \
     --verify=$HOME/.metatron/metatronClient.trust.pem \
     --verify=no \
     https://titusapi.$stack.us-east-1.dyntest.netflix.net:7004/api/v3/agent/instances | \
     jq -r ".agentInstances[] | select(.instanceGroupId == \"$partition\") | .ipAddress" > hosts
cat hosts

echo "Uploading setup scripts"
./upload_scripts.sh hosts

port=6666
while read ip; do
    echo "*** FORWARDING KERNEL LOGS ON: $ip ***"
    log_file_name=${ip//./_}
    log_file_name=/home/nfsuper/$log_file_name.log

    echo "Start listening for logs on $monitor_ip:$port to file $log_file_name"
    ssh -n -t root@$monitor_ip "nc -u -l $port > $log_file_name 2>&1 &"

    echo "Setting up netconsole on: $ip to push logs to $monitor_ip:$port"
    ssh -n -t root@$ip "/home/nfsuper/setup_net_console.sh $monitor_ip $port"

    echo "Incrementing port"
    port=$((port+1))
    echo "port: $port"
done <hosts


