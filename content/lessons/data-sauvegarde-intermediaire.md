# Backup, PITR et restauration — Intermédiaire

> **Mise en contexte.** Une base Skill-Tree contient les comptes, les inscriptions, les résultats et la progression des apprenants. Une mise à jour applicative introduit un défaut et supprime une partie des inscriptions. La réplication fonctionne toujours : la suppression est propagée au serveur secondaire. Le dernier fichier de sauvegarde semble présent, mais l'équipe ignore s'il couvre les données utiles, si les journaux nécessaires ont été conservés et combien de temps il faudra pour rétablir le service. Cet incident révèle une distinction essentielle : créer une sauvegarde, pouvoir restaurer une base cohérente et remettre une application en service dans les délais attendus sont trois objectifs liés, mais différents. Ce cours apprend à concevoir, réaliser, tester et exploiter une stratégie de sauvegarde et de restauration plutôt qu'à simplement exécuter une commande d'export.

## 1. Objectifs pédagogiques

Ce cours approfondit les travaux d'administration de bases de données. Il couvre les sauvegardes logiques et physiques, la récupération ponctuelle (*Point-in-Time Recovery*, PITR), les journaux de transactions, les objectifs de reprise, la protection des copies de sauvegarde, le test des restaurations et les procédures de bascule vers un environnement de récupération. Les principes s'appliquent à de nombreux systèmes relationnels, mais les mécanismes précis diffèrent selon le moteur et la plateforme.

À la fin de cette leçon, vous devrez savoir :

- différencier sauvegarde, réplication, haute disponibilité, archivage et restauration ;
- définir ce qui doit être sauvegardé, avec quelle fréquence, quelle rétention et quelles protections ;
- distinguer une sauvegarde logique d'une sauvegarde physique ;
- comprendre les rôles des journaux de transactions, notamment WAL dans PostgreSQL et redo log/binlog dans MySQL ;
- expliquer le principe d'une restauration à un instant précis et identifier ses prérequis ;
- définir des objectifs RPO et RTO avec les propriétaires du service ;
- concevoir une politique de rétention et de séparation des copies ;
- vérifier l'intégrité, la complétude et la restaurabilité d'une sauvegarde ;
- restaurer une copie dans un environnement de laboratoire et valider les données obtenues ;
- rédiger un runbook de restauration et un compte rendu d'exercice ;
- comprendre les risques associés aux restaurations sur une instance existante ;
- distinguer une erreur de fichier, une incompatibilité de version, une clé de chiffrement absente et une chaîne de journaux incomplète ;
- appliquer des contrôles de sécurité, de confidentialité et de moindre privilège aux sauvegardes ;
- préparer un scénario de reprise sans confondre le démarrage de la base avec le rétablissement fonctionnel de l'application.

Ce cours utilise PostgreSQL et MySQL comme repères concrets. Les commandes présentées sont indicatives et doivent être adaptées aux versions, aux extensions, à la taille des données et à l'architecture de votre environnement. Une commande de laboratoire ne constitue pas automatiquement une procédure de production.

## 2. Vocabulaire et objectifs de reprise

### 2.1 Sauvegarde, restauration, réplication et archivage

Une **sauvegarde** est une copie de données ou d'éléments de base conservée afin de pouvoir récupérer un état antérieur. Elle peut être logique ou physique, complète ou partielle selon la stratégie. Elle doit être protégée contre les dommages, la suppression accidentelle et les accès non autorisés.

Une **restauration** est le processus qui utilise une ou plusieurs sauvegardes et, lorsque nécessaire, des journaux ou des métadonnées pour remettre les données dans un état cohérent. La restauration n'est terminée que lorsque les résultats attendus ont été vérifiés et que le service peut reprendre selon les critères convenus.

La **réplication** propage des changements d'un système vers un autre. Elle peut aider à la disponibilité ou à la lecture, mais elle ne remplace pas une sauvegarde indépendante. Une suppression accidentelle ou une corruption logique peut être répliquée. Un serveur secondaire qui contient le même état erroné n'est pas un retour à l'état antérieur.

La **haute disponibilité** vise à limiter l'interruption de service lors de pannes couvertes par l'architecture. Elle peut mobiliser plusieurs nœuds, des mécanismes de détection, une bascule et une réorientation des clients. Elle ne garantit pas la récupération d'une table supprimée plusieurs heures auparavant.

L'**archivage** conserve certaines informations sur une période prolongée pour des besoins métier, historiques ou réglementaires. Une archive n'est pas nécessairement conçue pour remettre rapidement le système complet en service. Les formats, les métadonnées, les clés de chiffrement et les logiciels nécessaires doivent cependant rester accessibles pendant toute la durée de conservation.

Ces notions correspondent à des objectifs différents. Un système de production peut avoir besoin des quatre : réplication pour la disponibilité, sauvegardes pour le retour à un état antérieur, archivage pour les obligations de conservation et restauration testée pour démontrer que la reprise fonctionne.

~~~mermaid
flowchart TD
    A["Service de données"] --> B["Sauvegarde"]
    A --> C["Réplication et haute disponibilité"]
    A --> D["Archivage"]
    B --> E["Restaurer un état sauvegardé"]
    C --> F["Réduire certaines interruptions"]
    D --> G["Conserver des données dans le temps"]
    E --> H["Validation fonctionnelle"]
    F --> H
    G --> I["Consultation ou récupération selon le besoin"]
~~~

### 2.2 RPO : perte de données maximale acceptable

Le RPO (*Recovery Point Objective*) décrit la perte de données maximale acceptable, exprimée comme une période avant l'incident. Si le RPO cible est de quinze minutes, la solution de sauvegarde et de journalisation doit permettre, pour le scénario considéré, de retrouver un état dont le décalage ne dépasse pas cette fenêtre. Cela ne signifie pas nécessairement que le système sauvegarde un fichier complet toutes les quinze minutes : une sauvegarde de base combinée à une chaîne continue de journaux peut offrir une granularité de récupération différente.

Le RPO doit être défini avec les propriétaires métier. Pour un journal de consultation, quelques minutes de perte peuvent éventuellement être tolérables. Pour des résultats d'examen, des opérations financières ou des validations importantes, la perte acceptable peut être bien plus faible. Le DBA et les équipes techniques doivent ensuite démontrer que la stratégie choisie répond au besoin.

### 2.3 RTO : durée cible du rétablissement

Le RTO (*Recovery Time Objective*) est la durée cible pour rétablir le service selon une définition convenue. Il faut préciser ce qui marque le rétablissement : serveur démarré, connexions acceptées, données restaurées, contrôles métier passés, ou utilisateurs capables d'accomplir les parcours essentiels. Si le RTO signifie que la base accepte une connexion mais que l'application n'arrive pas à lire les cours, l'objectif métier n'est pas satisfait.

Le RTO comprend plusieurs durées : détection et qualification de l'incident, décision, préparation de l'environnement, transfert ou lecture des sauvegardes, application des journaux, démarrage, vérification de cohérence, réorientation des clients et validation fonctionnelle. Pour les bases volumineuses, le temps de transfert et le débit de stockage peuvent dominer la restauration.

### 2.4 Exemple de matrice de service

| Service ou donnée | RPO de travail à valider | RTO de travail à valider | Vérification de réussite |
|---|---|---|---|
| Catalogue de cours | À définir avec le métier | À définir avec le métier | Cours visibles et relations cohérentes |
| Inscriptions et progression | À définir selon la tolérance à la perte | À définir selon l'impact utilisateur | Comptes et inscriptions retrouvés |
| Résultats d'examen | À définir selon le caractère critique | À définir avec les responsables | Scores et historiques contrôlés |
| Journaux techniques | Selon les besoins de diagnostic | Selon les besoins opérationnels | Journaux accessibles et protégés |

Ces valeurs ne doivent pas être copiées d'un exemple. Elles constituent des objectifs à négocier, documenter et tester. Les délais et pertes acceptables doivent correspondre à l'impact réel d'un incident, au coût de la solution et aux capacités de l'équipe.

