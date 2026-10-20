#!/bin/sh
set -e

# Topologie :
#   h1 -- r1 ===== r2 -- h2
# r1 et r2 sont les deux routeurs. h1 et h2 representent les reseaux distants.
ip netns add h1
ip netns add r1
ip netns add r2
ip netns add h2

ip link add h1-eth0 type veth peer name r1-lan
ip link add r1-wan type veth peer name r2-wan
ip link add r2-lan type veth peer name h2-eth0

ip link set h1-eth0 netns h1
ip link set r1-lan netns r1
ip link set r1-wan netns r1
ip link set r2-wan netns r2
ip link set r2-lan netns r2
ip link set h2-eth0 netns h2

# LAN du site 1
ip netns exec h1 ip addr add 192.168.10.10/24 dev h1-eth0
ip netns exec r1 ip addr add 192.168.10.1/24 dev r1-lan

# Lien entre les deux routeurs
ip netns exec r1 ip addr add 10.255.0.1/30 dev r1-wan
ip netns exec r2 ip addr add 10.255.0.2/30 dev r2-wan

# LAN du site 2
ip netns exec r2 ip addr add 192.168.20.1/24 dev r2-lan
ip netns exec h2 ip addr add 192.168.20.20/24 dev h2-eth0

for ns in h1 r1 r2 h2; do
    ip netns exec "$ns" ip link set lo up
done

ip netns exec h1 ip link set h1-eth0 up
ip netns exec r1 ip link set r1-lan up
ip netns exec r1 ip link set r1-wan up
ip netns exec r2 ip link set r2-wan up
ip netns exec r2 ip link set r2-lan up
ip netns exec h2 ip link set h2-eth0 up

# Les hotes connaissent leur passerelle ; les routeurs n'ont pas encore
# de route vers le LAN distant : c'est le travail de l'exercice.
ip netns exec h1 ip route add default via 192.168.10.1
ip netns exec h2 ip route add default via 192.168.20.1

# Docker monte parfois /proc/sys en lecture seule. On retablit l'ecriture
# puis on active le forwarding dans les deux namespaces routeurs.
mount -o remount,rw /proc/sys 2>/dev/null || true
ip netns exec r1 sysctl -w net.ipv4.ip_forward=1 >/dev/null
ip netns exec r2 sysctl -w net.ipv4.ip_forward=1 >/dev/null
