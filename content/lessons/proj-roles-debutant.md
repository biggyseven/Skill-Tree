# Rôles (Chef de projet, MOA, MOE)

> **Encadré de mise en contexte** — Un projet de déploiement d’un outil de gestion échoue à prendre des décisions car les métiers, l’équipe technique et le fournisseur pensent que les autres sont responsables.

## Introduction

La gestion de projet IT consiste à organiser un changement technique et humain afin de produire un résultat utile dans un environnement où les besoins, les technologies, les contraintes de sécurité et les capacités évoluent. Elle ne se réduit ni à remplir un planning ni à surveiller les personnes. Elle relie une intention métier à des livrables vérifiables, à des décisions explicites et à une adoption effective. Le responsable du projet doit rendre les incertitudes visibles assez tôt pour que l’organisation puisse choisir en connaissance de cause.

Ce cours traite le sujet « Rôles (Chef de projet, MOA, MOE) » sous l’angle pratique. L’objectif n’est pas d’appliquer mécaniquement un modèle universel, mais de comprendre les principes, de reconnaître le contexte et de choisir une méthode proportionnée. Un projet réglementé, une migration d’infrastructure, un produit numérique en exploration et une amélioration interne n’ont pas les mêmes contraintes. Le bon dispositif de pilotage dépend du coût de l’erreur, de la stabilité du besoin, des dépendances, de la taille de l’équipe et de la fréquence à laquelle un résultat exploitable peut être livré.

Le fil rouge du cours est le cas « Le nouveau système de gestion des demandes ». Il permet de relier les concepts à une situation plausible, de formaliser les hypothèses, de raisonner sur les compromis et d’expliquer comment une décision sera contrôlée. Les exemples restent adaptables : les termes contractuels, les exigences de sécurité, le droit applicable et les règles internes doivent être confirmés dans chaque organisation avant une mise en œuvre réelle.

## Objectifs pédagogiques

À la fin de cette leçon, tu devrais pouvoir expliquer les concepts essentiels avec tes propres mots, choisir un outil ou une méthode en fonction d’un besoin concret, construire des preuves de progression, identifier les risques et communiquer une décision aux personnes concernées. Tu devrais également savoir reconnaître les situations où il faut interrompre le travail, solliciter un arbitrage ou réviser une hypothèse plutôt que masquer un écart.

- Définir les termes clés et distinguer les notions souvent confondues.
- Décrire une démarche reproductible et les livrables utiles.
- Relier chaque décision à une personne habilitée, une preuve et un critère.
- Détecter les signaux d’alerte avant qu’ils ne deviennent des incidents majeurs.
- Appliquer les concepts au cas fil rouge et expliquer les limites de la solution choisie.

## Concepts clés

**Résultat et livrable.** Un livrable est un élément produit et vérifiable : application, procédure, modèle, environnement, formation ou rapport. Le résultat décrit ce qui change grâce à ce livrable. Le bénéfice mesure l’amélioration obtenue dans la durée. La distinction évite de déclarer un projet réussi parce qu’un logiciel a été installé alors que personne ne l’utilise ou que le processus reste inefficace.

```mermaid
flowchart TD
    A["Besoin métier"] --> B["MOA : valeur et priorités"]
    B --> C["Chef de projet : coordination"]
    C --> D["MOE : conception et réalisation"]
    D --> E["Recette et acceptation"]
    E --> F["Exploitation et utilisateurs"]
    F --> G["Mesure des bénéfices"]
    G -. "retour d'expérience" .-> B
```

Ce parcours représente une chaîne de responsabilité, pas une cascade où chaque rôle travaillerait en silo. Le chef de projet organise les interfaces et rend visibles les décisions ; la MOA demeure responsable de la pertinence métier et l’équipe de réalisation de la qualité technique de ce qu’elle livre. L’acceptation et la mesure des bénéfices ferment la boucle.

**Valeur et critères de succès.** La valeur doit être reliée à un besoin réel, à un bénéficiaire identifiable et à un effet attendu. Un objectif vague comme « moderniser le système » doit être traduit en résultats observables : réduction du délai, diminution d’erreurs, meilleure disponibilité, baisse d’un coût ou amélioration de l’expérience. Les indicateurs doivent être définis avant la livraison, avec une valeur de référence et un horizon de mesure.

