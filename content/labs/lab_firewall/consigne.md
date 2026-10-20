# Lab firewall stateful : conntrack, HTTP et ICMP

## Objectif

Le routeur `fw` sépare deux réseaux. Son forwarding est actif, mais sa politique
`FORWARD` est **DROP** : aucun trafic ne traverse pour l'instant. Tu dois créer
un firewall **stateful** qui :

- autorise le retour des connexions établies avec `conntrack` ;
- autorise les nouvelles connexions HTTP vers le serveur ;
- laisse les nouveaux ping entrants bloqués.

```text
10.90.1.0/24                         10.90.2.0/24
+--------+            +--------+            +--------+
| client |            |   fw   |            | server |
| .10    |<---------->| .1  .1 |<---------->| .10    |
+--------+  veth-client+--------+ veth-server+--------+
                       FORWARD DROP
                       HTTP :80
```

| Équipement | Interface | Adresse | Passerelle |
|---|---|---|---|
| `client` | `veth-client` | `10.90.1.10/24` | `10.90.1.1` |
| `fw` | `veth-fwA` | `10.90.1.1/24` | — |
| `fw` | `veth-fwB` | `10.90.2.1/24` | — |
| `server` | `veth-server` | `10.90.2.10/24` | `10.90.2.1` |

## Ce qui est déjà prêt

Le script `setup.sh` crée les trois namespaces, les liens, les adresses, les
routes et active le forwarding. Il démarre aussi un serveur HTTP de test sur
`server` et positionne :

```text
FORWARD policy = DROP
```

Il n'y a volontairement aucune règle d'autorisation.

## Travail demandé

1. Autorise le trafic de retour des connexions déjà établies :

```bash
ip netns exec fw iptables -A FORWARD \
    -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

2. Autorise les nouvelles connexions HTTP vers le serveur :

```bash
ip netns exec fw iptables -A FORWARD \
    -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT
```

3. Vérifie les deux comportements :

```bash
ip netns exec client wget -q -O - http://10.90.2.10/
ip netns exec client ping -c 2 10.90.2.10
```

`wget` doit afficher `FW-LAB-OK`. Le ping doit échouer.

4. Inspecte les règles et les compteurs :

```bash
ip netns exec fw iptables -L FORWARD -n -v
```

## Pourquoi le retour doit être autorisé

Une connexion TCP est une conversation dans les deux sens. Le client envoie un
paquet `SYN` (état `NEW`). Le serveur répond `SYN-ACK` : ce paquet appartient à
une connexion déjà connue, donc à l'état `ESTABLISHED`. Sans la règle
`ESTABLISHED,RELATED`, la politique `DROP` bloque la réponse et HTTP ne
fonctionne jamais, même si le port 80 est autorisé à l'aller.

| État conntrack | Signification |
|---|---|
| `NEW` | Premier paquet d'une nouvelle connexion. |
| `ESTABLISHED` | Paquet appartenant à une connexion déjà vue dans les deux sens. |
| `RELATED` | Connexion liée à une autre, par exemple FTP ou ICMP d'erreur. |
| `INVALID` | Paquet qui ne correspond à aucune connexion connue. |

Le firewall stateful ne se contente donc pas de filtrer des adresses et des
ports : il suit l'état des connexions. C'est la différence essentielle avec une
ACL stateless.

## Critères de validation

Le script `check.sh` vérifie :

- le nouveau ping `client -> server` échoue ;
- HTTP `client -> server` fonctionne ;
- une règle `conntrack` est visible dans la chaîne `FORWARD`.

## Pistes en cas d'échec

- Vérifie que la politique est bien `DROP` :
  `ip netns exec fw iptables -L FORWARD -n`.
- Vérifie l'ordre des règles : `ESTABLISHED,RELATED` doit être évaluée avant le
  refus implicite de la politique.
- Si HTTP échoue, regarde les compteurs : le `SYN` est peut-être accepté, mais
  le retour est bloqué.
- Si le ping passe, une règle ICMP trop large a probablement été ajoutée.
- Vérifie le forwarding :
  `ip netns exec fw cat /proc/sys/net/ipv4/ip_forward`.
- Le serveur HTTP écoute sur `10.90.2.10:80` et répond `FW-LAB-OK`.

> En production, on combine souvent une politique par défaut `DROP`, des règles
> explicites pour les flux autorisés et le suivi de connexions. On surveille
> aussi les compteurs et les journaux pour détecter les flux refusés.
