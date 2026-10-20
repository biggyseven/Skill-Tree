# CI/CD & Git pour le réseau – Cours intensif (Niveau Senior Network Admin)  

> **Objectif** : Maîtriser la mise en place d’une chaîne d’intégration et de déploiement continu (CI/CD) pour les environnements réseau, en s’appuyant sur Git comme source de vérité. Vous repartirez avec une architecture prête à être déployée, des scripts d’automatisation, des bonnes pratiques et un atelier de dépannage complet.  

---  

## 1. Introduction & Pourquoi le CI/CD en réseau ?  

| Contexte traditionnel | Environnement CI/CD moderne |
|----------------------|-----------------------------|
| **Modifications manuelles** (telnet/SSH, console) | **Automatisation déclarative** (IaC) |
| **Documentation séparée** (Word, PDF) | **Documentation versionnée** (Git) |
| **Déploiement ponctuel** (maintenance planifiée) | **Déploiement continu** (push‑to‑prod) |
| **Rollback difficile** (copie de config) | **Rollback automatisé** (Git revert + playbook) |
| **Visibilité limitée** (ticket) | **Traçabilité complète** (pipeline, logs) |

Les réseaux modernes (SD‑WAN, automatisation de data‑center, NFV) exigent :  

* **Vélocité** – déployer des changements en minutes, pas en heures.  
* **Fiabilité** – éviter les erreurs humaines qui provoquent des outages.  
* **Audits & conformité** – chaque modification doit être traçable, signée et approuvée.  

Le CI/CD répond à ces exigences en appliquant les mêmes principes que le développement logiciel : **source‑controlled**, **testée**, **validée**, **déployée**.  

---  

## 2. Fondamentaux de Git appliqués au réseau  

### 2.1. Repository Layout (exemple de structure)

```
network-repo/
├── inventories/
│   ├── prod/
│   │   ├── hosts.yml
│   │   └── groups.yml
│   └── lab/
│       ├── hosts.yml
│       └── groups.yml
├── playbooks/
│   ├── base.yml               # configuration de base (NTP, syslog)
│   ├── routing.yml            # OSPF/BGP
│   └── security.yml           # ACL, zone‑based FW
├── roles/
│   ├── cisco_ios/
│   │   ├── tasks/
│   │   └── templates/
│   └── junos/
│       ├── tasks/
│       └── templates/
├── tests/
│   ├── lint/
│   │   └── ansible-lint.yml
│   └── integration/
│       └── test_ospf.yml
├── .gitlab-ci.yml
└── README.md
```

* **Inventories** : source de vérité sur les hôtes et groupes.  
* **Playbooks** : « déclaration » de la configuration réseau.  
* **Roles** : réutilisables, versionnés séparément.  
* **Tests** : lint, unit, integration.  

### 2.2. Branching strategy recommandée (Git Flow + NetOps)

| Branche | Usage | Exemple de commit |
|--------|-------|-------------------|
| `main` | Production – état validé, toujours déployable | `Merge branch 'feature/bgp‑peering' into main` |
| `dev`  | Staging – pré‑production, tests d’intégration | `Add test suite for OSPF` |
| `feature/*` | Développement d’une nouvelle fonctionnalité (BGP, ACL) | `feature/bgp‑peer‑add` |
| `hotfix/*` | Corrections urgentes sur `main` | `hotfix/ntp‑typo` |
| `release/*` | Pré‑déploiement, gel des changements | `release/2024.10` |

**Règle d’or** : *Aucun commit direct sur `main`.* Tous les changements passent par une MR (Merge Request) qui déclenche la pipeline CI.  

---  

## 3. Architecture CI/CD adaptée au réseau  

```
+-------------------+      +--------------------+      +-------------------+
|   Git Repository  | ---> |   CI Server (JENK) | ---> |   CD Runner (Ansible) |
|   (GitLab, GH, BB)|      |   (Lint, Test)     |      |   (Playbooks)          |
+-------------------+      +--------------------+      +-------------------+
          |                         |                         |
          v                         v                         v
   Webhook / API            Docker containers          SSH / NETCONF / RESTCONF
   (push, MR)               (ansible‑lint, pyATS)      (Cisco IOS, NX‑OS, Junos)
```

* **CI** : vérifie la syntaxe (YAML, Jinja2), exécute les tests unitaires (pyATS, NTC) et crée un artefact (bundle de playbooks).  
* **CD** : le runner récupère l’artefact, applique les changements via Ansible/Nornir, puis notifie le résultat.  

### 3.1. Outils couramment utilisés  

