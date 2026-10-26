# Sécurité Active Directory

> **Mise en contexte**
>
> Active Directory Domain Services (AD DS) centralise l'identité et l'accès à de nombreuses ressources Windows : comptes, groupes, ordinateurs, politiques de sécurité et authentification. Cette centralisation simplifie l'administration, mais rend également l'annuaire extrêmement sensible. Une identité ou un serveur capable de modifier les comptes privilégiés, les contrôleurs de domaine ou les politiques qui leur sont appliquées peut avoir un impact sur une grande partie de l'organisation.
>
> La sécurité d'Active Directory ne consiste pas seulement à protéger le compte Domain Admins. Elle exige un modèle d'administration séparé, des contrôleurs de domaine durcis, des droits de délégation maîtrisés, une authentification robuste, la surveillance des modifications, la protection des sauvegardes et une récupération testée. Ce cours présente les principes et les contrôles de façon défensive, avec des commandes d'inventaire et d'audit à exécuter uniquement dans un domaine que tu es autorisé à administrer.

## 1. Objectifs et périmètre

À la fin du cours, tu dois pouvoir décrire la structure d'un domaine AD DS, distinguer forêt, domaine, unité d'organisation, groupe et objet, comprendre l'authentification Kerberos, identifier les comptes et groupes sensibles, appliquer un modèle d'administration par niveaux, réduire les privilèges, sécuriser les GPO, contrôler la délégation, mettre en place Windows LAPS, préparer le renforcement de LDAP et surveiller les événements utiles.

Tu apprendras aussi à sécuriser les contrôleurs de domaine, les services DNS et SYSVOL, à comprendre les risques liés aux comptes de service et aux SPN, à examiner les délégations Kerberos, à gouverner les modèles de certificats AD CS, à protéger la réplication et les sauvegardes et à réagir à une suspicion de compromission. Ce cours ne remplace pas le plan de changement et de reprise de ton organisation : une mauvaise modification d'AD peut perturber l'authentification, les applications et l'administration de tout le domaine.

L'objectif opérationnel est de réduire les chemins par lesquels un poste utilisateur, un compte de service ou un serveur membre pourrait influencer les identités privilégiées. Il faut également préserver la disponibilité : les politiques de sécurité doivent être testées avec des clients représentatifs, documentées, observées avant enforcement lorsque la compatibilité le nécessite et accompagnées d'une méthode de retour arrière.

~~~text
                 OBJECTIFS DE SECURITE AD
+-------------------------------------------------------------+
| Identite : comptes, groupes, MFA, lifecycle                 |
+-------------------------------------------------------------+
| Administration : tiers de confiance, postes privilegies     |
+-------------------------------------------------------------+
| Annuaire : ACL, OU, delegation, GPO, replication             |
+-------------------------------------------------------------+
| Protocoles : Kerberos, LDAP, SMB, NTLM sous controle        |
+-------------------------------------------------------------+
| Infrastructure : DC, DNS, SYSVOL, AD CS, sauvegardes         |
+-------------------------------------------------------------+
| Detection : journaux, changements, alertes, recovery         |
+-------------------------------------------------------------+
~~~

## 2. Comprendre les composants Active Directory

AD DS est un service d'annuaire utilisé pour stocker des objets et leurs attributs, fournir des services d'authentification et d'autorisation et distribuer des politiques. Les objets fréquents sont utilisateurs, groupes, ordinateurs, unités d'organisation, contacts et objets de stratégie de groupe. L'identité d'un utilisateur est représentée par plusieurs attributs et identifiants ; son nom d'affichage n'est pas l'identifiant de sécurité principal utilisé pour les permissions.

Une forêt constitue une frontière administrative et de sécurité importante. Elle contient un ou plusieurs domaines partageant un schéma et un catalogue global. Un domaine organise une partie de l'espace de noms et la base d'objets associée. Les unités d'organisation (OU) permettent notamment d'organiser les objets et d'appliquer ou déléguer l'administration ; elles ne constituent pas automatiquement une frontière de sécurité contre un administrateur du domaine.

~~~text
FORET : exemple.corp
|
+-- Domaine : exemple.corp
|   +-- OU=Users
|   +-- OU=Workstations
|   +-- OU=Servers
|   +-- OU=Domain Controllers
|
+-- Domaine enfant : europe.exemple.corp
    +-- OU=Users
    +-- OU=Servers

Les approbations et les droits entre domaines doivent etre explicites et audites.
~~~

Les contrôleurs de domaine (DC) hébergent AD DS et assurent notamment l'authentification et la réplication. Ils doivent être considérés comme des actifs critiques : un administrateur capable de prendre le contrôle d'un DC peut potentiellement modifier l'annuaire et influencer les identités. Il faut limiter leurs rôles, leur exposition réseau, les logiciels installés et les identités qui s'y connectent.

Le catalogue global facilite certaines recherches et résolutions à l'échelle de la forêt. DNS est indispensable à la découverte des services AD : les clients recherchent notamment des enregistrements SRV pour localiser les contrôleurs appropriés. Une configuration DNS inadéquate peut faire échouer les connexions et encourager des contournements dangereux.

## 3. Menaces et chemins de compromission

Les attaques contre AD commencent souvent par la compromission d'un poste utilisateur, le vol de justificatifs, l'abus de droits d'administration, un mot de passe réutilisé ou une application vulnérable. Le risque augmente quand un administrateur utilise son compte privilégié sur un poste bureautique, quand des mots de passe locaux sont partagés, quand un compte de service dispose de droits excessifs ou quand une GPO peut être modifiée par un groupe trop large.

Un chemin de compromission peut être indirect. Un compte qui ne fait pas partie de Domain Admins peut disposer d'une ACL qui modifie un groupe privilégié, un objet ordinateur ou une GPO appliquée à des serveurs sensibles. L'examen doit donc aller au-delà de la liste des membres des groupes les plus connus.

~~~text
[Poste utilisateur compromis]
            |
            v
[Identifiants / session / secret exposé]
            |
            v
[Compte avec droit excessif ou delegation faible]
            |
            v
[Modification GPO / groupe / compte / service]
            |
            v
[Acces a des serveurs privilegies ou au plan identite]
            |
            v
[Impact etendu sur le domaine]

Barriere cle : moindre privilege + tiers de confiance + detection.
~~~

Une évaluation de sécurité doit cartographier les actifs, les identités, les permissions effectives et les dépendances. Un groupe vide aujourd'hui peut devenir dangereux après un changement ; une GPO peut être sensible même si son nom semble inoffensif ; une identité technique peut avoir des droits accumulés au fil des ans.

## 4. Modèle d'administration par niveaux

Le modèle par niveaux de confiance sépare les systèmes, les comptes et les postes en fonction de ce qu'ils peuvent administrer. Dans un modèle classique à trois niveaux, Tier 0 représente le plan de contrôle de l'identité et les systèmes qui peuvent le compromettre ; Tier 1 regroupe l'administration des serveurs et applications d'entreprise ; Tier 2 couvre les postes et les comptes utilisateurs.

La classification doit suivre le contrôle réel, pas seulement la fonction visible ou la sous-unité organisationnelle. Un serveur de sauvegarde, un hyperviseur ou un outil EDR qui peut lire ou modifier les contrôleurs de domaine peut relever du Tier 0. Un poste utilisé pour administrer un DC hérite du niveau de confiance requis pour cette tâche. Les noms de tier peuvent varier selon l'architecture, mais les frontières de confiance restent essentielles.

~~~text
TIER 0 : PLAN IDENTITE
[DC] [AD CS critique] [identites Tier 0] [outil gerant les DC]
             ^
             | administration depuis poste privilegie Tier 0
             |
TIER 1 : SERVEURS / APPLICATIONS
[serveurs membres] [bases] [apps metier]
             ^
             | administration depuis poste Tier 1
             |
TIER 2 : POSTES / UTILISATEURS
[PC bureautiques] [helpdesk postes] [comptes standards]

Aucun secret de Tier superieur ne doit etre saisi sur un hote de tier inferieur.
~~~

Évite les connexions quotidiennes au courrier, au Web ou aux applications bureautiques avec un compte très privilégié. Utilise des comptes séparés par rôle, des postes d'administration dédiés et un chemin d'accès contrôlé. N'utilise pas un compte Domain Admin pour une opération simple qui peut être réalisée par un groupe délégué plus limité.

Le modèle par tiers ne se limite pas à créer des OU ou des groupes. Il faut contrôler les logons, les chemins d'administration, les privilèges locaux, les outils d'administration, les sauvegardes, la supervision et la chaîne de déploiement. Si un outil de gestion de serveurs possède des droits de contrôle sur les DC, il doit être protégé au niveau correspondant.

