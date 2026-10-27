# Helpdesk : prise en charge et résolution des demandes

> **Mise en contexte**
>
> Tu es technicien de support de premier niveau dans une organisation qui utilise des postes Windows, un réseau local, une messagerie professionnelle, des imprimantes et quelques applications métier. À 8 h 15, une collègue n'arrive plus à ouvrir sa session, un responsable se plaint d'une application très lente et trois personnes signalent qu'elles ne peuvent plus accéder au même partage de fichiers. Un quatrième utilisateur t'écrit simplement : « Internet ne marche pas. »
>
> Ton rôle n'est pas de lancer immédiatement des commandes au hasard, de redémarrer tous les équipements ou de promettre une réparation instantanée. Tu dois comprendre ce que la personne essaie de faire, déterminer l'étendue du problème, sécuriser l'intervention, recueillir des faits, tester des hypothèses simples et réversibles, puis résoudre ou transmettre le dossier avec des éléments utiles.
>
> Ce cours complète la leçon consacrée à la gestion des tickets. Ici, l'objectif est la **prise en charge opérationnelle** : mener un entretien de diagnostic, transformer un symptôme vague en problème vérifiable, effectuer les contrôles de premier niveau, aider un utilisateur à distance sans dépasser les autorisations accordées et vérifier que la solution fonctionne réellement.

## 1. Ce que tu sauras faire

À la fin de ce cours, tu devrais être capable de :

- accueillir une demande sans culpabiliser l'utilisateur et sans annoncer trop tôt une cause ;
- faire préciser le symptôme, le contexte, l'heure de début, la portée et les conséquences du problème ;
- distinguer un incident individuel d'une panne collective, d'une demande d'accès et d'un événement potentiellement lié à la sécurité ;
- conduire un diagnostic structuré en partant des vérifications les moins risquées ;
- utiliser quelques commandes Windows et Linux en sachant ce qu'elles montrent et ce qu'elles ne prouvent pas ;
- reconnaître les situations dans lesquelles il faut s'arrêter et escalader ;
- effectuer une assistance à distance avec consentement, authentification et respect des règles internes ;
- définir un test de validation avec l'utilisateur et laisser des traces techniques compréhensibles ;
- communiquer une résolution, une limitation ou une prochaine étape dans un langage adapté au destinataire.

Le résultat attendu n'est pas que tu connaisses déjà toutes les solutions. Un bon technicien débutant sait surtout **collecter les bonnes observations, raisonner sans improviser et demander de l'aide au bon moment**.

## 2. Le périmètre du helpdesk

### 2.1 Helpdesk, service desk et support de proximité

Le helpdesk est le point d'entrée opérationnel où les utilisateurs cherchent de l'aide pour un incident informatique, un usage qu'ils ne maîtrisent pas ou une difficulté d'accès. Dans certaines organisations, le mot désigne une petite équipe chargée de résoudre rapidement les problèmes fréquents. Un service desk peut couvrir un périmètre plus large : demandes standardisées, coordination avec plusieurs équipes, communication sur les services et suivi de la qualité.

Les appellations varient selon les entreprises. Les responsabilités doivent donc être définies localement : quels logiciels peut-on dépanner, quels changements peut-on appliquer, quels accès peut-on demander, et quelles équipes doivent prendre le relais ?

Le support de premier niveau prend généralement en charge les vérifications reproductibles et les problèmes connus. Il peut vérifier l'alimentation d'un poste, son état réseau, un message d'erreur, une mise à jour visible, une connexion à un service ou l'existence d'une procédure approuvée. Il ne doit pas se donner des droits d'administrateur, modifier une politique de sécurité ou intervenir sur un serveur critique simplement parce qu'une demande semble urgente.

### 2.2 Les niveaux de support

Les niveaux constituent une organisation de compétences, pas un classement de valeur des personnes.

- **Niveau 1 (N1)** : réception et qualification, diagnostic initial, procédures documentées, contrôles non destructifs, résolution des demandes fréquentes et collecte des preuves.
- **Niveau 2 (N2)** : analyses plus approfondies, configurations système ou applicatives, droits administratifs et investigations nécessitant une expertise ou des autorisations spécifiques.
- **Niveau 3 (N3)** : experts produit, ingénieurs réseau ou systèmes, éditeurs, fabricants et équipes qui peuvent analyser le code, l'architecture ou des composants spécialisés.
- **Équipe sécurité** : suspicion de compromission, hameçonnage, perte d'équipement, activité anormale, exposition de données ou demande d'accès suspecte. Ce relais peut être prioritaire quel que soit le niveau technique.

Une escalade n'est pas un échec. Elle devient un problème seulement lorsque le technicien transmet un dossier sans observations, sans résultats et sans explication de ce qui reste à résoudre.

~~~mermaid
flowchart TD
    A["Demande reçue"] --> B["Comprendre le besoin et l'impact"]
    B --> C{"Risque de sécurité ou panne collective ?"}
    C -- Oui --> D["Appliquer la procédure d'alerte"]
    C -- Non --> E["Diagnostic N1 autorisé"]
    E --> F{"Solution connue et vérifiée ?"}
    F -- Oui --> G["Valider avec l'utilisateur"]
    F -- Non --> H["Transmettre avec preuves et tests"]
    D --> I["Suivi avec le responsable compétent"]
    H --> I
    G --> J["Documenter et clôturer"]
~~~

### 2.3 Ce qui relève ou non du support

Une demande d'aide n'autorise pas automatiquement n'importe quelle action. Par exemple :

- expliquer comment utiliser un outil approuvé peut être du support ;
- réinstaller un logiciel peut nécessiter une procédure, une licence et des privilèges ;
- donner un accès à un dossier suppose une validation du responsable des données ;
- réinitialiser un facteur d'authentification demande une vérification d'identité selon le processus officiel ;
- désactiver l'antivirus pour « voir si cela marche » n'est pas une première mesure acceptable ;
- contourner une restriction de sécurité ne constitue pas une résolution.

En cas de doute, pose-toi trois questions : **ai-je l'autorisation ? l'action est-elle réversible ? quel est le risque si je me trompe ?** Si l'une des réponses est incertaine, documente le besoin et demande la validation prévue.

## 3. L'accueil : instaurer une relation de travail efficace

### 3.1 L'utilisateur décrit un effet, pas toujours une cause

« Le réseau est en panne » est souvent l'interprétation de l'utilisateur, pas un diagnostic. Il peut s'agir d'un Wi-Fi déconnecté, d'un seul site inaccessible, d'un problème d'authentification, d'une application indisponible ou d'une panne générale. De la même façon, « mon ordinateur est cassé » peut décrire un écran figé, un périphérique débranché, un ralentissement ou une application qui ne répond plus.

Accueillir correctement ne signifie pas confirmer la cause annoncée. Il faut valider l'expérience vécue, puis préciser les faits.

Exemple d'accueil utile :

> « Bonjour, je vais regarder cela avec vous. Pour commencer, dites-moi ce que vous essayez de faire, ce qui se produit à la place et depuis quand. Nous allons vérifier les éléments un par un. »

Évite les réponses qui ferment la discussion : « Vous avez forcément fait une mauvaise manipulation », « C'est encore le réseau » ou « Redémarrez, ça va marcher ». Elles peuvent être fausses et incitent l'utilisateur à retenir ou minimiser certaines informations.

### 3.2 Poser des questions ouvertes, puis précises

Commence par une question qui laisse l'utilisateur décrire la situation. Ensuite, utilise des questions fermées pour isoler les possibilités.

Questions ouvertes :
- « Peux-tu me montrer ce qui se passe lorsque tu essaies ? »
- « Qu'est-ce qui a changé depuis la dernière fois où cela fonctionnait ? »
- « Quel est le résultat attendu dans ton activité ? »

Questions de précision :
- « Est-ce que le problème se produit à chaque essai ? »
- « Est-ce que tes collègues rencontrent la même chose ? »
- « As-tu un message exact ou un code d'erreur ? »
- « Le problème apparaît-il dans une autre application ou sur un autre réseau approuvé ? »
- « Y a-t-il une échéance immédiate ou un contournement acceptable ? »

Il faut éviter d'enchaîner dix questions sans expliquer pourquoi. Un entretien efficace ressemble à une enquête collaborative : chaque réponse oriente la question suivante.

### 3.3 Les sept informations de départ

Pour une demande technique, cherche généralement à établir les points suivants. Le formulaire ou l'outil de ticketing de l'entreprise peut avoir d'autres champs ; utilise-le sans recopier inutilement toutes les informations.

