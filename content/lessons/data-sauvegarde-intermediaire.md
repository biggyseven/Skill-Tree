# Backup, PITR et restauration — Intermédiaire

> **Mise en contexte.** Une sauvegarde n’a de valeur que si elle permet de reconstruire un état cohérent dans le délai demandé. La présence d’un fichier, un journal de succès ou une réplication active ne prouvent pas à eux seuls que le service pourra être rétabli après une panne, une corruption, une suppression accidentelle ou une compromission. La restauration à un point dans le temps (PITR, *Point-in-Time Recovery*) permet, lorsque le moteur et sa configuration le supportent, de reconstruire un état antérieur à un instant précis à partir d’une sauvegarde de base et des journaux de changements requis. Ce cours relie les objectifs métier, les familles de sauvegarde, la continuité des journaux, la protection des copies, les tests de restauration et la procédure d’incident. Effectuez tous les ateliers sur des données synthétiques et une cible isolée ; ne restaurez jamais directement sur la production sans approbation et plan contrôlé.

## Objectifs pédagogiques

À la fin du cours, vous pourrez définir RPO et RTO, comparer sauvegardes logiques et physiques, choisir entre sauvegarde complète, différentielle et incrémentale, expliquer le rôle des journaux de transactions, décrire les prérequis de la PITR, établir une politique de rétention, vérifier une archive par une restauration réelle, gérer clés et permissions, et rédiger une procédure de reprise qui prouve que le service peut être remis en état.

Vous devrez aussi distinguer plusieurs scénarios : perte d’un nœud, perte de stockage, suppression logique, corruption silencieuse, erreur applicative, panne de région et compromission de compte. Une seule stratégie ne couvre pas tous ces événements. La solution doit expliciter les hypothèses, le point récupérable, les dépendances requises, le responsable qui autorise la bascule et les preuves nécessaires avant réouverture.

## Prérequis et environnement

Vous devez connaître les bases de données relationnelles, transactions, journaux, comptes, fichiers, réseaux et rôles d’accès. Les procédures exactes diffèrent entre PostgreSQL, MySQL, SQL Server, Oracle et SQLite. Vérifiez toujours la version, les outils, les options et les garanties du moteur installé. Une commande trouvée dans un tutoriel d’un autre SGBD n’est pas une procédure de restauration valide pour votre environnement.

Préparez une base de laboratoire, une cible de restauration distincte, un compte aux privilèges nécessaires et un petit jeu de données synthétiques. Notez la version du moteur, la configuration de journalisation, le format de sauvegarde, le chemin de destination et la procédure de remise à zéro. Ne conservez pas de mots de passe, clés ou jetons dans les scripts, logs ou documents partagés.

## 1. Définir RPO et RTO avec le métier

Le RPO (*Recovery Point Objective*) exprime la perte maximale de données acceptable en cas de reprise, généralement sous forme de durée. Un RPO de quinze minutes signifie que l’organisation cherche à récupérer un état dont les transactions confirmées ne sont pas plus anciennes que la fenêtre tolérée. Le RTO (*Recovery Time Objective*) exprime le délai cible pour rétablir un service utilisable. Un RTO de deux heures inclut davantage que la copie des fichiers : il faut aussi redémarrer les dépendances, vérifier l’intégrité, restaurer les accès et obtenir l’approbation de reprise.

Ces objectifs doivent venir des exigences métier, pas uniquement des possibilités techniques. Le DBA mesure ce qu’il est possible de faire et explique les coûts, mais il ne peut pas décider seul qu’une perte de commandes, de paiements ou de données réglementées est acceptable. Les responsables métier valident l’impact, les fenêtres d’indisponibilité et les priorités de restauration.

Pour chaque application, demandez quelles fonctions doivent revenir en premier, quelles données peuvent être reconstruites, quel retard est acceptable et quelles transactions ne doivent jamais être perdues selon le contrat. Distinguez les services critiques des rapports secondaires. Un tableau de bord analytique peut tolérer une restauration plus tardive que le système de paiement dont il agrège les données. Les dépendances doivent être classées et l’ordre de reprise écrit à l’avance.

## 2. Sauvegarde, haute disponibilité et réplication : trois responsabilités

Une sauvegarde conserve un point de récupération. La réplication copie les changements vers une autre instance ou un autre stockage selon le mécanisme choisi. La haute disponibilité cherche à réduire la durée pendant laquelle le service est indisponible lors d’une panne couverte. Ces capacités se complètent, mais elles ne se remplacent pas.

