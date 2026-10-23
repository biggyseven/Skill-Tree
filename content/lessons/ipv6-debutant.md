
# IPv6 (Internet Protocol version 6) - Débutant

**Niveau :** Débutant

Au début des années 1980, la conception du protocole IPv4 reposait sur un espace d'adressage codé sur 32 bits, permettant théoriquement de générer environ 4,29 milliards d'adresses uniques. À cette époque pionnière de l'ARPANET, cet espace semblait pratiquement inépuisable. Cependant, la démocratisation massive d'Internet dans les années 1990, associée au déploiement des équipements mobiles et des objets connectés, a conduit à une saturation inévitable du réservoir d'adresses IPv4. Des techniques palliatives temporaires, telles que le NAT (Network Address Translation) et le subnetting VLSM, ont permis de prolonger la durée de vie d'IPv4, mais au prix d'une dégradation de la connectivité bout-en-bout, de la complexité du routage et d'une surconsommation de ressources matérielles sur les équipements réseau.

Pour résoudre définitivement la pénurie d'adresses et moderniser l'architecture de couche 3 du modèle OSI, l'IETF (Internet Engineering Task Force) a formalisé le protocole IPv6 à travers la RFC 2460 (mise à jour ultérieurement par la RFC 8200). En étendant la taille des adresses de 32 bits à 128 bits, IPv6 n'offre pas seulement un espace d'adressage virtuellement illimité de $3.4 \times 10^{38}$ adresses, mais il repense également la structure de l'en-tête IP pour optimiser le traitement des paquets par les routeurs d'interconnexion.

Au-delà de la simple expansion de l'espace d'adressage, IPv6 intègre nativement des fonctionnalités autrefois optionnelles ou superposées en IPv4 : la suppression du besoin de NAT, la simplification du format d'en-tête pour un routage matériel accéléré, la configuration automatique des adresses sans état (SLAAC), ainsi qu'une gestion de la sécurité (IPsec) et de la mobilité pensée dès la conception du protocole. Comprendre les bases d'IPv6 est aujourd'hui indispensable pour concevoir des infrastructures réseau pérennes et alignées sur les standards des opérateurs télécoms modernes.

> **Analogie** : Imaginez que le système de numérotation téléphonique d'un pays soit basé sur un numéro à 4 chiffres (IPv4). Au début, cela suffit largement pour attribuer une ligne à chaque habitation. Mais lorsque chaque citoyen souhaite avoir son téléphone portable, sa montre connectée et sa voiture connectée, le système s'effondre. Pour contourner le problème, on installe des standards téléphoniques d'entreprise (NAT) où tout le monde partage le même numéro public et doit composer un numéro d'extension interne. IPv6 équivaut à remplacer les numéros à 4 chiffres par des combinaisons alphanumériques globales de 32 caractères : chaque objet sur Terre, de la simple ampoule connectée au supercalculateur, reçoit désormais un numéro direct, unique à l'échelle de la planète, éliminant totalement le besoin de standards d'extension intermédiaire.

---

## 1. La théorie et les algorithmes

### 1.1. Structure et représentation d'une adresse IPv6

Une adresse IPv6 est codée sur **128 bits** (soit 16 octets), généralement représentée sous forme de 8 groupes de 4 chiffres hexadécimaux (appelés *hextets* ou *mectets*), séparés par des deux-points (`:`).

Exemple de forme brute : `2001:0db8:0000:0000:0000:0000:1428:57ab`

Pour faciliter la lecture et la saisie, deux règles d'abréviation strictes sont appliquées :

1. **Omission des zéros en tête :** Dans chaque hextet, les zéros situés au début peuvent être supprimés.
   * `0db8` devient `db8`
   * `0000` devient `0`
2. **Compressions successives de zéros (`::`) :** Une séquence continue d'un ou plusieurs hextets nuls (`0000`) peut être remplacée par un double deux-points (`::`). Cette règle ne peut être appliquée **qu'une seule fois** par adresse pour éviter toute ambiguïté lors du décodage.

Forme optimisée : `2001:db8::1428:57ab`

### 1.2. Types d'adresses IPv6 et portées (Scopes)