| Information | Question possible | Pourquoi elle compte |
|---|---|---|
| Identité vérifiée | « Quelle est la référence du compte ou de l'équipement ? » | Associer le problème à la bonne personne et au bon actif |
| Objectif | « Quelle opération essayez-vous de réaliser ? » | Comprendre le besoin métier derrière le symptôme |
| Symptôme | « Que voyez-vous exactement ? » | Séparer les faits des hypothèses |
| Début | « À quel moment cela a-t-il commencé ? » | Corréler avec une mise à jour, une panne ou un changement |
| Portée | « Qui d'autre est concerné ? » | Distinguer une panne individuelle d'une panne collective |
| Reproduction | « Quelles étapes conduisent au problème ? » | Obtenir un test répétable |
| Impact et solution provisoire | « Qu'est-ce qui est bloqué et existe-t-il un contournement ? » | Déterminer la réponse adaptée |

Ne demande pas de mots de passe, de codes à usage unique, de secrets d'API ou de réponses aux questions de récupération. Si le processus demande un identifiant, utilise le mécanisme approuvé et les données strictement nécessaires.

~~~mermaid
flowchart LR
    A["Objectif métier"] --> B["Symptôme observé"]
    B --> C["Date et conditions"]
    C --> D["Périmètre : un poste ou plusieurs"]
    D --> E["Étapes de reproduction"]
    E --> F["Impact et contournement"]
    F --> G["Diagnostic initial"]
~~~

### 3.4 Faire reformuler sans humilier

La reformulation montre que tu as compris et permet de corriger un malentendu avant toute action.

Exemple :

> « Si je résume : depuis ce matin, tu ouvres le navigateur, mais seul le portail interne affiche une erreur. Les autres sites accessibles depuis l'entreprise fonctionnent, et deux collègues ont le même résultat. C'est bien cela ? »

Cette reformulation est utile parce qu'elle contient un moment de début, un comportement, une portée et une confirmation. Elle ne conclut pas encore que le serveur du portail est en panne : elle décrit les faits qui permettront d'étudier cette hypothèse.

## 4. Du symptôme au problème vérifiable

### 4.1 Décrire l'observation

Une description technique utile suit la structure :

**contexte + action effectuée + résultat observé + résultat attendu + fréquence**.

Description faible : « La messagerie ne marche pas. »

Description exploitable : « Sur le poste portable ST-024, l'utilisateur ouvre la messagerie web depuis le réseau du bureau. Après l'authentification, la page reste en chargement et aucune boîte de réception ne s'affiche. Le problème se reproduit à chaque essai depuis 9 h 10. L'accès au portail RH fonctionne. Un collègue du même service obtient le même résultat. »

La seconde formulation ne prouve pas la cause, mais elle permet de choisir les tests. Elle indique que la connexion réseau n'est pas complètement perdue et que la portée dépasse peut-être un seul poste.

### 4.2 Symptôme, cause possible et preuve

Un symptôme est ce que l'on observe. Une cause possible est une explication à tester. Une preuve est une observation qui renforce ou affaiblit cette explication.

| Élément | Exemple |
|---|---|
| Symptôme | Le nom du serveur interne ne s'ouvre pas |
| Hypothèse A | La connexion réseau est coupée |
| Hypothèse B | Le nom ne se résout pas en adresse IP |
| Hypothèse C | Le serveur ne répond plus |
| Test initial | Vérifier les paramètres réseau et interroger la résolution de nom |
| Résultat possible | Une adresse IP est retournée, mais le service reste inaccessible |
| Interprétation | La résolution DNS fonctionne probablement ; il faut examiner la connectivité et le service visé |

Ne transforme pas une corrélation en certitude. Une commande qui échoue peut indiquer une piste, mais elle peut aussi être bloquée par un pare-feu, une politique réseau ou les limites du test.

### 4.3 Tester une hypothèse à la fois

Si tu changes simultanément le DNS, réinitialises le réseau, redémarres le poste et réinstalles l'application, tu ne sauras plus quelle action a eu un effet. Tu peux également créer un second problème.

Procède ainsi :

1. écris mentalement ou dans tes notes l'hypothèse ;
2. choisis un test adapté et suffisamment sûr ;
3. note le résultat exact ;
4. compare ce résultat à ce que tu attendais ;
5. ne change qu'un élément à la fois ;
6. vérifie si le symptôme évolue ;
7. reviens en arrière si un changement contrôlé aggrave la situation et si tu es autorisé à le faire.

~~~mermaid
flowchart TD
    A["Symptôme confirmé"] --> B["Formuler une hypothèse"]
    B --> C["Choisir un test sûr"]
    C --> D["Noter le résultat réel"]
    D --> E{"Résultat conforme à l'hypothèse ?"}
    E -- Oui --> F["Préciser la cause probable"]
    E -- Non --> G["Écarter ou réviser l'hypothèse"]
    F --> H["Appliquer une correction autorisée"]
    G --> B
    H --> I["Tester le résultat attendu"]
~~~

### 4.4 Réduire le périmètre avant de creuser

Une bonne question de diagnostic est : « Quel est le plus petit élément commun aux situations où le problème apparaît ? »

Imagine trois cas :
- la messagerie échoue uniquement sur un ordinateur ;
- la messagerie échoue sur tous les ordinateurs du même bureau ;
- la messagerie échoue pour tous les utilisateurs de l'entreprise.

Ces portées suggèrent des zones de recherche différentes. Dans le premier cas, le poste, son profil ou sa session sont des pistes. Dans le deuxième, le réseau local ou un équipement partagé peut être pertinent. Dans le troisième, un service central ou une modification globale devient plus plausible. Cela ne constitue pas une preuve : c'est une manière d'organiser l'enquête.

Le diagnostic doit aussi protéger la disponibilité. Si plusieurs personnes sont bloquées, n'attends pas une longue analyse individuelle avant de signaler l'incident collectif à l'équipe compétente.

## 5. Une méthode pratique de dépannage N1

### 5.1 L'ordre des vérifications

Commence par les vérifications les plus simples, les moins intrusives et les plus réversibles. L'ordre exact dépend du contexte et des procédures internes, mais le canevas suivant est utile :

1. **Confirmer** : quel besoin est bloqué, depuis quand et pour qui ?
2. **Observer** : message, voyant, état de connexion, heure, comportement.
3. **Comparer** : un autre service, un autre utilisateur autorisé ou un autre poste comparable rencontre-t-il le même problème ?
4. **Vérifier les basiques** : alimentation, câble, Wi-Fi, espace disponible, état de l'application, session et mises à jour visibles.
5. **Consulter les sources autorisées** : état du service, annonces internes, base de connaissances et incidents connus.
6. **Tester** : exécuter un contrôle ciblé et noter sa sortie.
7. **Corriger** : appliquer une seule action approuvée, de préférence réversible.
8. **Valider** : demander à l'utilisateur de refaire le scénario initial.
9. **Documenter** : résultat, contournement, limitation et suite prévue.

Un redémarrage peut parfois résoudre un blocage, mais il peut aussi faire perdre un travail non enregistré, interrompre un traitement ou effacer des éléments temporaires utiles au diagnostic. Demande d'abord si les documents sont enregistrés, préviens de l'impact et applique les règles de l'organisation.

### 5.2 Distinguer observation et action

Une observation lit l'état du système ; une action le modifie. Les commandes de lecture sont souvent plus adaptées au diagnostic de premier niveau, même si leurs résultats peuvent contenir des données sensibles.

Exemples d'observation :
- afficher l'adresse IP et la passerelle ;
- vérifier l'heure et la version du système ;
- lire le message d'erreur exact ;
- tester la résolution d'un nom autorisé ;
- consulter un journal avec les droits prévus ;
- regarder le statut d'un service dans le tableau de bord officiel.

Exemples d'action modificatrice :
- renouveler une adresse DHCP ;
- vider un cache DNS ;
- désactiver puis réactiver une interface ;
- supprimer un profil utilisateur ;
- installer un pilote ;
- réinitialiser un client VPN.

La seconde catégorie exige davantage de précautions, car elle peut déconnecter l'utilisateur, supprimer des paramètres ou aggraver une panne. N'exécute pas une action simplement parce qu'elle apparaît dans un forum.

### 5.3 Le test de référence

Avant une correction, définis comment tu vas reconnaître une amélioration. Par exemple, si le problème est l'accès au partage documentaire, le test n'est pas uniquement « le réseau répond ». Le test réel consiste à ouvrir le partage autorisé et à lire le fichier de test prévu ou un document que l'utilisateur est habilité à consulter.

Un bon test de référence comprend :
- l'action exacte ;
- le résultat attendu ;
- le résultat observé avant l'intervention ;
- le résultat observé après l'intervention ;
- les conditions identiques qui permettent la comparaison.

Si tu ne définis pas le succès à l'avance, tu peux confondre disparition d'un message et résolution du besoin.

## 6. Premiers contrôles réseau sous Windows

