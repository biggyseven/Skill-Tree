# Cisco SD‑Access & Fabric – Cours Intensif (Niveau Senior Network Admin)

> **Objectif** : Maîtriser la conception, le déploiement, l’exploitation et le dépannage d’une solution Cisco Software‑Defined Access (SD‑Access) et du Cisco Fabric.  
> **Durée estimée** : 3 jours de formation intensive (≈ 24 h) + laboratoire de 6 h.  
> **Prérequis** : CCNP Enterprise, connaissance du routing IP, des VLANs, du VXLAN, du L2/L3, expérience des commutateurs Catalyst 9000 et des solutions ACI.

---

## Table des Matières

| # | Chapitre | Description |
|---|----------|-------------|
| 1 | **Introduction & Concepts de base** | Définitions, motivations, comparaison avec les approches traditionnelles |
| 2 | **Architecture SD‑Access** | Fabric, Controllers, Edge, Border, Policy, Assurance |
| 3 | **Composants matériels & logiciels** | Catalyst 9000, vManage, DNA Center, ISE, APIC‑EM |
| 4 | **Design du Fabric** | Topologies, segmentation, overlay, sous‑netting, plan d’adressage |
| 5 | **Déploiement pas à pas** | Pré‑requis, licences, mise à jour, activation du Fabric |
| 6 | **Configuration détaillée** | CLI, API, templates, policies (Group, Authentication, Policy) |
| 7 | **Intégration avec les services existants** | L3‑out, WAN, MPLS, ACI, Cloud |
| 8 | **Assurance, Telemetry & Monitoring** | NetFlow, Syslog, DNA Assurance, OpenTelemetry |
| 9 | **Atelier de dépannage** | Scénarios réels, méthodologie, outils |
|10 | **Bonnes pratiques & Checklist** | Sécurité, haute disponibilité, upgrade, sauvegarde |
|11 | **Examen de validation** | QCM, exercices pratiques |
|12 | **Références & Ressources** | Docs Cisco, livres, labs, communautés |

---

## 1️⃣ Introduction & Concepts de base

### 1.1 Pourquoi SD‑Access ?

| Problème traditionnel | Solution SD‑Access |
|-----------------------|--------------------|
| **Segmentation manuelle** (VLANs, ACLs) | **Segmentation basée sur les groupes** (Policy‑Based Segmentation) |
| **Provisioning lent** (configuration CLI) | **Provisioning automatisé** (DNA Center, templates) |
| **Visibilité limitée** (SNMP, NetFlow) | **Assurance intégrée** (DNA Assurance, Telemetry) |
| **Gestion de la mobilité** (VLAN hopping) | **Mobility native** (Overlay VXLAN, fabric‑wide) |
| **Interopérabilité difficile** (multivendor) | **Abstraction du hardware** (Control Plane séparé) |

### 1.2 Définitions clés

| Terme | Définition |
|-------|------------|
| **SD‑Access** | Architecture Cisco qui sépare le **Control Plane** (DNA Center) du **Data Plane** (fabric switches) et fournit un **fabric overlay** basé sur VXLAN. |
| **Fabric** | Ensemble de commutateurs (Edge, Border, Leaf‑Spine) qui transportent le trafic overlay via **VXLAN** et le trafic underlay via **OSPF/ISIS**. |
| **Overlay** | Réseau virtuel (VXLAN) qui porte les **Group‑Based Policies** (GBP). |
| **Underlay** | Réseau physique (IP) qui assure la connectivité des nœuds du fabric (IP‑routing, IGP). |
| **Border Node** | Point d’entrée/sortie du fabric vers le réseau externe (WAN, Internet, Data Center). |
| **Edge Node** | Point d’accès des endpoints (PC, serveurs, AP) au fabric. |
| **Control Plane (DNA Center)** | Orchestrateur central qui pousse les politiques, gère les identités, crée les tunnels VXLAN, etc. |
| **Policy (Group‑Based)** | Association d’un **User/Device Group** à un **Virtual Network (VN)** et à des **ACLs**. |
| **Assurance** | Collecte en temps réel de la performance, du comportement, des incidents. |

