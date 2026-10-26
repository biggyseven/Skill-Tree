# La Triade CIA

> **Mise en contexte**
>
> Imagine que tu travailles dans une entreprise qui possède un site de commerce en ligne. Les clients peuvent créer un compte, consulter les produits, passer des commandes et payer leurs achats. Le site contient des noms, des adresses, des historiques de commandes et des informations commerciales.
>
> Un pirate récupère les mots de passe des clients et publie leurs informations personnelles. Une autre personne modifie discrètement le prix d'un produit de 100 000 FCFA à 10 000 FCFA. Quelques jours plus tard, un incident informatique rend le site inaccessible pendant plusieurs heures.
>
> Ces trois situations représentent trois problèmes différents : la divulgation d'informations, leur modification non autorisée et l'indisponibilité d'un service.
>
> Pour comprendre ces risques et apprendre à les prévenir, les professionnels de la cybersécurité utilisent un modèle fondamental : la **triade CIA**, formée de la confidentialité, de l'intégrité et de la disponibilité. Ces trois propriétés constituent une base pour analyser les risques, choisir des protections et vérifier qu'un système reste digne de confiance.

## 1. Présentation générale de la triade CIA

### 1.1. Qu'est-ce que la cybersécurité ?

La cybersécurité regroupe les méthodes, les règles, les technologies et les pratiques qui permettent de protéger les systèmes informatiques, les réseaux, les applications et les informations contre les incidents et les actions non autorisées.

Elle concerne de nombreux environnements :

- les ordinateurs personnels et les smartphones ;
- les serveurs d'entreprise ;
- les réseaux informatiques et les équipements de télécommunication ;
- les applications Web et les API ;
- les bases de données ;
- les services Cloud ;
- les infrastructures industrielles ;
- les systèmes de paiement et les plateformes de commerce en ligne.

La cybersécurité ne consiste pas simplement à installer un antivirus ou un pare-feu. Elle vise à maintenir un niveau de confiance acceptable dans les informations et les services, même lorsqu'il existe des erreurs humaines, des pannes, des logiciels vulnérables ou des personnes malveillantes.

Prenons l'exemple d'une école qui utilise une application pour gérer les inscriptions et les notes. Il ne suffit pas que l'application fonctionne et affiche une page de connexion. Il faut également que les élèves ne puissent pas consulter les dossiers des autres, que les notes ne soient pas modifiées sans autorisation et que les enseignants puissent accéder au service lorsqu'ils doivent saisir les résultats.

La sécurité doit donc répondre à plusieurs objectifs complémentaires.

### 1.2. Pourquoi a-t-on besoin d'un modèle de sécurité ?

Lorsqu'on étudie un système informatique, il est facile de se concentrer uniquement sur les menaces les plus visibles. On peut, par exemple, considérer qu'un système est sécurisé parce qu'il utilise un mot de passe complexe ou parce qu'il possède un antivirus.

Ces mesures peuvent être utiles, mais elles ne garantissent pas toutes les propriétés nécessaires.

Un mot de passe solide ne permet pas, à lui seul, de récupérer des données supprimées. Une sauvegarde ne garantit pas que les fichiers d'origine n'ont pas été modifiés par un utilisateur malveillant. Le chiffrement d'une base de données ne garantit pas que son service restera disponible pendant une panne électrique.

Il faut donc examiner la sécurité sous plusieurs angles.

La triade CIA offre précisément cette grille de lecture. Elle permet de poser trois questions fondamentales :

1. **Confidentialité :** seules les personnes et les applications autorisées peuvent-elles accéder aux informations ?
2. **Intégrité :** les informations restent-elles exactes, complètes et protégées contre les modifications non autorisées ?
3. **Disponibilité :** les personnes autorisées peuvent-elles accéder aux informations et aux services lorsqu'elles en ont besoin ?

Ces objectifs sont reconnus dans les références du National Institute of Standards and Technology (NIST), organisme américain qui publie des recommandations et des ressources techniques en matière de sécurité informatique.

### 1.3. Que signifie CIA ?

Dans le domaine de la cybersécurité, CIA est un acronyme anglais. Il ne désigne pas ici une agence de renseignement.

| Lettre | Terme anglais | Terme français | Question centrale |
|---|---|---|---|
| C | Confidentiality | Confidentialité | Qui peut voir l'information ? |
| I | Integrity | Intégrité | L'information est-elle correcte et protégée contre les modifications non autorisées ? |
| A | Availability | Disponibilité | Le service est-il accessible quand il est nécessaire ? |

On représente souvent la triade par un triangle dont chaque sommet correspond à l'un de ces objectifs.

```text
                    CONFIDENTIALITÉ
                    Qui peut accéder ?
                         /\
                        /  \
                       /    \
                      /      \
                     / SÉCURITÉ\
                    /          \
                   /____________\
             INTÉGRITÉ        DISPONIBILITÉ
          Données fiables    Accès au moment utile
```

Ce dessin est une aide à la mémorisation. Il ne signifie pas que chaque propriété possède la même importance dans toutes les organisations. L'importance relative dépend de l'activité, des données traitées, des obligations applicables et des conséquences possibles d'un incident.

Par exemple, la confidentialité est particulièrement importante pour un dossier médical. L'intégrité est essentielle pour une transaction bancaire. La disponibilité est critique pour un service d'urgence ou un système de supervision industrielle.

Dans les trois cas, les autres propriétés restent pertinentes.

### 1.4. Ce que la triade CIA n'est pas

La triade CIA est un modèle de base, pas une solution technique complète.

Elle ne fournit pas automatiquement une configuration de pare-feu, une politique de mots de passe ou une architecture de sauvegarde. Elle permet plutôt de déterminer les objectifs que ces mécanismes doivent contribuer à atteindre.

Elle ne signifie pas non plus qu'un système peut atteindre une sécurité absolue. Aucun mécanisme ne supprime tous les risques. Le travail du professionnel consiste à comprendre les risques, à choisir des protections adaptées et à vérifier que ces protections fonctionnent.

Enfin, la triade ne couvre pas tous les aspects de la confiance informatique. L'authenticité, la traçabilité, la responsabilité et la non-répudiation sont également importantes. Elles complètent les objectifs CIA dans de nombreux systèmes.

### 1.5. Les objectifs pédagogiques du cours

À la fin de cette leçon, tu devras être capable de :

- définir précisément la confidentialité, l'intégrité et la disponibilité ;
- distinguer les trois propriétés dans une situation concrète ;
- reconnaître les menaces susceptibles de compromettre chaque propriété ;
- expliquer le rôle du contrôle d'accès, du chiffrement, des sauvegardes et de la journalisation ;
- effectuer quelques vérifications simples sur un ordinateur ;
- expliquer pourquoi une même attaque peut toucher plusieurs propriétés ;
- proposer une première stratégie de protection pour un service informatique ;
- présenter un raisonnement de sécurité compréhensible par un collègue ou un responsable.

Aucune connaissance avancée en informatique n'est nécessaire pour commencer. Les notions plus techniques seront introduites progressivement.

## 2. Comprendre la confidentialité

### 2.1. Définition

La **confidentialité** est la propriété qui consiste à empêcher la divulgation d'informations à des personnes, des organisations ou des processus qui ne sont pas autorisés à y accéder.

Il faut souligner deux éléments.

Premièrement, l'information doit être accessible aux personnes autorisées. La confidentialité ne signifie donc pas que personne ne doit pouvoir consulter les données.

Deuxièmement, l'autorisation doit être adaptée au rôle de chaque utilisateur. Une personne peut avoir le droit de lire certaines informations sans avoir le droit de consulter tout le reste.

Prenons l'exemple d'un établissement scolaire. Un enseignant doit pouvoir consulter les notes des élèves de ses classes. Il n'a pas nécessairement besoin de consulter les informations salariales du personnel administratif. Le responsable des ressources humaines doit accéder aux dossiers des employés, mais n'a pas automatiquement besoin de modifier les notes scolaires.

La confidentialité consiste à appliquer des limites d'accès cohérentes avec les responsabilités de chacun.

### 2.2. Quelles informations doivent rester confidentielles ?

La sensibilité d'une information dépend de son contexte.

On peut notamment protéger :

**Les données personnelles.** Il s'agit, par exemple, des noms, adresses, numéros de téléphone, coordonnées bancaires ou informations permettant d'identifier une personne.

**Les données de santé.** Les dossiers médicaux, les résultats d'analyses et les informations relatives à une prise en charge médicale peuvent nécessiter une protection particulièrement stricte.

**Les secrets d'authentification.** Les mots de passe, jetons de session, clés privées et clés d'accès permettent parfois de prendre le contrôle d'un compte ou d'un service.

**Les informations commerciales.** Une entreprise peut devoir protéger ses contrats, ses tarifs confidentiels, ses plans d'affaires et ses données clients.

**Les informations techniques sensibles.** Les schémas d'architecture interne, les configurations réseau, les clés cryptographiques et certaines informations de sécurité peuvent faciliter une attaque si elles sont divulguées.

**Les informations opérationnelles.** Les horaires, les procédures internes ou les données d'inventaire peuvent être confidentiels selon l'activité et les risques associés.

Tout n'est cependant pas secret par défaut. Certaines informations ont vocation à être publiques, comme la documentation commerciale publiée par une entreprise. Le travail de sécurité consiste à déterminer quelles informations doivent être protégées, et contre quelles catégories d'accès.

### 2.3. Exemple : le dossier d'un client

Imaginons une entreprise qui conserve les données suivantes :

```text
CLIENT
├── Nom
├── Adresse électronique
├── Numéro de téléphone
├── Historique des commandes
└── Adresse de livraison
```

Un employé du service client doit pouvoir consulter l'historique des commandes pour répondre aux réclamations.

En revanche, une personne qui visite le site sans compte ne doit pas pouvoir accéder aux informations personnelles de ce client.

Si l'application laisse n'importe quel visiteur récupérer un dossier en remplaçant simplement un identifiant dans une URL, la confidentialité est compromise.

Par exemple, un site mal conçu pourrait utiliser une adresse de la forme :

```text
https://exemple.invalid/clients/1042
```

Si un utilisateur peut remplacer `1042` par `1043` et lire le dossier d'une autre personne sans contrôle d'autorisation, l'application présente une faille de contrôle d'accès.

