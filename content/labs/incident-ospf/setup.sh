#!/bin/sh
set -e
ip netns add r1
ip netns add r2
ip link add veth1 type veth peer name veth2
ip link set veth1 netns r1
ip link set veth2 netns r2
ip netns exec r1 ip addr add 10.0.0.1/24 dev veth1
ip netns exec r2 ip addr add 10.0.0.2/24 dev veth2
ip netns exec r1 ip link set veth1 up
ip netns exec r2 ip link set veth2 up
ip netns exec r1 ip link set lo up
ip netns exec r2 ip link set lo up
ip netns exec r1 ip addr add 192.168.2.254/24 dev lo
ip netns exec r1 sysctl -w net.ipv4.ip_forward=1 > /dev/null
ip netns exec r2 ip route add 192.168.2.0/24 via 10.0.0.1
ip netns exec r1 ip route add 10.0.0.0/24 via 10.0.0.99