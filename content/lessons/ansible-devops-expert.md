# Automatisation Ansible à grande échelle — Expert

> **Mise en contexte.** Une plateforme exploite des centaines de serveurs répartis entre plusieurs environnements. Les mêmes playbooks ne peuvent pas être lancés sans contrôle partout : une erreur de groupe, un secret expiré ou un redémarrage simultané peut provoquer une panne. À ce niveau, le défi consiste à gouverner l’automatisation autant qu’à écrire des tâches.

## Objectifs d’apprentissage

À la fin de ce cours, tu dois savoir structurer une collection de rôles, contrôler l’exécution sur un grand parc, tester les rôles, protéger les secrets, gérer les environnements d’exécution et intégrer Ansible dans une chaîne de livraison avec audit et mécanismes de retour arrière.

## Prérequis

Maîtriser les inventaires, les playbooks, les variables, les templates, les handlers, les rôles, SSH, Git et les principes de CI/CD. Ce niveau complète l’intermédiaire ; il ne s’agit pas de remplacer la maîtrise des bases par une collection de commandes avancées.

## 1. Concevoir une architecture d’automatisation

Sépare les responsabilités. Terraform ou un outil de provisionnement crée les ressources ; Ansible configure le système ; un pipeline valide les changements et une plateforme d’exécution gouverne qui peut les lancer.

~~~text
Pull request
   |
   +--> lint YAML / ansible-lint
   +--> tests unitaires et tests de rôles
   +--> validation des variables et des secrets
   |
Artefact versionné
   |
Plan d'exécution / approbation
   |
Contrôleur d'automatisation
   |
Groupes limités --> lots d'hôtes --> vérifications post-déploiement
~~~

Le playbook n’est qu’un élément de la chaîne. Les inventaires, rôles, versions des collections, identités d’exécution, contrôles d’approbation et journaux d’audit doivent aussi être versionnés ou gérés avec des règles explicites.

## 2. Rôles et collections réutilisables

Un rôle doit avoir une interface compréhensible : variables d’entrée, état produit, plateformes supportées et prérequis. Une structure classique comprend tasks/main.yml, handlers/main.yml, defaults/main.yml, templates/, files/ et éventuellement meta/main.yml.

~~~text
roles/
  baseline_linux/
    defaults/main.yml
    tasks/main.yml
    handlers/main.yml
    templates/
    meta/main.yml
  reverse_proxy/
    defaults/main.yml
    tasks/main.yml
    handlers/main.yml
collections/requirements.yml
site.yml
~~~

Place les valeurs par défaut raisonnables dans defaults, pas dans des variables ayant une priorité très élevée. Évite de cacher les paramètres importants dans des valeurs magiques. Documente les variables obligatoires, les valeurs autorisées et les effets de chaque rôle.

Les collections regroupent rôles, modules, plugins et autres composants distribuables sous un espace de noms. Épingle des versions testées dans le fichier de dépendances :

~~~yaml
collections:
  - name: ansible.posix
    version: "2.0.0"
~~~

La version choisie doit être validée avec la version d’Ansible et les plateformes cibles de ton organisation. En CI, installe les dépendances déclarées au lieu de dépendre implicitement de ce qui est présent sur l’agent.

## 3. Maîtriser le risque d’exécution

À grande échelle, l’idempotence ne suffit pas. Un playbook idempotent peut quand même redémarrer beaucoup de serveurs simultanément ou modifier le mauvais groupe.

- Utilise --list-hosts avant toute exécution sur un inventaire étendu.
- Limite les cibles par environnement ou par groupes clairement nommés.
- Utilise serial pour déployer par vagues et vérifier la santé entre les lots.
- Définis max_fail_percentage lorsque le comportement en cas d’échec partiel doit être explicite.
- Utilise any_errors_fatal uniquement lorsque l’arrêt global est réellement souhaité.
- Demande une approbation et une fenêtre de changement pour les opérations à fort impact.
- Prévois une vérification après changement et une procédure de retour arrière.

Exemple de déploiement progressif :

