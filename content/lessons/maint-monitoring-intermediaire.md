# Supervision réseau (Nagios, Zabbix)

> **Mise en contexte** — Un réseau d'entreprise comprend routeurs, commutateurs, pare-feu, liens opérateur, DNS, systèmes d'authentification, serveurs, API et applications métiers. Une panne peut venir d'un composant, d'une dépendance, d'une saturation lente, d'un certificat expiré ou de la collecte qui ne reçoit plus les données. La supervision doit permettre de distinguer ces situations et d'agir avant que les utilisateurs ne découvrent le problème.

> **Idée directrice** — Une bonne supervision ne cherche pas à afficher le plus de voyants verts. Elle collecte les bons signaux, explique ce qu'ils prouvent, détecte les anomalies significatives, limite les fausses alertes, protège les accès de gestion et conserve les traces nécessaires à la reconstruction d'un incident. Nagios Core et Zabbix peuvent servir ces objectifs, mais reposent sur des modèles différents.

## 1. Objectifs pédagogiques

Tu dois pouvoir concevoir un pilote avec Nagios et Zabbix, créer des contrôles cohérents, comprendre pourquoi une alerte apparaît et expliquer les résultats à une équipe technique. Cela demande de distinguer hôte, service, item, métrique, trigger, événement, état et notification ; comprendre les plugins et codes de retour Nagios ; expliquer la logique SOFT/HARD et les dépendances ; décrire les composants Zabbix, ses agents, proxys, templates, items, triggers et actions ; distinguer collecte active, passive, SNMP, traps et contrôles applicatifs ; définir des seuils adaptés ; sécuriser les flux et diagnostiquer une collecte manquante.

Les exemples sont illustratifs : chemins, options, noms de services et clés d'items varient selon la version et la distribution. Toute configuration de production doit être adaptée, testée en laboratoire et révisée avant application.

## 2. Ce que l'on mesure

### 2.1 Hôte, service, métrique et événement

Un **hôte** est un élément supervisé : routeur, commutateur, serveur, VM, imprimante, point d'accès ou système applicatif. Un hôte est un objet logique et ne doit pas forcément correspondre à une machine physique.

Un **service Nagios** représente une vérification associée à un hôte. Le terme peut désigner HTTP, DNS, espace disque, latence, état d'interface ou nombre de connexions. Dans Zabbix, un **item** collecte ou reçoit une valeur, tandis qu'un **trigger** évalue une expression pour décider si un problème doit être signalé.

Une **métrique** doit être définie avec une unité, une cible, un intervalle et une méthode de collecte : latence en millisecondes, perte en pourcentage, débit en bits par seconde, mémoire disponible en octets ou âge du dernier point de sauvegarde. Un **événement** représente une occurrence significative ; une **notification** transmet une information à une personne ou à un autre système. Toutes les valeurs ne doivent pas déclencher des notifications.

~~~mermaid
flowchart LR
  A[Équipement] --> B[Mesure]
  B --> C[Évaluation]
  C --> D{Anomalie significative ?}
  D -->|Non| E[Historique]
  D -->|Oui| F[Événement]
  F --> G[Priorisation]
  G --> H[Notification]
~~~

### 2.2 Pourquoi le ping ne suffit pas

ICMP Echo vérifie si une cible répond à une requête réseau. Il ne prouve pas que l'application fonctionne. Un serveur Web peut répondre au ping mais avoir son processus HTTP arrêté ; une API peut accepter TCP et renvoyer une erreur de base de données ; un hôte peut bloquer ICMP tout en servant correctement HTTPS.

Pour un service Web important, combiner selon le besoin réponse ICMP, port TCP, code HTTP, contenu attendu, validité TLS et test d'une transaction. Pour un commutateur, surveiller l'accès de gestion, les états des interfaces, les erreurs, les discards, les débits, la température et les alimentations lorsque les données existent.

~~~mermaid
flowchart TD
  A[Serveur Web] --> B[ICMP]
  A --> C[TCP]
  A --> D[HTTP]
  A --> E[TLS]
  A --> F[Transaction métier]
  B --> G[Diagnostic]
  C --> G
  D --> G
  E --> G
  F --> G
~~~

Le point de mesure compte également : un test du poste d'un technicien ne traverse pas nécessairement les mêmes routes, ACL ou pare-feu que le serveur de supervision. Pour diagnostiquer la collecte, reproduire le check depuis le bon endroit.

### 2.3 Zéro et absence de donnée

Zéro peut être valide : aucune erreur mesurée, aucune perte ou aucun utilisateur actif. L'absence de valeur peut provenir d'un agent arrêté, d'un pare-feu, d'un problème SNMP, d'un proxy hors ligne ou d'un délai de traitement. Ne transforme jamais silencieusement une valeur absente en zéro : tu pourrais afficher un système comme sain alors qu'il n'est plus observé.

### 2.4 Pull et push

En collecte interrogée (pull ou polling), le serveur ou le proxy contacte la cible. Dans une collecte émise (push), l'agent ou un collecteur initie la connexion et transmet les résultats ; les checks actifs Zabbix utilisent ce modèle. Nagios peut aussi recevoir des résultats passifs.

~~~mermaid
flowchart LR
  A[Serveur] -->|Requête| B[Cible]
  B -->|Réponse| A
  C[Collecteur distant] -->|Résultat envoyé| D[Récepteur]
  D --> E[Évaluation]
~~~

Le choix dépend des routes, du pare-feu, du volume de collecte, de l'autonomie en cas de coupure et du modèle de sécurité. Tout déploiement hybride doit documenter ses flux.

## 3. Nagios Core : fonctionnement en profondeur

### 3.1 Le moteur, les objets et les plugins

Nagios Core est un moteur qui ordonnance des contrôles, lance des commandes, interprète leurs résultats et gère les états des hôtes et services. Le cœur n'embarque pas la connaissance détaillée de chaque protocole ou application. Il délègue la vérification à des plugins et standardise le résultat par un code de retour et un texte de statut.

Un plugin peut contrôler un port TCP, interroger SNMP, vérifier un disque, mesurer une latence, appeler une API ou tester DNS. Le moteur orchestre : il décide quand lancer le contrôle, avec quels paramètres et comment traiter le résultat. Le plugin mesure et décide de son statut selon sa logique propre. Cette séparation simplifie l'extension du système, mais signifie qu'un plugin mal écrit peut produire des résultats faux tout en laissant le moteur fonctionner normalement.

~~~mermaid
flowchart TB
  A[Objets de configuration] --> B[Moteur Nagios]
  B --> C[Ordonnanceur]
  C --> D[Commande]
  D --> E[Plugin]
  E --> F[Code et sortie]
  F --> G[État courant]
  F --> H[Données de performance]
  G --> I[Notification ou handler]
~~~

### 3.2 Les objets importants

| Objet | Fonction |
|---|---|
| **host** | Identité de la cible, adresse et vérification d'accessibilité. |
| **hostgroup** | Groupement par site, rôle ou équipe. |
| **service** | Contrôle associé à un hôte : HTTP, DNS, disque, interface ou latence. |
| **servicegroup** | Groupement de contrôles connexes. |
| **command** | Programme exécuté et paramètres passés au plugin. |
| **contact / contactgroup** | Destinataires et groupes de notification. |
| **timeperiod** | Périodes actives de contrôle ou de notification. |
| **hostdependency / servicedependency** | Règles de dépendance entre composants ou services. |
| **hostescalation / serviceescalation** | Règles de notification supplémentaires. |

Les modèles d'objet permettent de partager des valeurs habituelles sans dupliquer toute la configuration. Un modèle peut définir les options communes, tandis que l'hôte déclare son adresse et le service son contrôle précis. La structure des fichiers doit être lisible, versionnée et validée. Une génération automatique peut être utile à grande échelle, à condition de pouvoir inspecter et reproduire le résultat.