**Périmètre et exigences.** Le périmètre définit ce que le projet prend en charge et ce qu’il ne prend pas en charge. Les exigences expriment les comportements attendus, les contraintes non fonctionnelles et les règles d’acceptation. Une demande nouvelle n’est pas automatiquement mauvaise, mais elle doit être analysée. Il faut décider si elle remplace une exigence, s’ajoute au périmètre, devient un lot ultérieur ou n’est pas retenue.

**Référence et prévision.** Une référence approuvée sert à mesurer l’écart ; une prévision décrit l’état le plus probable à partir de la situation connue. Une équipe peut conserver une baseline et prévoir une date différente sans manipuler les chiffres. Un écart n’est pas nécessairement une faute : l’absence d’explication, la répétition de surprises et la non-escalade des conséquences sont en revanche des problèmes de gouvernance.

**Gouvernance et transparence.** La gouvernance précise les rôles, les droits de décision, les seuils d’escalade et la manière de traiter les changements. Elle ne doit pas imposer une réunion de comité pour chaque détail. Les décisions fréquentes et réversibles peuvent être déléguées à l’équipe, alors que les décisions coûteuses, réglementaires ou difficiles à inverser exigent une autorité définie et une trace exploitable.

**Risque et incertitude.** Un risque est un événement incertain susceptible d’affecter les objectifs. Un problème est déjà survenu ; une hypothèse reste à confirmer ; une dépendance associe le projet à un acteur ou à un autre travail. Les confondre rend les plans moins utiles. Les risques doivent avoir des propriétaires, des signaux de déclenchement et des réponses proportionnées à leur probabilité et à leur impact.

**Qualité intégrée.** La qualité ne se vérifie pas uniquement à la fin. Elle se construit par des critères, des revues, des tests, des environnements de validation et des contrôles de sécurité adaptés. Un projet qui accélère en supprimant les tests obligatoires peut simplement déplacer son coût vers l’exploitation. Les critères d’acceptation doivent être compris par le métier et techniquement réalisables.

**Adoption et transition.** Une livraison réussie doit être exploitable, supportable et comprise. La transition inclut l’appropriation, les procédures, le support, les habilitations, la supervision, les sauvegardes, le retour arrière et la formation. Les bénéficiaires ne sont pas de simples destinataires d’un changement : leurs retours peuvent révéler des contraintes non identifiées et orienter l’ordre des priorités.

## Méthodologie et outils

La démarche de pilotage peut être prédictive lorsque les exigences sont relativement stables et qu’une planification détaillée est utile, adaptative lorsque le besoin est incertain et que l’apprentissage doit se faire par petits incréments, ou hybride lorsque des composants présentent des niveaux d’incertitude différents. Choisir une méthode ne dispense jamais de clarifier la valeur, les responsabilités, les risques, la qualité et les critères de décision.

Les outils sont au service d’une pratique, pas l’inverse. Un tableau peut rendre le travail visible, un diagramme de Gantt montrer les dépendances calendaires, un registre expliciter les risques et un journal de décisions préserver la mémoire des arbitrages. Aucun outil ne compense des données inexactes, un périmètre flou ou l’absence de responsable. Avant d’adopter un outil, définir les décisions qu’il doit soutenir et qui maintiendra les informations.

L’information doit être adaptée à son public. L’équipe a besoin de détails opérationnels et de blocages immédiats ; le sponsor a besoin des résultats, risques majeurs, options d’arbitrage et conséquences ; les utilisateurs ont besoin de connaître l’impact, les dates, les changements de processus et l’aide disponible. Une communication efficace associe un message compréhensible, un canal adapté, une fréquence raisonnable et une voie de retour.

Voici un modèle de raisonnement à utiliser pour chaque décision importante : constater la situation, vérifier les faits, comparer des options, évaluer les effets sur la valeur et les contraintes, désigner une personne habilitée, décider, consigner puis vérifier le résultat. Il évite les décisions prises uniquement sous pression et permet de revenir sur une hypothèse lorsque de nouvelles informations apparaissent.

```mermaid
flowchart LR
S[Sponsor] --> CP[Chef de projet]
MOA[MOA / représentant métier] --> CP
MOE[MOE / équipe de réalisation] --> CP
CP --> GOV[Comité de pilotage]
MOA <--> MOE
GOV --> DEC[Arbitrages et décisions]
DEC --> CP
```

