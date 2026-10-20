# Sécurité au Niveau 2 (L2) – ARP Spoofing & DHCP Snooping  
**Niveau : Administrateur Réseau Senior (CCIE‑Ready)**  
**Durée estimée : 2 jours intensifs (≈ 16 h)**  

---  

## Table des matières
| # | Section | Durée approximative |
|---|---------|---------------------|
| 1 | Introduction & concepts fondamentaux | 1 h |
| 2 | ARP – fonctionnement, vulnérabilités | 2 h |
| 3 | ARP Spoofing / Poisoning – mécanismes d’attaque | 2 h |
| 4 | Contre‑mesures L2 – Static ARP, Dynamic ARP Inspection (DAI) | 3 h |
| 5 | DHCP – fonctionnement et points faibles | 1,5 h |
| 6 | DHCP Snooping – architecture, configuration | 3 h |
| 7 | Interaction DAI ↔ DHCP Snooping – trust & untrust | 1 h |
| 8 | Atelier pratique – Lab de détection et mitigation | 4 h |
| 9 | Guide de dépannage avancé | 2 h |
|10 | Bonnes pratiques, checklist & références | 1 h |

> **Objectif** : Maîtriser les mécanismes d’attaque L2 les plus répandus, implémenter les solutions Cisco (DAI, DHCP Snooping, IP Source Guard, etc.) et être capable de diagnostiquer, isoler et corriger un incident en moins de 30 minutes.

---  

## 1. Introduction & concepts fondamentaux  

### 1.1 Pourquoi la couche 2 est critique  
- **Broadcast domain** : Tous les hôtes d’un VLAN partagent le même segment L2, les protocoles de découverte (ARP, DHCP) utilisent des trames broadcast.  
- **Absence d’authentification native** : Ethernet ne fournit pas d’authentification des sources, les commutateurs se basent sur les adresses MAC uniquement.  
- **Impact en cascade** : Une compromission L2 peut affecter le routage (L3) via le vol d’IP, les attaques DDoS internes, la perte de confidentialité (sniffing) et la compromission de services critiques (voIP, SCADA).

### 1.2 Terminologie clé  

| Terme | Définition |
|-------|------------|
| **MAC address** | Adresse physique 48 bits, unique (ou parfois spoofée). |
| **ARP (Address Resolution Protocol)** | Résolution d’une adresse IPv4 → MAC via requêtes broadcast. |
| **DHCP (Dynamic Host Configuration Protocol)** | Attribution dynamique d’IP, masque, passerelle, DNS, etc. |
| **DAI (Dynamic ARP Inspection)** | Filtrage des réponses ARP en fonction d’une base de données d’associations IP‑MAC fiables. |
| **DHCP Snooping** | Filtrage des messages DHCP, construction d’une base de données “binding” (MAC‑IP‑VLAN‑Port). |
| **IP Source Guard** | Bloque les paquets dont l’adresse IP source ne correspond pas à la table DHCP Snooping/ARP. |
| **Trust/Untrust port** | Port configuré comme « trusted » autorise les messages DHCP/ARP, les autres sont filtrés. |

---  

## 2. ARP – fonctionnement, vulnérabilités  

### 2.1 Cycle de vie d’une requête ARP  

```
+----------+        Broadcast ARP Request (who-has 10.0.0.5?)        +----------+
| Host A   | -----------------------------------------------------> | Host B   |
+----------+                                                       +----------+
        ^                                                               |
        |  Unicast ARP Reply (is-at 00:11:22:33:44:55)                |
        +-----------------------------------------------------------+
```

1. **Host A** envoie une trame Ethernet `ff:ff:ff:ff:ff:ff` (broadcast) contenant un **ARP request**.  
2. Tous les hôtes du VLAN reçoivent la trame.  
3. **Host B** (possédant l’IP cible) répond en **unicast** avec son adresse MAC.  

### 2.2 Table ARP (Cache)  

