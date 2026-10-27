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

# Contrôle de base : garder les mesures valides et repérer les doublons.
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

## 9. Exercices corrigés

### Exercice 1 — Fuite de données

Une équipe entraîne un modèle sur un tableau qui contient la date de dernière réparation, la température actuelle et un champ calculé après clôture du ticket. Le score de test atteint 99 %. Peut-on considérer le modèle validé ?

**Correction.** Non. Le champ de réparation et tout champ calculé après l'événement risquent de révéler l'issue au modèle. Il faut reconstruire les caractéristiques telles qu'elles auraient existé à l'instant de prédiction, créer une découpe temporelle et réévaluer sans utiliser le jeu de test pour choisir les paramètres.

### Exercice 2 — Haute précision, faible rappel

Le modèle déclenche dix alertes : neuf correspondent à un défaut confirmé. Sur vingt défauts observés, il n'en détecte que neuf. Que faut-il examiner ?

**Correction.** La précision observée est 9/10, soit 90 %, et le rappel est 9/20, soit 45 %. Le modèle évite les fausses alertes mais manque plus de la moitié des défauts. La décision dépend du coût des omissions, du délai d'anticipation et des ressources. Il faut examiner les défauts manqués, les populations mal couvertes et les seuils, sans simplement abaisser le seuil sans mesure.

### Exercice 3 — Capteur muet

Un capteur ne transmet plus de mesure depuis deux heures. Le dernier score prédictif était faible. Peut-on maintenir le statut « aucun risque » ?

**Correction.** Non. La fraîcheur des données fait partie du fonctionnement. Le statut doit signaler une mesure indisponible et appliquer la stratégie de surveillance de repli. Un score ancien ne prouve pas que l'état courant est sain.

## 10. Défi final corrigé

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

## Références pour approfondir

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) — gouvernance, mesure et gestion des risques associés aux systèmes d'IA.
- [NIST — publications et ressources de confiance](https://www.nist.gov/) — méthodes de validation, gestion des risques et pratiques d'ingénierie.
- La documentation du fabricant de l'actif et du capteur reste la référence prioritaire pour les plages physiques, les consignes de sécurité et les fréquences recommandées.
