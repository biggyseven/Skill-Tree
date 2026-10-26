# Hachage et signatures

> **Encadré de mise en contexte**
>
> Tu travailles comme technicien informatique dans une entreprise qui développe une plateforme de formation. L'équipe publie régulièrement des mises à jour, des supports PDF, des scripts d'administration et des fichiers de configuration. Les apprenants téléchargent ces fichiers depuis le site de l'entreprise, tandis que les techniciens les installent sur les postes et les serveurs.
>
> Un matin, un administrateur reçoit un fichier d'installation transmis par un collègue. Le nom semble correct, mais le fichier a-t-il été modifié pendant le transfert ? Est-ce réellement la version publiée par l'équipe de développement ? Peut-on démontrer que le fichier provient du bon éditeur ? Un simple nom de fichier ou une taille identique ne suffit pas pour répondre.
>
> Un autre problème apparaît : une sauvegarde contient des empreintes de fichiers, mais personne ne sait expliquer ce que ces empreintes prouvent réellement. Certains pensent qu'un hachage valide garantit que le fichier est sûr. D'autres croient qu'une signature numérique chiffre automatiquement le document.
>
> Ce cours t'apprend à distinguer hachage, HMAC, signature numérique et vérification d'identité. Tu vas calculer des empreintes, vérifier des fichiers et comprendre les limites de ces mécanismes. Une empreinte n'identifie pas à elle seule son auteur ; une signature mathématiquement valide ne garantit pas que son contenu est sûr.

## 1. Objectifs du cours

À la fin du cours, tu devras être capable de définir une fonction de hachage cryptographique et une empreinte ; expliquer la résistance à la préimage, à la seconde préimage et aux collisions ; distinguer hachage, encodage, chiffrement, HMAC et signature numérique ; vérifier l'intégrité d'un fichier sous Windows ou Linux ; interpréter correctement une différence d'empreinte ; comprendre le rôle d'une clé privée et d'une clé publique ; vérifier une signature sans confondre sa validité avec la confiance dans le signataire ; expliquer les limites des signatures ; et proposer une procédure de vérification reproductible.

Le but n'est pas de devenir cryptographe en un cours. Il est de comprendre assez précisément les concepts pour choisir les bons outils, reconnaître les fausses garanties et savoir quand une vérification est insuffisante.

## 2. Pourquoi a-t-on besoin du hachage ?

### 2.1. Le problème de l'intégrité

L'intégrité concerne la protection contre les modifications non autorisées ou non détectées. Dans un système informatique, une modification peut être accidentelle, légitime ou malveillante. Une archive peut être corrompue pendant un transfert ; un fichier de configuration peut être modifié par erreur ; un logiciel téléchargé peut ne pas correspondre à la version publiée par son éditeur ; un document peut être altéré après sa validation ; un attaquant peut remplacer un script par une version qui exécute une action non souhaitée ; une sauvegarde peut être partiellement endommagée ; et un paquet logiciel peut être remplacé sur un serveur miroir compromis.

Il faut donc un moyen de comparer un contenu de référence avec un contenu reçu ou conservé. Une taille de fichier n'est pas suffisante. Deux fichiers différents peuvent avoir exactement la même taille. Le nom, la date de modification et l'extension ne suffisent pas non plus : ils sont faciles à copier ou à modifier.

Le hachage fournit un moyen compact de représenter le contenu d'un fichier. On calcule une empreinte à partir des octets du fichier, puis on compare cette empreinte à une référence obtenue par un canal fiable.

    Contenu d'entrée
          |
          v
    Fonction de hachage
          |
          v
    Empreinte de longueur déterminée

### 2.2. Qu'est-ce qu'une fonction de hachage ?

**Schéma pédagogique — Une fonction calcule une empreinte de taille définie à partir d'un contenu de taille variable.**

~~~text
Fichier A (petit ou grand) ----\
Texte --------------------------+--> [Fonction SHA-256] --> empreinte 256 bits
Fichier B ----------------------/

Meme contenu => meme empreinte.
Modification du contenu => empreinte generalement tres differente.
Le hachage n'est pas un chiffrement reversible.
~~~


Une fonction de hachage prend une donnée en entrée et calcule une valeur de longueur déterminée, appelée empreinte, digest ou résumé cryptographique. Une fonction telle que SHA-256 produit une empreinte de 256 bits, quelle que soit la taille ordinaire du message traité. Une empreinte SHA-256 affichée en hexadécimal comporte généralement 64 caractères, chaque caractère hexadécimal représentant quatre bits.

L'empreinte n'est pas le fichier lui-même. Elle ne permet pas normalement de reconstruire le contenu original. Il s'agit d'une représentation calculée à partir du contenu, conçue notamment pour permettre des comparaisons fiables selon les propriétés de sécurité de l'algorithme.

### 2.3. Le hachage n'est pas un chiffrement

Le chiffrement transforme des données afin que seules les personnes disposant du mécanisme de déchiffrement approprié puissent retrouver le contenu en clair. Une fonction de hachage cryptographique, elle, calcule une empreinte qui n'a pas vocation à être inversée.

Le hachage ne cache pas les données. Si tu calcules l'empreinte d'un fichier public, tu ne rends pas ce fichier confidentiel. De même, le chiffrement ne fournit pas toujours un mécanisme d'intégrité : certains modes anciens de chiffrement n'empêchent pas nécessairement une modification détectable du contenu. Les systèmes modernes utilisent souvent un chiffrement authentifié, par exemple AES-GCM, qui vise à protéger la confidentialité et à détecter certaines modifications non autorisées.

### 2.4. Le hachage n'est pas un encodage

Un encodage comme Base64 sert à représenter des données sous une forme compatible avec un support donné. Il est normalement réversible sans clé secrète. Le hachage, lui, produit une empreinte de taille définie et ne fournit pas un mécanisme général permettant de retrouver le contenu original.

Il faut distinguer :
- l'encodage, qui transforme une représentation selon un format ;
- le hachage, qui calcule une empreinte ;
- le chiffrement, qui transforme un contenu pour en protéger la confidentialité ;
- la signature numérique, qui produit une preuve cryptographique vérifiable associée à des données et à une clé privée.

Ces opérations peuvent être combinées, mais elles ne sont pas interchangeables. Renommer un fichier, encoder son contenu ou calculer son empreinte ne remplace pas le chiffrement.

## 3. Les propriétés attendues d'un hachage cryptographique

### 3.1. Déterminisme

Pour un même algorithme et exactement les mêmes octets en entrée, le résultat est le même. C'est ce qui permet de comparer une empreinte de référence à celle d'un fichier reçu.

La condition « exactement les mêmes octets » est importante. Les chaînes « Bonjour », « bonjour » et « Bonjour » suivie d'un espace ne sont pas identiques. Une différence de majuscule, d'espace, de retour à la ligne ou d'encodage peut modifier l'empreinte.

### 3.2. Effet avalanche

Une petite modification en entrée doit provoquer un changement important et imprévisible dans l'empreinte. Deux textes qui diffèrent d'une lettre doivent produire des empreintes radicalement différentes, plutôt que deux résultats presque identiques.

L'effet avalanche ne révèle pas où se trouve la modification. Il indique seulement que le contenu complet ne correspond plus à celui qui a produit la référence. Il ne permet pas de reconstituer la modification à partir de l'empreinte.

### 3.3. Résistance à la préimage

Étant donné une empreinte, il doit être impraticable de retrouver un message qui produit cette empreinte, dans le cadre des hypothèses de sécurité de la fonction. La question est : « J'ai une empreinte ; puis-je retrouver un contenu qui la produit ? »

Cette propriété ne signifie pas que tous les messages sont impossibles à deviner. Si le contenu appartient à un ensemble très petit, comme un PIN de quatre chiffres, un attaquant peut essayer les possibilités. La résistance cryptographique doit être évaluée avec le contexte et l'espace de recherche en tête.

### 3.4. Résistance à la seconde préimage

