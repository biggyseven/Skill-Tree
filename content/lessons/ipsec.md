# Cours Intensif – VPN IPsec (IKEv2, ESP)  
**Niveau : Administrateur Réseau Senior (CCIE)**  

---  

## Table des matières  

| # | Section | Description |
|---|---------|-------------|
| 1 | Introduction & concepts fondamentaux | Architecture, modèles OSI, terminologie |
| 2 | IKEv2 – Phase 1 & Phase 2 | Échanges, SA, algorithmes, extensions |
| 3 | ESP – Encapsulation Security Payload | Modes, algorithmes, RFC 4303 |
| 4 | Comparaison IKEv1 vs IKEv2 | Tableau détaillé |
| 5 | Architecture Cisco vs Linux (StrongSwan / Libreswan) | Configurations parallèles |
| 6 | Sélection d’algorithmes & politiques de sécurité | NIST, PCI‑DSS, recommandations |
| 7 | Scénarios avancés | Site‑to‑Site, Remote‑Access, Multi‑gateway, HA |
| 8 | Déploiement – Best‑Practice | Hardening, PKI, gestion des clés |
| 9 | Atelier de dépannage | Capture, analyse, checklist, cas pratiques |
|10| Annexes – RFC, commandes, scripts | Références rapides |

---  

## 1. Introduction & concepts fondamentaux  

### 1.1 Pourquoi IPsec ?  

* **Confidentialité** – chiffrement du trafic (AES‑GCM, ChaCha20).  
* **Intégrité & authenticité** – HMAC‑SHA2/3, ESP‑auth.  
* **Authentification mutuelle** – certificats X.509 ou PSK.  
* **Transparence** – fonctionne au niveau IP (couche 3) → aucune modification d’applications.  

### 1.2 Modèle OSI et placement  

```
+-------------------+-------------------+
|   Application     |   (ex. HTTP)      |
+-------------------+-------------------+
|   Transport       |   TCP/UDP         |
+-------------------+-------------------+
|   Network         |   IPsec (ESP/IKE) |
+-------------------+-------------------+
|   Data Link       |   Ethernet        |
+-------------------+-------------------+
|   Physical        |   Fibre/Cuivre    |
+-------------------+-------------------+
```

* **IKEv2** opère en **couche 3** (IP) mais utilise UDP 500/4500 pour le transport des messages d’échange.  
* **ESP** encapsule le **payload IP** (ou le transport complet) et se situe également en couche 3, juste au-dessus de l’en-tête IP.

### 1.3 Terminologie clé  

| Terme | Définition |
|------|------------|
| **SA (Security Association)** | Unidirectionnelle, identifiée par un SPI (Security Parameter Index). |
| **SPD (Security Policy Database)** | Table de filtrage qui décide quel trafic doit être protégé. |
| **PKI** | Infrastructure de gestion des certificats (CA, CRL, OCSP). |
| **PFS (Perfect Forward Secrecy)** | Renouvellement de clés DH à chaque SA pour éviter la compromission rétroactive. |
| **NAT‑Traversal (NAT‑T)** | Encapsulation UDP 4500 pour traverser les appareils NAT. |

---  

## 2. IKEv2 – Phase 1 & Phase 2  

### 2.1 Vue d’ensemble du protocole  

```
+-------------------+     +-------------------+
|   Initiateur      | --> |   Répondeur       |
|  (Client VPN)    |     |  (Gateway)        |
+-------------------+     +-------------------+
        |  IKE_SA_INIT  (UDP 500)               |
        |-------------------------------------->|
        |   SA, KE, NONCE, IDi, IDr, AUTH      |
        |<--------------------------------------|
        |  IKE_AUTH (UDP 500)                  |
        |-------------------------------------->|
        |   AUTH, CHILD_SA, CP, TS             |
        |<--------------------------------------|
        |  CREATE_CHILD_SA (UDP 4500)          |
        |-------------------------------------->|
        |   NEW CHILD_SA (ESP)                 |
+-------------------+     +-------------------+
```