| Outil | Rôle | Points forts | Limites |
|------|------|--------------|---------|
| **GitLab CI** | Pipelines intégrées, artefacts, secrets | UI riche, runners auto‑hosted | Nécessite GitLab SaaS ou on‑prem |
| **Jenkins** | Pipeline as Code (Jenkinsfile) | Plugins nombreux (Cisco, Ansible) | Gestion des plugins lourde |
| **GitHub Actions** | CI/CD natif GitHub | Marketplace d’actions, secrets | Limité aux runners GitHub (ou self‑hosted) |
| **Azure DevOps Pipelines** | CI/CD hybride | Intégration Azure, artefacts | Moins orienté réseau que GitLab |
| **Ansible Tower / AWX** | Orchestrateur CD | RBAC, API, job templates | Coût (Tower) ou complexité (AWX) |
| **Nornir** | Pythonic CD, parallélisation | Bibliothèque pure Python, extensible | Moins d’UI que Ansible |
| **NetBox** | Source of truth (inventaire) | Modèle de données riche | Pas de pipeline CI, nécessite intégration |

---  

## 4. Mise en place d’une pipeline CI (exemple GitLab CI)  

### 4.1. `.gitlab-ci.yml` minimal  

```yaml
stages:
  - lint
  - test
  - package
  - deploy

variables:
  ANSIBLE_FORCE_COLOR: "true"
  PYTHONPATH: "$CI_PROJECT_DIR"

# ---------- Lint ----------
lint_ansible:
  stage: lint
  image: python:3.11-slim
  script:
    - pip install ansible ansible-lint
    - ansible-lint playbooks/
  artifacts:
    reports:
      codequality: lint_report.json

# ---------- Unit Tests ----------
test_pyats:
  stage: test
  image: ciscotest/pyats:latest
  script:
    - pip install -r requirements.txt
    - pyats run job test_ospf.job
  artifacts:
    when: always
    paths:
      - logs/

# ---------- Package ----------
package_bundle:
  stage: package
  image: alpine:latest
  script:
    - tar -czf bundle.tar.gz playbooks/ roles/ inventories/
  artifacts:
    paths:
      - bundle.tar.gz
    expire_in: 1 week

# ---------- Deploy ----------
deploy_to_lab:
  stage: deploy
  image: python:3.11
  script:
    - pip install ansible
    - ansible-playbook -i inventories/lab/hosts.yml playbooks/base.yml
  only:
    - dev
  when: manual
```

**Explications clés**  

* **Stages** : `lint → test → package → deploy`.  
* **Artifacts** : les artefacts (bundle, logs) sont conservés pour le CD.  
* **`only: dev`** : le déploiement automatique ne s’exécute que sur la branche `dev`.  

### 4.2. Lint & Validation  

* **`ansible-lint`** : détecte les mauvaises pratiques (usage de `command` au lieu de modules).  
* **`yamllint`** : assure la conformité du format YAML (indents, clés).  
* **`cisco‑ntc‑templates`** + **`ntc‑client`** : validation de la sortie de `show` contre les templates.  

```bash
# Installation sur runner
pip install yamllint ansible-lint ntc-templates ntc-client
# Exemple de validation de la sortie d'un show command
ntc-parse --template "cisco_ios_show_version.textfsm" < show_version.txt
```  

---  

## 5. Déploiement CD – Ansible + NAPALM  

### 5.1. Playbook de base (exemple)  

```yaml
---
- name: Configure base services on all IOS devices
  hosts: ios
  gather_facts: no
  connection: network_cli
  vars:
    ansible_network_os: ios
    ansible_user: "{{ vault_user }}"
    ansible_password: "{{ vault_pass }}"
  tasks:
    - name: Ensure NTP servers are configured
      ios_config:
        lines:
          - ntp server 192.0.2.10 prefer
          - ntp server 192.0.2.11
        save_when: changed

    - name: Deploy syslog configuration
      ios_config:
        lines:
          - logging host 192.0.2.20
          - logging trap warnings
        save_when: changed

    - name: Commit (if using IOS‑XR or NX‑OS)
      when: ansible_network_os in ['iosxr','nxos']
      nxos_config:
        save: true
```

### 5.2. Utilisation de NAPALM pour le **diff** avant commit  

```bash
napalm get-config --hostname r1.example.com \
    --username admin --password cisco123 \
    --optional_args '{"port": 22}' \
    --config_type running > running_before.cfg

# Après le playbook
napalm get-config --hostname r1.example.com ... > running_after.cfg

# Diff
diff -u running_before.cfg running_after.cfg | less
```

*Si le diff dépasse un seuil (ex. > 30 lignes), le pipeline échoue et alerte.*  

### 5.3. Rollback automatisé  

```yaml
- name: Rollback to previous commit if validation fails
  hosts: ios
  gather_facts: no
  connection: network_cli
  tasks:
    - name: Retrieve previous configuration from Git
      git:
        repo: "git@example.com:netops/configs.git"
        dest: /tmp/prev_cfg
        version: "{{ rollback_tag }}"

    - name: Push rollback configuration
      ios_config:
        src: /tmp/prev_cfg/{{ inventory_hostname }}.cfg
        replace: line
        save_when: changed
```

Le tag `rollback_tag` est généré automatiquement lors d’un **failed deployment** (`git tag -a rollback-{{ ansible_date_time.iso8601 }} -m "Rollback after failure"`).  

---  

## 6. Tests d’intégration réseau (pyATS / NTC)  

### 6.1. Exemple de job pyATS (`test_ospf.job`)  

