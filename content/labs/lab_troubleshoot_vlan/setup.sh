#!/bin/sh
set -e

# Topologie :
#   ns1 --veth1-a-- [veth1-b] br-trouble [veth2-b] --veth2-a-- ns2
# Le bridge applique un filtrage VLAN 802.1Q.
ip netns add ns1
ip netns add ns2

ip link add veth1-a type veth peer name veth1-b
ip link add veth2-a type veth peer name veth2-b

ip link set veth1-a netns ns1
ip link set veth2-a netns ns2

ip link add br-trouble type bridge
ip link set br-trouble type bridge vlan_filtering 1
ip link set veth1-b master br-trouble
ip link set veth2-b master br-trouble

ip link set br-trouble up
ip link set veth1-b up
ip link set veth2-b up

ip netns exec ns1 ip addr add 192.168.50.10/24 dev veth1-a
ip netns exec ns2 ip addr add 192.168.50.20/24 dev veth2-a
ip netns exec ns1 ip link set veth1-a up
ip netns exec ns2 ip link set veth2-a up
ip netns exec ns1 ip link set lo up
ip netns exec ns2 ip link set lo up

# Port de ns1 correctement place dans le VLAN 50.
bridge vlan add vid 50 dev veth1-b pvid untagged
bridge vlan add vid 50 dev br-trouble self

# ERREUR VOLONTAIRE : le port de ns2 est dans le VLAN 60.
# Les adresses IP sont correctes ; c'est le classement L2 qui est faux.
bridge vlan add vid 60 dev veth2-b pvid untagged
