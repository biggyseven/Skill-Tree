# Cours intensif – Architecture Zero Trust  
**Niveau : Administrateur Réseau Senior (CCIE)**  
**Durée estimée : 2 jours (12 h) – 10 000 + caractères**  

---

## Table des matières
| # | Section | Durée estimée |
|---|---------|---------------|
| 1 | Introduction & mythes | 30 min |
| 2 | Principes fondamentaux | 45 min |
| 3 | Modèle de référence NIST SP 800‑207 | 45 min |
| 4 | Identité, Authentification & Autorisation (IAM) | 1 h |
| 5 | Micro‑segmentation & segmentation du réseau | 1 h 30 min |
| 6 | Contrôle d’accès dynamique (Policy Engine) | 1 h |
| 7 | Sécurisation des données (chiffrement, DLP) | 45 min |
| 8 | Intégration des solutions Cisco (ISE, TrustSec, SD‑WAN, DNA Center) | 2 h |
| 9 | Comparaison Zero Trust vs modèle périmétrique | 30 min |
|10 | Schémas d’architecture (ASCII) | 30 min |
|11 | Commandes Cisco & Linux (exemples concrets) | 1 h 30 min |
|12 | Atelier de dépannage – Lab pratique | 2 h |
|13 | Checklist de mise en œuvre & bonnes pratiques | 30 min |
|14 | Bibliographie & ressources complémentaires | 15 min |

---

## 1. Introduction & mythes

> **Zero Trust (ZT)** ne signifie pas “pas de confiance du tout”.  
> Il s’agit d’un **modèle de sécurité basé sur la vérification continue** de chaque transaction, qu’elle provienne du réseau interne ou externe.

| Mythe | Réalité |
|-------|---------|
| “ZT = VPN + pare-feu” | ZT dépasse le VPN : il contrôle le **who**, le **what**, le **when**, le **where** et le **how** à chaque flux. |
| “ZT supprime le périmètre” | Le périmètre existe toujours (ex. : edge, cloud), mais il est **dégradé** et **complété** par des contrôles internes. |
| “ZT est uniquement logiciel” | ZT repose sur **hardware** (TP‑ID, ASIC TrustSec), **cloud services** (IdP, CSP) et **policy engines**. |
| “ZT est impossible à déployer à grande échelle” | Les architectures modulaires (Cisco DNA, ISE, SD‑WAN) permettent un déploiement incrémental. |

---

## 2. Principes fondamentaux

1. **Vérifier explicitement** – Authentification forte, contexte (device posture, localisation, risque).  
2. **Limiter le périmètre** – Micro‑segmentation, “least‑privilege”.  
3. **Assumer la compromission** – Journaux détaillés, réponse automatisée, isolation dynamique.  
4. **Utiliser le moindre privilège** – Accès au minimum requis, durée limitée.  
5. **Inspecter et logger** – Tous les flux sont inspectés, les logs sont centralisés et corrélés.

---

## 3. Modèle de référence NIST SP 800‑207

```
+----------------------+      +-----------------------+
| 1. Policy Decision   |<---->| 2. Policy Enforcement |
|    Point (PDP)       |      |    Point (PEP)        |
+----------------------+      +-----------------------+
          ^                              ^
          |                              |
          v                              v
+----------------------+      +-----------------------+
| 3. Identity Provider |      | 4. Data & Application |
|    (IdP) – OIDC/OAuth|      |    Services           |
+----------------------+      +-----------------------+
```

* **PDP** : moteur d’évaluation des politiques (ex. : Cisco ISE, Palo Alto Panorama).  
* **PEP** : points d’application (firewalls, switches, agents).  
* **IdP** : source d’identité (AD, LDAP, Azure AD, Okta).  

---

## 4. Identité, Authentification & Autorisation (IAM)

### 4.1. Authentification forte (MFA)  
- **Protocoles** : RADIUS, TACACS+, SAML, OIDC, FIDO2.  
- **Cisco ISE** :  
  ```text
  aaa group server radius ZT-RADIUS
   server-private 10.10.10.10 key <secret>
   server-private 10.10.10.11 key <secret>
  aaa authentication login default group ZT-RADIUS local
  ```
- **Linux (pam‑duo)** :  
  ```bash
  sudo apt-get install libpam-duo
  echo "auth required pam_duo.so" >> /etc/pam.d/sshd
  ```

### 4.2. Posture du dispositif (Device Trust)

| Contrôle | Cisco | Linux |
|----------|-------|-------|
| Vérif. certificats | `show certificate ca trustpoint` | `openssl x509 -in /etc/ssl/certs/host.pem -text` |
| Vérif. conformité (MDM) | `ise device-group` | `osqueryi "SELECT * FROM rpm_packages WHERE name='selinux'"` |
| État du système (patches) | `show version` | `yum check-update` |

### 4.3. Autorisation basée sur les attributs (ABAC)

Exemple de règle ISE (pseudo‑JSON) :

