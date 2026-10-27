# Frameworks ITIL (incidents, changements)

> **Mise en contexte**
>
> Dans une équipe informatique, certains tickets décrivent une panne, d'autres une demande d'accès, un changement planifié ou un problème qui réapparaît chaque semaine. Lorsque toutes ces situations suivent le même circuit, les urgences se mélangent aux demandes ordinaires et les changements risqués sont exécutés sans analyse suffisante. Les pratiques de gestion des services aident à distinguer les objectifs et à rendre les décisions explicables.

## Objectifs du cours

Tu vas apprendre à distinguer incident, demande de service, problème et changement ; à comprendre les pratiques ITIL liées à la gestion des incidents, des problèmes et des changements ; à évaluer le risque, préparer une validation, définir un retour arrière et mesurer l'amélioration du service.

## 1. ITIL : un cadre de pratiques, pas une recette unique

ITIL est un ensemble de recommandations pour gérer des services numériques et améliorer leur valeur pour les utilisateurs et l'organisation. Il ne remplace pas la connaissance technique, les règles de sécurité, les contrats ni les procédures locales. Les pratiques doivent être adaptées à la taille de l'équipe, au risque et aux obligations du service.

L'objectif n'est pas de produire le plus de formulaires possible. Il est de décider de manière cohérente, de réduire les interruptions évitables, de contrôler les modifications et d'apprendre des incidents.

## 2. Distinguer les principaux flux de travail

| Type | But | Exemple | Résultat attendu |
|---|---|---|---|
| Incident | Rétablir un service interrompu ou dégradé | Une application ne répond plus | Service restauré et impact réduit |
| Demande de service | Fournir une demande standard pré-approuvée | Accès à un outil selon les règles | Demande exécutée, contrôlée et tracée |
| Problème | Comprendre et traiter la cause d'un ou plusieurs incidents | La même panne revient chaque semaine | Cause confirmée ou documentée, actions de réduction du risque |
| Changement | Modifier un service ou son environnement de manière contrôlée | Mise à jour d'un serveur en production | Modification évaluée, autorisée, vérifiée et documentée |

Un incident peut être résolu avant que sa cause profonde soit connue. Le traitement du problème peut continuer après le rétablissement. Une demande de service n'est pas automatiquement un changement : la mise à disposition d'un accès standard peut suivre un flux préautorisé, tandis qu'une modification de droits sensibles peut exiger une validation différente.

## 3. Gestion des incidents

Le processus d'incident cherche à restaurer le service aussi rapidement et sûrement que possible. Il comprend habituellement la détection, l'enregistrement, la catégorisation, l'évaluation de l'impact et de l'urgence, l'investigation, l'escalade si nécessaire, le rétablissement, la validation et la clôture.

La priorité doit reposer sur des critères communs. Le ticket doit conserver les symptômes observés, les utilisateurs affectés, les contrôles, la chronologie et les communications. Un contournement peut restaurer le service même si la cause n'est pas encore corrigée ; dans ce cas, indique clairement les risques résiduels et ouvre ou rattache un problème si le processus le demande.

## 4. Gestion des problèmes et des erreurs connues

Un problème concerne la cause ou les causes potentielles d'incidents, ainsi que les moyens de réduire la probabilité ou l'impact de leur réapparition. L'analyse peut conduire à une cause racine confirmée, à une erreur connue assortie d'un contournement ou à une conclusion encore incertaine.

Ne déclare pas une cause racine simplement parce qu'une corrélation existe. Compare la chronologie, les éléments techniques, les hypothèses concurrentes et les résultats des tests. Documente les mesures immédiates séparément des actions de fond : redémarrer un service peut rétablir le service sans éliminer la raison pour laquelle il s'est arrêté.

## 5. Gestion des changements

Un changement doit être décrit, évalué, autorisé selon le risque et vérifié après exécution. Le dossier précise le but, le périmètre, les actifs et services concernés, les dépendances, les risques, la fenêtre, les tests, le plan de communication et le retour arrière.

Trois catégories sont courantes dans les modèles de gestion, avec une terminologie qui peut varier selon l'organisation :

