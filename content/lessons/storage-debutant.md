# Système de fichiers et permissions Linux
## Cours complet — Niveau débutant

> **Fichier :** `storage-debutant.md`  
> **Domaine :** Administration Linux et stockage  
> **Niveau :** Débutant  
> **Prérequis :** Savoir utiliser le terminal, se déplacer avec `cd` et exécuter des commandes simples.  
> **Environnement conseillé :** Ubuntu ou Debian dans une machine virtuelle, ou un autre environnement Linux de test.  
> **Objectif général :** Comprendre l'organisation des fichiers sous Linux, découvrir les systèmes de fichiers, maîtriser les propriétaires et les permissions, et apprendre à vérifier l'utilisation du stockage sans risquer les données.


# Sommaire

1. Présentation du cours et objectifs pédagogiques
2. Comprendre le système de fichiers Linux
3. Explorer l'arborescence des répertoires
4. Comprendre les noms et les types de fichiers
5. Comprendre les disques, partitions et systèmes de fichiers
6. Comprendre les points de montage
7. Identifier les fichiers avec les inodes
8. Comprendre les liens physiques et symboliques
9. Comprendre les propriétaires et les groupes
10. Maîtriser les permissions classiques
11. Comprendre la notation numérique des permissions
12. Modifier les permissions avec `chmod`
13. Modifier le propriétaire et le groupe
14. Comprendre l'umask
15. Découvrir les permissions spéciales
16. Introduction aux ACL
17. Mesurer et contrôler l'espace de stockage
18. Rechercher et examiner les fichiers
19. Méthode de dépannage des problèmes d'accès
20. Travaux pratiques guidés
21. Exercices d'évaluation corrigés
22. Fiche de révision des commandes
23. Challenge final : préparer un espace de stockage partagé
24. Correction détaillée du challenge
25. Checklist finale des compétences


# 1. Présentation du cours et objectifs pédagogiques

Un système Linux peut contenir des milliers de fichiers : documents, journaux, applications, bibliothèques, configurations, données utilisateur et fichiers utilisés par les services.

Ces fichiers doivent être organisés, accessibles aux utilisateurs autorisés et protégés contre les modifications non souhaitées.

Le système de fichiers constitue l'un des mécanismes fondamentaux de Linux. Il permet d'organiser les données et de les retrouver à travers une arborescence.

Les permissions déterminent ensuite quelles opérations les utilisateurs peuvent réaliser sur les fichiers et les répertoires.

Enfin, les disques, les partitions, les systèmes de fichiers et les points de montage permettent de rendre le stockage disponible dans cette arborescence.

Ces notions sont directement liées : un fichier peut exister sur un disque, appartenir à un utilisateur, posséder des permissions correctes et rester inaccessible si un répertoire parent ne peut pas être traversé.

Ce cours vous apprend à comprendre ces relations et à les diagnostiquer.

## 1.1 Compétences à acquérir

À la fin du cours, vous devrez être capable de :

- Expliquer ce qu'est un système de fichiers.
- Naviguer dans l'arborescence Linux.
- Reconnaître les répertoires système importants.
- Distinguer un disque, une partition et un système de fichiers.
- Comprendre le rôle d'un point de montage.
- Identifier les systèmes de fichiers montés.
- Comprendre la notion d'inode.
- Distinguer un lien physique d'un lien symbolique.
- Identifier le propriétaire et le groupe d'un fichier.
- Lire les permissions affichées par `ls -l`.
- Comprendre les permissions de lecture, d'écriture et d'exécution.
- Utiliser `chmod` pour modifier les permissions.
- Comprendre et utiliser la notation numérique, notamment `600`, `640`, `644`, `700`, `750` et `755`.
- Utiliser `chown` et `chgrp` pour modifier les propriétaires et groupes.
- Comprendre le rôle de l'umask.
- Examiner l'espace disponible et l'espace utilisé.
- Diagnostiquer les erreurs courantes liées aux permissions et aux montages.

## 1.2 La méthode d'apprentissage

Chaque notion sera abordée selon le cycle suivant :

```text
+--------------------------------------+
| 1. COMPRENDRE LE CONCEPT              |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 2. OBSERVER UN EXEMPLE                |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 3. EXECUTER LES COMMANDES             |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 4. INTERPRETER LE RESULTAT            |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 5. REALISER UN EXERCICE               |
+--------------------------------------+
                  |
                  v
+--------------------------------------+
| 6. VERIFIER LA COMPREHENSION          |
+--------------------------------------+
```

Le but n'est pas de mémoriser mécaniquement les commandes. Il faut comprendre leurs effets et savoir vérifier si le résultat correspond à l'objectif.

## 1.3 Précautions importantes

Certaines opérations liées au stockage sont potentiellement destructives.

Pendant ce cours :

- Travaillez dans un répertoire de test.
- Ne modifiez pas les permissions de fichiers système au hasard.
- Ne formatez jamais un disque sans avoir identifié précisément le périphérique.
- Ne supprimez pas un répertoire avant d'avoir vérifié son contenu.
- Ne modifiez pas `/etc/fstab` sur une machine importante sans procédure de retour arrière.
- N'utilisez pas `chmod 777` comme solution automatique aux problèmes d'accès.
- Ne lancez pas `chown -R` sur une grande arborescence sans comprendre précisément les conséquences.

Les commandes les plus sensibles seront expliquées avant d'être utilisées.


# 2. Comprendre le système de fichiers Linux

## 2.1 Qu'est-ce qu'un système de fichiers ?

Un système de fichiers est un mécanisme qui permet d'organiser, de retrouver et de gérer des données stockées.

Il définit notamment la manière dont les fichiers et les répertoires sont représentés et comment certaines métadonnées sont conservées.

Ces métadonnées peuvent inclure :

- La taille du fichier.
- Les permissions.
- Le propriétaire.
- Le groupe.
- Les horodatages.
- Les références aux données du fichier.
- Les informations nécessaires à la gestion des entrées du répertoire.

Les détails varient selon le système de fichiers utilisé.

Sous Linux, on rencontre notamment :

- `ext4`
- `XFS`
- `Btrfs`
- `FAT32` ou des systèmes dérivés de FAT
- `exFAT`
- `NTFS` dans des environnements compatibles
- Des systèmes de fichiers réseau comme NFS

Ces systèmes de fichiers ne possèdent pas tous les mêmes fonctionnalités. Par exemple, la prise en charge des permissions Unix, des ACL, des snapshots ou des mécanismes de contrôle d'intégrité peut varier.

## 2.2 Pourquoi un système de fichiers est-il nécessaire ?

Un disque brut est constitué d'un espace de stockage qui ne possède pas automatiquement l'organisation nécessaire à la gestion habituelle des fichiers.

Pour stocker des fichiers de manière conventionnelle, il faut généralement créer ou utiliser une structure adaptée.

### Schéma simplifié

```text
+----------------------------------+
| Disque de stockage               |
| Capable de conserver des donnees |
+----------------------------------+
                |
                v
+----------------------------------+
| Partition ou volume              |
| Espace delimite pour un usage    |
+----------------------------------+
                |
                v
+----------------------------------+
| Systeme de fichiers              |
| Exemple : ext4                   |
+----------------------------------+
                |
                v
+----------------------------------+
| Fichiers et repertoires          |
| notes.txt, Documents/, etc.      |
+----------------------------------+
```

Ce schéma représente un cas courant, mais il ne décrit pas toutes les architectures possibles.

Un système de fichiers peut aussi être utilisé sur un volume logique, un périphérique chiffré, un volume réseau ou d'autres types de périphériques.

## 2.3 Le système de fichiers ne se limite pas au disque

Sous Linux, le terme « système de fichiers » peut aussi désigner des interfaces qui exposent des informations ou des objets du noyau.

Exemples :

- `/proc` expose de nombreuses informations sur les processus et le noyau.
- `/sys` expose des informations sur les périphériques et les sous-systèmes.
- `/dev` contient des entrées permettant d'accéder à des périphériques ou mécanismes spéciaux.
- `/run` contient notamment des données d'exécution temporaires.

Ces répertoires ne correspondent pas nécessairement à des fichiers ordinaires stockés sur le disque comme les documents d'un utilisateur.

Certains utilisent des systèmes de fichiers virtuels fournis par le noyau.

## 2.4 Comprendre la différence entre fichier et contenu

Il faut distinguer :

- Le nom utilisé pour retrouver un fichier.
- Les métadonnées qui décrivent le fichier.
- Les données contenues dans le fichier.
- L'entrée de répertoire qui associe un nom à un objet du système de fichiers.

Cette distinction est importante pour comprendre les liens physiques, les inodes et les permissions.

Un nom de fichier est une référence pratique. Il n'est pas nécessairement l'identité complète des données stockées.

## 2.5 Exemple simple

Dans le répertoire suivant :

```text
/home/alice/Documents/
|
+-- rapport.txt
+-- notes.txt
+-- projet/
    +-- README.md
```

Les noms `rapport.txt`, `notes.txt`, `projet` et `README.md` représentent des entrées accessibles dans une arborescence.

Le contenu de chaque fichier est géré par le système de fichiers auquel il appartient.

La permission de parcourir les répertoires est essentielle pour atteindre les fichiers situés dans cette arborescence.


# 3. Explorer l'arborescence des répertoires

Sous Linux, les fichiers sont organisés dans une arborescence qui commence à la racine `/`.

Contrairement à une organisation basée sur des lecteurs tels que `C:` ou `D:`, l'arborescence Linux présente les fichiers à partir d'une racine commune.

## 3.1 La racine `/`

La racine est le point de départ de l'arborescence.

```text
/
|
+-- home/
+-- etc/
+-- var/
+-- usr/
+-- tmp/
+-- dev/
+-- proc/
+-- sys/
```

Le contenu exact dépend de la distribution.

Pour afficher la racine :

```bash
ls /
```

Pour vérifier le répertoire courant :

```bash
pwd
```

Pour revenir à la racine :

```bash
cd /
```

## 3.2 Les répertoires essentiels

### `/home`

Contient généralement les répertoires personnels des utilisateurs ordinaires.

Exemple :

```text
/home/
|
+-- alice/
|   +-- Documents/
|   +-- Images/
|   +-- Projets/
|
+-- bob/
    +-- Documents/
```

### `/etc`

Contient de nombreux fichiers de configuration.

Exemples :

```text
/etc/hostname
/etc/hosts
/etc/passwd
/etc/group
```

Les fichiers de ce répertoire ne doivent pas être modifiés sans comprendre leur rôle.

### `/var`

Contient diverses données variables, notamment des journaux, caches et files d'attente selon la configuration.

Exemple :

```text
/var/
|
+-- log/
+-- cache/
+-- tmp/
```

### `/tmp`

Sert à stocker des fichiers temporaires.

Les règles de nettoyage et de conservation dépendent du système. Ne supposez pas que tout son contenu sera conservé indéfiniment.

### `/usr`

Contient une grande partie des logiciels, bibliothèques et ressources installés.

Exemples :

```text
/usr/bin/
/usr/sbin/
/usr/share/
```

### `/dev`

Contient des entrées représentant des périphériques ou des mécanismes spéciaux.

Exemples :

```text
/dev/null
/dev/zero
/dev/sda
```

Les noms de périphériques de stockage peuvent varier d'une machine à l'autre.

### `/mnt` et `/media`

Ces répertoires servent souvent de points de montage.

- `/mnt` est couramment utilisé pour des montages temporaires ou administratifs.
- `/media` est souvent utilisé pour des supports amovibles, selon l'environnement.

Il ne s'agit pas de règles absolues : les points de montage peuvent être choisis selon l'organisation du système.

## 3.3 Schéma récapitulatif

```text
/
|
+-- home       Donnees personnelles
|
+-- etc        Configuration
|
+-- var        Donnees variables et journaux
|
+-- tmp        Fichiers temporaires
|
+-- usr        Logiciels et ressources
|
+-- dev        Peripheriques et mecanismes speciaux
|
+-- proc       Informations liees aux processus et au noyau
|
+-- sys        Informations sur les peripheriques et sous-systemes
|
+-- mnt        Montages temporaires ou administratifs
|
+-- media      Supports amovibles selon l'environnement
```

## 3.4 Chemins absolus et chemins relatifs

Un chemin absolu commence par `/`.

Exemple :

```text
/home/alice/Documents/rapport.txt
```

Il décrit l'emplacement à partir de la racine.

Un chemin relatif dépend du répertoire courant.

Si vous vous trouvez dans :

```text
/home/alice
```

alors :

```text
Documents/rapport.txt
```

désigne le même fichier.

Les symboles suivants sont utiles :

```text
.   Repertoire courant
..  Repertoire parent
~   Repertoire personnel dans les Shells courants
```

## 3.5 Afficher le contenu d'un répertoire

```bash
ls
```

Affiche les entrées du répertoire courant.

```bash
ls -l
```

Affiche une liste détaillée.

```bash
ls -la
```

Inclut également les entrées cachées et fournit des détails.

