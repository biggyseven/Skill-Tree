# Gestion des paquets Linux — Niveau Débutant

> **Fichier :** `packages-debutant.md`  
> **Niveau :** Débutant  
> **Domaine :** Administration système Linux  
> **Thème :** Installation, recherche, mise à jour, suppression et dépannage des paquets logiciels  
> **Environnement principal :** Debian et Ubuntu  
> **Ouverture :** Fedora, RHEL et Arch Linux  
> **Prérequis :** Savoir utiliser un terminal, exécuter des commandes Linux, naviguer dans les répertoires et comprendre les bases des permissions.


# Sommaire

1. Introduction à la gestion des paquets
2. Comprendre un paquet logiciel
3. Pourquoi utiliser un gestionnaire de paquets ?
4. Les principales familles de distributions Linux
5. Comprendre les dépôts logiciels
6. Découvrir APT et dpkg
7. Identifier le système et les outils disponibles
8. Rechercher un paquet
9. Consulter les informations d'un paquet
10. Installer un paquet avec APT
11. Comprendre les dépendances
12. Mettre à jour la liste des paquets et les logiciels installés
13. Comprendre les mises à jour de sécurité
14. Supprimer un paquet proprement
15. Nettoyer les dépendances inutilisées
16. Lister les paquets et vérifier leur état
17. Identifier les fichiers installés par un paquet
18. Installer un paquet local
19. Comprendre les dépôts et leur configuration
20. Sécurité, signatures et confiance
21. Comparaison avec DNF/RPM et Pacman
22. Fonctionnement interne d'une installation
23. Journaux, erreurs et dépannage
24. Gestion des paquets dans les environnements serveur
25. Automatiser des opérations simples
26. Travaux pratiques guidés
27. Exercices d'application
28. Corrections détaillées
29. Défi final : préparer un serveur Linux
30. Correction détaillée du défi final
31. Checklist de compétences
32. Fiche de révision
33. Glossaire
34. Documentation officielle


# 1. Introduction à la gestion des paquets

## 1.1. Qu'est-ce qu'un paquet logiciel ?

Linux peut exécuter des logiciels, mais un administrateur doit aussi pouvoir les installer, les mettre à jour, les supprimer et vérifier leur état.

Prenons quelques exemples de logiciels courants :

- `curl` : outil de communication avec des serveurs ;
- `htop` : visualisation interactive des processus ;
- `nginx` : serveur Web et proxy ;
- `openssh-server` : serveur SSH ;
- `python3` : interpréteur Python ;
- `vim` : éditeur de texte ;
- `tcpdump` : outil de capture réseau.

Sur de nombreuses distributions Linux, ces logiciels peuvent être distribués sous forme de **paquets**.

Un paquet est une unité de distribution logicielle qui contient notamment des fichiers, des informations d'identification, des métadonnées et des règles relatives à l'installation.

Selon le logiciel et le format, il peut aussi contenir des scripts exécutés pendant certaines étapes de son installation ou de sa suppression.

## 1.2. Pourquoi la gestion des paquets est-elle importante ?

Imagine un serveur qui doit héberger une application Web.

L'administrateur doit éventuellement :

1. installer le serveur Web ;
2. installer ses dépendances ;
3. appliquer les mises à jour de sécurité ;
4. consulter la version installée ;
5. identifier les fichiers fournis par le paquet ;
6. réparer une installation défectueuse ;
7. supprimer un logiciel devenu inutile ;
8. conserver un système cohérent après les changements.

Sans gestionnaire de paquets, ces opérations nécessiteraient davantage de travail manuel et seraient plus difficiles à reproduire.

La gestion des paquets est donc une compétence fondamentale de l'administration Linux.

## 1.3. Les objectifs de ce cours

À la fin de ce cours, tu dois être capable de :

- expliquer ce qu'est un paquet logiciel ;
- distinguer un paquet d'un dépôt ;
- comprendre la notion de dépendance ;
- identifier le gestionnaire de paquets de ta distribution ;
- rechercher un logiciel disponible ;
- consulter sa version et sa description ;
- installer un paquet ;
- mettre à jour la liste des paquets disponibles ;
- mettre à jour les logiciels installés ;
- différencier `apt update` et `apt upgrade` ;
- supprimer un paquet sans effacer inutilement d'autres logiciels ;
- reconnaître les dépendances devenues inutiles ;
- vérifier si un paquet est installé ;
- retrouver les fichiers fournis par un paquet ;
- installer un paquet local en tenant compte de ses dépendances ;
- comprendre les principes de sécurité des dépôts ;
- diagnostiquer les erreurs courantes de gestion de paquets ;
- travailler prudemment sur un serveur.

## 1.4. La méthode de travail

La méthode à retenir est la suivante :

```text
BESOIN LOGICIEL
      |
      v
IDENTIFIER LA DISTRIBUTION
      |
      v
RECHERCHER LE PAQUET
      |
      v
VÉRIFIER SON ORIGINE ET SA VERSION
      |
      v
EXAMINER LES DÉPENDANCES
      |
      v
INSTALLER OU MODIFIER
      |
      v
VÉRIFIER LE RÉSULTAT
      |
      v
MAINTENIR ET SÉCURISER
```

Il ne suffit pas qu'une commande se termine sans erreur. Il faut vérifier que le paquet a bien été installé et que le logiciel remplit sa fonction.


# 2. Comprendre un paquet logiciel

## 2.1. Un logiciel peut comprendre plusieurs paquets

Un logiciel complexe est rarement constitué d'un seul fichier.

Il peut nécessiter :

- un programme exécutable ;
- des bibliothèques ;
- des fichiers de configuration ;
- des fichiers de documentation ;
- des outils auxiliaires ;
- des données partagées ;
- des services système.

La distribution peut répartir ces composants dans plusieurs paquets.

Exemple conceptuel :

```text
APPLICATION WEB
      |
      +-- paquet serveur-web
      |
      +-- paquet bibliothèque-réseau
      |
      +-- paquet bibliothèque-crypto
      |
      +-- paquet fichiers-configuration
      |
      +-- paquet documentation
```

Ces noms sont illustratifs : les véritables noms et le découpage dépendent de la distribution.

## 2.2. Que contient un paquet ?

Un paquet peut contenir plusieurs catégories d'informations.

| Élément | Rôle |
|---|---|
| Nom | Identifier le paquet |
| Version | Identifier une révision du logiciel |
| Architecture | Indiquer la plateforme concernée |
| Description | Expliquer l'utilité du paquet |
| Fichiers | Contenir les éléments installés |
| Dépendances | Déclarer les autres composants nécessaires |
| Métadonnées | Décrire le paquet et ses propriétés |
| Scripts de maintenance éventuels | Effectuer certaines opérations prévues lors de l'installation ou de la suppression |

Les champs exacts dépendent du format du paquet.

## 2.3. Comprendre le nom et la version

Exemple fictif d'identification :

```text
outil-reseau 2.4.1-3 amd64
```

Cette présentation pourrait représenter :

```text
Nom           : outil-reseau
Version       : 2.4.1-3
Architecture  : amd64
```

La signification détaillée du suffixe de version dépend du système de paquetage.

Une version amont, une révision du paquet de distribution et une architecture ne doivent pas être confondues.

Dans une distribution Linux, le numéro affiché ne correspond pas toujours directement au dernier numéro publié par le développeur du logiciel. La distribution peut appliquer des correctifs sans changer la version amont de la façon attendue.

## 2.4. Les architectures

Un paquet peut être destiné à une architecture particulière.

Exemples courants :

- `amd64` : architecture x86-64 dans la nomenclature Debian ;
- `arm64` : architecture ARM 64 bits dans la nomenclature Debian ;
- `x86_64` : nom courant de l'architecture x86-64 dans de nombreux outils RPM ;
- `aarch64` : nom courant de l'architecture ARM 64 bits dans de nombreux outils RPM.

Les noms ne sont pas nécessairement identiques d'une famille à l'autre.

Pour afficher l'architecture de ta machine :

```bash
dpkg --print-architecture
```

Cette commande est destinée aux systèmes utilisant `dpkg`.

Pour afficher les informations matérielles générales :

```bash
uname -m
```

Les deux résultats n'expriment pas exactement la même chose. `uname -m` décrit l'architecture exposée par le noyau, tandis que la commande de `dpkg` indique l'architecture principale de la base de paquets Debian.

## 2.5. Un paquet est différent d'un programme en cours d'exécution

Installer un paquet ne signifie pas toujours que l'application démarre immédiatement.

Prenons un serveur Web :

```text
PAQUET INSTALLÉ
       |
       v
FICHIERS INSTALLÉS
       |
       v
CONFIGURATION PRÉSENTE
       |
       v
SERVICE ÉVENTUELLEMENT DÉMARRÉ
       |
       v
APPLICATION À VÉRIFIER
```

Le résultat dépend du paquet, de ses scripts de maintenance, des politiques de la distribution et de la configuration du service.

Un paquet peut être correctement installé alors que son application n'est pas démarrée ou ne répond pas.

Il faut donc différencier :

- le paquet installé ;
- le programme présent sur le disque ;
- le service configuré ;
- le service actif ;
- l'application fonctionnelle.


# 3. Pourquoi utiliser un gestionnaire de paquets ?

## 3.1. Installation manuelle et gestionnaire de paquets

Supposons que tu souhaites installer un logiciel téléchargé sous forme d'archive.

Une installation manuelle peut demander :

- de décompresser les fichiers ;
- de placer les exécutables ;
- de créer les répertoires nécessaires ;
- de gérer les bibliothèques ;
- de configurer les permissions ;
- de préparer les services ;
- d'organiser les mises à jour ;
- de conserver la liste des fichiers installés.

Le gestionnaire de paquets centralise une grande partie de ces opérations.

## 3.2. Les principales fonctions

Un gestionnaire de paquets peut notamment :

- rechercher des paquets ;
- afficher leur description ;
- installer les fichiers nécessaires ;
- résoudre des dépendances ;
- vérifier certaines contraintes de version ;
- enregistrer l'état de l'installation ;
- appliquer des mises à jour ;
- supprimer des paquets ;
- identifier des fichiers appartenant à un paquet ;
- vérifier certains attributs des fichiers installés.

Ses capacités exactes dépendent de la famille de paquets et de l'outil utilisé.

## 3.3. La base locale de paquets

Le gestionnaire maintient des informations sur les paquets connus et leur état.

Sur Debian et Ubuntu, les outils `dpkg` et APT reposent notamment sur une base locale de paquets installés et sur des index provenant des dépôts.

Ces informations ne sont pas la même chose que les fichiers présents dans les répertoires du système.

Un fichier peut avoir été modifié manuellement sans que la base de paquets reflète cette modification comme un nouvel état déclaré.

C'est pourquoi il est important d'utiliser les outils de vérification appropriés après un incident.


# 4. Les principales familles de distributions Linux

## 4.1. Pourquoi les commandes diffèrent-elles ?

Toutes les distributions Linux ne partagent pas le même système de paquets.

Certaines utilisent le format DEB et les outils `dpkg`/APT.

D'autres utilisent le format RPM et des outils comme `rpm` avec un gestionnaire de dépôts tel que DNF.

Arch Linux utilise principalement le format de paquet géré par `pacman`.

Les concepts généraux sont proches, mais les commandes et les fichiers de configuration diffèrent.

## 4.2. Comparaison générale

| Famille | Exemples | Outil de haut niveau courant | Outil de bas niveau |
|---|---|---|---|
| Debian | Debian | `apt` | `dpkg` |
| Ubuntu | Ubuntu, Linux Mint dans sa base Ubuntu | `apt` | `dpkg` |
| Fedora | Fedora | `dnf` | `rpm` |
| RHEL et distributions compatibles | RHEL, Rocky Linux, AlmaLinux | `dnf` sur les versions modernes concernées | `rpm` |
| Arch Linux | Arch Linux | `pacman` | Mécanismes propres à pacman |

Des distributions immuables ou orientées images peuvent adopter d'autres mécanismes. Fedora, par exemple, possède aussi des variantes utilisant `rpm-ostree`. Le gestionnaire adapté dépend donc de l'édition installée.

## 4.3. Pourquoi APT et dpkg sont-ils souvent utilisés ensemble ?

Sur Debian et Ubuntu :

- `dpkg` gère les opérations de bas niveau sur les paquets DEB ;
- APT résout les dépendances à partir des index des dépôts et organise les installations et mises à jour.

