# Authentification réseau — AAA, RADIUS, TACACS+ et 802.1X

> **Objectif** : centraliser l'authentification, l'autorisation et la comptabilité des accès réseau, comprendre RADIUS et TACACS+, et déployer 802.1X avec EAP sur un réseau filaire ou Wi-Fi.

---

## 1. AAA : trois fonctions distinctes

AAA signifie **Authentication, Authorization, Accounting**.

| Fonction | Question | Exemple |
|---|---|---|
| Authentification | Qui es-tu ? | Mot de passe, certificat, MFA |
| Autorisation | Que peux-tu faire ? | Commandes, VLAN, ACL, rôle |
| Comptabilité | Qu'as-tu fait ? | Durée, octets, commandes, échecs |

Un système qui authentifie mais n'autorise pas laisse passer tout utilisateur valide. Un système qui autorise mais ne journalise pas ne permet pas l'enquête. Les trois fonctions doivent être conçues ensemble.

```text
Utilisateur / équipement
        |
        v
   Authentificateur (switch, AP, VPN)
        |
        | RADIUS / TACACS+
        v
   Serveur AAA (FreeRADIUS, ISE, TACACS+)
        |
        +--> annuaire (AD/LDAP)
        +--> base de politiques
        +--> journaux / SIEM
```

---

## 2. Local, RADIUS et TACACS+

### 2.1 Base locale

Une base locale (`username admin secret ...`) est utile en secours ou pour un petit lab. Elle ne passe pas à l'échelle, ne centralise pas les journaux et complique la rotation des mots de passe.

### 2.2 RADIUS

RADIUS est le standard des accès réseau (RFC 2865/2866). Il est très utilisé pour le Wi-Fi, le VPN, le filaire 802.1X et les FAI.

| Caractéristique | RADIUS |
|---|---|
| Transport | UDP 1812 (auth), 1813 (accounting) |
| Chiffrement | Mot de passe utilisateur chiffré ; payload souvent clair |
| Granularité | Attributs d'accès, VLAN, ACL, sessions |
| Usage | Accès réseau, Wi-Fi, VPN, 802.1X |
| Comptabilité | Détaillée par session |

### 2.3 TACACS+

TACACS+ est souvent utilisé pour l'administration des équipements Cisco.

| Caractéristique | TACACS+ |
|---|---|
| Transport | TCP 49 |
| Chiffrement | Corps du paquet chiffré |
| Granularité | Commandes, niveaux de privilège |
| Usage | Administration CLI, autorisation fine |
| Comptabilité | Commandes et sessions |

### 2.4 Comparaison

| Critère | RADIUS | TACACS+ |
|---|---|---|
| Transport | UDP | TCP |
| Confidentialité | Partielle | Paquet entier |
| Autorisation | Réseau | Commande par commande |
| Standard | Ouvert | Cisco, largement supporté |
| Cas typique | 802.1X, VPN | Admin CLI |

On peut utiliser les deux : RADIUS pour l'accès réseau, TACACS+ pour l'administration. Les deux doivent pointer vers une source de temps fiable et journaliser vers un SIEM.

---

## 3. 802.1X : les trois rôles

802.1X est un contrôle d'accès au port avant l'obtention d'une adresse IP.

```text
Supplicant (poste) --- Authentificateur (switch/AP) --- Serveur AAA
     EAP over LAN              RADIUS
```

| Rôle | Fonction |
|---|---|
| Supplicant | Client 802.1X sur le poste |
| Authentificateur | Switch ou borne Wi-Fi qui contrôle le port |
| Serveur d'authentification | RADIUS qui valide l'identité et renvoie la politique |