Une réplique peut recevoir une suppression erronée ou une mise à jour corrompue très rapidement. Elle offre une copie de l’état courant, pas nécessairement un historique exploitable. Une sauvegarde séparée peut préserver un état antérieur, mais la restauration complète peut durer trop longtemps pour répondre à l’objectif de disponibilité. Une solution combine donc, selon le risque, réplication, sauvegardes, journaux archivés, isolation et procédures de bascule.

Les domaines de panne comptent. Deux copies situées sur le même volume, sous le même compte d’administration, restent exposées à certains incidents communs. Pour résister à une compromission, il faut séparer permissions, clés et parfois compte ou domaine de stockage. Pour résister à la perte d’une région, la copie doit se trouver dans un emplacement indépendant approprié. Les choix doivent être testés, car une réplication vers une région distante n’est pas automatiquement une sauvegarde complète.

## 3. Les principales familles de sauvegarde

Une sauvegarde logique exporte des objets et des données vers un format que des outils du moteur peuvent restaurer. Elle peut permettre de récupérer une table ou de migrer des données entre environnements, mais la restauration de gros volumes peut être lente. Vérifiez si elle inclut schéma, séquences, procédures, rôles, privilèges, extensions et autres dépendances nécessaires.

Une sauvegarde physique capture des fichiers ou structures de stockage dans un format pris en charge par le moteur. Elle peut être adaptée à la restauration de grandes bases et à une récupération fondée sur les journaux. Elle impose néanmoins des contraintes de version, de système, de configuration et de cohérence. Copier les fichiers actifs à la main n’est pas une sauvegarde physique valide par définition : il faut un mécanisme cohérent, documenté et supporté.

Une sauvegarde complète fournit un ensemble de base. Une sauvegarde différentielle conserve les modifications depuis une complète précédente. Une sauvegarde incrémentale conserve les changements depuis le point antérieur défini par la chaîne ou le produit. Les terminologies et implémentations diffèrent. Une stratégie incrémentale peut réduire le volume écrit chaque jour, mais la restauration exige un ensemble de fichiers cohérent et l’ordre exact. Une différentielle peut simplifier le nombre de composants à réunir au prix d’un volume croissant jusqu’à la prochaine complète.

Les journaux de transactions conservent des informations permettant la récupération et, dans une configuration appropriée, la reconstruction d’un état dans le temps. Leur rôle et leur format dépendent du moteur. Il faut protéger leur continuité, surveiller leur archivage et garantir que les journaux requis restent disponibles pendant toute la fenêtre de reprise annoncée.

| Famille | Avantage habituel | Limite à prévoir |
|---|---|---|
| Logique | Restauration sélective et portabilité relative | Temps de restauration parfois élevé |
| Physique | Reprise efficace d’un gros volume | Dépendances de version et de configuration |
| Complète | Point de départ autonome plus simple | Volume et durée de capture |
| Différentielle | Chaîne de restauration souvent plus courte | Volume qui grandit entre complètes |
| Incrémentale | Réduit la taille des changements capturés | Chaîne de restauration plus sensible |
| Journaux archivés | Permet une récupération plus précise dans le temps | Continuité et rétention à garantir |
| Réplication | Réduit certaines indisponibilités | Peut reproduire les erreurs logiques |

## 4. Journaux de transactions et PITR

La PITR cherche à reconstruire l’état de la base à un point précis, par exemple avant une suppression accidentelle ou une migration incorrecte. Il faut généralement une sauvegarde de base cohérente et l’ensemble des journaux nécessaires pour faire avancer l’état jusqu’au point souhaité. Un journal absent, corrompu ou issu d’une autre chaîne peut rendre la récupération impossible ou incomplète.

La procédure commence par sélectionner un point de récupération défendable. Utilisez les journaux d’audit, l’heure du commit, les événements métier et les métadonnées du moteur. Le temps doit comporter le fuseau et la source d’horloge ; une heure saisie par un opérateur n’est pas forcément l’instant exact de validation transactionnelle. Choisissez un point antérieur à l’opération fautive, puis validez sur la cible restaurée que l’événement destructeur n’est pas présent et que l’état précédant l’incident l’est.

```mermaid
flowchart LR
    B["Sauvegarde cohérente"] --> R["Restaurer sur cible isolée"]
    J["Journaux archivés continus"] --> P["Rejouer jusqu'au point choisi"]
    R --> P
    P --> Q["Contrôles structurels et métier"]
    Q --> A["Validation applicative"]
    A --> D{"Point approuvé ?"}
    D -->|Oui| S["Préparer la bascule"]
    D -->|Non| I["Choisir un autre point / investiguer"]
```

