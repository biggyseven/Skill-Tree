# Gestion des identités et des accès avancée

> **Mise en contexte**

Une entreprise possède un annuaire central, un fournisseur d’identité cloud, plusieurs applications web, des comptes techniques, des clusters Kubernetes et des pipelines de livraison. Chaque équipe a ajouté au fil du temps des groupes, des rôles, des clés API et des exceptions. Un salarié qui a changé de fonction conserve encore des droits de son ancien poste ; un compte de service possède des permissions administratives parce que son propriétaire craignait de bloquer une tâche automatique ; une application accepte un jeton valide sans vérifier que l’utilisateur a le droit d’accéder à la ressource demandée.

L’authentification fonctionne, mais le système d’accès ne garantit plus que chaque identité exerce uniquement les actions nécessaires. Une compromission de compte peut alors ouvrir un chemin vers des données sensibles, les environnements cloud ou les mécanismes de déploiement.

La gestion avancée des identités et des accès, ou IAM, vise à établir une relation contrôlée entre une identité, une action, une ressource, un contexte et une décision. Elle dépasse le simple écran de connexion. Elle englobe le cycle de vie des identités humaines et techniques, les méthodes d’authentification, la fédération, les modèles d’autorisation, les permissions temporaires, les comptes privilégiés, la gouvernance, la surveillance et la réponse aux incidents.

Le fil conducteur de ce cours est une organisation fictive appelée Atlas Formation. Elle héberge une plateforme pédagogique, une API, une base de données, un registre d’images, un pipeline CI/CD et un cluster Kubernetes. Votre mission est de concevoir un modèle d’accès qui reste compréhensible lorsque l’organisation grandit, que les utilisateurs changent de rôle et que les services sont automatisés.

## 1. Les fondations : identité, authentification et autorisation

Une **identité** est une représentation d’un sujet dans un système : personne, service, application, appareil ou processus. Elle est associée à des attributs et à un cycle de vie. Un identifiant, comme un nom d’utilisateur ou un identifiant de service, sert à retrouver cette représentation ; il n’est pas à lui seul une preuve d’identité. Deux systèmes peuvent utiliser des identifiants différents pour la même personne, et un identifiant réutilisé sans contrôle peut provoquer l’héritage involontaire d’anciens droits.

L’**authentification** établit que le sujet contrôle un ou plusieurs moyens reconnus par le système. Elle répond à la question « qui présente cette preuve ? ». L’**autorisation** décide ce que ce sujet peut faire sur une ressource donnée. Elle répond à « cette action précise est-elle permise dans ce contexte ? ». La **gestion des comptes** englobe la création, les modifications, la suspension et la suppression des identités et de leurs accès. La **comptabilisation** et l’audit rendent les décisions et actions traçables.

Ces fonctions se complètent, mais ne se remplacent pas. Un utilisateur peut être correctement authentifié et pourtant ne pas avoir le droit de lire le dossier demandé. Inversement, un contrôle d’autorisation parfait ne compense pas un compte volé si l’attaquant peut se présenter comme son propriétaire.

~~~text
Sujet
  |
  v
Identification : quelle identité est revendiquée ?
  |
  v
Authentification : la preuve est-elle valide ?
  |
  v
Contexte : appareil, session, risque, heure, ressource
  |
  v
Autorisation : cette action est-elle permise ?
  |
  v
Action + journal d'audit + surveillance
~~~

Le modèle d’accès doit aussi tenir compte du sujet réel. Un navigateur agit au nom d’un utilisateur ; une API peut agir au nom d’un service ; une tâche planifiée peut être lancée par un orchestrateur ; un pipeline peut obtenir une identité temporaire auprès d’un fournisseur cloud. Ces identités n’ont pas les mêmes besoins et ne doivent pas partager arbitrairement les mêmes secrets ou groupes.

## 2. Modèle de menace IAM

L’IAM est une surface d’attaque parce qu’il contrôle les chemins permettant d’accéder aux actifs. Les menaces incluent le vol de mot de passe, le phishing, le détournement d’une session, l’abus des jetons OAuth, l’attribution excessive de privilèges, la création d’un compte technique clandestin, la persistance d’un ancien accès, la falsification d’attributs et le contournement des vérifications dans une API.

Commencez par inventorier les actifs : données personnelles, dépôt source, registre d’images, comptes cloud, clés de signature, base de production, console d’administration et outils de gestion d’identités. Pour chaque actif, définissez les actions sensibles, les sujets qui en ont besoin, l’impact d’un accès abusif et les preuves qui permettront de détecter une anomalie.

~~~text
ACTIF                     CHEMIN D'ATTAQUE POSSIBLE
-----------------------   -----------------------------------------
Données pédagogiques      Compte enseignant compromis
Base de production        Jeton de service trop privilégié
Dépôt source              Compte développeur détourné
Cloud                     Rôle fédéré mal restreint
Cluster Kubernetes        Création de Pod avec compte puissant
Console IAM               Droit d'attribuer des rôles à soi-même
Journaux                  Accès d'édition ou suppression non contrôlé
~~~

Une analyse de menace IAM doit identifier les chemins d’escalade : un utilisateur qui peut modifier un groupe peut-il s’y ajouter lui-même ? Un opérateur capable de créer un compte peut-il lui attribuer le rôle administrateur ? Un développeur pouvant lancer un pipeline peut-il obtenir les identifiants de production ? Un service pouvant créer des Pods peut-il choisir un compte de service déjà privilégié ? Il faut examiner les relations entre permissions, et pas seulement la liste des rôles.

Évaluez aussi les menaces organisationnelles. Les comptes orphelins, les accès temporaires qui ne sont jamais retirés, les propriétaires inconnus, les comptes partagés et les exceptions permanentes sont des problèmes de sécurité. Un système IAM peut être techniquement robuste tout en restant fragile si personne ne sait qui doit valider un accès ou désactiver une identité devenue inutile.

Le risque se réduit par des contrôles complémentaires : preuve d’identité adaptée au risque, authentification robuste, autorisation systématique, permissions minimales, révision périodique, journalisation et détection. Aucun de ces contrôles ne doit être considéré comme l’unique barrière.

## 3. Référentiels et niveaux d’assurance

NIST SP 800-63-4, publiée en 2025, présente les lignes directrices relatives à l’identité numérique, à la preuve d’identité, à l’authentification et à la fédération. Elle remplace la révision 3. Ce référentiel distingue plusieurs dimensions d’assurance, qu’il ne faut pas confondre : l’assurance de la preuve d’identité, l’assurance de l’authentification et l’assurance des échanges fédérés. Une organisation doit choisir ses exigences selon les risques, les données et les obligations applicables, plutôt que d’appliquer partout la vérification la plus lourde.

La preuve d’identité cherche à établir qu’une personne est celle qu’elle prétend être lors de l’enrôlement. L’authentification cherche ensuite à vérifier qu’elle contrôle les moyens reconnus. La fédération permet à un système de s’appuyer sur une assertion d’un autre système selon une relation de confiance établie. Une assertion fédérée fiable ne dispense pas l’application destinataire d’appliquer ses propres règles d’autorisation.

~~~text
Enrôlement et preuve d'identité
             |
             v
Compte et facteurs d'authentification
             |
             v
Authentification à chaque session
             |
             v
Assertion fédérée éventuelle
             |
             v
Contrôle d'accès propre à l'application
~~~

Les niveaux d’assurance ne sont pas des étiquettes marketing. Ils servent à relier la force des mécanismes à la conséquence d’une compromission. Pour une application de faible risque, une démarche d’enrôlement proportionnée peut suffire. Pour un accès administratif à des ressources sensibles, l’organisation peut exiger une authentification résistante au phishing, une session courte, un appareil administré et une élévation de privilège temporaire.

Un cadre comme NIST SP 800-207 sur l’architecture Zero Trust complète cette réflexion : le réseau où se trouve un utilisateur ne constitue pas une preuve suffisante de confiance. L’identité, l’appareil, la ressource et le contexte doivent être évalués au moment d’autoriser l’accès. Zero Trust ne signifie pas « demander une authentification à chaque clic » sans réflexion ; il signifie ne pas accorder de confiance implicite basée uniquement sur la position réseau ou la propriété de l’appareil.

## 4. Annuaire, fournisseur d'identité et source de vérité

Un annuaire stocke des objets et attributs d’identité, des groupes et parfois des relations hiérarchiques. Un fournisseur d’identité, ou IdP, réalise ou orchestre l’authentification et peut émettre des assertions vers les applications. Une application peut déléguer la connexion à un IdP tout en conservant ses propres règles d’accès. Ces rôles sont parfois fournis par le même produit, mais il faut distinguer les responsabilités logiques.

La source de vérité RH peut indiquer les personnes actives, leur statut, leur service et leur responsable. Un système de gestion des accès peut convertir ces informations en demandes d’accès et en règles. L’annuaire central distribue les comptes et groupes. L’IdP authentifie les utilisateurs. Les applications consomment les identités et prennent leurs décisions d’autorisation. La chaîne doit préciser quel système fait autorité sur chaque attribut.

~~~text
Système RH / registre des collaborateurs
             |
             v
Moteur de cycle de vie IAM
             |
      +------+------+
      v             v
   Annuaire        Approbations et rôles
      |             |
      v             v
     IdP -------> Applications
                   |
                   v
             Autorisation locale
