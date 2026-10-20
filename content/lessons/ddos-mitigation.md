# Cours intensif – Attaques DDoS et Mitigation  
**Niveau : Administrateur Réseau Senior (CCIE)**  

---

## Table des matières
| # | Section |
|---|---------|
| 1 | Introduction & enjeux |
| 2 | Taxonomie des attaques DDoS |
| 3 | Architecture des botnets & vecteurs d’amplification |
| 4 | Métriques de mesure & indicateurs de performance |
| 5 | Détection précoce – signatures, anomalies & télémétrie |
| 6 | Stratégies de mitigation – couche réseau, transport, application |
| 7 | Solutions matérielles & logicielles (appliances, cloud, SD‑WAN) |
| 8 | BGP & routage de protection (RTBH, BGP Flowspec, Anycast) |
| 9 | Configurations Cisco avancées (CBF, MPF, NBAR, ZBF) |
|10 | Linux – iptables/nftables, tc, ipset, eBPF |
|11 | Tableau comparatif des solutions |
|12 | Atelier de dépannage – scénario réel |
|13 | Bonnes pratiques & checklist post‑mortem |
|14 | Références & lectures complémentaires |

---

## 1. Introduction & enjeux

Les attaques par déni de service distribué (**DDoS**) sont aujourd’hui l’une des menaces les plus répandues et les plus coûteuses pour les opérateurs, les fournisseurs de services cloud et les entreprises. Selon le **Akamai State of the Internet 2024**, le trafic DDoS moyen a atteint **1,8 Tbps**, avec des pics dépassant **2,5 Tbps**.  

- **Impact business** : perte de revenus, atteinte à la réputation, pénalités contractuelles.  
- **Impact technique** : saturation de la bande passante, épuisement des tables de connexion, désynchronisation des protocoles de transport.  
- **Contraintes réglementaires** : GDPR, NIS2 imposent des exigences de disponibilité et de notification d’incident.

Le rôle du senior network admin est de **prévenir**, **détecter**, **réagir** et **documenter** les attaques, tout en garantissant la continuité de service.

---

## 2. Taxonomie des attaques DDoS

| Catégorie | Sous‑type | Protocole(s) ciblé(s) | Mécanisme | Exemple |
|-----------|-----------|-----------------------|-----------|---------|
| **Volumétrique** | UDP Flood, DNS Amplification, NTP Reflection | UDP, DNS, NTP | Inondation de bande passante | 300 GB/s UDP Flood |
| **Protocole** | SYN Flood, ACK Flood, TCP Reset, ICMP Flood | TCP, ICMP | Saturation des tables de connexion / état | 500 k SYN/s |
| **Application (L7)** | HTTP GET/POST Flood, Slowloris, RUDY, WordPress XML‑RPC | HTTP/HTTPS, TCP | Consommation de ressources CPU / RAM / thread pool | 200 k HTTP GET/s |
| **Hybrid / Multi‑vector** | Combinaison de plusieurs types, souvent synchronisée | Tous | Masquage de la vraie nature, dépassement des filtres simples | 1 Tbps + 200 k SYN/s + 150 k HTTP GET/s |
| **Attaques de couche 2** | MAC Flood, ARP Spoofing, STP BPDUs | Ethernet, ARP | Saturation du CAM table, déstabilisation du pontage | 100 k ARP replies/s |

### 2.1 Amplification & réflexion

| Service | Port | Facteur d’amplification moyen |
|---------|------|--------------------------------|
| DNS (open resolver) | 53/udp | 20‑70× |
| NTP (monlist) | 123/udp | 30‑50× |
| Memcached | 11211/udp | 500‑1000× |
| SSDP (UPnP) | 1900/udp | 10‑30× |
| Chargen | 19/udp | 30‑40× |

> **Note** : Le facteur dépend du payload de la requête (ex. `monlist` NTP = 48 octets → 1 KB réponse).

---

## 3. Architecture des botnets & vecteurs d’amplification

```
+-------------------+          +-------------------+          +-------------------+
|  Bot #1 (IoT)     |---+      |  Bot #2 (VM)      |---+      |  Bot #N (Comp.)   |
|  (malware)        |   \     |  (C&C)            |   \     |  (zombie)         |
+-------------------+    \    +-------------------+    \    +-------------------+
        |                 \            |                 \            |
        |  UDP/ICMP/HTTP   \           |  UDP/ICMP/HTTP   \           |
        v                  \          v                  \          v
+---------------------------------------------------------------+
|                     Command & Control (C&C)                  |
|  (IRC, HTTP, P2P, DNS) – distribue les scripts d’attaque       |
+---------------------------------------------------------------+
        |
        |  Amplification (ex: DNS open resolver, NTP monlist)
        v
+---------------------------------------------------------------+
|                     Cible (target) – ISP Edge                |
+---------------------------------------------------------------+
```

- **Botnet « Low‑and‑Slow »** : utilise peu de bande passante mais cible les ressources CPU/threads (ex. Slowloris).  
- **Botnet « High‑Volume »** : exploite des réseaux d’IoT et de serveurs compromis pour générer des Gbps.  
- **C&C** : souvent réside sur des services légitimes (GitHub, Discord) pour éviter le blocage.