Tant que l'authentification n'a pas réussi, le port reste dans un état restreint (VLAN d'attente, guest, ou bloqué).

### 3.1 EAP

EAP (Extensible Authentication Protocol) transporte la méthode d'authentification. Les variantes courantes :

| Méthode | Authentification | Remarques |
|---|---|---|
| EAP-TLS | Certificat client et serveur | Très fort, PKI nécessaire |
| PEAP | Mot de passe dans un tunnel TLS | Serveur certifié, client souvent mot de passe |
| EAP-TTLS | Tunnel TLS, méthode interne variée | Flexible |
| EAP-FAST | Tunnel protégé, provisioning | Cisco, legacy |
| EAP-MD5 | Mot de passe | Faible, à éviter |

EAP-TLS est recommandé lorsque la PKI est maîtrisée. PEAP est courant pour les parcs existants, mais il faut valider le certificat serveur pour éviter un faux portail.

### 3.2 MAB

MAB (MAC Authentication Bypass) authentifie un équipement par son adresse MAC lorsque 802.1X n'est pas possible (imprimante, caméra). C'est faible : une MAC se usurpe. MAB doit être limité aux équipements connus, avec un VLAN restreint et une surveillance.

### 3.3 CoA et changement de politique

CoA (Change of Authorization) permet au serveur RADIUS de modifier une session active : VLAN, ACL, déconnexion. Utile pour l'isolation d'un poste compromis ou l'application d'une politique après posture.

### 3.4 VLAN dynamique et profils

Le serveur peut renvoyer des attributs RADIUS :

- VLAN ;
- ACL ;
- profil de bande passante ;
- URL de portail ;
- session timeout.

Le switch applique ces attributs à la session. Une mauvaise correspondance entre attributs et configuration du switch conduit à un port non autorisé.

---

## 4. Configuration Cisco IOS

### 4.1 AAA de base

```cisco
aaa new-model
!
aaa group server radius RAD-GRP
 server name radius1
 server name radius2
!
radius server radius1
 address ipv4 10.10.1.20 auth-port 1812 acct-port 1813
 key MonSecretRadius
!
radius server radius2
 address ipv4 10.10.1.21 auth-port 1812 acct-port 1813
 key MonSecretRadius
!
aaa authentication login default group RAD-GRP local
aaa authorization exec default group RAD-GRP local
aaa accounting exec default start-stop group RAD-GRP
```

Le mot-clé `local` en secours permet une connexion si le serveur AAA est indisponible. Il faut sécuriser ce compte local et le surveiller.

### 4.2 TACACS+ pour l'administration

```cisco
tacacs server TAC1
 address ipv4 10.10.1.30
 key MonSecretTacacs
!
aaa group server tacacs+ TAC-GRP
 server name TAC1
!
aaa authentication login ADMIN group TAC-GRP local
aaa authorization commands 15 ADMIN group TAC-GRP local
aaa accounting commands 15 ADMIN start-stop group TAC-GRP
```

L'autorisation par commande permet d'interdire `reload`, `configure` ou `debug` à certains rôles.

### 4.3 802.1X sur un switch

```cisco
aaa new-model
aaa authentication dot1x default group RAD-GRP
aaa authorization network default group RAD-GRP
aaa accounting dot1x default start-stop group RAD-GRP

dot1x system-auth-control

interface GigabitEthernet1/0/10
 switchport mode access
 authentication port-control auto
 dot1x pae authenticator
 authentication host-mode multi-auth
 authentication order dot1x mab
 authentication priority dot1x mab
 mab
```

Vérification :

```cisco
show dot1x all
show authentication sessions
show authentication interface GigabitEthernet1/0/10
show aaa servers
test aaa group RAD-GRP user password new-code
```

---

## 5. FreeRADIUS : exemple de lab

### 5.1 Client et utilisateur

```conf
# /etc/freeradius/3.0/clients.conf
client switch-lab {
    ipaddr = 10.10.1.10
    secret = MonSecretRadius
    shortname = switch-lab
}
```

```conf
# /etc/freeradius/3.0/users
labuser Cleartext-Password := "MotDePasseLab"
    Reply-Message := "Bienvenue",
    Tunnel-Type = VLAN,
    Tunnel-Medium-Type = IEEE-802,
    Tunnel-Private-Group-Id = "20"
```

### 5.2 Tests

```bash
radtest labuser MotDePasseLab 127.0.0.1 0 testing123
radclient -x 10.10.1.20 auth testing123 <<< 'User-Name=labuser,User-Password=MotDePasseLab'
freeradius -X
```

Le mode debug `-X` affiche les attributs et les règles. On vérifie le secret partagé, l'adresse source, le dictionnaire et la politique de VLAN.

---

## 6. PKI et certificats

EAP-TLS repose sur des certificats. Il faut :

- une autorité de certification (CA) interne ;
- un certificat serveur RADIUS avec le bon SAN ;
- des certificats clients pour les postes ;
- une révocation (CRL/OCSP) ;
- une politique de renouvellement.

Le client doit valider le certificat du serveur. Sinon, un attaquant peut monter un faux serveur RADIUS et récolter les identifiants. Le nom du serveur dans le profil doit correspondre au SAN.

---

## 7. Sécurité et menaces

### 7.1 Rogue DHCP/RADIUS

Un attaquant peut déployer un faux serveur DHCP ou RADIUS. Les défenses : DHCP snooping, IP Source Guard, Dynamic ARP Inspection, 802.1X, certificats, segmentation.

### 7.2 Usurpation de MAC

MAB et le filtrage MAC sont contournables. On les combine avec 802.1X, la détection de changement de port et la surveillance.

### 7.3 Attaques sur les mots de passe

Le mot de passe dans PEAP doit être protégé par TLS. Les attaques hors ligne sur des hashes faibles restent possibles si la politique de mot de passe est faible. MFA et certificats réduisent le risque.

### 7.4 Journalisation et conformité

Les logs AAA doivent inclure : identité, méthode, résultat, adresse, port, raison. On les envoie à un SIEM avec NTP. Les échecs répétés doivent déclencher une alerte.

---

## 8. Dépannage AAA

### 8.1 Le serveur ne répond pas

```bash
ping 10.10.1.20
ss -lunp | grep 1812
tcpdump -ni any port 1812 or port 1813
```

Vérifier le secret, l'adresse source, le pare-feu, la route de retour et le client déclaré dans FreeRADIUS.

### 8.2 Authentification refusée

- utilisateur inconnu ou mot de passe faux ;
- méthode EAP non supportée ;
- certificat expiré ou SAN incorrect ;
- VLAN inexistant sur le switch ;
- politique de groupe qui refuse l'accès.

```cisco
show authentication sessions
show dot1x all
show aaa servers
debug dot1x all
debug radius
```

### 8.3 Le port reste en unauthorized

Vérifier `authentication port-control auto`, la configuration du supplicant, le VLAN d'attente et les attributs renvoyés. Un port peut être bloqué par une politique de posture ou par un CoA.

---

## 9. Bonnes pratiques

- centraliser les identités dans un annuaire ;
- utiliser RADIUS pour l'accès réseau et TACACS+ pour l'admin ;
- préférer EAP-TLS quand la PKI est disponible ;
- activer MFA pour les accès sensibles ;
- limiter MAB aux équipements non supplicants ;
- journaliser et superviser les échecs ;
- tester la panne du serveur AAA et le compte de secours ;
- segmenter les VLAN invités et critiques ;
- protéger les secrets partagés et les renouveler ;
- documenter les attributs RADIUS utilisés.

---

## 10. Exercices

1. Configurer un switch Cisco pour 802.1X avec RADIUS.
2. Tester un utilisateur avec `radtest` et lire les attributs.
3. Configurer un VLAN dynamique renvoyé par RADIUS.
4. Mettre en place TACACS+ pour autoriser seulement les commandes de diagnostic.
5. Diagnostiquer un port qui reste unauthorized.
6. Comparer EAP-TLS et PEAP.
7. Configurer un compte local de secours et tester la panne AAA.
8. Analyser un échec de certificat dans les logs.
9. Mettre en place MAB pour une imprimante et expliquer ses limites.
10. Rédiger une procédure de rotation des secrets RADIUS/TACACS+.
