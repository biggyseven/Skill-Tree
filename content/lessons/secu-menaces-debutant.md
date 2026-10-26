# Panorama des menaces

> **Encadré de mise en contexte**
>
> Imagine que tu travailles comme technicien informatique dans une entreprise qui possède une plateforme de formation. Les apprenants se connectent avec un compte personnel, consultent leurs cours et passent des évaluations. Les enseignants disposent de comptes leur permettant de gérer les contenus, tandis que les administrateurs assurent la maintenance du système.
>
> Un matin, une employée reçoit un courriel indiquant que son compte sera désactivé si elle ne confirme pas immédiatement son mot de passe. Elle ouvre le lien et saisit ses identifiants sur une page qui ressemble à celle de l'entreprise. Quelques heures plus tard, des connexions inhabituelles apparaissent dans les journaux. Un compte est utilisé pour télécharger des documents, puis des fichiers deviennent inaccessibles.
>
> Plusieurs événements peuvent être liés : une tentative de manipulation, le vol d'identifiants, un accès non autorisé et éventuellement une action destructive. Mais avant de conclure qu'une attaque précise a eu lieu, il faut examiner les faits.
>
> Ce cours t'apprend à reconnaître les principales menaces informatiques, à comprendre comment elles peuvent affecter un système et à choisir les premières protections adaptées. Tu apprendras surtout à raisonner comme un professionnel : observer, identifier les risques, réduire les possibilités d'attaque et signaler correctement les incidents.

## 1. Comprendre ce qu'est une menace informatique

### 1.1. Définition d'une menace

Une **menace informatique** est une situation, une action ou un événement susceptible de compromettre la sécurité d'un système, de ses données ou de son fonctionnement.

Une menace peut provenir d'une personne malveillante, d'un logiciel, d'une erreur humaine, d'une panne matérielle, d'une catastrophe naturelle ou d'une combinaison de plusieurs facteurs.

Une attaque par hameçonnage est une menace. Un employé qui supprime accidentellement un répertoire important peut également provoquer une situation menaçante. Une coupure électrique peut interrompre un serveur et rendre un service inaccessible sans qu'aucun pirate n'intervienne.

Il est donc incorrect de considérer que toute menace informatique provient nécessairement d'un pirate.

Le rôle du professionnel de la cybersécurité consiste à comprendre les événements possibles, à évaluer leurs conséquences et à mettre en place des mesures de réduction du risque.

### 1.2. Différence entre menace, vulnérabilité et risque

**Schéma pédagogique — Le risque naît d'un scénario plausible qui relie une menace à une faiblesse et à un impact.**

~~~text
Actif a proteger
      |
      v
[Vulnerabilite exploitable] <--- [Menace / acteur / evenement]
      |
      v
