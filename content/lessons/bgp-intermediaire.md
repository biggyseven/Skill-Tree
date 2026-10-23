
# BGP – Intermédiaire

Maintenant que vous savez faire une session de base, explorons l'intérieur de BGP : les états de voisinage, les attributs et le iBGP.

## 1. Les états de voisinage BGP

Quand deux routeurs BGP se connectent, ils passent par 6 états :
1. **Idle** : Le routeur cherche une route vers le voisin.
2. **Connect** : La session TCP (port 179) est en cours d'établissement.
3. **Active** : Le routeur essaie d'initier la connexion TCP. *(Si ça reste bloqué ici, c'est qu'il n'y a pas de route ou qu'un pare-feu bloque le port 179).*
4. **OpenSent** : Les paramètres de base (Version, AS) sont échangés.
5. **OpenConfirm** : En attente du Keepalive.
6. **Established** : La session est établie, les routeurs s'échangent les routes.

## 2. iBGP vs eBGP

- **eBGP** : Entre deux AS différents. La TTL est de 1 par défaut.
- **iBGP** : À l'intérieur du même AS. La TTL est de 255. 
> **Règle d'or du iBGP** : Un routeur qui apprend une route via iBGP ne peut pas la transmettre à un autre routeur iBGP. C'est la règle du "Split Horizon" BGP. Pour contourner cela, on utilise un **Route Reflector** (vu au niveau Expert).

## 3. Le Next-Hop (Prochain saut)

Dans eBGP, le Next-Hop est l'adresse IP du voisin eBGP.
Dans iBGP, le Next-Hop est conservé tel qu'il a été appris par eBGP. **Attention** : Si l'adresse Next-Hop n'est pas dans la table de routage IGP (OSPF) du routeur, la route BGP sera marquée comme inaccessible. On utilise alors la commande `next-hop-self` sur le routeur frontière.

```cisco
router bgp 65001
 neighbor 10.0.0.2 next-hop-self
4. L'attribut AS_PATH
Chaque fois qu'une route traverse un AS, son numéro est ajouté à l'attribut AS_PATH.
BGP préfère toujours le chemin avec l'AS_PATH le plus court.
(Si la route est annoncée à l'intérieur du même AS, l'AS_PATH n'est pas modifié).