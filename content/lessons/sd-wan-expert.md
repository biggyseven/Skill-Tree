## node_id: sd-wan-expert
title: SD-WAN (Software-Defined Wide Area Network) - Expert

# SD-WAN (Software-Defined Wide Area Network) - Expert

**Niveau :** Expert

**Prérequis :** SD-WAN Débutant (`sd-wan-debutant`), SD-WAN Intermédiaire (`sd-wan-intermediaire`)

Dans les modules précédents, nous avons consolidé les fondamentaux de l'architecture découplée SD-WAN, puis approfondi la mécanique du protocole **OMP**, la gestion des **TLOCs**, l'ingénierie des politiques centralisées et l'intégration des accès directs Internet (DIA / SASE).

Au niveau **Expert**, l'objectif est d'aborder les défis d'architecture d'entreprise à très grande échelle (plusieurs milliers de sites distants, environnements multi-Data Centers, intégration multi-cloud hybride). Ce cours traite du design et du redimensionnement de l'infrastructure de contrôle (Cluster vManage, vSmart/vBond Redundancy), du routage hiérarchique multi-région (*Multi-Region Fabric*), de l'insertion dynamique de services complexes (*Service Chaining / Multi-VRF Leaking*), de la programmabilité système via API REST/NETCONF, ainsi que des techniques de diagnostic applicatif et système à bas niveau.

## 1. Architecture Haute Disponibilité & Redimensionnement du Plan de Contrôle

Dans un déploiement SD-WAN d'envergure mondiale, la résilience et la scalabilité des composants du plan de contrôle et de gestion sont critiques. Une panne du plan de contrôle n'interrompt pas immédiatement le transfert des données déjà établies (*Data Plane Holddown*), mais elle empêche toute mise à jour topologique, tout renouvellement des clés IPsec et toute adaptation aux variations de qualité réseau.

```
                  ┌─────────────────────────────────────────┐
                  │          CLUSTER MANAGEMENT             │
                  │   vManage 1 ─── vManage 2 ─── vManage 3 │
                  │     (Active)     (Active)     (Active)  │
                  └────────────────────┬────────────────────┘
                                       │ VIP / Load Balancer
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │          PLAN D'ORCHESTRATION           │
                  │        vBond 1         vBond 2          │
                  └────────────────────┬────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌──────────────────────┐                               ┌──────────────────────┐
│  PLAN DE CONTRÔLE 1  │                               │  PLAN DE CONTRÔLE 2  │
│  vSmart 1   vSmart 2 │                               │  vSmart 3   vSmart 4 │
│   (Region Group 1)   │                               │   (Region Group 2)   │
└───────────┬──────────┘                               └───────────┬──────────┘
            │                                                      │
            └──────────────────────────┬───────────────────────────┘
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │            FABRIQUE OVERLAY             │
                  │  [WAN Edge 1]    ...    [WAN Edge N]    │
                  └─────────────────────────────────────────┘
```

### 1. Cluster vManage & Synchronisation des Base de Données

Le vManage prend en charge le fonctionnement en cluster distribué (minimum 3 nœuds pour assurer le quorum et éviter le syndrome du *Split-Brain*). La répartition des responsabilités au sein du cluster repose sur plusieurs bases de données spécialisées :

