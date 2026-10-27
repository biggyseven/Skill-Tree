# Introduction à la maintenance préventive

> **Mise en contexte**
>
> Tu es technicien débutant dans une entreprise qui utilise des ordinateurs, des serveurs, des équipements réseau, des imprimantes et des services cloud. Depuis plusieurs semaines, l’équipe traite les mêmes problèmes : des ordinateurs manquent d’espace disque, une imprimante se bloque régulièrement, les mises à jour redémarrent parfois les postes au mauvais moment et les alertes de sauvegarde ne sont pas toujours examinées.
>
> Chaque incident est traité lorsqu’il gêne déjà le travail. Les techniciens passent alors d’une urgence à une autre, sans disposer de temps pour comprendre les répétitions. Pourtant, certains signes étaient visibles avant les interruptions : l’espace libre diminuait, les journaux contenaient des avertissements, les sauvegardes n’étaient pas vérifiées et les opérations périodiques n’étaient pas planifiées.
>
> La maintenance préventive consiste à organiser des contrôles et des tâches avant qu’une défaillance ne perturbe le service. Elle ne promet pas qu’aucune panne ne surviendra. Elle cherche à réduire les risques, détecter les dérives plus tôt, préparer la réponse et maintenir les équipements dans un état compatible avec leur usage.
>
> Dans ce cours, tu vas apprendre à créer un plan préventif raisonnable, à déterminer ce qui mérite d’être contrôlé, à choisir des fréquences justifiées, à préparer une fenêtre de travail, à exécuter une check-list, à conserver des preuves et à améliorer le programme à partir des résultats. Tu ne vas pas appliquer des fréquences universelles au hasard : tu apprendras à les définir à partir de la documentation du fabricant, de la criticité, des données d’exploitation, de l’environnement et des règles de ton organisation.

## 1. Objectifs pédagogiques

À la fin de ce cours, tu seras capable de :

- expliquer l’objectif de la maintenance préventive et ses limites ;
- distinguer maintenance corrective, préventive systématique, conditionnelle et prédictive ;
- comprendre la différence entre une tâche de routine, une inspection et une opération nécessitant un arrêt ou une autorisation spécifique ;
- décrire les conséquences d’une maintenance absente, excessive ou mal planifiée ;
- établir un inventaire simple des actifs à maintenir ;
- relier un actif à un service, à des utilisateurs et à des dépendances ;
- évaluer la criticité d’un actif avec une méthode simple et documentée ;
- construire une fiche de tâche préventive comprenant une fréquence justifiée, un responsable, les prérequis, les risques et les critères de réussite ;
- organiser un calendrier tenant compte des fenêtres d’intervention, du temps de préparation, des essais et de la remise en service ;
- effectuer des contrôles non destructifs à partir de procédures autorisées ;
- reconnaître les cas où il faut arrêter l’opération et solliciter une personne qualifiée ;
- distinguer la réussite d’une tâche planifiée de l’efficacité réelle du programme ;
- mesurer quelques indicateurs sans les interpréter abusivement ;
- rédiger un compte rendu utile et actualiser le plan en fonction des résultats.

## 2. Qu’est-ce que la maintenance préventive ?

### 2.1 Définition

La maintenance préventive regroupe des activités décidées à l’avance pour réduire la probabilité d’une dégradation ou d’une défaillance. Elle peut être déclenchée selon un calendrier, un nombre d’heures d’utilisation, un compteur, un état observé ou une tendance mesurée.

En informatique, elle peut comprendre :

- vérifier les résultats de sauvegarde et réaliser des essais de restauration ;
- suivre l’espace disque, les températures et l’état des composants ;
- examiner les alertes importantes de supervision ;
- vérifier les dates de support et les versions des logiciels ;
- planifier les mises à jour de sécurité selon les risques et les procédures ;
- inspecter l’état du matériel dans les limites de compétence et de sécurité ;
- contrôler la capacité des services ;
- vérifier les configurations de référence et la documentation ;
- tester les procédures de récupération ;
- examiner les incidents répétés afin de trouver une mesure préventive ;
- contrôler les pièces de rechange et les moyens nécessaires à une intervention.

La maintenance préventive n’est donc pas seulement un nettoyage physique ou une série de mises à jour. Elle comprend des contrôles techniques, des vérifications documentaires, de la planification et des décisions de risque.

### 2.2 Pourquoi agir avant la panne ?

Une panne peut avoir plusieurs effets : interruption de service, perte de temps, coût de réparation, perte ou corruption de données, baisse de confiance ou risque de sécurité. Une tâche préventive tente d’identifier un état défavorable avant qu’il ne cause une interruption et de réduire la probabilité ou la gravité de celle-ci.

Prenons un serveur de fichiers. Une inspection périodique peut révéler que le volume de données approche de sa capacité. Si l’alerte est traitée tôt, l’équipe peut analyser la croissance, libérer de l’espace de manière approuvée ou planifier une extension. Si elle ignore l’indicateur, une saturation peut empêcher les utilisateurs d’enregistrer de nouveaux documents.

Autre exemple : un système de sauvegarde indique que les tâches se terminent avec succès. Cela ne prouve pas encore qu’une restauration fonctionnera. Un essai de restauration dans un environnement approprié peut vérifier le processus de récupération avant que l’organisation en ait besoin lors d’un incident majeur.

### 2.3 La prévention réduit le risque, elle ne garantit pas zéro panne

Un équipement correctement entretenu peut toujours tomber en panne. Un composant peut présenter un défaut imprévisible, une mise à jour peut provoquer une régression, une coupure externe peut affecter un service et une erreur humaine peut se produire.

L’objectif réaliste est de rendre le système plus maîtrisé :

1. connaître les équipements et les services ;
2. repérer les défauts qui peuvent être détectés tôt ;
3. définir des contrôles pertinents ;
4. planifier les tâches dans de bonnes conditions ;
5. vérifier les résultats ;
6. apprendre des anomalies et incidents constatés.

Un plan préventif doit aussi rester proportionné. Vérifier inutilement un équipement toutes les heures peut consommer du temps sans réduire le risque de façon utile. Une fréquence trop faible peut laisser passer un défaut important. La fréquence doit être justifiée, puis adaptée aux observations.

### Schéma 1 — La logique préventive

