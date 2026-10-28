# Corrélation d'événements et RCA automatisée — Expert

> **Mise en contexte :** pendant une panne multisite, le centre de supervision reçoit des centaines d'alertes issues des routeurs, des commutateurs, des sondes applicatives et des outils cloud. Plusieurs alertes décrivent le même symptôme, d'autres signalent des conséquences en cascade, et quelques événements peuvent être sans rapport. Le défi est de regrouper les événements, reconstruire une chronologie, identifier les causes candidates et proposer des tests vérifiables sans confondre corrélation et causalité. Les exemples sont destinés à un environnement de test et ne doivent pas être utilisés comme un moteur de changement automatique sans validation.

## Sommaire

1. Objectifs et concepts
2. Corrélation, causalité et cause racine
3. Qualité des événements et schéma canonique
4. Horodatage, déduplication et fenêtrage
5. Corrélation temporelle et topologique
6. Représenter les dépendances sous forme de graphe
7. Scoring des causes candidates
8. Raisonnement causal et hypothèses concurrentes
9. Architecture d'une RCA automatisée
10. Implémentation Python pédagogique
11. TP : analyser une panne multisite
12. Évaluer les résultats et les erreurs
13. Exploitation, sécurité et gouvernance
14. Diagnostic et dépannage
15. Exercices corrigés
16. Défi final, checklist et références

## 1. Objectifs et concepts

La corrélation d'événements consiste à relier des observations qui semblent partager une origine, un contexte ou une chronologie. Elle sert à réduire le bruit, à former des incidents cohérents et à déterminer les informations les plus utiles à l'investigation. L'analyse de cause racine, souvent désignée par RCA, va plus loin : elle cherche à expliquer pourquoi la dégradation s'est produite et quelles preuves soutiennent l'explication. Une RCA automatisée fiable doit présenter un raisonnement traçable, des alternatives et des limites.

À la fin du cours, vous devez être capable de construire un modèle canonique d'événement, de traiter des événements dupliqués ou tardifs, de créer un graphe de dépendances, d'agréger des signaux temporels et topologiques, de classer plusieurs causes candidates et de mesurer la qualité des résultats. Vous devez surtout distinguer une hypothèse probable d'une cause confirmée. Le système peut accélérer le triage, mais il ne doit pas inventer une certitude lorsque les données sont insuffisantes.

Les usages comprennent le regroupement d'alarmes réseau, la corrélation entre changements de configuration et pertes de connectivité, l'identification de dépendances affectées, l'analyse de pannes DNS ou applicatives, la recherche d'une cause commune à plusieurs sites et l'aide au diagnostic d'incidents cloud. La méthode dépend des données disponibles : un centre de supervision qui ne possède aucun historique de topologie ne peut pas se comporter comme un système qui connaît les relations de dépendance métier en temps réel.

### Vocabulaire

- **Événement** : observation datée décrivant une transition, une anomalie ou un état.
- **Alarme** : événement ayant satisfait une règle de déclenchement ou une condition de notification.
- **Incident** : interruption ou dégradation opérationnelle nécessitant une prise en charge.
- **Corrélation** : relation statistique, temporelle, contextuelle ou topologique entre événements.
- **Cause racine** : facteur à l'origine du mécanisme de défaillance, à distinguer de ses symptômes.
- **Hypothèse candidate** : explication plausible qui reste à vérifier.
- **Dépendance** : relation selon laquelle la disponibilité ou le comportement d'un composant affecte un autre.
- **RCA** : processus de collecte de preuves, de recherche d'hypothèses, de tests et de documentation du mécanisme causal.

## 2. Corrélation, causalité et cause racine

Deux événements qui apparaissent ensemble ne sont pas nécessairement liés par une relation de cause à effet. Le trafic et la température peuvent augmenter simultanément parce que l'activité quotidienne du site a changé. Une hausse d'erreurs peut précéder un incident sans en être la cause. Une alerte sur un serveur peut survenir après une coupure réseau et simplement en être la conséquence. La chronologie fournit des indices, mais elle ne suffit pas seule à prouver la causalité.

### 2.1 Trois niveaux d'affirmation

Il est utile de distinguer :
1. **Observation :** les alertes de trois agences ont commencé dans une fenêtre de deux minutes.
2. **Hypothèse de corrélation :** ces alertes peuvent partager une dépendance commune.
3. **Cause confirmée :** un test discriminant, des preuves de changement et une restauration contrôlée démontrent que la défaillance de cette dépendance explique les symptômes observés.

L'interface doit conserver ces niveaux. Une réponse qui affiche « cause racine : routeur cœur » sans mention de confiance ni de preuve pousse les opérateurs à arrêter l'investigation. Préférez « cause candidate prioritaire : routeur cœur ; preuves : erreurs de voisinage précèdent trois symptômes ; preuve manquante : test indépendant depuis le site D ».

### 2.2 Un exemple de cause commune

Trois applications semblent indépendamment en panne. Un regroupement par application produit trois incidents séparés. En ajoutant la topologie, on découvre que les trois chemins passent par le même lien d'agrégation. Le lien devient une cause candidate commune. Cela ne prouve pas encore que le lien est défaillant : une panne d'alimentation peut toucher plusieurs équipements, un service DNS partagé peut expliquer les symptômes applicatifs, ou une maintenance peut avoir provoqué un comportement attendu. Le graphe améliore le raisonnement mais ne remplace pas les tests.

### 2.3 Symptôme, facteur contributif et cause racine

Un incident peut avoir plusieurs niveaux. Un délai élevé est un symptôme, une file saturée est un mécanisme immédiat et un changement de capacité peut être un facteur contributif. Une cause racine n'est pas toujours unique ; l'incident peut résulter de plusieurs facteurs qui se combinent. Chercher une seule cause coûte que coûte conduit à simplifier abusivement des incidents complexes.

Les rapports doivent préciser le niveau d'explication. « Le lien a perdu sa connectivité » décrit l'effet immédiat. « Le défaut du module optique a provoqué une hausse des erreurs et des pertes » est plus explicatif si l'inspection et les compteurs le confirment. « Le processus de maintenance a permis un déploiement de matériel non qualifié » peut être une cause organisationnelle plus profonde, qui demande une enquête différente.

## 3. Qualité des événements et schéma canonique

Les sources produisent des événements de formes différentes : syslog, traps SNMP, métriques, changements de configuration, traces applicatives, tickets et notifications de cloud. Avant de corréler, il faut normaliser les champs utiles et conserver les détails originaux. La normalisation doit rendre les formats comparables sans inventer d'information qui n'existait pas dans la source.

### 3.1 Schéma d'événement canonique

Un événement canonique peut contenir :
- un identifiant unique ou stable ;
- l'heure de l'événement et l'heure de réception ;
- l'actif, l'interface ou le service concernés ;
- une catégorie et une sévérité ;
- une mesure et son unité éventuelle ;
- le système source et la version du parseur ;
- un identifiant de changement ou d'incident si disponible ;
- l'état de qualité et de complétude des données ;
- la référence vers la charge utile originale conservée selon la politique de rétention.

Le schéma doit accepter les informations absentes. Une absence d'identifiant d'interface ne doit pas provoquer la création d'un champ fictif qui serait ensuite interprété comme une vraie interface. Les inconnues doivent être encodées explicitement et rester visibles pendant la corrélation.

### 3.2 Sévérité et taxonomie

Les systèmes ont souvent des échelles différentes. Un événement « critical » d'un outil peut correspondre à un « major » d'un autre. La taxonomie commune doit être documentée et peut conserver à la fois la sévérité source et la sévérité normalisée. Elle doit également distinguer les classes d'événements : disponibilité, performance, sécurité, changement, capacité, collecte ou diagnostic.

Une taxonomie trop générale réduit l'utilité des regroupements ; une taxonomie trop détaillée crée un catalogue difficile à entretenir. Commencez avec des catégories qui soutiennent des décisions concrètes et faites évoluer le schéma à partir des investigations réelles.

### 3.3 Conserver provenance et qualité

Chaque transformation doit garder la provenance. Si un parseur extrait la cible à partir d'un texte mal formé, la qualité est inférieure à celle d'un identifiant structuré fourni par l'API. Cette différence peut influencer le poids d'une preuve. Une donnée provenant d'un collecteur en panne ou d'un système dont l'horloge est décalée doit être signalée.

La normalisation n'est pas une occasion de supprimer les événements « bizarres ». Un événement inattendu peut révéler un changement de version, un défaut de parsing ou une nouvelle forme de panne. Le pipeline doit mettre les événements illisibles en quarantaine observable, avec compteurs et alertes sur la qualité de la collecte.

## 4. Horodatage, déduplication et fenêtrage

Les événements sont rarement livrés dans l'ordre exact de leur survenue. Les systèmes peuvent avoir des horloges décalées, des files d'attente, des pannes de collecte ou des reprises après interruption. La corrélation doit distinguer l'heure à laquelle le fait s'est produit de celle où le système l'a reçu.

### 4.1 Événement en retard

Si un événement possède une heure de source, une heure de réception et une identité de collecteur, il est possible d'estimer son retard et de détecter des anomalies d'horloge. Lorsque l'heure source est absente ou peu fiable, gardez le degré d'incertitude. Une séquence calculée à partir d'horodatages incorrects peut placer la conséquence avant la cause et orienter tout le diagnostic dans une mauvaise direction.

Les fenêtres de corrélation doivent être choisies selon la dynamique de l'incident. Une perte de connectivité peut produire ses symptômes en quelques secondes, tandis qu'une saturation progressive s'étale sur des heures. Une fenêtre unique pour tous les événements est rarement optimale. Les fenêtres peuvent être spécifiques à une classe et être ajustées par une validation sur les incidents historiques.

### 4.2 Déduplication

Une même panne peut générer des centaines d'alarmes identiques. La déduplication peut utiliser l'actif, le code, l'interface, la condition, une fenêtre et l'identifiant source. Mais elle doit éviter de fusionner deux pannes distinctes qui se répètent après un rétablissement. Il faut donc définir le moment où une alarme s'ouvre, se met à jour et se ferme, ainsi que la durée de silence nécessaire pour considérer un nouvel épisode.

