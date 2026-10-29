# Automatisation du support : concevoir des chatbots et du self-service fiables

> **Mise en contexte**
>
> Automatiser le support ne consiste pas à remplacer chaque conversation humaine par un bot. Il s'agit de rendre les tâches simples plus accessibles, de guider les utilisateurs vers des solutions fiables et de libérer les spécialistes pour les situations complexes. Un système mal conçu peut au contraire bloquer les utilisateurs, diffuser une procédure périmée ou automatiser une décision risquée. Le niveau expert consiste à choisir les bons cas d'usage, définir des garde-fous et mesurer le résultat global, pas seulement le nombre de conversations automatisées.

## 1. Partir des besoins et sélectionner les bons cas

Les candidats à l'automatisation sont des tâches fréquentes, prévisibles, bien documentées et présentant un risque maîtrisable : retrouver une procédure approuvée, suivre l'état d'une demande, guider l'installation d'un logiciel autorisé, collecter les informations nécessaires au diagnostic ou effectuer une vérification non destructive. Les cas rares, ambigus, sensibles ou ayant des conséquences importantes nécessitent une voie humaine claire.

Analysez le volume, la répétition, la stabilité des procédures, le temps nécessaire, le taux d'échec, les exceptions et le risque. Un problème récurrent dû à une mauvaise conception ne doit pas simplement être masqué par un chatbot : corriger la source peut être plus efficace. Le self-service doit compléter le catalogue de services, les articles de connaissance et les processus existants, pas créer un canal parallèle impossible à gouverner.

Établissez une base de référence avant le projet : volume par catégorie, temps de résolution, réouvertures, effort utilisateur, satisfaction et part des demandes qui nécessitent une intervention spécialisée. Sans référence, il est impossible de distinguer une vraie amélioration d'un simple déplacement de charge.

## 2. Distinguer FAQ, chatbot guidé et assistant génératif

Une FAQ présente des articles sélectionnés ; l'utilisateur doit chercher et interpréter. Un parcours guidé pose des questions et suit une logique définie ; il est prévisible et peut contrôler les données requises. Un assistant génératif interprète le langage naturel et formule des réponses à partir d'un modèle et de sources. Cette souplesse introduit des risques supplémentaires : réponse inventée, mélange de contexte, interprétation erronée ou exposition de données.

Le choix doit dépendre de la variabilité du problème, des exigences de traçabilité et du risque. Pour une demande standard à étapes stables, un formulaire guidé est parfois préférable à l'IA. Pour expliquer un article ou orienter l'utilisateur vers le bon document, un assistant avec récupération de sources peut être utile, à condition d'afficher les références et de reconnaître quand il ne sait pas répondre.

~~~mermaid
flowchart TD
    A[Besoin utilisateur] --> B{Tâche stable et faible risque ?}
    B -->|Oui, réponse connue| C[FAQ ou article validé]
    B -->|Oui, plusieurs étapes| D[Parcours guidé]
    B -->|Question variable| E[Assistant avec sources contrôlées]
    C --> F[Évaluer le résultat]
    D --> F
    E --> G{Confiance et règles suffisantes ?}
    G -->|Oui| F
    G -->|Non| H[Transfert vers un humain]
    H --> F
~~~

N'attribuez pas à un chatbot un pouvoir d'exécuter des opérations privilégiées simplement parce qu'il sait expliquer une procédure. La capacité à parler d'une action et le droit d'exécuter cette action sont deux choses distinctes.

## 3. Architecturer un self-service fiable

Un portail de self-service comporte généralement un catalogue de demandes, une base de connaissances, un moteur de recherche, des parcours guidés, une authentification adaptée, une intégration au système de tickets et un suivi de qualité. Chaque composant doit avoir un propriétaire. Les articles ont une source validée, une version et une date de révision ; les parcours ont un responsable métier et les règles d'accès sont maintenues avec les équipes concernées.

