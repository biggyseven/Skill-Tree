# DAO et gouvernance on-chain

## Encadré de mise en contexte

Une DAO, ou organisation autonome décentralisée, utilise des règles et des outils logiciels pour coordonner des participants autour d'un objectif commun. Le terme recouvre des systèmes très différents : trésoreries gouvernées par des jetons, collectifs qui financent des projets, protocoles qui votent des paramètres, communautés qui coordonnent des services ou organisations hybrides qui combinent contrats, signatures et décisions hors chaîne.

Une DAO n'est pas automatiquement démocratique, autonome, légale ou résistante à la capture. Une gouvernance fondée sur le poids des jetons peut concentrer le pouvoir chez les gros détenteurs. Un quorum mal conçu peut rendre les décisions impossibles. Un contrat de gouvernance peut contenir un bug ou donner à une seule clé le pouvoir de contourner le vote. Une décision votée peut aussi dépendre d'une exécution technique, d'un contrat tiers ou d'une responsabilité humaine hors chaîne.

Ce cours examine l'ensemble du système : constitution et règles, propositions, vote, quorum, délégation, exécution, timelocks, multisignatures, trésorerie, gouvernance hors chaîne, défense contre la capture, gestion des conflits et réponse à incident. L'objectif est de concevoir un processus transparent, vérifiable, compréhensible pour les membres et robuste face aux erreurs, aux attaques et aux situations imprévues.

## Objectifs d'apprentissage

À la fin de cette leçon, tu dois pouvoir distinguer une DAO d'un simple vote en ligne, identifier les composants d'une gouvernance, expliquer proposition, snapshot, vote, quorum, timelock et exécution, comparer plusieurs méthodes de vote, analyser les risques de capture, concevoir des garde-fous pour la trésorerie, définir des procédures d'urgence et écrire une politique de gouvernance testable.

## Prérequis et parcours pratique

Il est recommandé de connaître les smart contracts, les jetons, les wallets, les signatures, la gestion des permissions et les transactions. Les exercices utilisent des scénarios fictifs et des valeurs sans fonds réels. Ne déploie pas de système de gouvernance contrôlant une trésorerie réelle sans revue indépendante, tests et responsabilités juridiques définies.

Le parcours pratique consiste à écrire une règle de gouvernance, la transformer en états vérifiables, tester les cas de vote valides et invalides, puis simuler une proposition qui tente de modifier un paramètre critique. L'objectif est de vérifier non seulement qui peut voter, mais aussi qui peut préparer, exécuter, suspendre ou contourner une décision.

## 1. Qu'est-ce qu'une DAO ?

Une DAO est une organisation qui utilise des mécanismes logiciels, souvent des smart contracts, pour coordonner des décisions et des ressources avec une certaine transparence. Les règles peuvent être exécutées automatiquement lorsqu'une proposition satisfait les conditions définies, mais toutes les responsabilités ne sont pas forcément on-chain. Les membres, les développeurs, les délégués, les modérateurs et les prestataires peuvent agir hors chaîne selon une constitution ou un ensemble de conventions.

Le mot « autonome » est relatif. Un contrat peut exécuter un transfert après un vote, mais les mises à niveau, la communication, les litiges, la gestion d'une faille et l'interprétation d'une règle complexe peuvent encore dépendre de personnes ou d'entités. Il faut donc distinguer l'automatisation du processus de décision et l'absence de contrôle humain.

Le mot « décentralisée » est lui aussi une propriété à évaluer. Un système peut avoir des centaines de votants mais dépendre d'un développeur unique, d'un seul multisig ou d'une clé capable de mettre à jour le contrat. L'analyse doit examiner les droits réels, les dépendances opérationnelles et la distribution des décisions, pas seulement le nombre de wallets.

Une DAO crédible définit qui peut participer, comment les règles changent, quelles décisions sont contraignantes, quelle autorité exécute la décision et comment les membres contestent une erreur. Elle documente également les limites du système et les pouvoirs qui demeurent hors chaîne.

## 2. Gouvernance, constitution et droits de décision

La gouvernance commence par définir les décisions qui peuvent être prises : dépenses de trésorerie, mise à jour de contrat, paramètres du protocole, admission de membres, attribution de subventions, sanctions ou changement de règles. Chaque catégorie peut nécessiter un processus différent. Une proposition de financement modeste n'a pas nécessairement le même seuil qu'une modification qui permet de transférer tous les actifs.

Une constitution ou un document de gouvernance décrit les objectifs, les compétences, les règles de participation, les processus de proposition, les mécanismes d'urgence et les procédures de résolution de conflit. Si le document et le contrat se contredisent, les membres doivent savoir lequel est applicable et comment le désaccord est résolu. Les règles doivent aussi préciser qui peut modifier la constitution et à quelles conditions.

La conception devrait distinguer les droits de suggestion, de proposition, de vote, de veto, d'exécution, de pause et de mise à niveau. Une personne peut être autorisée à discuter d'une proposition sans être autorisée à l'inscrire dans le système on-chain. Un rôle d'urgence peut être utile pour bloquer un transfert malveillant, mais il doit avoir une portée et une procédure de contrôle clairement définies.

## 3. Architecture d'une gouvernance on-chain

Une gouvernance courante comprend un jeton ou un autre mécanisme d'éligibilité, un contrat de gouvernance qui gère les propositions et les votes, une trésorerie ou des contrats cibles, parfois un timelock, et des rôles administratifs ou multisignatures. Les participants utilisent des portefeuilles pour voter ou déléguer leurs droits. L'interface affiche les propositions, mais le résultat contraignant est défini par l'état des contrats et les règles officielles.

~~~mermaid
flowchart TD
    M[Membres et délégataires] --> P[Création de proposition]
    P --> V[Vote et quorum]
    V --> R{Seuils satisfaits ?}
    R -->|Non| X[Proposition rejetée ou expirée]
    R -->|Oui| T[Timelock ou délai de sécurité]
    T --> E[Exécution autorisée]
    E --> C[Trésorerie ou contrats cibles]
    E --> L[Événements et auditabilité]
~~~

Les déploiements réels peuvent combiner une gouvernance on-chain avec des discussions, forums, signatures ou accords externes. Il faut expliquer quelle étape est consultative et quelle étape exécute effectivement une décision. Une capture d'écran de vote ne constitue pas une preuve que l'opération a été exécutée.

## 4. Propositions : qualité avant mise au vote

Une proposition devrait décrire le problème, l'action exacte, les bénéficiaires, le coût, les risques, les dépendances, les tests, le délai, la méthode de retour et la personne ou l'équipe responsable. Pour une mise à niveau de contrat, le contenu devrait identifier le bytecode ou l'implémentation attendue et les changements de permissions. Une proposition qui dit seulement « améliorer le protocole » est trop vague pour permettre un vote informé.

Un système peut imposer une période de discussion, un seuil de dépôt, une réputation, un nombre de jetons ou une délégation requise avant qu'une proposition puisse passer au vote. Ces règles peuvent limiter le spam, mais elles peuvent aussi exclure des membres qui ont une contribution réelle. Le coût de création ne doit pas devenir une barrière que seuls les gros détenteurs peuvent franchir, sauf si le modèle assume explicitement cette limite.

Les propositions devraient être préparées de manière vérifiable. Si elles exécutent des appels, conserve les données exactes de transaction, les adresses cibles, les valeurs et les signatures concernées. Un simulateur peut aider à examiner le résultat, mais il dépend de l'état et du contexte de simulation. Une proposition complexe doit être testée sur une copie ou un réseau de test avant d'être exécutée sur la trésorerie réelle.

## 5. Poids de vote, jetons et délégation

