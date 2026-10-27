# Rôle du DBA et architecture SGBD — Intermédiaire

> **Mise en contexte.** Une application peut sembler fonctionner correctement tout en accumulant des connexions inutiles, des verrous trop longs, des sauvegardes impossibles à restaurer ou des privilèges excessifs. Le rôle du DBA consiste à rendre le service de données prévisible : il faut comprendre l’architecture, mesurer son comportement, préserver l’intégrité, réduire le risque de changement et pouvoir démontrer qu’un retour à la normale est possible. Les exemples utilisent principalement PostgreSQL, avec des points de comparaison pour MySQL. Les commandes exactes dépendent de la version, du système d’exploitation et du mode de déploiement. Travaillez dans un environnement de test avant toute opération sur des données réelles.

## Objectifs d’apprentissage

À l’issue de ce cours, vous devez être capable de représenter les composants d’un SGBD, de décrire le rôle du moteur transactionnel, de distinguer les responsabilités du DBA des responsabilités du développeur et de l’équipe plateforme, d’interpréter quelques indicateurs opérationnels, de choisir une méthode de diagnostic, de limiter les privilèges et de préparer une intervention réversible. Vous apprendrez aussi à formaliser une décision technique avec des preuves, plutôt qu’avec une impression comme « la base est lente ».

Le niveau intermédiaire suppose que vous connaissez les tables, les clés, les transactions et le SQL courant. Il ne signifie pas que vous devez administrer seul un cluster de production dès le premier jour. Il signifie que vous savez organiser une investigation, demander les bons éléments, reconnaître les limites de vos droits et vérifier une hypothèse sans dégrader le service.

Les objectifs opérationnels sont les suivants :

- tracer le chemin d’une requête depuis le client jusqu’au stockage et au résultat ;
- distinguer processus, sessions, transactions, verrous, cache, journal et fichiers de données ;
- expliquer pourquoi une transaction longue peut gêner d’autres transactions même si elle n’exécute presque plus de requêtes ;
- reconnaître les symptômes de saturation CPU, mémoire, entrées-sorties, connexions et verrous ;
- concevoir une séparation raisonnable entre comptes applicatifs, comptes d’administration et comptes de supervision ;
- préparer un changement avec préconditions, fenêtre, étapes, critères d’arrêt et procédure de retour arrière ;
- différencier disponibilité, sauvegarde, réplication et reprise après sinistre ;
- rédiger un compte rendu opérable par un collègue qui n’a pas participé à l’incident.

## Prérequis et environnement de travail

Vous devez pouvoir vous connecter à une instance de test avec un client SQL, lire les informations de version, créer un schéma de test et exécuter une transaction. Une installation locale suffit pour les premiers exercices. Une instance de laboratoire isolée est encore préférable lorsque vous pouvez reproduire des connexions concurrentes.

Dans les exemples, utilisez une base de laboratoire nommée lab_dba et un compte applicatif limité. Ne réutilisez jamais un compte superutilisateur dans un logiciel applicatif. Les mots de passe, jetons, fichiers de configuration contenant des secrets et exports de données personnelles doivent rester hors des dépôts Git et des journaux de démonstration.

Avant un atelier, consignez :
- le produit et sa version ;
- le système d’exploitation ou le conteneur ;
- le mode de connexion : socket local, TCP, proxy ou pool ;
- les privilèges du compte utilisé ;
- les données de test ;
- les commandes de remise à zéro.

Une observation sans version, contexte ni unité est rarement reproductible. Une durée de 200 millisecondes ne signifie pas la même chose pour une requête interactive très fréquente et pour un traitement analytique lancé une fois par nuit.

## 1. Le rôle du DBA dans le cycle de vie d’un service

Le DBA ne se limite pas à créer des tables ou à répondre aux demandes de mots de passe. Il contribue à la conception, à l’exploitation, à la sécurité et à la continuité du service de données. Dans une petite équipe, une seule personne peut couvrir plusieurs fonctions. Dans une grande organisation, ces fonctions peuvent être réparties entre administration, plateforme, sécurité, ingénierie de données et développement.

### 1.1 Conception et préparation

Lors de la conception, le DBA vérifie que les besoins sont traduits en règles concrètes. Combien d’utilisateurs simultanés sont prévus ? Quel volume de données est attendu ? Quels sont les pics ? Quelles données doivent être conservées ? Quelles opérations doivent être atomiques ? Quelle durée d’indisponibilité est acceptable ? Quel niveau de perte de données est tolérable ?

La réponse n’est pas simplement « dimensionner un serveur puissant ». Une architecture mal conçue peut gaspiller beaucoup de ressources tout en restant lente. Par exemple, ajouter de la mémoire n’élimine pas une requête qui lit toute une table à chaque appel. De même, augmenter le nombre maximal de connexions peut aggraver une saturation si chaque session consomme une portion importante de mémoire.

Le DBA documente les hypothèses. Si la charge prévue est de 300 requêtes par seconde, il faut préciser si ce chiffre est un pic, une moyenne, un objectif mesuré ou une extrapolation. Il faut également distinguer les lectures, les écritures, les transactions courtes et les traitements longs.

### 1.2 Exploitation quotidienne