- **Changement standard :** faible risque, procédure documentée et autorisation préapprouvée dans un périmètre défini.
- **Changement normal :** évalué et autorisé selon le processus applicable avant exécution.
- **Changement d'urgence :** nécessaire pour traiter une menace ou une situation urgente ; il suit un chemin accéléré défini à l'avance et reçoit une revue adaptée ensuite.

« Urgent » ne signifie pas « sans contrôle ». Même dans une urgence, consigne l'autorité qui a autorisé l'action, les risques acceptés, le plan de rétablissement et les tests. Un comité de changement peut intervenir pour certains changements importants, mais toutes les petites tâches n'ont pas besoin d'une réunion formelle si la politique a prévu une autre voie sûre.

## 6. Cycle contrôlé d'un changement

~~~mermaid
flowchart TD
    A[Demande de changement] --> B[Portée et actifs concernés]
    B --> C[Analyse du risque et des dépendances]
    C --> D[Tests, fenêtre et retour arrière]
    D --> E[Autorisation selon la politique]
    E --> F[Exécution et journal de preuve]
    F --> G[Tests après changement]
    G --> H{Critères atteints ?}
    H -->|Oui| I[Clôture et mise à jour documentaire]
    H -->|Non| J[Arrêt, retour arrière ou escalade]
    J --> K[Rapport et revue]
    K --> I
~~~

Le changement est réussi si le service atteint les critères définis, pas uniquement si la commande s'est terminée. Le plan de retour arrière est une décision préparée avant l'exécution, avec les personnes autorisées, le temps nécessaire et les contrôles après retour.

## 7. Relations entre incident, problème et changement

Un incident entraîne la restauration. Si le même symptôme se répète ou si le risque l'exige, un problème est enregistré pour analyser la cause. La correction durable peut nécessiter un changement contrôlé. L'incident et le problème doivent rester reliés, afin que le support puisse identifier un contournement connu et mesurer la répétition.

Cette relation évite deux erreurs courantes : garder un incident ouvert indéfiniment tant que la cause racine n'est pas confirmée, ou clôturer tous les suivis après un simple rétablissement et perdre la trace de la cause récurrente.

## 8. Indicateurs et amélioration continue

Les métriques doivent guider les décisions, pas punir les personnes. Suis selon les besoins le volume d'incidents, le temps de prise en charge, le temps de rétablissement, les réouvertures, les changements échoués, les retours arrière, les incidents récurrents et les problèmes avec actions en retard. Définis précisément la période, les règles de calcul, les exclusions et la source de données.

Un indicateur qui s'améliore peut masquer un effet indésirable. Une baisse du nombre de tickets peut refléter une sous-déclaration. Une réduction du temps moyen peut résulter de clôtures trop rapides. Compare les chiffres à l'impact utilisateur, à la qualité de résolution et au contexte du service.

## Mise en pratique

### Laboratoire : router correctement quatre scénarios

Pour chaque scénario, sélectionne le flux principal et justifie-le :

1. Un utilisateur ne peut plus accéder à une application utilisée par son équipe.
2. Un nouvel employé demande un accès standard que le responsable a validé.
3. La même erreur revient après trois redémarrages et le service est rétabli à chaque fois.
4. L'équipe doit appliquer une mise à jour de sécurité sur un serveur critique.

Pour le quatrième cas, rédige un dossier de changement minimal : périmètre, risque, fenêtre, sauvegarde ou mécanisme de reprise, tests avant/après, autorisation et critères de retour arrière. Pour le troisième, rattache les incidents et définis une investigation, sans présumer de la cause.

**Résultat attendu :** un tableau qui montre le type de flux, le propriétaire, les preuves requises et les critères de clôture.

## Exercices corrigés

**1. Un incident est rétabli, mais sa cause est encore inconnue. Peut-on clôturer l'incident ?**

Correction : oui si le processus autorise la clôture après validation du service et si les données nécessaires sont conservées. Le problème ou l'analyse de cause doit rester suivi séparément lorsqu'il est nécessaire.

**2. Une mise à jour urgente doit être appliquée. Peut-on ignorer l'analyse de risque ?**

Correction : non. Le processus d'urgence peut être accéléré, mais il doit toujours définir une autorité, les risques acceptés, les étapes, le rétablissement et une revue adaptée.