```text
ADMINISTRATEUR
      |
      v
      APT
      |
      +-- Recherche
      +-- Dépôts
      +-- Résolution des dépendances
      +-- Téléchargement
      |
      v
     DPKG
      |
      +-- Dépaquetage
      +-- Installation des fichiers
      +-- Configuration du paquet
      |
      v
SYSTÈME DE FICHIERS ET BASE LOCALE
```

Cette organisation explique pourquoi APT est généralement préférable à une suite de commandes `dpkg` manuelles lorsqu'il faut installer ou supprimer des logiciels avec leurs dépendances.

## 4.4. Quand faut-il utiliser ces outils ?

Sur Debian ou Ubuntu, commence généralement avec APT pour les opérations habituelles.

Utilise `dpkg` lorsque tu dois examiner un paquet local ou consulter précisément la base locale, ou encore diagnostiquer un état de paquet.

Sur Fedora ou RHEL, utilise généralement DNF pour les opérations reposant sur les dépôts, et RPM pour les consultations ou vérifications de bas niveau.

Ne copie pas une commande `apt` sur Fedora ou une commande `dnf` sur Ubuntu en supposant qu'elle fonctionnera.


# 5. Comprendre les dépôts logiciels

## 5.1. Qu'est-ce qu'un dépôt ?

Un dépôt logiciel est une source organisée de paquets et de métadonnées.

Il permet au gestionnaire de paquets de connaître les versions disponibles, leurs informations et, selon le système, les fichiers nécessaires au téléchargement.

Un dépôt peut être fourni par :

- la distribution ;
- un éditeur logiciel ;
- une organisation ;
- un projet tiers ;
- une entreprise qui héberge ses propres logiciels.

## 5.2. Comment fonctionne un dépôt ?

```text
ADMINISTRATEUR
      |
      v
GESTIONNAIRE DE PAQUETS
      |
      v
INDEX LOCAL DES PAQUETS
      ^
      |
MISE À JOUR DES MÉTADONNÉES
      ^
      |
      v
DÉPÔTS CONFIGURÉS
      |
      v
PAQUETS DISPONIBLES
      |
      v
TÉLÉCHARGEMENT ET INSTALLATION
```

Le schéma représente le principe général.

Le gestionnaire utilise les informations des dépôts configurés afin de sélectionner des paquets et de résoudre les dépendances.

## 5.3. Les dépôts officiels

Les dépôts officiels d'une distribution sont généralement la source recommandée pour installer les logiciels disponibles dans cette distribution.

Ils peuvent fournir :

- des versions adaptées à la distribution ;
- des mises à jour de sécurité ;
- des paquets compatibles avec les dépendances disponibles ;
- des métadonnées signées ou protégées par un mécanisme de confiance.

Cela ne signifie pas que tout paquet officiel convient à tous les usages. Il faut aussi tenir compte de la version de la distribution, de son cycle de maintenance et du rôle du serveur.

## 5.4. Les dépôts tiers

Un dépôt tiers est géré en dehors des dépôts standards de la distribution.

Il peut être utile lorsqu'un éditeur fournit sa propre version d'un logiciel.

Cependant, il introduit une relation de confiance supplémentaire.

Un dépôt tiers peut :

- fournir des versions différentes ;
- remplacer certaines dépendances ;
- entrer en conflit avec des paquets existants ;
- appliquer une politique de mise à jour différente ;
- affecter la stabilité si les paquets ne sont pas adaptés à la distribution.

Avant d'ajouter un dépôt, vérifie son propriétaire, son origine, sa documentation, ses clés de signature, sa compatibilité et les conséquences des mises à jour futures.


# 6. Découvrir APT et dpkg

## 6.1. APT

APT signifie **Advanced Package Tool**.

C'est une famille d'outils utilisée pour gérer les paquets dans les distributions Debian et leurs dérivées.

La commande interactive courante est :

```bash
apt
```

Elle permet notamment de rechercher, d'installer, de mettre à jour et de supprimer des paquets.

## 6.2. dpkg

`dpkg` est l'outil de bas niveau qui gère les paquets Debian.

Exemple :

```bash
dpkg --version
```

Cette commande affiche la version de `dpkg`.

Pour obtenir de l'aide :

```bash
dpkg --help
```

`dpkg` peut installer un paquet DEB local, mais il ne fournit pas à lui seul toutes les fonctions de résolution des dépendances depuis les dépôts dont dispose APT.

## 6.3. apt, apt-get et apt-cache

Ces commandes sont liées, mais leurs usages privilégiés diffèrent.

| Outil | Usage habituel |
|---|---|
| `apt` | Gestion interactive courante des paquets |
| `apt-get` | Commandes adaptées aux opérations automatisées classiques |
| `apt-cache` | Consultation et recherche d'informations dans les index locaux |

Pour administrer un système depuis un terminal, `apt` est généralement pratique.

Pour des scripts, `apt-get` est préférable dans les scénarios classiques d'automatisation, notamment parce que l'interface et les messages de `apt` sont orientés vers l'utilisation interactive.

Pour la consultation des index, `apt-cache` reste utile.


# 7. Identifier le système et les outils disponibles

## 7.1. Identifier la distribution

Avant toute opération, exécute :

```bash
cat /etc/os-release
```

Ce fichier contient des informations sur la distribution, notamment son nom et son identifiant.

La sortie peut ressembler à :

```text
NAME="Ubuntu"
VERSION="..."
ID=ubuntu
ID_LIKE=debian
```

Cet exemple est illustratif.

## 7.2. Identifier le noyau

```bash
uname -r
```

Cette commande affiche la version du noyau en cours d'utilisation.

La version du noyau et la version de la distribution sont deux informations distinctes.

## 7.3. Identifier l'architecture

Sur un système Debian ou Ubuntu :

```bash
dpkg --print-architecture
```

Autre commande :

```bash
uname -m
```

Compare les résultats pour distinguer l'architecture du système de gestion des paquets et celle que le noyau expose.

## 7.4. Vérifier la présence de commandes

```bash
command -v apt
```

```bash
command -v dpkg
```

Sur une distribution utilisant DNF :

```bash
command -v dnf
```

La commande `command -v` indique si un programme ou une commande connue du shell peut être trouvé.

Une commande absente ne signifie pas automatiquement que le système est cassé : elle peut simplement ne pas être utilisée sur cette distribution ou ne pas être installée.


# 8. Rechercher un paquet

## 8.1. Pourquoi faut-il rechercher avant d'installer ?

Le nom d'un logiciel et le nom de son paquet ne sont pas toujours identiques.

Une application peut avoir plusieurs paquets :

- un paquet principal ;
- un paquet contenant les outils auxiliaires ;
- un paquet de documentation ;
- un paquet réservé au développement ;
- un paquet de bibliothèques.

La recherche permet d'identifier le bon paquet avant l'installation.

## 8.2. Rechercher avec APT

Exemple :

```bash
apt search htop
```

Cette commande recherche des correspondances dans les index disponibles localement.

Les résultats dépendent des dépôts configurés et de la fraîcheur des index locaux.

Pour obtenir des résultats récents, il faut généralement actualiser l'index avant la recherche.

## 8.3. Rechercher avec `apt-cache`

```bash
apt-cache search htop
```

Cette commande recherche les paquets connus dans les index locaux d'APT.

Elle est pratique dans les scripts et les procédures d'administration.

## 8.4. Filtrer une recherche

```bash
apt-cache search 'serveur web'
```

La recherche porte sur les champs indexés, notamment les noms et descriptions de paquets selon les métadonnées disponibles.

Il ne s'agit pas d'un moteur de recherche général sur Internet.

## 8.5. Rechercher un outil à partir de son nom

Supposons que tu souhaites installer un outil de supervision de processus.

Tu peux commencer par :

```bash
apt-cache search htop
```

Examine ensuite le nom exact du paquet et sa description.

Ne choisis pas automatiquement le premier résultat : plusieurs paquets peuvent avoir des noms proches ou des fonctions différentes.

## 8.6. Rechercher un fichier fourni par un paquet

Sur Debian et Ubuntu, une fois qu'un paquet est installé, `dpkg -S` peut aider à identifier le paquet propriétaire d'un fichier.

Exemple :

```bash
dpkg -S /usr/bin/apt
```

Le résultat dépend du système, du chemin et de la base locale.

Si tu cherches un fichier qui n'existe pas encore parce que le paquet n'est pas installé, il faut utiliser les outils de recherche de fichiers dans les index de paquets disponibles, lorsque la distribution les fournit.


# 9. Consulter les informations d'un paquet

## 9.1. La commande `apt show`

```bash
apt show htop
```

La commande affiche les informations disponibles sur le paquet sélectionné.

Selon les index et la version, tu peux notamment y trouver :

- le nom ;
- la version ;
- l'architecture ;
- la taille estimée ;
- la description ;
- les dépendances ;
- la source du paquet.

Les informations portent sur le paquet sélectionné dans les index, qui peut être une version disponible et non exactement la version installée.

## 9.2. Consulter avec `apt-cache show`

```bash
apt-cache show htop
```

Cette commande affiche les métadonnées disponibles dans les index APT.

Plusieurs versions ou variantes peuvent apparaître selon la configuration.

## 9.3. Consulter les versions disponibles et leur origine

```bash
apt-cache policy htop
```

Cette commande aide à examiner les versions connues et les priorités des sources configurées.

Elle est particulièrement utile lorsque plusieurs dépôts fournissent un même paquet.

Il faut comprendre qu'une version candidate peut changer en fonction de l'état des index, des priorités APT et de la configuration du système.

## 9.4. Informations d'un paquet déjà installé

```bash
dpkg-query -W htop
```

Cette commande interroge la base locale de paquets.

Pour demander un format simple :

```bash
dpkg-query -W -f='${Package} ${Version} ${Architecture}\n' htop
```

Si le paquet n'est pas connu comme installé, la commande peut retourner une erreur ou ne pas fournir le résultat attendu.

Pour une vérification plus précise de l'état d'installation :

```bash
dpkg -s htop
```

Le champ `Status` permet d'identifier l'état que `dpkg` enregistre pour le paquet.

## 9.5. Différence entre disponible et installé

Un paquet disponible dans un dépôt n'est pas nécessairement installé.

Un paquet installé n'est pas nécessairement à la dernière version disponible.

```text
PAQUET DISPONIBLE DANS UN DÉPÔT
             |
             v
         RECHERCHE
             |
             v
PAQUET NON INSTALLÉ
             |
             v
INSTALLATION
             |
             v
PAQUET ENREGISTRÉ COMME INSTALLÉ
             |
             v
NOUVELLE VERSION DISPONIBLE
             |
             v
MISE À JOUR ÉVENTUELLE
```

Cette distinction explique pourquoi il faut vérifier l'état du paquet avant et après une opération.


# 10. Installer un paquet avec APT

## 10.1. La commande de base

La forme générale est :

```bash
sudo apt install nom-du-paquet
```

Par exemple :

```bash
sudo apt install htop
```

Cette commande demande à APT d'installer le paquet `htop`, s'il est disponible et si les dépendances peuvent être résolues.

Le mot `sudo` permet d'exécuter la commande avec les privilèges nécessaires, selon la configuration de l'utilisateur.

## 10.2. Que fait APT pendant l'installation ?

L'opération peut comprendre :

1. la consultation des index disponibles ;
2. la sélection d'une version ;
3. la résolution des dépendances ;
4. le téléchargement des archives nécessaires ;
5. la vérification des éléments de confiance et d'intégrité prévus par le système ;
6. le dépaquetage et l'installation ;
7. la configuration des paquets ;
8. l'exécution des scripts de maintenance prévus ;
9. la mise à jour de la base locale.

Les étapes réelles dépendent de la situation : certaines dépendances peuvent déjà être installées, certains paquets peuvent être déjà présents, et certaines opérations peuvent demander une intervention.

## 10.3. Installer plusieurs paquets

```bash
sudo apt install htop curl
```

APT examine les paquets demandés et les dépendances nécessaires.

L'installation de plusieurs paquets dans une seule transaction peut simplifier l'administration, mais il faut lire le résumé avant de confirmer.

## 10.4. Examiner les changements avant de confirmer

Avant de valider une opération, lis le résumé présenté par APT.

Examine notamment :

