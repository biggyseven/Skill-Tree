# Authentification et MFA

> **Encadré de mise en contexte**
>
> Tu travailles comme technicien informatique dans une entreprise qui utilise une plateforme de formation en ligne. Les apprenants disposent de comptes personnels pour consulter leurs cours et passer leurs examens. Les formateurs peuvent publier des contenus, tandis que les administrateurs gèrent les utilisateurs, les droits d'accès et les paramètres de sécurité.
>
> Un matin, un formateur reçoit un courriel qui semble provenir du service informatique. Le message lui demande de confirmer son mot de passe sur un site présenté comme le portail officiel. Il saisit ses identifiants, puis reçoit une demande de validation sur son téléphone. Il l'accepte sans vérifier pourquoi cette demande vient d'apparaître.
>
> Quelques minutes plus tard, un attaquant se connecte au compte, consulte des informations auxquelles le formateur a accès et tente de modifier les coordonnées de récupération. L'entreprise découvre que le mot de passe seul n'était pas le seul problème : la méthode d'authentification supplémentaire a été utilisée dans un contexte frauduleux, et la procédure de récupération était insuffisamment protégée.
>
> Quelques jours plus tard, un employé perd son téléphone et ne peut plus se connecter. L'équipe doit restaurer son accès sans permettre à une autre personne de se faire passer pour lui.
>
> Ces situations montrent que la sécurité des comptes ne consiste pas simplement à choisir un mot de passe complexe. Il faut comprendre l'identité numérique, les facteurs d'authentification, la MFA, les attaques contre les comptes, la gestion des sessions et la récupération des accès.

## 1. Objectifs du cours

À la fin de ce cours, tu devras pouvoir distinguer identification, authentification et autorisation ; comprendre les catégories de facteurs ; expliquer pourquoi deux mots de passe ne constituent pas une MFA ; gérer des mots de passe uniques et robustes ; comprendre les codes temporaires, les applications d'authentification, les clés de sécurité et les passkeys ; reconnaître les limites de chaque méthode ; identifier les attaques par phishing, vol de session, échange frauduleux de SIM et fatigue liée aux notifications ; sécuriser la récupération du compte ; et proposer une politique adaptée aux utilisateurs, aux administrateurs et aux comptes sensibles.

Ce cours vise un niveau débutant. Il présente les concepts nécessaires pour administrer des comptes et comprendre les mécanismes de sécurité usuels, sans prétendre remplacer une formation spécialisée en gestion des identités.

## 2. Comprendre l'identité numérique

### 2.1. Qu'est-ce qu'une identité numérique ?

Une identité numérique est l'ensemble des informations utilisées par un système pour représenter une personne, une organisation, un appareil ou un service. Sur une plateforme de formation, une identité peut comprendre un identifiant, un nom d'affichage, une adresse électronique, un rôle, des informations de récupération, des facteurs inscrits et un historique de connexion.

Toutes ces informations ne sont pas nécessairement des secrets. Un nom d'affichage peut être visible, tandis que les facteurs et les moyens de récupération doivent être protégés. Connaître le nom d'utilisateur d'une personne ne signifie pas que l'on contrôle son compte.

### 2.2. Identification, authentification et autorisation

**Schéma pédagogique — Ces trois étapes sont liées mais ne signifient pas la même chose.**

~~~text
[Identification] --> [Authentification] --> [Autorisation]
 Qui es-tu ?        Prouve-le comment ?   Que peux-tu faire ?
       |                    |                    |
       v                    v                    v
 nom / compte       mot de passe + MFA      role / politique

Une authentification reussie ne confere pas tous les privileges.
~~~


L'identification consiste à indiquer quelle identité on souhaite utiliser. Par exemple, tu saisis le nom de compte technicien01 dans le formulaire de connexion.

L'authentification consiste à vérifier que tu contrôles les moyens d'accès associés à cette identité. Tu peux fournir un mot de passe, puis confirmer la connexion avec un facteur supplémentaire.

L'autorisation détermine les actions permises à une identité authentifiée. Un apprenant peut consulter un cours sans pouvoir modifier les résultats d'examen des autres utilisateurs.

    Utilisateur
        |
        v
    Identification : quel compte ?
        |
        v
    Authentification : contrôle-t-il les facteurs attendus ?
        |
        v
    Session établie
        |
        v
    Autorisation : quelles actions sont permises ?
        |
        v
    Accès aux ressources autorisées

Une authentification réussie ne donne donc pas automatiquement accès à toutes les ressources. Les droits doivent être vérifiés séparément par l'application.

### 2.3. Principe du moindre privilège

Le moindre privilège consiste à accorder uniquement les permissions nécessaires à une fonction. Un utilisateur qui consulte des cours ne devrait pas recevoir des droits d'administration. Un compte de maintenance peut être distinct du compte ordinaire utilisé pour les tâches quotidiennes.

Ce principe réduit les conséquences d'un compte compromis. Même si un attaquant s'authentifie, les dommages possibles sont limités par les permissions accordées.

## 3. Pourquoi les mots de passe ne suffisent-ils pas toujours ?

### 3.1. Le fonctionnement du mot de passe

Un mot de passe est un secret mémorisé. Lors de la connexion, l'utilisateur le fournit au service, qui vérifie qu'il correspond au vérificateur associé au compte. Le mot de passe ne devrait normalement pas être conservé en clair dans la base de données. Le stockage doit utiliser une fonction adaptée aux mots de passe, avec des paramètres appropriés et un sel unique.

### 3.2. Les attaques courantes

Un mot de passe robuste peut être compromis si l'utilisateur le saisit sur un faux site, si son appareil est infecté, si le secret est stocké sans protection ou si un service tiers est compromis.

La force brute consiste à essayer de nombreuses possibilités. L'attaque par dictionnaire teste des mots, expressions et combinaisons courantes. Le credential stuffing utilise des paires identifiant-mot de passe récupérées lors d'une fuite sur d'autres services. Le phishing trompe l'utilisateur afin qu'il révèle des identifiants ou valide une opération frauduleuse. Après le vol d'une base de données, un attaquant peut aussi tester localement des mots de passe candidats contre les vérificateurs volés.

Ces attaques ne se règlent pas toutes de la même manière. La limitation des tentatives aide contre certains essais en ligne ; un gestionnaire de mots de passe réduit la réutilisation ; une méthode résistante au phishing protège mieux contre certains faux sites.

### 3.3. Pourquoi un facteur supplémentaire aide

Si un attaquant connaît uniquement le mot de passe, il peut lui manquer un autre élément nécessaire à la connexion. La MFA réduit ainsi les conséquences de certains vols d'identifiants. Mais elle n'est pas absolue : certains codes peuvent être interceptés ou relayés, certaines notifications approuvées par erreur et des sessions déjà établies peuvent être volées.

## 4. Les trois catégories de facteurs

### 4.1. Quelque chose que l'on connaît

C'est un secret mémorisé : mot de passe, code PIN ou phrase secrète. Un code PIN et un mot de passe appartiennent à la même catégorie. Demander successivement deux mots de passe ne constitue donc pas une MFA.