```bash
ls -lh
```

Utilise un affichage lisible des tailles lorsqu'il est pris en charge.

Pour examiner un répertoire précis :

```bash
ls -lah /var/log
```

## 3.6 Pourquoi les fichiers cachés ne sont-ils pas nécessairement secrets ?

Sous Linux, les noms qui commencent par un point sont généralement masqués dans l'affichage normal de `ls`.

Exemples :

```text
.bashrc
.profile
.gitconfig
```

Le caractère initial est une convention de nommage. Il ne protège pas le fichier par lui-même.

Pour afficher ces entrées :

```bash
ls -la
```

La protection des données dépend des permissions et des autres mécanismes de sécurité, pas du fait que le nom commence par un point.


# 4. Comprendre les noms et les types de fichiers

Tous les objets présents dans l'arborescence ne sont pas des fichiers ordinaires.

Linux prend en charge plusieurs types d'entrées, chacun ayant des caractéristiques particulières.

## 4.1 Les types courants

Les principaux types sont :

- Fichier ordinaire.
- Répertoire.
- Lien symbolique.
- Périphérique bloc.
- Périphérique caractère.
- Tube nommé, ou FIFO.
- Socket Unix.

Les types disponibles et leurs propriétés dépendent de l'interface et du système de fichiers.

## 4.2 Identifier un fichier avec `file`

La commande `file` examine le contenu ou la structure d'un objet pour estimer son type.

```bash
file notes.txt
```

Exemples possibles de résultats :

```text
notes.txt: ASCII text
```

ou :

```text
image.png: PNG image data
```

Le résultat dépend du contenu réel du fichier et des règles d'identification utilisées.

L'extension d'un nom n'est pas une preuve que le contenu correspond au format attendu.

## 4.3 Examiner les métadonnées avec `stat`

```bash
stat notes.txt
```

La commande fournit des informations comme :

- Le type et le nom.
- La taille.
- Le nombre de liens physiques.
- L'identifiant d'inode.
- Les permissions.
- Le propriétaire.
- Le groupe.
- Les horodatages.

Le format exact dépend de la version de `stat` et du système.

## 4.4 Pourquoi les métadonnées sont-elles importantes ?

Imaginons deux fichiers de même taille.

L'un peut être lisible par tous, l'autre réservé à son propriétaire. Ils peuvent avoir des propriétaires différents, des horodatages différents ou des relations de liens différentes.

La taille du contenu ne suffit donc pas à comprendre les propriétés d'un fichier.

Les métadonnées permettent de vérifier l'identité, l'accès et l'état d'un objet.


# 5. Comprendre les disques, partitions et systèmes de fichiers

Avant de travailler sur le stockage, il faut comprendre les couches principales qui interviennent.

## 5.1 Le disque ou périphérique de stockage

Le périphérique de stockage est le support sur lequel les données peuvent être conservées.

Il peut s'agir d'un disque dur, d'un SSD, d'un périphérique NVMe, d'un stockage virtuel ou d'un autre support.

Exemples de noms sous Linux :

```text
/dev/sda
/dev/sdb
/dev/nvme0n1
```

Ces exemples ne sont pas universels. Les noms dépendent du matériel, du pilote et de l'environnement.

**Ne choisissez jamais un disque uniquement à partir d'un nom mémorisé.** Vérifiez sa taille, son modèle, ses partitions et son rôle.

## 5.2 Qu'est-ce qu'une partition ?

Une partition représente une région délimitée d'un périphérique de stockage.

Un même disque peut contenir plusieurs partitions.

```text
+--------------------------------------------------+
| Disque : /dev/sda                                |
+--------------------------------------------------+
| Partition 1 : /dev/sda1                           |
+--------------------------------------------------+
| Partition 2 : /dev/sda2                           |
+--------------------------------------------------+
| Partition 3 : /dev/sda3                           |
+--------------------------------------------------+
```

Le nombre de partitions dépend de l'organisation choisie.

Une partition peut contenir un système de fichiers, être utilisée pour du swap ou participer à une autre configuration de stockage.

## 5.3 Qu'est-ce qu'un système de fichiers ?

Le système de fichiers permet de gérer des fichiers et des répertoires sur un espace de stockage.

Exemples :

- `ext4`
- `XFS`
- `Btrfs`
- `vfat`
- `exfat`
- `ntfs`, dans les environnements qui le prennent en charge

Le choix du système de fichiers doit dépendre des besoins, de la distribution, des fonctionnalités recherchées et de l'environnement.

## 5.4 La différence entre disque, partition et système de fichiers

```text
DISQUE
  |
  +-- PARTITION
          |
          +-- SYSTEME DE FICHIERS
                    |
                    +-- Fichiers
                    +-- Repertoires
                    +-- Metadonnees
```

Ce modèle est courant, mais il existe d'autres organisations, notamment LVM, le chiffrement, le RAID et le stockage réseau.

Un système de fichiers peut être placé sur un volume logique ou un périphérique virtuel plutôt que directement sur une partition traditionnelle.

## 5.5 Examiner les périphériques avec `lsblk`

```bash
lsblk
```

Cette commande affiche les périphériques de stockage en mode bloc et leurs relations.

Pour obtenir davantage d'informations sur les systèmes de fichiers :

```bash
lsblk -f
```

Selon la configuration, la sortie peut inclure :

- Le nom du périphérique.
- La taille.
- Le type de périphérique.
- Le système de fichiers.
- L'UUID.
- Le point de montage.

Exemple illustratif :

```text
NAME        FSTYPE   SIZE MOUNTPOINTS
sda                  40G
+--sda1     ext4     39G /
+--sda2     swap      1G [SWAP]
```

Cette sortie est fictive. Les noms, les tailles et les points de montage peuvent varier.

## 5.6 Identifier les systèmes de fichiers avec `blkid`

```bash
sudo blkid
```

Affiche des informations relatives aux systèmes de fichiers identifiés sur les périphériques de bloc, lorsque les informations sont accessibles.

Pour interroger un périphérique précis :

```bash
sudo blkid /dev/sda1
```

**Précaution :** `/dev/sda1` est un exemple. Vérifiez l'identité réelle du périphérique avant d'interroger ou de modifier un support de stockage.

La commande `blkid` est utilisée pour examiner des informations. Elle ne doit pas être confondue avec un outil de création ou de formatage.

## 5.7 Pourquoi ne pas formater un disque pendant l'apprentissage ?

Le formatage crée généralement une structure de système de fichiers sur un support ou une partition.

Une erreur de cible peut détruire les données existantes.

Il faut donc vérifier :

1. Le périphérique exact.
2. La taille du périphérique.
3. Les partitions présentes.
4. Le contenu éventuel.
5. Le besoin réel de formatage.
6. La présence de sauvegardes.
7. L'impact sur les applications.

Ce cours n'exige aucun formatage. Toutes les notions peuvent être apprises avec des répertoires de test et des commandes d'observation.


# 6. Comprendre les points de montage

## 6.1 Qu'est-ce qu'un point de montage ?

Sous Linux, un système de fichiers doit généralement être monté dans l'arborescence pour que son contenu soit accessible par un chemin.

Le répertoire utilisé pour rendre ce contenu accessible est appelé point de montage.

Exemple :

```text
Périphérique :
/dev/sdb1

Système de fichiers :
ext4

Point de montage :
/srv/donnees
```

Les fichiers du système de fichiers deviennent alors accessibles à travers le chemin `/srv/donnees`.

## 6.2 Schéma de montage

```text
+--------------------------------+
| Peripherique /dev/sdb1         |
+--------------------------------+
                 |
                 v
+--------------------------------+
| Systeme de fichiers ext4       |
+--------------------------------+
                 |
                 v
+--------------------------------+
| Montage dans l'arborescence    |
| /srv/donnees                   |
+--------------------------------+
                 |
                 v
+--------------------------------+
| /srv/donnees/rapport.txt       |
| /srv/donnees/archives/         |
+--------------------------------+
```

Le périphérique reste identifié par son chemin de périphérique ou d'autres identifiants disponibles. Le point de montage donne un chemin dans l'arborescence Linux.

## 6.3 Afficher les systèmes de fichiers montés

```bash
findmnt
```

Cette commande affiche une vue des systèmes de fichiers montés.

Pour examiner le système de fichiers associé à un chemin :

```bash
findmnt /
```

Ou :

```bash
findmnt /home
```

La sortie dépend de la configuration.

## 6.4 Comprendre la différence entre `lsblk` et `findmnt`

`lsblk` montre l'organisation des périphériques de stockage.

`findmnt` montre les relations de montage.

Exemple conceptuel :

```text
lsblk
  |
  +-- Identifie les peripheriques et partitions
  |
  +-- Affiche les relations de stockage

findmnt
  |
  +-- Affiche les montages actifs
  |
  +-- Relie les systemes de fichiers aux chemins
```

Un périphérique peut exister sans être monté.

Un système peut également utiliser des couches virtuelles, des montages réseau ou d'autres mécanismes qui rendent le résultat plus complexe qu'une relation simple entre un disque et un répertoire.

## 6.5 Un répertoire peut-il contenir des fichiers avant un montage ?

Oui.

Supposons que `/srv/donnees` soit un répertoire ordinaire qui contient déjà un fichier :

```text
/srv/donnees/
|
+-- ancien-fichier.txt
```

Si un autre système de fichiers est ensuite monté sur `/srv/donnees`, le contenu du système de fichiers monté devient visible à ce chemin.

Le fichier précédent n'est généralement pas supprimé par le montage, mais il peut devenir masqué tant que le montage est actif.

C'est pourquoi il faut vérifier le contenu d'un point de montage avant d'y monter un système de fichiers.

## 6.6 Examiner un montage avec `df`

```bash
df -h
```

Cette commande affiche l'utilisation des systèmes de fichiers montés.

Pour examiner le système de fichiers auquel appartient un chemin :

```bash
df -h /srv
```

Si le chemin n'existe pas ou n'est pas accessible, la commande peut échouer.

## 6.7 Monter et démonter : notions essentielles

La commande `mount` permet de monter un système de fichiers.

La commande `umount` permet de demander le démontage.

Exemple conceptuel :

```bash
sudo mount PERIPHERIQUE POINT_DE_MONTAGE
```

Puis :

```bash
sudo umount POINT_DE_MONTAGE
```

Ces commandes ne doivent pas être exécutées sans avoir identifié la source, le type de système de fichiers, le point de montage et les données présentes.

Le cours ne nécessite pas de monter ou de démonter un véritable périphérique.

## 6.8 Pourquoi un démontage peut-il échouer ?

Un système de fichiers peut être considéré comme occupé lorsque des processus utilisent des ressources situées sous son point de montage.

Exemples :

- Un terminal dont le répertoire courant se trouve sous le point de montage.
- Une application qui garde un fichier ouvert.
- Un processus qui utilise des données dans ce système de fichiers.

Dans ce cas, il faut identifier les utilisateurs du montage et comprendre la situation avant de tenter une autre opération.

Forcer un démontage sans comprendre les conséquences peut perturber une application ou risquer une incohérence opérationnelle.

## 6.9 Le fichier `/etc/fstab`

`/etc/fstab` contient des informations sur des systèmes de fichiers et leurs options de montage.

Une entrée comprend généralement :

```text
source  point_de_montage  type  options  dump  pass
```

Le fichier peut inclure des systèmes de fichiers locaux, des montages réseau ou d'autres ressources.

Une ligne illustrative :

```text
UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx /srv/donnees ext4 defaults 0 2
```

Cette ligne est uniquement un exemple de structure.

**Ne la copiez pas telle quelle.** L'UUID, le système de fichiers, les options et le point de montage doivent correspondre à la réalité de votre machine.

Une erreur dans `/etc/fstab` peut empêcher le montage attendu ou compliquer le démarrage. Toute modification doit être préparée et vérifiée.


# 7. Identifier les fichiers avec les inodes

Les inodes constituent un concept essentiel pour comprendre les systèmes de fichiers de type Unix, notamment les systèmes de fichiers locaux courants.

## 7.1 Qu'est-ce qu'un inode ?

Un inode est une structure de métadonnées utilisée par de nombreux systèmes de fichiers Unix.

Selon le système de fichiers, il peut notamment référencer :

- Le type d'objet.
- Les permissions.
- Le propriétaire.
- Le groupe.
- Les horodatages.
- La taille.
- Des références aux données.
- Le nombre de liens physiques.

Le nom d'un fichier n'est généralement pas stocké comme simple propriété de son inode : le répertoire associe un nom à une entrée du système de fichiers.

## 7.2 Schéma conceptuel

```text
+--------------------------------+
| Repertoire Documents           |
+--------------------------------+
| notes.txt   ------------+      |
| rapport.txt --------+   |      |
+---------------------|---|------+
                      |   |
                      v   v
                 +------------+
                 | Inode      |
                 +------------+
                 | Type       |
                 | Proprietaire|
                 | Permissions|
                 | Taille     |
                 | Metadonnees|
                 +------------+
                      |
                      v
                 +------------+
                 | Donnees    |
                 | du fichier |
                 +------------+
```

