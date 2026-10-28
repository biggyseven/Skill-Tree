# Backup, PITR et restauration — Intermédiaire

> **Mise en contexte.** Un vendredi soir, une migration applicative supprime par erreur un ensemble d’inscriptions. Le serveur est toujours disponible et les répliques fonctionnent : elles ont simplement reproduit la suppression. L’équipe découvre alors qu’une sauvegarde réussie ne garantit pas à elle seule une restauration complète, et qu’un fichier de sauvegarde ne suffit pas si les journaux qui permettent de revenir au bon instant ont disparu. Une stratégie de continuité doit répondre à trois questions concrètes : que peut-on restaurer, jusqu’à quel instant peut-on revenir et combien de temps faut-il pour remettre l’application en service ?

## Objectifs et parcours pratique

Ce cours approfondit les sauvegardes relationnelles, les sauvegardes logiques et physiques, les journaux de transaction, la restauration à un instant donné (PITR), les objectifs RPO et RTO, la protection des copies, les contrôles d’intégrité et les exercices de restauration. À la fin, vous devrez pouvoir écrire une politique de sauvegarde, sélectionner une méthode adaptée à une base donnée, préparer une restauration isolée, calculer les écarts entre l’objectif et le résultat mesuré, et construire une procédure de reprise documentée.

Les exemples principaux concernent PostgreSQL. Certaines idées sont communes à MySQL et à d’autres SGBD, mais leurs formats, leurs mécanismes de journalisation, leurs commandes, leurs niveaux de cohérence et leurs procédures de PITR ne sont pas interchangeables. Les exemples de commandes supposent des outils compatibles avec la version du serveur et des permissions adéquates. Ils doivent être exécutés dans un environnement de test avant d’être adaptés à la production.

Le parcours pratique suit une application de formation. Les données comprennent les apprenants, les cours, les inscriptions, les tentatives de quiz, les récompenses et l’état de progression. Toutes les commandes destructives doivent utiliser une base isolée. Ne restaurez jamais une copie sur le serveur de production sans un plan approuvé qui explique l’impact, la perte potentielle de données et la possibilité de revenir à l’état précédent.

## 1. Ce que signifie réellement « avoir une sauvegarde »

Une sauvegarde est une représentation récupérable d’un état des données et, selon la méthode, d’une partie de la configuration nécessaire à la remise en service. Son utilité dépend de la cohérence de la copie, de son intégrité, de sa disponibilité, de sa compatibilité avec le moteur, de la conservation des clés de chiffrement et de la documentation de restauration. Une tâche terminée avec un code de retour égal à zéro apporte une preuve limitée : elle n’atteste pas nécessairement que la base est récupérable dans le délai métier.

Il faut séparer plusieurs objectifs. La disponibilité cherche à garder le service accessible. La redondance fournit des composants de remplacement. La réplication copie des modifications vers un autre nœud. La sauvegarde permet de retrouver un état antérieur. L’archivage conserve des données ou des journaux pour des objectifs de conformité ou d’investigation. Ces mécanismes peuvent se compléter mais ne se remplacent pas. Une réplique peut accélérer une bascule; elle peut aussi répliquer une suppression accidentelle, une corruption logique ou une commande malveillante.

La stratégie doit couvrir des scénarios de défaillance différents : perte d’un disque, suppression de lignes, erreur de migration, compromission de compte, corruption de fichiers, perte d’un environnement complet, défaillance du fournisseur et suppression des sauvegardes elles-mêmes. Le même plan ne protège pas nécessairement contre tous ces scénarios. Une sauvegarde stockée uniquement sur le même volume que les données est vulnérable à la perte de ce volume. Une copie accessible par le même compte administrateur peut être vulnérable à une compromission de ce compte.

Une copie doit aussi être lisible par l’organisation. Il faut savoir qui peut demander une restauration, qui l’autorise, où elle sera exécutée, comment les secrets seront disponibles, qui vérifie la cohérence et qui décide du retour en service. Une sauvegarde cryptée dont la clé a été perdue n’est pas une sauvegarde exploitable. Une archive intacte, mais sans information sur sa version ni la façon de la restaurer, peut prendre beaucoup plus de temps à exploiter qu’attendu.

## 2. RPO, RTO et objectifs de service