~~~mermaid
flowchart TD
  A[Modèle générique] --> B[Hôte routeur]
  A --> C[Hôte Linux]
  B --> D[Check ping]
  B --> E[Check interface]
  C --> F[Check disque]
  C --> G[Check processus]
  H[Commandes réutilisables] --> D
  H --> E
  H --> F
  H --> G
~~~

### 3.3 Cycle complet d'un contrôle

Le moteur repère un contrôle prévu, sélectionne sa commande, résout les macros, lance le plugin et attend son résultat dans les limites de temps prévues. Il lit ensuite le code de sortie, le texte et, si le plugin en fournit, les données de performance. Il met à jour l'état et la tentative, puis évalue la logique de notification et les dépendances.

~~~mermaid
sequenceDiagram
  participant N as Nagios Core
  participant P as Plugin
  participant T as Cible
  N->>P: Commande et arguments
  P->>T: Mesure
  T-->>P: Réponse
  P-->>N: Code et texte
  N->>N: État et tentative
  N->>N: Dépendances et notifications
~~~

Un timeout n'est pas automatiquement une panne de la cible. Il peut provenir d'un DNS inaccessible, d'une route absente, d'un port filtré, d'un plugin bloqué ou d'une charge excessive sur le serveur de supervision. Augmenter le timeout sans diagnostic peut retarder les alertes et aggraver la file des checks.

### 3.4 Codes de retour des plugins

Pour les contrôles de service, les codes conventionnels sont :

| Code | État | Sens |
|---:|---|---|
| 0 | OK | Le plugin juge le service conforme à ses critères. |
| 1 | WARNING | Une limite de vigilance est franchie. |
| 2 | CRITICAL | Le plugin détecte une condition critique définie. |
| 3 | UNKNOWN | Le plugin ne peut pas déterminer un état fiable ou rencontre une erreur de contrôle. |

Exemple de sortie :

~~~text
PING OK - packet loss 0%, rta 12.4 ms | rta=12.4ms;100;500;0; pl=0%;20;60;0;100
~~~

La partie avant le séparateur est destinée à une lecture rapide. Les données de performance après le séparateur peuvent être traitées par des outils de graphes. Les unités et seuils suivent la convention du plugin. Vérifie son aide et sa sortie plutôt que de supposer que tous les plugins expriment les valeurs de la même façon.

Un état UNKNOWN doit conduire à examiner les arguments, les droits, le DNS, les bibliothèques, l'authentification, le timeout et le contexte d'exécution. Pour un check d'hôte, un résultat non nominal peut indiquer une cible réellement inaccessible ou un problème de route. Les vérifications de services et les vérifications d'hôtes ont des conséquences d'état différentes : il faut lire leur configuration et ne pas en déduire la panne à partir d'un seul chiffre.

### 3.5 Commande et arguments

Les plugins se trouvent souvent dans un répertoire nommé libexec, mais le chemin dépend de l'installation. Exemple d'une commande déclarée dans la configuration :

~~~text
define command {
    command_name    check_ping_custom
    command_line    $USER1$/check_ping -H $HOSTADDRESS$ -w $ARG1$ -c $ARG2$
}
~~~

Le service transmet les arguments dans l'ordre voulu :

~~~text
check_command check_ping_custom!100.0,20%!500.0,60%
~~~

L'exemple suppose que le plugin, le macro et les objets mentionnés existent réellement. Les séparateurs, les unités, la ponctuation et l'ordre des arguments ont un sens. Une configuration erronée peut contrôler la mauvaise cible ou interpréter le seuil à l'envers. Les macros rendent les objets réutilisables, mais toute donnée incorporée dans une commande doit être contrôlée ; ne mets pas de secret directement dans une ligne de configuration versionnée.

### 3.6 Exemple d'hôte et de service

~~~text
define host {
    use                     generic-host
    host_name               routeur-agence-01
    alias                   Routeur principal agence
    address                 192.0.2.10
    check_command           check-host-alive
    max_check_attempts      3
    check_interval          5
    retry_interval          1
}

define service {
    use                     generic-service
    host_name               routeur-agence-01
    service_description     Disponibilite ICMP
    check_command           check_ping_custom!100.0,20%!500.0,60%
    max_check_attempts      3
    check_interval          5
    retry_interval          1
    notification_options    w,u,c,r
}
~~~

Les modèles génériques et la commande référencés doivent exister dans ton installation. Ce bloc démontre la structure, mais doit être relu selon la version et les règles de l'environnement. Le nom du service doit être stable et explicite, car il apparaît dans les tableaux de bord, notifications et rapports.

### 3.7 Intervalles et délai de détection

**check_interval** définit l'intervalle normal entre les contrôles. **retry_interval** règle l'intervalle de nouvelle tentative en cas de résultat anormal. **max_check_attempts** fixe le nombre de tentatives avant confirmation pour un check actif. Demander plusieurs échecs avant de confirmer réduit certains faux positifs, mais ajoute un délai de détection.

Le réglage doit concilier le délai de détection souhaité, la charge produite par les checks et le nombre de fausses alertes. Des intervalles très courts sur un grand parc augmentent le volume de contrôles. Lors d'une panne généralisée, davantage de résultats non nominaux et de notifications arrivent simultanément ; une plateforme déjà à la limite peut alors retarder l'ensemble des contrôles.

### 3.8 États SOFT et HARD

Lorsqu'un service passe de l'état normal à un état anormal, Nagios peut enregistrer un état **SOFT** pendant les tentatives de confirmation. Si l'anomalie persiste jusqu'au nombre de tentatives configuré, l'état devient **HARD**. La notification habituelle de problème dépend de cette transition et des règles configurées. Les résultats passifs et certaines options ont des particularités documentées à vérifier.

~~~mermaid
stateDiagram-v2
  [*] --> OK
  OK --> SOFT: Premier échec
  SOFT --> OK: Contrôle suivant réussi
  SOFT --> SOFT: Échec et tentatives restantes
  SOFT --> HARD: Échec confirmé
  HARD --> OK: Récupération vérifiée
~~~

Trop de tentatives peut retarder une alerte critique ; trop peu rend le système sensible aux microcoupures. Choisir une politique par type de service, puis vérifier le délai de détection dans un test contrôlé.

### 3.9 Checks actifs et résultats passifs

Un check actif est planifié et exécuté par Nagios. Un résultat passif est produit par un autre composant et transmis au moteur. Les résultats passifs sont utiles quand un collecteur distant connaît déjà le résultat ou qu'un événement doit être signalé sans polling régulier.

Le mode passif ne signifie pas que tout résultat doit être accepté sans validation. La provenance doit être identifiable et les sources autorisées. Il faut aussi définir ce qui se passe quand aucun résultat n'arrive ; sinon, un ancien état peut rester affiché alors que le service n'est plus observé.

~~~mermaid
flowchart LR
  A[Planificateur] --> B[Check actif]
  B --> C[Plugin]
  D[Collecteur externe] --> E[Résultat passif]
  C --> F[Moteur Nagios]
  E --> F
  F --> G[Statut et historique]
  G --> H[Notification éventuelle]
~~~

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

## 5. Les objets Zabbix : hôtes, items, triggers et templates

### 5.1 Hôtes et interfaces

Un hôte Zabbix représente l'objet suivi. Son nom doit être stable et cohérent avec l'identité utilisée par les agents pour les contrôles actifs. Une interface indique le chemin de communication quand l'item en a besoin : agent, SNMP, IPMI ou JMX selon la configuration. Un check simple, un item calculé ou certains types de données peuvent ne pas nécessiter une interface classique.