### 4.2. Quelque chose que l'on possède

C'est un objet ou dispositif contrôlé par l'utilisateur : clé de sécurité compatible FIDO2, téléphone inscrit comme authentificateur, carte à puce ou dispositif matériel générant des codes temporaires. La preuve de possession varie selon la technologie. Un système robuste peut vérifier la possession d'une clé par un protocole cryptographique plutôt que de se fier uniquement à un code saisi.

### 4.3. Quelque chose que l'on est

C'est une caractéristique biométrique, par exemple une empreinte digitale ou une reconnaissance faciale. La biométrie n'est pas un secret ordinaire que l'on peut remplacer comme un mot de passe. Dans de nombreux systèmes, elle sert à déverrouiller localement un authentificateur ; le serveur ne reçoit pas nécessairement l'image biométrique.

### 4.4. Exemples d'authentification multifacteur

**Schéma pédagogique — Deux facteurs de catégories différentes sont plus solides que deux secrets du même type.**

~~~text
Facteur connaissance: mot de passe ------\
                                           +--> decision MFA
Facteur possession: cle / application -----/

Autres controles possibles:
- biometrie locale d'un appareil
- certificat d'appareil
- contexte et etat de conformite

Deux mots de passe restent deux elements de la meme categorie.
~~~


Cas A : le site demande deux mots de passe. Les deux sont des secrets connus ; ce n'est pas une MFA au sens des catégories de facteurs.

Cas B : le site demande un mot de passe et un code temporaire produit par une application inscrite. Le système combine généralement un secret connu et un facteur lié à la possession du dispositif. Il faut malgré tout protéger l'inscription et vérifier correctement le code.

Cas C : une clé de sécurité protégée par un PIN local peut combiner possession et activation locale selon le protocole. Il ne faut pas déduire la classification uniquement du nombre d'écrans : il faut comprendre ce que le système vérifie réellement.

Cas D : mot de passe et reconnaissance faciale peuvent relever de catégories différentes si l'architecture les utilise comme facteurs indépendants. En revanche, une biométrie servant seulement à déverrouiller localement un authentificateur n'est pas nécessairement envoyée au serveur comme facteur séparé.

| Catégorie | Exemples | Limite principale |
|---|---|---|
| Connaissance | Mot de passe, PIN, phrase secrète | Peut être deviné, réutilisé ou divulgué |
| Possession | Téléphone inscrit, clé de sécurité, carte | Peut être perdu, volé ou mal configuré |
| Inhérence | Empreinte, reconnaissance faciale | Dépend de la mise en œuvre et du contexte |

## 5. Créer et gérer des mots de passe robustes

### 5.1. Longueur et imprévisibilité

Un mot de passe robuste doit être difficile à deviner. La longueur est importante, mais la prévisibilité compte aussi. Password2026! peut sembler complexe en combinant majuscules, chiffres et ponctuation, mais suit un motif courant.

Une phrase secrète longue et unique peut être plus facile à mémoriser. Pour un compte sensible, un gestionnaire peut générer un secret aléatoire et le conserver dans un coffre protégé.

### 5.2. Un secret différent par service

Ne réutilise pas un mot de passe sur plusieurs services. Si un site secondaire est compromis, un attaquant peut tenter le même secret sur la messagerie, le stockage cloud ou le compte professionnel. L'unicité réduit la propagation d'une fuite d'identifiants.

### 5.3. Le gestionnaire de mots de passe

Un gestionnaire permet de stocker des secrets et de générer des mots de passe uniques. Il réduit la charge de mémorisation, mais son coffre doit être protégé par un secret robuste, une MFA si disponible et une procédure de récupération adaptée. L'appareil qui héberge le gestionnaire doit également être maintenu et sécurisé.

### 5.4. Politique de mots de passe

Une politique actuelle devrait :
- imposer une longueur minimale adaptée au risque et autoriser les mots de passe longs ;
- refuser les secrets manifestement compromis ou très courants lorsque c'est possible ;
- encourager les gestionnaires et les mots de passe uniques ;
- éviter les règles de composition arbitraires qui n'apportent pas de valeur démontrée ;
- limiter les essais automatisés sans créer un moyen simple de déni de service contre les utilisateurs ;
- permettre le collage dans les champs d'authentification lorsque cela peut être fait de façon sûre ;
- éviter les changements périodiques sans motif de risque ou signe de compromission ;
- imposer une modification rapide lorsqu'une divulgation est suspectée ou confirmée.

Les exigences exactes dépendent du niveau de risque et des obligations applicables. Une politique doit être compréhensible, appliquée et testée.

### 5.5. Que faire après une compromission ?

Il faut changer le mot de passe, vérifier les sessions et examiner les activités inhabituelles. Si le même mot de passe a été utilisé ailleurs, il faut également le remplacer sur les autres services concernés. Pour un compte professionnel sensible, l'organisation peut devoir révoquer les sessions actives et examiner les méthodes de récupération, les authentificateurs ajoutés et les jetons d'accès.

Changer uniquement le mot de passe ne suffit pas toujours si un attaquant a créé une session persistante ou ajouté un moyen de récupération frauduleux.

## 6. Comprendre la MFA

### 6.1. Définition

La MFA, ou authentification multifacteur, exige au moins deux facteurs distincts issus de catégories différentes. Elle cherche à réduire la probabilité qu'un attaquant puisse s'authentifier en contrôlant une seule preuve.

Elle peut combiner un mot de passe et un code temporaire, un mot de passe et une clé de sécurité ou d'autres méthodes selon le système. Toutes ces méthodes ne présentent pas la même résistance aux attaques.

### 6.2. Où déployer la MFA ?

Elle devrait être prioritaire pour les comptes administrateurs, la messagerie professionnelle, les accès distants, les consoles cloud, les outils financiers, les systèmes contenant des données sensibles, les comptes de publication de logiciels et les comptes capables de modifier les permissions d'autres utilisateurs.

La messagerie est particulièrement importante, car elle peut servir à réinitialiser les mots de passe d'autres services. Sa compromission peut donc entraîner une cascade d'accès non autorisés.

### 6.3. Limites de la MFA

Si l'attaquant contrôle une session active, il peut parfois agir sans déclencher de nouvelle demande MFA. Si l'utilisateur approuve une demande initiée par l'attaquant, le facteur peut être contourné par manipulation. Si la récupération du compte est faible, l'attaquant peut chercher à contourner la connexion en demandant le retrait du second facteur.

La MFA doit donc être associée à une gestion correcte des sessions, à une authentification adaptée au risque et à une récupération robuste.

## 7. Les codes à usage unique

### 7.1. Principe

Un code à usage unique sert à valider une étape d'authentification. Il peut être transmis par un canal de communication ou généré par une application ou un dispositif. Selon la méthode, sa validité est limitée dans le temps ou liée à un événement.

Un code temporaire n'est pas nécessairement résistant au phishing. Si l'utilisateur le saisit sur un faux site, l'attaquant peut parfois le relayer immédiatement au service légitime.

