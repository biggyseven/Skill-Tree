# Ansible et automatisation de configuration — Débutant

> **Mise en contexte.** Une équipe administre huit serveurs Linux. Installer manuellement le même paquet, créer les mêmes comptes et modifier huit fichiers de configuration prend du temps et produit des écarts. Ansible permet de décrire l’état attendu une fois, puis de l’appliquer de manière contrôlée à plusieurs machines.

## Objectifs d’apprentissage

À la fin du cours, tu dois pouvoir expliquer le rôle d’Ansible, préparer un inventaire, écrire et lancer un playbook simple, utiliser les variables, comprendre l’idempotence et diagnostiquer un échec sans appliquer aveuglément des changements en production.

## Prérequis

- Savoir utiliser un terminal Linux et reconnaître les chemins de fichiers.
- Comprendre les bases de SSH, des utilisateurs et des permissions.
- Connaître les notions de paquet, de service et de fichier de configuration.
- Avoir les bases du YAML : indentation, listes et paires clé-valeur.

## 1. À quoi sert Ansible ?

Ansible est un outil d’automatisation piloté par un nœud de contrôle. Il se connecte généralement aux hôtes gérés par SSH et y exécute des modules. Sur les systèmes courants, il ne nécessite pas d’agent Ansible permanent sur chaque cible.

Quelques responsabilités à distinguer :

- **Provisionner** : créer une machine virtuelle, un réseau ou une instance auprès d’un fournisseur. Terraform est souvent utilisé pour cette étape.
- **Configurer** : installer des paquets, créer des comptes, déployer un fichier et gérer des services. Ansible est adapté à cette étape.
- **Déployer une application** : installer une version applicative, appliquer une configuration et vérifier la disponibilité.
- **Orchestrer** : enchaîner des opérations avec un ordre, des limites et des conditions explicites.

Ansible ne remplace pas une politique de changement. Il rend l’exécution reproductible, mais il faut définir le périmètre, la preuve de réussite et la procédure de retour arrière.

## 2. Architecture et vocabulaire

~~~text
Poste de contrôle
  ├── inventaire : quels hôtes gérer ?
  ├── playbook : quel état doit être atteint ?
  ├── variables : quels paramètres utiliser ?
  └── connexion SSH ───────────> serveurs Linux
                                  ├── modules
                                  └── état réel
~~~

- **Inventaire** : liste ou groupes d’hôtes.
- **Playbook** : fichier YAML contenant un ou plusieurs plays.
- **Play** : associe un groupe d’hôtes à une liste de tâches.
- **Task** : action qui appelle un module.
- **Module** : opération spécialisée, par exemple gérer un paquet, un fichier ou un service.
- **Handler** : tâche déclenchée lorsqu’une autre tâche signale un changement.
- **Facts** : informations collectées sur l’hôte, par exemple le système d’exploitation.
- **Rôle** : structure réutilisable regroupant tâches, variables, fichiers, modèles et handlers.

## 3. Installer et vérifier l’outil

Sur une machine de laboratoire Debian ou Ubuntu, une installation via le gestionnaire de paquets ou un environnement Python isolé est préférable à une modification non maîtrisée de Python système. La méthode exacte dépend de la distribution et de la politique de l’équipe.

Vérifie ensuite l’installation :

~~~bash
ansible --version
ansible-playbook --version
~~~

Garde en tête que l’ordinateur de contrôle, les cibles et les environnements Python peuvent avoir des versions différentes. Note la version utilisée dans le dépôt ou le cahier de TP afin que le résultat soit reproductible.

## 4. Définir un inventaire

Crée un répertoire de travail, puis un fichier nommé inventory.ini :

~~~ini
[web]
web01 ansible_host=192.0.2.21
web02 ansible_host=192.0.2.22

[db]
db01 ansible_host=192.0.2.31

[linux:children]
web
db
~~~

Les adresses du bloc sont des adresses de documentation : remplace-les uniquement par celles de ton laboratoire. La clé ansible_host donne l’adresse de connexion. Le nom web01 reste un alias utilisable dans les commandes et les playbooks.

Teste l’inventaire :

~~~bash
ansible-inventory -i inventory.ini --graph
ansible all -i inventory.ini -m ping
~~~

Le module ping d’Ansible n’est pas l’équivalent du paquet ICMP : il vérifie surtout que la connexion et l’exécution du module fonctionnent. Si le test échoue, vérifie le réseau, la résolution du nom, le port SSH, l’utilisateur distant, la clé, les permissions de cette clé et les droits sudo.

## 5. Écrire un premier playbook

Crée site.yml :

~~~yaml
- name: Préparer les serveurs web
  hosts: web
  become: true
  tasks:
    - name: Installer Nginx
      ansible.builtin.package:
        name: nginx
        state: present

    - name: Vérifier que Nginx est démarré
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true
~~~

L’indentation fait partie de la syntaxe YAML. Les valeurs de hosts, become et tasks sont des paramètres du play. Les noms des tâches décrivent l’intention et rendent la sortie compréhensible.

Avant l’exécution réelle, valide le fichier et inspecte le plan :

~~~bash
ansible-playbook -i inventory.ini --syntax-check site.yml
ansible-playbook -i inventory.ini --list-hosts site.yml
ansible-playbook -i inventory.ini --check --diff site.yml
~~~

Le mode check est une simulation utile, mais pas une preuve parfaite : certains modules ne simulent pas chaque effet et certaines tâches conditionnelles ne se comportent pas exactement comme en exécution réelle. N’exécute jamais un playbook sur un parc que tu n’as pas confirmé avec list-hosts.

