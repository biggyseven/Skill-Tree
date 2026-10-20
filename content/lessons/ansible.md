# **Cours Intensif – Automatisation Réseau avec Ansible**  
**Niveau : Senior Network Administrator (CCIE)**  
**Durée estimée : 3 jours (24 h)**  

---  

## Table des matières  

| # | Section | Durée (h) |
|---|---------|-----------|
| 1 | Introduction & Principes fondamentaux | 1 |
| 2 | Architecture d’Ansible (Control node, Managed nodes, Inventory) | 2 |
| 3 | Installation, configuration et bonnes pratiques | 2 |
| 4 | Inventaires avancés (static, dynamic, plugins) | 3 |
| 5 | Playbooks, tâches, boucles, conditionnels | 4 |
| 6 | Modules réseau Cisco (ios, nxos, iosxr, junos) | 4 |
| 7 | Gestion des états, idempotence et verifications | 2 |
| 8 | Rôles, collections et Galaxy | 2 |
| 9 | Ansible Tower / AWX (CI/CD, RBAC, API) | 2 |
|10 | Sécurité (Vault, SSH, certificats, fact gathering) | 2 |
|11 | Optimisation & performances (forks, async, poll) | 2 |
|12 | Comparatif avec les autres outils d’orchestration | 2 |
|13 | Atelier pratique : Déploiement d’une configuration BGP sur IOS & NX‑OS | 3 |
|14 | Atelier de dépannage – “Playbook qui ne s’exécute pas” | 2 |
|15 | Bibliographie & ressources complémentaires | 1 |

> **Objectif** : Maîtriser la conception, le déploiement et le maintien d’infrastructures réseau automatisées avec Ansible, en respectant les exigences de haute disponibilité et de conformité propres aux environnements d’entreprise CCIE.

---  

## 1️⃣ Introduction & Principes fondamentaux  

- **Ansible** : moteur d’orchestration agent‑less, écrit en Python, utilisant **SSH** (ou **WinRM** pour Windows) comme protocole de transport.  
- **Idempotence** : chaque tâche décrit l’état désiré ; si l’état est déjà atteint, aucune modification n’est effectuée.  
- **Declarative vs Imperative** : Ansible adopte un modèle déclaratif (décrire *ce que* l’on veut, pas *comment* le faire).  

### Pourquoi Ansible pour le réseau ?  

| Critère | Ansible | Chef | Puppet | SaltStack |
|--------|---------|------|--------|-----------|
| Agent‑less | ✔️ (SSH) | ❌ (agent) | ❌ (agent) | ✔️ (optionnel) |
| Courbe d’apprentissage | Modérée (YAML) | Élevée (Ruby) | Élevée (DSL) | Modérée (YAML + Python) |
| Support natif IOS/NX‑OS | ✔️ (modules ios, nxos) | ❌ (plugins) | ❌ (plugins) | ✔️ (net‑modules) |
| Gestion du « state » réseau | ✔️ (netconf, napalm) | ❌ | ❌ | ✔️ |
| Intégration CI/CD | ✔️ (Tower/AWX) | ✔️ | ✔️ | ✔️ |
| Communauté | > 10 k rôles sur Galaxy | < 5 k | < 4 k | < 6 k |

---  

## 2️⃣ Architecture d’Ansible  

```
+-------------------+          +-------------------+
|  Control Node     |  SSH     |  Managed Node 1   |
|  (Linux/WSL)      +--------->|  IOS/ NX‑OS /Linux|
|  - ansible.cfg    |          |  - ansible_user   |
|  - inventory/     |          |  - ansible_ssh_* |
|  - playbooks/     |          +-------------------+
|  - roles/         |
|  - collections/   |          +-------------------+
|  - vault/         +--------->|  Managed Node 2   |
+-------------------+   ...    |  (JunOS, EOS…)    |
                                 +-------------------+
```