---

## 4. Métriques de mesure & indicateurs de performance

| Métrique | Unité | Seuil d’alerte (exemple) | Outil de collecte |
|----------|-------|--------------------------|-------------------|
| **Bps** (bits/s) | bps | > 70 % de la capacité de liaison | NetFlow, sFlow, SNMP |
| **pps** (paquets/s) | pps | > 80 % du taux de traitement du routeur | Cisco NetFlow, NFDUMP |
| **Conn/s** (nouveaux flux TCP) | conn/s | > 200 k conn/s | Cisco IOS `show ip accounting` |
| **CPU utilisation** | % | > 85 % pendant > 30 s | `show processes cpu` |
| **Memory usage** | % | > 90 % | `show memory statistics` |
| **Latency** | ms | +200 ms vs baseline | Ping, traceroute, BGP monitoring |
| **Packet loss** | % | > 2 % | `show interface` counters |

> **Tip** : Utilisez **Cisco NetFlow v9** + **sFlow** + **IPFIX** pour corréler trafic volumétrique et sources d’attaque.

---

## 5. Détection précoce – signatures, anomalies & télémétrie

### 5.1 Signatures (IDS/IPS)

| Signature | Description | Exemple de règle Snort |
|-----------|-------------|------------------------|
| `DDoS-UDP-Flood` | > 1000 UDP packets/s vers même destination | `alert udp any any -> $HOME_NET any (msg:"DDoS UDP Flood"; threshold: type both, track by_src, count 1000, seconds 1; sid:1000001; rev:1;)` |
| `DDoS-SYN-Flood` | > 200k SYN/s sans ACK | `alert tcp any any -> $HOME_NET 80 (flags:S; threshold: type both, track by_dst, count 200000, seconds 1; sid:1000002; rev:1;)` |
| `DDoS-HTTP-GET` | > 150k HTTP GET/s sur même URL | `alert http $EXTERNAL_NET any -> $HOME_NET $HTTP_PORTS (http_method; content:"GET"; threshold: type both, track by_dst, count 150000, seconds 1; sid:1000003; rev:1;)` |

### 5.2 Anomalies (Statistical)

- **Entropie d’IP source** : chute brutale → attaque par spoofing.  
- **Distribution des ports** : pic sur un port peu utilisé → réflexion.  
- **Ratio SYN/ACK** : > 10 :1 → SYN flood.  

Utilisez **Cisco Stealthwatch**, **Arbor Networks** ou **Zeek** (Bro) pour les analyses en temps réel.

### 5.3 Télémétrie (Telemetry)

| Protocole | Avantages | Exemple d’implémentation |
|-----------|-----------|--------------------------|
| **gRPC/Streaming** (Google BBR) | Latence ultra‑faible, push de métriques | `cisco telemetry model-driven` |
| **IPFIX** | Standard ouvert, agrégation | `ip flow-export destination 10.0.0.10 2055` |
| **sFlow** | Échantillonnage léger | `sflow 1 destination 10.0.0.11 6343` |

---

## 6. Stratégies de mitigation – couche réseau, transport, application

### 6.1 Couche réseau (L2/L3)

| Technique | Action | Impact sur le trafic légitime | Exemple Cisco |
|-----------|--------|------------------------------|---------------|
| **uRPF strict** | Bloque les paquets avec source non reachable via interface d’entrée | Faible, nécessite topologie symétrique | `interface GigabitEthernet0/0/0`<br>`ip verify unicast source reachable-via any` |
| **RTBH (Remote Triggered Black Hole)** | Annonce BGP /32 vers nul (discard) | Aucun trafic légitime vers /32 | `route-map RTBH permit 10`<br>`match ip address prefix-list BLACKHOLE`<br>`set community no-export` |
| **BGP Flowspec** | Filtrage granulaire (protocol, ports, dscp) | Granularité élevée, peu d’impact | `route-map FLOWSPEC permit 10`<br>`match community FLOWSPEC`<br>`set community 65535:666` |
| **ACL statiques** | Bloque IP/port spécifiques | Risque de false positive | `access-list 101 deny udp any host 203.0.113.10 eq 53` |
| **Rate‑limit (policing)** | Limite pps/bps sur interface | Peut affecter trafic légitime si mal dimensionné | `policy-map POLICE-UDP`<br>`class class-default`<br>`police 500000000 1000000 conform-action transmit exceed-action drop`<br>`service-policy output POLICE-UDP` |

### 6.2 Couche transport (TCP/UDP)

| Méthode | Description | Cisco IOS‑XE |
|---------|-------------|--------------|
| **SYN‑Cookie** | Répond avec un cookie sans réserver de ressource | `ip tcp synwait-time 5`<br>`ip tcp intercept` |
| **TCP Intercept (Proxy Mode)** | Termination SYN, validation, puis forward | `ip tcp intercept mode proxy`<br>`ip tcp intercept list 101` |
| **UDP‑Lite/Port‑Randomisation** | Modifie ports source pour éviter le spoofing | Pas natif – implémenter via **iptables** (Linux) |
| **TCP‑MSS clamp** | Réduit la taille maximale des segments pour limiter le nombre de paquets | `ip tcp adjust-mss 1300` |