---

## 2️⃣ Architecture SD‑Access

```
+-----------------------------------------------------------+
|                     DNA Center (Control)                |
|  +-----------+   +-----------+   +-----------+            |
|  | Policy    |   | Assurance |   | Provision |            |
|  +-----------+   +-----------+   +-----------+            |
+------------------------|----------------------------------+
                         |
                         | NETCONF / RESTCONF / gNMI
                         v
+-------------------+-------------------+-------------------+
|  Border Nodes (Leaf)    Edge Nodes (Leaf)    Spine Nodes   |
|  (Layer 3)              (Layer 2)            (Layer 2)      |
|  +-------------------+  +----------------+  +------------+ |
|  | 10.1.0.0/24       |  | 10.2.0.0/24    |  | 10.3.0.0/24| |
|  +-------------------+  +----------------+  +------------+ |
|          |                     |                |        |
|          |   VXLAN Overlay (VNI per VN)          |        |
|          +---------------------------------------+        |
|                Underlay IGP (OSPF/ISIS)                |
+-----------------------------------------------------------+
```

### 2.1 Couches du Fabric

| Couche | Fonction | Protocoles |
|--------|----------|------------|
| **Data Plane** | Transport du trafic (underlay + overlay) | VXLAN, BGP EVPN (optionnel), OSPF/ISIS |
| **Control Plane** | Distribution des politiques, création des tunnels | DNA Center (RESTCONF), Cisco ISE (AAA) |
| **Management Plane** | Gestion, monitoring, assurance | DNA Center, Cisco Prime, Syslog, NetFlow, SNMP |
| **Identity Plane** | Authentification, autorisation | Cisco ISE, RADIUS, TACACS+ |

### 2.2 Types de nœuds

| Type | Rôle | Exemple de modèle |
|------|------|--------------------|
| **Border** | Routage vers l’extérieur, L3‑out, firewall, Internet | Catalyst 9500, Catalyst 9400 (L3) |
| **Edge** | Accès aux endpoints, PoE, APs, serveurs | Catalyst 9200/9300, Catalyst 9400 (L2) |
| **Spine** | Transport haute densité, agrégation sous‑plan | Catalyst 9500, Nexus 9000 (mode L2) |
| **Controller** | Orchestrateur central (DNA Center) | Appliance ou VM (Cisco DNA Center) |
| **ISE** | Gestion des identités et des politiques d’accès | Cisco ISE VM/Appliance |

---

## 3️⃣ Composants matériels & logiciels

| Composant | Version minimale | Licence requise | Fonction |
|-----------|------------------|-----------------|----------|
| **Catalyst 9000 (Edge/Border/Spine)** | IOS‑XE 16.12+ | DNA‑Essentials / DNA‑Advantage | Data Plane, VXLAN, LISP/EVPN |
| **Cisco DNA Center** | 2.3+ | DNA‑Advantage (perpetual) | Orchestration, Assurance, Policy |
| **Cisco ISE** | 3.1+ | ISE‑Base + ISE‑Plus (policy) | AAA, Group‑Based Policies |
| **Cisco Prime Infrastructure** (optionnel) | 3.9+ | N/A | Monitoring legacy |
| **Linux host (vManage/Ansible)** | Ubuntu 22.04 | N/A | Automation, API testing |
| **APIC‑EM** (optional) | 4.2+ | N/A | Programmabilité, SD‑WAN integration |

### 3.1 Licences SD‑Access

| Licence | Fonctionnalité | Exemple d’utilisation |
|---------|----------------|-----------------------|
| **DNA‑Essentials** | Basique : VLAN, VXLAN, L2/L3, PoE | Petit campus, 2‑3 sites |
| **DNA‑Advantage** | Avancé : Policy‑Based Segmentation, Assurance, Telemetry, Automation | Grand campus, multi‑site, Cloud‑Ready |
| **DNA‑Premiere** | Full stack + ACI integration, SD‑WAN | Data Center, hybride cloud |

---

## 4️⃣ Design du Fabric

