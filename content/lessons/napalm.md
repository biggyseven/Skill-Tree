# Automatisation réseau avec NAPALM  
**Niveau : Senior Network Administrator (CCIE)**  

---  

## Table des matières  

| # | Section | Durée estimée |
|---|---------|----------------|
| 1 | Introduction & concepts clés | 15 min |
| 2 | Architecture NAPALM & modèles de données | 30 min |
| 3 | Installation & configuration (Linux / Windows) | 20 min |
| 4 | Pilotes (drivers) – comparaison détaillée | 25 min |
| 5 | Opérations de base (facts, config, interfaces) | 45 min |
| 6 | Gestion avancée : merge, replace, commit, rollback | 40 min |
| 7 | Intégration avec Ansible, Nornir & Netmiko | 35 min |
| 8 | Sécurité, performance & bonnes pratiques | 30 min |
| 9 | Atelier pratique : script complet & déploiement | 60 min |
|10 | Laboratoire de dépannage & FAQ | 45 min |
|   | **Total** | **~5 h** |

---  

## 1. Introduction & concepts clés  

### 1.1 Pourquoi NAPALM ?  

* **Multi‑vendor** : même API Python pour IOS‑XE, NX‑OS, EOS, Junos, IOSXR, etc.  
* **Idempotence** : les changements sont appliqués uniquement si la configuration cible diffère de l’état actuel.  
* **Abstraction de la couche transport** : SSH, NETCONF, eAPI, RESTCONF sont gérés en interne.  
* **Interopérabilité** : se combine naturellement avec Ansible, Nornir, SaltStack, Terraform, etc.  

### 1.2 Glossaire  

| Terme | Définition |
|-------|------------|
| **Driver** | Implémentation Python qui traduit les appels NAPALM en commandes propres au OS du dispositif. |
| **Getter** | Méthode qui récupère des informations (facts, config, interfaces). |
| **Setter** | Méthode qui pousse des changements (merge_config, replace_config). |
| **Commit** | Validation atomique d’une configuration (supporté sur les OS qui le permettent). |
| **Rollback** | Retour à une configuration antérieure via la fonction `rollback()` ou via le journal de configuration. |
| **Diff** | Résultat textuel (unified diff) montrant les différences entre configuration cible et actuelle. |

---  

## 2. Architecture NAPALM & modèles de données  

```
+-------------------+          +-------------------+          +-------------------+
|   Application    |  <--->   |   NAPALM Core    |  <--->   |   Device Driver   |
| (Ansible, Nornir)|          | (API Python)      |          | (IOS‑XE, EOS…)    |
+-------------------+          +-------------------+          +-------------------+
          ^                               ^                               ^
          |                               |                               |
          |   appels Python (napalm)      |   transport (SSH/NETCONF)     |
          +-------------------------------+-------------------------------+
```

### 2.1 Modèle de données unifié  

| Catégorie | Méthode NAPALM | Retour (exemple) | OS supportés |
|-----------|----------------|------------------|--------------|
| **facts** | `get_facts()` | `{'hostname': 'R1', 'model': 'ISR4321', 'os_version': '16.12.1', …}` | All |
| **interfaces** | `get_interfaces()` | `{ 'Gig0/0': {'is_up': True, 'description': 'Uplink', …}, …}` | All |
| **bgp_neighbors** | `get_bgp_neighbors()` | `{ '10.0.0.2': {'remote_as': 65002, 'is_up': True, …} }` | IOS‑XR, EOS, Junos |
| **lldp_neighbors** | `get_lldp_neighbors()` | `{ 'Gig0/1': {'remote_port': 'Eth0/0', 'remote_system_name': 'SW1'} }` | All |
| **config** | `get_config()` | `{ 'running': '...', 'candidate': '...' }` | All (candidate only on EOS, Junos, IOS‑XR) |

---  

## 3. Installation & configuration  

### 3.1 Prérequis système  

