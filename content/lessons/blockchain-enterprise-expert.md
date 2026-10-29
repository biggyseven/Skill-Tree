# Blockchain d'entreprise (Hyperledger)

## Encadré de mise en contexte

Toutes les applications blockchain n'ont pas besoin d'un réseau public ouvert. Dans une chaîne logistique, un consortium bancaire, un système d'identité ou un échange de documents entre entreprises, les participants sont généralement identifiés, leurs droits sont contractuels et certaines données ne doivent être partagées qu'avec une partie des organisations. Une blockchain permissionnée cherche à fournir un registre partagé et auditable sans rendre chaque opération publique à l'ensemble d'Internet.

Hyperledger Fabric est une plateforme de registre distribué permissionnée. Elle sépare plusieurs rôles qui sont souvent confondus dans les modèles de blockchain publique : les organisations et leurs identités, les peers qui hébergent le ledger et exécutent les chaincodes, le service d'ordering qui établit l'ordre des transactions, les channels qui isolent des groupes de participants, et les collections de données privées qui limitent la diffusion de valeurs spécifiques. Cette architecture donne des outils de gouvernance et de confidentialité, mais elle ne supprime pas la nécessité de définir les droits, la disponibilité, la confiance entre organisations et les responsabilités d'exploitation.

Le mot « blockchain d'entreprise » n'est pas une garantie de qualité. Un réseau privé peut être mal gouverné, centralisé, mal configuré ou inutile si une base de données classique répond mieux au besoin. Ce cours apprend à évaluer le cas d'usage, concevoir une topologie Fabric, définir les politiques d'endossement, organiser les identités et la confidentialité, déployer un chaincode, surveiller le réseau et préparer les opérations de production.

## Objectifs d'apprentissage

À la fin de cette leçon, tu dois pouvoir expliquer l'architecture de Fabric, distinguer peers et orderers, comprendre MSP et certificats, décrire channels et collections privées, expliquer le cycle de vie d'un chaincode, construire une politique d'endossement, concevoir une transaction de registre, analyser le modèle de confiance et planifier le déploiement, la surveillance, la sauvegarde et la réponse à incident.

## Prérequis et environnement de laboratoire

Il est utile de connaître les concepts de transaction, de hachage, de signatures, de ledger, de smart contract et de base de données. Les exercices doivent être réalisés dans un environnement local de test. Ne réutilise pas des certificats, clés ou mots de passe de production dans un atelier. Pour déployer un réseau réel, suis la documentation officielle de la version choisie et vérifie les exigences de compatibilité entre images, CLI, bibliothèques clientes et chaincodes.

Le parcours pratique commence par une définition métier : quelles organisations participent, quel actif est partagé, qui peut lire chaque donnée, qui peut proposer une transaction, qui doit l'approuver et comment les désaccords sont résolus. Ensuite seulement, la topologie et les composants sont choisis. Une bonne architecture commence par le modèle de gouvernance et de données, pas par l'installation d'un conteneur.

## 1. Quand choisir une blockchain permissionnée ?

Une blockchain permissionnée peut être utile lorsque plusieurs organisations doivent partager un historique cohérent, mais qu'aucune ne doit être seule maîtresse de toutes les écritures ou de l'audit. Les participants possèdent des identités reconnues, peuvent se soumettre à des règles contractuelles et doivent pouvoir vérifier les transactions pertinentes. L'architecture peut permettre à une organisation d'exécuter un nœud sans faire confiance à une plateforme contrôlée par un seul partenaire.

Ce modèle se distingue d'une blockchain publique où la participation, la visibilité de l'état et les incitations sont organisées différemment. Le réseau permissionné peut limiter la lecture et l'écriture à des membres autorisés, mais cette limitation crée une dépendance à la gouvernance de l'adhésion et à l'administration des identités. Si l'exploitant central peut révoquer ou modifier toutes les identités sans contrôle, la distribution technique des nœuds n'offre pas à elle seule une gouvernance partagée.

Avant d'utiliser une blockchain, compare-la à une base de données répliquée avec journal d'audit, signatures et gestion d'accès. Une blockchain peut être excessive lorsque toutes les parties font confiance au même opérateur et qu'il n'existe pas de besoin indépendant de vérification. En revanche, un ledger partagé peut aider lorsque les organisations doivent vérifier l'historique des changements et imposer collectivement des politiques de validation.

Une note de décision doit expliquer pourquoi un registre distribué est nécessaire, quelles organisations ont un intérêt à le maintenir, quelle donnée doit être immuable et quelles données doivent être modifiables sous procédure. Elle doit également traiter les coûts d'exploitation, la gouvernance des versions, la gestion des clés et les responsabilités lors d'une panne.

## 2. Les composants majeurs de Fabric

Un réseau Fabric regroupe plusieurs organisations. Chaque organisation possède des identités et des politiques qui déterminent ses actions. Les peers hébergent les copies de ledger auxquelles ils participent, peuvent exécuter des chaincodes pour simuler des propositions et valident les transactions reçues selon les règles du canal. Les ordering nodes fournissent le service d'ordering : ils établissent l'ordre des transactions qui seront distribuées aux peers.

Une autorité de certification peut émettre des certificats d'identité, tandis qu'un MSP, Membership Service Provider, définit comment ces identités sont reconnues et quelles catégories de certificats sont acceptées dans le contexte du réseau. Les clients utilisent leurs identités pour proposer des transactions et interagir avec les services. Le Gateway Fabric peut simplifier la découverte des peers nécessaires pour satisfaire les politiques d'endossement et l'envoi vers le service d'ordering.

Il est important de distinguer l'exécution du chaincode et l'ordering. Les peers simulent la proposition et produisent les endorsements ; le service d'ordering établit l'ordre des transactions et distribue les blocs ; les peers valident ensuite les transactions avant de mettre à jour leur ledger et leur état courant. Les ordering nodes ne jouent pas simplement le rôle d'un peer exécutant toute la logique métier.