~~~

Il ne faut pas permettre à chaque application de maintenir une copie indépendante et incontrôlée des rôles. Une approche centralisée aide à révoquer les comptes, mais l’application doit tout de même vérifier l’autorisation sur chaque ressource et éviter d’utiliser un attribut non vérifié. Définissez des identifiants stables, la règle de rapprochement des comptes et la procédure de résolution des doublons.

L’attribut « département » ou « fonction » peut être utile dans une politique, mais il doit avoir un propriétaire et une qualité connue. Si l’application fait confiance à un attribut que l’utilisateur peut modifier, la décision d’accès est manipulable. Les attributs doivent être validés, limités aux émetteurs autorisés et protégés pendant leur transport.

## 5. Protocoles : SAML, OpenID Connect et OAuth 2.0

SAML est un standard de fédération souvent employé dans des environnements d’entreprise. Il utilise des assertions signées et des échanges définis entre un fournisseur d’identité et un fournisseur de service. La sécurité dépend de la validation de la signature, de l’émetteur, de l’audience, de la destination, de la durée de validité et des paramètres de corrélation. Accepter une assertion sans vérifier son contexte peut permettre une usurpation.

OpenID Connect (OIDC) ajoute une couche d’identité à OAuth 2.0. Il permet à un client de vérifier l’identité d’un utilisateur et de recevoir des informations standardisées via un ID Token et, le cas échéant, UserInfo. L’ID Token et l’Access Token n’ont pas le même but : le premier porte des assertions d’authentification destinées au client OIDC ; le second autorise l’accès à une ressource selon l’audience et les droits qui lui sont associés.

OAuth 2.0 est principalement un cadre de délégation d’autorisation, pas à lui seul un protocole qui prouve l’identité de l’utilisateur. Dire « nous utilisons OAuth pour la connexion » est imprécis tant que l’on ne sait pas si OIDC ou un autre mécanisme d’identité est impliqué. Les clients doivent suivre les recommandations de sécurité actuelles, notamment le RFC 9700, qui décrit les bonnes pratiques OAuth 2.0 et met en garde contre plusieurs flux ou modes d’utilisation trop faibles.

~~~text
OIDC : IDENTITÉ ET SESSION

Navigateur -> Client : demande de connexion
Client -> Fournisseur OIDC : requête d'authentification
Fournisseur -> Navigateur : interaction et authentification
Fournisseur -> Client : code d'autorisation
Client -> Fournisseur : échange sécurisé du code
Fournisseur -> Client : jetons
Client : valide l'ID Token, puis crée une session locale
~~~

Utilisez un flux adapté au type de client et aux recommandations du fournisseur. Pour une application web, le flux avec code d’autorisation et PKCE est généralement préférable aux approches historiques qui exposaient des jetons directement dans le navigateur. Les URI de redirection doivent être strictement enregistrées et comparées, le paramètre state doit protéger la corrélation de la requête et la nonce est utilisée selon les exigences OIDC. N’acceptez pas une URI arbitraire provenant d’un paramètre utilisateur.

Lors de la validation d’un ID Token, vérifiez au minimum la signature selon les clés attendues, l’émetteur, l’audience, l’expiration et les autres paramètres requis par le flux. Les données de jeton sont des assertions qui doivent être validées, pas simplement décodées. Un JWT décodé en Base64URL n’est pas automatiquement authentique. Ne placez pas dans un jeton des secrets qui seraient visibles par son détenteur.

Les jetons d’accès devraient avoir une durée limitée correspondant au risque. Les jetons de rafraîchissement nécessitent une protection et une politique de rotation adaptées. Prévoyez comment révoquer les sessions et gérer un compte désactivé ; la désactivation dans l’IdP ne garantit pas toujours l’invalidation immédiate de toutes les sessions locales ou copies de jetons déjà émises.

## 6. Authentification multifactorielle et résistance au phishing

L’authentification multifactorielle, ou MFA, combine des catégories différentes de facteurs. Les catégories classiques sont quelque chose que l’utilisateur sait, comme un secret mémorisé ; quelque chose qu’il possède, comme une clé matérielle ; et quelque chose qu’il est, comme une caractéristique biométrique traitée par un authentificateur. Deux mots de passe ne constituent pas deux facteurs indépendants simplement parce qu’ils sont différents.

Les codes à usage unique peuvent améliorer la sécurité par rapport au mot de passe seul, mais les codes qui peuvent être relayés dans un site de phishing restent vulnérables aux attaques en temps réel. Les notifications push peuvent être victimes de fatigue d’approbation. Les clés de sécurité WebAuthn et les passkeys reposant sur des mécanismes cryptographiques liés à l’origine peuvent apporter une meilleure résistance au phishing, selon l’implémentation, l’enrôlement et les dispositifs de récupération.

~~~text
Risque de connexion                 Contrôle à considérer
----------------------------------  -----------------------------------
Compte standard, risque faible      Authentification et surveillance
Données personnelles                MFA adaptée au risque
Administration cloud                Facteur résistant au phishing
Action très privilégiée             Réauthentification + élévation courte
Connexion anormale                  Vérification supplémentaire / refus
~~~

Une politique MFA doit traiter le cycle de vie entier. L’enrôlement initial est sensible : un attaquant qui prend le contrôle du compte pendant l’enrôlement peut associer son propre authentificateur. La récupération est tout aussi sensible. Le support ne doit pas pouvoir contourner les facteurs à partir d’une simple demande convaincante ; il faut des preuves, une procédure de vérification et une traçabilité.

Prévoyez plusieurs méthodes de récupération robustes sans offrir un chemin plus faible que le mécanisme normal. Les codes de secours doivent être affichés une fois, conservés de manière sûre et invalidés après usage. Une perte de clé doit déclencher une procédure qui vérifie l’identité et enregistre le remplacement. Les comptes privilégiés doivent bénéficier de protections renforcées ; le mécanisme le plus facile à contourner devient la véritable force de la politique.

MFA ne résout pas l’autorisation incorrecte. Un utilisateur authentifié avec un facteur fort peut tout de même accéder à une ressource qui ne lui appartient pas si l’API ne vérifie pas les droits. Les facteurs, les sessions et les règles d’accès doivent donc être conçus comme des couches distinctes.

## 7. Sessions, cookies, jetons et révocation

Après une authentification réussie, l’application crée souvent une session. Un cookie de session devrait être difficile à prédire, protégé par HTTPS et configuré avec les attributs appropriés. HttpOnly empêche les scripts ordinaires de lire le cookie ; Secure exige son envoi sur HTTPS ; SameSite aide à réduire certaines attaques intersites. Ces attributs réduisent des risques mais ne remplacent pas une bonne gestion du CSRF, du XSS et de l’autorisation.

Réémettez l’identifiant de session après une authentification ou une élévation significative afin d’éviter la fixation de session. Invalidez les sessions à la déconnexion, lors d’une désactivation ou d’un événement de sécurité, et appliquez une durée d’inactivité ainsi qu’une durée maximale. Une session longue peut être acceptable dans certaines applications à faible risque, mais pas par défaut pour les opérations d’administration.

~~~text
Connexion réussie
      |
      v
Créer une session protégée
      |
      v
Chaque requête : session valide ?
      |
      +---- non ----> Refus / nouvelle authentification
      |
      v
Autorisation sur la ressource
      |
      v
Événement sensible ?
      |
      +---- oui ----> réauthentification ou étape renforcée
      |
      v
Expiration / révocation / déconnexion
~~~

Les tokens bearer sont des jetons dont le détenteur peut les présenter ; la possession suffit selon le protocole et la politique. Ils doivent donc être traités comme des secrets. Ne les placez pas dans les URL où ils peuvent apparaître dans l’historique, les journaux ou les en-têtes de référent. Ne les écrivez pas dans les traces applicatives et réduisez leur durée de vie.

Un jeton JWT signé n’est pas nécessairement chiffré et son contenu peut être lisible. La validation doit vérifier l’algorithme autorisé, la clé attendue, l’émetteur, l’audience, l’expiration et les contraintes nécessaires au type de jeton. N’acceptez pas une signature ou un algorithme arbitraire choisi dans l’en-tête. Ne réutilisez pas un ID Token comme Access Token. Vérifiez le type de jeton et sa finalité.

La révocation est un problème d’architecture. Un jeton autonome valide jusqu’à son expiration peut rester utilisable jusqu’à cette date si le service ne consulte pas d’état de révocation. Vous pouvez réduire le risque grâce à des durées courtes, à la rotation des jetons de rafraîchissement, à une liste de révocation ou à un mécanisme d’introspection selon le protocole. La décision dépend des exigences de latence, d’échelle et de disponibilité.

## 8. Modèles d’autorisation : RBAC, ABAC et ReBAC

RBAC, le contrôle d’accès basé sur les rôles, relie les utilisateurs ou groupes à des rôles, puis les rôles à des permissions. Il est facile à expliquer lorsqu’une organisation possède des responsabilités stables : lecteur, éditeur, gestionnaire ou administrateur. Toutefois, les rôles peuvent proliférer lorsque chaque exception devient un nouveau rôle. Les rôles doivent refléter des responsabilités compréhensibles et être limités dans leur portée.