Le RPO, ou Recovery Point Objective, représente la perte maximale de données que l’organisation accepte après un incident. Il est généralement exprimé en durée. Avec un RPO de cinq minutes, l’équipe vise à récupérer un état dont le retard ne dépasse pas cinq minutes de transactions; cela ne signifie pas que chaque système a automatiquement cette garantie. Le RTO, ou Recovery Time Objective, correspond au délai maximum admis pour restaurer le service opérationnel, pas seulement pour lancer le processus de restauration.

Ces objectifs appartiennent au métier. Un système de progression pédagogique peut tolérer la perte d’un faible volume de données de lecture calculées, mais pas nécessairement la perte de résultats d’examen ou d’achats. Une application interne non critique et un service de certification peuvent demander des RPO et RTO différents. Il faut classer les données selon leur valeur, leur fréquence de modification et les conséquences d’une indisponibilité ou d’une perte.

Le RPO influence la fréquence des sauvegardes, l’archivage des journaux, la réplication et les confirmations d’écriture. Le RTO influence le choix entre restauration complète, restauration partielle, nœud de secours, procédures automatisées et capacité réservée. Une sauvegarde complète quotidienne peut répondre à un RPO de 24 heures dans certaines conditions, mais elle ne répond pas à un RPO de cinq minutes sans mécanisme complémentaire qui conserve les modifications plus récentes.

Le RTO doit inclure l’ensemble de la chaîne : identification de l’incident, décision, provisionnement de l’environnement, restauration, application des journaux, validation de la base, configuration de l’application, changement de routage, tests fonctionnels et communication. Mesurer uniquement le temps de copie des fichiers sous-estime souvent le délai réel. Il faut ajouter une marge pour les erreurs et l’indisponibilité des personnes clés.

Exemple d’un objectif de reprise explicite : « À la suite de la perte complète du primaire, remettre les fonctions d’inscription et de consultation en service en moins de 45 minutes, avec au maximum cinq minutes de données validées perdues. Vérifier le nombre d’inscriptions, la cohérence des résultats et le fonctionnement des flux d’authentification avant de rouvrir l’accès ». Cet objectif est testable; il indique aussi quels flux doivent fonctionner avant de déclarer la reprise terminée.

## 3. Sauvegarde logique et sauvegarde physique

Une sauvegarde logique exporte les objets ou données sous une représentation logique : instructions SQL, tables, lignes ou contenu dans un format de dump. Elle peut être sélective et transférable entre environnements compatibles. Elle est utile pour déplacer une base, restaurer une table ciblée ou inspecter le contenu. Cependant, sa restauration peut nécessiter de recréer les objets et réinsérer les données; pour une très grosse base, cela peut être beaucoup plus lent qu’une restauration physique.

Une sauvegarde physique copie les fichiers ou blocs utilisés par le moteur, accompagnés des métadonnées et journaux nécessaires pour obtenir un état cohérent. Elle est souvent plus adaptée à la restauration rapide d’une grosse instance ou à une reprise à un instant donné, selon le mécanisme. Elle peut être étroitement liée à la version du moteur, à l’architecture, aux paramètres et au layout du stockage. Une copie de fichiers à chaud sans utiliser le mécanisme supporté par le moteur n’est pas forcément une sauvegarde cohérente.

Il faut aussi décider du périmètre : une base unique ou toute l’instance, les objets globaux, les rôles, les permissions, les extensions, les paramètres, les certificats, les secrets, les tâches planifiées et les dépendances externes. Une sauvegarde de données peut ne pas inclure les rôles globaux ou la configuration du serveur. La procédure de reprise doit identifier ces éléments séparément. Les données de l’application et la configuration nécessaire pour les servir sont deux catégories qui doivent être coordonnées.

La sauvegarde à chaud permet de capturer des données alors que le système continue à fonctionner, si le mécanisme du moteur assure la cohérence requise. Une sauvegarde à froid nécessite un arrêt ou une période d’indisponibilité, mais peut simplifier certaines opérations. Le choix dépend du niveau de disponibilité, du moteur et de la méthode supportée. Ne copiez pas directement un répertoire de données actif avec un outil générique en supposant qu’il s’agit d’un point cohérent.

