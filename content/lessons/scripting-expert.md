# Ansible Avancé et AWX

> **Niveau :** Expert  
> **Public cible :** administrateurs Linux, ingénieurs systèmes, ingénieurs réseau, DevOps, SRE et responsables de plateformes d'automatisation  
> **Environnement :** GNU/Linux, Ansible Core, collections Ansible, AWX et environnements d'exécution conteneurisés  
> **Prérequis :** maîtrise des fondamentaux Ansible, des playbooks YAML, des inventaires, des variables, des rôles, de SSH, de Git et des bases de Bash  
> **Objectif :** concevoir, industrialiser, sécuriser, tester et superviser une plateforme d'automatisation distribuée reposant sur Ansible et AWX.


# 1. Objectifs pédagogiques

Ce cours aborde l'automatisation d'infrastructure à un niveau expert. Il ne s'agit plus seulement d'écrire des playbooks qui configurent des machines, mais de construire un système d'automatisation reproductible, gouverné, testable et adapté à une exploitation professionnelle.

À l'issue du cours, vous devez pouvoir :

- concevoir une architecture de dépôts Ansible pour plusieurs environnements ;
- structurer des rôles réutilisables et des collections ;
- maîtriser la précédence des variables, les imports, les inclusions et les mécanismes de contrôle d'exécution ;
- organiser des déploiements progressifs et des opérations sur plusieurs groupes de machines ;
- définir des stratégies de reprise après erreur ;
- créer des environnements d'exécution reproductibles ;
- gérer les secrets, les identités et les permissions ;
- déployer et exploiter AWX à travers son Operator sur Kubernetes ;
- créer des organisations, projets, inventaires, identifiants et modèles de jobs ;
- orchestrer des processus complexes avec les workflows AWX ;
- sécuriser les exécutions à travers RBAC, la gestion des credentials et les validations ;
- piloter AWX à travers son API ;
- tester les playbooks avec Ansible Lint, Molecule et des tests ciblés ;
- gérer les déploiements, les migrations de versions et la reprise après incident ;
- détecter les risques opérationnels avant qu'ils ne provoquent une interruption de service.

Le cours se concentre sur Ansible et AWX. Il mobilise Bash, Git, Python, Kubernetes et les conteneurs lorsqu'ils sont nécessaires à la mise en œuvre d'une plateforme d'automatisation.

# 2. Architecture générale

## 2.1. Ansible, AWX et les environnements d'exécution

Ansible exécute des tâches de configuration et d'orchestration à partir d'inventaires, de playbooks, de rôles, de modules et de plugins.

AWX ajoute une plateforme de pilotage centralisée : interface web, API, gestion des organisations et des permissions, gestion des identifiants, planification, historique d'exécution, workflows et orchestration des jobs.

Les environnements d'exécution permettent de définir les dépendances nécessaires à l'exécution des playbooks dans un environnement reproductible.

```text
                 ÉQUIPE D'ADMINISTRATION
                          |
                          v
                  Git / Revue de code
                          |
                          v
              Playbooks, rôles, collections
                          |
                          v
              AWX : plateforme de contrôle
              +--------------------------+
              | Organisations            |
              | Inventaires              |
              | Credentials              |
              | Projects                 |
              | Job Templates            |
              | Workflow Templates        |
              | Schedules / Notifications |
              +--------------------------+
                          |
                          v
                Environnement d'exécution
                +--------------------------+
                | ansible-core             |
                | Collections              |
                | Modules / Plugins        |
                | Dépendances Python       |
                +--------------------------+
                          |
                          v
              Nœud(s) géré(s) / API / réseau
                          |
                          v
                Résultats et journalisation
```

Cette représentation est conceptuelle. L'architecture réelle dépend de la version d'AWX, de l'Operator, du stockage, du nombre de nœuds d'exécution et des composants activés.

## 2.2. Séparer les responsabilités

Une plateforme professionnelle distingue plusieurs responsabilités.

| Composant | Responsabilité principale |
|---|---|
| Git | historique, revue, versionnement du code et des playbooks |
| Ansible | logique déclarative et exécution des tâches |
| Collections | distribution de rôles, modules, plugins et contenus réutilisables |
| Execution Environment | dépendances nécessaires à l'exécution |
| AWX | interface, planification, autorisations, lancement et traçabilité des jobs |
| Inventaire | définition des cibles et de leurs groupes |
| Credential | accès aux systèmes et services concernés |
| Workflow | orchestration de plusieurs jobs et décisions entre étapes |
| Kubernetes | hébergement et cycle de vie de l'instance AWX gérée par l'Operator |
| Supervision | suivi de la disponibilité, des erreurs, des durées et de la capacité |

Une erreur architecturale fréquente consiste à considérer AWX comme un simple terminal web pour Ansible. AWX est surtout une plateforme d'exploitation : ses permissions, ses identifiants, ses projets, ses environnements et ses workflows doivent être conçus comme des composants de production.

## 2.3. Distinguer AWX et Ansible Automation Platform

AWX est le projet amont communautaire associé à l'automatisation par Ansible. Red Hat Ansible Automation Platform est une offre distincte, avec ses propres composants, conditions de support et fonctionnalités selon les versions et les souscriptions.

Les concepts présentés ici sont centrés sur AWX communautaire. Ne supposez pas que toutes les interfaces, fonctions, procédures d'installation ou garanties de support sont identiques entre AWX et Ansible Automation Platform.


# 3. Concevoir un dépôt Ansible professionnel

## 3.1. Pourquoi structurer le dépôt ?

Un dépôt peut commencer avec un seul playbook. Il devient rapidement difficile à maintenir lorsqu'il contient plusieurs environnements, rôles, configurations et procédures de déploiement.

Les problèmes courants sont :

- des variables dupliquées ;
- des secrets dans Git ;
- des rôles trop couplés ;
- des dépendances non documentées ;
- des chemins difficiles à retrouver ;
- des différences invisibles entre les environnements ;
- des changements impossibles à reproduire.

Une structure explicite facilite la revue, les tests et l'intégration avec AWX.

## 3.2. Structure recommandée

Exemple de dépôt pour une automatisation d'infrastructure :

```text
infra-automation/
├── ansible.cfg
├── README.md
├── requirements.yml
├── requirements.txt
├── inventories/
│   ├── lab/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── webservers.yml
│   ├── staging/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       └── all.yml
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
│           └── all.yml
├── playbooks/
│   ├── site.yml
│   ├── baseline.yml
│   ├── deploy_application.yml
│   ├── validate_services.yml
│   └── rollback_application.yml
├── roles/
│   ├── baseline_linux/
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   ├── vars/
│   │   │   └── main.yml
│   │   ├── tasks/
│   │   │   ├── main.yml
│   │   │   ├── packages.yml
│   │   │   ├── users.yml
│   │   │   └── services.yml
│   │   ├── handlers/
│   │   │   └── main.yml
│   │   ├── templates/
│   │   ├── files/
│   │   ├── meta/
│   │   │   └── main.yml
│   │   └── README.md
│   └── application/
│       ├── defaults/
│       ├── tasks/
│       ├── handlers/
│       ├── templates/
│       └── meta/
├── templates/
├── scripts/
├── tests/
└── docs/
```

Cette organisation est un exemple. Les projets de grande ampleur peuvent préférer des collections dédiées, séparer les dépôts de configuration et de code ou utiliser des inventaires externes.

## 3.3. Écrire un `ansible.cfg` explicite

Exemple :

```ini
[defaults]
inventory = ./inventories/lab/hosts.yml
roles_path = ./roles
collections_path = ./collections:~/.ansible/collections:/usr/share/ansible/collections
host_key_checking = True
retry_files_enabled = False
stdout_callback = default
```

Les options disponibles dépendent de la version d'Ansible installée. Vérifiez leur prise en charge avec la documentation de la version cible.

### Points importants

- `inventory` définit l'inventaire par défaut pour une exécution locale utilisant ce fichier de configuration.
- `roles_path` précise où Ansible recherche les rôles.
- `collections_path` contribue à déterminer où les collections sont recherchées.
- `host_key_checking = True` maintient la vérification des clés d'hôte SSH.
- Le choix du callback détermine une partie du format d'affichage des résultats.

Dans AWX, les chemins et l'environnement de recherche ne sont pas nécessairement ceux de la machine depuis laquelle le développeur lance Ansible. Les dépendances doivent être accessibles à travers le projet et l'environnement d'exécution effectivement utilisés.

## 3.4. Vérifier la configuration active

Commandes utiles :

```bash
ansible --version
ansible-config dump --only-changed
ansible-config list
ansible-galaxy collection list
ansible-galaxy role list
```

Pour déterminer le fichier de configuration effectivement utilisé :

```bash
ansible --version
```

La sortie indique généralement le chemin du fichier `ansible.cfg` détecté, ou précise qu'aucun fichier n'a été trouvé.

N'exécutez pas des mises à niveau globales de toutes les dépendances sans examiner les changements de comportement et les contraintes de compatibilité.


# 4. Maîtriser la précédence des variables

La précédence des variables est une cause fréquente d'erreurs difficiles à diagnostiquer.

Ansible permet de définir des valeurs dans plusieurs emplacements : inventaire, `group_vars`, `host_vars`, variables de rôle, variables de play, fichiers inclus, extra vars et paramètres d'exécution.

Ces sources ne possèdent pas toutes la même priorité.

## 4.1. Exemple de conflit

Inventaire :

```yaml
# inventories/lab/group_vars/all.yml

application_port: 8080
```

Rôle :

```yaml
# roles/application/defaults/main.yml

application_port: 8000
```

Playbook :

```yaml
- name: Déployer l'application
  hosts: application_servers
  gather_facts: false

  vars:
    application_port: 9000

  roles:
    - application
```

Une variable définie dans les valeurs par défaut d'un rôle est conçue pour pouvoir être remplacée. Les valeurs explicites du play et d'autres sources de priorité supérieure peuvent donc prendre le dessus.

Une variable supplémentaire passée à l'exécution peut également modifier le résultat :

```bash
ansible-playbook playbooks/deploy_application.yml \
  -e application_port=7000
```

Dans ce cas, la valeur fournie par `-e` possède une priorité très élevée.

## 4.2. Règle de conception

Il faut distinguer :

- les paramètres par défaut : valeurs raisonnables et remplaçables ;
- les variables internes : valeurs qui pilotent l'implémentation du rôle ;
- les variables d'environnement : valeurs propres à une cible ou à un groupe ;
- les paramètres de lancement : valeurs explicitement fournies à une exécution ;
- les secrets : informations sensibles dont le stockage et l'accès doivent être contrôlés.

Évitez de définir la même variable dans cinq endroits différents. La précédence peut résoudre techniquement le conflit, mais la maintenance devient alors difficile.