| Champ | Description |
|-------|-------------|
| **IP address** | Adresse IPv4 recherchée. |
| **MAC address** | Adresse physique résolue. |
| **Type** | *Dynamic* (appris) ou *Static* (configuré). |
| **TTL** | Temps de vie (généralement 60 s à 20 min). |

### 2.3 Points faibles  

| Vulnerability | Why it exists |
|---------------|----------------|
| **Statelessness** | ARP ne possède aucun mécanisme d’authentification ou de chiffrement. |
| **Broadcast nature** | Tout hôte peut écouter et répondre. |
| **Cache poisoning** | Un attaquant peut injecter une entrée fausse dans le cache ARP d’un hôte. |
| **Gratuitous ARP** | Utilisé légitimement (IP takeover) mais exploitable pour masquer des changements. |

---  

## 3. ARP Spoofing / Poisoning – mécanismes d’attaque  

### 3.1 Scénario d’attaque classique  

```
[Attacker]---[Switch]---[Victim]---[Server]
      |                     |
      +---[Gateway]---------+
```

1. L’attaquant envoie **des réponses ARP non sollicitées** (ARP reply) indiquant que l’adresse MAC de l’attaquant correspond à l’IP de la passerelle.  
2. Le **victim** met à jour son cache ARP → trafic destiné à la passerelle passe par l’attaquant (Man‑in‑the‑Middle).  
3. L’attaquant peut **forward** le trafic (transparent) ou **intercepter** (sniffing, modification).  

### 3.2 Techniques d’injection  

| Technique | Commande Linux (exemple) | Description |
|-----------|--------------------------|-------------|
| **arpspoof (dsniff)** | `arpspoof -i eth0 -t 10.0.0.10 10.0.0.1` | Envoie des ARP reply falsifiées à la cible. |
| **ettercap (ARP poisoning)** | `ettercap -T -q -M arp:remote /10.0.0.10// /10.0.0.1//` | Mode MITM complet, redirige tout le trafic. |
| **scapy (Python)** | `send(ARP(op=2, pdst='10.0.0.10', psrc='10.0.0.1', hwsrc='aa:bb:cc:dd:ee:ff'))` | Script personnalisable pour automatiser le spoofing. |

### 3.3 Conséquences  

- **Interception de données sensibles** (login, credentials).  
- **Déni de service** (si l’attaquant ne forward pas).  
- **Redirection DNS** → injection de sites malveillants.  
- **Compromission de certificats** (SSL stripping).  

---  

## 4. Contre‑mesures L2 – Static ARP & Dynamic ARP Inspection (DAI)  

### 4.1 ARP statique (Cisco)  

```bash
interface GigabitEthernet0/1
  ip address 10.0.0.2 255.255.255.0
  arp 10.0.0.2 0011.2233.4455 ARPA
```

- **Avantages** : aucune dépendance à DAI, simple à déployer sur petits réseaux.  
- **Limites** : difficile à maintenir, ne scale pas, ne protège contre les attaques internes non‑authorisées.  

### 4.2 Dynamic ARP Inspection (DAI) – principe  

1. **DHCP Snooping** crée une base de données *binding* (MAC‑IP‑VLAN‑Port).  
2. DAI intercepte chaque **ARP request/reply**.  
3. Vérifie que l’association (IP↔MAC) correspond à la table DHCP Snooping **ou** à une entrée ARP statique.  
4. Si non‑conforme → **drop** + log (syslog, SNMP trap).  

### 4.3 Configuration DAI (Cisco IOS XE)  

```bash
! 1️⃣ Activer DHCP Snooping (prérequis)
ip dhcp snooping
ip dhcp snooping vlan 10,20,30

! 2️⃣ Marquer les ports « trusted » (généralement uplinks)
interface TenGigabitEthernet1/0/1
  ip dhcp snooping trust
  ip arp inspection trust   ! si l’up‑link doit transmettre ARP non‑filtrées

! 3️⃣ Configurer DAI sur les VLANs
ip arp inspection vlan 10
ip arp inspection vlan 20
ip arp inspection vlan 30

! 4️⃣ Optionnel : définir le taux maximal d’ARP (anti‑storm)
interface GigabitEthernet0/2
  ip arp inspection limit rate 100

! 5️⃣ Activer les logs
logging host 192.0.2.10
logging trap warnings
```