| OS | Version minimale | Packages requis |
|----|------------------|-----------------|
| Ubuntu 20.04+ | Python 3.8+ | `python3-pip`, `libssh2-1`, `libssl-dev` |
| RHEL/CentOS 8+ | Python 3.6+ | `python3-pip`, `gcc`, `openssl-devel` |
| Windows 10/Server 2019 | Python 3.8+ | `pip`, `Git for Windows` |

### 3.2 Installation via `pip`  

```bash
# Créez un venv dédié (recommandé)
python3 -m venv napalm-env
source napalm-env/bin/activate

# Upgrade pip & install NAPALM + drivers les plus courants
pip install --upgrade pip
pip install napalm[ios,iosxr,iosxe,eos,junos,netconf]

# Vérifiez l’installation
python -c "import napalm; print('NAPALM version', napalm.__version__)"
```

### 3.3 Configuration SSH sans mot de passe (clé publique)  

```bash
# Sur la machine d’automatisation
ssh-keygen -t ed25519 -C "napalm@automation"

# Copiez la clé sur chaque dispositif
ssh-copy-id -i ~/.ssh/id_ed25519.pub admin@10.0.0.1
ssh-copy-id -i ~/.ssh/id_ed25519.pub admin@10.0.0.2
```

> **Tip** : Pour les équipements qui n’acceptent que le **login via enable**, créez un fichier `~/.ssh/config` :

```
Host 10.0.0.*
    User admin
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_ed25519
    PubkeyAuthentication yes
```

---  

## 4. Pilotes (drivers) – comparaison détaillée  

| Driver | OS cible | Transport(s) supportés | Mode configuration | Fonctionnalités avancées | Licence |
|--------|----------|------------------------|--------------------|--------------------------|---------|
| `napalm_ios` | Cisco IOS (15.x‑16.x) | SSH (CLI) | Running only | `get_arp_table()`, `get_mac_address_table()` | BSD |
| `napalm_iosxe` | Cisco IOS‑XE (16.9+) | SSH, NETCONF (option) | Running / Candidate (via `configure terminal`) | `get_ntp_servers()`, `get_snmp_information()` | BSD |
| `napalm_iosxr` | Cisco IOS‑XR (6.x‑7.x) | NETCONF, SSH | Running / Candidate | **Commit**/Rollback, `get_route_to()` | BSD |
| `napalm_eos` | Arista EOS | eAPI (HTTPS), SSH | Running / Candidate | `get_config()` (candidate), `rollback()` | BSD |
| `napalm_junos` | Juniper Junos | NETCONF, SSH | Running / Candidate | **Commit**/Rollback, `get_facts()` très complet | BSD |
| `napalm_nxos` | Cisco NX‑OS | SSH, NX‑API (HTTPS) | Running only | `get_vlans()`, `get_cdp_neighbors()` | BSD |
| `napalm_fortios` | Fortinet FortiOS | REST API | Running only | `get_firewall_policies()` | BSD |
| `napalm_asa` | Cisco ASA | SSH | Running only | `get_aaa_servers()` | BSD |

### 4.1 Choix du driver en fonction du besoin  

| Besoin | Driver recommandé | Raison |
|--------|-------------------|--------|
| **Commit atomique** | `napalm_eos`, `napalm_junos`, `napalm_iosxr` | Support natif du mode *candidate* + *commit* |
| **Gestion via API HTTP** | `napalm_eos` (eAPI), `napalm_nxos` (NX‑API) | Moins de latence, JSON structuré |
| **Environnements mixtes (Cisco + Juniper)** | `napalm` + `napalm_iosxe` + `napalm_junos` | API unifiée, même code Python |

---  

## 5. Opérations de base  

### 5.1 Connexion à un dispositif  

```python
from napalm import get_network_driver

driver = get_network_driver('iosxe')
device = driver(hostname='10.0.0.1',
                username='admin',
                password='cisco123',
                optional_args={'port': 22})
device.open()
```