Une empreinte trop simple basée uniquement sur le texte peut fusionner des équipements différents. Une empreinte trop stricte ne reconnaît pas les messages qui diffèrent légèrement. Conservez le compteur de répétition et les premières et dernières occurrences : cette information aide à distinguer un événement ponctuel d'une condition persistante.

### 4.3 Fenêtres, fenêtres glissantes et événements de changement

Une fenêtre fixe regroupe les événements sur des intervalles définis. Une fenêtre glissante recalcule continuellement les relations dans un horizon récent. Les fenêtres événementielles peuvent s'ouvrir lors d'un déclencheur et rester actives jusqu'à un rétablissement confirmé. Le choix dépend de la volumétrie, de la latence admissible et de la capacité du système à traiter les événements tardifs.

Les changements de configuration sont souvent des pivots utiles, mais « changement juste avant panne » n'établit pas automatiquement la causalité. Il faut vérifier la cible, le contenu réel du changement, l'heure d'application, les systèmes affectés et les hypothèses alternatives. Un changement sans rapport peut coïncider avec la panne par hasard, surtout dans une infrastructure qui évolue souvent.

## 5. Corrélation temporelle et topologique

La corrélation temporelle recherche des événements proches dans le temps. La corrélation topologique exploite les relations entre composants. La corrélation contextuelle intègre des attributs partagés : site, version, fournisseur, domaine de routage, service métier ou fenêtre de maintenance. Les meilleures investigations combinent ces dimensions au lieu de s'appuyer sur une seule.

### 5.1 Relations temporelles

Une relation temporelle peut indiquer qu'un événement A précède systématiquement un événement B, ou que plusieurs symptômes apparaissent après un même changement. Les mesures peuvent inclure le délai, la répétition de la séquence et la proportion d'incidents comparables. Il faut définir si le système attend une simultanéité ou un ordre temporel. Une corrélation qui ignore l'ordre peut relier un symptôme à un événement postérieur.

La temporalité est sensible aux événements manquants. Si le signal qui décrit le vrai début de panne n'a pas été collecté, l'algorithme peut attribuer la priorité à un événement secondaire. La chronologie doit montrer les lacunes et permettre à l'opérateur de comparer l'heure source à l'heure de réception.

### 5.2 Relations de topologie

La topologie représente des équipements, liens, interfaces, routes, services, dépendances DNS, applications, alimentations et sites. Un graphe permet de rechercher les ancêtres ou les dépendances partagées par les composants en panne. Les relations doivent être datées et qualifiées : une relation prévue n'est pas nécessairement une relation active à l'instant de l'incident.

~~~mermaid
flowchart TD
  Core[Routeur cœur] --> Agg1[Agrégation A]
  Core --> Agg2[Agrégation B]
  Agg1 --> Site1[Agence 1]
  Agg1 --> Site2[Agence 2]
  Agg2 --> Site3[Agence 3]
  Site1 --> App1[Application paiement]
  Site2 --> App2[Application stock]
  Site3 --> App3[Application métier]
  Core -. dépendance candidate .-> SharedDNS[DNS partagé]
~~~

Dans cette illustration, un incident affectant les trois agences peut conduire à examiner le routeur cœur ou une dépendance partagée. Si seules les applications échouent tandis que les tests réseau passent, le DNS ou une dépendance applicative commune devient une hypothèse importante. Si une seule agence échoue et qu'un seul lien présente des erreurs physiques, l'hypothèse locale gagne du poids.

### 5.3 Score combiné

Un score de cause candidate peut réunir la proximité temporelle, la relation topologique, la sévérité des symptômes, le lien à un changement, la fiabilité des sources et la similarité avec des incidents historiques. Chaque terme doit avoir une définition documentée. Les coefficients peuvent être définis par règle ou appris à partir d'exemples, mais le score doit rester interprétable par l'équipe.

Ne combinez pas aveuglément des nombres qui n'ont pas la même signification. Un score de similarité sémantique n'est pas une probabilité, pas plus qu'un poids de graphe. Si le score final est calibré comme une probabilité, cette calibration doit être testée sur une période indépendante. Sinon, présentez-le comme un rang ou un indice et évitez un pourcentage qui semble plus certain qu'il ne l'est.

## 6. Représenter les dépendances sous forme de graphe

Un graphe permet d'exprimer des relations directionnelles et non directionnelles. Un lien physique peut être représenté comme une relation bidirectionnelle, tandis qu'un service dépend d'un résolveur DNS dans une relation orientée. Un graphe de causalité candidat doit être distingué d'un graphe d'inventaire : une dépendance de service connue n'est pas forcément une preuve qu'elle a causé l'incident.

### 6.1 Types de nœuds et d'arêtes

Les nœuds peuvent représenter des équipements, interfaces, services, collecteurs, configurations, changements et incidents. Les arêtes peuvent représenter « connecte à », « dépend de », « transporte », « héberge », « modifié par » ou « observé par ». Chaque relation devrait porter une source, une date de validité et éventuellement une confiance. Une relation déduite doit être distinguée d'une relation directement enregistrée.

Un graphe détaillé peut devenir coûteux. Établissez des vues adaptées à la question : graphe réseau pour un incident de routage, graphe de service pour une transaction applicative, graphe de changement pour une dégradation post-déploiement. Le système ne doit pas parcourir sans limite tous les nœuds d'une infrastructure gigantesque et présenter des milliers de candidats.

### 6.2 Recherche des ancêtres communs

Pour plusieurs nœuds touchés, rechercher les dépendances communes qui se trouvent sur leurs chemins. Les ancêtres proches constituent des candidats, mais leur présence dans le graphe ne prouve pas qu'ils sont défaillants. Il faut ensuite examiner les états observés du candidat et chercher des événements qui discriminent entre lui et ses voisins.

Une dépendance très centrale sera souvent commune à de nombreux incidents et peut apparaître fréquemment dans les classements. Il faut corriger ce biais en tenant compte de la centralité et de la fréquence normale des événements. Un composant souvent traversé n'est pas automatiquement la cause la plus probable d'une panne particulière.

### 6.3 Topologie temporelle

Les relations doivent refléter l'état du réseau au moment de l'incident. Une migration peut avoir déplacé un service, et le graphe actuel peut être différent de celui du mois précédent. Si l'on attribue une panne passée à une dépendance apparue après l'événement, le diagnostic est invalide. Conservez des versions datées ou un historique de changements de topologie suffisant pour reconstruire l'état passé.

Quand aucune version historique complète n'est disponible, le dossier doit le signaler. Le système peut proposer des hypothèses, mais il doit réduire la confiance accordée aux conclusions qui dépendent d'un graphe incertain.

## 7. Scoring des causes candidates

Le classement doit être conçu pour orienter l'investigation. Un système qui fournit les dix premières hypothèses, leurs preuves et le prochain test le plus utile peut être plus opérationnel qu'un classifieur qui annonce une seule cause. L'opérateur doit pouvoir voir pourquoi une hypothèse est en tête et quelles observations pourraient la faire descendre.

### 7.1 Fonctions de score

Un score élémentaire peut être défini en combinant plusieurs facteurs normalisés :
- proximité temporelle entre le début du candidat et le premier symptôme ;
- correspondance topologique avec les actifs touchés ;
- présence d'un changement dans la fenêtre pertinente ;
- gravité et pertinence des mesures associées ;
- fiabilité, fraîcheur et indépendance des sources ;
- similarité avec des cas historiques dont la cause a été confirmée.

Un facteur ne doit pas être compté plusieurs fois sous des noms différents. Par exemple, plusieurs alarmes provenant du même collecteur défaillant ne sont pas trois preuves indépendantes. La diversité des sources et leur indépendance doivent être représentées dans le score ou dans le résumé de preuve.

### 7.2 Preuves contradictoires

Les éléments qui contredisent une hypothèse doivent rester visibles. Si un lien est candidat mais que des tests depuis plusieurs points confirment son fonctionnement et que la panne suit une erreur DNS, son rang doit diminuer. Ignorer les contre-indices crée un biais de confirmation qui est particulièrement dangereux dans une investigation assistée par IA générative.

### 7.3 Sélection du test suivant

Le meilleur prochain test n'est pas forcément le test le plus facile. Il doit réduire l'incertitude tout en limitant le coût et le risque. Pour départager une panne de lien et une panne DNS, comparer un ping par adresse IP et une résolution de nom depuis le même point peut être très informatif. Pour départager une panne de routeur et une panne d'alimentation, consulter les états des interfaces et les événements matériels peut être plus utile qu'un test applicatif supplémentaire.

Le moteur peut classer les tests en lecture seule, tests actifs avec faible impact, tests nécessitant une approbation et interventions disruptives. Le système doit privilégier les observations non invasives en première intention, puis escalader si la distinction nécessite une intervention plus risquée.

## 8. Raisonnement causal et hypothèses concurrentes

La causalité demande plus que la proximité temporelle. La preuve la plus utile est souvent une combinaison d'ordre temporel, de mécanisme plausible, de mesure directe et de test discriminant. Une intervention contrôlée qui restaure le service peut renforcer une hypothèse, mais elle doit être interprétée prudemment si plusieurs changements ont été réalisés en même temps.

### 8.1 Hypothèses concurrentes

Pour une baisse de connectivité, établir au moins plusieurs explications possibles : panne physique, changement de routage, saturation, défaut DNS, problème de collecte ou incident applicatif. Chaque hypothèse reçoit les preuves favorables, les preuves défavorables et le test qui permettrait de la vérifier. Cette méthode évite que le système se fixe sur la première relation visible.

Le dossier peut être présenté sous forme de tableau :

| Hypothèse | Preuves favorables | Contre-indices | Prochain test |
|---|---|---|---|
| Lien physique dégradé | Erreurs CRC et pertes sur le même port | État physique stable sur un autre instantané | Comparer compteurs et puissance optique |
| Problème DNS | Résolution intermittente, accès IP direct valide | Une seule application touchée | Comparer plusieurs résolveurs |
| Changement de routage | Modifications proches du début d'incident | Chemin secondaire également en échec | Vérifier routes, annonces et historique |
| Collecteur indisponible | Série de métriques interrompue | Les tests actifs échouent aussi | Valider depuis un point indépendant |
| Panne applicative | Réseau fonctionnel et erreur applicative explicite | Plusieurs services indépendants touchés | Comparer traces et dépendances partagées |

