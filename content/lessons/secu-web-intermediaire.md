# Sécurité Web de base

> **Mise en contexte**
>
> Une application Web n’est pas seulement une page affichée dans un navigateur. C’est un système distribué qui traite des identités, des droits, des données personnelles, des paiements éventuels et des appels à des services tiers. Une faille dans une route API, une règle d’autorisation oubliée ou un paramètre SQL mal traité peut exposer les données de plusieurs utilisateurs, même lorsque l’interface semble correcte. Ce cours construit une méthode pratique pour comprendre ces risques, sécuriser les mécanismes essentiels et vérifier les protections dans un environnement de test autorisé. Il prolonge les notions de sécurité des services réseau par la sécurité applicative.

## Objectifs pédagogiques

À la fin du parcours, vous saurez représenter les flux d’une application Web, identifier ses frontières de confiance, distinguer authentification et autorisation, protéger les sessions, traiter les entrées, limiter les injections, comprendre XSS et CSRF, sécuriser les téléversements et les appels sortants, configurer les en-têtes HTTP utiles, organiser les journaux et construire un plan de tests défensifs. Vous saurez aussi expliquer pourquoi une protection doit être appliquée côté serveur et comment recueillir des preuves qu’elle fonctionne.

Le fil conducteur est une application fictive appelée **Campus**, qui permet à un apprenant de consulter ses cours, de modifier son profil, d’envoyer un devoir et de voir sa progression. Les exemples et tests se réalisent uniquement sur cette application de démonstration, en local ou dans un laboratoire expressément autorisé.

## 1. Comprendre l’application comme un système de sécurité

Une application Web relie plusieurs composants qui ne partagent ni les mêmes responsabilités ni le même niveau de confiance. Le navigateur collecte des actions et affiche les résultats. Le serveur reçoit les requêtes, applique les règles métier, authentifie les utilisateurs et autorise les opérations. La base de données conserve les informations. Des composants externes peuvent fournir l’authentification, le stockage de fichiers, l’envoi de courriels ou les paiements.

~~~text
[Utilisateur]
     |
     | HTTPS : requête, cookie, jeton
     v
[Navigateur] <---- contenu HTML / JSON ---- [Serveur Web / API]
                                              |         |
                                     règles métier    journal
                                              |
                                              v
                                         [Base de données]
                                              |
                                              v
                                      [Stockage de fichiers]
~~~

Une erreur fréquente consiste à penser que le navigateur constitue une frontière de sécurité suffisante. Or l’utilisateur peut modifier une requête, désactiver JavaScript, appeler une route API directement ou réutiliser une requête observée dans ses propres outils. Le navigateur aide à guider l’utilisateur ; il ne remplace jamais les contrôles serveur. Une liste déroulante peut masquer une option interdite, mais l’API doit encore vérifier le droit demandé.

### 1.1 Cartographier les actifs

Avant de chercher les vulnérabilités, recensez ce qui doit être protégé. Dans Campus, les actifs comprennent les comptes, les mots de passe ou leurs empreintes, les sessions, les profils, les devoirs, les résultats de quiz, les jetons de récupération, les journaux, les clés d’API et les sauvegardes. Il faut noter pour chacun la confidentialité, l’intégrité et la disponibilité attendues.

La confidentialité signifie qu’une donnée n’est lisible que par les personnes autorisées. L’intégrité signifie que les données et les décisions ne sont pas modifiées sans autorisation. La disponibilité signifie que le service reste accessible dans des conditions acceptables. Une application peut respecter la confidentialité mais manquer d’intégrité si un apprenant peut modifier les notes d’un autre utilisateur. Elle peut rester intègre mais indisponible si une route de recherche consomme trop de mémoire.

### 1.2 Modéliser les menaces

Une menace est un acteur ou un événement susceptible d’occasionner un dommage. Une vulnérabilité est une faiblesse exploitable. Un risque combine la probabilité, l’impact et le contexte. La modélisation des menaces permet de traiter d’abord les chemins qui relient une entrée contrôlée par l’utilisateur à un actif important.

~~~text
Actif : devoir privé
     ^
     | exposition ou modification
     |
API /devoirs/{id}
     ^
     | paramètre id contrôlable
     |
Utilisateur authentifié
     |
     +-- légitime : demande son propre devoir
     |
     +-- abus possible : demande le devoir d'un autre compte
~~~

Pour chaque flux, posez cinq questions : qui contrôle la donnée d’entrée ? Où la donnée est-elle interprétée ? Quelle identité est établie ? Quelle autorisation doit être vérifiée ? Quelle preuve permettra de détecter un abus ? Cette petite grille évite de se concentrer uniquement sur la forme des requêtes et aide à découvrir les problèmes de conception.

### 1.3 Frontières de confiance

Une frontière de confiance est une limite au-delà de laquelle les hypothèses doivent être revérifiées. Le navigateur vers l’API en constitue une. L’API vers un fournisseur externe en est une autre. Les données qui arrivent d’un import, d’une pièce jointe ou d’un webhook sont également à considérer comme non fiables jusqu’à validation.

~~~text
Zone non fiable                 Zone de traitement contrôlé
+------------------+           +-------------------------------+
| navigateur       | HTTPS     | proxy / serveur applicatif    |
| paramètres       |---------->| validation et authentification|
| corps JSON       |           | autorisation / règles métier  |
+------------------+           +---------------+---------------+
                                                |
                                                | requêtes paramétrées
                                                v
                                      +-----------------------+
                                      | base de données       |
                                      | compte de service     |
                                      | droits limités        |
                                      +-----------------------+
~~~

La confiance ne découle pas du fait qu’une requête provient de l’interface officielle. Une requête portant un cookie valide peut tout de même demander une opération non autorisée. Le serveur doit établir les faits qui comptent : l’identité, l’état de la session, la propriété de la ressource, le rôle actif et les contraintes métier.

## 2. HTTP, cookies, sessions et API

### 2.1 Lire une requête

HTTP transporte une méthode, une cible, des en-têtes et parfois un corps. La méthode indique l’intention générale : GET pour lire, POST pour soumettre ou créer selon le contrat, PUT pour remplacer une ressource, PATCH pour une modification partielle, DELETE pour demander une suppression. Le contrat réel de l’API doit être cohérent avec ces intentions. Un GET ne devrait pas réaliser une action destructive, car les navigateurs, mandataires et mécanismes de prélecture peuvent déclencher des GET sans intervention explicite de l’utilisateur.

~~~text
Requête HTTP simplifiée
POST /api/profil HTTP/1.1
Host: campus.example.test
Content-Type: application/json
Cookie: session=<identifiant-de-session>
Origin: https://campus.example.test

{"displayName":"Amina"}
~~~

Le serveur doit valider la méthode, le type de contenu, la taille du corps et le schéma des données. Un corps JSON ne devient pas sûr parce qu’il est en JSON. Une chaîne contenant une commande, un fragment HTML ou une expression SQL reste une chaîne contrôlée par l’émetteur. La validation doit également porter sur les paramètres du chemin et de la requête.

Les codes HTTP contribuent à un contrat compréhensible. 200 indique un succès général, 201 une création, 204 un succès sans corps, 400 une requête invalide, 401 une authentification requise ou invalide, 403 un refus d’accès, 404 une ressource absente ou volontairement non révélée, 409 un conflit, 413 un contenu trop volumineux, 415 un type non pris en charge, 429 une limitation de débit, et 500 une erreur serveur inattendue. Les codes ne remplacent pas la journalisation, mais les réponses cohérentes facilitent le diagnostic et les tests.

### 2.2 TLS et transport

L’application doit utiliser HTTPS afin de protéger le transport contre l’écoute et la modification en transit. Un certificat valide permet au client de vérifier l’identité du serveur selon la chaîne de confiance et le nom attendu. Ne désactivez jamais la vérification du certificat pour « corriger » un problème de connexion. Il faut plutôt diagnostiquer le nom, la date, la chaîne intermédiaire et la configuration du service.

TLS ne sécurise pas une application vulnérable aux accès non autorisés. Si une API expose toutes les notes à chaque compte authentifié, HTTPS ne fait que chiffrer cette exposition pendant le transport. La protection du transport et le contrôle d’accès sont deux couches complémentaires.

Le serveur doit rediriger le trafic HTTP vers HTTPS lorsqu’un accès HTTP est encore disponible, renouveler les certificats avant expiration et éviter les contenus mixtes. Le navigateur peut conserver la préférence HTTPS via HSTS, en fonction de la stratégie de déploiement. Activez HSTS uniquement lorsque tous les sous-domaines concernés et leur disponibilité HTTPS ont été vérifiés : une configuration imprudente peut rendre un sous-domaine inaccessible dans les navigateurs concernés.