Si un message donné est fixé, il doit être impraticable de trouver un autre message différent qui produit exactement la même empreinte. Cette propriété compte lorsqu'on souhaite protéger un contenu de référence contre son remplacement par un autre contenu ayant la même empreinte.

### 3.5. Résistance aux collisions

Une collision existe lorsque deux entrées différentes produisent la même empreinte :

    Message A différent de Message B
    H(Message A) = H(Message B)

Comme une fonction traite potentiellement un très grand nombre de messages pour produire une sortie de longueur fixe, des collisions existent nécessairement en théorie. La sécurité dépend du fait qu'il soit impraticable d'en trouver une de manière utile.

Il faut distinguer la recherche de deux messages quelconques ayant la même empreinte de la recherche d'un autre message qui correspond à une empreinte déjà fixée. Ces problèmes ne sont pas équivalents. Pour une fonction idéale produisant n bits, rechercher une collision générique demande approximativement 2 puissance n/2 essais grâce à l'effet d'anniversaire, tandis qu'une recherche de préimage demande théoriquement un effort proche de 2 puissance n. Ces ordres de grandeur sont des repères simplifiés : les faiblesses d'un algorithme et le contexte peuvent modifier l'analyse.

### 3.6. Pourquoi toutes les collisions ne peuvent-elles pas être supprimées ?

Une fonction de hachage à sortie fixe ne peut pas attribuer mathématiquement une valeur différente à chaque message possible, car le nombre de messages est illimité alors que le nombre d'empreintes possibles est limité. Le but est donc de rendre la recherche de collisions impraticable, pas de les supprimer mathématiquement.

Cette distinction explique pourquoi les professionnels parlent de résistance aux collisions plutôt que d'absence de collisions.

## 4. Les familles de fonctions de hachage

### 4.1. SHA-256 et SHA-2

SHA-256 appartient à la famille SHA-2, qui comprend plusieurs algorithmes. SHA-256 fournit une empreinte de 256 bits. Il est utilisé dans de nombreux outils de vérification de fichiers, systèmes de signature et applications de sécurité.

C'est un choix courant pour les vérifications d'intégrité générales. Il reste essentiel de l'utiliser dans un protocole correct : choisir SHA-256 ne rend pas automatiquement sûr un système qui accepte une empreinte fournie par une source non fiable.

### 4.2. SHA-512

SHA-512 appartient également à SHA-2 et produit une empreinte de 512 bits. Le choix entre SHA-256 et SHA-512 dépend de l'application, des exigences, des plateformes et du protocole. Une empreinte plus longue n'implique pas automatiquement que tous les aspects d'un système soient plus sûrs.

### 4.3. SHA-3

SHA-3 est une autre famille normalisée de fonctions de hachage cryptographiques. Elle repose sur une construction différente de celle de SHA-2. Il est utile de connaître les deux, mais il ne faut pas changer d'algorithme au hasard dans un système existant. L'application doit préciser la fonction, la longueur de sortie et le format utilisés.

### 4.4. MD5 et SHA-1

MD5 et SHA-1 ne doivent pas être choisis pour de nouveaux usages qui dépendent de la résistance aux collisions. Des attaques pratiques contre leurs propriétés de collision ont été démontrées. Tu peux encore rencontrer ces noms dans d'anciens fichiers ou systèmes de compatibilité. Leur présence ne signifie pas qu'une attaque a eu lieu, mais elle doit conduire à examiner le contexte et à planifier une migration lorsque cela est possible.

Il faut éviter de traiter une empreinte MD5 ou SHA-1 comme une preuve cryptographique forte qu'un fichier est bien celui publié par un éditeur.

### 4.5. Choisir l'algorithme

Avant de choisir une fonction, demande-toi : quel est le but de la vérification ? Quel algorithme le protocole ou l'éditeur recommande-t-il ? L'algorithme est-il adapté au niveau de sécurité recherché ? Les deux parties utilisent-elles les mêmes paramètres ? L'empreinte de référence vient-elle d'une source fiable ? Existe-t-il une procédure de migration si les exigences changent ?

Pour un exercice de vérification de fichier, SHA-256 est un exemple pédagogique adapté. Pour un système de production, il faut aussi respecter les standards et les consignes du produit concerné.

## 5. Vérifier un fichier avec une empreinte

### 5.1. Le principe

**Schéma pédagogique — La comparaison n'est utile que si l'empreinte de référence provient d'une source fiable.**

~~~text
[Fichier telecharge] ---------> SHA-256 --------> H1
                                                       |
[Empreinte attendue fiable] --------------------------+--> comparaison
                                                       |
                                      +----------------+----------------+
                                      v                                 v
                                  Identiques                       Differentes
                                  concordance                      verifier source,
                                  technique                        transfert et fichier
~~~


La vérification se déroule généralement ainsi :
1. obtenir le fichier à examiner ;
2. obtenir l'empreinte de référence par une source fiable ;
3. calculer localement l'empreinte du fichier reçu avec le même algorithme ;
4. comparer les deux valeurs ;
5. interpréter le résultat en tenant compte de la provenance de la référence.

Si les empreintes sont identiques, on dispose d'un indice fort que le fichier correspond au contenu associé à la référence, sous les hypothèses de sécurité de la fonction et si la référence a été obtenue de manière fiable.

Si les empreintes sont différentes, le fichier ne correspond pas au contenu de référence pour la fonction utilisée. La cause peut être une corruption, une version différente, une transformation du fichier ou une altération. Le résultat ne permet pas à lui seul de déterminer laquelle.

### 5.2. Exemple de téléchargement

Imagine que l'éditeur d'un logiciel publie une archive et une valeur SHA-256 officielle. Tu télécharges l'archive et calcules son empreinte. Si les valeurs correspondent, le contenu est compatible avec celui associé à la référence. Si elles diffèrent, n'installe pas le fichier avant d'avoir compris la différence.

Si tu n'as pas de source fiable pour l'empreinte, la simple présence d'une valeur à côté du téléchargement ne prouve pas l'authenticité. Un attaquant qui remplace le fichier peut aussi remplacer une empreinte non protégée publiée au même endroit. Le hachage détecte la différence entre deux contenus, mais il ne garantit pas à lui seul qui a publié la référence.

### 5.3. La provenance de la référence

Une empreinte correcte obtenue depuis un canal compromis n'apporte pas la garantie recherchée. La référence doit provenir d'une source de confiance : documentation officielle accessible par un canal fiable, manifeste signé, dépôt authentifié ou autre mécanisme recommandé par l'éditeur.

Supposons qu'un serveur héberge un programme et un fichier contenant son empreinte. Si un attaquant remplace le programme et l'empreinte sur ce serveur, les valeurs peuvent continuer de correspondre. La comparaison ne révèle alors pas le remplacement. Pour renforcer la confiance, on doit authentifier la référence ou vérifier une signature numérique.

## 6. TP : calculer une empreinte sous Windows

Cette activité peut être réalisée avec Windows PowerShell. Elle ne nécessite pas d'installer un logiciel supplémentaire.

### 6.1. Créer un fichier de test

Dans PowerShell, exécute :

    Set-Content -Path .\message-test.txt -Value "Skill-Tree : test d'intégrité" -Encoding utf8

La commande crée un fichier dans le répertoire courant. L'encodage exact peut varier selon la version de PowerShell ; l'important est de calculer l'empreinte du fichier réellement créé.

### 6.2. Calculer SHA-256

    Get-FileHash .\message-test.txt -Algorithm SHA256

Pour n'afficher que la valeur :

    (Get-FileHash .\message-test.txt -Algorithm SHA256).Hash

Copie la valeur obtenue dans tes notes. Elle représente l'état exact du fichier à cet instant.

### 6.3. Modifier le fichier

Ajoute une seconde ligne :

    Add-Content -Path .\message-test.txt -Value "Deuxième ligne"

Calcule de nouveau l'empreinte :

    Get-FileHash .\message-test.txt -Algorithm SHA256

Compare les deux valeurs. L'empreinte devrait être différente. Une petite modification du contenu change l'empreinte de manière importante.