La fréquence n’est pas seulement un calendrier. Un full quotidien, des incréments plus fréquents et des journaux archivés peuvent former une stratégie; il faut vérifier que chaque chaîne reste complète. Des copies fréquentes simplifient parfois le RPO, mais augmentent le stockage, le trafic et les opérations de vérification. Une stratégie optimale compare la récupération possible, le coût et la charge opérationnelle, plutôt que de maximiser uniquement le nombre de copies.

## 4. Sauvegarde logique avec PostgreSQL

pg_dump produit une sauvegarde logique d’une base PostgreSQL. Le format personnalisé est pratique pour une restauration flexible via pg_restore. Il est possible d’utiliser un nom de fichier qui identifie la base, la date, le type de sauvegarde et éventuellement un identifiant de changement. Les fichiers doivent être stockés dans un emplacement protégé, avec une politique de rétention et un contrôle d’intégrité.

~~~bash
pg_dump --format=custom --no-owner --no-privileges \
  --dbname=skilltree \
  --file=skilltree-2026-10-28.dump
~~~

Cette commande suppose que les variables d’environnement ou le service d’authentification du client permettent la connexion à la base skilltree. Elle ne contient pas de mot de passe en ligne de commande, ce qui éviterait de l’exposer dans l’historique du shell ou la liste des processus. Utilisez un fichier de configuration protégé, un gestionnaire de secrets ou le mécanisme d’authentification approuvé. Ne stockez pas le mot de passe dans le dépôt.

Vérifiez que le dump peut être lu par pg_restore et inspectez la liste des objets avant de compter sur cette copie :

~~~bash
pg_restore --list skilltree-2026-10-28.dump
~~~

Cette liste n’est pas un test complet de restauration. Le fichier peut contenir les objets attendus, mais la preuve la plus forte consiste à le restaurer dans une base propre et à valider les données. Une sauvegarde logique est souvent adaptée aux migrations entre environnements, mais une restauration peut échouer si les versions, extensions, rôles ou paramètres nécessaires ne sont pas disponibles.

Un essai de restauration dans un nom de base isolé :

~~~bash
createdb skilltree_restore_test
pg_restore --dbname=skilltree_restore_test \
  --no-owner --no-privileges \
  skilltree-2026-10-28.dump
~~~

N’exécutez pas cette commande sur une base portant un nom de production. Dans un exercice de laboratoire, vérifiez ensuite les tables, les contraintes, le nombre d’enregistrements et quelques invariants métier. Les options pour recréer ou supprimer des objets doivent être choisies selon la cible. pg_restore --clean peut supprimer des objets existants avant de les recréer; il est dangereux sur une base contenant des données à conserver.

Les rôles et objets globaux nécessitent une stratégie séparée si l’environnement restauré en dépend. Les options exactes varient selon le besoin et la version. Une migration d’un environnement à un autre est aussi une occasion de vérifier si les propriétaires, les droits et les extensions sont souhaités dans la cible. Restaurer chaque privilège historique sans revue peut réintroduire des accès qui ne devraient plus exister.

## 5. Sauvegarde physique et journal WAL

PostgreSQL utilise le Write-Ahead Log (WAL) pour enregistrer les modifications nécessaires à la reprise. Une sauvegarde physique exploitable est coordonnée avec le mécanisme de base backup et les journaux requis. pg_basebackup permet d’effectuer une sauvegarde de base dans les conditions prévues par PostgreSQL. Les options dépendent de la version, du protocole de réplication disponible et des paramètres du serveur.

~~~bash
pg_basebackup \
  --pgdata=/srv/restore/base \
  --format=plain \
  --wal-method=stream \
  --progress
~~~

Cette commande est schématique et doit être adaptée au système, à l’authentification, aux permissions du répertoire, au type de déploiement et à la version PostgreSQL. Le répertoire cible doit être approprié au service, vide et correctement protégé. Les options de sauvegarde physique ne sont pas une commande de restauration à exécuter n’importe où : la procédure complète doit comprendre la préparation du répertoire, les journaux, la configuration de récupération, la validation et le passage contrôlé en service.

L’archivage continu du WAL permet de conserver des segments nécessaires à la récupération à un instant donné. Il doit être configuré et testé avant l’incident. Il faut surveiller les échecs d’archivage et l’espace consommé, car un problème d’archive peut empêcher une restauration au point requis et, selon la configuration, provoquer une accumulation de journaux. La politique définit les destinations, les droits, le chiffrement, les règles de rétention et les alertes.