La gouvernance fondée sur un jeton peut attribuer un vote à chaque jeton, permettre la délégation à un représentant ou calculer le poids selon un snapshot à une hauteur donnée. Chaque modèle a des implications. Le vote par solde courant peut être manipulé par des transferts temporaires ou des emprunts, alors qu'un snapshot fixe une référence mais doit définir précisément la hauteur et les règles de délégation.

La délégation permet aux personnes qui ne veulent pas voter sur chaque sujet de confier leur pouvoir à un représentant. Elle ne doit pas être confuse avec le transfert de propriété du jeton. Les règles doivent définir si un membre peut voter après avoir délégué, si le délégué peut sous-déléguer et comment les conflits entre plusieurs délégations sont résolus.

Le vote proportionnel au solde peut donner plus de pouvoir aux grands détenteurs. Ce résultat peut être acceptable dans certains modèles de capital, mais il ne doit pas être présenté comme une démocratie égalitaire. Les alternatives comprennent un vote par personne vérifiée, des mécanismes quadratiques ou des systèmes hybrides, chacun avec des risques d'identité, de sybil et de manipulation différents. Aucun système ne garantit seul une représentation parfaite.

## 6. Quorum, majorité et participation

Le quorum définit un niveau minimal de participation ou de poids nécessaire pour que la proposition soit traitée comme valide selon les règles. La majorité décrit le seuil de soutien parmi les votes pris en compte. Ces notions sont différentes. Une majorité de votes exprimés peut être très faible si peu de membres participent ; un quorum trop élevé peut rendre la gouvernance incapable d'agir.

Les paramètres doivent correspondre aux conséquences de la décision. Un changement de texte ou une subvention de petite taille peut avoir des exigences différentes d'une modification de trésorerie ou de sécurité. Mais plus de seuils ne signifie pas toujours plus de sécurité : une participation faible ou une opposition organisée peut bloquer les décisions nécessaires à la correction d'une faille.

Les abstentions doivent être définies dans la règle. Elles peuvent compter pour le quorum sans compter dans la majorité, ou recevoir une autre interprétation. Le contrat et l'interface doivent utiliser les mêmes règles. Un écart entre le décompte affiché et le décompte on-chain peut provoquer des décisions contestées.

Un bon design simule des distributions réalistes de participation : forte, faible, concentrée, divisée et adversariale. Les paramètres doivent être évalués sur ces scénarios, pas seulement sur un vote hypothétique où tout le monde participe.

## 7. Snapshot, délégation et risques de vote emprunté

Un snapshot associe le poids de vote à un état de référence de la distribution du pouvoir. Il réduit certains problèmes liés aux transferts temporaires pendant la période de vote, mais sa précision dépend de la mise en œuvre : hauteur, timestamp, éligibilité, délégations et règles de vote doivent être cohérents. Si l'état de référence est choisi trop tôt ou trop tard, les droits obtenus peuvent différer de ce que les membres imaginent.

Les prêts flash peuvent rendre temporairement accessibles des quantités de jetons importantes. Si une gouvernance utilise le solde au moment de l'appel sans garde-fou, un acteur peut potentiellement obtenir un poids qui ne reflète pas une participation durable. Un snapshot antérieur au vote, un historique de vote ou une période de blocage peuvent réduire certains risques, mais chaque mécanisme a son propre compromis de liquidité et d'accessibilité.

Le vote peut aussi être manipulé par la concentration de délégations, des identités sybil ou des promesses de récompense contre un vote. L'analyse doit considérer les incitations, pas seulement la fonction qui additionne les poids. Une règle cryptographiquement correcte peut produire une gouvernance capturée si la concentration de pouvoir et la participation ne correspondent pas aux objectifs de l'organisation.

## 8. Vote hors chaîne et exécution on-chain

Le vote hors chaîne, par exemple avec des signatures, peut réduire les coûts et faciliter la participation. Il repose toutefois sur une méthode de vérification des signatures, des snapshots de poids, des paramètres et parfois sur une personne ou un service qui relaye la décision vers une exécution on-chain. Les membres doivent comprendre ce qui est contraignant et quelle preuve peut être vérifiée publiquement.

Le vote on-chain rend l'état du vote directement observable dans le protocole, mais chaque action peut coûter des frais et exclure des utilisateurs pour qui le coût est trop élevé. Un modèle hybride peut utiliser un processus de signalisation hors chaîne puis un mécanisme d'exécution on-chain, à condition de préciser la transition entre les deux et les contrôles qui empêchent une substitution non autorisée.

La séparation entre vote et exécution est importante. Une proposition peut être adoptée mais encore attendre un timelock ou une action de relais. L'interface doit afficher les états : discussion, ouverte, terminée, adoptée, en délai, exécutable, exécutée, annulée ou expirée. « Adoptée » n'implique pas que tous les appels aient réussi.

## 9. Timelocks et exécution différée

Un timelock impose une attente entre l'approbation d'une action et son exécution. Il donne aux membres le temps de lire les changements, de vérifier les données de transaction et, dans certains modèles, de retirer leurs fonds ou de préparer une réaction. Le délai doit être adapté à l'impact et au besoin de réaction.

Un timelock ne rend pas une proposition correcte. Il permet d'observer et de réagir avant l'exécution. Si personne ne surveille le contrat, si les données sont difficiles à comprendre ou si les utilisateurs ne disposent pas d'une sortie, le délai peut offrir une protection limitée. Le système doit fournir des alertes et des informations lisibles sur la destination, les paramètres et les effets de l'action.

Une procédure d'urgence peut permettre d'interrompre une action ou d'appliquer une pause. Elle doit être clairement séparée de l'autorité normale d'exécution. Si un rôle peut contourner immédiatement tous les délais, l'analyse doit préciser l'étendue de cette exception. Les garde-fous peuvent inclure une multisignature, des événements d'alerte, des limites de valeur et une revue post-incident.

## 10. Trésorerie, budgets et contrôles des dépenses

Une DAO qui détient une trésorerie doit définir comment les fonds sont demandés, approuvés, envoyés, suivis et rapportés. Une proposition de dépense doit identifier le montant, le token, le destinataire, la finalité, les étapes, les conditions de livraison et les preuves de réalisation. Une décision votée ne garantit pas automatiquement que le destinataire est fiable ou que le projet atteindra son objectif.

Les budgets peuvent être découpés en tranches liées à des jalons vérifiables plutôt qu'envoyés en une transaction unique. Ce modèle exige un suivi hors chaîne et une décision sur la preuve requise pour libérer la tranche suivante. L'organisation doit également distinguer le coût planifié, le coût effectivement dépensé et la valeur des actifs fluctuants.

Les contrôles de trésorerie incluent la diversification des signataires, des plafonds de dépense, des délais pour les actions importantes, la surveillance des changements de permissions et une comptabilité compréhensible. Les portefeuilles multisignatures ne sont pas automatiquement une DAO : ils protègent l'exécution, mais la distribution du pouvoir dépend des signataires et de leur mode de nomination.

Les rapports doivent rester accessibles aux membres. Un événement de transfert est une preuve technique utile, mais un bilan de gouvernance doit relier ce transfert à la proposition adoptée, au budget, au bénéficiaire et au résultat. La transparence aide à l'audit, mais ne supprime pas les risques de mauvaise allocation ou de conflit d'intérêts.

## 11. Capture de gouvernance et attaque par proposition

Une capture se produit lorsqu'un acteur ou un groupe obtient suffisamment de pouvoir pour imposer des décisions contre les objectifs du système. Elle peut être économique, par accumulation de jetons, ou organisationnelle, par contrôle des délégations et faible participation. Les protections ne peuvent pas reposer uniquement sur l'espoir que les membres surveilleront chaque proposition.