La PITR n’est pas une réparation automatique d’une donnée qui était déjà fausse avant le point choisi. Si une application a produit des montants incorrects durant plusieurs jours, il faut identifier l’état sain, puis éventuellement rejouer des transactions légitimes postérieures ou appliquer une correction métier. Ce travail doit éviter les doublons et préserver les contraintes ; il nécessite souvent une comparaison entre état restauré et état courant.

Le test de PITR doit couvrir la chaîne complète. Prenez une sauvegarde, créez un marqueur connu, faites une seconde écriture, simulez une opération erronée dans le jeu de laboratoire, puis restaurez avant celle-ci. Confirmez les marqueurs et le point de coupure. Notez le temps, les outils, les erreurs et les vérifications. Une procédure validée une fois devra être rejouée périodiquement et après les changements de version ou de stockage.

## 5. Fréquence, rétention et fenêtres de sauvegarde

La fréquence se déduit du RPO, du volume, du débit de changements, du temps de capture, de la charge sur la source et du coût. Une sauvegarde complète quotidienne seule ne respecte pas un RPO de quinze minutes si les changements entre les captures ne sont pas protégés par un mécanisme supplémentaire. Les journaux archivés peuvent réduire la fenêtre de perte, mais l’archive doit être continue et répliquée vers un stockage durable.

La rétention détermine combien de temps chaque point est conservé. Une période courte économise du stockage, mais peut supprimer le seul point sain avant qu’une corruption découverte tardivement soit signalée. Une rétention longue augmente les coûts et peut entrer en conflit avec les règles de minimisation ou de suppression de données. Définissez des horizons par classe de données et faites approuver les exceptions par les responsables concernés.

La fenêtre de sauvegarde doit éviter les périodes où la charge opérationnelle est critique. Une sauvegarde en ligne peut être possible selon le moteur et la configuration, mais elle doit préserver la cohérence. Mesurez le débit, les I/O, les verrous éventuels, l’espace temporaire et l’effet sur les transactions. Un job qui termine sans erreur mais dégrade fortement l’application peut ne pas respecter l’objectif de service.

La politique doit aussi gérer les échecs. Les retries doivent être bornés, l’échec doit générer une alerte et le prochain point de sauvegarde doit être évalué par rapport au RPO. Une tâche planifiée qui échoue tous les jours sans alerte est une fausse assurance. Surveillez ancienneté du dernier point validé, retard d’archivage, nombre de sauvegardes en erreur et marge restante avant l’objectif de perte.

## 6. Protection des sauvegardes contre la suppression et la compromission

Les copies de secours doivent être séparées des comptes qui exploitent la base. Si une identité compromise peut supprimer base, snapshots et sauvegardes, la protection contre la perte reste limitée. Selon le contexte, utilisez stockage immuable, verrous de rétention, comptes séparés, copies hors ligne, accès d’urgence contrôlé et politiques empêchant la suppression par les identités ordinaires.

La séparation doit être testée, pas seulement décrite. Vérifiez qu’un rôle applicatif ne peut pas effacer les archives, qu’un opérateur courant ne peut pas modifier la rétention sans approbation et qu’un accès d’urgence est journalisé. Les identifiants de sauvegarde doivent être dédiés, limités et renouvelés selon une procédure. Ne partagez pas les clés maîtresses dans les scripts d’automatisation.

Un stockage distinct ne protège pas automatiquement contre les erreurs de rétention, le chiffrement par rançongiciel ou la suppression par un compte d’administration global. Le plan doit identifier le scénario de compromission et les capacités indépendantes permettant de restaurer une copie saine. Les alertes sur suppression, changement de politique et accès inhabituel font partie du contrôle.

## 7. Chiffrement, clés et dépendances de sécurité

Le chiffrement protège certains risques mais introduit une dépendance opérationnelle : la clé doit rester disponible quand la restauration est nécessaire. Une archive chiffrée sans clé utilisable n’est pas récupérable. Stockez les clés dans un système dédié, contrôlez les autorisations, journalisez les usages et documentez comment obtenir la clé pendant une panne d’identité ou de fournisseur.

La rotation des clés exige une compatibilité avec les sauvegardes encore retenues. Vérifiez si les anciens fichiers restent lisibles après rotation, si plusieurs versions de clés sont conservées et si un accès d’urgence est possible. N’associez pas la clé uniquement au même compte, volume ou domaine de sécurité que les archives.

Le test doit utiliser la procédure de récupération des clés prévue, pas une clé toujours disponible dans la session d’un administrateur. L’accès au coffre, l’approbation et le déchiffrement doivent faire partie de l’exercice chronométré. Les logs doivent prouver l’accès sans exposer le secret lui-même.