La solution n'est pas simplement de rendre les identifiants difficiles à deviner. Le serveur doit vérifier systématiquement que la personne connectée est autorisée à accéder au dossier demandé.

### 2.4. Les menaces contre la confidentialité

Plusieurs catégories de menaces peuvent provoquer une divulgation d'informations.

#### L'accès non autorisé

Une personne utilise un compte qu'elle ne devrait pas pouvoir utiliser, exploite une faille d'application ou accède à un ordinateur laissé ouvert.

L'accès non autorisé peut être facilité par des mots de passe faibles, des comptes partagés ou des droits trop larges.

#### Le vol d'identifiants

Un attaquant peut obtenir un mot de passe par hameçonnage, par réutilisation d'un mot de passe déjà divulgué ou par l'installation d'un logiciel malveillant.

Si le compte permet d'accéder à des informations sensibles, leur confidentialité peut alors être compromise.

#### L'erreur humaine

La fuite n'est pas toujours provoquée par un pirate.

Une personne peut envoyer un fichier contenant des informations confidentielles au mauvais destinataire, publier par erreur un document privé ou accorder un accès public à un espace de stockage.

#### La mauvaise configuration

Un service de stockage, une base de données ou une interface d'administration peut être accessible depuis Internet alors qu'il devrait être limité à des utilisateurs ou à des réseaux précis.

#### L'interception des communications

Lorsque les données circulent entre un ordinateur et un serveur, elles peuvent être exposées si les communications ne sont pas convenablement protégées.

Le chiffrement des communications, notamment par HTTPS correctement configuré, aide à protéger les données en transit.

### 2.5. Comment protéger la confidentialité ?

Il existe plusieurs mécanismes complémentaires.

#### Le contrôle d'accès

Le contrôle d'accès détermine qui peut utiliser une ressource et quelles opérations cette personne peut effectuer.

Une application peut distinguer trois rôles :

| Rôle | Consulter les dossiers | Modifier les dossiers | Gérer les comptes |
|---|---|---|---|
| Visiteur | Informations publiques uniquement | Non | Non |
| Employé autorisé | Dossiers nécessaires à son travail | Selon ses fonctions | Non |
| Administrateur habilité | Selon sa mission | Selon ses fonctions | Oui, dans les limites prévues |

Ce tableau n'est qu'un exemple. Dans un véritable système, les autorisations doivent être définies à partir des fonctions et des responsabilités réellement nécessaires.

#### Le principe du moindre privilège

Le principe du moindre privilège consiste à accorder à chaque utilisateur, programme ou service uniquement les permissions nécessaires à sa mission.

Un employé qui doit consulter des factures n'a pas automatiquement besoin d'un accès administrateur à la base de données.

Un programme qui doit lire un fichier n'a pas nécessairement besoin de pouvoir supprimer tout un répertoire.

Ce principe réduit les conséquences d'une erreur ou de la compromission d'un compte.

#### L'authentification multifacteur

L'authentification multifacteur, souvent appelée MFA, demande plusieurs facteurs de vérification pour confirmer l'identité d'un utilisateur.

Selon la méthode choisie, il peut s'agir d'un élément connu de l'utilisateur, d'un appareil qu'il possède ou d'une caractéristique biométrique.

La MFA peut réduire le risque lié au vol d'un mot de passe. Elle ne remplace cependant pas le contrôle d'autorisation : une personne correctement authentifiée ne doit pas automatiquement pouvoir accéder à toutes les ressources.

#### Le chiffrement

Le chiffrement transforme les données à l'aide d'un mécanisme cryptographique et d'une clé. L'objectif est de rendre leur contenu illisible pour une personne qui ne possède pas les moyens autorisés de les déchiffrer.

Il peut protéger les données stockées sur un ordinateur, un disque ou un serveur, ainsi que les données qui circulent sur un réseau.

Le chiffrement ne suffit pas si les clés sont accessibles aux mauvaises personnes, si le compte de l'utilisateur est compromis ou si l'application affiche les données à un utilisateur qui ne devrait pas les voir.

Il faut donc protéger les clés, limiter les autorisations et maintenir une configuration correcte.

#### La classification des informations

Une organisation peut classer les informations selon leur sensibilité : publiques, internes, confidentielles ou très sensibles, par exemple.

Cette classification permet d'adapter les protections.

Un document public n'a pas besoin des mêmes restrictions qu'un fichier contenant des mots de passe ou des données financières. À l'inverse, placer des informations sensibles dans un espace partagé sans restriction est une erreur de conception.

#### La sensibilisation des utilisateurs

Les personnes doivent savoir comment reconnaître les messages suspects, partager correctement les documents, protéger leurs comptes et signaler un incident.

La sensibilisation ne remplace pas les mesures techniques. Elle réduit toutefois la probabilité que des données soient divulguées par erreur ou par manipulation.

### 2.6. Confidentialité des données au repos et en transit

Il est utile de distinguer deux situations.

Les **données au repos** sont stockées sur un support : disque dur, SSD, serveur, sauvegarde ou base de données.

Les **données en transit** circulent entre deux systèmes, par exemple entre un navigateur et un serveur.

Une troisième situation est celle des données en cours d'utilisation. Une application doit souvent les charger en mémoire pour les traiter. Dans ce cas, le contrôle des accès au système et à l'application reste important, même si les données sont chiffrées sur le disque.

Une stratégie complète doit tenir compte de ces différentes étapes.

### 2.7. Exemple pratique : un ordinateur portable perdu

Une entreprise prête un ordinateur portable à un employé. Celui-ci conserve des documents de travail et accède à une application interne.

Si l'ordinateur est perdu ou volé, plusieurs questions se posent :

- Les données stockées sont-elles chiffrées ?
- L'accès à la session est-il protégé ?
- Les comptes de l'employé peuvent-ils être révoqués rapidement ?
- Les sessions ouvertes peuvent-elles être invalidées ?
- Les documents sensibles étaient-ils réellement nécessaires sur cet ordinateur ?

Le chiffrement du disque peut réduire le risque de divulgation en cas de vol du matériel. La révocation des accès peut empêcher l'utilisation ultérieure des comptes. La minimisation des données locales réduit enfin la quantité d'informations exposées.

La bonne réponse associe donc plusieurs protections plutôt que de dépendre d'un seul outil.

## 3. Comprendre l'intégrité

### 3.1. Définition

L'**intégrité** désigne la protection des informations et des systèmes contre les modifications ou destructions non autorisées. Elle vise également à préserver l'exactitude, la cohérence et la complétude des données.

Une information peut rester confidentielle tout en étant fausse. À l'inverse, une information peut être parfaitement exacte mais accessible à tout le monde.

L'intégrité répond donc à une question différente de la confidentialité.

Prenons le cas d'un relevé bancaire. Si une personne non autorisée modifie le solde d'un compte de 500 000 FCFA à 50 000 FCFA, la donnée n'est plus exacte. Même si aucun tiers n'a consulté le relevé, l'intégrité a été compromise.

De même, si une application modifie accidentellement les résultats d'un examen ou si un programme corrompt un fichier, il existe un problème d'intégrité, même sans intervention malveillante.

### 3.2. Pourquoi l'intégrité est-elle essentielle ?

Les décisions informatiques et humaines reposent sur les informations disponibles.

Un médecin utilise un dossier pour prendre une décision clinique. Une banque utilise les données de transaction pour calculer les soldes. Un administrateur réseau s'appuie sur des configurations pour contrôler le trafic. Une application de formation se base sur les résultats des apprenants pour déterminer leur progression.

Si ces données ont été modifiées sans autorisation, les décisions qui en découlent peuvent être incorrectes.

L'intégrité concerne donc autant la protection contre les attaques que la fiabilité du fonctionnement quotidien.

### 3.3. Les différentes formes d'altération

Une perte d'intégrité peut prendre plusieurs formes.

**Modification non autorisée.** Une personne change une note, une facture, un tarif ou une configuration système sans en avoir le droit.

**Suppression.** Des informations sont effacées alors qu'elles doivent être conservées.

**Insertion frauduleuse.** Une transaction, un compte ou un enregistrement fictif est ajouté au système.

**Altération accidentelle.** Une erreur de manipulation ou un défaut logiciel modifie des données.

**Corruption technique.** Une panne matérielle, une erreur d'écriture ou un incident de stockage rend un fichier incomplet ou illisible.

**Altération en transit.** Les données reçues ne correspondent pas à ce qui a été envoyé, par exemple à cause d'une erreur de transmission ou d'une manipulation non autorisée.

Ces situations n'ont pas toutes la même origine et ne se détectent pas toujours de la même manière. Il faut donc choisir des mécanismes adaptés au type de données.

### 3.4. Exemple : modifier une note scolaire

Considérons une application qui enregistre les résultats d'étudiants.

Un enseignant saisit :

```text
Étudiant : Nadia
Matière   : Réseaux
Note      : 14/20
```

Une personne qui ne possède pas les droits nécessaires remplace ensuite la note par `20/20`.

La valeur affichée a changé, mais ce n'est pas le seul problème. L'application ne peut plus garantir que le résultat reflète réellement l'évaluation effectuée.

Pour mieux préserver l'intégrité, on peut mettre en place :

- des autorisations limitant les personnes capables de modifier les notes ;
- une validation des valeurs, par exemple en imposant une note comprise entre 0 et 20 ;
- une journalisation des modifications ;
- une identification claire de l'auteur de chaque changement ;
- une procédure de correction permettant de justifier les modifications ;
- des sauvegardes permettant de retrouver une version antérieure en cas d'incident.

La validation d'une valeur ne garantit pas, à elle seule, son intégrité. Une note de 19/20 peut être parfaitement valide du point de vue du format et néanmoins avoir été attribuée frauduleusement. Il faut combiner les contrôles techniques et les règles de gestion.

### 3.5. Les menaces contre l'intégrité

#### Le compte compromis

Un attaquant utilise un compte légitime dont il a obtenu les identifiants. Il peut essayer de modifier des données sans déclencher les contrôles conçus uniquement pour repérer les accès inconnus.

Il faut donc limiter les permissions, surveiller les actions sensibles et protéger les comptes.

