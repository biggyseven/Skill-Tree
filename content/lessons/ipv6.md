# IPv6 et NDP (Neighbor Discovery Protocol)

**Niveau :** débutant à intermédiaire  
**Objectifs :** lire une adresse IPv6, comprendre les types d’adresses et les préfixes, expliquer SLAAC et identifier les principaux messages NDP.

## 1. Pourquoi IPv6 ?

IPv6 est la version 6 du protocole Internet, conçue notamment pour disposer d’un espace d’adressage très vaste et moderniser certains aspects de l’IP. Une adresse IPv6 fait **128 bits**, contre 32 bits pour IPv4. IPv6 ne se sert pas de la diffusion Ethernet broadcast pour la découverte des voisins : il emploie notamment le multicast.

## 2. Format d’une adresse IPv6

Une adresse de 128 bits est généralement écrite en huit groupes hexadécimaux de 16 bits séparés par des deux-points. Chaque groupe représente quatre chiffres hexadécimaux au maximum.

```text
2001:0db8:0000:0000:02aa:00ff:fe28:9c5a
|----| |----| |----| |----| |----| |----| |----| |----|
 16 bits par groupe × 8 groupes = 128 bits
```

### Règles de simplification

- Les zéros au début d’un groupe peuvent être omis : `0db8` devient `db8`.
- Une seule séquence continue de groupes `0000` peut être remplacée par `::`.
- `::` ne peut apparaître qu’une seule fois dans une adresse, sinon la longueur de l’adresse deviendrait ambiguë.

Exemple :

```text
Adresse complète : 2001:0db8:0000:0000:0000:0000:0000:0025
Adresse abrégée  : 2001:db8::25
```

Le préfixe `/64` signifie que les 64 premiers bits identifient le préfixe réseau et que les 64 bits restants forment l’identifiant d’interface, dans le schéma courant d’un LAN. `/64` est le cas habituel pour SLAAC sur les LAN Ethernet, mais tous les préfixes IPv6 ne sont pas nécessairement `/64`.

```text
2001:db8:1234:0001: 0000:0000:0000:0042
|------ préfixe /64 ------| | identifiant d’interface |
```

## 3. Types d’adresses IPv6 importants

| Type | Préfixe / exemple | Utilisation |
|---|---|---|
| Global Unicast | `2000::/3` | Adresses globales unicast couramment routables sur Internet, selon l’allocation et la politique réseau |
| Link-local | `fe80::/10` | Communication sur le lien local ; utilisée notamment par NDP et pour les next-hops IPv6 |
| Unique Local (ULA) | `fc00::/7` | Adresses à portée privée/interne ; elles ne sont pas destinées au routage global public |
| Multicast | `ff00::/8` | Envoyer un paquet à un groupe d’interfaces ; utilisé par NDP |
| Unspecified | `::` | Adresse non spécifiée, par exemple comme source pendant certaines vérifications initiales ; pas une adresse d’hôte utilisable comme destination ordinaire |
| Loopback | `::1` | La machine elle-même, équivalent fonctionnel de `127.0.0.1` en IPv4 |

IPv6 **n’a pas de broadcast**. Le multicast remplit des fonctions de diffusion ciblée vers un groupe, sans être identique au broadcast IPv4.

## 4. En quoi consiste SLAAC ?

**SLAAC** (*Stateless Address Autoconfiguration*) permet à un hôte de configurer automatiquement ses adresses IPv6 à partir des informations locales et des annonces de routeurs, sans qu’un serveur DHCPv6 attribue nécessairement chaque adresse.

### Déroulement simplifié

```text
Hôte IPv6                           Routeur IPv6
    |                                    |
    | (1) Crée une adresse link-local    |
    |     dans fe80::/10                 |
    |                                    |
    | (2) Router Solicitation (RS) ----->|  facultatif, sollicite une annonce
    |<----------- Router Advertisement (RA) (préfixe, durée, paramètres, flags)
    |                                    |
    | (3) Forme une adresse à partir     |
    |     du préfixe annoncé et d’un     |
    |     identifiant d’interface       |
    |                                    |
    | (4) DAD : vérifie l’unicité         |
    |     avec Neighbor Solicitation     |
    |                                    |
    | (5) Utilise l’adresse si elle       |
    |     n’est pas détectée en doublon  |
```

Points importants :

1. L’hôte crée généralement une adresse **link-local** pour communiquer sur le lien local.
2. Il reçoit des **Router Advertisements (RA)** périodiques ou sollicités, avec les préfixes et des paramètres réseau.
3. Si le préfixe annoncé autorise l’autoconfiguration autonome, l’hôte combine le préfixe avec un identifiant d’interface. Celui-ci n’est pas obligatoirement dérivé de la MAC : les systèmes modernes utilisent souvent des identifiants stables ou temporaires pour préserver la confidentialité.
4. La **Duplicate Address Detection (DAD)** vérifie qu’aucun autre nœud n’utilise déjà l’adresse envisagée.
5. Une adresse a des durées de vie et peut passer de l’état préféré à l’état déprécié avant d’expirer.

SLAAC ne signifie pas que DHCPv6 est inutile. Selon le réseau, SLAAC et DHCPv6 peuvent coexister. Les Router Advertisements permettent aux hôtes de découvrir les routeurs par défaut ; DHCPv6, à lui seul, ne remplace généralement pas cette fonction de découverte du routeur.

## 5. Neighbor Discovery Protocol (NDP)

Le **NDP** est un ensemble de fonctions IPv6 défini principalement par la RFC 4861 et transporté par **ICMPv6**. Il couvre plusieurs besoins assurés en IPv4 par une combinaison d’ARP, de mécanismes de découverte de routeurs et de redirection ICMP.