~~~mermaid
flowchart LR
    A["Incident"] --> B["Dernier point de données récupérable"]
    B --> C["Écart temporel = mesure du RPO"]
    A --> D["Détection et décision"]
    D --> E["Restauration et contrôles"]
    E --> F["Service validé"]
    D --> G["Durée totale = mesure du RTO"]
~~~

~~~mermaid
flowchart TD
    A["Inventaire et criticité"] --> B["Définir RPO et RTO"]
    B --> C["Choisir méthode et fréquence"]
    C --> D["Protéger copies et clés"]
    D --> E["Conserver journaux si PITR requis"]
    E --> F["Surveiller jobs et rétention"]
    F --> G["Restaurer et vérifier régulièrement"]
    G --> H{"Objectifs atteints ?"}
    H -- "Non" --> B
    H -- "Oui" --> I["Documenter la preuve et recommencer selon calendrier"]
~~~

## 3. Définir la stratégie avant de choisir l'outil

Une politique de sauvegarde commence par les besoins et les scénarios de risque. Choisir une commande ou activer une fonction automatique avant de préciser le périmètre peut conduire à une copie qui ne répond pas au besoin. Il faut savoir quelles bases, quels schémas, quels rôles, quelles extensions, quels objets et quelles dépendances doivent être récupérés.

### 3.1 Inventaire du périmètre

Pour chaque base, documentez :

- le propriétaire métier et l'équipe responsable ;
- le moteur, la version et la topologie ;
- les tables et objets critiques ;
- les dépendances aux rôles, extensions, fonctions, procédures et configurations ;
- la taille actuelle, la croissance et les pics ;
- les besoins de reprise, de restauration partielle ou de restauration complète ;
- la sensibilité des données et les contraintes d'accès ;
- la rétention nécessaire et les obligations de conservation ;
- l'emplacement des copies et les personnes autorisées à lancer une restauration.

Une sauvegarde qui ne contient que les données peut ne pas suffire à reconstruire le service. Certains éléments, tels que les rôles, les paramètres, les extensions, les tâches planifiées et les secrets externes, peuvent devoir être documentés ou sauvegardés séparément. Cela varie selon le moteur, la méthode de sauvegarde et la plateforme managée.

### 3.2 Menaces à considérer

La stratégie doit au minimum envisager la panne matérielle, la défaillance d'un volume, une erreur humaine, un défaut applicatif, une migration incorrecte, une corruption logique, la perte d'un site, la compromission d'un compte d'administration, une attaque par rançongiciel et la suppression de copies par un acteur malveillant. Tous ces scénarios n'ont pas la même probabilité ni le même impact.

Une réplication peut réduire les conséquences de la panne d'un nœud tout en reproduisant une suppression logique. Une sauvegarde stockée uniquement sur le même volume que la base peut être perdue avec celui-ci. Une copie accessible avec le même compte admin peut être supprimée par la même compromission. Une stratégie résiliente utilise des couches complémentaires et limite le domaine de panne partagé.

### 3.3 Politique de rétention

La rétention détermine combien de temps chaque génération de sauvegarde reste disponible. Une politique simple pourrait conserver plusieurs copies récentes et quelques copies plus anciennes ; la durée réelle dépend du RPO, des besoins métier, du coût et des obligations de conservation. Un incident peut être découvert plusieurs jours après la cause initiale, d'où l'intérêt d'une rétention qui dépasse la durée moyenne de détection.

La rétention doit être vérifiée par un contrôle automatique et une revue périodique. Les règles de purge doivent tenir compte des chaînes de journaux dont dépendent les points de restauration. Supprimer une sauvegarde ou un segment de journal encore nécessaire peut invalider des possibilités de restauration. Ne construisez pas une purge qui ne connaît pas les dépendances de restauration.

### 3.4 Séparer les responsabilités

Les rôles de création, de suppression et de restauration des copies doivent être séparés et limités autant que possible. Les comptes de sauvegarde n'ont pas nécessairement besoin des mêmes droits qu'un compte de développement. Un utilisateur qui peut administrer l'instance ne devrait pas automatiquement pouvoir effacer toutes les copies conservées hors site. Une séparation des comptes et des systèmes de stockage réduit le risque d'une compromission unique qui détruit à la fois la base et ses sauvegardes.

## 4. Sauvegardes logiques et physiques

### 4.1 Sauvegarde logique

Une sauvegarde logique exporte des objets et des données vers un format pouvant représenter des instructions SQL ou des enregistrements exportés. Elle est utile pour déplacer des données entre environnements, sauvegarder certains objets, migrer entre versions ou restaurer une partie du périmètre selon l'outil.

Les avantages fréquents sont la portabilité relative et la possibilité de choisir certains objets. Les limites comprennent la durée d'export et de restauration, le traitement des dépendances, les versions de schéma, les gros volumes et la nécessité de reconstruire les index ou contraintes pendant l'import. La sauvegarde logique n'est pas une image physique instantanée dans tous les sens du terme ; sa cohérence dépend de l'outil et des options utilisées.

### 4.2 Sauvegarde physique

Une sauvegarde physique capture les fichiers et structures de stockage nécessaires au moteur, selon la méthode et les garanties de celui-ci. Elle est souvent adaptée aux grandes bases et peut être liée à une chaîne de journaux qui permet une récupération à un point précis. Elle peut cependant être liée à une version, une plateforme, un format ou une procédure de récupération spécifiques.

Certaines sauvegardes physiques doivent être prises par un mécanisme reconnu du moteur ou du fournisseur pour assurer la cohérence entre les fichiers et les journaux. Copier arbitrairement le répertoire de données d'un moteur actif ne constitue pas une procédure universellement sûre. Le stockage, les snapshots, les journaux et l'état de l'instance doivent être coordonnés selon la documentation.

### 4.3 Comparaison pragmatique

| Critère | Sauvegarde logique | Sauvegarde physique |
|---|---|---|
| But fréquent | Portabilité, export d'objets ou de données | Reprise à grande échelle et restauration du cluster selon la méthode |
| Portabilité | Souvent plus élevée, mais dépend du SQL et des versions | Souvent plus dépendante du moteur, de la version et de la plateforme |
| Temps de restauration | Peut être long lorsque l'import reconstruit les objets | Peut être plus adapté aux grandes bases, selon le stockage et la méthode |
| Restauration partielle | Possible selon l'outil et l'objet exporté | Possible selon la méthode, mais souvent plus spécialisée |
| Besoin de journaux | Pas toujours pour l'export logique ; dépend du besoin de cohérence | Peut faire partie d'une stratégie PITR à partir d'une sauvegarde de base |
| Vérification | Import d'essai et contrôles des objets et données | Restauration d'essai, validation du moteur et contrôles fonctionnels |

Aucune ligne de ce tableau ne dispense de consulter la documentation correspondant au moteur. Les termes « logique » et « physique » recouvrent des méthodes différentes selon les produits et les services managés.

## 5. Sauvegarde PostgreSQL : principes et commandes de base

PostgreSQL offre plusieurs méthodes de sauvegarde. Pour une sauvegarde logique, l'outil courant est pg_dump, qui exporte une base. pg_dumpall peut être utilisé pour exporter plusieurs objets globaux, notamment les rôles, selon l'usage. Pour les sauvegardes physiques et PITR, PostgreSQL s'appuie sur une sauvegarde de base compatible et sur l'archivage des segments WAL nécessaires.

### 5.1 Sauvegarde logique avec pg_dump

Exemple d'export au format custom :

~~~bash
pg_dump -h localhost -U lab_backup -d skilltree_lab -F c -f skilltree_lab.dump
~~~

Le format custom peut être restauré avec pg_restore et permet de choisir certains objets dans les cas pris en charge. Le compte doit avoir les droits nécessaires, et l'authentification doit utiliser un mécanisme protégé ; ne stockez pas un mot de passe en clair dans la commande, le script ou l'historique du terminal.

Pour un format SQL texte :

~~~bash
pg_dump -h localhost -U lab_backup -d skilltree_lab -F p -f skilltree_lab.sql
~~~