### 1. Sponsor

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », sponsor doit être traité comme un élément de décision et non comme une formalité isolée. Le sponsor porte la justification, assure le soutien exécutif et tranche les décisions hors délégation du chef de projet. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart TD
    A["Sponsor"] --> B["Confirme la justification"]
    A --> C["Sécurise les moyens"]
    A --> D["Arbitre les décisions majeures"]
    E["Chef de projet"] --> F["Prépare options et impacts"]
    F --> A
    D --> G["Décision et mandat clarifiés"]
    G --> E
```

Le sponsor ne doit pas se substituer au chef de projet dans le suivi quotidien. Il donne une direction, protège le projet contre les blocages organisationnels et tranche les sujets qui dépassent les délégations convenues. Le chef de projet lui fournit une analyse factuelle, plusieurs options réalistes et une recommandation explicite.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Le sponsor arbitre entre une exigence supplémentaire et le respect du budget approuvé. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 2. Chef de projet

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », chef de projet doit être traité comme un élément de décision et non comme une formalité isolée. Le chef de projet intègre planning, coût, périmètre, risques, qualité, dépendances et communication sans nécessairement commander hiérarchiquement les experts. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart LR
    A["Périmètre"] --> E["Pilotage intégré"]
    B["Délais et coûts"] --> E
    C["Risques et qualité"] --> E
    D["Équipe et communication"] --> E
    E --> F["Prévisions et décisions"]
    F --> G["Livraison cohérente"]
```

Le chef de projet réunit les dimensions qui sont souvent gérées séparément. Une modification technique peut impacter le coût, le délai, la sécurité et la formation ; son rôle est de rendre ces liens visibles, de faire instruire le changement par les personnes compétentes et de maintenir une prévision cohérente. Il coordonne sans prétendre posséder toutes les expertises.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Il coordonne une équipe transversale et rend les arbitrages visibles plutôt que de promettre seul toutes les dates. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 3. MOA et représentant métier

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », moa et représentant métier doit être traité comme un élément de décision et non comme une formalité isolée. La maîtrise d’ouvrage exprime le besoin, priorise la valeur, valide les processus et organise l’acceptation métier. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart TD
    A["Utilisateurs et métiers"] --> B["MOA recueille les besoins"]
    B --> C["Priorisation et critères d'acceptation"]
    C --> D["Dialogue avec la MOE"]
    D --> E["Démonstration et recette"]
    E --> F{"Critères satisfaits ?"}
    F -- "Oui" --> G["Acceptation métier"]
    F -- "Non" --> H["Écarts documentés"]
    H --> D
```

La MOA transforme les demandes en résultats attendus et en critères observables. Elle ne se limite pas à transmettre un cahier des charges initial : elle clarifie les ambiguïtés, priorise lorsque tout ne peut pas être réalisé immédiatement et organise l’acceptation avec des représentants habilités. Les écarts doivent être documentés plutôt que réglés par une impression générale.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Le représentant métier définit les critères d’acceptation d’une demande et confirme que le processus cible répond au besoin. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 4. MOE et réalisation technique

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », moe et réalisation technique doit être traité comme un élément de décision et non comme une formalité isolée. La maîtrise d’œuvre conçoit, construit, intègre et teste la solution selon les exigences, les contraintes techniques et les niveaux de service. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart TD
    A["Exigences approuvées"] --> B["Architecture et conception"]
    B --> C["Réalisation et intégration"]
    C --> D["Tests techniques et sécurité"]
    D --> E{"Preuves conformes ?"}
    E -- "Oui" --> F["Version proposée à la recette"]
    E -- "Non" --> G["Correction et nouveaux tests"]
    G --> D
```

La MOE choisit et met en œuvre une solution compatible avec les exigences, l’architecture, la sécurité, les contraintes d’exploitation et les délais convenus. Elle doit rendre la qualité démontrable : résultats de tests, documentation, éléments de configuration et limites connues. La validation technique ne remplace toutefois pas l’acceptation métier.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** L’équipe technique explicite les limites d’une API et propose plusieurs options d’architecture avec leurs impacts. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 5. Product Owner

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », product owner doit être traité comme un élément de décision et non comme une formalité isolée. Dans Scrum, le Product Owner maximise la valeur du produit et ordonne le Product Backlog ; le rôle n’est pas simplement un secrétaire de demandes. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart TD
    A["Objectifs du produit"] --> B["Product Owner"]
    C["Retours utilisateurs"] --> B
    D["Contraintes et dépendances"] --> B
    B --> E["Product Backlog ordonné"]
    E --> F["Équipe sélectionne le travail réalisable"]
    F --> G["Incrément vérifiable"]
    G --> C