### 6.4. Restaurer la première version

    Set-Content -Path .\message-test.txt -Value "Skill-Tree : test d'intégrité" -Encoding utf8
    Get-FileHash .\message-test.txt -Algorithm SHA256

L'empreinte doit retrouver la valeur initiale si les octets sont exactement les mêmes. Si tu observes une différence inattendue, vérifie les caractères, l'encodage, les retours à la ligne et la manière dont les commandes ont écrit le fichier.

### 6.5. Limites de l'expérience

L'activité démontre qu'une empreinte change lorsque le contenu change et qu'elle peut être recalculée. Elle ne démontre pas que le fichier est inoffensif, que son auteur est connu, que le contenu n'a jamais été modifié dans le passé, ni que la valeur conservée dans tes notes est authentique.

L'empreinte est un outil de comparaison, pas un certificat de confiance universel.

## 7. TP : vérifier une empreinte sous Linux

### 7.1. Créer le fichier

    printf 'Skill-Tree : test d’intégrité\n' > message-test.txt

Cette commande écrit une ligne dans le fichier.

### 7.2. Calculer SHA-256

Sur les systèmes Linux qui disposent de sha256sum, exécute :

    sha256sum message-test.txt

Une sortie typique ressemble à ceci, où la valeur est calculée à partir de ton propre fichier :

    <empreinte_sha256>  message-test.txt

Ne copie pas une empreinte provenant d'un exemple en la considérant comme la valeur attendue.

### 7.3. Modifier et recalculer

    printf 'Une modification\n' >> message-test.txt
    sha256sum message-test.txt

La nouvelle empreinte doit être différente.

### 7.4. Comparer avec une valeur enregistrée

    sha256sum message-test.txt > empreintes.txt
    sha256sum -c empreintes.txt

La première commande enregistre la sortie ; la seconde vérifie le fichier indiqué dans le manifeste sur les systèmes GNU qui prennent en charge cette option. Cette méthode reste dépendante de la confiance dans le fichier d'empreintes. Si le fichier de référence peut être modifié par un attaquant, le contrôle est affaibli.

Pour les systèmes de production, définis qui crée et approuve le manifeste, où il est conservé, qui peut le modifier et comment les changements sont audités.

## 8. Hachage et mots de passe

### 8.1. Pourquoi ne pas conserver les mots de passe en clair ?

Une base de données peut contenir les comptes d'un service. Si elle conserve les mots de passe en clair et que cette base est volée, l'attaquant récupère directement les secrets. Une pratique plus sûre consiste à stocker un vérificateur calculé avec une fonction spécialisée plutôt que le mot de passe lui-même.

Lors de l'authentification, le système utilise le mécanisme prévu pour vérifier si le mot de passe fourni correspond au vérificateur conservé.

### 8.2. Pourquoi SHA-256 seul ne convient-il pas ?

SHA-256 est conçu pour calculer rapidement une empreinte. Pour un fichier, cette rapidité est utile. Pour les mots de passe, elle peut devenir un inconvénient : un attaquant qui obtient une base peut tester un grand nombre de mots de passe candidats rapidement, surtout si les secrets sont faibles.

Le stockage des mots de passe utilise donc des fonctions dédiées, conçues pour rendre les essais coûteux et permettre des paramètres ajustables. Selon les exigences et les recommandations applicables, on peut utiliser Argon2id, scrypt, bcrypt ou PBKDF2 correctement configurés.

### 8.3. Le rôle du sel

**Schéma pédagogique — Le sel est propre à chaque enregistrement et rend plus difficile la réutilisation de tables précalculées.**

~~~text
Mot de passe + sel aleatoire
            |
            v
[Argon2id / scrypt / bcrypt selon politique]
            |
            v
[Parametres + sel + hash stockes]
            |
Connexion: mot de passe fourni + meme sel
            |
            v
        recalcul et comparaison

Ne jamais stocker le mot de passe en clair ni utiliser SHA-256 seul pour le stockage.
~~~


Un sel est une valeur associée au mot de passe lors du calcul de son vérificateur. Il doit être unique pour chaque mot de passe stocké et généré de manière appropriée. Le sel empêche notamment que deux utilisateurs ayant choisi le même mot de passe aient automatiquement des vérificateurs identiques, et limite l'utilité de tables précalculées.

Le sel n'a pas besoin d'être secret. Il est conservé avec les paramètres et le vérificateur. Il ne remplace ni un mot de passe robuste ni une fonction spécialisée.

### 8.4. Distinguer les besoins

    Besoin : vérifier deux fichiers identiques
    Approche : hachage cryptographique adapté, tel que SHA-256

    Besoin : stocker un vérificateur de mot de passe
    Approche : fonction spécialisée, paramétrée, avec sel unique

    Besoin : authentifier un message au moyen d'un secret partagé
    Approche : HMAC avec une clé secrète

    Besoin : vérifier une signature publique sur un document
    Approche : signature numérique et clé publique authentifiée

Le mot « hachage » ne signifie donc pas que tous les usages peuvent partager la même fonction ou la même configuration.

## 9. Du hachage au HMAC

### 9.1. Pourquoi une empreinte seule ne prouve pas l'origine

Une fonction de hachage ordinaire ne nécessite pas de secret. Tout utilisateur qui dispose du fichier peut généralement recalculer son empreinte. Si deux personnes échangent un fichier et son SHA-256, l'empreinte ne prouve pas qui l'a calculée.

Pour authentifier un message entre des parties qui partagent un secret, on peut utiliser un HMAC, un code d'authentification de message construit à partir d'une fonction de hachage et d'une clé secrète.

### 9.2. Principe du HMAC

**Schéma pédagogique — Un HMAC authentifie un message avec un secret partagé ; une empreinte simple ne prouve pas l'origine.**

~~~text
Emetteur: message + secret partage --> HMAC --> message || tag
                                                |
                                                v
Destinataire: message recu + meme secret --> HMAC recalcule
                                                |
                                        comparer le tag

HMAC n'est pas une signature a cle publique : les deux parties partagent le secret.
~~~


    Message + clé secrète
            |
            v
           HMAC
            |
            v
    Code d'authentification

La personne qui calcule et celle qui vérifie doivent posséder la clé. Le destinataire recalcule le HMAC à partir du message reçu et de la clé partagée, puis compare le résultat. Si la vérification réussit, cela permet de détecter certaines modifications et d'authentifier le message vis-à-vis des détenteurs du secret.

### 9.3. HMAC et signature numérique

Avec un HMAC, les deux parties partagent un secret ; chacune peut donc produire un code valide. Le destinataire ne peut pas déduire du seul HMAC que l'autre partie, plutôt que lui-même, a produit le message.

Avec une signature numérique, la clé privée sert à signer et la clé publique correspondante sert à vérifier. Le vérificateur peut disposer de la clé publique sans pouvoir créer des signatures valides simplement avec cette clé.

HMAC est adapté à l'authentification entre des parties qui partagent un secret. Une signature convient lorsque des destinataires doivent vérifier un document sans posséder le secret de signature. Le choix dépend du modèle de confiance, des performances et des exigences du protocole.

## 10. Comprendre la signature numérique

### 10.1. Le besoin

Un éditeur publie une mise à jour logicielle et veut que les utilisateurs puissent vérifier que le fichier correspond à ce qui a été signé à l'aide de sa clé privée.

Une empreinte publiée à côté du fichier aide à détecter une différence seulement si la référence est fiable. Une signature numérique permet de protéger cryptographiquement un message ou un fichier à l'aide d'une clé privée, puis de vérifier la signature avec la clé publique correspondante.

Une signature peut aider à établir que les données vérifiées correspondent à celles associées à la signature, et que celle-ci a été produite par quelqu'un qui contrôlait la clé privée correspondante, sous les hypothèses de l'algorithme et de sa mise en œuvre. Elle ne prouve pas automatiquement que la personne derrière la clé est celle qu'elle prétend être.

### 10.2. Le processus conceptuel

    Signature :
    Données + clé privée
              |
              v
      Algorithme de signature
              |
              v
           Signature

    Vérification :
    Données + signature + clé publique
              |
              v
      Algorithme de vérification
              |
        +-----+-----+
        |           |
      Valide     Invalide

