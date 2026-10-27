### 3.10 Dépendances et topologie

La panne d'une passerelle peut rendre injoignables des dizaines d'équipements. Sans connaissance des dépendances, chaque service peut générer une alerte, ce qui détourne l'équipe du problème racine. Nagios dispose de dépendances d'hôte et de service qui permettent, selon les conditions configurées, de supprimer certains contrôles ou notifications lorsque le statut d'un composant parent explique les symptômes.

~~~mermaid
flowchart TD
  A[Lien WAN] --> B[Routeur de site]
  B --> C[Commutateur LAN]
  C --> D[Serveurs locaux]
  D --> E[Applications]
  A -. perte .-> F[Incident parent possible]
  B -. symptôme .-> F
  C -. symptôme .-> F
~~~

Les dépendances doivent correspondre à la topologie réelle. Elles ne doivent pas masquer une panne indépendante qui survient en parallèle. Il est utile de surveiller aussi le chemin de gestion et la passerelle, puis de documenter précisément quels checks ou notifications peuvent être supprimés lorsqu'un parent est indisponible.

### 3.11 Notifications, escalades et handlers

Une notification informe un contact ; un **event handler** est une commande exécutée lors d'un événement selon la configuration. Ces mécanismes ne sont pas interchangeables. Une notification peut envoyer un message ou créer un ticket. Un handler peut lancer une action automatisée, mais toute modification de production exige une autorisation, une journalisation, des limites d'exécution et une possibilité de retour à un état sûr.

~~~mermaid
flowchart TD
  A[État confirmé] --> B[Évaluer dépendances]
  B --> C{Notification permise ?}
  C -->|Non| D[Consigner le statut]
  C -->|Oui| E[Contact principal]
  E --> F{Incident pris en charge ?}
  F -->|Oui| G[Suivi]
  F -->|Non| H[Escalade prévue]
~~~

Pour chaque sévérité, préciser qui doit agir, dans quel délai et selon quelle procédure. Les contacts et plages de notification ne sont pas des détails secondaires : un service critique qui tombe en dehors d'une plage mal définie peut ne pas alerter la bonne personne. Tester l'acheminement et la réception réels, pas seulement le statut dans l'interface.

### 3.12 Valider la configuration Nagios

Avant de recharger le moteur, vérifier la configuration avec la commande et le chemin adaptés à l'installation. Une installation depuis les sources peut utiliser un chemin différent de celui du paquet de la distribution.

~~~bash
sudo nagios -v /usr/local/nagios/etc/nagios.cfg
~~~

Corriger toutes les erreurs et examiner les avertissements. Une configuration peut être valide syntaxiquement tout en contenant un objet mal ciblé, un seuil inadapté ou un contact qui ne reçoit pas l'alerte. Après validation, appliquer la méthode de reload recommandée par l'installation, puis confirmer que le processus reste sain et que les checks reprennent. Tester les plugins manuellement sur des cibles autorisées, avec des paramètres documentés.

## 4. Zabbix : l'architecture intégrée

### 4.1 Les composants

Zabbix réunit la collecte, le stockage des valeurs, l'évaluation des expressions, la gestion des événements, les notifications et la visualisation. Une architecture typique comprend :

- **Zabbix server** : orchestre la supervision, traite les données, évalue les triggers, produit les événements et exécute les actions.
- **Frontend Web** : configure les hôtes, interfaces, items, triggers, templates, comptes, médias, tableaux de bord et fenêtres de maintenance.
- **Base de données** : conserve configuration, historique et tendances ; le moteur de base, son stockage et les index influencent les performances.
- **Agent Zabbix ou Agent 2** : collecte des mesures locales sur les systèmes supportés, en mode actif ou passif.
- **Zabbix proxy** : collecte les données d'un groupe de cibles ou d'un site distant et les synchronise avec le serveur selon le mode choisi.
- **Équipements réseau et sources externes** : routeurs, switches, pare-feu, onduleurs, applications, API et systèmes exposant des valeurs via SNMP ou d'autres types d'items.