* **NMS Application Server** : Fournit l'interface graphique utilisateur (GUI) et l'accès API.
* **Database OrientDB / Neo4j** : Stocke la configuration des modèles (*Templates*), des politiques, les inventaires d'équipements et la carte du réseau. Elle est répliquée de manière synchrone sur les nœuds du cluster.
* **Elasticsearch / OpenSearch** : Base de données de séries temporelles stockant les métriques de performance (statistiques BFD, consommations applicatives, journaux d'événements). Elle utilise un système de découpage en *shards* distribués entre les nœuds.
* **Kafka & Zookeeper** : Assure la coordination du cluster, le passage de messages d'état en temps réel et la synchronisation des événements d'alarme entre les instances vManage.

### 2. Redondance des Contrôleurs vSmart & Affinity Groups

Pour garantir la montée en charge, les routeurs WAN Edge doivent pouvoir s'interconnecter à plusieurs contrôleurs vSmart.
Par défaut, un vSmart peut gérer jusqu'à 5 000 à 10 000 connexions OMP selon ses ressources matérielles (vCPU/RAM).

* **OMP Mesh entre vSmarts** : Tous les vSmarts au sein de la fabrique établissent des sessions OMP entre eux pour maintenir une vue parfaitement synchronisée des routes OMP et TLOC.
* **Control Controller Group ID (Affinity)** : Pour optimiser la charge mémoire et les flux réseau, les WAN Edges peuvent être configurés pour privilégier un groupe de vSmarts géographiquement proche (*Controller Group ID*).

$$
\text{Nombre Max Tunnels Control} = \text{Nombre de vSmarts ciblés} \times \text{Nombre de TLOCs locaux actifs}
$$

### 3. Redondance de l'Orchestrateur vBond

Les vBonds ne maintiennent pas d'état persistant (*Stateless Controllers*). La haute disponibilité s'effectue simplement en publiant plusieurs enregistrements `A` dans le serveur DNS de l'entreprise pour le FQDN du vBond, ou en déployant plusieurs nœuds vBond avec des adresses IP publiques distinctes derrière un nom de domaine unique.

---

## 2. Routage Avancé OMP & Multi-Region Fabric (MRF)

Lorsque le nombre de sites d'entreprise dépasse quelques milliers d'équipements, la diffusion globale de l'ensemble des TLOCs et routes OMP à tous les WAN Edges entraîne une saturation des ressources CPU et de la mémoire vive sur les routeurs d'agence.

### 1. Algorithme de Sélection de Route OMP (Path Selection Algorithm)

Lorsqu'un routeur WAN Edge ou un contrôleur vSmart reçoit plusieurs routes OMP pour le même préfixe IP destination, il applique une séquence d'évaluation stricte pour sélectionner la meilleure route (similaire au processus BGP) :

1. **Valid Route Check** : La route OMP doit posséder un TLOC valide et résolu.
2. **OMP Preference** : La valeur d'attribut `preference` la plus élevée est privilégiée (valeur par défaut : 0).
3. **Site-ID Metric / Origin** : Préférence pour les routes issues du même `Site-ID` (routes locales).
4. **TLOC Path Metric** : Préférence pour le TLOC ayant la métrique administrative de transport la plus faible.
5. **Origin Type** : Ordre de préférence du protocole source : `Connected` $\gt$ `Static` $\gt$ `BGP` $\gt$ `OSPF inter-area` $\gt$ `OSPF intra-area` $\gt$ `OSPF external`.
6. **Origin Metric** : La métrique d'origine la plus faible du protocole redistribué.
7. **System-IP** : L'adresse `System-IP` la plus élevée (ou la plus basse selon l'implémentation du tirage au sort) pour rompre l'égalité.

### 2. Architecture Multi-Region Fabric (SD-WAN Region-Based Architecture)

Pour passer à l'échelle (10 000+ sites), l'architecture est segmentée en **Régions** autonomes :

```
┌────────────────────────────────────────────────────────────────────────┐
│                              REGION 0                                  │
│                   (Core / Data Centers / Transit)                      │
│                                                                        │
│            ┌──────────────────┐      ┌──────────────────┐              │
│            │   Border Edge    │      │   Border Edge    │              │
│            │     (DC East)    │      │     (DC West)    │              │
│            └────────┬─────────┘      └────────┬─────────┘              │
└─────────────────────┼─────────────────────────┼────────────────────────┘
                      │                         │
            ┌─────────┴─────────┐     ┌─────────┴─────────┐
            │                   │     │                   │
            ▼                   ▼     ▼                   ▼
┌───────────────────────────────┐ ┌───────────────────────────────┐
│           REGION 1            │ │           REGION 2            │
│         (EMEA Sites)          │ │         (AMER Sites)          │
│   [WAN Edge]    [WAN Edge]    │ │   [WAN Edge]    [WAN Edge]    │
└───────────────────────────────┘ └───────────────────────────────┘
```