L’exploitation inclut la surveillance, l’analyse des anomalies, la gestion de l’espace disque, les mises à jour, le contrôle des sauvegardes, la gestion des utilisateurs, les modifications de schéma et l’assistance aux développeurs. Les tâches doivent être planifiées et suivies. Une action faite « de mémoire » est difficile à auditer et à reproduire.

Une bonne routine comprend un petit ensemble de vérifications : état du service, place disponible, volume d’erreurs, durée des requêtes importantes, transactions anciennes, état des sauvegardes et dernières alertes pertinentes. La routine doit rester suffisamment courte pour être utilisée ; un tableau de bord comportant cent indicateurs dont personne ne sait quoi faire ne constitue pas une stratégie d’exploitation.

### 1.3 Gestion du changement

Tout changement est un risque, même lorsqu’il semble mineur. Une modification de type peut verrouiller une grande table. Un index supplémentaire peut accélérer une lecture mais alourdir les écritures. Une mise à jour de version peut modifier les plans d’exécution ou retirer une option. Un changement de permissions peut empêcher un traitement nocturne.

Une demande de changement doit donc préciser son objectif, sa portée, les préconditions, les vérifications, les critères d’arrêt, l’impact possible, la communication et le retour arrière. « Exécuter la commande et regarder si cela marche » n’est pas un plan de changement suffisamment précis.

### 1.4 Responsabilités et limites

Le DBA est responsable de la bonne administration du service, mais il ne doit pas être la seule personne capable de restaurer une sauvegarde ou de comprendre la topologie. Il coordonne avec les développeurs, l’équipe plateforme, la sécurité et les propriétaires métier. Le propriétaire métier définit la valeur des données et les contraintes de conservation ; l’équipe sécurité définit les politiques et exigences ; le DBA contribue à les implémenter et à les vérifier.

Le partage des responsabilités doit être explicite. Si une application génère une charge SQL inefficace, l’administration peut mesurer et conseiller, mais la correction du code appartient généralement à l’équipe applicative. Si le stockage persistant est mal configuré, l’équipe plateforme doit participer. Si un compte est trop privilégié, le DBA et la sécurité définissent une correction et vérifient qu’elle n’interrompt pas les usages légitimes.

## 2. Architecture logique et chemin d’une requête

La manière la plus efficace de diagnostiquer une base est de suivre le chemin réel d’une opération.

~~~mermaid
flowchart LR
    A[Client ou application] --> B[Pool de connexions]
    B --> C[Session du SGBD]
    C --> D[Parseur et planificateur]
    D --> E[Exécuteur SQL]
    E --> F[Gestionnaire de verrous et transactions]
    E --> G[Cache mémoire]
    G --> H[Fichiers de données]
    E --> I[Journal de transactions]
    H --> J[Résultat]
    I --> K[Reprise après incident]
~~~

Le schéma est volontairement simplifié. Le détail varie selon le produit et les options activées, mais les frontières sont utiles : le client peut attendre le réseau ou le pool avant même que le SGBD exécute la requête ; le SGBD peut attendre un verrou ; le moteur peut lire des pages du stockage ; et le client peut encore prendre du temps pour traiter le résultat.

### 2.1 Client et pool

L’application utilise une bibliothèque ou un pilote qui ouvre une connexion. Une connexion est un canal de communication et, suivant le produit, peut correspondre à une session serveur avec un état et des ressources. Créer puis détruire une connexion à chaque requête peut coûter cher. Un pool réutilise des connexions dans des limites définies.

Un pool doit être dimensionné à partir de la charge et de la capacité serveur, pas d’un nombre arbitraire. Si vingt instances applicatives autorisent chacune cinquante connexions, le total théorique atteint mille connexions. Le paramètre local « cinquante » ne dit rien sur la capacité totale. Il faut examiner le nombre d’instances, les pools secondaires, les tâches d’arrière-plan et les connexions administratives.

Le pool peut lui-même devenir le goulot d’étranglement. Un grand nombre de requêtes en attente côté application n’implique pas nécessairement que le moteur soit saturé. Vérifiez les métriques d’attente du pool, le temps d’obtention d’une connexion et le nombre de connexions réellement actives côté serveur.

### 2.2 Session, transaction et requête

Une session peut exécuter de nombreuses requêtes successives. Une transaction regroupe des opérations qui doivent respecter les garanties transactionnelles. Une requête est une instruction, par exemple un SELECT ou un UPDATE. Ces unités ne doivent pas être confondues.

Une session ouverte et inactive peut être normale dans un pool. Une transaction ouverte depuis longtemps et non terminée peut retenir des verrous ou empêcher certaines opérations de maintenance. Le statut « idle » n’est donc pas suffisant pour juger qu’une session est sans risque : il faut examiner si une transaction est en cours, depuis combien de temps, quel utilisateur l’a ouverte et quelle opération a précédé l’attente.

### 2.3 Parseur et planificateur

Le parseur vérifie la syntaxe et la structure de la requête. Le planificateur estime le coût des stratégies possibles à partir des statistiques, des index et des caractéristiques des données. L’exécuteur applique ensuite le plan choisi.

