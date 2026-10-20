#!/bin/sh

failures=0

fail() {
    echo "ECHEC : $1"
    failures=$((failures + 1))
}

ok() {
    echo "OK : $1"
}

ip_addr=$(ip netns exec cli ip -4 -o addr show dev veth-cli 2>/dev/null \
    | awk '{print $4}' | cut -d/ -f1)

if [ -z "$ip_addr" ]; then
    fail "le client cli n'a aucune adresse IPv4 sur veth-cli"
else
    case "$ip_addr" in
        10.20.0.*)
            last=${ip_addr##*.}
            if [ "$last" -ge 100 ] && [ "$last" -le 150 ]; then
                ok "bail DHCP dans la plage attendue : $ip_addr/24"
            else
                fail "adresse $ip_addr hors de la plage 10.20.0.100-150"
            fi
            ;;
        *)
            fail "adresse $ip_addr hors du reseau 10.20.0.0/24"
            ;;
    esac
fi

if ip netns exec cli ip route show default 2>/dev/null | grep -q 'via 10.20.0.1'; then
    ok "route par defaut via 10.20.0.1 installee par DHCP"
else
    fail "route par defaut via 10.20.0.1 absente"
fi

if ip netns exec cli sh -c "cat /etc/resolv.conf 2>/dev/null" \
    | grep -q 'nameserver 10.20.0.1'; then
    ok "serveur DNS 10.20.0.1 present dans /etc/resolv.conf"
else
    fail "le client n'utilise pas 10.20.0.1 comme serveur DNS"
fi

if [ -z "$ip_addr" ]; then
    fail "resolution de intranet.lab impossible sans adresse client"
else
    resolved=$(ip netns exec cli dig +short A intranet.lab @10.20.0.1 2>/dev/null | tail -n 1)
    if [ "$resolved" = "10.20.0.1" ]; then
        ok "intranet.lab resolu en 10.20.0.1"
    else
        fail "intranet.lab resolu en '${resolved:-aucune adresse}' au lieu de 10.20.0.1"
    fi
fi

if ip netns exec cli ping -c 1 -W 1 10.20.0.1 >/dev/null 2>&1; then
    ok "le client peut joindre le serveur 10.20.0.1"
else
    fail "le client ne peut pas joindre le serveur 10.20.0.1"
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    echo "[cli] adresses"
    ip netns exec cli ip -4 addr 2>/dev/null || true
    echo "[cli] routes"
    ip netns exec cli ip route 2>/dev/null || true
    echo "[cli] resolv.conf"
    ip netns exec cli cat /etc/resolv.conf 2>/dev/null || true
    echo "[srv] baux DHCP"
    ip netns exec srv cat /var/lib/misc/dnsmasq.leases 2>/dev/null || true
    exit 1
fi

echo "Lab DHCP/DNS valide : bail, passerelle, DNS et resolution operationnels."
exit 0
