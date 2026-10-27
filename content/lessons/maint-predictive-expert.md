# Maintenance prédictive : capteurs, données et modèles

> **Mise en contexte**
>
> Une plateforme d'exploitation signale qu'un serveur de virtualisation présente des pointes de température et des vibrations inhabituelles sur ses ventilateurs. Les alertes disparaissent parfois avant qu'un technicien ouvre le ticket. L'équipe hésite entre augmenter tous les seuils, remplacer les ventilateurs immédiatement ou analyser les mesures historiques. Au niveau expert, l'objectif n'est pas de « mettre de l'IA partout » : il faut établir si les données permettent réellement d'anticiper une défaillance, quantifier l'incertitude, relier les alertes à une décision opérationnelle et conserver un moyen de revenir à une stratégie sûre.
>
> Ce cours traite la maintenance prédictive comme une chaîne de décision : actif, capteurs, données, indicateurs, modèle, validation humaine, intervention et mesure du résultat. Un score de modèle n'est jamais, à lui seul, une autorisation de modifier un système de production.

## Objectifs pédagogiques

À la fin du cours, tu devrais pouvoir construire un cas d'usage prédictif cadré, définir des signaux et des fenêtres d'observation, détecter les défauts de qualité des séries temporelles, comparer une règle simple à un modèle statistique ou d'apprentissage automatique, choisir des métriques adaptées aux défaillances rares, éviter les fuites de données, mesurer la dérive après mise en service et concevoir un dispositif de repli.

## Prérequis et périmètre

Il faut savoir lire des courbes de supervision, manipuler des tableaux de données et comprendre les risques de changement en production. Une maîtrise avancée du calcul différentiel n'est pas indispensable, mais les notions de moyenne, variance, quantile, probabilité conditionnelle et classification sont utiles. Le cours s'applique à la maintenance informatique, aux réseaux, aux alimentations, aux systèmes de refroidissement et aux infrastructures industrielles instrumentées. Il ne remplace ni les instructions du fabricant ni les habilitations nécessaires.

## 1. Distinguer les stratégies de maintenance

La maintenance préventive systématique déclenche une tâche selon un calendrier ou un compteur. La maintenance conditionnelle déclenche une action lorsqu'une mesure franchit une règle ou révèle un état défavorable. La maintenance prédictive exploite l'historique et plusieurs signaux pour estimer un risque futur, une classe d'état ou une fenêtre d'intervention. Ces stratégies peuvent coexister sur un même actif.

| Approche | Déclencheur | Atout | Limite |
|---|---|---|---|
| Corrective | Une défaillance est constatée | Simple à définir | L'impact a déjà commencé |
| Préventive calendaire | Date, durée ou compteur | Prévisible | Peut entretenir trop tôt ou trop tard |
| Conditionnelle | Mesure ou seuil actuel | Compréhensible et rapide | Un seul seuil peut rater des interactions |
| Prédictive | Tendance, motif ou probabilité estimée | Peut mieux cibler l'intervention | Dépend de la qualité des données et de la validation |

Le premier travail est de choisir un problème qui justifie le coût supplémentaire. Une alerte prédictive n'est pas automatiquement meilleure qu'un seuil robuste. Si un seuil simple détecte le défaut assez tôt, avec peu de fausses alertes, un modèle complexe peut n'apporter qu'une charge supplémentaire.

### Schéma 1 — De la mesure à la décision