Les commandes ci-dessous sont destinées à l'apprentissage sur un poste de test ou à une intervention autorisée. Respecte la politique de l'entreprise. Certaines sorties exposent le nom de machine, les adresses locales, les DNS ou d'autres informations internes : ne les publie pas dans un espace public.

### 6.1 Vérifier la configuration IP

Ouvre l'invite de commandes ou PowerShell et lance :

~~~powershell
ipconfig
~~~

Cette commande affiche les principales informations IP des interfaces actives. Repère l'adresse IPv4, le masque et la passerelle par défaut correspondant à la bonne interface. Une adresse automatique de la plage 169.254.0.0/16 indique généralement qu'une configuration IPv4 n'a pas été obtenue par DHCP, mais elle ne suffit pas à identifier la cause. Le service DHCP peut être indisponible, le Wi-Fi peut être associé au mauvais réseau, le câble peut être déconnecté ou une configuration peut être particulière.

Pour afficher davantage de détails :

~~~powershell
ipconfig /all
~~~

Cette variante est utile pour examiner l'état DHCP, les serveurs DNS et les informations des interfaces. Elle génère plus d'informations ; n'envoie pas la sortie complète à une personne non autorisée et masque les éléments internes lorsqu'un partage est nécessaire.

**Ne lance pas systématiquement** les options de libération ou de renouvellement de bail. Elles modifient la configuration réseau en cours et peuvent interrompre la session distante. Si le poste dépend d'une adresse fixe ou d'une procédure spécifique, une commande de renouvellement non adaptée peut compliquer l'intervention.

### 6.2 Vérifier la connectivité

La commande suivante teste la réponse IP d'une destination :

~~~powershell
ping 192.0.2.1
~~~

L'adresse 192.0.2.1 est ici une adresse réservée à la documentation ; remplace-la uniquement par une adresse de test fournie par l'organisation ou par une passerelle locale identifiée. Ne teste pas au hasard des systèmes externes ou sensibles.

Un résultat positif montre qu'une réponse ICMP est revenue de la destination testée. Il ne prouve pas que l'application métier fonctionne. Un résultat négatif ne prouve pas à lui seul que le réseau est coupé : la cible peut ignorer ICMP ou un pare-feu peut bloquer cette réponse.

Tu peux aussi tester la passerelle réellement affichée par le poste, si la politique l'autorise. Si le poste ne peut pas joindre la passerelle, concentre-toi sur l'interface, le Wi-Fi ou le segment local avant de supposer qu'un serveur externe est responsable.

### 6.3 Vérifier la résolution DNS

Quand une application accepte un nom de domaine mais échoue, il peut être utile de séparer la résolution du nom de l'accès au service.

~~~powershell
nslookup intranet.exemple.invalid
~~~

Le nom indiqué est fictif. Remplace-le par un nom interne autorisé et documenté. Le résultat montre la réponse DNS reçue et le serveur interrogé. Si aucune réponse n'est obtenue, vérifie le contexte et les serveurs DNS configurés ; ne change pas arbitrairement le DNS d'un poste d'entreprise pour utiliser un résolveur public. Cela peut contourner des règles internes, casser l'accès aux noms privés ou violer la politique de sécurité.

Pour lire l'adresse et la configuration des interfaces, commence par les commandes de lecture. Les options de modification ne doivent être appliquées qu'après avoir vérifié que l'action est indiquée par une procédure.

### 6.4 Lire un diagnostic dans le bon ordre

Exemple : l'utilisateur dit que « tout Internet » est en panne. Tu observes que le Wi-Fi est connecté.

1. Vérifie l'adresse IPv4, la passerelle et le DNS.
2. Teste la passerelle locale avec la méthode approuvée.
3. Consulte la page de statut interne du réseau, si elle existe.
4. Teste un nom de service approuvé avec l'outil DNS.
5. Compare le résultat avec un autre poste autorisé dans le même contexte.
6. Note ce qui fonctionne et ce qui ne fonctionne pas.
7. Escalade si les tests indiquent un problème d'infrastructure ou si le périmètre est collectif.

~~~mermaid
flowchart TD
    A["L'utilisateur ne peut pas accéder à un service"] --> B["Vérifier l'interface et l'adresse IP"]
    B --> C{"Adresse et passerelle plausibles ?"}
    C -- Non --> D["Contrôler lien, Wi-Fi, DHCP et profil réseau"]
    C -- Oui --> E["Tester la connectivité prévue"]
    E --> F{"Connectivité de base présente ?"}
    F -- Non --> G["Comparer avec un poste témoin et alerter si collectif"]
    F -- Oui --> H["Tester la résolution DNS du service"]
    H --> I{"Nom résolu ?"}
    I -- Non --> J["Collecter les paramètres DNS et transmettre"]
    I -- Oui --> K["Vérifier le service, l'accès et les autorisations"]
~~~

### 6.5 Pourquoi un test isolé ne suffit pas

- **Ping réussi** : démontre une réponse IP/ICMP depuis la cible, pas le bon fonctionnement de tous les ports applicatifs.
- **Ping en échec** : peut révéler une absence de chemin ou une politique qui filtre ICMP.
- **Résolution DNS réussie** : montre que le nom a obtenu une réponse DNS, pas que le serveur est sain.
- **Navigateur fonctionnel** : prouve que certaines destinations et certains protocoles fonctionnent, pas nécessairement le VPN, le partage de fichiers ou le serveur de messagerie.
- **Autre poste fonctionnel** : aide à comparer, mais les droits, le réseau, les profils et les versions doivent être suffisamment comparables.

Cette nuance fait la différence entre une suite de commandes et un diagnostic.

## 7. Contrôles Linux très simples

Dans un environnement Linux, les outils disponibles dépendent de la distribution et des droits. Les exemples sont orientés lecture.

Afficher les interfaces et leurs adresses :

~~~bash
ip addr
~~~

Afficher les routes connues par la machine :

~~~bash
ip route
~~~

Consulter la configuration de résolution avec un outil présent sur le système :

~~~bash
resolvectl status
~~~

La commande resolvectl n'est pas disponible partout. Si elle manque, ne cherche pas à installer un paquet ou à changer la configuration sans autorisation : utilise les outils supportés par la distribution ou passe le relais.

Tester la résolution d'un nom autorisé :

~~~bash
getent hosts intranet.exemple.invalid
~~~

Tester un chemin IP, si la politique du réseau l'autorise :

~~~bash
ping -c 4 192.0.2.1
~~~

Sur Linux comme sur Windows, une commande doit répondre à une question de diagnostic. Évite de coller une liste de commandes sans relation avec le symptôme. Ne modifie pas les règles réseau, le fichier de résolution ou les services du système dans un environnement professionnel sans procédure et autorisation explicites.

## 8. Résoudre quelques situations fréquentes

### 8.1 « Mon ordinateur n'a plus Internet »

Commence par demander si le problème concerne tous les services ou seulement une application. Vérifie le Wi-Fi ou le câble, le profil réseau utilisé et la configuration IP. Si l'utilisateur est en déplacement, son accès peut dépendre d'un VPN ou d'un réseau public ; ne suppose pas que les mêmes contrôles sont adaptés à tous les contextes.

Procédure de premier niveau :
1. demander le nom du service qui échoue et le message exact ;
2. vérifier si d'autres services autorisés fonctionnent ;
3. vérifier l'état de connexion et l'adresse IP ;
4. comparer le résultat avec le statut officiel du réseau ;
5. exécuter un test ciblé, par exemple une vérification IP ou DNS ;
6. éviter de désactiver le pare-feu ou l'antivirus ;
7. consigner les résultats et transmettre si le problème paraît collectif.

Si plusieurs personnes sont affectées, signale la portée rapidement. Il ne faut pas traiter séparément chaque utilisateur comme s'il s'agissait de pannes indépendantes.

### 8.2 Un seul site ou une seule application ne répond plus

Si les autres sites fonctionnent, la connexion générale peut être opérationnelle. Demande l'adresse exacte par un canal sûr, l'heure du problème et si un autre utilisateur autorisé observe le même comportement. Vérifie la page de statut officielle ou les annonces de maintenance si elles existent.

Tu peux comparer la résolution du nom et le message applicatif. N'effectue pas de scan du service ni de tests de ports improvisés ; ces actions peuvent être considérées comme non autorisées. Si le nom se résout et que le service refuse l'accès, cela peut venir de l'application, d'une autorisation, d'une session expirée, d'un certificat ou d'une dépendance. Il faut collecter le message précis plutôt que d'en choisir une au hasard.

### 8.3 L'utilisateur ne peut pas se connecter à sa session

Les problèmes d'authentification peuvent provenir d'une saisie incorrecte, d'un clavier dans une autre disposition, d'un compte verrouillé, d'un mot de passe expiré, d'une synchronisation ou d'une panne du fournisseur d'identité. La première vérification consiste à comprendre l'écran et le compte concernés.