* **Phase 1 (IKE_SA_INIT + IKE_AUTH)** : négociation de l’**IKE SA** (protection des messages d’échange).  
* **Phase 2 (CREATE_CHILD_SA)** : création des **CHILD SA** (ESP/ AH).  

### 2.2 IKE_SA_INIT – Paramètres échangés  

| Champ | Description | Valeur typique |
|------|-------------|----------------|
| **SAi / SAr** | Liste des algorithmes supportés (encryption, integrity, PRF, DH) | `ENCR: AES256-GCM, PRF: HMAC-SHA2-256, DH: MODP-3072` |
| **KEi / KEr** | Diffie‑Hellman public value | `0x...` |
| **Ni / Nr** | Nonces aléatoires (128 bits min) | `0x5F4A...` |
| **IDi / IDr** | Identité (FQDN, email, IP) | `IDi = fqdn:client.example.com` |
| **NAT‑D** | Indique la présence d’un NAT (option 0x01) | `NAT‑D = 1` |

**Exemple de ligne de configuration Cisco (IKEv2 policy) :**  

```
crypto ikev2 policy 10
  encryption aes-cmac-256 aes-gcm-256
  integrity sha256
  group 21               ! 3072‑bit MODP
  prf sha256
  lifetime seconds 86400
```

### 2.3 IKE_AUTH – Authentification  

* **Méthodes** :  
  * **Certificates** (X.509) – `auth-method rsa-signature` ou `ecdsa`.  
  * **Pre‑Shared Key (PSK)** – `auth-method pre-shared-key`.  
  * **EAP‑TLS / EAP‑TTLS** – pour Remote‑Access.  

* **Payloads obligatoires** : `AUTH`, `IDi`, `IDr`, `SAi2`/`SAr2` (CHILD SA), `TSi`/`TSr` (Traffic Selectors).  

**Exemple de configuration Linux StrongSwan (ipsec.conf) :**  

```
conn site-to-site
  left=192.0.2.1
  leftid=@gw1.example.com
  leftcert=gw1.crt
  leftkey=gw1.key
  right=198.51.100.1
  rightid=@gw2.example.com
  rightcert=gw2.crt
  ike=aes256gcm16-sha2_256-modp3072!
  esp=aes256gcm16-sha2_256!
  keyexchange=ikev2
  dpdaction=clear
  dpddelay=30s
  dpdtimeout=120s
  auto=add
```

### 2.4 CHILD SA – ESP (ou AH)  

* **SPI** (32 bits) généré aléatoirement par le créateur du SA.  
* **Mode** :  
  * **Transport** – ne chiffre que le **payload** IP, l’en‑tête IP reste visible.  
  * **Tunnel** – encapsule un **paquet IP complet** dans un nouveau paquet IP (souvent utilisé pour site‑to‑site).  

**Exemple de création d’une CHILD SA sur Cisco :**  

```
crypto ipsec transform-set TS-ESP-AES256GCM esp-aes-gcm-256 esp-sha256-hmac
crypto ipsec profile IPSEC-PROFILE
  set transform-set TS-ESP-AES256GCM
  set pfs group21
  set security-association lifetime seconds 3600
```

---  

## 3. ESP – Encapsulation Security Payload  

### 3.1 Structure du paquet ESP (Mode Tunnel)  

```
+-----------------+-----------------+-----------------+-----------------+
|   IP Header (outer)          | ESP Header (SPI, Seq)               |
+-----------------+-----------------+-----------------+-----------------+
|   ESP Payload (encrypted)    | ESP Trailer (Pad, PadLen, NextHdr) |
+-----------------+-----------------+-----------------+-----------------+
|   ESP Auth (HMAC) (optional)                                         |
+-----------------------------------------------------------------------+
```