## 4.3. Utiliser `defaults` et `vars` correctement

`defaults/main.yml` contient les valeurs par défaut de l'interface publique du rôle.

```yaml
application_name: exemple
application_port: 8080
application_service_enabled: true
application_config_path: /etc/exemple/application.conf
```

Ces valeurs doivent pouvoir être surchargées par les utilisateurs du rôle.

`vars/main.yml` convient aux valeurs plus internes que le rôle ne souhaite pas facilement laisser remplacer dans les scénarios habituels.

Ne transformez pas toutes les variables en variables de haute priorité : cela réduit la réutilisabilité du rôle.

## 4.4. Inventaires par environnement

Exemple :

```yaml
# inventories/staging/group_vars/all.yml

environment_name: staging
application_replicas: 2
application_log_level: INFO
```

```yaml
# inventories/production/group_vars/all.yml

environment_name: production
application_replicas: 4
application_log_level: WARNING
```

Le code du playbook reste commun. Les valeurs décrivant les différences légitimes entre environnements sont placées dans les inventaires ou dans les mécanismes de configuration adaptés.

Cette séparation ne dispense pas de valider les valeurs sensibles à l'environnement.

## 4.5. Vérifier les valeurs finales

Utilisez les mécanismes de diagnostic adaptés :

```bash
ansible-inventory -i inventories/lab/hosts.yml --list
```

Pour une démonstration ciblée :

```yaml
- name: Diagnostiquer la configuration
  hosts: application_servers
  gather_facts: false

  tasks:
    - name: Afficher les paramètres non sensibles
      ansible.builtin.debug:
        msg:
          environment: "{{ environment_name }}"
          port: "{{ application_port }}"
```

Ne faites pas afficher les secrets pour diagnostiquer un problème de configuration.


# 5. Imports, inclusions et réutilisation

Les playbooks peuvent réutiliser des tâches, des rôles et d'autres fichiers. Il faut comprendre la différence entre une inclusion dynamique et un import statique.

## 5.1. `import_tasks` et `include_tasks`

`import_tasks` est une réutilisation statique : les tâches sont intégrées dans le plan d'exécution de façon statique.

`include_tasks` est une inclusion dynamique : les tâches sont incluses pendant l'exécution, ce qui permet notamment d'utiliser des variables pour déterminer les fichiers à inclure.

Exemple de tâche importée :

```yaml
- name: Configurer les bases
  ansible.builtin.import_tasks: tasks/base.yml
```

Exemple d'inclusion conditionnelle :

```yaml
- name: Charger les tâches correspondant au système
  ansible.builtin.include_tasks: "tasks/{{ ansible_facts['os_family'] }}.yml"
```

L'exemple dynamique suppose que les faits sont disponibles et qu'un fichier correspondant à la famille de système existe.

Il faut prévoir une gestion explicite pour les systèmes non supportés.

## 5.2. Utiliser `import_role` et `include_role`

Pour réutiliser un rôle depuis les tâches :

```yaml
- name: Appliquer la configuration commune
  ansible.builtin.import_role:
    name: baseline_linux
```

Pour une inclusion dynamique :

```yaml
- name: Charger un rôle selon l'environnement
  ansible.builtin.include_role:
    name: "{{ role_name }}"
```

Le deuxième exemple doit être encadré par une validation de `role_name`. Il serait dangereux de laisser une donnée non fiable déterminer librement le code à exécuter.

## 5.3. Quand privilégier une collection ?

Une collection devient intéressante lorsque le contenu doit être distribué de manière structurée, versionné indépendamment ou partagé entre plusieurs équipes et dépôts.

Elle peut contenir :

- des rôles ;
- des modules ;
- des plugins ;
- des filtres ;
- des inventaires et plugins associés ;
- de la documentation ;
- des tests ;
- des playbooks.

Une collection permet notamment de définir un namespace et un nom, par exemple :

```yaml
ansible.builtin.copy:
  src: application.conf
  dest: /etc/application/application.conf
  owner: root
  group: root
  mode: "0644"
```

L'utilisation des noms pleinement qualifiés (*Fully Qualified Collection Names*, FQCN) facilite l'identification du module et limite les ambiguïtés entre collections.

## 5.4. Fichier de dépendances des collections

Exemple de `requirements.yml` :

```yaml
collections:
  - name: ansible.posix
    version: "VERSION_VALIDEE"
  - name: community.general
    version: "VERSION_VALIDEE"
```

Les valeurs `VERSION_VALIDEE` sont des marqueurs à remplacer par des versions réellement testées et approuvées. Ce fichier n'est pas directement exécutable tant que les versions ne sont pas remplacées.

Installation :

```bash
ansible-galaxy collection install -r requirements.yml
```

Pour un environnement reproductible, consignez les versions et vérifiez leur compatibilité avec la version d'`ansible-core`, la version Python et les autres dépendances.


# 6. Concevoir des rôles véritablement réutilisables

## 6.1. Le rôle comme contrat

Un rôle ne doit pas être une simple collection de commandes. Il doit définir une interface claire.

Exemple : rôle `application`.

| Variable | Fonction | Exemple |
|---|---|---|
| `application_port` | port d'écoute | `8080` |
| `application_service_enabled` | démarrage au boot | `true` |
| `application_config_path` | chemin de configuration | `/etc/exemple/application.conf` |
| `application_allowed_hosts` | liste de cibles acceptées | `["localhost"]` |

Ces valeurs doivent être accompagnées d'une documentation précisant leurs types, leurs valeurs autorisées, leurs effets et leurs limites.

## 6.2. Ajouter des validations

Un rôle doit refuser des valeurs incohérentes avant d'effectuer une modification.

```yaml
- name: Valider les paramètres du rôle
  ansible.builtin.assert:
    that:
      - application_port | int >= 1
      - application_port | int <= 65535
      - application_service_enabled is boolean
    fail_msg: "Les paramètres de l'application sont invalides."
```

Il faut être attentif à la conversion implicite des données YAML et à leur type réel.

Une variable provenant de l'inventaire, d'une API ou d'AWX peut être une chaîne de caractères alors que le rôle attend un entier ou un booléen.

Lorsque le type doit être strictement contrôlé, validez explicitement la structure et les contraintes acceptées.

## 6.3. Séparer tâches et configuration

Un rôle peut être divisé en plusieurs fichiers :

```text
roles/application/
├── defaults/main.yml
├── tasks/main.yml
├── tasks/install.yml
├── tasks/configure.yml
├── tasks/service.yml
├── handlers/main.yml
└── templates/application.conf.j2
```

`tasks/main.yml` :

```yaml
- name: Valider les paramètres
  ansible.builtin.import_tasks: validate.yml

- name: Installer l'application
  ansible.builtin.import_tasks: install.yml

- name: Configurer l'application
  ansible.builtin.import_tasks: configure.yml

- name: Gérer le service
  ansible.builtin.import_tasks: service.yml
```

Cet exemple suppose que `tasks/validate.yml`, `tasks/install.yml`, `tasks/configure.yml` et `tasks/service.yml` existent.

L'organisation doit rendre les responsabilités visibles. Elle ne doit pas fragmenter artificiellement un rôle en dizaines de fichiers difficiles à suivre.

## 6.4. Dépendances de rôles

Le fichier `meta/main.yml` peut décrire des métadonnées et des dépendances du rôle.

Exemple :

```yaml
galaxy_info:
  role_name: application
  author: equipe_automatisation
  description: Configure une application de démonstration
  license: MIT

dependencies:
  - role: baseline_linux
```

Une dépendance de rôle doit être choisie avec soin. Les dépendances multiples et imbriquées compliquent le diagnostic et peuvent provoquer des effets de bord.

La licence doit refléter les droits applicables au contenu réellement distribué.


# 7. Idempotence et gestion des changements

## 7.1. Comprendre l'idempotence

Une opération idempotente peut être répétée sans produire des changements supplémentaires lorsque l'état souhaité est déjà atteint.

Exemple :

```yaml
- name: Assurer la présence du paquet nginx
  ansible.builtin.package:
    name: nginx
    state: present
```

Une deuxième exécution ne doit normalement pas réinstaller le paquet lorsque l'état souhaité est déjà atteint.

À l'inverse :

```yaml
- name: Ajouter une ligne à chaque exécution
  ansible.builtin.shell: "echo 'application=true' >> /tmp/application.conf"
```

Cette commande ajoute une nouvelle ligne à chaque exécution. Elle n'est pas idempotente.

Version préférable :

```yaml
- name: Déclarer le paramètre de configuration
  ansible.builtin.lineinfile:
    path: /tmp/application.conf
    regexp: '^application='
    line: 'application=true'
    create: true
```

Cet exemple est pédagogique. Le chemin `/tmp/application.conf` n'est pas recommandé pour une configuration persistante de production.

## 7.2. Quand `command` et `shell` sont-ils nécessaires ?

Privilégiez un module dédié lorsqu'il existe et couvre correctement le besoin.

Exemples :

- `package` pour les paquets ;
- `file` pour les permissions et répertoires ;
- `copy` pour les fichiers ;
- `template` pour les fichiers dynamiques ;
- `service` ou `systemd_service` pour les services ;
- `user` pour les comptes ;
- `uri` pour les appels HTTP.

Utilisez `command` lorsque vous devez lancer un programme externe sans dépendre d'une interprétation shell particulière.

Utilisez `shell` lorsque les fonctionnalités du shell sont réellement nécessaires, par exemple un pipeline ou une expansion shell explicitement voulue.

Une commande opaque est plus difficile à rendre idempotente et à tester qu'une déclaration d'état fondée sur des modules adaptés.

## 7.3. Définir correctement `changed_when`

Certaines commandes ne possèdent pas de comportement idempotent exposé au niveau du module. Dans ce cas, `changed_when` permet d'adapter la classification du résultat.

```yaml
- name: Contrôler une version d'application
  ansible.builtin.command:
    cmd: /usr/local/bin/application --version
  register: version_result
  changed_when: false
```

Cette tâche ne modifie normalement pas l'état de la machine. `changed_when: false` évite qu'elle soit signalée comme ayant changé le système.

Ne définissez pas systématiquement `changed_when: false` sur une commande qui modifie réellement la machine. Vous masqueriez alors des modifications importantes dans les résultats.

## 7.4. Définir correctement `failed_when`

Exemple :

```yaml
- name: Vérifier un programme
  ansible.builtin.command:
    cmd: /usr/local/bin/application --health
  register: health_result
  changed_when: false
  failed_when: health_result.rc != 0
```

La tâche échoue si le code de retour est non nul.

Lorsque plusieurs conditions sont définies comme une liste YAML dans `failed_when`, Ansible les combine normalement avec un ET logique. Si une seule condition doit suffire pour déclarer l'échec, exprimez le OU explicitement dans une expression adaptée.