Les défenses possibles incluent un quorum adapté, une fenêtre de discussion, un timelock, des seuils plus élevés pour les actions critiques, des garde-fous de trésorerie, des pouvoirs d'urgence limités et une surveillance des grandes variations de délégation. Les protections doivent être évaluées conjointement : un quorum très haut peut aider à bloquer une capture mais rendre impossible une réponse urgente ; un seuil de proposition élevé peut limiter le spam mais concentrer la capacité de décision.

Le mécanisme de gouvernance devrait isoler les actions qui peuvent changer ses propres règles. Si une proposition peut réduire le quorum, supprimer le timelock puis transférer la trésorerie, les conséquences de la première étape doivent être évaluées dans l'ensemble de la séquence. Les tests doivent couvrir des propositions composées et pas seulement chaque appel isolément.

La détection doit se baser sur des signaux : concentration des poids, délégations soudaines, proposition qui change des rôles, destinataire de trésorerie nouveau, ou séquence d'appels inattendue. Les signaux ne prouvent pas à eux seuls une attaque, mais doivent déclencher une revue avant l'exécution d'une action à fort impact.

## 12. Conflits, contestations et gouvernance humaine

Toutes les décisions ne peuvent pas être totalement codifiées. Il peut y avoir un désaccord sur la qualité d'un livrable, une urgence légale, un conflit d'intérêts ou une information nouvelle après le vote. Le processus doit expliquer quelles décisions sont purement on-chain, lesquelles nécessitent un jugement humain et comment les conflits sont arbitrés.

Un processus de contestation doit définir qui peut déposer une objection, les délais, les preuves requises, les personnes responsables et les effets possibles. Un mécanisme d'appel peut être nécessaire avant l'exécution d'une dépense ou après un incident. Les règles devraient protéger les participants contre les modifications arbitraires tout en permettant de traiter un résultat manifestement erroné.

La gouvernance humaine peut être documentée par une constitution, des propositions publiques, des comptes rendus et des déclarations de conflit d'intérêts. Le fait que la décision finale soit inscrite sur chaîne ne rend pas les discussions, les informations de contexte ou les conditions externes automatiquement vérifiables.

Les membres doivent comprendre la différence entre les règles programmées, les conventions sociales, les obligations juridiques et les mécanismes d'urgence. Une DAO peut être techniquement décentralisée à un niveau et dépendre fortement d'une équipe dans un autre. La transparence exige de nommer ces dépendances plutôt que de prétendre qu'aucune intervention humaine n'existe.

## 13. Identité, sybil et représentation

Un système qui veut accorder un vote par personne doit résoudre le problème de l'identité : comment déterminer qu'une personne est unique sans exposer plus de données que nécessaire ? Un portefeuille est une clé cryptographique, pas une identité civile unique. Une même personne peut contrôler plusieurs wallets, et plusieurs personnes peuvent être derrière un même service de conservation.

Les méthodes de preuve d'identité et les attestations peuvent réduire certains risques mais introduisent des dépendances envers les émetteurs, les règles de révocation et la confidentialité. Le vote quadratique vise à réduire le pouvoir des gros détenteurs, mais peut être vulnérable à la création de nombreuses identités si l'unicité n'est pas assurée. Les systèmes de réputation ou de participation ont aussi des effets de réseau et peuvent exclure les nouveaux membres.

La conception doit expliquer quel type d'égalité elle cherche : égalité par jeton, par personne vérifiée, par contribution, par délégation ou par catégorie de membre. Il faut également traiter les membres absents, les clés perdues et les comptes compromis. Aucun mécanisme ne résout simultanément tous ces problèmes sans compromis.

## 14. Mise à niveau de contrat de gouvernance

Les contrats de gouvernance peuvent contrôler leurs propres paramètres et parfois l'autorité de mise à niveau. Cela crée un risque de circularité : le processus censé contrôler les pouvoirs peut lui-même être modifié par la même voie. Les actions qui changent le quorum, les délais, les rôles ou les cibles d'exécution doivent être classées comme critiques et testées avec un environnement reproductible.

Une proposition de mise à niveau doit identifier l'implémentation exacte, les différences de stockage, les changements de comportement, les rôles et les conditions de retour. La simulation doit utiliser un état représentatif et tester les chemins de vote, la file d'exécution et les actions en attente. Une compilation réussie ne prouve ni la compatibilité de stockage ni la sécurité de la migration.

Après exécution, vérifie la version active, les rôles, les paramètres, les propositions en cours et l'état de la trésorerie. Si l'ancienne version avait des actions programmées, assure-toi qu'elles n'ont pas été rendues exécutables de façon inattendue. Le compte rendu doit être relié à la proposition qui autorisait exactement le changement.

## 15. Surveillance et tableau de bord de gouvernance

Un tableau de bord utile montre les propositions et leurs états, les votes exprimés, le quorum, la délégation, les actions en attente, le temps avant exécution, les adresses cibles et les opérations de trésorerie. Les informations importantes doivent pouvoir être vérifiées on-chain ou reliées à la source officielle. Les données d'indexation peuvent avoir du retard ; un tableau de bord ne doit pas les présenter comme absolues sans indication.

Les alertes devraient couvrir une proposition qui touche à des permissions critiques, une modification soudaine de délégation, un changement de trésorerie, une exécution imminente, un pouvoir d'urgence utilisé ou une divergence entre les données de l'indexeur et l'état du contrat. Chaque alerte doit mener à une action définie et à un propriétaire.

Le tableau de bord doit distinguer les votes consultatifs des votes contraignants, et l'approbation de l'exécution. Pour chaque proposition, montre les données exactes d'exécution, les contrats concernés et les délais. Les membres doivent pouvoir vérifier que la transaction exécutée correspond à ce qu'ils ont voté.

Les journaux ne devraient pas exposer de données personnelles inutiles ou de secrets liés aux signataires. La transparence on-chain n'exige pas de publier tous les renseignements des membres. Le produit doit trouver un équilibre entre auditabilité et minimisation des données.

## 16. TP guidé A : modéliser une gouvernance de trésorerie

Définis une DAO fictive qui gère un budget. Écris les types de propositions, qui peut les créer, le délai de discussion, les règles de quorum, la majorité, le timelock, les limites de dépense et le chemin d'urgence. Indique quelles décisions sont exécutées automatiquement et lesquelles nécessitent une approbation humaine ou une preuve de livrable.

### Correction proposée

Le modèle doit distinguer les dépenses ordinaires des changements de sécurité. Une proposition importante doit afficher ses cibles et paramètres exacts. Le résultat du vote ne doit pas être assimilé à l'exécution. Les contrôles de trésorerie doivent limiter le risque et la politique d'urgence doit prévoir une surveillance et une reprise.

## 17. TP guidé B : tester quorum et délégation

Simule une faible participation, un grand détenteur, plusieurs délégués, un membre qui change sa délégation et une proposition proche du quorum. Détermine le résultat attendu et vérifie que l'interface utilise la même formule que le contrat. Ajoute un scénario de vote répété et un scénario où le snapshot choisi diffère de l'état courant.

### Correction proposée

Le compte rendu explique la hauteur de snapshot, le calcul du poids, le traitement des abstentions et la différence entre quorum et majorité. Chaque résultat doit être reproductible à partir des données de vote. Le test vérifie également qu'une même capacité de vote n'est pas comptée deux fois selon les règles.

## 18. Étude de cas : proposition adoptée mais exécution dangereuse

Une proposition reçoit suffisamment de votes et atteint le quorum. Elle configure une nouvelle adresse d'implémentation et transfère la trésorerie vers un portefeuille qui n'avait pas été décrit clairement dans le forum. Le délai avant exécution est court et l'interface ne rend pas les appels facilement lisibles.