Le format texte peut être utile pour inspection et restauration avec un client SQL, mais il ne possède pas toutes les possibilités de sélection et de restauration offertes par les formats d'archive. Le choix doit être fait à partir du besoin de restauration, pas uniquement de la taille du fichier.

### 5.2 Sauvegarder les objets globaux

Une base peut dépendre de rôles, de tablespaces et d'autres objets globaux qui ne sont pas représentés par le seul dump de cette base. PostgreSQL dispose d'outils pour exporter les objets globaux, notamment pg_dumpall avec des options adaptées. Le mécanisme exact dépend de la façon dont vous gérez les rôles et l'infrastructure.

Une sauvegarde logique d'une base peut restaurer son contenu sans recréer automatiquement tous les rôles ou les privilèges globaux attendus si ces éléments ne sont pas couverts par votre plan. Documentez donc le schéma de droits et la méthode de restauration des objets nécessaires. Ne publiez jamais un dump contenant des informations sensibles dans un dépôt accessible sans autorisation.

### 5.3 Restaurer un dump custom avec pg_restore

Pour restaurer dans une base de laboratoire déjà créée et préparée, une commande indicative est :

~~~bash
pg_restore -h localhost -U lab_restore -d skilltree_restore --no-owner skilltree_lab.dump
~~~

La base cible doit exister, et la stratégie doit tenir compte des propriétaires, rôles, extensions et privilèges. L'option --no-owner peut être utile lorsque l'utilisateur cible n'a pas ou ne doit pas recréer les propriétaires d'origine, mais elle ne remplace pas l'analyse des permissions et de la sécurité. Les options exactes dépendent de l'objectif.

Il est souvent plus sûr de restaurer dans une base neuve de récupération que d'écraser immédiatement la base actuellement utilisée par l'application. Cela permet de comparer les volumes, de vérifier le schéma et les contraintes puis de décider du transfert. Toute restauration dans un environnement partagé exige une procédure spécifique et une validation des dépendances applicatives.

### 5.4 Vérifier la restauration PostgreSQL

Après la restauration, vérifiez les bases et schémas, les tables attendues, les comptages des objets critiques, les contraintes, les vues, les fonctions et les privilèges. Une commande pg_restore terminée sans erreur ne prouve pas que le service complet fonctionne. Certains avertissements peuvent signaler des objets non restaurés, des propriétaires absents ou des dépendances qui demandent une attention.

Un contrôle simple sur le jeu pédagogique :

~~~sql
SELECT COUNT(*) AS nombre_apprenants FROM apprenants;
SELECT COUNT(*) AS nombre_cours FROM cours;
SELECT COUNT(*) AS nombre_inscriptions FROM inscriptions;
~~~

Ces comptages sont utiles mais insuffisants à eux seuls. Comparez aussi les relations, les distributions, les clés, quelques valeurs métier connues et des parcours applicatifs. Pour une base critique, définissez des assertions et un plan de validation adaptés au métier.

## 6. Sauvegarde MySQL : principes et commandes de base

MySQL possède plusieurs méthodes de sauvegarde selon la taille, le moteur de stockage, les besoins de récupération et les outils disponibles. mysqldump est un outil logique courant. Pour une stratégie physique ou une sauvegarde cohérente de grands volumes, il faut utiliser les outils et mécanismes adaptés à la version de MySQL, au moteur InnoDB et à la plateforme.

### 6.1 Sauvegarde logique avec mysqldump

Exemple pédagogique pour exporter une base :

~~~bash
mysqldump -h 127.0.0.1 -u lab_backup -p skilltree_lab > skilltree_lab.sql
~~~

Le client demande le mot de passe de façon interactive avec -p. Dans un environnement automatisé, choisissez un mécanisme de secrets approprié et évitez les valeurs sensibles dans les arguments, les logs et le dépôt. Vérifiez les options qui déterminent la cohérence transactionnelle, les routines, les événements, les triggers et les objets inclus.

Pour une base utilisant InnoDB, la stratégie de cohérence d'un dump doit tenir compte des transactions et du moteur. Un export effectué pendant que les données changent doit utiliser des options adaptées à un instant cohérent, selon les tables et les objets impliqués. Les options utiles varient avec les besoins et la version ; l'équipe doit noter précisément celles qu'elle utilise.

### 6.2 Restaurer un dump MySQL dans un environnement isolé

Une méthode courante consiste à créer une base de récupération puis à importer le fichier SQL avec le client :

~~~bash
mysql -h 127.0.0.1 -u lab_restore -p skilltree_restore < skilltree_lab.sql
~~~

Cette commande suppose que la base skilltree_restore existe et que le compte dispose de privilèges suffisants. Un import peut échouer à cause d'une table, d'un trigger, d'un utilisateur, d'une collation ou d'une syntaxe qui diffère selon le serveur. Vérifiez le code de retour, les logs du client et l'état de la base ; après une erreur partielle, ne supposez pas que tout a été restauré ou qu'aucune donnée n'a changé.

Une restauration d'essai doit être réalisée dans une base ou une instance isolée. Contrôlez les contraintes, les vues, les routines, les triggers et les privilèges requis par le service. Si le dump ne contient pas certains objets ou utilisateurs, suivez la procédure documentée pour les recréer avec les droits minimums.

### 6.3 Sauvegarde cohérente et options

Les options d'un outil de dump ne doivent pas être choisies au hasard. Pour une base InnoDB, les choix d'isolation et de lecture cohérente peuvent déterminer si les données exportées représentent un état cohérent. Les tables utilisant d'autres moteurs de stockage peuvent offrir des garanties différentes. Les routines, événements, triggers et utilisateurs exigent aussi des choix explicites.

La stratégie doit décrire le périmètre exact : base unique, plusieurs bases, événements, routines, objets globaux ou seules données. Les outils de restauration doivent être compatibles avec le format exporté. Conservez la version des outils, les options importantes et le résultat de l'exercice de restauration.

## 7. PITR : restauration à un instant précis

Le *Point-in-Time Recovery* (PITR) permet de retrouver un état autour d'un instant souhaité entre une sauvegarde de base et un point ultérieur couvert par une chaîne de journaux suffisante. Cela peut servir à récupérer des données juste avant une suppression accidentelle, une migration défectueuse ou un défaut applicatif qui a modifié les données. Les mécanismes diffèrent selon le moteur.

La PITR ne signifie pas que toutes les bases possèdent automatiquement un historique complet. Il faut disposer d'une sauvegarde de base valide, conserver les journaux nécessaires, garantir leur continuité et connaître le point cible. Si des segments de journal ont été perdus, l'intervalle de récupération peut être interrompu. Les limites et points de cohérence doivent être documentés.

### 7.1 Principe avec journalisation

~~~mermaid
flowchart LR
    A["Sauvegarde de base"] --> B["Journaux conservés"]
    B --> C["Modifications successives"]
    C --> D["Incident ou erreur métier"]
    D --> E["Choisir l'instant cible"]
    E --> F["Restaurer la base de départ"]
    F --> G["Rejouer les journaux jusqu'au point cible"]
    G --> H["Valider l'état récupéré"]
~~~

La sauvegarde fournit un état initial et les journaux rejouent les modifications nécessaires à avancer jusqu'au point voulu, selon les garanties du moteur. Le point d'arrêt doit être choisi avec soin. Il peut s'agir d'une heure avant la commande erronée, d'un point de restauration nommé, d'une transaction identifiée ou d'un autre repère pris en charge.

### 7.2 Déterminer l'instant cible

Le moment de l'incident n'est pas toujours le moment exact où les données sont devenues incorrectes. Une tâche planifiée peut avoir commencé plus tôt ; un défaut peut avoir modifié progressivement plusieurs tables ; une suppression peut être constatée longtemps après son exécution. Il faut consulter les journaux, les événements applicatifs, les audits et les témoignages pour identifier une fenêtre plausible.

