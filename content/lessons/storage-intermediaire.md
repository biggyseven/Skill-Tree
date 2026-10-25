# Stockage Linux — Niveau intermédiaire
## Administration avancée des disques, partitions, systèmes de fichiers, LVM, RAID et quotas


# Sommaire

1. [Présentation du niveau intermédiaire](#1-présentation-du-niveau-intermédiaire)
2. [Rappel des fondamentaux du stockage Linux](#2-rappel-des-fondamentaux-du-stockage-linux)
3. [Identifier et analyser les périphériques de stockage](#3-identifier-et-analyser-les-périphériques-de-stockage)
4. [Partitions, GPT et outils de partitionnement](#4-partitions-gpt-et-outils-de-partitionnement)
5. [UUID, montages persistants et fichier /etc/fstab](#5-uuid-montages-persistants-et-fichier-etcfstab)
6. [Systèmes de fichiers : ext4, XFS et Btrfs](#6-systèmes-de-fichiers--ext4-xfs-et-btrfs)
7. [Maintenance et réparation des systèmes de fichiers](#7-maintenance-et-réparation-des-systèmes-de-fichiers)
8. [Gestion avancée de l'espace disque](#8-gestion-avancée-de-lespace-disque)
9. [LVM : Logical Volume Manager](#9-lvm--logical-volume-manager)
10. [Extension et réduction des volumes logiques](#10-extension-et-réduction-des-volumes-logiques)
11. [RAID logiciel avec mdadm](#11-raid-logiciel-avec-mdadm)
12. [Le swap et la mémoire virtuelle](#12-le-swap-et-la-mémoire-virtuelle)
13. [Quotas de stockage par utilisateur et groupe](#13-quotas-de-stockage-par-utilisateur-et-groupe)
14. [Permissions et stockage partagé](#14-permissions-et-stockage-partagé)
15. [Surveillance, diagnostic et alertes](#15-surveillance-diagnostic-et-alertes)
16. [Sauvegarde, restauration et résilience](#16-sauvegarde-restauration-et-résilience)
17. [Sécurité et bonnes pratiques d'administration](#17-sécurité-et-bonnes-pratiques-dadministration)
18. [Laboratoires pratiques guidés](#18-laboratoires-pratiques-guidés)
19. [Exercices d'entraînement](#19-exercices-dentraînement)
20. [Défi final : administrer le stockage d'un serveur Linux](#20-défi-final--administrer-le-stockage-dun-serveur-linux)
21. [Correction détaillée du défi final](#21-correction-détaillée-du-défi-final)
22. [Checklist d'exploitation](#22-checklist-dexploitation)
23. [Fiche de révision et commandes essentielles](#23-fiche-de-révision-et-commandes-essentielles)
24. [Conclusion](#24-conclusion)


# 1. Présentation du niveau intermédiaire

## 1.1. Objectif général

Au niveau débutant, nous avons appris à reconnaître l'arborescence Linux, comprendre les permissions, identifier les systèmes de fichiers et utiliser les commandes de base pour consulter l'espace disque.

Au niveau intermédiaire, nous allons apprendre à administrer un stockage dans des conditions proches de celles d'un serveur en production.

Un administrateur doit notamment savoir :

- Ajouter un disque à un serveur Linux.
- Créer et identifier des partitions.
- Choisir un système de fichiers adapté à un usage.
- Monter un système de fichiers automatiquement au démarrage.
- Diagnostiquer un disque presque plein.
- Étendre un espace de stockage grâce à LVM.
- Comprendre les mécanismes de redondance avec RAID.
- Définir des limites de consommation pour les utilisateurs.
- Surveiller l'état du stockage.
- Préparer une stratégie de sauvegarde et de restauration.
- Réduire les risques de perte de données pendant une opération de maintenance.

La maîtrise du stockage ne se limite pas à connaître les commandes. Elle nécessite de comprendre les conséquences de chaque action.

Une commande de partitionnement peut rendre les données inaccessibles. Une mauvaise modification de `/etc/fstab` peut empêcher un serveur de démarrer normalement. Une extension mal réalisée peut aggraver un incident.

Nous allons donc toujours associer trois compétences :

1. **Observer** : identifier l'état réel du système.
2. **Planifier** : déterminer la modification nécessaire.
3. **Exécuter et vérifier** : effectuer l'opération, puis contrôler son résultat.

## 1.2. Prérequis

Avant de commencer, il faut savoir :

- Utiliser un terminal Linux.
- Exécuter des commandes avec `sudo`.
- Comprendre les fichiers, répertoires, propriétaires et permissions.
- Lire les informations affichées par `lsblk`, `df`, `du` et `findmnt`.
- Utiliser des commandes simples comme `mkdir`, `cp`, `mv`, `chmod` et `chown`.

Il est également utile de connaître les notions de disque, partition, montage et système de fichiers.

## 1.3. Environnement recommandé

Le cours peut être suivi sur une machine virtuelle Debian, Ubuntu, Rocky Linux ou une distribution Linux équivalente.

Environnement conseillé :

- Une machine virtuelle Linux.
- Un utilisateur disposant de droits `sudo`.
- Un disque système existant.
- Un ou plusieurs disques virtuels supplémentaires pour les exercices.
- Une sauvegarde ou un instantané de la machine virtuelle avant les laboratoires.

Les commandes disponibles et les noms des paquets peuvent varier suivant la distribution.

## 1.4. Règle de sécurité essentielle

> **Ne formate jamais un disque avant d'avoir confirmé son identité et vérifié qu'il ne contient aucune donnée à conserver.**

Les noms tels que `/dev/sdb`, `/dev/sdc` ou `/dev/nvme1n1` sont des exemples. Ils ne désignent pas nécessairement les mêmes périphériques sur deux machines différentes.

Avant toute modification importante, examine le système :

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,UUID,MOUNTPOINTS
```

Puis vérifie les montages :

```bash
findmnt
```

Enfin, consulte l'espace utilisé :

```bash
df -hT
```

Ces commandes permettent de réduire le risque de manipuler le mauvais périphérique.


# 2. Rappel des fondamentaux du stockage Linux

## 2.1. Le chemin suivi par les données

Dans un système Linux classique, les données passent par plusieurs couches avant d'être écrites sur un support physique.

```text
                 APPLICATION
                      |
                      v
             Fichier ou répertoire
                      |
                      v
             Système de fichiers
              ext4, XFS, Btrfs...
                      |
                      v
              Couche de stockage
            Partition ou volume LVM
                      |
                      v
              Périphérique bloc
           Disque, SSD ou stockage virtuel
                      |
                      v
              Support physique
```

Cette représentation décrit une architecture possible, et non une obligation. Un système peut utiliser un système de fichiers directement sur un disque, sur une partition, sur un volume logique LVM ou sur un périphérique RAID.

### Exemple simple

Considérons le fichier :

```text
/var/log/application.log
```

Ce fichier est situé dans le répertoire `/var/log`.

Si `/var` est un point de montage indépendant, ses données peuvent se trouver sur un autre volume que celui qui contient `/`.

Si `/var` n'est pas monté séparément, le fichier réside généralement sur le système de fichiers qui contient `/`.

Pour déterminer le système de fichiers utilisé par ce fichier :

```bash
findmnt -T /var/log/application.log
```

Cette commande affiche le montage qui héberge le chemin demandé.

## 2.2. Les principales couches à distinguer

| Élément | Fonction | Exemple |
|---|---|---|
| Disque | Support de stockage physique ou virtuel | `/dev/sdb` |
| Partition | Découpage d'un disque | `/dev/sdb1` |
| Système de fichiers | Organise les fichiers et leurs métadonnées | ext4, XFS |
| Point de montage | Emplacement où le système de fichiers devient accessible | `/data` |
| Volume physique LVM | Périphérique intégré à LVM | `/dev/sdb1` |
| Groupe de volumes | Réserve d'espace administrée par LVM | `vgdata` |
| Volume logique | Volume créé dans un groupe LVM | `lvarchives` |
| RAID logiciel | Regroupe plusieurs périphériques en un ensemble RAID | `/dev/md0` |

Ces éléments ne sont pas interchangeables.

Un disque peut contenir plusieurs partitions. Une partition peut contenir un système de fichiers ou servir de composant à une autre couche de stockage. Un point de montage n'est pas un disque : c'est un emplacement dans l'arborescence Linux.

## 2.3. Comprendre le montage

Prenons un volume contenant un système de fichiers ext4.

```text
Périphérique : /dev/sdb1
Système      : ext4
Point        : /data
```

Lorsqu'il est monté :

```text
/dev/sdb1
    |
    | montage
    v
/data
    |
    +--- rapports/
    +--- archives/
    +--- projets/
```

Les fichiers sont accessibles à travers `/data`.

Attention : si des fichiers existaient déjà dans `/data` avant le montage, ils ne sont pas automatiquement supprimés, mais ils deviennent masqués par le contenu du système de fichiers monté. Ils réapparaîtront généralement après le démontage.

C'est une source fréquente de confusion lorsqu'un administrateur monte un nouveau volume sur un répertoire déjà utilisé.

## 2.4. Capacité, occupation et disponibilité

Trois notions doivent être distinguées :

- **Capacité totale** : espace global fourni par le système de fichiers.
- **Espace utilisé** : espace actuellement consommé.
- **Espace disponible** : espace encore utilisable selon les règles du système de fichiers et les privilèges.

Exemple :

```bash
df -hT /data
```

Sortie illustrative :

```text
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sdb1      ext4   100G   72G   23G  76% /data
```

Interprétation :

- La capacité totale affichée est de 100 Go.
- Environ 72 Go sont utilisés.
- Environ 23 Go sont disponibles.
- L'occupation affichée est de 76 %.

Les chiffres sont arrondis : ils ne s'additionnent pas toujours exactement en raison des métadonnées, des réservations et de l'arrondi.

Autre point important : la taille d'un fichier n'est pas nécessairement égale à l'espace réellement occupé sur le disque. Les fichiers creux, la compression, les allocations différées et les instantanés peuvent modifier cette relation.


# 3. Identifier et analyser les périphériques de stockage

Avant de créer une partition ou un volume, l'administrateur doit comprendre l'état du matériel et les couches déjà présentes.

## 3.1. Afficher les disques et leurs partitions

Commande :

```bash
lsblk
```

Version détaillée :

```bash
lsblk -o NAME,MODEL,SIZE,TYPE,FSTYPE,FSVER,LABEL,UUID,MOUNTPOINTS
```

Cette commande permet d'identifier :

- Le nom du périphérique.
- Son modèle, lorsque cette information est disponible.
- Sa capacité.
- Son type : disque, partition ou autre objet bloc.
- Le système de fichiers détecté.
- Le label.
- L'UUID.
- Les points de montage.

Exemple :

```text
NAME        SIZE TYPE FSTYPE LABEL UUID                                 MOUNTPOINTS
sda          80G disk
├─sda1      512M part vfat         AAAA-BBBB                            /boot/efi
├─sda2        2G part ext4         11111111-2222-3333-4444-555555555555  /boot
└─sda3     77.5G part LVM2_member
  ├─vg0-root  40G lvm  ext4                                             /
  └─vg0-var   15G lvm  ext4                                             /var
sdb         200G disk
```

Dans cet exemple, `sda` contient le système. Le périphérique `sdb` semble être un disque supplémentaire non encore utilisé.

Toutefois, l'absence de système de fichiers ou de point de montage ne prouve pas qu'un disque ne contient aucune donnée utile. Il pourrait contenir une partition non reconnue, une signature ancienne ou des métadonnées de stockage.

Il faut approfondir les vérifications avant de le modifier.

## 3.2. Afficher les systèmes de fichiers connus

```bash
lsblk -f
```

Cette commande est particulièrement utile avant une opération de montage.

Pour rechercher les signatures présentes sur un périphérique :

```bash
sudo blkid
```

Pour interroger un périphérique précis :

```bash
sudo blkid /dev/sdb
```

Une absence de résultat ne constitue pas une garantie absolue que le périphérique soit vide.

## 3.3. Examiner les montages

```bash
findmnt
```

Pour connaître le système de fichiers portant un chemin :

```bash
findmnt -T /var
```

Pour afficher uniquement certains champs :

```bash
findmnt -o SOURCE,TARGET,FSTYPE,OPTIONS
```

Ces commandes permettent de savoir si un chemin dépend d'un montage dédié et d'identifier les options effectivement utilisées.

## 3.4. Analyser les périphériques en espace et en capacité

```bash
df -hT
```

Pour les inodes :

```bash
df -i
```

Les inodes représentent les structures de métadonnées utilisées pour représenter les fichiers et certains objets du système de fichiers.

Un système peut manquer d'inodes même si plusieurs gigaoctets sont encore disponibles.

C'est possible, par exemple, lorsqu'une application produit des millions de petits fichiers.

Exemple :

```text
Filesystem     Inodes  IUsed  IFree IUse% Mounted on
/dev/sdb1     1000000 990000  10000   99% /data
```

Ici, l'occupation des inodes atteint 99 %. Il faut investiguer le nombre de fichiers et leur emplacement, même si `df -h` ne montre pas encore un disque plein.

## 3.5. Consulter les messages du noyau

Pour afficher les messages récents :

```bash
sudo dmesg --level=err,warn
```

Pour rechercher certains messages liés au stockage :

```bash
sudo dmesg | grep -Ei 'I/O error|filesystem|nvme|ata|scsi|ext4|xfs'
```

Avec systemd, on peut aussi examiner les journaux du démarrage courant :

```bash
sudo journalctl -k -b
```

Des erreurs d'entrée-sortie répétées, des réinitialisations de périphériques ou des erreurs de système de fichiers peuvent indiquer un problème nécessitant une investigation.

**Ne conclus pas automatiquement qu'un disque est défectueux à partir d'un seul message.** Il faut corréler les journaux, l'état matériel, les événements récents et les symptômes.

## 3.6. Diagnostic guidé : « Le disque est plein »

Supposons que `/data` soit presque plein.

Commence par mesurer l'occupation du système de fichiers :

```bash
df -hT /data
```

Vérifie également les inodes :

```bash
df -i /data
```

Puis identifie les répertoires les plus volumineux :

```bash
sudo du -xhd1 /data 2>/dev/null | sort -h
```

Sur les systèmes dont la version de `du` ne prend pas en charge `-d` :

```bash
sudo du -xh --max-depth=1 /data 2>/dev/null | sort -h
```

Le paramètre `-x` évite de parcourir les autres systèmes de fichiers montés sous le chemin étudié. C'est utile pour ne pas confondre plusieurs volumes.

Pour rechercher des fichiers volumineux :

```bash
sudo find /data -xdev -type f -size +1G -printf '%s %p\n' 2>/dev/null
```

La taille indiquée par `find` est exprimée en octets dans cet exemple. Pour lire la sortie plus facilement, on peut employer :

```bash
sudo find /data -xdev -type f -size +1G -exec du -h {} + 2>/dev/null
```

N'efface jamais un fichier uniquement parce qu'il est volumineux. Il peut s'agir d'une base de données, d'un fichier nécessaire à une application ou d'une archive réglementaire.


# 4. Partitions, GPT et outils de partitionnement

## 4.1. Pourquoi partitionner un disque ?

Le partitionnement divise l'espace adressable d'un disque en régions distinctes.

Exemple :

```text
Disque /dev/sdb : 200 Go
┌──────────────────────────────────────────────┐
│                  /dev/sdb                    │
├───────────────────────┬──────────────────────┤
│       /dev/sdb1       │      /dev/sdb2       │
│         80 Go         │        120 Go        │
└───────────────────────┴──────────────────────┘
```

Chaque partition peut ensuite recevoir un système de fichiers, servir à LVM ou être utilisée par une autre couche de stockage.

Le partitionnement ne crée pas, à lui seul, un système de fichiers exploitable pour les fichiers ordinaires.

## 4.2. MBR et GPT

Deux formats de table de partitions sont couramment rencontrés.

| Caractéristique | MBR | GPT |
|---|---|---|
| Nom complet | Master Boot Record | GUID Partition Table |
| Architecture | Ancien format | Format moderne |
| Nombre de partitions | Quatre entrées principales au maximum, avec partitions logiques possibles | De nombreuses partitions, selon l'implémentation |
| Disques de grande capacité | Limites importantes avec l'adressage traditionnel de 32 bits | Adapté aux très grandes capacités |
| Redondance de la table | Limitée | Métadonnées principales et copie de secours |
| Usage actuel | Compatibilité avec certains anciens systèmes | Choix courant pour les nouveaux disques |

GPT est généralement préférable pour un nouveau disque, sauf contrainte de compatibilité particulière.

## 4.3. Examiner la table de partitions

Commande :

```bash
sudo fdisk -l
```

Pour un périphérique particulier :

```bash
sudo fdisk -l /dev/sdb
```

Pour afficher le type de table et les informations des partitions :

```bash
sudo parted /dev/sdb print
```

Ces commandes permettent d'inspecter l'organisation actuelle du disque. Elles ne nécessitent pas de créer ou de supprimer des partitions.

## 4.4. Créer une table GPT et une partition avec `parted`

> **Attention : l'étape de création d'une nouvelle table de partitions peut rendre les partitions existantes inaccessibles.** La procédure suivante est destinée à un disque de test préalablement identifié et dont les données peuvent être détruites.

Supposons qu'un disque de laboratoire soit identifié comme `/dev/sdb` et qu'il soit dédié à cet exercice.

Vérifie d'abord :

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
sudo fdisk -l /dev/sdb
findmnt
```

Vérifie également que le disque n'appartient pas à un groupe LVM, à un ensemble RAID ou à un autre système de stockage que tu dois préserver.

Pour créer une nouvelle table GPT :

```bash
sudo parted /dev/sdb --script mklabel gpt
```

Créer une partition occupant une partie du disque, de 1 MiB à 50 GiB :

```bash
sudo parted /dev/sdb --script mkpart primary 1MiB 50GiB
```

Vérifier la nouvelle organisation :

```bash
sudo parted /dev/sdb print
lsblk /dev/sdb
```

Selon l'environnement, le noyau peut nécessiter une actualisation de la table de partitions ou une nouvelle détection du périphérique avant que tous les outils voient la modification.

Ne poursuis pas tant que la partition attendue n'est pas visible.

## 4.5. Créer un système de fichiers

Supposons que la partition de test soit `/dev/sdb1`.

Avant tout formatage :

```bash
lsblk -f /dev/sdb
sudo blkid /dev/sdb1
findmnt /dev/sdb1
```

Si la partition est réellement réservée au laboratoire et qu'aucune donnée n'est à conserver, un système de fichiers ext4 peut être créé :

```bash
sudo mkfs.ext4 -L DATA_TEST /dev/sdb1
```

Explication :

- `mkfs.ext4` crée un système de fichiers ext4.
- `-L DATA_TEST` attribue le label `DATA_TEST`.
- `/dev/sdb1` désigne le périphérique cible dans cet exemple.

Cette opération n'est pas une simple vérification : elle écrit des structures de système de fichiers sur la cible et peut détruire les données antérieures.

Vérifier ensuite :

```bash
sudo blkid /dev/sdb1
lsblk -f /dev/sdb
```

## 4.6. Monter le nouveau système de fichiers

Créer le point de montage :

```bash
sudo mkdir -p /data
```

Monter le périphérique :

```bash
sudo mount /dev/sdb1 /data
```

Vérifier le résultat :

```bash
findmnt /data
df -hT /data
```

Tester l'écriture :

```bash
sudo touch /data/test-stockage.txt
sudo ls -l /data
```

Si le test est terminé et qu'il n'est pas nécessaire de conserver le montage :

```bash
sudo umount /data
```

Le démontage échouera si le système considère le volume comme occupé. Il faut alors identifier le processus qui l'utilise au lieu de forcer immédiatement le démontage.

Pour diagnostiquer l'utilisation :

```bash
sudo fuser -vm /data
```


# 5. UUID, montages persistants et fichier /etc/fstab

## 5.1. Pourquoi le montage manuel ne suffit pas

Cette commande :

```bash
sudo mount /dev/sdb1 /data
```

monte le volume jusqu'à ce qu'il soit démonté, ou jusqu'à un événement qui supprime ce montage.

Pour obtenir un montage automatique au démarrage, Linux utilise généralement `/etc/fstab`.

Ce fichier décrit les systèmes de fichiers à monter et plusieurs options associées.

## 5.2. Le problème des noms de périphériques

Les noms comme `/dev/sdb1` dépendent de l'ordre dans lequel les périphériques sont détectés.

Dans certaines architectures, un changement matériel ou une modification de configuration peut modifier les noms attribués.

Pour rendre la configuration plus robuste, on peut identifier un système de fichiers par son UUID.

Exemple :

```text
UUID=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
```

L'UUID est un identifiant du système de fichiers. Il ne faut pas le confondre avec le nom du disque ni avec un identifiant de volume RAID ou LVM.

Pour retrouver l'UUID :

```bash
sudo blkid /dev/sdb1
```

Ou :

```bash
lsblk -f
```

## 5.3. Comprendre les six champs de `/etc/fstab`

Une ligne classique peut ressembler à ceci :

```fstab
UUID=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee /data ext4 defaults 0 2
```

Les champs sont séparés par des espaces ou des tabulations.

| Champ | Exemple | Rôle |
|---|---|---|
| 1. Source | `UUID=...` | Identifie le système de fichiers |
| 2. Point de montage | `/data` | Répertoire cible |
| 3. Type | `ext4` | Type du système de fichiers |
| 4. Options | `defaults` | Options de montage |
| 5. Dump | `0` | Indicateur historique utilisé par `dump` |
| 6. Pass | `2` | Priorité de vérification au démarrage pour les systèmes de fichiers concernés |

La valeur `2` dans le dernier champ est courante pour un système de fichiers ext4 non racine. Le système de fichiers racine utilise généralement `1` lorsqu'il doit être vérifié par le mécanisme classique de démarrage. Certaines configurations utilisent d'autres comportements, notamment avec XFS ou les distributions qui s'appuient sur d'autres mécanismes de vérification.

Ne copie pas mécaniquement une ligne dans un système existant sans comprendre son type de stockage et son mode de démarrage.

## 5.4. Modifier `/etc/fstab` avec prudence

Avant la modification :

```bash
sudo cp -a /etc/fstab /etc/fstab.bak
```

Récupérer l'UUID réel :

```bash
sudo blkid /dev/sdb1
```

Éditer le fichier :

```bash
sudo nano /etc/fstab
```

Ajouter une ligne correspondant aux informations réelles de la partition.

Exemple fictif :

```fstab
UUID=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee /data ext4 defaults 0 2
```

Ne laisse pas la chaîne fictive `aaaaaaaa-...` dans le fichier : elle doit être remplacée par l'UUID exact.

Avant de redémarrer, demander au système de vérifier la configuration :

```bash
sudo findmnt --verify --verbose
```

Cette vérification peut détecter des erreurs de configuration et des références manquantes. Elle ne garantit pas que tous les systèmes de fichiers pourront être montés dans toutes les situations.

Si `/data` est déjà monté, on peut vérifier la déclaration :

```bash
findmnt --fstab --target /data
```

Pour tester les montages déclarés qui ne sont pas encore montés :

```bash
sudo mount -a
```

**Ne redémarre pas tant que des erreurs de configuration pertinentes restent présentes.**

Après les tests, contrôler le résultat :

```bash
findmnt /data
df -hT /data
```

## 5.5. Options de montage utiles

Les options dépendent du système de fichiers et de l'usage.

| Option | Fonction générale | Exemple d'utilisation |
|---|---|---|
| `defaults` | Active les options par défaut du système | Montage général |
| `ro` | Monte en lecture seule | Données qui ne doivent pas être modifiées par ce montage |
| `rw` | Autorise les opérations de lecture et d'écriture si le système le permet | Volume de données actif |
| `noatime` | Évite les mises à jour classiques de la date de dernier accès | Réduction de certaines écritures de métadonnées |
| `nodev` | Empêche l'utilisation de périphériques spéciaux présents sur le système de fichiers | Certains volumes utilisateurs |
| `nosuid` | Ignore les effets des bits SUID et SGID sur les fichiers concernés | Certains volumes de données |
| `noexec` | Empêche l'exécution directe de fichiers depuis le système de fichiers dans les conditions normales | Certains volumes d'importation |
| `nofail` | Permet de traiter certains échecs de montage comme non bloquants pendant le démarrage | Disque de données optionnel |

Une option n'est pas une garantie de sécurité absolue.

Par exemple, `noexec` ne remplace pas une politique de contrôle d'accès et n'empêche pas toutes les utilisations possibles du contenu d'un fichier par d'autres interpréteurs ou programmes.

De même, l'emploi de `nofail` ne doit pas masquer le fait qu'une application a besoin d'un stockage indispensable. Un service peut démarrer sans son volume, puis créer des fichiers sur le système de fichiers parent au mauvais endroit.

## 5.6. Exemple d'une ligne plus restrictive

Pour un volume ext4 utilisé comme espace de dépôt de fichiers non exécutables :

```fstab
UUID=UUID_REEL /data ext4 defaults,nodev,nosuid,noexec 0 2
```

`UUID_REEL` est un marqueur explicatif, pas un UUID valide à copier tel quel.

Avant d'appliquer ces options, vérifie que les applications exécutées depuis ce volume n'en dépendent pas.


# 6. Systèmes de fichiers : ext4, XFS et Btrfs

## 6.1. Pourquoi plusieurs systèmes de fichiers ?

Le système de fichiers détermine la manière dont Linux organise les données, leurs métadonnées et certaines opérations de maintenance.

Il influence notamment :

- Les performances selon la charge.
- La gestion des fichiers volumineux.
- La récupération après certains incidents.
- Les possibilités d'instantanés.
- Les opérations d'extension ou de réduction.
- Les outils de diagnostic disponibles.

Il n'existe pas un système de fichiers idéal pour tous les environnements.

## 6.2. ext4

ext4 est un système de fichiers généraliste très répandu.

Ses points forts incluent :

- Une large disponibilité.
- Des outils de maintenance connus.
- Une bonne prise en charge des usages courants.
- La possibilité d'agrandir un système de fichiers dans les conditions appropriées.

Commandes courantes :

```bash
sudo mkfs.ext4 /dev/sdb1
```

Cette commande crée un système de fichiers ext4 sur une cible. Elle peut détruire les données antérieures.

Informations sur un système ext4 :

```bash
sudo tune2fs -l /dev/sdb1
```

Inspection du système de fichiers :

```bash
sudo dumpe2fs -h /dev/sdb1
```

Ces outils ne doivent pas être utilisés aveuglément sur un périphérique dont la nature n'est pas établie.

## 6.3. XFS

XFS est un système de fichiers robuste, notamment courant sur les serveurs Linux d'entreprise.

Il est conçu pour gérer de grands systèmes de fichiers et convient à de nombreux scénarios de données et de charge importante.

Création sur un périphérique de test dédié :

```bash
sudo mkfs.xfs /dev/sdb1
```

Cette opération est destructive si le périphérique contient des données.

Afficher ses informations :

```bash
sudo xfs_info /data
```

Cette commande s'applique à un système de fichiers XFS monté dans cet exemple.

**Particularité importante : XFS ne prend pas en charge la réduction du système de fichiers sur place par une opération équivalente à une réduction ext4.** Une stratégie de réduction implique généralement sauvegarde des données, recréation avec une taille adaptée, puis restauration.

## 6.4. Btrfs

Btrfs est un système de fichiers qui fournit notamment des sommes de contrôle des données et des métadonnées, ainsi que des sous-volumes et des instantanés selon la configuration.

Ces fonctions permettent des stratégies de gestion différentes de celles d'un ext4 traditionnel.

Exemple de consultation :

```bash
sudo btrfs filesystem usage /data
```

Afficher les systèmes de fichiers et sous-volumes, selon le montage :

```bash
sudo btrfs filesystem show
sudo btrfs subvolume list /data
```

Btrfs offre des fonctionnalités évoluées, mais elles doivent être comprises avant d'être intégrées à une procédure opérationnelle.

Un instantané Btrfs n'est pas automatiquement une sauvegarde indépendante : la perte du support contenant les données peut également faire perdre les instantanés qui s'y trouvent.

## 6.5. Comparaison pratique

| Critère | ext4 | XFS | Btrfs |
|---|---|---|---|
| Usage général | Excellent | Excellent | Adapté selon l'architecture |
| Outils de diagnostic | `e2fsck`, `tune2fs` | `xfs_repair`, `xfs_info` | `btrfs check`, outils Btrfs dédiés |
| Extension | Possible sous conditions | Possible sous conditions | Possible selon la configuration |
| Réduction du système de fichiers | Possible hors ligne avec procédure adaptée | Pas de réduction sur place | Possible selon l'opération et la configuration |
| Instantanés natifs du système de fichiers | Non | Non | Oui, par sous-volumes |
| Complexité opérationnelle | Faible à modérée | Faible à modérée | Modérée à élevée |

Le choix doit correspondre aux besoins, à la distribution, à la stratégie de maintenance et aux compétences disponibles.


# 7. Maintenance et réparation des systèmes de fichiers

## 7.1. Le système de fichiers présente des erreurs

Des erreurs peuvent apparaître après :

- Une panne d'alimentation.
- Un incident matériel.
- Des erreurs d'entrée-sortie.
- Un problème survenu pendant une écriture.
- Un défaut logiciel.
- Une défaillance d'une couche de stockage sous-jacente.

Il faut d'abord distinguer les erreurs logiques du système de fichiers d'un problème matériel.

Si des erreurs d'entrée-sortie persistent, une réparation logicielle ne suffit pas à résoudre le problème matériel sous-jacent.

## 7.2. Vérifier sans réparer aveuglément

Pour un système de fichiers ext4, on peut observer des informations sans lancer immédiatement une réparation :

```bash
lsblk -f
findmnt
df -hT
sudo dmesg --level=err,warn
```

Le contrôle complet d'un système de fichiers et la réparation sont des opérations différentes.

Les outils comme `e2fsck` sont généralement exécutés sur un système de fichiers ext4 démonté, sauf cas particuliers documentés par leur manuel. Sur un système de fichiers monté en écriture, une vérification ou réparation improvisée peut mettre les données en danger.

## 7.3. Vérification ext4

Pour consulter la documentation :

```bash
man e2fsck
```

Sur un volume ext4 de test démonté :

```bash
sudo umount /dev/sdb1
sudo e2fsck -f /dev/sdb1
```

Cette commande vérifie le système de fichiers et peut demander des décisions si des problèmes sont détectés, selon les options utilisées.

Vérifie que `/dev/sdb1` est bien la partition attendue et non une partition système.

Ne lance pas cette commande sur un périphérique monté en écriture.

Si le système de fichiers contient des données importantes, une sauvegarde ou une image de récupération peut être nécessaire avant toute réparation.

## 7.4. Maintenance XFS

La vérification et la réparation XFS reposent sur des outils différents de ceux d'ext4.

Documentation :

```bash
man xfs_repair
man xfs_info
```

Pour examiner un volume XFS monté :

```bash
sudo xfs_info /data
```

Une réparation XFS classique se réalise généralement sur un système de fichiers démonté. Il faut déterminer la procédure correspondant aux symptômes et à la version du système.

Ne lance pas automatiquement une réparation avec une option qui supprime ou reconstruit des métadonnées sans avoir mesuré les conséquences possibles.

## 7.5. Pourquoi ne pas employer `fsck` aveuglément ?

`fsck` est une interface qui peut appeler l'outil de vérification correspondant au type de système de fichiers.

Cela ne signifie pas que toutes les familles de systèmes de fichiers se réparent avec les mêmes options, ni qu'une réparation peut être exécutée sans risque sur un système actif.

La méthode correcte est :

1. Identifier le type du système de fichiers.
2. Identifier les symptômes.
3. Consulter les outils correspondant à ce type.
4. Vérifier si le volume doit être démonté.
5. Sauvegarder les données importantes lorsque cela est possible.
6. Exécuter la vérification ou la réparation appropriée.
7. Contrôler le résultat.
8. Examiner la cause initiale de l'incident.


# 8. Gestion avancée de l'espace disque

## 8.1. Mesurer l'occupation globale

La commande :

```bash
df -hT
```

présente l'occupation par système de fichiers.

Mais elle ne permet pas toujours d'identifier les répertoires responsables.

Pour analyser un chemin précis :

```bash
sudo du -xhd1 /var 2>/dev/null | sort -h
```

La commande `du` estime l'espace associé aux fichiers parcourus. Elle ne fournit pas la même information que `df`, car les deux outils n'utilisent pas le même point de vue.

Des écarts sont possibles à cause :

- Des fichiers supprimés encore ouverts par un processus.
- Des différences d'allocation.
- Des fichiers masqués sous un autre montage.
- Des réservations du système de fichiers.
- Des instantanés ou d'autres fonctions propres au système.

## 8.2. Rechercher les gros fichiers supprimés mais encore ouverts

Un cas fréquent se produit lorsqu'une application conserve un fichier journal ouvert après sa suppression.

Le nom du fichier a disparu du répertoire, mais le processus garde une référence vers ses données. L'espace n'est donc pas nécessairement libéré.

Pour rechercher ces fichiers, si `lsof` est installé :

```bash
sudo lsof +L1
```

Repère les lignes indiquant un nombre de liens nul ou des fichiers supprimés encore ouverts.

La solution est généralement de faire en sorte que l'application ferme le fichier concerné ou le recrée correctement. Selon le service, cela peut nécessiter une rotation des journaux ou un rechargement contrôlé.

Ne tue pas automatiquement tous les processus affichés. Une interruption brutale peut affecter une application de production.

## 8.3. Utiliser des limites de taille pour les journaux

Les journaux peuvent consommer beaucoup d'espace si leur rotation et leur rétention ne sont pas adaptées.

Avec systemd, consulter l'espace occupé par le journal :

```bash
journalctl --disk-usage
```

Nettoyer les journaux anciens en conservant une fenêtre de rétention adaptée :

```bash
sudo journalctl --vacuum-time=14d
```

Cette commande supprime certaines archives de journaux selon l'âge. Elle n'est pas une sauvegarde.

On peut aussi limiter la taille des journaux conservés :

```bash
sudo journalctl --vacuum-size=1G
```

Cette action retire des archives pour se rapprocher de la limite indiquée. Elle ne remplace pas une configuration durable de rétention et ne doit pas violer les obligations de conservation des journaux.

## 8.4. Vérifier la consommation d'un utilisateur

Pour analyser les fichiers appartenant à un compte :

```bash
sudo find /data -xdev -user alice -type f -printf '%s %p\n' 2>/dev/null
```

Pour totaliser l'espace selon une arborescence :

```bash
sudo du -sh /data/utilisateurs/alice
```

`du` ne garantit pas que le total corresponde parfaitement à un quota logique si le système utilise des fichiers creux, des reflinks ou des fonctionnalités spécifiques de stockage.

Il faut choisir l'outil adapté au système de fichiers et au mécanisme de quotas employé.

## 8.5. Anticiper le manque d'espace

Il est généralement préférable d'intervenir avant que le volume soit presque plein.

Exemple de seuils d'alerte à adapter :

```text
Occupation < 70 %       : surveillance normale
Occupation >= 70 %      : vérifier la tendance
Occupation >= 85 %      : investigation et plan d'action
Occupation >= 95 %      : intervention prioritaire
Occupation = 100 %      : incident potentiel
```

Ces seuils sont des exemples de politique opérationnelle, et non des valeurs universelles.

Un volume contenant des fichiers volumineux et peu nombreux n'a pas le même profil de risque qu'un volume contenant des millions de petits fichiers.

Il faut surveiller à la fois :

- Les octets disponibles.
- Les inodes disponibles.
- La vitesse de croissance.
- La latence des opérations d'entrée-sortie.
- Les erreurs matérielles et logicielles.


# 9. LVM : Logical Volume Manager

## 9.1. Pourquoi utiliser LVM ?

LVM est une couche de gestion logique du stockage sous Linux.

Elle permet de séparer la représentation du stockage pour les applications de l'organisation physique des disques.

Sans LVM, une organisation traditionnelle peut ressembler à ceci :

```text
Disque /dev/sdb
       |
       v
Partition /dev/sdb1
       |
       v
Système de fichiers ext4
       |
       v
Montage /data
```

Avec LVM :

```text
         /dev/sdb1                /dev/sdc1
             |                         |
             v                         v
      Volume physique PV        Volume physique PV
             |                         |
             +------------+------------+
                          |
                          v
                   Groupe de volumes
                       vgdata
                          |
                +---------+---------+
                |                   |
                v                   v
          Volume logique LV   Volume logique LV
             lvprojects         lvarchives
                |                   |
                v                   v
             Système              Système
           de fichiers           de fichiers
                |                   |
                v                   v
             /data/projects      /data/archives
```

La représentation est conceptuelle : LVM peut répartir les extents sur plusieurs volumes physiques selon sa configuration. La topologie réelle doit être examinée avant toute opération.

## 9.2. Les trois composants fondamentaux

### Physical Volume — PV

Un volume physique est un périphérique ou une partition préparé pour être utilisé par LVM.

Exemples :

```text
/dev/sdb1
/dev/sdc1
```

### Volume Group — VG

Le groupe de volumes rassemble l'espace fourni par un ou plusieurs volumes physiques.

Exemple :

```text
vgdata
```

Ce groupe fournit une réserve de capacité à partir de laquelle des volumes logiques sont créés.

### Logical Volume — LV

Un volume logique est un volume créé à l'intérieur d'un groupe.

Exemples :

```text
/dev/vgdata/lvprojects
/dev/vgdata/lvarchives
```

Un système de fichiers peut ensuite être créé sur un volume logique, puis monté dans l'arborescence.

## 9.3. Pourquoi LVM facilite-t-il l'administration ?

Imaginons une application qui écrit ses données dans `/data/projects`.

Le système de fichiers approche de sa limite.

Sans LVM, l'extension peut exiger des opérations de partitionnement ou une migration plus complexe.

Avec LVM, si le groupe de volumes dispose d'espace libre, il est souvent possible d'agrandir le volume logique puis le système de fichiers.

```text
Avant :

vgdata : 100 Go
├── lvprojects : 60 Go
└── lvarchives : 30 Go
    Espace libre : 10 Go

Après extension de lvprojects :

vgdata : 100 Go
├── lvprojects : 70 Go
├── lvarchives : 30 Go
└── Espace libre : 0 Go
```

Ce schéma est illustratif : la capacité est arrondie et les métadonnées peuvent introduire des différences.

LVM ne crée pas d'espace physique. Si le groupe n'a plus d'espace disponible, il faut libérer de la capacité ou ajouter un nouveau périphérique compatible.

## 9.4. Préparer un laboratoire LVM

Le laboratoire suivant suppose un disque ou une partition réservée aux exercices.

Par exemple :

```text
/dev/sdb1 : partition de test destinée à LVM
```

**Ne réutilise pas une partition qui contient déjà un système de fichiers, des données, des métadonnées LVM utiles ou un composant RAID.**

Avant de continuer :

```bash
lsblk -f
sudo pvs
sudo vgs
sudo lvs
```

Si l'outil est absent, installe le paquet correspondant à la distribution. Sur Debian ou Ubuntu, le paquet courant est généralement `lvm2` :

```bash
sudo apt update
sudo apt install lvm2
```

Sur les systèmes compatibles avec DNF :

```bash
sudo dnf install lvm2
```

Adapte la méthode d'installation à ton système.

## 9.5. Créer un volume physique

Sur une partition de test vide, explicitement destinée à LVM :

```bash
sudo pvcreate /dev/sdb1
```

Cette commande initialise les métadonnées LVM sur la cible. Elle ne doit pas être lancée sur un périphérique dont l'utilisation antérieure n'a pas été vérifiée.

Vérifier :

```bash
sudo pvs
sudo pvdisplay /dev/sdb1
```

Exemple de résultat conceptuel :

```text
PV         VG     Fmt  Attr PSize   PFree
/dev/sdb1         lvm2 ---  100 GiB 100 GiB
```

Tant que le volume physique n'est pas affecté à un groupe, il peut apparaître sans nom de groupe de volumes.

## 9.6. Créer un groupe de volumes

Créer un groupe nommé `vgdata` :

```bash
sudo vgcreate vgdata /dev/sdb1
```

Vérifier :

```bash
sudo vgs
sudo vgdisplay vgdata
```

Le groupe dispose maintenant d'une réserve d'espace que l'on pourra affecter à un ou plusieurs volumes logiques.

## 9.7. Créer un volume logique

Créer un volume logique de 20 GiB :

```bash
sudo lvcreate -L 20G -n lvprojects vgdata
```

Explication :

- `lvcreate` crée un volume logique.
- `-L 20G` définit une taille absolue de 20 GiB dans l'interprétation habituelle des outils LVM.
- `-n lvprojects` attribue le nom `lvprojects`.
- `vgdata` désigne le groupe de volumes.

Vérifier :

```bash
sudo lvs
sudo lvdisplay /dev/vgdata/lvprojects
```

Chemin du volume logique :

```text
/dev/vgdata/lvprojects
```

Selon la distribution, des liens équivalents peuvent exister sous `/dev/mapper/`.

## 9.8. Créer un système de fichiers sur le volume logique

Sur le volume logique fraîchement créé :

```bash
sudo mkfs.ext4 /dev/vgdata/lvprojects
```

Cette étape est nécessaire pour obtenir un système de fichiers ext4. Elle peut détruire les données déjà présentes sur le volume logique ciblé.

Créer un point de montage :

```bash
sudo mkdir -p /data/projects
```

Monter le volume :

```bash
sudo mount /dev/vgdata/lvprojects /data/projects
```

Vérifier le résultat :

```bash
findmnt /data/projects
df -hT /data/projects
```

Tester l'accès :

```bash
sudo touch /data/projects/test-lvm.txt
sudo ls -l /data/projects
```

Nous avons maintenant une architecture complète :

```text
/dev/sdb1
   |
   v
PV
   |
   v
vgdata
   |
   v
lvprojects (20 GiB)
   |
   v
ext4
   |
   v
/data/projects
```

## 9.9. Consulter l'état de LVM

Les commandes principales sont :

```bash
sudo pvs
sudo vgs
sudo lvs
```

Avec des informations plus détaillées :

```bash
sudo pvdisplay
sudo vgdisplay
sudo lvdisplay
```

Pour connaître l'espace libre du groupe :

```bash
sudo vgs -o vg_name,vg_size,vg_free
```

Pour afficher la relation entre groupes et volumes :

```bash
sudo lvs -o lv_name,vg_name,lv_size,devices
```

La colonne `devices` peut aider à comprendre sur quels périphériques se trouvent les segments des volumes logiques.

Cette information est importante avant d'agrandir, de déplacer ou de dépanner un volume.


# 10. Extension et réduction des volumes logiques

## 10.1. Les trois tailles à surveiller

Dans un environnement LVM, la capacité utilisable dépend de plusieurs couches.

```text
Disques / partitions
        |
        v
Capacité disponible pour LVM
        |
        v
Taille du volume logique
        |
        v
Taille du système de fichiers
        |
        v
Espace disponible pour les fichiers
```

Il faut distinguer :

1. L'espace physique réellement disponible.
2. L'espace libre au niveau du groupe de volumes.
3. La capacité du volume logique.
4. La capacité du système de fichiers.
5. L'espace restant pour les données.

Un volume logique peut avoir été agrandi sans que le système de fichiers utilise encore toute cette nouvelle capacité, si l'extension des deux couches n'a pas été effectuée.

## 10.2. Étendre un volume logique

Imaginons :

```text
vgdata
├── lvprojects : 20 GiB
└── Espace libre : 30 GiB
```

Nous souhaitons augmenter `lvprojects` de 10 GiB.

D'abord, vérifier l'état :

```bash
sudo vgs
sudo lvs
df -hT /data/projects
```

Puis :

```bash
sudo lvextend -L +10G /dev/vgdata/lvprojects
```

Cette commande augmente la taille du volume logique de 10 GiB.

Elle ne garantit pas à elle seule que le système de fichiers sera agrandi.

Vérifier :

```bash
sudo lvs
```

## 10.3. Agrandir le système de fichiers ext4

Si le système de fichiers est monté et que les conditions sont compatibles, ext4 permet généralement son extension en ligne.

Commande :

```bash
sudo resize2fs /dev/vgdata/lvprojects
```

Le système de fichiers doit être compatible avec l'opération. Vérifie également qu'il s'agit bien d'ext4 avant d'utiliser `resize2fs`.

Puis :

```bash
df -hT /data/projects
```

Le volume logique et le système de fichiers doivent maintenant présenter la capacité attendue, sous réserve de l'espace réellement attribué et des métadonnées.

## 10.4. Étendre LVM et ext4 en une opération

Pour les versions courantes de LVM, `lvextend` peut demander l'extension du système de fichiers en même temps que celle du volume logique lorsque le type de système de fichiers et l'environnement sont pris en charge.

Exemple :

```bash
sudo lvextend -r -L +10G /dev/vgdata/lvprojects
```

Le paramètre `-r` demande l'agrandissement du système de fichiers lorsque l'outil dispose du support nécessaire.

C'est pratique, mais il faut quand même contrôler :

```bash
sudo lvs
df -hT /data/projects
```

Ne pars pas du principe que toutes les couches ont été agrandies sans consulter le résultat de l'opération.

## 10.5. Utiliser tout l'espace libre du groupe

Si le volume logique doit recevoir tout l'espace libre disponible dans le groupe :

```bash
sudo lvextend -r -l +100%FREE /dev/vgdata/lvprojects
```

Cette commande consomme la totalité de l'espace libre disponible du groupe de volumes.

Elle est donc inadaptée si d'autres volumes logiques doivent encore être créés ou agrandis.

Une extension vers 100 % de l'espace libre peut aussi empêcher des évolutions ultérieures, notamment l'extension d'autres volumes.

Avant d'utiliser cette option, examine :

```bash
sudo vgs
sudo lvs
```

## 10.6. Ajouter un nouveau disque à LVM

Supposons que `/dev/sdc1` soit une nouvelle partition de test destinée à rejoindre `vgdata`.

Vérifier la cible et son rôle :

```bash
lsblk -f
sudo pvs
sudo vgs
```

Si la partition est vide, non utilisée et réservée à cette opération :

```bash
sudo pvcreate /dev/sdc1
sudo vgextend vgdata /dev/sdc1
```

Contrôler ensuite :

```bash
sudo pvs
sudo vgs
```

Le groupe de volumes dispose maintenant d'une capacité supplémentaire.

La création du nouveau volume physique ne déplace pas nécessairement les données déjà présentes sur les périphériques précédents.

Il faut également tenir compte du fait que le groupe de volumes dépend désormais de plusieurs périphériques. La perte d'un périphérique peut affecter les volumes qui y possèdent des extents, sauf configuration spécifique de redondance.

**LVM améliore la flexibilité de gestion, mais ne constitue pas à lui seul une sauvegarde ou une garantie de tolérance aux pannes.**

## 10.7. Réduire un volume logique : opération à risque

La réduction est plus délicate que l'extension, car elle peut supprimer la partie des données qui se trouverait au-delà de la nouvelle limite.

Pour ext4, la procédure comprend généralement :

1. Sauvegarder les données.
2. Vérifier le système de fichiers.
3. Démonter le volume.
4. Réduire le système de fichiers.
5. Réduire le volume logique.
6. Vérifier de nouveau le système de fichiers.
7. Remonter et valider les données.

Il faut toujours respecter l'ordre adapté au système de fichiers.

**Ne réduis jamais d'abord le volume logique sous la taille du système de fichiers qu'il contient.** Tu risquerais de supprimer des blocs nécessaires et de corrompre les données.

Exemple pédagogique, réservé à un volume ext4 de laboratoire vide ou sauvegardé :

Supposons que le volume logique fasse 30 GiB et qu'on veuille le ramener à 20 GiB.

Vérifier le montage :

```bash
findmnt /data/projects
df -hT /data/projects
```

Démonter le système de fichiers :

```bash
sudo umount /data/projects
```

Vérifier ext4 :

```bash
sudo e2fsck -f /dev/vgdata/lvprojects
```

Réduire le système de fichiers à une taille compatible avec la cible :

```bash
sudo resize2fs /dev/vgdata/lvprojects 20G
```

Puis réduire le volume logique à une taille légèrement supérieure ou égale à la taille réelle du système de fichiers, conformément aux unités et contraintes de l'outil :

```bash
sudo lvreduce -L 20G /dev/vgdata/lvprojects
```

Cette dernière commande modifie la limite du volume logique. Elle doit être effectuée uniquement après avoir confirmé que le système de fichiers tient entièrement dans la nouvelle taille.

Puis vérifier :

```bash
sudo e2fsck -f /dev/vgdata/lvprojects
```

Remonter :

```bash
sudo mount /dev/vgdata/lvprojects /data/projects
```

Contrôler les données :

```bash
df -hT /data/projects
sudo ls -la /data/projects
```

Ce scénario illustre l'ordre des opérations, mais la réduction réelle exige de calculer précisément la capacité nécessaire et de suivre la documentation correspondant à l'outil, au système de fichiers et à la version installée.

Si le volume contient des données importantes, la stratégie la plus sûre peut être de créer un nouveau volume à la bonne taille, restaurer les données, vérifier, puis basculer l'application.

## 10.8. Pourquoi la réduction est-elle plus risquée ?

Lors d'une extension, on ajoute de l'espace à la fin du volume ou du système de fichiers. Les données existantes ne doivent généralement pas être déplacées de manière à rendre le volume plus petit.

Lors d'une réduction, l'espace retiré peut contenir des données utiles. Il faut donc que le système de fichiers réorganise les données pour les faire tenir dans la nouvelle limite, puis seulement réduire l'espace qui lui est présenté.

C'est pour cela que le type de système de fichiers change la procédure.

**Pour XFS, ne transpose pas la procédure ext4 : XFS ne prend pas en charge la réduction sur place de son système de fichiers.**


# 11. RAID logiciel avec mdadm

## 11.1. Qu'est-ce que le RAID ?

RAID signifie *Redundant Array of Independent Disks*.

Le RAID combine plusieurs périphériques en une structure logique selon un niveau et une configuration choisis.

Selon le niveau, il peut améliorer :

- La tolérance à certaines pannes.
- Le débit de lecture ou d'écriture.
- L'utilisation de plusieurs périphériques.
- La disponibilité des données.

Le RAID ne garantit pas la protection contre tous les types de pertes.

Une suppression accidentelle, un ransomware, une erreur applicative ou une destruction physique de l'ensemble peuvent affecter les données même sur un RAID redondant.

## 11.2. Les niveaux courants

### RAID 0 : répartition sans redondance

```text
             Données
                |
        +-------+-------+
        |               |
        v               v
     Disque A        Disque B
      Bloc 1          Bloc 2
      Bloc 3          Bloc 4
```

Le RAID 0 répartit les données entre les composants.

Avantages :

- Capacité combinée.
- Possibilité d'augmenter les débits selon la charge.

Inconvénient majeur :

- Une panne d'un composant peut rendre l'ensemble inutilisable.

Le RAID 0 ne doit pas être choisi pour tolérer une panne de disque.

### RAID 1 : miroir

```text
               Données
                  |
           +------+------+
           |             |
           v             v
       Disque A      Disque B
       Copie X        Copie X
       Copie Y        Copie Y
```

Les données sont répliquées sur les composants du miroir.

Avec deux disques de même capacité, la capacité utilisable est approximativement celle d'un disque.

Le RAID 1 peut tolérer la perte d'un composant selon l'état et la configuration de l'ensemble.

### RAID 5 : répartition avec parité

```text
         Disque A   Disque B   Disque C
Bloc 1      D1         D2          P
Bloc 2      D3          P          D4
Bloc 3       P         D5          D6
```

`D` représente des données et `P` une parité distribuée.

Le RAID 5 nécessite au moins trois périphériques et peut tolérer la panne d'un composant dans les conditions prévues par la configuration.

La reconstruction après une panne dépend notamment de la taille des disques, de leur état et de la charge.

### RAID 6 : double parité

Le RAID 6 utilise une double parité distribuée et peut tolérer la panne simultanée de deux composants, sous réserve d'une configuration correcte et d'un ensemble encore récupérable.

Il demande généralement au moins quatre périphériques.

### RAID 10 : miroir et répartition

```text
             RAID 10
                |
          +-----+-----+
          |           |
          v           v
       Miroir A    Miroir B
        /   \       /   \
       A     B     C     D
```

Le RAID 10 associe des groupes en miroir et une répartition des données.

Il nécessite généralement au moins quatre périphériques pour une configuration classique. La capacité utilisable et la tolérance aux pannes dépendent de la disposition des miroirs et des périphériques effectivement perdus.

## 11.3. Comparaison synthétique

| Niveau | Nombre minimal courant | Capacité utile approximative avec disques égaux | Tolérance aux pannes |
|---|---:|---:|---|
| RAID 0 | 2 | Somme des capacités | Aucune panne de composant |
| RAID 1 | 2 | Capacité d'un composant | Généralement un disque dans un miroir à deux composants |
| RAID 5 | 3 | `(N - 1) × capacité du plus petit disque` | Une panne de composant |
| RAID 6 | 4 | `(N - 2) × capacité du plus petit disque` | Deux pannes de composants |
| RAID 10 | 4 | Environ la moitié de la capacité totale | Dépend des miroirs touchés |

Ces estimations supposent des périphériques comparables et une configuration classique. Les métadonnées, les tailles différentes, les réserves et les contraintes d'implémentation peuvent réduire la capacité réelle.

## 11.4. RAID matériel et RAID logiciel

Le RAID matériel est géré par un contrôleur ou un équipement spécialisé.

Le RAID logiciel, sur Linux, peut être géré avec des outils comme `mdadm`.

Le RAID logiciel est directement intégré à l'environnement système et peut être administré avec des commandes Linux.

Il ne faut pas confondre :

- Le RAID, qui gère la disposition et la redondance entre périphériques.
- LVM, qui gère des volumes logiques.
- Le système de fichiers, qui organise les fichiers et les métadonnées.

Ces couches peuvent être combinées, mais leur ordre dépend de l'architecture choisie.

## 11.5. Préparer un environnement RAID

Pour un laboratoire sérieux, utilise des disques virtuels indépendants ou des périphériques de boucle réservés à l'exercice.

Avant de modifier le système :

```bash
lsblk -f
sudo mdadm --detail --scan
cat /proc/mdstat
```

Si nécessaire, installer `mdadm`.

Sur Debian ou Ubuntu :

```bash
sudo apt update
sudo apt install mdadm
```

Sur les distributions utilisant DNF :

```bash
sudo dnf install mdadm
```

La création d'un RAID sur un périphérique réel peut écraser des métadonnées utiles ou rendre les données existantes inaccessibles. Le laboratoire doit être isolé du disque système.

## 11.6. Création pédagogique d'un RAID 1

Ce scénario utilise deux partitions de test, nommées `/dev/sdb1` et `/dev/sdc1`.

**Ces noms sont des exemples. Ne lance aucune commande tant que les périphériques réels n'ont pas été identifiés et confirmés comme étant dédiés au laboratoire.**

Vérifier leur taille et leur état :

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,UUID,MOUNTPOINTS
sudo blkid
cat /proc/mdstat
```

Si les deux partitions sont réellement réservées au laboratoire, non montées et adaptées à la création d'un RAID :

```bash
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb1 /dev/sdc1
```

Cette commande crée un ensemble RAID 1. Elle n'est pas destinée à être exécutée sur des partitions dont le contenu doit être conservé.

Suivre la reconstruction ou la synchronisation :

```bash
watch cat /proc/mdstat
```

Pour quitter `watch`, utilise `Ctrl+C`.

Afficher les détails :

```bash
sudo mdadm --detail /dev/md0
```

Le nom `/dev/md0` peut varier selon la configuration. Vérifie toujours le nom réel fourni par le système.

## 11.7. Créer le système de fichiers sur le RAID

Une fois l'ensemble correctement créé et son état vérifié, un système de fichiers peut être créé sur le périphérique RAID.

Sur le RAID de test :

```bash
sudo mkfs.ext4 /dev/md0
```

Cette commande crée un système de fichiers sur l'ensemble RAID. Elle peut détruire les données précédemment présentes sur le périphérique ciblé.

Créer le point de montage :

```bash
sudo mkdir -p /data/raid
```

Monter le volume :

```bash
sudo mount /dev/md0 /data/raid
```

Vérifier :

```bash
findmnt /data/raid
df -hT /data/raid
sudo mdadm --detail /dev/md0
```

Schéma obtenu :

```text
Partition /dev/sdb1 ----\
                         \
                          >-- RAID 1 /dev/md0
                         /          |
Partition /dev/sdc1 ----/           v
                                ext4
                                  |
                                  v
                              /data/raid
```

## 11.8. Surveiller l'état RAID

État général :

```bash
cat /proc/mdstat
```

Détails de l'ensemble :

```bash
sudo mdadm --detail /dev/md0
```

Ces commandes permettent notamment de détecter des composants absents, une synchronisation en cours ou un ensemble dégradé.

Un RAID dégradé peut encore fournir un accès aux données, mais son niveau de protection est réduit.

Dans ce cas, l'administrateur doit éviter les manipulations improvisées, identifier le périphérique concerné et suivre une procédure de remplacement appropriée.

## 11.9. À retenir pour la production

Un RAID doit être surveillé.

Il faut notamment prévoir :

- La détection des défaillances.
- Les alertes.
- La documentation de la topologie.
- La procédure de remplacement d'un composant.
- La vérification des opérations de reconstruction.
- Des sauvegardes indépendantes.
- Des tests de restauration.

La simple présence de deux disques dans un ensemble ne signifie pas que la redondance fonctionne correctement.


# 12. Le swap et la mémoire virtuelle

## 12.1. Qu'est-ce que le swap ?

Linux utilise la mémoire vive pour exécuter les programmes et maintenir certaines données en mémoire.

Le swap fournit un espace de stockage secondaire qui peut être utilisé pour certaines pages mémoire lorsque les mécanismes de gestion de la mémoire le décident.

Il peut prendre la forme :

- D'une partition swap.
- D'un fichier swap.

Le swap n'est pas un remplacement équivalent de la RAM. Les accès au stockage sont généralement beaucoup plus lents que les accès à la mémoire vive.

Il ne garantit pas non plus qu'un système évitera toute situation de manque de mémoire.

## 12.2. Vérifier la configuration existante

```bash
free -h
```

Afficher l'état du swap :

```bash
swapon --show
```

Consulter les informations mémoire :

```bash
grep -E 'MemAvailable|SwapTotal|SwapFree' /proc/meminfo
```

Interprétation :

- `MemAvailable` estime la mémoire disponible sans forte pression.
- `SwapTotal` indique la capacité de swap configurée.
- `SwapFree` indique l'espace swap encore libre.

Une utilisation du swap n'est pas automatiquement anormale. Il faut examiner la pression mémoire, l'activité du système et les performances.

## 12.3. Comprendre `swappiness`

Le paramètre `vm.swappiness` influence la tendance du noyau à utiliser le swap dans sa gestion de la mémoire.

Consulter la valeur :

```bash
cat /proc/sys/vm/swappiness
```

Ou :

```bash
sysctl vm.swappiness
```

Une valeur élevée ne signifie pas simplement « utiliser le swap dès que la RAM est pleine », et une valeur faible ne désactive pas le swap.

Le comportement réel dépend de la version du noyau, de la charge, de la mémoire disponible, des types de pages et des paramètres associés.

Il ne faut donc pas changer cette valeur sans comprendre le problème à résoudre.

## 12.4. Créer un fichier swap de laboratoire

La méthode ci-dessous est destinée à un système de test. Vérifie auparavant la capacité disponible et les exigences de la distribution.

Créer un fichier de 1 GiB :

```bash
sudo fallocate -l 1G /swapfile
```

Si `fallocate` ne convient pas au système de fichiers utilisé, une autre méthode peut être nécessaire.

Restreindre l'accès au fichier :

```bash
sudo chmod 600 /swapfile
```

Initialiser le fichier comme espace swap :

```bash
sudo mkswap /swapfile
```

Activer le swap :

```bash
sudo swapon /swapfile
```

Vérifier :

```bash
swapon --show
free -h
```

Cette procédure modifie l'état du système. Ne remplace pas un fichier swap déjà utilisé sans comprendre ses usages.

## 12.5. Rendre le swap persistant

Pour activer le fichier automatiquement au démarrage, ajouter la ligne suivante à `/etc/fstab` :

```fstab
/swapfile none swap sw 0 0
```

Avant de modifier le fichier :

```bash
sudo cp -a /etc/fstab /etc/fstab.bak
```

Après modification, vérifier la configuration :

```bash
sudo findmnt --verify --verbose
```

Cette vérification n'analyse pas à elle seule toutes les conditions d'activation du swap. Vérifie aussi la ligne ajoutée et, lorsque cela est approprié, utilise les outils de gestion de swap pour confirmer le fonctionnement.

## 12.6. Désactiver proprement le swap de test

Si ce fichier n'est plus nécessaire :

```bash
sudo swapoff /swapfile
```

Vérifie ensuite :

```bash
swapon --show
```

Avant de supprimer le fichier, assure-toi qu'il n'est plus déclaré dans `/etc/fstab`.

Après avoir retiré sa ligne de configuration et vérifié les autres entrées, le fichier peut être supprimé si cela correspond bien à l'objectif :

```bash
sudo rm /swapfile
```

Ne supprime jamais un fichier swap encore actif.


# 13. Quotas de stockage par utilisateur et groupe

## 13.1. Pourquoi utiliser des quotas ?

Dans un serveur partagé, une seule personne ou application peut remplir tout un système de fichiers.

Les quotas permettent de limiter l'espace qu'un utilisateur ou un groupe peut consommer, et parfois le nombre d'inodes utilisés.

Exemple :

```text
Système de fichiers : /data
Capacité disponible : 500 GiB

alice : limite logique de 50 GiB
bob   : limite logique de 30 GiB
equipe-dev : limite collective définie par l'administrateur
```

Cette représentation donne une idée du mécanisme, mais les quotas par utilisateur et par groupe peuvent être cumulés selon la configuration. Il faut choisir les limites en fonction des besoins.

## 13.2. Quota souple et quota strict

Un quota peut distinguer :

- **Limite souple** : seuil qui peut être dépassé pendant une durée de grâce.
- **Limite stricte** : plafond qui ne doit pas être dépassé pour l'allocation concernée.
- **Limite d'inodes** : plafond du nombre de fichiers et objets comptabilisés par le mécanisme.

Exemple :

```text
Utilisateur alice
|
+-- Limite souple : 40 GiB
|
+-- Limite stricte : 50 GiB
|
+-- Période de grâce : définie par la politique locale
```

Le mécanisme exact dépend du système de fichiers, du type de quota et de l'outillage choisi.

## 13.3. Préparer ext4 pour les quotas

Les outils de quotas peuvent être installés sur les distributions courantes.

Sur Debian ou Ubuntu :

```bash
sudo apt update
sudo apt install quota
```

Sur les distributions utilisant DNF :

```bash
sudo dnf install quota
```

Pour vérifier le type de système de fichiers du volume :

```bash
findmnt -T /data
```

Pour une configuration traditionnelle de quotas ext4, on utilise généralement des options de montage adaptées, telles que `usrquota` et `grpquota`.

Les procédures de configuration et d'initialisation varient selon la distribution et le type de quota. Consulte la documentation locale avant toute activation sur un volume déjà utilisé.

## 13.4. Différence entre permissions et quotas

Les permissions répondent à cette question :

> Un utilisateur est-il autorisé à lire, écrire ou exécuter un fichier ?

Le quota répond plutôt à cette question :

> Quelle quantité de ressources cet utilisateur ou ce groupe peut-il consommer sur le système de fichiers concerné ?

Ces mécanismes sont complémentaires.

Un utilisateur peut posséder les droits d'écriture sur un répertoire tout en étant incapable d'y créer un fichier supplémentaire parce que sa limite d'espace ou d'inodes a été atteinte.

À l'inverse, un utilisateur peut avoir une grande limite de quota sans disposer des permissions nécessaires pour écrire dans un répertoire.

## 13.5. Vérifier les quotas

Sur un système où les quotas sont installés et activés :

```bash
quota -u alice
```

Pour un groupe :

```bash
quota -g equipe-dev
```

Pour afficher les quotas d'utilisateurs, lorsque le système et les outils le prennent en charge :

```bash
sudo repquota -a
```

Les options et les formats de sortie varient selon l'implémentation.

Ne considère pas une commande de lecture de quotas comme une preuve que tous les quotas attendus sont correctement activés. Vérifie le montage, la configuration et les comptes effectivement pris en charge.

## 13.6. Pourquoi le quota est-il utile ?

Dans une entreprise, les quotas peuvent prévenir certains incidents :

```text
Application A
    |
    v
Écrit de nombreux fichiers
    |
    v
Consommation du volume augmente
    |
    v
Quota appliqué
    |
    v
La consommation de l'utilisateur est limitée
```

Le quota ne remplace toutefois pas les alertes globales. Plusieurs utilisateurs peuvent consommer ensemble toute la capacité d'un volume, même si chacun respecte sa propre limite.


# 14. Permissions et stockage partagé

## 14.1. Le stockage partagé pose deux problèmes différents

Un répertoire partagé doit satisfaire deux exigences :

1. Chaque utilisateur doit pouvoir effectuer les opérations autorisées.
2. Un utilisateur ne doit pas pouvoir modifier ou supprimer les fichiers qui ne relèvent pas de ses droits.

Les permissions Unix, les groupes, les ACL et parfois les mécanismes propres au système de fichiers permettent de construire cette politique.

Le montage du volume ne règle pas à lui seul les droits des utilisateurs.

## 14.2. Créer un espace partagé pour une équipe

Supposons que l'équipe de développement utilise :

```text
/data/projects
```

Créer le groupe si nécessaire :

```bash
sudo groupadd equipe-dev
```

Ajouter un utilisateur existant au groupe :

```bash
sudo usermod -aG equipe-dev alice
```

L'option `-aG` ajoute le groupe supplémentaire sans supprimer les autres groupes supplémentaires de l'utilisateur.

Créer le répertoire :

```bash
sudo mkdir -p /data/projects
```

Attribuer le groupe :

```bash
sudo chown root:equipe-dev /data/projects
```

Donner au propriétaire et au groupe les droits de lecture, d'écriture et de traversée :

```bash
sudo chmod 2770 /data/projects
```

Le premier chiffre `2` active le bit SGID sur le répertoire. Les nouveaux fichiers et sous-répertoires héritent généralement du groupe du répertoire parent, sous réserve des règles applicables.

Le résultat attendu ressemble à ceci :

```text
/data/projects
|
+-- propriétaire : root
+-- groupe       : equipe-dev
+-- mode         : 2770
|
+-- Les membres du groupe peuvent créer des fichiers
+-- Les autres utilisateurs n'ont pas d'accès ordinaire
```

Les membres doivent parfois ouvrir une nouvelle session pour bénéficier de leurs nouveaux groupes.

## 14.3. La différence entre SGID et le bit sticky

SGID sur un répertoire peut aider à maintenir le groupe partagé des fichiers qui y sont créés.

Le bit sticky répond à un autre problème. Dans un répertoire partagé par plusieurs utilisateurs, il limite notamment la suppression ou le renommage des entrées aux propriétaires concernés et aux comptes privilégiés, selon les règles Unix.

Par exemple, le répertoire `/tmp` possède classiquement un mode `1777`.

Il ne faut pas appliquer automatiquement `1777` à un répertoire de projet : les exigences de confidentialité sont différentes.

## 14.4. Utiliser les ACL

Les listes de contrôle d'accès, ou ACL, permettent de définir des droits plus précis que le modèle classique propriétaire/groupe/autres.

Pour examiner les ACL :

```bash
getfacl /data/projects
```

Pour accorder un droit spécifique à un utilisateur :

```bash
sudo setfacl -m u:alice:rwx /data/projects
```

La commande suppose que les ACL soient prises en charge par le système de fichiers et disponibles dans la configuration.

Pour afficher les ACL appliquées :

```bash
getfacl /data/projects
```

Une ACL peut aussi inclure un masque qui limite les droits effectifs des entrées concernées.

Ne confonds donc pas les droits affichés pour un utilisateur avec ses droits effectifs sans vérifier le masque et les autres mécanismes d'accès.

## 14.5. Séparer données et permissions

Une bonne conception du stockage conserve une séparation claire entre :

- La capacité physique.
- L'organisation logique.
- Le système de fichiers.
- Le point de montage.
- Les droits des utilisateurs.
- Les quotas et les politiques de rétention.

Cette séparation simplifie les évolutions et le dépannage.

Par exemple, déplacer un système de fichiers sur un volume plus grand ne devrait pas exiger de réinventer toute la politique de permissions. Mais une migration doit bien entendu préserver ou rétablir les propriétaires, modes, ACL et attributs nécessaires.


# 15. Surveillance, diagnostic et alertes

## 15.1. Un stockage ne se surveille pas uniquement avec `df`

Une stratégie de supervision doit prendre en compte plusieurs dimensions.

| Dimension | Question à poser | Exemple de contrôle |
|---|---|---|
| Capacité | Le volume approche-t-il de sa limite ? | `df -hT` |
| Inodes | Reste-t-il assez d'inodes ? | `df -i` |
| Performance | Les entrées-sorties ralentissent-elles ? | `iostat` |
| Erreurs | Le noyau signale-t-il des problèmes ? | `journalctl -k` |
| LVM | Le groupe dispose-t-il encore d'espace ? | `vgs`, `lvs` |
| RAID | L'ensemble est-il sain ? | `cat /proc/mdstat` |
| Swap | La mémoire est-elle sous pression ? | `free -h`, `swapon --show` |
| Croissance | Quels répertoires grandissent rapidement ? | `du`, outils de supervision |

## 15.2. Surveiller les entrées-sorties

Sur de nombreuses distributions, `iostat` est fourni par le paquet `sysstat`.

Installation sur Debian ou Ubuntu :

```bash
sudo apt update
sudo apt install sysstat
```

Sur une distribution utilisant DNF :

```bash
sudo dnf install sysstat
```

Afficher les statistiques :

```bash
iostat -xz 1 5
```

Cette commande demande cinq rapports espacés d'une seconde, sous réserve du comportement de l'outil sur la version installée.

Parmi les indicateurs utiles :

- Débit de lecture et d'écriture.
- Nombre d'opérations par seconde.
- Temps de réponse moyen.
- Utilisation des périphériques.
- Indicateurs de file d'attente.

Attention : une forte utilisation n'est pas automatiquement une panne. L'interprétation dépend du matériel, du volume de travail, de la latence attendue et des autres ressources.

## 15.3. Identifier les processus actifs

Installer ou utiliser `iotop` lorsque disponible permet d'observer les processus qui génèrent des entrées-sorties.

Commande courante :

```bash
sudo iotop
```

Suivant la distribution, le programme peut être absent ou nécessiter des privilèges supplémentaires.

Cette observation peut aider à déterminer si la charge provient d'une base de données, d'une sauvegarde, d'une indexation ou d'une autre application.

## 15.4. Détecter un disque presque plein

Vérifier les points de montage :

```bash
df -hT
```

Pour les inodes :

```bash
df -i
```

Rechercher les grands répertoires :

```bash
sudo du -xhd1 /var 2>/dev/null | sort -h
```

Une alerte de capacité devrait être associée à une action définie :

```text
ALERTE
  |
  v
Identifier le volume
  |
  v
Vérifier les inodes et les journaux
  |
  v
Repérer la source de croissance
  |
  v
Décider : nettoyer, archiver ou agrandir
  |
  v
Contrôler les effets de l'intervention
```

L'agrandissement ne doit pas être la réponse automatique à toutes les alertes.

Si la croissance provient d'un programme qui produit des données sans limite, il faut aussi corriger le comportement ou la politique de rétention.

## 15.5. Construire une fiche de diagnostic

Lorsqu'un incident est signalé, consigne au minimum :

```text
Date et heure :
Hôte concerné :
Point de montage :
Système de fichiers :
Capacité totale :
Espace utilisé :
Espace disponible :
Utilisation des inodes :
Messages du noyau :
Événements récents :
Application impactée :
Hypothèse principale :
Action envisagée :
Risque associé :
Résultat après intervention :
```

Cette fiche facilite la collaboration, l'audit et la compréhension des incidents récurrents.


# 16. Sauvegarde, restauration et résilience

## 16.1. RAID, LVM et sauvegarde ne sont pas synonymes

Il est essentiel de distinguer trois objectifs.

### LVM : flexibilité

LVM aide à gérer les capacités logiques et à faire évoluer certains volumes.

### RAID : disponibilité contre certaines pannes

RAID permet, selon le niveau et la configuration, de continuer à fonctionner malgré la défaillance de certains composants.

### Sauvegarde : capacité de récupération

Une sauvegarde permet de retrouver des données à partir d'une copie conservée indépendamment des incidents touchant les données originales.

Schéma :

```text
                  DONNÉES
                     |
          +----------+----------+
          |                     |
          v                     v
       RAID / LVM          Sauvegarde
          |                     |
          v                     v
  Disponibilité selon       Copie de données
  les pannes couvertes      sur une cible distincte
          |                     |
          +----------+----------+
                     |
                     v
             Restauration testée
```

Un RAID miroir peut reproduire immédiatement une suppression accidentelle sur les autres composants du miroir.

Un volume logique peut devenir inaccessible si un périphérique dont il dépend disparaît.

Une sauvegarde conservée sur le même support physique que les données peut disparaître dans le même incident.

## 16.2. Une stratégie de sauvegarde exploitable

Une stratégie doit définir :

- Les données à sauvegarder.
- La fréquence.
- La période de rétention.
- La destination.
- Les droits d'accès aux copies.
- La protection contre la suppression ou l'altération.
- Les responsables.
- La procédure de restauration.
- Le délai acceptable de remise en service.

Une sauvegarde qui n'a jamais été restaurée à titre de test ne constitue pas une preuve suffisante de capacité de récupération.

## 16.3. Copier un répertoire avec `rsync`

Pour synchroniser des fichiers vers une destination de sauvegarde montée :

```bash
sudo rsync -aHAX --numeric-ids /data/projects/ /backup/projects/
```

Cette commande illustre la préservation des attributs et métadonnées pris en charge par l'environnement.

Options courantes :

- `-a` : mode archive.
- `-H` : préservation des liens physiques lorsque cela est pris en charge.
- `-A` : préservation des ACL.
- `-X` : préservation des attributs étendus.
- `--numeric-ids` : traite les identifiants numériques d'utilisateurs et de groupes sans les remapper par nom lors de cette copie.

Les options requises varient selon le système de fichiers source et cible et selon le besoin de restauration.

Vérifie que `/backup` est bien le support prévu :

```bash
findmnt /backup
df -hT /backup
```

Si la destination n'est pas montée, il faut éviter qu'une sauvegarde soit accidentellement écrite dans un répertoire vide du système de fichiers parent.

## 16.4. Comprendre le slash final de `rsync`

Dans l'exemple :

```bash
rsync -a /data/projects/ /backup/projects/
```

Le slash final de la source signifie que l'on synchronise le contenu du répertoire source vers la destination.

Sans ce slash :

```bash
rsync -a /data/projects /backup/
```

la structure peut être différente.

Avant une sauvegarde importante, effectue une simulation :

```bash
sudo rsync -aHAXn --numeric-ids /data/projects/ /backup/projects/
```

L'option `-n` demande une simulation sans appliquer les modifications.

Examine les chemins, les exclusions éventuelles et le résultat attendu.

## 16.5. Tester la restauration

Pour tester une sauvegarde, ne restaure pas directement par-dessus des données de production sans plan.

Choisis un répertoire temporaire :

```bash
sudo mkdir -p /restore-test/projects
```

Restaure une partie des données dans cet emplacement :

```bash
sudo rsync -aHAX --numeric-ids /backup/projects/ /restore-test/projects/
```

Vérifie le contenu :

```bash
sudo find /restore-test/projects -maxdepth 2 -type f
```

Compare les fichiers et, selon les exigences, utilise des sommes de contrôle ou un outil de sauvegarde qui fournit une vérification d'intégrité.

Le test doit également vérifier les éléments qui ne sont pas toujours couverts par une copie de fichiers : configuration de service, droits, ACL, dépendances applicatives, bases de données cohérentes et documentation de restauration.


# 17. Sécurité et bonnes pratiques d'administration

## 17.1. Identifier avant de modifier

Avant une commande de partitionnement, de formatage ou de réduction :

```bash
lsblk -f
sudo blkid
findmnt
df -hT
```

Pour LVM :

```bash
sudo pvs
sudo vgs
sudo lvs
```

Pour RAID logiciel :

```bash
cat /proc/mdstat
sudo mdadm --detail --scan
```

Le but n'est pas d'accumuler des commandes, mais de confirmer l'état réel avant de toucher au stockage.

## 17.2. Préserver la traçabilité

Une opération importante doit laisser une trace compréhensible.

Note :

- L'objectif de l'opération.
- Le périphérique visé.
- Les commandes exécutées.
- Les résultats avant et après.
- Les sauvegardes réalisées.
- Les contrôles effectués.
- Les écarts constatés.
- La possibilité de retour arrière.

Les procédures écrites réduisent les erreurs liées à la précipitation ou à la mémoire.

## 17.3. Ne pas automatiser une destruction sans vérification

Les options qui répondent automatiquement « oui » aux questions d'un outil peuvent rendre une opération irréversible beaucoup plus facile à lancer.

Il faut éviter de mélanger une procédure de découverte et une procédure destructive dans un script sans garde-fous.

Un script sérieux doit vérifier les préconditions, journaliser les actions, traiter les erreurs et distinguer une simulation d'une exécution réelle.

## 17.4. Ne pas supprimer les données pour masquer une anomalie

Lorsqu'un volume se remplit, l'administrateur doit comprendre la cause.

Une croissance peut être normale :

- Augmentation du volume de données métier.
- Archivage en attente.
- Import initial.
- Génération temporaire de fichiers de travail.

Elle peut aussi être anormale :

- Rotation des journaux mal configurée.
- Boucle applicative générant des fichiers.
- Fichiers temporaires jamais supprimés.
- Sauvegarde écrite au mauvais endroit.
- Processus conservant des fichiers supprimés ouverts.

La bonne solution consiste à traiter la cause avant qu'elle ne se reproduise.

## 17.5. Toujours vérifier après une modification

Après une extension LVM :

```bash
sudo lvs
df -hT
```

Après une modification de montage :

```bash
findmnt
sudo findmnt --verify --verbose
```

Après une opération RAID :

```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
```

Après la résolution d'un incident :

```bash
sudo journalctl -k --since "30 minutes ago"
```

Adapte la fenêtre temporelle à l'heure réelle de l'incident.


# 18. Laboratoires pratiques guidés

Les laboratoires suivants servent à consolider les compétences acquises.

**Toutes les manipulations destructrices doivent être réalisées dans une machine virtuelle ou sur des périphériques de test dédiés.**

Ne considère jamais les noms de disques fournis comme des indications fiables sur ton propre ordinateur.

## Laboratoire 1 — Cartographier le stockage existant

### Objectif

Produire une vue de l'organisation actuelle des disques, des systèmes de fichiers et des montages.

### Étape 1 : identifier les périphériques

```bash
lsblk -o NAME,MODEL,SIZE,TYPE,FSTYPE,UUID,MOUNTPOINTS
```

### Étape 2 : afficher les montages

```bash
findmnt -o SOURCE,TARGET,FSTYPE,OPTIONS
```

### Étape 3 : relever les capacités

```bash
df -hT
df -i
```

### Étape 4 : rechercher les informations complémentaires

```bash
sudo blkid
sudo dmesg --level=err,warn
```

### Résultat attendu

Construis un tableau de ce type :

| Périphérique | Capacité | Type | Système de fichiers | Montage | Observation |
|---|---:|---|---|---|---|
| À compléter | À compléter | Disque/partition/LV | À compléter | À compléter | À compléter |
| À compléter | À compléter | Disque/partition/LV | À compléter | À compléter | À compléter |

### Critère de validation

Tu dois pouvoir identifier le volume qui contient `/`, les volumes spécialisés éventuellement montés séparément et les périphériques non montés qui nécessitent une investigation.


## Laboratoire 2 — Monter un volume de test de manière persistante

### Objectif

Créer un montage persistant en utilisant l'UUID.

### Prérequis

Une partition de test dédiée, par exemple `/dev/sdb1`, sans données à conserver.

### Étape 1 : confirmer la cible

```bash
lsblk -f
sudo blkid /dev/sdb1
```

### Étape 2 : créer ext4 sur la cible confirmée

```bash
sudo mkfs.ext4 -L DATA_TEST /dev/sdb1
```

Cette opération détruit le contenu précédent de la cible.

### Étape 3 : créer le point de montage

```bash
sudo mkdir -p /data
```

### Étape 4 : relever l'UUID

```bash
sudo blkid /dev/sdb1
```

### Étape 5 : sauvegarder la configuration

```bash
sudo cp -a /etc/fstab /etc/fstab.bak
```

### Étape 6 : modifier `/etc/fstab`

Ajouter une entrée qui utilise l'UUID réel, le point de montage `/data`, le type `ext4` et les options adaptées.

### Étape 7 : vérifier la déclaration

```bash
sudo findmnt --verify --verbose
```

### Étape 8 : tester les montages

Si le volume n'est pas déjà monté :

```bash
sudo mount -a
```

Puis :

```bash
findmnt /data
df -hT /data
```

### Résultat attendu

Le volume doit être identifié par son UUID dans la configuration et être correctement monté.

### Critère de validation

La configuration doit être cohérente et le point de montage doit apparaître dans `findmnt`.


## Laboratoire 3 — Créer une architecture LVM complète

### Objectif

Construire une chaîne de stockage comprenant un volume physique, un groupe de volumes et un volume logique.

### Prérequis

Une partition dédiée à LVM.

### Étape 1 : confirmer que la partition peut être utilisée

```bash
lsblk -f
sudo pvs
sudo vgs
sudo lvs
```

### Étape 2 : créer le volume physique

```bash
sudo pvcreate /dev/sdb1
```

### Étape 3 : créer le groupe de volumes

```bash
sudo vgcreate vgdata /dev/sdb1
```

### Étape 4 : créer le volume logique

```bash
sudo lvcreate -L 10G -n lvtest vgdata
```

### Étape 5 : créer le système de fichiers

```bash
sudo mkfs.ext4 /dev/vgdata/lvtest
```

### Étape 6 : créer le point de montage

```bash
sudo mkdir -p /data/lvmtest
```

### Étape 7 : monter le volume

```bash
sudo mount /dev/vgdata/lvtest /data/lvmtest
```

### Étape 8 : contrôler le résultat

```bash
sudo pvs
sudo vgs
sudo lvs
findmnt /data/lvmtest
df -hT /data/lvmtest
```

### Résultat attendu

L'architecture obtenue doit être comparable à ceci :

```text
/dev/sdb1
    |
    v
  PV LVM
    |
    v
   vgdata
    |
    v
   lvtest
    |
    v
   ext4
    |
    v
/data/lvmtest
```

### Critère de validation

Tu dois être capable d'expliquer le rôle de chaque couche et de retrouver les informations avec les outils appropriés.


## Laboratoire 4 — Agrandir un volume logique

### Objectif

Ajouter de la capacité à un volume LVM.

### Prérequis

Le volume créé dans le laboratoire précédent doit disposer d'espace libre suffisant dans son groupe.

### Étape 1 : relever l'état initial

```bash
sudo vgs
sudo lvs
df -hT /data/lvmtest
```

### Étape 2 : agrandir le volume logique

Dans cet exemple, ajouter 2 GiB :

```bash
sudo lvextend -r -L +2G /dev/vgdata/lvtest
```

N'exécute cette commande que si le groupe possède suffisamment d'espace libre et si le volume cible est bien celui du laboratoire.

### Étape 3 : vérifier la capacité

```bash
sudo lvs
df -hT /data/lvmtest
```

### Résultat attendu

Le volume logique et son système de fichiers doivent présenter une capacité supérieure à celle observée avant l'opération.

### Critère de validation

Tu dois distinguer l'extension du volume logique de l'extension du système de fichiers et être capable de vérifier ces deux niveaux.


## Laboratoire 5 — Diagnostiquer un manque d'espace

### Objectif

Construire une démarche de diagnostic complète.

### Étape 1 : vérifier la capacité

```bash
df -hT
```

### Étape 2 : vérifier les inodes

```bash
df -i
```

### Étape 3 : identifier les répertoires volumineux

Pour `/var` :

```bash
sudo du -xhd1 /var 2>/dev/null | sort -h
```

### Étape 4 : examiner les journaux

```bash
journalctl --disk-usage
```

### Étape 5 : rechercher des fichiers supprimés encore ouverts

Si `lsof` est installé :

```bash
sudo lsof +L1
```

### Étape 6 : examiner les événements du noyau

```bash
sudo journalctl -k --since "1 hour ago"
```

### Résultat attendu

Rédige une conclusion basée sur les observations, plutôt que de simplement proposer de supprimer des fichiers.

### Critère de validation

La démarche doit distinguer au moins les causes suivantes :

- Capacité réellement consommée.
- Inodes épuisés.
- Journaux trop volumineux.
- Fichiers supprimés mais toujours ouverts.
- Erreurs matérielles ou logicielles.
- Croissance applicative normale ou anormale.


## Laboratoire 6 — Préparer un espace partagé

### Objectif

Mettre en place un répertoire de groupe avec héritage du groupe et contrôle des accès.

### Étape 1 : créer un groupe de laboratoire

```bash
sudo groupadd equipe-test
```

Si le groupe existe déjà, vérifie-le au lieu de le recréer.

### Étape 2 : ajouter un utilisateur existant

```bash
sudo usermod -aG equipe-test alice
```

Remplace `alice` par un compte de test réellement présent sur la machine.

### Étape 3 : créer le répertoire

```bash
sudo mkdir -p /data/equipe-test
```

### Étape 4 : affecter le groupe

```bash
sudo chown root:equipe-test /data/equipe-test
```

### Étape 5 : appliquer les permissions

```bash
sudo chmod 2770 /data/equipe-test
```

### Étape 6 : vérifier

```bash
ls -ld /data/equipe-test
getfacl /data/equipe-test
```

### Résultat attendu

Le groupe doit être `equipe-test`, et le bit SGID doit être présent.

### Critère de validation

Tu dois savoir expliquer pourquoi l'accès dépend à la fois des permissions et de l'appartenance au groupe.


# 19. Exercices d'entraînement

Réponds aux exercices avant de consulter les corrections.

## Exercice 1 — Identifier un montage

La commande `findmnt -T /srv` affiche que `/srv` appartient au système de fichiers monté sur `/`.

Que peux-tu en conclure ?

A. `/srv` est obligatoirement une partition indépendante.

B. Le chemin `/srv` est situé sur le système de fichiers qui contient `/`, selon la vue de montage actuelle.

C. `/srv` ne contient aucun fichier.

D. Le disque est défectueux.

## Exercice 2 — LVM

Un groupe `vgdata` possède 100 GiB de capacité libre. Un volume logique de 20 GiB doit passer à 30 GiB.

Quelle commande correspond à une extension de 10 GiB du volume logique ?

A. `sudo vgremove vgdata`

B. `sudo lvextend -L +10G /dev/vgdata/lvprojects`

C. `sudo mkfs.ext4 /dev/vgdata/lvprojects`

D. `sudo umount /dev/sdb`

Explique également ce qu'il faut vérifier pour que le système de fichiers utilise la nouvelle capacité.

## Exercice 3 — ext4 et XFS

Pourquoi ne peut-on pas utiliser la procédure classique de réduction ext4 pour réduire directement un système de fichiers XFS ?

## Exercice 4 — RAID

Un RAID 1 classique constitué de deux disques sains fonctionne normalement. Un des deux disques tombe en panne.

Que peut-on dire ?

A. Le RAID 1 détruit automatiquement toutes les données.

B. L'ensemble peut continuer à fonctionner avec une redondance dégradée, selon son état et sa configuration.

C. Le RAID 1 constitue une sauvegarde historique.

D. Le disque restant ne contient aucune donnée.

## Exercice 5 — Montage persistant

Pourquoi l'utilisation d'un UUID peut-elle être préférable à celle d'un nom tel que `/dev/sdb1` dans `/etc/fstab` ?

## Exercice 6 — Espace et inodes

La commande `df -h` indique encore 40 GiB disponibles, mais `df -i` affiche 100 % d'inodes utilisés.

Quel problème peut se produire ?

## Exercice 7 — Répertoire partagé

Pourquoi un répertoire configuré avec le mode `2770` peut-il faciliter le travail d'une équipe ?

Que fait le premier chiffre `2` dans ce contexte ?

## Exercice 8 — Volume plein

Un volume atteint 96 % d'occupation. Quelle est la meilleure démarche initiale ?

A. Formater immédiatement le volume.

B. Supprimer au hasard les fichiers les plus anciens.

C. Vérifier les capacités, les inodes, les répertoires volumineux, les journaux et les éventuelles erreurs avant de choisir une action.

D. Désactiver toutes les sauvegardes.

## Exercice 9 — Réduction LVM

Pourquoi faut-il réduire le système de fichiers ext4 avant de réduire le volume logique qui le contient ?

## Exercice 10 — Sauvegarde

Pourquoi un RAID 1 n'est-il pas équivalent à une sauvegarde indépendante ?


# 20. Défi final : administrer le stockage d'un serveur Linux

## 20.1. Contexte professionnel

Tu es l'administrateur système d'une petite entreprise.

Un serveur Linux héberge plusieurs services internes. Les données des projets sont actuellement conservées dans une arborescence du système principal.

L'équipe veut une organisation plus fiable et plus facile à faire évoluer.

Tu dois concevoir et réaliser, dans une machine virtuelle de laboratoire, une configuration de stockage cohérente.

## 20.2. Situation initiale

Le serveur contient :

```text
Disque système
     |
     +-- /
     |
     +-- /boot
     |
     +-- /var
```

Un espace supplémentaire est disponible pour un laboratoire.

La direction formule les exigences suivantes :

1. Disposer d'un volume logique dédié aux projets.
2. Monter ce volume dans `/srv/projects`.
3. Faire en sorte que le montage persiste au redémarrage.
4. Appliquer des permissions adaptées à une équipe.
5. Disposer d'une méthode documentée d'extension du volume.
6. Détecter rapidement un manque de capacité.
7. Prévoir une procédure de sauvegarde et de restauration.
8. Documenter une stratégie de redondance appropriée si le service exige une continuité malgré la perte d'un disque.

Le laboratoire ne doit pas modifier les disques système ni détruire des données existantes.

## 20.3. Mission 1 — Faire l'inventaire

Exécute :

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,UUID,MOUNTPOINTS
findmnt
df -hT
df -i
```

Consigne les périphériques qui peuvent être utilisés pour les tests.

**Validation :** tu dois pouvoir identifier sans ambiguïté la cible réservée au laboratoire.

## 20.4. Mission 2 — Construire une couche LVM

Sur une partition de test réservée :

1. Créer un volume physique.
2. Créer un groupe de volumes nommé `vgprojects`.
3. Créer un volume logique nommé `lvprojects`.
4. Créer un système de fichiers ext4.

La taille doit rester compatible avec la capacité disponible.

Vérifie l'architecture avec :

```bash
sudo pvs
sudo vgs
sudo lvs
lsblk -f
```

**Validation :** les noms, tailles et relations entre les couches doivent correspondre au plan.

## 20.5. Mission 3 — Monter le volume

Créer le point de montage :

```bash
sudo mkdir -p /srv/projects
```

Monter le volume logique :

```bash
sudo mount /dev/vgprojects/lvprojects /srv/projects
```

Vérifier :

```bash
findmnt /srv/projects
df -hT /srv/projects
```

**Validation :** le point de montage doit utiliser le système de fichiers prévu.

## 20.6. Mission 4 — Rendre le montage persistant

1. Relever l'UUID du système de fichiers.
2. Sauvegarder `/etc/fstab`.
3. Ajouter une ligne adaptée.
4. Vérifier la syntaxe.
5. Tester les montages.
6. Confirmer le montage final.

Commandes de contrôle :

```bash
sudo blkid
sudo cp -a /etc/fstab /etc/fstab.bak
sudo findmnt --verify --verbose
```

Après avoir ajouté la ligne correcte, tester avec :

```bash
sudo mount -a
findmnt /srv/projects
```

Ne redémarre pas avant d'avoir vérifié que la configuration est cohérente.

**Validation :** le fichier de configuration doit désigner le système de fichiers réel au moyen de son UUID.

## 20.7. Mission 5 — Créer un accès partagé

Préparer un groupe `projets` et un répertoire accessible aux membres autorisés.

Appliquer les permissions appropriées et vérifier les droits effectifs.

Commandes utiles :

```bash
sudo groupadd projets
sudo chown root:projets /srv/projects
sudo chmod 2770 /srv/projects
ls -ld /srv/projects
getfacl /srv/projects
```

Ajoute uniquement des comptes de test existants au groupe.

**Validation :** tu dois pouvoir expliquer l'effet des permissions, du groupe et du bit SGID.

## 20.8. Mission 6 — Préparer la procédure d'extension

Documenter les étapes nécessaires si le volume approche de sa limite.

La procédure doit comprendre :

- L'identification du volume.
- La vérification de l'espace libre de `vgprojects`.
- La décision de libérer de l'espace ou d'ajouter un périphérique.
- L'extension du volume logique.
- L'extension du système de fichiers lorsque nécessaire.
- La validation finale.

Commandes de contrôle :

```bash
sudo vgs
sudo lvs
df -hT /srv/projects
```

**Validation :** aucun ajout de capacité ne doit être exécuté sans contrôle de la capacité réellement disponible.

## 20.9. Mission 7 — Établir une surveillance

Préparer une fiche d'alerte qui inclut :

```text
Nom du serveur
Date et heure
Volume concerné
Capacité totale
Occupation en pourcentage
Inodes disponibles
Tendance de croissance
Événements système pertinents
Application touchée
Action décidée
Vérification après intervention
```

Proposer des seuils d'alerte adaptés à l'activité réelle.

**Validation :** la surveillance doit couvrir les capacités et les inodes, et ne pas se limiter à un seul indicateur.

## 20.10. Mission 8 — Préparer une sauvegarde et une restauration

Définir une destination de sauvegarde distincte du volume source.

Démontrer une copie de fichiers en laboratoire et restaurer les données dans un répertoire temporaire.

Vérifier que les droits, propriétaires et fichiers attendus sont présents.

**Validation :** la procédure doit permettre de démontrer une restauration, pas simplement de prouver qu'une commande de copie s'est exécutée.

## 20.11. Mission 9 — Présenter l'architecture

Produire un schéma textuel final similaire à celui-ci, adapté à tes résultats réels :

```text
                    SERVEUR LINUX
                         |
                         v
                   Disque de test
                         |
                         v
                  Partition de test
                         |
                         v
                         PV
                         |
                         v
                     vgprojects
                         |
                         v
                     lvprojects
                         |
                         v
                        ext4
                         |
                         v
                    /srv/projects
                         |
                  +------+------+
                  |             |
                  v             v
              Fichiers       Permissions
              de projets     du groupe
```

Ajoute sur ton schéma :

- La capacité réellement créée.
- L'UUID réellement utilisé.
- La méthode de montage persistant.
- La destination de sauvegarde.
- Les commandes de diagnostic.
- La procédure d'extension.

**Validation finale :** une autre personne doit être capable de comprendre l'architecture et d'en assurer la maintenance à partir de ta documentation.


# 21. Correction détaillée du défi final

Cette section présente un exemple de démarche. Les noms et capacités sont illustratifs : ils doivent être remplacés par ceux de la machine de laboratoire.

## 21.1. Inventaire

Commencer par :

```bash
lsblk -f
findmnt
df -hT
```

Ne choisir un périphérique qu'après avoir confirmé qu'il est destiné au laboratoire.

## 21.2. Création LVM

Supposons que `/dev/sdb1` soit une partition de test vide et réservée.

Créer le volume physique :

```bash
sudo pvcreate /dev/sdb1
```

Créer le groupe :

```bash
sudo vgcreate vgprojects /dev/sdb1
```

Créer un volume logique de 20 GiB :

```bash
sudo lvcreate -L 20G -n lvprojects vgprojects
```

Vérifier :

```bash
sudo pvs
sudo vgs
sudo lvs
```

L'espace libre du groupe sera inférieur à sa taille totale, car 20 GiB ont été attribués au volume logique et les outils peuvent afficher des écarts d'arrondi ou de métadonnées.

## 21.3. Système de fichiers et montage

Créer ext4 :

```bash
sudo mkfs.ext4 /dev/vgprojects/lvprojects
```

Créer le point de montage :

```bash
sudo mkdir -p /srv/projects
```

Monter :

```bash
sudo mount /dev/vgprojects/lvprojects /srv/projects
```

Contrôler :

```bash
findmnt /srv/projects
df -hT /srv/projects
```

## 21.4. Montage persistant

Relever l'UUID :

```bash
sudo blkid /dev/vgprojects/lvprojects
```

Sauvegarder le fichier de configuration :

```bash
sudo cp -a /etc/fstab /etc/fstab.bak
```

Ajouter une ligne utilisant l'UUID réel.

Exemple fictif :

```fstab
UUID=UUID_REEL /srv/projects ext4 defaults 0 2
```

Le marqueur `UUID_REEL` doit être remplacé par la véritable valeur.

Vérifier :

```bash
sudo findmnt --verify --verbose
```

Tester :

```bash
sudo mount -a
findmnt /srv/projects
```

## 21.5. Permissions

Créer le groupe, si nécessaire :

```bash
sudo groupadd projets
```

Attribuer le groupe au répertoire :

```bash
sudo chown root:projets /srv/projects
```

Appliquer les permissions :

```bash
sudo chmod 2770 /srv/projects
```

Contrôler :

```bash
ls -ld /srv/projects
getfacl /srv/projects
```

Un résultat de mode proche de `drwxrws---` est attendu pour ce type de configuration, en tenant compte du propriétaire, du groupe et des ACL.

## 21.6. Procédure d'extension

Examiner l'état :

```bash
sudo vgs
sudo lvs
df -hT /srv/projects
```

Si le groupe a suffisamment d'espace libre et si l'on souhaite ajouter 5 GiB :

```bash
sudo lvextend -r -L +5G /dev/vgprojects/lvprojects
```

Contrôler :

```bash
sudo lvs
df -hT /srv/projects
```

Si le groupe ne dispose pas d'assez d'espace, il faut planifier l'ajout d'un périphérique compatible ou libérer de la capacité. Il ne faut pas tenter une extension qui suppose l'existence d'espace physique inexistant.

## 21.7. Surveillance

Une surveillance manuelle initiale peut utiliser :

```bash
df -hT /srv/projects
df -i /srv/projects
sudo vgs
```

Pour les problèmes techniques :

```bash
sudo journalctl -k --since "1 hour ago"
```

Une infrastructure de production devrait automatiser les alertes de capacité, de croissance et d'erreur, selon les contraintes de service.

## 21.8. Sauvegarde

Si `/backup` est bien une destination de sauvegarde distincte et correctement montée :

```bash
findmnt /backup
df -hT /backup
```

Réaliser une copie de test :

```bash
sudo rsync -aHAXn --numeric-ids /srv/projects/ /backup/projects/
```

Examiner la simulation.

Puis effectuer la synchronisation réelle si les chemins et les politiques ont été validés :

```bash
sudo rsync -aHAX --numeric-ids /srv/projects/ /backup/projects/
```

Créer ensuite une zone de restauration de test :

```bash
sudo mkdir -p /restore-test/projects
```

Restaurer les fichiers :

```bash
sudo rsync -aHAX --numeric-ids /backup/projects/ /restore-test/projects/
```

Vérifier le résultat et les permissions.

Une procédure de sauvegarde de production doit aussi préciser les conditions de cohérence applicative, la fréquence des copies et les mesures de protection contre la perte ou la suppression de la sauvegarde.

## 21.9. Architecture finale

```text
                   Stockage du serveur
                           |
                           v
                      Partition
                           |
                           v
                           PV
                           |
                           v
                       vgprojects
                           |
                           v
                       lvprojects
                           |
                           v
                         ext4
                           |
                           v
                     /srv/projects
                           |
            +--------------+--------------+
            |                             |
            v                             v
       Accès contrôlés               Surveillance
       par groupe                    capacité/inodes
            |                             |
            +--------------+--------------+
                           |
                           v
                 Sauvegarde indépendante
                           |
                           v
                  Test de restauration
```

Ce schéma ne représente pas un RAID : il décrit une architecture LVM accompagnée de permissions, de surveillance et d'une sauvegarde. La redondance matérielle doit être ajoutée si les exigences de disponibilité la nécessitent.


# 22. Checklist d'exploitation

## Avant une modification de stockage

- [ ] Identifier le disque ou le volume exact.
- [ ] Consulter `lsblk -f`.
- [ ] Vérifier les systèmes de fichiers avec `blkid`.
- [ ] Contrôler les montages avec `findmnt`.
- [ ] Vérifier l'espace avec `df -hT` et `df -i`.
- [ ] Examiner LVM, RAID et les autres couches présentes.
- [ ] Vérifier les données à préserver.
- [ ] Prévoir une sauvegarde lorsque le risque le justifie.
- [ ] Définir une procédure de retour arrière.

## Après une extension

- [ ] Vérifier les volumes logiques avec `lvs`.
- [ ] Vérifier l'espace libre du groupe avec `vgs`.
- [ ] Contrôler le système de fichiers avec `df -hT`.
- [ ] Contrôler les inodes avec `df -i`.
- [ ] Vérifier le montage.
- [ ] Effectuer un test applicatif.
- [ ] Documenter la nouvelle capacité.

## Après une modification de montage

- [ ] Vérifier le point de montage.
- [ ] Confirmer l'UUID.
- [ ] Vérifier les options réellement actives.
- [ ] Contrôler les déclarations de `/etc/fstab`.
- [ ] Tester les montages sans redémarrage lorsque c'est possible.
- [ ] Confirmer que les services dépendent du bon volume.
- [ ] Ne pas considérer l'opération terminée tant que l'application n'a pas été vérifiée.

## En cas de volume presque plein

- [ ] Vérifier la capacité du système de fichiers.
- [ ] Vérifier les inodes.
- [ ] Identifier les répertoires volumineux.
- [ ] Examiner les journaux.
- [ ] Rechercher les fichiers supprimés mais encore ouverts.
- [ ] Examiner les erreurs du noyau.
- [ ] Déterminer si la croissance est normale.
- [ ] Choisir une action documentée.
- [ ] Vérifier le résultat et surveiller l'évolution.

## Pour une configuration RAID

- [ ] Vérifier la topologie réelle.
- [ ] Contrôler l'état de l'ensemble.
- [ ] Vérifier les alertes.
- [ ] Documenter la procédure de remplacement.
- [ ] Surveiller les reconstructions.
- [ ] Maintenir des sauvegardes indépendantes.
- [ ] Tester la restauration.


# 23. Fiche de révision et commandes essentielles

## 23.1. Inventaire

| Commande | Utilité |
|---|---|
| `lsblk -f` | Identifier disques, partitions, systèmes de fichiers et UUID |
| `sudo blkid` | Examiner les signatures et identifiants de systèmes de fichiers |
| `findmnt` | Afficher les montages |
| `findmnt -T /chemin` | Identifier le montage contenant un chemin |
| `df -hT` | Mesurer l'occupation des systèmes de fichiers |
| `df -i` | Examiner l'utilisation des inodes |
| `sudo fdisk -l` | Examiner les partitions |
| `sudo journalctl -k -b` | Consulter les journaux du noyau du démarrage courant |

## 23.2. Partitionnement et montage

| Commande | Utilité |
|---|---|
| `sudo parted /dev/sdX print` | Examiner la table de partitions |
| `sudo mkfs.ext4 /dev/sdX1` | Créer un système de fichiers ext4 sur la cible choisie |
| `sudo mount /dev/sdX1 /data` | Monter un système de fichiers |
| `sudo umount /data` | Démonter un système de fichiers |
| `sudo findmnt --verify --verbose` | Vérifier la configuration des montages |
| `sudo mount -a` | Tenter les montages déclarés et non encore montés |

Les noms `/dev/sdX` et `/dev/sdX1` sont des espaces réservés. Il ne faut pas les copier littéralement en supposant qu'ils identifient un périphérique précis.

## 23.3. LVM

| Commande | Utilité |
|---|---|
| `sudo pvs` | Afficher les volumes physiques |
| `sudo vgs` | Afficher les groupes de volumes |
| `sudo lvs` | Afficher les volumes logiques |
| `sudo pvcreate /dev/sdX1` | Initialiser un périphérique pour LVM |
| `sudo vgcreate vgdata /dev/sdX1` | Créer un groupe de volumes |
| `sudo vgextend vgdata /dev/sdY1` | Ajouter un volume physique à un groupe |
| `sudo lvcreate -L 20G -n lvdata vgdata` | Créer un volume logique |
| `sudo lvextend -L +5G /dev/vgdata/lvdata` | Agrandir un volume logique |
| `sudo lvextend -r -L +5G /dev/vgdata/lvdata` | Agrandir un volume logique et demander l'extension du système de fichiers compatible |
| `sudo pvdisplay` | Consulter les détails d'un volume physique |
| `sudo vgdisplay` | Consulter les détails d'un groupe |
| `sudo lvdisplay` | Consulter les détails d'un volume logique |

## 23.4. Systèmes de fichiers

| Commande | Utilité |
|---|---|
| `sudo tune2fs -l /dev/XXX` | Consulter les métadonnées ext |
| `sudo e2fsck -f /dev/XXX` | Vérifier ext2/ext3/ext4 dans les conditions appropriées |
| `sudo resize2fs /dev/XXX` | Étendre ou réduire ext selon les contraintes du système de fichiers |
| `sudo xfs_info /data` | Consulter les informations XFS d'un montage |
| `sudo xfs_repair /dev/XXX` | Outil de réparation XFS, à utiliser selon la procédure documentée |
| `sudo btrfs filesystem usage /data` | Examiner l'usage d'un système de fichiers Btrfs |
| `sudo btrfs subvolume list /data` | Afficher les sous-volumes Btrfs |

Les outils de réparation et de réduction nécessitent une attention particulière. Le type de système de fichiers et son état doivent être établis avant l'intervention.

## 23.5. Analyse et surveillance

| Commande | Utilité |
|---|---|
| `sudo du -xhd1 /var` | Identifier les répertoires volumineux |
| `sudo lsof +L1` | Rechercher les fichiers supprimés encore ouverts |
| `journalctl --disk-usage` | Mesurer l'espace consommé par le journal systemd |
| `iostat -xz 1 5` | Observer les statistiques d'entrée-sortie |
| `free -h` | Afficher un résumé de la mémoire |
| `swapon --show` | Afficher les zones swap actives |
| `cat /proc/mdstat` | Consulter l'état général du RAID logiciel md |
| `sudo mdadm --detail /dev/md0` | Afficher les détails d'un ensemble RAID md |

## 23.6. Commandes à risque élevé

Les commandes suivantes ne doivent jamais être utilisées sans vérification de la cible et de l'objectif :

```bash
sudo parted /dev/sdX --script mklabel gpt
sudo mkfs.ext4 /dev/sdX1
sudo pvcreate /dev/sdX1
sudo mdadm --create /dev/md0 ...
sudo lvreduce ...
sudo resize2fs ...
sudo e2fsck ...
```

Elles n'ont pas toutes les mêmes effets, mais elles peuvent modifier les structures du stockage ou les données. Certaines servent à créer des structures, d'autres à les réduire ou à les réparer. La bonne commande dépend de l'état réel et du système de fichiers.


# 24. Conclusion

L'administration intermédiaire du stockage Linux repose sur la compréhension des couches et sur une méthode rigoureuse.

Tu as appris à :

- Cartographier les périphériques de stockage.
- Examiner les partitions et les systèmes de fichiers.
- Créer et monter un système de fichiers de manière contrôlée.
- Configurer les montages persistants à l'aide des UUID.
- Différencier ext4, XFS et Btrfs.
- Comprendre les limites et les risques des opérations de maintenance.
- Diagnostiquer une saturation de capacité ou d'inodes.
- Construire une architecture LVM.
- Étendre un volume logique et son système de fichiers.
- Comprendre pourquoi la réduction est plus risquée.
- Expliquer les différences entre les principaux niveaux RAID.
- Surveiller un ensemble RAID logiciel.
- Configurer un espace de swap.
- Comprendre les quotas et leur complémentarité avec les permissions.
- Organiser le stockage partagé d'une équipe.
- Préparer une sauvegarde et vérifier une restauration.
- Établir une checklist de maintenance.

Le réflexe essentiel à retenir est le suivant :

```text
         OBSERVER
             |
             v
       IDENTIFIER
             |
             v
       COMPRENDRE
             |
             v
        PLANIFIER
             |
             v
         EXÉCUTER
             |
             v
         VÉRIFIER
             |
             v
       DOCUMENTer
```

Une administration du stockage fiable ne dépend pas seulement de la connaissance des commandes. Elle dépend de la capacité à identifier précisément chaque couche, à anticiper les conséquences d'une modification et à vérifier que le système répond toujours aux besoins de l'application.

Le niveau suivant pourra approfondir l'exploitation avancée : performances et latence, stockage multipath, stratégies de haute disponibilité, instantanés, chiffrement, automatisation de la maintenance et procédures de récupération après incident.