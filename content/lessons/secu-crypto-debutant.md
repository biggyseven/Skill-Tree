# Cryptographie

> **Encadré de mise en contexte**
>
> Tu es technicien informatique dans une entreprise qui utilise une plateforme de formation en ligne. Les apprenants possèdent des comptes personnels, les enseignants publient les cours et les administrateurs gèrent les données enregistrées dans une base de données.
>
> Un jour, l'entreprise doit transmettre un fichier contenant des informations confidentielles à un partenaire. Elle doit également protéger les fichiers stockés sur ses ordinateurs portables, vérifier que les téléchargements n'ont pas été modifiés et empêcher qu'un attaquant puisse récupérer directement les mots de passe des utilisateurs après le vol d'une base de données.
>
> Ces problèmes sont différents. Le chiffrement permet de rendre des données illisibles sans la clé appropriée. Une fonction de hachage permet de calculer une empreinte. Une signature numérique peut contribuer à vérifier l'intégrité d'un document et son origine cryptographique. Le stockage sécurisé des mots de passe repose sur des mécanismes spécialisés.
>
> La cryptographie fournit les outils permettant de répondre à ces besoins. Mais elle n'est efficace que si elle est correctement choisie, configurée et utilisée. Un algorithme puissant ne protège pas un système si les clés sont divulguées, si les permissions sont incorrectes ou si l'application contourne les vérifications.

## 1. Comprendre la cryptographie

### 1.1. Définition

La **cryptographie** est une discipline qui utilise des méthodes mathématiques et informatiques pour protéger des informations et fournir certains services de sécurité.

Elle intervient dans de nombreux usages quotidiens : connexion à un site Web, applications bancaires, messagerie sécurisée, réseaux privés virtuels, stockage chiffré, mises à jour logicielles et authentification.

Lorsque tu consultes un site Web utilisant HTTPS, des mécanismes cryptographiques contribuent à protéger les échanges entre ton navigateur et le serveur. Lorsque tu déverrouilles un ordinateur doté d'un disque chiffré, un mécanisme cryptographique contribue à protéger les fichiers contre un accès non autorisé au support de stockage.

La cryptographie ne sert pas uniquement à cacher des textes. Elle peut également contribuer à détecter les modifications d'une information, à vérifier une signature ou à établir un secret partagé entre deux systèmes.

### 1.2. Cryptographie et cybersécurité

La cybersécurité vise à protéger les systèmes, les réseaux, les données et les services. La cryptographie représente l'un des moyens d'atteindre ces objectifs.

Pour comprendre son rôle, reprenons les propriétés CIA étudiées dans le premier cours.

**Confidentialité.** Le chiffrement peut rendre une information illisible pour une personne qui ne possède pas la clé nécessaire.

**Intégrité.** Des mécanismes cryptographiques tels que les codes d'authentification de message et les signatures numériques peuvent aider à détecter une modification non autorisée.

**Disponibilité.** La cryptographie ne garantit pas directement qu'un service reste accessible. Une mauvaise gestion des clés peut même rendre des données irrécupérables. Les procédures de récupération et la gestion du cycle de vie des clés sont donc indispensables.

La cryptographie contribue ainsi à plusieurs objectifs, mais elle ne remplace pas le contrôle d'accès, les sauvegardes, la maintenance ni la supervision.

### 1.3. Un exemple simple

Imaginons qu'Alice souhaite envoyer un document confidentiel à Bob. Elle ne veut pas qu'un tiers puisse lire son contenu pendant le transfert.

Sans chiffrement, le document peut être lisible si quelqu'un parvient à intercepter une copie exploitable. Avec un mécanisme de chiffrement correctement choisi, Alice transforme le document en une suite de données chiffrées. Bob peut ensuite retrouver le contenu grâce à la clé nécessaire.

```text
Document lisible
       |
       v
Chiffrement + clé
       |
       v
Données chiffrées
       |
       | Transmission
       v
Données chiffrées
       |
       v
Déchiffrement + clé
       |
       v
Document lisible
```

Ce schéma montre le principe général. Dans les systèmes réels, d'autres éléments peuvent être nécessaires : paramètres de chiffrement, nonces, clés de session, mécanismes d'authentification ou certificats.

Il ne faut pas non plus oublier que le document peut rester accessible avant son chiffrement ou après son déchiffrement. La sécurité dépend donc de l'ensemble du système.

### 1.4. Les limites de la cryptographie

Un mécanisme cryptographique peut fonctionner correctement tout en étant mal intégré à une application.

Par exemple, un fichier peut être chiffré, mais son mot de passe peut être écrit dans un document conservé au même endroit. Une application peut protéger les communications, mais laisser tous les utilisateurs consulter toutes les données. Un fichier peut être signé, mais l'utilisateur peut ne pas vérifier l'identité associée à la clé publique.

Ces situations montrent que la cryptographie ne doit pas être considérée comme une protection magique.

Il faut toujours se demander :

- quelle information doit être protégée ;
- contre quel type de menace ;
- quel mécanisme est adapté ;
- comment les clés seront protégées ;
- comment les identités seront vérifiées ;
- comment le fonctionnement sera testé ;
- comment récupérer les informations en cas de perte de clé.

Ce raisonnement permet de choisir une solution en fonction du besoin plutôt que de sélectionner un algorithme simplement parce que son nom est connu.

## 2. Le vocabulaire fondamental

### 2.1. Texte en clair

Le **texte en clair**, ou *plaintext*, désigne les données dans leur forme lisible ou exploitable avant chiffrement.

Il peut s'agir d'un texte, d'une image, d'un fichier PDF, d'un enregistrement audio, d'une base de données ou d'un autre type de contenu.

Le terme « clair » ne signifie pas nécessairement que les données sont présentées comme une phrase. Un fichier binaire peut aussi être considéré comme des données en clair si son contenu est directement exploitable par le programme qui l'utilise.

Exemple :

```text
Montant : 250000 FCFA
Destinataire : Entreprise B
Référence : CMD-1048
```

Si ces informations sont stockées dans un fichier lisible sans protection adaptée, une personne qui obtient accès au fichier peut être en mesure de les consulter.

### 2.2. Texte chiffré

Le **texte chiffré**, ou *ciphertext*, est le résultat produit par un mécanisme de chiffrement.

Il contient les données transformées à l'aide d'un algorithme et d'une clé. Le résultat peut sembler illisible pour une personne qui ne connaît pas le mécanisme et ne possède pas les éléments nécessaires au déchiffrement.

Le texte chiffré n'est pas nécessairement une suite de caractères étranges. Il peut s'agir d'un fichier binaire, d'une chaîne encodée ou d'un ensemble de données contenant plusieurs champs.

Il ne faut pas non plus croire que l'absence de lisibilité suffit à prouver que les données sont protégées. Une suite apparemment incompréhensible peut être simplement encodée et donc facilement décodée.

### 2.3. Algorithme cryptographique

Un algorithme cryptographique est une méthode définie permettant d'effectuer une opération de sécurité.

L'algorithme décrit les règles de transformation ou de calcul. Dans de nombreux systèmes, sa sécurité dépend de la qualité de la clé utilisée et des conditions d'application.

Les algorithmes modernes sont conçus pour être analysés publiquement. La sécurité ne devrait pas reposer sur le secret de l'algorithme, mais sur les propriétés du mécanisme et la protection des clés.

Cacher le nom d'un algorithme ou inventer une transformation personnelle ne constitue pas une méthode fiable de protection.

### 2.4. Clé cryptographique

Une **clé cryptographique** est une donnée utilisée par un algorithme pour effectuer une opération de chiffrement, de déchiffrement, de signature, de vérification ou une autre opération cryptographique.

La forme et le rôle d'une clé dépendent du mécanisme. Une clé symétrique utilisée pour chiffrer un fichier est généralement secrète. Une clé publique utilisée pour vérifier une signature peut être diffusée, tandis que la clé privée correspondante doit être protégée.

La sécurité dépend fortement de la génération, du stockage et de l'utilisation des clés.

### 2.5. Chiffrement et déchiffrement

Le **chiffrement** transforme les données en une forme protégée. Le **déchiffrement** retrouve les données d'origine grâce à la clé requise et aux paramètres appropriés.

Ces opérations sont généralement réversibles pour un utilisateur autorisé disposant des bons éléments.

Le chiffrement n'est donc pas un mécanisme destiné à supprimer définitivement le contenu. Son objectif est de contrôler l'accès à ce contenu.

### 2.6. Décryptage

Dans le langage courant, les termes « déchiffrement » et « décryptage » sont parfois employés de manière interchangeable. Dans le vocabulaire technique traditionnel, le décryptage désigne souvent la recherche du texte en clair sans disposer normalement de la clé nécessaire.

Il peut s'agir de l'analyse d'un chiffrement faible, de l'exploitation d'une mauvaise implémentation ou de la recherche d'une clé à l'aide de méthodes d'analyse.

Cette distinction est utile pour apprendre, même si les usages professionnels et les traductions ne sont pas toujours parfaitement uniformes.

## 3. Chiffrement, encodage et obfuscation : trois notions différentes

### 3.1. L'encodage

L'encodage transforme des données pour les représenter selon un format donné. Il répond souvent à un besoin de compatibilité, de transport ou de stockage.