### Travail demandé

Définis les protections qui auraient dû exister, les informations à présenter avant le vote et pendant le timelock, puis la procédure de traitement si la proposition semble malveillante.

### Correction proposée

Les appels exacts, les adresses, les paramètres et les effets doivent être visibles avant le vote et vérifiables après. Les modifications de code et les transferts importants devraient avoir des règles adaptées, un délai, une simulation et des alertes. Pendant le timelock, un mécanisme de pause ou d'interruption peut exister selon l'architecture, mais ses pouvoirs et son usage doivent être définis. L'équipe doit préserver les preuves, consulter les règles de gouvernance et ne pas affirmer qu'une proposition est annulée tant que l'état on-chain ne le confirme pas.

## 19. Concevoir une politique d'urgence sans créer un pouvoir absolu

Une DAO doit pouvoir réagir à une faille, à une clé compromise ou à une transaction anormale, mais les mécanismes d'urgence peuvent devenir un pouvoir centralisé s'ils ne sont pas bornés. La conception devrait définir qui peut déclencher une pause, quelles opérations elle affecte, combien de temps elle peut durer, comment une reprise est autorisée et quelles preuves doivent être publiées.

Le pouvoir d'urgence peut être séparé du vote normal. Une petite multisignature peut suspendre temporairement certaines fonctions, tandis que la reprise exige une procédure plus large, une proposition ou une revue. Ce modèle offre une réaction rapide mais implique une confiance envers les détenteurs des clés. L'architecture doit documenter cette dépendance plutôt que présenter la DAO comme entièrement autonome.

Les actions d'urgence doivent être journalisées, annoncées et surveillées. Chaque utilisation devrait produire une explication, un horodatage, les données pertinentes et les conditions de retour. Si la pause peut arrêter les retraits, l'impact sur les utilisateurs doit être pris en compte ; si elle ne bloque pas les fonctions exploitées, sa portée peut être insuffisante.

Teste la procédure avec une fausse alerte, une vraie panne de laboratoire et une autorité d'urgence indisponible. Vérifie que les acteurs savent utiliser les accès, que les messages sont compris et que la reprise exige les contrôles prévus. Une procédure non testée peut être aussi fragile qu'un contrat non audité.

## 20. Mesurer la concentration et la participation

Le nombre total de détenteurs ne décrit pas la distribution du pouvoir. Mesure la concentration des poids de vote, la participation aux dernières propositions, la part des votes provenant des plus grands comptes, la concentration des délégations et la diversité des propositions. Ces métriques aident à détecter des tendances, mais elles ne prouvent pas à elles seules une capture ou une manipulation.

Un système peut compter de nombreuses adresses qui appartiennent à une seule entité. Les données publiques peuvent également sous-estimer la concentration lorsque les tokens sont détenus via des dépositaires, des contrats ou des délégataires. Le tableau de bord doit préciser ce qui est observable et ce qui reste inconnu. Ne transforme pas une analyse d'adresses en affirmation certaine d'identité humaine.

La participation est influencée par le coût des transactions, la complexité des propositions, les fuseaux horaires, l'accessibilité des informations et la confiance dans le processus. Une faible participation peut être un signal de désengagement ou un résultat normal d'une communauté qui délègue ses votes. Les actions d'amélioration doivent être choisies à partir des causes, pas seulement d'un objectif numérique.

La gouvernance devrait examiner si les membres comprennent les propositions, s'ils peuvent vérifier les paramètres et si les délégués rendent des comptes. Un indicateur de vote ne mesure pas la qualité de délibération. Le processus peut compléter les statistiques par des comptes rendus, des déclarations de conflits d'intérêts et une procédure pour contester une erreur de présentation.

## 21. Prévenir les propositions malveillantes et les erreurs de paramètres

Une proposition peut être dangereuse parce qu'elle est malveillante, mais aussi parce qu'elle contient une adresse erronée, un montant avec une mauvaise unité, une fonction mal choisie ou une dépendance oubliée. Le processus doit demander une simulation et une revue des appels exacts avant le vote ou au moins avant l'exécution, selon le design. Les membres doivent pouvoir comprendre les effets prévus.

La simulation devrait examiner l'état du contrat au moment envisagé de l'exécution. Une simulation ancienne peut devenir obsolète si des paramètres, des soldes ou des rôles changent avant le vote ou pendant le timelock. Les propositions critiques doivent donc être vérifiées de nouveau avant leur exécution et la gouvernance doit définir ce qui arrive si les préconditions ont changé.

Les contrôles automatiques peuvent interdire certaines classes d'action, imposer des plafonds de dépenses ou exiger des délais supplémentaires pour les mises à niveau. Ces contrôles doivent être suffisamment flexibles pour permettre les opérations légitimes, mais ne pas pouvoir être contournés immédiatement par la même action qui est censée être contrôlée. Les tests doivent inclure une séquence où une proposition réduit les garde-fous avant d'effectuer une dépense.

L'interface doit afficher les adresses cibles, les valeurs exactes, la fonction appelée et les changements d'autorisation. Une description textuelle seule peut être incohérente avec les données de transaction. L'organisation doit prévoir une façon de comparer la prose de la proposition et l'appel exécutable, et de signaler toute différence avant l'exécution.

## 22. Délégation responsable et conflits d'intérêts

La délégation améliore la capacité des membres à participer sans examiner chaque décision, mais elle confère aux délégués un pouvoir réel. Les règles devraient permettre de comprendre leur historique de vote, leurs déclarations d'intérêts et les sujets sur lesquels ils souhaitent intervenir. Elles peuvent également prévoir la révocation ou la réaffectation du pouvoir selon des règles explicites.

Les délégués devraient être tenus de divulguer les liens qui pourraient influencer une décision, par exemple un financement reçu d'un bénéficiaire ou un intérêt dans une proposition. La divulgation seule ne résout pas le conflit, mais permet aux membres de décider si la délégation reste appropriée. La gouvernance devrait aussi établir un processus pour les situations où un délégué est indisponible ou compromis.

Les systèmes techniques peuvent montrer les votes et la distribution des délégations, mais les motivations et identités ne sont pas toujours vérifiables on-chain. Les engagements de comportement sont alors des règles de gouvernance humaine. Le produit doit distinguer les faits techniques, les déclarations des participants et les conclusions qui nécessitent une enquête.

Le suivi de la délégation devrait examiner les changements soudains autour d'une proposition sensible, sans supposer que toute variation est malveillante. Les mesures d'alerte doivent servir à demander une revue, pas à censurer automatiquement des membres. Toute action de restriction doit être prévue par la constitution et rester contestable selon le processus officiel.

## 23. Exécution sûre des propositions complexes

Une proposition peut exécuter plusieurs appels dans une même séquence : mettre à niveau une implémentation, changer un rôle, modifier un paramètre et transférer des fonds. L'ordre des appels est important. Si une étape modifie les permissions avant une étape de transfert, elle peut rendre la suite plus risquée. Une proposition devrait être découpée lorsque cela améliore la vérifiabilité, mais le découpage doit préserver la logique métier.

Les tests doivent utiliser l'état exact ou une copie représentative de la trésorerie et des contrats. Vérifie que les appels échouent comme prévu si une précondition est absente et que l'ensemble ne laisse pas un état partiel qui soit dangereux. Les transactions on-chain sont atomiques dans leur exécution, mais une proposition peut être découpée en plusieurs transactions séparées ou dépendre de services hors chaîne, qui ne bénéficient pas de la même atomicité.

