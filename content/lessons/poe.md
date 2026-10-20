# Power over Ethernet (PoE) – Cours intensif pour Administrateur Réseau Senior  
*Version CCIE‑Level – 2026*  

---

## Table des matières
| # | Section |
|---|---------|
| 1 | Introduction & Historique |
| 2 | Normes IEEE 802.3 (AF, AT, BT, UPOE, 4‑Pair) |
| 3 | Architecture PoE – PSE vs PD |
| 4 | Classes de puissance & budgets |
| 5 | Topologies et câblage (1‑Pair, 4‑Pair, Mid‑Span, End‑Span) |
| 6 | Implémentations Cisco (Catalyst, Nexus, Meraki, ISR) |
| 7 | Configuration Cisco – CLI détaillée |
| 8 | Vérification & monitoring (Cisco, Linux, SNMP, LLDP) |
| 9 | Sécurité et bonnes pratiques |
|10 | Dimensionnement & calculs de budget |
|11 | PoE dans les data‑centers & les environnements industriels |
|12 | Comparatif des solutions (Cisco, Juniper, Aruba, Ubiquiti) |
|13 | Atelier de dépannage – Scénarios réels |
|14 | Annexes : ASCII diagrams, scripts, références |

---

## 1. Introduction & Historique

Le **Power over Ethernet (PoE)** permet d’alimenter des équipements terminaux (IP phones, caméras, points d’accès Wi‑Fi, contrôleurs d’accès, capteurs IoT, etc.) via le même câble Ethernet qui transporte les données.  

- **1995‑1999** : Premiers prototypes propriétaires (Cisco Power over Ethernet, HP Power over Ethernet).  
- **2003** : Publication de **IEEE 802.3af** (PoE – 15,4 W max).  
- **2009** : **IEEE 802.3at** (PoE+ – 30 W max).  
- **2014‑2018** : **IEEE 802.3bt** (PoE++ / 4‑Pair) – jusqu’à 90 W (Type 4).  
- **2021‑2024** : Extension vers **UPOE** (Cisco Universal PoE) et **PoE over 4‑pair** pour les serveurs d’alimentation haute densité.  

Le PoE a évolué d’une simple commodité à une composante critique d’infrastructures **Edge‑to‑Core**, **IoT**, **Smart‑Building** et **Data‑Center**.

---

## 2. Normes IEEE 802.3 – Vue d’ensemble

| Norme | Alias | Puissance nominale (PSE → PD) | Tension | Courant max (per port) | Paires utilisées | Année de publication |
|-------|-------|-------------------------------|---------|------------------------|------------------|----------------------|
| 802.3af | PoE (Class 0‑4) | 15,4 W (12,95 W disponible) | 44‑57 V | 350 mA | 2 paires (Mode A ou B) | 2003 |
| 802.3at | PoE+ (Class 5‑8) | 30 W (25,5 W disponible) | 50‑57 V | 600 mA | 2 paires (Mode A ou B) | 2009 |
| 802.3bt Type 3 | PoE++ (Class 9‑10) | 60 W (51 W disponible) | 50‑57 V | 960 mA | 4 paires (Mode A/B) | 2014 |
| 802.3bt Type 4 | PoE++ (Class 11‑12) | 90 W (71,5 W disponible) | 50‑57 V | 1,44 A | 4 paires (Mode A/B) | 2018 |
| 802.3bu | PoE over 4‑Pair (2‑pair) | 100 W+ (défini par OEM) | 48‑57 V | >1,5 A | 4 paires (tous) | 2022 (draft) |
| 802.3br | PoE over 4‑Pair (single‑pair) | 15 W (défini) | 15‑36 V | 500 mA | 1 paire | 2023 (draft) |

### Modes d’injection
| Mode | Description | Paires utilisées |
|------|-------------|------------------|
| **Mode A** (End‑Span) | Alimentation injectée sur les mêmes paires que les données (1‑2 & 3‑6). | 1‑2 & 3‑6 |
| **Mode B** (Mid‑Span) | Alimentation injectée sur les paires inutilisées (4‑5 & 7‑8). | 4‑5 & 7‑8 |
| **Mode 4‑Pair** | Utilise les 4 paires pour partager la puissance, réduisant la chute de tension. | 1‑2, 3‑6, 4‑5, 7‑8 |

---

## 3. Architecture PoE – PSE vs PD

```
+-------------------+          +-------------------+
| Power Sourcing   |          | Powered Device    |
| Equipment (PSE)  |<-------->| (PD)              |
|  (Switch, Injector|  PoE     |  (IP Phone, AP)   |
|   ou POE‑midspan) |  Cable   |                   |
+-------------------+          +-------------------+
```

