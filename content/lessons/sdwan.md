# Cours Intensif SD‑WAN – Niveau Admin Réseau Senior (CCIE)

> **Objectif** : Maîtriser les concepts, l’architecture, le déploiement, la configuration et le dépannage avancé d’une solution SD‑WAN.  
> **Pré‑requis** : CCNP Routing & Switching, connaissances solides du routage IP, MPLS, BGP, QoS, sécurité réseau, Linux et des plateformes Cisco (IOS‑XE, IOS‑XR, NX‑OS).  

---

## 1. Introduction & Contexte

| Critère | WAN traditionnel (MPLS, L2VPN) | SD‑WAN |
|--------|--------------------------------|--------|
| **Modèle de contrôle** | Centralisé (LDP/RSVP) | Découplé (Control plane + Data plane) |
| **Coût du lien** | Élevé (MPLS dédié) | Mix de MPLS, Internet, LTE, 5G, satellite |
| **Agilité** | Déploiement mois/semaines | Provisioning en minutes via orchestrateur |
| **Visibilité** | Limitée (statistiques de lien) | Telemetry granulaire (per‑flow, per‑application) |
| **Sécurité** | ACLs, VPN IPsec ponctuels | Segmentation micro‑tunnel, chiffrement de bout en bout |
| **QoS** | Basé sur DiffServ, class‑of‑service du transport | Application‑aware, politiques dynamiques, steering |

> **Pourquoi SD‑WAN ?**  
> - Optimiser les coûts en tirant parti du haut débit public.  
> - Améliorer la performance des applications cloud (SaaS, IaaS).  
> - Simplifier la gestion multi‑site via un orchestrateur central.

---

## 2. Architecture Générale

```
                     +-------------------+
                     |  Orchestrateur    |
                     |  (Controller)    |
                     +----+----------+---+
                          |  API/REST |
   +----------------------+-----------+----------------------+
   |                      |           |                      |
+--v--+               +---v---+   +---v---+               +--v--+
|Edge |               |Edge   |   |Edge   |               |Edge |
|Site A               |Site B  |   |Site C |               |Site D|
+-----+               +-------+   +-------+               +-----+
   |                     |           |                      |
   |   +-----------------+-----------+----------------------+   
   |   |   Underlay (Internet, MPLS, LTE, 5G)               |
   +---+----------------------------------------------------+
```

### 2.1. Composants clés

| Composant | Fonction | Exemple de produit |
|-----------|----------|--------------------|
| **Edge (CPE)** | Encapsulation/decapsulation, appli‑policy, sécurité | Cisco vEdge, Viptela, Meraki MX, FortiGate 60F |
| **Orchestrateur** | Gestion centralisée des politiques, provisioning, monitoring | Cisco vManage, VMware NSX Manager, FortiManager |
| **Controller** (Control Plane) | Distribution des routes, états de santé, algorithmes de path‑selection | Viptela Controller, Cisco SD‑WAN controller |
| **Overlay Network** | Tunnels IPsec/DTLS entre Edge | IPsec (AES‑256‑GCM), DTLS 1.2 |
| **Underlay** | Transport physique (Internet, MPLS, LTE) | ISP, circuits dédiés |
| **Service Insertion** | Firewalls, IDS/IPS, WAN optimisation, DLP | FortiGate, Palo Alto VM‑Series, Cisco WAAS |
| **Telemetry & Analytics** | Collecte de métriques (Jitter, loss, RTT) | InfluxDB, Grafana, Cisco DNA Center |

---

## 3. Modèle de Contrôle vs. Modèle de Données

### 3.1. Control Plane (Orchestrateur + Controllers)

- **BGP‑like route distribution** : chaque Edge annonce ses préfixes via le contrôleur (BGP‑Lite).  
- **Policy‑Based Routing (PBR)** : les politiques sont traduites en règles de forwarding (ACL + QoS).  
- **Health‑check & Path‑Selection** : monitoring continu (ICMP, BFD, TCP‑ping) → métriques agrégées → algorithmes de sélection (latency‑first, jitter‑first, cost‑based).  

### 3.2. Data Plane (Edge)

- **Encapsulation** : chaque flux est encapsulé dans un tunnel (IPsec/DTLS) selon la politique.  
- **Forwarding** : basé sur FIB générée à partir du Control Plane (label‑based ou route‑based).  
- **QoS** : DSCP remap, policing, shaping au niveau du tunnel.  

---

## 4. Overlay & Underlay – Détails Techniques

### 4.1. Tunnel Types

| Tunnel | Chiffrement | Port | MTU recommandée | Cas d’usage |
|--------|-------------|------|-----------------|------------|
| IPsec ESP (AES‑256‑GCM) | Oui | UDP 500 / 4500 (NAT‑T) | 1400 | Sites avec exigences de conformité |
| DTLS 1.2 (AES‑128‑CBC) | Oui | UDP 443 | 1400 | Traversée NAT stricte, faible latence |
| GRE (non‑chiffré) | Non | N/A | 1476 | Environnements de test, pas de sensibilité data |

### 4.2. Underlay – Sélection du Transport