## 7.5. Check mode et diff mode

Test avec simulation :

```bash
ansible-playbook playbooks/site.yml --check
```

Avec comparaison des différences :

```bash
ansible-playbook playbooks/site.yml --check --diff
```

Le check mode simule les modifications prises en charge par les modules. Ce n'est pas une simulation parfaite de toutes les opérations.

Limites importantes :

- certains modules ne prennent pas en charge check mode ;
- un module peut rapporter un état sans exécuter exactement le même chemin que dans un lancement réel ;
- les conditions dépendant de résultats enregistrés peuvent se comporter différemment ;
- certaines tâches peuvent encore avoir des effets externes si elles sont mal conçues ou si elles utilisent des mécanismes incompatibles avec la simulation.

Le diff mode peut exposer des données sensibles si des fichiers de configuration contiennent des secrets. Vérifiez les risques avant de diffuser les sorties.


# 8. Handlers et orchestration

## 8.1. Le principe des handlers

Un handler permet d'effectuer une action seulement lorsqu'une tâche l'a notifiée.

Exemple :

```yaml
- name: Configurer le service
  hosts: application_servers
  become: true

  tasks:
    - name: Déployer la configuration
      ansible.builtin.template:
        src: application.conf.j2
        dest: /etc/application/application.conf
        owner: root
        group: root
        mode: "0644"
      notify: Redémarrer application

  handlers:
    - name: Redémarrer application
      ansible.builtin.service:
        name: application
        state: restarted
```

Le handler ne redémarre le service que si la tâche notifie le changement. La notification n'est généralement exécutée qu'une seule fois par handler dans le contexte concerné, même si plusieurs tâches l'ont notifié.

## 8.2. Utiliser `listen`

Un handler peut écouter un nom de notification commun.

```yaml
handlers:
  - name: Redémarrer le service principal
    ansible.builtin.service:
      name: application
      state: restarted
    listen: recharger_configuration_application
```

Plusieurs tâches peuvent notifier `recharger_configuration_application`, sans devoir connaître le nom exact du handler.

Cela aide à découpler les tâches de configuration des actions techniques effectuées après les changements.

## 8.3. Forcer l'exécution des handlers

Par défaut, les handlers sont généralement exécutés à des points de synchronisation prévus par Ansible, notamment à la fin du play.

Dans certains scénarios, on peut utiliser :

```yaml
- name: Exécuter les handlers notifiés maintenant
  ansible.builtin.meta: flush_handlers
```

Cette opération modifie l'ordre d'exécution. Elle doit être placée lorsque le service doit absolument être rechargé avant que les tâches suivantes poursuivent le traitement.

Évitez d'utiliser `flush_handlers` sans comprendre ses effets sur la séquence complète du playbook.


# 9. Stratégies d'exécution multi-hôtes

## 9.1. La stratégie `linear`

La stratégie par défaut `linear` fait avancer les hôtes par tâche, en respectant les points de synchronisation de la stratégie.

```yaml
- name: Configurer les serveurs
  hosts: application_servers
  strategy: linear
  tasks:
    - name: Créer le répertoire applicatif
      ansible.builtin.file:
        path: /opt/application
        state: directory
        mode: "0755"
```

## 9.2. La stratégie `free`

La stratégie `free` permet aux hôtes de progresser indépendamment selon leur rythme, plutôt que d'attendre systématiquement les autres hôtes à chaque tâche.

```yaml
- name: Exécuter indépendamment par hôte
  hosts: application_servers
  strategy: free

  tasks:
    - name: Vérifier la connectivité
      ansible.builtin.ping:
```

Cette approche peut améliorer la durée de certaines opérations, mais elle modifie l'ordre relatif des tâches entre hôtes.

N'utilisez pas `free` lorsque la conception dépend d'une synchronisation stricte entre les machines.

## 9.3. `serial` : déploiement progressif

Le paramètre `serial` permet de traiter les hôtes par lots.

```yaml
- name: Mettre à jour progressivement les serveurs web
  hosts: webservers
  serial: 2
  become: true

  tasks:
    - name: Mettre à jour le cache des paquets
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600
```

Cet exemple suppose que les machines ciblées utilisent un système compatible avec APT.

Si le parc est composé de plusieurs distributions, le traitement des paquets doit être adapté par groupe ou par rôle.

## 9.4. Limiter les échecs tolérés

```yaml
- name: Déploiement progressif
  hosts: webservers
  serial: 4
  max_fail_percentage: 25
```

Le seuil est évalué dans le contexte des lots lorsqu'on utilise `serial`. Il faut comprendre la manière dont les échecs sont comptés et que le seuil doit être dépassé pour provoquer l'arrêt.

Pour une opération critique, il est souvent préférable de tester une règle de déploiement avec peu d'hôtes avant de l'étendre au parc.

## 9.5. `run_once` et `delegate_to`

`run_once: true` indique qu'une tâche doit être exécutée une seule fois dans le contexte prévu par le play, mais lorsqu'elle est associée à `serial`, le comportement doit être interprété avec prudence : l'exécution peut être liée à chaque lot.

Exemple de délégation :

```yaml
- name: Vérifier un point de contrôle central
  ansible.builtin.command:
    cmd: /usr/local/bin/check-control-plane
  delegate_to: localhost
  run_once: true
  changed_when: false
```

Cette tâche exécute la commande sur le contrôleur d'exécution local, ici `localhost`, et non sur chaque machine ciblée.

Dans AWX, ce « localhost » correspond à l'environnement d'exécution du job, pas nécessairement au poste depuis lequel l'opérateur consulte l'interface web.

## 9.6. Fact gathering et `delegate_facts`

La délégation d'une tâche ne signifie pas automatiquement que ses faits seront stockés pour l'hôte auquel elle est déléguée.

Lorsqu'une tâche collecte des faits et doit les associer à l'hôte délégué, il peut être nécessaire d'utiliser `delegate_facts: true`.

La gestion des faits doit être conçue explicitement pour éviter de stocker les informations sur le mauvais hôte.


# 10. Gestion des erreurs avec blocks, rescue et always

Les blocs Ansible permettent de structurer les traitements qui doivent posséder une stratégie de reprise ou de nettoyage.

## 10.1. Structure générale

```yaml
- name: Traiter un changement protégé
  block:
    - name: Préparer l'opération
      ansible.builtin.debug:
        msg: "Préparation"

    - name: Effectuer l'opération
      ansible.builtin.command:
        cmd: /usr/local/bin/operation-controllee
  rescue:
    - name: Signaler l'échec
      ansible.builtin.debug:
        msg: "Une tâche du bloc a échoué"
  always:
    - name: Effectuer le traitement final
      ansible.builtin.debug:
        msg: "Fin du bloc"
```

Les commandes de cet exemple sont illustratives. Dans un vrai playbook, les tâches de reprise et de nettoyage doivent être adaptées à l'opération concernée.

## 10.2. Limites des blocs de reprise

`rescue` ne capte pas indistinctement toutes les erreurs possibles.

Par exemple :

- une erreur de syntaxe ou de définition de tâche ne se comporte pas comme un échec normal d'exécution ;
- un hôte inaccessible ne déclenche pas nécessairement `rescue` ;
- une panne de l'environnement d'exécution peut interrompre le traitement avant la reprise.

Les blocs de reprise ne doivent pas être confondus avec un mécanisme universel de transaction.

## 10.3. Exemple de déploiement avec validation

```yaml
- name: Déployer et valider une configuration
  hosts: application_servers
  become: true

  tasks:
    - name: Appliquer la configuration et contrôler le résultat
      block:
        - name: Installer le paquet applicatif
          ansible.builtin.package:
            name: application
            state: present

        - name: Déployer la configuration
          ansible.builtin.template:
            src: application.conf.j2
            dest: /etc/application/application.conf
            owner: root
            group: root
            mode: "0644"
          notify: Redémarrer application

        - name: Vérifier la syntaxe de la configuration
          ansible.builtin.command:
            cmd: /usr/local/bin/application --check-config
          changed_when: false

      rescue:
        - name: Signaler l'échec du déploiement
          ansible.builtin.fail:
            msg: "Le déploiement de l'application a échoué."

  handlers:
    - name: Redémarrer application
      ansible.builtin.service:
        name: application
        state: restarted
```

Cet exemple décrit une structure, mais le programme `application --check-config` doit réellement exister et fournir le comportement attendu.

Une opération de production devrait également définir la stratégie de restauration si une modification partielle a déjà eu lieu.


# 11. Ansible Vault et gestion des secrets

## 11.1. Pourquoi les secrets sont différents des variables ordinaires

Un secret peut être :

- un mot de passe ;
- une clé privée ;
- un jeton d'API ;
- une chaîne de connexion ;
- un certificat ;
- un mot de passe de base de données.

Les secrets ne doivent pas être enregistrés en clair dans un dépôt Git ni affichés dans les journaux d'exécution.

Les risques existent dans toutes les étapes : développement, revue, stockage, transfert, exécution, diagnostic et sauvegarde.

## 11.2. Chiffrer un fichier avec Vault

Exemple :

```bash
ansible-vault encrypt inventories/production/group_vars/all/secrets.yml
```

L'outil demande une information de chiffrement selon le mode configuré.

Pour créer un nouveau fichier chiffré :

```bash
ansible-vault create inventories/production/group_vars/all/secrets.yml
```

Pour consulter ou modifier un fichier :

```bash
ansible-vault view inventories/production/group_vars/all/secrets.yml
ansible-vault edit inventories/production/group_vars/all/secrets.yml
```

Ne stockez jamais le mot de passe Vault en clair dans le dépôt ou dans une commande durablement enregistrée dans l'historique du shell.

## 11.3. Exemple de configuration chiffrée

Fichier déchiffré conceptuellement :

```yaml
database_username: application_service
database_password: SECRET_NON_PARTAGE
```

La valeur d'exemple `SECRET_NON_PARTAGE` est un marqueur, pas un secret utilisable.

Le fichier réel doit être chiffré avec Ansible Vault avant d'être intégré au dépôt.

## 11.4. Combiner Vault et AWX

AWX peut gérer des credentials de type Vault selon les types disponibles et la configuration de la plateforme. Il permet d'exécuter des jobs dont le contenu utilise des fichiers ou variables chiffrés sans exiger que l'opérateur connaisse ou affiche directement leur valeur.

L'organisation doit s'assurer que :

- seuls les utilisateurs autorisés peuvent utiliser les credentials ;
- les secrets ne sont pas imprimés dans les messages de debug ;
- les extra vars n'exposent pas accidentellement des informations sensibles ;
- la sortie des jobs est contrôlée ;
- les dépôts ne contiennent pas les mots de passe Vault ;
- la rotation des secrets suit un processus documenté.

