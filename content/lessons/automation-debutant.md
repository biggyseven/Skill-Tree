# Automatisation Réseau - Débutant

**Niveau :** Débutant

**Prérequis :** Notions de base en réseau (CLI Cisco/Junos, SSH, adresses IP, VLANs, routage de base) et se sentir à l'aise avec la ligne de commande.

Ce module introduit les fondements de l'**automatisation réseau**. Il couvre le passage de la gestion manuelle (CLI) vers l'automatisation programmatique à l'aide de Python, des formats de données structurées (JSON, YAML), ainsi qu'une introduction à Ansible et aux API REST.

---

## 1. Pourquoi Automatiser le Réseau ?

Pendant des années, l'administration réseau s'est faite de manière manuelle via SSH et la ligne de commande (CLI). Cette approche présente plusieurs limites à grande échelle :

* **Erreurs humaines :** Fautes de frappe, configurations oubliées ou incohérentes.
* **Lenteur d'exécution :** Configurer 50 switchs un par un prend des heures.
* **Absence de Source Unique de Vérité (*Single Source of Truth*) :** Difficile de savoir si la configuration active correspond exactement à la documentation.

```
MÉTHODE TRADITIONNELLE (Manuelle) :
[ Administrateur ] ──(SSH manuel)──> [ Switch 1 ]  (Erreurs possibles)
                   ──(SSH manuel)──> [ Switch 2 ]  (Lent)
                   ──(SSH manuel)──> [ Switch 3 ]  (Incohérent)

MÉTHODE AUTOMATISÉE (Programmatique) :
                                   ┌──> [ Switch 1 ]
[ Script / Ansible ] ──(API/SSH)───┼──> [ Switch 2 ]  (Rapide, reproductible,
                                   └──> [ Switch 3 ]   standardisé)
```

---

## 2. Formats de Données Structurées : JSON & YAML

En automatisation, les configurations ne sont plus manipulées sous forme de texte brut non structuré, mais via des **données structurées**.

### JSON (JavaScript Object Notation)
Très utilisé par les API REST et les langages de programmation.

```json
{
  "hostname": "SW-CORE-01",
  "interfaces": [
    {
      "name": "GigabitEthernet0/1",
      "vlan": 10,
      "enabled": true
    },
    {
      "name": "GigabitEthernet0/2",
      "vlan": 20,
      "enabled": false
    }
  ]
}
```

### YAML (YAML Ain't Markup Language)
Format lisible par l'humain, très utilisé par **Ansible**. Il repose sur l'indentation.

```yaml
hostname: SW-CORE-01
interfaces:
  - name: GigabitEthernet0/1
    vlan: 10
    enabled: true
  - name: GigabitEthernet0/2
    vlan: 20
    enabled: false
```

---

## 3. Premiers Pas avec Python pour le Réseau

Python est le langage de référence pour l'automatisation réseau grâce à son écosystème riche.

### Interaction SSH simplifiée avec `Netmiko`

`Netmiko` est une bibliothèque Python spécialisée pour interagir en SSH avec des équipements réseau multi-constructeurs (Cisco, Juniper, Arista, HP, etc.).

#### Exemple de script Python :

```python
from netmiko import ConnectHandler

# Définition de l'équipement
device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'Password123!',
}

# Connexion SSH et exécution d'une commande de lecture
print("Connexion à l'équipement...")
with ConnectHandler(**device) as net_connect:
    output = net_connect.send_command('show ip interface brief')
    print("--- Résultat ---")
    print(output)

    # Envoi de commandes de configuration
    config_commands = [
        'interface GigabitEthernet0/3',
        'description Connecte au serveur Web',
        'switchport access vlan 10',
        'no shutdown'
    ]
    config_output = net_connect.send_config_set(config_commands)
    print("--- Configuration appliquée ---")
    print(config_output)
```

---

## 4. Introduction aux API REST & RESTCONF

De nombreux équipements réseau modernes (Cisco IOS-XE, NX-OS, Arista EOS) intègrent des API web HTTP pour envoyer et recevoir du JSON ou du XML.

### Principes des API REST HTTP :

| Méthode HTTP | Action Réseau | Exemple d'utilisation |
| --- | --- | --- |
| **GET** | Lecture | Récupérer la liste des VLANs ou l'état des interfaces |
| **POST** | Création | Créer une nouvelle interface ou un nouveau VLAN |
| **PUT / PATCH** | Modification | Modifier la description ou le masque d'une IP |
| **DELETE** | Suppression | Supprimer une sous-interface ou une route statique |

#### Exemple d'appel API avec la bibliothèque Python `requests` :

```python
import requests

url = "https://192.168.1.1/restconf/data/ietf-interfaces:interfaces"
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
auth = ("admin", "Password123!")

# Requête GET (lecture d'interfaces via RESTCONF)
response = requests.get(url, headers=headers, auth=auth, verify=False)

if response.status_code == 200:
    data = response.json()
    print("Données récupérées avec succès !")
    print(data)
else:
    print(f"Erreur HTTP {response.status_code}")
```

---

## 5. Introduction à Ansible pour le Réseau

**Ansible** est un outil d'automatisation *agentless* (sans agent installé sur l'équipement). Il communique via SSH ou API.

### Les éléments de base d'Ansible :

1. **Inventory (Inventaire) :** Liste des équipements réseau classés par groupes.
2. **Playbook :** Fichier YAML décrivant la liste des tâches à exécuter.
3. **Modules réseau :** Modules spécialisés par constructeur (ex: `cisco.ios.ios_config`, `junipernetworks.junos.junos_config`).

#### Exemple d'Inventaire (`inventory.ini`) :
```ini
[switches]
sw-access-01 ansible_host=192.168.1.10
sw-access-02 ansible_host=192.168.1.11

[switches:vars]
ansible_network_os=cisco.ios.ios
ansible_user=admin
ansible_password=Password123!
ansible_connection=network_cli
```

#### Exemple de Playbook (`site.yml`) :
```yaml
---
- name: Configuration de base des switchs
  hosts: switches
  gather_facts: no

  tasks:
    - name: Configurer le serveur NTP
      cisco.ios.ios_ntp_global:
        config:
          peers:
            - peer: 10.0.0.1
        state: merged

    - name: Assurer la présence du VLAN 10
      cisco.ios.ios_vlans:
        config:
          - vlan_id: 10
            name: ADMINISTRATION
        state: merged
```

---

## CommandesUtiles pour Débuter

| Commande | Usage / Objectif |
| --- | --- |
| `pip install netmiko requests ansible` | Installe les bibliothèques indispensables Python & Ansible |
| `ansible-playbook -i inventory.ini site.yml --check` | Mode simulation (Dry Run) : vérifie ce qu'Ansible modifierait sans appliquer |
| `python3 script.py` | Exécute un script d'automatisation Python |

---

## Points à Retenir

* **Données structurées (JSON/YAML) :** Essentielles pour automatiser et séparer la logique de code des données de configuration.
* **Netmiko & Python :** Permettent de scripter facilement des interactions SSH complexes.
* **API REST / RESTCONF :** Offrent un accès structuré, moderne et sans parsing de texte CLI.
* **Ansible :** Outil déclaratif puissant sans agent pour gérer la configuration de parc à grande échelle.