Le schéma simplifie le fonctionnement réel et suppose des entrées pointant vers le même inode dans le cas illustré.

Tous les systèmes de fichiers ne gèrent pas les objets exactement de la même façon.

## 7.3 Afficher l'inode avec `ls -i`

```bash
ls -i notes.txt
```

La commande affiche généralement le numéro d'inode associé au fichier sur un système de fichiers qui expose cette information.

Exemple fictif :

```text
123456 notes.txt
```

Le numéro réel dépend du système de fichiers.

## 7.4 Examiner l'inode avec `stat`

```bash
stat notes.txt
```

La sortie peut inclure :

```text
File: notes.txt
Size: 128
Inode: 123456
Links: 1
```

Ces valeurs sont fictives et illustratives.

## 7.5 Pourquoi l'inode est-il utile ?

La notion d'inode explique notamment :

- Le fait que plusieurs noms puissent pointer vers le même fichier.
- La différence entre un lien physique et un lien symbolique.
- La présence d'un fichier accessible par plusieurs chemins.
- Certaines situations où un fichier supprimé du répertoire reste utilisé par un processus.
- La distinction entre un nom et l'objet de stockage auquel il fait référence.

Il faut cependant connaître les limites de ce concept : tous les systèmes de fichiers n'ont pas les mêmes caractéristiques internes et la représentation des inodes n'est pas universelle.


# 8. Comprendre les liens physiques et symboliques

Linux permet d'associer plusieurs chemins à un même contenu ou de créer une référence vers un autre chemin.

Les deux mécanismes principaux étudiés ici sont les liens physiques et les liens symboliques.

## 8.1 Le lien physique

Un lien physique, ou *hard link*, est une entrée de répertoire qui pointe vers le même inode qu'une autre entrée, sur le système de fichiers concerné.

Exemple :

```bash
ln notes.txt notes-physique.txt
```

Cette commande crée un lien physique appelé `notes-physique.txt` vers le même objet de fichier que `notes.txt`, lorsque le système de fichiers et les permissions le permettent.

## 8.2 Comprendre le lien physique

```text
+----------------------------+
| notes.txt                  |
+----------------------------+
              |
              v
          +--------+
          | Inode  |
          +--------+
              ^
              |
+----------------------------+
| notes-physique.txt         |
+----------------------------+
```

Les deux noms pointent vers le même inode dans le modèle illustré.

Ils ne représentent pas deux copies indépendantes des données.

Si le contenu est modifié via l'un des deux noms, le changement est visible par l'autre nom, puisque les deux entrées référencent le même objet.

## 8.3 Tester un lien physique

Dans un répertoire de test :

```bash
echo "Premiere version" > notes.txt
ln notes.txt notes-physique.txt
```

Vérifiez les inodes :

```bash
ls -li notes.txt notes-physique.txt
```

Les deux noms devraient normalement afficher le même numéro d'inode lorsqu'ils résident sur le même système de fichiers et que le lien physique a été créé avec succès.

Modifiez ensuite le fichier par l'un des noms :

```bash
echo "Modification partagee" >> notes.txt
```

Lisez l'autre nom :

```bash
cat notes-physique.txt
```

Vous devez retrouver le contenu modifié.

## 8.4 Limites du lien physique

Les liens physiques ordinaires ne permettent généralement pas :

- De créer un lien vers un répertoire ordinaire.
- De créer un lien physique traversant deux systèmes de fichiers distincts.

Les restrictions précises dépendent du système de fichiers et du mécanisme utilisé.

## 8.5 Le lien symbolique

Un lien symbolique, ou *symlink*, est un type d'entrée qui référence un chemin.

Pour créer un lien symbolique :

```bash
ln -s notes.txt notes-symbolique.txt
```

Le lien contient une référence vers le chemin cible.

### Schéma

```text
+----------------------------+
| notes-symbolique.txt       |
| Type : lien symbolique     |
+----------------------------+
              |
              | Reference vers le chemin
              v
+----------------------------+
| notes.txt                  |
| Fichier cible              |
+----------------------------+
```

Le lien symbolique ne constitue pas une copie des données du fichier cible.

Il peut référencer un fichier ou un répertoire.

## 8.6 Tester un lien symbolique

```bash
echo "Document de test" > notes.txt
ln -s notes.txt notes-symbolique.txt
```

Examinez les entrées :

```bash
ls -l notes.txt notes-symbolique.txt
```

Le lien symbolique apparaît généralement avec un `l` au début des permissions et une indication de la cible.

Affichez son contenu via le lien :

```bash
cat notes-symbolique.txt
```

Si le chemin cible est valide et accessible, le contenu du fichier cible s'affiche.

## 8.7 Lien symbolique cassé

Un lien symbolique devient cassé lorsque son chemin cible ne peut plus être résolu.

Exemple :

```bash
ln -s fichier-absent.txt lien-casse.txt
```

Le lien peut être créé même si le fichier cible n'existe pas, mais les opérations qui tentent d'accéder à la cible échoueront.

Vérifiez :

```bash
ls -l lien-casse.txt
```

Un lien symbolique cassé ne signifie pas forcément que le système de fichiers est endommagé.

Il peut simplement référencer un chemin absent.

## 8.8 Comparer les deux types de liens

| Caractéristique | Lien physique | Lien symbolique |
|---|---|---|
| Objet référencé | Même inode que l'autre entrée | Chemin cible |
| Copie indépendante des données | Non | Non |
| Peut référencer un répertoire | Généralement non pour les usages ordinaires | Oui |
| Peut traverser des systèmes de fichiers | Non, dans le cas courant | Oui, si la cible est accessible |
| Cible absente | Le lien conserve l'objet référencé | Peut devenir cassé |
| Affichage courant | Même inode pour les liens ordinaires d'un même système de fichiers | Type lien symbolique avec cible |

## 8.9 Attention à `rm` avec les liens

Supprimer un nom ne signifie pas nécessairement que toutes les références à l'objet disparaissent.

Avec un lien physique, l'objet peut rester accessible via un autre nom.

Avec un lien symbolique, supprimer le lien supprime normalement l'entrée du lien, pas le fichier cible.

Exemple :

```bash
rm lien-symbolique.txt
```

Cette commande supprime l'entrée `lien-symbolique.txt`.

Elle ne doit pas être utilisée sans vérifier le chemin et l'objet visé.

## 8.10 Atelier sur les liens

Dans un répertoire de test, exécutez :

```bash
mkdir -p ~/storage-lab/liens
cd ~/storage-lab/liens

echo "Contenu initial" > source.txt

ln source.txt lien-physique.txt
ln -s source.txt lien-symbolique.txt

ls -li
```

Puis :

```bash
echo "Nouvelle ligne" >> source.txt
cat lien-physique.txt
cat lien-symbolique.txt
```

Expliquez pourquoi les deux lectures peuvent afficher la modification.


# 9. Comprendre les propriétaires et les groupes

Chaque fichier possède un propriétaire et un groupe associé dans le modèle classique des permissions Unix.

Ces informations influencent les droits d'accès accordés à l'utilisateur, au groupe et aux autres.

## 9.1 Le propriétaire

Le propriétaire est l'utilisateur associé au fichier.

Exemple :

```text
-rw-r--r-- 1 alice support 250 Oct 24 09:00 rapport.txt
```

Ici, `alice` est le propriétaire.

Le propriétaire peut généralement être affiché à l'aide de :

```bash
ls -l rapport.txt
```

## 9.2 Le groupe associé

Le groupe associé au fichier est utilisé pour la catégorie de permissions `g`.

Dans l'exemple :

```text
-rw-r--r-- 1 alice support 250 Oct 24 09:00 rapport.txt
```

le groupe est `support`.

Les membres du groupe sont déterminés par les informations de comptes et groupes du système, ainsi que par les mécanismes d'identification applicables.

## 9.3 Afficher l'identité courante

```bash
whoami
```

Affiche le nom de l'utilisateur effectif.

```bash
id
```

Affiche des informations sur l'identifiant de l'utilisateur et ses groupes.

```bash
groups
```

Affiche généralement les groupes associés à l'utilisateur courant.

## 9.4 Pourquoi les groupes sont-ils utiles ?

Supposons qu'une équipe de support doive partager des documents.

Sans groupes, il faudrait configurer les accès individuellement de manière répétée.

Avec un groupe :

```text
+--------------------------------+
| Groupe : support               |
+--------------------------------+
       |             |
       v             v
+-------------+ +-------------+
| Alice       | | Bob         |
+-------------+ +-------------+
       |             |
       +------+------+
              |
              v
+--------------------------------+
| Repertoire partage              |
| Permissions adaptees au groupe  |
+--------------------------------+
```

Le groupe permet d'organiser les droits de manière plus cohérente.

## 9.5 Examiner le propriétaire et le groupe

```bash
ls -l rapport.txt
```

Pour davantage de détails :

```bash
stat rapport.txt
```

Le résultat dépend des permissions, des métadonnées et du système de fichiers.

## 9.6 Pourquoi un fichier peut-il être inaccessible à son propriétaire apparent ?

Les permissions classiques ne sont pas l'unique mécanisme pouvant intervenir.

Le chemin peut être bloqué par un répertoire parent. Une ACL ou une politique de sécurité peut aussi influencer l'accès.

Il faut examiner le fichier et son chemin d'accès complet.


# 10. Maîtriser les permissions classiques

Les permissions Linux permettent de déterminer les opérations autorisées sur un fichier ou un répertoire.

Le modèle classique distingue trois catégories et trois permissions principales.

## 10.1 Les trois catégories

- `u` : propriétaire (*user*).
- `g` : groupe (*group*).
- `o` : autres (*others*).

La notation `a` peut désigner l'ensemble des catégories dans certaines commandes de modification des permissions.

## 10.2 Les trois permissions

| Symbole | Signification | Fichier ordinaire | Répertoire |
|---|---|---|---|
| `r` | Read | Lire le contenu | Lire la liste des entrées, sous réserve des autres droits |
| `w` | Write | Modifier le contenu | Modifier les entrées, en général avec `x` |
| `x` | Execute | Exécuter le fichier si cela est applicable | Traverser le répertoire et accéder aux objets par leur chemin |

Ces significations doivent être comprises séparément pour les fichiers ordinaires et les répertoires.

## 10.3 Permissions sur un fichier

Considérons :

```text
-rw-r--r--
```

Découpage :

```text
- rw- r-- r--
|  |   |   |
|  |   |   +-- Autres utilisateurs
|  |   +------ Groupe
|  +---------- Proprietaire
+------------- Type d'entree
```

Interprétation :

- Le propriétaire peut lire et écrire.
- Le groupe peut lire.
- Les autres peuvent lire.
- Aucune des trois catégories ne possède la permission classique d'exécution.

## 10.4 Permissions sur un répertoire

Pour un répertoire, les permissions ont une signification particulière.

### `r` — lire

Permet généralement de consulter la liste des noms contenus dans le répertoire.

### `w` — écrire

Permet de modifier les entrées du répertoire, généralement en combinaison avec `x`.

Cela peut permettre de créer, supprimer ou renommer des entrées selon les autres contrôles applicables.

### `x` — traverser

Permet d'utiliser le répertoire comme élément d'un chemin et d'accéder aux objets dont le nom est connu, sous réserve des autres permissions.

### Exemple

```text
/srv/support/
|
+-- rapport.txt
+-- notes.txt
```

Même si `rapport.txt` possède une permission de lecture, il peut être impossible de l'atteindre si un répertoire parent ne permet pas sa traversée.

## 10.5 Pourquoi `rwx` ne signifie-t-il pas la même chose partout ?

Sur un fichier ordinaire :

- `r` correspond à la lecture du contenu.
- `w` correspond à la modification du contenu.
- `x` correspond à l'exécution lorsque cela est applicable.

Sur un répertoire :

- `r` concerne la liste des entrées.
- `w` concerne la modification des entrées.
- `x` concerne la traversée du répertoire.

Cette différence explique de nombreux problèmes de permissions.

## 10.6 Examiner les permissions avec `ls -l`

```bash
ls -l
```

Exemple :

```text
-rw-r----- 1 alice support 512 Oct 24 10:00 secret.txt
```

Interprétation :

```text
-rw-r-----
|
+-- -       -> fichier ordinaire
    rw-     -> proprietaire
       r--  -> groupe
          --- -> autres
```

Dans cet exemple :

- Alice peut lire et modifier le fichier.
- Les membres du groupe concerné disposent de la lecture classique.
- Les autres n'ont aucune permission classique.

Les ACL et autres mécanismes peuvent cependant influencer les accès réels.

## 10.7 Le droit d'exécution d'un script

Un script Shell ne doit pas nécessairement être exécutable pour être lu ou interprété explicitement par Bash.

Exemple :

```bash
bash script.sh
```

Bash lit le fichier et exécute son contenu si les conditions d'accès le permettent.