## 11.5. `no_log`

Pour une tâche susceptible de manipuler une donnée sensible :

```yaml
- name: Créer une ressource nécessitant un secret
  ansible.builtin.uri:
    url: https://api.example.invalid/resources
    method: POST
    body_format: json
    body:
      username: "{{ service_username }}"
      password: "{{ service_password }}"
    status_code:
      - 200
      - 201
  no_log: true
```

L'adresse `.invalid` est volontairement un domaine réservé aux exemples. Le playbook ne doit pas être utilisé tel quel contre un service réel.

`no_log: true` réduit l'exposition des données dans les sorties Ansible. Il ne chiffre pas les fichiers sources et ne protège pas automatiquement chaque système ou système de journalisation en aval.

Cette option peut également rendre le diagnostic plus difficile. Il faut éviter de supprimer indistinctement les diagnostics utiles de toutes les tâches.


# 12. Inventaires dynamiques et faits

## 12.1. Inventaire statique

Un inventaire statique peut être écrit en YAML :

```yaml
all:
  children:
    webservers:
      hosts:
        web01:
          ansible_host: 192.0.2.10
        web02:
          ansible_host: 192.0.2.11

    databases:
      hosts:
        db01:
          ansible_host: 192.0.2.20
```

Les adresses `192.0.2.0/24` appartiennent à une plage réservée à la documentation. Remplacez-les par des adresses autorisées dans votre laboratoire.

## 12.2. Cibler les groupes

Exemple :

```bash
ansible-playbook -i inventories/lab/hosts.yml \
  playbooks/site.yml --limit webservers
```

`--limit` réduit l'ensemble des cibles pour cette exécution.

Cette option est utile pour les tests progressifs, mais elle peut aussi empêcher une étape nécessaire de s'exécuter sur les autres groupes. Vérifiez les dépendances entre les plays avant de limiter une exécution.

## 12.3. Inventaire dynamique

Un inventaire dynamique récupère les cibles depuis une source externe, comme un système cloud, un CMDB ou une API.

Il exige souvent :

- une collection adaptée ;
- une configuration du plugin d'inventaire ;
- des credentials ;
- des droits de lecture sur la source ;
- une procédure de gestion des erreurs et des changements de schéma.

Les détails dépendent du plugin choisi. Il faut utiliser le plugin correspondant à la plateforme et à ses versions, plutôt que de supposer qu'un même fichier de configuration sera compatible avec tous les fournisseurs.

## 12.4. AWX et synchronisation des inventaires

AWX permet de gérer des inventaires statiques et des sources dynamiques compatibles avec la plateforme.

La synchronisation doit être testée séparément du lancement des jobs. Une synchronisation qui échoue peut produire un inventaire incomplet ou laisser des données plus anciennes que prévu.

Il faut donc surveiller l'état et la date de la dernière mise à jour de chaque source importante.


# 13. Créer un environnement d'exécution reproductible

## 13.1. Pourquoi un environnement d'exécution ?

Le contrôleur Ansible et l'environnement dans lequel les tâches s'exécutent ont besoin de dépendances compatibles.

Ces dépendances incluent notamment :

- `ansible-core` ;
- les collections Ansible ;
- des bibliothèques Python ;
- des utilitaires système ;
- certains outils spécifiques aux modules et plugins utilisés.

Une exécution locale peut fonctionner parce que le poste possède déjà ces dépendances. Le même playbook peut échouer dans AWX lorsque l'environnement d'exécution ne les contient pas.

## 13.2. Contenu typique d'un environnement

```text
Execution Environment
├── Base image
├── Python
├── ansible-core
├── Collections
├── Bibliothèques Python
├── Outils système
└── Métadonnées de construction
```

L'objectif est de rendre les dépendances explicites et de limiter les écarts entre les exécutions.

## 13.3. Définir les collections

Exemple `requirements.yml` :

```yaml
collections:
  - name: ansible.posix
    version: "VERSION_VALIDEE"
  - name: community.general
    version: "VERSION_VALIDEE"
```

Les versions doivent être remplacées par des versions homologuées. Dans un environnement de production, ne laissez pas une installation choisir silencieusement des versions arbitraires à chaque reconstruction.

## 13.4. Définir les dépendances Python

Exemple `requirements.txt` :

```text
# Remplacer par les dépendances réelles et leurs versions validées.
requests==VERSION_VALIDEE
```

Cette ligne est un modèle documentaire : `VERSION_VALIDEE` doit être remplacé par une véritable version numérique avant installation.

Ne déclarez pas une bibliothèque uniquement parce qu'elle est disponible sur le poste de développement. Justifiez chaque dépendance dans le projet.

## 13.5. Définir les dépendances système

Exemple `bindep.txt` :

```text
# Exemple documentaire :
# git
# openssh-clients
```

Les noms des paquets dépendent de la distribution et de l'image de base. Vérifiez qu'ils existent dans l'environnement de construction choisi.

## 13.6. Définition d'Execution Environment

Exemple de structure de fichier `execution-environment.yml` pour une version compatible d'Ansible Builder :

```yaml
version: 3

dependencies:
  galaxy: requirements.yml
  python: requirements.txt
  system: bindep.txt
```

Le schéma de définition doit être compatible avec la version d'Ansible Builder utilisée. La version de format présentée ici est un exemple courant ; les schémas et options doivent être vérifiés dans la documentation de la version installée.

## 13.7. Construire l'environnement

Une fois Ansible Builder installé :

```bash
ansible-builder build \
  --file execution-environment.yml \
  --tag registry.example.invalid/automation/infra-ee:1.0.0
```

Le nom de registre `.invalid` est réservé à l'exemple. Remplacez-le par un registre privé ou public autorisé.

Avant de pousser l'image, vérifiez :

- la compatibilité entre `ansible-core` et les collections ;
- les versions de Python ;
- les dépendances système ;
- l'origine de l'image de base ;
- les vulnérabilités connues ;
- la reproductibilité de la construction.

## 13.8. Versionner les images

Évitez d'utiliser un tag flottant tel que `latest` comme seule référence de production.

Exemple :

```text
registry.exemple/automation/infra-ee:1.0.0
```

Le tag doit identifier une version approuvée. Pour renforcer l'intégrité, les plateformes peuvent également utiliser un digest d'image immuable, selon leur méthode de distribution et de contrôle.

La reproductibilité dépend aussi du contenu de base et des dépendances transitives. Un simple tag sémantique ne suffit pas à garantir qu'une reconstruction produira des octets identiques.

## 13.9. Intégrer l'environnement à AWX

Les grandes étapes sont :

1. construire l'image ;
2. exécuter les tests locaux ;
3. publier l'image dans un registre accessible ;
4. créer ou configurer les credentials nécessaires au registre ;
5. déclarer l'Execution Environment dans AWX ;
6. l'associer à un modèle de job ;
7. exécuter un job de validation ;
8. promouvoir l'image dans les environnements suivants après approbation.

AWX doit pouvoir récupérer l'image depuis le registre. Les identifiants de registre ne doivent pas être intégrés en clair à la définition du modèle ou à un dépôt Git.


# 14. Installer et exploiter AWX avec l'Operator

## 14.1. Architecture d'installation

L'AWX Operator est un opérateur Kubernetes conçu pour installer et gérer le cycle de vie d'une instance AWX dans son namespace.

L'approche n'est pas équivalente à l'installation de la commande `ansible-playbook` sur une machine Linux.

Le modèle général est :

```text
Cluster Kubernetes
        |
        v
Namespace d'automatisation
        |
        +-- AWX Operator
        |
        +-- Ressources personnalisées AWX
        |
        +-- Workloads AWX
        |
        +-- Service / exposition réseau
        |
        +-- Stockage et base de données
        |
        +-- Secrets et configuration
```

La composition exacte dépend de la version de l'Operator, du mode de déploiement et de la configuration du stockage et de la base de données.

## 14.2. Prérequis

Avant le déploiement, vérifiez :

- la disponibilité et l'état du cluster Kubernetes ;
- la version de Kubernetes et sa compatibilité avec l'Operator choisi ;
- les ressources CPU et mémoire ;
- le stockage persistant ;
- la stratégie de sauvegarde ;
- la méthode d'exposition réseau ;
- la gestion des certificats TLS ;
- la politique de gestion des secrets ;
- les autorisations et limites de l'Operator ;
- les procédures de restauration et de mise à niveau.

Ne choisissez pas une version de l'Operator sans consulter sa documentation de compatibilité.

## 14.3. Créer un namespace dédié

```bash
kubectl create namespace automation
```

Vérifiez son existence :

```bash
kubectl get namespace automation
```

Ce namespace est un exemple. Adaptez-le aux règles d'organisation du cluster.

## 14.4. Installer l'Operator

L'installation dépend de la version de l'Operator et de la méthode choisie. Utilisez les instructions correspondant exactement à la version ciblée dans la documentation officielle.

Après installation, contrôlez les ressources :

```bash
kubectl get pods -n automation
kubectl get deployments -n automation
kubectl get events -n automation --sort-by=.metadata.creationTimestamp
```

Le nom des ressources peut différer selon la version et la méthode d'installation.

## 14.5. Exemple conceptuel de ressource AWX

Après installation de l'Operator et selon le schéma de la version correspondante, une ressource personnalisée peut ressembler à ceci :

```yaml
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx-demo
  namespace: automation
spec:
  service_type: ClusterIP
```

Cet exemple minimal doit être vérifié contre le schéma de la version installée. Les configurations de persistance, de TLS, de base de données, d'exposition réseau et d'autres propriétés peuvent nécessiter des champs supplémentaires.

`ClusterIP` expose le service au niveau interne du cluster. L'accès depuis l'extérieur doit être conçu séparément avec une solution appropriée, par exemple un ingress ou un autre mécanisme de publication réseau compatible.

N'exposez pas le service d'administration directement sur Internet sans politique d'accès, TLS et contrôle d'identité adaptés.

## 14.6. Vérifier le déploiement

```bash
kubectl get awx -n automation
kubectl get pods -n automation
kubectl get pvc -n automation
kubectl get services -n automation
kubectl get events -n automation --sort-by=.metadata.creationTimestamp
```

Inspectez ensuite les journaux de l'Operator et les ressources concernées si le déploiement reste bloqué.

Exemple :

```bash
kubectl logs deployment/awx-operator-controller-manager \
  -n automation \
  -c awx-manager
```

Le nom du déploiement, du conteneur et les options exactes dépendent de l'installation. Vérifiez-les avec `kubectl get deployments` et `kubectl describe`.

## 14.7. Sauvegardes et restauration

Une plateforme AWX de production doit posséder un plan de sauvegarde testé.