- les paquets qui seront installés ;
- ceux qui seront mis à jour ;
- ceux qui seront supprimés ;
- la quantité de données à télécharger ;
- l'espace disque nécessaire.

Si une installation propose la suppression d'un composant important, annule l'opération et examine pourquoi le solveur prend cette décision.

Ne confirme jamais automatiquement toutes les opérations sans avoir compris les changements annoncés.

## 10.5. Prévisualiser une installation

Sur Debian et Ubuntu :

```bash
apt-get -s install htop
```

L'option `-s` effectue une simulation.

Elle permet d'examiner les changements prévus sans effectuer l'installation habituelle.

La simulation ne constitue pas une garantie absolue : l'état des index, les paquets réellement présents, les scripts d'installation et d'autres conditions peuvent différer au moment de l'opération réelle.

## 10.6. Vérifier après l'installation

Vérifie l'état du paquet :

```bash
dpkg -s htop
```

Puis recherche la commande :

```bash
command -v htop
```

Si le programme est disponible dans le `PATH`, sa commande peut être lancée :

```bash
htop
```

Cette vérification permet de distinguer l'état du paquet de la disponibilité de la commande.

Un paquet peut être correctement installé sans fournir un exécutable portant exactement le nom attendu.


# 11. Comprendre les dépendances

## 11.1. Qu'est-ce qu'une dépendance ?

Une dépendance est un composant nécessaire ou utile au fonctionnement, à la construction ou à une étape d'installation d'un logiciel, selon la nature de la dépendance déclarée.

Exemple conceptuel :

```text
APPLICATION
    |
    +-- dépend de bibliothèque A
    |
    +-- dépend de bibliothèque B
              |
              +-- dépend de bibliothèque C
```

Installer manuellement uniquement l'application principale pourrait ne pas suffire si ses dépendances sont absentes.

Le gestionnaire utilise les métadonnées des paquets pour identifier les composants requis.

## 11.2. Les catégories de dépendances

Le format de paquetage distingue plusieurs types de relations, selon les outils et les métadonnées.

Dans Debian, les relations usuelles comprennent notamment :

- `Depends` : dépendances nécessaires selon les règles du paquet ;
- `Pre-Depends` : dépendances qui doivent être configurées avant certaines étapes ;
- `Recommends` : paquets recommandés pour une installation habituelle ;
- `Suggests` : logiciels suggérés qui ne sont généralement pas indispensables ;
- `Conflicts` : paquets incompatibles selon la relation déclarée ;
- `Breaks` : relation exprimant certaines incompatibilités ;
- `Provides` : capacités ou noms virtuels fournis par un paquet.

Il n'est pas nécessaire de mémoriser tous les détails à ce niveau, mais il faut comprendre que les dépendances ne se résument pas à une simple liste de noms.

## 11.3. Pourquoi certaines installations ajoutent-elles plusieurs paquets ?

Supposons qu'un outil demande une bibliothèque qui n'est pas encore installée.

```text
INSTALLATION DEMANDÉE
        |
        v
   outil-reseau
        |
        v
Dépend de bibliothèque-réseau
        |
        v
Bibliothèque-réseau absente
        |
        v
APT prévoit deux installations
```

Le gestionnaire peut proposer l'installation de l'outil et de plusieurs dépendances.

C'est un comportement normal lorsque les paquets peuvent être résolus.

## 11.4. Examiner les dépendances avec `apt-cache`

```bash
apt-cache depends htop
```

Cette commande affiche les relations de dépendance connues dans les index pour le paquet.

Pour consulter les relations inversement déclarées, c'est-à-dire les paquets dépendant d'un autre paquet, tu peux utiliser :

```bash
apt-cache rdepends nom-du-paquet
```

Cette sortie peut être volumineuse. Elle doit être interprétée en tenant compte des relations déclarées et du contexte des paquets.

## 11.5. Pourquoi ne pas installer les dépendances à la main ?

Si tu installes séparément chaque fichier nécessaire, tu dois toi-même résoudre :

- la compatibilité des versions ;
- les dépendances transitives ;
- les conflits ;
- l'architecture ;
- l'ordre de configuration ;
- le suivi des versions ultérieures.

APT est conçu pour gérer une grande partie de ces tâches à partir des métadonnées disponibles.

Il est généralement préférable de lui confier les opérations ordinaires d'installation et de suppression.

## 11.6. Dépendance déclarée et dépendance réelle

Les métadonnées de paquet décrivent les relations prévues par le mainteneur.

Une application peut aussi dépendre d'un service externe, d'un fichier de configuration ou d'une ressource non représentée comme une dépendance logicielle classique.

Par exemple, installer un serveur Web ne garantit pas qu'un site Web soit configuré, que son nom DNS existe ou qu'un pare-feu autorise le trafic.

La gestion des paquets couvre l'installation du logiciel, pas tous les aspects de sa mise en service.


# 12. Mettre à jour la liste des paquets et les logiciels installés

## 12.1. Les deux opérations sont différentes

Sous Debian et Ubuntu, la commande :

```bash
sudo apt update
```

actualise les index des dépôts configurés.

Elle ne met pas directement à niveau tous les logiciels installés.

La commande :

```bash
sudo apt upgrade
```

demande la mise à niveau des paquets installés dans les conditions autorisées par cette opération.

Ces deux commandes ont des objectifs différents.

## 12.2. Comment fonctionne `apt update` ?

Le gestionnaire télécharge les métadonnées des dépôts configurés et actualise les informations locales des paquets disponibles.

```text
DÉPÔTS CONFIGURÉS
       |
       v
sudo apt update
       |
       v
INDEX LOCAUX ACTUALISÉS
       |
       v
APT CONNAÎT LES VERSIONS DISPONIBLES
```

L'index local sert ensuite à déterminer quelles versions sont disponibles, quels paquets existent et quelles relations sont déclarées.

Si les index sont anciens, APT peut ne pas connaître les versions ou les métadonnées les plus récentes du dépôt.

## 12.3. Comment fonctionne `apt upgrade` ?

Après actualisation de l'index :

```bash
sudo apt upgrade
```

APT examine les paquets installés et met à niveau ceux qui peuvent être mis à jour dans les conditions de cette opération.

L'objectif est d'éviter certaines suppressions de paquets installés qui seraient nécessaires pour effectuer une mise à niveau plus complexe.

Le résumé doit toujours être lu avant confirmation.

## 12.4. La commande complète habituelle

Une séquence courante est :

```bash
sudo apt update
sudo apt upgrade
```

Il est possible d'utiliser les deux commandes l'une après l'autre, mais il faut bien comprendre qu'elles réalisent deux opérations distinctes.

La première actualise les index.

La seconde examine puis applique les mises à niveau autorisées par la commande.

## 12.5. Examiner les mises à jour disponibles

```bash
apt list --upgradable
```

Cette commande affiche les paquets pour lesquels des mises à jour sont proposées par les index locaux.

Une liste vide ne signifie pas qu'il n'existe aucune vulnérabilité dans les applications utilisées. Elle indique uniquement qu'aucune mise à niveau correspondante n'est proposée dans le contexte courant des index et de la configuration.

## 12.6. Que fait `full-upgrade` ?

```bash
sudo apt full-upgrade
```

Cette commande peut résoudre des changements de dépendances plus complexes que `apt upgrade`, notamment en installant ou en supprimant des paquets si cela est nécessaire pour terminer la mise à niveau.

C'est pourquoi il faut examiner attentivement le plan proposé avant confirmation.

Sur un serveur, une suppression inattendue d'un composant essentiel peut interrompre un service ou modifier sensiblement le système.

Ne lance pas `full-upgrade` de manière automatique sans examiner le résultat proposé.

## 12.7. Mises à niveau de distribution

Une mise à niveau de distribution, par exemple le passage d'une version majeure d'Ubuntu à une autre, est différente de la simple mise à jour des paquets d'une version existante.

Elle peut modifier de nombreux composants, les dépôts et les dépendances.

Il faut suivre la procédure officielle de mise à niveau de la distribution concernée, préparer une sauvegarde et vérifier les contraintes de compatibilité.

Ne confonds pas une mise à jour ordinaire avec une migration entre versions de système.


# 13. Comprendre les mises à jour de sécurité

## 13.1. Pourquoi mettre à jour ?

Les mises à jour peuvent apporter :

- des correctifs de sécurité ;
- des corrections de bugs ;
- des améliorations de compatibilité ;
- des adaptations aux bibliothèques ;
- des changements fonctionnels ;
- des modifications de performance.

Un système non mis à jour peut conserver des vulnérabilités corrigées dans des versions plus récentes.

## 13.2. Une mise à jour ne garantit pas l'absence de vulnérabilité

Un paquet à jour par rapport aux dépôts configurés n'est pas automatiquement exempt de vulnérabilités.

La sécurité dépend notamment :

- de la version de distribution ;
- du cycle de maintenance ;
- de la source du paquet ;
- des correctifs disponibles ;
- de la configuration de l'application ;
- de l'exposition du service ;
- du respect des recommandations de sécurité pertinentes.

Il faut connaître le statut de maintenance de la distribution et appliquer les correctifs fournis par les sources fiables correspondantes.

## 13.3. Pourquoi une version peut-elle sembler ancienne ?

Certaines distributions maintiennent une version stable d'un logiciel et y appliquent des correctifs.

La version amont affichée ne suffit donc pas toujours à déterminer si un correctif de sécurité est présent.

Pour les décisions de sécurité, consulte les avis officiels de la distribution et les informations de paquet plutôt que de comparer uniquement le numéro de version à celui du site du développeur.

## 13.4. Vérifier le fonctionnement après une mise à jour

Après une mise à niveau importante, vérifie les composants essentiels.

Exemples :

```bash
systemctl --failed
```

Cette commande liste les unités en échec dans un système utilisant `systemd`.

Pour un service précis :

```bash
systemctl status nom.service
```

Puis, si nécessaire :

```bash
journalctl -u nom.service -n 100 --no-pager
```

Les vérifications doivent correspondre aux services réellement utilisés sur la machine.

## 13.5. Les redémarrages

Certaines mises à jour nécessitent un redémarrage, d'autres peuvent simplement nécessiter un rechargement ou un redémarrage d'un service.

Les conséquences dépendent du type de composant et des mécanismes de gestion de l'application.

Un administrateur doit suivre les recommandations de la distribution et de l'application au lieu de supposer que chaque mise à jour nécessite un redémarrage complet.


# 14. Supprimer un paquet proprement

## 14.1. Supprimer un paquet avec APT

La commande générale est :

```bash
sudo apt remove nom-du-paquet
```

Par exemple :

```bash
sudo apt remove htop
```

Cette commande demande la suppression du paquet.

APT peut également proposer la suppression de certains composants devenus inutiles selon ses règles de résolution des dépendances.

Lis attentivement la liste des opérations avant de confirmer.

## 14.2. `remove` et `purge`

Ces deux commandes n'ont pas le même objectif.

```bash
sudo apt remove nom-du-paquet
```

Demande la suppression du paquet en conservant généralement certains fichiers de configuration gérés comme tels par le paquet.

```bash
sudo apt purge nom-du-paquet
```

Demande aussi la suppression des fichiers de configuration gérés par le paquet, selon les règles de Debian.

**Attention :** `purge` ne supprime pas nécessairement toutes les données produites par l'application. Les fichiers utilisateur, les données de service et les données stockées en dehors des fichiers de configuration gérés par le paquet peuvent rester présents.

Avant une suppression définitive, vérifie les chemins et les données à conserver.

## 14.3. Pourquoi ne pas supprimer un fichier à la main ?

Supposons que tu veuilles supprimer un outil installé par APT.

Supprimer manuellement son exécutable avec `rm` ne retire pas nécessairement l'enregistrement du paquet dans la base locale.

Le gestionnaire peut toujours considérer le paquet comme installé.

Cela peut provoquer une différence entre la base de paquets et l'état réel des fichiers.

Il est généralement préférable d'utiliser APT pour supprimer le logiciel, plutôt que de retirer arbitrairement ses fichiers un par un.

## 14.4. Consulter les dépendances avant de supprimer

Pour examiner les dépendances déclarées d'un paquet :

```bash
apt-cache depends nom-du-paquet
```

Pour rechercher les paquets déclarant une dépendance inverse :

```bash
apt-cache rdepends nom-du-paquet
```

