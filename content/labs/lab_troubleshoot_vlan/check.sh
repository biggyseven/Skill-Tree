#!/bin/sh
set -e

failures=0

if ip netns exec ns1 ping -c 2 -W 2 192.168.50.20 >/dev/null 2>&1; then
    echo "ns1 -> ns2 : OK"
else
    echo "ns1 -> ns2 : ECHEC"
    failures=$((failures + 1))
fi

if ip netns exec ns2 ping -c 2 -W 2 192.168.50.10 >/dev/null 2>&1; then
    echo "ns2 -> ns1 : OK"
else
    echo "ns2 -> ns1 : ECHEC"
    failures=$((failures + 1))
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    echo "VLAN du bridge :"
    bridge vlan show 2>/dev/null || true
    echo "Liens du bridge :"
    bridge link show 2>/dev/null || true
    echo "Adresses ns1 :"
    ip netns exec ns1 ip -br addr 2>/dev/null || true
    echo "Adresses ns2 :"
    ip netns exec ns2 ip -br addr 2>/dev/null || true
    exit 1
fi

echo "Lab de depannage valide : le VLAN est corrige et le ping passe."
exit 0
