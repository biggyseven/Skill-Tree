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

## 8. Choisir les actifs et les modes de défaillance à surveiller

Une démarche prédictive ne commence pas par le choix d'un algorithme. Elle commence par l'identification d'un actif, de sa fonction, des conséquences d'une défaillance et des signes observables avant l'événement. L'objectif est de détecter suffisamment tôt une évolution qui justifie une action, sans générer tant de fausses alertes que l'équipe cesse de les lire.

Pour les équipements d'une salle informatique, les actifs peuvent inclure les unités de refroidissement, les ventilateurs, les pompes, les onduleurs, les batteries, les alimentations, les unités de distribution électrique et certains composants d'infrastructure. Pour un environnement IT, les signaux possibles comprennent aussi la température, les erreurs de stockage, la correction d'erreurs mémoire, les compteurs d'interface, la capacité d'alimentation, les délais de service et les journaux d'incidents. Le signal doit avoir une relation plausible avec le mode de défaillance étudié.

### 8.1 Définir la cible avant de chercher des caractéristiques

Écris la cible en termes opérationnels. « Prévoir une panne » est trop vague. Une cible plus utile pourrait être : « identifier les unités de refroidissement présentant un risque accru d'échec de ventilateur dans les sept jours précédant un incident qui provoque une interruption ou une intervention corrective ». Cette définition fixe l'actif, l'événement, l'horizon temporel et la preuve de panne.

Il faut également préciser comment les étiquettes sont produites. Un ticket de maintenance peut être fermé sans que la pièce soit réellement défaillante ; un capteur peut avoir été remplacé de façon préventive ; une alarme peut être liée à un test. Définis les catégories confirmé, probable, préventif et inconnu. Ne transforme pas automatiquement toute intervention en étiquette « panne ». Si la qualité des étiquettes est faible, commence par un usage de surveillance et d'aide à l'investigation plutôt que d'affirmer une capacité prédictive robuste.