Par exemple, Base64 permet de représenter certaines données binaires sous forme de caractères utilisables dans des environnements textuels.

Cependant, Base64 ne chiffre pas les données et ne nécessite aucun secret pour décoder le résultat.

Exemple conceptuel :

```text
Texte : BONJOUR
Encodage Base64 : Qk9OSk9VUg==
```

La chaîne encodée est différente du texte initial, mais elle ne constitue pas une protection cryptographique. Une personne qui connaît Base64 peut retrouver le texte sans clé.

Base64 est utile dans certains formats et protocoles, mais ne doit jamais être utilisé pour prétendre protéger un mot de passe ou un document confidentiel.

### 3.2. L'obfuscation

L'obfuscation consiste à rendre un contenu plus difficile à comprendre, notamment en modifiant sa présentation ou sa structure.

Un programme peut être transformé afin de rendre son code moins lisible. Un nom de variable peut être remplacé par une séquence peu explicite ou une structure peut être compliquée.

L'obfuscation peut compliquer une analyse superficielle, mais elle n'offre pas les garanties d'un mécanisme cryptographique éprouvé. Elle ne doit pas être considérée comme un moyen suffisant de protéger des secrets.

### 3.3. Le chiffrement

**Schéma pédagogique — Le chiffrement protège le contenu avec une clé et un algorithme.**

~~~text
Texte en clair + cle
         |
         v
   [Algorithme de chiffrement]
         |
         v
   Texte chiffre
         |
         | cle et algorithme adaptes
         v
   [Dechiffrement autorise]
         |
         v
   Texte en clair

Le chiffrement n'empêche pas à lui seul la suppression ou le blocage d'un message.
~~~


Le chiffrement utilise un mécanisme cryptographique et une clé. Les personnes qui ne possèdent pas les éléments nécessaires ne devraient pas pouvoir retrouver efficacement le contenu, dans les conditions prévues par le système.

La différence essentielle est donc la suivante :

| Méthode | Objectif principal | Nécessite-t-elle une clé secrète pour retrouver le contenu ? |
|---|---|---|
| Encodage | Représentation et compatibilité | Non |
| Obfuscation | Rendre la compréhension moins immédiate | Pas nécessairement |
| Chiffrement | Protéger l'accès au contenu | Oui, selon le mécanisme |

Une entreprise ne doit pas stocker un secret simplement encodé ou obfusqué en croyant qu'il est chiffré.

## 4. Le chiffrement symétrique

### 4.1. Définition

Le **chiffrement symétrique** utilise une clé secrète commune pour chiffrer et déchiffrer les données.

Alice et Bob doivent tous deux disposer de la clé, ou du moyen cryptographique qui permet d'effectuer les opérations nécessaires. Ils doivent également empêcher les personnes non autorisées de récupérer cette clé.

Le chiffrement symétrique est généralement efficace pour traiter de grandes quantités de données. Il est couramment utilisé pour protéger les fichiers, les disques et les communications.

### 4.2. Exemple de fonctionnement

**Schéma pédagogique — Le chiffrement symétrique utilise le même secret aux deux extrémités.**

~~~text
Emetteur                           Destinataire
   |                                      ^
   | texte + cle K                        | texte lisible
   v                                      |
[Chiffrement avec K]                [Dechiffrement avec K]
   |                                      ^
   +---------- texte chiffre -------------+

Les deux côtés doivent obtenir la clé K de façon sûre.
~~~


```text
             Alice
        Document en clair
                |
                v
        Chiffrement symétrique
                |
                | Clé secrète K
                v
          Texte chiffré
                |
                | Canal de communication
                v
          Texte chiffré
                |
                | Clé secrète K
                v
        Déchiffrement symétrique
                |
                v
              Bob
        Document en clair
```

Le schéma suppose qu'Alice et Bob possèdent déjà la bonne clé de manière sécurisée.

C'est précisément l'une des difficultés du chiffrement symétrique : comment partager le secret au départ sans qu'un tiers puisse le récupérer ?

Si Alice envoie la clé par le même canal non protégé que le document chiffré, l'attaquant peut récupérer les deux éléments. Le contenu peut alors être exposé.

### 4.3. Avantages

Le chiffrement symétrique présente plusieurs avantages :

- il est efficace pour chiffrer des volumes importants ;
- il peut être utilisé pour protéger des fichiers et des disques ;
- il est adapté au chiffrement des données de session ;
- il est largement pris en charge par les bibliothèques et les systèmes modernes.

Sa principale difficulté opérationnelle réside dans la protection et la distribution des clés.

### 4.4. L'algorithme AES

