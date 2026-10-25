# Configuration avec Ansible

## 1. Positionnement dans le parcours DevOps

Ce cours correspond au niveau intermédiaire d’Ansible. Il part des bases de Linux, de SSH, de YAML, de Git et de l’automatisation, puis développe les pratiques nécessaires pour gérer plusieurs serveurs de manière reproductible, sécurisée et intégrée à une chaîne DevOps.

Il constitue une suite des cours consacrés à Git, à Docker, à Kubernetes, à la CI/CD avec GitHub Actions et GitLab CI, ainsi qu’à Terraform à grande échelle.

L’objectif n’est pas simplement de savoir lancer un playbook. Il est de construire une automatisation de configuration que l’on peut versionner, tester, réutiliser, auditer et exécuter dans différents environnements.

### 1.1. Place d’Ansible dans une architecture DevOps

Terraform et Ansible répondent à des besoins complémentaires.

- Terraform décrit et crée les ressources d’infrastructure : réseaux, machines virtuelles, adresses IP, pare-feu, volumes et autres ressources prises en charge par son fournisseur.
- Ansible configure les systèmes accessibles : utilisateurs, paquets, fichiers, services, règles système et applications installées sur les machines.
- Docker permet de construire et d’exécuter des applications dans des conteneurs.
- Kubernetes orchestre les applications conteneurisées au sein d’un cluster.
- Git conserve l’historique des changements.
- GitHub Actions ou GitLab CI exécutent les contrôles et les automatisations du pipeline.

Architecture logique :

```text
                         DÉPÔT GIT
                            |
          +-----------------+-----------------+
          |                 |                 |
      Terraform          Ansible          CI/CD
          |                 |                 |
          |                 |          Vérifications
          |                 |          Tests et règles
          |                 |          Autorisations
          |                 |                 |
          v                 v                 v
   Infrastructure ----> Configuration <--- Pipeline
   Réseau, VM, IP        des systèmes       automatisé
                            |
                  +---------+---------+
                  |                   |
                  v                   v
             Serveurs Linux      Hôtes techniques
             Web, API, BDD       Agents, outils
                  |
                  v
           Services configurés

   Applications conteneurisées et workloads Kubernetes :
   généralement déployés par des outils adaptés à Kubernetes,
   tels que Helm ou un mécanisme GitOps.
```

### 1.2. Exemple de chaîne complète

Supposons qu’une équipe doive déployer une API sur trois machines virtuelles Linux.

1. Terraform crée le réseau et les trois machines.
2. Les sorties Terraform fournissent les adresses des machines.
3. Ansible vérifie l’accès SSH.
4. Ansible installe les paquets nécessaires, crée les utilisateurs techniques et configure le service.
5. Ansible utilise des templates pour générer les fichiers de configuration.
6. Les tests et les contrôles vérifient le résultat.
7. Le pipeline valide les changements avant d’autoriser leur application en production.

Le découpage recommandé est le suivant :

```text
Terraform
   |
   | Machines créées, adresses disponibles
   v
Inventaire Ansible
   |
   | Hôtes et groupes
   v
Playbooks et rôles
   |
   | Configuration déclarative
   v
Serveurs configurés
   |
   | Contrôles et validations
   v
Service prêt à être utilisé
```

Il est important de ne pas faire d’Ansible un remplacement de Terraform, ni de transformer Terraform en outil de configuration quotidienne des logiciels installés sur les serveurs.

### 1.3. Compétences visées

À la fin du cours, il faut être capable de :

- construire un projet Ansible organisé ;
- administrer un inventaire comportant plusieurs environnements ;
- écrire des playbooks réutilisables et idempotents ;
- structurer la configuration avec les variables et les facts ;
- créer des rôles réutilisables ;
- gérer les templates, les handlers et les dépendances entre tâches ;
- protéger les secrets avec Ansible Vault et les mécanismes de gestion de secrets ;
- tester les changements avant leur application ;
- déployer progressivement une configuration sur plusieurs hôtes ;
- intégrer Ansible à GitHub Actions ou GitLab CI ;
- relier proprement les sorties d’une infrastructure Terraform à un inventaire Ansible ;
- diagnostiquer des erreurs d’inventaire, de connexion, de privilèges et d’exécution ;
- établir une séparation claire entre développement, recette et production.

## 2. Architecture d’Ansible

### 2.1. Fonctionnement sans agent

Dans une installation classique, Ansible est exécuté depuis une machine de contrôle. Il se connecte aux hôtes administrés, généralement par SSH pour les machines Linux.

```text
                     MACHINE DE CONTRÔLE
                     -------------------
                     Ansible installé
                     Inventaire
                     Playbooks
                     Rôles
                     Variables
                           |
              +------------+------------+
              |            |            |
             SSH          SSH          SSH
              |            |            |
              v            v            v
          Serveur 1    Serveur 2    Serveur 3
          Web          API          Base de données
```

La machine de contrôle peut être un poste d’administration, une machine dédiée ou un environnement d’exécution contrôlé dans un pipeline.

Ansible n’impose pas l’installation permanente d’un agent Ansible sur chaque serveur Linux administré. Il faut néanmoins disposer des prérequis nécessaires sur les hôtes cibles, notamment d’un interpréteur Python compatible pour de nombreux modules, ainsi que des droits nécessaires à l’opération demandée.

Les hôtes Windows suivent généralement un modèle de connexion différent, fréquemment basé sur WinRM ou PSRP selon l’environnement.

### 2.2. Les principaux composants

| Composant | Rôle |
|---|---|
| Inventaire | Décrit les hôtes et les groupes d’hôtes |
| Playbook | Décrit les opérations à appliquer |
| Play | Associe un ensemble de tâches à un groupe d’hôtes |
| Task | Décrit une opération précise |
| Module | Réalise une opération, par exemple installer un paquet |
| Variable | Paramètre la configuration |
| Fact | Information collectée depuis un hôte |
| Template | Fichier généré à partir de variables |
| Handler | Opération déclenchée lorsqu’une tâche signale un changement |
| Rôle | Organisation réutilisable des tâches, variables, templates et fichiers |
| Collection | Ensemble distribuable de rôles, de modules et d’autres éléments Ansible |
| Plugin | Étend certaines capacités d’Ansible : inventaire, connexion, filtre, callback, etc. |

### 2.3. La différence entre idempotence et exécution répétée

Une automatisation idempotente converge vers un état souhaité. Lorsque le système atteint cet état, la prochaine exécution ne devrait normalement pas modifier à nouveau les mêmes éléments.

Exemple :

```yaml
- name: Garantir que Nginx est installé
  become: true
  ansible.builtin.package:
    name: nginx
    state: present
```

Ce n’est pas la même chose qu’exécuter systématiquement :

```yaml
- name: Installer Nginx avec une commande brute
  become: true
  ansible.builtin.shell: apt-get install -y nginx
```

La seconde forme est moins descriptive et peut signaler un changement à chaque exécution. Elle peut également reproduire des effets de bord que le module dédié aurait évités.

Le principe général est le suivant :

```text
État observé
     |
     v
Comparaison à l'état souhaité
     |
     +---- État déjà conforme ----> Aucune modification
     |
     +---- État différent --------> Modification nécessaire
                                      |
                                      v
                               État souhaité atteint
```

L’idempotence ne signifie pas que toutes les opérations possibles sont sans danger. Un redémarrage, une migration de base de données ou une suppression peut toujours être risqué. Il faut distinguer convergence, réversibilité et sécurité opérationnelle.

## 3. Préparer l’environnement de travail

### 3.1. Installer Ansible dans un environnement Python isolé