Une requête SQL identique peut recevoir un plan différent après une variation importante du volume de données, une mise à jour des statistiques, une modification de schéma ou un changement de version. Un plan est une décision fondée sur des estimations, pas une preuve que l’exécution sera rapide dans toutes les conditions.

Le coût estimé n’est pas une durée en millisecondes. Il sert à comparer des plans dans le modèle du moteur. Pour mesurer la réalité, on utilise des outils d’exécution et des métriques. Attention aux commandes qui exécutent réellement une requête ; en laboratoire, certaines commandes de mesure peuvent consommer les ressources qu’elles sont censées étudier.

### 2.4 Cache, pages et stockage

Les SGBD gèrent généralement des pages de données en mémoire afin d’éviter des lectures physiques répétées. Le système d’exploitation peut aussi avoir son propre cache. Une requête peut donc lire une page depuis la mémoire ou attendre une opération d’entrée-sortie.

Un bon taux de cache ne garantit pas une application rapide. Il peut y avoir trop de CPU consommé, une attente de verrou, un grand tri en mémoire, une contention sur une ressource partagée ou trop de données transférées vers l’application. Le taux de cache doit être interprété avec la latence et le volume de travail.

Les fichiers de données contiennent les structures persistantes du moteur. Le journal de transactions sert notamment à garantir la durabilité et à récupérer un état cohérent après un arrêt. La façon exacte dont le moteur écrit les pages, synchronise le journal et effectue les checkpoints varie selon le produit et sa configuration.

## 3. Moteur transactionnel, journalisation et durabilité

Les propriétés ACID constituent un cadre de référence : atomicité, cohérence, isolation et durabilité. Elles ne signifient pas que toute application est automatiquement correcte. Le schéma, les contraintes et les transactions de l’application doivent être conçus de façon cohérente.

### 3.1 Atomicité et cohérence

L’atomicité signifie qu’une transaction est entièrement validée ou n’est pas appliquée comme une transaction validée. Supposons qu’une opération déplace une quantité de stock d’un entrepôt A vers un entrepôt B. Si le débit est enregistré mais pas le crédit, l’état est incorrect. Les deux opérations doivent appartenir à une transaction commune.

La cohérence renvoie au respect des règles d’intégrité. Les contraintes SQL contribuent à cet objectif, mais les règles métier doivent être exprimées correctement. Une transaction qui termine avec COMMIT n’est pas nécessairement correcte si l’application a appliqué une mauvaise règle.

### 3.2 Isolation et concurrence

Plusieurs transactions peuvent travailler simultanément sur les mêmes données. L’isolation détermine quels effets d’une transaction sont visibles par les autres. Les niveaux d’isolation et leurs implémentations diffèrent selon les moteurs. Il faut donc lire la documentation du produit utilisé au lieu de supposer qu’un même nom garantit exactement le même comportement partout.

Une lecture répétée peut, suivant le niveau d’isolation, voir un état différent. Une opération de mise à jour peut attendre un verrou détenu par une autre transaction. Un deadlock survient lorsque plusieurs transactions se bloquent mutuellement dans un cycle d’attente ; le moteur choisit généralement une transaction victime pour rétablir la progression.

Un deadlock n’est pas nécessairement une panne du moteur. Il peut révéler un ordre d’accès incohérent dans l’application. La correction consiste souvent à uniformiser l’ordre des mises à jour, réduire la durée des transactions et ajouter une reprise bornée lorsque l’erreur est reconnue comme transitoire. Répéter automatiquement toute opération sans vérifier son atomicité peut doubler un paiement ou créer des écritures en double.

### 3.3 Durabilité et journal de transactions

La durabilité signifie que la confirmation de validation respecte le contrat de persistance du moteur et de sa configuration. Dans PostgreSQL, le WAL journalise les changements nécessaires à la récupération et permet plusieurs stratégies de sauvegarde et de réplication. Dans MySQL, les mécanismes du moteur InnoDB et le journal binaire jouent des rôles différents mais complémentaires selon les besoins.

La présence d’un journal ne suffit pas. Le stockage doit être persistant et correctement configuré, les paramètres de synchronisation doivent correspondre au niveau de durabilité attendu et le mécanisme de sauvegarde doit pouvoir être restauré. Une réplication asynchrone peut avoir un retard ; un basculement immédiat n’implique donc pas toujours qu’aucune donnée confirmée ne soit perdue.

### 3.4 Checkpoints et récupération

Les checkpoints contribuent à limiter le travail nécessaire lors de la reprise après un arrêt. Ils écrivent ou synchronisent des pages modifiées selon le fonctionnement du moteur. Un réglage agressif peut augmenter la charge d’écriture à certains moments ; un réglage trop permissif peut allonger la récupération et augmenter le volume de journal nécessaire.

Il ne faut pas copier les paramètres d’un serveur sans comprendre sa charge. La bonne méthode consiste à mesurer le volume d’écriture, les temps de checkpoint, les retards, les attentes de stockage et la durée de récupération en test. Les métriques du moteur et celles du système d’exploitation doivent être examinées ensemble.

## 4. Transactions longues et verrous