Il faut distinguer :

- les données de la base de données ;
- les secrets et identifiants de la plateforme ;
- les configurations et ressources AWX ;
- les volumes persistants ;
- les dépôts Git sources ;
- les images d'Execution Environment ;
- les documents nécessaires à la restauration.

La restauration ne se limite pas à recréer les pods. Elle exige une procédure cohérente entre les données, les secrets, la configuration et les versions.

L'Operator fournit des mécanismes de sauvegarde et de restauration selon ses versions. Vérifiez la documentation correspondante et effectuez un test de restauration dans un environnement isolé avant de considérer la sauvegarde comme opérationnelle.


# 15. Modèle opérationnel AWX

AWX repose sur plusieurs objets qui doivent être cohérents.

## 15.1. Organisation

Une organisation structure une partie des ressources, des utilisateurs et des équipes de la plateforme.

Exemple de séparation conceptuelle :

```text
AWX
├── Organisation Réseau
│   ├── Inventaires réseau
│   ├── Credentials réseau
│   └── Projets réseau
├── Organisation Linux
│   ├── Inventaires Linux
│   ├── Credentials Linux
│   └── Projets Linux
└── Organisation Plateforme
    ├── Workflows communs
    ├── Projets de plateforme
    └── Environnements d'exécution
```

Les organisations ne remplacent pas les règles de moindre privilège. Il faut aussi configurer les autorisations des utilisateurs, équipes et ressources.

## 15.2. Projet

Un projet AWX représente généralement une source de contenu d'automatisation, souvent un dépôt Git.

Le projet fournit les playbooks et les rôles, tandis que les dépendances externes doivent être disponibles dans l'environnement d'exécution ou selon le mécanisme de gestion de contenu retenu.

Une bonne pratique consiste à référencer une branche ou un commit approuvé et à faire passer les changements par une revue de code.

## 15.3. Inventaire

Un inventaire définit les machines gérées et leur regroupement.

Il peut être statique ou alimenté par une source dynamique.

Les groupes peuvent refléter :

- les rôles des machines ;
- les environnements ;
- les zones réseau ;
- les centres de données ;
- les fonctions métier.

Les groupes et les variables doivent être cohérents avec l'architecture réelle de l'infrastructure.

## 15.4. Credential

Les credentials permettent d'utiliser les informations nécessaires à une connexion ou à un service externe.

Il peut s'agir d'un accès SSH, d'un credential Vault, d'un accès API ou d'une autre identité prise en charge.

Les utilisateurs peuvent être autorisés à utiliser certains credentials sans disposer nécessairement du droit de lire leur valeur secrète. Cette distinction doit être prise en compte dans la conception des permissions.

## 15.5. Execution Environment

L'Execution Environment fournit l'environnement logiciel à partir duquel Ansible est lancé.

Il doit correspondre aux dépendances nécessaires au projet choisi.

Il est recommandé de tester et versionner ces environnements au même titre que les playbooks.

## 15.6. Job Template

Un Job Template définit les paramètres utilisés pour lancer un job.

Il peut notamment associer :

- un projet ;
- un playbook ;
- un inventaire ;
- des credentials ;
- un environnement d'exécution ;
- des variables ;
- des tags ;
- des limites de cibles ;
- des paramètres de privilèges ;
- des politiques d'exécution.

Un modèle de job est donc un contrat opérationnel entre le code d'automatisation et son utilisation dans AWX.

## 15.7. Workflow Job Template

Un workflow orchestre plusieurs ressources AWX, souvent plusieurs modèles de jobs, dans un ordre défini.

Il peut représenter une procédure de mise en production, une maintenance, une validation post-déploiement ou une opération de retour arrière.


# 16. Construire un Job Template fiable

## 16.1. Définir un modèle de job

Exemple de modèle conceptuel :

```text
Nom :
  Validation - Serveurs Linux

Organisation :
  Linux

Projet :
  infra-automation

Playbook :
  playbooks/validate_services.yml

Inventaire :
  staging

Execution Environment :
  infra-ee:1.0.0

Credential :
  SSH - staging

Options :
  Limites contrôlées
  Tags autorisés
  Survey activé
  Privilege escalation selon le besoin
```

Les valeurs sont illustratives. Les noms réels doivent correspondre aux ressources effectivement créées dans AWX.

## 16.2. Ne pas confondre inventaire et credential

L'inventaire indique quelles cibles sont visées.

Le credential indique comment authentifier l'accès.

Ces deux responsabilités sont distinctes. Un inventaire correct n'implique pas que le job possède les identifiants nécessaires. De même, un credential valide ne doit pas donner automatiquement accès à tout le parc.

## 16.3. Contrôler le privilège d'exécution

L'option *Privilege Escalation* permet d'exécuter certaines tâches avec des privilèges élevés sur les hôtes gérés.

Son activation doit correspondre au besoin réel du playbook.

Ne l'activez pas systématiquement au niveau d'un modèle de job si le traitement n'en a pas besoin.

## 16.4. Gérer les extra vars

Les extra vars peuvent remplacer des valeurs définies dans le projet et ont une priorité élevée.

Cela signifie que les variables fournies à l'exécution doivent être considérées comme une interface sensible.

Ne permettez pas à une personne non autorisée de saisir une variable qui pourrait modifier arbitrairement un chemin, un utilisateur privilégié ou une cible critique.

Utilisez des Survey fields typés et des validations Ansible, et limitez les variables exposées.

## 16.5. `Limit` et `Tags`

Le champ `Limit` peut limiter les cibles d'un playbook.

Les tags peuvent limiter les tâches sélectionnées.

Ces mécanismes sont utiles pour le contrôle d'exécution, mais ne constituent pas à eux seuls des contrôles d'autorisation. Un opérateur ne doit pas obtenir des droits étendus uniquement parce qu'il peut sélectionner des tags ou saisir des limites.


# 17. Workflows AWX avancés

## 17.1. Pourquoi les workflows sont-ils utiles ?

Un déploiement complet peut nécessiter plusieurs étapes :

1. validation des variables ;
2. vérification des prérequis ;
3. contrôle du système ;
4. déploiement de la configuration ;
5. vérification de santé ;
6. approbation ;
7. déploiement en production ;
8. notification des résultats.

Un workflow permet de modéliser cette séquence dans AWX.

## 17.2. Exemple de workflow

```text
                    DÉMARRAGE
                        |
                        v
              Validation des paramètres
                        |
               +--------+--------+
               |                 |
             Succès             Échec
               |                 |
               v                 v
         Précontrôles       Notification
               |
               v
          Déploiement
               |
        +------+------+
        |             |
      Succès         Échec
        |             |
        v             v
    Validation     Diagnostic
     de santé          |
        |              v
        v        Décision humaine
   Approbation
        |
        v
 Déploiement suivant
        |
        v
  Notification finale
```

Ce schéma montre une logique d'orchestration. Les relations exactes sont configurées dans le workflow AWX, avec des chemins de succès, d'échec ou d'état final selon les capacités de la version utilisée.

## 17.3. Les transitions de workflow

Les nœuds peuvent être reliés par des conditions sur le résultat des jobs précédents, par exemple :

- succès ;
- échec ;
- fin ou état final, selon les transitions disponibles dans la version.

Une action de reprise doit être clairement définie. Il ne suffit pas de relier un échec à un autre job : le job de diagnostic ou de restauration doit être conçu de façon à limiter les dommages.

## 17.4. Ajouter des approbations

Pour une opération à risque, une approbation humaine peut être placée avant le déploiement en production.

Cette étape permet de vérifier :

- la version de l'application ;
- les résultats des tests ;
- les préconditions ;
- l'environnement ciblé ;
- la fenêtre de maintenance ;
- la disponibilité de la procédure de restauration.

Une approbation n'est utile que si l'approbateur reçoit suffisamment d'informations pour comprendre ce qui va être exécuté.

## 17.5. Schedules et notifications

AWX permet de programmer des exécutions et d'associer des notifications selon les fonctionnalités et les intégrations disponibles.

Une tâche planifiée doit posséder :

- un horaire clair ;
- un responsable ;
- une politique de notification ;
- un comportement attendu en cas d'échec ;
- une procédure de diagnostic ;
- une règle concernant les exécutions concurrentes.

Ne supposez pas qu'un schedule est réussi simplement parce qu'il est configuré. Surveillez les résultats réels et les erreurs.


# 18. Gestion des accès et sécurité AWX

## 18.1. RBAC

Le contrôle d'accès fondé sur les rôles, ou RBAC, permet d'associer des autorisations à des utilisateurs et des équipes.

La conception doit distinguer les tâches courantes :

- consulter les résultats ;
- lancer les jobs ;
- modifier le contenu d'automatisation ;
- gérer les credentials ;
- modifier les inventaires ;
- créer des modèles et des workflows ;
- administrer la plateforme.

Ces responsabilités ne doivent pas être regroupées dans un rôle unique lorsque les besoins sont différents.

## 18.2. Séparation des rôles

Exemple d'organisation :

| Équipe | Responsabilités possibles |
|---|---|
| Développement de l'automatisation | modifier les playbooks et rôles dans Git |
| Exploitation Linux | utiliser certains jobs de maintenance |
| Réseau | gérer les automatisations réseau autorisées |
| Release Management | approuver les déploiements critiques |
| Administrateurs AWX | administrer la plateforme |
| Audit | consulter les résultats et historiques autorisés |

La séparation exacte dépend du contexte. L'objectif est d'accorder chaque permission pour une responsabilité définie.

## 18.3. Credential sans exposition de sa valeur

Une plateforme d'automatisation doit distinguer le droit d'utiliser un credential du droit d'en consulter la valeur.

Les credentials ne doivent pas être copiés dans les variables de projet, les playbooks ou les journaux.

Un modèle de job peut éventuellement utiliser un credential avec des permissions de lancement appropriées, sans permettre à l'utilisateur de récupérer directement le secret stocké.

Il faut vérifier les autorisations de la version AWX réellement déployée, plutôt que d'assumer que toutes les versions exposent exactement les mêmes options.

## 18.4. Minimiser les secrets et les sorties

N'écrivez pas :

```yaml
- name: Afficher le mot de passe
  ansible.builtin.debug:
    var: database_password
```

Même pendant un diagnostic, une telle tâche peut exposer le secret dans les sorties.

Préférez :

```yaml
- name: Vérifier que le secret a été fourni
  ansible.builtin.assert:
    that:
      - database_password is defined
      - database_password | length > 0
    fail_msg: "La configuration du secret est incomplète."
  no_log: true
```

Cette tâche valide la présence et la non-vacuité du paramètre. Elle ne prouve pas que le secret fonctionne auprès du service distant.

## 18.5. Sécuriser l'interface AWX