### 7.2. Codes reçus par SMS

Le SMS est familier et simple à déployer, et peut être préférable à l'absence de protection supplémentaire. Mais un numéro peut être détourné par une fraude au remplacement de SIM, un utilisateur peut être trompé pour divulguer son code et la réception dépend du réseau téléphonique.

Le SMS n'est donc pas le choix à privilégier pour un compte à haut risque lorsque des méthodes plus résistantes au phishing sont disponibles.

### 7.3. Applications TOTP

Certaines applications génèrent des codes à partir d'un secret partagé et de paramètres temporels, selon un protocole tel que TOTP. Le service et l'application doivent d'abord être inscrits correctement, puis calculent et vérifient les codes selon les règles prévues.

Une application de codes peut éviter la dépendance au SMS à chaque connexion, mais le code affiché peut toujours être demandé par un faux site puis relayé en temps réel. Cette méthode améliore certains contrôles sans fournir nécessairement la même résistance au phishing qu'une authentification cryptographique liée au site attendu.

### 7.4. Durée de validité

Un code valable pendant une durée limitée réduit la période durant laquelle il peut être utilisé, mais ne le rend pas impossible à voler. Il faut combiner la durée de validité avec les contrôles de tentatives, la protection de session et une méthode adaptée au risque.

### 7.5. Codes de secours

Un service peut fournir des codes de récupération pour retrouver l'accès lorsque l'authentificateur principal est perdu. Ils doivent être conservés dans un endroit sûr et ne pas être publiés dans des notes accessibles, envoyés dans un canal non protégé ou partagés avec le support.

Chaque code peut être utilisable une seule fois, selon le service. L'utilisateur doit savoir comment obtenir de nouveaux codes et comment invalider ceux qui ont été utilisés ou exposés.

## 8. Notifications d'approbation et fatigue MFA

### 8.1. Le fonctionnement

Certains services envoient une notification sur un appareil inscrit lorsqu'une connexion est tentée. L'utilisateur peut alors approuver ou refuser la demande. La méthode peut être simple, mais dépend de la conception du système et du comportement de l'utilisateur.

### 8.2. La fatigue MFA

Un attaquant qui connaît le mot de passe peut déclencher plusieurs demandes jusqu'à ce que l'utilisateur, agacé ou pressé, en accepte une. Ce phénomène est appelé fatigue MFA.

Les utilisateurs ne doivent jamais approuver une demande qu'ils n'ont pas eux-mêmes initiée. Une succession de notifications inattendues peut signaler une tentative d'accès non autorisé.

### 8.3. Le contexte et la correspondance de nombres

**Schéma pédagogique — La confirmation explicite réduit les approbations accidentelles liées aux notifications répétées.**

~~~text
Attaquant provoque demande MFA
             |
             v
Utilisateur voit: demande / nombre / contexte
             |
       +-----+------+
       |            |
       v            v
Demande attendue  Demande inattendue
       |            |
       v            v
Verifier le code  Refuser + signaler

Ne jamais approuver une notification que tu n'as pas initiee.
~~~


Une notification indiquant seulement « Autoriser la connexion ? » donne peu d'informations. Lorsqu'un système le permet, il peut afficher des détails complémentaires ou exiger une correspondance de nombres pour rendre les validations accidentelles plus difficiles.

Cela n'est pas automatiquement une protection résistante au phishing : l'amélioration réduit certains risques sans remplacer un protocole cryptographique lié au site attendu.

### 8.4. Réagir à une demande inattendue

Refuse la demande, ne communique aucun code, consulte le compte par le canal officiel et examine les activités récentes. Si une compromission est suspectée, change les identifiants, révoque les sessions ou facteurs suspects selon la procédure et signale l'incident à l'équipe de sécurité.

Ne traite pas la notification inattendue comme un problème que tu dois faire disparaître en appuyant sur « Autoriser ».

## 9. Clés de sécurité et passkeys

### 9.1. Clé de sécurité

Une clé de sécurité est un dispositif capable de réaliser des opérations cryptographiques pendant l'authentification. Certaines utilisent des protocoles FIDO2 et WebAuthn. Au lieu de transmettre simplement un code que l'utilisateur peut recopier sur un faux site, une méthode résistante au phishing lie la réponse cryptographique au service auquel l'utilisateur tente réellement de s'authentifier.

La clé publique est enregistrée par le service ; le secret cryptographique correspondant reste protégé par l'authentificateur.

### 9.2. Principe de WebAuthn

**Schéma pédagogique — Une passkey est liée à une origine et limite l'envoi d'un secret réutilisable à un faux domaine.**

~~~text
[Site legitime] --> challenge --> [Navigateur]
                                  |
                                  v
                           [Authentificateur]
                           cle privee locale
                                  |
                       signature du challenge
                                  |
                                  v
[Serveur verifie la signature avec la cle publique enregistree]

Le navigateur verifie aussi l'origine dans le mecanisme WebAuthn.
~~~


Lors de l'inscription, un authentificateur crée généralement une paire de clés associée au compte et au service. La clé publique est enregistrée par le service, tandis que le secret privé est conservé par l'authentificateur. Lors d'une connexion, le service présente un défi cryptographique ; l'authentificateur produit une réponse vérifiable avec la clé publique.

Le protocole inclut des informations liées à l'origine et au contexte. Cela contribue à empêcher qu'une réponse destinée à un faux site soit réutilisée comme si elle avait été produite pour le domaine légitime. Le résultat dépend du protocole, du navigateur, de l'authentificateur et de la mise en œuvre.

### 9.3. Pourquoi cette méthode résiste mieux au phishing

Avec un mot de passe ou un code saisi manuellement, un faux site peut essayer de récupérer la valeur et de la transmettre au service légitime. Avec WebAuthn correctement mis en œuvre, la réponse cryptographique est liée au contexte du site. Un faux domaine ne peut normalement pas demander une réponse valable pour le domaine attendu simplement en connaissant le mot de passe.

Cette protection ne supprime pas les risques liés à un appareil compromis, à une procédure de récupération faible ou à une mauvaise gestion du compte.

### 9.4. Qu'est-ce qu'une passkey ?

Une passkey est un authentificateur fondé sur des clés cryptographiques, conçu pour offrir une connexion pratique et résistante au phishing sur les services compatibles. Elle peut être utilisée sur un appareil ou, selon la configuration, être synchronisée entre des appareils associés au compte.

L'authentification peut nécessiter le déverrouillage local de l'appareil par un PIN ou une biométrie. Une passkey n'est donc pas simplement un mot de passe mémorisé.

### 9.5. Biométrie et passkeys

Lorsque l'utilisateur utilise une empreinte ou son visage pour activer l'authentificateur local, le mécanisme biométrique sert généralement à autoriser l'utilisation de la clé sur l'appareil. Cela ne signifie pas nécessairement que le site reçoit l'image de l'empreinte ou du visage. Le protocole et l'appareil déterminent les informations utilisées et transmises.

### 9.6. Perte d'appareil et récupération