Le WAL n’est pas un journal applicatif destiné à être lu par un humain pour expliquer un métier. Il sert au moteur. Le journal des événements d’application demeure nécessaire pour comprendre quelle opération a déclenché une modification. Les deux systèmes sont complémentaires : les journaux SQL/HTTP permettent la chronologie; les journaux de transaction permettent la reprise technique lorsque toutes les préconditions sont réunies.

Pour être utile, la sauvegarde physique doit être associée à une procédure qui connaît le fichier de base, les segments WAL nécessaires, les paramètres et la version du moteur. Un segment manquant peut rompre la chaîne. Une sauvegarde et ses journaux doivent être conservés de façon cohérente et vérifiés ensemble, pas seulement chacun séparément.

## 6. PITR : revenir à un instant juste avant l’erreur

La restauration à un instant donné utilise une sauvegarde de base et les journaux de transaction requis pour avancer jusqu’à un point cible. Le point peut correspondre à une heure, une transaction ou un identifiant de restauration pris en charge par le moteur. L’intérêt est de récupérer l’état antérieur à un événement dommageable tout en conservant les modifications qui l’ont précédé.

Pour réussir, il faut disposer d’une sauvegarde de base compatible, d’une archive WAL complète depuis le point de base jusqu’à la cible, des paramètres de récupération et du temps nécessaire à la replay. Si l’archivage a été activé après l’incident ou si certains segments ont expiré, il est possible que le point voulu soit impossible à atteindre. Cette limite doit être surveillée avant l’incident.

Le processus général est :

