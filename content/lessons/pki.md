# Cours Intensif – PKI et Certificats (TLS/SSL)  
**Niveau : Administrateur Réseau Senior (CCIE)**  
**Durée estimée : 2 jours (16 h) – 10 000+ caractères**  

---  

## Table des matières  

| # | Section | Durée approximative |
|---|---------|---------------------|
| 1 | Introduction à la PKI | 45 min |
| 2 | Architecture et composants | 1 h 30 |
| 3 | Algorithmes cryptographiques (RSA, ECC, …) | 1 h |
| 4 | Cycle de vie d’un certificat | 2 h |
| 5 | TLS / SSL – Protocoles et Handshake | 2 h |
| 6 | Implémentation sur les équipements Cisco | 2 h |
| 7 | Implémentation sous Linux (OpenSSL, GnuTLS) | 1 h 30 |
| 8 | Gestion des CA (Root, Sub‑CA, Offline) | 1 h |
| 9 | Bonnes pratiques, Hardening & Conformité | 45 min |
|10| Atelier de dépannage (lab) | 2 h |
|11| Annexes (références, scripts, FAQ) | 30 min |

---  

## 1. Introduction à la PKI  

### 1.1 Définitions clés  

| Terme | Définition |
|-------|------------|
| **PKI** (Public Key Infrastructure) | Ensemble de politiques, procédures, matériels et logiciels permettant la création, la gestion, la distribution, l’utilisation, le stockage et la révocation de certificats numériques. |
| **CA** (Certificate Authority) | Entité qui signe les certificats après avoir validé l’identité du demandeur. |
| **RA** (Registration Authority) | Point de contact qui authentifie les requêtes de certificats avant transmission à la CA. |
| **CRL** (Certificate Revocation List) | Liste publiée contenant les numéros de série des certificats révoqués. |
| **OCSP** (Online Certificate Status Protocol) | Service de validation en temps réel d’un certificat. |
| **PKCS** (Public‑Key Cryptography Standards) | Famille de standards (PKCS#1, #7, #10, #12, …) décrivant formats, échanges et enveloppages. |
| **TLS** (Transport Layer Security) | Successeur de SSL, protocole de sécurisation de la couche transport. |

### 1.2 Pourquoi la PKI ?  

- **Authenticité** : Garantir l’identité du serveur/client.  
- **Intégrité** : Détecter toute altération du trafic.  
- **Confidentialité** : Chiffrement de bout en bout.  
- **Non‑répudiation** : Preuve juridique de l’échange (signature numérique).  

---  

## 2. Architecture et composants  

```
+-------------------+       +-------------------+       +-------------------+
|  Root CA (offline)| ----> |  Sub‑CA (online)  | ----> |  RA / Enrollment  |
+-------------------+       +-------------------+       +-------------------+
        ^                         ^                         |
        |                         |                         v
+-------------------+       +-------------------+       +-------------------+
|  CRL / OCSP Responder          |   Certificate DB  |   End‑Entity (Server/Client)
+-------------------+       +-------------------+       +-------------------+
```

### 2.1 Topologies usuelles  

| Topologie | Avantages | Inconvénients |
|-----------|-----------|----------------|
| **Flat (single CA)** | Simplicité, déploiement rapide | Point unique de défaillance, moindre granularité de contrôle |
| **Hierarchical (Root + Sub‑CA)** | Séparation des responsabilités, isolation du Root (offline) | Complexité de gestion, besoin de réplication CRL/OCSP |
| **Mesh (multiple cross‑signed CAs)** | Haute disponibilité, fédération | Gestion de la confiance plus lourde, risque de boucles de validation |

### 2.2 Stockage des clés privées  

| Méthode | Sécurité | Performance | Cas d’usage |
|---------|----------|-------------|-------------|
| **HSM (Hardware Security Module)** | Très élevée (tamper‑evident, FIPS 140‑2 Level 3/4) | Latence légèrement supérieure | PKI d’entreprise, CA offline |
| **Smartcard / TPM** | Élevée, portable | Dépend du lecteur | Authentification d’utilisateurs |
| **Software keystore (OpenSSL, Java keystore)** | Variable (chiffrement AES‑256) | Rapide | Dev / test, CA interne non‑critique |

---  

## 3. Algorithmes cryptographiques  

| Algorithme | Type | Taille de clé typique | Sécurité (bits) | Usage recommandé |
|------------|------|-----------------------|----------------|------------------|
| RSA | Asymétrique (facteur) | 2048 bits (minimum), 3072 bits, 4096 bits | 112 bits (2048) | Signatures, chiffrement de clé symétrique |
| ECC (secp256r1, secp384r1) | Asymétrique (courbe elliptique) | 256 bits (secp256r1) | 128 bits | Signatures, ECDHE, plus efficace sur CPU |
| DSA | Asymétrique (signature) | 2048 bits | 112 bits | Déprécié, à éviter en production |
| SHA‑2 (256/384/512) | Hachage | – | 128‑256 bits | Hachage de messages, signatures |
| SHA‑3 | Hachage | – | 128‑256 bits | Alternative moderne, peu d’adoption yet |
| AES‑GCM | Symétrique (chiffrement + authentification) | 128/256 bits | 128/256 bits | Cipher suite TLS 1.3 |

> **Note** : Depuis 2023, la plupart des CA recommandent **ECC** (P‑256 ou P‑384) pour réduire la charge CPU sur les appareils IoT et les serveurs à forte densité de connexions TLS.

---  

## 4. Cycle de vie d’un certificat  

### 4.1 Phases  

1. **Planification** – Politique de certification (CP), profil de certificat (CPS).  
2. **Provisioning** – Génération de la CSR (Certificate Signing Request).  
3. **Validation** – RA vérifie l’identité (OV, EV, DV).  
4. **Issuance** – CA signe et délivre le certificat.  
5. **Installation** – Déploiement sur le serveur/client.  
6. **Renouvellement** – Avant expiration, nouvelle CSR ou re‑use de la clé.  
7. **Révocation** – CRL/OCSP, raisons (keyCompromise, CACompromise, affiliationChanged, superseded, cessationOfOperation).  
8. **Expiration** – Le certificat devient invalide, doit être retiré ou renouvelé.  

### 4.2 Formats de certificats  

| Extension | Description | MIME Type |
|-----------|-------------|-----------|
| **.pem** | Base64 ASCII avec header `-----BEGIN CERTIFICATE-----` | `application/x-pem-file` |
| **.der** | ASN.1 DER binaire | `application/octet-stream` |
| **.pfx / .p12** | PKCS#12 (cert + clé + chaîne) chiffré | `application/x-pkcs12` |
| **.crt** | Souvent PEM ou DER selon le contexte | `application/x-x509-ca-cert` |
| **.cer** | Variante PEM/DER, dépend du système | `application/pkix-cert` |

### 4.3 Commandes OpenSSL essentielles  

```bash
# 1. Générer une clé RSA 2048 bits
openssl genpkey -algorithm RSA -out server.key -pkeyopt rsa_keygen_bits:2048

# 2. Générer une clé ECC (secp384r1)
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:secp384r1 -out server_ec.key

# 3. Créer une CSR (RSA) avec SAN
cat > csr.conf <<EOF
[ req ]
default_bits        = 2048
prompt              = no
default_md          = sha256
distinguished_name  = dn
req_extensions      = req_ext

[ dn ]
C=FR
ST=Île‑de‑France
L=Paris
O=Acme Corp
OU=IT
CN=www.acme.fr
emailAddress=admin@acme.fr

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1   = www.acme.fr
DNS.2   = acme.fr
IP.1    = 192.0.2.10
EOF

openssl req -new -key server.key -config csr.conf -out server.csr
```

```bash
# 4. Signer la CSR avec une CA interne (root-ca.key/root-ca.crt)
openssl x509 -req -in server.csr -CA root-ca.crt -CAkey root-ca.key \
  -CAcreateserial -out server.crt -days 825 -sha256 -extfile csr.conf -extensions req_ext
```

```bash
# 5. Convertir en PKCS#12 (inclut chaîne de confiance)
cat > chain.pem <<EOF
-----BEGIN CERTIFICATE-----
# Root CA
$(cat root-ca.crt)
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
# Intermediate CA
$(cat sub-ca.crt)
-----END CERTIFICATE-----
EOF

openssl pkcs12 -export -inkey server.key -in server.crt -certfile chain.pem \
  -name "www.acme.fr" -out server.p12
```

```bash
# 6. Vérifier la chaîne et la date
openssl verify -CAfile root-ca.crt -untrusted sub-ca.crt server.crt
openssl x509 -noout -dates -in server.crt
```

---  

## 5. TLS / SSL – Protocoles et Handshake  

### 5.1 Versions supportées  

| Version | Année | RFC | Statut (2026) | Cipher suites recommandées |
|---------|-------|-----|---------------|----------------------------|
| SSL 2.0 | 1995 | 6176 | Obsolète (déprécié) | — |
| SSL 3.0 | 1996 | 6101 | Obsolète (POODLE) | — |
| TLS 1.0 | 1999 | 2246 | Obsolète (PCI DSS 2024) | — |
| TLS 1.1 | 2006 | 4346 | Obsolète (POODLE‑TLS) | — |
| TLS 1.2 | 2008 | 5246 | Supporté, mais migrer | TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 |
| TLS 1.3 | 2018 | 8446 | Recommandé (défaut sur la plupart) | TLS_AES_128_GCM_SHA256, TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256 |

### 5.2 Schéma simplifié du handshake TLS 1.2 (RSA)  

```
Client                                          Server
  |   ClientHello (ciphers, extensions)          |
  |--------------------------------------------->|
  |                                                |
  |   ServerHello (chosen cipher, session ID)    |
  |   Certificate (chain)                        |
  |   ServerKeyExchange (if DHE/ECDHE)           |
  |   ServerHelloDone                            |
  |<---------------------------------------------|
  |                                                |
  |   ClientKeyExchange (pre‑master secret)      |
  |   ChangeCipherSpec                           |
  |   Finished                                   |
  |--------------------------------------------->|
  |                                                |
  |   ChangeCipherSpec                           |
  |   Finished                                   |
  |<---------------------------------------------|
  |   Application Data (encrypted)               |
```

### 5.3 Schéma du handshake TLS 1.3 (0‑RTT possible)  

```
Client                                              Server
  |   ClientHello (supported groups, key_shares, early_data?) |
  |--------------------------------------------------------->|
  |   ServerHello (selected cipher, key_share)               |
  |   EncryptedExtensions                                   |
  |   CertificateRequest? (optional)                        |
  |   Certificate                                           |
  |   CertificateVerify                                     |
  |   Finished                                              |
  |<--------------------------------------------------------|
  |   Finished                                              |
  |-------------------------------------------------------->|
  |   Application Data (encrypted)                          |
```

> **Remarque** : TLS 1.3 supprime les suites `RSA`‑only pour l’échange de clés, ne conserve que **(EC)DHE** + **AEAD**.  

### 5.4 Extensions critiques  

| Extension | Fonction | Exemple d’utilisation |
|-----------|----------|-----------------------|
| **Server Name Indication (SNI)** | Permet à un serveur d’héberger plusieurs certificats sur la même IP | `www.example.com` vs `api.example.com` |
| **ALPN (Application‑Layer Protocol Negotiation)** | Négocie HTTP/2, HTTP/3, etc. | `h2`, `h2c`, `http/1.1` |
| **OCSP Stapling** | Le serveur envoie la réponse OCSP avec le handshake | Réduit la latence de validation |
| **Signed Certificate Timestamp (SCT)** | Transparence des certificats (CT) | Google CT logs |
| **Key Share** | Échange de clés Diffie‑Hellman/ECDHE dans TLS 1.3 | `x25519`, `secp256r1` |

---  

## 6. Implémentation sur les équipements Cisco  

### 6.1 TLS sur IOS / IOS‑XE (ex. serveur HTTPS, SSH, EEM)  

```text
! 1. Créer une PKI trustpoint (CA interne ou externe)
crypto pki trustpoint MY_CA
 enrollment url http://pki.example.com/ca
 revocation-check crl
 rsakeypair MY_CA_KEY label MY_CA_KEY
!

! 2. Enrollement de la clé et du certificat (auto‑sign ou via CA)
crypto pki enroll MY_CA
  usage ssl-client
  subject-name CN=router1.example.com,O=Acme Corp,L=Paris,ST=Île‑de‑France,C=FR
  rsa keypair MY_CA_KEY label MY_CA_KEY
!

! 3. Configurer le serveur HTTPS (IOS‑XE 16.12+)
ip http secure-server
ip http authentication local
ip http secure-port 443
ip http secure-ciphersuite high
ip http secure-trustpoint MY_CA
!

! 4. Activer TLS sur SSH (v2) – utilisation du même trustpoint
crypto key generate rsa usage-keys label SSH_KEY modulus 4096
ip ssh rsa keypair-name SSH_KEY
ip ssh version 2
ip ssh server algorithm encryption aes256-ctr
ip ssh server algorithm mac hmac-sha2-256
ip ssh server algorithm publickey rsa-sha2-512
ip ssh server algorithm key-exchange ecdh-sha2-nistp384
ip ssh server trustpoint MY_CA
!

! 5. Vérifier le certificat installé
show crypto pki certificates MY_CA
show ip http server status
```

### 6.2 TLS termination sur un **Cisco ASA** (firewall)  

```text
! 1. Importer le certificat et la clé (PKCS#12)
crypto ca import outside_ca pkcs12 mycert.p12 password cisco123

! 2. Créer un trustpoint pour le serveur SSL VPN
crypto ca trustpoint outside_ca
 enrollment terminal
 subject-name CN=vpn.acme.fr,O=Acme Corp,C=FR
 crl configure
!

! 3. Associer le certificat au listener SSL VPN
webvpn
 enable outside
 anyconnect image disk0:/anyconnect-win-4.10.06086.pkg 1
 anyconnect enable
 ssl trust-point outside_ca outside
!

! 4. Activer OCSP stapling (ASA 9.9+)
crypto ca trustpoint outside_ca
 ocsp url http://ocsp.example.com
 ocsp use-local-responder
!
```

### 6.3 Vérification et débogage  

```text
show crypto pki certificates
show crypto ca certificates
show crypto ca trustpoints
debug crypto ca transaction
debug crypto pki enrollment
```

---  

## 7. Implémentation sous Linux  

### 7.1 Serveur web Nginx avec certificat ECC  

```bash
# 1. Générer une clé ECC P‑256 et un CSR
openssl ecparam -genkey -name prime256v1 -out nginx_ec.key
openssl req -new -key nginx_ec.key -out nginx.csr \
  -subj "/C=FR/ST=Île-de-France/L=Paris/O=Acme Corp/OU=IT/CN=www.acme.fr"

# 2. Signer avec la CA interne (root-ca.key/root-ca.crt)
openssl x509 -req -in nginx.csr -CA root-ca.crt -CAkey root-ca.key \
  -CAcreateserial -out nginx.crt -days 825 -sha256 -extfile <(printf "subjectAltName=DNS:www.acme.fr,DNS:acme.fr,IP:192.0.2.10")

# 3. Configurer Nginx
cat > /etc/nginx/conf.d/ssl_acme.conf <<EOF
server {
    listen 443 ssl http2;
    server_name www.acme.fr acme.fr;

    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key