Ces commandes donnent des informations utiles, mais ne remplacent pas le plan de suppression réel présenté par APT.

## 14.5. Simuler une suppression

```bash
apt-get -s remove nom-du-paquet
```

Cette simulation permet d'examiner les changements envisagés sans effectuer l'opération habituelle de suppression.

Si des services ou des bibliothèques importantes figurent dans le plan de suppression, arrête-toi et examine la situation avant d'effectuer l'opération réelle.


# 15. Nettoyer les dépendances inutilisées

## 15.1. Pourquoi des paquets restent-ils après une suppression ?

Une application installée peut avoir entraîné l'installation de plusieurs dépendances.

Après sa suppression, certaines dépendances peuvent ne plus être nécessaires.

Le gestionnaire peut enregistrer les paquets considérés comme automatiquement installés pour satisfaire des dépendances.

Il peut ensuite proposer de supprimer les paquets automatiquement installés qui ne sont plus requis.

## 15.2. La commande `autoremove`

```bash
sudo apt autoremove
```

Cette commande demande la suppression des paquets considérés comme automatiquement installés et désormais inutiles selon l'analyse d'APT.

Il ne faut pas traiter ce nettoyage comme une opération aveugle.

Examine toujours la liste affichée avant de confirmer.

Certaines applications peuvent avoir été installées pour un usage particulier sans que cet usage soit représenté dans les dépendances d'autres paquets.

## 15.3. Pourquoi vérifier avant de confirmer ?

Supposons qu'une bibliothèque ait été installée automatiquement.

Un administrateur peut toutefois avoir besoin de cette bibliothèque pour une opération locale spécifique, même si aucune dépendance installée ne la réclame.

La commande de nettoyage ne connaît pas nécessairement toutes les intentions de l'administrateur.

Il faut donc contrôler la liste proposée et conserver les paquets nécessaires à l'exploitation.

## 15.4. La commande `clean`

```bash
sudo apt clean
```

Cette commande supprime les fichiers d'archives téléchargés mis en cache par APT.

Elle ne supprime pas les paquets actuellement installés.

Le nettoyage du cache réduit l'espace occupé par les archives téléchargées, mais peut nécessiter de nouveaux téléchargements lors de prochaines installations.

## 15.5. La commande `autoclean`

```bash
sudo apt autoclean
```

Cette commande nettoie des archives téléchargées qui ne peuvent généralement plus être récupérées depuis les sources configurées, selon la logique d'APT.

Elle diffère de `clean`, qui supprime les archives en cache plus largement.

## 15.6. Les trois commandes à distinguer

| Commande | Rôle |
|---|---|
| `apt autoremove` | Proposer la suppression de dépendances devenues inutiles |
| `apt clean` | Supprimer les archives de paquets téléchargées dans le cache |
| `apt autoclean` | Nettoyer certaines archives obsolètes du cache |

Aucune de ces opérations ne doit être confondue avec la suppression complète de données d'application.


# 16. Lister les paquets et vérifier leur état

## 16.1. Lister les paquets installés

```bash
apt list --installed
```

Cette commande peut produire une grande quantité de résultats.

Pour interroger la base locale :

```bash
dpkg-query -W
```

Les résultats dépendent du format et des paquets connus de la base locale.

## 16.2. Vérifier un paquet précis

```bash
dpkg -s htop
```

Cette commande affiche les informations d'état du paquet si celui-ci est connu.

Pour rechercher une correspondance dans la liste des paquets :

```bash
dpkg -l 'htop*'
```

Les caractères génériques doivent être cités lorsque c'est nécessaire, afin d'éviter une expansion inattendue par le shell.

## 16.3. Comprendre le statut affiché par `dpkg -l`

La sortie de `dpkg -l` commence par des colonnes de statut.

Dans une installation normale et entièrement configurée, un paquet installé peut apparaître avec un indicateur de ce type :

```text
ii  htop  ...  amd64  ...
```

Les lettres représentent l'action souhaitée et l'état du paquet, et une autre colonne peut signaler des erreurs.

Les états complets sont plus nombreux que les deux lettres de cet exemple. Pour comprendre une situation particulière, consulte :

```bash
man dpkg
```

ou :

```bash
man dpkg-query
```

Ne traite pas un paquet marqué dans un état intermédiaire comme si son installation était nécessairement complète.

## 16.4. Afficher la version d'un paquet installé

```bash
dpkg-query -W -f='${Version}\n' htop
```

Cette commande affiche la version enregistrée dans la base locale si le paquet est connu dans l'état attendu.

Il peut être utile d'enregistrer cette information lors d'un diagnostic ou avant une opération de maintenance.

## 16.5. Identifier les paquets retenus

Dans les systèmes Debian ou Ubuntu :

```bash
apt-mark showhold
```

Cette commande affiche les paquets marqués comme retenus.

Un paquet retenu peut ne pas suivre les mises à niveau habituelles de la manière attendue.

Si une mise à jour n'apparaît pas comme prévu, il est donc utile de vérifier les éventuelles retenues et les priorités configurées.

## 16.6. Comparer version installée et version candidate

```bash
apt-cache policy htop
```

Cette commande aide à examiner les versions disponibles et la version candidate.

Pour connaître la version installée, consulte également la base locale :

```bash
dpkg-query -W -f='${Package} ${Version}\n' htop
```

Les deux commandes répondent à des questions différentes.

La première décrit les informations disponibles pour le choix d'une version. La seconde interroge la base locale du système.


# 17. Identifier les fichiers installés par un paquet

## 17.1. Pourquoi cette compétence est-elle utile ?

Lorsqu'un logiciel est installé, l'administrateur doit parfois savoir :

- où se trouve son exécutable ;
- quels fichiers de configuration il fournit ;
- où sont placées ses documentations ;
- quels répertoires peuvent contenir des données ;
- quel paquet est propriétaire d'un fichier suspect.

Ces informations sont utiles pour le dépannage, la sauvegarde et la compréhension d'un logiciel.

## 17.2. Lister les fichiers avec `dpkg -L`

```bash
dpkg -L htop
```

Cette commande liste les chemins enregistrés dans la base locale pour le paquet.

Le résultat peut inclure des fichiers et des répertoires de différentes catégories.

## 17.3. Trouver le paquet propriétaire d'un fichier

```bash
dpkg -S /usr/bin/apt
```

Cette commande cherche le paquet auquel la base associe le chemin.

Elle peut échouer si le fichier n'est pas géré par un paquet connu, si le chemin n'est pas exact ou si le fichier est issu d'un processus de génération ou d'installation hors gestionnaire.

## 17.4. Lister les fichiers de configuration

Le mécanisme de gestion des configurations n'est pas une simple garantie que tous les fichiers de configuration de l'application seront identifiés par une seule commande.

On peut toutefois consulter les informations propres aux fichiers de configuration enregistrés par `dpkg` avec :

```bash
dpkg-query -W -f='${Conffiles}\n' nom-du-paquet
```

Remplace le nom par celui du paquet concerné.

Les fichiers générés manuellement, les données utilisateur et les fichiers créés pendant l'exploitation peuvent ne pas être inclus dans cette liste.

## 17.5. Fichiers du paquet et données applicatives

Il faut distinguer :

- les fichiers fournis par le paquet ;
- les fichiers de configuration gérés par le paquet ;
- les fichiers générés à l'exécution ;
- les données de l'application ;
- les fichiers créés manuellement par un administrateur ;
- les journaux et archives.

Supprimer un paquet ne signifie pas nécessairement supprimer toutes les données associées.

Cette distinction est particulièrement importante pour les bases de données et les services de production.


# 18. Installer un paquet local

## 18.1. Qu'est-ce qu'un paquet local ?

Un paquet local est un fichier de paquetage déjà présent sur la machine.

Sur Debian et Ubuntu, il peut prendre la forme d'un fichier `.deb`.

Sur les systèmes RPM, il peut s'agir d'un fichier `.rpm`.

Installer un fichier local est différent de demander à rechercher un paquet par son nom dans les dépôts.

## 18.2. Installer un fichier DEB avec APT

Si tu disposes d'un fichier DEB téléchargé depuis une source fiable, la commande suivante est généralement préférable pour une installation locale :

```bash
sudo apt install ./nom-du-paquet.deb
```

Le préfixe `./` indique un chemin relatif, si le fichier se trouve dans le répertoire courant.

APT peut alors prendre en charge la résolution des dépendances à partir des sources configurées.

## 18.3. Installer avec `dpkg -i`

La commande de bas niveau est :

```bash
sudo dpkg -i nom-du-paquet.deb
```

`dpkg` installe le paquet local, mais ne résout pas automatiquement toutes les dépendances à partir des dépôts de la même façon qu'APT.

Si des dépendances sont absentes, le paquet peut rester dans un état incomplètement configuré.

C'est pourquoi APT est généralement plus adapté à l'installation habituelle des paquets depuis les dépôts ou pour l'installation locale lorsqu'il peut résoudre les dépendances.

## 18.4. Vérifier avant d'installer

Avant d'installer un paquet téléchargé :

1. identifie son origine ;
2. vérifie le site ou l'éditeur ;
3. confirme que le paquet correspond à la distribution ;
4. vérifie l'architecture ;
5. contrôle les signatures ou mécanismes de vérification fournis ;
6. examine les dépendances ;
7. lis les changements proposés ;
8. installe uniquement si la source est digne de confiance.

Le fait qu'un fichier porte l'extension `.deb` ne garantit pas qu'il est sûr.

## 18.5. Pourquoi éviter `dpkg --force-*` ?

`dpkg` fournit des options de forçage dans certaines situations.

Elles peuvent permettre de contourner des vérifications ou des contraintes, mais risquent de placer le système dans un état incohérent.

Un débutant ne doit pas utiliser des options de forçage comme solution habituelle à un problème de dépendances.

Il faut d'abord comprendre l'erreur, vérifier la compatibilité du paquet et utiliser le mécanisme normal de résolution.


# 19. Comprendre les dépôts et leur configuration

## 19.1. Où sont configurées les sources APT ?

Sur Debian et Ubuntu, les sources APT se trouvent couramment dans :

```text
/etc/apt/sources.list
/etc/apt/sources.list.d/
```

Les configurations exactes dépendent de la version de la distribution.

Sur les versions récentes d'Ubuntu, les sources peuvent être déclarées dans des fichiers au format deb822, notamment dans :

```text
/etc/apt/sources.list.d/ubuntu.sources
```

Il faut examiner la configuration réellement présente au lieu de supposer qu'un seul fichier contient toutes les sources.

## 19.2. Exemple conceptuel de source

Une entrée de source peut décrire :

```text
Type de paquets
Adresse du dépôt
Version ou suite de la distribution
Composants disponibles
Clé ou trousseau de confiance utilisé
```

Les syntaxes possibles comprennent le format traditionnel d'une ligne et le format deb822.

Ne copie pas une source issue d'une autre version de distribution sans vérifier qu'elle convient au système.

## 19.3. Pourquoi mélanger des dépôts de distributions différentes est-il risqué ?

Une distribution organise ses paquets avec un ensemble cohérent de versions et de dépendances.

Ajouter des sources appartenant à une version différente ou à une distribution différente peut modifier les choix de versions et provoquer des conflits.

Conséquences possibles :

- installation de bibliothèques incompatibles ;
- remplacement de paquets fondamentaux ;
- suppression de composants nécessaires ;
- impossibilité de mettre à niveau certains paquets ;
- instabilité du système.

N'ajoute pas un dépôt d'une autre version de Debian ou Ubuntu simplement parce qu'il contient un logiciel absent du dépôt actuel.

Recherche plutôt une source compatible ou une méthode d'installation officiellement prise en charge.

## 19.4. Dépôts et priorités APT

APT peut utiliser des priorités de source et des préférences de version pour sélectionner les paquets.

La commande :

```bash
apt-cache policy nom-du-paquet
```

aide à examiner les versions connues et leurs priorités.

Un paquet peut être disponible depuis plusieurs sources, avec des versions et des priorités différentes.

Ne suppose pas que le dépôt dont le nom semble le plus familier est forcément celui choisi par APT.

## 19.5. Les dépôts tiers et les clés de confiance

Lorsqu'une source tierce demande l'ajout d'une clé de signature, il faut comprendre qui gère cette clé et à quels paquets la confiance s'applique.

Il faut éviter les méthodes qui désactivent les vérifications d'authenticité ou qui permettent à une clé tierce de signer sans restriction tous les dépôts du système.