```

Dans Scrum, le Product Owner est responsable de maximiser la valeur du produit et de gérer efficacement le Product Backlog. Il ne distribue pas individuellement toutes les tâches à l’équipe. Le chef de projet, lorsqu’il existe en parallèle, doit clarifier les interfaces de gouvernance, budget, dépendances ou reporting au lieu de créer une seconde autorité concurrente sur le backlog.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Le Product Owner ordonne les demandes selon valeur, risque, dépendances et apprentissage, puis explique les choix. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 6. Équipe de réalisation

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », équipe de réalisation doit être traité comme un élément de décision et non comme une formalité isolée. L’équipe pluridisciplinaire estime et réalise le travail ; sa contribution ne doit pas être remplacée par des engagements irréalistes décidés hors équipe. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart LR
    A["Analyse et conception"] --> B["Construction"]
    B --> C["Revue par les pairs"]
    C --> D["Tests automatisés et manuels"]
    D --> E["Intégration"]
    E --> F["Démonstration et retour"]
    F -. "amélioration" .-> A
```

Le travail de réalisation exige une collaboration continue entre développement, infrastructure, qualité, sécurité et exploitation selon la nature du projet. Les revues, les tests et les démonstrations sont des pratiques partagées : elles ne devraient pas être reportées à la fin ni reposer uniquement sur la confiance dans une déclaration de tâche terminée.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Les développeurs et testeurs définissent ensemble une approche réalisable et identifient la capacité nécessaire à la qualité. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 7. RACI

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », raci doit être traité comme un élément de décision et non comme une formalité isolée. Une matrice RACI clarifie qui réalise, qui est redevable, qui est consulté et qui est informé pour une activité donnée. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart TD
    A["Lister les activités et décisions"] --> B["Identifier les personnes concernées"]
    B --> C["Attribuer R : réalise"]
    C --> D["Attribuer A : redevable"]
    D --> E["Définir C : consulté"]
    E --> F["Définir I : informé"]
    F --> G{"Un seul A par activité ?"}
    G -- "Oui" --> H["Valider avec les acteurs"]
    G -- "Non" --> D
    H --> I["Réviser lors des changements"]
```

Une RACI est utile lorsqu’elle porte sur des activités concrètes, par exemple « approuver le plan de migration » ou « accepter la recette », plutôt que sur des intitulés vagues. Le rôle A doit être unique pour éviter deux redevabilités finales incompatibles ; plusieurs R peuvent contribuer. La matrice doit refléter l’autorité réelle et rester assez simple pour être utilisée.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** La validation sécurité a un responsable d’exécution identifié, un décideur final et des experts consultés avant approbation. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 8. Comité de pilotage

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », comité de pilotage doit être traité comme un élément de décision et non comme une formalité isolée. Le comité suit la santé du projet, prend les décisions dépassant les délégations et protège l’alignement stratégique. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart TD
    A["Chef de projet consolide les faits"] --> B["Prépare options, impacts et recommandation"]
    B --> C["Comité de pilotage"]
    C --> D{"Décision dans le mandat ?"}
    D -- "Oui" --> E["Arbitrage consigné"]
    D -- "Non" --> F["Escalade au sponsor ou à l'autorité"]
    E --> G["Responsable et échéance désignés"]
    F --> G
    G --> H["Suivi de l'exécution"]
```

Un bon comité de pilotage ne se limite pas à recevoir des diapositives de statut. Les décisions attendues sont formulées à l’avance, accompagnées des impacts et d’une échéance. Le compte rendu consigne la décision, son propriétaire, les conditions éventuelles et la date de réexamen ; sans cette trace, la même question risque de revenir à chaque réunion.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Le comité choisit entre une réduction de périmètre, des moyens supplémentaires ou un changement de calendrier. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 9. Responsable sécurité et conformité

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », responsable sécurité et conformité doit être traité comme un élément de décision et non comme une formalité isolée. Le RSSI ou le responsable conformité formule les exigences et apporte les décisions relevant de son mandat, sans devenir propriétaire de tous les risques métier. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart TD
    A["Besoins et données identifiés"] --> B["Analyse des risques et obligations"]
    B --> C["Exigences de sécurité et conformité"]
    C --> D["Conception et réalisation"]
    D --> E["Contrôles et preuves"]
    E --> F{"Risque résiduel acceptable ?"}
    F -- "Oui, par l'autorité habilitée" --> G["Autorisation selon le processus prévu"]
    F -- "Non" --> H["Mesures correctives ou arbitrage"]
    H --> D
