# Lab ACL : bloquer ICMP sans couper HTTP

## Objectif

Le routeur `r1` relie deux réseaux. Le serveur `h2` expose un service HTTP. Tu
dois utiliser `iptables` sur le routeur pour **interdire le ping** entre `h1` et
`h2`, tout en **laissant passer HTTP**.

```text
     10.10.1.0/24                         10.10.2.0/24
+--------+            +--------+            +--------+
|   h1   |            |   r1   |            |   h2   |
| .10    |<---------->| .1  .1 |<---------->| .10    |
+--------+  veth-h1   +--------+  veth-h2   +--------+
                       routeur                HTTP :80
```

Adresses :

| Équipement | Interface | Adresse | Passerelle |
|------------|-----------|---------|------------|
| `h1` | `veth-h1` | `10.10.1.10/24` | `10.10.1.1` |
| `r1` | `veth-r1a` | `10.10.1.1/24` | — |
| `r1` | `veth-r1b` | `10.10.2.1/24` | — |
| `h2` | `veth-h2` | `10.10.2.10/24` | `10.10.2.1` |

## Ce qui est déjà prêt

Le script `setup.sh` :

- crée les trois namespaces et les deux liens ;
- configure les adresses et les routes par défaut ;
- active le forwarding IPv4 sur `r1` ;
- démarre un petit serveur HTTP sur `h2`.

Le routage et HTTP fonctionnent **avant** le filtrage. C'est normal : le but est
d'ajouter une règle sans casser le service.

## Travail demandé

Ajoute une règle dans la chaîne `FORWARD` du routeur `r1` pour bloquer ICMP :

```bash
ip netns exec r1 iptables -A FORWARD -p icmp -j DROP
```

Tu peux aussi cibler uniquement les demandes d'écho :

```bash
ip netns exec r1 iptables -A FORWARD -p icmp --icmp-type echo-request -j DROP
```

Vérifie ensuite :

```bash
ip netns exec h1 ping -c 2 10.10.2.10
ip netns exec h1 wget -q -O - http://10.10.2.10/
```

Le ping doit échouer et `wget` doit afficher `ACL-LAB-OK`.

## Pourquoi ça marche

`iptables` est évalué dans l'ordre. Une règle `DROP` sur le protocole ICMP
supprime les paquets ICMP, mais ne touche pas aux paquets TCP du port 80. C'est
tout l'intérêt d'une ACL : filtrer un flux précis sans bloquer les autres.

| Chaîne | Trafic concerné |
|--------|------------------|
| `INPUT` | Paquets destinés au routeur lui-même. |
| `FORWARD` | Paquets qui traversent le routeur. |
| `OUTPUT` | Paquets émis par le routeur. |

Ici, le ping de `h1` vers `h2` **traverse** `r1` : il passe donc par `FORWARD`.

## Critères de validation

Le script `check.sh` vérifie :

- le ping de `h1` vers `h2` échoue ;
- HTTP de `h1` vers `h2` fonctionne toujours ;
- une règle de filtrage est visible dans la chaîne `FORWARD`.

## Pistes en cas d'échec

- Vérifie que tu as bien appliqué la règle dans le namespace `r1` :
  `ip netns exec r1 iptables -L FORWARD -n -v`.
- Vérifie que le forwarding est actif :
  `ip netns exec r1 cat /proc/sys/net/ipv4/ip_forward`.
- Teste le serveur localement : `ip netns exec h2 wget -q -O - http://10.10.2.10/`.
- Si HTTP ne marche plus, tu as probablement bloqué tout le trafic au lieu de
  filtrer seulement ICMP.
- Le contrôle accepte `DROP` et `REJECT` : les deux empêchent le ping.

> En production, on documente toujours la règle et on vérifie le flux autorisé
> après l'avoir appliquée. Une ACL trop large peut couper un service sans que le
> ping ne le montre.
