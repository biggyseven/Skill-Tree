# Méthodologies hybrides Agile/Waterfall

> **Encadré de mise en contexte** — Un programme comprend du matériel commandé longtemps à l’avance, une infrastructure réglementée et une application dont les besoins s’affinent par les retours utilisateurs.

## Introduction

La gestion de projet IT transforme une demande parfois imprécise en résultats utiles grâce à des décisions explicites. Les outils de pilotage ne suppriment pas l’incertitude : ils rendent les hypothèses, les responsabilités, les dépendances et les écarts visibles. Une pratique bien choisie aide les personnes compétentes à se coordonner, à détecter les problèmes tôt et à choisir le bon compromis entre valeur, délais, coûts, qualité, sécurité et adoption.

Ce cours sur « Méthodologies hybrides Agile/Waterfall » privilégie les méthodes applicables dans un environnement réel. Une pratique n’est utile que si elle répond à un besoin précis. Il faut calibrer le niveau de détail en fonction de la criticité, du coût de l’erreur, de la stabilité du périmètre et des obligations externes. Un petit projet réversible peut s’appuyer sur un dispositif léger, alors qu’une transformation importante ou un programme réglementé exige des preuves plus formelles.

Le cas « Moderniser une plateforme bancaire » sert de fil rouge. Il permet de distinguer les faits des hypothèses, d’identifier les décisions qui conditionnent le résultat et de construire une manière de vérifier l’effet des choix. Les outils cités sont des exemples : leurs fonctions évoluent, les offres commerciales changent et chaque organisation doit vérifier ses règles, ses contrats et ses contraintes de conformité avant de les utiliser.

## Objectifs pédagogiques

- Expliquer les concepts de base et les limites des méthodes étudiées.
- Choisir une approche adaptée à la nature du travail et à l’incertitude.
- Décrire les étapes, livrables, responsabilités et contrôles associés.
- Mesurer les résultats avec des indicateurs reliés aux objectifs.
- Appliquer la démarche au cas proposé et justifier les arbitrages.

## Concepts clés

**Valeur.** La valeur décrit le bénéfice recherché pour un utilisateur ou l’organisation. Elle doit être reliée à une situation initiale, à un changement attendu et à une mesure raisonnable. Sans cette relation, l’équipe risque d’optimiser un outil ou un processus sans résoudre le problème métier.

```mermaid
flowchart TD
    A["Besoins, incertitude et contraintes"] --> B["Choisir le cycle de vie par composant"]
    B --> C["Plan directeur et jalons de gouvernance"]
    B --> D["Backlog et livraisons incrémentales"]
    C --> E["Architecture, sécurité et conformité"]
    D --> E
    E --> F["Intégration et preuves de qualité"]
    F --> G["Décisions aux portes de contrôle"]
    G --> H["Livraison, adoption et bénéfices"]
    H --> I["Retour d'expérience et adaptation"]
    I --> B
```

Une approche hybride combine des éléments prédictifs et adaptatifs de manière intentionnelle. Elle ne consiste pas à juxtaposer un Gantt et un tableau agile : les équipes doivent clarifier quelles décisions sont prises à long terme, quelles parties du produit sont livrées par incréments, comment les dépendances sont gérées et quelles preuves sont exigées avant chaque jalon. La méthode est choisie au niveau pertinent — projet, flux de travail, produit ou composant — en fonction de l’incertitude, du coût de changement et des obligations.

**Périmètre et qualité.** Le périmètre fixe les limites du travail ; la qualité précise les caractéristiques et critères qui permettront d’accepter les livrables. Les ajouts doivent être analysés au lieu d’être acceptés implicitement. Une date ou un budget ne justifie jamais de prétendre qu’un critère obligatoire est satisfait sans preuve.

**Prévision et référence.** La référence approuvée permet d’étudier les écarts, tandis que la prévision décrit l’issue la plus probable à partir des données actuelles. On peut réviser une prévision et conserver une référence historique. La distinction préserve la transparence et aide à décider sans maquiller les évolutions.

**Gouvernance.** La gouvernance répartit les responsabilités, les pouvoirs de décision, les seuils d’escalade et les mécanismes de validation. Elle doit soutenir le travail plutôt que le bloquer. Les décisions fréquentes et réversibles sont généralement déléguées ; les décisions coûteuses, risquées ou réglementaires nécessitent une autorité et une trace explicites.

**Risque et dépendances.** Un risque correspond à un événement incertain et à ses conséquences éventuelles. Une dépendance relie le projet à un système, une équipe, un fournisseur ou une approbation. Les réponses doivent avoir un propriétaire, un signal et une action. Une dépendance non suivie peut transformer une activité courte en facteur de retard global.