```

Le responsable sécurité conseille, contrôle et alerte selon son mandat ; il ne doit pas être impliqué seulement à la veille de la mise en production. Les exceptions doivent documenter le risque, les mesures compensatoires, la durée et l’autorité qui accepte le risque. Un chef de projet ne peut pas déclarer seul acceptable un risque pour lequel il n’a pas délégation.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Une analyse de risque détermine les contrôles d’accès, la journalisation et la conservation des données. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 10. Fournisseur et intégrateur

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », fournisseur et intégrateur doit être traité comme un élément de décision et non comme une formalité isolée. Les fournisseurs doivent avoir des livrables, critères, interfaces, délais, obligations de sécurité et mécanismes d’escalade contractuellement clarifiés. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart LR
    A["Contrat et périmètre"] --> B["Livrables et critères mesurables"]
    B --> C["Fournisseur réalise"]
    C --> D["Revues et preuves de conformité"]
    D --> E{"Livrable conforme ?"}
    E -- "Oui" --> F["Acceptation contractuelle"]
    E -- "Non" --> G["Réserves et plan de correction"]
    G --> C
    F --> H["Transfert de connaissances"]
```

L’externalisation d’une tâche ne transfère pas automatiquement toute la responsabilité du résultat. Le contrat, les niveaux de service, les dépendances, les droits d’accès, la propriété des livrables et les conditions d’acceptation doivent être explicites. Le transfert de connaissances et la réversibilité sont à planifier au même titre que la livraison.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Le contrat lie la livraison d’un connecteur à une recette mesurable et à la remise de la documentation. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 11. Délégation et escalade

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », délégation et escalade doit être traité comme un élément de décision et non comme une formalité isolée. Une délégation fixe les décisions qu’un rôle peut prendre ; l’escalade intervient lorsque seuils ou responsabilités sont dépassés. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart TD
    A["Un problème ou changement apparaît"] --> B["Qualifier l'impact et l'urgence"]
    B --> C{"Dans les seuils délégués ?"}
    C -- "Oui" --> D["Décision par le rôle habilité"]
    C -- "Non" --> E["Préparer dossier d'escalade"]
    E --> F["Autorité compétente ou sponsor"]
    F --> G["Décision, conditions et délai"]
    D --> H["Consigner et communiquer"]
    G --> H
    H --> I["Suivre le résultat"]
```

Une délégation efficace indique le type de décision, les seuils, les limites, la personne suppléante et les cas à escalader. Un chef de projet peut souvent réorganiser une séquence de tâches dans les limites convenues, mais une hausse significative du budget, une modification de l’objectif ou l’acceptation d’un risque majeur peut nécessiter un sponsor ou un comité.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Le chef de projet peut déplacer une tâche dans la marge disponible, mais pas modifier seul une obligation réglementaire. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 12. Conflit d’intérêts

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », conflit d’intérêts doit être traité comme un élément de décision et non comme une formalité isolée. Un désaccord doit être traité sur des objectifs, preuves, options et impacts, pas par statut ou accusation personnelle. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

```mermaid
flowchart TD
    A["Désaccord identifié"] --> B["Séparer faits, hypothèses et préférences"]
    B --> C["Reformuler l'objectif commun"]
    C --> D["Établir plusieurs options"]
    D --> E["Comparer valeur, coût, délai et risques"]
    E --> F{"Accord dans le mandat ?"}
    F -- "Oui" --> G["Décision et engagement"]
    F -- "Non" --> H["Médiation ou arbitrage"]
    H --> G
    G --> I["Documenter et réévaluer"]
