# Cours Intensif – VTP et Gestion des VLANs  
**Niveau : Administrateur Réseau Senior (CCIE)**  

---

## Table des matières
| # | Section | Pages approximatives |
|---|---------|----------------------|
| 1 | Introduction générale à VTP & VLANs | 1 |
| 2 | Architecture du VLAN – Modèle 802.1Q | 2 |
| 3 | VTP – Concepts, modes et fonctionnement | 4 |
| 4 | Comparaison VTP vs. alternatives (PVST+, Rapid‑PVST+, MST) | 7 |
| 5 | Conception d’une topologie multi‑site avec VTP | 9 |
| 6 | Configuration avancée Cisco IOS | 12 |
| 7 | Configuration sous Linux (bridge, vlan, openvswitch) | 15 |
| 8 | Sécurité et bonnes pratiques | 18 |
| 9 | Dépannage – Atelier pratique | 21 |
|10 | Annexes (scripts, références, FAQ) | 26 |

> **Objectif** : Maîtriser le déploiement, l’optimisation et le dépannage de VTP et des VLANs dans des environnements d’entreprise complexes (datacenters, campus, WAN MPLS).  

---

## 1. Introduction générale à VTP & VLANs  

### 1.1 Pourquoi les VLANs ?  
- **Segmentation logique** du réseau L2, réduction des broadcasts.  
- **Isolation de la sécurité** (ex. voix vs. données).  
- **Facilitation de la mobilité** des hôtes (VM, postes, IoT).  

### 1.2 Le rôle de VTP (VLAN Trunking Protocol)  
- Protocole propriétaire Cisco (RFC 2005) qui **propagation automatiquement la base de données VLAN** à travers les trunks.  
- **Évite les incohérences** manuelles entre les commutateurs.  

### 1.3 Scope du cours  
- **VTPv1, VTPv2, VTPv3** (authentification, pruning, version 3).  
- **Intégration avec 802.1Q** (tagging, native VLAN).  
- **Interopérabilité** avec les solutions non‑Cisco (MST, GVRP).  

---

## 2. Architecture du VLAN – Modèle 802.1Q  

### 2.1 Trunk vs. Access  
```
+-----------------+                     +-----------------+
|  Switch A       |                     |  Switch B       |
| (Access Port)  |---(Access)--------->| (Access Port)  |
+-----------------+                     +-----------------+

+-----------------+                     +-----------------+
|  Switch A       |---(Trunk)-----------|  Switch B       |
| (Trunk Port)   | 802.1Q Tagging      | (Trunk Port)   |
+-----------------+                     +-----------------+
```

### 2.2 Le champ VLAN ID (VID)  
- 12 bits → **4094** VLANs (0 et 4095 réservés).  
- **VID 1** = VLAN native (non‑taguée par défaut).  

### 2.3 Tagging et Untagging – ASCII Diagram  

```
+-----------+      Tag (VID 10)      +-----------+
|  Host A   |----------------------->|  Switch   |
| (PC)      |   (untagged)           |  (access) |
+-----------+                        +-----------+
       |                                    |
       | 802.1Q Tag (VID 10)                |
       v                                    v
+-----------+      Tag (VID 10)      +-----------+
|  Switch   |----------------------->|  Switch   |
| (trunk)   |   (tagged)             | (trunk)   |
+-----------+                        +-----------+
       |                                    |
       | 802.1Q Tag (VID 10)                |
       v                                    v
+-----------+      Untagged          +-----------+
|  Host B   |<-----------------------|  Switch   |
| (Server)  |   (native VLAN 1)      | (access) |
+-----------+                        +-----------+
```

### 2.4 Pruning – Réduction du trafic broadcast  
- **VTP pruning** : le switch supprime les VLANs inutiles sur un trunk.  
- **MST pruning** : plus granulaire, basé sur les instances MST.  

---

## 3. VTP – Concepts, modes et fonctionnement  

