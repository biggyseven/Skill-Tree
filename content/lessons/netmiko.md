# Cours Intensif – Scripting Réseau avec Python & Netmiko  
**Niveau : Administrateur Réseau Senior (CCIE)**  
**Durée estimée : 2 jours (16 h) – 10 000 + caractères**  

---

## Table des matières  

| # | Section | Objectifs |
|---|---------|-----------|
| 1 | Introduction & concepts fondamentaux | Comprendre pourquoi automatiser, les principes du « Infrastructure as Code » (IaC) |
| 2 | Environnement de travail | Installation, virtualisation, gestion des dépendances |
| 3 | Python – rappels avancés | Types, comprehensions, décorateurs, context managers, typing |
| 4 | Netmiko – architecture et API | Connexions, drivers, gestion des prompts, logs |
| 5 | Bibliothèques complémentaires | NAPALM, TextFSM, Jinja2, Paramiko, Pydantic, Rich |
| 6 | Modélisation des configurations | Templates Jinja2, variables, boucles, conditionnels |
| 7 | Gestion du parc (inventory) | CSV, YAML, JSON, SQLite, NetBox, Ansible‑dynamic inventory |
| 8 | Bonnes pratiques de code | Logging, tests unitaires, CI/CD, linting, packaging |
| 9 | Dépannage & atelier pratique | Scénario complet – mise en place, debug, rollback |
|10 | Annexes | Cheat‑sheets, références, scripts prêts‑à‑l’emploi |

---

## 1 – Pourquoi automatiser le réseau ?  

| Domaine | Gains attendus | Risques résiduels |
|---------|----------------|-------------------|
| Provisioning d’équipements | Temps de déploiement ↓ de 90 % (minutes → secondes) | Erreurs de template si variables manquantes |
| Gestion des configurations | Historisation, conformité, audit | Dépendance à la connectivité SSH |
| Monitoring & collecte | Extraction de données en temps réel, corrélation | Saturation du dispositif si requêtes trop fréquentes |
| Migration / upgrade | Scripts idempotents, rollback automatisé | Bugs de script → panne massive si non testé |

> **Citation** – *“Automation is not about removing people, it’s about removing the repetitive work so engineers can focus on design.”* – Jeff Dean

---

## 2 – Mise en place de l’environnement  

### 2.1 Virtualisation (Docker + VS Code Remote)  

```bash
# Créez un réseau Docker dédié
docker network create netlab

# Lancez un container Ubuntu avec Python 3.12 et Netmiko
docker run -dit --name py‑netlab \
    --network netlab \
    -v $(pwd)/work:/work \
    python:3.12-slim-bullseye bash -c "apt-get update && \
    apt-get install -y git openssh-client && \
    pip install netmiko napalm textfsm jinja2 pydantic rich && \
    tail -f /dev/null"
```

- **VS Code** → *Remote‑Containers* → attachez‑vous au container `py‑netlab`.  
- Le répertoire `work` est partagé avec votre hôte (scripts, inventory).

### 2.2 Gestion des dépendances – `pipenv` vs `poetry`  

| Outil | Verrouillage | Gestion des environnements | Support PEP‑517 |
|-------|--------------|---------------------------|-----------------|
| `pipenv` | `Pipfile.lock` | Automatique (`pipenv shell`) | Oui |
| `poetry` | `poetry.lock` | `poetry env use` | Oui (recommandé pour projets complexes) |

```bash
# Exemple avec Poetry
poetry init          # crée pyproject.toml
poetry add netmiko napalm jinja2 rich
poetry shell        # active l'env virtuel
```

---

## 3 – Python – Rappels avancés pour le réseau  

### 3.1 Types et `typing`  

```python
from typing import List, Dict, Literal, TypedDict, Optional

class Device(TypedDict):
    hostname: str
    ip: str
    platform: Literal['cisco_ios', 'cisco_xe', 'juniper_junos']

def ping(host: str, count: int = 3) -> bool:
    ...

# Utilisation
devices: List[Device] = [...]
```

### 3.2 Context Managers personnalisés  

```python
from contextlib import AbstractContextManager
import logging

class NetmikoSession(AbstractContextManager):
    def __init__(self, device: dict):
        self.device = device
        self.conn = None
        self.logger = logging.getLogger('netmiko')

    def __enter__(self):
        from netmiko import ConnectHandler
        self.conn = ConnectHandler(**self.device)
        self.logger.info(f"Connected to {self.device['host']}")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.disconnect()
            self.logger.info(f"Disconnected from {self.device['host']}")
        return False   # Propager les exceptions
```

```python
with NetmikoSession(dev) as conn:
    output = conn.send_command('show version')
    print(output)
```

### 3.3 Décorateurs de retry (exponential back‑off)  

```python
import time
from functools import wraps

def retry(attempts: int = 3, backoff: float = 1.5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = backoff
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == attempts - 1:
                        raise
                    time.sleep(delay)
                    delay *= backoff
        return wrapper
    return decorator
```

---

## 4 – Netmiko – Architecture et API  

### 4.1 Principe de fonctionnement  

