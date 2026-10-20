#!/bin/sh

failures=0

fail() {
    echo "ECHEC : $1"
    failures=$((failures + 1))
}

ok() {
    echo "OK : $1"
}

a_record=$(ip netns exec client dig +short A app.lab @10.80.0.53 2>/dev/null | tail -n 1)
if [ "$a_record" = "10.80.0.10" ]; then
    ok "app.lab resout en 10.80.0.10"
else
    fail "app.lab resout en '${a_record:-aucune adresse}' au lieu de 10.80.0.10"
fi

cname_record=$(ip netns exec client dig +short CNAME www.app.lab @10.80.0.53 2>/dev/null | tail -n 1)
case "$cname_record" in
    app.lab|app.lab.)
        ok "www.app.lab possede le CNAME app.lab"
        ;;
    *)
        fail "CNAME de www.app.lab absent ou incorrect ('${cname_record:-aucune valeur}')"
        ;;
esac

www_record=$(ip netns exec client dig +short A www.app.lab @10.80.0.53 2>/dev/null | tail -n 1)
if [ "$www_record" = "10.80.0.10" ]; then
    ok "www.app.lab resout aussi en 10.80.0.10"
else
    fail "www.app.lab resout en '${www_record:-aucune adresse}' au lieu de 10.80.0.10"
fi

if ip netns exec client dig +short A app.lab @10.80.0.53 >/dev/null 2>&1; then
    ok "le serveur DNS repond sur 10.80.0.53"
else
    fail "aucun serveur DNS ne repond sur 10.80.0.53"
fi

if [ "$failures" -ne 0 ]; then
    echo "--- diagnostic ---"
    echo "configuration du lab"
    cat /tmp/dns-adv.conf 2>/dev/null || true
    echo "processus dnsmasq"
    ip netns exec dns ps 2>/dev/null | grep dnsmasq || true
    echo "test direct A"
    ip netns exec client dig app.lab @10.80.0.53 2>/dev/null || true
    echo "test direct CNAME"
    ip netns exec client dig CNAME www.app.lab @10.80.0.53 2>/dev/null || true
    exit 1
fi

echo "Lab DNS avance valide : zone locale, A et CNAME operationnels."
exit 0