[Scenario d'incident plausible]
      |
      +---- Probabilite estimee
      +---- Impact estime
      |
      v
[Risque a prioriser]
      |
      v
[Mesure] -> [Test] -> [Risque residuel]
~~~


Ces trois notions sont liées, mais elles ne signifient pas la même chose.

**La menace** est la cause potentielle d'un incident. Par exemple, une personne peut tenter de voler les identifiants d'un employé.

**La vulnérabilité** est une faiblesse qui rend un incident plus facile à provoquer. Il peut s'agir d'un mot de passe réutilisé, d'une application non corrigée ou d'une permission trop large.

**Le risque** représente la possibilité qu'un événement produise des conséquences négatives. Son évaluation tient généralement compte de la vraisemblance et de la gravité des conséquences.

Prenons une situation concrète :

- Menace : une personne cherche à accéder à la messagerie d'une entreprise.
- Vulnérabilité : un compte ne possède pas de protection adaptée et son mot de passe a été divulgué.
- Événement : la personne utilise les identifiants pour se connecter.
- Conséquence : des documents confidentiels sont consultés ou des messages frauduleux sont envoyés.
- Risque : l'entreprise peut subir une fuite de données, une fraude ou une perte de confiance.

Cette distinction est fondamentale. Un outil de sécurité ne doit pas être choisi simplement parce qu'une menace existe. Il faut comprendre quelle faiblesse doit être réduite et quelles conséquences doivent être évitées.

### 1.3. Une menace ne signifie pas qu'une attaque a réussi

Il faut distinguer une possibilité, une tentative et un incident confirmé.

Une entreprise peut recevoir un courriel malveillant sans qu'aucun utilisateur clique dessus. Un serveur peut recevoir des requêtes inhabituelles qui sont bloquées par le pare-feu. Une personne peut tenter d'utiliser un ancien mot de passe sans parvenir à se connecter.

Dans ces situations, une menace ou une tentative existe, mais la compromission n'est pas nécessairement établie.

À l'inverse, un événement apparemment banal peut révéler un incident important. Une connexion depuis un emplacement inhabituel peut être légitime, mais elle mérite parfois une vérification si elle est suivie d'un téléchargement massif de documents.

Le professionnel doit donc distinguer les faits observés des hypothèses. Il ne doit ni ignorer les signaux inquiétants ni déclarer une attaque sans éléments suffisants.

## 2. Relier les menaces à la Triade CIA

Dans le cours précédent, tu as découvert les trois propriétés fondamentales de sécurité : confidentialité, intégrité et disponibilité. Elles permettent d'organiser les conséquences possibles d'une menace.

### 2.1. Menaces contre la confidentialité

La confidentialité est compromise lorsque des informations sont consultées ou divulguées à des personnes qui ne sont pas autorisées à les recevoir.

Exemples :

- un attaquant vole un compte de messagerie et lit des documents internes ;
- un employé transmet une liste de clients au mauvais destinataire ;
- une application permet à un utilisateur de consulter le dossier d'une autre personne ;
- un ordinateur portable contenant des données sensibles est perdu sans protection adaptée.

La prévention s'appuie notamment sur le contrôle d'accès, la protection des identités, le chiffrement et la limitation des informations accessibles.

### 2.2. Menaces contre l'intégrité

L'intégrité concerne l'exactitude et la protection des informations contre les modifications ou destructions non autorisées.

Exemples :

- un compte compromis modifie des factures ;
- un programme altère des fichiers ;
- une erreur de manipulation supprime des enregistrements ;
- une configuration réseau est changée sans validation.

Les contrôles d'accès, la validation des données, la journalisation, la gestion des changements et les sauvegardes contribuent à réduire ces risques.

### 2.3. Menaces contre la disponibilité

La disponibilité est compromise lorsque les utilisateurs autorisés ne peuvent plus accéder aux données ou aux services dont ils ont besoin.

Exemples :

- une panne de serveur arrête une application ;
- une attaque par déni de service surcharge un site ;
- un rançongiciel rend des fichiers inutilisables ;
- une coupure réseau empêche les utilisateurs d'accéder à une base de données.

La supervision, la redondance, la maintenance, les sauvegardes testées et la préparation à la reprise contribuent à protéger la disponibilité.

### 2.4. Une même menace peut affecter plusieurs propriétés

Imagine qu'un attaquant obtienne les droits d'administration d'un serveur.

Il peut télécharger des fichiers confidentiels, modifier des données et supprimer des composants nécessaires au service. La confidentialité, l'intégrité et la disponibilité peuvent alors être compromises au cours du même incident.

Il faut donc déterminer les propriétés touchées en fonction des effets observés, et non supposer qu'une menace correspond toujours à une seule propriété.

## 3. Qui ou quoi peut être à l'origine d'une menace ?

Il est utile de comprendre qu'une menace peut avoir des origines différentes. La prévention ne sera pas identique selon que l'incident provient d'une personne malveillante, d'une erreur ou d'un événement technique.

### 3.1. Les cybercriminels

Les cybercriminels cherchent généralement à obtenir un avantage financier ou matériel. Ils peuvent voler des identifiants, escroquer des victimes, dérober des informations, extorquer de l'argent ou utiliser les ressources d'un système compromis.

Certains agissent seuls, tandis que d'autres utilisent des services criminels spécialisés. Une personne peut, par exemple, vendre des identifiants volés à une autre qui les utilisera pour pénétrer un environnement.

L'objectif n'est pas toujours immédiatement visible. Une activité apparemment limitée peut servir à préparer une fraude ou une compromission plus importante.

### 3.2. Les acteurs motivés par le renseignement

Certaines opérations cherchent à obtenir des informations stratégiques, scientifiques, diplomatiques, militaires ou économiques. Elles peuvent viser des administrations, des entreprises, des infrastructures critiques ou des organisations détenant des informations sensibles.

Ces opérations peuvent être longues et discrètes. L'attaquant peut chercher à rester présent dans un environnement plutôt qu'à perturber immédiatement son fonctionnement.

Il serait toutefois imprudent d'attribuer automatiquement une intrusion à un gouvernement ou à une organisation précise. L'attribution d'une opération nécessite des éléments techniques et contextuels qui dépassent souvent les capacités d'un simple observateur.

### 3.3. Les acteurs idéologiques

Certains acteurs cherchent à défendre une cause politique, sociale ou idéologique. Ils peuvent tenter de publier des informations, de perturber un service ou de modifier l'apparence d'un site.

Leur motivation peut influencer le choix de la cible et les conséquences recherchées. Cela ne signifie pas que toutes les personnes qui défendent une cause commettent des actes malveillants : il faut examiner les actions concrètes.

### 3.4. Les personnes internes à l'organisation

Un risque peut provenir d'un employé, d'un prestataire ou d'un ancien collaborateur disposant encore d'accès.

La personne peut agir volontairement ou commettre une erreur. Un salarié mécontent pourrait supprimer des fichiers, mais un collègue peut également divulguer un document en se trompant de destinataire.

La protection contre les risques internes repose notamment sur des droits adaptés, des comptes individuels, des journaux d'audit et des procédures claires lors des changements de fonction ou des départs.

### 3.5. Les erreurs et les événements techniques

Un incident peut survenir sans intention malveillante : panne électrique, défaut logiciel, matériel défaillant, erreur d'administration, incident environnemental ou mauvaise planification d'une maintenance.

La cybersécurité doit également s'intéresser à ces scénarios, car leurs conséquences peuvent être aussi sérieuses que celles d'une attaque.

Une base de données supprimée accidentellement peut être aussi indisponible qu'une base sabotée. Une configuration réseau incorrecte peut provoquer une interruption sans qu'un pirate soit intervenu.

La distinction entre origine malveillante et origine accidentelle est importante pour comprendre l'événement et choisir les mesures correctives.

## 4. L'ingénierie sociale et les manipulations humaines

### 4.1. Qu'est-ce que l'ingénierie sociale ?

L'**ingénierie sociale** désigne des techniques de manipulation qui cherchent à amener une personne à révéler une information, à effectuer une action ou à accorder un accès.

Plutôt que de s'attaquer uniquement à un logiciel, l'attaquant exploite la confiance, l'urgence, la curiosité, la peur ou le désir d'aider.

Une personne peut ainsi transmettre un mot de passe, ouvrir un document dangereux, envoyer un paiement ou approuver une connexion qui ne devrait pas être autorisée.

L'ingénierie sociale ne repose pas toujours sur des techniques informatiques complexes. Elle exploite surtout le contexte et le comportement humain.

### 4.2. L'hameçonnage

**Schéma pédagogique — Le message trompeur cherche à déclencher une action qui compromet l'identité ou le poste.**

~~~text
[Courriel imite une source de confiance]
                 |
                 v
       [Lien ou piece jointe]
                 |
       +---------+----------+
       |                    |
       v                    v
[Verification externe]   [Saisie du secret]
       |                    |
       v                    v
[Signalement]          [Compte expose]
                            |
                            v
                  [Revoquer session / alerter]

Le bon réflexe est de vérifier par un canal indépendant.
~~~


L'hameçonnage, aussi appelé *phishing*, consiste à tromper une personne pour l'amener à révéler des informations ou à effectuer une action dangereuse.

Un courriel frauduleux peut imiter un service de messagerie, une banque, un transporteur, une plateforme de formation ou un responsable hiérarchique.

Le message peut prétendre qu'un compte sera bloqué, qu'une facture est en attente ou qu'une connexion inhabituelle doit être vérifiée immédiatement.

Les signaux d'alerte possibles comprennent :

- une demande inattendue de mot de passe ou de code de connexion ;
- un sentiment d'urgence inhabituel ;
- un lien qui mène vers un domaine différent de celui du service attendu ;
- une pièce jointe inattendue ;
- une demande de paiement ou de modification de coordonnées bancaires par un canal inhabituel ;
- une demande qui contourne les procédures normales de l'organisation.

Aucun signal n'est une preuve absolue. Un message légitime peut être maladroit et un message frauduleux peut sembler très professionnel. Il faut considérer l'ensemble du contexte.

### 4.3. Hameçonnage ciblé

Le hameçonnage ciblé, souvent appelé *spear phishing*, vise une personne ou un groupe précis.

L'attaquant peut reprendre le nom d'un collègue, utiliser le vocabulaire de l'entreprise ou mentionner un projet réel. Le message paraît alors plus crédible qu'un envoi générique.

Par exemple, une employée reçoit un message indiquant que le responsable du projet a partagé un nouveau document. Le message utilise le nom du projet et semble provenir d'un collègue.

Le bon réflexe consiste à examiner la demande, vérifier l'expéditeur réel et confirmer les demandes sensibles par un canal distinct déjà connu. Pour un paiement ou un changement de coordonnées bancaires, il faut suivre une procédure de vérification définie à l'avance.

### 4.4. Fraude au président et aux paiements

Une personne malveillante peut se faire passer pour un dirigeant ou un fournisseur et demander un virement urgent.

La demande peut invoquer une acquisition confidentielle, un problème de délai ou une facture à régler immédiatement. La victime peut se sentir obligée d'agir rapidement.

Pour réduire le risque, les entreprises doivent définir des règles d'approbation des paiements et de vérification des changements bancaires. Une demande reçue par courriel ne doit pas permettre de contourner les contrôles.

La sensibilisation individuelle est utile, mais les procédures organisationnelles sont indispensables. Une bonne procédure doit faciliter la vérification, même lorsque le demandeur semble important ou pressé.

### 4.5. Faux support technique

Un escroc peut prétendre représenter le support informatique et demander l'installation d'un outil, la communication d'un code ou la désactivation d'une protection.

Il peut également afficher un faux avertissement qui demande d'appeler un numéro de téléphone.

Un technicien doit vérifier l'identité du demandeur par les canaux officiels, suivre les procédures d'assistance et ne pas communiquer les secrets d'authentification.

Un message qui prétend provenir du support n'est pas une preuve suffisante de légitimité.

### 4.6. Prévenir les manipulations humaines

La prévention ne consiste pas à demander aux utilisateurs de se méfier de tout. Elle doit leur fournir des réflexes simples et des moyens de vérifier les demandes inhabituelles.

Une bonne pratique consiste à :

1. ralentir lorsque le message impose une action urgente ;
2. vérifier l'identité et le contexte de la demande ;
3. ne pas ouvrir un lien ou une pièce jointe inattendue sans vérification ;
4. ne jamais transmettre un mot de passe en réponse à un message ;
5. confirmer les opérations sensibles par un canal distinct ;
6. signaler les messages suspects au contact de sécurité prévu.

Les organisations devraient aussi faciliter le signalement d'une erreur. Une personne qui pense avoir cliqué sur un lien suspect doit pouvoir prévenir rapidement le service concerné sans craindre d'être humiliée. Une réaction rapide peut limiter les dégâts.

## 5. Les logiciels malveillants

### 5.1. Définition

Un logiciel malveillant, ou *malware*, est un programme conçu pour effectuer une action nuisible ou non autorisée sur un système.

Les comportements possibles sont variés : voler des informations, espionner les utilisateurs, modifier des fichiers, perturber des services ou donner à un tiers un accès non autorisé.

Il existe plusieurs catégories de logiciels malveillants. Elles se distinguent notamment par leurs modes de propagation et leurs objectifs.

### 5.2. Le virus informatique

Un virus est un programme qui peut se rattacher à un fichier ou à un autre élément exécutable et se propager lorsque cet élément est utilisé.

Selon son fonctionnement, il peut modifier des fichiers, perturber un système ou déclencher d'autres actions nuisibles.

Il ne faut pas utiliser le mot « virus » pour désigner automatiquement tous les logiciels malveillants. Le terme *malware* est plus général.

### 5.3. Le ver informatique

Un ver peut se propager entre des systèmes sans dépendre exactement du même mécanisme qu'un virus classique. Certains exploitent des failles ou des services accessibles sur un réseau pour atteindre d'autres machines.

Une propagation rapide peut entraîner une saturation des ressources, des interruptions de service et des compromissions successives.

La limitation des accès réseau, la correction des vulnérabilités et la segmentation contribuent à réduire les possibilités de propagation.

### 5.4. Le cheval de Troie

Un cheval de Troie est un programme qui semble légitime ou utile, mais qui dissimule une fonction malveillante.

Il peut être présenté sous la forme d'un outil, d'un document, d'un installateur ou d'une application. L'utilisateur croit exécuter une fonction normale, alors que le programme effectue également des actions non autorisées.

Télécharger un logiciel depuis une source officielle, vérifier son origine et limiter les privilèges d'exécution sont des mesures utiles.

### 5.5. Le rançongiciel

Un rançongiciel, ou *ransomware*, cherche à bloquer l'accès à un système ou à des données, souvent en chiffrant les fichiers, puis exige une rançon pour tenter de les rendre accessibles ou pour menacer de divulguer des informations volées.

Certains incidents associent plusieurs opérations : compromission d'un compte, collecte de données, déplacement vers d'autres machines et action destructive.

Payer une rançon ne garantit ni la récupération des données ni la suppression des copies détenues par l'attaquant. Une organisation doit préparer ses moyens de reprise et son processus de réponse aux incidents à l'avance.

Les mesures de prévention comprennent notamment la gestion des correctifs, la protection des accès distants, les comptes à privilèges limités, la surveillance, la segmentation et les sauvegardes protégées et testées.

### 5.6. Les logiciels espions

Un logiciel espion cherche à recueillir des informations sur un utilisateur, un appareil ou une organisation sans autorisation appropriée.

Selon ses capacités, il peut surveiller des activités, collecter des informations saisies ou transmettre des données vers un tiers.

Une consommation inhabituelle de ressources ou un comportement étrange peut être un signal, mais ne suffit pas à confirmer une infection. Il faut utiliser des mécanismes de détection adaptés et procéder à une investigation.

### 5.7. Les enregistreurs de frappe

Un enregistreur de frappe, ou *keylogger*, est un mécanisme qui enregistre les frappes au clavier. Certains usages peuvent être légitimes et explicitement autorisés, mais les logiciels malveillants de cette catégorie servent notamment à collecter des mots de passe et d'autres informations.

Si un terminal est compromis, changer le mot de passe depuis ce même terminal peut ne pas suffire. Il faut évaluer l'état de l'appareil et, si nécessaire, utiliser un appareil de confiance pour rétablir les accès.

### 5.8. Les portes dérobées et l'accès distant malveillant

Une porte dérobée est un moyen d'accès qui contourne les mécanismes normaux ou qui n'est pas autorisé par le responsable du système.

Certains logiciels malveillants établissent un mécanisme permettant à un attaquant de communiquer à distance avec le système compromis.

Il faut distinguer les outils d'administration à distance légitimes des usages malveillants. Un outil connu peut être utilisé à des fins légitimes ou détourné par un intrus. Le contexte, les permissions, l'origine de l'installation et les traces d'utilisation sont importants.

### 5.9. Les signes possibles d'une infection

Des signaux peuvent justifier une vérification :

- apparitions répétées de fenêtres inhabituelles ;
- applications inconnues qui s'exécutent ;
- ralentissements inexpliqués et persistants ;
- connexions ou échanges réseau inhabituels ;
- désactivation inattendue de protections ;
- fichiers renommés ou devenus inaccessibles ;
- alertes de sécurité ;
- tentatives de connexion suspectes liées à un appareil.

Ces signes ne sont pas spécifiques à une infection. Une mise à jour, une panne matérielle ou une application légitime peut produire des symptômes similaires.

Il faut éviter de supprimer des fichiers au hasard ou de réinstaller immédiatement un système sans réfléchir à la préservation des preuves et aux besoins de l'organisation. Dans un environnement professionnel, il est préférable de suivre la procédure d'incident et de solliciter les responsables compétents.

## 6. Les menaces liées aux mots de passe et aux identités

### 6.1. Le vol d'identifiants

Les identifiants peuvent être volés à l'aide d'un faux formulaire, d'un logiciel malveillant, d'une fuite de données ou d'une manipulation directe.

Un compte compromis peut permettre de lire des messages, de consulter des documents, de modifier des informations ou de réinitialiser d'autres comptes.

Le risque dépend des privilèges associés au compte. Un compte ordinaire peut représenter un point d'entrée, tandis qu'un compte administrateur peut donner accès à des ressources beaucoup plus importantes.

### 6.2. La réutilisation des mots de passe

Lorsqu'une personne utilise le même mot de passe sur plusieurs services, la compromission d'un service peut faciliter l'accès aux autres.

Des attaquants peuvent essayer des identifiants déjà divulgués sur d'autres plateformes. Ce mécanisme est souvent appelé *credential stuffing*.

L'utilisation de mots de passe uniques et suffisamment robustes limite l'impact d'une fuite. Un gestionnaire de mots de passe peut faciliter la gestion de secrets différents pour chaque service.

### 6.3. La force brute et les tentatives automatisées

Une attaque par force brute consiste à essayer de nombreuses valeurs pour deviner un secret d'authentification. D'autres attaques utilisent des listes de mots de passe fréquents ou des identifiants déjà compromis.

Les protections possibles comprennent la limitation des tentatives, la détection des comportements anormaux, la protection des comptes, l'utilisation de secrets robustes et l'authentification multifacteur.

Les mécanismes de limitation doivent être conçus avec précaution afin d'éviter qu'un attaquant puisse bloquer facilement les comptes légitimes par des tentatives répétées.

### 6.4. L'authentification multifacteur

L'authentification multifacteur associe au moins deux facteurs distincts parmi les catégories suivantes :

- quelque chose que l'utilisateur connaît, comme un mot de passe ;
- quelque chose qu'il possède, comme un appareil ou une clé de sécurité ;
- une caractéristique qui lui est propre, par exemple une donnée biométrique dans un système prévu à cet effet.

La MFA réduit le risque que le seul vol d'un mot de passe suffise à accéder à un compte. Toutes les méthodes n'offrent toutefois pas le même niveau de résistance aux manipulations.

Il reste important de sécuriser les mécanismes de récupération de compte et de protéger les appareils utilisés pour l'authentification.

### 6.5. Les sessions et les jetons d'accès

Après une connexion, une application peut utiliser un mécanisme de session ou un jeton pour éviter de demander les identifiants à chaque action.

Ces éléments peuvent devenir sensibles : une personne qui obtient un jeton valide peut parfois agir comme l'utilisateur auquel il est associé.

Il faut les protéger, limiter leur durée de validité lorsque cela est approprié, sécuriser leur stockage et prévoir les moyens de révoquer les sessions en cas de compromission.

Un utilisateur ne doit pas publier des jetons d'accès dans un dépôt de code, un message public ou un fichier de diagnostic.

## 7. Les vulnérabilités des logiciels et des systèmes

### 7.1. Qu'est-ce qu'une vulnérabilité technique ?

Une vulnérabilité est une faiblesse qui peut être exploitée ou déclencher un incident. Elle peut se trouver dans un logiciel, une configuration, une architecture, un processus ou un contrôle organisationnel.

Une vulnérabilité n'est pas toujours une faille spectaculaire. Un service d'administration exposé inutilement, une permission excessive ou une procédure de récupération de compte trop faible peut également créer un risque.

Les vulnérabilités doivent être considérées dans leur contexte : l'existence d'une faiblesse ne signifie pas qu'elle sera nécessairement exploitée, mais elle mérite une évaluation.

### 7.2. Les logiciels non corrigés

Un logiciel peut contenir une faiblesse connue pour laquelle une mise à jour de sécurité existe.

Si le système n'est pas corrigé, l'organisation peut rester exposée à une vulnérabilité que des attaquants savent déjà exploiter.

La gestion des correctifs doit comprendre l'inventaire des logiciels, l'identification des versions, l'évaluation de la gravité, les tests et la planification de l'installation.

Il ne faut pas ignorer les mises à jour importantes, mais il convient de les préparer selon le contexte. Pour les systèmes critiques, il peut être nécessaire de prévoir un environnement de test ou une procédure de retour arrière.

### 7.3. Les services inutilement exposés

Un service qui accepte des connexions depuis un réseau ne devrait être accessible qu'aux personnes ou systèmes qui en ont besoin.

Une interface d'administration exposée à Internet peut attirer des tentatives d'accès non autorisées. Un port laissé ouvert sans raison peut augmenter la surface d'attaque.

Il faut donc inventorier les services, comprendre leur fonction, limiter les accès et supprimer les services inutiles lorsque cela peut être fait en sécurité.

### 7.4. Les erreurs de configuration

Une mauvaise configuration peut annuler une partie des protections prévues.

Exemples :

- un espace de stockage est rendu public par erreur ;
- des comptes possèdent des droits trop élevés ;
- une règle de pare-feu autorise davantage de trafic que nécessaire ;
- un mécanisme de sauvegarde n'est pas protégé contre la suppression ;
- une application conserve des secrets directement dans un fichier de configuration accessible.

La gestion des configurations doit être documentée et vérifiée. Les paramètres importants doivent être contrôlés après chaque changement significatif.

### 7.5. Les erreurs de programmation

Une application peut contenir des faiblesses de contrôle d'accès, de validation des entrées ou de gestion des sessions.

Une application Web doit par exemple vérifier côté serveur qu'un utilisateur est autorisé à effectuer l'action demandée. Masquer un bouton dans l'interface ne suffit pas, car un utilisateur peut parfois construire une requête différente.

La sécurité applicative repose notamment sur la conception, la revue du code, les tests, les mises à jour des dépendances et la surveillance de l'application en exploitation.

### 7.6. La gestion des vulnérabilités

Un programme élémentaire de gestion des vulnérabilités suit généralement plusieurs étapes :

1. inventorier les équipements et logiciels ;
2. identifier les versions et les faiblesses connues ;
3. évaluer la gravité et l'exposition ;
4. décider du traitement prioritaire ;
5. appliquer les corrections ou les mesures compensatoires ;
6. vérifier que la correction fonctionne ;
7. conserver une trace de la décision et du résultat.

L'ordre de traitement ne doit pas dépendre uniquement d'un score technique. Il faut également tenir compte de l'exposition, de la facilité d'exploitation, de la criticité de l'actif et des conséquences possibles.

## 8. Les attaques contre les réseaux

### 8.1. Pourquoi les réseaux sont-ils ciblés ?

Un réseau permet aux appareils de communiquer et aux services de s'échanger des données. Lorsqu'un service est accessible, il peut aussi devenir un point de tentative d'intrusion.

La sécurité réseau cherche notamment à limiter les communications inutiles, à détecter les activités suspectes et à protéger les échanges.

Un équipement réseau mal configuré peut exposer un service, permettre un accès inattendu ou interrompre la communication entre des composants légitimes.

### 8.2. L'interception des communications

L'interception consiste à recueillir des données qui circulent sur un réseau sans autorisation appropriée.

Sur un réseau mal protégé, certaines informations peuvent être exposées aux appareils ou personnes capables d'observer le trafic. Le risque dépend des protocoles utilisés, de la configuration et de la position de l'observateur.

Le chiffrement des communications, les réseaux correctement configurés et la gestion des accès limitent ce risque.

Il est important de comprendre que le chiffrement ne masque pas nécessairement toutes les métadonnées. Selon le protocole, certaines informations comme les adresses de communication, les volumes ou les horaires peuvent encore être observables.

### 8.3. Les attaques de l'intermédiaire

Une attaque dite *man-in-the-middle* consiste à s'interposer dans une communication afin de l'observer ou éventuellement de la modifier.

Une protection adaptée dépend du protocole et de la situation. La validation correcte des certificats, le chiffrement authentifié et l'absence de contournement des avertissements de sécurité sont importants dans les communications Web sécurisées.

Un utilisateur ne devrait pas ignorer une alerte de certificat sans comprendre sa cause.

### 8.4. L'usurpation d'identité réseau

L'usurpation consiste à présenter une identité ou une information qui ne correspond pas à l'origine réelle.

Elle peut porter sur une adresse, un nom, une identité d'expéditeur ou d'autres éléments d'un protocole.

L'usurpation n'implique pas nécessairement que l'attaquant a pris le contrôle de la véritable identité. Elle peut cependant faciliter certaines manipulations ou rendre l'analyse plus difficile.

Les mécanismes de vérification et la corrélation de plusieurs sources de journalisation contribuent à mieux comprendre l'origine des communications.

### 8.5. Le déni de service

Une attaque par déni de service cherche à empêcher un service de répondre correctement aux utilisateurs légitimes. Elle peut exploiter des ressources limitées ou envoyer un volume de demandes supérieur à ce que le système peut traiter.

Une attaque distribuée utilise plusieurs sources pour produire ou amplifier la charge.

Les protections possibles comprennent le filtrage, la limitation de débit, la répartition de charge et des services de protection spécialisés. Elles doivent être adaptées aux caractéristiques de l'application et du réseau.

Il faut éviter de confondre une attaque avec une simple montée de trafic légitime. Une campagne commerciale peut également provoquer une forte charge. L'analyse doit se fonder sur les mesures, les journaux et le comportement observé.

### 8.6. Le Wi-Fi mal sécurisé

Un réseau Wi-Fi mal configuré peut faciliter l'accès d'une personne non autorisée ou exposer les communications des utilisateurs.

Les bonnes pratiques comprennent l'utilisation de mécanismes de sécurité modernes, la désactivation des paramètres dangereux, la mise à jour des équipements, la séparation des réseaux selon les besoins et la protection des comptes d'administration.

Dans une entreprise, le réseau destiné aux visiteurs ne devrait pas nécessairement accorder le même accès que celui utilisé pour les postes administratifs.

### 8.7. La segmentation réseau

**Schéma pédagogique — La segmentation réduit le déplacement latéral ; les flux entre zones doivent être filtrés explicitement.**

~~~text
              [Routeur / pare-feu L3]
                 /       |       \
                v        v        v
        [Utilisateurs] [Serveurs] [Invites]
          VLAN 10      VLAN 20    VLAN 40
             |            |          |
       droits limites  applis      Internet
             \            |          /
              +---- politiques inter-zones ----+

Séparer les VLAN et filtrer les flux routés sont deux actions complémentaires.
~~~


La segmentation divise un réseau en zones dont les communications sont contrôlées.

Par exemple, les postes des apprenants, les postes administratifs et les serveurs peuvent être placés dans des segments différents, avec des règles qui limitent les échanges aux besoins de l'activité.

La segmentation peut réduire la possibilité de déplacement d'un attaquant d'un système compromis vers d'autres actifs. Elle ne remplace toutefois pas la sécurité de chaque système.

## 9. Les menaces contre les sites Web et les applications

### 9.1. Les formulaires et les entrées utilisateur

Les applications Web reçoivent des données venant des utilisateurs : identifiants, recherches, formulaires, commentaires, commandes et fichiers.

Si l'application traite ces entrées sans validation ni protections adaptées, une faille peut permettre de contourner des règles, d'accéder à des données ou de modifier le comportement attendu de l'application.

Il faut valider les entrées, employer les mécanismes de requêtes sécurisés fournis par les frameworks et appliquer des contrôles d'autorisation côté serveur.

### 9.2. Les contrôles d'accès défectueux

Une application peut afficher des informations différentes selon le compte connecté. Si le serveur vérifie mal les droits, un utilisateur peut parfois accéder à une ressource qui appartient à quelqu'un d'autre.

Un exemple classique est l'accès à un dossier en changeant un identifiant dans une URL sans que le serveur vérifie si le dossier appartient réellement à l'utilisateur.

La correction doit se faire du côté serveur, en fonction de l'identité et des autorisations réelles. Il ne suffit pas de cacher les liens dans l'interface.

### 9.3. Les attaques liées aux sessions

Une mauvaise gestion des sessions peut exposer des comptes si les jetons sont accessibles, prévisibles, mal stockés ou conservés trop longtemps dans un contexte inadapté.

Les applications doivent utiliser des mécanismes de session conçus pour la sécurité, protéger les cookies, appliquer des délais adaptés et offrir des moyens de révoquer les sessions.

Après un incident d'authentification, il peut être nécessaire d'invalider les sessions existantes plutôt que de simplement changer un mot de passe.

### 9.4. Les dépendances et bibliothèques

Les applications modernes utilisent des bibliothèques externes. Celles-ci peuvent contenir des vulnérabilités ou devenir non maintenues.

Il faut donc connaître les dépendances utilisées, suivre les avis de sécurité pertinents, corriger les versions vulnérables et limiter les composants inutiles.

Un logiciel peut être vulnérable même si son propre code semble correct, simplement parce qu'il dépend d'une bibliothèque affectée.

### 9.5. La protection des secrets applicatifs

Les clés d'API, jetons, mots de passe de base de données et clés privées ne doivent pas être publiés dans un dépôt public ou transmis dans des messages non protégés.

Un secret divulgué doit être considéré comme potentiellement compromis. Selon sa nature, il faudra le révoquer ou le remplacer, vérifier son utilisation et examiner les traces d'accès.

Déplacer un secret dans un fichier séparé ne suffit pas s'il reste accessible aux personnes ou programmes qui n'en ont pas besoin. Il faut contrôler les permissions et le cycle de vie des secrets.

## 10. Les menaces liées au Cloud et aux services en ligne

### 10.1. Le Cloud ne supprime pas la responsabilité du client

Un fournisseur Cloud assure certaines fonctions de l'infrastructure, mais le client reste généralement responsable de plusieurs aspects selon le service et le contrat.

Cela peut inclure les comptes, les données, les permissions, les configurations, les secrets et la manière dont les ressources sont exposées.

La répartition précise des responsabilités dépend du modèle de service et du fournisseur. Il faut lire la documentation et éviter de supposer que toute la sécurité est automatiquement prise en charge.

### 10.2. Les erreurs de permissions

Un espace de stockage ou une ressource Cloud peut être rendu accessible à un public trop large.

Le problème ne vient pas nécessairement d'une faille spectaculaire du fournisseur : une configuration incorrecte peut suffire.

Les organisations doivent examiner régulièrement les permissions, limiter les accès publics aux ressources qui doivent réellement l'être et conserver une trace des modifications importantes.

### 10.3. Les comptes Cloud compromis

Un attaquant qui obtient un compte disposant de droits importants peut créer de nouvelles ressources, consulter des données, modifier des configurations ou supprimer des éléments.

La protection de ces comptes exige des identités individuelles, des rôles adaptés, une authentification renforcée et une surveillance des opérations sensibles.

Les clés d'accès qui ne sont plus utilisées doivent être révoquées. Les comptes et autorisations doivent être réexaminés lors des changements de fonction et des départs.

### 10.4. La disponibilité des services Cloud

Un incident de configuration, une panne du fournisseur ou l'épuisement des ressources disponibles peut interrompre un service.

La disponibilité dépend aussi de l'architecture choisie, des dépendances, de la planification des capacités et des procédures de récupération.

Un système qui repose sur un seul composant ou une seule région peut présenter un point de défaillance important. Les mécanismes de redondance doivent cependant être définis selon les objectifs, les coûts et les contraintes.

## 11. Les menaces liées aux prestataires et à la chaîne d'approvisionnement

### 11.1. Pourquoi un prestataire peut-il représenter un risque ?

Une organisation dépend souvent de logiciels, de fournisseurs, d'intégrateurs, d'hébergeurs et de services externes.

Ces partenaires peuvent disposer d'accès techniques ou traiter des données pour son compte. Une compromission chez un prestataire peut donc avoir des conséquences pour ses clients.

Le risque ne signifie pas qu'il faut éviter toute externalisation. Il faut comprendre les dépendances et définir des contrôles adaptés.

### 11.2. Les logiciels provenant de sources non fiables

Un installateur modifié ou un paquet logiciel obtenu depuis une source non vérifiée peut intégrer des composants malveillants.

Pour réduire ce risque, il faut utiliser des sources de confiance, vérifier les signatures ou empreintes lorsqu'elles sont disponibles et limiter les droits des programmes exécutés.

Les outils de développement doivent également protéger les dépendances, les secrets de déploiement et les environnements de construction.

### 11.3. Les accès des prestataires

Un fournisseur peut avoir besoin d'un accès distant pour réaliser une maintenance. Si cet accès n'est pas limité, protégé ou révoqué à la fin de la mission, il peut créer une exposition durable.

Les bonnes pratiques incluent des comptes nominatifs lorsque cela est possible, des permissions limitées à la tâche, des accès temporaires, la journalisation et une procédure de révocation.

### 11.4. Planifier la sécurité des dépendances

Une organisation devrait connaître ses fournisseurs critiques, les composants logiciels importants et les accès externes nécessaires.

Elle peut définir les exigences de sécurité, les règles de notification des incidents, les responsabilités et les modalités de récupération.

La question à se poser n'est pas uniquement « Notre propre système est-il sécurisé ? », mais aussi « De quelles dépendances avons-nous besoin, et quelles conséquences subirions-nous si l'une d'elles était compromise ou indisponible ? »

## 12. Les menaces physiques et environnementales

### 12.1. La sécurité physique fait partie de la cybersécurité

Un ordinateur, un serveur ou un équipement réseau peut être compromis si une personne obtient un accès physique non autorisé.

Une personne qui vole un ordinateur peut chercher à accéder aux fichiers, aux comptes ou aux clés qui y sont stockés. Une personne qui débranche un câble ou coupe une alimentation peut perturber un service sans exploiter de logiciel.

La protection physique doit donc être adaptée aux actifs et à leur criticité.

### 12.2. Le vol et la perte d'équipements

Les ordinateurs portables, smartphones, clés USB et équipements d'administration sont susceptibles d'être perdus ou volés.

Le chiffrement des supports, le verrouillage des sessions, la gestion des appareils et la capacité de révoquer les accès réduisent certaines conséquences.

Il est également préférable de limiter le stockage local de données sensibles lorsque ce stockage n'est pas nécessaire.

### 12.3. Les risques environnementaux

Les incendies, les inondations, la chaleur, l'humidité ou les coupures d'alimentation peuvent perturber les systèmes.

La continuité de service peut nécessiter une alimentation secourue, un refroidissement adapté, une protection physique et des procédures de reprise.

Les sauvegardes conservées dans le même lieu que les systèmes principaux peuvent être exposées au même événement. Leur emplacement et leur protection doivent tenir compte des scénarios envisagés.

### 12.4. Le support amovible

Une clé USB inconnue peut contenir des fichiers dangereux ou des données sensibles. Elle peut aussi être perdue et exposer les informations qu'elle contient.

Il faut éviter de connecter des supports inconnus à un poste professionnel, respecter les procédures de sécurité et analyser les supports selon les moyens approuvés par l'organisation.

Ne branche pas une clé trouvée dans un lieu public pour découvrir son contenu. Le risque ne vaut pas la curiosité.

## 13. Les menaces internes et les erreurs humaines

### 13.1. Les erreurs sont prévisibles

Les utilisateurs peuvent se tromper de destinataire, supprimer un fichier, accorder une permission excessive ou oublier de verrouiller un poste.

La sécurité ne doit pas dépendre de l'idée que personne ne fera jamais d'erreur. Elle doit prévoir des mécanismes qui réduisent la probabilité et les conséquences de ces erreurs.

Des autorisations adaptées, des confirmations pour les actions destructrices, des sauvegardes et des procédures claires peuvent aider.

### 13.2. Les privilèges excessifs

Un utilisateur peut disposer de permissions supérieures à celles dont il a besoin.

Plus les privilèges sont importants, plus une erreur ou une compromission peut avoir de conséquences.

Le principe du moindre privilège recommande de limiter les droits à ce qui est nécessaire. Il est également utile de séparer les comptes quotidiens des comptes administratifs lorsque le contexte le justifie.

### 13.3. Les comptes oubliés

Un compte peut rester actif après le départ d'un employé ou après la fin d'un contrat avec un prestataire.

Un ancien compte actif représente un risque si personne ne vérifie qui l'utilise ou s'il conserve des accès sensibles.

Les organisations doivent suivre le cycle de vie des identités : création, modification, revue périodique, suspension et suppression lorsque cela est approprié.

### 13.4. Une culture de signalement

Un employé qui signale rapidement un clic accidentel, un document envoyé à la mauvaise personne ou une alerte inhabituelle permet parfois d'éviter un incident plus grave.

Une politique de sécurité efficace encourage le signalement rapide et privilégie l'analyse des faits. La dissimulation d'une erreur par peur d'une sanction peut retarder les mesures correctives.

La responsabilité individuelle reste importante, mais elle doit être associée à des procédures qui facilitent la prévention et la réaction.

## 14. Reconnaître les signes d'un incident

### 14.1. Les indicateurs ne sont pas toujours évidents

Une attaque ne déclenche pas nécessairement une grande alerte. Certains incidents produisent des symptômes discrets, parfois similaires à ceux d'un problème technique ordinaire.

Les signaux possibles comprennent :

- connexions inhabituelles ou à des heures inattendues ;
- échecs d'authentification répétés ;
- création de comptes ou modification de permissions non prévues ;
- téléchargements massifs de données ;
- désactivation inattendue des protections ;
- changements de fichiers inexpliqués ;
- consommation inhabituelle de ressources ;
- nouveaux services ou processus inconnus ;
- alertes du système de sécurité ;
- plaintes simultanées d'utilisateurs qui ne peuvent plus accéder à un service.

Il faut examiner ces événements en tenant compte de l'activité légitime. Une hausse du trafic peut venir d'un événement commercial, et une connexion tardive peut être liée à une intervention autorisée.

### 14.2. Les journaux

Les journaux enregistrent les événements produits par les systèmes, les applications et les équipements.

Ils peuvent aider à répondre à des questions telles que : quel compte s'est connecté, quand une action a été réalisée et quelle erreur a été signalée ?

Pour être utiles, les journaux doivent être suffisamment détaillés, protégés contre les modifications et conservés pendant une durée adaptée aux objectifs de l'organisation.

Il faut également tenir compte de l'heure système. Si plusieurs composants utilisent des heures différentes, reconstituer l'ordre des événements devient plus difficile.

### 14.3. Le principe de corrélation

**Schéma pédagogique — Plusieurs sources et une chronologie cohérente donnent plus de contexte qu'un signal isolé.**

~~~text
[Email / passerelle] ----\
[Identite / MFA] ----------+--> [Collecte centralisee] --> [Correlation]
[Endpoint / EDR] ----------+             |                     |
[DNS / pare-feu] ----------/             v                     v
                                      horodatage           alerte enrichie
                                                            |
                                                            v
                                                    triage humain

Corréler ne signifie pas que chaque signal est une preuve définitive.
~~~


Un événement isolé est souvent ambigu. Plusieurs événements liés peuvent révéler un scénario plus clair.

Par exemple :

1. plusieurs échecs de connexion apparaissent ;
2. une connexion réussie se produit ensuite ;
3. un nouveau facteur d'authentification ou une permission est modifié ;
4. des documents sont téléchargés en volume ;
5. le compte tente ensuite une action administrative inhabituelle.

Cette succession mérite une vérification urgente, sans qu'il soit nécessaire de déclarer immédiatement toutes les hypothèses comme confirmées.

La corrélation permet de mieux comprendre l'enchaînement, à condition que les journaux soient disponibles et suffisamment fiables.

### 14.4. Quand faut-il signaler un événement ?

Dans un environnement professionnel, il faut suivre la procédure prévue par l'organisation. Si un incident sérieux est suspecté, il vaut mieux signaler les faits rapidement plutôt que mener seul des expériences risquées.

Il est utile de communiquer :

- ce qui a été observé ;
- l'heure approximative et le système concerné ;
- les actions déjà réalisées ;
- les messages ou erreurs visibles ;
- les éléments qui restent incertains.

Il ne faut pas envoyer de mots de passe, de jetons d'accès ou de données sensibles dans un message ordinaire pour « prouver » un incident.

## 15. Que faire lorsqu'une menace devient un incident ?

### 15.1. Garder son calme et éviter les manipulations inutiles

Lorsqu'un incident est suspecté, les premières actions peuvent influencer la qualité de l'analyse et l'ampleur des conséquences.

Il faut appliquer la procédure de l'organisation et contacter les personnes responsables. Un employé ne doit pas improviser une investigation intrusive ou tenter de réparer seul un système critique.

Selon le contexte, il peut être nécessaire de limiter la connectivité d'un appareil, de révoquer certains accès ou de suspendre une opération. Ces actions doivent être coordonnées pour éviter d'aggraver la situation.

### 15.2. Préserver les informations utiles

Les journaux, messages suspects, heures d'apparition et observations des utilisateurs peuvent être utiles pour comprendre ce qui s'est passé.

Il faut éviter de supprimer les fichiers ou les traces de manière impulsive. La priorité consiste à préserver les éléments nécessaires selon les consignes de l'équipe responsable.

Les preuves ne doivent pas être modifiées inutilement. Dans certains environnements, une procédure de collecte documentée est nécessaire.

### 15.3. Limiter la propagation

**Schéma pédagogique — Conserver les preuves tout en réduisant le rayon d'impact.**

~~~text
[Detecter]
    |
    v
[Confirmer les faits et conserver les journaux]
    |
    v
[Isoler le compte / poste / segment concerne]
    |
    v
[Revoquer acces et jetons si necessaire]
    |
    v
[Eradiquer la cause] --> [Restaurer] --> [Surveiller]

Choisir un confinement proportionne et coordonne.
~~~


Si un appareil semble compromis, il peut être nécessaire de le déconnecter du réseau selon la procédure d'incident. L'objectif est de réduire la possibilité que l'événement affecte d'autres systèmes.

La déconnexion ne doit pas être présentée comme une solution universelle : selon le contexte, l'équipe d'investigation peut avoir des besoins particuliers de collecte. Il faut suivre les consignes du service responsable.

Un employé ne doit pas brancher l'appareil suspect à d'autres équipements pour essayer de comparer le comportement.

### 15.4. Protéger les comptes

Si des identifiants ont été saisis sur une page frauduleuse, l'équipe peut devoir réinitialiser les secrets concernés, révoquer les sessions, examiner les connexions et vérifier les paramètres de récupération du compte.

Ces opérations doivent être réalisées depuis un environnement de confiance, selon les règles applicables.

Changer simplement le mot de passe sans examiner les sessions actives, les règles de transfert de messagerie ou les accès supplémentaires peut laisser persister certains risques.

### 15.5. Restaurer et vérifier

Après avoir traité la cause et limité l'incident, il peut être nécessaire de restaurer un service ou des données.

Avant la remise en production, il faut vérifier que les éléments utilisés pour la restauration sont sains, corriger les faiblesses identifiées et confirmer le fonctionnement du service.

Il faut également conserver une trace des décisions importantes, communiquer aux personnes responsables et planifier des actions pour éviter la répétition de l'incident.

## 16. Une méthode simple pour prioriser les risques

### 16.1. Pourquoi ne peut-on pas tout traiter en même temps ?

Une organisation dispose d'un temps, d'un budget et de ressources limités. Elle doit donc choisir les actions qui réduisent les risques les plus importants.

Le risque dépend notamment de la vraisemblance d'un événement et de l'ampleur de ses conséquences. Il faut également considérer l'exposition, les protections existantes et les contraintes métier.

Une faiblesse très grave sur un système non exposé n'a pas nécessairement la même priorité qu'une faiblesse exploitable sur un service public critique. Le contexte est essentiel.

### 16.2. Exemple de matrice élémentaire

On peut utiliser une échelle simplifiée :

- vraisemblance : faible, moyenne ou élevée ;
- impact : faible, moyen ou élevé.

Une situation vraisemblable avec des conséquences élevées mérite généralement une attention importante. Une situation peu vraisemblable mais aux conséquences catastrophiques peut elle aussi justifier des protections.

Cette matrice est un outil d'aide à la décision. Elle ne remplace pas une analyse professionnelle ni les exigences spécifiques d'une organisation.

### 16.3. Exemple : trois risques

Une petite école examine les risques suivants.

**Risque A : compte administratif partagé.** Plusieurs personnes peuvent modifier des données et l'organisation ne sait pas toujours qui a réalisé une action.

**Risque B : ordinateur d'accueil parfois lent.** Le problème affecte la productivité, mais l'ordinateur ne semble pas traiter de données particulièrement sensibles.

**Risque C : sauvegardes jamais restaurées en test.** L'école ne sait pas si elle pourra récupérer ses dossiers après un incident majeur.

L'école pourrait donner une priorité élevée au compte partagé et à la vérification des sauvegardes, car les conséquences possibles sont importantes. Le problème de performance doit aussi être étudié, mais son ordre de priorité dépendra des conséquences sur l'activité.

### 16.4. Les mesures préventives, détectives et correctives

Les mesures de sécurité peuvent être regroupées selon leur rôle.

**Préventives :** cherchent à empêcher un événement ou à réduire sa probabilité. Exemples : contrôle d'accès, mises à jour, segmentation et authentification renforcée.

**Détectives :** aident à repérer un événement. Exemples : journaux, supervision, alertes et détection de comportements anormaux.

**Correctives et de récupération :** limitent les conséquences ou permettent de rétablir le service. Exemples : restauration, révocation d'accès, correction d'une configuration et procédure de reprise.

Une organisation doit combiner ces catégories. Empêcher chaque incident n'est pas toujours possible, mais la détection et une bonne récupération peuvent limiter ses conséquences.

## 17. TP guidé : analyser un courriel suspect sans risque

### 17.1. Objectif

Tu vas apprendre à examiner un message suspect sans cliquer sur ses liens, télécharger de pièce jointe ni transmettre d'informations personnelles.

Ce TP utilise un exemple fictif. Il ne demande pas de contacter un site réel ou de tester un service dont tu ne possèdes pas l'autorisation.

### 17.2. Message de démonstration

Considère le message suivant :

```text
Objet : URGENT — Votre compte sera supprimé aujourd'hui

Bonjour,

Notre système a détecté un problème sur votre compte.
Vous devez confirmer vos identifiants dans les 15 minutes
pour éviter la suspension définitive.

Ouvrez le lien ci-dessous pour continuer :
https://compte-verification.invalid/exemple

Si vous ne répondez pas, votre accès sera supprimé.

Service informatique
```

Le domaine `.invalid` est utilisé ici à titre d'exemple fictif. Le message ne doit pas être envoyé à un vrai service.

### 17.3. Étape 1 — Repérer les signaux

Observe les caractéristiques du message :

- urgence très forte ;
- menace de suppression du compte ;
- demande de confirmation des identifiants ;
- lien dont le domaine ne correspond pas à un domaine officiel préalablement connu ;
- formule générique ne précisant pas un contexte vérifiable.

Ces éléments sont suspects. Aucun élément isolé ne prouve à lui seul une fraude, mais leur combinaison justifie de ne pas utiliser le lien.

### 17.4. Étape 2 — Vérifier par un autre canal

Si un message prétend provenir du service informatique de ton établissement, utilise les coordonnées officielles déjà connues ou le portail interne habituel pour vérifier la demande.

Ne réponds pas en envoyant ton mot de passe. Ne cherche pas à prouver la légitimité du message en cliquant sur le lien.

Si le message est reçu sur un compte professionnel, suis la procédure de signalement de l'organisation.

### 17.5. Étape 3 — Examiner l'expéditeur

Le nom affiché dans un courriel peut être trompeur. Il faut, lorsque cela est possible et autorisé, examiner l'adresse réelle de l'expéditeur et le contexte de réception.

Même une adresse qui semble correcte ne constitue pas une preuve absolue : un compte légitime peut avoir été compromis, et certains mécanismes d'affichage peuvent induire en erreur.

Il est préférable de vérifier les demandes sensibles par un canal indépendant.

### 17.6. Étape 4 — Décider de l'action

Dans ce scénario, l'action prudente consiste à ne pas suivre le lien, à signaler le message et à vérifier la situation via le portail officiel.

Si un utilisateur a déjà saisi ses identifiants, il doit le signaler rapidement. L'équipe responsable pourra évaluer la nécessité de réinitialiser le secret, révoquer les sessions et examiner les événements de connexion.

### 17.7. Ce que tu dois retenir

L'objectif n'est pas de reconnaître chaque courriel frauduleux uniquement à son apparence. Les messages malveillants peuvent imiter très correctement une organisation.

La bonne méthode consiste à examiner le contexte, à éviter les actions sensibles sous pression, à vérifier l'identité par un canal indépendant et à signaler les éléments suspects.

## 18. TP guidé : inventorier les signaux simples sur son propre poste

### 18.1. Objectif

Tu vas réaliser une petite vérification non intrusive de ton propre ordinateur. Les commandes affichent des informations de base et ne nécessitent pas de scanner un réseau tiers.

Ces vérifications ne constituent pas un audit de sécurité complet et ne prouvent pas l'absence de menace.

### 18.2. Sous Windows PowerShell

Pour afficher la version du système :

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber
```

Pour afficher les processus en cours :

```powershell
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 ProcessName, Id, CPU
```

Pour afficher les connexions réseau associées aux processus, lorsque les permissions et la version du système le permettent :

```powershell
Get-NetTCPConnection -ErrorAction SilentlyContinue |
    Select-Object -First 20 LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess
```

Pour consulter l'état du service Microsoft Defender lorsque ce service est présent et que les permissions le permettent :

```powershell
Get-Service -Name WinDefend -ErrorAction SilentlyContinue
```

L'affichage de ces informations ne permet pas, à lui seul, de déterminer si un ordinateur est compromis. Certains processus peuvent être inconnus d'un débutant tout en étant légitimes.

### 18.3. Sous Linux

Pour afficher les informations du système :

```bash
uname -a
```

Pour afficher les processus en cours :

```bash
ps aux --sort=-%cpu | head -n 11
```

Pour examiner les sockets réseau et les connexions visibles selon les outils installés :

```bash
ss -tupn
```

Certaines informations peuvent nécessiter des permissions supplémentaires. N'utilise pas une commande administrative sans comprendre son effet.

### 18.4. Méthode d'observation

Pour chaque commande, note :

- les informations qu'elle affiche ;
- les éléments que tu reconnais ;
- les éléments sur lesquels tu dois demander des explications ;
- les changements éventuels par rapport à un état connu.

Ne conclus pas qu'un processus est malveillant uniquement parce que son nom ne t'est pas familier. En cas de doute, consulte la documentation du système ou le service technique compétent.

Si tu soupçonnes un incident réel sur un ordinateur professionnel, ne tente pas de supprimer des processus ou de modifier les paramètres au hasard. Suis la procédure de sécurité de ton organisation.

## 19. Construire une défense de base contre les principales menaces

La protection repose sur plusieurs couches. L'objectif est de réduire la probabilité d'un incident, de limiter ses conséquences et de faciliter sa détection.

### 19.1. Protéger les identités

Chaque utilisateur devrait disposer de droits adaptés à son rôle. Les comptes partagés doivent être évités lorsqu'ils empêchent d'identifier les actions individuelles ou qu'ils accordent des droits excessifs.

Les comptes à privilèges doivent bénéficier d'une protection renforcée. Les comptes inutilisés doivent être examinés et désactivés selon les procédures prévues.

L'authentification multifacteur peut réduire le risque lié au vol d'un mot de passe, en particulier pour les accès sensibles.

### 19.2. Maintenir les systèmes à jour

Les logiciels, systèmes d'exploitation, navigateurs, équipements réseau et applications doivent faire l'objet d'un suivi.

Il faut connaître les versions utilisées, évaluer les correctifs importants et prévoir leur installation. Un inventaire à jour permet également d'identifier les systèmes qui ne reçoivent plus de mises à jour de sécurité.

### 19.3. Réduire la surface d'attaque

La surface d'attaque correspond aux éléments par lesquels un système peut être atteint ou influencé.

Elle inclut notamment les services exposés, les comptes, les interfaces d'administration, les applications et les accès externes.

Il est utile de désactiver les services inutiles, de limiter les connexions à ce qui est nécessaire et de séparer les environnements selon les besoins.

La réduction de la surface d'attaque doit être réalisée avec prudence pour ne pas interrompre les fonctions légitimes.

### 19.4. Protéger les données

Les données sensibles doivent être identifiées, classées et accessibles uniquement aux personnes qui en ont besoin.

Les protections peuvent inclure les permissions, le chiffrement, la limitation des copies locales et la surveillance des accès inhabituels.

Il faut également connaître les obligations applicables à la collecte, à la conservation, au partage et à la suppression des informations.

### 19.5. Préparer les sauvegardes et la reprise

Les sauvegardes doivent être régulières selon les besoins, protégées contre la suppression non autorisée et testées.

Une organisation peut envisager plusieurs copies, des copies isolées ou des mécanismes d'immuabilité adaptés à son environnement. Les choix dépendent de la valeur des données, des objectifs de reprise et des moyens disponibles.

Il faut aussi documenter les étapes de restauration et vérifier que l'application peut réellement fonctionner après la récupération.

### 19.6. Surveiller les événements importants

La journalisation et la supervision aident à repérer les connexions, modifications et comportements inhabituels.

Il faut savoir quels événements sont importants, où les journaux sont stockés, qui peut les consulter et pendant combien de temps ils doivent être conservés.

Les alertes doivent être utiles et exploitables. Un système qui produit trop d'alertes sans hiérarchie peut rendre les signaux importants plus difficiles à identifier.

### 19.7. Sensibiliser et entraîner les équipes

Les utilisateurs doivent savoir reconnaître les demandes suspectes, protéger les informations et signaler un incident.

Les consignes doivent être concrètes : ne pas transmettre un mot de passe par courriel, vérifier les demandes de paiement, signaler les liens suspects et contacter rapidement le support après une erreur.

Des exercices encadrés peuvent aider les équipes à appliquer ces réflexes sans utiliser de véritables secrets ni exposer des données sensibles.

### 19.8. Préparer une procédure d'incident

Avant qu'un incident survienne, l'organisation doit définir les personnes à contacter, les responsabilités et les premières mesures possibles.

La procédure peut prévoir la protection des comptes, l'isolement contrôlé d'un poste, la préservation des journaux, la communication avec les responsables et la restauration des services.

Elle doit être adaptée au système réel et testée. En cas d'incident sérieux, les décisions doivent être prises avec les personnes compétentes et selon les obligations applicables.

## 20. Erreurs de raisonnement à éviter

### 20.1. « Nous sommes trop petits pour être ciblés »

Une organisation de petite taille peut être visée directement ou affectée indirectement par une campagne opportuniste. Les attaquants n'ont pas toujours besoin de connaître précisément leur cible avant d'envoyer des messages frauduleux ou de rechercher des services exposés.

La taille de l'organisation ne remplace pas une analyse de risque.

### 20.2. « Nous avons un antivirus, donc nous sommes protégés »

Un antivirus peut détecter ou bloquer certains logiciels malveillants, mais il ne protège pas contre toutes les menaces.

Le contrôle d'accès, les mises à jour, les sauvegardes, les protections réseau, les procédures et la vigilance des utilisateurs restent nécessaires.

### 20.3. « Le courriel semble professionnel, donc il est légitime »

Un message peut être soigneusement rédigé et utiliser des informations exactes tout en étant malveillant.

La forme du message ne remplace pas la vérification de son origine et de sa demande.

### 20.4. « Une connexion inhabituelle prouve qu'un compte est piraté »

Une connexion inhabituelle constitue un signal à examiner, mais elle peut aussi correspondre à un déplacement, à une intervention ou à une utilisation légitime.

Il faut la corréler avec d'autres éléments et suivre le processus d'investigation.

### 20.5. « La sauvegarde est terminée, donc nous pouvons tout récupérer »

La réussite apparente d'une tâche de sauvegarde ne garantit pas que les données pourront être restaurées et utilisées.

Une restauration testée permet de vérifier la qualité des copies et la faisabilité de la procédure.

### 20.6. « Tous les incidents sont causés par une vulnérabilité logicielle »

Des incidents peuvent provenir de manipulations, de comptes compromis, de mauvaises configurations, de pannes matérielles et d'événements environnementaux.

Il faut chercher la cause dans le contexte réel, sans se limiter aux failles de code.

## 21. Étude de cas : l'incident de l'entreprise Horizon

### 21.1. La situation

Horizon Services est une petite entreprise qui utilise un logiciel de gestion des commandes, une messagerie professionnelle et un serveur de fichiers.

Un employé reçoit un courriel qui prétend provenir du service informatique. Il est invité à confirmer son compte. Il saisit son mot de passe sur la page proposée.

Le lendemain, un autre employé remarque que plusieurs messages ont été envoyés depuis le compte compromis. Une connexion inhabituelle figure dans les journaux. Quelques fichiers ont été téléchargés et un dossier partagé ne contient plus certains documents.

La direction souhaite comprendre la situation et empêcher qu'elle se reproduise.

### 21.2. Étape 1 : séparer les faits des hypothèses

Les faits connus sont les suivants :

- un employé a saisi son mot de passe sur une page reçue par courriel ;
- des messages inhabituels ont été envoyés depuis son compte ;
- une connexion inhabituelle est visible ;
- certains fichiers ne sont plus présents dans le dossier partagé.

Les hypothèses peuvent comprendre le vol du mot de passe, l'utilisation du compte par une personne non autorisée, le téléchargement de documents ou une suppression de fichiers.

Ces hypothèses doivent être vérifiées. Les données disponibles ne suffisent pas encore à établir précisément toutes les actions réalisées.

### 21.3. Étape 2 : déterminer les propriétés concernées

La confidentialité peut être compromise si les courriels ou les fichiers ont été consultés par une personne non autorisée.

L'intégrité peut être compromise si les fichiers ont été supprimés ou modifiés sans autorisation.

La disponibilité peut être affectée si les employés ne peuvent plus accéder aux documents nécessaires.

L'analyse doit déterminer quelles données ont été accessibles, quelles modifications ont eu lieu et quelles fonctions sont encore opérationnelles.

### 21.4. Étape 3 : prendre les premières mesures

L'employé doit signaler immédiatement l'incident. L'équipe compétente examine les accès, révoque les sessions concernées si nécessaire et rétablit un moyen d'authentification fiable.

Elle vérifie également les règles de messagerie, les permissions et les journaux pour rechercher d'éventuelles actions persistantes.

Les fichiers supprimés doivent être récupérés à partir de copies fiables si cela est nécessaire, après avoir évalué l'état du système et conservé les éléments utiles à l'enquête.

### 21.5. Étape 4 : chercher les causes

L'enquête doit rechercher si le compte était protégé par une authentification multifacteur, si d'autres identifiants ont été utilisés, quelles ressources étaient accessibles et si des comptes supplémentaires ont été affectés.

Il faut aussi vérifier si les utilisateurs savent comment signaler un message suspect et si les procédures de révocation des accès sont suffisamment rapides.

### 21.6. Étape 5 : prévenir la répétition

Les actions correctives peuvent comprendre :

- le renforcement de l'authentification ;
- la révocation des sessions et secrets compromis ;
- la vérification des règles de messagerie ;
- la réduction des droits d'accès ;
- l'amélioration de la journalisation ;
- la sensibilisation des employés ;
- des exercices de restauration des fichiers ;
- un processus simple de signalement des courriels suspects.

Chaque action doit être affectée à un responsable et accompagnée d'une vérification.

### 21.7. Leçons de l'étude de cas

L'incident n'a pas nécessairement commencé par une vulnérabilité logicielle. Une manipulation humaine peut créer une opportunité, puis le vol d'identifiants permet d'utiliser un service légitime.

Une défense efficace doit donc combiner les mesures techniques, les procédures et les réflexes des utilisateurs. Elle doit également pouvoir détecter les comportements anormaux et limiter rapidement les conséquences.

## 22. Exercices avec corrections

Essaie de résoudre chaque exercice avant de lire la correction.

### Exercice 1 — Menace, vulnérabilité ou risque ?

Pour chaque élément, indique s'il s'agit principalement d'une menace, d'une vulnérabilité ou d'une conséquence.

A. Une personne cherche à voler des identifiants.

B. Un compte possède des privilèges administratifs inutiles.

C. Des données clients sont divulguées à une personne non autorisée.

D. Une panne électrique pourrait arrêter un serveur.

**Correction**

A. Menace : une personne cherche à provoquer un incident.

B. Vulnérabilité ou faiblesse de configuration : les privilèges sont plus importants que nécessaire.

C. Conséquence : la confidentialité a été compromise.

D. Menace : l'événement pourrait provoquer une interruption.

### Exercice 2 — Reconnaître l'hameçonnage

Un message reçu sur ton adresse professionnelle indique que ton compte sera supprimé dans dix minutes si tu ne transmets pas ton mot de passe.

Quelle est la meilleure première réaction ?

A. Répondre immédiatement pour éviter le blocage.

B. Ouvrir le lien depuis un téléphone personnel.

C. Vérifier la demande par un canal officiel et signaler le message selon la procédure.

D. Transférer le courriel à tous les collègues en leur demandant de tester le lien.

**Correction : C.**

Le sentiment d'urgence et la demande de mot de passe sont des signaux inquiétants. Il faut vérifier la demande indépendamment et éviter de propager le lien.

### Exercice 3 — Identifier un rançongiciel

Une entreprise constate que des fichiers sont devenus inaccessibles et qu'un message exige un paiement pour les récupérer.

Quelle propriété est certainement préoccupée par cette indisponibilité ?

A. Disponibilité.

B. Confidentialité uniquement.

C. Authentification uniquement.

D. Aucune propriété CIA.

**Correction : A.**

La disponibilité est directement affectée. L'intégrité et la confidentialité doivent aussi être étudiées selon les autres actions réalisées et les données éventuellement copiées.

### Exercice 4 — Gestion des vulnérabilités

Un serveur public utilise une version obsolète d'un logiciel pour lequel un correctif de sécurité existe. Quelle démarche est la plus adaptée ?

A. Ignorer le problème si le serveur fonctionne.

B. Évaluer la vulnérabilité, sa gravité et son exposition, planifier une correction et vérifier le résultat.

C. Supprimer tous les journaux pour libérer de l'espace.

D. Partager le compte administrateur avec toute l'équipe.

**Correction : B.**

La gestion des vulnérabilités exige une évaluation, une correction adaptée et une vérification. Le fait que le service fonctionne normalement ne garantit pas qu'il est sécurisé.

### Exercice 5 — Erreur humaine

Un employé supprime un dossier de travail en pensant qu'il s'agissait d'une copie temporaire.

S'agit-il nécessairement d'une attaque ?

**Correction**

Non. Il peut s'agir d'une erreur accidentelle. La conséquence peut tout de même toucher l'intégrité et la disponibilité des données. Il faut comprendre la situation, vérifier les sauvegardes et chercher des moyens d'éviter la répétition de l'erreur.

### Exercice 6 — Réseau et disponibilité

Une application ne répond plus. Le serveur est allumé, mais les utilisateurs ne peuvent pas l'atteindre.

Cite trois éléments à vérifier avant de conclure à une attaque.

**Correction possible**

Il faut examiner la connectivité réseau, l'état du service applicatif et les dépendances telles que le DNS ou la base de données. On peut également vérifier la charge, les journaux et les changements de configuration récents.

Ces vérifications aident à distinguer une panne technique d'un incident malveillant éventuel.

### Exercice 7 — Compte administrateur

Un technicien utilise quotidiennement le même compte administrateur pour consulter ses courriels, naviguer sur Internet et modifier les configurations du réseau.

Quel est le problème principal et quelle mesure proposer ?

**Correction**

L'utilisation permanente d'un compte privilégié augmente les conséquences possibles d'une erreur ou d'une compromission. Une mesure adaptée consiste à séparer les usages quotidiens des opérations d'administration, à limiter les privilèges et à protéger les comptes administratifs.

### Exercice 8 — Prioriser les risques

Une organisation possède les faiblesses suivantes :

- A : un poste d'accueil fonctionne lentement ;
- B : un compte d'administration partagé permet de modifier les données de clients ;
- C : les sauvegardes n'ont jamais été restaurées en test.

Quelle priorité initiale proposes-tu ?

**Correction indicative**

B et C méritent généralement une attention importante : le compte partagé affecte le contrôle des accès et la traçabilité, tandis que les sauvegardes non testées peuvent compromettre la récupération après incident.

A doit également être examiné, mais sa priorité dépend de ses causes et de son impact réel. L'ordre final doit prendre en compte les conséquences métier et les informations disponibles.

### Exercice 9 — Un signal ou une preuve ?

Un antivirus affiche une alerte sur un fichier téléchargé. L'utilisateur affirme qu'il n'a rien exécuté.

Que faut-il conclure ?

**Correction**

L'alerte doit être prise au sérieux et examinée selon la procédure prévue, mais elle ne permet pas à elle seule d'affirmer que le système entier est compromis. Il faut déterminer la nature de l'alerte, l'état du fichier et les actions éventuellement réalisées.

### Exercice 10 — Scénario combiné

Une personne récupère les identifiants d'un employé, télécharge des documents internes et supprime quelques fichiers dans un répertoire partagé.

Quelles propriétés CIA peuvent être affectées ?

**Correction**

La confidentialité peut être touchée par le téléchargement non autorisé. L'intégrité peut être compromise par la suppression des fichiers. La disponibilité peut également être affectée si les fichiers supprimés sont nécessaires à l'activité.

Il faut enquêter pour confirmer l'étendue des actions et les systèmes concernés.

## 23. Défi final — Construire un plan de réduction des menaces

### 23.1. Le scénario

Tu viens d'être recruté comme technicien débutant chez **NovaLearn**, une entreprise qui propose des formations en ligne.

L'entreprise dispose d'une application Web, d'une base de données d'apprenants, d'une messagerie professionnelle et d'un serveur de fichiers. Les enseignants utilisent des comptes individuels, mais les comptes administratifs sont mal documentés.

Le responsable t'explique les problèmes suivants :

1. Plusieurs employés réutilisent le même mot de passe sur des services différents.
2. Le site contient un logiciel qui n'a pas été mis à jour depuis longtemps.
3. Certains documents sont partagés à l'aide de liens dont les permissions ne sont pas régulièrement revues.
4. Une sauvegarde est effectuée, mais personne ne sait si la restauration fonctionne.
5. Les courriels suspects sont souvent supprimés sans être signalés.
6. L'entreprise ne possède pas de procédure claire pour réagir lorsqu'un compte est compromis.

Le responsable te demande de proposer un premier plan de réduction des risques.

### 23.2. Travail demandé

Rédige une réponse contenant :

- les actifs essentiels à protéger ;
- les menaces plausibles associées à chaque problème ;
- les vulnérabilités ou faiblesses identifiées ;
- les propriétés CIA potentiellement affectées ;
- les mesures préventives prioritaires ;
- les moyens de détecter un incident ;
- les premières actions à prévoir lorsqu'un incident est signalé ;
- les contrôles permettant de vérifier les résultats.

Ne choisis pas un produit commercial au hasard. Décris le contrôle attendu et explique pourquoi il est utile.

### 23.3. Correction détaillée

**1. Les actifs essentiels**

Les principaux actifs sont les données personnelles des apprenants, les résultats, les comptes des utilisateurs, la plateforme de formation, la base de données, les documents internes, les comptes administratifs et les sauvegardes.

La messagerie est aussi importante, car elle peut servir à réinitialiser des comptes ou à diffuser des messages frauduleux.

**2. Les menaces et faiblesses**

La réutilisation des mots de passe crée une faiblesse qui peut faciliter l'accès à plusieurs services si un identifiant est divulgué. Une menace peut tenter d'exploiter cette faiblesse.

Le logiciel obsolète peut contenir des vulnérabilités connues. La menace est qu'une personne ou un programme tente de les exploiter.

Les liens de partage mal contrôlés peuvent donner accès à des documents à des personnes qui n'en ont plus besoin ou qui ne devraient pas les consulter.

Les sauvegardes non testées créent une incertitude concernant la reprise et la récupération des données.

L'absence de signalement des courriels suspects réduit la capacité de l'organisation à détecter des campagnes ou des tentatives de manipulation.

L'absence de procédure d'incident peut retarder la révocation des accès et aggraver les conséquences d'une compromission.

**3. Les propriétés CIA concernées**

La confidentialité est concernée par les permissions de partage trop larges, la compromission de comptes et la consultation non autorisée de données.

L'intégrité peut être affectée si un compte compromis modifie les résultats, les documents ou la configuration de l'application.

La disponibilité peut être affectée par une exploitation de vulnérabilité, un rançongiciel ou une interruption de service. L'absence de restauration testée augmente l'incertitude sur la capacité de reprise.

**4. Les mesures préventives**

L'entreprise devrait adopter des mots de passe uniques et une protection renforcée pour les comptes importants. Elle doit limiter les privilèges et réexaminer les comptes administratifs.

Le logiciel obsolète doit être inventorié, évalué puis mis à jour selon une procédure adaptée, avec des tests et une vérification après correction.

Les permissions des documents doivent être réexaminées et les liens publics supprimés lorsqu'ils ne sont pas nécessaires. Les utilisateurs doivent pouvoir partager des documents selon des règles simples et compréhensibles.

Les sauvegardes doivent être protégées, vérifiées et restaurées régulièrement dans un environnement adapté.

Un mécanisme de signalement simple doit être communiqué aux employés. Les messages suspects doivent être transmis à l'équipe responsable sans propager les liens dangereux.

**5. Les mesures de détection**

Les journaux d'authentification peuvent contribuer à repérer des connexions inhabituelles, des échecs répétés ou des changements de paramètres de compte.

Les journaux applicatifs peuvent aider à identifier des accès anormaux ou des opérations administratives inattendues.

La surveillance des ressources et des services permet de repérer des interruptions ou des comportements anormaux.

Il faut vérifier que les alertes arrivent aux bonnes personnes et que les événements sont examinés dans des délais adaptés.

**6. Les premières actions en cas d'incident**

L'utilisateur signale rapidement les faits et évite les manipulations improvisées. L'équipe responsable évalue le compte ou l'appareil concerné, révoque les sessions et secrets compromis lorsque cela est nécessaire, préserve les journaux et limite la propagation selon la procédure.

Elle détermine si des données ont été consultées, modifiées ou supprimées, puis restaure les services à partir de sources fiables si nécessaire.

Après l'incident, elle documente les causes identifiées et met en œuvre des corrections.

**7. Vérifier les résultats**

Les contrôles d'accès doivent être testés avec des comptes de rôles différents.

La gestion des mises à jour doit confirmer les versions installées et l'application des correctifs prévus.

Les permissions de partage doivent être contrôlées à partir d'une liste de ressources identifiées.

Les sauvegardes doivent faire l'objet d'une restauration testée, avec un résultat documenté.

La procédure d'incident doit être testée au moyen d'un exercice encadré, sans compromettre de vraies données.

### 23.4. Grille d'autoévaluation

Tu peux te donner une note sur 20 :

| Critère | Points |
|---|---:|
| Identification correcte des actifs | 3 |
| Distinction menace, vulnérabilité, risque et conséquence | 4 |
| Analyse de la triade CIA | 4 |
| Choix des mesures préventives et détectives | 4 |
| Capacité de réaction et de reprise | 3 |
| Vérification et justification des mesures | 2 |
| **Total** | **20** |

Une bonne réponse doit expliquer le raisonnement et ne pas seulement accumuler des noms d'outils. Elle doit montrer comment les mesures proposées réduisent un risque précis.

## 24. Synthèse du cours

Le panorama des menaces permet de comprendre les principales façons dont un système informatique peut être compromis ou perturbé.

Les menaces peuvent provenir de cybercriminels, d'acteurs motivés par le renseignement, de manipulations humaines, de personnes internes, d'erreurs techniques ou d'événements environnementaux.

Les principales familles étudiées comprennent :

- l'ingénierie sociale et l'hameçonnage ;
- les logiciels malveillants, dont les rançongiciels ;
- le vol d'identifiants et la compromission de comptes ;
- les vulnérabilités logicielles et les erreurs de configuration ;
- les attaques réseau et les dénis de service ;
- les faiblesses des applications Web et des services Cloud ;
- les risques associés aux prestataires et aux dépendances ;
- les menaces physiques et les erreurs humaines.

Pour analyser une situation, tu dois distinguer la menace, la vulnérabilité, l'événement et ses conséquences. Tu dois également déterminer quelles propriétés de la triade CIA sont concernées.

La protection repose sur plusieurs couches : contrôle d'accès, mises à jour, limitation des privilèges, protection des données, sauvegardes, supervision, journalisation, sensibilisation et procédures de réponse aux incidents.

Aucun outil ne peut empêcher tous les événements. Une démarche professionnelle cherche à réduire la probabilité d'un incident, à détecter les comportements suspects, à limiter la propagation et à récupérer les activités essentielles lorsque cela est nécessaire.

Le raisonnement à retenir est le suivant :

1. Identifier l'actif qui doit être protégé.
2. Décrire la menace plausible.
3. Rechercher les vulnérabilités qui pourraient faciliter l'incident.
4. Déterminer les conséquences et les propriétés CIA concernées.
5. Choisir les mesures de prévention et de détection adaptées.
6. Préparer les actions de réaction et de récupération.
7. Vérifier l'efficacité des protections et réviser les mesures.

La cybersécurité ne consiste pas à avoir peur de chaque événement. Elle consiste à observer les faits, comprendre les risques et prendre des décisions proportionnées.

## 25. Glossaire

**Attaque :** action visant à compromettre un système, une donnée ou un service.

**Cheval de Troie :** programme qui paraît légitime ou utile tout en dissimulant une fonction malveillante.

**Cybercriminel :** acteur qui utilise des moyens numériques pour commettre des actes criminels, notamment à des fins financières.

**Déni de service :** perturbation qui empêche un service de répondre correctement aux demandes légitimes.

**Hameçonnage :** manipulation visant à inciter une personne à révéler des informations ou à réaliser une action dangereuse.

**Ingénierie sociale :** techniques exploitant le comportement humain afin d'obtenir une information, un accès ou une action.

**Intégrité :** propriété qui vise à préserver l'exactitude et l'état autorisé des données et des systèmes.

**Journalisation :** enregistrement des événements utiles pour le suivi, la détection et l'analyse.

**Logiciel malveillant :** programme conçu pour effectuer des actions nuisibles ou non autorisées.

**Menace :** circonstance ou événement susceptible de produire des conséquences négatives sur un système ou une organisation.

**Pare-feu :** mécanisme de sécurité qui applique des règles de contrôle aux communications réseau.

**Rançongiciel :** logiciel ou opération malveillante visant à bloquer l'accès à des systèmes ou à des données, souvent en échange d'une rançon.

**Risque :** possibilité qu'un événement produise des conséquences négatives, généralement évaluée selon sa vraisemblance et son impact.

**Surface d'attaque :** ensemble des points par lesquels un système peut être atteint ou influencé.

**Vulnérabilité :** faiblesse d'un système, d'une configuration ou d'une procédure qui peut être exploitée ou provoquer un incident.

**Authentification multifacteur :** méthode de vérification qui combine plusieurs facteurs distincts.

**Compromission de compte :** situation dans laquelle un tiers non autorisé peut utiliser ou contrôler un compte.

**Segmentation réseau :** séparation d'un réseau en zones dont les communications sont contrôlées.

**Correctif de sécurité :** mise à jour destinée notamment à corriger une faiblesse ou une vulnérabilité.

**Incident de sécurité :** événement qui compromet ou menace les objectifs de sécurité et qui nécessite une évaluation et une réponse adaptées.

## 26. Ressources pour approfondir

Les ressources suivantes proviennent d'organismes spécialisés et peuvent compléter le cours :

- **ANSSI / CERT-FR — Panorama de la cybermenace 2025 :** analyse des menaces et tendances observées, incluant la compromission des environnements Cloud, l'exploitation de vulnérabilités et les activités cybercriminelles.  
  https://www.cert.ssi.gouv.fr/uploads/CERTFR-2026-CTI-002.pdf

- **Cybermalveillance.gouv.fr — Rançongiciels : que faire si votre organisation est victime d'une attaque ?** Conseils de réaction et de protection après un incident.  
  https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/rancongiciels-ransomwares/27f97a8d-cf2a-4bbc-8824-c09a17c2b57b

- **NIST — Glossaire de cybersécurité, notion de menace :** définition et contexte de la notion de menace.  
  https://csrc.nist.gov/glossary/term/threat

- **NIST — Glossaire de cybersécurité, notion de vulnérabilité :** définition et contexte de la notion de vulnérabilité.  
  https://csrc.nist.gov/glossary/term/vulnerability

Utilise ces ressources pour approfondir les concepts, comparer les recommandations et apprendre à identifier les mesures réellement adaptées à un environnement donné.

**Fin du cours : Panorama des menaces.**
