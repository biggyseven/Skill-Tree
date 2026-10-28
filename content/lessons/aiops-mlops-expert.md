# MLOps pour l'infrastructure — Expert

> **Mise en contexte :** une équipe a développé un modèle qui repère les risques d'incident dans les métriques réseau. Le prototype fonctionne dans un notebook, mais les résultats changent selon la machine, les dépendances et les données chargées. Après une mise à jour du collecteur, le score se dégrade et personne ne sait si le modèle, le pipeline ou les données sont responsables. Le MLOps apporte des pratiques d'ingénierie pour construire, versionner, tester, déployer et surveiller des systèmes de machine learning sur la durée. L'objectif est la reproductibilité et la maîtrise du risque, non l'automatisation aveugle des déploiements.

## Sommaire

1. Objectifs et périmètre du MLOps
2. Cycle de vie d'un modèle opérationnel
3. Architecture de référence
4. Données, contrats et lignage
5. Versionnement et reproductibilité
6. Construire un pipeline d'entraînement
7. Tests de données, de modèles et de sécurité
8. Registre et promotion des modèles
9. CI/CD et déploiement contrôlé
10. Inférence, latence et disponibilité
11. Observabilité, dérive et qualité
12. Incident, rollback et réponse à une régression
13. Atelier Python et manifeste d'artefact
14. TP : industrialiser un modèle de supervision
15. Gouvernance, accès et coûts
16. Dépannage
17. Exercices corrigés
18. Défi final, checklist et références

## 1. Objectifs et périmètre du MLOps

Le MLOps applique l'ingénierie logicielle, l'automatisation des déploiements et la gestion des données au cycle de vie des modèles. Dans une infrastructure réseau, le modèle peut détecter des anomalies, prévoir des pannes, classer des incidents, aider à prioriser des inspections ou enrichir un diagnostic. Une fois en production, le système doit gérer les mises à jour de données, les changements de topologie, les dépendances logicielles, la disponibilité du service d'inférence et l'évolution des résultats.

Un prototype est souvent évalué sur un jeu de données fixe. Un système exploité doit fonctionner avec des entrées réelles, fournir un résultat dans un délai défini, signaler une entrée invalide, garder sa provenance et pouvoir être arrêté ou restauré. La performance dépend donc du pipeline complet : collecte, préparation, entraînement, évaluation, packaging, registre, déploiement, inférence, surveillance et retour terrain.

À la fin du cours, vous devez pouvoir concevoir une chaîne reproductible, versionner les données et les paramètres, automatiser les tests, définir des critères de promotion, surveiller la qualité en production, détecter une dérive, effectuer un rollback et expliquer les contrôles de sécurité. Vous devez également pouvoir justifier pourquoi chaque composant existe et quel problème il résout.

### Vocabulaire

- **Artefact** : fichier ou objet versionné produit par un pipeline, par exemple un modèle ou un rapport.
- **Lignage** : historique reliant données, code, paramètres, environnement, modèle et résultats.
- **Registre de modèles** : catalogue des versions, métadonnées et statuts des modèles.
- **CI** : intégration continue, qui exécute automatiquement des contrôles sur les changements.
- **CD** : livraison ou déploiement continu, qui prépare ou promeut des versions selon des règles.
- **Feature pipeline** : code qui transforme les données brutes en variables d'entrée du modèle.
- **Dérive de données** : évolution des entrées par rapport à la référence.
- **Dérive de concept** : changement de la relation entre variables et résultats.
- **Rollback** : retour contrôlé à une version précédente.
- **Reproductibilité** : possibilité de réexécuter le pipeline et de retrouver des résultats cohérents à partir des mêmes entrées, du même code et du même environnement.

## 2. Cycle de vie d'un modèle opérationnel

Le cycle de vie commence par un besoin métier mesurable. L'équipe définit le problème, les entrées, la cible, les utilisateurs, les conséquences d'une erreur et le délai disponible pour agir. Elle construit ensuite un dataset traçable, une baseline, un modèle candidat et une évaluation indépendante. Un modèle n'est publié que s'il satisfait des critères définis à l'avance et si les consommateurs savent comment utiliser son résultat.

~~~mermaid
flowchart TD
  A[Besoin opérationnel] --> B[Contrat de données et cible]
  B --> C[Ingestion et validation]
  C --> D[Préparation reproductible]
  D --> E[Entraînement et évaluation]
  E --> F{Critères remplis ?}
  F -->|Non| G[Analyse et nouvel essai]
  G --> D
  F -->|Oui| H[Registre et revue]
  H --> I[Déploiement progressif]
  I --> J[Inférence et observabilité]
  J --> K[Retour terrain et dérive]
  K --> L{Revue nécessaire ?}
  L -->|Oui| C
  L -->|Non| J
~~~

Une chaîne peut être techniquement automatisée tout en conservant des étapes d'approbation. La promotion d'un modèle qui influencera un réseau critique ne devrait pas être déclenchée uniquement par le fait qu'un pipeline s'est terminé avec le code de retour zéro. Le pipeline doit attester les critères statistiques, techniques et opérationnels.

### 2.1 Séparer les responsabilités

Le propriétaire métier définit le résultat opérationnel. L'équipe de données assure la qualité des mesures et des labels. L'équipe ML conçoit les variables, les modèles et l'évaluation. L'équipe plateforme fournit l'environnement, le registre, les déploiements et l'observabilité. L'équipe réseau valide que les recommandations ont un sens dans la topologie et les procédures. Une même petite équipe peut assumer plusieurs rôles, mais les responsabilités doivent être documentées.

