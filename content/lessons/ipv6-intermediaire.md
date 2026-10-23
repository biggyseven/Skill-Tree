# IPv6 (Internet Protocol version 6) - Intermédiaire

**Niveau :** Intermédiaire

Dans la transition globale des architectures de communication, la maîtrise simple du format d'adresse IPv6 ne suffit plus à répondre aux exigences des réseaux d'entreprise complexes. Lorsque les infrastructures croissent, les ingénieurs réseau doivent faire face à des problématiques d'allocation dynamique d'adresses à grande échelle, de routage dynamique interne (IGP) inter-sites, et d'interopérabilité fluide avec les systèmes patrimoniaux IPv4. L'adoption progressive d'IPv6 impose une compréhension fine des mécanismes d'interaction de couche 3 et de l'intégration des protocoles de contrôle.

Historiquement, le passage de la simple théorie IPv6 au déploiement opérationnel a révélé la nécessité de standardiser des architectures d'adressage hiérarchiques et des protocoles de découverte automatique évolués. Des spécifications majeures telles que la RFC 4861 pour Neighbor Discovery (NDP), la RFC 4862 pour Stateless Address Autoconfiguration (SLAAC), et les évolutions des protocoles de routage à état de liens comme OSPFv3 (RFC 5340) constituent la colonne vertébrale des réseaux IPv6 d'entreprise contemporains.

Ce niveau intermédiaire explore les mécanismes internes du protocole NDP, l'allocation dynamique avancée via DHCPv6 (Stateless et Stateful), le fonctionnement d'OSPFv3 multi-aires, ainsi que les stratégies de transition indispensables à la coexistence temporaire des piles d'adresses IPv4 et IPv6.

> **Analogie** : Imaginez un grand complexe hôtelier international. Dans une petite auberge (niveau débutant), chaque client choisit librement sa clé et sa chambre sur un tableau fixe. Dans cet hôtel de luxe (niveau intermédiaire), dès qu'un client arrive à l'accueil, l'hôtel lui délivre automatiquement une carte d'accès personnalisée (SLAAC). Si le client a besoin d'options spécifiques comme un coffre-fort ou le Wi-Fi VIP, un majordome dédié (DHCPv6) intervient pour lui fournir ces informations complémentaires sans changer sa chambre. Pour permettre aux employés de naviguer rapidement entre les différents bâtiments et étages sans se perdre, un réseau d'interphones ultra-rapide et sectorisé par zones (OSPFv3) met à jour les trajets optimaux en temps réel. Enfin, pour communiquer avec les anciens fournisseurs qui ne parlent que l'ancienne langue de l'hôtel, des traducteurs assermentés (mécanismes de transition Dual-Stack/Tunnels) traduisent instantanément les requêtes au comptoir.

## 1. La théorie et les algorithmes

### 1.1. Auto-configuration SLAAC et Génération d'Interface ID

La configuration automatique d'adresses sans état (**SLAAC - Stateless Address Autoconfiguration**) permet à un hôte de générer sa propre adresse Global Unicast (GUA) ou Unique Local (ULA) sans l'intervention d'un serveur DHCPv6.

Le processus SLAAC se déroule en plusieurs étapes algorithmiques :

1. **Génération d'une adresse Link-Local (`fe80::/10`) :** L'interface génère un identifiant d'interface de 64 bits (Interface ID) soit via la méthode historique **EUI-64** (basée sur l'adresse MAC), soit via des identifiants aléatoires temporaires/privés (RFC 4941).

2. **Détection d'Adresse Dupliquée (DAD - Duplicate Address Detection) :** L'hôte envoie un message ICMPv6 *Neighbor Solicitation* (Type 135) vers l'adresse Multicast de nœud sollicité (*Solicited-Node Multicast Address*) correspondant à l'adresse qu'il souhaite utiliser. Si aucun message *Neighbor Advertisement* (Type 136) n'est reçu en réponse, l'adresse est validée.