Le destinataire ne doit pas modifier les données avant la vérification. Une signature est liée aux données précises qui ont été signées selon le format et l'algorithme utilisés.

### 10.3. Pourquoi ne signe-t-on pas simplement un nom ?

Une image de signature manuscrite peut être collée sur un fichier, tout comme un texte contenant le nom d'un auteur. Cela ne constitue pas une signature numérique cryptographique.

Une signature numérique repose sur une relation mathématique entre la signature, les données et une clé. Elle doit être vérifiée par un logiciel qui comprend le format utilisé. Une image peut avoir une valeur administrative dans certains contextes, mais elle n'offre pas à elle seule les garanties cryptographiques d'une signature numérique.

### 10.4. Une signature ne chiffre pas le document

Une signature vise principalement l'intégrité et l'authentification cryptographique par rapport à la clé publique. Le document peut rester lisible par toute personne qui le reçoit. Si le fichier doit rester confidentiel, il faut aussi appliquer un contrôle d'accès ou un mécanisme de chiffrement adapté.

Un éditeur peut signer publiquement un installateur : le but est que chaque utilisateur puisse vérifier l'intégrité et la relation avec la clé du signataire, et non de cacher le contenu du programme.

### 10.5. Une signature valide ne signifie pas « sans danger »

Un logiciel signé peut contenir un défaut, une vulnérabilité ou un comportement indésirable. Une signature valide établit une relation cryptographique entre le contenu, la signature et la clé vérifiée. Elle ne prouve pas que le logiciel a été audité, qu'il est exempt de bogues ou que l'éditeur est digne de confiance à tous égards.

La confiance dans le signataire, le processus de publication et le logiciel exige d'autres contrôles : examen du code, gestion des vulnérabilités, contrôle de la chaîne d'approvisionnement et politique de mise à jour.

## 11. Clé privée, clé publique et identité

### 11.1. La clé privée

La clé privée est la partie secrète de la paire. Elle doit être protégée contre le vol, la copie non autorisée et l'utilisation abusive. Si un attaquant obtient la clé privée d'un éditeur, il peut potentiellement signer des contenus que les systèmes associés accepteront tant que la clé reste considérée comme fiable.

Les clés privées doivent donc faire l'objet de contrôles : accès restreint, stockage sécurisé, sauvegarde maîtrisée, rotation et procédure de révocation ou de remplacement en cas de compromission.

### 11.2. La clé publique

La clé publique est utilisée par les vérificateurs pour valider les signatures. Elle peut être distribuée sans être secrète, mais sa provenance doit être vérifiée. Une clé publique fournie par un attaquant peut permettre de faire accepter ses propres signatures si le système ne vérifie pas à qui appartient la clé.

L'algorithme de signature peut fonctionner correctement tout en donnant un résultat inutile si le vérificateur utilise la mauvaise clé publique.

### 11.3. À qui appartient cette clé ?

Une clé publique est d'abord une valeur cryptographique. Pour savoir si elle correspond à un éditeur, à une organisation ou à une personne, il faut une procédure d'association à une identité. Cette procédure peut s'appuyer sur un certificat, un système de clés de confiance, une empreinte confirmée par un canal indépendant ou une infrastructure de signature de logiciels.

Ne traite jamais une clé publique comme authentique simplement parce que son nom de fichier contient celui de l'éditeur.

## 12. Algorithmes de signature : notions essentielles

### 12.1. RSA

RSA est un système à clé publique qui peut être utilisé pour les signatures numériques lorsqu'il est configuré avec un schéma adapté. Pour un nouveau système, le schéma, les paramètres et la taille de la clé doivent suivre les recommandations applicables. Écrire seulement « RSA » ne décrit pas complètement une signature : le schéma de signature et ses paramètres font partie de la construction. RSA-PSS est un exemple de schéma de signature conçu à cet effet.

### 12.2. ECDSA

ECDSA est un algorithme de signature fondé sur la cryptographie à courbes elliptiques. Comme pour tout algorithme de signature, la génération des clés, les paramètres, les encodages et la mise en œuvre doivent être corrects.

La sécurité d'ECDSA dépend notamment d'une bonne gestion de la valeur interne utilisée lors de la signature. Des erreurs graves peuvent révéler la clé privée. Les applications doivent utiliser des bibliothèques de confiance et éviter toute implémentation artisanale.

### 12.3. EdDSA et Ed25519

EdDSA est une famille de schémas de signature. Ed25519 en est une variante largement utilisée dans de nombreux outils et bibliothèques. Pour un projet concret, on choisit un algorithme pris en charge par la plateforme et adapté aux exigences de sécurité, de compatibilité et d'interopérabilité.

### 12.4. Pourquoi ne pas écrire son propre algorithme ?

Les algorithmes de signature dépendent de détails mathématiques subtils. Une erreur peut permettre de forger des signatures ou de divulguer une clé. Dans une application, il faut préférer une bibliothèque réputée et maintenue, suivre sa documentation et utiliser les paramètres prévus.

### 12.5. Le format compte aussi

La signature mathématique ne définit pas à elle seule comment les octets sont encodés, quels éléments sont signés, quel algorithme est déclaré ou comment le vérificateur récupère la clé publique. Un format doit préciser ces éléments. Dans un système de production, il faut suivre le format prévu par le protocole ou l'éditeur plutôt que concaténer librement des données.

## 13. Certificats et chaîne de confiance

### 13.1. Le rôle d'un certificat

Un certificat numérique associe une identité ou des attributs à une clé publique selon un format et une politique donnés. Dans une infrastructure de clés publiques, le certificat est généralement signé par une autorité de certification.

La validation doit considérer la chaîne de certification, les périodes de validité, les usages autorisés, l'identité attendue et l'état de révocation lorsque cela est applicable. Le simple fait qu'un fichier de certificat existe ne prouve pas sa validité.

### 13.2. Certificat et clé privée

Un certificat peut contenir la clé publique et des informations d'identité. Il ne doit pas être confondu avec la clé privée, qui reste secrète et permet d'effectuer les opérations de signature. Le certificat peut être distribué publiquement ; la clé privée associée doit rester protégée.

### 13.3. Chaîne de certification

**Schéma pédagogique — Une signature de certificat relie une clé publique à une identité suivant une chaîne de confiance.**

~~~text
Racine de confiance locale
          |
          v
Certificat CA intermediaire
          |
          v
Certificat du service / identite
          |
          v
Verification: chaine + dates + nom + usages + statut

Une signature valide ne suffit pas si l'identité ou la politique est incorrecte.
~~~


    Autorité racine approuvée
              |
              v
    Autorité intermédiaire
              |
              v
    Certificat du serveur ou du signataire
              |
              v
    Validation selon le contexte

Cette structure est courante mais ne représente pas toutes les architectures possibles. Certaines applications utilisent d'autres modèles de confiance.

### 13.4. Tous les écosystèmes ne fonctionnent pas pareil

Une signature de code Windows, une signature de paquet Linux, une signature OpenPGP ou une signature de conteneur peuvent utiliser des formats et des politiques différents. Il faut suivre les instructions de l'outil et de l'éditeur. La présence d'un certificat ne signifie pas que tous les systèmes appliquent les mêmes règles.

### 13.5. Validité mathématique et confiance

Il faut séparer trois questions :
1. La signature correspond-elle aux données et à la clé publique ?
2. La clé publique est-elle authentiquement associée au signataire attendu ?
3. Le signataire est-il autorisé ou digne de confiance pour ce contenu ?

Une signature peut être mathématiquement valide et ne pas être digne de confiance pour l'usage recherché si la clé n'est pas correctement identifiée ou si le signataire n'est pas autorisé à publier ce type de fichier.

## 14. Limites d'une signature numérique

### 14.1. Clé compromise