Le timelock doit contenir les données qui seront réellement exécutées. Si une proposition peut être modifiée après le vote sans repasser par les mêmes contrôles, les membres ne votent plus sur une action stable. Le hash des données d'exécution ou un mécanisme équivalent doit permettre de vérifier que la transaction correspond exactement à la proposition approuvée.

Après exécution, compare les événements, les paramètres et l'état des contrats avec les résultats attendus. Si une étape est rejetée, informe les membres et conserve l'identifiant de proposition. Le rapport post-exécution devrait indiquer les résultats, les écarts et les tâches de suivi plutôt que se limiter à un statut de transaction.

## 24. Runbook : proposition suspecte dans le timelock

Lorsqu'une proposition adoptée semble contenir une adresse inattendue ou un changement de permission dangereux, commence par comparer les données d'exécution à la description publique et à la simulation approuvée. Conserve le hash de proposition, les appels, les valeurs, le délai restant et les contrats affectés. Évite de publier une accusation non vérifiée ; il faut séparer l'incohérence observée de l'intention supposée.

Identifie ensuite les mécanismes disponibles : annulation par les acteurs autorisés, pause d'urgence, veto défini par les règles ou procédure de gouvernance accélérée. N'assume pas qu'une action est possible si le contrat ne l'expose pas. La réponse doit respecter la constitution en vigueur et documenter la personne ou l'organe qui autorise une mesure d'urgence.

Si l'action peut être suspendue, vérifie le résultat on-chain et confirme que le timelock n'exécutera pas encore la proposition. Avertis les utilisateurs des effets possibles et donne des informations vérifiables. Si aucune action d'annulation n'existe, la gouvernance doit expliquer les options réalistes et leurs limites plutôt que promettre un arrêt impossible.

Après l'incident, ajoute des contrôles de comparaison entre la description et les données exécutables, améliore les alertes et vérifie les pouvoirs de modification. Un incident évité reste une preuve utile sur le processus de gouvernance, et doit entraîner une action corrective mesurable.

## 25. Évaluer les mécanismes de vote alternatifs

Le vote par jeton donne un pouvoir proportionnel à la possession ou à un snapshot du token. Le vote par personne cherche à donner un pouvoir égal à des identités distinctes, mais exige un mécanisme d'unicité et introduit des enjeux de vie privée. Le vote quadratique cherche à modérer l'effet du capital, mais la résistance aux identités multiples est une hypothèse essentielle. Les modèles par réputation ou contribution peuvent récompenser l'expérience, mais risquent de créer des barrières pour les nouveaux participants.

La comparaison devrait examiner l'égalité visée, le coût de participation, les attaques sybil, les conflits d'intérêts, la facilité de vérification et la possibilité de corriger une erreur. Un vote qui donne le même poids à chaque adresse peut être facilement manipulé si une personne peut créer plusieurs adresses sans coût significatif. Un système qui exige une identité civile peut créer une dépendance envers un fournisseur ou exposer des données privées.

Il peut être utile de combiner les méthodes : par exemple, des seuils de sécurité pour certaines actions, des votes de membres pour d'autres et une délégation transparente sur le reste. Mais les catégories et les règles doivent être compréhensibles. Un modèle hybride peut devenir difficile à vérifier si chaque type de décision utilise des exceptions implicites.

La note de conception doit éviter d'appeler un mécanisme « juste » sans préciser le critère. Elle doit décrire qui gagne du pouvoir, qui peut être exclu, quelles données sont nécessaires et comment les membres peuvent contester le résultat. Le choix final dépend de l'objectif politique de la DAO autant que du code.

## 26. Concevoir une politique de trésorerie mesurable

Une politique de trésorerie doit définir les actifs gérés, les dépenses permises, les plafonds, les catégories de risque, les rôles, le reporting et le processus de contrôle. Les actifs volatils exigent une méthode de valorisation et une règle pour mesurer le budget. Les dépenses ponctuelles, les engagements récurrents et les allocations de subventions ne doivent pas être traités comme une seule opération.

Pour chaque dépense, la proposition devrait identifier le bénéficiaire, l'actif, le montant, le calendrier, les livrables attendus et les conditions de paiement. Si des paiements sont fractionnés, les étapes doivent avoir des critères vérifiables. Un vote favorable ne prouve pas qu'un livrable a été réalisé ; la DAO doit définir quelles preuves sont nécessaires et qui peut les examiner.

Les contrôles techniques peuvent inclure des plafonds par transaction ou période, un timelock, des rôles d'urgence séparés, des alertes sur les destinations nouvelles et des règles qui exigent un vote plus fort pour les changements critiques. Les limites doivent être conçues pour que le mécanisme de contrôle ne puisse pas être retiré instantanément par une proposition qui dépense toute la trésorerie. Le test doit vérifier les séquences d'appels, pas seulement chaque fonction.

Le reporting devrait relier les transferts aux propositions qui les autorisent, aux budgets, aux actifs transférés et aux résultats attendus. La valeur de marché peut changer après un vote ; le tableau de bord doit distinguer la quantité transférée de son équivalent monétaire estimé. Les membres doivent pouvoir vérifier les données on-chain et comprendre les limites de l'évaluation des résultats.

## 27. Gérer les propositions expirées, annulées ou partiellement exécutées

Une proposition peut expirer, être annulée selon les règles, devenir impossible à exécuter parce qu'un prérequis a changé ou échouer au cours d'une séquence de mise à niveau. Le système doit avoir des états précis pour ces situations et ne pas laisser l'interface indiquer simplement « terminée ». Il faut distinguer le résultat du vote, la disponibilité d'une exécution, le succès technique des appels et la confirmation du résultat métier.

Lorsque l'exécution est différée, l'état du protocole peut changer pendant le délai. Une adresse cible peut être mise à niveau, un rôle peut être transféré ou un paramètre peut changer. Le mécanisme doit définir si la proposition reste valide, si elle doit être resimulée ou si elle doit expirer. Toute règle de modification après le vote doit préserver le lien entre l'action approuvée et les données réellement exécutées.

Les opérations hors chaîne associées à une proposition peuvent ne pas être atomiques avec l'exécution on-chain. Par exemple, le transfert d'une tranche de trésorerie peut être confirmé alors que le système de reporting est indisponible. Le plan de reprise doit permettre d'identifier l'effet déjà appliqué, de reprendre le suivi et d'éviter de renvoyer un paiement.

Le rapport d'état doit conserver l'identifiant de proposition, le hash des données, le résultat du vote, le statut du timelock, le résultat d'exécution et les événements de la chaîne. Les membres et les opérateurs doivent pouvoir comprendre pourquoi une proposition n'a pas été exécutée et ce qui doit se produire ensuite.

## 28. Règles de délégation et continuité du pouvoir

Les délégations doivent avoir une sémantique claire : elles peuvent être révocables, limitées à un type de proposition, dépendre d'une hauteur de snapshot ou s'appliquer à une catégorie de vote. Si la règle n'est pas documentée, les membres peuvent croire qu'ils ont délégué un pouvoir général alors que le contrat n'autorise qu'une délégation limitée, ou inversement.

Le système doit traiter les changements de délégation pendant une proposition. Quel poids est utilisé si le membre change de délégué après le snapshot ? Quelle identité peut voter ? Un délégué peut-il voter pour son propre solde et celui qui lui est délégué dans la même transaction ? Les règles exactes doivent être définies et couvertes par des tests, afin d'éviter les doubles comptages ou un changement inattendu du poids.

