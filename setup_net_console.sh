#!/bin/bash
set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: setup_net_console.sh <remote ip> <remote port>"
    exit 1
fi

remote_ip=$1
remote_port=$2
echo "Remote IP address:" $remote_ip
echo "Remote port:" $remote_port

local_ip=$(ip route | grep default | awk '{print $9}')
echo "Local IP address:" $local_ip

remote_mac=$(arp -a | grep $(ip route show | grep default | awk '{print $3}') | awk '{print $4}')
echo "Remote mac address:" $remote_mac

echo "Loading module: configfs"
modprobe configfs

echo "Loading module: netconsole"
modprobe netconsole

target_dir=/sys/kernel/config/netconsole/t0

if [ ! -d "$target_dir" ]; then
    echo "Making netconsole target directory:" $target_dir
    mkdir /sys/kernel/config/netconsole/t0
else
    echo "Target directory already exists:" $target_dir
fi

echo "Disabling netconsole target"
echo 0 > $target_dir/enabled

echo "Configuring local_ip:" $local_ip
echo $local_ip > $target_dir/local_ip

echo "Configuring remote_ip:" $remote_ip
echo $remote_ip > $target_dir/remote_ip

echo "Configuring remote_mac:" $remote_mac
echo $remote_mac > $target_dir/remote_mac

echo "Enabling netconsole target"
echo 1 > $target_dir/enabled