## 8. Cohérence pendant la capture

Les bases continuent souvent de recevoir des écritures pendant qu’une sauvegarde est produite. Le moteur peut fournir snapshots, journalisation, verrouillage ou outils de sauvegarde en ligne. Utilisez le mécanisme supporté et vérifiez ses prérequis. Copier arbitrairement des fichiers actifs peut créer un ensemble composé de pages provenant de moments incompatibles.

Les données dépendantes ne sont pas toujours stockées dans la même base. Une application peut utiliser un SGBD, des fichiers joints, un stockage objet, une file de messages et une configuration externe. Si la base est restaurée à 10 h 00 mais les fichiers joints à 10 h 30, la relation entre les deux peut être incohérente. Il faut donc documenter les frontières de capture et, quand nécessaire, créer un point de cohérence partagé ou des versions immuables liées.

Pour les sources à haut débit, surveillez le volume et le retard de journaux. Si l’archivage n’arrive plus à suivre, le RPO réel se détériore même si les sauvegardes complètes sont toujours créées. Définissez une alerte et une action quand la chaîne d’archives approche la rétention disponible ou quand l’espace disque requis risque d’être épuisé.

## 9. Vérifier l’intégrité d’une archive

La présence et la taille du fichier sont des vérifications initiales. Un checksum ou une empreinte permet de détecter certains dommages, mais ne prouve pas que l’archive peut être restaurée ni que l’application fonctionnera. La preuve la plus forte est une restauration complétée, accompagnée de contrôles structurels et métier.

La vérification devrait comprendre :
- une restauration dans une cible isolée ;
- l’ouverture par une version de moteur supportée ;
- les contrôles d’intégrité prévus par le produit ;
- la présence des tables, index, fonctions et contraintes requises ;
- le nombre de lignes et les plages de dates attendues ;
- les clés étrangères et les principaux invariants métier ;
- la vérification des rôles, privilèges et accès applicatifs ;
- l’exécution de parcours applicatifs essentiels ;
- le chronométrage complet et la liste des manipulations manuelles.

Les contrôles dépendent du domaine. Une base de logs peut exiger une recherche représentative sur la période attendue ; une base de commandes doit aussi vérifier totaux, liens commande-paiement et transitions d’état. Deux bases avec le même nombre de lignes peuvent avoir des valeurs très différentes. Les rapprochements de mesures et les échantillons par clé complètent donc le simple comptage.

Automatisez les vérifications répétables. Stockez le rapport hors de l’environnement restauré, afin qu’il subsiste si la cible est détruite. Le rapport indique version, point de récupération, sauvegarde, destination, durée, erreurs, contrôles, approbation et limites. Une restauration échouée doit déclencher une action corrective ; elle ne doit pas être ignorée parce que le job de sauvegarde a retourné zéro.

## 10. Dépendances en dehors des données

La restauration de la base ne garantit pas celle de l’application. Il peut manquer comptes et rôles, extensions, procédures, configurations, certificats, secrets, jobs planifiés, fichiers externes, versions de l’application ou paramètres réseau. Certains éléments peuvent être inclus dans la sauvegarde selon le moteur ; d’autres doivent être sauvegardés ou versionnés séparément.

Un plan de reprise doit inventorier ces dépendances et fixer leur ordre. Il faut d’abord disposer du stockage et des clés, puis restaurer le moteur, appliquer les objets et privilèges requis, reconfigurer les connexions, puis lancer les tests applicatifs. Les systèmes amont et aval doivent rester isolés jusqu’à ce que la cible soit validée pour éviter des écritures sur un état non approuvé.

Les artefacts applicatifs et migrations doivent être reproductibles. Ne conservez pas les secrets en clair dans le dépôt. Référencez le coffre et la procédure d’accès d’urgence. Si la version du code dépend d’un schéma particulier, restaurez une version compatible ou appliquez les migrations selon le plan validé.

## 11. Exécuter une restauration en incident

Commencez par déclarer l’incident, limiter les changements non essentiels et préserver les indices. Déterminez le périmètre, l’heure, la dernière version connue saine, les points disponibles et les objectifs de reprise. Évitez de restaurer immédiatement sur le chemin de production si cette action pourrait écraser des données saines ou détruire des preuves nécessaires.

Restaurez dans une cible isolée. Vérifiez l’intégrité, les comptes, les données représentatives et les parcours essentiels. Pour une suppression accidentelle, comparez l’état restauré à l’état courant afin d’identifier les transactions légitimes postérieures qu’il faudrait éventuellement réappliquer. Le rejeu peut violer contraintes ou créer des doublons ; il nécessite des clés idempotentes, des règles de métier et une validation explicite.