Ce tableau n'impose pas une cause. Il aide l'équipe à investir son temps dans les tests les plus discriminants et à conserver une explication alternative lorsque les données ne suffisent pas.

### 8.2 Cause racine ou cause la plus probable

Dans certains incidents, la cause réelle n'est confirmée qu'après intervention. Pendant le diagnostic, la formulation correcte est « cause la plus probable selon les preuves disponibles ». Après la résolution, l'équipe peut mettre à jour le dossier avec le mécanisme confirmé. Les deux états doivent être conservés pour mesurer la qualité des recommandations et éviter de réécrire l'histoire a posteriori.

### 8.3 Éviter les fausses causalités

Un changement récent attire naturellement l'attention, mais l'ordre temporel n'établit pas une causalité. Vérifiez si le changement touche la ressource, si le symptôme était absent auparavant, si des événements similaires surviennent sans ce changement, et si un mécanisme technique explique le résultat. Une comparaison avec des cas non affectés peut aider à estimer si l'événement est spécifique à la panne.

## 9. Architecture d'une RCA automatisée

Une architecture fiable contient les fonctions suivantes : ingestion multi-source, normalisation, déduplication, stockage temporel, inventaire topologique, moteur de corrélation, service de classement des hypothèses, recherche de runbooks, interface de validation et registre d'audit. Les composants peuvent être réunis dans une application au début, mais leurs responsabilités et leurs contrats doivent être séparés.

~~~mermaid
flowchart TD
  A[Syslog, métriques, traces, changements] --> B[Ingestion]
  B --> C[Validation et normalisation]
  C --> D[Déduplication et fenêtres temporelles]
  D --> E[Contexte topologique versionné]
  E --> F[Corrélation et candidats RCA]
  F --> G[Recherche de preuves et tests discriminants]
  G --> H[Rapport avec alternatives]
  H --> I[Validation opérateur]
  I --> J[Résolution et retour terrain]
  J --> K[Historique des incidents confirmés]
  K --> F
  C --> L[Quarantaine des événements invalides]
~~~

### 9.1 Ingestion et résilience

L'ingestion doit gérer les duplications, les retards, les interruptions et les pics de volume. Un mécanisme de reprise évite de perdre silencieusement les événements pendant une panne de collecteur. La priorité des événements doit être explicitée si le système est surchargé : perdre une télémétrie de faible priorité peut être acceptable, perdre les traces d'un changement sur un composant central peut dégrader fortement l'analyse.

Le pipeline conserve une voie d'observation des erreurs de parsing et de la qualité des sources. Il doit être possible de répondre à la question : « avons-nous peu d'alertes parce que le réseau va bien ou parce qu'un collecteur ne fonctionne plus ? ». Cette distinction est fondamentale.

### 9.2 Moteur de corrélation

Le moteur peut combiner règles, fenêtres, graphes et méthodes statistiques. Les règles conviennent aux relations bien établies, tandis que les modèles peuvent classer des séquences plus complexes. Un moteur hybride doit enregistrer quelle méthode a contribué à une hypothèse et ne pas présenter des résultats hétérogènes comme s'ils provenaient d'une seule probabilité calibrée.

L'évaluation doit inclure les incidents déjà connus et des périodes sans incident pour vérifier le bruit généré. Les événements de grande fréquence peuvent dominer la corrélation si leur poids n'est pas contrôlé. Les règles de suppression doivent limiter le bruit sans cacher un changement significatif dans le comportement d'un actif.

### 9.3 Rapport de RCA

Un rapport utile comprend le résumé de l'incident, la chronologie, les actifs touchés, les causes candidates classées, les preuves favorables et défavorables, le prochain test conseillé, les données manquantes et le niveau de confiance. Il cite des identifiants d'événement ou des références consultables plutôt que de présenter un récit sans provenance.

Si un LLM rédige la synthèse, l'application doit contrôler les citations, vérifier que les événements référencés existent et distinguer les faits du résumé généré. Toute commande ou hypothèse produite par le LLM est un contenu à examiner, pas une instruction d'exécution. Les secrets, clés et données non nécessaires doivent être supprimés avant envoi au modèle.

## 10. Implémentation Python pédagogique

Le code ci-dessous montre un classement simple de causes candidates. Il n'établit pas une causalité statistique. Les scores sont heuristiques, destinés à illustrer la combinaison de proximité temporelle et de relation topologique. Dans une application réelle, la qualité et l'indépendance des preuves, les données manquantes et les cas contradictoires doivent être traités plus finement.

~~~python
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class Event:
    event_id: str
    asset: str
    kind: str
    occurred_at: datetime
    severity: int
    source: str


@dataclass(frozen=True)
class Candidate:
    asset: str
    event_time: datetime
    topological_relevance: float
    change_related: bool


def temporal_score(candidate: Candidate, incident_start: datetime) -> float:
    """Score pédagogique décroissant avec le retard du candidat."""
    delta_seconds = abs((incident_start - candidate.event_time).total_seconds())
    hours = delta_seconds / 3600
    return max(0.0, 1.0 - hours / 24.0)


def rank_candidates(
    incident_start: datetime,
    candidates: Iterable[Candidate],
) -> list[tuple[Candidate, float]]:
    ranked = []
    for candidate in candidates:
        if not 0.0 <= candidate.topological_relevance <= 1.0:
            raise ValueError("La pertinence topologique doit être entre 0 et 1")
        score = (
            0.50 * temporal_score(candidate, incident_start)
            + 0.35 * candidate.topological_relevance
            + 0.15 * float(candidate.change_related)
        )
        ranked.append((candidate, score))
    return sorted(ranked, key=lambda item: item[1], reverse=True)


if __name__ == "__main__":
    start = datetime.fromisoformat("2026-09-12T09:30:00")
    candidates = [
        Candidate("core-r1", datetime.fromisoformat("2026-09-12T09:15:00"), 0.9, True),
        Candidate("dns-02", datetime.fromisoformat("2026-09-12T08:50:00"), 0.5, False),
        Candidate("access-sw-7", datetime.fromisoformat("2026-09-12T09:25:00"), 0.3, False),
    ]
    for candidate, score in rank_candidates(start, candidates):
        print(candidate.asset, round(score, 3))
~~~

Ce code ne doit pas piloter un réseau. Il ne contrôle ni la qualité des horloges, ni l'indépendance des sources, ni les contre-indices, ni la vérité de la topologie. Son rôle est d'expliquer comment un classement peut être construit et pourquoi le résultat demeure une hypothèse. En production, les scores devraient être versionnés et évalués sur des incidents dont la cause a été confirmée indépendamment.

### 10.1 Tests à ajouter

Testez les candidats exactement à l'heure de début, à douze heures d'écart et à plus de vingt-quatre heures. Vérifiez la gestion d'une pertinence topologique hors plage, d'une date absente, d'une source non fiable et de candidats identiques. Testez aussi les événements dont l'heure de réception est plus récente que l'heure de source. Un classement ne devrait pas être calculé à partir d'un horodatage incohérent sans signaler cette anomalie.

## 11. TP : analyser une panne multisite

### Scénario

Trois agences signalent des échecs d'accès à une application interne à 09 h 30. Les événements disponibles montrent une hausse de latence, plusieurs erreurs DNS, un changement sur le routeur cœur à 09 h 15 et un épisode de collecte manquante sur une agence. Vous devez produire un rapport de RCA en distinguant observation et hypothèse.

### Étape 1 — Normaliser et vérifier les événements

Attribuez un identifiant à chaque observation, séparez l'heure de survenue de l'heure de réception et notez la source. Vérifiez l'écart d'horloge entre les équipements. Dédupliquez les alarmes identiques sans perdre leur nombre d'occurrences. Marquez la collecte absente comme un état inconnu.

### Étape 2 — Reconstituer la chronologie

Construisez une chronologie avec au minimum les changements, les premières erreurs applicatives, les premiers échecs DNS, les métriques de latence et les tests de connectivité. Affichez les incertitudes temporelles. Ne placez pas un événement reçu tardivement dans la chronologie sur la seule base de son heure de réception si son heure d'origine est disponible.

### Étape 3 — Construire le graphe d'impact

Reliez les trois agences à leurs chemins, aux résolveurs DNS et à l'application. Identifiez les composants communs. Utilisez l'état topologique valable à l'heure de l'incident, pas uniquement la topologie actuelle. Si une partie du graphe est inconnue, la rapporter comme limite de l'analyse.

### Étape 4 — Classer les hypothèses

Hypothèses initiales : changement de routage, panne DNS partagée, problème applicatif, défaut de collecte ou plusieurs incidents distincts. Pour chaque hypothèse, lister les preuves favorables et défavorables. Choisissez un test discriminant à faible risque, tel qu'une résolution DNS et un accès IP direct depuis plusieurs agences.

### Étape 5 — Décider de la prochaine action

Ne modifiez pas automatiquement la route du cœur simplement parce qu'un changement est récent. Vérifiez le diff, les journaux d'application, l'état des voisins et les tests de bout en bout. Si le service est critique ou que la preuve n'est pas concluante, escaladez avec un dossier clair. Le but du TP est une RCA de qualité, pas un changement de configuration.

### Livrables

- un schéma canonique des événements ;
- une chronologie avec données manquantes visibles ;
- un graphe de dépendances ;
- un classement d'au moins trois hypothèses ;
- un test discriminant par hypothèse prioritaire ;
- un rapport qui sépare faits, inférences et inconnues ;
- une liste des éléments à confirmer après résolution.

## 12. Évaluer les résultats et les erreurs

Il faut évaluer la qualité du regroupement d'incidents et la justesse du diagnostic. Le regroupement peut être jugé sur le nombre d'événements pertinents conservés ensemble, les doublons supprimés, les incidents distincts fusionnés par erreur et le délai de création d'un incident utile. La RCA peut être évaluée sur la présence de la cause confirmée parmi les premières hypothèses, le temps de diagnostic et la qualité des preuves rapportées.

Une mesure de rang, comme le taux de causes confirmées en première ou troisième position, peut être plus adaptée qu'une exactitude binaire. Les opérateurs examinent souvent quelques hypothèses plutôt qu'une seule. Cependant, une liste longue qui contient la bonne réponse parmi vingt possibilités ne fournit pas nécessairement une grande valeur opérationnelle.