* **Region 0 (Core/Backbone Region)** : Interconnecte les Data Centers principaux et les points de transit régionaux.
* **Access Regions (Regions 1 à N)** : Regroupent les sites distants par zone géographique ou administrative. Les routeurs d'agence d'une région d'accès ne connaissent que les routes de leur propre région.
* **Border Routers (Border WAN Edges)** : Équipements situés à la frontière entre la Région 0 et une Région d'Accès. Ils réécrivent les TLOCs, réalisent la sommation de routes (*Route Summarization*) et évitent le maillage global des tunnels IPsec inter-régions.

---

## 3. Service Chaining & Fuite de Routes Multi-VRF

Le **Service Chaining** permet d'insérer dynamiquement des équipements de traitement réseau (*VNFs / Appliances*) tels que des Pare-Feux de nouvelle génération (NGFW), des systèmes d'inspection IPS/IDS ou des accélérateurs WAN dans le chemin d'acheminement des données, sans modifier la topologie physique du réseau.

### 1. Mecanisme de Service Insertion via OMP

Un routeur d'agence ou de Data Center sur lequel est raccordé un Pare-Feu déclare ce service au contrôleur vSmart au moyen d'une route de service OMP (`Service Route`).

```
+---------------------------------------------------------------------+
| DATA CENTER (SITE 100)                                              |
|                                                                     |
|    ┌───────────────┐              ┌────────────────────┐            |
|    │  Firewall L4-7│              │   WAN Edge (Hub)   │            |
|    └───────┬───────┘              │                    │            |
|            │ (Interface Service)  │ System-IP: 10.0.0.1│            |
|            └─────────────────────►│ TLOC: DC-MPLS      │            |
|                                   └─────────┬──────────┘            |
+---------------------------------------------┼-----------------------+
                                              │ OMP Service Advert:
                                              │ "Service FW, VRF 10,
                                              │  TLOC DC-MPLS"
                                              ▼
                                   ┌────────────────────┐
                                   │  Contrôleur vSmart │
                                   └────────────────────┘
```

Le vSmart propage cette information. Lorsqu'une politique centralisée de données (*Data Policy*) est appliquée, elle détourne les flux correspondants vers le TLOC hébergeant le service requis. Le paquet encapsulé IPsec inclut alors une étiquette de service (*Service Label*) dans l'en-tête pour indiquer au WAN Edge récepteur d'orienter le paquet vers l'interface du Pare-Feu avant de le réacheminer vers sa destination finale.

### 2. Fuite de Routes Inter-VRF (Multi-VRF Leaking)

Dans les architectures segmentées (ex: VRF 10 = Utilisateurs, VRF 20 = Partenaires / IoT, VRF 30 = Services Communs), il est souvent nécessaire d'autoriser la communication contrôlée entre deux VRF au niveau du site Hub/Data Center.

---

## 4. Configuration Avancée & Ingénierie du Code CLI

La configuration CLI suivante sur un **cEdge (IOS-XE SD-WAN)** illustre l'implémentation avancée du **Service Chaining** (insertion d'un Pare-Feu en VRF 10) ainsi qu'un mécanisme de **Multi-VRF Route Leaking** sécurisé.

```
! =====================================================================
! SECTION 1 : DECLARATION DU SERVICE DANS LE PROTOCOLE OMP
! =====================================================================
sdwan
 omp
  no shutdown
  graceful-restart
  advertise connected
  advertise static
  
  ! Déclaration de la présence d'un Pare-feu (FW) en VRF 10
  service FW vrf 10 10.100.10.254
 !
!

! =====================================================================
! SECTION 2 : CONFIGURATION DU SERVICE SIDE & INTERACTION FW
! =====================================================================
vrf definition 10
 rd 100:10
 address-family ipv4
  exit-address-family
!

! Interface connectée à la patte "Inside" du Pare-Feu
interface GigabitEthernet4
 description *** Interface vers Firewall LAN Inside ***
 vrf forwarding 10
 ip address 10.100.10.1 255.255.255.0
 no shutdown
!

! =====================================================================
! SECTION 3 : FUITE DE ROUTES INTER-VRF (VRF LEAKING VIA TARGET SUBNETS)
! =====================================================================
vrf definition 20
 description *** VRF Partenaires / IoT ***
 rd 100:20
 address-family ipv4
  ! Importation ciblée des routes de la VRF 10 vers VRF 20
  route-target import 100:10
  exit-address-family
!

vrf definition 10
 address-family ipv4
  ! Exportation des routes de la VRF 10 vers d'autres VRFs
  route-target export 100:10
  exit-address-family
!

! =====================================================================
! SECTION 4 : POLITIQUE AAR AVEC REARRANGEMENT DE MERTIES BFD
! =====================================================================
sdwan
 bfd app-route multiplier 3
 bfd app-route poll-interval 60000
!

policy
 sla-class CRITICAL_APPS
  latency 80
  loss 0.5
  jitter 5
 !
 app-route-policy HEURISTIC_AAR
  sequence 10
   match
    app-list ERP_APPLICATIONS
   !
   action
    sla-class CRITICAL_APPS preferred-color mpls
    backup-preferred-color public-internet
   !
  !
 !
!
```