La séparation évite de confier à un modèle la responsabilité d'une décision qui relève d'un propriétaire de service. Elle permet aussi de décider qui doit être alerté lorsque la qualité baisse ou lorsque les données ne sont plus disponibles.

### 2.2 Le notebook n'est pas une plateforme

Un notebook facilite l'exploration et les essais. Il devient fragile comme mécanisme de production s'il dépend d'un état en mémoire, d'un ordre d'exécution manuel ou d'une version implicite d'une bibliothèque. Le passage en pipeline exige de convertir les transformations en fonctions testables, d'expliciter les paramètres, de conserver les entrées et de décrire l'environnement.

Les sorties doivent être structurées : métriques, paramètres, schéma de données, erreurs, version de code et identifiant d'expérience. Un simple graphique dans un notebook ne suffit pas à justifier la promotion d'un modèle. Les résultats importants doivent pouvoir être comparés automatiquement et audités après coup.

## 3. Architecture de référence

Une architecture minimale comprend un stockage de données, un pipeline de préparation, un moteur d'entraînement, un système d'évaluation, un registre d'artefacts, un processus de déploiement et une chaîne de surveillance. Le nombre de services dépend du volume et des contraintes. Il est préférable de démarrer avec une architecture simple mais traçable plutôt que d'ajouter des composants qui n'ont pas de besoin identifié.

### 3.1 Environnement de développement

L'environnement de développement doit permettre d'explorer les données et de tester les fonctions avec un échantillon. Il ne doit pas avoir automatiquement les mêmes droits que la production. Les données sensibles peuvent être remplacées par un jeu anonymisé ou synthétique. Les secrets de production ne doivent pas être copiés dans les notebooks.

### 3.2 Entraînement et validation

Le pipeline d'entraînement reçoit des entrées identifiées, vérifie le schéma, prépare les variables, entraîne le modèle et génère un rapport d'évaluation. Chaque étape doit échouer explicitement si les préconditions ne sont pas satisfaites. Une entrée vide, une variable obligatoire absente ou une période sans événement ne doit pas produire un modèle trompeur marqué comme valide.

Le pipeline doit aussi pouvoir être exécuté sans accès aux systèmes opérationnels lorsqu'il n'en a pas besoin. Cette séparation diminue le risque que l'entraînement modifie accidentellement le réseau ou dépende de services en production.

### 3.3 Registre et inférence

Le registre conserve les artefacts, les métadonnées, les rapports et le statut de chaque version. Le service d'inférence charge une version approuvée, vérifie les données entrantes et renvoie une réponse conforme au contrat. Il doit identifier la version utilisée pour chaque score afin de permettre l'explication d'une décision passée.

L'inférence peut être intégrée à un collecteur, exposée par API, exécutée périodiquement ou consommée dans un flux. Le choix dépend de la latence, du volume, de la disponibilité et du coût. L'architecture doit prévoir le mode dégradé si le service ML est indisponible.

## 4. Données, contrats et lignage

Un contrat de données définit le schéma, les unités, les valeurs permises, les champs obligatoires, les règles de fraîcheur, la signification des valeurs manquantes et le propriétaire. Toute modification du contrat doit être traitée comme un changement logiciel. Un champ qui change de type ou de signification peut invalider un modèle sans produire d'erreur de parsing.

### 4.1 Contrôles de données

Les validations courantes incluent :
- présence des champs obligatoires ;
- types corrects et unités connues ;
- plages de valeurs plausibles ;
- absence de doublons d'identité au niveau prévu ;
- horodatages valides et retard de collecte acceptable ;
- taux de données manquantes sous des seuils définis ;
- distribution comparée à une référence ;
- vérification de l'intégrité des labels et de la fenêtre temporelle.

Les contrôles doivent produire un résultat exploitable : succès, avertissement ou échec bloquant. Une anomalie de qualité mineure peut conduire à une revue ; une absence de variable déterminante doit empêcher la promotion ou l'inférence concernée. L'équipe doit expliquer pourquoi un contrôle est bloquant et quel processus permet de le corriger.

### 4.2 Lignage complet

Un score ou un modèle devrait pouvoir être relié à la version des données, au code, aux paramètres, aux dépendances, à l'environnement et aux métriques. Sans lignage, deux artefacts dont les noms se ressemblent peuvent être impossibles à distinguer. Les noms datés sont utiles, mais ils ne remplacent pas des identifiants stables, des empreintes et des métadonnées.

Le lignage sert au débogage, à la conformité, à l'analyse post-incident et au retour arrière. Si un modèle produit une prédiction inattendue, il permet de déterminer quelle version et quel jeu de caractéristiques ont été utilisés au lieu de reconstruire les hypothèses à partir de souvenirs d'équipe.

### 4.3 Données sensibles et rétention

Les métriques d'infrastructure peuvent contenir des identifiants d'actifs, des adresses IP, des noms de services et des informations d'exploitation. Les journaux peuvent inclure des identifiants et des données applicatives. Il faut minimiser les informations nécessaires, contrôler les accès, chiffrer les stockages adaptés et définir des durées de rétention. Les environnements de développement ne doivent pas devenir une copie permanente de toutes les données opérationnelles.