## 5. Comptes sensibles et moindre privilège

Les groupes intégrés Domain Admins, Enterprise Admins et Administrators ont des pouvoirs très étendus, mais d'autres groupes et ACL peuvent également créer des capacités importantes. Il faut examiner les membres permanents et temporaires, les groupes imbriqués, les droits délégués et les identités de service. La liste des membres directs ne décrit pas toujours l'ensemble des privilèges effectifs.

~~~powershell
# Inventaire en lecture seule dans une session PowerShell avec le module ActiveDirectory
Get-ADGroupMember "Domain Admins" -Recursive
Get-ADGroupMember "Enterprise Admins" -Recursive
Get-ADGroupMember "Administrators" -Recursive
Get-ADUser -Filter * -Properties Enabled,PasswordLastSet,LastLogonDate |
  Select-Object SamAccountName,Enabled,PasswordLastSet,LastLogonDate
~~~

Exécute ces commandes dans un environnement autorisé et avec le module RSAT ActiveDirectory installé. Les noms des groupes localisés peuvent varier ; le SID et les groupes effectifs doivent être vérifiés lorsque le domaine n'utilise pas les noms anglais. Les dates de dernière connexion ne constituent pas à elles seules une preuve fiable d'inactivité : elles peuvent être répliquées avec des limites de précision ou ne pas représenter l'utilisation de tous les services.

Un compte privilégié doit être nominatif, justifié, séparé du compte de travail quotidien et revu à intervalle défini. Limite le nombre de personnes qui peuvent approuver et exécuter les changements les plus sensibles. L'accès permanent doit être réduit lorsque des mécanismes d'élévation temporaire approuvés sont disponibles.

~~~text
Demande privilegiee
       |
       v
Besoin + role + duree + approbateur
       |
       v
Attribution minimale et limitee
       |
       v
Action admin tracee
       |
       v
Expiration / retrait / revue
~~~

N'ajoute pas automatiquement tous les administrateurs à tous les groupes privilégiés. Un opérateur de sauvegarde, un administrateur de postes et un administrateur de DC ont des besoins distincts. Les droits doivent être définis à partir du rôle, contrôlés régulièrement et retirés quand le besoin disparaît.

## 6. Comptes de service, gMSA et secrets

Les comptes de service peuvent être utilisés par des applications, planificateurs, agents de supervision, services de sauvegarde ou scripts. Les mots de passe statiques, les identifiants partagés et les comptes réutilisés sur de nombreux serveurs créent un fort rayon d'impact. Si un même secret est présent sur un serveur membre et un actif Tier 0, le serveur membre peut devenir un chemin de compromission vers l'identité.

Lorsque les applications et versions le supportent, les comptes de service gérés de groupe (gMSA) peuvent automatiser la gestion du mot de passe et réduire les opérations manuelles. Ils ne suppriment pas le besoin de contrôler les droits, les hôtes autorisés à récupérer le secret géré, les permissions du service et la surveillance. Vérifie la compatibilité avant migration et ne partage pas un gMSA entre des niveaux de confiance incompatibles.

~~~text
Compte de service
    |
    +--> proprietaire applicatif identifie
    +--> hotes autorises connus
    +--> droits AD et locaux minimaux
    +--> aucune appartenance privilegiee sans justification
    +--> rotation / expiration / procedure de retrait
    +--> journaux et dependances documentes
~~~

Recherche les secrets dans les scripts, tâches planifiées, fichiers de configuration, jobs d'automatisation et systèmes de supervision. Ne collecte pas les mots de passe en clair dans un inventaire. Si un secret a été exposé, révoque-le, identifie les services qui en dépendent, remplace-le et vérifie l'absence d'usage de l'ancienne valeur.

Les comptes de service doivent avoir un propriétaire métier et un propriétaire technique, une finalité, une durée de revue et une procédure de rotation. Les comptes orphelins, les comptes qui peuvent se connecter interactivement sans raison et les comptes dont les droits ont accumulé des exceptions doivent être examinés en priorité.

## 7. Kerberos, NTLM et protection des justificatifs

Kerberos est le protocole d'authentification utilisé couramment dans un domaine AD. Le client obtient un ticket initial auprès du KDC, puis utilise un ticket de service pour accéder à une ressource. L'horloge, le DNS, la découverte du contrôleur et les identités SPN font partie des dépendances. Un problème de temps ou de nommage peut entraîner un échec d'authentification.

~~~text
[Client]
   | demande initiale
   v
[KDC / service Kerberos sur le DC]
   | TGT (ticket-granting ticket)
   v
[Client]
   | demande ticket pour SPN du service
   v
[KDC]
   | ticket de service
   v
[Client] ------------------> [Service cible]
        ticket de service + authentification mutuelle selon contexte
~~~

Le TGT permet de demander des tickets de service pendant sa validité ; il n'est pas le mot de passe et ne doit pas être confondu avec une session d'accès à toutes les ressources. Les tickets et secrets restent sensibles, et leur exposition doit être limitée en protégeant les postes, les processus et les comptes.

NTLM est un mécanisme historique encore présent dans certains environnements, mais il doit être traité comme une dépendance à inventorier et à réduire selon la compatibilité. Avant de restreindre ou bloquer NTLM, collecte les événements, identifie les applications et appareils qui en dépendent, teste les remplacements et suit le plan de migration. Une désactivation impréparée peut interrompre l'authentification de systèmes anciens.

Ne confonds pas la désactivation d'un protocole d'authentification avec la suppression de tous les risques liés aux identifiants. Les mots de passe faibles, les services mal configurés, les privilèges excessifs et les hôtes compromis restent des risques même lorsque Kerberos fonctionne correctement.

## 8. SPN, délégation et comptes d'application

Un Service Principal Name (SPN) associe une identité de service à un nom utilisé par Kerberos. Les SPN doivent être cohérents avec les applications et leurs comptes. Des SPN dupliqués ou attribués à la mauvaise identité peuvent provoquer des problèmes d'authentification et compliquer le diagnostic.

~~~powershell
setspn -Q HTTP/app.exemple.corp
setspn -L compte_service
setspn -X
~~~

Ces commandes interrogent les SPN dans un domaine accessible, listent ceux d'un compte et recherchent les doublons selon les capacités disponibles. Elles sont utilisées ici en lecture seule. Avant une modification, identifie le propriétaire de l'application, confirme les noms et teste dans un environnement représentatif ; un changement erroné peut provoquer une panne Kerberos.

La délégation Kerberos permet à un service de représenter un utilisateur ou d'utiliser des identifiants pour accéder à un service en aval dans certains scénarios. Elle est parfois nécessaire pour une application à plusieurs couches, mais les permissions de délégation doivent être limitées et documentées. Les paramètres de délégation non contrainte méritent une revue attentive. Les options de délégation contrainte et de ressource nécessitent également un modèle d'identité et de service précis.

~~~text
Utilisateur --> Front-end --> Service back-end
                 |
                 v
         Delegation Kerberos ?
                 |
           +-----+-----+
           |           |
         limitee     trop large
           |           |
           v           v
  service cible precise  risque d'abus et d'exposition
~~~

La correction consiste à comprendre l'application, inventorier les services et leurs SPN, choisir la forme de délégation minimale supportée, vérifier les comptes et tester les accès. N'active pas la délégation non contrainte comme solution rapide à une erreur de double saut ; elle peut modifier fortement le modèle de risque.

## 9. OU, ACL, délégation d'administration

Les unités d'organisation facilitent le regroupement d'objets, l'application de GPO et la délégation de certaines opérations. La structure des OU doit soutenir l'administration et le cycle de vie des appareils, pas seulement représenter l'organigramme. Déplacer des objets peut changer leur héritage de stratégie et affecter des dépendances applicatives.

Les ACL de l'annuaire définissent qui peut lire, modifier, supprimer ou gérer des objets et attributs. Il faut porter attention aux droits de modification sur les groupes privilégiés, les comptes, les GPO, les OU et les objets d'identité critiques. Un compte ne faisant pas partie d'un groupe privilégié peut tout de même disposer d'un droit dangereux via une ACL ou un groupe imbriqué.

~~~text
[Objet AD / OU / groupe / GPO]
            |
            v
[ACL explicite + héritage + groupes imbriqués]
            |
            v
[Qui peut lire / modifier / supprimer / prendre controle ?]
            |
            v
[Compare au role attendu et au proprietaire]
            |
            v
[Retirer les droits excessifs, tester, journaliser]
~~~