```
+------------------+-------------------+-------------------+-----------------+
|  Transport       |  Latency (ms)     |  Jitter (ms)      |  Coût ($/Mbps)  |
+------------------+-------------------+-------------------+-----------------+
| MPLS (Tier‑1)    |  10‑20            |  <1               |  0.15            |
| Internet (Fiber)|  30‑60            |  2‑5              |  0.02            |
| LTE/5G           |  40‑80            |  5‑15             |  0.03            |
+------------------+-------------------+-------------------+-----------------+
```

> **Best‑practice** : Utiliser le **MPLS** comme transport de secours (fail‑over) pour les applications critiques, le **Internet** pour le trafic best‑effort et le **LTE/5G** pour les sites distants sans fibre.

---

## 5. Configuration Cisco vEdge (IOS‑XE) – Exemple complet

> **Hypothèse** : Deux sites (HQ & Branch) connectés via MPLS et Internet.  
> **Objectif** : Prioriser le trafic voix sur le MPLS, le trafic SaaS sur Internet, avec redondance.

### 5.1. Déclaration des interfaces

```text
!--- HQ Edge
interface GigabitEthernet0/0
 description MPLS Backbone
 ip address 10.10.10.1 255.255.255.252
 no shutdown

interface GigabitEthernet0/1
 description Internet ISP
 ip address dhcp
 no shutdown
```

### 5.2. Création des tunnels (IPsec)

```text
crypto ikev2 proposal IKEV2-PROPOSAL
 encryption aes-gcm-256
 integrity sha256
 group 21

crypto ikev2 policy IKEV2-POLICY
 proposal IKEV2-PROPOSAL

crypto ikev2 keyring KEYRING-HQ
 peer BRANCH
  address 203.0.113.2
  pre-shared-key local HQ-PSK
  pre-shared-key remote BR-PSK

crypto ikev2 profile IKEV2-PROFILE
 match address local 0.0.0.0
 identity local address 10.10.10.1
 authentication remote pre-share
 authentication local pre-share
 keyring local KEYRING-HQ
 dpd 10 5 on-demand
```

```text
crypto ipsec transform-set TS-AES256 esp-aes-gcm 256
 mode tunnel

crypto ipsec profile IPSEC-PROFILE
 set transform-set TS-AES256
 set ikev2-profile IKEV2-PROFILE
```

```text
interface Tunnel0
 description Tunnel to Branch
 ip address 172.16.255.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 10.10.10.2
 tunnel mode ipsec ipv4
 tunnel protection ipsec profile IPSEC-PROFILE
```

### 5.3. Politique de routage (BGP‑Lite)

```text
router bgp 65001
 bgp log-neighbor-changes
 neighbor 172.16.255.2 remote-as 65002
 neighbor 172.16.255.2 ebgp-multihop 2
 neighbor 172.16.255.2 update-source Tunnel0
 !
 address-family ipv4 unicast
  network 10.0.0.0 mask 255.255.255.0
  neighbor 172.16.255.2 activate
 exit-address-family
```

### 5.4. Application‑aware Policy (Cisco vManage)

| Application | Port(s) | Priorité | Transport préféré |
|-------------|---------|----------|--------------------|
| VoIP (SIP)  | 5060,5061 | 1 (Critical) | MPLS |
| Microsoft 365 | 443 | 2 | Internet |
| HTTP/HTTPS | 80,443 | 3 | Internet |
| Backup (Veeam) | 2500‑2502 | 4 | MPLS (fallback) |

> **vManage** : Créez une *Application‑aware Policy* → *App‑List* → *App‑Policy* → *Transport‑Preference* → *Assign to VPN*.

### 5.5. QoS – Remapping DSCP

```text
policy-map VOICE-PRIO
 class VOICE
  set dscp ef
  police 512000 8000 exceed-action drop
 class class-default
  set dscp default

interface Tunnel0
 service-policy output VOICE-PRIO
```

---

## 6. Configuration Linux Edge (Open‑source – Viptela‑compatible)

> Utilisation de **StrongSwan** pour IPsec et **FRR** pour le routage.

### 6.1. StrongSwan (ipsec.conf)

```ini
config setup
 charondebug="ike 2, cfg 2, net 2"

conn %default
 keyexchange=ikev2
 ike=aes256gcm16-prfsha256-modp2048!
 esp=aes256gcm16!
 dpdaction=clear
 dpddelay=30s
 dpdtimeout=120s
 left=%defaultroute
 leftid=@hq
 leftauth=psk
 leftsubnet=10.0.0.0/24
 right=%any
 rightid=@branch
 rightauth=psk
 rightsubnet=10.1.0.0/24
 auto=add
```

### 6.2. PSK (ipsec.secrets)

```
@hq @branch : PSK "StrongSharedKey123!"
```

### 6.3. FRR BGP configuration (/etc/frr/bgpd.conf)

```text
router bgp 65001
 bgp router-id 10.0.0.1
 neighbor 172.16.255.2 remote-as 65002
 neighbor 172.16.255.2 ebgp-multihop 2
 neighbor 172.16.255.2 update-source tun0
 !
 address-family ipv4 unicast
  network 10.0.0.0/24
  neighbor 172.16.255.2 activate
 exit-address-family
```

