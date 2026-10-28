# Rôle du DBA et architecture SGBD — Intermédiaire

> **Mise en contexte.** Une application de formation commence avec quelques dizaines d'utilisateurs et une base simple. Quelques mois plus tard, des milliers de personnes consultent les cours, enregistrent leurs progrès et passent des évaluations. Une requête auparavant rapide se met à ralentir, une sauvegarde existe mais personne n'a vérifié qu'elle peut être restaurée, plusieurs développeurs possèdent des privilèges trop étendus et les équipes ne savent pas à qui signaler une saturation. C'est dans ce contexte que le rôle du DBA — administrateur de bases de données — devient central. Le DBA ne se contente pas de créer des tables ou d'exécuter des commandes : il contribue à garantir que les données restent disponibles, cohérentes, protégées, observables et récupérables pendant tout leur cycle de vie.

## 1. Objectifs et périmètre du cours

Ce cours prolonge les travaux pratiques SQL. Vous avez appris à définir des tables, des contraintes, des requêtes et des transactions ; vous allez maintenant examiner le système qui exécute ces requêtes et les responsabilités nécessaires pour exploiter une base durablement. Le point de vue change : il ne s'agit plus seulement de savoir écrire du SQL, mais de comprendre les composants, les risques et les décisions d'exploitation qui entourent ce SQL.

À la fin de cette leçon, vous serez capable de :

- distinguer le rôle du DBA de ceux du développeur, de l'ingénieur plateforme, de l'architecte et de l'équipe sécurité ;
- expliquer l'architecture logique et physique d'un SGBD relationnel ;
- décrire le parcours général d'une requête entre client, moteur SQL, optimiseur, exécuteur, mémoire et stockage ;
- expliquer pourquoi les transactions, le journal de transactions, les verrous et les mécanismes de récupération sont essentiels ;
- distinguer sauvegarde, réplication, haute disponibilité et reprise après sinistre ;
- définir des objectifs de reprise et des contrôles de restaurabilité ;
- organiser les comptes, les privilèges, les secrets et les responsabilités d'accès ;
- lire les indicateurs de base d'une instance et relier une saturation à des hypothèses vérifiables ;
- comprendre les principaux facteurs qui influencent la capacité et la performance ;
- préparer une modification ou une migration avec validation, stratégie de retour et communication ;
- construire une checklist d'exploitation et un tableau de bord adapté aux risques du service.

Le cours se concentre sur les principes communs aux systèmes relationnels, avec des exemples pouvant être adaptés à PostgreSQL ou MySQL. Les composants internes et les commandes d'administration ne sont pas identiques entre moteurs ni entre versions. Les exemples SQL et les commandes de client sont donc présentés comme des points de départ à vérifier dans la documentation officielle du moteur effectivement exploité.

## 2. Qu'est-ce qu'un DBA ?

DBA signifie Database Administrator, ou administrateur de bases de données. Selon l'organisation, le DBA peut être responsable d'une instance, d'un ensemble de bases, d'un service managé ou d'une plateforme distribuée. Dans une petite équipe, une personne peut prendre en charge une grande partie de ces activités. Dans une grande organisation, les responsabilités sont souvent partagées entre administration, ingénierie de fiabilité, sécurité, développement, réseau, stockage et équipes de données.

L'objectif opérationnel est de rendre le service de données conforme à des exigences définies : disponibilité, intégrité, sécurité, performance, capacité, coût et possibilité de reprise. Ces exigences sont liées. Par exemple, augmenter la conservation des journaux peut améliorer la capacité de restauration à un instant précis, mais augmenter les besoins en stockage. Accroître la réplication peut accélérer certaines stratégies de reprise, mais ne remplace pas une sauvegarde indépendante. Réduire les privilèges limite les effets d'une erreur, mais nécessite d'organiser les demandes de droits pour éviter de bloquer les opérations légitimes.

### 2.1 Responsabilités fréquentes

Les tâches courantes comprennent la préparation et la configuration des instances, la gestion des comptes et des privilèges, l'application de mises à jour, la surveillance de la santé du service, l'analyse des requêtes lentes, la gestion des index, la planification des sauvegardes, les tests de restauration, la gestion de la capacité et la coordination des changements de schéma.

Le DBA travaille avec les développeurs pour comprendre la charge et le modèle de données. Il collabore avec les équipes de sécurité pour appliquer le moindre privilège, protéger les connexions et assurer la traçabilité. Il collabore avec l'équipe plateforme pour dimensionner les ressources, superviser le réseau et préparer une stratégie de disponibilité. Il participe à la gestion des incidents et à l'analyse des causes après une panne.

Le DBA n'est pas nécessairement le seul responsable de toutes les données. Le propriétaire métier définit le sens des données, les règles de conservation et les usages autorisés. Le développeur connaît le comportement de l'application. L'équipe sécurité établit les politiques organisationnelles et réglementaires. Le DBA transforme ces exigences en configuration de base de données, en procédures et en contrôles qui peuvent être vérifiés.

### 2.2 DBA traditionnel, DBA de plateforme et service managé

Dans un environnement auto-hébergé, le DBA peut devoir gérer le système d'exploitation, le moteur, les disques, les mises à jour, les sauvegardes et la réplication. Dans un service de base de données managé, le fournisseur prend en charge certaines opérations matérielles et logicielles, mais l'équipe cliente reste généralement responsable du modèle, des droits, des requêtes, de la rétention métier, des tests de restauration et de la conception de la haute disponibilité. La répartition dépend du contrat de service.

Un service managé ne supprime donc pas le besoin d'administration ; il déplace certaines responsabilités. L'équipe doit savoir quelles tâches sont prises en charge par le fournisseur, quelles tâches restent à sa charge et comment les preuves sont disponibles. Par exemple, le fait qu'un fournisseur annonce des sauvegardes automatiques ne prouve pas que le bon point de restauration répondra aux besoins métier. Il faut connaître la durée de rétention, les options de restauration, les délais attendus et la procédure testée.

### 2.3 Responsabilités selon le cycle de vie

~~~mermaid
flowchart TD
    A["Conception"] --> B["Provisionnement"]
    B --> C["Sécurisation"]
    C --> D["Mise en service"]
    D --> E["Surveillance et optimisation"]
    E --> F["Sauvegarde et reprise"]
    E --> G["Changements et migrations"]
    F --> H["Exercices de restauration"]
    G --> E
    H --> E
    E --> I["Retrait contrôlé du service"]
~~~

L'administration couvre tout le cycle de vie, y compris le retrait. Une base que personne n'utilise encore peut conserver des données sensibles, des comptes valides et des sauvegardes coûteuses. La fermeture doit confirmer les dépendances, la conservation réglementaire, les besoins d'archivage et la suppression sécurisée des données lorsque cela est autorisé.

## 3. Architecture générale d'un SGBD

Un système de gestion de base de données (SGBD) est un logiciel qui permet de définir, stocker, interroger, modifier et protéger des données structurées. Pour raisonner sur son architecture, il est utile de distinguer plusieurs couches, même si leur implémentation varie d'un moteur à l'autre.