~~~mermaid
flowchart TD
    A[Détecter et borner l'incident] --> B[Préserver la production et les journaux]
    B --> C[Choisir une sauvegarde de base connue saine]
    C --> D[Restaurer dans un environnement isolé]
    D --> E[Rejouer les journaux jusqu'au point cible]
    E --> F[Mettre en pause et valider les données]
    F --> G{Cohérence métier confirmée ?}
    G -- Non --> H[Choisir un autre point ou corriger la stratégie]
    H --> D
    G -- Oui --> I[Préparer la bascule contrôlée]
    I --> J[Test fonctionnel et réouverture]
~~~

La cible doit être choisie avec des preuves. Une heure approximative peut couper une transaction métier ou inclure l’opération fautive. Les journaux applicatifs, les alertes, les identifiants de requête, les journaux d’audit et l’heure des opérations aident à identifier le point. Les écarts de fuseau horaire ou les horloges mal synchronisées compliquent l’enquête; les systèmes doivent utiliser une stratégie de temps cohérente.

Le PITR n’annule pas automatiquement les effets externes. Une commande SQL peut avoir inséré une demande de paiement dont le message a déjà été envoyé à un service externe. Restaurer l’état de la base avant ce paiement ne rembourse pas l’opération chez le fournisseur. La procédure doit coordonner les services externes, la file de messages, les envois de courriels, les systèmes de facturation et les éventuelles clés d’idempotence.

Une restauration PITR devrait souvent être réalisée dans un environnement isolé, puis validée avant de remplacer le service actif. Cela permet de vérifier la cohérence des données et de comparer l’état restauré à la production. La bascule requiert une stratégie claire pour éviter que deux primaires acceptent simultanément des écritures divergentes, et un plan pour réconcilier les transactions valides créées après le point de restauration.

## 7. Restauration complète, partielle et réconciliation

Une restauration complète reconstruit l’état de la base ou du serveur selon la sauvegarde. Elle est appropriée lorsque la panne concerne l’ensemble de l’environnement. Une restauration partielle peut être utile lorsque seule une table, un schéma ou un ensemble d’objets a été supprimé. Cependant, un dump logique et un PITR physique n’ont pas la même granularité ni les mêmes procédures. Il peut être plus sûr de restaurer la base entière dans une instance temporaire, puis d’extraire les objets ou lignes nécessaires après validation.

La restauration partielle exige de comprendre les dépendances. Une table d’inscriptions dépend d’apprenants et de cours; un résultat de quiz peut dépendre de tentatives, de banques de questions et d’un identifiant de version. Récupérer une table sans ses contraintes, séquences, vues, fonctions et relations peut produire une base dont les données paraissent présentes mais ne sont plus cohérentes. Il faut préparer une extraction qui conserve les relations pertinentes.

La réconciliation est le processus de comparaison et de fusion des données restaurées avec les opérations valides effectuées après le point choisi. Il faut définir quelles données sont conservées, supprimées ou reconstruites; les règles ne doivent pas être décidées au hasard pendant l’incident. Les identifiants d’opérations, les historiques d’événements et les contraintes uniques peuvent aider à éviter les doublons. Toute réconciliation importante doit être scriptée et testée plutôt qu’effectuée par un ensemble de modifications manuelles non reproductibles.

Une procédure de restauration partielle ne peut pas remplacer les sauvegardes qui ont été perdues. Elle doit être documentée avec les limites connues, le niveau de cohérence, le nombre de lignes vérifiées et la décision du propriétaire métier. Pour un jeu de données critique, il peut être nécessaire de conserver un instantané avant de commencer l’extraction afin de pouvoir reproduire le processus.

## 8. Rétention, chiffrement et protection des copies

Une politique de rétention définit combien de temps conserver les copies, à quelle fréquence, sur quel support et avec quelles règles de suppression. Elle doit concilier la possibilité de détecter tardivement une corruption, les objectifs d’investigation, la capacité de stockage, la confidentialité et les obligations applicables. Conserver plus longtemps n’est pas toujours plus sûr : les copies historiques peuvent contenir des données personnelles qui ne devraient plus être accessibles à grande échelle.

Le chiffrement protège la confidentialité des sauvegardes lorsque les fichiers sont stockés ou transférés. Il doit être associé à une gestion des clés : rotation, séparation des responsabilités, disponibilité pendant la reprise, journal d’accès et procédure de récupération en cas de perte. Si l’unique clé est stockée sur le même serveur que les sauvegardes et qu’un incident détruit les deux, le chiffrement devient un obstacle à la restauration.

Les comptes qui écrivent ou suppriment les sauvegardes doivent être limités. Un mécanisme d’immutabilité ou de verrouillage de rétention peut réduire le risque de suppression malveillante, s’il est disponible sur le service de stockage choisi. Les accès de lecture doivent être suffisamment restreints, car un dump peut contenir toutes les données métier et les informations personnelles de l’application.

Les copies hors site ou dans une région séparée peuvent protéger contre la perte d’un emplacement, mais elles introduisent des questions de coût, de latence et de conformité. Le lieu de stockage doit respecter la politique de données et les contrats applicables. Une réplique de base dans une autre région n’est pas nécessairement équivalente à une sauvegarde indépendante, notamment si les identifiants, le compte de contrôle et la possibilité de suppression restent partagés.

L’effacement final des copies fait partie du plan. Si une personne exerce un droit de suppression de ses données, les règles applicables aux sauvegardes historiques et aux restaurations doivent être précisées : durée de rétention, impossibilité ou coût d’une suppression immédiate dans une copie immuable, et mécanisme de réapplication des suppressions après restauration. Cette politique doit être revue avec les responsables de confidentialité et de conformité.

## 9. Vérifier les sauvegardes automatiquement

Une supervision efficace suit les dernières sauvegardes réussies, la durée de création, la taille, l’âge des journaux archivés, les erreurs, le volume de stockage et la date du dernier test de restauration. Les alertes doivent tenir compte du RPO et du délai nécessaire pour corriger le problème. Si l’archivage WAL cesse de fonctionner pendant 20 minutes et que l’objectif de perte est cinq minutes, l’alerte doit arriver avant l’incident ou immédiatement lorsque l’objectif est menacé.

Les sommes de contrôle détectent certaines altérations de fichiers, mais elles ne prouvent pas que le contenu restauré respecte les invariants métier. Un test complet peut vérifier la structure, l’existence des objets, les relations, le nombre de lignes, les enregistrements récents et l’ouverture de routes applicatives sur une copie. Les métriques doivent être enregistrées dans un système indépendant de celui qui subit la panne.

Les tests de restauration doivent être réguliers et représenter les scénarios les plus importants. Un test de dump logique vérifie le transfert d’objets; un test de restauration physique vérifie la capacité de récupérer un serveur; un test de PITR vérifie la chaîne des journaux et le choix de la cible; un test de reprise d’application vérifie la connexion, les permissions, les migrations et les fonctions métier. Aucun test unique ne couvre tous les risques.

Un rapport de test utile contient : la méthode, la sauvegarde source, sa date, le serveur ou l’instance cible, la version du moteur, les paramètres requis, le volume restauré, les erreurs, le temps de chaque étape, le nombre de lignes vérifié et le RPO/RTO réellement obtenu. Il doit indiquer les limites et les actions correctives avec un propriétaire et une échéance. Si les mêmes étapes sont répétées manuellement, automatisez-les progressivement, tout en conservant des contrôles de sécurité.

## 10. Scénarios d’incident et décisions de reprise

Lorsqu’une base entière est indisponible à cause de la perte du primaire, le choix peut être une bascule sur une réplique saine si son retard et la cohérence sont acceptables, ou une restauration si aucune réplique appropriée n’existe. Il faut vérifier l’état de la réplication, empêcher un double primaire et contrôler la capacité de la cible. Après le basculement, l’équipe valide les fonctions, les écritures, les sauvegardes et le comportement des clients.

Lorsqu’une suppression accidentelle vient de se produire et que le service reste disponible, une restauration à un point antérieur peut être plus sûre qu’une réparation improvisée. Préservez les preuves, identifiez l’instant de suppression et restaurez dans une instance temporaire. Comparez les lignes, extrayez les données utiles ou reconstruisez l’ensemble selon la procédure approuvée. Ne laissez pas une urgence pousser l’équipe à restaurer directement sur l’unique production avant d’avoir compris les effets.

Lorsqu’une sauvegarde est corrompue ou que des journaux manquent, essayez une autre chaîne connue saine et déterminez l’intervalle réellement récupérable. Ne déclarez pas un RPO atteint parce qu’un fichier existe. Si aucun point compatible n’est disponible, la décision doit inclure le propriétaire métier et les responsables d’incident; il faut consigner la perte et le plan de reconstruction, pas masquer l’écart.

Lorsqu’une compromission est suspectée, la priorité comprend la protection des données et des preuves : révoquer les accès nécessaires, isoler les copies, vérifier les journaux d’audit et utiliser des identifiants de restauration contrôlés. Une sauvegarde postérieure à la compromission peut contenir des données déjà corrompues ou des mécanismes de persistance ajoutés par l’attaquant. Le choix du point doit tenir compte de la date probable de compromission, pas seulement de la sauvegarde la plus récente.

Le rétablissement technique n’est pas synonyme de retour complet au service. Avant la réouverture, validez les données, les droits, les contraintes, les tâches planifiées, les connexions, la réplication, les fonctions critiques et la surveillance. Une base restaurée avec un rôle d’application manquant peut accepter la connexion d’un administrateur tout en échouant pour les utilisateurs. Les tests de fin de reprise doivent refléter les parcours réels.

## 11. Atelier pratique : dump logique et restauration

Dans un environnement où PostgreSQL est installé et accessible, créez une base de laboratoire, chargez quelques tables, puis réalisez une sauvegarde logique. Les commandes supposent que l’identité d’authentification dispose des privilèges nécessaires.

~~~bash
createdb skilltree_backup_lab
pg_dump --format=custom --dbname=skilltree_backup_lab \
  --file=skilltree_backup_lab.dump
pg_restore --list skilltree_backup_lab.dump
createdb skilltree_backup_restore
pg_restore --dbname=skilltree_backup_restore \
  skilltree_backup_lab.dump
~~~

Si la base est vide, créez des tables et données avant la sauvegarde. Vérifiez les clés primaires, les contraintes, la présence des données et les valeurs de référence après restauration. Ajoutez intentionnellement une contrainte UNIQUE et une clé étrangère, puis assurez-vous qu’elles existent après restauration. Testez une requête métier qui relie les apprenants à leurs inscriptions.

La restauration doit être mesurée de façon reproductible. Notez le volume du fichier, le nombre de tables, les temps de sauvegarde et de restauration, le matériel et la version du moteur. Pour un petit jeu de données, le temps n’est pas représentatif d’une très grosse base, mais la méthode et les contrôles le sont. Pour évaluer le RTO, ajoutez les étapes de préparation du serveur et de validation fonctionnelle.

Nettoyez uniquement les ressources de laboratoire dont vous êtes certain qu’elles peuvent être supprimées. Ne réutilisez pas les noms de base de données pour pointer vers un système de production. Ne placez pas de secrets dans les commandes enregistrées. Le test est terminé lorsqu’une restauration complète a été validée, que les journaux de sortie ont été examinés et que les ressources temporaires ont été nettoyées en respectant la politique.

## 12. Atelier conceptuel : préparation d’un PITR

La configuration PITR doit être préparée à l’avance. Il faut activer l’archivage, définir un emplacement ou un système d’archivage durable, vérifier que les archives sont déposées, surveiller leur continuité, conserver une sauvegarde de base et documenter la procédure de récupération correspondant à la version de PostgreSQL. Le paramètre restore_command et le fichier de signal de récupération, par exemple, font partie de la procédure de restauration en PostgreSQL moderne, mais le détail exact doit être confirmé avec la documentation de la version du serveur.

Ne testez pas une cible PITR en inventant une heure au hasard et en supposant que tous les segments sont disponibles. Choisissez un incident simulé, créez une marque temporelle ou utilisez une transaction de test que vous pouvez identifier, puis restaurez la copie dans un environnement isolé. Vérifiez que les modifications précédant l’événement sont présentes et que celles qui lui succèdent ne sont pas incluses selon la cible sélectionnée.

Le test devrait ensuite démarrer l’application contre la base restaurée avec des secrets et des identifiants propres à l’environnement de test. Confirmez que les permissions, fonctions, extensions et migrations correspondent. Prenez une capture du rapport de restauration et stockez les preuves hors de l’environnement temporaire. La démonstration doit pouvoir être répétée par une personne de l’équipe qui n’a pas conçu la procédure initiale.

## 13. Exercices corrigés

### Exercice 1 — Une sauvegarde toutes les nuits suffit-elle?

L’application exige de perdre au plus cinq minutes de données validées. Une sauvegarde complète est réalisée chaque jour à minuit.

**Correction.** Non. Sans journaux de transaction archivés, snapshots fréquents ou autre mécanisme adapté, la dernière sauvegarde peut être jusqu’à presque 24 heures en retard. Il faut compléter le plan par un mécanisme qui permet de récupérer les changements postérieurs au point de sauvegarde et le tester. Les garanties exactes dépendent du moteur et du service.

### Exercice 2 — Réplique et suppression

Une table est supprimée par erreur. Toutes les répliques ont déjà appliqué la suppression.

**Correction.** La réplication n’offre pas de copie historique indépendante. Il faut identifier la dernière heure saine, choisir une sauvegarde et les journaux disponibles, restaurer dans un environnement isolé, puis extraire ou réconcilier les données. Le retour direct de toute la base sur le primaire pourrait effacer des modifications légitimes postérieures à l’erreur.

### Exercice 3 — Fichier dump présent

Le job de sauvegarde indique succès et le fichier est présent. Peut-on affirmer que le RTO est atteint?

**Correction.** Non. La présence du fichier ne prouve ni sa lisibilité ni sa restaurabilité. Il faut faire un test de restauration, vérifier les contraintes et les invariants, mesurer le temps jusqu’au service fonctionnel et documenter les étapes manuelles. Le RTO porte sur le service rétabli, pas sur la fin de la sauvegarde.

### Exercice 4 — Secrets absents en restauration

La base est restaurée, mais l’application échoue à se connecter.

**Correction.** Le plan doit inclure les rôles, permissions, certificats, secrets, paramètres et mécanismes réseau nécessaires. Un dump logique peut ne pas inclure tous les objets globaux ni les secrets de déploiement. Il faut rétablir les composants manquants avec des identifiants propres et sécurisés, vérifier le moindre privilège puis exécuter les tests fonctionnels.

### Exercice 5 — PITR trop récent

Une suppression a été découverte trois jours après. L’équipe conserve les journaux uniquement pendant deux jours.

**Correction.** La chaîne ne couvre plus nécessairement l’instant qui précède l’événement. Le RPO utile pour corriger une corruption détectée tardivement dépend aussi de la capacité à conserver des points sains sur la durée. La rétention doit considérer le délai de détection, les audits et les obligations métier, pas seulement l’intervalle entre les sauvegardes.

## 14. Défi final : plan de reprise pour Skill-Tree

La plateforme a besoin de respecter un RPO de cinq minutes et un RTO de 45 minutes pour les inscriptions et les résultats de quiz. Les utilisateurs peuvent apprendre, passer des examens et obtenir des certificats. Proposez une politique de sauvegarde, un plan PITR, une procédure en cas de suppression accidentelle et une validation post-restauration.

### Correction attendue

1. **Catégoriser les données.** Les résultats de quiz, les inscriptions, les certificats et les éléments de progression qui ne peuvent pas être reconstruits sont critiques. Les caches et certains tableaux de synthèse peuvent être recalculés. Chaque catégorie a une politique explicite de sauvegarde, rétention et reconstruction.

2. **Choisir une méthode.** Utiliser une sauvegarde de base cohérente et un archivage continu des journaux ou un mécanisme managé offrant des garanties équivalentes. Documenter la durée de conservation et vérifier que l’archive est complète. Une sauvegarde logique peut être conservée en complément pour une restauration sélective ou un transfert.

3. **Protéger les copies.** Utiliser un stockage indépendant, des permissions distinctes, un chiffrement et une gestion durable des clés. Tester le chemin de restauration avec les comptes et secrets appropriés. Empêcher qu’un compte applicatif puisse supprimer les sauvegardes.

4. **Préparer l’incident.** En cas de suppression, préserver les journaux et l’état actuel, identifier l’instant de l’erreur, restaurer à une cible antérieure dans une instance séparée et comparer les lignes. Déterminer comment conserver les opérations valides postérieures, puis faire approuver la bascule.

5. **Valider le service.** Contrôler les clés étrangères, le nombre d’inscriptions, les résultats, les certificats, les privilèges et les routes critiques. Tester les connexions applicatives, les files de travaux, les sauvegardes post-reprise et la surveillance. Mesurer le RTO et l’écart de RPO réellement obtenu.

6. **Exercer le plan.** Planifier des restaurations complètes et PITR, relever les temps, corriger les étapes manuelles et mettre à jour la documentation. La procédure doit être exécutable par l’équipe de garde, avec les contacts, rôles et critères de retour clairement définis.

La réussite ne consiste pas à lancer une commande de restauration. Elle consiste à retrouver un état cohérent, à établir l’impact sur les données et les clients, à rétablir un service fonctionnel dans les objectifs convenus et à démontrer cette capacité par des essais répétés.

## 15. Liste de vérification et synthèse

Une stratégie sérieuse définit le RPO, le RTO, les données couvertes, la fréquence des sauvegardes, la rétention, les journaux requis, les supports, les clés, les rôles et les personnes responsables. Elle surveille les échecs et l’espace, teste les restaurations, garde des preuves et couvre les dépendances applicatives. Elle décrit les actions en cas d’erreur logique, de perte de serveur, de corruption, d’attaque et de restauration tardivement nécessaire.

Les sauvegardes logiques sont flexibles et adaptées à l’export de données; les sauvegardes physiques sont souvent mieux adaptées aux grosses bases et aux scénarios de reprise rapides; les journaux de transaction permettent une récupération fine si la chaîne est complète; la réplication vise la continuité mais ne remplace pas la restauration. Le RPO décrit la perte de données acceptée et le RTO le délai de reprise, avec des mesures fondées sur des exercices réels.

## Ressources officielles

- PostgreSQL, sauvegarde et restauration : https://www.postgresql.org/docs/current/backup.html
- PostgreSQL, pg_dump : https://www.postgresql.org/docs/current/app-pgdump.html
- PostgreSQL, pg_restore : https://www.postgresql.org/docs/current/app-pgrestore.html
- PostgreSQL, pg_basebackup : https://www.postgresql.org/docs/current/app-pgbasebackup.html
- PostgreSQL, archivage WAL et récupération à un instant donné : https://www.postgresql.org/docs/current/continuous-archiving.html
- MySQL, sauvegarde et récupération : https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html

Vérifiez la documentation correspondant à la version et au service précis. Les noms des paramètres, les options de commande, les conditions de restauration et les garanties peuvent varier; une procédure de reprise doit donc être versionnée avec l’environnement qu’elle doit restaurer.