Si une clé privée est volée, un attaquant peut potentiellement produire des signatures valides. Les vérificateurs peuvent accepter des contenus malveillants si la compromission n'est pas connue ou traitée. La gestion des clés doit donc prévoir le stockage sûr, la limitation des personnes autorisées, la surveillance des opérations, la révocation, le remplacement et la communication de l'incident.

### 14.2. Expiration et révocation

Une signature produite avec une clé aujourd'hui expirée n'est pas nécessairement invalide dans tous les contextes historiques ; l'interprétation dépend de la politique, des horodatages et du système. À l'inverse, une clé révoquée à la suite d'une compromission peut rendre la confiance inadaptée pour certaines signatures. Il faut appliquer la politique du système au lieu de se limiter à un indicateur isolé.

### 14.3. Horodatage

Un horodatage de confiance peut fournir une preuve qu'une signature existait à un moment associé à une autorité d'horodatage. Il ne supprime pas la nécessité d'examiner la validité du certificat, l'historique de confiance et la politique d'horodatage. La date de modification locale d'un fichier peut être changée et n'est pas équivalente à un horodatage cryptographique.

### 14.4. Non-répudiation : prudence

Les signatures sont parfois associées à la non-répudiation, mais une signature mathématiquement valide ne résout pas toutes les questions d'attribution dans le monde réel. Il faut examiner qui contrôlait la clé privée, quelles mesures de sécurité étaient en place, si l'utilisation était autorisée et quelles règles juridiques ou contractuelles s'appliquent.

## 15. Étude de cas : la mise à jour de NovaLearn

### 15.1. Situation

NovaLearn publie une nouvelle version d'un outil installé sur les postes de formation. Les techniciens téléchargent une archive d'installation. Un technicien constate que l'empreinte calculée diffère de celle qu'il avait notée la semaine précédente. Un collègue suggère de renommer le fichier puis de continuer l'installation. Un autre affirme qu'une signature valide suffira toujours, sans examiner le nom du signataire.

### 15.2. Étape 1 — Suspendre l'installation

Le technicien ne doit pas ignorer la différence. Il conserve le fichier pour une analyse contrôlée et évite de l'exécuter. Il ne doit pas supprimer les preuves utiles au diagnostic ni transférer le fichier à d'autres utilisateurs en le présentant comme fiable.

### 15.3. Étape 2 — Examiner la source

Il vérifie que le téléchargement provient du canal officiel et qu'il utilise la version attendue. Il consulte les notes de version et recherche l'empreinte officielle par un canal fiable. Il vérifie que la référence appartient bien à la bonne version et au bon fichier.

### 15.4. Étape 3 — Recalculer l'empreinte

Le technicien recalcule SHA-256 localement. Si la différence persiste, l'installation reste suspendue. Les causes possibles incluent une corruption, une version différente, un téléchargement incomplet, une modification légitime ou une altération malveillante. Il ne conclut pas immédiatement que la dernière hypothèse est certaine.

### 15.5. Étape 4 — Vérifier la signature

Si l'éditeur fournit une signature, le technicien utilise l'outil recommandé. Il examine le résultat, l'identité du signataire, la chaîne de confiance lorsqu'elle s'applique, l'état du certificat et les consignes de l'éditeur. La simple présence d'un fichier de signature à côté de l'archive n'apporte aucune preuve tant que la vérification n'a pas été réalisée.

### 15.6. Étape 5 — Décider à partir des éléments

Si l'empreinte correspond à une référence fiable et que les contrôles nécessaires réussissent, le technicien peut poursuivre selon la procédure de l'organisation. Si un contrôle échoue ou si la source demeure incertaine, il suspend l'installation, signale le problème et suit la procédure de sécurité.

### 15.7. Leçons à retenir

Une vérification correcte ne se résume pas à lancer une commande. Il faut connaître le bon fichier, obtenir une référence fiable, utiliser l'algorithme attendu et comprendre le résultat. Une signature apporte des garanties supplémentaires, mais doit être vérifiée avec la bonne clé et dans le bon contexte. La décision finale dépend aussi de la politique de sécurité.

## 16. TP : signer et vérifier un fichier avec Python

Cette activité illustre une signature Ed25519 à l'aide de la bibliothèque Python cryptography. Réalise le TP dans un répertoire de test, sur des fichiers que tu contrôles. N'utilise pas une clé créée pour cet exercice afin de signer des logiciels ou des documents professionnels.

### 16.1. Préparer Python

Vérifie que Python est disponible :

    python --version

Installe la bibliothèque dans l'environnement de test :

    python -m pip install cryptography

Selon la plateforme, la commande peut être python3. Dans un projet réel, il est préférable d'utiliser un environnement virtuel et de suivre la politique de dépendances de l'organisation.

### 16.2. Créer le document

Crée un fichier document.txt qui contient :

    Document de démonstration pour Skill-Tree.
    Version 1.

Enregistre le fichier. Ce sont les octets du fichier qui seront signés.

### 16.3. Générer une paire de clés

Crée un fichier Python nommé signer.py avec le code suivant :

    from pathlib import Path
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Simplification pédagogique : clé privée enregistrée sans chiffrement.
    # Ne pas reproduire ce choix pour une clé de production.
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    Path("private_key.pem").write_bytes(private_pem)
    Path("public_key.pem").write_bytes(public_pem)
    print("Clé privée et clé publique créées.")

Exécute le script :

    python signer.py

La clé privée est secrète ; la clé publique peut être partagée. Dans ce TP, garde les fichiers dans un répertoire local. La clé privée est enregistrée sans chiffrement uniquement pour rendre la démonstration simple. Ne la place pas dans un dépôt public, un ticket de support ou des journaux.

### 16.4. Signer les octets

Crée sign_document.py :

    from pathlib import Path
    from cryptography.hazmat.primitives import serialization

    private_key = serialization.load_pem_private_key(
        Path("private_key.pem").read_bytes(),
        password=None,
    )
    data = Path("document.txt").read_bytes()
    signature = private_key.sign(data)
    Path("document.sig").write_bytes(signature)
    print("Document signé : document.sig")

Puis exécute :

    python sign_document.py

Le fichier document.sig contient la signature binaire. Il n'est pas nécessaire que sa représentation soit lisible comme du texte ; le programme de vérification utilisera les octets exacts.

### 16.5. Vérifier la signature

Crée verify_document.py :

    from pathlib import Path
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import serialization

    public_key = serialization.load_pem_public_key(
        Path("public_key.pem").read_bytes()
    )
    data = Path("document.txt").read_bytes()
    signature = Path("document.sig").read_bytes()

    try:
        public_key.verify(signature, data)
    except InvalidSignature:
        print("ÉCHEC : la signature ne correspond pas au fichier.")
        raise SystemExit(1)
    else:
        print("SUCCÈS : signature valide pour ce contenu et cette clé.")

Exécute :

    python verify_document.py

Si les fichiers et les clés n'ont pas été modifiés, la vérification doit réussir.

### 16.6. Modifier le document

Modifie document.txt, par exemple en remplaçant Version 1 par Version 2. Relance le vérificateur. La vérification doit échouer car le document ne correspond plus aux octets signés.

Restaure ensuite exactement le contenu original et relance la vérification. La signature doit réussir de nouveau si les octets sont identiques.

### 16.7. Ce que le TP démontre

Le TP montre comment une clé privée produit une signature qu'une clé publique correspondante peut vérifier. Il ne démontre pas que la clé publique est celle d'un éditeur officiel. Tu as généré les clés toi-même : tu sais donc qu'elles correspondent, mais un destinataire distant ne peut pas savoir à qui appartient cette clé simplement à partir de son nom de fichier.

Pour vérifier un véritable éditeur, il faut disposer d'une procédure fiable pour identifier et approuver sa clé publique ou son certificat.

### 16.8. Bonnes pratiques

Utilise une bibliothèque cryptographique maintenue et une version prise en charge. Restreins l'accès à la clé privée. Protège-la selon le niveau de risque, par exemple avec un stockage sécurisé adapté. Évite de charger une clé depuis un emplacement contrôlable par un utilisateur non fiable. Gère la rotation et la révocation. Définis le format des données sans ambiguïté. Traite un échec de signature comme un échec de validation et non comme un avertissement ignoré pour gagner du temps.