ABAC, le contrôle basé sur les attributs, prend en compte les attributs du sujet, de la ressource, de l’action et du contexte. Une règle peut autoriser un enseignant à modifier un cours si le cours appartient à son équipe et si le compte est actif. ABAC est souple, mais dépend de la qualité des attributs, de la cohérence des politiques et de la capacité à expliquer une décision.

ReBAC, le contrôle basé sur les relations, décide à partir des liens entre objets : propriétaire d’un document, membre d’une équipe, responsable d’un projet ou relation de partage. Il convient aux applications où les accès dépendent fortement des liens entre utilisateurs et ressources. Les grands systèmes combinent souvent ces modèles au lieu de choisir un seul paradigme.

~~~text
RBAC : utilisateur -> rôle -> permission
ABAC : sujet + ressource + action + contexte -> règle
ReBAC : sujet -- relation --> ressource

Exemple :
Alice -- enseigne --> Cours 17
Politique : un enseignant peut modifier le contenu du cours
uniquement si la relation est active et si le compte n'est pas suspendu.
~~~

Le contrôle d’accès doit refuser par défaut lorsqu’aucune règle explicite n’autorise une action. La permission doit être vérifiée à chaque requête, et pas uniquement à l’affichage d’un bouton. Un attaquant peut appeler directement une API ou modifier un identifiant. Masquer une ressource dans l’interface est utile pour l’expérience utilisateur, mais ce n’est pas un contrôle d’autorisation.

Il faut également distinguer autorisation au niveau d’une fonction et autorisation au niveau d’un objet. Une route peut être accessible à un utilisateur authentifié, mais il peut ne pas avoir le droit de consulter l’objet demandé. Vérifiez toutes les opérations de lecture, création, modification, suppression, export et administration. Une seule route oubliée peut exposer tout un ensemble de données.

## 9. Concevoir une politique de moindre privilège

Le moindre privilège attribue à une identité les droits minimum nécessaires, pour une portée et une période déterminées. Il s’applique aux personnes, services, comptes d’urgence, équipes d’administration, jetons et appareils. Le principe implique de supprimer les permissions inutiles et de réévaluer périodiquement celles qui restent.

Définissez les permissions en termes d’action, de ressource, de portée et de contexte. « Administrateur » est souvent trop vague. Un opérateur peut avoir besoin de redémarrer un service dans un namespace précis sans pouvoir lire les secrets du cluster ou modifier les rôles. Un développeur peut publier une image de test sans pouvoir pousser une image en production. La permission spécifique rend le risque plus facile à évaluer.

~~~text
IDENTITÉ
  |
  +--> action autorisée
  +--> ressource et portée
  +--> environnement
  +--> durée
  +--> conditions de contexte
  |
  v
Accès minimal vérifiable
~~~

Évitez les jokers larges dans les politiques d’accès. Une permission sur toutes les ressources actuelles peut également donner accès à des types de ressources ajoutés plus tard. Évitez les droits qui permettent à une identité de s’accorder elle-même des permissions, de modifier les contrôles d’accès ou d’impersonner une identité plus puissante, sauf besoin opérationnel défini et renforcé.

Le moindre privilège ne veut pas dire une politique tellement restrictive qu’elle pousse tout le monde à utiliser un compte partagé. Il faut fournir un chemin d’accès légitime et rapide, documenter les demandes et rendre la révocation fiable. Une politique sûre doit être opérable ; sinon, les contournements apparaissent dans des scripts, des mots de passe partagés et des privilèges persistants.

Le principe « deny by default » complète le moindre privilège. Une action non couverte par une règle explicite est refusée. Les nouvelles fonctionnalités, ressources et API doivent hériter d’un refus par défaut jusqu’à ce qu’une règle appropriée soit définie et testée.

## 10. Séparation des tâches et prévention des conflits de privilèges

La séparation des tâches vise à éviter qu’une personne ou identité puisse accomplir seule toutes les étapes d’une action à haut impact. Un développeur peut proposer un changement ; une revue valide le code ; un pipeline contrôlé construit l’artefact ; une politique l’autorise ; un compte de déploiement l’applique. Selon le risque, une même personne peut exercer plusieurs responsabilités, mais les contrôles doivent empêcher les changements invisibles ou non approuvés.

Les conflits de privilèges apparaissent par exemple lorsqu’une personne peut créer un compte, lui attribuer un rôle administrateur et supprimer ensuite les journaux d’audit. Ils peuvent aussi apparaître entre opérations financières, publication logicielle ou administration d’identités. Définissez les combinaisons incompatibles et déployez un mécanisme qui détecte ou bloque ces cumuls.

~~~text
Changement sensible
       |
       v
Demandeur différent du valideur ?
       |
       v
Contrôles automatiques réussis ?
       |
       v
Identité d'exécution limitée ?
       |
       v
Journal d'approbation et d'application
       |
       v
Revue ultérieure par un rôle indépendant
~~~

Une approbation humaine n’est utile que si elle repose sur le contexte : demande, ressources visées, droits demandés, durée, risque et contrôles automatiques. Une approbation répétitive et opaque n’est qu’un clic. Gardez une trace de la décision, de sa justification et de la version concernée, et évitez qu’un administrateur puisse supprimer ses propres traces.

Les comptes d’urgence, parfois appelés comptes break-glass, peuvent être nécessaires lorsque l’IdP ou le mécanisme normal est indisponible. Ils doivent être rares, protégés par des facteurs robustes, hors des parcours quotidiens, surveillés fortement et testés. Chaque utilisation déclenche une alerte, une enquête et une rotation des moyens d’accès. Une exception d’urgence qui n’est jamais testée ou dont le secret est connu de toute l’équipe constitue un risque.

## 11. PAM, élévation temporaire et administration juste-à-temps

La gestion des accès privilégiés, ou PAM, contrôle les identités et sessions qui permettent d’administrer des systèmes sensibles. Elle peut inclure un coffre de secrets, la rotation, l’enregistrement des sessions, les approbations, l’accès juste-à-temps (JIT) et l’accès juste suffisant (JEA). Ces mécanismes sont complémentaires : le coffre protège certains secrets, JIT limite la durée d’un privilège et JEA réduit ce que le privilège permet de faire.

Un modèle mature évite que les administrateurs utilisent leur identité privilégiée pour la messagerie, la navigation générale et toutes les tâches ordinaires. Il peut distinguer le compte quotidien du compte d’administration, imposer une authentification renforcée et limiter les postes autorisés à lancer des tâches sensibles. La gestion doit couvrir les comptes locaux, cloud, annuaires, équipements réseau et plans de contrôle.

~~~text
Demande d'élévation
       |
       v
Vérifier identité, justification et ressource
       |
       v
Approbation adaptée au risque
       |
       v
Accorder le rôle temporaire
       |
       v
Session surveillée / actions journalisées
       |
       v
Expiration automatique et revue
~~~

L’accès JIT donne un rôle uniquement pendant la fenêtre nécessaire, puis le retire automatiquement. Le JEA limite les opérations disponibles pendant cette fenêtre. Par exemple, un opérateur peut consulter l’état d’un service et relancer un déploiement connu sans pouvoir modifier la politique IAM ou créer de nouveaux administrateurs.

Les élévations doivent être liées à une demande précise. Exigez une justification, une échéance et les ressources concernées. Réduisez les durées par défaut et autorisez une prolongation uniquement selon une règle explicitement définie. Surveillez les extensions répétées qui peuvent signaler que le modèle de privilèges permanents reste mal conçu.

Un compte à haut privilège doit être surveillé pour les connexions inhabituelles, les ajouts de rôle, l’accès aux secrets, la création de comptes, la modification de règles de fédération et la suppression de logs. L’alerte doit pouvoir être corrélée à une demande JIT. Une action privilégiée sans demande associée nécessite une explication ou une enquête.

## 12. Identités de charge de travail et comptes non humains

Les comptes non humains incluent les services applicatifs, tâches planifiées, fonctions serverless, pipelines, opérateurs Kubernetes, robots de synchronisation et intégrations SaaS. Ils ont souvent besoin d’une autorisation sans intervention humaine. Un mot de passe ou une clé API durable oubliée dans une variable d’environnement peut devenir une identité orpheline très difficile à suivre.

Chaque identité technique doit avoir un propriétaire responsable, un objectif, une ressource autorisée, un mode d’émission des identifiants, une date ou un mécanisme de rotation, une politique de révocation et une surveillance. Les identités partagées entre plusieurs applications augmentent le rayon d’impact et rendent l’investigation difficile. Créez des identités distinctes lorsque les fonctions et risques sont différents.

~~~text
Service A ---- identité A ----> API A uniquement
Service B ---- identité B ----> Base B, accès en lecture
Pipeline ---- identité CI ----> Registre, publication limitée
Tâche de sauvegarde -- identité backup --> stockage sauvegardes
~~~

Privilégiez les identités de charge de travail gérées ou fédérées lorsque disponibles, plutôt que des clés statiques distribuées manuellement. Dans Kubernetes, associez chaque charge de travail à un compte de service approprié et ne montez pas automatiquement un jeton lorsque le workload n’en a pas besoin. Les permissions du compte de service doivent être minimales ; un compte dédié à une API ne doit pas hériter du rôle administrateur du cluster.

