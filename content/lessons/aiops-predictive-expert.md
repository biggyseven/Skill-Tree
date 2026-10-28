# Maintenance prédictive par IA — Expert

> **Mise en contexte :** une entreprise exploite un réseau multisite où certains modules optiques, alimentations, ventilateurs et équipements montrent des signes de dégradation avant la panne. Les interventions réactives sont coûteuses, mais remplacer prématurément des composants sur la base d'un score opaque entraîne aussi des dépenses et des interruptions évitables. La maintenance prédictive consiste à estimer un risque futur à partir de données fiables, puis à planifier une action proportionnée et vérifiable. Les exemples de ce cours reposent sur des données de laboratoire et ne doivent pas être interprétés comme des règles universelles pour un équipement réel.

## Sommaire

1. Objectifs, vocabulaire et périmètre
2. Distinguer surveillance, détection et prédiction
3. Formuler le problème métier
4. Construire un jeu de données exploitable
5. Préparer les séries temporelles et les étiquettes
6. Concevoir les variables explicatives
7. Construire une baseline et choisir un modèle
8. Évaluer les performances sans fuite de données
9. Choisir un seuil selon le coût des erreurs
10. Estimer le temps avant défaillance
11. Intégrer la prédiction dans les opérations
12. Atelier Python et données simulées
13. TP complet et validation de bout en bout
14. Dérive, surveillance et réentraînement
15. Explicabilité, limites et sécurité
16. Dépannage
17. Exercices corrigés
18. Défi final, checklist et références

## 1. Objectifs, vocabulaire et périmètre

La maintenance prédictive cherche à estimer la probabilité qu'un composant ou un service rencontre un événement indésirable dans un horizon défini. Elle diffère de la supervision classique, qui décrit l'état actuel, et de la détection d'anomalies, qui repère un comportement inhabituel sans nécessairement prédire une panne. Le résultat d'un modèle n'est pas une certitude ni un ordre de remplacement. Il s'agit d'une information supplémentaire qui doit être confrontée au contexte, au coût de l'intervention et aux observations de terrain.

À la fin du parcours, vous devez pouvoir traduire un objectif opérationnel en cible de prédiction, analyser la qualité des étiquettes, construire des variables sans utiliser d'information du futur, évaluer des modèles selon les coûts des erreurs, calibrer des scores, suivre les performances après déploiement et expliquer comment une prédiction se transforme en ordre de travail. Vous devez aussi être capable d'expliquer pourquoi un bon score moyen peut être insuffisant si les pannes rares mais critiques sont mal détectées.

Les cas d'usage possibles comprennent la dégradation optique, l'augmentation progressive d'erreurs sur une interface, la saturation régulière d'un équipement, la défaillance d'un ventilateur ou d'une alimentation, ainsi que la dégradation d'un service à travers plusieurs indicateurs. Le choix d'une cible dépend du contexte. Un composant peut afficher une température élevée sans être défectueux ; un événement isolé ne suffit donc pas toujours à créer une étiquette de panne.

### Définitions essentielles

- **Prédiction** : estimation d'un événement futur ou d'un risque sur un horizon explicite.
- **Étiquette** : résultat observé utilisé pour entraîner ou évaluer un modèle.
- **Horizon de prédiction** : période future dans laquelle on souhaite anticiper l'événement.
- **Fenêtre d'observation** : période passée utilisée pour calculer les variables explicatives.
- **Censure** : situation où l'on sait qu'un composant a fonctionné jusqu'à une date, mais où sa durée totale de vie ou sa date de panne n'est pas connue.
- **Fuite de données** : accès involontaire, pendant la préparation ou l'évaluation, à une information qui n'aurait pas été disponible au moment réel de la prédiction.
- **Calibration** : cohérence entre les risques annoncés et la fréquence observée des événements.
- **Dérive** : changement de la distribution des données, de la relation entre les données et la panne, ou des conditions d'exploitation.

## 2. Distinguer surveillance, détection et prédiction

La surveillance mesure un état actuel : disponibilité d'un lien, température d'une optique, utilisation mémoire, erreurs CRC ou délai d'une transaction. La détection d'anomalies identifie un écart par rapport à un modèle de comportement normal. La prédiction estime un risque futur, comme la probabilité qu'un module échoue dans les sept prochains jours. Ces trois fonctions peuvent se combiner, mais elles ne répondent pas à la même question.