#### Les erreurs de configuration

Une modification incorrecte d'une règle réseau peut interrompre des communications ou exposer des systèmes. Une modification erronée d'une base de données peut fausser les informations.

La gestion des changements doit permettre de vérifier, d'approuver et de tracer les modifications importantes.

#### Les logiciels malveillants

Certains logiciels malveillants altèrent des fichiers, détruisent des données ou chiffrent des documents en vue d'extorquer de l'argent. Les incidents de ce type peuvent affecter simultanément l'intégrité et la disponibilité.

#### Les erreurs humaines

Un utilisateur peut modifier une mauvaise ligne, écraser un fichier ou exécuter une commande dans le mauvais répertoire.

Les protections contre ces erreurs incluent les validations, les confirmations pour les opérations destructrices, les droits limités et les procédures de récupération.

#### Les failles applicatives

Une application qui ne vérifie pas les autorisations avant une modification peut permettre à un utilisateur de changer des données qui ne lui appartiennent pas.

La validation des entrées et le contrôle des permissions doivent être réalisés côté serveur, et pas uniquement dans l'interface affichée au navigateur.

### 3.6. Les mécanismes de protection de l'intégrité

#### Les permissions et la séparation des rôles

Il faut distinguer les personnes qui consultent les données de celles qui peuvent les modifier ou les supprimer.

Les actions critiques peuvent nécessiter une approbation supplémentaire ou une séparation des responsabilités. Par exemple, une même personne ne devrait pas forcément pouvoir créer un fournisseur, modifier ses coordonnées bancaires et approuver seule le paiement associé.

#### Les journaux d'audit

Un journal d'audit enregistre les événements importants : connexions, changements de permissions, modifications de données ou actions administratives.

Un journal utile indique notamment :

- quand l'action a eu lieu ;
- quel compte l'a effectuée ;
- quelle ressource a été concernée ;
- quelle action a été réalisée ;
- si l'opération a réussi ou échoué.

Il faut également protéger les journaux. Si un attaquant peut modifier librement les traces de ses actions, celles-ci perdent une grande partie de leur valeur.

La centralisation des journaux et la limitation de leurs droits de modification peuvent aider à protéger leur fiabilité.

#### Les sommes de contrôle et les fonctions de hachage

Une fonction de hachage cryptographique transforme des données en une empreinte de longueur déterminée. Avec une fonction comme SHA-256, une modification du contenu entraîne généralement une empreinte différente.

L'empreinte peut servir à vérifier qu'un fichier téléchargé correspond au fichier de référence, à condition que l'empreinte de référence soit elle-même fiable.

Exemple : tu possèdes un fichier appelé `document.txt`. Sous Linux, tu peux calculer son empreinte avec :

```bash
sha256sum document.txt
```

Sous macOS, la commande est également :

```bash
shasum -a 256 document.txt
```

Sous Windows PowerShell :

```powershell
Get-FileHash .\document.txt -Algorithm SHA256
```

Ces commandes lisent le contenu du fichier et affichent une empreinte. Elles ne modifient pas le fichier.

Si tu calcules l'empreinte, modifies le texte puis calcules une nouvelle empreinte, les valeurs devraient être différentes.

**Limite importante :** une empreinte seule n'empêche pas une modification. Si un attaquant peut remplacer à la fois le fichier et l'empreinte de référence, il peut tromper une vérification naïve. Il faut donc protéger la référence, par exemple au moyen d'une signature numérique ou d'un canal de confiance.

Une fonction de hachage n'est pas non plus un chiffrement. Elle ne permet pas de retrouver directement le contenu original à partir de l'empreinte.

#### Les signatures numériques

Une signature numérique permet de vérifier qu'un message ou un fichier a été signé avec une clé privée correspondant à une clé publique connue, et que le contenu vérifié correspond au contenu signé.

Elle contribue à vérifier l'intégrité et l'origine du contenu. Il faut toutefois vérifier que la clé publique appartient bien à l'entité attendue et que la clé privée est restée protégée.

Une signature ne prouve pas automatiquement qu'une personne physique a réalisé une action dans tous les contextes possibles. La gestion des identités, des clés et des procédures de signature reste importante.

#### Les sauvegardes et la restauration

Une sauvegarde peut permettre de restaurer une version antérieure des données après une corruption ou une modification frauduleuse.

Elle aide à rétablir l'intégrité, mais seulement si elle contient une version saine des données et que sa restauration fonctionne.

Il faut donc vérifier les sauvegardes, protéger leur accès et tester les procédures de restauration.

#### La validation des données

Une application doit vérifier que les informations reçues respectent les règles attendues.

Pour un champ de quantité, on peut imposer une valeur numérique positive. Pour une date de naissance, on peut vérifier le format et la cohérence de la date. Pour un transfert d'argent, on peut contrôler le montant, le compte débité, le compte crédité et les autorisations du demandeur.

Ces validations réduisent les erreurs et certaines manipulations, mais elles doivent être cohérentes avec les règles métier.

### 3.7. Intégrité des données et intégrité du système

Il faut distinguer deux notions proches.

L'intégrité des données concerne l'exactitude et la protection des informations. L'intégrité du système concerne notamment le fait que le système et ses composants restent dans un état autorisé et fonctionnent comme prévu.

Par exemple, un fichier de configuration réseau peut être exact mais un logiciel malveillant présent sur le serveur peut altérer le comportement du système. À l'inverse, le système peut fonctionner correctement tout en affichant une donnée incorrecte qui a été saisie à l'origine.

Une démarche de sécurité doit considérer les deux aspects.

## 4. Comprendre la disponibilité

### 4.1. Définition

La **disponibilité** est la propriété qui permet aux utilisateurs et aux processus autorisés d'accéder aux informations et aux services dans les conditions et les délais nécessaires.

Un système peut être parfaitement confidentiel et conserver des données exactes, mais être inutilisable si son serveur est en panne.

Imaginons un service hospitalier qui ne parvient plus à consulter les dossiers des patients. Même si aucune donnée n'a été divulguée ou modifiée, l'indisponibilité peut perturber le fonctionnement de l'établissement.

La disponibilité ne signifie pas nécessairement qu'un service doit fonctionner sans aucune interruption pendant toute son existence. Elle signifie qu'il doit atteindre un niveau de disponibilité adapté à son besoin.

### 4.2. Pourquoi un service devient-il indisponible ?

Plusieurs causes sont possibles.

**Panne matérielle.** Un disque, un serveur, une alimentation ou un équipement réseau peut tomber en panne.

**Panne logicielle.** Une mise à jour défectueuse, une erreur de programmation ou un service bloqué peut empêcher l'application de fonctionner.

**Erreur humaine.** Un administrateur peut supprimer une configuration nécessaire, arrêter le mauvais service ou appliquer une règle réseau incorrecte.

**Saturation des ressources.** Un serveur peut manquer de mémoire, d'espace disque, de capacité CPU ou de connexions disponibles.

**Coupure d'alimentation.** Une panne électrique ou un problème de refroidissement peut arrêter un environnement informatique.

**Incident réseau.** Un lien défaillant, une mauvaise configuration du routage ou une panne DNS peut rendre un service inaccessible même si le serveur fonctionne.

**Attaque par déni de service.** Un attaquant peut chercher à saturer les ressources d'un service afin d'empêcher les utilisateurs légitimes d'y accéder.

**Rançongiciel ou destruction de données.** Un logiciel malveillant peut rendre les fichiers ou les systèmes inutilisables. Cette situation affecte souvent la disponibilité et peut également compromettre l'intégrité.

L'origine d'une panne n'est donc pas nécessairement une attaque. La disponibilité doit être protégée contre les incidents malveillants et accidentels.

### 4.3. Exemple : une application inaccessible

Supposons qu'une plateforme de formation possède un serveur Web, une base de données et un réseau d'accès.

```text
Apprenant
    |
    v
Réseau / Internet
    |
    v
Serveur Web
    |
    v
Base de données
```

Pour qu'un cours soit accessible, plusieurs composants doivent fonctionner.

Si le réseau est coupé, l'apprenant ne peut pas atteindre le serveur. Si le serveur Web est arrêté, la page ne répond plus. Si la base de données est indisponible, le site peut afficher une erreur ou ne plus retrouver les leçons.

La disponibilité est donc une propriété du service complet, et pas seulement d'un ordinateur isolé.

### 4.4. Les mécanismes de protection de la disponibilité

#### La redondance

La redondance consiste à disposer de composants ou de capacités supplémentaires pour éviter qu'une panne unique entraîne l'arrêt total du service.

Par exemple, une organisation peut avoir deux alimentations, plusieurs liens réseau ou plusieurs instances d'une application.

La redondance doit être conçue correctement. Deux serveurs situés dans le même local peuvent tous les deux être affectés par un incendie ou une coupure électrique. La présence de deux composants ne garantit donc pas automatiquement la résilience.

#### Les sauvegardes

Les sauvegardes servent à restaurer les données après un incident.

Cependant, sauvegarder un fichier ne garantit pas que l'application pourra redémarrer immédiatement. Il peut également être nécessaire de restaurer les serveurs, les configurations, les clés et les dépendances.

Une politique de sauvegarde doit donc prévoir des tests de restauration et des responsabilités clairement définies.

#### La supervision

La supervision consiste à observer l'état des systèmes, des services et des ressources.

On peut surveiller le temps de réponse, l'espace disque, la mémoire, la charge CPU, l'état des services et les erreurs rencontrées.

Une alerte rapide permet de détecter un problème avant qu'il ne provoque une interruption plus importante.

Les outils de supervision n'empêchent pas toutes les pannes, mais ils aident à les détecter et à réduire leur durée.

#### Les mises à jour et la maintenance

Un système mal entretenu peut devenir instable, manquer de capacité ou être vulnérable à des attaques.

La maintenance consiste notamment à appliquer des mises à jour, contrôler l'état des composants, documenter les configurations et prévoir les interventions.

Les mises à jour doivent être préparées et testées selon le niveau de criticité du système. Une mise à jour non vérifiée peut elle-même provoquer une indisponibilité.

#### La protection contre les dénis de service

Un service accessible sur Internet doit anticiper les requêtes excessives ou malveillantes.

