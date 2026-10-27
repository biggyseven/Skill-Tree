# Analyse de cause racine (5 Pourquoi, Ishikawa)

> **Mise en contexte**
>
> Tous les lundis matin, les utilisateurs signalent que l'application est lente. L'équipe redémarre le serveur et la situation s'améliore, puis le problème revient la semaine suivante. Dire « le serveur est lent » décrit un symptôme, pas une explication exploitable. L'analyse de cause racine cherche à identifier les conditions qui ont produit l'incident, à tester les hypothèses et à réduire le risque de répétition.

## Objectifs du cours

Tu apprendras à séparer les faits des hypothèses, construire une chronologie, utiliser les 5 Pourquoi et Ishikawa, tester des causes possibles, choisir des actions correctives proportionnées et vérifier leur efficacité sans rechercher un coupable.

## 1. Symptôme, cause contributive et cause racine

Un symptôme est ce que l'on observe : une requête échoue, un disque se remplit ou un service redémarre. Une cause contributive augmente la probabilité ou l'impact de l'incident. Une cause racine est une explication causale suffisamment étayée pour orienter une action durable dans le périmètre étudié.

La cause racine n'est pas forcément unique. Une panne peut résulter de plusieurs facteurs : seuils de supervision incomplets, capacité insuffisante, changement non vérifié et procédure de retour arrière inadéquate. Le but n'est pas d'inventer une réponse simple, mais de trouver les causes que les preuves permettent de soutenir.

Sépare toujours :
- **Faits :** mesures, journaux, horodatages, changement enregistré et résultats reproductibles.
- **Hypothèses :** explications possibles à confirmer.
- **Conclusions :** hypothèses appuyées par des preuves et confrontées aux alternatives.
- **Actions :** mesures immédiates, correction de fond et prévention de la récidive.

## 2. Préserver les éléments et construire une chronologie

Commence par définir le périmètre : service, période, utilisateurs affectés, impact et état actuel. Collecte les éléments nécessaires selon les autorisations et les règles de rétention : journaux applicatifs, métriques de supervision, changements récents, événements système, tickets similaires et mesures de capacité.

Une chronologie peut prendre cette forme :

| Heure | Fait observé | Source | Interprétation actuelle |
|---|---|---|---|
| 08 h 55 | Début de hausse de latence | Tableau de bord | À confirmer |
| 09 h 02 | Files de requêtes en hausse | Métrique applicative | Piste à explorer |
| 09 h 08 | Redémarrage du service enregistré | Journal de changement | A modifié l'état, pas nécessairement la cause |
| 09 h 12 | Latence redevenue normale | Sonde fonctionnelle | Rétablissement observé |

Les heures doivent provenir des sources et utiliser un fuseau cohérent. Vérifie les décalages d'horloge. Ne supprime pas les journaux et ne lance pas de modification susceptible d'écraser les preuves avant d'avoir évalué leur nécessité. La collecte doit rester proportionnée à l'incident.

## 3. La méthode des 5 Pourquoi

Les 5 Pourquoi consistent à demander pourquoi un résultat s'est produit, puis à poursuivre en utilisant les réponses comme pistes à vérifier. Le nombre cinq est indicatif, pas une obligation ; une chaîne peut être plus courte ou comporter plusieurs branches.

Exemple à examiner :
1. Pourquoi les utilisateurs voient-ils des erreurs ? Parce que les requêtes dépassent le délai.
2. Pourquoi les requêtes dépassent-elles le délai ? Parce que la file de traitement s'accumule.
3. Pourquoi la file s'accumule-t-elle ? Parce que les traitements prennent plus de temps que d'habitude.
4. Pourquoi prennent-ils plus de temps ? Une piste est la saturation d'une dépendance, à vérifier avec les métriques.
5. Pourquoi cette saturation n'a-t-elle pas été détectée plus tôt ? Une hypothèse est l'absence d'un indicateur ou d'un seuil adapté.