1. **Clients et applications** : ils envoient des requêtes au serveur au travers d'un pilote ou d'un protocole.
2. **Gestion des connexions et de l'authentification** : le serveur reçoit les connexions, identifie les comptes et contrôle les accès.
3. **Analyse et préparation SQL** : le moteur analyse la syntaxe et vérifie les objets et les types.
4. **Optimisation** : le moteur estime les plans d'exécution possibles selon les statistiques, les index et le coût attendu.
5. **Exécution** : le plan choisi lit, filtre, joint, trie ou modifie les données.
6. **Mémoire et caches** : des pages de données et des résultats intermédiaires peuvent être conservés en mémoire pour éviter des lectures répétées.
7. **Stockage et journaux** : les pages de données, métadonnées et journaux sont persistés selon les mécanismes du moteur.
8. **Contrôle transactionnel et récupération** : le moteur gère la concurrence, la visibilité des versions, les verrous ou autres mécanismes de synchronisation, et la récupération après incident.

~~~mermaid
flowchart LR
    A["Application"] --> B["Pilote / protocole"]
    B --> C["Connexions et authentification"]
    C --> D["Analyse et validation SQL"]
    D --> E["Optimiseur de requêtes"]
    E --> F["Plan d'exécution"]
    F --> G["Moteur transactionnel"]
    G <--> H["Mémoire / caches"]
    G <--> I["Stockage des données"]
    G --> J["Journal de récupération"]
~~~

Cette représentation est conceptuelle. Dans un moteur réel, les composants peuvent être organisés différemment, interagir en parallèle ou partager plusieurs sous-systèmes. L'objectif est d'identifier les responsabilités et les points d'observation possibles, pas de supposer que chaque moteur possède exactement les mêmes processus internes.

### 3.1 Architecture client-serveur

Dans l'architecture client-serveur, l'application cliente envoie des commandes à un serveur SQL. Le serveur possède les données et exécute les requêtes autorisées. Cette séparation permet à plusieurs applications de partager une source de données contrôlée, avec des permissions et des transactions coordonnées par le SGBD.

Une connexion réseau ajoute toutefois des sujets d'exploitation : résolution DNS, port, pare-feu, chiffrement, latence, limites de connexions, interruption du réseau et délais d'attente. Une erreur de connexion ne prouve pas que la base est en panne. Le problème peut se situer dans l'application, le DNS, le routage, le pare-feu, l'authentification ou la capacité du service à accepter de nouvelles sessions.

### 3.2 Connexions et pools de connexions

L'ouverture d'une connexion coûte du temps et des ressources. Une application web qui crée une nouvelle connexion pour chaque petite requête peut produire une quantité excessive de connexions simultanées, particulièrement lorsqu'elle fonctionne avec de nombreuses instances. Un pool de connexions réutilise un ensemble de connexions disponibles et limite le nombre de sessions simultanées.

Le pool doit être dimensionné à partir du budget de connexions et du profil de charge. Un pool trop petit peut créer une file d'attente côté application ; un pool trop grand peut épuiser les ressources du serveur ou augmenter la contention. Ajouter des connexions n'accélère pas automatiquement une base saturée. Il faut examiner le temps d'attente, le nombre de connexions actives, les requêtes en cours et les ressources consommées.

~~~mermaid
flowchart TD
    A["Requêtes HTTP concurrentes"] --> B["Pool de connexions applicatif"]
    B --> C{"Connexion disponible ?"}
    C -- "Oui" --> D["Exécuter la requête"]
    C -- "Non" --> E["Attendre dans la file ou appliquer un délai"]
    D --> F["Libérer la connexion"]
    F --> B
    E --> B
~~~

La connexion doit être rendue au pool même lorsqu'une requête échoue, et toute transaction ouverte doit être remise dans un état sûr avant la réutilisation. Une connexion retournée au pool avec un état transactionnel inattendu, un paramètre de session modifié ou une session en erreur peut affecter une requête suivante. Les pilotes et pools de qualité gèrent une partie de ces problèmes, mais la configuration et la discipline applicative restent importantes.

## 4. Du SQL au plan d'exécution

Lorsqu'une application envoie une instruction SQL, le moteur doit en vérifier la syntaxe, les objets, les types et les droits. Ensuite, il choisit une stratégie d'exécution. Pour une requête qui joint plusieurs tables, différents ordres de jointure, méthodes d'accès ou stratégies d'agrégation peuvent être possibles. L'optimiseur estime leur coût à partir des statistiques et des caractéristiques disponibles, puis sélectionne un plan.

Cette explication ne signifie pas que chaque instruction suit toujours une séquence visible identique. Les moteurs peuvent réutiliser des plans préparés, transformer des expressions ou appliquer des optimisations supplémentaires. L'important pour le DBA est de savoir qu'une requête SQL décrit le résultat désiré, tandis que le moteur choisit la manière de calculer ce résultat.

### 4.1 Statistiques et sélectivité

L'optimiseur estime généralement combien de lignes seront touchées par les filtres, la distribution des valeurs et les relations entre tables. Si les statistiques sont périmées ou ne représentent pas la distribution réelle, le plan choisi peut être inadapté. Par exemple, un filtre qui renvoie une ligne sur un grand volume pourrait justifier un accès par index, tandis qu'un filtre qui renvoie une part très importante de la table peut rendre un parcours plus large raisonnable.

Un index ne garantit donc pas que l'optimiseur l'utilisera. La qualité du plan dépend notamment des statistiques, de la sélectivité, du coût des lectures et des opérations nécessaires ensuite. Il faut analyser une requête représentative plutôt que conclure à partir de la seule présence d'un index.

### 4.2 Examiner un plan

EXPLAIN est disponible dans PostgreSQL et MySQL, avec des différences de format et d'options. Il permet d'étudier le plan prévu. Certaines variantes peuvent exécuter réellement la requête et fournir des mesures observées ; elles doivent être utilisées avec prudence sur des données ou systèmes sensibles.

~~~sql
EXPLAIN
SELECT c.cours_id, c.titre_cours, COUNT(i.apprenant_id) AS inscriptions
FROM cours AS c
LEFT JOIN inscriptions AS i
  ON i.cours_id = c.cours_id
GROUP BY c.cours_id, c.titre_cours;
~~~

Le plan peut indiquer des accès séquentiels ou par index, des jointures, des tris et des agrégations. Les termes précis et les champs de la sortie varient selon le moteur. Pour interpréter un plan, comparez les lignes estimées aux lignes observées si le moteur fournit ces mesures, regardez le coût des étapes et comprenez d'abord ce que la requête calcule.

### 4.3 Optimiser une requête de manière rigoureuse

Une démarche efficace comprend :
1. définir une métrique observable — temps, volume lu, nombre de lignes, charge CPU ou attente ;
2. reproduire la requête et le contexte ;
3. examiner les statistiques, les index et le plan ;
4. formuler une hypothèse ;
5. modifier une chose à la fois dans un environnement représentatif ;
6. vérifier le résultat fonctionnel et la mesure de performance ;
7. surveiller le compromis sur l'écriture, le stockage et les autres requêtes.

Une optimisation qui réduit le temps d'une requête tout en provoquant une dégradation globale importante n'est pas nécessairement une amélioration. L'objectif porte sur le service, pas sur une seule requête isolée.

## 5. Mémoire, cache et stockage

Les systèmes relationnels utilisent des structures en mémoire pour limiter les lectures physiques et coordonner le travail. Le moteur peut conserver des pages lues, des pages modifiées, des informations de session, des structures de verrouillage et des résultats intermédiaires. Les détails varient selon la version et l'architecture.