~~~yaml
- name: Déployer le proxy par lots
  hosts: reverse_proxies
  become: true
  serial: 2
  max_fail_percentage: 0
  tasks:
    - name: Déployer la configuration validée
      ansible.builtin.template:
        src: proxy.conf.j2
        dest: /etc/nginx/conf.d/proxy.conf
        owner: root
        group: root
        mode: "0644"
      notify: Recharger Nginx

    - name: Vérifier la configuration Nginx
      ansible.builtin.command: nginx -t
      changed_when: false
  handlers:
    - name: Recharger Nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded
~~~

L’exemple illustre une séquence, mais les handlers et leur ordre doivent être testés avec la plateforme cible. Pour des déploiements critiques, sépare souvent validation et activation : il est préférable d’exécuter explicitement les tests de configuration avant de recharger le service plutôt que de s’appuyer sur un enchaînement ambigu de handlers.

## 4. Variables, secrets et séparation des environnements

Les fichiers group_vars et host_vars permettent des paramètres propres aux environnements. Évite de mélanger des variables de laboratoire et de production dans une même source sans frontière explicite. La source de vérité des secrets devrait être un gestionnaire de secrets ou Ansible Vault, avec rotation, contrôle d’accès et journalisation.

~~~yaml
# Exemple de référence, non secret
monitoring_endpoint: "https://monitoring.example.invalid"
service_port: 8443
~~~

Ne versionne pas un secret chiffré sans politique de clés et de sauvegarde. Utilise des identifiants Vault maîtrisés, limite l’usage de vault-password-file, protège ce fichier et ne copie pas les secrets dans les journaux. no_log: true réduit le risque d’exposition dans la sortie Ansible, mais doit être utilisé de façon ciblée afin de ne pas rendre les diagnostics impossibles.

Prévois des validations de variables avant les tâches qui changent l’état. Une valeur de port en dehors de la plage attendue ou un nom d’environnement incorrect doit provoquer un échec précoce, compréhensible, avant toute modification.

## 5. Mode check, diff et limites des simulations

Le mode de vérification est un garde-fou utile :

~~~bash
ansible-playbook -i inventories/staging site.yml --syntax-check
ansible-playbook -i inventories/staging site.yml --list-hosts
ansible-playbook -i inventories/staging site.yml --check --diff
~~~

Mais --check n’est pas un moteur de plan complet comparable à tous les outils d’IaC. Certains modules ne prévoient pas les changements, et les tâches fondées sur les résultats d’une commande peuvent réagir différemment. Un contrôle de changement doit combiner la simulation, l’analyse de diff, les tests sur environnement représentatif et des vérifications après exécution.

## 6. Qualité automatisée : lint, tests et contrat de rôle

Utilise ansible-lint pour détecter de nombreuses erreurs de style ou de conception. Complète-le par des tests qui expriment le comportement attendu : paquet présent, fichier au bon emplacement, permissions correctes, service activé et absence de secret en sortie. Les tests Molecule sont fréquemment utilisés pour tester des rôles dans des environnements isolés ; la stratégie exacte dépend du système cible.

Exemple de pipeline :

~~~text
Commit
  -> format/lint
  -> tests de syntaxe
  -> tests de rôle en conteneur ou VM
  -> revue du diff
  -> publication de l'artefact versionné
  -> approbation
  -> déploiement par lots
  -> vérification de santé
~~~

Les tests ne doivent pas seulement valider le cas idéal. Ajoute un cas d’échec : serveur inaccessible, variable invalide, service incapable de redémarrer ou version de dépendance incompatible. L’automatisation doit échouer de façon sûre, exposer les informations utiles et laisser l’opérateur comprendre ce qui a été modifié.

## 7. Inventaires dynamiques et environnements d’exécution

Un inventaire dynamique récupère les cibles d’une source telle qu’un fournisseur cloud ou une plateforme d’inventaire. Contrôle les critères de sélection afin qu’un nouveau serveur de test ne soit pas automatiquement traité comme un serveur de production.

Les plateformes d’automatisation comme AWX ou Red Hat Ansible Automation Platform ajoutent, selon l’installation, des mécanismes de planification, d’identifiants, d’approbation, de journaux et de délégation. Les environnements d’exécution encapsulent Ansible, les collections Python et les dépendances ; ils améliorent la reproductibilité du contrôleur. Ils ne dispensent pas de vérifier la compatibilité et de maintenir les images utilisées.