Sur une machine Linux de contrôle disposant de Python et de `venv`, on peut créer un environnement dédié :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ansible
```

Vérifier l’installation :

```bash
ansible --version
ansible-playbook --version
ansible-galaxy --version
ansible-lint --version
```

Si `ansible-lint` n’est pas installé :

```bash
python -m pip install ansible-lint
```

La distribution `ansible` et le paquet `ansible-core` ne correspondent pas exactement au même ensemble de fonctionnalités. `ansible-core` fournit le moteur essentiel ; la distribution communautaire `ansible` peut comprendre des collections communautaires supplémentaires.

Pour un projet professionnel, il est important de contrôler les versions du moteur, de Python et des collections. Une mise à jour non testée peut changer le comportement ou rendre certains composants incompatibles.

Exemple de fichier de dépendances Python :

```text
ansible
ansible-lint
```

Ce fichier est adapté à une première démonstration, mais il ne constitue pas un verrouillage de versions reproductible. Dans un projet réel, fixer et tester les versions attendues.

Créer un environnement propre et vérifier les versions installées :

```bash
python -m pip freeze
```

### 3.2. Préparer l’accès SSH

Sur une machine de contrôle :

```bash
ssh-keygen -t ed25519 -C "ansible-control"
```

Cette commande génère une paire de clés. Utiliser une phrase secrète lorsqu’elle est appropriée au contexte opérationnel et protéger la clé privée.

Pour copier la clé publique sur un hôte compatible SSH :

```bash
ssh-copy-id deploy@192.0.2.21
```

Puis tester la connexion :

```bash
ssh deploy@192.0.2.21
```

L’adresse `192.0.2.21` appartient à un bloc d’adresses réservé à la documentation. La remplacer par l’adresse d’une machine réellement administrée.

Le compte utilisé doit avoir les permissions nécessaires. Lorsque les opérations nécessitent des droits élevés, Ansible peut utiliser l’escalade de privilèges avec `become`.

Ne jamais déposer une clé privée de production dans un dépôt Git simplement pour simplifier les tests.

### 3.3. Vérifier les prérequis

Avant le premier playbook, vérifier :

```bash
ansible --version
python3 --version
ssh -V
```

Vérifier également que :

- le réseau permet la connexion aux hôtes ;
- le nom DNS ou l’adresse IP est correct ;
- le compte SSH existe ;
- la clé est autorisée ;
- l’authenticité de la clé hôte SSH est vérifiée ;
- le compte dispose des droits nécessaires pour les tâches envisagées ;
- les composants Python nécessaires sont disponibles sur les cibles.

## 4. Organiser un projet Ansible

### 4.1. Structure recommandée

On ne doit pas transformer un dépôt intermédiaire en un ensemble de playbooks monolithiques. Il faut séparer les inventaires, la logique de configuration et les paramètres propres aux environnements.

Structure de départ :

```text
ansible-platform/
|
+-- ansible.cfg
+-- requirements.yml
+-- .gitignore
+-- README.md
|
+-- inventories/
|   +-- dev/
|   |   +-- hosts.yml
|   |   +-- group_vars/
|   |   +-- host_vars/
|   |
|   +-- staging/
|   |   +-- hosts.yml
|   |   +-- group_vars/
|   |   +-- host_vars/
|   |
|   +-- production/
|       +-- hosts.yml
|       +-- group_vars/
|       +-- host_vars/
|
+-- playbooks/
|   +-- site.yml
|   +-- configure_web.yml
|   +-- deploy_app.yml
|   +-- verify.yml
|
+-- roles/
|   +-- common/
|   +-- webserver/
|   +-- application/
|
+-- files/
|
+-- templates/
|
+-- tests/
```

Cette organisation est une convention de projet, pas une obligation imposée par Ansible. Des organisations plus simples ou plus complexes peuvent être pertinentes selon la taille du parc.

Éviter de dupliquer entièrement le playbook de production pour créer un playbook de recette. La logique devrait être partagée ; les différences entre les environnements doivent être principalement exprimées par les variables, les inventaires et les règles d’autorisation.

### 4.2. Fichier de configuration `ansible.cfg`

Le fichier `ansible.cfg` permet de centraliser les réglages du projet.

```ini
[defaults]
inventory = inventories/dev/hosts.yml
roles_path = roles
host_key_checking = True
retry_files_enabled = False
interpreter_python = auto_silent
```

Ce fichier est volontairement simple. Les options exactes et leur prise en charge peuvent dépendre de la version du moteur.

Points importants :

- `inventory` définit un inventaire par défaut pour ce projet.
- `roles_path` définit l’emplacement des rôles.
- `host_key_checking = True` conserve la vérification des identités SSH.
- `retry_files_enabled` n’est pas nécessaire dans toutes les versions modernes et les environnements d’exécution ; ne pas supposer que cette option constitue une exigence universelle.
- `interpreter_python` aide Ansible à choisir un interpréteur Python sur les hôtes lorsque la sélection automatique est disponible.

Un fichier de configuration local ne doit pas remplacer les contrôles de sécurité du système ou les règles de gestion des secrets.

Pour sélectionner explicitement un environnement, il reste possible d’utiliser :

```bash
ansible-playbook -i inventories/staging/hosts.yml playbooks/site.yml
```

### 4.3. Fichier `.gitignore`

```gitignore
.venv/
__pycache__/
*.pyc
*.retry
*.log
.vault-pass
.env
```

Ne pas s’appuyer uniquement sur `.gitignore` pour protéger les secrets. Un fichier déjà suivi par Git n’est pas automatiquement retiré du suivi lorsqu’une règle y est ajoutée.

Vérifier les fichiers suivis :

```bash
git status
git ls-files
```

Si un secret a été commité, sa suppression dans un nouveau commit ne garantit pas qu’il ait disparu de l’historique. Il faut considérer le secret comme potentiellement compromis, le révoquer ou le renouveler, puis traiter l’historique et les copies concernées.

## 5. Maîtriser les inventaires

L’inventaire définit les hôtes que l’automatisation peut cibler. Il représente la frontière entre la logique de configuration et les systèmes concernés.

### 5.1. Inventaire YAML

Fichier `inventories/dev/hosts.yml` :

```yaml
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 192.0.2.21
          ansible_user: deploy
        web02:
          ansible_host: 192.0.2.22
          ansible_user: deploy

    application:
      hosts:
        api01:
          ansible_host: 192.0.2.31
          ansible_user: deploy

    databases:
      hosts:
        db01:
          ansible_host: 192.0.2.41
          ansible_user: deploy
```

Les noms `web01`, `api01` et `db01` sont des alias d’inventaire. L’attribut `ansible_host` définit l’adresse utilisée pour joindre l’hôte.

Vérifier l’inventaire :

```bash
ansible-inventory -i inventories/dev/hosts.yml --list
ansible-inventory -i inventories/dev/hosts.yml --graph
```

Afficher la configuration fusionnée d’un hôte :

```bash
ansible-inventory \
  -i inventories/dev/hosts.yml \
  --host web01
```

### 5.2. Inventaire INI

Un inventaire INI reste adapté à de petits environnements :

```ini
[webservers]
web01 ansible_host=192.0.2.21 ansible_user=deploy
web02 ansible_host=192.0.2.22 ansible_user=deploy

[application]
api01 ansible_host=192.0.2.31 ansible_user=deploy

[databases]
db01 ansible_host=192.0.2.41 ansible_user=deploy
```

Pour les structures complexes, YAML rend souvent les données plus lisibles.

### 5.3. Utiliser les groupes d’hôtes

Les groupes permettent de sélectionner des cibles cohérentes.

Tester la connectivité à tous les serveurs web :

```bash
ansible webservers \
  -i inventories/dev/hosts.yml \
  -m ansible.builtin.ping
```

Tester un hôte :

```bash
ansible web01 \
  -i inventories/dev/hosts.yml \
  -m ansible.builtin.ping
```

Le module `ansible.builtin.ping` ne se contente pas d’envoyer une requête réseau ICMP. Il vérifie principalement la capacité d’Ansible à communiquer avec l’hôte et à exécuter le module sur la cible.

Sélectionner plusieurs groupes :

```bash
ansible 'webservers:application' \
  -i inventories/dev/hosts.yml \
  -m ansible.builtin.ping
```

Exclure un groupe :

```bash
ansible 'all:!databases' \
  -i inventories/dev/hosts.yml \
  -m ansible.builtin.ping
```

Toujours vérifier le périmètre avant une opération à impact élevé.

### 5.4. Séparer les variables communes et spécifiques

Créer `inventories/dev/group_vars/all.yml` :

```yaml
environment_name: development
timezone_name: Africa/Douala
managed_by_ansible: true
```

Créer `inventories/dev/group_vars/webservers.yml` :

```yaml
web_service_port: 80
web_document_root: /var/www/html
webserver_package: nginx
```

Créer `inventories/dev/host_vars/web01.yml` :

```yaml
monitoring_role: primary
```

Ces fichiers rendent les paramètres plus faciles à faire évoluer.

En général, conserver les valeurs communes dans les groupes communs, les valeurs de service dans les groupes concernés et les différences strictement propres à un hôte dans `host_vars`.

Ne pas multiplier les variables au niveau de chaque hôte si une simple règle de groupe suffit.

## 6. Comprendre les variables et leur priorité

### 6.1. Variables dans un playbook

```yaml
- name: Exemple avec des variables
  hosts: webservers
  gather_facts: false

  vars:
    webserver_package: nginx
    webserver_service: nginx

  tasks:
    - name: Installer le serveur Web
      become: true
      ansible.builtin.package:
        name: "{{ webserver_package }}"
        state: present

    - name: Démarrer le service Web
      become: true
      ansible.builtin.service:
        name: "{{ webserver_service }}"
        state: started
        enabled: true
```

Les expressions `{{ variable }}` permettent de substituer une valeur dans les champs appropriés.

Dans un YAML contenant une valeur qui commence par une expression Jinja, utiliser des guillemets :

```yaml
destination_path: "{{ base_path }}/config.yml"
```

### 6.2. Variables de type liste et dictionnaire

```yaml
application_packages:
  - ca-certificates
  - curl
  - jq

application_settings:
  name: inventory-api
  port: 8080
  log_level: info
```

Accéder à des éléments dans un template ou un playbook :

```yaml
- name: Installer les paquets requis
  become: true
  ansible.builtin.package:
    name: "{{ application_packages }}"
    state: present
```

Pour un dictionnaire, une notation explicite peut être utile :

```yaml
- name: Afficher le port applicatif
  ansible.builtin.debug:
    msg: "Port configuré : {{ application_settings['port'] }}"
```

### 6.3. Priorité des variables

Ansible dispose de plusieurs sources de variables : valeurs par défaut des rôles, fichiers de variables, inventaires, variables de playbook, variables passées en ligne de commande et autres sources.

Le détail de la priorité est plus complexe qu’une simple règle « la dernière valeur gagne ». La source exacte et la catégorie de variable déterminent le résultat.

Bonne pratique :

1. mettre les valeurs réutilisables et non spécifiques dans les valeurs par défaut du rôle ;
2. mettre les différences d’environnement dans `group_vars` ;
3. utiliser `host_vars` uniquement pour les exceptions propres à un hôte ;
4. passer des variables de ligne de commande pour un besoin ponctuel, sans bâtir toute l’architecture de configuration autour de `-e` ;
5. éviter de redéfinir la même variable dans de trop nombreux endroits.

Exemple de variable de rôle :

```yaml
# roles/webserver/defaults/main.yml
webserver_package: nginx
webserver_service: nginx
webserver_port: 80
webserver_document_root: /var/www/html
```

Ces valeurs par défaut sont destinées à être surchargées proprement par l’inventaire ou par un appelant du rôle.

### 6.4. Vérifier les variables lors de l’exécution

```yaml
- name: Vérifier les paramètres requis
  ansible.builtin.assert:
    that:
      - application_name is defined
      - application_port is defined
      - application_port | int > 0
      - application_port | int < 65536
    fail_msg: "Les paramètres de l'application sont absents ou invalides."
```

Cette approche échoue tôt lorsque les données nécessaires sont incorrectes.

Pour les variables sensibles ou susceptibles d’être absentes, choisir des validations adaptées. Ne pas remplacer silencieusement une variable obligatoire par une valeur arbitraire uniquement pour faire réussir l’exécution.

## 7. Écrire des playbooks maintenables

### 7.1. Anatomie d’un playbook

Un playbook contient un ou plusieurs plays. Un play détermine les hôtes ciblés et définit notamment les tâches à exécuter sur ces hôtes.

```yaml
- name: Configurer les serveurs Web
  hosts: webservers
  become: true
  gather_facts: true

  tasks:
    - name: Installer Nginx
      ansible.builtin.package:
        name: nginx
        state: present

    - name: Démarrer et activer Nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true
```

Exécution :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/configure_web.yml
```

### 7.2. Nommer clairement les tâches

Les noms des tâches doivent expliquer leur intention.

À éviter :

```yaml
- name: Tâche 1
  ansible.builtin.command: uptime
```

À préférer :

```yaml
- name: Vérifier la disponibilité des hôtes
  ansible.builtin.command:
    cmd: uptime
  changed_when: false
```

Une tâche correctement nommée facilite :

- l’analyse des journaux ;
- la compréhension des échecs ;
- la revue de code ;
- le débogage à distance ;
- la maintenance par une autre personne.

### 7.3. Choisir les modules appropriés

Préférer les modules dédiés plutôt qu’une commande shell lorsque c’est possible.