Contrairement à IPv4, la notion de *Broadcast* n'existe plus en IPv6. Elle est entièrement remplacée par des mécanismes *Multicast* ciblés. Les types d'adresses principaux sont :

* **Global Unicast Address (GUA) :** Équivalent des adresses IPv4 publiques (`2000::/3`). Routables sur Internet.
* **Link-Local Address (LLA) :** Adresses préfixées par `fe80::/10`. Uniques et valides uniquement sur le segment de couche 2 local. Elles sont automatiquement générées sur chaque interface IPv6 et servent aux communications de voisinage (OSPFv3, NDP, next-hop).
* **Unique Local Address (ULA) :** Équivalent des adresses IPv4 privées RFC 1918 (`fc00::/7` ou `fd00::/7`). Routables en interne mais non sur Internet.
* **Multicast :** Préfixe `ff00::/8`. Utilisé pour joindre un groupe d'hôtes (ex: `ff02::1` pour tous les nœuds IPv6 du lien local, `ff02::2` pour tous les routeurs IPv6 du lien local).
* **Loopback :** `::1/128` (équivalent de `127.0.0.1`).

### 1.3. L'en-tête IPv6 et le protocole NDP (Neighbor Discovery Protocol)

L'en-tête fixe d'un paquet IPv6 est simplifié à **40 octets**, contre un en-tête de taille variable (20 à 60 octets) en IPv4. Cette taille fixe permet un alignement mémoire optimal et un traitement direct par les circuits ASICs des routeurs.

Les champs optionnels d'IPv4 ont été supprimés de l'en-tête de base et déportés dans des **en-têtes d'extension** (*Extension Headers*) insérés entre l'en-tête IPv6 et le segment de couche transport (TCP/UDP).

Le protocole **NDP (Neighbor Discovery Protocol)**, reposant sur **ICMPv6**, remplace le protocole ARP d'IPv4 et gère les fonctions essentielles :
* **Neighbor Solicitation (NS) / Neighbor Advertisement (NA) :** Résolution d'adresse IP vers adresse MAC (remplace ARP).
* **Router Solicitation (RS) / Router Advertisement (RA) :** Découverte dynamique de routeurs et autoconfiguration d'adresses sans état (**SLAAC**).

> **Piège :** Lors du calcul ou de la saisie d'adresses IPv6, n'utilisez **JAMAIS** la compression `::` deux fois dans la même adresse. Par exemple, l'adresse `2001::1::1` est invalide car il est impossible de déterminer la répartition exacte des blocs de zéros entre le premier et le second groupe.

```text
+-----------------------------------------------------------------------------------+
|                            STRUCTURE D'UN EN-TÊTE IPV6 (40 OCTETS)               |
+-----------------------------------------------------------------------------------+

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version| Traffic Class |           Flow Label                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Payload Length        |  Next Header  |   Hop Limit   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                                                               +
|                                                               |
+                         Source Address                        +
|                           (128 bits)                          |
+                                                               +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                                                               +
|                                                               |
+                      Destination Address                      +
|                           (128 bits)                          |
+                                                               +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

+-----------------------------------------------------------------------------------+
|               DÉCOUPAGE D'UNE ADRESSE GLOBAL UNICAST (GUA)                        |
+-----------------------------------------------------------------------------------+

 0                      48                  64                            128 bits
+-----------------------+-------------------+-------------------------------+
| Global Routing Prefix |     Subnet ID     |         Interface ID          |
+-----------------------+-------------------+-------------------------------+
|<----- 48 bits ------->|<---- 16 bits ---->|<----------- 64 bits --------->|
   Fourni par le FAI     Identifiant Sous-    Généré via EUI-64 ou Aléatoire
                         Réseau d'Entreprise
```

---

## 2. Configuration et Pratique

Pour déployer IPv6 sur un routeur Cisco IOS, le routage Unicast IPv6 doit d'abord être activé globalement, car il est généralement désactivé par défaut.

### Configuration complète sur un Routeur Cisco IOS