Pour lancer directement le fichier :

```bash
./script.sh
```

il faut notamment que le fichier possède un droit d'exécution approprié et que le système puisse utiliser l'interpréteur prévu.

Pour ajouter la permission d'exécution au propriétaire :

```bash
chmod u+x script.sh
```

Le droit d'exécution n'est pas équivalent à la simple capacité de lire le fichier.


# 11. Comprendre la notation numérique des permissions

Les permissions peuvent être exprimées à l'aide de nombres octaux.

Cette représentation est pratique pour définir simultanément les permissions du propriétaire, du groupe et des autres.

## 11.1 Les valeurs de base

```text
r = 4
w = 2
x = 1
```

On additionne les valeurs des permissions attribuées à chaque catégorie.

## 11.2 Tableau de conversion

| Permissions | Calcul | Valeur |
|---|---:|---:|
| `---` | 0 | 0 |
| `--x` | 1 | 1 |
| `-w-` | 2 | 2 |
| `-wx` | 2 + 1 | 3 |
| `r--` | 4 | 4 |
| `r-x` | 4 + 1 | 5 |
| `rw-` | 4 + 2 | 6 |
| `rwx` | 4 + 2 + 1 | 7 |

Chaque chiffre correspond à une catégorie :

```text
XYZ
|||
||+-- Autres utilisateurs
|+--- Groupe
+---- Proprietaire
```

## 11.3 Comprendre `644`

```bash
chmod 644 fichier.txt
```

Le mode `644` signifie :

```text
6 = rw- pour le proprietaire
4 = r-- pour le groupe
4 = r-- pour les autres
```

La représentation classique est :

```text
rw-r--r--
```

C'est un mode courant pour un fichier texte non exécutable qui doit être modifiable par son propriétaire et lisible par les autres catégories.

Il ne convient pas nécessairement à tous les fichiers.

## 11.4 Comprendre `600`

```bash
chmod 600 secret.txt
```

Interprétation :

```text
6 = rw- pour le proprietaire
0 = --- pour le groupe
0 = --- pour les autres
```

Résultat :

```text
rw-------
```

Ce mode est utile lorsque la lecture et l'écriture classiques doivent être réservées au propriétaire.

Cela ne remplace pas une politique complète de protection des données.

## 11.5 Comprendre `755`

```bash
chmod 755 script.sh
```

Interprétation :

```text
7 = rwx pour le proprietaire
5 = r-x pour le groupe
5 = r-x pour les autres
```

Résultat :

```text
rwxr-xr-x
```

Le propriétaire peut lire, modifier et exécuter. Les autres catégories peuvent lire et exécuter.

Ce mode peut être approprié pour certains programmes ou scripts destinés à être exécutés par d'autres utilisateurs.

## 11.6 Comprendre `700`

```bash
chmod 700 dossier
```

Résultat :

```text
rwx------
```

Le propriétaire dispose de `rwx`. Les autres catégories n'ont aucune permission classique.

Pour un répertoire, cela signifie notamment que le propriétaire peut le parcourir, lire ses entrées et les modifier selon les autres contrôles.

## 11.7 Comprendre `750`

```bash
chmod 750 dossier
```

Résultat :

```text
rwxr-x---
```

Le propriétaire dispose de `rwx`.

Le groupe peut lire les entrées et traverser le répertoire.

Les autres n'ont aucune permission classique.

Cette configuration peut être utile pour un répertoire accessible à une équipe particulière.

## 11.8 Comparer les modes courants

| Mode | Propriétaire | Groupe | Autres | Exemple d'utilisation |
|---|---|---|---|---|
| `600` | `rw-` | `---` | `---` | Fichier privé |
| `640` | `rw-` | `r--` | `---` | Document lisible par un groupe |
| `644` | `rw-` | `r--` | `r--` | Document ordinaire lisible |
| `700` | `rwx` | `---` | `---` | Répertoire privé |
| `750` | `rwx` | `r-x` | `---` | Répertoire réservé à une équipe |
| `755` | `rwx` | `r-x` | `r-x` | Répertoire traversable ou programme public en lecture |
| `770` | `rwx` | `rwx` | `---` | Répertoire partagé entre propriétaire et groupe |

Le mode approprié dépend du contenu et du besoin réel.

## 11.9 Exercices de conversion

### Exercice A

Convertissez `640`.

**Correction :**

```text
6 -> rw-
4 -> r--
0 -> ---
```

Résultat :

```text
rw-r-----
```

### Exercice B

Convertissez `750`.

**Correction :**

```text
7 -> rwx
5 -> r-x
0 -> ---
```

Résultat :

```text
rwxr-x---
```

### Exercice C

Convertissez `444`.

**Correction :**

```text
4 -> r--
4 -> r--
4 -> r--
```

Résultat :

```text
r--r--r--
```

Ces permissions ne donnent aucune permission classique d'écriture. D'autres mécanismes, comme le propriétaire, les ACL et les contrôles de sécurité, peuvent intervenir.


# 12. Modifier les permissions avec `chmod`

La commande `chmod` permet de modifier les permissions classiques d'un fichier ou d'un répertoire.

Il existe deux méthodes principales :

- La notation numérique.
- La notation symbolique.

## 12.1 Modifier les permissions avec un nombre

Exemple :

```bash
chmod 640 rapport.txt
```

Le mode classique devient `rw-r-----`.

Vérifiez :

```bash
ls -l rapport.txt
```

## 12.2 Modifier les permissions avec une notation symbolique

La notation symbolique permet d'ajouter, de retirer ou de définir des permissions pour certaines catégories.

Les symboles principaux sont :

```text
u = proprietaire
g = groupe
o = autres
a = toutes les categories

r = lecture
w = ecriture
x = execution ou traversee
```

## 12.3 Ajouter une permission

```bash
chmod u+x script.sh
```

Ajoute la permission d'exécution au propriétaire.

Pour ajouter la lecture au groupe :

```bash
chmod g+r rapport.txt
```

Pour ajouter la lecture à toutes les catégories :

```bash
chmod a+r rapport.txt
```

Ces commandes modifient les permissions selon les options utilisées.

## 12.4 Retirer une permission

```bash
chmod o-w rapport.txt
```

Retire la permission d'écriture aux autres utilisateurs.

Pour retirer l'exécution au groupe :

```bash
chmod g-x script.sh
```

## 12.5 Définir explicitement certaines permissions

```bash
chmod u=rw,g=r,o= rapport.txt
```

Cette commande définit :

- `rw` pour le propriétaire.
- `r` pour le groupe.
- Aucune permission classique pour les autres.

Il s'agit d'une affectation explicite, pas simplement d'un ajout.

## 12.6 Comprendre `chmod -R`

L'option `-R` applique une modification récursive à une arborescence.

Exemple :

```bash
chmod -R 750 dossier-test
```

Cette commande applique récursivement le mode indiqué aux entrées de l'arborescence concernée selon le comportement de l'outil.

**Attention :** appliquer le même mode numérique à tous les éléments peut être inadapté, car les fichiers ordinaires et les répertoires n'ont pas les mêmes besoins en permissions.

Certains fichiers ordinaires pourraient devenir exécutables ou perdre une permission nécessaire.

Dans un exercice, il est préférable de modifier quelques fichiers de test plutôt qu'une grande arborescence.

## 12.7 Pourquoi `chmod 777` est-il risqué ?

```bash
chmod 777 fichier.txt
```

Cette commande attribue les permissions classiques `rwx` au propriétaire, au groupe et aux autres.

Pour un fichier ordinaire, cela peut permettre à d'autres utilisateurs de modifier son contenu ou de l'exécuter si le fichier est un programme interprétable ou exécutable dans le contexte concerné.

Pour un répertoire, cela peut permettre aux autres de consulter ses entrées, de le traverser et de tenter d'en modifier le contenu selon les règles applicables.

Cette commande est souvent trop permissive.

**Bonne méthode :** examinez les permissions, le propriétaire, le groupe et le chemin complet avant de décider de la modification nécessaire.

## 12.8 Atelier : gérer les permissions d'un fichier

Créez un répertoire de test :

```bash
mkdir -p ~/storage-lab/permissions
cd ~/storage-lab/permissions
```

Créez un fichier :

```bash
echo "Document de test" > document.txt
```

Examinez les permissions :

```bash
ls -l document.txt
```

Attribuez le mode `600` :

```bash
chmod 600 document.txt
```

Vérifiez :

```bash
ls -l document.txt
```

Puis attribuez le mode `644` :

```bash
chmod 644 document.txt
```

Vérifiez encore le résultat.

Vous devez pouvoir expliquer les différences entre les deux modes.


# 13. Modifier le propriétaire et le groupe

Les permissions et les catégories d'utilisateurs sont liées aux informations de propriétaire et de groupe.

Les commandes `chown` et `chgrp` permettent de modifier ces associations lorsque les privilèges nécessaires sont disponibles.

## 13.1 Modifier le propriétaire avec `chown`

La syntaxe générale est :

```bash
chown UTILISATEUR fichier
```

Exemple :

```bash
sudo chown alice rapport.txt
```

Cette commande demande que `alice` devienne propriétaire du fichier.

Elle nécessite les autorisations appropriées.

Il faut que le compte existe.

## 13.2 Modifier le propriétaire et le groupe

```bash
sudo chown alice:support rapport.txt
```

Cette commande définit le propriétaire sur `alice` et le groupe sur `support`, lorsque les conditions nécessaires sont réunies.

Vérifiez :

```bash
ls -l rapport.txt
```

## 13.3 Modifier uniquement le groupe avec `chgrp`

```bash
sudo chgrp support rapport.txt
```

Cette commande demande à affecter le fichier au groupe `support`.

Le droit de réaliser cette opération dépend notamment des permissions administratives et des règles applicables au compte.

## 13.4 Propriétaire et permissions : deux notions différentes

Changer le propriétaire ne signifie pas nécessairement que les permissions changent de façon à donner accès au nouvel utilisateur.

Le propriétaire et les permissions sont deux propriétés distinctes.

Exemple :

```text
Fichier : rapport.txt
Proprietaire : Alice
Groupe : support
Permissions : rw-------
```

Dans ce cas, les permissions classiques donnent `rw` à la catégorie du propriétaire et aucune permission classique au groupe ou aux autres.

Si le propriétaire change, les droits associés à la catégorie propriétaire continuent d'être interprétés selon le modèle classique.

Mais il faut toujours examiner les ACL, les répertoires parents et les autres mécanismes pour comprendre l'accès réel.

## 13.5 Le danger de `chown -R`

La commande :

```bash
sudo chown -R alice:support dossier
```

demande à modifier récursivement le propriétaire et le groupe de l'arborescence ciblée.

Elle peut être adaptée à certains scénarios, mais son effet peut être vaste.

Avant de l'exécuter :

1. Vérifiez le chemin avec `pwd` et `ls`.
2. Identifiez le contenu concerné.
3. Vérifiez les services qui utilisent ce contenu.
4. Confirmez le propriétaire et le groupe attendus.
5. Préparez un moyen de retour arrière si nécessaire.

Ne modifiez jamais récursivement les propriétaires de grands répertoires système sans comprendre leurs fonctions.

## 13.6 Atelier sur le propriétaire et le groupe

Dans un environnement de test où vous disposez d'un compte approprié, examinez :

```bash
id
ls -l ~/storage-lab/permissions/document.txt
stat ~/storage-lab/permissions/document.txt
```

Si plusieurs comptes de test sont disponibles, créez un fichier indépendant et observez les effets d'un changement de propriétaire avec les privilèges autorisés.

Le but est de comprendre la différence entre :

- Le compte qui possède le fichier.
- Le groupe associé.
- Les permissions accordées.
- L'identité du processus qui tente d'accéder au fichier.


# 14. Comprendre l'umask

Lorsque vous créez un fichier ou un répertoire, vous ne définissez pas nécessairement explicitement toutes les permissions.

Le Shell et le programme créateur utilisent des permissions de base, modifiées par l'umask.

## 14.1 Qu'est-ce que l'umask ?

L'umask est un masque de création qui retire certaines permissions des permissions initiales prévues.

Afficher sa valeur :

```bash
umask
```

Une valeur courante est :

```text
0022
```

Cette valeur est un exemple. Votre environnement peut utiliser un autre umask.

## 14.2 Permissions de base habituelles

Les bases courantes pour les programmes traditionnels sont :

```text
Fichier ordinaire : 666
Repertoire        : 777
```

Les fichiers ordinaires ne reçoivent donc normalement pas automatiquement la permission d'exécution dans ce modèle.

Le programme créateur peut également demander des permissions différentes, et les systèmes de fichiers ou d'autres mécanismes peuvent influencer le résultat final.

## 14.3 Exemple avec umask `022`

Pour un fichier ordinaire :

```text
Permissions de base : 666
Umask               : 022
Resultat habituel   : 644
```

Pour un répertoire :

```text
Permissions de base : 777
Umask               : 022
Resultat habituel   : 755
```