3. **Découverte de Routeur (Router Discovery) :** L'hôte émet un message ICMPv6 *Router Solicitation* (RS - Type 133) à destination du groupe multicast de tous les routeurs (`ff02::2`).

4. **Réception du Router Advertisement (RA - Type 134) :** Le routeur local répond en multicast (`ff02::1`) en fournissant :

   * Le préfixe réseau IPv6 (ex: `2001:db8:1000:1::/64`).

   * Les drapeaux de configuration (**M-Flag** pour Managed Address Configuration, **O-Flag** pour Other Configuration).

   * La durée de vie valide et préférée du préfixe.

5. **Combinaison :** L'hôte concatène le préfixe `/64` reçu du RA avec son Interface ID de 64 bits pour former son adresse routable.

#### Algorithme de conversion EUI-64

Pour convertir une adresse MAC 48 bits (ex: `00:1A:2B:3C:4D:5E`) en Interface ID 64 bits :

* Séparer la MAC en deux blocs de 24 bits : `00:1A:2B` et `3C:4D:5E`.

* Insérer les octets hexadécimaux `FF:FE` au milieu : `00:1A:2B:FF:FE:3C:4D:5E`.

* Inverser le 7ᵉ bit du premier octet (bit U/L - Universal/Local) : `00` (`00000000` binaire) devient `02` (`00000010` binaire).

* **Interface ID EUI-64 :** `021a:2bff:fe3c:4d5e`.

### 1.2. Interraction avec DHCPv6 (Stateless vs Stateful)

Le comportement des clients IPv6 dépend directement des drapeaux **M** et **O** transportés dans les messages ICMPv6 RA du routeur :

| **Mode** | **Drapeau M (Managed)** | **Drapeau O (Other)** | **Description** | 
| **SLAAC Pur** | 0 | 0 | L'hôte obtient son adresse IP et sa passerelle via RA. Pas de serveur DHCPv6. | 
| **DHCPv6 Stateless** | 0 | 1 | L'hôte génère son adresse IP via SLAAC, mais interroge un serveur DHCPv6 pour obtenir des options annexes (DNS, nom de domaine). | 
| **DHCPv6 Stateful** | 1 | 0 ou 1 | L'hôte ignore le préfixe du RA pour l'adressage et demande une adresse IP + options à un serveur DHCPv6 centralisé (similaire à IPv4). | 

### 1.3. Routage dynamique IPv6 avec OSPFv3

OSPFv3 (RFC 5340) est la réécriture d'OSPFv2 pour supporter nativement IPv6.

Principales différences architecturales :

* **Prise en charge du protocole :** OSPFv3 s'exécute **par lien** (*per-link*) et non plus par sous-réseau (*per-subnet*). Deux interfaces sur un même segment physique peuvent communiquer même si leurs adresses Unicast appartiennent à des sous-réseaux différents.

* **Adjacences sur Link-Local :** Les paquets d'adjacence OSPFv3 (Hello, DBD, LSR, LSU, LSAck) et les adresses de Next-Hop utilisent exclusivement les adresses **Link-Local (`fe80::/10`)**.

* **Nouveaux types de LSA :**

  * *Link LSA (Type 8) :* Informe les voisins du lien local de l'adresse Link-Local de l'interface et des adresses IPv6 associées.

  * *Intra-Area-Prefix LSA (Type 9) :* Transporte les préfixes IPv6 associés aux liens (séparation de la topologie pure et des informations de préfixes).

> **Piège :** En OSPFv3, bien que le protocole route des préfixes IPv6, l'identifiant du routeur (**Router-ID**) reste obligatoirement une valeur au format **IPv4 32-bit** (ex: `1.1.1.1`). Si aucun Router-ID 32-bit n'est configuré manuellement et qu'aucune adresse IPv4 n'est présente sur le routeur, le processus OSPFv3 ne pourra pas démarrer.