```

Un conflit est souvent le symptôme d’objectifs, d’incitations ou de responsabilités non alignés. La discussion gagne à partir de faits vérifiables et de critères partagés plutôt que du rang hiérarchique. Quand un compromis n’est pas possible, le bon réflexe consiste à appliquer la voie d’arbitrage connue et à consigner les conséquences acceptées.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Le métier demande une fonctionnalité, l’exploitation refuse une date risquée et le chef de projet compare les options. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

### 13. Responsabilité et reddition de comptes

**Comprendre le sujet.** Dans le cadre de « Rôles (Chef de projet, MOA, MOE) », responsabilité et reddition de comptes doit être traité comme un élément de décision et non comme une formalité isolée. L’accountability exige un responsable clairement redevable du résultat, même si l’exécution est distribuée. La bonne pratique consiste à expliciter le but recherché, l’autorité concernée, les hypothèses encore ouvertes, les contraintes applicables et la preuve qui permettra de conclure. Sans cette explicitation, deux personnes peuvent utiliser les mêmes mots tout en poursuivant des résultats différents. Le responsable doit demander ce qui est attendu, pourquoi cela compte et quelle conséquence aurait une décision erronée.

**Relier le principe à l’ensemble du projet.** Un élément de gestion n’agit jamais seul. Il influence le périmètre, la date, le budget, la qualité, la charge et l’acceptation du résultat. Avant d’agir, vérifier les dépendances en amont et en aval, identifier les équipes qui seront touchées et repérer les décisions qui pourraient être difficiles à inverser. Une solution locale apparemment efficace peut créer une dette opérationnelle, un défaut de conformité ou un coût de support durable. Une décision solide rend ces effets visibles et explique les compromis.

**Application au terrain.** Le responsable de recette ne peut pas être supposé différent selon les réunions ; la décision et sa trace doivent rester explicites. Pour transformer cet exemple en action, commencer par écrire une description courte de la situation, puis distinguer les faits observés des hypothèses. Identifier un responsable, convenir d’un résultat attendu et fixer le moment où la preuve sera examinée. Si une information manque, créer une tâche d’investigation avec une échéance plutôt que présenter une supposition comme une certitude. Si plusieurs options sont acceptables, comparer explicitement leurs impacts, leurs coûts de réversibilité et leurs conséquences pour les utilisateurs.

**Déroulement recommandé.** Premièrement, recueillir les données utiles auprès des personnes les plus proches du travail. Deuxièmement, vérifier la cohérence des informations avec les documents déjà approuvés. Troisièmement, décrire les options réalistes et leurs limites. Quatrièmement, décider au niveau approprié, en précisant les seuils qui nécessiteraient une escalade. Cinquièmement, consigner la décision, informer les personnes concernées et suivre son effet. Cette séquence réduit les retours en arrière et rend la démarche reproductible, même si les outils ou l’organisation changent.

**Mesures et éléments de preuve.** Une affirmation telle que « le travail avance » doit être étayée par une preuve pertinente : un livrable relu, un test passé, une décision approuvée, une dépendance levée, une mesure comparée à sa référence ou un utilisateur ayant réalisé une tâche. Choisir un indicateur directement relié à l’objectif et préciser sa source, sa fréquence, son propriétaire et ses limites. Les indicateurs quantitatifs gagnent à être complétés par une observation qualitative, particulièrement lorsqu’il est question d’adoption, de satisfaction ou de risque humain.

**Signaux d’alerte et correction.** Les signaux typiques sont une définition contradictoire, une décision repoussée sans propriétaire, des changements non évalués, une preuve difficile à retrouver, une estimation donnée sans hypothèse ou un résultat déclaré acceptable sans critères. Face à ces signaux, ne pas multiplier les tableaux ni demander une mise à jour cosmétique. Revenir au besoin, vérifier les faits, attribuer la responsabilité manquante et réduire le problème à une décision explicite. Si l’impact dépasse la délégation prévue, alerter rapidement avec des options et une recommandation argumentée.

**Approfondissement.** Pour les projets à forte criticité, la rigueur doit augmenter avec le coût d’une erreur : revue indépendante, approbation formelle, contrôle des accès, traçabilité renforcée ou répétition en environnement représentatif. Pour un petit projet réversible, la même intention peut être satisfaite par un contrôle plus léger. Le principe est de calibrer les pratiques sans abolir les contrôles essentiels. À chaque étape, demander : « Quelle preuve rend cette décision défendable, qui peut l’accepter et qu’est-ce qui nous ferait changer d’avis ? »

## Étude de cas : Le nouveau système de gestion des demandes

La direction métier porte les besoins, l’équipe IT construit les interfaces, le RSSI impose des exigences de sécurité et un intégrateur livre une partie de la solution. Les décisions restent bloquées faute d’attribution claire.

```mermaid
flowchart TD
    A["Métier décrit le problème et les résultats attendus"] --> B["MOA priorise et définit la recette"]
    B --> C["MOE propose la solution et les estimations"]
    C --> D["Sécurité et exploitation examinent les contraintes"]
    D --> E["Chef de projet consolide risques, coûts et planning"]
    E --> F{"Arbitrage nécessaire ?"}
    F -- "Non" --> G["Équipe exécute dans le mandat"]
    F -- "Oui" --> H["Sponsor ou comité décide"]
    H --> G
    G --> I["Recette, acceptation et transfert"]