La continuité exige aussi de prévoir la perte de clé, l'inactivité d'un délégué, le décès ou le départ d'un participant lorsque le modèle d'identité le prévoit, et la capacité à réaffecter le pouvoir. Pour un mécanisme fondé sur des jetons, la possession du token peut fournir une procédure de reprise ; pour un modèle fondé sur une identité vérifiée, la révocation et la réémission d'attestation peuvent exiger un processus séparé.

La gouvernance doit publier les données de délégation et les règles d'interprétation. Les informations personnelles ne doivent pas être divulguées sans besoin, mais les membres doivent pouvoir vérifier le poids et le résultat. Cette tension doit être traitée explicitement par le modèle plutôt que par des hypothèses invisibles.

## 29. Scénario d'attaque : capture d'un vote par faible participation

Une proposition critique est ouverte pendant une période où peu de membres participent. Un groupe coordonné possède ou emprunte assez de poids pour atteindre le seuil prévu et propose un changement de contrôles de trésorerie avant une seconde proposition de transfert. Le système respecte la formule de vote, mais l'issue peut contredire l'objectif de gouvernance.

La défense ne consiste pas uniquement à augmenter le quorum. Un quorum trop élevé peut rendre tout changement impossible. Il faut examiner les snapshots, la distribution des délégations, les délais, le pouvoir de modification des paramètres, les limites de dépense et l'ordre des appels. Une séparation entre les propositions qui changent la sécurité et les dépenses ordinaires peut être appropriée.

Le test de laboratoire devrait simuler plusieurs distributions de vote et la séquence complète des propositions. Mesure quand les alertes de concentration sont déclenchées, si la proposition critique reçoit un délai suffisant et si l'autorité d'urgence dispose d'une action légitime et limitée. Une alerte ne prouve pas une attaque ; elle doit déclencher une vérification selon la constitution.

La correction consiste à renforcer le processus de proposition, rendre visibles les données d'exécution, protéger les pouvoirs critiques par un délai et des approbations adaptées, puis vérifier que le système reste capable d'adopter des décisions normales. Le rapport doit présenter les limites de chaque défense et éviter de promettre qu'une configuration de vote empêche toute capture.

## 30. Mesurer la qualité de gouvernance, pas uniquement le résultat des votes

Une gouvernance efficace ne se mesure pas seulement à la proportion de propositions adoptées. Elle doit aussi considérer le temps de traitement, la qualité des informations, la participation, les conflits d'intérêts déclarés, les corrections après vote, la capacité à gérer les incidents et la proportion des actions exécutées comme annoncé.

Définis des métriques qui respectent le contexte. Le temps de décision peut être faible parce que les membres sont informés ou parce qu'ils votent sans examiner les propositions ; il doit être interprété avec d'autres preuves. Un taux de réussite technique élevé ne prouve pas que les dépenses étaient pertinentes. Un grand nombre de discussions ne prouve pas que le résultat est représentatif.

Les post-mortems de gouvernance devraient relier le résultat on-chain à l'objectif métier et aux éléments qui ont influencé la décision. Si une proposition est annulée après un changement d'état ou un incident, documente l'apprentissage et les mesures prises. La communauté doit pouvoir distinguer une erreur honnête, une hypothèse incorrecte et une action malveillante lorsque les preuves le permettent.

Ces métriques servent à apprendre et à améliorer la conception, pas à automatiser toutes les décisions humaines. Une DAO doit expliquer ses objectifs, ses critères d'évaluation et la manière dont les membres peuvent contester une mesure ou proposer un changement des règles.

## 31. Concevoir une procédure de vote accessible et vérifiable

L'accessibilité du vote dépend du coût de transaction, de la complexité de l'interface, de la clarté des propositions, des outils d'assistance et du temps nécessaire pour examiner une décision. Une gouvernance qui n'est accessible qu'aux membres capables de lire les données brutes de transaction peut concentrer le pouvoir chez une minorité technique. Le tableau de bord doit rendre les paramètres et les effets compréhensibles sans masquer les données qui permettent une vérification indépendante.

Chaque proposition devrait fournir un résumé, les raisons, les conséquences, les changements exacts, les risques, le calendrier, les dépendances et les preuves de test. Le résumé aide à comprendre mais ne remplace pas les données exécutables. L'interface doit permettre à un membre ou à un auditeur de comparer la description aux adresses, valeurs et appels qui seront exécutés.

Précise les règles concernant les membres qui ne peuvent pas participer pendant toute la période, les délégations, les clés perdues, les transactions rejetées et les erreurs de vote. Les procédures de récupération ne doivent pas attribuer un pouvoir supplémentaire sans autorisation. Si une signature est utilisée pour voter hors chaîne, le système doit empêcher qu'elle soit rejouée dans un autre domaine et expliquer comment le snapshot est déterminé.

Une revue d'accessibilité doit aussi examiner les formats alternatifs, la langue, la navigation clavier et la compréhension des statuts. Les améliorations d'interface ne modifient pas la règle de vote, mais elles peuvent modifier qui participe réellement. La gouvernance devrait mesurer ces effets sans prétendre que la seule interface garantit une participation équitable.

## 32. Revue des données d'une proposition avant vote

La donnée la plus importante n'est pas toujours le texte de la proposition ; ce sont les appels et paramètres qui seront exécutés. Avant le vote, vérifie la chaîne, les contrats cibles, les valeurs, les rôles, les méthodes appelées, les risques de mise à niveau et les résultats d'une simulation. Un changement d'adresse ou d'unités peut transformer une action décrite comme mineure en opération à risque élevé.

Un reviewer doit confirmer que le texte et les données correspondent, que les tests se rapportent à la version exacte et que le délai laisse le temps d'examiner l'action. Si la proposition utilise une valeur externe, comme un prix ou un taux, documente la source et la date, et vérifie si la valeur peut changer avant l'exécution.

La simulation doit couvrir l'état pertinent et indiquer ses limites. Une simulation après un changement de paramètres peut produire un résultat différent de celle qui a précédé le vote. Le processus devrait définir quand il faut resimuler, quand une proposition doit expirer et dans quelles conditions les appels sont jugés trop différents de l'action approuvée.

Après le vote et avant l'exécution, compare à nouveau le hash des données ou la représentation exacte des appels. Si la proposition exécutable a changé, la gouvernance doit suivre la règle de modification prévue. Les membres ne doivent pas être amenés à approuver un texte tout en exécutant une opération différente.

## 33. Préserver l'historique et la traçabilité des décisions

L'histoire de gouvernance comprend les propositions, les votes, les délégations, les discussions, les simulations, les exécutions et les rapports postérieurs. Une partie est on-chain ; une partie peut être hors chaîne. Il faut relier ces sources par des identifiants stables sans exposer des données privées inutiles. Une décision devient difficile à auditer si le contrat indique un résultat mais que la justification et le contexte ont disparu.

Conserve les versions des propositions, les hashes des données exécutables, les résultats de simulation, les votes, les événements de timelock et les transactions d'exécution. Pour les décisions hors chaîne, archive le processus d'approbation et les éventuelles déclarations de conflit d'intérêts. Les données doivent être horodatées et la source doit être identifiée, mais une date dans un document ne constitue pas à elle seule une preuve du moment exact de sa création.

Un post-mortem doit relier le résultat à l'objectif initial. Si une dépense n'a pas produit le résultat attendu, documente les coûts, les livrables, les écarts et les apprentissages. Si une proposition a été annulée, conserve la raison et la règle invoquée. Cette mémoire permet aux membres futurs d'éviter de répéter des erreurs ou de réinterpréter l'historique sans contexte.

La conservation doit néanmoins respecter la confidentialité et les obligations applicables. Les données personnelles des participants ne doivent pas être exposées uniquement pour rendre l'historique plus détaillé. Définis ce qui doit rester public, ce qui doit être retenu hors chaîne et quelles informations ne doivent jamais être collectées.