Chaque réponse doit être confrontée aux éléments. Une chaîne bien racontée mais non vérifiée n'est pas une analyse de cause racine.

## 4. Le diagramme d'Ishikawa

Ishikawa organise les hypothèses par grandes catégories pour réduire le risque de s'arrêter à la première explication. Dans un système informatique, on peut adapter les catégories aux personnes, aux procédures, à la technologie, aux données, à l'environnement et aux dépendances externes.

~~~mermaid
flowchart LR
    A[Incident observé] --> B[Personnes et compétences]
    A --> C[Procédures et changements]
    A --> D[Technologie et capacité]
    A --> E[Données et configuration]
    A --> F[Environnement et dépendances]
    B --> G[Hypothèses à tester]
    C --> G
    D --> G
    E --> G
    F --> G
    G --> H[Preuves et expériences]
    H --> I[Causes étayées et actions]
~~~

Le diagramme ne prouve aucune cause ; il aide à produire des hypothèses diverses. Évite les catégories qui blâment une personne. Analyse les conditions, les garde-fous, les informations disponibles et la conception du processus.

## 5. Tester les hypothèses

Pour chaque hypothèse, précise le fait qui la soutient, les éléments qui la contredisent, le test sûr qui permet de la vérifier et la décision selon le résultat. Les tests doivent être proportionnés et autorisés. Lorsque l'incident a un impact fort, privilégie la collecte non destructive, un environnement de reproduction ou une analyse par un spécialiste.

| Hypothèse | Preuve attendue | Test raisonnable | Limite |
|---|---|---|---|
| Le stockage manque d'espace | Courbe d'espace et erreurs liées | Comparer l'historique et l'état du volume | L'espace faible peut être un symptôme d'une autre activité |
| Une modification récente déclenche les erreurs | Chronologie cohérente et différence de configuration | Comparer la version et reproduire en test si possible | Une succession temporelle ne prouve pas seule la causalité |
| Le réseau provoque la latence | Mesures de perte, délai ou erreurs sur le chemin concerné | Comparer plusieurs points de mesure | Un ping seul ne représente pas forcément la voie applicative |

Ne conclus pas à partir d'une seule coïncidence. Si les preuves sont insuffisantes, note la cause comme probable ou inconnue et définis ce qui permettrait de progresser. L'honnêteté sur l'incertitude vaut mieux qu'une certitude inventée.

## 6. Passer de la cause aux actions

Une bonne analyse ne s'arrête pas à une explication. Distingue :
- **Action immédiate :** rétablir ou limiter l'impact.
- **Correction :** éliminer la cause confirmée ou réduire directement sa présence.
- **Prévention :** améliorer la détection, la capacité, les tests, la procédure ou la conception.
- **Vérification :** mesurer si la modification a réduit la probabilité ou l'impact de récurrence.

Chaque action doit avoir un responsable, une échéance, un indicateur d'achèvement et un critère d'efficacité. « Surveiller davantage » est trop vague ; « créer une alerte sur la croissance du volume, vérifier le seuil en test et mesurer les alertes pertinentes pendant la période convenue » est plus vérifiable.

## 7. Mesurer l'efficacité et partager le résultat

Après la mise en œuvre, vérifie si les symptômes sont absents ou réduits pendant une période pertinente, si les contrôles déclenchent au bon moment et si le contournement est toujours nécessaire. L'absence immédiate de récidive ne garantit pas un succès définitif si le cycle naturel de l'incident est hebdomadaire.

Le rapport doit résumer l'impact, la chronologie, les causes étayées, les facteurs contributifs, les preuves, les actions et les incertitudes restantes. Il doit aider l'équipe à apprendre, sans exposer des données sensibles et sans transformer l'analyse en accusation personnelle.

## Mise en pratique

### Laboratoire : rechercher la cause d'une lenteur récurrente

