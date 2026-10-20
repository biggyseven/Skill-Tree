#!/bin/sh
set -e

# Topologie :
#   h1 --- r1 --- h2
#
# Le lien r1-h2 est volontairement limite a un MTU de 1400. Les interfaces
# h1 et h2 sont en 1500 : les petits paquets passent, les gros paquets avec
# DF sont rejetes par le routeur.

ip netns add h1
ip netns add r1
ip netns add h2

ip link add veth-h1 type veth peer name veth-r1a
ip link add veth-r1b type veth peer name veth-h2
ip link set veth-h1 netns h1
ip link set veth-r1a netns r1
ip link set veth-r1b netns r1
ip link set veth-h2 netns h2

for ns in h1 r1 h2; do
    ip netns exec "$ns" ip link set lo up
done

ip netns exec h1 ip link set veth-h1 up
ip netns exec r1 ip link set veth-r1a up
ip netns exec r1 ip link set veth-r1b up
ip netns exec h2 ip link set veth-h2 up

ip netns exec h1 ip addr add 10.60.1.10/24 dev veth-h1
ip netns exec r1 ip addr add 10.60.1.1/24 dev veth-r1a
ip netns exec r1 ip addr add 10.60.2.1/24 dev veth-r1b
ip netns exec h2 ip addr add 10.60.2.10/24 dev veth-h2

ip netns exec h1 ip route add default via 10.60.1.1
ip netns exec h2 ip route add default via 10.60.2.1
ip netns exec r1 sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

# Le lien de transit est plus petit que les interfaces des hotes.
ip netns exec r1 ip link set veth-r1b mtu 1400

if ! ip netns exec h1 ping -c 1 -W 1 10.60.2.10 >/dev/null 2>&1; then
    echo "ERREUR : le petit ping initial ne fonctionne pas"
    exit 1
fi

if ip netns exec h1 ping -c 1 -W 1 -M do -s 1472 10.60.2.10 >/dev/null 2>&1; then
    echo "ERREUR : le paquet de 1500 octets passe deja ; le MTU du lien n'est pas applique"
    exit 1
fi

echo "Petit ping OK, paquet de 1500 octets avec DF bloque par le MTU 1400 du transit."
echo "A toi de trouver et corriger le MTU de h1."