### 12.1 Mesurer les regroupements

Les faux regroupements fusionnent des incidents indépendants. Ils sont dangereux parce qu'ils peuvent entraîner une action de grande portée alors que seul un sous-ensemble est touché. Les séparations excessives fragmentent un même incident en plusieurs tickets et peuvent masquer une cause commune. Les deux erreurs doivent être mesurées.

Comparez les résultats automatiques avec des incidents étiquetés après investigation. Les labels opérationnels ne sont pas toujours parfaits ; certaines pannes restent ambiguës. Gardez un statut « non concluant » au lieu de forcer chaque dossier en vrai ou faux. Faites revoir un échantillon par des experts qui ne connaissent pas le classement du modèle lorsque c'est possible.

### 12.2 Mesurer l'aide à la décision

Le temps de triage peut diminuer même si le système ne trouve pas toujours immédiatement la cause. Mesurez le temps jusqu'à la première hypothèse utile, le nombre de recherches manuelles, la fréquence des hypothèses erronées, le taux de preuves réellement consultées et la qualité du compte rendu. Incluez des retours qualitatifs des personnes d'astreinte.

N'évaluez pas le système uniquement par le nombre de recommandations acceptées : un opérateur peut accepter trop facilement une explication convaincante. La validation doit vérifier la cause confirmée après résolution et la capacité du système à signaler correctement l'incertitude.

### 12.3 Régression et incidents rares

Construisez un corpus de référence avec des pannes confirmées et des périodes sans incident. Chaque mise à jour de la topologie, de la normalisation ou du modèle doit rejouer ce corpus. Un nouveau parseur peut changer la distribution des événements et modifier les résultats même si le moteur de corrélation n'a pas changé.

Les incidents graves et les cas d'abstention correcte doivent être suivis séparément. Une amélioration moyenne ne doit pas masquer une régression sur un type de panne critique. Après une modification, documentez les cas qui changent de classement et leur impact attendu.

## 13. Exploitation, sécurité et gouvernance

La RCA automatisée traite des informations sensibles : topologie, journaux d'authentification, noms de clients, adresses, configurations et incidents de sécurité. L'accès doit être limité au besoin de connaître, et les données transmises aux services externes doivent être minimisées. Le pipeline doit prévoir la redaction des secrets, les politiques de rétention et la journalisation des accès.

Les droits d'observation et les droits de changement doivent être séparés. Un moteur de corrélation devrait d'abord posséder des droits de lecture. Si un système de recommandation est ensuite relié à l'automatisation, les actions doivent passer par un moteur de politique distinct avec une liste blanche et des contrôles de préconditions. Une conclusion de RCA ne constitue pas une autorisation de corriger automatiquement.

Les rapports générés doivent conserver leurs sources. Un LLM peut aider à synthétiser des événements, mais la récupération de preuves, la validation des citations et la vérification des valeurs doivent être faites par l'application. Les journaux ou les tickets peuvent contenir des instructions malveillantes ; ces textes doivent être traités comme des données non fiables, pas comme des directives qui modifient les règles du système.

### 13.1 Journal d'audit

Conservez l'identifiant d'incident, la liste d'événements sources, les versions de parsing, la version du graphe, la version du moteur, les hypothèses calculées, la décision humaine et la cause finalement confirmée. Ne stockez que les informations nécessaires et protégez le journal contre les modifications non autorisées. L'audit doit permettre de reconstruire pourquoi une cause a été classée en tête à une date donnée.

### 13.2 Revue de la cause après résolution

Après l'incident, comparez la cause retenue et les hypothèses initiales. Notez les signaux qui étaient pertinents, ceux qui étaient trompeurs et ceux qui manquaient. La revue ne doit pas transformer automatiquement l'interprétation d'une seule équipe en vérité incontestable. Lorsque la cause reste incertaine, conservez le niveau d'incertitude afin de ne pas polluer les données d'apprentissage.

## 14. Diagnostic et dépannage

### Les événements sont regroupés en un seul incident géant

Vérifiez la fenêtre temporelle, les identifiants, les dépendances et les critères de déduplication. Les événements très fréquents ou un équipement central peuvent relier artificiellement des incidents sans rapport. Réduisez le périmètre de recherche, introduisez des frontières de service et comparez avec les incidents connus.

### Le système ne relie pas des symptômes identiques

Il peut manquer une normalisation des codes, une cartographie d'actifs ou un traitement des noms de champs. Vérifiez si le même événement est exprimé par plusieurs constructeurs et si les identifiants restent stables après remplacement matériel. N'abaissez pas simplement les seuils de similarité sans mesurer les faux regroupements.

### La cause candidate est toujours le composant le plus central

Une centralité élevée entraîne une fréquence de coïncidence élevée. Corrigez l'effet de la centralité, utilisez des preuves de défaillance directes et comparez les candidats avec des incidents sans impact. Un composant central doit être examiné, mais il ne doit pas gagner systématiquement faute de meilleure mesure.

### Le classement change lorsque des données tardives arrivent

C'est normal si la nouvelle information modifie la chronologie, mais le système doit gérer les mises à jour de dossier sans perdre l'ancien résultat. Conservez la version de chaque classement et indiquez pourquoi il a changé. Si les événements tardifs sont fréquents, ajustez la fenêtre d'attente ou fournissez un résultat provisoire puis un résultat révisé.

### La synthèse générative cite une alarme inexistante

Traitez cela comme une erreur bloquante. Les références d'événements doivent être validées contre le stockage et la synthèse doit être régénérée ou remplacée par un modèle déterministe. Un rapport sans source vérifiable ne doit pas être présenté comme une RCA soutenue par des preuves.

### Le système donne une seule cause même quand les preuves sont faibles

Ajoutez un statut « non concluant », autorisez plusieurs hypothèses et faites apparaître les données manquantes. Une interface qui force une réponse unique encourage une confiance non justifiée. Le système doit pouvoir indiquer que l'investigation nécessite un test ou une intervention humaine.

## Architecture de référence et implémentation guidée

La corrélation d'événements cherche à réduire le bruit et à trouver les dépendances plausibles entre les symptômes. L'analyse de cause racine ajoute une étape supplémentaire : elle doit comparer des hypothèses concurrentes et rechercher les observations qui peuvent les départager. Une proximité temporelle seule ne constitue pas une preuve de causalité.

### Corrélation temporelle et topologique

```mermaid
flowchart TD
  A["Alertes et événements bruts"] --> B["Normaliser les horodatages et identifiants"]
  B --> C["Dédupliquer les répétitions"]
  C --> D["Regrouper dans une fenêtre temporelle"]
  E["Topologie et dépendances"] --> F["Graphe de dépendances versionné"]
  D --> G["Construire des groupes d'événements"]
  F --> G
  G --> H["Générer des hypothèses de cause"]
  H --> I["Ajouter preuves et contre-indices"]
  I --> J{"Cause suffisamment étayée ?"}
  J -- "Non" --> K["Choisir un test discriminant"]
  J -- "Oui" --> L["Présenter la RCA avec incertitude"]
```

### Contrôler les preuves avant de publier la synthèse

```mermaid
sequenceDiagram
  participant E as Moteur de corrélation
  participant G as Graphe d'infrastructure
  participant P as Validateur de preuves
  participant L as LLM de synthèse
  participant O as Opérateur
  E->>G: Demander les dépendances au moment de l'incident
  G-->>E: Chemins possibles et version du graphe
  E->>P: Événements, horodatages et identifiants
  P-->>E: Données valides et contre-indices
  E->>L: Dossier de preuves borné
  L-->>P: Hypothèses et références
  P->>P: Vérifier références et assertions permises
  P-->>O: Synthèse validée ou signalement d'incertitude
```

### Exemple de rapprochement avec fenêtre temporelle

```python
from datetime import datetime, timedelta, timezone

def correlate_events(events, window_seconds=180):
    ordered = sorted(events, key=lambda event: event["timestamp"])
    groups = []
    for event in ordered:
        timestamp = event["timestamp"]
        if timestamp.tzinfo is None:
            raise ValueError("Chaque horodatage doit inclure son fuseau")
        timestamp = timestamp.astimezone(timezone.utc)

        if not groups:
            groups.append({"start": timestamp, "events": [event]})
            continue

        current = groups[-1]
        if (timestamp - current["start"]) <= timedelta(seconds=window_seconds):
            current["events"].append(event)
        else:
            groups.append({"start": timestamp, "events": [event]})
    return groups
```

Cette fonction démontre un regroupement temporel élémentaire, pas un moteur de RCA complet. En production, chaque événement doit être dédupliqué, les événements en retard doivent être gérés explicitement, les sources doivent être pondérées selon leur qualité et la fenêtre doit être liée au service étudié. Un seul groupe peut contenir plusieurs incidents indépendants.

### Travaux pratiques — mêmes symptômes, causes différentes

Construis un petit jeu contenant : une panne d'alimentation qui affecte un commutateur et ses descendants, une panne locale d'interface, un changement de routage, une alerte répétée et un événement arrivé en retard. Compare la corrélation temporelle seule à une corrélation enrichie par la topologie. Vérifie qu'une dépendance absente du graphe ne peut pas être présentée comme établie.

Pour chaque hypothèse de cause, impose un schéma comportant les événements favorables, les contre-indices, les dépendances utilisées, l'heure d'apparition, les inconnues et le test recommandé. L'arrivée tardive d'un événement doit pouvoir reclasser une hypothèse sans effacer l'historique des décisions précédentes. Ne force jamais un score unique à masquer une incertitude importante.

### Critères d'acceptation

Le système trace la version du graphe utilisée, conserve les événements sources, distingue corrélation et causalité et vérifie les identifiants de preuve avant d'afficher la synthèse. Il est préférable de proposer une investigation ciblée plutôt que d'annoncer une cause non démontrée.

## 15. Exercices corrigés

### Exercice 1 — Corrélation temporelle

Un changement survient cinq minutes avant une panne. Est-ce suffisant pour l'identifier comme cause racine ?

**Correction :** non. Il faut vérifier que le changement concerne les composants touchés, examiner le contenu réellement appliqué, chercher des preuves de mécanisme et tester des hypothèses concurrentes. La proximité temporelle est un indice, pas une preuve de causalité.

