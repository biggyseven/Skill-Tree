#!/bin/sh
set -e

# La negociation LACP peut prendre quelques secondes sur des veths.
sleep 5

failures=0

fail() {
    echo "ECHEC : $1"
    failures=$((failures + 1))
}

ok() {
    echo "OK : $1"
}

bond_value() {
    ns="$1"
    key="$2"
    ip netns exec "$ns" sh -c \
        "cat /proc/net/bonding/bond0 2>/dev/null | awk -F': ' '/^$key/ {print \$2; exit}'" \
        2>/dev/null || true
}

for ns in ns1 ns2; do
    if ! ip netns exec "$ns" ip link show bond0 >/dev/null 2>&1; then
        fail "bond0 absent dans $ns"
        continue
    fi
    ok "bond0 present dans $ns"

    mode=$(bond_value "$ns" "Bonding Mode")
    case "$mode" in
        *802.3ad*) ok "$ns : mode $mode" ;;
        *) fail "$ns : mode attendu 802.3ad, obtenu '$mode'" ;;
    esac

    status=$(bond_value "$ns" "MII Status")
    if [ "$status" = "up" ]; then
        ok "$ns : bond0 est up"
    else
        fail "$ns : bond0 MII Status = '$status'"
    fi
done

for iface in veth1a veth2a; do
    if ip netns exec ns1 sh -c "cat /proc/net/bonding/bond0 2>/dev/null" \
        | grep -q "Slave Interface: $iface"; then
        ok "ns1 : $iface est membre du bond"
    else
        fail "ns1 : $iface n'est pas membre du bond"
    fi
done

for iface in veth1b veth2b; do
    if ip netns exec ns2 sh -c "cat /proc/net/bonding/bond0 2>/dev/null" \
        | grep -q "Slave Interface: $iface"; then
        ok "ns2 : $iface est membre du bond"
    else
        fail "ns2 : $iface n'est pas membre du bond"
    fi
done

if ip netns exec ns1 ip -4 addr show dev bond0 2>/dev/null | grep -q "10.10.0.1/24"; then
    ok "ns1 : adresse 10.10.0.1/24 presente"
else
    fail "ns1 : adresse 10.10.0.1/24 absente"
fi

if ip netns exec ns2 ip -4 addr show dev bond0 2>/dev/null | grep -q "10.10.0.2/24"; then
    ok "ns2 : adresse 10.10.0.2/24 presente"
else
    fail "ns2 : adresse 10.10.0.2/24 absente"
fi

if ip netns exec ns1 ip route get 10.10.0.2 2>/dev/null | grep -q "dev bond0"; then
    ok "ns1 : la route vers ns2 passe par bond0"
else
    fail "ns1 : la route vers ns2 ne passe pas par bond0"
fi

if ip netns exec ns1 ping -c 3 -W 2 10.10.0.2 >/dev/null 2>&1; then
    ok "ns1 -> ns2 : ping OK"
else
    fail "ns1 -> ns2 : ping ECHEC"
fi

if ip netns exec ns2 ping -c 3 -W 2 10.10.0.1 >/dev/null 2>&1; then
    ok "ns2 -> ns1 : ping OK"
else
    fail "ns2 -> ns1 : ping ECHEC"
fi

rx=$(ip netns exec ns1 cat /sys/class/net/bond0/statistics/rx_bytes 2>/dev/null || echo 0)
tx=$(ip netns exec ns1 cat /sys/class/net/bond0/statistics/tx_bytes 2>/dev/null || echo 0)
if [ "${rx:-0}" -gt 0 ] && [ "${tx:-0}" -gt 0 ]; then
    ok "ns1 : compteurs du bond actifs (rx=$rx, tx=$tx)"
else
    fail "ns1 : aucun trafic observé sur bond0 (rx=$rx, tx=$tx)"
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    for ns in ns1 ns2; do
        echo "[$ns] liens"
        ip netns exec "$ns" ip -br link 2>/dev/null || true
        echo "[$ns] adresses"
        ip netns exec "$ns" ip -4 addr 2>/dev/null || true
        echo "[$ns] routes"
        ip netns exec "$ns" ip route 2>/dev/null || true
        echo "[$ns] bonding"
        ip netns exec "$ns" cat /proc/net/bonding/bond0 2>/dev/null || true
    done
    exit 1
fi

echo "Lab HA valide : bond LACP operationnel et trafic bidirectionnel via bond0."
exit 0