Une passkey ne supprime pas toutes les difficultés de gestion de compte. L'utilisateur peut perdre un appareil, changer de téléphone ou perdre l'accès au gestionnaire de passkeys. Il faut connaître les moyens de récupération proposés, conserver les solutions de secours de manière sûre et retirer les authentificateurs qui ne sont plus contrôlés.

Pour un compte professionnel, l'organisation doit définir les appareils autorisés, la vérification nécessaire à l'inscription d'un nouvel appareil et la procédure de révocation.

## 10. Comparer les méthodes

| Méthode | Atout principal | Limite importante |
|---|---|---|
| Mot de passe seul | Simple, largement pris en charge | Vol, réutilisation et phishing |
| Mot de passe + SMS | Facile à comprendre | Fraude SIM et relais des codes |
| Mot de passe + application OTP | Pas de SMS nécessaire à chaque connexion | Code saisissable et relayable |
| Notification d'approbation | Parcours simple | Fatigue MFA et validation accidentelle |
| Clé FIDO2/WebAuthn | Forte résistance au phishing si correctement mise en œuvre | Provisionnement et récupération à organiser |
| Passkey | Connexion pratique par clés cryptographiques | Gestion des appareils, synchronisation et récupération |
| Certificat ou dispositif matériel | Peut répondre à des exigences élevées | Gestion du cycle de vie et du support plus complexe |

Ce tableau n'est pas un classement absolu pour tous les environnements. Le choix dépend de la valeur du compte, des applications, des capacités des utilisateurs, des contraintes opérationnelles et des exigences applicables.

## 11. Les attaques qui ciblent la MFA

### 11.1. Phishing classique

L'attaquant crée une page ressemblant au service officiel et demande les identifiants. Il peut ensuite tenter d'utiliser les informations volées sur le vrai site. La formation des utilisateurs aide, mais ne doit pas être le seul contrôle. Les méthodes résistantes au phishing réduisent la dépendance à la capacité de détecter un faux site.

### 11.2. Phishing en temps réel

Dans une attaque de relais, l'attaquant agit comme un intermédiaire entre l'utilisateur et le service légitime. L'utilisateur peut voir une page qui semble fonctionner normalement tandis que l'attaquant transmet les identifiants ou codes au vrai service. Un code temporaire peut être valide et néanmoins relayé.

C'est pourquoi une MFA qui exige simplement de saisir un code ne constitue pas nécessairement une protection contre le phishing.

### 11.3. Fraude au remplacement de SIM

L'attaquant tente de faire transférer le numéro de la victime vers une SIM qu'il contrôle. Si le service utilise les SMS, l'attaquant peut alors recevoir les codes selon les circonstances et les contrôles de l'opérateur.

Les utilisateurs doivent protéger leur compte auprès de l'opérateur et les organisations éviter de dépendre exclusivement du SMS pour les comptes à haut risque si de meilleures méthodes sont disponibles.

### 11.4. Vol de session

Après une authentification réussie, le serveur peut émettre un identifiant de session ou un jeton. Si un attaquant récupère un jeton valide, il peut parfois agir comme l'utilisateur sans repasser immédiatement par la MFA.

Le vol peut résulter d'une compromission de l'appareil, d'une fuite de jeton, d'une faille applicative ou d'une mauvaise configuration. La MFA seule ne protège donc pas tous les usages d'une session active.

### 11.5. Vol de cookies

Dans de nombreuses applications Web, un cookie permet de maintenir la session. S'il est volé, un attaquant peut parfois réutiliser la session. Les applications doivent protéger les cookies, utiliser HTTPS et choisir des attributs comme Secure, HttpOnly et SameSite selon le scénario. Elles doivent aussi prévoir l'expiration, la révocation et le renouvellement des sessions.

Les développeurs devraient préférer les mécanismes de session pris en charge par leur framework plutôt qu'un système artisanal.

### 11.6. Compromission de l'appareil

Si un appareil est compromis, un attaquant peut observer les saisies, utiliser une session ouverte ou abuser d'un authentificateur accessible. La protection des comptes doit être accompagnée de mises à jour, de verrouillage d'écran, du chiffrement lorsque pertinent et de la gestion des appareils professionnels.

### 11.7. Ingénierie sociale auprès du support

Un attaquant peut convaincre un agent de retirer un facteur, de réinitialiser un compte ou de modifier les informations de récupération. Si le support se contente d'une information facile à trouver, il peut accorder l'accès à la mauvaise personne.

Les organisations doivent définir une procédure de vérification, limiter les personnes autorisées à réaliser ces changements et journaliser les opérations.

## 12. Récupération des comptes

### 12.1. Pourquoi est-ce critique ?

L'utilisateur peut perdre son téléphone, casser sa clé, oublier son mot de passe ou perdre l'accès à son adresse de récupération. Le système doit permettre de retrouver l'accès sans créer une voie simple pour les attaquants.

La récupération peut devenir le point faible d'une architecture équipée d'une MFA solide. Il faut donc traiter ce processus comme une fonction sensible.

### 12.2. Coordonnées de récupération

Une adresse électronique ou un numéro de téléphone peuvent servir à confirmer une demande. Ils doivent être protégés et mis à jour lorsque l'utilisateur change de coordonnées. Toute modification devrait suivre une procédure adaptée au risque. Pour les comptes sensibles, le système peut exiger une réauthentification, appliquer un délai ou avertir les canaux précédemment associés.

### 12.3. Questions secrètes

Les questions telles que « Quel est le nom de jeune fille de votre mère ? » reposent souvent sur des informations connues ou trouvables publiquement. Elles ne doivent pas être considérées comme une preuve forte d'identité pour récupérer un compte sensible.

Un processus robuste utilise des méthodes adaptées au risque et évite de remplacer une MFA forte par une question facile à deviner.

### 12.4. Retirer un authentificateur perdu

Quand un dispositif est perdu, l'organisation doit pouvoir retirer l'authentificateur qui n'est plus sous le contrôle de l'utilisateur. La procédure vérifie la demande, révoque le facteur concerné, inscrit le nouveau facteur de manière sûre et examine les activités suspectes si nécessaire.

Il peut aussi être utile d'invalider certaines sessions. Les opérations précises dépendent du type de compte et du risque.

### 12.5. Récupération d'un administrateur

Un compte administrateur exige davantage de précautions qu'un compte ordinaire. Il faut prévoir un processus d'urgence documenté, une vérification d'identité adaptée, une séparation des rôles et une journalisation.

Les mécanismes de secours ne doivent pas dépendre d'un seul employé, mais ne doivent pas non plus être exploitables par quiconque prétend avoir perdu son téléphone.

## 13. Sessions après la connexion

### 13.1. Pourquoi créer une session ?

Sans session, l'application devrait souvent demander les facteurs à chaque requête. Une session permet au serveur de reconnaître un utilisateur qui s'est déjà authentifié dans un contexte donné. Elle ne doit pas être confondue avec le mot de passe : elle possède son propre cycle de vie et ses propres risques.

### 13.2. Expiration et réauthentification

