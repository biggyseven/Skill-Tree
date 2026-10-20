#!/bin/sh

failures=0

fail() {
    echo "ECHEC : $1"
    failures=$((failures + 1))
}

ok() {
    echo "OK : $1"
}

if ip netns exec client ping -c 1 -W 1 10.90.2.10 >/dev/null 2>&1; then
    fail "le nouveau ping client -> server passe encore"
else
    ok "les nouveaux ping entrants sont bloques"
fi

http_output=$(ip netns exec client wget -q -T 3 -O - http://10.90.2.10/ 2>/dev/null || true)
if echo "$http_output" | grep -q 'FW-LAB-OK'; then
    ok "HTTP client -> server fonctionne"
else
    fail "HTTP client -> server ne fonctionne pas"
fi

if ip netns exec fw iptables -L FORWARD -n 2>/dev/null \
    | grep -Eq 'conntrack|ctstate'; then
    ok "une regle conntrack est presente dans FORWARD"
else
    fail "aucune regle conntrack visible dans FORWARD"
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    echo "[fw] politique et regles FORWARD"
    ip netns exec fw iptables -L FORWARD -n -v 2>/dev/null || true
    echo "[client] route"
    ip netns exec client ip route 2>/dev/null || true
    echo "[server] serveur HTTP"
    ip netns exec server ps 2>/dev/null | grep -E 'nc|http-fw' || true
    echo "[server] log HTTP"
    cat /tmp/http-fw.log 2>/dev/null || true
    echo "Indice : autorise ESTABLISHED,RELATED puis NEW TCP/80 avec -m conntrack."
    exit 1
fi

echo "Lab firewall valide : firewall stateful, HTTP autorise, ping bloque."
exit 0