Règles :
- confirme l'identité à l'aide du processus approuvé ;
- ne demande jamais le mot de passe de l'utilisateur ;
- ne demande pas qu'il te transmette un code MFA ;
- ne contourne pas la politique de verrouillage ;
- utilise le portail officiel de réinitialisation ou le processus d'identité autorisé ;
- respecte les délais de verrouillage et les procédures de protection des comptes.

Si l'utilisateur dit avoir saisi ses identifiants sur un site suspect, reçu une demande MFA inattendue ou communiqué un code, cela peut être un incident de sécurité, pas un simple oubli de mot de passe. Il faut suivre sans délai la procédure de sécurité interne.

### 8.4 Le VPN refuse de se connecter

Avant de modifier le client, pose les questions suivantes : l'utilisateur est-il sur le réseau adapté ? l'accès fonctionne-t-il sans VPN quand le service doit être public ? quel message apparaît ? le certificat ou le facteur d'authentification a-t-il changé ? le problème est-il apparu après une mise à jour ou un changement d'appareil ?

Pour un premier niveau, tu peux vérifier le statut du client, sa version affichée, l'heure système, l'état du réseau et les instructions de connexion officielles. Ne copie pas de fichiers de configuration sensibles dans un ticket non protégé. N'installe pas un autre client VPN pour contourner une restriction. Les erreurs de certificat, d'authentification ou de stratégie doivent être transmises à l'équipe VPN avec leur message exact et le contexte utile.

### 8.5 L'imprimante n'imprime pas

Détermine d'abord si une seule personne est touchée ou si plusieurs personnes sont affectées par la même imprimante. Demande si les travaux restent en attente, si l'impression part vers le bon appareil et si un message apparaît sur l'imprimante.

Vérifications de premier niveau :
- confirmer le nom exact de l'imprimante sélectionnée ;
- vérifier l'état visible de l'appareil et les consommables selon les responsabilités locales ;
- vérifier les connexions physiques uniquement si elles sont accessibles sans danger ;
- imprimer une page de test selon la procédure approuvée ;
- comparer avec un poste autorisé qui utilise la même imprimante ;
- relever l'heure, le nom de file et le code d'erreur ;
- éviter de supprimer massivement la file d'impression sans avertir les utilisateurs, car cela peut faire perdre des documents en attente.

Si le voyant indique un bourrage, ne force pas les pièces mécaniques ; applique les instructions du fabricant ou contacte la personne compétente.

### 8.6 Une application est lente ou se ferme

Demande ce qui est lent précisément : le démarrage, l'ouverture d'un document, la recherche, la connexion ou toutes les fonctions. Le mot « lent » peut désigner un délai réseau, un manque de ressources locales, une dépendance distante ou une charge serveur.

Si les règles le permettent, vérifie les ressources visibles du poste, l'espace libre, les autres applications ouvertes, l'heure de l'erreur et les mises à jour récentes. Si l'application se ferme, note le message et l'action qui la déclenche. Les journaux du système peuvent aider, mais leur lecture doit suivre les procédures et les droits prévus.

Ne supprime pas le profil de l'utilisateur et ne réinstalle pas l'application comme premier réflexe : ces actions peuvent effacer des paramètres ou des données locales. Cherche d'abord une procédure documentée et un test qui différencie les causes possibles.

### 8.7 Le poste est très lent

Vérifie si la lenteur est récente, constante, liée à une application ou limitée à certaines heures. Cherche les signes d'une cause collective, comme une application centrale en difficulté ou un réseau saturé. Le redémarrage peut être utile dans certains cas, mais ne doit pas remplacer la collecte du contexte.

Les indicateurs simples — utilisation CPU et mémoire, espace disque disponible, processus visiblement bloqués — peuvent orienter le diagnostic sans prouver la cause. Ne tue pas un processus que tu ne connais pas et ne désactive pas des services système au hasard. Si le poste présente un message suspect, des fenêtres inhabituelles ou un comportement indiquant une compromission, applique la procédure sécurité plutôt que de continuer les optimisations.

### 8.8 Un partage de fichiers est inaccessible

Distingue trois questions : le poste peut-il atteindre le service ? l'utilisateur est-il authentifié ? le compte a-t-il les droits nécessaires sur le partage et sur le fichier ? Une erreur d'accès refusé ne signifie pas nécessairement que le réseau est en panne.

N'ajoute pas l'utilisateur à un groupe privilégié pour tester. Vérifie le nom du partage, l'identité professionnelle attendue, l'existence d'une annonce de maintenance et le message exact. Si une autorisation manque, demande la validation prévue au propriétaire des données ou au responsable du service.

### 8.9 Caméra, micro ou périphérique audio

Vérifie le périphérique sélectionné dans l'application, les paramètres de confidentialité, la connexion matérielle et la possibilité de tester dans un outil autorisé. Un appareil peut fonctionner dans le système et être désactivé dans une application, ou fonctionner dans une application mais pas dans une autre.

Ne demande pas à l'utilisateur d'installer un utilitaire inconnu. Ne prends pas une photo ou un enregistrement de l'utilisateur sans nécessité et accord. Si le périphérique est partagé ou géré centralement, utilise la procédure de support correspondante.

### 8.10 Plusieurs utilisateurs signalent la même panne

À partir du deuxième signalement similaire, cherche à déterminer s'ils ont un service ou un équipement en commun. Ne commence pas par des corrections individuelles qui masqueraient l'ampleur de l'incident.

Collecte :
- le nombre approximatif de personnes ou de sites affectés ;
- le service et le périmètre géographique ;
- la première heure connue ;
- les changements récents mentionnés ;
- les résultats de vérification déjà effectués ;
- l'existence d'un contournement sûr.

Puis avertis rapidement l'équipe responsable de l'incident collectif selon le processus interne. Priorise le rétablissement du service et la communication coordonnée ; l'analyse exhaustive de la cause peut venir après la stabilisation. Cette distinction est importante : chercher immédiatement une cause parfaite n'est pas toujours la meilleure façon de réduire l'impact.

~~~mermaid
flowchart TD
    A["Signaux similaires provenant de plusieurs personnes"] --> B["Comparer heure, service, zone et symptômes"]
    B --> C{"Même service ou dépendance commune ?"}
    C -- Oui --> D["Signaler un incident collectif"]
    C -- Incertain --> E["Faire valider la portée par l'équipe concernée"]
    C -- Non --> F["Traiter les dossiers séparément"]
    D --> G["Communiquer un point de situation unique"]
    E --> G
    G --> H["Suivre le contournement et le rétablissement"]
~~~

## 9. L'assistance à distance : aider sans prendre de risques

### 9.1 Préparer une session

Une session à distance est une intervention sur un appareil réel. Elle peut révéler des messages, des documents, des données personnelles et des informations confidentielles. Utilise uniquement l'outil approuvé par l'organisation et un canal officiel pour établir la connexion.

Avant de commencer :
1. confirme que la demande a bien été initiée ou validée par le processus interne ;
2. vérifie l'identité de l'utilisateur ;
3. explique le but de la session et les actions envisagées ;
4. demande son accord explicite ;
5. privilégie le partage d'écran en lecture seule si cela suffit ;
6. rappelle à l'utilisateur de fermer ou masquer les fenêtres confidentielles non nécessaires ;
7. vérifie que la session est autorisée pour ce type d'équipement.

Ne te fie pas uniquement au fait qu'une personne dit « je suis le directeur » ou qu'elle connaît un nom interne. Les demandes inhabituelles de prise de contrôle, d'urgence ou de contournement doivent suivre les mêmes vérifications, et parfois des contrôles renforcés.

### 9.2 Consentement et visibilité

Dans un outil tel que Quick Assist, les deux parties suivent un parcours de connexion et l'utilisateur doit accepter le partage de son écran ou le contrôle demandé. Les options exactes dépendent de la version et des politiques de l'environnement. Explique les étapes et laisse l'utilisateur voir ce qui se passe ; ne cherche pas à obtenir un accès caché.

Pendant la session :
- annonce avant de modifier un paramètre ou de fermer une application ;
- demande à l'utilisateur d'enregistrer son travail ;
- évite d'ouvrir des fichiers personnels ;
- ne demande pas la transmission d'un mot de passe ou d'un code de validation ;
- arrête la session lorsque le but est atteint ou si la situation devient suspecte ;
- ferme proprement la session et confirme avec l'utilisateur ce qui a été fait.

L'accès complet n'est pas automatiquement préférable au simple affichage. Réduire le niveau d'accès réduit aussi le risque d'action accidentelle.