## 34. Exercices périodiques de gouvernance

Une organisation doit tester son processus avant une crise réelle. Les exercices peuvent simuler une proposition malveillante, une clé de gouvernance compromise, une indisponibilité de l'interface, un désaccord sur un livrable ou une faille qui exige une pause. L'objectif est de vérifier que les acteurs connaissent les règles, les accès et les responsabilités.

Un exercice doit avoir une portée définie, des observateurs, des critères de réussite et une limite claire afin de ne pas effectuer d'opérations réelles non autorisées. Les participants doivent déterminer quelles preuves sont nécessaires, qui peut déclencher la procédure d'urgence et comment ils communiquent aux membres. Mesure le temps de détection, de décision, d'action et de confirmation.

Après l'exercice, consigne les étapes qui ont été retardées, les informations manquantes, les rôles ambigus et les hypothèses erronées. Les actions correctives doivent avoir un responsable et un délai. Une procédure ne devrait pas être considérée comme validée tant que les changements nécessaires n'ont pas été testés.

Les exercices améliorent la gouvernance humaine aussi bien que les contrats. Ils peuvent révéler une interface qui cache les données d'exécution, un délégué qui n'a pas les bonnes informations ou une procédure d'escalade qui dépend d'une personne unique. Une DAO résiliente dispose d'un processus d'apprentissage et de révision, pas seulement d'un vote en chaîne.

## 35. Politique de sécurité pour les paramètres de gouvernance

Les paramètres qui contrôlent la gouvernance sont des actifs de sécurité. Le quorum, la période de vote, les seuils de proposition, les pouvoirs de délégation, le timelock et les rôles d'urgence déterminent comment les membres peuvent prendre des décisions et comment le système réagit à une attaque. Une proposition qui change l'un de ces paramètres peut être plus risquée qu'une dépense ordinaire.

La constitution devrait classifier les changements de paramètres selon leur impact et définir les contrôles correspondants. Une modification qui augmente un seuil de proposition peut limiter l'accès ; une modification qui supprime un timelock peut accélérer une attaque ; une modification qui change la règle de calcul du vote peut modifier la distribution du pouvoir. Les propositions de paramètres doivent afficher leur effet exact et être testées avant leur exécution.

Évite les mécanismes où une proposition peut supprimer immédiatement toutes les protections puis effectuer une action sensible dans la même séquence. Selon le modèle, des plafonds immuables ou difficiles à modifier, des délais plus longs pour les changements critiques et des contrôles séparés peuvent réduire certains risques. Ces garde-fous doivent néanmoins pouvoir être mis à jour dans des conditions explicites si les exigences changent.

Les tests doivent inclure des séquences de propositions : changement de quorum, modification des rôles, modification du timelock, puis tentative de transfert. Vérifie la règle réellement appliquée à chaque étape, les délais, les événements et l'état de la trésorerie. Un test qui examine chaque fonction isolément peut manquer le risque de composition.

## 36. Modèle de suivi des engagements et des livrables

Une DAO qui finance des travaux doit relier la décision de dépenses à des engagements vérifiables. La proposition peut spécifier le résultat attendu, les jalons, les délais, le budget, les risques et les critères d'acceptation. Ces informations doivent être suffisamment claires pour qu'un membre qui n'a pas participé à la discussion puisse comprendre si l'engagement a été rempli.

Les paiements peuvent être découpés par étape, mais le mécanisme ne doit pas prétendre automatiser un jugement qui reste humain. Si un livrable est qualitatif, la gouvernance doit définir qui l'examine, comment les conflits d'intérêts sont gérés et comment une contestation est possible. La transaction qui libère une tranche devrait être reliée à la preuve d'approbation ou au processus correspondant.

Les tableaux de bord doivent distinguer le budget approuvé, le montant payé, les engagements restant à payer et les résultats attestés. Un solde de trésorerie ne décrit pas l'ensemble des obligations futures. Une DAO peut être solvable aujourd'hui mais avoir pris des engagements qui dépassent ses ressources si les paiements futurs ne sont pas suivis.

Le bilan post-financement devrait documenter les résultats, les écarts, la valeur créée, les dépenses réelles et les enseignements. La transparence des transactions est utile, mais elle ne suffit pas à mesurer l'efficacité d'une allocation. La gouvernance devrait publier les critères d'évaluation avant les décisions et appliquer ces critères de manière cohérente.

## 37. Gestion des clés de vote et continuité des membres

La capacité à voter dépend souvent de clés de portefeuille. Une clé perdue, compromise ou partagée peut empêcher la participation ou permettre à un acteur non prévu d'exprimer un vote. Les règles de gouvernance doivent expliquer si le poids est lié au token, à une identité, à une délégation ou à une attestation, et comment un participant récupère l'accès sans obtenir indûment un pouvoir supplémentaire.

La récupération d'un compte peut être très différente d'une révocation de délégation. Si le pouvoir est attaché à la possession du token, une politique de récupération de portefeuille peut nécessiter une migration de solde et des contrôles de sécurité. Si le pouvoir est attaché à une identité vérifiée, il peut exiger une nouvelle attestation et une révocation de l'ancienne. Les tests doivent prévenir la double participation pendant une transition.

Les délégations devraient préciser comment elles changent, quand elles prennent effet et ce qui se passe si une proposition est déjà ouverte. Le système doit éviter qu'un même pouvoir soit compté deux fois ou soit transféré dans une autre identité de façon à contourner la règle du snapshot. Les événements doivent permettre de reconstruire le poids de vote.

La politique de clés doit également prévenir les conflits d'intérêts et l'usurpation de représentants. Un délégué ne devrait pas pouvoir exiger les secrets d'un membre pour voter à sa place. Les interfaces et documents de gouvernance doivent rappeler que les phrases de récupération et les clés privées ne sont jamais nécessaires pour participer à une proposition.

## 38. Préparer la migration d'une DAO vers une nouvelle architecture

Une migration de gouvernance peut déplacer la trésorerie, remplacer le contrat de vote, modifier le token ou changer les règles de proposition. Il faut définir comment l'ancienne gouvernance autorise la migration, comment les droits et les propositions en attente sont traités, et comment l'état est vérifié après le transfert. La migration peut être irréversible si les fonds ou pouvoirs sont remis au nouveau système.

Prépare un inventaire des actifs, des rôles, des paramètres, des délégations, des propositions actives et des actions en timelock. Teste la migration sur un environnement de test avec des scénarios de succès et d'échec. Vérifie les appels, les unités, les destinataires et les protections de reprise. Si les deux systèmes restent actifs simultanément, le plan doit prévenir les doubles exécutions ou les gouvernances concurrentes.

Les utilisateurs doivent être informés des changements, des nouvelles interfaces, des domaines de signature et des règles de participation. Le transfert d'un token ou la signature d'un message sur une nouvelle application peut introduire des risques d'usurpation. Les liens et adresses doivent provenir de canaux officiels, et les membres ne doivent jamais communiquer leurs secrets pour migrer.

Après la migration, compare les soldes, les rôles, les paramètres, les hashes de proposition et les événements à l'état approuvé. Archive les preuves et ferme explicitement l'ancienne voie d'exécution si telle est la décision. Une migration n'est terminée que lorsque la nouvelle gouvernance fonctionne, que les anciens pouvoirs ont été traités et que les utilisateurs peuvent vérifier le nouvel état.

## 39. Évaluer une réforme de gouvernance sans confondre intention et résultat