## 5. Versionnement et reproductibilité

Les quatre éléments essentiels sont le code, les données, les paramètres et l'environnement logiciel. Les versions de modèles doivent être immuables après promotion ; une version corrigée reçoit un nouvel identifiant. Le versionnement ne consiste pas uniquement à nommer un fichier model-final-v2. Il doit permettre de vérifier que l'artefact chargé correspond bien à celui qui a été évalué et approuvé.

### 5.1 Code et données

Le code de préparation doit être versionné comme le code du modèle. Une modification de calcul d'une moyenne glissante peut changer tous les scores. Les datasets peuvent être stockés avec des versions ou des identifiants d'instantanés. Si les données ne peuvent pas être conservées pour des raisons de sécurité, les métadonnées, les empreintes et les jeux de test synthétiques peuvent aider à démontrer la reproductibilité.

### 5.2 Environnement logiciel

Les versions de Python, des bibliothèques et des outils doivent être fixées et mises à jour selon une procédure. Une dépendance flottante peut installer une version différente lors d'une exécution ultérieure. Utilisez un environnement isolé, un fichier de dépendances ou un conteneur construit de façon reproductible, puis faites analyser les dépendances selon les politiques de sécurité de l'organisation.

Une reproductibilité parfaite peut être difficile pour certaines opérations GPU ou certains algorithmes stochastiques. Dans ce cas, documentez les graines, les tolérances et les limites, puis définissez ce qui constitue un résultat reproductible pour l'usage concerné.

### 5.3 Manifeste d'artefact

Un manifeste peut enregistrer le nom du modèle, l'identifiant de version, l'empreinte de l'artefact, le commit de code, l'identifiant des données, les paramètres, les versions de dépendances, les métriques et la date de création. Les métadonnées ne doivent pas intégrer des secrets ou des données sensibles inutiles.

~~~json
{
  "model_name": "network-anomaly-ranker",
  "model_version": "1.4.0",
  "code_revision": "example-commit-sha",
  "dataset_version": "telemetry-snapshot-2026-09",
  "feature_schema": "v3",
  "metrics": {
    "precision_at_k": 0.82,
    "recall": 0.76
  },
  "approval_status": "candidate"
}
~~~

Les valeurs ci-dessus sont entièrement illustratives. Elles ne représentent pas une performance attendue ou mesurée. En production, les métriques doivent provenir du rapport d'évaluation et être reliées au protocole qui a produit le jeu de test.

## 6. Construire un pipeline d'entraînement

Un pipeline permet d'exécuter des étapes dans un ordre connu, d'enregistrer leurs entrées et sorties et de les réessayer sans devoir reconstruire manuellement l'état d'un notebook. Il peut être orchestré par un outil dédié ou un script simple si le volume est faible. L'outil ne résout pas la qualité du processus : celle-ci vient des contrats, des tests et de la traçabilité.

### 6.1 Les étapes essentielles

1. Charger une version de données déterminée.
2. Valider le schéma et les règles de qualité.
3. Construire les variables par une fonction versionnée.
4. Créer les séparations d'entraînement, validation et test.
5. Entraîner une baseline et un ou plusieurs candidats.
6. Calculer les métriques préalablement choisies.
7. Évaluer les segments et les cas limites.
8. Écrire modèle, rapport, manifeste et journaux.
9. Soumettre le candidat à une revue ou à un critère automatique de promotion.

Les étapes doivent être idempotentes lorsque possible. Réexécuter le pipeline sur les mêmes entrées ne doit pas écraser silencieusement le modèle approuvé. Les sorties sont nommées ou stockées par identifiant de run afin de préserver les essais antérieurs.

### 6.2 Paramètres et configuration

Les paramètres doivent être explicites et validés. Une plage invalide, un horizon négatif ou une taille de fenêtre nulle doit entraîner un échec clair. Les valeurs par défaut doivent être documentées et versionnées. Évitez d'intégrer en dur des chemins locaux ou des secrets dans le code d'apprentissage.

La configuration d'environnement peut varier, mais les écarts doivent être déclarés. Un endpoint de collecte de production ne doit pas être utilisé par erreur lors des tests. Un mode de simulation ou un dataset synthétique est utile pour automatiser les tests sans mettre en danger l'infrastructure.

### 6.3 Baseline et reproductibilité

Le pipeline doit entraîner une baseline simple, car elle permet d'évaluer le gain réel du modèle candidat. Une version plus sophistiquée ne doit être promue que si elle satisfait des critères métier et techniques. La baseline demeure utile comme solution de repli si la qualité du candidat baisse ou si ses dépendances deviennent indisponibles.

## 7. Tests de données, de modèles et de sécurité

La qualité de production repose sur une pyramide de tests. Les tests unitaires vérifient les fonctions de transformation. Les tests de données valident le schéma et les valeurs. Les tests de modèle vérifient les métriques et les comportements attendus sur des cas de référence. Les tests d'intégration valident le contrat d'inférence. Les tests de déploiement vérifient le chargement et le retour arrière.

### 7.1 Tests unitaires de caractéristiques

Pour une caractéristique de taux d'erreur, tester les valeurs normales, zéro, des compteurs qui diminuent après remise à zéro, les valeurs manquantes et les divisions par zéro. Vérifier que les unités et l'ordre temporel sont corrects. Les tests doivent couvrir les cas que les données réelles ont révélés comme source d'erreurs.

