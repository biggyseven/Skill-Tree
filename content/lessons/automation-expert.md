# Automatisation Réseau - Expert

**Niveau :** Expert

**Prérequis :** Automatisation Réseau Intermédiaire (`automation-intermediaire.md`), solide maîtrise de Python, des architectures CI/CD, de Docker/Git, ainsi que des principes de modélisation YANG et RESTCONF/NETCONF.

Ce module aborde l'automatisation réseau à l'échelle d'une infrastructure globale. Vous y découvrirez le framework **Nornir** pour l'exécution parallèle à haute performance, les pipelines **CI/CD** dédiés au *Network Infrastructure as Code* (NIaC), la validation automatisée avec **pyATS / Genie**, la **Télémétrie en Streaming**, et le réseau événementiel (**Event-Driven Automation**).

## 1. Multi-Threading & Concurrence Haute Performance avec Nornir

Bien qu'Ansible soit puissant, son surcoût (*overhead*) de performances peut devenir un frein sur des parcs de milliers d'équipements. **Nornir** est un framework d'automatisation pur Python qui offre un contrôle total et une exécution hautement concurrente (multi-threading).

```
                            ┌────────────────────────┐
                            │    NORNIR INVENTORY    │
                            │ (Hosts, Groups, Data)  │
                            └───────────┬────────────┘
                                        │
                                        ▼
                            ┌────────────────────────┐
                            │   NORNIR RUNNER CORE   │
                            │ (ThreadedPool / Async) │
                            └───────────┬────────────┘
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         ▼                              ▼                              ▼
  [ Thread 1: SW-01 ]            [ Thread 2: SW-02 ]            [ Thread N: SW-N ]
  (Netmiko/NAPALM Task)          (Netmiko/NAPALM Task)          (Netmiko/NAPALM Task)

```

### Exemple de script Nornir 3 (`nornir_run.py`) :

```
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result

# Initialisation de Nornir avec la configuration YAML
nr = InitNornir(config_file="config.yaml")

# Filtrage dynamique des équipements (Target: Site Paris)
paris_devices = nr.filter(site="paris")

# Définition de la tâche d'extraction
def get_device_facts(task):
    task.run(task=napalm_get, getters=["facts", "interfaces"])

# Exécution parallèle sur l'ensemble du sous-groupe
results = paris_devices.run(task=get_device_facts)

# Affichage structuré
print_result(results)

```

## 2. Testing & Validation de Réseau : pyATS / Genie

La validation post-changement est essentielle pour garantir l'absence de régression. Le framework **pyATS** (développé par Cisco) permet de modéliser, tester et comparer l'état opérationnel (*Operational State*) d'un réseau.

```
 [ État Réseau Avant Changement ] ──> ( Genie Learn / Snapshot A ) ──┐
                                                                     ├──> [ Genie Diff ] ──> [ Rapport de Conformité ]
 [ État Réseau Après Changement ] ──> ( Genie Learn / Snapshot B ) ──┘

```

### Exemple de Testbed pyATS (`testbed.yaml`) et script de validation :

```
# Test de différence d'état OSPF avant/après intervention
from genie.testbed import load

testbed = load('testbed.yaml')
dev = testbed.devices['R1-CORE']
dev.connect()

# Capture de l'état des voisins OSPF sous forme de structures de données Python
ospf_state = dev.parse('show ip ospf neighbor')

# Assertion de sécurité
for neighbor, data in ospf_state['ospf']['neighbors'].items():
    assert data['state'] == 'FULL', f"Alerte: Le voisin OSPF {neighbor} n'est pas dans l'état FULL !"

```

## 3. Network Infrastructure as Code (NIaC) & Pipeline CI/CD

Le paradigme **Network Infrastructure as Code (NIaC)** applique les règles du génie logiciel aux configurations réseau : contrôle de version (Git), revues de code (Pull Requests), tests automatisés, et déploiement continu.

```
 ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
 │ 1. Git Push  │ ───> │ 2. Dry-Run / │ ───> │ 3. Automated │ ───> │ 4. Continuous│
 │ (PR Config)  │      │ Syntax Check │      │ pyATS Tests  │      │ Deployment   │
 └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
                         (Pipeline)            (Virtual Lab)          (Production)

```