| Élément | Rôle | Fonctions clés |
|---------|------|----------------|
| **PSE (Power Sourcing Equipment)** | Fournit tension & courant | - Détection (Signature, Classification) <br> - Gestion de la puissance (Power Management) <br> - Protection contre court‑circuit & surcharge |
| **PD (Powered Device)** | Consomme la puissance | - Signature (Détection) <br> - Classification (optionnelle) <br> - Négociation de la puissance requise |
| **Mid‑Span (Inline Injector)** | Intermédiaire entre switch non‑PoE et PD | - Convertit le port non‑PoE en PoE <br> - Souvent utilisé pour ajouter du PoE à un réseau existant |
| **End‑Span (Switch PoE)** | Intégré au switch | - Gestion centralisée via SNMP, NetFlow, etc. <br> - Support de la classification et du contrôle de la puissance par VLAN/port |

### Séquence de négociation (IEEE 802.3af/at)

1. **Detection** – PSE applique 2,8 V sur les paires, mesure le courant (≤ 10 mA). Si PD répond, on passe à l’étape suivante.  
2. **Classification** (optionnel) – PSE applique 15,4 V, PD renvoie un **Class ID** (0‑8).  
3. **Power Up** – PSE fournit la tension nominale (44‑57 V) et la puissance selon la classe.  
4. **Power Management** – Le PSE surveille la consommation et peut réduire/éteindre le port en cas de surcharge ou de perte de lien.  

---

## 4. Classes de puissance & budgets

| Classe | Norme | Puissance disponible (W) | Courant max (A) | Utilisation typique |
|--------|-------|--------------------------|-----------------|---------------------|
| 0 | AF | 0,44 | 0,015 | VoIP, capteurs |
| 1 | AF | 3,84 | 0,13 | Téléphones bas de gamme |
| 2 | AF | 6,49 | 0,21 | Caméras analogiques |
| 3 | AF | 12,95 | 0,35 | Caméras IP haute résolution (sans éclairage) |
| 4 | AF | 12,95 | 0,35 | PD non‑PoE (détection) |
| 5 | AT | 15,4 | 0,35 | Caméras IP avec IR, AP légers |
| 6 | AT | 22,5 | 0,5 | Point d’accès Wi‑Fi 802.11ac |
| 7 | AT | 25,5 | 0,6 | Point d’accès Wi‑Fi 802.11ax, téléphones vidéo |
| 8 | AT | 30,0 | 0,6 | Point d’accès haut débit, panneaux LED |
| 9 | BT‑Type 3 | 45,0 | 0,96 | Caméras PTZ, points d’accès 4×4 MIMO |
|10 | BT‑Type 3 | 60,0 | 0,96 | Access‑points 5 GHz + 2,4 GHz, panneaux d’affichage |
|11 | BT‑Type 4 | 71,5 | 1,44 | Points d’accès 8×8 MIMO, panneaux LED haute puissance |
|12 | BT‑Type 4 | 90,0 | 1,44 | Systèmes de vidéoconférence, chargeurs de laptops |

> **Note** : La puissance réellement disponible pour le PD est inférieure à la puissance nominale du PSE à cause de la perte de tension (≈ 2 V) et du facteur de sécurité (80 % de la capacité maximale du PSE).

### Calcul de budget PoE (exemple)

```
Port Power Budget = (Nombre de ports * Puissance nominale) – (Perte de marge de sécurité)
```

Exemple : Switch 48‑ports PoE+ (30 W/port) avec un budget total de 720 W.
- Si 30 ports sont occupés à 25 W chacun → 30 * 25 = 750 W > 720 W → **over‑budget** → activer la **Power Management** (déclassement ou désactivation des ports non‑critiques).

---

## 5. Topologies et câblage

### 5.1 Topologies classiques

```
[Switch PoE]---(Cat5e/6/6a)---[PD]
[Switch]---[Mid‑Span Injector]---(Cat5e/6)---[PD]
```

- **End‑Span** : Le switch intègre le PSE. Moins de latence, gestion centralisée.  
- **Mid‑Span** : Ajout d’un injecteur PoE entre un switch non‑PoE et le PD. Idéal pour la migration.

### 5.2 Câblage recommandé

| Catégorie | Bande passante | Longueur max (m) | Support PoE |
|-----------|----------------|------------------|-------------|
| Cat5e | 100 MHz | 100 | Jusqu’à 30 W (AF/AT) |
| Cat6 | 250 MHz | 100 | Jusqu’à 60 W (BT Type 3) |
| Cat6a | 500 MHz | 100 | Jusqu’à 90 W (BT Type 4) |
| Cat7/8 | 600 MHz‑2 GHz | 100 | 100 W+ (UPOE, 4‑Pair) |