| Besoin | Module à privilégier |
|---|---|
| Installer un paquet | `ansible.builtin.package` |
| Gérer un service | `ansible.builtin.service` |
| Copier un fichier | `ansible.builtin.copy` |
| Générer un fichier à partir d’un template | `ansible.builtin.template` |
| Gérer un utilisateur | `ansible.builtin.user` |
| Gérer un groupe système | `ansible.builtin.group` |
| Gérer une tâche planifiée | `ansible.builtin.cron` |
| Exécuter une commande simple | `ansible.builtin.command` |
| Exécuter une commande avec les fonctions d’un shell | `ansible.builtin.shell` |
| Vérifier une condition | `ansible.builtin.assert` |
| Arrêter avec un message explicite | `ansible.builtin.fail` |
| Créer un répertoire | `ansible.builtin.file` |

`command` et `shell` ne sont pas équivalents. `shell` passe par un interpréteur de commandes et peut donc interpréter les redirections, les expansions et les opérateurs du shell. Il introduit aussi des risques supplémentaires lorsqu’il manipule des données non fiables.

Exemple avec `command` :

```yaml
- name: Contrôler la version de Python
  ansible.builtin.command:
    argv:
      - python3
      - --version
  register: python_version
  changed_when: false

- name: Afficher la version de Python
  ansible.builtin.debug:
    var: python_version.stdout
```

`argv` évite de construire une chaîne de commande susceptible d’être interprétée de façon inattendue.

Ne pas mettre `changed_when: false` sur une opération qui réalise de véritables changements : le statut rapporté par Ansible doit refléter le comportement de la tâche.

## 8. Facts, conditions et boucles

### 8.1. Collecter les facts

Les facts sont les informations qu’Ansible collecte depuis les hôtes, par exemple :

- famille de système d’exploitation ;
- version du système ;
- interfaces réseau ;
- adresses IP ;
- mémoire ;
- processeurs ;
- montages et volumes selon les facts disponibles.

Un playbook peut les afficher :

```yaml
- name: Examiner le système
  hosts: all
  gather_facts: true

  tasks:
    - name: Afficher la famille du système
      ansible.builtin.debug:
        var: ansible_facts['os_family']

    - name: Afficher la distribution
      ansible.builtin.debug:
        var: ansible_facts['distribution']
```

Pour limiter la collecte :

```yaml
- name: Vérification rapide
  hosts: all
  gather_facts: false

  tasks:
    - name: Vérifier la présence de la cible
      ansible.builtin.ping:
```

Le choix entre collecte complète et collecte réduite doit dépendre des informations dont le playbook a besoin.

### 8.2. Conditions avec `when`

Une condition peut utiliser une variable ou un fact.

```yaml
- name: Installer les outils d'administration Debian
  become: true
  ansible.builtin.package:
    name:
      - curl
      - ca-certificates
    state: present
  when: ansible_facts['os_family'] == 'Debian'
```

La condition `when` est une expression Jinja évaluée directement. Il ne faut pas entourer cette expression de `{{ }}`.

Un playbook peut également échouer lorsqu’un prérequis n’est pas respecté :

```yaml
- name: Exiger Linux pour ce playbook
  ansible.builtin.assert:
    that:
      - ansible_facts['system'] == 'Linux'
    fail_msg: "Ce playbook est réservé aux systèmes Linux."
```

L’assertion ne remplace pas une stratégie de compatibilité lorsque plusieurs familles Linux sont réellement prises en charge.

### 8.3. Boucles

```yaml
- name: Installer les outils utiles
  become: true
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop:
    - curl
    - jq
    - ca-certificates
```

Pour une liste de dictionnaires :

```yaml
application_users:
  - name: appdeploy
    shell: /bin/bash
  - name: monitoring
    shell: /usr/sbin/nologin
```

Playbook :

```yaml
- name: Créer les utilisateurs applicatifs
  become: true
  ansible.builtin.user:
    name: "{{ item.name }}"
    shell: "{{ item.shell }}"
    state: present
  loop: "{{ application_users }}"
```

Ne pas activer un shell interactif pour tous les comptes techniques sans raison. Les droits, les groupes et les possibilités de connexion doivent être adaptés au rôle de chaque compte.

### 8.4. Enregistrer le résultat d’une tâche

`register` permet de capturer le résultat d’une opération.

```yaml
- name: Tester une URL locale
  ansible.builtin.uri:
    url: http://127.0.0.1/
    method: GET
    status_code: 200
  register: web_response
  retries: 5
  delay: 2
  until: web_response.status == 200
```

Les mécanismes `retries`, `delay` et `until` peuvent servir à attendre la disponibilité d’un service.

Il faut cependant choisir un test pertinent. Une page HTTP qui renvoie `200` ne prouve pas nécessairement que toutes les dépendances de l’application sont fonctionnelles.

## 9. Templates Jinja2 et configuration système

### 9.1. Pourquoi les templates sont utiles

Copier le même fichier de configuration sur toutes les machines peut être inadapté si le port, l’environnement, l’adresse d’écoute ou le niveau de journalisation change.

Un template permet de séparer :

- la structure du fichier ;
- les paramètres spécifiques à l’environnement ;
- les règles de déploiement.

Créer `roles/webserver/templates/site.conf.j2` :

```nginx
server {
    listen {{ webserver_port }};
    server_name {{ webserver_server_name }};

    root {{ webserver_document_root }};
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Définir les variables :

```yaml
webserver_port: 80
webserver_server_name: example.internal
webserver_document_root: /var/www/html
```

Le nom de domaine donné est un exemple et doit être remplacé par celui de l’environnement concerné.

### 9.2. Déployer un template

```yaml
- name: Générer la configuration du site
  become: true
  ansible.builtin.template:
    src: site.conf.j2
    dest: /etc/nginx/sites-available/managed-site.conf
    owner: root
    group: root
    mode: "0644"
```

La tâche est idempotente : si le fichier rendu ne diffère pas de celui déjà en place, il n’est normalement pas réécrit.

### 9.3. Échapper et valider les données

Toutes les valeurs ne doivent pas être injectées aveuglément dans un fichier de configuration. Une variable contenant des caractères inattendus peut produire un fichier invalide ou, selon le format généré, un comportement dangereux.

Il faut :

1. valider les paramètres attendus ;
2. employer les filtres appropriés ;
3. rendre la configuration ;
4. vérifier sa syntaxe si l’application propose une commande de validation ;
5. recharger le service seulement après validation.

## 10. Handlers et redémarrages contrôlés

### 10.1. Problème des redémarrages inutiles

Un mauvais playbook redémarre systématiquement tous les services à chaque exécution. Cela peut interrompre des connexions, provoquer des indisponibilités et compliquer les déploiements.

Un handler permet de redémarrer ou recharger un service seulement lorsqu’une tâche ayant signalé un changement le demande.

```yaml
tasks:
  - name: Déployer la configuration Nginx
    become: true
    ansible.builtin.template:
      src: site.conf.j2
      dest: /etc/nginx/conf.d/managed-site.conf
      owner: root
      group: root
      mode: "0644"
    notify: Recharger Nginx

handlers:
  - name: Recharger Nginx
    become: true
    ansible.builtin.service:
      name: nginx
      state: reloaded
```

Les handlers sont exécutés à des moments contrôlés par Ansible, en général à la fin de la section de tâches concernée. Plusieurs notifications vers un même handler sont normalement regroupées pour qu’il ne soit exécuté qu’une fois pendant cette phase.

### 10.2. Valider avant le rechargement

Pour Nginx, on peut ajouter une validation :

```yaml
tasks:
  - name: Déployer la configuration Nginx
    become: true
    ansible.builtin.template:
      src: site.conf.j2
      dest: /etc/nginx/conf.d/managed-site.conf
      owner: root
      group: root
      mode: "0644"
      validate: "/usr/sbin/nginx -t -c %s"
    notify: Recharger Nginx

handlers:
  - name: Recharger Nginx
    become: true
    ansible.builtin.service:
      name: nginx
      state: reloaded
```

**Attention :** les chemins, les fichiers inclus, les arguments de validation et les emplacements de configuration peuvent différer selon le système et le paquet installé. Il faut adapter ce mécanisme à la configuration réelle de Nginx. Une commande de validation ciblant seulement un fichier isolé peut échouer si le fichier dépend d’autres éléments ou si le chemin de configuration n’est pas approprié.

Cette séquence illustre un principe plus général :

```text
Génération du fichier
        |
        v
Validation de syntaxe
        |
        +---- Échec ----> Déploiement bloqué
        |
        v
Fichier accepté
        |
        v
Notification du handler
        |
        v
Rechargement contrôlé
        |
        v
Vérification du service
```

### 10.3. Choisir entre redémarrer et recharger

- `restarted` demande un redémarrage du service.
- `reloaded` demande un rechargement de sa configuration.
- `started` garantit que le service est démarré.
- `stopped` demande que le service soit arrêté.

Le rechargement n’est pas pris en charge par tous les services. Il faut choisir un état compatible avec le service concerné et s’appuyer sur sa documentation.

## 11. Gérer les fichiers, les permissions et les utilisateurs

### 11.1. Créer un répertoire

```yaml
- name: Préparer le répertoire de l'application
  become: true
  ansible.builtin.file:
    path: /opt/inventory-api
    state: directory
    owner: appdeploy
    group: appdeploy
    mode: "0750"
```

Le compte `appdeploy` et le groupe correspondant doivent exister au préalable.

### 11.2. Copier un fichier

```yaml
- name: Installer un fichier de configuration statique
  become: true
  ansible.builtin.copy:
    src: application-defaults.yml
    dest: /etc/inventory-api/defaults.yml
    owner: root
    group: appdeploy
    mode: "0640"
```

Les fichiers sources des tâches `copy` sont généralement placés dans un répertoire `files/` de rôle, ou dans un emplacement explicite adapté à la structure du projet.

### 11.3. Créer un compte technique

```yaml
- name: Créer le compte d'exécution
  become: true
  ansible.builtin.user:
    name: appdeploy
    system: true
    create_home: false
    shell: /usr/sbin/nologin
    state: present
```

Un compte de service ne doit pas nécessairement pouvoir ouvrir une session interactive.

### 11.4. Définir les permissions sans ambiguïté

Les valeurs de permissions devraient être écrites sous forme de chaînes, par exemple `"0640"`, afin que YAML ne les interprète pas comme un nombre d’une autre base.

Pour chaque fichier sensible, décider :

- qui en est propriétaire ;
- quel groupe peut le lire ;
- qui peut le modifier ;
- si l’exécution est nécessaire ;
- si le fichier doit contenir des secrets ;
- si les permissions doivent être différentes dans un environnement particulier.

Ne pas se contenter de `mode: "0777"` pour éliminer un problème de permission : cela accorde trop de droits.

## 12. Structurer des rôles réutilisables

### 12.1. Pourquoi les rôles sont importants

Un playbook devient difficile à maintenir lorsque la même logique est répétée partout.

Un rôle fournit une unité de réutilisation qui peut contenir :

- des tâches ;
- des valeurs par défaut ;
- des variables ;
- des handlers ;
- des templates ;
- des fichiers ;
- des métadonnées et dépendances éventuelles.

Structure classique :

```text
roles/
+-- webserver/
    +-- defaults/
    |   +-- main.yml
    +-- files/
    +-- handlers/
    |   +-- main.yml
    +-- meta/
    |   +-- main.yml
    +-- tasks/
    |   +-- main.yml
    +-- templates/
        +-- site.conf.j2
