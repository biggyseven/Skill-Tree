#!/bin/sh
set -e

# Topologie :
#   srv (10.20.0.1/24, dnsmasq) <==== veth ====> cli (aucune adresse)
#
# Le serveur fournit un bail DHCP et le meme equipement fait office de DNS
# pour intranet.lab. Le client est volontairement laisse sans configuration.

ip netns add srv
ip netns add cli

ip link add veth-srv type veth peer name veth-cli
ip link set veth-srv netns srv
ip link set veth-cli netns cli

for ns in srv cli; do
    ip netns exec "$ns" ip link set lo up
done

ip netns exec srv ip link set veth-srv up
ip netns exec cli ip link set veth-cli up
ip netns exec srv ip addr add 10.20.0.1/24 dev veth-srv

# Le script udhcpc par defaut remplace /etc/resolv.conf. Dans Docker, ce fichier
# est un point de montage : on redirige donc l'ecriture vers le resolv.conf du
# namespace client, qui sera monte automatiquement par ip netns exec.
mkdir -p /etc/netns/cli
cat > /etc/udhcpc/udhcpc.conf <<'EOF'
RESOLV_CONF="/etc/netns/cli/resolv.conf"
EOF

cat > /tmp/dnsmasq-dhcp.conf <<'EOF'
interface=veth-srv
bind-interfaces
dhcp-range=10.20.0.100,10.20.0.150,255.255.255.0,12h
dhcp-option=3,10.20.0.1
dhcp-option=6,10.20.0.1
address=/intranet.lab/10.20.0.1
no-resolv
no-hosts
log-dhcp
EOF

ip netns exec srv dnsmasq --conf-file=/tmp/dnsmasq-dhcp.conf
sleep 1

if ! ip netns exec srv sh -c "ip -4 addr show dev veth-srv | grep -q '10.20.0.1/24'"; then
    echo "ERREUR : le serveur n'a pas l'adresse 10.20.0.1/24"
    exit 1
fi

echo "Serveur DHCP/DNS pret : 10.20.0.1 (plage 10.20.0.100-150)."
echo "Le client cli est sans adresse. A toi de demander un bail."