Le fait de pouvoir créer des Pods peut indirectement permettre d’utiliser le compte de service d’un autre workload si la configuration ne limite pas ce comportement. La possibilité de créer des rôles, des liaisons de rôles, des demandes de jetons ou des certificats client peut aussi créer des chemins d’escalade. La revue des permissions Kubernetes doit donc examiner les combinaisons de verbes et de ressources, pas seulement rechercher le mot admin.

Pour les identités techniques, une absence de connexion interactive n’est pas une raison d’ignorer le risque. Les services doivent avoir des journaux d’utilisation, des limites de fréquence, des restrictions réseau adaptées et un processus de rotation. Lorsque l’application est retirée, son identité et ses secrets doivent être supprimés avec elle.

## 13. IAM cloud et contrôle des permissions sur les ressources

Les plateformes cloud distinguent généralement les sujets, les rôles ou politiques, les ressources et les conditions. Une politique peut autoriser une action sur un ensemble de ressources à partir d’un contexte particulier. Une mauvaise portée, un joker ou une condition absente peut transformer un accès de lecture en accès transversal.

Évitez d’accorder des rôles d’administration complets aux applications par commodité. Une API qui lit un objet dans un stockage n’a généralement pas besoin de créer des utilisateurs, modifier des réseaux et administrer le compte cloud. Décomposez les capacités, limitez les ressources et vérifiez les chemins d’escalade. Les politiques doivent être revues en contexte avec les politiques de ressources, les rôles assumés et les contrôles d’organisation.

~~~text
Identité de charge de travail
        |
        v
Politique attachée au rôle
        |
        +--> Action demandée
        +--> Ressource cible
        +--> Conditions et contexte
        |
        v
Décision : autorisé / refusé
        |
        v
Journal d'accès et surveillance
~~~

Une politique de refus explicite, lorsqu’elle est prise en charge par le moteur de politique, peut l’emporter sur une autorisation plus large. Cependant, il faut comprendre la sémantique précise du fournisseur : héritage, priorités, frontières de permission, politiques de ressources et conditions ne sont pas identiques dans tous les environnements. Testez avec les outils d’analyse du fournisseur et avec des scénarios réels contrôlés.

Le contrôle d’accès cloud doit prendre en compte les conditions. Une identité de pipeline peut publier uniquement dans un registre précis depuis une branche approuvée. Un opérateur peut administrer une ressource uniquement depuis un appareil géré et pendant une fenêtre autorisée. Les conditions doivent reposer sur des attributs fiables et testés ; une valeur que l’utilisateur peut falsifier n’est pas une base sûre.

Les droits de gestion de l’IAM sont eux-mêmes très sensibles. Les capacités de modifier une politique, d’assumer un rôle plus puissant, d’émettre des clés ou de désactiver l’audit doivent être réservées et fortement surveillées. Une analyse des permissions doit chercher les chemins indirects, pas simplement constater qu’un rôle n’a pas le nom « Administrator ».

## 14. RBAC Kubernetes : rôles, comptes de service et escalade

Kubernetes offre le contrôle d’accès fondé sur les rôles (RBAC). Un Role définit des permissions dans un namespace ; un ClusterRole peut concerner des ressources à portée cluster ou être utilisé dans un namespace selon le binding. Un RoleBinding associe un sujet à un rôle dans un namespace, alors qu’un ClusterRoleBinding accorde le rôle à portée cluster. Préférez les liaisons de portée la plus limitée qui répondent au besoin.

Évitez les jokers sur les verbes et les ressources, ainsi que l’attribution du rôle cluster-admin à des utilisateurs ou services ordinaires. Les droits sur les sous-ressources sensibles, l’impersonation, les demandes de jetons, les demandes de signature de certificats, les webhooks d’admission et les namespaces peuvent créer des chemins d’escalade. Les noms des verbes ne suffisent pas ; il faut connaître les conséquences indirectes de l’action.

~~~yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: lecture-pods
  namespace: formation
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
~~~

~~~yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: equipe-observation
  namespace: formation
subjects:
  - kind: Group
    name: observabilite
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: lecture-pods
  apiGroup: rbac.authorization.k8s.io
~~~

Cet exemple est une base de lecture limitée dans le namespace formation ; il n’accorde pas l’accès aux logs des Pods, aux Secrets ou à l’ensemble du cluster. Ajoutez une ressource ou un verbe seulement si le besoin est établi. Testez les permissions effectives avec les outils Kubernetes appropriés et revoyez périodiquement les bindings.

Un compte de service ne doit pas recevoir de permissions puissantes par défaut. Lorsque le Pod n’a pas besoin de l’API Kubernetes, désactivez le montage automatique du jeton au niveau de la configuration appropriée. Ne partagez pas le même compte de service entre applications de confiance différente. Limitez les workloads puissants, examinez leurs placements et imposez les politiques de sécurité des Pods adaptées.

La frontière d’un namespace n’est pas une barrière absolue contre toutes les escalades. Les droits de créer des workloads peuvent donner indirectement accès aux capacités du compte de service choisi. Les droits de créer des PersistentVolumes ou des montages hostPath sont particulièrement sensibles. Les règles de sécurité doivent être adaptées aux possibilités réelles de l’API et aux extensions installées.

## 15. Cycle de vie : arrivée, mobilité, départ

Le cycle de vie des identités est souvent décrit comme Joiner, Mover, Leaver : arrivée, changement de fonction et départ. Lors de l’arrivée, la création du compte et les permissions doivent suivre la source de vérité et le rôle attendu. Lors d’une mobilité, il faut retirer les droits devenus inutiles en plus d’ajouter les nouveaux. Lors du départ, les accès doivent être désactivés selon la politique et le risque, et les actifs transférés à un propriétaire.

~~~text
ARRIVÉE
Source RH -> identité -> compte -> accès de base -> approbations

MOBILITÉ
Changement de fonction -> recalcul des droits -> retrait des droits anciens
                                      -> attribution des droits nouveaux

DÉPART
Désactivation -> révocation des sessions et jetons -> transfert des actifs
              -> suppression contrôlée -> vérification des accès résiduels
~~~

Le changement de fonction est un point d’attention fréquent. Une personne peut accumuler de nouveaux groupes sans perdre ceux liés à son ancien poste. Ce privilege creep fait que les droits effectifs dérivent du besoin initial. Un processus de mobilité doit recalculer les droits attendus et retirer les permissions obsolètes, y compris celles accordées directement et non via des groupes.

La désactivation de l’utilisateur n’est pas toujours suffisante. Il peut rester des sessions locales, jetons de rafraîchissement, clés API, clés SSH, certificats, sessions VPN, clés d’accès cloud ou comptes locaux. Définissez la liste des systèmes à révoquer et testez son exécution. La procédure de départ doit traiter aussi les comptes propriétaires de ressources et les intégrations créées par la personne.

Pour les départs urgents, la suspension d’accès peut précéder la suppression définitive. Préservez les journaux nécessaires et assurez le transfert des données professionnelles selon la politique. Ne réattribuez pas immédiatement un identifiant si les autres systèmes peuvent l’utiliser pour rattacher par erreur d’anciens droits au nouvel utilisateur.

## 16. Gouvernance des accès et recertification

La gouvernance décide qui peut demander, approuver, accorder, revoir et révoquer un accès. Une demande doit préciser la ressource, le droit sollicité, le motif métier, la durée et le propriétaire. L’approbateur doit connaître l’impact des permissions et ne devrait pas valider un accès dont il est lui-même le demandeur lorsque le risque exige une séparation.

La recertification est une revue périodique des accès effectifs. Elle doit comparer les droits réels aux responsabilités actuelles et produire des décisions : confirmer, réduire, révoquer ou demander des informations. La revue est inefficace si elle consiste à approuver un écran de centaines de lignes sans contexte. Regroupez l’information par ressource, rôle, dernière utilisation, propriétaire et niveau de risque.

~~~text
Demande d'accès
      |
      v
Validation métier : pourquoi ce droit ?
      |
      v
Analyse IAM : quelle portée et quelle durée ?
      |
      v
Approbation séparée si risque élevé
      |
      v
Attribution automatisée
      |
      v
Expiration ou recertification
      |
      v
Révocation et preuve d'exécution
~~~

La dernière utilisation est un signal utile, mais l’absence d’usage récent ne signifie pas automatiquement que le droit est inutile. Une permission de reprise après sinistre peut être rarement utilisée et pourtant essentielle. La décision doit intégrer le besoin, la conséquence d’une révocation et le propriétaire de l’accès.

Les accès temporaires sont préférables pour les besoins ponctuels. Une date d’expiration ne doit pas être un simple champ documentaire : le mécanisme doit effectivement retirer le droit. Lorsqu’une politique ne peut pas retirer automatiquement un accès, attribuez un propriétaire et des alertes avant échéance, puis vérifiez la révocation.

Les rôles d’entreprise doivent être compréhensibles par les métiers et testables techniquement. Évitez les groupes avec des droits très hétérogènes, les exceptions sans propriétaire et les rôles qui persistent après plusieurs réorganisations. Un catalogue de rôles entretenu est une source de vérité utile, à condition qu’il soit relié aux permissions effectives.

## 17. Accès partenaires, applications et consentement

