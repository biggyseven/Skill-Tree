# KPI de maintenance (MTTR, MTBF)

> **Mise en contexte** — Au niveau expert, piloter la maintenance ne consiste pas à afficher un tableau de chiffres colorés. Il faut transformer des données opérationnelles imparfaites en décisions fiables : quels actifs concentrent le risque, quelles défaillances reviennent, où le temps d'indisponibilité se forme, si le préventif réduit réellement les pannes et si les ressources sont affectées au bon endroit. Un KPI n'a de valeur que si sa définition, son périmètre, sa source, son calcul, ses limites et la décision associée sont compris par ceux qui l'utilisent.

## Présentation et enjeux

La maintenance intervient dans un environnement où coexistent fiabilité technique, disponibilité du service, sécurité, coûts, expérience utilisateur, exigences contractuelles et obligations de continuité. Aucun indicateur isolé ne décrit tous ces objectifs. Le MTBF renseigne sur la durée moyenne de fonctionnement entre défaillances pour un système réparable dans une population et une période définies. Le MTTR renseigne sur une durée moyenne liée à la réparation ou au rétablissement, selon la définition retenue. Ces deux mesures sont complémentaires : la fréquence des pannes et la durée de récupération contribuent ensemble à l'indisponibilité, mais elles ne capturent pas les mêmes mécanismes.

Les acronymes sont parfois utilisés de manière ambiguë. MTTR peut désigner le temps moyen de réparation, de rétablissement ou de résolution selon le métier et l'outil. MTTD est généralement associé au temps moyen de détection ; MTTA au temps moyen d'accusé de réception ou de prise en charge ; MTTF au temps moyen avant défaillance d'un élément non réparable ; MDT au temps moyen d'indisponibilité. Avant de comparer des indicateurs, l'organisation doit donc fixer une définition locale claire, notamment le point de départ, le point de fin, les pauses, les maintenances planifiées et les règles applicables aux incidents ouverts.

Le niveau expert ajoute une difficulté de gouvernance : les résultats dépendent autant de la qualité des données que de la formule. Si la date de rétablissement est absente, si un ticket parent et ses sous-tickets sont tous comptés comme des pannes, si les actifs retirés restent dans le dénominateur, ou si la maintenance planifiée est traitée comme une panne non planifiée, une formule mathématiquement correcte donnera un résultat trompeur. Un indicateur peut aussi être manipulé sans falsifier de données : reclasser les incidents, réduire artificiellement le temps d'indisponibilité en fermant tôt les tickets ou exclure les équipements les moins performants suffit parfois à améliorer le résultat affiché.

Ce cours couvre la définition des KPI, les formules, les conventions de calcul, les contrôles de données, l'analyse statistique, les tableaux de bord, la gouvernance des seuils et le suivi de l'amélioration. Les exemples combinent maintenance d'équipements, infrastructures informatiques et services de support. Ils doivent être adaptés à la nature des actifs, au contrat, aux objectifs de service et aux conventions internes approuvées.

## Objectifs pédagogiques

À la fin du parcours, l'apprenant pourra :

- distinguer fiabilité, maintenabilité, disponibilité, performance opérationnelle et qualité de service ;
- définir sans ambiguïté MTBF, MTTR, MTTD, MTTA, MTTF et MDT ;
- calculer les indicateurs à partir d'événements horodatés et d'heures de fonctionnement ;
- choisir le bon dénominateur et expliquer les effets des exclusions ou des données manquantes ;
- construire un dictionnaire de KPI avec source, formule, unité, périmètre, fréquence, propriétaire et décision associée ;
- utiliser des médianes, percentiles, distributions et cohortes lorsque la moyenne masque des écarts ;
- distinguer corrélation, causalité, saisonnalité, changement de population et effet d'une action ;
- concevoir un tableau de bord orienté décisions plutôt qu'une collection de compteurs ;
- détecter les indicateurs manipulables ou incomplets et établir des contrôles anti-gaming ;
- automatiser un calcul simple sans masquer les erreurs de données ni faire passer un résultat partiel pour un bilan complet ;
- définir une cible, une référence, une intervention et un contrôle d'efficacité avant de conclure à une amélioration.

## Prérequis et cadre de mesure

Le parcours suppose de savoir lire les tickets et ordres de travail, identifier les actifs, comprendre une chronologie d'incident, interpréter des journaux et lire un tableau de bord. Les KPI doivent être utilisés selon les procédures approuvées. Les exemples du cours n'autorisent aucune action en production et ne remplacent pas les engagements contractuels ou les règles internes.

Une mesure opérationnelle utile doit permettre de répondre à six questions : que mesure-t-on, sur quelle population, pendant quelle période, à partir de quelle source, par quelle formule et pour quelle décision ? Si une de ces réponses manque, le nombre doit être considéré comme provisoire ou non comparable. Le lecteur doit pouvoir reproduire le résultat à partir des données de référence, connaître les limites et comprendre si le chiffre porte sur un actif, une famille d'actifs, une équipe, un service ou toute une organisation.

Les données doivent être protégées selon leur sensibilité. Un tableau de bord destiné à la direction n'a pas besoin d'exposer les noms des techniciens, les journaux détaillés, les identifiants de clients ou des informations de sécurité. Les analyses de performance individuelle peuvent être biaisées par la complexité des tickets, les dépendances et la répartition des horaires ; elles exigent une gouvernance appropriée et ne doivent pas remplacer l'analyse du processus.

## Vocabulaire de référence

| Terme | Définition opérationnelle |
|---|---|
| KPI | Indicateur clé relié à un objectif et à une décision. |
| Fiabilité | Capacité d'un actif ou service à accomplir la fonction requise pendant une durée et des conditions définies. |
| Maintenabilité | Capacité à être diagnostiqué, réparé et remis en état dans un délai et avec des ressources donnés. |
| Disponibilité | Proportion du temps pendant lequel le service satisfait les conditions d'aptitude à l'usage définies. |
| MTBF | Mean Time Between Failures : temps de fonctionnement cumulé divisé par le nombre de défaillances pertinentes pour les éléments réparables, selon la convention adoptée. |
| MTTR | Mean Time To Repair ou parfois Recovery/Resolve : durée associée à la réparation ou au rétablissement divisée par le nombre d'événements retenus ; la convention doit être documentée. |
| MTTF | Mean Time To Failure : temps moyen avant défaillance d'un élément considéré comme non réparable ou remplacé après défaillance. |
| MTTD | Mean Time To Detect : temps moyen entre l'apparition d'un problème et sa détection, selon les horodatages définis. |
| MTTA | Mean Time To Acknowledge : temps moyen jusqu'à l'accusé de réception ou la prise en charge qualifiée, selon la convention locale. |
| MDT | Mean Down Time : durée moyenne d'indisponibilité par événement selon les bornes retenues. |
| Taux de panne | Nombre d'événements de panne divisé par une base de temps, une population ou une exposition définie. |
| Temps de fonctionnement | Temps où l'actif était effectivement en état de fournir le service attendu ; la méthode d'observation doit être claire. |
| Temps de réparation active | Temps passé à diagnostiquer, réparer ou tester activement, distinct des délais d'attente si la convention les sépare. |
| Temps d'indisponibilité | Intervalle durant lequel le service ne satisfait pas le critère défini ; il peut dépasser le temps de réparation active. |
| Ordre de travail | Enregistrement d'une intervention de maintenance, avec périmètre, statut, ressources et résultats. |
| Période de référence | Période documentée utilisée pour comparer un résultat ultérieur dans des conditions suffisamment comparables. |
| Population | Ensemble des actifs ou événements auxquels la mesure prétend s'appliquer. |
| Cohorte | Groupe d'éléments partageant une caractéristique définie : modèle, criticité, site, âge ou service. |
| Dénominateur | Base sur laquelle le KPI est calculé ; un changement de dénominateur peut rendre une comparaison invalide. |
| SLA | Engagement de niveau de service, avec des règles de mesure contractuelles et des exclusions définies. |
| OEE/TRS | Overall Equipment Effectiveness ou taux de rendement synthétique, indicateur industriel combinant disponibilité, performance et qualité selon une méthode définie. |

