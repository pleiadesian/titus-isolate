#!/bin/bash
set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: upload_scripts.sh <file with a list of ip addresses>"
    exit 1
fi

hosts_file=$1

while read ip; do
    echo "Uploading setup_note_console.sh to: $ip"
    scp setup_net_console.sh root@$ip:/home/nfsuper
done <$hosts_file
