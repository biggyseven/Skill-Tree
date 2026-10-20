#!/bin/sh

failures=0

fail() {
    echo "ECHEC : $1"
    failures=$((failures + 1))
}

ok() {
    echo "OK : $1"
}

mtu=$(ip netns exec h1 cat /sys/class/net/veth-h1/mtu 2>/dev/null || echo 0)
if [ "$mtu" -le 1400 ] 2>/dev/null; then
    ok "le MTU de h1/veth-h1 est passe a $mtu"
else
    fail "le MTU de h1/veth-h1 est encore $mtu (attendu <= 1400)"
fi

if ip netns exec h1 ping -c 1 -W 1 10.60.2.10 >/dev/null 2>&1; then
    ok "le petit ping h1 -> h2 fonctionne"
else
    fail "le petit ping h1 -> h2 ne fonctionne plus"
fi

if ip netns exec h1 ping -c 1 -W 2 -M do -s 1372 10.60.2.10 >/dev/null 2>&1; then
    ok "le gros paquet avec DF passe (1400 octets IP)"
else
    fail "le gros paquet avec DF echoue encore"
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    echo "[h1] interface et MTU"
    ip netns exec h1 ip link show veth-h1 2>/dev/null || true
    echo "[r1] interfaces et MTU"
    ip netns exec r1 ip link show 2>/dev/null || true
    echo "[h2] interface et MTU"
    ip netns exec h2 ip link show veth-h2 2>/dev/null || true
    echo "[h1] routes"
    ip netns exec h1 ip route 2>/dev/null || true
    echo "[r1] forwarding"
    ip netns exec r1 cat /proc/sys/net/ipv4/ip_forward 2>/dev/null || true
    echo "Indice : ip netns exec h1 ip link set veth-h1 mtu 1400"
    exit 1
fi

echo "Lab MTU valide : le chemin accepte les paquets de 1400 octets avec DF."
exit 0
