# Cours Intensif – IDS / IPS & Deep Packet Inspection  
**Niveau : Senior Network Administrator (CCIE)**  
**Durée estimée : 2 jours (16 h) – 10 000 + caractères**  

---

## Table des matières  

| # | Section | Durée approximative |
|---|---------|----------------------|
| 1 | Introduction & Concepts fondamentaux | 30 min |
| 2 | Architecture IDS/IPS – Placement & Topologies | 45 min |
| 3 | Types d’IDS/IPS (Network, Host, Wireless, Cloud) | 45 min |
| 4 | Deep Packet Inspection (DPI) – Théorie & Protocoles | 1 h |
| 5 | Méthodes de détection – Signatures, Anomalies, Heuristiques | 1 h |
| 6 | Métriques de performance & dimensionnement | 45 min |
| 7 | Configuration Cisco (Firepower, IOS‑XE, IOS) | 2 h |
| 8 | Configuration Linux (Suricata, Snort, Zeek) | 2 h |
| 9 | Gestion des politiques & intégration SIEM | 1 h |
|10 | Atelier de dépannage (lab) – Scénarios réels | 3 h |
|11 | Bonnes pratiques, hardening & conformité | 45 min |
|12 | Quiz / Q&A | 30 min |

---

## 1. Introduction & Concepts fondamentaux  

### 1.1 Définitions  

| Terme | Description |
|-------|-------------|
| **IDS** (Intrusion Detection System) | Dispositif qui **détecte** les activités malveillantes et génère des alertes, sans bloquer le trafic. |
| **IPS** (Intrusion Prevention System) | Variante active de l’IDS qui **bloque** ou **modifie** le trafic suspect en temps réel. |
| **DPI** (Deep Packet Inspection) | Analyse du **contenu complet** du paquet (en-tête + charge utile) jusqu’à la couche application, permettant classification, filtrage et prévention. |
| **NIDS** | IDS placé **sur le réseau** (ex. en mode SPAN/TAP). |
| **HIDS** | IDS installé **sur l’hôte** (ex. agents Windows/Linux). |
| **Hybrid IDS/IPS** | Combine les deux approches – ex. Cisco Firepower NGIPS. |

### 1.2 Pourquoi DPI est indispensable aujourd’hui  

* **Chiffrement** : TLS 1.3, QUIC – DPI s’appuie sur le *SSL/TLS termination* ou sur le *TLS inspection* (décryptage en ligne).  
* **Applications Cloud** : SaaS, IaaS – les signatures traditionnelles ne suffisent plus.  
* **Attaques multi‑vecteurs** : exfiltration via DNS, steganographie dans les images, etc.  
* **Conformité** : PCI‑DSS, GDPR, NIS2 exigent la visibilité du trafic applicatif.  

---

## 2. Architecture IDS/IPS – Placement & Topologies  

```
                +-------------------+
                |   Internet ISP    |
                +--------+----------+
                         |
                +--------v----------+      +-----------------+
                |   Edge Router     +----->|  External IDS   |
                +--------+----------+      +-----------------+
                         |
                +--------v----------+      +-----------------+
                |   Firewall (FW)   +----->|  Inline IPS     |
                +--------+----------+      +-----------------+
                         |
          +--------------+--------------+
          |                             |
   +------v------+               +------v------+
   | Core Switch |               | Core Switch |
   +------+------+-+          +--+------+------+
          |        |          |         |
   +------v--+ +---v------+ +---v------+---+
   | Server  | | DMZ Hosts| |   Users   |
   +----------+ +----------+ +-----------+

```

### 2.1 Topologies classiques  

| Topologie | Avantages | Inconvénients |
|-----------|-----------|----------------|
| **Out‑of‑Band (Passive)** | Aucun impact sur la latence, aucune perte de paquets. | Ne peut pas bloquer (IDS uniquement). |
| **Inline (Bump‑in‑the‑Wire)** | Bloque le trafic malveillant (IPS). | Introduit un point de défaillance, nécessite HA. |
| **Tap‑Based** | Copie 1:1 du trafic, aucune modification. | Nécessite du matériel de capture (TAP) coûteux. |
| **Hybrid (Inline + SPAN)** | Flexibilité – IPS en ligne pour les flux critiques, IDS passif pour le reste. | Complexité de configuration. |