### 6.4. Systemd service pour démarrage

```bash
systemctl enable strongswan
systemctl start strongswan
systemctl enable frr
systemctl start frr
```

---

## 7. Orchestration – Cisco vManage (extraits UI)

1. **Devices → Add** → Import du certificat et du serial number du Edge.  
2. **Configuration → Templates → Device Template** → Sélection du type (vEdge‑C8000V).  
3. **Feature Templates** → *VPN*, *Transport*, *Security*, *QoS* → remplissage des champs (exemple : `vpn 0`, `vpn 1` pour data & management).  
4. **Policy → Centralized Policy → Application‑aware** → Drag‑&‑Drop des applications → Assignation du *Transport Preference* (MPLS > Internet).  
5. **Monitor → Dashboard** → Graphiques de *Jitter, Packet Loss, RTT* par tunnel.

---

## 8. Tableaux Comparatifs – Vendors Leaders

| Vendor | Architecture | Tunnel Type | Orchestrateur | Cloud Integration | Licence (per‑site) |
|--------|--------------|-------------|---------------|-------------------|--------------------|
| **Cisco Viptela** | Dual‑plane (Control + Data) | IPsec/DTLS | vManage (GUI + API) | Azure, AWS, GCP (direct connect) | $2 500 – $8 000 |
| **Cisco Meraki** | Cloud‑first, SD‑WAN Lite | IPsec (AES‑256) | Dashboard (SaaS) | Meraki Insight, Auto VPN | $1 200 – $4 500 |
| **VMware VeloCloud** | Edge‑centric, Virtual Appliance | IPsec (AES‑256) | Orchestrator (SaaS) | NSX‑SD‑WAN, AWS Direct Connect | $2 000 – $7 000 |
| **Fortinet FortiGate SD‑WAN** | FortiOS (UTM + SD‑WAN) | IPsec/DTLS | FortiManager | FortiGate Cloud, Azure/OCI | $1 500 – $6 000 |
| **Palo Alto Networks Prisma SD‑WAN** | Cloud‑managed, App‑aware | IPsec (AES‑256) | Prisma SD‑WAN Console | Prisma Access, AWS Transit Gateway | $2 200 – $7 500 |

> **Critères de sélection** :  
> - **Scalabilité** (nombre de sites, capacité du contrôleur)  
> - **Intégration Cloud** (direct connect vs. VPN)  
> - **Fonctionnalités de sécurité** (NGFW intégré, sandbox)  
> - **Modèle de licence** (CAPEX vs. OPEX)  

---

## 9. Sécurité – Chiffrement, Authentification & Segmentation

| Niveau | Action | Exemple de configuration |
|--------|--------|--------------------------|
| **Tunnel** | IPsec ESP AES‑256‑GCM, IKEv2, PFS (modp2048) | `crypto ipsec transform-set TS-AES256 esp-aes-gcm 256` |
| **Endpoint** | Mutual X.509 certificates (optional) | `crypto pki trustpoint TP` → `enrollment terminal` |
| **Zero‑Trust Segmentation** | VPN‑per‑App, micro‑tunnels | Policy‑based segmentation dans vManage → *Segment‑ID* |
| **Inspection** | IDS/IPS inline, URL‑filter | Service insertion → `firewall` → `intrusion-prevention` |
| **Compliance** | PCI‑DSS, GDPR, HIPAA | Chiffrement de bout en bout, journalisation centralisée (Syslog, Splunk) |

---

## 10. Monitoring & Telemetry

| Métrique | Méthode de collecte | Fréquence | Utilisation |
|----------|---------------------|-----------|-------------|
| **RTT / Jitter** | BFD (Bidirectional Forwarding Detection) | 1 s | Path‑selection dynamique |
| **Loss** | ICMP/UDP probe | 5 s | Déclenchement de fail‑over |
| **Utilisation du tunnel** | SNMP OID `cisco‑sdwan‑tunnel‑stats` | 30 s | Dashboard de bande passante |
| **QoS per‑flow** | NetFlow v9 / IPFIX | 1 min | Analyse applicative |
| **Security events** | Syslog, CEF | en temps réel | SIEM integration |

> **Exemple de requête SNMP** (Cisco vEdge) :

```bash
snmpwalk -v2c -c public 10.0.0.1 1.3.6.1.4.1.9.9.618.1.3.1.1.2
# OID → ciscoSdwanTunnelStatsTable → ciscoSdwanTunnelTxBytes
```

---

## 11. Atelier de Dépannage – Scénario

### 11.1. Contexte

- Site **HQ** (MPLS + Internet) → Site **Branch** (Internet uniquement).  
- Application critique : *SIP VoIP* (port 5060) doit passer par MPLS.  
- Symptom : Les appels tombent après 30 s, le trafic bascule sur Internet, perte de qualité.

### 11.2. Checklist de Vérification

| Étape | Commande | Interprétation |
|-------|----------|----------------|
| 1️⃣ Vérifier l