* **ESP Header** : `SPI (4 octets) | Sequence Number (4 octets)`.  
* **ESP Trailer** : `Padding (0‑255 octets) | Pad Length (1 octet) | Next Header (1 octet)`.  
* **ESP Auth** : HMAC‑SHA2‑256/384/512 ou AES‑GMAC (selon transform‑set).  

### 3.2 Modes d’opération  

| Mode | Avantages | Inconvénients |
|------|-----------|----------------|
| **Transport** | Moins d’overhead (pas d’en‑tête IP supplémentaire). | Ne protège pas l’en‑tête IP → vulnérable aux attaques de spoofing. |
| **Tunnel** | Confidentialité totale du trafic interne, support NAT‑T. | Overhead supplémentaire (nouvel IP + ESP). |

### 3.3 Algorithmes recommandés (2024)  

| Famille | Algorithme | Taille clé | Mode | Note |
|--------|------------|------------|------|------|
| **Encryption** | AES‑GCM‑256 | 256 bits | AEAD | + intégrité, recommandé. |
| | ChaCha20‑Poly1305 | 256 bits | AEAD | Idéal sur CPU sans AES‑NI. |
| | AES‑CBC‑256 | 256 bits | CBC | Déprécié (padding oracle). |
| **Integrity (si non‑AEAD)** | HMAC‑SHA2‑256 | – | – | Utilisé avec AES‑CBC. |
| **PRF** | HMAC‑SHA2‑256 | – | – | Pour dérivation de clés. |
| **DH Group** | MODP‑3072 (group 14) | – | – | Minimum pour conformité PCI‑DSS. |
| | ECP‑256 (group 19) | – | – | Courbe elliptique, plus rapide. |

### 3.4 ESP‑AEAD vs ESP‑CBC+HMAC  

| Caractéristique | ESP‑AEAD (ex. AES‑GCM) | ESP‑CBC + HMAC |
|-----------------|------------------------|----------------|
| **Confidentialité + Intégrité** | Unique bloc, authentifié en même temps | Deux blocs distincts (chiffrement + MAC) |
| **Performance** | SIMD (AES‑NI) très rapide, moins de cycles | Plus de cycles, besoin de padding |
| **Résilience aux attaques** | Résistant aux attaques de replay & padding | Susceptible aux padding oracle si mal implémenté |
| **Overhead** | 16 octets (tag) | 12 octets (HMAC‑SHA2‑256) + padding variable |

---  

## 4. Comparaison IKEv1 vs IKEv2  

| Aspect | IKEv1 (Main/Aggressive) | IKEv2 |
|--------|--------------------------|-------|
| **Nombre de messages** | 4‑6 (Main) ou 3 (Aggressive) | 2 (IKE_SA_INIT) + 2 (IKE_AUTH) = 4 |
| **Support NAT‑T** | Option NAT‑D, souvent fragile | NAT‑T natif (UDP 4500) |
| **PFS** | Optionnel, nécessite re‑Nego | Obligatoire par défaut (configurable) |
| **Extensions** | Limited (Notify, Vendor ID) | Rich (EAP, MOBIKE, V2I, V2CP) |
| **Résilience** | Susceptible aux DoS (Aggressive) | Protection anti‑DoS via cookies |
| **Interopérabilité** | Large (legacy) | Modern, recommandé pour tout nouveau déploiement |
| **Gestion des SA** | Deux SA (ISAKMP + IPsec) | Un IKE SA + multiples CHILD SA |
| **Performance** | Plus de round‑trips (re‑key) | Re‑key plus efficace (CREATE_CHILD_SA) |
| **Complexité de configuration** | Plus élevée (mode, exchange) | Simpler, unified policy |

---  

## 5. Architecture Cisco vs Linux (StrongSwan / Libreswan)  

### 5.1 Diagramme d’architecture (ASCII)  