La bascule est distincte de la restauration. Préparez routage, DNS, connexions, tâches planifiées et blocage des anciennes écritures si nécessaire. Fixez des critères d’approbation : contrôles de données, tests applicatifs, sécurité, fraîcheur et métriques. Ne réouvrez pas le service uniquement parce que le processus de restauration a terminé.

Après reprise, surveillez erreurs, latence, écritures et éventuels retards. Gardez les preuves de l’incident, communiquez la perte réelle éventuelle et planifiez une revue. Le rapport doit distinguer symptôme, cause technique, facteur organisationnel, délais observés, données perdues, décisions prises et actions de prévention.

## 12. Réplication et modes de panne

Une réplication synchrone peut limiter la perte d’écritures confirmées selon les garanties du produit, mais introduire de la latence ou réduire la disponibilité lorsque le nœud requis n’est pas joignable. Une réplication asynchrone peut réduire la latence mais laisse une fenêtre de retard. Les noms et garanties exactes varient ; n’inférez pas une promesse sans lire la documentation de la version et tester le scénario.

Le mode de panne doit être concret. Perdre un serveur, perdre un volume, perdre la région, corrompre une table, compromettre les identifiants ou supprimer une ligne ne sont pas le même événement. Une bascule vers une réplique peut restaurer le service lors d’une panne matérielle, mais elle peut également reproduire l’erreur logique. Une restauration PITR peut récupérer une suppression, mais le temps et le rejeu des écritures postérieures peuvent rendre le RTO plus long.

Pour chaque mode, écrivez la source de vérité, le point de récupération, le processus d’autorisation, le contrôle de cohérence et le retour arrière. Les exercices doivent inclure au moins une perte de nœud, une erreur logique et une récupération à partir d’une copie indépendante si la criticité le justifie.

## 13. Procédure de PITR : exemple pédagogique

Supposons une table de laboratoire `recovery_demo`. Vous écrivez un marqueur avant sauvegarde, réalisez la sauvegarde, écrivez un second marqueur, puis simulez une suppression accidentelle. La procédure dépend du moteur, mais le contrat de test reste stable : restaurer une cible au point antérieur à l’opération destructive, vérifier le marqueur initial, confirmer que la suppression n’a pas affecté l’état restauré et consigner l’intervalle de perte.

```sql
CREATE TABLE recovery_demo (
    event_id INTEGER PRIMARY KEY,
    label TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

INSERT INTO recovery_demo (event_id, label, created_at)
VALUES (1, 'avant sauvegarde', CURRENT_TIMESTAMP);
```

Après la sauvegarde, insérez une seconde ligne, notez l’heure du commit et exécutez sur les données fictives une opération d’erreur contrôlée. Utilisez les outils officiels du moteur pour restaurer la cible. Ne copiez pas ces instructions SQL comme procédure de sauvegarde : elles illustrent les marqueurs métier du test, tandis que la commande de sauvegarde dépend du produit.

Vérifiez l’état obtenu et notez la durée du processus complet. Si le point restauré contient la suppression fautive, le point ou la chaîne sélectionnée n’est pas correct. Si le marqueur attendu manque, la sauvegarde ou les journaux ne couvrent pas la fenêtre. Recommencez sur une cible propre après avoir identifié la cause.

## 14. Atelier pratique guidé : concevoir et tester une stratégie

### Scénario

Une application de commandes doit conserver les transactions et retrouver un état antérieur à une suppression accidentelle. Le responsable métier demande un RPO de quinze minutes et un RTO de deux heures. Votre travail consiste à traduire ces objectifs en procédure et à démontrer la restauration sur une instance de laboratoire.

### Étape A — Définir le périmètre

Identifiez base, schéma, pièces jointes, comptes, extensions, scripts, clés, dépendances et fonctions essentielles. Établissez quelles données sont incluses, quelles données peuvent être reconstruites et quels systèmes doivent être rétablis en premier. Validez RPO et RTO avec le propriétaire métier.

### Étape B — Choisir une stratégie adaptée au moteur

Choisissez une sauvegarde de base cohérente, un mécanisme de journaux si une PITR est exigée et un stockage indépendant adapté. Notez fréquence, durée, rétention, permissions, clés, seuils d’alerte et procédure en cas d’archive manquante. Utilisez les commandes documentées pour le moteur installé.

### Étape C — Vérifier la sauvegarde

