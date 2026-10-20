# Automatisation réseau : API REST, Netmiko, Ansible et Jinja2

L'automatisation réseau consiste à remplacer une partie des commandes manuelles
par des scripts et des modèles reproductibles. Elle ne supprime pas la
compréhension du réseau : elle déplace l'effort vers la validation, la
documentation et la gestion des changements.

> Analogie : un script est une recette de cuisine. Si la recette est claire, les
> ingrédients sont vérifiés et le résultat est goûté, elle produit le même plat
> chaque fois. Une mauvaise recette appliquée à cent cuisines produit cent fois
> la même erreur.

## 1. Pourquoi automatiser ?

Les tâches répétitives sont sources d'erreurs :

- créer des VLAN sur plusieurs switches ;
- ajouter une description de port ;
- vérifier une configuration ;
- sauvegarder les configurations ;
- déployer une ACL ;
- collecter des informations d'inventaire.

L'automatisation apporte :

- répétabilité ;
- rapidité ;
- traçabilité ;
- réduction des fautes de frappe ;
- possibilité de tests ;
- documentation vivante.

Elle exige en retour :

- une source de vérité ;
- des sauvegardes ;
- des validations ;
- une gestion des secrets ;
- un plan de retour arrière.

## 2. Les API REST

Une API REST expose des ressources accessibles par HTTP. Les équipements et
les contrôleurs modernes proposent souvent une API pour éviter de se connecter
en SSH.

### Méthodes HTTP

| Méthode | Usage |
|---|---|
| GET | Lire une ressource |
| POST | Créer une ressource |
| PUT | Remplacer une ressource |
| PATCH | Modifier partiellement |
| DELETE | Supprimer |

### Codes de statut

| Code | Signification |
|---:|---|
| 200 | Succès |
| 201 | Ressource créée |
| 204 | Succès sans contenu |
| 400 | Requête invalide |
| 401 | Authentification requise |
| 403 | Accès refusé |
| 404 | Ressource absente |
| 429 | Trop de requêtes |
| 500 | Erreur serveur |

### JSON

Les API modernes échangent souvent du JSON :

```json
{
  "interface": "GigabitEthernet0/1",
  "description": "Uplink vers le coeur",
  "enabled": true
}
```

Le JSON est lisible par les humains et par les programmes. Il faut vérifier les
types : un nombre, une chaîne et un booléen ne sont pas interchangeables.

### Authentification

Selon l'API :

- clé API dans un header ;
- jeton Bearer ;
- OAuth 2.0 ;
- certificat client ;
- session avec cookie.

Les secrets ne doivent jamais être écrits dans le code source ou dans un dépôt
Git. On utilise des variables d'environnement, un coffre-fort ou un gestionnaire
de secrets.

### Exemple avec curl

```bash
curl -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/json" \
  https://controller.example/api/v1/devices
```

### Exemple Python avec requests

```python
import os
import requests

token = os.environ["CONTROLLER_TOKEN"]
response = requests.get(
    "https://controller.example/api/v1/devices",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10,
)
response.raise_for_status()
devices = response.json()
print(len(devices), "équipements")
```

Il faut gérer :

- les timeouts ;
- les codes HTTP ;
- les réponses paginées ;
- les limites de débit ;
- les erreurs réseau ;
- les données absentes ou inattendues.

## 3. NETCONF et RESTCONF

NETCONF est un protocole de configuration basé sur XML et SSH. RESTCONF expose
des données YANG via HTTP. Les modèles YANG décrivent la structure des données.

Ces protocoles sont plus structurés que le CLI, mais demandent de connaître le
modèle de l'équipement. Ils sont adaptés aux plateformes qui les supportent
nativement.

## 4. Netmiko

Netmiko est une bibliothèque Python qui simplifie les sessions SSH vers les
équipements réseau. Elle gère les invites, la pagination et les particularités
des constructeurs.

### Installation

```bash
python -m pip install netmiko
```

### Connexion simple