Une transaction longue est l’une des causes les plus fréquentes de comportements apparemment inexplicables. L’application peut exécuter une requête, recevoir un résultat, puis conserver la transaction ouverte pendant qu’un utilisateur remplit un formulaire ou qu’un processus appelle un service externe.

La bonne pratique consiste à réduire la zone transactionnelle. Le réseau, l’appel d’une API distante ou le traitement d’un long fichier ne doivent pas être inclus dans une transaction de base de données sauf nécessité explicite et bien évaluée.

### 4.1 Lire les états d’attente

Dans PostgreSQL, la vue pg_stat_activity renseigne sur les sessions, les requêtes et les états. Les colonnes disponibles et leur sens précis dépendent de la version. Une exploration de laboratoire peut commencer avec :

~~~sql
SELECT pid, usename, application_name, state,
       wait_event_type, wait_event,
       now() - xact_start AS duree_transaction,
       now() - query_start AS duree_requete,
       left(query, 180) AS extrait
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY xact_start NULLS LAST;
~~~

Cette requête est un outil de diagnostic, pas un ordre automatique de tuer les sessions. Une session ancienne peut correspondre à une opération importante ; l’extrait peut contenir des valeurs sensibles ; et la visibilité complète exige des privilèges de supervision adaptés. Sur un service réel, appliquez la politique de confidentialité de l’organisation.

### 4.2 Diagnostic des deadlocks

Pour analyser un deadlock, collectez les messages du serveur, les identifiants de transaction lorsqu’ils sont disponibles, les requêtes impliquées, les verrous concernés et les événements qui ont précédé le conflit. L’objectif est de reconstruire la séquence d’accès, pas uniquement de supprimer la transaction victime.

Exemple pédagogique :
1. La transaction A modifie la ligne de commande 10.
2. La transaction B modifie la ligne de commande 20.
3. A attend la ligne 20.
4. B attend la ligne 10.
5. Le moteur détecte le cycle et annule une transaction.

Une correction possible est de mettre à jour les lignes dans le même ordre dans les deux chemins applicatifs. Une autre consiste à réduire les transactions ou à revoir la granularité des verrous. Le choix dépend des garanties métier ; désactiver les protections ou répéter indéfiniment n’est pas une solution.

## 5. Capacité et ressources

Une base de données consomme plusieurs ressources, et l’occupation d’une seule n’explique pas toujours la latence.

### 5.1 CPU

Une consommation CPU élevée peut venir d’une requête très fréquente, d’un plan inefficace, d’un tri ou agrégat coûteux, d’un traitement de données, de nombreuses petites requêtes ou d’une contention qui entraîne du travail répété. Il faut classer les requêtes par fréquence et par durée cumulée. Une requête de 20 millisecondes exécutée cent mille fois peut coûter davantage qu’une requête de dix secondes exécutée une fois.

### 5.2 Mémoire

La mémoire sert au cache et à certaines opérations comme les tris et les jointures. Selon le moteur et le contexte, certains paramètres sont appliqués par session ou par opérateur ; augmenter un paramètre de mémoire peut donc multiplier la consommation lorsque de nombreuses requêtes s’exécutent simultanément. Une configuration qui fonctionne dans une session de test peut provoquer une pression mémoire sous concurrence.

### 5.3 Entrées-sorties et espace disque

Une latence de stockage élevée peut allonger des lectures aléatoires, des checkpoints, des écritures de journal ou des sauvegardes. Mais un grand nombre d’entrées-sorties n’est pas forcément mauvais : une charge analytique peut être légitimement intensive. Examinez la latence, le débit, la profondeur de file, le volume et les objectifs de service.

L’espace disque est une dimension de continuité. Une base proche de sa limite peut refuser de nouvelles écritures ou perdre la capacité de produire certains fichiers de journal. L’alerte doit anticiper le seuil réel d’action : il faut prendre en compte le rythme de croissance, les fichiers temporaires, les sauvegardes locales et la marge de récupération.

### 5.4 Nombre de connexions

Le maximum de connexions n’est pas un objectif à atteindre. Un grand nombre de sessions actives peut augmenter la contention et la mémoire consommée. Les sessions inactives peuvent être attendues dans un pool, mais un nombre inhabituel doit être expliqué par le modèle de connexion et non accepté comme normal sans mesure.

La capacité doit être évaluée avec une charge représentative. Mesurez les temps d’attente du pool, le nombre de requêtes concurrentes, les sessions réellement actives, la consommation mémoire et la latence côté application. Augmentez la limite seulement si les éléments montrent qu’elle est le véritable goulot d’étranglement.

## 6. Observabilité et alertes utiles

Un tableau de bord utile répond à des questions opérationnelles. Une alerte utile indique un symptôme, un seuil, un propriétaire et une action possible. Les alertes qui se déclenchent en permanence finissent par être ignorées.

### 6.1 Signaux de base

La latence des requêtes importantes, le taux d’erreur, le nombre de connexions actives et en attente, la durée des transactions, les deadlocks, l’espace disque, les retards de réplication et le résultat des sauvegardes sont de bons points de départ. Ils doivent être interprétés par rapport à un profil normal et à un objectif de service.

