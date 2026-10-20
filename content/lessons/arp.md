# ARP et résolution L2/L3

**Niveau :** débutant à intermédiaire  
**Objectifs :** expliquer la résolution d’adresse IPv4 vers MAC, lire un cache ARP, comprendre le proxy ARP et reconnaître les risques de l’ARP spoofing.

## 1. Situer ARP entre les couches 2 et 3

Dans un réseau Ethernet, l’adresse IP sert à identifier la destination au niveau réseau (**couche 3**), tandis que l’adresse MAC sert à livrer une trame sur le lien local (**couche 2**). ARP (*Address Resolution Protocol*) permet à une machine IPv4 de trouver l’adresse MAC associée à une adresse IPv4 située sur le même lien local.

| Élément | Couche OSI usuelle | Exemple | Rôle |
|---|---:|---|---|
| Adresse IPv4 | 3 — Réseau | `192.168.1.20` | Identifier une interface IP et acheminer les paquets |
| Adresse MAC Ethernet | 2 — Liaison | `00:11:22:33:44:55` | Acheminer une trame sur le réseau local |
| ARP | Entre L2 et L3 | « Qui possède `192.168.1.20` ? » | Résoudre IPv4 → MAC sur un lien local IPv4 |

> **Point essentiel :** ARP ne choisit pas la route IP. La table de routage décide si la destination est locale ou distante ; ARP résout ensuite l’adresse MAC du prochain saut Ethernet.

## 2. Comment fonctionne une résolution ARP ?

Supposons que PC-A (`192.168.1.10/24`, MAC `AA-AA-AA-AA-AA-AA`) veuille contacter PC-B (`192.168.1.20/24`, MAC `BB-BB-BB-BB-BB-BB`) sur le même LAN.

```text
PC-A                         LAN Ethernet                         PC-B
IP .10 / MAC AA                                                   IP .20 / MAC BB
  |                                                                  |
  | 1. Requête ARP en diffusion :                                    |
  |    « Qui possède 192.168.1.20 ? Répondez à 192.168.1.10 » -----> |
  |                                                                  |
  | <---- 2. Réponse ARP, généralement unicast :                     |
  |      « 192.168.1.20 est à BB-BB-BB-BB-BB-BB »                   |
  |                                                                  |
  | 3. PC-A mémorise IP .20 → MAC BB dans son cache                   |
  | 4. PC-A envoie la trame Ethernet à MAC BB, contenant le paquet IP|
```

Étapes détaillées :

1. PC-A consulte sa table de routage pour déterminer que `192.168.1.20` est sur son sous-réseau.
2. PC-A vérifie son cache ARP. Si l’entrée est absente ou inutilisable, il diffuse une requête ARP sur le domaine de diffusion local.
3. Le propriétaire de l’adresse IPv4 répond avec son adresse MAC.
4. PC-A met à jour son cache, puis envoie la trame Ethernet vers cette MAC.

La requête ARP Ethernet est généralement envoyée à l’adresse de diffusion `FF:FF:FF:FF:FF:FF`. Les commutateurs la diffusent dans le même domaine de broadcast, à l’exception du port d’entrée et selon leur configuration.

### Et si la destination est sur un autre réseau ?

PC-A (`192.168.1.10/24`) veut joindre un serveur `192.168.2.50`. Comme le serveur est hors du sous-réseau local, PC-A envoie le paquet IP à sa passerelle, par exemple `192.168.1.1`. Il utilise ARP pour découvrir **la MAC de la passerelle**, pas celle du serveur distant.

```text
PC-A                     Routeur / passerelle                    Serveur distant
192.168.1.10              192.168.1.1                             192.168.2.50
     |                          |                                        |
     | ARP : MAC de .1 ?        |                                        |
     |------------------------->|                                        |
     |<-------------------------|                                        |
     | Trame Ethernet vers MAC du routeur                               |
     | Paquet IP : source .1.10, destination .2.50                       |
     |                          | Route le paquet vers le réseau suivant |
```

À chaque lien Ethernet traversé, l’en-tête de couche 2 est adapté au prochain saut ; les adresses IP source et destination restent en principe celles des hôtes de bout en bout, hors mécanismes tels que NAT.

## 3. Le cache ARP

Le **cache ARP** (ou table ARP) garde temporairement les correspondances IPv4/MAC apprises. Cela évite de rediffuser une requête pour chaque paquet.

| Notion | Description |
|---|---|
| Entrée dynamique | Apprise automatiquement ; elle expire ou est rafraîchie selon le système |
| Entrée statique/permanente | Configurée manuellement ou par politique ; gestion et syntaxe variables selon l’OS |
| Expiration | Une entrée dynamique peut devenir périmée et être vérifiée ou supprimée |
| Cache incorrect | Peut causer une perte de connectivité, un détournement du trafic ou une panne intermittente |

Commandes utiles (selon version et privilèges) :

| Système | Voir le cache | Supprimer/vider des entrées |
|---|---|---|
| Windows | `arp -a` | `arp -d *` (souvent depuis un terminal administrateur) |
| Linux | `ip neigh show` | `ip neigh flush all` (privilèges administrateur généralement requis) |
| macOS | `arp -a` | `sudo arp -d <adresse_IP>` pour une entrée ciblée |

