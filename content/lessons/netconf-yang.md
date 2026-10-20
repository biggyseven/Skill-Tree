# Cours Intensif – NETCONF, YANG & RESTCONF  
**Niveau : Administrateur Réseau Senior (CCIE)**  

> **Objectif** – Maîtriser les protocoles de gestion programmée NETCONF/RESTCONF, le langage de modélisation YANG, leurs implémentations Cisco et Linux, ainsi que les bonnes pratiques de déploiement et de dépannage.

---  

## 1. Contexte & Pourquoi ces technologies ?

| Limite des modèles traditionnels | Solution apportée par NETCONF/YANG/RESTCONF |
|----------------------------------|--------------------------------------------|
| **CLI / SNMP** – statique, difficile à automatiser, manque de validation de schéma | **NETCONF** – protocole transactionnel (RPC) avec validation de modèle YANG |
| **SNMP v2c** – sécurité faible, MIBs peu lisibles | **RESTCONF** – API RESTful, JSON/YANG, TLS/HTTPS natif |
| **Configuration manuelle** – risque d’incohérence | **YANG** – modèle de données déclaratif, contraintes, réutilisable |
| **Interopérabilité** – vendors différents, syntaxes propres | **IETF standards** – interopérabilité multi‑vendor |

Ces trois briques forment le socle d’une **Network Automation** moderne, « Infrastructure as Code » (IaC) et de la **Programmabilité** du réseau (SD‑N, intent‑based networking).

---  

## 2. NETCONF – Le protocole de configuration

### 2.1. Principes fondamentaux  

* **Transport** : TCP (port 830) ou SSH (port 22) – le plus sûr est SSH.  
* **Modèle de données** : YANG (RFC 7950).  
* **Messages** : XML‑encodé, enveloppés dans des **RPC**.  
* **Opérations de base** : `get`, `get-config`, `edit-config`, `copy-config`, `delete-config`, `lock`, `unlock`, `close-session`, `kill-session`.  
* **Capacités** – chaque serveur annonce ses *capabilities* (ex. : `urn:ietf:params:netconf:base:1.1`).  

### 2.2. Session NETCONF – Diagramme ASCII  

```
+-------------------+          SSH (port 22)          +-------------------+
|   NETCONF Client  | <-----------------------------> |   NETCONF Server  |
|   (ncclient,      |   1. SSH Handshake + Encryption  |   (Cisco IOS XE, |
|    pyang, curl…)  |   2. <hello> exchange            |    NX‑OS, etc.)   |
|                   |   3. RPC/Reply (XML)             |                   |
+-------------------+                                 +-------------------+
```

### 2.3. Exemple de session `edit-config` (Cisco IOS XE)

```bash
# Sur le client (Linux) – utilisation de ncclient (Python)
$ python3 - <<'PY'
from ncclient import manager
import xmltodict

with manager.connect(host='10.0.0.1',
                    port=830,
                    username='admin',
                    password='cisco123',
                    hostkey_verify=False) as m:

    # Verrouillage du datastore candidate
    m.lock('candidate')

    # Payload XML – création d'une interface Loopback10
    config = """
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback>
            <name>10</name>
            <description>Loopback via NETCONF</description>
            <ip>
              <address>
                <primary>
                  <address>192.0.2.10</address>
                  <mask>255.255.255.255</mask>
                </primary>
              </address>
            </ip>
          </Loopback>
        </interface>
      </native>
    </config>
    """

    # Envoi de l'édition
    m.edit_config(target='candidate', config=config)

    # Validation et commit
    m.commit()
    m.unlock('candidate')
PY
```

### 2.4. Commandes Cisco IOS XE pour activer NETCONF  

| Commande | Description |
|----------|-------------|
| `netconf-yang` | Active le serveur NETCONF/YANG (IOS XE 16.9+). |
| `netconf-yang ssh` | Force l’usage du transport SSH (recommandé). |
| `netconf-yang commit-queue` | Autorise le commit‑queue (multi‑user). |
| `show netconf-yang sessions` | Liste les sessions actives. |
| `show netconf-yang capabilities` | Affiche les capabilities du serveur. |

Exemple complet :

```bash
conf t
 netconf-yang
 netconf-yang ssh
 netconf-yang commit-queue
end
write memory
```

---  

## 3. YANG – Langage de modélisation de données

### 3.1. Syntaxe de base (extrait d’un module)

```yang
module cisco‑interface {
  yang-version 1.1;
  namespace "http://cisco.com/ns/yang/cisco-interface";
  prefix ci;

  import ietf‑interfaces { prefix if; }

  organization "Cisco Systems";
  contact "netdev@cisco.com";

  description
    "Modélise les interfaces de type Loopback avec des attributs enrichis.";

  revision 2024-06-01 {
    description "Version initiale.";
  }

  augment "/if:interfaces/if:interface" {
    when "../if:type = 'iana-if-type:softwareLoopback'";
    description "Ajoute des paramètres spécifiques aux Loopbacks Cisco.";
    leaf description {
      type string;
      description "Description libre de l’interface.";
    }
    leaf-list allowed‑vlans {
      type uint16 {
        range "1..4094";
      }
      description "VLANs autorisés sur le port (pour les L2).";
    }
  }
}
```