## 6. Comprendre l’idempotence

Une tâche idempotente décrit un état plutôt qu’une action à répéter. state: present signifie que le paquet doit être installé, pas « lancer l’installation à chaque passage ». Après le premier passage, une deuxième exécution correctement conçue devrait généralement signaler peu ou pas de changements.

L’idempotence réduit les différences entre serveurs. Elle n’empêche toutefois pas tous les effets de bord : un script arbitraire, une commande non conditionnée ou une tâche qui redémarre toujours un service peut produire des changements inutiles.

Compare les sorties de deux exécutions du playbook. Si le second passage modifie encore les mêmes ressources, demande-toi si la tâche décrit bien un état cible et si un module spécialisé existe.

## 7. Variables et modèles

Place les valeurs réutilisables dans des variables plutôt que de dupliquer les mêmes chaînes dans plusieurs tâches.

~~~yaml
- name: Préparer une page de test
  hosts: web
  become: true
  vars:
    page_title: "Serveur de laboratoire"
  tasks:
    - name: Déployer la page
      ansible.builtin.copy:
        dest: /var/www/html/index.html
        content: "<h1>{{ page_title }}</h1>\n"
        owner: root
        group: root
        mode: "0644"
~~~

Les doubles accolades indiquent une expression Jinja dans une valeur prise en charge. copy suffit pour un contenu fixe. Le module template devient utile lorsque le fichier comporte plusieurs valeurs, des conditions ou une structure plus élaborée. Les permissions doivent être explicites et adaptées au contenu.

Les variables peuvent venir du playbook, de l’inventaire, de fichiers dédiés, de la ligne de commande ou de systèmes de secrets. La priorité entre sources peut être complexe ; évite de définir la même variable à de nombreux endroits sans raison documentée.

## 8. Élévation de privilèges et secrets

become: true demande l’élévation de privilèges pour les tâches concernées. Il ne faut pas activer cette option partout par réflexe. Applique le moindre privilège : un compte de déploiement, des autorisations SSH contrôlées et une élévation uniquement lorsque c’est nécessaire.

Ne place jamais un mot de passe ou une clé privée en clair dans l’inventaire, le playbook, les journaux ou Git. Pour les secrets, utilise un coffre dédié ou Ansible Vault, limite les personnes autorisées à déchiffrer les valeurs et protège les sauvegardes. no_log: true peut masquer la sortie d’une tâche sensible, mais ne transforme pas une mauvaise gestion du secret en bonne pratique.

## 9. TP guidé : préparer deux serveurs web

**Situation :** deux machines de laboratoire doivent disposer de Nginx et d’une page d’accueil cohérente.

1. Déclare les deux hôtes dans le groupe web.
2. Vérifie l’inventaire et la connexion avec le module ansible.builtin.ping.
3. Écris le playbook d’installation et de démarrage.
4. Utilise le mode syntaxe, puis list-hosts, puis check et diff.
5. Une fois le périmètre confirmé, exécute le playbook sur les seules machines de laboratoire.
6. Relance-le et observe la différence entre les deux exécutions.
7. Vérifie le service depuis chaque hôte et consigne l’état final.

**Critères de réussite :** les deux machines sont ciblées, Nginx est installé et activé au démarrage, aucune clé secrète n’est stockée dans Git, et la deuxième exécution ne répète pas inutilement les changements.

## 10. Exercices corrigés

**Exercice 1.** Quelle différence existe entre un inventaire et un playbook ?

**Correction :** l’inventaire identifie les hôtes et leurs groupes ; le playbook décrit les états et opérations à appliquer sur les hôtes sélectionnés.

**Exercice 2.** Pourquoi le module ping ne prouve-t-il pas que l’application web est disponible ?

**Correction :** il confirme la connectivité Ansible et la capacité d’exécuter le module. Il ne valide ni le service HTTP, ni le contenu servi, ni les dépendances applicatives.

**Exercice 3.** Quelle est la meilleure approche pour installer un paquet déjà présent ?

**Correction :** décrire state: present avec le module package. Ansible peut alors comparer l’état réel et l’état attendu, au lieu de lancer systématiquement une commande shell.

**Exercice 4.** Est-il prudent de lancer immédiatement un playbook sur all ?

**Correction :** non. Il faut d’abord examiner les hôtes avec list-hosts, valider le YAML, effectuer les vérifications appropriées puis exécuter sur un groupe limité.

## Défi final corrigé

Une équipe veut créer un compte technique, installer un paquet de supervision et déployer un fichier de configuration sur deux machines Linux.

**Livrable attendu :** un inventaire avec un groupe monitoring, un playbook idempotent, une variable pour le nom du paquet, une tâche de fichier avec propriétaire et permissions explicites, et un handler pour redémarrer le service uniquement quand sa configuration change.

**Démarche de correction :** utiliser ansible.builtin.user pour le compte, ansible.builtin.package pour le paquet, ansible.builtin.template ou copy pour le fichier, et ansible.builtin.service dans un handler notifié par la tâche de configuration. Vérifier le périmètre, les permissions, l’absence de secret en clair, puis exécuter le playbook deux fois. Le second passage doit être stable ; un changement de configuration doit déclencher le handler.

## À retenir

Ansible automatise des états déclaratifs à travers un inventaire, des playbooks et des modules. La qualité ne se mesure pas au nombre de commandes exécutées, mais à la reproductibilité, à l’idempotence, au périmètre maîtrisé, à la sécurité et à la capacité de vérifier le résultat.