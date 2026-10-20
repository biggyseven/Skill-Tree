#!/bin/sh
set -e

# Topologie :
#   dns (10.80.0.53/24, aucun service) <==== veth ====> client (10.80.0.10/24)
#
# Le serveur est pret mais dnsmasq n'est pas demarre. A toi de creer la zone
# locale avec un A et un CNAME, puis de lancer le service.

ip netns add dns
ip netns add client

ip link add veth-dns type veth peer name veth-client
ip link set veth-dns netns dns
ip link set veth-client netns client

for ns in dns client; do
    ip netns exec "$ns" ip link set lo up
done

ip netns exec dns ip link set veth-dns up
ip netns exec client ip link set veth-client up
ip netns exec dns ip addr add 10.80.0.53/24 dev veth-dns
ip netns exec client ip addr add 10.80.0.10/24 dev veth-client

mkdir -p /etc/netns/client
printf 'nameserver 10.80.0.53\n' > /etc/netns/client/resolv.conf

if ! ip netns exec client ping -c 1 -W 1 10.80.0.53 >/dev/null 2>&1; then
    echo "ERREUR : le client ne joint pas le serveur DNS 10.80.0.53"
    exit 1
fi

echo "Serveur DNS 10.80.0.53 pret, mais aucun service DNS n'est lance."
echo "Objectif : zone locale avec A app.lab -> 10.80.0.10 et CNAME www.app.lab."