Une réforme peut promettre plus de participation, une meilleure représentation ou une réponse plus rapide aux incidents. Il faut définir les métriques et les effets attendus avant sa mise en œuvre. Une augmentation du taux de participation peut refléter un meilleur engagement, mais elle peut aussi provenir d'incitations temporaires ou d'une concentration accrue des votes chez quelques délégataires.

Évalue les effets sur plusieurs propositions et catégories de décision. Mesure la distribution des poids, le délai de décision, les propositions abandonnées, les contestations, les erreurs d'exécution et la diversité des participants actifs. Les indicateurs quantitatifs doivent être complétés par une revue de la qualité des informations, de l'accessibilité et de la compréhension des changements.

Le rapport devrait présenter les résultats observés et les limites. Si une réforme n'améliore pas le résultat attendu, l'organisation doit être capable de la réviser selon les règles plutôt que de conserver le changement pour des raisons de prestige. La gouvernance peut aussi nécessiter une période transitoire et une stratégie de retour.

Une réforme solide relie chaque objectif à une règle, chaque règle à un test et chaque test à une mesure post-déploiement. Le processus devient ainsi vérifiable : les membres peuvent comparer l'intention, les paramètres exécutés et les effets observés sur la gouvernance.

## 40. Contrôle final avant activation d'une gouvernance

Avant d'activer une DAO qui contrôle des actifs, vérifie la règle de vote, les snapshots, le quorum, les délégations, les états de proposition, le timelock, les droits d'urgence et la méthode d'exécution. Les appels doivent correspondre à la proposition approuvée, et les actions à fort impact doivent faire l'objet de tests représentatifs.

Teste les erreurs de paramètres, une participation faible, une délégation modifiée, une proposition malveillante, un vote répété et une panne de l'interface. Vérifie les états on-chain et les données affichées, puis documente les scénarios non couverts. Le rapport doit aussi indiquer qui détient les clés d'urgence et quels pouvoirs ne sont pas contrôlés par le vote normal.

La surveillance post-activation doit suivre les changements de rôle, les propositions de sécurité, les actions de trésorerie et les écarts entre vote et exécution. Chaque alerte critique doit avoir un propriétaire et une procédure de réponse. Si les résultats d'un test ne sont pas concluants, la publication doit être reportée ou l'exposition limitée jusqu'à ce que les propriétés essentielles soient vérifiées.

## 41. Questions d'entraînement avec corrigé

### Question 1 : Une DAO est-elle toujours entièrement autonome ?

**Correction :** Non. Les contrats automatisent certaines règles, mais la gouvernance, la gestion de crise, la conformité et l'exploitation peuvent dépendre d'acteurs humains.

### Question 2 : Quelle différence entre quorum et majorité ?

**Correction :** Le quorum définit le niveau minimal de participation ou de poids ; la majorité définit le seuil de soutien parmi les votes comptés selon les règles.

### Question 3 : Pourquoi un snapshot est-il utile ?

**Correction :** Il fixe une référence pour calculer les droits de vote et réduit certains risques liés aux changements de solde pendant la période de vote.

### Question 4 : La délégation transfère-t-elle nécessairement les jetons ?

**Correction :** Non. Elle peut confier le pouvoir de vote tout en laissant la propriété des jetons au délégant, selon le mécanisme retenu.

### Question 5 : Un timelock garantit-il qu'une proposition est sûre ?

**Correction :** Non. Il donne un délai pour examiner et réagir ; il ne corrige pas une décision mauvaise ou une surveillance inexistante.

### Question 6 : Pourquoi une multisignature ne suffit-elle pas à définir une DAO ?

**Correction :** Une multisignature contrôle l'approbation d'opérations mais ne définit pas nécessairement un processus collectif de proposition, de vote et de gouvernance.

### Question 7 : Quel risque pose un vote fondé uniquement sur les soldes au moment du vote ?

**Correction :** Le pouvoir peut être influencé par des transferts temporaires ou des capitaux empruntés. Un snapshot et des règles de participation peuvent réduire certains risques.

### Question 8 : Le vote quadratique élimine-t-il les attaques sybil ?

**Correction :** Non. Sans mécanisme crédible d'unicité ou de résistance sybil, une personne peut utiliser plusieurs identités pour contourner certaines propriétés.

### Question 9 : Que faut-il vérifier lors d'une proposition de mise à niveau ?

**Correction :** L'implémentation exacte, les données d'exécution, les pouvoirs, la compatibilité de stockage, les tests, les délais et le résultat après exécution.

### Question 10 : Que doit montrer un tableau de bord de gouvernance ?

**Correction :** Les états de proposition, le poids, le quorum, les délais, les données exactes d'exécution, les actions de trésorerie et les preuves de l'état réel.

## 42. Challenge final : créer une constitution de DAO vérifiable

Une DAO gère une trésorerie et développe un protocole. Elle veut permettre aux membres de proposer des dépenses, voter des modifications et répondre rapidement à une faille de sécurité. Elle cherche à éviter à la fois la capture économique et la paralysie du processus.

### Travail demandé

Rédige une constitution courte et un modèle technique qui définissent les catégories de décision, les critères d'éligibilité, la proposition, le quorum, la majorité, le snapshot, la délégation, le timelock, les pouvoirs d'urgence et la transparence de la trésorerie. Prépare des tests pour une faible participation, une proposition malveillante, un vote emprunté, une mise à niveau et une urgence.

### Correction proposée

La constitution distingue les objectifs, les décisions contraignantes, les responsabilités et les limites. Le modèle technique relie chaque règle à un état de contrat et à un test. Les actions qui peuvent transférer la trésorerie ou modifier le système de vote sont traitées comme des opérations critiques, avec une exécution vérifiable et un délai approprié lorsque possible.

Le modèle d'urgence donne des pouvoirs limités, surveillés et révisables. La reprise exige des critères de sécurité et un processus de communication. Le rapport final expose les risques résiduels, notamment la concentration du poids de vote, les identités sybil, les dépendances aux développeurs et les limites des mécanismes de vote. Il ne prétend pas qu'une formule de vote rend toutes les décisions équitables.

## Glossaire

**DAO** : organisation coordonnée par des règles et outils logiciels, souvent avec une gouvernance sur chaîne.

**Proposition** : action soumise au processus de décision.

**Quorum** : niveau minimal de participation requis pour que le vote puisse aboutir selon les règles.

**Majorité** : seuil de soutien nécessaire parmi les votes comptés.

**Snapshot** : référence d'état utilisée pour calculer les droits ou poids de vote.

**Délégation** : attribution du pouvoir de vote à un représentant selon les règles du système.

**Timelock** : délai imposé entre l'approbation et l'exécution d'une action.

**Multisignature** : mécanisme qui exige plusieurs signatures pour autoriser une opération.

**Capture de gouvernance** : situation où un acteur ou un groupe peut imposer des décisions contraires aux objectifs attendus.

**Vote quadratique** : système qui cherche à modérer l'effet du poids économique, avec des hypothèses particulières sur l'unicité des participants.

**Trésorerie** : actifs contrôlés et dépensés par le processus de gouvernance.

**Exécution** : appel ou ensemble d'appels qui applique effectivement une décision adoptée.

## Pour aller plus loin

- OpenZeppelin Governor : https://docs.openzeppelin.com/contracts/governance
- Documentation OpenZeppelin Contracts : https://docs.openzeppelin.com/contracts/
- Ethereum.org, DAO : https://ethereum.org/en/dao/
- Documentation de la gouvernance utilisée par le protocole étudié : vérifier la version des contrats et les pouvoirs actifs.

Les règles de gouvernance doivent être testées avec leur implémentation exacte. Un vote transparent et un contrat public sont des outils de vérifiabilité, mais ils ne garantissent ni une participation équitable, ni la sécurité économique, ni la conformité juridique du projet.