**Communication.** Une information est efficace quand elle permet à son destinataire de comprendre la situation et d’agir. L’équipe a besoin de détails opérationnels, le sponsor d’options d’arbitrage et les utilisateurs de connaître les impacts. Les rapports doivent distinguer faits observés, hypothèses, risques et décisions attendues.

**Adoption et transfert.** Le résultat doit pouvoir être utilisé, maintenu et supporté. Les responsabilités d’exploitation, les accès, la documentation, la formation, la supervision et la continuité doivent être préparés avant la mise en service. Les bénéfices peuvent nécessiter une mesure plusieurs semaines après la livraison.

## Méthodologie et outils

Commencer par formuler le problème, les bénéficiaires, le résultat attendu et les contraintes non négociables. Décrire ensuite les options, les dépendances, les responsabilités, les risques et les preuves nécessaires. La planification fournit une hypothèse structurée ; elle doit être révisée lorsque de nouveaux faits modifient le travail restant ou les conditions de réussite.

Les outils servent à externaliser la mémoire collective. Ils doivent permettre de répondre à des questions concrètes : quel résultat est attendu, qui le prend en charge, qu’est-ce qui est bloqué, quelle décision est en attente, quelle preuve existe et comment la prévision change-t-elle ? La simplicité est une qualité si les contrôles essentiels restent couverts et si les données sont maintenues.

Un reporting utile ne récompense pas seulement le volume d’activité. Il met en évidence le travail réellement terminé, les critères qui restent ouverts, les risques qui évoluent et les arbitrages nécessaires. Les estimations doivent exposer leurs hypothèses, les marges doivent être explicables et les mesures doivent être comprises par ceux qui les utilisent pour décider.

```mermaid
flowchart LR
A[Contraintes fixes et conformité] --> B[Portes de gouvernance]
B --> C[Architecture et dépendances]
C --> D[Backlog produit]
D --> E[Sprints et incréments]
E --> F[Tests intégrés continus]
F --> G[Validation formelle]
G --> H[Déploiement contrôlé]
H --> I[Retour et amélioration]
```

### 1. Choisir une approche par risque

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », choisir une approche par risque constitue une pratique qui doit répondre à une intention précise. Le choix considère stabilité du besoin, coût d’erreur, incertitude technique, dépendances et besoin d’apprentissage. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Décrire composants, contraintes et résultat"] --> B["Évaluer incertitude et coût du changement"]
    B --> C["Identifier obligations et dépendances"]
    C --> D{"Le périmètre est-il stable et vérifiable ?"}
    D -->|"Majoritairement oui"| E["Planification prédictive possible"]
    D -->|"Partiellement ou non"| F["Livraisons adaptatives pour les éléments incertains"]
    E --> G["Définir interfaces entre les approches"]
    F --> G
    G --> H["Tester l'adéquation et réviser au fil du projet"]
```

Le choix du cycle de vie doit se fonder sur le contexte : stabilité des exigences, conséquences d’une erreur, besoins de feedback, dépendances externes, disponibilité des experts et contraintes réglementaires. Une pièce matérielle à long délai peut nécessiter des engagements précoces, alors qu’une interface utilisateur incertaine bénéficie d’incréments testés avec les utilisateurs. Le niveau d’hybridation doit résoudre une vraie contrainte, pas satisfaire une préférence méthodologique.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Le matériel suit un délai d’achat prédictif, mais le parcours utilisateur est conçu et validé par incréments. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 2. Waterfall et prédictif

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », waterfall et prédictif constitue une pratique qui doit répondre à une intention précise. Une approche prédictive planifie des phases et validations lorsque les exigences et dépendances peuvent être spécifiées tôt. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Besoin et exigences"] --> B["Architecture et conception approuvées"]
    B --> C["Planification des lots et approvisionnements"]
    C --> D["Réalisation contrôlée"]
    D --> E["Vérifications et tests"]
    E --> F["Validation et autorisation"]
    F --> G["Déploiement et transfert"]
    G --> H["Suivi des résultats"]
```