Le masque retire les permissions correspondantes.

## 14.4 Exemple avec umask `027`

Pour un fichier :

```text
Permissions de base : 666
Umask               : 027
Resultat habituel   : 640
```

Pour un répertoire :

```text
Permissions de base : 777
Umask               : 027
Resultat habituel   : 750
```

L'umask `027` empêche généralement le groupe d'obtenir l'écriture et retire toutes les permissions classiques aux autres dans les exemples présentés.

## 14.5 Modifier temporairement l'umask

Dans une session Bash de test :

```bash
umask 027
```

Créez un fichier :

```bash
touch fichier-umask.txt
```

Puis un répertoire :

```bash
mkdir dossier-umask
```

Vérifiez :

```bash
ls -l fichier-umask.txt
ls -ld dossier-umask
```

Comparez avec un second umask dans la même session :

```bash
umask 022
touch fichier-umask-022.txt
mkdir dossier-umask-022
```

Puis :

```bash
ls -l fichier-umask-022.txt
ls -ld dossier-umask-022
```

Les résultats habituels devraient correspondre aux valeurs expliquées, sous réserve des permissions demandées par les outils et des particularités du système.

## 14.6 Umask et permissions explicites

Il faut distinguer deux opérations :

- Créer un nouveau fichier avec une commande comme `touch`.
- Modifier les permissions d'un fichier existant avec `chmod`.

L'umask intervient normalement dans la création, par l'intermédiaire des permissions demandées au mécanisme de création.

Une commande explicite `chmod` définit ensuite les permissions classiques ciblées et ne fonctionne pas comme une nouvelle création soumise à l'umask de la même manière.

## 14.7 Atelier sur l'umask

Exécutez :

```bash
umask
```

Puis :

```bash
umask 027
touch ~/storage-lab/fichier-027.txt
mkdir ~/storage-lab/dossier-027
```

Vérifiez :

```bash
ls -l ~/storage-lab/fichier-027.txt
ls -ld ~/storage-lab/dossier-027
```

Ensuite :

```bash
umask 022
touch ~/storage-lab/fichier-022.txt
mkdir ~/storage-lab/dossier-022
```

Comparez les résultats.

**Précaution :** une modification d'umask dans la session courante ne change pas nécessairement les valeurs des autres sessions ou des services déjà lancés.


# 15. Découvrir les permissions spéciales

Les permissions numériques peuvent aussi contenir un chiffre supplémentaire correspondant à certains bits spéciaux.

Les mécanismes qui suivent sont importants pour comprendre certaines arborescences Linux, mais doivent être utilisés avec prudence.

## 15.1 Setgid

Sur un répertoire, le bit setgid peut favoriser l'héritage du groupe associé pour les nouvelles entrées créées dans ce répertoire.

Exemple :

```bash
chmod 2770 dossier-partage
```

Dans cette notation :

```text
2   -> bit setgid
770 -> permissions classiques
```

L'objectif est notamment de faciliter la collaboration entre utilisateurs d'un groupe.

Le résultat réel dépend aussi de l'umask, des ACL par défaut et des règles d'accès du système.

## 15.2 Sticky bit

Le sticky bit est utilisé dans certains répertoires partagés.

Un exemple classique est `/tmp`.

Examiner ses permissions :

```bash
ls -ld /tmp
```

Une sortie possible :

```text
drwxrwxrwt
```

Le `t` final indique habituellement la présence du sticky bit dans cette représentation.

Dans un répertoire partagé protégé par ce mécanisme, la suppression et le renommage des entrées sont limités par des règles particulières, notamment liées au propriétaire de l'entrée.

Cela permet de réduire les suppressions non souhaitées entre utilisateurs.

**Ne modifiez pas les permissions de `/tmp` pendant ce cours.**

## 15.3 Setuid

Le bit setuid modifie certains aspects des privilèges effectifs lors de l'exécution d'un programme dans les environnements qui le prennent en charge.

Il doit être traité avec une grande prudence, car il peut affecter les limites de privilèges.

Ne l'appliquez pas à vos scripts ou programmes de test sans avoir étudié ses implications.

Ce cours ne demande pas de créer de programme setuid.

## 15.4 Pourquoi ces bits doivent-ils être compris séparément ?

Le premier chiffre d'un mode numérique peut représenter des bits spéciaux.

Exemple :

```text
2770
|
+-- 2 : setgid
+-- 770 : permissions classiques
```

Les bits spéciaux ne remplacent pas les permissions classiques. Ils modifient certains comportements selon le type d'objet et le contexte.

Les permissions affichées par `ls -l` peuvent employer des lettres comme `s`, `S`, `t` ou `T` pour représenter ces situations.

Leur signification doit être interprétée avec les permissions concernées.


# 16. Introduction aux ACL

Les permissions classiques distinguent le propriétaire, le groupe et les autres utilisateurs.

Il arrive qu'une organisation souhaite accorder des permissions à plusieurs utilisateurs ou groupes spécifiques sans changer l'organisation principale.

Les ACL (*Access Control Lists*) peuvent répondre à ce besoin.

## 16.1 Exemple de besoin

Supposons qu'Alice soit propriétaire d'un document et que Bob doive pouvoir le lire.

Le groupe associé au fichier ne convient pas à cette collaboration.

Une ACL permet, sur un système compatible, de définir une permission supplémentaire pour Bob.

### Schéma conceptuel

```text
+--------------------------------+
| fichier : rapport.txt          |
+--------------------------------+
| Proprietaire : Alice           |
| Groupe : support               |
+--------------------------------+
| Permissions classiques         |
| Alice : lecture/ecriture       |
| Groupe : lecture               |
| Autres : aucune                |
+--------------------------------+
| ACL supplementaire             |
| Bob : lecture                  |
+--------------------------------+
```

Les permissions effectives dépendent également du masque ACL et des permissions applicables au chemin complet.

## 16.2 Examiner les ACL avec `getfacl`

Si l'outil est disponible :

```bash
getfacl rapport.txt
```

La commande peut afficher les permissions classiques et les entrées ACL présentes.

Si elle est absente, le paquet nécessaire dépend de la distribution.

## 16.3 Définir une ACL avec `setfacl`

Exemple dans un répertoire de test :

```bash
setfacl -m u:bob:r-- rapport.txt
```

Cette commande demande d'ajouter ou de modifier une entrée ACL pour accorder à Bob la lecture.

L'utilisateur doit exister, et le système de fichiers doit prendre en charge l'opération.

Vérifiez ensuite :

```bash
getfacl rapport.txt
```

Ne recopiez pas cette commande sur un fichier important sans connaître les conséquences.

## 16.4 Retirer une entrée ACL

```bash
setfacl -x u:bob rapport.txt
```

Cette commande retire l'entrée ACL spécifiée si elle existe.

Pour supprimer les ACL étendues d'un fichier :

```bash
setfacl -b rapport.txt
```

Cette opération retire les ACL étendues. Elle ne doit être exécutée que si leur suppression est intentionnelle.

## 16.5 Quand utiliser les ACL ?

Les ACL sont utiles lorsqu'il faut définir des accès plus précis que ceux permis par le modèle classique.

Cependant, elles ajoutent de la complexité.

Pour un débutant, il est conseillé de maîtriser d'abord :

1. Le propriétaire.
2. Le groupe.
3. Les permissions classiques.
4. L'accès par les répertoires parents.
5. L'umask.

Les ACL peuvent ensuite être utilisées pour des scénarios où le modèle classique ne répond pas au besoin.


# 17. Mesurer et contrôler l'espace de stockage

L'administration du stockage ne consiste pas uniquement à savoir combien de fichiers existent.

Il faut distinguer la taille des fichiers, l'espace alloué, l'utilisation des systèmes de fichiers et la disponibilité des métadonnées.

## 17.1 Examiner l'espace avec `df`

```bash
df -h
```

La commande affiche une vue de l'espace des systèmes de fichiers montés.

L'option `-h` demande généralement des tailles lisibles par un humain.

Les colonnes courantes comprennent :

- Taille.
- Espace utilisé.
- Espace disponible.
- Pourcentage utilisé.
- Point de montage.

Pour examiner le système de fichiers qui contient un chemin :

```bash
df -h ~/Documents
```

## 17.2 Comprendre un résultat `df`

Exemple fictif :

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        40G   20G   18G  53% /
```

Interprétation simplifiée :

- La capacité totale affichée est de 40 Go.
- Environ 20 Go sont utilisés selon les règles du système de fichiers.
- Environ 18 Go sont indiqués comme disponibles.
- Le taux d'utilisation affiché est de 53 %.
- Le point de montage est `/`.

La somme des valeurs affichées peut ne pas correspondre exactement à la capacité totale, notamment à cause des arrondis et des mécanismes du système de fichiers.

Les valeurs sont uniquement illustratives.

## 17.3 Examiner l'espace d'un répertoire avec `du`

```bash
du -sh ~/Documents
```

La commande estime l'espace associé au répertoire indiqué.

L'option `-s` demande un résumé.

L'option `-h` affiche des tailles lisibles.

Pour examiner la taille des sous-répertoires immédiats, sur un système prenant en charge GNU `du` :

```bash
du -h --max-depth=1 ~/Documents
```

La syntaxe exacte peut varier selon la version disponible.

## 17.4 Différence entre `df` et `du`

`df` examine l'espace utilisé et disponible au niveau des systèmes de fichiers.

`du` estime l'espace associé aux fichiers et répertoires parcourus.

Ils peuvent donc donner des résultats différents.

### Schéma

```text
df
 |
 +-- Espace des systemes de fichiers montes

du
 |
 +-- Espace associe aux fichiers et repertoires parcourus
```

Un écart peut s'expliquer par :

- Des fichiers supprimés mais encore ouverts par un processus.
- Des points de montage imbriqués.
- Des limites de parcours.
- Des métadonnées du système de fichiers.
- Des fichiers creux.
- Des différences entre la taille logique et l'espace réellement alloué.

Il faut étudier le contexte avant de conclure à une anomalie.

## 17.5 Examiner les inodes disponibles

Certains systèmes de fichiers reposent sur des inodes ou des structures équivalentes.

La disponibilité des inodes peut être examinée avec :

```bash
df -i
```

Un système de fichiers peut manquer de capacité à créer de nouvelles entrées alors que de l'espace en octets reste disponible.

Ce scénario peut se produire lorsqu'un très grand nombre de petits fichiers est présent.

Le comportement et la pertinence de cette métrique dépendent du système de fichiers.

## 17.6 Rechercher les fichiers volumineux

Pour rechercher les fichiers ordinaires les plus volumineux dans un répertoire de test :

```bash
find ~/storage-lab -type f -printf '%s %p\n'
```

Cette syntaxe utilise une option de GNU `find`. Elle n'est pas universelle.

Les tailles affichées sont ici des octets selon la sortie demandée.

Pour trier la sortie du plus grand au plus petit :

```bash
find ~/storage-lab -type f -printf '%s %p\n' | sort -nr
```

Cette commande permet d'identifier les fichiers de test qui occupent le plus d'espace dans la recherche.

N'appliquez pas une suppression automatique aux fichiers trouvés.

## 17.7 La taille logique et l'espace alloué

La taille logique correspond au nombre d'octets représentés dans le contenu du fichier.

L'espace alloué correspond aux blocs attribués par le système de fichiers selon son mode de stockage.

Les deux quantités peuvent différer.

Exemples :

- Un fichier vide possède une taille logique nulle.
- Un petit fichier peut occuper un bloc de stockage.
- Un fichier creux peut afficher une taille logique importante avec une allocation physique plus faible.
- Les métadonnées et l'organisation interne peuvent influencer l'espace réellement utilisé.

Pour examiner ces informations :

```bash
stat fichier.txt
```

Et, selon les besoins :

```bash
du -h fichier.txt
```

Les résultats doivent être interprétés selon les options utilisées et les caractéristiques du système de fichiers.

## 17.8 Que faire lorsque le disque est presque plein ?

La bonne démarche consiste à diagnostiquer avant de supprimer.

```text
df indique une utilisation elevee
                |
                v
Identifier le systeme de fichiers concerne
                |
                v
Examiner les repertoires importants
                |
                v
Rechercher les donnees volumineuses
                |
                v
Identifier leur fonction et leur proprietaire
                |
                v
Determiner ce qui peut etre archive ou nettoye
                |
                v
Effectuer une action maitrisee
                |
                v