### Exercice 2 — Dépendance partagée

Quatre applications tombent simultanément en échec alors que leurs serveurs sont différents. Quelle stratégie est la plus utile en premier ?

**Correction :** rechercher une dépendance commune dans le graphe — réseau, DNS, identité, base partagée ou service d'authentification — puis la tester depuis plusieurs points. Ne pas conclure à une cause unique avant d'avoir vérifié que les symptômes suivent réellement cette dépendance.

### Exercice 3 — Événement tardif

Un événement de changement arrive vingt minutes après le début de l'incident, mais son heure source indique une application cinq minutes avant le début. Quelle heure doit être utilisée ?

**Correction :** l'heure source peut servir à reconstruire la chronologie si elle est fiable, tandis que l'heure de réception sert à mesurer le retard. Il faut noter la qualité de l'horloge et corroborer l'heure avec le journal de changement. Les deux timestamps doivent être conservés.

### Exercice 4 — Déduplication excessive

Le système fusionne deux pannes du même routeur à deux heures d'écart en un seul incident, alors qu'une première panne avait été résolue entre-temps.

**Correction :** intégrer l'état de l'incident, la période de rétablissement et la durée de silence dans la règle de déduplication. Une même identité d'actif ne signifie pas qu'il s'agit du même épisode. Conserver les occurrences et leurs états est indispensable.

### Exercice 5 — RCA générative

Un LLM produit un récit clair et une commande de correction, mais il cite des références d'événements introuvables.

**Correction :** rejeter la synthèse, vérifier les références par code et reconstruire le rapport à partir des preuves connues. La commande n'est pas exécutée. Le cas doit être ajouté au corpus de tests adverses.

## Atelier approfondi — corréler les événements sans masquer les causes

Cet atelier traite un problème d'exploitation avancé : comment transformer un grand volume d'événements partiellement fiables en une investigation structurée qui aide réellement à comprendre une panne ? Le système doit éliminer les doublons, repérer les symptômes liés, relier les éléments à la topologie connue au moment concerné, classer des causes candidates et identifier la prochaine vérification qui permettrait de les départager. Il ne doit pas fabriquer une certitude quand les données sont contradictoires ou absentes.

Le scénario principal est une dégradation multisite. Des alertes de latence, de perte, d'état de session et d'indisponibilité applicative arrivent de sources différentes. Certaines sont des conséquences d'un même changement ; d'autres sont des incidents indépendants apparus dans la même période. Le moteur reçoit également des événements tardifs, des changements d'inventaire et des indicateurs de qualité. L'objectif est de restituer une histoire vérifiable plutôt que de produire une explication séduisante mais invérifiable.

### 1. Définir l'unité d'analyse avant de corréler

Trois objets doivent être séparés. Un événement est un fait horodaté provenant d'une source, avec sa cible et sa provenance. Un symptôme est une interprétation fonctionnelle d'un ou plusieurs événements, par exemple « perte de connectivité entre le site A et le service B ». Un incident est un dossier opérationnel qui regroupe les symptômes et les événements jugés liés. Mélanger ces niveaux conduit à des erreurs : une notification répétée est parfois traitée comme un incident distinct, tandis que deux incidents simultanés sont fusionnés parce qu'ils touchent le même service.

L'unité de corrélation dépend de la question posée. Un regroupement des alarmes de port peut être utile pour comprendre une panne locale ; une investigation du service doit considérer les dépendances qui relient le port à un chemin applicatif. Il n'existe pas nécessairement un seul regroupement correct pour tous les consommateurs. Le centre de supervision peut voir un incident parent et plusieurs incidents enfants, alors qu'une équipe applicative ne voit que les symptômes qui affectent son service.

```mermaid
flowchart TD
    A["Événements bruts"] --> B["Normalisation"]
    B --> C["Déduplication"]
    C --> D["Regroupement en symptômes"]
    D --> E["Corrélation et graphe de preuves"]
    E --> F["Incidents candidats"]
    F --> G["Revue et décision opérationnelle"]
```

Définissez une politique de séparation qui précise ce qui constitue deux incidents distincts. Des symptômes peuvent être regroupés si leur cible, leur dépendance, leur chronologie et leur comportement sont compatibles. Ils ne doivent pas être fusionnés uniquement parce qu'ils partagent un libellé ou une proximité temporelle. Une cause commune reste une hypothèse jusqu'à ce que des preuves suffisantes la soutiennent. Les changements planifiés, les pannes de collecte et les alertes de performance doivent conserver leur nature afin de ne pas devenir un incident de performance artificiel.

Un dossier d'incident doit pouvoir contenir plusieurs hypothèses concurrentes. Il peut aussi rester temporairement sans cause prioritaire. Le classement « cause probable » n'est pas une propriété immuable : il doit évoluer lorsque des événements tardifs, des tests ou des informations de topologie sont ajoutés. Gardez les anciens états du classement pour que l'enquête puisse expliquer comment l'interprétation a changé.

### 2. Définir un contrat d'événement canonique

Les sources ont souvent des formats différents : compteur, message système, alarme SNMP, notification gNMI, trace distribuée, journal applicatif ou changement d'inventaire. Avant toute corrélation, définissez un contrat commun qui ne détruit pas le contexte d'origine. Chaque événement devrait porter un identifiant stable, un type, une sévérité source, une cible ou un ensemble de cibles, l'heure de l'événement, l'heure de réception, la source, la provenance, une indication de qualité et une référence au contenu source conservé.

La normalisation doit préserver le message original ou une référence fiable vers lui. Le moteur ne doit pas perdre la possibilité de vérifier qu'un événement normalisé représente correctement la donnée d'origine. Les identifiants source peuvent être réutilisés, manquer ou changer après redémarrage ; prévoyez un identifiant interne distinct, tout en conservant la clé source lorsqu'elle existe. L'identité interne ne doit pas être prise pour une preuve d'unicité absolue si des producteurs dupliquent les données.

```mermaid
flowchart TD
    A["Source hétérogène"] --> B["Parser et valider"]
    B --> C["Préserver la provenance"]
    C --> D["Normaliser temps, cible et type"]
    D --> E["Attribuer un identifiant interne"]
    E --> F{"Contrat valide ?"}
    F -- "Non" --> G["Quarantaine et métrique d'erreur"]
    F -- "Oui" --> H["Événement canonique"]
    H --> I["Corrélation"]
```

Les valeurs absentes doivent être distinguées des valeurs nulles, des valeurs invalides et des valeurs par défaut. Un équipement qui ne publie plus un compteur ne publie pas un compteur égal à zéro. De même, un événement dont le timestamp source manque ne doit pas être horodaté rétroactivement comme si l'heure de réception était l'heure réelle de la panne. Une valeur de remplacement peut parfois être utile, mais le moteur doit conserver l'indication qu'il s'agit d'une estimation.

La sévérité source doit aussi rester distincte de la priorité calculée par la corrélation. Une alarme de faible sévérité peut être très informative si elle est le premier événement dans une chaîne de dépendances ; une alarme critique peut être secondaire si elle décrit la conséquence attendue d'une coupure déjà identifiée. Conservez la classification originale, ajoutez les attributs dérivés et versionnez la règle de priorité.

### 3. Gérer trois notions de temps

Les moteurs de corrélation doivent distinguer au moins l'heure de l'événement, l'heure d'ingestion et l'heure de traitement. L'heure de l'événement décrit le moment déclaré par la source. L'heure d'ingestion décrit l'arrivée dans la plateforme. L'heure de traitement indique quand le moteur a évalué l'événement. Ces temps peuvent diverger lorsqu'un équipement est mal synchronisé, qu'un collecteur est déconnecté ou qu'une file accumule du retard.

Le temps de l'événement est utile pour reconstruire la séquence supposée de la panne, mais sa fiabilité dépend de la source et de l'horloge. Le temps d'ingestion permet de mesurer le retard. Le temps de traitement explique la charge du moteur et la latence interne. Si l'on remplace tous ces champs par un seul timestamp, on ne peut plus distinguer un incident réel d'un événement reçu en retard.

```mermaid
sequenceDiagram
    participant S as Source
    participant I as Ingestion
    participant Q as File
    participant C as Corrélateur
    S->>I: Événement et heure source
    Note over I: Enregistrer heure de réception
    I->>Q: Événement normalisé
    Note over Q: Mesurer l'attente
    Q->>C: Événement livré
    Note over C: Enregistrer heure de traitement
    C->>C: Recalculer chronologie et retard
```

Choisissez une politique pour les événements tardifs. Une fenêtre d'attente peut retarder la publication d'un incident afin de recevoir davantage de données ; elle améliore parfois la qualité du regroupement, mais augmente le délai d'alerte. Une autre approche publie une hypothèse rapidement puis la réévalue lorsque des données arrivent. Cette seconde option donne une réponse précoce, mais l'interface doit montrer qu'une conclusion est provisoire et conserver l'évolution du dossier.

Ne supposez pas que les timestamps de plusieurs équipements sont directement comparables. La dérive d'horloge, les fuseaux horaires et les résolutions différentes peuvent modifier l'ordre apparent. Utilisez l'heure UTC selon une convention documentée et surveillez l'état de synchronisation lorsqu'il est disponible. En présence d'une incertitude temporelle importante, le moteur doit diminuer la confiance dans une relation d'ordre plutôt que décider qu'un événement est définitivement antérieur à un autre.

```mermaid
flowchart TD
    A["Événement tardif"] --> B["Conserver heure source et réception"]
    B --> C["Calculer retard et incertitude"]
    C --> D["Relire incident candidat"]
    D --> E{"Relations temporelles changées ?"}
    E -- "Non" --> F["Ajouter la preuve au dossier"]
    E -- "Oui" --> G["Recalculer le classement"]
    F --> H["Publier mise à jour traçable"]
    G --> H
```

### 4. Construire un graphe de dépendances temporel

Un graphe de dépendances représente les relations possibles entre les composants : interfaces, liens, routeurs, services, zones cloud, bases de données ou applications. Les nœuds décrivent des actifs ou fonctions ; les arêtes indiquent une dépendance, une relation physique, une relation de routage ou une relation de service. La direction des arêtes compte. Un service peut dépendre d'un routeur, mais la défaillance du service ne prouve pas que le routeur dépend du service.