Les configurations modernes permettent notamment d'associer une clé à une source particulière au moyen de mécanismes comme `Signed-By`, selon la syntaxe de la distribution.

Ne copie pas des commandes d'ajout de clés provenant d'un site sans vérifier leur sens et leur portée.


# 20. Sécurité, signatures et confiance

## 20.1. Pourquoi la provenance est-elle importante ?

Installer un paquet peut permettre l'exécution de code sur le système.

Le gestionnaire peut également exécuter des scripts prévus par le paquet lors de son installation, de sa mise à jour ou de sa suppression.

Une source de paquet doit donc être traitée comme une source de code à laquelle on accorde de la confiance.

## 20.2. Vérification de l'authenticité

APT utilise des mécanismes de vérification des métadonnées de dépôt, fondés notamment sur une chaîne de confiance et des signatures.

Ces mécanismes permettent de vérifier l'authenticité des informations du dépôt selon la configuration et la politique de confiance.

Cela ne signifie pas que chaque paquet est automatiquement exempt de code malveillant : le système de signature repose sur la confiance accordée aux mainteneurs et à la gestion du dépôt.

## 20.3. Ne pas désactiver les vérifications de signature

Si APT signale un problème de signature ou d'authenticité, ne cherche pas immédiatement à contourner la vérification.

Il faut vérifier :

- si la clé est correcte ;
- si la source est légitime ;
- si la configuration est adaptée à la distribution ;
- si les métadonnées sont disponibles ;
- si une erreur de réseau ou une configuration obsolète explique le problème.

Désactiver les vérifications peut supprimer une protection essentielle.

## 20.4. Pourquoi `curl | sudo bash` mérite-t-il de la prudence ?

Certains sites proposent une commande qui télécharge un script et l'exécute immédiatement avec les privilèges administratifs.

Cette pratique exige une confiance très forte dans la source et dans le contenu reçu.

Le script peut modifier les fichiers système, ajouter des sources de logiciels ou effectuer d'autres opérations administratives.

Il est préférable de privilégier une méthode d'installation documentée et vérifiable, de lire les instructions, de comprendre les modifications et d'utiliser les dépôts pris en charge lorsque cela est possible.

## 20.5. Les dépôts officiels ne sont pas une garantie absolue

Les dépôts officiels offrent généralement une intégration adaptée à la distribution.

Cependant, il faut encore vérifier :

- le cycle de maintenance ;
- la version installée ;
- l'exposition de l'application ;
- les avis de sécurité ;
- la configuration ;
- les mises à jour effectivement appliquées.

La gestion des paquets fait partie de la sécurité du système, mais ne la résume pas entièrement.


# 21. Comparaison avec DNF/RPM et Pacman

Les commandes des sections précédentes portent principalement sur Debian et Ubuntu. Cette section permet de reconnaître les outils équivalents sur d'autres systèmes.

## 21.1. Fedora et les distributions RPM

Les distributions utilisant le format RPM s'appuient fréquemment sur DNF pour les opérations de gestion des dépôts et des dépendances.

Le programme `rpm` permet notamment de consulter et de vérifier les paquets RPM.

## 21.2. Rechercher avec DNF

```bash
dnf search htop
```

Cette commande recherche des correspondances selon les métadonnées disponibles.

## 21.3. Consulter les informations d'un paquet

```bash
dnf info htop
```

Cette commande affiche les informations connues par DNF sur le paquet concerné.

## 21.4. Installer un paquet

```bash
sudo dnf install htop
```

DNF cherche à installer le paquet demandé et les dépendances nécessaires en fonction des sources configurées.

Comme avec APT, lis le résumé de transaction avant de confirmer.

## 21.5. Rechercher les mises à jour

```bash
dnf check-update
```

Cette commande vérifie si des mises à jour sont disponibles.

**Attention :** DNF peut retourner le code de sortie `100` lorsqu'il indique que des mises à jour sont disponibles. Dans un script, ce résultat ne doit donc pas être automatiquement interprété comme une erreur d'exécution.

## 21.6. Mettre à jour les paquets

```bash
sudo dnf upgrade
```

Cette commande demande la mise à niveau des paquets conformément à la résolution de dépendances de DNF.

Le nombre de paquets concernés et le résultat dépendent des sources, des versions et des contraintes déclarées.

## 21.7. Supprimer un paquet

```bash
sudo dnf remove htop
```

DNF présente les changements envisagés. Il faut vérifier les éventuelles suppressions de dépendances et les conséquences avant de confirmer.

## 21.8. Consulter la base RPM

Pour vérifier si le paquet est installé :

```bash
rpm -q htop
```

Pour obtenir davantage d'informations :

```bash
rpm -qi htop
```

Pour lister les fichiers enregistrés :

```bash
rpm -ql htop
```

Pour rechercher le paquet propriétaire d'un fichier :

```bash
rpm -qf /usr/bin/htop
```

Le résultat dépend naturellement du fait que le paquet et le chemin existent sur le système concerné.

## 21.9. Vérifier les fichiers d'un paquet RPM

```bash
rpm -V htop
```

Cette commande compare les attributs enregistrés des fichiers du paquet avec les informations attendues par la base RPM.

Une différence doit être interprétée : elle peut correspondre à une modification de configuration légitime, à un fichier changé ou à une anomalie.

L'absence de différence n'est pas une preuve absolue de sécurité de l'application.

## 21.10. Arch Linux et Pacman

Sur Arch Linux, le gestionnaire habituel est `pacman`.

Rechercher un paquet dans les dépôts synchronisés :

```bash
pacman -Ss htop
```

Installer un paquet :

```bash
sudo pacman -S htop
```

Actualiser les bases de données des dépôts et mettre à niveau le système se fait habituellement avec :

```bash
sudo pacman -Syu
```

Arch Linux recommande une gestion cohérente des mises à niveau ; il faut consulter la documentation de la distribution avant d'effectuer des opérations partielles ou inhabituelles.

Pour consulter un paquet installé :

```bash
pacman -Qi htop
```

Pour lister ses fichiers :

```bash
pacman -Ql htop
```

Les commandes ne sont pas interchangeables avec celles d'APT ou de DNF.

## 21.11. Tableau de correspondance

| Opération | Debian / Ubuntu | Fedora / RHEL | Arch Linux |
|---|---|---|---|
| Rechercher | `apt search nom` | `dnf search nom` | `pacman -Ss nom` |
| Informations disponibles | `apt show nom` | `dnf info nom` | `pacman -Si nom` |
| Installer | `apt install nom` | `dnf install nom` | `pacman -S nom` |
| Mettre à jour l'index | `apt update` | Le gestionnaire synchronise ses métadonnées selon son fonctionnement | `pacman -Sy` est la synchronisation seule, à éviter comme routine isolée |
| Mettre à niveau | `apt upgrade` | `dnf upgrade` | `pacman -Syu` |
| Supprimer | `apt remove nom` | `dnf remove nom` | `pacman -R nom` |
| État du paquet installé | `dpkg -s nom` | `rpm -qi nom` | `pacman -Qi nom` |
| Lister les fichiers | `dpkg -L nom` | `rpm -ql nom` | `pacman -Ql nom` |

Ce tableau présente les usages courants, mais il ne décrit pas toutes les options, politiques de mise à jour ou différences de versions.

## 21.12. Cas particulier : systèmes immuables

Certaines distributions ou éditions utilisent des images système et des mécanismes de mise à jour différents des installations traditionnelles de paquets.

Il peut être nécessaire d'utiliser un outil adapté, tel que `rpm-ostree`, plutôt que d'appliquer mécaniquement les commandes DNF prévues pour une installation traditionnelle.

La bonne méthode commence toujours par l'identification exacte de la distribution et de son mode de fonctionnement.


# 22. Fonctionnement interne d'une installation

## 22.1. Le gestionnaire ne copie pas seulement des fichiers

Une transaction de gestion de paquets comprend plusieurs étapes.

```text
DEMANDE D'INSTALLATION
          |
          v
SÉLECTION DES PAQUETS
          |
          v
RÉSOLUTION DES DÉPENDANCES
          |
          v
VÉRIFICATION DES CONTRAINTES
          |
          v
TÉLÉCHARGEMENT DES ARCHIVES
          |
          v
VÉRIFICATIONS D'INTÉGRITÉ
ET D'AUTHENTICITÉ PRÉVUES
          |
          v
DÉPAQUETAGE
          |
          v
CONFIGURATION ET SCRIPTS
          |
          v
MISE À JOUR DE L'ÉTAT LOCAL
          |
          v
VÉRIFICATION DU RÉSULTAT
```

Les étapes précises dépendent du gestionnaire, du type de paquet et des conditions du système.

## 22.2. Les scripts de maintenance

Certains paquets comportent des scripts qui interviennent pendant l'installation, la mise à jour ou la suppression.

Ils peuvent notamment préparer un utilisateur de service, ajuster des éléments de configuration ou intégrer le logiciel au mécanisme de gestion des services.

Ces scripts peuvent aussi échouer.

Le message d'erreur doit alors être examiné avec les informations de la transaction. Il ne faut pas supposer que le seul fait d'avoir téléchargé l'archive signifie que l'installation est terminée.

## 22.3. L'état local peut être incomplet

Une installation interrompue peut laisser le gestionnaire dans un état qui nécessite une reprise.

Sur Debian ou Ubuntu, certains paquets peuvent être dépaquetés mais pas complètement configurés.

La commande :

```bash
sudo dpkg --configure -a
```

permet de demander la configuration des paquets dépaquetés mais non configurés.

Elle n'est pas une solution universelle : si une dépendance manque ou si un script de configuration échoue, il faut d'abord comprendre le problème.

Ne lance pas cette commande comme réflexe unique à chaque erreur APT ; examine le message initial et la situation de la base de paquets.

## 22.4. Que se passe-t-il pendant une mise à jour ?

La mise à jour peut remplacer des fichiers, exécuter des scripts, modifier certains composants du service et déclencher des opérations annexes.

Selon le logiciel, il peut être nécessaire de :

- recharger un service ;
- redémarrer le service ;
- redémarrer la machine ;
- effectuer une migration de données ;
- contrôler la compatibilité de la configuration.

Les indications de la distribution et du logiciel doivent guider la procédure.

## 22.5. Pourquoi une base locale est-elle importante ?

La base permet au gestionnaire de connaître les paquets et leurs métadonnées.

Si des fichiers sont modifiés ou supprimés manuellement, le système peut se retrouver dans un état où la base ne correspond plus parfaitement au contenu du disque.

Une réparation doit donc prendre en compte les deux aspects : les enregistrements du paquet et les fichiers réellement présents.


# 23. Journaux, erreurs et dépannage

## 23.1. Les erreurs de gestion des paquets

Les problèmes peuvent provenir de différentes couches :

- réseau inaccessible ;
- dépôt indisponible ;
- index périmés ;
- mauvaise configuration de source ;
- clé ou signature de dépôt invalide ;
- dépendances incompatibles ;
- espace disque insuffisant ;
- verrou utilisé par un autre gestionnaire ;
- paquet partiellement configuré ;
- script de maintenance en échec.

Il faut lire le message exact plutôt que d'appliquer directement une série de commandes de réparation.

## 23.2. Erreur : impossible de télécharger un paquet

Commence par vérifier si le réseau fonctionne et si les dépôts sont accessibles.

Sur Debian ou Ubuntu :

```bash
sudo apt update
```

Examine ensuite les messages.

Une erreur HTTP, DNS ou TLS peut avoir des causes différentes.

Ne désactive pas les contrôles TLS ou les vérifications de signature pour contourner une erreur de réseau.

## 23.3. Erreur : dépendances non satisfaites

APT peut signaler que certaines dépendances ne peuvent pas être résolues.

Les causes possibles comprennent :

- un dépôt incompatible ;
- des index qui ne correspondent pas à la configuration ;
- un paquet local incompatible ;
- une version qui n'est pas disponible ;
- des paquets retenus ;
- un état local incomplet.

Commence par examiner les sources et les versions :

```bash
apt-cache policy nom-du-paquet
```

Puis consulte les paquets retenus :

```bash
apt-mark showhold
```

Il est important de lire l'ensemble du message d'erreur avant de modifier la configuration.

## 23.4. Erreur : espace disque insuffisant

Vérifie l'espace disque :

