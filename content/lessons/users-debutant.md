# Utilisateurs et groupes Linux — Niveau débutant
## Comprendre les comptes, gérer les identités et contrôler les accès


# Sommaire

1. [Introduction à la gestion des utilisateurs](#1-introduction-à-la-gestion-des-utilisateurs)
2. [Comprendre les utilisateurs Linux](#2-comprendre-les-utilisateurs-linux)
3. [Les identifiants UID et GID](#3-les-identifiants-uid-et-gid)
4. [Les fichiers système des utilisateurs et des groupes](#4-les-fichiers-système-des-utilisateurs-et-des-groupes)
5. [Afficher et rechercher les comptes](#5-afficher-et-rechercher-les-comptes)
6. [Créer un utilisateur](#6-créer-un-utilisateur)
7. [Gérer les mots de passe](#7-gérer-les-mots-de-passe)
8. [Comprendre les groupes Linux](#8-comprendre-les-groupes-linux)
9. [Ajouter et retirer un utilisateur d'un groupe](#9-ajouter-et-retirer-un-utilisateur-dun-groupe)
10. [Modifier un compte utilisateur](#10-modifier-un-compte-utilisateur)
11. [Gérer les répertoires personnels](#11-gérer-les-répertoires-personnels)
12. [Supprimer ou désactiver un compte](#12-supprimer-ou-désactiver-un-compte)
13. [Permissions et relations entre utilisateurs et groupes](#13-permissions-et-relations-entre-utilisateurs-et-groupes)
14. [Le compte root et les privilèges sudo](#14-le-compte-root-et-les-privilèges-sudo)
15. [Les comptes système et les comptes de service](#15-les-comptes-système-et-les-comptes-de-service)
16. [Expiration, verrouillage et sécurité des comptes](#16-expiration-verrouillage-et-sécurité-des-comptes)
17. [Diagnostic des problèmes courants](#17-diagnostic-des-problèmes-courants)
18. [Laboratoires pratiques guidés](#18-laboratoires-pratiques-guidés)
19. [Exercices d'entraînement](#19-exercices-dentraînement)
20. [Défi final : administrer les utilisateurs d'une entreprise](#20-défi-final--administrer-les-utilisateurs-dune-entreprise)
21. [Correction détaillée du défi final](#21-correction-détaillée-du-défi-final)
22. [Checklist d'administration](#22-checklist-dadministration)
23. [Fiche de révision et commandes essentielles](#23-fiche-de-révision-et-commandes-essentielles)
24. [Conclusion](#24-conclusion)


# 1. Introduction à la gestion des utilisateurs

## 1.1. Pourquoi Linux possède-t-il des utilisateurs ?

Linux est un système d'exploitation conçu pour permettre à plusieurs utilisateurs et processus de travailler sur une même machine.

Un serveur peut, par exemple, héberger plusieurs développeurs, une application web, une base de données, un service de sauvegarde et des tâches planifiées.

Tous ces acteurs ne doivent pas disposer des mêmes droits.

Un développeur peut avoir besoin de modifier les fichiers d'un projet sans pouvoir changer la configuration réseau du serveur.

Un administrateur peut devoir installer un logiciel, gérer les comptes et modifier la configuration système.

Un service web doit pouvoir lire certains fichiers et écrire dans certains répertoires, mais il ne devrait généralement pas disposer d'un accès administratif complet.

Linux utilise des mécanismes d'identité et de permissions pour distinguer ces acteurs.

```text
                   SYSTÈME LINUX
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       Alice            Bob         Service web
       Utilisatrice     Utilisateur   Processus
          |              |              |
          v              v              v
       Fichiers       Fichiers       Fichiers
       autorisés      autorisés      autorisés
          |              |              |
          +--------------+--------------+
                         |
                         v
                  Contrôle d'accès
```

Le principe essentiel est le suivant :

**Chaque utilisateur et chaque processus doivent disposer uniquement des droits nécessaires à leur fonction.**

Cette règle contribue à limiter les erreurs, les accès non autorisés et les conséquences d'une compromission.

## 1.2. Qu'est-ce qu'un utilisateur Linux ?

Un utilisateur Linux est une identité reconnue par le système.

Cette identité possède notamment :

- Un nom de compte.
- Un identifiant numérique appelé UID.
- Un groupe principal.
- Éventuellement plusieurs groupes supplémentaires.
- Des informations de compte.
- Un répertoire personnel, lorsque cela est prévu.
- Un interpréteur de commandes ou shell de connexion, selon le compte.

Exemple fictif :

```text
Nom du compte : alice
UID           : 1001
Groupe principal : developpeurs
Répertoire personnel : /home/alice
Shell         : /bin/bash
```

Ces informations décrivent l'identité du compte. Elles ne signifient pas qu'Alice possède automatiquement tous les droits dans son répertoire personnel ou ailleurs.

Les droits effectifs dépendent également des permissions, des ACL, des privilèges attribués et d'autres contrôles de sécurité.

## 1.3. Qu'est-ce qu'un groupe Linux ?

Un groupe est un ensemble d'utilisateurs qui partagent une identité de groupe.

Les groupes simplifient l'attribution de droits à plusieurs personnes.

Imaginons une équipe de développement composée de trois personnes :

```text
Groupe : developpeurs
|
+-- alice
+-- bob
+-- claire
```

Plutôt que d'accorder des droits séparément à chaque utilisateur, on peut attribuer les droits appropriés au groupe `developpeurs`.

Les membres de ce groupe peuvent alors bénéficier de ces droits, sous réserve des règles de permissions et des autres restrictions appliquées.

## 1.4. Pourquoi ne pas travailler constamment en root ?

Le compte `root` est le compte administrateur historique de Linux.

Il possède généralement des privilèges très étendus sur le système.

Une erreur commise avec ce compte peut avoir des conséquences importantes :

- Suppression de fichiers système.
- Modification incorrecte des permissions.
- Interruption de services.
- Altération de la configuration.
- Accès à des données confidentielles.
- Modification du stockage.

Il est préférable de travailler avec un compte ordinaire et d'utiliser des privilèges élevés seulement pour les opérations qui le nécessitent.

Exemple :

```bash
# Opération ordinaire : consulter un fichier accessible
cat notes.txt

# Opération administrative : consulter un fichier protégé
sudo cat /etc/shadow
```

La seconde commande nécessite normalement des privilèges appropriés. Sur de nombreux systèmes, un utilisateur ordinaire n'est pas autorisé à lire directement `/etc/shadow`.

## 1.5. Objectifs du cours

À la fin de ce cours, tu dois pouvoir :

- Expliquer la différence entre un utilisateur et un groupe.
- Comprendre les UID et les GID.
- Lire les informations de compte.
- Identifier les fichiers système liés aux utilisateurs.
- Créer un utilisateur.
- Définir et modifier son mot de passe.
- Créer un groupe.
- Ajouter un utilisateur à un groupe.
- Modifier les informations d'un compte.
- Comprendre le fonctionnement d'un répertoire personnel.
- Désactiver ou supprimer un compte de manière prudente.
- Comprendre comment les groupes influencent les permissions.
- Identifier le rôle du compte root et de `sudo`.
- Reconnaître les comptes système et les comptes de service.


# 2. Comprendre les utilisateurs Linux

## 2.1. Les deux grandes catégories d'utilisateurs

On distingue généralement deux grandes catégories de comptes.

### Les comptes humains

Ces comptes sont destinés aux personnes qui utilisent le système.

Exemples :

```text
alice
bob
claire
adminlocal
```

Ils servent notamment à :

- Se connecter à un terminal.
- Exécuter des programmes.
- Lire et modifier des fichiers.
- Administrer des services, si des droits leur sont accordés.
- Participer à des projets partagés.

Un compte humain possède souvent un répertoire personnel et un shell de connexion interactif.

Mais ces caractéristiques ne suffisent pas, à elles seules, à prouver qu'un compte appartient à une personne.

### Les comptes système

Certains comptes sont utilisés par les composants du système ou par les applications.

Exemples fréquents selon la distribution :

```text
root
daemon
nobody
www-data
```

Un service peut utiliser une identité distincte afin de limiter les dommages éventuels en cas d'erreur ou de compromission.

Le nom exact des comptes système varie selon les distributions et les logiciels installés.

## 2.2. Exemple : un serveur web

Supposons qu'un serveur héberge une application web.

```text
                    SERVEUR LINUX
                         |
             +-----------+-----------+
             |                       |
             v                       v
          alice                   www-data
       Utilisatrice              Compte de service
             |                       |
             v                       v
     Administration du         Exécution du service
     projet autorisée          web selon ses droits
             |                       |
             v                       v
     Fichiers du projet        Fichiers web autorisés
```

Alice peut avoir le droit de modifier le code source.

Le service web peut avoir le droit de lire le code et d'écrire dans un répertoire réservé aux données temporaires ou aux fichiers importés.

En revanche, il ne devrait pas nécessairement pouvoir modifier tous les fichiers du projet.

La séparation des comptes permet de limiter les privilèges de chaque acteur.

## 2.3. Un nom de compte n'est pas son identité numérique

Linux utilise des identifiants numériques pour les utilisateurs et les groupes.

Un nom comme `alice` est une représentation lisible par les humains.

Le système utilise un UID pour identifier le compte dans de nombreux contextes.

De même, le nom d'un groupe est associé à un GID.

Ces identifiants sont importants pour les permissions des fichiers.

Exemple :

```text
Nom d'utilisateur : alice
UID               : 1001

Nom du groupe     : developpeurs
GID               : 1005
```

Un fichier peut alors être associé à :

```text
Propriétaire : UID 1001
Groupe       : GID 1005
```

Les outils d'affichage traduisent souvent ces identifiants en noms lisibles.

## 2.4. Que se passe-t-il si un utilisateur est supprimé ?

Supposons qu'un utilisateur possédant l'UID `1001` crée plusieurs fichiers.

```text
Utilisateur alice
UID 1001
    |
    v
Fichiers appartenant à UID 1001
    |
    +-- rapport.txt
    +-- projet.py
    +-- archive.tar
```

Si le compte est ensuite supprimé, les fichiers ne sont pas nécessairement supprimés en même temps.

Ils peuvent conserver l'UID numérique du propriétaire.

Les outils peuvent alors afficher un numéro à la place du nom :

```text
1001 1001 rapport.txt
```

Le fichier n'est pas devenu anonyme au niveau des métadonnées : ses identifiants numériques sont toujours présents.

C'est une des raisons pour lesquelles la suppression d'un compte nécessite une préparation.

## 2.5. Les informations d'un compte

Pour un utilisateur classique, les informations importantes comprennent :

| Information | Exemple | Fonction |
|---|---|---|
| Nom de connexion | `alice` | Nom utilisé pour identifier le compte |
| UID | `1001` | Identifiant numérique de l'utilisateur |
| GID principal | `1005` | Identifiant du groupe principal |
| Répertoire personnel | `/home/alice` | Emplacement personnel associé au compte |
| Shell | `/bin/bash` | Interpréteur de commandes de connexion |
| Mot de passe | Géré selon la configuration | Authentification |
| Groupes supplémentaires | `projets`, `sudo` | Accès complémentaires |

Un compte peut exister sans répertoire personnel, et le shell peut être configuré pour empêcher une connexion interactive.

La configuration dépend du rôle du compte.


# 3. Les identifiants UID et GID

## 3.1. Qu'est-ce qu'un UID ?

UID signifie *User Identifier*.

C'est l'identifiant numérique associé à un utilisateur.

Exemple :

```text
alice:x:1001:1005:Alice Martin:/home/alice:/bin/bash
```

Dans cette représentation :

```text
1001 = UID d'alice
1005 = GID de son groupe principal
```

Le système de fichiers conserve généralement des identifiants numériques pour le propriétaire et le groupe des fichiers.

Lorsqu'une commande affiche `alice`, elle peut simplement traduire le numéro `1001` à partir des informations de comptes disponibles.

## 3.2. Qu'est-ce qu'un GID ?

GID signifie *Group Identifier*.

Il s'agit de l'identifiant numérique d'un groupe.

Exemple :

```text
developpeurs:x:1005:alice,bob,claire
```

Dans cet exemple, le GID de `developpeurs` est `1005`.

Le groupe peut servir à autoriser un ensemble d'utilisateurs à accéder aux mêmes fichiers.

## 3.3. UID 0 : le compte root

Dans une installation Linux classique, l'UID `0` est associé au compte superutilisateur.

Exemple :

```text
root:x:0:0:root:/root:/bin/bash
```

Le compte `root` possède l'UID `0` et le GID principal `0` dans cette configuration courante.

Il est important de comprendre que les privilèges élevés sont principalement associés à l'identité numérique et aux mécanismes de sécurité du système, pas seulement au texte `root`.

Un nom de compte différent qui recevrait l'UID `0` pourrait également bénéficier de privilèges très étendus. Une telle configuration ne doit pas être créée de manière improvisée.

## 3.4. Les plages d'UID

Les distributions réservent habituellement certaines plages pour les comptes système et d'autres pour les comptes ordinaires.

Exemple conceptuel :

```text
UID 0
 |
 +-- root

UID bas
 |
 +-- comptes système et services

UID plus élevés
 |
 +-- comptes humains
```

Il ne faut toutefois pas considérer une plage numérique unique comme universelle.

Les limites exactes dépendent de la distribution et de sa configuration.

Sur un système utilisant des valeurs configurées dans `/etc/login.defs`, tu peux examiner :

```bash
grep -E '^(UID_MIN|UID_MAX|SYS_UID_MIN|SYS_UID_MAX)' /etc/login.defs
```

Ce fichier fournit des paramètres utilisés par certains outils de gestion des comptes. Toutes les sources d'identité ne suivent pas nécessairement les mêmes plages.

## 3.5. Afficher l'identité numérique

Commande :

```bash
id alice
```

Exemple de résultat :

```text
uid=1001(alice) gid=1005(developpeurs) groups=1005(developpeurs),1006(projets)
```

Interprétation :

- `uid=1001(alice)` : UID de l'utilisateur.
- `gid=1005(developpeurs)` : groupe principal.
- `groups=...` : groupes supplémentaires de l'utilisateur.

Pour connaître l'identité de l'utilisateur courant :

```bash
id
```

Pour obtenir uniquement l'UID :

```bash
id -u
```

Pour obtenir le GID principal :

```bash
id -g
```

Pour afficher les noms des groupes :

```bash
id -Gn
```

## 3.6. Pourquoi les identifiants numériques sont-ils importants ?

Imaginons qu'un fichier appartienne à l'UID `1001`.

Si un système dispose de plusieurs sources d'identité ou si des fichiers sont transférés entre serveurs, le nom associé à cet UID peut différer.

Par exemple :

```text
Serveur A :
UID 1001 = alice

Serveur B :
UID 1001 = service-backup
```

Le même UID peut donc être associé à des noms différents sur ces deux machines.

Lorsqu'on partage ou restaure des fichiers entre systèmes, il est important de comprendre la correspondance entre UID et noms.

Dans un environnement centralisé, des services de gestion des identités peuvent assurer une correspondance cohérente entre les machines.


# 4. Les fichiers système des utilisateurs et des groupes

Linux conserve localement plusieurs fichiers consacrés aux comptes.

Les plus connus sont :

```text
/etc/passwd
/etc/shadow
/etc/group
/etc/gshadow
```

Ces fichiers ont des rôles différents.

## 4.1. Le fichier `/etc/passwd`

Le fichier `/etc/passwd` contient les entrées de comptes locales classiques.

Afficher son contenu :

```bash
cat /etc/passwd
```

Une ligne peut ressembler à ceci :

```text
alice:x:1001:1005:Alice Martin:/home/alice:/bin/bash
```

Les champs sont séparés par le caractère `:`.

| Position | Valeur | Signification |
|---|---|---|
| 1 | `alice` | Nom du compte |
| 2 | `x` | Indication que les informations d'authentification sont stockées ailleurs, généralement dans `/etc/shadow` |
| 3 | `1001` | UID |
| 4 | `1005` | GID principal |
| 5 | `Alice Martin` | Champ descriptif, parfois appelé GECOS |
| 6 | `/home/alice` | Répertoire personnel |
| 7 | `/bin/bash` | Shell de connexion |

Il ne faut pas confondre le deuxième champ `x` avec un mot de passe.

Dans une configuration courante, le condensat du mot de passe et certaines informations de politique d'authentification sont stockés dans `/etc/shadow`.

## 4.2. Pourquoi `/etc/passwd` est-il généralement lisible ?

De nombreux programmes doivent pouvoir consulter les noms, les UID, les groupes principaux et les répertoires personnels des comptes.

C'est pourquoi `/etc/passwd` est généralement lisible par les utilisateurs ordinaires.

Mais cette lisibilité ne signifie pas que chacun doit pouvoir le modifier.

Vérifier les permissions :

```bash
ls -l /etc/passwd
```

Sur un système classique, le fichier est modifiable seulement par des comptes privilégiés.

Ne modifie pas manuellement ce fichier avec un éditeur ordinaire lorsque des outils de gestion de comptes sont disponibles. Une modification incorrecte peut empêcher l'authentification ou créer des incohérences.

## 4.3. Le fichier `/etc/shadow`

Le fichier `/etc/shadow` contient les informations de mot de passe protégées et des données relatives à son expiration.

Pour consulter les permissions du fichier :

```bash
ls -l /etc/shadow
```

Sur de nombreux systèmes, il n'est pas lisible par les utilisateurs ordinaires.

Une ligne peut avoir une structure de ce type :

```text
alice:$y$EXEMPLE...:20000:0:99999:7:::
```

Cette ligne est uniquement illustrative.

Les champs peuvent représenter notamment :

1. Le nom du compte.
2. Le condensat du mot de passe ou un marqueur d'état.
3. La date de dernière modification du mot de passe, exprimée en jours depuis une date de référence.
4. Le nombre minimal de jours entre deux modifications.
5. Le nombre maximal de jours avant expiration.
6. Le délai d'avertissement avant expiration.
7. Le délai après expiration avant désactivation de l'authentification concernée.
8. La date d'expiration du compte.
9. Un champ réservé.

La structure exacte et les interprétations doivent être vérifiées sur le système utilisé.

Il ne faut pas diffuser le contenu de `/etc/shadow` dans un espace public ou dans un rapport non protégé.

## 4.4. Le fichier `/etc/group`

Le fichier `/etc/group` décrit les groupes locaux.

Afficher son contenu :

```bash
cat /etc/group
```

Exemple :

```text
developpeurs:x:1005:alice,bob,claire
```

Les champs sont :

| Position | Valeur | Signification |
|---|---|---|
| 1 | `developpeurs` | Nom du groupe |
| 2 | `x` | Champ de référence pour les informations de groupe protégées, lorsqu'elles sont utilisées |
| 3 | `1005` | GID |
| 4 | `alice,bob,claire` | Liste des membres supplémentaires du groupe dans ce fichier |

La liste du dernier champ ne présente pas nécessairement tous les comptes dont ce groupe est le groupe principal. Le GID principal est associé à chaque compte dans la définition de celui-ci.

Pour connaître les groupes effectifs d'un utilisateur, utilise plutôt :

```bash
id alice
```

## 4.5. Le fichier `/etc/gshadow`

Le fichier `/etc/gshadow` contient les informations de groupe protégées, notamment certaines informations d'administration des groupes.

Vérifier les permissions :

```bash
ls -l /etc/gshadow
```

Il ne faut pas le modifier manuellement sans connaître les mécanismes utilisés par la distribution.

Les commandes telles que `groupadd`, `groupmod` et `gpasswd` sont conçues pour gérer les groupes et préserver la cohérence des fichiers concernés.

## 4.6. Schéma récapitulatif

```text
               GESTION DES COMPTES
                        |
         +--------------+--------------+
         |              |              |
         v              v              v
    /etc/passwd    /etc/shadow     /etc/group
         |              |              |
         v              v              v
     Identité       Authentification   Groupes
     et UID         et expiration     et GID
         |
         v
    /etc/gshadow
         |
         v
 Informations protégées
 liées aux groupes
```

Ce schéma représente les fichiers locaux classiques. Un système peut également obtenir des comptes depuis d'autres sources, telles qu'un annuaire centralisé.

## 4.7. Utiliser les outils plutôt que modifier les fichiers à la main

Pour créer un compte :

```bash
sudo useradd ...
```

Pour modifier un compte :

```bash
sudo usermod ...
```

Pour changer un mot de passe :

```bash
sudo passwd ...
```

Pour gérer un groupe :

```bash
sudo groupadd ...
sudo groupmod ...
sudo gpasswd ...
```

Ces outils réduisent le risque de créer des entrées incohérentes entre les fichiers.


# 5. Afficher et rechercher les comptes

## 5.1. Afficher les comptes configurés localement

Pour parcourir les comptes du fichier local :

```bash
cat /etc/passwd
```

Pour afficher seulement les noms :

```bash
cut -d: -f1 /etc/passwd
```

Explication :

- `cut` extrait certains champs d'une ligne.
- `-d:` précise que les champs sont séparés par `:`.
- `-f1` sélectionne le premier champ.

Cette commande présente les comptes figurant dans `/etc/passwd`. Elle ne garantit pas qu'elle affiche toutes les identités disponibles si le système utilise aussi une source externe.

## 5.2. Interroger la base de comptes du système

La commande `getent` interroge la base d'identités configurée sur le système.

Afficher les entrées utilisateur :

```bash
getent passwd
```

Rechercher un compte précis :

```bash
getent passwd alice
```

Pour les groupes :

```bash
getent group
```

Rechercher un groupe :

```bash
getent group developpeurs
```

Ces commandes sont particulièrement utiles sur les machines qui utilisent une gestion centralisée des identités.

## 5.3. Vérifier si un compte existe

Exemple :

```bash
getent passwd alice
```

Si une entrée correspondante est renvoyée, le système peut résoudre cette identité.

Si aucune entrée n'apparaît, plusieurs raisons sont possibles : le compte peut être absent, la source externe peut être indisponible ou le système peut être configuré différemment.

Il ne faut donc pas toujours interpréter une absence de résultat comme une preuve que le compte n'a jamais existé.

## 5.4. Afficher les informations d'un utilisateur

```bash
id alice
```

Pour consulter les informations de compte avec la commande `getent` :

```bash
getent passwd alice
```

Pour connaître le répertoire personnel déclaré :

```bash
getent passwd alice | cut -d: -f6
```

Pour connaître le shell déclaré :

```bash
getent passwd alice | cut -d: -f7
```

Ces commandes montrent les informations définies pour le compte. Elles ne garantissent pas que le répertoire personnel existe réellement ou que le shell est installé.

## 5.5. Connaître les groupes de l'utilisateur courant

```bash
groups
```

Pour un compte précis :

```bash
groups alice
```

Une autre commande :

```bash
id alice
```

`id` est souvent plus utile pour obtenir les UID et GID en plus des noms.

## 5.6. Afficher les utilisateurs connectés

Commandes courantes :

```bash
who
```

Et :

```bash
w
```

`who` affiche des informations sur les sessions enregistrées par le système.

`w` fournit généralement des informations supplémentaires sur les utilisateurs connectés et leur activité.

Pour examiner l'historique disponible des connexions :

```bash
last
```

La quantité d'information dépend des journaux présents et de la configuration locale.

Ces commandes ne remplacent pas une solution d'audit complète, mais elles permettent d'effectuer une première vérification.


# 6. Créer un utilisateur

## 6.1. Pourquoi créer des comptes individuels ?

Dans une entreprise, il est préférable que chaque personne utilise son propre compte.

Si plusieurs personnes partagent le même compte, il devient plus difficile de déterminer :

- Qui a modifié un fichier.
- Qui a exécuté une commande.
- Qui a changé une configuration.
- Qui doit se voir retirer un accès.
- À qui appartiennent certains fichiers.

Un compte individuel permet une meilleure séparation des responsabilités.

Évite de créer un compte partagé simplement pour simplifier l'administration lorsque des comptes individuels sont possibles.

## 6.2. La commande `useradd`

La commande `useradd` permet de créer un compte utilisateur.

Forme générale :

```bash
sudo useradd [options] nom_utilisateur
```

L'action réelle dépend des options fournies et des valeurs par défaut de la distribution.

Consulte le manuel :

```bash
man useradd
```

Exemple :

```bash
sudo useradd alice
```

Cette commande tente de créer un compte appelé `alice` avec les valeurs par défaut applicables.

Selon la configuration, elle peut ne pas créer le répertoire personnel et ne définit pas nécessairement un mot de passe utilisable pour une connexion.

Pour un compte humain classique, il est donc utile de préciser les options nécessaires.

## 6.3. Créer un utilisateur avec un répertoire personnel

Exemple :

```bash
sudo useradd -m alice
```

Le paramètre `-m` demande la création du répertoire personnel si nécessaire et selon les règles de l'outil.

Le chemin est généralement de la forme :

```text
/home/alice
```

Mais la base des répertoires personnels peut varier selon la configuration.

Vérifier le compte :

```bash
getent passwd alice
```

Vérifier le répertoire :

```bash
ls -ld /home/alice
```

Si le compte vient d'être créé, le système peut également recopier les fichiers présents dans `/etc/skel`.

## 6.4. Créer un compte avec un shell précis

Exemple :

```bash
sudo useradd -m -s /bin/bash alice
```

Explication :

- `-m` demande la création du répertoire personnel.
- `-s /bin/bash` définit le shell de connexion.
- `alice` est le nom du compte.

Le shell doit exister sur le système. Sur certaines distributions, le chemin disponible peut être différent.

Pour vérifier le chemin du programme Bash :

```bash
command -v bash
```

Pour créer un utilisateur ordinaire, choisis un shell adapté à son besoin.

Ne considère pas un shell particulier comme une garantie de sécurité : les permissions, les privilèges et les mécanismes d'authentification restent essentiels.

## 6.5. Définir un mot de passe

Pour définir le mot de passe d'un compte :

```bash
sudo passwd alice
```

Le système demande habituellement de saisir le nouveau mot de passe puis de le confirmer.

Le mot de passe ne doit pas être ajouté directement à la commande sous forme de texte visible.

Évite les méthodes qui exposent un secret dans l'historique du shell, les arguments de processus, les journaux ou les scripts non protégés.

## 6.6. Procédure complète de création

Pour créer un compte de laboratoire nommé `alice` :

### Étape 1 : vérifier que le compte n'existe pas déjà

```bash
getent passwd alice
```

Si le compte existe, ne le recrée pas. Inspecte sa configuration.

### Étape 2 : créer le compte

```bash
sudo useradd -m -s /bin/bash alice
```

### Étape 3 : définir le mot de passe

```bash
sudo passwd alice
```

### Étape 4 : vérifier l'identité

```bash
id alice
```

### Étape 5 : vérifier le répertoire personnel et le shell

```bash
getent passwd alice
ls -ld /home/alice
```

### Étape 6 : examiner les groupes

```bash
groups alice
```

### Résultat attendu

Le système doit reconnaître le compte, ses informations doivent être cohérentes et le répertoire personnel doit exister si sa création a été demandée.

## 6.7. La commande `adduser`

Sur certaines distributions, notamment Debian et Ubuntu, `adduser` est un outil de plus haut niveau qui guide l'administrateur lors de la création d'un compte.

Exemple :

```bash
sudo adduser alice
```

L'outil peut demander des informations et proposer des étapes supplémentaires.

`adduser` et `useradd` ne sont pas identiques sur toutes les distributions.

- `useradd` est un outil système traditionnel de création de comptes.
- `adduser` est souvent un outil plus convivial, selon la distribution.

Avant de rédiger un script destiné à plusieurs distributions, vérifie la disponibilité et le comportement de l'outil choisi.

## 6.8. Pourquoi vérifier après la création ?

Une commande peut échouer ou produire un résultat différent de ce qui était prévu.

Après avoir créé un compte, il est donc recommandé de vérifier :

```bash
getent passwd alice
id alice
ls -ld /home/alice
```

L'administration ne se termine pas au moment où la commande est exécutée. Elle se termine lorsque l'état attendu est confirmé.


# 7. Gérer les mots de passe

## 7.1. Modifier son propre mot de passe

Un utilisateur ordinaire peut généralement changer son propre mot de passe avec :

```bash
passwd
```

Le système demande habituellement le mot de passe actuel, puis le nouveau mot de passe.

Les politiques locales peuvent refuser un mot de passe trop faible ou une modification non autorisée.

## 7.2. Modifier le mot de passe d'un autre utilisateur

Un administrateur disposant des privilèges nécessaires peut utiliser :

```bash
sudo passwd alice
```

La commande permet de définir un nouveau mot de passe sans avoir à connaître l'ancien secret de l'utilisateur.

L'administrateur ne doit pas chercher à connaître les mots de passe personnels des utilisateurs. Il doit utiliser les mécanismes de gestion des comptes prévus à cet effet.

## 7.3. Vérifier l'état du mot de passe

Une commande utile est :

```bash
sudo passwd -S alice
```

Elle affiche un état synthétique du mot de passe, selon les capacités de la distribution.

Sur les systèmes qui le prennent en charge, le résultat permet notamment de distinguer certaines situations comme un mot de passe présent, verrouillé ou non défini.

Ne partage pas des informations sensibles provenant des bases d'authentification dans un rapport public.

## 7.4. Verrouiller un mot de passe

Commande :

```bash
sudo passwd -l alice
```

Cette commande verrouille le mot de passe selon le mécanisme utilisé par le système.

Il faut cependant comprendre sa limite :

**Verrouiller le mot de passe ne désactive pas nécessairement toutes les méthodes d'accès au compte.**

Une connexion utilisant une clé SSH, un autre mécanisme PAM, un jeton ou un service externe peut être soumise à des règles différentes.

Si le compte doit être complètement désactivé, l'administrateur doit définir une procédure adaptée à toutes les méthodes d'authentification disponibles.

## 7.5. Déverrouiller un mot de passe

Lorsque le verrouillage doit être retiré :

```bash
sudo passwd -u alice
```

Ne déverrouille pas un compte uniquement parce qu'un utilisateur le demande sans vérifier que la demande est légitime et que le compte doit réellement être réactivé.

Vérifie également l'état des autres mécanismes de sécurité.

## 7.6. Expiration des mots de passe

La commande `chage` permet de consulter ou de modifier certaines règles d'expiration des comptes.

Pour consulter les informations disponibles :

```bash
sudo chage -l alice
```

Le résultat peut inclure :

- La date de dernière modification du mot de passe.
- La durée de validité configurée.
- Les avertissements avant expiration.
- Des informations sur l'expiration du compte.

La politique de sécurité de l'organisation et les mécanismes de connexion doivent déterminer les règles à appliquer.

Il ne faut pas choisir automatiquement une durée arbitraire sans tenir compte des exigences de sécurité et de l'environnement.

## 7.7. Forcer un changement de mot de passe à la prochaine connexion

Dans les environnements qui utilisent le mécanisme local classique :

```bash
sudo chage -d 0 alice
```

Cette commande marque généralement le mot de passe comme devant être changé à la prochaine occasion d'authentification compatible.

Il faut vérifier le comportement de l'environnement et avertir l'utilisateur si cela peut interrompre son activité.

## 7.8. Ne jamais stocker les mots de passe en clair

Un mot de passe est un secret d'authentification.

Évite de placer un mot de passe dans :

```text
Un script partagé
Un dépôt Git
Un fichier texte accessible à plusieurs personnes
Une commande enregistrée dans l'historique
Un message de journalisation
Un document de procédure non protégé
```

Les administrateurs doivent utiliser les mécanismes de gestion des secrets adaptés à l'environnement.


# 8. Comprendre les groupes Linux

## 8.1. Pourquoi les groupes sont-ils nécessaires ?

Sans groupes, il faudrait souvent gérer individuellement les permissions de chaque utilisateur.

Considérons une équipe :

```text
alice
bob
claire
```

Tous les membres doivent pouvoir accéder à un même répertoire de projet.

Une organisation fondée sur un groupe est plus simple :

```text
Groupe : developpeurs
|
+-- alice
+-- bob
+-- claire
       |
       v
Répertoire partagé
/data/projets
```

Les permissions du répertoire peuvent autoriser le groupe `developpeurs` à lire, modifier ou créer des fichiers.

Les groupes rendent les politiques d'accès plus faciles à comprendre et à maintenir.

## 8.2. Groupe principal

Chaque utilisateur possède un GID principal dans sa définition de compte.

Exemple :

```text
alice
|
+-- UID : 1001
|
+-- Groupe principal : developpeurs
                         |
                         +-- GID : 1005
```

Lorsqu'un utilisateur crée un fichier dans un contexte ordinaire, le groupe associé au fichier dépend des règles du répertoire parent, du comportement du système de fichiers et des paramètres applicables.

Le groupe principal constitue la base de l'identité de groupe du processus, mais il n'est pas toujours le groupe attribué à un nouveau fichier.

## 8.3. Groupes supplémentaires

Un utilisateur peut appartenir à plusieurs groupes supplémentaires.

Exemple :

```text
alice
|
+-- Groupe principal : developpeurs
|
+-- Groupe supplémentaire : projets
|
+-- Groupe supplémentaire : sauvegarde
```

Ces groupes peuvent lui donner des droits complémentaires.

Vérifier les groupes d'un utilisateur :

```bash
id alice
```

Ou :

```bash
groups alice
```

## 8.4. Créer un groupe

Commande :

```bash
sudo groupadd developpeurs
```

Vérifier le groupe :

```bash
getent group developpeurs
```

L'identifiant GID est attribué selon les règles et disponibilités du système.

Ne suppose pas qu'un GID précis sera disponible ou qu'il sera identique sur toutes les machines.

## 8.5. Créer un utilisateur avec un groupe principal précis

Exemple :

```bash
sudo groupadd projets
sudo useradd -m -g projets alice
```

Explication :

- `groupadd projets` crée le groupe si celui-ci n'existe pas.
- `useradd -m` crée le compte et demande la création du répertoire personnel.
- `-g projets` désigne le groupe principal du nouvel utilisateur.

Cette méthode doit être utilisée seulement si le groupe principal recherché correspond réellement à la politique de l'organisation.

Si le groupe existe déjà, il faut le vérifier plutôt que tenter de le recréer.

## 8.6. Créer un utilisateur et lui attribuer un groupe supplémentaire

Exemple :

```bash
sudo useradd -m -G projets alice
```

Le paramètre `-G` précise les groupes supplémentaires à l'initialisation du compte.

L'option `-g`, elle, désigne le groupe principal.

Cette distinction est importante.

Un utilisateur peut avoir :

```text
Groupe principal : utilisateurs
Groupes supplémentaires : projets, sauvegarde
```

Il ne faut pas intervertir les deux options sans comprendre l'effet souhaité.


# 9. Ajouter et retirer un utilisateur d'un groupe

## 9.1. Ajouter un groupe supplémentaire avec `usermod`

Exemple :

```bash
sudo usermod -aG developpeurs alice
```

Cette commande ajoute `alice` au groupe supplémentaire `developpeurs`.

Les options sont importantes :

- `-G` désigne la liste des groupes supplémentaires.
- `-a` signifie ajouter aux groupes supplémentaires existants.

**Ne retire pas `-a` sans comprendre les conséquences.**

En effet, la commande :

```bash
sudo usermod -G developpeurs alice
```

peut remplacer la liste existante des groupes supplémentaires par la liste donnée.

Un utilisateur pourrait alors perdre l'appartenance à d'autres groupes dont il a besoin.

## 9.2. Vérifier l'ajout

```bash
id alice
```

Ou :

```bash
groups alice
```

Le groupe doit apparaître parmi les groupes associés au compte.

Les processus déjà en cours ne reçoivent pas nécessairement immédiatement la nouvelle liste de groupes. L'utilisateur doit souvent ouvrir une nouvelle session pour que les nouveaux groupes soient pris en compte dans ses processus.

## 9.3. Retirer un utilisateur d'un groupe

Sur de nombreuses distributions, la commande suivante est disponible :

```bash
sudo gpasswd -d alice developpeurs
```

Elle retire `alice` du groupe supplémentaire indiqué, sous réserve de la configuration locale et de l'existence du groupe.

Vérifier :

```bash
id alice
```

Ne retire pas un utilisateur d'un groupe avant de comprendre quelles permissions et quels services dépendent de cette appartenance.

## 9.4. Modifier le groupe principal

Pour modifier le groupe principal d'un utilisateur :

```bash
sudo usermod -g developpeurs alice
```

Cette commande change le groupe principal déclaré du compte.

Elle ne modifie pas automatiquement le groupe des fichiers déjà présents dans le répertoire personnel ou ailleurs.

Si l'objectif est également de modifier les fichiers appartenant à l'ancien groupe, il faut définir une procédure distincte et vérifier quels fichiers sont concernés.

## 9.5. Examiner l'appartenance à un groupe

```bash
getent group developpeurs
```

Cette commande affiche l'entrée du groupe selon les sources d'identité configurées.

Les utilisateurs dont le groupe principal correspond au GID peuvent ne pas apparaître dans le dernier champ de cette entrée.

Pour une vue plus complète des groupes d'un utilisateur :

```bash
id alice
```

## 9.6. Schéma d'accès par groupe

```text
Utilisateurs
|
+-- alice
|
+-- bob
|
+-- claire
      |
      v
Groupe developpeurs
      |
      v
Permissions du répertoire
      |
      v
/data/projets
      |
      +-- Lecture
      +-- Écriture
      +-- Traversée
```

Ce schéma montre le principe général.

Les opérations réellement permises dépendent aussi des permissions du fichier, des ACL, des options de montage et d'autres règles éventuelles.


# 10. Modifier un compte utilisateur

## 10.1. La commande `usermod`

`usermod` permet de modifier des attributs d'un compte existant.

Forme générale :

```bash
sudo usermod [options] nom_utilisateur
```

Pour consulter les options disponibles :

```bash
man usermod
```

Les options courantes permettent de modifier :

- Le nom du compte.
- Le répertoire personnel.
- Le shell de connexion.
- Le groupe principal.
- Les groupes supplémentaires.
- La date d'expiration du compte.
- Certains attributs associés au compte.

Il faut choisir l'option adaptée à l'objectif et vérifier le résultat après la modification.

## 10.2. Changer le nom d'un compte

Exemple :

```bash
sudo usermod -l alice2 alice
```

Cette commande change le nom de connexion de `alice` en `alice2`.

**Elle ne renomme pas automatiquement le répertoire personnel existant dans tous les cas.**

Avant de modifier un nom de compte, examine les usages du compte, ses processus, ses tâches planifiées, les permissions de fichiers et les références éventuelles dans la configuration.

Une modification de nom n'est pas une simple transformation cosmétique sur un serveur utilisé par des services.

## 10.3. Modifier le répertoire personnel

Commande :

```bash
sudo usermod -d /home/alice2 alice
```

Cette commande change le répertoire personnel déclaré dans les informations du compte.

Elle ne signifie pas nécessairement que tout le contenu a été déplacé.

Pour déplacer le répertoire personnel en même temps que sa référence, l'option `-m` peut être utilisée lorsque cela correspond à la situation :

```bash
sudo usermod -d /home/alice2 -m alice
```

Cette opération doit être préparée : le chemin cible, les permissions, l'espace disponible et l'état des processus doivent être vérifiés.

Ne déplace pas un répertoire personnel utilisé par une session active sans comprendre les conséquences.

## 10.4. Changer le shell de connexion

Exemple :

```bash
sudo usermod -s /bin/bash alice
```

Pour examiner les shells de connexion généralement autorisés par la configuration locale :

```bash
cat /etc/shells
```

Ce fichier énumère les shells considérés comme valides par certains mécanismes.

La présence d'un shell dans ce fichier ne signifie pas qu'il est adapté à tous les comptes.

## 10.5. Modifier les informations descriptives

Le champ descriptif d'un compte peut contenir un nom complet ou une information administrative.

Exemple :

```bash
sudo usermod -c "Alice Martin - Developpement" alice
```

Le texte descriptif ne remplace pas le nom de connexion et ne doit pas contenir d'informations sensibles inutiles.

## 10.6. Modifier le compte puis vérifier

Chaque modification devrait être suivie d'un contrôle.

Exemple :

```bash
sudo usermod -s /bin/bash alice
```

Puis :

```bash
getent passwd alice
id alice
```

Pour une modification du répertoire personnel :

```bash
ls -ld /home/alice
```

La vérification doit porter sur la propriété que l'on souhaitait modifier, mais également sur les effets secondaires importants.


# 11. Gérer les répertoires personnels

## 11.1. À quoi sert un répertoire personnel ?

Le répertoire personnel est l'espace associé à l'utilisateur.

Il contient généralement ses documents personnels, ses configurations et certains fichiers propres à ses applications.

Exemple :

```text
/home
 |
 +-- alice
 |    |
 |    +-- Documents/
 |    +-- Téléchargements/
 |    +-- .config/
 |
 +-- bob
      |
      +-- Documents/
      +-- .config/
```

Les répertoires personnels de comptes humains sont souvent stockés sous `/home`, mais ce n'est pas une obligation absolue.

Le compte `root` utilise traditionnellement `/root`.

## 11.2. Pourquoi les permissions du répertoire personnel sont-elles importantes ?

Un répertoire personnel peut contenir des informations confidentielles.

Il est donc important de vérifier qui peut le lire, le traverser ou le modifier.

Afficher les permissions :

```bash
ls -ld /home/alice
```

Pour inspecter les détails :

```bash
stat /home/alice
```

Le répertoire doit appartenir au bon utilisateur, avec des permissions adaptées à la politique de l'environnement.

Il ne faut pas supposer qu'un compte nouvellement créé possède forcément toutes les permissions souhaitées.

## 11.3. Comprendre `/etc/skel`

Lorsqu'un compte est créé avec une option de création du répertoire personnel, des fichiers présents dans `/etc/skel` peuvent être copiés dans le nouveau répertoire.

Afficher le contenu :

```bash
ls -la /etc/skel
```

Cette arborescence peut contenir des fichiers de configuration par défaut.

Les administrateurs peuvent l'utiliser pour préparer un environnement de travail cohérent pour les nouveaux comptes.

Ne place pas de secret personnel ou de clé privée partagée dans `/etc/skel`.

Tout fichier ajouté à cet emplacement peut être copié vers les nouveaux comptes selon le comportement de l'outil de création.

## 11.4. Créer un répertoire personnel avec les bonnes propriétés

Exemple pour un compte de laboratoire :

```bash
sudo useradd -m -s /bin/bash alice
```

Examiner le répertoire :

```bash
ls -ld /home/alice
```

Si des modifications de propriété sont nécessaires, il faut définir une action adaptée après avoir vérifié le chemin.

Par exemple :

```bash
sudo chown alice:alice /home/alice
```

Cette commande suppose que le groupe principal s'appelle réellement `alice`. Ce n'est pas une règle universelle : vérifie le résultat de `id alice` avant de l'utiliser.

Une commande de changement de propriétaire ne doit jamais être appliquée à un chemin large ou mal vérifié.

## 11.5. Retrouver les fichiers d'un utilisateur

Pour rechercher des fichiers appartenant à Alice dans un système de fichiers donné :

```bash
sudo find /home -xdev -user alice -type f -print
```

Le paramètre `-xdev` évite de parcourir les autres systèmes de fichiers montés sous le chemin étudié.

Cette commande recherche les fichiers appartenant à l'utilisateur. Elle ne trouve pas nécessairement tous les objets dont le compte est responsable au sens applicatif.

Pour examiner les fichiers qui appartiennent à un UID numérique :

```bash
sudo find /home -xdev -uid 1001 -print
```

Le numéro doit être remplacé par l'UID réellement concerné.

## 11.6. Ne pas confondre répertoire personnel et autorisation globale

Posséder un répertoire personnel n'accorde pas automatiquement à l'utilisateur le droit de modifier tous les fichiers du système.

Les accès restent limités par les permissions, les ACL et les contrôles complémentaires.

De même, un utilisateur peut avoir le droit d'écrire dans un répertoire partagé sans que celui-ci fasse partie de son répertoire personnel.


# 12. Supprimer ou désactiver un compte

## 12.1. Pourquoi la suppression doit-elle être préparée ?

La suppression d'un utilisateur peut affecter :

- Ses sessions actives.
- Ses tâches planifiées.
- Ses fichiers.
- Ses clés et autorisations.
- Ses groupes.
- Ses services.
- Les scripts qui dépendent de son nom ou de son UID.
- Les applications qui utilisent son identité.

Avant de supprimer un compte, il faut déterminer ce qui doit être conservé, transféré ou désactivé.

Une suppression n'est pas seulement une opération sur `/etc/passwd`.

## 12.2. Verrouiller un mot de passe ou désactiver un compte ?

Ces notions sont différentes.

Le verrouillage du mot de passe peut empêcher certaines authentifications fondées sur ce mécanisme.

Mais d'autres moyens d'accès peuvent rester opérationnels selon la configuration.

Une désactivation complète doit être abordée au regard des méthodes réellement utilisées :

- Mot de passe local.
- Clés SSH.
- Authentification centralisée.
- Jetons ou mécanismes PAM.
- Sessions déjà ouvertes.
- Comptes de service et tâches automatisées.

Il faut vérifier la documentation du système et les exigences de sécurité de l'organisation.

## 12.3. Vérifier les processus d'un utilisateur

Avant une désactivation ou une suppression, examiner les processus associés :

```bash
ps -u alice -f
```

Cette commande affiche les processus associés à l'identité sélectionnée selon les possibilités de l'outil.

Il faut également rechercher les tâches planifiées et les services qui peuvent dépendre du compte.

Sur un serveur de production, la suppression d'un compte de service peut interrompre des applications.

## 12.4. Supprimer un utilisateur sans supprimer son répertoire personnel

Commande :

```bash
sudo userdel alice
```

Cette commande supprime l'entrée du compte local concerné, lorsque les conditions le permettent.

Les fichiers ne sont pas nécessairement supprimés en même temps.

C'est parfois souhaitable pour conserver les données jusqu'à ce qu'elles soient archivées, transférées ou examinées.

Avant de poursuivre, vérifie les conséquences sur les fichiers et les services associés.

## 12.5. Supprimer un compte avec son répertoire personnel

Commande :

```bash
sudo userdel -r alice
```

**Attention : l'option `-r` demande également la suppression du répertoire personnel et du répertoire de messagerie local associé, selon la configuration.**

Cette opération peut être destructive.

Avant de l'utiliser :

1. Vérifie le nom exact du compte.
2. Examine son répertoire personnel.
3. Identifie les fichiers à conserver.
4. Contrôle les processus et tâches.
5. Effectue une sauvegarde si nécessaire.
6. Confirme que la suppression est autorisée.
7. Vérifie le résultat.

Ne lance pas cette commande sur un compte important sans préparation.

## 12.6. Rechercher des fichiers orphelins

Après la suppression d'un compte, certains fichiers peuvent conserver son ancien UID.

Supposons que l'UID soit `1001`.

```bash
sudo find / -xdev -uid 1001 -print 2>/dev/null
```

Cette commande peut parcourir une partie importante du système de fichiers racine.

Adapte le chemin à la zone concernée pour limiter la recherche.

Les fichiers trouvés ne doivent pas être automatiquement supprimés ou réattribués.

Ils peuvent appartenir à une application ou correspondre à des données qu'il faut conserver.

## 12.7. Retirer un utilisateur d'un groupe

Avant de supprimer un groupe, vérifie les comptes et les permissions qui en dépendent.

Pour retirer un utilisateur d'un groupe supplémentaire :

```bash
sudo gpasswd -d alice projets
```

Vérifie ensuite :

```bash
id alice
```

La gestion des groupes doit être cohérente avec les permissions des fichiers et les responsabilités des utilisateurs.

## 12.8. Procédure de retrait d'un utilisateur

Une méthode prudente peut suivre cet ordre :

```text
Demande de retrait
       |
       v
Vérification de l'autorisation
       |
       v
Identification du compte
       |
       v
Inventaire des accès et processus
       |
       v
Sauvegarde ou transfert des données
       |
       v
Désactivation des accès nécessaires
       |
       v
Vérification des accès restants
       |
       v
Suppression éventuelle du compte
       |
       v
Contrôle des fichiers restants
       |
       v
Documentation de l'opération
```

Les procédures de départ d'un collaborateur doivent également traiter les accès externes : clés, applications, dépôts, VPN et autres services.


# 13. Permissions et relations entre utilisateurs et groupes

## 13.1. Les trois catégories de permissions

Linux distingue classiquement trois catégories :

- Le propriétaire du fichier.
- Le groupe associé au fichier.
- Les autres utilisateurs.

Pour un fichier donné, on peut représenter les permissions ainsi :

```text
             Fichier
                |
      +---------+---------+
      |         |         |
      v         v         v
 Propriétaire  Groupe   Autres
      |         |         |
      v         v         v
   rwx         r-x       ---
```

Les droits affichés ici sont illustratifs.

Ils peuvent autoriser le propriétaire à lire, modifier et exécuter le fichier, autoriser le groupe à le lire et à l'exécuter, et interdire l'accès aux autres utilisateurs.

## 13.2. Examiner un fichier

Commande :

```bash
ls -l rapport.txt
```

Exemple de sortie :

```text
-rw-r----- 1 alice developpeurs 2048 oct 24 10:00 rapport.txt
```

Interprétation :

```text
-rw-r-----
 |
 +-- Type : fichier ordinaire
 |
 +-- Propriétaire : alice
 |
 +-- Groupe : developpeurs
 |
 +-- Taille : 2048 octets
```

Les droits sont divisés en trois groupes de trois caractères :

```text
rw- r-- ---
 |   |   |
 |   |   +-- Autres
 |   +------ Groupe
 +---------- Propriétaire
```

La présence d'un utilisateur dans le groupe `developpeurs` peut donc lui donner accès au fichier si les permissions et les autres règles le permettent.

## 13.3. Les permissions de répertoire

Les permissions appliquées à un répertoire ont une signification particulière.

| Permission | Signification générale pour un répertoire |
|---|---|
| `r` | Lire la liste des noms présents, sous réserve des autres contrôles |
| `w` | Modifier les entrées du répertoire, sous réserve notamment du droit de traversée |
| `x` | Traverser le répertoire et accéder aux chemins autorisés |

Un utilisateur peut avoir le droit de lire les noms présents dans un répertoire sans être autorisé à lire le contenu de tous les fichiers.

De même, un utilisateur a besoin du droit de traversée approprié pour accéder à un fichier situé dans un répertoire.

## 13.4. Créer un répertoire partagé

Supposons qu'une équipe utilise le groupe `developpeurs`.

Créer le répertoire :

```bash
sudo mkdir -p /srv/projets
```

Attribuer le groupe :

```bash
sudo chown root:developpeurs /srv/projets
```

Appliquer des permissions de partage de groupe :

```bash
sudo chmod 2770 /srv/projets
```

Le mode `2770` active le bit SGID sur le répertoire, et accorde les droits de lecture, d'écriture et de traversée au propriétaire et au groupe.

Les autres utilisateurs ne disposent pas des droits ordinaires définis par ce mode.

Le bit SGID favorise l'héritage du groupe du répertoire parent pour les nouveaux éléments créés dans ce répertoire, selon les règles applicables.

## 13.5. Vérifier les droits d'un utilisateur

Commande :

```bash
id alice
```

Puis :

```bash
ls -ld /srv/projets
```

Pour tester l'accès en tant qu'utilisateur dans un environnement approprié :

```bash
sudo -u alice -- test -x /srv/projets
echo $?
```

Un code de retour `0` indique que le test d'exécution ou de traversée a réussi dans ce contexte. Une autre valeur indique que le test a échoué.

Cette technique constitue un test ciblé, mais les applications peuvent être soumises à d'autres contrôles.

## 13.6. Propriétaire et groupe ne sont pas interchangeables

Changer le groupe d'un fichier ne change pas automatiquement son propriétaire.

Exemple :

```bash
sudo chown alice:developpeurs rapport.txt
```

Cette commande définit le propriétaire à `alice` et le groupe à `developpeurs`.

Changer seulement le groupe peut se faire avec :

```bash
sudo chgrp developpeurs rapport.txt
```

Ces opérations nécessitent les privilèges appropriés.

Il faut toujours vérifier le fichier ciblé et les droits avant d'exécuter une modification récursive.


# 14. Le compte root et les privilèges sudo

## 14.1. Le rôle de root

`root` est le compte privilégié historique des systèmes Unix et Linux.

Il possède généralement des droits très étendus pour administrer le système.

Il peut notamment, sous réserve des mécanismes de sécurité applicables :

- Modifier des fichiers système.
- Gérer les comptes.
- Installer des logiciels.
- Modifier des permissions.
- Administrer des services.
- Effectuer des opérations de stockage.
- Changer la configuration système.

Une opération effectuée avec `root` peut affecter tout le système.

## 14.2. Utiliser sudo

`sudo` permet à un utilisateur autorisé d'exécuter une commande avec des privilèges élevés, selon la politique configurée.

Exemple :

```bash
sudo systemctl status ssh
```

Cette commande demande les privilèges nécessaires pour consulter l'état du service, selon la configuration du système.

Autre exemple :

```bash
sudo useradd -m alice
```

La commande `useradd` modifie la base des comptes et nécessite généralement des privilèges administratifs.

## 14.3. Vérifier les droits sudo

Pour consulter les autorisations applicables au compte courant :

```bash
sudo -l
```

Le résultat présente les commandes autorisées dans le cadre de la configuration en place.

Pour consulter les groupes du compte :

```bash
id
```

Sur de nombreux systèmes, le groupe autorisé à utiliser `sudo` peut être nommé `sudo` ou `wheel`.

Le nom et les règles exactes dépendent de la distribution.

## 14.4. Ajouter un utilisateur à un groupe administratif

**Cette opération augmente fortement les privilèges du compte.**

Si un compte doit réellement bénéficier des droits administratifs sur une distribution utilisant le groupe `sudo`, la commande peut être :

```bash
sudo usermod -aG sudo alice
```

Sur une distribution utilisant le groupe `wheel`, la configuration peut être différente :

```bash
sudo usermod -aG wheel alice
```

Ne lance pas les deux commandes mécaniquement. Identifie d'abord la politique réelle de la machine.

Après un changement de groupe, l'utilisateur doit souvent ouvrir une nouvelle session.

Vérifie les droits accordés :

```bash
id alice
sudo -l -U alice
```

La commande de vérification pour un autre utilisateur peut nécessiter des privilèges administratifs et dépend de la version installée.

## 14.5. Pourquoi faut-il être prudent avec sudo ?

Un utilisateur disposant de droits sudo très étendus peut effectuer de nombreuses opérations sur le système.

L'ajout à un groupe administratif ne doit donc pas être utilisé comme solution générale à un problème de permissions.

Exemple :

Si Alice doit seulement écrire dans `/srv/projets`, il est préférable de configurer le groupe et les permissions de ce répertoire, plutôt que de lui donner des privilèges administratifs complets.

Le principe est simple :

**Accorde le droit le plus limité qui permet d'effectuer le travail demandé.**

## 14.6. Modifier la configuration sudo

La configuration de `sudo` est souvent gérée dans `/etc/sudoers` et dans des fichiers inclus, par exemple sous `/etc/sudoers.d/`.

Ne modifie pas ces fichiers avec un éditeur ordinaire sans comprendre leur syntaxe.

L'outil habituel pour modifier la configuration principale est :

```bash
sudo visudo
```

`visudo` vérifie la syntaxe selon son fonctionnement et sa configuration, ce qui réduit le risque d'une erreur bloquante.

Pour un usage avancé, il est conseillé de lire le manuel :

```bash
man sudoers
```

Ce cours ne recommande pas d'ajouter des privilèges globaux pour résoudre un simple problème d'accès aux fichiers.


# 15. Les comptes système et les comptes de service

## 15.1. Pourquoi les applications ont-elles besoin d'identités ?

Un service peut devoir lire ou écrire certains fichiers même lorsqu'aucun utilisateur humain n'est connecté.

Linux peut attribuer une identité distincte à ce service.

Exemple :

```text
Serveur web
     |
     v
Compte de service www-data
     |
     v
Fichiers accessibles au service
```

Le compte de service permet de définir des limites d'accès propres au programme.

Si le service est compromis, l'impact peut être réduit lorsque les permissions sont correctement conçues.

## 15.2. Reconnaître un compte de service

Certains comptes système possèdent des caractéristiques fréquentes :

- Un UID situé dans une plage réservée aux comptes système.
- Un répertoire personnel particulier ou inexistant.
- Un shell qui ne permet pas une session interactive.
- Des permissions limitées aux ressources nécessaires.

Ces caractéristiques sont des indices, pas des règles absolues.

Il faut examiner la configuration de la distribution et du service concerné.

## 15.3. Créer un compte de service

Pour créer un compte de service, on peut utiliser des options adaptées à l'environnement.

Exemple illustratif :

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin monservice
```

Cette commande demande :

- `--system` : un compte de type système selon les règles de l'outil.
- `--no-create-home` : ne pas créer de répertoire personnel.
- `--shell /usr/sbin/nologin` : utiliser un shell empêchant généralement une session interactive ordinaire.

Le chemin de `nologin` dépend de la distribution. Vérifie sa présence :

```bash
command -v nologin
```

Un service peut avoir besoin de fichiers ou de répertoires dédiés, qui doivent être créés et attribués avec des droits adaptés.

## 15.4. Pourquoi ne pas utiliser root pour tous les services ?

Si plusieurs services fonctionnent avec des privilèges très étendus, une compromission d'un seul service peut avoir des conséquences beaucoup plus importantes.

Une meilleure séparation peut ressembler à ceci :

```text
          SERVEUR LINUX
               |
      +--------+--------+
      |                 |
      v                 v
  Service web       Service base
   www-data          postgres
      |                 |
      v                 v
  Fichiers web       Données DB
  autorisés          autorisées
```

Les noms exacts dépendent du logiciel et de la distribution.

Chaque service doit avoir les droits réellement nécessaires, sans permissions excessives.

## 15.5. Pourquoi un compte de service n'est-il pas automatiquement sûr ?

Créer un compte non interactif ne suffit pas à sécuriser une application.

Il faut également contrôler :

- Les fichiers accessibles.
- Les répertoires où le service peut écrire.
- Les capacités ou privilèges supplémentaires éventuels.
- Les permissions des secrets.
- Les services et ports utilisés.
- La configuration du programme.
- Les mécanismes de confinement, lorsqu'ils sont employés.

Un compte `nologin` ne remplace pas une politique de sécurité complète.


# 16. Expiration, verrouillage et sécurité des comptes

## 16.1. Distinguer les états d'un compte

Un compte peut exister tout en étant inutilisable pour certaines méthodes de connexion.

Il faut distinguer :

- Compte présent dans la base d'identités.
- Mot de passe défini.
- Mot de passe verrouillé.
- Compte arrivé à expiration.
- Shell de connexion non interactif.
- Accès SSH autorisé ou interdit.
- Session déjà ouverte.
- Accès géré par une source d'identité externe.

Ces conditions peuvent se combiner.

Aucune commande unique ne désactive nécessairement toutes les formes d'accès dans tous les environnements.

## 16.2. Consulter les informations d'expiration

```bash
sudo chage -l alice
```

La sortie donne des informations sur la politique d'expiration du mot de passe et éventuellement sur le compte.

Le format et les valeurs dépendent des paramètres existants.

## 16.3. Configurer une expiration de compte

Pour définir une date d'expiration, le mécanisme local peut utiliser :

```bash
sudo usermod -e 2026-12-31 alice
```

Cette commande est un exemple de configuration d'une date d'expiration du compte au format attendu par l'outil.

Avant de l'appliquer, vérifie la date réelle, la politique de l'organisation et les effets sur les applications qui utilisent le compte.

Pour retirer une date d'expiration explicitement configurée, certaines versions acceptent une option de type :

```bash
sudo usermod -e "" alice
```

Le comportement exact doit être confirmé dans le manuel local avant de l'utiliser.

## 16.4. Désactivation temporaire

Une désactivation temporaire doit tenir compte des moyens d'accès utilisés.

Selon la situation, l'administrateur peut :

- Verrouiller l'authentification par mot de passe.
- Définir une expiration du compte.
- Restreindre les accès SSH.
- Retirer les privilèges temporaires.
- Arrêter ou réattribuer les tâches dépendant du compte.
- Mettre fin aux sessions actives selon une procédure contrôlée.

Il faut comprendre que ces actions ont des effets différents.

Une modification de mot de passe ne termine pas automatiquement toutes les sessions déjà ouvertes.

## 16.5. Bonnes pratiques de sécurité

Pour les comptes humains :

- Utilise un compte individuel par personne.
- Évite les mots de passe réutilisés ou faciles à deviner.
- Ne partage pas les secrets.
- Accorde des privilèges limités.
- Retire les accès qui ne sont plus nécessaires.
- Contrôle régulièrement les groupes privilégiés.
- Vérifie les comptes inactifs selon la politique applicable.
- Conserve une trace des changements importants.

Pour les comptes de service :

- Évite les connexions interactives inutiles.
- Restreins les fichiers accessibles.
- Évite d'accorder des droits administratifs complets sans nécessité.
- Protège les secrets et les fichiers de configuration.
- Documente les dépendances du service.
- Prévois une procédure de rotation des secrets si nécessaire.

## 16.6. Exemple de contrôle d'un compte avant de lui accorder des droits

Supposons qu'Alice demande l'accès administratif.

Commence par :

```bash
id alice
```

Puis :

```bash
sudo -l -U alice
```

Examine également les groupes et les responsabilités du compte.

La bonne question n'est pas seulement « Comment ajouter Alice à un groupe ? », mais plutôt :

> Quel accès Alice doit-elle réellement obtenir pour accomplir sa tâche ?

Cette démarche évite d'accorder des droits excessifs.


# 17. Diagnostic des problèmes courants

## 17.1. Problème : `useradd` indique que l'utilisateur existe déjà

Exemple :

```text
useradd: user 'alice' already exists
```

La première étape consiste à examiner le compte existant :

```bash
getent passwd alice
id alice
```

N'essaie pas de recréer le compte en changeant arbitrairement son UID.

Si le compte existe, détermine s'il faut le modifier ou si un nom différent doit être utilisé.

## 17.2. Problème : l'utilisateur ne peut pas se connecter

Plusieurs causes sont possibles :

- Aucun mot de passe utilisable.
- Mot de passe verrouillé.
- Compte expiré.
- Shell non interactif.
- Mauvais répertoire personnel.
- Mauvaises permissions.
- Configuration SSH restrictive.
- Problème d'authentification centralisée.
- Problème du système de fichiers.

Commence par examiner les informations du compte :

```bash
getent passwd alice
id alice
sudo passwd -S alice
sudo chage -l alice
```

Pour les journaux, les chemins et commandes varient selon la distribution et le mécanisme d'authentification. Sur un système utilisant systemd, on peut commencer par :

```bash
sudo journalctl --since "30 minutes ago"
```

Ne réinitialise pas systématiquement le mot de passe avant d'avoir identifié la cause probable.

## 17.3. Problème : le compte n'accède pas au répertoire partagé

Exemple :

```text
Permission denied
```

Vérifie l'identité :

```bash
id alice
```

Vérifie les permissions du répertoire :

```bash
ls -ld /srv/projets
```

Vérifie les permissions du chemin et les montages :

```bash
namei -l /srv/projets
findmnt -T /srv/projets
```

La commande `namei -l` permet d'examiner les permissions des différents éléments du chemin.

L'accès peut échouer parce que l'utilisateur n'a pas le droit de traversée sur un répertoire parent, même si le dernier répertoire semble autoriser l'accès.

## 17.4. Problème : l'utilisateur appartient au groupe, mais le droit n'est pas effectif

Examine les groupes :

```bash
id alice
```

Si le groupe vient d'être ajouté, une nouvelle session peut être nécessaire.

Vérifie aussi les permissions :

```bash
ls -ld /srv/projets
```

Les ACL peuvent modifier les droits effectifs.

Si les outils ACL sont disponibles :

```bash
getfacl /srv/projets
```

Un groupe présent dans l'identité de l'utilisateur ne garantit pas qu'il obtiendra l'accès si les permissions du répertoire ou d'un élément parent l'empêchent.

## 17.5. Problème : un fichier appartient à un UID numérique inconnu

Exemple :

```text
-rw-r----- 1 1001 1005 2048 rapport.txt
```

Commence par rechercher les identifiants :

```bash
getent passwd 1001
getent group 1005
```

Si aucune correspondance n'existe, il peut s'agir d'un ancien compte supprimé ou d'une identité qui provient d'une autre source.

Ne change pas immédiatement le propriétaire.

Il faut d'abord déterminer l'origine du fichier et savoir quel compte ou service doit en être responsable.

## 17.6. Problème : un utilisateur a perdu ses accès après une modification

Examiner le compte :

```bash
id alice
getent passwd alice
```

Vérifier les groupes supplémentaires :

```bash
groups alice
```

Vérifier les permissions des fichiers concernés :

```bash
ls -l /chemin/du/fichier
namei -l /chemin/du/fichier
```

Rechercher les changements récents et confirmer si le groupe principal ou la liste des groupes supplémentaires a été modifié.

Une commande `usermod -G` exécutée sans `-a` peut avoir remplacé la liste précédente des groupes supplémentaires.

## 17.7. Problème : un répertoire personnel n'existe pas

Vérifie le chemin déclaré :

```bash
getent passwd alice
```

Puis vérifie le système de fichiers :

```bash
ls -ld /home/alice
```

Si le répertoire manque, ne crée pas immédiatement un répertoire vide sans examiner la situation.

Il faut déterminer si :

- La création du répertoire a été omise.
- Le répertoire est situé ailleurs.
- Un volume contenant `/home` n'est pas monté.
- Des données doivent être restaurées.
- Le compte utilise une source d'identité distante.

Le répertoire personnel est parfois hébergé sur un stockage séparé.

## 17.8. Problème : `sudo` refuse la commande

Vérifie les droits :

```bash
sudo -l
```

Examine les groupes :

```bash
id
```

Ne donne pas automatiquement des privilèges complets au compte pour contourner le problème.

Il faut déterminer :

- Quelle commande doit être autorisée.
- Pourquoi elle est refusée.
- Quelle règle de sécurité s'applique.
- Si une modification de la politique est réellement nécessaire.


# 18. Laboratoires pratiques guidés

Les laboratoires suivants doivent être réalisés sur une machine de test.

Si tu travailles sur une machine utilisée par d'autres personnes, ne supprime pas de comptes et ne modifie pas les groupes sans autorisation.

## Laboratoire 1 — Explorer les comptes du système

### Objectif

Comprendre les informations associées aux utilisateurs.

### Étape 1 : afficher les comptes locaux

```bash
cat /etc/passwd
```

### Étape 2 : afficher seulement les noms

```bash
cut -d: -f1 /etc/passwd
```

### Étape 3 : rechercher un compte courant

```bash
id
```

### Étape 4 : examiner les groupes

```bash
getent group
```

### Étape 5 : examiner les répertoires personnels déclarés

```bash
getent passwd | cut -d: -f1,6
```

### Travail demandé

Choisis trois comptes et relève :

- Le nom.
- L'UID.
- Le GID principal.
- Le répertoire personnel.
- Le shell déclaré.
- Les groupes supplémentaires lorsqu'ils sont disponibles.

### Résultat attendu

Tu dois savoir expliquer les différences entre un compte humain, un compte de service et le compte root.


## Laboratoire 2 — Créer un utilisateur de test

### Objectif

Créer un compte humain et vérifier son identité.

### Étape 1 : confirmer que le nom est disponible

```bash
getent passwd userlab
```

Si le compte existe déjà, choisis un autre nom de test.

### Étape 2 : créer le compte

```bash
sudo useradd -m -s /bin/bash userlab
```

### Étape 3 : définir le mot de passe

```bash
sudo passwd userlab
```

### Étape 4 : examiner l'identité

```bash
id userlab
getent passwd userlab
```

### Étape 5 : vérifier le répertoire personnel

```bash
ls -ld /home/userlab
```

### Étape 6 : examiner les fichiers de départ

```bash
ls -la /home/userlab
```

### Résultat attendu

Le compte doit exister et son répertoire personnel doit être présent si l'opération a réussi.

### Critère de validation

Tu dois pouvoir expliquer l'UID, le GID principal, le shell et le répertoire personnel du compte créé.


## Laboratoire 3 — Créer un groupe et y ajouter des utilisateurs

### Objectif

Mettre en place un groupe de travail.

### Étape 1 : créer le groupe

```bash
sudo groupadd labprojets
```

Si le groupe existe déjà, vérifie son identité et sa configuration au lieu de le recréer.

### Étape 2 : ajouter le compte de test

```bash
sudo usermod -aG labprojets userlab
```

### Étape 3 : vérifier l'appartenance

```bash
id userlab
groups userlab
```

### Étape 4 : examiner l'entrée du groupe

```bash
getent group labprojets
```

### Travail demandé

Explique pourquoi `-aG` est utilisé et pourquoi `-G` seul pourrait avoir des conséquences inattendues.

### Résultat attendu

Le compte `userlab` doit apparaître dans les groupes qui lui sont attribués.


## Laboratoire 4 — Créer un répertoire partagé

### Objectif

Utiliser un groupe pour contrôler l'accès à un répertoire.

### Étape 1 : créer le répertoire

```bash
sudo mkdir -p /srv/labprojets
```

### Étape 2 : attribuer le groupe

```bash
sudo chown root:labprojets /srv/labprojets
```

### Étape 3 : appliquer les permissions

```bash
sudo chmod 2770 /srv/labprojets
```

### Étape 4 : vérifier

```bash
ls -ld /srv/labprojets
getfacl /srv/labprojets
```

### Étape 5 : tester l'accès de l'utilisateur

```bash
sudo -u userlab -- test -x /srv/labprojets
echo $?
```

### Étape 6 : tester l'écriture

```bash
sudo -u userlab -- touch /srv/labprojets/test-userlab.txt
```

### Étape 7 : vérifier le fichier

```bash
ls -l /srv/labprojets
```

### Résultat attendu

L'utilisateur doit pouvoir effectuer le test de traversée et créer un fichier si les groupes et permissions sont correctement configurés.

### Critère de validation

Tu dois être capable d'expliquer le rôle du groupe et celui du bit SGID.


## Laboratoire 5 — Modifier les informations d'un utilisateur

### Objectif

Changer le shell de connexion et examiner le résultat.

### Étape 1 : relever l'état initial

```bash
getent passwd userlab
```

### Étape 2 : changer le shell

```bash
sudo usermod -s /bin/bash userlab
```

### Étape 3 : vérifier le résultat

```bash
getent passwd userlab
```

### Étape 4 : examiner les groupes

```bash
id userlab
```

### Travail demandé

Explique pourquoi il est nécessaire de vérifier le compte après la modification.

### Résultat attendu

Le champ du shell doit correspondre au changement demandé.


## Laboratoire 6 — Observer le verrouillage d'un mot de passe

### Objectif

Comprendre la différence entre mot de passe verrouillé et compte entièrement désactivé.

### Étape 1 : consulter l'état

```bash
sudo passwd -S userlab
```

### Étape 2 : verrouiller le mot de passe du compte de test

```bash
sudo passwd -l userlab
```

### Étape 3 : examiner l'état

```bash
sudo passwd -S userlab
```

### Étape 4 : déverrouiller si nécessaire

```bash
sudo passwd -u userlab
```

### Étape 5 : vérifier à nouveau

```bash
sudo passwd -S userlab
```

### Résultat attendu

Tu dois observer le changement d'état fourni par l'outil et comprendre que d'autres mécanismes d'accès peuvent nécessiter des vérifications complémentaires.

Ne réalise pas ce test sur un compte de production dont l'accès doit rester disponible.


## Laboratoire 7 — Inventorier les fichiers d'un utilisateur

### Objectif

Comprendre la relation entre un compte et les fichiers qui portent son UID.

### Étape 1 : identifier l'UID du compte de test

```bash
id -u userlab
```

### Étape 2 : créer quelques fichiers dans le répertoire personnel

```bash
sudo -u userlab -- touch /home/userlab/fichier1.txt
sudo -u userlab -- touch /home/userlab/fichier2.txt
```

### Étape 3 : rechercher les fichiers

```bash
sudo find /home -xdev -user userlab -type f -print
```

### Étape 4 : afficher les identifiants numériques d'un fichier

```bash
stat /home/userlab/fichier1.txt
```

### Résultat attendu

Tu dois pouvoir relier le propriétaire affiché au nom du compte et à son UID.


# 19. Exercices d'entraînement

Essaie de répondre aux questions avant de lire les corrections.

## Exercice 1 — UID

Que signifie l'UID `1001` dans la configuration d'un compte Linux ?

A. La taille du répertoire personnel.

B. L'identifiant numérique de l'utilisateur.

C. Le numéro du shell.

D. Le nombre de groupes du compte.

## Exercice 2 — Groupe principal

Quelle est la différence entre le groupe principal et les groupes supplémentaires ?

## Exercice 3 — Création d'utilisateur

Quelle commande demande la création d'un utilisateur `alice` avec un répertoire personnel et Bash comme shell ?

A. `sudo groupadd -m alice`

B. `sudo useradd -m -s /bin/bash alice`

C. `sudo passwd -m alice`

D. `sudo chown alice /home`

## Exercice 4 — Ajouter à un groupe

Pourquoi la commande suivante utilise-t-elle `-aG` ?

```bash
sudo usermod -aG developpeurs alice
```

## Exercice 5 — Fichier `/etc/shadow`

Pourquoi les informations d'authentification protégées ne sont-elles généralement pas conservées en clair dans un fichier lisible par tous les utilisateurs ?

## Exercice 6 — Mot de passe verrouillé

Vrai ou faux :

```bash
sudo passwd -l alice
```

garantit que toutes les méthodes d'accès d'Alice sont désactivées, y compris les clés SSH, toutes les sessions actives et tous les mécanismes externes.

Explique ta réponse.

## Exercice 7 — Permissions de groupe

Le répertoire `/srv/projets` appartient au groupe `developpeurs`.

Alice appartient à ce groupe, mais elle n'arrive pas à traverser le répertoire.

Quelles vérifications dois-tu effectuer ?

## Exercice 8 — Suppression de compte

Quelle est la différence entre :

```bash
sudo userdel alice
```

et :

```bash
sudo userdel -r alice
```

Pourquoi faut-il être prudent avec la seconde commande ?

## Exercice 9 — Compte de service

Pourquoi un service web devrait-il généralement fonctionner avec une identité dédiée plutôt qu'avec le compte root ?

## Exercice 10 — Informations de compte

Quelle commande permet d'afficher l'UID, le GID principal et les groupes d'un compte ?

A. `df -h`

B. `id alice`

C. `mkfs.ext4`

D. `mount`

## Exercice 11 — Répertoire personnel

Un utilisateur existe dans `/etc/passwd`, mais son répertoire personnel n'existe pas.

Peut-on conclure automatiquement que le compte est invalide ?

Explique les autres vérifications nécessaires.

## Exercice 12 — Privilèges

Un utilisateur doit seulement pouvoir écrire dans `/srv/projets`.

Est-il nécessaire de lui accorder systématiquement les droits administratifs complets avec `sudo` ?

Justifie ta réponse.


# 20. Défi final : administrer les utilisateurs d'une entreprise

## 20.1. Contexte professionnel

Tu es administrateur d'un serveur Linux utilisé par une petite équipe informatique.

L'entreprise veut organiser les comptes et les permissions afin de distinguer les utilisateurs, les développeurs et les opérations d'administration.

Tu dois mettre en place une organisation simple et documentée.

## 20.2. Besoins

Le serveur doit disposer des éléments suivants :

- Un utilisateur de laboratoire nommé `alice`.
- Un groupe `developpeurs`.
- Un utilisateur `bob` qui appartient également au groupe `developpeurs`.
- Un répertoire partagé `/srv/projets`.
- Des permissions permettant au groupe autorisé de travailler dans le répertoire.
- Une vérification des identités et des droits.
- Une procédure simple pour retirer un membre du groupe.
- Une procédure prudente de retrait d'un compte.
- Un contrôle des privilèges administratifs.

Ces comptes et le répertoire sont destinés au laboratoire. N'applique pas ces modifications à des comptes de production sans autorisation.

## 20.3. Mission 1 — Vérifier l'état initial

Exécute :

```bash
getent passwd alice
getent passwd bob
getent group developpeurs
```

Si un compte ou un groupe existe déjà, examine sa configuration avant de continuer.

**Validation :** tu dois connaître l'état initial et éviter de recréer des identités existantes sans raison.

## 20.4. Mission 2 — Créer le groupe

Si le groupe n'existe pas :

```bash
sudo groupadd developpeurs
```

Vérifie :

```bash
getent group developpeurs
```

**Validation :** le groupe doit être résolu par le système.

## 20.5. Mission 3 — Créer les utilisateurs

Créer Alice si elle n'existe pas :

```bash
sudo useradd -m -s /bin/bash alice
```

Créer Bob si nécessaire :

```bash
sudo useradd -m -s /bin/bash bob
```

Définir un mot de passe pour chacun si un accès par mot de passe est nécessaire :

```bash
sudo passwd alice
sudo passwd bob
```

**Validation :** les comptes doivent exister et les informations de base doivent être cohérentes.

## 20.6. Mission 4 — Ajouter les membres au groupe

```bash
sudo usermod -aG developpeurs alice
sudo usermod -aG developpeurs bob
```

Contrôler :

```bash
id alice
id bob
getent group developpeurs
```

**Validation :** les deux utilisateurs doivent posséder l'appartenance supplémentaire attendue.

## 20.7. Mission 5 — Créer le répertoire partagé

```bash
sudo mkdir -p /srv/projets
sudo chown root:developpeurs /srv/projets
sudo chmod 2770 /srv/projets
```

Contrôler :

```bash
ls -ld /srv/projets
getfacl /srv/projets
```

**Validation :** le groupe doit être `developpeurs` et le mode doit correspondre à la politique retenue.

## 20.8. Mission 6 — Tester l'accès

Tester la traversée :

```bash
sudo -u alice -- test -x /srv/projets
echo $?
```

Tester la création d'un fichier :

```bash
sudo -u alice -- touch /srv/projets/test-alice.txt
```

Effectuer un test similaire avec Bob :

```bash
sudo -u bob -- touch /srv/projets/test-bob.txt
```

Contrôler les fichiers :

```bash
ls -l /srv/projets
```

**Validation :** les deux utilisateurs doivent pouvoir effectuer les opérations autorisées et l'appartenance au groupe doit être vérifiée.

## 20.9. Mission 7 — Vérifier les privilèges

Pour le compte administrateur utilisé dans le laboratoire :

```bash
sudo -l
```

Pour Alice, examine son identité :

```bash
id alice
```

Ne lui accorde pas automatiquement de privilèges administratifs.

**Validation :** les utilisateurs doivent recevoir les droits correspondant à leurs responsabilités.

## 20.10. Mission 8 — Retirer un membre du groupe

Simule le retrait de Bob du groupe `developpeurs` :

```bash
sudo gpasswd -d bob developpeurs
```

Vérifie :

```bash
id bob
```

**Validation :** l'appartenance supplémentaire doit être retirée si cette opération correspond bien à l'état de départ.

## 20.11. Mission 9 — Préparer le retrait d'un compte

Avant de supprimer un compte, documente :

- Son UID.
- Ses groupes.
- Ses fichiers.
- Ses processus.
- Ses tâches planifiées éventuelles.
- Les données à conserver.
- Les accès externes à retirer.

Commandes utiles :

```bash
id alice
getent passwd alice
ps -u alice -f
sudo find /home -xdev -user alice -print
```

**Validation :** tu dois pouvoir expliquer les conséquences d'une suppression et choisir si les données doivent être archivées ou transférées.

## 20.12. Mission 10 — Produire un schéma final

Ton architecture devrait ressembler à ceci :

```text
                   SERVEUR LINUX
                         |
             +-----------+-----------+
             |                       |
             v                       v
           alice                    bob
             |                       |
             +-----------+-----------+
                         |
                         v
                  Groupe developpeurs
                         |
                         v
                    /srv/projets
                         |
                +--------+--------+
                |                 |
                v                 v
             Lecture            Écriture
            autorisée          autorisée
             au groupe          au groupe
```

Ajoute au schéma les UID, le GID du groupe et les permissions réellement constatées.

**Validation finale :** un autre administrateur doit pouvoir comprendre l'organisation des comptes, retrouver les groupes et vérifier les autorisations.


# 21. Correction détaillée du défi final

Cette correction illustre une procédure type. Les UID et GID sont ceux qui seront attribués par le système réel et doivent être relevés après les créations.

## 21.1. Créer le groupe

Si le groupe est absent :

```bash
sudo groupadd developpeurs
```

Vérifier :

```bash
getent group developpeurs
```

## 21.2. Créer les utilisateurs

Si Alice et Bob n'existent pas :

```bash
sudo useradd -m -s /bin/bash alice
sudo useradd -m -s /bin/bash bob
```

Configurer les mots de passe seulement si ce mode d'authentification est requis :

```bash
sudo passwd alice
sudo passwd bob
```

## 21.3. Ajouter les groupes supplémentaires

```bash
sudo usermod -aG developpeurs alice
sudo usermod -aG developpeurs bob
```

Vérifier :

```bash
id alice
id bob
```

Les identifiants numériques peuvent varier d'une machine à l'autre. Il faut les lire à partir du système au lieu de supposer une valeur.

## 21.4. Configurer le répertoire partagé

Créer le répertoire :

```bash
sudo mkdir -p /srv/projets
```

Définir le groupe :

```bash
sudo chown root:developpeurs /srv/projets
```

Appliquer les permissions :

```bash
sudo chmod 2770 /srv/projets
```

Vérifier :

```bash
ls -ld /srv/projets
```

Un résultat typique de mode peut ressembler à :

```text
drwxrws--- root developpeurs /srv/projets
```

Le résultat exact dépend de la configuration.

## 21.5. Tester les accès

Pour Alice :

```bash
sudo -u alice -- touch /srv/projets/test-alice.txt
```

Pour Bob :

```bash
sudo -u bob -- touch /srv/projets/test-bob.txt
```

Lister le contenu :

```bash
ls -l /srv/projets
```

Si le test échoue, examine les groupes, les permissions du chemin et les éventuelles ACL.

La réussite d'une seule commande ne prouve pas que tous les accès de l'application sont corrects ; elle démontre seulement le comportement de cette opération de test.

## 21.6. Retirer Bob du groupe

```bash
sudo gpasswd -d bob developpeurs
```

Vérifier :

```bash
id bob
```

Les processus déjà en cours peuvent conserver leur identité de groupe initiale. Une nouvelle session est généralement nécessaire pour observer le nouvel ensemble de groupes dans les processus de Bob.

## 21.7. Documenter la gestion des comptes

Le compte rendu devrait contenir :

```text
Nom du compte :
UID :
Groupe principal :
Groupes supplémentaires :
Répertoire personnel :
Shell :
Accès administratifs :
Date de création :
Responsable :
Données à conserver :
État du compte :
```

La documentation permet de gérer les modifications futures et de retirer proprement les accès lorsqu'ils ne sont plus nécessaires.


# 22. Checklist d'administration

## Avant de créer un compte

- [ ] Vérifier que le compte n'existe pas déjà.
- [ ] Définir le rôle du compte.
- [ ] Choisir un nom approprié.
- [ ] Déterminer le groupe principal.
- [ ] Identifier les groupes supplémentaires nécessaires.
- [ ] Définir le besoin de répertoire personnel.
- [ ] Définir le shell adapté.
- [ ] Déterminer le mode d'authentification.
- [ ] Vérifier les exigences de sécurité.
- [ ] Contrôler le résultat après création.

## Lors de l'ajout à un groupe

- [ ] Vérifier le groupe cible.
- [ ] Comprendre les droits associés au groupe.
- [ ] Utiliser `usermod -aG` pour ajouter un groupe supplémentaire sans remplacer les autres.
- [ ] Vérifier le résultat avec `id`.
- [ ] Prévoir une nouvelle session si nécessaire.
- [ ] Contrôler les permissions des ressources concernées.

## Lors d'une modification de compte

- [ ] Examiner l'état initial.
- [ ] Déterminer les effets secondaires.
- [ ] Modifier une propriété à la fois lorsque cela facilite le contrôle.
- [ ] Vérifier le compte après modification.
- [ ] Examiner les fichiers et services dépendants.
- [ ] Mettre à jour la documentation.

## Avant de supprimer un compte

- [ ] Vérifier la demande et l'autorisation.
- [ ] Identifier l'UID.
- [ ] Examiner les groupes.
- [ ] Examiner les processus.
- [ ] Rechercher les tâches et services dépendants.
- [ ] Identifier les fichiers à conserver.
- [ ] Préparer une sauvegarde si nécessaire.
- [ ] Révoquer les autres accès pertinents.
- [ ] Décider si le répertoire personnel doit être supprimé.
- [ ] Vérifier les fichiers restants.
- [ ] Documenter la suppression.

## Pour les privilèges administratifs

- [ ] Déterminer le besoin précis.
- [ ] Vérifier `sudo -l`.
- [ ] Éviter les privilèges globaux inutiles.
- [ ] Modifier la politique via les outils adaptés.
- [ ] Vérifier la configuration après modification.
- [ ] Retirer les privilèges lorsqu'ils ne sont plus nécessaires.


# 23. Fiche de révision et commandes essentielles

## 23.1. Identité et comptes

| Commande | Utilité |
|---|---|
| `id` | Afficher l'identité de l'utilisateur courant |
| `id alice` | Afficher UID, GID principal et groupes d'Alice |
| `groups alice` | Afficher les groupes d'un utilisateur |
| `getent passwd alice` | Rechercher les informations de compte |
| `getent group developpeurs` | Rechercher les informations d'un groupe |
| `who` | Afficher les sessions connues de l'outil |
| `w` | Afficher les sessions et leur activité |
| `last` | Examiner l'historique de connexion disponible |

## 23.2. Création et modification

| Commande | Utilité |
|---|---|
| `sudo useradd -m alice` | Créer un compte avec répertoire personnel |
| `sudo useradd -m -s /bin/bash alice` | Créer un compte avec Bash comme shell |
| `sudo usermod -aG developpeurs alice` | Ajouter un groupe supplémentaire |
| `sudo usermod -g developpeurs alice` | Changer le groupe principal |
| `sudo usermod -s /bin/bash alice` | Modifier le shell de connexion |
| `sudo usermod -l alice2 alice` | Changer le nom de connexion |
| `sudo groupadd developpeurs` | Créer un groupe |
| `sudo groupmod ...` | Modifier les attributs d'un groupe |
| `sudo gpasswd -d alice developpeurs` | Retirer un utilisateur du groupe indiqué |

## 23.3. Mots de passe et expiration

| Commande | Utilité |
|---|---|
| `passwd` | Modifier le mot de passe de l'utilisateur courant |
| `sudo passwd alice` | Définir le mot de passe d'Alice |
| `sudo passwd -S alice` | Consulter l'état synthétique du mot de passe |
| `sudo passwd -l alice` | Verrouiller le mot de passe selon le mécanisme local |
| `sudo passwd -u alice` | Déverrouiller le mot de passe selon le mécanisme local |
| `sudo chage -l alice` | Consulter les informations d'expiration |
| `sudo chage -d 0 alice` | Demander un changement de mot de passe à la prochaine authentification compatible |

## 23.4. Répertoires et permissions

| Commande | Utilité |
|---|---|
| `ls -ld /home/alice` | Vérifier les propriétés du répertoire personnel |
| `stat fichier.txt` | Examiner les métadonnées d'un fichier |
| `sudo chown alice:developpeurs fichier.txt` | Modifier le propriétaire et le groupe |
| `sudo chgrp developpeurs fichier.txt` | Modifier le groupe d'un fichier |
| `sudo chmod 2770 /srv/projets` | Définir les permissions de partage de groupe avec SGID |
| `namei -l /srv/projets` | Examiner les permissions de chaque composant du chemin |
| `getfacl /srv/projets` | Lire les ACL lorsque l'outil est disponible |

## 23.5. Privilèges et diagnostic

| Commande | Utilité |
|---|---|
| `sudo -l` | Consulter les privilèges sudo du compte courant |
| `id alice` | Vérifier l'identité et les groupes |
| `ps -u alice -f` | Examiner les processus associés au compte |
| `sudo find /home -xdev -user alice -print` | Rechercher les fichiers appartenant à Alice dans `/home` |
| `getent passwd 1001` | Rechercher un compte par UID dans les sources configurées |
| `getent group 1005` | Rechercher un groupe par GID dans les sources configurées |

## 23.6. Suppression et gestion prudente

| Commande | Utilité |
|---|---|
| `sudo userdel alice` | Supprimer le compte local sans demander la suppression du répertoire personnel |
| `sudo userdel -r alice` | Demander également la suppression du répertoire personnel et du répertoire de messagerie local associé, selon la configuration |
| `sudo gpasswd -d alice developpeurs` | Retirer un utilisateur d'un groupe supplémentaire |
| `sudo find /home -xdev -uid 1001 -print` | Rechercher les fichiers associés à un UID numérique |

Les commandes de suppression doivent être précédées d'une vérification de l'identité, des fichiers et des dépendances du compte.


# 24. Conclusion

La gestion des utilisateurs et des groupes est une compétence fondamentale de l'administration Linux.

Elle permet de déterminer qui peut accéder au système, quelles ressources sont accessibles et quels privilèges chaque compte peut utiliser.

Dans ce cours, tu as appris à :

- Comprendre les utilisateurs humains et les comptes système.
- Expliquer les UID et les GID.
- Lire les informations des comptes et des groupes.
- Comprendre les fichiers `/etc/passwd`, `/etc/shadow`, `/etc/group` et `/etc/gshadow`.
- Rechercher des identités avec `getent`.
- Créer un utilisateur avec `useradd`.
- Gérer les mots de passe.
- Créer des groupes.
- Ajouter et retirer des groupes supplémentaires.
- Modifier les informations d'un compte.
- Comprendre le rôle des répertoires personnels.
- Désactiver ou supprimer un compte avec prudence.
- Relier les groupes aux permissions des fichiers.
- Comprendre le rôle de root et de `sudo`.
- Distinguer les comptes humains des comptes de service.
- Diagnostiquer les problèmes d'accès courants.

Le principe à retenir est le suivant :

```text
               UTILISATEUR
                    |
                    v
               IDENTITÉ UID
                    |
                    v
             GROUPES ET GID
                    |
                    v
             PERMISSIONS
                    |
                    v
             RESSOURCE CIBLE
                    |
                    v
            ACCÈS AUTORISÉ
            OU ACCÈS REFUSÉ
```

Cette représentation illustre le principe général. L'accès réel dépend également des ACL, des privilèges, des mécanismes d'authentification, des options de montage et d'autres contrôles éventuels.

**Une bonne administration ne consiste pas à donner le maximum de droits pour éviter les problèmes. Elle consiste à attribuer les droits nécessaires, à les vérifier et à les retirer lorsqu'ils ne sont plus justifiés.**

Le niveau suivant pourra approfondir la gestion des groupes, les ACL, les privilèges sudo, la gestion des comptes de service et les stratégies de sécurité des identités dans un environnement Linux partagé.