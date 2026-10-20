#!/bin/sh
set -e

# Topologie :
#   h1 --- r1 --- r2 --- h2
#
#   h1 : 10.40.1.10/24, GW 10.40.1.1
#   r1 : 10.40.1.1/24 et 10.40.2.1/24, GW 10.40.2.2
#   r2 : 10.40.2.2/24 et 10.40.3.1/24, pas de route par defaut !
#   h2 : 10.40.3.10/24, GW 10.40.3.1
#
# Le ping h1 -> h2 part bien, mais la reponse de h2 ne trouve pas le reseau
# 10.40.1.0/24 sur r2. C'est la panne a diagnostiquer.

ip netns add h1
ip netns add r1
ip netns add r2
ip netns add h2

ip link add veth-h1 type veth peer name veth-r1a
ip link add veth-r1b type veth peer name veth-r2a
ip link add veth-r2b type veth peer name veth-h2
ip link set veth-h1 netns h1
ip link set veth-r1a netns r1
ip link set veth-r1b netns r1
ip link set veth-r2a netns r2
ip link set veth-r2b netns r2
ip link set veth-h2 netns h2

for ns in h1 r1 r2 h2; do
    ip netns exec "$ns" ip link set lo up
done

ip netns exec h1 ip link set veth-h1 up
ip netns exec r1 ip link set veth-r1a up
ip netns exec r1 ip link set veth-r1b up
ip netns exec r2 ip link set veth-r2a up
ip netns exec r2 ip link set veth-r2b up
ip netns exec h2 ip link set veth-h2 up

ip netns exec h1 ip addr add 10.40.1.10/24 dev veth-h1
ip netns exec r1 ip addr add 10.40.1.1/24 dev veth-r1a
ip netns exec r1 ip addr add 10.40.2.1/24 dev veth-r1b
ip netns exec r2 ip addr add 10.40.2.2/24 dev veth-r2a
ip netns exec r2 ip addr add 10.40.3.1/24 dev veth-r2b
ip netns exec h2 ip addr add 10.40.3.10/24 dev veth-h2

ip netns exec h1 ip route add default via 10.40.1.1
ip netns exec r1 ip route add default via 10.40.2.2
ip netns exec h2 ip route add default via 10.40.3.1

ip netns exec r1 sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
ip netns exec r2 sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

echo "Topologie prete. Les deux routeurs forwardent, mais r2 n'a pas de route"
echo "pour joindre 10.40.1.0/24. Le ping h1 -> h2 doit echouer."
