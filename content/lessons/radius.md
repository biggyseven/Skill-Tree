# Authentification centralisée avec RADIUS  
**Niveau : Administrateur Réseau Senior (CCIE)**  

---

## Table des matières
1. [Introduction et objectifs](#introduction-et-objectifs)  
2. [Principes fondamentaux du protocole RADIUS](#principes-fondamentaux-du-protocole-radius)  
   - 2.1. Architecture et flux de messages  
   - 2.2. Format des paquets RADIUS  
   - 2.3. Attributs RADIUS les plus courants  
3. [Déploiement typique](#déploiement-typique)  
   - 3.1. Topologie réseau (ASCII)  
   - 3.2. Scénarios d’intégration (Cisco, Linux, WLAN, VPN)  
4. [Installation et configuration de FreeRADIUS (Linux)](#installation-et-configuration-de-freeradius-linux)  
5. [Configuration d’un serveur RADIUS sur Cisco IOS/XE/XR](#configuration-dun-serveur-radius-sur-cisco)  
6. [Haute disponibilité et répartition de charge](#haute-disponibilité-et-rép)  
7. [Sécurisation du trafic RADIUS](#sécurisation-du-trafic-radius)  
8. [Comparatif RADIUS vs. TACACS+](#comparatif-radius-vs-tacacs)  
9. [Atelier de dépannage (lab)](#atelier-de-dépannage)  
10. [Bonnes pratiques & checklist de mise en production](#bonnes-pratiques)  
11. [Références & lectures complémentaires](#références)  

---

## 1. Introduction et objectifs <a name="introduction-et-objectifs"></a>

L’authentification centralisée permet de :

| Objectif | Bénéfice | Impact sur le réseau |
|----------|----------|----------------------|
| **Gestion unique des identités** | Réduction du nombre de bases d’utilisateurs locales | Simplification de la politique de sécurité |
| **Contrôle d’accès granulaire** | Attribution d’autorisations par groupe/role | Application cohérente des ACLs, QoS, VLAN |
| **Audit et conformité** | Journaux centralisés, traceabilité | Facilite les exigences ISO/PCI/DSS |
| **Scalabilité** | Ajout d’équipements sans re‑configurer les comptes | Support de milliers d’utilisateurs simultanés |

Ce cours vous donne les compétences pour :

* Concevoir une architecture RADIUS robuste (HA, répartition, sécurité).  
* Installer, paramétrer et dépanner FreeRADIUS sous Linux.  
* Configurer les serveurs RADIUS sur les plateformes Cisco (IOS, IOS‑XE, IOS‑XR, NX‑OS).  
* Intégrer RADIUS à des services d’accès réseau (802.1X, VPN, CLI, Wi‑Fi).  
* Réaliser des tests de charge et de résilience.  

---

## 2. Principes fondamentaux du protocole RADIUS <a name="principes-fondamentaux-du-protocole-radius"></a>

### 2.1. Architecture et flux de messages

```
+-----------+          +------------+          +-----------+
|   Client  | <------> |   RADIUS   | <------> |   DB/LDAP |
| (NAS)     |   Access-Request   |   Auth   |   (backend)|
+-----------+          +------------+          +-----------+
```

* **NAS (Network Access Server)** – routeur, switch, point d’accès, VPN concentrator.  
* **RADIUS Server** – traitement des requêtes, logique de décision.  
* **Backend** – base de données locale, LDAP/Active Directory, SQL.

**Séquence typique** :

1. **Access‑Request** (NAS → RADIUS) : contient User‑Name, User‑Password (chiffré avec le secret partagé), NAS‑IP‑Address, etc.  
2. **Access‑Accept** (RADIUS → NAS) : autorise l’accès, transmet les attributs (VLAN, QoS, etc.).  
3. **Access‑Reject** (RADIUS → NAS) : refuse l’accès.  
4. **Access‑Challenge** (RADIUS → NAS) : sollicite une authentification supplémentaire (OTP, EAP‑TLS).  

### 2.2. Format des paquets RADIUS

| Champ | Taille (octets) | Description |
|-------|-----------------|-------------|
| Code  | 1               | Type de message (1=Access‑Request, 2=Access‑Accept, …) |
| Identifier | 1          | Correlation du message (retransmission) |
| Length | 2              | Taille totale du paquet |
| Authenticator | 16       | Challenge/Response (MD5) |
| Attributes | Variable   | TLV (Type, Length, Value) |

**Exemple d’attribut** :

```
Type = 1 (User-Name)
Length = 14
Value = "jdoe@example.com"
```

### 2.3. Attributs RADIUS les plus courants

| Numéro | Nom | Usage typique |
|--------|-----|----------------|
| 1      | User-Name | Identifiant de connexion |
| 2      | User-Password | Mot de passe (chiffré) |
| 3      | CHAP-Password | Authentification CHAP |
| 4      | NAS-IP-Address | Adresse IP du NAS |
| 5      | NAS-Port | Port physique du NAS |
| 6      | Service-Type | Type de service (Login, Framed) |
| 7      | Framed-IP-Address | IP assignée à l’utilisateur |
| 31     | Called-Station-Id | MAC du point d’accès (802.1X) |
| 32     | Calling-Station-Id | MAC du client (802.1X) |
| 61     | Tunnel-Type | 13 = VLAN |
| 65     | Tunnel-Medium-Type | 6 = IEEE‑802 |
| 66     | Tunnel-Private-Group-ID | VLAN ID (ex: "100") |
| 79     | EAP-Message | Encapsulation EAP (TLS, PEAP…) |
| 80     | Message-Authenticator | HMAC‑MD5 pour integrity (obligatoire avec EAP) |

---

## 3. Déploiement typique <a name="déploiement-typique"></a>

### 3.1. Topologie réseau (ASCII)

```
                               +-------------------+
                               |   Authent. DB     |
                               | (AD/LDAP/SQL)     |
                               +--------+----------+
                                        |
               +------------------------+------------------------+
               |                                                 |
   +-----------+-----------+                         +-----------+-----------+
   |  RADIUS Primary (FR)  |                         | RADIUS Secondary (FR)|
   |  10.0.0.10            |                         | 10.0.0.11            |
   +-----------+-----------+                         +-----------+-----------+
               |                                                 |
   +-----------+-----------+                         +-----------+-----------+
   |  Switch Core (IOS)    |                         |  Switch Core (NX-OS) |
   |  10.0.0.1             |                         | 10.0.1.1             |
   +-----------+-----------+                         +-----------+-----------+
               |                                                 |
   +-----------+-----------+                         +-----------+-----------+
   |  Access Switches      |                         |  Access Switches      |
   |  (802.1X, VPN)        |                         | (802.1X, VPN)        |
   +-----------------------+                         +-----------------------+
```

* **Redondance** : les NAS sont configurés avec deux serveurs RADIUS (primary + secondary).  
* **Load‑Balancing** : le NAS envoie les requêtes en round‑robin ou via le **RADIUS‑proxy** (Cisco).  

### 3.2. Scénarios d’intégration

| Cas d’usage | Composant Cisco | Attributs clés | Exemple de configuration |
|------------|----------------|----------------|--------------------------|
| **802.1X filaire** | Switch Catalyst 9500 | `Tunnel-Type=13`, `Tunnel-Private-Group-ID` (VLAN) | `authentication host-mode multi-auth` |
| **Wi‑Fi WPA2‑Enterprise** | WLC / AireOS | `Calling-Station-Id`, `EAP-Message` | `dot1x authentication` |
| **VPN SSL** | ASA 5500 | `Framed-IP-Address`, `Class` | `aaa authentication ssh console radius` |
| **CLI (SSH/Telnet)** | IOS XE | `Service-Type=Login`, `Priv‑Lvl` | `aaa authentication login default group radius local` |
| **MFA (OTP)** | Any | `Access‑Challenge` + `EAP‑TLS` | `radius-server host 10.0.0.10 key secret` + `radius-server vsa send authentication` |

---

## 4. Installation et configuration de FreeRADIUS (Linux) <a name="installation-et-configuration-de-freeradius-linux"></a>

### 4.1. Prérequis

```bash
# Ubuntu 22.04 LTS
sudo apt update && sudo apt install -y freeradius freeradius-utils
# Vérifier la version
freeradius -v
# 3.2.2 (ou supérieur recommandé)
```

### 4.2. Structure des fichiers

```
/etc/freeradius/3.2/
├─ clients.conf          # définition des NAS (clients)
├─ users                 # base d’utilisateurs locale (fallback)
├─ mods-enabled/
│  ├─ sql/
│  └─ eap/
├─ mods-available/
│  ├─ sql/
│  └─ eap/
└─ radiusd.conf
```

### 4.3. Configuration d’un client (NAS)

*Fichier : `/etc/freeradius/3.2/clients.conf`*

```text
client switch01 {
    ipaddr = 10.0.0.1
    secret = SuperSecret123
    shortname = SWITCH01
    nastype = other
}
client wlc01 {
    ipaddr = 10.0.1.10
    secret = WiFiSecret!
}
```

### 4.4. Authentification contre Active Directory (LDAP)

1. Activer le module **ldap** :

```bash
sudo ln -s /etc/freeradius/3.2/mods-available/ldap /etc/freeradius/3.2/mods-enabled/
```

2. Modifier `/etc/freeradius/3.2/mods-enabled/ldap` :

```text
ldap {
    server = "ad.example.com"
    identity = "cn=radius,ou=Service Accounts,dc=example,dc=com"
    password = "RadiusPwd!"
    base_dn = "dc=example,dc=com"
    filter = "(sAMAccountName=%{%{Stripped-User-Name}:-%{User-Name}})"
    start_tls = yes
    tls {
        ca_file = /etc/ssl/certs/ca-certificates.crt
    }
}
```

3. Ajouter le module dans le **authorize** et **authenticate** :

```text
authorize {
    ldap
    ...
}
authenticate {
    Auth-Type LDAP {
        ldap
    }
    ...
}
```

### 4.5. EAP‑TLS (802.1X) – Certificats

```bash
# Générer CA interne
sudo mkdir -p /etc/freeradius/certs
cd /etc/freeradius/certs
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/C=FR/ST=Paris/L=Paris/O=MyCompany/OU=IT/CN=MyCompany-CA"

# Certificat serveur RADIUS
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr -subj "/C=FR/ST=Paris/L=Paris/O=MyCompany/OU=RADIUS/CN=radius.example.com"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650 -sha256

# Copier les certificats dans /etc/freeradius/certs
sudo cp ca.crt server.crt server.key /etc/freeradius/certs/
sudo chown freerad:freerad /etc/freeradius/certs/*
```

Modifier le module **eap** (`mods-enabled/eap`) :

```text
eap {
    default_eap_type = tls
    timer_expire = 60
    ignore_unknown_eap_types = no
    cisco_accounting_username_bug = no
    tls {
        private_key_password = whatever
        private_key_file = ${certdir}/server.key
        certificate_file = ${certdir}/server.crt
        ca_file = ${certdir}/ca.crt
        dh_file = ${certdir}/dh
        random_file = /dev/urandom
        fragment_size = 1024
        include_length = yes
        check_crl = no
    }
}
```

Redémarrer le service :

```bash
sudo systemctl restart freeradius
```

### 4.6. Test de base

```bash
# Simuler un Access-Request depuis le NAS
radclient -x 10.0.0.1 auth testing123 <<EOF
User-Name = "jdoe"
User-Password = "Password123"
NAS-IP-Address = 10.0.0.1
EOF
```

Résultat attendu : `Access-Accept` avec attributs VLAN, etc.

---

## 5. Configuration d’un serveur RADIUS sur Cisco IOS/XE/XR <a name="configuration-dun-serveur-radius-sur-cisco"></a>

### 5.1. IOS / IOS‑XE (ex. Catalyst 9500)

```text
!--- Définir le serveur RADIUS principal
radius server RADIUS1
 address ipv4 10.0.0.10 auth-port 1812 acct-port 1813
 key SuperSecret123
!--- Serveur secondaire (fallback)
radius server RADIUS2
 address ipv4 10.0.0.11 auth-port 1812 acct-port 1813
 key SuperSecret123
!--- Authentification AAA
aaa new-model
aaa group server radius RADIUS-GROUP
 server name RADIUS1
 server name RADIUS2
!--- Utiliser le groupe pour les logins
aaa authentication login default group RADIUS-GROUP local
aaa authentication enable default group RADIUS-GROUP enable
!--- Autoriser le serveur à recevoir les attributs VSA
radius-server vsa send authentication
!--- 802.1X (port‑based)
dot1x system-auth-control
interface GigabitEthernet1/0/10
 switchport mode access
 authentication port-control auto
 dot1x pae authenticator
 spanning-tree portfast
!
```

### 5.2. IOS‑XR (ex. ASR 9000)

```text
radius
 server 10.0.0.10
  auth-port 1812
  acct-port 1813
  key SuperSecret123
 server 10.0.0.11
  auth-port 1812
  acct-port 1813
  key SuperSecret123
!
aaa
 group radius RADIUS-GROUP
  server 10.0.0.10
  server 10.0.0.11
!
login authentication default group RADIUS-GROUP local
!
```

### 5.3. NX‑OS (ex. Nexus 9000)

```text
radius server RADIUS1
 address ipv4 10.0.0.10 auth-port 1812 acct-port 1813
 key SuperSecret123
radius server RADIUS2
 address ipv4 10.0.0.11 auth-port 1812 acct-port 1813
 key SuperSecret123
!
aaa group server radius RADIUS-GROUP
 server name RADIUS1
 server name RADIUS2
!
aaa authentication login default group RADIUS-GROUP local
!
```

---

## 6. Haute disponibilité et répartition de charge <a name="haute-disponibilité-et-rép"></a>

### 6.1. Méthodes de redondance

| Méthode | Description | Pro |
|---------|-------------|-----|
| **Primary/Secondary** | NAS envoie d’abord au serveur primaire, bascule en cas de timeout. | Simple, peu de trafic supplémentaire. |
| **Round‑Robin** | NAS alterne les requêtes entre plusieurs serveurs. | Répartition de charge naturelle. |
| **RADIUS Proxy (Cisco)** | Un serveur agit comme proxy et ré‑oriente vers plusieurs back‑ends. | Centralise la logique de failover, permet de masquer les back‑ends. |
| **VRRP/HSRP + IP flottante** | Un IP virtuel partagé entre deux serveurs RADIUS. | Transparence totale pour le NAS. |

### 6.2. Exemple de configuration RADIUS‑proxy (Cisco)

```text
! Définir les serveurs réels
radius server RADIUS-PRI
 address ipv4 10.0.0.10 auth-port 1812 acct-port 1813
 key SuperSecret123
!
radius server RADIUS-SEC
 address ipv4 10.0.0.11 auth-port 1812 acct-port 1813
 key SuperSecret123
!
! Créer le proxy
radius server PROXY1
 address ipv4 10.0.0.100 auth-port 1812 acct-port 1813
 key Proxy