## 17. Signature et chaîne d'approvisionnement logicielle

### 17.1. Vérification manuelle et automatisation

Pour un petit fichier reçu ponctuellement, comparer une empreinte peut être raisonnable si une référence fiable est disponible. Cette méthode devient difficile à gérer pour des centaines de paquets et des mises à jour fréquentes. Une personne peut copier une mauvaise valeur, vérifier le mauvais fichier ou réutiliser une empreinte appartenant à une ancienne version.

Les dépôts et gestionnaires de paquets peuvent utiliser des signatures, des métadonnées signées et des clés de dépôt pour vérifier les paquets et les informations de publication. La sécurité dépend de la chaîne complète : confiance dans les clés, métadonnées, contrôles de version, configuration du dépôt, logiciel client et procédure de mise à jour.

### 17.2. La chaîne d'approvisionnement

Un logiciel moderne peut comprendre des dépendances externes, des bibliothèques, des compilateurs, des scripts d'intégration continue et des artefacts produits automatiquement. La signature d'un artefact est un contrôle important, mais elle ne suffit pas à garantir que toute la chaîne de production était sûre.

Une organisation peut renforcer sa chaîne d'approvisionnement par la gestion des dépendances, la protection des secrets de signature, des contrôles d'accès, des journaux d'audit et des procédures reproductibles de construction et de publication.

### 17.3. L'automatisation en intégration continue

Dans un flux d'intégration continue, on peut ajouter des étapes pour calculer des empreintes, signer un artefact et vérifier automatiquement la signature avant diffusion. Le processus doit échouer explicitement si la vérification nécessaire échoue.

Les clés de signature doivent être séparées des environnements non fiables. Un attaquant qui contrôle le processus de construction peut chercher à obtenir l'accès à la clé ou à signer un artefact modifié. Il faut donc protéger les permissions, les secrets et les étapes de publication.

## 18. Erreurs fréquentes à éviter

### Erreur 1 — Croire qu'une empreinte prouve l'identité de l'auteur

Une empreinte peut être calculée par tout utilisateur qui dispose du fichier. Elle identifie un contenu par rapport à une référence ; elle n'établit pas l'identité de son créateur.

**Correction :** utiliser une référence fiable ou vérifier une signature numérique avec une clé authentifiée.

### Erreur 2 — Comparer les empreintes de deux versions différentes

Une mise à jour légitime modifie naturellement le contenu. Une empreinte officielle pour la version 4.2.1 n'est pas une référence valable pour la version 4.2.0.

**Correction :** vérifier le nom, la version, l'architecture et le canal de publication avant la comparaison.

### Erreur 3 — Utiliser un algorithme obsolète dans un nouveau système

Un ancien script peut encore calculer MD5 ou SHA-1 parce que l'outil est disponible. Cela ne justifie pas leur usage pour de nouvelles garanties fortes contre les collisions.

**Correction :** suivre les algorithmes recommandés et planifier la migration des mécanismes anciens lorsque cela est possible.

### Erreur 4 — Confondre hachage et chiffrement

Une empreinte n'empêche pas la lecture d'un fichier. Elle ne garantit pas la confidentialité.

**Correction :** associer chaque contrôle à son objectif et utiliser un mécanisme adapté.

### Erreur 5 — Croire qu'une signature valide prouve qu'un logiciel est sans danger

Une signature confirme que la vérification cryptographique réussit selon la clé et les règles utilisées. Elle ne garantit pas l'absence de vulnérabilités.

**Correction :** conserver les contrôles complémentaires de la chaîne logicielle.

### Erreur 6 — Accepter automatiquement une nouvelle clé publique

Une clé peut avoir été renouvelée légitimement, mais elle peut aussi avoir été remplacée par un attaquant.

**Correction :** suivre le mécanisme de renouvellement officiel et authentifier la nouvelle clé.

### Erreur 7 — Ignorer un échec de vérification

Un avertissement peut être ignoré par commodité, ce qui supprime précisément la valeur du contrôle.

**Correction :** traiter l'échec comme un problème à expliquer et résoudre avant une action sensible.

### Erreur 8 — Utiliser HMAC comme preuve publique d'origine

Tous les détenteurs du secret partagé peuvent calculer un HMAC valide.

**Correction :** utiliser une signature numérique lorsqu'une vérification publique est nécessaire.

### Erreur 9 — Conserver une clé privée dans un dépôt

Une clé publiée ou copiée dans des journaux doit être considérée comme potentiellement compromise.

**Correction :** protéger les secrets et suivre une procédure de rotation ou de révocation en cas d'exposition.

### Erreur 10 — Confondre signature valide et identité confirmée

La vérification mathématique réussit par rapport à une clé donnée, mais celle-ci peut appartenir à une autre personne.

**Correction :** authentifier la clé publique par un modèle de confiance adapté.

### Erreur 11 — Traiter la date du fichier comme preuve d'historique

La date de modification peut être changée. Elle n'est pas équivalente à un horodatage de confiance.

**Correction :** utiliser des journaux protégés, des signatures et des mécanismes appropriés lorsque l'historique compte.

### Erreur 12 — Hacher du texte au lieu du fichier réel

Les espaces, encodages et retours à la ligne peuvent changer les octets.

**Correction :** calculer le hachage sur le fichier exact et suivre les conventions du format.

## 19. TP : rédiger une procédure de vérification

### 19.1. Objectif

Conçois une procédure que les techniciens suivront avant d'installer un outil sur les postes de production. Elle doit empêcher les installations fondées uniquement sur le nom du fichier ou sur une empreinte venant d'une source inconnue.

### 19.2. Étape 1 — Identifier l'artefact

La procédure doit préciser le nom du fichier, sa version, la plateforme concernée, la source de téléchargement, le format et l'équipe responsable de l'approbation.

### 19.3. Étape 2 — Choisir le contrôle

Si l'éditeur fournit une empreinte, le technicien utilise l'algorithme recommandé et la compare à la référence officielle. Si l'éditeur fournit une signature, il utilise l'outil approprié et examine le signataire, la clé ou le certificat et le résultat de validation. Si l'éditeur exige les deux contrôles, il faut les effectuer tous les deux.

### 19.4. Étape 3 — Définir la provenance

La procédure doit répondre à ces questions :
- Où l'empreinte ou la signature est-elle publiée ?
- Comment le technicien vérifie-t-il la source ?
- La référence est-elle protégée par une signature ou un autre mécanisme ?
- Qui peut modifier la référence approuvée ?
- Comment les nouvelles clés sont-elles validées ?

Une liste d'empreintes modifiable par tout le monde dans le même dossier que le fichier ne suffit pas à authentifier ce fichier.

### 19.5. Étape 4 — Définir la conduite en cas d'échec

Si un contrôle échoue, il faut suspendre l'installation, préserver les informations utiles, éviter les contournements, vérifier la version et la source, signaler le problème et documenter la résolution. La reprise ne se fait que lorsque les contrôles nécessaires sont satisfaits.

### 19.6. Étape 5 — Garder une trace

Le journal de vérification peut enregistrer l'identifiant du fichier, la version, la date, l'outil utilisé, l'algorithme, le résultat et la personne qui a autorisé la suite. Il ne doit pas enregistrer de clés privées, de mots de passe ou d'autres secrets.

### 19.7. Exemple de procédure

    1. Télécharger l'artefact depuis la source approuvée.
    2. Vérifier le nom, la version et la plateforme.
    3. Récupérer la référence officielle.
    4. Calculer l'empreinte ou vérifier la signature.
    5. Authentifier la clé publique ou la référence.
    6. Si un contrôle échoue, arrêter l'installation et signaler l'anomalie.
    7. Si les contrôles réussissent, appliquer la procédure d'installation.
    8. Documenter le résultat sans exposer de secret.

La procédure est générale. Les outils précis et les contrôles requis dépendent du système et des consignes de l'éditeur.

## 20. Exercices d'application avec corrections