### 3.1 Modes de fonctionnement VTP  

| Mode          | Description | Utilisation typique |
|---------------|-------------|---------------------|
| **Server**    | Crée, modifie, supprime les VLANs et les diffuse. | Switchs d’accès/agrégation. |
| **Client**    | Reçoit les informations, ne peut pas créer/modifier. | Switchs de bordure, où l’on veut éviter les changements accidentels. |
| **Transparent**| Ne participe pas à la synchronisation VTP, mais passe les advertisements. | Environnements mixtes ou lorsqu’on veut désactiver VTP sur un switch. |

### 3.2 Versions VTP  

| Version | Caractéristiques clés | Compatibilité |
|---------|-----------------------|---------------|
| **VTPv1** | Pas de support du « trunking pruning ». | Legacy, rarement utilisé. |
| **VTPv2** | Pruning, support du MTU > 1500, meilleure gestion du native VLAN. | Courant sur IOS 12.x+. |
| **VTPv3** | Authentification (MD5, SHA‑256), rôle de serveur/client, support de VLANs privées, capacité à transporter plusieurs domaines VTP. | IOS 15.x+, recommandé pour la sécurité. |

### 3.3 Processus d’élection du **Root Bridge** (pour VTP)  
- Le **switch avec le plus haut numéro de version** devient le **primary server**.  
- En cas d’égalité, le **switch avec le plus haut numéro de priorité** (32768 par défaut) gagne.  
- Si toujours égalité, le **MAC address** le plus élevé l’emporte.  

### 3.4 Fonctionnement du **VTP Advertisement**  

1. **Advertisement interval** (default 5 s) – envoi d’un **VTP summary advertisement**.  
2. **Hold time** (default 15 s) – durée pendant laquelle les informations sont valides.  
3. **Sequence number** – incrémenté à chaque modification de la base VLAN.  

### 3.5 VTP Pruning – Algorithme  

```
1. Switch A (Server) envoie un VTP Summary Advertisement contenant la liste de ses VLANs.
2. Switch B (Client) compare la liste avec ses propres VLANs actifs.
3. Si VLAN X n’est pas présent sur le port trunk, Switch B envoie un VTP Prune Request.
4. Switch A retire VLAN X du trunk pendant le prune interval (default 5 min).
5. Si du trafic apparaît sur VLAN X, un VTP Join Request réactive le trunk.
```

---

## 4. Comparaison VTP vs. alternatives (PVST+, Rapid‑PVST+, MST)

| Fonctionnalité | VTP (v3) | PVST+ | Rapid‑PVST+ | MST |
|----------------|----------|-------|-------------|-----|
| **Protocole propriétaire** | Cisco | Cisco | Cisco | IEEE 802.1s |
| **Spanning‑Tree par VLAN** | Non (utilise STP classique) | Oui (STP par VLAN) | Oui (RSTP par VLAN) | Oui (MST instance) |
| **Convergence** | 30–50 s | 30–50 s | < 10 s | < 10 s (dépend de la topologie) |
| **Pruning** | Oui (v2/v3) | Oui (PVST+) | Oui | Oui (MST) |
| **Sécurité** | Auth MD5/SHA, rôle serveur/client (v3) | Auth MD5 | Auth MD5 | Aucun natif, dépend du contrôle d’accès |
| **Scalabilité** | Jusqu’à 4094 VLANs, mais limité à un domaine VTP | Un domaine STP par VLAN (limite CPU) | Même que PVST+ | Multi‑instance, plus efficace pour > 100 VLANs |
| **Interopérabilité** | Faible avec non‑Cisco | Faible | Faible | Excellente (standard IEEE) |

**Quand choisir quoi ?**  
- **Datacenter / Campus large** : MST ou Rapid‑PVST+ (performance, standard).  
- **Environnement pure Cisco, petite à moyenne taille** : VTPv3 + PVST+ (simplicité).  
- **Mise à jour progressive** : VTPv3 en mode Transparent sur les nouveaux switches, MST sur le cœur.