Une approche prédictive est utile lorsque les étapes sont fortement interdépendantes, que le coût des changements tardifs est élevé ou que des autorisations formelles sont nécessaires. Les exigences, les livrables, les dépendances et les critères de passage sont établis avec un niveau de détail proportionné au risque. Cela n’interdit ni les prototypes ni les retours utilisateurs : une conception prédictive peut apprendre avant d’engager des dépenses irréversibles.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Une fenêtre réglementaire de mise en production exige des preuves et une préparation coordonnée avant la date autorisée. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 3. Agile et adaptatif

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », agile et adaptatif constitue une pratique qui doit répondre à une intention précise. Une approche adaptative découpe le produit en incréments, recueille du feedback et réordonne le travail selon la valeur. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Objectif produit"] --> B["Backlog ordonné"]
    B --> C["Sélection d'un incrément"]
    C --> D["Conception, réalisation et tests continus"]
    D --> E["Incrément conforme aux critères qualité"]
    E --> F["Feedback des utilisateurs"]
    F --> G["Réviser les priorités et les hypothèses"]
    G --> B
```

Une approche adaptative convient lorsque la connaissance du besoin progresse grâce aux résultats et aux retours d’usage. Elle garde un cap produit mais permet de préciser le contenu à partir d’éléments observés. Les incréments doivent rester intégrables et vérifiés ; les contraintes de sécurité, d’architecture et d’exploitation sont intégrées au travail plutôt que repoussées à une phase finale séparée.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Le formulaire utilisateur est testé sur un prototype avant que l’équipe n’engage les optimisations de détail. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 4. Architecture et interfaces

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », architecture et interfaces constitue une pratique qui doit répondre à une intention précise. Les contrats d’interface doivent être définis assez tôt pour intégrer des équipes qui travaillent à des cadences différentes. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart LR
    A["Plateforme et fondations"] --> B["Contrats d'API stabilisés"]
    B --> C["Équipe produit A"]
    B --> D["Équipe produit B"]
    C --> E["Tests de contrat et intégration"]
    D --> E
    E --> F["Version intégrée vérifiable"]
    G["Principes d'architecture et sécurité"] --> B
    G --> E
```

L’hybridation augmente le besoin de coordination autour des interfaces. Les composants peuvent évoluer à des cadences différentes, mais leurs contrats, versions, exigences de sécurité et conditions d’intégration doivent être compris par tous. Une architecture suffisamment claire limite les changements coûteux, tandis que les tests de contrat, environnements partagés et décisions d’architecture révisables permettent à l’innovation locale de rester compatible avec l’ensemble.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Les équipes API et interface utilisent des contrats versionnés et des mocks pour limiter l’attente réciproque. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 5. Portes de gouvernance

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », portes de gouvernance constitue une pratique qui doit répondre à une intention précise. Les portes formelles vérifient des critères de décision sans imposer que tout le travail soit figé dès le départ. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Préparer un jalon de gouvernance"] --> B["Rassembler livrables et preuves"]
    B --> C["Vérifier qualité, sécurité, risques et coûts"]
    C --> D{"Critères de passage satisfaits ?"}
    D -->|"Oui"| E["Autoriser la prochaine étape"]
    D -->|"Non mais récupérable"| F["Plan d'action et nouvelle revue"]
    D -->|"Non et risque inacceptable"| G["Suspendre, redimensionner ou arrêter"]
    F --> B
    E --> H["Continuer avec les limites approuvées"]
```

Une porte de gouvernance est une décision fondée sur des critères et des preuves, pas seulement une réunion de statut. Les critères peuvent exiger une conception approuvée, une preuve de sécurité, des tests réussis, un plan de retour arrière ou une capacité de support. Les équipes agiles peuvent continuer à livrer entre les portes, à condition que le produit ne franchisse pas une limite de risque ou d’autorisation avant que les conditions requises soient satisfaites.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Le comité autorise la production lorsque contrôles, preuves et solution de repli sont prêts. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 6. Planification multi-horizon

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », planification multi-horizon constitue une pratique qui doit répondre à une intention précise. Un plan intégré combine jalons de haut niveau, dépendances longues et plans détaillés à court terme révisables. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Vision, résultats et jalons de haut niveau"] --> B["Plan de version et dépendances majeures"]
    B --> C["Plan détaillé de la prochaine période"]
    C --> D["Itération ou lot en cours"]
    D --> E["Données réelles et feedback"]
    E --> F["Réviser les hypothèses proches"]
    F --> C
    E --> G["Escalader les changements de portée ou de jalon"]
    G --> A
```