---

## 5. Automation, Programmabilité & API REST

La gestion manuelle de milliers de modèles d'équipements via l'interface vManage devient inefficace à l'échelle Expert. L'automatisation repose sur des scripts interagissant directement avec l'**API REST du vManage** ou via des modèles **NETCONF/YANG**.

### 1. Modèle d'Authentification & Flux API vManage

Pour exécuter des requêtes sur l'API REST vManage, un client doit gérer une session authentifiée à deux facteurs d'en-tête :
1. **Cookie de Session (`JSESSIONID`)** : Obtenu via la route `/j_security_check`.
2. **Jeton CSRF (`X-XSRF-TOKEN`)** : Obtenu via la route `/dataservice/token` après établissement du cookie.

### 2. Script Python d'Automation : Extraction des Tunnels BFD & Audit de Santé

Le script Python ci-dessous démontre comment s'authentifier de manière sécurisée auprès du vManage, récupérer le jeton anti-CSRF, et interroger l'état de tous les tunnels BFD en échec dans la fabrique SD-WAN.

```python
#!/usr/bin/env python3
"""
Script d'Automation SD-WAN Expert:
Extraction des sessions BFD dégradées via l'API REST du vManage.
"""

import requests
import urllib3
import json
import sys

# Masquer les avertissements liés aux certificats auto-signés
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VMANAGE_IP = "192.168.1.10"
USERNAME = "admin"
PASSWORD = "Password123!"

BASE_URL = f"https://{VMANAGE_IP}"

session = requests.Session()
session.verify = False

def get_vmanage_session():
    """Authentification et récupération du Cookie JSESSIONID."""
    login_url = f"{BASE_URL}/j_security_check"
    payload = {'j_username': USERNAME, 'j_password': PASSWORD}
    
    try:
        response = session.post(login_url, data=payload)
        if response.status_code != 200 or "login" in response.text.lower():
            print("[!] Échec d'authentification vManage.")
            sys.exit(1)
        print("[+] Authentification réussie (Cookie JSESSIONID obtenu).")
    except Exception as e:
        print(f"[!] Erreur de connexion : {e}")
        sys.exit(1)

def get_csrf_token():
    """Récupération du Token Anti-CSRF obligatoire pour les requêtes API."""
    token_url = f"{BASE_URL}/dataservice/token"
    response = session.get(token_url)
    if response.status_code == 200:
        token = response.text
        session.headers.update({'X-XSRF-TOKEN': token})
        print(f"[+] Token CSRF récupéré : {token[:10]}...")
    else:
        print("[!] Impossible de récupérer le token CSRF.")
        sys.exit(1)

def audit_bfd_sessions():
    """Interrogation des métriques BFD pour détecter les tunnels Down."""
    bfd_url = f"{BASE_URL}/dataservice/device/bfd/synced/sessions"
    response = session.get(bfd_url)
    
    if response.status_code == 200:
        data = response.json().get('data', [])
        down_sessions = [s for s in data if s.get('state') != 'up']
        
        print(f"\n=== AUDIT DES TUNNELS BFD ({len(data)} Tunnels inspectés) ===")
        if not down_sessions:
            print("[✔] Tous les tunnels BFD de la fabrique sont dans l'état UP.")
        else:
            print(f"[✘] ALERTE : {len(down_sessions)} tunnel(s) BFD hors service !")
            for s in down_sessions:
                print(f" -> Device: {s.get('vdevice-dataKey')} | Local Color: {s.get('local-color')} | "
                      f"Remote IP: {s.get('dst-ip')} | State: {s.get('state')}")
    else:
        print(f"[!] Échec de récupération des données BFD (HTTP {response.status_code}).")

if __name__ == "__main__":
    get_vmanage_session()
    get_csrf_token()
    audit_bfd_sessions()
```