---

## 5. Conception d’une topologie multi‑site avec VTP  

### 5.1 Exemple de topologie  

```
                +-------------------+      +-------------------+
                |   Core Switch 1   |------|   Core Switch 2   |
                | (VTP Server v3)  |      | (VTP Server v3)  |
                +-------------------+      +-------------------+
                         |                        |
          +--------------+--------------+---------+--------------+
          |                             |                        |
+-------------------+          +-------------------+    +-------------------+
|  Distribution A   |          |  Distribution B   |    |  Distribution C   |
| (VTP Client)      |          | (VTP Client)      |    | (VTP Transparent)|
+-------------------+          +-------------------+    +-------------------+
          |                             |                        |
   +------+-----+                +------+-----+          +------+-----+
   | Access Sw  |                | Access Sw  |          | Access Sw  |
   | (Server)   |                | (Client)   |          | (Transparent)|
   +------------+                +------------+          +------------+
```

- **Core** : VTP Server (v3) avec authentification MD5.  
- **Distribution** : VTP Client, hérite de la base VLAN du Core.  
- **Access** : VTP Transparent pour éviter la propagation des VLANs inutiles.  

### 5.2 Design des VLANs (exemple)  

| VLAN ID | Nom | Type | Utilisation | Subnet | Tag |
|---------|-----|------|-------------|--------|-----|
| 10 | VOICE | Data | Téléphonie IP | 10.10.10.0/24 | 10 |
| 20 | DATA | Data | Poste de travail | 10.10.20.0/24 | 20 |
| 30 | MGMT | Data | Gestion réseau | 10.10.30.0/24 | 30 |
| 40 | GUEST | Data | Accès invité | 10.10.40.0/24 | 40 |
| 50 | DMZ | Data | Serveurs exposés | 10.10.50.0/24 | 50 |
| 99 | NATIVE | Data | VLAN native (untagged) | – | 1 (native) |
| 100 | VTP_PRUNE | Data | VLAN dédié au pruning (optionnel) | – | 100 |

### 5.3 Calcul du **VTP Prune Interval**  

```
Prune interval = (Hold time – Advertisement interval) / 2
= (15 s – 5 s) / 2 = 5 s
```
=> Le switch attend 5 s avant de retirer un VLAN du trunk.  

---

## 6. Configuration avancée Cisco IOS  

### 6.1 Activation du VTPv3 avec authentification  

```text
Switch(config)# vtp version 3
Switch(config)# vtp domain MON_DOMAINE
Switch(config)# vtp mode server
Switch(config)# vtp password secret 7 12345678   ! MD5 secret
Switch(config)# vtp authentication mode md5
Switch(config)# vtp authentication key-chain VTP_KEYS
Switch(config)# key chain VTP_KEYS
Switch(config-keychain)# key 1
Switch(config-keychain-key)# key-string MonMotDePasseVTP
Switch(config-keychain-key)# accept-lifetime 00:00:00 Jan 01 2025 00:00:00 Jan 01 2035
Switch(config-keychain)# exit
```

### 6.2 Configuration d’un trunk avec VLAN pruning  

```text
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20,30,40,50
Switch(config-if)# vtp pruning
Switch(config-if)# spanning-tree vlan 10 priority 4096
Switch(config-if)# spanning-tree vlan 20 priority 8192
Switch(config-if)# no shutdown
```

### 6.3 VLAN Private (Isolated) – Exemple  

```text
Switch(config)# vlan 200
Switch(config-vlan)# name PRIVATE_SALES
Switch(config-vlan)# private-vlan primary
Switch(config-vlan)# private-vlan association 201,202
Switch(config)# vlan 201
Switch(config-vlan)# name PRIVATE_SALES_ISOLATED
Switch(config-vlan)# private-vlan isolated
Switch(config)# vlan 202
Switch(config-vlan)# name PRIVATE_SALES_PROMISCUOUS
Switch(config-vlan)# private-vlan promiscuous
Switch(config)# interface range GigabitEthernet0/10-12
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 201
Switch(config-if-range)# exit
Switch(config)# interface GigabitEthernet0/13
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 202
```

