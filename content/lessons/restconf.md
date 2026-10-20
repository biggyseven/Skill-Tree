# Cours Intensif – API RESTCONF & NETCONF  
**Niveau : Administrateur Réseau Senior (CCIE)**  
**Durée estimée : 2 jours (16 h)**  

---

## Table des matières
| # | Section | Durée approximative |
|---|---------|---------------------|
| 1 | Introduction & concepts fondamentaux | 30 min |
| 2 | Architecture NETCONF | 1 h |
| 3 | Modélisation YANG | 1 h 30 min |
| 4 | Session NETCONF – transports & sécurités | 1 h |
| 5 | Opérations NETCONF (RPC, notifications) | 1 h |
| 6 | RESTCONF – principes & mapping YANG ↔ HTTP | 1 h |
| 7 | Authentification & sécurisation (TLS, OAuth2, JWT) | 45 min |
| 8 | Comparaison NETCONF vs RESTCONF | 30 min |
| 9 | Mise en pratique – Lab Cisco IOS‑XE, IOS‑XR, NX‑OS, Junos, Linux (sysrepo) | 4 h |
|10| Atelier de dépannage avancé | 2 h |
|11| Optimisation & bonnes pratiques | 45 min |
|12| Annexes : références, scripts, cheat‑sheet | 30 min |

> **Objectif** : Maîtriser la configuration, la lecture, la surveillance et le dépannage d’infrastructures réseau via les API NETCONF & RESTCONF, en s’appuyant sur les modèles YANG, les transports sécurisés, et les outils d’automatisation (Ansible, Python, Go).  

---

## 1. Introduction & concepts fondamentaux  

| Concept | Description | RFC / IETF |
|---------|-------------|------------|
| **NETCONF** | Protocole de gestion de configuration réseau orienté *RPC* (Remote Procedure Call) fonctionnant sur SSH (ou TLS). | RFC 6241 |
| **RESTCONF** | Interface REST‑like qui expose les modèles YANG via HTTP/HTTPS (GET, POST, PUT, PATCH, DELETE). | RFC 8040 |
| **YANG** | Langage de modélisation de données, base de la plupart des API modernes. | RFC 7950 |
| **Datastore** | *candidate*, *running*, *startup*, *operational*. | RFC 6241 §3.2 |
| **Locking** | Verrouillage de datastore pour éviter les conflits de configuration. | RFC 6241 §7.4 |
| **Notifications** | Push d’événements du dispositif vers le client (NETCONF/RESTCONF). | RFC 5277 (NETCONF) ; RFC 8641 (RESTCONF) |

> **Pourquoi ces API ?**  
- **Programmabilité** : décorrélation du CLI, automatisation CI/CD.  
- **Interopérabilité** : même modèle YANG exploité par plusieurs transports.  
- **Sécurité** : chiffrement natif (SSH/TLS), authentification forte, auditabilité.

---

## 2. Architecture NETCONF  

```
+-------------------+          +-------------------+
|   NETCONF Client  |  SSH/TLS |   NETCONF Server  |
| (Ansible, pyang)  |<-------->| (Cisco IOS‑XE,   |
|  +-------------+  |          |  IOS‑XR, Junos…) |
|  |  YANG Lib   |  |          +-------------------+
|  +-------------+  |
+-------------------+
        |
        |  RPC (XML)
        v
   <rpc message-id="101">
       <edit-config>
           <target><running/></target>
           <config> … </config>
       </edit-config>
   </rpc>
```

### 2.1. Couche transport  
| Transport | Port | Sécurité | Usage typique |
|-----------|------|----------|---------------|
| SSH       | 22   | Authentification par clé/pub‑key, chiffrement symétrique | Déploiement standard, compatible avec la plupart des équipements |
| TLS       | 830  | Certificats X.509, Mutual TLS | Environnements où SSH est désactivé ou pour interopérabilité avec des appliances non‑SSH |
| BEEP (obsolete) | 102 | – | Historique, rarement utilisé |

### 2.2. Message framing (RFC 6242)  
- **Chunked framing** (`\n##\n`) ou **netconf:base:1.0** (EOF `]]>]]>`).  
- Exemple d’envoi d’un *hello* :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <capabilities>
    <capability>urn:ietf:params:netconf:base:1.0</capability>
    <capability>urn:ietf:params:netconf:base:1.1</capability>
    <capability>urn:ietf:params:netconf:capability:candidate:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:confirmed-commit:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</capability>
    <capability>urn:ietf:params:netconf:capability:url:1.0?scheme=file,ftp,http,https</capability>
  </capabilities>
  <session-id>12345</session-id>
</hello>]]>]]>
```

---

## 3. Modélisation YANG  

### 3.1. Structure d’un module YANG  

```yang
module cisco‑interface‑config {
  yang-version 1.1;
  namespace "http://cisco.com/ns/yang/Cisco-Interface-Config";
  prefix ci;

  import ietf‑interfaces { prefix if; }

  organization "Cisco Systems";
  description
    "Modèle de configuration des interfaces Ethernet.";

  revision 2024-06-01 {
    description "Initial release.";
  }