> Les commandes et leur effet peuvent varier selon le système, sa version et les privilèges. Vider un cache peut temporairement provoquer de nouvelles résolutions ARP.

## 4. Proxy ARP

Le **Proxy ARP** permet à un routeur ou à un équipement intermédiaire de répondre à une requête ARP pour une adresse IPv4 qui n’appartient pas directement à son interface, lorsqu’il peut acheminer les paquets vers cette adresse. Il annonce alors **sa propre adresse MAC** afin que l’émetteur lui remette la trame.

```text
Hôte A                         Routeur avec Proxy ARP                   Hôte B
192.168.1.10                   MAC R                                   192.168.2.20
    |                               |                                       |
    | ARP : qui possède .2.20 ?     |                                       |
    |------------------------------>|                                       |
    |<------------------------------| Réponse : .2.20 est à MAC R           |
    | Envoie la trame à MAC R       | Route le paquet IP vers Hôte B        |
```

**Utilité :** permettre, dans certains scénarios, à des hôtes mal configurés ou sans route appropriée d’atteindre des destinations au travers d’un routeur, sans modifier leur configuration.  
**Limites :** ajoute de la complexité et du trafic ARP, masque la topologie réelle, peut produire des comportements difficiles à diagnostiquer et élargit les risques d’usurpation. Il ne remplace pas une conception correcte de l’adressage et du routage. Il doit être activé volontairement lorsque le besoin est compris.

Le Proxy ARP n’est pas la même chose que l’ARP spoofing : le premier est une fonction réseau légitime et configurée ; le second consiste à diffuser des associations IP/MAC mensongères pour tromper les voisins.

## 5. ARP spoofing / empoisonnement du cache ARP

L’**ARP spoofing** (ou *ARP cache poisoning*) est une attaque sur un réseau local IPv4 qui consiste à faire accepter une association IP/MAC falsifiée. ARP ne fournit pas, à lui seul, un mécanisme cryptographique d’authentification des réponses.

Exemple : un attaquant annonce à PC-A que l’IP de la passerelle correspond à la MAC de l’attaquant. Le trafic destiné à la passerelle peut alors être envoyé vers l’attaquant.

```text
                  Réponse ARP falsifiée : « passerelle → MAC attaquant »
PC-A ----------------------------------------------------------------> Attaquant
 |                                                                         |
 | Paquets qui devraient aller à la passerelle                             |
 |                                                                         | Peut les relayer,
 |                                                                         | les modifier ou les bloquer
 +------------------------------ trafic détourné --------------------------+
```

Conséquences possibles :

- **Interception (man-in-the-middle)** : l’attaquant se place entre la victime et la passerelle, parfois en relayant le trafic.
- **Déni de service** : le trafic est envoyé vers une MAC qui ne le transmet pas correctement.
- **Altération ou observation du trafic** : l’impact concret dépend des protocoles applicatifs, du chiffrement et de la position obtenue.

### Détection et prévention

- Utiliser sur les commutateurs gérés les protections disponibles, notamment **Dynamic ARP Inspection (DAI)**, souvent associée à **DHCP snooping** et aux liaisons IP/MAC/port de confiance.
- Segmenter le réseau avec des VLAN et limiter qui peut rejoindre un même domaine de broadcast.
- Surveiller les changements inattendus d’association IP/MAC, les alertes IDS et les doublons d’IP.
- Réserver les entrées ARP statiques à des cas maîtrisés : cela peut aider dans de petits environnements, mais se déploie difficilement à grande échelle.
- Chiffrer les communications applicatives (par exemple TLS). Le chiffrement ne bloque pas le spoofing lui-même, mais réduit la possibilité de lire ou modifier le contenu sans détection.
- Contrôler les ports d’accès et appliquer les fonctions anti-usurpation disponibles sur les équipements.

## 6. À retenir

1. ARP résout une **adresse IPv4 en adresse MAC** sur un lien local IPv4.
2. La table de routage choisit le prochain saut ; ARP en recherche la MAC lorsqu’elle est nécessaire.
3. Pour une destination distante, l’hôte résout généralement la MAC de sa passerelle par défaut.
4. Le cache ARP accélère la communication mais une entrée erronée peut perturber le trafic.
5. Le Proxy ARP est une fonction intermédiaire légitime ; l’ARP spoofing est une usurpation.
6. En IPv6, ARP est remplacé par les mécanismes de **Neighbor Discovery (NDP)** sur ICMPv6.

## Références

- IETF, [RFC 826 — An Ethernet Address Resolution Protocol](https://www.rfc-editor.org/rfc/rfc826)
- Cisco, [Understand Proxy ARP](https://www.cisco.com/c/en/us/support/docs/ip/dynamic-address-allocation-resolution/13718-5.html)
- Cisco, [Preventing ARP Spoofing and Flood Attack](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst_pon/software/configuration_guide/sec/b-gpon-config-security/preventing_arf_spoofing_and_flood_attack.html)