```bash
df -h
```

Pour repérer les principaux répertoires, tu peux utiliser un outil approprié tel que `du`, en choisissant un chemin pertinent pour l'analyse.

Avant de supprimer des fichiers, distingue :

- les archives de paquets téléchargées ;
- les journaux ;
- les données applicatives ;
- les fichiers de configuration ;
- les fichiers temporaires ;
- les fichiers supprimés mais encore ouverts.

Pour nettoyer le cache APT, après avoir vérifié qu'il s'agit bien du besoin :

```bash
sudo apt clean
```

Cette commande ne doit pas être confondue avec la suppression des données de l'application.

## 23.5. Erreur : verrou de gestion des paquets

Si un message indique que la base ou un verrou de gestion des paquets est utilisé, un autre processus peut être en train de travailler.

Il peut s'agir d'une mise à jour automatique ou d'une autre opération d'administration.

La conduite correcte est la suivante :

1. lire le message ;
2. vérifier s'il existe une opération APT ou dpkg active ;
3. attendre la fin de l'opération légitime si elle est toujours en cours ;
4. examiner les journaux et l'état local si l'opération semble bloquée ;
5. éviter de supprimer manuellement les fichiers de verrou sans diagnostic.

Supprimer un fichier de verrou ne termine pas le processus qui utilise réellement la base. Cela peut permettre à une seconde opération de commencer et de créer une situation incohérente.

## 23.6. Erreur : paquet partiellement configuré

Sur Debian ou Ubuntu, commence par examiner :

```bash
dpkg --audit
```

Cette commande peut signaler des paquets qui nécessitent une attention particulière.

Puis examine le message associé au paquet en difficulté et les dépendances concernées.

Lorsque les causes du problème ont été traitées, il peut être approprié d'utiliser les outils APT et dpkg de réparation adaptés à la situation.

## 23.7. La commande `apt --fix-broken install`

```bash
sudo apt --fix-broken install
```

Cette commande demande à APT de tenter de corriger des dépendances cassées.

Elle peut proposer des installations ou des suppressions.

Il faut examiner soigneusement le plan proposé avant de confirmer.

Ne lance pas cette commande sans comprendre les changements envisagés, notamment sur un serveur important.

## 23.8. Consulter les journaux APT et dpkg

Sur Debian et Ubuntu, les journaux peuvent inclure :

```text
/var/log/apt/history.log
/var/log/apt/term.log
/var/log/dpkg.log
```

Consulter les dernières lignes, selon ce qui est disponible :

```bash
sudo tail -n 100 /var/log/dpkg.log
```

Et :

```bash
sudo tail -n 100 /var/log/apt/history.log
```

Ces journaux peuvent aider à déterminer quels paquets ont été installés, mis à jour ou supprimés et quand les opérations ont eu lieu.

La rotation des journaux peut déplacer ou compresser les fichiers plus anciens.

## 23.9. Erreur après mise à jour

Si un service ne fonctionne plus après une mise à jour :

```bash
systemctl --failed
```

Puis, pour le service concerné :

```bash
systemctl status nom.service
```

Et :

```bash
journalctl -u nom.service -n 100 --no-pager
```

Il faut examiner la chronologie, la configuration et le message réel.

Une erreur qui apparaît après une mise à jour peut être liée à cette mise à jour, mais il faut vérifier les preuves avant d'en conclure qu'elle en est la cause.


# 24. Gestion des paquets dans les environnements serveur

## 24.1. Pourquoi un serveur exige-t-il plus de prudence ?

Un serveur peut fournir des fonctions utilisées par d'autres personnes ou d'autres systèmes.

Une suppression ou une mise à jour incorrecte peut interrompre :

- le réseau ;
- l'accès distant ;
- un serveur Web ;
- une base de données ;
- des sauvegardes ;
- l'authentification ;
- la supervision ;
- un service métier.

Le fait qu'une opération soit simple sur un poste de laboratoire ne signifie pas qu'elle soit sans risque en production.

## 24.2. Préparer une opération de maintenance

Avant une installation, suppression ou mise à jour importante :

1. identifier la machine et son rôle ;
2. connaître les paquets concernés ;
3. lire les changements prévus ;
4. vérifier les dépendances ;
5. contrôler l'espace disque ;
6. sauvegarder les données et configurations importantes ;
7. définir une fenêtre d'intervention lorsque nécessaire ;
8. prévoir les vérifications après l'opération ;
9. conserver une procédure de retour arrière adaptée.

Une sauvegarde doit être testée et sa restauration comprise, pas simplement considérée comme existante parce qu'une commande de copie a été exécutée.

## 24.3. Mettre à jour un serveur

Une séquence de base sur Debian ou Ubuntu est :

```bash
sudo apt update
```

Puis examiner les mises à jour :

```bash
apt list --upgradable
```

Puis, après examen du contexte et des changements proposés :

```bash
sudo apt upgrade
```

Sur un serveur important, ces commandes s'intègrent dans une procédure de maintenance plus large.

Selon les services, des redémarrages peuvent être nécessaires.

## 24.4. Contrôler après la mise à jour

Vérifie notamment :

```bash
systemctl --failed
```

Examine ensuite les services nécessaires au rôle de la machine.

Pour un service précis :

```bash
systemctl status nom.service
```

Pour ses journaux :

```bash
journalctl -u nom.service -n 100 --no-pager
```

Enfin, vérifie le fonctionnement de l'application à l'aide de tests adaptés.

## 24.5. Conserver une trace des changements

Pour une intervention importante, note :

- la date ;
- la machine ;
- les paquets concernés ;
- les versions avant et après ;
- les commandes exécutées ;
- les erreurs observées ;
- les vérifications réalisées ;
- le résultat final.

Cette traçabilité aide à comprendre les différences entre systèmes et à retrouver l'origine d'une régression.


# 25. Automatiser des opérations simples

## 25.1. Pourquoi automatiser ?

Les vérifications suivantes sont fréquentes :

- connaître la version d'un paquet ;
- vérifier si un paquet est installé ;
- détecter des mises à jour disponibles ;
- enregistrer des informations sur les paquets ;
- préparer un compte rendu.

L'automatisation réduit les manipulations répétitives, mais elle doit gérer correctement les erreurs et éviter les modifications involontaires.

## 25.2. Script : vérifier un paquet Debian ou Ubuntu

Créer un fichier :

```bash
nano verifier-paquet.sh
```

Contenu :

```bash
#!/usr/bin/env bash

set -u

if [[ $# -ne 1 ]]; then
    printf 'Usage : %s nom-du-paquet\n' "$0" >&2
    exit 2
fi

PACKAGE=$1

if ! command -v dpkg-query >/dev/null 2>&1; then
    printf 'Erreur : dpkg-query est indisponible.\n' >&2
    exit 2
fi

if dpkg-query -W -f='${db:Status-Status}\n' "$PACKAGE" 2>/dev/null \
    | grep -qx 'installed'; then

    printf 'Paquet installé : %s\n' "$PACKAGE"
    dpkg-query -W -f='Version : ${Version}\nArchitecture : ${Architecture}\n' "$PACKAGE"

else
    printf 'Paquet absent ou non installé dans l''état attendu : %s\n' "$PACKAGE"
    exit 1
fi
```

Rendre le script exécutable :

```bash
chmod +x verifier-paquet.sh
```

Exemple d'utilisation :

```bash
./verifier-paquet.sh bash
```

Le paquet `bash` est utilisé ici comme exemple, car il est courant sur les systèmes Linux.

### Explication

- Le script vérifie qu'un argument est fourni.
- Il vérifie que `dpkg-query` est disponible.
- Il interroge la base locale.
- Il vérifie le statut demandé.
- Il affiche la version et l'architecture si le paquet est dans l'état prévu.

Ce script est conçu pour les distributions utilisant `dpkg`.

## 25.3. Script : enregistrer les mises à jour disponibles

Exemple pour Debian ou Ubuntu :

```bash
#!/usr/bin/env bash

set -u

if ! command -v apt-get >/dev/null 2>&1; then
    printf 'Erreur : apt-get est indisponible.\n' >&2
    exit 2
fi

printf '=== Date du contrôle ===\n'
date '+%F %T'

printf '\n%s\n' '=== Mises à jour disponibles dans les index locaux ==='
apt list --upgradable
```

Ce script ne modifie pas les paquets.

Il se base sur les index locaux actuellement disponibles et ne les actualise pas lui-même.

Pour obtenir des informations récentes, il faut actualiser les index dans une opération appropriée, qui peut nécessiter des privilèges administratifs et une connectivité réseau.

## 25.4. Pourquoi éviter les mises à jour automatiques mal contrôlées ?

Un script qui installe systématiquement tous les paquets sans examiner le résultat peut :

- accepter une suppression inattendue ;
- modifier des composants essentiels ;
- masquer un échec ;
- négliger un besoin de redémarrage ;
- appliquer une mise à jour incompatible avec l'application ;
- interrompre un service important.

L'automatisation doit donc séparer la collecte des informations et l'exécution des changements.


# 26. Travaux pratiques guidés

Les travaux pratiques suivants sont conçus pour une machine de laboratoire Debian ou Ubuntu. Ils utilisent des paquets courants et des actions d'administration classiques.

Lis toujours les résumés de transaction avant de confirmer une installation ou une suppression.

## TP 1 — Identifier la distribution

### Objectif

Découvrir le système de gestion des paquets présent sur la machine.

### Étape 1

```bash
cat /etc/os-release
```

Relève le nom et l'identifiant de la distribution.

### Étape 2

```bash
uname -r
```

Relève la version du noyau.

### Étape 3

```bash
command -v apt
```

### Étape 4

```bash
command -v dpkg
```

### Étape 5

Si la machine utilise Debian ou Ubuntu :

```bash
dpkg --print-architecture
```

### Résultat attendu

Tu dois pouvoir identifier la distribution, son noyau, son architecture de paquets et les outils disponibles.


## TP 2 — Rechercher et examiner un paquet

### Objectif

Rechercher un logiciel et comprendre les informations de son paquet.

### Étape 1

```bash
apt-cache search htop
```

Si les index ne sont pas disponibles ou s'ils sont anciens, actualise-les dans le contexte de ta machine.

### Étape 2

```bash
apt show htop
```

### Étape 3

```bash
apt-cache policy htop
```

### Étape 4

```bash
apt-cache depends htop
```

### Résultat attendu

Tu dois savoir distinguer le nom, la version disponible, l'origine et les dépendances déclarées du paquet.


## TP 3 — Installer et vérifier un paquet

### Objectif

Effectuer une installation contrôlée.

### Étape 1 : rechercher le paquet

```bash
apt-cache search htop
```

### Étape 2 : simuler l'installation

```bash
apt-get -s install htop
```

### Étape 3 : installer

Après avoir examiné le plan :

```bash
sudo apt install htop
```

### Étape 4 : vérifier l'état

```bash
dpkg -s htop
```

### Étape 5 : vérifier les fichiers

```bash
dpkg -L htop
```

### Étape 6 : vérifier la commande

```bash
command -v htop
```

### Résultat attendu

Le paquet doit être enregistré comme installé, et les fichiers de la liste doivent correspondre au paquet présent dans la base locale.


## TP 4 — Examiner les mises à jour disponibles

### Objectif

Distinguer l'actualisation des index de la mise à niveau des paquets.

### Étape 1

```bash
sudo apt update
```

### Étape 2

```bash
apt list --upgradable
```

### Étape 3

Examiner les résultats.

### Étape 4

Si tu souhaites appliquer les mises à jour sur la machine de laboratoire, et après avoir compris les conséquences :

```bash
sudo apt upgrade
```

### Résultat attendu

Tu dois être capable d'expliquer le rôle de chacune des deux commandes et de montrer comment vérifier le résultat.


## TP 5 — Supprimer un paquet de test

### Objectif

Comprendre le retrait d'un paquet sans modifier manuellement les fichiers du système.

### Étape 1

Vérifier que `htop` est installé :

```bash
dpkg -s htop
```

### Étape 2

Examiner la simulation :

```bash
apt-get -s remove htop
```

### Étape 3

Après examen du plan :

```bash
sudo apt remove htop
```

### Étape 4

Vérifier le résultat :

```bash
dpkg -s htop
```

Le paquet doit avoir été retiré dans les conditions normales de l'opération.

### Étape 5