**3. Pourquoi relier les incidents répétés à un problème ?**

Correction : pour rendre les répétitions visibles, analyser une cause possible, identifier les contournements et préparer des actions de fond plutôt que corriger chaque symptôme isolément.

**4. Une demande d'accès standard est-elle toujours un changement normal ?**

Correction : pas nécessairement. Une demande standard peut suivre un flux préapprouvé, si elle respecte le périmètre, les droits et les contrôles de l'organisation. Une demande qui modifie un service ou un privilège sensible peut nécessiter un autre processus.

## Défi final corrigé

Une équipe redémarre chaque semaine le même service en production. Après le redémarrage, les utilisateurs peuvent travailler. Un ingénieur propose une modification de configuration pour éviter la répétition.

**Correction attendue :** traiter chaque occurrence comme un incident, préserver les preuves et valider le service après le contournement ; ouvrir ou relier un problème pour analyser la répétition ; documenter l'hypothèse technique et la confirmer par des éléments ; préparer la modification comme un changement avec portée, risque, approbation, tests, fenêtre, retour arrière et contrôle post-changement ; puis mesurer si les incidents reviennent. Le redémarrage rétablit le service mais ne démontre pas la cause racine.


## 9. Standard, normal et urgence : décider du chemin du changement

La gestion des changements vise à maximiser les changements réussis en évaluant les risques, en obtenant les autorisations nécessaires et en organisant la mise en œuvre. Un changement **standard** est de faible risque, répétitif et préautorisé dans un cadre défini. Un changement **normal** requiert une évaluation et une autorisation selon la politique. Un changement **d'urgence** répond à une nécessité immédiate et suit un chemin accéléré prévu par l'organisation, avec une revue et une trace après l'action.

N'utilise pas le terme « urgence » uniquement parce qu'une équipe a pris du retard. Un changement d'urgence peut accélérer les décisions, mais ne supprime pas la sécurité, les tests possibles, la responsabilité ni la documentation. La méthode doit préciser quels rôles peuvent autoriser, comment les parties prenantes sont informées, quels tests peuvent être réduits sans risque disproportionné et comment la revue a posteriori sera effectuée.