Mesurez au minimum :
- la disponibilité du point de connexion ;
- le temps de réponse perçu par l’application ;
- la latence et le débit du moteur ;
- les erreurs SQL et leurs familles ;
- les ressources système ;
- la fraîcheur des sauvegardes ;
- le retard de réplication lorsqu’une réplication est utilisée.

Une sonde qui se contente d’ouvrir un port TCP ne prouve pas que le moteur peut exécuter une requête. Une sonde SQL simple prouve davantage, mais elle ne vérifie toujours pas toute l’application, les autorisations métier et les dépendances externes.

### 6.2 Seuils, tendance et durée

Il faut combiner seuil et durée. Un pic CPU de quelques secondes peut être normal ; une saturation prolongée qui coïncide avec l’augmentation de la latence est plus préoccupante. Un disque à 85 % peut être acceptable si sa croissance est lente et la marge suffisante, mais dangereux s’il progresse rapidement et si les journaux vont grossir avant la prochaine fenêtre de maintenance.

Les seuils doivent dériver des objectifs et de l’observation. Un tableau de bord est une hypothèse visuelle. Une alerte est une décision opérationnelle. Si personne ne peut préciser ce qu’il fera lorsque l’alerte s’active, il faut la revoir.

### 6.3 Éviter les métriques trompeuses

Une moyenne peut cacher une longue traîne. Une latence moyenne faible peut coexister avec un petit nombre de requêtes très lentes qui affectent fortement les utilisateurs. Les percentiles, le taux d’erreur et la fréquence d’une requête complètent la moyenne.

Le taux de cache n’indique pas à lui seul la rapidité. Une session active ne signifie pas qu’elle consomme du CPU. Une réplication « connectée » ne signifie pas qu’elle est à jour. Un job de sauvegarde « terminé » ne signifie pas nécessairement que le fichier est intègre et restaurable. Chaque métrique doit être reliée à une preuve et à une limite connue.

## 7. Sécurité et séparation des comptes

La séparation des identités est un principe fondamental. L’application n’a généralement besoin que des opérations nécessaires à son fonctionnement. Elle ne devrait pas créer des comptes, modifier des rôles d’administration ou lire toutes les bases du serveur.

### 7.1 Rôles distincts

Un modèle simple distingue :
- le compte applicatif, limité au schéma et aux opérations nécessaires ;
- le compte de migration, utilisé temporairement lors des changements de schéma ;
- le compte de supervision, autorisé à lire les métriques nécessaires ;
- le compte d’administration, soumis à des contrôles renforcés ;
- le compte de sauvegarde, autorisé à effectuer les opérations requises sans disposer de privilèges inutiles.

Ces comptes peuvent être différents selon l’organisation. Le but est de limiter les conséquences d’un secret volé, d’une erreur de script ou d’un processus compromis.

### 7.2 Exemple de rôles PostgreSQL

Dans une base de laboratoire, un administrateur peut préparer des privilèges ciblés de la façon suivante. Vérifiez les noms de schéma et les exigences de la version avant adaptation.

~~~sql
CREATE ROLE app_reader LOGIN;
CREATE ROLE app_writer LOGIN;
GRANT CONNECT ON DATABASE lab_dba TO app_reader, app_writer;
GRANT USAGE ON SCHEMA public TO app_reader, app_writer;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_reader;
GRANT SELECT, INSERT, UPDATE, DELETE
  ON ALL TABLES IN SCHEMA public TO app_writer;
~~~

Ce modèle n’est qu’un point de départ. Il faut également considérer les séquences, les fonctions, les futurs objets, les propriétaires de schéma et les privilèges par défaut. Les commandes de création doivent être intégrées à une migration ou une procédure versionnée. Accordez les droits nécessaires à l’objectif, puis testez avec le compte réel qui sera utilisé par l’application.

### 7.3 Secrets et accès d’urgence

Les secrets doivent être stockés dans un gestionnaire de secrets ou dans le système adapté à l’environnement. Ils ne doivent pas apparaître dans un fichier de configuration partagé, les arguments de commande visibles, les captures d’écran ou les journaux. L’accès d’urgence doit avoir une procédure, une traçabilité et une date de revue.

Après une rotation de secret, vérifiez que les pools redémarrent ou renouvellent leurs connexions comme prévu. Une rotation réussie côté coffre de secrets mais non appliquée au service ne constitue pas une rotation terminée.

## 8. Haute disponibilité, réplication et reprise

La haute disponibilité réduit la durée d’indisponibilité face à certains types de panne. La réplication copie des changements vers une autre instance. Une sauvegarde permet de reconstruire des données après perte, corruption ou erreur. Ces mécanismes sont complémentaires, pas interchangeables.

Une réplication peut propager une suppression accidentelle. Une sauvegarde peut être inutilisable si la clé de chiffrement est perdue. Un basculement peut échouer si les clients conservent l’ancien endpoint. Une restauration peut prendre plus de temps que l’objectif admis si elle n’a jamais été testée sur un volume réaliste.

### 8.1 Questions à poser avant un basculement

Quel est l’état du primaire ? Quel est le retard du réplica ? Les données sont-elles suffisamment synchronisées pour le type de basculement envisagé ? Comment l’application découvrira-t-elle le nouvel endpoint ? Qui autorise l’opération ? Comment éviter que deux primaires acceptent simultanément des écritures ? Comment vérifier l’état après le changement ?

