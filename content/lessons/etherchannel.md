# Cours intensif : Agrégation de liens (EtherChannel / LACP)  
**Niveau** : Administrateur Réseau Senior (CCIE)  
**Durée estimée** : 3 h (théorie + labs)  

---  

## 1. Introduction

L’agrégation de liens (Link Aggregation, LA) permet de combiner plusieurs interfaces physiques en un seul lien logique.  
Les bénéfices majeurs :

| Bénéfice | Description |
|----------|-------------|
| **Bande passante** | Multiplication de la capacité (ex. 4 × 1 Gbps = 4 Gbps). |
| **Redondance** | Si une interface tombe, le trafic continue sur les autres. |
| **Équilibrage de charge** | Répartition du trafic selon des algorithmes (src‑dst MAC/IP, TCP/UDP ports, etc.). |
| **Simplification** | Un seul groupe logique à gérer dans les protocoles de routage, ACL, QoS… |

Les deux grands standards :

| Standard | RFC / IEEE | Mode d’opération | Compatibilité |
|----------|------------|------------------|----------------|
| **Static (Propriétaire)** | – | Aucun protocole d’échange, configuration manuelle identique des deux côtés. | Tous les équipements supportant l’agrégation. |
| **LACP (Link Aggregation Control Protocol)** | IEEE 802.3ad (renommé 802.1AX‑2000) | Échange de *LACPDU* (Link Aggregation Control Protocol Data Units) pour négocier, vérifier, et monitorer le groupe. | Cisco, Juniper, HP, Linux, Windows, etc. |
| **PAgP (Port Aggregation Protocol)** | Cisco Proprietary | Échange de *PAgPDU* (protocole propriétaire) – similaire à LACP mais uniquement Cisco. | Cisco uniquement. |

---

## 2. Principes fondamentaux de l’agrégation

### 2.1. Conditions de base (Cisco)

| Condition | Valeur attendue |
|-----------|-----------------|
| **Type d’interface** | Identique (ex. GigabitEthernet, TenGigabitEthernet). |
| **Vitesse & Duplex** | Identiques sur toutes les interfaces du groupe. |
| **Mode de trunk** | Tous en *trunk* ou tous en *access* (pas de mix). |
| **VLANs autorisés** | Identiques (ou aucun VLAN sur les ports *access*). |
| **MTU** | Identique (important pour les L3‑VPN). |
| **Spanning‑Tree** | Tous les ports doivent être dans le même état (STP). |
| **Port‑channel number** | Identique sur les deux extrémités. |

### 2.2. Algorithmes d’équilibrage de charge (Cisco)

| Algorithme | Champ(s) utilisé(s) | Exemple d’application |
|------------|--------------------|------------------------|
| **src‑mac** | Adresse MAC source | Flux unicast avec même source MAC → même lien. |
| **dst‑mac** | Adresse MAC destination | Idéal pour plusieurs destinations différentes. |
| **src‑dst‑mac** | MAC source + MAC destination | Distribution plus fine que *src‑mac* ou *dst‑mac*. |
| **src‑dst‑ip** | IP source + IP destination | Bon pour le trafic IP mixte. |
| **src‑dst‑port** | IP src/dst + ports TCP/UDP | Meilleur pour les serveurs web (HTTP/HTTPS). |
| **src‑dst‑ip‑port** | Combinaison complète | Distribution quasi‑aléatoire, recommandé pour les data‑center. |

> **Note** : Sur les commutateurs Nexus, l’algorithme par défaut est *src‑dst‑ip‑port* (hash 32 bits). Sur les Catalyst classiques, c’est *src‑dst‑mac*.

---

## 3. Architecture et topologies courantes

### 3.1. Topologie simple – deux switches

```
      +-------------------+          +-------------------+
      |  Switch A (CISCO) |          |  Switch B (CISCO) |
      |  Port‑Channel 10  |<========>|  Port‑Channel 10  |
      |  (LACP)           |          |  (LACP)           |
      +-------------------+          +-------------------+
          |  |  |  |                     |  |  |  |
          Gi0/1 Gi0/2 Gi0/3 Gi0/4      Gi0/1 Gi0/2 Gi0/3 Gi0/4
```

### 3.2. Topologie *Multi‑Chassis EtherChannel* (MEC) – Cisco Nexus 7000/9000

```
          +-------------------+       +-------------------+
          |  Nexus 7000 (A)   |       |  Nexus 7000 (B)   |
          |  vPC Domain 1    |       |  vPC Domain 1    |
          +-------------------+       +-------------------+
               |      |                     |      |
               |      |  (vPC Peer‑Link)    |      |
               +------|---------------------|------+
                      |                     |
               +------+-----+         +-----+------+
               |  Server 1  |         |  Server 2  |
               |  Bond0 (LACP)        |  Bond0 (LACP) |
               +------------+         +------------+
```