~~~mermaid
flowchart TD
    A[Actif et modes de défaillance] --> B[Capteurs et journaux]
    B --> C[Contrôle de qualité des données]
    C --> D[Indicateurs et caractéristiques]
    D --> E[Seuil simple ou modèle]
    E --> F[Validation du contexte et de l'incertitude]
    F --> G{Risque opérationnel confirmé ?}
    G -- Non --> H[Continuer la surveillance et documenter]
    G -- Oui --> I[Créer une tâche selon la procédure]
    I --> J[Test, intervention et preuve]
    J --> K[Mesurer le résultat et recalibrer]
~~~

## 2. Cadrer le cas d'usage avant de collecter les données

Définis l'actif, le service rendu, le défaut que l'on veut anticiper, l'horizon utile, la décision qui peut être prise et le coût des erreurs. « Prédire les pannes » est trop vague. Une formulation exploitable serait : « détecter, entre 24 heures et 14 jours à l'avance, les unités de ventilation dont le risque de défaillance exige une inspection planifiée, en maintenant moins de deux fausses alertes par cent unités et par semaine ».

Il faut distinguer trois temps : l'instant où les données sont mesurées, la période sur laquelle le modèle observe les signaux et l'horizon pendant lequel une défaillance doit être prédite. Ces temps ne sont pas interchangeables. Le modèle peut être exact à une minute près sur une donnée déjà connue tout en étant inutile pour planifier une intervention vingt-quatre heures à l'avance.

### Fiche de cadrage

- Actifs inclus et exclus, identifiés par un identifiant stable.
- Mode(s) de défaillance étudié(s), symptômes et conséquence métier.
- Définition d'un événement positif et source de confirmation.
- Fréquence de mesure, fenêtres d'observation et horizon de prédiction.
- Décision autorisée, équipe responsable et délai de réaction.
- Coût d'une fausse alerte, d'une alerte manquée et d'une intervention inutile.
- Mesures de comparaison avant et après déploiement.
- Conditions d'arrêt, retour à la supervision classique et responsable de la décision.

## 3. Concevoir une chaîne de données fiable

Les données peuvent provenir de sondes de température, de compteurs d'erreurs, de journaux système, de l'outil d'inventaire, de l'historique de tickets, de mesures de puissance, de cycles de charge et des interventions réalisées. Chaque source doit avoir une sémantique explicite : unité, fuseau horaire, fréquence, identifiant de l'actif, version du capteur, méthode de collecte et politique de conservation.

La qualité doit être contrôlée avant l'entraînement. Recherche les horodatages dupliqués, les périodes manquantes, les valeurs impossibles, les unités incohérentes, les remplacements de capteur et les changements de configuration. Une absence de mesure ne signifie pas que l'actif fonctionne normalement. Elle peut indiquer une perte de télémétrie, précisément le type d'événement qu'il faut traiter.

### Schéma 2 — Le pipeline avec portes de qualité

~~~mermaid
flowchart LR
    A[Sources hétérogènes] --> B[Normaliser unités et horodatages]
    B --> C[Dédupliquer et contrôler les trous]
    C --> D[Relier les mesures à l'actif et à sa version]
    D --> E[Construire les fenêtres temporelles]
    E --> F[Créer les caractéristiques]
    F --> G[Jeu de validation chronologique]
    G --> H[Évaluation et décision de mise en service]
~~~

Ne joins pas les mesures uniquement sur un nom d'équipement susceptible de changer. Utilise un identifiant de parc et conserve les dates de début et de fin de validité de chaque association. Si une sonde est remplacée ou déplacée, note le changement : une modification de position peut produire une rupture statistique qui ressemble à un défaut matériel.

Les étiquettes de panne demandent autant d'attention que les capteurs. Un ticket « ventilateur bruyant » n'est pas nécessairement une défaillance confirmée. Associe chaque événement à une règle d'acceptation, à une preuve, à la date de confirmation et, lorsque c'est possible, à la date de début estimée. Distingue « confirmé », « probable », « non confirmé » et « absence d'information ».

## 4. Transformer les séries temporelles en caractéristiques

Une caractéristique (feature) est une information dérivée utilisée par une règle ou un modèle. Pour une température, les caractéristiques possibles incluent la dernière mesure, la moyenne sur 15 minutes, la médiane, le quantile élevé, la pente récente, l'écart par rapport à la charge attendue, la durée passée au-dessus d'un seuil et le nombre de dépassements dans une fenêtre.

Une fenêtre glissante stabilise le bruit mais peut masquer une pointe brève. Une fenêtre courte réagit rapidement et génère parfois plus de fausses alertes ; une fenêtre longue lisse les anomalies et introduit du retard. Compare plusieurs horizons sur des exemples annotés et relie le choix au temps d'action disponible. Toute transformation utilisée en production doit être documentée et reproductible.

Exemple de pseudo-code Python pour calculer des indicateurs simples avec pandas, à adapter au nom réel des colonnes et à la cadence de collecte :

~~~python
import pandas as pd

df = pd.read_csv("telemetrie.csv", parse_dates=["timestamp"])
df = df.sort_values(["asset_id", "timestamp"])

### Contrôle de base : garder les mesures valides et repérer les doublons.
df = df.dropna(subset=["asset_id", "timestamp", "temperature_c"])
df = df.drop_duplicates(["asset_id", "timestamp"], keep="last")

groups = df.groupby("asset_id", group_keys=False)
df["mean_15"] = groups["temperature_c"].transform(
    lambda s: s.rolling(15, min_periods=5).mean()
)
df["max_60"] = groups["temperature_c"].transform(
    lambda s: s.rolling(60, min_periods=10).max()
)
df["delta_mean"] = df["temperature_c"] - df["mean_15"]

df.to_csv("telemetrie_features.csv", index=False)
~~~

Cette illustration suppose une mesure par minute ; le nombre de lignes n'est pas une durée universelle. En production, vérifie les trous temporels, le tri, les fuseaux et les redémarrages de compteur. Calcule toute caractéristique uniquement avec les données disponibles au moment où la prédiction aurait été produite.

### Pourquoi la fuite temporelle invalide les résultats

Une fuite se produit lorsqu'une caractéristique utilise une information qui n'aurait pas encore été connue au moment de la prédiction. Exemples : un champ « date de réparation » recopié dans la fenêtre d'observation, une moyenne calculée sur le futur, une normalisation ajustée sur l'ensemble train-test, ou des tickets clos après la panne utilisés comme signal précédent l'événement. Le score obtenu lors du développement devient irréaliste.

Découpe les données par le temps et, si nécessaire, par famille d'actifs. Une bonne validation simule le futur : entraîner sur la période ancienne, choisir les paramètres sur une période suivante et tester sur une période plus récente jamais utilisée pour le réglage. Si plusieurs mesures d'un même incident se retrouvent dans train et test, la performance peut sembler élevée parce que le modèle reconnaît le même événement.

## 5. Choisir une approche proportionnée

Commence par une référence simple : règle experte, tendance linéaire, moyenne glissante, seuil par charge ou score de déviation par rapport à une référence propre à l'actif. Cette base sert à déterminer si le modèle plus élaboré apporte une amélioration opérationnelle nette.

Un modèle supervisé exige des événements historiques suffisamment fiables. Une méthode non supervisée peut repérer un comportement inhabituel sans avoir beaucoup d'étiquettes, mais une anomalie statistique n'est pas toujours une panne. Un modèle de durée de vie restante peut être utile si les cycles de dégradation sont observables ; il est trompeur si les remplacements préventifs censurent une grande partie des trajectoires. Le choix du modèle dépend d'abord de la définition de l'événement et de la décision.

## 6. Évaluer dans un environnement où les pannes sont rares

L'accuracy globale peut être trompeuse. Si 99 % des fenêtres ne correspondent pas à une panne, un modèle qui ne signale jamais rien peut afficher 99 % d'accuracy tout en étant inutile. Observe au minimum :

- la précision des alertes : parmi les alertes générées, quelle part correspond à un besoin confirmé ;
- le rappel : quelle part des événements pertinents a été détectée ;
- le délai d'anticipation : combien de temps reste-t-il pour intervenir ;
- le nombre de fausses alertes par actif et par période ;
- la proportion d'événements critiques manqués ;
- la charge de travail engendrée par les alertes et les inspections.

La précision et le rappel entrent souvent en tension. Réduire le seuil peut détecter plus d'événements, mais générer davantage de fausses alertes. Fixe le seuil à partir du risque et des ressources disponibles, puis documente les cas limites. Utilise aussi des résultats par type d'actif, modèle, site et régime de charge : une moyenne générale peut masquer une population mal couverte.

### Schéma 3 — Décision selon les conséquences

~~~mermaid
quadrantChart
    title Conséquence d'une alerte et niveau de preuve
    x-axis "Preuve faible" --> "Preuve forte"
    y-axis "Impact faible" --> "Impact critique"
    quadrant-1 "Inspection prioritaire"
    quadrant-2 "Vérifier avant action"
    quadrant-3 "Surveillance"
    quadrant-4 "Action proportionnée"
~~~

Une matrice de confusion ne remplace pas une analyse opérationnelle. Vérifie si l'équipe peut effectivement inspecter toutes les alertes à l'heure, si les pièces sont disponibles et si l'intervention elle-même présente un risque. Dans certains cas, une alerte de niveau faible doit simplement augmenter la fréquence de surveillance. Dans d'autres, une alerte critique déclenche un processus humain immédiat selon la procédure d'exploitation.

## 7. Mettre en production sans créer une nouvelle source de panne

Commence en mode observation : le modèle produit des alertes invisibles aux opérateurs ou comparées aux décisions existantes. Compare les alertes à des examens manuels, mesure les faux positifs et vérifie la chaîne de livraison des données. Ensuite, affiche les alertes avec leur contexte et laisse l'équipe autorisée décider de l'action.

Sépare les permissions d'analyse et celles de commande. Le système prédictif ne doit pas pouvoir arrêter un équipement, modifier un seuil de sécurité ou déclencher une opération irréversible simplement parce que son score dépasse une valeur. Toute automatisation d'action exige une analyse de risque distincte, une autorisation explicite, une procédure de retour et des tests représentatifs.

### Surveillance du modèle

Surveille la disponibilité et la fraîcheur des mesures, la proportion de valeurs manquantes, la distribution des caractéristiques, les scores émis, le nombre d'alertes, le taux de confirmation, le délai moyen d'anticipation, les incidents après alerte et les résultats du modèle sur des événements confirmés. Distingue la dérive des données (les conditions ont changé) de la dégradation des performances (les décisions deviennent moins pertinentes). Elles peuvent apparaître séparément.

Un changement de modèle doit être versionné : données utilisées, code et paramètres, période d'évaluation, limites connues, approbation et plan de retour. Si une source de données devient indisponible, le système doit le signaler et revenir à la stratégie de surveillance convenue. Il ne doit pas interpréter l'absence de capteur comme une preuve de bon état.

### Schéma 4 — Cycle de vie opérationnel

~~~mermaid
flowchart TD
    A[Définir le cas d'usage] --> B[Établir la référence]
    B --> C[Entraîner et évaluer dans le temps]
    C --> D[Revue technique et métier]
    D --> E[Mode observation]
    E --> F{Critères tenus ?}
    F -- Non --> C
    F -- Oui --> G[Déploiement limité]
    G --> H[Surveillance des données et résultats]
    H --> I{Dérive ou incident ?}
    I -- Oui --> J[Réduire le périmètre ou revenir à la référence]
    I -- Non --> H
~~~

## 8. TP guidé : définir un seuil défendable

**Scénario.** Une équipe supervise la température de baies informatiques. Elle observe des dépassements fréquents pendant les pointes de charge, mais les contrôles manuels confirment peu de défauts. L'équipe veut éviter de créer des tickets inutiles.

1. Vérifie que les mesures ont une unité cohérente et une cadence suffisamment stable.
2. Compare les courbes aux périodes de charge, à la température ambiante et au type de baie.
3. Définis une référence par classe d'actif plutôt qu'un seuil universel non justifié.
4. Mesure les alertes, confirmations, défauts manqués et délais d'anticipation.
5. Teste la règle sur une période ultérieure sans régler le seuil sur cette même période.
6. Présente les résultats à l'équipe de maintenance et définis un seuil de révision.
7. En mode observation, compare la nouvelle règle à celle en vigueur avant de la rendre opérationnelle.

**Critère de réussite :** le résultat contient les données utilisées, la règle, les métriques, les limites, les cas d'échec et la décision opérationnelle proposée. Une capture du graphique seule ne constitue pas une validation.


## 9. Instrumenter correctement : les capteurs font partie du modèle

Une chaîne prédictive ne peut pas être plus fiable que les mesures qui l'alimentent. Avant de choisir un algorithme, confirme que les capteurs mesurent les phénomènes pertinents, au bon endroit, avec une unité connue, une cadence adaptée et une incertitude acceptable. Une température prise dans le flux d'air de sortie n'a pas la même signification qu'une température prise sur le boîtier d'un moteur. Une vibration dépend de la position, du montage, de la charge et de la vitesse de rotation. Un courant électrique dépend notamment de la charge réellement appliquée. Une valeur ne doit jamais être interprétée sans son contexte opérationnel.

### 9.1 Définir la chaîne de mesure

Pour chaque capteur, documente l'identifiant, l'actif, la position, la grandeur, l'unité, la plage, la précision annoncée, la cadence, la calibration, la date de remplacement, le dernier état de santé et la source du temps. Quand un équipement remplace un autre capteur, ne suppose pas automatiquement que les deux séries sont directement comparables : la plage, la précision, la fixation ou la fréquence peuvent avoir changé.

| Grandeur observée | Exemple d'usage | Contrôles à prévoir |
|---|---|---|
| Température | Détection d'échauffement anormal | Unité, emplacement, plage et décalage de mesure |
| Vibration | Détection de déséquilibre ou de dégradation mécanique | Fréquence d'échantillonnage, montage, régime de rotation |
| Pression | Détection d'un filtre obstrué ou d'une perte de pression | Capteur, conditions de fonctionnement et plage valide |
| Courant / puissance | Détection de surcharge ou de comportement atypique | Charge, facteur de puissance le cas échéant, phase et unité |
| Débit | Suivi d'une pompe ou d'un circuit | Sens de mesure, état des vannes et stabilité du régime |
| Erreurs et états logiciels | Détection de réinitialisations ou de dégradations de service | Version du firmware, événements de maintenance et événements de supervision |

Il est parfois préférable d'améliorer l'emplacement d'un capteur ou la procédure de collecte plutôt que d'ajouter un modèle complexe. Les mesures doivent permettre de distinguer une variation normale du régime d'exploitation d'une dégradation réelle.

~~~mermaid
flowchart LR
    A[Actif physique] --> B[Capteur et emplacement]
    B --> C[Calibration et horodatage]
    C --> D[Collecte et validation]
    D --> E[Caractéristiques et tendances]
    E --> F[Diagnostic ou alerte]
    F --> G[Inspection et retour terrain]
~~~

### 9.2 Fréquence d'échantillonnage et fenêtre d'observation

La cadence doit suivre le phénomène. Une température d'ambiance peut changer relativement lentement, tandis que certaines signatures vibratoires nécessitent un échantillonnage rapide. Une collecte trop rare peut manquer un événement transitoire ; une collecte extrêmement rapide peut créer un volume difficile à stocker sans apporter d'information utile. Le choix se fonde sur le phénomène mesuré, les recommandations du fabricant, le débit nécessaire à l'analyse et les contraintes de stockage.

Les moyennes glissantes sont utiles pour visualiser les tendances, mais elles peuvent lisser un pic important. Si un pic court est lié à un défaut, une moyenne sur une longue fenêtre peut le faire disparaître. Conserve les données brutes nécessaires, puis calcule plusieurs caractéristiques adaptées : moyenne, minimum, maximum, écart-type, variation, percentiles ou indicateurs spécifiques au domaine. La fenêtre et la méthode doivent être documentées pour que les tests restent reproductibles.

### 9.3 Calibration, décalage et dérive du capteur

Un capteur peut se décaler lentement, se saturer, rester figé ou transmettre une valeur plausible mais incorrecte. Un modèle entraîné sur ces mesures peut interpréter la dérive de l'instrument comme un changement de l'actif. Relie donc la télémétrie aux dates de calibration, aux remplacements, aux interventions et aux anomalies connues du capteur. Un signal doit posséder un état de qualité : valide, suspect, manquant, périmé ou hors plage, plutôt qu'une simple valeur numérique.

Les contrôles de base comprennent :
- détection des valeurs impossibles selon la plage physique et l'unité ;
- détection d'une valeur inchangée trop longtemps quand une variation est normalement attendue ;
- vérification de la fraîcheur du dernier échantillon ;
- contrôle de la cadence et des trous de transmission ;
- comparaison avec des capteurs redondants ou des indicateurs indépendants, quand ils existent ;
- corrélation avec les dates de maintenance, de remplacement et de calibration ;
- traitement explicite des unités différentes et des changements de configuration.

Une valeur manquante n'est pas équivalente à zéro. Une mesure de température absente ne signifie pas que la température est nulle, et un capteur muet ne signifie pas que l'actif est sain. Lorsqu'une donnée n'est pas fiable, l'algorithme doit recevoir cette information ou l'échantillon doit être mis en quarantaine selon une règle documentée.

## 10. Concevoir un jeu de données qui respecte le temps et le contexte

La maintenance prédictive s'appuie souvent sur plusieurs sources : télémétrie, alarmes, ordres de travail, pièces remplacées, contrôles manuels, événements logiciels, charge, environnement et calendrier d'exploitation. Il faut relier ces sources à l'actif, au moment et au contexte corrects. Une table qui contient des mesures sans identifiant stable de l'équipement, sans unité ou sans fuseau horaire est une mauvaise base de modélisation.

### 10.1 Schéma minimal d'une série temporelle

~~~text
asset_id | timestamp_utc       | signal         | value | unit | quality
---------|---------------------|----------------|-------|------|--------
PUMP-014 | 2026-02-10T08:00:00Z| bearing_temp   | 67.2  | °C   | valid
PUMP-014 | 2026-02-10T08:05:00Z| bearing_temp   | 67.5  | °C   | valid
PUMP-014 | 2026-02-10T08:10:00Z| bearing_temp   |       | °C   | missing
PUMP-014 | 2026-02-10T08:15:00Z| bearing_temp   | 68.9  | °C   | valid
~~~

Le schéma est illustratif. Le nom du signal et l'unité doivent être définis dans un dictionnaire commun. Garde les unités d'origine dans les données conservées et enregistre toute conversion. La normalisation du temps doit conserver l'heure d'origine lorsqu'elle est utile à l'investigation, ainsi que le fuseau utilisé. Si les journaux de la passerelle, du contrôleur et de l'outil de tickets utilisent des horloges différentes, une simple jointure par timestamp peut rattacher une mesure à la mauvaise intervention.

### 10.2 Relier les mesures aux événements de maintenance

Pour entraîner ou évaluer un modèle, il faut des événements de référence suffisamment fiables : panne confirmée, inspection avec constat, remplacement d'une pièce, arrêt planifié ou alarme finalement non liée à un défaut. Le ticket de maintenance est une source, mais il peut être créé après l'événement, avoir une catégorie approximative ou être clôturé sans cause confirmée. Un technicien qui saisit « moteur défectueux » après le remplacement ne fournit pas nécessairement un instant exact où la dégradation a commencé.

Crée des règles d'annotation : événement cible, date de début connue ou estimée, date de confirmation, actif concerné, niveau de confiance, cause et interventions associées. Sépare les événements confirmés des soupçons ou des observations incomplètes. Il peut être utile de conserver plusieurs états : « défaut confirmé », « inspection sans défaut détecté », « capteur défaillant », « événement inconnu » et « maintenance planifiée ».

~~~mermaid
flowchart TD
    A[Télémétrie] --> D[Réconciliation temporelle]
    B[Tickets et ordres de travail] --> D
    C[Journal d'intervention et changements] --> D
    D --> E[Annotation et confiance]
    E --> F[Dataset versionné]
    F --> G[Analyse et séparation temporelle]
    G --> H[Évaluation hors échantillon]
~~~

### 10.3 Éviter la fuite de données temporelle

La fuite temporelle se produit lorsque le modèle apprend indirectement des informations qui ne seraient pas connues au moment où l'alerte doit être produite. Exemple : une variable indique qu'une intervention a été ouverte après la panne, ou un agrégat inclut une mesure prise après la date de prédiction. Le modèle peut alors présenter de bons résultats dans un test, mais échouer dans l'exploitation.

Pour chaque caractéristique, pose la question : « Cette information serait-elle disponible à l'instant exact où la prédiction est censée être faite ? » Si la réponse est non, elle ne doit pas être utilisée comme variable de prédiction. Les séparations entraînement/validation/test doivent respecter le temps et, si nécessaire, séparer aussi les équipements pour mesurer la capacité de généralisation à de nouveaux actifs. Une division aléatoire de lignes peut mélanger des mesures presque identiques du même incident dans les ensembles d'entraînement et de test.

## 11. Construire des caractéristiques utiles et choisir une méthode adaptée

Les caractéristiques sont des informations calculées à partir des données brutes pour aider à reconnaître un comportement. Elles peuvent être simples et explicables : moyenne sur une fenêtre, pente, nombre de dépassements, variance, rapport entre deux signaux ou durée passée dans un état. La complexité doit être justifiée par un gain démontré. Un modèle sophistiqué sur des données mal étiquetées peut être moins utile qu'une règle claire correctement exploitée.

### 11.1 Exemples de caractéristiques

| Caractéristique | Ce qu'elle peut révéler | Limite |
|---|---|---|
| Moyenne glissante | Niveau de fonctionnement sur une période | Peut masquer un pic court |
| Pente ou variation | Hausse progressive d'une mesure | Sensible au bruit et aux changements de régime |
| Écart à une référence | Écart par rapport à un fonctionnement comparable | La référence peut devenir obsolète |
| Variabilité | Instabilité d'une mesure | Peut être normale à certains régimes |
| Comptage de dépassements | Fréquence d'un seuil franchi | Dépend du seuil et de la durée |
| Temps depuis la dernière intervention | Contexte du cycle de vie | Ne prouve pas l'état réel de l'actif |
| Combinaison de signaux | Relations entre température, charge et vibration | Peut devenir difficile à expliquer sans validation |

La référence devrait comparer des périodes et des conditions de fonctionnement similaires. Un équipement chargé à 90 % ne doit pas nécessairement être comparé à son propre régime de repos. Segmente les données selon le mode de fonctionnement, la charge, les saisons ou les étapes de production lorsque ces facteurs modifient le comportement attendu.

### 11.2 Des méthodes simples aux modèles complexes

Commence par une référence de comparaison :
1. règles du fabricant ou seuils de sécurité existants ;
2. tendances historiques et seuils conditionnés par le régime ;
3. règles combinant plusieurs signaux ;
4. détection d'anomalies non supervisée, si les pannes sont trop peu étiquetées ;
5. modèle supervisé si les événements historiques et les labels sont suffisamment fiables ;
6. estimation de durée de vie restante seulement si les trajectoires de dégradation permettent de la valider.

Un modèle de classification peut répondre « défaut probable dans un horizon défini » ; un détecteur d'anomalie répond plutôt « comportement inhabituel » ; une estimation de durée de vie restante prédit une quantité différente et nécessite des hypothèses supplémentaires. Ne présente pas une anomalie comme une panne confirmée. Les alertes doivent être utilisées pour orienter une inspection, non pour remplacer automatiquement le diagnostic expert.

~~~mermaid
flowchart TD
    A[Objectif métier et données] --> B{Labels fiables et suffisants ?}
    B -->|Non| C[Règles et détection d'anomalies]
    B -->|Oui| D[Classifieur ou modèle de durée]
    C --> E[Comparaison au seuil de référence]
    D --> E
    E --> F[Test temporel hors échantillon]
    F --> G[Analyse des défauts manqués et fausses alertes]
    G --> H[Décision humaine et pilote]
~~~

### 11.3 La dérive et les changements de régime

Un modèle entraîné sur une année peut devenir moins pertinent si l'actif change, si les capteurs sont remplacés, si une nouvelle version de logiciel modifie les mesures ou si le mode de production évolue. La dérive peut concerner la distribution des entrées, la relation entre les mesures et la panne, ou simplement les données manquantes. Un changement statistique ne prouve pas toujours une dégradation physique : il faut vérifier les modifications de contexte.

Conserve une ligne de base et un historique des versions. Quand une alerte devient plus fréquente, vérifie d'abord le capteur, les unités, le rythme de collecte, les modifications de firmware et le régime opérationnel. Réentraîner immédiatement peut masquer un défaut de capteur ou apprendre une nouvelle normalité qui serait dangereuse. Les changements importants doivent être évalués par une personne compétente et testés avant de remplacer le modèle en production.

## 12. Évaluer correctement un système de prédiction

Les pannes sont souvent rares par rapport au nombre de mesures normales. Un modèle qui dit toujours « aucun défaut » peut donc afficher une exactitude élevée sans aider la maintenance. Les métriques doivent refléter l'objectif et le coût métier : défaut critique manqué, inspection inutile, temps d'anticipation, durée d'immobilisation, coût des pièces et capacité des équipes à traiter les alertes.

### 12.1 Les métriques de base

- **Précision des alertes** : parmi les alertes positives, proportion correspondant à un événement confirmé.
- **Rappel** : parmi les défauts observés, proportion détectée.
- **Taux de faux positifs** : proportion de cas normaux signalés à tort selon la population définie.
- **Défauts critiques manqués** : nombre et proportion des événements graves non détectés.
- **Temps d'anticipation** : différence entre l'alerte exploitable et le début ou la confirmation de l'événement, selon une définition explicite.
- **Charge d'alerte** : nombre d'alertes par actif, par équipe ou par période, et part des alertes réellement traitées.
- **Valeur opérationnelle** : inspections pertinentes, interruptions évitées ou temps gagné, avec une méthode de mesure et des limites.

Les seuils sont des décisions opérationnelles, pas uniquement des paramètres mathématiques. Si une fausse alerte nécessite une inspection longue, l'équipe peut rapidement perdre confiance dans le système. Si une omission peut causer une défaillance dangereuse, il faut peut-être accepter davantage d'inspections, ajouter un contrôle indépendant ou ne pas utiliser le modèle pour cette décision.

### 12.2 Validation chronologique et par équipement

Le test doit imiter l'exploitation future. Entraîne sur une période ancienne, ajuste sur la période suivante, puis évalue sur une fenêtre plus récente non utilisée pour choisir les caractéristiques ou le seuil. Si le même équipement apparaît à plusieurs moments, assure-toi que la séparation ne donne pas au modèle un avantage irréaliste. Dans certains contextes, il est utile d'évaluer deux cas distincts : les actifs déjà connus et les nouveaux actifs.

Un rapport de validation inclut le nombre de pannes, la période, les équipements couverts, les conditions d'exploitation, les données exclues, les valeurs manquantes, le nombre d'alertes, la précision, le rappel, les événements manqués, le délai d'anticipation et les conséquences de la sélection du seuil. Les valeurs globales doivent être accompagnées d'un examen des erreurs importantes. Les cas rares et critiques ne doivent pas disparaître dans une moyenne.

~~~mermaid
flowchart LR
    A[Données historiques] --> B[Entraînement chronologique]
    B --> C[Réglage sur fenêtre de validation]
    C --> D[Test final sur période plus récente]
    D --> E[Analyse par actif et par type de défaut]
    E --> F[Revue des faux positifs]
    E --> G[Revue des défauts manqués]
    F --> H[Décision de pilote]
    G --> H
~~~

### 12.3 Exemple de coûts asymétriques

Supposons qu'un modèle émette 40 alertes dans un mois. Vingt-huit déclenchent une inspection utile, huit sont des fausses alertes et quatre restent indéterminées faute de démontage ou de preuve suffisante. Pendant la même période, un défaut critique est découvert après coup sans alerte préalable. Il serait trompeur de déclarer le modèle « précis à 70 % » en classant arbitrairement les quatre cas inconnus. Il faut expliquer la règle de définition d'une vraie alerte, le traitement des incertitudes et le défaut manqué.

La bonne démarche consiste à examiner l'événement manqué, la qualité des capteurs, l'horizon de prédiction, le profil de fonctionnement et la limite du modèle. La décision peut être d'ajouter un capteur, de modifier l'horizon, d'utiliser une règle indépendante ou de limiter le modèle à une recommandation d'inspection. Il ne faut pas modifier le seuil après coup puis rapporter les performances sur les mêmes données comme si le test était indépendant.

## 13. Transformer l'alerte en décision de maintenance

Une prédiction n'a de valeur que si l'organisation peut agir à temps. L'alerte doit apporter le contexte, la sévérité, les éléments qui la soutiennent et une recommandation autorisée. Elle doit également préciser l'incertitude et le délai pendant lequel une action préventive peut encore être utile.

Une fiche d'alerte comprend par exemple :
- identifiant de l'actif et du capteur ;
- heure de génération et heure de dernière mesure valide ;
- horizon de prédiction et version du modèle ;
- comportement observé et référence utilisée ;
- score ou niveau de confiance avec sa définition ;
- hypothèses possibles et contrôles à effectuer ;
- criticité et conséquence possible ;
- action recommandée et autorité de validation ;
- date de réévaluation ou de fermeture ;
- retour de l'inspection ou de l'intervention.

Ne présente pas un score de 0,92 comme « 92 % de chance de panne » si le modèle n'a pas été calibré et évalué pour donner cette probabilité sur la population concernée. Un score de modèle peut n'être qu'un classement. Les écrans et les procédures doivent nommer correctement ce que la mesure signifie.

~~~mermaid
flowchart TD
    A[Alerte prédictive] --> B[Vérifier fraîcheur et qualité des signaux]
    B --> C{Données valides ?}
    C -->|Non| D[Déclarer l'alerte non fiable et activer le repli]
    C -->|Oui| E[Évaluer l'actif, l'impact et l'horizon]
    E --> F[Inspection ou décision humaine]
    F --> G[Résultat terrain documenté]
    G --> H[Comparer à l'alerte et améliorer le système]
~~~

### 13.1 Boucle de retour terrain

Pour chaque alerte, enregistre ce qui a été inspecté et découvert. Une alerte sans retour ne permet pas de savoir si elle était utile. Mais « aucun défaut détecté » ne signifie pas toujours « fausse alerte » : l'inspection peut avoir eu lieu trop tôt, ne pas couvrir le mode de défaillance ou ne pas disposer des moyens de vérification. Définis les catégories de retour et les informations minimales attendues avant de calculer la précision.

La maintenance prédictive devrait enrichir le système d'ordres de travail, pas créer une file parallèle sans propriétaire. Les recommandations doivent être triées selon la criticité, les pièces et compétences disponibles, les fenêtres d'intervention et les autres tâches planifiées. Le meilleur modèle ne sert à rien si aucune équipe ne peut traiter les alertes.

## 14. Déploiement, surveillance et sécurité de la chaîne de données

Le déploiement débute en mode observation : le système calcule et journalise les alertes sans commander directement l'actif. Les résultats sont comparés aux inspections et à la maintenance normale. Après la validation du pilote, on peut faire évoluer l'usage vers des recommandations mieux intégrées, tout en conservant l'autorité du processus technique. Un changement de modèle ou de capteur doit être versionné et justifié.

### 14.1 Surveiller le système autant que l'actif

Les indicateurs de suivi incluent :
- fraîcheur des mesures et taux de données manquantes ;
- anomalies de capteurs et changements de calibration ;
- volume et répartition des alertes ;
- taux d'inspection et délai de traitement ;
- précision/rappel estimés lorsque les résultats terrain sont disponibles ;
- défauts manqués et fausses alertes majeures ;
- stabilité des distributions et des caractéristiques ;
- versions de données, du code et du modèle ;
- retours opérateurs et décisions de repli.

### 14.2 Sécurité et protection de la production

Les capteurs, passerelles et plateformes de données sont des actifs informatiques. Ils peuvent introduire des accès distants, des identifiants, des logiciels, des mises à jour et de nouveaux chemins de communication. Dans un environnement opérationnel, la cybersécurité doit tenir compte de la disponibilité, de la fiabilité et de la sûreté. N'ajoute pas un accès cloud direct à un contrôleur ou un équipement critique simplement pour faciliter l'analyse. Fais passer les données par une architecture approuvée, limite les flux et protège les comptes.

NIST SP 800-82 Rev. 3 fournit des recommandations pour sécuriser les technologies opérationnelles tout en tenant compte de leurs contraintes de fiabilité et de sûreté. En septembre 2026, NIST a publié le projet initial de la révision 4 pour commentaires ; il s'agit d'un projet public, pas encore d'une version finale applicable comme telle. Toute architecture réelle doit être évaluée selon les politiques de l'organisation et les prescriptions du fabricant.

Le système prédictif doit échouer dans un état contrôlé. Si les données sont périmées, le modèle ne doit pas présenter un état « sain » par défaut. Si le service de prédiction tombe, la procédure de maintenance existante, les alarmes de sécurité et les protections locales doivent continuer à fonctionner selon leur conception. Une suggestion de modèle ne doit pas inhiber une alarme native ou court-circuiter un interverrouillage de sécurité.

~~~mermaid
flowchart TD
    A[Capteurs / passerelle] --> B[Zone de collecte contrôlée]
    B --> C[Validation, identité et journalisation]
    C --> D[Plateforme d'analyse]
    D --> E[Recommandation aux opérateurs]
    E --> F[Procédure et validation humaine]
    F --> G[Ordre de travail autorisé]
    D -. aucune commande directe .-> H[Contrôles locaux de sûreté inchangés]
~~~

### 14.3 Le modèle de repli

Définis avant le pilote les conditions dans lesquelles le système est considéré comme indisponible ou non fiable : données manquantes au-delà d'un délai, capteur hors plage, version non approuvée, dérive non expliquée, taux de faux positifs excessif ou anomalie de sécurité. Le repli peut consister à ignorer l'alerte prédictive, à revenir à une surveillance de seuil approuvée, à augmenter la fréquence d'inspection ou à faire intervenir un spécialiste. Le choix dépend du risque et doit être documenté.

La personne qui reçoit l'alerte doit pouvoir voir sa qualité et son âge. Un score récent calculé sur des mesures valides n'a pas la même valeur qu'un score ancien calculé avant le remplacement d'un capteur. La provenance des données, la version du modèle et l'état du pipeline font partie de la preuve opérationnelle.

## 15. Mesurer la valeur du programme et éviter les mauvaises incitations

Une baisse des pannes après le déploiement ne prouve pas à elle seule que le modèle en est responsable. Le volume de production peut avoir diminué, un équipement peut avoir été remplacé, une campagne de maintenance peut avoir été menée ou la façon de classer les incidents peut avoir changé. Définis une ligne de base et documente les changements qui influencent la comparaison.

Mesures possibles :
- nombre de défaillances par période et par exposition comparable ;
- heures d'arrêt non planifié ;
- coût et charge des inspections préventives ;
- nombre d'alertes traitées et proportion confirmée ;
- délai d'anticipation et actions réalisables avant la panne ;
- coûts des pièces et interventions ;
- incidents non détectés par le modèle ;
- taux de données indisponibles ;
- effets inattendus et contraintes de sécurité.

Il faut aussi analyser les incitations. Si l'équipe est évaluée uniquement sur le nombre de pannes évitées, elle peut classer les interventions comme préventives ou déclarer les alertes comme correctes sans preuve. Si l'équipe est évaluée uniquement sur la précision, elle peut augmenter le seuil pour réduire les alertes et manquer davantage de défauts. Les indicateurs doivent se compléter et la qualité des données doit pouvoir être vérifiée.

## 16. TP 2 guidé : évaluer un pilote de détection de dégradation

### Situation

Une pompe de circulation possède des mesures de température de palier, de vibration et de courant moteur toutes les cinq minutes. Les techniciens ont documenté six défaillances confirmées et plusieurs inspections sans anomalie sur deux ans. Un modèle d'essai émet 30 alertes en un mois, dont 21 sont suivies d'une inspection ; 12 inspections confirment une anomalie à traiter, 6 concluent à un fonctionnement normal et 3 restent indéterminées. Neuf alertes n'ont pas été inspectées pendant le mois. Une défaillance a également eu lieu sans alerte exploitable. Le fournisseur affirme que son modèle est « précis à 90 % », sans fournir la méthode de calcul.

### Travail demandé

1. Liste les informations à demander avant d'accepter le chiffre de 90 %.
2. Classe les alertes en confirmées, non confirmées et inconnues selon les éléments fournis.
3. Explique pourquoi les neuf alertes non inspectées ne peuvent pas être déclarées fausses positives.
4. Propose un protocole de test temporel et des métriques métier.
5. Définis des conditions de repli et une recommandation de pilote.

### Corrigé détaillé

Le chiffre de 90 % n'est pas interprétable sans savoir comment la vérité terrain a été définie, quelle population est le dénominateur, quelle période a été évaluée, si le jeu de test est indépendant et si les événements rares ont été pris en compte. Il faut connaître les identifiants des actifs, la répartition des défaillances, les alertes, les inspections, les événements inconnus et les règles de déduplication. Un score issu d'un test de laboratoire ne démontre pas la même performance sur les conditions réelles d'exploitation.

Les douze inspections avec anomalie sont des alertes confirmées selon le niveau d'information disponible, mais il faut préciser si l'anomalie correspond au défaut cible. Les six inspections normales peuvent être classées comme non confirmées selon le protocole retenu. Les trois inspections indéterminées restent inconnues. Les neuf alertes non inspectées ne peuvent pas être classées, car l'absence de retour n'est pas une preuve d'absence de défaut.

La défaillance non anticipée doit être examinée, même si elle ne fait pas partie des alertes : elle peut révéler une couverture incomplète, un défaut sans signature mesurée, un capteur défaillant ou un horizon inadéquat. Pour la validation, sépare les données par périodes chronologiques, conserve une fenêtre finale non utilisée pour le réglage, examine les résultats par pompe et par défaut, et documente les cas manqués. Les mesures devraient inclure le rappel, la précision sur les alertes effectivement évaluées, les inconnues, le temps d'anticipation, le nombre d'inspections, les défauts critiques manqués et la charge des équipes.

La recommandation est de prolonger le pilote en mode observation, de traiter les alertes en attente selon la procédure de maintenance, de vérifier les capteurs et d'organiser une revue technique des défauts manqués. Le modèle ne doit pas commander la pompe. Il ne peut être utilisé comme aide à la décision que si le système de données est fiable, si les alertes ont un propriétaire et si le processus de repli est testé. La décision d'élargir le pilote nécessite des critères d'acceptation définis à l'avance.

## 17. Checklist avant mise en production

- [ ] Cas d'usage, actifs, défauts cibles et horizon définis.
- [ ] Baseline simple et testable documentée.
- [ ] Capteurs, unités, cadence, calibration et qualité inventoriés.
- [ ] Horodatages normalisés, changements et interventions rapprochés.
- [ ] Labels, défauts confirmés et cas inconnus distingués.
- [ ] Fuite temporelle et fuite entre équipements évaluées.
- [ ] Test final chronologique indépendant du réglage des paramètres.
- [ ] Précision, rappel, défauts critiques manqués et charge d'alerte mesurés.
- [ ] Fausses alertes et cas manqués examinés avec des experts du domaine.
- [ ] Seuils et décisions calibrés selon les conséquences.
- [ ] Aucune commande directe non autorisée vers un équipement physique.
- [ ] Journalisation, contrôle d'accès et provenance des données en place.
- [ ] Procédure de repli, rôles et consignes d'escalade testés.
- [ ] Version du modèle, du code et des données conservée.
- [ ] Résultats et bénéfices du pilote mesurés par rapport à une ligne de base.


## 17. Exercices corrigés

### Exercice 1 — Fuite de données

Une équipe entraîne un modèle sur un tableau qui contient la date de dernière réparation, la température actuelle et un champ calculé après clôture du ticket. Le score de test atteint 99 %. Peut-on considérer le modèle validé ?

**Correction.** Non. Le champ de réparation et tout champ calculé après l'événement risquent de révéler l'issue au modèle. Il faut reconstruire les caractéristiques telles qu'elles auraient existé à l'instant de prédiction, créer une découpe temporelle et réévaluer sans utiliser le jeu de test pour choisir les paramètres.

### Exercice 2 — Haute précision, faible rappel

Le modèle déclenche dix alertes : neuf correspondent à un défaut confirmé. Sur vingt défauts observés, il n'en détecte que neuf. Que faut-il examiner ?

**Correction.** La précision observée est 9/10, soit 90 %, et le rappel est 9/20, soit 45 %. Le modèle évite les fausses alertes mais manque plus de la moitié des défauts. La décision dépend du coût des omissions, du délai d'anticipation et des ressources. Il faut examiner les défauts manqués, les populations mal couvertes et les seuils, sans simplement abaisser le seuil sans mesure.

### Exercice 3 — Capteur muet

Un capteur ne transmet plus de mesure depuis deux heures. Le dernier score prédictif était faible. Peut-on maintenir le statut « aucun risque » ?

**Correction.** Non. La fraîcheur des données fait partie du fonctionnement. Le statut doit signaler une mesure indisponible et appliquer la stratégie de surveillance de repli. Un score ancien ne prouve pas que l'état courant est sain.

## 18. Défi final corrigé

**Mission.** Tu dois proposer un pilote de maintenance prédictive pour les unités de refroidissement d'une salle informatique, sans autoriser le modèle à commander directement les équipements.

**Livrable attendu :** fiche de cadrage, schéma des données, définition de la panne, méthode de validation, métriques, seuils d'escalade, plan de surveillance et procédure de repli.

**Correction type.**

1. Définir les actifs et l'événement cible avec l'équipe responsable des installations.
2. Inventorier les mesures, leurs unités, la cadence, l'historique de changement des capteurs et les données de tickets.
3. Construire une référence à base de seuils et de tendances avant de tester des modèles plus complexes.
4. Découper les données chronologiquement et empêcher toute information postérieure à l'événement de devenir une caractéristique.
5. Évaluer précision, rappel, défauts critiques manqués, délai d'anticipation et charge d'inspection.
6. Déployer d'abord en observation puis sur un groupe limité, avec validation humaine.
7. Surveiller fraîcheur et dérive, versionner chaque modèle et revenir à la méthode de référence si la qualité baisse.
8. Mesurer à intervalle défini si les interventions sont plus anticipées et si les interruptions diminuent. Ne revendiquer une amélioration que si les données la soutiennent.

## 19. Références et approfondissement

- [ISO 17359:2018 — Condition monitoring and diagnostics of machines: General guidelines](https://www.iso.org/standard/71194.html) — lignes directrices pour établir un programme de surveillance de l'état des machines. Cette édition a été confirmée en 2023 comme restant actuelle.
- [ISO 13379-1:2025 — Condition monitoring and diagnostics of machine systems: Data interpretation and diagnostics techniques](https://www.iso.org/standard/88027.html) — concepts et principes pour interpréter les mesures et sélectionner une approche de diagnostic appropriée.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) — gouvernance, mesure et gestion des risques associés aux systèmes d'IA.
- [NIST SP 800-82 Rev. 3 — Guide to Operational Technology Security](https://csrc.nist.gov/pubs/sp/800/82/r3/final) — sécurité OT en tenant compte des exigences de performance, de fiabilité et de sûreté. La révision 4 était un projet public en consultation en septembre 2026, pas encore une édition finale.
- [NASA Prognostics Center of Excellence Data Set Repository](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/) — jeux de données d'essai pour étudier la dégradation de batteries, moteurs et autres systèmes; les jeux simulés ou expérimentaux ne remplacent pas la validation dans les conditions réelles.
- La documentation du fabricant de l'actif et du capteur reste prioritaire pour les plages physiques, les consignes de sécurité, les fréquences recommandées et les limites d'exploitation.

## 20. Conclusion

La maintenance prédictive ne commence pas par le choix d'un modèle d'IA. Elle commence par un objectif métier, une définition du défaut, une instrumentation fiable et une méthode honnête de validation. Les données doivent décrire l'actif au moment où la décision sera prise ; les mesures douteuses doivent être signalées ; les modèles doivent être comparés à une méthode simple ; les résultats doivent inclure les défauts manqués et la charge des fausses alertes.

Un système de prédiction n'est utile que s'il améliore une décision réelle et si l'organisation sait quoi faire lorsqu'il se trompe, se dégrade ou devient indisponible. Le déploiement doit être progressif, surveillé, traçable et compatible avec la sûreté des équipements. La bonne question n'est pas seulement « le modèle détecte-t-il quelque chose ? », mais « l'alerte aide-t-elle une équipe à intervenir à temps, de manière sûre et mesurable ? »