### 7.2 Tests de modèle

Les tests peuvent vérifier que les métriques restent au-dessus d'un minimum de référence, que le modèle répond au format contractuel, qu'il ne produit pas de NaN ou d'infini, qu'il gère les valeurs limites et que les cas critiques font l'objet d'un comportement prévu. Le seuil d'acceptation doit être justifié par le coût des erreurs, et pas choisi après avoir vu le résultat du candidat.

Un test de performance ne suffit pas. Le candidat doit être comparé à la version en production sur un même jeu de référence et sur une période plus récente. Toute amélioration doit être segmentée pour éviter qu'un gain global masque une régression sur un site critique.

### 7.3 Tests de sécurité et d'intégrité

Le pipeline doit contrôler les droits d'écriture dans le stockage d'artefacts, valider les fichiers d'entrée, empêcher l'exécution de code provenant d'une source non approuvée et limiter les secrets accessibles. Les modèles sérialisés peuvent être dangereux si leur format permet l'exécution de code lors du chargement ; le choix du format et la provenance de l'artefact doivent être évalués selon la bibliothèque utilisée.

L'analyse des dépendances, les contrôles d'accès, la signature ou l'empreinte des artefacts et la protection du pipeline CI sont des mesures importantes. Un acteur qui peut remplacer un modèle approuvé ou modifier le seuil de promotion peut changer le comportement du système sans modifier le code principal.

## 8. Registre et promotion des modèles

Le registre organise les versions selon leur état : expérimentation, candidat, validé, en production, retiré ou interdit. Il conserve les rapports qui permettent de comprendre la décision de promotion. Un registre n'est pas simplement un répertoire de fichiers ; il est un point de contrôle entre l'expérimentation et l'exploitation.

### 8.1 Critères de promotion

Un candidat peut être promu si le jeu de test est indépendant, les métriques principales atteignent le seuil, la qualité par segment est acceptable, le contrat d'entrée et de sortie est valide, les contrôles de sécurité passent et le rollback a été éprouvé. Les critères sont fixés avant l'évaluation. Modifier les seuils après avoir vu que le candidat échoue rend la validation moins crédible.

### 8.2 Version courante et version candidate

En mode champion-challenger, le modèle courant reste responsable de la production et un candidat est évalué séparément. On peut comparer les prédictions en mode fantôme, puis déployer le candidat sur une petite part du trafic si le contexte le permet. La stratégie doit définir comment mesurer les cas où le résultat réel n'est disponible que plusieurs jours après la prédiction.

### 8.3 Retrait d'une version

Le retrait doit empêcher de nouvelles inférences sans détruire les preuves nécessaires à l'audit. Il faut conserver le lien entre une prédiction et la version qui l'a produite. Si une version présente un défaut de sécurité ou de qualité, marquer clairement son statut et déclencher l'alerte appropriée.

## 9. CI/CD et déploiement contrôlé

L'intégration continue automatise les tests de code, de données et de contrat à chaque changement pertinent. Le déploiement continu prépare une version et la promeut selon les critères définis. Dans un environnement sensible, la livraison peut être automatique alors que la mise en production reste soumise à une approbation explicite.

~~~mermaid
flowchart LR
  A[Pull request] --> B[Lint et tests unitaires]
  B --> C[Validation du dataset]
  C --> D[Entraînement et évaluation]
  D --> E{Gates qualité}
  E -->|Échec| F[Rapport de rejet]
  E -->|Succès| G[Artefact candidat signé ou vérifié]
  G --> H[Registre]
  H --> I[Mode fantôme]
  I --> J[Revue et approbation]
  J --> K[Déploiement progressif]
  K --> L[Monitoring et rollback si nécessaire]
~~~

### 9.1 Exemple de pipeline déclaratif

Le pipeline concret dépend de l'hébergeur CI. Un workflow générique peut exécuter les étapes suivantes, sans supposer un accès au réseau de production :

~~~yaml
name: model-quality
on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -r requirements.txt
      - run: python -m compileall -q src
      - run: python -m unittest discover -s tests
      - run: python scripts/validate_dataset.py --sample data/sample.json
      - run: python scripts/evaluate_model.py --config configs/evaluation.yaml
~~~

Cet extrait est un modèle de conception, pas une configuration prête à déployer telle quelle. Les scripts, chemins, versions d'actions et mécanismes de secrets doivent correspondre au dépôt réel et être contrôlés dans la CI. Un job de validation ne doit pas utiliser de jeton de production ni modifier des équipements.

### 9.2 Déploiement progressif

Le mode fantôme calcule les scores sans les utiliser pour modifier le comportement opérationnel. Il permet de comparer le candidat au modèle courant, d'estimer le volume de nouvelles alertes et de détecter les différences avant d'exposer les opérateurs au changement. Un canari peut ensuite servir une part limitée de la charge. L'étendue du canari dépend du risque et de la capacité à revenir rapidement en arrière.

Un déploiement n'est pas réussi simplement parce que l'API répond. Il faut contrôler la latence, les erreurs, la qualité des données, la conformité du format et les résultats opérationnels. Les seuils d'arrêt doivent être clairs et le rollback testé avant le déploiement.

## 10. Inférence, latence et disponibilité

Le service d'inférence reçoit des caractéristiques validées et renvoie un résultat conforme à un schéma. Il doit imposer des limites de taille, de temps, de concurrence et de mémoire. Les requêtes invalides doivent produire une erreur claire et ne pas être transformées silencieusement en prédictions normales.

