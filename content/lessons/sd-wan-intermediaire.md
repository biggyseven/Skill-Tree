# SD-WAN (Software-Defined Wide Area Network) - Intermédiaire

**Niveau :** Intermédiaire  
**Prérequis :** SD-WAN Débutant (`sd-wan-debutant`)

Dans le cours d'introduction (*SD-WAN Débutant*), nous avons abordé la séparation fondamentale des quatre plans (Orchestration, Gestion, Contrôle, Données) et le concept d'Overlay IPsec orchestré dynamiquement par rapport aux réseaux physiques sous-jacents (*Underlay*). 

Pour maîtriser le SD-WAN dans un contexte d'ingénierie et de déploiement d'entreprise, il est nécessaire de dépasser la vision macroscopique et d'analyser en profondeur les mécanismes internes d'échange d'informations de routage et de politique. Le passage au niveau intermédiaire nécessite de comprendre comment les contrôleurs **vSmart** manipulent la topologie réseau en temps réel via le protocole **OMP (Overlay Management Protocol)**, comment la notion de **TLOC (Transport Location)** façonne les chemins de données, et comment mettre en œuvre des politiques de routage complexes ou d'accès direct au Cloud (*Direct Internet Access / SASE*).

---

## 1. La théorie et les algorithmes avancés

### 1. Protocole OMP (Overlay Management Protocol)

**OMP** est le protocole de contrôle propriétaire (développé initialement par Viptela et intégré par Cisco) qui fonctionne exclusivement entre les routeurs WAN Edge et les contrôleurs vSmart, ainsi qu'entre les contrôleurs vSmart eux-mêmes. Il est souvent comparé à BGP pour sa capacité à transporter une grande variété d'attributs et de métadonnées, mais il est spécialement conçu pour les architectures Overlay SDN.

Contrairement aux protocoles de routage traditionnels (OSPF, EIGRP, BGP), OMP ne crée pas de maillage d'adjacences de routage directement entre les routeurs d'agence. Tous les routeurs WAN Edge établissent une session de contrôle chiffrée (DTLS ou TLS) uniquement avec les contrôleurs **vSmart**. 

```
┌──────────────┐                  ┌──────────────┐
│  WAN Edge A  │◄─── Session ────►│   vSmart     │
│   (Site 10)  │      OMP         │ (Control)    │
└──────────────┘                  └──────┬───────┘
       │                                 │
       │ IPsec                           │ Session
       │ Data Plane                      │ OMP
       ▼                                 ▼
┌──────────────┐                  ┌──────────────┐
│  WAN Edge B  │◄─────────────────┤  WAN Edge C  │
│   (Site 20)  │   IPsec Overlay  │   (Site 30)  │
└──────────────┘                  └──────────────┘
```

OMP échange trois types fondamentaux d'informations (appellent *Routes OMP*) :