Il faut distinguer cache froid et cache chaud. Lors d'un premier accès, certaines données peuvent devoir être lues depuis le stockage ; les accès suivants peuvent être plus rapides si les pages sont présentes en mémoire. Un test de performance qui n'indique pas l'état du cache risque donc d'être difficile à comparer. Il ne faut pas vider un cache de production pour « rendre le test réaliste » sans connaître les conséquences.

### 5.1 Pages, blocs et lecture

De nombreux moteurs gèrent le stockage par pages ou blocs, plutôt que de traiter chaque cellule comme une opération disque indépendante. Une requête peut lire plusieurs pages contenant des lignes dont elle ne veut conserver qu'une partie. La taille des pages, leur organisation et les stratégies d'accès sont propres au moteur, mais le principe reste que le volume de données lu peut être très différent du volume renvoyé au client.

Une requête qui renvoie dix lignes peut lire beaucoup de pages si elle ne dispose pas d'un chemin d'accès adapté. À l'inverse, un parcours séquentiel important peut être efficace si le résultat porte sur une part significative de la table. Le DBA doit examiner le volume et la méthode, pas seulement le nombre de lignes finales.

### 5.2 Stockage, latence et espace disponible

La capacité disque ne se limite pas à la taille des tables visibles. Il faut considérer les index, les journaux, les fichiers temporaires, les fichiers de tri, les sauvegardes locales éventuelles, les données système et les marges nécessaires à la maintenance. La croissance doit être suivie dans le temps.

Un disque presque plein peut provoquer des erreurs d'écriture, des échecs de maintenance, une incapacité à produire des fichiers temporaires ou à conserver certains journaux requis. Une alerte de capacité doit donc être anticipée à un seuil qui laisse le temps d'agir ; attendre 100 % est trop tard.

### 5.3 Journaux de transactions et durabilité

Les moteurs utilisent des mécanismes de journalisation pour permettre de préserver la cohérence et récupérer des modifications après un arrêt inattendu. PostgreSQL utilise notamment le Write-Ahead Logging (WAL). MySQL/InnoDB utilise notamment un redo log ainsi que d'autres mécanismes de journalisation et de récupération. Les détails exacts ne sont pas identiques, mais le principe de base est que les informations nécessaires à la récupération doivent être rendues persistantes dans un ordre approprié par rapport à certaines écritures de données.

Le journal de transactions ne doit pas être assimilé à une sauvegarde complète. Il peut servir à la récupération après incident et, selon l'architecture et la configuration, à une restauration à un instant précis lorsqu'il est combiné à une sauvegarde de base et à la chaîne de journaux nécessaire. Perdre ou purger trop tôt des journaux requis peut rendre impossible un point de restauration souhaité.

~~~mermaid
flowchart TD
    A["Transaction modifie des lignes"] --> B["Journal de récupération préparé"]
    B --> C["Garanties de persistance selon moteur et configuration"]
    C --> D["Pages de données écrites selon le mécanisme du moteur"]
    D --> E["Après incident : récupération à partir des journaux"]
    E --> F["État cohérent restauré selon les garanties disponibles"]
~~~

La durabilité effective dépend aussi de la configuration, du stockage, des confirmations envoyées par le matériel et des réglages du moteur. Le DBA doit comprendre les compromis entre latence et durabilité, ne pas modifier à l'aveugle les paramètres associés et documenter le niveau de garantie réellement offert.

## 6. Transactions, concurrence et verrous

Plusieurs sessions peuvent lire et modifier simultanément les données. Le moteur doit appliquer les règles d'isolation et coordonner les écritures concurrentes. Les conflits peuvent provoquer des attentes, des interblocages (*deadlocks*) ou des échecs transactionnels. Ces phénomènes sont des éléments ordinaires de l'exploitation d'un système multi-utilisateur.

### 6.1 ACID en contexte opérationnel

- **Atomicité** : une transaction est traitée comme une unité logique ; les modifications non validées ne doivent pas être considérées comme un résultat complet.
- **Cohérence** : les contraintes et règles applicables doivent rester satisfaites lorsque la transaction est acceptée.
- **Isolation** : les transactions concurrentes sont séparées selon le niveau d'isolation et les garanties du moteur.
- **Durabilité** : une transaction confirmée doit respecter les garanties de persistance annoncées par le système et la configuration.

ACID ne veut pas dire que l'application ne peut pas comporter de bug, que toutes les règles métier sont automatiquement codées ou qu'une donnée supprimée peut toujours être restaurée facilement. Les contraintes, le code et les procédures de récupération restent nécessaires.

### 6.2 Verrous et attentes

Les verrous protègent certaines opérations contre des modifications incompatibles. Un verrou peut être conservé pendant une partie importante d'une transaction ; si la transaction est trop longue, d'autres sessions peuvent attendre. Un traitement qui lit des données puis attend plusieurs minutes une interaction utilisateur ne devrait généralement pas garder une transaction ouverte sur toute cette durée.

Un DBA qui observe une hausse de la latence doit vérifier si les requêtes attendent le CPU, le stockage, des verrous, une connexion disponible ou une autre ressource. Le temps total d'une requête peut inclure du temps passé à attendre, pas uniquement du calcul. Il faut identifier la catégorie d'attente avant d'augmenter les ressources au hasard.

### 6.3 Interblocages

Un interblocage se produit lorsque des transactions se bloquent mutuellement de façon cyclique : par exemple, la transaction A détient une ressource attendue par B tandis que B détient une ressource attendue par A. Les moteurs savent généralement détecter certaines situations et annuler une transaction pour permettre au système de progresser.

La correction exige souvent de comprendre l'ordre d'accès aux objets et la durée des transactions. Utiliser un ordre de mise à jour cohérent, maintenir les transactions courtes et traiter proprement les erreurs de transaction peut réduire le risque. Réessayer aveuglément chaque erreur en boucle sans limite peut amplifier la charge et masquer une cause structurelle.

## 7. Sauvegarde, restauration et continuité

Une sauvegarde n'est pas uniquement un fichier créé périodiquement. C'est un élément d'une capacité de reprise. L'organisation doit savoir quelles données sont couvertes, quand la sauvegarde a été effectuée, où elle est conservée, combien de temps elle est gardée, qui peut la lire, comment son intégrité est contrôlée et quelle procédure permet de restaurer le service.

### 7.1 Sauvegarde logique et physique

Une sauvegarde logique représente les objets et les données sous une forme exportée, par exemple un dump SQL ou des instructions d'insertion. Elle peut être pratique pour exporter certains objets, migrer entre environnements ou restaurer une partie des données, selon l'outil. Elle peut prendre du temps et nécessiter des traitements lors de la restauration.

Une sauvegarde physique copie ou capture les structures de stockage selon les mécanismes pris en charge par le moteur ou la plateforme. Elle peut permettre des restaurations plus adaptées à de grands volumes et s'inscrire dans une stratégie avec journaux. Les contraintes de version, de plateforme et de cohérence doivent être respectées.

Aucune méthode n'est universellement meilleure. Le choix dépend de la taille, du temps de restauration, du besoin de récupération ponctuelle, de la portabilité, du coût et des capacités de l'équipe.

### 7.2 RPO et RTO