Si tu dois remettre l'outil à disposition pour un autre travail pratique :

```bash
sudo apt install htop
```

### Résultat attendu

Tu dois comprendre la différence entre la suppression d'un paquet par APT et la suppression manuelle de fichiers.


## TP 6 — Examiner le cache APT

### Objectif

Comprendre la différence entre les paquets installés et les archives mises en cache.

### Étape 1

```bash
sudo du -sh /var/cache/apt/archives
```

Cette commande affiche la taille du répertoire d'archives, si celui-ci existe et est accessible.

### Étape 2

Consulte la documentation de la commande :

```bash
man apt
```

### Étape 3

Si l'objectif est de nettoyer les archives téléchargées après avoir compris la conséquence :

```bash
sudo apt clean
```

### Étape 4

Revérifie la taille :

```bash
sudo du -sh /var/cache/apt/archives
```

### Résultat attendu

Tu dois comprendre que le nettoyage des archives téléchargées ne désinstalle pas les logiciels.


## TP 7 — Trouver le paquet propriétaire d'un fichier

### Objectif

Associer un fichier à son paquet.

### Étape 1

Identifier le chemin de la commande `apt` :

```bash
command -v apt
```

### Étape 2

Utiliser le chemin obtenu avec :

```bash
dpkg -S /usr/bin/apt
```

Le chemin de l'exemple peut varier. Utilise la valeur réelle renvoyée par `command -v` si elle diffère.

### Étape 3

Lister les fichiers du paquet indiqué par la sortie.

### Résultat attendu

Tu dois pouvoir expliquer pourquoi un fichier géré par un paquet doit être examiné avec les outils de gestion de paquets appropriés.


# 27. Exercices d'application

Réponds aux questions avant de consulter les corrections.

## Exercice 1 — Paquet et programme

Explique la différence entre un paquet logiciel et un programme exécutable.

Pourquoi un paquet installé ne garantit-il pas que son application fonctionne correctement ?

## Exercice 2 — Gestionnaires

Quel est le rôle général d'APT ?

Quel est le rôle général de `dpkg` ?

## Exercice 3 — Dépôts

Qu'est-ce qu'un dépôt logiciel ?

Pourquoi faut-il examiner la provenance d'un dépôt tiers avant de lui accorder sa confiance ?

## Exercice 4 — Recherche

Quelle commande Debian/Ubuntu permet de rechercher un paquet nommé `htop` dans les index locaux ?

Quelle commande affiche ses informations disponibles ?

## Exercice 5 — Installation

Écris la commande qui permet de demander l'installation du paquet `curl` avec APT.

Explique le rôle de `sudo`.

## Exercice 6 — Dépendances

Pourquoi une installation peut-elle entraîner l'installation de plusieurs paquets ?

Qu'est-ce qu'une dépendance ?

## Exercice 7 — Mise à jour

Explique la différence entre :

```bash
sudo apt update
```

et :

```bash
sudo apt upgrade
```

## Exercice 8 — Suppression

Quelle est la différence générale entre `apt remove` et `apt purge` ?

Pourquoi faut-il rester prudent avec `apt autoremove` ?

## Exercice 9 — Fichiers

Quelle commande permet de lister les fichiers enregistrés pour un paquet Debian/Ubuntu déjà installé ?

Quelle commande peut rechercher le paquet propriétaire d'un fichier ?

## Exercice 10 — Paquet local

Pourquoi `apt install ./fichier.deb` est-il souvent plus adapté à l'installation locale qu'une simple utilisation de `dpkg -i` ?

## Exercice 11 — Signature

APT signale une erreur d'authenticité pour un dépôt.

Pourquoi ne faut-il pas désactiver immédiatement les vérifications de signature ?

## Exercice 12 — Paquet partiellement configuré

Une installation a échoué pendant la configuration d'un paquet.

Quelles informations faut-il examiner avant de tenter une réparation ?

## Exercice 13 — Cache

Quelle commande permet de supprimer les archives téléchargées du cache APT sans désinstaller les paquets installés ?

## Exercice 14 — Journalisation

Cite deux journaux qui peuvent aider à comprendre les changements de paquets sur Debian ou Ubuntu.

## Exercice 15 — Autres distributions

Quelle commande installe couramment un paquet avec DNF ?

Quelle commande permet de consulter la version installée d'un paquet avec RPM ?

## Exercice 16 — Production

Avant de mettre à jour un serveur important, cite au moins six vérifications ou précautions utiles.


# 28. Corrections détaillées

## Correction 1 — Paquet et programme

Un paquet est une unité de distribution qui contient des fichiers et des métadonnées nécessaires à la gestion d'un logiciel.

Un programme est l'un des composants pouvant être fournis par ce paquet.

Un paquet installé ne garantit pas que le service est démarré, que la configuration est correcte ou que toutes les dépendances externes sont disponibles.

## Correction 2 — Gestionnaires

APT fournit des fonctions de gestion de haut niveau : recherche dans les dépôts, résolution des dépendances, téléchargement, installation et mises à jour.

`dpkg` gère les opérations de bas niveau sur les paquets Debian, notamment le dépaquetage, la configuration et l'interrogation de la base locale.

## Correction 3 — Dépôts

Un dépôt est une source organisée de paquets et de métadonnées.

Un dépôt tiers peut fournir du code qui s'exécute avec des privilèges élevés lors de l'installation ou du fonctionnement du logiciel. Sa provenance, sa compatibilité et sa politique de confiance doivent donc être examinées.

## Correction 4 — Recherche

Pour rechercher :

```bash
apt-cache search htop
```

Pour consulter les informations du paquet :

```bash
apt show htop
```

## Correction 5 — Installation

La commande est :

```bash
sudo apt install curl
```

`sudo` permet d'exécuter l'opération avec les privilèges administratifs nécessaires, selon les droits accordés à l'utilisateur.

## Correction 6 — Dépendances

Un paquet peut nécessiter d'autres composants pour fonctionner ou pour être configuré.

Le gestionnaire doit donc installer les dépendances manquantes et vérifier les contraintes de compatibilité.

## Correction 7 — Mise à jour

`apt update` actualise les index locaux des dépôts.

`apt upgrade` applique les mises à niveau autorisées pour les paquets installés, selon les dépendances et les règles de la commande.

La première commande met à jour les informations disponibles ; la seconde modifie les paquets installés.

## Correction 8 — Suppression

`apt remove` retire le paquet, tout en conservant généralement certains fichiers de configuration gérés.

`apt purge` demande aussi la suppression des fichiers de configuration gérés par le paquet.

`apt autoremove` peut supprimer des dépendances qui ne sont plus considérées nécessaires. Il faut vérifier la liste avant de confirmer, car le gestionnaire ne connaît pas nécessairement tous les usages particuliers de l'administrateur.

## Correction 9 — Fichiers

Pour lister les fichiers :

```bash
dpkg -L nom-du-paquet
```

Pour rechercher le propriétaire d'un fichier :

```bash
dpkg -S /chemin/du/fichier
```

Les commandes interrogent la base locale. Elles peuvent ne pas identifier les fichiers générés manuellement ou ceux qui ne sont pas enregistrés par le paquetage.

## Correction 10 — Paquet local

`apt install ./fichier.deb` permet à APT de prendre en charge la résolution des dépendances à partir des sources configurées.

`dpkg -i` traite le paquet local mais ne résout pas toutes les dépendances depuis les dépôts comme APT.

## Correction 11 — Signature

Les vérifications d'authenticité participent à la protection contre les sources non fiables ou les métadonnées altérées.

Il faut vérifier la source, les clés et la configuration au lieu de désactiver les protections.

## Correction 12 — Paquet partiellement configuré

Il faut examiner le message d'erreur, la version, les dépendances, l'état local du paquet et les éventuelles opérations qui ont échoué.

La commande :

```bash
dpkg --audit
```

peut aider à identifier des paquets qui nécessitent une attention particulière.

## Correction 13 — Cache

La commande est :

```bash
sudo apt clean
```

Elle nettoie les archives de paquets téléchargées dans le cache APT. Elle ne supprime pas les paquets installés.

## Correction 14 — Journalisation

Deux journaux courants sont :

```text
/var/log/apt/history.log
/var/log/dpkg.log
```

Le premier peut retracer l'historique des opérations APT ; le second enregistre des événements de gestion des paquets par dpkg.

Leur disponibilité et leur contenu dépendent de la configuration et de la rotation des journaux.

## Correction 15 — Autres distributions

Pour installer un paquet avec DNF :

```bash
sudo dnf install nom-du-paquet
```

Pour consulter la version et les informations d'un paquet RPM installé :

```bash
rpm -qi nom-du-paquet
```

## Correction 16 — Production

Les précautions peuvent comprendre :

1. vérifier la distribution et sa version ;
2. consulter les paquets concernés ;
3. examiner les changements proposés ;
4. vérifier l'espace disque ;
5. sauvegarder les données et configurations importantes ;
6. planifier une fenêtre de maintenance si nécessaire ;
7. vérifier les dépendances ;
8. consulter les informations de sécurité ;
9. prévoir les contrôles après mise à jour ;
10. conserver les informations nécessaires au retour arrière.


# 29. Défi final : préparer un serveur Linux

## 29.1. Contexte

Tu reçois un serveur Linux de laboratoire destiné à accueillir de futurs services.

L'équipe te demande de préparer une base logicielle simple et de produire un compte rendu.

Le serveur utilise Debian ou Ubuntu.

Les besoins sont les suivants :

```text
BESOIN 1
Identifier la distribution et l'architecture.

BESOIN 2
Vérifier les sources logicielles configurées.

BESOIN 3
Rechercher un outil de surveillance des processus.

BESOIN 4
Installer un paquet de test.

BESOIN 5
Vérifier la version et les fichiers du paquet.

BESOIN 6
Contrôler les mises à jour disponibles.

BESOIN 7
Comprendre la suppression du paquet.

BESOIN 8
Conserver une trace des opérations.
```

Le serveur est une machine de laboratoire. Les opérations d'installation, de mise à niveau et de suppression restent soumises à l'examen des changements proposés.

## 29.2. Mission

Réalise les opérations suivantes :

1. identifier la distribution ;
2. identifier l'architecture ;
3. examiner les sources APT ;
4. actualiser les index ;
5. rechercher `htop` ;
6. examiner les informations et dépendances du paquet ;
7. simuler l'installation ;
8. installer le paquet après vérification ;
9. vérifier le statut, la version et les fichiers ;
10. examiner les mises à jour disponibles ;
11. consulter les journaux d'administration des paquets ;
12. supprimer le paquet dans le cadre de l'exercice ;
13. vérifier le résultat de la suppression ;
14. rédiger un compte rendu.

## 29.3. Contraintes

- N'ajoute pas de dépôt tiers pour cet exercice.
- Ne désactive pas de vérification de signature.
- Ne supprime pas manuellement les fichiers du paquet.
- N'exécute pas une opération de mise à niveau sans examiner le plan et les conséquences.
- N'utilise pas `full-upgrade` sans une raison identifiée et une vérification des suppressions éventuelles.
- Vérifie le résultat après chaque opération.


# 30. Correction détaillée du défi final

## 30.1. Étape 1 — Identifier le système

Exécuter :

```bash
cat /etc/os-release
```

Puis :

```bash
uname -r
```

Et :

```bash
dpkg --print-architecture
```

Consigner les valeurs relevées.

Il faut confirmer qu'il s'agit bien d'un environnement utilisant `dpkg` avant d'effectuer les opérations suivantes.

## 30.2. Étape 2 — Examiner les sources APT

Lister les fichiers couramment utilisés :

```bash
ls -l /etc/apt/sources.list /etc/apt/sources.list.d/
```

Un des chemins peut être absent selon la version et la configuration.

Examiner ensuite le contenu des fichiers de sources présents et pertinents.

L'objectif est de comprendre quelles sources sont configurées, sans modifier leurs paramètres.

Si une source inattendue apparaît, il faut examiner sa provenance et sa compatibilité avant de continuer.

## 30.3. Étape 3 — Actualiser les index

```bash
sudo apt update
```

Lire l'ensemble des résultats.

Si une erreur d'authenticité, de signature ou de dépôt apparaît, ne contourne pas immédiatement la protection. Identifie la source concernée et la cause du problème.

## 30.4. Étape 4 — Rechercher `htop`

```bash
apt-cache search htop
```

Puis :