- **Control Node** : machine où Ansible est installé (ex. Ubuntu 22.04, RHEL 9, ou WSL2).  
- **Managed Nodes** : équipements réseau ou serveurs ciblés. Aucun agent n’est requis.  
- **Connection plugins** : `ssh`, `network_cli`, `netconf`, `httpapi`.  

### Schéma ASCII du flux d’exécution  

```
[Playbook] --> [Parser YAML] --> [Task Queue] --> [Connection Plugin] --> [Device]
   |                |                |                 |                 |
   |                |                |                 |                 v
   |                |                |                 |            [CLI/NETCONF]
   |                |                |                 |                 |
   |                |                |                 |                 v
   |                |                |                 |          [Device State]
   |                |                |                 |                 |
   |                |                |                 | <--- diff <---  |
   |                |                |                 |   (idempotence)|
   |                |                |                 |                 |
   |                |                |                 v                 v
   |                |                |            [Result JSON]   [Callback]
   |                |                |                 |                 |
   |                |                +-----------------+-----------------+
   |                |                                  |
   v                v                                  v
[Stdout]       [Log Files]                        [Ansible Tower UI]
```

---  

## 3️⃣ Installation & Configuration  

### 3.1 Prérequis  

| Plateforme | Packages requis |
|------------|-----------------|
| Ubuntu 22.04 | `python3‑venv python3‑pip sshpass` |
| RHEL 9 | `python3‑virtualenv python3‑pip openssh-clients` |
| macOS | `brew install ansible` |
| Windows (WSL2) | Ubuntu + les paquets Linux ci‑dessus |

### 3.2 Installation via *virtualenv* (recommandé)  

```bash
# Créer un répertoire dédié
mkdir -p ~/ansible_env && cd ~/ansible_env

# Créer l'environnement virtuel
python3 -m venv .venv

# Activer
source .venv/bin/activate

# Installer Ansible (version stable 2.15.x au moment du cours)
pip install --upgrade pip
pip install ansible==2.15.5

# Vérifier
ansible --version
```

### 3.3 Fichier de configuration global `ansible.cfg`  

```ini
[defaults]
inventory      = ./inventory
host_key_checking = False          # à désactiver uniquement en lab
retry_files_enabled = False
log_path       = ./logs/ansible.log
forks          = 20                # nombre de processus parallèles
callback_whitelist = timer,profile_json

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
retries = 3
```

> **Astuce CCIE** : activez `pipelining` pour réduire le nombre de round‑trip SSH, surtout sur des commutateurs à forte latence.

### 3.4 Gestion des clés SSH  

```bash
# Générer une clé RSA de 4096 bits
ssh-keygen -t rsa -b 4096 -C "ansible@corp"

# Copier la clé publique sur les équipements (exemple IOS)
ssh admin@router1 "configure terminal
 ip ssh pubkey-chain
  username ansible
   key-string
$(cat ~/.ssh/id_rsa.pub)
   exit
  exit
 exit"

# Vérifier la connexion sans mot de passe
ssh -i ~/.ssh/id_rsa ansible@router1
```

---  

## 4️⃣ Inventaires avancés  

### 4.1 Inventaire statique (INI)  

```ini
[ios_routers]
r1 ansible_host=10.0.0.1 ansible_user=admin ansible_ssh_pass=secret
r2 ansible_host=10.0.0.2

[nxos_switches]
s1 ansible_host=10.0.1.1 ansible_network_os=nxos ansible_user=admin
s2 ansible_host=10.0.1.2

[all:vars]
ansible_python_interpreter=/usr/bin/python3
ansible_connection=network_cli
ansible_network_os=ios
```

### 4.2 Inventaire dynamique (script)  

Un script Python retournant du JSON conforme à l’API d’inventaire :