```

Tous les répertoires ne sont pas obligatoires pour chaque rôle.

### 12.2. Créer un rôle

```bash
ansible-galaxy role init roles/webserver
```

La structure générée dépend des options et de la version d’Ansible Galaxy. Adapter les fichiers générés aux besoins du projet.

### 12.3. Exemple de rôle `webserver`

`roles/webserver/defaults/main.yml` :

```yaml
webserver_package: nginx
webserver_service: nginx
webserver_port: 80
webserver_server_name: localhost
webserver_document_root: /var/www/html
```

`roles/webserver/tasks/main.yml` :

```yaml
- name: Installer le serveur Web
  ansible.builtin.package:
    name: "{{ webserver_package }}"
    state: present

- name: Garantir que le service Web est actif
  ansible.builtin.service:
    name: "{{ webserver_service }}"
    state: started
    enabled: true
```

`roles/webserver/handlers/main.yml` :

```yaml
- name: Recharger Nginx
  ansible.builtin.service:
    name: "{{ webserver_service }}"
    state: reloaded
```

`roles/webserver/templates/site.conf.j2` :

```nginx
server {
    listen {{ webserver_port }};
    server_name {{ webserver_server_name }};
    root {{ webserver_document_root }};
    index index.html;
}
```

Cette première version illustre la structure du rôle. Pour la rendre pleinement opérationnelle, il faut intégrer à ses tâches la génération du fichier, la validation de la configuration, la notification du handler et les particularités propres au système cible.

### 12.4. Utiliser le rôle dans un playbook

`playbooks/configure_web.yml` :

```yaml
- name: Configurer les serveurs Web
  hosts: webservers
  become: true
  gather_facts: true

  roles:
    - role: webserver
```

Un rôle est généralement préférable à la duplication du même bloc de tâches dans plusieurs playbooks.

### 12.5. Séparer les rôles par responsabilité

Exemple :

```text
roles/
+-- common/
|   +-- Comptes et configuration système commune
|
+-- firewall/
|   +-- Règles de filtrage prises en charge
|
+-- webserver/
|   +-- Configuration du serveur Web
|
+-- application/
|   +-- Dépendances et déploiement de l'application
|
+-- monitoring_agent/
    +-- Installation et configuration de l'agent
```

Éviter de créer un rôle unique appelé `everything` qui modifie tous les aspects du système.

À l’inverse, ne pas créer un rôle distinct pour chaque tâche élémentaire lorsqu’il n’existe pas de responsabilité ou de besoin de réutilisation réel.

## 13. Collections et dépendances

### 13.1. Comprendre les collections

Ansible est extensible. Des fonctionnalités peuvent se trouver dans des collections, y compris des collections communautaires ou fournies par des éditeurs.

Les modules intégrés sont couramment préfixés par `ansible.builtin`, comme dans :

```yaml
ansible.builtin.copy
ansible.builtin.service
ansible.builtin.template
ansible.builtin.user
```

Employer le nom complet des modules favorise la lisibilité et évite les ambiguïtés entre collections.

### 13.2. Déclarer les dépendances d’une collection

Créer `requirements.yml` :

```yaml
collections:
  - name: community.general
```

Installer les dépendances :

```bash
ansible-galaxy collection install -r requirements.yml
```

Dans un projet d’équipe, ce fichier doit être versionné et les versions des collections utilisées en production doivent être contrôlées, testées et documentées.

Exemple avec une contrainte de version :

```yaml
collections:
  - name: community.general
    version: "X.Y.Z"
```

`X.Y.Z` est un marqueur d’exemple et doit être remplacé par une version réellement publiée, testée et compatible avec le moteur employé.

L’objectif n’est pas de choisir systématiquement la dernière version, mais de pouvoir reconstruire un environnement d’exécution fiable.

### 13.3. Rôles et collections

Un rôle correspond principalement à une unité de réutilisation de tâches et de données. Une collection peut regrouper plusieurs rôles, modules et autres composants partageables.

Pour un petit projet local, des rôles dans `roles/` suffisent souvent. Pour une organisation qui partage des automatisations entre plusieurs équipes et dépôts, une collection peut devenir plus adaptée.

## 14. Gestion des environnements : développement, recette, production

### 14.1. Le principe de promotion

Il vaut mieux promouvoir une même logique validée entre plusieurs environnements plutôt que maintenir trois versions du playbook.

```text
                    Dépôt Git
                        |
                        v
                Validation des règles
                        |
                        v
                Tests sur développement
                        |
                        v
                  Recette / Staging
                        |
                Validation explicite
                        |
                        v
                    Production
```

Chaque environnement peut utiliser son propre inventaire, ses variables et ses secrets.

Exemple :

`inventories/dev/group_vars/all.yml` :

```yaml
environment_name: development
application_log_level: debug
```

`inventories/staging/group_vars/all.yml` :

```yaml
environment_name: staging
application_log_level: info
```

`inventories/production/group_vars/all.yml` :

```yaml
environment_name: production
application_log_level: warning
```

Le niveau de journalisation est un exemple. Les valeurs réelles dépendent de l’application et des besoins de diagnostic.

### 14.2. Cibler explicitement l’environnement

Développement :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/site.yml
```

Recette :

```bash
ansible-playbook \
  -i inventories/staging/hosts.yml \
  playbooks/site.yml
```

Production :

```bash
ansible-playbook \
  -i inventories/production/hosts.yml \
  playbooks/site.yml
```

L’option `-i` est importante, même lorsque le projet dispose d’un inventaire par défaut. Elle rend le périmètre plus visible.

### 14.3. Limiter les hôtes d’une exécution

```bash
ansible-playbook \
  -i inventories/staging/hosts.yml \
  playbooks/site.yml \
  --limit web01
```

Cette option permet de cibler un sous-ensemble d’hôtes, mais ne garantit pas à elle seule qu’une opération soit sans risque.

Lors d’une opération en production, vérifier l’inventaire, les variables, le commit exécuté et le nombre de cibles avant de démarrer.

## 15. Contrôles avant application

### 15.1. Vérification syntaxique

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/site.yml \
  --syntax-check
```

Cette commande aide à détecter les erreurs de structure du playbook. Elle ne prouve pas que les hôtes sont accessibles, que les modules sont compatibles ou que les configurations générées sont correctes.

### 15.2. Mode de vérification

```bash
ansible-playbook \
  -i inventories/staging/hosts.yml \
  playbooks/site.yml \
  --check
```

Le mode `--check` permet d’estimer l’effet des changements sans appliquer la plupart des opérations prises en charge par le mode de vérification des modules.

Il ne faut pas le considérer comme une simulation complète. Certains modules ou certaines tâches ne prennent pas en charge correctement ce mode, et les tâches dépendantes de résultats produits pendant l’exécution peuvent se comporter différemment.

### 15.3. Afficher les différences

```bash
ansible-playbook \
  -i inventories/staging/hosts.yml \
  playbooks/site.yml \
  --check \
  --diff
```

`--diff` peut exposer des informations sensibles si un template contient des secrets. Ne pas publier sans contrôle les journaux du pipeline ou les sorties de cette commande.

Ne pas utiliser une simulation comme seule validation avant une modification risquée.

### 15.4. Limiter le périmètre

```bash
ansible-playbook \
  -i inventories/staging/hosts.yml \
  playbooks/site.yml \
  --limit webservers
```

Les balises constituent une autre façon de sélectionner des tâches. Elles ne remplacent pas le contrôle de l’inventaire.

### 15.5. Balises de tâches

```yaml
- name: Installer Nginx
  become: true
  ansible.builtin.package:
    name: nginx
    state: present
  tags:
    - packages
    - webserver
```

Exécuter seulement les tâches associées à une balise :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/site.yml \
  --tags webserver
```

Les balises peuvent compliquer le parcours réel des tâches lorsque des inclusions, des imports ou des dépendances entrent en jeu. Il faut les tester avant de s’en servir comme mécanisme principal de déploiement.

## 16. Maîtriser les privilèges avec `become`

### 16.1. Pourquoi `become` est nécessaire

L’installation de paquets, la modification de `/etc/` et la gestion des services nécessitent souvent des privilèges élevés.

Il est possible de définir `become: true` au niveau du play :

```yaml
- name: Configurer les serveurs
  hosts: webservers
  become: true

  tasks:
    - name: Installer Nginx
      ansible.builtin.package:
        name: nginx
        state: present
```

Ou de le définir sur une tâche spécifique :

```yaml
- name: Lire un fichier public
  ansible.builtin.command:
    argv:
      - cat
      - /etc/os-release
  changed_when: false

- name: Installer un paquet
  become: true
  ansible.builtin.package:
    name: curl
    state: present
```

Privilégier le périmètre minimal : toutes les tâches n’ont pas nécessairement besoin d’être exécutées avec les privilèges administratifs.

### 16.2. Utilisateur d’exécution et escalade

Le compte SSH utilisé pour se connecter n’est pas nécessairement celui qui exécute toutes les commandes. Avec `become`, Ansible peut demander une élévation de privilèges, souvent vers `root` sur Linux.

Si un mot de passe d’escalade est nécessaire :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/site.yml \
  --ask-become-pass
```

Ne pas écrire le mot de passe directement dans le playbook ou l’inventaire en clair.

Les droits sudo doivent être adaptés au rôle du compte, et les changements sensibles doivent être contrôlés selon les règles de l’organisation.

## 17. Gestion des secrets avec Ansible Vault

### 17.1. Ce que protège Vault

Ansible Vault chiffre des variables ou des fichiers. Il est utile pour empêcher que les secrets restent lisibles en clair dans le dépôt.

Il ne remplace pas la gestion des permissions, les politiques de rotation, le contrôle de sortie, ni un gestionnaire de secrets. Une fois déchiffré, un secret peut encore apparaître dans les journaux, les sorties de tâches ou certains fichiers temporaires si l’automatisation n’est pas conçue prudemment.

### 17.2. Créer un fichier chiffré

```bash
ansible-vault create inventories/production/group_vars/secrets.yml
```

Ansible ouvre un éditeur pour créer le fichier chiffré.

Contenu d’exemple :

```yaml
database_username: appuser
database_password: "REMPLACER_PAR_UN_SECRET_REEL"
```

La valeur illustrée n’est pas un véritable secret.

Pour exécuter le playbook avec une demande interactive du mot de passe Vault :

```bash
ansible-playbook \
  -i inventories/production/hosts.yml \
  playbooks/site.yml \
  --ask-vault-pass
