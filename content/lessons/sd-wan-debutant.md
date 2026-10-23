
# SD-WAN (Software-Defined Wide Area Network) - Débutant
**Niveau :** Débutant

Pendant plusieurs décennies, l'architecture des réseaux étendus d'entreprise (WAN) reposait quasi exclusivement sur des liaisons privées dédiées, principalement de type MPLS (Multiprotocol Label Switching). Ces architectures traditionnelles offraient une garantie de service optimale et une sécurité intrinsèque élevée, mais elles souffraient d'une rigidité extrême, de coûts financiers prohibitifs et d'une bande passante limitée. Dans ce modèle classique, l'intégralité du trafic réseau provenance des agences distantes était rapatriée vers un site central ou un Data Center via un mécanisme dit de *Backhauling* afin d'y subir des inspections de sécurité strictes avant d'accéder à Internet.

L'avènement massif du Cloud Computing, la migration des applications critiques vers des plateformes Software-as-a-Service (SaaS telles que Microsoft 365, Salesforce ou Google Workspace) et le déploiement d'infrastructures Infrastructure-as-a-Service (IaaS sur AWS, Azure ou GCP) ont profondément déstabilisé ce modèle historique. Rapatrier le trafic Cloud vers un Data Center central avant de le réacheminer vers Internet crée un goulot d'étranglement majeur, augmente la latence de manière inacceptable et dégrade considérablement l'expérience utilisateur. De plus, augmenter la capacité d'une liaison MPLS d'agence nécessite souvent des délais de livraison opérateur de plusieurs semaines, voire plusieurs mois, tout en pesant lourdement sur les budgets IT.

C'est pour répondre à cette mutation profonde des usages que la technologie **SD-WAN (Software-Defined Wide Area Network)** a été conçue. Le SD-WAN applique les principes fondamentaux du Software-Defined Networking (SDN) aux réseaux WAN. Il s'agit d'une architecture d'overlay virtuel qui fait abstraction des supports physiques de transport sous-jacents (MPLS, Internet Haut Débit/Fibre, 4G/5G, Satellite). Le SD-WAN permet aux entreprises de combiner plusieurs liaisons de transports héparpillées, d'allouer dynamiquement le trafic en fonction des exigences en temps réel des applications et d'effectuer des accès directs à Internet (*Direct Internet Access* - DIA) en toute sécurité depuis les agences distantes.

En centralisant l'administration et le contrôle des politiques réseau au sein de contrôleurs logiciels, le SD-WAN simplifie le déploiement des équipements d'agence grâce à l'automatisation Zero-Touch Provisioning (ZTP). L'intelligence n'est plus distribuée au cas par cas dans chaque routeur individuel via des configurations manuelles par ligne de commande, mais orchestrée de manière globale. Le réseau étendu devient ainsi agile, résilient, économique et intrinsèquement adapté aux exigences des environnements hybrides et Cloud modernes.

> **Analogie** : Imaginez un système de transport postal de marchandises reliant plusieurs villes. Dans le système WAN traditionnel (MPLS), vous disposez d'un unique chemin de fer privé. Il est extrêmement fiable, les trains y circulent de manière ponctuelle et la sécurité y est garantie, mais le coût de maintenance des rails est exorbitant et la construction d'une nouvelle voie prend des mois. Si un paquet doit être envoyé dans un autre pays (représentant le Cloud), il doit impérativement voyager par ce train jusqu'au centre de tri central (le Data Center), même si la ville de départ possède un port ou un aéroport à proximité.
>
> Le SD-WAN agit comme un **Gestionnaire de Flotte Intelligent et Automatisé**. Au lieu de vous limiter au seul chemin de fer privé, ce gestionnaire prend le contrôle de multiples réseaux de transport existants : l'autoroute publique (Internet BroadBand), les routes secondaires rapides (Fibre grand public) et les voies aériennes/mobiles (4G/5G).
>
> Chaque colis (paquet de données) est étiqueté selon sa priorité et son contenu. Un produit médical d'urgence (trafic VOIP/Visioconférence) sera expédié via la voie la plus rapide et la plus stable disponible à l'instant T. Un carton de fournitures de bureau (chargement de fichier de sauvegarde) sera envoyé par l'autoroute publique standard. Si un accident survient sur l'autoroute (perte de paquets ou montée de latence sur une liaison Internet), le gestionnaire redirige automatiquement et instantanément les camions suivants sur le chemin de fer ou la route secondaire, de manière totalement invisible pour les destinataires. De plus, si un colis est destiné à l'étranger, le gestionnaire autorise l'agence locale à utiliser l'aéroport le plus proche (Direct Internet Access) au lieu de faire le détour inutile par le centre de tri national.