```
+-------------------+        +--------------------+
|   Python script   |  SSH   |   Network device   |
|   (Netmiko)       |<------>|   (IOS, NX‑OS…)    |
+-------------------+        +--------------------+
        |  ^  |
        |  |  |  Prompt‑handler (expect‑like)
        v  |  v
   Netmiko Base class
```

- **Base class** : `BaseConnection` (gestion du socket, log, timeouts).  
- **Driver** : `CiscoIosSSH`, `CiscoXrSSH`, `JuniperJunosSSH`, etc.  
- **Prompt handling** : `self.find_prompt()`, `self._test_channel_read()`.

### 4.2 Connexion simple  

```python
from netmiko import ConnectHandler

cisco = {
    "device_type": "cisco_ios",
    "host": "10.10.10.10",
    "username": "admin",
    "password": "cisco123",
    "secret": "enable123",          # enable secret
    "global_delay_factor": 2,      # pour les IOS lents
}

with ConnectHandler(**cisco) as net_connect:
    net_connect.enable()            # passe en mode enable
    version = net_connect.send_command("show version")
    print(version)
```

### 4.3 Envoi de configuration (idempotence)  

```python
cfg_commands = [
    "interface Loopback0",
    "description Gestion du réseau",
    "ip address 10.255.255.1 255.255.255.255",
    "no shutdown",
]

output = net_connect.send_config_set(cfg_commands, exit_config_mode=True)
print(output)
```

> **Astuce** – Utilisez `send_config_set(..., commit=False)` sur les plateformes qui supportent le *commit* (e.g., Junos) pour préparer le diff avant de valider.

### 4.4 Gestion des erreurs  

| Exception Netmiko | Cause typique | Action corrective |
|-------------------|----------------|--------------------|
| `NetMikoTimeoutException` | Timeout TCP / ACL bloquant SSH | Vérifier reachabilité, ACL, `ssh -vvv` |
| `NetMikoAuthenticationException` | Creds invalides ou `enable` manquant | Re‑vérifier `username/password/secret` |
| `ReadTimeout` | Prompt non reconnu (ex: banner long) | Ajuster `global_delay_factor` ou `banner_timeout` |
| `SSHException` (Paramiko) | Version SSH incompatible | Forcer `ssh_version=2` ou mettre à jour firmware |

---

## 5 – Bibliothèques complémentaires  

| Librairie | Usage principal | Exemple d’appel |
|-----------|----------------|-----------------|
| **NAPALM** | Abstraction multi‑vendor, `get_facts()`, `load_merge_candidate()` | `driver = get_network_driver('ios')` |
| **TextFSM** | Parsing de sortie texte en tables | `parse_output = textfsm.TextFSM(open('show_int.template')).ParseText(output)` |
| **Jinja2** | Templates de configuration | `template.render(hostname=dev['hostname'])` |
| **Paramiko** | SSH bas‑niveau (utile pour tunnels) | `client = paramiko.SSHClient()` |
| **Pydantic** | Validation de données d’inventory | `class DeviceModel(BaseModel): ip: IPvAnyAddress` |
| **Rich** | Affichage coloré, tables, progress bars | `from rich.console import Console` |
| **PySNMP** | Collecte SNMP (complémentaire à Netmiko) | `snmp_get(... )` |

### 5.1 Exemple d’intégration TextFSM  

```python
import textfsm
from pathlib import Path

template_path = Path('templates/show_int.template')
with open(template_path) as f, open('show_int.txt') as out:
    fsm = textfsm.TextFSM(f)
    rows = fsm.ParseText(out.read())

# rows → list of lists, chaque sous‑liste = champs du template
for intf, status, protocol in rows:
    print(f"{intf:20} {status:8} {protocol}")
```

> **Template minimal** (`show_int.template`)  

```
Value INTERFACE (\S+)
Value STATUS (\w+)
Value PROTOCOL (\w+)

Start
  ^${INTERFACE}\s+${STATUS}\s+${PROTOCOL} -> Record
```

---

## 6 – Modélisation des configurations (Jinja2)  

### 6.1 Structure du répertoire  

```
/project
│
├─ inventory/
│   └─ devices.yaml
├─ templates/
│   ├─ ios_base.j2
│   └─ nxos_l3_interface.j2
├─ scripts/
│   └─ deploy.py
└─ requirements.txt
```

### 6.2 Exemple de template `ios_base.j2`  

```jinja
! -------------------------------------------------
! Configuration générée automatiquement – {{ now }}
! -------------------------------------------------
hostname {{ hostname }}

{% if domain_name %}
ip domain-name {{ domain_name }}
{% endif %}

{% for loop in loopbacks %}
interface Loopback{{ loop.id }}
 description {{ loop.description }}
 ip address {{ loop.ip }} {{ loop.mask }}
{% endfor %}

{% if ntp.servers %}
ntp server {{ ntp.servers[0] }}
{% for srv in ntp.servers[1:] %}
ntp server {{ srv }}
{% endfor %}
{% endif %}

end
```

### 6.3 Rendering avec Python  