#### 4.3.1 Table de vérification DAI  

| Champ | Source |
|-------|--------|
| **IP** | DHCP Snooping binding, ARP static entry, manual binding (`ip arp inspection verify mac-address`) |
| **MAC** | Same as above |
| **VLAN** | VLAN de l’interface où la trame a été reçue |
| **Port** | Port de réception (trusted vs untrusted) |

### 4.4 Interaction avec IP Source Guard  

```bash
interface GigabitEthernet0/5
  ip verify source
```

- **IP Source Guard** utilise la même table binding que DAI pour bloquer les paquets IP dont l’adresse source ne correspond pas à la table.  
- **Couplage recommandé** : DAI + IP Source Guard + DHCP Snooping = **tripwire L2**.

---  

## 5. DHCP – fonctionnement et points faibles  

### 5.1 Cycle DHCP (DORA)  

```
+-----------------+      +-------------------+      +-----------------+
| Client (Host)   | ---> | DHCP Discover    | ---> | DHCP Server     |
+-----------------+      +-------------------+      +-----------------+
          ^                     ^                         |
          |                     |                         v
   DHCP Offer <--- DHCP Request <--- DHCP ACK (IP lease)
```

1. **Discover** (broadcast) – le client cherche un serveur.  
2. **Offer** – le serveur propose une adresse.  
3. **Request** – le client accepte l’offre.  
4. **ACK** – le serveur confirme et crée la lease.  

### 5.2 Attaques DHCP classiques  

| Attaque | Méthode | Impact |
|---------|---------|--------|
| **DHCP Starvation** | Envoi massif de requêtes avec MAC aléatoires → épuisement du pool d’adresses. | Nouveaux hôtes ne reçoivent plus d’IP. |
| **Rogue DHCP Server** | Serveur non autorisé répond aux Discover, attribue fausses informations (gateway, DNS). | Redirection du trafic, MITM, perte de connectivité. |
| **DHCP Snooping Bypass** | Port non‑trusted mal configuré, ou utilisation de DHCP Relay. | Contournement de la protection. |

---  

## 6. DHCP Snooping – architecture, configuration  

### 6.1 Concept  

- **Binding table** : `MAC | IP | VLAN | Interface | Lease‑time`.  
- **Trusted ports** : Uplinks, serveurs DHCP légitimes.  
- **Untrusted ports** : Accès client, où les messages DHCP sont filtrés.  

### 6.2 Configuration complète (Cisco IOS XE)  

```bash
! 0️⃣ Activer le service DHCP snooping globalement
ip dhcp snooping
! 1️⃣ Spécifier les VLANs à protéger
ip dhcp snooping vlan 10,20,30

! 2️⃣ Marquer les ports uplink comme trusted
interface TenGigabitEthernet1/0/1
  ip dhcp snooping trust
  description Uplink-to-Core

! 3️⃣ (Optionnel) Limiter le nombre de DHCP packets sur un port (anti‑starvation)
interface GigabitEthernet0/12
  ip dhcp snooping limit rate 10

! 4️⃣ Vérifier la table de binding
show ip dhcp snooping binding
```

#### 6.2.1 Exemple de sortie `show ip dhcp snooping binding`

```
MacAddress          IpAddress        Lease(sec)  Type        VLAN Interface
-----------------   ---------------  ----------  ----------- ---- ----------
0011.2233.4455      10.0.10.25       86400       Dynamic     10   Gi0/5
00aa.bbcc.ddee      10.0.20.12       86400       Dynamic     20   Gi0/12
```