```python
from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios",
    "host": "192.168.1.1",
    "username": "admin",
    "password": "motdepasse",
    "secret": "enable_secret",
    "timeout": 10,
}

with ConnectHandler(**device) as conn:
    conn.enable()
    output = conn.send_command("show ip interface brief")
    print(output)
```

Le bloc `with` ferme la session proprement. Le mot de passe ne doit pas être
codé en dur dans un script de production.

### Envoyer une configuration

```python
commands = [
    "interface GigabitEthernet0/1",
    "description Uplink vers le coeur",
    "switchport mode trunk",
]

with ConnectHandler(**device) as conn:
    conn.enable()
    output = conn.send_config_set(commands)
    print(output)
    print(conn.save_config())
```

`send_config_set` entre en mode configuration, applique les commandes puis
revient au mode précédent. Il faut vérifier le résultat et sauvegarder seulement
si la configuration est correcte.

### Gérer les erreurs

```python
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException

try:
    with ConnectHandler(**device) as conn:
        print(conn.send_command("show version"))
except NetmikoAuthenticationException:
    print("Authentification refusée")
except NetmikoTimeoutException:
    print("Équipement injoignable")
```

Il faut aussi prévoir :

- un inventaire ;
- des timeouts ;
- des logs ;
- des sauvegardes avant changement ;
- une validation après changement ;
- un rollback.

### Bonnes pratiques

- utiliser un compte de service dédié ;
- préférer les clés SSH aux mots de passe ;
- limiter les commandes autorisées ;
- désactiver la pagination ;
- ne pas parser le CLI quand une API existe ;
- tester sur un équipement de lab ;
- versionner les scripts.

## 5. Ansible

Ansible est un outil d'automatisation sans agent. Il se connecte aux équipements
par SSH ou API et applique des tâches décrites dans des playbooks YAML.

### Inventaire

```ini
[switchs]
sw1 ansible_host=192.168.1.10
sw2 ansible_host=192.168.1.11

[switchs:vars]
ansible_network_os=cisco.ios.ios
ansible_user=automation
ansible_connection=network_cli
```

### Playbook

```yaml
---
- name: Vérifier les interfaces
  hosts: switchs
  gather_facts: false
  tasks:
    - name: Afficher les interfaces
      cisco.ios.ios_command:
        commands:
          - show ip interface brief
      register: interfaces

    - name: Afficher le résultat
      ansible.builtin.debug:
        var: interfaces.stdout_lines
```

### Configuration

```yaml
---
- name: Configurer la description du port
  hosts: switchs
  gather_facts: false
  tasks:
    - name: Appliquer la description
      cisco.ios.ios_config:
        lines:
          - description Uplink vers le coeur
        parents:
          - interface GigabitEthernet0/1
```

### Idempotence

Une tâche idempotente ne modifie l'équipement que si l'état souhaité n'est pas
déjà présent. C'est un avantage majeur par rapport à un script qui renvoie
toutes les commandes à chaque exécution.

Les modules réseau modernes comparent souvent la configuration avant de
l'appliquer. Il faut néanmoins vérifier que le module utilisé est réellement
idempotent.

### Variables et group_vars

```text
inventory/
  hosts.ini
  group_vars/
    switchs.yml
```

```yaml
uplink_description: "Uplink vers le coeur"
allowed_vlans: "10,20,30"
```

Les variables évitent de dupliquer les valeurs dans les playbooks.

### Vault

Les mots de passe et clés ne doivent pas être stockés en clair :

```bash
ansible-vault encrypt group_vars/switchs/vault.yml
ansible-playbook -i inventory/hosts.ini playbook.yml --ask-vault-pass
```

### Check mode

Le mode `--check` permet de simuler certaines tâches. Tous les modules ne le
supportent pas parfaitement, mais il aide à détecter les changements imprévus.

```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --check
```

## 6. Jinja2

Jinja2 est un moteur de templates Python. Il permet de générer une configuration
à partir de variables, de boucles et de conditions.

### Exemple simple