Selon le contexte, les protections peuvent comprendre la limitation du débit, le filtrage du trafic, l'équilibrage de charge, la mise en cache et des services spécialisés de protection contre les attaques volumétriques.

La capacité disponible et les limites des protections doivent être évaluées en fonction des besoins réels.

#### Le plan de continuité

Un plan de continuité décrit la manière dont une organisation maintient ses activités essentielles pendant un incident.

Il peut préciser les priorités, les responsabilités, les solutions de secours, les moyens de communication et les procédures de reprise.

Un tel plan doit être testé. Un document qui n'a jamais été vérifié ne garantit pas que les équipes sauront l'utiliser correctement.

### 4.5. Les notions de RTO et de RPO

Deux notions sont particulièrement utiles pour comprendre la disponibilité et la récupération après incident.

**RTO — Recovery Time Objective**, ou objectif de durée de reprise : il s'agit du délai cible dans lequel un service doit être rétabli après une interruption.

**RPO — Recovery Point Objective**, ou objectif de point de reprise : il désigne la perte maximale de données, exprimée comme une durée, que l'organisation accepte en cas d'incident.

Exemple :

Une entreprise définit les objectifs suivants pour son application de commandes :

- RTO : 4 heures ;
- RPO : 30 minutes.

Cela signifie qu'elle vise un rétablissement du service dans les quatre heures suivant l'interruption et qu'elle accepte au maximum une perte de données correspondant à environ trente minutes de travail, dans le scénario de reprise considéré.

Ces valeurs sont des objectifs, pas une garantie automatique. Il faut une architecture, des sauvegardes, des procédures et des tests adaptés pour les atteindre.

Un système qui doit reprendre en quelques minutes peut demander une infrastructure très différente d'un service interne utilisé une fois par semaine.

### 4.6. Disponibilité et sauvegardes : une confusion fréquente

Une sauvegarde protège principalement la capacité à récupérer des données. Elle ne garantit pas à elle seule un accès immédiat au service.

Si une base de données de 500 Go est restaurée sur un serveur, le temps de copie, la reconstruction des index, la validation des données et le redémarrage de l'application peuvent prendre du temps.

Pour améliorer la disponibilité, il peut aussi être nécessaire de disposer de composants redondants, de procédures de reprise documentées et d'une supervision efficace.

Il faut donc distinguer la protection contre la perte de données et la réduction de la durée d'interruption. Les deux sont complémentaires.

## 5. Les trois propriétés dans une même situation

### 5.1. La triade fonctionne comme un ensemble

Dans la pratique, confidentialité, intégrité et disponibilité sont interdépendantes.

Une application qui expose des données confidentielles peut également subir des modifications frauduleuses si l'attaquant obtient des droits élevés.

Une attaque qui détruit une base de données peut compromettre son intégrité et empêcher son accès, affectant ainsi la disponibilité.

Une mauvaise politique de sauvegarde peut conduire à une perte définitive de données, ce qui affecte l'intégrité historique et la disponibilité des informations.

Il faut donc examiner les trois propriétés à chaque analyse.

### 5.2. Étude de cas : une boutique en ligne

Considérons une boutique qui traite des commandes et des paiements.

Ses données comprennent les comptes clients, les articles, les prix, les commandes et les informations de suivi.

**Incident A : divulgation de données.**

Un visiteur parvient à consulter les adresses de livraison d'autres clients en manipulant les identifiants de l'application.

La propriété directement compromise est la confidentialité. Les informations sont accessibles à une personne qui n'est pas autorisée à les consulter.

**Incident B : modification des tarifs.**

Un compte compromis permet de remplacer le prix de certains articles. Des clients voient des tarifs erronés et passent des commandes incorrectes.

L'intégrité est directement compromise. La disponibilité peut rester normale, puisque le site continue de répondre.

**Incident C : site hors service.**

Une panne de base de données empêche les clients d'afficher leur panier et de finaliser leurs achats.

La disponibilité est directement compromise. Selon la cause et les conséquences, il peut également y avoir une atteinte à l'intégrité si certaines commandes ont été perdues ou corrompues.

**Incident D : rançongiciel.**

Un logiciel malveillant chiffre des fichiers de données et bloque l'accès à une partie du système.

La disponibilité est affectée. L'intégrité peut également être affectée si les données ont été modifiées, supprimées ou rendues irrécupérables. La confidentialité peut être compromise si l'attaquant a également copié les données avant de les chiffrer.

Cette dernière situation illustre pourquoi il ne faut pas toujours attribuer un incident à une seule lettre de la triade.

### 5.3. Tableau de correspondance

| Situation | Confidentialité | Intégrité | Disponibilité |
|---|---|---|---|
| Divulgation d'un dossier à une personne non autorisée | Directement touchée | Pas nécessairement | Pas nécessairement |
| Modification frauduleuse d'un prix | Pas nécessairement | Directement touchée | Pas nécessairement |
| Panne d'un serveur Web | Pas nécessairement | Pas nécessairement | Directement touchée |
| Suppression non autorisée d'une base de données | Pas nécessairement | Touchée | Souvent touchée |
| Vol d'un ordinateur contenant des fichiers non chiffrés | Risque élevé | Possible | Possible |
| Hameçonnage suivi d'un vol de compte | Risque élevé | Possible | Possible |
| Saturation d'un service par des requêtes excessives | Pas nécessairement | Pas nécessairement | Directement touchée |
| Sauvegarde inutilisable après une panne | Pas nécessairement | Récupération compromise | Récupération retardée ou impossible |

Dans ce tableau, « pas nécessairement » est important. Une situation ne touche pas systématiquement toutes les propriétés. Il faut identifier les effets réellement observés ou plausibles dans le contexte étudié.

### 5.4. Choisir des protections adaptées

Un outil ne protège pas toujours les trois propriétés de la même manière.

Le chiffrement contribue à la confidentialité. Il peut aussi contribuer à l'intégrité lorsqu'il est associé à un mécanisme d'authentification cryptographique, mais un chiffrement sans authentification ne garantit pas à lui seul que les données n'ont pas été modifiées.

Une sauvegarde aide à récupérer des données et soutient ainsi l'intégrité et la disponibilité, à condition qu'elle soit saine et accessible au moment de la restauration. Elle doit elle-même être protégée contre les accès non autorisés.

La journalisation aide à détecter des actions inhabituelles et à reconstituer un incident. Elle ne bloque pas automatiquement toutes les modifications et ne remplace pas les autorisations.

Le contrôle d'accès contribue à limiter les divulgations et les modifications non autorisées. Il peut également éviter des actions accidentelles susceptibles d'arrêter un service.

La sécurité résulte donc de protections combinées, organisées autour de risques identifiés.

## 6. Menaces, vulnérabilités et risques

Pour appliquer correctement la triade CIA, il faut comprendre quelques notions supplémentaires.

### 6.1. Menace

Une menace est une cause potentielle d'incident.

Il peut s'agir d'un attaquant, d'un logiciel malveillant, d'une erreur humaine, d'une panne matérielle ou d'un événement physique.

Exemple : un ordinateur peut être volé. Le vol constitue une menace pour les données qu'il contient.

### 6.2. Vulnérabilité

Une vulnérabilité est une faiblesse exploitable dans un système, une configuration, une procédure ou une organisation.

Un ordinateur dont le disque n'est pas chiffré peut présenter une faiblesse si des données sensibles y sont stockées et si le matériel est perdu ou volé.

Un compte doté de droits excessifs peut constituer une faiblesse si son titulaire commet une erreur ou si ses identifiants sont compromis.

### 6.3. Risque

Le risque correspond à la possibilité qu'un événement produise des conséquences négatives.

Dans une analyse élémentaire, on examine souvent :

- la vraisemblance de l'événement ;
- la gravité de ses conséquences ;
- les protections déjà en place ;
- les conséquences résiduelles après application des protections.

On peut utiliser une matrice simple pour classer les risques, par exemple faible, moyen, élevé ou critique. Il ne faut cependant pas confondre cette classification avec une mesure scientifique exacte : les méthodes de calcul varient selon les organisations.

### 6.4. Exemple de raisonnement

Une petite entreprise conserve les factures de ses clients sur un ordinateur partagé.

**Actif :** les factures et les informations qu'elles contiennent.

**Menace :** une personne non autorisée peut accéder à l'ordinateur.

**Vulnérabilité :** tous les employés utilisent le même compte, sans restriction de fichiers.

**Conséquence possible :** une personne consulte des données qui ne sont pas nécessaires à son travail.

**Propriété CIA principalement concernée :** confidentialité.

**Mesures envisageables :** comptes individuels, droits d'accès adaptés, verrouillage de session, chiffrement du disque et sensibilisation des utilisateurs.

Cette méthode évite de choisir un outil sans savoir quel problème on veut résoudre.

### 6.5. Pourquoi la confidentialité, l'intégrité et la disponibilité ne se résument pas à une liste d'outils

Une erreur fréquente consiste à dire : « Pour la confidentialité, on installe un antivirus ; pour l'intégrité, on fait une sauvegarde ; pour la disponibilité, on achète un second serveur. »

Ces raccourcis sont trop simplistes.

Un antivirus peut contribuer à réduire certains risques, mais ne contrôle pas nécessairement les permissions des utilisateurs. Une sauvegarde peut être inutilisable. Un second serveur peut partager la même alimentation électrique ou la même panne réseau que le premier.

Il faut raisonner à partir de la menace, de la vulnérabilité et de la conséquence recherchée. On choisit ensuite les mesures et on vérifie leur efficacité.

## 7. Appliquer la triade CIA à un réseau informatique

### 7.1. Exemple d'architecture réseau

Une entreprise possède un réseau local, des postes de travail, un serveur de fichiers et une application métier.

```text
                  INTERNET
                      |
                  Pare-feu
                      |
                Routeur / LAN
                      |
            +---------+---------+
            |                   |
        Postes employés     Serveur métier
                                |
                           Base de données
```

Cette représentation est volontairement simplifiée. Elle permet de comprendre comment les propriétés CIA s'appliquent à l'ensemble de l'infrastructure.

### 7.2. Confidentialité sur un réseau

La confidentialité consiste notamment à empêcher un poste non autorisé d'accéder au serveur métier et à protéger les échanges entre les clients et le serveur.