Lors d'un incident, préserver les preuves peut compter autant que la restauration. Évitez de faire des changements improvisés sur la base endommagée. Documentez l'heure et le fuseau utilisé, l'identité des opérations, l'étendue des données affectées et les critères de validation. Si le point cible est incertain, il peut être utile de restaurer plusieurs candidats dans des environnements isolés et de les comparer.

~~~mermaid
sequenceDiagram
    participant DBA as DBA
    participant Base as PostgreSQL
    participant Archive as Archive WAL
    DBA->>Base: Lancer une sauvegarde de base compatible
    Base-->>DBA: Référence de sauvegarde et métadonnées
    Base->>Archive: Archiver les segments WAL terminés
    Archive-->>DBA: État d'archivage à surveiller
    Note over DBA,Archive: Sauvegarde et chaîne de journaux doivent rester compatibles
~~~

## 8. PITR PostgreSQL avec WAL et archivage

PostgreSQL utilise le Write-Ahead Log (WAL). Une stratégie PITR physique nécessite une sauvegarde de base obtenue par une méthode compatible et la conservation continue des segments WAL qui permettent de rejouer les changements nécessaires après cette sauvegarde. Les paramètres et procédures exacts doivent suivre la documentation de la version.

L'archivage WAL envoie les segments terminés vers un emplacement configuré. La chaîne doit être complète et protégée. Il faut superviser les échecs d'archivage, l'espace local occupé et l'état du stockage d'archive. Une archive en retard ou un répertoire plein peut compromettre la stratégie de récupération ou faire grossir le stockage des journaux.

### 8.1 Sauvegarde de base

PostgreSQL propose des méthodes comme pg_basebackup pour produire une sauvegarde physique de base selon les options et l'architecture retenues. Exemple indicatif :

~~~bash
pg_basebackup -h localhost -U backup_replication -D /srv/backups/pg_basebackup -Fp -Xs -P
~~~

Cette commande suppose un compte et une configuration appropriés, ainsi qu'un répertoire de destination préparé et protégé. Les options doivent être vérifiées pour la version, le type de sauvegarde et la méthode d'archivage. L'exemple ne suffit pas à configurer une chaîne PITR complète ; il illustre le rôle d'une sauvegarde physique de base.

Les droits nécessaires à une sauvegarde physique peuvent être plus sensibles que ceux d'un dump logique. Créez un compte dédié selon la documentation, limitez son accès réseau et ne réutilisez pas des identifiants de développement. Les copies doivent être protégées contre les utilisateurs non autorisés, notamment parce qu'elles contiennent une grande partie ou la totalité des données.

### 8.2 Configuration d'archivage WAL

Le principe consiste à configurer l'archivage dans le moteur, en définissant la méthode et la destination selon la version. La configuration exacte n'est pas donnée comme une recette universelle, car elle dépend du système de fichiers, de l'outil d'archivage, des mécanismes de chiffrement, des autorisations et du mode de déploiement.

Le mécanisme d'archivage doit être idempotent ou traiter proprement le cas où un segment existe déjà, éviter l'écrasement silencieux de données nécessaires et signaler les échecs. Un script d'archivage qui renvoie toujours un succès alors que la copie n'a pas été écrite donne une fausse confiance. Les journaux archivés doivent être vérifiés à partir de métriques, de logs et d'exercices de récupération.

### 8.3 Restaurer à un point cible

Une procédure générale PostgreSQL de PITR comprend :
1. mettre à l'abri l'instance touchée et préserver les preuves utiles ;
2. sélectionner une sauvegarde de base valide antérieure au point cible ;
3. restaurer cette sauvegarde dans un environnement préparé ;
4. configurer les paramètres de récupération et l'accès à la chaîne de WAL ;
5. indiquer le point cible selon la syntaxe prise en charge par la version ;
6. démarrer la récupération et surveiller les logs ;
7. valider l'état et arrêter au point prévu ;
8. effectuer les contrôles de cohérence et de métier ;
9. décider de la façon de réintégrer les données récupérées dans le service.

PostgreSQL a modifié certains paramètres de configuration de récupération au fil des versions. Utilisez les paramètres documentés pour la version en service et évitez les instructions copiées d'un guide ancien sans validation. Un test PITR doit faire partie du plan de restauration périodique.

~~~mermaid
sequenceDiagram
    participant DBA as DBA
    participant MySQL as MySQL
    participant Binlog as Stockage binlog
    DBA->>MySQL: Prendre une sauvegarde cohérente
    MySQL-->>DBA: Sauvegarde de base
    MySQL->>Binlog: Conserver les événements binlog
    DBA->>Binlog: Sélectionner la chaîne nécessaire au point cible
    Note over DBA,Binlog: Le rejeu s'arrête avant l'opération erronée
~~~

## 9. PITR MySQL avec journaux binaires

MySQL utilise notamment le binary log (binlog) pour enregistrer des événements de modification selon la configuration. Une stratégie de récupération ponctuelle s'appuie sur une sauvegarde de base cohérente et les journaux binaires nécessaires à rejouer les changements jusqu'au point cible. Les mécanismes exacts varient selon le moteur, la version, le format de journal et l'outil de sauvegarde.

Le binlog peut également servir à la réplication et à d'autres usages opérationnels, mais ses objectifs doivent être compris. Il est nécessaire de conserver la chaîne de journaux et de connaître le point où s'arrêter. Une sauvegarde MySQL sans les journaux nécessaires ne permet pas nécessairement de retrouver chaque instant après sa création.

### 9.1 Conserver les journaux nécessaires

La configuration du binary logging, sa rétention et son archivage doivent être conçus pour couvrir la fenêtre de récupération prévue. Si la purge supprime un fichier binlog encore requis, la PITR ne peut plus rejouer cette partie de l'historique. La politique de purge doit tenir compte des sauvegardes et des restaurations en cours, pas simplement de l'âge de chaque fichier.

Surveillez le volume, la rotation des journaux, les erreurs d'écriture, l'espace libre et les exigences de rétention. La bonne stratégie doit aussi sécuriser ces journaux : ils peuvent contenir des informations détaillées sur les modifications de données et être sensibles.

### 9.2 Exemple conceptuel de rejeu contrôlé

Après avoir restauré une sauvegarde complète dans un environnement de récupération, l'équipe identifie les fichiers binlog correspondant à l'intervalle à rejouer. Les outils MySQL tels que mysqlbinlog peuvent servir à examiner les événements ou à produire des instructions de rejeu avec des options adaptées. La forme exacte de la commande dépend des fichiers, du point de départ, du point d'arrêt et de la version.

Un rejeu doit être borné au point cible. Il est dangereux de rejouer l'intégralité de l'historique lorsque l'objectif est de s'arrêter avant une commande erronée. Le point d'arrêt doit être vérifié, par exemple à partir de la date, de la position du journal ou d'un autre repère reconnu par l'outil, selon le scénario.

Ne lancez pas un rejeu sur le primaire de production dans le cadre d'un essai. Restaurez dans une instance isolée, contrôlez les logs et vérifiez le nombre de lignes et l'état métier. Le but est de prouver une procédure et de mesurer son déroulement, pas de prendre un risque supplémentaire pendant un incident.

## 10. Points de cohérence, sauvegardes et journaux

Une restauration peut échouer même si la sauvegarde de base paraît valide, si les journaux ne sont pas continus ou ne correspondent pas à l'état de départ. À l'inverse, des journaux peuvent être disponibles mais inutilisables si la sauvegarde de base qui leur correspond est absente, corrompue ou incompatible. Il faut concevoir et surveiller l'ensemble de la chaîne.

Une stratégie PITR doit répondre aux questions :
- quelles sauvegardes de base peuvent servir de point de départ ?
- quelle séquence de journaux est nécessaire après chacune ?
- les segments sont-ils archivés, complets et lisibles ?
- le temps de conservation couvre-t-il le délai possible de détection ?
- comment sait-on qu'un segment manque ?
- qui peut empêcher ou corriger la purge de journaux ?
- comment restaurer et rejouer dans un environnement vierge ?
- comment définir le point cible sans ambiguïté ?
- quelle validation confirme que le résultat est cohérent ?