La planification multi-horizon stabilise les décisions qui nécessitent de la visibilité tout en gardant souple le détail éloigné. Le budget, les contrats et les jalons réglementaires peuvent être établis au niveau programme ; le contenu du prochain incrément est détaillé avec l’équipe ; les travaux lointains restent des prévisions avec une marge d’incertitude. Cette distinction évite à la fois le plan figé et l’absence de prévisibilité.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Le trimestre garde les dates d’achat et de certification, tandis que le sprint précise les stories réellement prêtes. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 7. Qualité dans les deux modes

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », qualité dans les deux modes constitue une pratique qui doit répondre à une intention précise. La qualité doit être intégrée à l’incrément et démontrée aux portes formelles sans duplication inutile des mêmes contrôles. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Critères de qualité communs"] --> B["Contrôles continus pendant la construction"]
    B --> C["Tests automatisés et revues"]
    C --> D["Intégration fréquente des composants"]
    D --> E["Vérifications formelles au jalon"]
    E --> F{"Preuves suffisantes ?"}
    F -->|"Oui"| G["Passage autorisé"]
    F -->|"Non"| H["Corriger et compléter la preuve"]
    H --> C
```

Un modèle hybride ne doit pas créer deux définitions de la qualité, l’une pour les équipes agiles et l’autre pour la gouvernance. La Definition of Done, les critères d’acceptation, les exigences non fonctionnelles et les conditions de passage doivent se renforcer mutuellement. Les tests continus réduisent la découverte tardive des défauts ; les revues formelles confirment que les éléments critiques de risque, de conformité et d’exploitation sont bien couverts.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** La CI valide les tests à chaque changement et la recette réglementaire conserve une preuve formellement approuvée. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 8. Gestion de configuration

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », gestion de configuration constitue une pratique qui doit répondre à une intention précise. Les versions de livrables, exigences, contrats, environnements et approbations doivent rester cohérentes. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Élément de configuration identifié"] --> B["Version, propriétaire et dépendances"]
    B --> C["Changement proposé"]
    C --> D["Analyser impact et compatibilité"]
    D --> E["Revue et autorisation adaptée au risque"]
    E --> F["Construire, tester et versionner"]
    F --> G["Publier les notes et preuves"]
    G --> H["Déployer de manière contrôlée"]
    H --> I["Traçabilité et retour arrière"]
```

Les livrables prédictifs, les composants logiciels, les exigences, les environnements et les configurations opérationnelles doivent partager une stratégie de version claire. La gestion de configuration protège l’intégrité et permet de savoir quelle version a été testée, approuvée et déployée. Les équipes conservent la possibilité d’itérer, mais tout changement d’un composant partagé doit prendre en compte les interfaces, la compatibilité et les preuves de non-régression.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** La release identifie le code, les schémas de données, les contrôles exécutés et la version de la procédure de reprise. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 9. Budget et engagement

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », budget et engagement constitue une pratique qui doit répondre à une intention précise. Les contrats et achats lourds sont budgétés en amont, tandis que la construction itérative suit la valeur et les coûts réels. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Financement et contraintes globales"] --> B["Prévoir lots, capacité et achats"]
    B --> C["Engagements irréversibles et coûts de sortie"]
    B --> D["Budget d'incréments et hypothèses de valeur"]
    C --> E["Prévision intégrée du coût total"]
    D --> E
    E --> F["Revue régulière des coûts et bénéfices"]
    F --> G{"L'investissement reste-t-il justifié ?"}
    G -->|"Oui"| H["Continuer selon l'autorisation"]
    G -->|"Non"| I["Revoir périmètre, cadence ou financement"]
```

Le budget hybride doit intégrer les dépenses qui doivent être engagées tôt — par exemple un matériel à long délai ou un contrat fournisseur — et celles qui peuvent être libérées progressivement selon les apprentissages. Il faut séparer un engagement contractuel, une prévision de consommation et une réserve, puis relier les changements de budget à des décisions de gouvernance. La flexibilité n’autorise pas à masquer les coûts ou à ajouter continuellement du périmètre sans arbitrage.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Une enveloppe est libérée par phase, puis le Product Owner réordonne le backlog dans le cadre autorisé. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 10. Gestion des changements

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », gestion des changements constitue une pratique qui doit répondre à une intention précise. La gouvernance distingue les demandes produit des changements qui affectent un contrat ou une certification. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Nouveau besoin ou contrainte"] --> B["Qualifier le changement et son urgence"]
    B --> C["Analyser valeur, impact, risque et dépendances"]
    C --> D{"Dans les tolérances et délégations ?"}
    D -->|"Oui"| E["Ajuster le backlog ou le plan local"]
    D -->|"Non"| F["Soumettre des options à l'autorité compétente"]
    F --> G["Décision et références mises à jour"]
    E --> H["Communiquer et vérifier l'effet"]
    G --> H
```