Les mécanismes possibles comprennent :

- la segmentation du réseau selon les besoins ;
- le contrôle des accès au niveau de l'application ;
- des règles de filtrage adaptées ;
- le chiffrement des communications ;
- la protection des comptes d'administration ;
- la gestion sécurisée des clés et des secrets.

Un pare-feu peut limiter les flux réseau, mais il ne garantit pas, à lui seul, que chaque utilisateur de l'application ne consultera que les données auxquelles il a droit.

Le contrôle réseau et le contrôle d'accès applicatif doivent être conçus ensemble.

### 7.3. Intégrité sur un réseau

L'intégrité peut être concernée par les changements de configuration, les altérations de données et les modifications de messages.

Par exemple, lorsqu'un administrateur modifie une configuration sur un commutateur ou un routeur, il faut réduire le risque d'une modification incorrecte.

Des mesures utiles comprennent :

- des sauvegardes de configuration ;
- une procédure d'approbation pour les changements critiques ;
- la limitation des comptes administrateurs ;
- des journaux d'administration ;
- des comparaisons de configuration ;
- une procédure de retour arrière.

La gestion des changements permet de savoir ce qui a changé, pourquoi et par qui. Elle est particulièrement importante dans les réseaux qui doivent rester stables.

### 7.4. Disponibilité sur un réseau

La disponibilité d'un service réseau dépend de nombreux composants : l'alimentation, les équipements, les liens, le routage, le DNS, les serveurs et les applications.

Une panne peut se produire même lorsqu'un seul composant est indisponible. C'est pourquoi les architectures critiques utilisent souvent des mécanismes de redondance et des procédures de reprise.

La supervision doit être capable de détecter les problèmes de connectivité et de performance. Une alerte portant uniquement sur l'état « allumé » d'un serveur ne garantit pas que l'application est réellement utilisable.

Il est souvent utile de surveiller le service vu du point de vue de l'utilisateur, par exemple en vérifiant qu'une page répond ou qu'une requête de test aboutit.

## 8. Un peu de pratique : vérifier l'intégrité d'un fichier

Cette section est une première activité technique. Elle ne nécessite pas d'accès à un réseau tiers ni de privilèges administrateur.

### 8.1. Objectif

Tu vas créer un fichier de test, calculer son empreinte, modifier son contenu et comparer les résultats.

Cette activité permet de comprendre comment un outil simple peut détecter une modification. Elle ne prouve pas, à elle seule, que le système est inviolable.

### 8.2. Sur Windows avec PowerShell

Ouvre PowerShell dans un dossier de travail où tu es autorisé à créer des fichiers. Exécute :

```powershell
"Bonjour, cybersécurité !" | Set-Content -Path .\cia-demo.txt -Encoding utf8
Get-FileHash .\cia-demo.txt -Algorithm SHA256
```

La première commande crée le fichier. La seconde calcule son empreinte SHA-256.

Note la valeur affichée dans le champ `Hash`.

Modifie ensuite le contenu :

```powershell
"Bonjour, securite informatique !" | Set-Content -Path .\cia-demo.txt -Encoding utf8
Get-FileHash .\cia-demo.txt -Algorithm SHA256
```

Compare les deux empreintes. Elles devraient être différentes parce que le contenu n'est plus identique.

Pour afficher le contenu du fichier, tu peux utiliser :

```powershell
Get-Content .\cia-demo.txt
```

Pour supprimer le fichier de démonstration après l'exercice, vérifie d'abord que tu es dans le bon dossier, puis utilise :

```powershell
Remove-Item .\cia-demo.txt
```

Ne lance pas cette dernière commande sur un fichier important. Elle ne sert ici qu'à nettoyer le fichier de test créé pour l'activité.

### 8.3. Sur Linux

Dans un répertoire de test, exécute :

```bash
printf '%s\n' 'Bonjour, cybersécurité !' > cia-demo.txt
sha256sum cia-demo.txt
```

Note l'empreinte. Modifie ensuite le fichier :

```bash
printf '%s\n' 'Bonjour, securite informatique !' > cia-demo.txt
sha256sum cia-demo.txt
```

Compare les résultats. Ils devraient être différents.

Pour lire le fichier :

```bash
cat cia-demo.txt
```

Pour supprimer uniquement le fichier créé pendant ce test :

```bash
rm cia-demo.txt
```

Assure-toi de bien identifier le fichier avant de le supprimer.

### 8.4. Que démontre cette expérience ?

Cette activité montre qu'une fonction de hachage comme SHA-256 produit une empreinte liée au contenu traité. Une modification du contenu entraîne normalement une empreinte différente.

Elle illustre un mécanisme de vérification de l'intégrité.

Elle ne démontre pas que :

- le fichier est confidentiel ;
- le fichier est disponible en permanence ;
- la personne qui l'a créé est digne de confiance ;
- l'empreinte de référence provient d'une source fiable ;
- un attaquant ne peut pas remplacer simultanément le fichier et sa référence.

Pour vérifier l'intégrité d'un téléchargement, il faut comparer l'empreinte calculée avec une empreinte de référence obtenue par un canal de confiance. Si cette référence est publiée à côté d'un fichier sur une page compromise, la comparaison ne suffit pas nécessairement.

### 8.5. Pourquoi cette activité ne prouve-t-elle pas la confidentialité ?

Le fichier `cia-demo.txt` reste lisible par toute personne autorisée à accéder à son emplacement. Le calcul de l'empreinte n'empêche pas sa consultation.

Pour protéger la confidentialité, il faut examiner les permissions du fichier, les comptes qui peuvent y accéder et les protections du support de stockage.

Cet exemple permet de retenir une distinction fondamentale : une propriété peut être protégée sans que les deux autres le soient automatiquement.

## 9. Activité guidée : construire une première matrice CIA

### 9.1. Scénario

Une petite entreprise possède un service informatique composé de quatre éléments :

1. une base de données qui contient les informations des clients ;
2. une application Web de gestion des commandes ;
3. un serveur de fichiers utilisé par les employés ;
4. une connexion Internet qui permet aux clients d'accéder au site.

L'entreprise souhaite identifier les risques prioritaires avant d'investir dans de nouvelles protections.

### 9.2. Étape 1 — Identifier les actifs

Un actif est quelque chose qui possède une valeur pour l'organisation et qui doit être protégé.

Dans ce scénario, les actifs peuvent être les données des clients, les commandes, les fichiers de travail, l'application Web, les équipements réseau et les comptes utilisateurs.

Il faut décrire les actifs de manière suffisamment précise pour pouvoir identifier les conséquences d'un incident.

Dire « protéger l'informatique » est trop vague. Dire « préserver la confidentialité des adresses clients enregistrées dans la base de données » est beaucoup plus utile.

### 9.3. Étape 2 — Définir les besoins

Pour chaque actif, on se demande si sa confidentialité, son intégrité et sa disponibilité sont importantes.

| Actif | Confidentialité | Intégrité | Disponibilité |
|---|---|---|---|
| Données clients | Élevée | Élevée | Élevée |
| Prix des produits | Selon la politique commerciale | Très élevée | Élevée |
| Fichiers internes | Selon leur sensibilité | Élevée | Moyenne à élevée |
| Site de commande | Selon les données affichées et traitées | Élevée | Très élevée |

Cette classification est illustrative. Les niveaux doivent être définis par l'organisation en fonction de ses activités et des conséquences qu'elle souhaite éviter.

Une propriété peut être plus critique qu'une autre pour un actif donné, mais il ne faut pas négliger les autres sans justification.

### 9.4. Étape 3 — Identifier les incidents plausibles

Pour les données clients, on peut envisager une fuite, une modification ou une perte des dossiers.

Pour les prix des produits, il faut envisager des changements frauduleux, des erreurs de saisie et des problèmes de synchronisation.

Pour le serveur de fichiers, il faut anticiper les suppressions accidentelles, les accès excessifs et les pannes de stockage.

Pour le site de commande, il faut anticiper les erreurs applicatives, les interruptions réseau et la saturation du service.

Les scénarios ne doivent pas se limiter aux attaques sophistiquées. Les erreurs quotidiennes représentent également une source importante de risques.

### 9.5. Étape 4 — Associer des mesures

| Problème identifié | Mesures envisageables | Propriété principalement visée |
|---|---|---|
| Des employés accèdent à des dossiers clients sans raison professionnelle | Comptes individuels et permissions adaptées | Confidentialité |
| Des prix peuvent être modifiés par des personnes non habilitées | Contrôle d'autorisation, validation métier et journalisation | Intégrité |
| Un serveur de fichiers peut tomber en panne | Supervision, sauvegardes testées et procédure de restauration | Disponibilité et intégrité |
| Un attaquant peut voler un mot de passe | MFA, protection contre l'hameçonnage et surveillance des connexions | Confidentialité et intégrité, selon les accès |
| Une règle réseau incorrecte peut interrompre le site | Gestion des changements, sauvegarde de configuration et tests | Disponibilité et intégrité |

Les mesures doivent correspondre au scénario. Il faut aussi envisager leurs limites, leur coût et la manière dont elles seront maintenues.

### 9.6. Étape 5 — Définir comment vérifier le résultat

Une protection ne doit pas être considérée comme efficace uniquement parce qu'elle a été installée.

Pour les autorisations, on peut réaliser des tests avec des comptes possédant des rôles différents.

Pour l'intégrité, on peut comparer les changements avec les demandes approuvées et examiner les journaux.

Pour la disponibilité, on peut suivre les délais de réponse et effectuer des tests de restauration.

La vérification doit être périodique et adaptée à la criticité de l'actif.

## 10. Les compromis entre les trois propriétés

### 10.1. La sécurité n'est pas uniquement une question de restriction

Il peut sembler logique de tout bloquer pour éviter les accès non autorisés. Pourtant, un système complètement inaccessible aux utilisateurs légitimes ne remplit pas son objectif.

À l'inverse, un service qui permet à tous les utilisateurs de tout consulter et de tout modifier peut être très facile à utiliser, mais présente des risques importants de confidentialité et d'intégrité.

Les professionnels doivent donc définir un équilibre adapté aux besoins.

### 10.2. Exemple : protéger une base de données

