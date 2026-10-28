# Rôle du DBA et architecture SGBD — Intermédiaire

> **Mise en contexte.** Une application de formation connaît une croissance rapide. Les inscriptions augmentent, les résultats de quiz doivent être enregistrés sans doublon, les tableaux de bord deviennent lents et une mise à jour provoque un blocage entre deux transactions. Le code applicatif n’explique pas à lui seul ces incidents : il faut comprendre comment le serveur de base de données organise sa mémoire, ses fichiers, ses transactions, ses connexions et ses mécanismes de reprise. Le rôle du DBA consiste à transformer ce système essentiel en un service prévisible, observable, sécurisé et récupérable. Ce cours suit un cas fil rouge : exploiter la base d’une plateforme Skill-Tree, depuis l’analyse de son architecture jusqu’à la préparation d’un plan de restauration.

## Objectifs pédagogiques et parcours pratique

À la fin de ce cours, vous devrez savoir décrire les principales couches d’un système de gestion de base de données (SGBD), expliquer le trajet d’une requête, distinguer les responsabilités de l’administration de celles du développement, diagnostiquer une saturation de connexions, interpréter les symptômes d’un verrouillage, choisir des indicateurs de supervision et préparer un changement réversible. Vous devrez aussi pouvoir expliquer pourquoi la disponibilité, la cohérence, la sécurité et la capacité de restauration sont des propriétés complémentaires, et non des sujets indépendants.

Le parcours pratique suppose que vous avez déjà écrit des requêtes SQL, utilisé des clés et des contraintes, et construit un schéma relationnel. Les exemples utilisent PostgreSQL et mentionnent MySQL lorsque le comportement varie. Les commandes de diagnostic sont à exécuter sur une instance de test, avec des droits appropriés. Certaines vues système nécessitent un compte autorisé. Ne copiez jamais de commande destructive sur une production sans identifier l’instance, lire les préconditions et préparer un retour arrière.

Le DBA n’est pas uniquement une personne qui « répare la base quand elle est lente ». Il conçoit les procédures d’exploitation, prévient les incidents, explique les compromis d’architecture, automatise les tâches répétitives et rend les décisions mesurables. Une bonne administration s’appuie sur des preuves : métriques, journaux, plans d’exécution, historiques de changement et tests de restauration.

## 1. Le métier de DBA dans une équipe produit

Le DBA — administrateur de bases de données — est responsable de la fiabilité opérationnelle du stockage structuré. Dans une petite équipe, cette responsabilité peut être partagée avec un ingénieur backend ou un ingénieur plateforme. Dans une organisation plus grande, elle peut être répartie entre DBA de production, administrateur de plateforme de données, ingénieur fiabilité, responsable sécurité et développeurs propriétaires d’un domaine métier.

Ses missions se répartissent en plusieurs familles. La conception consiste à évaluer le modèle de données, la volumétrie, la croissance, la distribution des accès et les exigences de disponibilité. L’exploitation couvre le provisionnement, les mises à jour, le suivi des connexions, la gestion de l’espace disque et la rotation des journaux. La sécurité inclut les rôles, les privilèges, les secrets, le chiffrement, l’audit et la conformité. La continuité comprend les sauvegardes, la réplication, les tests de restauration et le plan de reprise. La performance concerne les requêtes, les index, les statistiques, la contention et la capacité.

Le DBA ne décide pas seul de tous les arbitrages. Le propriétaire métier exprime la perte de données acceptable. Le responsable de service fixe les objectifs de disponibilité. Le développeur explique les accès attendus et les garanties transactionnelles nécessaires. La sécurité détermine les contraintes de protection. Le DBA traduit ces besoins en mécanismes vérifiables et signale les conflits. Par exemple, réduire la durée de conservation peut répondre à un besoin de confidentialité, mais compliquer l’investigation d’incidents. Accroître les répliques peut améliorer la capacité de lecture, mais créer des retards de propagation ou des coûts supplémentaires.

Une responsabilité essentielle est de rendre explicites les niveaux de service. Le RPO, ou objectif de point de reprise, représente la quantité maximale de données que l’organisation accepte de perdre, exprimée en durée. Le RTO, ou objectif de temps de reprise, représente la durée maximale acceptable avant de rétablir le service. Un objectif « nous devons pouvoir redémarrer vite » n’est pas suffisamment opérationnel. Un objectif tel que « restaurer le service en moins de 45 minutes avec une perte maximale de cinq minutes de transactions confirmées » permet d’évaluer une solution et d’écrire un test.

Il faut également distinguer responsabilité et autorité. Le DBA doit avoir les droits nécessaires pour intervenir, mais l’accès permanent à tous les environnements augmente le risque. Les comptes personnels, les accès d’urgence et les opérations privilégiées doivent être contrôlables. Les changements risqués suivent un processus d’approbation adapté à leur impact. Une procédure d’urgence n’est pas une absence de procédure : elle décrit qui peut décider, comment limiter le risque et comment documenter l’action après coup.

## 2. Architecture logique et architecture physique

L’architecture logique décrit les objets que l’utilisateur SQL manipule : bases, schémas, tables, vues, index, séquences, fonctions, rôles et contraintes. L’architecture physique décrit les fichiers, pages, segments, journaux, caches, volumes, dispositifs de stockage et mécanismes de reprise qui supportent ces objets. La distinction est fondamentale : deux tables logiquement similaires peuvent avoir un coût opérationnel très différent selon leur taille, leurs index, leur répartition et leur activité d’écriture.

Un schéma relationnel possède des identifiants stables, des règles d’intégrité et des relations explicites. La base physique a, elle, des contraintes de ressources : mémoire, cycles CPU, latence disque, débit réseau, limites de connexions et espace disponible. Les requêtes SQL sont compilées ou transformées en plans exécutables. Le moteur estime les coûts, choisit des méthodes d’accès et orchestre la lecture, les verrous ou les versions de lignes. La qualité de ce plan dépend notamment des statistiques disponibles et de la forme réelle des données.