Les noms de fichiers ne suffisent pas comme preuve de continuité. Utilisez les métadonnées et les outils du moteur, les journaux d'archivage et un test de récupération réel pour valider la chaîne. Une alerte d'archivage doit être actionnable avant que le problème ne rende les objectifs de reprise impossibles à tenir.

## 11. Sécurité des sauvegardes

Les sauvegardes sont souvent aussi sensibles que la base en production, voire plus faciles à exploiter parce qu'elles peuvent contenir un grand nombre de tables et d'objets dans un seul fichier. Le contrôle d'accès et la protection des copies font donc partie de l'architecture de sécurité, pas seulement de l'exploitation.

### 11.1 Chiffrement en transit et au repos

Les copies doivent être protégées pendant leur transfert et dans leur stockage selon le risque. Le chiffrement au repos peut être assuré par le stockage, l'outil de sauvegarde ou une couche de chiffrement dédiée ; il faut connaître la frontière de protection réelle. Si le chiffrement dépend d'une clé externe, la récupération exige que la clé soit disponible et que son accès soit maintenu pendant la durée de rétention.

Une sauvegarde chiffrée dont la clé a été perdue n'est pas restaurable. Une clé conservée uniquement dans le même compte compromis que les copies peut être supprimée avec elles. La stratégie de gestion des clés, de contrôle d'accès, de rotation et de récupération doit donc être testée en même temps que celle des données.

### 11.2 Copie hors du domaine de panne

Conserver la seule sauvegarde sur le même volume que la base ne protège pas contre la perte de ce volume. Conserver toutes les copies avec le même compte administrateur peut ne pas protéger contre la compromission de ce compte. Une stratégie robuste sépare les copies du système principal, limite qui peut les supprimer et utilise les options de rétention ou d'immutabilité appropriées lorsque le service le permet.

L'expression « copie hors site » ne garantit pas à elle seule une protection suffisante. Le site distant peut être connecté aux mêmes identifiants, aux mêmes politiques de suppression ou au même environnement compromis. Examinez les chemins d'accès, les comptes, les clés, les contrôles de suppression et les procédures de récupération.

### 11.3 Confidentialité et minimisation

Un dump de base peut contenir des informations personnelles, des emails, des résultats, des rôles et des données historiques. L'accès doit être limité au besoin opérationnel. L'environnement de restauration doit posséder des permissions adaptées et ne pas exposer accidentellement des données réelles à des équipes qui ne devraient pas y accéder.

Pour des tests de développement, privilégiez des données synthétiques ou une anonymisation approuvée et vérifiée. Une copie restaurée reste une copie des données source ; elle ne devient pas non sensible parce qu'elle est utilisée en test. Les règles de conservation et de suppression doivent couvrir les sauvegardes et leurs réplicats.

## 12. Contrôles d'intégrité et preuve de restaurabilité

Un job de sauvegarde terminé avec succès prouve au mieux que le processus a atteint son état déclaré de succès. Il ne prouve pas nécessairement que le fichier est complet, que la clé est disponible, que le bon périmètre a été exporté ni que l'application fonctionnera après restauration. Le contrôle doit être proportionné au risque et à la criticité.

### 12.1 Vérification du fichier

La présence, la taille, l'horodatage et, selon les outils, une somme de contrôle peuvent détecter certains problèmes de copie ou de stockage. Une taille plausible ne prouve pas la validité interne d'une archive. Un hash calculé au moment de la sauvegarde puis comparé après transfert permet de vérifier que les octets correspondent, mais ne prouve pas que le contenu est restaurable.

Les outils peuvent fournir leurs propres vérifications de contenu et de métadonnées. Utilisez-les selon la méthode de sauvegarde, puis réalisez une restauration d'essai. Le meilleur contrôle reste une procédure de récupération qui parvient à reconstruire la base et à passer les assertions prévues.

### 12.2 Tests de validation après restauration

La validation doit être définie avant l'exercice. Elle peut inclure :
- existence des bases, schémas, tables, vues, fonctions, procédures et triggers essentiels ;
- présence des rôles et privilèges requis ;
- comptage des tables critiques et comparaison avec les références disponibles ;
- vérification des relations et de l'intégrité référentielle ;
- contrôle de distributions ou de périodes de données ;
- lecture d'échantillons de valeurs connues ;
- requêtes métier critiques ;
- démarrage de l'application dans un environnement isolé ;
- test de connexion, de lecture, d'écriture et du parcours utilisateur essentiel ;
- mesure du temps obtenu et comparaison au RTO.

Un simple comptage des lignes ne détecte pas toutes les corruptions logiques. Une table peut contenir le nombre attendu de lignes et relier des clés aux mauvais objets. Les contrôles doivent refléter les invariants métier connus et utiliser plusieurs formes de preuves.

### 12.3 Contrôler le RPO et le RTO réels

Le RPO observé est établi à partir du dernier état connu valide ou du point de récupération final comparé à l'instant de l'incident selon la définition adoptée. Le RTO mesuré commence et se termine selon des événements précisément définis. Si le chronomètre commence uniquement quand l'opérateur démarre la restauration, il ignore la détection et la décision ; il faut préciser ce choix dans le compte rendu.

Ne promettez pas un RTO sur la seule base du débit théorique de téléchargement. Une restauration peut inclure la décompression, la reconstruction des index, le rejeu de journaux, la reprise des connexions et des contrôles fonctionnels. Mesurez toute la séquence et identifiez les étapes dominantes.

~~~mermaid
flowchart TD
    A["Job de sauvegarde réussi"] --> B["Contrôle fichier et métadonnées"]
    B --> C["Restauration d'essai isolée"]
    C --> D["Contrôles techniques"]
    D --> E["Tests métier et application"]
    E --> F{"RPO et RTO conformes ?"}
    F -- "Non" --> G["Analyser les écarts et améliorer"]
    G --> A
    F -- "Oui" --> H["Consigner la preuve et la prochaine échéance"]
~~~

## 13. Planifier les exercices de restauration

Un exercice de restauration doit avoir un propriétaire, un scénario, un périmètre, des préconditions, un point de reprise cible, des critères de réussite et une procédure de nettoyage. Il ne doit pas se réduire à vérifier que le fichier existe ou qu'un outil accepte le format.

### 13.1 Fréquence fondée sur le risque

La fréquence des exercices dépend de la criticité du service, de la fréquence des changements, du volume des données, de la complexité des dépendances et des objectifs de reprise. Un système critique doit être testé plus fréquemment et après certains changements majeurs. Le calendrier doit être documenté et réellement respecté.

Un test peut restaurer une sauvegarde complète périodiquement, puis un test plus complet peut valider les journaux et le PITR. Un service managé peut fournir des outils spécifiques pour restaurer une copie ou créer un point de récupération temporaire, mais la procédure complète de validation applicative reste nécessaire.

### 13.2 Types d'exercice

- **Restauration logique** : importer un dump dans une base propre, vérifier les objets et les données.
- **Restauration physique** : récupérer les fichiers ou la base à partir d'une sauvegarde physique compatible.
- **PITR** : restaurer une sauvegarde de base puis rejouer les journaux jusqu'à un point sélectionné.
- **Récupération après suppression logique** : trouver un point cible antérieur à l'opération destructive et valider les données restaurées.
- **Reprise d'une instance ou d'un site** : confirmer que l'environnement de secours et les dépendances permettent le service.
- **Test des clés** : vérifier que les clés de chiffrement et les autorisations nécessaires sont disponibles selon le processus approuvé.

### 13.3 Préserver l'environnement source

Restaurez d'abord dans une instance ou base de récupération distincte lorsque cela convient au scénario. Évitez d'écraser la seule copie encore exploitable avant d'avoir sécurisé les données et documenté la décision. En cas d'incident réel, préservez les journaux nécessaires à l'analyse et coordonnez les opérations avec les responsables du service.