~~~mermaid
sequenceDiagram
    participant U as Utilisateur
    participant T as Technicien
    participant O as Outil approuvé
    T->>U: Expliquer le but et les actions prévues
    U->>T: Confirmer la demande et son accord
    T->>O: Créer la session selon la procédure
    O-->>U: Afficher la demande d'autorisation
    U->>O: Accepter le niveau d'accès approprié
    T->>U: Annoncer chaque action de modification
    T->>U: Faire vérifier le résultat
    T->>O: Terminer la session
    O-->>U: Fermer l'accès distant
~~~

### 9.3 Si quelque chose paraît anormal

Arrête-toi si :
- l'utilisateur ne reconnaît pas la demande ;
- un tiers tente de te faire installer un outil non approuvé ;
- on te presse de contourner la vérification d'identité ;
- une demande exige la communication d'un mot de passe ou d'un code MFA ;
- tu observes un outil d'accès distant inattendu ou une activité suspecte ;
- l'intervention demande un accès à des données sans justification ou autorisation.

N'essaie pas de « vérifier discrètement » en continuant l'accès. Mets fin à la session de façon sûre et signale le cas par le canal prévu. Lorsqu'une fraude ou une compromission est possible, la priorité peut être la sécurité du compte ou du poste plutôt que la résolution immédiate de la demande initiale.

### 9.4 Captures d'écran et journaux

Une capture d'écran peut montrer des noms de clients, des messages, des identifiants, des adresses internes ou des données personnelles. Avant d'en faire une, demande-toi si elle est nécessaire et où elle sera conservée. Recadre et masque les informations inutiles. Ne publie jamais des journaux internes dans un forum public en espérant qu'une communauté identifiera la panne.

Une preuve doit être utile et proportionnée : message d'erreur exact, horodatage, nom du service concerné, sortie ciblée d'une commande et résultat du test. La quantité de données ne remplace pas la qualité de la collecte.

## 10. Communiquer tout au long du dépannage

### 10.1 Ne pas promettre ce que tu ne contrôles pas

Évite : « Ce sera réparé dans cinq minutes » si tu n'as ni diagnostic confirmé ni délai fourni par l'équipe responsable.

Préfère :
- « J'ai confirmé que le problème se reproduit. Je vérifie maintenant si cela concerne seulement votre poste ou le service commun. »
- « Le premier contrôle n'a pas permis de confirmer la cause. Je transmets les observations à l'équipe qui gère ce service. »
- « Le contournement approuvé permet de reprendre l'activité ; la cause complète reste en cours d'analyse. »

Cette façon de communiquer reste honnête tout en donnant à l'utilisateur une visibilité sur la suite.

### 10.2 Expliquer sans jargon inutile

Au lieu de dire « le DNS ne résout pas le FQDN », tu peux dire « le poste ne parvient pas à retrouver l'adresse du service à partir de son nom ». Si le destinataire est technicien réseau, tu peux ensuite préciser le nom testé, le serveur DNS interrogé et le résultat.

Le niveau de détail varie selon le destinataire, mais les faits ne doivent pas varier. Un compte rendu utilisateur peut être court ; un dossier transmis à l'équipe technique doit préserver les résultats nécessaires à la poursuite de l'analyse.

### 10.3 Donner un point de situation utile

Un point de situation efficace comprend quatre éléments :
1. ce que l'on a confirmé ;
2. ce que l'on n'a pas encore confirmé ;
3. l'action en cours ou la prochaine étape ;
4. le moment ou l'événement qui déclenchera la prochaine communication, selon les règles du service.

N'envoie pas un message qui dit seulement « en cours ». Si aucune nouvelle information n'est disponible, explique au moins que le dossier reste pris en charge et indique la dépendance ou l'équipe qui doit intervenir, sans inventer une échéance.

## 11. Escalader sans perdre l'information

### 11.1 Quand faut-il escalader ?

Escalade quand :
- les tests dépassent ton périmètre d'autorisation ou tes compétences ;
- une action pourrait affecter plusieurs utilisateurs ou un service critique ;
- un accès administrateur ou une modification centrale est nécessaire ;
- le problème persiste après la procédure de premier niveau documentée ;
- tu suspectes un incident de sécurité ;
- les données nécessaires au diagnostic ne sont accessibles qu'à une autre équipe ;
- le risque de rendre la situation pire est supérieur au bénéfice d'une tentative supplémentaire.

Ne continue pas simplement parce que l'utilisateur insiste. Il est possible de maintenir une bonne expérience en transmettant clairement le problème et la prochaine étape.

### 11.2 Construire un dossier de transfert

Un transfert de qualité comprend :
- le besoin métier bloqué et la portée ;
- l'équipement, le service et le contexte exacts ;
- l'heure de début et la dernière heure où tout fonctionnait, si elle est connue ;
- les étapes de reproduction ;
- le message d'erreur exact ;
- les tests effectués et les résultats, y compris ceux qui ont réussi ;
- les changements réalisés et leur résultat ;
- les contournements déjà essayés ou disponibles ;
- le niveau d'impact et la raison de l'escalade ;
- les précautions déjà prises, notamment en matière de sécurité.

N'écris pas « tout essayé ». Une équipe suivante ne peut pas utiliser cette information. Écris plutôt « redémarrage de l'application après sauvegarde du travail : le même message réapparaît ; test depuis un second poste autorisé : même erreur ; statut du service interne : aucun incident annoncé à 10 h 05 ».

~~~mermaid
flowchart LR
    A["N1 : symptômes et contexte"] --> B["Tests réalisés et résultats"]
    B --> C["Actions et changements effectués"]
    C --> D["Impact et risque"]
    D --> E["Hypothèse restante ou question précise"]
    E --> F["Équipe destinataire"]
    F --> G["Confirmation de reprise"]
~~~

### 11.3 Passer la main et rester responsable du suivi

Une escalade ne signifie pas forcément que tu abandonnes le dossier. Selon l'organisation, le technicien qui reçoit la demande doit vérifier qu'une équipe a accepté la prise en charge, informer l'utilisateur du changement de responsable et conserver le suivi jusqu'à la clôture ou le transfert formel.

N'effectue pas des changements supplémentaires en parallèle sans coordination. Deux équipes qui modifient la même configuration sans se parler peuvent annuler leurs actions ou rendre la cause difficile à identifier. Lors d'un incident collectif, utilise le canal de coordination désigné plutôt que des conversations privées contradictoires.

## 12. Tester la résolution avant de conclure

### 12.1 Un redémarrage n'est pas une preuve suffisante

Si le poste redémarre, cela démontre seulement que le redémarrage a abouti. Pour conclure, il faut reproduire le besoin initial. Si l'utilisateur ne pouvait pas ouvrir l'application métier, demande-lui de refaire l'opération et de confirmer que le contenu attendu est accessible.

Le test doit être proche du scénario qui échouait, sans créer de risque supplémentaire. Si un problème intermittent ne se reproduit plus immédiatement, note la durée d'observation et évite d'annoncer une cause certaine sans preuve.

### 12.2 Vérification à trois niveaux

- **Technique** : le service, l'équipement ou la fonction répond selon les contrôles appropriés.
- **Fonctionnel** : l'opération attendue par l'utilisateur réussit.
- **Opérationnel** : la solution ne crée pas de régression évidente et le contournement éventuel est compris.

Par exemple, un utilisateur peut réussir à se connecter au VPN mais ne pas pouvoir accéder à la ressource attendue. L'établissement du tunnel n'est donc pas à lui seul la preuve que le besoin initial est satisfait.

### 12.3 Confirmer avec la personne

Demande à l'utilisateur de réaliser le test. C'est important parce que son compte, ses droits, son profil et son contexte peuvent être différents des tiens. Si tu testes uniquement avec un compte administrateur, tu risques de masquer un problème d'autorisation.

La clôture peut résumer :
- le symptôme initial ;
- la correction appliquée ;
- le test effectué ;
- le résultat confirmé par l'utilisateur ;
- les limites restantes ou la surveillance prévue.

Si la solution est temporaire, nomme-la comme telle et décris la prochaine étape. Ne présente pas un contournement comme une correction définitive.

~~~mermaid
flowchart TD
    A["Appliquer une correction approuvée"] --> B["Refaire le test technique"]
    B --> C{"Test technique réussi ?"}
    C -- Non --> D["Annuler si nécessaire, documenter et escalader"]
    C -- Oui --> E["Faire rejouer le scénario à l'utilisateur"]
    E --> F{"Besoin métier satisfait ?"}
    F -- Non --> G["Reprendre le diagnostic ou transmettre"]
    F -- Oui --> H["Vérifier les limites et communiquer"]
    H --> I["Documenter la résolution"]
~~~

## 13. Les bonnes habitudes d'un technicien fiable

### 13.1 Maintenir une chronologie