```jinja2
hostname {{ hostname }}
!
{% for vlan in vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% endfor %}
```

Données :

```yaml
hostname: sw1
vlans:
  - id: 10
    name: Users
  - id: 20
    name: Voice
```

Résultat :

```text
hostname sw1
!
vlan 10
 name Users
vlan 20
 name Voice
```

### Conditions

```jinja2
{% if uplink %}
interface {{ uplink }}
 description Uplink
 switchport mode trunk
{% endif %}
```

### Filtres

```jinja2
{{ vlans | length }} VLANs
{{ description | upper }}
{{ allowed_vlans | join(",") }}
```

### Boucle sur des interfaces

```jinja2
{% for port in access_ports %}
interface {{ port.name }}
 description {{ port.description }}
 switchport mode access
 switchport access vlan {{ port.vlan }}
{% endfor %}
```

### Génération avec Python

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader("templates"),
    trim_blocks=True,
    lstrip_blocks=True,
)
template = env.get_template("switch.j2")
configuration = template.render(
    hostname="sw1",
    vlans=[{"id": 10, "name": "Users"}],
)
print(configuration)
```

Le template doit être testé avec des données valides et invalides. Une variable
manquante peut produire une configuration partielle ou une erreur.

## 7. Une chaîne d'automatisation complète

```text
Source de vérité YAML
        |
        v
Validation du schéma
        |
        v
Template Jinja2
        |
        v
Ansible / Netmiko / API
        |
        v
Équipement réseau
        |
        v
Tests et logs
```

### Exemple de source de vérité

```yaml
switches:
  - hostname: sw1
    mgmt_ip: 192.168.1.10
    vlans:
      - id: 10
        name: Users
      - id: 20
        name: Voice
```

Le fichier est versionné dans Git. Une revue de code précède le déploiement.
Le pipeline génère la configuration, la valide, puis l'applique sur un
équipement de test avant la production.

### Validation

Avant d'appliquer :

- vérifier la syntaxe YAML ;
- vérifier les adresses et les VLAN ;
- générer la configuration et la relire ;
- tester sur un lab ;
- sauvegarder la configuration actuelle ;
- prévoir un rollback.

Après application :

- vérifier les voisins ;
- vérifier les routes ;
- vérifier les interfaces ;
- comparer la configuration ;
- surveiller les logs.

## 8. Modèles de données et idempotence

Une automatisation fiable commence par une source de vérité lisible. Le fichier
YAML ou JSON décrit l'intention, pas une suite de commandes CLI.

```yaml
site:
  name: paris
  switches:
    - hostname: sw1
      management_ip: 192.168.1.10
      vlans:
        - id: 10
          name: Users
        - id: 20
          name: Voice
      uplinks:
        - name: GigabitEthernet0/1
          description: Uplink coeur
          allowed_vlans: "10,20"
```

Un schéma doit préciser les champs obligatoires, les types et les plages
valides. Une validation avant génération évite de produire une configuration
incomplète. On peut utiliser un schéma JSON, Pydantic ou un rôle Ansible dédié.

L'idempotence signifie que réappliquer le même état ne change rien si la
configuration est déjà correcte. Un script qui renvoie aveuglément toutes les
commandes n'est pas forcément idempotent : il peut redémarrer une interface ou
réinitialiser un compteur sans nécessité.

## 9. Cas concret : déployer des VLAN

### Données

```yaml
hostname: sw1
vlans:
  - id: 10
    name: Users
  - id: 20
    name: Voice
  - id: 30
    name: Guests
```

### Template Jinja2

```jinja2
hostname {{ hostname }}
!
{% for vlan in vlans %}
vlan {{ vlan.id }}
 name {{ vlan.name }}
{% endfor %}
!
```

### Playbook Ansible

```yaml
---
- name: Déployer les VLAN
  hosts: switchs
  gather_facts: false
  vars_files:
    - vars/vlans.yml
  tasks:
    - name: Générer la configuration
      ansible.builtin.template:
        src: templates/vlans.j2
        dest: build/{{ inventory_hostname }}.cfg
      delegate_to: localhost

    - name: Appliquer les lignes VLAN
      cisco.ios.ios_config:
        src: build/{{ inventory_hostname }}.cfg
      register: result

    - name: Sauvegarder la configuration
      cisco.ios.ios_config:
        save_when: modified
      when: result.changed