Le **RPO** (Recovery Point Objective) est la perte de données maximale acceptable mesurée en temps. Si le RPO est de quinze minutes, l'architecture et les procédures doivent permettre, dans le scénario envisagé, de reprendre avec un point de données ne dépassant pas cette fenêtre de perte. Le **RTO** (Recovery Time Objective) est la durée cible pour rétablir le service selon la définition convenue.

Ces objectifs sont des exigences métier et opérationnelles, pas des valeurs qu'un outil garantit tout seul. Ils doivent être discutés avec les propriétaires du service, puis testés avec des scénarios réalistes. Un RPO très faible peut exiger une chaîne de journaux robuste, une réplication adaptée et une exploitation disciplinée. Un RTO très faible peut nécessiter automatisation, infrastructure de secours et procédures éprouvées.

~~~mermaid
flowchart LR
    A["Incident à l'instant T"] --> B["Dernier point restaurable"]
    B --> C["Perte potentielle de données = RPO"]
    A --> D["Détection et décision"]
    D --> E["Restauration / bascule"]
    E --> F["Service validé"]
    D --> G["Durée totale cible = RTO"]
~~~

### 7.3 Pourquoi tester une restauration ?

Une sauvegarde peut exister tout en étant inutilisable : fichier incomplet, clé de chiffrement indisponible, droits insuffisants, sauvegarde corrompue, documentation périmée, journaux manquants, incompatibilité de version ou durée de restauration trop longue. Le test de restauration vérifie l'ensemble de la chaîne, pas uniquement la présence d'un fichier.

Un exercice de restauration doit préciser le scénario, la sauvegarde choisie, l'environnement de récupération, les dépendances, les contrôles de cohérence et les critères de réussite. Pour des données sensibles, l'environnement restauré doit être protégé avec des droits adaptés, car il peut contenir une copie de données réelles.

### 7.4 Exemple d'export logique

Dans PostgreSQL, pg_dump est un outil courant de sauvegarde logique. Exemple indicatif :

~~~bash
pg_dump -h localhost -U lab_user -d skilltree_lab -F c -f skilltree_lab.dump
~~~

Le format choisi et les options de restauration doivent correspondre à la méthode retenue. Le secret ne doit pas être écrit directement dans le script. Utilisez le mécanisme d'authentification sécurisé prévu par l'environnement.

Pour MySQL, un outil courant est mysqldump. Exemple indicatif :

~~~bash
mysqldump -h 127.0.0.1 -u lab_user -p skilltree_lab > skilltree_lab.sql
~~~

Ces commandes sont des exemples pédagogiques, pas une procédure de sauvegarde complète pour une application de production. Il faut examiner la cohérence pendant l'export, les objets inclus, les options du moteur, la taille, la compression, le chiffrement, le stockage hors du système principal, le contrôle d'intégrité et la procédure de restauration.

## 8. Réplication, haute disponibilité et reprise après sinistre

La réplication consiste à propager des données ou des modifications d'un système vers un autre. Elle peut servir à la disponibilité, à la lecture, à la distribution géographique ou à la reprise. Elle n'est pas équivalente à une sauvegarde : une suppression ou une corruption logique peut être propagée au réplicat.

La haute disponibilité (HA) vise à réduire l'interruption de service lors de certains incidents. Elle repose souvent sur la redondance, la détection de défaillance, une procédure de bascule et des contrôles après bascule. La reprise après sinistre (DR) couvre des scénarios plus larges, tels que la perte d'un site, une corruption importante ou un incident de sécurité. Les deux domaines se chevauchent mais les objectifs et les plans doivent être explicites.

### 8.1 Réplication synchrone et asynchrone

Dans une architecture à réplication synchrone, l'accusé de réception de certaines opérations peut dépendre de la confirmation du réplicat selon la configuration. Cela peut renforcer certaines garanties de durabilité, mais augmenter la latence et rendre la disponibilité dépendante du comportement du nœud secondaire ou du réseau.

La réplication asynchrone permet souvent de confirmer plus tôt les écritures sur le primaire, tandis que le secondaire peut présenter un retard. Lors d'une panne brutale, certaines modifications récentes peuvent ne pas être présentes sur le réplicat selon le mécanisme et l'état au moment de l'incident. Les garanties exactes dépendent du moteur et de la topologie ; ne déduisez pas un RPO de zéro du seul mot « réplication ».

### 8.2 Rôle de la bascule

Une bascule (failover) désigne le transfert du service vers un nœud de secours. Le mécanisme doit détecter le bon incident, sélectionner une cible suffisamment à jour, empêcher une double écriture non contrôlée et réorienter les clients. Le nom d'un nœud secondaire n'est pas une garantie qu'il pourra automatiquement devenir primaire sans risque.

Une bascule réussie techniquement doit aussi faire l'objet de vérifications fonctionnelles : les connexions se rétablissent, les applications écrivent au bon endroit, les données sont présentes, les tâches différées redémarrent de manière sûre et la supervision reflète la nouvelle topologie. Il faut également savoir comment revenir à l'état nominal, ce qui peut demander une resynchronisation plutôt qu'un simple retour au serveur précédent.

~~~mermaid
flowchart TD
    A["Nœud primaire"] --> B["Réplication"]
    B --> C["Nœud secondaire"]
    D["Détection d'incident"] --> E["Évaluer état et retard de réplication"]
    E --> F{"Bascule sûre ?"}
    F -- "Non" --> G["Mode dégradé et décision opératoire"]
    F -- "Oui" --> H["Promouvoir le secondaire selon procédure"]
    H --> I["Réorienter les clients"]
    I --> J["Valider écriture, lecture et surveillance"]
~~~

### 8.3 Scénarios à tester

Un plan de reprise doit examiner des scénarios concrets : panne d'un processus, perte d'un disque, interruption réseau, perte du nœud primaire, corruption d'une table, suppression accidentelle, indisponibilité du site ou compromission d'un compte. Tous les scénarios ne doivent pas être testés directement sur la production ; les exercices peuvent utiliser des environnements isolés ou des simulations contrôlées.

Pour chaque scénario, documentez le signal de détection, la personne responsable de la décision, les étapes de reprise, les risques de perte de données, les validations post-reprise et les critères d'arrêt. Un plan qui ne mentionne pas la validation fonctionnelle pourrait déclarer le système rétabli alors que l'application ne peut plus accomplir son parcours métier essentiel.

## 9. Sécurité et gestion des accès

La base de données contient des faits métier parfois sensibles. Le DBA doit appliquer les politiques de l'organisation tout en aidant les applications à obtenir les droits nécessaires, ni plus ni moins. Le principe du moindre privilège limite la portée d'une erreur, d'une compromission ou d'une mauvaise manipulation.

### 9.1 Comptes distincts

Évitez de partager un compte administrateur entre les développeurs, l'application et les tâches d'exploitation. Les comptes distincts permettent d'attribuer les droits à un rôle, de révoquer un accès et d'examiner les journaux. Les comptes humains, les comptes applicatifs et les comptes d'automatisation doivent avoir des fonctions différentes.

Une application qui n'a besoin que de lire certains objets ne devrait pas recevoir les privilèges de création de comptes ou de modification globale du schéma. Les migrations peuvent être exécutées via un compte ou un rôle séparé, déclenché par un processus contrôlé. Les droits élevés doivent être rares, approuvés et traçables.

### 9.2 Rôles, privilèges et séparation des tâches