Les intégrations tierces et applications SaaS étendent l’IAM au-delà des comptes internes. Une application autorisée à lire les fichiers d’un utilisateur ou à envoyer des messages au nom d’une organisation peut devenir un chemin d’exfiltration ou de persistance si son éditeur ou ses identifiants sont compromis.

Avant d’approuver une intégration, vérifiez l’éditeur, l’objectif, les permissions demandées, la durée d’accès, les modalités de révocation et la façon dont les jetons sont conservés. Demandez seulement les scopes nécessaires, et distinguez les permissions d’un utilisateur de celles accordées à une application au niveau de l’organisation. Une permission large acceptée une fois peut rester en place après que l’utilisateur a cessé d’utiliser l’application.

~~~text
Application tierce
      |
      v
Demande de scopes
      |
      v
Évaluation des permissions et du fournisseur
      |
      v
Consentement ou approbation administrative
      |
      v
Jeton limité et durée maîtrisée
      |
      v
Surveillance + revue + révocation
~~~

OAuth permet une délégation avec des scopes, mais ceux-ci ne suffisent pas toujours à exprimer l’autorisation réelle sur chaque objet. L’API doit vérifier les permissions associées à la ressource. Les jetons devraient être limités en audience et en durée, conservés de manière sûre et révoqués lorsqu’ils ne sont plus nécessaires.

Les comptes partenaires doivent avoir un responsable interne, une date de fin ou de revue et une portée limitée. Le partage de comptes entre personnes différentes empêche l’attribution des actions et complique la révocation. Pour un prestataire, utilisez une identité nominative et une méthode d’accès contrôlée. Évitez de créer un compte générique « consultant » utilisé par toute une équipe externe.

## 18. Contrôles d'autorisation dans les API et applications

L’autorisation doit être appliquée côté serveur à chaque requête sensible. Ne faites pas confiance à un rôle envoyé par le navigateur, à un champ caché ou à une valeur stockée uniquement dans le client. Un utilisateur peut modifier la requête. Le serveur doit charger les attributs fiables, identifier le sujet et vérifier la permission sur l’action et l’objet concernés.

Un défaut classique est l’accès direct à un objet par son identifiant, parfois appelé contrôle d’accès au niveau objet défaillant. Le fait qu’un utilisateur puisse appeler une route ne signifie pas qu’il peut agir sur tout objet que la route accepte. Après avoir identifié l’objet, vérifiez son propriétaire, son tenant, la relation métier et l’action demandée. Le même contrôle s’applique aux exports, aux téléchargements et aux fonctions administratives.

~~~text
Requête API
    |
    v
Authentifier l'identité
    |
    v
Valider le type et les contraintes de la requête
    |
    v
Charger la ressource côté serveur
    |
    v
Vérifier le droit sur CETTE ressource
    |
    +---- refus ----> Réponse contrôlée + journal
    |
    v
Exécuter l'action et journaliser
~~~

Évitez de construire l’autorisation uniquement dans le frontend. Masquer le bouton « supprimer » améliore l’interface, mais la route DELETE doit effectuer sa propre vérification. Utilisez des tests négatifs : utilisateur A qui tente de lire l’objet de B, utilisateur standard qui appelle une route administrative, compte suspendu avec un ancien jeton et service qui tente une action non prévue.

L’autorisation ne doit pas non plus révéler excessivement l’existence d’un objet. Selon le risque, une réponse uniforme pour une ressource absente et une ressource non autorisée peut réduire certaines possibilités d’énumération. Choisissez le comportement en tenant compte de l’expérience utilisateur, de l’audit et de la sensibilité des données.

Les règles complexes doivent produire une raison de décision exploitable dans les logs sans divulguer de secrets. Par exemple, un résultat peut indiquer « refusé : relation propriétaire absente » ou « refusé : rôle expiré ». Cela aide au diagnostic et à la détection des abus.

## 19. Surveillance, audit et détection du privilege creep

Les événements IAM utiles incluent la création et la suppression de compte, les changements de groupe, l’attribution de rôle, la création de clé, l’activation d’un facteur, la récupération de compte, l’élévation de privilège, la modification de politique et l’échec répété d’authentification. Les journaux doivent être suffisamment complets pour reconstituer les actions, mais ne doivent pas enregistrer les secrets ou jetons en clair.

Surveillez les anomalies : connexion impossible depuis un nouvel emplacement suivie d’une élévation, ajout d’un utilisateur à un groupe administrateur, création d’un compte technique sans propriétaire, modification d’une politique d’audit, émission inhabituelle de jetons ou révocation désactivée. Le contexte compte : une opération prévue dans une demande de changement ne ressemble pas à la même opération lancée hors procédure.

~~~text
Événements IAM
   |
   v
Normalisation : identité, action, ressource, résultat
   |
   v
Corrélation : rôle, contexte, demande, historique
   |
   +--> activité attendue : conserver la preuve
   |
   +--> anomalie : alerte et triage
                       |
                       v
              Contenir / révoquer / enquêter
~~~

Protégez les journaux contre la modification et la suppression par les personnes mêmes dont les actions sont auditées. Une administration d’identité ne doit pas permettre de supprimer sans trace l’historique d’élévation. Synchronisez les horloges et conservez les identifiants de corrélation pour relier IdP, API, cloud et cluster.

Le privilege creep est une dérive cumulative. Mesurez les permissions directes, les groupes imbriqués, les rôles cloud, les comptes techniques et les exceptions. Une revue doit examiner les droits réellement effectifs : un utilisateur peut hériter de plusieurs rôles dont la combinaison est plus puissante que chacun pris séparément.

Une alerte n’est efficace que si quelqu’un peut y répondre. Attribuez un propriétaire, définissez les critères d’escalade et testez la révocation. Après une alerte de compte compromis, il faut invalider les sessions et les jetons concernés, examiner les changements d’accès et confirmer qu’aucune nouvelle identité persistante n’a été créée.

## 20. Répondre à une compromission d'identité

La réponse commence par contenir l’accès. Selon le risque, suspendez le compte, révoquez les sessions et jetons, réinitialisez les authentificateurs, retirez les rôles et bloquez les clés techniques. Pour une identité de service, révoquer sans identifier les dépendances peut interrompre un service : le plan doit privilégier le confinement tout en organisant un remplacement sûr et rapide.

~~~text
Signal de compte compromis
       |
       v
Évaluer la portée et les actions récentes
       |
       v
Suspendre / révoquer sessions et jetons
       |
       v
Retirer les privilèges et rotations nécessaires
       |
       v
Rechercher persistance, comptes et clés créés
       |
       v
Restaurer un accès légitime et surveiller
       |
       v
Analyse des causes + correction des contrôles
~~~

Préservez les preuves : connexions, demandes de jetons, modifications de groupes, API appelées, ressources consultées et événements de récupération. N’exposez pas les jetons dans le rapport. Déterminez si l’attaquant a modifié les moyens de récupération, créé une clé, accordé un rôle à un autre compte ou supprimé des traces. Un simple changement de mot de passe ne suffit pas toujours si des sessions et jetons restent actifs.

Rétablissez l’accès pour le propriétaire légitime par un processus de récupération vérifié. Exigez de nouveaux facteurs si nécessaire et examinez les appareils ou applications associés. En présence d’un jeton de service compromis, identifiez tous les consommateurs, remplacez le secret ou passez à une identité fédérée, puis confirmez que l’ancienne valeur n’est plus acceptée.

L’analyse post-incident transforme les enseignements en actions : réduire les durées, exiger un facteur plus robuste, corriger la récupération, limiter les droits d’attribution de rôle, ajouter un test d’autorisation ou améliorer une alerte. L’objectif est de diminuer la probabilité de répétition et de raccourcir le temps de détection et de confinement.

## 21. Architecture de référence pour Atlas Formation

Pour la plateforme Atlas Formation, utilisez un fournisseur d’identité central pour l’authentification humaine et une fédération OIDC pour les applications qui le prennent en charge. Conservez une source de vérité pour les états des personnes et leurs fonctions. Transformez les changements en opérations de cycle de vie automatisées, mais gardez une approbation pour les accès à haut impact. Les applications maintiennent des règles d’autorisation au niveau des ressources et ne se contentent pas de savoir que le fournisseur a authentifié l’utilisateur.

Les comptes administratifs sont séparés des comptes quotidiens. Les accès privilégiés sont temporaires, liés à une demande et surveillés. Les workloads possèdent des identités distinctes avec droits de service limités. Le pipeline utilise une identité fédérée pour publier dans un registre défini, et le cluster utilise des comptes de service minimaux.

~~~text
                 +----------------------+
                 | Source RH / groupes  |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Gouvernance IAM      |
                 | JML, demandes, revue |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | IdP / MFA / OIDC     |
                 +----+------------+----+
                      |            |
                      v            v
               +----------+   +----------+
               | Portail  |   | Console  |
               | et API   |   | admin    |
               +----+-----+   +-----+----+
                    |               |
                    v               v
             Autorisation       PAM / JIT
             par ressource          |
                                    v
                            Accès privilégié
~~~

Les identités non humaines suivent un parcours distinct. Un compte de service du frontend ne doit pas accéder à la base de données. Une API qui lit des contenus n’a pas besoin de modifier la politique IAM. Le pipeline de publication ne peut pas administrer l’ensemble du cloud. Des journaux centralisés relient les événements d’authentification, les décisions d’autorisation, les changements de rôles et les actions privilégiées.