La réponse dépend du produit et du mode de réplication. Ne copiez pas une procédure d’un autre moteur sans vérifier les garanties. Après basculement, testez l’écriture, la lecture, les permissions, les tâches planifiées et la cohérence des données. Conservez une preuve horodatée des étapes importantes.

### 8.2 Objectifs RPO et RTO

Le RPO représente la perte maximale de données tolérée, souvent exprimée comme une durée de données. Le RTO représente la durée cible pour rétablir le service. Ces objectifs doivent venir du métier et être transformés en architecture, processus et exercices.

Une entreprise qui accepte une perte de cinq minutes ne peut pas se contenter de savoir qu’un réplica existe. Elle doit mesurer le retard, comprendre le comportement lors de panne et confirmer que son processus de basculement respecte l’objectif. De même, un RTO de quinze minutes exige de mesurer la détection, la décision, la restauration ou le basculement, la validation et la reconnexion applicative.

## 9. Méthode de diagnostic d’incident

La méthode commence par l’impact et la sécurité, pas par une modification aléatoire de paramètres.

1. Définir le symptôme observable : utilisateurs concernés, fonctions touchées, début, fréquence et impact métier.
2. Confirmer le périmètre : instance, base, application, région, réseau ou dépendance externe.
3. Collecter des indices avant modification : métriques, logs, erreurs, requêtes, changements récents et sessions en attente.
4. Formuler une hypothèse testable : « les requêtes attendent un verrou de table » est plus utile que « la base est lente ».
5. Choisir une vérification qui discrimine plusieurs causes sans aggraver la situation.
6. Appliquer la mesure la moins risquée qui répond à la cause confirmée.
7. Vérifier les postconditions côté moteur et côté utilisateur.
8. Documenter les limitations et les actions restantes.

La première tâche n’est pas toujours de restaurer immédiatement toutes les fonctionnalités. Si une opération d’écriture risque d’aggraver une corruption, la protection des données peut imposer une mesure de confinement. L’autorité d’arrêt et le processus d’escalade doivent être définis par l’organisation.

## 10. Changement de schéma sans surprise

Les migrations de schéma doivent être compatibles avec les versions de l’application qui peuvent coexister pendant le déploiement. Une migration qui renomme immédiatement une colonne peut casser l’ancienne version encore en service.

Une méthode courante est progressive :
1. ajouter la nouvelle structure ;
2. déployer une application capable de lire ou écrire l’ancien et le nouveau modèle si nécessaire ;
3. migrer les données par lots surveillés ;
4. vérifier la cohérence et les compteurs ;
5. basculer les lecteurs et les écrivains ;
6. retirer l’ancienne structure lors d’une étape distincte lorsque son absence est démontrée sûre.

Le plan doit inclure l’effet sur les verrous et la durée de traitement. Un index construit sur une table volumineuse peut avoir des implications de disponibilité dépendantes de la méthode utilisée. Une conversion de type peut provoquer une réécriture. Testez la commande sur un volume proche de la réalité et définissez un critère d’arrêt.

## 11. Atelier pratique guidé : diagnostic de sessions et de capacité

### But

Observer des sessions concurrentes sur une base de test, repérer une transaction longue et produire une note de diagnostic sans tuer de session à l’aveugle.

### Préparation

Utilisez une instance PostgreSQL de laboratoire. Créez une table simple et quelques lignes :