Créez la copie, confirmez l’état et les métadonnées, puis restaurez dans une cible isolée. Le test doit se faire avec la procédure et les identifiants d’urgence normalement prévus. Mesurez durée de capture, transfert, restauration et contrôle.

### Étape D — Simuler une erreur

Insérez des marqueurs, prenez une sauvegarde, effectuez des changements après la sauvegarde puis simulez une suppression sur le jeu synthétique. Identifiez le point antérieur et restaurez. Si des écritures légitimes ont eu lieu après le point de reprise, déterminez comment les préserver ou les rejouer sans double comptage.

### Étape E — Valider la reprise

Contrôlez intégrité, volume, clés, comptes, accès et parcours applicatifs. Chronométrez jusqu’à l’état où les utilisateurs peuvent reprendre leur travail, pas seulement jusqu’à la fin de la restauration du fichier. Préparez une décision de bascule et une surveillance post-reprise.

### Critères d’acceptation

Le laboratoire est réussi si le point attendu peut être restauré, les contrôles prouvent son contenu, l’accès aux clés fonctionne, le RPO/RTO est mesuré et la procédure peut être suivie par une autre personne. La remise contient la version du moteur, les commandes adaptées à l’environnement, les résultats, les erreurs, les risques et le plan de retour.

## 15. Étude de cas : suppression accidentelle en production

### Symptôme

Un opérateur valide un DELETE sans le filtre prévu. La réplication est active, la base reste en ligne et plusieurs écritures légitimes ont lieu après la suppression. Une simple restauration complète ferait perdre ces écritures postérieures.

### Investigation

Identifiez la table, la population affectée et l’heure de la transaction destructive. Préservez les logs et auditez les changements. Vérifiez les sauvegardes et journaux disponibles. Restaurez un état pré-incident sur une cible isolée, puis comparez les lignes manquantes à la base courante. N’écrasez pas la source tant que la portée n’est pas connue.

### Correction

Une réparation sélective peut être possible en exportant les lignes restaurées et en les réinsérant selon une procédure contrôlée, mais il faut également reconstruire les références et gérer les identifiants. Si les données postérieures ont modifié ces lignes, une simple réinsertion peut être incorrecte. L’équipe métier doit approuver la stratégie et les contrôles. Une restauration complète avec rejeu d’événements peut être préférable pour certains scénarios.

### Prévention

Limitez les privilèges de suppression, utilisez des comptes d’administration séparés, imposez une revue des opérations destructives, testez les scripts sur un jeu représentatif et configurez une procédure de rollback quand elle est disponible. Ajoutez un contrôle préventif pour les opérations sans filtre lorsque le moteur et les outils le permettent. La prévention ne remplace pas la sauvegarde vérifiée.

## 16. Exercices avec corrigés

### Exercice 1 — Les sauvegardes sont quotidiennes alors que le RPO est de quinze minutes. Est-ce cohérent ?

**Correction.** Non, pas sans un mécanisme complémentaire qui couvre les transactions entre deux captures. Une archive continue de journaux ou une fréquence compatible peut permettre une récupération plus fine, selon le moteur. Il faut tester la chaîne et mesurer le point le plus récent réellement restaurable.

### Exercice 2 — Une réplique saine suffit-elle pour récupérer une suppression erronée ?

**Correction.** Non. La suppression peut être répliquée vers le secondaire. Il faut un point antérieur ou une méthode d’historique capable de reconstruire les lignes, puis valider les changements légitimes postérieurs. Une réplique et une sauvegarde remplissent des rôles distincts.

### Exercice 3 — Un checksum est correct, mais la restauration échoue. Pourquoi ?

**Correction.** L’empreinte indique que le fichier correspond à l’empreinte calculée, pas qu’il est compatible avec la version du moteur, complet dans sa chaîne de journaux ou accompagné des dépendances nécessaires. La seule preuve opérationnelle est une restauration valide avec contrôles.

### Exercice 4 — Le fichier est restauré en trente minutes, mais le service revient en quatre heures. Le RTO est-il respecté ?

**Correction.** Si le RTO porte sur le service utilisable, non. Il inclut configuration, identités, réseau, tests, validation et bascule. Les exercices doivent chronométrer l’ensemble de la procédure.

### Exercice 5 — Pourquoi le point PITR ne doit-il pas être choisi uniquement à partir de l’horloge d’un opérateur ?

**Correction.** Les horloges peuvent différer et l’instant de saisie peut ne pas correspondre au commit. Utilisez journaux, identifiants de transaction ou indices du moteur, consignez fuseau et source temporelle puis validez sur l’état restauré.

