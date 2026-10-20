# Lab dépannage routage : la route de retour manquante

## Objectif

Deux réseaux ne communiquent pas. Le ping part de `h1`, atteint `h2`, mais la
réponse ne revient jamais. Tu dois trouver **quel routeur ne sait pas joindre le
réseau de retour** et ajouter la route par défaut manquante.

```text
10.40.1.0/24          10.40.2.0/24          10.40.3.0/24
+------+    +------+          +------+    +------+
|  h1  |----|  r1  |----------|  r2  |----|  h2  |
| .10  |    |  .1  |          |  .2  |    | .10  |
+------+    +------+          +------+    +------+
             GW .2  --------->  <-------- GW .1
                                  X
                          pas de route par defaut
```

| Équipement | Adresses | Route par défaut |
|------------|----------|------------------|
| `h1` | `10.40.1.10/24` | `10.40.1.1` |
| `r1` | `10.40.1.1/24`, `10.40.2.1/24` | `10.40.2.2` |
| `r2` | `10.40.2.2/24`, `10.40.3.1/24` | **absente** |
| `h2` | `10.40.3.10/24` | `10.40.3.1` |

## Ce qui est déjà prêt

Le script `setup.sh` crée les quatre namespaces, les liens, les adresses, les
routes des extrémités et active le forwarding sur `r1` et `r2`.

Le routage aller fonctionne : `h1` envoie vers `r1`, qui envoie vers `r2`, qui
livre à `h2`. Le retour échoue car `r2` ne possède aucune route vers
`10.40.1.0/24` et aucune route par défaut.

## Travail demandé

1. Reproduis la panne et lis les tables de routage :

```bash
ip netns exec h1 ping -c 2 10.40.3.10
ip netns exec r2 ip route
ip netns exec h2 ip route
```

2. Ajoute la route par défaut sur `r2` :

```bash
ip netns exec r2 ip route add default via 10.40.2.1
```

3. Vérifie dans les deux sens :

```bash
ip netns exec h1 ping -c 2 10.40.3.10
ip netns exec h2 ping -c 2 10.40.1.10
ip netns exec r2 ip route
```

## Méthode de diagnostic

Un ping qui part mais ne revient pas est souvent un problème de **route de
retour**. La bonne méthode est de suivre le paquet dans les deux sens :

1. Le paquet sort-il de `h1` ? Vérifie la route par défaut et l'ARP.
2. Arrive-t-il sur `r1` ? Vérifie `ip route` et le forwarding.
3. Arrive-t-il sur `r2` ? Vérifie la route vers `10.40.3.0/24`.
4. La réponse de `h2` trouve-t-elle une route vers `10.40.1.0/24` ?
5. Le forwarding est-il actif sur chaque routeur traversé ?

Une route par défaut est utilisée quand aucune route plus spécifique ne
correspond. Sur `r2`, elle doit pointer vers `r1` (`10.40.2.1`), pas vers
`h1` directement : les routeurs ne sont pas sur le même réseau.

## Critères de validation

Le script `check.sh` vérifie :

- la présence d'une route par défaut sur `r2` via `10.40.2.1` ;
- le ping `h1 -> h2` ;
- le ping `h2 -> h1`.

## Pistes en cas d'échec

- Vérifie que tu as ajouté la route dans le namespace `r2` :
  `ip netns exec r2 ip route`.
- Vérifie le forwarding :
  `ip netns exec r2 cat /proc/sys/net/ipv4/ip_forward`.
- Vérifie que `r1` a bien une route vers `10.40.3.0/24` (sa route par défaut
  vers `10.40.2.2` suffit).
- Si le ping fonctionne dans un sens seulement, compare les tables de routage
  des deux routeurs.
- Ne modifie pas les adresses : le contrôle attend la topologie fournie.

> En production, une route manquante peut être masquée par le cache ARP ou par
> un test lancé depuis le mauvais équipement. On teste toujours depuis les deux
> extrémités et on lit la table de routage du routeur de transit.