### 2.2 Redondance & HA  

| Méthode | Description | Exemple Cisco |
|---------|-------------|----------------|
| **Active/Standby** | Un dispositif en service, l’autre en veille. | `standby 1 ip 10.0.0.2 priority 110` |
| **Active/Active** | Deux appliances partagent la charge (load‑balancing). | `failover lan unit primary` + `failover lan unit secondary` |
| **Clustered DPI** | DPI partagé via *hash‑based distribution* (e.g., Cisco FTD cluster). | `cluster enable` |

---

## 3. Types d’IDS/IPS  

| Type | Environnement | Points forts | Points faibles |
|------|----------------|--------------|----------------|
| **Network IDS (NIDS)** | Segments réseau, DMZ | Grande visibilité, aucune charge sur les hôtes | Pas de visibilité sur le trafic chiffré |
| **Host IDS (HIDS)** | Serveurs, postes de travail | Analyse des appels système, détection de rootkits | Consomme des ressources hôte |
| **Wireless IDS (WIDS)** | Points d’accès Wi‑Fi | Détection d’attaques RF, rogue AP | Couverture limitée, besoin de radios compatibles |
| **Cloud‑Native IDS/IPS** | AWS, Azure, GCP | Scalabilité, intégration avec logs cloud | Dépendance du fournisseur, visibilité limitée sur le trafic interne chiffré |

---

## 4. Deep Packet Inspection – Théorie & Protocoles  

### 4.1 Processus DPI  

1. **Capture** – Interface en mode *promiscuous* ou *inline* (DPDK, AF_PACKET).  
2. **Décryptage** (optionnel) – TLS termination via *SSL Forward Proxy* ou *SSL Bridging*.  
3. **Parsing** – Décodage de chaque couche (Ethernet → IP → TCP/UDP → Application).  
4. **Normalisation** – Re‑construction des flux (reassembly TCP, fragmentation IP).  
5. **Matching** – Application des signatures, modèles d’anomalie, règles de conformité.  
6. **Action** – Log, alerte, blocage, redirection.  

### 4.2 Protocoles fréquemment ciblés  

| Protocole | Port(s) | DPI spécifique |
|-----------|---------|----------------|
| HTTP/HTTPS | 80/443 | Analyse de URI, méthodes, headers, corps (POST). |
| DNS | 53 | Détection de tunneling DNS (exfiltration). |
| SMTP | 25, 587 | Analyse de pièces jointes, commandes SMTP. |
| FTP | 21 | Inspection du canal de données (PASV/PORT). |
| SIP | 5060/5061 | Détection de VoIP phishing, media hijacking. |
| SMB | 445 | Inspection de fichiers, signatures de ransomware. |
| MQTT | 1883/8883 | IoT – détection de bots, anomalie de topics. |
| QUIC | 443 (UDP) | DPI via *TLS 1.3* decryption, reassembly UDP. |

### 4.3 Exemple de normalisation TCP – Reassembly  

```
[Client]--- SYN -->[IPS]--- SYN-ACK -->[Server]
[Client]--- ACK -->[IPS]--- ACK -->[Server]
[Client]--- PSH,Seq=1 Len=1460 -->[IPS]
[Client]--- PSH,Seq=1461 Len=500 -->[IPS]
[IPS]--- Reassemble (Seq=1..1960) --> Analyse DPI
```

---

## 5. Méthodes de détection  