```cisco
! Activation globale du routage IPv6
ipv6 unicast-routing

! Configuration de l'interface WAN vers le FAI
interface GigabitEthernet0/0
 description WAN_LINK
 ! Attribution d'une adresse Global Unicast (GUA)
 ipv6 address 2001:db8:1000:1::2/64
 ! Définition manuelle optionnelle d'une adresse Link-Local explicite
 ipv6 address fe80::1:1 link-local
 no shutdown
exit

! Configuration de l'interface LAN avec auto-configuration SLAAC pour les clients
interface GigabitEthernet0/1
 description LAN_CLIENTS
 ipv6 address 2001:db8:2000:10::1/64
 ! Activation de l'émission des annonces de routeur (Router Advertisements)
 no ipv6 nd ra suppress
 no shutdown
exit

! Configuration d'une route statique IPv6 par défaut (Default Route)
ipv6 route ::/0 GigabitEthernet0/0 2001:db8:1000:1::1
```

> **Astuce :** Utilisez la commande `show ipv6 interface brief` pour visualiser rapidement l'état des interfaces, leurs adresses Global Unicast et leurs adresses Link-Local associées.

---

## 3. Dépannage et Sécurité

### 3.1. Diagnostic des pannes courantes

Lors du déploiement ou du dépannage d'un réseau IPv6, vérifiez les éléments suivants :

1. **Oubli de la commande globale :** Si la commande `ipv6 unicast-routing` n'est pas saisie, le routeur ne transfèrera pas les paquets IPv6 entre ses interfaces et ne répondra pas aux requêtes de routage.
2. **Problème de masque de préfixe (`/64`) :** La majorité des fonctionnalités IPv6 (notamment SLAAC) nécessitent strictement un masque de préfixe `/64` sur le segment LAN.
3. **Blocage des paquets ICMPv6 :** Contrairement à IPv4 où l'on pouvait parfois bloquer ICMP sans impacter directement l'adressage, le blocage d'ICMPv6 casse le protocole NDP (résolution d'adresses MAC, détection de doublons DAD, autoconfiguration).

Commandes de vérification :
* `show ipv6 neighbors` : Équivalent de `show ip arp` en IPv4, permet d'afficher la table de correspondance d'adresses IPv6 vers adresses MAC.
* `ping ipv6 [adresse]` : Test de connectivité ICMPv6.
* `traceroute ipv6 [adresse]` : Analyse du cheminement des paquets IPv6.

### 3.2. Sécurisation du protocole IPv6

L'absence de filtrage peut exposer le réseau local à des attaques spécifiques à IPv6 :

* **Rogue RA (Rogue Router Advertisements) :** Un équipement malveillant ou mal configuré émet des paquets ICMPv6 Router Advertisement pour se proclamer passerelle par défaut du sous-réseau.
* **Mitigation :** Activer la fonctionnalité **RA Guard** sur les commutateurs de couche 2 pour bloquer les messages RA provenant de ports non autorisés.

```cisco
! Exemple d'activation élémentaire du filtrage de trafic IPv6 via une Access List
ipv6 access-list SECURE_LAN_IN
 permit icmp any any neighbor-advertisement
 permit icmp any any neighbor-solicitation
 permit icmp any any router-advertisement
 deny ipv6 any any
exit

interface GigabitEthernet0/1
 ipv6 traffic-filter SECURE_LAN_IN in
exit
```

> **Danger :** Ne filtrez jamais aveuglément tout le trafic ICMPv6 avec une règle `deny icmp any any`. Un tel filtrage empêchera la résolution MAC via NDP, détruira le mécanisme DAD (Duplicate Address Detection) et causera une coupure totale des communications sur le lien local.

---

## Points à retenir

- **Espace d'adressage et codage :** IPv6 utilise des adresses sur **128 bits** écrites en hexadécimal. L'abréviation autorise la suppression des zéros en tête et l'utilisation unique de `::` pour comprimer une suite de blocs nuls.
- **Protocole NDP et ICMPv6 :** NDP remplace le protocole ARP d'IPv4. Il gère la résolution d'adresses, la détection d'adresses dupliquées (DAD) et la configuration dynamique via SLAAC grâce aux paquets ICMPv6.
- **Rôle critique de Link-Local (`fe80::/10`) :** Les adresses Link-Local sont générées automatiquement sur chaque interface active et sont indispensables aux communications de voisinage et aux protocoles de routage sur le segment de couche 2.