## Schémas de référence

### Schéma 1 — Les KPI répondent à des questions différentes

~~~mermaid
flowchart TD
  A[Événement de panne] --> B[Détection]
  B --> C[Prise en charge]
  C --> D[Diagnostic et réparation]
  D --> E[Validation du service]
  F[Temps de fonctionnement entre pannes] --> G[MTBF]
  B --> H[MTTD]
  C --> I[MTTA]
  D --> J[MTTR selon convention]
  E --> K[Retour au service confirmé]
~~~

Les étapes doivent être définies dans le système d'enregistrement. Un même horodatage ne doit pas être utilisé par facilité pour mesurer plusieurs temps si les événements métier sont distincts.

### Schéma 2 — Décomposer le temps d'un incident

~~~mermaid
flowchart LR
  A[Défaillance] --> B[Détection]
  B --> C[Attente de prise en charge]
  C --> D[Diagnostic]
  D --> E[Attente de pièce ou fournisseur]
  E --> F[Réparation et test]
  F --> G[Rétablissement validé]
~~~

Le délai total peut comprendre des temps actifs et des temps d'attente. Selon l'objectif, les mesurer ensemble montre l'expérience réelle ; les séparer aide à déterminer où agir. Ne pas retirer un délai d'attente du MTTR contractuel si la convention de service exige de le compter.

### Schéma 3 — Fiabilité, maintenabilité et disponibilité

~~~mermaid
flowchart TD
  A[Réduire la fréquence des pannes] --> B[MTBF plus élevé]
  C[Réduire le délai de réparation] --> D[MTTR plus faible]
  B --> E[Disponibilité améliorée]
  D --> E
  F[Maintenance planifiée et dépendances] --> E
  G[Mesure cohérente] --> E
~~~

Un MTBF élevé n'implique pas toujours une grande disponibilité si les rares pannes durent très longtemps. Un MTTR faible ne compense pas nécessairement une fréquence élevée de pannes critiques.

### Schéma 4 — De la source au KPI publié

~~~mermaid
flowchart LR
  A[CMMS et tickets] --> D[Normaliser les événements]
  B[Supervision et télémétrie] --> D
  C[Inventaire et calendrier] --> D
  D --> E[Valider la qualité]
  E --> F[Calcul versionné]
  F --> G[Revue et publication]
  G --> H[Décision et action]
~~~

La traçabilité de la transformation est nécessaire pour reproduire un chiffre et expliquer un changement de résultat. Les erreurs ne doivent pas être absorbées silencieusement.

### Schéma 5 — Contrôle des données avant calcul

~~~mermaid
flowchart TD
  A[Importer les sources] --> B{Identifiants fiables ?}
  B -->|Non| X[Mettre en quarantaine]
  B -->|Oui| C[Contrôler les horodatages]
  C --> D{Chronologie cohérente ?}
  D -->|Non| X
  D -->|Oui| E[Dédupliquer et classifier]
  E --> F[Calculer le KPI]
  F --> G[Valider avec un échantillon]
~~~

Le KPI doit être accompagné du nombre d'événements exclus ou rejetés. Une mesure calculée sur des données incomplètes doit signaler la couverture et ne pas être présentée comme exhaustive.

### Schéma 6 — Détecter une fausse amélioration

