# Lab : OSPF et routage entre deux routeurs Linux

## Topologie

```text
        LAN 1                                            LAN 2
  192.168.10.0/24                                  192.168.20.0/24
        |                                                 |
     h1-eth0                                          h2-eth0
  192.168.10.10                                    192.168.20.20
        |                                                 |
   [ h1 ]                                             [ h2 ]
        |                                                 |
     r1-lan                                            r2-lan
  192.168.10.1                                      192.168.20.1
        |                                                 |
   [ r1 ]================= 10.255.0.0/30 =============[ r2 ]
      r1-wan .1                                      r2-wan .2
```

Quatre namespaces sont deja crees : `h1`, `r1`, `r2` et `h2`.

| Équipement | Interface | Adresse | Rôle |
| --- | --- | --- | --- |
| h1 | h1-eth0 | `192.168.10.10/24` | Hôte du réseau 1 |
| r1 | r1-lan | `192.168.10.1/24` | Passerelle du réseau 1 |
| r1 | r1-wan | `10.255.0.1/30` | Lien vers r2 |
| r2 | r2-wan | `10.255.0.2/30` | Lien vers r1 |
| r2 | r2-lan | `192.168.20.1/24` | Passerelle du réseau 2 |
| h2 | h2-eth0 | `192.168.20.20/24` | Hôte du réseau 2 |

Les adresses sont déjà configurées, les liens sont up, le forwarding IP est
activé sur `r1` et `r2`, et les hôtes ont une route par défaut vers leur
passerelle. **Il manque les routes vers le réseau distant sur les deux
routeurs.**

## Objectif

Faire communiquer `h1` et `h2` dans les deux sens :

```text
h1 (192.168.10.10)  ->  r1  ->  r2  ->  h2 (192.168.20.20)
h2 (192.168.20.20)  ->  r2  ->  r1  ->  h1 (192.168.10.10)
```

Le `check.sh` exécute un ping de `h1` vers `h2`, puis de `h2` vers `h1`. Les
deux sens doivent fonctionner : une route aller sans route retour produit un
ping qui échoue.

## Solution avec routes statiques

Depuis le shell du lab, saisis une commande par ligne :

```sh
ip netns exec r1 ip route add 192.168.20.0/24 via 10.255.0.2
ip netns exec r2 ip route add 192.168.10.0/24 via 10.255.0.1
```

Vérifie ensuite :

```sh
ip netns exec r1 ip route
ip netns exec r2 ip route
ip netns exec h1 ping -c 2 192.168.20.20
ip netns exec h2 ping -c 2 192.168.10.10
```

La route de `r1` indique que `192.168.20.0/24` est joignable via `10.255.0.2`
sur `r1-wan`. La route de `r2` fait le chemin inverse. Les hôtes utilisent leur
route par défaut ; les routeurs doivent connaître le réseau distant.

## Variante avec un démon de routage

L'image `skilltree/lab:latest` ne contient pas BIRD ou FRRouting par défaut.
Les routes statiques ci-dessus sont donc la solution immédiate. Si tu utilises
une image enrichie avec BIRD ou FRRouting, tu peux configurer OSPF sur le lien
`10.255.0.0/30` et annoncer les réseaux `192.168.10.0/24` et
`192.168.20.0/24`. Le principe reste le même :

- les deux routeurs doivent former une adjacence OSPF sur le lien ;
- chaque routeur doit annoncer son LAN ;
- la table de routage doit contenir la route vers le LAN distant ;
- le forwarding IP doit rester activé ;
- le check valide la connectivité de bout en bout, pas la méthode utilisée.

Exemple de vérification avec FRRouting (si disponible) :

```sh
vtysh -c "show ip ospf neighbor"
vtysh -c "show ip route"
```

Ne lance pas un démon de routage sans connaître son fichier de configuration
et ses interfaces : une mauvaise annonce peut créer une route par défaut ou
une adjacence inattendue.

## Diagnostic

### Vérifier le lien et les adresses

```sh
ip netns exec r1 ip -br addr
ip netns exec r2 ip -br addr
ip netns exec r1 ping -c 2 10.255.0.2
ip netns exec h1 ping -c 2 192.168.10.1
ip netns exec h2 ping -c 2 192.168.20.1
```

### Vérifier le forwarding

```sh
ip netns exec r1 sysctl net.ipv4.ip_forward
ip netns exec r2 sysctl net.ipv4.ip_forward
```

La valeur doit être `1`. Si elle vaut `0`, active-la :

```sh
mount -o remount,rw /proc/sys 2>/dev/null || true
ip netns exec r1 sysctl -w net.ipv4.ip_forward=1
ip netns exec r2 sysctl -w net.ipv4.ip_forward=1
```

### Vérifier les routes

```sh
ip netns exec r1 ip route get 192.168.20.20
ip netns exec r2 ip route get 192.168.10.10
ip netns exec h1 ip route
ip netns exec h2 ip route
```

Si `r1` n'a pas de route vers `192.168.20.0/24`, le paquet est abandonné ou
envoyé vers une route par défaut absente. Si `r2` n'a pas de route retour vers
`192.168.10.0/24`, la requête arrive mais la réponse ne revient pas : le ping
échoue et peut donner l'impression que le lien est coupé.

### Capturer le trafic

```sh
ip netns exec r1 tcpdump -ni r1-wan -c 10
ip netns exec r2 tcpdump -ni r2-wan -c 10
ip netns exec h1 tcpdump -ni h1-eth0 -c 10
```

Une requête ICMP doit apparaître sur `h1-eth0`, puis sur `r1-wan`, `r2-wan`
et `h2-eth0`. Si elle disparaît après `r1-wan`, vérifie la route de `r2` et
son forwarding. Si elle arrive à `h2` mais que la réponse n'apparaît pas sur
`r2-wan`, vérifie la route retour de `r2`.

## Critères de réussite

- `h1` joint `h2` ;
- `h2` joint `h1` ;
- aucune route par défaut n'a été ajoutée sur les routeurs pour contourner
  l'exercice ;
- les routes vers les LAN distants sont visibles dans `ip route` ;
- le forwarding est actif sur les deux routeurs.

## Commandes utiles

```sh
ip netns list
ip netns exec <ns> ip route
ip netns exec <ns> ip -br addr
ip netns exec <ns> ping -c 2 <destination>
ip netns exec <ns> tcpdump -ni <interface> -c 10
```