### 6.3 Couche application (L7)

| Technique | Outil | Exemple de règle (NGINX) |
|-----------|-------|--------------------------|
| **Rate‑limit par IP** | NGINX, HAProxy, Envoy | `limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;` |
| **Challenge‑Response (CAPTCHA)** | Cloudflare, Akamai | `if ($request_uri ~* "/login") { set $challenge 1; }` |
| **Web Application Firewall (WAF)** | ModSecurity, F5 ASM | `SecRule REQUEST_METHOD "POST" "id:200001,phase:2,deny,status:403,msg:'DDoS POST flood'"` |
| **Connection‑draining** | L4/L7 load balancer | `set timeout client 10s;` |
| **HTTP/2 Push‑back** | Envoy | `ratelimit` filter with `max_tokens` |

---

## 7. Solutions matérielles & logicielles

| Vendor | Appliance | Débit max | Méthodes de mitigation | Points forts |
|--------|-----------|----------|------------------------|--------------|
| **A10 Networks** | Thunder TPS | 2 Tbps | Scrubbing, TCP‑Intercept, UDP‑Rate‑limit | DPI + SSL‑offload |
| **Radware** | DefensePro | 5 Tbps | Behavioral analysis, BGP‑RTBH, Cloud‑scrubbing | Auto‑learning |
| **Cisco** | ASA/Firepower, NCS‑540 | 1 Tbps | CBF, MPF, uRPF, NetFlow, BGP‑Flowspec | Intégration avec IOS‑XR |
| **Juniper** | SRX, vSRX | 4 Tbps | AppSecure, DDoS‑Protection (J‑Flow) | Tight coupling avec Contrail |
| **Cloud** | AWS Shield, Azure DDoS Protection, Cloudflare | Illimité (via Anycast) | Scrubbing, Rate‑limit, IP‑Reputation | Aucun besoin de CAPEX |
| **Open‑Source** | **FastNetMon**, **KillerBee**, **Suricata** | Dépend du hardware | Flow‑based detection, BGP‑RTBH, IPtables | Flexibilité, coût réduit |

---

## 8. BGP & routage de protection

### 8.1 RTBH (Remote Triggered Black Hole)

```
# Exemple d'annonce sur le routeur d'edge
router bgp 65001
  neighbor 192.0.2.1 remote-as 65002
  address-family ipv4 unicast
    network 203.0.113.0 mask 255.255.255.0 route-map RTBH-IN
    neighbor 192.0.2.1 route-map RTBH-OUT out
!
ip prefix-list BLACKHOLE seq 5 permit 203.0.113.45/32 le 32
route-map RTBH-IN permit 10
  match ip address prefix-list BLACKHOLE
  set community no-export additive
!
route-map RTBH-OUT permit 10
  match community 65535:666
  set community no-export
```

- **Flux** : le serveur de mitigation envoie un **BGP UPDATE** avec le préfixe `/32` et la communauté `no-export`. Le routeur d’edge le redirige vers **Null0** (`discard`).

### 8.2 BGP Flowspec (RFC 5575)

```
# Flowspec pour bloquer UDP > 500 Mbps vers 203.0.113.0/24
router bgp 65001
  address-family ipv4 flowspec
    neighbor 192.0.2.2 activate
    neighbor 192.0.2.2 route-map FLOWSPEC-OUT out
!
route-map FLOWSPEC-OUT permit 10
  match community FLOWSPEC
  set community 65535:666
!
ip community-list standard FLOWSPEC permit 65535:666
!
# Flowspec rule (CLI simplifiée)
flowspec ipv4
  match destination 203.0.113.0/24
  match source any
  match protocol udp
  match destination-port range 0 65535
  then discard
```

### 8.3 Anycast scrubbing

```
          +-------------------+       +-------------------+
          |  Anycast Edge #1  |       |  Anycast Edge #2  |
          +--------+----------+       +----------+--------+
                   |                         |
          +--------+----------+   +----------+--------+
          |   Scrubbing Center (Cloud)   |
          +-----------------------------+
```

- Le trafic légitime et l’attaque sont **routés** vers le même Anycast prefix. Le centre de scrubbing filtre le trafic malveillant et renvoie le trafic « clean » vers le serveur d’origine.

---

## 9. Configurations Cisco avancées

### 9.1 CBF – Control Plane Policing (IOS‑XE)

``` 
policy-map type control-plane POL-CONTROL-PLANE
  class type control-plane police
    police 2000000 2000 exceed-action drop
    police 2000000 2000 exceed-action drop
    police 2000000 2000 exceed-action drop
!
control-plane
  service-policy input POL-CONTROL-PLANE
```

- **Objectif** : protéger le CPU du routeur contre les paquets de contrôle (SYN, UDP, ICMP) en limitant le débit à 2 Mpps.

### 9.2 MPF – Modular Policy Framework (ACL