### Exercice 1 — Identifier le bon mécanisme

Un technicien veut rendre un fichier illisible aux personnes qui le récupèrent sans autorisation. Quel mécanisme répond directement à ce besoin ?

A. Calculer SHA-256  
B. Encoder le fichier en Base64  
C. Chiffrer le fichier avec un mécanisme adapté et gérer la clé  
D. Renommer le fichier avec une extension différente

**Correction : C.** Le chiffrement vise la confidentialité. Le hachage calcule une empreinte, Base64 est un encodage et le nom du fichier ne protège pas les données.

### Exercice 2 — Interpréter une différence d'empreinte

L'empreinte du fichier téléchargé ne correspond pas à la référence officielle. Quelle conclusion est justifiée ?

A. Une attaque est forcément confirmée.  
B. Le fichier ne correspond pas à la référence pour la fonction utilisée ; il faut examiner la cause.  
C. Le fichier est forcément inoffensif.  
D. Il suffit de renommer le fichier.

**Correction : B.** La différence signale un problème de correspondance, mais ne révèle pas seule si la cause est une erreur de version, une corruption ou une modification malveillante.

### Exercice 3 — Choisir une fonction de hachage

Un nouveau script doit calculer l'empreinte d'un fichier. Quel choix est adapté pour un contrôle courant, sous réserve des exigences de l'application ?

A. MD5 pour tout nouveau système  
B. SHA-1 uniquement parce qu'il est ancien  
C. SHA-256 pour un usage d'intégrité général, selon la politique et le protocole  
D. Base64

**Correction : C.** SHA-256 est un choix courant pour vérifier l'intégrité. Le choix réel doit respecter le protocole et les recommandations applicables ; MD5 et SHA-1 ne conviennent pas pour de nouvelles garanties fortes de résistance aux collisions.

### Exercice 4 — Comprendre la collision

Deux messages différents produisent la même empreinte. Comment appelle-t-on ce phénomène ?

A. Une collision  
B. Un déchiffrement  
C. Un encodage  
D. Une révocation

**Correction : A.** Une collision est une paire de messages différents qui produit la même empreinte. Une fonction robuste vise à rendre la recherche de collisions impraticable.

### Exercice 5 — Signature et confiance

Une signature est vérifiée avec succès à l'aide d'une clé publique que l'organisation n'a jamais authentifiée. Quelle affirmation est la plus juste ?

A. L'identité du signataire est automatiquement garantie.  
B. Le fichier est nécessairement sûr.  
C. La signature correspond aux données et à cette clé, mais la confiance dans l'identité liée à la clé reste à établir.  
D. Le fichier est automatiquement chiffré.

**Correction : C.** La vérification mathématique et l'association de la clé à une identité sont deux étapes distinctes. La signature n'assure pas non plus que le contenu soit exempt de défauts.

### Exercice 6 — HMAC ou signature

Deux services partagent un secret et veulent authentifier leurs messages. Quel mécanisme convient à ce besoin ?

A. HMAC avec la clé secrète partagée, correctement mis en œuvre  
B. SHA-256 simple sans clé  
C. Un nom de fichier secret  
D. Une image de signature

**Correction : A.** Le HMAC convient à l'authentification de messages entre parties qui partagent un secret. Un hachage ordinaire ne prouve pas que l'émetteur connaît un secret.

### Exercice 7 — Protéger les clés

Quelle partie de la paire de clés doit être protégée contre la divulgation ?

A. La clé publique uniquement  
B. La clé privée  
C. Le nom du fichier  
D. Le certificat public en toutes circonstances

**Correction : B.** La clé privée permet de signer. Si elle est compromise, l'attaquant peut produire des signatures que les systèmes risquent d'accepter tant que la compromission n'est pas traitée.

### Exercice 8 — Réagir à un échec

La signature d'un installateur ne peut pas être vérifiée. Quelle est la meilleure réaction ?

A. Ignorer l'avertissement si le nom du fichier semble correct.  
B. Désactiver durablement la vérification.  
C. Suspendre l'installation, vérifier la source et la version, puis suivre la procédure de diagnostic.  
D. Renommer l'installateur.

**Correction : C.** L'échec doit être compris. Il peut résulter d'une signature incorrecte, d'un mauvais fichier, d'une erreur de format ou d'une clé non approuvée. L'installation ne doit pas continuer en contournant la protection.

### Exercice 9 — Stockage de mots de passe

Pourquoi ne faut-il pas stocker des mots de passe avec un simple SHA-256 sans mécanisme supplémentaire ?

A. Parce que SHA-256 chiffre les mots de passe.  
B. Parce que SHA-256 est rapide et facilite les essais massifs sur des mots de passe devinés.  
C. Parce que SHA-256 produit une empreinte différente à chaque calcul.  
D. Parce que l'empreinte a toujours la taille du mot de passe.

**Correction : B.** Le stockage des mots de passe doit utiliser une fonction spécialisée et correctement paramétrée, telle qu'Argon2id, scrypt, bcrypt ou PBKDF2 selon les exigences, avec un sel unique.

### Exercice 10 — Authentifier une clé

Un fichier contient une signature et une clé publique. La signature est mathématiquement valide, mais personne ne sait à qui appartient la clé. Quelle étape manque-t-il ?

A. Vérifier l'identité ou la provenance de la clé publique au moyen d'un mécanisme de confiance adapté.  
B. Ajouter une extension .secure.  
C. Calculer la taille du document.  
D. Encoder la clé publique en Base64 et lui faire confiance.

**Correction : A.** La validité cryptographique ne suffit pas à établir l'identité du signataire. Il faut un certificat validé, un ancrage de confiance ou un autre mécanisme adapté à l'écosystème.

## 21. Défi final — Sécuriser la publication d'un outil

### 21.1. Scénario

L'entreprise NetForma développe un agent de supervision. Chaque mois, l'équipe publie une archive contenant l'agent et ses fichiers de configuration. Les techniciens téléchargent l'archive pour l'installer sur des dizaines de postes.

L'équipe publie actuellement le fichier, sa version et une note contenant une empreinte SHA-256 dans le même répertoire. Les techniciens ne savent pas comment authentifier la note. Un compte de publication est partagé. La clé privée de signature éventuelle est stockée sur un poste accessible à plusieurs personnes. Aucune procédure n'indique ce qu'il faut faire en cas d'échec. Enfin, l'équipe pense qu'un fichier signé est nécessairement exempt de vulnérabilités.

### 21.2. Travail demandé

Propose un plan qui répond aux questions suivantes :
1. Comment vérifier l'intégrité du fichier publié ?
2. Comment renforcer la confiance dans l'empreinte de référence ?
3. Comment introduire la signature numérique lorsque l'écosystème le permet ?
4. Comment protéger la clé privée ?
5. Que doivent faire les techniciens si la vérification échoue ?
6. Quelles limites faut-il expliquer au sujet d'une signature valide ?
7. Comment améliorer la traçabilité de la publication ?

### 21.3. Correction détaillée

**Identifier précisément l'artefact.** Chaque publication doit identifier la version et la plateforme visées. L'équipe doit s'assurer que les notes, empreintes et signatures correspondent au bon fichier. Les noms seuls ne suffisent pas : les versions et artefacts doivent être distingués sans ambiguïté.

**Calculer SHA-256 à la publication.** Le processus peut calculer l'empreinte de l'archive finale, celle que les techniciens téléchargeront. Il faut éviter de calculer l'empreinte sur une version intermédiaire puis de modifier le contenu sans recalculer la valeur.

**Protéger la référence.** Publier une empreinte dans un emplacement que le même compte peut modifier ne garantit pas son authenticité. L'équipe doit utiliser le mécanisme de confiance adapté à son infrastructure : manifeste signé, dépôt authentifié et correctement configuré, ou autre méthode documentée. Les techniciens doivent pouvoir vérifier que la référence appartient bien à l'éditeur attendu.

