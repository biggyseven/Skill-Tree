#!/bin/sh
set -e

# Topologie :
#   h1 10.10.1.10/24 --- r1 --- 10.10.2.10/24 h2
#                        |
#                 10.10.1.1 / 10.10.2.1
#
# Le routage fonctionne deja. Aucun filtrage n'est en place : c'est le travail
# de l'exercice. h2 heberge un petit serveur HTTP (BusyBox nc).

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

ip netns exec h1 ip addr add 10.10.1.10/24 dev veth-h1
ip netns exec r1 ip addr add 10.10.1.1/24 dev veth-r1a
ip netns exec r1 ip addr add 10.10.2.1/24 dev veth-r1b
ip netns exec h2 ip addr add 10.10.2.10/24 dev veth-h2

ip netns exec h1 ip route add default via 10.10.1.1
ip netns exec h2 ip route add default via 10.10.2.1
ip netns exec r1 sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

cat > /tmp/http-acl.sh <<'EOF'
#!/bin/sh
while true; do
    printf 'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 11\r\nConnection: close\r\n\r\nACL-LAB-OK\n' \
        | nc -l -p 80 -w 2 >/dev/null 2>&1
done
EOF
chmod +x /tmp/http-acl.sh

ip netns exec h2 nohup /tmp/http-acl.sh >/tmp/http-acl.log 2>&1 &
sleep 1

if ! ip netns exec h1 ping -c 1 -W 1 10.10.2.10 >/dev/null 2>&1; then
    echo "ERREUR : le routage initial h1 -> h2 ne fonctionne pas"
    exit 1
fi

http_ok=0
for _ in 1 2 3 4 5; do
    if ip netns exec h1 wget -q -T 2 -O - http://10.10.2.10/ 2>/dev/null \
        | grep -q 'ACL-LAB-OK'; then
        http_ok=1
        break
    fi
    sleep 1
done
if [ "$http_ok" -ne 1 ]; then
    echo "ERREUR : le serveur HTTP de h2 ne repond pas"
    exit 1
fi

echo "Routage et HTTP operationnels avant filtrage."
echo "Objectif : bloquer ICMP de h1 vers h2 sans couper HTTP."
