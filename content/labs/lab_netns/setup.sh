#!/bin/sh
set -e

# Topologie : ns-a --veth-a/[veth-ra] ns-router [veth-rb]/veth-b-- ns-b
ip netns add ns-a
ip netns add ns-b
ip netns add ns-router

ip link add veth-a type veth peer name veth-ra
ip link add veth-b type veth peer name veth-rb

ip link set veth-a netns ns-a
ip link set veth-ra netns ns-router
ip link set veth-b netns ns-b
ip link set veth-rb netns ns-router

ip netns exec ns-a ip link set lo up
ip netns exec ns-a ip link set veth-a up

ip netns exec ns-b ip link set lo up
ip netns exec ns-b ip link set veth-b up

ip netns exec ns-router ip link set lo up
ip netns exec ns-router ip link set veth-ra up
ip netns exec ns-router ip link set veth-rb up

# Docker monte parfois /proc/sys en lecture seule : on tente de le remettre
# en écriture avant d'activer le forwarding dans le namespace routeur.
mount -o remount,rw /proc/sys 2>/dev/null || true
ip netns exec ns-router sysctl -w net.ipv4.ip_forward=1 > /dev/null