Une session peut expirer après une période d'inactivité ou une durée maximale. Le système peut aussi demander une réauthentification avant une action sensible, comme changer un mot de passe, ajouter un facteur, modifier l'adresse de récupération, créer un administrateur ou exporter des données sensibles.

La réauthentification doit être proportionnée au risque et expliquée à l'utilisateur.

### 13.3. Renouvellement de l'identifiant

Lorsqu'un utilisateur passe de l'état non authentifié à une session authentifiée, une application doit gérer correctement l'identifiant de session pour éviter certains scénarios de fixation de session. Les frameworks proposent généralement des mécanismes pour renouveler ou invalider les sessions ; il est préférable de les utiliser plutôt que de construire une solution artisanale.

### 13.4. Déconnexion et révocation

**Schéma pédagogique — Une session active est distincte du mot de passe et peut nécessiter une révocation explicite.**

~~~text
Connexion + MFA
      |
      v
[Session / cookie / jeton]
      |
      +--> requetes authentifiees
      |
      +--> expiration
      |
      +--> deconnexion / revocation cote serveur
      |
      +--> reauthentification si action sensible

Changer le mot de passe ne garantit pas l'invalidation de toutes les sessions.
~~~


Se déconnecter dans un navigateur doit invalider la session selon le fonctionnement de l'application. Fermer un onglet n'a pas nécessairement le même effet. Les services sensibles doivent prévoir comment révoquer une session depuis le serveur, fermer les sessions d'un appareil perdu et traiter les jetons devenus invalides.

Après un changement de mot de passe ou une suspicion de compromission, il peut être nécessaire de fermer les sessions actives selon la politique.

## 14. SSO et fédération d'identité

### 14.1. Single Sign-On

Le SSO permet à un utilisateur de s'authentifier auprès d'un fournisseur d'identité puis d'accéder à plusieurs applications compatibles, selon les règles de confiance et les autorisations établies.

Au lieu de gérer indépendamment un mot de passe pour chaque application, l'organisation centralise une partie de la gestion de l'identité.

### 14.2. Avantages

Le SSO peut faciliter le contrôle centralisé des comptes, l'application cohérente de la MFA, le retrait rapide des accès après le départ d'un employé, la réduction de la réutilisation des mots de passe et la surveillance des connexions. Les bénéfices dépendent d'une configuration correcte et d'une gestion efficace du fournisseur d'identité.

### 14.3. Le point central de confiance

Si le fournisseur d'identité est compromis, l'attaquant peut atteindre plusieurs applications qui lui font confiance. Le fournisseur doit donc être particulièrement bien protégé : MFA robuste, contrôle des administrateurs, surveillance, récupération sécurisée et plan d'urgence.

### 14.4. Le SSO ne donne pas une autorisation universelle

Chaque application doit appliquer ses permissions. Le fait que l'utilisateur ait réussi une authentification auprès du fournisseur d'identité ne signifie pas qu'il doit devenir administrateur de toutes les applications. Les rôles et attributs transmis doivent être validés selon la configuration prévue.

### 14.5. Cycle de vie des comptes

Lorsqu'un employé rejoint l'entreprise, change de fonction ou la quitte, ses accès doivent être ajustés. La fermeture d'un compte dans le fournisseur d'identité ne garantit pas que toutes les sessions externes et tous les jetons soient déjà révoqués si les systèmes ne sont pas synchronisés.

Il faut tester le processus et retirer les accès locaux, les clés API et les comptes qui ne sont pas gérés directement par le SSO.

## 15. Authentification adaptative et comptes sensibles

### 15.1. L'authentification adaptative

Un système peut adapter les contrôles à certains signaux de risque, par exemple demander une réauthentification lorsqu'un appareil inconnu accède à un compte sensible. Ces signaux ne sont pas des preuves absolues : une adresse IP inhabituelle peut être légitime, notamment lorsqu'un utilisateur voyage ou change de réseau.

### 15.2. Signaux à examiner

Selon le service, on peut examiner une connexion depuis un nouvel appareil, des échecs répétés, des changements de récupération, une demande de privilèges, l'inscription d'un authentificateur ou une activité anormale après la connexion.

La décision doit tenir compte du risque et éviter de bloquer automatiquement un utilisateur légitime sur la base d'un signal isolé.

### 15.3. Comptes administrateurs

Les comptes administrateurs peuvent modifier les droits, gérer les données et influencer la sécurité des autres utilisateurs. Ils méritent des contrôles renforcés : comptes individuels, MFA robuste, séparation entre compte quotidien et compte privilégié, limitation des droits et de la durée d'accès, journalisation, réauthentification pour les opérations critiques et récupération documentée.

### 15.4. Comptes de service

Un compte de service est utilisé par une application ou un processus. Il peut s'authentifier avec un secret, un certificat, un jeton ou un autre mécanisme machine-à-machine. La MFA traditionnelle destinée à un humain ne convient pas directement à tous ces scénarios.

Il faut utiliser des identités techniques adaptées, limiter les permissions, protéger les secrets et organiser leur rotation. Les clés API ne doivent pas être placées dans un dépôt public ou un fichier accessible sans contrôle.

## 16. TP : réaliser un audit simple d'authentification

### 16.1. Objectif et périmètre

Choisis un environnement de test que tu administres ou sur lequel tu disposes d'une autorisation explicite. N'essaie pas de contourner les contrôles d'un système réel. Identifie les comptes ordinaires, les comptes d'administration et les méthodes de récupération.

### 16.2. Examiner les méthodes disponibles

Documente les méthodes prises en charge : mot de passe seul, SMS, application OTP, passkey, clé de sécurité ou fournisseur d'identité. Note les méthodes réellement activées et celles qui ne sont proposées qu'en secours.

N'active pas une méthode sur un compte de production sans comprendre la procédure de récupération ; privilégie un compte de test.

### 16.3. Vérifier l'inscription

La méthode la plus forte peut être affaiblie si un attaquant peut ajouter son propre facteur simplement en connaissant un mot de passe compromis. Vérifie que l'inscription exige une vérification adaptée, que les changements sensibles sont notifiés lorsque le système le permet et que les authentificateurs inconnus peuvent être retirés.

### 16.4. Tester une connexion normale

Réalise une connexion avec le compte de test et note l'identification, le premier facteur, le facteur supplémentaire, la création de session et les ressources auxquelles le compte a accès.

### 16.5. Tester le refus

Dans l'environnement de test, utilise volontairement un facteur incorrect ou refuse une demande. Vérifie que le système n'accorde pas l'accès. Ne réalise pas de tentatives automatisées contre un service réel.

### 16.6. Examiner la récupération et les sessions

Vérifie le parcours de récupération, la protection des codes de secours, l'affichage des sessions actives, la possibilité de révoquer une session et le retrait d'un facteur perdu. Documente ce qui existe et ce qui manque plutôt que de supposer que tous les contrôles sont disponibles.

### 16.7. Tableau de constats