Scénario fictif : une application est lente chaque lundi à 9 h. Le redémarrage la rétablit temporairement. Tu disposes d'un historique de latence, de l'utilisation CPU, de l'espace disque, de l'état d'une dépendance et d'un journal des changements.

1. Écris cinq faits observables sans interprétation.
2. Construis une chronologie avec la source de chaque heure.
3. Utilise les 5 Pourquoi pour formuler une chaîne d'hypothèses, sans prétendre que chaque réponse est vraie.
4. Construis un Ishikawa avec au moins quatre catégories pertinentes.
5. Choisis deux hypothèses et précise le test, la preuve attendue et ce qui invaliderait chaque hypothèse.
6. Rédige une action immédiate, une action de fond et un indicateur de vérification.
7. Présente une conclusion avec un niveau de confiance explicite et les inconnues restantes.

**Résultat attendu :** une analyse fondée sur les preuves, qui différencie clairement hypothèse et cause étayée. Ne réalise pas de changement destructif sur une production pour les besoins du laboratoire.

## Exercices corrigés

**1. Le service fonctionne après un redémarrage. Est-ce la preuve que le redémarrage était la cause de la panne ?**

Correction : non. Il a servi de contournement ou d'action de rétablissement, mais ne démontre pas pourquoi l'incident s'est produit. Il faut confronter plusieurs hypothèses à des éléments vérifiables.

**2. Quel est le risque d'utiliser les 5 Pourquoi sans vérifier les réponses ?**

Correction : la chaîne peut transformer des suppositions en récit cohérent mais faux. Chaque réponse doit devenir une hypothèse à tester avec des preuves.

**3. Pourquoi utiliser Ishikawa si une première piste semble évidente ?**

Correction : pour considérer d'autres facteurs et éviter de conclure prématurément. Le diagramme aide à structurer les pistes mais ne remplace pas les tests.

**4. Que faire si la cause racine ne peut pas encore être déterminée ?**

Correction : documenter les faits et les hypothèses, indiquer les limites de l'analyse, définir les preuves et tests nécessaires, puis suivre les actions de réduction de risque. Ne pas inventer de certitude.

## Défi final corrigé

Une erreur applicative revient chaque lundi. Les journaux montrent des délais d'attente, la latence réseau ne change pas sensiblement et le redémarrage résout temporairement le problème. L'équipe soupçonne une saturation de la base de données.

**Correction attendue :** enregistrer les faits et leurs sources, aligner les horloges, comparer les métriques de base de données et d'application autour des incidents, rechercher les changements et les tâches planifiées du lundi, puis tester la piste dans un environnement sûr ou avec l'équipe responsable. Si les preuves confirment une saturation, définir une correction mesurable et un contrôle préventif. Sinon, poursuivre l'analyse des hypothèses alternatives. Le rapport doit qualifier le niveau de confiance et la période de validation nécessaire.


## 8. Définir un problème de manière testable

Une analyse de cause racine commence par une description qui évite la conclusion prématurée. Indique le service, le symptôme, le périmètre, la fréquence, le début, les conséquences, la manière de reproduire le phénomène et les critères qui prouveraient la résolution. « Le réseau est mauvais » ne donne pas de question vérifiable. « Entre 9 h et 9 h 20, les requêtes DNS depuis deux sous-réseaux ont expiré ; les requêtes depuis le troisième ont réussi » permet de comparer les contextes.

Conserve une chronologie et les preuves disponibles avant de modifier le système : journaux, compteurs, configuration connue, versions, alertes, tickets et changements récents. Respecte la rétention et la confidentialité. Une capture peut aider, mais note aussi son heure, le système d'origine, le filtre appliqué et la limite de l'observation. Les éléments incertains doivent rester signalés comme tels.

