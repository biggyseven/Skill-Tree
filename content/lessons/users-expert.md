# Utilisateurs et groupes Linux — Niveau expert
## Identités centralisées, architecture LDAP/Active Directory, sécurité, résilience et automatisation avancée


# Sommaire

1. [Présentation du niveau expert](#1-présentation-du-niveau-expert)
2. [Architecture experte de la gestion des identités](#2-architecture-experte-de-la-gestion-des-identités)
3. [Révision approfondie de LDAP et Active Directory](#3-révision-approfondie-de-ldap-et-active-directory)
4. [Kerberos avancé : tickets, keytabs et délégation](#4-kerberos-avancé--tickets-keytabs-et-délégation)
5. [SSSD expert : architecture, fournisseurs et contrôles](#5-sssd-expert--architecture-fournisseurs-et-contrôles)
6. [UID, GID, SID et stratégies de correspondance](#6-uid-gid-sid-et-stratégies-de-correspondance)
7. [Active Directory multi-domaines et relations d'approbation](#7-active-directory-multi-domaines-et-relations-dapprobation)
8. [LDAP avancé : sécurité, recherche, réplication et disponibilité](#8-ldap-avancé--sécurité-recherche-réplication-et-disponibilité)
9. [Politiques d'accès et autorisation centralisée](#9-politiques-daccès-et-autorisation-centralisée)
10. [PAM avancé et authentification multifacteur](#10-pam-avancé-et-authentification-multifacteur)
11. [sudo expert et délégation administrative](#11-sudo-expert-et-délégation-administrative)
12. [SSH, identités centralisées et accès privilégiés](#12-ssh-identités-centralisées-et-accès-privilégiés)
13. [Cycle de vie, révocation et gouvernance des identités](#13-cycle-de-vie-révocation-et-gouvernance-des-identités)
14. [Comptes de service, keytabs et secrets techniques](#14-comptes-de-service-keytabs-et-secrets-techniques)
15. [Cache SSSD, fonctionnement hors ligne et continuité de service](#15-cache-sssd-fonctionnement-hors-ligne-et-continuité-de-service)
16. [Architecture de sécurité et durcissement](#16-architecture-de-sécurité-et-durcissement)
17. [Audit, observabilité et conformité](#17-audit-observabilité-et-conformité)
18. [Dépannage expert par couche](#18-dépannage-expert-par-couche)
19. [Automatisation et gestion de configuration](#19-automatisation-et-gestion-de-configuration)
20. [Laboratoires pratiques avancés](#20-laboratoires-pratiques-avancés)
21. [Exercices experts corrigés](#21-exercices-experts-corrigés)
22. [Défi final : concevoir une architecture d'identité d'entreprise](#22-défi-final--concevoir-une-architecture-didentité-dentreprise)
23. [Correction détaillée du défi final](#23-correction-détaillée-du-défi-final)
24. [Checklist opérationnelle](#24-checklist-opérationnelle)
25. [Référence des commandes essentielles](#25-référence-des-commandes-essentielles)
26. [Documentation de référence](#26-documentation-de-référence)


# 1. Présentation du niveau expert

## 1.1. De la gestion des comptes à l'architecture d'identité

Au niveau débutant, nous avons appris à gérer les utilisateurs et les groupes Linux.

Au niveau intermédiaire, nous avons étudié l'intégration à LDAP et Active Directory, les rôles de NSS, PAM, SSSD, Kerberos et realmd, ainsi que les contrôles d'accès.

Le niveau expert aborde les situations qui apparaissent lorsque cette architecture devient critique pour l'entreprise.

Un administrateur expert doit pouvoir répondre à des questions telles que :

- Comment garantir que les identifiants d'un utilisateur restent cohérents sur plusieurs serveurs ?
- Comment intégrer un serveur Linux à un domaine Active Directory sans accorder l'accès à tous les utilisateurs du domaine ?
- Comment distinguer une erreur de résolution d'identité d'une erreur Kerberos ou d'un refus d'autorisation ?
- Comment gérer les groupes issus de domaines approuvés ?
- Quelle stratégie retenir pour les UID et GID dans une infrastructure multi-serveurs ?
- Comment diagnostiquer une panne SSSD sans supprimer aveuglément le cache ?
- Comment assurer la continuité de service lors d'une indisponibilité temporaire de l'annuaire ?
- Comment déléguer des privilèges administratifs sans créer un chemin indirect vers un shell root ?
- Comment retirer rapidement les accès d'un collaborateur qui quitte l'entreprise ?
- Comment sécuriser les comptes techniques et les secrets utilisés par les applications ?
- Comment automatiser les contrôles d'identité sans provoquer de changements non maîtrisés ?
- Comment prouver que les politiques d'accès sont réellement appliquées ?

Ces questions nécessitent une compréhension de l'ensemble des composants, pas seulement la connaissance de quelques commandes.

## 1.2. Objectifs pédagogiques

À la fin de ce cours, tu dois pouvoir :

1. Concevoir une architecture d'authentification centralisée adaptée à plusieurs serveurs.
2. Analyser les dépendances entre DNS, LDAP, Kerberos, SSSD, PAM et NSS.
3. Comprendre le fonctionnement des domaines et des relations d'approbation Active Directory.
4. Choisir une méthode cohérente de correspondance des UID/GID.
5. Sécuriser la communication avec les annuaires.
6. Concevoir une politique d'accès basée sur les groupes.
7. Comprendre les limites du cache et du fonctionnement hors ligne.
8. Construire une délégation administrative avec des privilèges minimaux.
9. Sécuriser les accès SSH des comptes centralisés.
10. Gérer les identités techniques et les keytabs.
11. Concevoir une procédure complète de révocation.
12. Mettre en place une collecte de journaux pertinente.
13. Diagnostiquer les incidents en isolant la couche défaillante.
14. Automatiser les contrôles sans exposer de secrets.
15. Documenter une architecture dont un autre administrateur peut reprendre l'exploitation.

## 1.3. Environnement recommandé

Pour les manipulations avancées, privilégie un laboratoire comprenant :

```text
                  ENVIRONNEMENT DE TEST
                           |
              +------------+------------+
              |                         |
              v                         v
       Infrastructure AD           Infrastructure LDAP
       -----------------           ---------------------
       DC01                          LDAP01
       DC02                          LDAP02
              |                         |
              +------------+------------+
                           |
                           v
                    Réseau de test
                           |
              +------------+------------+
              |                         |
              v                         v
          Linux01                   Linux02
          SSSD/AD                   SSSD/LDAP
              |                         |
              +------------+------------+
                           |
                           v
                 Tests et supervision
```

Tous les noms sont fictifs.

Les exercices d'intégration ne doivent pas être réalisés sur un serveur de production sans autorisation, sauvegarde de configuration et moyen de récupération.

Avant de toucher à PAM, SSH, SSSD ou aux paramètres du domaine, assure-toi de disposer d'un accès de secours indépendant de la nouvelle configuration.

## 1.4. Convention utilisée dans le cours

Les exemples emploient :

```text
Domaine AD       : ad.example.test
Royaume Kerberos : AD.EXAMPLE.TEST
Contrôleur AD    : dc01.ad.example.test
Serveur Linux    : linux01.ad.example.test
Utilisateur      : alice
Groupe admin     : Linux-Admins
Groupe métier    : Developpeurs
```

Pour l'exemple LDAP :

```text
Serveur LDAP     : ldap01.example.test
Base DN          : dc=example,dc=test
OU utilisateurs  : ou=People,dc=example,dc=test
OU groupes       : ou=Groups,dc=example,dc=test
```

Ces valeurs sont des paramètres de démonstration. Remplace-les par les valeurs autorisées de ton laboratoire.


# 2. Architecture experte de la gestion des identités

## 2.1. Les quatre dimensions fondamentales

Toute architecture d'identité doit distinguer :

- L'identité.
- L'authentification.
- L'autorisation.
- L'audit.

### Identité

L'identité détermine la manière dont un utilisateur, un groupe ou un système est représenté.

Exemples :

```text
alice@ad.example.test
UID Linux : 20001
Groupe principal : 20010
```

L'identité fournit les informations nécessaires à la représentation du compte, mais ne garantit pas son accès.

### Authentification

L'authentification vérifie que l'entité peut démontrer son identité selon la méthode attendue.

Exemples :

- Mot de passe.
- Kerberos.
- Clé SSH.
- Certificat.
- Authentification multifacteur.
- Autre mécanisme pris en charge par le service.

### Autorisation

L'autorisation décide si une action est permise.

Elle peut intervenir à plusieurs niveaux :

```text
Accès au réseau
      |
      v
Accès au serveur
      |
      v
Ouverture de session
      |
      v
Exécution d'une commande
      |
      v
Accès à un fichier
      |
      v
Accès à une fonction applicative
```

Chaque niveau peut appliquer des politiques distinctes.

### Audit

L'audit permet de reconstruire ce qui s'est produit, dans la mesure où les événements nécessaires sont enregistrés et protégés.

Il sert à répondre à des questions telles que :

- Qui a ouvert une session ?
- Quel compte a exécuté une commande privilégiée ?
- Quel changement de groupe a été effectué ?
- Pourquoi un accès a-t-il été refusé ?
- Quel administrateur a modifié la politique ?

## 2.2. Architecture complète d'une connexion

Lorsqu'Alice ouvre une session SSH sur Linux01, le flux peut ressembler à ceci :

```text
                  Alice
                    |
                    v
               Client SSH
                    |
                    v
              Serveur SSH
                    |
                    v
            Chaîne d'authentification
                    |
                    v
               PAM, si activé
                    |
                    v
                  SSSD
                    |
          +---------+---------+
          |                   |
          v                   v
    Identités/groupes     Authentification
          |                   |
          v                   v
       NSS/SSSD         LDAP/Kerberos/AD
          |                   |
          +---------+---------+
                    |
                    v
            Contrôle d'accès
                    |
                    v
             Session autorisée
                    |
                    v
            UID et groupes effectifs
                    |
                    v
          Permissions et ACL locales
```

Cette représentation est simplifiée. Le flux réel dépend du serveur SSH, de la configuration PAM, du fournisseur SSSD et du mécanisme d'authentification utilisé.

L'idée fondamentale reste la même : la résolution du compte, l'authentification et l'autorisation sont des opérations distinctes.

## 2.3. Pourquoi un compte existant peut-il être refusé ?

Supposons que :

```bash
getent passwd 'alice@ad.example.test'
```

renvoie une entrée correcte.

Cela démontre que l'identité est résolue dans ce contexte.

Cela ne prouve pas :

- Que Kerberos fonctionne.
- Que le compte est autorisé par SSSD.
- Que PAM accepte la session.
- Que SSH autorise la méthode d'authentification.
- Que le répertoire personnel existe.
- Que les permissions des fichiers sont adaptées.

Le diagnostic doit donc examiner les différentes couches dans le bon ordre.

## 2.4. Les dépendances à surveiller

Une architecture centralisée peut dépendre de plusieurs services :

```text
                 CLIENT LINUX
                      |
                      v
                 Configuration
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
         DNS        Réseau       Heure
          |           |           |
          +-----------+-----------+
                      |
                      v
             Contrôleur de domaine
                      |
              +-------+-------+
              |               |
              v               v
           Annuaire         Kerberos
              |               |
              +-------+-------+
                      |
                      v
                    SSSD
                      |
                 +----+----+
                 |         |
                 v         v
                NSS       PAM
                 |         |
                 +----+----+
                      |
                      v
              Services Linux
```

Si le DNS est incorrect, le serveur peut ne pas découvrir le bon contrôleur.

Si l'heure est incorrecte, Kerberos peut refuser des tickets.

Si SSSD est arrêté, la résolution des identités distantes peut échouer.

Si PAM est mal configuré, le système peut connaître l'utilisateur tout en refusant sa connexion.

Si les permissions locales sont incorrectes, l'utilisateur peut se connecter sans pouvoir utiliser les fichiers attendus.

## 2.5. Définir les responsabilités des composants

| Composant | Responsabilité principale |
|---|---|
| LDAP | Protocole d'accès à un annuaire |
| Active Directory DS | Service d'annuaire de domaine |
| Kerberos | Authentification fondée sur des tickets |
| DNS | Résolution des noms et découverte de services |
| NSS | Résolution des utilisateurs, groupes et autres bases système |
| PAM | Chaînes modulaires d'authentification, de contrôle de compte et de session |
| SSSD | Intégration cliente aux sources d'identités et d'authentification |
| realmd | Découverte et configuration de l'intégration à certains domaines |
| adcli | Opérations d'adhésion et de gestion associées à Active Directory |
| winbind | Intégration de domaine, notamment pour les environnements Samba |
| sudo | Délégation de commandes privilégiées |
| OpenSSH | Accès distant et authentification SSH |

Ces outils peuvent coopérer, mais aucun ne remplace toutes les autres fonctions.


# 3. Révision approfondie de LDAP et Active Directory

## 3.1. LDAP : un protocole, pas un produit complet d'authentification

LDAP permet aux clients d'interagir avec un annuaire structuré.

Il permet notamment :

- De rechercher des entrées.
- De lire des attributs.
- D'accéder à certaines informations d'identité.
- D'effectuer des opérations autorisées sur l'annuaire.
- D'utiliser certaines méthodes d'authentification LDAP.

Un serveur LDAP peut être OpenLDAP ou un autre service compatible avec le protocole.

LDAP ne fournit pas automatiquement la configuration des sessions Linux, les permissions POSIX sur les fichiers ou la politique SSH.

## 3.2. Active Directory Domain Services

Active Directory Domain Services est un service d'annuaire qui gère les objets d'un domaine.

Il s'intègre notamment à :

- LDAP.
- Kerberos.
- DNS.
- Des mécanismes Windows d'identité et de sécurité.
- Des relations d'approbation entre domaines, selon la configuration.

LDAP permet d'accéder à des informations d'Active Directory, mais ne représente pas à lui seul l'intégralité de l'architecture AD.

## 3.3. La différence qui évite de nombreux malentendus

```text
LDAP
 |
 +-- Protocole d'accès à des informations d'annuaire

Active Directory DS
 |
 +-- Service d'annuaire
 +-- Domaines
 +-- Utilisateurs et groupes
 +-- Ordinateurs
 +-- Intégration Kerberos
 +-- Découverte de services via DNS
```

Un client Linux peut utiliser LDAP pour lire des informations d'un annuaire AD et Kerberos pour s'authentifier.

Il peut également utiliser SSSD avec son fournisseur AD, qui intègre les mécanismes spécifiques au domaine.

Le choix du fournisseur SSSD dépend de l'architecture.

## 3.4. LDAP et schéma POSIX

Dans certains annuaires LDAP, les identités Unix utilisent des attributs POSIX.

Exemple illustratif :

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

Les attributs `uidNumber` et `gidNumber` fournissent des identifiants numériques Unix.

Les attributs `homeDirectory` et `loginShell` peuvent fournir le chemin du répertoire personnel et le shell de connexion.

Les entrées et attributs exacts dépendent du schéma utilisé.

## 3.5. Les DN, OU et DC

Exemple :

```text
uid=alice,ou=People,dc=example,dc=test
```

Le DN identifie l'entrée dans son contexte d'annuaire.

Les composants les plus courants de cet exemple sont :

- `uid=alice` : identifiant relatif de l'entrée.
- `ou=People` : unité d'organisation.
- `dc=example,dc=test` : composants du domaine dans le DN.

Dans Active Directory, l'abréviation DC peut aussi signifier *Domain Controller*. Il faut distinguer cet usage du composant `dc` dans un nom LDAP.

## 3.6. Vérifier les données avant de configurer un client

Pour rechercher un utilisateur :

```bash
ldapsearch -x \
  -H ldaps://ldap01.example.test \
  -b 'dc=example,dc=test' \
  '(uid=alice)' \
  uid uidNumber gidNumber homeDirectory loginShell
```

Cette commande est un exemple de recherche sécurisée. Elle suppose que la recherche anonyme soit autorisée ou que les paramètres d'authentification nécessaires soient fournis par une méthode adaptée.

Avant de configurer SSSD, vérifie :

- La base DN.
- L'attribut contenant le nom du compte.
- Les attributs POSIX.
- Le schéma des groupes.
- La manière de représenter les membres des groupes.
- La méthode de chiffrement du transport.
- Les droits de lecture disponibles pour le client.

Un client mal configuré ne peut pas compenser un schéma d'annuaire incomplet.


# 4. Kerberos avancé : tickets, keytabs et délégation

## 4.1. Rôle de Kerberos

Kerberos est un protocole d'authentification par tickets.

Il permet à un utilisateur ou à un système de présenter une preuve d'identité aux services qui prennent en charge ce mécanisme.

Un mot de passe n'est donc pas transmis à chaque service comme méthode universelle d'authentification.

Dans Active Directory, Kerberos constitue l'un des mécanismes principaux d'authentification du domaine.

## 4.2. Les acteurs

Kerberos implique notamment :

- Le client.
- Le KDC, ou *Key Distribution Center*.
- Le service auquel le client souhaite accéder.

Le KDC comporte les fonctions d'authentification et de délivrance des tickets nécessaires au protocole.

```text
              Client
                |
                v
                KDC
                |
          +-----+-----+
          |           |
          v           v
       Ticket       Ticket
       initial      de service
          |           |
          |           v
          |         Service
          |
          v
     Autres demandes
```

Ce schéma illustre le principe général, pas tous les échanges du protocole.

## 4.3. Le TGT

Le *Ticket-Granting Ticket* (TGT) permet au client de demander d'autres tickets auprès du service prévu par Kerberos.

Le TGT n'est pas le mot de passe utilisateur.

Il est utilisé dans le cadre du protocole pour obtenir des tickets de service selon les règles applicables.

## 4.4. Le ticket de service

Un ticket de service correspond à une cible particulière.

Exemple conceptuel :

```text
Alice s'authentifie
        |
        v
Obtient un TGT
        |
        v
Demande un ticket pour un service
        |
        v
Présente le ticket au service
        |
        v
Le service vérifie le ticket
        |
        v
L'autorisation est évaluée
```

Un ticket valide ne signifie pas que l'utilisateur peut lire tous les fichiers du serveur ou exécuter n'importe quelle commande.

L'autorisation reste une étape distincte.

## 4.5. Pourquoi l'heure est-elle critique ?

Les tickets Kerberos possèdent des périodes de validité.

Un écart d'heure excessif peut provoquer le refus d'une authentification.

Contrôler l'heure :

```bash
timedatectl
```

Si le système utilise chrony :

```bash
chronyc tracking
chronyc sources -v
```

La synchronisation doit être configurée selon la politique de l'infrastructure.

Ne modifie pas arbitrairement l'heure manuellement pour masquer une erreur Kerberos : identifie le service de synchronisation utilisé.

## 4.6. Examiner les tickets

```bash
klist
```

La commande montre les tickets du cache utilisé par la session.

Pour demander un ticket dans un domaine de laboratoire :

```bash
kinit alice@AD.EXAMPLE.TEST
```

Puis :

```bash
klist
```

Pour demander explicitement un ticket de service lorsqu'un principal adapté est disponible :

```bash
kvno host/linux01.ad.example.test
```

Le principal `host/linux01.ad.example.test` est un exemple. Le service doit réellement posséder le principal approprié et les droits nécessaires.

## 4.7. Keytab : définition

Un keytab est un fichier ou une ressource contenant des clés Kerberos associées à des principaux.

Il est souvent utilisé par les services et les machines pour s'authentifier sans demander interactivement le mot de passe d'un utilisateur humain.

Exemples d'usages :

- Authentification de la machine membre du domaine.
- Exécution de tâches automatisées.
- Authentification d'un service compatible avec Kerberos.

Le keytab n'est pas un fichier de mot de passe à partager entre administrateurs.

Il doit être protégé comme un secret.

## 4.8. Examiner le keytab

Commande courante :

```bash
sudo klist -kte /etc/krb5.keytab
```

Cette commande affiche les principaux et les informations de clés visibles dans le keytab, selon les capacités des outils installés.

Elle n'affiche pas les clés secrètes en clair.

N'envoie pas le fichier keytab à un tiers ou dans un dépôt de code.

## 4.9. Authentification d'un service avec un keytab

Dans un environnement de laboratoire, un test avec un keytab approprié peut utiliser :

```bash
sudo kinit -k -t /etc/krb5.keytab 'host/linux01.ad.example.test@AD.EXAMPLE.TEST'
```

Le principal doit réellement exister dans le keytab et être autorisé par l'infrastructure.

Après le test :

```bash
klist
```

Selon la méthode employée, il peut être nécessaire de contrôler le cache Kerberos utilisé par la session ou par le compte de service.

## 4.10. Rotation du secret machine

Lorsqu'une machine est membre d'Active Directory, son compte ordinateur possède un secret utilisé dans le fonctionnement du domaine.

La rotation ou le renouvellement de ce secret doit suivre les mécanismes de l'intégration.

Ne remplace pas manuellement le contenu de `/etc/krb5.keytab` par un fichier non validé.

Une incohérence entre les secrets du contrôleur et ceux utilisés par le client peut empêcher les opérations Kerberos.

Pour vérifier l'état de l'adhésion, si `adcli` est disponible :

```bash
sudo adcli testjoin
```

Le résultat dépend du domaine, des droits locaux et de la configuration de la machine.

## 4.11. Délégation Kerberos

La délégation Kerberos permet, dans certains scénarios, à un service d'utiliser des informations d'authentification pour accéder à un autre service au nom d'un utilisateur.

Elle doit être configurée très soigneusement.

Une mauvaise configuration peut permettre à un service compromis d'abuser d'identités privilégiées.

Les possibilités dépendent notamment :

- Du type de délégation.
- Des principaux.
- Des politiques de domaine.
- Des services cibles.
- Des paramètres du fournisseur d'identité.

Ne configure pas une délégation Kerberos uniquement pour résoudre une erreur d'authentification sans comprendre les implications de sécurité.


# 5. SSSD expert : architecture, fournisseurs et contrôles

## 5.1. Rôle de SSSD

SSSD (*System Security Services Daemon*) assure l'intégration entre le système Linux et des sources d'identité ou d'authentification distantes.

Selon le fournisseur et la configuration, il peut gérer :

- La résolution des utilisateurs.
- La résolution des groupes.
- L'authentification.
- Des contrôles d'accès.
- Le cache des identités.
- Certains usages hors ligne.
- Des informations liées aux politiques de compte.

Documentation :

https://sssd.io/docs/introduction.html

## 5.2. Les fournisseurs SSSD

Le fournisseur doit correspondre à l'architecture réelle.

| Fournisseur | Usage typique |
|---|---|
| `ad` | Intégration directe à Active Directory |
| `ldap` | Annuaire LDAP générique |
| `ipa` | Red Hat Identity Management/FreeIPA, selon la configuration |
| `krb5` | Authentification Kerberos dans une architecture adaptée |
| `proxy` | Délégation de certaines opérations à un autre module ou service compatible |
| `files` | Certaines informations locales dans les configurations qui le prennent en charge |

La configuration d'un domaine SSSD est composée de paramètres qui doivent être cohérents entre eux.

Il ne faut pas simplement changer `id_provider` sans vérifier les autres fournisseurs et paramètres.

## 5.3. Architecture interne simplifiée

```text
Applications Linux
       |
       +--------------------+
       |                    |
       v                    v
      NSS                  PAM
       |                    |
       v                    v
   Répondeur NSS       Répondeur PAM
       |                    |
       +---------+----------+
                 |
                 v
             Fournisseur
                 |
          +------+------+ 
          |             |
          v             v
        Cache       Service distant
                         |
                +--------+--------+
                |                 |
                v                 v
              LDAP             Kerberos
```

Cette représentation est simplifiée. SSSD possède une architecture de processus et de fournisseurs dépendant de sa version et de ses paramètres.

## 5.4. Fichier de configuration

Le fichier principal se trouve souvent ici :

```text
/etc/sssd/sssd.conf
```

Vérifier son existence et ses permissions :

```bash
sudo ls -l /etc/sssd/sssd.conf
```

Sur de nombreuses installations, le fichier doit appartenir à root et avoir des permissions restrictives, par exemple :

```bash
sudo chown root:root /etc/sssd/sssd.conf
sudo chmod 600 /etc/sssd/sssd.conf
```

Vérifie les exigences de ta version avant d'appliquer une modification.

Une configuration incorrecte peut empêcher le service de démarrer.

## 5.5. Ne pas remplacer aveuglément la configuration générée

Après une adhésion effectuée avec `realm join`, examine la configuration existante :

```bash
realm list
sudo cat /etc/sssd/sssd.conf
```

Le fichier peut comporter des paramètres générés ou nécessaires à la distribution.

Avant de modifier un paramètre :

1. Sauvegarde le fichier.
2. Note la valeur initiale.
3. Consulte le manuel SSSD correspondant à la version installée.
4. Change un paramètre à la fois.
5. Vérifie la syntaxe et le démarrage.
6. Teste la résolution des identités.
7. Teste l'accès réel au service.

## 5.6. Résolution des utilisateurs

Pour vérifier une identité :

```bash
getent passwd 'alice@ad.example.test'
```

Puis :

```bash
id 'alice@ad.example.test'
```

Si aucune entrée n'apparaît, cela ne démontre pas automatiquement que l'utilisateur n'existe pas dans AD.

Il faut examiner :

- Le nom pleinement qualifié.
- Le domaine configuré.
- Le fournisseur SSSD.
- Le DNS.
- L'accès à l'annuaire.
- Le cache.
- Les règles de recherche et de correspondance.

## 5.7. Contrôle de l'état du domaine

Si l'outil est disponible :

```bash
sudo sssctl domain-status ad.example.test
```

Pour vérifier le compte :

```bash
sudo sssctl user-checks 'alice@ad.example.test' -s sshd
```

La disponibilité et la syntaxe de certaines options dépendent de la version de `sssctl`.

Ces commandes peuvent aider à distinguer la résolution d'identité du contrôle d'accès appliqué à un service.

## 5.8. Paramètres de nommage

Un paramètre important est :

```ini
use_fully_qualified_names = True
```

Ce réglage détermine si les identités sont utilisées avec le domaine complet dans certaines formes de résolution.

Exemple :

```text
alice@ad.example.test
```

ou, selon une autre configuration :

```text
alice
```

Le choix doit être cohérent dans toute l'infrastructure.

Des noms courts peuvent devenir ambigus lorsque plusieurs domaines possèdent un utilisateur du même nom.

Ne modifie pas le nommage en production sans tester les scripts, les permissions, les tâches planifiées et les politiques d'accès dépendant des noms.

## 5.9. Contrôle d'accès par SSSD

Les fournisseurs SSSD peuvent appliquer des règles d'accès différentes.

Dans une intégration AD, on peut rencontrer :

```ini
access_provider = ad
```

Le contrôle d'accès s'appuie alors sur le fournisseur AD et les règles compatibles avec ce mode.

Un autre modèle peut utiliser :

```ini
access_provider = simple
simple_allow_groups = Linux-Admins
```

Dans ce second exemple, seuls les groupes indiqués sont autorisés par la politique simple, sous réserve de la configuration réelle.

Ces modèles ne doivent pas être combinés sans comprendre leur interaction.

Une commande `realm permit` peut changer le mécanisme de contrôle d'accès configuré par realmd. Vérifie la configuration après son utilisation.

## 5.10. Les groupes imbriqués

Les groupes peuvent contenir d'autres groupes, selon les capacités de l'annuaire et les règles d'intégration.

Cela permet d'organiser une politique telle que :

```text
Linux-Admins
      |
      +-- Groupe Exploitation
      |       |
      |       +-- Groupe Administrateurs Linux
      |
      +-- Groupe Plateforme
```

La profondeur et les capacités de résolution des groupes dépendent du fournisseur et de la configuration.

Il faut vérifier le résultat réel avec :

```bash
id 'alice@ad.example.test'
```

Ne suppose pas que toutes les appartenances imbriquées sont visibles ou interprétées de la même manière par tous les clients.

## 5.11. Filtre d'accès AD

Le fournisseur AD de SSSD peut prendre en charge des filtres d'accès dans les versions compatibles.

Un filtre peut être configuré pour autoriser certaines identités selon les attributs de l'annuaire.

La construction du filtre dépend du schéma et des règles AD.

Un filtre trop large peut autoriser des comptes imprévus ; un filtre trop restrictif peut bloquer les administrateurs.

Avant de déployer une telle règle :

- Définis les comptes autorisés.
- Vérifie que le filtre correspond à ces comptes.
- Teste des identités autorisées et interdites.
- Préserve un accès de secours.
- Documente les conséquences d'un changement de groupe.

Ne copie pas un filtre AD d'un exemple sans vérifier les attributs et la structure des groupes utilisés dans ton domaine.

## 5.12. Journaux SSSD

Pour examiner les événements :

```bash
sudo journalctl -u sssd --since "30 minutes ago"
```

Selon la configuration, des fichiers détaillés peuvent se trouver sous :

```text
/var/log/sssd/
```

Vérifie le chemin réel de la distribution.

Le niveau de journalisation peut être augmenté temporairement avec les outils disponibles, par exemple :

```bash
sudo sssctl debug-level 6
```

Cette commande dépend de la version installée.

N'active pas inutilement un niveau très détaillé en permanence. Des journaux volumineux compliquent l'analyse et peuvent contenir des informations opérationnelles sensibles.


# 6. UID, GID, SID et stratégies de correspondance

## 6.1. Les identifiants des deux mondes

Linux utilise :

```text
UID : identifiant numérique d'utilisateur
GID : identifiant numérique de groupe
```

Active Directory utilise notamment :

```text
SID : identifiant de sécurité Windows
```

Exemple conceptuel :

```text
Utilisateur AD : alice
SID            : S-1-5-21-...-1105
UID Linux      : 20001
GID principal  : 20010
```

Ces valeurs n'ont pas la même fonction.

Une intégration Linux doit déterminer une correspondance cohérente pour que les permissions POSIX puissent être appliquées.

## 6.2. Méthode A : correspondance automatique des identifiants

Dans certains scénarios AD, SSSD peut produire des identifiants POSIX à partir des SID de manière déterministe.

Le paramètre courant est :

```ini
ldap_id_mapping = True
```

Avec cette approche, les UID/GID peuvent être calculés à partir des identifiants AD au lieu d'exiger des attributs Unix explicitement renseignés pour chaque compte.

Cette méthode simplifie certains déploiements, mais les résultats dépendent du mécanisme de correspondance et de sa configuration.

Les identifiants calculés doivent rester cohérents entre les serveurs qui utilisent la même politique.

## 6.3. Méthode B : attributs POSIX présents dans AD

Une organisation peut choisir d'utiliser des attributs POSIX explicites dans l'annuaire, par exemple :

```text
uidNumber
gidNumber
unixHomeDirectory
loginShell
```

Cette approche exige que les attributs soient présents, cohérents et maintenus selon une politique d'entreprise.

Le paramètre :

```ini
ldap_id_mapping = False
```

est associé au modèle où l'intégration AD utilise les attributs POSIX appropriés, lorsqu'il est pris en charge par la configuration retenue.

La signification exacte de ce paramètre doit être vérifiée avec la version de SSSD installée.

## 6.4. Comparaison des stratégies

| Critère | Correspondance automatique | Attributs POSIX explicites |
|---|---|---|
| Attribution des UID/GID | Calculés à partir des identifiants AD selon le mécanisme | Fournis dans l'annuaire |
| Préparation de l'annuaire | Peut réduire le besoin d'attributs POSIX | Nécessite des attributs bien gérés |
| Cohérence entre serveurs | Exige une configuration cohérente | Exige des données d'annuaire cohérentes |
| Exploitation | Moins de gestion manuelle des UID/GID, selon le scénario | Gestion explicite des numéros POSIX |
| Risque principal | Incohérence si la correspondance diffère | Doublons ou numéros mal gérés dans l'annuaire |

Aucune approche n'est universellement meilleure. Elle doit correspondre à l'architecture, aux systèmes de fichiers partagés et aux contraintes opérationnelles.

## 6.5. Pourquoi le choix doit être fait tôt

Supposons qu'Alice possède un UID calculé par SSSD sur plusieurs serveurs.

Si l'administrateur change la stratégie de correspondance, l'UID affiché peut changer.

Les fichiers existants conservent leurs propriétaires numériques.

```text
Avant
Alice -> UID 20001
Fichier -> propriétaire UID 20001

Après changement mal planifié
Alice -> UID 30001
Fichier -> propriétaire UID 20001
```

Les droits peuvent alors devenir différents de ceux attendus.

Ce problème est critique dans les architectures NFS ou de stockage partagé.

Il faut donc :

1. Définir la stratégie.
2. Vérifier la cohérence des identifiants.
3. Tester sur les serveurs concernés.
4. Préparer une migration si nécessaire.
5. Contrôler les fichiers existants.
6. Vérifier les permissions après le changement.

## 6.6. Rechercher les fichiers d'un UID

Commande :

```bash
sudo find /srv/projets -xdev -uid 20001 -print
```

Remplace `20001` par l'UID réellement concerné.

Pour rechercher les fichiers d'un groupe :

```bash
sudo find /srv/projets -xdev -gid 20010 -print
```

Ne réattribue pas automatiquement tous les fichiers trouvés.

Certaines données peuvent appartenir volontairement à un ancien compte de service ou à une autre identité.

## 6.7. Le nom du compte n'est pas suffisant

Deux domaines peuvent contenir des utilisateurs portant le même nom.

Exemple :

```text
DOMAINE A : alice
DOMAINE B : alice
```

Un identifiant pleinement qualifié permet de différencier les comptes, selon les règles de nommage configurées.

C'est l'une des raisons pour lesquelles le format `utilisateur@domaine` est utile dans certaines architectures.


# 7. Active Directory multi-domaines et relations d'approbation

## 7.1. Domaine, forêt et relation d'approbation

Une architecture Active Directory peut comporter plusieurs domaines.

Ces domaines peuvent faire partie d'une même forêt ou appartenir à des forêts distinctes.

Les relations d'approbation déterminent comment les identités d'un domaine peuvent être reconnues ou utilisées dans un autre environnement.

L'existence d'une relation d'approbation ne signifie pas que tous les utilisateurs d'un domaine obtiennent les mêmes droits sur tous les serveurs.

## 7.2. Architecture multi-domaines

Exemple :

```text
                     Forêt AD
                         |
             +-----------+-----------+
             |                       |
             v                       v
       ad.example.test        eu.example.test
             |                       |
             v                       v
          Utilisateurs            Utilisateurs
          du domaine A             du domaine B
             |                       |
             +-----------+-----------+
                         |
                         v
                    Serveur Linux
```

L'architecture de résolution des identités doit savoir quel domaine fournit les informations d'un utilisateur donné.

## 7.3. Groupes provenant d'un domaine approuvé

Un groupe peut contenir des utilisateurs issus d'un autre domaine, selon la structure et les relations d'approbation.

Le client Linux doit être configuré pour résoudre correctement ces identités.

Il faut vérifier :

```bash
id 'alice@ad.example.test'
id 'bob@eu.example.test'
```

Ces commandes utilisent des noms d'exemple.

Si un utilisateur d'un domaine approuvé n'est pas résolu, il faut distinguer :

- Une relation d'approbation absente ou incorrecte.
- Une résolution DNS défaillante.
- Un domaine non pris en charge par le modèle d'intégration.
- Un problème d'autorisation.
- Un problème de correspondance des identifiants.
- Une restriction de recherche ou de cache.

## 7.4. Limites de l'intégration directe SSSD/AD

Les capacités de SSSD envers les domaines approuvés dépendent de la version et de l'architecture.

Le fournisseur AD de SSSD prend notamment en charge la découverte de domaines au sein d'une même forêt selon les règles du produit. Les environnements qui nécessitent des identités provenant de plusieurs forêts ou une architecture de confiance complexe doivent être évalués soigneusement.

Selon le scénario, une architecture basée sur FreeIPA/IdM avec des relations d'approbation ou une intégration utilisant winbind peut être plus appropriée.

Ne présume pas que l'ajout de plusieurs domaines dans un fichier SSSD suffira à supporter toutes les topologies AD.

La documentation de la version déployée doit être consultée avant de choisir une architecture.

## 7.5. Les noms courts dans un environnement multi-domaines

Lorsque plusieurs domaines contiennent des comptes de même nom, le nom court peut devenir ambigu.

Exemple :

```text
alice@ad.example.test
alice@eu.example.test
```

Il est généralement plus sûr d'utiliser un format pleinement qualifié lorsqu'il est nécessaire de distinguer les domaines.

Avant de modifier `use_fully_qualified_names`, vérifie les scripts, les tâches planifiées, les noms de groupe, les ACL et les règles `sudo`.

Une modification du format de nommage peut affecter les outils existants.

## 7.6. Contrôler les domaines activés

Selon la version de SSSD, des paramètres peuvent permettre de limiter les domaines approuvés qui sont interrogés.

Le but est notamment de réduire les recherches inutiles vers des domaines inaccessibles ou non nécessaires.

Cette optimisation doit être fondée sur la topologie réellement utilisée.

Avant de désactiver la résolution d'un domaine, vérifie si des utilisateurs, groupes ou ressources en dépendent.


# 8. LDAP avancé : sécurité, recherche, réplication et disponibilité

## 8.1. LDAP et la sécurité du transport

Les communications avec un annuaire peuvent exposer des données sensibles si elles ne sont pas protégées.

Une configuration de production doit tenir compte :

- Du chiffrement du transport.
- De l'intégrité des échanges.
- De l'authentification du serveur.
- De la chaîne de confiance du certificat.
- Des identifiants utilisés pour les recherches.
- Des droits accordés au compte technique.

Les modes courants comprennent LDAP avec StartTLS et LDAP directement sur TLS.

Le mode choisi doit être cohérent avec le serveur et la politique de sécurité.

## 8.2. Ne pas désactiver la validation du certificat

Une erreur de certificat doit être traitée comme un problème à diagnostiquer.

Vérifie :

- Le nom DNS utilisé.
- Le nom présent dans le certificat.
- La chaîne d'autorités de certification.
- La validité du certificat.
- L'heure du système.
- La configuration de confiance.

Ne désactive pas la vérification du certificat comme solution permanente.

Cela pourrait permettre à un serveur non approuvé d'intercepter ou d'usurper les communications d'annuaire.

## 8.3. Protéger les comptes techniques de lecture LDAP

Certains clients LDAP utilisent un compte technique pour lire les informations nécessaires à la résolution des identités.

Ce compte doit disposer uniquement des permissions nécessaires.

Il ne doit pas posséder de droits de modification de l'annuaire si le client n'a besoin que de lire les identités.

Une configuration qui conserve un secret de connexion doit protéger ce secret par des permissions de fichier strictes et une politique de rotation.

Ne stocke pas les identifiants de lecture dans un script public ou un dépôt de code.

## 8.4. Recherches LDAP et base de recherche

Une base DN trop large peut augmenter le volume de recherche et exposer des entrées non nécessaires.

Une base trop restrictive peut empêcher la résolution d'utilisateurs ou de groupes.

Exemple :

```text
dc=example,dc=test
        |
        +-- ou=People
        |
        +-- ou=Groups
        |
        +-- ou=Services
```

Si le client recherche uniquement dans `ou=People`, il ne trouvera pas directement des groupes situés dans `ou=Groups` à partir de cette base.

La configuration doit correspondre à l'organisation réelle de l'annuaire.

## 8.5. Filtres d'utilisateurs et de groupes

Les filtres LDAP définissent les entrées qui correspondent à une recherche.

Un filtre mal conçu peut produire :

- Trop peu de résultats.
- Trop de résultats.
- Des groupes partiellement résolus.
- Des échecs d'accès difficiles à comprendre.

Avant de déployer un filtre :

1. Teste-le directement avec l'outil de recherche.
2. Vérifie les entrées attendues.
3. Vérifie les cas limites.
4. Contrôle les autorisations du compte de recherche.
5. Vérifie le comportement SSSD.
6. Teste les résultats dans Linux.

Ne construis pas un filtre d'accès à partir d'un attribut dont la sémantique n'est pas confirmée.

## 8.6. Réplication d'annuaire

La réplication permet à plusieurs serveurs d'annuaire de conserver des données synchronisées selon les mécanismes du produit.

```text
                 Annuaire
                     |
          +----------+----------+
          |                     |
          v                     v
       LDAP01                 LDAP02
          |                     |
          +----------+----------+
                     |
                     v
                Clients Linux
```

Ce schéma représente une architecture possible. Le mode de réplication, le sens des flux et les responsabilités dépendent du produit.

La réplication ne garantit pas que toutes les modifications soient visibles instantanément sur tous les serveurs.

Il peut exister un délai de propagation ou une situation de réplication défaillante.

Il faut donc distinguer :

- La disponibilité d'un serveur LDAP.
- La cohérence de ses données.
- L'état de réplication.
- La disponibilité du mécanisme d'authentification.

## 8.7. Haute disponibilité côté client

Certains clients SSSD peuvent être configurés avec plusieurs serveurs LDAP de secours.

Exemple conceptuel :

```ini
ldap_uri = ldap://ldap01.example.test, ldap://ldap02.example.test
```

Cette ligne est illustrative. La syntaxe exacte des listes d'URI doit être vérifiée dans le manuel SSSD de la version installée.

Pour une utilisation en production, chaque serveur et certificat doit respecter la politique de sécurité.

Le client doit pouvoir atteindre les serveurs prévus, et ces derniers doivent posséder des données cohérentes.

**La disponibilité de plusieurs endpoints ne garantit pas à elle seule la cohérence des données répliquées.**

## 8.8. Vérifier l'état d'un fournisseur LDAP

Si l'outil est disponible :

```bash
sudo ldapsearch -x \
  -H ldaps://ldap01.example.test \
  -b 'dc=example,dc=test' \
  '(uid=alice)' uid
```

Teste également le serveur de secours.

Les erreurs peuvent venir d'une autorisation insuffisante, d'un certificat, d'un problème réseau ou d'une incohérence de réplication.

## 8.9. LDAP et Kerberos ensemble

Dans certaines architectures, LDAP fournit les identités, tandis que Kerberos fournit l'authentification.

```text
Client Linux
     |
     v
SSSD
     |
     +----------------------+
     |                      |
     v                      v
LDAP                   Kerberos
     |                      |
     v                      v
Identités              Tickets
et groupes             d'authentification
     |                      |
     +----------+-----------+
                |
                v
              Linux
```

Cette architecture exige de définir clairement les rôles et les paramètres de chaque fournisseur.

Ne suppose pas qu'une configuration LDAP avec `auth_provider = ldap` et une configuration LDAP/Kerberos sont interchangeables sans autres modifications.


# 9. Politiques d'accès et autorisation centralisée

## 9.1. Pourquoi séparer identification et accès au serveur ?

Une entreprise peut posséder des milliers d'identités, alors qu'un serveur donné ne doit accueillir qu'un petit sous-ensemble d'utilisateurs.

L'autorisation d'accès doit donc être explicitement définie.

```text
Annuaire
  |
  +-- Tous les utilisateurs
  |
  +-- Groupe Développement
  |
  +-- Groupe Exploitation
  |
  +-- Groupe Audit
          |
          v
      Serveur Linux
          |
          +-- Groupes autorisés
          |
          +-- Groupes refusés
```

Le fait qu'un utilisateur existe dans l'annuaire ne signifie pas qu'il doit pouvoir ouvrir une session sur tous les serveurs.

## 9.2. Politique d'accès SSSD

Dans une architecture AD, le fournisseur d'accès peut utiliser les fonctions compatibles du fournisseur AD.

Dans d'autres architectures, le fournisseur simple peut autoriser une liste de groupes précise.

Exemple conceptuel :

```ini
access_provider = simple
simple_allow_groups = Linux-Admins, Linux-Operators
```

Ce modèle doit être adapté aux noms de groupes effectivement résolus.

Une configuration réelle peut nécessiter les noms pleinement qualifiés ou d'autres réglages.

Le modèle `simple` n'est pas équivalent à une politique d'accès fondée sur tous les mécanismes AD.

## 9.3. Commandes realmd de gestion d'accès

Les commandes `realm permit` et `realm deny` peuvent aider à appliquer certaines politiques d'accès au domaine.

Exemple :

```bash
sudo realm permit --groups 'Linux-Admins@ad.example.test'
```

Le comportement exact dépend de la version et de la configuration realmd.

Vérifie ensuite :

```bash
realm list
```

et examine la configuration SSSD.

Ne lance pas aveuglément une commande de restriction globale sur un serveur de production : tu pourrais exclure les comptes administratifs attendus.

## 9.4. Test positif et test négatif

Une politique correcte doit être validée dans les deux sens.

### Test positif

Un utilisateur autorisé doit pouvoir s'authentifier et ouvrir une session selon la méthode prévue.

### Test négatif

Un utilisateur qui n'est pas autorisé doit être refusé par la politique attendue.

Un seul test positif ne prouve pas que la restriction fonctionne.

Un seul test négatif ne prouve pas que les utilisateurs légitimes sont correctement configurés.

Il faut tester plusieurs catégories de comptes, notamment les administrateurs, les utilisateurs ordinaires et les comptes de service.

## 9.5. Distinguer l'accès SSH des permissions de fichiers

Une politique d'accès peut autoriser Alice à ouvrir une session sans lui donner le droit de modifier `/srv/projets`.

```text
Accès à la session
        |
        v
UID et groupes du processus
        |
        v
Permissions locales et ACL
        |
        v
Accès au fichier
```

L'autorisation d'ouvrir une session ne remplace pas la gestion des fichiers.

Les administrateurs doivent contrôler les deux.


# 10. PAM avancé et authentification multifacteur

## 10.1. Rôle de PAM dans l'architecture experte

PAM est utilisé par les services compatibles pour mettre en œuvre certaines chaînes d'authentification, de contrôle de compte, de changement de mot de passe et de session.

Les fichiers se trouvent souvent sous :

```text
/etc/pam.d/
```

Afficher les fichiers :

```bash
ls /etc/pam.d/
```

Une configuration PAM est une chaîne ordonnée de modules et d'indicateurs de contrôle.

Une erreur de configuration peut bloquer des services, y compris la connexion administrateur.

## 10.2. Contrôler la chaîne d'authentification

Dans un environnement utilisant SSSD, les fichiers PAM peuvent appeler des modules associés à SSSD.

Il faut vérifier si le service concerné utilise effectivement PAM.

Si les journaux ne montrent pas l'appel attendu à `pam_sss`, le problème peut se situer dans la configuration PAM plutôt que dans le fournisseur d'identités.

Ne modifie pas des fichiers PAM au hasard pour résoudre un échec de connexion.

## 10.3. Politique de compte et authentification

Une authentification réussie ne signifie pas nécessairement que le compte peut ouvrir une nouvelle session.

Des vérifications complémentaires peuvent concerner :

- L'expiration du compte.
- La politique d'accès du service.
- L'appartenance aux groupes autorisés.
- Les restrictions de connexion.
- Les contrôles PAM.
- La disponibilité du fournisseur d'identité.

Il faut distinguer ces refus d'un simple mot de passe incorrect.

## 10.4. Authentification multifacteur

L'authentification multifacteur combine plusieurs facteurs d'une nature différente.

Exemples :

- Un secret connu par l'utilisateur.
- Un dispositif ou une clé possédée.
- Une propriété ou un mécanisme d'authentification pris en charge par l'environnement.

Le choix du mécanisme doit correspondre au service et à la politique de sécurité.

Une authentification à plusieurs facteurs peut être mise en œuvre par un fournisseur d'identité, par une chaîne PAM ou par une autre architecture compatible.

Il faut vérifier où le second facteur est réellement appliqué et si certains chemins de connexion le contournent.

## 10.5. Pourquoi MFA doit-il être testé avec soin ?

Un serveur peut proposer plusieurs méthodes de connexion :

- Console.
- SSH.
- Authentification par mot de passe.
- Clé publique.
- Connexion d'un compte de service.
- Session déjà ouverte.

L'activation d'un facteur supplémentaire sur une seule méthode ne signifie pas nécessairement que toutes les autres sont couvertes.

Le plan de test doit couvrir les services pertinents.

## 10.6. PAM et récupération

Avant de modifier PAM :

1. Conserve une copie de la configuration.
2. Note les valeurs initiales.
3. Garde un accès de secours.
4. Teste sur une machine de laboratoire.
5. Valide la syntaxe selon l'outil disponible.
6. Ouvre une nouvelle session de test.
7. Vérifie le refus et l'autorisation attendus.
8. Conserve une méthode de retour arrière.

Ne ferme pas la seule session administrative disponible avant d'avoir validé une nouvelle connexion.


# 11. sudo expert et délégation administrative

## 11.1. Déléguer une tâche plutôt que donner root

Une équipe d'exploitation peut avoir besoin de consulter l'état d'un service, de le redémarrer ou de lancer une commande de maintenance spécifique.

Cela ne justifie pas automatiquement un accès root complet.

Le modèle souhaité peut être :

```text
Groupe Linux-Operators
          |
          v
Commandes autorisées
          |
          +-- Statut d'un service
          +-- Redémarrage d'un service précis
          +-- Consultation de journaux définis
```

La délégation doit reposer sur une analyse des possibilités de la commande, de ses arguments et des fichiers qu'elle peut modifier.

## 11.2. Examiner les droits actuels

```bash
sudo -l
```

Pour un autre compte, selon la version de sudo :

```bash
sudo -l -U alice
```

Examine également les groupes du compte :

```bash
id alice
```

Dans une architecture centralisée, il faut vérifier que les groupes attendus sont correctement résolus.

## 11.3. Fichiers sudoers dédiés

Les règles peuvent être réparties dans des fichiers sous :

```text
/etc/sudoers.d/
```

Pour éditer un fichier précis :

```bash
sudo visudo -f /etc/sudoers.d/linux-operators
```

Cette opération doit être faite avec les droits appropriés et selon la politique locale.

La validation de syntaxe peut être réalisée avec :

```bash
sudo visudo -c
```

Le fichier doit également avoir un nom et des permissions compatibles avec les règles de la distribution et de sudo.

## 11.4. Exemple de délégation limitée

Supposons que l'équipe puisse consulter l'état d'un service précis.

Une règle conceptuelle pourrait être :

```sudoers
%Linux-Operators ALL=(root) /usr/bin/systemctl status application.service
```

Cet exemple doit être adapté :

- Au nom de groupe réellement résolu.
- Au chemin exact du programme.
- À la syntaxe prise en charge.
- Aux règles de l'organisation.
- Aux options et arguments qui seront acceptés.

Ne considère pas cette ligne comme une politique complète prête pour la production.

## 11.5. Le danger des commandes à possibilités étendues

Une commande autorisée peut permettre de :

- Lancer un shell.
- Modifier des fichiers arbitraires.
- Exécuter d'autres programmes.
- Charger des extensions.
- Modifier la configuration du système.

Limiter sudo à un binaire ne suffit donc pas à garantir le moindre privilège.

Il faut analyser les possibilités d'évasion et, si nécessaire, utiliser un outil spécialisé qui réalise une seule opération contrôlée.

## 11.6. sudo et groupes AD

Un groupe AD peut être utilisé comme base d'une politique sudo si son nom et son identité sont résolus par le client Linux et si la règle correspondante est correctement configurée.

Mais l'appartenance à un groupe AD ne donne pas automatiquement de privilèges.

Le système doit disposer d'une règle sudo ou d'un mécanisme de délégation approprié.

Vérifie le résultat avec :

```bash
id 'alice@ad.example.test'
sudo -l -U 'alice@ad.example.test'
```

La syntaxe et les possibilités de la seconde commande dépendent de la configuration locale.

## 11.7. Gestion des exceptions

Chaque règle privilégiée devrait être documentée :

```text
Compte ou groupe :
Commande permise :
Identité d'exécution :
Justification :
Responsable :
Date d'attribution :
Date de réexamen :
Conditions de retrait :
Méthode de validation :
```

Les exceptions deviennent dangereuses lorsqu'elles sont oubliées.


# 12. SSH, identités centralisées et accès privilégiés

## 12.1. Accès SSH et identité du domaine

Le serveur SSH doit être configuré pour utiliser les méthodes d'authentification prévues.

Dans de nombreuses distributions, PAM est utilisé par OpenSSH pour certains contrôles de compte et de session, selon les options configurées.

La résolution d'un utilisateur par SSSD ne prouve pas que SSH soit autorisé à lui ouvrir une session.

## 12.2. Vérifier la configuration SSH

Le fichier principal se trouve souvent sous :

```text
/etc/ssh/sshd_config
```

La configuration peut aussi inclure des fichiers additionnels.

Pour vérifier la syntaxe sur une installation OpenSSH compatible :

```bash
sudo sshd -t
```

Pour examiner la configuration effective :

```bash
sudo sshd -T
```

Certaines règles peuvent dépendre du compte et des conditions de connexion. Les options disponibles varient selon la version.

## 12.3. Autoriser certains groupes avec SSH

OpenSSH dispose de mécanismes tels que `AllowUsers`, `AllowGroups`, `DenyUsers` et `DenyGroups`, selon la version et la configuration.

Mais les noms de groupes AD doivent être correctement résolus et formatés.

Avant de définir une politique :

```bash
id 'alice@ad.example.test'
getent group
```

Teste ensuite la politique avec plusieurs identités.

Ne copie pas une directive `AllowGroups` en supposant qu'elle utilisera automatiquement le format de groupe AD attendu par ton système.

## 12.4. Ne pas fermer le seul accès d'administration

Une modification SSH peut empêcher les nouvelles connexions.

Avant un changement important :

- Garde une session administrative de secours.
- Vérifie le fichier.
- Teste la configuration.
- Applique la modification de manière contrôlée.
- Ouvre une nouvelle session.
- Vérifie l'accès des comptes prévus.
- Vérifie les refus attendus.
- Ne ferme la session initiale qu'après validation.

## 12.5. Clés SSH et comptes centralisés

Les comptes centralisés peuvent aussi utiliser des clés SSH, selon la configuration du serveur.

Le fait qu'une identité provienne d'AD ne signifie pas que ses clés SSH sont automatiquement enregistrées ou révoquées dans AD.

Il faut savoir où les clés autorisées sont stockées :

```text
~/.ssh/authorized_keys
```

ou dans un autre mécanisme configuré.

L'architecture doit définir le processus de création, de rotation, d'audit et de révocation de ces clés.


# 13. Cycle de vie, révocation et gouvernance des identités

## 13.1. Le cycle de vie complet

Une identité d'entreprise traverse plusieurs phases :

```text
Demande
   |
   v
Validation
   |
   v
Création
   |
   v
Attribution des groupes
   |
   v
Attribution des accès
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
Archivage des données
   |
   v
Suppression contrôlée
```

Ce cycle doit être documenté et associé à des responsabilités.

## 13.2. Provisionnement et déprovisionnement

Le provisionnement est le processus qui donne à un utilisateur ses identités et ses autorisations.

Le déprovisionnement est le processus qui retire ou désactive ces accès.

Le retrait d'un compte centralisé ne garantit pas que toutes les données, sessions, clés et autorisations locales disparaissent immédiatement.

Il faut examiner chaque ressource importante.

## 13.3. Retrait d'un collaborateur

Une procédure complète peut contenir :

```text
Identité centrale
       |
       +-- Désactivation de l'authentification
       |
       +-- Retrait des groupes
       |
       +-- Retrait des privilèges
       |
       +-- Révocation des clés
       |
       +-- Contrôle des sessions
       |
       +-- Contrôle des comptes locaux
       |
       +-- Traitement des fichiers
       |
       +-- Révocation des accès externes
       |
       +-- Documentation
```

La désactivation d'un compte ne termine pas nécessairement les sessions déjà actives.

Il faut appliquer la politique de l'organisation pour les sessions et les jetons existants.

## 13.4. Comptes locaux de secours

Une architecture fortement centralisée peut dépendre du réseau et de l'annuaire.

Un compte local de secours peut être nécessaire pour récupérer un serveur lors d'une panne d'identité centrale.

Ce compte doit être protégé :

- Accès restreint.
- Secret géré de manière sûre.
- Utilisation tracée.
- Tests de récupération.
- Politique de rotation.
- Absence d'usage quotidien non justifié.

Le compte de secours ne doit pas devenir un compte partagé utilisé pour les opérations courantes.

## 13.5. Fichiers orphelins

Les fichiers peuvent conserver les UID/GID d'un utilisateur après son départ.

Exemple :

```bash
sudo find /srv/projets -xdev -uid 20001 -print
```

Remplace `20001` par l'UID observé.

L'administrateur doit déterminer si ces fichiers doivent être archivés, conservés, transférés ou supprimés.

Une modification récursive des propriétaires sans inventaire peut casser des applications ou altérer la traçabilité.

## 13.6. Révision périodique des droits

Une revue d'accès peut vérifier :

- Les groupes administratifs.
- Les groupes métiers.
- Les règles sudo.
- Les ACL.
- Les clés SSH.
- Les comptes de service.
- Les comptes inactifs.
- Les utilisateurs des domaines approuvés.
- Les exceptions individuelles.

Elle doit produire une liste d'actions et des preuves de validation, pas uniquement un inventaire brut.


# 14. Comptes de service, keytabs et secrets techniques

## 14.1. Compte humain et identité technique

Un compte humain représente une personne.

Un compte de service représente généralement un logiciel ou un processus.

```text
Personne
   |
   v
Compte humain
   |
   v
Sessions interactives et accès personnels


Application
   |
   v
Identité technique
   |
   v
Ressources de service autorisées
```

Les deux types d'identités n'ont pas les mêmes besoins.

## 14.2. Limiter les privilèges des services

Un service devrait disposer uniquement des permissions nécessaires à son fonctionnement.

Un compte de service peut être local ou géré par une infrastructure d'identité plus large, selon l'architecture.

Il faut contrôler :

- Les fichiers accessibles.
- Les répertoires où le service peut écrire.
- Les permissions des secrets.
- Les privilèges Linux.
- Les droits sur les ressources distantes.
- Les méthodes d'authentification utilisées.

## 14.3. Keytab et compte machine

Un keytab peut contenir les clés nécessaires à certains principaux Kerberos.

Dans une intégration AD, le keytab du serveur peut contenir des principaux associés à l'identité de la machine.

Consulter les principaux :

```bash
sudo klist -kte /etc/krb5.keytab
```

Cette commande ne doit pas être confondue avec une lecture du mot de passe du compte machine.

Le fichier doit rester protégé contre l'accès non autorisé.

## 14.4. Secret machine et continuité

L'adhésion au domaine peut dépendre de secrets utilisés par le compte ordinateur.

En cas de perte de synchronisation entre les secrets du client et ceux du contrôleur, certaines opérations peuvent échouer.

Pour vérifier l'adhésion, si `adcli` est disponible :

```bash
sudo adcli testjoin
```

La réparation doit suivre une procédure adaptée à la version et à l'architecture.

Ne supprime pas le compte ordinateur ou le keytab comme premier réflexe. Cela peut aggraver l'incident.

## 14.5. Rotation des secrets

Les secrets techniques doivent posséder :

- Un propriétaire fonctionnel.
- Une méthode de stockage sûre.
- Une politique de rotation appropriée.
- Une méthode de révocation.
- Une procédure de récupération.
- Un contrôle d'accès aux fichiers et outils concernés.

Le stockage d'un mot de passe dans un script partagé n'est pas une méthode correcte de gestion des secrets.

## 14.6. Séparer les comptes techniques des utilisateurs humains

Il est préférable de ne pas dépendre du compte personnel d'un administrateur pour un service d'entreprise.

Si le collaborateur part ou change de fonction, cela pourrait interrompre le fonctionnement de l'application.

Le compte technique doit avoir son propre cycle de vie, sa documentation et son responsable.


# 15. Cache SSSD, fonctionnement hors ligne et continuité de service

## 15.1. Pourquoi le cache existe-t-il ?

SSSD peut conserver localement certaines informations d'identité pour accélérer les recherches et permettre certains usages lors d'une indisponibilité temporaire du fournisseur distant.

Le cache peut contribuer à la disponibilité, mais il n'est pas une copie parfaite et instantanément synchronisée de l'annuaire.

## 15.2. Les différentes catégories d'information

Il faut distinguer :

- Informations d'identité.
- Appartenances aux groupes.
- Informations d'authentification.
- État d'accès.
- Tickets Kerberos.
- Sessions déjà ouvertes.

Ces éléments n'ont pas tous la même durée de validité ni le même mécanisme de cache.

Une information d'identité mise en cache ne signifie pas automatiquement qu'une nouvelle authentification pourra réussir hors ligne.

## 15.3. Architecture hors ligne

```text
                Serveur Linux
                      |
                      v
                     SSSD
                      |
             +--------+--------+
             |                 |
             v                 v
       Cache local       Annuaire distant
             |                 |
             +--------+--------+
                      |
                      v
              Résultat dépendant
              de la configuration
```

Lors d'une panne réseau, les identités connues peuvent rester consultables selon le cache et la configuration.

Certaines authentifications peuvent fonctionner hors ligne si la politique le permet et si les informations nécessaires sont disponibles.

D'autres opérations continueront d'échouer, notamment celles qui nécessitent un service distant.

## 15.4. Cache et retrait d'accès

Supposons qu'Alice soit retirée d'un groupe administratif dans l'annuaire.

Une machine isolée peut ne pas connaître immédiatement ce changement.

Les délais et comportements dépendent du cache, du fournisseur et de la nature du contrôle d'accès.

Il faut donc intégrer le retrait des privilèges dans la stratégie de sécurité, et non supposer que tous les serveurs reçoivent instantanément le nouvel état.

## 15.5. Vérifier l'état du domaine

```bash
sudo sssctl domain-status ad.example.test
```

La syntaxe dépend de la version.

Examiner le service :

```bash
systemctl status sssd
```

Consulter les journaux :

```bash
sudo journalctl -u sssd --since "30 minutes ago"
```

## 15.6. Vider ou invalider le cache

SSSD fournit des outils permettant de faire expirer certaines entrées ou de retirer des données en cache.

Par exemple, selon la version :

```bash
sudo sssctl cache-expire -u 'alice@ad.example.test'
```

Une expiration globale peut aussi être disponible.

Ne vide pas le cache comme une mesure de dépannage universelle.

Cela peut supprimer des informations utiles au fonctionnement hors ligne et ne résout pas nécessairement les causes de l'incident.

Avant d'agir :

1. Vérifie DNS.
2. Vérifie l'accès au fournisseur.
3. Vérifie les journaux.
4. Identifie si le problème vient réellement du cache.
5. Préserve un accès administratif de secours.
6. Effectue l'action ciblée.
7. Vérifie la résolution et l'authentification après l'opération.


# 16. Architecture de sécurité et durcissement

## 16.1. Défense en profondeur

Une architecture centralisée ne doit pas reposer sur un unique contrôle.

Elle combine plusieurs mécanismes :

```text
                 Sécurité globale
                        |
         +--------------+--------------+
         |              |              |
         v              v              v
     Identités      Authentification  Autorisation
         |              |              |
         v              v              v
       LDAP/AD        Kerberos/PAM   Groupes/ACL/sudo
         |              |              |
         +--------------+--------------+
                        |
                        v
                     Journalisation
                        |
                        v
                       Audit
```

La défaillance ou le contournement d'une couche ne doit pas automatiquement donner accès à toutes les ressources.

## 16.2. Réduire la surface d'accès

Il faut déterminer quels utilisateurs peuvent :

- Ouvrir une session sur le serveur.
- Utiliser SSH.
- Exécuter des commandes privilégiées.
- Lire des données sensibles.
- Modifier les fichiers applicatifs.
- Accéder aux secrets.
- Administrer l'annuaire.

Ces autorisations doivent être séparées.

## 16.3. Protection du transport LDAP

Pour les connexions LDAP, utilise une configuration de transport et de validation de certificat adaptée.

Une connexion TLS qui accepte un certificat non vérifié ne fournit pas la même garantie de confiance qu'une connexion dont le certificat est correctement validé.

La politique doit vérifier le nom du serveur, la chaîne de confiance et la validité du certificat.

## 16.4. Comptes privilégiés

Les comptes administratifs doivent être protégés contre :

- Les droits excessifs.
- Les comptes partagés non maîtrisés.
- Les mots de passe et clés compromis.
- Les sessions persistantes non contrôlées.
- Les erreurs de délégation `sudo`.
- Les autorisations obsolètes.
- Les accès inutiles aux annuaires.

La présence dans un groupe administratif doit être révisée régulièrement.

## 16.5. Protection des fichiers de configuration

Certains fichiers peuvent contenir des références à des serveurs, des DN, des paramètres de confiance ou des secrets techniques.

Exemples :

```text
/etc/sssd/sssd.conf
/etc/krb5.conf
/etc/ssh/sshd_config
/etc/sudoers
/etc/sudoers.d/
```

Le niveau de confidentialité varie selon le contenu. Les fichiers contenant des secrets doivent être accessibles uniquement aux comptes qui en ont besoin.

Utilise les outils appropriés pour modifier les fichiers sensibles et conserver une possibilité de retour arrière.

## 16.6. Éviter les comptes de secours non maîtrisés

Un compte local de secours peut être nécessaire, mais il doit avoir une gouvernance.

Il faut définir :

- Qui détient les moyens d'accès.
- Quand le compte peut être utilisé.
- Comment l'utilisation est enregistrée.
- Comment le secret est renouvelé.
- Comment l'accès est testé.
- Comment éviter sa transformation en compte partagé quotidien.

## 16.7. Sauvegarder les configurations

Avant une modification critique :

```bash
sudo cp -a /etc/sssd/sssd.conf \
  /root/sssd.conf.backup
```

Cette opération est illustrative. Vérifie que le fichier existe et que le chemin de destination convient.

La sauvegarde doit rester protégée, car elle peut contenir des informations sensibles.

Il faut également conserver l'information sur la version, le changement effectué et la méthode de retour arrière.


# 17. Audit, observabilité et conformité

## 17.1. Pourquoi un inventaire ne suffit-il pas ?

Un inventaire indique ce qui existe.

Un audit compare ce qui existe à ce qui devrait exister.

Exemple :

```text
État attendu
Groupe Linux-Admins
Membres : comptes approuvés


État observé
Groupe Linux-Admins
Membres : comptes actuellement résolus


                    |
                    v
                 Comparaison
                    |
          +---------+---------+
          |                   |
          v                   v
       Conforme          Écart détecté
```

Les écarts doivent être analysés puis traités selon une procédure validée.

## 17.2. Inventaire des identités

Pour le système :

```bash
getent passwd
getent group
```

Pour un utilisateur centralisé :

```bash
id 'alice@ad.example.test'
```

Pour le domaine :

```bash
realm list
```

Pour SSSD :

```bash
systemctl status sssd
```

La collecte doit préciser si elle porte sur les comptes locaux ou sur toutes les identités résolues.

## 17.3. Audit des privilèges administratifs

Les informations pertinentes comprennent :

- Les groupes administratifs.
- Les règles sudoers.
- Les comptes privilégiés locaux.
- Les exceptions individuelles.
- Les accès SSH.
- Les clés et comptes techniques.

Vérifie les fichiers sudoers avec :

```bash
sudo visudo -c
```

La validité syntaxique ne garantit pas que les droits soient appropriés : il faut examiner les règles et leur justification.

## 17.4. Journalisation SSSD

```bash
sudo journalctl -u sssd --since "1 hour ago"
```

Les journaux peuvent fournir des indications sur :

- Les fournisseurs inaccessibles.
- Les problèmes de résolution.
- Les erreurs d'authentification.
- Les refus d'accès.
- Les problèmes de configuration.

Les journaux doivent être conservés et protégés selon la politique de sécurité.

## 17.5. Corréler les événements

Un incident d'authentification peut toucher plusieurs composants.

Il faut rapprocher les événements :

```text
Journal SSH
     |
     v
Journal PAM
     |
     v
Journal SSSD
     |
     v
Journaux Kerberos
     |
     v
Événements AD/LDAP
```

Les horodatages doivent être cohérents.

Sans synchronisation de l'heure, il devient plus difficile de reconstruire la chronologie.

## 17.6. Mesures de supervision

Les indicateurs peuvent inclure :

- État de SSSD.
- Succès des recherches d'identité.
- Disponibilité des contrôleurs.
- Résolution DNS.
- Synchronisation de l'heure.
- État de l'adhésion au domaine.
- Échecs d'authentification.
- Refus d'accès.
- Erreurs de certificat.
- Disponibilité LDAP.
- Échecs de renouvellement de secrets techniques.

Les indicateurs doivent être associés à une procédure d'action.

Une alerte sans responsable ni méthode de résolution devient rapidement du bruit opérationnel.

## 17.7. Matrice d'audit

| Contrôle | Preuve | Action en cas d'écart |
|---|---|---|
| SSSD actif | État du service | Diagnostic du service |
| Domaine découvert | `realm list` | Vérifier DNS et configuration |
| Utilisateur résolu | `getent`, `id` | Examiner fournisseur et cache |
| Groupe admin correct | Inventaire des groupes | Réviser les appartenances |
| sudo syntaxiquement valide | `visudo -c` | Corriger la configuration |
| Accès SSH conforme | Tests positifs et négatifs | Corriger la politique |
| Certificats valides | Validation TLS | Corriger confiance ou certificat |
| Retrait des accès effectué | Vérifications après retrait | Traiter sessions et accès persistants |


# 18. Dépannage expert par couche

## 18.1. Méthode de diagnostic

Lorsqu'une connexion centralisée échoue, il faut éviter de modifier simultanément plusieurs composants.

La méthode recommandée est :

```text
Symptôme
   |
   v
Collecte des faits
   |
   v
Identification de la première couche en échec
   |
   v
Hypothèse testable
   |
   v
Test ciblé
   |
   v
Correction minimale
   |
   v
Test positif et négatif
   |
   v
Documentation
```

Une bonne démarche sépare les observations des hypothèses.

## 18.2. Cas A — Le compte n'est pas résolu

Commande :

```bash
getent passwd 'alice@ad.example.test'
```

Si aucune entrée n'est retournée :

```bash
realm list
systemctl status sssd
```

Puis :

```bash
sudo journalctl -u sssd --since "30 minutes ago"
```

Contrôle aussi DNS :

```bash
dig SRV _ldap._tcp.ad.example.test
dig SRV _kerberos._tcp.ad.example.test
```

Hypothèses possibles :

- Domaine mal configuré.
- DNS incorrect.
- Fournisseur SSSD indisponible.
- Mauvais format de nom.
- Cache incohérent.
- Erreur de correspondance d'identifiants.
- Compte absent ou non visible dans la source configurée.

Ne commence pas par supprimer le cache.

## 18.3. Cas B — Le compte est résolu mais ne peut pas ouvrir une session

Si `getent` et `id` fonctionnent, la résolution a réussi dans ce contexte.

Il faut alors examiner les couches d'authentification et d'autorisation.

```bash
realm list
systemctl status sssd
sudo journalctl -u sssd --since "30 minutes ago"
```

Pour SSH :

```bash
sudo journalctl -u ssh --since "30 minutes ago"
```

Le nom du service peut différer selon la distribution.

Vérifie :

- La politique d'accès du domaine.
- Les groupes autorisés.
- Les règles PAM.
- Les méthodes d'authentification SSH.
- L'état du compte dans l'annuaire.
- Les tickets Kerberos et la synchronisation de l'heure, si Kerberos est utilisé.

## 18.4. Cas C — Erreur Kerberos

Contrôle :

```bash
timedatectl
```

Puis :

```bash
dig SRV _kerberos._tcp.ad.example.test
klist
```

Pour un test d'obtention de ticket dans un environnement de laboratoire :

```bash
kinit alice@AD.EXAMPLE.TEST
```

Vérifie :

- Le royaume.
- Le nom du principal.
- Le DNS.
- Le contrôleur de domaine.
- L'heure.
- L'état de l'adhésion.
- Les secrets ou clés associés.

Ne présume pas qu'une erreur Kerberos signifie nécessairement que le mot de passe est faux.

## 18.5. Cas D — Le domaine AD n'est plus correctement joint

Vérifie :

```bash
realm list
```

Puis, si l'outil est disponible :

```bash
sudo adcli testjoin
```

Consulte aussi :

```bash
sudo journalctl -u sssd --since "30 minutes ago"
```

Les causes possibles comprennent les problèmes de compte ordinateur, les secrets, le réseau, DNS ou la configuration locale.

N'efface pas le keytab ni le compte ordinateur avant d'avoir identifié la cause.

## 18.6. Cas E — LDAP inaccessible

Effectue une recherche avec la configuration du laboratoire :

```bash
ldapsearch -x \
  -H ldaps://ldap01.example.test \
  -b 'dc=example,dc=test' \
  '(uid=alice)' uid
```

Examine :

- La résolution DNS.
- Le certificat TLS.
- Le serveur cible.
- La base DN.
- Les autorisations de recherche.
- Les informations d'authentification du client.
- Le schéma de l'annuaire.

Une erreur TLS et une erreur d'autorisation doivent être traitées différemment.

## 18.7. Cas F — Le service SSSD refuse de démarrer

```bash
systemctl status sssd
sudo journalctl -u sssd -b
```

Vérifie :

```bash
sudo ls -l /etc/sssd/sssd.conf
```

Causes possibles :

- Syntaxe incorrecte.
- Paramètre non pris en charge.
- Permissions inadaptées.
- Fournisseur mal défini.
- Dépendance absente.
- Problème de configuration réseau ou TLS.

Compare la configuration avec une sauvegarde connue comme fonctionnelle.

Ne remplace pas tout le fichier avant d'avoir conservé la configuration initiale.

## 18.8. Cas G — L'utilisateur a été retiré d'un groupe mais conserve un accès

Examine :

- Les groupes actuellement résolus.
- Les sessions actives.
- Les processus existants.
- Les règles sudoers.
- Les ACL locales.
- Les clés SSH.
- Les autorisations propres aux applications.
- Les caches et les délais de mise à jour.

Un retrait dans l'annuaire ne garantit pas que toutes les sessions actives soient immédiatement terminées.

Le comportement dépend du service et des politiques applicables.

## 18.9. Cas H — Authentification correcte mais permission refusée

Commande :

```bash
id 'alice@ad.example.test'
```

Puis :

```bash
namei -l /srv/projets/rapport.txt
getfacl /srv/projets
getfacl /srv/projets/rapport.txt
```

Il faut examiner :

- Le groupe effectif.
- Les droits de traversée.
- Les ACL.
- Les permissions du fichier.
- Le système de fichiers.
- Les options de montage.
- Le compte réel du processus.
- Les contrôles de sécurité supplémentaires, s'ils sont présents.

Une correction de mot de passe ne résoudra pas nécessairement un problème de permission.

## 18.10. Cas I — Cache potentiellement incohérent

Avant d'expirer des entrées :

1. Vérifie que le fournisseur est joignable.
2. Identifie le compte concerné.
3. Examine les journaux.
4. Vérifie l'état de l'annuaire.
5. Évalue le besoin de fonctionnement hors ligne.
6. Effectue une action ciblée.
7. Contrôle les résultats.

Une commande telle que :

```bash
sudo sssctl cache-expire -u 'alice@ad.example.test'
```

peut être utile dans un cas ciblé, si elle est prise en charge par la version installée.

Ne considère pas l'expiration du cache comme une correction universelle.


# 19. Automatisation et gestion de configuration

## 19.1. Pourquoi automatiser l'identité ?

L'automatisation peut faciliter :

- Les contrôles périodiques des comptes.
- La vérification des groupes autorisés.
- La détection de dérives.
- Le contrôle de la configuration SSSD.
- La vérification de l'état des services.
- La préparation des rapports d'audit.
- La standardisation des serveurs.

Elle doit être conçue pour éviter les actions destructrices déclenchées par un résultat incomplet.

## 19.2. Principe d'idempotence

Une opération idempotente peut être répétée sans provoquer des changements non désirés lorsque l'état attendu est déjà atteint.

Exemple :

```text
État attendu :
SSSD actif
Domaine configuré
Groupe d'accès présent
Fichier de configuration valide
```

Si le système correspond déjà à cet état, la nouvelle exécution ne doit pas retirer des groupes, réinitialiser des comptes ou réécrire inutilement les secrets.

Les scripts doivent vérifier l'état avant de modifier les ressources.

## 19.3. Rapport de contrôle AD/SSSD

Le script suivant effectue des contrôles en lecture seule.

```bash
#!/usr/bin/env bash

set -u

DOMAIN="ad.example.test"
USER_NAME="alice@ad.example.test"

echo "========================================"
echo "AUDIT D'IDENTITÉ"
echo "Date : $(date -Is)"
echo "Hôte : $(hostname)"
echo "Domaine : ${DOMAIN}"
echo "========================================"

echo
echo "=== Domaine configuré ==="
if command -v realm >/dev/null 2>&1; then
    realm list
else
    echo "realmd non disponible."
fi

echo
echo "=== Service SSSD ==="
if systemctl is-active --quiet sssd; then
    echo "SSSD actif."
else
    echo "SSSD non actif."
fi

echo
echo "=== Résolution d'identité ==="
if getent passwd "${USER_NAME}" >/dev/null; then
    getent passwd "${USER_NAME}"
    id "${USER_NAME}" || true
else
    echo "Identité non résolue : ${USER_NAME}"
fi

echo
echo "=== DNS LDAP ==="
if command -v dig >/dev/null 2>&1; then
    dig +short SRV "_ldap._tcp.${DOMAIN}"
else
    echo "dig non disponible."
fi

echo
echo "=== DNS Kerberos ==="
if command -v dig >/dev/null 2>&1; then
    dig +short SRV "_kerberos._tcp.${DOMAIN}"
else
    echo "dig non disponible."
fi

echo
echo "=== Heure ==="
if command -v timedatectl >/dev/null 2>&1; then
    timedatectl
fi

echo
echo "=== Fin du rapport ==="
```

Ce script ne réalise pas l'adhésion au domaine et ne modifie aucun compte.

Il doit être adapté au domaine réel et testé sur la distribution cible.

## 19.4. Détecter les écarts sans supprimer automatiquement les accès

Un contrôle périodique peut comparer :

```text
Groupes autorisés attendus
          |
          v
Groupes réellement résolus
          |
          v
Comparaison
          |
          +-- Conforme
          |
          +-- Écart à examiner
```

Une différence ne doit pas déclencher automatiquement la suppression d'un compte sans comprendre son origine.

Il peut s'agir d'une modification autorisée, d'une panne de résolution ou d'un problème de disponibilité.

La correction automatisée doit être conçue selon la criticité du système et les responsabilités des administrateurs.

## 19.5. Gestion de configuration

Dans une infrastructure importante, un outil de gestion de configuration peut maintenir des paramètres tels que :

- Les paquets attendus.
- Les services actifs.
- Les fichiers SSSD.
- Les règles sudoers.
- Les fichiers de confiance.
- Les autorisations SSH.
- Les politiques locales.

L'outil doit préserver les secrets et distinguer les données publiques de configuration des informations confidentielles.

Un système automatisé peut aussi propager très rapidement une configuration incorrecte. Il faut donc tester, valider et prévoir un retour arrière.

## 19.6. Gestion des secrets dans l'automatisation

Évite de stocker directement dans les scripts :

- Le mot de passe du compte d'adhésion.
- Les secrets LDAP.
- Les clés privées.
- Les keytabs.
- Les jetons d'accès.
- Les mots de passe de comptes techniques.

Utilise le mécanisme de gestion des secrets approuvé dans l'environnement.

Les fichiers de variables, les journaux et les artefacts d'automatisation doivent être protégés en conséquence.


# 20. Laboratoires pratiques avancés

Les laboratoires doivent être effectués dans un environnement de test disposant des services nécessaires.

Les commandes qui modifient l'accès au domaine, PAM ou SSH ne doivent pas être exécutées aveuglément sur une machine de production.

## Laboratoire 1 — Cartographier la chaîne d'identité

### Objectif

Comprendre quelles couches interviennent dans la résolution et l'authentification d'un compte.

### Étape 1 : examiner NSS

```bash
grep -E '^(passwd|group|shadow):' /etc/nsswitch.conf
```

### Étape 2 : examiner SSSD

```bash
systemctl status sssd
realm list
```

### Étape 3 : identifier un utilisateur centralisé

```bash
getent passwd 'alice@ad.example.test'
id 'alice@ad.example.test'
```

### Étape 4 : examiner PAM et SSH

```bash
ls /etc/pam.d/
sudo sshd -t
```

### Travail demandé

Dessine la chaîne de résolution, d'authentification et d'autorisation de ton laboratoire.

### Validation

Tu dois pouvoir identifier le rôle de NSS, PAM et SSSD sans les confondre.


## Laboratoire 2 — Vérifier DNS et Kerberos

### Objectif

Démontrer que la découverte du domaine et l'authentification par tickets dépendent de plusieurs conditions.

### Étape 1 : consulter l'heure

```bash
timedatectl
```

### Étape 2 : examiner DNS

```bash
dig SRV _ldap._tcp.ad.example.test
dig SRV _kerberos._tcp.ad.example.test
```

### Étape 3 : consulter le cache Kerberos

```bash
klist
```

### Étape 4 : demander un ticket dans le laboratoire

```bash
kinit alice@AD.EXAMPLE.TEST
```

### Étape 5 : contrôler le ticket

```bash
klist
```

### Travail demandé

Explique pourquoi un ticket valide ne garantit pas qu'Alice puisse modifier `/srv/projets`.

### Validation

Tu dois distinguer l'authentification Kerberos des permissions Linux.


## Laboratoire 3 — Vérifier la stratégie UID/GID

### Objectif

Comprendre comment Linux représente un utilisateur AD.

### Étape 1 : examiner le compte

```bash
id 'alice@ad.example.test'
getent passwd 'alice@ad.example.test'
```

### Étape 2 : examiner la stratégie de correspondance

```bash
sudo grep -E '^(ldap_id_mapping|use_fully_qualified_names)' /etc/sssd/sssd.conf
```

L'absence d'un paramètre explicite ne signifie pas nécessairement qu'il est désactivé : certaines valeurs par défaut dépendent de la version et du fournisseur.

### Étape 3 : examiner les propriétaires

```bash
ls -ln /srv/projets
```

### Travail demandé

Explique les différences entre le SID, l'UID et le GID.

### Validation

Tu dois pouvoir expliquer pourquoi un changement de stratégie de correspondance doit être planifié avant d'être déployé.


## Laboratoire 4 — Contrôler l'accès au serveur

### Objectif

Valider une politique de connexion reposant sur un groupe.

### Étape 1 : examiner le groupe

```bash
id 'alice@ad.example.test'
```

### Étape 2 : examiner la politique

```bash
realm list
```

### Étape 3 : définir un test autorisé

Utilise un compte qui doit réellement être autorisé.

### Étape 4 : définir un test interdit

Utilise un compte de laboratoire qui ne doit pas être autorisé.

### Étape 5 : tester les deux cas

Effectue les connexions de test conformément aux méthodes utilisées par ton serveur.

### Travail demandé

Documente le résultat attendu, le résultat observé, les journaux et la cause de toute différence.

### Validation

Le serveur doit autoriser les comptes prévus et refuser ceux qui ne font pas partie de la politique.


## Laboratoire 5 — Examiner un problème SSSD sans supprimer le cache

### Objectif

Développer une démarche de diagnostic avant toute intervention destructive.

### Étape 1 : vérifier le service

```bash
systemctl status sssd
```

### Étape 2 : consulter les journaux

```bash
sudo journalctl -u sssd --since "30 minutes ago"
```

### Étape 3 : examiner le domaine

```bash
sudo sssctl domain-status ad.example.test
```

### Étape 4 : examiner l'identité

```bash
getent passwd 'alice@ad.example.test'
id 'alice@ad.example.test'
```

### Étape 5 : vérifier DNS et heure

```bash
timedatectl
dig SRV _ldap._tcp.ad.example.test
dig SRV _kerberos._tcp.ad.example.test
```

### Travail demandé

Écris une hypothèse testable à partir des résultats.

### Validation

Tu dois expliquer pourquoi la suppression du cache n'est pas la première mesure à appliquer systématiquement.


## Laboratoire 6 — Vérifier les règles sudo

### Objectif

Auditer une délégation administrative.

### Étape 1 : consulter les droits

```bash
sudo -l
```

### Étape 2 : vérifier les groupes

```bash
id
```

### Étape 3 : vérifier la syntaxe sudoers

```bash
sudo visudo -c
```

### Étape 4 : examiner les exceptions

Inventorie les règles du répertoire `/etc/sudoers.d/` si les permissions le permettent.

### Travail demandé

Rédige un tableau contenant :

```text
Compte/groupe
Commande autorisée
Justification
Risque principal
Test positif
Test négatif
Date de revue
```

### Validation

Tu dois pouvoir expliquer pourquoi une commande unique peut éventuellement permettre des opérations plus larges que prévu.


## Laboratoire 7 — Contrôler le retrait d'accès

### Objectif

Préparer une procédure de révocation d'un compte centralisé.

### Étape 1 : identifier l'utilisateur

```bash
id 'alice@ad.example.test'
```

### Étape 2 : recenser les groupes

Documente les groupes attendus et leur rôle.

### Étape 3 : examiner les accès locaux

Contrôle les permissions, les ACL et les règles sudo applicables.

### Étape 4 : examiner les méthodes de connexion

Vérifie SSH, PAM, les clés et les sessions actives selon la politique de l'organisation.

### Étape 5 : simuler le retrait dans le laboratoire

Effectue la modification dans la source d'identité de test, conformément aux règles de ton environnement.

### Étape 6 : contrôler les effets

Vérifie de nouveau les groupes, l'accès au serveur et les permissions.

### Validation

Tu dois pouvoir démontrer le retrait des accès attendus sans détruire les données qui doivent être conservées.


## Laboratoire 8 — Auditer une configuration SSSD

### Objectif

Préparer une fiche de contrôle avant un changement en production.

Collecte :

```bash
realm list
systemctl status sssd
sudo sssctl domain-status ad.example.test
getent passwd 'alice@ad.example.test'
id 'alice@ad.example.test'
sudo journalctl -u sssd --since "30 minutes ago"
```

Puis relève :

```text
Version de la distribution :
Version SSSD :
Fournisseur :
Domaine :
Méthode UID/GID :
Format des noms :
Fournisseur d'accès :
Cache activé :
Mode hors ligne prévu :
Groupe d'administration :
Compte de secours :
Procédure de retour arrière :
Tests positifs :
Tests négatifs :
```

### Validation

Un autre administrateur doit pouvoir comprendre la configuration avant la modification.


# 21. Exercices experts corrigés

## Exercice 1 — Identité et authentification

`getent passwd` trouve un utilisateur, mais SSH refuse sa connexion.

Quelle conclusion peut-on tirer ?

**Correction :**

L'identité est résolue dans le contexte du test, mais l'authentification ou l'autorisation peut échouer.

Il faut examiner SSH, PAM, SSSD, Kerberos ou LDAP selon l'architecture, ainsi que la politique d'accès au serveur.

La résolution d'une identité ne garantit pas une session autorisée.

## Exercice 2 — Correspondance des identifiants

Pourquoi est-il dangereux de changer de stratégie UID/GID sans plan de migration ?

**Correction :**

Les fichiers conservent leurs propriétaires numériques.

Si l'UID d'Alice change, ses anciens fichiers ne deviennent pas automatiquement la propriété du nouvel UID.

Il faut identifier les fichiers concernés et planifier leur traitement.

## Exercice 3 — LDAP et AD

LDAP et Active Directory sont-ils des technologies équivalentes ?

**Correction :**

Non.

LDAP est un protocole d'accès à un annuaire.

Active Directory Domain Services est un service d'annuaire qui s'intègre à plusieurs technologies, dont LDAP, Kerberos et DNS.

## Exercice 4 — DNS

Pourquoi un mauvais DNS peut-il empêcher l'intégration à AD même si le contrôleur est joignable par adresse IP ?

**Correction :**

L'intégration peut dépendre de la découverte des services via des enregistrements DNS et des noms des principaux ou services.

Une connectivité IP directe ne remplace pas automatiquement cette découverte.

## Exercice 5 — Cache SSSD

Pourquoi la suppression du cache ne doit-elle pas être la première action à chaque incident ?

**Correction :**

Le problème peut venir du DNS, du réseau, du fournisseur, de la configuration ou des autorisations.

Vider le cache ne corrige pas nécessairement la cause et peut réduire la capacité de fonctionnement hors ligne.

Il faut collecter les observations avant d'agir.

## Exercice 6 — Kerberos

Un utilisateur peut obtenir un TGT mais ne peut pas modifier un fichier.

Pourquoi ?

**Correction :**

Le TGT indique une réussite dans une étape de l'authentification Kerberos.

Les permissions du fichier dépendent des UID/GID effectifs, des groupes, des ACL, des permissions du chemin et des autres contrôles.

## Exercice 7 — Domaine approuvé

Pourquoi un utilisateur issu d'une forêt différente peut-il ne pas être résolu par un client SSSD configuré avec le fournisseur AD ?

**Correction :**

Les capacités de découverte des domaines approuvés dépendent de l'architecture et de la version.

Une intégration directe SSSD/AD ne couvre pas automatiquement toutes les topologies multi-forêts.

Il faut vérifier les relations d'approbation et choisir un mécanisme d'intégration compatible avec les besoins.

## Exercice 8 — sudo limité

Pourquoi autoriser un binaire précis dans sudoers ne garantit-il pas toujours le moindre privilège ?

**Correction :**

Le binaire peut permettre de lancer d'autres programmes, de modifier des fichiers arbitraires ou d'obtenir un shell.

Il faut analyser ses possibilités et les arguments permis.

## Exercice 9 — Révocation

Pourquoi désactiver le compte AD ne termine-t-il pas nécessairement une session SSH déjà ouverte ?

**Correction :**

La session a déjà été authentifiée et peut continuer à exister selon le service et la politique locale.

Il faut appliquer la procédure de contrôle des sessions et des accès persistants.

## Exercice 10 — LDAP TLS

Pourquoi la validation du certificat LDAP est-elle importante ?

**Correction :**

Elle permet au client de vérifier la confiance accordée au serveur contacté.

Accepter n'importe quel certificat peut permettre à un serveur non approuvé d'usurper l'annuaire ou d'intercepter les communications.

## Exercice 11 — Groupes imbriqués

Pourquoi faut-il tester les groupes effectivement résolus par Linux au lieu de supposer que tous les groupes de l'annuaire apparaîtront ?

**Correction :**

Le résultat dépend des propriétés du fournisseur, de la structure de groupes, des domaines, du cache et des paramètres SSSD.

Il faut contrôler les groupes obtenus pour les comptes réels.

## Exercice 12 — Continuité de service

Un serveur est isolé du réseau. Certains utilisateurs peuvent encore ouvrir une session.

Cela prouve-t-il que l'annuaire est disponible ?

**Correction : Non.**

Le résultat peut provenir du cache et du mode hors ligne autorisé par la configuration.

Il faut distinguer la résolution locale des informations mises en cache de la disponibilité réelle du fournisseur distant.


# 22. Défi final : concevoir une architecture d'identité d'entreprise

## 22.1. Contexte

Une entreprise utilise Active Directory pour gérer ses utilisateurs, ses groupes et ses ordinateurs.

Elle déploie maintenant 40 serveurs Linux, répartis entre les environnements suivants :

- Développement.
- Exploitation.
- Production.
- Audit.

Les administrateurs veulent centraliser les identités, limiter les privilèges et standardiser les contrôles.

Le système doit rester exploitable malgré certaines pannes temporaires et permettre un dépannage documenté.

## 22.2. Besoins

L'architecture doit fournir :

1. Une source d'identité centrale.
2. Une correspondance UID/GID cohérente.
3. Une méthode d'authentification validée.
4. Une résolution correcte des groupes.
5. Une politique d'accès par serveur.
6. Des privilèges administratifs limités.
7. Des répertoires personnels correctement gérés.
8. Une protection des secrets et du transport.
9. Une méthode de révocation des accès.
10. Une surveillance de l'état de l'intégration.
11. Une procédure de récupération lorsque le domaine est inaccessible.
12. Une méthode d'audit périodique.

## 22.3. Mission 1 — Choisir l'architecture

Documente :

```text
Source d'identité :
Domaine :
Fournisseur SSSD :
Mécanisme d'authentification :
Stratégie UID/GID :
Format des noms :
Groupes autorisés :
Méthode de gestion des répertoires personnels :
Méthode d'audit :
```

**Livrable :** un schéma illustrant les composants et les flux de connexion.

## 22.4. Mission 2 — Définir les dépendances réseau

Identifie :

- Les résolveurs DNS.
- Les contrôleurs de domaine.
- Les services nécessaires.
- La synchronisation de l'heure.
- Les flux autorisés par le réseau.
- Les chemins de secours.
- Les contrôles de certificat éventuellement nécessaires.

**Livrable :** une matrice réseau expliquant quel composant doit pouvoir communiquer avec quel service et pour quelle fonction.

## 22.5. Mission 3 — Choisir une stratégie UID/GID

Compare :

- La correspondance automatique à partir des SID.
- L'utilisation d'attributs POSIX gérés dans l'annuaire.

Explique :

- Comment les identifiants sont générés ou attribués.
- Comment les identifiants restent cohérents entre serveurs.
- Quel est l'impact sur les fichiers existants.
- Quelle stratégie est utilisée pour les systèmes de fichiers partagés.
- Comment une migration serait planifiée.

**Livrable :** une politique d'identifiants documentée.

## 22.6. Mission 4 — Mettre en place un pilote

Sur une machine non critique :

1. Vérifie DNS et l'heure.
2. Installe les outils d'intégration.
3. Découvre le domaine.
4. Joins le domaine.
5. Vérifie SSSD.
6. Vérifie les utilisateurs et groupes.
7. Teste une session autorisée.
8. Teste une session interdite.
9. Vérifie les permissions des fichiers.
10. Documente les résultats.

**Livrable :** un compte rendu de test avec les commandes et les résultats observés.

## 22.7. Mission 5 — Construire la politique d'accès

Définis des règles distinctes pour :

```text
Développement
Production
Exploitation
Audit
```

Chaque catégorie doit avoir des autorisations adaptées à ses responsabilités.

Détermine :

- Qui peut ouvrir une session.
- Qui peut utiliser SSH.
- Qui peut exécuter des commandes privilégiées.
- Qui peut modifier les fichiers applicatifs.
- Qui peut lire les journaux.
- Qui peut consulter les données sensibles.

**Livrable :** une matrice d'accès.

## 22.8. Mission 6 — Concevoir sudo

Pour chaque règle, précise :

```text
Compte/groupe :
Commande permise :
Identité d'exécution :
Justification :
Risques :
Test positif :
Test négatif :
Date de revue :
```

Vérifie que les commandes autorisées ne créent pas un chemin indirect vers des privilèges plus larges.

**Livrable :** une politique sudo et sa procédure de validation.

## 22.9. Mission 7 — Préparer l'exploitation hors ligne

Détermine ce qui doit continuer à fonctionner si :

- Le DNS est indisponible.
- Un contrôleur de domaine est en panne.
- SSSD est arrêté.
- Le réseau est coupé.
- Une information de groupe vient d'être modifiée dans l'annuaire.

Précise les services qui doivent être disponibles et les risques acceptables.

**Livrable :** une matrice de continuité.

## 22.10. Mission 8 — Définir la révocation

Prépare une procédure de départ d'un collaborateur, incluant :

- Désactivation de l'identité.
- Retrait des groupes.
- Contrôle des règles sudo.
- Révocation des clés.
- Contrôle des sessions.
- Traitement des fichiers.
- Vérification des accès externes.
- Documentation.

**Livrable :** un runbook de retrait d'accès.

## 22.11. Mission 9 — Construire la supervision

Les contrôles doivent inclure :

- État de SSSD.
- Résolution de comptes de référence.
- État d'adhésion.
- DNS et heure.
- Disponibilité des services centraux.
- Échecs d'authentification.
- Erreurs TLS ou Kerberos.
- Groupes administratifs.
- Validité de la configuration sudo.
- État des comptes de secours.

**Livrable :** une matrice d'alertes avec un responsable, un seuil ou une condition, et une procédure d'action.

## 22.12. Mission 10 — Démontrer la récupération

Simule un incident dans le laboratoire.

Exemples :

- Résolveur incorrect.
- Compte de test non autorisé.
- Groupe attendu absent.
- Service SSSD arrêté.
- Entrée de configuration invalide.
- Session refusée par la politique d'accès.

Pour chaque scénario :

1. Collecte les observations.
2. Identifie la première couche en échec.
3. Formule une hypothèse.
4. Effectue un test ciblé.
5. Corrige le problème.
6. Vérifie les accès positifs et négatifs.
7. Documente le résultat.

**Livrable :** un dossier de dépannage montrant la cause, la correction et les tests finaux.


# 23. Correction détaillée du défi final

La correction suivante donne une architecture de référence. Elle doit être adaptée au domaine, à la distribution et aux politiques réelles de l'entreprise.

## 23.1. Architecture de référence

```text
                   Active Directory
                         |
            +------------+------------+
            |                         |
            v                         v
           DNS                     Kerberos
            |                         |
            +------------+------------+
                         |
                         v
                    Serveur Linux
                         |
                         v
                        SSSD
                         |
                +--------+--------+
                |                 |
                v                 v
               NSS               PAM
                |                 |
                v                 v
        Identités/groupes   Authentification
                |                 |
                +--------+--------+
                         |
                         v
                  Politique d'accès
                         |
              +----------+----------+
              |                     |
              v                     v
           Session           Privilèges et
           utilisateur       accès aux ressources
```

Cette architecture utilise les mécanismes appropriés au fournisseur AD et à la version déployée.

## 23.2. Vérifier les conditions préalables

Les contrôles de départ peuvent inclure :

```bash
hostnamectl
hostname -f
resolvectl status
timedatectl
```

Puis :

```bash
dig SRV _ldap._tcp.ad.example.test
dig SRV _kerberos._tcp.ad.example.test
```

Si ces prérequis ne sont pas cohérents, il faut les corriger avant l'intégration.

## 23.3. Vérifier l'intégration

```bash
realm list
systemctl status sssd
sudo sssctl domain-status ad.example.test
```

La dernière commande dépend de la version installée.

Le but est de confirmer que le domaine est reconnu, que le service fonctionne et que le fournisseur est accessible.

## 23.4. Vérifier les identités

```bash
getent passwd 'alice@ad.example.test'
id 'alice@ad.example.test'
```

Le système doit résoudre l'utilisateur et les groupes attendus.

Une résolution incorrecte doit être traitée avant de créer des ACL ou des règles sudo fondées sur ce compte.

## 23.5. Définir les politiques d'accès

La politique doit séparer :

- Les utilisateurs autorisés à ouvrir une session.
- Les utilisateurs autorisés à accéder aux données.
- Les utilisateurs autorisés à exécuter des commandes administratives.
- Les comptes de secours.
- Les comptes de service.

Un groupe métier ne doit pas automatiquement recevoir l'ensemble des privilèges du serveur.

## 23.6. Définir la stratégie UID/GID

La stratégie retenue doit être uniforme dans l'infrastructure.

Si les identifiants sont calculés à partir des SID, la configuration doit garantir un calcul cohérent.

Si les identifiants POSIX sont gérés dans l'annuaire, l'attribution doit être contrôlée pour éviter les doublons et incohérences.

Les changements doivent être accompagnés d'une analyse des propriétaires des fichiers existants.

## 23.7. Tester le modèle de permissions

Pour un répertoire partagé, vérifie :

```bash
id 'alice@ad.example.test'
ls -ld /srv/projets
namei -l /srv/projets
getfacl /srv/projets
```

Teste les opérations avec un utilisateur autorisé et un utilisateur non autorisé.

Le test doit démontrer que les permissions sont appliquées comme prévu, pas seulement qu'un compte peut se connecter.

## 23.8. Vérifier sudo

Contrôle :

```bash
sudo -l
sudo visudo -c
```

Établis un inventaire de chaque règle et examine les possibilités offertes par les commandes autorisées.

## 23.9. Tester la continuité

Simule les pannes uniquement dans un environnement de test.

Vérifie :

- Les résultats obtenus lorsque le fournisseur est accessible.
- Les résultats lorsque le fournisseur est inaccessible.
- Les limites du cache.
- La possibilité de récupérer le serveur.
- Les risques associés aux comptes de secours.

Ne considère pas le cache comme un substitut à une architecture centrale disponible.

## 23.10. Valider le retrait d'accès

Après un retrait dans la source d'identité :

1. Vérifie les groupes résolus.
2. Vérifie les règles d'accès.
3. Contrôle les nouvelles connexions.
4. Vérifie les sessions actives.
5. Contrôle les clés et autres méthodes d'accès.
6. Examine les autorisations locales.
7. Vérifie le traitement des données.
8. Documente les preuves de validation.

La clôture de l'opération nécessite une vérification de toutes les voies d'accès importantes, pas uniquement le verrouillage du mot de passe.


# 24. Checklist opérationnelle

## Avant une intégration AD ou LDAP

- [ ] Identifier la source d'identité.
- [ ] Confirmer le domaine et le schéma.
- [ ] Vérifier DNS et les services de découverte.
- [ ] Vérifier la synchronisation de l'heure.
- [ ] Vérifier le réseau et les certificats.
- [ ] Choisir le fournisseur SSSD approprié.
- [ ] Définir la stratégie UID/GID.
- [ ] Définir le format des noms.
- [ ] Définir les groupes autorisés.
- [ ] Préserver un accès de secours.
- [ ] Préparer une procédure de retour arrière.

## Après l'intégration

- [ ] Vérifier l'état du domaine.
- [ ] Vérifier SSSD.
- [ ] Vérifier les journaux.
- [ ] Résoudre plusieurs identités de test.
- [ ] Vérifier les groupes et les identifiants.
- [ ] Tester une authentification réelle.
- [ ] Tester les refus attendus.
- [ ] Vérifier les répertoires personnels.
- [ ] Vérifier les permissions des ressources.
- [ ] Documenter la configuration.

## Pour une modification UID/GID

- [ ] Identifier la stratégie actuelle.
- [ ] Examiner les identifiants réellement attribués.
- [ ] Contrôler les systèmes de fichiers partagés.
- [ ] Rechercher les fichiers concernés.
- [ ] Planifier la migration des propriétés.
- [ ] Tester les permissions après modification.
- [ ] Vérifier tous les serveurs dépendants.
- [ ] Documenter les résultats.

## Pour sudo et PAM

- [ ] Définir le besoin d'autorisation.
- [ ] Examiner les règles existantes.
- [ ] Éviter les privilèges globaux inutiles.
- [ ] Examiner les possibilités de contournement.
- [ ] Valider la syntaxe.
- [ ] Préserver une session de secours.
- [ ] Tester les connexions autorisées et refusées.
- [ ] Documenter les exceptions.

## Pour un incident SSSD/Kerberos/LDAP

- [ ] Identifier le symptôme exact.
- [ ] Contrôler DNS.
- [ ] Contrôler l'heure.
- [ ] Vérifier le domaine et le fournisseur.
- [ ] Vérifier l'état de SSSD.
- [ ] Consulter les journaux.
- [ ] Contrôler la résolution de l'utilisateur.
- [ ] Contrôler les groupes.
- [ ] Examiner l'authentification.
- [ ] Examiner la politique d'accès.
- [ ] Ne pas supprimer le cache sans justification.
- [ ] Tester après correction.

## Pour le départ d'un utilisateur

- [ ] Désactiver ou retirer les accès centraux appropriés.
- [ ] Retirer les groupes inutiles.
- [ ] Contrôler les sessions existantes.
- [ ] Révoquer les clés et secrets associés.
- [ ] Vérifier les privilèges sudo.
- [ ] Examiner les fichiers et données.
- [ ] Contrôler les comptes locaux.
- [ ] Retirer les accès externes.
- [ ] Documenter le résultat.


# 25. Référence des commandes essentielles

## 25.1. Identités et groupes

| Commande | Fonction |
|---|---|
| `getent passwd` | Résolution des comptes selon NSS |
| `getent group` | Résolution des groupes selon NSS |
| `id utilisateur` | UID, GID principal et groupes |
| `realm list` | Domaines configurés |
| `realm discover domaine` | Découverte du domaine |
| `sudo sssctl domain-status domaine` | État du domaine dans SSSD, selon la version |
| `sudo sssctl user-checks utilisateur -s sshd` | Contrôles d'accès liés à un service, selon la version |

## 25.2. DNS et Kerberos

| Commande | Fonction |
|---|---|
| `dig SRV _ldap._tcp.domaine` | Examiner la découverte LDAP |
| `dig SRV _kerberos._tcp.domaine` | Examiner la découverte Kerberos |
| `timedatectl` | Examiner l'heure et la synchronisation |
| `chronyc tracking` | Vérifier l'état de chrony, si installé |
| `klist` | Consulter les tickets |
| `kinit principal` | Demander un ticket |
| `kvno principal/service` | Demander ou examiner un ticket de service, selon le contexte |
| `sudo klist -kte /etc/krb5.keytab` | Examiner les principaux dans un keytab |
| `sudo adcli testjoin` | Vérifier l'adhésion AD lorsque l'outil est disponible |

## 25.3. SSSD et journaux

| Commande | Fonction |
|---|---|
| `systemctl status sssd` | État du service |
| `sudo journalctl -u sssd --since "30 minutes ago"` | Journaux récents |
| `sudo sssctl domain-status domaine` | État du fournisseur |
| `sudo sssctl cache-expire -u utilisateur` | Invalider une entrée ciblée, selon la version |
| `sudo sssctl debug-level niveau` | Modifier le niveau de journalisation si pris en charge |

## 25.4. LDAP

| Commande | Fonction |
|---|---|
| `ldapsearch -x -H URI -b BASE FILTRE` | Recherche dans un annuaire |
| `getent passwd utilisateur` | Vérifier la résolution Linux |
| `getent group groupe` | Vérifier la résolution d'un groupe |
| `openssl s_client ...` | Outil possible pour examiner une connexion TLS, selon les paramètres du serveur |

## 25.5. Accès et permissions

| Commande | Fonction |
|---|---|
| `sudo -l` | Consulter les droits sudo |
| `sudo visudo -c` | Vérifier la syntaxe de sudoers |
| `sudo sshd -t` | Vérifier la syntaxe SSH |
| `namei -l chemin` | Examiner les permissions de chaque composant d'un chemin |
| `getfacl chemin` | Lire les ACL |
| `ls -ln chemin` | Afficher les propriétaires numériques |
| `sudo find chemin -xdev -uid UID -print` | Rechercher des fichiers par UID |

Les commandes doivent être adaptées aux paquets, versions et politiques réellement utilisés.


# 26. Documentation de référence

Les ressources suivantes permettent d'approfondir les fonctions, les paramètres et les procédures.

## Intégration Active Directory

- Ubuntu — Configurer SSSD avec Active Directory :  
  https://ubuntu.com/server/docs/how-to/sssd/with-active-directory/

- Ubuntu — Introduction à l'authentification réseau avec SSSD :  
  https://ubuntu.com/server/docs/service-sssd/

- Red Hat — Intégrer directement Linux à Active Directory avec SSSD :  
  https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html/integrating_rhel_systems_directly_with_windows_active_directory/connecting-rhel-systems-directly-to-ad-using-sssd

- Microsoft Learn — Active Directory Domain Services :  
  https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/active-directory-domain-services-overview

## SSSD et dépannage

- SSSD — Introduction :  
  https://sssd.io/docs/introduction.html

- SSSD — Dépannage général :  
  https://sssd.io/troubleshooting/basics.html

- Ubuntu — Dépannage SSSD :  
  https://ubuntu.com/server/docs/how-to/sssd/troubleshooting/

## LDAP

- RFC 4511 — LDAP :  
  https://www.rfc-editor.org/rfc/rfc4511

- OpenLDAP — Guide de l'administrateur :  
  https://openldap.org/doc/admin27/guide.html

## Kerberos

- RFC 4120 — The Kerberos Network Authentication Service :  
  https://www.rfc-editor.org/rfc/rfc4120

## Manuels locaux

Les manuels suivants peuvent être utiles lorsque les paquets sont installés :

```bash
man sssd
man sssd.conf
man sssctl
man realm
man adcli
man krb5.conf
man kinit
man klist
man getent
man nsswitch.conf
man pam
man sudoers
man sshd_config
```

Les paramètres disponibles, les valeurs par défaut et les procédures prises en charge peuvent varier selon la version. Consulte toujours la documentation correspondant au système réellement administré.


# Conclusion

L'administration experte des utilisateurs et des groupes sous Linux consiste à maîtriser l'ensemble du système d'identité, depuis la source centralisée jusqu'aux autorisations effectivement appliquées sur le serveur.

Tu as approfondi :

- La distinction entre identité, authentification et autorisation.
- Le rôle respectif de LDAP et d'Active Directory.
- Kerberos, les tickets et les keytabs.
- SSSD, ses fournisseurs et ses mécanismes de cache.
- Les stratégies de correspondance entre SID, UID et GID.
- Les architectures AD comportant plusieurs domaines.
- La sécurité et la disponibilité LDAP.
- Les politiques d'accès au serveur.
- PAM et l'authentification multifacteur.
- La délégation administrative avec sudo.
- Les accès SSH des identités centralisées.
- La gouvernance et la révocation des comptes.
- La gestion des comptes techniques.
- L'audit et l'observabilité.
- Le dépannage méthodique.
- L'automatisation contrôlée.

Le principe opérationnel à retenir est :

```text
              SOURCE D'IDENTITÉ
                   LDAP / AD
                       |
                       v
              IDENTITÉ RÉSOLUE
                       |
                       v
              AUTHENTIFICATION
          Kerberos / PAM / autres
                       |
                       v
              CONTRÔLE D'ACCÈS
              SSSD / politiques
                       |
                       v
               SESSION AUTORISÉE
                       |
                       v
          UID / GID / GROUPES EFFECTIFS
                       |
                       v
           PERMISSIONS / ACL / SUDO
                       |
                       v
                  ACTION RÉELLE
                       |
                       v
                  AUDIT ET SUIVI
```

Cette représentation est simplifiée : le flux exact dépend des fournisseurs et services configurés.

Une architecture experte ne se contente pas de vérifier que les utilisateurs peuvent se connecter. Elle garantit que les identités sont cohérentes, que les droits sont limités, que les erreurs peuvent être diagnostiquées et que les accès peuvent être révoqués de manière contrôlée.

**Le véritable niveau expert est atteint lorsque tu peux expliquer pourquoi une connexion fonctionne, pourquoi elle échoue, quelles autorisations sont réellement accordées et comment restaurer le service sans affaiblir la sécurité.**