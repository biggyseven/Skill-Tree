#!/bin/sh
set -e

# Petite marge pour un demon de routage qui demarrerait en arriere-plan.
sleep 2

failures=0

if ip netns exec h1 ping -c 2 -W 2 192.168.20.20 >/dev/null 2>&1; then
    echo "h1 -> h2 : OK"
else
    echo "h1 -> h2 : ECHEC"
    failures=$((failures + 1))
fi

if ip netns exec h2 ping -c 2 -W 2 192.168.10.10 >/dev/null 2>&1; then
    echo "h2 -> h1 : OK"
else
    echo "h2 -> h1 : ECHEC"
    failures=$((failures + 1))
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    for ns in h1 r1 r2 h2; do
        echo "[$ns] routes"
        ip netns exec "$ns" ip route 2>/dev/null || true
        echo "[$ns] forwarding"
        ip netns exec "$ns" sysctl -n net.ipv4.ip_forward 2>/dev/null || true
    done
    exit 1
fi

echo "Lab OSPF valide : connectivite bidirectionnelle entre les deux LAN."
exit 0