---

## 6. Dépannage Bas-Niveau & Analyse Traces Système

Au niveau Expert, le diagnostic de pannes complexes (ex: interruptions intermittentes de tunnels, fuites mémoire du processus OMP, rejets de certificats PKI) nécessite l'analyse directe des processus internes et la capture de paquets avancée.

### 1. Analyse des processus de contrôle (vDaemon / OMP Daemon)

Sur les équipements SD-WAN, les processus clés du plan de contrôle tournent sous forme de démons système :

* `vda` (vBond/vSmart Control Daemon) : Gère les sessions DTLS/TLS de contrôle.
* `omp` (OMP Routing Daemon) : Calcule la table de routage OMP et traite les politiques.
* `ftm` (Forwarding Table Manager) : Injecte les routes de l'OMP vers la table CEF/FIB matérielle du plan de données.

```bash
# Activation des traces de débogage ciblées sur le démon OMP (sur vSmart / cEdge)
debug sdwan omp adjacencies
debug sdwan omp packets

# Consultation des journaux système de contrôle en temps réel
show logging process ompd
```

### 2. Validation de la chaîne de confiance PKI & Certificats

Les rejets de connexions de contrôle (`CR_ERR` / `CONTROL_CONN_ERR`) sont fréquemment causés par une désynchronisation d'horloge (NTP) ou une invalidité de la chaîne de certificats X.509.

```bash
# 1. Vérification de la validité temporelle du certificat SUDI/Enterprise
show sdwan certificate serial

# 2. Validation de la chaîne d'autorité de certification (CA Root)
show sdwan certificate installed

# 3. Diagnostic des rejets de contrôle
show sdwan control valid-vsmarts
show sdwan control valid-vedges
```

### 3. Packet Tracing & Embedded Packet Capture (EPC)

Pour analyser la traversée exacte d'un paquet à travers les fonctionnalités SD-WAN (DPI, AAR, NAT, Encryption IPsec), l'outil **Datapath Packet Trace** (sur IOS-XE) est l'instrument le plus précis :

```
# Activation du suivi du chemin de données pour une IP source donnée
monitor platform condition ipv4 10.101.10.50/32 both
monitor platform packet-trace packet 2048 fia-trace
monitor platform condition start

# Une fois le trafic généré :
show platform packet-trace summary
show platform packet-trace packet 0
```

---

## Points à retenir

* **Architecture Cluster vManage** : Repose sur un quorum de minimum 3 nœuds coordonnés par Zookeeper/Kafka, combinant une base OrientDB/Neo4j pour la configuration et Elasticsearch pour le stockage des métriques BFD/AAR.
* **Algorithme de Sélection OMP** : Suit un processus déterministe rigoureux où la valeur d'attribut `OMP Preference` et la provenance locale (`Site-ID`) priment sur la métrique du protocole source.
* **Multi-Region Fabric (MRF)** : Permet de découper l'Overlay en Régions d'Accès et une Région Core (Region 0) reliées par des *Border WAN Edges*, éliminant les limites de scalabilité des tables de routage.
* **Service Chaining & Label Overlays** : Insère des services de niveau 4 à 7 (NGFW, IPS) de manière transparente via l'annonce de `Service Routes` OMP et l'encapsulation de *Service Labels* dans les paquets IPsec.
* **Programmabilité REST / Python** : L'automatisation du vManage requiert la gestion conjointe du cookie d'authentification `JSESSIONID` et du jeton de protection `X-XSRF-TOKEN`.