Au niveau de la plateforme, examinez notamment :

- TLS et les certificats ;
- le contrôle d'accès au réseau ;
- l'authentification et l'intégration éventuelle à un fournisseur d'identité ;
- la politique de permissions ;
- la protection des credentials ;
- la gestion et la rotation des tokens API ;
- les journaux d'audit ;
- les sauvegardes chiffrées et les droits de lecture ;
- la mise à jour de la plateforme et de ses dépendances.

Les mécanismes exacts dépendent de la version d'AWX, de son déploiement Kubernetes et des services d'identité utilisés.


# 19. Piloter AWX avec son API

## 19.1. Pourquoi utiliser l'API ?

Une API permet d'intégrer les opérations AWX à des outils externes :

- portails internes ;
- systèmes de ticketing ;
- pipelines CI/CD ;
- outils d'approbation ;
- scripts de contrôle ;
- tableaux de bord ;
- orchestrateurs.

Le pilotage par API doit respecter les mêmes permissions que le pilotage depuis l'interface.

## 19.2. Authentification

AWX propose des mécanismes d'authentification pour son API, dont des tokens selon la configuration et la version.

Le token doit être conservé dans un mécanisme adapté et limité au besoin de l'intégration.

Évitez :

- de coder le token directement dans un script ;
- de le versionner dans Git ;
- de le transmettre en clair à des journaux ;
- de l'injecter dans une commande durablement conservée dans l'historique ;
- d'accorder plus de permissions que nécessaire.

## 19.3. Exemple de lancement par API

Supposons un endpoint AWX autorisé et un Job Template déjà créé.

Exemple conceptuel :

```bash
curl --fail-with-body \
  --silent \
  --show-error \
  --request POST \
  --header "Authorization: Bearer ${AWX_TOKEN}" \
  --header "Content-Type: application/json" \
  --data '{}' \
  "${AWX_URL}/api/v2/job_templates/${JOB_TEMPLATE_ID}/launch/"
```

Les variables sont des prérequis et doivent être définies avant l'exécution. `AWX_TOKEN` représente un secret, `AWX_URL` une URL de base autorisée et `JOB_TEMPLATE_ID` un identifiant réel.

L'exemple suppose que la version et la configuration AWX acceptent cette méthode d'authentification et cet endpoint. Vérifiez l'API de la plateforme cible.

Cette commande lance un job ; elle ne prouve pas que le job s'est terminé avec succès.

## 19.4. Vérifier les paramètres

```bash
: "${AWX_URL:?AWX_URL est obligatoire}"
: "${AWX_TOKEN:?AWX_TOKEN est obligatoire}"
: "${JOB_TEMPLATE_ID:?JOB_TEMPLATE_ID est obligatoire}"
```

Ces validations empêchent de poursuivre lorsque les paramètres sont absents ou vides.

Ne faites pas afficher le token dans les diagnostics.

Il faut également valider que l'identifiant du Job Template et l'URL correspondent à la cible attendue. Une mauvaise valeur peut conduire à lancer une automatisation dans le mauvais environnement.

## 19.5. Lire la réponse de lancement

Un appel réussi peut renvoyer un objet JSON contenant notamment les informations relatives au job lancé.

Il faut ensuite récupérer son identifiant et consulter son état avec l'endpoint approprié.

La procédure générale :

```text
Appel de lancement
       |
       v
Réponse HTTP et données JSON
       |
       v
Extraction de l'identifiant du job
       |
       v
Interrogation du statut
       |
       +---- En cours ----> Réessayer selon une politique définie
       |
       +---- Succès ------> Rapport de succès
       |
       +---- Échec -------> Diagnostic et traitement prévu
```

Évitez de faire un polling sans fin. Définissez une temporisation, une limite de temps et un comportement à l'expiration.

## 19.6. Exemple de contrôle de l'URL

```bash
case "$AWX_URL" in
    https://*)
        ;;
    *)
        printf 'Erreur : AWX_URL doit utiliser HTTPS.\n' >&2
        exit 2
        ;;
esac
```

Ce contrôle constitue un garde-fou élémentaire. Il ne garantit pas que le certificat est valide ou que le serveur est bien celui attendu.

N'utilisez pas une option de type `curl -k` pour contourner les erreurs TLS en production.


# 20. Tests et intégration continue

## 20.1. Valider la syntaxe des playbooks

```bash
ansible-playbook \
  -i inventories/lab/hosts.yml \
  playbooks/site.yml \
  --syntax-check
```

Cette validation détecte certaines erreurs de syntaxe et de structure. Elle ne garantit pas le succès de l'exécution réelle.

## 20.2. Tester un rôle

Un rôle devrait posséder des tests qui vérifient :

- l'état attendu après application ;
- le comportement si l'état est déjà correct ;
- les variables invalides ;
- les erreurs système ;
- les changements de configuration ;
- les cas particuliers liés aux distributions.

Molecule peut être utilisé pour tester les rôles dans un environnement contrôlé. Les pilotes et les dépendances doivent être compatibles avec la version du framework et l'environnement choisi.

## 20.3. Ansible Lint

```bash
ansible-lint
```

Ansible Lint analyse le contenu Ansible et propose des diagnostics selon ses règles.

Il est recommandé de l'intégrer dans un pipeline de validation de code, en contrôlant les règles et dérogations autorisées dans le projet.

Une dérogation doit être justifiée et documentée. Il ne faut pas désactiver un grand nombre de règles simplement pour obtenir un pipeline vert.

## 20.4. Contrôles recommandés avant publication

Une chaîne de validation peut suivre ce processus :

```text
Modification Git
      |
      v
Validation YAML
      |
      v
Syntax-check Ansible
      |
      v
Ansible Lint
      |
      v
Tests des rôles
      |
      v
Construction de l'environnement
      |
      v
Tests d'intégration en laboratoire
      |
      v
Revue humaine
      |
      v
Publication de la version approuvée
```

Les tests doivent être adaptés au risque des changements. Une modification de texte n'exige pas nécessairement les mêmes tests qu'un changement de règles réseau ou de configuration de sécurité.

## 20.5. Pipeline Git

Exemple de pipeline conceptuel, dont la syntaxe exacte dépend du moteur CI choisi :

```text
stage: validate
  - yaml-check
  - ansible-syntax-check
  - ansible-lint

stage: test
  - unit-tests
  - role-tests
  - lab-integration-tests

stage: build
  - build-execution-environment
  - vulnerability-scan
  - publish-artifact

stage: approval
  - review
  - release-approval

stage: deployment
  - launch-approved-AWX-workflow
  - monitor-result
  - publish-report
```

La chaîne doit conserver la traçabilité entre le commit source, les dépendances, l'image d'exécution et le job AWX lancé.

## 20.6. Ne pas utiliser la production comme banc de test

Les tests doivent utiliser des environnements isolés lorsque cela est possible.

Avant une modification à risque :

- vérifier les cibles visées ;
- réaliser un test de syntaxe ;
- examiner le résultat du check mode lorsqu'il est pertinent ;
- tester le cas nominal ;
- tester au moins un cas d'erreur ;
- établir la procédure de restauration ;
- prévoir une fenêtre d'intervention si nécessaire.

Le check mode n'est pas une garantie de sécurité. Il doit être combiné avec la revue et des tests adaptés.


# 21. Fiabilité, capacité et performances

## 21.1. Comprendre la parallélisation

Ansible peut exécuter des tâches sur plusieurs hôtes simultanément, dans la limite des paramètres de parallélisation et de la stratégie utilisée.

Une hausse du niveau de parallélisme ne signifie pas systématiquement que le traitement sera plus rapide. Elle peut aussi augmenter :

- la charge du contrôleur ;
- le nombre de connexions SSH ;
- la pression sur les services distants ;
- la consommation mémoire ;
- le nombre de requêtes vers une API ;
- la contention sur les systèmes de stockage.

## 21.2. Régler `forks`

Le paramètre `forks` définit une limite de parallélisme pour certaines exécutions Ansible.

Le nombre adapté dépend notamment du nombre de cibles, des ressources disponibles et de la capacité des systèmes gérés.

Commencez par mesurer le comportement du playbook avant de modifier ce paramètre.

Un inventaire de plusieurs milliers de machines peut nécessiter une architecture différente d'un playbook exécuté sur une dizaine de serveurs.

## 21.3. Job slicing

AWX peut proposer le découpage d'un job en plusieurs parties pour certaines configurations et versions.

Cela permet de répartir une charge importante, mais ajoute des contraintes sur le nombre de jobs, la synchronisation des tâches et les résultats.

Certaines interactions entre job slicing, inventaires et limites peuvent provoquer des résultats inattendus.

Testez le comportement exact de la version AWX retenue avant d'utiliser cette fonction sur un parc critique.

## 21.4. Tâches asynchrones

Ansible propose des mécanismes d'exécution asynchrone et de polling pour certaines commandes longues.

Le choix dépend du comportement de la commande, de la durée attendue et du besoin de collecter son résultat.

Une tâche longue doit avoir une stratégie explicite de délai, de statut et d'arrêt. Il ne faut pas confondre un job qui a été lancé en arrière-plan avec un traitement qui s'est terminé avec succès.


# 22. Dépannage avancé

## 22.1. Le playbook fonctionne localement, mais échoue dans AWX

Causes possibles :

- mauvais inventaire ;
- mauvais credential ;
- dépendance absente de l'Execution Environment ;
- version différente d'Ansible ;
- environnement Python différent ;
- variable définie uniquement sur le poste de développement ;
- mauvais chemin dans le projet ;
- accès réseau différent depuis le nœud d'exécution.

Méthode de diagnostic :

1. identifier précisément le job et son environnement d'exécution ;
2. examiner la version d'Ansible et les dépendances ;
3. confirmer les sources de variables ;
4. vérifier l'inventaire et les credentials autorisés ;
5. contrôler la connectivité depuis le contexte du job ;
6. examiner les sorties du job sans exposer de secrets.

## 22.2. Une variable vaut une autre valeur que prévu

Vérifiez :

- ses valeurs par défaut ;
- les variables de groupe et d'hôte ;
- les variables du playbook ;
- les variables liées au rôle ;
- les extra vars de lancement ;
- les valeurs définies par un Survey ;
- les éventuels imports et inclusions.

Évitez de résoudre le problème en dupliquant une autre valeur à un nouvel emplacement. Identifiez d'abord la source qui prend réellement le dessus.

## 22.3. Le service n'a pas redémarré

Vérifiez :

- si la tâche de configuration a réellement signalé un changement ;
- si le handler a été notifié ;
- si une erreur a interrompu le play ;
- si le handler a été exécuté ;
- si le gestionnaire de services accepte l'opération ;
- si le service est réellement opérationnel après le redémarrage.