---

## 1. La théorie et les algorithmes

Le fonctionnement fondamental du SD-WAN repose sur une architecture découplée, structurée en quatre plans distincts : le **Plan de Gestion (*Management Plane*)**, le **Plan de Contrôle (*Control Plane*)**, le **Plan de Données (*Data Plane*)** et le **Plan d'Orchestration (*Orchestration Plane*)**. Cette séparation est l'élément clé qui différencie le SD-WAN du routage traditionnel où tous ces plans cohabitent au sein de chaque routeur.

```text
+-----------------------------------------------------------------------+
|                       PLAN D'ORCHESTRATION                            |
|                            (vOrchestrator)                            |
|        - Authentification initiale et Zero-Touch Provisioning (ZTP)   |
+-----------------------------------┬-----------------------------------+
                                    |
                                    v
+-----------------------------------+-----------------------------------+
|                         PLAN DE GESTION                               |
|                             (vManage)                                 |
|        - Interface graphique centralisée, Politiques & Modèles        |
+-----------------------------------┬-----------------------------------+
                                    |
                                    v
+-----------------------------------+-----------------------------------+
|                         PLAN DE CONTRÔLE                              |
|                              (vSmart)                                 |
|        - Distribution des routes (OMP), Topologies & Sécurité         |
+-----------------------------------┬-----------------------------------+
                                    |
           =================================================
           Établissement des tunnels Overlay IPsec sécurisés
           =================================================
                                    |
                                    v
+-----------------------------------------------------------------------+
|                         PLAN DE DONNÉES                               |
|                           (vEdge / cEdge)                             |
|                                                                       |
|   [ WAN Transport 1: MPLS ]               [ WAN Transport 2: Internet ]
|               │                                       │               |
|               └───────────────► BFD ◄─────────────────┘               |
|                      (Mesure Jitter / Loss / Latency)                 |
+-----------------------------------------------------------------------+
```

### 1. Descriptif des Plans de l'Architecture SD-WAN (Exemple Cisco Catalyst SD-WAN)

