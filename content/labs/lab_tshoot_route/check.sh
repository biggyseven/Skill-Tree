#!/bin/sh

failures=0

fail() {
    echo "ECHEC : $1"
    failures=$((failures + 1))
}

ok() {
    echo "OK : $1"
}

if ip netns exec r2 ip route show default 2>/dev/null \
    | grep -q 'via 10.40.2.1'; then
    ok "r2 possede une route par defaut via 10.40.2.1"
else
    fail "r2 n'a pas de route par defaut via 10.40.2.1"
fi

if ip netns exec h1 ping -c 2 -W 1 10.40.3.10 >/dev/null 2>&1; then
    ok "ping h1 -> h2 operationnel"
else
    fail "ping h1 -> h2 toujours en echec"
fi

if ip netns exec h2 ping -c 2 -W 1 10.40.1.10 >/dev/null 2>&1; then
    ok "ping h2 -> h1 operationnel"
else
    fail "ping h2 -> h1 toujours en echec"
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    for ns in h1 r1 r2 h2; do
        echo "[$ns] adresses"
        ip netns exec "$ns" ip -4 addr 2>/dev/null || true
        echo "[$ns] routes"
        ip netns exec "$ns" ip route 2>/dev/null || true
    done
    echo "[r1] forwarding"
    ip netns exec r1 cat /proc/sys/net/ipv4/ip_forward 2>/dev/null || true
    echo "[r2] forwarding"
    ip netns exec r2 cat /proc/sys/net/ipv4/ip_forward 2>/dev/null || true
    exit 1
fi

echo "Lab routage valide : la route de retour manquante a ete ajoutee."
exit 0