~~~mermaid
flowchart TD
    A[Symptôme précisément décrit] --> B[Chronologie et impact]
    B --> C[Hypothèses alternatives]
    C --> D[Choisir un test discriminant]
    D --> E[Résultat observé]
    E --> F{Hypothèse soutenue ?}
    F -->|Non| C
    F -->|Oui| G[Confirmer la cause au niveau permis par les preuves]
    G --> H[Action et mesure d'efficacité]
~~~

## 9. Bien utiliser les 5 Pourquoi

Les 5 Pourquoi consistent à demander pourquoi une situation s'est produite, puis à examiner la réponse comme une hypothèse à tester. Il n'est pas obligatoire d'obtenir exactement cinq questions : parfois deux ou quatre suffisent ; parfois la chaîne mène à un problème plus large qui nécessite plusieurs branches. Le nombre ne garantit ni la profondeur ni l'exactitude.

Exemple illustratif :
- **Symptôme :** le système de fichiers est arrivé à saturation.
- Pourquoi ? Des journaux ont occupé la majorité du volume.
- Pourquoi ? La rotation attendue ne s'est pas produite.
- Pourquoi ? Le service de rotation n'a pas exécuté la règle prévue.
- Pourquoi ? La configuration modifiée lors d'une migration n'a pas été vérifiée par le contrôle de conformité.
- Pourquoi ? Le plan de migration ne définissait pas de test pour la rotation des journaux.

Cette chaîne suggère une cause de processus, mais elle n'est pas prouvée tant qu'on n'a pas vérifié les journaux, la configuration, la chronologie de migration et le fonctionnement réel de la règle. Il peut y avoir plusieurs facteurs : une croissance exceptionnelle, une alerte absente, une mauvaise estimation de capacité ou une rétention non adaptée. Ne transforme pas un récit plausible en vérité uniquement parce que les questions s'enchaînent.

~~~mermaid
flowchart TD
    A[Saturation du disque] --> B[Pourquoi ? Journaux volumineux]
    B --> C[Pourquoi ? Rotation absente]
    C --> D[Pourquoi ? Règle non appliquée]
    D --> E[Pourquoi ? Migration non vérifiée]
    E --> F[Pourquoi ? Test absent du plan]
    F --> G[Hypothèse à confronter aux preuves]
~~~

## 10. Utiliser Ishikawa sans transformer le diagramme en preuve

Le diagramme d'Ishikawa organise les causes possibles par familles. En informatique, une version adaptée peut explorer les personnes et compétences, les méthodes et procédures, le matériel, les logiciels et configurations, les mesures et données, et l'environnement ou les dépendances. Les catégories sont un support de brainstorming structuré, pas une liste obligatoire.

~~~mermaid
flowchart LR
    A[Personnes et compétences] --> Z[Incident observé]
    B[Procédures et méthodes] --> Z
    C[Matériel et capacité] --> Z
    D[Logiciels et configuration] --> Z
    E[Mesures et observabilité] --> Z
    F[Environnement et dépendances] --> Z
~~~

Chaque branche génère des hypothèses à vérifier. Pour un problème de latence, les causes peuvent inclure congestion, retransmissions, résolution de noms, CPU, stockage, dépendances externes, changements récents ou mesures mal interprétées. Le diagramme aide à ne pas s'enfermer trop tôt dans une seule explication. Il faut ensuite choisir des tests qui distinguent les hypothèses et documenter les résultats.

ASQ présente les outils de résolution de problème, dont les 5 Pourquoi et le diagramme causes-effets/Ishikawa : https://asq.org/quality-resources/problem-solving et https://asq.org/quality-resources/quality-tools. Utilise ces techniques avec des preuves, pas comme substitut à l'analyse technique.

## 11. Tester les hypothèses et distinguer cause, déclencheur et facteur contributif

Une cause directe est l'événement ou la condition qui déclenche immédiatement le symptôme. Un facteur contributif rend la panne plus probable ou plus grave. Un défaut latent peut exister depuis longtemps et n'avoir produit des effets qu'après un changement de charge. Un mécanisme de détection absent peut prolonger l'incident sans être la cause initiale de la panne.

Conçois un test qui élimine ou soutient une hypothèse. Si une lenteur se produit seulement sur un site, compare les chemins, DNS, interfaces et mesures au même instant. Si toutes les applications d'un serveur sont lentes, examine les ressources et dépendances communes avant de modifier chaque application séparément. Si le phénomène a commencé après un changement, compare les versions et paramètres, mais n'en conclus pas que le changement est causal sans éléments supplémentaires.

La corrélation temporelle ne suffit pas. Deux alertes peuvent être provoquées par une cause commune ; l'une peut être une conséquence et non l'origine ; une pointe de CPU peut être normale. Reproduis le phénomène dans un environnement autorisé lorsque c'est possible, compare avec un cas sain et conserve le résultat qui contredit ton hypothèse. Une bonne analyse est prête à abandonner l'explication initiale.

~~~mermaid
sequenceDiagram
    participant A as Analyste
    participant D as Données et journaux
    participant S as Système de test
    A->>D: Formule une question et période
    D-->>A: Données et limites de preuve
    A->>S: Test contrôlé ou comparaison
    S-->>A: Résultat reproductible
    A->>A: Confirme, rejette ou affine l'hypothèse
~~~

## 12. Transformer l'analyse en actions qui empêchent la récurrence

Les actions doivent traiter la cause confirmée et les facteurs contributifs. Une réponse peut combiner correction technique, surveillance, capacité, procédure, formation, automatisation et gouvernance. « Sensibiliser l'équipe » est trop vague si aucune action observable n'est définie. Préfère « ajouter un contrôle automatique qui vérifie la présence de la tâche de rotation et crée une alerte si elle n'a pas exécuté pendant la période prévue », avec un responsable, une échéance et un test.

Sépare les actions de confinement, de correction immédiate et de prévention durable. Le contournement limite l'impact maintenant, mais peut exiger une surveillance renforcée. Une correction technique peut nécessiter un changement approuvé. Une action durable doit avoir un critère de réussite et un délai de mesure. Les actions ne sont closes qu'après preuve, pas simplement lorsqu'une tâche est marquée terminée.

| Catégorie | Exemple d'action | Preuve d'efficacité |
|---|---|---|
| Correction | Réparer la règle de rotation | Journaux et contrôles confirment la rotation |
| Prévention | Ajouter un test dans la migration | Compte rendu de tests avant mise en production |
| Détection | Alerter sur le taux de croissance | Alerte reçue et testée |
| Procédure | Ajouter un contrôle de fin | Fiche d'intervention mise à jour et testée |
| Capacité | Ajuster l'espace ou la rétention | Projection et historique revus |
| Gouvernance | Nommer un propriétaire de la règle | Champ propriétaire et revue périodique renseignés |

## 13. Travaux pratiques, exercices et défi final

### TP 6 — Construire une chronologie

Une application devient lente à 10 h 15. À 10 h 08, un changement de configuration a été appliqué ; à 10 h 18, le CPU dépasse son seuil ; à 10 h 20, la supervision de la base signale un nombre de connexions élevé. Construis une chronologie et trois hypothèses qui ne présument pas du lien causal.

**Correction :** conserver l'ordre, les sources et les heures. Hypothèses possibles : la modification a provoqué une charge supplémentaire ; un facteur indépendant a fait augmenter la charge ; la hausse CPU est une conséquence d'une file d'attente en base. Il faut comparer les mesures avant/après, examiner les journaux de la base et comprendre la modification. Les événements doivent être corrélés au périmètre exact.

### TP 7 — Contre-vérifier les 5 Pourquoi

L'équipe conclut que l'erreur vient d'un manque de formation parce qu'un opérateur a oublié une étape. Quels tests ou preuves permettraient de vérifier cette conclusion ?

**Correction :** examiner l'ergonomie de la procédure, les accès, les messages d'erreur, la pression opérationnelle, la version du document, les cas similaires, le contrôle automatisé et les consignes contradictoires. La formation peut être un facteur, mais ne doit pas être choisie par défaut au lieu de traiter une procédure ambiguë ou un système qui autorise une action dangereuse.

### TP 8 — Choisir une action de prévention

Un stockage sature tous les deux mois. L'équipe supprime manuellement des fichiers sans règles de rétention.

**Correction :** identifier les consommateurs d'espace, les types de fichiers, les règles applicables et la croissance. Définir une rétention approuvée, un contrôle de capacité, un avertissement suffisamment anticipé et un test de suppression/restauration adapté. Ne supprime pas des données avant validation de leur propriétaire et des exigences de conservation.

### Défi final — Analyse d'une panne répétitive

Une application tombe en panne chaque fin de mois. Prépare un rapport RCA avec symptôme, impact, chronologie, hypothèses, éléments de preuve, cause confirmée ou limites, actions immédiates, actions permanentes et critères de validation.

**Correction détaillée :** comparer plusieurs occurrences, pas seulement la dernière ; aligner les journaux et métriques sur la même fenêtre temporelle ; examiner la charge, les tâches planifiées et les dépendances ; tester les hypothèses ; préciser les facteurs contributifs ; affecter les actions à un propriétaire et définir une période d'observation. Si la cause n'est pas confirmée, écris « cause probable » ou « non déterminée », ne fabrique pas une certitude. La prévention est vérifiée sur plusieurs fins de mois et les incidents récurrents sont suivis jusqu'à ce que les critères convenus soient atteints.


## 15. Faciliter une analyse sans blâme

L'analyse de cause racine vise à comprendre pourquoi le système a permis à l'incident de survenir et pourquoi il n'a pas été détecté ou limité plus tôt. La recherche d'un coupable détourne souvent l'équipe des conditions qui rendent l'erreur probable : procédures ambiguës, contrôles inexistants, accès trop larges, dépendances mal documentées, surcharge ou absence de données. Cela ne supprime pas les responsabilités individuelles ; cela fait porter l'investigation sur des éléments qui peuvent être vérifiés et améliorés.

Commence par poser le cadre : quel service, quel intervalle, quel impact, quelles sources, quelles questions restent ouvertes, qui peut effectuer les tests et quelle information doit être protégée. Invite les personnes qui connaissent le système et le processus, sans exiger que l'une d'elles défende une conclusion à l'avance. Note les divergences de témoignage comme des points à examiner.

Une bonne réunion d'analyse sépare les faits, les hypothèses, les décisions et les actions. Affiche une chronologie commune, évite de confondre le déclencheur immédiat et la cause systémique, et recherche les éléments qui pourraient contredire l'hypothèse favorite. Une analyse n'a pas besoin d'annoncer une cause unique si plusieurs mécanismes ont contribué ou si les preuves restent incomplètes.

~~~mermaid
flowchart TD
    A[Réunion RCA] --> B[Revoir faits et chronologie]
    B --> C[Énoncer plusieurs hypothèses]
    C --> D[Choisir preuves et tests]
    D --> E[Confronter résultats]
    E --> F[Cause et facteurs contributifs]
    F --> G[Actions vérifiables]
    G --> H[Revue de l'efficacité]
~~~

Pour éviter une liste d'actions sans effet, classe-les par impact, probabilité de succès, coût, dépendances et délai. Une action de détection peut réduire le temps d'impact sans éliminer la cause ; une correction technique peut éliminer le mode de défaillance mais demander un changement ; une action de processus peut éviter que la même situation soit créée. Le rapport doit distinguer ces catégories et prévoir les preuves attendues.

Les actions dont la date est dépassée restent dans le suivi. Si une action a été abandonnée, documente la décision et l'acceptation du risque. Si l'action a été réalisée mais qu'aucune mesure ne montre une amélioration, révise l'hypothèse. L'analyse ne se termine pas à la publication du document ; elle se termine lorsque les actions ont été vérifiées ou que le risque résiduel est explicitement accepté.