Verifier de nouveau l'espace et les services
```

Les journaux, les bases de données, les caches et les fichiers temporaires ne doivent pas être supprimés au hasard.

Un nettoyage mal conçu peut empêcher une application de fonctionner ou supprimer des informations utiles au diagnostic.


# 18. Rechercher et examiner les fichiers

La recherche de fichiers permet de contrôler un répertoire, retrouver un document ou diagnostiquer des chemins manquants.

## 18.1 Utiliser `find`

Pour lister le contenu d'une arborescence :

```bash
find ~/storage-lab -print
```

Pour retrouver les fichiers ordinaires :

```bash
find ~/storage-lab -type f
```

Pour retrouver les répertoires :

```bash
find ~/storage-lab -type d
```

Pour rechercher les fichiers `.txt` :

```bash
find ~/storage-lab -type f -name "*.txt"
```

Les guillemets empêchent le Shell de développer le motif avant de le transmettre à `find`.

## 18.2 Examiner les permissions des répertoires

```bash
find ~/storage-lab -type d -exec ls -ld {} \;
```

Cette commande demande à `find` d'exécuter `ls -ld` sur les répertoires trouvés.

La syntaxe dépend d'un environnement compatible avec les outils utilisés.

Elle est utile pour examiner les permissions de plusieurs répertoires dans un laboratoire.

## 18.3 Examiner les permissions des fichiers

```bash
find ~/storage-lab -type f -exec ls -l {} \;
```

La sortie peut être longue si le répertoire contient beaucoup de fichiers.

Limitez la recherche à un emplacement pertinent.

## 18.4 Rechercher du texte

Pour rechercher un mot dans les fichiers d'un répertoire :

```bash
grep -R -n "configuration" ~/storage-lab
```

Cette commande recherche le motif dans les fichiers parcourus récursivement et affiche les numéros de ligne dans les correspondances.

La commande peut rencontrer des fichiers illisibles ou des contenus binaires. Le résultat dépend du périmètre et des permissions.

## 18.5 Examiner les métadonnées

```bash
stat ~/storage-lab
```

Pour un fichier particulier :

```bash
stat ~/storage-lab/fichier.txt
```

Ces informations permettent de vérifier la taille, l'identité de l'objet, les permissions et les horodatages fournis par le système.

## 18.6 Pourquoi la recherche peut-elle échouer ?

Une recherche peut échouer pour différentes raisons :

- Le chemin de départ n'existe pas.
- Le nom ne correspond pas.
- Les permissions empêchent de parcourir certains répertoires.
- Le fichier a été déplacé.
- Le fichier se trouve sur un système de fichiers non monté.
- Le nom contient des majuscules ou des caractères différents de ceux recherchés.

Il faut examiner ces hypothèses une par une plutôt que conclure immédiatement à la perte du fichier.


# 19. Méthode de dépannage des problèmes d'accès

Une erreur de permission est un symptôme, pas nécessairement la cause complète du problème.

Pour diagnostiquer correctement l'accès à un fichier, il faut examiner le chemin, les propriétaires, les permissions et les autres mécanismes susceptibles d'intervenir.

## 19.1 Erreur `Permission denied`

Supposons que la commande suivante échoue :

```bash
cat secret.txt
```

Le système indique :

```text
Permission denied
```

Commencez par :

```bash
whoami
id
pwd
ls -l secret.txt
```

Ces commandes permettent de connaître l'utilisateur courant, ses groupes, son répertoire et les permissions du fichier.

Mais elles ne suffisent pas toujours.

Il faut également examiner le chemin complet.

## 19.2 Vérifier les répertoires parents

Considérons :

```text
/home/alice/Documents/secret.txt
```

Le système doit normalement autoriser la traversée des répertoires nécessaires.

Schéma :

```text
/home
  |
  v
alice/
  |
  v
Documents/
  |
  v
secret.txt
```

Pour examiner les permissions des composants du chemin :

```bash
namei -l /home/alice/Documents/secret.txt
```

`namei` est disponible sur de nombreux systèmes Linux, mais n'est pas garanti sur toutes les installations.

Cette commande permet de voir les permissions et les propriétaires des éléments du chemin.

## 19.3 Pourquoi ne pas utiliser immédiatement `sudo` ?

Si l'accès est refusé, exécuter systématiquement la commande avec `sudo` peut masquer la cause.

Il faut déterminer :

- Quel utilisateur doit accéder au fichier.
- Quel niveau d'accès est nécessaire.
- Quel propriétaire et quel groupe sont appropriés.
- Si une ACL est présente.
- Si un répertoire parent empêche la traversée.
- Si un mécanisme supplémentaire bloque l'accès.

La correction peut être une modification ciblée de permission ou de groupe plutôt qu'une exécution permanente en tant qu'administrateur.

## 19.4 Erreur liée à un système de fichiers absent

Un fichier peut sembler absent parce que le système de fichiers attendu n'est pas monté.

Vérifiez :

```bash
findmnt
```

Puis :

```bash
df -h
```

Et :

```bash
lsblk -f
```

Le résultat permet de comprendre la relation entre les périphériques et les points de montage.

Ne tentez pas de créer un nouveau système de fichiers simplement parce qu'un chemin ne contient pas les données attendues.

## 19.5 Un fichier existe-t-il réellement ?

Pour examiner un chemin :

```bash
ls -l /chemin/vers/fichier.txt
```

Pour vérifier sa nature :

```bash
file /chemin/vers/fichier.txt
```

Pour examiner ses métadonnées :

```bash
stat /chemin/vers/fichier.txt
```

Si le chemin n'existe pas, il faut vérifier le point de départ, le nom et les montages.

## 19.6 Erreur de lecture seule

Un système de fichiers peut être monté en lecture seule.

Dans ce cas, des opérations qui modifient son contenu peuvent échouer même si les permissions classiques semblent permettre l'écriture.

Examinez le montage :

```bash
findmnt /chemin
```

Le résultat peut afficher les options appliquées au montage.

Ne tentez pas de remonter automatiquement un système de fichiers en lecture-écriture sans comprendre pourquoi il est en lecture seule.

Cette situation peut être liée à la configuration, au support de stockage ou à un mécanisme de protection.

## 19.7 Méthode complète de diagnostic

```text
ERREUR D'ACCES
      |
      v
Verifier l'identite de l'utilisateur
      |
      v
Verifier que le chemin existe
      |
      v
Examiner proprietaire et groupe
      |
      v
Examiner permissions du fichier
      |
      v
Examiner permissions des repertoires parents
      |
      v
Verifier les montages et leur etat
      |
      v
Examiner ACL et autres controles si necessaire
      |
      v
Appliquer uniquement la correction justifiee
      |
      v
Recommencer le test
```

Cette méthode permet de réduire les changements inutiles.


# 20. Travaux pratiques guidés

Ces travaux pratiques sont destinés à un environnement de test.

## TP 1 — Explorer le système de fichiers

### Objectifs

- Identifier la racine.
- Explorer les répertoires importants.
- Examiner les entrées cachées.
- Comprendre les chemins.

### Étape 1 : examiner la racine

```bash
cd /
pwd
ls -lah
```

Notez les principaux répertoires.

### Étape 2 : examiner le répertoire personnel

```bash
cd ~
pwd
ls -la
```

Comparez les résultats.

### Étape 3 : examiner `/var/log`

```bash
ls -lah /var/log
```

La sortie dépend de la distribution, des journaux présents et des permissions.

### Questions

1. Quel est le rôle de `/home` ?
2. Que contient souvent `/etc` ?
3. Pourquoi `/dev` ne se comporte-t-il pas comme un répertoire de documents ordinaire ?
4. Pourquoi les fichiers cachés ne sont-ils pas nécessairement secrets ?

### Résultats attendus

Vous devez pouvoir expliquer l'organisation générale et identifier les principaux répertoires.


## TP 2 — Créer et examiner des fichiers

### Objectifs

- Créer un répertoire.
- Créer des fichiers.
- Examiner leur type et leurs métadonnées.
- Comparer leurs tailles.

### Étape 1 : créer un laboratoire

```bash
mkdir -p ~/storage-lab/fichiers
cd ~/storage-lab/fichiers
```

### Étape 2 : créer deux fichiers

```bash
echo "Premiere ligne" > document.txt
echo "Deuxieme document" > notes.txt
```

### Étape 3 : examiner le contenu

```bash
cat document.txt
cat notes.txt
```

### Étape 4 : examiner les types

```bash
file document.txt
file notes.txt
```

### Étape 5 : examiner les métadonnées

```bash
stat document.txt
stat notes.txt
```

### Étape 6 : afficher les inodes

```bash
ls -li
```

### Questions

1. Quelle différence existe entre le contenu et les métadonnées ?
2. Quel est le rôle de l'inode dans le système de fichiers ?
3. Pourquoi le numéro d'inode n'est-il pas universel à toutes les machines ?
4. Pourquoi un nom de fichier ne suffit-il pas à connaître toutes ses propriétés ?


## TP 3 — Comprendre les liens

### Objectifs

- Créer un lien physique.
- Créer un lien symbolique.
- Examiner leurs inodes.
- Observer leurs comportements.

### Étape 1 : créer un fichier source

```bash
mkdir -p ~/storage-lab/liens
cd ~/storage-lab/liens

echo "Contenu original" > source.txt
```

### Étape 2 : créer les liens

```bash
ln source.txt lien-physique.txt
ln -s source.txt lien-symbolique.txt
```

### Étape 3 : examiner les entrées

```bash
ls -li
ls -l
```

### Étape 4 : modifier le contenu

```bash
echo "Nouvelle ligne" >> source.txt
```

### Étape 5 : lire via les liens

```bash
cat lien-physique.txt
cat lien-symbolique.txt
```

### Questions

1. Pourquoi le lien physique partage-t-il l'inode du fichier source ?
2. Pourquoi le lien symbolique affiche-t-il une cible dans `ls -l` ?
3. Que se passe-t-il si la cible du lien symbolique est supprimée ?
4. Pourquoi ne faut-il pas assimiler un lien à une copie ?


## TP 4 — Manipuler les permissions

### Objectifs

- Lire les permissions.
- Modifier un mode numérique.
- Comparer plusieurs modes.
- Vérifier les résultats.

### Étape 1 : préparer le laboratoire

```bash
mkdir -p ~/storage-lab/permissions
cd ~/storage-lab/permissions
```

### Étape 2 : créer les fichiers

```bash
echo "Document public de test" > document-public.txt
echo "Document prive de test" > document-prive.txt
touch script-test.sh
```

### Étape 3 : appliquer les permissions

```bash
chmod 644 document-public.txt
chmod 600 document-prive.txt
chmod 700 script-test.sh
```

### Étape 4 : vérifier

```bash
ls -l
stat document-public.txt
stat document-prive.txt
```

### Questions

1. Que signifie `644` ?
2. Que signifie `600` ?
3. Quelle différence existe entre `600` et `700` ?
4. Pourquoi faut-il distinguer les besoins des fichiers et ceux des répertoires ?


## TP 5 — Comprendre les propriétaires et les groupes

### Objectifs

- Examiner l'utilisateur courant.
- Identifier les groupes.
- Afficher le propriétaire d'un fichier.
- Comprendre le rôle du groupe associé.

### Étape 1 : identifier la session

```bash
whoami
id
groups
```

### Étape 2 : examiner un fichier

```bash
ls -l ~/storage-lab/permissions/document-public.txt
stat ~/storage-lab/permissions/document-public.txt
```

### Étape 3 : expliquer les résultats

Décrivez :

- Le propriétaire.
- Le groupe.
- Les permissions.
- La taille.
- Le type de fichier.

N'effectuez pas de changement de propriétaire si vous ne disposez pas d'un environnement adapté et d'un objectif clair.


## TP 6 — Comparer les umask

### Objectifs

- Afficher l'umask.
- Modifier temporairement le masque.
- Comparer les permissions des nouveaux fichiers et répertoires.

### Étape 1 : examiner l'umask courant

```bash
umask
```

### Étape 2 : appliquer `027`

```bash
umask 027

touch ~/storage-lab/fichier-027.txt
mkdir ~/storage-lab/dossier-027
```

### Étape 3 : vérifier

```bash
ls -l ~/storage-lab/fichier-027.txt
ls -ld ~/storage-lab/dossier-027
```

### Étape 4 : appliquer `022`

```bash
umask 022