```json
{
  "condition": {
    "and": [
      {"attribute": "user.role", "equals": "Network-Admin"},
      {"attribute": "device.trust", "equals": "trusted"},
      {"attribute": "network.location", "in": ["DC1","DC2"]},
      {"attribute": "time", "between": "08:00-18:00"}
    ]
  },
  "action": "permit"
}
```

---

## 5. Micro‑segmentation & segmentation du réseau

### 5.1. Concepts clés

| Concept | Description | Exemple Cisco |
|---------|-------------|---------------|
| **Security Group Tag (SGT)** | Identifiant logique attaché à un endpoint | `cts role-based sgt 10` |
| **Security Group ACL (SGACL)** | ACL qui utilise les SGT comme source/destination | `ip access-list extended SGACL-10 permit ip any any` |
| **Enforcement Point** | Switch/Router/Firewall qui applique les SGACL | `cts role-based enforce` |

### 5.2. Implémentation sur un campus Cisco

```
   +-------------------+          +-------------------+
   |  Core Switch 1    |---Trunk---|  Core Switch 2    |
   +-------------------+          +-------------------+
            |                              |
   +--------+--------+            +--------+--------+
   | Access Switch A |            | Access Switch B |
   +--------+--------+            +--------+--------+
            |                              |
   +--------+--------+            +--------+--------+
   |   Host A (PC)   |            |   Host B (Server)|
   +-----------------+            +-----------------+
```

**Configuration SGT/SGACL (exemple simplifié) :**

```text
! --- Sur le Core Switch 1 ---
cts role-based sgt 10 name "Finance"
cts role-based sgt 20 name "Engineering"

! SGACL qui autorise Finance ↔ Engineering uniquement sur le port 443
ip access-list extended SGACL-FIN-ENG
  permit tcp any any eq 443
  remark SGACL for Finance ↔ Engineering

! Appliquer SGACL sur les interfaces d’accès
interface GigabitEthernet1/0/10
  cts role-based sgt 10
  ip access-group SGACL-FIN-ENG in
!
interface GigabitEthernet1/0/20
  cts role-based sgt 20
  ip access-group SGACL-FIN-ENG in
```

### 5.3. Micro‑segmentation côté Linux (nftables)

```bash
# Crée un set d’IP de confiance (ex. Finance)
sudo nft add set inet filter finance { type ipv4_addr\; flags interval\; }

# Ajoute les IP autorisées
sudo nft add element inet filter finance { 10.10.10.0/24, 10.10.20.0/24 }

# Politique : autoriser HTTPS uniquement entre les deux sets
sudo nft add rule inet filter forward ip saddr @finance ip daddr @engineering tcp dport 443 accept
sudo nft add rule inet filter forward ip saddr @finance ip daddr @engineering counter drop
```

---

## 6. Contrôle d’accès dynamique (Policy Engine)

### 6.1. Architecture typique

```
+-------------------+      +-------------------+      +-------------------+
|   Identity Store  | ---> |   Policy Engine   | ---> |   Enforcement    |
| (AD/LDAP/OIDC)    |      | (ISE, Palo Alto) |      |   (FW, Switch)   |
+-------------------+      +-------------------+      +-------------------+
```

### 6.2. Exemple de flux d’évaluation

1. **Endpoint** → **PEP** (switch) envoie un *access‑request* RADIUS.  
2. **PEP** ajoute le contexte (IP, MAC, posture).  
3. **PDP** (ISE) interroge l’**IdP** (Azure AD) → récupère les attributs.  
4. **PDP** applique les **politiques ABAC** → renvoie un **SGT** ou une décision *permit/deny*.  
5. **PEP** applique la décision (SGACL, ACL, QoS).  

### 6.3. Déploiement d’un Policy Engine Open‑Source (OPA)

```bash
# Installation d’OPA
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/

# Exemple de règle Rego (policy.rego)
cat <<'EOF' > policy.rego
package zt

default allow = false

allow {
    input.user.role == "Network-Admin"
    input.device.trust == "trusted"
    input.network.zone == "DC"
    input.time >= "08:00"
    input.time <= "18:00"
}
EOF

# Test de la règle
opa eval -i input.json -d policy.rego "data.zt.allow"
```

---

## 7. Sécurisation des données (chiffrement, DLP)

| Niveau | Technique | Outils Cisco / Open‑Source |
|--------|-----------|----------------------------|
| **Transit** | TLS 1.3, IPsec, WireGuard | `crypto ipsec transform-set ZT-TRANSFORM esp-aes-256 esp-sha256-hmac` |
| **Repos** | AES‑256‑GCM, LUKS, BitLocker | `cryptsetup luksFormat /dev/sdb1` |
| **Application** | FIPS‑validated libraries, OIDC‑based token | `openssl s_client -connect app.example.com:443` |
| **DLP** | Inspection de flux, classification | Cisco SecureX, OpenDLP (`opendlp scan -r /data`) |

### Exemple de tunnel IPsec site‑to‑site (Cisco IOS)