### 2.3 Cookies et sessions

Dans un modèle de session serveur, le navigateur conserve un identifiant opaque ; les données d’identité et les droits restent côté serveur. L’identifiant doit être imprévisible, renouvelé après une connexion ou une élévation de privilèges et invalidé à la déconnexion. Ne placez pas de mot de passe, de rôle décisionnel ou de donnée sensible dans un cookie simplement encodé en Base64.

~~~text
1. Connexion : identifiants -> serveur
2. Serveur : vérifie les identifiants et crée une nouvelle session
3. Serveur -> navigateur : Set-Cookie avec attributs sûrs
4. Navigateur -> API : envoie le cookie automatiquement selon sa portée
5. Serveur : retrouve la session et applique les contrôles d'accès
6. Déconnexion : invalidation serveur et suppression du cookie client
~~~

Les attributs de cookies doivent être choisis explicitement. **Secure** limite l’envoi aux connexions HTTPS. **HttpOnly** empêche l’accès direct au cookie depuis JavaScript, ce qui peut réduire les conséquences de certaines XSS, sans empêcher une XSS de réaliser des actions dans la page. **SameSite** contrôle certains envois intersites et aide à réduire le risque CSRF. **Path** et **Domain** définissent la portée ; une portée trop large augmente l’exposition aux sous-domaines. Un cookie de session est un secret porteur d’accès : il faut le traiter comme tel.

Le drapeau SameSite n’est pas une stratégie CSRF complète à lui seul. Les exigences dépendent du modèle de connexion, des sous-domaines, des parcours externes et des navigateurs pris en charge. Pour les actions sensibles, associez des jetons anti-CSRF ou une vérification robuste de l’origine, selon le cadre applicatif, à des cookies bien configurés.

## 3. Authentification, autorisation et gestion des comptes

### 3.1 Deux questions différentes

L’authentification répond à « qui est cette personne ou ce client ? ». L’autorisation répond à « cette identité peut-elle réaliser cette action sur cette ressource dans cet état ? ». Une authentification réussie ne signifie pas qu’une personne a le droit de lire tous les objets du système.

~~~text
Requête reçue
     |
     v
[Session valide ?] -- non --> 401 / flux de connexion
     |
    oui
     v
[Action permise pour ce rôle ?] -- non --> 403 / refus journalisé
     |
    oui
     v
[Accès à cette ressource précis ?] -- non --> refus contrôlé
     |
    oui
     v
[Validation métier] --> exécution --> audit
~~~

Un rôle de type administrateur, enseignant ou apprenant peut aider à regrouper des permissions, mais il faut également vérifier la portée de l’objet. L’enseignant du cours A ne doit pas forcément modifier les notes du cours B. Un administrateur de contenu ne doit pas automatiquement accéder aux secrets de l’infrastructure. La permission « modifier » doit être distincte de « consulter », « publier », « supprimer » ou « exporter » lorsque le risque le justifie.

### 3.2 Autorisation au niveau de l’objet

Les failles de contrôle d’accès apparaissent lorsque le serveur vérifie l’existence d’une ressource mais pas le droit du demandeur à y accéder. Une route telle que /api/devoirs/481 ne doit pas simplement charger l’enregistrement 481. Elle doit confirmer qu’il appartient au compte demandeur ou qu’une permission explicite accorde l’accès.

~~~text
Compte A, session valide
     |
     | GET /api/devoirs/481
     v
Serveur
     |
     +-- recherche le devoir
     +-- récupère son propriétaire et son contexte
     +-- compare avec le principal authentifié
     +-- vérifie une permission explicite éventuelle
     |
     +-- autorisé : renvoyer uniquement les champs permis
     +-- refusé : réponse contrôlée et événement d'audit
~~~

Ne faites pas confiance à un champ user_id fourni dans le corps de la requête pour décider au nom de qui l’action est effectuée. Le principal doit provenir de la session ou du mécanisme d’authentification vérifié côté serveur. Si un administrateur peut agir au nom d’un utilisateur, l’impersonation doit être une fonction explicite, limitée, autorisée et auditée.

### 3.3 Mot de passe et récupération

Les mots de passe doivent être stockés sous forme d’empreintes adaptées à cet usage, calculées par un algorithme spécialisé de dérivation de mot de passe, avec paramètres et sel appropriés, plutôt que par un simple hachage rapide. Les secrets de connexion ne doivent jamais être écrits dans les logs ou envoyés par courriel. Utilisez les capacités éprouvées du framework ou d’un fournisseur d’identité ; évitez d’inventer votre propre protocole.

La politique de mot de passe doit être cohérente avec une authentification moderne : favoriser des mots de passe longs, bloquer les mots de passe connus comme compromis lorsque cela est possible, limiter les tentatives et éviter les règles de composition arbitraires qui créent des mots de passe prévisibles. Les protections contre la force brute doivent contrôler l’abus sans permettre à un attaquant de verrouiller facilement le compte d’une victime. Un mécanisme de limitation par compte, adresse réseau, appareil et contexte, assorti d’une temporisation progressive et de signaux de risque, peut être plus robuste qu’un blocage simple permanent.

Un lien de récupération doit être à usage unique, avoir une durée de validité courte et être invalidé après utilisation ou après un changement approprié du secret. Le jeton doit être suffisamment aléatoire et stocké de manière à limiter son exposition. La réponse d’une demande de récupération devrait éviter de révéler clairement si une adresse est inscrite au service. Toute modification sensible doit être notifiée par un canal adapté.

### 3.4 MFA et sessions privilégiées

L’authentification multifacteur augmente la résistance à la réutilisation de mots de passe volés. Les facteurs doivent réellement provenir de catégories différentes ; le fait de demander deux secrets connus n’offre pas nécessairement deux facteurs indépendants. Une preuve résistante au phishing est préférable lorsqu’elle est disponible. Pour les opérations administratives, exigez une réauthentification récente ou une confirmation renforcée selon le niveau de risque.

La session représente une autorisation persistante. Définissez des durées d’inactivité et des durées absolues qui correspondent à l’usage. Renouvelez la session après l’authentification, après un changement de privilèges ou après une récupération. Révoquez les sessions lors d’événements sensibles. Dans un système distribué, vérifiez que la révocation est effectivement propagée aux nœuds applicatifs.

## 4. Validation, encodage et injections

### 4.1 Validation côté serveur

La validation décide si une valeur correspond au contrat métier. Utilisez des schémas explicites, des types, des tailles maximales, des ensembles de valeurs autorisées et des contrôles de cohérence. Une adresse électronique doit avoir une forme acceptable, mais cela ne prouve ni sa propriété ni l’identité de la personne. Une date valide peut encore être dans une période métier interdite. Valider la syntaxe ne suffit donc pas : il faut aussi vérifier les règles métier et les permissions.

La validation doit être stricte pour les champs structurés et permissive seulement lorsque l’usage le nécessite. Pour les identifiants, privilégiez un format documenté. Pour un tri ou un ordre de colonne SQL, on ne peut généralement pas remplacer le nom de colonne par un paramètre SQL ordinaire ; utilisez une liste blanche de valeurs choisies par l’application. Pour une valeur numérique, vérifiez aussi les bornes, pas seulement la capacité à la convertir.

~~~text
Entrée contrôlée par le client
        |
        v
[Limites de taille et type attendu]
        |
        v
[Validation du schéma et des valeurs]
        |
        v
[Contrôle d'autorisation sur l'objet]
        |
        v
[Requête paramétrée / encodage de sortie]
        |
        v
[Réponse minimale et audit utile]
~~~

### 4.2 Injection SQL

Une injection SQL survient quand une donnée non fiable est interprétée comme une partie de la commande SQL au lieu de rester une valeur. L’erreur classique est de composer la requête en concaténant du texte avec l’entrée utilisateur. La défense principale consiste à utiliser des requêtes paramétrées ou l’interface sûre d’un ORM, tout en limitant les privilèges du compte de base de données.

Exemple pédagogique à proscrire :

~~~text
SQL assemblé par concaténation :
"SELECT id, title FROM lessons WHERE owner = '" + owner + "'"
Problème : owner est aussi du code SQL potentiel.
~~~

La forme correcte sépare la requête de ses valeurs. Le pseudo-code suivant décrit l’intention ; adaptez la syntaxe à votre pilote de base de données.

~~~text
sql = "SELECT id, title FROM lessons WHERE owner = ?"
execute(sql, [authenticated_user_id])
~~~

N’utilisez pas un identifiant envoyé par le navigateur à la place de l’identité authentifiée dans cet exemple. Les paramètres protègent la séparation entre commande et valeur, mais n’accordent aucun droit d’accès par eux-mêmes. Si le compte SQL peut lire ou modifier toute la base, une erreur applicative conserve un impact important. Attribuez à chaque service les permissions minimales compatibles avec son rôle.