```python
#!/usr/bin/env python3
import json, os

def main():
    inventory = {
        "ios_routers": {
            "hosts": ["r1", "r2"],
            "vars": {"ansible_network_os": "ios", "ansible_connection": "network_cli"}
        },
        "_meta": {
            "hostvars": {
                "r1": {"ansible_host": "10.0.0.1", "ansible_user": "admin"},
                "r2": {"ansible_host": "10.0.0.2", "ansible_user": "admin"}
            }
        }
    }
    print(json.dumps(inventory))

if __name__ == "__main__":
    main()
```

Enregistré sous `inventory/dyn_inventory.py`, rendu exécutable (`chmod +x`) puis référencé dans `ansible.cfg` :

```ini
inventory = ./inventory/dyn_inventory.py
```

### 4.3 Plugins d’inventaire (exemple **netbox**)  

```bash
pip install pynetbox
```

`ansible.cfg` :

```ini
[inventory]
enable_plugins = netbox

[netbox]
api_url = https://netbox.corp/api/
token = <TOKEN>
```

---  

## 5️⃣ Playbooks, tâches, boucles, conditionnels  

### 5.1 Structure minimale d’un playbook  

```yaml
---
- name: Déploiement BGP sur IOS
  hosts: ios_routers
  gather_facts: false
  connection: network_cli
  become: false

  tasks:
    - name: Vérifier la version du système
      ios_facts:
      register: sys_facts

    - name: Appliquer la configuration BGP
      ios_config:
        lines:
          - router bgp {{ bgp_asn }}
          - neighbor {{ bgp_neighbor }} remote-as {{ bgp_remote_asn }}
        before: "no router bgp"
      vars:
        bgp_asn: 65001
        bgp_neighbor: 10.0.0.254
        bgp_remote_asn: 65002
```

### 5.2 Boucles & `with_items` (déprécié, remplacé par `loop`)  

```yaml
- name: Configurer plusieurs interfaces
  ios_interface:
    name: "{{ item.name }}"
    description: "{{ item.desc }}"
    enabled: true
  loop:
    - { name: Gig0/1, desc: "Uplink to Core" }
    - { name: Gig0/2, desc: "Link to Server Farm" }
```

### 5.3 Conditionnels (`when`)  

```yaml
- name: Appliquer OSPF uniquement si le device est IOS XE 16.12+
  ios_ospf:
    process_id: 1
    state: present
  when:
    - sys_facts.ansible_net_version is version('16.12', '>=')
    - "'router ospf' not in sys_facts.ansible_net_config"
```

### 5.4 Gestion des erreurs (`ignore_errors`, `failed_when`)  

```yaml
- name: Tentative de mise à jour du firmware (peut échouer)
  ios_command:
    commands: "request platform software package install switch all file flash:{{ fw_image }}"
  register: fw_result
  ignore_errors: true

- name: Vérifier le succès du firmware
  fail:
    msg: "Installation du firmware a échoué"
  when: "'[OK]' not in fw_result.stdout[0]"
```

---  

## 6️⃣ Modules réseau Cisco  

| Module | OS cible | Action principale | Exemple d’utilisation |
|--------|----------|-------------------|-----------------------|
| `ios_config` | IOS, IOS‑XE | Push de lignes de config | `lines: - hostname R1` |
| `ios_command` | IOS, IOS‑XE | Exécution de commandes ad‑hoc | `commands: - show version` |
| `ios_facts` | IOS, IOS‑XE | Collecte de facts | `register: facts` |
| `nxos_config` | NX‑OS | Gestion de la config en mode `cli` ou `json` | `lines: - hostname N9K1` |
| `nxos_vlans` | NX‑OS | Gestion des VLANs | `vlan_id: 100` |
| `iosxr_config` | IOS‑XR | Config via NETCONF/CLI | `lines: - router ospf 1` |
| `netconf_config` | Tous (via NETCONF) | Envoi de XML | `config: "{{ lookup('file','bgp.xml') }}"` |
| `napalm_install_config` | Multi‑vendor | Déploiement atomic via NAPALM | `provider: "{{ napalm_provider }}"` |

