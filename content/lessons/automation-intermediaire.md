# Automatisation Réseau - Intermédiaire

**Niveau :** Intermédiaire

**Prérequis :** Automatisation Réseau Débutant (`automation-debutant.md`), bonnes bases en Python (fonctions, dictionnaires, modules), compréhension des formats JSON/YAML, et notions de base sur Ansible et les API REST.

Ce module approfondit l'automatisation réseau en passant de simples scripts impératifs à une **architecture d'automatisation déclarative et modulaire**. Vous découvrirez l'utilisation de **Jinja2** pour la génération dynamique de configurations, **NAPALM** pour l'abstraction multi-constructeurs, **NetBox** comme source unique de vérité (*SSoT*), ainsi que l'utilisation de **NETCONF / RESTCONF** adossés aux modèles **YANG**.

## 1. Génération Dynamique de Configuration : Jinja2 + Python

Plutôt que d'écrire des configurations en dur (*hardcodées*), la bonne pratique consiste à séparer **la donnée** (fichiers YAML) de **la logique de configuration** (templates Jinja2).

```
 ┌─────────────────────────┐
 │   Données (YAML/JSON)   │
 │ - IP, VLANs, Hostname   │
 └────────────┬────────────┘
              │
              ├─────────────────> [ Moteur Jinja2 ] ──> [ Configuration Finale ]
              │                                           (Prête à être poussée)
 ┌────────────┴────────────┐
 │  Template Jinja2 (.j2)  │
 │ - Structure & Variables │
 └─────────────────────────┘

```

### Exemple de Template Jinja2 (`templates/router.j2`) :

```jinja2
hostname {{ hostname }}

{% for intf in interfaces %}
interface {{ intf.name }}
 description {{ intf.description }}
 ip address {{ intf.ip }} {{ intf.mask }}
 {% if intf.enabled %}
 no shutdown
 {% else %}
 shutdown
 {% endif %}
{% endfor %}

router bgp {{ bgp.asn }}
 {% for neighbor in bgp.neighbors %}
 neighbor {{ neighbor.ip }} remote-as {{ neighbor.remote_as }}
 {% endfor %}
```

### Script Python d'injection (`render_config.py`) :

```python
import yaml
from jinja2 import Environment, FileSystemLoader

# Load variables
with open('data/router_vars.yml') as f:
    data = yaml.safe_load(f)

# Initialize Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('router.j2')

# Render final configuration
rendered_config = template.render(data)
print(rendered_config)
```

## 2. Abstraction Multi-Constructeur avec NAPALM

**NAPALM** (*Network Automation and Programmability Abstraction Layer with Multivendor support*) fournit une API unifiée pour interagir de manière identique avec Cisco IOS/IOS-XR/NX-OS, Juniper JunOS, Arista EOS, etc.

```
                  ┌──────────────────┐
                  │   Script NAPALM  │
                  └────────┬─────────┘
                           │ API Unifiée (get_facts, load_merge_candidate)
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ Cisco IOS  │  │ JunOS      │  │ Arista EOS │
     └────────────┘  └────────────┘  └────────────┘
```

### Fonctionnalités Clés de NAPALM :

1. **Getter Methods :** Récupération normalisée d'informations (`get_facts()`, `get_interfaces()`, `get_bgp_neighbors()`).
2. **Configuration Management :**
   * `load_merge_candidate()` : Fusionne une nouvelle configuration avec la configuration existante.
   * `load_replace_candidate()` : Remplace intégralement la configuration.
   * `compare_config()` : Affiche le *diff* avant application.
   * `commit_config()` / `rollback()` : Valide ou annule les changements.

```python
from napalm import get_network_driver

driver = get_network_driver('junos')
device = driver('10.0.0.1', 'admin', 'Password123!')
device.open()

# Fetch facts in unified JSON format
facts = device.get_facts()
print(f"Hostname: {facts['hostname']}, Vendor: {facts['vendor']}")

# Stage configuration & Check Diff
device.load_merge_candidate(filename='config_changes.txt')
print("--- DIFF CONFIGURATION ---")
print(device.compare_config())

# Commit or Rollback
choice = input("Appliquer les modifications ? (y/n): ")
if choice.lower() == 'y':
    device.commit_config()
    print("Configuration appliquée avec succès.")
else:
    device.rollback()
    print("Modifications annulées.")

device.close()
```

## 3. NETCONF, RESTCONF et Modèles YANG

Le CLI présente des limites pour le parsing de texte. Les architectures modernes utilisent des protocoles de gestion structurés basés sur le standard **YANG**.

