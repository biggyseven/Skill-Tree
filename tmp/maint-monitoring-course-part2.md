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
