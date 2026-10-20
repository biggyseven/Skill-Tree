#!/bin/sh

failures=0

fail() {
    echo "ECHEC : $1"
    failures=$((failures + 1))
}

ok() {
    echo "OK : $1"
}

if grep -q '^nameserver 10.70.1.53' /etc/netns/client/resolv.conf 2>/dev/null; then
    ok "le client utilise maintenant 10.70.1.53 comme resolveur"
else
    fail "le resolveur du client n'est pas 10.70.1.53"
fi

if ip netns exec client ping -c 1 -W 1 10.70.1.53 >/dev/null 2>&1; then
    ok "le client joint le serveur DNS"
else
    fail "le client ne joint pas le serveur DNS"
fi

resolved=$(timeout 5 ip netns exec client dig +short A intranet.lab 2>/dev/null | tail -n 1)
if [ "$resolved" = "10.70.1.53" ]; then
    ok "intranet.lab se resout vers 10.70.1.53"
else
    fail "intranet.lab se resout vers '${resolved:-aucune adresse}' au lieu de 10.70.1.53"
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    echo "resolv.conf du namespace client"
    cat /etc/netns/client/resolv.conf 2>/dev/null || true
    echo "configuration dnsmasq"
    cat /tmp/dnsmasq-tshoot.conf 2>/dev/null || true
    echo "test direct du serveur DNS"
    ip netns exec client nslookup -type=A intranet.lab 10.70.1.53 2>/dev/null || true
    echo "processus dnsmasq"
    ip netns exec dns ps 2>/dev/null | grep dnsmasq || true
    echo "Indice : corriger address=/intranet.lab/10.70.1.99 en .53 puis relancer dnsmasq."
    exit 1
fi

echo "Lab DNS valide : le client resout intranet.lab via 10.70.1.53."
exit 0