1. **Plan d'Orchestration (vBond / vOrchestrator)** : C'est le point d'entrée unique de la fabrique SD-WAN. Il authentifie tous les équipements (contrôleurs et routeurs WAN d'agence) lors de leur démarrage. Il attribue les adresses IP nécessaires, valide les certificats de sécurité et facilite la mise en relation initiale entre les routeurs d'agence et les contrôleurs de gestion et de contrôle, même si l'équipement d'agence se trouve derrière un équipement NAT.
2. **Plan de Gestion (vManage / NMS)** : Il fournit une console centralisée à interface graphique (GUI) permettant aux administrateurs de concevoir, déployer et surveiller l'ensemble du réseau étendu. C'est à partir du vManage que sont définis les modèles de configuration (*Templates*) et les politiques globales de routage et de sécurité.
3. **Plan de Contrôle (vSmart)** : C'est le "cerveau" du réseau. Le contrôleur vSmart échange des informations de routage, de sécurité et de topologie avec tous les routeurs de la fabrique. Il utilise un protocole d'échange spécifique appelé **OMP (*Overlay Management Protocol*)**. Il applique les politiques centralisées (ex: forcer un trafic d'agence à passer par un Pare-Feu central) et distribue les clés de chiffrement IPsec aux équipements d'extrémité.
4. **Plan de Données (vEdge / cEdge / WAN Edge)** : Ce sont les équipements physiques ou virtuels situés dans les agences, les Data Centers ou les infrastructures Cloud. Ils sont responsables du transfert effectif des paquets d'utilisateurs. Ils montent dynamiquement des tunnels chiffrés **IPsec** ou **GRE** entre eux à travers les différents réseaux sous-jacents (*Underlay*).

### 2. Algorithmes de Mesure et Sélection Dynamique de Chemin (Application-Aware Routing)

Contrairement aux routeurs IP classiques qui orientent les paquets uniquement en fonction de l'adresse IP de destination (via la table de routage RIB/FIB), le SD-WAN utilise le routage applicatif orienté sur la qualité de service (*Application-Aware Routing* ou AAR).

Pour mesurer la qualité de chaque liaison WAN en temps réel, les équipements WAN Edge injectent des sondes du protocole **BFD (*Bidirectional Forwarding Detection*)** à l'intérieur de chaque tunnel IPsec. Ces paquets de sondage sont transmis à haute fréquence (par défaut toutes les secondes) et permettent de calculer continuellement trois métriques fondamentales :

* **La Latence (*Latency / RTT*)** : Le temps aller-retour nécessaire à un paquet pour traverser le tunnel.
* **La Gigue (*Jitter*)** : La variation de la latence au fil du temps (élément critique pour la voix et la vidéo).
* **La Perte de Paquets (*Packet Loss*)** : Le pourcentage de paquets de sonde non restitués sur une fenêtre glissante définie.

L'algorithme AAR évalue continuellement ces métriques par rapport aux exigences configurées dans les politiques du réseau. Par exemple, une politique "Voix sur IP" peut imposer les seuils maximaux suivants : *Latence $\le$ 150 ms, Gigue $\le$ 10 ms, Perte $\le$ 1%*.

$$
\text{Conformité Liaison} = (\text{Latence}_{\text{mesurée}} \le 150\text{ms}) \land (\text{Gigue}_{\text{mesurée}} \le 10\text{ms}) \land (\text{Perte}_{\text{mesurée}} \le 1\%)
$$

Si la liaison WAN primaire (ex: Internet Broadband) subit une dégradation temporaire et franchit l'un de ces seuils, l'algorithme AAR bascule instantanément le flux de voix vers la liaison secondaire (ex: MPLS), sans rompre la session de communication en cours et sans perte d'appel.

### 3. Construction des Paquets et Identification des Transports (Color TLOC)

Pour structurer le réseau logique (*Overlay*) au-dessus des circuits physiques (*Underlay*), le SD-WAN introduit le concept de **TLOC (*Transport Location*)**. Un TLOC est l'identifiant unique d'un point d'attachement réseau d'un routeur WAN Edge. Il est défini par un triplet :

$$\text{TLOC} = \{\text{System-IP}, \text{Color}, \text{Encapsulation}\}$$

* **System-IP** : Une adresse IP fixe à valeur d'identifiant (similaire à un Router-ID BGP/OSPF), indépendante de toute adresse IP d'interface.
* **Color** : Une étiquette réservée ou personnalisée (ex: `mpls`, `public-internet`, `4g`) qui identifie le type de transport physique utilisé. Les couleurs permettent d'empêcher, par exemple, un routeur de tenter de monter un tunnel IPsec entre une interface MPLS privée et une interface Internet publique non routable directement.
* **Encapsulation** : Le type d'encapsulation réseau utilisé, généralement `IPsec` ou `GRE`.

Lorsqu'un paquet utilisateur pénètre dans le WAN Edge d'une agence, l'équipement effectue une inspection approfondie (*Deep Packet Inspection* - DPI) au niveau 7 du modèle OSI pour identifier le type d'application (ex: Zoom, Facebook, Salesforce). Une fois l'application identifiée, le routeur consulte sa table AAR, sélectionne le TLOC de destination conforme aux SLAs applicatifs, encapsule le paquet d'origine dans un en-tête IPsec/ESP avec le marquage DSCP adéquat, et le transmet à travers le tunnel approprié.

> **Piège :** Lors d'un examen ou d'une première conception architecturale, une erreur fréquente consiste à confondre la **System-IP** d'un équipement SD-WAN avec une adresse IP d'interface routable. La System-IP sert uniquement d'identifiant logique (similaire à un numéro de sécurité sociale pour l'équipement). Elle ne doit **jamais** être utilisée comme adresse de sous-réseau physiquement attribuée à un lien WAN d'accès sous peine de casser l'établissement des adjacences OMP et le routage sous-jacent !

---

## 2. Configuration et Pratique

Dans les déploiements d'entreprise réels, la configuration SD-WAN est orchestrée de manière centralisée via l'interface graphique du vManage en utilisant des modèles appelés **Feature Templates** et **Device Templates**. Néanmoins, pour comprendre la mécanique interne, il est indispensable de maîtriser la structure de configuration en ligne de commande (CLI) sur un routeur SD-WAN moderne (Cisco cEdge tournant sous IOS-XE SD-WAN).