Note les heures importantes : début du problème, test, modification, résultat et rétablissement. Sans chronologie, il est difficile de comparer les observations avec une panne de service, une maintenance ou une modification récente.

Une chronologie concise pourrait ressembler à ceci :

| Heure | Événement | Résultat |
|---|---|---|
| 09:10 | Première erreur signalée | Page d'accès refusé |
| 09:16 | Vérification depuis le même poste | Même erreur |
| 09:21 | Vérification du statut officiel | Aucun incident annoncé |
| 09:28 | Test par un second utilisateur autorisé | Même erreur |
| 09:33 | Transmission à l'équipe applicative | Dossier accepté |
| 10:02 | Notification de rétablissement | Test utilisateur réussi |

Ces données sont fictives. Dans un véritable dossier, utilise l'heure et le fuseau adaptés à l'organisation, en évitant les informations personnelles non nécessaires.

### 13.2 Documenter le savoir utile

Après une résolution reproductible, améliore la base de connaissances selon la procédure de l'équipe. Une bonne fiche contient :
- les symptômes auxquels elle s'applique ;
- les prérequis et les autorisations nécessaires ;
- les risques et conditions d'arrêt ;
- les étapes courtes et vérifiables ;
- le résultat attendu de chaque étape ;
- les critères d'escalade ;
- la version ou l'environnement pour lesquels elle est valable ;
- la date de vérification et le propriétaire de la procédure.

Une fiche ne doit pas devenir une recette universelle. Elle doit expliquer dans quelles situations elle est applicable. Une commande qui est sans risque sur un poste de test peut être dangereuse sur un serveur ou un poste distant.

### 13.3 Éviter les pièges cognitifs

**Ancrage** : tu entends « réseau » et tu ne vérifies que le Wi-Fi.

**Confirmation** : tu penses que DNS est en panne et tu interprètes chaque résultat dans ce sens.

**Précipitation** : tu redémarres sans enregistrer le message d'erreur.

**Généralisation** : un collègue a le problème, alors tu affirmes que toute l'entreprise est touchée.

**Fausse résolution** : le message d'erreur disparaît, mais l'action métier reste impossible.

**Transfert incomplet** : tu envoies la demande à une autre équipe sans résultats de test ni portée.

Pour limiter ces biais, écris les faits séparément des hypothèses et demande-toi quel résultat pourrait invalider ton idée de départ. Quand l'enjeu est important, demande une seconde lecture plutôt que de prendre une action risquée sous pression.

## 14. Checklist de prise en charge

Avant d'agir, vérifie les points applicables :

- [ ] La personne et l'équipement sont identifiés avec le mécanisme prévu.
- [ ] Le besoin métier et le symptôme sont reformulés.
- [ ] L'heure de début et les changements récents connus sont consignés.
- [ ] Le périmètre est estimé : personne, équipe, site ou service global.
- [ ] Le message d'erreur exact ou les étapes de reproduction sont disponibles.
- [ ] Les droits nécessaires à l'intervention sont établis.
- [ ] Les risques d'une action et la possibilité de retour arrière ont été évalués.
- [ ] Les contrôles choisis répondent à une hypothèse précise.
- [ ] Chaque test et son résultat sont documentés.
- [ ] Le test final représente bien l'action qui échouait.
- [ ] L'utilisateur a confirmé le rétablissement ou la limitation restante est expliquée.
- [ ] Le transfert comprend les preuves, les actions réalisées et la question à résoudre.

Cette checklist n'a pas vocation à ralentir chaque demande mineure. Elle sert de garde-fou, particulièrement quand le diagnostic devient incertain ou que l'action peut avoir un impact élevé.

## 15. Travaux pratiques guidés

Les scénarios qui suivent sont conçus pour être réalisés sur un environnement de laboratoire, un poste personnel de test ou un environnement professionnel pour lequel tu as une autorisation explicite. N'applique pas des modifications sur un équipement de production uniquement pour reproduire un exercice.

### TP 1 — Transformer une phrase vague en diagnostic exploitable

**Situation :** une personne écrit « je ne peux pas travailler, ça ne fonctionne pas ».

**Travail demandé :**
1. rédige un message d'accueil respectueux ;
2. prépare six questions qui collectent l'objectif, le symptôme, le début, la portée, la reproduction et l'impact ;
3. rédige une reformulation qui distingue les faits et les hypothèses ;
4. indique quelles informations sont indispensables avant une prise en main à distance ;
5. cite deux situations dans lesquelles tu arrêtes le diagnostic pour transmettre.

**Correction indicative :**

Message possible : « Bonjour, je vais vous aider à préciser le problème. Quelle opération essayez-vous de réaliser, que voyez-vous exactement et depuis quand ? Si possible, donnez-moi le message d'erreur sans communiquer de mot de passe ou de code de sécurité. »

Questions pertinentes :
- quelle application ou ressource est concernée ?
- quelle action échoue ?
- que se passe-t-il exactement ?
- à quelle heure le problème a-t-il commencé ?
- d'autres utilisateurs sont-ils concernés ?
- quel est l'impact et existe-t-il un contournement ?
- le résultat se reproduit-il à chaque tentative ?
- y a-t-il eu une modification récente connue ?

On reformule uniquement les éléments confirmés, puis on choisit un premier test à faible risque. Une demande d'authentification douteuse ou une panne collective doit être signalée selon la procédure plutôt que traitée comme une demande isolée.

### TP 2 — Interpréter une configuration réseau

**Situation :** l'utilisateur ne peut pas ouvrir le portail interne. Sur un poste de laboratoire, tu lances la commande de lecture ipconfig et observes une adresse IPv4 qui commence par 169.254, sans passerelle par défaut sur l'interface Wi-Fi.

**Travail demandé :**
1. écris ce que tu sais avec certitude ;
2. propose trois causes possibles ;
3. définis deux vérifications sûres ;
4. cite une action à ne pas réaliser sans vérifier le contexte ;
5. rédige une phrase de compte rendu.

**Correction :**

Faits : l'interface examinée n'affiche pas une configuration IPv4 classique avec passerelle. Une adresse de type 169.254 est souvent associée à une configuration automatique lorsque le bail DHCP n'a pas été obtenu, mais la cause exacte n'est pas prouvée.

Causes possibles : le poste n'est pas associé au bon réseau, le lien est interrompu, le service DHCP ou le relais ne répond pas, ou une configuration particulière est en place.

Vérifications : confirmer le nom du réseau Wi-Fi, vérifier l'état du lien et comparer avec un poste témoin autorisé dans la même zone. Consulter aussi les informations de statut approuvées.

À éviter : exécuter au hasard des commandes de libération ou de renouvellement, modifier le DNS ou redémarrer des équipements partagés. Ces actions peuvent interrompre la connectivité et ne sont pas justifiées tant que le contexte n'est pas connu.

Compte rendu : « Sur l'interface Wi-Fi examinée, la configuration IPv4 observée ne contient pas de passerelle par défaut. L'accès au portail reste impossible. La connexion au réseau et l'obtention de la configuration doivent être vérifiées ; la cause n'est pas encore confirmée. »

### TP 3 — Séparer DNS et connectivité

**Situation :** un nom de service ne s'ouvre pas, mais l'utilisateur accède à un autre site. Tu disposes d'un nom interne fictif autorisé par le laboratoire.

**Travail demandé :**
1. explique pourquoi le navigateur qui fonctionne ne suffit pas à prouver que tout le réseau est sain ;
2. lance une requête DNS sur le nom de laboratoire ;
3. note le serveur DNS interrogé et le résultat ;
4. indique ce qu'une réponse positive prouve et ce qu'elle ne prouve pas ;
5. propose la prochaine vérification sans changer la configuration DNS.

**Correction :**

Un autre site peut utiliser une adresse, un cache, un protocole ou une route différente. La réussite de ce test ne prouve pas l'accès à toutes les ressources internes. Une requête DNS réussie indique que le nom a reçu une réponse ; elle ne confirme pas que le service est disponible ni que le compte a le droit d'y accéder. La prochaine étape consiste à vérifier la portée, le message de l'application et le statut du service. Toute demande d'accès ou modification centrale doit suivre le processus d'autorisation.

### TP 4 — Conduire une assistance à distance sûre

**Situation :** une personne demande de prendre la main sur son poste et propose de t'envoyer son mot de passe par messagerie pour gagner du temps.

**Travail demandé :**
1. explique pourquoi tu refuses le mot de passe ;
2. écris ce que tu dois confirmer avant de commencer ;
3. précise le niveau d'accès minimal utile ;
4. décris comment annoncer tes actions ;
5. explique comment terminer et vérifier la session.

**Correction :**