~~~mermaid
flowchart TB
  A[Frontend Web] --> B[Zabbix Server]
  B <--> C[Base de données]
  B <--> D[Agent Linux ou Windows]
  B <--> E[Routeur et switch SNMP]
  B <--> F[Proxy de site]
  F <--> G[Hôtes du site]
  F <--> H[SNMP local]
  B --> I[Événements et actions]
  I --> J[Mail webhook ou ticket]
~~~

Dans un petit environnement, plusieurs rôles peuvent être sur la même machine. Dans un environnement important, ils peuvent être séparés pour sécurité, disponibilité, capacité ou maintenance. Le nombre d'hôtes ne suffit pas à dimensionner la plateforme : le nombre de valeurs collectées par seconde, le nombre de triggers, le prétraitement, la fréquence et la rétention influencent fortement le serveur et la base.

### 4.2 Cheminement d'une valeur

Un item est collecté ou reçoit une valeur. Cette donnée peut être prétraitée, validée, transformée ou rejetée avant enregistrement. Les triggers évaluent les données suivant leurs expressions. Lorsqu'une expression passe à l'état problème, Zabbix produit un événement ; les actions évaluent ensuite leurs conditions et opérations. La récupération peut produire un événement distinct.

~~~mermaid
flowchart LR
  A[Item] --> B[Collecte]
  B --> C[Prétraitement]
  C --> D[Historique]
  D --> E[Trigger]
  E --> F[Événement]
  F --> G[Conditions d'action]
  G --> H[Notification]
~~~

Ce chemin aide à localiser un défaut. Si une valeur manque, examiner la collecte. Si elle est présente mais que le trigger reste inactif, vérifier l'expression, la clé, l'unité, la fenêtre et l'historique nécessaire. Si l'événement existe mais que le courriel n'arrive pas, examiner les actions, les médias, les destinataires, les conditions temporelles et les journaux du canal.

### 4.3 Le proxy : distribution de la collecte

Un proxy est utile dans des agences, des sites distants ou des réseaux séparés où le serveur central ne doit pas interroger directement chaque cible. Il peut collecter localement puis transférer les données selon son mode et la version. Il ne faut pas le considérer automatiquement comme un serveur de secours qui exécute toutes les fonctions du serveur central : les fonctions de traitement et de notification dépendent de l'architecture et de la version installée.

~~~mermaid
flowchart LR
  A[Hôtes distants] --> B[Proxy Zabbix]
  C[Équipements SNMP] --> B
  B --> D[Buffer local selon mode]
  D --> E[Serveur central]
  E --> F[Triggers et événements]
  F --> G[Actions et notifications]
~~~

Lors du déploiement, vérifier le mode du proxy, le nom déclaré, la connectivité vers le serveur, les règles de pare-feu, l'accès local aux cibles, le stockage tampon et la capacité à synchroniser après une coupure. Le proxy lui-même doit être supervisé : sinon, le serveur peut continuer d'afficher les dernières valeurs alors qu'elles sont devenues périmées.

### 4.4 Quand séparer les composants

Séparer le serveur, le frontend et la base peut améliorer l'isolation et rendre le dimensionnement plus clair, mais accroît aussi la complexité du réseau, des certificats et de la maintenance. Le serveur de supervision dépend de sa base : une base lente ou inaccessible peut retarder le traitement même si les équipements répondent. Le frontend n'est pas le moteur de collecte ; une interface Web indisponible ne signifie pas nécessairement que tous les checks sont arrêtés. Le diagnostic doit identifier le composant réellement touché.

Une architecture distribuée doit documenter les ports, origines autorisées, secrets, règles DNS et routes. Il faut savoir comment le proxy se comporte pendant une coupure et quelles données il peut garder temporairement, puis comment il synchronise après rétablissement. Les valeurs anciennes doivent rester reconnaissables comme anciennes et ne pas être présentées comme des mesures actuelles.