### Exemple de pipeline GitLab CI (`.gitlab-ci.yml`) pour le réseau :

```
stages:
  - validate
  - test
  - deploy

lint_and_validate:
  stage: validate
  script:
    - yamllint inventory/
    - python3 -m py_compile scripts/*.py

simulate_changes:
  stage: test
  script:
    - ansible-playbook -i inventory.yml deploy_bgp.yml --check --diff
    - pytest tests/test_network_syntax.py

deploy_to_production:
  stage: deploy
  script:
    - nornir_run.py --deploy
  only:
    - main

```

## 4. Télémétrie en Streaming & Observabilité (GNOI/GNMI)

Les requêtes SNMP traditionnelles basées sur le *polling* périodique sont remplacées par la **Télémétrie en Streaming** basée sur **gNMI** (*gRPC Network Management Interface*). L'équipement pousse les métriques en temps réel dès qu'une modification survient.

```
┌───────────────────────────────┐
│       Équipement Réseau       │
│  (gNMI Target / OpenConfig)   │
└───────────────┬───────────────┘
                │ Streaming PUSH (Protobuf / gRPC / Port 9339)
                ▼
┌───────────────────────────────┐
│      Collecteur (Telegraf)    │
└───────────────┬───────────────┘
                │ Time Series Data
                ▼
┌───────────────────────────────┐
│  Base InfluxDB / Prometheus   │ ───> [ Dashboard Grafana ]
└───────────────────────────────┘

```

### Avantages de gNMI / OpenConfig :

* **Mode On-Change :** Notification instantanée uniquement lorsqu'un état change (ex: port *down*).

* **Format Binaire Protobuf :** Empreinte bande passante et processeur extrêmement faible comparée au SNMP/XML.

* **Modèle Standardisé OpenConfig :** Télémétrie indépendante du constructeur.

## 5. Network Event-Driven Automation (EDA)

L'automatisation pilotée par les événements (**Event-Driven Automation**) permet au réseau de réagir et de s'auto-guérir (*self-healing*) sans intervention humaine.

```
 [ Événement Réseau ] ──> [ Syslog / Webhook / gNMI Stream ] ──> [ EDA Rulebook (Ansible EDA / StackStorm) ]
                                                                             │
                                                                             ▼
 [ Auto-Remédiation ] <── [ Action : Redémarrer l'interface / BGP ] <────────┘

```

### Exemple de Ansible Rulebook (`eda_rulebook.yml`) :

```
---
- name: Écouter les événements Syslog et auto-remédier
  hosts: all
  sources:
    - ansible.eda.syslog:
        host: 0.0.0.0
        port: 5000

  rules:
    - name: Détecter une erreur d'authentification répété sur un port
      condition: event.message contains "PORT_SECURITY_VIOLATION"
      action:
        run_playbook:
          name: playbooks/remediate_port_security.yml
          extra_vars:
            interface: "{{ event.interface }}"

```

## Commandes et Outils de Niveau Expert

| Outil / Commande | Description / Usage | 
| ----- | ----- | 
| `gnmic -a 192.168.1.1:9339 --insecure subscribe --path "openconfig-interfaces:interfaces"` | Outil CLI pour interroger et s'abonner aux flux de télémétrie gNMI. | 
| `pyats run job jobs/network_test_job.py` | Exécute une suite complète de tests automatiques pyATS/Genie. | 
| `ansible-rulebook --rulebook eda_rulebook.yml -i inventory.yml` | Lance le moteur Event-Driven Ansible pour écouter et traiter les événements temps réel. | 

## Points à Retenir

* **Nornir :** La solution idéale pour les réseaux à très grande échelle nécessitant performance, flexibilité Python et parallélisme strict.

* **pyATS / Genie :** Permet la validation complète d'état (*state verification*) et l'analyse de différence (*diff*) automatisée.

* **CI/CD & NIaC :** Transforme la gestion réseau en un workflow de développement sécurisé (validation Git, simulation, déploiement continu).

* **Télémétrie gNMI & Event-Driven Automation :** Assurent l'observabilité ultra-rapide et l'auto-réparation intelligente des réseaux modernes.