**Utiliser une signature numérique.** La signature doit être générée sur l'artefact ou dans le format de publication prévu, puis vérifiée avec l'outil approprié. La distribution de la clé publique ou du certificat doit s'appuyer sur un mécanisme fiable. Les techniciens ne doivent pas faire confiance à une clé inconnue simplement parce qu'elle se trouve près du fichier.

**Protéger la clé privée.** Elle doit être accessible uniquement aux personnes et processus autorisés. L'équipe peut s'appuyer sur un service de signature, un coffre ou un module de sécurité adapté. Elle doit contrôler les accès, journaliser les opérations, prévoir le renouvellement et documenter la procédure en cas de compromission. Le compte partagé doit être remplacé par des identités et permissions permettant d'attribuer les actions.

**Définir une procédure d'échec.** Si l'empreinte ne correspond pas ou si la signature ne se vérifie pas, l'installation doit être suspendue. Le technicien vérifie la version, la source, la référence et les messages de l'outil, puis informe l'équipe responsable. Aucun contournement ne doit être réalisé simplement pour gagner du temps.

**Conserver des preuves de publication.** L'équipe doit documenter qui a approuvé la version, quel artefact a été publié, quelle clé a servi à signer et quels contrôles ont été effectués. Les journaux doivent être protégés contre les modifications non autorisées.

**Décrire les limites.** Une signature valide indique que l'artefact correspond à la signature vérifiée selon la clé et le format utilisés. Elle ne prouve pas que le logiciel ne contient aucune vulnérabilité, que le processus de construction est toujours sûr ou que l'appareil de l'utilisateur est protégé contre toute attaque.

### 21.4. Exemple de feuille de route

- **Phase A — Standardiser les artefacts :** définir les noms, versions, sources et formats de publication.
- **Phase B — Automatiser le hachage :** calculer SHA-256 après la construction finale.
- **Phase C — Authentifier la référence :** adopter un canal de confiance documenté.
- **Phase D — Protéger la clé :** supprimer le partage incontrôlé et journaliser les opérations.
- **Phase E — Automatiser la vérification :** valider la signature avant l'installation ou la diffusion en production.
- **Phase F — Tester la réaction :** simuler une empreinte incorrecte, une clé renouvelée et une signature invalide en environnement de test.
- **Phase G — Maintenir le dispositif :** revoir les clés, permissions, bibliothèques et procédures.

### 21.5. Critères d'autoévaluation

Le défi est réussi si tu peux expliquer pourquoi l'empreinte doit provenir d'une source fiable, la différence entre intégrité et authenticité, les rôles distincts des clés privée et publique, la nécessité d'authentifier une clé publique, la réaction appropriée en cas d'échec, les limites d'une signature valide et le rôle de la protection des clés et de la traçabilité.

## 22. Synthèse du cours

Le hachage cryptographique calcule une empreinte de longueur définie à partir d'un contenu. Il aide à comparer un fichier avec une référence et à détecter les différences, mais ne prouve pas à lui seul qui a créé le fichier ni si le contenu est sans danger.

Une fonction de hachage cryptographique doit viser la résistance à la préimage, à la seconde préimage et aux collisions. SHA-256 appartient à SHA-2 et constitue un choix courant pour les vérifications d'intégrité générales. MD5 et SHA-1 ne doivent pas servir de base à de nouvelles garanties fortes de résistance aux collisions.

La confiance dans une empreinte dépend de la provenance de la référence. Si un attaquant peut remplacer en même temps le fichier et la référence, une comparaison seule peut ne pas révéler le remplacement.

Le hachage des mots de passe est un autre problème. Il ne faut pas utiliser une fonction rapide comme SHA-256 seule pour stocker des mots de passe. Il faut privilégier une fonction spécialisée, correctement configurée, associée à un sel unique.

Le HMAC permet d'authentifier des messages entre parties qui partagent un secret. Une signature numérique est produite avec une clé privée et vérifiée avec une clé publique correspondante. Elle peut fournir une preuve cryptographique de l'intégrité des données signées et de leur relation avec cette clé.

La vérification d'une signature et la confiance dans l'identité du signataire sont deux choses distinctes. Il faut authentifier la clé publique ou le certificat, appliquer la politique de validation et examiner les résultats.

Enfin, une signature valide ne garantit pas qu'un logiciel soit sans défaut. La sécurité combine des mécanismes cryptographiques correctement utilisés, une gestion rigoureuse des clés, une chaîne de publication contrôlée, des procédures de vérification et une bonne réaction en cas d'échec.

## 23. Glossaire

**Algorithme de hachage :** fonction qui calcule une empreinte à partir de données.

**Authenticité :** propriété qui permet d'établir qu'une donnée ou une entité correspond à ce qui est attendu, selon un mécanisme de confiance.

**Certificat numérique :** document qui associe une clé publique à une identité ou à des attributs selon un format et une politique définis.

**Chiffrement :** transformation destinée à protéger la confidentialité et qui nécessite le mécanisme de déchiffrement approprié.

**Clé privée :** partie secrète d'une paire de clés utilisée pour des opérations telles que la création de signatures.

**Clé publique :** partie distribuable utilisée pour vérifier des signatures.

**Collision :** situation où deux entrées différentes produisent la même empreinte.

**Empreinte cryptographique :** valeur calculée à partir des données par une fonction de hachage.

**Effet avalanche :** propriété selon laquelle une petite modification en entrée produit un changement important et imprévisible de l'empreinte.

**HMAC :** code d'authentification de message calculé avec une fonction de hachage et une clé secrète partagée.

**Intégrité :** protection contre les modifications non autorisées ou non détectées.

**Préimage :** donnée qui produit une empreinte donnée avec une fonction de hachage.

**Résistance aux collisions :** propriété recherchée qui rend impraticable la découverte de deux entrées différentes produisant la même empreinte.

**SHA-256 :** fonction de hachage de la famille SHA-2 qui produit une empreinte de 256 bits.

**SHA-3 :** famille de fonctions de hachage normalisées, construite différemment de SHA-2.

**Signature numérique :** résultat cryptographique produit avec une clé privée et vérifié avec une clé publique correspondante.

**Sel :** valeur associée au calcul d'un vérificateur de mot de passe pour limiter certaines attaques précalculées et différencier les vérificateurs.

**Vérificateur de mot de passe :** valeur et mécanisme utilisés pour vérifier un mot de passe sans conserver directement le mot de passe en clair.

**Chaîne de confiance :** relations qui permettent de relier une clé ou un certificat à une autorité ou identité reconnue.

## 24. Ressources pour approfondir

Consulte les versions et recommandations adaptées à ton contexte avant de prendre une décision de production.

- **NIST — Secure Hash Standard, FIPS 180-4 :** spécification officielle de SHA-2.  
  https://csrc.nist.gov/pubs/fips/180-4/upd1/final

- **NIST — SHA-3 Standard, FIPS 202 :** spécification de SHA-3.  
  https://csrc.nist.gov/pubs/fips/202/final

- **NIST — Digital Signature Standard, FIPS 186-5 :** référence sur les signatures numériques.  
  https://csrc.nist.gov/pubs/fips/186-5/final

- **RFC Editor — RFC 8032, EdDSA :** description technique d'EdDSA, incluant Ed25519 et Ed448.  
  https://www.rfc-editor.org/rfc/rfc8032

- **Python — Documentation de hashlib :** utilisation des fonctions de hachage en Python.  
  https://docs.python.org/3/library/hashlib.html

- **Python Cryptographic Authority — Documentation de cryptography :** bibliothèque et guides pour utiliser des mécanismes cryptographiques en Python.  
  https://cryptography.io/en/latest/

- **OWASP — Password Storage Cheat Sheet :** conseils sur le stockage des mots de passe et les fonctions spécialisées.  
  https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

- **OWASP — Cryptographic Storage Cheat Sheet :** conseils sur l'utilisation des mécanismes cryptographiques dans les applications.  
  https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html

Le but n'est pas simplement de calculer une empreinte ou d'afficher « signature valide », mais de savoir précisément ce que le résultat établit, ce qu'il n'établit pas et comment protéger la confiance dans les clés et les références.

**Fin du cours : Hachage et signatures.**