### Exercice 6 — Une archive chiffrée est-elle récupérable si la clé est perdue ?

**Correction.** Pas nécessairement. Les clés, leurs versions et la procédure d’urgence font partie du plan de sauvegarde. Testez l’accès avec les identités de reprise prévues et gardez la clé séparée des données selon la politique de sécurité.

## 17. Défi final : documenter un plan de reprise exploitable

Une application conserve commandes et paiements. Le métier demande un RPO de cinq minutes et un RTO de quatre-vingt-dix minutes. La base croît quotidiennement, les sauvegardes sont chiffrées et une équipe de trois personnes assure le service.

### Corrigé attendu

Validez les objectifs avec les propriétaires métier et classez les scénarios de panne. Choisissez une sauvegarde cohérente et une chaîne de journaux compatible avec le RPO ; mesurez le retard maximal et surveillez la continuité. La fréquence, la rétention et l’espace nécessaire doivent être dérivés du volume de changement, pas d’une estimation optimiste.

Séparez les archives, les identités d’administration et les clés. Restreignez la suppression, surveillez les changements de politique et testez l’accès d’urgence. Inventoriez version de moteur, extensions, rôles, schémas, certificats, scripts et dépendances. Automatisez vérification de présence, âge de dernière sauvegarde, chaîne de journaux et tests de restauration.

La procédure décrit l’incident, la sélection du point, la restauration en cible isolée, les contrôles structurels et métier, la reconstruction de dépendances, la décision de bascule et la surveillance. L’exercice RTO doit inclure coordination, accès aux clés et approbation, et pas seulement une opération automatisée. Réservez une marge pour les erreurs et les retards.

Pour respecter le RPO, prouvez que le dernier journal disponible permet de reconstruire l’état requis et définissez quoi faire si l’archive est interrompue. Pour respecter le RTO, entraînez l’équipe avec une procédure suivie par un opérateur qui ne l’a pas écrite. Ajoutez une solution de repli si la personne ou le compte d’urgence habituel n’est pas disponible.

La remise finale contient architecture, planning, rétention, droits, clés, métriques, seuils, commande par moteur, contrôles attendus, critères de bascule, risques résiduels et date du prochain exercice. Le plan est accepté quand les preuves montrent que la récupération est possible, pas lorsqu’un document affirme qu’elle le sera.

## 18. Erreurs à éviter

**Confondre la réplication et une sauvegarde.** Une erreur logique peut être répliquée. Gardez des points de récupération isolés et testés.

**Croire qu’un job de sauvegarde vert prouve la restaurabilité.** Seule une restauration complète et contrôlée fournit cette preuve.

**Oublier les clés et dépendances.** Les données chiffrées ou une base sans extensions, rôles et secrets requis peuvent être inutilisables.

**Ignorer la chaîne de journaux.** Une sauvegarde de base ne suffit pas pour toute PITR si les journaux requis sont absents.

**Restaurer directement en production sans validation.** La cible isolée préserve les preuves et permet de comparer l’état récupéré avant bascule.

**Utiliser des sauvegardes de test contenant des données sensibles sans protection.** La restauration déplace aussi les obligations de sécurité et de rétention.

**Ne pas exercer l’équipe.** Une procédure non testée cache souvent des dépendances, des autorisations expirées ou des durées irréalistes.

## 19. Checklist avant incident et avant reprise

- [ ] RPO, RTO et périmètre ont été validés par les responsables métier.
- [ ] Types de sauvegarde, fréquences, rétention et dépendances sont documentés.
- [ ] La continuité des journaux nécessaires à PITR est surveillée.
- [ ] Les copies sont séparées du domaine de panne et protégées contre la suppression.
- [ ] Les clés peuvent être récupérées par un processus d’urgence testé.
- [ ] Les versions du moteur, extensions, rôles et artefacts sont inventoriés.
- [ ] Les tests de restauration mesurent intégrité, accès et durée complète.
- [ ] Le point de récupération est justifié avec des preuves temporelles.
- [ ] Les écritures légitimes postérieures sont considérées avant réparation.
- [ ] Une autorité et des critères de bascule sont explicitement définis.
- [ ] Les logs et rapports restent disponibles pendant l’incident.
- [ ] Les actions correctives et le prochain exercice sont assignés.

## Conclusion

Une stratégie de sauvegarde est un système de récupération et pas un calendrier de fichiers. Elle associe RPO/RTO, sauvegarde cohérente, journaux, chiffrement, séparation des accès, rétention, dépendances, contrôles et exercice humain. La PITR apporte une précision temporelle quand le moteur et la chaîne d’archives le permettent, mais la restauration doit rester sur une cible isolée jusqu’à validation. Le seul moyen crédible de démontrer la récupérabilité consiste à restaurer régulièrement, vérifier l’état obtenu et mesurer le temps nécessaire pour que le service redevienne réellement utilisable.