  augment "/if:interfaces/if:interface" {
    leaf speed {
      type enumeration {
        enum "10M"   { value 10; }
        enum "100M"  { value 100; }
        enum "1G"    { value 1000; }
        enum "10G"   { value 10000; }
      }
      description "Interface speed.";
    }
    leaf duplex {
      type enumeration { enum full; enum half; }
      default "full";
    }
  }
}
```

### 3.2. Principaux modules standards (extraits)  

| Module | Namespace | Fonction | Exemple d’utilisation |
|--------|-----------|----------|-----------------------|
| `ietf-interfaces` | `urn:ietf:params:xml:ns:yang:ietf-interfaces` | Gestion des interfaces L2/L3 | `<interface><name>GigabitEthernet0/0</name>…</interface>` |
| `ietf-ip` | `urn:ietf:params:xml:ns:yang:ietf-ip` | Config IP, routes | `<ipv4><address><ip>10.0.0.1</ip>…</address></ipv4>` |
| `ietf-routing` | `urn:ietf:params:xml:ns:yang:ietf-routing` | Table de routage | `<routing-instance><name>default</name>…</routing-instance>` |
| `ietf-system` | `urn:ietf:params:xml:ns:yang:ietf-system` | Gestion du système (users, clock) | `<system><hostname>router1</hostname></system>` |
| `ietf-bfd` | `urn:ietf:params:xml:ns:yang:ietf-bfd` | BFD session | `<bfd><session><local-discriminator>…</local-discriminator></session></bfd>` |

### 3.3. Compilation & validation  

```bash
# Vérifier la syntaxe d’un module YANG
pyang --ietf --print-error-code cisco-interface-config.yang

# Générer la tree diagram (ASCII) pour le module
pyang --tree-path cisco-interface-config.yang
```

---

## 4. Session NETCONF – transports & sécurités  

### 4.1. Établir une session SSH (OpenSSH)  

```bash
# Générer une paire de clés (client)
ssh-keygen -t ed25519 -f ~/.ssh/netconf_id_ed25519 -N ""

# Copie de la clé publique sur le routeur (IOS‑XE)
ssh admin@10.0.0.1 "configure terminal
  ip ssh pubkey-chain
    username admin
      key-string
$(cat ~/.ssh/netconf_id_ed25519.pub)
      exit
    exit
  exit"

# Test de connexion NETCONF via ncclient (Python)
python3 - <<'PY'
from ncclient import manager
with manager.connect(host='10.0.0.1',
                    port=22,
                    username='admin',
                    hostkey_verify=False,
                    key_filename='~/.ssh/netconf_id_ed25519',
                    look_for_keys=False,
                    allow_agent=False) as m:
    print(m.server_capabilities)
PY
```

### 4.2. Session TLS (OpenSSL)  

```bash
# Générer un certificat auto‑signé (CA + serveur)
openssl req -new -x509 -days 365 -nodes -out ca.crt -keyout ca.key -subj "/CN=MyNetconfCA"
openssl req -newkey rsa:2048 -nodes -keyout server.key -out server.csr -subj "/CN=router1"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365

# Copier server.crt / server.key sur le routeur (ex. Cisco IOS‑XR)
# Exemple de configuration IOS‑XR
crypto pki trustpoint NETCONF-CA
 enrollment selfsigned
 subject-name "CN=MyNetconfCA"
 revocation-check none
!
crypto pki certificate chain NETCONF-CA
 certificate ca.crt
!
netconf-yang
 transport tls 830
  certificate NETCONF-CA
  trustpoint NETCONF-CA
!
```

### 4.3. Verrouillage (lock) & validation  

```xml
<rpc message-id="102">
  <lock>
    <target>
      <candidate/>
    </target>
  </lock>
</rpc>]]>]]>
```

Après le **commit** :

```xml
<rpc message-id="103">
  <commit>
    <confirmed/>
    <confirm-time>600</confirm-time>
  </commit>
</rpc>]]>]]>
```

---

## 5. Opérations NETCONF (RPC, notifications)  

| RPC | Description | Exemple minimal |
|-----|-------------|-----------------|
| `<get>` | Lecture d’un datastore (running, candidate, operational). | `<get><filter type="subtree"><interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/></filter></get>` |
| `<get-config>` | Lecture d’un *config* datastore (running, candidate, startup). | idem que `<get>` mais cible `<target><running/></target>` |
| `<edit-config>` | Modifications atomiques. | `<edit-config><target><candidate/></target><config>…</config></edit-config>` |
| `<copy-config>` | Copie d’un datastore vers un autre (ex. candidate → running). | `<copy-config><target><running/></target><source><candidate/></source></copy-config>` |
| `<delete-config>` | Suppression d’un datastore (rare, ex. startup). | `<delete-config><target><startup/></target></delete-config>` |
| `<lock>` / `<unlock>` | Verrouillage du datastore. | `<lock><target><candidate/></target></lock>` |
| `<close-session>` | Fermer proprement la session. | `<close-session/>` |
| `<kill-session>` | Forcer la fermeture d’une session (admin). | `<kill-session><session-id>123</session-id></kill-session>` |
| `<commit>` | Appliquer les changements du candidate. | `<commit/>` |
| `<discard-changes>` | Annuler les changements non‑committed. | `<discard-changes/>` |
| `<validate>` | Vérifier la validité du candidate avant commit. | `<validate><source><candidate/></source></validate>` |
| `<cancel-commit>` | Annuler un commit confirmé. | `<cancel-commit/>` |

### 5.1. Notifications (NETCONF Event)  

```xml
<rpc message-id="200">
  <create-subscription xmlns="urn:ietf:params:xml:ns:netconf:notification:1.0">
    <stream>NETCONF</stream>
    <filter type="subtree">
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
    </filter>
  </create-subscription>