```
+-----------------------------------------------------------------------------------+
|                        PROCESSUS D'AUTOCONFIGURATION SLAAC + DAD                  |
+-----------------------------------------------------------------------------------+

   Client IPv6 (Hôte)                                        Routeur IPv6
        |                                                          |
        |--- 1. Génération LLA (fe80::21a:2bff:fe3c:4d5e) -------->|
        |                                                          |
        |--- 2. ICMPv6 NS (DAD) ---------------------------------->| (Multicast Sollicité)
        |    (Vérification d'unicité de la Link-Local sur le L2)   |
        |<-- [Pas de réponse NA -> Adresse LLA validée] -----------|
        |                                                          |
        |--- 3. ICMPv6 Router Solicitation (RS) ------------------>| (ff02::2 - Routers)
        |                                                          |
        |<-- 4. ICMPv6 Router Advertisement (RA) ------------------| (ff02::1 - All Nodes)
        |    (Préfixe: 2001:db8:1::/64, M-flag=0, O-flag=1)        |
        |                                                          |
        |--- 5. Combinaison Préfixe + Interface ID ----------------|
        |    => GUA: 2001:db8:1::21a:2bff:fe3c:4d5e/64              |
        |                                                          |
        |--- 6. Request DHCPv6 Information-Request --------------->| (ff02::1:2 - DHCP Servers)
        |<-- 7. Response DHCPv6 Reply (DNS: 2001:db8::53) ---------|

+-----------------------------------------------------------------------------------+
|                           TOPOLOGIE OSPFV3 MULTI-AIRES                            |
+-----------------------------------------------------------------------------------+

            [ Aire 1 ]                     [ Aire 0 (Backbone) ]
  
     +---------------------+               +---------------------+
     |      Routeur R1     |               |      Routeur R2     |
     | Router-ID: 1.1.1.1  |---------------| Router-ID: 2.2.2.2  |
     +---------------------+               +---------------------+
     Eth0/0: 2001:db8:1::1/64              Eth0/0: 2001:db8:12::2/64
     LLA: fe80::1                          Eth0/1: 2001:db8:23::2/64
                                           LLA: fe80::2

```

## 2. Configuration et Pratique

Voici la configuration complète d'un routeur Cisco IOS jouant le rôle de routeur OSPFv3 multi-aires, serveur DHCPv6 Stateless, et émetteur de Router Advertisements configurés sur mesure.

### Configuration complète Cisco IOS

```
! Activation du routage IPv6 Unicast
ipv6 unicast-routing
ipv6 cef

! Configuration d'un pool DHCPv6 Stateless pour fournir le serveur DNS
ipv6 dhcp pool STATELESS-DHCP-POOL
 dns-server 2001:db8:ffff::53
 domain-name entreprise.local
exit

! Configuration du processus OSPFv3 avec un Router-ID 32-bit obligatoire
router ospfv3 100
 router-id 2.2.2.2
 auto-cost reference-bandwidth 100000
exit

! --- Interface LAN (Aire 1) ---
interface GigabitEthernet0/0
 description LAN_AIRE_1
 ip address unnumbered Loopback0 ! Désactivation optionnelle d'IPv4
 ipv6 enable
 ipv6 address fe80::2 link-local
 ipv6 address 2001:db8:1::1/64
 
 ! Association du pool DHCPv6 à l'interface
 ipv6 dhcp server STATELESS-DHCP-POOL
 
 ! Configuration des flags RA : M=0 (SLAAC) et O=1 (Stateless DHCPv6)
 no ipv6 nd managed-config-flag
 ipv6 nd other-config-flag
 
 ! Ajustement des intervalles RA (Optionnel)
 ipv6 nd ra interval 10 3
 
 ! Activation d'OSPFv3 directement sur l'interface dans l'Aire 1
 ospfv3 100 ipv6 area 1
 no shutdown
exit

! --- Interface WAN / Interconnexion Backbone (Aire 0) ---
interface GigabitEthernet0/1
 description WAN_BACKBONE_AIRE_0
 ipv6 enable
 ipv6 address fe80::2 link-local
 ipv6 address 2001:db8:12::2/64
 
 ! Configuration des coûts OSPFv3
 ospfv3 cost 10
 
 ! Activation d'OSPFv3 dans l'Aire 0 (Backbone)
 ospfv3 100 ipv6 area 0
 no shutdown
exit

! Interface Loopback pour la stabilité du Router-ID et tests
interface Loopback0
 ip address 10.2.2.2 255.255.255.255
 ipv6 address 2001:db8:99::2/128
 ospfv3 100 ipv6 area 0
exit

```

