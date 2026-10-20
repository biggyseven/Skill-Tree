# Lab DNS avancé : zone locale, A et CNAME

## Objectif

Le serveur DNS `10.80.0.53` est joignable, mais aucun service DNS n'est encore
lancé. Tu dois créer une petite zone locale avec `dnsmasq` et publier :

- un enregistrement **A** : `app.lab -> 10.80.0.10` ;
- un enregistrement **CNAME** : `www.app.lab -> app.lab`.

```text
+-----------------------------+          +-----------------------------+
| dns                         |          | client                      |
| veth-dns : 10.80.0.53/24    |<========>| veth-client : 10.80.0.10/24 |
| aucun service DNS           |          | resolv.conf -> .53          |
+-----------------------------+          +-----------------------------+

Zone attendue :
  app.lab.       A       10.80.0.10
  www.app.lab.   CNAME   app.lab.
```

## Ce qui est déjà prêt

Le script `setup.sh` crée les namespaces `dns` et `client`, les liens, les
adresses IP et le fichier `resolv.conf` du client. Le serveur n'a **aucun
service DNS actif** : c'est le travail de l'exercice.

## Travail demandé

1. Crée la configuration `dnsmasq` :

```bash
cat > /tmp/dns-adv.conf <<'EOF'
interface=veth-dns
bind-interfaces
listen-address=10.80.0.53
port=53
pid-file=/tmp/dns-adv.pid
no-resolv
no-hosts
host-record=app.lab,10.80.0.10
cname=www.app.lab,app.lab
EOF
```

2. Démarre le serveur dans le namespace `dns` :

```bash
ip netns exec dns dnsmasq --conf-file=/tmp/dns-adv.conf
```

3. Vérifie les enregistrements avec `dig` :

```bash
ip netns exec client dig +short A app.lab @10.80.0.53
ip netns exec client dig +short CNAME www.app.lab @10.80.0.53
ip netns exec client dig +short A www.app.lab @10.80.0.53
```

Résultats attendus :

```text
10.80.0.10
app.lab.
10.80.0.10
```

Tu peux aussi interroger le client sans préciser de serveur, puisque son
`resolv.conf` pointe déjà vers `10.80.0.53` :

```bash
ip netns exec client dig +short A app.lab
```

## Comprendre les enregistrements

| Type | Rôle | Exemple |
|------|------|---------|
| `A` | Nom vers adresse IPv4 | `app.lab -> 10.80.0.10` |
| `AAAA` | Nom vers adresse IPv6 | `app.lab -> 2001:db8::10` |
| `CNAME` | Alias vers un autre nom canonique | `www.app.lab -> app.lab` |
| `MX` | Serveur de messagerie | `mail.app.lab` |
| `TXT` | Texte libre, SPF, DKIM, vérifications | `v=spf1 ...` |
| `PTR` | Résolution inverse | `10.0.80.10.in-addr.arpa -> app.lab` |

Un CNAME ne doit pas cohabiter avec d'autres enregistrements au même nom : il
pointe vers un nom canonique, qui porte l'adresse. C'est pour cela que
`www.app.lab` ne reçoit pas directement un A dans cet exercice.

## Critères de validation

Le script `check.sh` vérifie :

- `app.lab` répond avec `10.80.0.10` ;
- `www.app.lab` possède un CNAME vers `app.lab` ;
- `www.app.lab` résout finalement vers `10.80.0.10` ;
- le serveur DNS répond sur `10.80.0.53`.

## Pistes en cas d'échec

- Vérifie que `dnsmasq` tourne : `ip netns exec dns ps | grep dnsmasq`.
- Vérifie que l'interface `veth-dns` est `UP`.
- Teste directement le serveur avec `@10.80.0.53`.
- Regarde la configuration : `cat /tmp/dns-adv.conf`.
- Si le CNAME n'apparaît pas, vérifie l'orthographe exacte
  `cname=www.app.lab,app.lab`.
- Le nom pleinement qualifié se termine par un point dans les réponses DNS ;
  `app.lab.` et `app.lab` désignent le même nom.

> En production, un CNAME est pratique pour les alias et les migrations, mais il
> faut éviter les chaînes de CNAME trop longues et ne jamais placer un CNAME au
> sommet d'une zone qui doit aussi porter des enregistrements MX ou TXT.