> **Note** : `optional_args` accepte `secret` (enable password), `ssh_config_file`, `transport` (`ssh`/`netconf`), `timeout`, etc.

### 5.2 Récupérer les *facts*  

```python
facts = device.get_facts()
print(f"Hostname : {facts['hostname']}")
print(f"OS version : {facts['os_version']}")
print(f"Uptime (s) : {facts['uptime']}")
```

| Clé | Description |
|-----|-------------|
| `hostname` | Nom du dispositif tel que déclaré dans le prompt. |
| `model` | Référence matériel (ex. ISR4321). |
| `serial_number` | Numéro de série (si disponible). |
| `uptime` | Temps depuis le dernier redémarrage (secondes). |
| `interface_list` | Liste brute des interfaces (ex. `['Gig0/0', 'Gig0/1']`). |

### 5.3 Récupérer la configuration  

```python
cfg = device.get_config()
print("--- Running config ---")
print(cfg['running'])
# Si le driver supporte le candidat
if cfg.get('candidate'):
    print("--- Candidate config ---")
    print(cfg['candidate'])
```

### 5.4 Récupérer les interfaces  

```python
interfaces = device.get_interfaces()
for intf, data in interfaces.items():
    print(f"{intf}: up={data['is_up']} speed={data['speed']} desc={data['description']}")
```

### 5.5 Récupérer les voisins LLDP  

```python
lldp = device.get_lldp_neighbors()
for local_int, neigh in lldp.items():
    for remote in neigh:
        print(f"{local_int} <-> {remote['remote_port']} ({remote['remote_system_name']})")
```

### 5.6 Fermeture de la session  

```python
device.close()
```

---  

## 6. Gestion avancée : merge, replace, commit, rollback  

### 6.1 Différence entre *merge* et *replace*  

| Action | Description | Cas d’usage |
|--------|-------------|-------------|
| **merge_config** | Ajoute/modifie les lignes présentes dans le fragment, laisse le reste intact. | Ajout d’une ACL, mise à jour d’un description d’interface. |
| **replace_config** | Remplace entièrement la configuration (ou le *candidate*) par le texte fourni. | Restauration d’une configuration de référence, migration complète. |

### 6.2 Exemple : mise à jour d’une ACL sur IOS‑XE  

```python
acl_fragment = """
ip access-list extended BLOCK_SSH
  deny tcp any any eq 22
  permit ip any any
"""

device.load_merge_candidate(config=acl_fragment)
diff = device.compare_config()
print("=== Diff ===")
print(diff)

# Validation manuelle
if "BLOCK_SSH" in diff:
    # Commit
    device.commit_config()
    print("ACL mise à jour et commitée")
else:
    device.discard_config()
    print("Aucun changement détecté")
```

### 6.3 Utilisation du mode *candidate* (EOS, Junos, IOS‑XR)  

```python
# Charger un fichier complet en mode candidate
with open('full_config.cfg') as f:
    device.load_replace_candidate(config=f.read())

# Vérifier le diff
diff = device.compare_config()
print(diff)

# Commit avec timeout
device.commit_config(timeout=120)

# Rollback en cas d’erreur
device.rollback()
```

### 6.4 Rollback & sauvegarde automatisée  

```python
# Sauvegarde du running config avant tout changement
running = device.get_config()['running']
with open(f"/backup/{device.hostname}_running_{int(time.time())}.cfg", "w") as f:
    f.write(running)

# Après le commit, on garde la version précédente dans le journal du dispositif
# Pour un rollback manuel :
device.rollback()
```

### 6.5 Gestion des *commit* asynchrones (IOS‑XR)  

```python
device.load_merge_candidate(config=acl_fragment)
# Le commit peut prendre plusieurs secondes, on attend le résultat
device.commit_config(sync=False)   # lance le commit en background
while not device.is_committed():
    print("Commit en cours...")
    time.sleep(5)
print("Commit terminé")
```

