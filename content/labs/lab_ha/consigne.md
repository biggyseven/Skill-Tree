# Lab Haute Disponibilité : bonding LACP

## Objectif

Deux namespaces Linux sont reliés par **deux liens veth**. Tu dois créer un
bond Linux en mode **802.3ad (LACP)** sur chaque rive, poser les adresses IP
sur les bonds et vérifier que le trafic passe bien par le bond.

```text
ns1 veth1a ==================== veth1b ns2
ns1 veth2a ==================== veth2b ns2

        bond0                            bond0
      10.10.0.1/24                    10.10.0.2/24
```

Le mode `802.3ad` agrège les deux liens et négocie LACP avec le partenaire.
L'objectif est de comprendre qu'un bond ne se résume pas à mettre deux câbles
dans une machine : il faut aussi que les deux extrémités soient configurées de
la même façon.

## Ce qui est déjà prêt

Le script `setup.sh` crée :

- les namespaces `ns1` et `ns2` ;
- les paires `veth1a/veth1b` et `veth2a/veth2b` ;
- les liens et les interfaces loopback.

Les bonds ne sont **pas** créés. C'est ton travail.

## Travail demandé

Configure `bond0` dans `ns1` :

```bash
ip netns exec ns1 ip link add bond0 type bond mode 802.3ad miimon 100 lacp_rate fast xmit_hash_policy layer3+4

ip netns exec ns1 ip link set veth1a down
ip netns exec ns1 ip link set veth2a down
ip netns exec ns1 ip link set veth1a master bond0
ip netns exec ns1 ip link set veth2a master bond0
ip netns exec ns1 ip link set veth1a up
ip netns exec ns1 ip link set veth2a up

ip netns exec ns1 ip addr add 10.10.0.1/24 dev bond0
ip netns exec ns1 ip link set bond0 up
```

Configure `bond0` dans `ns2` :

```bash
ip netns exec ns2 ip link add bond0 type bond mode 802.3ad miimon 100 lacp_rate fast xmit_hash_policy layer3+4

ip netns exec ns2 ip link set veth1b down
ip netns exec ns2 ip link set veth2b down
ip netns exec ns2 ip link set veth1b master bond0
ip netns exec ns2 ip link set veth2b master bond0
ip netns exec ns2 ip link set veth1b up
ip netns exec ns2 ip link set veth2b up

ip netns exec ns2 ip addr add 10.10.0.2/24 dev bond0
ip netns exec ns2 ip link set bond0 up
```

Attends quelques secondes que LACP négocie, puis teste :

```bash
ip netns exec ns1 ping -c 3 10.10.0.2
ip netns exec ns2 ping -c 3 10.10.0.1
```

Tu peux vérifier l'état du bond avec :

```bash
ip netns exec ns1 cat /proc/net/bonding/bond0
ip netns exec ns1 ip -s link show bond0
ip netns exec ns2 cat /proc/net/bonding/bond0
```

## Critères de validation

Le script `check.sh` vérifie :

- la présence de `bond0` dans les deux namespaces ;
- le mode `802.3ad` sur les deux bonds ;
- la présence de `veth1a` et `veth2a` dans le bond de `ns1` ;
- la présence de `veth1b` et `veth2b` dans le bond de `ns2` ;
- les adresses `10.10.0.1/24` et `10.10.0.2/24` ;
- que la route vers l'autre namespace passe par `bond0` ;
- le ping bidirectionnel ;
- l'activité des compteurs `rx_bytes` et `tx_bytes` du bond.

## Pistes en cas d'échec

- Vérifie que le mode est bien `802.3ad` des deux côtés.
- Vérifie que les deux veths sont membres du bond, pas seulement un.
- Vérifie que `bond0` est `up`.
- Vérifie que les adresses sont posées sur `bond0`, pas sur les veths.
- Attends quelques secondes après la configuration : LACP doit négocier.
- Regarde `/proc/net/bonding/bond0` : les interfaces doivent apparaître avec
  un état MII `up`.
- Les commandes `ip netns exec` sont exécutées dans le conteneur : garde les
  noms `ns1`, `ns2`, `veth1a`, `veth2a`, `veth1b` et `veth2b`.

## Pourquoi c'est utile

Un bond LACP apporte de la redondance et de la capacité. Si un lien tombe, le
bond peut continuer à transmettre sur l'autre. Mais il faut que le partenaire
(l'autre switch ou l'autre serveur) parle aussi LACP. Un mauvais mode ou un
seul lien actif donne une fausse impression de redondance.

> En production, on vérifie toujours les deux extrémités, la négociation LACP,
> les compteurs par esclave et la politique de répartition avant de conclure
> qu'un bond est réellement opérationnel.