Le modèle hybride distingue les adaptations locales réversibles des changements qui modifient un engagement majeur : budget global, date contractuelle, périmètre réglementaire, architecture critique ou seuil de risque. Les petites évolutions peuvent être ordonnées dans le backlog ou le plan détaillé selon les règles convenues ; les changements qui dépassent les tolérances suivent une procédure d’arbitrage. Dans tous les cas, les impacts croisés doivent être visibles.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Une nouvelle fonction est ordonnée au backlog, mais un changement du périmètre certifié requiert une analyse indépendante. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 11. Coordination des équipes

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », coordination des équipes constitue une pratique qui doit répondre à une intention précise. Les cadences doivent être synchronisées sur les dépendances réelles, pas par des réunions permanentes sans décision. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Cadence des équipes agiles"] --> C["Synchronisation des dépendances"]
    B["Jalons de gouvernance et fournisseurs"] --> C
    C --> D["Revue des interfaces, risques et décisions ouvertes"]
    D --> E["Résoudre les conflits de capacité et d'ordre"]
    E --> F["Mettre à jour le plan intégré"]
    F --> A
    F --> B
```

La coordination doit réunir les cadences nécessaires sans transformer toutes les réunions en cérémonies supplémentaires. Les équipes ont leurs routines de planification et d’inspection ; les responsables de dépendances se synchronisent sur les interfaces, environnements et dates ; la gouvernance reçoit les informations dont elle a besoin aux jalons. Un registre partagé des décisions, des dépendances, des propriétaires et des échéances évite de faire reposer la coordination sur la mémoire individuelle.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Une revue d’intégration fréquente rassemble les responsables concernés par les interfaces et les risques. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 12. Critères de préparation

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », critères de préparation constitue une pratique qui doit répondre à une intention précise. Une équipe n’entre pas dans une phase ou release sans prérequis connus et critères de sortie observables. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Demande d'entrée en réalisation"] --> B["Exigences et but compris"]
    B --> C["Dépendances et accès disponibles"]
    C --> D["Critères de test et sécurité définis"]
    D --> E["Capacité et données de test prêtes"]
    E --> F{"Prêt à commencer ?"}
    F -->|"Oui"| G["Planifier et réaliser"]
    F -->|"Non"| H["Rendre visibles les écarts et le propriétaire"]
    H --> E
```

Les critères de préparation, souvent appelés Definition of Ready par certaines équipes, peuvent aider à révéler les dépendances et informations manquantes, mais ils ne sont pas une exigence universelle de Scrum. Utilise-les comme une aide à la conversation plutôt que comme une porte bureaucratique. Pour des travaux à fort risque, les prérequis doivent inclure les autorisations, accès, données, environnement, critères de sécurité et personne capable de prendre les décisions nécessaires.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** La migration générale attend une répétition réussie, la restauration testée et la décision d’exploitation. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

### 13. Apprendre et ajuster

**Comprendre le concept.** Dans « Méthodologies hybrides Agile/Waterfall », apprendre et ajuster constitue une pratique qui doit répondre à une intention précise. L’approche hybride doit être inspectée et adaptée si l’expérience révèle une inadéquation. Le responsable doit définir le résultat attendu, l’autorité concernée et les informations qui manquent encore. Une méthode ne doit pas être appliquée uniquement parce qu’elle figure dans un guide ou qu’elle est proposée par un outil. Sa valeur dépend du contexte, des personnes qui l’utilisent et de la qualité des décisions qu’elle permet de prendre.

```mermaid
flowchart TD
    A["Observer résultats et écarts"] --> B["Identifier la source : incertitude, dépendance ou processus"]
    B --> C["Formuler une amélioration limitée"]
    C --> D["Tester avec un incrément ou un lot"]
    D --> E["Mesurer qualité, délai, risque et valeur"]
    E --> F{"L'approche est-elle plus efficace ?"}
    F -->|"Oui"| G["Conserver et documenter"]
    F -->|"Non"| H["Adapter le modèle ou rétablir un contrôle utile"]
    G --> A
    H --> A
```

Une approche hybride doit elle-même être améliorée. Examine où les décisions sont prises trop tard, où les validations créent des files d’attente, où les incréments sont difficiles à intégrer et où l’équipe découvre les contraintes après l’engagement. Les ajustements doivent être testables et mesurer plusieurs dimensions : délai, coût de reprise, qualité, exposition au risque et valeur réellement livrée. Il ne faut pas confondre la suppression d’une étape avec l’amélioration du résultat.

**Articuler avec les autres dimensions.** La décision peut affecter le périmètre, la capacité, les coûts, le calendrier, la sécurité et l’exploitation. Il est nécessaire de repérer les dépendances en amont, les conséquences pour les bénéficiaires et les coûts de réversibilité. Une optimisation locale peut transférer le coût vers une autre équipe ou reporter un risque après la mise en service. Une analyse complète rend explicite le compromis, indique ce qui est protégé et précise quelles limites ne peuvent pas être négociées.