### 6.1 Exemple complet – BGP sur IOS & NX‑OS  

```yaml
---
- name: Déployer BGP sur IOS et NX‑OS
  hosts: all
  gather_facts: false
  connection: network_cli
  vars:
    bgp_asn: 65010
    bgp_neighbors:
      - { ip: 10.1.0.2, remote_as: 65020 }
      - { ip: 10.1.0.3, remote_as: 65030 }

  tasks:
    - name: Appliquer BGP sur IOS
      ios_config:
        lines:
          - router bgp {{ bgp_asn }}
          - "{{ item.ip }} remote-as {{ item.remote_as }}"
        before: "no router bgp"
      when: ansible_network_os == 'ios'
      loop: "{{ bgp_neighbors }}"

    - name: Appliquer BGP sur NX‑OS
      nxos_config:
        lines:
          - router bgp {{ bgp_asn }}
          - "{{ item.ip }} remote-as {{ item.remote_as }}"
        before: "no router bgp"
      when: ansible_network_os == 'nxos'
      loop: "{{ bgp_neighbors }}"
```

---  

## 7️⃣ Gestion des états, idempotence & vérifications  

| Situation | Solution Ansible | Commande de vérif |
|-----------|------------------|-------------------|
| **Interface déjà configurée** | `ios_interface` avec `state: present` (idempotent) | `show run interface Gi0/1` |
| **Suppression d’un VLAN** | `nxos_vlan` avec `state: absent` | `show vlan id 200` |
| **Mise à jour du mot de passe** | `ios_user` – Ansible compare le hash actuel | `show run | include username` |
| **Déploiement de fichier de configuration** | `napalm_install_config` – compare le hash du fichier | `show running-config checksum` |

> **Note** : Utilisez toujours `register` + `changed_when` pour forcer la logique d’idempotence lorsqu’un module ne le gère pas nativement.

---  

## 8️⃣ Rôles, collections & Galaxy  

### 8.1 Structure d’un rôle (exemple `cisco_bgp`)  

```
cisco_bgp/
├── defaults/
│   └── main.yml          # variables par défaut
├── vars/
│   └── main.yml          # variables spécifiques au rôle
├── tasks/
│   └── main.yml          # logique principale
├── handlers/
│   └── main.yml          # notifications (ex: reload)
├── templates/
│   └── bgp.j2            # Jinja2 pour config IOS/NX‑OS
├── files/
│   └── bgp.cfg           # fichier brut (si besoin)
└── meta/
    └── main.yml          # dépendances, galaxy info
```

### 8.2 Publication sur Ansible Galaxy  

```bash
ansible-galaxy init my_role
# ... remplissez les meta/main.yml
ansible-galaxy login   # créez un compte sur galaxy.ansible.com
ansible-galaxy import my_namespace my_role
```

### 8.3 Collections (exemple `cisco.nxos`)  

```bash
ansible-galaxy collection install cisco.nxos
ansible-doc -t module -l cisco.nxos
```

---  

## 9️⃣ Ansible Tower / AWX  

| Fonctionnalité | Ansible Tower | AWX (Open‑Source) |
|----------------|---------------|-------------------|
| UI Web | ✔️ | ✔️ |
| RBAC (Roles, Teams) | ✔️ | ✔️ |
| API RESTful | ✔️ | ✔️ |
| Job Scheduling | ✔️ | ✔️ |
| Credential Store (Vault, SSH, Cloud) | ✔️ | ✔️ |
| Notifications (Slack, Email, Webhook) | ✔️ | ✔️ |
| License | Commercial | Gratuit (GPL) |

### 9.1 Déploiement d’AWX (Docker‑Compose)  

```bash
git clone https://github.com/ansible/awx.git
cd awx/installer
# Créez un fichier inventory (exemple ci‑dessous)
cat > inventory <<EOF
localhost ansible_connection=