*Le **vPC** (Virtual Port‑Channel) permet d’obtenir une agrégation redondante entre deux chassis, tout en évitant les boucles STP.*

### 3.3. Agrégation *Cross‑Vendor* – Cisco ↔ Linux

```
  Cisco Switch (LACP)               Linux Server (bonding)
  +-------------------+            +-------------------+
  |  Port‑Channel 5   |<==========>|  bond0 (mode 4)   |
  +-------------------+            +-------------------+
      |  |  |  |                       eth0 eth1 eth2 eth3
```

---

## 4. Implémentation Cisco IOS

### 4.1. Configuration d’un EtherChannel **statique** (mode *on*)

```
interface range GigabitEthernet0/1 - 4
  switchport mode trunk
  channel-group 1 mode on
  exit

interface Port-channel1
  switchport mode trunk
  spanning-tree portfast trunk
  exit
```

*Toutes les interfaces du groupe doivent être configurées exactement de la même façon.*

### 4.2. Configuration d’un EtherChannel **LACP** (mode *active*/*passive*)

```
interface range GigabitEthernet0/1 - 4
  switchport mode trunk
  channel-group 10 mode active   ! ou mode passive sur le second switch
  exit

interface Port-channel10
  switchport mode trunk
  lacp system-priority 100
  lacp max-bundle 8
  exit
```

#### 4.2.1. Vérification