**Illustration opérationnelle.** Après deux cycles de validation lente, l’équipe simplifie le dossier de revue sans supprimer les contrôles obligatoires. Pour traiter ce type de situation, consigner les faits, distinguer les hypothèses, fixer une responsabilité et définir une preuve vérifiable. Lorsque plusieurs solutions sont possibles, les comparer avec des critères communs. Si les données sont incomplètes, organiser une courte investigation avec une échéance au lieu de présenter une estimation fragile comme un engagement ferme. La décision doit pouvoir être comprise par une personne qui n’a pas assisté à la discussion d’origine.

**Mise en œuvre.** Recueillir les données auprès des personnes proches du travail, examiner les contraintes, formuler des options, préciser leurs impacts et décider au niveau approprié. Après la décision, consigner le motif, informer les acteurs concernés et suivre l’effet réel. Lorsque le seuil de délégation est dépassé, préparer une escalade concise qui présente le problème, les options, les risques, une recommandation et la date à laquelle la décision devient urgente.

**Mesure et preuve.** Il faut choisir un indicateur correspondant à la finalité de la pratique. Une donnée d’activité ne démontre pas nécessairement un résultat. Définir la source, la fréquence, le responsable, la valeur de référence et les limites de l’indicateur. Compléter si nécessaire les chiffres par une observation qualitative, une revue ou un test. Les mesures doivent être assez fiables pour soutenir une décision, mais pas si coûteuses qu’elles consomment une part disproportionnée du travail.

**Erreurs fréquentes et correction.** Les erreurs habituelles incluent une information non actualisée, des définitions variables, une responsabilité implicite, un contrôle fait trop tard ou une exception devenue la règle. Le correctif n’est pas d’ajouter des tableaux sans fin : il faut retrouver la cause, simplifier le flux, attribuer la décision et mesurer l’amélioration. Si une pratique ne produit plus de valeur, la revoir avec les personnes concernées, tout en conservant les contrôles obligatoires et les traces nécessaires à l’audit.

**Approfondissement.** Pour un projet à forte criticité, la pratique peut exiger une validation indépendante, une séparation des tâches, une piste d’audit et un test sur un environnement représentatif. Pour un travail limité et réversible, une revue de pair peut suffire. La proportionnalité ne signifie pas l’absence de rigueur : elle cherche le meilleur rapport entre contrôle et utilité. Le test décisif est de savoir si l’équipe peut expliquer ce qu’elle fait, pourquoi elle le fait, quelle preuve confirme le résultat et comment elle réagira si l’hypothèse devient fausse.

## Étude de cas : Moderniser une plateforme bancaire

Le projet inclut acquisition de matériel, revue d’architecture, exigences de contrôle, développement d’API, migration de données, tests de sécurité et amélioration itérative d’interfaces. Les étapes de gouvernance restent obligatoires tandis que certains besoins peuvent évoluer.

```mermaid
flowchart TD
    A["Contraintes bancaires, sécurité et continuité"] --> B["Plan directeur, architecture et jalons d'approbation"]
    B --> C["Approvisionnements et préparation des environnements"]
    C --> D["Équipes API livrent des incréments"]
    D --> E["Tests d'intégration et de sécurité continus"]
    E --> F["Porte formelle avant migration de données"]
    F --> G["Migration pilote et validation"]
    G --> H{"Critères d'exploitation atteints ?"}
    H -->|"Oui"| I["Déploiement par lots"]
    H -->|"Non"| J["Corriger et réévaluer"]
    J --> E
```

La plateforme bancaire combine des dépendances d’infrastructure, des achats, des obligations de sécurité et des besoins produit qui évoluent avec les retours utilisateurs. Une approche hybride peut fixer tôt les contrôles, les interfaces critiques et les fenêtres de changement, tout en laissant aux équipes la capacité de livrer et ajuster les API en incréments. Les portes de passage protègent les risques à fort impact, tandis que les équipes ne reportent pas tous les tests à la fin.

### Cadrage et analyse

Les acteurs commencent par décrire le problème avec des faits vérifiables, puis identifient les bénéficiaires, les exigences et les contraintes. Ils séparent les obligations impératives des préférences, écrivent les hypothèses et demandent confirmation lorsque celles-ci conditionnent fortement le coût ou la date. Le responsable désigne un propriétaire pour chaque décision majeure, fixe un mécanisme d’escalade et conserve une trace des validations.