~~~mermaid
flowchart TD
    A[Connaître l'actif et son usage] --> B[Identifier les risques et les signes de dégradation]
    B --> C[Définir les contrôles]
    C --> D[Planifier et préparer]
    D --> E[Exécuter la tâche]
    E --> F[Mesurer et conserver les résultats]
    F --> G{Anomalie détectée ?}
    G -->|Non| H[Maintenir le plan et suivre les tendances]
    G -->|Oui| I[Qualifier et traiter l'anomalie]
    I --> J[Réviser la tâche ou la fréquence si nécessaire]
    J --> C
~~~

## 3. Les types de maintenance et leur complémentarité

Les termes utilisés peuvent différer selon l’entreprise et le secteur. Il faut donc connaître la classification de l’organisation et la documentation du fabricant.

### 3.1 Maintenance corrective

La maintenance corrective intervient après la détection d’un défaut ou d’une défaillance pour rétablir la fonction attendue. Elle peut prendre la forme d’un dépannage provisoire ou d’une réparation plus durable.

Exemple : un bloc d’alimentation de poste de travail ne fournit plus d’énergie. Le technicien confirme le diagnostic, remplace le composant approprié selon la procédure et teste le fonctionnement.

La maintenance corrective est nécessaire même avec un bon programme préventif. Certaines pannes ne peuvent pas être prédites à partir des informations disponibles. Le but du préventif n’est donc pas de supprimer toute correction, mais de réduire les défaillances évitables et de préparer une réponse plus efficace.

### 3.2 Maintenance préventive systématique ou programmée

La tâche se déroule à des intervalles définis à l’avance : par calendrier ou selon un compteur d’usage. Elle est utile lorsque les instructions du fabricant, les exigences locales ou l’expérience justifient une périodicité.

Exemples indicatifs :

- contrôler périodiquement un résultat de sauvegarde ;
- examiner à intervalles prévus les alertes de capacité ;
- vérifier les procédures de récupération selon un planning ;
- effectuer un contrôle planifié d’un actif selon les instructions du fabricant ;
- réviser un inventaire à une date déterminée.

Une fréquence inscrite dans un calendrier n’est pas automatiquement pertinente. Il faut pouvoir expliquer pourquoi la tâche est nécessaire à cet intervalle, quelle est la preuve attendue et comment le programme sera réévalué.

### 3.3 Maintenance conditionnelle

La tâche dépend de l’état observé de l’actif ou d’un indicateur. Au lieu d’attendre uniquement une date fixe, l’équipe examine un paramètre et intervient lorsque les critères définis sont atteints.

Exemples :

- examiner une augmentation durable de la température ;
- analyser une hausse des erreurs signalées par un composant ;
- investiguer un volume qui approche d’un seuil de capacité ;
- déclencher un contrôle complémentaire lorsqu’un compteur dépasse une limite définie ;
- inspecter un équipement lorsqu’une alerte fiable apparaît.

Une alerte est un signal à analyser, pas toujours une preuve de défaillance. Le seuil doit être défini en fonction du système, de ses usages, de ses tolérances et de son contexte.

### 3.4 Maintenance prédictive

La maintenance prédictive exploite des observations et des tendances pour estimer la possibilité d’une défaillance future. Elle peut faire appel à des historiques, à des séries temporelles ou à des modèles analytiques.

Exemple : sur une infrastructure qui mesure régulièrement la température, les erreurs et la charge, une évolution durable peut justifier une analyse plus approfondie avant la perte de service.

Il ne faut pas confondre prédiction et certitude. Un modèle peut produire une fausse alerte ou ne pas détecter un défaut nouveau. Toute décision doit tenir compte de la qualité des données, des limites du modèle et des conséquences d’une action incorrecte.

### Schéma 2 — Choisir le mode de surveillance

~~~mermaid
flowchart TD
    A[Actif ou service à surveiller] --> B{Documentation ou règle imposant un intervalle ?}
    B -->|Oui| C[Tâche systématique planifiée]
    B -->|Non| D{Un indicateur d'état utile existe-t-il ?}
    D -->|Oui| E[Contrôle conditionnel avec seuil justifié]
    D -->|Non| F{Données fiables et historiques suffisants ?}
    F -->|Oui| G[Évaluer la pertinence d'une approche prédictive]
    F -->|Non| H[Définir une inspection simple ou améliorer la mesure]
    C --> I[Consigner le résultat]
    E --> I
    G --> I
    H --> I
~~~

### 3.5 Run-to-failure : attendre la défaillance

Dans certaines situations, une organisation peut décider de remplacer ou réparer un élément seulement lorsqu’il tombe en panne. Cette stratégie est parfois appelée fonctionnement jusqu’à défaillance.

Elle ne doit pas être appliquée automatiquement. Elle peut être envisageable pour un élément peu critique, peu coûteux et facilement remplaçable, lorsque la conséquence d’une panne est acceptable et documentée. Elle peut être inacceptable pour un service critique, une fonction de sécurité ou un équipement dont la défaillance expose des personnes ou des données.

La décision doit tenir compte de la criticité, du coût du remplacement, du délai d’approvisionnement, de la redondance, du temps d’arrêt et des exigences de conformité.

### 3.6 Tableau de comparaison

| Mode | Déclencheur | Avantage | Limite ou risque |
|---|---|---|---|
| Correctif | Défaut constaté | Rétablit une fonction défaillante | L’impact est parfois déjà présent |
| Préventif systématique | Date ou compteur planifié | Facile à programmer et à auditer | Peut être trop fréquent ou manquer une dérive entre deux dates |
| Conditionnel | État ou seuil mesuré | Relie l’action à l’état réel | Dépend de mesures fiables et de seuils pertinents |
| Prédictif | Tendance ou estimation | Peut aider à anticiper certains défauts | Dépend de données et de modèles dont les limites doivent être connues |
| Fonctionnement jusqu’à défaillance | Défaillance effective | Peut éviter une maintenance inutile sur un élément non critique | Risque d’interruption ou de dommage si la criticité est mal évaluée |

## 4. Construire l’inventaire des actifs

On ne peut pas planifier correctement la maintenance d’un équipement que l’on ne sait pas identifier. L’inventaire constitue donc la base du plan préventif.

### 4.1 Quelles informations faut-il connaître ?

Un inventaire de départ peut contenir :

| Champ | Utilité |
|---|---|
| Identifiant unique | Éviter de confondre deux équipements similaires |
| Nom ou étiquette | Faciliter l’identification sur le terrain |
| Type | Poste de travail, serveur, switch, imprimante, onduleur, service cloud, etc. |
| Localisation ou périmètre logique | Trouver l’actif et comprendre son environnement |
| Propriétaire ou équipe responsable | Savoir qui coordonne les décisions |
| Service supporté | Comprendre la conséquence potentielle d’une défaillance |
| Criticité | Aider à choisir le niveau de préparation et de contrôle |
| Modèle, version ou configuration | Retrouver la documentation appropriée |
| Date de mise en service et état du support | Anticiper obsolescence et remplacement |
| Garanties et contrat de maintenance | Savoir quand contacter un fournisseur |
| Dépendances | Identifier les éléments qui utilisent ou alimentent cet actif |
| Historique d’intervention | Repérer les récurrences et les actions déjà réalisées |
| Localisation de la documentation | Accéder aux procédures et plans approuvés |

Tous les champs ne sont pas indispensables pour chaque petit équipement. Les informations doivent être proportionnées et protégées. Les données d’inventaire peuvent être sensibles lorsqu’elles décrivent les composants, versions et dépendances d’une infrastructure.

### 4.2 Inventaire physique et inventaire logique

L’inventaire physique concerne les équipements matériels : serveurs, postes, commutateurs, onduleurs, baies, câbles et périphériques.

L’inventaire logique concerne les systèmes, applications, instances cloud, configurations, licences, comptes de service et dépendances logicielles.

Un même service peut dépendre de plusieurs composants physiques et logiques. Pour comprendre l’effet d’une maintenance, il faut connaître les dépendances utiles, et pas seulement la liste des équipements.

### 4.3 Comment démarrer sans avoir un inventaire parfait ?

Commence par un périmètre limité :

1. recenser les actifs qui soutiennent les activités les plus importantes ;
2. identifier le responsable de chaque actif ;
3. enregistrer sa fonction et les dépendances essentielles ;
4. collecter les informations de documentation et de support ;
5. noter les champs inconnus au lieu de les inventer ;
6. vérifier l’inventaire lors des interventions et des changements ;
7. élargir progressivement le périmètre.

Un inventaire partiellement fiable et explicitement incomplet est préférable à un document qui donne une fausse impression de certitude.

### Schéma 3 — L’inventaire comme fondation

~~~mermaid
flowchart TD
    A[Actif identifié] --> B[Type et configuration]
    A --> C[Service supporté]
    A --> D[Responsable et localisation]
    A --> E[Documentation et support]
    B --> F[Évaluation de la criticité]
    C --> F
    D --> G[Organisation de l'intervention]
    E --> H[Définition des contrôles]
    F --> I[Plan préventif]
    G --> I
    H --> I
~~~

## 5. Évaluer la criticité avant de planifier

Tous les actifs ne nécessitent pas le même niveau d’effort. Un poste de test isolé n’a pas les mêmes conséquences en cas de panne qu’un système de stockage central utilisé par plusieurs équipes.

### 5.1 Les questions à poser

- Quelle activité métier dépend de l’actif ?
- Combien d’utilisateurs ou de services sont affectés si l’actif devient indisponible ?
- Existe-t-il une solution de secours réellement testée ?
- Y a-t-il un risque pour les données, la sécurité ou les personnes ?
- Le remplacement est-il facile ou nécessite-t-il une pièce rare ?
- Les équipes peuvent-elles tolérer une interruption ?
- L’actif a-t-il présenté des défauts répétés ?
- Existe-t-il une obligation contractuelle ou réglementaire particulière ?

L’évaluation doit impliquer les personnes qui connaissent le service et ses contraintes. Le technicien peut fournir les observations techniques, mais il ne doit pas supposer seul la valeur métier du service.

### 5.2 Une grille simple d’impact

Pour un premier exercice, tu peux noter l’impact de 1 à 5. Cette échelle est un outil local de discussion, pas une norme universelle.

| Niveau | Interprétation indicative |
|---|---|
| 1 — Très faible | Actif non essentiel, impact limité, remplacement simple |
| 2 — Faible | Gêne locale, activité alternative disponible |
| 3 — Moyen | Plusieurs utilisateurs ou une activité importante sont perturbés |
| 4 — Élevé | Service important indisponible, reprise difficile ou interruption coûteuse |
| 5 — Critique | Fonction essentielle, risque majeur pour l’activité, les données, la sécurité ou les personnes |

Cette note doit être accompagnée d’une justification. Si deux actifs ont le même score mais des risques de nature différente, ils peuvent nécessiter des traitements différents.

### 5.3 Ne pas confondre criticité et état actuel

La criticité indique les conséquences potentielles d’une défaillance. L’état actuel décrit ce que l’on observe aujourd’hui. Un actif critique peut être en bon état ; il peut malgré tout nécessiter une surveillance adaptée, une récupération testée et une procédure claire.

À l’inverse, un poste de faible criticité peut présenter un défaut évident qui mérite une correction immédiate pour des raisons de sécurité ou parce qu’il est nécessaire à un utilisateur.

### 5.4 Priorité du programme préventif

Une règle raisonnable est de commencer par les actifs à fort impact, surtout lorsque les conséquences ne sont pas maîtrisées ou que la procédure de reprise n’est pas testée. On examine ensuite les actifs présentant des dégradations, les équipements proches d’une limite et les tâches exigées par la documentation ou les règles applicables.

Il faut conserver une place aux tâches de routine et aux opérations de base. Mais lorsque les ressources sont limitées, la criticité permet d’expliquer pourquoi une tâche est réalisée avant une autre.

### Schéma 4 — Prioriser le portefeuille d’actifs

~~~mermaid
flowchart TD
    A[Inventaire de départ] --> B[Évaluer l'impact métier]
    A --> C[Examiner l'état observé]
    A --> D[Identifier dépendances et redondance]
    B --> E[Décision de criticité]
    C --> E
    D --> E
    E --> F{Risque élevé ou obligation prioritaire ?}
    F -->|Oui| G[Contrôle renforcé et plan validé]
    F -->|Non| H[Tâche proportionnée et planifiée]
    G --> I[Suivi et réévaluation]
    H --> I
~~~

## 6. Concevoir une tâche préventive de qualité

Une tâche préventive doit être suffisamment précise pour que deux techniciens formés puissent comprendre ce qui est attendu et comparer les résultats.

### 6.1 Les éléments d’une fiche de tâche

| Élément | Question à laquelle il répond |
|---|---|
| Identifiant de la tâche | Comment retrouver cette tâche dans le plan ? |
| Actif ou périmètre | Sur quel élément intervient-on ? |
| Objectif | Pourquoi cette tâche est-elle nécessaire ? |
| Déclencheur ou fréquence | Quand doit-elle être réalisée et sur quelle justification ? |
| Responsable | Qui exécute et qui valide ? |
| Prérequis | Quelles conditions doivent être réunies ? |
| Outils et documents | De quoi l’intervenant a-t-il besoin ? |
| Risques et mesures de prévention | Qu’est-ce qui pourrait mal se passer et comment le limiter ? |
| Étapes | Quels contrôles ou gestes sont autorisés ? |
| Critères de réussite | Quel résultat mesurable est attendu ? |
| Conduite en cas d’écart | Quand arrêter, ouvrir un incident ou escalader ? |
| Preuve | Quelle donnée montre que la tâche a été réalisée ? |
| Durée estimée | Combien de temps prévoir, y compris préparation et restitution ? |
| Suivi | Quelle action est requise si une anomalie est trouvée ? |

La fiche doit être adaptée au niveau de risque. Une inspection visuelle simple ne nécessite pas forcément un dossier aussi détaillé qu’une intervention avec arrêt d’un service critique. En revanche, chaque tâche doit avoir un objectif et un résultat attendu.

### 6.2 Écrire une tâche mesurable

Consigne trop vague : « Vérifier le serveur ».

Consigne plus utile : « Consulter le tableau de supervision approuvé pour le serveur identifié, vérifier les alertes de disponibilité, capacité et température sur la période définie, enregistrer les écarts dans le ticket prévu et ouvrir une investigation si un seuil local est dépassé ».

La seconde formulation précise le périmètre et la preuve, sans imposer des valeurs arbitraires. Les seuils et périodes exacts viennent des procédures approuvées et des caractéristiques du système.

### 6.3 Définir une preuve attendue

Une tâche sans preuve est difficile à auditer et à améliorer. La preuve peut être :

- un enregistrement daté de contrôle ;
- une mesure avec unité et seuil de référence ;
- un rapport fourni par l’outil ;
- une capture ou un export autorisé et protégé ;
- un résultat de test ;
- une check-list remplie ;
- une référence de ticket ;
- la confirmation du responsable du service.

La preuve doit être pertinente, compréhensible et suffisamment protégée. Il ne faut pas accumuler des captures inutiles ni copier des secrets dans un rapport.

### 6.4 Critères de réussite et critères d’arrêt

Le critère de réussite indique le résultat attendu. Le critère d’arrêt décrit une condition qui empêche de continuer normalement.

Exemple de contrôle de sauvegarde :

- **Réussite :** le travail de sauvegarde est terminé selon le statut attendu, aucune erreur non traitée n’est présente et les éléments demandés par la procédure sont consignés.
- **Écart :** tâche échouée, durée inhabituelle, volume incomplet ou alerte non expliquée.
- **Suite :** ouvrir ou rattacher un incident, préserver les journaux utiles et informer le responsable selon la criticité.
- **Limite :** le statut de réussite ne remplace pas un essai de restauration planifié.

Le but n’est pas de déclarer tous les contrôles réussis. Le but est de distinguer clairement l’état conforme, l’écart à traiter et le doute qui nécessite une analyse.

## 7. Déterminer la fréquence sans inventer une règle universelle

### 7.1 Les sources à utiliser

Pour définir une fréquence, examine dans cet ordre selon le contexte :

1. les exigences légales, contractuelles ou de sécurité applicables ;
2. la documentation et les recommandations du fabricant ;
3. les engagements de service et la criticité métier ;
4. les paramètres réellement mesurés et l’historique de l’actif ;
5. les incidents et dégradations observés ;
6. les capacités de l’équipe et les fenêtres possibles ;
7. les résultats des contrôles précédents.

Une valeur trouvée dans un autre cours ou utilisée dans une autre entreprise ne doit pas être copiée sans vérifier qu’elle convient à l’équipement et au contexte.

### 7.2 Fréquence calendaire

Une tâche peut être programmée par jour, semaine, mois, trimestre ou année, si l’intervalle est justifié. La fréquence dépend du risque, des instructions techniques et de ce que le contrôle permet réellement de détecter.

Exemples illustratifs :

- examiner régulièrement les alertes importantes de supervision ;
- vérifier les échecs de sauvegarde selon une routine définie ;
- vérifier périodiquement les procédures de restauration ;
- faire une revue périodique des actifs non couverts ou arrivant en fin de support ;
- examiner à date fixe les tâches arrivées à échéance.

Ces exemples ne prescrivent pas une cadence précise. Chaque organisation doit définir les intervalles pertinents et les rendre visibles dans son plan.

### 7.3 Fréquence basée sur l’usage

Certaines tâches dépendent d’un compteur ou d’un volume d’utilisation : heures de fonctionnement, cycles, nombre d’impressions, opérations, kilomètres ou autres unités pertinentes pour l’équipement.

Cette approche peut être plus représentative que la seule date calendrier. Mais elle exige de disposer d’un compteur fiable et de préciser ce qui se passe si le compteur n’est pas disponible.

### 7.4 Fréquence conditionnelle

Certaines tâches sont déclenchées à partir d’un indicateur. Il faut définir :

- quelle mesure est observée ;
- d’où vient la donnée ;
- quelle plage est considérée normale ;
- quel seuil déclenche une investigation ;
- qui reçoit l’alerte ;
- quel délai de traitement s’applique ;
- comment éviter qu’une alerte répétée soit ignorée.

Un seuil doit être adapté au contexte. Une utilisation à 80 % n’a pas forcément la même signification pour un volume de stockage, la mémoire d’un serveur et une liaison réseau. L’évolution, la durée, la marge disponible et la criticité importent autant que la valeur isolée.

### Schéma 5 — Choisir et réviser une fréquence

~~~mermaid
flowchart TD
    A[Définir l'objectif de contrôle] --> B[Consulter les règles et la documentation]
    B --> C[Examiner la criticité et l'usage]
    C --> D[Analyser l'historique et les mesures]
    D --> E[Proposer une fréquence ou un déclencheur]
    E --> F[Valider et documenter]
    F --> G[Mesurer les résultats réels]
    G --> H{Contrôle utile et proportionné ?}
    H -->|Oui| I[Conserver et surveiller]
    H -->|Non| J[Réviser avec validation]
    J --> F
~~~

### 7.5 Quand revoir la fréquence ?

Une fréquence doit être réexaminée lorsque :

- un défaut apparaît plusieurs fois entre deux contrôles ;
- une tâche est réalisée très souvent sans trouver d’écart et sans bénéfice démontré ;
- les conditions d’utilisation changent ;
- la charge, la température ou le volume de données augmente ;
- le fabricant publie une nouvelle recommandation pertinente ;
- l’actif, le logiciel ou son environnement est modifié ;
- l’organisation change ses engagements, risques ou contraintes opérationnelles ;
- une opération devient dangereuse ou difficile à réaliser avec les moyens disponibles.

Réduire la fréquence pour gagner du temps sans analyser le risque n’est pas une amélioration. Augmenter la fréquence sans objectif ni preuve n’en est pas une non plus.

## 8. Construire le calendrier préventif

### 8.1 Pourquoi planifier ?

Un plan préventif permet de réserver du temps, de coordonner les intervenants, de préparer les pièces et les outils, d’informer les utilisateurs et d’éviter que toutes les tâches soient repoussées au moment des urgences.

La planification doit tenir compte du temps réel de travail. Une opération peut nécessiter une préparation, une vérification des accès, une interruption, une exécution, des essais, une observation après redémarrage et une restitution aux utilisateurs.

### 8.2 Les champs d’un calendrier

Un calendrier simple peut contenir :

| Champ | Exemple de contenu |
|---|---|
| Référence de la tâche | PM-004 |
| Actif ou groupe | Serveurs de fichiers |
| Objet du contrôle | Examiner les alertes de capacité |
| Déclencheur | Fréquence et conditions définies par l’équipe |
| Échéance | Date ou période convenue |
| Durée prévue | Temps de préparation, de contrôle et de restitution |
| Responsable | Équipe ou rôle affecté |
| Prérequis | Accès autorisé, documentation, outil disponible |
| Fenêtre | Période compatible avec l’activité |
| Critère de réussite | État attendu et preuves à fournir |
| Statut | À planifier, prêt, en cours, terminé, en écart |
| Référence de preuve | Ticket, rapport ou enregistrement |
| Suite à donner | Action et responsable en cas d’écart |

La donnée d’exemple n’est pas une fréquence recommandée. Le plan doit lier chaque tâche au contexte réel et à sa justification.

### 8.3 Fenêtre de maintenance

Une fenêtre de maintenance est une période pendant laquelle une opération est autorisée et coordonnée. Elle est particulièrement utile lorsque des tâches peuvent interrompre des utilisateurs : redémarrage, mise à jour, modification de configuration ou remplacement d’un composant.

Une fenêtre doit préciser la période de début et de fin, le périmètre, les acteurs, la communication, les critères de réussite et la conduite à tenir si la tâche dépasse la durée prévue. Selon la plateforme, une fenêtre planifiée ne garantit pas que toute opération sera terminée à l’heure exacte : il faut prévoir la marge et les procédures de débordement.

Pour les appareils Windows, Microsoft documente des mécanismes de planification des mises à jour et des fenêtres de maintenance, notamment pour limiter l’impact des redémarrages sur l’activité. Les fonctions disponibles dépendent de la version et de la gestion de l’appareil ; voir les [politiques de conformité des mises à jour et fenêtres de maintenance](https://learn.microsoft.com/fr-fr/windows/deployment/update/wufb-compliancedeadlines).

### 8.4 Réserver le temps complet

Une estimation ne doit pas compter seulement la manipulation visible. Il faut inclure :

- lecture de la procédure ;
- vérification de l’actif et du périmètre ;
- coordination et communication ;
- préparation des outils et pièces ;
- contrôles préalables ;
- intervention ;
- tests de réussite ;
- surveillance ou contrôle supplémentaire ;
- remise en service ;
- documentation et mise à jour de l’inventaire.

Sous-estimer ces étapes conduit à des interventions écourtées, à des comptes rendus incomplets et à des tests omis.

### 8.5 Gérer les tâches en retard

Une tâche peut devenir en retard parce qu’une urgence mobilise l’équipe, une fenêtre n’est pas disponible, une pièce manque ou un contrôle préalable échoue. Il faut éviter de la marquer artificiellement comme terminée.

La bonne réponse est de réévaluer le risque, identifier la raison, décider si l’échéance peut être déplacée selon les règles internes et désigner une personne responsable. Les tâches en retard sur des actifs critiques ou portant sur une obligation doivent être escaladées selon la procédure.

### Schéma 6 — Du plan à la preuve

~~~mermaid
flowchart LR
    A[Plan préventif] --> B[Échéance et ressource]
    B --> C[Préparation et autorisation]
    C --> D[Exécution]
    D --> E[Tests et constat]
    E --> F[Compte rendu]
    F --> G{Conforme ?}
    G -->|Oui| H[Clôturer la tâche]
    G -->|Non| I[Créer une action de suivi]
    I --> J[Réviser le risque et le calendrier]
~~~

## 9. Préparer et réaliser une tâche préventive

### 9.1 Avant : préparer

Avant de commencer, confirmer l’équipement, le but de la tâche, la procédure, la fréquence prévue, les autorisations, les risques, les outils, la durée et la preuve attendue.

Les principales questions sont :

- Est-ce le bon actif ?
- Le contrôle prévu est-il toujours nécessaire ?
- Ai-je l’autorisation et la compétence requises ?
- Le service sera-t-il interrompu ?
- Qui doit être informé ?
- Existe-t-il des dépendances ou interventions simultanées ?
- Ai-je accès à la documentation approuvée ?
- Quelle action est prévue si un résultat dépasse un seuil ?
- Un arrêt ou une modification nécessite-t-il une sauvegarde, un plan de reprise ou un retour arrière ?
- Les tests et conditions de restitution sont-ils clairs ?

Si une condition critique n’est pas réunie, la tâche doit être suspendue ou réévaluée. L’échéance ne justifie pas une opération dangereuse.

### 9.2 Pendant : suivre les étapes

La tâche doit être réalisée selon la procédure validée. Le technicien note les valeurs utiles, les anomalies et les actions effectuées. Il ne doit pas modifier le périmètre sans évaluation et autorisation appropriées.

Une check-list est utile parce qu’elle stabilise le processus et réduit les oublis. Elle ne remplace pas la compétence : si une instruction est ambiguë, si l’équipement ne correspond pas à la documentation ou si un danger apparaît, il faut arrêter la partie concernée et demander une clarification.

### 9.3 Après : contrôler et clôturer

La tâche est terminée lorsque les vérifications définies ont été réalisées, que les écarts sont traités ou enregistrés comme actions de suivi, que l’équipement est dans l’état attendu et que les responsables concernés sont informés.

Une tâche « exécutée » n’est pas forcément une tâche « conforme ». Si le contrôle révèle une anomalie, il faut l’enregistrer même si le technicien a suivi toute la check-list.

### Schéma 7 — Le cycle d'une tâche préventive

~~~mermaid
flowchart TD
    A[Consulter la tâche] --> B[Confirmer actif, autorisation et sécurité]
    B --> C{Prérequis réunis ?}
    C -->|Non| D[Suspendre et signaler l'écart]
    C -->|Oui| E[Effectuer les contrôles prévus]
    E --> F[Comparer aux critères]
    F --> G{Résultat conforme ?}
    G -->|Oui| H[Enregistrer la preuve]
    G -->|Non| I[Ouvrir un suivi ou escalader]
    H --> J[Restituer et clôturer]
    I --> K[Évaluer l'impact et le risque résiduel]
~~~

## 10. Les contrôles préventifs sur les postes de travail

Les contrôles préventifs d’un poste de travail visent à détecter les problèmes courants, préserver les données et limiter les interruptions. Ils doivent être adaptés au système d’exploitation, à la politique de sécurité et à l’outil de gestion de l’entreprise.

### 10.1 Inventaire et état du poste

Vérifier que l’identifiant, l’utilisateur ou le service affecté, le modèle et le système d’exploitation correspondent à l’inventaire. Les changements d’affectation doivent être répercutés dans l’outil autorisé.

Relever les informations qui aident à déterminer le support : version du système, état de la garantie, date de fin de support, compatibilité des applications et périphériques. Ne pas lancer une mise à niveau importante sans vérifier les exigences et la méthode autorisée.

### 10.2 Capacité et performances

Les contrôles peuvent porter sur :

- la capacité du stockage et sa tendance ;
- les alertes système pertinentes ;
- les erreurs répétées ;
- les performances inhabituelles ;
- l’état déclaré des composants par les outils prévus ;
- la disponibilité des ressources nécessaires au fonctionnement normal.

Une mesure isolée ne donne pas toujours une conclusion. Par exemple, un stockage presque plein peut être acceptable pendant une courte période si une extension est déjà planifiée, ou critique si l’application ne peut plus écrire. Il faut examiner l’usage et la tendance.

### 10.3 Mises à jour et protection

Le suivi des mises à jour doit suivre la politique de gestion approuvée : classification de l’urgence, groupe pilote, tests, déploiement progressif, suivi des échecs et gestion des redémarrages. Ne désactive pas les protections ou les mises à jour pour obtenir un résultat plus rapide sans autorisation et analyse de risque.

Un déploiement progressif permet de détecter des problèmes sur un petit groupe avant une extension plus large. Les groupes pilotes doivent toutefois être représentatifs des usages et disposer d’un suivi réel.

### 10.4 Redémarrage et communication

Un redémarrage peut être nécessaire pour appliquer une mise à jour ou terminer une opération. Il faut prévenir les utilisateurs, tenir compte des travaux en cours et respecter la fenêtre prévue. La configuration exacte dépend du système et de sa gestion. Microsoft documente la gestion des fenêtres de maintenance et des redémarrages selon les versions Windows dans [la documentation sur les mises à jour](https://learn.microsoft.com/fr-fr/windows/deployment/update/waas-restart).

### 10.5 Contrôles de premier niveau

Une check-list générique et non destructive peut comprendre :

- confirmer l’identité de l’actif ;
- examiner les alertes signalées par l’outil de gestion ;
- vérifier si le poste est couvert par les protections attendues ;
- vérifier la disponibilité et l’état des mises à jour selon la politique ;
- examiner l’espace disponible et les tendances ;
- vérifier les échecs qui exigent un suivi ;
- enregistrer le résultat et ouvrir une action si un écart est observé.

Les manipulations physiques, les réparations, les changements de configuration et les opérations sur les données doivent suivre une procédure spécifique et être confiés à une personne compétente.

## 11. Les contrôles préventifs sur les serveurs et les équipements réseau

Les serveurs et équipements réseau peuvent soutenir plusieurs services. Les opérations préventives doivent donc tenir compte des dépendances, de la redondance, des fenêtres de travail et de l’impact d’une interruption.

### 11.1 Disponibilité et capacité

Les outils autorisés peuvent surveiller :

- la disponibilité du service et de ses dépendances ;
- l’espace de stockage ;
- les ressources de traitement et la mémoire ;
- les interfaces et liens réseau ;
- les erreurs remontées par l’équipement ;
- les tendances de charge ;
- les alertes de température ou d’alimentation disponibles dans la supervision ;
- les journaux significatifs.

Le but est d’identifier une dérive suffisamment tôt pour qu’une équipe puisse agir. Il faut documenter la durée et le contexte d’une alerte, plutôt que déclencher systématiquement une modification à chaque événement isolé.

### 11.2 Redondance : la vérifier, pas seulement la supposer

Une infrastructure peut comporter deux alimentations, deux liens réseau ou plusieurs nœuds. Cela ne prouve pas que la redondance fonctionnera au moment où on en aura besoin. Un lien de secours peut être mal configuré, une alimentation peut partager une source commune ou une procédure de bascule peut ne pas avoir été testée.

La vérification d’une redondance peut être risquée lorsqu’elle implique de provoquer une défaillance volontaire. Ce type d’essai doit être planifié, autorisé, réalisé par des personnes compétentes et exécuté dans les conditions adaptées. Un débutant ne doit pas débrancher un lien ou une alimentation en production pour « vérifier si le secours prend le relais ».

### 11.3 Versions et support

Conserver les versions pertinentes des systèmes, firmwares et configurations permet d’identifier les équipements qui approchent de la fin de support ou nécessitent une revue. Un équipement en fin de support n’est pas toujours immédiatement remplaçable : il faut évaluer le risque, les options de migration, les contraintes de compatibilité et le plan de financement.

### 11.4 Configuration et documentation

Les changements approuvés doivent être répercutés dans les documents de référence. Selon les procédures, il peut être pertinent de vérifier l’existence d’une sauvegarde de configuration et de s’assurer qu’elle est utilisable pour le modèle et la version concernés.

Ne copie pas de secrets ou de clés dans un document non protégé. L’accès à une configuration de référence doit respecter les règles de sécurité.

### Schéma 8 — Surveiller sans provoquer une panne

~~~mermaid
flowchart TD
    A[Collecter les indicateurs autorisés] --> B[Comparer au comportement attendu]
    B --> C{Dérive confirmée ou seuil dépassé ?}
    C -->|Non| D[Conserver la preuve et suivre la tendance]
    C -->|Oui| E[Qualifier impact et criticité]
    E --> F{Test ou modification nécessaire ?}
    F -->|Non| G[Créer une investigation ou un suivi]
    F -->|Oui| H[Préparer autorisation, fenêtre et retour arrière]
    H --> I[Exécuter selon la procédure]
    I --> J[Tester le service et documenter]
~~~

## 12. Les sauvegardes et la restauration : une priorité préventive

### 12.1 Pourquoi surveiller les sauvegardes ?

Les sauvegardes permettent de récupérer des données ou des systèmes après certaines défaillances, erreurs humaines ou attaques. Leur présence ne suffit pas : il faut connaître les données couvertes, les horaires, la rétention, les responsabilités, les limites et les conditions de récupération.

Un système peut annoncer qu’une tâche s’est terminée alors que le périmètre attendu n’est pas complet, qu’une erreur secondaire existe ou que la restauration n’a jamais été testée. Le suivi doit donc dépasser le simple constat d’un voyant vert.

### 12.2 Les contrôles utiles

Le plan de maintenance des sauvegardes peut notamment couvrir :

- la confirmation du périmètre prévu ;
- les échecs ou avertissements de tâches ;
- les volumes et durées anormales ;
- la disponibilité et la capacité de la destination ;
- l’état des politiques de rétention ;
- la protection des accès à la sauvegarde ;
- la séparation des copies lorsque cela est requis par l’architecture ;
- les procédures de restauration et leurs responsabilités ;
- la réalisation d’essais de récupération planifiés.

Les fréquences et critères doivent être adaptés à la criticité des données, au rythme de modification, aux objectifs de reprise et aux capacités de stockage. Une base de données transactionnelle n’a pas nécessairement le même besoin qu’un dossier d’archives peu modifié.

### 12.3 Vérification et test de restauration

Un contrôle de tâche peut confirmer qu’un travail est terminé. Un test de restauration vérifie une autre question : peut-on récupérer les données ou le système dans les conditions nécessaires ?

L’essai doit être fait dans un environnement autorisé, avec un périmètre et des critères clairs. Il faut vérifier l’intégrité des données restaurées, les droits, les dépendances et la possibilité d’exploiter le résultat. Une restauration de test ne doit pas écraser les données de production.

### 12.4 RPO et RTO, à connaître

Le **RPO**, ou objectif de point de reprise, correspond à la quantité de données ou à la période de données que l’organisation peut accepter de perdre, selon la définition retenue.

Le **RTO**, ou objectif de délai de reprise, correspond à la durée cible pour rétablir un service après une interruption.

Ces objectifs sont des exigences métier et techniques à définir par l’organisation ; le technicien ne doit pas les inventer. Ils aident à déterminer le type de protection et la méthode de test. Un essai de restauration doit enregistrer les résultats réels afin d’évaluer si le plan peut respecter les objectifs annoncés.

### Schéma 9 — De la sauvegarde à la capacité de reprise

~~~mermaid
flowchart TD
    A[Données et services critiques identifiés] --> B[Politique de sauvegarde]
    B --> C[Exécution et supervision]
    C --> D[Examen des erreurs et exceptions]
    D --> E[Test de restauration planifié]
    E --> F[Contrôle intégrité et utilisabilité]
    F --> G{Objectifs de reprise atteints ?}
    G -->|Oui| H[Documenter preuve et limites]
    G -->|Non| I[Corriger le plan et planifier un nouvel essai]
    I --> B
~~~

### 12.5 Si une sauvegarde échoue

Ne supprime pas l’alerte et ne relance pas indéfiniment le même travail sans comprendre l’échec. Il faut enregistrer l’erreur, identifier le périmètre impacté, évaluer l’ancienneté de la dernière copie utilisable, respecter les autorisations, alerter le responsable selon la criticité et suivre la résolution.

Si l’échec concerne des données critiques ou menace les objectifs de reprise, la priorité doit refléter ce risque même si aucun utilisateur n’est encore bloqué.

Pour des recommandations générales de protection et de récupération, consulte le [guide CISA StopRansomware](https://www.cisa.gov/stopransomware/ransomware-guide), qui insiste notamment sur l’inventaire, la protection des actifs et la disponibilité de sauvegardes utilisables.

## 13. Les mises à jour : planifier et contrôler

### 13.1 Pourquoi les mises à jour font partie de la prévention

Les mises à jour peuvent corriger des défauts, des vulnérabilités ou des problèmes de compatibilité. Mais elles peuvent aussi nécessiter un redémarrage, modifier un comportement ou provoquer une régression. Le préventif ne consiste donc ni à retarder toutes les mises à jour ni à installer aveuglément tout paquet dès qu’il est disponible.

La démarche doit considérer l’urgence de sécurité, le périmètre touché, les applications métier, la compatibilité, les tests et les possibilités de récupération.

### 13.2 Une approche progressive

Un déroulement possible :

1. inventorier les appareils et versions concernés ;
2. examiner l’urgence, les risques et les avis pertinents ;
3. tester la mise à jour sur un groupe pilote adapté ;
4. vérifier les fonctions métier et les dépendances ;
5. programmer les groupes suivants selon la procédure ;
6. communiquer les redémarrages ou interruptions ;
7. examiner les appareils en échec ou non conformes ;
8. conserver les preuves et clôturer les actions réussies ;
9. traiter les exceptions dans un délai défini.

Cette approche doit être adaptée au niveau de risque. Une vulnérabilité activement exploitée peut nécessiter un traitement accéléré, selon la procédure d’urgence. Le groupe pilote ne doit pas devenir un prétexte pour retarder indéfiniment une correction urgente.

### 13.3 Comprendre les vagues de déploiement

~~~mermaid
flowchart LR
    A[Évaluer la mise à jour] --> B[Test sur groupe pilote]
    B --> C[Contrôler applications et sécurité]
    C --> D{Résultats acceptables ?}
    D -->|Non| E[Stopper l'extension et analyser]
    D -->|Oui| F[Déployer à un groupe limité]
    F --> G[Surveiller les erreurs]
    G --> H{Stabilité confirmée ?}
    H -->|Non| E
    H -->|Oui| I[Étendre selon le plan]
    I --> J[Rapport de conformité]
~~~

### 13.4 Firmware et équipements d’infrastructure

Les mises à jour de firmware des serveurs, contrôleurs de stockage, commutateurs, routeurs, onduleurs et autres équipements peuvent avoir des prérequis propres au fabricant. Il faut vérifier la compatibilité, les dépendances, la procédure, la fenêtre, les mécanismes de récupération et les restrictions éventuelles.

Ne pas exécuter une mise à jour de firmware simplement parce qu’une version plus récente existe. L’urgence, le défaut corrigé, le support, la compatibilité et le risque d’interruption doivent être évalués. Une telle tâche peut nécessiter un spécialiste ou une approbation de changement.

### 13.5 Vérifier les exceptions

Après un déploiement, la liste des appareils qui n’ont pas appliqué la mise à jour est aussi importante que la liste de ceux qui ont réussi. Un appareil éteint, isolé ou en erreur peut rester vulnérable. Il faut identifier les exceptions, leur criticité, le responsable de la correction et la prochaine échéance de contrôle.

## 14. Contrôles physiques : rester dans le périmètre autorisé

### 14.1 Inspection de l’environnement

Certaines tâches de premier niveau peuvent consister à observer l’environnement : voyants d’alerte, ventilation obstruée, câbles visiblement détériorés, accès encombré ou température signalée par la supervision. Ces observations doivent être faites sans exposer la personne à un danger ni intervenir sur un équipement non autorisé.

Un serveur ou un équipement réseau peut nécessiter des outils, des protections ou une procédure spécifiques. L’ouverture d’un châssis, le démontage, la manipulation d’une batterie, la modification d’un circuit ou l’intervention sur une alimentation ne sont pas de simples gestes d’inspection pour un débutant.

### 14.2 Nettoyage

Un nettoyage préventif doit respecter les instructions du fabricant, les limites d’intervention, la protection contre les décharges électrostatiques et les conditions de mise hors énergie prévues par la procédure. Il ne faut pas souffler des particules vers des composants ou des personnes, utiliser un liquide inapproprié, bloquer un ventilateur avec un outil ou improviser une méthode qui pourrait endommager l’équipement.

Si l’opération exige un démontage, une consignation, une habilitation ou un outil spécialisé, elle doit être planifiée et exécutée par une personne qualifiée.

### 14.3 Câblage et alimentation

Un contrôle visuel peut permettre de repérer un câble écrasé, une étiquette manquante, une connexion manifestement désengagée ou un environnement encombré. Mais un câble ne doit pas être retiré en production pour « voir si le secours fonctionne ». Une alimentation redondante ou un double lien ne garantit pas à lui seul qu’une déconnexion sera sans conséquence.

Le but du contrôle est de signaler un risque et de déclencher la procédure adaptée, pas de provoquer une panne pour confirmer une hypothèse.

### 14.4 Onduleurs et batteries

Le suivi peut inclure les alertes de l’équipement, l’état exposé par l’outil de supervision, la documentation du fabricant, les contrats, l’historique et les essais prévus par le programme. Les tests qui interrompent l’alimentation ou sollicitent la batterie doivent être planifiés selon les instructions et les règles de sécurité. Un technicien débutant ne doit pas improviser une décharge ou une manipulation interne.

## 15. Exemple de programme préventif pour une petite entreprise

Cet exemple montre comment organiser un programme. Les tâches et catégories sont illustratives ; les fréquences réelles doivent être définies à partir du fabricant, du risque, de l’usage et des règles de l’organisation.

### 15.1 Périmètre initial

Une petite entreprise possède :

- 20 postes de travail ;
- un serveur de fichiers ;
- un commutateur principal ;
- une imprimante partagée ;
- un onduleur ;
- une solution de sauvegarde ;
- une application métier hébergée ;
- un accès Internet dépendant d’un routeur.

Le programme initial ne doit pas supposer que tous ces actifs ont le même impact. Le serveur de fichiers, l’application métier, la sauvegarde et l’alimentation peuvent avoir des dépendances importantes.

### 15.2 Créer les fiches de tâche

| Actif ou service | Exemple de contrôle | Preuve attendue | Suite en cas d’écart |
|---|---|---|---|
| Postes | Examiner les alertes de gestion et les appareils en échec | Rapport de conformité | Ouvrir un suivi pour les appareils concernés |
| Serveur de fichiers | Examiner capacité, alertes et disponibilité | Valeurs, tendances et anomalies | Prioriser selon l’impact et lancer une investigation |
| Commutateur principal | Examiner les alertes et erreurs disponibles | Rapport de supervision | Escalader les anomalies inhabituelles |
| Imprimante partagée | Examiner alertes, consommables déclarés et incidents répétés | Résultat de contrôle et incidents associés | Créer une tâche corrective si nécessaire |
| Onduleur | Examiner l’état déclaré et les alertes selon le fabricant | Rapport ou preuve de contrôle | Faire évaluer tout défaut de batterie ou d’alimentation |
| Sauvegarde | Examiner échecs, exceptions et capacité | Rapport de tâche | Escalader selon le risque et la dernière copie utilisable |
| Application métier | Vérifier les indicateurs et tests autorisés | Résultats de contrôles | Ouvrir un incident ou une investigation |
| Routeur Internet | Examiner les alertes et la stabilité observée | Mesures et historique | Qualifier le périmètre et coordonner le fournisseur si nécessaire |

La table ne remplace pas une procédure détaillée pour chaque actif. Elle donne le squelette du programme : actif, contrôle, preuve et suite.

### 15.3 Organiser la charge de travail

Le responsable regroupe les tâches compatibles, prévoit des créneaux, tient compte des périodes métier sensibles et affecte les personnes compétentes. Les contrôles qui n’interrompent pas le service peuvent être organisés différemment des mises à jour, tests de bascule ou inspections matérielles.

Il faut réserver le temps pour lire les résultats et ouvrir les suivis. Une maintenance qui détecte un défaut sans organiser sa correction ne fait que déplacer le problème.

### 15.4 Exemple de calendrier de départ

Les catégories ci-dessous sont des exemples de périodes de planification, pas une fréquence technique obligatoire.

| Période du programme | Activité possible | Condition avant validation |
|---|---|---|
| Routine opérationnelle | Examiner les alertes importantes et les échecs signalés | Sources fiables, destinataire nommé, procédure d’escalade connue |
| Revue périodique | Vérifier les actifs en retard, les exceptions et la conformité du parc | Inventaire suffisamment à jour |
| Fenêtre technique planifiée | Déployer des mises à jour ou effectuer des contrôles nécessitant un redémarrage | Autorisation, tests, communication et retour arrière définis |
| Revue de capacité | Examiner les tendances de stockage, de charge et de croissance | Seuils et critères adaptés à chaque système |
| Essai de récupération | Restaurer des données ou un service dans un environnement prévu | Périmètre, autorisation et critères de test définis |
| Revue de programme | Analyser les résultats, récurrences et tâches inutiles ou inefficaces | Historique et preuves disponibles |

Cette structure aide à organiser le travail tout en laissant la fréquence technique être définie par l’analyse et la documentation.

### Schéma 10 — Du parc au programme durable

~~~mermaid
flowchart TD
    A[Inventaire et criticité] --> B[Catalogue de tâches]
    B --> C[Justification des fréquences]
    C --> D[Calendrier et ressources]
    D --> E[Exécution et preuves]
    E --> F[Gestion des écarts]
    F --> G[Analyse des résultats]
    G --> H[Révision du programme]
    H --> B
~~~

## 16. Comment traiter une anomalie découverte pendant le préventif

La tâche préventive peut révéler un problème que personne n’avait signalé. Il faut alors séparer l’exécution prévue de la gestion de l’anomalie.

### 16.1 Ne pas improviser une réparation

Si un contrôle révèle un résultat inattendu, ne réalise pas automatiquement une réparation. Il faut déterminer si le travail de correction est déjà couvert par l’autorisation, si les compétences sont disponibles, si les risques sont acceptables et si une interruption serait nécessaire.

La tâche initiale peut être terminée avec le statut « contrôle effectué, écart détecté », tandis qu’un incident ou un ordre de travail distinct prend en charge la réparation.

### 16.2 Décrire la découverte

Le compte rendu devrait préciser :

- ce qui devait être contrôlé ;
- ce qui a été observé ;
- les valeurs et seuils pertinents ;
- les conditions d’observation ;
- le niveau de confiance dans la mesure ;
- l’impact possible ;
- les actions immédiates autorisées ;
- les personnes informées ;
- la référence du suivi.

Il faut éviter les descriptions comme « équipement mauvais » ou « disque bientôt mort » si les éléments ne permettent pas cette conclusion.

### 16.3 Escalader et ajuster le plan

Une anomalie qui révèle un risque important peut justifier une priorité supérieure. Une dérive répétée peut conduire à modifier le plan, ajouter une mesure ou améliorer le contrôle. Une tâche inutilement coûteuse peut être révisée après validation. Toute modification doit rester traçable.

## 17. Les indicateurs d’un programme préventif

Un programme de qualité doit mesurer à la fois l’exécution et les résultats. Le pourcentage de tâches cochées ne suffit pas.

### 17.1 Taux de réalisation à l’échéance

Une mesure possible est :

Nombre de tâches préventives réalisées dans la période attendue, divisé par le nombre de tâches dues pendant cette même période, multiplié par 100.

Il faut définir les exclusions, les reports approuvés et le traitement des tâches annulées. Si l’on exclut de nombreuses tâches difficiles, le taux peut donner une image trompeuse.

### 17.2 Tâches en retard

Le nombre de tâches en retard ne suffit pas à lui seul. Il faut connaître leur âge, la criticité, la raison du retard, le risque associé et la personne qui décide du report. Une tâche mineure en retard et une tâche critique en retard ne doivent pas être traitées comme équivalentes.

### 17.3 Écarts découverts par le préventif

Le nombre d’anomalies peut augmenter au début d’un programme parce que l’équipe mesure enfin des choses auparavant invisibles. Une augmentation ne signifie donc pas nécessairement que les équipements se dégradent. Il faut suivre la gravité, le délai de traitement et la récurrence.

### 17.4 Récurrence et pannes entre deux contrôles

Si un défaut survient plusieurs fois entre des contrôles, il faut examiner la pertinence de la fréquence, l’efficacité du contrôle, les critères de mesure et la possibilité que la tâche ne traite pas le facteur réel. Augmenter le nombre de contrôles ne résout pas nécessairement un mauvais diagnostic.

### 17.5 Temps consacré aux tâches et temps d’arrêt

Le programme doit suivre le temps consommé, les interruptions et les résultats. Des tâches excessivement fréquentes peuvent détourner les ressources de contrôles plus importants. À l’inverse, des contrôles sous-estimés peuvent être écourtés ou reportés.

### 17.6 Calcul simple du taux de réalisation

Supposons qu’un programme prévoyait 40 tâches durant une période et que 34 ont été réalisées dans la période attendue.

Taux = 34 ÷ 40 × 100 = 85 %.

Le résultat est 85 %. Mais pour interpréter ce nombre, il faut aussi examiner les six tâches non réalisées : quelles étaient leurs criticités, quelles raisons expliquent le retard, les reports ont-ils été approuvés, et des risques importants demeurent-ils ?

### Schéma 11 — Ne pas mesurer seulement la quantité

~~~mermaid
flowchart LR
    A[Exécution des tâches] --> D[Évaluation du programme]
    B[Qualité et utilité des contrôles] --> D
    C[Écarts, récurrences et risques] --> D
    D --> E[Décisions d'amélioration]
    E --> F[Plan plus pertinent]
~~~

## 18. Les erreurs fréquentes à éviter

### Erreur 1 : copier une fréquence sans justification

Une fréquence utilisée ailleurs peut ne pas correspondre à l’actif, à son environnement ou à son usage. Il faut enregistrer la source et réévaluer lorsque le contexte change.

### Erreur 2 : confondre tâche terminée et tâche conforme

Le technicien peut avoir exécuté chaque étape, mais découvrir un défaut. Le résultat doit être enregistré comme écart, et non transformé en réussite artificielle.

### Erreur 3 : ne pas tester les sauvegardes

Un rapport de sauvegarde ne remplace pas une restauration testée. Le plan doit préciser quel résultat est réellement démontré.

### Erreur 4 : tout mettre à jour au même moment

Une mise à jour peut interrompre un service ou provoquer une incompatibilité. Il faut évaluer l’urgence, utiliser des groupes adaptés et contrôler les résultats.

### Erreur 5 : ne pas tenir compte des utilisateurs

Une tâche qui redémarre un poste pendant une activité critique peut créer un incident évitable. La communication et la fenêtre sont des parties de la maintenance.

### Erreur 6 : accumuler des alertes sans propriétaire

Une alerte n’aide que si quelqu’un la reçoit, l’évalue et sait quoi faire. Le plan doit définir un rôle responsable et un délai adapté au risque.

### Erreur 7 : faire un test dangereux pour confirmer la redondance

La redondance doit être vérifiée selon une procédure. Débrancher une liaison ou une alimentation en production sans autorisation peut provoquer une interruption.

### Erreur 8 : fermer une tâche sans trace

Sans données datées, il devient impossible de comparer l’état avant et après, de comprendre une dérive ou de prouver qu’un contrôle a été effectué.

### Erreur 9 : ne jamais réviser le programme

Un plan figé devient progressivement inadapté lorsque les actifs, les logiciels, les risques et l’activité changent. Les résultats doivent nourrir les révisions.

### Erreur 10 : mesurer seulement le nombre de tâches

Le nombre de tâches réalisées n’explique pas leur utilité. Il faut associer conformité, qualité, anomalies, récurrence et risque résiduel.

## 19. Check-lists de référence

### 19.1 Vérifier qu’une tâche est bien conçue

- [ ] L’actif et le service sont identifiés.
- [ ] L’objectif du contrôle est clair.
- [ ] La fréquence ou le déclencheur est justifié.
- [ ] La source technique ou la règle applicable est documentée.
- [ ] Le responsable est désigné.
- [ ] Les prérequis, outils et accès sont connus.
- [ ] Les risques et limites de compétence sont identifiés.
- [ ] Les étapes sont suffisamment précises.
- [ ] Les critères de réussite sont mesurables.
- [ ] La conduite en cas d’écart est décrite.
- [ ] La preuve attendue et son lieu de stockage sont définis.
- [ ] La durée comprend la préparation et la restitution.
- [ ] La tâche a une date ou une règle de planification.

### 19.2 Avant d’exécuter une tâche planifiée

- [ ] Le bon actif est confirmé.
- [ ] La tâche est due et reste pertinente.
- [ ] L’autorisation et les compétences nécessaires sont disponibles.
- [ ] Le risque et l’impact sont compris.
- [ ] Les utilisateurs et équipes concernés sont informés.
- [ ] Les outils et documents sont disponibles.
- [ ] La fenêtre et la durée sont réalistes.
- [ ] Les tests et critères de réussite sont connus.
- [ ] Le plan de récupération ou les conditions d’arrêt sont adaptés.
- [ ] Un responsable est disponible si un écart survient.

### 19.3 Après le contrôle

- [ ] Les étapes réalisées sont consignées.
- [ ] Les mesures sont associées à leur contexte et leurs unités.
- [ ] Les résultats sont comparés aux critères attendus.
- [ ] Les anomalies ont un suivi approprié.
- [ ] La fonction ou le service attendu est vérifié lorsque nécessaire.
- [ ] Les personnes concernées sont informées.
- [ ] Les preuves sont conservées dans l’emplacement approprié.
- [ ] L’inventaire et la procédure sont mis à jour si le périmètre a changé.
- [ ] Les tendances et récurrences importantes sont signalées.
- [ ] La tâche est clôturée avec un statut fidèle au résultat réel.

## 20. Travaux pratiques guidés

Les travaux pratiques s’effectuent à partir d’un environnement de test, d’un inventaire fictif ou d’outils pour lesquels tu es autorisé. Les opérations susceptibles d’interrompre un service réel ne doivent pas être exécutées sans la procédure et les autorisations nécessaires.

### TP 1 — Créer un mini-inventaire de maintenance

**Situation :** tu es chargé de préparer la première version de l’inventaire d’une petite entreprise qui possède dix ordinateurs, un serveur de fichiers, un commutateur central et une imprimante partagée.

**Étape 1 : définir les champs.**

Crée un tableau contenant au minimum l’identifiant, le type, la fonction, le responsable, la criticité, les dépendances, la documentation disponible et les informations manquantes.

**Étape 2 : recenser les actifs.**

Attribue un identifiant stable à chaque actif. Ne mets pas les mots de passe, clés ou secrets dans le tableau.

**Étape 3 : identifier les dépendances.**

Note quelles activités dépendent du serveur et du commutateur. Ne suppose pas qu’un équipement est sans importance simplement parce qu’il est petit ou bon marché.

**Étape 4 : relever les inconnues.**

Si la configuration, le contrat ou le propriétaire ne sont pas connus, marque le champ « à vérifier », puis crée une action de suivi.

**Livrable attendu :** un inventaire court, compréhensible et vérifiable, sans données inventées.

### TP 2 — Concevoir une fiche de tâche

Choisis un actif fictif, par exemple un serveur de fichiers, et crée une tâche destinée à examiner ses alertes de capacité et de disponibilité.

La fiche doit comprendre l’objectif, l’identifiant de l’actif, la source de la procédure, le responsable, le déclencheur ou la fréquence justifiée, les prérequis, les données à consulter, les critères de réussite, les écarts possibles, la preuve, la durée et le suivi en cas d’anomalie.

**Correction attendue :** la consigne doit décrire ce qui est vérifié et la preuve attendue. « Regarder si tout va bien » n’est pas un critère de réussite mesurable. Les seuils doivent être pris dans les règles ou mesures adaptées au système, pas inventés pour compléter la fiche.

### TP 3 — Évaluer un échec de sauvegarde

**Situation :** le tableau de bord indique qu’une tâche de sauvegarde prévue a échoué. Tu ne sais pas encore si une autre copie est disponible.

**Étape 1 :** enregistre l’alerte et la période concernée.

**Étape 2 :** vérifie le périmètre et les informations autorisées : données concernées, dernière copie connue, raisons de l’échec et statut des autres tâches.

**Étape 3 :** évalue la criticité avec le responsable approprié et applique la procédure de suivi.

**Étape 4 :** ne prétends pas qu’une restauration est possible tant qu’elle n’a pas été démontrée selon la méthode prévue.

**Étape 5 :** si la politique le prévoit, planifie un test de restauration contrôlé dans un environnement adapté.

**Correction attendue :** l’échec doit avoir un responsable, une évaluation de risque, une action et un résultat documenté. Il ne doit pas être masqué par une relance aveugle ou par la clôture du ticket.

### TP 4 — Préparer une fenêtre de mises à jour

**Situation :** un groupe pilote doit recevoir une mise à jour. Certains postes sont utilisés toute la journée et plusieurs applications sont nécessaires au traitement des commandes.

Établis un plan décrivant le groupe pilote, les conditions de test, les personnes à informer, la fenêtre, les critères d’acceptation, le suivi des échecs et les conditions qui empêchent d’élargir le déploiement.

**Correction attendue :** le déploiement ne doit pas passer au groupe suivant tant que les critères d’acceptation définis ne sont pas satisfaits. Les mises à jour urgentes doivent suivre le processus accéléré prévu, et les exceptions restantes doivent être visibles.

## 21. Exercices avec corrigés

### Exercice 1 — Quel mode de maintenance ?

Associe chaque situation à une approche appropriée :

A. Un défaut est déjà présent et empêche l’utilisateur de travailler.

B. Une inspection est programmée selon une exigence du fabricant.

C. Une mesure de température dépasse un seuil défini et doit être étudiée.

D. Un historique fiable et un modèle validé estiment une hausse du risque de défaillance.

**Corrigé :** A relève de la maintenance corrective ; B de la maintenance préventive systématique ; C de la maintenance conditionnelle ; D peut relever d’une maintenance prédictive. Le choix exact dépend de la politique et des preuves disponibles.

### Exercice 2 — Quelle fréquence choisir ?

Une personne propose de contrôler tous les équipements tous les jours parce que « plus on vérifie, mieux c’est ».

Explique pourquoi ce raisonnement est insuffisant.

**Corrigé :** la fréquence doit être justifiée par la criticité, la documentation, les risques, l’usage, la possibilité de détecter une dérive et le coût du contrôle. Un contrôle trop fréquent peut consommer du temps sans apporter de réduction de risque. Il faut définir l’objectif puis choisir et réévaluer l’intervalle.

### Exercice 3 — Actif critique ou non ?

Un ordinateur de test peut être remplacé rapidement. Un serveur héberge des documents essentiels et n’a pas de procédure de restauration testée.

Lequel exige généralement une priorité plus forte dans le programme préventif ? Justifie.

**Corrigé :** le serveur doit généralement être traité en priorité, car son impact potentiel et l’incertitude sur sa capacité de récupération sont plus élevés. La décision finale doit être validée avec le propriétaire du service selon les règles locales.

### Exercice 4 — Une tâche a échoué

Une check-list a été entièrement exécutée, mais une alerte critique demeure.

La tâche est-elle conforme ?

**Corrigé :** non, pas nécessairement. La tâche a été exécutée, mais le contrôle a révélé un écart qui doit être documenté et traité. L’état de la tâche doit distinguer exécution et conformité.

### Exercice 5 — La sauvegarde est « verte »

Le tableau de bord affiche un statut de réussite. Peut-on affirmer que la restauration fonctionnera ?

**Corrigé :** non. Le statut confirme un résultat de l’exécution selon l’outil, mais seule une validation appropriée de la restauration démontre la capacité de récupération sur le périmètre testé.

### Exercice 6 — Déploiement d’une mise à jour

Le groupe pilote fonctionne, mais le groupe de production contient une application métier différente qui n’a pas été testée.

Faut-il étendre le déploiement immédiatement ?

**Corrigé :** pas sans évaluer la compatibilité et les critères d’acceptation pour cette application. Le groupe pilote doit être représentatif, ou les différences doivent faire l’objet de tests avant extension, sauf procédure d’urgence approuvée.

### Exercice 7 — Un contrôle physique

Tu observes un câble endommagé près d’un équipement réseau utilisé par plusieurs équipes. Que fais-tu ?

**Corrigé :** ne le retire pas en production pour tester l’effet. Note l’observation, évalue le risque apparent, informe le responsable et fais organiser une intervention par une personne compétente, selon la procédure et la priorité appropriées.

### Exercice 8 — Un plan devient obsolète

Un équipement est remplacé, mais l’ancienne tâche préventive continue d’apparaître dans le calendrier.

**Corrigé :** l’inventaire, la tâche et les dépendances doivent être révisés avec les autorisations nécessaires. Il faut vérifier la documentation du nouvel équipement et s’assurer que le nouveau programme est approprié. Il ne faut ni supprimer aveuglément l’ancienne tâche ni la garder sans analyse.

### Exercice 9 — Le taux de réalisation baisse

Le taux de réalisation des tâches passe de 95 % à 80 %, alors que le service traite plusieurs incidents urgents.

Que faut-il analyser avant de conclure que le programme est mauvais ?

**Corrigé :** la criticité des tâches en retard, les raisons, les reports approuvés, les ressources, l’âge du retard, les risques et l’évolution des incidents. La baisse est un signal qui nécessite une analyse, pas une explication à elle seule.

### Exercice 10 — Vrai ou faux

1. La maintenance préventive garantit qu’aucune panne ne se produira.
2. Une fréquence doit être justifiée et peut être réévaluée.
3. Un équipement redondant ne nécessite jamais de contrôle.
4. Une tâche en écart doit avoir un suivi.
5. La maintenance préventive concerne aussi les données, les services et la documentation.

**Corrigé :** 1. Faux. 2. Vrai. 3. Faux. 4. Vrai. 5. Vrai.

## 22. Défi final corrigé — Établir le programme préventif d’une petite infrastructure

### Scénario

Tu rejoins une entreprise de 25 personnes. Son infrastructure comprend 25 postes, un serveur de fichiers, un commutateur principal, un routeur Internet, une imprimante partagée et un système de sauvegarde. Le plan de maintenance n’existe pas. Certaines alertes sont consultées de temps en temps, les mises à jour sont lancées sans calendrier commun et personne ne sait quand la restauration des données a été testée pour la dernière fois.

Tu dois proposer une première version du programme. Tu n’as pas l’autorisation de changer les équipements ni de lancer un test sur la production. Ton travail est de recenser, prioriser, préparer et faire valider le plan.

### Partie A — Inventaire et dépendances

Établis la liste des actifs et précise quelles activités en dépendent. Identifie les informations manquantes sans les inventer.

**Correction attendue :** le serveur, le commutateur et le routeur doivent être reliés aux services qu’ils rendent possibles. La sauvegarde doit être associée aux données qu’elle protège et aux procédures de reprise. Les postes doivent être recensés et rattachés à une équipe ou à un utilisateur selon les règles internes.

### Partie B — Criticité

Propose une évaluation de criticité justifiée pour le serveur de fichiers, le commutateur et un poste de test isolé.

**Correction possible :** le serveur et le commutateur peuvent présenter un impact plus élevé parce que plusieurs utilisateurs ou services en dépendent. Le poste de test peut être moins critique si son remplacement est simple et qu’aucune activité essentielle n’en dépend. Cette conclusion doit être vérifiée, notamment si le poste de test sert à une fonction métier particulière.

### Partie C — Définir les tâches

Prépare au minimum une tâche pour chacun de ces domaines :

- suivi des alertes et de la capacité ;
- conformité des postes et mises à jour ;
- suivi des équipements réseau ;
- suivi des sauvegardes et test de restauration ;
- mise à jour de l’inventaire et de la documentation.

Pour chacune, indique l’objectif, le responsable, la source de la fréquence, les prérequis, la preuve attendue et la suite en cas d’écart.

**Correction attendue :** une tâche doit être exploitable par un autre technicien, avec un objectif et des critères vérifiables. Les fréquences précises restent à définir à partir de la documentation, de la criticité et des règles locales.

### Partie D — Organiser le calendrier

Identifie les tâches qui peuvent être réalisées sans interruption, celles qui nécessitent une fenêtre, et les tâches qui peuvent exiger une approbation ou une expertise supplémentaire.

**Correction attendue :** les vérifications d’indicateurs disponibles dans un outil autorisé peuvent être planifiées sans interruption dans de nombreux contextes. Les mises à jour, redémarrages, tests de bascule, modifications de configuration ou interventions physiques peuvent nécessiter une fenêtre, des autorisations et un plan de récupération. La décision dépend des caractéristiques de l’actif et des procédures réelles.

### Partie E — Gérer les exceptions

Pendant la première revue, le rapport de sauvegarde indique un échec, le commutateur affiche une alerte répétée et trois postes n’ont pas appliqué une mise à jour attendue.

**Correction attendue :**

- Enregistrer et qualifier l’échec de sauvegarde, déterminer le périmètre et la dernière copie connue, évaluer l’impact avec le responsable et suivre la procédure de restauration ou d’escalade.
- Documenter l’alerte réseau, la période, les équipements et services affectés, puis ouvrir une investigation proportionnée. Ne pas retirer de lien pour tester la redondance.
- Identifier les trois postes, la raison de leur exception et leur criticité, puis organiser leur correction selon la politique et les risques de sécurité. Ne pas masquer leur non-conformité.
- Conserver la preuve, attribuer un responsable et vérifier la résolution de chaque exception.

### Partie F — Mesurer et améliorer

Propose trois indicateurs de suivi et explique comment ils seront utilisés.

**Correction possible :**

1. taux de tâches réalisées à échéance, avec une analyse des tâches critiques en retard ;
2. nombre et âge des exceptions non résolues, pondérés par le risque ;
3. taux d’échec ou de récurrence des contrôles et incidents concernés, afin de vérifier si le programme détecte et réduit les problèmes.

Il faut examiner les tendances dans le temps et compléter les chiffres par des faits et des actions. Un indicateur seul ne prouve pas que le programme est efficace.

### Conditions de réussite

Le défi est réussi si tu peux présenter un inventaire compréhensible, expliquer la criticité, rédiger des tâches vérifiables, justifier les fréquences proposées, distinguer routine et intervention à risque, prévoir les preuves et démontrer comment une anomalie sera suivie jusqu’à sa résolution.

## 23. Synthèse opérationnelle

La maintenance préventive est un programme de contrôles et d’actions planifiés, construit à partir des actifs, de leur usage, de leur criticité et des risques. Elle ne se réduit ni au nettoyage, ni aux mises à jour, ni à la fermeture de tâches dans un outil.

Pour démarrer correctement :

1. connaître les actifs et les services qu’ils supportent ;
2. identifier les conséquences d’une défaillance ;
3. choisir des contrôles adaptés au risque ;
4. justifier les fréquences et les critères de réussite ;
5. planifier les ressources, les fenêtres et les autorisations ;
6. exécuter la tâche sans dépasser le périmètre approuvé ;
7. documenter les preuves et les anomalies ;
8. traiter les écarts au lieu de les masquer ;
9. revoir le plan à partir des incidents, tendances et retours d’expérience.

Un bon programme accepte l’existence d’incertitudes et les rend visibles. Il distingue ce qui a été vérifié de ce qui reste inconnu, puis transforme ces informations en actions de maintenance plus sûres et plus utiles.

## 24. Ressources pour approfondir

- [INRS — Définitions et types de maintenance](https://www.inrs.fr/risques/maintenance/definitions.html) : définitions de la maintenance corrective, préventive systématique et conditionnelle.
- [INRS — Organisation de la maintenance et prévention](https://www.inrs.fr/risques/maintenance/prevention.html) : préparation, ressources, planification, évaluation des risques, coordination, contrôles après intervention et retour d’expérience.
- [INRS — Facteurs de risque en maintenance](https://www.inrs.fr/risques/maintenance/facteurs-risque.html) : exemples de risques liés à la planification, aux moyens et à l’organisation.
- [Microsoft Learn — Fenêtres de maintenance Windows](https://learn.microsoft.com/fr-fr/windows/deployment/update/wufb-compliancedeadlines) : gestion des fenêtres et de la planification des mises à jour, selon les versions et capacités disponibles.
- [Microsoft Learn — Maintenance automatique Windows](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-maintenence) : fonctionnement général des tâches de maintenance opportunistes de Windows.
- [CISA — StopRansomware Guide](https://www.cisa.gov/stopransomware/ransomware-guide) : inventaire des actifs et pratiques générales de protection et de récupération.

Les procédures locales, la documentation du fabricant, les obligations applicables et les autorisations de l’organisation doivent toujours être vérifiées avant une intervention réelle.