### Messages principaux

| Message | Abréviation | Rôle principal |
|---|---|---|
| Router Solicitation | RS | Un hôte sollicite rapidement une annonce de routeur |
| Router Advertisement | RA | Un routeur annonce sa présence, des préfixes et des paramètres |
| Neighbor Solicitation | NS | Résolution d’adresse de couche 2, vérification de voisin ou DAD |
| Neighbor Advertisement | NA | Réponse à une NS ou annonce d’un changement d’adresse de couche 2 |
| Redirect | — | Un routeur indique à un hôte un meilleur prochain saut pour une destination |

### Résolution d’un voisin IPv6

Si PC-A doit envoyer un paquet à une adresse IPv6 sur le même lien mais ne connaît pas sa MAC, il envoie une **Neighbor Solicitation (NS)** vers une adresse multicast *solicited-node* associée à la cible. La cible répond généralement par une **Neighbor Advertisement (NA)** contenant son adresse de couche 2.

```text
PC-A IPv6                                             PC-B IPv6
  |                                                      |
  | NS envoyée au multicast solicited-node de PC-B       |
  |----------------------------------------------------->|
  |                                                      |
  |<-----------------------------------------------------|
  | NA : adresse IPv6 cible et information MAC            |
  |                                                      |
  | Cache des voisins mis à jour ; trame envoyée à la MAC |
```

NDP tient un **cache des voisins** qui associe les adresses IPv6 voisines à des informations de couche 2 et de joignabilité. Il utilise notamment des états pour gérer la confirmation qu’un voisin est encore joignable. Cela rappelle le cache ARP, mais NDP va au-delà de la simple résolution IP/MAC.

### NDP comparé à ARP

| Fonction | IPv4 | IPv6 |
|---|---|---|
| Résolution adresse réseau → MAC | ARP | Neighbor Solicitation / Advertisement (NDP) |
| Découverte des routeurs | Mécanismes IPv4 dédiés, souvent DHCP/configuration en pratique | Router Solicitation / Advertisement (NDP) |
| Détection de doublons d’adresse | Mécanismes IPv4, par exemple ARP Probe selon le contexte | Duplicate Address Detection (DAD), basée sur NS |
| Transport de contrôle | ARP directement sur le lien local Ethernet | Messages NDP transportés par ICMPv6 |
| Broadcast | Fréquent pour les requêtes ARP sur Ethernet | Pas de broadcast IPv6 ; utilisation du multicast |

## 6. Sécurité IPv6/NDP

NDP est essentiel au fonctionnement local d’IPv6, mais les messages de découverte doivent être correctement contrôlés dans les environnements non fiables. Un attaquant présent sur le même lien peut tenter de diffuser de fausses annonces de voisin ou de routeur (*Neighbor Advertisement spoofing*, *rogue RA*), perturber la connectivité ou détourner du trafic.

Mesures de réduction des risques :

- Activer **RA Guard** et les contrôles de sécurité de couche 2 lorsque les commutateurs les prennent en charge ; définir quels ports peuvent légitimement envoyer des RA.
- Segmenter le réseau et limiter l’accès physique ou logique au même lien.
- Surveiller les annonces de routeurs, les changements de voisinage et les conflits d’adresses.
- Garder les systèmes et équipements à jour et utiliser les protections IPv6 adaptées à leur environnement.
- Ne pas désactiver ICMPv6 indistinctement : IPv6 et NDP dépendent de messages ICMPv6 pour plusieurs fonctions nécessaires.

Les mécanismes de protection avancés, comme SEND, existent dans les standards mais ne sont pas universellement déployés. Les capacités de filtrage et les détails de configuration varient selon les fabricants.

## 7. Vérifications pratiques

Commandes courantes (la sortie exacte dépend du système) :

| Système | Voir la configuration IPv6 | Voir les voisins |
|---|---|---|
| Windows | `ipconfig` | `netsh interface ipv6 show neighbors` |
| Linux | `ip -6 address show` | `ip -6 neigh show` |
| macOS | `ifconfig` | `ndp -an` |

Pour diagnostiquer un poste qui a une adresse link-local mais aucune connectivité IPv6 globale, vérifier notamment la présence d’un RA valide, les préfixes et durées de vie annoncés, la route par défaut, les règles de pare-feu ICMPv6/NDP et la configuration du routeur.

## 8. À retenir

1. Une adresse IPv6 contient 128 bits ; l’écriture utilise huit groupes hexadécimaux, avec des règles d’abréviation.
2. `fe80::/10` est le bloc link-local ; `::1` est la loopback ; `ff00::/8` correspond au multicast.
3. SLAAC utilise notamment le préfixe annoncé par un routeur pour aider l’hôte à former sa propre adresse ; DAD vérifie l’absence de doublon.
4. NDP utilise ICMPv6 et fournit la résolution des voisins, la découverte des routeurs, la détection de joignabilité et la redirection.
5. IPv6 n’utilise pas le broadcast ; NDP emploie le multicast.
6. Protéger NDP et les annonces de routeurs est important sur les réseaux partagés.

## Références

- IETF, [RFC 8200 — Internet Protocol, Version 6 (IPv6) Specification](https://www.rfc-editor.org/rfc/rfc8200)
- IETF, [RFC 4291 — IP Version 6 Addressing Architecture](https://www.rfc-editor.org/rfc/rfc4291)
- IETF, [RFC 4861 — Neighbor Discovery for IP version 6 (IPv6)](https://www.rfc-editor.org/rfc/rfc4861)
- IETF, [RFC 4862 — IPv6 Stateless Address Autoconfiguration](https://www.rfc-editor.org/rfc/rfc4862)