```mermaid
flowchart TD
    A["Cartographier obligations et objectifs métier"] --> B["Séparer contraintes fixes et éléments incertains"]
    B --> C["Identifier dépendances, délais d'approvisionnement et compétences"]
    C --> D["Choisir approche par composant"]
    D --> E["Définir jalons, critères d'acceptation et cadence"]
    E --> F["Attribuer décisions, propriétaires et tolérances"]
```

Le cadrage identifie ce qui doit être stable et contrôlé : conformité, sécurité, interfaces, fenêtre de bascule, exigences de disponibilité et contrats. Il identifie aussi ce qui doit pouvoir être découvert : ergonomie, détail des fonctionnalités et priorités utilisateur. La structure de gouvernance précise comment l’information issue des incréments peut conduire à des décisions sur le périmètre ou les dates sans court-circuiter les responsabilités.

### Comparaison des options

L’équipe compare au moins deux options réalistes, dont une option limitée ou progressive. Chaque option est évaluée selon valeur, coût complet, délai, risques, réversibilité, dépendances et conséquences en exploitation. Les avantages non mesurés sont explicitement identifiés comme hypothèses. Une décision est recommandée lorsque le raisonnement est clair, les compromis sont compris et la personne habilitée dispose des éléments nécessaires.

```mermaid
flowchart TD
    A["Modèle entièrement prédictif"] --> D["Comparer prévisibilité, feedback, coût de changement et risques"]
    B["Modèle fortement adaptatif"] --> D
    C["Modèle hybride par composant et par jalon"] --> D
    D --> E["Vérifier les obligations et la capacité d'intégration"]
    E --> F["Identifier compromis et critères de révision"]
    F --> G["Décision documentée"]
```

Une approche entièrement prédictive apporte de la visibilité sur les engagements, mais peut figer trop tôt des détails incertains. Une approche entièrement adaptative accélère le feedback, mais peut s’adapter difficilement à certains achats, contrats ou jalons réglementaires. L’approche hybride cherche à combiner ces avantages, au prix d’une coordination plus exigeante ; ses interfaces, ses responsabilités et ses règles de passage doivent être explicites.

### Mise en œuvre et suivi

Le plan est découpé en livrables vérifiables. Les travaux critiques sont associés à des critères de sortie, des responsables et des preuves. Les prévisions sont actualisées en fonction du travail restant, pas uniquement par décalage des dates précédentes. Les changements sont analysés pour leurs impacts croisés. Lorsqu’un indicateur devient rouge, l’équipe expose la cause et propose une action plutôt que de modifier sa définition.

```mermaid
flowchart TD
    A["Plan intégré et backlog"] --> B["Réaliser des incréments"]
    B --> C["Intégrer tests et preuves continus"]
    C --> D["Suivre coûts, dépendances et jalons"]
    D --> E{"Une porte de décision est-elle due ?"}
    E -->|"Non"| F["Poursuivre l'apprentissage et l'intégration"]
    E -->|"Oui"| G["Examiner critères et risques résiduels"]
    G --> H{"Passage autorisé ?"}
    H -->|"Oui"| I["Continuer vers l'étape suivante"]
    H -->|"Non"| J["Correction, replanification ou arrêt"]
    F --> B
    I --> B
    J --> C
```

Le pilotage utilise un plan intégré qui relie les livraisons incrémentales, les jalons, les engagements contractuels et les dépendances. Il faut vérifier régulièrement si le produit intégré correspond toujours aux hypothèses d’architecture et si les critères de gouvernance peuvent être démontrés. Les retards et défauts sont analysés dans leur contexte ; les équipes évitent de modifier artificiellement le statut d’un livrable pour satisfaire le calendrier.

### Acceptation et apprentissage

Avant la clôture, les livrables sont comparés aux critères convenus, les défauts et risques résiduels sont documentés, les responsabilités sont transférées et le support est préparé. Les mesures de bénéfices ont un propriétaire et une échéance de suivi. La rétrospective décrit les faits, les causes des écarts, les adaptations utiles et les pratiques à conserver.

```mermaid
flowchart TD
    A["Vérifier produit intégré et preuves"] --> B["Confirmer critères fonctionnels, non fonctionnels et conformité"]
    B --> C["Obtenir l'autorisation de livraison"]
    C --> D["Transférer opérations, support et responsabilités"]
    D --> E["Mesurer stabilité et adoption après déploiement"]
    E --> F["Comparer modèle prévu et résultats réels"]
    F --> G["Ajuster les pratiques hybrides pour la suite"]
```

L’acceptation porte sur un produit intégré et des preuves vérifiables, pas uniquement sur la fin des sprints ou la tenue d’un jalon. Le transfert inclut support, supervision, procédures, accès, risques résiduels et plans de reprise. Après la mise en service, l’organisation compare les résultats au modèle prévu : cela permet d’améliorer le niveau de contrôle, la cadence d’intégration et le dosage entre planification prédictive et adaptation.