AES signifie *Advanced Encryption Standard*. C'est un algorithme de chiffrement symétrique normalisé dans le standard FIPS 197 du NIST. La version mise à jour en 2023 a apporté des améliorations éditoriales sans modifier techniquement l'algorithme défini. [Référence officielle NIST sur AES](https://csrc.nist.gov/pubs/fips/197/final).

AES utilise une taille de bloc de 128 bits et prend en charge les clés de 128, 192 ou 256 bits.

Ces tailles ne signifient pas que le fichier doit mesurer exactement 128 bits. Les modes d'utilisation permettent de traiter des contenus de tailles variées.

La sécurité dépend aussi du mode de chiffrement, des paramètres, de la génération des clés et de leur gestion. Choisir AES ne suffit donc pas à garantir une solution complète.

### 4.5. AES-128 et AES-256

Les appellations AES-128 et AES-256 correspondent à la taille de la clé.

Une clé de 128 bits possède \(2^{128}\) valeurs possibles en théorie. Une clé de 256 bits possède \(2^{256}\) valeurs possibles.

Ces nombres sont extrêmement grands. Mais il serait simpliste de déduire que chaque système utilisant AES-256 est automatiquement plus sûr qu'un système utilisant AES-128 : la mise en œuvre, les données de départ, les paramètres, les clés et les risques restent essentiels.

Pour un système réel, le choix doit suivre des recommandations reconnues et les exigences de l'environnement.

### 4.6. Pourquoi ne pas inventer son propre algorithme ?

Imaginons un programme qui remplace chaque lettre par une autre, inverse l'ordre du texte puis ajoute un numéro au début.

Cette transformation peut donner l'impression que le texte est protégé. Pourtant, elle peut être analysée, reproduite et parfois inversée sans grand effort.

Les algorithmes cryptographiques modernes sont soumis à des analyses mathématiques approfondies et à de nombreuses années d'examen. Une méthode inventée rapidement ne bénéficie pas de ce niveau de confiance.

En pratique, il faut utiliser des bibliothèques cryptographiques maintenues, des algorithmes reconnus et des configurations adaptées, plutôt que concevoir un chiffrement artisanal.

## 5. Modes de chiffrement et protection de l'intégrité

### 5.1. Pourquoi existe-t-il des modes ?

AES est un chiffrement par blocs. Pour protéger des données plus longues qu'un bloc, il faut utiliser un mode de chiffrement approprié.

Les modes ont des propriétés différentes. Certains ne protègent que la confidentialité et ne garantissent pas l'authenticité du contenu. D'autres associent la confidentialité à une protection permettant de détecter une altération.

Le choix du mode est une partie importante de la conception cryptographique.

### 5.2. Chiffrer ne garantit pas toujours que les données n'ont pas été modifiées

Supposons qu'un document chiffré soit transmis à un destinataire. Celui-ci doit pouvoir vérifier non seulement que son contenu reste secret, mais également que les données reçues n'ont pas été modifiées de manière indétectable.

Un mécanisme de chiffrement sans authentification ne fournit pas nécessairement cette garantie.

C'est pourquoi les applications modernes devraient privilégier des mécanismes de chiffrement authentifié lorsqu'ils sont adaptés à leur besoin.

### 5.3. AES-GCM

AES-GCM est un mode qui permet d'obtenir le chiffrement et une vérification d'authenticité des données au moyen d'une étiquette d'authentification.

Avec une configuration correcte, le destinataire peut détecter qu'un contenu chiffré ou certains paramètres associés ont été modifiés. Le déchiffrement doit échouer si la vérification d'authenticité ne passe pas.

La sécurité d'AES-GCM dépend notamment de la bonne génération et de l'utilisation correcte du nonce. La réutilisation dangereuse d'un nonce avec la même clé peut gravement compromettre la sécurité.

Un débutant ne devrait pas concevoir manuellement la gestion de ces paramètres. Il doit utiliser une bibliothèque réputée et suivre sa documentation.

### 5.4. Le nonce

Un nonce est une valeur utilisée une fois dans un contexte donné, selon les exigences du mécanisme cryptographique. Le terme provient de l'expression anglaise *number used once*.

Un nonce n'est pas systématiquement une clé secrète. Son rôle et ses exigences dépendent de l'algorithme et de son mode.

Pour certaines constructions, il est essentiel d'empêcher la réutilisation d'un nonce avec une même clé. Il ne faut pas supposer que changer le nom du fichier ou la date du système suffit à garantir cette propriété.

Les bibliothèques cryptographiques fournissent généralement des moyens de générer et de gérer ces paramètres. Il faut respecter leurs instructions.

### 5.5. Les modes anciens ou inadaptés

Le choix d'un mode ancien, mal utilisé ou inadapté peut introduire des faiblesses même si l'algorithme sous-jacent est reconnu.

Par exemple, le mode ECB ne doit pas être utilisé pour le chiffrement général de données sensibles, car il peut révéler des structures répétitives du contenu.

Les modes qui ne fournissent pas l'authenticité doivent être complétés par un mécanisme adapté lorsque l'intégrité est nécessaire. Cette intégration est délicate et doit être confiée à des bibliothèques éprouvées.

Pour les applications modernes, il est préférable de choisir une construction authentifiée recommandée par une documentation fiable plutôt que de combiner arbitrairement plusieurs primitives.

## 6. Le chiffrement asymétrique

### 6.1. Définition

Le **chiffrement asymétrique**, aussi appelé cryptographie à clé publique, repose sur une paire de clés associées : une clé publique et une clé privée.

La clé publique peut être communiquée à d'autres personnes. La clé privée doit rester sous le contrôle de son propriétaire ou du système autorisé à l'utiliser.

Les mécanismes asymétriques servent à plusieurs usages, notamment le chiffrement, l'établissement de secrets partagés et les signatures numériques, selon l'algorithme utilisé.

La cryptographie à clé publique est décrite dans le glossaire du NIST. [Définition officielle de la cryptographie à clé publique](https://csrc.nist.gov/glossary/term/public_key_cryptography).

### 6.2. Exemple de chiffrement à clé publique

Dans un scénario pédagogique simplifié, Bob possède une paire de clés. Il communique sa clé publique à Alice, tout en conservant sa clé privée.

Alice utilise la clé publique de Bob dans le mécanisme prévu pour protéger le message à destination de Bob.

Le contenu chiffré est transmis. Bob utilise ensuite sa clé privée pour retrouver le contenu, selon le mécanisme employé.

```text
Bob
├── Clé publique : peut être communiquée
└── Clé privée   : doit rester protégée

Alice
    |
    | Utilise la clé publique de Bob
    v
Message protégé pour Bob
    |
    v
Transmission
    |
    v
Bob utilise sa clé privée
    |
    v
Message récupéré
```

Le schéma est volontairement général. Les algorithmes à clé publique ne fonctionnent pas tous de la même manière.

### 6.3. L'importance de l'authenticité de la clé publique

Un problème apparaît si Alice reçoit une clé publique provenant d'un attaquant qui prétend être Bob.

Alice peut chiffrer son message pour cette fausse clé. L'attaquant peut alors être capable de lire le contenu ou de le transmettre à Bob, selon le scénario.

La cryptographie ne supprime donc pas le besoin de vérifier les identités. Il faut un moyen fiable de relier une clé publique à la personne, au service ou à l'organisation attendue.

C'est l'un des rôles des certificats numériques et des mécanismes de confiance étudiés plus loin.

### 6.4. La clé privée n'est pas le mot de passe du compte

Une clé privée est un élément cryptographique. Un mot de passe est un secret mémorisé ou une valeur utilisée pour authentifier un utilisateur.

Un mot de passe peut éventuellement protéger l'utilisation d'une clé privée, mais les deux concepts restent distincts.

Une clé privée peut être stockée dans un fichier, un composant matériel ou un service spécialisé. Sa protection dépend de la méthode de stockage et des mécanismes d'accès.

Si une clé privée est compromise, changer simplement le mot de passe d'un compte ne suffit pas toujours. Il faut déterminer quel rôle joue cette clé et comment révoquer ou remplacer la confiance qui lui est accordée.

### 6.5. RSA et la cryptographie à courbes elliptiques

RSA et différentes constructions fondées sur des courbes elliptiques sont des familles de mécanismes asymétriques.

Leur utilisation dépend de l'objectif : chiffrement, signature, échange ou établissement de clés, et d'autres fonctions spécialisées.

Leur sécurité repose sur des hypothèses mathématiques et des paramètres adaptés. Les algorithmes et tailles de clés doivent être choisis selon les recommandations actuelles, la bibliothèque et les contraintes du système.

Un débutant ne doit pas retenir un nombre de bits isolé comme une garantie universelle. Les pratiques évoluent, et les exigences peuvent varier selon le protocole, l'algorithme et la durée pendant laquelle les informations doivent rester protégées.

Il faut utiliser des bibliothèques maintenues et suivre des recommandations techniques actualisées.

## 7. Pourquoi les systèmes combinent chiffrement symétrique et asymétrique

### 7.1. Un problème de performance et de distribution

Le chiffrement symétrique est efficace pour protéger de grands volumes de données, mais il faut gérer le secret partagé.

La cryptographie asymétrique permet d'utiliser des paires de clés et facilite certains mécanismes d'établissement de secrets ou de protection des échanges. Toutefois, elle n'est pas systématiquement le meilleur moyen de chiffrer directement de très gros fichiers.

Les systèmes modernes combinent donc souvent plusieurs mécanismes.

### 7.2. Le chiffrement hybride

**Schéma pédagogique — Les protocoles modernes combinent établissement de clés, authentification et chiffrement symétrique des données.**

~~~text
[Client] <---- certificat / echange de cles ----> [Serveur]
    |                                                   |
    +-------- authentification et secret partage -------+
                            |
                            v
                 [Cle(s) de session]
                            |
                            v
             Donnees protegees par chiffrement symetrique

Les détails exacts dépendent du protocole et de sa suite cryptographique.
~~~


Dans une architecture hybride, un mécanisme à clé publique ou un mécanisme d'établissement de clés permet aux participants d'obtenir un secret partagé ou de protéger une clé de session. Le chiffrement symétrique utilise ensuite cette clé pour protéger les données.

Un modèle conceptuel :

```text
1. Établissement d'un secret de session
                 |
                 v
2. Dérivation d'une clé symétrique
                 |
                 v
3. Chiffrement authentifié des données
                 |
                 v
4. Transmission des données protégées
```

Les protocoles réels comportent d'autres étapes, dont la vérification des identités, les paramètres de négociation et la protection contre certaines manipulations.

Le chiffrement hybride ne signifie pas que toutes les méthodes sont automatiquement sécurisées dès qu'elles sont combinées. Il faut utiliser un protocole reconnu et éviter les constructions improvisées.

### 7.3. Exemple : un service Web

Lorsqu'un navigateur communique avec un serveur via HTTPS, les deux parties établissent des paramètres cryptographiques pour protéger leur session.

La négociation inclut des mécanismes qui contribuent à établir les clés et à vérifier l'identité du serveur, selon le protocole et la configuration. Les données échangées sont ensuite protégées par des mécanismes adaptés à la session.

Le navigateur n'a pas besoin de chiffrer chaque octet du contenu Web avec une clé publique de manière indépendante. Les mécanismes de session permettent d'utiliser efficacement le chiffrement symétrique.

Cette architecture illustre l'intérêt de combiner différentes familles de cryptographie.

## 8. Le hachage : une opération différente du chiffrement

### 8.1. Définition

Une fonction de hachage transforme des données de taille variable en une empreinte de taille déterminée.

Par exemple, SHA-256 produit une empreinte de 256 bits. La fonction peut traiter un petit message ou un fichier beaucoup plus grand.

Contrairement au chiffrement, le hachage cryptographique est conçu pour ne pas permettre de retrouver directement les données d'origine à partir de l'empreinte.

Le hachage ne nécessite pas de clé secrète dans son usage de base, même s'il existe également des mécanismes cryptographiques apparentés qui utilisent une clé, tels que les codes d'authentification de message.

### 8.2. Pourquoi le hachage ne remplace-t-il pas le chiffrement ?

Supposons qu'une application doive enregistrer l'adresse d'un client pour pouvoir l'afficher lors d'une prochaine connexion.

Le hachage de cette adresse ne permet pas de retrouver directement le texte original. Il ne répond donc pas au besoin d'affichage.

Le chiffrement, lui, permet à l'application autorisée de déchiffrer la donnée lorsqu'elle doit l'utiliser.

À l'inverse, un système de connexion ne devrait généralement pas conserver le mot de passe d'un utilisateur dans une forme directement récupérable. Il utilise plutôt une méthode de stockage de mots de passe fondée sur un hachage spécialisé.

Le bon choix dépend de l'objectif : doit-on retrouver le contenu, vérifier une correspondance, ou vérifier l'intégrité d'un message ?

### 8.3. Les propriétés attendues d'une fonction de hachage cryptographique

Une fonction de hachage cryptographique doit notamment rendre difficile la recherche d'un contenu correspondant à une empreinte donnée et la recherche de deux contenus différents possédant la même empreinte, selon les propriétés formelles appropriées.

Aucun hachage de longueur finie ne peut fournir une empreinte différente pour chaque contenu possible, car il existe une infinité de contenus de longueur variable et un nombre fini d'empreintes possibles. La sécurité repose plutôt sur l'impossibilité pratique de trouver certaines collisions ou préimages.

Pour un débutant, il est surtout important de comprendre que la comparaison d'empreintes peut aider à détecter des changements, mais qu'elle n'offre pas automatiquement une authentification.

### 8.4. Exemple : vérifier un fichier

Sous Windows PowerShell :

```powershell
Get-FileHash .\document.txt -Algorithm SHA256
```

Sous Linux :

```bash
sha256sum document.txt
```

Ces commandes calculent l'empreinte du fichier.

Si tu compares le résultat avec une empreinte de référence fiable, tu peux vérifier que le contenu correspond à ce qui était attendu.

Si la référence vient d'un endroit lui-même compromis, un attaquant peut parfois la remplacer. Il faut donc obtenir la valeur de référence par un canal de confiance ou utiliser un mécanisme d'authentification adapté.

Le cours suivant, consacré au hachage et aux signatures, approfondira les empreintes, les collisions et les signatures numériques.

## 9. Pourquoi le hachage rapide ne convient-il pas au stockage des mots de passe ?

### 9.1. Le problème

Une application ne devrait généralement pas conserver les mots de passe des utilisateurs en clair. Si la base de données est volée, l'attaquant pourrait les utiliser directement, notamment sur d'autres services lorsque les utilisateurs réutilisent leurs mots de passe.

Le stockage des mots de passe repose généralement sur des fonctions spécialisées conçues pour rendre les essais répétés plus coûteux.

### 9.2. Les fonctions adaptées

Des fonctions telles qu'Argon2id, scrypt, bcrypt ou PBKDF2 sont utilisées selon les bibliothèques, les exigences et les contextes.

Ces méthodes prennent en compte des paramètres qui ralentissent ou rendent plus coûteuse la vérification d'un grand nombre de mots de passe candidats.

Il faut utiliser le mécanisme prévu par le framework ou une bibliothèque reconnue, et respecter les recommandations actualisées relatives à sa configuration.

L'OWASP recommande de ne pas stocker les mots de passe en clair et décrit les méthodes de stockage appropriées dans sa [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

### 9.3. Le sel

Un *salt*, ou sel cryptographique, est une valeur associée au calcul de stockage d'un mot de passe selon la méthode utilisée.

Un sel unique pour chaque mot de passe permet notamment d'empêcher que deux comptes ayant le même mot de passe produisent systématiquement la même valeur stockée selon un schéma déterminé.

Le sel n'est pas nécessairement secret. Son rôle est différent de celui de la clé utilisée pour chiffrer des données.

Avec les mécanismes modernes, la génération et le stockage du sel sont généralement gérés par la bibliothèque. Il vaut mieux s'appuyer sur ces fonctions plutôt que créer sa propre méthode.

### 9.4. Pourquoi SHA-256 seul ne suffit-il pas pour les mots de passe ?

SHA-256 est une fonction de hachage cryptographique utile pour de nombreuses tâches, mais elle est conçue pour être rapide.

Cette rapidité peut faciliter les essais massifs lorsqu'un attaquant possède des empreintes de mots de passe et tente de retrouver les valeurs d'origine.

Pour stocker les mots de passe, on préfère des fonctions spécialisées avec des paramètres adaptés, qui rendent les essais bien plus coûteux.

Il ne faut pas confondre le fait qu'une fonction soit cryptographiquement utile avec son adéquation à chaque problème.

### 9.5. Une application n'a-t-elle jamais besoin de retrouver le mot de passe ?

Dans une conception habituelle, l'application vérifie si le mot de passe présenté correspond au mot de passe enregistré, sans avoir besoin de retrouver le mot de passe en clair à partir de la valeur stockée.

Si un système doit transmettre le secret d'un utilisateur à un autre service, il faut réévaluer son architecture et privilégier si possible un mécanisme d'authentification déléguée ou des jetons plutôt que conserver les mots de passe en clair.

La règle générale est de ne pas stocker un secret récupérable quand le besoin métier ne l'exige pas.

## 10. Les signatures numériques

### 10.1. Le problème d'un document transmis

Alice reçoit un fichier qui semble provenir de son responsable. Le document contient une instruction qui lui demande de modifier une configuration importante.

Deux questions se posent :

- le fichier a-t-il été modifié depuis qu'il a été signé ?
- la signature correspond-elle à une clé associée à la personne ou à l'organisation attendue ?

Le chiffrement seul ne répond pas automatiquement à ces deux questions.

### 10.2. Principe d'une signature numérique

**Schéma pédagogique — Une signature vérifie l'intégrité et l'origine liée à une clé ; elle ne chiffre pas le document.**

~~~text
Emetteur:
Document --> Hachage --> Empreinte --> Signature avec cle privee
    |                                         |
    +---------------- document + signature ---+
                         |
                         v
Destinataire: document --> Hachage --> Empreinte recalculee
                         signature --> Verification cle publique
                                         |
                         +---------------+---------------+
                         v                               v
                    Correspond                     Ne correspond pas
~~~


Une signature numérique utilise un mécanisme cryptographique à clé publique.

Dans un scénario classique, le signataire utilise sa clé privée pour produire une signature associée aux données. Le destinataire vérifie cette signature à l'aide de la clé publique correspondante.

La vérification peut contribuer à détecter une modification du contenu signé et à établir que la signature a été produite avec la clé privée associée.

Le NIST décrit l'utilisation des signatures numériques pour détecter des modifications non autorisées et contribuer à authentifier le signataire. [Standard NIST FIPS 186-5 sur les signatures numériques](https://csrc.nist.gov/pubs/fips/186-5/final).

### 10.3. Signature et chiffrement ne sont pas la même chose

Un document signé n'est pas automatiquement confidentiel.

Si Alice signe un fichier et le transmet sans chiffrement, les personnes capables de lire le fichier peuvent toujours consulter son contenu. La signature peut contribuer à vérifier son intégrité et son origine cryptographique, mais elle ne cache pas le document.

Inversement, un fichier chiffré peut être confidentiel sans porter de signature permettant au destinataire d'identifier son origine.

Une application peut donc avoir besoin de chiffrer un document et de vérifier une signature, selon les exigences. La solution doit être conçue selon un protocole reconnu.

### 10.4. Pourquoi la clé publique doit-elle être vérifiée ?

Supposons qu'Alice reçoive une signature et qu'elle utilise une clé publique fournie par un attaquant. La vérification peut démontrer que la signature correspond à la clé fournie, mais elle ne prouve pas à elle seule que cette clé appartient à la personne attendue.

Il faut établir un lien de confiance entre la clé et l'identité : certificat vérifié, empreinte obtenue par un canal indépendant, infrastructure de confiance ou autre procédure adaptée.

La cryptographie fournit des preuves mathématiques concernant les clés et les données. La confiance dans l'identité dépend également de la façon dont les clés sont distribuées et vérifiées.

## 11. Les certificats numériques et les autorités de certification

### 11.1. À quoi sert un certificat ?

Un certificat numérique permet d'associer une clé publique à une identité ou à un nom selon un format et un processus de confiance.

Dans le Web, un certificat TLS aide le navigateur à vérifier que la clé publique présentée est associée au nom du serveur visité, en s'appuyant sur les autorités de certification et les règles de validation du navigateur.

Un certificat ne remplace pas la clé privée. Il contient généralement des informations publiques et une signature d'autorité ou un mécanisme de validation prévu par l'infrastructure concernée.

### 11.2. Le rôle d'une autorité de certification

**Schéma pédagogique — La confiance dépend de la chaîne de certificats et de l'identité vérifiée.**

~~~text
[Autorite racine approuvee]
           |
           v
[Autorite intermediaire]
           |
           v
[Certificat du serveur]
   |       |        |
   |       |        +-- nom / SAN attendu
   |       +----------- dates de validite
   +------------------- signature et usages
           |
           v
[Client verifie la chaine et l'identite]
~~~


Une autorité de certification, ou CA (*Certificate Authority*), émet ou signe des certificats selon un processus défini.

Le navigateur ou le système client doit vérifier que la chaîne de certificats aboutit à une autorité de confiance, que le nom attendu correspond et que les autres règles de validation pertinentes sont respectées.

Un certificat expiré, révoqué ou associé à un nom incorrect peut déclencher un avertissement. Il ne faut pas ignorer automatiquement ces avertissements.

### 11.3. HTTPS et TLS

HTTPS utilise TLS pour protéger les communications entre un client et un serveur. La négociation TLS permet d'établir des paramètres cryptographiques pour la session et de vérifier l'identité du serveur selon le certificat et la configuration.

Une session TLS correctement configurée protège la confidentialité et l'intégrité des données en transit, selon les propriétés du protocole et de son utilisation.

Cependant, HTTPS ne garantit pas que le site lui-même est honnête ou exempt de vulnérabilités. Un site frauduleux peut obtenir un certificat valide pour son propre domaine.

Il faut donc vérifier le nom du domaine et la légitimité du service, et pas uniquement la présence du cadenas dans le navigateur.

### 11.4. Erreurs fréquentes sur les certificats

Un certificat valide n'indique pas automatiquement que l'organisation derrière le site est digne de confiance dans tous les sens du terme.

De même, le certificat public peut être transmis librement, mais la clé privée associée doit rester protégée.

Si une clé privée de serveur est compromise, il peut être nécessaire de révoquer ou remplacer le certificat et d'évaluer les connexions ou données concernées selon la situation.

## 12. Gestion des clés : l'élément souvent oublié

### 12.1. La sécurité dépend aussi des clés

On peut choisir un algorithme robuste, mais affaiblir toute la solution en stockant la clé dans un fichier accessible à trop de personnes.

Si un attaquant obtient simultanément le fichier chiffré et la clé nécessaire, le chiffrement ne protège plus le contenu contre cet attaquant.

La gestion des clés inclut leur génération, leur stockage, leur distribution, leur utilisation, leur remplacement, leur sauvegarde éventuelle et leur destruction contrôlée.

Le NIST fournit des recommandations de gestion des clés cryptographiques dans la série SP 800-57. [Références NIST sur la gestion des clés](https://csrc.nist.gov/Projects/Key-Management/Key-Management-Guidelines).

### 12.2. Générer les clés

Les clés doivent être générées avec des mécanismes cryptographiquement sûrs. Elles ne devraient pas être dérivées de phrases simples ou improvisées en mélangeant quelques caractères.

Les générateurs aléatoires ordinaires destinés aux jeux, aux simulations ou aux tirages non sensibles ne conviennent pas nécessairement à la génération de clés.

Il faut utiliser les mécanismes sécurisés fournis par le système, la bibliothèque ou l'infrastructure cryptographique appropriée.

### 12.3. Stocker les clés séparément des données

**Schéma pédagogique — Séparer les clés des données limite l'impact d'un accès non autorisé à un seul composant.**

~~~text
[Application autorisee] ---- demande controlee ----> [Coffre de cles]
          |                                           |
          v                                           v
    [Donnees chiffrees] <------ operation ------ [Cle protegee]
          |
          +---- sauvegarde de donnees
          +---- journalisation sans secret

Planifier rotation, révocation, sauvegarde sécurisée et récupération.
~~~


Lorsque c'est possible, les clés de chiffrement doivent être protégées séparément des données qu'elles protègent.

Si la clé est conservée dans le même dossier que le fichier chiffré avec des permissions identiques, le vol du dossier peut fournir les deux éléments.

Dans un environnement professionnel, des mécanismes de gestion des clés, des coffres à secrets ou des composants matériels dédiés peuvent aider à contrôler les accès et les opérations.

La solution dépend du risque, du budget et des capacités de l'organisation.

### 12.4. Ne jamais publier de clés privées dans un dépôt de code

Un développeur peut être tenté d'inclure une clé directement dans son programme afin de simplifier les tests.

Si le dépôt est partagé, sauvegardé dans un service tiers ou rendu public, la clé peut être exposée à des personnes qui n'en ont pas besoin.

Les secrets ne doivent donc pas être intégrés au code source ou à l'historique des versions. Il faut utiliser une méthode de gestion adaptée à l'environnement et contrôler les permissions.

Si une clé ou un jeton est publié accidentellement, il faut considérer qu'il peut être compromis, le révoquer ou le remplacer selon son rôle, puis vérifier les traces d'utilisation.

### 12.5. Rotation des clés

La rotation consiste à remplacer une clé selon une politique ou après un événement qui justifie son remplacement.

Elle peut être requise en cas de compromission suspectée, de changement d'équipe ou selon le cycle de vie prévu par l'organisation.

La rotation doit tenir compte des données déjà chiffrées. Remplacer simplement la clé sans prévoir la récupération des données peut empêcher leur déchiffrement.

Il faut donc savoir quelles clés sont utilisées, quelles données en dépendent et comment procéder de manière sûre.

### 12.6. Perte et récupération des clés

La perte d'une clé peut rendre les données chiffrées irrécupérables. C'est pourquoi les organisations doivent définir leurs procédures de sauvegarde ou de récupération lorsqu'elles sont nécessaires et compatibles avec leur modèle de sécurité.

Une procédure de récupération doit elle-même être protégée. Une personne non autorisée ne doit pas pouvoir récupérer facilement les clés uniquement parce qu'une procédure de secours existe.

La sécurité résulte d'un équilibre entre protection contre les accès non autorisés et capacité de récupération légitime.

## 13. L'aléatoire cryptographique

### 13.1. Pourquoi l'aléatoire est-il important ?

La cryptographie utilise des valeurs qui doivent parfois être imprévisibles : clés, nonces, jetons de session et autres paramètres.

Si un attaquant peut prédire ces valeurs, il peut affaiblir le mécanisme qui les utilise.

Les valeurs de sécurité ne doivent donc pas être générées à l'aide de mécanismes destinés uniquement à produire des séquences variées pour un usage non sensible.

### 13.2. Générateur pseudo-aléatoire ordinaire et générateur cryptographique

Un générateur pseudo-aléatoire produit des valeurs à partir d'un état interne ou d'une graine. Pour les usages ordinaires, il peut convenir à des simulations ou à des opérations sans exigence de secret.

Un générateur cryptographiquement sûr est conçu pour rendre les sorties difficiles à prédire, même dans des conditions d'attaque définies.

Il faut utiliser les fonctions cryptographiques sûres de la plateforme plutôt que de créer soi-même un générateur à partir de l'heure du système, d'un nom ou d'un nombre simple.

### 13.3. Exemple de mauvaise pratique

Un programme crée une clé en concaténant le nom d'une entreprise et l'année courante.

Cette valeur est facile à deviner pour une personne qui connaît le contexte. Même si le programme la transforme ensuite, le manque d'imprévisibilité initiale peut compromettre la sécurité.

La bonne pratique consiste à générer une clé à l'aide d'une bibliothèque cryptographique et à la conserver de manière appropriée.

## 14. Choisir les bons outils cryptographiques

### 14.1. Ne pas fabriquer sa propre cryptographie

Il est tentant d'inventer un système simple lorsque l'on commence à étudier la sécurité. Pourtant, de nombreux détails peuvent rendre une construction vulnérable : paramètres mal choisis, mauvaise gestion des clés, erreurs d'authentification ou problèmes de génération aléatoire.

Il faut préférer des bibliothèques reconnues, maintenues et documentées, avec les algorithmes et modes adaptés au besoin.

La documentation de l'OWASP sur le stockage cryptographique recommande d'éviter les algorithmes personnalisés et de considérer le modèle de menace avant de choisir les protections. [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html).

### 14.2. Vérifier la maintenance d'une bibliothèque

Une bibliothèque doit être entretenue, recevoir des corrections et être compatible avec l'environnement utilisé.

Il faut examiner sa provenance, sa documentation, son historique de maintenance et les recommandations de sécurité qui la concernent.

Une bibliothèque très ancienne ou abandonnée peut présenter des risques, même si elle porte un nom connu.

### 14.3. Ne pas choisir uniquement la taille de la clé

La taille de clé est un élément important, mais pas le seul.

Il faut aussi examiner l'algorithme, le mode, la qualité de l'aléatoire, le protocole, les règles de gestion de clés et le contexte d'utilisation.

Un algorithme robuste mal configuré peut offrir une protection insuffisante. Inversement, une solution bien conçue utilise des mécanismes appropriés et limite les erreurs courantes.

### 14.4. Attention aux algorithmes anciens

Certains algorithmes historiques sont utiles pour comprendre l'évolution de la cryptographie, mais ne sont pas adaptés à de nouvelles applications de sécurité.

Le chiffrement de César, par exemple, repose sur un décalage simple des lettres. Il peut être cassé facilement et ne doit pas être utilisé pour protéger des informations réelles.

Les protocoles et algorithmes doivent être sélectionnés selon des recommandations actuelles, plutôt que sur la seule base de leur simplicité.

## 15. Cryptographie et évolution des menaces

### 15.1. Les capacités des attaquants évoluent

Les ressources informatiques et les techniques d'analyse évoluent. Un mécanisme qui semblait acceptable dans un ancien contexte peut devenir insuffisant lorsque les capacités de calcul, les connaissances ou les techniques d'attaque changent.

Il est donc important de suivre les recommandations des organismes spécialisés et de planifier le remplacement des mécanismes obsolètes.

### 15.2. La cryptographie post-quantique

La cryptographie post-quantique étudie des mécanismes conçus pour résister à certaines attaques rendues possibles par des ordinateurs quantiques suffisamment puissants.

Certains mécanismes asymétriques classiques pourraient être vulnérables à de futurs ordinateurs quantiques cryptographiquement pertinents. Cela ne signifie pas que toutes les formes de cryptographie sont affectées de la même manière.

Le NIST a publié le standard FIPS 203 pour ML-KEM, un mécanisme d'encapsulation de clé conçu pour établir un secret partagé. Ce mécanisme n'est pas un chiffrement de fichier remplaçant directement AES : il contribue à l'établissement d'un secret que des algorithmes symétriques peuvent ensuite utiliser. [NIST FIPS 203 — ML-KEM](https://csrc.nist.gov/pubs/fips/203/final).

### 15.3. Pourquoi en parler à un niveau débutant ?

Il est utile de savoir que la cryptographie évolue et que les systèmes doivent pouvoir être maintenus.

Tu n'as pas besoin de maîtriser les mathématiques de ML-KEM pour ce cours. L'idée importante est qu'une solution cryptographique doit être conçue pour évoluer et suivre les recommandations techniques appropriées.

Une organisation qui conserve des données confidentielles pendant de nombreuses années doit également prendre en compte la durée de protection nécessaire, les possibilités de migration et la manière de remplacer les mécanismes utilisés.

## 16. TP guidé : comprendre le chiffrement avec une bibliothèque

Cette activité utilise Python et la bibliothèque `cryptography`. Elle sert à comprendre le principe du chiffrement authentifié. Elle ne constitue pas un système complet de gestion documentaire.

### 16.1. Préparer l'environnement

Utilise un environnement Python local que tu contrôles. Installe la bibliothèque dans cet environnement :

```bash
python -m pip install cryptography
```

Dans un environnement de formation, il est préférable d'utiliser un environnement virtuel et de vérifier les dépendances installées. Ne lance pas de code issu d'une source inconnue sur un poste professionnel sans validation.

### 16.2. Exemple d'un chiffrement local

Le programme suivant génère une clé en mémoire, chiffre un message et le déchiffre ensuite avec cette même clé.

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Génération d'une clé AES de 256 bits à l'aide de la bibliothèque.
key = AESGCM.generate_key(bit_length=256)
cipher = AESGCM(key)

# Le nonce doit être unique avec cette clé.
nonce = os.urandom(12)

message = b"Document confidentiel de demonstration"
associated_data = b"cours-cybersecurite-v1"

# Chiffrement authentifié.
ciphertext = cipher.encrypt(nonce, message, associated_data)

print("Message original :", message)
print("Donnees chiffrees :", ciphertext.hex())

# Déchiffrement et vérification d'authenticité.
recovered = cipher.decrypt(nonce, ciphertext, associated_data)

print("Message retrouve :", recovered)
assert recovered == message
print("Verification : OK")
```

Dans cette démonstration, AES-GCM assure le chiffrement et une vérification d'authenticité des données. La clé est produite par une fonction de la bibliothèque, et le nonce est généré avec le module aléatoire du système.

La même clé et le nonce correspondant sont utilisés pour la démonstration de déchiffrement. Dans une application réelle, le format de stockage devrait conserver les paramètres nécessaires selon une conception rigoureuse.

### 16.3. Comprendre les variables

`key` contient la clé cryptographique. Elle doit rester secrète pour protéger le message.

`cipher` représente le mécanisme AES-GCM configuré avec cette clé.

`nonce` est une valeur de paramétrage requise par ce mode. Dans cet exemple, elle est générée aléatoirement. Il faut respecter les règles de non-réutilisation avec la même clé.

`message` contient le contenu original.

`associated_data` représente des données supplémentaires associées à l'opération. Elles ne sont pas chiffrées par ce paramètre, mais elles sont liées à la vérification d'authenticité du résultat.

`ciphertext` contient les données chiffrées ainsi que les éléments d'authentification produits par la bibliothèque.

`recovered` contient le message retrouvé lorsque la vérification et le déchiffrement réussissent.

### 16.4. Pourquoi ne pas réutiliser cette démonstration telle quelle pour des fichiers sensibles ?

La clé est conservée uniquement dans la mémoire du programme. À la fin de l'exécution, elle n'est pas stockée pour une récupération ultérieure. Le message serait donc impossible à déchiffrer lors d'une nouvelle exécution sans disposer de la même clé.

Ce comportement est volontaire dans la démonstration : il montre que la clé est indispensable.

Pour une véritable application, il faut concevoir le format de stockage, protéger la clé, gérer son cycle de vie et prévoir la récupération autorisée. Il faut aussi documenter comment la clé a été créée, où elle est stockée, qui peut l'utiliser et comment procéder à sa révocation ou à son remplacement.

N'enregistre jamais une clé de production directement dans le code source pour contourner cette difficulté.

### 16.5. Observer l'effet d'une modification

La bibliothèque vérifie l'authenticité du contenu. Si tu modifies le texte chiffré ou fournis un paramètre incorrect, le déchiffrement doit échouer plutôt que retourner silencieusement un message accepté.

Tu peux effectuer une expérimentation contrôlée en modifiant un octet de `ciphertext` dans un nouveau bloc de test. Il faut s'attendre à une exception liée à l'échec de vérification. N'utilise pas un mécanisme qui ignore cette erreur ou accepte les données non vérifiées.

Cette observation illustre une distinction importante : un chiffrement authentifié peut détecter certaines altérations, tandis qu'un mécanisme de chiffrement qui ne fournit que la confidentialité ne garantit pas à lui seul l'intégrité.

### 16.6. Nettoyage

Le programme ne crée pas de fichier sur le disque. Il n'y a donc pas de fichier de test à supprimer.

Ne copie pas la clé imprimée dans un message, dans un dépôt ou dans un espace partagé. Dans cet exemple, le programme ne l'affiche pas. Garde cette habitude dans les applications réelles.

## 17. TP guidé : observer la différence entre hachage et chiffrement

Cette activité utilise un message de test et ne nécessite aucun secret réel.

### 17.1. Calculer une empreinte en Python

```python
import hashlib

message = b"Premier message de test"
empreinte = hashlib.sha256(message).hexdigest()

print("Empreinte SHA-256 :", empreinte)
```

Modifie ensuite le texte :

```python
import hashlib

message = b"Message de test modifie"
empreinte = hashlib.sha256(message).hexdigest()

print("Nouvelle empreinte :", empreinte)
```

Les deux empreintes devraient être différentes.

### 17.2. Interpréter le résultat

Le hachage produit une empreinte associée au contenu. Il ne permet pas de retrouver le message en clair en effectuant simplement une opération inverse.

Le chiffrement, au contraire, permet à une personne disposant des éléments requis de déchiffrer les données.

Il faut donc choisir l'opération en fonction du besoin. Utiliser une empreinte pour stocker une adresse que l'application doit réafficher ne répond pas à ce besoin. Utiliser du chiffrement réversible pour enregistrer un mot de passe de connexion est généralement inadapté.

### 17.3. Limites de l'expérience

Le code montre comment une bibliothèque standard calcule une empreinte. Il ne met pas en place un stockage de mots de passe sécurisé et ne prouve pas que la référence d'une empreinte vient d'une source de confiance.

Le hachage SHA-256 est utile dans de nombreux contextes, mais les mots de passe nécessitent des mécanismes spécialisés et des paramètres adaptés.

## 18. Étude de cas : protéger les données de NovaLearn

### 18.1. Situation

NovaLearn est une plateforme de formation qui conserve les informations de ses apprenants, leurs résultats et les documents de cours.

L'entreprise souhaite transmettre certains documents à un partenaire, protéger la base de données et garantir que les mises à jour du logiciel n'ont pas été modifiées.

La direction te demande de proposer une stratégie de cryptographie adaptée à ces besoins.

### 18.2. Protéger les données en transit

Les communications entre les navigateurs et le site devraient utiliser HTTPS configuré selon des recommandations actuelles.

Il faut utiliser un certificat valide pour le nom attendu, protéger la clé privée du serveur et corriger les avertissements de configuration.

HTTPS protège les échanges au niveau du transport selon TLS, mais ne garantit pas que l'application est exempte de vulnérabilités. Les contrôles d'accès et les tests applicatifs restent nécessaires.

### 18.3. Protéger les données au repos

Les informations sensibles conservées sur les ordinateurs et les supports de stockage peuvent bénéficier d'un chiffrement adapté.

L'entreprise doit déterminer quelles données sont sensibles, où elles sont stockées et qui doit y accéder.

Le chiffrement du disque peut contribuer à protéger les fichiers lorsque le matériel est perdu ou volé. Il ne remplace pas les permissions et ne protège pas nécessairement les données contre une personne qui utilise déjà une session autorisée sur un ordinateur déverrouillé.

### 18.4. Stocker les mots de passe

La plateforme ne devrait pas conserver les mots de passe des apprenants en clair.

Elle doit employer les mécanismes de stockage de mots de passe appropriés fournis par une bibliothèque ou un framework reconnu.

Le mécanisme doit être configuré selon les recommandations actuelles. Un simple hachage rapide ne suffit pas.

### 18.5. Vérifier les fichiers du logiciel

Les fichiers de mise à jour peuvent être accompagnés de signatures ou d'empreintes de référence.

Une vérification d'empreinte peut confirmer que le fichier correspond à une valeur de référence fiable. Une signature numérique peut contribuer à vérifier l'origine cryptographique du fichier et à détecter certaines modifications, sous réserve de la vérification correcte de la clé publique et de sa confiance.

La vérification doit être intégrée à un processus de déploiement fiable. Un simple fichier d'empreinte téléchargé depuis la même source compromise que le binaire n'offre pas nécessairement une garantie suffisante.

### 18.6. Protéger les clés

Les clés ne devraient pas être incluses dans le dépôt de code de l'application. Leur accès doit être limité et leur gestion documentée.

Si une clé est compromise, NovaLearn doit savoir comment la révoquer ou la remplacer, quelles données ou communications sont concernées et quelles procédures permettent de revenir à un état sûr.

### 18.7. Résultat attendu

La stratégie de NovaLearn associe plusieurs contrôles :

- chiffrement adapté des communications et des données stockées ;
- stockage sécurisé des mots de passe ;
- gestion des certificats et des clés ;
- vérification fiable des logiciels ;
- contrôle d'accès et supervision ;
- tests périodiques et procédures de récupération.

Cette approche évite de confier toute la sécurité à un seul algorithme.

## 19. Les erreurs fréquentes à éviter

### Erreur 1 — Confondre encodage et chiffrement

Base64 est un encodage, pas un algorithme de chiffrement. Si un secret est simplement encodé, une personne peut généralement le récupérer sans clé.

### Erreur 2 — Utiliser le même secret partout

Réutiliser une clé ou un mot de passe dans plusieurs systèmes peut augmenter l'impact d'une compromission. Les clés doivent avoir un rôle clair et être gérées selon les besoins.

### Erreur 3 — Inventer un algorithme personnel

Une transformation conçue rapidement n'a pas nécessairement les propriétés de sécurité attendues. Les mécanismes reconnus et les bibliothèques maintenues sont préférables.

### Erreur 4 — Croire que le chiffrement garantit toujours l'intégrité

Le chiffrement seul ne garantit pas nécessairement l'authenticité des données. Il faut sélectionner un mécanisme adapté, par exemple un chiffrement authentifié lorsque cela convient.

### Erreur 5 — Croire que la clé publique doit rester secrète

La clé publique est conçue pour pouvoir être communiquée. La clé privée correspondante doit rester protégée. En revanche, il faut vérifier que la clé publique appartient bien à l'entité attendue.

### Erreur 6 — Stocker les mots de passe avec SHA-256 seul

SHA-256 est rapide et ne constitue pas, à lui seul, le mécanisme recommandé pour stocker des mots de passe. Les applications doivent utiliser une fonction spécialisée et configurée correctement.

### Erreur 7 — Croire qu'un certificat valide prouve que le site est honnête

Un certificat TLS contribue à vérifier l'identité du domaine selon le mécanisme de confiance utilisé. Il ne garantit pas que tous les contenus du site sont fiables ou que l'organisation ne commettra aucune fraude.

### Erreur 8 — Oublier la récupération des clés

Une clé perdue peut rendre des données irrécupérables. Une stratégie de chiffrement doit inclure les besoins de récupération, les permissions et les procédures de secours.

### Erreur 9 — Publier une clé dans le code source

Une clé intégrée au code peut être copiée, conservée dans l'historique ou exposée à des collaborateurs qui ne devraient pas y avoir accès. Il faut utiliser une gestion de secrets appropriée.

### Erreur 10 — Confondre signature numérique et chiffrement

Une signature numérique n'a pas pour objectif principal de cacher le contenu du document. Elle sert notamment à vérifier la signature et à détecter des modifications. Si la confidentialité est également nécessaire, un mécanisme supplémentaire peut être requis.

## 20. Exercices avec corrections

Essaie de répondre avant de consulter les corrections.

### Exercice 1 — Reconnaître le bon mécanisme

Une entreprise souhaite protéger le contenu d'un fichier afin que seuls les utilisateurs disposant de la clé appropriée puissent le lire. Quel mécanisme répond le plus directement à ce besoin ?

A. Encodage Base64.

B. Chiffrement adapté avec une gestion sûre de la clé.

C. Renommage du fichier.

D. Compression du fichier.

**Correction : B.**

Le chiffrement permet de rendre le contenu illisible aux personnes qui ne possèdent pas les éléments nécessaires. La clé et sa gestion sont déterminantes. L'encodage, le renommage et la compression ne procurent pas, à eux seuls, la confidentialité cryptographique recherchée.

### Exercice 2 — Distinguer clé publique et clé privée

Dans un système asymétrique, quelle clé doit généralement rester secrète ?

A. La clé publique.

B. La clé privée.

C. Les deux clés doivent nécessairement être publiées.

D. Aucune clé n'est nécessaire.

**Correction : B.**

La clé privée doit être protégée. La clé publique peut être distribuée, mais le destinataire doit vérifier qu'elle est associée à l'identité attendue.

### Exercice 3 — Comprendre les mots de passe

Une application enregistre tous les mots de passe dans un fichier en clair. Quel est le problème principal ?

A. Les mots de passe sont trop faciles à afficher dans l'interface.

B. Le vol du fichier pourrait fournir directement les mots de passe utilisables.

C. Le fichier sera automatiquement chiffré par le système.

D. Le stockage en clair augmente nécessairement la disponibilité.

**Correction : B.**

Le stockage en clair expose directement les mots de passe à toute personne capable de lire le fichier. Une application doit utiliser un mécanisme approprié de stockage des mots de passe.

### Exercice 4 — Hachage ou chiffrement ?

Une application doit vérifier qu'un fichier téléchargé correspond à une version de référence. Quelle méthode peut contribuer à vérifier le contenu ?

A. Comparer une empreinte cryptographique avec une empreinte de référence fiable.

B. Transformer le nom du fichier en majuscules.

C. Utiliser un mot de passe très court.

D. Ajouter une extension `.secure`.

**Correction : A.**

La comparaison des empreintes peut détecter une différence de contenu. Il faut toutefois disposer d'une référence fiable, et un hachage seul ne permet pas toujours de vérifier qui a produit le fichier.

### Exercice 5 — Le site HTTPS

Tu visites un site possédant un certificat TLS valide. Peux-tu conclure que tous les contenus publiés par ce site sont honnêtes ?

**Correction**

Non. Le certificat aide à vérifier l'identité du domaine selon les règles de validation et permet la mise en place d'une communication sécurisée. Il ne certifie pas que toutes les informations du site sont vraies, ni que l'organisation est digne de confiance dans tous les domaines.

### Exercice 6 — Réutilisation d'une clé

Une entreprise utilise la même clé pour chiffrer toutes les données de tous ses systèmes, sans documentation ni procédure de rotation.

Quel est le risque ?

**Correction**

Une compromission de cette clé peut affecter plusieurs systèmes. L'absence de documentation complique l'identification des données concernées et leur migration. Il faut définir des rôles de clés, limiter les accès et préparer leur remplacement selon une politique adaptée.

### Exercice 7 — Le fichier est chiffré mais modifiable

Un développeur utilise un mécanisme qui chiffre les données sans leur fournir de protection d'authenticité. Un attaquant modifie certains bits du texte chiffré.

Pourquoi cela peut-il poser problème ?

**Correction**

Le mécanisme utilisé ne garantit pas nécessairement la détection d'une altération. Selon l'algorithme et le mode, le déchiffrement peut produire des données modifiées sans preuve suffisante que le contenu est authentique. Il faut privilégier un mécanisme adapté qui fournit une authentification du contenu lorsque cela est nécessaire.

### Exercice 8 — Signature numérique

Un fichier possède une signature numérique valide avec une clé publique. Quelles vérifications restent importantes ?

**Correction**

Il faut vérifier que la clé publique est bien associée à la personne ou à l'organisation attendue, que le contenu vérifié est celui qui sera utilisé et que le mécanisme de confiance est fiable. Une signature valide ne garantit pas que le document est forcément correct ou qu'il est confidentiel.

### Exercice 9 — Perte de clé

Une entreprise chiffre ses archives avec une clé qui n'existe plus après le départ de l'administrateur.

Quelle leçon doit-elle retenir ?

**Correction**

La gestion des clés doit inclure leur cycle de vie et les conditions de récupération nécessaires. La protection ne doit pas dépendre d'une seule personne ou d'un fichier non documenté. Les procédures de secours doivent être sécurisées et testées.

### Exercice 10 — Choisir un stockage de mots de passe

Un développeur affirme qu'il est suffisant de calculer SHA-256 une fois sur chaque mot de passe pour le protéger.

Pourquoi cette affirmation est-elle incorrecte ?

**Correction**

SHA-256 est une fonction conçue pour être rapide. Un attaquant qui obtient les empreintes peut essayer de nombreuses valeurs candidates. Le stockage de mots de passe doit utiliser un mécanisme spécialisé, tel qu'Argon2id ou une alternative adaptée au contexte, configuré selon les recommandations actuelles.

## 21. Défi final — Concevoir une stratégie cryptographique

### 21.1. Situation

Tu travailles pour une entreprise appelée **NovaLearn**. Elle gère une plateforme de formation, une base de données d'apprenants et un système qui permet aux enseignants de publier les résultats.

Elle doit répondre aux besoins suivants :

1. Les données personnelles doivent être protégées contre les accès non autorisés.
2. Les communications entre les navigateurs et le serveur doivent être protégées.
3. Les mots de passe doivent être stockés de manière adaptée.
4. Les fichiers de mise à jour doivent pouvoir être vérifiés.
5. Les clés doivent rester protégées et pouvoir être remplacées si nécessaire.
6. Les données doivent rester récupérables en cas de panne ou d'erreur.

La direction te demande de concevoir une première architecture de protection cryptographique.

### 21.2. Travail demandé

Décris une solution pour chacun des six besoins. Pour chaque choix, explique :

- l'objectif de sécurité ;
- le mécanisme cryptographique envisagé ;
- la manière de protéger les clés ou les références de confiance ;
- les limites du mécanisme ;
- le test permettant de vérifier le résultat.

Ne sélectionne pas des produits uniquement sur la base de leur nom. Explique d'abord le besoin.

### 21.3. Correction détaillée

**Besoin 1 : protéger les données personnelles.**

L'organisation doit identifier les données sensibles, contrôler leurs permissions et décider lesquelles doivent être chiffrées au repos.

Le chiffrement doit utiliser un mécanisme reconnu et une gestion de clés adaptée. Il faut séparer autant que possible les clés des données et limiter les personnes capables de les utiliser.

Le chiffrement ne remplace pas le contrôle d'accès applicatif. Un utilisateur authentifié ne doit pas pouvoir consulter tous les dossiers uniquement parce que la base est chiffrée au repos.

Le contrôle peut être vérifié avec des tests de rôles et des procédures de récupération dans un environnement contrôlé.

**Besoin 2 : protéger les communications Web.**

La plateforme doit utiliser HTTPS configuré correctement avec TLS. Le certificat doit être valide pour le domaine attendu, et la clé privée du serveur doit être protégée.

Il faut vérifier la configuration et s'assurer que les utilisateurs n'ignorent pas les avertissements de sécurité.

La protection des communications ne rend pas automatiquement l'application sûre contre les contrôles d'accès insuffisants ou les failles de logique métier.

**Besoin 3 : protéger les mots de passe.**

Les mots de passe ne doivent pas être stockés en clair ou avec un simple encodage. La plateforme doit utiliser un mécanisme de stockage de mots de passe adapté, intégré à une bibliothèque ou à un framework reconnu.

Il faut vérifier que les paramètres sont appropriés et que le système ne révèle pas les secrets dans les journaux ou les messages d'erreur.

**Besoin 4 : vérifier les fichiers de mise à jour.**

Une méthode peut reposer sur des signatures numériques : le logiciel de déploiement vérifie la signature des fichiers à l'aide d'une clé publique de confiance.

La clé publique ou le certificat utilisé doit être distribué et vérifié de manière sûre. Si l'organisation utilise des empreintes, la référence doit provenir d'un canal fiable et protégé.

La vérification doit être réalisée automatiquement dans le processus de déploiement lorsque cela est possible, et le système doit refuser les fichiers qui ne satisfont pas les contrôles.

**Besoin 5 : gérer les clés.**

L'organisation doit documenter quelles clés sont utilisées, par quels systèmes, à quelles fins et par quels comptes. Il faut limiter les accès, prévoir leur rotation et définir les actions à mener en cas de compromission.

Les clés ne doivent pas être intégrées au dépôt de code ou partagées par courriel sans protection adaptée.

Les procédures de rotation doivent être testées pour éviter de rendre les données existantes irrécupérables.

**Besoin 6 : maintenir la capacité de récupération.**

Il faut combiner les sauvegardes et les procédures de récupération avec une gestion adéquate des clés. La sauvegarde d'un fichier chiffré ne suffit pas si la clé nécessaire au déchiffrement est perdue.

L'organisation doit définir les conditions de récupération, protéger les copies de secours et tester la restauration des données comme celle des clés nécessaires, dans un cadre sûr.

### 21.4. Grille d'autoévaluation

| Critère | Points |
|---|---:|
| Bonne distinction entre chiffrement, hachage et signature | 4 |
| Choix approprié des mécanismes | 4 |
| Gestion et protection des clés | 4 |
| Prise en compte des limites et du contrôle d'accès | 3 |
| Vérification et tests | 3 |
| Récupération et documentation | 2 |
| **Total** | **20** |

Une bonne réponse n'est pas une liste d'algorithmes. Elle montre que tu sais relier chaque mécanisme à son objectif, expliquer ses limites et prévoir comment vérifier son fonctionnement.

## 22. Synthèse du cours

La cryptographie fournit des mécanismes importants pour protéger les systèmes et les informations.

Le chiffrement protège la confidentialité du contenu lorsqu'il est correctement utilisé et que les clés restent protégées.

Le chiffrement symétrique emploie une clé secrète commune. AES est un algorithme de référence pour de nombreux usages, mais son mode, ses paramètres et sa mise en œuvre sont essentiels.

La cryptographie asymétrique utilise des paires de clés associées. La clé publique peut être diffusée, mais il faut vérifier son association à l'identité attendue. La clé privée doit rester protégée.

Les systèmes modernes combinent souvent des mécanismes asymétriques ou d'établissement de clés avec du chiffrement symétrique, notamment pour protéger efficacement les sessions de communication.

Le hachage calcule une empreinte et ne remplace pas le chiffrement. Les mots de passe doivent être conservés à l'aide de méthodes spécialisées adaptées à leur stockage, et non en clair ni par un simple encodage.

Les signatures numériques permettent de vérifier des propriétés d'intégrité et d'origine cryptographique. Elles ne rendent pas automatiquement un document confidentiel.

Les certificats et les autorités de confiance permettent d'associer des clés publiques à des identités selon des règles de validation. HTTPS/TLS utilise ces mécanismes pour contribuer à protéger les communications Web.

Enfin, la sécurité dépend de la gestion des clés : génération, stockage, accès, rotation et récupération. Un algorithme puissant ne compense pas une clé perdue ou divulguée.

Pour analyser un besoin cryptographique, pose-toi ces questions :

1. Dois-je cacher le contenu, vérifier un changement ou confirmer une signature ?
2. Le contenu doit-il pouvoir être retrouvé par une application autorisée ?
3. Quelle clé ou référence de confiance est nécessaire ?
4. Comment cette clé sera-t-elle générée et protégée ?
5. Comment pourra-t-on vérifier le résultat ?
6. Comment procéder si une clé est compromise ou perdue ?

Ces questions permettent de sélectionner des mécanismes cohérents au lieu de multiplier les outils sans comprendre leur rôle.

## 23. Glossaire

**Algorithme cryptographique :** méthode permettant de réaliser une opération cryptographique.

**AES :** algorithme de chiffrement symétrique normalisé pour protéger des données électroniques.

**Autorité de certification :** entité qui émet ou signe des certificats selon une politique de confiance.

**Certificat numérique :** document numérique qui associe une clé publique à une identité ou à un nom selon un mécanisme de validation.

**Chiffrement :** transformation cryptographique qui protège l'accès au contenu en le rendant illisible sans les éléments appropriés.

**Chiffrement asymétrique :** mécanisme utilisant une paire de clés associées, publique et privée.

**Chiffrement symétrique :** mécanisme utilisant une clé secrète commune pour chiffrer et déchiffrer selon l'algorithme.

**Clé cryptographique :** donnée utilisée par un mécanisme cryptographique.

**Clé privée :** partie secrète d'une paire de clés asymétriques.

**Clé publique :** partie d'une paire de clés asymétriques qui peut être diffusée, sous réserve de vérifier son association à l'identité attendue.

**Déchiffrement :** opération permettant de retrouver le contenu protégé avec la clé et les paramètres nécessaires.

**Encodage :** transformation de représentation qui ne fournit pas à elle seule de confidentialité cryptographique.

**Fonction de hachage :** fonction qui calcule une empreinte de longueur déterminée à partir d'un contenu.

**Hachage des mots de passe :** mécanisme de stockage fondé sur une fonction spécialisée pour rendre la recherche d'un mot de passe plus coûteuse.

**HTTPS :** version de HTTP utilisant TLS pour protéger les communications entre un client et un serveur.

**Intégrité :** propriété qui vise à détecter ou empêcher les modifications non autorisées et à préserver l'exactitude des données.

**Nonce :** valeur utilisée une fois dans un contexte cryptographique défini selon les exigences du mécanisme.

**Signature numérique :** signature cryptographique vérifiable à l'aide d'une clé publique associée.

**Texte chiffré :** résultat du chiffrement.

**Texte en clair :** contenu avant chiffrement ou après déchiffrement.

**TLS :** protocole cryptographique permettant de protéger des communications.

**Clé de session :** clé utilisée pour protéger les données d'une session de communication ou d'un échange donné.

**Chiffrement authentifié :** construction qui combine le chiffrement et une vérification d'authenticité des données selon les propriétés du mécanisme choisi.

**Sel cryptographique :** valeur associée au traitement d'un secret, notamment dans le stockage des mots de passe, pour limiter certains rapprochements et attaques précomputées.

## 24. Ressources pour approfondir

Les ressources suivantes permettent d'approfondir le sujet avec des références institutionnelles et techniques.

- [NIST — FIPS 197, Advanced Encryption Standard (AES)](https://csrc.nist.gov/pubs/fips/197/final) : description de l'algorithme AES et de ses tailles de clés.
- [NIST — Cryptographie à clé publique](https://csrc.nist.gov/glossary/term/public_key_cryptography) : définition de la cryptographie asymétrique.
- [NIST — FIPS 186-5, Digital Signature Standard](https://csrc.nist.gov/pubs/fips/186-5/final) : référence concernant les signatures numériques.
- [NIST — Key Management Guidelines](https://csrc.nist.gov/Projects/Key-Management/Key-Management-Guidelines) : recommandations relatives au cycle de vie et à la protection des clés.
- [OWASP — Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html) : conseils pratiques sur le choix des mécanismes, les modes de chiffrement et la gestion des clés.
- [OWASP — Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) : recommandations spécifiques au stockage sécurisé des mots de passe.
- [NIST — FIPS 203, ML-KEM](https://csrc.nist.gov/pubs/fips/203/final) : référence d'introduction à un mécanisme d'établissement de clés post-quantique.

**Fin du cours : Cryptographie.**