```

Cette séquence évite qu’une personne soit supposée approuver tous les aspects. Le métier décide si le résultat répond au besoin, la MOE démontre que la solution respecte les exigences techniques, les spécialistes évaluent leurs domaines de contrôle et l’autorité de gouvernance arbitre les écarts qui dépassent le mandat du projet.

### 1. Clarifier la demande

L’équipe commence par reformuler le problème du point de vue des bénéficiaires, les résultats attendus et les contraintes non négociables. Elle distingue les faits, les hypothèses et les préférences. Elle identifie ensuite le sponsor, le propriétaire métier, le responsable technique, les personnes chargées de la sécurité et l’exploitant qui recevra la solution. Ce travail empêche de supposer que la personne qui demande une fonctionnalité possède automatiquement le budget, l’autorité ou la connaissance nécessaires pour valider toutes les décisions.

### 2. Définir une base de travail

Le groupe rédige une courte charte, délimite un premier périmètre, formule des critères d’acceptation et estime le travail en indiquant l’incertitude. Il établit une première liste de dépendances, prépare une analyse de risques et fixe la fréquence de pilotage. Les estimations sont présentées comme des fourchettes lorsque les informations sont incomplètes. Le plan comporte aussi les activités souvent oubliées : préparation des environnements, validation de sécurité, transfert aux opérations, communication, formation et retour arrière.

### 3. Comparer les options

Trois options plausibles sont comparées : livrer tout le périmètre en une seule bascule, livrer un premier lot limité, ou reporter pour résoudre les incertitudes critiques. La comparaison porte sur la valeur obtenue, le coût, la durée, la complexité, les risques et la réversibilité. Une option ne doit pas être retenue uniquement parce qu’elle paraît plus rapide sur le calendrier. Il faut mesurer les conséquences des incidents, les besoins de support et la capacité réelle de l’organisation à absorber le changement.

### 4. Piloter l’exécution et l’acceptation

L’équipe suit des résultats vérifiables, pas uniquement le pourcentage de tâches déclarées terminées. Les critères d’acceptation sont associés à des tests et à des preuves dont les responsables sont désignés. Les écarts sont analysés par rapport à la référence et accompagnés d’une prévision actualisée. Si une décision dépasse l’autorité du chef de projet, le comité reçoit une note concise présentant la situation, les options, les impacts, la recommandation et la date limite de décision.

```mermaid
flowchart TD
    A["Critères d'acceptation convenus"] --> B["Responsable et preuve associés à chaque critère"]
    B --> C["Tests et démonstration"]
    C --> D{"Résultats conformes ?"}
    D -- "Oui" --> E["Décision formelle d'acceptation"]
    D -- "Non" --> F["Décrire les écarts et leurs impacts"]
    F --> G["Corriger, différer ou accepter une dérogation autorisée"]
    G --> C
    E --> H["Transfert vers exploitation et mesure des bénéfices"]
