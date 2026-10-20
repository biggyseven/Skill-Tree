#!/bin/sh

failures=0

fail() {
    echo "ECHEC : $1"
    failures=$((failures + 1))
}

ok() {
    echo "OK : $1"
}

if ip netns exec h1 ping -c 1 -W 1 10.10.2.10 >/dev/null 2>&1; then
    fail "le ping h1 -> h2 passe encore (ICMP non filtre)"
else
    ok "le ping h1 -> h2 est bloque"
fi

http_output=$(ip netns exec h1 wget -q -T 3 -O - http://10.10.2.10/ 2>/dev/null || true)
if echo "$http_output" | grep -q 'ACL-LAB-OK'; then
    ok "HTTP h1 -> h2 fonctionne toujours"
else
    fail "HTTP h1 -> h2 ne fonctionne plus"
fi

if ip netns exec r1 sh -c "iptables -L FORWARD -n 2>/dev/null" \
    | grep -Eq 'DROP|REJECT'; then
    ok "une regle de filtrage ICMP est presente dans FORWARD"
else
    fail "aucune regle DROP/REJECT visible dans la chaine FORWARD de r1"
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    echo "[r1] filtrage FORWARD"
    ip netns exec r1 iptables -L FORWARD -n -v 2>/dev/null || true
    echo "[h1] route"
    ip netns exec h1 ip route 2>/dev/null || true
    echo "[h2] serveur HTTP"
    ip netns exec h2 ps 2>/dev/null | grep -E 'nc|http-acl' || true
    echo "[h2] log HTTP"
    cat /tmp/http-acl.log 2>/dev/null || true
    exit 1
fi

echo "Lab ACL valide : ICMP bloque, HTTP autorise."
exit 0