Il faut aussi éviter les conflits d'identité réseau. Une base restaurée peut se présenter avec le même nom, la même adresse ou les mêmes comptes que l'instance d'origine. Si l'application ou les tâches planifiées se connectent automatiquement à cette copie, elles risquent de modifier l'environnement de récupération de façon imprévue. Isolez la restauration et désactivez les intégrations actives lorsque cela est nécessaire et autorisé.

~~~mermaid
flowchart TD
    A["Détecter et qualifier l'incident"] --> B["Préserver les preuves et choisir le point cible"]
    B --> C{"Sauvegarde et journaux disponibles ?"}
    C -- "Non" --> D["Déterminer le dernier point récupérable et escalader"]
    C -- "Oui" --> E["Restaurer sur une cible isolée"]
    E --> F["Contrôles techniques et métier"]
    F --> G{"Critères passés ?"}
    G -- "Non" --> H["Analyser l'écart, ne pas basculer"]
    G -- "Oui" --> I["Décision de reprise et surveillance"]
    I --> J["Compte rendu et actions correctives"]
~~~

## 14. Runbook de restauration

Un runbook décrit pas à pas la restauration pour une situation précise. Il doit être assez clair pour être suivi par une personne habilitée même sous pression, tout en laissant la place aux décisions qui nécessitent un jugement. Les commandes doivent être testées sur la version exacte et les paramètres doivent être gérés par un mécanisme sécurisé.

### 14.1 Avant l'incident

Le runbook doit indiquer les propriétaires, les contacts, le périmètre, les outils, les prérequis, l'accès aux copies, la procédure de validation des clés, les destinations possibles et les critères de décision. Il doit contenir des liens vers la documentation de version et les commandes propres à l'environnement. Les secrets ne doivent pas apparaître dans le document.

### 14.2 Pendant l'incident

Une séquence de haut niveau :
1. confirmer l'incident et l'étendue de l'impact ;
2. enregistrer l'heure, le fuseau et les preuves connues ;
3. empêcher toute aggravation si l'action est autorisée et sûre ;
4. identifier le point cible et la méthode de récupération ;
5. vérifier l'existence de la sauvegarde et des journaux nécessaires ;
6. préparer une cible de restauration sûre ;
7. lancer la restauration avec la procédure validée ;
8. surveiller les logs, l'espace disque, les erreurs et la progression ;
9. effectuer les contrôles techniques et métier ;
10. faire approuver la bascule ou le retour du service selon le processus ;
11. surveiller les premiers parcours et documenter le rétablissement.

### 14.3 Après l'incident

Le compte rendu doit mentionner la chronologie, le point restauré, le RPO mesuré, le RTO mesuré, les données éventuellement perdues, les contrôles passés et échoués, les décisions, les effets sur les utilisateurs et les actions de prévention. Les actions doivent posséder un propriétaire, une date cible et une preuve de clôture.

Un échec de restauration n'est pas un détail à cacher. Il doit déclencher une analyse sur les causes et la mise à jour du runbook, des alertes, de la rétention ou de la chaîne de journaux. La confiance dans la reprise vient de résultats mesurés et de procédures corrigées, pas de déclarations.

## 15. Atelier pratique : restaurer un dump dans un environnement isolé

### Mission

Vous êtes chargé de prouver qu'une sauvegarde logique de la base de laboratoire Skill-Tree peut être restaurée dans une cible neuve, que les objets attendus existent et que les requêtes métier essentielles répondent correctement. L'objectif de cet atelier n'est pas de toucher à une base partagée : utilisez une base dédiée et des données fictives.

### Étape 1 — Préconditions

- Vous disposez d'une base source de laboratoire.
- Le compte de sauvegarde possède seulement les droits nécessaires.
- Le compte de restauration est distinct et limité à la cible.
- Le répertoire et les fichiers sont protégés par des permissions appropriées.
- L'espace disque est suffisant.
- Les noms de fichiers ne contiennent pas de secret.
- La procédure de réinitialisation est documentée.
- Les critères de validation sont écrits avant de commencer.

Consignez le moteur et sa version, la version des outils, la date et la méthode de sauvegarde. Pour un test de PITR, documentez en plus la sauvegarde de base, les journaux requis et le point cible prévu.

### Étape 2 — Créer une sauvegarde PostgreSQL

Dans un environnement PostgreSQL où la base de laboratoire existe, exécutez l'export logique :

~~~bash
pg_dump -h localhost -U lab_backup -d skilltree_lab -F c -f skilltree_lab.dump
~~~

Vérifiez le code de retour, la taille du fichier et les logs de la commande. Si l'outil signale des erreurs ou des objets non couverts, arrêtez l'exercice et documentez-les. Ne concluez pas à la validité du dump uniquement parce que le fichier existe.

### Étape 3 — Restaurer dans une base neuve

Créez une base de récupération, puis restaurez le dump à l'aide d'un compte adapté :

~~~bash
pg_restore -h localhost -U lab_restore -d skilltree_restore --no-owner skilltree_lab.dump
~~~

Les étapes de création de la cible et de préparation des rôles doivent suivre la procédure correspondant à votre environnement. Les options présentées sont indicatives ; examinez le comportement des propriétaires et privilèges avant l'import. N'utilisez pas cette commande comme procédure universelle pour écraser une base existante.

### Étape 4 — Valider le schéma et les données

Exécutez des requêtes qui vérifient les objets critiques, les volumes et certaines règles métier. Par exemple :

~~~sql
SELECT COUNT(*) AS nombre_apprenants FROM apprenants;
SELECT COUNT(*) AS nombre_cours FROM cours;
SELECT COUNT(*) AS nombre_inscriptions FROM inscriptions;
~~~

Comparez avec des références produites par la base source au moment de la sauvegarde. Si la source a continué à changer après la création de la copie, choisissez les attentes correspondant à l'instant sauvegardé, pas aux volumes actuels.

Testez une jointure métier qui relie apprenants, cours et inscriptions. Contrôlez qu'un apprenant connu possède les inscriptions attendues et que les contraintes sont présentes. Vérifiez également les vues, routines et droits requis par l'application. Si vous restaurez les objets sous un autre rôle, assurez-vous que le compte applicatif a les droits prévus.

### Étape 5 — Vérifier le parcours de l'application

Dans une cible isolée, lancez les contrôles nécessaires pour établir que l'application peut lire le catalogue et les inscriptions. Vérifiez les connexions, les droits, les variables d'environnement et les intégrations. Si des tâches planifiées peuvent écrire dans la base, désactivez-les dans la copie selon une procédure approuvée afin de ne pas provoquer de changements indésirables pendant les contrôles.

Le test doit documenter la différence entre une restauration technique et un service réellement fonctionnel. Une base peut démarrer correctement alors qu'une vue ou une routine attendue manque, que le compte d'application ne peut plus lire une table ou que la copie pointe encore vers un service externe de production.

### Étape 6 — Mesurer

Chronométrez les étapes selon la définition du RTO. Distinguez préparation, copie, restauration des objets, contrôle de cohérence et tests applicatifs. Notez la taille du dump, le volume restauré, la méthode, les ressources et les messages d'erreur. L'objectif est d'établir une mesure reproductible, pas une estimation théorique.

### Étape 7 — Nettoyer et consigner

Après validation, conservez uniquement les preuves autorisées et supprimez les copies temporaires selon la politique de laboratoire. Si la sauvegarde contient des données sensibles, traitez le fichier et la cible restaurée selon les règles applicables. Ne placez pas les dumps dans le dépôt Git. Rédigez un compte rendu avec la procédure, le résultat et les limites du test.

## 16. Atelier avancé : simuler un scénario PITR

Cet atelier avancé doit se dérouler dans un environnement jetable et avec une méthode adaptée au moteur. L'objectif est de comprendre les étapes et les preuves requises. N'essayez pas de créer un incident sur la base réelle de l'application.

### Étape 1 — Préparer une sauvegarde de base

Pour PostgreSQL, choisissez une méthode de sauvegarde physique compatible, comme pg_basebackup, et configurez l'archivage WAL selon la documentation de votre version. Pour MySQL, sélectionnez une sauvegarde de base cohérente et configurez la conservation des binary logs. La procédure exacte dépend des outils disponibles ; consignez la version et les paramètres.