## Complément expert : capacité, audit et amélioration continue

### Dimensionner la chaîne de sauvegarde

La capacité nécessaire dépend de la taille de base, de la croissance, du taux de changement, de la compression, de la durée de rétention et des copies supplémentaires. Un volume de stockage égal à la taille actuelle de la base n’est généralement pas une estimation suffisante : il faut prévoir les sauvegardes complètes simultanées, les incrémentales, les journaux, les fichiers temporaires de restauration, les copies régionales et une marge de fonctionnement.

Mesurez le débit de capture, la quantité de journaux générés, le retard d’archivage et la vitesse de restauration. Un backup peut terminer correctement mais produire un transfert trop lent pour alimenter la chaîne de reprise. La vitesse de lecture et d’écriture de la cible, le réseau, le chiffrement et la compression peuvent tous faire varier le temps. Les mesures doivent être collectées dans des conditions réalistes.

### Gestion du cycle de vie et des anciennes versions

Le nettoyage des anciennes sauvegardes doit être gouverné et vérifié. Une erreur de sélection peut supprimer les derniers points sains ou une archive requise pour une PITR. La procédure doit déterminer les dépendances : une sauvegarde incrémentale peut dépendre d’une complète plus ancienne, et des journaux peuvent n’être utiles qu’avec cette base précise. Il faut appliquer la politique de rétention tout en conservant les chaînes nécessaires aux points encore annoncés comme restaurables.

Avant un nettoyage, contrôlez le manifeste, la chaîne de dépendances et l’existence d’un point plus récent validé. Les opérations destructives de rétention doivent être journalisées, limitées et testées. Une copie retenue pour une obligation ou un incident ne doit pas être purgée automatiquement sans validation.

### Auditabilité et preuves

Le rapport de sauvegarde doit contenir l’identité de la base, la version du moteur, le point de capture, la méthode, le résultat, la taille, la durée et l’emplacement protégé. Il ne doit pas contenir de secrets. Le rapport de restauration ajoute la cible, le point choisi, les journaux appliqués, les vérifications, les anomalies et la décision de reprise.

Pour une enquête, les preuves doivent distinguer ce qui a été observé, ce qui est supposé et ce qui reste inconnu. Un indicateur de succès ne doit pas être présenté comme une preuve d’intégrité métier. Les décisions de restauration et le rejeu d’écritures postérieures doivent porter l’identité de l’approbateur, le périmètre touché et le résultat de validation.

### Tester les risques de corruption silencieuse

Une corruption peut ne pas faire échouer immédiatement le service. Les données peuvent continuer à être lues tout en renvoyant un contenu incorrect ou en omettant une partie de la population. Choisissez des contrôles de cohérence métier, comme totaux, relations, comptes par période et échantillons de clés critiques. Pour les données financières, faites valider les rapprochements par le propriétaire métier.

Des tests périodiques doivent inclure plus qu’un démarrage du moteur : requêtes représentatives, contraintes, permissions, données historiques, séquences et interactions applicatives. Conservez une base de référence et expliquez les écarts saisonniers. Une variation de total peut être légitime ; elle exige une explication plutôt qu’une correction automatique.

### Apprendre après un exercice ou un incident

Après chaque test, comparez le RPO et le RTO effectivement obtenus aux objectifs. Relevez la durée d’accès aux clés, la récupération des permissions, les tâches manuelles, les problèmes de réseau et les étapes qui dépendent d’une seule personne. Attribuez les améliorations et vérifiez qu’elles sont terminées avant le prochain exercice.

La procédure doit évoluer avec le produit. Une nouvelle version de moteur, un nouveau stockage, une rotation de clés, une modification de schéma ou un changement du fournisseur peut invalider un plan qui fonctionnait auparavant. Déclenchez donc un test de restauration après les changements importants, sans attendre la prochaine date périodique.

### Critères de maturité

Une organisation mature peut démontrer à tout moment quel est son dernier point sain, combien de temps il faudrait pour le restaurer, qui peut autoriser la reprise, comment récupérer les clés et quelles preuves valident l’intégrité. Elle sait aussi identifier ses limites : un RPO non mesuré, un journal incomplet ou une clé non testée signifie que l’objectif n’est pas prouvé. Mieux vaut signaler explicitement cet écart que déclarer un niveau de protection que les tests ne soutiennent pas.