```
+-------------------+          +-------------------+          +-------------------+
|  Router Cisco    |  IKEv2   |  Linux GW (Swan)  |  IKEv2   |  Router Cisco    |
| (crypto map)      | <------> | (ipsec.conf)      | <------> | (crypto map)      |
+-------------------+          +-------------------+          +-------------------+
        |                               |                               |
        |   ESP (tunnel)                |   ESP (tunnel)                |
        +-------------------------------+-------------------------------+
                               |
                     Encrypted traffic (IP)
```

### 5.2 Configuration Cisco (exemple site‑to‑site)  

```
crypto ikev2 proposal IKEV2-PROPOSAL
  encryption aes-gcm-256
  integrity sha256
  group 21
  prf sha256
  lifetime seconds 86400

crypto ikev2 policy IKEV2-POLICY
  match fvrf any
  proposal IKEV2-PROPOSAL

crypto ikev2 keyring KEYRING
  peer GW2
    address 198.51.100.1
    pre-shared-key local 0 MyStrongPSK1
    pre-shared-key remote 0 MyStrongPSK2

crypto ikev2 profile IKEV2-PROFILE
  match identity remote fqdn gw2.example.com
  authentication local pre-share
  authentication remote pre-share
  keyring local KEYRING
  dpd 30 120 holdtime 150
  lifetime seconds 86400

crypto ipsec transform-set TS-ESP-AES256GCM esp-aes-gcm-256 esp-sha256-hmac
crypto ipsec profile IPSEC-PROFILE
  set transform-set TS-ESP-AES256GCM
  set pfs group21
  set ikev2-profile IKEV2-PROFILE

interface Tunnel0
  ip address 10.0.0.1 255.255.255.252
  tunnel source GigabitEthernet0/0
  tunnel destination 198.51.100.1
  tunnel mode ipsec ipv4
  tunnel protection ipsec profile IPSEC-PROFILE
```

### 5.3 Configuration StrongSwan (exemple)  

```
# /etc/ipsec.conf
config setup
  charondebug="ike 2, knl 2, cfg 2, net 2"

conn site-to-site
  left=192.0.2.1
  leftid=@gw1.example.com
  leftcert=gw1.crt
  leftsubnet=10.1.0.0/16
  leftfirewall=yes
  right=198.51.100.1
  rightid=@gw2.example.com
  rightcert=gw2.crt
  rightsubnet=10.2.0.0/16
  rightfirewall=yes
  ike=aes256gcm16-sha2_256-modp3072!
  esp=aes256gcm16-sha2_256!
  keyexchange=ikev2
  dpdaction=restart
  dpddelay=30s
  dpdtimeout=120s
  auto=add
```

* **Note** : `!` force strict algorithm ordering (no fallback).  

### 5.4 Points de divergence  

| Fonctionnalité | Cisco IOS | StrongSwan |
|----------------|-----------|------------|
| **MOBIKE** (re‑binding) | `ikev2 mobility` (v15.5+) | `mobike=yes` (default) |
| **EAP‑TLS** | `authentication remote eap tls` | `eap-tls` plugin |
| **PKI** | `crypto ca trustpoint` | `ca` section (pki) |
| **DPD** | `dpd 30 120` | `dpdaction=restart` |
| **VTI (Virtual Tunnel Interface)** | `tunnel mode ipsec ipv4` | `ipsec interface` (v2) |
| **Logging** | `debug crypto ikev2` | `charondebug="ike 2"` |

---  

## 6. Sélection d’algorithmes & politiques de sécurité  

### 6.1 Références normatives  

| Standard | Version | Exigences clés |
|----------|---------|----------------|
| **NIST SP 800‑57** | Rev 5 | AES‑256, SHA‑2/3, DH ≥ 3072 bits. |
| **PCI‑DSS v4.0** | 2023 | PFS obligatoire, AES‑GCM recommandé, rotation clé ≤ 90 jours. |
| **ISO/IEC 27001** | 2022 | Gestion du cycle de vie des certificats, audit des SA. |
|