Le graphe doit représenter les faits connus à l'instant étudié. Une topologie actuelle peut ne pas être celle qui existait lors de l'incident. Les changements de configuration, migrations, déplacements d'actifs et mises à jour d'inventaire doivent être horodatés. Si la topologie historique est inconnue, signalez cette limite. Une corrélation effectuée sur une topologie anachronique peut accuser un composant qui n'était pas sur le chemin au moment de la panne.

```mermaid
flowchart TD
    A["Service métier"] --> B["Service applicatif"]
    B --> C["Équilibreur"]
    C --> D["Lien WAN"]
    D --> E["Routeur de site"]
    E --> F["Interface physique"]
    G["Collecteur de télémétrie"] -. "observe" .-> D
    H["Pipeline de déploiement"] -. "modifie" .-> E
```

Toutes les arêtes ne représentent pas le même type de preuve. Une dépendance déclarée dans l'inventaire est une information de configuration. Une relation observée pendant une requête peut venir d'une trace distribuée. Une relation temporelle entre deux alarmes est une association statistique. Conservez le type, la source, l'heure de validité et le niveau de confiance de chaque arête. Si vous transformez toutes les relations en simples connexions, le moteur peut confondre une dépendance certaine avec une hypothèse issue de quelques coïncidences.

La centralité d'un nœud peut aider à comprendre combien de services il relie, mais ne constitue pas une preuve de cause racine. Les composants centraux sont souvent plus surveillés et produisent davantage d'événements. Le moteur doit comparer la centralité à d'autres signaux, tels que l'ordre temporel, les changements récents, les pertes observées, les tests de connectivité et les composants qui continuent de fonctionner normalement.

### 5. Combiner dépendance, temps et symptômes

Une cause candidate devrait être soutenue par plusieurs dimensions de preuve : proximité temporelle, dépendance topologique pertinente, cohérence des symptômes, changement récent, mesure directe et absence de contradiction majeure. Le système peut convertir ces éléments en un score ordonné, mais ne doit pas présenter ce score comme une probabilité sans calibration spécifique. Un score de 0,8 issu d'une somme de règles n'a pas automatiquement le sens de « 80 % de chances que cette cause soit vraie ».

Une approche utile consiste à calculer des contributions séparées plutôt qu'un score opaque unique. Par exemple, conserver les composantes temporelle, topologique, statistique et de changement permet de voir pourquoi un candidat arrive en tête. Pondérez les contributions selon l'objectif et testez l'effet de chaque pondération. Si le score favorise toujours le composant le plus central, la corrélation ne fait que reproduire la topologie sans identifier de cause.

```mermaid
flowchart TD
    A["Incident candidat"] --> B["Évaluer ordre temporel"]
    A --> C["Évaluer dépendances"]
    A --> D["Évaluer cohérence des symptômes"]
    A --> E["Chercher changements récents"]
    A --> F["Examiner preuves contraires"]
    B --> G["Contributions explicites"]
    C --> G
    D --> G
    E --> G
    F --> H["Ajuster ou déclasser le candidat"]
    G --> I["Classer les hypothèses"]
    H --> I
    I --> J["Proposer le test discriminant"]
```

Exemple : trois sites perdent le même service quelques secondes après un changement de politique sur un routeur commun. La relation temporelle et la dépendance topologique soutiennent cette hypothèse. Mais si un site conserve une connectivité directe vers le même routeur et que son chemin a changé auparavant, le modèle doit examiner une cause alternative. Les symptômes partagés donnent une piste, non une conclusion automatique.

L'absence d'événement ne doit pas être traitée comme une preuve négative lorsqu'un capteur est muet. Le fait qu'aucune alarme de port ne soit reçue peut indiquer que le port est sain, mais aussi que la source ne publie plus. Une preuve contradictoire n'a de valeur que si la couverture de surveillance était suffisante durant la période. La disponibilité, la qualité et le délai de chaque source doivent accompagner l'interprétation de ses signaux.

### 6. Dédupliquer sans effacer les transitions

La déduplication réduit les alertes répétées, mais une règle trop agressive peut supprimer la transition utile entre un état dégradé et un état rétabli. Un événement identique en texte n'est pas nécessairement le même phénomène : il peut concerner une autre cible, une autre période ou une autre version de configuration. À l'inverse, deux messages formulés différemment peuvent décrire le même état.

Définissez une clé de déduplication à partir de propriétés sémantiques : cible stable, type d'événement, attributs significatifs, fenêtre temporelle et contexte. Les champs volatils, tels qu'un identifiant de requête ou l'heure d'ingestion, ne devraient pas créer une nouvelle identité à chaque message. Les changements de sévérité, l'apparition d'une preuve indépendante ou le retour à la normale doivent être représentés comme des mises à jour du cycle de vie et non éliminés avec les doublons.

```mermaid
stateDiagram-v2
    [*] --> Open: premier symptôme
    Open --> Enriched: nouvelle preuve compatible
    Enriched --> Escalated: impact augmente
    Open --> Recovering: conditions de retour vraies
    Enriched --> Recovering: conditions de retour vraies
    Escalated --> Recovering: service en reprise
    Recovering --> Closed: stabilité confirmée
    Recovering --> Open: réapparition significative
    Closed --> Open: nouvel épisode après clôture
```

Une fenêtre de regroupement doit être calibrée selon le type de signal. Quelques secondes peuvent être adaptées à une rafale de messages réseau, alors qu'un événement applicatif peut avoir des symptômes étalés dans le temps. Une fenêtre trop large mélange des pannes séparées ; une fenêtre trop courte crée une multitude d'incidents pour une même perturbation. Évaluez les règles sur des dossiers historiques et conservez les événements bruts pour pouvoir reconstituer le regroupement.

Les transitions de récupération méritent autant d'attention que les déclenchements. Pour conclure un incident, vérifiez que les mesures reviennent dans une plage acceptable pendant une période définie, que la couverture est suffisante et qu'aucun symptôme connexe ne reste actif. Une alarme de fin envoyée par une source ne prouve pas à elle seule que le service est sain. Gardez un état de récupération lorsque les données sont contradictoires ou trop peu nombreuses.

### 7. Gérer les événements tardifs, dupliqués et hors ordre

Les systèmes de messagerie peuvent livrer un événement plusieurs fois, après un délai ou dans un ordre différent de celui de sa création. Le corrélateur doit être conçu pour ces cas plutôt que d'assumer une livraison unique et strictement ordonnée. Un événement ancien peut arriver après la clôture et remettre en cause la cause retenue. Le système doit le rattacher au dossier pertinent, recalculer si nécessaire et préserver la décision originale ainsi que sa révision.

Définissez un horizon de correction tardive. Les événements reçus dans cet horizon peuvent déclencher un recalcul automatique limité. Les événements plus anciens peuvent alimenter un rapport de qualité ou rouvrir une investigation suivant la criticité. L'horizon n'efface pas les données ; il détermine combien de temps le classement temps réel peut changer sans revue. Pour les incidents critiques, une information tardive importante doit rester visible même après la fin de la fenêtre habituelle.

```mermaid
flowchart TD
    A["Message reçu"] --> B["Vérifier clé d'événement"]
    B --> C{"Déjà connu ?"}
    C -- "Oui" --> D["Actualiser statistiques de duplication"]
    C -- "Non" --> E["Évaluer timestamp et retard"]
    E --> F{"Dans l'horizon de correction ?"}
    F -- "Oui" --> G["Mettre à jour chronologie et candidats"]
    F -- "Non" --> H["Conserver et marquer comme tardif"]
    G --> I["Réviser le dossier sans effacer l'historique"]
    H --> J["Révision selon criticité"]
```

La gestion des événements tardifs doit être observable. Mesurez leur proportion par source, le retard médian et les percentiles élevés, ainsi que la part des dossiers dont le classement change après arrivée tardive. Une source régulièrement tardive peut nécessiter une politique spécifique, mais ne doit pas bénéficier d'un traitement privilégié qui masque son défaut. La qualité temporelle peut aussi servir à décider si l'on attend davantage avant de déclarer une cause probable.

Les déduplications et recalculs doivent être idempotents. Rejouer le même lot ne devrait pas faire gonfler le nombre d'incidents, répéter les notifications ou changer le classement sans nouvelle preuve. Conservez l'identifiant du lot, la version de la règle et l'état antérieur. Le rejeu est utile pour corriger un défaut de corrélation, mais il doit être distingué de la production normale afin de ne pas déclencher les mêmes actions opérationnelles.

### 8. Comparer des hypothèses causales concurrentes

Une analyse de cause racine ne devrait pas commencer par une hypothèse unique et chercher seulement les éléments qui la confirment. Au moins deux ou trois hypothèses plausibles doivent être formulées quand les faits le permettent. Pour une panne multisite, les possibilités peuvent inclure un lien partagé, un changement d'itinéraire, une défaillance de service applicatif, un défaut de collecte ou plusieurs incidents indépendants. Chaque hypothèse doit préciser les observations attendues si elle est vraie et les observations qui la rendraient moins probable.

Une table d'hypothèses oblige à rendre les raisonnements explicites. Pour chaque cause, conservez les preuves favorables, les preuves défavorables, les données manquantes, le niveau de confiance et le prochain test discriminant. Les contributions doivent rester liées aux sources d'origine. Le classement est une aide au triage, pas un substitut à l'enquête technique.

```mermaid
flowchart LR
    A["Symptômes observés"] --> B["Hypothèse A : dépendance partagée"]
    A --> C["Hypothèse B : changement récent"]
    A --> D["Hypothèse C : collecte défaillante"]
    B --> E["Prédictions vérifiables"]
    C --> F["Prédictions vérifiables"]
    D --> G["Prédictions vérifiables"]
    E --> H["Test discriminant"]
    F --> H
    G --> H
    H --> I["Réviser les hypothèses"]
```

Le prochain test doit maximiser l'information utile tout en restant proportionné au risque et au coût. Une requête en lecture sur un état de route peut être préférable à un changement actif ; un test depuis un seul point peut être insuffisant si plusieurs chemins sont concernés. Pensez à la couverture de chaque test : quelles hypothèses peuvent-il éliminer, quelles conditions doivent être vraies pour l'interpréter, et que conclure si le test échoue lui-même ?