### 3.2. Principaux concepts  

| Concept | Rôle |
|---------|------|
| **module / submodule** | Conteneur logique du modèle. |
| **namespace** | Identifiant unique (URI). |
| **prefix** | Alias pour le namespace dans le XML/JSON. |
| **container** | Regroupe des nodes (similaire à un objet). |
| **list** | Tableau d’objets, clé obligatoire (`key`). |
| **leaf / leaf‑list** | Attribut simple (scalar). |
| **choice / case** | Mutuellement exclusif. |
| **augment** | Extension d’un modèle existant (ex. : IETF‑interfaces). |
| **grouping** | Réutilisation de fragments de modèle. |
| **typedef** | Type de données réutilisable. |
| **must / when** | Contraintes XPath. |
| **status** | `current`, `deprecated`, `obsolete`. |

### 3.3. Outils de validation  

| Outil | Fonction | Installation |
|------|----------|--------------|
| `pyang` | Compilation, lint, génération de schematrons, documentation. | `pip install pyang` |
| `yanglint` (libyang) | Validation rapide, conversion JSON↔XML. | `sudo apt-get install yanglint` |
| `yangdump` (Cisco) | Export des modules du routeur. | `show running-config yang` → `copy running-config tftp://...` |

Exemple de validation :

```bash
pyang -f tree cisco-interface.yang
pyang -f yang --ietf cisco-interface.yang
yanglint -p . cisco-interface.yang
```

---  

## 4. RESTCONF – API RESTful pour YANG

### 4.1. Principes  

* **Transport** : HTTPS (port 443) – TLS obligatoire.  
* **Encodage** : JSON (par défaut) ou XML (option).  
* **URI** : `/restconf/data/<yang‑path>` (opérations CRUD).  
* **Méthodes HTTP** : `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.  
* **Headers** : `Accept: application/yang-data+json`, `Content-Type: application/yang-data+json`.  

### 4.2. Exemple d’appel – création d’une Loopback (Cisco IOS XE)

```bash
# 1️⃣ Authentification basique (encodée en base64)
AUTH=$(echo -n "admin:cisco123" | base64)

# 2️⃣ Payload JSON
cat > payload.json <<EOF
{
  "Cisco-IOS-XE-native:interface": {
    "Loopback": [
      {
        "name": 10,
        "description": "Loopback via RESTCONF",
        "ip": {
          "address": {
            "primary": {
              "address": "192.0.2.10",
              "mask": "255.255.255.255"
            }
          }
        }
      }
    ]
  }
}
EOF

# 3️⃣ POST vers le datastore candidate
curl -k -X POST \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/yang-data+json" \
  -H "Accept: application/yang-data+json" \
  -d @payload.json \
  https://10.0.0.1/restconf/data/Cisco-IOS-XE-native:native/interface/Loopback=10
```

### 4.3. Commandes Cisco pour activer RESTCONF

```bash
conf t
 ip http secure-server
 restconf
 restconf-yang
 restconf-yang schema-mount
end
write memory
```

Vérifications :

```bash
show restconf
show restconf capabilities
```

### 4.4. Table comparative NETCONF vs RESTCONF  

| Caractéristique | NETCONF | RESTCONF |
|-----------------|---------|----------|
| **Transport** | SSH (ou TLS) | HTTPS |
| **Encodage** | XML (RFC 6241) | JSON ou XML |
| **Modèle de données** | YANG (RFC 7950) | YANG (via JSON mapping) |
| **Transactionalité** | RPC commit/rollback (candidate → running) | `PATCH` + `POST` (no explicit candidate) |
| **Streaming** | `notification` (NETCONF notifications) | `event-stream` (SSE) |
| **Performance** | Moins overhead XML, mais plus lourd que JSON | Lighter payload, plus adapté aux API web |
| **Gestion de gros blocs** | `copy-config` (full‑sync) | `GET` avec pagination (RFC 8040) |
| **Sécurité** | SSH‑key ou TLS + X.509 | TLS + OAuth2 / Basic Auth |
| **Adoption** | Très présent sur IOS XR, Junos, OpenDaylight | En forte croissance sur IOS XE, NX‑OS, Arista EOS |

---  

## 5. Implémentations concrètes

### 5.1. Cisco IOS XR (exemple de configuration)

```bash
router xr
 netconf-yang
 netconf-yang ssh
 netconf-yang commit-queue