| Commande | Description |
|----------|-------------|
| `show etherchannel summary` | Vue synthétique du groupe (Po, membres, protocole). |
| `show etherchannel 10 detail` | Détails du groupe : état LACP, timers, flags. |
| `show lacp neighbor` | Voisins LACP détectés (port, sys‑prio, port‑prio). |
| `show spanning-tree vlan <vlan-id>` | Vérifie que le Po apparaît comme *Root*/*Designated* selon STP. |

#### 4.2.2. Exemple de sortie (`show etherchannel summary`)

```
Group  Port-channel  Protocol  Member Ports
------+-------------+----------+----------------------------
10     Po10         LACP      Gi0/1(P)  Gi0/2(P)  Gi0/3(P)  Gi0/4(P)
```

*Le **P** indique que le port est **participating**.*

### 4.3. Configuration d’un EtherChannel **PAgP** (Cisco‑only)

```
interface range GigabitEthernet0/1 - 4
  switchport mode trunk
  channel-group 20 mode desirable   ! ou mode auto sur le second switch
  exit

interface Port-channel20
  switchport mode trunk
  exit
```

> **Avertissement** : PAgP n’est pas recommandé dans les environnements multi‑vendor car il est propriétaire.

### 4.4. Paramètres avancés

| Paramètre | Commande | Valeur par défaut | Usage |
|-----------|----------|-------------------|-------|
| **LACP System‑Priority** | `lacp system-priority <value>` | 32768 | Influence le rôle de *system* (master) dans le groupe. |
| **LACP Port‑Priority** | `lacp port-priority <value>` (dans `interface`) | 32768 | Décide quel port sera désélectionné en cas de surcharge. |
| **LACP Max‑Bundle** | `lacp max-bundle <N>` | 8 (ou 16 selon plateforme) | Limite le nombre de liens actifs dans le groupe. |
| **Load‑Balancing** | `port-channel load-balance <mode>` (global) | src‑dst‑mac | Ajuste l’algorithme d’équilibrage. |
| **Graceful‑Shutdown** | `channel-group <id> mode active graceful` | N/A | Permet de retirer un lien sans interruption (NX‑OS). |

---

## 5. Implémentation Linux – Bonding Driver

### 5.1. Modes de bonding (RFC 802.3ad)

| Mode | Description | Utilisation typique |
|------|-------------|---------------------|
| **0 (balance‑rr)** | Round‑Robin (trunking) – distribution séquentielle. | Pas recommandé (pas de redondance de lien). |
| **1 (active‑backup)** | Un seul lien actif, les autres en veille. | Redondance simple, aucune agrégation de bande passante. |
| **2 (balance‑xor)** | XOR basé sur src/dst MAC. | Compatibilité avec certains switches non‑LACP. |
| **3 (broadcast)** | Envoie les paquets sur tous les liens. | Utilisé pour la redondance de diffusion. |
| **4 (802.3ad LACP)** | Agrégation dynamique via LACP. | Recommandé pour la plupart des data‑center. |
| **5 (balance‑tlb)** | Transmit Load Balancing – basé sur trafic sortant. | Pas besoin de switch LACP, mais nécessite support du driver. |
| **6 (balance‑alb)** | Adaptive Load Balancing – TX + RX load‑balancing. | Pas besoin de switch LACP, mais pas de support VLAN trunk. |

### 5.2. Configuration d’un bond en mode **4 (LACP)** – Debian/Ubuntu

1. **Chargement du module**  

   ```bash
   modprobe bonding mode=4 miimon=100 lacp_rate=1
   ```

2. **Fichier `/etc/network/interfaces`**  

   ```text
   auto bond0
   iface bond0 inet static
       address 192.168.10.10
       netmask 255.255.255.0
       gateway 192.168.10.1
       dns-nameservers 8.8.8.8 8.8.4.4
       bond-slaves eth0 eth1 eth2 eth3
       bond-mode 802.3ad
       bond-miimon 100
       bond-lacp-rate fast
       bond-xmit_hash_policy layer3+4   # src‑dst‑ip‑port
   ```

3. **Redémarrage**  

   ```bash
   ifdown eth0 && ifdown eth1 && ifdown eth2 && ifdown eth3
   ifup bond0
   ```

4. **Vérification**  

   ```bash
   cat /proc/net/bonding/bond0
   ```

   Exemple de sortie :

   ```
   Ethernet Channel Bonding Driver: v3.7.1 (April 30, 2020)

   Bonding Mode: IEEE 802.3ad Dynamic link aggregation
   Transmit Hash Policy: layer3+4
   MII Status: up
   MII Polling Interval (ms): 100
   Up Delay (ms): 0
   Down Delay (ms): 0

   802.3ad info:
       Aggregator ID: 2
       Number of ports: 4
       Actor Key: 1
       Partner Key: 2
       Partner MAC Address: 00:1a:2b:3c:4d:5e

   Slave Interface: eth0
   MII Status: up
   Speed: 1000 Mbps
   Duplex: full
   Link Failure Count: 0
   Permanent HW addr: 00:11:22:33:44:55
   Aggregator ID: 2

   … (repeat for eth1‑eth3) …
   ```

### 5.3. Commandes de diagnostic Linux

| Commande | Objectif |
|----------|----------|
| `cat /proc/net/bonding/bond0` | État complet du bond, LACPDU, agrégateur. |
| `ip -d link show bond0` | Détails du bond (mode, hash policy). |
| `teamdctl team0 state` (si *team* driver) | État du groupe *team*. |
| `tcpdump -i bond0 -e -nn -vv` | Capture des LACPDU (type 0x8809). |
| `ethtool -S eth0` | Statistiques de chaque NIC (erreurs, collisions). |

---

## 6. Conception avancée

### 6.1. Dimensionnement et limites

| Plateforme | Max. Lien par Po | Max. Po par Switch | Max. LACP Partners | Commentaire |
|------------|------------------|--------------------|--------------------|-------------|
| Cisco Catalyst 9500 | 8 (16 en 48‑port) | 128 | 2 (local + remote) | Utiliser *port‑channel load‑balance* adapté. |
| Cisco Nexus 9000 (NX‑OS) | 64 (en mode vPC) | 512 | 2 (vPC pair) | vPC nécessite un *peer‑link* dédié. |
| Juniper EX Series | 8 | 256 | 2 | LACP *active* par défaut. |
| Linux bonding (kernel ≥ 5.10) | 32 (soft limit) | N/A | 1 (local) | Le nombre réel dépend de la RAM et du driver NIC. |

### 6.2. Interaction avec STP / RSTP / MSTP

* **STP** considère chaque **Port‑Channel** comme un seul port.  
* **BPDU Guard** : à activer sur les ports *access* qui ne doivent pas devenir partie d’un Po.  
* **Loop Guard** : utile lorsqu’un Po est configuré en *on* (pas de négociation).  

### 6.3. QoS et Policing sur un Po

| Niveau | Action |
|--------|--------|
| **Interface physique** | `mls qos trust dscp` – chaque NIC hérite du trafic. |
| **Port‑Channel** | `mls qos trust dscp` + `policy-map` appliquée sur le Po. |
| **Service‑Policy** | `service-policy output <policy>` sur le Po (débit, shaping). |

> **Bon à savoir** : le *hash* d’équilibrage doit être cohérent avec la politique QoS (ex. : si QoS s’appuie sur les ports TCP, choisissez *src‑dst‑port*).

### 6.4. Sécurité

| Risque | Mitigation |
|--------|------------|
| **LACP spoofing** (un attaquant injecte de fausses LACPDU) | Activer `lacp system-id <mac>` fixe et filtrer les LACPDU avec ACL MAC‑type 0x8809. |
| **Storm de broadcast** sur un Po mal configuré | Limiter le *storm‑control* sur le Po (`storm-control broadcast level 1.00 0.90`). |
| **Mauvaise négociation** (mix static/LACP) | Utiliser `show etherchannel summary` pour détecter les mismatches. |
| **Fail‑over non‑graceful** | Configurer `lacp graceful-recovery` (NX‑OS) ou