La causalité exige une prudence particulière avec les données observées. Le fait que deux phénomènes évoluent ensemble ne démontre pas que l'un cause l'autre. Une variable tierce peut expliquer les deux, ou les horodatages peuvent être trop imprécis pour déterminer l'ordre. Une intervention contrôlée peut fournir davantage de preuves, mais elle peut être dangereuse en production. Utilisez les historiques de changement, les chemins réellement traversés, les mesures indépendantes et les résultats de tests pour affiner les hypothèses ; mentionnez les limites qui demeurent.

### 9. Calibrer les scores de corrélation et l'incertitude

Un moteur peut attribuer un score à chaque incident candidat à partir de la proximité temporelle, du nombre de symptômes expliqués, de la dépendance topologique, des changements récents et de la qualité des sources. Les caractéristiques doivent être mises à une échelle compréhensible. Un score composé doit montrer la contribution des composants ; sinon, un opérateur risque de prendre un rang relatif pour une probabilité absolue.

Les scores peuvent être utilisés pour classer les investigations et choisir une prochaine action. Ils ne doivent pas être utilisés sans calibration pour annoncer une cause certaine. Si une valeur est présentée comme une probabilité, vérifiez cette interprétation sur des incidents annotés qui n'ont pas servi à construire les règles. Évaluez la calibration par catégorie, car les événements réseau, applicatifs et de plateforme peuvent avoir des distributions et des taux de faux positifs très différents.

```mermaid
flowchart TD
    A["Candidats causaux"] --> B["Contributions temporelles"]
    A --> C["Contributions topologiques"]
    A --> D["Changements et mesures directes"]
    A --> E["Qualité et preuves contraires"]
    B --> F["Score explicable et rang"]
    C --> F
    D --> F
    E --> G["Pénalité, abstention ou faible confiance"]
    F --> H["Classement des candidats"]
    G --> H
    H --> I["Choisir l'investigation suivante"]
```

L'incertitude peut venir de plusieurs sources : capteur déconnecté, historique incomplet, topologie périmée, labels contradictoires, nouveau comportement ou hypothèses proches en score. Le système doit pouvoir déclarer qu'aucune cause ne se distingue suffisamment. Un résultat « plusieurs hypothèses restent plausibles » est plus utile qu'une cause racine arbitraire. La confiance ne doit pas augmenter simplement parce que plus d'événements dupliqués se rapportent à la même source.

Le score doit aussi être robuste au volume d'alertes. Une cause candidate associée à cent messages répétés d'un même équipement ne doit pas obtenir cent fois plus de poids qu'une preuve indépendante d'une autre source. Agrégez les événements corrélés, estimez leur indépendance et évitez de compter plusieurs dérivés du même signal comme autant de confirmations. Cette précaution limite le biais lié à la densité de surveillance.

### 10. Intégrer traces, métriques, logs et changements

Les métriques décrivent des séries quantifiées dans le temps. Les logs enregistrent des événements textuels ou structurés. Les traces distribuées relient les opérations au fil d'un parcours applicatif. Les événements de changement indiquent les modifications d'état ou de configuration. Ces sources se complètent, mais ne possèdent ni la même granularité ni la même qualité temporelle. Le corrélateur doit les rapprocher en conservant leur nature.

Une trace peut montrer qu'une requête attend longtemps sur une dépendance ; une métrique peut indiquer que la latence globale s'est dégradée ; un log peut préciser une erreur ; un événement de déploiement peut expliquer le début de la perturbation. L'association entre trace et métrique dépend de clés de service et de fenêtres temporelles cohérentes. Lorsque les identifiants de corrélation manquent, utilisez des indices prudents et signalez leur niveau de confiance plutôt que de prétendre suivre exactement la même requête.

```mermaid
flowchart TD
    A["Métriques"] --> E["Contexte commun"]
    B["Logs structurés"] --> E
    C["Traces distribuées"] --> E
    D["Événements de changement"] --> E
    E --> F["Alignement temporel"]
    F --> G["Relations explicites et provenance"]
    G --> H["Hypothèses de cause"]
    H --> I["Vérification par source indépendante"]
```

L'instrumentation n'est pas uniforme. Certains services n'ont pas de traces distribuées complètes ; certaines requêtes ne portent pas de contexte de propagation ; certains équipements réseau ne peuvent pas exposer les mêmes dimensions que les applications. Le moteur doit supporter les champs manquants et distinguer « aucune trace trouvée » de « ce service n'est pas instrumenté ». Sinon, il privilégiera systématiquement les composants les mieux instrumentés et ignorera les systèmes dont les signaux sont plus rares.

Les changements constituent un élément fort du contexte, mais leur proximité temporelle n'est pas une preuve définitive. Une configuration peut être déployée sans affecter le chemin concerné, ou une panne peut coïncider avec un changement indépendant. Pour évaluer le lien, vérifiez la cible, le périmètre, l'heure d'application, l'état avant/après et les symptômes attendus. Si le plan a été exécuté par une automatisation, utilisez l'identifiant de workflow et ses postconditions pour relier l'opération à l'incident.

### 11. Évaluer le regroupement et l'aide au diagnostic

Les indicateurs de performance ne doivent pas se limiter à la précision de classification d'un événement. Pour la corrélation, il faut évaluer si les événements d'un même incident sont regroupés ensemble, si des incidents distincts restent séparés, si le premier signal pertinent est conservé et si le regroupement facilite l'investigation. Des labels d'incidents imparfaits peuvent néanmoins être utiles, à condition de mesurer leurs limites et de ne pas les traiter comme une référence absolue.

Suivez les regroupements incorrects, les incidents trop fragmentés, les incidents géants, le nombre d'alertes par dossier, le délai avant première hypothèse, le nombre de candidats proposés et la proportion de dossiers pour lesquels l'équipe a pu identifier une cause. Mesurez les résultats par service, source et criticité. Un moteur peut sembler performant en moyenne tout en échouant systématiquement sur un type de topologie ou sur les événements provenant d'un système peu fiable.

```mermaid
flowchart TD
    A["Dossiers historiques annotés"] --> B["Exécuter ancienne et nouvelle règle"]
    B --> C["Comparer regroupements"]
    C --> D["Mesurer fragmentation"]
    C --> E["Mesurer fusion d'incidents distincts"]
    C --> F["Mesurer délai de première hypothèse"]
    D --> G["Revue qualitative"]
    E --> G
    F --> G
    G --> H["Accepter, ajuster ou rejeter la règle"]
```

Les métriques doivent être interprétées avec soin. Un regroupement très large réduit le nombre d'incidents mais peut les rendre inutilisables. Un regroupement très fin donne des dossiers simples, mais oblige l'équipe à reconstituer les dépendances manuellement. Les objectifs doivent tenir compte du temps de triage, du taux de dossiers rouverts, de la qualité de la cause proposée et de la capacité des opérateurs à confirmer ou contester l'explication.

Créez un corpus de régression comprenant des incidents bien documentés, des cas ambigus, des événements tardifs, des données manquantes, des changements planifiés et des pannes simultanées mais indépendantes. Chaque changement des règles doit être testé sur ce corpus. Quand une amélioration est faite, enregistrez les cas qui s'améliorent et ceux qui régressent, ainsi que la raison pour laquelle la modification est acceptée.

### 12. Gérer la synthèse générative sans inventer des preuves

Un modèle de langage peut résumer une chronologie, comparer les hypothèses et formuler les prochaines vérifications. Il ne doit pas inventer une alarme, compléter un champ absent par intuition ni présenter une corrélation comme une causalité démontrée. La synthèse doit s'appuyer sur un ensemble de faits structurés et conserver des références vers chaque élément cité. Les contenus provenant de logs ou de tickets sont des données non fiables ; ils ne doivent pas être traités comme des instructions qui modifient la politique du système.

La sortie devrait distinguer « observé », « inféré » et « à vérifier ». Une phrase indiquant qu'un redémarrage a précédé la perte de service devrait citer un événement de redémarrage et un événement de perte avec leurs horodatages et leurs sources. Une phrase qui dit que le redémarrage a causé la perte doit être formulée comme une hypothèse, à moins que des preuves suffisantes ne soient disponibles. L'interface devrait permettre de consulter les événements sources sans perdre le dossier résumé.

```mermaid
flowchart TD
    A["Dossier structuré et preuves"] --> B["Construire contexte autorisé"]
    B --> C["Générer synthèse avec références"]
    C --> D["Vérifier chaque affirmation"]
    D --> E{"Toutes les affirmations sont-elles appuyées ?"}
    E -- "Non" --> F["Retirer ou reformuler comme hypothèse"]
    E -- "Oui" --> G["Publier avec limites et confiance"]
    F --> D
```

Une vérification de synthèse peut contrôler que les identifiants cités existent dans le dossier, que les timestamps correspondent, que les noms de cibles sont exacts et que les causes sont bien étiquetées comme hypothèses ou conclusions. Ce contrôle ne garantit pas qu'une interprétation est correcte, mais il élimine certaines hallucinations factuelles. Une revue humaine reste nécessaire pour les décisions à haut impact.

La synthèse doit également reconnaître quand le dossier est trop incomplet. Si aucun événement ne précise l'état d'un composant et que la source n'est pas instrumentée, il faut annoncer cette limite plutôt que déduire un état normal. Un système honnête peut proposer une requête de diagnostic ou une collecte supplémentaire ; il ne doit pas remplir les blancs pour produire un résumé apparemment fluide.

### 13. Gouverner les changements du moteur de corrélation

Le moteur combine des règles, des modèles, une topologie et des paramètres de fenêtrage. Une modification de l'un de ces éléments peut changer les regroupements et les priorités. Versionnez les règles, les poids, les politiques d'événements tardifs, les modèles de graphe et les seuils. Conservez assez d'information pour reproduire un incident antérieur et expliquer pourquoi la nouvelle version classe différemment une cause candidate.

La promotion d'une nouvelle version doit s'appuyer sur un corpus de régression, une comparaison en mode observation et un déploiement progressif. Il est préférable d'exécuter l'ancienne et la nouvelle version en parallèle sur un échantillon, puis de mesurer les différences. Évitez que deux moteurs publient chacun des notifications d'action : seul le moteur désigné comme actif doit avoir le droit de déclencher les workflows.