touch ~/storage-lab/fichier-022.txt
mkdir ~/storage-lab/dossier-022
```

Puis :

```bash
ls -l ~/storage-lab/fichier-022.txt
ls -ld ~/storage-lab/dossier-022
```

### Questions

1. Quel effet l'umask exerce-t-il sur les permissions initiales ?
2. Pourquoi un fichier ordinaire ne reçoit-il pas automatiquement `x` dans le modèle habituel ?
3. Pourquoi faut-il examiner les permissions après la création ?


## TP 7 — Examiner le stockage

### Objectifs

- Lister les périphériques.
- Examiner les systèmes de fichiers montés.
- Comprendre les différences entre `df`, `du` et `lsblk`.

Exécutez :

```bash
lsblk -f
findmnt
df -h
df -i
du -sh ~/storage-lab
```

### Questions

1. Que présente `lsblk -f` ?
2. À quoi sert `findmnt` ?
3. Que mesure `df -h` ?
4. Que mesure `du -sh` ?
5. Pourquoi les résultats de `df` et `du` peuvent-ils différer ?
6. Que signifie une pénurie d'inodes ?

### Résultat attendu

Vous devez distinguer le périphérique, le système de fichiers, le point de montage et l'utilisation de l'espace.


# 21. Exercices d'évaluation corrigés

Essayez de répondre avant de consulter les corrections.

## Exercice 1 — Racine Linux

**Question :** quelle est la différence entre `/` et `/root` ?

**Correction :** `/` est la racine de l'arborescence Linux. `/root` est habituellement le répertoire personnel du superutilisateur `root`.

## Exercice 2 — Système de fichiers

**Question :** quel est le rôle principal d'un système de fichiers ?

**Correction :** organiser et gérer les fichiers, répertoires et métadonnées sur un espace de stockage.

## Exercice 3 — Disque et partition

**Question :** une partition est-elle identique à un système de fichiers ?

**Correction :** non. Une partition délimite un espace sur un périphérique. Elle peut ensuite être utilisée pour un système de fichiers, du swap ou d'autres usages.

## Exercice 4 — Point de montage

**Question :** pourquoi un système de fichiers doit-il être monté pour être accessible par un chemin conventionnel de l'arborescence ?

**Correction :** le montage associe son contenu à un point de l'arborescence, permettant d'y accéder à travers les chemins correspondants.

## Exercice 5 — `lsblk` et `df`

**Question :** quelle différence existe entre `lsblk` et `df` ?

**Correction :** `lsblk` présente les périphériques de stockage et leurs relations. `df` examine l'utilisation de l'espace des systèmes de fichiers montés.

## Exercice 6 — Inode

**Question :** que permet notamment de comprendre l'inode ?

**Correction :** il représente une structure de métadonnées associée à un objet de système de fichiers et aide notamment à comprendre les liens physiques.

## Exercice 7 — Lien physique

**Question :** pourquoi deux liens physiques vers le même fichier ne représentent-ils pas nécessairement deux copies ?

**Correction :** ils peuvent être deux entrées de répertoire qui pointent vers le même inode et les mêmes données.

## Exercice 8 — Lien symbolique

**Question :** qu'arrive-t-il à un lien symbolique lorsque son chemin cible n'existe plus ?

**Correction :** le lien peut devenir cassé. L'entrée du lien existe toujours, mais les opérations qui tentent de suivre la cible échouent normalement.

## Exercice 9 — Permissions

**Question :** que signifie `rw-r--r--` ?

**Correction :** le propriétaire peut lire et écrire ; le groupe peut lire ; les autres peuvent lire. Aucune catégorie ne dispose du droit d'exécution classique dans cette représentation.

## Exercice 10 — Mode `600`

**Question :** à quoi correspond `chmod 600 secret.txt` ?

**Correction :** le propriétaire reçoit `rw-`, tandis que le groupe et les autres n'obtiennent aucune permission classique.

## Exercice 11 — Mode `750`

**Question :** que signifie `chmod 750 dossier` ?

**Correction :** le propriétaire possède `rwx`, le groupe possède `r-x` et les autres n'ont aucune permission classique.

## Exercice 12 — Permissions d'un répertoire

**Question :** pourquoi la permission `x` est-elle importante sur un répertoire ?

**Correction :** elle permet généralement de traverser le répertoire et d'accéder aux objets par leur chemin, sous réserve des autres contrôles.

## Exercice 13 — Propriétaire

**Question :** quelle commande permet d'afficher le propriétaire et les permissions d'un fichier ?

**Correction :**

```bash
ls -l fichier.txt
```

## Exercice 14 — Modifier le groupe

**Question :** quelle commande permet de changer le groupe associé à un fichier lorsque l'opération est autorisée ?

**Correction :**

```bash
chgrp groupe fichier.txt
```

## Exercice 15 — Umask

**Question :** quel est le résultat habituel pour un fichier ordinaire créé avec une base `666` et un umask `027` ?

**Correction :** `640`, soit `rw-r-----`, dans le modèle de création habituel.

## Exercice 16 — `df` et `du`

**Question :** pourquoi les deux commandes peuvent-elles donner des résultats différents ?

**Correction :** elles ne mesurent pas la même chose et peuvent traiter différemment les fichiers supprimés mais encore ouverts, les points de montage, les limites de parcours, les métadonnées et l'allocation des blocs.

## Exercice 17 — Erreur de permission

**Question :** pourquoi faut-il examiner les répertoires parents avant de changer les permissions du fichier ?

**Correction :** les permissions du chemin complet influencent l'accès. La permission de traversée d'un répertoire parent peut être nécessaire pour atteindre le fichier.

## Exercice 18 — Montage

**Question :** pourquoi faut-il vérifier un point de montage avant de monter un autre système de fichiers dessus ?

**Correction :** les fichiers déjà présents dans le répertoire peuvent être masqués tant que le nouveau système de fichiers reste monté.

## Exercice 19 — `chmod 777`

**Question :** pourquoi cette commande est-elle risquée comme correction automatique ?

**Correction :** elle accorde des permissions très larges au propriétaire, au groupe et aux autres. Elle peut permettre des modifications ou des accès qui ne sont pas nécessaires.

## Exercice 20 — Sécurité du stockage

**Question :** que faut-il vérifier avant une commande de formatage ?

**Correction :** le périphérique exact, les partitions, les données existantes, les sauvegardes, la justification de l'opération et le plan de retour arrière.


# 22. Fiche de révision des commandes

## 22.1 Navigation

| Commande | Utilité |
|---|---|
| `pwd` | Afficher le répertoire courant |
| `ls` | Lister le contenu |
| `ls -l` | Afficher les détails |
| `ls -la` | Inclure les entrées cachées |
| `cd /` | Aller à la racine |
| `cd ~` | Aller au répertoire personnel |
| `cd ..` | Remonter au répertoire parent |

## 22.2 Stockage et montages

| Commande | Utilité |
|---|---|
| `lsblk` | Examiner les périphériques de stockage |
| `lsblk -f` | Examiner aussi les systèmes de fichiers |
| `blkid` | Identifier des systèmes de fichiers |
| `findmnt` | Examiner les montages |
| `df -h` | Examiner l'espace des systèmes de fichiers |
| `df -i` | Examiner les inodes |
| `du -sh repertoire` | Estimer l'espace utilisé par un répertoire |
| `mount` | Monter un système de fichiers selon les paramètres |
| `umount chemin` | Demander le démontage |

## 22.3 Fichiers et métadonnées

| Commande | Utilité |
|---|---|
| `file fichier` | Examiner le type probable |
| `stat fichier` | Examiner les métadonnées |
| `ls -i fichier` | Afficher le numéro d'inode |
| `find . -type f` | Rechercher les fichiers ordinaires |
| `find . -type d` | Rechercher les répertoires |
| `find . -name "*.txt"` | Rechercher selon un motif de nom |

## 22.4 Liens

| Commande | Utilité |
|---|---|
| `ln source lien` | Créer un lien physique dans le cas courant |
| `ln -s cible lien` | Créer un lien symbolique |
| `ls -li` | Examiner les inodes |
| `ls -l` | Observer les liens symboliques |

## 22.5 Permissions et propriétaires

| Commande | Utilité |
|---|---|
| `chmod 644 fichier` | Définir des permissions classiques |
| `chmod 600 fichier` | Réserver les permissions classiques au propriétaire |
| `chmod u+x script.sh` | Ajouter l'exécution au propriétaire |
| `chown utilisateur fichier` | Modifier le propriétaire si autorisé |
| `chown utilisateur:groupe fichier` | Modifier le propriétaire et le groupe si autorisé |
| `chgrp groupe fichier` | Modifier le groupe si autorisé |
| `umask` | Afficher le masque de création |
| `getfacl fichier` | Examiner les ACL si disponible |
| `setfacl -m u:alice:r-- fichier` | Définir une entrée ACL si disponible |

## 22.6 Commandes d'observation de l'accès

| Commande | Utilité |
|---|---|
| `whoami` | Afficher l'utilisateur effectif |
| `id` | Examiner les identifiants et groupes |
| `namei -l chemin` | Examiner les composants d'un chemin et leurs permissions |
| `ls -ld dossier` | Examiner le répertoire lui-même |
| `stat fichier` | Examiner les métadonnées |


# 23. Challenge final — Préparer un espace de stockage partagé

## 23.1 Scénario

Vous êtes chargé d'organiser un petit espace de stockage pour une équipe de support informatique.

L'équipe doit disposer d'une arborescence claire contenant des documents, des journaux, des rapports et une zone de préparation.

Vous devez créer cet espace, appliquer des permissions cohérentes et expliquer les choix effectués.

Le challenge mobilise les notions du cours. Il ne remplace pas les chapitres précédents : il sert à vérifier que les concepts peuvent être mis en pratique dans un scénario concret.

## 23.2 Objectifs

Vous devez :

1. Créer une arborescence.
2. Créer des documents.
3. Créer un journal d'activité.
4. Examiner les métadonnées.
5. Utiliser les liens physiques et symboliques.
6. Appliquer des permissions différentes selon les besoins.
7. Vérifier les propriétaires et les groupes.
8. Comparer l'espace occupé et l'espace disponible.
9. Expliquer comment diagnostiquer un accès refusé.
10. Documenter le résultat.

## 23.3 Environnement de travail

Réalisez le challenge dans votre répertoire personnel, avec le chemin :

```text
~/projet-stockage
```

N'utilisez pas `/etc`, `/usr`, `/var` ou un répertoire de production.

Aucun formatage ni changement de partition n'est requis.

## 23.4 Étape 1 — Créer l'arborescence

Vous devez obtenir :

```text
projet-stockage/
|
+-- documents/
|
+-- journaux/
|
+-- rapports/
|
+-- archives/
|
+-- temporaire/
```

Utilisez `mkdir -p` pour créer l'arborescence.

Puis vérifiez :

```bash
find ~/projet-stockage -print
```

**Critère de validation :** le répertoire principal et tous les sous-répertoires attendus doivent exister.

## 23.5 Étape 2 — Créer les documents

Dans `documents/`, créez :

```text
guide.txt
permissions.txt
stockage.txt
```

Le fichier `guide.txt` doit expliquer le but du projet.

Le fichier `permissions.txt` doit résumer la différence entre `r`, `w` et `x`.

Le fichier `stockage.txt` doit distinguer disque, partition, système de fichiers et point de montage.

Chaque document doit contenir plusieurs lignes.

## 23.6 Étape 3 — Créer le journal

Dans `journaux/`, créez :

```text
activite.log
```

Le journal doit contenir au minimum :

```text
Initialisation du projet
Creation des repertoires
Creation des documents
Verification de l'arborescence
```

Ajoutez ensuite une ligne confirmant que les permissions ont été contrôlées.

## 23.7 Étape 4 — Créer des liens

Dans `rapports/`, créez une copie de référence via un lien physique vers un fichier ordinaire du projet, lorsque le système de fichiers le permet.

Créez également un lien symbolique vers un document.

Examiner les inodes :

```bash
ls -li ~/projet-stockage/documents
ls -li ~/projet-stockage/rapports
```

Le lien physique et le lien symbolique doivent être correctement identifiés et expliqués.

Ne tentez pas de créer un lien physique entre deux systèmes de fichiers différents.

## 23.8 Étape 5 — Appliquer les permissions

Appliquez le mode `644` aux documents qui doivent être lisibles par les autres catégories.

Appliquez le mode `600` au journal afin de réserver les permissions classiques au propriétaire.

Appliquez le mode `700` au répertoire `temporaire/` si l'objectif est de le rendre accessible uniquement à son propriétaire selon le modèle classique.

Vérifiez :

```bash
ls -l ~/projet-stockage/documents
ls -l ~/projet-stockage/journaux
ls -ld ~/projet-stockage/temporaire
```

Expliquez chaque choix.

## 23.9 Étape 6 — Examiner le stockage

Exécutez :

```bash
df -h ~/projet-stockage
du -sh ~/projet-stockage
stat ~/projet-stockage/documents/guide.txt
```

Décrivez la signification des résultats.

Ne vous contentez pas d'indiquer les chiffres : expliquez ce que chaque outil mesure.

## 23.10 Étape 7 — Contrôler les permissions

Exécutez :

```bash
find ~/projet-stockage -type d -exec ls -ld {} \;
find ~/projet-stockage -type f -exec ls -l {} \;
```

Vérifiez que les droits correspondent aux objectifs du projet.

Si les résultats diffèrent des attentes, recherchez la cause avant de modifier les permissions.

## 23.11 Étape 8 — Rédiger un compte rendu

Créez un fichier :

```text
rapports/bilan-stockage.md
```

Le document doit indiquer :

- L'arborescence créée.
- Les fichiers présents.
- Les liens créés.
- Les permissions choisies.
- Les résultats des commandes d'espace.
- Les difficultés rencontrées.
- Les vérifications effectuées.
- Les limites de la solution.

## 23.12 Barème d'évaluation

| Compétence | Points |
|---|---:|
| Création de l'arborescence | 15 |
| Documents et journal | 10 |
| Compréhension des inodes et des liens | 15 |
| Permissions classiques | 20 |
| Propriétaires et groupes | 10 |
| Analyse du stockage | 15 |
| Vérification et diagnostic | 10 |
| Documentation | 5 |
| **Total** | **100** |

La qualité de l'explication compte autant que l'exécution des commandes.


# 24. Correction détaillée du challenge

Cette section propose une solution de référence. Essayez d'abord de réaliser le challenge sans recopier les commandes.

## 24.1 Créer l'arborescence

```bash
mkdir -p ~/projet-stockage/documents
mkdir -p ~/projet-stockage/journaux
mkdir -p ~/projet-stockage/rapports
mkdir -p ~/projet-stockage/archives
mkdir -p ~/projet-stockage/temporaire
```

Vérifiez :

```bash
find ~/projet-stockage -print
```

## 24.2 Créer les documents

```bash
echo "Projet de documentation et de controle du stockage Linux." \
    > ~/projet-stockage/documents/guide.txt