* **YANG (Yet Another Next Generation) :** Langage de modélisation de données décrivant la structure, le type et les contraintes des configurations et états d'un équipement réseau (RFC 6020).
* **NETCONF :** Protocole opérant sur SSH via le port **830**, manipulant du XML.
* **RESTCONF :** Protocole opérant sur HTTPS via le port **443**, manipulant du JSON ou du XML.

```
┌─────────────────────────────────────────────────────────────┐
│                 Modèle de Données (YANG)                    │
│   ietf-interfaces, openconfig-bgp, cisco-ios-xe-native      │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
    [ NETCONF (SSH / XML) ]         [ RESTCONF (HTTPS / JSON) ]
```

### Exemple de requête NETCONF en Python (`ncclient`) :

```python
from ncclient import manager

# XML RPC Filter targeting ietf-interfaces
filter_xml = """
<filter>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface></interface>
  </interfaces>
</filter>
"""

with manager.connect(
    host='192.168.1.1',
    port=830,
    username='admin',
    password='Password123!',
    hostkey_verify=False,
    device_params={'name': 'csr'}
) as m:
    response = m.get_config(source='running', filter=('subtree', filter_xml))
    print(response.xml)
```

## 4. Single Source of Truth (SSoT) avec NetBox

Dans une architecture d'automatisation mûre, l'état souhaité du réseau doit résider dans une **Source Unique de Vérité (SSoT)** comme **NetBox** (IPAM / DCIM) et non sur les équipements eux-mêmes.

```
 ┌──────────────────┐               ┌──────────────────┐               ┌──────────────────┐
 │     NetBox       │ ──(API REST)─>│   Orchestrateur  │ ──(NETCONF/ ──>│ Equipements      │
 │ (IPAM/DCIM/SSoT) │  pynetbox/     │ (Ansible/Python)│    RESTCONF/     │ Réseau Actifs    │
 │                  │  Dynamic Inv. │                  │    NAPALM)       │                  │
 └──────────────────┘               └──────────────────┘               └──────────────────┘
```

### Interaction avec NetBox via `pynetbox` :

```python
import pynetbox

nb = pynetbox.api('https://netbox.local.domain', token='0123456789abcdef0123456789abcdef01234567')

# Retrieve devices by site and role
devices = nb.dcim.devices.filter(site='par-dc1', role='leaf-switch')

for device in devices:
    print(f"Device: {device.name}, Primary IP: {device.primary_ip}")
```

## 5. Structuration Avancée Ansible : Inventaires Dynamiques & Rôles

### Inventaire Dynamique NetBox pour Ansible

Au lieu de gérer un fichier `inventory.ini` statique, Ansible peut interroger automatiquement NetBox via le plugin `netbox.netbox.nb_inventory` :

```yaml
# netbox_inventory.yml
plugin: netbox.netbox.nb_inventory
api_endpoint: https://netbox.local.domain
token: 0123456789abcdef0123456789abcdef01234567
validate_certs: false
group_by:
  - site
  - device_role
```

### Structure d'un Rôle Ansible Réseau :

Les rôles permettent de modulariser les playbooks Ansible.

```
roles/
└── network_base/
    ├── tasks/
    │   └── main.yml        # Logique des exécutions
    ├── templates/
    │   └── syslog.j2       # Templates de configuration
    ├── defaults/
    │   └── main.yml        # Valeurs par défaut
    └── vars/
        └── main.yml        # Variables du rôle
```

## Commandes et Outils d'Analyse

| Outil / Commande | Description / Usages |
| ----- | ----- |
| `yang-explorer` / `pyang` | Outils CLI pour visualiser et valider les modèles YANG (`pyang -f tree ietf-interfaces.yang`). |
| `ansible-inventory -i netbox_inventory.yml --graph` | Affiche l'arborescence de l'inventaire dynamique généré depuis NetBox. |
| `pynetbox` | Module Python client officiel pour interagir de façon fluide avec l'API REST de NetBox. |

## Points à Retenir

* **Jinja2 + YAML :** Découple formellement la donnée métier (variables) du code de configuration (template).
* **NAPALM :** Abstrait la complexité multi-constructeurs et offre des fonctionnalités essentielles de `compare_config` et `rollback`.
* **YANG / NETCONF / RESTCONF :** Remplacent l'interaction CLI fragile par un contrôle structuré, typé et transactionnel.
* **NetBox (SSoT) :** Sert de référence absolue pour définir l'état cible du réseau avant tout déploiement automatisé.