Le mot de passe et les codes d'authentification sont des secrets qui ne doivent pas être transmis au technicien. L'identité de la personne et la demande doivent être vérifiées par le processus officiel ; l'outil doit être approuvé ; l'accord doit être explicite ; le but et les actions doivent être expliqués. Le partage d'écran simple est préférable au contrôle complet s'il suffit. Le technicien annonce les changements, laisse l'utilisateur contrôler la session lorsque c'est prévu, termine l'accès à distance et vérifie qu'il est fermé avant de documenter le résultat.

### TP 5 — Préparer une escalade

**Situation :** plusieurs personnes ne peuvent plus ouvrir un même service. Tu as vérifié que le problème n'est pas limité à un seul poste. Le portail de statut officiel signale encore une investigation en cours.

**Travail demandé :**
1. écris un résumé à transmettre à l'équipe responsable ;
2. liste les faits et résultats déjà recueillis ;
3. indique les informations qui manquent ;
4. explique comment communiquer aux utilisateurs sans inventer un délai ;
5. propose une phrase de prochaine étape.

**Correction indicative :**

« Plusieurs utilisateurs de l'équipe comptabilité signalent depuis 09 h 10 une impossibilité d'ouvrir le portail de facturation. Le même écran d'erreur a été reproduit sur deux postes autorisés. Les autres services testés restent accessibles. Le portail de statut officiel affiche une investigation en cours à 09 h 35. Aucun changement de configuration n'a été effectué sur les postes. Nous transmettons pour vérification du service applicatif et attendons une confirmation du périmètre ainsi qu'une prochaine mise à jour. »

La communication aux utilisateurs peut dire que le problème est confirmé, que l'équipe responsable enquête et qu'une mise à jour sera transmise selon le canal de suivi. Elle ne doit pas promettre un retour à la normale à une heure qui n'a pas été validée.

## 16. Exercices avec corrections

### Exercice 1 — Symptôme ou hypothèse ?

Une utilisatrice dit : « Le serveur est en panne, car je n'arrive pas à enregistrer mon document. »

**Question :** quels éléments sont des faits et quelle partie est une hypothèse ?

**Correction :** le fait disponible est que l'enregistrement échoue, selon le récit de l'utilisatrice. « Le serveur est en panne » est une hypothèse. Il faut préciser l'application, le document, l'emplacement de sauvegarde, le message d'erreur, le moment et la portée, puis tester le chemin le plus pertinent.

### Exercice 2 — Un collègue peut accéder au service

L'utilisateur A ne peut pas se connecter au portail. L'utilisateur B, dans un autre service, peut y accéder.

**Question :** peut-on conclure que le portail fonctionne parfaitement ?

**Correction :** non. Cela montre que le service est accessible dans au moins un contexte. Des différences de droits, de réseau, de groupe d'utilisateurs ou de fonctionnalité peuvent expliquer le comportement. Il faut comparer les contextes et examiner si d'autres utilisateurs ayant les mêmes droits que A rencontrent le même problème.

### Exercice 3 — Ping sans réponse

Le ping vers un serveur échoue, mais une application web sur ce serveur s'ouvre.

**Question :** que conclus-tu ?

**Correction :** la réponse ICMP ne revient pas, mais l'application testée reste accessible. ICMP peut être filtré ; le ping n'est donc pas une preuve de panne générale. Enregistre les résultats et utilise un test adapté au service, sans contourner le pare-feu.

### Exercice 4 — Fausse résolution

Après un redémarrage, l'application s'ouvre mais les fichiers de l'utilisateur ne sont toujours pas accessibles.

**Question :** la demande est-elle résolue ?

**Correction :** non. Le démarrage de l'application n'est qu'un contrôle technique partiel. L'objectif initial comprend l'accès aux fichiers. Il faut vérifier le chemin, le compte et les autorisations, puis poursuivre le diagnostic ou escalader selon le périmètre.

### Exercice 5 — Demande urgente de réinitialisation

Une personne se présentant comme dirigeante appelle et réclame une réinitialisation immédiate du compte d'un collègue. Elle refuse les vérifications habituelles.

**Question :** que fais-tu ?

**Correction :** tu n'effectues pas la réinitialisation sur cette seule base. Tu suis le mécanisme officiel de validation d'identité et d'autorisation, puis tu signales la tentative de contournement si la procédure l'exige. Le statut ou l'urgence annoncée ne remplace pas les contrôles.

### Exercice 6 — Modifier plusieurs paramètres

Tu changes le DNS, désactives le VPN, redémarres le poste et réinstalles le navigateur en une seule intervention. Le problème disparaît.

**Question :** quel est le défaut méthodologique ?

**Correction :** plusieurs variables ont été modifiées simultanément. Il est impossible de déterminer laquelle a été utile, si un changement était inutile ou si un autre problème a été créé. La démarche devait tester une hypothèse à la fois, en commençant par des observations et en privilégiant les actions autorisées et réversibles.

### Exercice 7 — La bonne escalade

Une application métier renvoie une erreur sur trois postes. Le problème se reproduit, le réseau local fonctionne et le support N1 n'a pas accès aux journaux de l'application.

**Question :** que doit contenir le transfert ?

**Correction :** l'heure de début, les postes ou groupes concernés, les étapes de reproduction, l'erreur exacte, les vérifications réseau effectuées et leurs résultats, les dernières modifications connues, le statut officiel du service et la demande précise adressée à l'équipe applicative. Il faut également noter que les journaux applicatifs sont hors du périmètre N1.

### Exercice 8 — Capturer un écran

Une fenêtre d'erreur s'affiche au-dessus d'un tableau qui contient des informations personnelles. La capture intégrale n'est pas nécessaire.

**Question :** comment conserver une preuve ?

**Correction :** privilégie une description exacte ou une capture recadrée sur le message d'erreur. Masque les données non nécessaires, stocke la preuve dans un espace approuvé et limite son accès. Ne publie pas la capture dans un espace public.

### Exercice 9 — Un contournement utile mais temporaire

Le partage de fichiers central est indisponible. L'équipe responsable confirme un contournement approuvé qui permet de consulter une copie en lecture seule.

**Question :** comment annoncer la situation ?

**Correction :** précise que le contournement est temporaire, indique ce qu'il permet et ses limites, explique comment y accéder en sécurité et dis que le rétablissement définitif reste suivi par l'équipe responsable. Ne prétends pas que la cause est corrigée.

### Exercice 10 — Choisir le prochain test

Les utilisateurs peuvent ouvrir les autres sites. Un seul nom interne ne se résout pas sur deux postes autorisés du même réseau.

**Question :** quel est le prochain test pertinent ?

**Correction :** vérifier le nom exact, la portée, le serveur DNS configuré et les résultats de résolution sur des systèmes comparables autorisés, tout en consultant le statut et les changements connus. Il n'est pas pertinent de réinstaller le navigateur ou de modifier arbitrairement les résolveurs. Si la cause probable se trouve dans un service central, transmettre les preuves à l'équipe DNS ou réseau.

## 17. Défi final — Prendre en charge une matinée de support

### Situation

Tu es technicien N1 dans une entreprise de 80 personnes. À 08 h 40, trois demandes arrivent :

1. **Amina**, au service commercial, ne peut plus se connecter au VPN depuis son domicile. Elle dit que cela fonctionnait hier et fournit le message « authentification refusée ». Elle te propose de t'envoyer un code MFA.
2. **Patrick**, au service comptabilité, ne peut plus accéder au portail de facturation. Deux collègues du même service signalent la même erreur depuis 08 h 32. Le réseau local semble fonctionner ; un autre site interne s'ouvre.
3. **Luc**, au service logistique, affirme que son ordinateur est très lent depuis une semaine. Il peut travailler, mais certaines ouvertures de fichiers prennent plusieurs minutes. Aucun autre utilisateur de son équipe n'a encore signalé ce symptôme.

Tu dois traiter ces demandes sans dépasser le périmètre N1. Les détails du scénario sont fictifs ; l'objectif est d'appliquer une méthode de prise en charge.

### Travail demandé

Pour chaque demande :
1. rédige les questions initiales ;
2. classe le risque et l'impact avec les informations disponibles ;
3. décris les premières vérifications sûres ;
4. indique les actions interdites ou à éviter ;
5. définis le critère de succès ;
6. décide si tu continues en N1, escalades ou alertes immédiatement ;
7. prépare un message à l'utilisateur ;
8. rédige un compte rendu concis avec faits, hypothèses et prochaine étape.

### Correction détaillée

#### Demande A — VPN et authentification

**Faits confirmés :** l'utilisateur affirme que la connexion VPN fonctionnait la veille et renvoie actuellement un message d'authentification refusée. La cause exacte n'est pas connue.