Une base de données contenant des informations sensibles peut être accessible uniquement depuis un réseau interne, avec des comptes limités et des communications chiffrées.

Ces mesures renforcent la confidentialité.

Cependant, si les droits sont trop restrictifs et empêchent l'application de fonctionner, la disponibilité de celle-ci peut être affectée.

La solution n'est pas de supprimer les protections, mais de tester la configuration, d'identifier les accès réellement nécessaires et de définir des mécanismes administratifs sécurisés.

### 10.3. Exemple : les mises à jour

Une mise à jour peut corriger une faille de sécurité et réduire la probabilité d'une compromission.

Pour une application critique, son installation peut nécessiter une préparation, des tests et une fenêtre de maintenance.

Retarder toutes les mises à jour peut augmenter le risque de sécurité. Installer une modification importante sans vérification peut aussi provoquer une panne.

Une démarche professionnelle évalue ces deux risques et prévoit un retour arrière quand cela est possible.

### 10.4. Exemple : le chiffrement et la gestion des clés

Le chiffrement renforce la confidentialité, mais les données doivent rester utilisables par les personnes et applications autorisées.

Si les clés sont perdues, certains fichiers peuvent devenir irrécupérables. Si les clés sont accessibles à des personnes non autorisées, la protection peut être affaiblie.

Une stratégie de chiffrement doit donc inclure la gestion des clés, les procédures de récupération et le contrôle des accès.

### 10.5. Comment décider ?

On peut suivre une méthode simple :

1. Identifier l'actif et les personnes qui en ont besoin.
2. Déterminer les conséquences d'une divulgation, d'une modification ou d'une interruption.
3. Choisir des protections proportionnées aux risques.
4. Vérifier que les utilisateurs légitimes peuvent toujours accomplir leur travail.
5. Tester les protections et prévoir les situations d'échec.
6. Réexaminer les choix lorsque le système ou les risques évoluent.

La bonne décision dépend du contexte et ne consiste pas toujours à maximiser une seule propriété.

## 11. Les erreurs fréquentes chez les débutants

### Erreur 1 — Confondre confidentialité et intégrité

Dire qu'un fichier est confidentiel parce qu'il est exact est incorrect. La confidentialité concerne les accès et les divulgations. L'intégrité concerne notamment la protection contre les modifications non autorisées.

### Erreur 2 — Penser qu'une sauvegarde règle tous les problèmes

Une sauvegarde peut contribuer à récupérer des données, mais elle ne bloque pas une fuite et ne garantit pas que le service sera immédiatement disponible.

### Erreur 3 — Croire que le chiffrement règle tout

Le chiffrement peut protéger des données, mais ne garantit pas l'absence de corruption, ne remplace pas l'autorisation et ne garantit pas la disponibilité du service.

### Erreur 4 — Croire que toute panne est une attaque

Un service peut devenir indisponible à cause d'une erreur humaine, d'un défaut logiciel ou d'une panne matérielle. Il faut enquêter avant de conclure.

### Erreur 5 — Considérer qu'un compte authentifié est autorisé à tout faire

L'authentification confirme une identité ou un compte selon un mécanisme donné. L'autorisation détermine les actions permises. Les deux sont distinctes.

### Erreur 6 — Penser qu'une empreinte prouve que le contenu est digne de confiance

Une empreinte permet une comparaison de contenu. Sans source de référence fiable, elle ne prouve ni l'auteur ni la légitimité du fichier.

### Erreur 7 — Protéger uniquement les serveurs

Les postes de travail, comptes, appareils mobiles, réseaux et procédures peuvent également provoquer des incidents. Une démarche CIA doit prendre en compte tout le chemin par lequel les informations sont créées, consultées, transmises et conservées.

### Erreur 8 — Installer une protection sans jamais la tester

Une sauvegarde peut être corrompue, une règle réseau peut être incorrecte, un journal peut ne pas enregistrer l'événement attendu. Les contrôles doivent être vérifiés régulièrement.

## 12. Étude de cas détaillée : l'incident d'une école numérique

### 12.1. Situation initiale

Une école utilise une plateforme numérique pour gérer les inscriptions, publier les cours et enregistrer les résultats.

La plateforme se compose d'une application Web, d'une base de données et d'un serveur de fichiers. Les enseignants disposent de comptes individuels, mais plusieurs procédures sont encore mal définies.

Un vendredi matin, plusieurs problèmes apparaissent :

- des étudiants affirment avoir vu les notes de leurs camarades ;
- une série de résultats a changé sans explication ;
- le service devient ensuite inaccessible pendant une partie de la journée.

La direction demande à l'équipe technique de déterminer les priorités de protection.

### 12.2. Première analyse : confidentialité

La consultation des résultats d'autres étudiants peut révéler un défaut de contrôle d'accès.

L'équipe doit examiner les rôles, les autorisations et les requêtes utilisées pour récupérer les résultats. Elle doit vérifier si un utilisateur connecté peut consulter des données qui ne lui appartiennent pas.

Il faut éviter de se limiter à modifier les identifiants affichés dans l'interface. La vérification d'autorisation doit être effectuée côté serveur pour chaque ressource protégée.

L'équipe doit également déterminer quelles informations ont été consultées et si une notification ou une action supplémentaire est nécessaire selon les règles applicables.

### 12.3. Deuxième analyse : intégrité

Les notes ayant changé, l'équipe doit établir si les modifications étaient autorisées ou non.

Elle peut examiner les journaux disponibles, les sauvegardes, les traces de connexion et l'historique de modification de la base de données.

Les questions importantes sont les suivantes :

- quelles valeurs étaient présentes avant l'incident ?
- quelles valeurs sont présentes maintenant ?
- quel compte a réalisé la modification ?
- à quel moment l'action a-t-elle eu lieu ?
- existait-il une demande d'autorisation ?
- les journaux sont-ils fiables et suffisamment détaillés ?

Si les traces sont insuffisantes, il peut être impossible de reconstituer précisément toutes les actions. Cette situation indique la nécessité d'améliorer l'audit et les contrôles de modification.

### 12.4. Troisième analyse : disponibilité

L'équipe doit ensuite établir pourquoi la plateforme ne répond plus.

Elle vérifie l'état du serveur, les ressources disponibles, les journaux de l'application, la connectivité réseau et le fonctionnement de la base de données.

Une panne de disponibilité peut être la conséquence du même incident ou un événement indépendant. Il ne faut pas supposer automatiquement qu'une personne a provoqué les trois problèmes.

### 12.5. Mesures correctives

Une stratégie possible comprend :

**Pour la confidentialité :** corriger les contrôles d'accès, supprimer les permissions excessives, protéger les sessions et tester les rôles de chaque catégorie d'utilisateur.

**Pour l'intégrité :** contrôler les modifications de notes, restaurer les valeurs confirmées comme correctes, journaliser les opérations sensibles et limiter les droits d'écriture.

**Pour la disponibilité :** identifier la cause réelle de la panne, restaurer le service selon une procédure maîtrisée, vérifier les sauvegardes et définir des alertes adaptées.

**Pour l'ensemble du système :** préserver les éléments utiles à l'enquête, documenter les actions, coordonner les communications et vérifier les corrections avant le retour à un fonctionnement normal.

### 12.6. Leçons à retenir

Un incident complexe peut toucher plusieurs propriétés de la triade.

La confidentialité aide à déterminer quelles informations ne doivent pas être divulguées. L'intégrité permet de raisonner sur les modifications et la fiabilité des données. La disponibilité permet de réfléchir à la continuité du service et à sa reprise.

L'analyse CIA ne remplace pas une enquête technique complète, mais fournit une structure claire pour organiser les priorités.

## 13. TP guidé : réaliser un mini-audit CIA

### 13.1. Objectif du TP

Tu vas appliquer la triade CIA à un système fictif et produire un petit rapport de sécurité.

Le travail peut être réalisé sur papier, dans un fichier texte ou dans un tableau. Il ne nécessite pas d'outils payants.

### 13.2. Le système à analyser

Un centre de formation utilise :

- une application de gestion des apprenants ;
- une base de données contenant les comptes et les résultats ;
- un serveur de fichiers contenant les supports de cours ;
- un réseau Wi-Fi utilisé par le personnel et les apprenants ;
- une connexion Internet pour accéder à la plateforme.

Voici les faits connus :

- les enseignants utilisent des comptes individuels ;
- plusieurs utilisateurs partagent encore un compte d'administration ;
- les sauvegardes de la base sont effectuées chaque nuit ;
- aucune restauration n'a été testée récemment ;
- le Wi-Fi des apprenants et celui du personnel ne sont pas séparés ;
- les modifications de résultats ne sont pas systématiquement journalisées.

### 13.3. Étape A — Identifier les actifs critiques

Écris une liste des actifs qui doivent être protégés.

Pour chaque actif, précise les données ou les services qu'il contient et les personnes qui doivent y accéder.

Exemple : la base de données des résultats contient des notes, des identifiants et des informations sur les apprenants. Les enseignants autorisés doivent pouvoir consulter les résultats de leurs classes et les modifier dans les limites de leurs responsabilités.

### 13.4. Étape B — Identifier les faiblesses

À partir des faits, repère au moins quatre faiblesses.

Tu peux notamment examiner :

- les comptes partagés ;
- la séparation des réseaux ;
- l'absence de tests de restauration ;
- l'absence de journaux de modification.

Explique pour chacune les conséquences plausibles. Ne conclus pas automatiquement qu'une attaque a déjà eu lieu : une faiblesse crée un risque, mais ne prouve pas qu'elle a été exploitée.

### 13.5. Étape C — Associer chaque faiblesse à la triade

Utilise le tableau suivant :

| Faiblesse | Propriété CIA concernée | Conséquence possible | Première mesure |
|---|---|---|---|
| Compte d'administration partagé | À déterminer | À déterminer | À déterminer |
| Réseau du personnel non séparé du Wi-Fi des apprenants | À déterminer | À déterminer | À déterminer |
| Sauvegardes sans test de restauration | À déterminer | À déterminer | À déterminer |
| Modifications de notes non journalisées | À déterminer | À déterminer | À déterminer |

Une même faiblesse peut affecter plusieurs propriétés. Indique la propriété principalement concernée et, si nécessaire, les propriétés secondaires.