### 4.1 Topologies recommandées

| Topologie | Avantages | Inconvénients | Cas d’usage |
|-----------|-----------|---------------|-------------|
| **Leaf‑Spine (2‑tier)** | Scalabilité, faible latence, redondance | Besoin d’un plus grand nombre de liens | Campus moderne, > 5000 endpoints |
| **Ring (MST)** | Simplicité, moins de liens physiques | Boucles potentielles, convergence plus lente | Petit site, budget limité |
| **Hybrid (Leaf‑Spine + Ring)** | Combine redondance et économies | Complexité de configuration | Campus distribué avec plusieurs bâtiments |

### 4.2 Plan d’adressage IP (Underlay)

```
Underlay (OSPF) – 10.0.0.0/16
└─ Spine-1 : 10.0.0.1/30  (link to Edge-1)
└─ Spine-2 : 10.0.0.5/30  (link to Edge-2)
...
Edge-1 : 10.0.1.1/30 (to Spine-1)
Edge-2 : 10.0.1.5/30 (to Spine-2)
...
Border-1 : 10.0.255.1/24 (L3‑out)
```

### 4.3 Plan d’adressage VXLAN (Overlay)

| VN (Virtual Network) | VNI (VXLAN Network Identifier) | Subnet | Usage |
|----------------------|--------------------------------|--------|-------|
| **VN‑10 – Guest** | 1010 | 192.168.10.0/24 | BYOD, visiteurs |
| **VN‑20 – Corp** | 1020 | 192.168.20.0/24 | Employés internes |
| **VN‑30 – IoT** | 1030 | 192.168.30.0/24 | Caméras, capteurs |
| **VN‑40 – DataCenter** | 1040 | 10.10.0.0/16 | Serveurs, VM |
| **VN‑50 – Guest‑WiFi** | 1050 | 172.16.50.0/24 | Wi‑Fi invité |

> **Règle** : chaque VN possède son propre VNI, qui reste constant quel que soit le site.

### 4.4 Découpage des Groupes d’utilisateurs (AAA)

| Group‑Name | Source (ISE) | VN | ACL |
|------------|--------------|----|-----|
| **Guest** | BYOD‑Device‑Group | VN‑10 | ACL‑Guest (Internet only) |
| **Employee** | AD‑User‑Group | VN‑20 | ACL‑Corp (Full access) |
| **IoT** | IoT‑Device‑Group | VN‑30 | ACL‑IoT (Limited) |
| **DC‑Servers** | Server‑Group | VN‑40 | ACL‑DC (Restricted) |

---

## 5️⃣ Déploiement pas à pas

### 5.1 Pré‑requis

1. **Inventaire matériel** – Vérifier la compatibilité des modèles Catalyst 9000 (Nexus 9000 en mode L2 supporté).  
2. **Licences** – Activer DNA‑Advantage sur chaque switch via `license smart register idtoken <TOKEN>`.  
3. **Version IOS‑XE** – Minimum 16.12.5 f – mettre à jour via `install add file flash:<image>.bin` puis `install activate`.  
4. **Serveur ISE** – Configurer les **Identity Sources** (AD, LDAP) et créer les **User Groups**.  
5. **DNA Center** – Déployer l’appliance, configurer le **Site** (Physical, Virtual) et les **Fabric Domains**.

### 5.2 Activation du Fabric (CLI)

```bash
! Sur chaque switch (Edge, Border, Spine)
conf t
  feature sd-access
  fabric domain <DOMAIN_NAME>
  fabric site <SITE_NAME>
  fabric border-group <BG_NAME>
  fabric edge-group <EG_NAME>
  fabric control-plane
    ip routing
    no shutdown
  exit
  fabric data-plane
    vxlan
    encapsulation vxlan
    no shutdown
  exit
  fabric border-virtual-network <VN_NAME> vni <VNI>
  fabric edge-virtual-network <VN_NAME> vni <VNI>
  fabric border-group <BG_NAME>
    border-virtual-network <VN_NAME>
    exit
  fabric edge-group <EG_NAME>
    edge-virtual-network <VN_NAME>
    exit
end
write memory
```