~~~mermaid
flowchart TD
  A[MTTR en baisse] --> B[Contrôler les définitions]
  B --> C[Comparer le périmètre]
  C --> D[Examiner fermetures et réouvertures]
  D --> E[Analyser les percentiles]
  E --> F[Examiner l'impact utilisateur]
  F --> G{Amélioration réelle ?}
  G -->|Oui| H[Documenter et maintenir]
  G -->|Non| I[Corriger la mesure ou l'action]
~~~

Une baisse de moyenne peut venir d'un changement de population, d'une exclusion ou d'une clôture prématurée. Les preuves opérationnelles doivent confirmer le progrès annoncé.

### Schéma 7 — Boucle d'amélioration des KPI

~~~mermaid
flowchart LR
  A[Définition du KPI] --> B[Référence mesurée]
  B --> C[Hypothèse d'amélioration]
  C --> D[Action ciblée]
  D --> E[Mesure après action]
  E --> F[Analyse des effets secondaires]
  F --> G{Critères atteints ?}
  G -->|Oui| H[Standardiser]
  G -->|Non| C
~~~

La mesure avant intervention est nécessaire pour attribuer un résultat à une action. Lorsque plusieurs changements surviennent simultanément, la conclusion causale doit rester prudente.

### Schéma 8 — Lire une distribution, pas seulement une moyenne

~~~mermaid
flowchart TD
  A[Événements individuels] --> B[Moyenne]
  A --> C[Médiane]
  A --> D[P90 ou P95]
  A --> E[Outliers et segments]
  B --> F[Vue combinée]
  C --> F
  D --> F
  E --> F
~~~

La moyenne répond à une question de moyenne arithmétique ; elle ne montre pas à elle seule les cas extrêmes ou la dispersion. La médiane et les percentiles peuvent révéler une longue traîne d'incidents très difficiles à résoudre.

### Schéma 9 — Tableau de bord orienté décision

~~~mermaid
flowchart TD
  A[Objectif métier] --> B[KPI et seuil]
  B --> C[Tendance et segmentation]
  C --> D[Diagnostic des causes]
  D --> E[Décision et propriétaire]
  E --> F[Échéance et validation]
  F --> G[Mesure suivante]
~~~

Chaque indicateur important doit conduire à une question et à une décision potentielle. Un tableau rempli de chiffres sans propriétaire, seuil ou règle d'escalade fournit de la visibilité mais ne garantit pas un pilotage.

### Schéma 10 — Définir une cible équilibrée

~~~mermaid
flowchart TD
  A[MTTR] --> D[Équilibre de performance]
  B[MTBF et récurrence] --> D
  C[Qualité et sécurité] --> D
  E[Coût et charge] --> D
  F[Satisfaction et disponibilité] --> D
  D --> G[Décision équilibrée]
~~~

Réduire les délais ne doit pas conduire à supprimer les tests, à minimiser les diagnostics ou à clôturer prématurément les tickets. Les résultats doivent tenir compte de la qualité, de la sécurité et de la durabilité.

### Schéma 11 — Contrôles du changement de KPI

~~~mermaid
flowchart TD
  A[Demande de nouvelle définition] --> B[Documenter la raison]
  B --> C[Recalculer l'historique si possible]
  C --> D[Comparer ancienne et nouvelle série]
  D --> E[Validation du propriétaire]
  E --> F[Versionner et annoncer]
~~~

Changer une formule, un calendrier ou une règle d'exclusion peut créer une rupture de série. Si l'historique ne peut pas être recalculé, matérialiser la rupture plutôt que d'assembler les mesures comme si elles étaient équivalentes.

### Schéma 12 — Responsabilités de gouvernance

~~~mermaid
flowchart LR
  A[Propriétaire du service] --> B[Objectif et décision]
  C[Propriétaire des données] --> D[Qualité et définition]
  E[Analyste maintenance] --> F[Calcul et interprétation]
  G[Contrôle indépendant] --> H[Validation et auditabilité]
  B --> I[Revue périodique]
  D --> I
  F --> I
  H --> I
~~~

La responsabilité du nombre, celle des données, celle de la décision et celle du contrôle doivent être explicites. La séparation de rôles est particulièrement importante lorsqu'un indicateur est utilisé pour des contrats, des primes ou des décisions de remplacement.

## 1. Définir précisément MTBF, MTTR et les indicateurs associés

### 1.1 MTBF — Mean Time Between Failures

Le MTBF mesure, pour une population d'équipements réparables donnée, le temps de fonctionnement cumulé divisé par le nombre de défaillances retenues sur la période. Il est souvent exprimé en heures. L'équipement, la population, le temps de fonctionnement et la définition d'une défaillance doivent rester constants à l'intérieur de la comparaison.

Formule simplifiée :

MTBF = temps de fonctionnement total / nombre de défaillances retenues

Exemple : un équipement a fonctionné 1 800 heures et a subi 6 défaillances qualifiées pendant la période. Son MTBF observé est de 300 heures. Cela représente une moyenne historique calculée sur les données observées ; cela ne garantit pas que le prochain intervalle sera de 300 heures, ni que la panne surviendra à intervalles réguliers. Les taux observés peuvent varier avec la charge, l'environnement, l'âge, la maintenance, les changements et la définition des événements.

Le calcul doit éviter de compter plusieurs fois le même incident. Un incident majeur peut entraîner de nombreux tickets secondaires ou alertes de supervision. Le nombre de tickets n'est pas nécessairement le nombre de défaillances physiques ou fonctionnelles. Définir une règle d'agrégation, une fenêtre de corrélation et une validation humaine pour les événements ambigus. Une défaillance répétée après une réparation peut être un nouvel événement si le service a réellement été rétabli ; elle peut être la continuation du même événement si la résolution n'a jamais été confirmée. La convention doit être écrite.

Lorsque plusieurs actifs sont agrégés, le MTBF calculé à partir du temps de fonctionnement total et du nombre total de défaillances ne signifie pas forcément « intervalle moyen de chaque actif ». Le groupe doit être homogène ou les différences doivent être présentées. Un serveur rarement utilisé, un commutateur de cœur et un équipement de test ne devraient pas automatiquement partager la même série sans segmentation.

### 1.2 MTTR — Mean Time To Repair ou Recovery

Le MTTR est fréquemment utilisé pour désigner la durée moyenne de réparation, mais certains métiers emploient le même acronyme pour le rétablissement, la résolution ou la récupération. L'organisation doit préciser la convention dans son dictionnaire de données. Une mesure opérationnelle fréquente consiste à additionner les durées retenues pour les événements réparés et à diviser par le nombre de réparations ou événements éligibles.

MTTR = durée totale retenue pour les réparations / nombre d'événements de réparation retenus

Le début et la fin doivent être définis : apparition de la panne, détection, enregistrement, prise en charge, début de réparation, retour technique, validation métier ou clôture du ticket. Ces bornes répondent à des questions différentes. Si l'objectif est l'indisponibilité ressentie par les utilisateurs, mesurer uniquement le temps où le technicien manipulait l'équipement sous-estime souvent l'expérience réelle. Si l'objectif est l'efficacité des gestes de réparation, il peut être utile de séparer le temps actif des délais d'attente, tout en conservant le délai de bout en bout.

Exemple : quatre réparations ont des durées de 40, 65, 90 et 105 minutes entre l'entrée dans l'état de réparation défini et le retour technique validé. La somme est de 300 minutes et le MTTR est de 75 minutes. La mesure n'est valide que si les quatre événements sont comparables, terminés et conformes à la règle de comptage. Les cas ouverts peuvent nécessiter une analyse séparée, car leur durée continue d'augmenter et une moyenne calculée uniquement sur les événements clos peut donner une image trop favorable.

### 1.3 MTTD, MTTA et autres étapes

MTTD mesure généralement le délai entre l'apparition d'une défaillance et le moment où elle est détectée. La fiabilité du résultat dépend de la définition du début. Si le début est déterminé manuellement après investigation, la mesure sous-estime souvent l'intervalle réel. Les systèmes instrumentés peuvent fournir une meilleure chronologie si leurs horloges sont synchronisées et leurs règles d'alerte documentées.

MTTA désigne souvent le délai jusqu'à l'accusé de réception ou la prise en charge d'une alerte. Selon les organisations, il peut signifier qu'une personne a vu le ticket, qu'elle a accepté la responsabilité ou qu'elle a commencé un diagnostic. Choisir la définition qui correspond à l'engagement suivi. Un simple changement automatique de statut ne prouve pas que l'équipe travaille activement sur le problème.

Pour les délais détaillés, on peut suivre le temps jusqu'au diagnostic, le temps d'attente d'une pièce, le temps d'attente fournisseur, le temps de réparation active, le temps de test et le temps de validation. Ces mesures sont pertinentes si leur définition permet une action. Ajouter davantage de métriques n'améliore pas mécaniquement le pilotage ; chaque KPI demande une qualité de données, une revue et un propriétaire.

### 1.4 MTTF, MDT et disponibilité

MTTF est habituellement employé pour le temps moyen avant la défaillance d'un élément considéré comme non réparable ou qui est remplacé après panne. Le distinguer du MTBF évite de mélanger des stratégies de réparation et de remplacement. Pour les équipements réparables, le MTBF reste une convention courante, à condition d'identifier les événements et le temps de fonctionnement.

MDT est une mesure de durée moyenne d'indisponibilité selon un début et une fin convenus. Il peut inclure des délais de détection, diagnostic, attente et validation, tandis qu'un MTTR limité à la réparation active peut être beaucoup plus court. Ne pas comparer ces deux mesures comme si elles avaient la même définition.

Une formule simplifiée d'une disponibilité intrinsèque pour un modèle réparable est souvent écrite comme suit :

Disponibilité ≈ MTBF / (MTBF + MTTR)

Cette relation suppose des conventions de temps cohérentes et un modèle simple ; elle ne représente pas automatiquement la disponibilité contractuelle ou observée. Les indisponibilités planifiées, les arrêts logistiques, les redondances, la maintenance, les périodes de service attendues et les règles de mesure peuvent modifier le calcul. Pour un SLA, appliquer la formule contractuelle et ses exclusions, pas une approximation générique.

## 2. Exemple complet de calcul

Considérons une plateforme dont la durée théorique de fonctionnement sur quatre semaines de 7 jours est de 672 heures. L'organisation retire du périmètre 12 heures de maintenance planifiée, selon une convention explicitement approuvée. Le temps de service attendu dans cette période est donc de 660 heures. Pendant la période, 5 pannes éligibles ont été recensées, dont les durées d'indisponibilité sont de 1,5 h, 2 h, 3 h, 0,5 h et 5 h.

Le temps d'indisponibilité non planifiée cumulé est de 12 heures. Si le temps d'exposition opérationnelle retenu pour le MTBF est de 648 heures, parce que cette définition exclut l'indisponibilité et n'utilise pas le calendrier de service attendu, alors le MTBF observé sera 648 / 5 = 129,6 heures. Cette valeur illustre surtout un point : il faut annoncer la convention exacte du temps de fonctionnement, car une autre définition du dénominateur donnera un résultat différent.

Le délai moyen d'indisponibilité par panne, si les cinq événements constituent le même ensemble et que les durées sont bien celles retenues par le SLA, est de 12 / 5 = 2,4 heures. Si le MTTR est défini comme réparation active et que les données ne mesurent que 5 heures au total de gestes de réparation, alors le MTTR de réparation active est 5 / 5 = 1 heure. Les deux valeurs ne sont pas contradictoires : l'une couvre l'indisponibilité bout en bout, l'autre le temps actif de réparation. Les intitulés doivent le rendre évident.

Si la disponibilité SLA est calculée comme (temps de service attendu − indisponibilité non planifiée) / temps de service attendu, alors elle est (660 − 12) / 660, soit environ 98,18 %. Cette formule n'est pertinente que si la définition contractuelle utilise ces exclusions et cet ensemble d'événements. Dans un rapport, afficher la formule ainsi que les heures planifiées exclues et les 12 heures d'indisponibilité est plus honnête que ne présenter que « 98,18 % ».

### Contrôles à effectuer avant d'accepter le résultat

- Le calendrier de service attendu est-il correct et identique à celui de la période de comparaison ?
- Les fenêtres de maintenance planifiée sont-elles approuvées et classées selon les règles de l'indicateur ?
- Les cinq pannes sont-elles des événements distincts et éligibles ?
- Les heures de début et de fin concordent-elles avec les journaux et les tickets ?
- Le MTBF est-il calculé sur le temps d'exposition défini et non sur un nombre de tickets ?
- Le MTTR décrit-il le temps de réparation, le rétablissement ou la résolution ?
- Les incidents encore ouverts et les données manquantes sont-ils visibles ?
- La précision décimale est-elle proportionnée à la qualité des données ?

## 3. Construire un dictionnaire de KPI

Un dictionnaire est le contrat de mesure entre les équipes. Il doit être versionné et approuvé. Pour chaque KPI, consigner le nom complet, l'objectif, la question à laquelle il répond, la formule, les unités, la source, la population, les exclusions, la fréquence, le propriétaire, la cible, le seuil d'escalade, le public, les limites et la dernière date de validation.

| KPI | Formule indicative | Question utile | Précaution |
|---|---|---|---|
| MTBF | Temps de fonctionnement / défaillances retenues | À quelle fréquence le système connaît-il des défaillances ? | Clarifier la population, l'exposition et l'événement de panne. |
| MTTR réparation | Durée de réparation retenue / réparations | Combien de temps faut-il pour effectuer la réparation ? | Définir les temps actifs et les pauses. |
| MTTR rétablissement | Durée entre la panne et le retour de service / événements | Combien de temps le service reste-t-il dégradé ? | Ne pas confondre clôture et validation de service. |
| MTTD | Somme des délais de détection / événements mesurables | Combien de temps le problème reste-t-il non détecté ? | Le début peut être incertain si l'événement est connu après coup. |
| MTTA | Somme des délais d'accusé de réception / alertes éligibles | Combien de temps avant qu'une équipe prenne en charge l'alerte ? | Un accusé automatique n'est pas nécessairement une prise en charge réelle. |
| Disponibilité | Temps disponible / temps de service attendu | Quelle proportion du service attendu a été disponible ? | Appliquer les exclusions et règles du contrat. |
| Taux de récidive | Événements récurrents selon la règle / événements ou actifs suivis | Les corrections évitent-elles la répétition ? | Définir la fenêtre et la notion de même problème. |
| Conformité préventive | Tâches préventives réalisées dans les règles / tâches exigibles | Le plan est-il exécuté conformément à la politique ? | Définir les retards tolérés et la criticité. |
| Backlog en retard | Ordres de travail échus non terminés / ordres de travail échus | Quel volume de maintenance en retard persiste ? | Segmenter selon la criticité et les dépendances. |
| Part de maintenance planifiée | Heures planifiées / heures totales de maintenance | Quelle part du travail est anticipée ? | Les catégories et les temps saisis doivent être cohérents. |
| First-time fix | Interventions réparées sans retour ou récidive dans la fenêtre / interventions éligibles | La première intervention règle-t-elle durablement le problème ? | Définir la fenêtre et les retours associés. |
| Coût par actif ou événement | Coûts retenus / actifs ou événements éligibles | Où le coût se concentre-t-il ? | Inclure ou exclure pièces, sous-traitance et coûts indirects explicitement. |
| Couverture des données | Actifs ou événements mesurables / population attendue | Peut-on faire confiance au KPI à cette période ? | Publier ce chiffre avec les autres indicateurs. |

Éviter les définitions écrites uniquement dans un fichier personnel ou dans une formule de tableur sans commentaire. Si deux équipes nomment MTTR des métriques différentes, il faut harmoniser ou ajouter un qualificatif visible au nom du KPI. Dans un dashboard, préférer « MTTR réparation active — heures » et « délai moyen de rétablissement — heures » plutôt qu'un unique MTTR dont le sens change selon les graphiques.

## 4. Mesurer la qualité des données avant la performance

La première étape du calcul consiste à établir quelles données sont disponibles. L'inventaire doit représenter la population pertinente et fournir une clé de rapprochement. Les tickets doivent être classifiés de manière cohérente, les horodatages doivent être valides, les statuts doivent être normalisés et les doublons doivent être détectés. Les changements de fuseau horaire, d'heure d'été ou de synchronisation entre outils peuvent produire des durées négatives ou des événements apparaissant dans le mauvais ordre.

Pour chaque KPI, produire au moins un indicateur de qualité des données : proportion des événements ayant les deux horodatages requis, part des actifs rattachés à une catégorie, nombre de doublons détectés, proportion de tickets sans actif, nombre de durées négatives rejetées et date de dernière mise à jour de chaque source. Ces valeurs ne sont pas des notes accessoires : elles qualifient le niveau de confiance que l'organisation peut accorder au chiffre.

Les règles de nettoyage ne doivent pas corriger silencieusement les anomalies. Si une fin de panne précède le début, la ligne doit être rejetée ou mise en quarantaine jusqu'à vérification. Si un ticket est marqué « terminé » mais qu'aucun horodatage de rétablissement n'existe, il ne faut pas lui attribuer une durée nulle par défaut. La valeur zéro signifie un événement de durée nulle, pas une durée inconnue. Une moyenne qui ignore des valeurs manquantes peut être calculable mais biaisée : publier la couverture et les exclusions.

La déduplication doit s'appuyer sur une règle expliquée. Des alertes répétées sur un incident unique peuvent être regroupées dans une même panne, alors que deux défaillances distinctes d'un actif avec un rétablissement confirmé doivent rester séparées. Le regroupement doit tenir compte de la cause, de la ressource, de la fenêtre temporelle et du retour effectif au service. Une intervention préventive n'est pas une panne si le dictionnaire de données la traite séparément.

## 5. Utiliser moyenne, médiane, percentiles et segmentation

La moyenne résume l'ensemble des durées mais est sensible aux événements exceptionnellement longs. Supposons neuf interventions dont le délai de rétablissement est d'une heure chacune et un dixième délai de 21 heures. La moyenne vaut 3 heures ; la médiane vaut 1 heure. Afficher uniquement la moyenne suggère qu'une intervention typique prend trois heures, alors que neuf événements sur dix ont duré une heure et qu'un événement très long explique l'écart. Les deux statistiques sont utiles, mais elles répondent à des questions différentes.

Le P90 est la durée sous laquelle se situent environ 90 % des observations, selon la méthode de calcul de percentile choisie. Il permet d'examiner la queue de distribution et les cas difficiles. Comparer des P90 d'échantillons très petits exige prudence : la méthode de calcul, la taille, les ex aequo et les observations censurées peuvent modifier le résultat. Documenter l'algorithme ou laisser l'outil de référence calculer une série cohérente.

Segmenter les mesures selon la criticité, le site, la famille de matériel, le fournisseur, le type d'incident, l'équipe de garde, la tranche horaire, l'âge ou le statut de cycle de vie. Cette analyse permet souvent d'identifier une explication actionnable. Un MTTR global peut augmenter parce qu'un actif exceptionnellement complexe a été ajouté à la population, même si les équipes se sont améliorées pour chaque catégorie. C'est un effet de composition, pas nécessairement une dégradation des performances.

Les comparaisons doivent utiliser des définitions et populations comparables. Si le système de tickets a changé, si les heures de service ont été étendues, si les incidents majeurs ont été désormais comptés ou si l'inventaire s'est enrichi, signaler une rupture de série et recalculer l'historique lorsque cela est possible. Ne pas présenter les deux valeurs sans commentaire comme une évolution opérationnelle directe.

## 6. Interpréter MTBF et MTTR ensemble

Un MTBF en baisse signifie que les défaillances arrivent plus fréquemment dans la population et selon la définition mesurées. Il ne prouve pas, à lui seul, que les techniciens entretiennent mal le matériel. Les défaillances peuvent être influencées par la charge, l'environnement, un changement de version, un fournisseur, l'âge, des conditions saisonnières ou une amélioration de la détection. Une hausse du nombre de tickets de panne peut aussi traduire une meilleure détection, pas nécessairement une baisse de fiabilité réelle.

Un MTTR en hausse peut refléter un temps de diagnostic plus long, une pénurie de pièces, un accès fournisseur tardif, des dépendances documentées insuffisamment, un changement d'équipe, un délai d'approbation, une validation métier tardive ou une hausse de la complexité des incidents. Les étapes intermédiaires permettent de localiser la contrainte plutôt que de prescrire une accélération générale de la réparation.

L'association des deux indicateurs donne un tableau plus complet. Une meilleure disponibilité peut venir de moins de pannes, de réparations plus rapides ou des deux. Une maintenance peut aussi réduire légèrement la fréquence mais prolonger les interventions ; l'organisation doit examiner l'effet net sur le service et les coûts. La disponibilité théorique dérivée du MTBF et du MTTR peut servir à comprendre le mécanisme dans un modèle simple, mais la disponibilité observée et contractuelle reste à calculer selon les règles pertinentes.

L'analyse causale demande plus qu'une courbe avant/après. Définir une hypothèse, mesurer une période de référence, documenter l'intervention et les autres changements, puis suivre les mêmes cohortes. Si plusieurs modifications sont lancées simultanément, dire que le progrès est compatible avec le programme plutôt qu'affirmer sans réserve que chaque action a causé le résultat. Une comparaison avec une cohorte comparable ou un déploiement progressif peut améliorer l'inférence lorsque le contexte le permet.

## 7. Construire un tableau de bord de maintenance qui sert les décisions

Un tableau de bord commence par la décision à prendre. Le directeur de maintenance peut avoir besoin de connaître les risques sur les actifs critiques et le retard de maintenance ; le responsable de service a besoin des tendances de disponibilité et de récurrence ; le planificateur suit le backlog, les ressources et les pièces ; le technicien a besoin d'informations plus détaillées sur les pannes, les causes et les actions à réaliser. Un même écran ne doit pas tenter de satisfaire tous les publics avec une accumulation de graphiques.

Une structure utile comprend un petit nombre d'indicateurs principaux, une tendance temporelle, les segments qui expliquent le résultat, les exceptions prioritaires, la qualité des données et les actions en cours. Le détail doit être accessible à partir du niveau agrégé tout en respectant les autorisations. Les seuils doivent refléter les objectifs du service et les risques, pas seulement des couleurs choisies par convenance.

Chaque indicateur critique doit avoir une définition consultable : formule, unité, source, période, heure de dernière actualisation, population, exclusions, seuil, propriétaire et procédure d'escalade. Le lecteur doit savoir si la donnée est réelle, estimée, partielle ou provisoire. Si le dernier import est en échec, le tableau de bord ne doit pas afficher la valeur précédente comme si elle était actuelle.

Ne pas associer la couleur à la seule valeur absolue. Un MTTR de trois heures peut être acceptable pour une intervention planifiée sur un système de soutien et inacceptable pour un service critique avec un engagement de rétablissement de trente minutes. Les seuils peuvent donc être segmentés. Mais trop de seuils personnalisés peuvent rendre le tableau incompréhensible ; les règles doivent être stables et expliquées.

### Recommandations de visualisation

- Utiliser une courbe pour les tendances, avec la période de référence et les changements de définition visibles.
- Afficher moyenne et médiane, et ajouter P90/P95 lorsque les cas longs sont importants.
- Utiliser des barres segmentées pour comparer familles d'actifs, criticité ou sites, en affichant les volumes de chaque groupe.
- Mettre en évidence les exceptions associées à une action, plutôt que multiplier les cartes rouges et vertes.
- Afficher la couverture et la date des sources proches du KPI, pas uniquement dans une annexe.
- Eviter les axes tronqués ou les comparaisons de populations inégales sans explication.
- Assurer l'accessibilité des couleurs et fournir un libellé textuel pour les statuts critiques.
- Limiter les données personnelles ; un tableau de bord de pilotage n'a pas besoin d'exposer les détails nominaux de chaque intervention.

## 8. Se prémunir contre les effets pervers et le gaming des KPI

Quand une métrique devient un objectif, les équipes peuvent optimiser la valeur affichée au détriment de ce qui est réellement important. Il peut s'agir d'une conséquence involontaire de la pression, d'une définition mal conçue ou d'une incitation explicite. Le propriétaire du KPI doit penser aux comportements que la mesure peut encourager.

### Exemple : le MTTR diminue mais la satisfaction se dégrade

Une équipe ferme les tickets dès que l'équipement répond à un ping, alors que l'application n'a pas été testée. Le délai affiché baisse, mais les tickets sont réouverts ou les utilisateurs déclarent que le service reste inutilisable. Le correctif n'est pas simplement d'augmenter la cible de MTTR. Il faut définir le retour au service au regard du service métier, contrôler les réouvertures et ajouter une mesure de validation.

### Exemple : le MTBF paraît augmenter après l'exclusion d'actifs

Le périmètre de reporting a été modifié pour exclure les équipements les plus anciens et les plus sujets aux pannes. Le MTBF augmente parce que la population a changé. Il faut comparer la série sur une population stable ou afficher séparément la nouvelle cohorte, puis expliquer le changement dans le rapport.

### Exemple : la maintenance préventive est déclarée complète sans vérification

Les tâches non réalisées sont marquées terminées afin d'atteindre un objectif mensuel. Le taux de conformité préventive s'améliore, mais le registre ne correspond plus à la réalité. Le contrôle doit rapprocher les statuts des preuves de réalisation, des mesures requises, de la consommation de pièces et d'un échantillon indépendant d'actifs.

### Contrôles anti-gaming

- Conserver les définitions et la formule versionnées, approuvées et accessibles.
- Contrôler les changements de classification, de périmètre, de statuts et d'horodatages.
- Suivre les réouvertures, récidives, plaintes utilisateurs et pannes majeures en plus des délais.
- Comparer les agrégats aux événements bruts et tester les exclusions sur échantillon.
- Séparer les objectifs d'équipe de l'évaluation individuelle si les facteurs externes sont importants.
- Documenter les valeurs manquantes et empêcher qu'elles soient converties en succès par défaut.
- Examiner les effets secondaires avant de récompenser une amélioration statistique.
- Faire vérifier indépendamment les KPI utilisés dans les contrats, primes ou décisions de remplacement.

## 9. Automatiser un calcul avec Python et contrôler le résultat

L'exemple suivant montre une base reproductible pour calculer MTBF et MTTR à partir d'un fichier CSV fictif d'événements. Il n'accède pas aux équipements, ne modifie pas les tickets et ne fournit pas de verdict de conformité. Le fichier contient une ligne par panne retenue et doit avoir les colonnes suivantes : event_id, asset_id, operating_hours, repair_minutes et status. Pour simplifier l'exercice, chaque ligne représente un événement distinct et complet. Dans un environnement réel, les heures de fonctionnement doivent être calculées à partir de la durée d'exposition réelle, et non simplement additionnées ligne par ligne si cela double-compte des périodes communes.

~~~csv
event_id,asset_id,operating_hours,repair_minutes,status
EVT-101,PUMP-01,280,55,closed
EVT-102,PUMP-01,310,80,closed
EVT-103,PUMP-01,260,65,closed
EVT-104,PUMP-01,300,100,closed
~~~

Le code vérifie les champs, les doublons, les valeurs numériques et les statuts avant le calcul. Il signale séparément les lignes invalides et sort avec un code non nul si la qualité des données ne permet pas un résultat fiable.

~~~python
import csv
import sys
from pathlib import Path

REQUIRED = {
    "event_id",
    "asset_id",
    "operating_hours",
    "repair_minutes",
    "status",
}


def load_events(path):
    events = []
    seen_ids = set()

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV vide ou sans en-tête.")

        missing = REQUIRED - set(reader.fieldnames)
        if missing:
            raise ValueError(
                "Colonnes manquantes : " + ", ".join(sorted(missing))
            )

        for line, row in enumerate(reader, start=2):
            event_id = (row.get("event_id") or "").strip()
            asset_id = (row.get("asset_id") or "").strip()
            status = (row.get("status") or "").strip().lower()

            if not event_id or not asset_id:
                raise ValueError(f"Ligne {line} : identifiant obligatoire absent.")
            if event_id in seen_ids:
                raise ValueError(f"Ligne {line} : événement dupliqué {event_id}.")
            if status != "closed":
                raise ValueError(
                    f"Ligne {line} : événement non clos ; calcul interrompu."
                )

            try:
                operating = float(row["operating_hours"])
                repair = float(row["repair_minutes"])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Ligne {line} : durée non numérique.") from exc

            if operating <= 0 or repair < 0:
                raise ValueError(f"Ligne {line} : durée hors domaine.")
            seen_ids.add(event_id)
            events.append({
                "event_id": event_id,
                "asset_id": asset_id,
                "operating_hours": operating,
                "repair_minutes": repair,
            })

    if not events:
        raise ValueError("Aucun événement valide.")
    return events


def calculate_kpis(events):
    operating_total = sum(e["operating_hours"] for e in events)
    repair_total = sum(e["repair_minutes"] for e in events)
    failures = len(events)

    return {
        "failures": failures,
        "operating_hours_as_supplied": operating_total,
        "repair_hours": repair_total / 60,
        "mtbf_hours_indicative": operating_total / failures,
        "mttr_repair_minutes": repair_total / failures,
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python maintenance_kpi.py events.csv")
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print("Fichier introuvable.")
        return 2

    try:
        events = load_events(path)
        result = calculate_kpis(events)
    except (OSError, ValueError) as exc:
        print(f"Calcul refusé : {exc}")
        return 1

    print("KPI calculés à titre indicatif ; vérifier le contrat de données.")
    for key, value in result.items():
        print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
~~~

Lancer le script dans un répertoire de travail avec un export de test :

~~~bash
python maintenance_kpi.py events.csv
~~~

Avec les données ci-dessus, le code additionne les durées de fonctionnement indiquées à chaque événement, puis divise par quatre défaillances. Ce calcul est adapté uniquement à l'exemple dont les valeurs sont définies comme des quantités exposées par événement et non comme des heures totales de fonctionnement d'un même actif sur des périodes qui se recouvrent. Dans une vraie flotte, le temps d'exposition doit provenir d'une population d'actifs et d'une fenêtre sans double comptage ; il faut calculer MTBF par actif ou par groupe homogène selon la question. Le code ne doit donc pas être copié tel quel dans un rapport exécutif sans valider le modèle de données.

### Tests et limites de l'exemple

Tester un fichier normal, un événement dupliqué, un statut ouvert, une durée négative, une valeur non numérique, un fichier sans lignes et des champs manquants. Vérifier que les erreurs empêchent la publication. Comparer quelques calculs manuels avec le résultat du programme. Le script de démonstration échoue sur toute donnée incomplète afin d'éviter une moyenne silencieusement inexacte.

Pour un calcul de production, séparer au moins deux tables : les actifs et leur fenêtre d'exposition, puis les événements de défaillance avec des identifiants stables. Définir comment traiter les actifs remplacés, retirés ou mis en service pendant la période, les incidents qui durent au-delà de la période, les arrêts planifiés et les événements réouverts. Tester la gestion des fuseaux horaires et des heures de fonctionnement réelles lorsqu'elles sont issues de la télémétrie.

La validation du script inclut une revue du code, la version de Python, des tests unitaires, les droits d'accès, le stockage des exports, le contrôle des journaux et l'approbation de la règle de calcul. La sortie devrait inclure la formule et la version de la définition afin que le résultat reste explicable après une évolution du script.

## 10. Atelier pratique guidé — Diagnostic d'un KPI trompeur

### Situation de départ

Une équipe présente au comité de maintenance les chiffres suivants pour deux mois successifs :

| Mesure | Mois A | Mois B |
|---|---:|---:|
| MTTR déclaré | 3,2 h | 2,1 h |
| Nombre de pannes déclarées | 44 | 29 |
| Taux de maintenance préventive à l'échéance | 91 % | 97 % |
| Tickets rouverts dans les sept jours | 6 % | 15 % |
| Actifs disposant d'un propriétaire confirmé | 96 % | 82 % |
| Disponibilité métier déclarée | 99,1 % | 98,4 % |

La présentation initiale conclut que la maintenance s'améliore fortement parce que le MTTR baisse et que le préventif dépasse la cible. Pourtant, les tickets rouverts augmentent, la couverture d'inventaire baisse et la disponibilité métier se détériore. L'équipe doit vérifier si les deux périodes sont comparables avant de valider la conclusion.

### Phase A — Établir le dictionnaire de calcul

Demander la définition exacte du MTTR, la population, les dates de début et de fin, les exclusions, la méthode de traitement des tickets réouverts et la source des heures d'indisponibilité. Déterminer si le nombre de pannes repose sur les incidents techniques, les tickets utilisateurs ou les alertes. Identifier la version de la formule et la date du dernier changement.

Pour le préventif, définir ce qui constitue une tâche exigible, la date d'échéance, la tolérance éventuelle, les règles d'annulation et la preuve de réalisation. Vérifier si une tâche close sans contrôle final est comptée comme conforme. Pour la disponibilité, retrouver la formule de service attendue et les exclusions contractuelles.

### Phase B — Contrôler les données sources

Extraire un échantillon de tickets du Mois A et du Mois B, rapprocher les identifiants d'actifs et vérifier les horodatages. Examiner les quinze pour cent de tickets rouverts du Mois B, les erreurs de catégorie, les valeurs manquantes et les changements de périmètre. Vérifier pourquoi la couverture des propriétaires est passée de 96 % à 82 % et quels actifs sont sortis du calcul.

Vérifier les ordres préventifs par échantillon et rapprocher le statut de clôture, les mesures, le technicien, la date et la validation du résultat. Contrôler si le Mois B a supprimé des actifs ou reclassé des tâches au lieu de traiter les retards réels.

### Phase C — Formuler des hypothèses concurrentes

Hypothèse 1 : le diagnostic ou la réparation est réellement plus rapide grâce à une meilleure disponibilité des pièces. Cette hypothèse devrait être soutenue par les temps intermédiaires, les stocks et la baisse du délai actif, sans dégradation du rétablissement métier.

Hypothèse 2 : la définition du MTTR ou la population a changé. Cette hypothèse serait soutenue par une modification de la formule, des exclusions, des catégories ou de l'inventaire.

Hypothèse 3 : les tickets sont fermés plus tôt, puis rouverts. Cette hypothèse serait soutenue par un délai inférieur entre la fermeture et la réouverture, des tests métiers absents ou un nombre accru d'incidents répétés.

Les hypothèses ne sont pas mutuellement exclusives. Les preuves et les contrôles de qualité doivent déterminer quelle explication est soutenue.

### Phase D — Produire une conclusion équilibrée

Si les données confirment une baisse du temps de réparation active mais montrent une hausse du temps de validation et des réouvertures, rapporter les deux phénomènes. Ne pas résumer le résultat par une amélioration de MTTR sans préciser sa définition. Recalculer les séries sur un périmètre comparable lorsque cela est possible ; sinon, matérialiser la rupture.

Le rapport propose des actions ciblées : rendre obligatoire le test de service avant clôture pour les incidents concernés, surveiller les réouvertures, rétablir la qualité de l'inventaire, documenter les exclusions et réexaminer les règles de maintenance préventive. Chaque action reçoit un propriétaire et un critère de succès.

### Résultat attendu

L'atelier est réussi si l'apprenant peut montrer pourquoi un KPI seul ne suffit pas, retrouver les définitions et la source, identifier les écarts de comparabilité, calculer une métrique cohérente, expliquer les limites et proposer des actions dont l'effet pourra être vérifié sur une période future.

## Études de cas

### Cas 1 — MTBF en baisse après un changement de logiciel

La fréquence d'incidents augmente après un déploiement. L'équipe soupçonne une régression, mais la supervision a aussi été configurée pour détecter des événements auparavant invisibles. Le diagnostic doit séparer le changement de détection du changement de fiabilité. Comparer les types d'incidents, les symptômes, les journaux, les événements confirmés et, si possible, une population comparable non touchée. Si le résultat reste incertain, présenter plusieurs explications plausibles et éviter d'attribuer une cause sans preuve.

### Cas 2 — MTTR moyen stable avec une longue traîne

Le MTTR moyen reste proche de deux heures pendant trois mois, mais le P90 progresse de six à douze heures. Une minorité d'incidents est de plus en plus difficile à résoudre. Segmenter par famille d'actifs, fournisseur, pièces, accès, complexité et temps d'attente. Le résultat peut justifier un plan pour les incidents prolongés sans réclamer à toute l'équipe de diminuer uniformément chaque réparation.

### Cas 3 — Un bon taux préventif masque le backlog critique

Le tableau affiche 98 % de conformité au calendrier. Cependant, plusieurs tâches échues sur les actifs critiques sont reportées et la population de tâches exigibles a été réduite par des annulations. Contrôler le dénominateur, les motifs d'annulation, les autorisations et les reports. Une mesure globale doit être accompagnée d'une vue par criticité et d'un suivi des exceptions.

### Cas 4 — Cible MTTR non adaptée au contrat

Le tableau compare des équipes avec une cible de trente minutes alors que certains services sont couverts par un SLA de quatre heures et d'autres par une astreinte industrielle. Revoir les objectifs par service, les horaires de couverture, le démarrage et la fin du compteur ainsi que les exclusions. Conserver une définition commune pour les comparaisons internes lorsque possible, tout en affichant séparément l'atteinte des engagements contractuels.

## Exercices d'application avec corrigés

### Exercice 1 — Calcul du MTBF

**Question.** Un équipement réparable a cumulé 2 400 heures de fonctionnement mesuré et connu 8 défaillances éligibles. Calculer le MTBF observé.

**Corrigé expliqué.** MTBF = 2 400 / 8 = 300 heures par défaillance en moyenne. Il faut préciser que les 2 400 heures sont du temps de fonctionnement selon la convention retenue, et que les huit événements sont distincts et éligibles. La valeur n'est ni une garantie de durée de vie ni une prédiction déterministe de la prochaine panne.

### Exercice 2 — Calcul du MTTR réparation

**Question.** Les durées de réparation active sont 35, 45, 60 et 100 minutes. Calculer le MTTR et distinguer ce résultat du temps de rétablissement.

**Corrigé expliqué.** La somme est de 240 minutes pour quatre réparations, donc le MTTR de réparation active vaut 60 minutes. Le temps de rétablissement pourrait être plus important s'il comprend la détection, les attentes, les tests et la validation du service. Le nom du KPI doit préciser la convention.

### Exercice 3 — Interpréter une hausse de MTBF

**Question.** Le MTBF monte de 250 à 400 heures au même moment où 20 % des actifs cessent d'être inclus dans l'inventaire. Peut-on conclure à une amélioration de fiabilité ?

**Corrigé expliqué.** Pas sans vérifier le changement de population. Les actifs exclus peuvent concentrer les pannes et améliorer artificiellement la moyenne. Recalculer les périodes sur une cohorte comparable ou afficher le changement de périmètre et une vue séparée des actifs sortis. Contrôler également l'exposition, la classification et la définition des incidents.

### Exercice 4 — Identifier un problème de définition

**Question.** Une équipe calcule le MTTR depuis la création d'un ticket jusqu'à sa fermeture, tandis qu'une autre utilise la durée de réparation active. Pourquoi leurs résultats ne sont-ils pas comparables directement ?

**Corrigé expliqué.** Les points de départ et de fin diffèrent. La première mesure peut inclure détection, attente, diagnostic, validation et retard de clôture ; la seconde ne comprend que les gestes actifs. Les deux peuvent être utiles, mais doivent avoir des noms explicites et un dictionnaire définissant les événements, les pauses et les exclusions.

### Exercice 5 — Contrôler la disponibilité

**Question.** Un service était attendu pendant 700 heures au cours du mois. L'indisponibilité non planifiée éligible au SLA est de 3,5 heures. Calculer la disponibilité selon la formule (temps attendu − indisponibilité) / temps attendu.

**Corrigé expliqué.** Disponibilité = (700 − 3,5) / 700 = 696,5 / 700, soit environ 99,5 %. Le calcul n'est valide que si les 700 heures correspondent au calendrier de service et si les 3,5 heures suivent les règles contractuelles. Préciser les fenêtres planifiées exclues et le détail des événements permet de reproduire le résultat.

### Exercice 6 — Détecter l'effet d'une clôture prématurée

**Question.** Le MTTR baisse, mais le taux de tickets rouverts double et la validation métier est souvent absente. Quel contrôle effectuer avant de publier une conclusion d'amélioration ?

**Corrigé expliqué.** Examiner un échantillon de tickets clos et rouverts, vérifier les horodatages et le critère de rétablissement, comparer le temps de réparation active et le temps de service réellement indisponible, puis documenter les exceptions. Si la mesure ne confirme plus le retour au service, modifier la définition ou renforcer le contrôle de clôture avant de revendiquer une amélioration.

## Défi final — Construire un pilotage KPI fiable

Vous devez présenter au comité de maintenance un tableau de bord trimestriel pour trois familles d'actifs : serveurs de production, équipements réseau et appareils de soutien. Les équipes signalent une baisse du MTTR, une hausse du MTBF et une progression du taux de maintenance préventive. Dans le même temps, la qualité de l'inventaire baisse, les tickets rouverts augmentent et certains changements de formule ne sont pas tracés.

**Travail demandé.**

1. Rédiger un dictionnaire de dix KPI avec définitions, formules, unités, population, sources, propriétaires, fréquences, cibles et limites.
2. Établir un contrôle de qualité des données et expliciter les règles de quarantaine ou de rejet.
3. Calculer MTBF, MTTR et disponibilité sur un jeu d'événements simulés en indiquant les conventions appliquées.
4. Comparer moyenne, médiane et P90 ; segmenter les résultats par famille d'actifs et criticité.
5. Vérifier si les résultats sont comparables au trimestre précédent, notamment au regard des changements de périmètre et de formule.
6. Concevoir une page de tableau de bord exécutif et une vue technique d'investigation.
7. Proposer trois actions mesurables et définir leur test d'efficacité.
8. Préparer une note au comité qui distingue les résultats démontrés, les hypothèses, les limites et les décisions attendues.

**Correction attendue.** Le livrable commence par un dictionnaire versionné et une définition de la population. Les données manquantes, doublons et horodatages incohérents sont traités et quantifiés. Le MTBF utilise un temps de fonctionnement sans double comptage ; le MTTR indique clairement s'il représente réparation active ou rétablissement bout en bout ; la disponibilité suit la formule approuvée. Les résultats sont comparés sur des populations comparables ou affichent les ruptures de série. Le tableau de bord associe KPI, tendance, couverture, segment, seuil et action. Les recommandations ont des responsables, des échéances et des critères de succès vérifiables. La note exécutive ne confond pas corrélation et causalité et expose les limites importantes avant la décision.

## Ressources techniques et références

- [IBM — MTTR : définition et calcul](https://www.ibm.com/think/topics/mttr) : explication du temps moyen de réparation et des étapes qui peuvent influencer la mesure.
- [IBM — MTTR versus MTBF](https://www.ibm.com/think/topics/mttr-vs-mtbf) : différence entre fiabilité, fréquence des défaillances et durée de réparation.
- [IBM — MTBF](https://www.ibm.com/think/topics/mtbf) : calcul sur le temps de fonctionnement et interprétation de la moyenne.
- [IBM — Maintenance KPIs](https://www.ibm.com/think/topics/maintenance-kpis) : vue d'ensemble de KPI de maintenance, des données et du pilotage opérationnel.
- [IBM Cloud Docs — Understanding high availability](https://cloud.ibm.com/docs/resiliency?topic=resiliency-understanding-ha) : relation simplifiée entre MTBF, MTTR et disponibilité dans un modèle de haute disponibilité.

Ces ressources donnent des définitions générales et ne remplacent pas le dictionnaire local, les clauses du SLA ou les consignes de mesure. Avant d'établir une cible, comparer la définition du fournisseur à celle réellement implémentée dans les sources internes.

## Synthèse

Les KPI de maintenance sont des instruments de décision, pas des objectifs autonomes. Le MTBF renseigne sur le temps de fonctionnement entre défaillances retenues ; le MTTR décrit une durée moyenne dont le sens doit être explicitement choisi ; la disponibilité mesure la capacité à rendre un service durant le temps attendu. Leur valeur dépend du périmètre, du temps d'exposition, du comptage des événements, des horodatages et du traitement des exclusions. La gouvernance doit maintenir un dictionnaire versionné, publier la qualité des données, analyser les distributions, détecter les effets pervers et relier chaque seuil à une action. Une amélioration n'est crédible que lorsqu'elle est calculée sur des données comparables, soutenue par des preuves et confirmée par des résultats opérationnels.