Les liens entre l'assistant et la connaissance doivent être traçables. Si une réponse vient d'un article, affichez le titre ou la référence et fournissez l'accès à la source. Les documents doivent être filtrés selon les droits de l'utilisateur : une recherche sémantique ne doit pas contourner les contrôles d'accès du dépôt documentaire.

Les intégrations doivent utiliser des permissions limitées, des secrets gérés de manière sûre, des journaux appropriés et une stratégie de reprise. Le service ne devrait pas échouer silencieusement si l'API du système de tickets est indisponible. Un message explicite et une voie de création manuelle sont préférables à une demande perdue.

~~~mermaid
flowchart LR
    U[Utilisateur] --> I[Portail ou chatbot]
    I --> K[Recherche dans la connaissance autorisée]
    I --> W[Parcours guidé]
    K --> A[Réponse avec source]
    W --> T[Système de tickets]
    I --> H[Transfert humain]
    T --> M[Suivi de statut]
    H --> M
    A --> E[Retour utilisateur]
    M --> E
~~~

## 4. Concevoir le parcours conversationnel

Chaque parcours doit expliquer ce qu'il peut faire, quelles informations il demande et à quel moment il transfère la demande à une personne. Utilisez des questions simples, demandez une seule information à la fois quand c'est utile et acceptez les formulations différentes. Le bot doit reconnaître les erreurs, permettre de revenir en arrière et éviter de redemander un renseignement déjà fourni.

Collectez le minimum de données nécessaires. Une demande de réinitialisation n'a pas besoin du contenu complet du poste ou d'une capture d'écran contenant un document confidentiel. Les journaux de conversation sont eux aussi des données : définissez finalité, accès, conservation et suppression selon la politique de l'organisation.

Fournissez une sortie humaine lorsque l'utilisateur le demande, lorsque les sources sont insuffisantes, lorsque le même essai échoue, lorsque le besoin dépasse le périmètre ou lorsqu'un risque particulier est détecté. Ne créez pas une boucle infinie qui redonne la même instruction. Le transfert doit transmettre le résumé, les étapes déjà tentées, les résultats et les preuves autorisées afin que l'utilisateur ne doive pas recommencer depuis le début.

## 5. Gouverner les réponses d'un assistant génératif

Un assistant génératif devrait utiliser des sources approuvées et limitées au domaine de service. Le mécanisme de récupération de documents doit respecter les permissions et les versions. Les instructions définissent les actions autorisées, les limites, le format de réponse, les règles d'escalade et l'interdiction de révéler les secrets ou les prompts internes. Les protections doivent être testées ; une consigne écrite ne remplace pas les contrôles techniques.

Les réponses peuvent être obsolètes même si elles sont formulées avec assurance. Affichez les sources, leurs dates lorsque c'est pertinent et un moyen de signaler une réponse incorrecte. Une réponse importante ne doit pas déclencher automatiquement une action destructrice. Faites confirmer les opérations à impact élevé et gardez une validation humaine lorsque le contexte ou le risque l'exige.

Les documents importés peuvent contenir des instructions malveillantes ou du contenu hors sujet. Traitez-les comme des données à analyser, pas comme des règles système. Séparez les instructions de l'application du contenu des documents et empêchez les actions du modèle d'accéder à des outils non autorisés. Testez des tentatives de détournement, de divulgation et de contournement des rôles.