La délégation d'une tâche de support doit être étroite : par exemple, réinitialiser des mots de passe dans une OU déterminée n'implique pas de pouvoir modifier les appartenances des groupes privilégiés. Les permissions doivent être documentées, revues et testées avec les identités concernées.

Évite les changements de permissions sur le conteneur racine du domaine sans analyse des héritages et de la portée. Les opérations de sécurité sur les ACL doivent être planifiées, exportées ou documentées avant modification, et validées par une méthode indépendante. Une ACL trop large peut créer un risque durable, tandis qu'une suppression en masse peut casser des services essentiels.

## 10. GPO : gestion du changement et protection

Les stratégies de groupe (GPO) appliquent des paramètres aux utilisateurs et ordinateurs dans une portée déterminée par le lien, l'héritage, le filtrage de sécurité et les filtres WMI. Les paramètres peuvent contrôler le pare-feu, l'audit, les mots de passe, les scripts, les restrictions d'accès et de nombreux autres composants.

La capacité de modifier une GPO liée à des systèmes privilégiés est une autorité sensible. Une GPO peut modifier des paramètres de sécurité ou exécuter des scripts dans un contexte important. Contrôle qui peut créer, modifier, lier et supprimer les GPO, ainsi que les permissions sur les fichiers de stratégie stockés dans SYSVOL.

~~~text
[Creation / modification de GPO]
             |
             v
[ACL de la GPO + ACL du lien OU / domaine]
             |
             v
[Filtrage de securite + WMI + heritage]
             |
             v
[Ordinateurs et utilisateurs cibles]
             |
             v
[Parametres appliques + verification resultat]
~~~

Utilise des noms de GPO compréhensibles, une justification, un propriétaire, un environnement de test et une date de revue. Évite d'utiliser la stratégie par défaut du domaine comme bloc-notes de tous les réglages. Les changements sensibles devraient être séparés pour faciliter l'analyse du périmètre et le retour arrière.

~~~powershell
gpresult /h C:\Temp\gpresult.html
gpupdate /force
Get-GPO -All | Select-Object DisplayName,Id,ModificationTime
~~~

La première commande génère un rapport local du résultat des stratégies, la deuxième force une actualisation et la troisième inventorie les GPO si le module GroupPolicy est disponible. N'exécute gpupdate /force que lorsque l'effet de la politique est compris et que l'environnement le permet. Sur un serveur critique, examine le périmètre de la GPO et teste les dépendances avant d'appliquer une modification générale.

Les stratégies relatives au compte et à l'audit doivent être cohérentes avec la hiérarchie d'administration. Vérifie le résultat effectif sur des hôtes témoins et non seulement la configuration stockée. Le filtrage de sécurité peut empêcher un paramètre de s'appliquer alors qu'un administrateur s'attend à son activation, ou un lien plus large peut toucher des machines non prévues.

## 11. Contrôleurs de domaine et plan d'identité

Les DC ne doivent pas être traités comme des serveurs d'applications ordinaires. Réduis les logiciels non essentiels, l'accès interactif, les connexions depuis des postes de faible confiance et les identités capables d'administrer le système. Restreins les communications réseau aux services nécessaires et protège la console, l'hyperviseur et les systèmes de sauvegarde qui peuvent contrôler les DC.

Les correctifs de sécurité doivent être planifiés, testés et appliqués selon un cycle cohérent. Vérifie l'état des services AD DS, DNS, réplication, sauvegarde et journalisation après chaque changement. La disponibilité ne se mesure pas uniquement au fait que le service démarre : les clients doivent trouver leur DC et effectuer les opérations métier.