```text
crypto isakmp policy 10
  encr aes 256
  hash sha256
  authentication pre-share
  group 21
  lifetime 86400
crypto isakmp key ZTSecret address 203.0.113.2

crypto ipsec transform-set ZT-TRANSFORM esp-aes-256 esp-sha256-hmac
crypto map ZT-MAP 10 ipsec-isakmp
  set peer 203.0.113.2
  set transform-set ZT-TRANSFORM
  match address 101

interface GigabitEthernet0/0
  ip address 10.0.0.1 255.255.255.0
  crypto map ZT-MAP
```

---

## 8. Intégration des solutions Cisco

| Solution | Rôle ZT | Points forts |
|----------|----------|--------------|
| **Cisco ISE** | IdP, PDP, posture, SGT/SGACL | Authentification multi‑factor, intégration native avec TrustSec |
| **Cisco TrustSec** | Micro‑segmentation, SGT | Pas besoin de VLANs, support hardware accéléré |
| **Cisco SD‑WAN (vEdge)** | Périmètre distribué, chiffrement, segmentation | Routage basé sur l’identité, politique centralisée via vManage |
| **Cisco DNA Center** | Orchestration, visibilité, assurance | Déploiement automatisé des politiques ZT, analytics en temps réel |
| **Cisco Duo** | MFA, vérification de posture | Authentification adaptative, intégration RADIUS/TACACS+ |
| **Cisco Secure Firewall (Firepower)** | PEP, inspection approfondie (NGFW) | Analyse de trafic, sandboxing, intégration ISE pour SGT |

### Workflow typique (ISE + DNA Center)

1. **Provisioning** – DNA Center crée les profils de switch, active TrustSec.  
2. **Enregistrement** – Les endpoints s’enregistrent via 802.1X + posture (ISE).  
3. **Attribution SGT** – ISE attribue un SGT basé sur les attributs.  
4. **Application SGACL** – Les switches appliquent les SGACL en temps réel.  
5. **Feedback** – Telemetry (Telemetry Streaming, NetFlow) vers DNA Center pour audit.

---

## 9. Comparaison Zero Trust vs modèle périmétrique

| Aspect | Modèle Périmétrique (classique) | Zero Trust |
|--------|--------------------------------|------------|
| **Défense** | Pare‑feu périmétrique, DMZ | Vérification à chaque hop |
| **Confiance** | “Inside = trusted” | “Never trust, always verify” |
| **Segmentation** | VLANs, ACLs statiques | SGT/SGACL, micro‑segmentation dynamique |
| **Gestion des identités** | Authentification ponctuelle (VPN) | Authentification continue + posture |
| **Réponse aux incidents** | Détection tardive, isolation lente | Isolation automatisée, quarantine en temps réel |
| **Complexité** | Simplicité apparente, mais blind spots | Complexité initiale, mais visibilité totale |
| **Coût** | CAPEX faible, OPEX élevé (breaches) | OPEX initial élevé, ROI sur réduction des incidents |

---

## 10. Schémas d’architecture (ASCII)

### 10.1. Architecture Zero Trust d’entreprise

```
          +-------------------+   +-------------------+
          |   Cloud IdP (Azure AD)   |   |   On‑prem AD/LDAP   |
          +----------+--------+   +----------+--------+
                     |                     |
                     | SAML/OIDC           | LDAP
                     v                     v
+--------------------+---------------------+--------------------+
|                     Policy Engine (ISE / OPA)                     |
+--------------------+---------------------+--------------------+
        |                         |                         |
        |                         |                         |
        v                         v                         v
+-------+------+          +-------+------+          +-------+------+
|  Edge Router  |          |  Core Switch |          |  SD‑WAN Edge |
+-------+------+          +-------+------+          +-------+------+
        |                         |                         |
        |  SGACL/ACL              |  SGACL/ACL              |  IPsec/DTLS
        v                         v                         v
+-------+------+          +-------+------+          +-------+------+
|  Access Switch|          |  Access Switch|          |  Access Switch|
+-------+------+          +-------+------+          +-------+------+
        |                         |                         |
        |  802.1X + Posture      |  802.1X + Posture      |  802.1X + Posture
        v                         v                         v
+-------+------+          +-------+------+          +-------+------+
|   Endpoints  |          |   Endpoints  |          |   Endpoints  |
+--------------+          +--------------+          +--------------+
```

### 10.2. Flux de décision d’accès (PEP ↔ PDP)

```
Endpoint --> PEP (Switch) --> RADIUS Access‑Request --> PDP (ISE)
   ^                                                          |
   |<----------- Access‑Accept (SGT + SGACL) ------------------|
   |                                                          v
   |<------------------- Autorisation (grant/deny) -----------|
```

---

## 11. Commandes Cisco & Linux – Exemples concrets

### 11.1. Cisco – Activation de TrustSec sur un switch Catalyst 9300

```text
! 1. Activer le service TrustSec
cts role-based enforcement

! 2. Créer des SGT
cts role-based sgt 10 name "Finance"
cts role-based s