</rpc>]]>]]>
```

Le serveur envoie ensuite des `<notification>` encodées en XML dès qu’un changement d’état se produit.

---

## 6. RESTCONF – principes & mapping YANG ↔ HTTP  

### 6.1. Architecture (schéma ASCII)

```
+-------------------+   HTTPS   +-------------------+
|  RESTCONF Client  |<--------->|  RESTCONF Server  |
|  (curl, Postman,  |  JSON/YANG|  (Cisco, Junos,   |
|   Python requests)          |  sysrepo, etc.)   |
+-------------------+           +-------------------+
        |                                 |
        | GET /restconf/data/<path>       |
        | POST /restconf/data/<path>      |
        | PATCH /restconf/data/<path>     |
        | DELETE /restconf/data/<path>    |
        v                                 v
   HTTP/1.1 200 OK + JSON/YANG payload
```

### 6.2. Mapping des opérations  

| RESTCONF Method | NETCONF RPC équivalent | Exemple d’URL | Corps (JSON) |
|-----------------|------------------------|---------------|--------------|
| `GET` | `<get>` / `<get-config>` | `/restconf/data/ietf-interfaces:interfaces` | – |
| `POST` | `<edit-config>` (create) | `/restconf/data/ietf-interfaces:interfaces/interface=Gig0/0` | `{ "ietf-interfaces:interface": { "name":"Gig0/0","type":"iana-if-type:ethernetCsmacd","enabled":true } }` |
| `PUT` | `<edit-config>` (replace) | idem | même que POST, mais remplace entièrement l’objet |
| `PATCH` | `<edit-config>` (merge) | idem | `{ "ietf-interfaces:interface": { "description":"Uplink to Core" } }` |
| `DELETE` | `<edit-config>` (delete) | `/restconf/data/ietf-interfaces:interfaces/interface=Gig0/0` | – |
| `OPTIONS` | *none* (capabilities) | `/restconf/` | – |
| `GET` (capabilities) | `<hello>` | `/restconf/.well-known/host-meta` ou `/restconf/` | JSON list of capabilities |

### 6.3. Exemples concrets  

#### 6.3.1. Lecture d’une interface (cURL)

```bash
curl -k -u admin:password \
  -H "Accept: application/yang-data+json" \
  https://10.0.0.1/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet0/0
```

#### 6.3.2. Création d’une interface VLAN (POST)

```bash
curl -k -u admin:password \
  -H "Content-Type: application/yang-data+json" \
  -X POST \
  -d '{
        "ietf-interfaces:interface": {
          "name": "Vlan100",
          "type": "iana-if-type:l2vlan",
          "enabled": true,
          "ietf-ip:ipv4": {
            "address": [
              {
                "ip": "192.168.100.1",
                "netmask": "255.255.255.0"
              }
            ]
          }
        }
      }' \
  https://10.0.0.1/restconf/data/ietf-interfaces:interfaces
```

#### 6.3.3. Patch d’une description (PATCH)

```bash
curl -k -u admin:password \
  -H "Content-Type: application/yang-patch+json" \
  -X PATCH \
  -d '[ {"op":"replace","path":"/ietf-interfaces:interface[name=GigabitEthernet0/0]/description","value":"Uplink to DC"} ]' \
  https://10.0.0.1/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet0/0
```

> **Note** : Le type `application/yang-patch+json` suit la RFC 8072 (JSON Patch) mais avec des contraintes YANG (type‑checking, leaf‑ref validation).

---

## 7. Authentification & sécurisation  

| Méthode | Transport | Avantages | Limites |
|---------|-----------|-----------|---------|
| **SSH key** | NETCONF (SSH) | Pas de mots‑de‑passe en clair, MFA possible via *ssh‑agent* | Gestion des clés à grande échelle |
| **TLS mutual** | NETCONF (TLS) | Authentification forte, compatible avec PKI d’entreprise | Complexité de la PKI |
| **Basic Auth** | RESTCONF (HTTPS) | Simple à mettre en place | Mot‑de‑passe en base64 (pas chiffré) – à éviter en prod |
| **OAuth2 / JWT** | RESTCONF (HTTPS) | Token limité dans le temps, délégation | Nécessite un serveur d’autorisation (Keycloak, Athenz) |
| **AAA (RADIUS/TACACS+)** | NETCONF/RESTCONF | Centralisation des comptes | Dépend du dispositif supportant AAA pour NETCONF |

### 7.1. Exemple d’implémentation OAuth2 (Keycloak)  