Un état `changed` n'est pas équivalent à une preuve de bon fonctionnement métier.

## 22.4. L'inventaire AWX est vide ou ancien

Vérifiez :

- l'état de la synchronisation ;
- les droits sur la source ;
- la configuration du plugin ;
- les credentials ;
- les changements de structure de la source ;
- les erreurs de connexion ;
- les journaux du processus de mise à jour.

Ne poursuivez pas un déploiement critique en supposant qu'un inventaire dynamique est à jour sans vérification.

## 22.5. L'Operator est bloqué

Examinez :

```bash
kubectl get awx -n automation
kubectl get pods -n automation
kubectl get pvc -n automation
kubectl get events -n automation --sort-by=.metadata.creationTimestamp
```

Puis contrôlez les journaux des composants pertinents :

```bash
kubectl logs deployment/awx-operator-controller-manager \
  -n automation \
  -c awx-manager
```

Adaptez les noms des ressources à l'installation effective.

Des problèmes de stockage, de ressources, d'accès à une image, de configuration ou de compatibilité peuvent empêcher l'instance de devenir opérationnelle.

Ne supprimez pas immédiatement les volumes ou ressources de base de données : vérifiez d'abord les conséquences et l'existence de sauvegardes restaurables.


# 23. TP guidés

Les TP suivants constituent un parcours de mise en pratique. Ils supposent l'utilisation d'un laboratoire ou d'environnements dont vous êtes autorisé à administrer les cibles.

## TP 1 — Créer un rôle Linux réutilisable

### Objectif

Créer un rôle `baseline_linux` qui installe un paquet donné et vérifie que le service associé est présent.

### Arborescence

```text
roles/baseline_linux/
├── defaults/main.yml
├── tasks/main.yml
└── handlers/main.yml
```

### `defaults/main.yml`

```yaml
baseline_package_name: chrony
baseline_service_name: chronyd
baseline_service_enabled: true
baseline_service_state: started
```

Les noms de paquet et de service varient selon les distributions. Ce rôle de démonstration doit être adapté et testé sur les systèmes réellement ciblés.

### `tasks/main.yml`

```yaml
- name: Valider les paramètres
  ansible.builtin.assert:
    that:
      - baseline_package_name | length > 0
      - baseline_service_name | length > 0
      - baseline_service_enabled is boolean
      - baseline_service_state in ['started', 'stopped']
    fail_msg: "Les paramètres du rôle baseline_linux sont invalides."

- name: Installer le paquet
  ansible.builtin.package:
    name: "{{ baseline_package_name }}"
    state: present

- name: Gérer le service
  ansible.builtin.service:
    name: "{{ baseline_service_name }}"
    enabled: "{{ baseline_service_enabled }}"
    state: "{{ baseline_service_state }}"
```

### Playbook de test

```yaml
- name: Tester le rôle baseline_linux
  hosts: lab_linux
  become: true

  roles:
    - baseline_linux
```

### Tests

1. exécuter le playbook sur une machine de laboratoire ;
2. le relancer et vérifier que le système n'est plus modifié si l'état voulu est déjà atteint ;
3. utiliser un paramètre invalide et vérifier le diagnostic ;
4. tester le rôle sur les familles de distributions prises en charge.


## TP 2 — Concevoir un déploiement progressif

### Objectif

Déployer une configuration sur un lot de serveurs à la fois, puis vérifier le service.

### Playbook

```yaml
- name: Déployer progressivement la configuration
  hosts: lab_webservers
  become: true
  serial: 2
  max_fail_percentage: 0

  tasks:
    - name: Préparer le répertoire de configuration
      ansible.builtin.file:
        path: /etc/application
        state: directory
        owner: root
        group: root
        mode: "0755"

    - name: Déployer la configuration
      ansible.builtin.template:
        src: application.conf.j2
        dest: /etc/application/application.conf
        owner: root
        group: root
        mode: "0644"
      notify: Redémarrer application

    - name: Vérifier le service
      ansible.builtin.service:
        name: application
        state: started

  handlers:
    - name: Redémarrer application
      ansible.builtin.service:
        name: application
        state: restarted
```

Cet exemple suppose que l'application est installée et que le service existe. La configuration doit correspondre au format réel de l'application.

Le comportement du déploiement doit être testé avec un petit nombre de machines avant une utilisation en production.


## TP 3 — Préparer un workflow AWX

### Objectif

Mettre en place un processus structuré de validation avant le déploiement.

### Ressources à créer dans AWX

Créer les ressources suivantes en respectant les permissions de votre plateforme :

1. un projet lié au dépôt de playbooks ;
2. un inventaire de laboratoire ;
3. un credential SSH adapté ;
4. un Execution Environment homologué ;
5. un Job Template de validation ;
6. un Job Template de déploiement ;
7. un Job Template de vérification post-déploiement ;
8. un Workflow Job Template reliant les étapes.

### Logique du workflow

```text
Validation
    |
    +-- Échec --> Notification d'erreur
    |
    +-- Succès --> Déploiement
                    |
                    +-- Échec --> Diagnostic
                    |
                    +-- Succès --> Vérification
                                      |
                                      +-- Échec --> Escalade
                                      |
                                      +-- Succès --> Notification finale
```

### Critères de réussite

- un échec de validation ne doit pas déclencher le déploiement ;
- les credentials doivent être attribués avec les permissions nécessaires, sans exposition inutile ;
- les cibles doivent être limitées à l'inventaire approuvé ;
- un succès du job de déploiement ne doit pas être confondu avec un succès de vérification ;
- les résultats doivent rester consultables par les personnes autorisées.


# 24. Projet final — Industrialiser un déploiement avec Ansible et AWX

## 24.1. Contexte

Vous êtes responsable d'une plateforme d'automatisation utilisée pour maintenir plusieurs serveurs Linux.

L'entreprise souhaite un processus reproductible qui permette de valider une configuration, la déployer progressivement sur une cible de test, effectuer des contrôles puis autoriser sa promotion vers la production.

Le système doit être contrôlable, traçable et conçu pour limiter les risques.

## 24.2. Cahier des charges

Le projet doit inclure :

- un dépôt Git clairement organisé ;
- des rôles réutilisables ;
- des paramètres validés ;
- des inventaires séparés par environnement ;
- une gestion sécurisée des secrets ;
- un Execution Environment versionné ;
- des tests syntaxiques et de qualité ;
- des modèles de jobs AWX ;
- un workflow reliant validation, déploiement et vérification ;
- une approbation avant l'étape critique ;
- des notifications d'échec ;
- une procédure de reprise ou de restauration ;
- une documentation des permissions et des codes de retour.

## 24.3. Architecture cible

```text
                   DÉVELOPPEUR
                       |
                       v
                      GIT
                       |
                       v
             Validation et tests CI
                       |
                       v
            Build Execution Environment
                       |
                       v
               Image versionnée
                       |
                       v
                       AWX
                       |
                       v
                Workflow de release
                       |
           +-----------+-----------+
           |                       |
           v                       v
       Validation              Précontrôles
           |                       |
           +-----------+-----------+
                       |
                       v
             Déploiement staging
                       |
                       v
           Vérification fonctionnelle
                       |
                       v
              Approbation humaine
                       |
                       v
             Déploiement production
                       |
                       v
              Vérification finale
                       |
                       v
             Rapport et traçabilité
```

## 24.4. Livrables attendus

Le projet doit contenir au minimum :

- `README.md` décrivant le but, les prérequis et la procédure d'utilisation ;
- `requirements.yml` pour les collections ;
- les rôles et leurs valeurs par défaut ;
- les playbooks de validation et de déploiement ;
- une définition d'environnement d'exécution ;
- les tests automatisés ;
- une procédure de configuration des ressources AWX ;
- une stratégie de sauvegarde et de retour arrière ;
- une grille de vérification des permissions ;
- une procédure de diagnostic en cas d'échec.

## 24.5. Stratégie de réalisation

### Étape 1 — Concevoir l'interface

Définissez les paramètres que le déploiement doit accepter.

Pour chacun, précisez :

- son type ;
- sa valeur par défaut ;
- les valeurs acceptées ;
- les environnements dans lesquels il s'applique ;
- son éventuelle sensibilité ;
- la conséquence d'une valeur incorrecte.

### Étape 2 — Construire les rôles

Séparez l'installation, la configuration, le contrôle de santé et le déploiement.

Ajoutez une validation des paramètres et assurez-vous que le deuxième lancement du playbook ne déclenche pas des changements injustifiés.

### Étape 3 — Établir les tests

Incluez les scénarios d'échec, pas uniquement les cas de réussite.

Un test doit permettre de savoir si la sortie, le statut et les effets du playbook correspondent à ce qui est attendu.

### Étape 4 — Construire l'environnement d'exécution

Définissez les versions des composants et vérifiez leur compatibilité.

Publiez une image approuvée et associez-la au modèle de job AWX.

### Étape 5 — Configurer AWX

Créez les projets, inventaires, credentials, Execution Environments et Job Templates.

Vérifiez que les permissions des équipes sont limitées à leurs responsabilités.

### Étape 6 — Construire le workflow

Reliez les étapes par les états de succès et d'échec appropriés.

Ajoutez les validations et l'approbation humaine avant les opérations critiques.

### Étape 7 — Simuler une panne

Provoquez des situations contrôlées en laboratoire :

- paramètre invalide ;
- credential non autorisé ;
- service qui ne répond pas ;
- étape de validation qui échoue ;
- problème lors de la génération du rapport.

Vérifiez que le workflow ne continue pas de façon dangereuse.

### Étape 8 — Documenter la restauration

Décrivez comment revenir à l'état précédent, quelles ressources sont restaurées, qui peut lancer l'opération et comment vérifier le résultat.

Une procédure de restauration doit être testée. Sa simple présence dans le README ne garantit pas qu'elle fonctionne.

## 24.6. Critères de validation

Le projet est validé si :

- les playbooks passent les contrôles de syntaxe ;
- les erreurs de lint sont traitées ou justifiées ;
- les rôles possèdent des interfaces documentées ;
- les paramètres invalides sont rejetés ;
- la configuration se comporte de façon idempotente ;
- le workflow n'exécute pas les étapes critiques après une validation échouée ;
- les credentials sont protégés ;
- les exécutions sont traçables ;
- les procédures de reprise sont documentées ;
- les tests démontrent les comportements attendus.


# 25. Bonnes pratiques de production

Avant de mettre en production une automatisation, vérifiez systématiquement les points suivants.

## Code

- Les playbooks utilisent les modules appropriés.
- Les noms de modules sont pleinement qualifiés lorsque cela est pertinent.
- Les variables possèdent des responsabilités claires.
- Les secrets ne sont pas codés en dur.
- Les erreurs sont détectées et traitées.
- Les tâches importantes sont idempotentes.
- Les dépendances sont explicites.