~~~mermaid
flowchart TD
    A[Actif et fonction] --> B[Mode de défaillance]
    B --> C[Conséquence métier]
    C --> D[Signal ou mesure observable]
    D --> E[Horizon d'anticipation]
    E --> F[Définition de la cible]
    F --> G[Validation de la qualité des étiquettes]
    G --> H[Modèle ou règles de surveillance]
~~~

### 8.2 Relier le mode de panne aux mesures utiles

| Mode de défaillance possible | Mesures candidates | Points de vigilance |
|---|---|---|
| Dégradation de ventilation | Vibration, vitesse, température, intensité électrique | Charge, température ambiante, poussière, régime de fonctionnement |
| Batterie d'onduleur vieillissante | Tension, température, résistance interne si mesurée, résultats de test | Type de batterie, âge, température et procédure de test |
| Encrassement ou perte d'efficacité du refroidissement | Températures, débit, pression, puissance consommée | Charge thermique, ouverture des portes, conditions ambiantes |
| Dégradation d'un disque ou volume de stockage | Erreurs corrigées, délais d'E/S, files d'attente, alertes de contrôleur | Modèle du matériel, firmware, charge et fenêtre de maintenance |
| Problème d'interface réseau | Erreurs, pertes, changements d'état, utilisation, latence | Vitesse, duplex, changements de configuration, congestion |
| Dégradation de capacité d'un service | Latence, taux d'erreur, saturation, files d'attente | Déploiements, trafic, dépendances et saisonnalité |

Ces mesures sont des candidats, pas des diagnostics automatiques. Le fait qu'une température augmente ne signifie pas toujours que l'équipement va tomber en panne : une hausse de charge ou de température ambiante peut expliquer le signal. La démarche doit comparer la mesure à un contexte de fonctionnement et au comportement historique de l'actif.

## 9. Maîtriser la qualité des capteurs et des mesures

Un modèle ne peut pas corriger magiquement une mesure incorrecte. Avant l'apprentissage, documente l'origine, l'unité, la fréquence, le délai de transmission, la calibration, l'emplacement, le firmware, les interruptions et les modifications des capteurs. Deux capteurs nommés « température » peuvent mesurer des zones différentes, avoir des unités différentes ou être relevés à des fréquences qui ne permettent pas une comparaison directe.

### 9.1 Vérifier les données à l'arrivée

Les contrôles de base incluent :
- horodatage parsable, fuseau connu et absence de dates futures inattendues ;
- identifiant d'actif stable et correspondance avec l'inventaire ;
- unité et gamme de valeurs plausibles selon le fabricant et le contexte ;
- duplication, ordre des événements et données reçues en retard ;
- taux de valeurs manquantes et durée maximale d'une lacune ;
- fraîcheur du dernier point reçu ;
- cohérence des changements de capteur, de firmware, de configuration et de charge ;
- qualité des étiquettes de panne et des tickets liés.

Il ne faut pas remplacer toutes les valeurs absentes par zéro. Zéro peut être une valeur physique légitime ou, au contraire, une indication de capteur en défaut. La méthode de traitement doit dépendre de la signification de la mesure et doit préserver un indicateur de donnée manquante si celui-ci est informatif. Un capteur muet doit produire un état « données indisponibles », pas un score rassurant calculé à partir d'une dernière observation ancienne.

### 9.2 Distinguer mesure, anomalie et panne

Une mesure hors de sa plage habituelle n'est pas automatiquement une panne. Une anomalie statistique est une observation ou une séquence qui diffère du comportement de référence. Une défaillance est un événement défini selon des critères opérationnels. Une action de maintenance est une décision prise à partir de la mesure, du contexte et du coût d'erreur.

~~~mermaid
flowchart TD
    A[Mesure reçue] --> B{Donnée valide et fraîche ?}
    B -->|Non| C[Alarme de qualité de mesure]
    B -->|Oui| D[Comparer au contexte et à la référence]
    D --> E{Anomalie ou tendance ?}
    E -->|Non| F[Surveillance normale]
    E -->|Oui| G[Évaluer le risque et corroborer]
    G --> H{Critère opérationnel atteint ?}
    H -->|Non| I[Observer ou compléter les mesures]
    H -->|Oui| J[Créer une recommandation]
    J --> K[Validation humaine et action autorisée]
~~~

### 9.3 Calibration et dérive des capteurs

La calibration, le remplacement et le déplacement d'un capteur peuvent créer un saut qui ressemble à une anomalie. Conserve les dates de maintenance et les versions de configuration dans le dataset. Après une modification, vérifie si le modèle de référence reste comparable. La dérive peut venir du capteur lui-même, mais aussi de la charge, des saisons, de l'environnement, du logiciel de collecte ou d'une modification de l'installation.

Pour les mesures qui contribuent à une décision de sécurité, de refroidissement ou d'alimentation, respecte les méthodes de mesure et les procédures du fabricant. Un score prédictif ne remplace pas une protection technique ou une inspection exigée. Le modèle doit compléter les contrôles prévus, pas les désactiver.

## 10. Préparer des séries temporelles sans fuite de données

La fuite de données survient lorsqu'une caractéristique ou une étape d'entraînement utilise une information qui ne serait pas disponible au moment réel de la prédiction. Elle produit souvent des résultats de test artificiellement élevés. En maintenance, les données après panne, le ticket clôturé, la pièce remplacée ou la décision d'intervention peuvent révéler indirectement l'événement cible.

Exemple : on veut prédire à 08 h si un ventilateur risque de tomber en panne dans les prochaines 48 heures. Si une caractéristique contient le nombre d'alarmes créées à 11 h le même jour, le test utilise une information future. Le modèle peut paraître excellent dans l'historique et échouer en production.

### 10.1 Respecter l'ordre temporel

Un découpage aléatoire ordinaire peut placer des observations du même équipement et de la même panne dans l'entraînement et dans le test. Le modèle apprend alors des détails très proches de l'événement à prédire. Préfère un découpage chronologique, et si le contexte le justifie, garde certains actifs ou sites entièrement hors de l'entraînement afin de tester la généralisation.

~~~mermaid
flowchart LR
    A[Historique ancien] --> B[Entraînement]
    B --> C[Validation sur période ultérieure]
    C --> D[Réglage de la méthode]
    D --> E[Test final encore plus récent]
    E --> F[Déploiement contrôlé]
    G[Données futures de production] --> H[Surveillance après déploiement]
    F --> H
~~~

Les caractéristiques, normalisations, imputations, sélections de variables et seuils doivent être ajustés uniquement à partir de l'ensemble d'entraînement ou selon la procédure de validation définie. Si tu normalises toutes les données avant le découpage, l'information sur la distribution du futur peut fuiter dans le processus d'apprentissage. Construis un pipeline qui apprend ses paramètres sur l'entraînement puis les applique aux périodes suivantes.

### 10.2 Fenêtres et horizons d'anticipation

Décris la fenêtre d'observation, l'horizon de prédiction et la période d'exclusion autour de l'événement si les données proches de la panne sont trop directement liées à l'alarme finale. Par exemple, les mesures des 24 heures précédant une intervention peuvent servir à détecter l'approche de la panne, mais elles peuvent aussi contenir une alarme déjà visible par un système classique. Il faut comparer l'apport du modèle à une simple règle de seuil afin de savoir si la complexité ajoute une valeur réelle.

Les mesures répétées d'un même actif ne sont pas indépendantes. Un découpage par ligne peut surestimer la performance si les mêmes actifs apparaissent dans chaque ensemble. Teste sur une période ultérieure et, lorsque pertinent, sur des actifs, sites ou modèles d'équipement différents. Une validation robuste demande plusieurs fenêtres temporelles et une description claire des limites du jeu de données.

## 11. Choisir une approche et établir une référence simple

Le modèle le plus complexe n'est pas nécessairement le meilleur choix. Un seuil défini selon le fabricant, une tendance, une règle statistique ou un modèle de référence peuvent être plus fiables, plus explicables et moins coûteux à exploiter. Compare toujours les solutions à une référence.

| Approche | Quand elle peut être utile | Limite principale |
|---|---|---|
| Seuil technique validé | Limite physique connue ou consigne fabricant | Peut manquer les évolutions lentes et le contexte |
| Tendance et taux de variation | Dérive progressive d'une mesure | Sensible au bruit, au changement de charge et à la fenêtre choisie |
| Règle combinée | Plusieurs conditions sont nécessaires pour déclencher | Les règles peuvent devenir difficiles à maintenir |
| Détection d'anomalies non supervisée | Peu d'exemples étiquetés de panne | Une anomalie n'indique pas nécessairement une panne |
| Classification supervisée | Historique d'événements de qualité suffisante | Biais des étiquettes, fuite temporelle et changement de contexte |
| Modèle de durée de vie restante (RUL) | Décision liée à une estimation de dégradation et d'horizon | Nécessite des hypothèses, un historique adapté et une incertitude explicite |

Un modèle supervisé peut estimer une probabilité sur un horizon précis. Cette probabilité n'est utile que si elle est suffisamment calibrée pour le contexte, et si les décideurs comprennent ce que « risque de panne dans les sept jours » signifie. Un modèle d'anomalie peut classer des observations inhabituelles sans pouvoir dire quelle panne va se produire. Un RUL est une estimation de durée restante sous des conditions et des hypothèses spécifiques, pas une date certaine de panne.

### 11.1 Séparer exploration et décision

L'exploration analytique aide à comprendre les données ; la décision opérationnelle exige des règles explicites. On peut visualiser une variable, tester plusieurs fenêtres ou comparer différents modèles lors de l'analyse. Mais le seuil de production doit être versionné, approuvé et évalué selon les conséquences des faux positifs et des défauts manqués.

Avant un essai, documente :
- la question de décision et le propriétaire ;
- le mode de panne ciblé ;
- les données disponibles au moment de la prédiction ;
- la référence actuelle et ses résultats ;
- les métriques retenues et les seuils d'acceptation ;
- les limites connues et la solution de repli.

### 11.2 Exemple de pipeline expérimental avec Python

Cet exemple illustre un découpage temporel simple dans scikit-learn. Il suppose que les lignes ont déjà été triées chronologiquement, que la colonne cible est construite sans données futures et que les données ne contiennent pas plusieurs observations du même événement réparties entre les ensembles. Pour des équipements fortement corrélés, ajoute un contrôle par actif ou par site.

~~~python
from sklearn.model_selection import TimeSeriesSplit

# X et y doivent être triés selon l'instant de décision.
# Tout prétraitement qui apprend des paramètres doit être ajusté
# à l'intérieur de chaque pli, pas sur l'ensemble complet.
splitter = TimeSeriesSplit(n_splits=5)

for fold, (train_idx, test_idx) in enumerate(splitter.split(X), start=1):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    print(
        f"Pli {fold}: "
        f"{len(train_idx)} observations d'entraînement, "
        f"{len(test_idx)} observations de test"
    )
~~~

Ce code ne crée pas à lui seul une validation parfaite. Il faut encore vérifier les périodes, les étiquettes, la présence d'événements chevauchants, le prétraitement, le déséquilibre des classes et la représentativité du test. Pour une évaluation de production, conserve les bornes temporelles de chaque pli et les résultats détaillés.

## 12. Évaluer les résultats selon les conséquences métier

Les pannes sont souvent rares. Un modèle qui annonce « aucun défaut » peut afficher une exactitude de 99 % si seulement 1 % des fenêtres contiennent une panne. Cela ne veut pas dire qu'il fournit une valeur opérationnelle. Il faut analyser la matrice de confusion, la précision, le rappel, le nombre d'alertes, les défauts critiques manqués et le temps d'anticipation.

- **Vrai positif** : une alerte précède une panne ou un état confirmé correspondant à la cible.
- **Faux positif** : une alerte est déclenchée sans événement correspondant dans l'horizon défini.
- **Faux négatif** : l'événement survient sans alerte exploitable dans la fenêtre d'anticipation.
- **Vrai négatif** : aucune alerte et aucun événement correspondant pendant la période définie.

La précision indique la proportion d'alertes qui correspondent à une cible selon la définition utilisée. Le rappel indique la proportion des événements cibles détectés. L'une ou l'autre ne suffit pas à choisir un seuil. Une équipe ayant peu de techniciens peut être submergée par un grand nombre de fausses alertes ; une organisation qui tolère mal les défauts critiques peut devoir privilégier le rappel et accepter davantage d'inspections, sous réserve de capacité.

### 12.1 Définir un seuil à partir du coût des erreurs

Construis une matrice de décision avec les responsables. Un faux positif peut déclencher une inspection, un déplacement ou une pièce préparée inutilement. Un faux négatif peut causer une interruption de service, une perte de production ou une intervention d'urgence. Les montants ne sont parfois connus que sous forme de plages ou de niveaux qualitatifs. Il vaut mieux documenter ces hypothèses qu'inventer une précision monétaire.

~~~mermaid
flowchart TD
    A[Probabilité ou score du modèle] --> B[Seuil candidat]
    B --> C[Historique de validation]
    C --> D[Estimer fausses alertes et défauts manqués]
    D --> E[Évaluer coût, délai et capacité]
    E --> F{Risque résiduel acceptable ?}
    F -->|Non| G[Modifier le seuil ou le dispositif]
    G --> C
    F -->|Oui| H[Approuver un pilote sous surveillance]
~~~

### 12.2 Mesurer l'anticipation réelle

La bonne métrique dépend de la décision. Mesure le délai entre la première alerte exploitable et l'événement confirmé. Une alerte envoyée deux minutes avant la panne peut compter comme une détection, mais elle ne donne pas suffisamment de temps pour planifier une intervention. À l'inverse, une alerte dix jours à l'avance peut être inutile si son incertitude est trop grande ou si elle arrive trop tôt pour déclencher une action économique.

Évalue aussi l'alert fatigue : alertes répétées sur le même actif, alertes ouvertes sans action, seuils fréquemment ignorés, événements inconnus et temps nécessaire pour vérifier chaque alerte. Regroupe les alertes selon une politique approuvée et conserve l'historique pour pouvoir évaluer la méthode. Ne supprime pas les alertes gênantes sans analyser pourquoi elles se produisent.

## 13. Mettre le modèle en production sans perdre le contrôle

Un modèle prédictif doit être traité comme un composant opérationnel avec version, propriétaire, paramètres, journalisation, tests et solution de repli. La surveillance couvre à la fois la chaîne de données et le modèle : disponibilité du capteur, fraîcheur, taux de valeurs manquantes, erreurs de calcul, version de modèle, fréquence des alertes, qualité des résultats vérifiés et changement de distribution des données.

### 13.1 Déploiement par étapes

Commence par le mode observation : le modèle produit des alertes qui sont comparées aux contrôles existants, sans déclencher automatiquement une intervention. Après une période de validation, un pilote limité peut autoriser des recommandations ou créer des demandes de revue, toujours selon le processus approuvé. L'automatisation directe d'une action physique ou d'un changement de configuration nécessite une évaluation de sécurité distincte et des protections adéquates.

~~~mermaid
flowchart LR
    A[Analyse historique] --> B[Mode observation]
    B --> C[Revue par experts]
    C --> D[Pilote limité]
    D --> E[Validation des alertes et coûts]
    E --> F{Critères tenus ?}
    F -->|Non| G[Corriger, suspendre ou revenir à la référence]
    G --> B
    F -->|Oui| H[Déploiement gradué]
    H --> I[Surveillance continue et revue périodique]
~~~

### 13.2 Prévoir les modes de défaillance du système prédictif

Le système lui-même peut tomber en panne : capteur muet, collecte interrompue, horloge incorrecte, modèle non chargé, configuration mal versionnée, service de prédiction indisponible ou alertes non transmises. Définis un état explicite pour chaque situation. Si la mesure n'est plus fraîche, l'interface doit indiquer « données indisponibles » ; elle ne doit pas afficher le dernier score comme s'il décrivait l'état courant.

La procédure de repli peut revenir à des seuils techniques, à une tournée d'inspection renforcée ou au plan de maintenance habituel selon l'actif. Il faut connaître le propriétaire qui décide du repli, les seuils qui déclenchent la suspension, la manière d'en informer les techniciens et les preuves à conserver.

### 13.3 Gérer la dérive du modèle

La dérive peut toucher les données d'entrée, la relation entre les mesures et la panne ou la façon dont les tickets sont enregistrés. Un changement de pièce, de firmware, de charge, de température ambiante ou de fournisseur de capteur peut modifier la distribution. La répartition des pannes peut aussi évoluer après une campagne de maintenance.

Surveille les indicateurs de données et les résultats vérifiés au fil du temps. Ne réentraîne pas automatiquement le modèle dès qu'un seuil de dérive est franchi : conserve les données, recherche la cause, compare la méthode actuelle à une référence et fais valider la nouvelle version. Si les pannes réelles sont rares, les métriques de performance peuvent nécessiter une fenêtre plus longue avant d'être interprétables.

### 13.4 La boucle de retour des techniciens

Les retours des intervenants constituent un élément essentiel. Pour chaque alerte, recueille le résultat de l'inspection, le mode de panne confirmé ou non, l'action choisie, le temps passé et la présence d'une condition particulière. Distingue « alerte non confirmée », « inspection insuffisante », « défaut absent dans l'horizon », « donnée erronée » et « cible mal définie ». Toutes ces situations n'ont pas la même signification pour l'amélioration du modèle.

## 14. Mesurer la valeur et gouverner le cycle de vie

La maintenance prédictive est utile si elle améliore une décision ou un résultat opérationnel par rapport aux pratiques existantes. Le bon point de comparaison peut être la maintenance préventive, la maintenance conditionnelle, des seuils techniques ou une stratégie basée sur le risque. Mesure une période de référence avant le déploiement et définis des métriques qui reflètent le coût total : interventions d'urgence, temps d'arrêt, inspection, pièces remplacées, fausses alertes, heures de mise au point et exploitation du système.

Un pilote doit avoir une limite de temps et un critère de sortie. Si la valeur n'est pas démontrée, il faut pouvoir revenir à une méthode plus simple. Évite de conserver un modèle coûteux uniquement parce qu'il a demandé beaucoup de travail. À l'inverse, une absence de panne pendant le pilote ne prouve pas à elle seule que le modèle est inefficace ; compare les résultats aux périodes et groupes pertinents, en notant l'incertitude.

### 14.1 Exemple d'analyse coût-bénéfice

Supposons qu'un modèle génère 30 alertes sur un trimestre. Vingt alertes déclenchent une inspection utile, six sont sans défaut confirmé et quatre ne peuvent pas être évaluées faute de mesure complémentaire. Tu ne dois pas présenter automatiquement 20/30 comme la précision finale si les quatre cas non évalués sont ignorés sans justification. Indique la population évaluable, les raisons des exclusions et une analyse de sensibilité si ces cas pouvaient modifier la conclusion.

Compare ensuite le coût des inspections supplémentaires et du dispositif aux changements mesurés : réduction des interruptions, meilleur délai de planification, disponibilité des pièces, temps d'investigation ou baisse des interventions d'urgence. Si le coût d'une panne est très élevé, une politique de rappel élevé peut être justifiée ; si les alertes mobilisent une équipe déjà saturée, il faut aussi estimer la capacité nécessaire et le risque d'ignorer une alerte critique.

### Schéma — De l'expérimentation à une décision de gestion d'actif

~~~mermaid
flowchart TD
    A[Définir la ligne de base] --> B[Mesurer la performance technique]
    B --> C[Mesurer les effets opérationnels]
    C --> D[Calculer coûts et bénéfices avec leurs incertitudes]
    D --> E[Comparer à la stratégie actuelle]
    E --> F{Valeur et sécurité démontrées ?}
    F -->|Oui| G[Déploiement contrôlé et revue périodique]
    F -->|Non| H[Réviser le cas d'usage ou abandonner]
    H --> I[Documenter les leçons et le repli]
~~~

### 14.2 Gouvernance et responsabilités

Attribue un propriétaire métier de l'actif, un responsable technique de l'infrastructure de données, un responsable de la méthode analytique, un propriétaire du processus de maintenance et une personne qui autorise les actions. Dans un petit environnement, les rôles peuvent être combinés, mais la décision de sécurité et les changements qui affectent le service doivent suivre le processus existant.

Conserve les versions du jeu de données, des caractéristiques, du modèle, des seuils, des critères de validation et des règles d'alerte. La traçabilité permet de répondre à trois questions : pourquoi l'alerte a-t-elle été émise à cette date, quelle information était disponible à cet instant, et quelle décision a été prise à partir de cette information ? Sans cette trace, il devient difficile d'expliquer les faux positifs, les défauts manqués ou une modification de comportement après une mise à jour.


## 15. TP guidé : définir un seuil défendable

**Scénario.** Une équipe supervise la température de baies informatiques. Elle observe des dépassements fréquents pendant les pointes de charge, mais les contrôles manuels confirment peu de défauts. L'équipe veut éviter de créer des tickets inutiles.

1. Vérifie que les mesures ont une unité cohérente et une cadence suffisamment stable.
2. Compare les courbes aux périodes de charge, à la température ambiante et au type de baie.
3. Définis une référence par classe d'actif plutôt qu'un seuil universel non justifié.
4. Mesure les alertes, confirmations, défauts manqués et délais d'anticipation.
5. Teste la règle sur une période ultérieure sans régler le seuil sur cette même période.
6. Présente les résultats à l'équipe de maintenance et définis un seuil de révision.
7. En mode observation, compare la nouvelle règle à celle en vigueur avant de la rendre opérationnelle.

**Critère de réussite :** le résultat contient les données utilisées, la règle, les métriques, les limites, les cas d'échec et la décision opérationnelle proposée. Une capture du graphique seule ne constitue pas une validation.

## 16. Exercices corrigés

### Exercice 1 — Fuite de données

Une équipe entraîne un modèle sur un tableau qui contient la date de dernière réparation, la température actuelle et un champ calculé après clôture du ticket. Le score de test atteint 99 %. Peut-on considérer le modèle validé ?

**Correction.** Non. Le champ de réparation et tout champ calculé après l'événement risquent de révéler l'issue au modèle. Il faut reconstruire les caractéristiques telles qu'elles auraient existé à l'instant de prédiction, créer une découpe temporelle et réévaluer sans utiliser le jeu de test pour choisir les paramètres.

### Exercice 2 — Haute précision, faible rappel

Le modèle déclenche dix alertes : neuf correspondent à un défaut confirmé. Sur vingt défauts observés, il n'en détecte que neuf. Que faut-il examiner ?

**Correction.** La précision observée est 9/10, soit 90 %, et le rappel est 9/20, soit 45 %. Le modèle évite les fausses alertes mais manque plus de la moitié des défauts. La décision dépend du coût des omissions, du délai d'anticipation et des ressources. Il faut examiner les défauts manqués, les populations mal couvertes et les seuils, sans simplement abaisser le seuil sans mesure.

### Exercice 3 — Capteur muet

Un capteur ne transmet plus de mesure depuis deux heures. Le dernier score prédictif était faible. Peut-on maintenir le statut « aucun risque » ?

**Correction.** Non. La fraîcheur des données fait partie du fonctionnement. Le statut doit signaler une mesure indisponible et appliquer la stratégie de surveillance de repli. Un score ancien ne prouve pas que l'état courant est sain.

## 17. Défi final corrigé

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

## 18. Références et approfondissement

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) — gouvernance, mesure et gestion des risques associés aux systèmes d'IA.
- [NIST — publications et ressources de confiance](https://www.nist.gov/) — méthodes de validation, gestion des risques et pratiques d'ingénierie.
- [ISO 17359:2018 — Condition monitoring and diagnostics of machines: General guidelines](https://www.iso.org/standard/71194.html) — procédures de mise en place d'un programme de surveillance des équipements, analyse de criticité, méthodes de mesure, seuils et examen des résultats. Cette édition a été confirmée par ISO en 2023.
- [ISO 13374-1:2003 — Data processing, communication and presentation](https://www.iso.org/standard/21832.html) — lignes directrices pour le traitement, la communication et la présentation des données de surveillance d'état ; édition confirmée en 2025.
- [NASA — Reliability-Centered Maintenance Guide](https://www.nasa.gov/fred/documents/operations-and-maintenance/) — principes de maintenance centrée sur la fiabilité et sélection des tâches selon le risque et les modes de défaillance.
- La documentation du fabricant de l'actif et du capteur reste la référence prioritaire pour les plages physiques, les consignes de sécurité et les fréquences recommandées.