```

### Script Netmiko équivalent

```python
from pathlib import Path
from netmiko import ConnectHandler

commands = [
    "vlan 10",
    "name Users",
    "vlan 20",
    "name Voice",
    "vlan 30",
    "name Guests",
]

device = {
    "device_type": "cisco_ios",
    "host": "192.168.1.10",
    "username": "automation",
    "use_keys": True,
    "key_file": "~/.ssh/id_ed25519",
}

with ConnectHandler(**device) as conn:
    conn.enable()
    before = conn.send_command("show running-config")
    Path("backup/sw1-before.cfg").write_text(before)
    output = conn.send_config_set(commands)
    print(output)
    print(conn.send_command("show vlan brief"))
```

Le script doit sauvegarder la configuration avant modification, vérifier le
résultat et conserver une trace. Pour un vrai rollback, on peut comparer la
configuration ou rejouer une sauvegarde validée.

### Validation après déploiement

- `show vlan brief` contient les VLAN attendus ;
- les ports sont dans le bon VLAN ;
- les trunks autorisent les VLAN nécessaires ;
- les voisins OSPF/STP sont stables ;
- aucune interface n'est passée en err-disabled ;
- les logs ne montrent pas d'erreur.

## 10. Sécurité de l'automatisation

- Ne jamais committer de mot de passe ou de clé privée.
- Utiliser un coffre-fort de secrets.
- Appliquer le moindre privilège.
- Journaliser les changements et l'identité de l'exécutant.
- Signer ou vérifier les artefacts.
- Limiter l'accès réseau aux API et aux équipements.
- Chiffrer les connexions.
- Prévoir une procédure de révocation des clés.

Un script qui possède un accès administrateur à tout le réseau est une cible de
choix. Il faut le traiter comme un composant critique.

## 11. Dépannage

### L'API renvoie 401

Le jeton est absent, expiré ou mal formé. Vérifier le header, l'horloge et la
portée du jeton.

### L'API renvoie 429

Trop de requêtes. Ajouter un backoff, réduire la concurrence ou utiliser une
API batch.

### Netmiko reste bloqué

Vérifier l'adresse, le port SSH, les identifiants, l'invite et la pagination.
Certains équipements demandent une commande `terminal length 0`.

### Ansible ne se connecte pas

Vérifier l'inventaire, `ansible_network_os`, l'utilisateur, la clé SSH et le
mode de connexion. Tester avec `ansible -m ping`.

### La configuration générée est incomplète

Vérifier les variables, les conditions Jinja2 et les valeurs par défaut. Un
`trim_blocks` mal réglé peut produire des lignes vides ou des blocs incorrects.

### Un changement a cassé le réseau

Appliquer le rollback prévu, restaurer la sauvegarde et analyser le diff. Ne
pas relancer le même playbook sans avoir compris l'erreur.

## 12. À retenir

- Une API REST utilise HTTP, des ressources et souvent du JSON.
- Les codes HTTP et les timeouts doivent être gérés.
- Netmiko simplifie les sessions SSH vers les équipements réseau.
- Ansible décrit l'état souhaité dans des playbooks YAML.
- Jinja2 génère des configurations à partir de données.
- Une source de vérité versionnée évite les configurations divergentes.
- Les secrets ne doivent jamais être dans le code ou Git.
- Une automatisation fiable inclut validation, sauvegarde et rollback.
- Tester sur un lab avant la production n'est pas une option.

L'automatisation ne remplace pas la connaissance du réseau. Elle rend les
opérations plus rapides et plus reproductibles lorsque les fondamentaux sont
compris et contrôlés.