```

### 17.3. Chiffrer un fichier existant

```bash
ansible-vault encrypt inventories/production/group_vars/secrets.yml
```

Afficher le contenu déchiffré dans un terminal autorisé :

```bash
ansible-vault view inventories/production/group_vars/secrets.yml
```

Modifier le fichier :

```bash
ansible-vault edit inventories/production/group_vars/secrets.yml
```

Réencrypter avec un nouveau mot de passe lorsque nécessaire :

```bash
ansible-vault rekey inventories/production/group_vars/secrets.yml
```

Les opérations disponibles doivent être employées selon le format du fichier et le mode de chiffrement choisi.

### 17.4. Chiffrer une seule variable

Exemple de commande :

```bash
ansible-vault encrypt_string \
  --name 'database_password' \
  --ask-vault-pass
```

La commande demande les informations nécessaires pour chiffrer la valeur. La valeur chiffrée produite peut ensuite être incorporée dans un fichier de variables.

Le chiffrement d’une variable et celui d’un fichier entier ont des avantages différents. Choisir le mode selon les besoins de lisibilité, de maintenance et de rotation des secrets.

### 17.5. Ne pas exposer les secrets dans les journaux

Une tâche manipulant un secret peut utiliser `no_log: true` :

```yaml
- name: Configurer la ressource applicative sensible
  ansible.builtin.debug:
    msg: "Cette tâche illustre le traitement d'une donnée sensible."
  no_log: true
```

Cet exemple montre l’emplacement de l’option ; dans un déploiement réel, utiliser un module qui réalise l’action voulue plutôt que `debug`.

`no_log: true` limite l’exposition de la sortie de la tâche concernée, mais ne rend pas automatiquement tous les secrets sûrs. Les messages personnalisés, les fichiers temporaires, les systèmes distants et d’autres tâches peuvent toujours exposer des valeurs.

### 17.6. Vault ou gestionnaire externe ?

Ansible Vault peut convenir aux secrets chiffrés versionnés dans un dépôt avec une gestion rigoureuse de la clé Vault.

Un gestionnaire externe peut être préférable lorsque l’organisation exige, par exemple :

- une rotation centralisée ;
- des accès temporaires ;
- des journaux d’accès ;
- une séparation des rôles d’administration ;
- une politique de secrets commune à plusieurs systèmes.

La clé de déchiffrement ne doit pas être commitée au même endroit que les fichiers chiffrés.

## 18. Contrôler les erreurs et assurer la reprise

### 18.1. Arrêter lorsque les prérequis échouent

```yaml
- name: Vérifier que le port demandé est valide
  ansible.builtin.assert:
    that:
      - webserver_port is defined
      - webserver_port | int >= 1
      - webserver_port | int <= 65535
    fail_msg: "Le port du serveur Web est invalide."
```

Une erreur de validation précoce est souvent préférable à un déploiement partiellement appliqué.

### 18.2. Utiliser `block`, `rescue` et `always`

Ces mécanismes permettent de regrouper une séquence d’actions, de définir un comportement de reprise et de prévoir une section d’exécution finale lorsque les tâches concernées échouent ou réussissent.

Exemple conceptuel :

```yaml
- name: Déployer et vérifier un service
  block:
    - name: Appliquer la configuration
      ansible.builtin.debug:
        msg: "Étape de configuration illustrative"

    - name: Vérifier le service
      ansible.builtin.assert:
        that:
          - service_expected_state == 'ready'

  rescue:
    - name: Signaler un échec de déploiement
      ansible.builtin.debug:
        msg: "La phase de déploiement a échoué."

  always:
    - name: Indiquer la fin de la séquence
      ansible.builtin.debug:
        msg: "Séquence terminée."
```

Il s’agit ici d’un exemple pédagogique, pas d’un mécanisme de rollback. Une section `rescue` qui affiche un message ne restaure pas l’état précédent.

Pour réaliser une véritable reprise, il faut définir les opérations de restauration, leurs prérequis, les risques de perte de données et les cas dans lesquels elles sont sûres.

### 18.3. Ne pas ignorer les erreurs par défaut

`ignore_errors: true` ou un `failed_when` mal conçu peut transformer une erreur importante en succès apparent.

Si un échec doit être considéré comme normal, documenter précisément pourquoi, limiter le périmètre de la tolérance et vérifier explicitement le résultat attendu.

### 18.4. Toujours prévoir une validation après le changement

Un playbook qui termine sans erreur n’est pas nécessairement la preuve que le service fonctionne comme attendu.

Pour un serveur Web, une vérification peut inclure :

- le statut du service ;
- le port en écoute ;
- une requête HTTP ;
- un test de l’endpoint de santé ;
- la disponibilité des dépendances nécessaires ;
- une vérification après le déploiement du nouveau contenu.

Exemple de test HTTP local :

```yaml
- name: Vérifier la réponse HTTP locale
  ansible.builtin.uri:
    url: http://127.0.0.1/
    method: GET
    status_code: 200
```

Cette vérification suppose que le service écoute bien sur l’URL indiquée. Adapter le protocole, le port, le chemin et les codes attendus à l’application réelle.

## 19. Déploiements progressifs sur plusieurs hôtes

### 19.1. Éviter une modification simultanée de tous les serveurs

Modifier tous les serveurs à la fois peut provoquer une interruption si le déploiement échoue sur chaque instance.

Le paramètre `serial` permet d’exécuter un play sur des lots d’hôtes.

```yaml
- name: Mettre à jour les serveurs Web progressivement
  hosts: webservers
  become: true
  serial: 1

  tasks:
    - name: Vérifier que le serveur cible est accessible
      ansible.builtin.ping:

    - name: Installer la configuration attendue
      ansible.builtin.debug:
        msg: "Déploiement illustratif sur un hôte à la fois."
```

L’exemple illustre uniquement le mécanisme de progression. La tâche `debug` n’est pas un déploiement opérationnel.

Pour un vrai déploiement, intégrer les étapes d’installation, de validation, de redémarrage ou de rechargement, puis vérifier que l’hôte est disponible avant de passer au lot suivant.

### 19.2. Déterminer la taille des lots

Par exemple :

```yaml
serial: 2
```

ou :

```yaml
serial: "25%"
```

Le pourcentage permet d’exprimer une taille relative à l’inventaire concerné. Le choix correct dépend du nombre d’instances, de la capacité restante et du besoin de disponibilité.

### 19.3. Stratégie opérationnelle

Une séquence de déploiement robuste suit habituellement cette logique :

```text
Prévalidation
     |
     v
Choix d'un premier lot
     |
     v
Application du changement
     |
     v
Validation technique
     |
     +---- Échec ----> Arrêt ou procédure de reprise
     |
     v
Validation fonctionnelle
     |
     +---- Échec ----> Arrêt ou procédure de reprise
     |
     v
Lot suivant
     |
     v
Vérification de l'ensemble du service
```

Ne pas confondre `serial` avec une garantie complète de disponibilité. Le trafic doit être géré correctement par l’équilibreur, les vérifications doivent être adaptées et la capacité du système doit permettre la réduction temporaire du nombre d’instances actives.

## 20. Relier Terraform et Ansible

### 20.1. Séparer le provisionnement de la configuration

Terraform peut produire les adresses des machines. Ansible consomme ensuite un inventaire contenant ces adresses.

```text
Terraform
   |
   | Crée les ressources
   | Produit les sorties utiles
   v
Sorties Terraform
   |
   | Traitement et validation
   v
Inventaire Ansible
   |
   | Connexion et configuration
   v