| Point contrôlé | Observation à faire | Risque potentiel | Amélioration possible |
|---|---|---|---|
| Mots de passe uniques | Vérifier la politique | Réutilisation après une fuite | Gestionnaire et contrôle des secrets compromis |
| MFA activée | Vérifier selon le rôle | Vol d'identifiants | MFA adaptée au risque |
| Méthode résistante au phishing | Vérifier la disponibilité | Relais des codes | Passkey ou clé compatible |
| Ajout d'un facteur | Tester en compte de test | Enrôlement frauduleux | Réauthentification et notification |
| Récupération du compte | Documenter le parcours | Contournement des facteurs | Procédure robuste |
| Révocation des sessions | Tester si disponible | Session volée encore active | Gestion et invalidation des sessions |
| Comptes administrateurs | Inventorier les comptes | Privilèges excessifs | Comptes dédiés et MFA forte |

## 17. TP : concevoir une politique MFA pour Skill-Tree

### 17.1. Scénario

Skill-Tree possède des apprenants qui consultent les cours et passent les quiz, des formateurs qui publient les leçons, des responsables qui gèrent le catalogue, des administrateurs qui modifient les permissions et des comptes techniques pour les intégrations.

L'objectif est de choisir des contrôles réalistes sans imposer le même dispositif à tous les usages.

### 17.2. Classer les comptes selon l'impact

Pour un apprenant, un attaquant pourrait accéder à l'historique et modifier certaines informations. Pour un administrateur, il pourrait créer des comptes privilégiés, modifier des contenus, consulter des données ou changer la configuration. Le risque est généralement plus élevé pour les comptes privilégiés.

### 17.3. Choisir les contrôles

Les apprenants devraient avoir des mots de passe uniques et une récupération sûre ; l'organisation peut proposer ou exiger la MFA selon le risque. Les formateurs doivent bénéficier de contrôles plus forts en raison des permissions de publication. Les administrateurs doivent utiliser des comptes individuels, une MFA robuste, une inscription contrôlée des facteurs, une réauthentification pour les opérations critiques et une journalisation.

Les comptes techniques doivent utiliser des identités machine-à-machine, des secrets à portée limitée, un stockage protégé et une rotation adaptée.

### 17.4. Sécuriser l'inscription et la récupération

Lorsqu'un utilisateur ajoute une méthode MFA, il faut vérifier qu'il contrôle déjà le compte selon une procédure adaptée. Les changements sensibles devraient être enregistrés et notifiés lorsque cela convient. La récupération doit préciser comment vérifier l'identité, qui autorise l'opération, comment révoquer le facteur perdu et quelles sessions doivent être fermées.

### 17.5. Définir la réauthentification et la surveillance

La plateforme peut demander une nouvelle vérification avant un changement de mot de passe, d'authentificateur, de permissions ou d'informations de récupération. Les événements importants comprennent les connexions, les échecs, l'ajout et le retrait de facteurs, la récupération, les changements de privilèges et les fermetures de session.

La collecte doit être proportionnée et protégée. Les journaux ne doivent pas contenir des mots de passe, codes temporaires réutilisables ou clés privées.

### 17.6. Indicateurs

L'équipe peut suivre le pourcentage de comptes sensibles protégés par la MFA attendue, le nombre de comptes administrateurs sans méthode forte, le délai de retrait des accès au départ d'un employé, les échecs d'inscription, les récupérations de compte et les sessions suspectes examinées.

Un indicateur ne suffit pas à démontrer la sécurité. Il doit être interprété selon le contexte et complété par des tests.

## 18. Erreurs fréquentes à éviter

### Erreur 1 — Deux secrets connus seraient une MFA

Deux mots de passe restent deux facteurs de la même catégorie.

**Correction :** identifier les catégories réellement utilisées.

### Erreur 2 — Réutiliser le mot de passe

Une fuite sur un service peut exposer plusieurs comptes.

**Correction :** employer des mots de passe uniques et un gestionnaire adapté.

### Erreur 3 — Confondre code temporaire et résistance au phishing

Un code à durée limitée peut encore être relayé.

**Correction :** privilégier une méthode résistante au phishing lorsque le risque le justifie.

### Erreur 4 — Approuver toutes les notifications

Une demande inattendue peut venir d'un attaquant.

**Correction :** refuser la demande non initiée et examiner l'activité du compte.

### Erreur 5 — Oublier la récupération

Un parcours faible peut annuler la valeur de la MFA.

**Correction :** sécuriser les coordonnées, les codes de secours et les vérifications du support.

### Erreur 6 — Croire que la MFA protège automatiquement une session volée

Une session valide peut parfois être réutilisée sans nouvelle authentification.

**Correction :** protéger les jetons, limiter la durée, permettre la révocation et réauthentifier les actions sensibles.

### Erreur 7 — Utiliser un compte administrateur pour tout

Une compromission peut donner accès à des privilèges excessifs.

**Correction :** séparer les comptes ordinaires et privilégiés, et limiter les permissions.

### Erreur 8 — Envoyer les codes de secours par courriel ordinaire

Les codes peuvent être interceptés ou retrouvés par un attaquant qui contrôle la messagerie.

**Correction :** conserver les codes selon les modalités sûres prévues par le service.

### Erreur 9 — Croire que la biométrie résout tout

La protection dépend du capteur, du mécanisme et de l'architecture.

**Correction :** comprendre le rôle exact de la biométrie et de l'authentificateur.

### Erreur 10 — Désactiver la MFA parce qu'elle est contraignante

Une méthode mal adaptée peut frustrer l'utilisateur, mais sa désactivation peut exposer les comptes.

**Correction :** améliorer l'expérience et la récupération tout en conservant les contrôles requis.

### Erreur 11 — Considérer la connexion comme une autorisation universelle

Un utilisateur authentifié n'est pas nécessairement autorisé à chaque action.

**Correction :** contrôler les droits pour chaque opération sensible.

### Erreur 12 — Supposer qu'une connexion réussie prouve l'absence de compromission

La session peut avoir été volée ou l'appareil compromis.

**Correction :** examiner le contexte et les signaux pertinents en cas d'activité suspecte.

## 19. Exercices avec corrections

### Exercice 1 — Identifier les étapes

Une application demande un identifiant, un mot de passe, puis vérifie si le compte peut consulter un document réservé aux formateurs. Quelle proposition est correcte ?

A. Identifiant et autorisation sont identiques.  
B. Le mot de passe est une permission.  
C. L'authentification vérifie les facteurs ; l'autorisation détermine les actions permises.  
D. Tout utilisateur authentifié doit accéder à toutes les ressources.

**Correction : C.** L'identification désigne le compte, l'authentification vérifie les facteurs et l'autorisation détermine les actions permises.

### Exercice 2 — Reconnaître une MFA

Un système demande deux mots de passe successifs. S'agit-il nécessairement d'une MFA ?

A. Oui, car deux écrans apparaissent.  
B. Oui, si le second secret contient des chiffres.  
C. Non, car deux mots de passe appartiennent à la catégorie des secrets connus.  
D. Non, car un mot de passe n'est jamais un facteur.

**Correction : C.** Une MFA exige des facteurs de catégories différentes, pas seulement plusieurs secrets.