Un rôle regroupe des privilèges ou des appartenances. Selon le moteur, les mécanismes de rôle varient, mais la stratégie générale reste de créer des rôles correspondant aux fonctions : lecture analytique, opération applicative, migration, sauvegarde, administration restreinte. Évitez les droits accordés individuellement sans documenter pourquoi ils existent.

La séparation des tâches est particulièrement importante pour les opérations risquées. La personne qui rédige une migration n'est pas toujours la seule à l'approuver et à la déployer. Une revue indépendante peut repérer les suppressions involontaires, les changements de type dangereux, les verrous de longue durée ou les opérations qui nécessitent une fenêtre de maintenance.

### 9.3 Protection des secrets et connexions chiffrées

Les mots de passe ne doivent pas être codés en dur dans le dépôt, les scripts de migration, les images de conteneur ou les journaux. Les secrets doivent être stockés dans un mécanisme adapté, avec permissions et rotation. Les chaînes de connexion doivent être protégées en transit et au repos selon le risque. Lorsque les données traversent un réseau non fiable, configurez et vérifiez le chiffrement de la connexion selon le moteur et l'environnement.

Changer régulièrement les mots de passe sans traiter leur distribution peut provoquer des incidents. Préparez la rotation avec les équipes clientes, les pools de connexions, les tâches planifiées et les scripts de secours. La rotation doit inclure la vérification que l'ancien secret n'est plus utilisé, et pas seulement la modification d'une valeur dans un écran d'administration.

### 9.4 Audit et confidentialité

Les journaux peuvent contenir des noms de comptes, des requêtes, des valeurs sensibles ou des fragments de données selon la configuration. Ils doivent être protégés, conservés selon une durée définie et accessibles uniquement aux personnes habilitées. Le détail nécessaire à un diagnostic doit être équilibré avec le risque d'exposer des informations personnelles ou des secrets.

La conformité ne se résume pas à activer une option d'audit. Il faut comprendre les exigences applicables, les catégories de données, la durée de conservation, le droit d'accès, la suppression autorisée et les responsabilités des équipes. Le DBA contribue à l'application technique, mais les décisions réglementaires doivent être prises avec les personnes responsables de la conformité et du métier.

## 10. Surveillance et observabilité

La supervision vise à détecter les anomalies avant qu'elles ne deviennent des incidents majeurs, ou à réduire le délai de diagnostic lorsqu'un incident se produit. Un tableau de bord doit montrer les signaux qui permettent de répondre à des questions opérationnelles précises. Accumuler des graphiques sans seuil, propriétaire ni procédure d'action n'apporte pas une observabilité suffisante.

### 10.1 Indicateurs essentiels

Les mesures courantes comprennent :
- disponibilité de la connexion et réussite d'une requête de santé ;
- latence des requêtes représentatives, avec médiane et percentiles élevés ;
- taux d'erreur et délais d'attente côté application ;
- connexions actives, en attente et maximum de connexions ;
- utilisation CPU et mémoire sur le serveur ou le service managé ;
- lectures et écritures, latence du stockage, espace libre ;
- volume et croissance des tables et index ;
- requêtes lentes, plans inhabituels et attentes sur les verrous ;
- retard de réplication, état du nœud secondaire et résultats des sauvegardes ;
- durée et résultat des tests de restauration.

Chaque indicateur doit être interprété dans son contexte. Une forte utilisation CPU peut être normale pendant une opération d'analyse planifiée ; un CPU bas ne signifie pas que le service va bien si les requêtes attendent un verrou ou un disque lent. Un nombre de connexions élevé peut indiquer une charge réelle, un pool mal dimensionné ou des sessions dormantes qui conservent des ressources.

### 10.2 Latence et percentiles

Une moyenne peut masquer une mauvaise expérience utilisateur. Si la plupart des requêtes prennent très peu de temps mais qu'une minorité attend longtemps, la moyenne seule ne décrit pas cette queue de distribution. Les percentiles, comme le 95e ou le 99e percentile, aident à caractériser les requêtes les plus lentes. Leur interprétation exige une fenêtre d'observation et un volume suffisant.

Ne fixez pas les seuils uniquement parce qu'une valeur est courante dans un exemple. Établissez une référence à partir de la charge réelle et des objectifs de service, puis définissez un seuil et une durée qui déclenchent une action. Des alertes trop sensibles génèrent du bruit ; des alertes trop tardives réduisent le temps de réaction.

### 10.3 Alertes exploitables

Une alerte utile répond à quatre questions : quel problème est observé, quel service est touché, quelle est l'urgence, et quelle action ou documentation doit être consultée ? Par exemple, « la capacité du volume de données risque d'être épuisée avant la fenêtre normale de maintenance » est plus exploitable qu'une simple valeur CPU sans contexte.

~~~mermaid
flowchart LR
    A["Métriques, journaux et événements"] --> B["Seuils et détection"]
    B --> C["Alerte contextualisée"]
    C --> D["Runbook de diagnostic"]
    D --> E["Action ou escalade"]
    E --> F["Validation du rétablissement"]
    F --> G["Retour d'expérience"]
~~~

Les alertes doivent être testées. Il faut confirmer qu'elles se déclenchent lorsqu'une condition est reproduite dans un environnement approprié, qu'elles arrivent aux bons destinataires et que la procédure associée est à jour. Un système de monitoring lui-même peut être indisponible ou mal configuré ; les activités critiques nécessitent donc des vérifications de bout en bout.

## 11. Capacité, croissance et coûts

Le dimensionnement consiste à rapprocher le profil de charge, les besoins de disponibilité et les contraintes de coût des ressources nécessaires. Il doit inclure la croissance des données, les index, les journaux, les fichiers temporaires, les sauvegardes et la marge requise pour les opérations de maintenance. Une base qui fonctionne aujourd'hui peut devenir difficile à exploiter si aucune mesure de croissance n'est suivie.

### 11.1 Projeter le stockage

Une projection simple peut commencer par le volume actuellement occupé, sa croissance nette et la période à couvrir. Mais la taille des tables seules ne donne pas toujours le coût futur : les index peuvent croître, les journaux peuvent augmenter lors d'une charge élevée, une migration peut temporairement nécessiter un espace supplémentaire et une stratégie de sauvegarde peut doubler ou tripler le volume conservé.

L'estimation est une hypothèse qu'il faut réviser à partir des mesures. Notez la période observée et les événements particuliers, comme un import massif ou une migration. Une croissance ponctuelle ne doit pas être extrapolée aveuglément comme une tendance stable.

### 11.2 Limites de connexions et ressources

Le budget de connexions doit considérer le nombre d'instances applicatives multiplié par les connexions potentielles de chaque pool, mais aussi les comptes d'administration, les tâches planifiées, la supervision et les autres consommateurs. La capacité de traitement n'est pas égale au maximum autorisé de connexions. Chaque session peut consommer de la mémoire, et une forte concurrence peut augmenter la contention.

Avant d'augmenter une limite, cherchez la cause : fuite de connexions, pool sans limite, transactions longues, temps de réponse qui augmente et retient les sessions, ou croissance réelle du trafic. La correction peut demander un changement applicatif plutôt qu'un réglage du moteur.

### 11.3 Fenêtres de maintenance

