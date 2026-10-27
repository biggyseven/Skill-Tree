# RETEX : capitalisation et amélioration continue

> **Mise en contexte**
>
> Une panne majeure a interrompu un service pendant plusieurs heures. L'équipe a rétabli le service en contournant une dépendance, mais le rapport initial dit seulement « erreur humaine » et propose une formation. Trois mois plus tard, un incident similaire se produit. Un RETEX utile doit expliquer ce qui s'est passé, pourquoi les barrières n'ont pas empêché ou limité l'événement, ce qui a aidé l'équipe à se rétablir et comment vérifier que les améliorations tiennent dans le temps. Il ne s'agit ni de justifier toutes les décisions ni de chercher un coupable.
>
> Au niveau expert, le retour d'expérience devient une boucle d'ingénierie : preuves, chronologie, analyse, décisions, actions, vérification et diffusion contrôlée des apprentissages.

## Objectifs pédagogiques

Tu vas apprendre à déterminer le périmètre d'un RETEX, préserver une chronologie factuelle, distinguer déclencheur et facteurs contributifs, conduire une analyse constructive, formuler des actions mesurables, éviter les conclusions causales non étayées et intégrer les leçons dans les procédures, les outils, la formation et les contrôles.

## Prérequis et cadre de sécurité

Il faut comprendre les incidents, les changements, les journaux et les procédures d'escalade. Pendant un incident actif, la restauration et la sécurité passent avant l'analyse rétrospective. Respecte les politiques de conservation, de confidentialité et d'accès aux preuves. Les exercices de reproduction doivent être autorisés et réalisés dans un environnement maîtrisé.

## 1. Pourquoi organiser un RETEX ?

Les incidents révèlent parfois un défaut technique, mais aussi un problème de détection, de coordination, d'information, de capacité ou de procédure. Le RETEX tente de comprendre les interactions qui ont permis à l'événement de se produire ou d'en augmenter l'impact. Il doit aussi identifier les décisions efficaces, les outils qui ont aidé et les contrôles qui ont limité les conséquences.

La revue est dite constructive lorsqu'elle analyse les actions à partir des informations et contraintes disponibles au moment des faits, plutôt que de juger uniquement avec le recul. Cela ne supprime pas les responsabilités ni les exigences de sécurité : cela déplace l'analyse vers les conditions concrètes, les mécanismes de défense et les décisions qui peuvent rendre le système plus robuste.

### Schéma 1 — La boucle d'apprentissage

