#!/bin/sh
set -e

# Topologie :
#   client 10.90.1.10/24 --- fw --- 10.90.2.10/24 server
#                        10.90.1.1
#                        10.90.2.1
#
# Le forwarding est actif, mais la politique FORWARD est DROP. Aucune regle
# d'autorisation n'existe : le firewall est volontairement ferme au depart.

ip netns add client
ip netns add fw
ip netns add server

ip link add veth-client type veth peer name veth-fwA
ip link add veth-fwB type veth peer name veth-server
ip link set veth-client netns client
ip link set veth-fwA netns fw
ip link set veth-fwB netns fw
ip link set veth-server netns server

for ns in client fw server; do
    ip netns exec "$ns" ip link set lo up
done

ip netns exec client ip link set veth-client up
ip netns exec fw ip link set veth-fwA up
ip netns exec fw ip link set veth-fwB up
ip netns exec server ip link set veth-server up

ip netns exec client ip addr add 10.90.1.10/24 dev veth-client
ip netns exec fw ip addr add 10.90.1.1/24 dev veth-fwA
ip netns exec fw ip addr add 10.90.2.1/24 dev veth-fwB
ip netns exec server ip addr add 10.90.2.10/24 dev veth-server

ip netns exec client ip route add default via 10.90.1.1
ip netns exec server ip route add default via 10.90.2.1
ip netns exec fw sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

cat > /tmp/http-fw.sh <<'EOF'
#!/bin/sh
while true; do
    printf 'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 10\r\nConnection: close\r\n\r\nFW-LAB-OK\n' \
        | nc -l -p 80 -w 2 >/dev/null 2>&1
done
EOF
chmod +x /tmp/http-fw.sh
ip netns exec server nohup /tmp/http-fw.sh >/tmp/http-fw.log 2>&1 &
sleep 1

http_ok=0
for _ in 1 2 3 4 5; do
    if ip netns exec server wget -q -T 2 -O - http://10.90.2.10/ 2>/dev/null \
        | grep -q 'FW-LAB-OK'; then
        http_ok=1
        break
    fi
    sleep 1
done
if [ "$http_ok" -ne 1 ]; then
    echo "ERREUR : le serveur HTTP local de server ne repond pas"
    exit 1
fi

ip netns exec fw iptables -P FORWARD DROP

echo "Serveur HTTP local pret et politique FORWARD = DROP."
echo "Objectif : firewall stateful avec conntrack, HTTP autorise et ping bloque."