Les opérations de maintenance, les mises à jour, les changements de schéma et les reconstructions d'index peuvent consommer des ressources et parfois bloquer certaines opérations. Une planification réaliste tient compte des périodes de charge, des dépendances applicatives, de la capacité disponible et de la stratégie de retour. La durée doit être mesurée en répétant l'opération sur un environnement représentatif.

## 12. Changements, migrations et gestion d'incident

Un changement de base peut être plus difficile à annuler qu'un changement applicatif, en particulier lorsque de grandes quantités de données sont transformées ou supprimées. Un processus de changement doit préciser l'objectif, le périmètre, les dépendances, les risques, la validation, la surveillance et la stratégie de retour.

### 12.1 Préparer une migration

Une migration devrait répondre aux questions suivantes :
- quelle règle ou fonctionnalité impose ce changement ?
- quelles tables, colonnes, index, contraintes et applications sont affectées ?
- quelles données existantes doivent être transformées ?
- quelles sont les conditions de réussite et les contrôles de cohérence ?
- quels sont les risques de verrouillage, de croissance temporaire ou d'interruption ?
- l'application actuelle reste-t-elle compatible pendant le déploiement ?
- comment revenir à un état sûr si une étape échoue ?
- qui décide de poursuivre, d'arrêter ou de revenir en arrière ?

Les migrations par expansion puis contraction peuvent aider lorsqu'une migration doit rester compatible avec plusieurs versions de l'application : on introduit d'abord une structure compatible, on déploie l'application qui l'utilise, puis on retire l'ancien élément après vérification. Cette méthode ne convient pas automatiquement à chaque changement, mais rappelle qu'une migration doit être coordonnée avec le cycle de vie de l'application.

### 12.2 Runbook et journal d'exploitation

Un runbook est une procédure organisée pour un problème ou une opération. Il doit indiquer les préconditions, les commandes sûres, les signes attendus, les actions interdites ou risquées, les conditions d'escalade et les critères de clôture. Les commandes doivent être adaptées à la version et à la configuration réellement utilisées.

Une procédure d'incident peut commencer par confirmer l'étendue de l'impact, vérifier l'état du service, préserver les informations utiles, identifier les changements récents et consulter les métriques. Les actions correctives sont choisies ensuite selon les indices. Redémarrer le service peut masquer des preuves et interrompre davantage les utilisateurs ; ce n'est pas une réponse universelle à une lenteur.

### 12.3 Retour d'expérience

Après un incident significatif, l'équipe doit comprendre les facteurs techniques et organisationnels qui l'ont permis, sans chercher uniquement une personne à blâmer. Le rapport peut distinguer la cause directe, les facteurs contributifs, les signaux non détectés et les mesures de prévention. Une action préventive doit être assignée à un responsable et posséder un critère de validation.

## 13. Atelier pratique : préparer une fiche d'exploitation pour Skill-Tree

### Mission

Vous êtes chargé de proposer la fiche d'exploitation d'une base SQL qui sert à l'application de formation Skill-Tree. L'atelier n'accède pas à une vraie instance de production : vous construisez un document et réalisez des vérifications dans votre environnement isolé.

Votre fiche doit couvrir l'architecture, les accès, les indicateurs, la sauvegarde et la restauration, les changements et la gestion d'incident.

### Étape 1 — Décrire l'architecture

Complétez les champs suivants dans votre fiche :
- moteur et version ;
- base et schémas utilisés ;
- clients et applications autorisés ;
- méthode de connexion et de chiffrement ;
- pool de connexions et limites ;
- stockage et journaux ;
- réplication éventuelle ;
- dépendances externes et propriétaire du service.

Le diagramme doit montrer les composants réellement présents. Ne dessinez pas une réplication parce qu'elle semble souhaitable si elle n'existe pas dans l'environnement. La documentation doit refléter la réalité.

### Étape 2 — Définir des rôles

Proposez au moins quatre rôles logiques : application en lecture/écriture sur son périmètre, lecture analytique, migration contrôlée et exploitation. Associez à chacun les opérations nécessaires. Vérifiez ensuite que les rôles n'accordent pas involontairement le droit de créer des comptes, modifier l'ensemble du schéma ou supprimer des données hors périmètre.

Il ne suffit pas de donner des noms de rôles. Notez quelles tables et quelles opérations ils couvrent, comment les droits sont demandés, comment ils sont révoqués et comment leur utilisation est tracée. Les privilèges exacts doivent être traduits en commandes selon le moteur cible.

### Étape 3 — Écrire le plan de sauvegarde

Définissez :
- les données et objets couverts ;
- la fréquence de sauvegarde complète et, si pertinent, la conservation de journaux ;
- le lieu de stockage séparé du système principal ;
- la durée de rétention et les protections ;
- les responsables et les canaux d'alerte ;
- le contrôle d'intégrité ;
- les exercices de restauration ;
- le RPO et le RTO convenus avec les propriétaires du service.

Ne choisissez pas des objectifs arbitraires sans discuter du besoin métier. Dans un laboratoire d'apprentissage, notez les valeurs comme hypothèses pédagogiques, puis expliquez qu'elles doivent être validées pour un vrai service.

### Étape 4 — Construire les contrôles SQL

Pour vérifier la santé fonctionnelle du schéma pédagogique, des requêtes simples peuvent compter les objets ou détecter des relations inattendues. Par exemple, la requête suivante recherche les inscriptions sans apprenant ou sans cours correspondant dans un jeu importé :

~~~sql
SELECT i.apprenant_id, i.cours_id
FROM inscriptions AS i
LEFT JOIN apprenants AS a
  ON a.apprenant_id = i.apprenant_id
LEFT JOIN cours AS c
  ON c.cours_id = i.cours_id
WHERE a.apprenant_id IS NULL
   OR c.cours_id IS NULL;
~~~

Dans un schéma correctement protégé par les clés étrangères, ce contrôle devrait renvoyer zéro ligne. Il peut rester utile après une importation historique ou avant une migration. Si une ligne est retournée, ne supprimez pas automatiquement l'enregistrement : identifiez l'origine de la référence, la règle de correction et les dépendances concernées.

### Étape 5 — Concevoir un tableau de bord

Votre tableau de bord doit répondre aux questions :
- la base accepte-t-elle les connexions ?
- l'application réussit-elle une requête métier représentative ?
- les requêtes lentes ou les erreurs sont-elles en hausse ?
- la limite de connexions ou l'espace disque approche-t-il d'un seuil critique ?
- la réplication, si elle existe, est-elle à jour selon l'objectif attendu ?
- la dernière sauvegarde s'est-elle terminée ?
- une restauration récente a-t-elle été testée ?
- les modifications récentes ont-elles un impact observable ?

Pour chaque mesure, indiquez sa source, la fréquence, le seuil, la durée nécessaire avant alerte, le destinataire et la procédure associée. Les métriques sans action possible doivent être réévaluées ; elles ne devraient pas simplement augmenter le bruit opérationnel.

### Étape 6 — Simuler un incident

Choisissez un scénario sans danger, par exemple une requête lente dans la base de laboratoire. Décrivez comment l'alerte serait générée, quelles informations vous collecteriez, quelles hypothèses vous testeriez, comment vous valideriez le rétablissement et quel compte rendu serait écrit.

N'injectez pas de panne sur une instance partagée ou de production pour cet exercice. Les tests destructifs ou les exercices de bascule nécessitent une autorisation et un environnement appropriés. L'apprentissage porte sur la préparation et l'observation, non sur la création non contrôlée d'une interruption.