### Exercice 3 — Protéger un compte sensible

Une organisation veut réduire le risque de phishing contre les comptes administrateurs. Quel choix est généralement préférable si l'environnement le permet ?

A. Mot de passe seul.  
B. Code SMS uniquement.  
C. Authentification cryptographique résistante au phishing, telle que FIDO2/WebAuthn correctement configurée.  
D. Deux mots de passe.

**Correction : C.** Une méthode résistante au phishing est préférable lorsque les exigences et le système le permettent. Inscription, récupération et protection du compte restent nécessaires.

### Exercice 4 — Demandes inattendues

Tu reçois cinq demandes de validation alors que tu ne t'es pas connecté. Que faire ?

A. En approuver une pour faire cesser les notifications.  
B. Les approuver si elles arrivent rapidement.  
C. Les refuser, protéger le compte et signaler les tentatives selon la procédure.  
D. Envoyer le code reçu à un collègue.

**Correction : C.** Les demandes inattendues peuvent signaler une tentative d'accès. Il ne faut ni les approuver ni divulguer les codes.

### Exercice 5 — Limites du SMS

Pourquoi les SMS sont-ils généralement moins adaptés qu'une méthode résistante au phishing pour un compte très sensible ?

A. Un SMS est toujours public.  
B. Un code saisi manuellement peut être détourné ou relayé, et le numéro peut faire l'objet d'une fraude.  
C. Un code SMS n'a jamais de durée de validité.  
D. Les SMS ne peuvent jamais être utilisés pour authentifier.

**Correction : B.** Le SMS peut ajouter une protection utile, mais il présente des limites spécifiques.

### Exercice 6 — Téléphone perdu

Un administrateur perd le téléphone qui sert de facteur MFA. Quelle réponse est la plus adaptée ?

A. Désactiver définitivement la MFA de tous les comptes.  
B. Envoyer ses identifiants à un collègue.  
C. Appliquer la procédure de récupération, révoquer le facteur perdu, vérifier la demande et inscrire un nouveau facteur de manière sûre.  
D. Utiliser le compte d'un autre administrateur.

**Correction : C.** La récupération doit protéger l'identité tout en permettant le rétablissement de l'accès.

### Exercice 7 — Session volée

Un attaquant vole un cookie de session authentifiée. Pourquoi la MFA ne suffit-elle pas nécessairement à l'arrêter ?

A. La MFA ne fonctionne que sur téléphone.  
B. Un cookie valide peut permettre de réutiliser une session sans repasser par la MFA.  
C. Le cookie contient toujours le mot de passe en clair.  
D. Une session n'a aucun rapport avec l'authentification.

**Correction : B.** La session est distincte de l'authentification initiale. Les jetons doivent être protégés, limités et révocables.

### Exercice 8 — Compte administrateur

Pourquoi séparer un compte quotidien et un compte d'administration ?

A. Pour multiplier les mots de passe sans raison.  
B. Pour réduire l'exposition des privilèges élevés aux tâches ordinaires.  
C. Parce qu'un administrateur ne doit jamais utiliser de MFA.  
D. Pour ne pas enregistrer les activités d'administration.

**Correction : B.** La séparation réduit le risque lié à une compromission de l'environnement quotidien.

### Exercice 9 — Passkey

Une passkey fonctionne correctement sur un appareil. Quelle affirmation est la plus exacte ?

A. Elle prouve que le logiciel utilisé ne contient aucune vulnérabilité.  
B. Elle protège automatiquement tous les comptes de l'utilisateur.  
C. Elle réalise une authentification cryptographique selon le protocole, mais la sécurité dépend aussi de l'appareil, du compte et de la récupération.  
D. Elle est identique à un code SMS.

**Correction : C.** Une passkey améliore le mécanisme d'authentification, mais n'élimine pas les autres risques.

### Exercice 10 — Récupération frauduleuse

Le support reçoit un appel d'une personne affirmant avoir perdu son téléphone et demandant le retrait immédiat de la MFA d'un compte administrateur. Quelle action est correcte ?

A. Retirer la MFA dès que la personne connaît le nom du compte.  
B. Envoyer un code au numéro donné pendant l'appel.  
C. Appliquer la procédure renforcée de vérification et consigner l'opération.  
D. Créer un compte administrateur partagé.

**Correction : C.** Le support est une cible potentielle d'ingénierie sociale. Une récupération sensible exige une procédure documentée et vérifiable.

## 20. Défi final — Protéger les accès d'une entreprise

### 20.1. Scénario

NovaLearn gère une plateforme de formation comprenant des apprenants, des formateurs, quatre administrateurs et plusieurs intégrations. Certains utilisateurs réutilisent leurs mots de passe. La MFA est activée pour quelques administrateurs seulement. Les codes SMS servent de facteur supplémentaire pour plusieurs comptes. Un administrateur utilise le même compte au quotidien et pour les opérations privilégiées. La récupération repose principalement sur l'adresse électronique. Les utilisateurs ne savent pas comment réagir aux demandes inattendues et certaines sessions restent actives sur des appareils perdus. Les comptes techniques utilisent des secrets copiés manuellement dans plusieurs fichiers.

### 20.2. Travail demandé

Construis un plan qui comprend une politique de mots de passe, une stratégie MFA par type de compte, des mesures contre le phishing et la fatigue MFA, une procédure de récupération, une gestion des sessions, une politique de comptes administrateurs, des contrôles pour les comptes techniques et des indicateurs de suivi.

### 20.3. Correction détaillée

**Réduire les risques liés aux mots de passe.** L'entreprise doit encourager des mots de passe uniques et longs, faciliter l'utilisation d'un gestionnaire et éviter les changements périodiques arbitraires. Elle doit appliquer des contrôles adaptés aux secrets compromis, limiter les essais automatisés et protéger le stockage des vérificateurs.

**Déployer une MFA adaptée au risque.** Les administrateurs devraient utiliser une méthode forte et résistante au phishing lorsque compatible. Les formateurs devraient bénéficier de contrôles renforcés selon leurs permissions. Pour les apprenants, la politique doit tenir compte des données et actions disponibles tout en conservant une expérience utilisable.

**Ne pas dépendre exclusivement des SMS pour les comptes sensibles.** Le SMS peut être conservé comme solution de secours si le contexte le justifie, mais les comptes à fort impact devraient disposer d'une méthode plus résistante au phishing lorsque possible.

**Protéger l'inscription et le retrait des facteurs.** L'ajout d'un authentificateur ne doit pas être possible uniquement à partir d'un mot de passe compromis. Le processus doit utiliser une vérification adaptée, notifier l'utilisateur lorsque cela est pertinent et permettre de retirer les facteurs perdus ou suspects.

**Améliorer la récupération.** L'adresse électronique ne doit pas nécessairement être le seul contrôle pour restaurer un compte sensible. L'entreprise doit définir les preuves requises, une procédure distincte pour les administrateurs et une gestion sûre des codes de secours.