1. **Routes OMP (Service Routes / IP Routes)** : Routes apprises par le routeur WAN Edge du côté de son réseau local (Service Side / VPNs LAN via BGP, OSPF, statique ou connecté). Elles sont redistribuées au vSmart.
2. **Routes TLOC (Transport Location Routes)** : Informations sur les points de terminaison des tunnels WAN (adresse IP publique/privée, couleur, type de chiffrement, clé publique d'échange).
3. **Routes de Service (Service Routes)** : Déclarations de services réseau disponibles sur un site spécifique (ex: Pare-Feu, Sondes IPS, Proxy) pour permettre l'insertion dynamique de services (*Service Chaining*).

#### Attributs clés d'une route OMP :
* `TLOC` : Le pointeur de saut suivant (*Next-Hop*) associé à la route.
* `Originator ID` : L'adresse `System-IP` du routeur qui a injecté la route.
* `Preference` : Valeur numérique utilisée pour préférer une route OMP par rapport à une autre.
* `Tag` : Étiquette personnalisée permettant de filtrer ou marquer les routes dans les politiques.
* `Metric` : Métrique attribuée à la route.

### 2. Le concept TLOC et l'Anatomie d'une connexion de données

Comme étudié au niveau débutant, un **TLOC** est le point d'attachement d'un routeur à un transport WAN. Formellement, un TLOC est défini par :

$$
\text{TLOC} = \{\text{System-IP}, \text{Color}, \text{Encapsulation}\}
$$

Pour que deux routeurs WAN Edge puissent monter un tunnel IPsec direct entre eux (en mode *Full-Mesh* ou *Hub-and-Spoke*), ils doivent échanger leurs routes TLOC via le contrôleur vSmart. 

#### Structure d'une mise à jour TLOC :
Lorsqu'un WAN Edge démarre et active une interface WAN (ex: GigabitEthernet1 en `public-internet`), il génère une route TLOC contenant :
* Sa **Public IP & Port** (obtenus/détectés via le vBond / STUN si derrière un NAT).
* Sa **Private IP & Port** (l'adresse locale attribuée à l'interface physiquement).
* La **Color** (`public-internet`).
* La **Clé de chiffrement IPsec** (Encryption Encryption Key/SPI).

Le vSmart reçoit cette route TLOC et la réémet vers les autres WAN Edges autorisés par la politique réseau. Dès réception, le WAN Edge distant initie directement la négociation IPsec vers l'adresse du TLOC sans intervention ultérieure du vSmart.

### 3. Contrôle de Topologie : Évolution du Full-Mesh au Hub-and-Spoke

Par défaut, si aucune politique centralisée n'est appliquée sur le vSmart, la fabrique SD-WAN se comporte en mode **Full-Mesh** : tous les sites distants créent des tunnels IPsec avec tous les autres sites distants.

Pour réduire le nombre de tunnels IPsec (qui croît de manière quadratique $N(N-1)/2$ avec le nombre de sites $N$), le vSmart peut appliquer une **Control Policy** centralisée afin d'altérer la réécriture des TLOCs et forcer une architecture **Hub-and-Spoke** ou **Partial-Mesh**.

```
    [ Spoke Site 10 ]                  [ Spoke Site 20 ]
            │                                  │
            └───────────────┐  ┌───────────────┘
                            ▼  ▼
                     [ Data Center Hub ]
                         (Site 100)
```

En interceptant les routes OMP envoyées par le *Spoke Site 10*, le vSmart modifie le `TLOC` de saut suivant pour le remplacer par le `TLOC` du *Data Center Hub*. Ainsi, tout le trafic entre le *Site 10* et le *Site 20* sera automatiquement acheminé via le Data Center.

---

## 2. Architecture des Politiques SD-WAN

Dans Cisco Catalyst SD-WAN, les politiques (*Policies*) constituent le cœur du contrôle d'un réseau étendu. Elles se divisent en deux grandes catégories : **Centralized Policies** (exécutées sur le vSmart) et **Localized Policies** (exécutées directement sur les WAN Edges).

```
                             POLITIQUES SD-WAN
                                     │
           ┌─────────────────────────┴─────────────────────────┐
           ▼                                                   ▼
  Centralized Policies                                Localized Policies
  (Evaluées sur vSmart)                              (Evaluées sur WAN Edge)
   ├── Control Policy (OMP / Topologie)               ├── Route-Policy (BGP/OSPF local)
   └── Data Policy (AAR / Service Chaining)           └── QoS & ACLs (Class-Map, Shaping)
```

### 1. Centralized Policies (Politiques Centralisées)
Rédigées sur le vManage et poussées vers le **vSmart** :
* **Centralized Control Policy** : Agit sur le protocole OMP. Elle permet de modifier la topologie réseau (Hub-and-Spoke, région-per-région), de manipuler la distribution des routes OMP et de modifier les attributs des TLOCs.
* **Centralized Data Policy** : Agit sur le Plan de Données (trafic utilisateur). Elle gère le routage applicatif (**Application-Aware Routing - AAR**), l'isolation de flux, le pèlerinage vers un pare-feu (*Service Chaining*) et le bypass de sécurité.

### 2. Localized Policies (Politiques Localisées)
Appliquées directement sur la configuration d'un **WAN Edge** spécifique :
* **Localized Control Policy** : Agit sur les protocoles de routage locaux (OSPF, BGP) du côté LAN (*Service Side*) pour filtrer ou redistribuer les routes transmises entre le LAN de l'agence et le protocole OMP.
* **Localized Data Policy (QoS / ACLs)** : Applique le marquage DSCP, le façonnage du trafic (*Shaping*), la mise en file d'attente prioritaire (*Policing / Queueing*) et les Access Control Lists classiques d'interface.

---

## 3. Configuration et Cas Pratique Advanced

Dans cet exercice pratique, nous allons configurer sur le **vSmart** une politique de contrôle centralisée (*Control Policy*) pour transformer une topologie par défaut en **Hub-and-Spoke**, puis nous configurerons sur un routeur **cEdge** la fonctionnalité de **Direct Internet Access (DIA)** avec NAT d'agence.

### 1. Configuration Centralisée sur le vSmart (Control Policy : Hub-and-Spoke)

La politique ci-dessous demande au vSmart de filtrer la distribution des routes TLOC vers les agences (*Spokes*) afin qu'elles n'apprennent que le TLOC du Data Center (*Hub*).

```text
! =====================================================================
! POLITIQUE CENTRALISEE VSMART : TOPOLOGIE HUB-AND-SPOKE
! =====================================================================

policy
 ! --- Définition des listes de sites et TLOCs ---
 site-list HUBS
  site-id 100
 !
 site-list SPOKES
  site-id 10-99
 !
 tloc-list HUB-TLOCS
  tloc 172.16.255.100 color mpls encap ipsec
  tloc 172.16.255.100 color public-internet encap ipsec
 !

 ! --- Définition de la Control Policy ---
 control-policy HUB_AND_SPOKE_TOPOLOGY
  sequence 10
   match route
    site-list SPOKES
   !
   action accept
    ! Forcer le Next-Hop TLOC vers les Hubs pour tous les Spokes
    set tloc-list HUB-TLOCS
   !
  !
  default-action accept
 !
!

! --- Application de la politique OMP vers les Spokes ---
apply-policy
 site-list SPOKES
  control-policy HUB_AND_SPOKE_TOPOLOGY out
 !
!
```

### 2. Configuration du Direct Internet Access (DIA) sur un WAN Edge (cEdge)

Pour permettre à une agence d'accéder directement aux services Cloud (Microsoft 365, Google Workspace) via son accès Internet local (VPN 0) sans repasser par le Data Center, nous configurons le NAT de sortie dans le VPN 0 et nous injectons une route par défaut dans le VPN Utilisateur (VPN 10).

```text
! =====================================================================
! CONFIGURATION CEDGE : DIRECT INTERNET ACCESS (DIA) AVEC NAT LOCAL
! =====================================================================

! ---------------------------------------------------------------------
! STEP 1 : Activation du NAT Overload dans le VPN 0 (Transport WAN)
! ---------------------------------------------------------------------
interface GigabitEthernet1
 description *** Lien Internet avec NAT d'Agence (DIA) ***
 ip address 203.0.113.2 255.255.255.252
 tunnel-interface
  encapsulation ipsec
  color public-internet
  allow-service dhcp
  allow-service dns
  allow-service icmp
 !
 ! Activation de la fonctionnalité NAT sur l'interface WAN
 ip nat outside
!

ip nat inside source list DIA_NAT_ACL interface GigabitEthernet1 overload

ip access-list extended DIA_NAT_ACL
 permit ip 10.101.10.0 0.0.0.255 any
!

! ---------------------------------------------------------------------
! STEP 2 : Injection de la route par défaut DIA dans le VPN 10 (LAN)
! ---------------------------------------------------------------------
vrf definition 10
 address-family ipv4
  ! Fuite de route (Route Leaking) pour orienter le trafic web directement vers le VPN 0
  ip route 0.0.0.0 0.0.0.0 global
 exit-address-family
!
```

> **Avertissement de Sécurité :** L'activation du DIA permet au trafic local de quitter le tunnel chiffré IPsec pour aller directement sur Internet. Sans l'activation conjointe du pare-feu d'inspection d'état (*Zone-Based Firewall*) sur le WAN Edge ou la redirection vers un connecteur **SASE (Secure Access Service Edge)** tel que Cisco Umbrella ou Zscaler, l'agence devient vulnérable aux intrusions directes.

---

## 4. Intégration SASE et Cloud OnRamp

L'évolution moderne des architectures SD-WAN de niveau intermédiaire s'articule autour de deux piliers fondamentaux : **SASE** et l'optimisation **Multi-Cloud**.

```
                          ┌───────────────────────────┐
                          │   Architecture SASE       │
                          │ (Secure Access Svc Edge)  │
                          └─────────────┬─────────────┘
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
   Composants Réseau (SD-WAN)                                Composants Sécurité (SSE)
   ├── Optimization Transport WAN                            ├── Secure Web Gateway (SWG)
   ├── Routing Applicatif (AAR)                              ├── Cloud Access Security Broker (CASB)
   └── Overlay IPsec Chiffré                                 └── Zero Trust Network Access (ZTNA)
```

### 1. Le modèle SASE (Secure Access Service Edge)
Défini par Gartner, le SASE converge les fonctionnalités réseau du SD-WAN avec les fonctionnalités de sécurité Cloud dites **SSE ( Security Service Edge)**. 

Au lieu d'exécuter des moteurs d'inspection lourds (IPS, Antivirus, Filtrage URL) en surchargeant les ressources matérielles des routeurs WAN Edge d'agence, le WAN Edge établit automatiquement des tunnels sécurisés (IPsec ou GRE) vers le point de présence (*PoP*) le plus proche d'un fournisseur de sécurité Cloud. 

Le flux d'accès Internet suit alors le parcours :  
`Poste Utilisateur` $\rightarrow$ `WAN Edge Agence` $\rightarrow$ `Tunnel IPsec/GRE` $\rightarrow$ `Cloud SASE (Inspection & Filtrage)` $\rightarrow$ `SaaS / Internet Public`.

### 2. Cloud OnRamp for IaaS / SaaS
* **Cloud OnRamp for SaaS** : Mesure en continu la latence et la perte de paquets vers les applications SaaS (ex: Office 365) via deux chemins : l'accès direct local (DIA) et l'accès via le Data Center central. Le vSmart / WAN Edge bascule dynamiquement le trafic applicatif sur le chemin offrant les meilleures performances à l'instant $T$.
* **Cloud OnRamp for IaaS** : Automatise l'extension du réseau SD-WAN directement au sein des Virtual Private Clouds (VPC AWS / Azure VNets). Des instances virtuelles WAN Edge (vEdge/cEdge) sont instanciées automatiquement dans le Cloud public pour intégrer les ressources Cloud comme de simples agences du réseau d'entreprise.

---

## 5. Dépannage Avancé et Diagnostics OMP

Lors du dépannage d'un réseau SD-WAN intermédiaire, la compréhension de la table de routage OMP et de la table TLOC est cruciale.

### 1. Commandes de Diagnostic CLI Avancées (cEdge / IOS-XE SD-WAN)

```bash
# 1. Vérifier l'état détaillé des paires OMP avec les contrôleurs vSmart
show sdwan omp peers

# 2. Inspecter toutes les routes OMP reçues et envoyées, et identifier les routes choisies (* = valid, C = chosen)
show sdwan omp routes

# 3. Inspecter la table des TLOCs connus par le WAN Edge local
show sdwan tloc routes

# 4. Vérifier la santé et les métriques (Loss, Latency, Jitter) des sondes BFD sur chaque tunnel
show sdwan bfd sessions

# 5. Diagnostiquer les politiques AAR en cours d'application sur un flux spécifique
show sdwan app-route-stats
```

### 2. Anlayse des symptômes de panne courants

| Symptôme | Cause Probable | Action de Dépannage |
| :--- | :--- | :--- |
| **Sessions DTLS vers vSmart établies, mais aucune route OMP apprise** | Politique de contrôle (*Control Policy*) bloquante sur vSmart ou divergence de `Site-ID`. | Inspecter la politique centralisée active sur vSmart via `show sdwan running-config policy`. |
| **Les tunnels IPsec BFD entre deux agences ne s'établissent pas (`Down`)** | Problème de NAT intermédiaire, restriction de port UDP (12346+), ou inadéquation de couleur TLOC. | Vérifier si les TLOCs s'affichent via `show sdwan tloc routes`. Tester la joignabilité UDP avec `traceroute`. |
| **Le trafic applicatif ne bascule pas en cas de perte de paquets sur l'Internet** | Les seuils SLA dans l'AAR Policy sont trop permissifs ou le temps de calcul glissant BFD est trop long. | Ajuster le paramètre `app-route multiplier` et vérifier la classe SLA avec `show sdwan policy-firmware`. |

---

## Points à retenir

* **OMP (Overlay Management Protocol)** est le protocole de contrôle centralisé du SD-WAN. Il s'exécute uniquement entre les WAN Edges et le contrôleur vSmart pour échanger les routes IP du LAN, les routes TLOC et les services réseau.
* **Mise en forme de la Topologie** : La topologie physique sous-jacente n'impose pas la topologie logique. Une **Control Policy** appliquée sur le vSmart permet de transformer dynamiquement un réseau *Full-Mesh* par défaut en *Hub-and-Spoke* en réécrivant les attributs de TLOC.
* **Distinction des Politiques** : Les **Centralized Policies** gèrent la topologie (Control) et le routage applicatif global / AAR (Data) via le vSmart. Les **Localized Policies** gèrent la QoS, la redistribution locale (OSPF/BGP) et les Access Lists d'interface sur le WAN Edge.
* **Direct Internet Access (DIA)** : Permet aux agences de sortir directement vers Internet pour consommer du Cloud/SaaS. Il nécessite l'activation du NAT dans le VPN 0, une fuite de route par défaut vers le VPN Utilisateur, et une sécurisation stricte (SASE / Firewall).