> **Astuce :** Pour vérifier la topologie OSPFv3 et s'assurer que les adjacences s'établissent bien au-dessus des adresses Link-Local, utilisez la commande `show ospfv3 neighbor`. Si l'adjacence reste bloquée en état `INIT` ou `EXSTART`, vérifiez la présence de filtres de paquets ICMPv6 ou un conflit de Router-ID.

## 3. Dépannage et Sécurité

### 3.1. Diagnostic des pannes courantes

1. **Mismatches des drapeaux RA / DHCPv6 :** Si les hôtes ne reçoivent pas d'adresses DNS ou tentent d'obtenir une adresse via DHCPv6 alors aucun serveur n'est présent, contrôlez le paramétrage des flags `managed-config-flag` et `other-config-flag` sur l'interface du routeur.

2. **Problème d'adjacence OSPFv3 :**

   * Verifiez que l'adresse **Link-Local** est bien configurée et unique sur le lien.

   * Assurez-vous que les MTU IPv6 matchent sur les deux interfaces distantes. Un écart de MTU bloque l'échange des paquets DBD OSPFv3.

   * Commande de vérification de la MTU : `show ipv6 interface GigabitEthernet0/1`.

Commandes clés de diagnostic :

* `show ipv6 ospf neighbor` ou `show ospfv3 neighbor`

* `show ipv6 route ospf`

* `show ipv6 dhcp binding` (pour le mode Stateful)

* `debug ipv6 nd` (pour observer les émissions/réceptions des paquets RA/RS/NS/NA)

### 3.2. Sécurisation avancée et risques majeurs

* **Rogue DHCPv6 Server / RA Spoofing :** Un hôte illégitime émet des réponses DHCPv6 ou des messages RA falsifiés pour rediriger le trafic vers lui (Man-In-The-Middle).

* **Mitigation :**

  * Activer **IPv6 RA Guard** sur les commutateurs d'accès :

    ```
    ipv6 nd inspection policy RA_POLICY
     device-role host
    exit
    
    interface GigabitEthernet0/10
     ipv6 nd inspection attach-policy RA_POLICY
    exit
    
    ```

  * Activer **DHCPv6 Snooping** pour bloquer les messages de serveurs DHCPv6 non autorisés.

> **Danger :** En environnement Dual-Stack (IPv4/IPv6), si vous sécurisez uniquement le protocole IPv4 (ex: DHCP Snooping, Dynamic ARP Inspection) sans déployer les contre-mesures IPv6 (RA Guard, IPv6 First Hop Security), un attaquant peut exploiter l'autoconfiguration IPv6 pour détourner l'ensemble du trafic du réseau local à l'insu de l'administrateur, même si le réseau était pensé pour être "IPv4 uniquement".

## Points à retenir

* **SLAAC et DAD :** SLAAC permet l'autoconfiguration sans état en combinant un préfixe `/64` reçu via Router Advertisement (RA) et un Interface ID (EUI-64 ou aléatoire). La détection d'adresse dupliquée (DAD) est systématique avant toute attribution d'adresse.

* **OSPFv3 vs OSPFv2 :** OSPFv3 s'exécute par lien (*per-link*), s'appuie sur les adresses Link-Local (`fe80::/10`) pour établir ses adjacences et échanger ses paquets, mais exige un Router-ID au format 32-bit.

* **Sécurisation du Premier Saut (FHS) :** L'activation d'IPv6 sur un segment de couche 2 requiert impérativement le déploiement de **RA Guard** et de **DHCPv6 Snooping** pour prévenir les attaques de détournement de trafic.

```

Le cours complet **IPv6 - Niveau Intermédiaire** a été généré et sauvegardé dans le fichier `ipv6-intermediaire.md`.

```