### Étape 7 — Critères d'acceptation

Votre fiche est prête pour revue si un autre membre de l'équipe peut identifier les composants, connaître les propriétaires, comprendre les risques, exécuter les vérifications documentées dans un laboratoire et savoir quand escalader. Les objectifs de reprise doivent être formulés de façon testable, et la procédure de restauration ne doit pas s'arrêter à « récupérer le fichier ».

## 14. Exercices d'application avec corrigés

### Exercice 1 — Connexion impossible

Une application signale une erreur de connexion. Le serveur SQL répond depuis le terminal d'administration. Quelle est votre première analyse ?

**Corrigé.** Confirmez le périmètre du problème et examinez séparément l'application, le pilote, les secrets, la résolution DNS, le port, le pare-feu, l'authentification et la capacité de connexion. Comparez les paramètres de la connexion applicative à ceux du terminal. Le serveur accessible depuis une machine ne prouve pas qu'il l'est depuis le réseau de l'application.

### Exercice 2 — Trop de connexions

Après une hausse du trafic, la limite de connexions est atteinte. Pourquoi ne faut-il pas seulement augmenter cette limite ?

**Corrigé.** Les sessions consomment des ressources et peuvent augmenter la contention. Il faut examiner la taille des pools, le nombre d'instances, les connexions inactives, les transactions longues, les erreurs empêchant la libération des connexions et les temps de réponse. Une fuite ou un pool mal dimensionné ne se corrige pas nécessairement en autorisant davantage de sessions.

### Exercice 3 — Cache et performance

La même requête est rapide au deuxième essai. Quelles explications devez-vous envisager ?

**Corrigé.** Les pages ou structures nécessaires peuvent être présentes dans le cache lors du deuxième essai. Il peut aussi y avoir des variations de charge ou d'autres facteurs. Documentez l'environnement de test, l'état du cache dans la mesure où il est observable et la distribution des temps ; ne concluez pas à une amélioration durable sur deux exécutions.

### Exercice 4 — Index présent mais non utilisé

Un index existe mais l'optimiseur ne l'utilise pas. Faut-il le supprimer immédiatement ?

**Corrigé.** Non. Vérifiez les statistiques, le filtre, la sélectivité, la distribution des données et le plan. Un parcours plus large peut être moins coûteux si une forte proportion de lignes doit être lue. Mesurez aussi l'effet de l'index sur les écritures et l'espace disque.

### Exercice 5 — Sauvegarde réussie, restauration impossible

Un job confirme que la sauvegarde est terminée, mais le fichier ne se restaure pas. Quels domaines devez-vous examiner ?

**Corrigé.** Vérifiez l'intégrité et la complétude du fichier, les droits, la version du moteur, les options de sauvegarde, les dépendances, les clés de chiffrement, les journaux requis et la procédure utilisée. Cela montre pourquoi un succès de job ne remplace pas un exercice de restauration complet.

### Exercice 6 — Réplication et suppression accidentelle

Un utilisateur supprime accidentellement une table et le réplicat reflète la suppression. Pourquoi la réplication n'est-elle pas une sauvegarde indépendante ?

**Corrigé.** La réplication propage habituellement les modifications, y compris certaines suppressions et corruptions logiques. Une sauvegarde indépendante et un historique permettant de revenir à un état antérieur sont nécessaires pour ce type de scénario, sous réserve des capacités et de la configuration.

### Exercice 7 — RPO et RTO

Le propriétaire métier annonce qu'il tolère au maximum quinze minutes de données perdues et veut le service disponible en une heure. Quels objectifs faut-il formaliser ?

**Corrigé.** Le RPO cible est de quinze minutes au maximum de perte temporelle acceptable, et le RTO cible est d'une heure pour restaurer le service selon la définition convenue. Il faut ensuite prouver que l'architecture, les sauvegardes, les journaux et les procédures permettent d'atteindre ces objectifs lors de scénarios représentatifs.

### Exercice 8 — Rôle trop puissant

Le compte utilisé par l'application peut créer des utilisateurs, modifier le schéma et supprimer toutes les tables. Quel risque pose cette configuration ?

**Corrigé.** Une injection, une erreur de code ou la compromission du compte pourrait provoquer un impact très large. Séparez le rôle applicatif du rôle de migration et d'administration, puis accordez uniquement les opérations nécessaires au compte applicatif. Vérifiez que les changements de droits sont tracés et réversibles.

### Exercice 9 — Une transaction reste ouverte

Des sessions attendent des verrous et vous découvrez une transaction ouverte depuis longtemps. Comment procéder ?

**Corrigé.** Identifiez la session, les objets concernés, l'opération en cours et les conséquences avant de décider de l'annuler. Cherchez pourquoi l'application conserve la transaction : traitement lent, attente réseau, erreur non gérée ou logique applicative. Toute action de terminaison doit suivre le runbook et mesurer le risque de rollback et d'impact utilisateur.

### Exercice 10 — Bascule déclarée réussie

Après une bascule vers un secondaire, le serveur accepte les connexions mais l'application échoue encore à enregistrer les inscriptions. La reprise est-elle terminée ?

**Corrigé.** Non. La disponibilité de connexion est une condition nécessaire, mais la reprise doit être validée fonctionnellement. Vérifiez la cible d'écriture, les droits, les données et les parcours métier critiques, ainsi que la reprise des tâches différées et la cohérence de la supervision.

### Exercice 11 — Migration de colonne

Une migration modifie le type d'une colonne contenant plusieurs millions de lignes. Quelles questions faut-il résoudre avant de la déployer ?

**Corrigé.** Il faut évaluer la conversion des valeurs existantes, les verrous et la durée, l'espace temporaire, les index et contraintes dépendants, la compatibilité de l'application, le plan de validation et la stratégie de retour. Testez sur un volume représentatif et vérifiez le comportement DDL du moteur et de la version ciblés.

### Exercice 12 — Alerte CPU élevée

Une alerte CPU apparaît, mais la latence de l'application reste stable. Quelle est la bonne réaction ?

**Corrigé.** Analysez la durée, la charge attendue, les requêtes actives et les indicateurs associés. Déterminez si le signal est un pic planifié, une nouvelle charge ou le début d'une dégradation. Une alerte doit conduire à une investigation contextualisée, pas nécessairement à une intervention immédiate sur le serveur.

## 15. Défi final corrigé — concevoir l'exploitation d'une base d'application

### Mission

Vous devez remettre un plan d'exploitation pour une application de formation qui stocke comptes, cours, inscriptions et résultats. Le service est utilisé par plusieurs équipes, et les données ne doivent pas être perdues lors d'une panne courante. Le défi porte sur l'organisation des responsabilités et la preuve des contrôles, pas sur l'invention d'une architecture supposée déjà présente.

### Étape A — Cartographier les composants

Dressez une carte du client, des connexions, du moteur SQL, du stockage, des journaux, des sauvegardes, de la supervision et des éventuels réplicats. Identifiez la partie gérée par le fournisseur et celle gérée par l'équipe. Pour chaque composant, indiquez le propriétaire, les dépendances et l'indicateur qui prouve son état.

### Étape B — Définir le modèle d'accès