```

Il faut distinguer l’exécution des tests, l’avis technique et la décision d’acceptation. La personne qui exécute un test n’est pas nécessairement habilitée à accepter le résultat métier. Toute réserve importante doit préciser son impact, son responsable, son échéance et l’autorité qui accepte éventuellement le risque associé.

### 5. Tirer les leçons

La clôture vérifie que les livrables ont été acceptés, que les responsabilités d’exploitation sont formalisées, que la documentation est accessible et que les risques résiduels sont acceptés par une personne autorisée. Les bénéfices qui ne peuvent être mesurés qu’après plusieurs semaines sont confiés à un responsable métier avec une date de mesure. Une courte rétrospective identifie ce qu’il faut conserver, arrêter ou expérimenter au prochain projet.

## Atelier pratique

**Exercice.** Rédige une fiche de cadrage d’une page pour le cas étudié. Elle doit contenir : le problème, les bénéficiaires, les objectifs mesurables, les inclusions et exclusions, les contraintes, cinq parties prenantes, trois risques, trois critères d’acceptation et la personne qui décide lorsqu’un seuil est dépassé.

**Correction attendue.** Une bonne réponse ne se limite pas à une liste de fonctionnalités. Elle établit un lien vérifiable entre problème et bénéfice, précise une référence de départ, distingue les exigences obligatoires des options, attribue les risques à des propriétaires et fixe des critères que le métier peut comprendre. Chaque décision majeure doit avoir un responsable et une voie d’escalade. Les données manquantes sont clairement notées comme hypothèses à confirmer, avec un propriétaire et une échéance.

**Exercice avancé.** Le sponsor demande d’avancer la date de livraison de trois semaines alors que deux contrôles ne sont pas terminés. Prépare trois options avec leurs conséquences : conserver la date en réduisant un périmètre non essentiel, renforcer les moyens si les compétences sont disponibles, ou déplacer la date. La correction doit refuser de présenter une validation non réalisée comme acquise. Les contrôles de sécurité et les critères obligatoires ne doivent pas être supprimés pour rendre artificiellement le planning vert.

## Pièges à éviter

- Confondre activité, livrable et bénéfice : terminer des tâches ne prouve pas que le besoin est résolu.
- Définir le succès après la livraison : cela ouvre la voie à des critères changeants et à des déclarations invérifiables.
- Croire qu’un outil remplace la gouvernance : un tableau bien rempli ne clarifie pas qui décide.
- Cacher les incertitudes : une fourchette honnête vaut mieux qu’une date précise sans justification.
- Valider seulement le scénario idéal : les cas limites, la sécurité et le retour arrière doivent être considérés.
- Laisser la responsabilité implicite : les sujets sans propriétaire ont tendance à être ignorés.
- Traiter les utilisateurs comme de simples destinataires : leur préparation conditionne l’adoption.
- Faire évoluer le périmètre sans analyser les impacts : le coût peut apparaître tardivement.
- Escalader sans recommandation : présenter des faits, options, impacts et une date limite de décision.
- Fermer le projet au moment de la mise en production : le support, la stabilisation et les bénéfices ont aussi besoin d’un propriétaire.

## Checklist de révision

- [ ] Le besoin et les bénéficiaires sont formulés clairement.
- [ ] Les objectifs sont mesurables et associés à une référence.
- [ ] Le périmètre et les exclusions sont visibles.
- [ ] Les rôles, pouvoirs de décision et escalades sont explicites.
- [ ] Les hypothèses, risques et dépendances possèdent des propriétaires.
- [ ] Le planning et le budget exposent leurs hypothèses.
- [ ] Les critères d’acceptation sont testables.
- [ ] Les décisions et changements sont tracés.
- [ ] L’exploitation, la sécurité et l’adoption sont préparées.
- [ ] La clôture inclut transfert, leçons et mesure des bénéfices.

## À retenir

Le pilotage de projet est un exercice d’alignement, de décision et d’apprentissage. Une méthode efficace apporte juste assez de structure pour rendre le travail prévisible sans prétendre supprimer l’incertitude. Les livrables, les rôles, les estimations, les risques et les critères de réussite doivent former un système cohérent. Le chef de projet crée de la valeur lorsqu’il aide les personnes compétentes à prendre les bonnes décisions au bon moment, en disposant de faits compréhensibles et d’une trace utile.

## Glossaire

- **Baseline :** référence approuvée utilisée pour comparer les résultats.
- **Bénéfice :** amélioration mesurable obtenue grâce au résultat.
- **Dépendance :** lien qui conditionne l’ordre ou la faisabilité du travail.
- **Jalon :** événement important permettant de vérifier une étape.
- **Livrable :** résultat concret pouvant être vérifié et accepté.
- **Partie prenante :** personne ou organisation qui influence le projet ou en subit les effets.
- **Périmètre :** limites des travaux et des résultats inclus.
- **Risque :** événement incertain pouvant modifier les objectifs.
- **Sponsor :** responsable exécutif qui porte la justification et les arbitrages majeurs.
- **Critère d’acceptation :** condition observable permettant de déclarer un résultat acceptable.

## Références pour approfondir

- ISO 21502, lignes directrices sur le management de projet : https://committee.iso.org/sites/tc258/home/projects/published/iso-21502.html
- Project Management Institute (PMI) : https://www.pmi.org/
- Scrum Guide officiel : https://scrumguides.org/scrum-guide
- PRINCE2 7, présentation officielle : https://www.peoplecert.org/browse-certifications/project-programme-and-portfolio-management/PRINCE2-2/prince2-7-foundation-3579