**Gérer les sessions.** L'entreprise doit définir une durée d'expiration adaptée, permettre la révocation lorsque nécessaire et fermer les sessions d'un appareil perdu. Une réauthentification peut être requise avant des changements sensibles.

**Séparer les comptes privilégiés.** Les administrateurs doivent avoir des comptes individuels, limiter l'utilisation des privilèges aux tâches nécessaires et enregistrer les opérations. Un compte partagé réduit la traçabilité.

**Gérer les comptes techniques séparément.** Les intégrations doivent utiliser des identités techniques adaptées, des permissions minimales et des secrets conservés dans un stockage approprié. Il faut éviter les secrets en clair dans plusieurs fichiers et planifier leur rotation.

**Former les utilisateurs et tester.** La formation doit expliquer les demandes inattendues, les faux sites, la divulgation des codes et le signalement. L'équipe doit mesurer la couverture MFA, tester la récupération en compte de test, vérifier la révocation des sessions et examiner les comptes privilégiés.

### 20.4. Priorisation réaliste

- **Priorité 1 :** protéger les administrateurs, supprimer les comptes partagés, sécuriser la récupération et fermer les sessions qui ne devraient plus être actives.
- **Priorité 2 :** étendre la MFA selon le risque, promouvoir les gestionnaires de mots de passe et sécuriser l'inscription des facteurs.
- **Priorité 3 :** adopter des méthodes résistantes au phishing, améliorer les journaux et détecter les activités inhabituelles.
- **Priorité 4 :** tester régulièrement les procédures et réexaminer les exceptions.

Cette priorisation est un point de départ. L'organisation doit tenir compte de ses obligations, de ses applications et des résultats réels des tests.

### 20.5. Critères d'évaluation

Tu as réussi si tu peux expliquer pourquoi la MFA doit être adaptée au risque, pourquoi deux mots de passe ne constituent pas une MFA, pourquoi la résistance au phishing est importante pour les comptes sensibles, comment récupérer un compte sans créer une voie d'attaque, pourquoi une session volée peut contourner la connexion initiale, et comment séparer les comptes utilisateurs, administrateurs et techniques.

## 21. Synthèse du cours

L'authentification vérifie le contrôle des moyens d'accès associés à une identité. Elle doit être distinguée de l'identification, qui indique le compte visé, et de l'autorisation, qui détermine les actions permises.

Les facteurs appartiennent à trois catégories : connaissance, possession et inhérence. Une MFA combine des catégories différentes. Deux mots de passe ne suffisent donc pas. Les mots de passe uniques et robustes restent importants, mais peuvent être volés ou divulgués. Un gestionnaire réduit la réutilisation et simplifie la création de secrets.

La MFA ajoute une couche de protection, mais son efficacité dépend de la méthode choisie. Les SMS, les applications OTP et les notifications peuvent aider, mais ont des limites. Un code saisi manuellement peut être relayé et une notification peut être approuvée par erreur. Les mécanismes cryptographiques résistants au phishing, tels que FIDO2/WebAuthn, offrent une protection plus forte contre certaines attaques par imitation de site.

Les passkeys utilisent des clés cryptographiques. Leur déploiement doit inclure inscription, gestion des appareils et récupération. La protection ne s'arrête pas à la connexion : une session peut être volée et les jetons, cookies, durées, réauthentifications et révocations doivent être correctement gérés.

La récupération des comptes est une composante essentielle. Il faut empêcher un attaquant de remplacer un facteur ou de restaurer un compte avec des informations faciles à obtenir. Les comptes administrateurs et techniques nécessitent des contrôles distincts, des droits limités et une surveillance appropriée.

## 22. Glossaire

**Authentification :** vérification des preuves permettant d'établir le contrôle des moyens d'accès associés à un compte.

**Autorisation :** décision qui détermine quelles actions une identité authentifiée peut effectuer.

**Biométrie :** utilisation de caractéristiques physiques ou comportementales pour l'authentification ou l'activation d'un authentificateur.

**Code à usage unique (OTP) :** code destiné à une étape d'authentification, souvent de validité limitée.

**Compte de service :** identité utilisée par une application ou un processus pour s'authentifier auprès d'un autre système.

**Credential stuffing :** attaque qui réutilise des identifiants volés sur d'autres services.

**Facteur d'authentification :** élément d'une catégorie de preuve utilisé pour authentifier un utilisateur.

**FIDO2 :** ensemble de standards d'authentification comprenant WebAuthn et des mécanismes associés aux authentificateurs.

**Gestionnaire de mots de passe :** outil qui conserve et génère des secrets dans un coffre protégé.

**Hameçonnage :** tentative de tromper une personne afin d'obtenir des informations, des codes ou une action.

**Identification :** action qui indique quelle identité ou quel compte est utilisé.

**MFA :** authentification multifacteur qui exige des facteurs de catégories différentes.

**Passkey :** authentificateur fondé sur des clés cryptographiques, conçu pour une connexion pratique et résistante au phishing dans les systèmes compatibles.

**Réauthentification :** nouvelle vérification demandée avant certaines actions sensibles.

**Récupération de compte :** procédure permettant de retrouver l'accès après la perte d'un facteur ou autre moyen d'authentification.

**Session :** état conservé par une application pour reconnaître un utilisateur déjà authentifié.

**SSO :** authentification unique qui permet d'utiliser une authentification centralisée pour accéder à plusieurs applications compatibles.

**TOTP :** méthode de génération de codes temporaires reposant sur un secret partagé et le temps.

**WebAuthn :** standard Web permettant notamment l'authentification par clé publique avec des authentificateurs compatibles.

**Vol de session :** attaque consistant à obtenir un moyen de réutiliser une session déjà authentifiée.

## 23. Ressources pour approfondir

- **NIST — SP 800-63B-4, Digital Identity Guidelines: Authentication and Authenticator Management :** recommandations sur les facteurs, les méthodes d'authentification et la résistance au phishing.  
  https://pages.nist.gov/800-63-4/sp800-63b.html

- **OWASP — Authentication Cheat Sheet :** recommandations pratiques pour la conception et la mise en œuvre de l'authentification.  
  https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

- **OWASP — Multifactor Authentication Cheat Sheet :** conseils sur le choix et le déploiement de la MFA.  
  https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html

- **OWASP — Session Management Cheat Sheet :** recommandations sur les sessions et leur invalidation.  
  https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

- **W3C — Web Authentication (WebAuthn) :** référence technique du standard WebAuthn.  
  https://www.w3.org/TR/webauthn-3/

- **FIDO Alliance — Passkeys :** explications sur les passkeys et l'authentification par clés publiques.  
  https://fidoalliance.org/passkeys/

- **CISA — Implementing Phishing-Resistant MFA :** guide sur le déploiement d'une authentification résistante au phishing.  
  https://www.cisa.gov/resources-tools/resources/implementing-phishing-resistant-mfa

La sécurité ne dépend pas uniquement de l'existence d'une MFA. Il faut examiner le type de facteur, son inscription, sa récupération, la protection des sessions, les privilèges et la capacité de l'organisation à détecter puis traiter les incidents.

**Fin du cours : Authentification et MFA.**