~~~mermaid
flowchart LR
  A[Mesures actuelles] --> B[Surveillance]
  A --> C[Détection d'anomalies]
  A --> D[Variables historiques]
  D --> E[Modèle prédictif]
  B --> F[État présent]
  C --> G[Comportement inhabituel]
  E --> H[Risque sur un horizon]
  F --> I[Décision opérationnelle]
  G --> I
  H --> I
  I --> J[Inspection ou intervention]
  J --> K[Résultat réel et retour de terrain]
  K --> D
~~~

Un modèle d'anomalie peut détecter qu'une température sort de la plage habituelle ; il ne prouve pas qu'une panne aura lieu. Un modèle prédictif peut estimer un risque élevé sur plusieurs jours même si la mesure actuelle demeure dans une plage normale. À l'inverse, une panne provoquée par une coupure soudaine peut être impossible à anticiper avec les données disponibles. L'organisation doit donc définir les événements que le système peut raisonnablement prévoir, et conserver une supervision réactive pour ceux qui ne sont pas prédictibles.

### Exemple réseau

Supposons qu'un équipement affiche une augmentation progressive des erreurs de réception, une hausse de température et plusieurs baisses de puissance optique. Chacune de ces mesures peut être peu alarmante isolément. Leur évolution conjointe, si elle est observée sur plusieurs semaines et associée à des pannes passées similaires, peut contribuer à estimer un risque futur. Le modèle ne doit pas conclure automatiquement que le module est à remplacer : il peut recommander une inspection, une comparaison avec l'équipement opposé et un test supplémentaire.

La distinction entre corrélation et causalité est centrale. Une hausse de température peut coïncider avec l'augmentation du trafic, et non avec une dégradation matérielle. Une variable prédictive peut être utile même si elle n'est pas une cause directe, mais son importance doit être comprise et sa stabilité contrôlée. Une variable qui indique indirectement la date d'un ticket de maintenance peut produire un score artificiellement excellent et inutilisable en conditions réelles.

## 3. Formuler le problème métier

Avant de sélectionner un algorithme, écrire une phrase mesurable : « Estimer chaque jour le risque qu'une alimentation réseau tombe en panne dans les quatorze prochains jours afin de planifier une inspection sans dépasser un budget d'interventions. » Cette formulation précise la fréquence de scoring, l'événement, l'horizon et l'utilisation prévue. Elle empêche un projet de se limiter à un objectif vague tel que « utiliser l'IA pour prévoir les pannes ».

### 3.1 Définir l'unité de prédiction

L'unité peut être un équipement par jour, une interface par fenêtre de quinze minutes, un module optique par semaine ou un service par heure. Elle doit être stable entre entraînement, évaluation et production. Si les données sont agrégées par interface pendant l'entraînement, mais par routeur à la mise en service, les scores ne seront pas directement comparables.

Choisir l'unité implique de traiter les dépendances. Plusieurs interfaces d'un même routeur partagent une alimentation, un environnement et parfois une charge. Si elles sont réparties au hasard entre apprentissage et test, le modèle peut apprendre la signature d'un équipement plutôt que des mécanismes généralisables. La séparation doit tenir compte des groupes techniques lorsqu'on veut mesurer la capacité à se généraliser à des équipements jamais vus.

### 3.2 Définir la cible et l'horizon

Une cible possible est un événement confirmé dans un intervalle futur. Par exemple, à la date de scoring t, le label vaut 1 si une panne confirmée survient entre t+1 et t+14 jours ; sinon il vaut 0 seulement si l'observation est suffisamment complète. Si le composant est retiré du réseau au jour 5 pour une raison indépendante, on ne sait pas nécessairement ce qui se serait passé aux jours 6 à 14. Le considérer automatiquement comme un négatif peut introduire un biais.

L'horizon doit correspondre au délai nécessaire pour agir. Une prévision à dix minutes peut être utile pour moduler un trafic ; une prévision à deux semaines peut être utile pour commander une pièce et planifier une intervention. Un horizon trop long rend le lien avec les variables plus incertain. Un horizon trop court peut laisser trop peu de temps pour intervenir.

### 3.3 Définir l'action permise

Le modèle doit être conçu à partir de la décision qu'il soutient. S'il sert à classer les inspections, le rappel des pannes et le coût des inspections sont importants. S'il déclenche un arrêt d'équipement, les exigences de précision, de preuve et de validation humaine seront beaucoup plus fortes. Les seuils et les métriques ne doivent pas être choisis indépendamment du processus opérationnel.

Définissez le propriétaire de la décision, le budget d'inspection, les conditions d'escalade, la procédure de confirmation et le suivi du résultat. Une prédiction sans processus de retour terrain ne produit pas de données fiables pour évaluer la performance future.

## 4. Construire un jeu de données exploitable

La qualité du modèle dépend de la qualité de la relation entre télémétrie et événements terrain. Les sources peuvent inclure les métriques de supervision, les journaux, les configurations, l'inventaire, les dates d'installation, les versions logicielles, les tickets d'incident, les remplacements de matériel et les comptes rendus d'inspection. Chaque source possède sa cadence, sa granularité, son propriétaire et ses défauts.

### 4.1 Contrat de données

Documentez chaque champ : nom, type, unité, équipement concerné, cadence, source, valeur manquante, règle de nettoyage et date de disponibilité réelle. Une température exprimée parfois en degrés Celsius et parfois dans une unité différente ne doit pas être réunie sans normalisation. Le nombre d'erreurs doit être interprété comme un compteur cumulatif ou comme un taux sur une fenêtre ; une baisse du compteur peut résulter d'une remise à zéro, pas d'une guérison du composant.

Les identifiants doivent permettre de relier les mesures au bon équipement même après un remplacement, un changement de nom ou une migration. Un simple nom d'hôte réutilisé à travers le temps peut mélanger deux matériels. Un identifiant immuable d'actif ou une table de correspondance datée est généralement plus approprié.

### 4.2 Construire des étiquettes fiables

Une panne peut être définie par un ticket résolu, un code de défaillance, un remplacement confirmé ou une interruption de service dépassant un seuil. Les tickets sont néanmoins parfois incomplets, et la cause initiale peut être corrigée après investigation. Les étiquettes doivent distinguer panne confirmée, soupçon, maintenance préventive, défaut de collecte et interruption causée par une dépendance externe.

L'équipe doit faire auditer un échantillon des labels par un expert métier et suivre les changements de définition. Si la définition de panne évolue, les résultats d'un modèle entraîné sur l'ancienne définition deviennent difficiles à comparer. Il est souvent utile de conserver la source de l'étiquette, le niveau de confiance et les règles qui ont servi à la produire.

### 4.3 Sélectionner un historique représentatif

La période historique doit contenir une variété raisonnable de charges, de saisons, de versions et d'incidents. Un jeu uniquement constitué des dernières semaines peut être trop homogène. Un jeu trop ancien peut refléter un réseau qui n'existe plus. La période retenue doit être justifiée par les changements opérationnels et par la disponibilité des labels.

Les données de panne sont souvent rares par rapport aux périodes de fonctionnement normal. Il faut conserver les deux classes, mesurer le déséquilibre et choisir des métriques adaptées. Dupliquer artificiellement les rares pannes ne crée pas de nouveaux mécanismes de panne ; les méthodes de rééchantillonnage doivent être appliquées seulement aux données d'entraînement et après une séparation correcte des périodes.

## 5. Préparer les séries temporelles et les étiquettes

La préparation doit reproduire ce qu'un service de prédiction saura réellement calculer à l'instant où il émet un score. Pour chaque date de prédiction, les variables ne doivent utiliser que les informations déjà disponibles. Une statistique calculée sur la fenêtre des sept jours passés est acceptable si tous ses points sont arrivés ; une statistique utilisant les deux jours suivant le score constitue une fuite.

~~~mermaid
flowchart TD
  A[Mesures brutes horodatées] --> B[Contrôle d'intégrité et unités]
  B --> C[Alignement temporel]
  C --> D[Fenêtres d'observation passées]
  D --> E[Variables explicatives]
  E --> F[Étiquette future à horizon défini]
  F --> G[Séparation chronologique]
  G --> H[Entraînement et validation]
  H --> I[Évaluation sur une période ultérieure]
~~~

### 5.1 Valeurs manquantes

Il faut distinguer une mesure naturellement absente d'un défaut de collecte. Une valeur manquante peut avoir une signification opérationnelle, mais elle ne doit pas être traitée automatiquement comme une valeur extrême ou normale. Selon le modèle, on peut exclure certains cas, utiliser une imputation calculée sur les seules données d'entraînement, ajouter un indicateur de manque ou construire un modèle séparé pour les cas de collecte dégradée.

Toute imputation doit être calculée sans regarder la période de test. Par exemple, remplacer les valeurs manquantes par la médiane de l'ensemble des données, test inclus, introduit une information du futur. Les transformations et leurs paramètres doivent être appris sur l'entraînement puis réutilisés à l'identique en validation et en production.

### 5.2 Séparation chronologique

Lorsque l'objectif est de prévoir l'avenir, une séparation aléatoire peut donner une image trop optimiste. Utilisez une période ancienne pour l'entraînement, une période plus récente pour la validation puis une période encore plus récente pour le test final. Il faut veiller à éviter que les fenêtres d'un même incident soient partagées entre plusieurs jeux, ce qui permettrait au modèle de reconnaître presque exactement un cas déjà vu.

Une validation à fenêtres glissantes peut tester si le résultat se répète sur différentes périodes. Le test final ne sert pas à régler le modèle. Si l'équipe regarde ses résultats et modifie plusieurs fois la configuration pour optimiser cette période, le test n'est plus indépendant. Il faudra une nouvelle période ou un protocole externe pour estimer honnêtement les performances.

### 5.3 Événements concurrents et censure

Un matériel peut être remplacé avant sa panne, migré vers un nouveau site ou retiré pour une raison de capacité. L'absence de panne après son retrait ne signifie pas qu'il aurait survécu. Ces observations sont censurées pour une analyse de durée de vie. Selon le problème, elles peuvent être exclues d'une cible binaire, être traitées par une méthode de survie ou être examinées séparément.

Un événement concurrent peut aussi rendre la cause ambiguë : un routeur est remplacé pendant une panne logicielle, ou une intervention de câblage coïncide avec le changement d'une optique. Les règles de labels doivent prévoir ces situations. Une étiquette incertaine peut être gardée pour l'analyse qualitative plutôt que forcée dans une classe binaire.

## 6. Concevoir les variables explicatives

Une variable utile décrit une caractéristique disponible avant la prédiction et liée au phénomène étudié. Les variables peuvent représenter une valeur actuelle, une tendance, une dispersion, un nombre d'événements, une durée depuis un changement ou une relation avec un équipement voisin. Les variables doivent avoir un sens opérationnel et être calculables de façon reproductible.

### 6.1 Valeurs, tendances et variations

Pour un compteur d'erreurs, la valeur brute est parfois moins informative que son augmentation par minute. Pour une température, la moyenne peut être complétée par le maximum, l'écart à une baseline, la pente ou la proportion de mesures au-dessus d'un seuil. Pour les pertes, le quantile élevé peut mieux représenter les dégradations brèves qu'une moyenne globale.

Les variables temporelles exigent une fenêtre précisément définie. La pente d'une mesure calculée sur quatre heures ne décrit pas le même phénomène que la pente sur quatre semaines. Les fenêtres peuvent varier selon la dynamique attendue, mais elles doivent être testées sans fuite. La sélection des fenêtres ne doit pas se limiter à la meilleure performance observée sur le jeu final.

### 6.2 Variables de contexte

Des variables de contexte incluent le modèle d'équipement, l'âge, la version logicielle, la température ambiante, le site, le type de lien, le trafic habituel, la date de maintenance et les relations de voisinage. Ces informations peuvent améliorer le classement, mais elles peuvent aussi créer des biais. Le site peut être un proxy de conditions socio-techniques ou de différences de qualité de collecte. Un modèle performant sur les grands sites peut échouer sur un petit site moins représenté.

Une variable telle que « nombre de tickets ouverts » peut être utile, mais il faut vérifier sa chronologie. Si elle compte les tickets créés après l'incident cible, elle donne au modèle une information future. La date de disponibilité réelle est aussi importante que la date de l'événement.

### 6.3 Éviter la complexité gratuite

Les variables plus nombreuses ne garantissent pas de meilleures prédictions. Une variable coûteuse à collecter, peu stable ou difficile à expliquer augmente la charge de maintenance. Gardez une liste des variables retenues, de leur mode de calcul et de leur dépendance. Supprimez celles qui n'apportent pas de bénéfice démontré ou qui dépendent d'une source peu fiable.

La sélection doit être reproduite dans le pipeline et versionnée. Évitez une étape manuelle différente entre le notebook d'apprentissage et la production. Toute transformation non versionnée ouvre la porte à des écarts silencieux.

## 7. Construire une baseline et choisir un modèle

Une baseline fournit un repère simple. Elle peut utiliser un taux historique par type d'équipement, une règle fondée sur la pente d'un compteur, une régression logistique ou un arbre peu profond. Un modèle complexe ne mérite sa place que s'il améliore significativement la qualité, la robustesse ou la valeur opérationnelle par rapport à ce repère.

### 7.1 Familles de méthodes

- **Règles métier** : faciles à auditer et utiles lorsqu'un seuil physique a une justification établie ; elles peuvent être fragiles face aux combinaisons de signaux.
- **Régression logistique** : baseline interprétable pour une cible binaire ; elle demande de traiter l'échelle des variables et les relations non linéaires.
- **Arbres et forêts** : représentent des interactions non linéaires et acceptent des variables hétérogènes ; leur comportement doit être suivi.
- **Gradient boosting** : souvent efficace sur des tableaux de données structurées ; demande une validation rigoureuse et un contrôle de la complexité.
- **Modèles de survie** : estiment une distribution du temps avant événement et gèrent des cas censurés selon leurs hypothèses.
- **Séries temporelles et réseaux neuronaux** : utiles lorsque la structure temporelle est centrale et que l'historique est assez riche ; le coût d'exploitation peut être supérieur.
- **Modèles hybrides** : combinent un score statistique et des règles de sécurité ou de criticité.

Le modèle doit être choisi d'après la forme et la quantité des données, la fréquence des événements, l'horizon, les contraintes de calcul et la manière dont les opérateurs utiliseront le résultat. Un réseau neuronal n'est pas automatiquement plus adapté qu'une régression si les données ne contiennent que quelques centaines de pannes confirmées.

### 7.2 Baseline reproductible

Une baseline doit être sauvegardée avec ses hypothèses. Par exemple, le risque historique par famille d'équipement peut être calculé sur une période ancienne. Elle doit respecter la séparation chronologique et ne pas utiliser des fréquences calculées sur les données de test. Les performances de cette baseline fournissent un plancher pour les versions ultérieures.

Il faut mesurer le coût total et pas uniquement la qualité statistique. Un modèle légèrement meilleur mais très coûteux à maintenir, difficile à surveiller ou trop lent pour la cadence opérationnelle peut être une mauvaise option. À l'inverse, une amélioration modeste peut être utile si elle réduit les inspections inutiles dans un domaine critique.

## 8. Évaluer les performances sans fuite de données

L'exactitude globale est trompeuse lorsque les pannes sont rares. Si 99 % des périodes ne connaissent pas de panne, un modèle qui prédit toujours « pas de panne » atteint 99 % d'exactitude tout en échouant à signaler les incidents. Les métriques doivent représenter les conséquences des faux positifs et faux négatifs.

### 8.1 Matrice de confusion

| | Panne observée | Pas de panne observée |
|---|---:|---:|
| Panne prédite | Vrai positif | Faux positif |
| Pas de panne prédite | Faux négatif | Vrai négatif |

La précision indique quelle proportion des alertes prédictives correspond à un événement observé. Le rappel indique quelle proportion des événements pertinents a été détectée. Une précision faible entraîne des inspections inutiles ; un rappel faible laisse passer des pannes. Le meilleur compromis dépend du coût des interventions, du délai disponible et de la criticité.

Pour un programme d'inspection, la capacité à classer les équipements peut être plus pertinente qu'une seule décision binaire. Des métriques comme la précision parmi les dix équipements les plus risqués et le nombre de pannes détectées pour un budget fixé permettent de relier le modèle à la planification réelle.

### 8.2 PR-AUC et ROC-AUC

La ROC-AUC mesure la capacité à classer un positif au-dessus d'un négatif sur différents seuils. Lorsque les événements sont très rares, elle peut sembler bonne alors que la proportion d'alertes qui se révèlent utiles est faible. La courbe précision-rappel met davantage l'accent sur la classe positive et est souvent informative pour une maintenance rare. Il faut néanmoins lire la courbe avec le taux de base et le volume d'interventions.

N'utilisez pas une métrique seule. Présentez la précision, le rappel, le nombre absolu de pannes ratées, les fausses alertes, les métriques par équipement et la valeur obtenue à un budget d'inspection réaliste. Les intervalles de confiance et les périodes indépendantes aident à distinguer un gain robuste d'une fluctuation due à quelques événements.

### 8.3 Calibration

Si le modèle annonce un risque de 20 %, on aimerait que, parmi un grand groupe de cas comparables qui reçoivent ce score, environ 20 % connaissent l'événement selon la définition et l'horizon retenus. Cette propriété doit être évaluée sur des données indépendantes. Un classement correct n'implique pas une calibration correcte.

La calibration est importante pour convertir un score en politique opérationnelle, par exemple pour comparer le risque estimé au coût d'une inspection. Si les coûts sont incertains ou si l'événement est rare, les seuils doivent être revus avec les responsables métier et le modèle peut être présenté sous forme de catégories de risque plutôt que de promesses probabilistes trop précises.

### 8.4 Fuites classiques

Les fuites peuvent provenir d'un statut ajouté après la panne, de la résolution d'un ticket, d'un remplacement déjà planifié, de variables calculées avec une fenêtre future, d'une normalisation apprise sur tout le jeu ou d'une séparation aléatoire de fenêtres proches du même incident. Un score très élevé doit déclencher un audit de pipeline avant d'être célébré.

Le test doit correspondre au déploiement prévu. Si le modèle servira sur des équipements nouveaux, réserver certains équipements au test. S'il servira sur des équipements connus dans le futur, une séparation chronologique par équipement peut suffire, sous réserve de l'absence de fuite. Le protocole d'évaluation doit refléter la question que l'entreprise pose réellement.

## 9. Choisir un seuil selon le coût des erreurs

Un seuil de 0,5 n'est pas une règle naturelle. Il peut être trop bas si les inspections sont coûteuses et trop haut si une panne entraîne un impact majeur. La politique doit tenir compte du coût d'une inspection, du coût d'une panne, du délai de préparation d'une intervention, de la criticité de l'équipement et de la capacité de l'équipe.

Un exemple simplifié compare deux coûts. L'action d'inspection a un coût opérationnel stable. L'absence d'inspection a un coût variable si une panne survient et qu'elle n'a pas été anticipée. Le seuil optimal dépend de ces coûts ainsi que de la qualité réelle du modèle. Dans la pratique, les coûts sont rarement connus avec précision ; il faut réaliser une analyse de sensibilité plutôt que d'afficher un seuil unique comme vérité universelle.

La capacité d'intervention crée une contrainte supplémentaire. Même si trente équipements dépassent un seuil, l'équipe ne peut peut-être en inspecter que cinq cette semaine. Le système peut alors classer les risques, expliquer les critères de priorité et laisser les responsables choisir l'ordre en tenant compte des pièces disponibles, des fenêtres d'accès et de la criticité métier.

Une politique acceptable doit définir ce qui arrive lorsque le budget est atteint, lorsque les données sont trop anciennes ou lorsque le score sort de sa plage de calibration. Le système ne doit pas simplement continuer à créer des alertes jusqu'à saturer le centre de supervision.

## 10. Estimer le temps avant défaillance

Une cible binaire « panne dans les quatorze jours » est simple à comprendre, mais elle ne décrit pas tout le temps avant l'événement. Les méthodes de survie peuvent estimer une probabilité de survie au cours du temps et intégrer des observations censurées, sous des hypothèses spécifiques. Elles sont utiles lorsqu'on veut comprendre si le risque augmente avec l'âge ou les conditions d'exploitation.

La durée de vie d'un composant n'est pas toujours une propriété intrinsèque. Les conditions ambiantes, la charge, la qualité de l'alimentation, les cycles thermiques, les mises à jour et les interventions influencent la durée observée. Une prédiction de durée de vie doit donc préciser son contexte et ses limites. Elle ne doit pas être interprétée comme une date exacte à laquelle un composant tombera en panne.

Il faut également distinguer risque relatif et temps de panne. Un classement peut correctement mettre en tête les éléments les plus risqués sans fournir une estimation exacte de leur date de défaillance. Dans certains processus, ce classement est suffisant pour organiser les inspections. Dans d'autres, une prévision de temps restante exige une validation plus forte et un historique plus riche.

## 11. Intégrer la prédiction dans les opérations

Le résultat doit arriver dans un processus concret : tableau de bord, ticket, ordre de maintenance, notification ou planification des pièces. Chaque prédiction doit être liée à une cible, à un horizon, à une date de calcul, à la version du modèle, aux variables disponibles et à une explication qui ne prétend pas dépasser les preuves.

~~~mermaid
flowchart LR
  A[Télémétrie et inventaire] --> B[Pipeline de caractéristiques]
  B --> C[Modèle versionné]
  C --> D[Score et calibration]
  D --> E[Politique de priorité]
  E --> F[Ticket ou inspection]
  F --> G[Résultat terrain vérifié]
  G --> H[Étiquettes et retour d'expérience]
  H --> B
~~~

### 11.1 Transformer le score en action

Le score n'est pas l'action. La politique peut produire les catégories « surveillance renforcée », « inspection recommandée », « revue experte » ou « données insuffisantes ». La classe dépend de l'horizon et du niveau de risque ; elle doit être expliquée aux opérateurs. Évitez de présenter toutes les prédictions comme urgentes, sinon l'équipe les ignore rapidement.

Les tickets générés automatiquement doivent avoir une clé de déduplication afin d'éviter une avalanche de doublons. Ils doivent être mis à jour lorsque le risque change et clôturés lorsque la cause a été traitée. La clôture du ticket doit recueillir un résultat structuré : panne confirmée, défaut trouvé, aucune anomalie observée, matériel remplacé, événement externe ou investigation non concluante.

### 11.2 Human-in-the-loop

L'humain apporte le contexte qui n'est pas toujours présent dans les données : travaux planifiés, contraintes d'accès, évolution du trafic, informations d'un fournisseur ou décision métier. Le système doit donc permettre à un expert de confirmer, de rejeter ou de différer une recommandation, avec un motif documenté. Les désaccords sont des données utiles pour revoir le modèle, mais ils ne doivent pas être automatiquement traités comme une vérité sans validation.

L'approbation humaine ne doit pas devenir un clic machinal. Fournissez une synthèse des signaux, un niveau d'incertitude, le risque de la décision et les vérifications à effectuer. Lorsque la recommandation n'est pas explicable, il peut être préférable de la limiter à un classement et d'exiger une inspection supplémentaire.

## 12. Atelier Python et données simulées

Le code suivant illustre la préparation d'une cible à partir d'une série temporelle synthétique. Il ne contient pas de données de production. L'objectif est de voir comment une variable retardée peut être construite et comment une cible future doit être séparée des variables passées. Il ne constitue pas à lui seul un modèle de maintenance prêt à l'emploi.

~~~python
import pandas as pd
import numpy as np

rng = np.random.default_rng(42)
dates = pd.date_range("2025-01-01", periods=240, freq="D")
temperature = 40 + np.linspace(0, 8, len(dates)) + rng.normal(0, 1.5, len(dates))
errors = np.maximum(0, rng.poisson(lam=np.linspace(1, 4, len(dates))))
df = pd.DataFrame({
    "date": dates,
    "temperature_c": temperature,
    "rx_errors": errors,
})
# Variables bâties exclusivement à partir des jours présents ou passés.
df["temperature_mean_7d"] = df["temperature_c"].rolling(7, min_periods=7).mean()
df["temperature_slope_7d"] = df["temperature_c"].diff(6) / 6
df["errors_sum_7d"] = df["rx_errors"].rolling(7, min_periods=7).sum()

# Exemple de cible simulée : un événement survient après une dérive marquée.
# Cette règle pédagogique ne doit pas être utilisée comme vérité de panne réelle.
event = (
    (df["temperature_c"] > 47) &
    (df["errors_sum_7d"] > df["errors_sum_7d"].quantile(0.85))
).astype("int64")
horizon_days = 7
df["failure_in_next_7d"] = event.shift(-horizon_days)

dataset = df.dropna().copy()
cut1 = int(len(dataset) * 0.60)
cut2 = int(len(dataset) * 0.80)
train = dataset.iloc[:cut1]
validation = dataset.iloc[cut1:cut2]
test = dataset.iloc[cut2:]

print("Train :", train["date"].min(), "->", train["date"].max())
print("Validation :", validation["date"].min(), "->", validation["date"].max())
print("Test :", test["date"].min(), "->", test["date"].max())
print("Événements train :", int(train["failure_in_next_7d"].sum()))
~~~

Dans cet exemple, l'événement est simulé à partir des données afin de pouvoir reproduire le calcul. Dans un projet concret, la cible devrait venir d'un registre de pannes confirmé et horodaté. La règle simulée ne doit pas être utilisée pour évaluer un modèle réel, car elle crée artificiellement le lien entre les variables et l'événement.

### 12.1 Vérifications complémentaires

Avant d'entraîner un modèle, vérifier que les dates sont uniques au niveau de granularité choisi, que les unités sont cohérentes, que les variables n'utilisent pas d'information future et que les étiquettes sont disponibles sur l'horizon entier. Contrôlez la distribution par classe pour chaque période. Si le jeu de test ne contient aucune panne, certaines métriques seront impossibles à interpréter.

Les paramètres de nettoyage et d'imputation doivent être appris uniquement sur train. Les hyperparamètres doivent être choisis avec train et validation. Le test final ne sert qu'à une évaluation indépendante après gel de la configuration. Une fois les résultats connus, vous pouvez documenter les limites et préparer un nouveau test dans une période future, plutôt que d'ajuster sans fin le modèle sur le même jeu.

## 13. TP complet et validation de bout en bout

### Scénario

Le service d'exploitation suit 600 interfaces et plusieurs centaines de composants optiques. Les données remontent toutes les cinq minutes. L'équipe souhaite classer les composants à inspecter pendant les deux semaines à venir. Les pannes sont rares, les interventions sont coûteuses et le remplacement préventif est possible, mais il existe un risque de déclencher des travaux inutiles.

### Étape 1 — Formuler la cible

Définissez l'unité de prédiction comme « composant par jour de scoring », avec un horizon de quatorze jours. Une cible positive représente une défaillance confirmée pendant cet horizon. Excluez ou traitez séparément les cas où le composant a été retiré pour une raison indépendante avant la fin de l'horizon. Écrivez la définition de label et faites-la valider par les experts matériels.

### Étape 2 — Préparer les données

Rassemblez les données de télémétrie, les événements, les dates d'installation et les interventions. Vérifiez l'identité des composants à travers les remplacements. Contrôlez les unités et les changements de fréquence de collecte. Créez des variables à partir des fenêtres antérieures à la date de scoring : tendances, maxima, variabilité, erreurs cumulées et nombre de redémarrages déjà observés.

### Étape 3 — Établir un protocole de test

Séparez les données chronologiquement et protégez les fenêtres d'un même incident contre le mélange entre train et test. Faites une baseline simple. Mesurez les résultats selon le nombre d'inspections disponible par semaine et selon le type de matériel. Examinez manuellement les faux positifs et faux négatifs, particulièrement sur les équipements critiques.

### Étape 4 — Construire la politique opérationnelle

Un risque élevé génère une inspection recommandée, pas une mise hors service automatique. Les cas sans télémétrie fraîche apparaissent comme « données insuffisantes ». Les composants sous maintenance planifiée sont traités selon une règle spécifique. Les alertes répétées sur un même composant sont dédupliquées. L'équipe valide l'ordre de priorité en tenant compte des pièces, de l'accès au site et des fenêtres d'intervention.

### Étape 5 — Évaluer le résultat de terrain

Après l'inspection, consignez le constat, le composant éventuellement remplacé et la confirmation de la panne. La simple décision de remplacer n'est pas une preuve qu'une panne se serait produite. Les résultats incertains doivent rester distincts des vrais positifs, et le protocole doit éviter de considérer automatiquement chaque remplacement préventif comme un succès prédictif.

### Livrables attendus

- une définition versionnée de l'événement prédit et de l'horizon ;
- un dictionnaire de données et des règles de qualité ;
- un pipeline reproductible de caractéristiques ;
- une baseline et au moins un modèle candidat ;
- un rapport d'évaluation temporelle ;
- une politique de priorité et un canal de retour terrain ;
- un tableau de bord de calibration, de dérive et de qualité des labels ;
- une procédure d'arrêt si la qualité du modèle se dégrade.

## 14. Dérive, surveillance et réentraînement

Après déploiement, les données peuvent évoluer parce que le réseau change, que le trafic s'accroît, que les composants sont remplacés ou que les collecteurs changent de version. La relation entre indicateurs et panne peut aussi changer. Il faut suivre la dérive des données et la performance sur les événements réellement observés.

### 14.1 Types de dérive

La dérive de données se produit lorsque la distribution des variables change. La dérive de concept se produit lorsque la relation entre les variables et la cible évolue. Un changement de version peut modifier les valeurs remontées sans changer le comportement réel. Une campagne de remplacement préventif peut réduire le nombre de pannes observées et compliquer l'évaluation. Ces phénomènes demandent des réponses différentes.

Les alertes de dérive doivent conduire à une investigation, pas à un réentraînement aveugle. Vérifiez d'abord si les données ont changé de sens, d'unité, de cadence ou de source. Si un collecteur a cessé de remonter une métrique, le modèle n'a pas besoin d'un nouvel apprentissage ; il faut réparer le pipeline ou retirer temporairement la fonction concernée.

### 14.2 Réentraînement gouverné

Le réentraînement doit suivre une version de données, une définition de cible, un code et une configuration du modèle. Il doit être reproductible et comparer le candidat au modèle courant sur les mêmes périodes de référence, puis sur une période ultérieure indépendante. La nouvelle version ne remplace pas automatiquement celle en production : elle doit satisfaire des seuils d'acceptation définis à l'avance.

Un modèle peut améliorer un score global tout en régressant sur un site ou une famille de composants. La revue doit analyser les segments pertinents et l'impact opérationnel. Prévoir un mécanisme de retour à la version précédente et conserver les artefacts nécessaires à la reproduction d'une prédiction passée.

### 14.3 Surveiller l'utilité réelle

Les métriques de modèle doivent être reliées aux résultats de maintenance : nombre de pannes anticipées, inspections sans défaut trouvé, délai entre alerte et panne, disponibilité des pièces et récurrence après intervention. Les modèles peuvent changer la façon dont les personnes interviennent, ce qui affecte les données observées. Par exemple, une intervention préventive peut empêcher l'événement qui aurait servi à confirmer la prédiction. Il faut donc distinguer la qualité de la prédiction et l'effet de l'action préventive.

## 15. Explicabilité, limites et sécurité

Une explication utile présente les facteurs qui ont contribué au score, leur période et leur fiabilité. Elle ne doit pas affirmer une causalité que le modèle n'a pas établie. Une explication locale peut aider à examiner une décision, mais les méthodes d'explicabilité ont elles-mêmes des limites et peuvent être instables si les données changent légèrement.

L'équipe doit documenter les domaines où le modèle a été évalué, les familles matérielles peu représentées, les niveaux de confiance et les cas qui imposent une revue humaine. Un score ne doit pas servir à attribuer automatiquement une faute à une personne ou à un prestataire sans preuves indépendantes. Le but est d'améliorer la planification technique, pas d'automatiser une décision punitive.

Les données d'infrastructure peuvent révéler des noms de clients, des adresses, des identifiants, des habitudes de trafic ou des éléments de topologie sensibles. Contrôlez les accès, minimisez les données collectées, appliquez les durées de conservation et protégez les exports d'entraînement. Un jeu de données pseudonymisé reste potentiellement sensible si les identifiants peuvent être reliés à d'autres sources.

La sécurité du pipeline couvre les dépendances logicielles, l'intégrité des données, les droits sur le registre de modèles, la validation des artefacts, l'authentification des services et la protection du processus de déploiement. Un modèle ou un fichier de transformation modifié par un acteur non autorisé peut produire des recommandations erronées. Les artefacts doivent être versionnés, audités et promus par un mécanisme contrôlé.

## 16. Dépannage

### Le modèle annonce un risque élevé pour presque tous les équipements

Vérifiez le taux de base, la calibration, le seuil, les unités et la disponibilité des variables. Une nouvelle version de télémétrie peut avoir décalé toutes les valeurs. Examinez les distributions train et production, puis les taux d'alertes par famille. Ne baissez pas simplement les scores ni ne changez le seuil sans comprendre la cause.

### Le modèle ne détecte aucune panne

Vérifiez les labels, les dates, l'horizon et le déséquilibre. Un mauvais décalage temporel peut produire des étiquettes presque toutes négatives. Vérifiez que les variables prédisent un événement futur plutôt que l'état qui suit une intervention. Analysez les faux négatifs individuellement pour déterminer s'ils étaient prédictibles avec les données disponibles.

### L'évaluation est excellente mais la production échoue

Recherchez la fuite de données, une séparation aléatoire inadéquate, les équipements partagés entre train et test, des transformations qui ont utilisé tout le dataset ou une source indisponible en production. Reproduisez exactement le pipeline d'inférence et comparez chaque variable d'un exemple connu.

### La qualité baisse après une mise à jour d'équipement

Une mise à jour peut changer la sémantique, la granularité ou la distribution d'une mesure. Vérifiez la documentation du collecteur et comparez un échantillon avant-après. Si la mesure n'est plus comparable, marquez les périodes et réévaluez le modèle. Ne réentraînez pas sur des valeurs qui n'ont plus le même sens.

### Les équipes ignorent les prédictions

Le problème peut provenir d'un trop grand nombre d'alertes, d'explications insuffisantes, d'un manque de confiance dans les labels ou d'une absence de procédure d'action. Mesurez l'utilité des recommandations et organisez une revue avec les utilisateurs. La solution peut être de réduire le périmètre, d'améliorer la déduplication ou de changer l'interface plutôt que de complexifier le modèle.

## 17. Exercices corrigés

### Exercice 1 — Définition de la cible

Une équipe veut « prévoir les pannes » sans préciser de composant, d'horizon ou de type d'événement. Que manque-t-il ?

**Correction :** l'unité de prédiction, l'événement exact, l'horizon, la fréquence du scoring, la source de vérité et l'action métier soutenue. Sans ces éléments, la cible varie entre opérateurs et les performances ne sont pas comparables.

### Exercice 2 — Fuite de données

Un modèle utilise le statut d'un ticket, mis à jour après remplacement de la pièce, et annonce une excellente capacité prédictive.

**Correction :** le statut est indisponible au moment où le score est émis et contient indirectement le résultat de l'événement. Il doit être retiré ou reconstruit à partir de l'état réellement disponible à la date de scoring. Refaire la séparation chronologique et l'évaluation indépendante.

### Exercice 3 — Choix d'une métrique

Les pannes représentent moins de 1 % des observations. Le modèle atteint une exactitude de 99,2 %, mais n'identifie aucune panne.

**Correction :** l'exactitude est dominée par les négatifs. Il faut examiner le rappel, la précision-rappel, le nombre de pannes ratées et la valeur à budget d'inspection fixe. Une baseline qui prédit toujours « aucune panne » doit être présentée comme contre-exemple.

### Exercice 4 — Remplacement préventif

Un composant à risque élevé est remplacé et aucune panne ne survient ensuite. Peut-on compter ce cas comme un vrai positif confirmé ?

**Correction :** pas automatiquement. L'intervention a empêché l'observation du résultat contrefactuel. Le cas doit être classé selon une règle explicitement définie et éventuellement analysé comme censuré. Le succès de l'intervention et la justesse de la prédiction sont deux questions différentes.

### Exercice 5 — Dérive

Les scores augmentent sur tous les sites juste après un changement de collecteur.

**Correction :** commencer par vérifier les unités, les noms de champs, la cadence et les transformations du pipeline. Cette coïncidence est compatible avec une dérive de données causée par la collecte, mais elle doit être vérifiée. Un réentraînement ne corrigera pas une mesure dont le sens a changé.

## 18. Défi final corrigé, checklist et références

### Défi

Concevez un système de priorité d'inspection pour des modules optiques. Le système reçoit température, puissance reçue, erreurs de réception, âge du composant, historique des alarmes et tickets de maintenance. Les événements sont rares et le matériel de certains sites est sous-représenté. Vous devez proposer une cible, une validation, des métriques, un flux opérationnel et une gouvernance du modèle.

### Correction proposée

La cible peut être une défaillance matérielle confirmée dans les quatorze jours après le score, calculée au niveau du composant et à une heure définie. Les cas retirés pour migration, les maintenances préventives et les pannes externes sont marqués séparément pour ne pas créer de négatifs artificiels. Les variables utilisent seulement les données disponibles à la date du score ; les caractéristiques de tendance sont calculées sur des fenêtres passées.

La validation est chronologique, avec un jeu de test final plus récent que les données d'entraînement. Des équipements entiers peuvent être réservés au test si la cible comprend de nouveaux modèles matériels ou de nouveaux sites. La baseline utilise le taux historique par famille ou une règle simple documentée. Les candidats sont comparés avec précision-rappel, rappel à un budget d'inspection, précision parmi les premières recommandations et taux de pannes ratées. Les résultats sont découpés par site et type de matériel.

En exploitation, le score produit un rang et une justification, pas une commande de remplacement. La politique tient compte du stock de pièces, des fenêtres d'accès, du risque de panne et de la criticité. Les alertes sont regroupées par composant. L'équipe documente l'inspection et la confirmation terrain, en distinguant panne confirmée, anomalie sans panne et cas incertain.

Le modèle est enregistré avec la version des données, le code, les paramètres et les métriques. Les alertes de dérive déclenchent d'abord une vérification du pipeline. Un candidat est entraîné et évalué hors production, puis comparé au modèle courant avant toute promotion. Un retour à la version précédente est prévu et testé.

### Checklist de production

- [ ] Unité, cible, horizon et fréquence de prédiction définis.
- [ ] Étiquettes vérifiées par des experts et cas incertains distingués.
- [ ] Données et unités documentées, avec règles de fraîcheur et de qualité.
- [ ] Fenêtres calculées uniquement sur les informations passées.
- [ ] Séparation chronologique sans fuite entre incidents.
- [ ] Baseline simple et modèle candidat comparés.
- [ ] Précision, rappel, métriques au budget d'intervention et erreurs graves suivis.
- [ ] Calibration évaluée avant d'interpréter les scores comme des risques.
- [ ] Résultats ventilés par site, type de matériel et criticité.
- [ ] Décision opérationnelle approuvée par les responsables concernés.
- [ ] Retour terrain structuré et étiquettes versionnées.
- [ ] Dérive de données et de performance surveillées.
- [ ] Réentraînement, validation, promotion et rollback documentés.
- [ ] Accès aux données et aux modèles limités et audités.

### Références

- Scikit-learn, évaluation des modèles : https://scikit-learn.org/stable/modules/model_evaluation.html
- Scikit-learn, prévention des fuites de données : https://scikit-learn.org/stable/common_pitfalls.html
- NIST, AI Risk Management Framework : https://www.nist.gov/itl/ai-risk-management-framework
- Pandas, documentation : https://pandas.pydata.org/docs/
- Google, Rules of Machine Learning : https://developers.google.com/machine-learning/guides/rules-of-ml

Le principe à retenir est que la valeur d'une maintenance prédictive ne se résume pas à une métrique de modèle. Elle dépend d'une cible définie, de données temporelles correctes, de métriques alignées sur les coûts, d'une intervention réaliste et d'une confirmation des résultats sur le terrain.