### 13.6. Étape D — Définir les priorités

Toutes les mesures ne peuvent pas nécessairement être réalisées le même jour. Il faut déterminer ce qui doit être traité en premier en fonction de la gravité et de la vraisemblance des conséquences.

Une première approche consiste à réduire les risques qui permettent un accès administratif partagé, à protéger les données de résultats et à vérifier rapidement la capacité de restauration.

Il faut ensuite planifier une segmentation réseau appropriée, renforcer la journalisation et poursuivre l'analyse des autres composants.

Cette priorisation doit rester une proposition initiale. Une véritable décision nécessite de connaître la valeur des actifs, les contraintes opérationnelles et les risques propres à l'organisation.

### 13.7. Étape E — Définir les tests

Pour chaque protection, prévois une vérification.

Pour les comptes individuels, vérifie qu'une action réalisée par un utilisateur est associée à son identité.

Pour les permissions, utilise des comptes de test disposant de rôles différents et vérifie qu'ils ne peuvent effectuer que les actions prévues.

Pour les sauvegardes, effectue une restauration dans un environnement de test et contrôle le résultat.

Pour la journalisation, réalise une modification contrôlée puis vérifie que l'événement est correctement enregistré.

Un audit ne se limite pas à une liste de recommandations. Il doit préciser comment vérifier que les mesures fonctionnent.

## 14. Exercices d'application avec corrections

Essaie de répondre aux questions avant de consulter les corrigés.

### Exercice 1 — Identifier la propriété

Pour chaque situation, identifie la propriété CIA principalement affectée.

A. Un employé envoie par erreur un dossier confidentiel à une personne externe non autorisée.

B. Une personne modifie une facture sans autorisation.

C. Une panne électrique arrête un serveur et empêche l'accès à une application.

D. Un fichier important est supprimé accidentellement et aucune sauvegarde exploitable n'existe.

E. Une personne non autorisée consulte des données de santé dans une application.

**Correction**

A. Confidentialité, car des informations sont divulguées à un destinataire qui n'est pas autorisé.

B. Intégrité, car la facture a été modifiée sans autorisation. La confidentialité ou la disponibilité peuvent aussi être concernées selon les conséquences, mais elles ne sont pas établies par l'énoncé.

C. Disponibilité, car le service ne peut plus être utilisé.

D. Intégrité et disponibilité des données sont toutes deux concernées. La suppression constitue une atteinte à l'état attendu des données, et leur absence empêche de les utiliser. L'impossibilité de les restaurer augmente la gravité de l'incident.

E. Confidentialité, car les données sont consultées par une personne non autorisée.

### Exercice 2 — Choisir une mesure

Une entreprise souhaite empêcher les employés de consulter les dossiers de clients qui ne relèvent pas de leurs responsabilités. Quelle mesure est la plus directement adaptée ?

A. Ajouter de la mémoire vive au serveur.

B. Mettre en place un contrôle d'accès fondé sur les rôles et les responsabilités.

C. Acheter un deuxième disque dur.

D. Accélérer la connexion Internet.

**Correction : B.**

Le contrôle d'accès doit vérifier les autorisations de chaque utilisateur avant de permettre l'accès au dossier. Les autres mesures peuvent être utiles à d'autres objectifs, mais elles ne résolvent pas directement le problème de confidentialité.

### Exercice 3 — Comprendre une empreinte

Tu calcules l'empreinte SHA-256 d'un fichier. Tu modifies ensuite une phrase dans le fichier et calcules une nouvelle empreinte. Les deux valeurs sont différentes.

Que peux-tu conclure ?

A. Le fichier est désormais chiffré.

B. Le fichier est inaccessible aux personnes non autorisées.

C. Le contenu du fichier a changé entre les deux calculs.

D. Le fichier a été modifié par un pirate.

**Correction : C.**

Le changement d'empreinte indique que le contenu traité a changé, avec une très forte probabilité dans le fonctionnement attendu d'une fonction cryptographique comme SHA-256. Il ne permet pas d'identifier l'auteur de la modification ni de prouver qu'il s'agissait d'un pirate.

### Exercice 4 — Sauvegardes

Une organisation effectue quotidiennement des sauvegardes, mais n'a jamais testé leur restauration. Quel est le principal problème ?

A. La confidentialité est automatiquement compromise.

B. Il est impossible de garantir que les sauvegardes pourront restaurer les données dans les conditions nécessaires.

C. Les données ne peuvent jamais être modifiées.

D. Le serveur devient automatiquement plus lent.

**Correction : B.**

Une sauvegarde non testée peut être incomplète, corrompue ou difficile à restaurer. Les tests permettent de vérifier que les données et les procédures de récupération répondent aux besoins définis.

### Exercice 5 — Incident combiné

Un attaquant obtient un compte administrateur, télécharge une base de données, modifie plusieurs enregistrements et supprime ensuite des fichiers nécessaires au service.

Quelles propriétés sont probablement compromises ?

**Correction**

Les trois propriétés sont concernées :

- Confidentialité : l'attaquant a téléchargé des données auxquelles il ne devait pas accéder.
- Intégrité : il a modifié des enregistrements sans autorisation.
- Disponibilité : la suppression de fichiers peut empêcher le service de fonctionner.

Il faudra confirmer les conséquences exactes lors de l'investigation, mais ce scénario indique un risque sérieux pour l'ensemble de la triade.

### Exercice 6 — Authentification ou autorisation ?

Un utilisateur se connecte correctement à une application avec son mot de passe et un second facteur. Il essaie ensuite de modifier le dossier d'un autre utilisateur, alors que son rôle ne le permet pas.

Quelle mesure doit bloquer l'action ?

**Correction**

Le contrôle d'autorisation doit bloquer la modification. L'authentification a confirmé l'identité ou le compte selon la méthode utilisée, mais cela ne donne pas automatiquement le droit d'agir sur toutes les ressources.

La vérification doit se faire côté serveur pour empêcher un utilisateur de contourner la restriction en modifiant simplement une requête dans son navigateur.

### Exercice 7 — Classer des contrôles

Associe chaque contrôle à la propriété qu'il contribue principalement à protéger. Plusieurs associations peuvent être correctes.

1. Chiffrement d'un ordinateur portable.
2. Sauvegarde testée.
3. Contrôle d'accès aux dossiers.
4. Journal d'audit des modifications.
5. Redondance d'un lien réseau.
6. Signature numérique d'un fichier.

**Correction indicative**

1. Le chiffrement contribue principalement à la confidentialité des données stockées.
2. La sauvegarde testée soutient la récupération, donc l'intégrité et la disponibilité.
3. Le contrôle d'accès contribue à la confidentialité et peut aussi soutenir l'intégrité.
4. Le journal d'audit aide à détecter et reconstituer les modifications, soutenant l'intégrité et la traçabilité.
5. La redondance d'un lien contribue à la disponibilité.
6. La signature numérique contribue à vérifier l'intégrité et l'origine cryptographique du fichier, sous réserve d'une gestion fiable des clés et de leur confiance.

L'objectif n'est pas de mémoriser une seule association par outil. Il faut comprendre ce que le contrôle fait réellement et quelles sont ses limites.

### Exercice 8 — Analyse d'un incident

Un employé signale qu'un document partagé a été modifié et qu'il n'arrive plus à accéder à une application métier. Aucune preuve de fuite de données n'est disponible.

Rédige une courte analyse en distinguant les faits connus, les hypothèses et les propriétés CIA concernées.

**Correction possible**

**Faits connus :** un document partagé semble avoir été modifié et une application métier est inaccessible pour l'employé.

**Hypothèses :** la modification peut être accidentelle ou non autorisée. L'indisponibilité peut provenir d'une panne de l'application, d'un problème réseau ou d'un incident lié à l'environnement.

**Propriétés concernées :** l'intégrité doit être examinée pour le document et la disponibilité doit être étudiée pour l'application. Aucune compromission de confidentialité n'est démontrée par les informations initiales, mais elle peut être évaluée au cours de l'investigation.

**Actions :** préserver les éléments disponibles, consulter les journaux, vérifier l'état du service, déterminer l'historique du document et éviter toute conclusion non étayée.

## 15. Défi final — Sécuriser une petite entreprise

### 15.1. Le scénario

Tu viens d'être recruté comme assistant en sécurité informatique dans une entreprise de distribution appelée **KivuTech Services**.

L'entreprise utilise un site de commerce en ligne et un réseau interne. Les employés accèdent à un serveur de fichiers. Une base de données contient les informations des clients, les commandes et les prix. Le système doit être accessible pendant les heures de travail et les clients peuvent effectuer des commandes en ligne.

L'entreprise rencontre les problèmes suivants :

1. Tous les employés partagent un même compte pour accéder au serveur de fichiers.
2. Les factures peuvent être modifiées sans qu'un journal permette d'identifier précisément l'auteur.
3. La sauvegarde des données est effectuée sur un disque qui reste connecté en permanence au serveur.
4. Aucun test de restauration n'a été réalisé depuis plusieurs mois.
5. Le site Internet devient parfois indisponible pendant les périodes de forte activité.
6. Des documents contenant des informations clients sont parfois envoyés par courriel sans vérification du destinataire.

La direction te demande de produire une proposition initiale de sécurité.

### 15.2. Travail à réaliser

Prépare une réponse structurée en six parties :

1. Identifie les principaux actifs.
2. Relie chaque problème à une ou plusieurs propriétés CIA.
3. Classe les problèmes selon leur priorité initiale.
4. Propose au moins une mesure adaptée pour chaque problème.
5. Indique comment vérifier l'efficacité des mesures.
6. Présente les limites de ta proposition et les informations supplémentaires à collecter.

Tu n'as pas besoin de choisir un produit commercial. Le but est de prouver que tu sais relier un risque à un objectif et à un contrôle adapté.

### 15.3. Correction détaillée du défi

**Partie 1 — Identifier les actifs**

Les principaux actifs sont les données clients, les factures, les commandes, les prix des produits, le serveur de fichiers, la base de données, le site Web et les mécanismes de sauvegarde.

Les comptes des employés, les configurations et les journaux sont également importants parce qu'ils contribuent à protéger ou à maintenir les actifs précédents.