| Méthode | Principe | Avantages | Limitations |
|---------|----------|-----------|-------------|
| **Signature‑Based** | Recherche de patterns binaires (Snort, Suricata). | Faible taux de faux positifs, rapide. | Incapable de détecter 0‑day, nécessite mise à jour. |
| **Anomaly‑Based** | Profilage statistique du trafic (déviation > 3σ). | Détecte attaques inconnues. | Plus de faux positifs, besoin de phase d’apprentissage. |
| **Heuristic / Behavioral** | Analyse du comportement d’applications (ex. fréquence de requêtes DNS). | Bonne couverture des attaques multi‑vecteurs. | Complexité de mise en œuvre. |
| **Machine‑Learning** | Modèles supervisés / non‑supervisés (Random Forest, Auto‑Encoder). | Adaptatif, détection de patterns subtils. | Besoin de jeux de données, risque d’over‑fit. |
| **Hybrid** | Combinaison signature + anomaly + ML. | Meilleur compromis. | Consommation de ressources plus élevée. |

### 5.1 Exemple de règle Snort (signature)  

```
alert tcp $HOME_NET any -> $EXTERNAL_NET 80 (msg:"WEB-MISC malicious PHP backdoor";
    flow:to_server,established;
    content:"<?php eval(base64_decode("; http_uri;
    nocase; classtype:web-application-attack; sid:20231001; rev:3;)
```

### 5.2 Exemple de règle Suricata (DPI) – TLS inspection  

```
alert tls $HOME_NET any -> $EXTERNAL_NET 443 (msg:"TLS - possible malicious JA3 fingerprint";
    tls.ja3_hash; content:"c0d5b9e1b0b1e5a9c3e3c0c7"; nocase;
    classtype:trojan-activity; sid:3000001; rev:1;)
```

---

## 6. Métriques de performance & dimensionnement  

| Métrique | Unité | Méthode de mesure | Impact sur le design |
|----------|-------|-------------------|----------------------|
| **Throughput (pps / Gbps)** | Gbps | `show ips statistics` (Cisco) ou `suricata -S` | Choisir NIC 10 GbE ou plus, DPDK. |
| **Latency** | µs | `ping -c 10 <IP>` avant/après activation | Bypass mode pour trafic critique. |
| **CPU Utilisation** | % | `top`, `mpstat`, `show process cpu` | Scale‑out, CPU pinning, cores dédiés. |
| **Memory Footprint** | MB | `free -m`, `show memory` | Ajuster taille du *flow table* (suricata.conf). |
| **Session/Flow Table Size** | # entries | `show ips flow-table` | Dimensionner en fonction du *concurrent sessions* (ex. 1 M). |
| **Signature Count** | # | `snort -T -c /etc/snort/snort.conf -l .` | Plus de signatures = plus de CPU. |

### 6.1 Calcul de capacité (exemple)  

- **Débit moyen** : 8 Gbps (≈ 1 Mpps).  
- **CPU** : 1 core @ 3 GHz peut traiter ~200 kpps (signature‑based).  
- **Cores requis** : 1 Mpps / 200 kpps = **5 cores** (prévoir 8 cores pour marge).  
- **Mémoire** : 8 GB RAM (2 GB pour le OS, 6 GB pour les tables).  

---

## 7. Configuration Cisco – Firepower, IOS‑XE, IOS  

### 7.1 Prérequis  

| Item | Version minimale |
|------|-------------------|
| **Firepower Threat Defense (FTD)** | 6.7.0 |
| **Cisco IOS‑XE** | 16.9.3 |
| **Cisco IOS** | 15.2(4)M6 |
| **License** | IPS/NGIPS + URL‑Filtering (optional) |

### 7.2 Déploiement Inline – Firepower  

```text
conf t
  interface GigabitEthernet0/0
    description *** Uplink ISP ***
    ip address 203.0.113.2 255.255.255.0
    no shutdown
  exit

  interface GigabitEthernet0/1
    description *** Inside LAN ***
    ip address 10.0.0.1 255.255.255.0
    no shutdown
  exit

  object network obj-10net
    subnet 10.0.0.0 255.255.255.0
  exit

  access-list ACL_IN extended permit ip any any
  access-group ACL_IN in interface GigabitEthernet0/0

  policy-map type inspect dns preset_dns_map
    parameters
      message-length maximum 512
  exit

  class-map inspection_default
    match default-inspection-traffic
  exit

  policy-map type inspect dns policy_dns
    class inspection_default
      inspect dns preset_dns_map
  exit

  service-policy type inspect policy_dns interface GigabitEthernet0/0
exit
write memory
```