Serveurs prêts
```

L’objectif est d’éviter les adresses IP copiées manuellement dans plusieurs endroits et les configurations divergentes entre Terraform et Ansible.

### 20.2. Déclarer des sorties Terraform

Exemple côté Terraform :

```hcl
output "web_server_ips" {
  description = "Adresses IP des serveurs Web"
  value       = [for instance in example_compute_instance.web : instance.ip_address]
}
```

`example_compute_instance` est ici un nom fictif de ressource. Le type réel de ressource et l’attribut qui contient l’adresse dépendent du fournisseur et du module utilisés.

Pour l’exemple, supposons que `web_server_ips` expose une liste d’adresses IP valide.

Après la création de l’infrastructure, cette commande affiche la sortie :

```bash
terraform output -json web_server_ips
```

Elle renvoie une structure JSON adaptée à la sortie déclarée.

Ne pas traiter une sortie Terraform comme une source fiable sans validation : son type, son contenu, ses éventuelles valeurs sensibles et sa correspondance avec les machines attendues doivent être contrôlés.

### 20.3. Générer un inventaire avec Python

Une possibilité consiste à lire la sortie JSON et à générer un inventaire YAML. Cet exemple suppose que `terraform output -json web_server_ips` renvoie une liste de chaînes représentant les adresses à administrer.

Créer `scripts/generate_inventory.py` :

```python
#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    try:
        result = subprocess.run(
            ["terraform", "output", "-json", "web_server_ips"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(
            "Impossible de lire la sortie Terraform.",
            file=sys.stderr,
        )
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("Terraform n'est pas installé ou absent du PATH.", file=sys.stderr)
        return 1

    try:
        addresses = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("La sortie Terraform n'est pas un JSON valide.", file=sys.stderr)
        return 1

    if not isinstance(addresses, list) or not addresses:
        print("La liste des adresses est vide ou invalide.", file=sys.stderr)
        return 1

    if not all(isinstance(address, str) and address.strip() for address in addresses):
        print("Une adresse est vide ou n'est pas une chaîne.", file=sys.stderr)
        return 1

    lines = [
        "all:",
        "  children:",
        "    webservers:",
        "      hosts:",
    ]

    for index, address in enumerate(addresses, start=1):
        if any(char.isspace() for char in address):
            print(f"Adresse invalide : {address!r}", file=sys.stderr)
            return 1

        lines.extend(
            [
                f"        web{index:02d}:",
                f"          ansible_host: {json.dumps(address)}",
                "          ansible_user: deploy",
            ]
        )

    output_path = Path("inventories/generated/hosts.yml")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Inventaire généré : {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Exécuter ce script depuis le répertoire contenant le state Terraform concerné :

```bash
python scripts/generate_inventory.py
```

Puis vérifier le résultat :

```bash
ansible-inventory \
  -i inventories/generated/hosts.yml \
  --graph
```

Ce script est une base pédagogique. En production, il faut aussi valider les formats d’adresses autorisés, les environnements, les noms d’hôtes et la provenance du state. Si une sortie est sensible, elle doit être manipulée selon les règles de protection des données du projet.

### 20.4. Quand préférer un inventaire dynamique ?

Pour un parc changeant ou important, un inventaire dynamique peut être préférable à la génération d’un fichier statique.

Un plugin d’inventaire adapté au fournisseur peut permettre de découvrir les machines à partir de leur état réel dans la plateforme.

Le choix dépend de la fréquence des changements, du fournisseur, du modèle d’authentification, des permissions et du besoin de reproduire exactement un périmètre de déploiement.

La présence d’un inventaire dynamique ne dispense pas de contrôler l’environnement et la sélection des hôtes avant l’exécution.

### 20.5. Éviter le couplage entre deux états de vérité

Terraform et Ansible ne doivent pas devenir deux systèmes concurrents qui définissent les mêmes propriétés.

Exemples de responsabilités distinctes :

| Terraform | Ansible |
|---|---|
| Créer une machine virtuelle | Installer les paquets sur la machine |
| Créer un réseau | Configurer un service sur les hôtes |
| Affecter une ressource à un réseau | Déployer un fichier de configuration système |
| Définir les paramètres d’une machine | Gérer un compte technique sur le système |
| Créer une règle réseau côté plateforme | Configurer un service local lorsque cela est approprié |

Une règle réseau dans le cloud et un pare-feu local peuvent traiter des niveaux différents de la sécurité. Il faut les concevoir ensemble, sans les confondre.

## 21. Intégration à une chaîne CI/CD

### 21.1. Rôle du pipeline

Le pipeline ne doit pas exécuter aveuglément toutes les opérations à chaque commit. Il doit séparer les contrôles sans effet de bord des opérations qui modifient réellement les infrastructures.

Une chaîne typique :

```text
Pull request / Merge request
            |
            v
Vérification du YAML et de la syntaxe
            |
            v
ansible-lint
            |
            v
Tests du playbook ou du rôle
            |
            v
Revue et fusion
            |
            v
Déploiement en recette
            |
            v
Validation et approbation requise
            |
            v
Déploiement en production
            |
            v
Tests et traces d'exécution
```

Les contrôles de qualité peuvent être automatisés à chaque changement. Les déploiements de production nécessitent généralement une politique distincte, incluant les approbations et permissions adaptées.

### 21.2. Pipeline GitHub Actions : contrôles de base

Exemple de fichier `.github/workflows/ansible-checks.yml` :

```yaml
name: Ansible checks

on:
  pull_request:
    paths:
      - "ansible/**"
      - ".github/workflows/ansible-checks.yml"
  push:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest

    defaults:
      run:
        working-directory: ansible

    steps:
      - name: Checkout du dépôt
        uses: actions/checkout@v4

      - name: Installer Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - name: Installer les dépendances de validation
        run: |
          python -m pip install --upgrade pip
          python -m pip install ansible ansible-lint

      - name: Installer les collections du projet
        run: ansible-galaxy collection install -r requirements.yml

      - name: Vérifier la syntaxe
        run: |
          ansible-playbook \
            -i inventories/dev/hosts.yml \
            playbooks/site.yml \
            --syntax-check

      - name: Vérifier les règles de qualité
        run: ansible-lint
```

Cet exemple suppose que le répertoire `ansible/` contient les fichiers concernés. Si le dépôt place le projet Ansible à la racine, adapter `working-directory` et les chemins.

Les actions externes doivent être contrôlées, maintenues et, dans un environnement à exigences de sécurité élevées, référencées par un identifiant de commit immuable plutôt que par un tag mobile.

### 21.3. Pipeline GitLab CI : contrôles de base

Exemple de `.gitlab-ci.yml` :

```yaml
stages:
  - validate

ansible_syntax:
  stage: validate
  image: python:3-slim
  before_script:
    - python -m pip install --upgrade pip
    - python -m pip install ansible ansible-lint
    - cd ansible
    - ansible-galaxy collection install -r requirements.yml
  script:
    - ansible-playbook -i inventories/dev/hosts.yml playbooks/site.yml --syntax-check
    - ansible-lint
```

Cet exemple suppose que le projet Ansible se trouve dans le sous-répertoire `ansible/`.

Dans un dépôt réel, il est conseillé de fixer ou contrôler les versions des dépendances et de s’assurer que l’image du pipeline contient les prérequis requis.

### 21.4. Éviter les déploiements automatiques non contrôlés

Un pipeline de validation ne devrait pas disposer automatiquement de droits d’administration sur la production.

Pour les opérations de déploiement :

- séparer les jobs de contrôle et les jobs de déploiement ;
- utiliser des environnements protégés et des mécanismes d’approbation ;
- limiter les permissions des identités du pipeline ;
- ne fournir les secrets qu’aux jobs qui en ont réellement besoin ;
- éviter de rendre les clés de production accessibles aux pipelines issus de branches non fiables ;
- conserver les traces nécessaires sans exposer les secrets ;
- contrôler le commit et l’inventaire utilisés pour le déploiement.

### 21.5. Reproduire l’exécution localement

Les mêmes contrôles doivent pouvoir être exécutés par un développeur ou un administrateur :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/site.yml \
  --syntax-check

ansible-lint
```

Cette cohérence réduit les problèmes où une configuration passe en local mais échoue dans l’image de pipeline.

Le pipeline doit vérifier un comportement reproductible. Il ne doit pas devenir l’unique endroit où les règles de qualité sont définies.

## 22. Tests et qualité du code Ansible

### 22.1. Niveaux de test

On peut distinguer quatre niveaux :

| Niveau | Objectif |
|---|---|
| Syntaxe | Vérifier que le playbook peut être analysé |
| Qualité statique | Détecter les problèmes de pratiques et de style |
| Test de rôle | Exécuter les automatisations dans un environnement contrôlé |
| Validation fonctionnelle | Confirmer que le service final fonctionne |

Un playbook valide en YAML peut encore contenir des erreurs de logique, des noms de variables incorrects ou un module inadéquat.

### 22.2. Utiliser ansible-lint

```bash
ansible-lint
```

`ansible-lint` examine les playbooks, les rôles et les conventions prises en charge par sa version et sa configuration.

Il peut identifier certains risques, des constructions déconseillées et des problèmes de maintenabilité.

Il ne remplace pas une revue de code ni la validation de l’application cible. Il faut traiter les avertissements selon leur gravité, et ne pas neutraliser globalement les règles juste pour obtenir un pipeline vert.

### 22.3. Tests des rôles avec Molecule

Molecule est un outil couramment employé pour développer et tester des rôles Ansible dans un environnement contrôlé. Sa configuration dépend des versions retenues et du pilote choisi.

Une démarche de test peut suivre ce modèle :

```text
Création de l'environnement de test
              |
              v
Application du rôle
              |
              v
Validation de l'état configuré
              |
              v
Deuxième application du rôle
              |
              v
Vérification de l'idempotence
              |
              v
Nettoyage de l'environnement
```

Les mécanismes précis, commandes et dépendances nécessaires doivent être vérifiés dans la documentation correspondant à la version de Molecule et du pilote retenus. Éviter de copier un ancien exemple de configuration sans vérifier sa compatibilité.

### 22.4. Tester l'idempotence

Une méthode manuelle consiste à exécuter deux fois le même playbook dans un environnement de test.

Premier passage :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/site.yml
```

Second passage :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/site.yml
```

Le second passage ne devrait plus afficher de changements pour les tâches qui gèrent correctement l’état souhaité. Les tâches comportant volontairement des opérations non idempotentes ou des vérifications dynamiques doivent être analysées séparément.

Une variation de `changed` ne signifie pas systématiquement une panne, mais une modification récurrente inattendue mérite d’être étudiée.

## 23. Diagnostiquer les problèmes fréquents

### 23.1. Hôte inaccessible

Symptômes :

```text
UNREACHABLE
Failed to connect to the host via ssh
```

Contrôles :

```bash
ssh deploy@ADRESSE_DE_LA_CIBLE
```

Puis :

```bash
ansible web01 \
  -i inventories/dev/hosts.yml \
  -m ansible.builtin.ping \
  -vvv
```

Vérifier le routage, le pare-feu, le port SSH, le compte, la clé utilisée, l’authentification et la clé hôte SSH.

La verbosité élevée peut révéler des détails sensibles ; protéger les sorties de diagnostic.

### 23.2. Erreur de privilèges

Symptômes :

```text
Permission denied
Missing sudo password
```

Contrôler :

- si `become: true` est placé au bon niveau ;
- si le compte peut utiliser `sudo` ;
- si une demande interactive est nécessaire ;
- si la politique du serveur autorise l’élévation demandée ;
- si le mot de passe ou le mécanisme d’élévation utilisé correspond à la cible.

### 23.3. Module absent ou collection manquante

Contrôler les collections disponibles :

```bash
ansible-galaxy collection list
```

Vérifier le nom complet du module et les dépendances du projet. Installer la collection manquante dans l’environnement prévu.

### 23.4. Erreur YAML

Causes fréquentes :

- indentation incohérente ;
- mauvais type de guillemets ;
- expression Jinja mal écrite ;
- deux-points interprétés comme un élément de structure ;
- liste ou dictionnaire mal formé.

Utiliser un éditeur qui signale les erreurs YAML, puis lancer :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/site.yml \
  --syntax-check
```

Le contrôle syntaxique Ansible n’élimine pas toutes les erreurs qui peuvent se produire pendant l’exécution.

### 23.5. Un fichier change à chaque exécution

Rechercher :

- un contenu dynamique différent à chaque passage ;
- des espaces ou fins de ligne modifiés ;
- des valeurs de variables instables ;
- un usage trop large de `shell` ou `command` ;
- des timestamps générés dans les templates ;
- des permissions non déclarées ou modifiées par une autre automatisation.

### 23.6. Le service redémarre trop souvent

Examiner :

- les tâches `template` et `copy` ;
- les handlers et leurs notifications ;
- les valeurs rendues ;
- les différences réelles du fichier ;
- les tâches qui changent artificiellement leur état.

L’objectif est de déclencher le redémarrage seulement lorsqu’un changement validé le justifie.

## 24. Ansible et Kubernetes : délimiter les responsabilités

Le parcours précédent comprenait Kubernetes. Il est important de ne pas réintroduire une configuration manuelle de tous les workloads Kubernetes par Ansible si les ressources sont déjà gérées par un contrôleur de déploiement, Helm ou GitOps.

### 24.1. Les usages complémentaires

| Besoin | Outil généralement adapté |
|---|---|
| Créer les machines virtuelles | Terraform ou outil de provisionnement adapté |
| Configurer le système d'exploitation des machines | Ansible |
| Installer certains prérequis de nœuds, lorsque c'est l'approche retenue | Ansible ou outil de bootstrap adapté |
| Construire une image applicative | Docker/BuildKit ou outil de build adapté |
| Déployer des ressources Kubernetes | API Kubernetes, Helm, GitOps ou outils adaptés |
| Vérifier les tests avant fusion | CI/CD |
| Promouvoir les changements d'application | Pipeline et/ou GitOps selon l'architecture |

### 24.2. Exemple de responsabilités

```text
Terraform
   |
   v
Machines et réseau du cluster
   |
   v
Ansible
   |
   v
Configuration système et prérequis
   |
   v
Cluster Kubernetes opérationnel
   |
   v
Helm / GitOps / API Kubernetes
   |
   v
Applications Kubernetes
```

Le processus réel dépend de la plateforme et des outils de gestion du cycle de vie Kubernetes.

Ansible peut administrer certains éléments d’un cluster, mais il faut décider quelle source de vérité pilote les ressources Kubernetes. Éviter que deux systèmes différents modifient la même ressource sans coordination claire.

## 25. Bonnes pratiques d'équipe

### 25.1. Règles de conception

- Utiliser des modules dédiés lorsque c’est possible.
- Préférer des rôles avec une responsabilité clairement définie.
- Déclarer les variables et leurs valeurs par défaut.
- Valider les entrées importantes.
- Garder les secrets hors du code en clair.
- Prévoir des handlers pour les changements de configuration qui le nécessitent.
- Tester l’idempotence.
- Contrôler explicitement l’inventaire et l’environnement.
- Valider les configurations avant un rechargement ou un redémarrage.
- Garder les changements petits et examinables dans Git.

### 25.2. Règles de déploiement

Avant une application à impact élevé :

1. contrôler le commit utilisé ;
2. valider l’inventaire ;
3. vérifier les variables et les secrets nécessaires ;
4. lancer les contrôles syntaxiques et statiques ;
5. examiner les changements prévisibles ;
6. démarrer avec un périmètre réduit lorsque c’est approprié ;
7. vérifier le résultat sur les systèmes cibles ;
8. conserver les traces d’exécution ;
9. disposer d’un plan de reprise proportionné au risque.

### 25.3. Gouvernance des secrets

La protection des secrets doit faire partie des choix de conception du dépôt et du pipeline.

Les secrets de production ne doivent pas être accessibles aux workflows non fiables. L’utilisation de Vault ne dispense pas de limiter les permissions des identités qui peuvent déchiffrer les fichiers.

Le même principe s’applique aux identifiants cloud utilisés par Terraform et aux informations d’authentification SSH d’Ansible.

### 25.4. Documentation du dépôt

Le README du projet devrait expliquer :

- les prérequis et versions ;
- la structure du projet ;
- l’installation des dépendances ;
- les inventaires disponibles ;
- la sélection d’un environnement ;
- les commandes de validation ;
- la procédure de déploiement ;
- les mécanismes de gestion des secrets ;
- la procédure de diagnostic ;
- les risques d’exploitation et la méthode de reprise.

Ne pas y inclure de secret, même temporaire ou présenté comme un exemple réel.

## 26. Travaux pratiques guidés

Les travaux pratiques utilisent des machines de laboratoire autorisées. Les adresses IP d’exemple ne doivent pas être reprises sans adaptation.

### TP 1 — Créer un inventaire et vérifier les connexions

Objectif : vérifier qu’Ansible peut joindre deux hôtes de laboratoire.

Créer :

```text
inventories/dev/hosts.yml
```

Contenu :

```yaml
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 192.0.2.21
          ansible_user: deploy
        web02:
          ansible_host: 192.0.2.22
          ansible_user: deploy
```

Vérifier :

```bash
ansible-inventory \
  -i inventories/dev/hosts.yml \
  --graph
```

Tester :

```bash
ansible webservers \
  -i inventories/dev/hosts.yml \
  -m ansible.builtin.ping
```

Résultat attendu : les deux hôtes apparaissent dans le groupe et répondent au test Ansible si les accès SSH et prérequis sont correctement configurés.

En cas d’échec, corriger l’accès SSH avant d’écrire des playbooks plus complexes.

### TP 2 — Installer un serveur Web

Objectif : utiliser un playbook simple pour garantir la présence et le démarrage du service.

Créer `playbooks/configure_web.yml` :

```yaml
- name: Installer et démarrer Nginx
  hosts: webservers
  become: true
  gather_facts: true

  tasks:
    - name: Vérifier que la cible utilise Linux
      ansible.builtin.assert:
        that:
          - ansible_facts['system'] == 'Linux'
        fail_msg: "Le laboratoire attend un système Linux."

    - name: Installer Nginx
      ansible.builtin.package:
        name: nginx
        state: present

    - name: Activer et démarrer Nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true
```

Exécution :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/configure_web.yml \
  --syntax-check
```

Puis appliquer dans le laboratoire :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/configure_web.yml
```

La disponibilité du paquet Nginx, les privilèges et le système de paquets doivent être compatibles avec les hôtes cibles.

### TP 3 — Configurer une page via un template

Objectif : générer une page différente selon l’environnement.

Créer `roles/webserver/defaults/main.yml` :

```yaml
webserver_document_root: /var/www/html
environment_name: development
application_name: inventory-api
```

Créer `roles/webserver/templates/index.html.j2` :

```html
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ application_name }}</title>
</head>
<body>
  <h1>{{ application_name }}</h1>
  <p>Environnement : {{ environment_name }}</p>
  <p>Cette page est gérée par Ansible.</p>
</body>
</html>
```

Créer une tâche :

```yaml
- name: Déployer la page de test
  become: true
  ansible.builtin.template:
    src: index.html.j2
    dest: "{{ webserver_document_root }}/index.html"
    owner: root
    group: root
    mode: "0644"
```

Intégrer la tâche au rôle ou au playbook de configuration, puis vérifier la page avec une requête HTTP depuis l’environnement approprié.

Changer la variable `environment_name` dans un inventaire de test et vérifier que le contenu rendu reflète le nouvel environnement.

### TP 4 — Ajouter un handler

Objectif : recharger un service uniquement après une modification de configuration.

Créer un template de configuration adapté au serveur Web du laboratoire.

La tâche doit :

- générer le fichier ;
- définir son propriétaire et ses permissions ;
- valider la configuration si la commande appropriée est disponible ;
- notifier un handler de rechargement.

Exemple de structure :

```yaml
tasks:
  - name: Déployer la configuration du service
    become: true
    ansible.builtin.template:
      src: site.conf.j2
      dest: /etc/nginx/conf.d/managed-site.conf
      owner: root
      group: root
      mode: "0644"
    notify: Recharger le service Web

handlers:
  - name: Recharger le service Web
    become: true
    ansible.builtin.service:
      name: nginx
      state: reloaded
```

Avant l’exécution, vérifier que le fichier de destination, le chemin de configuration et le mécanisme de chargement correspondent au système réel. Pour terminer ce TP, ajouter une validation adaptée et confirmer que le handler s’exécute seulement après une modification effective.

### TP 5 — Protéger un secret

Objectif : déplacer un secret de test dans un fichier chiffré.

Créer :

```bash
ansible-vault create inventories/dev/group_vars/secrets.yml
```

Ajouter dans l’éditeur :

```yaml
lab_api_token: "SECRET_DE_TEST_A_REMPLACER"
```

Puis intégrer la variable dans le playbook sans l’afficher.

Lancer le playbook avec la demande du mot de passe Vault :

```bash
ansible-playbook \
  -i inventories/dev/hosts.yml \
  playbooks/site.yml \
  --ask-vault-pass
```

Vérifier le dépôt avec :

```bash
git status
git diff --staged
```

S’assurer que le fichier chiffré est versionné lorsque cela est prévu par la politique du projet, et qu’aucun fichier contenant le mot de passe Vault ou le secret en clair n’est ajouté au dépôt.

## 27. Exercices corrigés

### Exercice 1 — Choisir le module approprié

Pour chaque besoin, identifier le module Ansible adapté.

1. Installer `curl`.
2. Copier un fichier statique vers `/etc/app/defaults.yml`.
3. Créer un répertoire appartenant à un compte de service.
4. Générer un fichier à partir d’un template.
5. Activer un service au démarrage.
6. Vérifier qu’un port est compris entre 1 et 65535.

**Correction :**

1. `ansible.builtin.package`
2. `ansible.builtin.copy`
3. `ansible.builtin.file`
4. `ansible.builtin.template`
5. `ansible.builtin.service` avec `enabled: true`
6. `ansible.builtin.assert` avec une expression qui contrôle la valeur et ses bornes.

### Exercice 2 — Corriger un playbook trop imprécis

Le playbook suivant installe Nginx à l’aide d’une commande shell :

```yaml
- name: Configuration
  hosts: webservers

  tasks:
    - name: Installer le service
      ansible.builtin.shell: apt-get install -y nginx
```

**Problèmes :**

- il ne déclare pas l’escalade de privilèges ;
- il dépend directement de la commande `apt-get` ;
- il décrit mal l’état désiré ;
- il ne garantit pas que le service est démarré ou activé ;
- le nom de tâche est trop vague.

**Correction :**

```yaml
- name: Configurer Nginx
  hosts: webservers
  become: true

  tasks:
    - name: Installer Nginx
      ansible.builtin.package:
        name: nginx
        state: present

    - name: Démarrer et activer Nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true
```

Cette correction est plus déclarative et convient à de nombreux systèmes Linux, sous réserve de la disponibilité du paquet et du service sous les noms retenus.

### Exercice 3 — Déterminer pourquoi une tâche est ignorée

Playbook :

```yaml
- name: Configurer l'hôte
  hosts: webservers
  gather_facts: false

  tasks:
    - name: Installer le paquet
      become: true
      ansible.builtin.package:
        name: curl
        state: present
      when: ansible_facts['os_family'] == 'Debian'
```

**Problème :**

Les facts sont désactivés, mais la condition dépend de `ansible_facts['os_family']`. Cette donnée peut ne pas être disponible.

**Correction :**

```yaml
- name: Configurer l'hôte
  hosts: webservers
  gather_facts: true

  tasks:
    - name: Installer le paquet sur la famille Debian
      become: true
      ansible.builtin.package:
        name: curl
        state: present
      when: ansible_facts['os_family'] == 'Debian'
```

On pourrait également collecter explicitement les facts nécessaires d’une manière adaptée au projet. Le point essentiel est de ne pas désactiver une collecte dont une tâche dépend ensuite.

### Exercice 4 — Empêcher un redémarrage systématique

Une équipe utilise :

```yaml
- name: Redémarrer le serveur Web
  become: true
  ansible.builtin.service:
    name: nginx
    state: restarted
```

Cette tâche s’exécute systématiquement et peut provoquer des interruptions inutiles.

**Correction attendue :**

Associer un handler à la tâche qui modifie réellement la configuration.

```yaml
tasks:
  - name: Déployer la configuration
    become: true
    ansible.builtin.template:
      src: site.conf.j2
      dest: /etc/nginx/conf.d/managed-site.conf
      owner: root
      group: root
      mode: "0644"
    notify: Recharger Nginx

handlers:
  - name: Recharger Nginx
    become: true
    ansible.builtin.service:
      name: nginx
      state: reloaded
```

Il reste nécessaire de valider la configuration et d’adapter le chemin au système cible.

### Exercice 5 — Sécuriser un pipeline

Un pipeline CI/CD détient une clé SSH de production et l’utilise pour tous les pipelines de branches, y compris les branches soumises par des contributeurs externes.

**Correction attendue :**

- ne pas exposer les identifiants de production aux pipelines non fiables ;
- séparer validation et déploiement ;
- protéger l’environnement de production ;
- limiter les permissions du compte d’automatisation ;
- exiger les approbations nécessaires ;
- vérifier l’origine du commit avant toute action sensible ;
- conserver des journaux sans secrets ;
- privilégier les identités et mécanismes d’accès temporaires lorsqu’ils sont disponibles.

Le chiffrement d’un fichier Ansible ne suffit pas si un workflow non fiable peut obtenir la clé de déchiffrement.

## 28. Projet final — Configurer une plateforme Web avec Terraform et Ansible

### 28.1. Objectif

Créer un projet qui reprend les compétences du parcours DevOps et établit une séparation de responsabilités claire entre infrastructure, configuration, validation et déploiement.

Le projet doit configurer un ensemble de serveurs Web à partir d’une infrastructure déjà provisionnée par Terraform.

### 28.2. Architecture cible

```text
                         Git
                          |
            +-------------+-------------+
            |                           |
            v                           v
        Terraform                    Ansible
            |                           |
            v                           v
   Réseau et machines            Configuration système
            |                           |
            +-------------+-------------+
                          |
                          v
                  Serveurs disponibles
                          |
                          v
                   Tests de validation
                          |
                          v
                 Pipeline CI/CD contrôlé
```

Le projet ne doit pas recréer l’infrastructure à chaque lancement du playbook. Terraform et Ansible conservent des responsabilités distinctes.

### 28.3. Structure du dépôt

```text
devops-platform/
|
+-- terraform/
|   +-- main.tf
|   +-- variables.tf
|   +-- outputs.tf
|
+-- ansible/
|   +-- ansible.cfg
|   +-- requirements.yml
|   +-- inventories/
|   |   +-- dev/
|   |   +-- staging/
|   |   +-- production/
|   +-- playbooks/
|   |   +-- site.yml
|   |   +-- verify.yml
|   +-- roles/
|       +-- common/
|       +-- webserver/
|
+-- .github/workflows/
|   +-- ansible-checks.yml
|
+-- .gitlab-ci.yml
|
+-- README.md
```

La présence simultanée de GitHub Actions et de GitLab CI dans cet exemple sert à illustrer deux choix possibles. Un projet réel peut choisir l’un ou l’autre, ou organiser plusieurs pipelines si une contrainte organisationnelle le justifie.

### 28.4. Exigences du rôle Web

Le rôle doit :

1. vérifier les paramètres de configuration requis ;
2. installer les paquets nécessaires ;
3. créer les répertoires avec les permissions prévues ;
4. déployer une page ou une application de test ;
5. générer la configuration du service ;
6. valider la configuration avant le rechargement lorsque possible ;
7. démarrer et activer le service ;
8. utiliser un handler lorsque la configuration change ;
9. valider la disponibilité du service ;
10. conserver un comportement idempotent.

### 28.5. Exigences de l'intégration

Le pipeline doit :

1. installer les dépendances requises ;
2. exécuter les contrôles syntaxiques ;
3. exécuter `ansible-lint` ;
4. empêcher l’application de changements si les contrôles échouent ;
5. utiliser l’inventaire de l’environnement prévu ;
6. réserver les permissions de production aux jobs autorisés ;
7. préserver les secrets ;
8. conserver les traces de validation sans données sensibles.

### 28.6. Critères de réussite

Le projet est terminé lorsque :

- l’inventaire décrit correctement les hôtes ;
- le playbook peut être lancé avec la bonne sélection ;
- le service est installé et actif ;
- la configuration rendue correspond aux variables d’environnement ;
- le second passage ne produit pas de changements inattendus ;
- les contrôles de qualité passent ;
- les erreurs de connexion et de permissions sont diagnostiquées proprement ;
- l’exécution de production nécessite des autorisations et un périmètre contrôlés ;
- Terraform et Ansible ne définissent pas indépendamment les mêmes éléments de configuration ;
- les procédures et décisions sont expliquées dans le README.

### 28.7. Améliorations possibles

Une fois la version de base validée, ajouter progressivement :

- un inventaire dynamique si la plateforme le justifie ;
- une validation fonctionnelle du service ;
- des tests automatisés des rôles ;
- une stratégie de déploiement progressif ;
- une stratégie de retour arrière réaliste ;
- un mécanisme centralisé de secrets ;
- une publication contrôlée des rapports de validation ;
- des permissions minimales pour les comptes d’automatisation ;
- une documentation des risques et de la reprise après échec.

## 29. Liste de contrôle avant un déploiement

### Code et structure

- [ ] Le dépôt est versionné dans Git.
- [ ] Les rôles ont une responsabilité claire.
- [ ] Les variables communes et spécifiques sont séparées.
- [ ] Les dépendances sont déclarées.
- [ ] Le playbook passe le contrôle syntaxique.
- [ ] Le code passe les contrôles de qualité convenus.

### Inventaire et périmètre

- [ ] Le bon environnement est sélectionné.
- [ ] Les hôtes sont vérifiés.
- [ ] Les groupes correspondent au rôle des machines.
- [ ] Le nombre de cibles est conforme à l'attendu.
- [ ] Le compte utilisé dispose uniquement des droits nécessaires.

### Sécurité

- [ ] Les secrets ne sont pas stockés en clair dans Git.
- [ ] La clé de chiffrement n’est pas placée à côté des fichiers chiffrés.
- [ ] La sortie des tâches ne révèle pas les secrets.
- [ ] La clé hôte SSH est vérifiée.
- [ ] Les permissions des fichiers générés sont adaptées.
- [ ] Les identifiants du pipeline sont limités aux jobs autorisés.

### Déploiement

- [ ] Les changements prévisibles ont été examinés.
- [ ] Les tâches critiques ont été testées dans un environnement adapté.
- [ ] Les configurations sont validées avant leur rechargement lorsque c’est possible.
- [ ] Les handlers sont correctement associés aux changements.
- [ ] Une vérification fonctionnelle suit le déploiement.
- [ ] La stratégie de reprise est connue.
- [ ] Les traces d’exécution sont conservées sans secrets.

## 30. Glossaire

**Ansible** : outil d’automatisation de configuration, de déploiement et d’orchestration de tâches.

**Ansible Core** : moteur central d’Ansible.

**Inventaire** : ensemble d’hôtes et de groupes sur lesquels les playbooks peuvent agir.

**Playbook** : fichier YAML décrivant une ou plusieurs séquences d’automatisation.

**Play** : ensemble de directives et de tâches associé à un groupe d’hôtes.

**Task** : opération déclarée dans un playbook.

**Module** : composant chargé d’effectuer une opération, par exemple installer un paquet ou gérer un service.

**Idempotence** : propriété qui permet de répéter une opération sans reproduire de changements inutiles lorsque l’état visé est atteint.

**Fact** : information collectée à propos d’un hôte.

**Variable** : paramètre utilisé par les tâches, rôles et templates.

**Template** : fichier dont le contenu est rendu à partir de variables et d’expressions Jinja2.

**Handler** : tâche spéciale déclenchée par une notification, typiquement à la suite d’un changement de configuration.

**Rôle** : unité réutilisable de tâches, de variables, de templates et d’autres éléments d’automatisation.

**Collection** : ensemble distribuable de rôles, modules, plugins et ressources associées.

**Ansible Vault** : mécanisme de chiffrement de contenus destinés à être utilisés par Ansible.

**`become`** : mécanisme d’escalade des privilèges pour exécuter certaines opérations avec un autre utilisateur.

**Inventaire dynamique** : inventaire construit à partir d’une source externe, par exemple une plateforme cloud.

**`ansible-lint`** : outil de vérification statique des pratiques Ansible.

**Terraform** : outil d’Infrastructure as Code principalement utilisé pour déclarer et gérer les ressources d’infrastructure.

**CI/CD** : pratiques et mécanismes d’intégration continue, de livraison continue ou de déploiement continu.

**GitOps** : approche dans laquelle l’état souhaité et les changements sont pilotés par des dépôts versionnés et des mécanismes de réconciliation adaptés.

## 31. Références officielles

Documentation Ansible :

- Prise en main : https://docs.ansible.com/projects/ansible/latest/getting_started/get_started_ansible.html
- Inventaires : https://docs.ansible.com/projects/ansible/latest/getting_started/get_started_inventory.html
- Playbooks : https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html
- Variables : https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html
- Conditions : https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html
- Handlers : https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html
- Rôles et réutilisation : https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html
- Ansible Vault : https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html
- Installation et gestion des collections : https://docs.ansible.com/projects/ansible/latest/collections_guide/index.html
- ansible-lint : https://docs.ansible.com/projects/lint/
- Terraform : https://developer.hashicorp.com/terraform/docs
- GitHub Actions : https://docs.github.com/en/actions
- GitLab CI/CD : https://docs.gitlab.com/ci/
- Kubernetes : https://kubernetes.io/docs/home/

**Principe final :** une automatisation DevOps de qualité ne se limite pas à exécuter une commande. Elle décrit l’état souhaité, limite les privilèges, protège les secrets, contrôle son périmètre, valide le résultat et peut être répétée dans des conditions maîtrisées. Ansible devient particulièrement efficace lorsqu’il s’intègre à Terraform, Git et à la CI/CD sans brouiller les responsabilités de chacun.