~~~mermaid
flowchart TD
    C[Application cliente et identité] --> G[Fabric Gateway]
    G --> P1[Peer organisation A]
    G --> P2[Peer organisation B]
    P1 --> E[Endorsements requis]
    P2 --> E
    E --> O[Service d'ordering]
    O --> B[Bloc distribué au canal]
    B --> V[Validation par les peers]
    V --> L[Ledger et état courant]
~~~

Le schéma est conceptuel et simplifie les interactions. Une topologie réelle peut contenir plusieurs peers par organisation, plusieurs orderers et plusieurs canaux. La haute disponibilité, la séparation des environnements et les politiques sont des décisions d'architecture distinctes.

## 3. Organisations, identité et MSP

Fabric utilise un modèle d'identité basé sur des certificats et des politiques d'appartenance. Les identités ne sont pas de simples noms déclarés par l'application ; elles sont évaluées selon les autorités et les règles définies dans la configuration du réseau. Le MSP indique comment les certificats sont validés et comment les rôles ou catégories d'identité peuvent être reconnus.

L'autorité de certification (CA) sert à émettre et gérer des certificats, mais elle n'est pas synonyme de l'ensemble du MSP. Le MSP peut faire référence à des racines de confiance, des certificats intermédiaires, des listes de révocation et d'autres règles d'identité. Dans une architecture d'entreprise, la gouvernance doit expliquer qui contrôle les CA, comment les certificats sont renouvelés et comment la révocation est propagée.

Une identité expirée ou révoquée peut empêcher des transactions ou certaines opérations d'administration. Une clé compromise peut permettre à un acteur de se faire passer pour l'identité correspondante jusqu'à ce que la révocation et les autres contrôles prennent effet. La procédure opérationnelle doit donc couvrir l'émission, la distribution, la conservation, le renouvellement et la révocation. Les clés privées ne doivent pas être placées dans le dépôt du chaincode ou dans les journaux applicatifs.

Les rôles doivent suivre le principe du moindre privilège. Une identité d'application n'a généralement pas besoin des droits de gestion de canal ; une identité d'administration de réseau ne doit pas être utilisée pour des appels ordinaires de métier. Les comptes de production doivent être distingués des identités de laboratoire. Une séparation stricte réduit les conséquences d'une compromission ou d'une erreur de configuration.

## 4. Ledger, blockchain et état courant

Le ledger Fabric contient l'historique des transactions et un état courant pratique pour interroger les actifs. Le bloc et l'historique permettent de retracer les changements, tandis que l'état courant fournit les valeurs les plus récentes selon la logique du chaincode. Ces deux notions ne sont pas interchangeables : une lecture de l'état courant ne remplace pas une enquête historique, et un événement historique ne garantit pas que l'opération a modifié l'état comme l'application l'avait prévu.

Le chaincode définit les règles de lecture et de modification. Il doit avoir des fonctions claires pour créer, consulter, mettre à jour et transférer des actifs. Chaque opération doit vérifier les préconditions : l'actif existe-t-il, l'appelant est-il autorisé, l'état a-t-il changé depuis la lecture et les champs modifiables correspondent-ils à la règle métier ? Les attributs qui déterminent l'identité d'un actif ne devraient pas être remplacés librement par une mise à jour générique.

La conception doit décider quelles informations se trouvent dans l'état partagé. Une donnée immuable mais fausse reste fausse ; une blockchain ne vérifie pas automatiquement la véracité de ce qui est saisi par une organisation. Les processus métier doivent définir les pièces de preuve, les signatures ou les validations nécessaires avant qu'une donnée externe soit acceptée.

## 5. Channels et séparation des participants

Un channel Fabric fournit un domaine logique dans lequel les organisations participantes partagent une configuration et un ledger. Les organisations qui ne sont pas membres du canal ne doivent pas recevoir son contenu par les voies normales du protocole. Cette séparation peut être utile pour un consortium qui possède des sous-ensembles d'accords ou des actifs qui ne concernent pas tous les membres.

Les channels ne doivent pas être utilisés comme seule réponse à toutes les exigences de confidentialité. Un canal supplémentaire implique une configuration, des politiques et une exploitation supplémentaires. Si seules quelques clés ou valeurs doivent être privées tout en gardant le reste du ledger partagé, les collections de données privées peuvent être plus adaptées. Le choix dépend du périmètre de lecture, des politiques, de la fréquence d'évolution et du besoin d'audit.

La gouvernance du canal doit définir qui peut modifier la configuration, ajouter ou retirer des organisations, mettre à jour les politiques et approuver le chaincode. Les changements de membres sont des changements de sécurité : ils modifient qui peut participer à la validation et qui peut avoir accès aux données. Une procédure doit documenter les approbations, les vérifications après changement et la gestion des membres qui quittent le consortium.

## 6. Cycle de vie d'un chaincode

Dans Fabric, le chaincode contient la logique métier. Son cycle de vie comporte plusieurs étapes qui doivent être coordonnées entre organisations : emballer ou préparer le code, l'installer sur les peers concernés, approuver sa définition par les organisations requises, puis valider ou commit la définition sur le canal selon les règles de la version utilisée. Cette procédure rend explicite l'approbation collective des règles qui seront appliquées.

Installer un chaincode sur un peer ne signifie pas qu'il est déjà actif dans un canal. De même, une organisation peut installer le code puis refuser d'approuver la définition, selon sa gouvernance. Le lifecycle permet de vérifier que la définition et sa politique sont cohérentes entre les membres. La procédure doit conserver le package, sa version, son identifiant, les sources et les résultats de tests.

La mise à jour doit inclure une analyse de compatibilité avec les données déjà présentes. Un nouveau chaincode peut rencontrer des clés ou des valeurs produites par une ancienne version. Les changements de schéma doivent être rétrocompatibles ou accompagnés d'une migration contrôlée. Une migration incorrecte peut rendre des actifs illisibles même si le nouveau code passe ses tests unitaires.

Les mises à jour doivent être préparées sur un canal de test avec une copie représentative des données. Le plan de publication doit expliquer quelles organisations approuvent la nouvelle définition, quelle politique d'endossement est requise, quels tests de régression sont exécutés et comment on observe le résultat après activation.

## 7. Endorsement policies et validation des transactions

Une endorsement policy définit quelles organisations ou quels peers doivent approuver la simulation d'une transaction pour qu'elle puisse être considérée valide. Elle exprime la règle de confiance du consortium : par exemple, une transaction de transfert peut nécessiter l'endossement de l'organisation qui détient l'actif et de l'organisation qui le reçoit. Le modèle réel dépend du besoin métier et de la configuration.

Le client propose une transaction ; les peers requis exécutent la simulation et renvoient des endorsements avec les résultats et la lecture/écriture prévue. L'application rassemble les endorsements requis et soumet la transaction. L'ordering établit un ordre et distribue le bloc. Les peers valident ensuite les signatures, la politique d'endossement et les conflits de version dans le modèle de validation. Une réponse positive à la simulation n'est pas encore la confirmation que la transaction a été validée et inscrite au ledger.

Il faut bien distinguer plusieurs statuts : proposition simulée, endorsements collectés, transaction soumise, bloc distribué, transaction validée ou invalidée et état courant mis à jour. L'application doit attendre le statut de commit et réagir si la transaction est invalide. Elle ne doit pas annoncer la réussite d'une opération métier simplement parce qu'un peer a renvoyé un résultat favorable pendant la simulation.

Les politiques trop faibles peuvent permettre à une organisation de valider seule une modification sensible. Les politiques trop strictes peuvent bloquer la disponibilité si un membre requis est temporairement indisponible. Le design doit choisir le bon niveau de contrôle, le tester avec des organisations absentes et documenter le compromis entre gouvernance et continuité.

~~~mermaid
sequenceDiagram
    participant App as Application
    participant P as Peers d'endossement
    participant O as Ordering service
    participant V as Validation du canal
    App->>P: Proposition de transaction
    P-->>App: Simulations et endorsements
    App->>O: Soumission des endorsements
    O->>V: Bloc distribué
    V-->>App: Transaction validée ou invalide
~~~

## 8. Données privées et collections privées

Les collections de données privées permettent à un sous-ensemble autorisé d'organisations d'échanger certaines valeurs qui ne doivent pas être diffusées à tous les membres du canal. Les données privées sont distribuées aux membres autorisés selon la configuration, tandis que le ledger partagé conserve des éléments permettant de vérifier l'engagement associé, comme le hash de la donnée. Ce mécanisme est différent d'un simple champ secret dans une application.

Une collection privée doit définir les membres, la politique d'endossement, les limites de rétention et les comportements lorsque les destinataires n'ont pas reçu la valeur. Le fait que le hash figure dans le ledger peut permettre de vérifier ultérieurement que la donnée présentée correspond à l'engagement, mais cela ne masque pas toutes les métadonnées. La taille, la fréquence, les transactions et les relations entre événements peuvent encore révéler des informations.

Le transient data field permet notamment d'envoyer des données privées qui ne doivent pas être incluses comme données ordinaires dans la proposition et les journaux publics. Il faut néanmoins contrôler ce que le client, les peers autorisés, le chaincode et l'application enregistrent. Une erreur de journalisation peut révéler une valeur confidentielle même si le mécanisme de collection est configuré correctement.

Choisis une collection privée pour des données qui ne concernent qu'un sous-ensemble de membres, et un canal distinct lorsque le périmètre général de participation ou de gouvernance diffère. Une application ne doit pas supposer que les deux mécanismes offrent les mêmes garanties. La politique de confidentialité doit décrire qui peut lire, qui peut proposer une modification, qui peut vérifier l'engagement et comment une partie autorisée récupère les données.

## 9. Modèle de données et chaincode métier

Un chaincode devrait exposer des opérations correspondant au domaine : créer un actif, enregistrer un changement de propriétaire, déclarer un événement de livraison, accepter une facture ou vérifier un statut. Un modèle générique qui accepte n'importe quel JSON et remplace toute valeur n'offre pas une politique métier claire. Définis les champs immuables, les états autorisés et les transitions valides.

Un actif peut être représenté par une clé stable et une structure qui contient son propriétaire courant, son état et les dates utiles. Le chaincode doit vérifier la validité de l'appelant, l'existence de l'actif et la possibilité de la transition. Si deux organisations tentent de mettre à jour la même valeur sur la base d'un état ancien, le mécanisme de validation peut détecter un conflit, mais l'application doit traiter ce résultat sans prétendre que les deux changements ont été appliqués.

Les identifiants doivent être conçus pour éviter les collisions et ne pas exposer inutilement des données personnelles. Une clé composée peut aider à séparer les espaces de noms. Les champs d'heure et de provenance doivent être définis selon le modèle de confiance ; l'heure fournie par un client ne prouve pas à elle seule qu'un événement s'est produit à cette heure.

## 10. Sécurité des identités et des clés

Le système repose sur les clés privées associées aux identités et aux composants de consensus ou de service. Les clés doivent être protégées, renouvelées, révoquées et attribuées selon des rôles précis. Une organisation devrait documenter qui a accès à ses identités d'administration, comment les sauvegardes sont sécurisées et comment réagir quand un poste ou un compte est compromis.

La gestion des certificats couvre les certificats expirés, les révocations, le renouvellement et la distribution des nouvelles autorités lorsque nécessaire. Les opérations sensibles ne doivent pas dépendre d'un unique ordinateur personnel ou d'un compte partagé sans traçabilité. Utilise des secrets séparés entre développement et production et évite d'inclure des fichiers de clés dans les images ou artefacts distribués.

Un plan d'incident doit établir quelles identités peuvent être suspendues, qui peut mettre à jour les politiques et comment les autres organisations sont informées. La révocation n'annule pas automatiquement les transactions déjà validées ; le processus doit distinguer l'arrêt d'une identité compromise, l'enquête historique et la correction de tout état métier incorrect.

## 11. Confidentialité, consentement et limites du registre

Un ledger immuable peut entrer en tension avec les besoins de correction ou de suppression des données. La première défense est la minimisation : n'enregistre que ce dont le besoin métier et les exigences d'audit justifient la conservation. Les données personnelles ou contractuelles sensibles devraient être stockées selon une stratégie de confidentialité adaptée, et le ledger peut contenir une référence ou un engagement si cela répond à l'objectif.

Le hash d'une donnée ne garantit pas toujours qu'elle soit anonyme. Si l'espace des valeurs est prévisible, un observateur peut tester des valeurs candidates et comparer leur hash. Des données peuvent aussi être déduites des événements, des heures, des relations entre organisations et des changements d'état. Les équipes doivent traiter les métadonnées comme une surface d'exposition.

Les collections privées ne remplacent pas une politique de gouvernance des données. Il faut documenter qui peut accéder aux données, combien de temps elles sont conservées, comment elles sont sauvegardées et comment un départ d'organisation est géré. Une copie déjà transmise à un membre autorisé peut subsister dans ses systèmes même après qu'il n'est plus membre du canal.

## 12. Observabilité et exploitation du réseau

L'exploitation doit surveiller les peers, les orderers, les certificats, les canaux, les chaincodes, les volumes, le retard de commit, les erreurs d'endossement et les conflits de validation. Les métriques doivent permettre de distinguer une proposition refusée, un peer hors ligne, une politique d'endossement impossible à satisfaire, un problème d'ordering et une transaction validée comme invalide.

Les logs doivent être horodatés et corrélés par un identifiant de transaction. Ne journalise pas les données privées ou les secrets. Les tableaux de bord doivent afficher les états qui comptent pour le métier, pas seulement le statut du processus. Un peer peut être en ligne mais ne pas satisfaire la politique requise, et une transaction soumise peut avoir été invalidée lors de la validation du bloc.

Le plan de sauvegarde inclut les données du ledger selon la stratégie du produit, les configurations et les preuves de configuration, mais protège séparément les identités et les clés. Les tests de restauration doivent confirmer que le réseau peut redémarrer et que les applications retrouvent un état cohérent. Une sauvegarde qui n'a jamais été restaurée n'est pas une procédure validée.

## 13. Choisir entre channels et collections privées

L'utilisation de plusieurs channels peut isoler les groupes de participants qui partagent un ledger. Cette méthode implique davantage de gouvernance : chaque canal dispose de sa configuration, de ses membres, de ses politiques et de son cycle de vie. Une donnée qui doit être cohérente entre deux canaux peut nécessiter des échanges applicatifs qui ne sont pas automatiquement atomiques.

Une collection privée peut permettre à plusieurs organisations de partager un canal commun tout en limitant l'accès à certaines données. Le choix est déterminé par les obligations de visibilité, la politique d'endossement, les besoins de coordination et le modèle d'exploitation. Les deux options doivent être comparées à une architecture où les données sensibles restent dans un système externe contrôlé et seule une preuve d'engagement est conservée dans le ledger.

Il faut aussi considérer le modèle de menace : une organisation membre du canal peut avoir accès à l'historique partagé, et une organisation membre d'une collection privée peut conserver les données qu'elle a légitimement reçues. Les mécanismes ne peuvent pas empêcher un participant autorisé de copier une donnée vers un système externe. Les contrats, contrôles techniques et obligations de gouvernance sont complémentaires.

## 14. Tests d'intégration et validation métier

Les tests doivent vérifier le cycle complet, pas seulement le résultat retourné par une fonction de chaincode. Prépare plusieurs organisations, des identités autorisées et non autorisées, des peers absents et des politiques d'endossement différentes. Vérifie la lecture avant et après l'écriture, l'état après commit, les conflits, les erreurs de certificat et les scénarios de reprise.

Un test de transaction doit distinguer la réponse de simulation et le résultat après validation du bloc. Un appel peut être endossé mais invalidé parce que la version de l'état a changé entre la lecture et la validation. L'application doit écouter l'événement de commit approprié et présenter un échec de validation comme un échec métier, même si un premier appel RPC a reçu un succès de simulation.

Les tests de confidentialité doivent tenter de lire une donnée depuis une organisation non membre de la collection, analyser les logs et vérifier que les données transitoires ne se retrouvent pas dans des systèmes qui ne doivent pas les recevoir. Les tests d'identité doivent couvrir la révocation, l'expiration et les rôles. Le plan de test doit également inclure les migrations de données et les mises à jour de chaincode.

## 15. Déploiement, mise à niveau et gouvernance

Un déploiement de production doit spécifier la topologie, les membres, les certificats, les configurations de channel, les politiques d'endossement, les chaincodes et les versions des composants. Les configurations doivent être versionnées et approuvées par les organisations requises. Les secrets ne doivent pas être partagés dans le dépôt, et les environnements de test et de production doivent être séparés.

Une mise à niveau peut changer le comportement du chaincode ou la manière d'interpréter des données existantes. Avant le déploiement, vérifie la compatibilité, teste la migration, identifie les organisations qui doivent approuver la nouvelle définition et prépare un plan de retour ou de reprise. Les changements de policy doivent être considérés comme des changements de confiance, pas comme une simple mise à jour technique.

La gouvernance du réseau doit décrire le processus d'admission et de départ des organisations, la révocation d'identités, les conflits, la résolution des désaccords et le financement de l'exploitation. Sans gouvernance durable, la technologie ne règle pas le problème de confiance entre participants.

## 16. TP guidé A : modéliser une chaîne logistique

Conçois un registre qui suit un lot de produits entre un fabricant, un transporteur et un distributeur. Définis les opérations autorisées pour chaque organisation : création du lot, prise en charge, réception, déclaration d'incident et clôture. Précise quelles données sont partagées avec tous les membres et lesquelles doivent rester privées entre deux parties.

### Correction proposée

Le modèle doit assigner une identité et des droits à chaque organisation. Les transitions doivent être explicites, et une réception ne devrait pas être enregistrée par un acteur qui n'a pas les droits correspondants. Les données commerciales sensibles peuvent être placées dans une collection privée ou hors chaîne selon le modèle de gouvernance ; le ledger doit conserver le minimum nécessaire à la vérifiabilité.

## 17. TP guidé B : concevoir une politique d'endossement

Choisis une opération de transfert d'actif et définis quelles organisations doivent l'endosser. Teste le cas où l'une des organisations requises est indisponible et celui où un peer retourne une simulation différente. Vérifie l'état réel après la validation du bloc.

### Correction proposée

La politique doit refléter le risque métier et les accords du consortium. Elle doit empêcher une organisation seule d'effectuer une modification sensible si ce n'est pas souhaité, sans rendre le réseau inutilement indisponible. L'application attend la validation finale et traite les conflits explicitement.

## 18. Étude de cas : une transaction est endossée mais invalide

Une application reçoit des réponses d'endossement positives, soumet la transaction et affiche immédiatement « Opération terminée ». Le bloc est ensuite livré, mais la transaction est marquée invalide parce que l'état a changé entre la simulation et la validation.

### Travail demandé

Décris les modifications d'interface et de backend, les événements à écouter, les contrôles d'idempotence et les métriques nécessaires pour éviter que l'application traite une transaction invalide comme réussie.

### Correction proposée

L'application doit séparer l'étape de simulation de l'étape de commit. Elle conserve l'identifiant de transaction, attend le statut de validation et applique l'effet métier seulement après confirmation. En cas d'invalidation, elle informe l'utilisateur, relit l'état pertinent et demande une nouvelle décision si nécessaire. Les tests doivent reproduire les conflits de version et vérifier qu'une même transaction ne crée pas de traitement métier dupliqué.

## 19. Validation des transactions, conflits et idempotence applicative

Une proposition endossée n'est pas encore une écriture définitive dans le ledger. La simulation lit un état à un moment donné et calcule un ensemble de lectures et d'écritures. Avant que la transaction soit validée, une autre transaction peut modifier une clé pertinente. Le mécanisme de validation peut alors déclarer la transaction invalide pour éviter qu'elle écrive sur la base d'une version devenue obsolète. Ce mécanisme protège la cohérence, mais exige une gestion applicative explicite des conflits.

L'application devrait distinguer proposition créée, endorsements reçus, transaction soumise, transaction incluse dans un bloc, statut de validation et résultat métier. Elle ne doit pas déclencher un paiement externe ou délivrer un service sur la seule base du résultat de simulation. Attends l'événement de commit et vérifie que la transaction est valide selon le statut défini pour la version de Fabric utilisée.

Les traitements qui réagissent aux événements doivent être idempotents. Un consommateur peut redémarrer ou recevoir une notification plusieurs fois. Il devrait enregistrer un identifiant stable de transaction, vérifier si l'effet métier a déjà été appliqué et exécuter la mise à jour dans une transaction locale appropriée. Lorsque le système répond à un changement d'état du ledger, conserve suffisamment de données pour réconcilier les opérations après interruption.

Le test doit provoquer un conflit de version : deux clients lisent le même actif, simulent des modifications différentes puis soumettent leurs transactions. Vérifie qu'une transaction est validée selon l'ordre et la politique, et que l'autre est traitée comme invalide sans qu'un service externe accomplisse malgré tout son effet. Cette distinction est critique pour les factures, transferts de propriété et traitements de commande.

## 20. Gouvernance d'un consortium et changements de membres

Un réseau permissionné repose sur des organisations qui acceptent de partager certaines responsabilités. La gouvernance doit définir l'admission d'un nouveau membre, les conditions de départ, les responsabilités de maintenance, les coûts, la gestion des certificats, les procédures d'urgence et la résolution des désaccords. Sans ces règles, les décisions techniques peuvent devenir des conflits opérationnels entre entreprises.

L'ajout d'une organisation modifie la configuration et parfois les politiques qui déterminent quelles signatures ou quels endorsements sont requis. Avant le changement, documente ce que le nouveau membre peut lire, quelles transactions il peut endosser, quels chaincodes il doit exécuter et comment ses certificats sont reconnus. Après le changement, vérifie que les politiques ont la portée attendue et que les canaux concernés reflètent la même décision.

Le départ d'un membre demande une analyse différente. Révoquer ses identités peut empêcher de nouvelles opérations, mais ne supprime pas les données qu'il a reçues lorsque sa participation était autorisée. Il faut examiner le traitement des clés, les collections privées, les archives détenues par le membre, les responsabilités contractuelles et les éventuels processus de migration. Les propriétés de confidentialité doivent être décrites sans promettre l'effacement de copies déjà distribuées.

Un consortium devrait consigner les décisions de gouvernance, les versions de configuration, les validations des organisations et les tests exécutés. Les changements sensibles doivent avoir un plan de communication et une procédure de repli. Une organisation qui contrôle seule tous les certificats ou toutes les mises à niveau doit être traitée comme une autorité centrale dans le modèle de menace, même si plusieurs entreprises exploitent des peers.

## 21. Haute disponibilité, ordering et plan de reprise

L'architecture opérationnelle doit prévoir plusieurs peers selon le besoin de disponibilité, des sauvegardes et une stratégie de reprise des composants d'ordering. Le nombre exact d'instances dépend du modèle de consensus et du déploiement choisi ; ne transpose pas mécaniquement une configuration d'exemple à un réseau de production. Vérifie la documentation correspondant à la version installée et teste le comportement lorsque des instances deviennent indisponibles.

Le plan de reprise identifie les données à sauvegarder, leur cadence, l'endroit où les copies sont stockées, les procédures de récupération et les responsables. Les identités et les clés exigent des protections distinctes des données du ledger. La restauration doit vérifier que le réseau reprend avec les mêmes membres, politiques, canaux et définitions de chaincode que l'état approuvé.

Mesure les objectifs de récupération. Le RPO indique la quantité de données que l'organisation accepte de perdre ; le RTO indique le délai cible pour revenir au service. Dans un registre distribué, la stratégie doit distinguer la récupération du processus, la resynchronisation du ledger, la reprise de l'application et la réconciliation des traitements externes. Un peer qui démarre ne prouve pas que toutes les opérations métier en attente ont été traitées.

L'exercice de reprise doit provoquer une panne contrôlée dans un environnement isolé. Vérifie la progression des blocs, la capacité à valider les transactions, les certificats, les politiques et les événements. Le rapport doit indiquer les écarts entre les objectifs et les résultats réels. Une sauvegarde dont la restauration n'a jamais été testée ne doit pas être considérée comme une garantie opérationnelle.

## 22. Sécurité de la chaîne d'approvisionnement du chaincode

Le code métier peut dépendre de bibliothèques, de runtimes, d'images de conteneur, de scripts de construction et d'outils de déploiement. Un changement non contrôlé dans une dépendance peut modifier le comportement du chaincode même si le code métier semble identique. Verrouille les versions, conserve les sommes de contrôle ou identifiants d'artefacts et examine les modifications au lieu de faire confiance automatiquement à une nouvelle version.

Le pipeline de publication doit séparer le travail de développement de l'autorisation de déployer. Les identités de CI ont besoin de droits limités et les secrets ne doivent pas être inclus dans les images ou les journaux. Archive le package installé, les sources, les paramètres et les validations nécessaires pour reconstruire l'origine de la version déployée.

La procédure de mise à niveau doit vérifier l'interface entre anciennes et nouvelles données, les politiques d'endossement et les changements de permission. Un test de compilation n'assure pas que le nouveau chaincode interprète correctement les actifs créés par l'ancienne version. Les jeux de données de test devraient comprendre des enregistrements réels représentatifs mais anonymisés, lorsque cela est possible et autorisé.

Après déploiement, compare la version active aux artefacts approuvés et surveille les erreurs, les conflits de validation, les changements de configuration et les appels inhabituels. Les preuves d'origine et de publication réduisent le risque de confusion lorsqu'un incident survient. Toute modification d'une politique ou d'un chaincode doit être rattachée à une décision de gouvernance et à des résultats de test.

## 23. Exercice : concevoir une politique de confidentialité exploitable

Une entreprise souhaite que trois organisations partagent l'état d'un produit, alors que le prix contractuel ne doit être connu que du vendeur et de l'acheteur. Compare un canal dédié, une collection privée et un stockage externe avec engagement dans le ledger. Pour chaque option, identifie les lecteurs, les données qui restent publiques, les politiques d'endossement et les contraintes de récupération.

La correction doit montrer que la confidentialité est un choix architectural. Un canal dédié isole un groupe de participants et son ledger, mais augmente la charge de gouvernance. Une collection privée peut limiter les valeurs partagées dans un canal commun, tandis qu'un hash de la donnée peut rester vérifiable par les autres membres. Un système externe peut limiter la diffusion mais ajoute une dépendance de disponibilité et exige de gérer les preuves et l'accès aux données.

La décision doit également traiter les métadonnées, les journaux, les sauvegardes, les copies déjà transmises et le départ d'une organisation. La confidentialité attendue doit être définie pour chaque donnée et testée avec une identité qui n'a pas le droit de la lire. Le rapport doit éviter de promettre une suppression totale ou un secret absolu sans preuve.

## 24. Atelier avancé : conflit, panne et reprise

Définis une opération métier qui modifie un actif partagé. Lance deux propositions en concurrence, rends un peer indisponible, puis restaure le composant et vérifie le statut final. Ajoute ensuite une opération qui exige des données privées et teste les accès avec des identités autorisées et non autorisées.

### Correction proposée

Le rapport distingue les erreurs de proposition, les erreurs d'endossement, les échecs de soumission et les transactions invalidées au commit. L'application ne produit un effet externe qu'après le résultat attendu. Les identités hors collection ne peuvent pas lire le contenu privé par les interfaces prévues ; les logs et exports sont aussi examinés. Après restauration, la configuration et l'état métier sont réconciliés.

## 25. Définir un contrat de service entre organisations

Le réseau technique n'est qu'une partie de l'exploitation. Les membres doivent convenir de qui finance l'infrastructure, qui répond aux incidents, quels délais de traitement sont attendus, comment les mises à niveau sont planifiées, comment les certificats sont renouvelés et quelles preuves doivent être partagées lors d'un désaccord. Les obligations devraient préciser les limites du service et les conséquences d'une indisponibilité.

Un contrat de service utile définit les indicateurs : disponibilité des peers requis, délai de validation, fréquence de sauvegarde, délai de révocation, délai de réponse au support et temps de restauration. Les indicateurs doivent correspondre à ce que l'application observe. Un processus qui est en ligne mais qui ne peut pas satisfaire l'endorsement policy n'est pas nécessairement disponible pour le métier.

La gouvernance doit contenir une procédure de changement qui synchronise la mise à jour des certificats, des politiques et des chaincodes. Les changements coordonnés entre organisations sont plus difficiles qu'une mise à jour dans une seule entreprise. La préparation, les tests partagés et les fenêtres d'intervention doivent être documentés pour réduire les divergences de configuration.

Le contrat de service doit aussi prévoir les conflits : quelle organisation décide d'une mesure d'urgence, qui peut interrompre une route de données, comment un incident est déclaré clos et comment un membre quitte le réseau. Les règles humaines ne sont pas exécutées par la blockchain mais déterminent si les composants techniques restent maintenus et si le consortium continue à fonctionner.

## 26. Runbook de diagnostic d'une transaction Fabric

Lorsqu'une transaction ne modifie pas l'état attendu, commence par collecter son identifiant, le channel, l'identité du client, le chaincode et la version, les peers sollicités, les endorsements reçus et le statut de commit. Ne conclus pas qu'une transaction a réussi à partir de la seule réponse de simulation. La confirmation utile est le résultat final de validation dans le ledger selon la version et l'API utilisées.

Si l'endorsement échoue, vérifie les peers sélectionnés, leur disponibilité, la découverte et la politique appliquée. Si la soumission échoue, examine le service d'ordering, les identités et la configuration du canal. Si le bloc est livré mais la transaction invalide, vérifie les conflits de version, les signatures et la politique d'endossement. Si la transaction est valide mais l'interface affiche un ancien état, examine l'indexation, les caches et le traitement de l'événement de commit.

La collecte de données doit rester limitée aux informations nécessaires. Les journaux ne doivent pas contenir les valeurs privées, les clés ou les identifiants sensibles. Un dossier de diagnostic doit indiquer ce qui est observé, ce qui reste une hypothèse et les prochaines vérifications. Les commandes de lecture devraient précéder les changements de configuration, afin de préserver les preuves et d'éviter de rendre le problème plus difficile à reproduire.

Le runbook définit les critères de clôture : résultat de validation connu, état courant cohérent, traitement applicatif exécuté une seule fois et cause soit confirmée soit explicitement laissée ouverte avec un propriétaire. Une transaction qui n'a pas produit l'effet attendu ne doit pas être soumise de nouveau sans vérifier si elle a déjà été commitée, car une répétition métier peut créer un effet double.

## 27. Contrôler la confidentialité dans les applications clientes

Les données privées ne sont pas protégées uniquement par la configuration du ledger. L'application cliente peut les conserver dans les logs, les systèmes de suivi, les sauvegardes, les caches, les messages d'erreur ou les outils analytiques. Il faut cartographier le cycle de vie des données depuis la saisie, la proposition et le traitement du chaincode jusqu'à la lecture, l'archivage et la suppression selon la politique applicable.

Pour chaque champ sensible, indique qui doit pouvoir le lire, qui peut le modifier, où il transite et où il peut être conservé. Les données transitoires doivent être envoyées uniquement aux organisations nécessaires, et les policies de collection doivent correspondre à ce périmètre. Un test devrait vérifier non seulement que l'organisation non autorisée ne peut pas lire la valeur via le ledger, mais aussi qu'elle ne la reçoit pas par les logs ou le canal de support.

La séparation des environnements est essentielle. Les données de production ne doivent pas être copiées dans un environnement de test sans analyse et protections adéquates. Les données synthétiques ou anonymisées peuvent permettre de reproduire des scénarios. Les exports et rapports doivent masquer les champs qui ne sont pas nécessaires au diagnostic.

Les exigences de conservation doivent être définies par donnée. Le ledger peut garder des preuves de transactions et des hashes même si l'application retire une copie métier. Les collections privées peuvent également laisser des engagements ou des métadonnées. Les promesses de suppression doivent donc préciser ce qui est supprimé, par quel acteur et ce qui reste dans l'historique distribué.

## 28. Gestion des événements et intégration aux systèmes métier

Une application d'entreprise utilise souvent le ledger avec une base de données, un ERP, un système logistique ou un service de facturation. Les systèmes peuvent se désynchroniser lorsqu'une transaction est invalidée, lorsqu'un événement arrive en retard ou lorsqu'un service tombe en panne après le commit. Il faut définir quelle source fait autorité pour chaque étape et comment les écarts sont réconciliés.

Le traitement des événements doit être idempotent. Enregistre l'identifiant de transaction et le type d'événement, vérifie si l'effet métier est déjà appliqué puis écris l'état local dans une transaction appropriée. Si le service a traité l'événement mais perdu sa réponse, un nouvel essai ne doit pas créer une deuxième facture ou livraison. La reprise doit pouvoir reconstruire les événements manquants à partir de la source définie.

Il faut distinguer les événements émis par le chaincode des statuts de validation des transactions. Une application ne devrait pas exécuter un effet externe uniquement parce qu'elle a observé une réponse de simulation. Elle doit lier l'effet au résultat de commit qui confirme la validité et la mise à jour du ledger.

Les tests d'intégration devraient inclure un événement dupliqué, un service arrêté après commit, une transaction invalide et un retard d'indexation. Le résultat attendu est une base métier qui peut être reconstruite ou réconciliée sans perdre la traçabilité. Le dossier doit documenter comment gérer une divergence durable et qui peut autoriser une correction manuelle.

## 29. Planifier les changements d'une politique d'endossement

Modifier une endorsement policy change le niveau de confiance et la disponibilité de certaines opérations. Avant le changement, identifie les organisations requises, les transactions concernées, les cas où un membre est indisponible et les conséquences d'une approbation insuffisante. Une politique plus stricte peut améliorer la séparation des pouvoirs mais bloquer les opérations si trop d'organisations doivent être simultanément actives.

Prépare une matrice qui relie chaque opération métier aux membres nécessaires pour simuler et valider. Teste au moins un cas nominal, un membre absent, un endorsement signé par un acteur inattendu et une configuration partiellement mise à jour. Vérifie que les organisations convergent vers la définition attendue sur le canal et que l'application ne continue pas d'utiliser une politique supposée qui n'est pas active.

La modification doit être approuvée selon le processus de gouvernance. Archive la définition, les signatures ou approbations, la version du chaincode et les résultats des tests. Après activation, observe les taux de succès, les erreurs d'endossement et les cas de validation invalide. Si la disponibilité se dégrade, analyse d'abord les politiques et les dépendances avant de réduire le niveau de sécurité de façon improvisée.

Une procédure de retour doit être réaliste. Si le changement a déjà été commité dans la configuration du canal, le retour exige la procédure de mise à jour prévue et les approbations requises. Ne suppose pas qu'un simple changement de fichier rétablit l'état du réseau. Le runbook doit nommer la source de vérité et les critères de validation de la nouvelle configuration.

## 30. Comité d'exploitation et revue de sécurité périodique

Un réseau Fabric de production doit avoir un comité d'exploitation qui rassemble les responsabilités techniques et métier nécessaires : identité, peers, ordering, chaincodes, données privées, supervision et support. Chaque organisation doit connaître les contacts d'escalade et les responsabilités qu'elle conserve. Les décisions d'urgence, la rotation de clés et les mises à niveau doivent être préparées avant de survenir.

Une revue périodique contrôle les certificats, les MSP, les permissions, les versions des images, les dépendances de chaincode, les politiques d'endossement, les collections privées et la configuration des canaux. Les changements depuis la dernière revue doivent être traçables. Une identité qui a quitté l'entreprise, un certificat expiré ou une organisation qui ne suit plus le processus d'approbation peut affecter la sécurité et la disponibilité.

Le comité doit également vérifier les exercices de restauration et de réponse à incident. Les sauvegardes, l'accès aux clés, les procédures de révocation et les runbooks doivent être testés par une personne différente de celle qui les a écrits. Un document obsolète peut rendre un réseau permissionné aussi difficile à exploiter qu'un système mal documenté.

La revue se conclut par des constats avec gravité, responsable et échéance. Les risques acceptés doivent être documentés par les parties appropriées et réexaminés lorsque la topologie, les données ou les obligations changent. La gouvernance doit être capable de répondre à la question : qui décide et qui agit quand les participants ne sont pas d'accord sur une correction ?

## 31. Capacité, dimensionnement et objectifs de service

Le dimensionnement d'un réseau Fabric doit partir du profil des transactions et des objectifs métier. Une charge dominée par des lectures, une charge de mises à jour fréquentes et une charge de transactions qui exigent plusieurs endorsements produisent des profils différents. La taille des blocs, le nombre de peers, la topologie d'ordering, la latence entre organisations et le coût du chaincode affectent les performances de bout en bout.

Prépare un benchmark représentatif. Fixe les versions, les données de test, le nombre de clients, la proportion de lectures et d'écritures, la taille des transactions, les politiques d'endossement et la durée. Mesure le débit soutenu, les percentiles de latence, les erreurs de simulation, les conflits, le temps de commit et les ressources de chaque composant. Un pic bref ne démontre pas la capacité de soutenir un service critique pendant plusieurs heures.

Les objectifs de service doivent être exprimés au niveau métier : délai pour qu'une mise à jour soit confirmée, proportion de transactions valides, temps de restauration et délai de révocation d'une identité compromise. Les métriques de processus restent nécessaires, mais un peer en ligne n'est pas suffisant si les policies ne peuvent pas être satisfaites ou si l'application ne reçoit pas les événements de commit.

Après un changement de topologie, de policy ou de chaincode, répète les tests de référence et compare les résultats. Si le débit augmente mais que les conflits ou les transactions invalides augmentent aussi, la décision doit analyser ce compromis. Le rapport doit expliquer les limites du test et ne pas promettre un niveau de service que l'architecture n'a pas démontré.

## 32. Séparer les responsabilités de développement et d'exploitation

Le développement du chaincode, l'administration des identités, la gestion de l'ordering, la publication de configuration et le support métier devraient être attribués à des rôles définis. Une personne peut occuper plusieurs rôles dans un laboratoire, mais la production devrait évaluer le risque de concentration. Une seule identité qui peut modifier le code, approuver la définition et utiliser les clés d'administration augmente l'impact potentiel d'une compromission.

Les pipelines de développement doivent produire des artefacts vérifiables et les faire approuver avant publication. Les identités de CI doivent avoir des droits limités et les secrets doivent être gérés hors du code. Les organisations qui approuvent une définition devraient vérifier la version, le package, les tests et les politiques avant de signer leur approbation.

Les responsabilités ne s'arrêtent pas après l'installation. L'exploitation doit renouveler les certificats, appliquer les correctifs, surveiller les composants, sauvegarder les données et tester la reprise. Le développement doit maintenir les tests de régression et documenter les migrations. Les responsables métier doivent vérifier que les règles du chaincode reflètent toujours les processus et contrats entre entreprises.

Une matrice RACI ou un mécanisme équivalent peut rendre ces responsabilités explicites. Pour les incidents, indique qui détecte, qui décide, qui exécute, qui communique et qui approuve la reprise. Cette gouvernance évite qu'un réseau fonctionne techniquement sans qu'aucune équipe ne soit clairement responsable d'un problème métier.

## 33. Évaluer les alternatives à Fabric

Fabric doit être comparé aux alternatives avec les mêmes exigences : base de données partagée, preuve cryptographique, signatures d'organisation, journal d'audit, permissions et confidentialité. Une base répliquée avec un journal append-only peut être plus simple lorsque toutes les parties font confiance à un seul opérateur. Un registre distribué est plus pertinent lorsque plusieurs organisations doivent vérifier les règles et les changements sans déléguer tout le contrôle à l'une d'elles.

Le modèle permissionné implique des responsabilités d'adhésion et de gouvernance. Il peut simplifier la confidentialité et l'identité, mais demande aux participants de maintenir les certificats, l'infrastructure, les policies et les versions du chaincode. Les coûts de coordination entre organisations peuvent dépasser les gains d'automatisation si le besoin métier est petit ou le processus est rarement utilisé.

Une évaluation doit identifier les propriétés indispensables. Si l'exigence principale est la preuve qu'un document existait à une date donnée, un hash signé ou un service d'horodatage peut suffire. Si l'exigence est que plusieurs organisations valident collectivement une mutation d'actif, un ledger partagé avec policies explicites peut être adapté. Si la priorité est le contrôle d'accès complexe et la mise à jour fréquente, un système de données classique peut être plus simple.

La recommandation finale devrait exposer le coût d'exploitation, la gouvernance, les responsabilités, les limites de confidentialité et la stratégie de sortie. Le choix ne doit pas être justifié uniquement par le fait que la blockchain paraît plus moderne ; il doit résoudre un problème vérifiable que les alternatives ne résolvent pas aussi simplement.

## 34. Checklist de préparation à la production

Avant la mise en production, confirme la version de Fabric, la topologie, le modèle d'identité, les certificats, les clés, les canaux, les collections privées, les endorsement policies, le cycle de vie du chaincode et le plan de reprise. Les versions des images et des CLI doivent être compatibles, et les configurations doivent être approuvées par les organisations concernées.

Teste les transactions nominales et les échecs : identité expirée, peer indisponible, endorsement manquant, transaction invalide, conflit de version, donnée privée lue par une organisation non autorisée et restauration après panne. Vérifie l'état après commit, pas seulement les réponses des premiers appels RPC. Les sauvegardes et les procédures de renouvellement de certificats doivent être testées avant les incidents.

Archive le code, les packages, les résultats de tests, la configuration et les décisions de gouvernance. Vérifie après publication que les rôles et les politiques actives correspondent à ce qui a été approuvé. Le lancement devrait être bloqué si une identité privilégiée est inconnue, si la procédure de révocation n'est pas testée ou si l'application ne distingue pas simulation et commit.

La revue doit également confirmer que chaque alerte a un responsable, que les runbooks sont accessibles et que les membres savent comment joindre les autres organisations lors d'un incident. La préparation à la production est un processus technique et organisationnel ; elle ne se réduit pas à démarrer tous les conteneurs.

## 35. Gestion des certificats expirés et des identités compromises

Les identités Fabric doivent être maintenues pendant tout le cycle de vie du réseau. Un certificat expiré peut empêcher un client ou un composant de s'authentifier, tandis qu'une clé compromise peut permettre à un acteur de se présenter comme une identité légitime avant que les contrôles appropriés prennent effet. Le processus d'émission et de renouvellement doit être documenté par organisation.

Un runbook doit indiquer comment identifier le certificat concerné, confirmer les usages et les dépendances, révoquer ou renouveler les identités selon les mécanismes de la version, puis vérifier l'effet sur les applications. Une révocation ne doit pas interrompre plus de services que nécessaire ; cependant, la continuité ne doit pas servir de raison pour maintenir une identité compromise. Les permissions doivent être testées après le changement.

La procédure de récupération doit distinguer l'arrêt d'une identité compromise des transactions déjà validées. Le ledger conserve l'historique selon ses règles, et une révocation ne réécrit pas automatiquement le passé. Si des transactions frauduleuses ont été validées, le consortium doit appliquer sa procédure de résolution métier et conserver les preuves plutôt que prétendre que le registre a annulé les événements.

Les clés d'administration, les identités des applications et celles des utilisateurs devraient être séparées. Les copies de sauvegarde doivent être protégées et la rotation testée en laboratoire. Le rapport de changement documente les certificats concernés, les dates, les approbations, les tests et les éventuels effets sur les transactions en attente.

## 36. Stratégie de sauvegarde et restauration vérifiable

La sauvegarde d'un réseau Fabric comprend plus que le répertoire d'un peer. La stratégie doit identifier les données de ledger, les configurations, les définitions de chaincode, les configurations de canal et les artefacts nécessaires au redémarrage. Les certificats et les clés sont traités comme des éléments sensibles avec des contrôles d'accès et une politique distincte.

Définis un RPO et un RTO pour chaque service métier. Le RPO décrit la perte de données acceptable, et le RTO le délai visé pour restaurer la fonction. La restauration d'un peer, la remise en ligne de l'ordering et la reprise d'une application ne sont pas nécessairement la même étape. Les opérations métier hors chaîne doivent pouvoir être réconciliées avec le ledger après une interruption.

Réalise une restauration dans un environnement isolé, puis compare les canaux, les versions de chaincode, les rôles, les politiques, la progression des blocs et les résultats de lecture. Teste également que les identités expirées ou révoquées ne retrouvent pas un accès involontaire à la suite de la restauration. La sauvegarde n'est validée que si le service retrouve un état cohérent et si la procédure peut être reproduite.

Archive les journaux de test, les versions des outils et les écarts. Si la restauration prend plus de temps que prévu, identifie si la cause relève du stockage, de la configuration, des clés ou de la synchronisation. Le plan doit se conclure par des améliorations mesurables, et non par une simple case « sauvegarde configurée ».

## 37. Choix de topologie : plusieurs peers, plusieurs organisations et plusieurs domaines de panne

Le nombre de peers doit être déterminé selon les besoins de validation, de lecture, de disponibilité et de distribution des responsabilités. Plusieurs peers au sein d'une même organisation améliorent certaines capacités, mais ne remplacent pas une diversité entre organisations. Si une seule organisation contrôle toutes les identités, les politiques et le service d'ordering, le modèle de gouvernance peut rester centralisé malgré une topologie redondante.

Analyse les domaines de panne : processus, machine, zone, fournisseur cloud, organisation, autorité de certification et service réseau. Une architecture de haute disponibilité devrait éviter de placer tous les composants critiques dans le même domaine lorsqu'une panne commune serait inacceptable. La diversité doit être réelle et testée, pas seulement annoncée dans un diagramme.

Les performances et la sécurité doivent être mesurées ensemble. Une politique qui exige trop d'organisations simultanément peut améliorer les approbations mais réduire la disponibilité. À l'inverse, une politique trop permissive peut permettre une écriture sensible avec une seule identité. Simule les absences et vérifie les transactions que le métier doit encore pouvoir effectuer.

La note de décision devrait expliquer pourquoi la topologie choisie correspond aux objectifs de service, quelles dépendances résiduelles existent et comment les opérateurs vérifient les changements. Les coûts, le support et la maintenance des identités doivent faire partie du modèle de capacité.

## 38. Procédure de clôture d'un incident Fabric

La clôture doit confirmer la cause, l'effet sur le ledger et l'état métier. Vérifie l'identifiant de transaction, le statut de validation, l'état courant, les événements reçus par l'application et les effets hors chaîne. Si la cause n'est pas certaine, indique ce qui reste une hypothèse et assigne un suivi au lieu de déclarer arbitrairement l'incident résolu.

Le rapport conserve la configuration active, les versions, les certificats ou politiques impliqués, les métriques avant et après, les actions opérateur et les preuves de récupération. Les journaux privés ou sensibles doivent être limités à l'audience autorisée. Une mesure corrective doit inclure un test de régression et une mise à jour du runbook si la procédure initiale était incomplète.

Avant de rouvrir les opérations métier, vérifie les transactions en attente, les identités utilisées, les politiques d'endossement et la disponibilité des composants requis. Les données locales et le ledger doivent être réconciliés, et l'application doit éviter de rejouer des effets déjà appliqués. Le retour à un statut de service normal exige une preuve de stabilité correspondant aux objectifs définis.

## 39. Critères de clôture de la mise en production

La mise en production est prête lorsque les identités, les politiques, les chaincodes, les collections privées, les dépendances et les procédures de restauration ont été vérifiés sur l'environnement cible. La liste de vérification doit être liée à des preuves — versions, résultats de test, configuration approuvée et transactions de validation — plutôt qu'à de simples déclarations.

Teste une transaction de bout en bout avec les identités prévues et attends le statut de validation. Vérifie que l'état courant est correct, que les événements ont été consommés une seule fois et que l'application a réagi au commit plutôt qu'à une simulation. Les accès aux données privées doivent être contrôlés à partir d'une identité qui n'est pas membre de la collection.

La clôture comprend aussi le plan de surveillance, les contacts d'escalade, le propriétaire des sauvegardes et la procédure de renouvellement des certificats. Si une propriété de sécurité reste inconnue, documente le risque et décide si le lancement doit être limité ou reporté. Une mise en production n'est pas validée simplement parce que tous les processus sont démarrés.

## 40. Questions d'entraînement avec corrigé

### Question 1 : Fabric est-il une blockchain publique sans jeton ?

**Correction :** Non. C'est une plateforme permissionnée avec des identités et des politiques définies par les organisations. Son architecture et son modèle de confiance diffèrent d'une blockchain publique.

### Question 2 : Quel est le rôle d'un peer ?

**Correction :** Il héberge une copie du ledger concernée, peut exécuter des chaincodes pour simuler des propositions, endosse selon les politiques et valide les transactions reçues.

### Question 3 : Quel est le rôle du service d'ordering ?

**Correction :** Il établit l'ordre des transactions et distribue les blocs. Il ne joue pas simplement le rôle d'un peer exécutant toute la logique métier.

### Question 4 : Qu'est-ce qu'un MSP ?

**Correction :** Le MSP définit la manière dont les identités sont reconnues et les règles de confiance applicables dans le réseau.

### Question 5 : Une transaction endossée est-elle déjà commitée ?

**Correction :** Non. L'application doit distinguer simulation, endorsements, soumission, distribution du bloc et résultat de validation.

### Question 6 : À quoi sert une endorsement policy ?

**Correction :** Elle détermine quelles identités ou organisations doivent endosser une transaction pour qu'elle puisse être validée selon la configuration.

### Question 7 : Les collections privées empêchent-elles tout membre autorisé de copier une donnée ?

**Correction :** Non. Elles limitent les participants qui reçoivent les données dans le système, mais un participant autorisé peut conserver une copie externe.

### Question 8 : Quand utiliser un channel distinct ?

**Correction :** Lorsque le périmètre de participation, le ledger partagé ou la gouvernance diffère de manière significative. Pour certaines valeurs privées dans un canal commun, une collection peut être plus adaptée.

### Question 9 : Pourquoi versionner la définition du chaincode ?

**Correction :** Pour rendre les changements traçables, les approbations explicites et la procédure de reprise reproductible.

### Question 10 : Une blockchain garantit-elle que les données métier saisies sont vraies ?

**Correction :** Non. Elle permet de partager et vérifier des écritures selon les règles du réseau, mais la véracité des données externes dépend des identités, des preuves et des processus métier.

## 41. Challenge final : architecture d'un consortium

Un consortium de quatre entreprises veut suivre des actifs, protéger certains prix contractuels et conserver un historique vérifiable des transferts. Chaque organisation doit pouvoir vérifier les opérations qui la concernent, mais aucune ne doit avoir un contrôle unilatéral du registre partagé.

### Travail demandé

Rédige une proposition avec les organisations, peers, orderers, channels, MSP, politiques d'endossement, collections privées, cycle de vie du chaincode, surveillance et gestion des incidents. Ajoute un plan de test pour les organisations indisponibles et les transactions invalides.

### Correction proposée

La proposition sépare les responsabilités et identifie le modèle de gouvernance. Les données qui doivent être partagées sont inscrites dans le ledger commun, tandis que les valeurs sensibles sont limitées aux organisations concernées selon une stratégie explicite. Les politiques d'endossement traduisent les accords métier, et les tests prouvent ce qui arrive lorsqu'un membre requis est indisponible.

Le plan de production inclut la gestion des certificats et des clés, des mises à niveau approuvées, la surveillance des statuts de validation et la restauration. Il documente aussi les limites : un ledger partagé ne prouve pas qu'une déclaration du monde réel est vraie, et la confidentialité technique doit être complétée par des responsabilités de gouvernance.

## Glossaire

**Hyperledger Fabric** : plateforme de registre permissionnée organisée autour d'organisations, de peers, d'ordering et de politiques.

**Peer** : nœud qui héberge un ledger et peut exécuter ou valider des transactions.

**Ordering service** : service qui établit l'ordre des transactions et distribue les blocs.

**MSP** : composant logique qui définit les règles de reconnaissance des identités.

**CA** : autorité de certification qui émet et gère des certificats.

**Channel** : domaine logique dont les organisations participantes partagent la configuration et le ledger.

**Chaincode** : logique métier exécutée par les peers pour simuler des propositions.

**Endorsement policy** : règle déterminant les approbations requises pour une transaction.

**Collection de données privées** : mécanisme qui restreint la diffusion de certaines valeurs à des organisations autorisées.

**Ledger** : historique des transactions associé à l'état courant.

**Commit** : résultat de validation de la transaction dans le ledger, distinct d'une simple simulation.

**Transient data** : données envoyées dans le contexte d'une proposition sans être conservées comme données ordinaires sur le ledger.

## Pour aller plus loin

- Documentation Hyperledger Fabric : https://hyperledger-fabric.readthedocs.io/en/latest/
- Structure du réseau : https://hyperledger-fabric.readthedocs.io/en/latest/network/network.html
- Politiques d'endossement : https://hyperledger-fabric.readthedocs.io/en/latest/policies/policies.html
- Gateway Fabric : https://hyperledger-fabric.readthedocs.io/en/latest/gateway.html
- Collections de données privées : consulter le tutoriel officiel de la version retenue.

Les concepts et commandes peuvent évoluer selon la version de Fabric. Épingle les versions des images et des outils dans le déploiement et utilise les pages officielles correspondant à cette version pour la configuration de production.