### 6.4 Vérification & Dépannage  

| Commande | Objectif |
|----------|----------|
| `show vtp status` | État global VTP (version, mode, domain). |
| `show vtp counters` | Statistiques d’advertisements, prune, join. |
| `show vtp pruning` | VLANs actuellement pruned sur chaque trunk. |
| `show spanning-tree vlan <id>` | Priorité, root, états des ports. |
| `show interface trunk` | VLANs autorisés, natifs, état du trunk. |
| `debug vtp events` | Traces en temps réel (à activer avec précaution). |

---

## 7. Configuration sous Linux – Bridge, VLAN et Open vSwitch  

### 7.1 Création de VLANs sur une interface physique (ex. eth0)  

```bash
# Ajouter le module 8021q si nécessaire
sudo modprobe 8021q

# Créer le VLAN 10
sudo ip link add link eth0 name eth0.10 type vlan id 10
sudo ip addr add 10.10.10.1/24 dev eth0.10
sudo ip link set dev eth0.10 up

# Créer le VLAN 20
sudo ip link add link eth0 name eth0.20 type vlan id 20
sudo ip addr add 10.10.20.1/24 dev eth0.20
sudo ip link set dev eth0.20 up
```

### 7.2 Bridge Linux avec plusieurs VLANs (ex. br0)  

```bash
# Créer le bridge
sudo brctl addbr br0
sudo ip link set dev br0 up

# Attacher les interfaces VLAN au bridge
sudo brctl addif br0 eth0.10
sudo brctl addif br0 eth0.20

# Activer le bridge
sudo ip link set dev br0 up
```

### 7.3 Open vSwitch (OVS) – Exemple de configuration d’un trunk  

```bash
# Installer OVS (Debian/Ubuntu)
sudo apt-get install openvswitch-switch

# Créer le bridge OVS
sudo ovs-vsctl add-br ovs-br0

# Ajouter le port physique en mode trunk
sudo ovs-vsctl add-port ovs-br0 eth0 \
    -- set Interface eth0 type=internal \
    -- set Port eth0 tag=0 \
    -- set Port eth0 trunks=10,20,30

# Créer des interfaces VLAN internes (optionnel)
sudo ovs-vsctl add-port ovs-br0 vlan10 -- set Interface vlan10 type=vlan tag=10
sudo ovs-vsctl add-port ovs-br0 vlan20 -- set Interface vlan20 type=vlan tag=20
```

### 7.4 Vérification OVS  

```bash
sudo ovs-vsctl show
sudo ovs-ofctl dump-ports-desc ovs-br0
```

---

## 8. Sécurité et bonnes pratiques  

| Domaine | Recommandation | Raison |
|---------|----------------|--------|
| **Authentification VTP** | Utiliser VTPv3 avec MD5 ou SHA‑256, clé de chaîne. | Empêche les injections de VLANs. |
| **Native VLAN** | Ne jamais laisser la VLAN 1 comme native. Utiliser VLAN 999 ou 99. | Évite les attaques VLAN hopping. |
| **Pruning** | Activer le pruning sur tous les trunks, vérifier les listes de VLAN autorisés. | Réduit le trafic inutile et les vecteurs d’attaque. |
| **BPDU Guard / Root Guard** | Configurer sur ports d’accès. | Empêche le basculement du root bridge par un hôte. |
| **Port Security** | Limiter le nombre d’adresses MAC, activer sticky MAC. | Contre les attaques de type MAC flooding. |
| **ACLs sur trunks** | Filtrer les VLANs non‑utilisés (ex. `deny ip any any vlan 999`). | Sépare les flux de gestion et de data. |
| **Monitoring** | Syslog,