Séparez les rôles applicatif, lecture analytique, migration et exploitation. Décrivez les permissions nécessaires et celles qui doivent rester absentes. Identifiez la manière de demander, réviser et retirer un privilège. Indiquez comment les connexions sont chiffrées et comment les secrets sont renouvelés sans inclure de valeur sensible dans le dépôt.

### Étape C — Définir reprise et sauvegarde

Proposez un calendrier de sauvegarde cohérent avec les volumes et le besoin métier, une rétention, un stockage séparé et un processus de contrôle d'intégrité. Fixez des RPO et RTO après discussion avec les propriétaires du service, puis définissez un exercice qui peut démontrer ces objectifs. Décrivez le rôle éventuel des journaux et de la réplication sans les confondre avec une sauvegarde complète.

### Étape D — Définir les métriques et alertes

Choisissez les signaux essentiels : erreurs de connexion, latence des requêtes critiques, sessions, espace disponible, attentes, état des sauvegardes et retard de réplication s'il y a lieu. Pour chaque signal, donnez un seuil provisoire justifié, une durée, un destinataire, un runbook et une condition de clôture. Identifiez les mesures qui nécessitent un étalonnage sur le trafic réel.

### Étape E — Préparer un changement

Choisissez une modification fictive, comme ajouter un statut à INSCRIPTIONS. Écrivez un plan de migration avec les préconditions, la compatibilité des versions applicatives, le contrôle des valeurs existantes, la validation après déploiement et la stratégie de retour. Évaluez le besoin de verrouillage et de temps d'arrêt. Exécutez uniquement l'exemple dans un laboratoire jetable.

### Étape F — Simuler un incident

Décrivez les étapes de réponse à une hausse durable de latence. Commencez par confirmer l'impact, consulter les métriques, chercher les changements récents, inspecter les plans et attentes, puis décider d'une action à partir des preuves. Préservez les informations utiles au diagnostic et rédigez un bref retour d'expérience qui inclut une action de prévention mesurable.

### Corrigé de référence

Un plan acceptable n'impose pas un moteur, un fournisseur ou un nombre de réplicats arbitraire. Il distingue les responsabilités de l'équipe et du fournisseur, définit les propriétaires, décrit les contrôles et indique comment vérifier les objectifs de service. Il protège les secrets, applique le moindre privilège, possède une procédure de restauration testée et un système d'alertes avec des actions associées.

Le plan est également explicite sur les limites : une sauvegarde réussie n'assure pas la restauration tant qu'elle n'a pas été testée ; la réplication ne protège pas automatiquement contre toutes les suppressions ou corruptions logiques ; un pool plus grand n'améliore pas forcément la capacité ; une connexion au serveur ne prouve pas la disponibilité fonctionnelle de l'application ; et un changement de schéma doit tenir compte du volume et de la compatibilité applicative.

### Critères de réussite

Le défi est réussi si un autre membre de l'équipe peut expliquer l'architecture, identifier le responsable de chaque action, appliquer les contrôles dans un laboratoire, savoir quelle alerte déclenche quelle procédure et vérifier une reprise sans se fier à un seul message de succès. La fiche doit indiquer les hypothèses et les éléments qui nécessitent une validation dans l'environnement réel.

## 16. Checklist opérationnelle du DBA

Avant une mise en service ou une revue d'exploitation, vérifiez les points suivants :

- Le moteur, sa version, l'environnement et le propriétaire sont connus.
- L'architecture, les dépendances et les chemins réseau sont documentés.
- Les comptes applicatifs et humains sont distincts.
- Les rôles suivent le principe du moindre privilège.
- Les connexions sont protégées selon le risque et les secrets ne sont pas stockés dans les scripts.
- Les limites de connexions et le dimensionnement des pools sont connus.
- Les indicateurs de latence, d'erreur, de capacité et de concurrence sont suivis.
- Les requêtes critiques disposent d'un moyen de diagnostic du plan d'exécution.
- Les sauvegardes sont surveillées et stockées avec des protections appropriées.
- Une procédure de restauration existe et a été testée récemment.
- Les objectifs RPO et RTO sont validés par le métier et vérifiés par un exercice.
- La réplication, si elle existe, est surveillée et sa garantie réelle est connue.
- Les changements de schéma sont revus, testés, versionnés et accompagnés d'un plan de retour.
- Les procédures d'incident sont à jour et les personnes d'astreinte connaissent leur rôle.
- Les alertes mènent à des actions et possèdent des critères de clôture.
- Les tests n'utilisent pas de données sensibles sans autorisation.
- Les retours d'incident débouchent sur des actions préventives suivies.

## 17. Synthèse finale

Le DBA contribue à garantir qu'une base de données reste disponible, cohérente, protégée, performante et récupérable. Son travail combine architecture, gestion des accès, supervision, capacité, optimisation, sauvegarde, restauration, préparation des changements et réponse aux incidents. Il collabore avec les développeurs, la plateforme, la sécurité et les propriétaires métier ; il n'est pas un simple opérateur de commandes SQL et ne peut pas, seul, compenser des exigences mal définies.

Un SGBD reçoit les requêtes des clients, authentifie les connexions, analyse le SQL, choisit des plans, exécute les opérations et s'appuie sur la mémoire, le stockage et les journaux. Les transactions et mécanismes de concurrence protègent le comportement face aux opérations simultanées. Les détails techniques diffèrent entre moteurs, mais les questions d'exploitation sont communes : quelles ressources sont utilisées, quelles attentes se produisent, quelles garanties sont offertes et comment vérifier le résultat réel ?

La sauvegarde, la réplication, la haute disponibilité et la reprise après sinistre sont complémentaires mais non interchangeables. La restauration doit être testée. Les objectifs RPO et RTO doivent venir du besoin métier puis être démontrés par des exercices. La sécurité exige des rôles limités, la gestion des secrets, des connexions protégées et des contrôles appropriés. La surveillance doit transformer des métriques en signaux exploitables, avec des seuils, des responsables et des runbooks.

Enfin, l'administration fiable repose sur des preuves reproductibles. Une commande réussie ne démontre pas à elle seule que le service est sain ; un job de sauvegarde ne prouve pas que la reprise fonctionnera ; une bascule réseau ne prouve pas le retour de tous les parcours métier. La discipline du DBA consiste à formuler des hypothèses, observer les signaux, vérifier les postconditions, documenter les limites et améliorer les procédures à partir des incidents.

## Références techniques

Consultez les guides correspondant à la version réellement exploitée. Les noms de processus, options, métriques et comportements DDL varient selon le moteur et la plateforme.

- PostgreSQL, documentation officielle : https://www.postgresql.org/docs/current/
- PostgreSQL, architecture du système : https://www.postgresql.org/docs/current/tutorial-arch.html
- PostgreSQL, sauvegarde et restauration : https://www.postgresql.org/docs/current/backup.html
- PostgreSQL, surveillance des statistiques : https://www.postgresql.org/docs/current/monitoring-stats.html
- MySQL 8.4, référence officielle : https://dev.mysql.com/doc/refman/8.4/en/
- MySQL 8.4, moteur InnoDB et architecture : https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html
- MySQL 8.4, sauvegarde et récupération : https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html
- OWASP, prévention des injections SQL : https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

Les commandes présentes dans cette leçon sont illustratives. Validez-les dans une base de laboratoire, selon la version, les privilèges et les procédures de votre environnement, avant tout usage opérationnel.