**Questions initiales :** à quelle heure l'échec a-t-il commencé ? le même compte est-il utilisé sur l'appareil professionnel habituel ? le message est-il identique à chaque essai ? y a-t-il une annonce de panne VPN ? une modification récente a-t-elle été communiquée ? l'utilisateur peut-il suivre la procédure officielle sans communiquer de secret ?

**Risque :** la demande comporte un élément de sécurité : l'utilisateur propose de partager son code MFA. Tu refuses et rappelles que le code ne doit pas être transmis. Si elle signale une demande MFA inattendue ou une suspicion d'hameçonnage, tu suis immédiatement la procédure sécurité. L'échec de connexion seul ne prouve pas une attaque.

**Vérifications N1 :** confirmer l'identité selon le processus, vérifier l'état connu du service VPN et les instructions approuvées, relever la version visible du client, l'heure et le texte exact de l'erreur, sans modifier les paramètres de sécurité. Aucun contournement de l'authentification ni installation d'un client alternatif n'est acceptable.

**Critère de succès :** l'utilisateur parvient à établir la connexion par le processus officiel puis accède à la ressource autorisée attendue. Si le VPN se connecte mais que les ressources internes restent inaccessibles, la demande n'est pas encore entièrement résolue.

**Décision :** faire les vérifications simples et autorisées ; escalader à l'équipe VPN ou identité si le refus persiste. Appliquer la procédure de sécurité si une demande d'authentification suspecte est rapportée.

**Message possible :** « Merci pour le message d'erreur. Ne m'envoyez pas votre code MFA : il doit rester confidentiel. Je vais vérifier le statut du service et les éléments de connexion autorisés. Si le refus persiste, je transmettrai les informations utiles à l'équipe responsable. »

#### Demande B — Portail de facturation inaccessible à plusieurs personnes

**Faits confirmés :** plusieurs utilisateurs du même service signalent la même erreur depuis 08 h 32 ; un autre site interne s'ouvre. Cela suggère un périmètre commun possible, sans établir la cause.

**Questions initiales :** quel est le message exact ? tous utilisent-ils la même URL ? l'échec a-t-il commencé au même moment ? quel processus métier est bloqué ? existe-t-il un contournement approuvé ? le statut du portail annonce-t-il une investigation ?

**Risque et impact :** trois personnes d'un même service sont touchées. Le niveau de priorité dépend de l'importance du processus de facturation, de ses échéances et du contournement disponible. La portée collective justifie un signalement rapide à l'équipe responsable même si le support N1 poursuit quelques vérifications non intrusives.

**Vérifications N1 :** collecter l'erreur exacte et les horodatages, vérifier la même ressource sur un second poste déjà signalé, consulter le statut officiel, confirmer que l'on utilise l'URL approuvée et relever les fonctions qui restent accessibles. Ne modifie pas les postes individuellement pour contourner une panne centrale suspectée.

**Critère de succès :** au moins un utilisateur autorisé réussit à réaliser l'opération de facturation prévue, puis l'équipe confirme si les autres utilisateurs sont rétablis. Un simple affichage de la page d'accueil ne prouve pas que le processus métier complet fonctionne.

**Décision :** notifier rapidement l'équipe responsable avec les résultats et coordonner le suivi. Communiquer un point de situation commun selon le canal prévu.

**Message possible :** « Nous avons confirmé que plusieurs utilisateurs rencontrent la même erreur sur le portail. Les autres sites internes testés fonctionnent. Le problème est transmis à l'équipe responsable pour vérifier le service ; je vous communiquerai la prochaine information confirmée. Je ne peux pas encore annoncer de délai de rétablissement. »

**Transfert possible :** « Depuis 08 h 32, trois utilisateurs de la comptabilité ne peuvent pas ouvrir le portail de facturation à l'URL approuvée. Le message est identique sur les postes A et B. Un autre site interne s'ouvre. Aucun changement de configuration n'a été effectué. Merci de vérifier la disponibilité du portail et ses dépendances. L'impact métier porte sur le traitement des factures ; un contournement approuvé est à confirmer. »

#### Demande C — Ralentissement d'un seul poste depuis une semaine

**Faits confirmés :** lenteur rapportée sur un poste, depuis environ une semaine, avec délai d'ouverture de fichiers. Aucun autre signalement n'est connu pour l'équipe.

**Questions initiales :** quels fichiers et où sont-ils stockés ? quels délais sont observés ? le ralentissement se produit-il à certaines heures ? les fichiers locaux sont-ils également lents ? y a-t-il eu une mise à jour, une installation ou un changement récent ? existe-t-il un message précis ?

**Risque et impact :** l'utilisateur peut travailler, mais avec une perte de temps importante. À ce stade, aucune panne collective ou urgence critique n'est confirmée ; la priorité peut être évaluée selon l'activité de logistique et l'effet concret sur les opérations.

**Vérifications N1 :** observer les ressources visibles du poste selon les procédures, vérifier l'espace disque disponible et les messages système applicables, comparer l'ouverture d'un fichier local de test autorisé à celle d'un fichier sur le partage, et déterminer si la lenteur touche une application ou plusieurs. Ne supprime pas les données, ne désactive pas de services et ne tue pas un processus inconnu.

**Critère de succès :** le fichier représentatif s'ouvre dans le délai attendu défini pour l'environnement, et l'utilisateur confirme que le flux de travail est redevenu praticable. Si le problème est intermittent, noter la durée et les conditions de l'observation.

**Décision :** continuer les vérifications N1 réversibles et documentées. Escalader si les observations indiquent un problème de stockage, de matériel, de réseau partagé ou si les contrôles dépassent le périmètre. Ne pas promettre une résolution immédiate.

**Message possible :** « Je vais préciser si le délai vient du poste, de l'application ou de l'emplacement des fichiers. Nous commencerons par des contrôles sans modification, puis nous comparerons le résultat d'un fichier de test. Je vous tiendrai informé de ce que les mesures confirment. »

### Barème indicatif

| Critère | Points |
|---|---:|
| Questions qui séparent faits, contexte et hypothèses | 15 |
| Respect des secrets, vérification d'identité et des autorisations | 20 |
| Choix de tests proportionnés et non destructifs | 20 |
| Reconnaissance d'un impact collectif et escalade adaptée | 15 |
| Critère de validation qui représente le besoin réel | 15 |
| Compte rendu et communication sans promesse injustifiée | 15 |
| **Total** | **100** |

Pour valider le défi, vise au moins 80/100 et aucune erreur critique de sécurité : demander ou accepter un code MFA, contourner une autorisation, désactiver une protection pour faire un test ou modifier plusieurs éléments sans procédure peut invalider la prise en charge même si le symptôme disparaît.

## 18. À retenir

Une prise en charge réussie n'est pas une succession de commandes. C'est une démarche claire : comprendre le besoin, établir les faits, estimer le périmètre, tester une hypothèse à la fois, protéger les accès et les données, puis vérifier le résultat avec l'utilisateur.

Le technicien N1 n'est pas censé tout savoir. Il doit reconnaître la limite entre une vérification sûre et une modification risquée, savoir quand appeler l'équipe compétente et transmettre un dossier qui permet de reprendre le travail sans recommencer à zéro. La qualité de l'accueil, la rigueur des observations et la clarté de la communication font partie intégrante de la compétence technique.

## 19. Références et ressources pour approfondir

- [Microsoft Learn — Utiliser Quick Assist pour aider les utilisateurs](https://learn.microsoft.com/en-us/windows/client-management/client-tools/quick-assist) : principes de connexion, partage d'écran et autorisation de l'utilisateur.
- [Microsoft Support — Résoudre les problèmes de PC à distance](https://support.microsoft.com/fr-fr/windows/apps/solve-pc-problems-remotely-with-remote-assistance) : rappel sur les risques d'escroquerie au support et la nécessité de n'autoriser que les personnes de confiance.
- [Microsoft Learn — ipconfig](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig) : paramètres et informations de configuration IP.
- [Microsoft Learn — ping](https://learn.microsoft.com/en-gb/windows-server/administration/windows-commands/ping) : interprétation des réponses ICMP et limites du test.
- [Microsoft Learn — nslookup](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/nslookup) : outil de diagnostic DNS.
- [Google Site Reliability Engineering — Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/) : formulation d'hypothèses, usage des métriques et journaux, tests contrôlés et consignation des observations.
- [Atlassian — Incident Management Process](https://www.atlassian.com/incident-management/itsm) : qualification, triage, diagnostic, escalade et suivi des incidents.
- [Atlassian — How to Build a Service Desk](https://www.atlassian.com/itsm/service-request-management/how-to-build-a-service-desk) : rôle du point de contact, libre-service, routage et qualité du service.

Les outils, versions, règles de support à distance et autorisations évoluent selon les environnements. En production, privilégie toujours la documentation à jour de ton organisation et les instructions du propriétaire du service.