Définissez des critères d’acceptation : un compte suspendu ne peut pas ouvrir une nouvelle session ; les sessions existantes sont révoquées selon le délai fixé ; une demande JIT expire ; une API refuse l’accès à un objet appartenant à un autre utilisateur ; un service ne peut pas assumer un rôle non autorisé ; un compte de service inutilisé est identifié ; les opérations administratives génèrent des traces protégées.

## 22. Stratégie de tests IAM

Les tests IAM doivent couvrir les cas positifs et négatifs. Le test positif confirme qu’un sujet légitime peut effectuer l’action nécessaire. Le test négatif démontre qu’un sujet non autorisé est refusé. Les deux sont indispensables : une suite qui ne vérifie que les refus peut bloquer le fonctionnement, tandis qu’une suite qui teste uniquement les usages légitimes peut manquer les escalades.

Établissez une matrice sujet-action-ressource-contexte. Incluez les utilisateurs standards, propriétaires, managers, administrateurs, comptes suspendus, comptes de service et identités fédérées. Ajoutez des états limites : jeton expiré, rôle retiré, attribut manquant, demande JIT expirée, ressources appartenant à un autre tenant et identifiant d’objet modifié par un client.

~~~text
MATRICE DE TEST
Sujet          Action       Ressource           Résultat attendu
-------------  -----------  ------------------  ----------------
Élève A        Lire         Son cours           Autorisé
Élève A        Lire         Cours privé de B    Refusé
Enseignant A   Modifier     Cours de A          Autorisé
Enseignant A   Modifier     Cours de B          Refusé
Service lecture Lire        Objet autorisé      Autorisé
Service lecture Supprimer   Objet quelconque    Refusé
Compte suspendu Ouvrir      Session             Refusé
Admin JIT expiré Modifier   Politique IAM       Refusé
~~~

Automatisez les tests de régression au niveau de l’API et des politiques. Lorsque vous ajoutez une nouvelle ressource ou action, exigez que la décision d’autorisation correspondante soit explicitement définie. Testez les contrôles sur chaque endpoint et sous-route. Les tests exploratoires et revues manuelles complètent l’automatisation, surtout lorsque les droits sont dérivés de relations métier.

Mesurez les résultats : pourcentage des accès privilégiés recertifiés, comptes techniques avec propriétaire, délai de révocation après départ, nombre de rôles trop larges, nombre d’exceptions expirées et délai de réponse aux alertes d’identité. Les indicateurs doivent suivre les risques réels, pas seulement le nombre de comptes ou de connexions réussies.

## 23. Quatre travaux pratiques guidés

### TP 1 — Concevoir un modèle RBAC minimal pour une application pédagogique

**Situation :** une plateforme contient des cours, des quiz et des résultats. Les élèves lisent leurs cours et consultent leurs résultats. Les enseignants modifient le contenu de leurs propres cours. Les administrateurs gèrent les comptes et la configuration. Aujourd’hui, tous les utilisateurs possèdent le même rôle global et le frontend masque seulement certaines commandes.

**Étape 1 : identifier les ressources et actions.** Listez cours, quiz, résultat individuel, compte et configuration. Pour chaque ressource, séparez lire, créer, modifier, publier, supprimer et administrer.

**Étape 2 : définir les rôles métier.** Élève, enseignant, gestionnaire de contenu et administrateur ont des responsabilités différentes. Évitez d’utiliser administrateur comme rôle de secours pour les tâches courantes.

**Étape 3 : préciser la portée.** Un enseignant peut modifier un cours dont il est propriétaire ou membre de l’équipe responsable, pas tous les cours. Un élève peut consulter ses propres résultats, pas ceux d’un autre élève.

**Étape 4 : implémenter le refus par défaut.** Si aucune règle ne permet l’action, le serveur la refuse. Les checks sont exécutés sur chaque route, même lorsque le frontend ne présente pas le bouton.

**Étape 5 : écrire les tests négatifs.** L’élève A demande le résultat de B ; l’enseignant modifie un cours qui ne lui appartient pas ; un compte suspendu appelle une API avec une session existante. Tous les scénarios doivent être rejetés selon la politique.

**Étape 6 : vérifier la journalisation.** Le journal indique le sujet, l’action, la ressource et le résultat sans enregistrer de jeton ou de données secrètes.

**Correction attendue :** RBAC exprime les rôles, tandis qu’un contrôle au niveau de la ressource vérifie propriétaire ou relation. Le frontend améliore la navigation, mais la décision de sécurité reste côté serveur. Les cas positifs et négatifs sont automatisés.

### TP 2 — Durcir OIDC et les sessions d’une application web

**Situation :** une application utilise un fournisseur OIDC mais accepte toute URI de redirection passée dans un paramètre. Les sessions durent plusieurs semaines, et le logout local ne révoque pas les sessions actives sur le serveur.

**Étape 1 : vérifier les paramètres du client.** Enregistrez explicitement les URI de redirection permises. Refusez toute URI qui ne correspond pas aux valeurs attendues et n’acceptez pas de redirection ouverte.

**Étape 2 : utiliser un flux adapté.** Pour un client web approprié, choisissez le flux d’autorisation avec code et PKCE selon la plateforme. Utilisez state pour la corrélation et nonce lorsque requise, et vérifiez leurs valeurs au retour.

**Étape 3 : valider les jetons.** Vérifiez signature, émetteur, audience, expiration, type et autres contraintes pertinentes. Ne faites pas que décoder le contenu du JWT. Ne confondez pas ID Token et Access Token.

**Étape 4 : durcir la session.** Utilisez un identifiant imprévisible, les attributs de cookie adaptés, la rotation de session après authentification et une expiration d’inactivité. Définissez ce qui se passe après la suspension du compte.

**Étape 5 : traiter le logout et la révocation.** Invalidez la session locale et prévoyez l’invalidation des sessions et refresh tokens selon le mécanisme disponible. Documentez les limites de révocation des access tokens autonomes.

**Étape 6 : tester les erreurs.** Mauvaise audience, jeton expiré, state incorrect, URI non enregistrée, signature invalide et compte suspendu doivent entraîner un refus.

**Correction attendue :** l’application ne fait confiance qu’à l’IdP configuré, valide les assertions et gère les sessions selon le risque. Les jetons ne sont pas exposés dans les URLs ou logs et les procédures de révocation sont définies.

### TP 3 — Limiter les permissions Kubernetes d’un service

**Situation :** une API doit lire les Pods de son namespace, mais elle utilise le compte de service par défaut lié à un ClusterRole trop large. Le montage du jeton API est activé même dans les workloads qui n’appellent pas l’API Kubernetes.

**Étape 1 : établir les besoins.** Identifiez les ressources et verbes réellement nécessaires. L’API doit-elle lire les Pods, les modifier, accéder aux Secrets ou créer d’autres workloads ? Ne déduisez pas les besoins uniquement de la configuration existante.

**Étape 2 : créer un compte de service dédié.** Ne réutilisez pas un compte puissant. Liez une politique minimale au namespace nécessaire, en privilégiant Role et RoleBinding lorsque possible.

**Étape 3 : supprimer les permissions superflues.** Évitez les jokers. Examinez les droits d’impersonation, de création de jetons, de modification de bindings, d’accès aux webhooks et aux sous-ressources sensibles.

**Étape 4 : désactiver le montage inutile.** Pour les workloads qui ne consomment pas l’API Kubernetes, configurez la désactivation du montage automatique du jeton selon la documentation de la version utilisée.

**Étape 5 : tester les actions.** Lecture des Pods du namespace : autorisée. Lecture des Secrets : refusée si non nécessaire. Création de RoleBinding ou d’un Pod utilisant un compte privilégié : refusée.

**Étape 6 : vérifier la portée réelle.** Examinez les RoleBindings et ClusterRoleBindings effectifs, la politique de sécurité des Pods et le placement du workload. Documentez les droits qui restent requis.

**Correction attendue :** la charge possède une identité dédiée, les permissions sont limitées au namespace et aux actions nécessaires et les chemins d’escalade sont testés. Le simple fait qu’un compte de service existe ne justifie pas son accès au cluster entier.

### TP 4 — Répondre à un compte privilégié compromis

**Situation :** une alerte indique qu’un compte administrateur s’est connecté depuis un contexte inhabituel, a attribué un rôle à un deuxième compte et créé une clé API. Les journaux sont disponibles, mais plusieurs applications possèdent des sessions longues.

**Étape 1 : contenir.** Suspendez le compte compromis selon la procédure, révoquez les sessions et jetons et empêchez les nouvelles élévations. Coordonnez le confinement pour ne pas laisser les clés créées actives.

**Étape 2 : préserver et enquêter.** Collectez les événements d’authentification, changements de rôle, création de clés, appels API et accès aux ressources. Ne copiez pas les jetons dans le dossier d’incident.

**Étape 3 : rechercher la persistance.** Inspectez les comptes nouvellement créés, rôles ajoutés, méthodes de récupération modifiées, nouvelles applications autorisées, clés, certificats, règles de fédération et paramètres d’audit.