---  

## 7. Intégration avec les frameworks d’orchestration  

### 7.1 Ansible + NAPALM  

```yaml
# playbook napalm_get_facts.yml
- name: Collect facts via NAPALM
  hosts: routers
  gather_facts: no
  collections:
    - napalm.napalm
  tasks:
    - napalm_get_facts:
        provider:
          hostname: "{{ inventory_hostname }}"
          username: "{{ ansible_user }}"
          password: "{{ ansible_ssh_pass }}"
          dev_os: iosxe
      register: facts

    - debug:
        var: facts
```

> **Points clés**  
* `dev_os` correspond au driver NAPALM.  
* Le module `napalm_get_facts` renvoie le même dictionnaire que `device.get_facts()`.  

### 7.2 Nornir + NAPALM  

```python
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yml")
result = nr.run(task=napalm_get, getters=["facts", "interfaces"])
print_result(result)
```

### 7.3 Netmiko + NAPALM (hybride)  

Dans certains cas, on veut exploiter la puissance de Netmiko (ex. `send_command`) puis basculer vers NAPALM pour le commit.

```python
from netmiko import ConnectHandler
from napalm import get_network_driver

# 1. Netmiko – collecte rapide d’une commande custom
net = ConnectHandler(device_type='cisco_ios',
                     host='10.0.0.1',
                     username='admin',
                     password='cisco123')
output = net.send_command('show version')
print(output)

# 2. NAPALM – mise à jour de configuration
driver = get_network_driver('iosxe')
dev = driver(hostname='10.0.0.1',
             username='admin',
             password='cisco123')
dev.open()
dev.load_merge_candidate(config='hostname R1')
dev.commit_config()
dev.close()
```

---  

## 8. Sécurité, performance & bonnes pratiques  

### 8.1 Gestion des secrets  

| Méthode | Avantages | Inconvénients |
|---------|-----------|---------------|
| **Vault HashiCorp** | Chiffrement au repos, rotation dynamique | Complexité d’initialisation |
| **Ansible Vault** | Intégré à Ansible, simple | Nécessite de partager le mot de passe de déchiffrement |
| **OS environment variables** | Pas de fichiers en clair | Risque d’exposition via `ps` ou logs |
| **SSH‑key only** | Pas de mot de passe en clair | Pas adapté aux comptes *enable* uniquement |

**Exemple avec `python‑dotenv`**  

```bash
# .env
NAPALM_USER=admin
NAPALM_PASS=cisco123
```

```python
from dotenv import load_dotenv
import os
load_dotenv()
username = os.getenv('NAPALM_USER')
password = os.getenv('NAPALM_PASS')
```

### 8.2 Optimisation des appels  

| Situation | Optimisation |
|-----------|--------------|
| **Multiples dispositifs** | Utilisez le **ThreadPoolExecutor** ou **asyncio** (napalm‑async) pour paralléliser les connexions. |
| **Grandes configurations** | Limitez le `compare_config()` aux sections modifiées (`load_merge_candidate` + `diff`). |
| **NETCONF** | Activez le `capability` `urn:ietf:params:netconf:base:1.1` pour le *chunked framing* (réduit la latence). |
| **eAPI (Arista)** | Utilisez le paramètre `session_log` pour réutiliser les connexions HTTP Keep‑Alive. |

#### Exemple d’exécution parallèle (Python 3.9+)

```python
import concurrent.futures
from napalm import get_network_driver

hosts = ['10.0.0.1', '10.0.0.2', '10.0.0.3']
driver = get_network_driver('iosxe')

def fetch_facts(host):
    dev = driver(hostname=host,
                 username='admin',
                 password='cisco123')
    dev.open()
    facts = dev.get_facts()
    dev.close()
    return facts

with concurrent.futures.ThreadPoolExecutor(max_workers