```python
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import yaml, ipaddress

env = Environment(loader=FileSystemLoader('templates'), trim_blocks=True, lstrip_blocks=True)

def render_device(dev: dict) -> str:
    tmpl = env.get_template('ios_base.j2')
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    return tmpl.render(now=now, **dev)

# Chargement de l’inventory
with open('inventory/devices.yaml') as f:
    inventory = yaml.safe_load(f)

for dev in inventory['cisco_ios']:
    cfg = render_device(dev)
    Path(f"generated/{dev['hostname']}.cfg").write_text(cfg)
```

### 6.4 Idempotence – comparaison avant déploiement  

```python
from difflib import unified_diff

def diff_cfg(running: str, candidate: str) -> str:
    diff = unified_diff(running.splitlines(),
                        candidate.splitlines(),
                        fromfile='running',
                        tofile='candidate',
                        lineterm='')
    return '\n'.join(diff)

# Exemple d’usage
running_cfg = net_connect.send_command('show running-config')
candidate_cfg = render_device(dev)
print(diff_cfg(running_cfg, candidate_cfg))
```

---

## 7 – Gestion du parc (Inventory)  

### 7.1 Formats supportés  

| Format | Avantages | Inconvénients |
|--------|-----------|---------------|
| **YAML** | Lisibilité, hiérarchie, commentaires | Pas de schéma natif (mais Pydantic) |
| **CSV** | Simplicité, compatible Excel | Peu structuré, pas de listes imbriquées |
| **JSON** | Interopérabilité API | Verbosité, pas de commentaires |
| **SQLite** | Recherche rapide, relations | Nécessite un driver, migration de schéma |
| **NetBox** | Source unique, API REST, web UI | Déploiement supplémentaire |

### 7.2 Exemple d’inventory YAML  

```yaml
cisco_ios:
  - hostname: r1
    host: 10.0.0.1
    platform: cisco_ios
    username: admin
    password: cisco123
    secret: enable123
    domain_name: example.com
    loopbacks:
      - id: 0
        description: Management
        ip: 10.255.255.1
        mask: 255.255.255.255
      - id: 1
        description: VRF-Blue
        ip: 10.255.1.1
        mask: 255.255.255.255
    ntp:
      servers:
        - 192.168.0.1
        - 192.168.0.2
```

### 7.3 Validation avec Pydantic  

```python
from pydantic import BaseModel, IPvAnyAddress, validator
from typing import List, Literal

class Loopback(BaseModel):
    id: int
    description: str
    ip: IPvAnyAddress
    mask: IPvAnyAddress

class NTP(BaseModel):
    servers: List[IPvAnyAddress]

class Device(BaseModel):
    hostname: str
    host: IPvAnyAddress
    platform: Literal['cisco_ios', 'cisco_xe', 'juniper_junos']
    username: str
    password: str
    secret: str
    domain_name: str | None = None
    loopbacks: List[Loopback] = []
    ntp: NTP | None = None

# Chargement & validation
import yaml
with open('inventory/devices.yaml') as f:
    raw = yaml.safe_load(f)

devices = [Device(**d) for d in raw['cisco_ios']]
```

---

## 8 – Bonnes pratiques de code  

### 8.1 Logging structuré  

```python
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[RichHandler()]
)

log = logging.getLogger('netauto')
log.info('Début du playbook')
```

- **Niveaux** : `DEBUG` (données brutes), `INFO` (étapes), `WARNING` (timeouts), `ERROR` (échecs critiques).  
- **RotatingFileHandler** pour persistance (`maxBytes=5_000_000`).

### 8.2 Tests unitaires (pytest)  

```python
# tests/test_template.py
def test_render_loopbacks():
    dev = {
        "hostname": "r1",
        "loopbacks": [{"id": 0, "description": "MGMT", "ip": "10.255.255.1", "mask": "255.255.255.255"}],
        "domain_name": None,
        "ntp": {"servers": []}
    }
    cfg = render_device(dev)
    assert "interface Loopback0" in cfg
    assert "ip address 10.255.255.1 255.255.255.255" in cfg
```

- **CI** : GitHub Actions → `pytest`, `flake8`, `black --check`.  

### 8.3 Packaging (pip)  

```toml
# pyproject.toml (Poetry)
[tool.poetry]
name = "netauto"
version = "0.1.0"
description = "Toolkit d’automatisation réseau"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
netmiko = "^4.3.0"
jinja2 = "^3.1"
pydantic = "^2.6"
rich = "^13.7"

[tool.poetry.scripts]
netauto = "netauto.cli:main"
```

`poetry build && poetry publish` → partage interne via Artifactory.

---

## 9 – Atelier de dépannage (Lab)  

### 9.1 Scénario  

Vous devez déployer une nouvelle interface Loopback sur **10** routeurs Cisco IOS.  
Un des routeurs (`r5`) renvoie **`% Invalid input detected at '^' marker.`** lors de l’envoi du bloc de config.  

**Objectifs**  

1. Vérifier la connectivité SSH.  
2. Analyser le log Netmiko pour identifier le prompt réel.  
3. Corriger le template Jinja2 (mauvaise indentation).  
4. Implémenter un mécanisme de