**Étape 4 : révoquer les capacités.** Retirez le rôle ajouté, désactivez la clé et invalidez les sessions restantes. Si des applications possèdent des copies de jetons, appliquez le mécanisme de révocation ou d’expiration et surveillez les tentatives de réutilisation.

**Étape 5 : restaurer.** Vérifiez l’identité du propriétaire légitime avec la procédure de récupération prévue, réenrôlez des facteurs robustes si nécessaire et fournissez un accès de remplacement contrôlé.

**Étape 6 : corriger la cause.** Renforcez les règles d’élévation, les conditions de connexion, les alertes de changement de rôle et les durées de session. Testez qu’une nouvelle tentative de même scénario génère un refus ou une alerte.

**Correction attendue :** la réponse contient l’accès, invalide les capacités persistantes, identifie l’étendue de l’incident et restaure une identité légitime. Le changement de mot de passe seul n’est pas suffisant si les jetons, clés ou sessions restent valides.

## 24. Vingt exercices corrigés

### Exercice 1 — Distinguer authentification et autorisation
**Question :** une personne a réussi la MFA. Peut-elle automatiquement lire tous les documents de l’entreprise ?

**Correction :** non. La MFA renforce l’authentification, mais chaque action sur une ressource nécessite une décision d’autorisation. L’accès dépend de la ressource, du rôle, des relations et du contexte.

### Exercice 2 — Source de vérité
**Question :** pourquoi l’application ne devrait-elle pas considérer un attribut modifiable par l’utilisateur comme preuve de son rôle ?

**Correction :** l’utilisateur pourrait s’attribuer des permissions. Les attributs de décision doivent venir d’un système de confiance, être validés et avoir un propriétaire.

### Exercice 3 — OAuth ou OIDC
**Question :** OAuth 2.0 garantit-il seul l’identité de l’utilisateur ?

**Correction :** OAuth 2.0 est un cadre de délégation d’autorisation. OIDC ajoute une couche d’identité fondée sur OAuth et définit notamment l’ID Token.

### Exercice 4 — ID Token et Access Token
**Question :** pourquoi ne pas utiliser un ID Token comme Access Token ?

**Correction :** ils ont des finalités et audiences différentes. L’ID Token informe le client sur l’authentification ; l’Access Token autorise l’accès à une ressource selon sa politique.

### Exercice 5 — Valider un JWT
**Question :** une application peut-elle faire confiance au contenu d’un JWT simplement décodé ?

**Correction :** non. Elle doit vérifier la signature, l’émetteur, l’audience, l’expiration, le type et les contraintes du flux. Décoder ne prouve pas l’authenticité.

### Exercice 6 — MFA résistante au phishing
**Question :** pourquoi une clé de sécurité liée à l’origine peut-elle être plus résistante au phishing qu’un code saisi manuellement ?

**Correction :** le mécanisme cryptographique est lié au contexte du site authentique, ce qui limite le relais par une page frauduleuse. La sécurité dépend aussi de l’enrôlement et de la récupération.

### Exercice 7 — Récupération de compte
**Question :** quelle faiblesse apparaît si le support peut désactiver la MFA après une simple demande par courriel ?

**Correction :** le processus de récupération devient le chemin d’attaque le plus faible. Il faut vérifier l’identité avec une procédure robuste, tracer l’action et appliquer des contrôles adaptés au risque.

### Exercice 8 — Cookie de session
**Question :** HttpOnly suffit-il à sécuriser une session ?

**Correction :** non. Il empêche la lecture ordinaire par JavaScript, mais d’autres risques comme CSRF, vol de session ou autorisation incorrecte subsistent. Il faut aussi Secure, SameSite approprié, rotation et expiration.

### Exercice 9 — RBAC
**Question :** quel est le risque de créer un rôle unique par exception ?

**Correction :** la prolifération rend les droits difficiles à comprendre, à tester et à révoquer. Utilisez des rôles qui correspondent à des responsabilités et ajoutez des attributs ou relations pour les exceptions nécessaires.

### Exercice 10 — ABAC
**Question :** quelle condition doit être vraie pour qu’un modèle ABAC soit fiable ?

**Correction :** les attributs utilisés doivent être fiables, validés et maintenus. Un attribut que l’utilisateur peut falsifier ne doit pas déclencher une autorisation sensible.

### Exercice 11 — Refus par défaut
**Question :** que doit faire une API lorsqu’aucune règle n’autorise clairement l’action ?

**Correction :** refuser par défaut. Un droit doit être explicitement justifié, et les nouvelles routes doivent être accompagnées de tests d’autorisation.

### Exercice 12 — Moindre privilège
**Question :** une application qui ne lit que des objets a-t-elle besoin d’un rôle d’administration cloud ?

**Correction :** non, sauf justification exceptionnelle. Donnez-lui seulement les actions de lecture requises sur les ressources concernées et surveillez les accès effectifs.

### Exercice 13 — Accès JIT
**Question :** quelle est la valeur d’un accès privilégié temporaire ?

**Correction :** il réduit la durée pendant laquelle un compte est puissant et limite l’usage permanent d’un rôle élevé. Il doit expirer automatiquement et être lié à une demande.

### Exercice 14 — Compte de service
**Question :** pourquoi éviter que plusieurs applications partagent un compte de service puissant ?

**Correction :** cela étend le rayon d’impact d’une compromission et empêche d’attribuer clairement les actions. Des identités distinctes simplifient aussi la révocation.

### Exercice 15 — Kubernetes RBAC
**Question :** pourquoi un droit de créer des Pods peut-il être plus puissant qu’il n’y paraît ?

**Correction :** le créateur peut parfois sélectionner un compte de service déjà autorisé, monter certains volumes ou déclencher des chemins d’escalade. Il faut revoir les permissions et les politiques de sécurité des Pods ensemble.

### Exercice 16 — Mobilité d’un salarié
**Question :** que doit faire le processus lorsqu’une personne change d’équipe ?

**Correction :** recalculer les droits à partir de la nouvelle fonction, attribuer les permissions nécessaires et retirer celles de l’ancienne fonction qui ne sont plus justifiées.

### Exercice 17 — Départ
**Question :** désactiver le compte central révoque-t-il forcément toutes les sessions et clés d’applications ?

**Correction :** pas toujours. Il faut une procédure qui invalide les sessions, jetons, clés, certificats et accès locaux selon les capacités de chaque système, puis vérifier la révocation.

### Exercice 18 — Recertification
**Question :** pourquoi ne pas approuver en un clic tous les accès d’une équipe ?

**Correction :** cela ne fournit pas une évaluation réelle des besoins. La revue doit présenter la portée, le propriétaire, l’usage et le risque pour permettre confirmer, réduire ou révoquer les droits.

### Exercice 19 — Compromission privilégiée
**Question :** pourquoi changer seulement le mot de passe après une compromission administrative ne suffit-il pas ?

**Correction :** des jetons, sessions, clés API ou comptes de persistance peuvent rester actifs. Il faut révoquer toutes les capacités concernées, enquêter sur les modifications et restaurer l’accès de manière contrôlée.

### Exercice 20 — Mesurer l’IAM
**Question :** pourquoi le nombre de comptes est-il un mauvais indicateur isolé de maturité IAM ?

**Correction :** il ne montre ni les droits excessifs, ni les comptes orphelins, ni la qualité de la révocation ou du suivi. Mesurez plutôt les accès revus, le délai de retrait, la couverture des propriétaires et les chemins d’escalade éliminés.

## 25. Défi final : refondre le modèle IAM d’Atlas Formation

**Scénario :** Atlas Formation possède des élèves, enseignants, opérateurs, administrateurs, développeurs et plusieurs comptes de service. La plateforme utilise OIDC, une API métier, une base de données, un registre d’images, un compte cloud et Kubernetes. Les droits se sont accumulés au fil du temps et les sessions sont parfois longues. Un administrateur a aussi créé une clé API manuelle pour un processus automatique.

Votre mission consiste à proposer un modèle cible qui répond aux dimensions suivantes.

**A. Identité humaine.** Définissez la source de vérité, le cycle arrivée-mobilité-départ, les facteurs requis et la récupération de compte. Les comptes à privilèges élevés doivent avoir des contrôles plus forts.

**B. Fédération et sessions.** Précisez le rôle de l’IdP, le flux OIDC attendu, la validation des tokens, la gestion des cookies, les durées et la révocation.

**C. Autorisation métier.** Définissez les rôles, ressources et relations. Assurez-vous qu’un élève ne peut pas lire les résultats d’un autre élève et qu’un enseignant ne modifie que les contenus de son périmètre.

**D. Privilèges.** Concevez un processus JIT/JEA, des règles de séparation des tâches et des comptes break-glass. Les actions privilégiées doivent être traçables.

**E. Identités techniques.** Remplacez la clé API statique par une identité gérée ou fédérée lorsque possible. Chaque service doit avoir un propriétaire et une portée minimale. Réduisez les droits Kubernetes et cloud.

**F. Gouvernance.** Organisez la demande, l’approbation, la recertification, les exceptions et l’expiration. Définissez des métriques qui démontrent l’amélioration.

**G. Incident.** Préparez une procédure pour révoquer les sessions, clés et rôles d’un compte compromis et rechercher une éventuelle persistance.