```bash
apt show htop
```

Et :

```bash
apt-cache policy htop
```

Ces commandes permettent d'examiner le nom, la description, les dépendances, les versions connues et l'origine prévue du paquet.

## 30.5. Étape 5 — Simuler l'installation

```bash
apt-get -s install htop
```

Examine :

- les paquets ajoutés ;
- les éventuelles mises à niveau ;
- les dépendances ;
- les changements de configuration ;
- les risques de suppression.

Si le plan est inattendu, ne confirme pas l'opération réelle avant d'avoir compris pourquoi.

## 30.6. Étape 6 — Installer le paquet

Dans le cadre du laboratoire, si le plan est cohérent :

```bash
sudo apt install htop
```

Lire le résumé de transaction avant de confirmer.

Laisser l'opération se terminer et relever les éventuelles erreurs.

## 30.7. Étape 7 — Vérifier l'installation

```bash
dpkg -s htop
```

Puis :

```bash
dpkg-query -W -f='${Package} ${Version} ${Architecture}\n' htop
```

Ensuite :

```bash
command -v htop
```

Et :

```bash
dpkg -L htop
```

Les résultats permettent de confirmer l'état du paquet, sa version enregistrée, la disponibilité de la commande et les fichiers recensés.

## 30.8. Étape 8 — Examiner les mises à jour

```bash
apt list --upgradable
```

Cette commande ne met pas les paquets à niveau.

Si une mise à niveau doit être effectuée sur le laboratoire, examine les changements proposés et utilise la procédure adaptée à l'objectif.

Pour ce défi, l'observation et la documentation des mises à jour disponibles suffisent.

## 30.9. Étape 9 — Consulter les journaux

```bash
sudo tail -n 100 /var/log/dpkg.log
```

Et :

```bash
sudo tail -n 100 /var/log/apt/history.log
```

Si les journaux sont présents, ils permettent de rechercher les opérations récentes et de confirmer les changements enregistrés.

La rotation des journaux peut entraîner la présence de fichiers archivés.

## 30.10. Étape 10 — Simuler la suppression

```bash
apt-get -s remove htop
```

Examine les paquets concernés avant d'effectuer l'opération réelle.

## 30.11. Étape 11 — Supprimer le paquet de test

```bash
sudo apt remove htop
```

Après la suppression, vérifier :

```bash
dpkg -s htop
```

Le paquet doit avoir quitté l'état installé dans les conditions habituelles de l'opération.

Si des informations inattendues apparaissent, elles doivent être examinées avant de conclure.

## 30.12. Étape 12 — Rédiger le compte rendu

Exemple de structure :

```text
COMPTE RENDU — GESTION DES PAQUETS

1. Système
   Distribution :
   Version :
   Architecture :
   Noyau :

2. Sources
   Fichiers examinés :
   Sources pertinentes :
   Problèmes éventuels :

3. Paquet choisi
   Nom :
   Version candidate :
   Origine :
   Dépendances principales :

4. Installation
   Simulation réalisée :
   Changements prévus :
   Installation effectuée :
   Résultat :

5. Vérification
   Statut :
   Version installée :
   Chemin de la commande :
   Fichiers identifiés :

6. Mises à jour
   Index actualisés :
   Paquets à mettre à niveau :
   Action réellement effectuée :

7. Suppression
   Simulation :
   Suppression effectuée :
   Résultat après suppression :

8. Journaux
   Informations pertinentes :
   Heure des opérations :
   Anomalies détectées :

9. Conclusion
   Résultat final :
   Incertitudes restantes :
   Actions complémentaires :
```

Un bon compte rendu doit séparer les opérations effectivement réalisées des simples simulations.

Il ne doit pas prétendre qu'une mise à jour a été installée si seule la liste des mises à jour disponibles a été consultée.


# 31. Checklist de compétences

## Fondamentaux

- [ ] Je peux expliquer ce qu'est un paquet logiciel.
- [ ] Je comprends la différence entre un paquet, un programme et un service.
- [ ] Je comprends le rôle des dépendances.
- [ ] Je sais distinguer un dépôt d'un paquet local.
- [ ] Je sais identifier ma distribution avec `/etc/os-release`.

## APT et dpkg

- [ ] Je sais rechercher un paquet avec `apt-cache search`.
- [ ] Je sais consulter ses informations avec `apt show`.
- [ ] Je sais examiner les versions avec `apt-cache policy`.
- [ ] Je sais installer un paquet avec `apt install`.
- [ ] Je comprends la différence entre APT et dpkg.
- [ ] Je sais vérifier le statut d'un paquet.
- [ ] Je sais lister les fichiers associés à un paquet.
- [ ] Je sais rechercher le propriétaire d'un fichier.

## Mises à jour et suppressions

- [ ] Je distingue `apt update` et `apt upgrade`.
- [ ] Je sais consulter les mises à jour disponibles.
- [ ] Je comprends la différence entre `remove` et `purge`.
- [ ] Je sais examiner les changements proposés par une suppression.
- [ ] Je comprends le rôle de `autoremove`, `clean` et `autoclean`.
- [ ] Je sais pourquoi il faut examiner une opération avant de la confirmer.

## Sécurité et dépannage

- [ ] Je vérifie la provenance d'un paquet.
- [ ] Je ne désactive pas les vérifications de signature pour contourner une erreur.
- [ ] Je sais identifier les principaux journaux APT et dpkg.
- [ ] Je sais commencer un diagnostic de dépendances cassées.
- [ ] Je comprends le risque de supprimer manuellement des fichiers appartenant à un paquet.
- [ ] Je sais pourquoi il ne faut pas supprimer aveuglément un fichier de verrou.

## Autres distributions

- [ ] Je connais le rôle de DNF et de RPM.
- [ ] Je sais reconnaître les commandes principales de Pacman.
- [ ] Je comprends que les commandes diffèrent selon le système de paquetage.

## Administration

- [ ] Je sais préparer une mise à jour contrôlée.
- [ ] Je vérifie les services après une opération importante.
- [ ] Je conserve une trace des changements.
- [ ] Je sais distinguer une simulation d'une opération réellement effectuée.


# 32. Fiche de révision

## Identifier le système

```bash
cat /etc/os-release
```

```bash
uname -r
```

```bash
dpkg --print-architecture
```

## Recherche et informations

```bash
apt-cache search nom
```

```bash
apt show nom
```

```bash
apt-cache policy nom
```

```bash
apt-cache depends nom
```

```bash
apt-cache rdepends nom
```

## Installation

```bash
sudo apt install nom
```

Simulation :

```bash
apt-get -s install nom
```

Installation d'un fichier DEB local :

```bash
sudo apt install ./fichier.deb
```

## Mises à jour

```bash
sudo apt update
```

```bash
apt list --upgradable
```

```bash
sudo apt upgrade
```

Simulation d'une suppression :

```bash
apt-get -s remove nom
```

## Suppression et nettoyage

```bash
sudo apt remove nom
```

```bash
sudo apt purge nom
```

```bash
sudo apt autoremove
```

```bash
sudo apt clean
```

```bash
sudo apt autoclean
```

## Vérification

```bash
dpkg -s nom
```

```bash
dpkg-query -W nom
```

```bash
dpkg -L nom
```

```bash
dpkg -S /chemin/du/fichier
```

```bash
dpkg --audit
```

## Journaux et dépannage

```bash
sudo tail -n 100 /var/log/dpkg.log
```

```bash
sudo tail -n 100 /var/log/apt/history.log
```

```bash
sudo apt --fix-broken install
```

La dernière commande doit être utilisée après avoir compris les causes du problème et examiné les changements proposés.


# 33. Glossaire

**APT :** ensemble d'outils permettant notamment la recherche, l'installation, la mise à jour et la suppression de paquets sur les systèmes Debian et leurs dérivés.

**Architecture :** type de plateforme matérielle ou d'environnement visé par un paquet.

**Archive de paquet :** fichier contenant un paquet logiciel sous un format défini.

**Cache APT :** espace où APT conserve des archives téléchargées selon sa configuration.

**Conffile :** fichier de configuration suivi par le mécanisme de paquetage Debian.

**Dépendance :** relation déclarant qu'un paquet nécessite ou utilise un autre composant dans des conditions définies.

**Dépôt :** source organisée de paquets et de métadonnées.

**`dpkg` :** outil de bas niveau de gestion des paquets Debian.

**DNF :** gestionnaire de paquets de haut niveau couramment utilisé sur Fedora et d'autres distributions RPM.

**DEB :** format de paquet utilisé par Debian et les distributions qui s'appuient sur son système de paquetage.

**Installation locale :** opération qui utilise directement un fichier de paquet déjà présent sur la machine.

**Métadonnées :** informations décrivant les paquets, leurs versions, leurs dépendances et d'autres propriétés.

**Paquet :** unité de distribution et de gestion d'un logiciel.

**Paquet retenu :** paquet marqué afin que certaines mises à niveau habituelles ne s'appliquent pas à lui.

**Pacman :** gestionnaire de paquets utilisé par Arch Linux et certaines distributions associées.

**Purge :** suppression d'un paquet avec demande de suppression de ses fichiers de configuration gérés.

**RPM :** format et système de gestion des paquets utilisé par de nombreuses distributions Linux.

**Signature :** mécanisme cryptographique qui permet de vérifier l'authenticité de certaines données lorsque la chaîne de confiance est correctement configurée.

**Version candidate :** version qu'APT considère comme candidate à l'installation ou à la mise à niveau selon les informations et priorités disponibles.

**Version installée :** version enregistrée dans la base locale pour un paquet installé.


# 34. Documentation officielle

Les documents suivants permettent d'approfondir les notions présentées dans ce cours.

## Debian et Ubuntu

1. Documentation Ubuntu Server — gestion des paquets  
   https://ubuntu.com/server/docs/how-to/software/package-management/

2. FAQ Debian — outils de gestion des paquets  
   https://www.debian.org/doc/manuals/debian-faq/pkgtools

3. Debian Reference — gestion des paquets  
   https://www.debian.org/doc/manuals/debian-reference/ch02.en.html

4. Manuel Debian `apt-secure` — signatures et confiance des dépôts  
   https://manpages.debian.org/unstable/apt/apt-secure.8.en.html

5. Manuel `dpkg-query` — interrogation de la base locale  
   https://manpages.debian.org/testing/dpkg/dpkg-query.1.en.html

## Fedora et RPM

6. Documentation DNF — référence des commandes  
   https://dnf.readthedocs.io/en/latest/command_ref.html

7. Documentation RPM — manuel du gestionnaire RPM  
   https://rpm.org/docs/latest/man/rpm.8

8. Documentation RPM — dépendances  
   https://rpm.org/docs/latest/manual/more_dependencies.html

## Arch Linux

9. Wiki officiel Arch Linux — Pacman  
   https://wiki.archlinux.org/title/Pacman

Ces documents décrivent les possibilités et les comportements des outils. Les commandes et certains détails peuvent varier en fonction de la version de la distribution et de son mode de gestion des logiciels.


# Conclusion générale

La gestion des paquets est une composante essentielle de l'administration Linux.

Elle permet de gérer les logiciels de manière organisée, de suivre les versions, d'installer les dépendances nécessaires, d'appliquer les mises à jour et de conserver une base locale qui décrit l'état des paquets.

Tu sais maintenant distinguer un paquet, un dépôt, un gestionnaire et un programme. Tu as appris à rechercher, installer, vérifier, mettre à jour et supprimer des paquets avec APT, ainsi qu'à reconnaître les outils équivalents utilisés avec DNF/RPM et Pacman.

Tu as également étudié les sources logicielles, les signatures, les paquets locaux, les dépendances, les journaux et les principales erreurs rencontrées lors des opérations de maintenance.

Le principe essentiel reste le suivant :

```text
IDENTIFIER
    |
    v
RECHERCHER
    |
    v
VÉRIFIER LA SOURCE
    |
    v
EXAMINER LES DÉPENDANCES
    |
    v
PRÉVISUALISER LES CHANGEMENTS
    |
    v
EFFECTUER L'OPÉRATION
    |
    v
VÉRIFIER L'ÉTAT FINAL
    |
    v
DOCUMENTER
```

**Un administrateur Linux ne doit pas simplement savoir installer un logiciel. Il doit comprendre d'où provient le paquet, ce que son installation modifie et comment vérifier que le système reste cohérent après l'opération.**