## 8. Observabilité et audit

Pour chaque exécution, garde un identifiant de changement, la version de l’artefact, la cible, l’identité de l’opérateur, l’heure de début, le résultat et le rapport post-déploiement. Ne stocke pas les secrets dans les métadonnées d’exécution.

Surveille au minimum le taux de réussite, le nombre d’hôtes modifiés, la durée, les échecs par tâche, les erreurs d’authentification et les retours arrière. Un succès Ansible signifie que les tâches ont satisfait leurs critères ; il ne garantit pas à lui seul que le service métier reste disponible. Ajoute des tests de santé fonctionnels après la configuration.

## 9. Retour arrière et récupération

Une procédure de retour arrière doit être définie avant l’action. Pour un fichier, sauvegarde la version précédente ou utilise un déploiement versionné. Pour une application, conserve un artefact validé pouvant être redéployé. Pour une modification de données, définis si une restauration est possible et quelles pertes elle implique.

Ne confonds pas le fait de relancer un playbook avec un retour arrière. L’idempotence ramène un système vers l’état décrit par le playbook courant ; si cet état est mauvais, l’idempotence peut réappliquer le mauvais état. Un retour arrière exige une source connue comme bonne et un test de santé ensuite.

## 10. TP guidé : déploiement progressif d’un reverse proxy

**Situation :** quatre serveurs proxy servent une application. Une nouvelle configuration doit être déployée sans redémarrage global et sans exposer de secret.

1. Crée un rôle reverse_proxy avec les valeurs par défaut documentées.
2. Ajoute un template, un contrôle nginx -t et une tâche de reload.
3. Écris des tests sur le fichier généré, son propriétaire et le service.
4. Exécute les vérifications statiques puis les tests en environnement isolé.
5. Déploie sur un premier lot de deux serveurs.
6. Lance les contrôles de santé et n’avance que si les critères sont satisfaits.
7. Répète sur le second lot et archive le rapport de déploiement.
8. Simule un échec de vérification et démontre que le lot suivant ne commence pas.

**Réussite :** les cibles sont exactes, l’exécution est reproductible, le secret n’apparaît ni dans Git ni dans les logs, la mise à jour est progressive et la procédure d’échec est documentée.

## Exercices avec corrigés

**1. Pourquoi une tâche idempotente peut-elle provoquer une panne ?**  
Parce que l’idempotence concerne la répétabilité de l’état cible, pas l’innocuité de cet état ni l’ordre d’application. Il faut contrôler le périmètre, les dépendances, les lots et la santé du service.

**2. Pourquoi épingler les versions des collections ?**  
Pour empêcher qu’un changement de dépendance non contrôlé modifie le comportement du même playbook entre deux exécutions et pour permettre de reproduire un incident.

**3. À quoi sert serial ?**  
À exécuter un play sur des lots successifs d’hôtes, ce qui permet de limiter l’impact et d’insérer des vérifications entre les lots.

**4. Pourquoi le mode check ne remplace-t-il pas un test d’intégration ?**  
Parce que tous les modules ne simulent pas chaque effet, et qu’il ne valide pas à lui seul la disponibilité applicative ni toutes les dépendances réelles.

## Défi final corrigé

Conçois un pipeline qui valide un rôle Ansible, le publie dans une version identifiable, le déploie sur un groupe staging puis sur un groupe production en lots, et arrête le déploiement au premier échec de santé.

**Correction attendue :** lint et syntax-check obligatoires ; tests de rôle ; artefact/dépendances épinglés ; revue et approbation ; inventaires séparés ; list-hosts ; exécution progressive avec serial ; contrôle fonctionnel après chaque lot ; capture du résultat et procédure de rollback documentée. Le pipeline doit également prouver qu’une tentative échouée ne déclenche pas automatiquement les lots suivants.

## Synthèse

L’expertise Ansible repose sur les contrats des rôles, l’isolation des environnements, la maîtrise des secrets, les tests, les déploiements progressifs et l’observabilité. Une automatisation mature permet de répondre précisément à quatre questions : quoi a changé, où, sous quelle autorisation et comment revenir à un état sûr.