### Correction détaillée du défi

La source de vérité est l’enregistrement RH ou le registre de collaborateurs approuvé ; elle fournit des attributs stables et un statut. Le moteur IAM transforme les événements en opérations de compte, tandis que les rôles et attributs alimentent les politiques. Les arrivées reçoivent les droits de base adaptés, les mobilités retirent les accès devenus inutiles, et les départs déclenchent la désactivation ainsi que la révocation des sessions et clés.

Le fournisseur OIDC centralise l’authentification. Les applications vérifient correctement les assertions et créent des sessions locales protégées. Elles valident l’émetteur, l’audience, la signature, l’expiration et les paramètres du flux. Les tokens ne sont ni stockés dans des URLs ni imprimés dans les logs. Le logout local invalide la session, et le système documente comment traiter les refresh tokens et les access tokens déjà émis.

Le modèle RBAC définit les responsabilités générales : élève, enseignant, gestionnaire de contenu, opérateur et administrateur. Une décision au niveau de la ressource vérifie le propriétaire ou la relation métier. L’élève ne lit que ses propres résultats ; l’enseignant modifie uniquement les cours affectés à son équipe. Toute action non couverte est refusée. Les tests négatifs vérifient les accès croisés, les comptes suspendus et les appels directs à l’API.

Les privilèges administratifs utilisent des comptes séparés ou une activation temporaire. Une demande JIT précise le motif, la ressource et la durée. L’approbation est distincte lorsque le risque le requiert. Les sessions sont journalisées, l’expiration est automatique et les comptes d’urgence sont peu nombreux, surveillés et testés.

Les services reçoivent des identités non humaines distinctes. La clé API statique est remplacée par une identité gérée ou fédérée lorsque l’architecture le permet. Sinon, elle reste à portée étroite, est stockée dans un gestionnaire, renouvelée et surveillée. Les comptes de service Kubernetes sont dédiés et ne reçoivent que les verbes nécessaires dans les namespaces concernés. Les rôles cloud sont limités aux actions sur les ressources concernées.

La gouvernance impose un propriétaire à chaque rôle et compte technique, une demande justifiée, une approbation adaptée et une expiration pour les accès temporaires. Une recertification compare les permissions effectives aux responsabilités. Les exceptions possèdent une échéance, des mesures compensatoires et une personne responsable. Le tableau de bord suit les comptes orphelins, les droits privilégiés recertifiés, le délai de révocation et les anomalies de politique.

En cas de compromission, l’équipe suspend l’identité, révoque les sessions et jetons, retire les droits et clés associés et préserve les journaux. Elle recherche les comptes, rôles, applications et clés créés, puis restaure l’accès légitime par une procédure robuste. Le post-incident modifie les règles, les tests et les alertes qui auraient dû empêcher ou détecter l’attaque.

Le défi est réussi si chaque accès peut être expliqué par une identité reconnue, une action précise, une ressource et une portée, une justification métier, une durée, une politique de décision et une trace. La maturité IAM se démontre par l’application effective de ces règles, pas par la seule présence d’un fournisseur d’identité.

## 26. Checklist de mise en œuvre

### Identités et authentification
- Une source de vérité et un propriétaire sont définis pour chaque type d’identité.
- Les facteurs d’authentification sont adaptés au risque.
- La récupération de compte ne contourne pas la sécurité du mécanisme principal.
- Les sessions disposent de durées, de protections et d’une procédure de révocation.
- Les applications valident les assertions et les tokens selon leur type et leur audience.

### Autorisation
- Les permissions sont refusées par défaut sauf règle explicite.
- L’autorisation est vérifiée côté serveur à chaque action sensible et sur chaque ressource.
- RBAC, ABAC ou ReBAC sont choisis selon le besoin, avec des attributs fiables.
- Les rôles sont compréhensibles et les permissions indirectes sont examinées.
- Les tests couvrent les accès autorisés et les tentatives d’accès croisé.

### Privilèges et identités techniques
- Les comptes administratifs sont distincts ou activés temporairement selon le risque.
- Les accès JIT expirent automatiquement et sont liés à une demande.
- Les comptes break-glass sont protégés, surveillés et testés.
- Les comptes de service ont un propriétaire, une portée minimale et un mécanisme de révocation.
- Les secrets techniques ne sont pas partagés sans nécessité et les identifiants durables sont réduits.

### Gouvernance et réponse
- Les arrivées, mobilités et départs entraînent une mise à jour des droits.
- Les accès et rôles sont recertifiés périodiquement.
- Les exceptions sont limitées, justifiées et expirables.
- Les événements sensibles sont journalisés dans un système protégé.
- La procédure de compromission couvre sessions, jetons, clés, rôles et persistance.
- Les métriques suivent le risque réel : délais de révocation, comptes orphelins, privilèges et exceptions.

## 27. Erreurs de conception à éviter

**Confondre connexion et accès.** Une connexion réussie ne doit pas donner un accès général. Chaque action sensible nécessite une décision d’autorisation sur la ressource.

**Faire confiance à des rôles fournis par le navigateur.** Les contrôles de sécurité doivent utiliser des attributs fiables et être exécutés côté serveur.

**Réutiliser des comptes techniques.** Cela élargit l’impact d’une compromission et empêche l’attribution des actions. Préférez des identités distinctes par fonction.

**Donner des droits excessifs pour éviter un incident opérationnel.** Le bon objectif est un accès légitime rapide, avec permissions minimales, procédure d’urgence et révocation testée.

**Négliger les facteurs de récupération.** Un compte MFA peut être détourné si le support contourne facilement les facteurs. La récupération doit être aussi rigoureuse que l’authentification.

**Laisser les sessions trop longues sans stratégie.** Une session peut rester utilisable après le départ ou la compromission. Définissez durée, invalidation, rotation et comportement à la révocation.

**Oublier les privilèges indirects.** La création de Pods, l’impersonation, les modifications de bindings ou les droits de gestion des identités peuvent créer des chemins d’escalade. Évaluez les effets combinés.

**Recertifier sans contexte.** L’approbation en masse ne valide pas réellement les besoins. Présentez la portée, le propriétaire, la dernière utilisation et le risque.

## 28. Glossaire

- **IAM** : gestion des identités et des accès.
- **Identité** : représentation d’une personne, d’un service ou d’un autre sujet dans un système.
- **Authentification** : vérification d’une preuve de contrôle d’identité.
- **Autorisation** : décision de permettre ou non une action sur une ressource.
- **IdP** : fournisseur d’identité qui orchestre l’authentification et peut émettre des assertions.
- **Fédération** : relation de confiance entre systèmes d’identité.
- **OIDC** : couche d’identité fondée sur OAuth 2.0.
- **OAuth 2.0** : cadre de délégation d’accès à des ressources.
- **ID Token** : jeton OIDC contenant des assertions d’authentification destinées au client.
- **Access Token** : jeton présenté à une ressource selon une politique d’accès.
- **MFA** : authentification avec plusieurs facteurs indépendants.
- **RBAC** : autorisation basée sur les rôles.
- **ABAC** : autorisation basée sur des attributs et conditions.
- **ReBAC** : autorisation basée sur les relations entre sujets et ressources.
- **PAM** : gestion des accès privilégiés.
- **JIT** : élévation juste-à-temps, limitée à une fenêtre.
- **JEA** : accès juste suffisant, limité aux opérations nécessaires.
- **Compte break-glass** : compte d’urgence soumis à des contrôles renforcés.
- **Compte non humain** : identité technique utilisée par un service, une tâche ou une application.
- **Privilege creep** : accumulation de droits au-delà du besoin actuel.
- **Recertification** : revue des accès effectifs pour confirmer, réduire ou révoquer les droits.
- **JWT** : format de représentation de claims ; un jeton signé n’est pas automatiquement chiffré.
- **Scope** : ensemble de permissions ou de capacités demandé dans un flux OAuth.
- **Source de vérité** : système faisant autorité sur un attribut ou un état de référence.
- **Deny by default** : refus lorsque aucune règle explicite n’autorise l’action.

## 29. Références officielles

- NIST SP 800-63-4, Digital Identity Guidelines : https://csrc.nist.gov/pubs/sp/800/63/4/final
- Ressources d’implémentation NIST SP 800-63-4 : https://pages.nist.gov/800-63-4-Implementation-Resources/
- NIST SP 800-207, Zero Trust Architecture : https://csrc.nist.gov/pubs/sp/800/207/final
- RFC 9700, Best Current Practice for OAuth 2.0 Security : https://datatracker.ietf.org/doc/html/rfc9700
- OpenID Connect Core 1.0 : https://openid.net/specs/openid-connect-core-1_0.html
- OWASP Authorization Cheat Sheet : https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP Authentication Cheat Sheet : https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- Kubernetes RBAC Good Practices : https://kubernetes.io/docs/concepts/security/rbac-good-practices/
- Kubernetes RBAC : https://kubernetes.io/docs/reference/access-authn-authz/rbac/

Les protocoles et recommandations évoluent. Vérifiez les versions officielles, les capacités de votre fournisseur d’identité et les obligations applicables avant toute mise en production. Les exemples illustrent les principes ; ils ne remplacent pas une revue de la configuration, des tests d’autorisation et des exercices de révocation dans l’environnement réel.

Fin du cours.