!
netconf-yang schema-mount
!
restconf
 restconf-yang
 restconf-yang schema-mount
!
ssh server v2
!
```

### 5.2. Cisco NX‑OS  

```bash
feature netconf-yang
netconf-yang ssh
netconf-yang commit-queue
!
feature restconf
restconf
restconf-yang
!
```

### 5.3. Linux – Serveur NETCONF (Netopeer2)  

```bash
# Installation (Ubuntu 22.04)
sudo apt-get update
sudo apt-get install -y netopeer2-server netopeer2-cli libyang2-dev

# Démarrage du service
sudo systemctl enable netopeer2-server
sudo systemctl start netopeer2-server

# Vérifier les capabilities
netconf-cli --login admin@localhost --get-capabilities
```

### 5.4. OpenDaylight (ODL) – Plugin RESTCONF  

```bash
# Démarrage ODL (Karaf)
./bin/karaf
# Activer le feature
feature:install odl-restconf-all odl-netconf-all
# Vérifier le endpoint
curl -k -u admin:admin https://localhost:8181/restconf/operational/network-topology:network-topology/
```

---  

## 6. Workflow d’automatisation typique

```
+-------------------+      +----------------+      +-------------------+
|  CI/CD Pipeline   | ---> |  YANG Modules  | ---> |  NETCONF/RESTCONF |
|  (Git, Jenkins)  |      |  (pyang lint)  |      |  (ncclient/curl) |
+-------------------+      +----------------+      +-------------------+
        |                         |                         |
        v                         v                         v
   Git repo                Validation               Commit sur le device
   (module.yang)          (yanglint, pyang)          (candidate → running)
```

* **Étape 1** – *Versionning* du module YANG (`git tag v1.2`).  
* **Étape 2** – *CI* : `pyang -f tree -p modules/ module.yang` → génération de la documentation.  
* **Étape 3** – *Test* : `ncclient` exécute `edit-config` sur un simulateur (Cisco IOS XE‑vEOS).  
* **Étape 4** – *Déploiement* : `curl` ou Ansible `netconf_config` module.  

---  

## 7. Sécurité & Hardening

| Aspect | Recommandation |
|--------|----------------|
| **Transport** | Toujours utiliser SSH (NETCONF) ou TLS 1.2+ (RESTCONF). |
| **Authentification** | SSH keys + `aaa authentication login` ou certificat X.509 (RFC 5277). |
| **Autorisation** | `aaa authorization exec` + `netconf-yang` ACLs (`ip access-list`). |
| **Chiffrement** | Désactiver `ssh server` version 1, forcer `ssh server v2`. |
| **Logging** | `logging host <IP> transport tcp port 514` + `netconf-yang logging`. |
| **Rate‑limiting** | `rate-limit input` sur les ports 830/443. |
| **Patch Management** | Mettre à jour le firmware (ex. IOS XE 17.12). |

Exemple d’ACL sur IOS XE pour limiter NETCONF :

```bash
ip access-list extended NETCONF-ACL
 permit tcp host 10.1.1.100 any eq 830
 deny   ip any any log
!
interface GigabitEthernet0/0
 ip access-group NETCONF-ACL in
```

---  

## 8. Atelier de dépannage – “Loopback disparu”

### 8.1. Contexte  

Un technicien a créé une interface Loopback 10 via NETCONF (candidate → running).  
Après un redémarrage du routeur, l’interface a disparu.  

### 8.2. Objectifs  

1. Vérifier la persistance du datastore.  
2. Identifier le problème de *commit* ou de *startup‑config*.  
3. Corriger la configuration et mettre en place une sauvegarde automatisée.

### 8.3. Étapes de diagnostic (Cisco IOS XE)

| Étape | Commande | Interprétation |
|------|----------|----------------|
| **1** | `show netconf-yang sessions` | Vérifier qu’aucune session bloquée n’empêche le commit. |
| **2** | `show running-config interface Loopback10` | Si absent → le commit n’a pas été appliqué. |
| **3** | `show startup-config | include Loopback10` | Si absent → le commit n’a pas été sauvegardé. |
| **4** | `show netconf-yang candidate` | Affiche le contenu du datastore *candidate*. |
| **5** | `show netconf-yang lock` | Vérifier qu’un lock persiste (ex. : `candidate`). |
| **6** | `show logging | include NETCONF` | Recherche d’erreurs “`rpc-error`”. |
| **7** | `show clock` | S’assurer que l’heure est correcte (certificat TLS). |
| **8** | `show processes memory | include netconf` | Vérifier la charge mémoire du serveur NETCONF. |

### 8.4. Analyse typique  

* **Symptôme** – `show netconf-yang candidate` vide → le lock a été libéré sans commit.  
* **Cause** – Le client a envoyé `edit-config` mais a omis `commit`.  
* **Correction** – Ajouter `m.commit()` dans le script Python ou `POST