#### 7.2.1 Activation du module IPS  

```text
conf t
  policy-map type inspect ips ips_policy
    class class-default
      inspect ips
  exit

  service-policy type inspect ips_policy interface GigabitEthernet0/0
  exit
```

#### 7.2.2 Import d’une signature set  

```text
request security ips signature download location ftp://ftp.cisco.com/ips/signatures/2024/ips-signatures-2024-10-01.tar
request security ips signature install file ips-signatures-2024-10-01.tar
```

### 7.3 Configuration d’un **IPS en mode TAP** (Cisco IOS)  

```text
interface GigabitEthernet0/2
 description *** TAP Interface ***
 no ip address
 no shutdown
!
ip access-list extended TAP_IN
 permit ip any any
!
class-map match-all TAP_CLASS
 match access-group name TAP_IN
!
policy-map type inspect ip ips_policy_tap
 class TAP_CLASS
   inspect ip ips
!
service-policy type inspect ips_policy_tap interface GigabitEthernet0/2
```

### 7.4 TLS/SSL Decryption (Firepower)  

```text
conf t
  ssl decryption policy ssl_policy
    default-action forward
    ssl-forward-proxy trustpoint TP_FTD
    ssl-forward-proxy certificate self-signed name SSL_CERT
    ssl-forward-proxy key self-signed name SSL_KEY
  exit

  class-map type inspect ssl match-any SSL_CLASS
    match port tcp eq 443
  exit

  policy-map type inspect ssl ssl_policy_map
    class SSL_CLASS
      inspect ssl ssl_policy
  exit

  service-policy type inspect ssl ssl_policy_map interface GigabitEthernet0/0
exit
write memory
```

---

## 8. Configuration Linux – Suricata, Snort, Zeek  

### 8.1 Installation (Debian/Ubuntu)  

```bash
sudo apt update
sudo apt install -y suricata snort zeek
```

### 8.2 Suricata – Mode Inline avec NFQUEUE  

```bash
# 1. Activer le module nfqueue dans le kernel
sudo modprobe nfnetlink_queue

# 2. Créer une règle iptables redirigeant le trafic vers NFQUEUE 0
sudo iptables -I FORWARD -j NFQUEUE --queue-num 0

# 3. Configurer suricata.yaml (extrait)
%YAML 1.1
---
%TAG ! tag:yaml.org,2002:
---
vars:
  address-groups:
    HOME_NET: "[10.0.0.0/24]"
    EXTERNAL_NET: "!$HOME_NET"
default-log-dir: /var/log/suricata
af-packet:
  - interface: eth0
    threads: auto
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    ring-size: 200000
    block-size: 65535
    checksum-checks: auto
    copy-mode: ips
    copy-iface: eth1
    # Inline
    inline:
      mode: nfqueue
      queue-num: 0
      # Action on match: drop / reject / pass
      default-action: pass
```

```bash
# 4. Démarrer Suricata en mode service
sudo systemctl enable suricata
sudo systemctl start suricata
```

### 8.3 Snort – Exemple de configuration Inline (AF_PACKET)  

```conf
# /etc/snort/snort.conf (extrait)
config interface: eth0
config daq: afpacket
config daq_mode: inline
config daq_var: promisc=1

# Définir les variables réseau
var HOME_NET 10.0.0.0/24
var EXTERNAL_NET any

# Inclure les règles
include $RULE_PATH/local.rules
include $RULE_PATH/community.rules
```

```bash
# Lancer Snort en mode inline
sudo snort -c /etc/snort/snort.conf -i eth0 -Q
```

### 8.4 Zeek – Utilisation comme NIDS & DPI (passif)  

```bash
# Créer un script de détection de tunneling DNS
cat > /opt/zeek/scripts/dns_tunnel.zeek <<'EOF'
@load