~~~text
             [Poste d'administration Tier 0]
                         |
                         v
               [Zone de gestion contrôlée]
                         |
            +------------+------------+
            |                         |
            v                         v
      [DC principal] ------------ [DC secondaire]
            |                         |
            +------ replication ------+
                        |
                        v
             [Journaux et supervision]

Pas de navigation bureautique quotidienne sur les DC.
~~~

Protège particulièrement le compte DSRM et la procédure de récupération du service d'annuaire. Les mots de passe de récupération doivent être conservés selon un processus sécurisé, disponibles pour les personnes autorisées et testés dans un exercice de reprise. La sauvegarde des DC doit être prise en compte dans le plan de récupération forestière, pas seulement dans une stratégie de sauvegarde de fichiers.

L'accès aux hyperviseurs, aux contrôleurs de stockage et aux outils de gestion qui exécutent ou protègent les DC est également sensible. Si une solution peut modifier l'état du système sur lequel tourne un DC, son accès administratif peut participer au plan de contrôle de l'identité et doit être protégé en conséquence.

## 12. Windows LAPS et mots de passe locaux

Windows LAPS automatise la gestion et la sauvegarde du mot de passe d'un compte administrateur local sur les appareils compatibles joints à AD DS ou Microsoft Entra ID, et peut également gérer le compte DSRM de certains contrôleurs de domaine selon les conditions requises. Il réduit le risque lié à la réutilisation du même mot de passe local sur plusieurs appareils.

La politique doit spécifier quels appareils sont gérés, quel compte local est concerné, la durée de rotation, l'endroit où le secret est sauvegardé et quelles identités peuvent le lire. Les attributs de mot de passe sont sensibles : les droits de lecture, les droits étendus sur les OU et le chiffrement doivent être vérifiés selon la version et le niveau fonctionnel du domaine.

~~~text
[Ordinateur gere]
       |
       v
[Politique Windows LAPS]
       |
       v
[Mot de passe local unique genere et tourne]
       |
       v
[Stockage AD securise par ACL et options compatibles]
       |
       v
[Recuperation par une identite autorisee, avec trace]
~~~

L'adoption de Windows LAPS doit être planifiée avec les versions de Windows Server, le schéma et la gestion de politique. Les versions historiques de Microsoft LAPS et Windows LAPS ne sont pas identiques ; vérifie le mode de migration, l'état du parc et les conséquences avant de modifier la politique existante. Ne déploie pas le nouveau mécanisme sur une partie du parc sans vérifier la compatibilité du domaine et la capacité d'assistance.

Les permissions pour lire les secrets doivent être limitées par rôle et OU. Évite de donner à toute l'équipe helpdesk la lecture de tous les mots de passe administrateur locaux. Les événements de récupération doivent permettre de savoir qui a consulté une valeur sensible et pourquoi, selon les capacités de journalisation de l'environnement.

## 13. Comptes et groupes protégés

Le groupe Protected Users peut appliquer certaines restrictions de protection des justificatifs aux comptes compatibles. Il ne doit pas être utilisé sans comprendre ses limitations d'authentification et de compatibilité. Microsoft avertit notamment de ne pas y ajouter des comptes de service ou d'ordinateur et de mesurer les conséquences pour les comptes hautement privilégiés avant d'étendre l'appartenance.

Les mécanismes de protection des comptes réduisent certains risques mais ne remplacent pas une séparation des postes, une politique d'accès, une authentification forte et la surveillance. Teste les usages des protocoles, les applications anciennes et les scénarios de secours avant toute inclusion massive.

~~~text
[Compte sensible]
      |
      +--> appartenance aux groupes privilegies revue
      +--> usages de protocoles / compatibilite verifies
      +--> restrictions de justificatifs evaluees
      +--> poste d'administration dedie
      +--> surveillance et recuperation documentees
~~~

Les comptes de service doivent utiliser des mécanismes adaptés à leur fonction plutôt qu'être placés dans un groupe humain de protection par défaut. Évalue chaque compte séparément et documente la justification de sa configuration. Une restriction mal planifiée peut interrompre un service ou bloquer un administrateur, sans nécessairement réduire le risque de la manière attendue.

## 14. LDAP signing et channel binding

LDAP est utilisé par des applications et appareils pour lire ou modifier des objets d'annuaire. La signature LDAP protège l'intégrité de certaines sessions SASL et peut empêcher des binds non signés lorsque la politique est appliquée. Le channel binding associe l'authentification à la session TLS sous-jacente, ce qui renforce la protection contre certaines attaques de relais.

Les valeurs par défaut et exigences varient selon les versions de Windows Server et l'historique de la configuration. Les nouveaux déploiements Windows Server 2025 exigent la signature LDAP par défaut selon la documentation Microsoft ; les domaines plus anciens peuvent avoir des réglages plus permissifs. Le durcissement doit donc commencer par l'inventaire des clients, l'activation de l'audit et l'analyse des événements de compatibilité.

~~~text
Client LDAP
    |
    v
[Connexion TLS et authentification]
    |
    v
[LDAP signing / channel binding selon configuration]
    |
    +--> client compatible et politique valide : accepter
    |
    +--> exigence non respectee : refuser et journaliser
~~~

Avant d'exiger la signature ou le channel binding, identifie les applications, imprimantes, équipements réseau, systèmes Linux et produits qui utilisent LDAP. Vérifie les versions clientes, les bibliothèques et les fournisseurs d'identité. Utilise les événements du journal Directory Service pour détecter les connexions incompatibles, planifie une mise à jour et déploie progressivement.

La présence de TLS ne suffit pas à garantir tous les mécanismes de protection contre les relais ; channel binding relie le contexte d'authentification à la session TLS. À l'inverse, activer une politique stricte sans mesurer les dépendances peut interrompre des applications. Le bon processus combine audit, compatibilité, changement contrôlé, enforcement, surveillance et validation.

## 15. SMB, NTLM et protocoles hérités

Les protocoles hérités élargissent parfois les possibilités de relais ou de vol de justificatifs. Une politique de réduction des protocoles doit inventorier les dépendances et renforcer l'authentification, la signature ou le chiffrement selon les capacités et besoins. SMB signing contribue notamment à protéger l'intégrité des messages SMB contre certaines manipulations sur le chemin réseau, mais les valeurs par défaut dépendent de la version et du rôle du système.

Ne confonds pas la signature SMB avec le chiffrement SMB : elles répondent à des objectifs différents. Ne suppose pas non plus que toute connexion SMB utilise les mêmes paramètres. Mesure les usages, consulte les politiques actuelles et teste les clients, serveurs de fichiers, applications et systèmes anciens avant enforcement.

~~~text
[Client SMB] ---- session negociee ----> [Serveur SMB]
       |                                      |
       v                                      v
[Signature requise ?]                  [Politique effective]
       |                                      |
       +--------- integrite valide -----------+
                            |
                            v
                 Autoriser selon la politique
~~~

NTLM peut encore être nécessaire dans certains environnements, mais sa dépendance doit être explicitement documentée, limitée et progressivement réduite quand un chemin plus sûr est viable. Les événements de compatibilité doivent être analysés avant le blocage. N'effectue pas un changement global en supposant que tout client moderne utilise déjà Kerberos dans chaque scénario.

Les équipes doivent également surveiller les comptes qui accèdent à des partages sensibles, les autorisations sur les fichiers et les connexions qui proviennent de sources imprévues. Une authentification robuste ne remplace pas une permission NTFS ou de partage correctement configurée.

## 16. DNS, réplication et santé du domaine

DNS est une dépendance centrale d'AD. Les clients utilisent des enregistrements de service pour localiser les contrôleurs et services appropriés. Un enregistrement manquant, un serveur DNS externe configuré à la place des DNS du domaine ou une résolution incohérente peut provoquer des erreurs d'authentification, de stratégie ou de réplication.

~~~powershell
dcdiag /test:dns /v
repadmin /replsummary
repadmin /showrepl
nltest /dsgetdc:exemple.corp
~~~

Les commandes sont à exécuter avec les outils et privilèges adaptés, sur un environnement autorisé, en utilisant le vrai nom du domaine. Elles vérifient certains aspects de la découverte de contrôleur, du DNS et de la réplication ; elles ne prouvent pas à elles seules que tous les services métier fonctionnent.

~~~text
Client
  |
  v
DNS AD : enregistrements SRV / A / AAAA
  |
  v
Localisation d'un DC approprié
  |
  v
Authentification et application des GPO
  |
  v
Replication entre DC pour la convergence de l'annuaire
~~~

Une réplication en panne peut provoquer des différences d'état et rendre un changement inégalement visible. Avant une modification sensible, vérifie la santé des DC et la convergence des changements. Les erreurs doivent être diagnostiquées selon leur cause ; forcer une réplication sans comprendre la situation peut masquer un problème de DNS, de connectivité, d'authentification ou de temps.

Le temps est important pour Kerberos. Vérifie la hiérarchie de synchronisation et les décalages ; corrige les sources selon l'architecture approuvée. Ne configure pas chaque serveur vers une source arbitraire indépendamment de la hiérarchie de temps de domaine.

## 17. Group Policy, journalisation et audit

Les événements de sécurité et d'annuaire permettent de suivre les connexions, les changements de groupes, la création de comptes, les modifications de GPO et certaines actions sur les objets. La stratégie d'audit doit correspondre aux risques et inclure les événements nécessaires à l'investigation sans produire un volume impossible à exploiter.

Les numéros d'événement et les détails varient selon la catégorie d'audit, la version et le service. Quelques événements communément examinés incluent des échecs ou succès d'ouverture de session, la création d'un compte utilisateur, l'ajout à un groupe sensible et la modification d'une GPO. Il faut documenter les sources et catégories activées plutôt que se baser sur un numéro isolé.

~~~text
[Changement d'identite / groupe / GPO / ACL]
                   |
                   v
[Audit correspondant active et adapte]
                   |
                   v
[Journal Security / Directory Service / logs disponibles]
                   |
                   v
[Collecte distante + horodatage + acces protege]
                   |
                   v
[Correlation, alerte, triage et ticket]
~~~

Les journaux locaux seuls peuvent être supprimés ou expirer. Centralise les événements importants, protège l'accès au collecteur, synchronise les horloges et définis la rétention. Les alertes doivent être contextualisées : un ajout à un groupe privilégié peut être légitime, mais il doit correspondre à une demande et à une approbation identifiables.

L'audit sert aussi à détecter la dérive de configuration : changements de GPO, permissions d'OU, nouvelles identités, modification de méthodes d'authentification et accès inhabituels aux sauvegardes. Pour chaque alerte, assure-toi de pouvoir relier l'événement à un utilisateur ou système, une heure, un objet, une action et une validation attendue.

## 18. Active Directory Certificate Services (AD CS)

AD CS peut délivrer des certificats utilisés pour authentifier des utilisateurs, ordinateurs et services. Il peut également fournir l'infrastructure de confiance pour les connexions TLS, le réseau sans fil ou d'autres usages. Une autorité de certification, ses clés privées, ses modèles de certificats et ses permissions d'enrôlement ont donc une importance élevée.

La sécurité des certificats dépend du type de certificat délivré, de l'identité qui le demande, des droits de modifier les modèles, des approbations éventuelles, de la protection de la clé privée et des paramètres d'usage. Un modèle dont les permissions permettent à une identité non appropriée d'obtenir un certificat avec une identité ou un usage sensible peut créer un risque important. La revue doit analyser la configuration et les droits effectifs plutôt que le seul nom du modèle.

~~~text
[Demandeur]
    |
    v
[Modele de certificat + ACL + regles d'enrolement]
    |
    v
[Approbation / validation selon le modele]
    |
    v
[Autorite de certification]
    |
    v
[Certificat lie a une identite et des usages autorises]
~~~

Les autorités et leurs clés doivent être protégées, sauvegardées et surveillées au niveau correspondant à leur capacité de contrôle d'identité. Contrôle les comptes de service de l'autorité, les administrateurs, les délégations de modèle et la procédure de révocation. Une modification de modèle doit passer par une revue et un test, car elle peut influencer l'authentification de nombreux systèmes.

Pour évaluer AD CS, réalise un inventaire des autorités, modèles, droits, usages de certificats et dépendances ; ne déploie pas de changements globaux sans vérifier les applications. Prévois la mise à jour de la politique, la surveillance des émissions et la réponse à une clé privée ou un certificat compromis.

## 19. Sécuriser SYSVOL, NETLOGON et les scripts

SYSVOL distribue notamment des éléments liés aux stratégies de groupe et peut contenir des scripts exécutés dans un contexte significatif. Les fichiers de script, les répertoires de GPO et les droits de modification constituent des points de contrôle sensibles. Les identifiants ne doivent jamais être écrits en clair dans des scripts, tâches de connexion ou préférences déployées.

~~~text
[Administrateur GPO / script]
            |
            v
[ACL GPO + droits SYSVOL / NETLOGON]
            |
            v
[Replication entre controleurs de domaine]
            |
            v
[Client recupere politique ou script]
            |
            v
[Execution selon contexte utilisateur / machine]
~~~

Inspecte qui peut écrire dans les dossiers pertinents, comment les scripts sont distribués et qui peut modifier les GPO qui les référencent. Les droits d'écriture d'un script administrateur doivent être limités à des auteurs approuvés. Utilise une gestion de versions et une revue du code pour les scripts sensibles.

Les mots de passe ne doivent pas être inclus dans les scripts PowerShell, les fichiers batch, les arguments ou les préférences historiques. Si un script exige un secret, utilise le mécanisme de gestion des secrets adapté et des droits très limités. Lorsqu'un secret a été publié dans SYSVOL ou NETLOGON, traite-le comme compromis et passe par une procédure de rotation.

## 20. Protection des postes administratifs

Les postes d'administration privilégiée (PAW) sont configurés pour les tâches sensibles et évitent les usages ordinaires qui exposent les credentials : navigation générale, courrier, messagerie ou ouverture de documents non fiables. Ils doivent eux-mêmes être mis à jour, surveillés, protégés physiquement et administrés à partir d'un niveau de confiance approprié.

~~~text
[Administrateur Tier 0]
        |
        v
[Poste privilegie Tier 0 securise]
        |
        v
[Chemin reseau limite aux ressources Tier 0]
        |
        v
[DC / AD CS / outils controlant l'identite]

Poste bureautique standard --X--> administration directe du plan identite
~~~

Les comptes Tier 0 ne doivent pas être utilisés sur des hôtes moins fiables. Un poste de support utilisateur n'est pas approprié pour saisir un secret Domain Admin. Le principe fonctionne aussi dans les environnements hybrides : un système cloud ou outil d'identité ayant le contrôle sur des ressources critiques peut relever du même niveau de confiance.

Les postes d'administration doivent avoir un processus d'approvisionnement connu, une liste d'applications autorisées, une politique de sécurité adaptée, une surveillance et une procédure de restauration. L'accès d'administration à partir d'un poste tiers doit être justifié et limité ; l'utilisation ponctuelle ne doit pas devenir une exception permanente.

## 21. Sauvegardes et récupération d'Active Directory

La récupération AD nécessite plus qu'une copie ordinaire de fichiers. Il faut connaître la procédure de sauvegarde supportée, l'état des contrôleurs de domaine, les comptes et secrets de récupération, la version du système, la disponibilité du DNS et la manière de reconstruire les dépendances. Les restaurations doivent être planifiées pour préserver la cohérence de l'annuaire et de la forêt.

Protège les sauvegardes contre la modification et l'effacement par les mêmes identités qui peuvent compromettre les DC. Les opérateurs de sauvegarde, outils d'orchestration, comptes de stockage et hyperviseurs doivent avoir les privilèges strictement nécessaires et être surveillés. Si un système de sauvegarde dispose d'un contrôle étendu sur les DC, il doit être protégé au même niveau de confiance que les ressources qu'il restaure.

~~~text
[DC / annuaire]
      |
      v
[Sauvegarde AD supportee + preuve de reussite]
      |
      v
[Stockage protege, identites distinctes]
      |
      +--> copie isolee / immuable si disponible
      |
      v
[Exercice de restauration en environnement controle]
      |
      v
[Validation DNS, replication, authentification et GPO]
~~~

Définis les objectifs de rétablissement, les responsabilités, les secrets de récupération, les critères de reprise et les tests. Une sauvegarde réussie n'est pas une preuve que la forêt peut être récupérée. Organise des exercices documentés et mesure le temps nécessaire pour remettre les services d'identité à disposition.

## 22. Surveillance et indicateurs prioritaires

Les signaux prioritaires incluent l'ajout inattendu à un groupe privilégié, la création d'un compte sensible, des changements de GPO, la modification d'ACL critiques, les connexions d'administration depuis un hôte inhabituel, les changements de configuration d'authentification, les échecs de réplication ou l'accès aux secrets Windows LAPS en dehors du processus prévu.

Une bonne alerte décrit l'objet, l'action, le compte acteur, la source, l'heure, le résultat et le niveau de criticité. Elle doit être reliée à un processus de validation pour distinguer un changement approuvé d'une activité suspecte. Les règles d'alerte sont réévaluées à mesure que l'organisation, la topologie et les méthodes d'administration évoluent.

~~~text
Sources : Security / Directory Service / DNS / GPO / EDR
                         |
                         v
            Collecte et normalisation des logs
                         |
                         v
      Corrélation : identite + hote + objet + action
                         |
                         v
             Alerte + contexte de changement
                         |
                         v
       Triage / containment / preuve / suivi ticket
~~~

Surveille également la qualité de la journalisation : un changement de GPO peut désactiver un paramètre d'audit, un DC peut être isolé du collecteur et les horloges peuvent diverger. Le pipeline de logs doit avoir ses propres alertes de santé et des droits distincts de ceux du domaine surveillé.

## 23. Plan de durcissement progressif

Une transition vers des politiques plus strictes doit commencer par un inventaire et une observation. Active les journaux utiles, identifie les dépendances, teste sur une OU ou un groupe pilote représentatif, informe les propriétaires applicatifs et définis les critères de succès. Ne passe pas directement d'une configuration permissive à un refus global sans analyser les usages.

~~~text
1. Inventaire des DC, comptes, applis, SPN, GPO, LDAP et NTLM
                         |
                         v
2. Audit des evenements et analyse des exceptions
                         |
                         v
3. Pilote controle + test de compatibilite
                         |
                         v
4. Enforce progressivement avec rollback
                         |
                         v
5. Verifier authentification, GPO, replication et applications
                         |
                         v
6. Revue periodique et detection de derive
~~~

Pour chaque changement, conserve la valeur initiale, la décision, le propriétaire, la fenêtre, les résultats de tests et la méthode de retour arrière. Les exceptions doivent avoir une date de revue, pas devenir des règles permanentes. Les changements de protocole, de GPO, d'ACL ou de groupe sont particulièrement sensibles, car leurs effets peuvent être distribués sur plusieurs contrôleurs et hôtes.

## 24. TP 1 — Audit des identités privilégiées

**Contexte :** tu es administrateur d'un domaine de laboratoire et tu dois examiner les comptes les plus sensibles sans changer l'annuaire.

~~~powershell
Get-ADGroupMember "Domain Admins" -Recursive
Get-ADGroupMember "Enterprise Admins" -Recursive
Get-ADGroupMember "Administrators" -Recursive
Get-ADUser -Filter * -Properties Enabled,PasswordLastSet,LastLogonDate |
  Select-Object SamAccountName,Enabled,PasswordLastSet,LastLogonDate
~~~

**Travail demandé :** liste les membres directs et imbriqués, vérifie les comptes désactivés, identifie les comptes sans propriétaire et propose une revue des comptes de service. Indique les limites des attributs de dernière connexion et ne conclus pas qu'un compte est abandonné sur la base d'un seul champ.

**Correction attendue :** produire un tableau avec identité, type de compte, rôle, propriétaire, groupes privilégiés, état, dernière activité disponible, justification, décision et approbateur requis. Ne retire aucun membre durant la phase d'audit. Prépare une demande distincte et un plan de récupération avant une modification.

**Critère de réussite :** tous les accès privilégiés identifiés sont associés à un propriétaire et à une raison documentée, et les inconnues sont traitées comme des points à examiner.

## 25. TP 2 — Examiner une GPO et son périmètre

**Contexte :** une GPO gère la configuration de sécurité d'un groupe de serveurs. L'équipe veut réduire les droits de modification et vérifier que la politique s'applique aux cibles prévues.

~~~powershell
Get-GPO -All | Select-Object DisplayName,Id,ModificationTime
gpresult /h C:\Temp\gpresult.html
Get-GPPermission -Name "GPO-Serveurs-Lab" -All
~~~

Ces commandes requièrent les outils d'administration et les autorisations correspondantes ; le nom de GPO dans l'exemple doit être remplacé par un nom de laboratoire existant.

**Travail demandé :** inventorie le propriétaire, les permissions, les liens, le filtrage de sécurité, les filtres WMI et les machines cibles. Compare la stratégie stockée avec le résultat effectif sur une machine témoin.

**Correction attendue :** identifie séparément qui peut modifier la GPO, qui peut la lier et quels appareils la reçoivent. Retire les droits excessifs uniquement après validation du propriétaire. Teste les résultats sur un appareil pilote, observe les journaux et prévois le retour arrière.

**Critère de réussite :** les autorisations sont limitées, le périmètre est compris et le résultat appliqué correspond à l'intention.

## 26. TP 3 — Planifier le durcissement LDAP

**Contexte :** certaines applications utilisent LDAP pour consulter l'annuaire. Le domaine doit évoluer vers une politique renforcée de signature et de channel binding, sans interruption de service.

**Travail demandé :** inventorie les clients, collecte les événements d'audit disponibles, classe les dépendances par propriétaire et compatibilité, puis prépare une stratégie pilote et un plan d'application.

**Correction attendue :** commence par l'observation, examine les journaux Directory Service, identifie les clients non compatibles et les versions concernées, corrige ou remplace les clients, puis teste une politique plus stricte dans un périmètre limité. Applique progressivement, confirme l'authentification et conserve les preuves.

**Critère de réussite :** les applications critiques ont un propriétaire et un état de compatibilité documentés, la politique est appliquée selon un plan testé et les refus inattendus ont une procédure de diagnostic.

## 27. Exercices corrigés

### Exercice 1 — Un administrateur utilise son compte Domain Admin sur son PC bureautique

**Correction :** le compte privilégié y est exposé aux risques des courriels, navigateur et logiciels quotidiens. Sépare compte de travail et compte d'administration, utilise un poste privilégié et limite les connexions des identités Tier 0 aux systèmes appropriés. Documente le chemin d'administration et les journaux.

### Exercice 2 — Une OU Helpdesk peut réinitialiser tous les mots de passe du domaine

**Correction :** vérifie l'ACL et la portée effective de la délégation. Limite la permission à l'OU et aux objets nécessaires, sans inclure des comptes sensibles. Teste avec un compte de support et vérifie qu'un compte privilégié hors périmètre ne peut pas être modifié.

### Exercice 3 — Un compte de service est membre de Domain Admins

**Correction :** identifie l'application, l'usage réel et les droits nécessaires. Prépare un compte dédié, gMSA si compatible, et des permissions minimales. Teste les dépendances avant de retirer les privilèges ; ne laisse pas la décision dépendre uniquement du nom du service.

### Exercice 4 — Un client LDAP échoue après renforcement de la signature

**Correction :** identifie le client et les journaux d'audit, vérifie les capacités de signature/TLS et planifie la mise à jour ou le remplacement. N'annule pas immédiatement le durcissement global ; utilise le périmètre pilote et une exception limitée dans le temps si elle est formellement approuvée.

### Exercice 5 — Une GPO peut être modifiée par un groupe trop large

**Correction :** inspecte les permissions de la GPO et du lien, distingue les droits de lecture, d'édition et de liaison. Limite les modifications aux rôles responsables, teste l'application et active un audit adapté. Conserve un export ou une documentation de la configuration initiale.

### Exercice 6 — Le mot de passe local est identique sur plusieurs postes

**Correction :** ce partage facilite le mouvement latéral lorsque le secret est compromis. Planifie Windows LAPS ou le mécanisme de gestion pris en charge, vérifie les droits de récupération et teste la rotation et le support des appareils. Ne donne l'accès aux secrets qu'aux rôles habilités.

### Exercice 7 — Un compte inactif est membre d'un groupe sensible

**Correction :** vérifie le propriétaire, les usages applicatifs, les attributs de dernière connexion et les systèmes qui dépendent du compte. Décide d'une désactivation contrôlée, surveille les conséquences et conserve la procédure de réactivation selon la gouvernance. Les attributs seuls ne prouvent pas l'abandon.

### Exercice 8 — Une application dépend de NTLM

**Correction :** identifie le flux, la version cliente et la méthode actuelle. Cherche un remplacement Kerberos ou une correction de configuration, teste et surveille avant de bloquer NTLM. Documente une exception transitoire si elle est nécessaire, avec un propriétaire et une échéance.

### Exercice 9 — Un SPN est dupliqué

**Correction :** identifie les comptes et applications concernés, vérifie les noms et les journaux d'authentification. Planifie la correction sur le compte approprié, teste l'accès au service puis confirme l'absence de doublon. N'effectue pas une modification de production avant validation applicative.

### Exercice 10 — Un compte possède une délégation non contrainte

**Correction :** identifie la raison historique et les systèmes dépendants, confirme les options réellement nécessaires et prépare la migration vers une forme plus restreinte lorsque supportée. Teste les flux et surveille les logs. Ne bascule pas toutes les applications sans analyse de compatibilité.

### Exercice 11 — La réplication AD présente des erreurs

**Correction :** examine DNS, connectivité, résolution de noms, temps, authentification entre DC et événements de réplication. Corrige la cause puis valide la convergence. Ne force pas aveuglément toutes les opérations de réplication ni ne masque les erreurs sans comprendre leur origine.

### Exercice 12 — Une clé privée de l'autorité AD CS a pu être exposée

**Correction :** déclenche le processus d'incident PKI, identifie l'autorité, les certificats émis et les dépendances, préserve les preuves et évalue la révocation ou le remplacement de la clé selon le plan. Protège les sauvegardes et les systèmes d'administration associés ; rétablir la seule permission du fichier ne suffit pas.

## 28. Défi final — sécuriser un domaine d'entreprise

### Contexte

Une entreprise possède deux contrôleurs de domaine, des postes Windows, des serveurs métier, un helpdesk, des applications LDAP, une GPO de sécurité, des comptes de service, une autorité de certification interne et une infrastructure de sauvegarde. Certains administrateurs utilisent encore leur compte privilégié depuis un poste quotidien. Les mots de passe locaux sont partagés et les événements d'annuaire ne sont pas centralisés.

### Correction détaillée

**Étape 1 — Cartographier.** Inventorie les DC, DNS, forêts/domaines, sites, OU, GPO, groupes sensibles, comptes de service, SPN, applications LDAP, AD CS et systèmes de sauvegarde. Identifie les propriétaires et chemins d'administration.

**Étape 2 — Définir les tiers.** Classe les identités et systèmes selon le contrôle réel. Protège le Tier 0, utilise des postes administratifs correspondants et empêche la saisie de credentials privilégiés sur les postes de moindre confiance. Inclue les outils de sauvegarde, hyperviseurs et agents capables de contrôler les DC dans l'analyse.

**Étape 3 — Réduire les privilèges.** Revois groupes directs et imbriqués, ACL, délégations d'OU, droits de GPO et comptes de service. Retire les droits excessifs dans un processus approuvé, teste les applications et conserve les preuves.

**Étape 4 — Sécuriser l'authentification.** Réduis les dépendances NTLM, protège Kerberos, vérifie DNS et temps, inventorie les SPN et délégations, planifie le renforcement LDAP signing et channel binding après audit de compatibilité.

**Étape 5 — Protéger les postes et secrets locaux.** Déploie Windows LAPS selon les prérequis et la compatibilité du domaine, contrôle les permissions de lecture et les événements de récupération. Protège les clés, secrets et comptes de service, et privilégie gMSA lorsque cela convient.

**Étape 6 — Protéger les DC, GPO et AD CS.** Réduis les logiciels et logons sur DC, limite leurs flux réseau, revois les permissions de GPO/SYSVOL et les modèles de certificats. Toute modification doit être testée et approuvée.

**Étape 7 — Détecter.** Active les événements adaptés, centralise-les, synchronise le temps et alerte sur les changements sensibles. Surveille aussi la santé du pipeline de logs et la réplication. Associe les modifications à un ticket ou une approbation.

**Étape 8 — Récupérer.** Protège les sauvegardes contre les identités pouvant compromettre l'annuaire, documente les secrets de récupération et réalise un exercice de reprise qui valide DNS, réplication, authentification et GPO.

**Étape 9 — Tester.** Vérifie les accès légitimes, les refus hors périmètre, le résultat des GPO, la compatibilité LDAP, les connexions de service et la lecture des secrets Windows LAPS. Documente les tests positifs et négatifs.

**Étape 10 — Gouverner.** Revois périodiquement les comptes, ACL, GPO, exceptions protocolaires, certificats, agents d'administration et systèmes de sauvegarde. Chaque exception doit avoir un propriétaire, une raison, une date de revue et une stratégie de retrait.

Le défi est réussi quand les chemins vers le plan d'identité sont limités, les privilèges justifiés, les protocoles et politiques compatibles et surveillés, les sauvegardes restaurables et les opérations sensibles attribuables.

## 29. Checklist de validation

- Les forêts, domaines, DC, DNS et dépendances critiques sont documentés.
- Les membres des groupes sensibles et les groupes imbriqués ont été examinés.
- Les comptes de service sont justifiés, possèdent un propriétaire et des droits minimaux.
- Les administrations sont séparées par tiers et les postes privilégiés sont protégés.
- Les ACL d'OU, de groupes, de GPO et de SYSVOL sont revues.
- Les comptes et secrets locaux utilisent une stratégie de rotation adaptée.
- Les SPN, délégations Kerberos et dépendances NTLM ont été inventoriés.
- LDAP signing et channel binding sont traités avec audit de compatibilité.
- Les DC sont durcis, surveillés et limités aux services nécessaires.
- Les modèles et clés AD CS sont protégés et les émissions suivies.
- Les événements sensibles sont centralisés et corrélés.
- La réplication, le DNS et le temps sont surveillés.
- Les sauvegardes et procédures de récupération ont été testées.
- Les exceptions et changements possèdent un propriétaire et un rollback.
- Un exercice confirme que l'organisation sait restaurer les services d'identité.

## 30. Glossaire

**AD DS :** service d'annuaire Active Directory Domain Services pour les identités, objets et authentifications du domaine.

**Forêt :** ensemble de domaines AD partageant un schéma et un catalogue global et formant une frontière administrative importante.

**Domaine :** partition logique d'AD avec ses objets, politiques et services associés.

**OU :** unité d'organisation utilisée pour organiser les objets et déléguer certaines tâches.

**DC :** contrôleur de domaine qui héberge AD DS et fournit notamment l'authentification et la réplication.

**GPO :** objet de stratégie de groupe qui applique des paramètres aux utilisateurs ou ordinateurs ciblés.

**ACL :** liste de contrôle d'accès définissant les opérations autorisées sur un objet ou une ressource.

**Kerberos :** protocole d'authentification utilisant des tickets et un centre de distribution de clés.

**NTLM :** famille historique de mécanismes d'authentification Windows, à inventorier et réduire selon la compatibilité.

**SPN :** nom principal de service associé à l'identité d'un service Kerberos.

**gMSA :** compte de service géré de groupe dont le mot de passe est géré automatiquement par les mécanismes Windows compatibles.

**Tier 0 :** niveau de confiance qui contrôle l'identité et les actifs capables de contrôler le domaine.

**Windows LAPS :** fonctionnalité qui gère et renouvelle les mots de passe de comptes administrateurs locaux compatibles.

**AD CS :** Active Directory Certificate Services, infrastructure de délivrance et de gestion de certificats.

**SYSVOL :** partage répliqué contenant notamment les éléments de stratégie de groupe et scripts associés.

**LDAP signing :** protection d'intégrité applicable à certains binds LDAP selon le mécanisme et la politique.

**Channel binding :** association cryptographique de l'authentification à la session TLS pour renforcer la protection contre certains relais.

**PAW :** poste d'administration privilégiée conçu pour les tâches sensibles.

**DSRM :** mode de restauration des services d'annuaire sur un contrôleur de domaine Windows.

## 31. Références officielles Microsoft

- Best practices for securing Active Directory : https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/best-practices-for-securing-active-directory — réduction de la surface d'attaque, moindre privilège et protection des contrôleurs de domaine.
- AD DS Tier Model for Privileged Access Security : https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/tier-model — séparation des tiers et des postes d'administration.
- Windows LAPS overview : https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview — rotation et stockage sécurisé des mots de passe locaux.
- Protected Users security group : https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group — fonctionnement et précautions de compatibilité du groupe.
- LDAP signing overview : https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/ldap-signing — signature LDAP et différences de comportement selon les versions.
- LDAP channel binding : https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/ldap-channel-binding — protection liée à la session TLS et audit de compatibilité.
- Windows LAPS with Windows Server Active Directory : https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-scenarios-windows-server-active-directory — prérequis et mise en place dans AD DS.

Les politiques et valeurs par défaut évoluent selon les versions de Windows Server et les mises à jour. Avant enforcement, vérifie les versions réelles de ton environnement, la documentation liée à ces versions, les événements d'audit et les dépendances applicatives. Procède par pilote et conserve un plan de retour arrière.

Fin du cours.

## 32. Cas de dépannage détaillés — 31 situations

### Cas 1 — Un membre inattendu apparaît dans Domain Admins

**Analyse et démarche.** Il peut s'agir d'un changement approuvé, d'un compte oublié ou d'une activité malveillante. Vérifie l'événement de modification, l'acteur, les groupes imbriqués, le ticket et les connexions associées. Confirme auprès du propriétaire, puis retire l'accès par un changement contrôlé s'il est non autorisé. Analyse les autres identités et systèmes contrôlés par ce compte. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne te limite pas aux membres directs et ne supprime pas un compte critique sans plan de récupération. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 2 — Une application ne peut plus s'authentifier après durcissement LDAP

**Analyse et démarche.** Le client peut utiliser un bind non signé ou ne pas supporter la politique de channel binding appliquée. Examine les événements du journal Directory Service, identifie l'hôte et la version cliente puis reproduis en pilote. Mets à jour ou remplace le client et n'applique la politique stricte que selon un plan de compatibilité. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne désactive pas globalement le durcissement sans propriétaire et échéance de migration. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 3 — Un utilisateur helpdesk peut modifier une GPO de serveurs

**Analyse et démarche.** Les ACL de la GPO ou les droits de son lien peuvent être trop larges. Examine les permissions de lecture, d'édition et de liaison, les héritages et le filtrage. Limite les droits au rôle approuvé, teste l'effet sur une OU pilote et surveille les modifications futures. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne suppose pas qu'un compte non privilégié est sans risque pour le domaine. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 4 — Un service possède un compte avec mot de passe statique partagé

**Analyse et démarche.** Le secret peut être réutilisé ou compromis sur plusieurs serveurs, ce qui élargit l'impact. Identifie chaque hôte et dépendance, évalue un gMSA si compatible ou une rotation contrôlée, puis limite les droits et vérifie l'absence d'ouverture interactive inutile. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne tourne pas le secret sans cartographier les applications qui en dépendent. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 5 — Une GPO de sécurité ne s'applique pas à un serveur

**Analyse et démarche.** Le lien, l'héritage, le filtrage de sécurité ou le filtre WMI peut être incorrect. Génère un gpresult, vérifie l'OU, les permissions, le filtrage et les événements d'application. Corrige la portée et confirme le résultat effectif sur une machine témoin. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne présume pas que la présence d'une GPO dans la console prouve son application. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 6 — Kerberos échoue alors que le mot de passe est correct

**Analyse et démarche.** DNS, l'heure, le SPN, la découverte du DC ou une dépendance du service peuvent être en cause. Vérifie DNS, temps, contrôleur sélectionné et événements d'authentification. Examine les SPN en lecture seule et compare la configuration au service réel avant toute modification. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne bascule pas automatiquement toute l'application vers NTLM pour contourner une erreur Kerberos. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 7 — Des SPN dupliqués apparaissent dans un rapport

**Analyse et démarche.** Plusieurs objets peuvent être associés au même identifiant de service Kerberos. Identifie les comptes et services propriétaires, confirme les noms utilisés puis planifie une correction testée. Valide l'authentification et la disponibilité après modification. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne supprime pas un SPN sur la seule base de son nom sans vérifier l'application qui l'utilise. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 8 — Un compte présente une délégation Kerberos non contrainte

**Analyse et démarche.** Cette configuration peut étendre l'exposition des justificatifs dans certains scénarios. Documente le service, ses dépendances et ses propriétaires, puis détermine la forme de délégation minimale supportée. Teste le remplacement et vérifie les flux en aval. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne coupe pas une délégation en production sans valider l'application, mais ne laisse pas une exception sans revue. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 9 — Le mot de passe administrateur local est partagé entre postes

**Analyse et démarche.** La compromission d'un seul appareil peut faciliter le mouvement latéral vers d'autres postes. Planifie Windows LAPS ou un mécanisme pris en charge, vérifie le schéma et la compatibilité, restreins les permissions de lecture des secrets et teste la rotation et l'assistance. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne rends pas tous les mots de passe LAPS lisibles par le helpdesk sans séparation des rôles. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 10 — Un membre de Protected Users n'arrive plus à utiliser une application ancienne

**Analyse et démarche.** L'application peut dépendre d'un protocole ou d'un mode d'authentification incompatible avec les restrictions du groupe. Identifie les flux et protocoles, consulte les événements et teste la compatibilité. Conçois un chemin d'identité plus sûr ou un compte dédié à usage approprié ; documente toute exception approuvée. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne place pas aveuglément des comptes de service ou des comptes critiques dans ce groupe. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 11 — La réplication AD est en échec

**Analyse et démarche.** DNS, connectivité, authentification, temps ou santé d'un DC peuvent empêcher la convergence. Examine repadmin, dcdiag, les événements système et annuaire, la résolution DNS et le temps. Corrige la cause et vérifie que les changements convergent entre DC. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne force pas la réplication sans comprendre la raison de l'échec. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 12 — Un contrôleur de domaine est utilisé comme serveur applicatif général

**Analyse et démarche.** Les logiciels et connexions non essentiels augmentent la surface d'attaque de l'identité. Inventorie les rôles et applications, migre les workloads vers des serveurs membres et restreins les logons et logiciels sur les DC. Teste DNS, authentification, réplication et applications liées après migration. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne traite pas le DC comme un serveur généraliste ou un poste bureautique. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 13 — Une clé privée AD CS pourrait avoir été exposée

**Analyse et démarche.** Une compromission peut affecter les certificats et identités dépendant de l'autorité. Déclenche le processus d'incident PKI, préserve les preuves, identifie les certificats émis et les dépendances, puis évalue la révocation et le remplacement selon la procédure. Protège aussi les sauvegardes et l'administration de l'autorité. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne te contente pas de modifier les permissions du fichier clé si une copie a pu être faite. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 14 — Un script de connexion contient un mot de passe en clair

**Analyse et démarche.** Les utilisateurs qui lisent le script ou les partages peuvent récupérer le secret. Considère le secret comme exposé, révoque-le et remplace-le, identifie toutes les utilisations et retire-le du script et des dépôts. Examine les copies historiques et les logs. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne considère pas une suppression du fichier courant comme une rotation du secret. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 15 — Le renforcement NTLM bloque un système ancien

**Analyse et démarche.** Un client ou service dépend encore d'un mécanisme historique. Analyse les événements, identifie le propriétaire et la version du client, teste un chemin Kerberos ou une mise à jour et limite toute exception dans le temps. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne désactive pas au hasard le contrôle sur toute la forêt pour réparer un client isolé. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 16 — Les journaux de modification des groupes privilégiés manquent

**Analyse et démarche.** La politique d'audit peut être incomplète ou la collecte ne fonctionne pas. Vérifie les catégories d'audit, la GPO réellement appliquée, la collecte distante, l'heure et la santé du pipeline. Reproduis un changement de test contrôlé et confirme que l'événement est visible. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne suppose pas que l'absence d'alerte signifie qu'aucune modification n'a eu lieu. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 17 — Un compte de service semble inactif selon LastLogonDate

**Analyse et démarche.** L'attribut n'est pas une preuve complète d'abandon ou de non-utilisation. Vérifie les tâches planifiées, services, journaux applicatifs, réplication de l'attribut et propriétaire métier. Prépare une désactivation surveillée avec critères de restauration si l'inactivité est confirmée. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne supprime pas un compte utilisé par une tâche mensuelle sur la base d'un seul indicateur. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 18 — L'accès à un secret LAPS est accordé à un groupe trop large

**Analyse et démarche.** Des utilisateurs peuvent lire les mots de passe locaux d'appareils hors de leur périmètre. Inspecte les ACL et droits étendus sur l'OU, limite la lecture aux rôles nécessaires et teste l'accès autorisé et interdit. Surveille les événements de récupération lorsque disponibles. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne considère pas le droit de réinitialiser un compte comme équivalent au droit de lire son secret. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 19 — Un changement LDAP est prévu sans inventaire de compatibilité

**Analyse et démarche.** L'enforcement peut interrompre des services dont le comportement n'est pas connu. Active l'audit, identifie les clients, attribue les dépendances à un propriétaire et pilote la politique. Planifie mises à jour et validation avant l'application générale. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne passe pas directement à une stratégie de refus globale. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 20 — Une OU a hérité d'une délégation inattendue

**Analyse et démarche.** L'ACL peut être héritée d'une OU parente ou issue d'une modification précédente. Examine les ACL effectives, les héritages et groupes imbriqués. Documente l'autorisation prévue, corrige le périmètre précis et teste le rôle d'administration concerné. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne désactive pas l'héritage sans comprendre quelles permissions légitimes seraient retirées. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 21 — Le DNS AD renvoie des DC incorrects ou n'en trouve aucun

**Analyse et démarche.** Les enregistrements SRV ou la configuration du client peuvent être incorrects. Vérifie la configuration DNS du client, les enregistrements de service, la santé de DNS et l'état des DC avec les outils de diagnostic. Valide ensuite la découverte et l'authentification. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne remplace pas simplement le DNS du domaine par un DNS public pour contourner la panne. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 22 — Une GPO applique un paramètre à des machines non prévues

**Analyse et démarche.** Le lien, le filtrage ou le groupe cible a une portée trop large. Inspecte l'héritage, les liens, les filtres WMI, les permissions et le résultat gpresult. Réduis le périmètre dans une fenêtre contrôlée et valide les cibles positives et négatives. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne corrige pas une portée trop large en supprimant la GPO sans mesurer les dépendances. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 23 — Un outil de sauvegarde possède des privilèges sur les DC

**Analyse et démarche.** La compromission de cet outil peut offrir un chemin vers le plan d'identité. Classe l'outil selon son contrôle réel, protège ses comptes et son infrastructure au niveau requis, sépare les rôles et journalise les actions. Teste les restaurations avec des identités dédiées. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne considère pas la sauvegarde comme un service sans privilège simplement parce qu'il sert à la récupération. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 24 — Un compte de prestataire conserve ses droits après la fin du contrat

**Analyse et démarche.** Les identités externes et les exceptions n'ont pas été retirées. Vérifie compte, groupes, VPN, bastion, certificats, comptes de service et accès applicatifs. Révoque au point autoritaire, valide les logs et actualise le processus de départ. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne limite pas la révocation à la désactivation du compte utilisateur si des secrets partagés subsistent. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 25 — Une modification de politique bloque la réplication ou l'authentification

**Analyse et démarche.** Un changement de sécurité peut impacter une dépendance fondamentale ou ne pas être appliqué uniformément. Examine les changements récents, les événements, la politique effective sur chaque DC et la santé du domaine. Utilise le rollback prévu si nécessaire, puis reteste la réplication et l'accès des clients. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne réécris pas simultanément plusieurs politiques de base avant d'isoler la cause. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 26 — Un certificat inattendu a été émis par AD CS

**Analyse et démarche.** Le modèle, les permissions d'enrôlement ou le compte demandeur peut ne pas correspondre au besoin. Examine les logs de délivrance, le modèle, les ACL, l'identité et l'usage du certificat. Révoque suivant le processus PKI si nécessaire et resserre le modèle après tests. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne considère pas le certificat valide uniquement parce qu'il a été émis par l'autorité interne. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 27 — Un poste standard a été utilisé pour administrer un DC

**Analyse et démarche.** Les identifiants de haut niveau ont été exposés à un environnement moins fiable. Évalue les sessions, secrets saisis et journaux ; change les identifiants si leur exposition est plausible, déplace l'administration vers un poste privilégié et vérifie les accès inhabituels. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne suppose pas qu'aucun risque n'existe parce que le compte n'était utilisé que quelques minutes. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 28 — Les autorisations SYSVOL permettent à trop de personnes de modifier un script

**Analyse et démarche.** Un acteur peut altérer un script distribué et potentiellement exécuté par des clients. Vérifie les ACL de répertoire et fichier, le propriétaire, les GPO qui invoquent le script et les systèmes concernés. Restreins l'écriture, compare les versions et enquête sur les modifications inconnues. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne vérifie pas uniquement les permissions de lecture ; les droits d'écriture sur les parents sont également importants. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 29 — L'heure des DC diverge et Kerberos échoue

**Analyse et démarche.** Les tickets Kerberos peuvent être rejetés quand l'écart de temps dépasse les tolérances configurées. Vérifie la hiérarchie de temps, les sources, les services et les événements. Corrige la source autoritaire selon l'architecture puis valide les clients et les DC concernés. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne configure pas des sources de temps contradictoires sans comprendre la hiérarchie du domaine. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 30 — Une sauvegarde AD a réussi mais la reprise n'a jamais été testée

**Analyse et démarche.** La disponibilité d'une sauvegarde ne prouve pas que le service d'identité peut être restauré. Organise un exercice dans un environnement isolé, vérifie la procédure supportée, le DNS, l'authentification, la réplication et les GPO puis documente la durée et les écarts. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne découvre pas les secrets manquants ou dépendances critiques pendant une véritable crise. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

### Cas 31 — Une alerte de compte privilégié est générée par une opération approuvée

**Analyse et démarche.** Le processus de changement et le contexte de détection ne sont pas corrélés ou clairement documentés. Vérifie l'acteur, l'objet, le ticket, l'approbateur et la fenêtre. Améliore le contexte de l'alerte tout en conservant la détection indépendante et les journaux. Consigne l'heure, l'acteur, l'objet AD, l'hôte, le changement récent, les journaux et le résultat métier. Compare les droits effectifs à la fonction attendue et distingue les faits confirmés des hypothèses avant toute modification.

**Erreur à éviter.** Ne désactive pas une alerte de sécurité de façon permanente pour réduire le bruit. Après correction, teste un scénario autorisé et un scénario qui doit être refusé, conserve les preuves et documente l'approbation ainsi que le retour arrière.

Fin du cours.