### 4.3 XSS et encodage contextuel

Le cross-site scripting (XSS) apparaît lorsqu’une donnée contrôlée par un utilisateur est interprétée comme du contenu actif par le navigateur. Les variantes courantes incluent la XSS persistante, lorsque le contenu reste stocké, la XSS réfléchie, lorsque l’entrée revient dans une réponse, et la XSS basée sur le DOM, lorsque du JavaScript côté client construit dangereusement le document.

~~~text
Utilisateur soumet un commentaire
          |
          v
Stockage sans traitement sûr
          |
          v
Page d'un autre utilisateur
          |
          v
Navigateur interprète le contenu comme HTML actif
          |
          v
Action réalisée avec le contexte de la victime
~~~

La bonne défense dépend du contexte de sortie. Pour du texte HTML ordinaire, préférez une API qui traite la valeur comme du texte plutôt que comme du balisage. Pour un attribut, une URL, un contenu JavaScript ou CSS, les règles d’encodage diffèrent. Évitez de construire dynamiquement du code exécutable à partir de chaînes. Si une fonctionnalité riche accepte volontairement un sous-ensemble HTML, utilisez une bibliothèque de nettoyage maintenue et une liste de balises et attributs autorisés ; une simple expression régulière n’est pas une stratégie de nettoyage HTML fiable.

Un moteur de template correctement configuré qui échappe automatiquement les valeurs réduit les risques, mais les modes « contenu sûr » ou « ne pas échapper » peuvent neutraliser cette protection. Auditez ces exceptions. Une politique CSP peut limiter les sources de scripts et aider à réduire l’impact de certaines XSS, sans justifier l’acceptation d’une injection.

### 4.4 Prévention des injections au-delà de SQL

Le même principe de séparation entre données et instructions s’applique aux commandes système, aux requêtes LDAP, aux expressions de recherche, aux templates et aux appels à des interpréteurs. La meilleure option consiste souvent à éviter d’appeler un shell, à utiliser une API structurée, à fournir des arguments séparés plutôt qu’une commande recomposée, puis à limiter les droits du processus. N’essayez pas de résoudre le problème par une longue liste de caractères interdits : les encodages et les règles de parsing varient.

Les sorties affichées, les noms de fichiers, les exports CSV et les journaux ont aussi leurs propres contextes. Un contenu rendu en HTML et un contenu ouvert dans un tableur ne partagent pas le même modèle d’interprétation. Les applications doivent documenter les types de données attendus et les chemins d’affichage.

## 5. CSRF, CORS et navigation intersite

### 5.1 CSRF

La falsification de requête intersite (CSRF) exploite notamment le fait qu’un navigateur peut joindre automatiquement des cookies à des requêtes vers un site. Si l’utilisateur est connecté, une page externe pourrait tenter de déclencher une action sans intention explicite. Le risque concerne les actions qui modifient un état, pas seulement les formulaires HTML traditionnels.

~~~text
Victime connectée à Campus
       |
       +---- cookie de session conservé par le navigateur
       |
Visite une page externe malveillante
       |
       +---- tentative de requête vers Campus
                       |
                       v
              Le navigateur peut joindre le cookie
                       |
                       v
          Serveur : jeton CSRF / origine / méthode ?
                       |
                +------+------+
                |             |
              valide        absent ou invalide
                |             |
            action prévue   rejet et journal utile
~~~

Les protections courantes incluent des jetons anti-CSRF imprévisibles liés à la session ou à l’intention, une vérification rigoureuse de l’origine lorsque c’est adapté, des cookies SameSite raisonnablement restrictifs et l’absence d’actions de modification par GET. Les jetons doivent être validés côté serveur ; cacher un bouton ou placer un jeton dans un champ non vérifié n’a aucun effet. Les appels API utilisant un jeton bearer dans un en-tête plutôt qu’un cookie ont un profil différent, mais doivent toujours vérifier l’authentification, les permissions et l’origine selon le modèle retenu.

### 5.2 CORS n’est pas un contrôle d’accès

Cross-Origin Resource Sharing (CORS) est une politique navigateur qui contrôle dans quelles conditions du code exécuté dans une origine peut lire certaines réponses d’une autre origine. Elle ne remplace pas l’authentification ni l’autorisation. Un client qui n’est pas un navigateur n’est pas forcément soumis à la politique CORS. Une API ne doit jamais considérer « CORS bloque cette origine » comme la preuve que les données sont protégées.

~~~text
Site A dans un navigateur -- requête cross-origin --> API B
       |                                             |
       | le navigateur vérifie les en-têtes CORS     |
       |                                             |
       +-- réponse autorisée à être lue ?            |
                                                     |
API B doit toujours vérifier : identité, permission,
validation, limites et règles métier.
~~~

Une configuration CORS doit énumérer les origines nécessaires, les méthodes et les en-têtes acceptés. Évitez les combinaisons incohérentes entre autorisation générique de toutes les origines et envoi de credentials. Les origines sont des triplets schéma, hôte et port ; une correspondance approximative par suffixe peut accorder des droits à des domaines inattendus.

### 5.3 Redirections et liens

Les redirections ouvertes peuvent servir à tromper un utilisateur en faisant passer une URL apparemment légitime pour un relais vers un site externe. Utilisez une destination relative ou une liste explicite de destinations permises, plutôt que de rediriger arbitrairement vers une valeur fournie. Les messages d’erreur et les liens de récupération doivent éviter de révéler des jetons dans des référents transmis à des sites tiers. Les jetons sont des secrets temporaires : limitez leur durée, leur portée, leur usage et leur présence dans les journaux.

## 6. SSRF, fichiers et chemins

### 6.1 SSRF : requêtes serveur non maîtrisées

La falsification de requête côté serveur (SSRF) apparaît quand une fonctionnalité serveur récupère une URL ou effectue une requête réseau à partir d’une valeur contrôlée par l’utilisateur sans contraintes suffisantes. Exemples légitimes : générer une miniature depuis une URL ou vérifier un webhook. Sans garde-fous, la fonctionnalité peut être détournée pour atteindre des ressources internes que le demandeur ne peut pas joindre directement.

La défense consiste à préférer des destinations prédéfinies lorsque possible. Si l’URL libre est indispensable, parsez-la avec une bibliothèque fiable, autorisez explicitement les schémas, hôtes et ports attendus, résolvez le nom de manière sûre, vérifiez les adresses de destination selon la politique et contrôlez les redirections. Bloquez l’accès aux espaces réseau privés, locaux et aux points de métadonnées d’infrastructure lorsque la fonction n’a aucune raison d’y accéder. Appliquez également des règles de sortie réseau : la validation applicative seule est fragile en cas de divergence DNS ou de redirection.

~~~text
URL fournie par l'utilisateur
          |
          v
[Analyse stricte du schéma, nom et port]
          |
          v
