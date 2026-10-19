#!/bin/sh
set -e

# Deux namespaces, chacun avec un veth dont le pair reste dans le namespace
# principal où se trouve le bridge br-lab, volontairement laissé vide.
ip netns add ns1
ip netns add ns2

ip link add veth1-a type veth peer name veth1-b
ip link set veth1-a netns ns1

ip link add veth2-a type veth peer name veth2-b
ip link set veth2-a netns ns2

ip link add br-lab type bridge
ip link set br-lab up

ip netns exec ns1 ip addr add 192.168.100.1/24 dev veth1-a
ip netns exec ns2 ip addr add 192.168.100.2/24 dev veth2-a

ip netns exec ns1 ip link set veth1-a up
ip netns exec ns2 ip link set veth2-a up
ip netns exec ns1 ip link set lo up
ip netns exec ns2 ip link set lo up

ip link set veth1-b down
ip link set veth2-b down