Le serveur de base de données peut fonctionner sur une machine virtuelle, un conteneur ou une plateforme managée. Dans un service managé, l’équipe fournisseur prend généralement en charge une partie du système d’exploitation, des mises à jour et de la disponibilité physique. Cela ne supprime pas les responsabilités applicatives : schéma, index, droits, requêtes, sauvegardes selon le service, contrôle des coûts et validation d’une restauration restent des sujets essentiels. « Managé » ne signifie pas « sans administration ».

Le schéma suivant résume le trajet typique d’une requête relationnelle. Les détails d’implémentation diffèrent selon le moteur, mais l’idée générale est commune.

~~~mermaid
flowchart TD
    A[Application] --> B[Connexion ou pool]
    B --> C[Analyse et validation SQL]
    C --> D[Réécriture et planification]
    D --> E[Plan d'exécution]
    E --> F[Cache et mémoire]
    E --> G[Gestion des transactions]
    F --> H[Stockage des pages]
    G --> I[Journaux de reprise]
    H --> J[Résultats]
    I --> K[Reprise après incident]
    J --> A
~~~

Une requête ne se contente donc pas de « lire un fichier ». Le moteur évalue les chemins d’accès possibles, synchronise des opérations concurrentes et applique les garanties de cohérence. Si une requête attend un verrou, ajouter de la mémoire n’est pas nécessairement utile. Si un index réduit les lectures mais augmente fortement le coût de chaque écriture, le bénéfice peut être négatif. Le diagnostic doit séparer le temps de planification, le temps d’attente, le temps d’exécution et le temps passé dans le client ou le réseau.

## 3. Processus, mémoire, connexions et cache

Les serveurs de bases de données utilisent des structures mémoire pour éviter de relire constamment le stockage et pour organiser le travail. PostgreSQL utilise notamment un cache partagé de pages, une zone de travail par opération selon la configuration, ainsi que des processus de fond. MySQL/InnoDB s’appuie notamment sur un buffer pool pour les données et les index. Les noms, les tailles et les modes de fonctionnement varient : ne recopiez pas un paramètre PostgreSQL dans MySQL en supposant une correspondance.

Le cache ne rend pas toute requête gratuite. Il peut réduire les lectures physiques, mais le moteur doit toujours parcourir les index ou les lignes nécessaires, vérifier les prédicats, combiner les résultats et transmettre les données. Une requête qui renvoie plusieurs millions de lignes peut saturer le réseau ou le client, même si les données sont en mémoire. Réduire le volume de données retourné est souvent aussi important que le temps d’accès au disque.

Chaque connexion a un coût : mémoire, structures de session, ordonnanceur, transactions, sockets et travail de maintenance. Ouvrir sans limite une connexion par requête applicative conduit à une amplification. Une application avec 12 processus et 20 connexions par processus peut tenter de créer 240 sessions, avant de compter les tâches périodiques et les outils d’administration. La limite du serveur ne doit pas être choisie sans observer le coût de chaque session et la capacité CPU réelle.

Un pool de connexions réutilise des sessions afin d’éviter un établissement permanent des connexions. Il apporte une limite de concurrence et amortit le coût de démarrage. Cependant, un pool peut lui-même être mal configuré : trop petit, il crée une file d’attente; trop grand, il transfère la saturation vers le serveur. L’équipe doit observer le temps d’attente du pool, son nombre de connexions actives, le nombre en attente, la durée de transaction et le nombre de connexions abandonnées.

Une transaction longue peut conserver des versions de lignes, des verrous ou des ressources plus longtemps que nécessaire. La session reste alors active même si elle n’exécute aucune requête à l’instant de l’observation. Il faut regarder l’état de la connexion et le début de la transaction, pas seulement la dernière requête. Une bonne pratique applicative consiste à ne pas garder une transaction ouverte pendant une interaction utilisateur ou un appel HTTP externe.

Exemple de vérification des sessions PostgreSQL :

~~~sql
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    now() - xact_start AS transaction_age,
    wait_event_type,
    wait_event,
    left(query, 120) AS query_excerpt
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY xact_start NULLS LAST;
~~~

Cette requête peut révéler des transactions anciennes et des attentes. Elle ne fournit pas à elle seule le diagnostic complet : une requête affichée peut être tronquée, l’accès aux détails peut être limité et une ligne « active » ne signifie pas forcément qu’elle consomme intensément le processeur. Corrélez avec les métriques système et le journal des requêtes lentes.

## 4. Transactions et propriétés ACID

Une transaction regroupe des opérations qui doivent être validées ou annulées de façon cohérente. Les quatre propriétés couramment résumées par ACID sont l’atomicité, la cohérence, l’isolation et la durabilité. L’atomicité signifie que les modifications du groupe sont appliquées comme une unité. La cohérence signifie que les contraintes définies par le système restent satisfaites lorsque les transactions respectent ces règles. L’isolation décrit la façon dont les opérations concurrentes s’observent. La durabilité signifie qu’une transaction confirmée résiste aux défaillances couvertes par les garanties du moteur.

Considérons une inscription à une formation limitée à 30 places. Le système doit vérifier la disponibilité puis réserver une place. Si deux requêtes lisent simultanément qu’il reste une place et mettent toutes deux à jour le compteur sans coordination correcte, la limite peut être dépassée. Le problème n’est pas uniquement la syntaxe SQL : il s’agit d’un invariant métier soumis à la concurrence. Une transaction et une contrainte adaptée peuvent empêcher que cet invariant dépende d’un simple test applicatif.

~~~sql
BEGIN;

UPDATE formations
SET places_restantes = places_restantes - 1
WHERE id = 42
  AND places_restantes > 0;

-- L'application doit vérifier que exactement une ligne a été modifiée.
-- Si aucune ligne n'a été modifiée, la dernière place n'est plus disponible.

INSERT INTO inscriptions (apprenant_id, formation_id, inscrit_le)
VALUES (105, 42, CURRENT_TIMESTAMP);

COMMIT;
~~~

Cet exemple illustre la logique mais doit être adapté au schéma réel : l’application doit annuler la transaction si l’UPDATE ne modifie aucune ligne ou si l’insertion échoue. Pour empêcher la double inscription, une contrainte UNIQUE sur le couple apprenant/formation est également nécessaire. Une transaction ne remplace pas une contrainte d’intégrité, pas plus qu’une contrainte ne remplace toute logique transactionnelle.

Une transaction validée devient durable selon la configuration du moteur et le matériel sous-jacent. Le journal de reprise permet au moteur de reconstruire l’état après un arrêt inattendu. Les garanties dépendent des paramètres de synchronisation, du stockage et, en environnement distribué, de la politique de réplication. Un accusé de réception applicatif ne doit pas être interprété au-delà du niveau de durabilité effectivement garanti.

La cohérence doit être définie concrètement. Des contraintes NOT NULL, CHECK, UNIQUE et FOREIGN KEY encadrent certaines règles. D’autres invariants sont contrôlés dans une transaction ou via une conception appropriée. Une validation complexe uniquement dans le code devient fragile quand plusieurs applications, scripts de migration et tâches d’administration écrivent dans la même base. Les règles structurantes doivent être au plus près des données lorsque le moteur peut les exprimer efficacement.

## 5. Concurrence, isolation, verrous et interblocages

Les applications modernes exécutent plusieurs transactions simultanément. Le moteur doit permettre une concurrence efficace tout en garantissant que chaque transaction observe un état acceptable. Les mécanismes précis diffèrent. PostgreSQL utilise le contrôle de concurrence multiversion (MVCC) pour que des lectures puissent généralement voir une version cohérente sans bloquer systématiquement les écritures. InnoDB utilise également des mécanismes de versions et de verrous. MVCC ne signifie pas « aucun verrou » : les modifications de mêmes lignes, certaines opérations DDL et des contraintes de sérialisation peuvent encore provoquer une attente.

Les niveaux d’isolation déterminent quels phénomènes sont possibles. READ COMMITTED fournit, dans PostgreSQL, une vue cohérente pour chaque instruction. REPEATABLE READ maintient une vue plus stable pendant la transaction. SERIALIZABLE cherche à garantir un résultat équivalent à un ordre séquentiel, mais peut annuler des transactions qui doivent être réessayées. Ne considérez pas les libellés comme des garanties identiques dans tous les moteurs : l’implémentation et les phénomènes précis doivent être vérifiés dans la documentation de la version utilisée.

Un verrouillage peut être légitime : une transaction met à jour une inscription et une autre doit attendre. Le problème apparaît lorsque les attentes deviennent très longues, se propagent ou concernent des opérations nombreuses. Les causes typiques incluent une transaction laissée ouverte, un traitement par lots trop gros, un ordre de verrouillage incohérent, une requête manquant d’index ou une migration qui bloque une table active.

Un interblocage, ou deadlock, survient lorsque deux transactions se bloquent mutuellement, chacune attendant une ressource détenue par l’autre. Exemple : la transaction A verrouille la ligne X puis demande Y; la transaction B verrouille Y puis demande X. Un moteur qui détecte le cycle choisit généralement une transaction victime et l’annule. L’application doit gérer cet échec et peut réessayer la transaction complète avec une stratégie bornée. Le réessai ne doit pas répéter des effets externes non idempotents comme un paiement ou un courriel sans mécanisme de déduplication.

~~~mermaid
sequenceDiagram
    participant A as Transaction A
    participant DB as Moteur SGBD
    participant B as Transaction B
    A->>DB: Verrouille la ligne X
    B->>DB: Verrouille la ligne Y
    A->>DB: Demande Y
    DB-->>A: Attente
    B->>DB: Demande X
    DB-->>DB: Détecte le cycle d'attente
    DB-->>B: Annulation de la transaction victime
    B->>DB: ROLLBACK
    DB-->>A: Le verrou devient disponible
~~~

Pour réduire les deadlocks, maintenez les transactions courtes, accédez aux ressources dans un ordre cohérent, créez les index nécessaires aux prédicats et évitez de verrouiller des lignes non pertinentes. Un index n’élimine pas tous les blocages; il peut réduire la durée de recherche et le nombre de lignes concernées. Ne désactivez pas la détection de deadlock pour masquer le symptôme. Collectez les informations utiles, identifiez les requêtes en cause, puis corrigez la cause dans l’application ou la structure des données.

Le DBA doit connaître les requêtes permettant de lister les sessions bloquantes et bloquées. Une vue de diagnostic peut changer entre versions. Les scripts d’exploitation doivent être testés et versionnés, et être documentés avec les droits nécessaires. Terminer arbitrairement une session peut annuler un traitement métier en cours; cette action demande une analyse des effets, une communication au propriétaire du service et un suivi après intervention.

## 6. Journaux de transaction, écritures et récupération

Les moteurs relationnels utilisent des mécanismes de journalisation pour préserver la cohérence des écritures. Dans PostgreSQL, le WAL (Write-Ahead Logging) enregistre les changements nécessaires à la reprise avant que les pages de données correspondantes n’aient toutes été écrites sur leur emplacement final. Au redémarrage, le moteur rejoue ou analyse les informations de journal afin de ramener la base à un état cohérent. Le principe général est de permettre une reprise sans devoir considérer une écriture partielle comme une transaction complète.

Les journaux ne sont pas de simples fichiers de diagnostic humain. Ils remplissent un rôle technique central. Une stratégie de sauvegarde continue peut archiver les segments WAL nécessaires à une récupération à un instant donné. Cela peut réduire la perte de données, mais exige que les sauvegardes de base et les segments requis soient complets, accessibles et compatibles avec la procédure de reprise. Garder trop peu de journaux peut rendre une récupération impossible; les conserver indéfiniment peut saturer le stockage et entraîner une panne.

La synchronisation des écritures a un coût. Des réglages plus permissifs peuvent augmenter les performances mais affaiblir les garanties de durabilité. Un DBA ne doit jamais modifier un paramètre critique uniquement parce qu’un test synthétique va plus vite. Il faut documenter la garantie sacrificée, les transactions concernées et l’accord du propriétaire métier. Les valeurs par défaut sont des choix de compromis, non des réponses universelles.

Les écritures peuvent également consommer du stockage dans des fichiers temporaires, des versions de lignes obsolètes, des index, des journaux, des fichiers de sauvegarde et des copies de réplique. La capacité doit être calculée sur la croissance réelle des données et les pics d’activité, pas seulement sur la taille actuelle des tables. Une base de 20 Go avec 200 Go de fichiers temporaires potentiels ou de journaux d’archivage peut manquer d’espace malgré une taille logique modeste.

La supervision de l’espace disque doit distinguer le stockage des données, le stockage de WAL/binlogs, les fichiers temporaires, les sauvegardes et les journaux applicatifs. Elle doit déclencher des alertes avant la saturation, avec un seuil tenant compte de la vitesse de croissance et du temps de réaction opérationnel. Une alerte « disque à 95 % » peut être trop tardive si le volume se remplit en quelques minutes.

## 7. Disponibilité, réplication et haute disponibilité

La haute disponibilité vise à maintenir ou rétablir rapidement le service lorsqu’un composant tombe en panne. Une seule instance peut suffire à un prototype; un service métier critique peut exiger plusieurs zones de défaillance, une réplication, une surveillance de santé, un mécanisme de bascule et une procédure claire de retour au fonctionnement normal.

La réplication copie les modifications d’une instance vers une ou plusieurs autres. Une réplique synchrone peut contribuer à des garanties plus strictes concernant la perte de transactions confirmées, au prix d’une latence et d’une dépendance à la disponibilité des nœuds participants. Une réplique asynchrone peut continuer à recevoir des requêtes lorsque le réseau est perturbé, mais elle risque d’avoir du retard. Si l’application lit immédiatement une donnée depuis une réplique asynchrone après l’avoir écrite sur le primaire, elle peut ne pas voir cette modification pendant un court intervalle.

Il faut distinguer réplication, sauvegarde et redondance. Une réplication répercute souvent les suppressions et corruptions logiques. Si un utilisateur supprime accidentellement 10 000 inscriptions, les répliques vont généralement reproduire cette suppression. Une sauvegarde fournit une copie récupérable à un point donné. La redondance matérielle protège contre certaines pannes physiques, mais ne remplace ni les copies indépendantes ni un exercice de restauration. Une architecture solide utilise plusieurs mécanismes qui couvrent des modes de défaillance différents.

Le basculement automatisé peut rétablir le service, mais doit prévenir le double primaire, contrôler le quorum selon l’architecture et informer les clients de la possibilité de réessayer. Un client peut avoir perdu la réponse réseau après une transaction qui a pourtant été validée. Répéter l’opération sans identifiant d’idempotence peut créer un doublon. Le protocole applicatif doit donc traiter les timeouts ambigus avec prudence.

~~~mermaid
flowchart LR
    APP[Applications] --> LB[Point de connexion]
    LB --> P[Primaire]
    P -->|Réplication| R1[Réplique lecture]
    P -->|Journal archivé| B[Stockage de sauvegarde]
    M[Supervision] --> P
    M --> R1
    M --> B
    M --> F[Bascule contrôlée]
    F --> R1
    R1 --> LB
~~~

Une architecture de haute disponibilité doit définir des scénarios testables : panne du processus, perte d’une machine, perte de connectivité, disque saturé, retard de réplication, corruption logique, erreur de déploiement et indisponibilité du fournisseur. Pour chaque scénario, documentez la détection, le décideur, la procédure, les données qui peuvent être perdues, les vérifications post-reprise et la communication aux utilisateurs.

## 8. Sauvegardes et restauration : la garantie réelle

Une sauvegarde n’est utile que si elle peut être restaurée dans le délai demandé et si le contenu restauré est cohérent. Un job vert prouve généralement que la tâche s’est exécutée; il ne prouve pas qu’une sauvegarde est complète, que les clés de chiffrement sont disponibles, que les journaux associés existent, ni que l’application peut utiliser la base restaurée.

Une politique de sauvegarde précise les objets inclus, la fréquence, la rétention, le chiffrement, les comptes qui peuvent lire les copies, les régions ou supports utilisés, les contrôles d’intégrité et les tests périodiques. La rétention doit répondre aux exigences métier, juridiques et de confidentialité. Les copies ne doivent pas toutes dépendre du même compte privilégié ou du même domaine de panne. Si un attaquant contrôle l’environnement et peut supprimer toutes les sauvegardes, la stratégie est insuffisante.

Une sauvegarde complète capture un ensemble de données à un moment défini. Une stratégie incrémentale ou différentielle réduit le volume à sauvegarder, mais peut compliquer la restauration et rendre la chaîne de dépendances essentielle. Les journaux de transaction archivés permettent, si les préconditions sont réunies, de se rapprocher d’un instant cible. La restauration à un instant donné (PITR) exige d’identifier l’heure de l’événement, de disposer d’une sauvegarde de base exploitable et des journaux qui couvrent le chemin de reprise.

En cas de corruption logique, ne rétablissez pas aveuglément l’ancienne sauvegarde sur l’unique production. Préservez les preuves, identifiez la dernière heure connue comme saine, restaurez d’abord dans un environnement isolé, validez les données, puis définissez comment réconcilier les transactions plus récentes. Une restauration complète peut effacer des modifications légitimes effectuées après le point choisi. Le plan doit préciser la procédure de reprise, la validation métier et le sort des données créées pendant l’intervalle.

Le test de restauration doit enregistrer la date, la sauvegarde source, la version du moteur, les paramètres nécessaires, la durée, les erreurs rencontrées, le volume restauré et les contrôles de cohérence effectués. Mesurez le RTO réellement obtenu et la quantité de données perdue par rapport au point attendu. Un test qui se contente de constater qu’un processus a démarré est insuffisant.

## 9. Sécurité et séparation des privilèges

La sécurité d’une base ne se réduit pas à un mot de passe complexe. Elle combine l’identité, l’authentification, l’autorisation, le réseau, le chiffrement, l’audit, la gestion des secrets, la maintenance et la réponse aux incidents. Le DBA doit limiter l’accès au strict nécessaire, séparer les comptes applicatifs des comptes d’administration et empêcher qu’une fuite d’identifiants d’application donne un contrôle total sur l’instance.

Les rôles doivent représenter des capacités précises : lecture de certaines tables, écriture dans un domaine, exécution d’une fonction contrôlée, migration de schéma ou administration complète. Les applications ne devraient pas se connecter avec le superutilisateur. Une séparation entre rôle de migration et rôle d’exécution évite que l’application courante puisse modifier librement les structures ou créer de nouveaux privilèges.

Le principe du moindre privilège est dynamique. Un développeur peut avoir besoin d’une lecture temporaire pour diagnostiquer un incident; cette permission doit avoir une justification, une durée et une trace. Les comptes de service doivent être associés à un propriétaire, une finalité, une procédure de rotation et un mécanisme de révocation. Les secrets ne doivent pas être enregistrés en clair dans le dépôt, les fichiers de journal ou les tickets.

Le chiffrement en transit protège la communication entre client et serveur lorsqu’il est correctement configuré et vérifié. Le chiffrement au repos protège les fichiers ou volumes contre certains scénarios de vol de support, mais ne remplace pas les autorisations SQL. Un compte applicatif déjà autorisé peut généralement lire les données que l’application lui demande, même si le disque est chiffré. Il faut donc combiner les contrôles techniques et la réduction des données exposées.

Les données personnelles doivent être classées et traitées selon leur finalité. La minimisation consiste à ne collecter que ce qui est nécessaire. La durée de conservation doit être justifiée. Les environnements de test utilisent des données synthétiques ou correctement anonymisées lorsque cela est nécessaire. Les sauvegardes contenant des données supprimées de la production nécessitent une politique de rétention et une procédure de purge adaptée; leur conservation ne doit pas devenir une zone sans règle.

La revue des droits doit être régulière. Listez les rôles, les membres, les privilèges directs, les rôles hérités, les fonctions avec droits particuliers et les comptes inactifs. Après un incident, révoquez les secrets compromis, examinez les accès inhabituels, préservez les journaux pertinents et reconstruisez la chronologie sans détruire les éléments nécessaires à l’investigation.

## 10. Observabilité : savoir ce qui se passe

L’observabilité rassemble les indicateurs, les journaux et les traces nécessaires pour expliquer un comportement du système. Un tableau de bord utile ne doit pas seulement afficher beaucoup de chiffres; il doit aider à répondre à une question opérationnelle. Une latence applicative élevée peut provenir du serveur SQL, de l’attente de connexion, de l’accès disque, du réseau, du verrouillage ou du volume de résultats. Il faut distinguer ces possibilités.

Les métriques de base incluent le taux de requêtes, les percentiles de latence, le nombre de sessions actives, les connexions en attente, les transactions ouvertes, les verrous, les deadlocks, les erreurs, les écritures, les lectures physiques, les lectures dans le cache, les checkpoints, les fichiers temporaires, le retard de réplication et la croissance du stockage. Les définitions doivent être stables et documentées; un ratio isolé sans fenêtre de mesure peut induire en erreur.

Les percentiles permettent d’observer la queue de distribution. Une médiane acceptable n’empêche pas 1 % des requêtes de prendre plusieurs secondes. Si un parcours utilisateur dépend de quatre appels séquentiels, la latence de chaque appel s’additionne. Une action peut être lente alors que chaque requête semble « presque normale ». Mesurez le flux complet au niveau applicatif et corrélez les appels à la base.

Les journaux doivent contenir assez d’informations pour l’analyse, sans exposer de mots de passe, de jetons, de données sensibles ou de valeurs personnelles inutiles. Un identifiant de corrélation est souvent plus utile que l’enregistrement de toute la requête avec ses paramètres réels. La collecte des requêtes lentes doit être configurée avec un seuil adapté, une politique de rétention et un contrôle d’accès.

Une alerte doit être déclenchée par un risque opérationnel et inclure un contexte d’action. « CPU à 85 % » n’indique pas forcément une défaillance; un pic bref peut être attendu. « Latence au 95e percentile supérieure à l’objectif pendant dix minutes avec augmentation du taux d’erreur » est plus proche d’un symptôme utilisateur. Les seuils doivent être ajustés sur l’historique, l’heure, la saisonnalité et le budget d’erreur.

## 11. Changements de schéma, migrations et déploiements

Un changement de schéma est un changement de production. Une migration peut bloquer une table, consommer du disque, produire beaucoup de WAL, perturber les répliques ou rendre une ancienne version de l’application incompatible. Le fait qu’une migration réussisse sur une base vide ne prouve pas qu’elle est sûre sur une table contenant plusieurs dizaines de millions de lignes.

Adoptez une stratégie de compatibilité progressive. Dans un premier déploiement, ajoutez une colonne de manière compatible, sans imposer immédiatement un comportement qui casse l’ancienne version. Déployez ensuite le code qui écrit la nouvelle représentation, réalisez un backfill par lots, vérifiez les données, basculez les lectures, puis retirez l’ancien champ dans une version ultérieure. Ce modèle « expansion puis contraction » facilite le retour arrière car chaque étape conserve temporairement la compatibilité.

Chaque migration doit documenter les préconditions, la durée estimée, les verrous attendus, l’impact sur le stockage, le comportement en cas d’interruption et la procédure de rollback. Toutes les migrations ne sont pas réversibles : supprimer une colonne détruit des informations et ne peut pas être annulé par une simple instruction inverse. Un rollback du code n’est pas forcément un rollback des données. Distinguez les deux dans le plan de changement.

Les déploiements sans interruption sont aussi une question d’architecture applicative. Une migration peut être techniquement valide mais incompatible avec deux versions de l’application exécutées en parallèle. La procédure doit considérer le code, les données, les tâches asynchrones, les connexions persistantes et les répliques. Les scripts de migration doivent être idempotents ou conçus pour détecter un état déjà appliqué, quand cette propriété est réalisable.

## 12. Capacité, croissance et coût

La capacité doit être planifiée sur la charge réelle et le profil de croissance. Estimez le nombre de lignes, leur taille moyenne, les index, l’historique, les pièces jointes, les fichiers temporaires, les journaux et les sauvegardes. Les index peuvent parfois occuper autant ou davantage d’espace que les données correspondantes, selon le modèle et les colonnes indexées. Ne calculez pas la capacité uniquement en multipliant le nombre de lignes par la taille des champs.

Le coût CPU dépend de la concurrence, des plans et du travail effectué. Une requête qui relit une grande table toutes les secondes peut dominer la charge. Une requête coûteuse exécutée une fois par jour peut rester acceptable si elle est planifiée hors pointe. L’analyse doit inclure fréquence, durée, nombre de lignes examinées, nombre de lignes renvoyées et impact sur les autres utilisateurs.

Le dimensionnement vertical apporte plus de ressources à un seul nœud; il est souvent simple, mais possède des limites et peut accroître le coût. L’échelle horizontale répartit la charge et peut exiger partitionnement, sharding ou répliques. La complexité opérationnelle augmente avec les composants distribués. N’adoptez pas un sharding avant d’avoir démontré que les mesures plus simples — requêtes, index, cache, pool, rétention et capacité — ne résolvent pas le besoin.

Les coûts comprennent aussi les transferts de données, les sauvegardes, le stockage de journaux, les instances de test et le temps d’exploitation. Une réplique supplémentaire peut coûter plus cher qu’une optimisation de requête correctement ciblée. Le choix doit comparer coût total, risques, besoins de reprise et efforts de maintenance, pas uniquement le prix d’une instance.

## 13. Procédure de diagnostic lors d’une dégradation

Commencez par confirmer le symptôme. Est-ce une erreur de connexion, un délai d’attente, une requête lente, une panne complète ou un problème limité à un endpoint? Notez l’heure, la région, l’application concernée, les utilisateurs touchés et la première occurrence connue. Une bonne chronologie évite de modifier le système sur la base d’une impression.

Vérifiez ensuite la santé globale : disponibilité du serveur, place disque, CPU, mémoire, connexions, retard de réplication et erreurs dans les journaux. Identifiez les changements récents : migration, déploiement de code, variation de charge, rotation des secrets ou changement de configuration. Ne modifiez pas plusieurs paramètres simultanément sans hypothèse testable; cela rend l’effet difficile à interpréter.

Pour les requêtes lentes, identifiez la famille de requêtes et les paramètres représentatifs. Examinez le plan d’exécution, les statistiques et les index. Pour les connexions saturées, comparez la demande de l’application à la limite du serveur et au nombre d’instances applicatives. Pour les verrous, identifiez la transaction bloquante et son propriétaire avant toute interruption. Pour les problèmes de stockage, déterminez la catégorie de fichiers qui croît plutôt que de supprimer des fichiers au hasard.

Une intervention doit réduire le risque tout en préservant les éléments utiles. Si une action temporaire est nécessaire, indiquez l’heure, la raison, la personne qui l’exécute, le périmètre et les critères de retrait. Après le rétablissement, vérifiez la cohérence métier, les files en attente, la latence et les erreurs. Organisez ensuite une analyse de cause racine qui cherche les conditions ayant permis l’incident, plutôt que de s’arrêter à « le serveur était lent ».

## 14. Atelier pratique : observer une base de test

Créez une base isolée avant toute expérimentation. Les commandes suivantes illustrent PostgreSQL et supposent que les outils clients sont installés, que le serveur accepte les connexions et que votre compte dispose des privilèges nécessaires.

~~~bash
createdb skilltree_lab
psql -d skilltree_lab
~~~

Dans la session SQL, créez quelques tables représentatives :

~~~sql
CREATE TABLE apprenants (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE inscriptions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    apprenant_id BIGINT NOT NULL REFERENCES apprenants(id),
    formation_id BIGINT NOT NULL,
    inscrit_le TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (apprenant_id, formation_id)
);

INSERT INTO apprenants (email)
VALUES ('amina@example.test'), ('paul@example.test');

INSERT INTO inscriptions (apprenant_id, formation_id)
VALUES (1, 101), (2, 101);
~~~

Observez la connexion et l’identité de la base :

~~~sql
SELECT current_database(), current_user, version();
SELECT count(*) AS nombre_apprenants FROM apprenants;
SELECT pid, usename, state, now() - xact_start AS age_transaction
FROM pg_stat_activity
WHERE datname = current_database();
~~~

L’objectif est de relier une opération observable à la structure qui l’explique. L’identifiant de base est important avant un changement, car un environnement de test peut ressembler fortement à la production. Les variables de connexion, le nom de l’instance et la commande utilisée doivent être contrôlés avant toute écriture.

Pour simuler une attente, ouvrez deux sessions dans cet environnement de laboratoire. Dans la session A :

~~~sql
BEGIN;
UPDATE apprenants SET email = 'amina-modifiee@example.test' WHERE id = 1;
-- Ne validez pas immédiatement; observez la session depuis la session B.
~~~

Dans la session B, exécutez :

~~~sql
UPDATE apprenants SET email = 'autre-valeur@example.test' WHERE id = 1;
~~~

La session B attend normalement que le verrou de la session A soit libéré. Revenez à la session A et exécutez COMMIT ou ROLLBACK. La session B poursuit alors son travail. Cet exercice permet de comprendre qu’une ligne affichée comme « requête lente » peut en réalité attendre une autre transaction. Réinitialisez les valeurs après l’exercice et ne laissez pas les transactions ouvertes.

## 15. Outils de supervision et commandes prudentes

Les vues système diffèrent d’un SGBD à l’autre. Dans PostgreSQL, pg_stat_activity décrit les sessions; pg_stat_database fournit des statistiques globales par base; pg_stat_user_tables et les vues associées renseignent sur les tables; EXPLAIN permet d’observer le plan d’une requête. Dans MySQL, les vues Performance Schema et sys offrent des instruments d’analyse complémentaires. Utilisez la documentation correspondant exactement à la version installée avant d’adopter un script de supervision.

Les commandes administratives doivent être accompagnées de critères. Une action qui termine une session, supprime une table ou change une configuration peut avoir un effet irréversible ou interrompre des utilisateurs. Privilégiez d’abord les commandes de lecture. Si une action modifiante est nécessaire, évaluez le risque, vérifiez les droits, prévenez l’équipe responsable et vérifiez les effets après l’intervention.

La commande PostgreSQL suivante mesure la taille logique d’une base de test :

~~~sql
SELECT pg_size_pretty(pg_database_size(current_database())) AS taille_base;
~~~

Pour examiner un plan sans exécuter la requête, utilisez EXPLAIN. EXPLAIN ANALYZE exécute la requête et doit être choisi avec précaution, notamment si le SQL contient une modification. Pour un diagnostic de production, commencez par une requête de lecture sûre et reproduisez le cas sur un échantillon ou un environnement de test si nécessaire. Ne copiez pas un plan d’exécution sans enregistrer les paramètres et les statistiques au moment de sa collecte.

La surveillance doit être testée elle aussi. Faites un exercice de panne simulée sur un environnement de test et confirmez que l’alerte arrive à la bonne équipe, au bon niveau d’urgence et avec les informations nécessaires. Une métrique qui n’est consultée par personne, une alerte toujours ignorée ou un tableau de bord sans propriétaire ne constituent pas un dispositif opérationnel.

## 16. Cas pratique : les inscriptions sont lentes

Une équipe signale que l’inscription à une formation peut durer huit secondes à l’heure de pointe. La première réaction pourrait être d’augmenter la puissance de la base. Le DBA commence plutôt par tracer le flux : attente du pool, temps d’exécution SQL, attente de verrou, commit et délai réseau. L’observation révèle que plusieurs requêtes mettent à jour le même compteur de places, tandis qu’un rapport analytique lance une lecture lourde sur la table des inscriptions.

La première hypothèse est que la contention sur le compteur contribue à la latence. La deuxième est que le rapport augmente l’utilisation des ressources. Le DBA vérifie les sessions, les verrous, les plans et le profil temporel. Une analyse peut démontrer qu’un index manque pour le rapport; une autre peut montrer que le compteur central impose une sérialisation inhérente au modèle. Ce sont deux problèmes distincts qui peuvent requérir deux solutions différentes.

L’équipe ajoute un index ciblé après avoir comparé le plan avant et après, puis réduit la fréquence du rapport en utilisant une table de synthèse. Elle maintient la vérification atomique des places restantes et la contrainte d’unicité de l’inscription. Elle ne retire pas les contrôles d’intégrité pour accélérer le flux. Le résultat est mesuré avec le même jeu de charge, les mêmes paramètres et le même percentile de latence. La modification est déployée graduellement, surveillée, puis conservée seulement si elle améliore le comportement sans dégrader les écritures.

Le compte rendu d’incident contient le symptôme, l’impact, la chronologie, les données collectées, les hypothèses, les changements, le résultat mesuré et les actions préventives. Il ne se contente pas de dire « on a ajouté un index ». Un index qui améliore une requête peut augmenter l’espace disque et le coût d’écriture; son impact doit être observé après le déploiement.

## 17. Exercices avec corrigés

### Exercice 1 — Pool saturé

Une application a huit instances et ouvre jusqu’à 25 connexions par instance. Le serveur autorise 120 connexions utiles après réservation des sessions d’administration. Pourquoi cette configuration est-elle dangereuse et que faut-il mesurer avant de changer les limites?

**Correction.** La capacité théorique de 200 connexions applicatives dépasse la limite utile. Le résultat peut être une erreur à l’ouverture des connexions, ou une hausse de latence si l’application attend dans son propre pool. Il faut observer le nombre de sessions actives, le temps d’attente du pool, les transactions longues, le coût mémoire par session et la charge CPU. Il faut établir un budget de connexions pour toutes les applications, tâches de fond et opérateurs. Réduire la taille des pools peut améliorer la stabilité si le problème est une concurrence excessive; augmenter le nombre de connexions sans vérifier la capacité ne corrige pas le travail SQL qui prend trop longtemps.

### Exercice 2 — Une réplique suffit-elle comme sauvegarde?

Une réplique contient les mêmes données que le primaire. L’équipe propose de supprimer les sauvegardes pour réduire les coûts.

**Correction.** La proposition confond disponibilité et capacité de restauration. Une suppression erronée, un défaut logique ou une corruption répliquée peut affecter tous les nœuds. Une sauvegarde indépendante permet de revenir à un état antérieur selon sa fréquence et sa rétention. Le coût doit être comparé au coût d’une perte de données, et les sauvegardes doivent être testées et protégées contre la suppression accidentelle ou malveillante. Une réplique reste utile, mais elle couvre un autre ensemble de défaillances.

### Exercice 3 — Verrouillage après un déploiement

Après une nouvelle version, plusieurs requêtes restent en attente et une migration est toujours active. Quelles actions mener dans quel ordre?

**Correction.** Premièrement, confirmer les impacts utilisateurs, la durée et l’heure de début. Deuxièmement, identifier les sessions en attente et la transaction bloquante, puis établir si la migration effectue un travail attendu ou reste bloquée. Troisièmement, consulter le plan de déploiement et les propriétaires du changement. Quatrièmement, choisir une action qui réduit le risque : attendre si l’opération avance et reste dans le budget, arrêter proprement la migration si elle est sûre à annuler, ou terminer une session selon un protocole d’urgence. Enfin, vérifier le schéma, la cohérence métier et le taux d’erreur. Ne tue pas de sessions au hasard.

### Exercice 4 — Le CPU est élevé

Le CPU atteint 90 %, mais le nombre d’erreurs reste faible. Faut-il immédiatement redémarrer le serveur?

**Correction.** Non. Le CPU élevé est un signal, pas un diagnostic. Vérifiez sa durée, le taux de requêtes, les plans récemment modifiés, les tâches de fond, les attentes I/O, les connexions et la latence utilisateur. Un redémarrage peut supprimer des éléments diagnostiques, interrompre les transactions et ne rien corriger si la charge se reproduit. Il n’est justifié que par une procédure et un scénario établis, pas comme réaction automatique à un seuil isolé.

### Exercice 5 — Retour arrière

Une migration supprime une colonne obsolète. Une nouvelle version du code échoue et l’équipe souhaite revenir à l’ancienne version.

**Correction.** Le rollback applicatif seul ne suffit pas si l’ancienne version lit encore la colonne supprimée. La migration est destructive et son inverse n’est pas possible sans sauvegarde de la donnée. Une séquence expansion-contraction aurait d’abord retiré les lectures de l’ancienne colonne et vérifié qu’aucune version n’en dépend. Avant la suppression, l’équipe doit vérifier les consommateurs, conserver une sauvegarde ou une transformation de retour possible selon le besoin et définir la procédure de rétablissement.

## 18. Défi final : préparer une mise en production fiable

Vous administrez la base d’une plateforme de formation de 20 000 utilisateurs. Les inscriptions ne doivent jamais dépasser les capacités définies. Les résultats de quiz doivent être durables dès leur confirmation. Une panne ne doit pas faire perdre plus de cinq minutes de données et l’objectif de reprise est de 45 minutes. La base reçoit des écritures toute la journée et un rapport analytique lourd chaque heure. Proposez un plan couvrant les transactions, l’observabilité, la sauvegarde, la sécurité, les tests et le déploiement.

### Correction attendue

1. **Intégrité.** Définir une contrainte unique pour l’inscription par apprenant et formation, une clé étrangère vers les objets nécessaires et une opération transactionnelle qui ne décrémente la capacité que si une place reste disponible. Vérifier le nombre de lignes modifiées et annuler si la condition échoue. Ajouter des tests de concurrence qui tentent de réserver simultanément la dernière place.

2. **Durabilité.** Vérifier la configuration de commit, le stockage sous-jacent et les garanties proposées par le SGBD ou le service managé. Ne pas affaiblir la synchronisation sans décision explicite sur la perte de données acceptable. Documenter les limites exactes du RPO de cinq minutes.

3. **Reprise.** Choisir une sauvegarde compatible avec la reprise à un instant donné, ou un mécanisme équivalent pris en charge par la plateforme. Conserver les sauvegardes et les journaux requis sur un périmètre indépendant, vérifier leur intégrité et exécuter régulièrement une restauration complète dans un environnement isolé. Mesurer un RTO inférieur à 45 minutes avec marge et documenter le rôle de chaque intervenant.

4. **Performance.** Capturer des plans d’exécution pour les requêtes critiques, collecter les statistiques, surveiller les attentes, la latence par percentile et le retard de réplication. Séparer le rapport analytique des transactions critiques lorsque cela est justifié, et évaluer les répliques, agrégats pré-calculés ou exécutions décalées. Mesurer les index ajoutés sur les lectures, les écritures et l’espace disque.

5. **Sécurité.** Attribuer un compte d’exécution restreint à l’application, séparer les migrations et l’administration, gérer les secrets en dehors du code et auditer les privilèges. Classifier les données personnelles, minimiser les champs, appliquer une rétention définie et protéger les copies de sauvegarde.

6. **Déploiement.** Tester la migration sur une copie représentative. Définir les préconditions, la durée, le risque de verrouillage, les métriques de succès et le retour arrière. Utiliser des étapes compatibles entre l’ancienne et la nouvelle version lorsque la base est utilisée sans interruption. Prévoir une fenêtre de surveillance et un responsable de décision.

7. **Vérification opérationnelle.** Simuler la perte d’une instance, la restauration d’une sauvegarde, une saturation de connexions et un blocage de transaction. Pour chaque exercice, conserver les mesures et corriger les écarts avant la mise en production.

Le résultat attendu n’est pas une liste d’outils, mais un système d’exploitation cohérent : exigences mesurables, conception, instrumentation, procédures, responsabilités et preuves d’essais.

## 19. Liste de vérification du DBA

Avant une intervention, identifiez sans ambiguïté le serveur, la base, l’environnement et le compte utilisé. Confirmez l’objectif de l’opération, les autorisations nécessaires, les effets secondaires, le volume de données et les préconditions. Vérifiez la capacité disque et les limites de ressources. Assurez-vous de disposer d’une sauvegarde adaptée et d’un moyen de retour arrière ou, si l’opération est irréversible, d’une stratégie de reprise clairement assumée. Informez les équipes concernées lorsque l’impact le justifie.

Après l’intervention, vérifiez le code de sortie, les journaux, l’état du schéma, la cohérence des données et les métriques de service. Recherchez les erreurs nouvelles, les attentes, les retards de réplication et la croissance inattendue du stockage. Documentez le résultat, y compris les problèmes rencontrés. Un changement qui fonctionne une fois mais n’est pas reproductible ou observable reste un risque.

Une revue régulière doit contrôler les versions supportées, les correctifs, la capacité, les sauvegardes, les privilèges, les comptes inactifs, les index non utilisés, les transactions longues et les alertes. Chaque procédure opérationnelle doit avoir un propriétaire et une date de test. Le DBA doit également vérifier que les objectifs métiers sont encore pertinents : la croissance et les exigences changent, donc les paramètres et les exercices doivent évoluer eux aussi.

## 20. Synthèse et glossaire

Le SGBD transforme des requêtes en opérations coordonnées sur la mémoire, les index, les pages de données et les journaux. Le rôle du DBA est de préserver les propriétés attendues de ce système sous la charge réelle. Une performance acceptable n’est pas suffisante si les données ne peuvent pas être restaurées; une sauvegarde ne suffit pas si elle n’a jamais été testée; une réplique n’est pas une sauvegarde; un compte authentifié ne doit pas bénéficier automatiquement de droits d’administration; un plan d’exécution ne s’interprète pas sans connaître le contexte et les statistiques.

**ACID** décrit les garanties transactionnelles d’atomicité, cohérence, isolation et durabilité. **DBA** désigne l’administrateur de base de données. **MVCC** est un mécanisme de gestion de versions qui aide à coordonner les accès concurrents. **WAL** est le journal d’écriture préalable utilisé notamment par PostgreSQL. **RPO** décrit la perte de données maximale acceptable et **RTO** le temps maximal de reprise. **PITR** est la restauration à un instant donné. **Pool de connexions** signifie réutiliser un ensemble limité de connexions. **Deadlock** désigne un cycle d’attentes entre transactions. **Observabilité** associe métriques, journaux et traces pour expliquer les comportements. **Migration** est une évolution contrôlée du schéma ou des données.

## Ressources officielles pour approfondir

- PostgreSQL, surveillance et statistiques : https://www.postgresql.org/docs/current/monitoring.html
- PostgreSQL, explication des plans : https://www.postgresql.org/docs/current/using-explain.html
- PostgreSQL, sauvegarde et restauration : https://www.postgresql.org/docs/current/backup.html
- PostgreSQL, contrôle de concurrence : https://www.postgresql.org/docs/current/mvcc.html
- MySQL, InnoDB et architecture de stockage : https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html

Servez-vous de ces références pour confirmer les particularités de la version et du moteur utilisés dans votre environnement. Les concepts généraux se transfèrent d’un système à l’autre, mais les commandes d’administration et les garanties exactes ne sont jamais universelles.
