#!/bin/sh
set -e

# Topologie :
#   dns (10.70.1.53/24, dnsmasq) <==== veth ====> client (10.70.1.10/24)
#
# Le client utilise bien le serveur 10.70.1.53, mais l'enregistrement DNS du
# serveur renvoie volontairement une mauvaise adresse : 10.70.1.99.

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
ip netns exec dns ip addr add 10.70.1.53/24 dev veth-dns
ip netns exec client ip addr add 10.70.1.10/24 dev veth-client

cat > /tmp/dnsmasq-tshoot.conf <<'EOF'
interface=veth-dns
bind-interfaces
listen-address=10.70.1.53
port=53
pid-file=/tmp/dnsmasq-tshoot.pid
no-resolv
no-hosts
address=/intranet.lab/10.70.1.99
EOF

ip netns exec dns dnsmasq --conf-file=/tmp/dnsmasq-tshoot.conf
sleep 1

mkdir -p /etc/netns/client
printf 'nameserver 10.70.1.53\n' > /etc/netns/client/resolv.conf

if ! ip netns exec client ping -c 1 -W 1 10.70.1.53 >/dev/null 2>&1; then
    echo "ERREUR : le client ne joint pas le serveur DNS 10.70.1.53"
    exit 1
fi

if ! ip netns exec client dig +short A intranet.lab @10.70.1.53 2>/dev/null \
    | grep -qx '10.70.1.99'; then
    echo "ERREUR : le mauvais enregistrement DNS n'est pas actif"
    exit 1
fi

echo "Le serveur DNS 10.70.1.53 repond, mais intranet.lab pointe vers 10.70.1.99 (mauvaise IP)."
echo "Le client utilise pourtant le bon resolveur. A toi de corriger le serveur."