[Liste d'hôtes attendus + résolution DNS contrôlée]
          |
          v
[Politique réseau de sortie + délai + taille maximale]
          |
          v
[Redirections réévaluées à chaque étape]
          |
          v
[Réponse limitée et journalisée]
~~~

Désactivez les protocoles inutiles et imposez des délais, une taille maximale de réponse et des quotas. Une fonctionnalité d’import distant ne devrait pas suivre automatiquement des redirections vers des destinations non approuvées. Les contrôles doivent être répétés à chaque changement de destination, car la première URL ne garantit pas la cible finale.

### 6.2 Téléversements

Un téléversement sûr exige plusieurs contrôles. Vérifiez la permission d’envoyer le fichier, la taille, les quotas, les formats réellement attendus et les limites de traitement. Ne faites pas confiance au nom de fichier ni au type MIME annoncé par le client. Vérifiez le contenu avec une bibliothèque adaptée, en gardant à l’esprit que la détection par signature n’est pas une preuve absolue de sûreté. Réencodez les images avec une bibliothèque sûre si c’est cohérent avec le besoin métier. Les archives doivent être traitées avec des limites contre les tailles décompressées excessives, les chemins inattendus et les fichiers imbriqués.

Stockez les fichiers en dehors de la racine Web publique si possible, donnez-leur des noms générés par l’application et conservez les métadonnées en séparant l’identifiant interne du nom d’origine. Le téléchargement doit repasser par une vérification d’autorisation. Pour du contenu accessible au public, séparez le domaine de fichiers du domaine applicatif lorsque l’architecture le permet. Le serveur ne doit pas exécuter les fichiers déposés.

~~~text
Téléversement
    |
    +--> autorisation et quotas
    +--> limite de taille et de temps
    +--> validation du contenu attendu
    +--> traitement isolé si nécessaire
    +--> nom interne aléatoire
    +--> stockage hors racine publique
    |
Téléchargement
    |
    +--> session / permission de lecture
    +--> type de contenu déclaré explicitement
    +--> réponse sans interprétation active inutile
    +--> journalisation de l'accès
~~~

### 6.3 Traversée de répertoires

Une traversée de chemins survient quand une valeur externe détermine un chemin de fichier sans confinement fiable. Évitez de faire du nom fourni par le client un chemin système. Associez plutôt un identifiant opaque à un fichier connu. Si un chemin doit être accepté, résolvez-le avec les primitives adaptées, normalisez-le et vérifiez que le chemin final reste à l’intérieur du répertoire de base approuvé, en tenant compte des liens symboliques et de la plateforme. Le contrôle doit porter sur le chemin final effectivement ouvert, pas seulement sur la chaîne initiale.

La prévention inclut aussi des permissions minimales pour le compte du processus, l’accès en lecture seule lorsque possible, la séparation des fichiers temporaires et des fichiers permanents, ainsi que le nettoyage maîtrisé des fichiers temporaires. Les noms de fichier destinés à être affichés doivent être traités comme des données de sortie non fiables.

## 7. API, données métier et abus de logique

### 7.1 Sécuriser une API dès le contrat

Une API expose souvent davantage de détails qu’une interface graphique. Il faut définir pour chaque route les identités admises, les permissions, les champs acceptés, les limites de taille et de débit, les codes d’erreur, les opérations possibles et les champs renvoyés. Un schéma d’entrée explicite aide à rejeter des champs inattendus. Il est souvent dangereux d’accepter un objet complet provenant du client et de le recopier directement dans la base : un champ interne comme role, owner_id, is_paid ou approved pourrait être modifié par un client qui ne devrait pas le contrôler.

~~~text
Client -> POST /api/profile
       {"displayName":"Amina","role":"admin","approved":true}
                          |
                          v
Serveur : liste des champs modifiables par un profil standard
                          |
             +------------+------------+
             |                         |
   displayName accepté         role / approved rejetés
             |                         |
             v                         v
Mise à jour autorisée      événement de sécurité si pertinent
~~~

Construisez la réponse à partir d’une liste de champs de sortie explicitement permise, surtout pour les objets qui contiennent des informations internes. Laisser l’ORM sérialiser l’intégralité d’un enregistrement peut exposer des colonnes ajoutées plus tard par un autre développeur. Le principe du moindre privilège doit être appliqué aux utilisateurs, aux routes et aux propriétés des objets.

### 7.2 BOLA et autorisation par objet

Broken Object Level Authorization (BOLA), souvent rapproché de l’IDOR, désigne un défaut d’autorisation sur une ressource identifiée par une valeur manipulable. Un identifiant aléatoire réduit parfois l’énumération, mais ne remplace pas le contrôle de propriété. Même un UUID doit être protégé si sa connaissance suffit à lire ou modifier une ressource.

Une bonne conception applique l’autorisation dans le chemin d’exécution qui charge ou modifie l’objet, idéalement au plus près de la requête métier. Les tests doivent comparer plusieurs identités et plusieurs rôles. Ils doivent aussi couvrir les fonctions indirectes : exporter, supprimer, télécharger, partager, commenter ou effectuer une recherche. Une permission appliquée à l’écran de détail mais absente de l’export reste un défaut.

### 7.3 Mass assignment et règles métier

Le mass assignment apparaît quand un objet d’entrée est copié sans filtrage vers un objet interne. Créez des structures d’entrée distinctes des modèles de persistance et autorisez les champs modifiables par fonction. Les opérations sensibles doivent passer par des services métier qui contrôlent les transitions d’état : un devoir ne peut pas être noté avant d’être soumis ; un coupon ne peut pas être utilisé après expiration ; un remboursement ne peut pas dépasser le montant payable.

Des limites de débit ne sont pas uniquement une protection contre les attaques techniques. Elles limitent l’abus de fonctionnalités coûteuses, les exports massifs, l’envoi de courriels et les tentatives répétées. Utilisez des quotas adaptés à l’action et une gestion des erreurs qui évite de révéler trop d’informations.

## 8. En-têtes de sécurité et navigateur

### 8.1 Content Security Policy

La CSP définit les sources à partir desquelles le navigateur peut charger certains types de ressources. Une politique restrictive peut réduire l’impact de certaines XSS et limiter les scripts, images, connexions ou objets non prévus. Il faut commencer par inventorier les ressources nécessaires, tester la stratégie en mode rapport lorsque l’infrastructure le permet, analyser les violations et renforcer progressivement la politique. Une politique qui ajoute des exceptions générales ou autorise n’importe quel script ne remplit pas son objectif.

Exemple de base à adapter et tester, pas à copier aveuglément :

~~~text
Content-Security-Policy:
  default-src 'self';
  object-src 'none';
  base-uri 'self';
  frame-ancestors 'self';
  form-action 'self';
  upgrade-insecure-requests
~~~

Le support des directives et les besoins réels peuvent varier selon l’application. Les scripts en ligne et les bibliothèques externes doivent être traités explicitement, avec des nonces ou des empreintes cryptographiques lorsqu’ils sont adaptés. Évitez d’autoriser largement unsafe-inline sans analyse. Une CSP est une défense en profondeur ; elle ne remplace ni l’encodage de sortie ni la suppression de la cause d’une XSS.

### 8.2 Autres en-têtes utiles

**X-Content-Type-Options: nosniff** réduit les possibilités d’interprétation de contenu selon un type deviné par le navigateur. **Referrer-Policy** permet de limiter les informations d’URL transmises dans l’en-tête Referer. **frame-ancestors** dans la CSP indique quels sites peuvent intégrer la page dans un cadre ; elle aide à réduire le clickjacking. HSTS favorise l’usage de HTTPS pour les visites futures. Les politiques de permissions peuvent restreindre l’utilisation de certaines fonctionnalités du navigateur.

Aucun en-tête ne convient à toutes les applications sans réflexion. Par exemple, interdire tous les cadres peut casser un produit qui nécessite volontairement une intégration partenaire. Il faut documenter l’intention, mettre en place un test automatisé des en-têtes et surveiller les rapports du navigateur. Des en-têtes de sécurité ne corrigent pas un contrôle d’accès manquant côté serveur.

### 8.3 CORS et secrets côté client

Tout secret livré au navigateur doit être considéré comme public pour l’utilisateur qui reçoit la page. Les clés nécessitant une confidentialité doivent rester côté serveur ou être limitées à un usage public avec restrictions appropriées. N’incluez pas de clé privée, de secret fournisseur ou de mot de passe de base dans un paquet JavaScript. Les variables d’environnement d’une compilation frontend peuvent être incorporées dans les fichiers téléchargés ; leur nom « secret » ne les rend pas secrètes.

Les fichiers de source map, messages d’erreur détaillés et endpoints de diagnostic peuvent révéler une structure interne. Ils ne sont pas tous interdits, mais leur exposition doit être intentionnelle. La sécurité ne dépend pas de la dissimulation du code : le serveur doit fonctionner de façon sûre même si l’attaquant connaît les routes et les formats.

## 9. Erreurs, journaux et détection

### 9.1 Réponses d’erreur

Une erreur publique doit aider un client légitime à comprendre quoi corriger sans exposer une trace d’exécution, un chemin système, une requête SQL ou des secrets. Affichez un message stable et un identifiant de corrélation. Conservez les détails techniques dans des journaux d’accès contrôlé, en retirant ou masquant les secrets. Les clients ne devraient pas pouvoir distinguer des états internes sensibles à partir de réponses excessivement détaillées.

~~~text
Erreur interne
    |
    +--> Journal structuré : correlation_id, route, résultat, durée
    |        +--> détails techniques filtrés
    |        +--> pas de mot de passe, cookie, token ou corps secret complet
    |
    +--> Réponse client : code stable + message générique + référence
~~~

### 9.2 Journalisation utile

Journalisez les événements de sécurité importants : connexions réussies et échouées, changements de mot de passe, récupération de compte, élévation de privilèges, changements de droits, accès administratifs, export important, échecs répétitifs de contrôle d’accès et changements de configuration. Les événements doivent être structurés avec date, identifiant de corrélation, action, résultat, compte ou principal pseudonymisé si nécessaire, ressource et contexte technique utile. Les horloges des systèmes doivent être synchronisées et la conservation doit suivre les contraintes opérationnelles et juridiques applicables.

Évitez d’enregistrer les secrets. L’en-tête Authorization, les cookies, les codes de récupération et les mots de passe doivent être masqués ou exclus. Les données personnelles ne doivent pas être copiées massivement dans les logs. Les journaux eux-mêmes doivent être protégés contre la lecture, la modification et la suppression non autorisées. Un journal complet mais modifiable par l’application compromise n’est pas une preuve parfaite ; les événements à forte valeur peuvent être transmis vers une plateforme dédiée avec droits distincts.

### 9.3 Alertes et réponse

Une alerte utile associe une condition observable à un traitement. Dix mille erreurs 401 en quelques minutes, un grand nombre de refus BOLA sur plusieurs identifiants, ou une hausse d’exports volumineux peuvent indiquer un abus. Les seuils doivent être ajustés au trafic normal ; un pic peut être légitime, et une attaque lente peut rester sous les seuils simples. Corrélez identité, route, volume, contexte et évolution temporelle.

Prévoyez un processus de réponse : qualifier, conserver les éléments utiles, limiter l’abus, protéger les comptes, corriger la cause, vérifier les impacts, informer les responsables appropriés et apprendre de l’incident. Évitez de réagir uniquement à l’IP ; les utilisateurs partagent parfois une adresse, et un attaquant peut changer de source. Les journaux ne sont utiles que si quelqu’un les consulte, les alertes sont testées et les responsabilités sont claires.

## 10. Dépendances, configuration et cycle de développement

### 10.1 Dépendances logicielles

Une bibliothèque Web dépend d’autres paquets qui peuvent contenir des vulnérabilités ou être remplacés par une version malveillante. Maintenez un inventaire, utilisez des versions verrouillées quand c’est adapté, surveillez les avis de sécurité et mettez à jour avec des tests. Les scanners de dépendances (SCA) signalent les versions connues vulnérables, mais ne prouvent pas l’absence de vulnérabilités. Vérifiez aussi la provenance des paquets, les scripts d’installation, les permissions de publication et les jetons CI.

La gestion des dépendances doit inclure le suivi des versions transitives, la revue des changements importants et un plan de retrait des composants abandonnés. Un fichier de verrouillage reproductible aide à reconstruire le même ensemble de dépendances. Les builds et publications doivent se faire dans un environnement aux secrets limités, avec des permissions minimales et des journaux consultables.

### 10.2 Secrets et configuration

Les secrets doivent être fournis à l’exécution via une gestion dédiée ou un mécanisme de configuration protégé, avec rotation et permissions strictes. Ne commitez pas les clés dans Git, les fichiers de logs, les captures d’écran ou les rapports de test. Lorsqu’un secret a été publié, supprimer la ligne du dernier commit ne suffit pas toujours : il faut considérer le secret comme compromis, le révoquer, le remplacer et examiner l’usage éventuel.

Distinguez environnements de développement, de test et de production. Une base de données de production ne doit pas être copiée vers un environnement de test sans analyse et traitement adaptés des données. Désactivez les comptes de démonstration et les fonctions de debug en production. Les valeurs par défaut doivent être sûres, et le déploiement doit échouer explicitement si un secret obligatoire manque plutôt que de créer silencieusement une configuration dangereuse.

### 10.3 Tests de sécurité complémentaires

Les tests unitaires vérifient des règles isolées, comme le refus d’un accès non propriétaire. Les tests d’intégration valident les contrôles dans l’application complète avec sa base de données. Les tests de sécurité automatisés peuvent inclure l’analyse statique du code (SAST), l’analyse de dépendances (SCA), l’analyse dynamique (DAST) sur un environnement de test et des tests manuels ciblés. Aucun outil n’est suffisant isolément : ils produisent des signaux qui exigent du triage.

~~~text
Conception -> revue des menaces -> implémentation
    ^                               |
    |                               v
Retour d'expérience <- surveillance <- tests :
                                      - unitaires
                                      - intégration
                                      - SAST / SCA
                                      - DAST autorisé
                                      - revue manuelle
~~~

La qualité des tests dépend des scénarios d’autorisation, pas seulement du nombre de requêtes. Pour un objet privé, testez le propriétaire, un autre utilisateur, un utilisateur déconnecté, un rôle de lecture seule et un administrateur. Testez l’accès direct à l’API, car une interface qui masque un bouton peut créer une fausse impression de sécurité. Fixez des critères de réussite observables et rejouez les tests après une correction.

## 11. Lire l’OWASP Top 10:2025 et l’ASVS

L’OWASP Top 10:2025 est un document de sensibilisation aux catégories de risque importantes, pas une liste exhaustive de tous les contrôles à implémenter. Il couvre notamment le contrôle d’accès défaillant, les mauvaises configurations, les défaillances de chaîne d’approvisionnement logicielle, les défaillances cryptographiques, les injections, la conception non sécurisée, les échecs d’authentification, les problèmes d’intégrité logicielle ou de données, les défaillances de journalisation et d’alerte, et la mauvaise gestion des conditions exceptionnelles.

La catégorie ne donne pas une solution unique. Une injection peut être traitée avec requêtes paramétrées, validation, droits SQL minimaux et tests de régression. Une mauvaise configuration peut demander une revue d’infrastructure, des paramètres de sécurité et des contrôles de déploiement. Les problèmes d’accès exigent des règles explicites et des tests à travers tous les endpoints. La classification aide à discuter du risque ; elle ne remplace pas l’analyse de la fonctionnalité concernée.

L’OWASP ASVS, version 5.0.0, propose un référentiel de vérification de sécurité des applications et services Web. Il peut être utilisé pour transformer des exigences vagues en contrôles vérifiables. Une équipe peut sélectionner des exigences adaptées à son risque, définir des preuves attendues et relier les exigences aux tests et revues. Il faut préciser la version utilisée afin d’éviter des références ambiguës.

~~~text
Besoin métier
     |
     v
Actif et scénario de menace
     |
     v
Exigence de sécurité vérifiable
     |
     v
Contrôle de conception et implémentation
     |
     v
Test reproductible et résultat conservé
     |
     v
Suivi de la correction et surveillance
~~~

## 12. Méthode pratique d’audit applicatif

Commencez par comprendre le périmètre et les autorisations. Définissez l’environnement, les comptes de test, les fonctions autorisées et les limites du test. N’effectuez pas d’essais sur un site tiers sans autorisation explicite. Gardez une copie de la version testée et un moyen de restaurer les données. Évitez les tests qui modifient des comptes réels, envoient des courriels à des tiers ou suppriment des données, sauf si cela est explicitement prévu dans un environnement de test.

Établissez ensuite une cartographie des routes. Pour chaque route, documentez la méthode, les paramètres, le type d’utilisateur nécessaire, la ressource ciblée, les actions possibles, les données sensibles renvoyées, les dépendances externes et les limites attendues. Demandez quels champs peuvent être contrôlés par le client et quelles transitions métier sont permises.

~~~text
Route        Identité    Objet ciblé    Contrôle essentiel
GET /profile  session     profil propre  propriété / champs exposés
PATCH /profile session    profil propre  liste de champs autorisés
GET /assignments/{id} session devoir     autorisation par objet
POST /upload  session     nouveau fichier quota / contenu / stockage
POST /reset   public      jeton de reset limitation / usage unique
~~~

Construisez une matrice d’accès avant d’exécuter les tests. Elle doit indiquer les actions permises pour chaque rôle et les restrictions par objet. Ensuite, réalisez des tests négatifs : compte A essaie de lire un objet de B ; un rôle lecteur essaie de modifier ; un utilisateur déconnecté appelle directement une route ; un client ajoute un champ réservé ; une chaîne de test inoffensive est soumise comme donnée et doit rester une donnée. Les tests négatifs sont conçus pour prouver qu’une action non permise échoue proprement.

Pour chaque constat, consignez le prérequis, la route concernée, le comportement attendu, le comportement observé, l’impact, l’étendue, la preuve minimale expurgée et une recommandation testable. Évitez les rapports qui ne décrivent que le nom d’une faille sans démontrer la règle métier violée. Priorisez selon la criticité des actifs, l’exposition, la facilité d’abus, l’étendue des comptes touchés et les mesures de compensation.

## 13. Travaux pratiques corrigés

### TP 1 — Matrice d’autorisation sur Campus

**Objectif :** vérifier qu’une session valide ne suffit pas à autoriser toutes les actions.

**Contexte de laboratoire :** deux comptes fictifs Amina et Bruno, chacun avec un devoir privé. Un troisième compte enseignant peut consulter et noter les devoirs uniquement pour les cours qui lui sont attribués. Les données peuvent être recréées à chaque exécution.

**Étape 1.** Listez les rôles, les ressources et les actions : consulter un devoir, modifier son brouillon, soumettre le devoir, consulter une note, modifier une note et exporter les résultats.

**Étape 2.** Définissez les règles avant d’écrire les tests. Un apprenant ne peut consulter ou modifier que ses propres devoirs non verrouillés. Il ne peut pas modifier une note. Un enseignant ne peut noter que les cours qui lui sont attribués. L’administrateur peut gérer la configuration, mais son accès doit être explicite et journalisé.

**Étape 3.** Exécutez les tests sous plusieurs identités. Pour chaque ressource, vérifiez propriétaire, autre apprenant, enseignant non assigné et enseignant assigné. Testez chaque route de lecture, modification et export ; ne supposez pas que la page Web et l’API partagent les mêmes protections.

**Étape 4.** Conservez le code de réponse, le résultat métier et l’événement d’audit, sans enregistrer de cookie ou de jeton.

~~~text
Résultat attendu
Amina -> lire son devoir                 AUTORISÉ
Amina -> modifier son devoir brouillon   AUTORISÉ
Amina -> lire devoir de Bruno            REFUSÉ
Amina -> modifier note d'un devoir       REFUSÉ
Enseignant non assigné -> noter          REFUSÉ
Enseignant assigné -> noter devoir       AUTORISÉ + audit
Compte déconnecté -> lire devoir privé  REFUSÉ
~~~

**Correction expliquée.** L’identifiant de devoir ne constitue pas une preuve de permission. Le serveur charge la ressource, détermine son propriétaire et son contexte, puis compare avec l’identité authentifiée et le rôle. Pour le rôle enseignant, la propriété seule ne suffit pas : il faut vérifier l’affectation au cours. Les opérations d’écriture doivent recontrôler les conditions métier au moment où elles s’exécutent afin d’éviter qu’une permission vérifiée plus tôt devienne obsolète.

Un résultat positif est un refus côté serveur même lorsque la requête est envoyée directement sans utiliser l’interface. Si la réponse est 404 pour éviter la divulgation de l’existence d’une ressource, la cohérence de ce comportement doit être documentée. Un test réussi ne doit pas s’appuyer uniquement sur le statut HTTP : il vérifie aussi qu’aucune donnée sensible n’apparaît dans le corps et qu’aucune mutation n’a été réalisée.

**Critères d’acceptation :** chaque test dispose d’une identité et d’un objet connus ; les routes de lecture et d’écriture sont couvertes ; les refus ne modifient pas la base ; les actions privilégiées laissent un audit exploitable ; aucune preuve ne contient de secret.

### TP 2 — Corriger une requête SQL et un affichage de commentaire

**Objectif :** éviter qu’une entrée utilisateur modifie la structure d’une requête ou soit interprétée comme du HTML actif.

**Contexte :** une route de recherche accepte un titre de cours et une page de commentaires affiche le texte saisi par l’apprenant. Le laboratoire utilise des chaînes de test inoffensives, sans cibler un service réel.

**Étape 1.** Repérez les concaténations utilisées pour construire la requête. Remplacez-les par une requête paramétrée. N’utilisez pas l’identifiant transmis par le navigateur comme propriétaire ; utilisez la valeur issue de l’identité établie côté serveur.

**Étape 2.** Identifiez les sorties HTML. Pour le commentaire, utilisez le rendu textuel du framework. Si une fonction permet du HTML enrichi, définissez un ensemble minimal de balises autorisées et utilisez un assainisseur adapté et maintenu.

**Étape 3.** Ajoutez des tests de régression : apostrophe dans un titre, chaîne ressemblant à une balise, valeur trop longue, type inattendu et identifiant non autorisé. Les valeurs doivent rester des données et ne pas modifier la logique de la requête.

~~~text
Avant
Requête SQL assemblée depuis des fragments et entrée utilisateur

Après
Requête fixe + paramètres liés séparément

Avant affichage
Commentaire interprété comme du balisage

Après affichage
Commentaire présenté comme texte, sans exécution
~~~

**Correction expliquée.** Le paramétrage SQL garde le texte de la requête distinct des valeurs. Les règles de validation complètent cette défense en rejetant les types et tailles inattendus, mais la protection contre l’injection ne dépend pas du blocage de quelques caractères. Pour l’affichage, il faut utiliser les méthodes de sortie adaptées au contexte plutôt que supprimer des caractères à la main. L’encodage évite qu’un texte soit traité comme des balises, tandis qu’un assainisseur ne s’emploie que lorsqu’une fonctionnalité demande réellement du HTML.

Testez également les requêtes triées : le choix de colonne devrait provenir d’une liste blanche interne, car un nom de colonne ne se passe pas toujours comme une valeur SQL ordinaire. Réexécutez tous les tests après la correction.

**Critères d’acceptation :** aucune requête SQL n’est assemblée avec une valeur non fiable ; la sortie utilise le mécanisme de rendu sûr ; les tests prouvent que la valeur demeure une donnée ; les erreurs ne révèlent pas de détails de base de données.

### TP 3 — Session, cookies et protection CSRF

**Objectif :** contrôler le cycle de vie d’une session et empêcher qu’une action sensible soit déclenchée sans intention validée.

**Contexte :** Campus permet de modifier l’adresse de notification. L’opération utilise une session serveur et un formulaire Web.

**Étape 1.** Configurez le cookie de session avec Secure en production HTTPS, HttpOnly et une valeur SameSite compatible avec le parcours de navigation. Définissez la portée du cookie aussi étroitement que possible.

**Étape 2.** Vérifiez le renouvellement de l’identifiant après la connexion. Utilisez la nouvelle session après l’authentification et invalidez côté serveur la session lors de la déconnexion. Testez l’expiration d’inactivité et la révocation après une action sensible.

**Étape 3.** Ajoutez la protection CSRF prévue par le framework au formulaire de modification. Le serveur doit vérifier le jeton, pas seulement sa présence. Vérifiez le comportement pour jeton absent, invalide et valide.

**Étape 4.** Contrôlez que GET ne modifie pas l’adresse. Toute mutation utilise une méthode appropriée, une permission, une validation métier et une protection contre les requêtes forgées.

~~~text
Cas de test                          Résultat attendu
Session valide + jeton valide        modification contrôlée
Session valide + jeton absent        rejet sans mutation
Session valide + jeton invalide      rejet sans mutation
Session expirée                      authentification requise
Après déconnexion                    ancien identifiant inutilisable
Requête GET vers la même route        aucun changement d'état
~~~

**Correction expliquée.** Les attributs du cookie réduisent certaines expositions, mais ne remplacent ni la validation serveur ni le jeton CSRF. Le renouvellement de session limite le risque de fixation. La déconnexion doit rendre la session inutilisable côté serveur ; effacer uniquement le cookie côté navigateur n’invalide pas forcément un identifiant déjà copié. Une tentative refusée doit laisser un événement suffisamment utile au diagnostic, sans journaliser la valeur du jeton.

**Critères d’acceptation :** les tests vérifient l’état serveur après chaque tentative ; le jeton n’apparaît pas dans les logs ; le comportement des cookies est vérifié dans le navigateur ; le parcours complet fonctionne encore pour un utilisateur légitime.

### TP 4 — Téléversement, configuration et journaux

**Objectif :** limiter les risques introduits par les fichiers et conserver des preuves utiles sans journaliser de secrets.

**Contexte :** un apprenant téléverse un devoir. Les seuls formats autorisés dans le laboratoire sont PDF et images raster, avec taille et quota limités.

**Étape 1.** Appliquez une permission de téléversement avant tout traitement. Refusez les tailles excessives et vérifiez le format à partir du contenu avec des bibliothèques adaptées. Ne vous fiez pas uniquement à l’extension ni au type annoncé.

**Étape 2.** Attribuez un nom interne généré, stockez le fichier hors de la racine publique et conservez l’association entre le fichier, le devoir et son propriétaire. Toute route de téléchargement doit recontrôler la permission de lecture.

**Étape 3.** Gérez les erreurs de parsing, d’espace disque ou de quota sans afficher de trace technique. Ajoutez un identifiant de corrélation et journalisez l’issue, la taille, le type validé et le compte selon la politique de confidentialité, mais pas le contenu du fichier ou un jeton d’accès.

**Étape 4.** Vérifiez que les clés d’accès ne sont pas dans les fichiers suivis par Git, que les options de debug sont désactivées en production et que les droits du compte applicatif sur le stockage sont minimaux.

~~~text
Téléversement autorisé -> contrôle taille -> détection de format
        -> nom généré -> stockage isolé -> association propriétaire
        -> téléchargement avec autorisation -> événement expurgé
~~~

**Correction expliquée.** L’extension n’est qu’une métadonnée contrôlée par le client. Le contenu doit être vérifié, les traitements complexes isolés et les limites imposées à toutes les étapes. Le téléchargement repasse par l’autorisation, car connaître l’identifiant d’un fichier ne devrait pas accorder l’accès. Une erreur doit être exploitable par l’équipe sans révéler un chemin absolu, une trace ou un secret. Si un secret apparaît dans Git, il faut le révoquer et le remplacer, pas simplement supprimer le texte du fichier.

**Critères d’acceptation :** fichiers conformes acceptés ; formats non conformes, tailles excessives et quotas dépassés refusés ; aucun fichier déposé n’est exécuté ; lecture inter-utilisateur bloquée ; erreurs corrélables et expurgées ; secrets hors du dépôt.

## 14. Exercices corrigés

### Exercice 1 — Authentification ou autorisation ?

Un utilisateur valide ouvre une URL contenant l’identifiant d’un devoir appartenant à un autre compte. La session est acceptée, mais le devoir est retourné.

**Correction :** l’authentification a fonctionné, mais l’autorisation au niveau de l’objet est défaillante. La route doit appliquer une règle de propriété ou une permission explicitement définie. L’utilisation de HTTPS et d’un identifiant difficile à deviner ne corrige pas le défaut.

### Exercice 2 — Bouton masqué

L’interface masque le bouton « supprimer » pour un rôle apprenant, mais l’endpoint accepte la requête directe.

**Correction :** la restriction de l’interface n’est pas un contrôle de sécurité. L’API doit refuser la suppression selon l’identité, les permissions, l’état métier et la portée de la ressource. Ajoutez un test d’intégration qui appelle l’API directement.

### Exercice 3 — Requête SQL concaténée

Un développeur retire les apostrophes de la recherche par remplacement de chaîne et conserve la concaténation SQL.

**Correction :** ce filtre artisanal est fragile et ne sépare pas le code des données. Utilisez des paramètres liés. Les règles de validation peuvent compléter, mais ne remplacent pas les requêtes paramétrées.

### Exercice 4 — Commentaire HTML

Un commentaire est sauvegardé puis inséré dans la page via une propriété qui interprète une chaîne comme HTML.

**Correction :** utiliser un rendu textuel ou une API qui échappe la sortie dans le contexte concerné. Si du HTML est réellement nécessaire, utiliser un assainisseur maintenu avec une politique d’autorisation stricte. Ajouter une CSP comme défense en profondeur.

### Exercice 5 — Le rôle provient du formulaire

Le serveur accepte un champ role envoyé par le client et le copie dans l’objet utilisateur.

**Correction :** retirer ce champ des attributs modifiables pour un utilisateur standard. Les modifications de rôle sont une action privilégiée, par une route dédiée, avec autorisation explicite et audit. Prévoir un test de mass assignment.

### Exercice 6 — Le cookie contient l’identifiant du compte

Le développeur considère que le cookie est fiable parce qu’il est encodé en Base64.

**Correction :** l’encodage n’est pas un mécanisme de signature ou de chiffrement. Utiliser une session serveur ou un jeton correctement protégé selon un modèle établi, vérifier l’intégrité et les conditions d’expiration, et ne pas déduire un rôle privilégié de données modifiables côté client.

### Exercice 7 — SameSite suffit-il ?

Une application désactive le jeton CSRF car son cookie utilise SameSite.

**Correction :** la propriété SameSite est utile mais son adéquation dépend du modèle, des sous-domaines et des flux externes. Pour les actions sensibles, documenter les protections et tester les cas intersites. Le serveur doit valider les requêtes et ne jamais employer GET pour une mutation.

### Exercice 8 — API protégée par CORS

Une équipe autorise les requêtes CORS uniquement depuis son site officiel et conclut que la route est sécurisée.

**Correction :** CORS est une politique navigateur contrôlant la lecture de certaines réponses. Les clients non navigateur peuvent appeler l’API. Il faut authentifier, autoriser, valider et limiter les requêtes côté serveur.

### Exercice 9 — URL de miniature arbitraire

Une application télécharge une image depuis n’importe quelle URL et suit toutes les redirections.

**Correction :** cela crée un risque SSRF. Restreindre les schémas, destinations, ports et adresses, réévaluer chaque redirection, appliquer une politique d’accès réseau sortant, imposer des délais et des tailles maximales. Préférer une liste d’hôtes approuvés.

### Exercice 10 — Nom de fichier contrôlé

Le serveur assemble un chemin de stockage avec le nom de fichier envoyé par le navigateur.

**Correction :** utiliser un identifiant interne et un nom généré. Si un chemin doit être construit, le confiner au répertoire approuvé après résolution avec des primitives fiables, y compris les considérations de liens symboliques. Les permissions système doivent limiter l’impact d’une erreur.

### Exercice 11 — Vérifier seulement le type MIME

Le serveur accepte tout fichier dont le type annoncé est application/pdf.

**Correction :** le type est contrôlé par le client et peut être trompeur. Vérifier le contenu avec une bibliothèque adaptée, contrôler la taille, isoler le traitement et ne jamais exécuter les fichiers reçus. Le format détecté n’élimine pas tous les risques.

### Exercice 12 — Trace complète envoyée au client

Une réponse 500 retourne le message d’exception, le chemin de fichier et la requête SQL.

**Correction :** retourner un message stable et un identifiant de corrélation. Conserver les détails techniques filtrés dans un journal à accès contrôlé. Ne jamais inclure de mot de passe, cookie, jeton ou corps confidentiel dans les logs.

### Exercice 13 — CSP très permissive

La politique autorise toutes les sources et les scripts en ligne sans justification.

**Correction :** inventorier les sources nécessaires, commencer par une phase de rapport lorsque c’est possible, puis construire une politique restrictive. Éviter les exceptions larges. CSP est une défense en profondeur et ne remplace pas l’encodage de sortie.

### Exercice 14 — Secret dans le frontend

Une clé privée est stockée dans une variable d’environnement dont le nom commence par PUBLIC_ et est injectée dans le JavaScript.

**Correction :** les variables intégrées au frontend peuvent être lues par les utilisateurs. Révoquer la clé si elle a été publiée, la remplacer, puis déplacer l’opération nécessitant le secret côté serveur. Les secrets doivent être injectés à l’exécution avec droits minimaux.

### Exercice 15 — Journal des requêtes

Un middleware consigne tous les en-têtes, y compris Cookie et Authorization, afin de faciliter le dépannage.

**Correction :** masquer ou exclure les en-têtes sensibles. Journaliser un identifiant de corrélation, route, résultat, durée et contexte minimal utile. Protéger les journaux et limiter leur conservation selon les règles applicables.

### Exercice 16 — Tests uniquement positifs

Tous les tests vérifient qu’un utilisateur peut lire son propre profil ; aucun n’essaye avec un autre compte.

**Correction :** ajouter des tests négatifs et des tests croisés par rôle et propriétaire. Vérifier les accès directs à l’API, les routes d’export et de téléchargement, les modifications de champs sensibles et l’état de la base après un refus.

### Exercice 17 — Dépendance sans mise à jour

Une application utilise une bibliothèque non maintenue parce que tous les tests unitaires passent.

**Correction :** les tests fonctionnels ne prouvent pas l’absence de vulnérabilités connues. Inventorier les dépendances directes et transitives, surveiller les avis, examiner la provenance et migrer ou isoler le composant. Les mises à jour doivent rester testées et reproductibles.

### Exercice 18 — Réponse 404 ou 403 ?

L’équipe se demande si une ressource privée inexistante et une ressource existante mais non autorisée doivent toujours produire des réponses différentes.

**Correction :** le choix dépend du modèle de menace et du risque de révélation d’existence. Il faut un comportement cohérent et documenté, sans données confidentielles dans le corps. Quel que soit le code choisi, l’accès doit être refusé et la tentative pertinente doit être auditable.

### Exercice 19 — Limitation par IP uniquement

Les abus de création de compte sont limités par adresse IP ; plusieurs utilisateurs d’une même entreprise partagent cette adresse.

**Correction :** la limite purement IP peut bloquer des utilisateurs légitimes et se contourner par rotation de source. Combiner des signaux proportionnés au risque, des quotas sur l’action, des limites par compte et une temporisation. Prévoir un chemin d’assistance et surveiller les faux positifs.

### Exercice 20 — Nettoyage d’une dépendance compromise

Un secret de publication apparaît dans un commit puis est supprimé dans le commit suivant.

**Correction :** considérer le secret comme exposé. Le révoquer et le remplacer, vérifier les usages éventuels, réduire les permissions du nouveau secret et analyser l’historique et les journaux. Le retrait du texte n’annule pas la copie déjà faite par un tiers.

## 15. Défi final corrigé — sécuriser la release de Campus

### Situation

Une nouvelle version de Campus ajoute trois fonctions : consultation des devoirs, téléversement des travaux et génération d’un aperçu à partir d’une URL. Les tests montrent qu’un compte voit parfois un devoir qui n’est pas le sien, une erreur interne apparaît lors d’un fichier trop volumineux et la génération d’aperçu suit toute redirection. L’équipe souhaite livrer rapidement.

### Travail demandé

1. Définir les actifs critiques et les frontières de confiance.
2. Décrire les contrôles à mettre en place avant le déploiement.
3. Définir au moins six tests d’acceptation négatifs.
4. Définir les événements de journalisation et les secrets à exclure.
5. Proposer une décision de release justifiée avec critères de sortie.

### Correction détaillée

**1. Actifs et frontières.** Les actifs incluent les devoirs, les identités, les sessions, le stockage de fichiers, les secrets utilisés pour accéder au stockage et les ressources réseau internes. Les frontières importantes relient le navigateur à l’API, l’API au stockage, le traitement de fichiers au système, et le récupérateur d’URL au réseau sortant. Les paramètres, fichiers, métadonnées et URL sont non fiables.

**2. Contrôles.** Corriger l’autorisation par objet sur chaque route de lecture, téléchargement et export. Le demandeur provient de la session vérifiée ; il ne peut pas choisir le propriétaire dans le corps. Valider les transitions métier et retourner une réponse cohérente. Pour les fichiers : quotas, limites de taille et de temps, validation de contenu, nom interne, stockage isolé et autorisation de téléchargement. Pour l’aperçu : destinations approuvées, schémas et ports autorisés, protections réseau sortant, revalidation des redirections, limites et délais. Dans tous les cas, masquer les erreurs internes et retirer les secrets des journaux.

**3. Tests négatifs.** Un compte A tente de consulter le devoir de B ; il tente de télécharger un fichier de B ; un compte déconnecté appelle directement la route ; un corps de mise à jour tente de changer owner_id ; un fichier dépasse le quota ; un fichier présente une extension qui ne correspond pas au contenu ; un aperçu demande une destination interdite ; une URL redirige vers une destination qui ne figure pas dans la liste approuvée ; une erreur de traitement ne doit pas révéler la trace système ; un cookie ou un jeton ne doit pas apparaître dans les journaux. Chaque test vérifie le résultat HTTP, l’absence de mutation ou d’exposition, et les événements d’audit appropriés.

**4. Journalisation.** Enregistrer les refus d’accès significatifs, les tentatives de dépassement de quota, les erreurs de validation de fichier, les échecs de récupération d’URL et les opérations privilégiées. Inclure un identifiant de corrélation, route, résultat, heure, ressource interne et taille utile. Exclure les mots de passe, cookies, jetons, secrets, contenu complet du fichier et données privées non nécessaires. Protéger l’accès aux journaux et définir les règles de conservation.

**5. Décision de release.** Ne pas livrer tant que la fuite entre propriétaires n’est pas corrigée et que les tests de non-régression ne démontrent pas le refus. Le défaut d’autorisation expose directement la confidentialité et peut également permettre une modification. La génération d’aperçu doit être limitée avant mise en production, car l’accès serveur à des destinations non maîtrisées peut exposer l’infrastructure. L’erreur volumineuse doit être corrigée pour éviter divulgation technique et consommation excessive. La sortie est conditionnée par des tests verts, un contrôle de configuration, la revue des permissions, la vérification de l’absence de secrets dans les artefacts et une procédure de retour arrière.

### Grille de notation suggérée

~~~text
Cartographie actifs et frontières                 15 points
Contrôle d'accès objet et tests de régression      25 points
Sécurité des fichiers et du récupérateur d'URL     25 points
Gestion des erreurs et journalisation              15 points
Décision de release, preuves et retour arrière     20 points
Total                                             100 points
Seuil recommandé de validation                     80 points
~~~

Une réponse qui se limite à ajouter un pare-feu, HTTPS ou un scanner ne suffit pas. Les défauts décrits sont des problèmes de logique applicative qui exigent des contrôles sur les objets, les flux de données et les opérations métier.

## 16. Checklist de mise en production

- [ ] Toutes les routes sensibles ont une identité et une autorisation explicites, y compris au niveau de l’objet.
- [ ] Les champs acceptés par chaque endpoint sont documentés et filtrés ; les champs internes ne sont pas modifiables par défaut.
- [ ] Les requêtes SQL utilisent des paramètres liés ou un accès ORM sûr.
- [ ] La sortie HTML est encodée selon son contexte ; tout HTML enrichi passe par une politique de nettoyage explicite.
- [ ] Les actions qui modifient l’état ne passent pas par GET et disposent de protections CSRF adaptées au modèle de session.
- [ ] Les cookies de session ont des attributs et une portée adaptés ; la session est renouvelée et invalidée correctement.
- [ ] HTTPS et les certificats sont valides ; HSTS n’est activé qu’après validation du périmètre concerné.
- [ ] CORS n’est jamais utilisé comme remplacement de l’authentification ou de l’autorisation.
- [ ] Les téléversements sont limités, contrôlés, stockés sans exécution et téléchargés avec autorisation.
- [ ] Les récupérateurs d’URL restreignent les destinations et suivent les redirections sous contrôle.
- [ ] Les en-têtes de sécurité sont configurés, testés et documentés, y compris la politique CSP.
- [ ] Les réponses client n’exposent pas de traces, chemins, secrets ou requêtes internes.
- [ ] Les journaux contiennent des événements utiles sans secrets ni données personnelles excessives.
- [ ] Les dépendances et les secrets font l’objet d’une surveillance et de procédures de rotation.
- [ ] Les tests négatifs couvrent les rôles, propriétaires, utilisateurs non connectés, endpoints directs, exports et téléchargements.
- [ ] Les exigences et preuves de vérification sont rattachées à une version connue du référentiel choisi.
- [ ] La release dispose d’un plan de retour arrière, d’une surveillance et d’un responsable de traitement des alertes.

## 17. Glossaire

**API :** interface qui expose des fonctions ou données à des clients logiciels.  
**Authentification :** vérification de l’identité ou du principal présenté.  
**Autorisation :** décision d’accorder ou de refuser une action à un principal.  
**BOLA / IDOR :** défaut de contrôle d’accès à une ressource au niveau de l’objet.  
**CORS :** mécanisme de navigateur qui contrôle la lecture de certaines réponses entre origines.  
**CSRF :** attaque qui tente de déclencher une action avec l’autorité ambiante d’une session.  
**CSP :** politique du navigateur limitant les sources et comportements de certaines ressources.  
**Encodage de sortie :** transformation d’une donnée afin qu’elle soit traitée comme donnée dans un contexte précis.  
**HSTS :** mécanisme indiquant aux navigateurs de privilégier HTTPS pour un domaine pendant une durée donnée.  
**Injection :** interprétation d’une entrée comme partie d’une instruction au lieu d’une valeur.  
**MFA :** authentification reposant sur plusieurs facteurs distincts.  
**Mass assignment :** affectation incontrôlée de champs reçus à un objet interne.  
**SAST :** analyse statique du code source ou des artefacts sans exécuter l’application complète.  
**SCA :** analyse des composants et dépendances logicielles.  
**SSRF :** utilisation d’une fonction serveur pour effectuer des requêtes vers des destinations non voulues.  
**Session :** état permettant d’associer plusieurs requêtes à un contexte d’authentification.  
**XSS :** exécution de contenu actif injecté dans le contexte d’une application Web.

## 18. Références officielles et suite de travail

- OWASP Top 10:2025 : https://top10.owasp.org/2025/
- OWASP Application Security Verification Standard (ASVS), version 5.0.0 : https://asvs.owasp.org/
- OWASP Cheat Sheet Series : https://cheatsheetseries.owasp.org/
- OWASP Cheat Sheet — SQL Injection Prevention : https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- OWASP Cheat Sheet — Cross Site Scripting Prevention : https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- OWASP Cheat Sheet — Cross-Site Request Forgery Prevention : https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP Cheat Sheet — Server Side Request Forgery Prevention : https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP Cheat Sheet — File Upload : https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- MDN — Content-Security-Policy : https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy
- MDN — HTTP cookies : https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
- RFC 9110 — HTTP Semantics : https://www.rfc-editor.org/rfc/rfc9110
- RFC 9112 — HTTP/1.1 : https://www.rfc-editor.org/rfc/rfc9112

Consultez les versions publiées de ces ressources lors de la conception d’un contrôle. Les recommandations s’enrichissent avec l’évolution des navigateurs, des frameworks et des menaces. Pour un projet réel, reliez chaque contrôle à une version explicite du standard et consignez les raisons de toute exception.

Fin du cours.