### 10.1 API et contrat

Définissez la version du schéma, les champs obligatoires, la version du modèle, la signification du score, le statut de qualité et les comportements d'erreur. Les clients doivent être capables de distinguer une absence de risque d'une impossibilité de calculer un risque. Ne retournez pas seulement null sans expliquer s'il s'agit d'une mesure absente, d'une version incompatible ou d'une erreur technique.

### 10.2 Latence et capacité

Les modèles peuvent être exécutés à la demande, en tâche périodique ou dans un flux. Le choix dépend du volume et du délai utile. Une prédiction de maintenance quotidienne n'a peut-être pas besoin d'un service synchrone à très faible latence. Le surdimensionnement augmente les coûts sans nécessairement améliorer le résultat opérationnel.

Mesurez le délai au percentile élevé, le débit, le taux d'erreur, la consommation mémoire et les temps de chargement. Les tests doivent inclure des pics et des entrées invalides. Prévoyez des limites de concurrence et une stratégie de dégradation si le service devient saturé.

### 10.3 Mode dégradé

Si le service de modèle est indisponible, l'application doit appliquer un comportement défini : utiliser la dernière version validée si cela est sûr, revenir à une baseline, continuer la surveillance déterministe ou marquer la prédiction indisponible. Elle ne doit pas remplacer l'échec par un score arbitraire. La politique de repli varie selon la fonction et le coût d'une erreur.

## 11. Observabilité, dérive et qualité

L'observabilité d'un modèle couvre les métriques de service, la qualité des entrées, le comportement des sorties et les résultats observés après l'action. Surveiller uniquement CPU et mémoire ne détecte pas une dégradation statistique. Surveiller uniquement les scores ne détecte pas nécessairement une panne du service. Les deux familles sont nécessaires.

### 11.1 Mesures techniques

Suivez latence, taux d'erreur, débit, saturation, temps de chargement, échecs de parsing, consommation mémoire, statut du registre et disponibilité des sources. Les alertes sur la chaîne d'inférence doivent pouvoir être distinguées des alertes sur le réseau surveillé par le modèle. Sinon, un incident sur la plateforme ML peut être pris pour une dégradation du service métier.

### 11.2 Qualité et dérive

Comparez les distributions des entrées à une référence, surveillez les valeurs manquantes et mesurez la fréquence des scores par plage. Lorsque les labels arrivent tard, calculez les métriques de performance quand les résultats sont disponibles et documentez ce retard. Un changement dans le nombre de prédictions n'indique pas à lui seul une dérive ; il peut provenir d'un changement de volume ou de sélection des actifs.

### 11.3 Réponse à une dérive

Une alerte de dérive déclenche une enquête. Vérifiez d'abord la collecte, les unités, le schéma, la fréquence et la topologie. Si la source a changé, corriger les données. Si le phénomène opérationnel a changé, évaluer un nouvel entraînement. Si les labels sont insuffisants, maintenir un mode prudent ou une baseline plutôt que de promouvoir automatiquement un candidat.

Un réentraînement sans revue peut apprendre un incident temporaire, incorporer des labels erronés ou rendre un modèle moins performant sur les sites minoritaires. La promotion reste conditionnée à une évaluation reproductible, des tests et une décision documentée.

## 12. Incident, rollback et réponse à une régression

Le modèle en production est un composant logiciel soumis aux incidents. Il faut définir une équipe responsable, une alerte, une procédure d'investigation et des conditions d'arrêt. Lorsqu'un changement provoque un comportement anormal, conserver les logs, l'identifiant de la version, les entrées et la configuration utile, dans le respect des règles de confidentialité.

### 12.1 Déclencheurs de rollback

Les déclencheurs peuvent inclure une hausse du taux d'erreur, une latence excessive, une entrée devenue incompatible, une baisse significative d'une métrique de qualité disponible ou un incident attribuable au comportement du modèle. Les seuils doivent être ajustés à l'application et définis avant le déploiement. Une décision de rollback doit être journalisée.

### 12.2 Retour arrière réel

Revenir à une ancienne version exige de restaurer le modèle, les variables et parfois le schéma de données compatible. Si le pipeline a changé la représentation des caractéristiques, l'ancien modèle peut ne plus être compatible avec les nouvelles entrées. Les modèles et leur code de transformation doivent donc être packagés ou reliés par un contrat versionné.

Un rollback doit être testé de façon périodique. Une procédure non exercée peut échouer lorsque les registres, les dépendances ou les secrets ont changé. Le test confirme aussi que le système ne modifie pas l'historique des prédictions et que les opérateurs savent quel modèle est redevenu actif.

### 12.3 Retour d'expérience

Après incident, identifier si l'échec vient des données, de la transformation, du modèle, de l'API, du déploiement, de la surveillance ou de la procédure d'action. Consigner une action corrective et un test de non-régression. Il ne faut pas conclure immédiatement que le modèle doit être réentraîné : un défaut d'unité ou un mauvais schéma peut expliquer la plupart des symptômes.

## 13. Atelier Python et manifeste d'artefact

Le code suivant écrit un manifeste d'exemple en JSON et calcule une empreinte de fichier lorsque le chemin fourni existe. Il illustre comment relier un artefact à ses métadonnées. Il n'entraîne pas de modèle et n'accorde aucun statut de production.