**Partie 2 — Associer les problèmes à la triade**

| Problème | Propriété principale | Autres propriétés possibles |
|---|---|---|
| Compte partagé | Confidentialité et intégrité | Traçabilité insuffisante |
| Factures modifiables sans journal fiable | Intégrité | Confidentialité selon les accès |
| Sauvegarde connectée en permanence | Disponibilité et intégrité en cas d'incident destructeur | Confidentialité si la sauvegarde est mal protégée |
| Restauration jamais testée | Disponibilité et intégrité lors de la récupération | Sans effet direct automatique sur la confidentialité |
| Indisponibilité du site en période de forte activité | Disponibilité | Intégrité si les commandes sont perdues ou corrompues |
| Envoi de documents au mauvais destinataire | Confidentialité | Les autres propriétés ne sont pas nécessairement touchées |

Cette analyse montre qu'un problème peut concerner plusieurs propriétés et que les conséquences secondaires doivent être examinées plutôt que supposées.

**Partie 3 — Définir les priorités initiales**

La première priorité est de réduire les accès partagés et de mieux contrôler les modifications de factures, car ces faiblesses nuisent à la maîtrise des accès et à la capacité de comprendre les actions réalisées.

La deuxième priorité est de vérifier rapidement les sauvegardes et leur capacité de restauration. Le fait qu'elles restent connectées en permanence au serveur peut les exposer à certains incidents qui touchent le système principal.

La troisième priorité consiste à analyser les causes de l'indisponibilité du site en mesurant les ressources, les erreurs et le comportement de l'application durant les périodes concernées.

Enfin, l'entreprise doit améliorer les procédures d'envoi de documents contenant des données clients et sensibiliser les employés aux risques de divulgation.

Cet ordre est une proposition initiale. Si le site est actuellement indisponible ou si une fuite active est suspectée, la priorité opérationnelle peut changer.

**Partie 4 — Mesures à proposer**

Pour les comptes partagés, crée des comptes individuels et attribue des permissions selon les responsabilités. Réserve les droits administratifs aux personnes qui en ont réellement besoin. Protège les accès sensibles par une authentification adaptée.

Pour les factures, applique un contrôle d'autorisation sur les modifications et enregistre les événements importants : compte utilisé, date, ressource modifiée et résultat de l'action. Prévois une procédure d'approbation ou de correction pour les changements sensibles.

Pour les sauvegardes, établis une stratégie tenant compte des objectifs de reprise. Protège les sauvegardes contre la suppression et l'altération, par exemple avec des copies isolées ou des mécanismes de stockage immuable adaptés à l'environnement. Limite les comptes capables de supprimer les copies de sauvegarde.

Pour la restauration, réalise un test planifié dans un environnement de test. Vérifie que les données peuvent être relues, que les relations entre les enregistrements restent cohérentes et que l'application peut retrouver un fonctionnement normal. Note les résultats et les problèmes rencontrés.

Pour le site Web, collecte les métriques de charge, les temps de réponse, les erreurs et l'état des dépendances. Une fois la cause connue, il peut être pertinent d'améliorer la capacité, d'optimiser les requêtes, de configurer une mise en cache ou d'utiliser un mécanisme de répartition de charge.

Pour les courriels contenant des données clients, définis une procédure de vérification du destinataire, limite les pièces jointes aux informations nécessaires et privilégie des moyens de partage contrôlés pour les documents sensibles. Sensibilise les employés à la vérification des adresses et à l'utilisation correcte des autorisations.

**Partie 5 — Vérifier l'efficacité**

Les comptes individuels peuvent être vérifiés en examinant les comptes actifs, leurs permissions et les traces d'accès.

L'intégrité des factures peut être contrôlée à l'aide d'un test de modification autorisée et non autorisée, complété par une vérification des journaux.

Les sauvegardes doivent être testées par une restauration réelle. Il faut mesurer le temps nécessaire et comparer les données restaurées avec les résultats attendus.

La disponibilité du site doit être mesurée à l'aide de tests de réponse, de métriques de ressources et d'observations pendant les périodes de forte utilisation.

Les procédures de partage peuvent être évaluées à l'aide d'exemples contrôlés et d'une vérification des pratiques des équipes, sans exposer de vraies données clients.

**Partie 6 — Limites et informations complémentaires**

La proposition ne peut pas être considérée comme un audit complet. Il faudrait notamment connaître le volume et la sensibilité des données, les obligations applicables, l'architecture exacte, les résultats de supervision, le fonctionnement du stockage et les objectifs de reprise demandés par la direction.

Il faudrait aussi savoir si les indisponibilités actuelles sont liées à une saturation, à des défauts applicatifs ou à une autre cause.

Les protections devront être définies et testées avec les équipes responsables. Toute modification de production devra tenir compte de la continuité du service.

### 15.4. Critères d'évaluation du défi

Tu peux t'autoévaluer sur 20 points :

| Critère | Points |
|---|---:|
| Identification des actifs importants | 3 |
| Analyse correcte des propriétés CIA | 5 |
| Choix de mesures adaptées aux problèmes | 5 |
| Définition de moyens de vérification | 4 |
| Prise en compte des limites et des priorités | 3 |
| **Total** | **20** |

Une réponse de qualité ne doit pas simplement citer des outils. Elle doit expliquer pourquoi chaque mesure contribue à résoudre le problème identifié, comment son efficacité peut être vérifiée et quelles limites subsistent.

## 16. Synthèse du cours

La triade CIA est un modèle fondamental de la cybersécurité. Elle fournit une manière simple d'organiser les objectifs de protection d'un système.

La **confidentialité** limite l'accès et la divulgation des informations aux personnes ou processus autorisés. Elle repose notamment sur le contrôle d'accès, le moindre privilège, la protection des identités, le chiffrement et la sensibilisation.

L'**intégrité** contribue à préserver l'exactitude, la complétude et l'état autorisé des données et des systèmes. Elle s'appuie notamment sur les permissions, les validations, les journaux d'audit, les fonctions de hachage, les signatures numériques et les sauvegardes fiables.

La **disponibilité** vise à permettre aux utilisateurs autorisés d'accéder aux informations et aux services dans les délais nécessaires. Elle dépend notamment de la supervision, de la redondance, de la maintenance, des sauvegardes et des procédures de reprise.

Ces propriétés se complètent. Une même situation peut en affecter plusieurs, mais ce n'est pas toujours le cas. L'analyse doit donc se fonder sur les faits, les conséquences et les besoins de l'organisation.

Pour chaque problème de sécurité, adopte ce raisonnement :

1. Quel actif faut-il protéger ?
2. Quelle menace ou faiblesse pourrait affecter cet actif ?
3. Quelle propriété CIA est principalement menacée ?
4. Quelle mesure permet de réduire le risque ?
5. Comment vérifier que cette mesure fonctionne ?
6. Que se passe-t-il si la mesure échoue ?

Ce raisonnement constitue une base pour les cours suivants : panorama des menaces, cryptographie, hachage et signatures, authentification, sécurité des terminaux, sécurité Wi-Fi et introduction aux pare-feu.

## 17. Glossaire des notions essentielles

**Actif :** donnée, système, service ou ressource ayant de la valeur et nécessitant une protection.

**Authentification :** mécanisme permettant de vérifier une identité ou un autre attribut présenté par un utilisateur, un appareil ou un service.

**Autorisation :** décision déterminant quelles ressources et quelles opérations sont permises à une identité donnée.

**Sauvegarde :** copie de données conservée pour permettre leur récupération à la suite d'une suppression, d'une corruption ou d'un incident.

**Confidentialité :** protection contre l'accès ou la divulgation aux personnes et processus non autorisés.

**Disponibilité :** capacité d'un système ou d'une information à être accessible et utilisable lorsque cela est nécessaire.

**Empreinte cryptographique :** valeur calculée à partir de données au moyen d'une fonction de hachage, utile notamment pour comparer des contenus.

**Intégrité :** protection contre les modifications ou destructions non autorisées et préservation de l'exactitude et de la complétude des informations.

**Journalisation :** enregistrement d'événements relatifs au fonctionnement ou à la sécurité d'un système.

**MFA :** authentification multifacteur, qui combine plusieurs facteurs de vérification.

**Moindre privilège :** principe selon lequel chaque identité ou composant ne reçoit que les droits nécessaires à son rôle.

**Menace :** cause potentielle d'un incident susceptible d'avoir des conséquences négatives.

**Risque :** possibilité qu'un événement produise des conséquences négatives sur un actif ou une activité.

**RTO :** délai cible de rétablissement d'un service après une interruption.

**RPO :** point de reprise cible qui exprime la perte de données temporelle maximale acceptable dans un scénario défini.

**Vulnérabilité :** faiblesse pouvant être exploitée ou provoquer un incident.

**Chiffrement :** transformation cryptographique des données visant à protéger leur contenu contre la lecture par les personnes non autorisées.

**Signature numérique :** mécanisme cryptographique permettant de vérifier une signature produite avec une clé privée et de contrôler que le contenu vérifié correspond au contenu signé.

**Déni de service :** situation dans laquelle un service ne peut plus répondre correctement aux demandes légitimes, souvent à cause de l'épuisement ou de la perturbation de ses ressources.

**Résilience :** capacité d'un système ou d'une organisation à maintenir ou rétablir ses fonctions essentielles face à un incident.

## 18. Ressources pour approfondir

Les ressources suivantes permettent de prolonger l'apprentissage avec des références institutionnelles et techniques.

- NIST, *Data Integrity: Detecting and Responding to Ransomware and Other Destructive Events* : https://www.nccoe.nist.gov/publication/1800-26/VolA/index.html
- NIST Computer Security Resource Center, glossaire de la sécurité : https://csrc.nist.gov/glossary/term/security
- OWASP Developer Guide, principes fondamentaux de sécurité et triade CIA : https://devguide.owasp.org/en/02-foundations/01-security-fundamentals/

Lors de tes lectures, essaie toujours de relier les définitions aux situations étudiées. Le but n'est pas seulement de réciter les trois lettres CIA, mais de savoir analyser un incident, identifier les propriétés concernées, proposer des mesures proportionnées et vérifier leurs résultats.

**Fin du cours : La Triade CIA.**