~~~sql
CREATE TABLE dba_lab_orders (
  order_id BIGINT PRIMARY KEY,
  status TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO dba_lab_orders(order_id, status)
VALUES (10, 'pending'), (20, 'pending');
~~~

Ouvrez deux sessions de client. Dans la première, démarrez une transaction et modifiez la ligne 10 sans valider immédiatement :

~~~sql
BEGIN;
UPDATE dba_lab_orders
SET status = 'processing', updated_at = now()
WHERE order_id = 10;
~~~

Dans la seconde, effectuez une opération distincte sur la ligne 20 puis tentez une mise à jour de la ligne 10. Observez l’attente, puis revenez à la première session et terminez la transaction avec COMMIT ou ROLLBACK. N’utilisez pas de données réelles pour cet exercice.

### Déroulement et vérifications

Exécutez la requête de diagnostic de pg_stat_activity présentée plus haut. Identifiez les sessions, leur état, la durée des transactions et la requête active. Ne supposez pas que l’identifiant PID d’une capture précédente représente encore la même session plusieurs minutes plus tard.

Répétez ensuite le test en terminant la transaction rapidement. Comparez la durée d’attente. Notez la différence entre « une requête lente » et « une requête qui attend une autre transaction ». Enfin, rédigez une recommandation : réduire la durée de transaction, corriger l’ordre d’accès, ajouter un timeout prudent si cela correspond aux règles d’exploitation, ou instrumenter le chemin applicatif.

### Critères d’acceptation

- Les deux sessions sont identifiées sans mélanger PID, transaction et requête.
- L’attente observée est expliquée par une opération reproductible.
- Les données de laboratoire restent cohérentes.
- Aucune session n’est terminée sans raison et sans connaître les effets.
- Le compte rendu contient heure, version, preuve et limites.
- L’exercice est reproductible par un autre apprenant.

## 12. Étude de cas : connexion saturée après un déploiement

### Situation

Un service Web répond normalement le matin. Après un déploiement et une augmentation du trafic, les utilisateurs signalent que les opérations d’enregistrement prennent plusieurs secondes. Le tableau de bord montre beaucoup de connexions et une hausse du temps d’attente côté application. Le CPU du serveur de base n’est pas constamment saturé.

### Diagnostic

Le symptôme est compatible avec plusieurs causes : pool trop petit, connexions qui ne sont pas libérées, transactions trop longues, attente de verrous, augmentation du nombre de requêtes ou baisse de capacité du moteur. La seule observation du nombre de connexions ne permet pas de choisir entre ces hypothèses.

L’équipe collecte le nombre de connexions configurées par instance, le nombre d’instances actives, la taille réelle du pool, le temps moyen d’obtention d’une connexion, l’état des sessions côté SGBD, les durées de transaction et les requêtes principales. Elle compare aussi la version déployée à la précédente et cherche les modifications de logique transactionnelle.

Les traces montrent que plusieurs chemins d’application ouvrent une transaction, puis attendent un service externe avant de valider. Les connexions restent donc occupées même lorsque le moteur ne consomme pas beaucoup de CPU. Ajouter des connexions pourrait déplacer le problème vers le serveur sans corriger le comportement.

### Correction proposée

Le chemin applicatif est modifié afin d’éviter d’attendre l’API externe à l’intérieur d’une transaction longue, tout en conservant les garanties métier nécessaires. Les opérations de base sont découpées selon le modèle de cohérence défini. L’équipe ajoute des mesures de durée de transaction et de temps de pool, puis met en place une limite prudente de durée pour les opérations qui ne doivent pas rester ouvertes indéfiniment.

### Preuve d’efficacité

Le test de charge reproduit le profil d’activité précédent. On mesure une baisse du temps d’attente des connexions, une diminution des transactions longues et une latence de sauvegarde améliorée sans hausse anormale des erreurs. Les tests vérifient aussi qu’une interruption de l’API externe ne laisse pas des écritures dans un état incohérent. La correction n’est considérée terminée qu’après vérification de ces postconditions.

## 13. Exercices corrigés

### Exercice 1 — Beaucoup de connexions, CPU normal

**Énoncé.** Le nombre de connexions est presque au maximum, la latence utilisateur augmente, mais le CPU moyen reste modéré. Quelle investigation doit venir en premier ?

**Correction.** Mesurez le temps d’attente du pool, les sessions réellement actives, les transactions anciennes, les verrous et les attentes du moteur. Comparez les nombres de connexions configurées dans toutes les instances. N’augmentez pas directement le maximum : les sessions peuvent attendre un verrou, être retenues par des transactions longues ou être multipliées par des pools indépendants.

### Exercice 2 — Une sauvegarde existe, mais la restauration échoue

**Énoncé.** Le tableau de bord indique que le job de sauvegarde a terminé avec succès, mais la restauration ne peut pas être complétée.

**Correction.** Vérifiez le format attendu, l’intégrité du fichier, les métadonnées, l’espace de destination, la version du moteur, les clés de chiffrement et les journaux requis pour le niveau de reprise visé. La réussite du processus de copie n’équivaut pas à une restauration prouvée. Préparez un exercice reproductible et suivez le temps total jusqu’à la validation applicative.

### Exercice 3 — Le taux de cache est élevé, mais une requête reste lente

**Énoncé.** Un rapport indique un taux de cache de 99 %, mais un endpoint continue de dépasser son objectif de latence.

**Correction.** Examinez les attentes de verrou, le temps CPU, la cardinalité, le volume transféré, le tri, les jointures, le plan d’exécution et le traitement côté client. Le cache évite certaines lectures physiques, mais il n’élimine pas le travail logique ou la contention. Utilisez une mesure ciblée plutôt que d’interpréter un indicateur isolé comme preuve de performance.

### Exercice 4 — Un rôle applicatif exige des privilèges administrateur

**Énoncé.** Un composant demande un rôle superutilisateur pour effectuer une migration et exécuter des requêtes au quotidien.

**Correction.** Séparez le rôle de migration et le rôle d’exécution. Déterminez les objets et actions réels nécessaires, testez les privilèges les plus limités possibles et prévoyez une procédure de migration contrôlée. Un rôle d’exécution privilégié augmente fortement l’impact d’une injection SQL, d’un secret exposé ou d’une erreur applicative.

### Exercice 5 — Le deadlock revient

**Énoncé.** Le moteur annule régulièrement une transaction victime et les erreurs sont simplement retentées par l’application.

**Correction.** Collectez la trace du deadlock, reconstruisez l’ordre d’accès aux objets et harmonisez cet ordre dans les chemins concurrents. Réduisez la durée transactionnelle et appliquez une reprise bornée uniquement aux erreurs transitoires identifiées. Mesurez les occurrences avant et après correction. Ne transformez pas les retries en boucle infinie.

### Exercice 6 — Le réplica est connecté mais en retard

**Énoncé.** Le service de réplication indique une connexion active, mais les rapports affichent des données anciennes.

**Correction.** Vérifiez l’horodatage du dernier changement appliqué, le retard mesuré selon les métriques du moteur, l’accumulation de journaux, les limites réseau et la charge du réplica. La connectivité prouve un canal, pas la fraîcheur. Si les rapports ont un contrat de fraîcheur, ce contrat doit être mesuré et surveillé.

## 14. Défi final corrigé : préparer une intervention DBA

### Énoncé

Une équipe doit passer d’une instance de laboratoire à un service plus chargé. L’application a un pool, la base possède plusieurs index historiques, la réplication est configurée et les sauvegardes sont automatisées. Aucun document ne décrit les rôles, les temps de restauration ou les critères de basculement. Produisez un plan d’intervention vérifiable.

### Correction attendue

**1. Établir l’état initial.** Répertorier versions, architecture, tailles, paramètres importants, rôles, chemins réseau, volumes, fréquence des sauvegardes et retards de réplication. Exporter les paramètres non secrets et identifier les informations qui doivent rester protégées. Enregistrer les valeurs de référence pour la latence, le débit, le CPU, la mémoire, les connexions et les attentes.

**2. Définir les objectifs.** Obtenir du métier les objectifs de disponibilité, le RPO, le RTO, le niveau de perte toléré et les fenêtres de changement. Vérifier que la solution proposée peut les atteindre. Si ce n’est pas possible, documenter l’écart plutôt que présenter un objectif comme acquis.

**3. Tester la charge.** Construire un profil représentatif avec des lectures, des écritures, des opérations concurrentes et des traitements longs. Contrôler les résultats métier, pas seulement le débit. Observer les pools, les verrous, les plans et le stockage.

**4. Vérifier sécurité et privilèges.** Distinguer les comptes applicatifs, les migrations, la supervision et l’administration. Tester l’application avec les privilèges réels. Vérifier le stockage de secrets, leur rotation et le comportement des pools après rotation.

**5. Prouver la récupération.** Restaurer une sauvegarde sur une cible isolée et mesurer le temps complet, depuis la préparation jusqu’à la vérification des données et le démarrage applicatif. Si le PITR est requis, restaurer à un point précis avant et après un changement connu. Consigner les limites du test.

**6. Définir le plan de changement.** Écrire les étapes, les responsables, la fenêtre, les critères de poursuite, les critères d’arrêt, les vérifications, les annonces et le retour arrière. Les opérations destructives nécessitent une approbation et une sauvegarde dont la restaurabilité est démontrée.

**7. Vérifier après intervention.** Confirmer les connexions, les autorisations, les écritures et lectures métier, la réplication, la surveillance et la sauvegarde suivante. Les tests de fumée doivent être sans risque et ne pas créer de faux résultats ou de données métier indésirables.

**8. Transformer le retour d’expérience en amélioration.** Documenter ce qui a marché, les écarts de durée, les signaux qui manquaient et les actions à automatiser. Le compte rendu doit permettre à un autre opérateur de réaliser la procédure sans dépendre d’un échange oral.

Le défi est validé lorsque la procédure est reproductible, que les hypothèses sont explicites, que les risques ont une réponse et que les résultats sont observables.

## Fiche de vérification avant exploitation

- Je peux expliquer le trajet d’une requête et identifier la frontière responsable d’une attente.
- Je sais distinguer session, requête, transaction et verrou.
- Je sais trouver les transactions longues sans terminer arbitrairement une session.
- Je comprends que cache élevé, réplication connectée et sauvegarde réussie ne sont pas des preuves suffisantes isolément.
- Je peux décrire les rôles et privilèges nécessaires à l’application.
- Je sais préparer un changement avec préconditions, critères d’arrêt et retour arrière.
- Je sais décrire la différence entre haute disponibilité, réplication et restauration.
- Je possède au moins une mesure de restauration complète et récente.
- Je sais documenter les limites d’une investigation et les prochaines étapes.

## Glossaire

**DBA** : administrateur ou administratrice de bases de données, responsable de la fiabilité et de l’exploitation du service de données.

**SGBD** : logiciel qui organise le stockage et l’accès aux données, gère les transactions et fournit des interfaces de requête.

**Session** : contexte de communication entre un client et le moteur.

**Transaction** : ensemble d’opérations regroupées selon les garanties transactionnelles.

**Verrou** : mécanisme de coordination qui protège certains accès concurrents.

**Deadlock** : cycle d’attentes entre transactions qui empêche leur progression jusqu’à l’intervention du moteur.

**WAL** : journal utilisé notamment pour assurer la durabilité et la récupération dans PostgreSQL.

**Checkpoint** : point de synchronisation qui participe à la récupération après incident.

**RPO** : objectif de perte de données maximale tolérée.

**RTO** : objectif de délai maximal de rétablissement du service.

**Réplication** : propagation de données ou de changements entre instances.

**Pool de connexions** : composant qui réutilise et limite les connexions entre l’application et le SGBD.

**Observabilité** : capacité à comprendre l’état interne du système à partir de métriques, de logs et de traces.

**Postcondition** : état qui doit être vrai après une opération pour qu’elle soit considérée réussie.