Avant de simuler quoi que ce soit, vérifiez que les journaux sont effectivement archivés et que la stratégie permet de retrouver le point cible. Un test qui ne dispose pas de journaux suffisants n'est pas un exercice PITR valide.

### Étape 2 — Générer des changements connus

Utilisez des données fictives et effectuez quelques insertions ou mises à jour identifiables. Notez l'heure et le résultat attendu de chaque opération. La chronologie doit permettre de choisir un point avant un changement et un point après le changement pour démontrer que la restauration peut s'arrêter à l'état souhaité.

### Étape 3 — Créer un événement de référence

Dans le laboratoire uniquement, imaginez une mauvaise modification et marquez l'heure de son exécution. L'exercice vise à revenir à un état antérieur à cette opération. Ne supprimez pas des données réelles et ne rendez pas le test destructif sur une instance partagée. Conservez l'enregistrement de la chronologie pour comparer les différents points restaurés.

### Étape 4 — Restaurer sur une cible isolée

Utilisez une copie de récupération dédiée, le point de sauvegarde et la chaîne de journaux correspondant à la version du moteur. Pour PostgreSQL, configurez les options de récupération et le point cible selon la documentation de la version. Pour MySQL, restaurez la sauvegarde puis rejouez les binlogs jusqu'au repère choisi. Les paramètres et les commandes ne sont pas identiques entre les moteurs.

### Étape 5 — Vérifier le point récupéré

Contrôlez les lignes créées avant l'événement, celles créées après et l'état correspondant à l'événement erroné. Le résultat doit correspondre au point cible, ni plus tôt ni plus tard. Si un changement attendu manque ou si une modification ultérieure apparaît, vérifiez la chaîne de journaux et la définition du point cible.

### Étape 6 — Rédiger les conclusions

Consignez la sauvegarde de départ, les journaux nécessaires, l'instant visé, le temps total, les contrôles, les erreurs, les limites et les mesures correctives. Le test doit démontrer ce qui a été récupéré et comment vous l'avez vérifié. Un message « démarrage réussi » n'est pas la conclusion finale d'un exercice PITR.

## 17. Exercices d'application avec corrigés

### Exercice 1 — Sauvegarde ou réplication ?

Une base possède un réplicat en temps réel. Un utilisateur supprime accidentellement toutes les inscriptions d'un cours, et la suppression est immédiatement reproduite sur le secondaire. Pourquoi le réplicat ne suffit-il pas ?

**Corrigé.** La réplication propage les changements, y compris les suppressions logiques. Le réplicat reflète donc probablement la suppression. Il faut une sauvegarde indépendante et, si l'architecture le permet, des journaux pour retrouver un état avant l'opération. La restauration doit se faire dans un environnement contrôlé pour identifier les données à récupérer.

### Exercice 2 — Définir le RPO

Un service accepte au maximum dix minutes de perte de données. Que devez-vous démontrer avec la stratégie de sauvegarde ?

**Corrigé.** Pour les scénarios couverts, il faut démontrer que le point récupérable se situe dans la fenêtre définie, soit une perte temporelle maximale de dix minutes selon la définition validée. Il ne suffit pas de produire une sauvegarde complète toutes les dix minutes : la stratégie doit aussi tenir compte de la cohérence, des journaux, de leur disponibilité et du point final réellement restaurable.

### Exercice 3 — Définir le RTO

Une équipe déclare la restauration terminée dès que le moteur accepte une connexion. Quel est le problème ?

**Corrigé.** Cette étape ne prouve pas que le schéma, les données, les privilèges et les parcours applicatifs fonctionnent. Le RTO doit définir le retour au service selon des critères convenus. Les tests fonctionnels et le contrôle de cohérence peuvent faire partie du temps de reprise.

### Exercice 4 — Dump PostgreSQL disponible

Un fichier issu de pg_dump existe et sa taille paraît plausible. Peut-on déclarer la sauvegarde restaurable ?

**Corrigé.** Non. Vérifiez le résultat du job, les métadonnées et le contenu selon l'outil, puis restaurez dans un environnement d'essai. Contrôlez les objets, les contraintes, les données et les parcours métier essentiels. Une taille plausible ne démontre pas la validité de l'archive.

### Exercice 5 — Chaîne WAL incomplète

Une sauvegarde de base PostgreSQL a réussi, mais un segment WAL nécessaire à la période cible manque. Quelles sont les conséquences possibles ?

**Corrigé.** La récupération ne pourra pas nécessairement atteindre le point cible voulu, car la chaîne de journaux requise est incomplète. Il faut déterminer le dernier point récupérable, préserver les preuves, identifier le segment manquant si possible et corriger la surveillance et le stockage d'archives avant le prochain exercice.

### Exercice 6 — Binlogs purgés trop tôt

MySQL a une sauvegarde complète de la veille, mais les fichiers binlog couvrant la période nécessaire ont été purgés. Peut-on supposer qu'un PITR à la minute précédant l'incident reste possible ?

**Corrigé.** Non. Une PITR dépend de la sauvegarde de base et des journaux nécessaires entre celle-ci et le point cible. Si les journaux manquent, on ne peut pas simplement les recréer. Il faut identifier le point récupérable et corriger la politique de rétention.

### Exercice 7 — Restaurer sur la base courante

Lors d'un test, vous envisagez d'importer un dump dans la base courante de l'application. Quel est le risque ?

**Corrigé.** L'import peut entrer en conflit avec les objets existants, écraser des données, laisser une restauration partielle ou interrompre l'application. Une cible isolée est préférable pour les exercices. Une restauration en production nécessite une procédure contrôlée, un plan de communication, la sauvegarde des preuves et une stratégie de retour.

### Exercice 8 — Sauvegarde chiffrée, clé indisponible

Un fichier est intact mais la clé de déchiffrement n'est plus accessible. Quelle conclusion tirer ?

**Corrigé.** La copie peut être inutilisable en pratique. La stratégie doit sauvegarder et protéger la disponibilité des clés selon un processus autorisé, avec séparation des accès et test de récupération. Le chiffrement sans gestion de clés adaptée peut bloquer la restauration.

### Exercice 9 — Compter les lignes

Après restauration, les comptages des tables correspondent aux références. Est-ce une validation complète ?

**Corrigé.** Non. Il faut aussi vérifier les relations, les valeurs métier connues, les contraintes, les vues, les procédures, les droits et les parcours applicatifs. Des nombres de lignes identiques peuvent masquer des associations erronées ou des objets manquants.

### Exercice 10 — Sauvegarde logique ou physique

Vous devez restaurer rapidement une très grande base au sein du même moteur. Quelle méthode choisir sans autre analyse ?

**Corrigé.** Il ne faut pas trancher sans connaître la taille, le RTO, les outils et les contraintes de version. Une sauvegarde physique peut être plus adaptée aux grands volumes, tandis qu'un dump logique peut être utile pour certaines restaurations sélectives ou migrations. Testez la méthode en fonction du besoin réel.

### Exercice 11 — Copies nombreuses sur le même compte

L'équipe conserve cinq générations de sauvegarde dans un stockage partagé accessible à l'identité administrateur de la base. Est-ce une protection suffisante contre une compromission de ce compte ?

**Corrigé.** Pas nécessairement. L'acteur compromis pourrait peut-être supprimer ou chiffrer la base et les copies avec les mêmes privilèges. Séparez le domaine de sécurité, limitez les droits de suppression, appliquez les protections disponibles et testez la récupération des clés et des copies.

### Exercice 12 — PITR à l'instant erroné

Une restauration contient la modification accidentelle que l'équipe voulait éviter. Que devez-vous revoir ?

**Corrigé.** Vérifiez le point cible, l'heure et le fuseau, la définition du repère, la chaîne de journaux rejouée et les logs de récupération. Le temps de l'incident peut avoir été identifié incorrectement. Répétez l'essai dans une cible isolée avec un point cible explicitement documenté.