## Exécution

- Les cibles sont limitées au périmètre approuvé.
- Le credential utilisé est approprié.
- L'environnement d'exécution est versionné.
- Les dépendances sont compatibles.
- Les changements critiques sont testés.
- La stratégie de parallélisation est adaptée.
- Les résultats sont contrôlés après le déploiement.

## AWX

- Les permissions correspondent aux rôles des utilisateurs.
- Les modèles de jobs exposent uniquement les paramètres nécessaires.
- Les extra vars et Surveys sont validés.
- Les workflows sont testés avec leurs chemins d'échec.
- Les credentials ne sont pas exposés dans les sorties.
- Les tâches planifiées sont suivies.
- Les sauvegardes et procédures de restauration sont vérifiées.

## Gouvernance

- Les changements de playbooks passent par une revue.
- Les images d'exécution sont approuvées.
- Les versions d'Ansible et des collections sont maîtrisées.
- Les exceptions sont documentées.
- Les résultats des tests et des déploiements sont conservés selon une politique adaptée.
- Les responsabilités de maintenance sont clairement attribuées.


# 26. Grille de compétences expertes

Cochez chaque compétence uniquement après l'avoir démontrée dans un environnement de test.

## Architecture Ansible

- [ ] Je sais concevoir un dépôt multi-environnements.
- [ ] Je sais maîtriser les variables et leurs priorités.
- [ ] Je sais concevoir des rôles avec des interfaces documentées.
- [ ] Je sais organiser des collections versionnées.
- [ ] Je sais choisir entre imports statiques et inclusions dynamiques.
- [ ] Je sais créer des playbooks idempotents et testables.
- [ ] Je sais traiter les échecs avec des stratégies adaptées.
- [ ] Je sais organiser des déploiements progressifs.

## Exécution et dépendances

- [ ] Je sais définir les dépendances d'un Execution Environment.
- [ ] Je sais construire et versionner une image.
- [ ] Je sais vérifier les compatibilités entre les composants.
- [ ] Je sais diagnostiquer une différence entre exécution locale et AWX.
- [ ] Je sais employer check mode et diff mode en comprenant leurs limites.
- [ ] Je sais concevoir une stratégie de test et de promotion.

## AWX

- [ ] Je sais distinguer projet, inventaire, credential, job template et workflow.
- [ ] Je sais créer des modèles de jobs avec des paramètres contrôlés.
- [ ] Je sais construire un workflow avec des transitions de succès et d'échec.
- [ ] Je sais intégrer une approbation humaine lorsque cela est nécessaire.
- [ ] Je sais définir des permissions RBAC selon les responsabilités.
- [ ] Je sais sécuriser l'utilisation des credentials.
- [ ] Je sais piloter un lancement par API.
- [ ] Je sais suivre l'exécution d'un job et vérifier son résultat final.

## Exploitation et sécurité

- [ ] Je sais déployer AWX avec l'Operator dans un environnement compatible.
- [ ] Je sais examiner les ressources Kubernetes utiles au diagnostic.
- [ ] Je sais concevoir des sauvegardes et tester la restauration.
- [ ] Je sais éviter l'exposition des secrets dans les journaux.
- [ ] Je sais dimensionner une exécution multi-hôtes.
- [ ] Je sais concevoir des tests de défaillance.
- [ ] Je sais documenter les procédures de reprise.


# 27. Fiche de révision

## Validation d'un playbook

```bash
ansible-playbook -i inventories/lab/hosts.yml \
  playbooks/site.yml --syntax-check
```

## Simulation

```bash
ansible-playbook -i inventories/lab/hosts.yml \
  playbooks/site.yml --check --diff
```

Le résultat doit être interprété en tenant compte des limites du check mode et de la sensibilité des données exposées par le diff.

## Analyse de qualité

```bash
ansible-lint
```

## Inventaire

```bash
ansible-inventory -i inventories/lab/hosts.yml --list
```

## Dépendances

```bash
ansible-galaxy collection install -r requirements.yml
ansible-galaxy collection list
ansible --version
```

## Analyse des statuts

```yaml
- name: Vérifier le service
  ansible.builtin.command:
    cmd: /usr/local/bin/service-health
  register: result
  changed_when: false
  failed_when: result.rc != 0
```

## Déploiement progressif

```yaml
- name: Déploiement contrôlé
  hosts: webservers
  serial: 2
  max_fail_percentage: 0
```

## Protections essentielles

- Ne jamais faire confiance aux extra vars sans les valider.
- Ne pas utiliser `shell` lorsqu'un module Ansible adapté suffit.
- Ne pas considérer un check mode comme une preuve complète de réussite.
- Ne pas supposer qu'un lancement AWX réussi signifie que le déploiement métier est réussi.
- Ne pas stocker de secrets dans Git.
- Ne pas accorder à tous les opérateurs un accès global à tous les credentials.
- Ne pas lancer un déploiement critique sans stratégie de restauration.
- Ne pas modifier un environnement d'exécution de production sans vérifier les versions et les dépendances.


# 28. Glossaire

**Ansible Core** : moteur de base d'Ansible, comprenant les mécanismes de lecture des inventaires, d'exécution des playbooks et les éléments fondamentaux du système de modules et plugins.

**AWX** : plateforme communautaire de pilotage, d'orchestration et de traçabilité des automatisations Ansible.

**Collection** : format de distribution de contenu Ansible comprenant notamment des rôles, modules, plugins et documentation.

**Credential** : ressource contenant les informations nécessaires à une authentification ou à un accès à un service.

**Execution Environment** : environnement d'exécution versionné regroupant les dépendances nécessaires à Ansible et au contenu d'automatisation.

**FQCN** : nom pleinement qualifié désignant le namespace, la collection et le contenu Ansible sélectionné.

**Handler** : tâche exécutée en réaction à une notification lorsque le mécanisme d'exécution le prévoit.

**Idempotence** : propriété permettant de répéter une opération sans créer de modifications supplémentaires lorsque l'état souhaité est déjà atteint.

**Inventaire dynamique** : inventaire alimenté depuis une source externe par un plugin ou un mécanisme adapté.

**Job Template** : configuration réutilisable définissant les ressources et les paramètres d'un lancement de job AWX.

**Molecule** : outil de test et de validation de rôles Ansible selon une configuration adaptée.

**Playbook** : fichier YAML décrivant un ou plusieurs plays et leurs tâches d'automatisation.

**RBAC** : contrôle d'accès basé sur les rôles et les permissions associées.

**Role** : unité de réutilisation d'Ansible permettant de regrouper tâches, variables, handlers, fichiers, modèles et métadonnées.

**Survey** : formulaire de paramètres associé à un modèle ou workflow AWX selon les fonctionnalités disponibles, permettant de collecter des valeurs au moment du lancement.

**Workflow Job Template** : modèle AWX qui orchestre une séquence de ressources et de jobs en fonction des transitions configurées.

**Operator Kubernetes** : logiciel qui gère le cycle de vie d'une application au moyen des mécanismes Kubernetes et de ressources personnalisées.

**Ansible Vault** : mécanisme permettant de chiffrer des données sensibles utilisées par Ansible.

**Check mode** : mode de simulation qui estime certaines modifications sans les appliquer, sous réserve des capacités des modules et des tâches.

**Diff mode** : mode d'affichage de différences avant/après pour les opérations prises en charge, à utiliser en tenant compte des données sensibles.

**Serial** : paramètre de playbook qui contrôle les lots d'hôtes traités successivement.

**Job slicing** : mécanisme de répartition d'un job sur plusieurs portions pour certaines configurations AWX et certains volumes d'exécution.


# 29. Documentation officielle

Les références suivantes permettent d'approfondir les fonctionnalités utilisées dans ce cours. Vérifiez toujours que la documentation correspond aux versions réellement installées.

## Documentation Ansible

- Documentation générale :  
  https://docs.ansible.com/projects/ansible/latest/

- Guide officiel des playbooks :  
  https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html

- Gestion des erreurs :  
  https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html

- Modules et plugins :  
  https://docs.ansible.com/projects/ansible/latest/plugins/plugins.html

- Collections :  
  https://docs.ansible.com/projects/ansible/latest/user_guide/collections_using.html

- Ansible Vault :  
  https://docs.ansible.com/projects/ansible/latest/vault_guide/index.html

- Inventaires :  
  https://docs.ansible.com/projects/ansible/latest/inventory_guide/index.html

- Vérification et exécution des playbooks :  
  https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html

- Documentation des paramètres de configuration :  
  https://docs.ansible.com/projects/ansible/latest/reference_appendices/config.html

## Documentation AWX

- Documentation officielle AWX :  
  https://docs.ansible.com/projects/awx/en/latest/

- Guide d'utilisation :  
  https://docs.ansible.com/projects/awx/en/latest/userguide/

- Modèles de workflows :  
  https://docs.ansible.com/projects/awx/en/latest/userguide/workflow_templates.html

- Référence de l'API :  
  https://docs.ansible.com/projects/awx/en/latest/rest_api/

## Déploiement AWX

- AWX Operator :  
  https://docs.ansible.com/projects/awx-operator/en/latest/

- Guide officiel de l'Operator :  
  https://ansible.readthedocs.io/projects/awx-operator/

## Qualité et tests

- Ansible Lint :  
  https://ansible.readthedocs.io/projects/lint/

- Molecule :  
  https://ansible.readthedocs.io/projects/molecule/

- Tests de collections et `ansible-test` :  
  https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections_testing.html


# Conclusion

Ansible avancé et AWX représentent une évolution de l'automatisation, du playbook individuel vers une véritable plateforme opérationnelle.

La maîtrise du niveau expert exige de connaître les mécanismes internes d'Ansible, les règles de gestion des variables, les stratégies de déploiement multi-hôtes, les environnements d'exécution, les dépendances et les mécanismes de reprise. Elle exige aussi de comprendre AWX comme une plateforme de gouvernance et d'orchestration : les projets, inventaires, credentials, Job Templates, workflows, permissions, API et ressources Kubernetes doivent fonctionner ensemble.

Le critère de réussite n'est pas simplement qu'un playbook s'exécute sans erreur. Il faut pouvoir expliquer ce qu'il modifie, sur quelles cibles il agit, comment il gère les erreurs, quels secrets il utilise, comment son résultat est validé et comment restaurer un état précédent si le déploiement échoue.

**Validation du niveau expert :** vous êtes capable de concevoir une automatisation versionnée, testable et reproductible, de la déployer à travers AWX avec les permissions adaptées, d'orchestrer les étapes de validation et de promotion, et de démontrer son comportement face aux cas d'échec dans un environnement de laboratoire.