## Atelier pratique

**Exercice 1.** À partir du cas, écris une note de pilotage d’une page : résultat attendu, contraintes, options, risques, responsables, indicateurs et décisions nécessaires.

**Correction.** Une bonne réponse relie chaque recommandation à un fait ou une hypothèse clairement identifiée. Elle présente les conséquences de plusieurs options, distingue les décisions réversibles des engagements difficiles à défaire et identifie qui possède l’autorité requise. Les mesures de résultat doivent être observables, avec une source et une date de revue.

**Exercice 2.** Un dirigeant demande une action immédiate, mais les données disponibles ne suffisent pas à comparer ses conséquences. Prépare une réponse transparente et un plan de réduction d’incertitude.

**Correction.** Il faut dire ce qui est connu, ce qui ne l’est pas et pourquoi cette information compte. Proposer une mesure réversible, un pilote ou une courte investigation peut permettre d’agir sans prétendre que les inconnues ont disparu. Le plan doit définir l’échéance de retour et les critères qui permettront de poursuivre ou de changer d’option.

**Exercice 3.** Un indicateur est favorable mais un groupe d’utilisateurs signale une difficulté majeure. Explique comment traiter l’écart entre mesure et observation.

**Correction.** Il faut vérifier si l’indicateur mesure vraiment le résultat recherché, examiner le groupe concerné et rechercher une explication à l’écart. Une moyenne peut masquer des impacts inégaux. Compléter la mesure par des tests ou des entretiens ciblés permet de décider si le processus doit être adapté.

## Pièges à éviter

- Confondre activité, livraison et bénéfice.
- Présenter une estimation comme une certitude sans expliquer les hypothèses.
- Masquer un écart en modifiant la référence.
- Choisir une méthode parce qu’elle est populaire plutôt que adaptée.
- Surcharger l’équipe d’outils qui ne soutiennent aucune décision utile.
- Faire dépendre un résultat d’une personne ou d’un fournisseur sans plan de secours.
- Reporter les contrôles obligatoires à la toute fin.
- Laisser les responsabilités d’acceptation implicites.
- Confondre indicateurs d’activité et mesures de résultat.
- Clore un projet sans transfert, support ni mesure des bénéfices.

## Checklist de révision

- [ ] Le besoin et les résultats attendus sont explicites.
- [ ] Les inclusions et exclusions sont visibles.
- [ ] Les hypothèses, dépendances et risques sont suivis.
- [ ] Les responsables et les décideurs sont identifiés.
- [ ] Les choix et arbitrages sont tracés.
- [ ] Les indicateurs répondent à des questions de décision.
- [ ] Les changements sont analysés et autorisés.
- [ ] La qualité, la sécurité et l’adoption sont intégrées.
- [ ] Le transfert aux opérations est préparé.
- [ ] Les apprentissages sont capitalisés.

## À retenir

Un dispositif de gestion de projet est un système partagé pour comprendre le travail, prendre des décisions, observer les résultats et adapter le plan. Il doit être assez rigoureux pour protéger la valeur, la qualité et la confiance, mais assez léger pour rester utilisé. Les pratiques les plus utiles rendent les hypothèses visibles, les responsabilités explicites et les décisions vérifiables.

## Glossaire

- **Bénéfice :** amélioration mesurable obtenue grâce à un résultat.
- **Dépendance :** condition qui relie plusieurs activités ou équipes.
- **Gouvernance :** répartition des responsabilités, décisions et contrôles.
- **Indicateur :** mesure qui aide à comprendre un résultat ou à décider.
- **Partie prenante :** personne ou organisation influençant le projet ou affectée par lui.
- **Portefeuille :** ensemble d’initiatives arbitrées en fonction des objectifs et capacités.
- **Risque :** événement incertain susceptible d’affecter les objectifs.
- **Scénario :** option décrivant des hypothèses et conséquences possibles.
- **Valeur :** utilité obtenue par le bénéficiaire et l’organisation.
- **Réversibilité :** capacité à revenir sur une décision avec un coût contrôlé.

## Références pour approfondir

- ISO 21502 : https://committee.iso.org/sites/tc258/home/projects/published/iso-21502.html
- PMI : https://www.pmi.org/
- Guide Scrum officiel : https://scrumguides.org/scrum-guide
- PRINCE2 7 : https://www.peoplecert.org/browse-certifications/project-programme-and-portfolio-management/PRINCE2-2/prince2-7-foundation-3579
