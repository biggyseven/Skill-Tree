#!/bin/sh
set -e

# Topologie :
#   ns1 veth1a ==================== veth1b ns2
#   ns1 veth2a ==================== veth2b ns2
#
# Les deux liens doivent etre agreges dans un bond LACP sur chaque rive.
# Aucun bond n'est cree ici : c'est le travail de l'exercice.

modprobe bonding 2>/dev/null || true

ip netns add ns1
ip netns add ns2

ip link add veth1a type veth peer name veth1b
ip link add veth2a type veth peer name veth2b

ip link set veth1a netns ns1
ip link set veth2a netns ns1
ip link set veth1b netns ns2
ip link set veth2b netns ns2

for ns in ns1 ns2; do
    ip netns exec "$ns" ip link set lo up
done

for iface in veth1a veth2a; do
    ip netns exec ns1 ip link set "$iface" up
done
for iface in veth1b veth2b; do
    ip netns exec ns2 ip link set "$iface" up
done

echo "Liens prets : ns1(veth1a,veth2a) <-> ns2(veth1b,veth2b)"
echo "A toi de creer bond0 en mode 802.3ad dans les deux namespaces."
