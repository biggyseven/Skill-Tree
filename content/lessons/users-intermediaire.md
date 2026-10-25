# Utilisateurs et groupes Linux — Niveau intermédiaire
## Authentification centralisée, LDAP, Active Directory, Kerberos, SSSD, PAM et gestion avancée des accès


# Sommaire

1. [Présentation du niveau intermédiaire](#1-présentation-du-niveau-intermédiaire)
2. [Comprendre l'architecture d'une authentification centralisée](#2-comprendre-larchitecture-dune-authentification-centralisée)
3. [LDAP : comprendre les annuaires et leur fonctionnement](#3-ldap--comprendre-les-annuaires-et-leur-fonctionnement)
4. [Active Directory : domaines, contrôleurs et services](#4-active-directory--domaines-contrôleurs-et-services)
5. [Kerberos : comprendre l'authentification par tickets](#5-kerberos--comprendre-lauthentification-par-tickets)
6. [NSS, PAM, SSSD, realmd et winbind : rôles et différences](#6-nss-pam-sssd-realmd-et-winbind--rôles-et-différences)
7. [Comprendre les UID, GID, SID et la correspondance des identités](#7-comprendre-les-uid-gid-sid-et-la-correspondance-des-identités)
8. [Préparer un serveur Linux à rejoindre un domaine Active Directory](#8-préparer-un-serveur-linux-à-rejoindre-un-domaine-active-directory)
9. [Intégrer Linux à Active Directory avec SSSD](#9-intégrer-linux-à-active-directory-avec-sssd)
10. [Configurer l'accès par groupes et contrôler les connexions](#10-configurer-laccès-par-groupes-et-contrôler-les-connexions)
11. [Intégrer Linux à un annuaire LDAP](#11-intégrer-linux-à-un-annuaire-ldap)
12. [Créer les répertoires personnels et gérer les sessions](#12-créer-les-répertoires-personnels-et-gérer-les-sessions)
13. [Groupes centralisés et permissions sur les fichiers](#13-groupes-centralisés-et-permissions-sur-les-fichiers)
14. [ACL : gérer des autorisations précises](#14-acl--gérer-des-autorisations-précises)
15. [sudo, délégation et séparation des privilèges](#15-sudo-délégation-et-séparation-des-privilèges)
16. [SSH et authentification centralisée](#16-ssh-et-authentification-centralisée)
17. [Cycle de vie des comptes et désactivation des accès](#17-cycle-de-vie-des-comptes-et-désactivation-des-accès)
18. [Comptes de service et gestion des identités techniques](#18-comptes-de-service-et-gestion-des-identités-techniques)
19. [Cache, disponibilité et fonctionnement hors ligne](#19-cache-disponibilité-et-fonctionnement-hors-ligne)
20. [Sécurité de l'authentification centralisée](#20-sécurité-de-lauthentification-centralisée)
21. [Audit et diagnostic avancé](#21-audit-et-diagnostic-avancé)
22. [Automatisation de la gestion des identités](#22-automatisation-de-la-gestion-des-identités)
23. [Laboratoires pratiques guidés](#23-laboratoires-pratiques-guidés)
24. [Exercices d'entraînement corrigés](#24-exercices-dentraînement-corrigés)
25. [Défi final : intégrer un serveur Linux au domaine d'une entreprise](#25-défi-final--intégrer-un-serveur-linux-au-domaine-dune-entreprise)
26. [Correction détaillée du défi final](#26-correction-détaillée-du-défi-final)
27. [Checklist opérationnelle](#27-checklist-opérationnelle)
28. [Fiche de révision](#28-fiche-de-révision)
29. [Documentation de référence](#29-documentation-de-référence)


# 1. Présentation du niveau intermédiaire

## 1.1. Objectif général

Au niveau débutant, nous avons appris à créer des utilisateurs Linux, à gérer les groupes locaux, à configurer les mots de passe et à comprendre les permissions classiques.

Ces compétences sont indispensables, mais elles deviennent difficiles à maintenir lorsqu'une entreprise utilise plusieurs dizaines de serveurs et plusieurs centaines de comptes.

Imaginons une organisation possédant :

- 80 serveurs Linux.
- 150 postes Windows.
- 120 collaborateurs.
- 4 équipes informatiques.
- Plusieurs applications internes.
- Des serveurs de fichiers et des bases de données.

Si chaque serveur Linux gère indépendamment ses propres utilisateurs, l'administration devient rapidement complexe.

Un même collaborateur peut posséder des comptes différents sur plusieurs machines. Ses droits peuvent diverger. Son départ peut nécessiter des interventions sur de nombreux serveurs.

C'est dans ce contexte qu'intervient l'authentification centralisée.

L'objectif de ce cours est d'apprendre à comprendre et administrer les composants qui permettent à un serveur Linux d'utiliser des identités provenant d'un annuaire central, notamment LDAP ou Active Directory.

Nous allons également approfondir :

- La résolution des utilisateurs et des groupes.
- Les mécanismes d'authentification Linux.
- Les relations entre LDAP et Kerberos.
- L'intégration d'un domaine Active Directory.
- L'utilisation de SSSD.
- La gestion des groupes et des autorisations.
- Les accès SSH.
- La délégation des privilèges avec `sudo`.
- Les ACL et les permissions des ressources partagées.
- Le cache des identités.
- Le dépannage des connexions centralisées.
- Le cycle de vie des comptes.
- La sécurité de l'ensemble de l'architecture.

## 1.2. Les prérequis

Avant de commencer, il faut maîtriser :

- Les commandes de base du shell.
- Les utilisateurs Linux.
- Les groupes et leurs identifiants.
- Les UID et GID.
- Les permissions de fichiers.
- `useradd`, `usermod` et `userdel`.
- `groupadd`, `groups` et `id`.
- Le fonctionnement général de `sudo`.
- Les bases du réseau IP.
- Les noms DNS et les adresses IP.
- Les connexions SSH.

Il est également utile de connaître les ports réseau et le rôle des services d'annuaire, même si ces notions seront réexpliquées.

## 1.3. Résultats attendus

À la fin du cours, tu dois pouvoir :

1. Expliquer la différence entre identité, authentification et autorisation.
2. Comprendre LDAP et la structure d'un annuaire.
3. Expliquer la différence entre LDAP et Active Directory.
4. Comprendre le rôle de Kerberos.
5. Distinguer NSS, PAM, SSSD, realmd et winbind.
6. Expliquer comment Linux représente un utilisateur issu d'un annuaire.
7. Préparer un serveur Linux pour rejoindre un domaine Active Directory.
8. Intégrer Linux à AD à l'aide de SSSD.
9. Comprendre l'intégration d'un client Linux à un annuaire LDAP.
10. Vérifier la résolution des utilisateurs et des groupes.
11. Limiter l'accès au serveur à des utilisateurs ou groupes autorisés.
12. Comprendre le rôle des ACL et de `sudo`.
13. Diagnostiquer les problèmes de DNS, Kerberos, LDAP, PAM et SSSD.
14. Préparer le retrait des accès d'un collaborateur.
15. Documenter une architecture d'authentification centralisée.

## 1.4. Environnement de laboratoire

Le cours utilise le domaine fictif suivant :

```text
Domaine DNS       : ad.example.test
Royaume Kerberos  : AD.EXAMPLE.TEST
Contrôleur AD     : dc01.ad.example.test
Serveur Linux     : linux01.ad.example.test
Utilisateur       : alice
Groupe            : Linux-Admins
```

Ces noms sont des exemples réservés à la documentation. Ils doivent être remplacés par les valeurs de ton laboratoire.

Une architecture recommandée est :

```text
                    LABORATOIRE
                         |
              +----------+----------+
              |                     |
              v                     v
       Contrôleur AD             Serveur Linux
       dc01                      linux01
              |                     |
              v                     v
       Annuaire central       Client SSSD
       Kerberos               NSS et PAM
              |                     |
              +----------+----------+
                         |
                         v
                Utilisateur alice
```

Le contrôleur Active Directory doit déjà fonctionner pour les laboratoires d'intégration AD.

Pour les exercices LDAP, il faut disposer d'un serveur LDAP fonctionnel et d'informations de connexion fournies par l'administrateur du laboratoire.

**Important :** les manipulations d'intégration centralisée doivent être réalisées sur une machine de test ou pendant une fenêtre de maintenance autorisée. Une erreur de configuration de PAM, SSH ou SSSD peut empêcher l'ouverture de nouvelles sessions.


# 2. Comprendre l'architecture d'une authentification centralisée

## 2.1. Les trois questions fondamentales

Avant d'étudier les protocoles, distinguons trois concepts.

### Identité

L'identité répond à la question :

**Qui est cet utilisateur ?**

Exemple :

```text
Nom de connexion : alice
Identifiant Linux : UID attribué au compte
Groupes : developpeurs, audit
Répertoire personnel : /home/alice
```

Ces informations permettent au système de représenter le compte.

### Authentification

L'authentification répond à la question :

**Comment vérifier que cet utilisateur est bien celui qu'il prétend être ?**

Cela peut passer par un mot de passe, un mécanisme Kerberos, une clé SSH, un certificat ou une autre méthode prise en charge.

### Autorisation

L'autorisation répond à la question :

**Quelles opérations cet utilisateur a-t-il le droit d'effectuer ?**

Un utilisateur peut être correctement authentifié mais ne pas avoir le droit de lire un fichier ou de se connecter à un serveur particulier.

Les permissions Unix, les ACL, les politiques SSH, les règles `sudo` et les mécanismes de contrôle d'accès peuvent intervenir à ce niveau.

## 2.2. Un exemple concret

Alice est membre de l'équipe de développement.

Elle veut ouvrir une session SSH sur un serveur Linux et accéder à un répertoire de projet.

```text
Alice
  |
  v
Tentative de connexion SSH
  |
  v
Vérification de l'identité
  |
  v
Authentification
  |
  v
Contrôle d'accès au serveur
  |
  v
Ouverture éventuelle de la session
  |
  v
Vérification des permissions du projet
```

Plusieurs éléments interviennent.

Le serveur SSH prend en charge la connexion distante.

PAM peut participer à la chaîne d'authentification et de contrôle de compte utilisée par le service.

SSSD peut interroger l'annuaire et effectuer les vérifications prévues par sa configuration.

NSS permet au système de résoudre le nom d'Alice, son UID et ses groupes.

Les permissions Unix et les ACL déterminent ensuite son accès aux fichiers.

Une erreur à l'une de ces étapes peut entraîner un refus, même si les autres composants fonctionnent correctement.

## 2.3. Sans centralisation

Dans une organisation entièrement locale :

```text
              Administrateur
                    |
          +---------+---------+
          |                   |
          v                   v
      Serveur A            Serveur B
          |                   |
          v                   v
      /etc/passwd          /etc/passwd
      /etc/group           /etc/group
      /etc/shadow          /etc/shadow
          |                   |
          v                   v
    Comptes locaux      Comptes locaux
```

Alice peut posséder un compte local sur chaque serveur.

Si son mot de passe, son UID ou ses groupes diffèrent entre les machines, son expérience et ses autorisations peuvent devenir incohérentes.

Lorsqu'elle quitte l'entreprise, les comptes doivent être désactivés partout où ils existent, à moins qu'une solution de gestion locale centralisée ne coordonne déjà ces opérations.

## 2.4. Avec centralisation

Avec un annuaire central :

```text
                 Annuaire central
                  Utilisateurs
                    Groupes
                 Attributs et règles
                         |
                +--------+--------+
                |                 |
                v                 v
            Serveur A         Serveur B
                |                 |
                v                 v
             SSSD/PAM          SSSD/PAM
                |                 |
                v                 v
             Linux local      Linux local
```

Les serveurs peuvent utiliser les identités centralisées.

L'administrateur peut donc gérer les utilisateurs et les groupes dans une source commune.

Mais le serveur Linux conserve toujours ses propres politiques locales : permissions des fichiers, configuration SSH, règles `sudo`, services et restrictions spécifiques.

La centralisation ne signifie pas que toutes les autorisations sont automatiquement identiques partout.

## 2.5. Ce que la centralisation apporte

Une architecture centralisée peut faciliter :

- La gestion du cycle de vie des comptes.
- La cohérence des groupes.
- La révocation des accès.
- L'application de règles d'accès communes.
- L'intégration des serveurs Linux et Windows.
- L'audit des identités.
- La réduction des opérations manuelles.

Elle introduit cependant des dépendances :

- Réseau.
- DNS.
- Annuaire.
- Synchronisation de l'heure, selon les protocoles employés.
- Certificats et confiance TLS.
- Kerberos, dans les architectures qui l'utilisent.
- Configuration du client Linux.
- Gestion du cache.
- Disponibilité des services centraux.

Un annuaire mal configuré peut donc affecter plusieurs machines simultanément.


# 3. LDAP : comprendre les annuaires et leur fonctionnement

## 3.1. Définition de LDAP

LDAP signifie *Lightweight Directory Access Protocol*.

Il s'agit d'un protocole qui permet aux clients de communiquer avec des services d'annuaire.

LDAP n'est pas, à lui seul, un produit serveur précis ni une solution complète de gestion des connexions Linux.

Il définit notamment la manière dont un client peut rechercher des entrées, lire leurs attributs et effectuer certaines opérations d'annuaire.

La spécification du protocole est décrite notamment dans la RFC 4511.

Documentation :

https://www.rfc-editor.org/rfc/rfc4511

## 3.2. Qu'est-ce qu'un annuaire ?

Un annuaire stocke des informations organisées autour d'objets.

Par exemple :

```text
Entreprise
   |
   +-- Informatique
   |      |
   |      +-- Alice
   |      +-- Bob
   |
   +-- Audit
          |
          +-- Claire
```

Dans un annuaire LDAP réel, les entrées ne sont pas simplement des lignes dans une liste.

Elles sont organisées selon une structure qui possède des noms distincts et des attributs.

Un annuaire peut contenir des utilisateurs, des groupes, des ordinateurs, des services ou d'autres objets, selon son schéma.

## 3.3. Entrée LDAP

Une entrée LDAP représente un objet.

Exemple illustratif :

```text
dn: uid=alice,ou=People,dc=example,dc=test
objectClass: inetOrgPerson
uid: alice
cn: Alice Martin
sn: Martin
mail: alice@example.test
```

Cette entrée décrit une identité nommée Alice.

Elle possède des attributs tels que :

- `uid` : identifiant de connexion dans ce modèle.
- `cn` : nom commun.
- `sn` : nom de famille.
- `mail` : adresse électronique.
- `objectClass` : classes qui définissent la nature de l'objet et les attributs autorisés.

Les attributs exacts dépendent du schéma LDAP utilisé.

## 3.4. DN : Distinguished Name

Le DN est le nom distinctif d'une entrée dans l'annuaire.

Exemple :

```text
uid=alice,ou=People,dc=example,dc=test
```

Le DN indique la position de l'entrée dans l'arborescence de l'annuaire.

On peut le lire conceptuellement ainsi :

```text
dc=example,dc=test
          |
          v
        ou=People
          |
          v
       uid=alice
```

Le DN identifie l'entrée dans le contexte de l'annuaire.

Il ne faut pas confondre le DN avec le simple nom de connexion `alice`.

## 3.5. RDN : Relative Distinguished Name

Le RDN désigne un composant relatif du DN.

Dans :

```text
uid=alice,ou=People,dc=example,dc=test
```

le RDN le plus proche de l'entrée est :

```text
uid=alice
```

Le DN complet identifie l'entrée dans l'annuaire, tandis que le RDN décrit un élément relatif à son emplacement.

## 3.6. OU : Organizational Unit

OU signifie *Organizational Unit*.

Une OU est une unité d'organisation fréquemment utilisée pour structurer des objets dans un annuaire.

Exemple :

```text
dc=example,dc=test
       |
       +-- ou=People
       |      |
       |      +-- uid=alice
       |      +-- uid=bob
       |
       +-- ou=Groups
              |
              +-- cn=Developpeurs
              +-- cn=Audit
```

Cette organisation est illustrative.

Une OU permet de structurer des entrées, mais elle ne constitue pas automatiquement un mécanisme universel d'autorisation.

Les droits d'accès aux objets dépendent des règles de sécurité de l'annuaire.

## 3.7. Base DN

La base DN est la racine à partir de laquelle une recherche LDAP est effectuée.

Exemple :

```text
dc=example,dc=test
```

Une recherche dont la base est :

```text
ou=People,dc=example,dc=test
```

se limite à cette branche et à ses descendants selon le type de recherche choisi.

Le choix de la base influence les entrées qui pourront être trouvées.

## 3.8. DC : composant de DN ou contrôleur de domaine ?

Dans un nom LDAP, `dc` signifie *Domain Component*.

Exemple :

```text
dc=example,dc=test
```

Mais dans Active Directory, l'abréviation DC désigne également un *Domain Controller*, ou contrôleur de domaine.

Ces deux usages n'ont pas le même sens.

```text
dc=example,dc=test
   |
   +-- Composants du DN LDAP

DC Windows
   |
   +-- Serveur qui participe au domaine
```

La signification doit être interprétée selon le contexte.

## 3.9. Schéma LDAP

Le schéma définit les types d'objets et les attributs autorisés.

Par exemple, une entrée d'utilisateur peut utiliser des classes comme `inetOrgPerson` ou `posixAccount`, selon l'architecture.

Une entrée destinée à être interprétée par Linux doit fournir, directement ou au moyen d'un mécanisme de correspondance, les informations nécessaires à son utilisation comme compte Unix.

Ces informations peuvent inclure :

- UID numérique.
- GID numérique.
- Répertoire personnel.
- Shell.
- Nom de compte.

Tous les annuaires ne possèdent pas les mêmes attributs Unix.

Il faut donc connaître le schéma de l'annuaire avant de configurer le client Linux.

## 3.10. Exemple d'utilisateur LDAP compatible avec POSIX

Une entrée illustrative peut ressembler à ceci :

```ldif
dn: uid=alice,ou=People,dc=example,dc=test
objectClass: inetOrgPerson
objectClass: posixAccount
uid: alice
cn: Alice Martin
sn: Martin
uidNumber: 20001
gidNumber: 20010
homeDirectory: /home/alice
loginShell: /bin/bash
```

Cette entrée illustre les attributs nécessaires à un compte de type Unix.

Les attributs :

- `uidNumber` fournissent l'UID.
- `gidNumber` fournissent le GID principal.
- `homeDirectory` indique le répertoire personnel.
- `loginShell` indique le shell de connexion.

Cette entrée n'est pas une configuration universelle. Elle dépend du schéma utilisé par le serveur LDAP.

Dans un environnement de laboratoire, les identifiants numériques doivent être uniques et cohérents avec ceux des autres comptes de l'infrastructure.

## 3.11. Exemple de groupe LDAP compatible avec POSIX

Avec un schéma classique de type RFC2307, un groupe peut ressembler à ceci :

```ldif
dn: cn=Developpeurs,ou=Groups,dc=example,dc=test
objectClass: posixGroup
cn: Developpeurs
gidNumber: 20010
memberUid: alice
```

Le GID du groupe est fourni par `gidNumber`.

L'attribut `memberUid` référence ici un utilisateur par son identifiant de compte.

D'autres schémas, notamment RFC2307bis, peuvent représenter les membres autrement, par exemple en utilisant des DN.

C'est pourquoi le choix du schéma doit être cohérent entre le serveur LDAP et le client SSSD.

## 3.12. Bind LDAP

Le *Bind* est une opération LDAP utilisée pour établir l'identité et le contexte d'accès du client dans une session d'annuaire.

Plusieurs modes sont possibles, selon le serveur et le mécanisme utilisé.

Dans une architecture LDAP classique, un client peut rechercher une entrée puis tenter une authentification associée à cette identité, selon la configuration du service.

Il faut toutefois éviter de confondre :

- Une connexion réseau au serveur LDAP.
- La recherche d'un utilisateur.
- L'authentification de cet utilisateur.
- La décision de l'autoriser à ouvrir une session Linux.

Ce sont des étapes distinctes.

## 3.13. Recherche LDAP

La commande `ldapsearch` permet d'effectuer des recherches dans un annuaire lorsque le paquet correspondant est installé.

Exemple de recherche :

```bash
ldapsearch -x \
  -H ldaps://ldap01.example.test \
  -b "dc=example,dc=test" \
  "(uid=alice)" \
  uid cn uidNumber gidNumber
```

Cette commande suppose notamment :

- Que le serveur est joignable.
- Que le serveur TLS est correctement configuré.
- Que le certificat est approuvé par le client.
- Que les autorisations permettent la recherche demandée.
- Que le serveur possède un attribut `uid` correspondant au modèle utilisé.

L'option `-x` demande une authentification simple plutôt qu'un mécanisme SASL.

Cette recherche peut fonctionner sans authentification explicite si le serveur autorise la lecture anonyme des attributs demandés. Ce n'est pas une obligation.

Si le serveur exige une identité de lecture, utilise un compte technique en lecture seule et un mécanisme sécurisé pour fournir ses informations d'authentification. Ne place pas un secret en clair dans un script partagé.

## 3.14. LDAP, TLS et chiffrement

LDAP doit être configuré avec une protection du transport adaptée.

Deux modes courants sont :

- LDAP avec StartTLS.
- LDAP directement sur TLS, traditionnellement appelé LDAPS.

Les ports fréquemment utilisés sont :

| Mode | Port courant |
|---|---:|
| LDAP | TCP 389 |
| LDAP avec StartTLS | TCP 389 |
| LDAP sur TLS | TCP 636 |

Ces valeurs sont des usages courants, pas une garantie que chaque environnement utilise ces ports.

La présence de TLS ne suffit pas : le client doit également valider le certificat du serveur.

Il faut vérifier :

- La confiance accordée à l'autorité de certification.
- Le nom DNS utilisé pour contacter le serveur.
- La validité temporelle du certificat.
- La date et l'heure du client.
- Les règles de confiance configurées.

Ne désactive pas la validation du certificat pour faire disparaître une erreur de connexion. Identifie la cause et corrige la configuration de confiance.

## 3.15. LDAP seul ne fournit pas toute l'architecture Linux

Un serveur LDAP peut fournir les informations d'utilisateur et de groupe.

Mais l'intégration d'une identité à Linux exige que le système puisse :

1. Trouver l'utilisateur.
2. Connaître son UID et ses groupes.
3. Vérifier l'authentification.
4. Appliquer la politique d'accès.
5. Créer ou trouver son répertoire personnel.
6. Établir une session.
7. Appliquer les permissions aux ressources.

Des composants Linux tels que NSS, PAM et SSSD permettent d'assurer ces fonctions, selon la configuration.

C'est ce que nous allons étudier dans les sections suivantes.


# 4. Active Directory : domaines, contrôleurs et services

## 4.1. Définition d'Active Directory

Active Directory peut désigner plusieurs produits et services Microsoft.

Dans le contexte des domaines d'entreprise traditionnels, le service généralement concerné est **Active Directory Domain Services (AD DS)**.

AD DS est un service d'annuaire qui permet notamment de gérer les utilisateurs, les groupes, les ordinateurs, les domaines et les relations d'approbation.

Il s'intègre à plusieurs mécanismes de sécurité et de découverte de services, notamment LDAP, Kerberos et DNS.

Documentation officielle :

https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/active-directory-domain-services-overview

## 4.2. Le domaine Active Directory

Un domaine regroupe logiquement des objets et des identités administrés dans une même structure d'annuaire.

Exemple fictif :

```text
Domaine : ad.example.test
|
+-- Utilisateurs
|      |
|      +-- alice
|      +-- bob
|      +-- claire
|
+-- Groupes
|      |
|      +-- Linux-Admins
|      +-- Developpeurs
|      +-- Audit
|
+-- Ordinateurs
       |
       +-- LINUX01
       +-- WINDOWS01
       +-- WINDOWS02
```

Les utilisateurs et les groupes peuvent être créés et gérés par les administrateurs du domaine.

Les machines intégrées au domaine peuvent s'appuyer sur ces identités, selon leur configuration et les mécanismes d'intégration employés.

## 4.3. Le contrôleur de domaine

Un contrôleur de domaine, ou DC (*Domain Controller*), est un serveur qui participe au fonctionnement du domaine Active Directory.

Il fournit notamment des services liés à l'annuaire et à l'authentification.

Dans une architecture courante :

```text
                  Domaine AD
                      |
              +-------+-------+
              |               |
              v               v
            DC01            DC02
              |               |
              +-------+-------+
                      |
                      v
               Clients Linux
               et Windows
```

Plusieurs contrôleurs peuvent contribuer à la disponibilité du domaine.

La disponibilité réelle dépend néanmoins de la réplication, du réseau, du DNS et des autres composants de l'infrastructure.

## 4.4. Forêt Active Directory

Une forêt est une structure de niveau supérieur qui regroupe un ou plusieurs domaines Active Directory partageant une organisation logique, un schéma et d'autres éléments communs.

Exemple conceptuel :

```text
                 Forêt AD
                     |
          +----------+----------+
          |                     |
          v                     v
     ad.example.test       eu.example.test
          |                     |
          v                     v
      Utilisateurs           Utilisateurs
      et machines            et machines
```

Cette structure est illustrative.

Les relations entre domaines et les règles d'accès dépendent de la configuration de la forêt et de ses relations d'approbation.

Un serveur Linux peut devoir résoudre des identités provenant de plusieurs domaines approuvés. Cela a des conséquences sur les noms de connexion et la correspondance des identifiants.

## 4.5. OU et objets Active Directory

Une OU (*Organizational Unit*) permet d'organiser les objets dans un domaine.

Elle peut aussi servir de cible à certaines délégations administratives et politiques.

Exemple :

```text
ad.example.test
      |
      +-- OU=Linux
      |      |
      |      +-- LINUX01
      |      +-- LINUX02
      |
      +-- OU=Users
      |      |
      |      +-- Alice
      |      +-- Bob
      |
      +-- OU=Groups
             |
             +-- Linux-Admins
             +-- Linux-Users
```

La structure réelle dépend du modèle d'administration.

Une OU ne constitue pas automatiquement un groupe de permissions Unix. Il faut comprendre la manière dont les groupes et les règles d'accès sont configurés.

## 4.6. DNS et découverte des services AD

DNS joue un rôle central dans Active Directory.

Le client doit pouvoir localiser les services du domaine.

Des enregistrements DNS SRV permettent notamment de découvrir certains services LDAP et Kerberos.

Exemples de recherches :

```bash
dig SRV _ldap._tcp.ad.example.test
dig SRV _kerberos._tcp.ad.example.test
```

Si `dig` n'est pas installé, utilise l'outil équivalent disponible sur la machine ou installe le paquet DNS correspondant à la distribution.

Le nom `ad.example.test` doit correspondre au domaine de laboratoire réel.

Un serveur Linux qui utilise les mauvais résolveurs DNS peut échouer à découvrir les contrôleurs de domaine, même si une adresse IP de contrôleur est connue.

**Dans une intégration AD, le DNS est une dépendance de premier ordre.**

Il ne suffit pas de renseigner uniquement l'adresse IP du contrôleur dans un fichier local.

## 4.7. Kerberos dans Active Directory

Kerberos est un protocole d'authentification réseau utilisant un système de tickets.

Dans Active Directory, un service Kerberos est fourni dans l'architecture du domaine.

Une authentification Kerberos permet notamment à un client d'obtenir des tickets qui seront utilisés pour accéder à des services autorisés.

Le mécanisme réduit le besoin d'envoyer le mot de passe de l'utilisateur à chaque service.

Nous détaillerons ce fonctionnement dans la prochaine section.

## 4.8. SID : Security Identifier

Active Directory utilise des identifiants de sécurité Windows appelés SID.

Un SID peut prendre une forme telle que :

```text
S-1-5-21-123456789-234567890-345678901-1105
```

Cette valeur est fictive et sert uniquement à illustrer la structure d'un identifiant.

Le SID n'est pas un UID Linux.

Le système Linux doit obtenir ou calculer une représentation POSIX compatible pour utiliser l'identité dans les permissions Unix.

Cette correspondance peut être gérée automatiquement par SSSD ou par d'autres mécanismes selon l'architecture.

## 4.9. UPN et SAMAccountName

Active Directory propose plusieurs noms de connexion.

Le `sAMAccountName` est un nom de compte utilisé dans les environnements AD classiques.

L'UPN (*User Principal Name*) est un nom de connexion de type :

```text
alice@ad.example.test
```

La forme de connexion dépend des règles du domaine et de l'intégration Linux.

Un serveur utilisant SSSD avec des noms pleinement qualifiés peut demander un identifiant du type :

```text
alice@ad.example.test
```

Un environnement configuré différemment peut accepter une forme plus courte.

Il faut vérifier le comportement réel du serveur plutôt que supposer que le nom de connexion est toujours le même partout.

## 4.10. Group Policy et ADSys

Active Directory fournit des mécanismes de stratégie de groupe dans les environnements Windows.

Sur Linux, le fait de rejoindre le domaine ne signifie pas que toutes les stratégies Windows sont appliquées automatiquement.

Des composants complémentaires, tels qu'ADSys dans certains environnements Ubuntu, peuvent fournir des fonctions de gestion des politiques de domaine compatibles avec Linux.

Il faut distinguer :

- L'intégration du compte.
- L'authentification.
- L'autorisation d'accès au serveur.
- L'application des stratégies de groupe.
- La gestion des permissions Linux.

Ces fonctions ne sont pas identiques.

## 4.11. Active Directory n'est pas la même chose que Microsoft Entra ID

Microsoft Entra ID est un service d'identité cloud distinct d'Active Directory Domain Services.

Les deux peuvent être intégrés dans une architecture d'entreprise, mais ils ne sont pas interchangeables.

L'intégration d'un serveur Linux à un domaine AD DS traditionnel à l'aide de `realmd` et SSSD n'est pas la même opération qu'une inscription d'un appareil dans Microsoft Entra ID.

Il faut choisir une méthode d'intégration correspondant au service réellement utilisé par l'entreprise.

## 4.12. Comparaison LDAP et Active Directory

| Élément | LDAP | Active Directory Domain Services |
|---|---|---|
| Nature | Protocole d'accès à un annuaire | Service d'annuaire |
| Fonction principale | Rechercher et manipuler des entrées selon les droits | Organiser et administrer les objets d'un domaine |
| Utilisateurs et groupes | Dépendent du schéma du serveur | Objets d'annuaire AD |
| Authentification | Peut participer à certains mécanismes | Intègre notamment Kerberos |
| DNS | N'est pas fourni par LDAP lui-même | DNS est essentiel à la découverte de services AD |
| Identifiants Windows SID | Pas une fonction générale du protocole | Utilisés par AD pour identifier les objets de sécurité |
| Intégration Linux | Généralement avec SSSD ou d'autres clients | SSSD, winbind ou autre mécanisme adapté |
| Un mot de passe unique sur plusieurs machines | Possible selon l'architecture | Possible selon l'intégration et les politiques |

La distinction essentielle est la suivante :

**LDAP est un protocole. Active Directory Domain Services est un service d'annuaire qui utilise plusieurs technologies, dont LDAP et Kerberos.**


# 5. Kerberos : comprendre l'authentification par tickets

## 5.1. Définition

Kerberos est un protocole d'authentification réseau fondé sur des tickets et des clés cryptographiques.

Il permet à un utilisateur de prouver son identité à des services dans un environnement compatible, sans envoyer son mot de passe à chaque service.

Dans Active Directory, Kerberos est un élément important de l'authentification du domaine.

Documentation de référence du protocole :

https://www.rfc-editor.org/rfc/rfc4120

## 5.2. Pourquoi utiliser des tickets ?

Considérons un utilisateur qui souhaite accéder à plusieurs services :

```text
Alice
  |
  +-- Serveur de fichiers
  |
  +-- Service interne
  |
  +-- Autre ressource de domaine
```

Sans mécanisme de tickets, chaque service pourrait nécessiter une méthode d'authentification distincte.

Avec Kerberos, le client peut obtenir un ticket d'accès centralisé et des tickets de service selon le protocole.

Le mot de passe n'est pas simplement transmis au serveur de fichiers à chaque opération.

## 5.3. Les acteurs de Kerberos

Les composants fondamentaux comprennent :

- Le client.
- Le service auquel le client souhaite accéder.
- Le KDC (*Key Distribution Center*).

Le KDC comporte les fonctions d'authentification et d'émission des tickets nécessaires au fonctionnement Kerberos.

Schéma simplifié :

```text
               CLIENT
                  |
                  v
                 KDC
                  |
                  v
          Ticket de service
                  |
                  v
              SERVICE
```

Le fonctionnement exact comprend plusieurs échanges cryptographiques et dépend de l'environnement.

Ce schéma illustre seulement le principe général.

## 5.4. Ticket TGT

Le TGT (*Ticket-Granting Ticket*) est un ticket permettant au client de demander d'autres tickets auprès du service de délivrance des tickets.

Il ne doit pas être confondu avec le mot de passe de l'utilisateur.

Le client obtient le TGT selon les mécanismes du protocole, puis peut solliciter des tickets de service autorisés.

## 5.5. Ticket de service

Lorsqu'un utilisateur souhaite accéder à un service, un ticket spécifique à ce service peut être demandé.

Exemple conceptuel :

```text
Alice
  |
  v
Obtention du TGT
  |
  v
Demande d'accès à un service
  |
  v
Demande d'un ticket de service
  |
  v
Présentation du ticket au service
  |
  v
Accès selon les règles applicables
```

Le ticket Kerberos ne garantit pas que toutes les opérations du service seront autorisées.

L'autorisation dépend également des permissions et des règles propres au service.

## 5.6. L'heure est importante

Kerberos utilise des dates de validité pour ses tickets et ses mécanismes de protection.

Un écart d'heure important entre le client et les serveurs peut donc provoquer des échecs d'authentification.

Sur Linux :

```bash
timedatectl
```

Pour examiner l'état de la synchronisation :

```bash
timedatectl timesync-status
```

Cette seconde commande est disponible sur les systèmes systemd qui la prennent en charge.

Si l'environnement utilise `chrony` :

```bash
chronyc tracking
```

Il faut utiliser la méthode de synchronisation configurée sur le système.

Une heure correctement synchronisée ne corrige pas tous les problèmes Kerberos, mais c'est une condition importante de fonctionnement.

## 5.7. Examiner les tickets Kerberos

Lorsque le client Kerberos est installé :

```bash
klist
```

Cette commande affiche les tickets présents dans le cache de l'utilisateur courant.

Pour demander un ticket initial dans un environnement configuré :

```bash
kinit alice@AD.EXAMPLE.TEST
```

La commande demande généralement un secret ou utilise un mécanisme pris en charge.

Le principal utilisé doit correspondre au domaine et à la politique d'authentification de l'environnement.

Puis :

```bash
klist
```

Pour supprimer les tickets du cache de la session courante :

```bash
kdestroy
```

Cette commande détruit les tickets du cache Kerberos sélectionné. Elle ne supprime pas le compte de l'annuaire.

## 5.8. Pourquoi Kerberos et LDAP sont-ils souvent associés ?

LDAP permet notamment de consulter les données d'annuaire.

Kerberos fournit un mécanisme d'authentification par tickets.

Ils peuvent être utilisés ensemble :

```text
             ANNuaire LDAP
                  |
                  v
       Utilisateurs et groupes
                  |
                  v
              SSSD/NSS

             KERBEROS
                  |
                  v
      Authentification par tickets
                  |
                  v
                PAM
```

Ce modèle existe dans des environnements basés sur LDAP et Kerberos, ainsi que dans certaines architectures intégrées à Active Directory.

Les rôles exacts dépendent du fournisseur d'identité et de la configuration SSSD.


# 6. NSS, PAM, SSSD, realmd et winbind : rôles et différences

Cette section est essentielle pour comprendre comment une identité provenant d'un serveur central devient un compte utilisable par Linux.

## 6.1. NSS : Name Service Switch

NSS permet au système de rechercher diverses informations telles que les utilisateurs, les groupes et les noms d'hôtes au moyen de sources configurées.

Sa configuration se trouve généralement dans :

```text
/etc/nsswitch.conf
```

Examiner les sources de comptes et groupes :

```bash
grep -E '^(passwd|group|shadow):' /etc/nsswitch.conf
```

Exemple :

```text
passwd: files sss
group:  files sss
shadow: files sss
```

Dans ce modèle :

- `files` désigne les bases locales classiques.
- `sss` désigne le fournisseur d'identités associé à SSSD, lorsqu'il est configuré.

L'ordre des sources et la politique de résolution influencent le comportement réel du système.

## 6.2. Pourquoi NSS est-il nécessaire ?

Considérons une commande :

```bash
id alice@ad.example.test
```

Pour afficher :

```text
uid=... gid=... groups=...
```

le système doit pouvoir déterminer l'identité numérique correspondante et ses groupes.

NSS permet à certains outils et composants Linux d'accéder à cette information à travers la configuration du système.

Le compte peut provenir d'un annuaire plutôt que du fichier `/etc/passwd`.

NSS assure la résolution des identités ; il ne réalise pas à lui seul toute l'authentification.

## 6.3. PAM : Pluggable Authentication Modules

PAM fournit une architecture modulaire permettant à certains services Linux de s'appuyer sur des modules configurables pour l'authentification, le contrôle de compte, les changements de mot de passe et les sessions.

Les services concernés peuvent inclure les connexions locales, SSH et d'autres applications selon la configuration.

Les fichiers PAM sont généralement situés sous :

```text
/etc/pam.d/
```

Afficher les fichiers :

```bash
ls /etc/pam.d/
```

Les grandes catégories PAM sont notamment :

| Type | Rôle général |
|---|---|
| `auth` | Vérifier l'authentification |
| `account` | Appliquer certaines vérifications liées à l'état du compte |
| `password` | Gérer les changements de mot de passe |
| `session` | Gérer des opérations d'ouverture et de fermeture de session |

Les détails dépendent du service et de la configuration des modules.

## 6.4. PAM ne stocke pas nécessairement les identités

PAM peut utiliser différents modules d'authentification.

Il faut le distinguer de la base d'identités :

- NSS fournit la résolution des comptes et groupes.
- PAM permet à un service d'utiliser une chaîne de modules pour traiter l'authentification et d'autres contrôles.
- SSSD peut participer à ces deux domaines par ses modules et ses services.

**NSS et PAM ne sont donc pas deux noms pour le même mécanisme.**

## 6.5. SSSD : System Security Services Daemon

SSSD signifie *System Security Services Daemon*.

C'est un composant client utilisé sur Linux pour s'intégrer à différents fournisseurs d'identités et d'authentification.

Selon l'architecture, SSSD peut fournir :

- La résolution des utilisateurs.
- La résolution des groupes.
- L'authentification.
- Des contrôles d'accès.
- Un cache local des identités.
- Certaines capacités d'accès hors ligne, selon la configuration.

SSSD peut notamment s'intégrer avec Active Directory, LDAP, Kerberos et d'autres systèmes compatibles.

Documentation :

https://sssd.io/docs/introduction.html

## 6.6. Comment SSSD communique-t-il avec le système ?

Schéma conceptuel :

```text
              APPLICATION
                   |
                   v
                  NSS
                   |
                   v
                 SSSD
                   |
           +-------+-------+
           |               |
           v               v
       Cache local     Fournisseur
       d'identités     distant
                           |
                 +---------+---------+
                 |                   |
                 v                   v
                LDAP              Kerberos
                 |                   |
                 +---------+---------+
                           |
                           v
                  Service d'identité
```

La représentation est simplifiée.

SSSD comprend plusieurs composants internes et fournisseurs. Leur fonctionnement dépend de la configuration.

NSS sollicite SSSD pour obtenir les informations de comptes et de groupes.

PAM peut solliciter SSSD pour les opérations d'authentification et les contrôles pris en charge.

Le service SSSD communique avec l'annuaire ou les services d'authentification selon le fournisseur configuré.

## 6.7. realmd : découverte et intégration des domaines

`realmd` est un service qui facilite la découverte et l'intégration à certains domaines centralisés.

La commande `realm` constitue son interface d'administration.

Elle permet notamment de :

- Découvrir un domaine.
- Identifier les composants nécessaires.
- Joindre un domaine.
- Consulter la configuration.
- Gérer certaines règles locales d'accès des utilisateurs du domaine.

Exemples :

```bash
realm discover ad.example.test
realm list
```

La découverte dépend de la configuration réseau et, dans le cas d'AD, des mécanismes de découverte DNS disponibles.

`realmd` ne remplace ni LDAP ni Kerberos. Il aide à configurer l'intégration.

## 6.8. adcli : opérations d'adhésion à Active Directory

`adcli` est un outil utilisé pour effectuer certaines opérations d'administration liées aux domaines Active Directory, notamment l'adhésion d'une machine.

Il peut être utilisé indirectement par `realmd`.

Une intégration courante peut donc combiner :

```text
realm
  |
  v
realmd
  |
  v
adcli
  |
  v
Active Directory
```

Ce schéma est simplifié et n'implique pas que chaque opération de connexion utilisateur passe directement par `adcli`.

## 6.9. winbind

Winbind est un autre composant fréquemment utilisé dans les environnements Samba intégrés à Active Directory.

Il peut notamment servir à résoudre les identités du domaine et à intégrer certains scénarios de partage de fichiers ou de services Samba.

Il ne faut pas supposer que SSSD et winbind doivent toujours être actifs simultanément pour gérer les mêmes identités.

Le choix dépend de l'architecture, notamment lorsque Linux héberge des services Samba ou doit fonctionner comme membre de domaine avec des besoins particuliers de correspondance des identifiants.

## 6.10. Résumé des composants

| Composant | Rôle principal |
|---|---|
| LDAP | Protocole d'accès à l'annuaire |
| Active Directory DS | Service d'annuaire de domaine |
| Kerberos | Authentification par tickets |
| DNS | Découverte des services et résolution des noms |
| NSS | Résolution des utilisateurs, groupes et autres informations |
| PAM | Modules d'authentification, de contrôle de compte et de session |
| SSSD | Intégration cliente aux sources d'identité et d'authentification |
| realmd | Découverte et intégration des domaines pris en charge |
| adcli | Opérations d'adhésion et de gestion associées à AD |
| winbind | Intégration d'identités de domaine, notamment dans les environnements Samba |

## 6.11. Le flux d'une connexion Linux centralisée

Prenons un utilisateur AD qui ouvre une session SSH.

```text
               Utilisateur Alice
                       |
                       v
                Client SSH
                       |
                       v
               Serveur SSH Linux
                       |
                       v
                PAM, si activé
                       |
                       v
                      SSSD
                       |
              +--------+--------+
              |                 |
              v                 v
         Vérification       Vérification
          du compte          d'identité
              |                 |
              v                 v
          Kerberos/AD      LDAP/AD via
          selon le cas      le fournisseur
              |                 |
              +--------+--------+
                       |
                       v
             Décision d'accès locale
                       |
                       v
                Session éventuelle
                       |
                       v
             UID, groupes et permissions
```

La séquence exacte dépend de la configuration.

Il est important de retenir que l'annuaire, l'authentification, la résolution des identités et l'autorisation sont des fonctions différentes, même lorsqu'elles sont mises en œuvre dans un même ensemble de produits.


# 7. Comprendre les UID, GID, SID et la correspondance des identités

## 7.1. Linux utilise des identifiants POSIX

Linux représente les propriétaires et les groupes des fichiers par des identifiants numériques.

Un utilisateur possède un UID, et un groupe possède un GID.

Exemple :

```text
Alice
  |
  +-- UID : 20001
  |
  +-- GID principal : 20010
```

Ces valeurs déterminent notamment le propriétaire et le groupe associés aux fichiers.

## 7.2. Active Directory utilise des SID

Active Directory représente ses objets de sécurité au moyen de SID (*Security Identifiers*).

Exemple fictif :

```text
S-1-5-21-123456789-234567890-345678901-1105
```

Un SID n'est pas identique à un UID ou à un GID.

Il faut un mécanisme qui détermine quelle identité POSIX correspond à l'utilisateur ou au groupe AD.

## 7.3. Comment SSSD peut-il obtenir un UID et un GID ?

Deux grandes stratégies existent dans certains scénarios AD :

### Stratégie A : correspondance automatique

SSSD peut calculer des identifiants POSIX à partir des SID de manière déterministe selon son mécanisme de correspondance configuré.

Dans ce cas, il n'est pas nécessaire d'enregistrer explicitement tous les attributs POSIX dans Active Directory.

Les règles de correspondance doivent toutefois rester cohérentes dans l'environnement.

### Stratégie B : attributs POSIX présents dans l'annuaire

Une autre possibilité consiste à fournir des attributs tels que :

```text
uidNumber
gidNumber
unixHomeDirectory
loginShell
```

Les attributs doivent être correctement renseignés et gérés dans l'annuaire.

Le choix entre ces stratégies doit être défini avant d'intégrer plusieurs serveurs.

Il ne faut pas mélanger des méthodes incompatibles en espérant que les identifiants resteront automatiquement stables.

## 7.4. Pourquoi la cohérence UID/GID est-elle importante ?

Supposons qu'un fichier sur un stockage partagé appartienne à l'UID `20001`.

Si deux serveurs attribuent des identités numériques différentes à Alice, les permissions sur ce fichier peuvent être interprétées différemment selon le serveur.

Schéma :

```text
                Stockage partagé
                       |
                       v
              Propriétaire UID 20001
                       |
               +-------+-------+
               |               |
               v               v
           Serveur A        Serveur B
           Alice=20001      Alice=30001
```

Le résultat attendu n'est pas garanti si les identités ne sont pas cohérentes.

C'est particulièrement important pour :

- NFS.
- Les répertoires personnels partagés.
- Les serveurs de fichiers.
- Les environnements multi-serveurs.
- Les restaurations de sauvegardes.
- Les migrations de données.

## 7.5. Vérifier les identifiants effectifs

Après l'intégration d'un compte centralisé :

```bash
id alice@ad.example.test
```

Puis :

```bash
getent passwd alice@ad.example.test
```

La sortie permet d'observer l'identifiant numérique et les groupes connus du système.

Les noms et l'UID présentés dépendent de la configuration réelle.

Ne choisis pas arbitrairement un UID d'entreprise simplement parce qu'un exemple de documentation utilise cette valeur.


# 8. Préparer un serveur Linux à rejoindre un domaine Active Directory

Cette section prépare l'intégration pratique.

L'exemple emploie Ubuntu comme client Linux et un domaine AD déjà opérationnel.

Les commandes exactes peuvent varier selon la version de la distribution. La machine Linux doit être configurée pour utiliser les services DNS appropriés avant de rejoindre le domaine.

## 8.1. Conditions préalables

Avant l'installation, vérifie :

- Le nom DNS du domaine.
- Les noms des contrôleurs de domaine.
- Les adresses DNS réellement utilisées.
- L'heure du serveur.
- Le nom de la machine.
- La connectivité réseau.
- Les droits nécessaires pour joindre un ordinateur au domaine.
- La politique de connexion des utilisateurs.
- La correspondance des identifiants Linux.
- Les comptes qui seront autorisés à accéder au serveur.

Il est fortement recommandé d'utiliser un compte de domaine disposant uniquement des droits nécessaires à l'enrôlement de la machine plutôt que le compte d'administration général du domaine.

## 8.2. Vérifier le nom d'hôte

Afficher le nom actuel :

```bash
hostnamectl
```

Pour examiner le nom pleinement qualifié lorsqu'il est correctement configuré :

```bash
hostname -f
```

Exemple attendu :

```text
linux01.ad.example.test
```

Le nom doit correspondre à l'organisation prévue et ne doit pas entrer en conflit avec une autre machine.

## 8.3. Vérifier DNS

Sous Ubuntu avec systemd :

```bash
resolvectl status
```

Vérifie que le client utilise les résolveurs prévus pour l'intégration au domaine.

Rechercher les enregistrements SRV :

```bash
dig SRV _ldap._tcp.ad.example.test
```

Puis :

```bash
dig SRV _kerberos._tcp.ad.example.test
```

Les commandes doivent être adaptées au domaine réel.

Si les enregistrements ne sont pas résolus, vérifie le DNS avant de continuer.

L'accès direct par adresse IP ne remplace pas toujours la découverte des services attendue par l'intégration AD.

## 8.4. Vérifier l'heure

```bash
timedatectl
```

Si `chrony` est installé :

```bash
chronyc tracking
```

L'heure doit être correctement synchronisée avec l'infrastructure.

Un décalage important peut provoquer un échec Kerberos.

Ne corrige pas un problème d'heure en modifiant arbitrairement la date du serveur sans comprendre la politique de synchronisation.

## 8.5. Installer les outils nécessaires

Sur une version courante d'Ubuntu, une intégration SSSD avec Active Directory peut utiliser les paquets suivants :

```bash
sudo apt update
sudo apt install sssd-ad sssd-tools realmd adcli
```

Des dépendances supplémentaires, telles que les modules NSS et PAM pour SSSD, peuvent être proposées automatiquement.

Selon la version et la procédure suivie, les outils Kerberos et d'autres paquets peuvent aussi être nécessaires.

Si le serveur n'utilise pas Ubuntu, consulte la documentation de sa distribution.

## 8.6. Découvrir le domaine

Commande :

```bash
sudo realm discover ad.example.test
```

Pour une sortie plus détaillée :

```bash
sudo realm -v discover ad.example.test
```

La découverte permet de déterminer si le domaine est visible et de repérer certains composants nécessaires à l'intégration.

Une erreur de découverte peut provenir :

- Du DNS.
- D'un problème réseau.
- D'un domaine mal nommé.
- D'un contrôleur indisponible.
- D'une configuration du client incorrecte.

Il est préférable de résoudre ce problème avant de tenter l'adhésion.

## 8.7. Comprendre ce que signifie joindre un domaine

Joindre le domaine signifie que la machine est enregistrée comme membre du domaine AD selon le mécanisme d'intégration retenu.

Cela peut créer ou mettre à jour un compte ordinateur dans Active Directory et configurer les éléments nécessaires au fonctionnement du client.

Cette opération ne signifie pas que tous les utilisateurs du domaine doivent automatiquement être autorisés à se connecter au serveur.

L'adhésion, l'authentification et l'autorisation sont trois aspects distincts.


# 9. Intégrer Linux à Active Directory avec SSSD

## 9.1. Architecture cible

Après une intégration réussie, le fonctionnement peut être représenté ainsi :

```text
              Active Directory
                     |
          +----------+----------+
          |                     |
          v                     v
       Annuaire               Kerberos
       LDAP/AD               Authentification
          |                     |
          +----------+----------+
                     |
                     v
                  SSSD
                     |
             +-------+-------+
             |               |
             v               v
            NSS              PAM
             |               |
             v               v
     Résolution du compte   Connexion
     et des groupes         et contrôle
             |               |
             +-------+-------+
                     |
                     v
                Session Linux
```

L'architecture est simplifiée. SSSD utilise le fournisseur configuré pour accéder aux informations et effectuer les contrôles requis.

## 9.2. Joindre le domaine

Il est préférable d'utiliser un compte explicitement autorisé à joindre des machines.

Exemple :

```bash
sudo realm join --user=join-linux ad.example.test
```

Le compte `join-linux` est un exemple fictif. Il doit exister dans le domaine et posséder les droits nécessaires à l'opération.

La commande peut demander le mot de passe dans le terminal. Ne place pas ce secret directement dans la ligne de commande.

Selon l'environnement, un mécanisme d'enrôlement par mot de passe à usage unique ou une autre méthode approuvée peut être utilisé.

Si l'opération échoue, examine la sortie et les journaux plutôt que de relancer plusieurs fois la commande sans diagnostic.

## 9.3. Vérifier l'adhésion

```bash
realm list
```

Cette commande affiche les domaines configurés sur le système selon les capacités de realmd.

Vérifie également le service :

```bash
systemctl status sssd
```

Puis les journaux récents :

```bash
sudo journalctl -u sssd --since "15 minutes ago"
```

Les noms des services et certains détails peuvent varier selon la distribution.

## 9.4. Vérifier la configuration SSSD

Un fichier de configuration courant se trouve sous :

```text
/etc/sssd/sssd.conf
```

Exemple conceptuel pour Active Directory :

```ini
[sssd]
domains = ad.example.test
config_file_version = 2
services = nss, pam

[domain/ad.example.test]
id_provider = ad
access_provider = ad
ad_domain = ad.example.test
krb5_realm = AD.EXAMPLE.TEST
use_fully_qualified_names = True
fallback_homedir = /home/%u@%d
cache_credentials = True
```

**Ce bloc sert à illustrer les principaux paramètres. Il ne faut pas remplacer aveuglément le fichier créé par `realm join` par ce contenu.**

La configuration réelle peut inclure d'autres paramètres nécessaires à la version de SSSD, à la topologie du domaine et à la politique de sécurité.

Les paramètres ont les rôles suivants :

- `id_provider = ad` : utilise le fournisseur Active Directory pour les informations d'identité.
- `access_provider = ad` : utilise les règles d'accès prises en charge par le fournisseur AD.
- `ad_domain` : définit le domaine DNS associé.
- `krb5_realm` : définit le royaume Kerberos.
- `use_fully_qualified_names` : contrôle l'usage du nom pleinement qualifié pour l'identité.
- `fallback_homedir` : fournit un modèle de répertoire personnel lorsque le mécanisme applicable le demande.
- `cache_credentials` : permet de mettre en cache certains éléments d'authentification, selon les mécanismes pris en charge.

SSSD doit être en mesure de lire sa configuration.

Sur les installations courantes, `/etc/sssd/sssd.conf` doit être protégé par des permissions restrictives, généralement :

```bash
sudo chown root:root /etc/sssd/sssd.conf
sudo chmod 600 /etc/sssd/sssd.conf
```

Vérifie les exigences exactes de ta distribution avant de modifier la configuration.

## 9.5. Activer la création automatique des répertoires personnels

Un utilisateur centralisé peut être reconnu sans que son répertoire personnel existe déjà.

Sur Ubuntu, une méthode courante consiste à activer `pam_mkhomedir` au moyen de l'outil de configuration PAM :

```bash
sudo pam-auth-update --enable mkhomedir
```

Cette commande dépend de la disponibilité des profils PAM correspondants.

Sur d'autres distributions, la configuration peut employer d'autres composants, par exemple `oddjob` et le mécanisme de création de répertoires personnels adapté à la distribution.

Il ne faut pas supposer que le répertoire personnel sera créé automatiquement simplement parce que le domaine a été rejoint.

## 9.6. Vérifier la résolution d'un utilisateur AD

Supposons que le compte centralisé soit `alice`.

Avec une configuration qui utilise des noms pleinement qualifiés :

```bash
getent passwd 'alice@ad.example.test'
```

Puis :

```bash
id 'alice@ad.example.test'
```

Si l'identité est correctement résolue, les informations affichées doivent contenir un UID, un GID principal et les groupes connus du système.

Le résultat dépend du compte et de la correspondance d'identifiants employée.

## 9.7. Vérifier les groupes du domaine

Par exemple :

```bash
id 'alice@ad.example.test'
```

Cette commande est souvent plus instructive qu'une recherche isolée du groupe, car elle affiche les groupes associés à l'identité résolue.

Pour interroger un groupe :

```bash
getent group 'Linux-Admins@ad.example.test'
```

Le nom exact dépend de l'annuaire, des options SSSD et du format de nom retenu.

Les groupes imbriqués, les relations d'approbation et les attributs de groupes peuvent nécessiter une configuration complémentaire.

## 9.8. Tester l'authentification

La résolution d'un compte ne prouve pas que son authentification fonctionne.

Il faut tester une connexion réelle dans un environnement de laboratoire.

Si une connexion locale est disponible, elle peut servir à tester le comportement de PAM selon la configuration du système.

Pour SSH, il faudra également vérifier le serveur, les restrictions d'accès et le mode d'authentification retenu.

Ne considère pas ce contrôle comme réussi tant que le compte n'a pas été testé par le service qu'il doit réellement utiliser.

## 9.9. Examiner les tickets Kerberos

Si les outils Kerberos sont installés :

```bash
klist
```

Pour demander un ticket dans le domaine de laboratoire :

```bash
kinit alice@AD.EXAMPLE.TEST
```

Puis :

```bash
klist
```

L'obtention d'un ticket aide à examiner le fonctionnement Kerberos.

Elle ne prouve pas automatiquement que le compte est autorisé à se connecter au serveur Linux.

Il faut encore vérifier la politique d'accès locale et les permissions.

## 9.10. Vérifier le service SSSD

```bash
systemctl status sssd
```

Pour consulter les journaux :

```bash
sudo journalctl -u sssd --since "30 minutes ago"
```

Pour obtenir davantage de renseignements sur une identité, si l'outil est disponible :

```bash
sssctl user-checks 'alice@ad.example.test' -s sshd
```

Cette commande et ses options dépendent de la version installée. Consulte le manuel local de `sssctl`.

Elle peut aider à comprendre le comportement d'un compte pour un service donné, selon les informations disponibles.

## 9.11. Pourquoi ne pas copier un fichier SSSD trouvé sur Internet ?

La configuration dépend de plusieurs caractéristiques :

- Version de SSSD.
- Distribution Linux.
- Domaine AD.
- Schéma et identifiants.
- Méthode de correspondance UID/GID.
- Groupes autorisés.
- Politique de cache.
- Accès hors ligne.
- Stratégie de sécurité.
- Exigences SSH et PAM.

Un fichier incomplet peut empêcher SSSD de démarrer.

Un fichier incorrect peut aussi autoriser trop d'utilisateurs ou en bloquer certains.

La meilleure méthode consiste à effectuer une intégration guidée, à examiner la configuration générée puis à ne modifier que les paramètres nécessaires, en testant chaque changement.


# 10. Configurer l'accès par groupes et contrôler les connexions

## 10.1. La présence dans un domaine ne signifie pas l'autorisation de se connecter

Un utilisateur peut exister dans Active Directory et être correctement authentifié, mais ne pas devoir accéder à un serveur particulier.

Exemple :

```text
Domaine AD
   |
   +-- Groupe Developpeurs
   |
   +-- Groupe Audit
   |
   +-- Groupe Linux-Admins
```

Un serveur de développement peut n'autoriser que les groupes concernés.

Un serveur d'administration peut exiger un groupe restreint.

La politique doit être explicite.

## 10.2. Vérifier la politique actuelle de realmd

```bash
realm list
```

Cette commande permet notamment d'examiner la configuration de l'intégration et, selon la version, la politique de connexion au domaine.

Après une intégration, vérifie si les utilisateurs autorisés sont limités ou si le système autorise plus largement les comptes du domaine.

Ne suppose jamais que la politique par défaut correspond à celle attendue par ton organisation.

## 10.3. Restreindre les connexions avec `realm permit`

`realmd` fournit des commandes permettant de gérer certaines politiques locales d'accès aux comptes du domaine.

Pour autoriser un groupe particulier, une commande courante est :

```bash
sudo realm permit --groups 'Linux-Admins@ad.example.test'
```

Le nom utilisé doit correspondre au format de groupe résolu sur le système.

Une politique de ce type peut configurer SSSD pour utiliser un fournisseur d'accès simple qui autorise seulement les utilisateurs et groupes listés.

Cela signifie qu'il faut comprendre les conséquences de la commande et vérifier le résultat dans la configuration.

Cette opération ne doit pas être exécutée à l'aveugle sur un serveur où d'autres utilisateurs du domaine doivent conserver leur accès.

## 10.4. Vérifier les groupes avant de restreindre l'accès

Avant de déployer une restriction :

```bash
id 'alice@ad.example.test'
getent group 'Linux-Admins@ad.example.test'
realm list
```

Assure-toi que le groupe attendu est correctement résolu.

Si le groupe n'existe pas ou si son nom est mal interprété, le serveur peut refuser les connexions que tu souhaitais autoriser.

Prévois un compte administrateur local de secours dont l'accès est conforme à la politique de sécurité.

## 10.5. `access_provider = ad` et `access_provider = simple`

SSSD propose différents mécanismes de contrôle d'accès.

Avec le fournisseur AD :

```ini
access_provider = ad
```

SSSD applique les vérifications d'accès associées au fournisseur AD, selon sa configuration.

Avec le fournisseur simple :

```ini
access_provider = simple
simple_allow_groups = groupe1, groupe2
```

l'accès peut être limité à des utilisateurs ou groupes explicitement autorisés.

Ces deux modèles ne sont pas interchangeables sans analyse.

L'utilisation de `realm permit` peut modifier le modèle d'accès vers le fournisseur simple. Il faut donc contrôler la configuration résultante, plutôt que supposer que la commande ajoute simplement une liste sans effet sur le reste.

## 10.6. Attention aux noms de groupes

Les noms centralisés peuvent être affichés avec ou sans suffixe de domaine selon la configuration.

Exemples :

```text
Linux-Admins
Linux-Admins@ad.example.test
```

Les deux formes ne sont pas nécessairement interchangeables dans chaque commande.

Pour déterminer le format réellement utilisé :

```bash
id 'alice@ad.example.test'
getent group
realm list
```

Les groupes peuvent également comporter des espaces ou d'autres caractères, selon les règles du système.

Utilise des guillemets lorsque nécessaire.

## 10.7. Autorisation d'accès et permissions des fichiers

Autoriser un utilisateur à ouvrir une session ne lui donne pas automatiquement le droit de modifier tous les fichiers du serveur.

Par exemple :

```text
Authentification réussie
        |
        v
Accès SSH autorisé
        |
        v
Session ouverte
        |
        v
Accès à /srv/projets
        |
        v
Vérification des permissions
```

Le répertoire doit être configuré avec les groupes, permissions ou ACL appropriés.

La politique d'accès au serveur et la politique d'accès aux fichiers doivent être contrôlées séparément.


# 11. Intégrer Linux à un annuaire LDAP

Cette section traite d'une architecture où le serveur Linux utilise un annuaire LDAP, par exemple OpenLDAP, pour résoudre des utilisateurs et des groupes.

Il ne faut pas confondre ce scénario avec une intégration à Active Directory utilisant le fournisseur AD de SSSD.

## 11.1. Architecture d'intégration

```text
                 Serveur Linux
                      |
             +--------+--------+
             |                 |
             v                 v
            NSS               PAM
             |                 |
             +--------+--------+
                      |
                      v
                    SSSD
                      |
                      v
                 Client LDAP
                      |
                      v
               Serveur LDAP
                      |
            +---------+---------+
            |                   |
            v                   v
       Utilisateurs           Groupes
```

SSSD peut fournir la résolution des identités et l'authentification selon le fournisseur LDAP et les options configurés.

L'annuaire doit exposer des attributs compatibles avec le modèle d'identité attendu par Linux.

## 11.2. Préconditions

Avant de configurer le client :

- L'annuaire LDAP doit être opérationnel.
- Le DN de base doit être connu.
- Le schéma des utilisateurs doit être identifié.
- Le schéma des groupes doit être identifié.
- Les UID et GID doivent être cohérents.
- Le serveur doit pouvoir résoudre le nom de l'annuaire.
- Le transport doit être sécurisé.
- Les droits de recherche et d'authentification doivent être définis.
- La politique de création de répertoires personnels doit être connue.

Ne configure pas un client avec des attributs supposés sans vérifier ceux qui existent réellement dans l'annuaire.

## 11.3. Installer les outils LDAP et SSSD

Sur Ubuntu, une configuration LDAP avec SSSD peut notamment utiliser :

```bash
sudo apt update
sudo apt install sssd-ldap sssd-tools ldap-utils
```

Selon le scénario et les dépendances, des modules supplémentaires d'intégration PAM/NSS peuvent être requis ou installés automatiquement.

Le serveur LDAP doit déjà être configuré.

## 11.4. Examiner l'annuaire

Une recherche peut être réalisée avec `ldapsearch`.

Exemple :

```bash
ldapsearch -x \
  -H ldaps://ldap01.example.test \
  -b "dc=example,dc=test" \
  "(uid=alice)" \
  uid cn uidNumber gidNumber homeDirectory loginShell
```

Cette commande suppose que la recherche est autorisée sans authentification explicite.

Si le serveur exige une identité de lecture, il faut utiliser un compte technique prévu à cet effet et une méthode sécurisée pour fournir ses informations d'authentification.

Ne stocke pas le mot de passe de ce compte directement dans le script.

## 11.5. Configurer SSSD pour LDAP

Un exemple conceptuel de `/etc/sssd/sssd.conf` :

```ini
[sssd]
config_file_version = 2
domains = ldap.example.test
services = nss, pam

[domain/ldap.example.test]
id_provider = ldap
auth_provider = ldap
chpass_provider = ldap
access_provider = simple

ldap_uri = ldaps://ldap01.example.test
ldap_search_base = dc=example,dc=test
ldap_schema = rfc2307

ldap_tls_reqcert = demand
ldap_tls_cacert = /etc/ssl/certs/ca-certificates.crt

cache_credentials = true
simple_allow_groups = linux-users

use_fully_qualified_names = false
fallback_homedir = /home/%u
default_shell = /bin/bash
```

**Ce fichier est un exemple pédagogique à adapter, pas une configuration universelle prête à appliquer sur un serveur réel.**

Il suppose notamment :

- Un serveur LDAP qui prend en charge le schéma et les attributs attendus.
- Une autorité de certification reconnue.
- Un nom DNS valide pour le serveur LDAP.
- Un groupe `linux-users` qui existe dans l'annuaire.
- Une correspondance UID/GID correcte.
- Des modules SSSD et PAM convenablement installés.

Le mode exact de gestion des mots de passe et des connexions doit être validé avec l'administrateur LDAP.

Le fournisseur simple restreint les accès selon la liste définie, mais ses possibilités sont différentes de celles d'un fournisseur LDAP avec filtre d'accès ou d'un fournisseur AD.

## 11.6. Pourquoi utiliser TLS ?

Les échanges entre le client et l'annuaire peuvent contenir des données sensibles.

La configuration doit donc protéger le transport et valider le certificat du serveur.

Dans l'exemple, le nom :

```text
ldap01.example.test
```

doit correspondre au serveur réellement contacté et au certificat présenté.

La configuration doit aussi faire confiance à l'autorité qui a émis ce certificat.

Sur Ubuntu, si l'entreprise utilise une autorité de certification interne, cette autorité doit être installée selon la procédure de confiance du système.

Ne remplace pas la validation du certificat par un réglage qui accepte n'importe quel certificat.

## 11.7. Protéger la configuration SSSD

Après création du fichier :

```bash
sudo chown root:root /etc/sssd/sssd.conf
sudo chmod 600 /etc/sssd/sssd.conf
```

Vérifie ensuite la configuration et les journaux.

Le service SSSD peut refuser de démarrer si le fichier contient des erreurs ou présente des permissions inadaptées.

## 11.8. Démarrer le service

```bash
sudo systemctl enable --now sssd
```

Puis :

```bash
systemctl status sssd
```

Examiner les journaux :

```bash
sudo journalctl -u sssd --since "15 minutes ago"
```

Selon la version et les mécanismes de configuration, les modules PAM et NSS doivent également être activés.

## 11.9. Vérifier la résolution du compte

```bash
getent passwd alice
```

Puis :

```bash
id alice
```

Si l'annuaire utilise des noms pleinement qualifiés, le nom à rechercher peut être différent.

Si l'utilisateur n'est pas résolu, examine :

- L'accès réseau.
- La résolution DNS.
- Le certificat.
- Le DN de base.
- Les attributs LDAP.
- Le schéma.
- Les règles SSSD.
- Les permissions de recherche dans l'annuaire.

## 11.10. LDAP avec Kerberos

Dans une architecture plus élaborée, LDAP peut fournir les informations des comptes et Kerberos l'authentification.

```text
Annuaire LDAP
     |
     +-- Identités
     +-- Groupes
     +-- UID/GID POSIX

Serveur Kerberos
     |
     +-- Authentification
     +-- Tickets
            |
            v
          SSSD
            |
            v
         Linux
```

Cette architecture peut être utile lorsqu'une organisation sépare la gestion de l'annuaire et le service d'authentification.

Elle nécessite de configurer correctement les deux systèmes et de définir le fournisseur adapté dans SSSD.

Il ne suffit pas de remplacer `auth_provider = ldap` par `auth_provider = krb5` sans adapter le reste de la configuration.

## 11.11. Exemple d'attributs pour LDAP et POSIX

L'annuaire doit fournir les attributs correspondant au modèle Linux.

Exemple :

```text
uid: alice
uidNumber: 20001
gidNumber: 20010
homeDirectory: /home/alice
loginShell: /bin/bash
```

Un groupe compatible POSIX peut fournir :

```text
cn: linux-users
gidNumber: 20010
```

Les attributs des membres et leur interprétation dépendent du schéma utilisé.

La configuration doit correspondre à la structure réelle de l'annuaire.


# 12. Créer les répertoires personnels et gérer les sessions

## 12.1. Résoudre un utilisateur ne crée pas nécessairement son répertoire

Un compte centralisé peut être reconnu par :

```bash
id 'alice@ad.example.test'
```

mais son répertoire personnel peut ne pas exister.

Ces deux propriétés sont différentes.

La résolution d'identité fournit les informations du compte.

La création du répertoire est une opération distincte liée à la configuration de session ou à la gestion de l'espace personnel.

## 12.2. Trois modèles de répertoire personnel

### Modèle A : répertoire local sur chaque serveur

```text
Serveur A
    |
    +-- /home/alice

Serveur B
    |
    +-- /home/alice
```

Les contenus ne sont pas nécessairement partagés entre les machines.

### Modèle B : stockage personnel partagé

```text
                 Stockage partagé
                        |
             +----------+----------+
             |                     |
             v                     v
         Serveur A             Serveur B
             |                     |
             +----------+----------+
                        |
                        v
                   /home/alice
```

Les deux serveurs utilisent un emplacement commun, selon l'architecture du système de fichiers partagé.

Dans ce modèle, la cohérence des UID/GID est particulièrement importante.

### Modèle C : répertoire créé à la première connexion

```text
Utilisateur centralisé
        |
        v
Connexion
        |
        v
PAM ou mécanisme équivalent
        |
        v
Création éventuelle de /home/alice
```

La création automatique dépend de la configuration du système.

## 12.3. Activer la création automatique sur Ubuntu

Dans certains environnements Ubuntu utilisant PAM :

```bash
sudo pam-auth-update --enable mkhomedir
```

Cette opération active le profil correspondant lorsque celui-ci est disponible.

La méthode peut différer sous d'autres distributions.

Après configuration, effectue un test avec un compte de laboratoire et vérifie :

```bash
ls -ld /home/alice
```

Examine aussi le propriétaire, le groupe et les permissions du répertoire créé.

## 12.4. Répertoire personnel sur stockage partagé

Si les répertoires personnels sont stockés sur NFS ou sur une autre infrastructure partagée, il faut contrôler :

- Le montage.
- Les permissions et ACL.
- Les UID/GID effectifs.
- La disponibilité du stockage.
- Les droits d'accès réseau.
- Le comportement en cas de panne.
- La stratégie de sauvegarde.

Une authentification centralisée fonctionnelle ne garantit pas que le stockage personnel soit disponible.

## 12.5. Fermeture d'une session

Fermer une session ne supprime pas le compte de l'annuaire et ne révoque pas nécessairement toutes les autorisations existantes.

Il faut distinguer :

- La session active.
- Le compte.
- Les tickets Kerberos.
- Les clés SSH.
- Le cache local.
- Les autres applications accessibles avec la même identité.

La révocation des accès doit être coordonnée avec la politique d'identité de l'organisation.


# 13. Groupes centralisés et permissions sur les fichiers

## 13.1. Les groupes AD peuvent servir aux permissions Linux

Lorsqu'un groupe de domaine est correctement résolu par le système, il peut être utilisé dans certains contextes Linux pour déterminer les droits des utilisateurs.

Exemple :

```text
Active Directory
      |
      v
Groupe Developpeurs
      |
      v
SSSD
      |
      v
Groupe résolu par Linux
      |
      v
Permissions du répertoire
```

La manière dont le nom et le GID sont représentés dépend de la configuration SSSD.

Il faut vérifier le groupe réellement résolu au lieu de supposer un identifiant numérique.

## 13.2. Vérifier l'identité d'un membre du domaine

```bash
id 'alice@ad.example.test'
```

Les groupes affichés aident à déterminer les appartenances reconnues par Linux.

Si un groupe attendu n'apparaît pas, il faut examiner la configuration du fournisseur d'identité et les attributs d'appartenance.

Un compte centralisé peut être correctement authentifié tout en présentant des informations de groupe incomplètes.

## 13.3. Configurer un répertoire partagé

Supposons que le groupe `Developpeurs` soit autorisé à travailler dans :

```text
/srv/projets
```

L'administrateur doit d'abord confirmer le nom de groupe reconnu par Linux.

Puis, selon la politique et la résolution locale :

```bash
sudo chown root:'developpeurs' /srv/projets
```

Cette syntaxe n'est valable que si le nom de groupe `developpeurs` est bien résolu localement.

Dans une intégration AD, le nom réel peut inclure le domaine ou suivre une autre convention.

Vérifie avant modification :

```bash
getent group
id 'alice@ad.example.test'
```

## 13.4. SGID sur le répertoire

Pour un répertoire collaboratif :

```bash
sudo chmod 2770 /srv/projets
```

Le bit SGID favorise l'héritage du groupe associé au répertoire lors de la création de nouveaux éléments.

Il ne remplace pas les ACL et ne garantit pas que tous les nouveaux fichiers possèdent les permissions d'écriture voulues.

Il faut tester les résultats avec les comptes réels du domaine.

## 13.5. Comptes centralisés et permissions traditionnelles

Les permissions Unix continuent à fonctionner normalement au niveau de leur modèle fondamental.

```text
Propriétaire
     |
     +-- UID

Groupe
     |
     +-- GID

Autres
     |
     +-- Selon les permissions
```

Le fait que l'identité provienne d'un annuaire ne remplace pas les permissions des fichiers.

Le système doit d'abord connaître l'UID et les groupes du processus, puis les mécanismes de permissions déterminent si l'accès est autorisé.


# 14. ACL : gérer des autorisations précises

## 14.1. Pourquoi les ACL sont-elles utiles ?

Une politique basée uniquement sur le groupe peut être trop restrictive ou trop large.

Exemple :

- Alice et Bob doivent pouvoir modifier les projets.
- Claire doit seulement pouvoir les consulter.
- Les autres utilisateurs ne doivent pas y accéder.

Une ACL permet d'accorder une autorisation spécifique à Claire sans nécessairement transformer toute l'organisation en une multitude de groupes.

## 14.2. Examiner les ACL

```bash
getfacl /srv/projets
```

Une ACL peut contenir des entrées nominatives telles que :

```text
user:claire:r-x
```

Cette entrée représente des droits sur le répertoire, sous réserve du masque ACL et des permissions de tous les répertoires parents.

## 14.3. Accorder des droits à un utilisateur centralisé

Si l'identité centralisée est correctement résolue, une ACL peut être appliquée au compte reconnu par Linux.

Exemple :

```bash
sudo setfacl -m u:claire:rx /srv/projets
```

Dans un environnement AD, le nom à utiliser peut être différent selon les règles de résolution.

Vérifie l'identité avant de modifier l'ACL.

## 14.4. Masque ACL

Le masque ACL peut limiter les droits effectifs des entrées utilisateur et groupe concernées.

Par exemple :

```text
user:claire:rwx
mask::r-x
```

L'entrée affiche `rwx`, mais le masque limite les droits effectifs.

Pour comprendre les accès, examine :

```bash
getfacl /srv/projets
```

Le résultat complet est plus important qu'une entrée isolée.

## 14.5. ACL par défaut

Les ACL par défaut permettent de définir certaines règles d'héritage pour les futurs fichiers et répertoires.

Exemple :

```bash
sudo setfacl -m d:u:claire:rx /srv/projets
```

Il faut tester le résultat avec les programmes qui créeront réellement les fichiers.

Une ACL par défaut ne remplace pas toutes les permissions et ne garantit pas que chaque fichier sera lisible dans tous les scénarios de création.


# 15. sudo, délégation et séparation des privilèges

## 15.1. Pourquoi déléguer des privilèges ?

Un membre de l'équipe d'exploitation peut devoir redémarrer un service, consulter son état ou exécuter une commande de maintenance.

Cela ne signifie pas qu'il doit obtenir un accès root complet.

Une délégation précise peut réduire le risque d'erreur et d'abus.

## 15.2. Vérifier la politique actuelle

```bash
sudo -l
```

Pour examiner les privilèges d'un utilisateur, selon les capacités de la version utilisée :

```bash
sudo -l -U alice
```

Il faut comprendre les règles appliquées au compte et les éventuelles autorisations héritées d'un groupe.

## 15.3. Groupes centralisés et sudo

Les groupes centralisés peuvent servir de base à une politique de délégation administrative.

Exemple conceptuel :

```text
Active Directory
       |
       v
Groupe Linux-Admins
       |
       v
SSSD résout le groupe
       |
       v
Politique sudo
       |
       v
Commandes administratives autorisées
```

Cette architecture nécessite une configuration locale ou centralisée adaptée.

Le seul fait qu'un groupe existe dans AD ne garantit pas qu'il possède un droit `sudo` sur le serveur.

## 15.4. Fichiers sudoers

La configuration se trouve souvent dans :

```text
/etc/sudoers
```

Des fichiers additionnels peuvent se trouver sous :

```text
/etc/sudoers.d/
```

Utilise l'outil adapté pour modifier la politique :

```bash
sudo visudo
```

Pour valider la configuration :

```bash
sudo visudo -c
```

Les règles doivent être testées avant leur déploiement.

## 15.5. Principe de moindre privilège

Une bonne politique répond à une question précise :

**Quelle commande l'utilisateur doit-il pouvoir exécuter, avec quelle identité et pour quelle raison ?**

Il faut examiner le comportement complet de la commande autorisée.

Une commande qui paraît limitée peut permettre de lancer d'autres programmes ou de modifier des fichiers plus largement que prévu.

Les règles sudoers ne doivent pas être construites uniquement en fonction du nom d'un outil.


# 16. SSH et authentification centralisée

## 16.1. L'accès SSH est une couche supplémentaire

Un utilisateur peut exister dans AD ou LDAP sans être autorisé à ouvrir une connexion SSH sur un serveur.

L'accès SSH dépend :

- Du compte résolu.
- De la politique d'accès du système.
- De PAM lorsqu'il est utilisé par la configuration SSH.
- Des méthodes d'authentification configurées.
- Des restrictions du serveur SSH.
- Des permissions et des règles de session.

Il faut donc tester SSH séparément après l'intégration du domaine.

## 16.2. Examiner l'état du service SSH

```bash
systemctl status ssh
```

Selon la distribution, le service peut s'appeler différemment, notamment `sshd`.

Vérifie les unités disponibles et utilise celle qui correspond au système.

## 16.3. Tester une connexion avec un compte AD

Si SSSD utilise des noms pleinement qualifiés, un test peut prendre la forme :

```bash
ssh -l 'alice@ad.example.test' linux01.ad.example.test
```

Les noms doivent être adaptés au serveur réel.

La réussite dépend de la configuration SSH, de PAM, de SSSD, du domaine et de la politique d'accès.

## 16.4. Configurer les restrictions SSH

Les règles de connexion peuvent être définies dans la configuration OpenSSH, selon les directives prises en charge.

Avant de modifier la configuration :

```bash
sudo sshd -t
```

Cette commande permet de vérifier la syntaxe de la configuration pour un serveur OpenSSH compatible.

Ne coupe pas l'accès administratif existant sans disposer d'une méthode de récupération.

Après toute modification :

- Vérifie la configuration.
- Recharge ou redémarre le service selon la procédure appropriée.
- Teste une nouvelle connexion.
- Vérifie les journaux.
- Confirme que les comptes attendus peuvent se connecter.
- Confirme que les comptes interdits ne peuvent pas se connecter.

## 16.5. Clés SSH et compte centralisé

Un compte issu d'AD peut également utiliser une clé SSH, si la configuration l'autorise.

La clé publique doit être installée ou référencée suivant la politique du serveur.

Le fait que le compte soit centralisé ne signifie pas que les clés SSH sont gérées dans AD ou par SSSD de manière automatique.

Il faut identifier l'emplacement et la politique réels des clés.

## 16.6. Désactiver une personne ne consiste pas à changer uniquement son mot de passe

Lorsqu'un collaborateur quitte l'organisation, il faut vérifier :

- La politique d'accès de son compte.
- Les clés SSH.
- Les groupes administratifs.
- Les sessions actives.
- Les tickets et caches concernés.
- Les comptes locaux éventuels.
- Les accès aux applications externes.

Une session déjà ouverte n'est pas nécessairement interrompue par le simple verrouillage du mot de passe centralisé.


# 17. Cycle de vie des comptes et désactivation des accès

## 17.1. Le cycle de vie d'un compte centralisé

```text
Demande de création
        |
        v
Validation du responsable
        |
        v
Création dans l'annuaire
        |
        v
Attribution des groupes
        |
        v
Accès aux serveurs appropriés
        |
        v
Révision périodique
        |
        v
Changement de rôle ou départ
        |
        v
Retrait des accès
        |
        v
Archivage ou suppression
```

La création et la suppression doivent être cohérentes dans l'annuaire et dans les systèmes qui dépendent de lui.

## 17.2. Un compte désactivé peut-il encore laisser des traces ?

Oui.

Même après le retrait d'un utilisateur de l'annuaire, des fichiers peuvent rester sur les serveurs.

Des processus peuvent continuer à fonctionner sous l'UID précédemment attribué.

Un compte peut aussi avoir des tâches planifiées, des clés ou des autorisations locales.

Il faut donc prévoir un traitement des données et des accès associés.

## 17.3. Retrait des groupes

Lorsqu'une personne change de rôle, il peut être nécessaire de modifier les groupes qui lui donnent accès aux ressources.

La suppression d'une appartenance peut réduire les nouveaux accès, mais elle ne garantit pas que toutes les sessions actives ou tous les services ont immédiatement perdu leurs autorisations déjà établies.

Il faut examiner les mécanismes de session et les exigences de sécurité.

## 17.4. UID et fichiers orphelins

Si un utilisateur a un UID numérique précis, les fichiers qui lui appartiennent peuvent conserver cet UID après le retrait du compte.

Pour rechercher des fichiers dans un périmètre :

```bash
sudo find /srv/projets -xdev -uid 20001 -print
```

Le nombre `20001` est un exemple. Utilise l'UID réel du compte.

Ne supprime pas ou ne réattribue pas automatiquement tous les fichiers trouvés.

L'administrateur doit déterminer si les données doivent être conservées, archivées ou transférées à un autre propriétaire.

## 17.5. Distinguer compte humain et compte technique

Lorsqu'une personne quitte l'entreprise, il faut déterminer si elle possède également des comptes techniques ou des tâches automatisées.

Exemple :

```text
Collaborateur
    |
    +-- Compte personnel
    |
    +-- Clé SSH
    |
    +-- Tâches planifiées
    |
    +-- Scripts
    |
    +-- Secrets applicatifs
```

Un compte de service ne doit pas être supprimé uniquement parce qu'il a été créé par la personne qui quitte l'organisation.

Il faut identifier le propriétaire fonctionnel du service et transférer les responsabilités nécessaires.


# 18. Comptes de service et gestion des identités techniques

## 18.1. Qu'est-ce qu'un compte de service ?

Un compte de service est une identité utilisée par un logiciel ou un processus plutôt que par une personne pour ses opérations habituelles.

Exemples :

- Service web.
- Agent de sauvegarde.
- Application métier.
- Base de données.
- Agent de supervision.

Les comptes techniques peuvent être locaux ou gérés par une infrastructure d'identité plus large, selon les exigences.

## 18.2. Pourquoi séparer les identités ?

Supposons qu'une application fonctionne en tant que root.

```text
Application compromise
          |
          v
Privilèges très étendus
          |
          v
Risque important sur le système
```

Avec un compte dédié et des permissions limitées :

```text
Application compromise
          |
          v
Compte de service
          |
          v
Ressources accessibles limitées
```

Cette séparation peut réduire les conséquences d'une compromission.

Elle ne remplace pas les autres mécanismes de sécurité de l'application.

## 18.3. Créer un compte de service local

Exemple :

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin service-web
```

Cette commande est illustrative. Vérifie d'abord que le compte n'existe pas déjà et que le chemin de `nologin` est correct pour ta distribution.

Un compte de service n'a pas nécessairement besoin d'un répertoire personnel interactif.

## 18.4. Compte de service dans un environnement centralisé

Une organisation peut également gérer certains comptes techniques dans un annuaire central.

Mais le choix dépend du logiciel, des mécanismes d'authentification et de la politique du service.

Un compte technique n'a pas toujours besoin d'une connexion interactive ou d'un mot de passe utilisé comme celui d'un utilisateur humain.

Il faut choisir le mécanisme adapté au service : secret géré, clé, certificat ou autre méthode prise en charge.

## 18.5. Ne pas partager les secrets

Les secrets d'un service doivent être conservés dans des emplacements protégés.

Évite :

- Les mots de passe en clair dans les scripts.
- Les clés privées dans les répertoires partagés.
- Les secrets dans l'historique du shell.
- Les identifiants de connexion intégrés aux dépôts de code.
- Les fichiers de configuration lisibles par tous.

La rotation et la révocation des secrets doivent être documentées.


# 19. Cache, disponibilité et fonctionnement hors ligne

## 19.1. Pourquoi SSSD met-il en cache des informations ?

SSSD peut mettre en cache certaines informations d'identité et, lorsque la configuration le permet, des éléments utiles à l'authentification hors ligne.

Le cache peut améliorer les performances de résolution des comptes et permettre certains usages lorsque le fournisseur central n'est temporairement pas joignable.

Le comportement dépend de la configuration, de la version de SSSD et du mécanisme d'authentification.

## 19.2. Que se passe-t-il lorsque le réseau tombe ?

Une panne de réseau peut empêcher le serveur Linux de joindre l'annuaire ou les services d'authentification.

```text
              Serveur Linux
                    |
                    v
                   SSSD
                    |
                    v
             Réseau indisponible
                    |
                    v
             Annuaire inaccessible
                    |
           +--------+--------+
           |                 |
           v                 v
      Informations       Authentification
      en cache           hors ligne possible
                         selon la politique
```

Il faut distinguer :

- La résolution de l'identité.
- L'authentification hors ligne.
- L'autorisation de se connecter.
- L'accès aux fichiers.
- L'accès à d'autres services du réseau.

Une session locale peut fonctionner même si certaines ressources réseau restent indisponibles.

## 19.3. Le cache n'est pas toujours une autorisation actuelle

Un cache peut contenir une information qui ne reflète plus l'état le plus récent de l'annuaire.

Par exemple, un utilisateur peut avoir été retiré d'un groupe centralisé pendant que le serveur est isolé.

Selon la configuration et les contrôles appliqués, le serveur peut ne pas disposer immédiatement de toutes les informations récentes.

Il faut donc définir une politique qui concilie disponibilité et retrait rapide des accès.

## 19.4. Vérifier l'état SSSD

```bash
systemctl status sssd
```

Puis :

```bash
sudo journalctl -u sssd --since "30 minutes ago"
```

Si l'outil est disponible :

```bash
sudo sssctl domain-status ad.example.test
```

La syntaxe exacte dépend de la version installée. Consulte le manuel local de `sssctl`.

## 19.5. Vider le cache avec prudence

Pour un laboratoire, certains outils SSSD permettent de supprimer ou d'invalider des informations en cache.

Mais effacer le cache d'une machine en production peut avoir des conséquences, notamment lorsque le réseau central est inaccessible.

Avant une opération de cache :

1. Identifie le problème.
2. Vérifie la connectivité au fournisseur.
3. Examine les journaux.
4. Vérifie la politique de fonctionnement hors ligne.
5. Prévois une méthode de récupération.
6. Effectue l'opération autorisée.
7. Contrôle les identités et les sessions après la modification.

Ne vide pas le cache systématiquement à chaque erreur de connexion.


# 20. Sécurité de l'authentification centralisée

## 20.1. Protéger le transport

Les échanges avec un annuaire central doivent être protégés conformément à la politique de sécurité.

Pour LDAP, cela implique notamment l'utilisation correcte de TLS lorsque le mécanisme le demande.

La validation des certificats doit rester activée.

Pour Active Directory, les mécanismes de découverte de services, d'authentification et de communication doivent respecter les exigences de l'environnement.

Il ne faut pas simplifier la configuration au point d'accepter n'importe quel serveur ou certificat.

## 20.2. Réduire les privilèges du compte d'enrôlement

Le compte utilisé pour joindre un serveur au domaine ne devrait disposer que des droits nécessaires.

Un compte de domaine généraliste possédant des privilèges très élevés ne doit pas être utilisé automatiquement lorsqu'une délégation plus limitée est possible.

Le compte technique d'enrôlement doit être protégé et géré selon la politique de l'organisation.

## 20.3. Restreindre l'accès au serveur Linux

Le fait qu'un utilisateur existe dans l'annuaire ne signifie pas qu'il doit pouvoir ouvrir une session sur chaque serveur.

La politique doit définir les groupes ou utilisateurs autorisés.

```text
Annuaire d'entreprise
        |
        v
Utilisateurs et groupes
        |
        v
Politique d'accès du serveur
        |
        +-- Groupe autorisé
        |
        +-- Groupe non autorisé
```

Le contrôle d'accès doit être testé avant le déploiement.

Il est également important de disposer d'un accès de secours administré de manière sûre.

## 20.4. Protéger les fichiers de configuration

Des fichiers comme `/etc/sssd/sssd.conf` ou certaines configurations LDAP peuvent contenir des informations sensibles ou des références à des comptes de service.

Vérifie les permissions :

```bash
ls -l /etc/sssd/sssd.conf
```

Protège les fichiers qui contiennent des secrets ou des identifiants techniques.

Ne copie pas ces fichiers dans un dépôt public ou un document partagé sans contrôle.

## 20.5. Gestion des certificats

Dans une infrastructure utilisant une autorité de certification interne, les clients doivent faire confiance à la bonne autorité.

Il faut également vérifier que le certificat présenté correspond au serveur contacté.

Ne contourne pas les erreurs de certificat en désactivant la validation.

Les erreurs doivent être corrigées au niveau des noms, certificats, chaînes de confiance ou paramètres concernés.

## 20.6. Comptes administratifs

Les comptes appartenant aux groupes administratifs doivent faire l'objet d'un contrôle renforcé.

Examine :

```bash
id alice
sudo -l
```

Pour une politique de domaine, inspecte aussi les règles d'accès et les groupes configurés.

Ne confonds pas appartenance à un groupe, authentification réussie et privilège administratif global.

## 20.7. Journalisation

Les journaux peuvent permettre de comprendre :

- Les échecs de connexion.
- Les problèmes DNS.
- Les problèmes de résolution d'identités.
- Les erreurs de connexion à l'annuaire.
- Les problèmes d'authentification Kerberos.
- Les refus liés aux règles d'accès.

Mais ils doivent être protégés contre l'accès non autorisé et la divulgation de secrets.

## 20.8. Plan de récupération

Avant de modifier PAM, SSH ou SSSD :

- Prévois une console locale ou un accès de secours.
- Sauvegarde la configuration.
- Note l'état initial.
- Vérifie les droits administratifs.
- Prépare une procédure de retour arrière.
- Effectue les tests avec un compte non critique.
- Conserve une session administrative de secours tant que la nouvelle configuration n'est pas validée.

Cette précaution évite qu'une erreur de configuration coupe l'accès à distance.


# 21. Audit et diagnostic avancé

## 21.1. Diagnostic : utilisateur AD inconnu

Commence par :

```bash
getent passwd 'alice@ad.example.test'
```

Si aucune entrée n'est renvoyée, examine l'identité et le domaine.

### Vérifier le domaine

```bash
realm list
```

### Vérifier SSSD

```bash
systemctl status sssd
```

### Consulter les journaux

```bash
sudo journalctl -u sssd --since "30 minutes ago"
```

### Vérifier DNS

```bash
dig SRV _ldap._tcp.ad.example.test
dig SRV _kerberos._tcp.ad.example.test
```

### Vérifier l'identité

```bash
id 'alice@ad.example.test'
```

Il faut ensuite déterminer si le problème concerne :

- Le domaine non découvert.
- Un échec d'adhésion.
- SSSD arrêté.
- Le DNS.
- Le réseau.
- La correspondance d'identifiants.
- Le nom de connexion employé.
- Le cache.

Ne change pas les UID/GID avant d'avoir identifié la cause.

## 21.2. Diagnostic : compte résolu, connexion refusée

Si `id` fonctionne mais la connexion échoue, l'identité est au moins résolue dans ce contexte.

Il faut ensuite examiner l'authentification et la politique d'accès.

Vérifie :

```bash
realm list
```

Puis :

```bash
sudo journalctl -u sssd --since "30 minutes ago"
```

Pour SSH, examine également les journaux du service et la configuration de PAM.

Le compte peut être connu sans être autorisé à ouvrir une session.

## 21.3. Diagnostic : erreurs Kerberos

Commence par :

```bash
timedatectl
```

Puis vérifie DNS :

```bash
dig SRV _kerberos._tcp.ad.example.test
```

Si l'outil est disponible :

```bash
klist
```

Pour examiner une acquisition de ticket dans un environnement de test :

```bash
kinit alice@AD.EXAMPLE.TEST
```

Les problèmes Kerberos peuvent concerner :

- L'heure.
- Le royaume.
- Le nom du principal.
- DNS.
- La connectivité au KDC.
- Les règles de chiffrement.
- Les informations d'identification.
- La configuration du client.

Les erreurs ne doivent pas être traitées uniquement comme des erreurs de mot de passe.

## 21.4. Diagnostic : LDAP inaccessible

Avec les outils appropriés :

```bash
ldapsearch -x \
  -H ldaps://ldap01.example.test \
  -b "dc=example,dc=test" \
  "(uid=alice)" uid
```

Si cela échoue, examine :

- La résolution DNS.
- La connexion réseau.
- Le certificat du serveur.
- La base de recherche.
- Les droits du compte de recherche.
- Les paramètres TLS.
- Le schéma de l'annuaire.

Les réponses détaillées dépendent du client LDAP et du serveur.

## 21.5. Diagnostic : problème TLS

Vérifie :

- Le nom du serveur utilisé.
- Le certificat présenté.
- La chaîne d'autorités de certification.
- L'heure du client et du serveur.
- La validité du certificat.
- La configuration de confiance.

Une erreur TLS doit être traitée comme un problème de confiance ou de transport jusqu'à ce que les observations prouvent une autre cause.

Il est dangereux de désactiver la validation du certificat uniquement pour permettre la connexion.

## 21.6. Diagnostic : accès refusé à un fichier

Si l'authentification réussit mais qu'un fichier reste inaccessible, examine la politique locale.

```bash
id 'alice@ad.example.test'
```

Puis :

```bash
namei -l /srv/projets/rapport.txt
```

Si les ACL sont utilisées :

```bash
getfacl /srv/projets
getfacl /srv/projets/rapport.txt
```

Vérifie également les options de montage et le chemin complet.

L'authentification centralisée ne dispense pas d'analyser les permissions Unix.

## 21.7. Diagnostic : SSSD ne démarre pas

Commence par :

```bash
systemctl status sssd
```

Puis :

```bash
sudo journalctl -u sssd -b
```

Vérifie aussi les permissions du fichier :

```bash
ls -l /etc/sssd/sssd.conf
```

Les causes possibles incluent :

- Une erreur de syntaxe.
- Un paramètre incompatible avec la version.
- Des permissions incorrectes.
- Un domaine mal défini.
- Un fournisseur incorrect.
- Une dépendance manquante.
- Une configuration réseau ou TLS défaillante.

Ne remplace pas tout le fichier de configuration avant de conserver l'état initial et d'avoir identifié l'erreur.

## 21.8. Construire un tableau de diagnostic

| Symptôme | Première vérification | Causes possibles |
|---|---|---|
| Utilisateur inconnu | `getent passwd ...` | DNS, SSSD, fournisseur ou nom incorrect |
| Groupe absent | `id utilisateur` | Groupe non résolu ou appartenance incorrecte |
| Connexion refusée | Journaux SSSD/PAM/SSH | Politique d'accès, authentification ou expiration |
| Kerberos échoue | Heure, DNS, `kinit` | Royaume, KDC, principal, horloge ou secrets |
| LDAP échoue | `ldapsearch`, TLS | Serveur, certificat, DN ou permissions |
| Répertoire personnel absent | `getent passwd ...` | Configuration de session ou stockage |
| Permission refusée | `namei`, `getfacl` | Permissions, groupes ou ACL |
| SSSD arrêté | `systemctl`, journaux | Configuration, permissions ou dépendances |
| Accès persistant après retrait | Sessions et caches | Session existante, cache ou autre mécanisme d'accès |


# 22. Automatisation de la gestion des identités

## 22.1. Pourquoi automatiser ?

L'automatisation réduit certaines opérations manuelles et facilite la standardisation.

Elle peut notamment servir à :

- Produire un inventaire de comptes.
- Vérifier la résolution des identités.
- Contrôler les appartenances aux groupes.
- Vérifier le statut des services.
- Comparer des groupes attendus et obtenus.
- Générer un rapport de diagnostic.

Les scripts ne doivent pas exposer les mots de passe ou les secrets du domaine.

## 22.2. Script de contrôle d'une intégration AD

Le script suivant rassemble plusieurs contrôles en lecture seule.

Il suppose que les outils correspondants sont installés et que le domaine réel est renseigné.

```bash
#!/usr/bin/env bash

set -u

DOMAIN="ad.example.test"
USER_NAME="alice@ad.example.test"

echo "=========================================="
echo "RAPPORT D'INTÉGRATION AD / SSSD"
echo "Date : $(date -Is)"
echo "Hôte : $(hostname)"
echo "Domaine : ${DOMAIN}"
echo "=========================================="

echo
echo "=== État du domaine ==="

if command -v realm >/dev/null 2>&1; then
    realm list
else
    echo "Outil realm indisponible."
fi

echo
echo "=== État de SSSD ==="

if systemctl is-active --quiet sssd; then
    echo "SSSD est actif."
else
    echo "SSSD n'est pas actif."
fi

echo
echo "=== Résolution de l'utilisateur ==="

if getent passwd "${USER_NAME}"; then
    echo "Utilisateur résolu : ${USER_NAME}"
else
    echo "Utilisateur non résolu : ${USER_NAME}"
fi

echo
echo "=== Groupes de l'utilisateur ==="

if id "${USER_NAME}" 2>/dev/null; then
    :
else
    echo "Impossible d'obtenir l'identité complète."
fi

echo
echo "=== DNS LDAP ==="

if command -v dig >/dev/null 2>&1; then
    dig +short SRV "_ldap._tcp.${DOMAIN}"
else
    echo "Outil dig indisponible."
fi

echo
echo "=== DNS Kerberos ==="

if command -v dig >/dev/null 2>&1; then
    dig +short SRV "_kerberos._tcp.${DOMAIN}"
else
    echo "Outil dig indisponible."
fi

echo
echo "=== Synchronisation de l'heure ==="

if command -v timedatectl >/dev/null 2>&1; then
    timedatectl
else
    echo "Outil timedatectl indisponible."
fi

echo
echo "Fin du rapport."
```

Ce script ne modifie volontairement pas l'appartenance au domaine ni les politiques d'accès.

Il faut remplacer les noms d'exemple par les valeurs réelles et vérifier que les commandes disponibles correspondent au système.

## 22.3. Automatiser l'audit, pas les privilèges à l'aveugle

Une automatisation de sécurité devrait comparer l'état observé à un état attendu.

Exemple :

```text
Groupe attendu : Linux-Admins
Membres attendus : comptes approuvés
État observé : membres réellement résolus
                   |
                   v
              Comparaison
                   |
         +---------+---------+
         |                   |
         v                   v
      Conforme          Écart détecté
                             |
                             v
                       Rapport d'audit
```

Il est généralement préférable de signaler un écart avant de retirer automatiquement des accès.

Une correction automatique peut être utilisée dans un environnement contrôlé, mais elle doit respecter les procédures de validation et de retour arrière.

## 22.4. Gestion de configuration

Dans un environnement professionnel, des outils de gestion de configuration peuvent aider à maintenir les fichiers, services et politiques cohérents.

Ils ne remplacent pas la compréhension des mécanismes LDAP, AD, Kerberos, NSS, PAM et SSSD.

Un outil d'automatisation peut appliquer une configuration incorrecte avec une grande efficacité. La qualité dépend donc de l'état souhaité défini par l'administrateur.


# 23. Laboratoires pratiques guidés

Les exercices sont organisés de manière progressive.

Les opérations d'intégration AD et LDAP doivent être réalisées dans un environnement de test disposant d'un annuaire fonctionnel.

## Laboratoire 1 — Comprendre la résolution d'identité

### Objectif

Distinguer les comptes locaux de ceux résolus par les sources configurées.

### Étape 1 : examiner les comptes locaux

```bash
cat /etc/passwd
```

### Étape 2 : examiner la base d'identités du système

```bash
getent passwd
```

### Étape 3 : examiner NSS

```bash
grep -E '^(passwd|group|shadow):' /etc/nsswitch.conf
```

### Étape 4 : tester une identité connue

```bash
id
```

### Travail demandé

Explique pourquoi `/etc/passwd` ne représente pas nécessairement toutes les identités utilisables sur un serveur centralisé.

### Validation

Tu dois pouvoir expliquer le rôle de NSS et de `getent`.


## Laboratoire 2 — Explorer un annuaire LDAP

### Objectif

Comprendre la structure de recherche LDAP et les attributs POSIX.

### Prérequis

Un serveur LDAP de laboratoire opérationnel et un nom d'hôte valide.

### Étape 1 : rechercher un utilisateur

```bash
ldapsearch -x \
  -H ldaps://ldap01.example.test \
  -b "dc=example,dc=test" \
  "(uid=alice)" \
  uid cn uidNumber gidNumber homeDirectory loginShell
```

Cette commande suppose que la recherche soit autorisée et que le serveur soit configuré correctement.

### Étape 2 : identifier les attributs

Repère :

- `uid`.
- `uidNumber`.
- `gidNumber`.
- `homeDirectory`.
- `loginShell`.

### Étape 3 : étudier le DN

Repère le champ `dn` et explique comment il se rapporte à la base de recherche.

### Travail demandé

Rédige la définition du DN, de l'OU, du DC composant du DN et du schéma LDAP.

### Validation

Tu dois pouvoir distinguer le nom de connexion du DN complet et expliquer l'utilisation des attributs POSIX.


## Laboratoire 3 — Vérifier la découverte d'Active Directory

### Objectif

Valider les prérequis réseau avant d'intégrer le serveur Linux.

### Étape 1 : contrôler l'heure

```bash
timedatectl
```

### Étape 2 : contrôler DNS

```bash
resolvectl status
```

### Étape 3 : rechercher LDAP

```bash
dig SRV _ldap._tcp.ad.example.test
```

### Étape 4 : rechercher Kerberos

```bash
dig SRV _kerberos._tcp.ad.example.test
```

### Étape 5 : effectuer la découverte du domaine

```bash
realm discover ad.example.test
```

### Travail demandé

Identifie les résultats qui montrent que le domaine est découvert correctement.

### Validation

Tu dois savoir distinguer un problème de découverte du domaine d'un problème de connexion utilisateur.


## Laboratoire 4 — Joindre un domaine Active Directory

### Objectif

Intégrer un serveur Linux de test à un domaine AD.

### Prérequis

- Domaine AD opérationnel.
- DNS fonctionnel.
- Heure correcte.
- Compte autorisé à joindre des machines au domaine.
- Accès administratif local.
- Possibilité de récupérer la machine en cas d'erreur.

### Étape 1 : installer les outils

Sur Ubuntu :

```bash
sudo apt update
sudo apt install sssd-ad sssd-tools realmd adcli
```

### Étape 2 : découvrir le domaine

```bash
sudo realm discover ad.example.test
```

### Étape 3 : joindre le domaine

```bash
sudo realm join --user=join-linux ad.example.test
```

Saisis les informations d'authentification lorsque le système les demande.

### Étape 4 : vérifier le résultat

```bash
realm list
```

### Étape 5 : vérifier SSSD

```bash
systemctl status sssd
```

### Étape 6 : vérifier un utilisateur du domaine

```bash
getent passwd 'alice@ad.example.test'
id 'alice@ad.example.test'
```

### Étape 7 : vérifier les journaux

```bash
sudo journalctl -u sssd --since "15 minutes ago"
```

### Validation

Le domaine doit apparaître comme configuré, le service doit être fonctionnel et le compte doit être correctement résolu.

Ne passe pas à la configuration des restrictions d'accès avant de confirmer ces étapes.


## Laboratoire 5 — Restreindre l'accès à un groupe

### Objectif

Comprendre la différence entre adhésion au domaine et autorisation de se connecter.

### Étape 1 : examiner les groupes

```bash
id 'alice@ad.example.test'
```

### Étape 2 : afficher l'état de realmd

```bash
realm list
```

### Étape 3 : déterminer le groupe à autoriser

Le groupe doit exister dans l'annuaire et être correctement résolu par Linux.

### Étape 4 : définir une politique de laboratoire

Une commande de restriction peut être utilisée si elle correspond au modèle de politique choisi, par exemple :

```bash
sudo realm permit --groups 'Linux-Admins@ad.example.test'
```

**Ne lance cette commande que dans le laboratoire et après avoir vérifié que le groupe et le compte de secours sont adaptés.**

La commande peut modifier le fournisseur d'accès utilisé par SSSD.

### Étape 5 : vérifier la politique obtenue

```bash
realm list
```

Puis examine la configuration SSSD et les journaux.

### Validation

Tu dois pouvoir expliquer pourquoi un utilisateur appartenant au domaine peut être refusé par un serveur Linux qui n'autorise que certains groupes.


## Laboratoire 6 — Comprendre un problème LDAP TLS

### Objectif

Distinguer la connexion réseau de la confiance accordée au certificat.

### Étape 1 : effectuer une recherche LDAP sécurisée

```bash
ldapsearch -x \
  -H ldaps://ldap01.example.test \
  -b "dc=example,dc=test" \
  "(uid=alice)" uid
```

### Étape 2 : consulter le message d'erreur

Détermine s'il s'agit notamment :

- D'un problème DNS.
- D'une connexion impossible.
- D'une erreur de certificat.
- D'un refus d'accès.
- D'un DN de base incorrect.

### Étape 3 : vérifier le certificat

Utilise les outils et la documentation de ton environnement pour vérifier le certificat, le nom du serveur et l'autorité de certification.

### Validation

Tu dois expliquer pourquoi désactiver la validation du certificat n'est pas une solution acceptable en production.


## Laboratoire 7 — Vérifier Kerberos

### Objectif

Comprendre les tickets Kerberos et les conditions de base de l'authentification.

### Étape 1 : contrôler l'heure

```bash
timedatectl
```

### Étape 2 : vérifier DNS

```bash
dig SRV _kerberos._tcp.ad.example.test
```

### Étape 3 : consulter les tickets

```bash
klist
```

### Étape 4 : demander un ticket dans le domaine de test

```bash
kinit alice@AD.EXAMPLE.TEST
```

### Étape 5 : examiner le résultat

```bash
klist
```

### Validation

Tu dois pouvoir expliquer le rôle du TGT et distinguer l'authentification par tickets de l'autorisation d'accéder à une ressource.


## Laboratoire 8 — Tester les permissions d'un groupe centralisé

### Objectif

Relier les groupes AD ou LDAP aux permissions Linux.

### Étape 1 : vérifier le compte

```bash
id 'alice@ad.example.test'
```

### Étape 2 : créer un répertoire de laboratoire

```bash
sudo mkdir -p /srv/projets-lab
```

### Étape 3 : identifier le groupe effectivement reconnu

Consulte les groupes visibles avec `id` et les résultats de `getent`.

### Étape 4 : attribuer le groupe approprié

Utilise le nom ou l'identifiant de groupe réellement résolu sur le système.

### Étape 5 : configurer les permissions

Une fois le groupe confirmé :

```bash
sudo chmod 2770 /srv/projets-lab
```

Les permissions de partage doivent être associées au propriétaire et au groupe appropriés.

### Étape 6 : tester

Utilise le compte de laboratoire pour créer un fichier, puis examine les propriétaires et permissions.

### Validation

Tu dois expliquer pourquoi l'authentification centralisée ne remplace pas les contrôles de permissions.


# 24. Exercices d'entraînement corrigés

## Exercice 1 — LDAP et Active Directory

Quelle affirmation est correcte ?

A. LDAP et Active Directory sont exactement la même chose.

B. LDAP est un protocole d'accès à un annuaire ; AD DS est un service d'annuaire qui utilise plusieurs technologies, dont LDAP et Kerberos.

C. Kerberos est un système de fichiers.

D. Active Directory ne contient pas de groupes.

**Correction : B.**

LDAP définit un protocole de communication avec un annuaire. Active Directory Domain Services gère les objets d'un domaine et s'intègre à plusieurs mécanismes, notamment LDAP, Kerberos et DNS.

## Exercice 2 — NSS et PAM

Quelle est la principale différence entre NSS et PAM ?

**Correction :**

NSS permet au système de rechercher des informations telles que les utilisateurs et les groupes.

PAM permet aux services compatibles d'utiliser une chaîne de modules pour traiter l'authentification, les vérifications du compte, les changements de mot de passe et les sessions.

Ils sont complémentaires, mais ils ne remplissent pas la même fonction.

## Exercice 3 — SSSD

Pourquoi SSSD est-il utile dans un environnement Linux centralisé ?

**Correction :**

SSSD peut intégrer Linux à des fournisseurs d'identités tels qu'Active Directory ou LDAP. Selon la configuration, il fournit la résolution des comptes et des groupes, l'authentification, des contrôles d'accès et un cache.

Il sert d'intermédiaire entre les mécanismes Linux et les sources d'identités.

## Exercice 4 — Utilisateur inconnu

La commande suivante ne produit aucune sortie :

```bash
getent passwd 'alice@ad.example.test'
```

Peut-on conclure automatiquement que le compte n'existe pas dans Active Directory ?

**Correction : Non.**

Il peut exister dans AD, mais ne pas être résolu en raison d'un problème de configuration, de cache, de DNS, d'accès à l'annuaire ou de nom de connexion.

Il faut examiner le domaine, SSSD, les journaux et la configuration.

## Exercice 5 — DNS et AD

Pourquoi DNS est-il important dans une intégration Active Directory ?

**Correction :**

DNS permet notamment de découvrir les services du domaine au moyen d'enregistrements appropriés.

Si le client utilise le mauvais résolveur ou ne peut pas consulter les enregistrements attendus, la découverte des contrôleurs et des services peut échouer.

## Exercice 6 — Kerberos et heure

Pourquoi un décalage important d'heure peut-il provoquer une erreur Kerberos ?

**Correction :**

Kerberos utilise des informations de validité temporelle pour ses tickets et certains mécanismes de protection.

Un écart trop important entre les systèmes peut entraîner le rejet d'une requête ou d'un ticket.

Il faut vérifier la synchronisation de l'heure et la configuration du domaine.

## Exercice 7 — UID et SID

Pourquoi un SID Active Directory ne peut-il pas être utilisé directement comme UID Unix ?

**Correction :**

Un SID est un identifiant de sécurité Windows, tandis que les permissions POSIX utilisent des UID et GID numériques.

Il faut donc une méthode de correspondance entre les identités AD et les identifiants utilisés par Linux.

Cette correspondance doit rester cohérente dans les environnements multi-serveurs.

## Exercice 8 — Adhésion au domaine

Un serveur Linux a rejoint le domaine AD, mais Alice ne peut pas ouvrir une session SSH.

Quelles vérifications effectuer ?

**Correction :**

Il faut vérifier :

1. L'état du domaine avec `realm list`.
2. L'état de SSSD.
3. La résolution du compte avec `getent` et `id`.
4. Les groupes connus du serveur.
5. La politique d'accès de realmd/SSSD.
6. La configuration SSH et PAM.
7. Les journaux du service.
8. Les autres conditions d'authentification.

L'adhésion au domaine ne garantit pas automatiquement que tous les utilisateurs soient autorisés à se connecter.

## Exercice 9 — Authentification et autorisation

Alice s'authentifie correctement mais reçoit `Permission denied` lorsqu'elle ouvre `/srv/projets/rapport.txt`.

Pourquoi le problème ne relève-t-il pas nécessairement de l'authentification ?

**Correction :**

L'authentification permet de vérifier l'identité d'Alice.

L'accès au fichier dépend des permissions, des groupes, des ACL, du chemin complet et éventuellement des règles du système de fichiers ou de l'application.

Il faut examiner `id`, `namei -l` et `getfacl`.

## Exercice 10 — Cache SSSD

Pourquoi le cache SSSD doit-il être traité avec prudence lors d'un incident ?

**Correction :**

Le cache peut permettre certains accès lorsque l'annuaire est indisponible, selon la configuration.

Mais il peut aussi contenir des informations qui ne reflètent pas encore un changement récent dans la source centrale.

Il ne faut donc pas effacer le cache ou supposer qu'il correspond automatiquement à l'état actuel du domaine.

## Exercice 11 — Compte de domaine retiré

Un utilisateur est supprimé dans l'annuaire mais son ancienne session reste active sur un serveur Linux.

Est-ce forcément une incohérence de l'annuaire ?

**Correction : Non.**

Une session déjà ouverte peut continuer d'exister malgré le retrait du compte centralisé.

Il faut appliquer une procédure adaptée aux sessions et accès actifs, et vérifier les politiques de sécurité du système.

## Exercice 12 — TLS

Pourquoi ne faut-il pas désactiver la validation du certificat LDAP pour corriger une erreur de connexion ?

**Correction :**

La validation permet notamment de confirmer que le client contacte le serveur attendu, selon la chaîne de confiance et les noms associés au certificat.

La désactiver peut permettre à un serveur non approuvé de se faire passer pour l'annuaire.

Il faut corriger le nom DNS, le certificat ou la chaîne de confiance.

## Exercice 13 — Groupe administratif

Un utilisateur appartient au groupe AD `Linux-Admins`.

Est-il automatiquement autorisé à exécuter n'importe quelle commande avec `sudo` sur tous les serveurs Linux ?

**Correction : Non.**

Cela dépend de la configuration effective des règles `sudo`, de la résolution du groupe et des autorisations définies localement ou de manière centralisée.

Le nom du groupe ne suffit pas à accorder des privilèges.

## Exercice 14 — Compte de service

Pourquoi un compte de service doit-il généralement disposer de droits limités ?

**Correction :**

Un service compromis ou mal configuré ne devrait pas pouvoir modifier tout le système sans nécessité.

Un compte dédié permet de limiter les ressources accessibles et les conséquences potentielles d'une compromission.


# 25. Défi final : intégrer un serveur Linux au domaine d'une entreprise

## 25.1. Contexte

Tu es administrateur système d'une entreprise qui utilise Active Directory pour ses identités.

L'entreprise ajoute un serveur Linux destiné à héberger une application interne.

Elle veut éviter de créer les comptes utilisateurs séparément sur chaque serveur Linux.

Tu dois intégrer le serveur à l'architecture centralisée et préparer une configuration exploitable et documentée.

## 25.2. Architecture de laboratoire

```text
              Active Directory
              ad.example.test
                      |
          +-----------+-----------+
          |                       |
          v                       v
        DC01                   DC02
          |
          v
   Annuaire et Kerberos
          |
          v
   DNS du domaine
          |
          v
    Serveur Linux
    linux01
          |
    +-----+-----+
    |           |
    v           v
   NSS         PAM
    |           |
    +-----+-----+
          |
          v
        SSSD
          |
          v
 Utilisateurs centralisés
```

Cette représentation est simplifiée et n'exige pas que tous les mécanismes soient servis par le même contrôleur.

## 25.3. Objectifs de la mission

Tu dois :

1. Vérifier le nom d'hôte.
2. Vérifier le DNS.
3. Vérifier l'heure.
4. Installer les outils d'intégration nécessaires.
5. Découvrir le domaine.
6. Joindre le serveur au domaine.
7. Vérifier SSSD.
8. Résoudre un utilisateur et ses groupes.
9. Définir la politique d'accès.
10. Tester une connexion autorisée.
11. Tester l'accès aux fichiers.
12. Préparer le dépannage.
13. Documenter les opérations de retrait d'accès.

Le compte utilisé pour joindre le domaine doit posséder les droits appropriés.

## 25.4. Mission 1 — Préparer le réseau

Vérifie :

```bash
hostnamectl
hostname -f
resolvectl status
timedatectl
```

Recherche les enregistrements SRV :

```bash
dig SRV _ldap._tcp.ad.example.test
dig SRV _kerberos._tcp.ad.example.test
```

**Validation :**

Le client doit posséder un nom cohérent, utiliser le DNS attendu et disposer d'une heure correctement synchronisée.

## 25.5. Mission 2 — Installer les paquets

Sur Ubuntu :

```bash
sudo apt update
sudo apt install sssd-ad sssd-tools realmd adcli
```

Vérifie que les outils sont présents.

**Validation :**

Les outils nécessaires doivent être installés et la machine doit pouvoir interroger le domaine.

## 25.6. Mission 3 — Découvrir le domaine

```bash
sudo realm discover ad.example.test
```

En cas d'échec, documente le message et identifie la couche à corriger.

**Validation :**

La découverte doit reconnaître le domaine et les composants disponibles.

## 25.7. Mission 4 — Joindre le domaine

```bash
sudo realm join --user=join-linux ad.example.test
```

Utilise un compte autorisé à joindre la machine.

Ne stocke pas son mot de passe dans un script.

**Validation :**

La commande doit confirmer la réussite de l'adhésion.

## 25.8. Mission 5 — Vérifier l'intégration

```bash
realm list
systemctl status sssd
```

Puis :

```bash
getent passwd 'alice@ad.example.test'
id 'alice@ad.example.test'
```

Examine les journaux :

```bash
sudo journalctl -u sssd --since "15 minutes ago"
```

**Validation :**

L'identité doit être correctement résolue et le service SSSD doit fonctionner.

## 25.9. Mission 6 — Définir les accès autorisés

Détermine quel groupe doit accéder au serveur.

Examine l'appartenance de l'utilisateur :

```bash
id 'alice@ad.example.test'
```

Puis :

```bash
realm list
```

Ne suppose pas qu'une intégration réussie autorise uniquement les personnes prévues.

Définis explicitement la politique d'accès et vérifie le modèle d'autorisation utilisé par SSSD.

**Validation :**

La politique doit autoriser les comptes prévus sans ouvrir inutilement le serveur à tous les utilisateurs du domaine.

## 25.10. Mission 7 — Gérer le répertoire personnel

Vérifie le répertoire déclaré ou le modèle de répertoire utilisé :

```bash
getent passwd 'alice@ad.example.test'
```

Si le répertoire personnel doit être créé automatiquement à la première connexion sur Ubuntu, vérifie le mécanisme de création de répertoires personnels basé sur PAM.

Après le test, contrôle :

```bash
ls -ld /home/alice*
```

**Validation :**

Le compte doit pouvoir utiliser un répertoire approprié, avec les permissions attendues.

## 25.11. Mission 8 — Tester SSH

Effectue une connexion de test à partir d'un autre poste :

```bash
ssh -l 'alice@ad.example.test' linux01.ad.example.test
```

Si la connexion échoue, collecte les journaux SSH et SSSD.

**Validation :**

Le compte autorisé doit pouvoir ouvrir une session selon la méthode d'authentification prévue.

## 25.12. Mission 9 — Vérifier les permissions

Créer ou utiliser un répertoire de test.

Examiner :

```bash
id 'alice@ad.example.test'
ls -ld /srv/projets
namei -l /srv/projets
```

Si des ACL sont employées :

```bash
getfacl /srv/projets
```

**Validation :**

L'accès doit correspondre à la politique de développement et ne doit pas dépendre d'un privilège administratif inutile.

## 25.13. Mission 10 — Préparer la procédure de retrait d'accès

Rédige une procédure indiquant comment retirer l'accès d'Alice.

Elle doit notamment traiter :

- Le retrait du groupe concerné dans l'annuaire.
- Les règles locales d'accès qui pourraient encore l'autoriser.
- Les éventuelles sessions actives.
- Les clés SSH et autres mécanismes d'authentification.
- Les fichiers appartenant à son UID.
- Les données qu'il faut conserver.
- Les tests de validation après retrait.

**Validation :**

La procédure doit pouvoir être appliquée sans supprimer aveuglément des fichiers ni couper l'accès de tous les administrateurs.

## 25.14. Mission 11 — Présenter l'architecture

Produis un schéma final comparable à celui-ci :

```text
                Domaine Active Directory
                         |
                         v
                 Utilisateurs / Groupes
                         |
                         v
                DNS et services du domaine
                         |
                         v
                    Serveur Linux
                         |
                         v
                        SSSD
                         |
               +---------+---------+
               |                   |
               v                   v
              NSS                  PAM
               |                   |
               v                   v
       Identités et groupes   Authentification
               |                   |
               +---------+---------+
                         |
                         v
                  Politique locale
                         |
              +----------+----------+
              |                     |
              v                     v
           Connexion            Permissions
           au serveur           sur les fichiers
```

Ajoute les informations réelles observées dans ton laboratoire, notamment :

- Le nom du domaine.
- Le nom du serveur.
- Le mode d'identification des comptes.
- Les groupes autorisés.
- Le mécanisme de création des répertoires personnels.
- La méthode de dépannage.
- Les limites de la solution.

**Critère final :** un autre administrateur doit pouvoir comprendre la chaîne d'authentification, vérifier le domaine, retrouver les groupes et retirer un accès en suivant la procédure documentée.


# 26. Correction détaillée du défi final

Cette correction représente une démarche de référence pour un laboratoire Ubuntu déjà connecté à un réseau Active Directory opérationnel.

Les domaines, noms de comptes et noms d'hôtes sont fictifs.

## 26.1. Vérifier le réseau

```bash
hostnamectl
resolvectl status
timedatectl
```

Le client doit pouvoir résoudre le domaine et joindre les services nécessaires.

## 26.2. Installer les outils

```bash
sudo apt update
sudo apt install sssd-ad sssd-tools realmd adcli
```

Les dépendances sont installées selon la distribution et sa version.

## 26.3. Découvrir le domaine

```bash
sudo realm discover ad.example.test
```

Si la découverte échoue, vérifie le DNS et la connectivité avant de continuer.

## 26.4. Joindre le domaine

```bash
sudo realm join --user=join-linux ad.example.test
```

Saisis le secret lorsqu'il est demandé.

Une adhésion réussie doit être suivie d'une vérification explicite.

## 26.5. Vérifier SSSD

```bash
realm list
systemctl status sssd
sudo journalctl -u sssd --since "15 minutes ago"
```

Confirme que le domaine est configuré et que le service fonctionne.

## 26.6. Vérifier l'identité

```bash
getent passwd 'alice@ad.example.test'
id 'alice@ad.example.test'
```

L'utilisateur doit être résolu par le système.

Si ce n'est pas le cas, examiner la configuration du domaine, DNS et les journaux SSSD.

## 26.7. Examiner les groupes

```bash
id 'alice@ad.example.test'
```

Cette commande donne une vue utile des groupes reconnus pour le compte.

Les noms et identifiants doivent être cohérents avec la politique définie.

## 26.8. Contrôler l'accès

Vérifie la politique :

```bash
realm list
```

Puis examine les paramètres SSSD et la configuration SSH.

Les comptes autorisés doivent pouvoir ouvrir une session ; les autres doivent être soumis à la restriction prévue.

## 26.9. Contrôler le répertoire personnel et les droits

```bash
getent passwd 'alice@ad.example.test'
ls -ld /home/alice*
```

La création d'un répertoire personnel doit être prévue dans la configuration.

Pour les répertoires partagés, vérifie le groupe, les permissions et les ACL.

## 26.10. Valider les opérations de retrait

Pour retirer un accès, il faut agir sur la source et les politiques concernées.

Après le retrait du groupe ou de la permission :

```bash
id 'alice@ad.example.test'
realm list
```

Si des sessions existaient auparavant, vérifie leur état et suis la politique de l'organisation concernant leur terminaison.

Ne considère pas l'opération terminée sans contrôler les autres méthodes d'accès associées au compte.


# 27. Checklist opérationnelle

## Avant l'intégration au domaine

- [ ] Vérifier le nom d'hôte.
- [ ] Confirmer le domaine DNS.
- [ ] Vérifier les enregistrements SRV.
- [ ] Contrôler la synchronisation de l'heure.
- [ ] Vérifier le réseau.
- [ ] Confirmer le compte autorisé à joindre la machine.
- [ ] Préserver un accès administrateur local de secours.
- [ ] Documenter les groupes qui devront accéder au serveur.

## Après l'intégration AD

- [ ] Vérifier `realm list`.
- [ ] Vérifier le service SSSD.
- [ ] Examiner les journaux.
- [ ] Résoudre un compte avec `getent`.
- [ ] Contrôler les groupes avec `id`.
- [ ] Vérifier la politique d'accès.
- [ ] Vérifier le mécanisme de création du répertoire personnel.
- [ ] Tester une connexion réellement utilisée.
- [ ] Contrôler les permissions des ressources.
- [ ] Documenter la configuration.

## Pour une intégration LDAP

- [ ] Identifier le DN de base.
- [ ] Identifier le schéma LDAP.
- [ ] Vérifier les attributs UID/GID.
- [ ] Contrôler les groupes.
- [ ] Vérifier DNS et connectivité.
- [ ] Configurer TLS et la validation des certificats.
- [ ] Protéger les comptes techniques.
- [ ] Configurer NSS et PAM.
- [ ] Tester `getent` et `id`.
- [ ] Tester l'authentification.
- [ ] Documenter le cache et la politique d'accès.

## Pour les groupes et les permissions

- [ ] Vérifier l'identité réelle du compte.
- [ ] Vérifier les groupes effectivement résolus.
- [ ] Définir les droits minimaux nécessaires.
- [ ] Appliquer les permissions appropriées.
- [ ] Examiner les ACL.
- [ ] Tester les accès avec le compte concerné.
- [ ] Éviter les permissions excessives.
- [ ] Documenter les exceptions.

## Pour le retrait d'un compte

- [ ] Retirer les autorisations centrales appropriées.
- [ ] Examiner les accès locaux.
- [ ] Contrôler les clés SSH.
- [ ] Vérifier les sessions actives.
- [ ] Examiner les privilèges `sudo`.
- [ ] Identifier les fichiers à conserver.
- [ ] Traiter les dépendances de services.
- [ ] Contrôler les groupes et ACL restants.
- [ ] Documenter le résultat.


# 28. Fiche de révision

## 28.1. Les notions principales

| Notion | Définition |
|---|---|
| LDAP | Protocole d'accès à un annuaire |
| Active Directory DS | Service d'annuaire de domaine Microsoft |
| Domaine AD | Ensemble logique d'objets gérés dans une structure de domaine |
| Contrôleur de domaine | Serveur qui fournit des services de domaine AD |
| DN | Nom distinctif d'une entrée LDAP |
| OU | Unité d'organisation dans un annuaire |
| Kerberos | Protocole d'authentification par tickets |
| SID | Identifiant de sécurité utilisé par Windows/AD |
| UID | Identifiant numérique de l'utilisateur sous Linux |
| GID | Identifiant numérique d'un groupe |
| NSS | Résolution des identités et d'autres bases système |
| PAM | Architecture modulaire d'authentification et de sessions |
| SSSD | Composant client de gestion des identités et de l'authentification centralisées |
| realmd | Découverte et intégration des domaines pris en charge |
| adcli | Outil utilisé pour certaines opérations d'adhésion et de gestion AD |
| winbind | Composant d'intégration des identités de domaine, notamment avec Samba |

## 28.2. Commandes d'inventaire

| Commande | Fonction |
|---|---|
| `getent passwd alice` | Rechercher une identité |
| `getent group developpeurs` | Rechercher un groupe |
| `id alice` | Afficher l'UID, le GID et les groupes |
| `realm discover domaine` | Découvrir un domaine |
| `realm list` | Afficher les domaines configurés |
| `systemctl status sssd` | Vérifier l'état de SSSD |
| `journalctl -u sssd` | Examiner les journaux SSSD |
| `klist` | Examiner le cache de tickets Kerberos |
| `timedatectl` | Vérifier l'heure du système |
| `dig SRV _ldap._tcp.domaine` | Examiner les enregistrements LDAP SRV |
| `dig SRV _kerberos._tcp.domaine` | Examiner les enregistrements Kerberos SRV |

## 28.3. Commandes d'intégration AD courantes

| Commande | Fonction |
|---|---|
| `sudo apt install sssd-ad sssd-tools realmd adcli` | Installer les outils d'intégration sur Ubuntu |
| `sudo realm discover ad.example.test` | Découvrir le domaine |
| `sudo realm join --user=join-linux ad.example.test` | Joindre un domaine avec un compte autorisé |
| `realm list` | Vérifier la configuration du domaine |
| `getent passwd 'alice@ad.example.test'` | Vérifier la résolution d'un utilisateur |
| `id 'alice@ad.example.test'` | Examiner les groupes |
| `sudo journalctl -u sssd --since "15 minutes ago"` | Examiner les journaux récents |

## 28.4. Différences à retenir

| Question | Réponse |
|---|---|
| LDAP et AD sont-ils identiques ? | Non. LDAP est un protocole ; AD DS est un service d'annuaire. |
| NSS authentifie-t-il le mot de passe ? | Ce n'est pas sa fonction principale. Il résout notamment les identités. |
| PAM remplace-t-il NSS ? | Non. Il fournit une architecture de modules pour l'authentification et d'autres contrôles. |
| SSSD remplace-t-il AD ou LDAP ? | Non. C'est un composant client qui s'intègre à ces fournisseurs. |
| Joindre le domaine donne-t-il accès à tous les utilisateurs ? | Pas nécessairement ; il faut examiner la politique d'accès du serveur. |
| Un UID est-il un SID ? | Non. Ils appartiennent à des modèles d'identification différents. |
| Un compte résolu est-il automatiquement autorisé ? | Non. Résolution, authentification et autorisation sont distinctes. |
| Le cache SSSD contient-il toujours l'état actuel de l'annuaire ? | Pas nécessairement, notamment en cas d'indisponibilité du fournisseur. |
| Le groupe AD donne-t-il automatiquement accès à sudo ? | Non. Une politique `sudo` doit être configurée et vérifiée. |
| LDAP doit-il être protégé sur le réseau ? | Oui, le mécanisme de transport et la validation du certificat doivent répondre aux exigences de sécurité. |


# 29. Documentation de référence

Les ressources suivantes permettent d'approfondir les notions étudiées.

## LDAP

- RFC 4511 — Lightweight Directory Access Protocol : le protocole LDAP.  
  https://www.rfc-editor.org/rfc/rfc4511

- Documentation Ubuntu — Intégrer SSSD à LDAP.  
  https://ubuntu.com/server/docs/how-to/sssd/with-ldap/

- Documentation Ubuntu — Intégrer LDAP et Kerberos.  
  https://ubuntu.com/server/docs/how-to/sssd/with-ldap-and-kerberos/

## Active Directory

- Microsoft Learn — Vue d'ensemble d'Active Directory Domain Services.  
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/active-directory-domain-services-overview

- Documentation Ubuntu — Intégrer SSSD à Active Directory.  
  https://ubuntu.com/server/docs/how-to/sssd/with-active-directory/

- Documentation Ubuntu — Choisir une méthode d'intégration à Active Directory.  
  https://ubuntu.com/server/docs/explanation/active-directory/choosing-an-integration-method/

## Kerberos et SSSD

- RFC 4120 — The Kerberos Network Authentication Service.  
  https://www.rfc-editor.org/rfc/rfc4120

- Documentation SSSD — Présentation générale.  
  https://sssd.io/docs/introduction.html

- Documentation SSSD — Rejoindre un domaine Active Directory.  
  https://sssd.io/docs/ad/ad-provider.html

- Documentation Ubuntu — Dépannage SSSD.  
  https://ubuntu.com/server/docs/how-to/sssd/troubleshooting/

## Référence locale

Sur la machine de laboratoire, ces manuels peuvent également être utiles :

```bash
man getent
man nsswitch.conf
man pam
man sssd
man sssd.conf
man realm
man ldapsearch
man sudoers
```

La disponibilité et le contenu des manuels dépendent des paquets installés.


# Conclusion

L'authentification centralisée est une architecture composée de plusieurs mécanismes complémentaires.

LDAP permet d'accéder aux informations d'un annuaire. Active Directory organise les objets d'un domaine et fournit plusieurs services d'identité et d'authentification. Kerberos permet une authentification par tickets. NSS résout les identités et les groupes. PAM fournit des mécanismes modulaires pour l'authentification et les sessions. SSSD relie le client Linux aux fournisseurs centralisés, tandis que realmd facilite la découverte et l'intégration à certains domaines.

La maîtrise de ces composants permet de comprendre pourquoi une connexion peut échouer même lorsque le compte existe, pourquoi un utilisateur peut être authentifié sans être autorisé à accéder à un fichier et pourquoi les groupes centralisés doivent être cohérents avec les permissions locales.

Le modèle mental à retenir est le suivant :

```text
                  SOURCE D'IDENTITÉ
                   LDAP / AD DS
                         |
             +-----------+-----------+
             |                       |
             v                       v
          Identités              Authentification
          et groupes          Kerberos ou mécanisme
             |                   compatible
             v                       |
            NSS                     v
             |                     PAM
             |                       |
             +-----------+-----------+
                         |
                         v
                        SSSD
                         |
                         v
                 Politique du serveur
                         |
                +--------+--------+
                |                 |
                v                 v
           Accès SSH          Accès fichiers
                |                 |
                +--------+--------+
                         |
                         v
                   Audit et contrôle
```

Cette représentation est simplifiée : les flux exacts dépendent du fournisseur SSSD, de la configuration PAM, des services et des mécanismes d'autorisation.

**Le véritable objectif de l'administrateur intermédiaire n'est pas seulement de joindre une machine à un domaine : il est de comprendre l'ensemble de la chaîne, de contrôler les accès réellement accordés et de pouvoir diagnostiquer chaque couche lorsqu'une connexion échoue.**