Une convention de nommage peut combiner site, rôle et identifiant : **DOU-AGENCE01-RTR01**, **DC1-SW-CORE01** ou **DC1-LNX-APP01**. Évite d'incorporer dans le nom une propriété qui change souvent, comme le propriétaire ou l'adresse IP, si elle peut être gérée par des champs séparés. L'identité doit aider les recherches, le rapprochement avec l'inventaire et la déduplication d'événements.

### 5.2 Items : définir une donnée sans ambiguïté

Un **item** définit la donnée à collecter ou recevoir, le type de collecte, la clé ou la requête, l'intervalle, l'unité, le type d'information, la rétention et éventuellement le prétraitement. Les types et clés disponibles dépendent de la version et du composant.

| Famille | Exemple | Contrôle essentiel |
|---|---|---|
| Agent | CPU, mémoire, système de fichiers, processus | Clé disponible, permission et mode actif/passif. |
| SNMP | Statut d'interface, trafic, erreurs, température | OID, droits, unité et type de compteur. |
| ICMP ou check simple | Reachability, perte, latence | Portée du test et utilitaires disponibles. |
| HTTP ou API | Code HTTP, temps, réponse JSON | Authentification, certificat et contenu attendu. |
| Trap ou sender | Événement externe transmis | Récepteur, schéma et provenance. |
| Item dépendant ou calculé | Valeur dérivée d'une autre mesure | Prétraitement, unité et fraîcheur. |

Une valeur en octets ne doit pas être comparée directement à un seuil exprimé en pourcentage. Les noms doivent décrire la mesure et pas seulement répéter le nom du périphérique. La fréquence doit correspondre au besoin : trop courte, elle augmente le stockage ; trop longue, elle peut manquer un événement bref. Il faut fixer un délai de détection, évaluer la volatilité de la mesure et mesurer le coût de collecte.

### 5.3 Triggers et expressions temporelles

Un **trigger** transforme les données en état significatif. Il peut comparer une valeur à un seuil, rechercher l'absence de données ou détecter une évolution anormale. La durée fait partie de la logique : « CPU au-dessus de 90 % pendant cinq minutes » n'a pas la même signification qu'un seul échantillon. La persistance filtre certains pics, mais peut augmenter le délai de détection.

Exemples d'expressions modernes à adapter et à tester : le nom d'hôte et les clés d'items doivent réellement exister.

~~~text
max(/ROUTEUR-WAN01/icmpping,3m)=0
min(/SERVEUR-LINUX01/agent.ping,5m)=0
~~~

La seconde expression n'est pertinente que si la clé **agent.ping** existe dans la configuration de cet hôte et si sa sémantique correspond à l'intention. Vérifie la clé réelle, le type d'information, l'unité, la période et les valeurs reçues avant de copier une expression.

Un trigger doit avoir une gravité, une description et une condition de récupération compréhensibles. « Warning » doit appeler une action de vigilance ou de planification ; une gravité élevée doit correspondre à un impact supérieur. Des triggers qui se recouvrent peuvent créer plusieurs problèmes sur un même signal : contrôler les tags, la corrélation, les dépendances et les règles de récupération.