~~~mermaid
flowchart TD
    A[Incident et stabilisation] --> B[Chronologie et preuves]
    B --> C[Analyse des déclencheurs et facteurs]
    C --> D[Actions préventives et de mitigation]
    D --> E[Responsables et échéances]
    E --> F[Vérification de l'efficacité]
    F --> G[Procédures, outils et formation mis à jour]
    G --> H[Surveillance des récurrences]
    H --> A
~~~

Un compte rendu publié ne vaut pas capitalisation à lui seul. L'organisation doit transformer les actions en changements de système et vérifier que ces changements ont un effet. Les rapports doivent aussi être retrouvables par thème, service, type de défaillance et action, tout en limitant l'accès aux informations sensibles.

## 2. Définir le périmètre et rassembler les éléments

Le périmètre doit couvrir l'impact, la période, les services, les équipes et les décisions pertinentes. Collecte, selon le besoin, les alertes, journaux, changements, déploiements, tickets, métriques, communications et décisions horodatées. Préserve les informations selon la procédure, ne modifie pas les preuves et limite la diffusion aux personnes autorisées.

Tous les horodatages doivent être interprétés avec leur fuseau, leur source et leur niveau de fiabilité. Un événement enregistré par un système avec une horloge décalée peut apparaître avant sa cause. Une chronologie doit noter les incertitudes au lieu de les masquer. Si les journaux ne couvrent pas une période, indique cette lacune et son effet sur les conclusions.

## 3. Construire une chronologie factuelle

La chronologie présente ce qui s'est passé, quand, quelle observation était disponible et quelle décision a suivi. Sépare les événements observés des interprétations. « L'alerte a été reçue à 10 h 14 » est un fait si le système le prouve. « L'équipe a ignoré l'alerte » est une interprétation qui exige de comprendre le routage, la charge, le contexte et les informations visibles.

### Exemple simplifié

| Heure | Événement vérifié | Information connue à ce moment | Décision |
|---|---|---|---|
| 09:02 | Un changement réseau est terminé | Les contrôles de déploiement sont passés | Le changement est déclaré terminé |
| 09:08 | Le taux d'erreur augmente | L'alerte existe mais est routée vers une file secondaire | Pas d'escalade immédiate |
| 09:17 | Plusieurs utilisateurs signalent une interruption | L'impact devient visible | Début de l'investigation |
| 09:32 | Le lien est identifié comme facteur probable | Les compteurs et la chronologie concordent | Retour contrôlé selon la procédure |
| 09:46 | Le service est stable | Les tests fonctionnels passent | Surveillance renforcée |

Cette chronologie ne prouve pas encore que le changement a causé l'incident. Il faut examiner la preuve technique et les autres hypothèses. Elle permet toutefois de poser des questions : pourquoi l'alerte n'a-t-elle pas atteint la bonne équipe ? Quels critères ont déclenché le retour arrière ? Quels tests ont confirmé le rétablissement ?

## 4. Distinguer les niveaux de causalité

Il est utile de séparer :

- **Symptôme** : effet directement observable, par exemple des pertes de connexion.
- **Déclencheur** : événement rapproché dans le temps qui a initié la séquence.
- **Mécanisme technique** : processus par lequel le déclencheur produit l'effet.
- **Facteurs contributifs** : conditions qui rendent l'événement plus probable ou plus grave.
- **Défaillance de détection** : raison pour laquelle un signal n'a pas aidé l'équipe à temps.
- **Défaillance de récupération** : raison pour laquelle la limitation de l'impact ou le retour a été lent ou inefficace.
- **Mesure durable** : changement qui réduit la récurrence, améliore la détection ou limite les conséquences.

Un incident peut avoir plusieurs causes contributives. Une formulation unique du type « le technicien s'est trompé » ne décrit ni les contrôles qui auraient pu détecter l'erreur, ni la pression opérationnelle, ni l'ambiguïté de la procédure, ni le rayon d'impact autorisé par l'architecture.

### Schéma 2 — Analyser les barrières

~~~mermaid
flowchart TD
    A[Changement ou défaillance] --> B[Barrières de prévention]
    B --> C[Détection et alerte]
    C --> D[Décision et coordination]
    D --> E[Limitation de l'impact]
    E --> F[Retour au service]
    B -. barrière insuffisante .-> X[Impact]
    C -. détection tardive .-> X
    D -. décision retardée .-> X
    E -. récupération limitée .-> X
~~~

## 5. Choisir les méthodes d'analyse sans en faire une formalité

Les cinq pourquoi aident à interroger les mécanismes, mais ne doivent pas obliger une histoire à cinq étapes si les preuves ne la soutiennent pas. L'analyse peut produire plusieurs branches. Si chaque réponse répète l'affirmation précédente, elle n'apporte aucune explication.

Le diagramme d'Ishikawa organise les causes possibles selon des familles adaptées au contexte : méthodes, compétences et rôles, outils, composants, mesures, environnement, fournisseurs et gouvernance. Il sert à générer des hypothèses ; il ne prouve pas celles qui sont inscrites dans ses branches. Chaque hypothèse doit être reliée à une observation ou à un test autorisé.

Les arbres de défaillance ou l'analyse chronologique peuvent être pertinents pour des incidents complexes ou à conséquences graves. Une méthode plus formelle ne garantit pas une meilleure conclusion si les données sont insuffisantes. Choisis l'approche en fonction de la criticité, des mécanismes et du niveau de preuve.

### Schéma 3 — Ishikawa adapté à l'exploitation

~~~mermaid
flowchart LR
    A[Incident de service] --> B[Méthode]
    A --> C[Outils et technologie]
    A --> D[Mesures et alertes]
    A --> E[Compétences et rôles]
    A --> F[Environnement et charge]
    A --> G[Fournisseurs et dépendances]
    B --> H[Hypothèses à vérifier]
    C --> H
    D --> H
    E --> H
    F --> H
    G --> H
~~~

### Distinguer faits, hypothèses et conclusions

Un registre d'analyse peut utiliser trois états :

- **Fait confirmé** : soutenu par une preuve pertinente.
- **Hypothèse ouverte** : plausible, mais pas encore confirmée ou réfutée.
- **Conclusion** : explication retenue parce qu'elle est soutenue par les éléments disponibles et qu'elle résiste aux alternatives importantes.

Documente les hypothèses rejetées et la raison du rejet lorsque le risque le justifie. Ne transforme pas une corrélation temporelle en causalité. Si la cause exacte reste inconnue, indique ce qui est établi, les scénarios encore plausibles et les mesures qui réduisent le risque malgré cette incertitude.

## 6. Évaluer la qualité de la réponse

Le RETEX ne porte pas uniquement sur ce qui a provoqué l'incident. Il examine la détection, le routage, l'escalade, la coordination, le partage des faits, les changements appliqués pendant l'urgence, l'information des utilisateurs et le rétablissement. Une équipe peut avoir identifié rapidement la cause mais perdre du temps parce qu'elle ne sait pas qui autorise le retour arrière. À l'inverse, une bonne coordination peut limiter l'impact alors que la cause reste inconnue.

Mesure, lorsque les données le permettent, le temps de détection, le délai avant prise en charge, le temps de décision, le temps de restauration, le temps de communication et le nombre de décisions révisées faute d'information. Définis clairement le début et la fin de chaque durée : sans conventions stables, les comparaisons sont trompeuses.

Évite de transformer les indicateurs en objectifs qui incitent à cacher les incidents. Une augmentation initiale du nombre de tickets peut être le signe d'une meilleure détection et d'une déclaration plus complète. Combine les mesures avec l'analyse des cas, le contexte et le ressenti des équipes.

## 7. Concevoir des actions réellement efficaces

Une action doit traiter un mécanisme ou une barrière identifiée. Des actions robustes incluent parfois une limite technique, une détection fiable, une réduction du rayon d'impact, une procédure versionnée, un test obligatoire, une meilleure répartition des responsabilités ou une stratégie de retour maîtrisée. Une formation peut être utile, mais elle ne doit pas remplacer un contrôle de conception lorsque l'erreur est facile à reproduire.

Pour chaque action, définis :

- le constat et le risque visés ;
- l'état futur attendu ;
- le propriétaire qui peut réaliser la modification ;
- l'échéance et les dépendances ;
- la preuve de mise en œuvre ;
- un critère d'efficacité, une période d'observation et un responsable de vérification ;
- les conditions d'escalade si l'action échoue ou prend du retard.

### Exemple d'action faible et de formulation améliorée

**Faible :** « Rappeler aux équipes de faire attention lors des changements. »

**Plus vérifiable :** « Ajouter au pipeline de changement une validation automatique du périmètre et un contrôle post-déploiement sur le groupe pilote ; bloquer la promotion si le critère critique échoue ; conserver le résultat et vérifier après un mois que les changements concernés produisent la preuve attendue. »

Une action n'a pas besoin d'être automatisée pour être valide, mais elle doit corriger le mécanisme identifié et être proportionnée au risque. Un responsable, une échéance et un statut ne prouvent pas l'efficacité. La preuve de fermeture doit être définie au moment où l'action est créée.

## 8. Vérifier la capitalisation

La capitalisation consiste à intégrer un apprentissage là où il sera utile : procédure, checklist, test automatisé, supervision, architecture, modèle de changement, formation ou contrat fournisseur. Le document du RETEX est une source, mais l'utilisateur ne devrait pas avoir à retrouver un ancien rapport pour découvrir une barrière de sécurité essentielle.

Évalue l'efficacité des actions après un délai défini. Utilise des tests représentatifs, des simulations autorisées, des revues d'échantillons ou des métriques. Si aucun incident semblable ne se produit pendant une courte période, cela ne prouve pas à lui seul que le risque a disparu. Combine les données opérationnelles à une vérification de la barrière qui a été ajoutée.

### Schéma 4 — Des actions à la preuve

~~~mermaid
flowchart TD
    A[Constat du RETEX] --> B[Action et responsable]
    B --> C[Preuve de mise en œuvre]
    C --> D[Test de la barrière]
    D --> E{Efficace ?}
    E -- Non --> F[Revoir la mesure et la priorité]
    F --> B
    E -- Oui --> G[Mettre à jour la référence]
    G --> H[Surveiller le risque résiduel]
~~~

## 9. TP guidé : RETEX d'une panne réseau

**Scénario.** Après un changement d'ACL, des clients d'un service interne ne peuvent plus joindre une API. Le service est rétabli après retour arrière. Le ticket initial dit « ACL incorrecte ».

1. Collecte la configuration avant/après, le ticket de changement, les résultats de tests, les journaux et les horodatages.
2. Décris l'impact et la durée avec les définitions opérationnelles de l'organisation.
3. Construis une chronologie qui distingue l'heure du changement, du premier signal, de l'alerte et du rétablissement.
4. Vérifie les hypothèses : règle trop restrictive, test incomplet, environnement de préproduction différent ou manque de visibilité.
5. Examine les barrières : revue par pair, tests représentatifs, segmentation de l'impact, critères de retour arrière et alertes.
6. Formule des actions avec preuves de mise en œuvre et critères d'efficacité.
7. Organise une revue de suivi et vérifie la réduction du risque sur les changements ultérieurs.

**Critère de réussite :** le rapport distingue faits et hypothèses, évite le blâme, explique le mécanisme soutenu par les preuves, relie chaque action à un risque et décrit comment vérifier le résultat.

## 10. Exercices corrigés

### Exercice 1 — Cause unique trop rapide

Une panne suit une mise à jour. Le rapport conclut « la mise à jour est la cause » et recommande de former l'opérateur. Quelles sont les lacunes ?

**Correction.** La succession temporelle n'établit pas à elle seule la causalité. Il faut examiner les journaux, la version, les différences de configuration et les tests. La formation ne traite pas nécessairement les barrières de prévention ou de retour arrière. Le rapport doit distinguer le déclencheur présumé, les facteurs contributifs et la preuve de causalité.

### Exercice 2 — Absence de récidive

Une action est mise en œuvre et aucun incident similaire ne survient durant une semaine. Peut-on conclure qu'elle est efficace ?

**Correction.** Pas sans connaître la fréquence attendue, le volume d'opérations et la durée d'observation nécessaire. Définis un critère de vérification supplémentaire : test contrôlé, revue des changements suivants, couverture du contrôle ou période adaptée à la fréquence du risque.

### Exercice 3 — Revue punitive

Les participants hésitent à signaler les erreurs de décision parce que les rapports servent à sanctionner les personnes. Que peut faire le responsable du RETEX ?

**Correction.** Expliquer l'objectif d'apprentissage, distinguer l'analyse des conditions du système des processus formels de responsabilité, protéger les données selon les règles et recentrer la discussion sur les informations disponibles au moment de l'action. L'approche constructive n'autorise pas à dissimuler un acte intentionnel ou à ignorer les obligations réglementaires ; elle rend l'analyse des erreurs non intentionnelles plus utile.

## 11. Défi final corrigé

**Mission.** Un incident affectant un service critique s'est produit deux fois en trois mois. La première action avait consisté en une formation et une mise à jour de procédure, mais l'incident s'est reproduit.

**Correction type.** Commence par reconstruire les deux chronologies et comparer les mécanismes. Détermine si l'action précédente a été exécutée, testée et vérifiée, ou simplement déclarée terminée. Examine les contrôles techniques, les signaux de détection, les points de décision, les dépendances et le rayon d'impact. Définis des actions qui modifient les barrières et donne à chacune une preuve de mise en œuvre ainsi qu'un test d'efficacité. Mets à jour la procédure et les systèmes concernés, puis programme une vérification indépendante. Si la cause exacte demeure incertaine, documente cette limite et adopte des mesures proportionnées qui réduisent l'impact des scénarios plausibles.

## Références pour approfondir

- [Google SRE — Postmortem Culture](https://sre.google/workbook/postmortem-culture/) — retours d'expérience constructifs et actions de suivi mesurables.
- [Google SRE — Incident Management Guide](https://sre.google/resources/practices-and-processes/incident-management-guide/) — gestion des incidents et apprentissage après les interruptions.
- Les règles de conservation des preuves, de confidentialité et de signalement de l'organisation restent applicables à chaque RETEX.