> **Note** : Le **fabric domain** regroupe les sites qui partagent le même **Control Plane**.  

### 5.3 Enregistrement des nœuds auprès de DNA Center

```bash
# Sur le switch
conf t
  ip name-server 10.10.10.10
  ip domain-name corp.example.com
  username admin privilege 15 secret 0 <pwd>
  ip ssh version 2
  line vty 0 4
    login local
    transport input ssh
  exit
  fabric controller ip <DNA_CONTROLLER_IP>
  fabric controller port 443
  fabric controller username admin password <pwd>
  fabric controller register
end
```

### 5.4 Création d’un Virtual Network (VN) via DNA Center (API)

```bash
curl -k -u admin:password -X POST \
  https://<DNA_IP>/dna/intent/api/v1/sda/virtual-network \
  -H "Content-Type: application/json" \
  -d '{
        "name": "VN-Guest",
        "vlanId": "10",
        "vni": "1010",
        "ipPool": "192.168.10.0/24",
        "isLayer2Only": false,
        "isGuestVirtualNetwork": true
      }'
```

### 5.5 Association d’un groupe d’utilisateurs à une VN (ISE)

```bash
# Exemple via le CLI ISE (REST API)
curl -k -u iseadmin:password -X POST \
  https://<ISE_IP>/ers/config/authenticationpolicyset \
  -H "Content-Type: application/json" \
  -d '{
        "name": "GuestPolicySet",
        "description": "Policy for Guest devices",
        "default": false,
        "identitySourceId": "ad-source-id",
        "condition": {
          "conditionType": "ConditionAttributes",
          "attributeName": "Group",
          "attributeValue": "Guest"
        },
        "policy": {
          "profileName": "GuestProfile",
          "virtualNetworkName": "VN-Guest"
        }
      }'
```

---

## 6️⃣ Configuration détaillée

### 6.1 VLAN & VXLAN Mapping

| VLAN | VN | VNI | Description |
|------|----|-----|-------------|
| 10 | VN‑Guest | 1010 | BYOD, visiteurs |
| 20 | VN‑Corp | 1020 | Employés |
| 30 | VN‑IoT | 1030 | Caméras, capteurs |
| 40 | VN‑DC | 1040 | Serveurs DC |
| 50 | VN‑Guest‑WiFi | 1050 | Wi‑Fi invité |

```bash
! Sur un Edge Switch
conf t
  vlan 10
    name VN-Guest
    vn-segment 1010
  vlan 20
    name VN-Corp
    vn-segment 1020
  vlan 30
    name VN-IoT
    vn-segment 1030
  vlan 40
    name VN-DC
    vn-segment 1040
  vlan 50
    name VN-Guest-WiFi
    vn-segment 1050
exit
```

### 6.2 Configuration du **Underlay** (OSPF)

```bash
conf t
  router ospf 1
    router-id 10.0.0.1
    passive-interface default
    no passive-interface GigabitEthernet1/0/1
    network 10.0.0.0 0.0.255.255 area 0
  exit
  interface Vlan1
    ip address 10.0.0.2 255.255.255.0
    no shutdown
  exit
end
write memory
```

### 6.3 BGP EVPN (optionnel – pour inter‑fabric)

```bash
conf t
  router bgp 65001
    bgp log-neighbor-changes
    address-family l2vpn evpn
      neighbor 10.0.0.1 activate
      neighbor 10.0.0.1 route-reflector-client
    exit-address-family
  exit
end
```

### 6.4 Policies – ACLs (Cisco IOS‑XE)

```bash
ip access-list extended ACL-Guest
  permit ip any any log
  deny   ip any 192.168.20.0 0.0.0.255
  deny   ip any 192.168.30.0 0.0.0.255
  permit ip any any
exit

ip access-list extended ACL-Corp
  permit ip any any
exit
```

### 6.5 Mapping des ACL aux VN via DNA Center

```bash
# API call pour attacher l'ACL
curl -k -u admin:pwd -X POST \
  https://<DNA>/dna/