```mermaid
flowchart LR
    A["Règle ou modèle modifié"] --> B["Tests sur corpus figé"]
    B --> C["Comparaison en observation"]
    C --> D["Revue des différences"]
    D --> E{"Régressions acceptables ?"}
    E -- "Non" --> F["Corriger ou abandonner"]
    E -- "Oui" --> G["Déployer sur périmètre pilote"]
    G --> H["Surveiller qualité des regroupements"]
    H --> I{"Objectifs maintenus ?"}
    I -- "Non" --> J["Retour à la version précédente"]
    I -- "Oui" --> K["Promotion contrôlée"]
```

Les changements de topologie doivent aussi être versionnés. Le graphe utilisé pour une corrélation doit être identifiable et valide pour l'instant concerné. Si l'inventaire courant remplace l'historique, une enquête réexécutée plus tard peut produire une cause différente sans que les données sources aient changé. La reconstitution historique doit utiliser les versions de dépendances et les changements qui existaient à l'époque, ou signaler qu'une reproduction exacte est impossible.

Le processus de changement doit préciser le propriétaire, le motif, la portée, les résultats de test, les critères de retour et la date d'entrée en vigueur. Une règle temporaire utilisée lors d'un incident ne doit pas rester active indéfiniment sans revue. Les exceptions doivent avoir une expiration, une justification, des alertes si elles dépassent leur date et un processus de révocation.

### 14. Atelier pratique — panne multisite avec hypothèses concurrentes

Construisez un jeu de test contenant plusieurs sites reliés par des chemins partagés, des alarmes d'interface, des mesures de latence, des logs applicatifs et au moins un événement de changement. Injectez trois scénarios : une panne du chemin partagé, un problème d'application indépendant sur un site, et une interruption de collecte qui produit un silence trompeur. Mélangez quelques doublons et faites arriver un événement important en retard.

Le premier objectif est de normaliser les données sans détruire la provenance. Le deuxième est de reconstruire la chronologie en conservant les trois temps lorsque disponibles. Le troisième est de regrouper les symptômes et de maintenir séparés les incidents indépendants. Le quatrième est de classer les causes candidates à partir de preuves explicitement identifiées. Le cinquième est de choisir le prochain test qui permet de départager les hypothèses.

```mermaid
flowchart TD
    A["Générer événements et topologie versionnée"] --> B["Normaliser et dédupliquer"]
    B --> C["Calculer retard et qualité"]
    C --> D["Construire incidents candidats"]
    D --> E["Comparer hypothèses"]
    E --> F["Sélectionner test discriminant"]
    F --> G["Ajouter résultat du test"]
    G --> H["Mettre à jour classement et synthèse"]
    H --> I["Comparer au résultat connu"]
```

Le dossier de laboratoire doit montrer pourquoi une cause est retenue ou laissée en tête de classement sans être confirmée. Pour chaque candidat, consignez les preuves favorables, les contradictions, les trous de données et le niveau de confiance. Pour chaque action de diagnostic proposée, décrivez le résultat attendu sous chaque hypothèse. Si le test n'est pas discriminant, choisissez une autre mesure au lieu de prétendre que l'incertitude a diminué.

Testez aussi la réexécution du lot avec exactement les mêmes événements : le nombre d'incidents ne doit pas augmenter artificiellement et le classement doit rester stable. Ajoutez ensuite l'événement tardif et comparez les résultats. Le moteur doit expliquer la révision, conserver la décision antérieure et permettre à un opérateur de voir pourquoi la cause candidate a changé.

```mermaid
sequenceDiagram
    participant M as Moteur de corrélation
    participant G as Graphe temporel
    participant E as Équipe d'exploitation
    participant T as Test de diagnostic
    M->>G: Chercher dépendances valides à l'heure de l'incident
    G-->>M: Chemins et provenance
    M->>E: Présenter hypothèses et contradictions
    E->>T: Lancer test autorisé
    T-->>M: Résultat et heure mesurée
    M->>M: Recalculer classement
    M-->>E: Mise à jour avec éléments de preuve
```

Le rapport final doit contenir le jeu d'événements, les règles versionnées, les résultats du regroupement, le classement, les tests proposés, l'analyse des désaccords et la limite de ce que le système a pu conclure. Il doit permettre de comparer une version de corrélation à une autre sans modifier simultanément toutes les variables de l'expérience.

### 15. Critères d'acceptation pour la production

Une chaîne de corrélation prête pour la production doit être capable de distinguer événement, symptôme et incident ; préserver la provenance et les trois temps ; représenter les dépendances à la période correcte ; traiter les doublons et les événements tardifs ; conserver les hypothèses alternatives ; et expliquer les contributions au classement. Les périodes de silence doivent être interprétées en fonction de la santé et de la couverture des sources, non comme une confirmation automatique de normalité.

Les indicateurs d'acceptation devraient inclure la proportion d'événements correctement regroupés, le taux de fusion de causes indépendantes, le délai avant la première hypothèse utile, la stabilité du classement après arrivée tardive, la part des affirmations de synthèse reliées aux preuves et le coût de triage des opérateurs. Les objectifs doivent être définis à partir du contexte et réévalués avec les responsables concernés ; les mêmes chiffres ne conviennent pas forcément à chaque type de service.

```mermaid
flowchart TD
    A["Contrat événementiel validé"] --> B["Topologie historisée"]
    B --> C["Fenêtres et déduplication testées"]
    C --> D["Évaluation sur corpus"]
    D --> E["Synthèse reliée aux preuves"]
    E --> F["Mode observation"]
    F --> G{"Qualité acceptable ?"}
    G -- "Non" --> H["Réviser règles et sources"]
    H --> C
    G -- "Oui" --> I["Pilote et surveillance"]
    I --> J["Revue périodique et retour arrière"]
```

La corrélation ne remplace pas l'enquête technique. Elle réduit le nombre de pistes à examiner, révèle les relations que les événements isolés ne montrent pas et aide à sélectionner les tests les plus informatifs. Elle doit rester capable de reconnaître plusieurs causes possibles, de signaler une couverture insuffisante et de réviser ses conclusions. La qualité d'un moteur expert se mesure à la qualité de ses preuves et de ses abstentions autant qu'au nombre de causes qu'il propose.

### Grille d'autoévaluation de l'atelier

- [ ] Les événements, symptômes et incidents sont représentés séparément.
- [ ] La provenance, l'heure source, l'ingestion et le traitement sont préservés.
- [ ] La topologie est versionnée et sélectionnée selon l'heure de l'incident.
- [ ] Les relations temporelles, statistiques et topologiques restent distinctes.
- [ ] Les événements dupliqués et tardifs sont traités sans perdre l'historique.
- [ ] Les hypothèses concurrentes incluent preuves contraires et tests discriminants.
- [ ] Les scores sont explicables et ne sont pas présentés comme des probabilités sans calibration.
- [ ] Les périodes de silence prennent en compte la disponibilité des capteurs.
- [ ] Les traces, métriques, logs et changements sont rapprochés avec prudence.
- [ ] La synthèse générative renvoie aux sources et ne fabrique pas de faits.
- [ ] Les regroupements sont mesurés sur un corpus de régression.
- [ ] Les changements du moteur sont comparés en mode observation.
- [ ] Les résultats de corrélation sont traçables et reproductibles.
- [ ] Le système peut annoncer qu'aucune cause n'est suffisamment étayée.

## 16. Défi final, checklist et références

### Défi

Le centre de supervision reçoit de nombreuses alertes pendant une dégradation qui touche trois agences. Concevez un moteur qui déduplique les alertes, les relie à la topologie et produit trois hypothèses classées, avec les preuves et le test suivant. Le moteur ne doit pas déclencher de changement de configuration.

### Proposition de correction

Normalisez les événements en conservant leur provenance et les deux timestamps. Dédupliquez par identité stable, type et fenêtre contrôlée, tout en préservant le nombre d'occurrences et l'historique de l'incident. Reconstituez la topologie valable à l'heure du problème et identifiez les dépendances partagées. Combinez temporalité, topologie, changements et qualité des sources pour classer les candidats.

Présentez au minimum trois hypothèses concurrentes. Pour chacune, fournir les événements favorables, les contre-indices, le niveau d'incertitude et un test discriminant. Le rapport distingue clairement les observations des inférences. Toute citation produite par un LLM doit être vérifiée par le service qui détient les événements. Aucune action de changement n'est exécutée ; les résultats sont présentés à l'opérateur pour validation.

### Checklist de production

- [ ] Schéma canonique versionné et provenance conservée.
- [ ] Heure source et heure de réception différenciées.
- [ ] Données tardives, duplication et valeurs inconnues gérées.
- [ ] Déduplication testée contre les incidents distincts et les récidives.
- [ ] Topologie datée, source et qualité des relations documentées.
- [ ] Corrélation temporelle, topologique et contextuelle explicable.
- [ ] Plusieurs hypothèses et contre-indices présentés.
- [ ] Cause probable distinguée d'une cause confirmée.
- [ ] Tests discriminants non invasifs privilégiés.
- [ ] Rapport relié à des événements consultables.
- [ ] Sorties génératives et références validées.
- [ ] Accès, rétention et redaction des données sensibles définis.
- [ ] Corpus de référence maintenu et tests de non-régression exécutés.
- [ ] Cause confirmée et résultat terrain réintégrés selon une procédure revue.

### Références

- OpenTelemetry, documentation : https://opentelemetry.io/docs/
- Prometheus, bonnes pratiques de surveillance : https://prometheus.io/docs/practices/
- NIST, AI Risk Management Framework : https://www.nist.gov/itl/ai-risk-management-framework
- OpenConfig, modèles et spécifications : https://www.openconfig.net/
- Google SRE, ressources d'ingénierie de fiabilité : https://sre.google/

La conclusion centrale est que la corrélation automatise la recherche d'indices, tandis que la RCA doit expliquer une chaîne plausible et vérifiable. Un système digne de confiance garde les contre-indices, indique l'incertitude, cite des événements réels et privilégie le test qui permet de distinguer les hypothèses plutôt que d'imposer prématurément une cause unique.