~~~mermaid
flowchart TD
    A[Demande de changement] --> B[Évaluer le risque et la répétabilité]
    B --> C{Type de changement}
    C -->|Standard préautorisé| D[Contrôles et plan standard]
    C -->|Normal| E[Évaluation et approbation]
    C -->|Urgence justifiée| F[Chemin d'urgence documenté]
    D --> G[Planifier et exécuter]
    E --> G
    F --> G
    G --> H[Tests et revue du résultat]
    H --> I[Clôture et mise à jour des connaissances]
~~~

Une demande de changement utile décrit la raison, le périmètre, les actifs et services affectés, l'impact prévu, les risques, les prérequis, la fenêtre, les tests, le plan de retour, les responsables et les communications. Le but n'est pas de créer une paperasse disproportionnée : c'est de permettre une décision éclairée. Un changement faible peut utiliser un modèle court ; une modification de cœur de réseau ou de schéma de base de données nécessite plus d'analyse.

## 10. Relier incidents, problèmes, changements et connaissances

Un incident décrit une interruption ou une dégradation du service. La gestion des problèmes cherche à réduire la probabilité et l'impact des incidents en identifiant les causes, les solutions de contournement et les erreurs connues. Un changement est une modification d'un service ou d'un composant, souvent nécessaire pour éliminer une cause ou mettre en œuvre une amélioration. Ces enregistrements sont liés, mais ne doivent pas être confondus.

~~~mermaid
flowchart LR
    A[Incidents similaires] --> B[Analyse de problème]
    B --> C[Hypothèse et cause étayée]
    C --> D[Contournement documenté]
    C --> E[Changement proposé]
    E --> F[Évaluation et approbation]
    F --> G[Mise en œuvre et vérification]
    G --> H[Mettre à jour erreur connue et procédure]
    H --> I[Réduire les incidents récurrents]
~~~

Le lien doit permettre d'expliquer pourquoi un changement est nécessaire et quels incidents il cherche à prévenir. Le changement ne doit pas être considéré comme réussi uniquement parce qu'il a été exécuté ; il faut vérifier le résultat attendu, surveiller les effets secondaires et enregistrer les écarts. Si la correction est temporaire, conserve la relation avec le problème ouvert.

La base de connaissances aide le support à appliquer un contournement connu et à éviter des diagnostics redondants. L'article doit préciser les symptômes auxquels il s'applique, les versions concernées, le risque, les limites, la procédure autorisée, les conditions d'arrêt et la date de revue. Une solution copiée d'un ancien ticket ne doit pas être transformée en procédure sans validation.

## 11. Changement et communication des parties prenantes

La communication n'est pas seulement un courriel de début. Elle prépare les utilisateurs, identifie les services potentiellement touchés, décrit la fenêtre, les symptômes possibles et le contact en cas d'écart. Pendant l'intervention, elle signale les étapes majeures et les écarts pertinents. Après, elle confirme les résultats et les limites. La cible du message détermine son niveau de détail.

Le planning des changements sert à repérer les collisions : plusieurs changements peuvent toucher le même service ou la même équipe durant la même fenêtre. Les changements indépendants peuvent être coordonnés pour limiter le coût de mobilisation, mais le regroupement ne doit pas rendre le diagnostic impossible. Si une panne survient, l'historique doit permettre de savoir quelle modification a touché quel actif.

~~~mermaid
sequenceDiagram
    participant P as Propriétaire du service
    participant C as Responsable du changement
    participant O as Opérateur
    participant U as Utilisateurs
    C->>P: Périmètre, risques et fenêtre
    P-->>C: Approbation ou demandes de correction
    C->>U: Avis de maintenance
    C->>O: Autorisation et plan
    O->>O: Exécuter étapes et tests
    O-->>C: Résultat et écarts
    C->>U: État du service et prochaines étapes
~~~

Les incidents survenus après un changement doivent être associés à la chronologie sans présumer automatiquement d'un lien causal. Les données de supervision, les journaux, la version et les résultats des tests aident à évaluer si le changement a contribué au problème. Une revue après mise en œuvre doit examiner les résultats et la qualité de la décision.

## 12. Mesurer la pratique et éviter les indicateurs trompeurs

Les indicateurs peuvent suivre le taux de succès des changements, les changements d'urgence, les incidents associés à un changement, les retours arrière, les erreurs de planification, la qualité des preuves et la durée d'approbation. Chaque indicateur doit définir son numérateur, son dénominateur, la période, la source et les exclusions. Un taux élevé de changements réussis peut cacher une définition du succès trop faible.

Ne cherche pas à réduire artificiellement le nombre de changements d'urgence en reclassant les demandes. Étudie les causes : préparation insuffisante, défaut de planification, vulnérabilité imprévue, dépendance fournisseur ou besoin métier réel. Les indicateurs doivent soutenir l'amélioration, pas punir une équipe au point de la pousser à masquer des événements.

Sources officielles pour approfondir :
- PeopleCert, pratique de gestion des incidents ITIL 4 : https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil4-practices-incident-management-3684
- PeopleCert, pratique Change Enablement : https://www.peoplecert.org/browse-certifications/it-service-management/ITIL-1
- Référentiel des pratiques ITIL 4 : https://www.peoplecert.org/ITIL4-practices

### TP 6 — Qualifier une demande de changement

Un administrateur veut modifier la configuration DNS pour corriger un incident. Le service est partiellement disponible et le contournement est fragile. Prépare la demande, les vérifications, l'autorisation et la communication.

**Correction :** le changement décrit les noms et zones concernés, les observations, les risques, les vérifications de configuration, la fenêtre, le retour arrière, les tests depuis plusieurs clients et les responsables. La gravité de l'incident justifie une priorité, mais le chemin standard, normal ou urgence dépend des règles de l'organisation. Après le changement, vérifie la résolution des noms, les services métier et les alarmes.

### TP 7 — Définir une erreur connue

Plusieurs tickets ont la même erreur, et un contournement fonctionne mais ne supprime pas la cause.

**Correction :** créer ou compléter un enregistrement de problème avec les symptômes, le périmètre, les causes suspectées ou confirmées, le contournement et les limites. Lier les tickets et prévoir la revue. L'article doit indiquer la version et les conditions où le contournement est acceptable.

### TP 8 — Revue après mise en œuvre

Un changement est techniquement déployé, mais les utilisateurs signalent toujours une lenteur.

**Correction :** le succès n'est pas démontré. Comparer les mesures avant/après, tester le parcours métier, ouvrir ou lier un incident, consigner les effets secondaires et décider si un retour ou une investigation complémentaire est nécessaire. La clôture doit correspondre aux critères définis.

## 13. Défi final — Améliorer le traitement des changements

À partir de dix tickets récurrents, propose une façon d'identifier un problème commun, d'évaluer une solution, de créer un changement et d'en vérifier le résultat.

**Correction détaillée :** regrouper les incidents par symptômes et période, établir les preuves, ouvrir ou compléter un problème, définir le risque et les options, obtenir une autorisation adaptée, planifier les tests et le retour, communiquer, exécuter, vérifier et mettre à jour la base de connaissances. Le tableau de bord doit suivre les incidents associés et les retours arrière. Une baisse d'incidents n'est attribuée au changement que si les observations la soutiennent.


## 14. Revue de pratique et amélioration continue

Un processus doit être adapté au volume, au risque et à l'organisation. Une petite équipe peut utiliser quelques catégories et un contrôle de changement simplifié ; une entreprise avec plusieurs sites, des services critiques et des contraintes réglementaires peut avoir besoin de rôles formels, de fenêtres coordonnées, d'un registre des risques et de rapports de qualité. L'important est que les décisions soient adaptées, compréhensibles et traçables.

Lors d'une revue périodique, examine les incidents récurrents, les délais de prise en charge, les changements d'urgence, les retours arrière, les incidents associés à un changement, les problèmes sans propriétaire, les procédures obsolètes et les actions qui restent en retard. Ne traite pas une hausse du nombre de changements d'urgence comme un défaut sans examiner les causes : une vulnérabilité critique peut justifier un chemin d'urgence, mais une mauvaise préparation répétée appelle une amélioration.

~~~mermaid
flowchart TD
    A[Mesures et retours] --> B[Identifier motif récurrent]
    B --> C[Analyser processus et risques]
    C --> D[Décider une amélioration]
    D --> E[Test et approbation]
    E --> F[Mise en œuvre]
    F --> G[Mesurer l'effet]
    G --> H[Revue et ajustement]
~~~

Les pratiques ITIL doivent être utilisées comme un langage commun, non comme une obligation d'adopter un formulaire identique pour toutes les situations. Le service doit choisir les contrôles requis et définir qui prend les décisions. Pour un changement simple et répétitif, un modèle préautorisé peut suffire ; pour une modification risquée du réseau central, il faut un examen plus approfondi et une validation de fin.

La connaissance opérationnelle doit se mettre à jour à partir de l'expérience. Une erreur connue, un article d'aide ou une procédure doit être révisé si le contournement cesse de fonctionner, si les versions changent ou si un test révèle une limite. Un processus mature relie les incidents aux problèmes, aux changements et aux connaissances, puis vérifie si les actions ont réduit la récurrence.


## 15. Qualification et priorisation des incidents

La priorité doit refléter l'impact et l'urgence selon les critères du service. L'impact décrit l'étendue des activités touchées ; l'urgence exprime le temps disponible avant que la conséquence devienne inacceptable. Les niveaux précis, délais et escalades sont établis par l'organisation. Le vocabulaire commun évite qu'un même incident soit classé différemment selon l'insistance de la personne qui le signale.

Une matrice de priorité n'est utile que si elle guide une action. Pour chaque niveau, indique la communication attendue, le délai de prise en charge, le rôle de coordination, l'obligation d'escalade et les critères de sortie. La gravité peut être réévaluée si le périmètre change, si une solution de contournement disparaît ou si de nouvelles informations sont confirmées.

Les mesures doivent éviter d'encourager le sous-classement. Une équipe ne doit pas réduire artificiellement le nombre d'incidents majeurs pour paraître meilleure. Les revues étudient les exemples, les impacts et la justesse des décisions de priorité, plutôt que le seul nombre dans chaque catégorie.