echo "r signifie lecture, w ecriture et x execution ou traversee selon le type." \
    > ~/projet-stockage/documents/permissions.txt

echo "Un disque contient des espaces de stockage. Une partition delimite une region. Un systeme de fichiers organise les donnees. Un point de montage rend son contenu accessible dans l'arborescence." \
    > ~/projet-stockage/documents/stockage.txt
```

Ajouter une deuxième ligne :

```bash
echo "Le resultat des commandes doit etre verifie avant de conclure." \
    >> ~/projet-stockage/documents/guide.txt

echo "Les permissions effectives dependent aussi du chemin et des autres controles." \
    >> ~/projet-stockage/documents/permissions.txt

echo "Les operations sur les partitions et les peripheriques peuvent etre destructives." \
    >> ~/projet-stockage/documents/stockage.txt
```

Vérifiez le contenu :

```bash
cat ~/projet-stockage/documents/guide.txt
cat ~/projet-stockage/documents/permissions.txt
cat ~/projet-stockage/documents/stockage.txt
```

## 24.3 Créer le journal

```bash
echo "Initialisation du projet" \
    > ~/projet-stockage/journaux/activite.log

echo "Creation des repertoires" \
    >> ~/projet-stockage/journaux/activite.log

echo "Creation des documents" \
    >> ~/projet-stockage/journaux/activite.log

echo "Verification de l'arborescence" \
    >> ~/projet-stockage/journaux/activite.log

echo "Permissions controlees" \
    >> ~/projet-stockage/journaux/activite.log
```

Puis :

```bash
cat ~/projet-stockage/journaux/activite.log
```

Le journal doit contenir les événements prévus.

## 24.4 Créer un lien physique

```bash
ln ~/projet-stockage/documents/guide.txt \
   ~/projet-stockage/rapports/guide-reference.txt
```

Cette opération doit réussir lorsque les chemins sont sur le même système de fichiers et que les conditions nécessaires sont réunies.

Examinez les inodes :

```bash
ls -li ~/projet-stockage/documents/guide.txt
ls -li ~/projet-stockage/rapports/guide-reference.txt
```

Les deux entrées devraient normalement présenter le même inode dans ce cas de lien physique.

## 24.5 Créer un lien symbolique

```bash
ln -s ../documents/permissions.txt \
   ~/projet-stockage/rapports/permissions-reference.txt
```

La cible est donnée sous forme de chemin relatif à l'emplacement du lien symbolique.

Vérifiez :

```bash
ls -l ~/projet-stockage/rapports
```

Puis lisez le contenu via le lien :

```bash
cat ~/projet-stockage/rapports/permissions-reference.txt
```

Le chemin relatif est interprété depuis le répertoire qui contient le lien, et non depuis le répertoire courant du terminal.

## 24.6 Appliquer les permissions

```bash
chmod 644 ~/projet-stockage/documents/guide.txt
chmod 644 ~/projet-stockage/documents/permissions.txt
chmod 644 ~/projet-stockage/documents/stockage.txt
```

Pour le journal :

```bash
chmod 600 ~/projet-stockage/journaux/activite.log
```

Pour le répertoire temporaire :

```bash
chmod 700 ~/projet-stockage/temporaire
```

Vérifiez :

```bash
ls -l ~/projet-stockage/documents
ls -l ~/projet-stockage/journaux/activite.log
ls -ld ~/projet-stockage/temporaire
```

Les commandes `chmod` appliquées aux liens symboliques ne se comportent pas comme une modification de leurs propres permissions ordinaires sur de nombreux systèmes Linux. Pour un lien symbolique, les permissions affichées et la manière dont elles sont traitées doivent être interprétées selon le système.

Dans le cadre de cet exercice, les fichiers cibles sont les objets dont les permissions classiques sont principalement étudiées.

## 24.7 Examiner le stockage

```bash
df -h ~/projet-stockage
```

Cette commande examine l'espace du système de fichiers qui contient le projet.

```bash
du -sh ~/projet-stockage
```

Cette commande estime l'espace associé au projet et à son contenu, selon les règles de parcours et de comptabilisation.

```bash
stat ~/projet-stockage/documents/guide.txt
```

Cette commande affiche les métadonnées du fichier.

Les valeurs ne sont pas prédéterminées : elles dépendent de votre système de fichiers et de l'environnement.

## 24.8 Vérifier les permissions

Pour les répertoires :

```bash
find ~/projet-stockage -type d -exec ls -ld {} \;
```

Pour les fichiers ordinaires :

```bash
find ~/projet-stockage -type f -exec ls -l {} \;
```

Les résultats devraient permettre de retrouver :

- Les documents en `644`.
- Le journal en `600`.
- Le répertoire `temporaire` en `700`.
- Les propriétaires et les groupes associés.
- Les entrées de liens créées.

Il faut interpréter les permissions du chemin complet. Un fichier peut posséder un mode adapté mais rester inaccessible à travers un répertoire parent qui ne peut pas être traversé.

## 24.9 Rédiger le compte rendu

Créez :

```bash
nano ~/projet-stockage/rapports/bilan-stockage.md
```

Contenu possible :

```markdown
# Bilan du projet de stockage

## 1. Objectif

Préparer un espace organisé pour des documents, des journaux,
des rapports, des archives et des fichiers temporaires.

## 2. Arborescence

Le répertoire principal contient les sous-repertoires
documents, journaux, rapports, archives et temporaire.

## 3. Permissions

Les documents utilisent le mode 644.
Le journal utilise le mode 600.
Le repertoire temporaire utilise le mode 700.

## 4. Liens

Un lien physique reference guide.txt.
Un lien symbolique reference permissions.txt.

## 5. Verifications

Les chemins ont ete controles avec find.
Les metadonnees ont ete examinees avec stat.
Les permissions ont ete verifiees avec ls -l.
L'espace a ete examine avec df et du.

## 6. Limites

Les commandes df et du ne mesurent pas exactement
la meme chose.
Les permissions classiques ne couvrent pas tous les
mecanismes de controle d'acces.
```

Vous pouvez adapter ce compte rendu aux résultats réellement observés.

## 24.10 Résultat attendu

L'arborescence doit ressembler à :

```text
~/projet-stockage/
|
+-- documents/
|   +-- guide.txt
|   +-- permissions.txt
|   +-- stockage.txt
|
+-- journaux/
|   +-- activite.log
|
+-- rapports/
|   +-- guide-reference.txt
|   +-- permissions-reference.txt
|   +-- bilan-stockage.md
|
+-- archives/
|
+-- temporaire/
```

`guide-reference.txt` est un lien physique vers le même objet que `guide.txt` dans le scénario présenté.

`permissions-reference.txt` est un lien symbolique dont la cible est `permissions.txt`.

Les permissions et propriétaires doivent être vérifiés à l'aide des commandes plutôt que déduits de l'arborescence uniquement.


# 25. Checklist finale des compétences

Utilisez cette checklist pour vérifier votre progression.

## Système de fichiers

- [ ] Je sais expliquer le rôle d'un système de fichiers.
- [ ] Je connais les principaux répertoires Linux.
- [ ] Je sais utiliser les chemins absolus et relatifs.
- [ ] Je sais identifier différents types de fichiers.
- [ ] Je comprends la distinction entre nom, métadonnées et contenu.

## Stockage et montages

- [ ] Je sais distinguer disque, partition et système de fichiers.
- [ ] Je sais examiner les périphériques avec `lsblk`.
- [ ] Je sais examiner les informations de systèmes de fichiers avec `blkid`.
- [ ] Je comprends le rôle d'un point de montage.
- [ ] Je sais examiner les montages avec `findmnt`.
- [ ] Je sais interpréter `df -h`.
- [ ] Je sais examiner l'utilisation d'un répertoire avec `du`.
- [ ] Je comprends pourquoi `df` et `du` peuvent donner des résultats différents.
- [ ] Je comprends les risques liés au formatage et aux modifications de montage.

## Inodes et liens

- [ ] Je comprends le rôle général des inodes.
- [ ] Je sais examiner les numéros d'inode avec `ls -i`.
- [ ] Je sais expliquer le fonctionnement d'un lien physique.
- [ ] Je sais expliquer le fonctionnement d'un lien symbolique.
- [ ] Je comprends ce qu'est un lien symbolique cassé.
- [ ] Je sais distinguer un lien d'une copie indépendante.

## Propriétaires et groupes

- [ ] Je sais examiner le propriétaire et le groupe avec `ls -l`.
- [ ] Je sais utiliser `id` pour examiner les identifiants et groupes.
- [ ] Je comprends le rôle des groupes.
- [ ] Je sais expliquer le rôle de `chown`.
- [ ] Je sais expliquer le rôle de `chgrp`.
- [ ] Je comprends les risques liés aux changements récursifs de propriétaire.

## Permissions

- [ ] Je sais lire les permissions affichées par `ls -l`.
- [ ] Je comprends la différence entre les permissions d'un fichier et d'un répertoire.
- [ ] Je sais interpréter `r`, `w` et `x`.
- [ ] Je sais convertir une permission numérique.
- [ ] Je sais expliquer les modes `600`, `640`, `644`, `700`, `750` et `755`.
- [ ] Je sais modifier les permissions avec `chmod`.
- [ ] Je comprends pourquoi `chmod 777` n'est pas une solution universelle.
- [ ] Je sais examiner les permissions des répertoires parents.
- [ ] Je comprends le principe de l'umask.
- [ ] Je connais le rôle du setgid et du sticky bit.
- [ ] Je comprends le principe des ACL.

## Diagnostic et bonnes pratiques

- [ ] Je sais examiner un fichier avec `stat`.
- [ ] Je sais rechercher des fichiers avec `find`.
- [ ] Je sais diagnostiquer une erreur de permission.
- [ ] Je sais rechercher un problème lié à un point de montage.
- [ ] Je sais expliquer la différence entre espace utilisé et espace disponible.
- [ ] Je sais éviter les opérations destructives non nécessaires.
- [ ] Je sais vérifier le résultat d'une modification.
- [ ] Je sais documenter les commandes et les résultats importants.


# Conclusion générale

Le système de fichiers Linux ne se limite pas à une arborescence de dossiers et de documents. Il repose sur des mécanismes permettant d'identifier les objets, de gérer leurs métadonnées, d'associer des noms aux fichiers et de rendre les données accessibles par des chemins.

Le stockage apporte une autre dimension : les périphériques, les partitions, les systèmes de fichiers et les points de montage déterminent comment les données sont rendues accessibles.

Les permissions définissent ensuite les opérations autorisées pour le propriétaire, le groupe et les autres utilisateurs. L'umask influence la création des nouveaux objets, les ACL permettent une gestion plus fine et les mécanismes spéciaux répondent à certains besoins de partage.

Enfin, les commandes `lsblk`, `findmnt`, `df`, `du`, `stat`, `chmod`, `chown` et `find` fournissent des moyens complémentaires d'observer et de gérer l'environnement.

Les principes essentiels à retenir sont :

1. Examiner avant de modifier.
2. Distinguer le disque, la partition, le système de fichiers et le montage.
3. Ne pas confondre le nom d'un fichier avec son identité dans le système de fichiers.
4. Comprendre les permissions du fichier et de tous les répertoires nécessaires à son accès.
5. Utiliser le moindre privilège.
6. Éviter les permissions excessives.
7. Vérifier le résultat de chaque opération importante.
8. Ne jamais formater ou supprimer un stockage sans identifier précisément la cible.
9. Tester les sauvegardes et les mécanismes de restauration.
10. Documenter les opérations et leurs résultats.

La maîtrise de ces notions constitue une base essentielle pour poursuivre vers l'administration du stockage, la gestion avancée des permissions, les ACL, LVM, les systèmes de fichiers avancés et la sécurisation des serveurs Linux.

**Principe fondamental :** un accès correct résulte de la cohérence entre le chemin, le système de fichiers, le propriétaire, le groupe, les permissions et les autres mécanismes de contrôle.

Fin du cours — **Système de fichiers et permissions Linux, niveau débutant**.