~~~mermaid
flowchart TD
  A[Valeurs de l'item] --> B[Expression du trigger]
  B --> C{Condition vraie ?}
  C -->|Non| D[Pas de problème]
  C -->|Oui| E[Événement]
  E --> F[Action ciblée]
  F --> G[Notification]
  B --> H[Condition de récupération]
  H --> I[Événement de récupération]
~~~

### 5.4 Templates, macros et héritage

Un template regroupe des items, triggers, graphes, règles de découverte et éléments réutilisables. Le rattacher à plusieurs hôtes compatibles évite de reproduire des configurations manuelles. On peut créer un modèle Linux commun, puis des modèles spécialisés pour les bases de données, serveurs Web, applications ou équipements SNMP.

~~~mermaid
flowchart TD
  A[Template Linux commun] --> B[Serveur Linux 01]
  A --> C[Serveur Linux 02]
  D[Template switch SNMP] --> E[Switch accès 01]
  D --> F[Switch accès 02]
  G[Macros globales] --> A
  H[Macros spécifiques] --> B
  H --> C
~~~

Les macros réutilisent des paramètres comme les seuils ou identifiants de site. Les valeurs sensibles nécessitent un mécanisme de secret et des permissions adaptés : une macro masquée dans l'interface ne garantit pas qu'elle est absente de tous les exports ou journaux.

L'héritage doit rester lisible. Un template universel qui comporte des contrôles inapplicables à beaucoup d'hôtes génère du bruit et augmente la charge. Crée des modèles par rôle, ajoute une spécialisation lorsque les matériels diffèrent et teste sur un hôte pilote avant de lier le template à toute la flotte.

### 5.5 Découverte réseau et découverte de bas niveau

La découverte réseau identifie des hôtes ou des services dans un périmètre configuré. La découverte de bas niveau (LLD) détecte des entités d'un hôte, par exemple interfaces, systèmes de fichiers ou objets SNMP, puis utilise des prototypes pour créer les items, triggers ou graphes correspondants. Cette automatisation doit être filtrée : un commutateur peut exposer des interfaces internes, virtuelles ou inutilisées qui ne méritent pas chacune une alerte.

Tester la découverte sur un équipement pilote, examiner les objets générés et contrôler le volume de données avant de la généraliser. Une interface renommée ou supprimée peut laisser des objets historiques ou des graphes obsolètes ; les règles de conservation et de suppression doivent être explicites.

### 5.6 Prétraitement et items dépendants

Le prétraitement transforme ou valide une valeur avant son usage. Il peut convertir des unités, extraire un champ d'un JSON, appliquer une opération arithmétique ou rejeter une valeur invalide. Un item dépendant réutilise une valeur maître déjà collectée afin de produire plusieurs métriques sans répéter la même interrogation coûteuse.

Cette optimisation peut réduire le nombre de requêtes, mais introduit des dépendances : si le format de la réponse source change, plusieurs mesures dérivées peuvent échouer ensemble. Documenter la structure attendue et les erreurs de prétraitement.

### 5.7 Historique, tendances et rétention

L'historique conserve les valeurs individuelles selon la politique définie. Les tendances conservent des agrégats temporels pour les données numériques supportées, tels que minimum, moyenne, maximum et nombre d'échantillons. Elles permettent de visualiser des périodes longues sans conserver toutes les valeurs brutes indéfiniment. Les chaînes et journaux n'ont pas les mêmes propriétés d'agrégation que les métriques numériques.

La rétention influence le coût, l'espace disque et la profondeur d'analyse. Conserver chaque valeur toutes les quelques secondes pendant des années peut faire croître la base rapidement. Supprimer trop tôt les données rend difficile l'explication d'une saturation lente ou d'une panne rare. La politique doit correspondre à l'objectif de dépannage, aux besoins de capacité et aux exigences de conservation. Mesurer la croissance de base sur un pilote plutôt que se fier seulement à une estimation.

## 6. Agents Zabbix : contrôle actif et passif

### 6.1 Contrôle passif

En mode passif, le serveur Zabbix ou le proxy contacte l'agent et lui demande une donnée. L'agent écoute habituellement sur TCP 10050, sauf changement de configuration. Le collecteur doit pouvoir atteindre l'agent ; le pare-feu doit permettre ces connexions uniquement depuis les sources de supervision autorisées.

Le paramètre **Server** de l'agent limite les adresses autorisées à effectuer les contrôles passifs. Le laisser trop ouvert augmente la surface d'attaque. Vérifie aussi que le nom déclaré correspond à l'identité attendue, que l'agent peut lire les données et que les clés existent dans la version installée.

### 6.2 Contrôle actif

En mode actif, l'agent ouvre une connexion vers le serveur ou le proxy, récupère la liste des checks actifs qui lui sont attribués et envoie les valeurs. Le port du serveur Zabbix est habituellement TCP 10051. Ce mode est utile lorsque le réseau de la cible autorise les connexions sortantes vers la supervision mais interdit les connexions entrantes depuis le centre.

~~~mermaid
sequenceDiagram
  participant A as Agent actif
  participant Z as Serveur ou proxy
  participant DB as Base de données
  A->>Z: Demander configuration active
  Z-->>A: Items et paramètres
  A->>A: Collecter les valeurs
  A->>Z: Transmettre les mesures
  Z->>DB: Prétraiter et enregistrer
~~~

En passif, vérifier le chemin du serveur vers l'agent. En actif, vérifier la route sortante depuis l'agent vers le collecteur. Si les deux modes sont utilisés, documenter chaque flux et tester les items séparément.

### 6.3 Exemple de configuration agent

Voici des paramètres usuels à adapter au fichier et aux options de la version installée :

~~~ini
Server=192.0.2.20
ServerActive=192.0.2.20:10051
Hostname=SERVEUR-LINUX01
Timeout=5
~~~

**Server** désigne les sources autorisées pour les checks passifs. **ServerActive** désigne le serveur ou proxy auquel l'agent se connecte pour les checks actifs. **Hostname** doit correspondre au nom configuré côté Zabbix pour les checks actifs usuels. Le timeout doit être approprié aux contrôles autorisés. L'exemple ne montre pas toutes les options, notamment celles relatives au chiffrement, aux logs, aux modules ou scripts spécifiques.

Le protocole et les options varient selon les versions de l'agent. Agent et Agent 2 partagent une base de protocole unifiée dans les versions modernes, mais leurs fonctions et plugins doivent être vérifiés dans la documentation. Ne déploie pas une configuration identique sur un parc hétérogène sans essai pilote.

~~~mermaid
flowchart LR
  A[Agent et paramètres] --> B{Mode du check}
  B -->|Passif| C[Serveur vers agent TCP 10050]
  B -->|Actif| D[Agent vers serveur TCP 10051]
  C --> E[ACL et pare-feu]
  D --> E
  E --> F[Valeurs récentes]
~~~

### 6.4 Sécuriser les agents

Les données de supervision révèlent versions, chemins, processus et caractéristiques du système. Certains mécanismes peuvent aussi permettre des actions sensibles lorsqu'ils sont activés. Appliquer le moindre privilège, le filtrage réseau, le chiffrement disponible et la séparation des comptes. Désactiver les commandes distantes non nécessaires et examiner les modules externes avant leur déploiement.

Ne place jamais de secret réel dans un cours, un ticket largement partagé, un script commité ou une capture d'écran. Si un secret a été enregistré dans Git, le supprimer du fichier courant ne suffit pas : il faut le révoquer ou le renouveler, contrôler son utilisation et traiter l'historique exposé selon les procédures de sécurité.

## 7. SNMP : supervision des routeurs et commutateurs

### 7.1 SNMP, MIB et OID

SNMP permet à une station de gestion d'interroger des objets exposés par les équipements. Les données disponibles dépendent des OID, de la MIB, du firmware et des permissions. Deux familles d'équipements peuvent exposer des champs différents ou des limites d'implémentation différentes.

SNMPv1 et SNMPv2c reposent couramment sur des communautés et ne fournissent pas la confidentialité moderne attendue. SNMPv3 propose des niveaux de sécurité avec authentification et confidentialité lorsqu'ils sont configurés correctement. Limiter les sources autorisées, employer des droits de lecture, protéger les identifiants et éviter d'activer l'écriture uniquement pour faciliter la collecte.

Un OID identifie un objet dans une hiérarchie. Les compteurs d'interfaces permettent de mesurer le trafic. Les OID propriétaires peuvent donner d'autres informations, comme température, alimentation, état de module ou alarmes du constructeur. Il faut vérifier la MIB et la référence de l'équipement plutôt que supposer que chaque modèle expose les mêmes données.

### 7.2 Compteur brut et débit calculé

Un compteur d'octets représente un volume accumulé à un moment donné, pas le débit instantané. Le débit se calcule à partir de la différence entre deux lectures séparées par une durée connue. La différence est divisée par le temps écoulé puis multipliée par huit pour passer d'octets par seconde à bits par seconde.

~~~mermaid
flowchart LR
  A[Compteur à t1] --> C[Calcul différence]
  B[Compteur à t2] --> C
  D[Durée entre lectures] --> E[Octets par seconde]
  C --> E
  E --> F[Conversion en bits]
  F --> G[Débit calculé]
~~~

Les redémarrages, débordements de compteur, changements d'interface et données manquantes peuvent créer des pointes artificielles. Utiliser les compteurs adaptés à la vitesse de l'interface et traiter les valeurs incohérentes. La supervision doit aussi connaître la vitesse nominale réelle : un calcul fondé sur une capacité erronée produit un pourcentage trompeur.

Sur une interface importante, surveiller l'état administratif, l'état opérationnel, les trafics entrant et sortant ainsi que les erreurs et discards disponibles. Une utilisation élevée pendant une seconde ne signifie pas nécessairement une saturation persistante. Rapprocher débit, perte, latence, files d'attente, horaires et rôle de la liaison.

### 7.3 Vérifier SNMP depuis le point de collecte

Avant de configurer des centaines d'équipements, tester une cible pilote avec les utilitaires disponibles dans le réseau d'administration. Vérifier d'abord l'accessibilité IP, puis la version SNMP, l'accès UDP 161, l'utilisateur ou la communauté, le niveau de sécurité et l'OID demandé. Utiliser les mécanismes approuvés de fourniture des secrets plutôt que de les écrire dans un historique shell ou un fichier partagé.

Si un contrôle échoue, avancer par couches : connectivité IP, routage, filtrage, version SNMP, utilisateur, niveau de sécurité, secrets, vue de lecture, OID et prise en charge de la MIB. Un échec d'authentification ne justifie pas d'ouvrir SNMP en lecture/écriture ni de permettre toutes les sources.

### 7.4 Polling et traps SNMP

Le polling interroge périodiquement l'équipement pour connaître son état courant et lire ses compteurs. Une trap est un message émis par l'équipement lors d'un événement configuré. Une trap peut arriver rapidement après une panne d'interface ; le polling permet ensuite de confirmer si la condition persiste et d'obtenir des données de tendance.

~~~mermaid
flowchart TD
  A[Équipement réseau] --> B[Polling périodique]
  B --> C[État et compteurs actuels]
  A --> D[Trap sur événement]
  D --> E[Récepteur de traps]
  C --> F[Corrélation]
  E --> F
  F --> G[Incident documenté]
~~~

La réception des traps n'est pas automatique. Il faut un récepteur configuré, la bonne route, un format de message adapté et une intégration vers Zabbix ou Nagios. Une trap perdue ne signifie pas que l'événement n'a pas eu lieu ; une trap reçue ne confirme pas non plus que la panne est encore présente. Les deux mécanismes se complètent.

## 8. Concevoir des seuils et des déclencheurs pertinents

### 8.1 Seuil absolu, relatif et temporel

Un seuil absolu compare une mesure à une limite : occupation disque au-dessus de 90 %, perte au-dessus d'un pourcentage défini ou température supérieure à une limite constructeur. Un seuil relatif compare une valeur à son comportement historique. Une condition temporelle exige que le dépassement persiste ; elle permet d'éviter qu'un pic fugace devienne un incident alors qu'il n'a pas d'effet réel.

Les seuils doivent être justifiés par la capacité, les marges de sécurité, les contraintes du service et la vitesse de dégradation. Une partition stable à 85 % n'a pas la même urgence qu'une partition à 75 % qui augmente rapidement et sera pleine avant la prochaine fenêtre d'intervention. Un lien WAN à forte utilisation peut fonctionner normalement ; pour reconnaître une saturation, il faut observer la perte, la latence, les files d'attente et les exigences de l'application.

~~~mermaid
flowchart TD
  A[Valeur hors norme] --> B[Confirmer dans le temps]
  B --> C[Comparer à la référence]
  C --> D{Impact ou risque établi ?}
  D -->|Non| E[Observer la tendance]
  D -->|Oui| F[Créer un événement]
  F --> G[Action et responsable]
~~~

### 8.2 Hystérésis et récupération

Un trigger qui s'active à 90 % et récupère à 89,9 % risque d'osciller si la valeur bouge autour de la limite. Une condition de récupération distincte, une temporisation, une moyenne ou un minimum/maximum sur une fenêtre peuvent stabiliser l'état. Les possibilités exactes diffèrent entre Nagios et Zabbix ; le principe est de supprimer les oscillations inutiles sans retarder une récupération réelle.

La disparition d'un seuil n'est pas toujours la suppression du risque. Si un disque repasse sous la limite parce que des fichiers temporaires ont été supprimés, mais que la croissance va reproduire le problème le lendemain, l'événement peut se résoudre alors qu'une action de capacité reste nécessaire. Les tendances et le suivi d'actions doivent compléter les événements.

### 8.3 Corrélation et gravité

Les alertes doivent être analysées selon la topologie, le service, le site, la fenêtre temporelle et les dépendances. Des alertes simultanées peuvent avoir une cause commune, mais le timing seul ne prouve pas la causalité. Les règles de dépendance et de corrélation doivent être explicites et testées avec des scénarios réels ou de laboratoire.

~~~mermaid
flowchart LR
  A[Alertes brutes] --> B[Normalisation]
  B --> C[Analyse des dépendances]
  C --> D[Regroupement de symptômes]
  D --> E[Incident parent possible]
  E --> F[Évaluation de gravité]
  F --> G[Équipe responsable]
~~~

Chaque gravité doit correspondre à une action concrète. Une information peut enrichir un graphe. Un avertissement peut créer une tâche de capacité. Une alerte critique peut déclencher une astreinte et une communication. Un signal sans propriétaire ou sans suite attendue n'est pas correctement conçu.

### 8.4 Fatigue d'alerte

La fatigue d'alerte est provoquée par les faux positifs, les duplications, les notifications répétées et les signaux qui ne conduisent jamais à une action. Elle pousse les équipes à ignorer les messages ou à désactiver des contrôles importants. Pour réduire ce risque, mesurer les alertes actionnables, les doublons, les événements non acquittés, les délais de traitement et les incidents détectés trop tard.

Revoir les règles qui n'apportent aucune action, mais ne pas les supprimer par réflexe. La cause peut être un seuil mal réglé, une donnée qui ne mesure pas la bonne fonction, l'absence de propriétaire ou une procédure de traitement impraticable. Une bonne alerte doit changer une décision ou accélérer une action pertinente.

## 9. Modéliser et sécuriser la supervision

### 9.1 Inventaire et criticité

Avant de créer des hôtes, disposer d'un inventaire comprenant identifiant stable, type d'actif, adresse de gestion, site, rôle, criticité, propriétaire, dépendances, fenêtre de maintenance, protocole de collecte et contact d'escalade. Identifier les actifs retirés, temporaires, redondants et inconnus. Sinon, la couverture annoncée peut inclure des équipements inactifs tandis que des actifs critiques manquent.

La criticité influence la fréquence, la profondeur des contrôles, le niveau de notification et la rétention. Une passerelle partagée ou un DNS central peut avoir un rayon d'impact supérieur à celui d'un serveur isolé. Cartographier les composants partagés avant de décider quels symptômes doivent être agrégés.

### 9.2 Nommage, groupes et tags

Employer des noms stables et compréhensibles pour les hôtes, services et templates. Dans Zabbix, les tags peuvent qualifier le site, l'équipe, l'environnement, l'application ou le niveau de service selon la version. Dans Nagios, les groupes, contacts et noms d'objets structurent une partie de la gouvernance.

Les tags ne remplacent pas la qualité de l'inventaire. Un hôte portant **site=DOU** doit réellement appartenir au site concerné. Les mécanismes d'auto-découverte ne doivent pas placer un hôte inconnu dans un groupe privilégié ni lui attribuer des actions d'administration sans validation.

### 9.3 Sécurité des flux

La plateforme de supervision est sensible, car elle communique avec de nombreux segments et expose des informations sur l'état du parc. Limiter les ports par source et destination, séparer lecture et administration, utiliser des comptes nominatifs, protéger les identifiants, sécuriser l'interface Web et conserver les journaux de changement. Utiliser le chiffrement lorsqu'il est pris en charge par les composants.

~~~mermaid
flowchart LR
  A[Administrateurs nominatifs] -->|HTTPS contrôlé| B[Frontend Web]
  B --> C[Moteur supervision]
  C -->|Flux autorisés| D[Agents]
  C -->|SNMPv3 lecture| E[Routeurs et switches]
  C -->|Sortie contrôlée| F[Relais notification]
~~~

Vérifier qui peut modifier les triggers, les commandes, les médias, les scripts ou les intégrations. Un utilisateur capable de remplacer une commande ou d'élargir les cibles de collecte peut compromettre la détection ou introduire un risque d'exécution. Les droits d'administration doivent être réservés, revus et audités.

### 9.4 Superviser la plateforme elle-même

Surveiller les processus, l'ordonnanceur, les files d'attente, la base, l'espace disque, les retards de collecte, les derniers contacts des proxys et le canal de notification. Si le canal d'envoi tombe, le système peut générer des événements sans que l'équipe les voie. Prévoir un canal indépendant pour les alertes portant sur la plateforme centrale.

~~~mermaid
flowchart TD
  A[Moteur] --> B[Collecte et ordonnanceur]
  A --> C[Base de données]
  A --> D[Agents et proxies]
  A --> E[Notifications]
  B --> F[Contrôles de santé]
  C --> F
  D --> F
  E --> F
  F --> G[Canal indépendant]
~~~

Sauvegarder les configurations Nagios, les plugins maison et les modèles. Pour Zabbix, protéger de façon cohérente la base et la configuration nécessaire à la reconstruction. Une sauvegarde non testée ne prouve pas qu'il sera possible de restaurer l'environnement dans le temps visé.

## 10. Choisir entre Nagios et Zabbix

Les deux solutions peuvent superviser des hôtes, états, seuils et services, mais leur modèle diffère.

| Critère | Nagios Core | Zabbix |
|---|---|---|
| Modèle central | Hôtes, services, commandes et plugins | Hôtes, interfaces, items, triggers, templates et événements |
| Collecte | Plugins et commandes, checks actifs et résultats passifs | Agents, SNMP et types d'items variés selon version |
| Historique et graphes | Données de performance ; outils complémentaires possibles | Historique et tendances intégrés au modèle de données |
| Réutilisation | Templates d'objets, groupes, commandes et héritage | Templates, macros, prototypes et découverte |
| Extension | Plugins et intégrations externes | Types d'items, agents, proxies, prétraitement et intégrations |
| Compétence centrale | Commandes, plugins, états et notifications | Items, triggers, templates, rétention, proxies et actions |
| Point de vigilance | Organisation des configurations et composants associés | Complexité des modèles et volume de collecte |

Nagios est souvent naturel pour une équipe qui veut définir explicitement des contrôles spécialisés et dispose déjà de nombreux plugins. Zabbix convient lorsqu'on veut regrouper collecte, templates, historique, graphes, découverte et actions. Ce sont des tendances, pas une règle absolue : comparer les outils sur un échantillon représentatif du vrai parc.

~~~mermaid
flowchart TD
  A[Besoin et contraintes] --> B{Priorité dominante}
  B -->|Plugins et checks ciblés| C[Évaluer Nagios]
  B -->|Historique et templates| D[Évaluer Zabbix]
  C --> E[Pilote représentatif]
  D --> E
  E --> F[Mesurer qualité et coût]
  F --> G[Décision documentée]
~~~

Une coexistence ou une migration peut être pertinente, mais introduit des risques de doublons et de règles divergentes. Définir quel outil fait foi pour chaque service, où se trouve l'historique de référence et comment les événements sont corrélés.

## 11. Dépannage méthodique

### 11.1 Méthode commune

Lorsqu'une alerte apparaît, commencer par confirmer la cible, la période, le dernier résultat valide et la source de données. Déterminer ensuite si l'on est face à une panne réelle, une mesure absente, un seuil incorrect ou un problème de la plateforme. Ne pas redémarrer immédiatement un service sans recueillir les preuves disponibles : un redémarrage peut effacer des éléments utiles ou aggraver l'incident.

~~~mermaid
flowchart TD
  A[Alerte reçue] --> B[Confirmer cible et heure]
  B --> C{Valeur récente ?}
  C -->|Non| D[Diagnostiquer collecte]
  C -->|Oui| E[Comparer seuil et historique]
  D --> F[Agent réseau accès moteur]
  E --> G[Test indépendant]
  F --> H[Défaut de collecte possible]
  G --> I[Panne réelle ou faux positif]
  H --> J[Tracer résultat et action]
  I --> J
~~~

### 11.2 Diagnostiquer un check Nagios

Lire le statut, le texte complet du plugin, ses arguments, la tentative courante et les logs. Si le check est **UNKNOWN**, examiner en priorité la commande, les droits, la résolution DNS, les bibliothèques, l'authentification et le timeout. Si plusieurs services d'un hôte échouent simultanément, vérifier le contrôle d'hôte, la passerelle et le chemin de gestion. Si le service est disponible par un test indépendant mais le check échoue, le défaut est probablement dans la méthode de contrôle ou son chemin réseau.

~~~mermaid
flowchart TD
  A[Service Nagios non OK] --> B{Type de retour}
  B -->|UNKNOWN| C[Commande et exécution]
  B -->|WARNING ou CRITICAL| D[Mesure et seuil]
  B -->|Hôte inaccessible| E[Route et dépendance]
  C --> F[Arguments droits timeout]
  D --> G[Contre-test autorisé]
  E --> H[Passerelle ou lien]
  F --> I[Recontrôler]
  G --> I
  H --> I
~~~

### 11.3 Diagnostiquer une valeur Zabbix absente

Commencer par l'item et son horodatage : existe-t-il, l'interface est-elle correcte, quelle méthode utilise-t-il, quand la dernière valeur a-t-elle été reçue ? Ensuite vérifier l'agent ou le proxy, les routes, les ports, l'identité de l'hôte, le chiffrement et les logs. Si la valeur est visible mais que le trigger ne passe pas à problème, examiner l'expression, la clé, la fenêtre temporelle et l'historique requis.

~~~mermaid
flowchart TD
  A[Problème Zabbix] --> B[Dernière valeur item ?]
  B -->|Non| C[Agent SNMP proxy réseau]
  B -->|Oui| D[Expression du trigger]
  D --> E{Événement créé ?}
  E -->|Non| F[Seuil unité fenêtre]
  E -->|Oui| G[Action et opérations]
  G --> H[Média destinataire horaires]
  C --> I[Tester connectivité et accès]
  F --> J[Correction et retest]
  H --> J
  I --> J
~~~

### 11.4 Une notification n'est pas reçue

Si l'événement existe mais que le message n'arrive pas, le défaut peut être dans la chaîne de notification et non dans le trigger. Examiner les conditions de l'action, sévérité, tags, utilisateur, média, plage horaire, limitation de répétition, serveur SMTP ou webhook, puis les logs. Tester le média avec la fonction prévue par la version. Modifier le seuil n'aidera pas si le problème se trouve dans l'acheminement.

### 11.5 Files d'attente et charge

Un grand nombre d'alertes simultanées peut représenter une panne réelle, mais aussi un retard de collecte. Surveiller la durée des checks, les files d'attente, les processus de collecte, la base, le disque et l'écart entre la valeur attendue et le dernier échantillon reçu. Augmenter tous les intervalles sans diagnostic peut réduire la charge mais dégrader la détection. Identifier le goulot, vérifier la distribution des hôtes et comparer le volume aux objectifs.

### 11.6 Pourquoi tester depuis le collecteur

Un poste utilisateur et un serveur de supervision peuvent avoir des routes et permissions différentes. Le serveur peut résoudre un nom par un autre DNS ou se trouver derrière une ACL spécifique. Un test « depuis mon PC » ne prouve donc pas que le check configuré fonctionnera depuis Nagios ou le proxy Zabbix. Reproduire les tests depuis le vrai point de collecte et capturer la même destination, la même résolution et le résultat horodaté.

### 11.7 Corréler sans masquer

Une corrélation correcte simplifie une cascade de symptômes autour d'une cause commune. Elle ne doit pas supprimer les événements indépendants ou empêcher une équipe de voir une dégradation locale. Vérifier les dépendances sur plusieurs scénarios : panne du parent, panne d'un seul service, panne du collecteur et événements qui coïncident mais n'ont pas de cause commune.

## 12. Atelier pratique : petite infrastructure de laboratoire

### 12.1 Topologie

Utiliser un réseau de laboratoire réservé comprenant une machine de supervision, un serveur Linux, un serveur Web de test, un client et un commutateur administrable ou simulateur SNMP si disponible. Les adresses et comptes sont fictifs. N'exécute pas de scans sur des réseaux tiers et ne modifie pas un équipement de production pour réaliser ces exercices.

~~~mermaid
flowchart LR
  A[Poste apprenant] --> B[Switch de laboratoire]
  B --> C[Serveur Web test]
  B --> D[Serveur Linux test]
  B --> E[Routeur ou simulateur SNMP]
  B --> F[Nagios ou Zabbix]
  F --> C
  F --> D
  F --> E
~~~

### 12.2 Définir la matrice de contrôle avant de configurer

Pour chaque cible, noter le but, le signal, la fréquence, le résultat attendu et l'action en cas d'écart.

| Cible | Signal | Ce que le test prouve | Ce qu'il ne prouve pas |
|---|---|---|---|
| Routeur | ICMP | Réponse depuis le point de collecte | Santé de toutes les interfaces ou routage de bout en bout |
| Routeur | SNMP interface | Valeur exposée pour l'interface visée | Exactitude de tous les compteurs sans validation |
| Serveur Linux | Agent | Données système autorisées disponibles | Fonctionnement complet d'une application |
| Serveur Web | HTTP | Réponse au test configuré | Toutes les transactions métier |
| API | Requête fonctionnelle | Réponse conforme au contrat de test | Absence de tous les défauts possibles |

Cette matrice empêche de confondre un signal technique simple avec l'expérience de l'utilisateur. Elle rend aussi les seuils et résultats attendus vérifiables par un autre technicien.

### 12.3 Atelier Nagios

1. Vérifier la présence des plugins requis et lire leur aide.
2. Lancer les checks manuellement sur les cibles de laboratoire et consigner code de retour, sortie, durée et arguments.
3. Créer un hôte et un service avec des noms explicites et le modèle adapté à l'installation.
4. Définir intervalles, tentatives et options de notification selon le but du test.
5. Valider la configuration avant de la recharger.
6. Déclencher un échec contrôlé, par exemple en arrêtant le serveur Web de test ou en filtrant son port dans le laboratoire.
7. Observer l'état, les tentatives, la notification et la récupération.
8. Restaurer le service et vérifier que le check redevient nominal.

Ne coupe jamais un lien de production pour créer un scénario de panne. Le moyen de restauration doit être préparé avant de démarrer un test qui modifie l'état d'un système.

### 12.4 Atelier Zabbix

1. Créer un hôte avec un nom stable et l'interface adaptée.
2. Lier un template approprié au rôle, sans ajouter d'items inutiles.
3. Vérifier la configuration agent active/passive ou SNMP, y compris les règles de pare-feu.
4. Contrôler la fraîcheur des dernières valeurs et la cohérence des unités.
5. Créer ou utiliser un trigger avec un seuil et une persistance justifiés.
6. Configurer une action et un média ; valider la réception d'un test.
7. Simuler une panne contrôlée, observer l'événement puis vérifier la récupération.
8. Archiver les captures utiles, les résultats de tests et les limites de chaque mesure.

~~~mermaid
flowchart TD
  A[Créer un hôte pilote] --> B[Lier le template]
  B --> C[Contrôler valeurs fraîches]
  C --> D[Tester le trigger]
  D --> E[Tester action et média]
  E --> F[Simuler panne]
  F --> G[Valider récupération]
~~~

### 12.5 Étudier quatre pannes de base

- **Panne de service seul** : l'hôte répond, mais le port ou la transaction échoue. L'alerte doit cibler le service.
- **Perte de connectivité** : la cible devient inaccessible ; les contrôles dépendants peuvent générer plusieurs symptômes.
- **Perte de collecte** : l'agent ou le proxy est inaccessible alors que le service peut continuer de fonctionner.
- **Notification défaillante** : l'événement existe, mais le canal d'acheminement ne délivre rien.

Les quatre cas doivent aboutir à des diagnostics différents. Si un seul contrôle sert à les distinguer, le modèle de supervision est trop pauvre.

### 12.6 Livrable du laboratoire

Le rapport doit comporter la topologie, les versions, la liste des contrôles, les fréquences, les seuils, les résultats attendus, les tests de panne et de récupération, les preuves d'alerte et les actions restantes. Ne pas inclure les secrets SNMP, les mots de passe, les clés privées ou les tokens dans les captures diffusées. Pour chaque test, préciser ce qu'il prouve réellement et ce qui n'a pas été vérifié.

### 12.7 Critères d'acceptation

Le laboratoire est réussi lorsque les contrôles sont reproductibles, la cible et le service sont distingués, les données sont fraîches, les alertes ont le bon propriétaire, le canal de notification a été testé et le rétablissement est confirmé. L'apprenant doit pouvoir simuler une panne sans dégrader la production, revenir à l'état initial et expliquer pourquoi chaque alerte a été générée. Un écran vert seul n'est pas une preuve suffisante de validation.

## 13. Exercices avec corrigés détaillés

### Exercice 1 — Le ping est vert mais le site est inaccessible

**Situation.** Nagios indique que le serveur Web répond au ping ; les utilisateurs reçoivent une erreur HTTP.

**Corrigé.** Tester le port TCP, le code HTTP, le contenu attendu, le certificat TLS, le DNS et les dépendances applicatives depuis un point de collecte autorisé. Lire les journaux Web et applicatifs selon les permissions. Le ping démontre seulement la réponse au test ICMP ; il ne prouve pas que la transaction métier fonctionne.

### Exercice 2 — Un plugin retourne UNKNOWN

**Situation.** Un check affiche UNKNOWN et parle d'une erreur de résolution DNS.

**Corrigé.** Vérifier les arguments du plugin, reproduire la résolution depuis le serveur Nagios, examiner la configuration DNS, les droits et le réseau utilisé. UNKNOWN signifie que le plugin n'a pas produit un statut fiable ; le service peut être sain ou non. Réaliser un test indépendant avant de conclure.

### Exercice 3 — Zabbix collecte les données mais n'ouvre aucun problème

**Situation.** Les valeurs CPU sont visibles ; le dépassement prévu n'entraîne pas d'événement.

**Corrigé.** Vérifier le nom de l'hôte dans l'expression, la clé réelle de l'item, le type et l'unité, la fenêtre temporelle, l'historique requis et les conditions de récupération. Confirmer que les données dépassent réellement la condition exprimée. Une valeur présente ne garantit pas que le trigger examine la bonne valeur.

### Exercice 4 — Un événement existe mais aucun courriel n'arrive

**Corrigé.** Contrôler les conditions et opérations de l'action, le média de l'utilisateur, son adresse, les horaires, la sévérité, les règles de répétition et les logs du canal d'envoi. Tester le média par le mécanisme prévu. Ne pas changer le trigger si le problème se trouve dans l'acheminement.

### Exercice 5 — Une interface semble utiliser 115 % de sa capacité

**Corrigé.** Vérifier le type de compteur, le débit nominal configuré, l'unité, la durée entre échantillons, le redémarrage de l'équipement et le débordement d'un compteur. Calculer la différence sur une durée valide puis comparer à une autre mesure. Ne pas déclarer une saturation tant que la formule et le compteur n'ont pas été vérifiés.

### Exercice 6 — Cent alertes arrivent en même temps

**Corrigé.** Aligner les événements dans le temps, vérifier le périmètre du site, inspecter la passerelle et les dépendances communes. Déterminer s'il existe un incident parent qui explique une partie des symptômes. Ne pas supprimer toutes les alertes : une panne indépendante peut se produire en parallèle. Les dépendances doivent réduire le bruit tout en conservant l'information utile au diagnostic.

### Exercice 7 — L'agent Zabbix ne transmet plus après une règle de pare-feu

**Corrigé.** Identifier le mode de collecte. Pour un check passif, vérifier le chemin serveur/proxy vers l'agent et le filtrage TCP 10050. Pour un check actif, vérifier la connexion sortante de l'agent vers le serveur/proxy et le port généralement 10051. Vérifier aussi les paramètres Server, ServerActive, Hostname, le chiffrement, les routes et les logs. Ne pas ouvrir le port à toutes les sources.

### Exercice 8 — Une alerte CPU survient chaque nuit pendant une sauvegarde

**Corrigé.** Comparer les données aux horaires connus et déterminer si le pic affecte réellement le service. Examiner latence, files d'attente et taux d'erreur, pas seulement le CPU. Ajouter une fenêtre temporelle ou une règle plus appropriée si le comportement normal est documenté. Conserver l'alerte si une autre mesure montre que l'opération dégrade le service.

### Exercice 9 — Estimer le volume de collecte

**Situation.** On supervise 600 hôtes avec 80 items en moyenne, chacun toutes les 60 secondes.

**Corrigé.** L'ordre de grandeur est de 600 × 80 / 60, soit environ 800 valeurs par seconde. Ce chiffre n'est pas un calcul exact de capacité de base de données : les types d'items, prétraitements, triggers, pics, valeurs dépendantes, événements et durées de rétention changent la charge réelle. Tester un pilote et mesurer la latence, les files d'attente et la croissance de base.

### Exercice 10 — Le dashboard annonce 99,95 % mais les utilisateurs signalent des erreurs

**Corrigé.** Vérifier le périmètre et le point de mesure de la disponibilité. Un ping ou une simple réponse HTTP peut être nominale alors que les transactions métier échouent. Ajouter un contrôle synthétique représentatif ou une mesure de résultat utilisateur, documenter le changement de méthode et ne pas comparer les séries sans signaler les différences de définition.

### Exercice 11 — Réviser un seuil d'interface

**Situation.** Un lien est régulièrement à 85 % de charge, sans perte ni latence supplémentaire, alors que l'équipe reçoit une alerte critique.

**Corrigé.** Confirmer la capacité nominale, l'horaire, la stabilité de la tendance, les erreurs et les besoins de service. Si le seuil est trop sensible, réviser la gravité ou la persistance et documenter les raisons. Ne pas ignorer une tendance de croissance : une mesure qui ne déclenche pas d'incident immédiatement peut tout de même justifier une action de capacité.

### Exercice 12 — Distinguer panne de la cible et panne de collecte

**Situation.** Les dernières mesures d'un serveur ont vingt minutes alors que l'application semble disponible.

**Corrigé.** Vérifier le mode d'agent, le chemin réseau depuis la plateforme, le dernier succès, le pare-feu et le statut du serveur. Exécuter un test de service indépendant. Présenter séparément la disponibilité du service et la fraîcheur de la collecte. Le fait que l'application réponde ne signifie pas que la supervision collecte correctement.

## 14. Défi final : construire une supervision défendable

Une application métier est utilisée dans plusieurs agences. Elle dépend d'un lien WAN, d'un routeur central, d'un DNS, d'une API interne et d'une base de données. L'équipe veut déterminer si le problème signalé est une perte de connectivité, une saturation, une panne applicative ou une absence de collecte. Elle veut aussi limiter les alertes en cascade et produire un rapport de cause racine.

**Travail demandé**

1. Dessiner la topologie et indiquer le point de collecte de chaque check.
2. Définir quatre signaux distincts : reachability, service applicatif, capacité et fraîcheur des données.
3. Décrire les hôtes et services Nagios, les plugins nécessaires et l'interprétation de leurs codes de retour.
4. Décrire les hôtes, items, templates, triggers, tags et actions Zabbix du même scénario.
5. Justifier fréquence, seuils, confirmation temporelle, récupération et gravité.
6. Définir des dépendances qui regroupent les symptômes de la perte WAN sans masquer une panne indépendante.
7. Décrire les flux, ports, protocoles et mesures de sécurité.
8. Tester panne et récupération en laboratoire.
9. Préparer le message de notification et la séquence d'escalade.
10. Définir les preuves pour la RCA et trois indicateurs de qualité de supervision.

**Correction attendue**

La topologie fait apparaître les dépendances réseau et applicatives ; les tests de disponibilité ne sont pas confondus avec la disponibilité métier. Les plugins Nagios sont testés, les arguments documentés et la logique SOFT/HARD comprise. Les items Zabbix existent réellement, leurs valeurs sont fraîches, les triggers utilisent une unité et une fenêtre correctes, et les notifications sont testées de bout en bout. Les flux de gestion sont limités et les identifiants protégés. La panne WAN peut produire un incident parent avec des symptômes corrélés, tout en conservant des contrôles indépendants. Les tests couvrent la panne, la récupération et la fraîcheur. Le compte rendu indique ce qui est établi, ce qui reste incertain et qui doit suivre les actions.

## 15. Checklist d'exploitation avant production

- [ ] Tous les actifs critiques ont un nom stable, un propriétaire, une criticité et des dépendances documentées.
- [ ] Chaque check possède une définition, une unité, une fréquence et un résultat attendu.
- [ ] Les plugins Nagios ont été testés et leurs codes de retour sont compris.
- [ ] Les objets, macros, intervalles, tentatives et dépendances Nagios sont validés avant rechargement.
- [ ] Les items Zabbix existent et fournissent des valeurs récentes.
- [ ] Les templates et règles de découverte ne créent pas des milliers d'items sans usage.
- [ ] Les triggers et leurs conditions de récupération ont été testés.
- [ ] Les actions, médias, utilisateurs et canaux d'escalade sont testés de bout en bout.
- [ ] Les flux de gestion sont limités aux sources autorisées et utilisent le chiffrement disponible.
- [ ] Les identifiants sensibles sont absents des fichiers versionnés, rapports diffusés et captures.
- [ ] Le serveur, la base, les proxies, les agents et les canaux de notification sont eux-mêmes supervisés.
- [ ] Les configurations et la base sont sauvegardées et une restauration a été testée.
- [ ] Les fenêtres de maintenance ont une fin explicite et la reprise de la collecte est vérifiée.
- [ ] Les faux positifs, alertes dupliquées et données périmées sont revus périodiquement.
- [ ] Les incidents significatifs peuvent être reconstruits à partir de mesures, journaux, horodatages et changements.

## 16. Glossaire

| Terme | Définition |
|---|---|
| Agent | Composant installé sur une cible qui expose ou transmet des données. |
| Check actif Nagios | Contrôle planifié et lancé par Nagios à partir d'une commande. |
| Résultat passif Nagios | Résultat produit ailleurs puis soumis au moteur pour être évalué. |
| Check passif Zabbix | Le serveur ou proxy demande une donnée à l'agent. |
| Check actif Zabbix | L'agent demande sa configuration et transmet des valeurs au serveur ou proxy. |
| Plugin Nagios | Programme ou script qui renvoie un code et une sortie selon le contrat du plugin. |
| Item | Objet Zabbix qui définit une donnée collectée, reçue ou calculée. |
| Trigger | Expression Zabbix qui évalue des valeurs pour signaler un problème. |
| Template | Ensemble réutilisable d'items, triggers et autres objets liés aux hôtes. |
| LLD | Découverte de bas niveau qui détecte des entités et génère des objets à partir de prototypes. |
| MIB | Description des objets qu'un équipement expose pour la gestion SNMP. |
| OID | Identifiant d'un objet dans la hiérarchie SNMP. |
| Polling | Interrogation régulière d'une cible pour obtenir un état ou une mesure. |
| Trap SNMP | Message envoyé par un équipement lors d'un événement configuré. |
| Proxy Zabbix | Collecteur intermédiaire pour un groupe d'hôtes ou un site. |
| SOFT/HARD | États Nagios qui distinguent un résultat transitoire d'un état confirmé. |
| Prétraitement | Transformation ou validation d'une valeur avant son stockage ou usage dans Zabbix. |
| Historique | Valeurs individuelles conservées selon la rétention. |
| Tendance | Agrégat temporel de métriques numériques utile sur des périodes longues. |
| Fraîcheur | Ancienneté d'une donnée par rapport au moment attendu de collecte. |
| Faux positif | Alerte ne correspondant pas à une condition actionnable selon les critères fixés. |
| Dépendance | Relation entre un service supervisé et un composant dont il dépend. |
| Fatigue d'alerte | Réduction de l'attention liée à un trop grand nombre de notifications peu utiles. |
| RCA | Analyse d'un incident visant à expliquer ses mécanismes et vérifier des actions préventives. |

## 17. Références officielles

Les options, syntaxes et fonctions évoluent selon les versions. Consulter la documentation correspondant à la version réellement installée avant tout déploiement.

- [Nagios Core — définitions d'objets](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/objectdefinitions.html)
- [Nagios Core — contrat et codes de retour des plugins](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/pluginapi.html)
- [Nagios Core — dépendances hôtes et services](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/dependencies.html)
- [Zabbix — manuel officiel courant](https://www.zabbix.com/documentation/current/en/manual)
- [Zabbix — agents](https://www.zabbix.com/documentation/current/en/manual/concepts/agent)
- [Zabbix — notifications et actions](https://www.zabbix.com/documentation/current/en/manual/config/notifications)
- [Zabbix — types de médias](https://www.zabbix.com/documentation/current/en/manual/config/notifications/media)

La compétence essentielle est de relier un signal à ce qu'il démontre, aux limites de sa mesure et à la décision qu'il doit déclencher. Nagios apporte un modèle de checks, plugins et états ; Zabbix apporte un modèle de collecte, données, triggers et templates. Dans les deux cas, la qualité dépend de la méthode de mesure, de la sécurité, des tests, de la fraîcheur de l'information et de la capacité de l'équipe à interpréter les événements.