~~~mermaid
flowchart TD
    A[Question de l'utilisateur] --> B[Contrôle d'identité et de périmètre]
    B --> C[Recherche dans les sources autorisées]
    C --> D[Réponse fondée sur les sources]
    D --> E[Contrôles de sécurité et d'incertitude]
    E --> F{Réponse acceptable ?}
    F -->|Oui| G[Répondre avec références]
    F -->|Non| H[Refuser l'action risquée ou transférer]
    G --> I[Retour et évaluation]
    H --> I
~~~

## 6. Automatiser des actions sans introduire de risque

Commencez par des actions réversibles et à faible impact : créer un ticket, renseigner une catégorie suggérée, collecter un diagnostic non sensible ou vérifier un état de service. Les actions comme modifier des droits, supprimer des données, désactiver des protections ou redémarrer un service critique nécessitent des autorisations, contrôles, confirmations et parfois une exécution par un humain habilité.

Les règles de sécurité doivent exister hors du modèle conversationnel. Le backend vérifie l'identité, les droits, les paramètres, le périmètre et l'état avant l'exécution. Les entrées utilisateur ne doivent jamais être concaténées sans validation dans une commande ou une requête. Les opérations utilisent des identifiants de suivi, un journal d'audit, des limites de débit et des clés d'idempotence lorsque le rejeu est possible.

Préparez un mode dégradé : si une intégration tombe en panne, informez l'utilisateur, conservez le contexte minimal requis et dirigez-le vers une procédure manuelle. Testez les doublons, les réponses partielles, les délais dépassés, les permissions insuffisantes et les indisponibilités. Ne transformez pas une erreur technique en confirmation trompeuse de succès.

## 7. Tester la qualité avant et après le lancement

Établissez un jeu de tests représentatif : formulations différentes, fautes de frappe, demandes ambiguës, scénarios hors périmètre, données sensibles, questions sur des sources périmées, tentative de contournement et demande de transfert humain. Faites relire les réponses par des spécialistes et des utilisateurs réels. Les tests doivent examiner exactitude, pertinence de la source, sécurité, compréhension, accessibilité et possibilité de sortie.

Une mesure de « containment » indique souvent la part de conversations terminées sans agent. Elle ne prouve pas que le problème a été résolu. Un utilisateur peut abandonner, créer un ticket ailleurs ou recevoir une réponse fausse. Associez donc cette mesure au taux de résolution confirmée, à la réouverture, à l'effort utilisateur, à la satisfaction, au taux de transfert, aux incidents de sécurité et aux coûts de maintenance.

~~~mermaid
flowchart TD
    A[Jeu de tests et cas limites] --> B[Évaluation technique et métier]
    B --> C{Seuils et garde-fous satisfaits ?}
    C -->|Non| D[Corriger, limiter ou reporter]
    C -->|Oui| E[Pilote avec groupe limité]
    E --> F[Surveillance des résultats]
    F --> G{Qualité durable et risques acceptables ?}
    G -->|Oui| H[Déploiement progressif]
    G -->|Non| D
    H --> I[Revue continue et tests de régression]
~~~

## 8. Mesurer la valeur totale

Évaluez les bénéfices et les coûts. Le temps économisé dans la file support peut être compensé par le temps que les utilisateurs passent à corriger une mauvaise réponse. Intégrez le développement, l'hébergement, les licences, les intégrations, la validation des articles, l'analyse des erreurs, le support de la solution et la maintenance des modèles. Un self-service dont les articles deviennent rapidement obsolètes peut accumuler une dette opérationnelle importante.

Les indicateurs doivent être définis avant la mise en service : taux de résolution confirmée, délai de résolution, demandes répétées, taux d'abandon, transfert humain, satisfaction, erreur de réponse, indisponibilité et coût par demande résolue. Segmentez par type de demande et public ; un résultat moyen peut masquer une mauvaise expérience pour certaines catégories.

La valeur peut aussi être qualitative : disponibilité hors horaires, accès plus rapide aux instructions, meilleure collecte de contexte et autonomie. Mesurez ces bénéfices avec des observations, des enquêtes et des métriques de service plutôt qu'en extrapolant uniquement à partir du nombre de conversations.

## 9. Atelier pratique corrigé : automatiser les demandes de logiciel

**Situation.** Le support reçoit de nombreuses demandes d'installation. Certaines concernent des logiciels autorisés, d'autres des outils nécessitant une approbation de sécurité.

**Étape 1 — Segmenter.** Classer les logiciels selon le catalogue approuvé, le niveau de risque, le type de licence, les droits requis et la population autorisée.

**Étape 2 — Concevoir le parcours.** Le bot pose la question sur le logiciel et l'usage. Pour un outil standard autorisé, il vérifie les prérequis et propose une installation guidée ou crée une demande standard. Pour un outil non catalogué, il crée un ticket d'évaluation sans prétendre approuver l'installation.

**Étape 3 — Contrôler.** Le backend vérifie les droits et l'état du poste. Aucun texte libre ne peut déclencher une commande arbitraire. Les opérations sont journalisées et peuvent être rejouées sans créer de doublons.

**Étape 4 — Transférer.** Si l'utilisateur n'est pas autorisé, si le poste ne satisfait pas les prérequis ou si le service de déploiement est indisponible, expliquer le motif et transmettre le contexte à l'équipe compétente.

**Étape 5 — Mesurer.** Comparer le délai total, les installations réussies, les échecs, les tickets répétés, les incidents et la satisfaction. Une hausse du taux d'automatisation n'est un succès que si les résultats restent corrects et sûrs.

## 10. Exercices corrigés

**Exercice A.** Un chatbot a un taux de conversations terminées sans agent de 80 %, mais les réouvertures augmentent. Peut-on conclure à une automatisation réussie ?

**Correction.** Non. Le taux de containment peut inclure des abandons ou des réponses qui ne résolvent pas le problème. Analyser les parcours, les réouvertures, les tickets créés ensuite et la satisfaction, puis corriger les intents ou limiter les réponses en échec.

**Exercice B.** Un assistant peut réinitialiser des comptes si l'utilisateur lui demande. Quelle protection est prioritaire ?

**Correction.** Ne pas laisser la décision au seul modèle. Le backend doit vérifier l'identité, l'autorisation, le périmètre et les paramètres selon la procédure approuvée. Les actions sensibles doivent avoir des confirmations, des journaux et une voie de récupération.

## 11. Défi final corrigé

**Défi.** Concevez un assistant de self-service pour trois catégories : état de ticket, diagnostic Wi-Fi et demande d'accès. Définissez l'architecture, les sources, les limites, les transferts humains, les indicateurs et le plan de lancement.

**Proposition de correction.** L'état de ticket utilise une intégration en lecture seule avec authentification et contrôle du propriétaire. Le diagnostic Wi-Fi suit un parcours guidé, collecte des résultats non sensibles et propose uniquement des actions autorisées. La demande d'accès crée un workflow avec approbation métier et contrôles de droits ; l'assistant n'accorde pas lui-même l'accès. Les réponses de connaissance citent des articles approuvés et versionnés. Chaque parcours inclut une sortie humaine et conserve un résumé utile. Le lancement commence par un pilote, un jeu de tests de sécurité, une mesure de référence et une surveillance des résolutions confirmées, réouvertures, erreurs, abandons et retours utilisateurs.

## 12. Checklist d'automatisation

- Les cas d'usage sont choisis selon la fréquence, la stabilité et le risque.
- Le chatbot, le parcours guidé et l'assistant génératif sont utilisés à bon escient.
- Les sources sont approuvées, versionnées et limitées aux droits de l'utilisateur.
- Les identités et autorisations sont contrôlées côté backend.
- Les actions sensibles ont des confirmations et une piste d'audit.
- Les erreurs, indisponibilités et transferts humains sont prévus.
- Les réponses sont testées sur des cas normaux, ambigus et malveillants.
- Le succès est mesuré par la résolution réelle et la qualité, pas seulement par le containment.
- Le coût de maintenance, la fraîcheur des connaissances et le retour arrière sont prévus.

**À retenir :** une automatisation de support réussie rend le service plus accessible et plus fiable. Elle ne masque pas les problèmes, ne contourne pas les autorisations et sait transférer à un humain lorsque les preuves ou le niveau de confiance sont insuffisants.
