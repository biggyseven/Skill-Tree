
# BGP – Expert (CCIE)

Bienvenue à l'ultime niveau de BGP. Ici, on ne parle plus de configuration basique, mais d'ingénierie de trafic (Traffic Engineering) et d'optimisation.


## 1. La sélection de route BGP (Le fameux Best Path)

BGP a une table de routage immense. Comment choisit-il la meilleure route ? Il utilise un algorithme strict. Les étapes les plus importantes (dans l'ordre) sont :
1. **Weight** (Propriétaire Cisco, local au routeur). Plus il est lourd, mieux c'est.
2. **Local Preference** (LP). Plus il est élevé, mieux c'est. (Propagé dans tout l'AS).
3. **Origine locale** (Route injectée par `network` ou `redistribute`).
4. **AS_PATH** le plus court.
5. **Origin** (IGP < EGP < Incomplete).
6. **MED** (Multi-Exit Discriminator). Plus il est petit, mieux c'est.

## 2. Les attributs BGP en pratique

- **Weight** : 
  ```cisco
  neighbor 10.0.0.1 weight 200
Local Preference :

cisco
neighbor 10.0.0.1 route-map SET-LP in
route-map SET-LP permit 10
 set local-preference 200
AS_PATH Prepending (Allonger l'AS_PATH pour rendre une route moins attractive) :

cisco
neighbor 10.0.0.1 route-map PREPEND out
route-map PREPEND permit 10
 set as-path prepend 65001 65001 65001
3. Les Route Reflectors (RR)
Pour contourner la règle du Split Horizon du iBGP, on utilise des Route Reflectors. Un RR est un routeur iBGP spécial qui est autorisé à réfléchir (réfléchir = transmettre) les routes aux autres clients iBGP.

cisco
router bgp 65001
 neighbor 10.0.0.2 route-reflector-client
4. Les Peer Groups
Si vous avez 50 voisins BGP avec la même politique, configurez un Peer Group pour éviter de répéter les commandes 50 fois.

cisco
router bgp 65001
 neighbor ISP-PEERS peer-group
 neighbor ISP-PEERS remote-as 65002
 neighbor ISP-PEERS route-map FILTER in
 neighbor 192.168.1.1 peer-group ISP-PEERS
 neighbor 192.168.1.5 peer-group ISP-PEERS
5. Le filtrage (Prefix-List)
Ne croyez jamais un voisin BGP sur parole. Filtrez toujours les routes entrantes et sortantes.

cisco
ip prefix-list ALLOWED-NETS seq 10 permit 10.0.0.0/8 le 24
router bgp 65001
 neighbor 10.0.0.2 prefix-list ALLOWED-NETS in