```yaml
testscript:
  name: test_ospf
  description: Verify OSPF adjacency & LSDB
  groups: [lab]

  sections:
    - name: Connect
      steps:
        - connect:
            hostname: "{{ device_ip }}"
            protocol: ssh
            username: "{{ username }}"
            password: "{{ password }}"

    - name: Verify OSPF Neighbors
      steps:
        - execute:
            command: show ip ospf neighbor
        - parse:
            template: cisco_ios_show_ip_ospf_neighbor.textfsm
        - assert:
            that:
              - "len(result) == expected_neighbors"

    - name: Verify LSDB
      steps:
        - execute:
            command: show ip ospf database
        - parse:
            template: cisco_ios_show_ip_ospf_database.textfsm
        - assert:
            that:
              - "len(result) >= min_lsas"
```

### 6.2. Intégration dans GitLab CI  

```yaml
test_pyats:
  stage: test
  image: ciscotest/pyats:latest
  script:
    - pip install -r requirements.txt
    - pyats run job test_ospf.job --testbed testbed.yaml
```

---  

## 7. Sécurité & Gestion des secrets  

| Méthode | Implémentation | Avantages | Inconvénients |
|--------|----------------|-----------|---------------|
| **Git‑crypt** | `git-crypt unlock <keyfile>` | Chiffrement au repos, transparent pour les devs | Gestion de la clé hors‑Git |
| **Ansible Vault** | `ansible-vault encrypt_string` | Intégré à Ansible, granularité | Nécessite le mot de passe en CI (via variable protégée) |
| **HashiCorp Vault** | `vault read secret/network` | API, rotation dynamique, audit | Dépendance supplémentaire |
| **CI secret variables** | `CI/CD > Variables > Protected` | Simple, UI GitLab/GH | Visible par les mainteneurs du runner |

**Best practice** : ne jamais stocker de mots de passe en clair dans le repo. Utiliser **Ansible Vault** + **protected CI variables** pour les passer au runner.  

```yaml
# Exemple de variable protégée dans GitLab
variables:
  ANSIBLE_VAULT_PASSWORD: "${ANSIBLE_VAULT_PASSWORD}"
```

---  

## 8. Comparatif des outils d’orchestration  

| Critère | **Ansible** | **Nornir** | **SaltStack** | **Chef Infra** |
|--------|-------------|------------|---------------|----------------|
| **Langage** | YAML + Jinja2 | Python pur | YAML + Python | Ruby DSL |
| **Parallelisme** | Forks (default 5) | ThreadPool / AsyncIO | Multi‑process | Chef client |
| **Idempotence** | Modules idempotents | À implémenter manuellement | Oui | Oui |
| **Intégration CI** | Large (Docker, AWX) | Simple (Python script) | Salt‑API | Chef Automate |
| **Gestion d’inventaire** | Static, dynamic (plugins) | Python objects (NetBox, CSV) | Master‑minion | Chef Server |
| **Learning curve** | Modéré | Élevé (Python) | Modéré | Élevé (Ruby) |
| **Support réseau** | Modules natifs (ios, nxos, junos) | Netmiko/NAPALM | Netconf, RESTCONF | Peu d’outils natifs |

---  

## 9. Schéma ASCII d’une pipeline complète (CI → CD → Validation)  

```
+-------------------+          +----------------------+          +-------------------+
|   Git Push (dev)  |  webhook |   GitLab CI Runner   |  artifact|   Ansible Tower   |
|   feature/ospf   +--------->+  (lint, unit, pyATS) +--------->+ (playbook exec)   |
+-------------------+          +----------+-----------+          +----+--------------+
                                          |                       |
                                          v                       v
                                   +------+-------+        +------+------+
                                   |  Docker Img  |        |  Device(s)  |
                                   |  ansible‑lint|        |  IOS/NX‑OS  |
                                   +------+-------+        +------+------+
                                          |                       |
                                          v                       v
                                   +------+-------+        +------+------+
                                   |  GitLab Artif.|  SSH  |  Config diff |
                                   +------+-------+        +------+------+
                                          |                       |
                                          v                       v
                                   +------+-------+        +------+------+
                                   |  Notification|  Email|  Slack Bot  |
                                   +--------------+-------+-------------+
```

---  

## 10. Atelier de dépannage – Scénario complet  

### 10.1. Contexte  

* Vous avez un lab avec trois routeurs Cisco IOS‑XE (`R1`, `R2`, `R3`).  
* La branche `dev` contient un nouveau playbook `bgp.yml` qui doit établir un peering iBGP entre les trois routeurs.  
* Vous avez déclenché la pipeline via un *Merge Request* (MR).  

**Résultat** :  

* CI passe (`lint` & `unit` OK).  
* La phase `deploy_to_lab` échoue avec le message :  

```
[WARNING]: Unable to parse /etc/ansible/hosts as an inventory source
fatal: [R1]: FAILED! => {"msg": "SSH Error: Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password)."}
```

### 10.2. Étapes de diagnostic  

| Étape |