**Règle d’or** : Utiliser toujours la catégorie la plus élevée disponible pour anticiper les besoins futurs (Cat6a ou supérieur).

### 5.3 Schéma ASCII – Insertion de puissance (Mode A vs Mode B)

```
Mode A (End‑Span)                     Mode B (Mid‑Span)
+----------------------+              +----------------------+
|   Switch PoE         |              |   Switch (non‑PoE)   |
|   +----+   +----+    |              |   +----+   +----+    |
|   |TxD+|---|RxD+|---+------------->|---|TxD+|---|RxD+|---+   (Data)
|   |TxD-|---|RxD-|---+------------->|---|TxD-|---|RxD-|---+   (Data)
|   |V+  |---|V+  |---+---+          |   |V+  |---|V+  |---+   (Power)
|   |V-  |---|V-  |---+---+          |   |V-  |---|V-  |---+   (Power)
+----------------------+              +----------------------+

Legend:
TxD/RxD = Data pairs (1‑2, 3‑6)
V+/V-   = Power pairs (Mode‑specific)
```

---

## 6. Implémentations Cisco

| Plateforme | PoE Standard | Ports PoE max | Budget total | Fonctionnalités avancées |
|------------|--------------|---------------|--------------|---------------------------|
| Catalyst 9000 (C9500, C9300) | 802.3bt Type 3/4 + UPOE | 48 (30 W) / 24 (60 W) | 740 W – 1440 W | **Power Management**, **PoE‑PD Classification**, **LLDP‑MED**, **Cisco EnergyWise** |
| Nexus 9000 (N9K‑EX) | 802.3bt Type 3/4 | 48 (30 W) | 1440 W | **VDC‑based power pools**, **Dynamic Power Allocation** |
| Meraki MR Series (AP) | 802.3at (PoE+) + 802.3bt (UPOE) | 8 (30 W) | 240 W | **Cloud‑based power monitoring**, **PoE Scheduler** |
| ISR 4000 (ISR‑4331) | 802.3af/at (Integrated PoE) | 4 (30 W) | 120 W | **WAN‑optimized PoE**, **Embedded Power Management** |
| Catalyst 2960‑Plus | 802.3af | 24 (15,4 W) | 370 W | **Static Power Allocation**, **Port‑based PoE Shutdown** |

### 6.1 Fonctionnalités clés à connaître

- **Power Management** – `power inline never`, `power inline auto`, `power inline static max <W>`  
- **Port‑based PoE Scheduling** – `poe schedule <name> start <hh:mm> stop <hh:mm>` (Meraki)  
- **LLDP‑MED Power TLV** – Permet la découverte de la capacité PD via LLDP.  
- **Cisco EnergyWise** – Collecte de métriques de consommation en temps réel, intégration à Cisco Prime Infrastructure.  

---

## 7. Configuration Cisco – CLI détaillée

### 7.1 Activation globale du PoE (Catalyst 9000)

```text
conf t
  power enable
  power priority high
  power max <budget>   ! ex: power max 1440
exit
```

### 7.2 Configuration d’un port individuel

```text
interface GigabitEthernet1/0/12
  description AP‑Salle-12
  switchport mode access
  switchport access vlan 20
  spanning-tree portfast
  power inline auto          ! négociation automatique (default)
  ! ou pour forcer la puissance maximale
  power inline consumption 30
  power inline max 30
  ! désactiver le PoE sur un port inutilisé
  power inline never
exit
```

### 7.3 Classification et limitation

```text
interface TenGigabitEthernet1/1/1
  power inline consumption 15   ! force 15 W (classe 5)
  power inline police 20        ! limite à 20 W (déclenche alarm si dépasse)
exit
```

### 7.4 PoE Scheduler (Meraki)

```text
poe schedule night‑off start 22:00 stop 06:00
interface GigabitEthernet1/0/24
  poe schedule night‑off
exit
```

### 7.5 Vérification de l’état PoE

```text
show power inline
show power inline module 1
show poe interface GigabitEthernet1/0/12
show poe statistics
```

#### Exemple de sortie (`show power inline`)

```
Interface    Admin  Oper   Power   Device   Class  Voltage  Current   Power
------------ ------ ------ ------- -------- ------ -------- -------- -----
Gi1/0/12     auto   on     15.4W   IP-Phone   3      48.0V    0.32A    15.4W
Gi1/0/13     auto   off    0.0W    n/a        0      0.0V    0.0A     0.0W
...
Total Power   :  345.6 Watts
Power Budget  :  720.0 Watts
```

### 7.6 Linux – Vérification du PoE via `ethtool` (pour les NIC compatibles)

```bash
# Vérifier la prise en charge du PoE
ethtool -