~~~python
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(model_path: Path, version: str, code_revision: str) -> dict:
    if not model_path.is_file():
        raise FileNotFoundError(f"Artefact absent : {model_path}")
    if not version.strip():
        raise ValueError("La version du modèle est obligatoire")
    if not code_revision.strip():
        raise ValueError("La révision du code est obligatoire")

    return {
        "model_version": version,
        "code_revision": code_revision,
        "artifact_name": model_path.name,
        "artifact_sha256": sha256_file(model_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate",
    }


if __name__ == "__main__":
    artifact = Path("artifacts/model.bin")
    try:
        manifest = build_manifest(artifact, "0.1.0", "example-revision")
        Path("artifacts/manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        print("Manifeste écrit.")
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Impossible de produire le manifeste : {exc}")
~~~

Le chemin d'artefact de l'exemple est fictif. Le script doit être exécuté sur une version de modèle obtenue par un processus contrôlé. Une empreinte confirme l'identité des octets ; elle ne prouve ni la qualité du modèle ni l'autorité de la personne qui l'a approuvé. La provenance de l'empreinte, la protection des droits d'écriture et la validation du manifeste restent nécessaires.

## 14. TP : industrialiser un modèle de supervision

### Scénario

Vous disposez d'un modèle qui classe des fenêtres de télémétrie selon le risque d'incident. Il a été entraîné dans un notebook. Vous devez transformer le prototype en pipeline qui produit un artefact, un rapport et un manifeste, puis qui peut être évalué et déployé en mode fantôme.

### Étape 1 — Isoler les fonctions

Séparez le chargement, la validation, la préparation des variables, l'entraînement, l'évaluation et la sauvegarde. Chaque fonction prend des entrées explicites et retourne une sortie définie. Les fonctions ne doivent pas dépendre d'une variable globale créée par l'exécution précédente d'une cellule de notebook.

### Étape 2 — Définir les contrats

Écrivez le schéma d'entrée et le schéma de sortie. Définissez les champs obligatoires, les valeurs nulles permises, l'horizon, l'unité de score et le statut des données. Ajoutez des erreurs explicites pour les entrées invalides. Versionnez les transformations avec le modèle afin d'empêcher les incompatibilités.

### Étape 3 — Ajouter les tests

Créez des tests unitaires pour les caractéristiques, les tests de données, des cas de référence pour le modèle et un test de contrat d'inférence. Ajoutez des cas où une variable est absente, un timestamp est invalide ou une distribution est anormale. Le pipeline doit bloquer la promotion lorsqu'un contrôle obligatoire échoue.

### Étape 4 — Automatiser l'évaluation

Faites tourner une baseline et le candidat sur un jeu de référence figé. Générez les métriques et un rapport de comparaison. Le pipeline doit produire le statut « candidat » et ne doit pas modifier le modèle approuvé si le candidat échoue. Consignez la révision de code, l'identifiant de dataset et les paramètres.

### Étape 5 — Mode fantôme et promotion

Déployez le candidat sans influencer l'exploitation. Comparez ses résultats au modèle courant, observez la latence et les entrées, puis faites examiner les écarts. Définissez les critères de promotion et les seuils de rollback. Documentez comment restaurer le modèle précédent avec le bon schéma de caractéristiques.

### Livrables du TP

- pipeline d'entraînement reproductible ;
- tests unitaires et tests de données ;
- rapport d'évaluation et baseline ;
- manifeste d'artefact ;
- politique d'acceptation d'une version ;
- contrat d'API ou de batch d'inférence ;
- plan de déploiement progressif ;
- procédure de rollback testée ;
- tableau de bord de dérive et de service.

## 15. Gouvernance, accès et coûts

La gouvernance doit documenter le propriétaire, la finalité, les données, les limites, les utilisateurs et la procédure de retrait du modèle. Les accès au stockage, au registre et aux workflows sont limités au besoin. Les secrets sont injectés depuis un mécanisme prévu à cet effet et ne sont pas enregistrés dans les sorties. Les journaux de CI ne doivent pas exposer d'identifiants ou de données sensibles.

Le coût comprend stockage des jeux de données, calcul d'entraînement, service d'inférence, observabilité, support et travail humain de validation. Une architecture complexe peut coûter davantage que le bénéfice de quelques prédictions quotidiennes. Estimez le coût par run et le coût de maintenance, puis déterminez si une exécution périodique, une batch ou une API sert réellement l'objectif.

Les dépendances doivent être mises à jour dans un processus contrôlé. La mise à jour d'une bibliothèque de ML peut changer le comportement, le temps d'exécution ou le format de sérialisation. Il faut tester le candidat, documenter la compatibilité et éviter les mises à niveau automatiques non évaluées sur la chaîne de production.

### Responsabilités et niveaux d'approbation

Un modèle utilisé pour fournir un tableau de bord informatif n'a pas le même profil de risque qu'un modèle qui priorise des actions sur les équipements. Le niveau de revue doit suivre l'impact de l'erreur. Pour une fonction à faible risque, un pipeline testé et une approbation d'équipe peuvent suffire. Pour une fonction critique, il peut être nécessaire d'avoir une revue métier, une revue de sécurité et une procédure de changement formelle.

La responsabilité ne disparaît pas parce que la décision contient un score de modèle. Le propriétaire du service reste responsable de la politique qui utilise ce score et doit pouvoir expliquer les critères de décision.

## 16. Dépannage

### Le modèle produit des résultats différents à chaque entraînement

Vérifiez les graines aléatoires, les partitions temporelles, les versions de dépendances, les transformations et l'ordre des données. Certains algorithmes sont stochastiques ; documentez la tolérance admise. Conservez les identifiants d'entrée et de configuration pour distinguer une variation attendue d'une régression.

### Le modèle enregistré ne se charge plus

Vérifiez la compatibilité entre la version de la bibliothèque qui a sérialisé l'artefact et celle qui le charge. Examinez l'empreinte, les permissions, le format et le manifeste. Ne désactivez pas les contrôles d'intégrité pour contourner l'erreur. Restaurer la version précédente peut être plus sûr pendant l'investigation.

### La CI réussit mais la production échoue

La CI peut ne pas reproduire les permissions, la source de données, le schéma, la configuration ou la charge réels. Comparez les environnements et ajoutez des tests de contrat. Les tests doivent rester isolés et ne pas accéder à la production par défaut ; les tests d'intégration privilégiés suivent un processus distinct.

### Les métriques se dégradent sans erreur technique

Inspectez la distribution des entrées, la qualité des labels et les segments. Une baisse de qualité n'implique pas nécessairement un défaut de code. Elle peut provenir d'un changement de réseau ou de comportement métier. Le modèle doit pouvoir être restreint à son périmètre évalué pendant l'investigation.

### Un déploiement n'a pas de rollback fiable

Le modèle courant n'est pas suffisamment traçable ou la transformation compatible n'est pas conservée. Cessez les promotions jusqu'à ce que les versions de modèle et de caractéristiques soient reliées, que la procédure de restauration soit testée et que les responsables connaissent les étapes nécessaires.

## Architecture de référence et implémentation guidée

Le MLOps appliqué à l'infrastructure réseau encadre toute la vie du modèle : données, expériences, validation, empaquetage, déploiement, surveillance, réentraînement, retrait et retour à la dernière version connue. Un déploiement réussi au sens informatique n'implique pas que le modèle est utile ou sûr sur les flux réels.

### De l'expérience à un service contrôlé

```mermaid
flowchart TD
  A["Jeu de données versionné"] --> B["Validation de schéma et qualité"]
  B --> C["Entraînement reproductible"]
  C --> D["Évaluation et comparaison à la baseline"]
  D --> E{"Garde-fous qualité satisfaits ?"}
  E -- "Non" --> F["Refuser la promotion"]
  E -- "Oui" --> G["Artefact et registre de modèle"]
  G --> H["Test de compatibilité et sécurité"]
  H --> I["Déploiement shadow ou canari"]
  I --> J["Surveiller qualité, latence et dérive"]
  J --> K{"SLO et comportement acceptables ?"}
  K -- "Non" --> L["Rollback et analyse"]
  K -- "Oui" --> M["Promotion par étapes"]
  M --> N["Revue périodique et traçabilité"]
```

### Gestion des versions et retour arrière

```mermaid
sequenceDiagram
  participant CI as Pipeline CI
  participant R as Registre de modèles
  participant S as Service de prédiction
  participant M as Monitoring
  CI->>R: Publier artefact et manifeste validés
  R-->>CI: Version immuable
  CI->>S: Déployer canari avec cette version
  S-->>M: Prédictions, latence et erreurs
  M-->>CI: Rapport des garde-fous
  alt Garde-fous dépassés
    CI->>S: Revenir à la version précédente
    S-->>M: Vérifier le retour effectif
  else Garde-fous satisfaits
    CI->>S: Étendre le déploiement
  end
```

### Exemple de manifeste de modèle

```yaml
model:
  name: wan-congestion-risk
  version: 2026.10.3
  artifact_sha256: "REMPLACER_PAR_LE_SHA256_REEL"
data:
  dataset_version: wan-metrics-2026-10-01
  schema_version: 3
  feature_contract: wan-risk-features-v2
evaluation:
  temporal_test_end: "2026-09-30T23:59:59Z"
  baseline: seasonal-percentile-v1
  max_p95_latency_ms: 40
  minimum_recall_critical: 0.90
deployment:
  strategy: shadow
  rollback_version: 2026.09.2
  owner: network-reliability
```

Les seuils sont des exemples à calibrer avec les propriétaires du service. Le condensat d'artefact, le jeu de données, le schéma et le contrat de variables doivent être renseignés par la pipeline, jamais copiés manuellement sans contrôle. Un manifeste permet de répondre à la question : quel modèle, entraîné avec quelles données et évalué selon quelle politique, tourne actuellement ?

### Travaux pratiques — rendre le déploiement reproductible

Crée un petit modèle ou un modèle de référence et enregistre son contrat de données, ses dépendances et ses métriques. Produis deux artefacts avec des versions distinctes ; vérifie qu'un ancien nom ne peut pas être réutilisé silencieusement pour un contenu différent. Fais échouer une promotion lorsque le schéma d'entrée change, puis lorsque la performance sur la période temporelle diminue.

Simule ensuite une hausse de latence et une dérive de distribution. Le monitoring doit distinguer une panne du service de prédiction d'une dégradation de qualité du modèle. Le rollback doit restaurer le code, l'artefact et les paramètres compatibles, puis confirmer par lecture de l'état déployé qu'il est réellement effectif.

### Critères d'acceptation

Le modèle est reproductible, versionné, comparé à une baseline et promu par étapes. Le registre donne le lignage des données et artefacts. Le service expose latence, erreurs, disponibilité et indicateurs de dérive ; enfin, un rollback est démontré par un test, et pas seulement documenté dans un README.

## 17. Exercices corrigés

### Exercice 1 — Lignage

Un score a été généré il y a deux semaines, mais l'équipe ignore quelle version du modèle était active.

**Correction :** le système ne conserve pas une liaison obligatoire entre prédiction et version. Ajouter au résultat l'identifiant de modèle, la version de schéma et les métadonnées nécessaires, puis tester que chaque score expose ces champs. Préserver aussi le code, les paramètres et l'identifiant de dataset lorsque les politiques de conservation le permettent.

### Exercice 2 — Promotion automatique

Un candidat a une meilleure précision globale mais perd du rappel sur les équipements critiques.

**Correction :** ne pas le promouvoir automatiquement sur la seule métrique agrégée. Revoir les critères par segment, le coût des faux négatifs et les seuils de sécurité. Les critères de promotion auraient dû inclure les performances critiques avant l'entraînement du candidat.

### Exercice 3 — Dérive après changement de collecte

Après une mise à jour du collecteur, une métrique passe de secondes à millisecondes sans changement dans le contrat.

**Correction :** bloquer ou marquer les entrées concernées, corriger la normalisation et ajouter un test de schéma ou d'unité. Réentraîner un modèle sur les valeurs mal interprétées ne résoudrait pas le défaut. Les transformations versionnées doivent rendre ce type de changement visible.

### Exercice 4 — Échec du service de modèle

L'API d'inférence ne répond plus mais les règles de supervision classiques fonctionnent.

**Correction :** appliquer le mode dégradé prévu : conserver les alertes déterministes, marquer les scores ML indisponibles, journaliser l'incident et alerter le propriétaire. Ne pas convertir l'indisponibilité en score zéro. Restaurer le modèle après tests de service et vérification de la version active.

### Exercice 5 — Rollback incomplet

Le retour à l'ancien modèle fonctionne, mais le nouveau pipeline lui envoie des caractéristiques dont l'ordre a changé.

**Correction :** restaurer un ensemble cohérent modèle-plus-transformations ou une version compatible du schéma. Le rollback doit être testé sur le contrat complet et non seulement sur le fichier du modèle.

## 18. Défi final, checklist et références

### Défi

Industrialisez un classifieur de risque réseau. Il reçoit des métriques, produit un score et aide à prioriser l'investigation. Il doit être déployé sans action automatique sur les équipements. Proposez le pipeline, les contrôles CI, le registre, le mode fantôme, la surveillance et la procédure de rollback.

### Correction proposée

Définir d'abord le contrat d'entrée et de sortie, la cible, les métriques d'acceptation et les utilisateurs. Le code de préparation est versionné et testé. Le pipeline charge un snapshot identifié, valide le schéma, construit les variables, entraîne baseline et candidat, réalise une évaluation temporelle et écrit un rapport avec manifeste. Un candidat qui ne respecte pas les seuils est rejeté sans modifier la version courante.

Les artefacts sont enregistrés avec leur empreinte, la révision de code, l'identifiant de données, les paramètres, les dépendances et le rapport. Le déploiement commence en mode fantôme. L'équipe compare les scores, la latence et la qualité des entrées avant une promotion approuvée. Les dashboards suivent les erreurs de service, la fraîcheur, la dérive et les résultats terrain.

Un rollback restaure le modèle et la chaîne de caractéristiques compatibles. Les seuils d'arrêt sont définis avant le canari. En cas de dégradation, le système revient à une version vérifiée ou à une baseline et conserve le dossier de l'incident. Le processus prévoit une revue pour déterminer si la cause vient de la collecte, du pipeline, du modèle ou du déploiement.

### Checklist

- [ ] Objectif métier, cible et métriques mesurables.
- [ ] Contrat de données et de sortie versionné.
- [ ] Code, paramètres, environnement et identifiant de données conservés.
- [ ] Pipeline exécutable et reproductible.
- [ ] Tests unitaires, de données, de modèle, d'intégration et de sécurité.
- [ ] Baseline et critères de promotion définis avant évaluation.
- [ ] Artefacts immuables, empreintes et registre.
- [ ] Droits de CI minimaux, secrets protégés et dépendances contrôlées.
- [ ] Déploiement en mode fantôme et canari si nécessaire.
- [ ] Métriques techniques et qualité statistique surveillées.
- [ ] Dérive interprétée avant tout réentraînement.
- [ ] Rollback modèle-plus-transformations testé.
- [ ] Responsable d'astreinte et procédure de retrait documentés.

### Références

- MLflow, documentation : https://mlflow.org/docs/latest/
- Scikit-learn, modèles et pipelines : https://scikit-learn.org/stable/
- GitHub Actions, documentation : https://docs.github.com/actions
- NIST, AI Risk Management Framework : https://www.nist.gov/itl/ai-risk-management-framework
- OpenTelemetry, documentation : https://opentelemetry.io/docs/

Le MLOps transforme une expérimentation en service maintenable. La clé n'est pas seulement de déployer rapidement : il faut savoir exactement quel modèle tourne, comment il a été produit, pourquoi il a été accepté, comment détecter sa dégradation et comment revenir à un état connu sans perdre la traçabilité.