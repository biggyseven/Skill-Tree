# Lab dépannage MTU : les petits paquets passent, les gros échouent

## Objectif

Le ping classique fonctionne entre `h1` et `h2`, mais les transferts de gros
paquets échouent. Le lien de transit entre `r1` et `h2` a un MTU plus petit que
celui des interfaces des hôtes. Tu dois identifier le MTU limitant et l'ajuster
sur `h1` pour que les paquets de 1400 octets passent avec le bit DF.

```text
        h1                          r1                          h2
+----------------+          +----------------+          +----------------+
| veth-h1        |          | veth-r1a       |          | veth-h2        |
| 10.60.1.10/24  |<-------->| 10.60.1.1/24   |          | 10.60.2.10/24  |
| MTU 1500       |          |                |          | MTU 1500       |
+----------------+          | veth-r1b       |          +----------------+
                            | 10.60.2.1/24   |<-------->
                            | MTU 1400       |
                            +----------------+
```

Le lien `r1` ↔ `h2` est limité à **1400 octets**. Un paquet IP de 1500 octets
avec DF ne peut pas être transmis tel quel : le routeur le rejette et renvoie
normalement un message ICMP « fragmentation needed ».

## Ce qui est déjà prêt

Le script `setup.sh` crée les namespaces, les adresses, les routes et active le
forwarding. Il applique aussi le MTU 1400 sur l'interface de transit de `r1`.

Le petit ping et les paquets sans DF peuvent fonctionner grâce à la
fragmentation. Le test avec DF met en évidence le problème.

## Travail demandé

1. Reproduis le symptôme avec un ping de 1500 octets IP et DF :

```bash
ip netns exec h1 ping -c 1 -M do -s 1472 10.60.2.10
```

L'option `-s 1472` correspond à 1472 octets de données ICMP, soit 1500 octets
IP une fois les en-têtes ajoutés. `-M do` interdit la fragmentation. Le paquet
ne peut pas traverser le lien limité à 1400 octets.

2. Lis les MTU des interfaces :

```bash
ip netns exec h1 ip link show veth-h1
ip netns exec r1 ip link show veth-r1b
ip netns exec h2 ip link show veth-h2
```

3. Abaisse le MTU de `h1` à 1400 :

```bash
ip netns exec h1 ip link set veth-h1 mtu 1400
```

4. Vérifie que le petit et le gros ping passent :

```bash
ip netns exec h1 ping -c 2 10.60.2.10
ip netns exec h1 ping -c 1 -M do -s 1372 10.60.2.10
```

## Comprendre le MTU

Le MTU (Maximum Transmission Unit) est la taille maximale d'une trame IP sur une
interface. Quand un paquet dépasse le MTU d'un lien :

- sans DF, le routeur peut fragmenter le paquet ;
- avec DF, le routeur le rejette et prévient la source avec ICMP.

La fragmentation coûte du CPU et peut poser des problèmes de sécurité ou de
performance. En pratique, on préfère souvent aligner le MTU des extrémités sur
le plus petit MTU du chemin, ou utiliser le PMTUD (Path MTU Discovery).

| Élément | Valeur dans ce lab |
|---------|--------------------|
| MTU de `h1` | 1500 (à corriger) |
| MTU du transit `r1` ↔ `h2` | 1400 |
| Taille IP du test de reproduction | 1500 |
| Taille des données ICMP de reproduction | 1472 |
| Taille IP après correction | 1400 |
| Taille des données ICMP après correction | 1372 |

## Critères de validation

Le script `check.sh` vérifie :

- le MTU de `veth-h1` dans `h1` est inférieur ou égal à 1400 ;
- le petit ping fonctionne ;
- le ping de 1400 octets IP avec DF fonctionne.

## Pistes en cas d'échec

- Vérifie que tu as changé le MTU dans le bon namespace :
  `ip netns exec h1 ip link show veth-h1`.
- Ne modifie pas seulement le routeur : le contrôle vérifie le MTU de `h1`.
- Si tu choisis un MTU inférieur à 1400, le test de 1400 octets échouera aussi.
- Si le petit ping échoue, vérifie les routes et le forwarding.
- Le test `ping -M do -s 1372` doit produire un paquet IP de 1400 octets ;
  c'est le cas limite qui doit passer.

> Un MTU mal réglé peut donner des symptômes trompeurs : navigation lente,
> connexions SSH qui se bloquent après l'authentification, transferts de
> fichiers qui échouent alors que le ping fonctionne. On teste toujours avec
> des paquets de taille connue et le bit DF.