L'architecture logicielle divise l'équipement en espaces virtuels isolés appelés **VPNs** (équivalents aux VRF dans le monde traditionnel) :

* **VPN 0 (WAN/Transport Side)** : Réservé exclusivement aux interfaces connectées aux réseaux d'accès WAN (MPLS, Internet). C'est dans ce VPN que se montent les tunnels IPsec.
* **VPN 512 (Management Side)** : Réservé à la gestion hors-bande (*Out-of-Band Management*) de l'équipement.
* **VPN 1 à 511 / 513 à 65530 (Service Side)** : Dédiés au réseau local de l'entreprise (LAN agence, VLANs utilisateurs, serveurs, imprimantes).

La configuration ci-dessous illustre l'intégration complète d'un routeur d'agence d'extrémité (cEdge) disposant de deux accès WAN (un accès Internet direct et un accès MPLS) ainsi qu'un réseau local utilisateur.

```cisco
! =====================================================================
! SECTION 1 : CONFIGURATION DU SYSTEME ET DES PARAMETRES SD-WAN
! =====================================================================
system
 system-ip      172.16.255.11
 site-id        101
 organization-name "Enterprise-Global-SDWAN"
 vbond 192.168.1.100
!

! =====================================================================
! SECTION 2 : CONFIGURATION DU PROTOCOLE OMP (OVERLAY MANAGEMENT)
! =====================================================================
sdwan
 omp
  no shutdown
  graceful-restart
  advertise connected
  advertise static
 !

! =====================================================================
! SECTION 3 : TRANSPORT ET TUNNELS (VPN 0 - UNDERLAY & OVERLAY)
! =====================================================================
 ! --- Interface WAN 1 : Accès Internet Public ---
 interface GigabitEthernet1
  description *** Connexion Internet Haut Debit ***
  ip address 203.0.113.2 255.255.255.252
  tunnel-interface
   encapsulation ipsec
   color public-internet
   max-control-connections 2
  !
  exit
 !

 ! --- Interface WAN 2 : Accès MPLS Privé ---
 interface GigabitEthernet2
  description *** Liaison MPLS Operateur ***
  ip address 192.168.50.2 255.255.255.252
  tunnel-interface
   encapsulation ipsec
   color mpls
   max-control-connections 2
  !
  exit
 !

 ! --- Route par défaut pour l'accès Underlay Internet ---
 ip route 0.0.0.0 0.0.0.0 203.0.113.1
!

! =====================================================================
! SECTION 4 : RESEAU LOCAL ET SERVICES (VPN 10 - SERVICE LAN)
! =====================================================================
vrf definition 10
 rd 101:10
 address-family ipv4
  exit-address-family
!

interface GigabitEthernet3
 description *** LAN Agence Utilisateurs ***
 vrf forwarding 10
 ip address 10.101.10.1 255.255.255.0
 no shutdown
!

! =====================================================================
! SECTION 5 : POLITIQUE DE ROUTAGE APPLICATIF (AAR POLICY EXAMPLE)
! =====================================================================
policy
 SLA-class SLA_VOICE
  latency 150
  loss 1
  jitter 10
 !
 app-route-policy AAR_STRATEGY
  sequence 10
   match
    dscp 46
   !
   action
    sla-class SLA_VOICE preferred-color mpls public-internet
   !
  !
 !
!
```

> **Astuce :** Sur un routeur d'agence SD-WAN (cEdge IOS-XE), la commande de diagnostic la plus puissante pour vérifier immédiatement l'état d'établissement de la fabrique est `show sdwan control connections`. Elle permet de s'assurer en un coup d'œil que le routeur a établi ses sessions de contrôle sécurisées avec le vBond, le vManage et le vSmart sur toutes ses interfaces de transport (`color`).

---

## 3. Dépannage et Sécurité

### 1. Méthodologie et Diagnostics de Panne

Le dépannage d'une fabrique SD-WAN exige une approche rigoureuse qui suit la hiérarchie des plans (Underlay $\rightarrow$ Contrôle $\rightarrow$ Overlay). Lorsqu'une agence perd sa connectivité applicative, les ingénieurs doivent exécuter la séquence de validation suivante :