## 18. Défi final corrigé — préparer la reprise de Skill-Tree

### Mission

Vous devez remettre un plan de sauvegarde et de reprise pour une base applicative qui conserve comptes, catalogue, inscriptions et résultats. Les objectifs métier ne sont pas fournis : votre travail commence par identifier les questions à poser et à convertir en critères testables. Le livrable doit inclure la politique de sauvegarde, la protection des copies, la stratégie PITR adaptée au moteur, la procédure de restauration et le protocole de validation.

### Étape A — Inventorier les données et les dépendances

Documentez le moteur et la version, les bases et schémas, les objets critiques, les rôles et privilèges, les extensions et routines, les données sensibles, la taille et la croissance. Identifiez les dépendances externes et les tâches planifiées. Indiquez ce que la sauvegarde choisie couvre et ce qui nécessite une procédure complémentaire.

### Étape B — Définir les objectifs

Organisez une discussion avec les propriétaires métier pour fixer les RPO et RTO. Écrivez les événements de départ et d'arrivée pour le chronométrage, les scénarios couverts et les limites. Évitez de choisir une fréquence de sauvegarde uniquement sur la base d'une habitude. Le niveau de protection est une décision de risque et de coût.

### Étape C — Choisir la stratégie technique

Pour PostgreSQL, documentez la méthode de sauvegarde logique ou physique, l'archivage WAL si le PITR est requis, les lieux de stockage, les rôles et les commandes de vérification. Pour MySQL, documentez la méthode de sauvegarde, les exigences de cohérence, la rétention du binlog et les outils nécessaires à la restauration. Ne mélangez pas les instructions d'un moteur avec celles de l'autre.

### Étape D — Définir la rétention et la sécurité

Choisissez une rétention qui couvre la durée possible de détection d'un incident et les besoins réglementaires. Définissez les permissions, le chiffrement, la gestion des clés, le stockage séparé, les contrôles d'intégrité et les responsabilités de suppression. Prévoyez comment les copies et leurs clés restent récupérables au fil du temps.

### Étape E — Concevoir la restauration

Le runbook doit préciser les préconditions, le point cible, la sauvegarde de départ, les journaux nécessaires, la préparation de la cible, la restauration, les contrôles et les critères de décision. Les commandes exactes doivent être vérifiées dans un laboratoire sur la version ciblée. La procédure doit identifier comment éviter de connecter accidentellement les tâches de production à la base de récupération.

### Étape F — Définir les tests d'acceptation

Les tests devraient démontrer :
- que les fichiers et métadonnées attendus sont disponibles ;
- que la restauration technique réussit ;
- que les journaux requis permettent le point cible visé ;
- que les objets, contraintes et privilèges attendus existent ;
- que les données critiques correspondent aux références de l'instant récupéré ;
- que les parcours métier essentiels fonctionnent ;
- que les RPO et RTO observés satisfont les objectifs ;
- que les comptes et copies temporaires sont nettoyés ou conservés selon la politique.

### Étape G — Corrigé de référence

Un plan satisfaisant associe une sauvegarde de base adaptée, des journaux conservés si le PITR est requis, des copies protégées dans un domaine de panne approprié, des alertes sur les échecs d'archivage et la capacité, et des tests réguliers de restauration. Il distingue les copies indépendantes de la réplication et précise comment les points de reprise sont sélectionnés. Il documente les propriétaires, les permissions, la gestion des clés, les critères de validation et les résultats des exercices.

Un plan ne peut pas être jugé bon à partir du seul nombre de sauvegardes ou du statut vert d'un job. Il doit prouver que l'équipe peut retrouver le bon état des données dans les délais acceptés, sur une cible contrôlée et avec des preuves vérifiables. Si les exercices révèlent un dépassement de RTO ou un RPO non respecté, l'écart déclenche une mesure corrective avec un responsable.

## 19. Checklist opérationnelle

Avant de considérer la stratégie prête, vérifiez :

- Le périmètre, le propriétaire métier et les dépendances sont documentés.
- Le moteur, sa version et les méthodes de sauvegarde sont connus.
- Le RPO et le RTO sont validés et mesurables.
- Les sauvegardes logiques ou physiques couvrent les objets nécessaires.
- La chaîne WAL ou binlog est conservée si le PITR est requis.
- La rétention n'efface pas les journaux nécessaires à des points de reprise encore promis.
- Les erreurs d'archivage, la capacité et l'âge de la dernière sauvegarde sont surveillés.
- Les copies sont protégées par des permissions minimales et séparées du système principal.
- Le chiffrement et la disponibilité des clés sont testés.
- Les fichiers sont contrôlés, mais la restaurabilité est également démontrée par un essai.
- La restauration s'effectue d'abord sur une cible isolée lorsque c'est approprié.
- Les données, les contraintes, les privilèges et les objets sont vérifiés après restauration.
- Les parcours applicatifs essentiels sont inclus dans les tests.
- Les durées de restauration et les pertes temporelles observées sont consignées.
- Les procédures sont adaptées à la version réellement utilisée.
- Les secrets et dumps sensibles ne sont pas stockés dans le dépôt.
- Les conclusions, écarts et actions préventives possèdent des responsables et des échéances.

## 20. Synthèse finale

Une stratégie de sauvegarde est une capacité opérationnelle. Elle doit couvrir les bonnes données, utiliser une méthode cohérente, protéger les copies, conserver les journaux nécessaires et permettre une restauration vérifiée. Les sauvegardes logiques et physiques répondent à des besoins différents ; le choix dépend du volume, de la portabilité, du RTO, du besoin de restauration partielle et des capacités de l'équipe.

La PITR permet de récupérer un état jusqu'à un point cible lorsque la sauvegarde de base et la chaîne de journaux nécessaires sont disponibles et valides. PostgreSQL s'appuie sur une sauvegarde compatible et les segments WAL ; MySQL peut utiliser une sauvegarde cohérente et les binary logs. Les mécanismes, commandes et paramètres doivent être adaptés à la version et à la topologie. Une chaîne de journaux incomplète peut rendre un point de récupération inaccessible.

RPO et RTO sont des objectifs négociés, pas des garanties automatiques. La restauration doit être testée avec des critères qui couvrent les objets, les données, les relations, les droits et les parcours métier. Il faut mesurer le temps total, vérifier le point retrouvé et documenter les écarts. Un fichier présent ou un job terminé ne suffit pas à déclarer le système récupérable.

Enfin, la sécurité des copies et la gestion des clés sont aussi importantes que les données elles-mêmes. Les sauvegardes doivent être protégées contre une perte ou une compromission du domaine principal, et les restaurations doivent utiliser des comptes et des environnements contrôlés. Les procédures et les exercices produisent les preuves qui transforment une stratégie théorique en capacité de reprise.

## Références techniques

Consultez la documentation correspondant au moteur et à sa version. Les options, paramètres et procédures de récupération évoluent.

- PostgreSQL, sauvegarde et restauration : https://www.postgresql.org/docs/current/backup.html
- PostgreSQL, sauvegarde physique de base : https://www.postgresql.org/docs/current/app-pgbasebackup.html
- PostgreSQL, pg_dump : https://www.postgresql.org/docs/current/app-pgdump.html
- PostgreSQL, pg_restore : https://www.postgresql.org/docs/current/app-pgrestore.html
- PostgreSQL, archivage continu et PITR : https://www.postgresql.org/docs/current/continuous-archiving.html
- MySQL 8.4, stratégies de sauvegarde : https://dev.mysql.com/doc/refman/8.4/en/backup-strategy.html
- MySQL 8.4, mysqldump : https://dev.mysql.com/doc/refman/8.4/en/mysqldump.html
- MySQL 8.4, récupération à un instant précis : https://dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery.html
- MySQL 8.4, binary log : https://dev.mysql.com/doc/refman/8.4/en/binary-log.html

Ces références constituent le point de départ technique. Vérifiez les paramètres, les privilèges et la procédure de récupération dans un environnement de laboratoire avant toute utilisation opérationnelle.