### 6.3 Protection contre le **DHCP Starvation**  

- **Rate‑limit** sur les ports non‑trusted (`ip dhcp snooping limit rate`).  
- **Port security** (MAC‑learning limit).  

```bash
interface GigabitEthernet0/5
  switchport mode access
  switchport access vlan 10
  spanning-tree portfast
  switchport port-security maximum 2
  switchport port-security violation shutdown
```

### 6.4 Gestion des **Relay Agents** (IP Helper)  

- Le **relay** doit être configuré comme **trusted** pour que les réponses DHCP (unicast) soient acceptées.  

```bash
interface TenGigabitEthernet1/0/2
  ip dhcp snooping trust   ! Relay interface
```

---  

## 7. Interaction DAI ↔ DHCP Snooping – trust & untrust  

| Port type | DHCP Snooping | DAI | IP Source Guard |
|-----------|----------------|-----|------------------|
| **Uplink (core)** | `trust` | `trust` | optional (rare) |
| **Access (client)** | `untrusted` (default) | `untrusted` (default) | `enabled` |
| **Rogue DHCP Server** | `untrusted` → bloque les offers | `untrusted` → bloque ARP falsifiées | `blocked` |
| **Server DHCP** | `trust` | `trust` | `optional` |

### 7.1 Diagramme ASCII d’un réseau typique  

```
          +-------------------+      +-------------------+
          |   Core Switch     |------|   Core Switch     |
          +-------------------+      +-------------------+
               |   |  |                  |   |  |
      +--------+   |  +--------+   +------+   |  +--------+
      |            |           |   |            |           |
+-----------+  +-----------+ +-----------+  +-----------+ +-----------+
| Access SW |  | Access SW | | Access SW |  | Access SW | | Access SW |
+-----------+  +-----------+ +-----------+  +-----------+ +-----------+
   |   |          |   |          |   |          |   |
   |   +--- Gi0/5 (VLAN10)   |   +--- Gi0/12 (VLAN20)   |
   |        (Client)        |        (Client)        |
   +--- Gi0/5 (DHCP Snooping untrusted)          |
          (DAI untrusted)                       |
```

---  

## 8. Atelier pratique – Lab de détection et mitigation  

### 8.1 Objectifs du lab  

1. **Déployer** DHCP Snooping, DAI, IP Source Guard sur un commutateur de niveau 2.  
2. **Simuler** une attaque ARP spoofing avec `arpspoof`.  
3. **Observer** le log, les compteurs et la table de binding.  
4. **Corriger** le problème en ajustant les ports trust/untrust.  

### 8.2 Topologie du lab (GNS3 / Cisco Packet Tracer)  

```
[Attacker]---Gi0/2---[SW1]---Gi0/1---[Server DHCP]  
               |               |
               +---Gi0/3---[Victim PC]  
               |
               +---Gi0/4---[Core Switch] (uplink, trusted)
```

- **SW1** : Cisco Catalyst 2960X (IOS 15.2).  
- **Server DHCP** : Windows Server 2022 (ou `dhcpd` Linux).  
- **Victim PC** : Linux (Ubuntu 22.04).  
- **Attacker** : Kali Linux (ou autre distro).  

### 8.3 Étapes détaillées  

#### 8.3.1 Configuration de base (SW1)

```bash
configure terminal
hostname SW1
no ip domain-lookup
!
interface range GigabitEthernet0/1-4
  switchport mode access
  spanning-tree portfast
!
interface GigabitEthernet0/1
  description DHCP Server uplink
  switchport access vlan 10
  ip dhcp snooping trust
  ip arp inspection trust
!
interface GigabitEthernet0/2
  description Attacker (untrusted)
  switchport access vlan 10
!
interface GigabitEthernet0/3
  description Victim PC (untrusted)
  switchport access vlan 10
!
interface GigabitEthernet0/4
  description Core uplink (trusted)
  switchport trunk allowed vlan 10
  ip dhcp snooping trust
  ip