1. **Validation de l'Underlay (Niveau 1 à 3)** : Vérifier que l'interface physique est active et que le routeur d'agence peut joindre sa passerelle sous-jacente via des pings standards (`ping 203.0.113.1`).
2. **Validation des Connexions de Contrôle** : Inspecter si les sessions DTLS ou TLS entre le WAN Edge et les contrôleurs (vSmart/vManage) sont correctement établies :
   ```bash
   show sdwan control connections
   ```
   Si l'état affiche `CR_ERR` ou reste bloqué en `CONNECT`, vérifier la présence de règles de blocage de Pare-Feu intermédiaire sur les ports UDP réservés (`12346` ou port par défaut `12346-13150`).
3. **Validation du Protocole OMP** : Vérifier que le routeur reçoit bien les routes distribuées de manière centralisée par le contrôleur vSmart :
   ```bash
   show sdwan omp routes
   ```
4. **Validation de la Santé des Tunnels BFD** : Contrôler l'état des tunnels IPsec entre les agences et l'état des métriques de performance en temps réel :
   ```bash
   show sdwan bfd sessions
   ```

### 2. Sécurisation Native de l'Architecture SD-WAN

Le SD-WAN intègre une sécurité globale basée sur le principe du Zero-Trust et de la protection en profondeur :

* **Authentification Matérielle et Certificats** : Chaque équipement réseau physique embarque une puce matérielle sécurisée (**TPM 2.0** / *Anti-Counterfeit Chip*) dans laquelle est gravé un certificat unique fabricant (**SUDI** - *Secure Unique Device Identifier*). Aucun routeur non autorisé ne peut rejoindre la fabrique.
* **Chiffrement Authentifié du Data Plane** : Tout le trafic inter-sites traversant les tunnels d'Overlay est chiffré au moyen de l'algorithme hautement sécurisé **IPsec AES-256-GCM**.
* **Renouvellement Automatique des Clés IPsec** : Contrairement au VPN IKEv1/IKEv2 traditionnel où les négociations de clés de chiffrement génèrent une charge CPU considérable sur les routeurs lors des ré-authentifications, le contrôleur vSmart gère et distribue de manière centralisée les clés de chiffrement des équipements via le protocole OMP, éliminant tout impact sur les performances d'acheminement des paquets.
* **Sécurité Directe vers Internet (DIA / SASE)** : Pour protéger les agences utilisant le *Direct Internet Access* sans repasser par le Data Center, les routeurs WAN Edge modernes intègrent un Pare-Feu applicatif (NGFW), un système de prévention d'intrusions (IPS Snort), un filtrage d'URLs et une intégration directe avec des architectures de sécurité Cloud de type SASE (*Secure Access Service Edge* comme Cisco Umbrella ou Zscaler).

> **Danger :** N'activez jamais la fonctionnalité de *Direct Internet Access* (DIA) sur l'interface WAN d'une agence sans avoir préalablement appliqué une politique de sécurité rigoureuse (Pare-Feu d'inspection d'état et NAT) au sein du VPN 0 ou directement au niveau du point de sortie local. Autoriser un flux direct vers Internet sans filtrage applicatif expose le réseau local interne de l'agence directement aux menaces, scanners de vulnérabilités et cyberattaques en provenance du web.

---

## Points à retenir

- **Découplage des Plans** : Le SD-WAN sépare le réseau en 4 plans distincts (Orchestration/vBond, Gestion/vManage, Contrôle/vSmart, Données/WAN Edge), permettant une administration centralisée et automatisée de l'ensemble du réseau étendu.
- **Indépendance des Transports et TLOCs** : Le SD-WAN crée un réseau virtuel chiffré (*Overlay IPsec*) par-dessus n'importe quel réseau d'accès physique (*Underlay* de type MPLS, Internet, 4G/5G). Les liaisons sont identifiées de façon unique par des **TLOCs** définis par un triplet `(System-IP, Color, Encapsulation)`.
- **Routage Dynamique Applicatif (AAR)** : Grâce à des sondes **BFD** mesurant continuellement la latence, la gigue et la perte de paquets, le SD-WAN oriente automatiquement le trafic applicatif sensible sur la liaison la plus performante à l'instant T.
- **Isolation Logique par VPN** : Le réseau est partitionné en espaces virtuels étanches : le **VPN 0** pour le transport sous-jacent/WAN, le **VPN 512** pour le management, et les **VPNs de Service (1-511)** pour le réseau LAN d'entreprise.