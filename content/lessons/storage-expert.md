# Stockage Linux — Niveau expert
## Architecture avancée, performances, haute disponibilité, chiffrement et récupération après incident


# Sommaire

1. [Présentation du niveau expert](#1-présentation-du-niveau-expert)
2. [Architecture avancée des couches de stockage](#2-architecture-avancée-des-couches-de-stockage)
3. [Identification avancée et stabilité des périphériques](#3-identification-avancée-et-stabilité-des-périphériques)
4. [Modèle de performance : IOPS, débit, latence et profondeur de file](#4-modèle-de-performance--iops-débit-latence-et-profondeur-de-file)
5. [Diagnostic avancé des entrées-sorties](#5-diagnostic-avancé-des-entrées-sorties)
6. [Mesure des performances avec fio](#6-mesure-des-performances-avec-fio)
7. [Santé matérielle et surveillance des périphériques](#7-santé-matérielle-et-surveillance-des-périphériques)
8. [LVM expert : allocation, déplacements et provisionnement fin](#8-lvm-expert--allocation-déplacements-et-provisionnement-fin)
9. [Instantanés et gestion de la cohérence](#9-instantanés-et-gestion-de-la-cohérence)
10. [RAID avancé : dégradation, reconstruction et exploitation](#10-raid-avancé--dégradation-reconstruction-et-exploitation)
11. [Stockage multipath et environnements SAN](#11-stockage-multipath-et-environnements-san)
12. [Stockage réseau iSCSI et NVMe over Fabrics](#12-stockage-réseau-iscsi-et-nvme-over-fabrics)
13. [Chiffrement avec LUKS et cryptsetup](#13-chiffrement-avec-luks-et-cryptsetup)
14. [Maintenance experte d'ext4, XFS et Btrfs](#14-maintenance-experte-dext4-xfs-et-btrfs)
15. [Quotas avancés et gestion multi-tenant](#15-quotas-avancés-et-gestion-multi-tenant)
16. [Montages systemd et dépendances des services](#16-montages-systemd-et-dépendances-des-services)
17. [Sauvegarde, cohérence applicative et reprise après sinistre](#17-sauvegarde-cohérence-applicative-et-reprise-après-sinistre)
18. [Sécurité avancée du stockage](#18-sécurité-avancée-du-stockage)
19. [Automatisation et observabilité](#19-automatisation-et-observabilité)
20. [Procédures de réponse aux incidents](#20-procédures-de-réponse-aux-incidents)
21. [Laboratoires pratiques avancés](#21-laboratoires-pratiques-avancés)
22. [Exercices experts](#22-exercices-experts)
23. [Défi final : architecture de stockage de production](#23-défi-final--architecture-de-stockage-de-production)
24. [Correction du défi final](#24-correction-du-défi-final)
25. [Checklist d'exploitation experte](#25-checklist-dexploitation-experte)
26. [Référence des commandes essentielles](#26-référence-des-commandes-essentielles)
27. [Conclusion](#27-conclusion)


# 1. Présentation du niveau expert

## 1.1. Objectif général

Les niveaux débutant et intermédiaire ont permis d'apprendre à administrer les systèmes de fichiers, les permissions, les montages, les partitions, LVM et les premières architectures RAID.

Le niveau expert aborde une autre dimension : **la capacité à concevoir, exploiter, mesurer, sécuriser et récupérer une architecture de stockage dans des conditions exigeantes**.

Un administrateur expert doit savoir répondre à des questions telles que :

- Pourquoi une application ralentit-elle alors que le stockage possède encore beaucoup d'espace libre ?
- Comment distinguer une saturation de capacité d'une saturation des entrées-sorties ?
- Comment identifier un périphérique de stockage indépendamment du nom temporaire qui lui a été attribué ?
- Comment agrandir un système LVM sans interruption lorsque la configuration le permet ?
- Comment protéger un stockage contre certaines pannes matérielles ?
- Comment diagnostiquer un RAID dégradé sans aggraver l'incident ?
- Comment utiliser du stockage distant sans confondre les chemins physiques d'un SAN ?
- Comment chiffrer les données au repos et organiser la gestion des clés ?
- Comment vérifier qu'une sauvegarde permet réellement une restauration ?
- Comment éviter qu'un volume plein ne provoque l'arrêt de plusieurs services ?
- Comment prendre une décision technique à partir de mesures plutôt que d'intuitions ?

Ce niveau ne consiste pas à multiplier les commandes. Il faut comprendre leurs effets, leurs dépendances et leurs limites.

## 1.2. Compétences attendues

À la fin du cours, tu dois être capable de :

1. Concevoir une architecture combinant plusieurs couches de stockage.
2. Identifier les périphériques par des références stables.
3. Analyser les performances à partir du débit, des IOPS et de la latence.
4. Comparer des mesures avec un profil de charge représentatif.
5. Surveiller l'état matériel d'un SSD ou d'un disque dur.
6. Administrer des volumes LVM avancés, notamment les pools à allocation fine.
7. Comprendre le fonctionnement et les risques des instantanés.
8. Diagnostiquer un ensemble RAID dégradé.
9. Comprendre les principes du multipath et du stockage SAN.
10. Administrer des connexions de stockage réseau selon les besoins.
11. Concevoir un dispositif de chiffrement avec LUKS.
12. Choisir une procédure de maintenance adaptée à ext4, XFS ou Btrfs.
13. Concevoir des sauvegardes cohérentes et testées.
14. Construire des procédures de récupération documentées.
15. Automatiser certains contrôles sans introduire de risques inutiles.

## 1.3. Environnement conseillé

Un environnement de laboratoire sérieux comprend idéalement :

```text
                 MACHINE DE LABORATOIRE
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
     Disque système   Disques de test   Réseau de test
           |               |               |
           v               v               v
       Linux actif      LVM / RAID      iSCSI / SAN
```

Pour les exercices de stockage avancé, privilégie :

- Une machine virtuelle dédiée.
- Un disque système distinct des disques de laboratoire.
- Des disques virtuels supplémentaires.
- Une sauvegarde ou un instantané de la machine virtuelle.
- Un espace de test contenant uniquement des données jetables.
- Un accès console permettant de récupérer la machine en cas d'erreur de montage.
- Des journaux permettant de revoir les événements.

Les expériences sur LVM, RAID, LUKS, le multipath et les systèmes de fichiers ne doivent pas être réalisées sur un disque contenant des données importantes.

## 1.4. Convention utilisée dans les exemples

Les noms suivants sont fictifs :

```text
/dev/sdb1                 Partition de laboratoire
/dev/sdc1                 Seconde partition de laboratoire
/dev/md0                  Ensemble RAID de test
/dev/vgdata/lvprojects    Volume logique
/dev/mapper/cryptdata     Volume déchiffré
/data/projects             Point de montage
/backup                   Destination de sauvegarde
```

Un autre serveur peut utiliser des noms différents.

Avant d'exécuter une commande qui modifie des métadonnées, identifie toujours la cible réelle.

Les commandes d'observation et les commandes de modification ne présentent pas les mêmes risques. Le cours les distingue explicitement.


# 2. Architecture avancée des couches de stockage

## 2.1. Penser en couches plutôt qu'en périphériques isolés

Dans une architecture avancée, les fichiers peuvent reposer sur plusieurs couches successives.

Exemple d'une architecture comportant chiffrement et LVM :

```text
             APPLICATION
                  |
                  v
            Fichiers métier
                  |
                  v
             Système ext4
                  |
                  v
          Volume logique LVM
                  |
                  v
          Groupe de volumes
                  |
                  v
       Volume physique chiffré
                  |
                  v
           Couche LUKS/dm-crypt
                  |
                  v
           Partition ou disque
```

Cette architecture n'est qu'un exemple. Le chiffrement peut être placé à d'autres niveaux et une couche RAID ou multipath peut également être présente.

Il faut distinguer :

- Le support physique.
- Le périphérique bloc visible par Linux.
- Les éventuelles couches RAID.
- Le chiffrement.
- Les volumes LVM.
- Le système de fichiers.
- Le point de montage.
- L'application qui utilise les données.

Une erreur de diagnostic fréquente consiste à ne regarder que le système de fichiers alors que la saturation se trouve dans une couche inférieure.

Par exemple, un groupe LVM peut manquer d'espace alors que plusieurs volumes logiques existent déjà. À l'inverse, un groupe peut disposer d'espace libre alors que le système de fichiers d'un volume logique est plein.

## 2.2. Exemple d'une architecture RAID puis LVM

Une architecture possible consiste à construire un ensemble RAID, puis à créer LVM au-dessus :

```text
       Disque A                 Disque B
          |                        |
          v                        v
     Partition A              Partition B
          |                        |
          +-----------+------------+
                      |
                      v
                 RAID logiciel
                   /dev/md0
                      |
                      v
                 Volume PV
                      |
                      v
                   vgdata
                      |
           +----------+----------+
           |                     |
           v                     v
     lvprojects              lvarchives
           |                     |
           v                     v
          ext4                  XFS
           |                     |
           v                     v
     /data/projects         /data/archives
```

Cette représentation montre comment séparer deux responsabilités :

- RAID fournit certaines propriétés de redondance.
- LVM fournit une flexibilité de gestion de la capacité.

Le système de fichiers reste responsable de l'organisation des fichiers.

Attention : une architecture RAID logicielle au-dessus de plusieurs périphériques doit être conçue en fonction de la topologie réelle. Les couches supplémentaires augmentent aussi la complexité du dépannage.

## 2.3. L'ordre des couches n'est pas universel

Une autre organisation peut placer LVM sur les périphériques, puis créer des volumes logiques indépendants sur lesquels sont configurés les systèmes de fichiers.

Dans d'autres architectures, le chiffrement peut se situer entre le volume logique et le système de fichiers.

Avant de concevoir une chaîne de stockage, pose les questions suivantes :

1. Quelle couche doit gérer la redondance ?
2. À quel niveau faut-il chiffrer les données ?
3. Quelle couche doit gérer l'allocation flexible ?
4. Quel système de fichiers convient à l'application ?
5. Quel composant doit être surveillé pour détecter une panne ?
6. Comment une restauration sera-t-elle effectuée si plusieurs couches deviennent indisponibles ?

## 2.4. Le stockage est une chaîne de dépendances

Considérons ce montage :

```text
/data/projects
      |
      v
      ext4
      |
      v
/dev/vgdata/lvprojects
      |
      v
    vgdata
      |
      v
    /dev/md0
      |
      v
     RAID
      |
      v
 Plusieurs périphériques
```

Si `/dev/md0` devient indisponible, LVM peut perdre l'accès au périphérique physique qui lui fournit l'espace. Le système de fichiers situé au-dessus peut alors produire des erreurs ou devenir inaccessible.

L'observation de `/data/projects` ne suffit donc pas pour comprendre toute la situation.

L'administrateur doit suivre les dépendances vers les couches inférieures.

## 2.5. Cartographier une architecture réelle

Pour le stockage bloc :

```bash
lsblk -o NAME,PATH,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINTS
```

Pour les montages :

```bash
findmnt -o SOURCE,TARGET,FSTYPE,OPTIONS
```

Pour LVM :

```bash
sudo pvs -o+pv_used
sudo vgs -o+vg_free
sudo lvs -a -o+devices
```

Pour RAID logiciel :

```bash
cat /proc/mdstat
sudo mdadm --detail --scan
```

Pour les périphériques Device Mapper :

```bash
sudo dmsetup ls --tree
```

Ces informations peuvent être combinées pour établir une carte des dépendances.

Sur un serveur de production, documente cette carte avant un changement majeur. Elle doit permettre de répondre rapidement à la question : « Si ce périphérique disparaît, quels volumes et quels services risquent d'être affectés ? »


# 3. Identification avancée et stabilité des périphériques

## 3.1. Pourquoi `/dev/sdb` n'est pas une identité durable

Des noms comme `/dev/sda` ou `/dev/sdb` sont courants, mais ils dépendent de la manière dont le noyau détecte les périphériques.

Après un changement matériel, une modification de l'ordre de détection ou une opération de maintenance, un périphérique peut se voir attribuer un autre nom.

Sur un serveur possédant de nombreux disques, une mauvaise identification peut avoir des conséquences importantes.

Il faut donc distinguer :

- Le nom du périphérique dans le noyau.
- L'identité matérielle du disque.
- L'identifiant du chemin d'accès.
- L'identifiant de la partition.
- L'UUID du système de fichiers.
- L'identifiant d'un ensemble RAID ou d'un volume LVM.

Ces identifiants remplissent des fonctions différentes.

## 3.2. Les liens symboliques persistants

Linux expose souvent des liens symboliques sous :

```text
/dev/disk/by-id/
/dev/disk/by-path/
/dev/disk/by-uuid/
/dev/disk/by-label/
```

Consulter les identifiants disponibles :

```bash
ls -l /dev/disk/by-id/
```

Pour les UUID :

```bash
ls -l /dev/disk/by-uuid/
```

Pour les chemins matériels :

```bash
ls -l /dev/disk/by-path/
```

Les liens de type `by-id` peuvent contenir des informations issues du modèle, du numéro de série ou de l'identification fournie par la pile de stockage.

Les liens de type `by-path` décrivent plutôt un chemin de connexion matériel ou logique.

Aucun nom ne doit être choisi sans comprendre ce qu'il identifie réellement.

## 3.3. Disques, partitions et systèmes de fichiers

Une seule architecture peut contenir plusieurs identifiants différents.

```text
Disque matériel
  Identité : modèle + numéro de série
       |
       v
Partition
  Identité : numéro de partition / PARTUUID
       |
       v
Système de fichiers
  Identité : UUID / label
       |
       v
Point de montage
  Identité : chemin dans l'arborescence
```

L'UUID du système de fichiers est souvent adapté à `/etc/fstab`.

Le numéro de série du périphérique peut aider à identifier le disque lui-même.

Le PARTUUID identifie une partition dans sa table de partitions.

Il ne faut pas confondre ces trois identifiants ni supposer qu'ils désignent le même objet.

## 3.4. Examiner les informations matérielles

Avec `lsblk` :

```bash
lsblk -o NAME,MODEL,SERIAL,WWN,SIZE,TYPE,FSTYPE,UUID,MOUNTPOINTS
```

Selon le matériel et les droits disponibles, certains champs peuvent rester vides.

Pour afficher les informations de partitionnement :

```bash
sudo fdisk -l
```

Pour identifier les systèmes de fichiers :

```bash
sudo blkid
```

Pour rechercher les informations de correspondance entre noms et identifiants :

```bash
ls -l /dev/disk/by-id/
```

Cette méthode est utile lorsqu'un serveur contient plusieurs disques de capacité identique.

## 3.5. Cas des disques NVMe

Les périphériques NVMe utilisent généralement des noms distincts de ceux de nombreux disques SATA.

Exemples :

```text
/dev/nvme0n1
/dev/nvme0n1p1
/dev/nvme1n1
```

Le premier exemple représente un namespace NVMe et le second une partition de ce namespace.

Consulter les périphériques détectés :

```bash
lsblk
```

Si les outils NVMe sont disponibles :

```bash
sudo nvme list
```

Les outils `nvme-cli` et leurs fonctionnalités dépendent de l'environnement et du matériel.

Ne confonds pas le contrôleur NVMe avec le namespace qui expose la capacité utilisable par le système.

## 3.6. Cas des environnements multipath

Dans un SAN, un même stockage logique peut être accessible par plusieurs chemins.

```text
                Stockage distant
                       |
               +-------+-------+
               |               |
               v               v
          Chemin A         Chemin B
               |               |
               +-------+-------+
                       |
                       v
                 Device Mapper
                       |
                       v
               Périphérique logique
```

Le système doit reconnaître que plusieurs chemins désignent le même objet de stockage.

Il ne faut surtout pas créer séparément un système de fichiers sur chacun des chemins bruts d'un même volume SAN.

Cela risque de corrompre les données, car les chemins peuvent représenter le même espace de blocs.

La section consacrée au multipath détaillera cette architecture.


# 4. Modèle de performance : IOPS, débit, latence et profondeur de file

## 4.1. La capacité n'est pas la performance

Un volume de 10 To peut être lent pour une application donnée, tandis qu'un volume de capacité bien inférieure peut répondre très rapidement.

La capacité indique combien de données peuvent être conservées.

Les performances décrivent la manière dont le stockage répond aux opérations.

Les principales dimensions sont :

- Le débit.
- Les opérations d'entrée-sortie par seconde.
- La latence.
- La profondeur de file.
- Le type de charge.
- La concurrence des accès.
- Les caractéristiques du périphérique.
- Les performances du réseau, pour le stockage distant.

## 4.2. IOPS

IOPS signifie *Input/Output Operations Per Second*.

Il s'agit du nombre d'opérations d'entrée-sortie effectuées par seconde.

Une charge comportant de nombreuses petites opérations aléatoires exige souvent un profil de performance différent d'une charge lisant de grands fichiers séquentiels.

Exemple conceptuel :

```text
Charge A : lecture aléatoire
4 Kio par opération
Beaucoup d'opérations
Accès dispersés

Charge B : lecture séquentielle
1 Mio par opération
Lecture continue
Peu d'opérations pour un grand volume
```

La charge A peut nécessiter un nombre élevé d'IOPS.

La charge B peut viser un débit important avec un nombre d'opérations différent.

## 4.3. Débit

Le débit exprime le volume de données transféré par unité de temps.

Exemples :

```text
100 Mio/s
500 Mio/s
2 Gio/s
```

Un débit élevé ne signifie pas automatiquement une faible latence.

Une application peut transférer beaucoup de données par seconde et ressentir malgré tout des ralentissements lors de certaines opérations.

Il faut donc interpréter le débit avec le type d'opération et la latence.

## 4.4. Latence

La latence mesure le temps nécessaire pour obtenir une réponse à une opération.

Exemples conceptuels :

```text
Opération A : réponse en 0,5 ms
Opération B : réponse en 8 ms
Opération C : réponse en 150 ms
```

Ces valeurs sont illustratives. La latence attendue dépend du support, du contrôleur, du réseau, du protocole, de la charge et du type d'opération.

Une application sensible aux réponses rapides peut être fortement affectée par une augmentation de latence même si le volume est loin d'être plein.

## 4.5. Profondeur de file et concurrence

Les périphériques et les couches de stockage peuvent gérer plusieurs opérations en cours.

La profondeur de file représente, dans le contexte considéré, le nombre d'opérations en attente ou simultanément prises en charge.

Augmenter la concurrence peut améliorer le débit jusqu'à un certain point.

Mais augmenter indéfiniment le nombre d'opérations en attente peut également augmenter la latence.

```text
Peu de requêtes
      |
      v
Stockage peu sollicité
      |
      v
Temps de réponse faible
      |
      v
Augmentation de la concurrence
      |
      v
Meilleure utilisation possible du stockage
      |
      v
Saturation ou files d'attente excessives
      |
      v
Latence qui augmente
```

Le résultat dépend du stockage et de son profil de charge. Il ne faut donc pas adopter une valeur de profondeur de file comme une règle universelle.

## 4.6. La loi de Little comme outil de raisonnement

Dans un système stable, une relation fondamentale permet de relier :

- Le débit moyen des requêtes.
- Le temps moyen passé dans le système.
- Le nombre moyen de requêtes en cours.

Sous une forme simplifiée :

\[
L = \lambda W
\]

Où :

- \(L\) représente le nombre moyen d'opérations présentes dans le système.
- \(\lambda\) représente le débit moyen de requêtes.
- \(W\) représente le temps moyen passé dans le système.

Exemple :

Si un système traite en moyenne 200 opérations par seconde et que le temps moyen passé par opération est de 10 millisecondes :

\[
L = 200 \times 0{,}010 = 2
\]

Le système compte en moyenne environ deux opérations en cours, selon les hypothèses de cette approximation.

Cette relation aide à comprendre pourquoi une augmentation de la latence peut accroître le nombre d'opérations simultanément présentes dans le système.

Elle ne remplace pas les mesures et ne permet pas de conclure seule à la cause d'un ralentissement.

## 4.7. Profil de charge et choix du stockage

| Profil applicatif | Besoin dominant possible | Point à mesurer |
|---|---|---|
| Base de données transactionnelle | Latence et IOPS | Temps de réponse et lectures/écritures aléatoires |
| Entrepôt de données | Débit séquentiel et concurrence | Débit soutenu et temps des requêtes |
| Archivage | Capacité et coût | Capacité utile et vitesse de restauration |
| Serveur de fichiers | Mélange d'accès et concurrence | Latence, débit, nombre de clients |
| Machine virtuelle | Latence et charge mixte | IOPS, latence de queue et contention |
| Journaux applicatifs | Écriture soutenue et rétention | Débit d'écriture et durée des opérations |

Le choix final dépend du comportement réel de l'application. Il est préférable de reproduire la charge représentative avant de dimensionner le stockage.


# 5. Diagnostic avancé des entrées-sorties

## 5.1. Première lecture de l'état du système

Un diagnostic de performance commence par la collecte de plusieurs mesures, idéalement pendant que le problème se produit.

Examiner la capacité :

```bash
df -hT
```

Examiner les inodes :

```bash
df -i
```

Observer les périphériques blocs :

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
```

Puis examiner les statistiques d'entrée-sortie :

```bash
iostat -xz 1 10
```

Cette commande provient généralement du paquet `sysstat`.

Elle produit plusieurs rapports dans le temps. La première ligne de certaines statistiques représente des moyennes depuis le démarrage, tandis que les rapports suivants donnent des intervalles plus récents.

Il faut donc éviter d'interpréter uniquement le premier rapport comme s'il décrivait exclusivement l'incident actuel.

## 5.2. Lire `iostat`

Les champs disponibles varient selon les versions, mais on peut généralement examiner :

- `r/s` : nombre moyen de lectures par seconde.
- `w/s` : nombre moyen d'écritures par seconde.
- `rkB/s` ou `rMB/s` : débit de lecture.
- `wkB/s` ou `wMB/s` : débit d'écriture.
- `r_await` : temps de réponse moyen des lectures lorsque ce champ est disponible.
- `w_await` : temps de réponse moyen des écritures.
- `aqu-sz` : longueur moyenne de la file d'attente, selon la version.
- `%util` : indicateur d'activité du périphérique.

Ces mesures doivent être interprétées ensemble.

**Attention à `%util` : ce pourcentage ne constitue pas, à lui seul, une mesure universelle de saturation.** Sa signification dépend notamment de l'architecture du périphérique. Un périphérique à file unique et un SSD NVMe à traitement parallèle ne se lisent pas toujours de la même manière.

## 5.3. Exemple d'interprétation

Supposons que les mesures montrent :

```text
Débit de lecture       : modéré
Débit d'écriture       : modéré
Latence moyenne        : élevée
Espace disponible      : important
Erreurs matérielles    : aucune erreur récente évidente
```

Il serait incorrect de conclure que « le disque n'est pas en cause » simplement parce que son débit est modéré.

Plusieurs hypothèses restent possibles :

- La charge effectue de petites opérations.
- Une couche intermédiaire est en attente.
- Une file d'attente est trop longue.
- Le stockage distant présente une latence réseau.
- Un autre volume utilise le même périphérique physique.
- Le problème se situe dans une couche logicielle.
- La mesure ne couvre pas exactement la période de l'incident.

La prochaine étape doit être de corréler les données.

## 5.4. Identifier les processus actifs

Pour observer les processus qui génèrent des entrées-sorties, des outils comme `iotop` peuvent être utiles lorsqu'ils sont disponibles.

```bash
sudo iotop
```

L'outil peut nécessiter des privilèges spécifiques et n'est pas installé par défaut sur toutes les distributions.

Pour consulter des informations de processus et de ressources :

```bash
pidstat -d 1 10
```

Cette commande est également généralement fournie par `sysstat`.

Elle permet d'observer l'activité d'entrée-sortie des processus selon les champs exposés par la version installée.

Les statistiques par processus ne montrent pas nécessairement toute la chaîne d'attente d'un stockage distant. Elles doivent être rapprochées des mesures du périphérique et du réseau.

## 5.5. Examiner les journaux du noyau

```bash
sudo journalctl -k --since "30 minutes ago"
```

Rechercher des erreurs pertinentes :

```bash
sudo journalctl -k --since "30 minutes ago" \
  | grep -Ei 'I/O error|timeout|reset|nvme|scsi|ata|ext4|xfs|buffer I/O'
```

Des erreurs répétées peuvent suggérer :

- Un problème matériel.
- Un défaut de connectivité.
- Une réinitialisation du contrôleur.
- Un problème sur une couche de stockage.
- Des erreurs d'accès au système de fichiers.

Le texte exact dépend du noyau, du pilote et du matériel.

Ne réduis pas le diagnostic à une recherche par mots-clés : examine le contexte temporel et les événements précédents.

## 5.6. Examiner les statistiques du noyau

Les statistiques des périphériques blocs sont accessibles à travers plusieurs interfaces, notamment :

```bash
cat /proc/diskstats
```

Les champs sont numériques et leur interprétation dépend du format des statistiques exposées par le noyau.

Pour une analyse manuelle rapide, `iostat` est plus pratique. Pour une analyse poussée ou une automatisation, les statistiques brutes peuvent être collectées puis comparées dans le temps.

Une seule lecture de `/proc/diskstats` ne donne pas un débit instantané complet. Il faut comparer deux points dans le temps et calculer les différences avec les bonnes unités.

## 5.7. Quand les outils classiques ne suffisent plus

Sur des systèmes complexes, les outils standards peuvent ne pas identifier le composant exact responsable de la latence.

Des outils plus avancés peuvent être utiles :

- Tracepoints du noyau.
- eBPF et outils compatibles avec BPF.
- Traces de bloc, selon le noyau.
- Traces des pilotes et du multipath.
- Statistiques du SAN.
- Métriques du système de virtualisation.
- Métriques de l'application.

Ces outils doivent être choisis en fonction de la question à résoudre. Une trace détaillée peut produire beaucoup de données et elle-même ajouter une charge.

La première règle reste de réduire le problème à une hypothèse testable.


# 6. Mesure des performances avec fio

## 6.1. Pourquoi utiliser un générateur de charge ?

`fio` est un outil de mesure des performances d'entrée-sortie.

Il peut simuler différents profils :

- Lectures séquentielles.
- Écritures séquentielles.
- Lectures aléatoires.
- Écritures aléatoires.
- Charges mixtes.
- Différentes tailles de blocs.
- Différentes profondeurs de file.
- Plusieurs tâches en parallèle.

Il ne faut pas confondre une mesure avec une garantie de performance. Les résultats ne sont représentatifs que si le scénario correspond aux conditions que l'on souhaite étudier.

## 6.2. Règles de sécurité avant un test fio

> **N'exécute jamais un test d'écriture sur le périphérique brut d'un système en production.**

Le laboratoire doit utiliser un fichier dédié sur un volume de test.

Avant l'expérience :

```bash
findmnt /data
df -hT /data
```

Créer un emplacement réservé :

```bash
sudo mkdir -p /data/fio-lab
sudo chown "$USER":"$(id -gn)" /data/fio-lab
```

Choisis une taille compatible avec l'espace disponible.

Un test peut :

- Consommer beaucoup d'espace.
- Produire une charge intensive.
- Affecter les autres utilisateurs du même stockage.
- Modifier le fichier cible.
- Échauffer les périphériques.
- Dégrader temporairement la latence des autres services.

Les tests lourds doivent être programmés pendant une fenêtre adaptée.

## 6.3. Vérifier l'installation

Sur Debian ou Ubuntu, le paquet est généralement disponible sous le nom `fio` :

```bash
sudo apt update
sudo apt install fio
```

Sur une distribution utilisant DNF :

```bash
sudo dnf install fio
```

Consulter la version :

```bash
fio --version
```

## 6.4. Mesurer un profil séquentiel

Sur un fichier de test dédié :

```bash
fio \
  --name=seqread \
  --filename=/data/fio-lab/seqread.bin \
  --size=1G \
  --rw=read \
  --bs=1M \
  --iodepth=4 \
  --numjobs=1 \
  --runtime=30 \
  --time_based \
  --group_reporting
```

Interprétation des paramètres :

- `--name` : nom du scénario.
- `--filename` : fichier cible.
- `--size=1G` : taille du fichier de test.
- `--rw=read` : type d'accès.
- `--bs=1M` : taille des blocs de requête.
- `--iodepth=4` : profondeur de file demandée.
- `--numjobs=1` : nombre de tâches.
- `--runtime=30` : durée de la phase chronométrée.
- `--time_based` : exécute le scénario selon la durée demandée.
- `--group_reporting` : regroupe les résultats des tâches.

Selon le moteur d'entrée-sortie choisi et le système utilisé, la profondeur de file demandée ne se traduit pas nécessairement par la profondeur effective attendue.

## 6.5. Mesurer des lectures aléatoires de petite taille

Toujours dans le laboratoire, sur un fichier dédié et après vérification des capacités :

```bash
fio \
  --name=randread \
  --filename=/data/fio-lab/randread.bin \
  --size=1G \
  --rw=randread \
  --bs=4k \
  --iodepth=16 \
  --numjobs=2 \
  --runtime=30 \
  --time_based \
  --group_reporting
```

Ce scénario cherche à caractériser les lectures aléatoires de petite taille.

Il ne mesure pas tous les aspects d'une vraie base de données. Le cache, les synchronisations, la concurrence applicative et les exigences de durabilité peuvent changer les résultats.

## 6.6. Mesurer les écritures sans toucher aux données existantes

Un scénario d'écriture doit utiliser un fichier jetable, qui ne contient pas de données utiles.

Exemple :

```bash
fio \
  --name=randwrite \
  --filename=/data/fio-lab/randwrite.bin \
  --size=1G \
  --rw=randwrite \
  --bs=4k \
  --iodepth=8 \
  --numjobs=1 \
  --runtime=30 \
  --time_based \
  --group_reporting
```

Ce test remplit et modifie le fichier de test. Il faut donc vérifier que le chemin est bien dédié à cette expérience.

Il est déconseillé de réutiliser sans réflexion un fichier contenant des données importantes ou un chemin qui pourrait pointer vers un autre type de stockage.

## 6.7. Comprendre les résultats

`fio` peut afficher :

- Les IOPS.
- Le débit.
- La latence moyenne.
- Des distributions de latence.
- Des quantiles, selon les options et la version.
- Les caractéristiques de la charge générée.

Supposons que deux scénarios donnent les résultats illustratifs suivants :

```text
Scénario A
IOPS : 20 000
Latence moyenne : 1,2 ms

Scénario B
IOPS : 22 000
Latence moyenne : 8 ms
```

Le scénario B présente un nombre d'opérations supérieur, mais une latence moyenne beaucoup plus élevée.

Il serait donc insuffisant de comparer uniquement les IOPS.

Pour les applications sensibles à la latence, les percentiles tels que p95 ou p99 peuvent être importants. Ils aident à comprendre le comportement des opérations les plus lentes, et pas seulement la moyenne.

## 6.8. Construire un protocole de benchmark

Une comparaison sérieuse devrait documenter :

```text
Périphérique testé :
Capacité :
Système de fichiers :
Options de montage :
Couche LVM ou RAID :
Type de charge :
Taille des blocs :
Concurrence :
Durée :
État du cache :
Température éventuelle :
Charge concurrente :
Version de fio :
Débit :
IOPS :
Latence moyenne :
Latence de queue :
Observations :
```

Répète les mesures dans des conditions comparables.

Ne compare pas directement des mesures obtenues dans des contextes différents, par exemple un disque isolé et un autre qui partage sa capacité avec plusieurs applications actives.

## 6.9. Pourquoi les résultats peuvent tromper

Les principaux facteurs de confusion sont :

- Le cache système.
- Le cache du contrôleur.
- La mémoire du stockage distant.
- La concurrence des autres charges.
- La température et l'état du périphérique.
- Les limites imposées par une machine virtuelle.
- Le chiffrement.
- Le RAID.
- Les limites de débit du réseau.
- Les options de synchronisation.
- Le type d'accès et la taille des blocs.

Un benchmark n'a de valeur que si l'on sait ce qu'il a réellement mesuré.


# 7. Santé matérielle et surveillance des périphériques

## 7.1. Capacité et santé sont deux choses différentes

Un disque peut afficher beaucoup d'espace libre tout en présentant des erreurs matérielles.

À l'inverse, un disque presque plein peut être parfaitement sain d'un point de vue matériel.

Il faut donc surveiller séparément :

- La capacité.
- Les performances.
- La santé du support.
- Les erreurs du noyau.
- La disponibilité des chemins.
- L'état RAID.
- L'intégrité des données.

## 7.2. Examiner les informations SMART

Pour les périphériques compatibles avec SMART et lorsque les outils appropriés sont installés :

```bash
sudo smartctl -a /dev/sdX
```

Remplace `/dev/sdX` par le périphérique exact.

Cette commande peut afficher des informations sur l'état déclaré du disque, les erreurs, les compteurs et l'historique disponible.

Pour un test SMART étendu sur un périphérique compatible :

```bash
sudo smartctl -t long /dev/sdX
```

Cette commande demande un test au périphérique lorsqu'il le prend en charge. La durée et les possibilités dépendent du modèle.

Il faut consulter les résultats et le manuel de `smartctl` pour comprendre les informations disponibles sur le périphérique concerné.

Le support SMART peut varier selon que le disque est directement attaché, derrière un contrôleur, dans un boîtier USB ou exposé par une couche de virtualisation.

## 7.3. SSD et NVMe

Sur un environnement NVMe compatible :

```bash
sudo nvme list
```

Afficher les informations de santé d'un périphérique :

```bash
sudo nvme smart-log /dev/nvme0
```

Le chemin utilisé dépend du contrôleur NVMe et des outils installés.

Les données de santé peuvent notamment inclure des compteurs d'erreurs, une estimation de l'usure ou d'autres informations exposées par le périphérique.

Ces indicateurs doivent être interprétés conformément aux caractéristiques du matériel. Une seule valeur ne constitue pas toujours un diagnostic complet.

## 7.4. Quelles observations conserver ?

Pour un système important, conserve une évolution dans le temps de :

```text
Date et heure
Périphérique identifié
Numéro de série ou identifiant stable
État de santé disponible
Erreurs d'entrée-sortie
Latence observée
Température si disponible
Événements du contrôleur
Événements RAID ou multipath
Actions de maintenance
```

Une évolution anormale peut être plus informative qu'une valeur isolée.

## 7.5. Quand remplacer un périphérique ?

La décision dépend de plusieurs facteurs :

- Erreurs confirmées.
- Évolution des indicateurs de santé.
- Recommandations du fabricant.
- Rôle du périphérique dans la redondance.
- Charge et impact potentiel d'une panne.
- Possibilité de remplacement contrôlé.
- État des sauvegardes.
- Procédure de reconstruction.

Ne remplace pas un périphérique en retirant au hasard un chemin d'accès dans une architecture multipath ou un membre RAID.

Avant une intervention, vérifie l'identité exacte du composant et les procédures du système.


# 8. LVM expert : allocation, déplacements et provisionnement fin

## 8.1. Rappel des composants LVM

```text
Périphériques
      |
      v
     PV
      |
      v
     VG
      |
      +----------------+
      |                |
      v                v
     LV A             LV B
      |                |
      v                v
  Système A        Système B
```

LVM offre plusieurs capacités avancées :

- Ajouter de nouveaux périphériques à un groupe.
- Agrandir des volumes logiques.
- Déplacer des extents entre périphériques compatibles.
- Créer des volumes à allocation fine.
- Créer des instantanés.
- Surveiller certains pools et leurs métadonnées.

Ces fonctionnalités ne suppriment pas le besoin de surveiller le stockage physique sous-jacent.

## 8.2. Examiner l'allocation réelle

Les commandes d'observation principales sont :

```bash
sudo pvs -o+pv_used,pv_free
sudo vgs -o+vg_free,vg_size
sudo lvs -a -o+devices
```

Ces commandes aident à identifier :

- Les volumes physiques présents.
- L'espace utilisé par LVM.
- L'espace libre de chaque groupe.
- Les volumes logiques.
- Les périphériques sur lesquels les extents sont alloués.

Dans une architecture complexe, le nom du volume logique ne suffit pas. Il faut comprendre sur quels périphériques il repose.

## 8.3. Ajouter un volume physique à un groupe

Lorsqu'un nouveau périphérique de test a été préparé et validé :

```bash
sudo pvcreate /dev/sdc1
sudo vgextend vgdata /dev/sdc1
```

Ces commandes modifient les métadonnées LVM du périphérique et du groupe.

Elles ne doivent être exécutées que sur un périphérique dédié à l'opération.

Après l'ajout :

```bash
sudo pvs
sudo vgs
```

Le groupe dispose désormais d'une capacité supplémentaire, sous réserve de l'espace réellement utilisable.

## 8.4. Déplacer des extents avec pvmove

`pvmove` peut déplacer des extents LVM d'un volume physique vers un autre dans certaines configurations compatibles.

Ce mécanisme peut être utilisé lors d'une migration ou pour préparer le retrait d'un périphérique.

Exemple schématique :

```text
Avant :

vgdata
├── /dev/sdb1 : extents utilisés
└── /dev/sdc1 : espace disponible

Après un déplacement approprié :

vgdata
├── /dev/sdb1 : extents libérés
└── /dev/sdc1 : extents déplacés
```

La commande générale prend la forme :

```bash
sudo pvmove /dev/sdb1 /dev/sdc1
```

**Cet exemple n'est pas à exécuter sans inspection préalable.** Il suppose que les deux périphériques appartiennent correctement à l'architecture LVM et que le périphérique de destination dispose de suffisamment d'espace libre.

Avant l'opération :

```bash
sudo pvs -o+pv_used,pv_free
sudo vgs
sudo lvs -a -o+devices
```

Il faut aussi tenir compte des éventuels volumes RAID, pools fins et contraintes de disponibilité.

Après l'opération, vérifie les dépendances :

```bash
sudo pvs -o+pv_used,pv_free
sudo lvs -a -o+devices
```

Ne retire le périphérique physique qu'après avoir confirmé que les volumes ne dépendent plus de lui et que la procédure de retrait adaptée a été suivie.

## 8.5. Comprendre le provisionnement fin

Avec un volume logique classique, la capacité affectée est généralement réservée dans le groupe de volumes.

Avec un pool à allocation fine, les volumes logiques peuvent présenter une capacité virtuelle supérieure à la capacité physique déjà consommée par leurs données.

```text
Pool de stockage physique : 100 GiB
          |
          +----------------------+
          |                      |
          v                      v
     Volume virtuel A       Volume virtuel B
      Capacité 80 GiB        Capacité 80 GiB
```

La capacité virtuelle cumulée atteint 160 GiB, alors que le pool ne possède que 100 GiB de capacité physique.

Cette surallocation peut être utile si tous les volumes n'utilisent pas simultanément leur capacité virtuelle.

Elle peut aussi devenir dangereuse : **si les volumes consomment plus d'espace physique que le pool ne peut en fournir, les écritures peuvent échouer**.

Le provisionnement fin doit donc être accompagné d'une surveillance de capacité et d'une stratégie de réaction.

## 8.6. Créer un pool à allocation fine

Dans un laboratoire LVM disposant d'un groupe de volumes de test et d'assez d'espace libre, un pool peut être créé selon un modèle tel que :

```bash
sudo lvcreate --type thin-pool \
  -L 20G \
  --poolmetadatasize 1G \
  -n tpdata vgdata
```

Cette commande est illustrative. Les dimensions doivent être adaptées au volume de données, à la charge de métadonnées et à la version des outils.

Vérifier ensuite :

```bash
sudo lvs -a
sudo lvs -o+data_percent,metadata_percent
```

Les noms de colonnes disponibles peuvent dépendre de la version LVM.

Ne crée pas un pool avec une capacité inadaptée à la charge attendue. Le dimensionnement des métadonnées fait partie de la conception du pool.

## 8.7. Créer un volume logique fin

À partir du pool de test `tpdata` :

```bash
sudo lvcreate --type thin \
  -V 50G \
  -n lvvirtual \
  vgdata/tpdata
```

Ce volume présente une capacité virtuelle de 50 GiB, même si le pool de données a été créé avec une capacité physique de 20 GiB dans l'exemple.

La différence n'est pas une création de capacité physique : les blocs sont alloués dans le pool à mesure qu'ils sont nécessaires.

Contrôler :

```bash
sudo lvs -a -o+lv_size,data_percent,metadata_percent
```

Surveiller l'espace physique du pool est indispensable, même si les systèmes de fichiers des volumes virtuels affichent encore beaucoup d'espace libre.

## 8.8. Les deux limites du pool fin

Le pool doit surveiller au moins deux ressources :

1. Les données physiques du pool.
2. Les métadonnées du pool.

Un pool peut rencontrer un problème parce que les données occupent presque toute la capacité disponible, ou parce que les métadonnées ne disposent plus de suffisamment d'espace ou ne peuvent plus évoluer correctement.

Schéma :

```text
              POOL FIN
                  |
          +-------+-------+
          |               |
          v               v
   Espace de données   Métadonnées
          |               |
          v               v
    Blocs alloués     Cartographie des
    physiquement      blocs et volumes
          |               |
          +-------+-------+
                  |
                  v
            Surveillance
```

Les seuils d'alerte doivent être déterminés selon le comportement attendu, la capacité disponible pour extension et la procédure de maintenance.

## 8.9. Réagir à un pool presque plein

Lorsque le pool approche de sa limite :

1. Vérifier la capacité physique.
2. Examiner les volumes qui consomment les données.
3. Examiner le pourcentage des métadonnées.
4. Identifier la croissance récente.
5. Évaluer s'il est possible d'agrandir le pool.
6. Vérifier les périphériques disponibles pour cette extension.
7. Planifier et appliquer la modification.
8. Vérifier l'état des volumes et des applications.

Les instantanés peuvent également retenir des blocs et empêcher leur libération. Il faut donc examiner la politique d'instantanés avant de conclure que la capacité est consommée par les seuls volumes actifs.

N'efface pas un instantané sans vérifier son utilité opérationnelle.


# 9. Instantanés et gestion de la cohérence

## 9.1. Qu'est-ce qu'un instantané ?

Un instantané représente un état logique des données à un moment donné, selon les mécanismes pris en charge par la couche concernée.

Il peut être utilisé pour :

- Préparer une sauvegarde.
- Faciliter une opération de maintenance.
- Créer un environnement temporaire.
- Comparer des états.
- Faciliter certaines restaurations.

Mais un instantané n'est pas automatiquement une sauvegarde indépendante.

S'il repose sur le même pool ou le même périphérique que le volume source, une panne qui affecte ce stockage peut également affecter l'instantané.

## 9.2. Instantané LVM classique

Les instantanés LVM classiques à copie sur écriture peuvent conserver les blocs nécessaires à la représentation de l'état d'origine.

Lorsque des blocs changent sur le volume source, une partie de la capacité de l'instantané peut être utilisée pour conserver les anciennes versions nécessaires.

Schéma :

```text
Volume source
      |
      v
Instantané créé
      |
      +----------------------+
      |                      |
      v                      v
État initial          Modifications ultérieures
conservé selon        sur le volume source
la mécanique de
l'instantané
```

Si la capacité de copie sur écriture est épuisée, l'instantané classique peut devenir invalide.

Il est donc nécessaire de dimensionner et surveiller sa capacité.

## 9.3. Créer un instantané classique

Sur un volume de laboratoire identifié, monté ou non selon la procédure applicable :

```bash
sudo lvcreate \
  --snapshot \
  --size 5G \
  --name lvdata-snap \
  /dev/vgdata/lvdata
```

Cette commande est un exemple. Le volume source et le groupe doivent réellement exister.

Avant la création, vérifie :

```bash
sudo lvs -a
sudo vgs
```

Après la création :

```bash
sudo lvs -a -o+devices
```

Selon le scénario et l'outil de sauvegarde, il peut être nécessaire de suspendre les écritures ou de préparer le système de fichiers avant de créer l'instantané.

## 9.4. Instantané et cohérence applicative

La cohérence des données est un enjeu différent de l'instantané lui-même.

Une base de données peut avoir des données en mémoire, des journaux et plusieurs fichiers qui doivent représenter un état cohérent.

Un instantané bloc effectué à un instant précis peut ne pas suffire à garantir la cohérence applicative si les écritures sont toujours en cours.

Les méthodes possibles comprennent, selon l'application :

- Une mise en pause des écritures.
- Un mécanisme natif de sauvegarde cohérente.
- Une coordination des services.
- Une procédure documentée de gel et dégel du système de fichiers, lorsque appropriée.
- Des outils de sauvegarde intégrés à l'application.

Il faut choisir la méthode adaptée au service.

## 9.5. Instantanés de volumes fins

Les instantanés des volumes à allocation fine ont un fonctionnement distinct des instantanés classiques.

Ils peuvent partager le pool de données et économiser de l'espace en évitant de dupliquer immédiatement tous les blocs.

Cette efficacité a une contrepartie : la capacité du pool et l'évolution de ses métadonnées deviennent des éléments critiques pour tous les volumes qui en dépendent.

Consulte :

```bash
sudo lvs -a -o+lv_size,data_percent,metadata_percent
```

L'efficacité du stockage ne doit pas se transformer en une surallocation non contrôlée.

## 9.6. Instantanés Btrfs

Btrfs prend en charge les sous-volumes et les instantanés selon son modèle de gestion.

Consulter les sous-volumes :

```bash
sudo btrfs subvolume list /data
```

Un instantané Btrfs peut être créé avec `btrfs subvolume snapshot` selon la topologie du système.

La procédure doit prendre en compte :

- Le montage contenant le sous-volume.
- Le caractère lecture seule ou non de l'instantané.
- L'emplacement de la destination.
- Les dépendances du système.
- La consommation de capacité.

Comme pour LVM, un instantané placé sur le même support n'est pas une copie de sauvegarde indépendante de ce support.

## 9.7. Politique d'instantanés

Une stratégie efficace doit définir :

```text
Pourquoi créer un instantané ?
À quel moment ?
Pour combien de temps ?
Quel est le coût en capacité ?
Comment surveiller son état ?
Qui peut le supprimer ?
Comment vérifier la cohérence ?
Comment restaurer à partir de cet état ?
```

Les instantanés ne doivent pas être conservés indéfiniment sans comprendre leur consommation et leur impact.


# 10. RAID avancé : dégradation, reconstruction et exploitation

## 10.1. Comprendre les états d'un RAID

Un RAID logiciel peut être :

- Actif et sain.
- En cours de synchronisation.
- Dégradé.
- En reconstruction.
- En erreur.
- Inaccessible.

Ces états ne sont pas équivalents.

Un RAID dégradé peut encore fournir les données, mais il a perdu une partie de sa tolérance aux pannes.

Le temps de reconstruction et la charge générée peuvent aussi affecter les performances.

## 10.2. Observer l'ensemble

Commence par :

```bash
cat /proc/mdstat
```

Puis :

```bash
sudo mdadm --detail --scan
```

Et, pour un ensemble identifié :

```bash
sudo mdadm --detail /dev/md0
```

Ces commandes permettent de vérifier l'état de l'ensemble et les composants qui le constituent.

Ne suppose pas que `/dev/md0` est toujours le nom de l'ensemble. Identifie le vrai périphérique RAID avant d'utiliser les commandes.

## 10.3. Exemple d'une panne de composant

```text
RAID 1
|
+-- Composant A : actif
|
+-- Composant B : en panne
          |
          v
      RAID dégradé
          |
          v
 Accès éventuellement maintenu
 avec redondance réduite
```

La première priorité est de vérifier ce qui s'est réellement produit.

Il faut distinguer :

- La panne du support physique.
- La perte d'un chemin.
- Une erreur de connectivité.
- Un problème de contrôleur.
- Une défaillance logique de l'ensemble.
- Un problème qui touche simultanément plusieurs composants.

Dans un environnement SAN, un chemin indisponible peut être confondu avec une panne de disque si la topologie n'a pas été correctement identifiée.

## 10.4. Procédure de réponse initiale

Lorsqu'un RAID semble dégradé :

1. Ne lance pas immédiatement une reconstruction.
2. Collecte l'état de l'ensemble.
3. Identifie le composant défaillant.
4. Vérifie les journaux et le matériel.
5. Vérifie les sauvegardes.
6. Détermine la procédure adaptée au niveau RAID.
7. Prépare le remplacement du composant.
8. Lance l'action documentée et surveille sa progression.
9. Vérifie l'état final.

Commandes d'observation :

```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
sudo journalctl -k --since "1 hour ago"
lsblk -o NAME,SIZE,MODEL,SERIAL,TYPE,MOUNTPOINTS
```

En production, certaines commandes de gestion RAID peuvent avoir des conséquences importantes. Les commandes de remplacement doivent être exécutées avec l'identité exacte du composant et selon la documentation de la version installée.

## 10.5. Remplacement d'un composant

Le principe général dépend du niveau RAID, mais une procédure documentée comprend :

```text
Diagnostic
    |
    v
Identification du composant
    |
    v
Vérification de l'état matériel
    |
    v
Remplacement physique ou logique autorisé
    |
    v
Préparation du nouveau périphérique
    |
    v
Ajout contrôlé à l'ensemble
    |
    v
Reconstruction
    |
    v
Contrôle final
```

Il ne faut pas copier aveuglément une commande trouvée dans un ancien runbook : le périphérique désigné comme membre défaillant dans l'ancien document peut ne pas être le bon dans la situation présente.

## 10.6. Reconstruction et performance

Pendant une reconstruction, le RAID utilise des ressources d'entrée-sortie pour recopier ou reconstruire les données.

La charge peut inclure :

- La reconstruction.
- Les lectures des applications.
- Les écritures des applications.
- Les contrôles de cohérence.
- Les sauvegardes.
- Les autres opérations de maintenance.

Il faut donc suivre à la fois la progression de la reconstruction et les performances des services.

Une reconstruction accélérée peut réduire la durée d'exposition à une panne, mais elle peut aussi perturber les applications. Le choix doit prendre en compte le niveau de risque et les exigences de service.

## 10.7. Contrôle après reconstruction

Après la fin de la reconstruction :

```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
sudo journalctl -k --since "1 hour ago"
```

Vérifie :

- L'état de tous les composants.
- L'absence d'une reconstruction toujours active.
- Les erreurs restantes.
- Les performances.
- La santé du périphérique.
- Les alertes de supervision.

Un état RAID redevenu sain ne garantit pas que la cause de la panne initiale a été supprimée. Il faut déterminer pourquoi le composant a été perdu.

## 10.8. RAID ne remplace pas la sauvegarde

Le RAID apporte des propriétés de disponibilité selon son niveau et son état.

Il ne protège pas nécessairement contre :

- La suppression accidentelle.
- La corruption logique propagée.
- Un ransomware.
- Une erreur d'administration.
- La destruction du système de stockage.
- Une panne touchant trop de composants.
- La perte d'un ensemble et de ses dépendances.

Une stratégie de production doit conserver une capacité de restauration indépendante.


# 11. Stockage multipath et environnements SAN

## 11.1. Le problème du chemin unique

Un serveur peut accéder à un volume distant au moyen d'un réseau de stockage, par exemple par une infrastructure Fibre Channel ou iSCSI.

Si le volume n'a qu'un seul chemin d'accès, la défaillance de ce chemin peut le rendre inaccessible même si le stockage distant fonctionne toujours.

Le multipath permet de représenter plusieurs chemins vers un même stockage logique.

## 11.2. Architecture multipath

```text
                      SERVEUR LINUX
                            |
                   +--------+--------+
                   |                 |
                   v                 v
              Hôte réseau A     Hôte réseau B
                   |                 |
                   v                 v
                Commutateur A     Commutateur B
                   |                 |
                   +--------+--------+
                            |
                            v
                     Stockage SAN
                            |
                            v
                    Volume logique distant
```

Sur le serveur, un logiciel multipath peut réunir les chemins utilisables pour exposer un seul périphérique logique.

Le but est de gérer les chemins et leur disponibilité, pas de créer plusieurs systèmes de fichiers indépendants sur le même stockage.

## 11.3. Device Mapper Multipath

Dans les systèmes compatibles, `multipathd` et les outils associés permettent de gérer cette fonction.

Les commandes disponibles dépendent de la distribution et des paquets installés.

Pour inspecter l'état :

```bash
sudo multipath -ll
```

Pour voir les périphériques bloc :

```bash
lsblk
```

Pour examiner les mappages Device Mapper :

```bash
sudo dmsetup ls --tree
```

L'objectif est de relier :

- Le volume logique exposé par le SAN.
- Ses identifiants.
- Les chemins détectés.
- L'état de ces chemins.
- Le périphérique logique multipath utilisé par le système.

## 11.4. Le WWID et l'identité du stockage distant

Dans un environnement multipath, l'identité du volume doit être stable et différenciée de celle de chaque chemin d'accès.

Le WWID ou un identifiant équivalent fourni par le stockage peut permettre d'associer plusieurs chemins au même objet logique.

Ne considère pas les noms temporaires des chemins individuels comme l'identité durable du volume partagé.

Il faut aussi vérifier la configuration du stockage distant : deux périphériques peuvent avoir la même capacité sans être le même volume.

## 11.5. Erreur classique : utiliser chaque chemin séparément

Considérons deux chemins :

```text
/dev/sdb  ----\
               \
                >--- Même volume logique SAN
               /
/dev/sdc  ----/
```

Si les deux noms représentent réellement des chemins distincts vers le même volume, ce ne sont pas deux disques indépendants.

Créer des systèmes de fichiers sur chacun serait une erreur grave.

La bonne démarche consiste à vérifier le mappage multipath et à utiliser le périphérique logique prévu pour l'administration.

## 11.6. Symptômes de défaillance de chemin

Les symptômes possibles comprennent :

- Une hausse de latence.
- Des erreurs de temporisation.
- La disparition d'un chemin.
- Des réinitialisations de connexion.
- Des messages du pilote.
- Une modification de l'état de l'ensemble multipath.

Le diagnostic doit rapprocher :

```text
Journaux du noyau
        +
État multipath
        +
État des interfaces réseau ou HBA
        +
État des commutateurs
        +
État du contrôleur de stockage
        +
Mesures de latence
```

Un volume inaccessible ne signifie pas nécessairement que les données du SAN ont disparu. Une panne de chemin peut être en cause.

## 11.7. Discipline opérationnelle multipath

Avant de désactiver ou supprimer un chemin :

1. Confirme l'identité du volume.
2. Vérifie les chemins encore disponibles.
3. Vérifie l'état du multipath.
4. Confirme que la modification est autorisée.
5. Prépare une procédure de retour.
6. Effectue la modification contrôlée.
7. Observe les chemins restants.
8. Vérifie l'application.

Ne retire jamais un chemin simplement parce qu'il porte un nom inattendu ou parce qu'il a disparu d'une commande isolée.


# 12. Stockage réseau iSCSI et NVMe over Fabrics

## 12.1. Pourquoi utiliser un stockage distant ?

Le stockage distant permet à un serveur d'accéder à des volumes fournis par une infrastructure extérieure.

Il peut être utilisé pour :

- Le stockage centralisé.
- La mutualisation de la capacité.
- La gestion centralisée de la redondance.
- La mobilité des charges de travail.
- La séparation du calcul et du stockage.
- Certaines stratégies de haute disponibilité.

Mais le stockage distant introduit de nouvelles dépendances :

- Réseau.
- Authentification.
- Contrôleurs et chemins.
- Infrastructure de stockage.
- Configuration des sessions.
- Gestion des identifiants.
- Délais et erreurs de communication.

## 12.2. iSCSI : principe

iSCSI transporte des commandes SCSI sur un réseau IP.

Un initiateur, généralement le serveur Linux, se connecte à une cible qui expose un volume logique.

```text
              SERVEUR LINUX
             Initiateur iSCSI
                    |
                    v
                Réseau IP
                    |
                    v
                Cible iSCSI
                    |
                    v
            Volume logique distant
```

Une fois connecté, le volume peut apparaître comme un périphérique bloc.

Cela ne signifie pas qu'il est local au sens matériel. Sa disponibilité dépend toujours de la connectivité et du serveur de stockage.

## 12.3. Découverte iSCSI

Sur une machine disposant des outils `iscsiadm`, une découverte peut prendre la forme :

```bash
sudo iscsiadm -m discovery -t sendtargets -p <adresse-cible>
```

`<adresse-cible>` est un espace réservé à remplacer par l'adresse réellement fournie par l'administrateur du stockage.

Cette commande suppose que la cible autorise la découverte depuis la machine et que le réseau est configuré.

Avant de se connecter, vérifie :

- L'adresse et le port.
- L'identité de la cible.
- Les mécanismes d'authentification.
- Les autorisations.
- La configuration réseau.
- Les instructions de l'équipe de stockage.

Ne publie pas de secrets d'authentification dans des journaux ou des scripts accessibles aux utilisateurs non autorisés.

## 12.4. Sessions iSCSI

Les outils peuvent afficher les sessions et les périphériques associés.

Exemples de commandes d'observation :

```bash
sudo iscsiadm -m session
lsblk
sudo journalctl -k --since "30 minutes ago"
```

La configuration persistante et la reprise des sessions au démarrage dépendent des paramètres locaux, du paquet iSCSI utilisé et de la politique de l'environnement.

Une connexion iSCSI ne doit pas être considérée comme un montage de système de fichiers : elle fournit généralement un périphérique bloc sur lequel d'autres couches peuvent ensuite être construites.

## 12.5. Le danger des connexions multiples mal conçues

Un même volume peut être exposé par plusieurs chemins.

Il faut savoir si les chemins correspondent :

- À des volumes réellement différents.
- À des chemins redondants vers le même volume.
- À plusieurs sessions iSCSI qui doivent être gérées par multipath.

Ne crée pas plusieurs systèmes de fichiers indépendants sur des chemins qui donnent accès aux mêmes blocs.

La configuration doit être documentée par l'équipe responsable du stockage.

## 12.6. NVMe over Fabrics

NVMe over Fabrics permet d'accéder à des espaces de noms NVMe au travers d'une infrastructure de transport prise en charge.

Le transport peut dépendre de l'architecture et de la technologie employée.

L'administration comporte alors plusieurs couches :

```text
Application
    |
    v
Système de fichiers
    |
    v
Namespace NVMe distant
    |
    v
Transport NVMe-oF
    |
    v
Réseau et infrastructure
    |
    v
Contrôleur de stockage distant
```

Les commandes et les paramètres dépendent de la configuration du contrôleur, du transport et de la version des outils.

Pour un environnement de production, applique les procédures spécifiques à l'infrastructure plutôt que de supposer que toutes les connexions NVMe distantes fonctionnent comme un disque local.


# 13. Chiffrement avec LUKS et cryptsetup

## 13.1. Pourquoi chiffrer le stockage ?

Le chiffrement des données au repos peut réduire les risques liés à la perte, au vol ou à l'accès non autorisé aux supports physiques.

Il ne règle pas à lui seul tous les problèmes de sécurité.

Lorsque le volume est déverrouillé, les utilisateurs et processus possédant les permissions appropriées peuvent accéder aux données selon la politique d'accès du système.

Le chiffrement doit donc être associé :

- Aux permissions Linux.
- À la gestion des clés.
- À la protection de l'accès administrateur.
- À la sauvegarde des données.
- À la sécurité des applications.
- Aux procédures de démarrage et de récupération.

## 13.2. Architecture LUKS

LUKS est un format de gestion du chiffrement des périphériques blocs, couramment utilisé avec `cryptsetup` sur Linux.

```text
                Application
                    |
                    v
                Fichiers
                    |
                    v
                Système ext4
                    |
                    v
            /dev/mapper/cryptdata
                    |
                    v
               dm-crypt
                    |
                    v
                LUKS
                    |
                    v
              Disque chiffré
```

La couche déchiffrée fournit un périphérique bloc logique sur lequel on peut créer un système de fichiers ou construire une autre couche de stockage.

## 13.3. Préparer un périphérique de test

La procédure suivante utilise une partition de laboratoire qui ne contient aucune donnée à conserver.

Exemple :

```text
/dev/sdb1
```

Cette désignation doit être confirmée sur la machine réelle.

Avant de continuer :

```bash
lsblk -f
sudo blkid
findmnt
```

Vérifie également que le périphérique n'appartient pas à un ensemble RAID ou à un groupe LVM existant.

## 13.4. Initialiser LUKS

> **Attention : `luksFormat` initialise la configuration de chiffrement sur la cible et peut rendre les anciennes données inaccessibles. Ne l'exécute pas sur une partition existante sans une procédure de migration adaptée.**

Sur une partition de test explicitement réservée :

```bash
sudo cryptsetup luksFormat /dev/sdb1
```

L'outil demande normalement une confirmation et un secret de déverrouillage, selon la configuration.

Choisis un secret robuste et protège-le contre la divulgation.

Dans un environnement de production, l'algorithme, la configuration, les options de format et la méthode de gestion des clés doivent suivre la politique de sécurité de l'organisation.

## 13.5. Vérifier les métadonnées LUKS

```bash
sudo cryptsetup luksDump /dev/sdb1
```

Cette commande affiche des informations sur l'en-tête LUKS et les paramètres de la configuration.

Elle ne déverrouille pas automatiquement le volume.

Conserve la documentation nécessaire pour identifier le volume et gérer ses clés selon les règles de sécurité.

## 13.6. Ouvrir le volume chiffré

```bash
sudo cryptsetup open /dev/sdb1 cryptdata
```

Selon la configuration, un secret de déverrouillage sera demandé ou le mécanisme d'accès autorisé sera utilisé.

Le périphérique déchiffré apparaît généralement sous :

```text
/dev/mapper/cryptdata
```

Vérifie sa présence :

```bash
lsblk
sudo dmsetup ls --tree
```

Il faut distinguer la partition qui contient les données chiffrées du périphérique déchiffré exposé à Linux.

## 13.7. Créer un système de fichiers dans la couche déchiffrée

Sur le périphérique de laboratoire ouvert :

```bash
sudo mkfs.ext4 /dev/mapper/cryptdata
```

Cette commande crée ext4 au-dessus de la couche de chiffrement. Elle détruit un éventuel système de fichiers préexistant à cet emplacement logique.

Créer un point de montage :

```bash
sudo mkdir -p /data/secure
```

Monter le système de fichiers :

```bash
sudo mount /dev/mapper/cryptdata /data/secure
```

Vérifier :

```bash
findmnt /data/secure
df -hT /data/secure
```

L'architecture obtenue est :

```text
/dev/sdb1
   |
   v
  LUKS
   |
   v
cryptdata
   |
   v
  ext4
   |
   v
/data/secure
```

## 13.8. Deux UUID différents

Une source fréquente d'erreur est la confusion entre :

1. L'UUID du conteneur LUKS.
2. L'UUID du système de fichiers situé à l'intérieur du conteneur.

Pour examiner les deux niveaux :

```bash
sudo cryptsetup luksUUID /dev/sdb1
sudo blkid /dev/mapper/cryptdata
```

Ces UUID ne remplissent pas la même fonction.

Dans `/etc/crypttab`, on identifie le conteneur chiffré.

Dans `/etc/fstab`, on identifie généralement le système de fichiers déchiffré à monter.

## 13.9. Fermer le volume proprement

Avant de fermer le volume, le système de fichiers doit être démonté et ne plus être utilisé.

```bash
sudo umount /data/secure
```

Vérifie qu'il n'est plus monté :

```bash
findmnt /data/secure
```

Fermer ensuite le mappage :

```bash
sudo cryptsetup close cryptdata
```

Si un processus utilise encore le volume, l'opération peut échouer ou nécessiter des vérifications supplémentaires.

Ne force pas la fermeture d'un volume qui contient des écritures en cours sans avoir évalué les risques.

## 13.10. Montage persistant avec crypttab et fstab

Pour rendre le déverrouillage et le montage persistants, certaines distributions utilisent notamment :

- `/etc/crypttab` pour décrire les volumes chiffrés.
- `/etc/fstab` pour les systèmes de fichiers à monter.

L'exemple conceptuel suivant utilise un UUID LUKS fictif :

```text
cryptdata UUID=UUID_LUKS_REEL none luks
```

La ligne doit être adaptée à la politique de déverrouillage de la machine.

Pour le système de fichiers, une ligne conceptuelle peut ressembler à :

```fstab
UUID=UUID_FILESYSTEM_REEL /data/secure ext4 defaults 0 2
```

Les marqueurs doivent être remplacés par les véritables UUID.

Le comportement au démarrage dépend de la distribution, des options et des mécanismes de déverrouillage.

Ne suppose pas qu'un volume chiffré sera automatiquement accessible sans secret ou sans mécanisme de gestion des clés.

Une erreur de configuration peut empêcher le montage ou perturber le démarrage d'un service dépendant du volume.

## 13.11. Gestion experte des clés

Le chiffrement n'est utile que si les clés sont gérées de façon appropriée.

La procédure doit préciser :

- Qui peut déverrouiller le volume.
- Comment les secrets sont conservés.
- Comment une clé de récupération est protégée.
- Comment une révocation sera effectuée.
- Comment les clés sont renouvelées lorsque la politique l'exige.
- Comment une restauration se déroule si le serveur original est indisponible.
- Comment le déverrouillage fonctionne après un remplacement matériel.

Les informations nécessaires à la récupération doivent être conservées de manière indépendante et sécurisée.

Ne stocke pas la seule copie de la clé de déchiffrement sur le même support que les données qu'elle protège.

## 13.12. Chiffrement et sauvegardes

Une sauvegarde peut être chiffrée elle aussi, indépendamment du chiffrement du volume source.

Il faut définir où le chiffrement est appliqué :

```text
Données source
      |
      v
Chiffrement du volume
      |
      v
Application et fichiers accessibles
      |
      v
Sauvegarde
      |
      v
Chiffrement de la sauvegarde selon la politique
```

Le chiffrement du volume principal ne garantit pas que toutes les copies exportées soient protégées.

Inversement, le chiffrement d'une sauvegarde ne règle pas la gestion des permissions sur le système source.


# 14. Maintenance experte d'ext4, XFS et Btrfs

## 14.1. Identifier le système de fichiers avant d'agir

La commande :

```bash
findmnt -T /data
```

permet de repérer le système de fichiers qui porte le chemin.

La commande :

```bash
lsblk -f
```

fournit une autre vue de l'organisation du stockage.

Il faut identifier le type exact avant de sélectionner un outil de vérification ou de réparation.

Les commandes destinées à ext4 ne sont pas interchangeables avec celles destinées à XFS ou Btrfs.

## 14.2. ext4 : vérification et maintenance

Pour consulter la documentation :

```bash
man e2fsck
man tune2fs
man resize2fs
```

Pour examiner les informations d'un système de fichiers ext :

```bash
sudo tune2fs -l /dev/DEVICE
```

`/dev/DEVICE` est un marqueur à remplacer par la cible exacte.

Une vérification ext4 complète se réalise généralement sur un système de fichiers démonté.

Exemple sur un volume de laboratoire démonté :

```bash
sudo e2fsck -f /dev/DEVICE
```

Avant l'exécution, vérifie :

```bash
findmnt
lsblk -f
```

Il faut aussi tenir compte de la sauvegarde et de la nature des données.

Une réparation n'est pas un substitut au traitement d'une panne matérielle.

## 14.3. ext4 : réduire ou agrandir

L'extension ext4 peut généralement être effectuée en ligne dans les conditions compatibles.

La réduction nécessite normalement une procédure hors ligne.

L'ordre des opérations est essentiel :

```text
Réduction ext4
      |
      v
Réduire le système de fichiers
      |
      v
Vérifier le système de fichiers
      |
      v
Réduire la couche de stockage
```

Il faut calculer une taille correcte et vérifier que le système de fichiers peut tenir dans la nouvelle limite.

Ne réduis pas la couche bloc sous la taille nécessaire au système de fichiers.

## 14.4. XFS : maintenance adaptée

XFS fournit ses propres outils de diagnostic et de réparation.

Consulter les informations d'un montage :

```bash
sudo xfs_info /data
```

Examiner les options des outils :

```bash
man xfs_repair
man xfs_db
```

Pour une inspection non destructive des métadonnées dans un scénario compatible, `xfs_repair -n` peut être employé sur un système de fichiers démonté.

La procédure exacte doit correspondre au problème identifié.

La réparation classique XFS doit généralement être réalisée hors ligne.

**Ne transpose pas automatiquement les procédures ext4 à XFS. XFS ne prend pas en charge la réduction sur place de son système de fichiers.**

L'option de réparation qui efface ou reconstruit des métadonnées de journal doit être considérée comme une mesure exceptionnelle, et non comme la première action d'un dépannage.

Une telle opération peut entraîner la perte des métadonnées qui n'ont pas pu être récupérées autrement.

## 14.5. Btrfs : comprendre l'intégrité

Btrfs offre des fonctions telles que :

- Sous-volumes.
- Instantanés.
- Sommes de contrôle.
- Scrub.
- Gestion de plusieurs périphériques selon la configuration.

Afficher l'état de l'utilisation :

```bash
sudo btrfs filesystem usage /data
```

Afficher les périphériques Btrfs :

```bash
sudo btrfs filesystem show
```

Afficher les sous-volumes :

```bash
sudo btrfs subvolume list /data
```

## 14.6. Le scrub Btrfs

Un scrub parcourt les données et métadonnées pour vérifier les sommes de contrôle lorsque celles-ci sont disponibles.

Sur un système Btrfs dont le point de montage est connu :

```bash
sudo btrfs scrub start -Bd /data
```

Le scrub peut produire une charge d'entrée-sortie importante.

Son efficacité pour corriger une erreur dépend des possibilités de récupération et de la redondance disponible. La capacité de correction n'est pas la même dans toutes les configurations.

Après un scrub, examine le rapport et les statistiques pertinentes.

Le scrub n'est ni un remplacement de sauvegarde ni une garantie que toutes les erreurs possibles seront récupérables.

## 14.7. Pourquoi éviter `btrfs check --repair` par réflexe

Les outils de vérification Btrfs ont des objectifs et des risques différents.

Une opération de réparation des métadonnées doit être abordée avec une extrême prudence et conformément à la documentation du projet pour le cas précis.

Avant une intervention risquée :

1. Identifie le problème.
2. Consulte les journaux.
3. Vérifie la santé du stockage.
4. Préserve les données récupérables.
5. Évalue une image ou une copie de récupération lorsque c'est possible.
6. Utilise les outils correspondant au diagnostic.

Ne lance pas automatiquement `btrfs check --repair` simplement parce qu'un montage échoue.

## 14.8. Comparaison opérationnelle

| Besoin | ext4 | XFS | Btrfs |
|---|---|---|---|
| Informations générales | `tune2fs -l` | `xfs_info` | `btrfs filesystem usage` |
| Vérification spécialisée | `e2fsck` | `xfs_repair` selon le scénario | `btrfs check` selon le cas |
| Contrôle d'intégrité parcourant les données | Autres outils et stratégies adaptées | Outils et procédures adaptés | `btrfs scrub` |
| Extension | Possible sous conditions | Possible sous conditions | Possible sous conditions |
| Réduction sur place | Possible hors ligne selon la procédure | Non | Possible selon le modèle et la configuration |
| Instantanés intégrés au système de fichiers | Non | Non | Oui |
| Gestion de plusieurs périphériques | Généralement via d'autres couches | Généralement via d'autres couches | Prise en charge native selon le mode choisi |

## 14.9. Après une erreur de système de fichiers

Il faut consigner :

```text
Volume concerné
Type de système de fichiers
Heure de l'incident
Messages du noyau
État du matériel
État des couches inférieures
Opérations effectuées avant l'erreur
Sauvegarde disponible
Résultat de la vérification
Résultat de la réparation
Test de lecture et d'écriture
Validation applicative
```

Ce dossier permet de distinguer la récupération immédiate du travail de prévention.


# 15. Quotas avancés et gestion multi-tenant

## 15.1. Pourquoi les quotas deviennent importants à grande échelle

Dans une infrastructure partagée, les utilisateurs, équipes ou applications peuvent consommer la même capacité physique.

Les quotas évitent qu'un seul tenant consomme toutes les ressources qui lui sont attribuées, sous réserve que les limites configurées couvrent correctement le besoin.

Il faut distinguer :

- Les quotas utilisateurs.
- Les quotas de groupes.
- Les quotas de projet ou de répertoires selon le système de fichiers.
- Les limites logiques de volumes.
- Les limites physiques d'un pool.
- Les limites imposées par les plateformes de stockage.

## 15.2. Les quotas ne sont pas une capacité physique

Supposons :

```text
Volume physique : 1 To
Tenant A : limite de 300 Go
Tenant B : limite de 300 Go
Tenant C : limite de 300 Go
```

La somme des limites représente 900 Go, mais il reste à prendre en compte la marge opérationnelle, les métadonnées, la croissance et les éventuelles allocations supplémentaires.

Si les limites cumulées dépassent la capacité physique, elles constituent une politique d'allocation logique et non une garantie que chaque tenant pourra consommer sa totalité en même temps.

Dans le cas d'un stockage à allocation fine, la différence entre capacité virtuelle et capacité physique devient encore plus importante.

## 15.3. Quotas XFS par projet

XFS prend en charge différents modes de quotas, selon la version et la configuration du système.

Les project quotas sont particulièrement utiles pour contrôler l'espace consommé par certains ensembles de répertoires.

Les outils disponibles peuvent comprendre `xfs_quota`.

Pour consulter la documentation :

```bash
man xfs_quota
```

L'activation des quotas de projet nécessite une configuration adaptée au système de fichiers et au montage.

Il faut notamment définir correctement la relation entre les répertoires, les identifiants de projet et les règles de quota.

Ne considère pas la simple installation des outils comme une activation des limites.

## 15.4. Concevoir une politique multi-tenant

Une politique robuste précise :

```text
Identité du tenant
Volume associé
Limite logique
Limite physique
Limite d'inodes
Seuil d'alerte
Rétention des données
Propriétaire opérationnel
Méthode d'extension
Procédure de sauvegarde
Procédure de suppression
```

Ces informations doivent correspondre à la configuration réellement appliquée.

Une limite affichée dans un document ne protège rien si elle n'est pas mise en œuvre par le mécanisme de quotas adéquat.

## 15.5. Quotas, permissions et isolation

Les quotas ne remplacent pas les permissions.

Un compte peut disposer d'un quota important sans avoir le droit d'écrire dans un répertoire.

De même, un compte peut disposer des permissions nécessaires, mais atteindre sa limite de consommation.

Dans une architecture multi-tenant, il faut combiner :

- Isolation des accès.
- Contrôle des permissions.
- Quotas et limites de capacité.
- Surveillance.
- Sauvegardes.
- Gestion des identités.
- Procédures de récupération.


# 16. Montages systemd et dépendances des services

## 16.1. Les montages sont aussi des dépendances

Un service peut nécessiter un volume de données pour démarrer.

Si le montage échoue, le service peut :

- Échouer au démarrage.
- Se lancer sans ses données.
- Créer des fichiers au mauvais emplacement.
- Être incapable d'écrire.
- Produire des erreurs applicatives.

Le montage n'est donc pas seulement une question de stockage : il fait partie de l'architecture du service.

## 16.2. Consulter l'état des montages

Pour identifier le montage d'un chemin :

```bash
findmnt -T /srv/projects
```

Pour examiner les unités de montage systemd disponibles :

```bash
systemctl list-units --type=mount
```

Pour consulter les unités automount :

```bash
systemctl list-units --type=automount
```

Pour examiner les journaux associés au démarrage :

```bash
sudo journalctl -b
```

La configuration peut provenir de `/etc/fstab`, d'unités systemd explicites ou d'autres mécanismes gérés par le système.

## 16.3. Montages optionnels et montages indispensables

Il faut distinguer deux catégories :

### Montage indispensable

Une base de données ne doit pas démarrer si son répertoire de données est indisponible.

Dans ce cas, les dépendances et vérifications doivent empêcher un fonctionnement incorrect.

### Montage optionnel

Un répertoire d'archives secondaires peut être absent sans empêcher le démarrage de tous les services.

Dans ce cas, une stratégie de montage non bloquant peut être appropriée, à condition que les applications ne dépendent pas de ce volume.

Le choix doit être explicite. Une option comme `nofail` ne doit pas être utilisée pour masquer une dépendance critique.

## 16.4. Prévenir l'écriture sur le volume parent

Supposons que l'application écrive dans :

```text
/srv/projects
```

Si le volume attendu n'est pas monté, le répertoire correspondant peut rester présent sur le système de fichiers parent.

Une application pourrait alors écrire ses fichiers à cet endroit.

```text
Montage correct :

Volume projets
      |
      v
/srv/projects
      |
      v
Données du projet


Montage absent :

Système parent
      |
      v
Répertoire /srv/projects
      |
      v
Nouvelles écritures au mauvais endroit
```

Ce deuxième scénario peut consommer l'espace du système principal et compliquer la récupération après le retour du volume.

Pour l'éviter, il faut configurer correctement les dépendances des services, contrôler le montage avant le démarrage et s'assurer que les chemins utilisés sont ceux prévus.


# 17. Sauvegarde, cohérence applicative et reprise après sinistre

## 17.1. Trois objectifs à distinguer

Les systèmes de stockage répondent à plusieurs besoins différents :

| Objectif | Question |
|---|---|
| Disponibilité | Le service continue-t-il malgré certaines pannes ? |
| Intégrité | Les données sont-elles cohérentes et détectables en cas de corruption ? |
| Récupération | Peut-on restaurer les données après une perte ou une erreur ? |

Le RAID peut contribuer à la disponibilité.

Les sommes de contrôle, vérifications et mécanismes de cohérence contribuent à détecter certains problèmes d'intégrité.

Les sauvegardes et procédures de restauration contribuent à la récupération.

Aucun mécanisme ne remplace complètement les autres.

## 17.2. Objectif de point de récupération

Le RPO, ou *Recovery Point Objective*, représente la perte de données maximale acceptable, exprimée en temps ou en quantité de données selon la politique.

Exemple :

```text
RPO de 1 heure
```

Cela signifie que l'organisation accepte, dans les conditions définies, de perdre au maximum environ une heure de modifications de données.

Cet objectif détermine notamment les fréquences de sauvegarde ou de réplication nécessaires.

Une copie quotidienne ne satisfait pas automatiquement un objectif de récupération d'une heure.

## 17.3. Objectif de temps de récupération

Le RTO, ou *Recovery Time Objective*, correspond au délai cible pour rétablir le service après une interruption.

Exemple :

```text
RTO de 4 heures
```

Cet objectif comprend davantage que la copie de fichiers :

- Détection de l'incident.
- Préparation de l'environnement.
- Récupération du stockage.
- Restauration des données.
- Reconfiguration des accès.
- Validation applicative.
- Retour au fonctionnement.

Une stratégie de sauvegarde ne peut être considérée comme adaptée que si elle permet d'atteindre les objectifs définis dans des conditions testées.

## 17.4. Sauvegarde de fichiers et cohérence des applications

Une copie de fichiers peut convenir à de nombreux usages.

Mais une application active peut modifier plusieurs fichiers au cours d'une transaction.

Si la sauvegarde capture ces fichiers à des moments incompatibles, elle peut contenir un état incohérent.

Il faut donc choisir un mécanisme de cohérence adapté :

- Mode de sauvegarde natif de l'application.
- Gel contrôlé des écritures si la plateforme le permet.
- Instantané coordonné avec les services.
- Copie à partir d'un état stable.
- Vérification après restauration.

## 17.5. Exemple avec rsync

Examiner les systèmes de fichiers :

```bash
findmnt /srv/projects
findmnt /backup
```

Confirmer que la destination de sauvegarde est réellement montée :

```bash
df -hT /srv/projects /backup
```

Effectuer une simulation :

```bash
sudo rsync -aHAXn --numeric-ids \
  /srv/projects/ \
  /backup/projects/
```

Examiner la sortie.

Si les chemins et les effets sont conformes à la politique, effectuer la copie :

```bash
sudo rsync -aHAX --numeric-ids \
  /srv/projects/ \
  /backup/projects/
```

Ces commandes sont adaptées aux copies de fichiers dans les conditions prises en charge par le système. Elles ne garantissent pas à elles seules la cohérence d'une base de données en cours d'utilisation.

## 17.6. Ne pas confondre synchronisation et rétention

Une synchronisation peut reproduire les modifications et, si elle est configurée pour le faire, les suppressions.

Cela peut être souhaitable pour un miroir de travail, mais ne constitue pas nécessairement une sauvegarde historique.

Une stratégie de sauvegarde doit préciser :

- Combien de versions sont conservées.
- Combien de temps elles sont conservées.
- Comment les suppressions sont traitées.
- Comment les copies sont protégées.
- Comment une version ancienne est restaurée.

## 17.7. Protection contre la destruction logique

Dans une approche de défense en profondeur, les copies peuvent être conservées :

- Sur une infrastructure séparée.
- Sous des identifiants distincts.
- Avec des droits de suppression limités.
- Avec une rétention contrôlée.
- Dans un état immuable lorsque la solution le prend en charge.
- Hors ligne, lorsque cela correspond à la stratégie choisie.

L'objectif est de réduire le risque qu'un incident touche simultanément les données de production et toutes les sauvegardes.

## 17.8. La restauration doit être testée

Une procédure de restauration doit répondre aux questions suivantes :

```text
Quelles données sont restaurées ?
Depuis quelle copie ?
Avec quels droits ?
Avec quelle version de l'application ?
Dans quel ordre ?
Comment vérifier l'intégrité ?
Comment confirmer le fonctionnement du service ?
Comment éviter d'écraser des données plus récentes ?
Comment revenir en arrière si la restauration échoue ?
```

Un test de restauration doit être documenté avec un résultat vérifiable.


# 18. Sécurité avancée du stockage

## 18.1. Réduire les privilèges

La gestion du stockage requiert souvent des privilèges élevés.

Mais ces droits ne doivent être accordés qu'aux personnes et outils qui en ont besoin.

Un compte chargé de consulter la capacité n'a pas nécessairement besoin du droit de reformater un disque.

Une équipe chargée des sauvegardes n'a pas nécessairement besoin de modifier toutes les partitions du serveur.

La séparation des responsabilités permet de réduire les erreurs et certains abus.

## 18.2. Protéger les métadonnées

Les données ne sont pas les seuls éléments sensibles.

Les métadonnées peuvent révéler :

- La structure des volumes.
- Les noms des systèmes de fichiers.
- Des identifiants de matériel.
- Des chemins de stockage.
- Des informations sur la topologie.
- Des indices sur les applications et les données.

Les configurations, rapports et scripts qui exposent ces informations doivent être protégés selon les risques de l'environnement.

## 18.3. Chiffrement et permissions

Le chiffrement protège surtout les données contre certains scénarios d'accès aux supports physiques ou aux volumes fermés.

Les permissions Linux contrôlent les accès aux données accessibles dans le système déverrouillé.

Les deux mécanismes sont complémentaires :

```text
Sécurité des données
        |
        +--------------------+
        |                    |
        v                    v
Chiffrement au repos    Contrôle d'accès
        |                    |
        v                    v
Protection du support   Permissions et identités
```

Une architecture sécurisée doit aussi protéger les clés, les accès privilégiés et les sauvegardes.

## 18.4. Effacement et retrait de supports

L'effacement d'un disque ne se résume pas toujours à supprimer les fichiers ou à formater une partition.

Selon le support, l'environnement et les exigences réglementaires, une stratégie d'effacement peut employer des mécanismes différents.

Les SSD, les supports virtuels et les périphériques gérés par un contrôleur peuvent se comporter différemment d'un disque magnétique classique.

La méthode doit être adaptée :

- Au support exact.
- Aux risques de récupération.
- Au chiffrement déjà en place.
- Au mode d'hébergement.
- Aux exigences de l'organisation.
- À la documentation du fabricant.

Ne considère pas une simple suppression de fichiers comme une garantie d'effacement irréversible des données.

## 18.5. Journalisation des opérations privilégiées

Les opérations importantes doivent être traçables.

Il faut pouvoir déterminer :

- Quel compte a exécuté l'opération.
- À quelle heure.
- Sur quel périphérique.
- Dans quel but.
- Avec quel résultat.
- Quelle validation a été effectuée.

La journalisation doit être cohérente avec la politique de sécurité et ne pas exposer les secrets de chiffrement.


# 19. Automatisation et observabilité

## 19.1. Pourquoi automatiser ?

L'automatisation permet de détecter des anomalies et de réduire les tâches manuelles répétitives.

Elle peut notamment servir à :

- Collecter les capacités.
- Surveiller les inodes.
- Détecter les volumes approchant d'une limite.
- Surveiller certains pools LVM.
- Détecter un RAID dégradé.
- Recueillir les erreurs du noyau.
- Produire un rapport périodique.

Mais l'automatisation doit rester explicable, contrôlée et résistante aux erreurs.

## 19.2. Commencer par des contrôles en lecture seule

Une première étape consiste à regrouper les commandes d'observation dans un rapport.

Exemple de script :

```bash
#!/usr/bin/env bash

set -uo pipefail

echo "======================================"
echo "RAPPORT DE STOCKAGE LINUX"
echo "Date : $(date -Is)"
echo "Hôte : $(hostname)"
echo "======================================"

echo
echo "=== Périphériques bloc ==="
lsblk -o NAME,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINTS

echo
echo "=== Occupation des systèmes de fichiers ==="
df -hT

echo
echo "=== Inodes ==="
df -i

echo
echo "=== Montages ==="
findmnt -o SOURCE,TARGET,FSTYPE,OPTIONS

echo
echo "=== LVM : volumes physiques ==="
if command -v pvs >/dev/null 2>&1; then
    sudo pvs
else
    echo "Outil pvs indisponible."
fi

echo
echo "=== LVM : groupes de volumes ==="
if command -v vgs >/dev/null 2>&1; then
    sudo vgs
else
    echo "Outil vgs indisponible."
fi

echo
echo "=== LVM : volumes logiques ==="
if command -v lvs >/dev/null 2>&1; then
    sudo lvs -a -o+devices
else
    echo "Outil lvs indisponible."
fi

echo
echo "=== RAID logiciel ==="
if [ -r /proc/mdstat ]; then
    cat /proc/mdstat
else
    echo "État RAID indisponible."
fi

echo
echo "=== Erreurs et avertissements récents du noyau ==="
sudo journalctl -k -p warning --since "1 hour ago" --no-pager

echo
echo "Fin du rapport."
```

Le script regroupe plusieurs commandes utiles. Il peut demander une authentification `sudo` en fonction de la configuration.

Il ne modifie pas intentionnellement le stockage.

Il est toutefois nécessaire de tester le script sur la distribution ciblée et de vérifier que les commandes disponibles correspondent à l'environnement.

## 19.3. Ajouter une détection d'occupation

Une alerte simple peut être construite autour d'un seuil défini.

Exemple :

```bash
df -PTh
```

Le format `-P` contribue à stabiliser l'affichage pour l'analyse textuelle.

Un script de production devrait néanmoins traiter correctement :

- Les points de montage contenant certains caractères.
- Les systèmes de fichiers temporaires.
- Les volumes dont la capacité n'est pas comparable.
- Les erreurs de collecte.
- Les espaces de noms de conteneurs.
- Les volumes virtuels.
- Les seuils propres à chaque service.

Il faut éviter de déclencher une action destructive à partir d'une seule mesure ou d'une analyse de texte fragile.

## 19.4. Surveiller les pools LVM

Pour un pool fin :

```bash
sudo lvs -a -o+data_percent,metadata_percent
```

Les champs disponibles dépendent de la version installée.

Le système de supervision doit être capable d'identifier :

- Le pool concerné.
- L'évolution de la consommation.
- Les limites physiques.
- Le taux d'occupation des métadonnées.
- Le temps restant avant saturation, si une estimation suffisamment fiable est possible.

## 19.5. Les seuils ne sont pas universels

Un volume d'archives froides n'a pas la même criticité qu'un volume de base de données.

Une politique illustrative peut être :

```text
Moins de 70 % : situation nominale
70 à 85 %     : observation renforcée
85 à 95 %     : action préventive
Plus de 95 %  : intervention prioritaire
100 %         : incident de capacité
```

Ces valeurs ne doivent pas être appliquées aveuglément.

Le seuil devrait tenir compte :

- Du rythme de croissance.
- Du temps nécessaire pour augmenter la capacité.
- Du type d'application.
- Des marges nécessaires aux opérations internes.
- Des contraintes de maintenance.
- Des risques liés aux fichiers et aux métadonnées.

## 19.6. Observabilité multicouche

Une supervision experte rassemble plusieurs sources :

```text
Capacité des systèmes de fichiers
              |
              v
       Volumes logiques
              |
              v
       Groupes LVM et pools
              |
              v
          RAID/multipath
              |
              v
       Disques et contrôleurs
              |
              v
           Réseau SAN
              |
              v
           Application
```

La supervision doit aussi mesurer les résultats visibles par l'application : temps de réponse, erreurs, temps d'attente et disponibilité.

Une couche inférieure qui semble saine ne garantit pas que toute la chaîne soit performante.


# 20. Procédures de réponse aux incidents

## 20.1. Méthode commune aux incidents de stockage

La méthode suivante doit être appliquée avant toute intervention risquée.

```text
             INCIDENT
                 |
                 v
      1. Protéger les données
                 |
                 v
      2. Collecter les observations
                 |
                 v
      3. Identifier la couche touchée
                 |
                 v
      4. Évaluer l'impact
                 |
                 v
      5. Définir l'action autorisée
                 |
                 v
      6. Exécuter sous contrôle
                 |
                 v
      7. Vérifier le résultat
                 |
                 v
      8. Documenter et prévenir
```

Ne confonds pas la rapidité d'exécution avec la qualité d'un dépannage. Une action rapide mais mal ciblée peut aggraver l'incident.


## 20.2. Incident A — Le volume est plein

### Symptômes

- L'application ne peut plus écrire.
- Des erreurs « No space left on device » apparaissent.
- Les journaux augmentent rapidement.
- Certains services échouent.

### Étape 1 : confirmer la capacité

```bash
df -hT
```

### Étape 2 : vérifier les inodes

```bash
df -i
```

### Étape 3 : identifier le chemin réellement concerné

```bash
findmnt -T /chemin/impacte
```

### Étape 4 : trouver les principaux consommateurs

```bash
sudo du -xhd1 /chemin/impacte 2>/dev/null | sort -h
```

### Étape 5 : vérifier les fichiers supprimés encore ouverts

Si `lsof` est disponible :

```bash
sudo lsof +L1
```

### Étape 6 : vérifier le stockage inférieur

Si le volume repose sur LVM :

```bash
sudo lvs
sudo vgs
```

Si l'espace libre LVM est insuffisant, la capacité ne peut pas être augmentée simplement en agrandissant le système de fichiers.

### Décision

Selon la cause, il peut être approprié de :

- Réduire une croissance anormale.
- Déplacer des archives.
- Corriger la rotation des journaux.
- Restaurer une configuration d'application correcte.
- Augmenter la capacité.
- Traiter un problème de fichiers supprimés encore ouverts.

### Vérification finale

Après l'intervention :

```bash
df -hT
df -i
```

Contrôle également l'état de l'application et sa capacité à effectuer les opérations attendues.


## 20.3. Incident B — Le volume est lent

### Symptômes

- L'application répond lentement.
- Les fichiers restent accessibles.
- Le volume n'est pas plein.
- La latence semble avoir augmenté.

### Étape 1 : observer la charge

```bash
iostat -xz 1 10
```

### Étape 2 : observer les processus

```bash
pidstat -d 1 10
```

### Étape 3 : consulter les journaux

```bash
sudo journalctl -k --since "30 minutes ago"
```

### Étape 4 : examiner les couches

```bash
lsblk
sudo pvs
sudo vgs
sudo lvs -a -o+devices
cat /proc/mdstat
```

### Étape 5 : vérifier l'environnement distant si nécessaire

Pour un stockage SAN, examiner le multipath, les liens réseau, les contrôleurs et les statistiques de l'infrastructure.

### Décision

Ne lance pas un benchmark intensif sur le stockage de production comme première action. Cela peut augmenter la charge et perturber davantage les applications.

Commence par identifier la charge réelle et la période de l'incident.


## 20.4. Incident C — RAID dégradé

### Étape 1 : observer l'ensemble

```bash
cat /proc/mdstat
sudo mdadm --detail --scan
```

### Étape 2 : consulter les journaux

```bash
sudo journalctl -k --since "1 hour ago"
```

### Étape 3 : identifier les composants

```bash
lsblk -o NAME,MODEL,SERIAL,SIZE,TYPE,MOUNTPOINTS
```

### Étape 4 : vérifier les chemins d'accès

Si le stockage utilise multipath, examine les chemins et l'identité du stockage avant de considérer un disque comme défaillant.

### Étape 5 : suivre la procédure de remplacement

La réparation dépend du niveau RAID et de la topologie réelle.

### Étape 6 : surveiller la reconstruction

```bash
watch cat /proc/mdstat
```

### Étape 7 : valider l'état final

```bash
cat /proc/mdstat
sudo mdadm --detail /dev/md0
```

La procédure doit préserver autant que possible les données accessibles et éviter de retirer le mauvais composant.


## 20.5. Incident D — Montage absent après un redémarrage

### Étape 1 : vérifier les périphériques

```bash
lsblk -f
```

### Étape 2 : vérifier les montages actifs

```bash
findmnt
```

### Étape 3 : examiner les déclarations

```bash
sudo findmnt --verify --verbose
```

### Étape 4 : consulter les journaux du démarrage

```bash
sudo journalctl -b
```

### Étape 5 : vérifier les UUID et les couches sous-jacentes

Pour LVM :

```bash
sudo pvs
sudo vgs
sudo lvs
```

Pour un volume chiffré, vérifier également que la couche de déchiffrement est disponible.

### Étape 6 : tester la configuration après analyse

Une tentative de montage peut être effectuée lorsque la cause est comprise et que l'opération est sûre.

Ne modifie pas `/etc/fstab` au hasard pour faire disparaître une erreur de démarrage.


## 20.6. Incident E — LVM ne peut plus allouer d'espace

### Symptômes

- L'extension d'un volume logique échoue.
- Le groupe manque d'espace libre.
- Un pool fin approche de sa limite.
- Certains volumes disposent encore d'espace logique, mais leur couche physique est saturée.

### Étape 1 : examiner le groupe

```bash
sudo vgs -o vg_name,vg_size,vg_free
```

### Étape 2 : examiner les volumes

```bash
sudo lvs -a -o+devices
```

### Étape 3 : pour les pools fins, examiner les pourcentages

```bash
sudo lvs -a -o+data_percent,metadata_percent
```

### Étape 4 : identifier les options possibles

- Libérer de l'espace.
- Ajouter un périphérique compatible.
- Déplacer certains extents si l'architecture le permet.
- Agrandir le groupe.
- Redimensionner les allocations logiques après analyse.
- Réexaminer la politique de surallocation.

### Étape 5 : vérifier après la modification

Ne considère pas le problème résolu tant que la capacité physique, les métadonnées et le comportement des applications sont contrôlés.


## 20.7. Incident F — Erreurs de système de fichiers

### Étape 1 : arrêter les opérations risquées

Évite d'accumuler des tentatives de réparation sans diagnostic.

### Étape 2 : confirmer le type de système de fichiers

```bash
lsblk -f
findmnt
```

### Étape 3 : examiner les messages

```bash
sudo journalctl -k --since "1 hour ago"
```

### Étape 4 : contrôler les couches inférieures

Vérifie l'état matériel, RAID, multipath, LVM et les autres couches impliquées.

### Étape 5 : préserver les données récupérables

Si les données sont critiques, privilégie une stratégie de sauvegarde ou de copie de récupération adaptée à l'état du stockage.

### Étape 6 : choisir l'outil correspondant

- ext4 : outils `e2fsck` et documentation associée.
- XFS : outils `xfs_repair` et documentation associée.
- Btrfs : outils de diagnostic Btrfs et procédure appropriée.

### Étape 7 : vérifier la récupération

Le succès d'une commande ne suffit pas. Vérifie le montage, l'intégrité attendue et le fonctionnement applicatif.


# 21. Laboratoires pratiques avancés

> Les laboratoires de cette section doivent être réalisés sur une machine virtuelle dédiée ou des périphériques isolés réservés aux exercices. Les commandes qui modifient des métadonnées doivent être exécutées uniquement après vérification de la cible.

## Laboratoire 1 — Cartographier toute la chaîne de stockage

### Objectif

Identifier les dépendances entre le périphérique bloc, les éventuelles couches intermédiaires et le système de fichiers.

### Étape 1 : inventaire général

```bash
lsblk -o NAME,PATH,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINTS
```

### Étape 2 : montages

```bash
findmnt -o SOURCE,TARGET,FSTYPE,OPTIONS
```

### Étape 3 : LVM

```bash
sudo pvs -o+pv_used,pv_free
sudo vgs -o+vg_size,vg_free
sudo lvs -a -o+devices
```

### Étape 4 : Device Mapper

```bash
sudo dmsetup ls --tree
```

### Étape 5 : RAID

```bash
cat /proc/mdstat
sudo mdadm --detail --scan
```

### Travail demandé

Dessine l'architecture réelle d'un chemin important du système.

Le schéma doit indiquer :

- Les périphériques utilisés.
- Les éventuelles partitions.
- LVM, si présent.
- RAID ou multipath, si présent.
- Le système de fichiers.
- Le point de montage.
- Les services qui dépendent de ce stockage.

### Critère de validation

Tu dois pouvoir déterminer quels services pourraient être affectés par la perte d'un composant.


## Laboratoire 2 — Mesurer les performances sans écrire sur un périphérique brut

### Objectif

Comparer deux profils de charge en environnement de test.

### Prérequis

- Un volume de test monté sur `/data`.
- Un espace libre suffisant.
- `fio` installé.
- Une charge non critique.

### Étape 1 : vérifier l'espace

```bash
findmnt /data
df -hT /data
```

### Étape 2 : créer le répertoire réservé

```bash
mkdir -p /data/fio-lab
```

### Étape 3 : mesurer les lectures séquentielles

```bash
fio \
  --name=seqread \
  --filename=/data/fio-lab/seqread.bin \
  --size=512M \
  --rw=read \
  --bs=1M \
  --iodepth=4 \
  --numjobs=1 \
  --runtime=20 \
  --time_based \
  --group_reporting
```

### Étape 4 : mesurer les lectures aléatoires

```bash
fio \
  --name=randread \
  --filename=/data/fio-lab/randread.bin \
  --size=512M \
  --rw=randread \
  --bs=4k \
  --iodepth=16 \
  --numjobs=2 \
  --runtime=20 \
  --time_based \
  --group_reporting
```

### Étape 5 : surveiller les périphériques durant les mesures

Dans un autre terminal :

```bash
iostat -xz 1 10
```

### Étape 6 : interpréter

Compare :

- Le débit.
- Les IOPS.
- La latence.
- Les effets de la concurrence.
- L'évolution de la file d'attente.

### Critère de validation

Explique pourquoi les deux profils de charge peuvent produire des résultats très différents sur le même volume.


## Laboratoire 3 — Examiner un pool LVM à allocation fine

### Objectif

Comprendre la distinction entre capacité virtuelle et espace physique réellement consommé.

### Prérequis

Un groupe LVM de laboratoire disposant de suffisamment d'espace libre.

### Étape 1 : observer le groupe

```bash
sudo vgs
```

### Étape 2 : créer un pool fin de test

Sur un environnement isolé, avec une capacité disponible appropriée :

```bash
sudo lvcreate --type thin-pool \
  -L 10G \
  --poolmetadatasize 1G \
  -n tp-lab vgdata
```

Vérifie la syntaxe et les contraintes de la version LVM installée.

### Étape 3 : créer un volume virtuel

```bash
sudo lvcreate --type thin \
  -V 20G \
  -n lv-thin-lab \
  vgdata/tp-lab
```

### Étape 4 : observer les tailles

```bash
sudo lvs -a -o+data_percent,metadata_percent
sudo vgs
```

### Travail demandé

Explique :

1. Pourquoi la taille virtuelle dépasse la taille physique du pool.
2. Pourquoi cela ne signifie pas que 20 GiB ont déjà été consommés.
3. Quels problèmes peuvent survenir si le pool est plein.
4. Pourquoi les métadonnées doivent elles aussi être surveillées.

### Critère de validation

Tu dois être capable de différencier la capacité virtuelle visible du volume et l'espace physique disponible pour les nouvelles écritures.


## Laboratoire 4 — Créer un volume LUKS de test

### Objectif

Comprendre la différence entre le périphérique chiffré, le périphérique déchiffré et le système de fichiers.

### Prérequis

Une partition de test vide, identifiée sans ambiguïté.

### Étape 1 : confirmer la cible

```bash
lsblk -f
sudo blkid
```

### Étape 2 : initialiser LUKS

Sur le périphérique de laboratoire exclusivement :

```bash
sudo cryptsetup luksFormat /dev/sdb1
```

Cette opération peut rendre le contenu antérieur inaccessible.

### Étape 3 : ouvrir le volume

```bash
sudo cryptsetup open /dev/sdb1 crypt-lab
```

### Étape 4 : créer un système de fichiers

```bash
sudo mkfs.ext4 /dev/mapper/crypt-lab
```

### Étape 5 : monter

```bash
sudo mkdir -p /data/crypt-lab
sudo mount /dev/mapper/crypt-lab /data/crypt-lab
```

### Étape 6 : contrôler les deux UUID

```bash
sudo cryptsetup luksUUID /dev/sdb1
sudo blkid /dev/mapper/crypt-lab
```

### Étape 7 : démonter et fermer

```bash
sudo umount /data/crypt-lab
sudo cryptsetup close crypt-lab
```

### Critère de validation

Tu dois pouvoir expliquer pourquoi l'UUID LUKS et l'UUID ext4 désignent deux couches différentes.


## Laboratoire 5 — Construire une procédure de diagnostic

### Objectif

Rédiger un runbook pour un problème de latence.

### Situation

Une application ralentit depuis quelques minutes. Le volume contient encore de l'espace libre.

### Collecte initiale

```bash
df -hT
df -i
iostat -xz 1 10
pidstat -d 1 10
sudo journalctl -k --since "30 minutes ago"
```

### Travail demandé

Construis une fiche de diagnostic :

```text
Heure de début :
Application concernée :
Volume concerné :
Système de fichiers :
Occupation :
Inodes :
Débit observé :
Latence observée :
Activité des processus :
Événements du noyau :
Couche suspecte :
Hypothèse :
Vérification prévue :
Résultat :
Action :
Validation finale :
```

### Critère de validation

La conclusion doit reposer sur des observations et séparer les faits des hypothèses.


## Laboratoire 6 — Vérifier une sauvegarde

### Objectif

Démontrer qu'une copie permet une récupération.

### Prérequis

Un répertoire de test et une destination de sauvegarde appropriée.

### Étape 1 : créer des données de test

```bash
mkdir -p /data/backup-lab
printf 'donnee-de-test\n' > /data/backup-lab/fichier.txt
```

### Étape 2 : vérifier la destination

```bash
findmnt /backup
df -hT /backup
```

Ne poursuis pas si le point de montage n'est pas la destination attendue.

### Étape 3 : simuler la copie

```bash
rsync -avn /data/backup-lab/ /backup/backup-lab/
```

### Étape 4 : effectuer la copie validée

```bash
rsync -av /data/backup-lab/ /backup/backup-lab/
```

### Étape 5 : restaurer dans un emplacement distinct

```bash
mkdir -p /restore-test/backup-lab
rsync -av /backup/backup-lab/ /restore-test/backup-lab/
```

### Étape 6 : vérifier le contenu

```bash
cat /restore-test/backup-lab/fichier.txt
```

On peut aussi comparer les sommes de contrôle :

```bash
sha256sum \
  /data/backup-lab/fichier.txt \
  /restore-test/backup-lab/fichier.txt
```

### Critère de validation

La restauration doit produire un fichier dont le contenu et la somme de contrôle correspondent à la source.

Ce laboratoire valide une copie simple de fichier. Pour une base de données ou une application complexe, il faut ajouter les mécanismes de cohérence appropriés.


# 22. Exercices experts

Essaie de répondre avant de consulter les corrections.

## Exercice 1 — Capacité ou performance ?

Un volume présente 70 % d'occupation. Pourtant, l'application qui l'utilise a une latence élevée.

Explique pourquoi l'espace libre ne permet pas de conclure que le stockage fonctionne correctement.

## Exercice 2 — Identification

Pourquoi un UUID de système de fichiers, un PARTUUID et un WWID ne désignent-ils pas nécessairement le même objet ?

Donne un cas d'utilisation pour chacun.

## Exercice 3 — Pool fin

Un pool LVM dispose de 100 GiB physiques, mais ses volumes logiques présentent ensemble 250 GiB de capacité virtuelle.

Est-ce nécessairement une erreur ?

Quels risques faut-il surveiller ?

## Exercice 4 — Déplacement LVM

Un administrateur souhaite retirer un périphérique physique du groupe LVM.

Pourquoi doit-il examiner les extents et les dépendances des volumes avant de retirer ce périphérique ?

## Exercice 5 — RAID dégradé

Un RAID 1 fonctionne avec un seul composant restant actif.

Pourquoi est-il dangereux d'ignorer l'alerte même si les données sont encore accessibles ?

## Exercice 6 — Multipath

Deux chemins de stockage apparaissent sous deux noms de périphériques différents.

Quelles vérifications faut-il effectuer avant de les traiter comme deux disques indépendants ?

## Exercice 7 — Chiffrement

Explique la différence entre l'UUID du conteneur LUKS et celui du système de fichiers situé dans le volume déchiffré.

Quel type d'identifiant doit-on utiliser dans la configuration de déverrouillage, et lequel convient au montage du système de fichiers ?

## Exercice 8 — Instantanés

Pourquoi un instantané pris pendant les écritures d'une application ne garantit-il pas toujours la cohérence applicative ?

## Exercice 9 — XFS

Un volume XFS de 500 GiB doit être ramené à 300 GiB.

Pourquoi la procédure de réduction ext4 ne convient-elle pas ?

Propose une méthode de migration plus adaptée.

## Exercice 10 — Performance

Un benchmark indique plus d'IOPS, mais une latence p99 beaucoup plus élevée.

Pourquoi ce résultat ne signifie-t-il pas nécessairement que la nouvelle configuration est meilleure ?

## Exercice 11 — Stockage plein

`df -h` montre de l'espace libre, mais une application ne peut plus créer de fichiers.

Quelles vérifications effectuerais-tu avant de conclure à une anomalie matérielle ?

## Exercice 12 — Sauvegardes

Explique la différence entre :

- Un RAID.
- Un instantané LVM.
- Une sauvegarde indépendante.
- Une restauration testée.

Pourquoi sont-ils complémentaires ?


# 23. Défi final : architecture de stockage de production

## 23.1. Contexte

Tu es responsable de l'infrastructure Linux d'une entreprise.

Un serveur héberge une application métier importante. Ses données sont stockées sur un ensemble de volumes qui doivent être plus faciles à faire évoluer et à surveiller.

L'entreprise exige :

1. Une séparation entre le système et les données métier.
2. Une capacité d'extension documentée.
3. Une surveillance de la capacité physique et logique.
4. Une détection de panne des composants concernés.
5. Un chiffrement des données au repos lorsque l'architecture le permet.
6. Une protection contre certaines pannes matérielles.
7. Une gestion stricte des accès.
8. Une stratégie de sauvegarde distincte du stockage principal.
9. Un objectif de récupération documenté.
10. Une procédure d'incident testable.

Le laboratoire devra simuler ces besoins sans modifier le stockage d'une machine en production.

## 23.2. Architecture de référence

L'architecture ci-dessous est un modèle de travail, pas une prescription universelle :

```text
                    APPLICATION
                         |
                         v
                   /srv/projects
                         |
                         v
                    Système ext4
                         |
                         v
                 Volume logique LVM
                         |
                         v
                   Groupe LVM
                         |
                         v
                Couche de stockage
                         |
              +----------+----------+
              |                     |
              v                     v
        RAID local            Stockage SAN
              |                     |
              v                     v
       Périphériques          Multipath éventuel
              |                     |
              +----------+----------+
                         |
                         v
                  Surveillance
                         |
                         v
                Sauvegarde séparée
                         |
                         v
               Test de restauration
```

Toutes ces couches ne sont pas obligatoirement utilisées simultanément.

Par exemple, un serveur doté d'un SAN redondant géré par une équipe de stockage peut ne pas nécessiter un RAID logiciel local au-dessus du volume SAN. L'architecture finale doit respecter les responsabilités réelles de la plateforme.

## 23.3. Mission 1 — Établir la cartographie

Produis un inventaire :

```bash
lsblk -o NAME,MODEL,SERIAL,WWN,SIZE,TYPE,FSTYPE,UUID,MOUNTPOINTS
findmnt
df -hT
df -i
```

Puis collecte les informations LVM et RAID si ces couches sont utilisées :

```bash
sudo pvs
sudo vgs
sudo lvs -a -o+devices
cat /proc/mdstat
```

**Livrable :** un schéma de stockage indiquant les relations entre les couches et les points de montage critiques.

## 23.4. Mission 2 — Définir la capacité

Pour chaque volume métier, consigne :

```text
Capacité actuelle :
Occupation actuelle :
Inodes utilisés :
Croissance moyenne :
Croissance maximale observée :
Seuil d'alerte :
Marge opérationnelle :
Délai nécessaire à une extension :
Dépendances :
```

La capacité doit être dimensionnée à partir de l'utilisation actuelle et d'une prévision documentée.

## 23.5. Mission 3 — Concevoir la flexibilité LVM

Si LVM est utilisé :

- Vérifie les PV et les VG.
- Détermine si l'espace libre est suffisant.
- Identifie les volumes qui peuvent être agrandis.
- Définis la procédure d'ajout d'un périphérique.
- Détermine la nécessité ou non d'un pool fin.
- Évalue les effets d'une surallocation.
- Prévois la surveillance des métadonnées.

**Livrable :** une procédure d'extension avec préconditions, commandes de vérification et contrôles finaux.

## 23.6. Mission 4 — Choisir une stratégie de résilience

Documente les éléments suivants :

```text
Pannes couvertes :
Pannes non couvertes :
Niveau de redondance :
Mode de détection :
Procédure de remplacement :
Durée estimée de reconstruction :
Impact sur les performances :
Sauvegarde disponible :
Critères de retour à l'état nominal :
```

Pour du stockage SAN, intègre l'identité des volumes et des chemins.

Pour un RAID logiciel, documente les composants et la méthode de reconstruction.

Ne présente pas la redondance comme une sauvegarde.

## 23.7. Mission 5 — Protéger les données

Définis :

- Le niveau de chiffrement.
- Les personnes autorisées à déverrouiller.
- Les identifiants à conserver.
- La stratégie de sauvegarde des données.
- La protection des clés.
- La procédure de remplacement du serveur.
- La méthode de restauration sur une autre machine.

**Livrable :** une procédure de récupération qui n'exige pas l'accès au serveur original pour toutes les étapes.

## 23.8. Mission 6 — Établir le profil de performance

Définis les charges représentatives :

```text
Type de lecture :
Type d'écriture :
Taille des blocs :
Concurrence :
IOPS attendues :
Débit attendu :
Latence cible :
Latence p95/p99 acceptable :
Durée du test :
Charge concurrente :
```

Réalise les mesures uniquement dans un environnement approprié.

**Livrable :** un rapport qui explique les résultats et leurs limites, sans conclure à partir d'un indicateur isolé.

## 23.9. Mission 7 — Construire la surveillance

La supervision devra au minimum couvrir :

- Capacité des systèmes de fichiers.
- Inodes.
- Espace libre des groupes LVM.
- Pools fins et métadonnées.
- État RAID.
- État multipath si utilisé.
- État matériel disponible.
- Erreurs du noyau.
- Latence et débit.
- Résultat des sauvegardes.
- Résultat des tests de restauration.

**Livrable :** une liste d'alertes avec un seuil, une gravité, une personne ou équipe responsable et une procédure d'action.

## 23.10. Mission 8 — Construire un runbook de récupération

Prépare une procédure pour chacun des incidents suivants :

1. Volume plein.
2. Pool LVM presque plein.
3. RAID dégradé.
4. Perte d'un chemin multipath.
5. Échec de montage au démarrage.
6. Erreur de système de fichiers.
7. Perte d'un périphérique matériel.
8. Restauration d'une sauvegarde.

Chaque procédure doit inclure :

```text
Symptômes
Risques
Commandes d'observation
Hypothèses
Conditions d'intervention
Actions autorisées
Actions à éviter
Contrôles après intervention
Critères de clôture
```

## 23.11. Mission 9 — Démontrer la restauration

Dans un environnement de test :

1. Crée des données de démonstration.
2. Effectue une sauvegarde.
3. Contrôle les journaux et le résultat de la copie.
4. Simule l'indisponibilité de la source à l'aide d'un environnement isolé approprié.
5. Restaure les données dans une autre destination.
6. Vérifie le contenu.
7. Contrôle les propriétés nécessaires.
8. Exécute un test applicatif.
9. Consigne le temps réel de restauration.

Ne simule pas une panne sur un support critique en modifiant les périphériques réels.

## 23.12. Mission 10 — Présentation finale

Produis les livrables suivants :

- Un schéma textuel de l'architecture.
- Un inventaire des périphériques.
- Une matrice de dépendances.
- Un plan de capacité.
- Un plan de surveillance.
- Une procédure d'extension.
- Une procédure de remplacement des composants.
- Une stratégie de sauvegarde.
- Un plan de restauration.
- Un compte rendu du benchmark.
- Un bilan des risques restants.

**Critère de réussite :** un autre administrateur doit pouvoir comprendre l'architecture, identifier les couches importantes et exécuter une procédure de récupération sans dépendre exclusivement de tes explications orales.


# 24. Correction du défi final

Cette correction fournit une démarche modèle. Les capacités, chemins et identifiants doivent être remplacés par les valeurs observées dans l'environnement de laboratoire.

## 24.1. Architecture et dépendances

La première étape consiste à identifier les chemins critiques.

Exemple :

```text
Application
    |
    v
/srv/projects
    |
    v
ext4
    |
    v
/dev/vgdata/lvprojects
    |
    v
vgdata
    |
    v
Couche physique
    |
    v
Périphériques de stockage
```

On documente pour chaque couche :

- L'identifiant.
- La capacité.
- Les dépendances.
- L'état opérationnel.
- La méthode de surveillance.
- La procédure de restauration.

## 24.2. Capacité et flexibilité

Pour les volumes classiques, les commandes de contrôle sont :

```bash
sudo pvs -o+pv_used,pv_free
sudo vgs -o+vg_size,vg_free
sudo lvs -a -o+devices
df -hT /srv/projects
```

La procédure doit distinguer l'extension du volume logique de celle du système de fichiers.

Lorsque la configuration le permet, une extension ext4 peut être demandée avec :

```bash
sudo lvextend -r -L +10G /dev/vgdata/lvprojects
```

Cette opération suppose que :

- Le volume existe réellement.
- Le groupe dispose de la capacité physique nécessaire.
- La cible a été identifiée correctement.
- Le système de fichiers est compatible avec la procédure.
- Les conditions opérationnelles autorisent l'extension.

Le résultat se vérifie avec :

```bash
sudo lvs
df -hT /srv/projects
```

## 24.3. Résilience

Le choix de redondance doit correspondre aux risques que l'organisation veut réduire.

Une architecture RAID peut tolérer certaines pannes de composants.

Une architecture multipath peut maintenir des chemins d'accès vers un volume lorsque l'infrastructure et la configuration appropriées sont en place.

Ni l'une ni l'autre ne garantit à elle seule la restauration de données supprimées ou la survie à la perte de toute l'infrastructure.

## 24.4. Chiffrement

Une architecture LUKS peut suivre ce modèle :

```text
Périphérique chiffré
        |
        v
      LUKS
        |
        v
Périphérique déchiffré
        |
        v
      LVM ou ext4
        |
        v
Point de montage
```

La procédure doit documenter la gestion des secrets et la différence entre l'UUID LUKS et l'UUID du système de fichiers.

La récupération des données ne peut être considérée comme démontrée que si les secrets et les outils nécessaires sont accessibles conformément à la politique de sécurité.

## 24.5. Surveillance

La collecte de base peut inclure :

```bash
df -hT
df -i
iostat -xz 1 10
sudo pvs
sudo vgs
sudo lvs -a -o+devices
cat /proc/mdstat
sudo journalctl -k --since "30 minutes ago"
```

Les commandes qui ne concernent pas l'architecture réelle doivent être adaptées ou retirées du rapport.

La surveillance doit conserver une évolution dans le temps. Une série de mesures permet d'identifier la croissance et de distinguer certains incidents passagers d'une dégradation durable.

## 24.6. Sauvegarde et restauration

La méthode recommandée consiste à réaliser une copie de test, puis une restauration vers un emplacement différent.

Avant l'opération :

```bash
findmnt /srv/projects
findmnt /backup
df -hT /srv/projects /backup
```

Simulation :

```bash
sudo rsync -aHAXn --numeric-ids \
  /srv/projects/ \
  /backup/projects/
```

Exécution après validation :

```bash
sudo rsync -aHAX --numeric-ids \
  /srv/projects/ \
  /backup/projects/
```

Restauration dans une zone séparée :

```bash
sudo mkdir -p /restore-test/projects
sudo rsync -aHAX --numeric-ids \
  /backup/projects/ \
  /restore-test/projects/
```

Il faut ensuite vérifier les données, les permissions et les propriétés requises par l'application.

Une sauvegarde de fichiers n'est pas forcément une sauvegarde cohérente d'une base de données active. La stratégie finale doit traiter les besoins spécifiques de l'application.

## 24.7. Critères de clôture d'un incident

Un incident de stockage ne devrait pas être clos simplement parce qu'une commande ne renvoie plus d'erreur.

Il faut confirmer :

- Le retour de la capacité attendue.
- Le retour d'un état sain des couches de stockage.
- La cohérence du système de fichiers.
- L'absence de nouvelles erreurs pertinentes.
- Le fonctionnement applicatif.
- Le bon fonctionnement des sauvegardes.
- La mise à jour de la documentation.
- Le traitement de la cause initiale, ou au minimum l'acceptation documentée du risque restant.


# 25. Checklist d'exploitation experte

## Avant un changement

- [ ] Identifier les périphériques et leurs identifiants stables.
- [ ] Cartographier les couches dépendantes.
- [ ] Vérifier la capacité physique et logique.
- [ ] Examiner LVM, RAID et multipath si présents.
- [ ] Contrôler l'état matériel disponible.
- [ ] Vérifier les systèmes de fichiers.
- [ ] Confirmer l'existence d'une sauvegarde appropriée.
- [ ] Préparer un retour arrière.
- [ ] Documenter l'objectif et le risque.
- [ ] Confirmer que la fenêtre d'intervention est autorisée.

## Après une extension

- [ ] Vérifier les volumes physiques.
- [ ] Vérifier le groupe de volumes.
- [ ] Vérifier le volume logique.
- [ ] Vérifier la taille du système de fichiers.
- [ ] Vérifier les capacités et inodes disponibles.
- [ ] Confirmer le montage.
- [ ] Exécuter un test applicatif.
- [ ] Contrôler les journaux.
- [ ] Mettre à jour l'inventaire.

## Pour une architecture RAID ou multipath

- [ ] Identifier la vraie identité des composants.
- [ ] Vérifier l'état des chemins.
- [ ] Vérifier l'état de l'ensemble.
- [ ] Confirmer la procédure de remplacement.
- [ ] Surveiller la reconstruction ou le retour des chemins.
- [ ] Contrôler les performances après intervention.
- [ ] Vérifier que les alertes ont disparu.
- [ ] Maintenir des sauvegardes indépendantes.

## Pour LVM à allocation fine

- [ ] Surveiller l'espace physique.
- [ ] Surveiller les métadonnées.
- [ ] Observer les volumes virtuels.
- [ ] Contrôler les instantanés.
- [ ] Prévoir l'ajout de capacité.
- [ ] Documenter les limites d'allocation.
- [ ] Tester la procédure d'extension.

## Pour le chiffrement

- [ ] Identifier le conteneur LUKS.
- [ ] Distinguer l'UUID LUKS de l'UUID du système de fichiers.
- [ ] Protéger les clés.
- [ ] Documenter le déverrouillage.
- [ ] Tester la récupération.
- [ ] Vérifier les permissions après montage.
- [ ] Inclure les sauvegardes dans la politique de sécurité.

## Pour une sauvegarde

- [ ] Confirmer la destination.
- [ ] Vérifier la capacité disponible.
- [ ] Préserver la cohérence de l'application.
- [ ] Vérifier l'exécution de la copie.
- [ ] Protéger la rétention.
- [ ] Restaurer des données de test.
- [ ] Vérifier l'intégrité.
- [ ] Mesurer le temps de restauration.
- [ ] Documenter les écarts.

## Après un incident

- [ ] Consigner la chronologie.
- [ ] Identifier la couche défaillante.
- [ ] Conserver les mesures et les journaux utiles.
- [ ] Vérifier les données et les services.
- [ ] Confirmer la sauvegarde.
- [ ] Traiter la cause initiale.
- [ ] Mettre à jour le runbook.
- [ ] Définir des mesures préventives.


# 26. Référence des commandes essentielles

## 26.1. Inventaire et diagnostic

| Commande | Fonction |
|---|---|
| `lsblk -f` | Cartographie des périphériques et systèmes de fichiers |
| `lsblk -o NAME,MODEL,SERIAL,WWN,SIZE,TYPE` | Identification détaillée du matériel visible |
| `ls -l /dev/disk/by-id/` | Consultation des identifiants persistants disponibles |
| `sudo blkid` | Consultation des UUID et signatures détectées |
| `findmnt` | Observation des montages |
| `df -hT` | Capacité et occupation |
| `df -i` | Utilisation des inodes |
| `sudo journalctl -k --since "30 minutes ago"` | Journaux récents du noyau |
| `cat /proc/diskstats` | Statistiques brutes des périphériques blocs |

## 26.2. Performances

| Commande | Fonction |
|---|---|
| `iostat -xz 1 10` | Statistiques d'entrée-sortie dans le temps |
| `pidstat -d 1 10` | Activité d'entrée-sortie par processus |
| `sudo iotop` | Observation interactive des opérations d'entrée-sortie |
| `fio ...` | Génération de charges de test |
| `sudo smartctl -a /dev/sdX` | Informations de santé SMART disponibles |
| `sudo nvme list` | Inventaire NVMe, si pris en charge |
| `sudo nvme smart-log /dev/nvme0` | Informations de santé NVMe, si prises en charge |

## 26.3. LVM

| Commande | Fonction |
|---|---|
| `sudo pvs -o+pv_used,pv_free` | État et allocation des volumes physiques |
| `sudo vgs -o+vg_size,vg_free` | Capacité des groupes de volumes |
| `sudo lvs -a -o+devices` | Volumes logiques et dépendances |
| `sudo pvmove /dev/sdb1 /dev/sdc1` | Déplacement d'extents, sous conditions |
| `sudo lvcreate --type thin-pool ...` | Création d'un pool fin |
| `sudo lvs -a -o+data_percent,metadata_percent` | Surveillance des pools fins |
| `sudo lvextend -r ...` | Extension du volume et du système de fichiers compatible |

## 26.4. RAID et multipath

| Commande | Fonction |
|---|---|
| `cat /proc/mdstat` | État général du RAID logiciel |
| `sudo mdadm --detail --scan` | Liste des ensembles connus |
| `sudo mdadm --detail /dev/md0` | Détails d'un ensemble précis |
| `sudo multipath -ll` | État des chemins multipath |
| `sudo dmsetup ls --tree` | Arbre des mappages Device Mapper |
| `lsblk -o NAME,SIZE,MODEL,SERIAL` | Identification des périphériques |

## 26.5. Chiffrement

| Commande | Fonction |
|---|---|
| `sudo cryptsetup luksDump /dev/DEVICE` | Informations sur l'en-tête LUKS |
| `sudo cryptsetup luksUUID /dev/DEVICE` | UUID du conteneur LUKS |
| `sudo cryptsetup open /dev/DEVICE NOM` | Ouverture d'un volume chiffré |
| `sudo cryptsetup close NOM` | Fermeture d'un mappage ouvert |
| `sudo blkid /dev/mapper/NOM` | Identification du système de fichiers déchiffré |

## 26.6. Systèmes de fichiers

| Commande | Fonction |
|---|---|
| `sudo tune2fs -l /dev/DEVICE` | Informations ext |
| `sudo e2fsck -f /dev/DEVICE` | Vérification ext dans les conditions adaptées |
| `sudo resize2fs /dev/DEVICE` | Redimensionnement ext selon les contraintes |
| `sudo xfs_info /data` | Informations XFS sur un montage |
| `sudo xfs_repair /dev/DEVICE` | Outil de réparation XFS à utiliser selon le scénario |
| `sudo btrfs filesystem usage /data` | Utilisation du stockage Btrfs |
| `sudo btrfs filesystem show` | Périphériques Btrfs |
| `sudo btrfs scrub start -Bd /data` | Scrub Btrfs avec suivi de fin, selon la configuration |

## 26.7. Sauvegarde et récupération

| Commande | Fonction |
|---|---|
| `rsync -avn SOURCE/ DESTINATION/` | Simulation de synchronisation |
| `rsync -aHAX SOURCE/ DESTINATION/` | Copie avec préservation de propriétés prises en charge |
| `sha256sum fichier` | Calcul d'une somme de contrôle |
| `journalctl --disk-usage` | Espace utilisé par le journal systemd |
| `sudo lsof +L1` | Recherche de fichiers supprimés encore ouverts |

## 26.8. Commandes à risque élevé

Les commandes suivantes peuvent modifier les données ou métadonnées et doivent être exécutées seulement dans une procédure maîtrisée :

```bash
sudo mkfs.ext4 /dev/DEVICE
sudo cryptsetup luksFormat /dev/DEVICE
sudo pvcreate /dev/DEVICE
sudo lvcreate ...
sudo lvreduce ...
sudo pvmove ...
sudo mdadm --create ...
sudo e2fsck ...
sudo xfs_repair ...
sudo btrfs check --repair ...
```

Elles n'ont pas toutes les mêmes effets. La précaution consiste à identifier le périphérique, consulter la documentation et vérifier les préconditions spécifiques.

Une commande de réparation peut être aussi risquée qu'une commande de formatage si elle est lancée sur la mauvaise cible ou dans une situation inadaptée.


# 27. Conclusion

Le niveau expert de l'administration du stockage Linux demande de dépasser la connaissance des commandes pour raisonner sur la chaîne complète des données.

Tu as appris à :

- Cartographier les couches physiques et logiques.
- Utiliser des identifiants stables.
- Comprendre les performances en termes d'IOPS, de débit et de latence.
- Mesurer une charge avec `fio`.
- Examiner la santé du stockage.
- Déplacer des extents avec LVM.
- Comprendre le provisionnement fin et ses risques.
- Utiliser les instantanés en tenant compte de leur capacité et de la cohérence applicative.
- Réagir face à un RAID dégradé.
- Comprendre le rôle de multipath dans les environnements SAN.
- Explorer les principes du stockage réseau.
- Mettre en œuvre un volume chiffré avec LUKS.
- Choisir les outils de maintenance selon ext4, XFS ou Btrfs.
- Concevoir une supervision multicouche.
- Documenter les procédures d'incident.
- Distinguer haute disponibilité, intégrité et restauration.
- Construire une stratégie de sauvegarde vérifiable.
- Préparer des tests de récupération réalistes.

La discipline centrale de l'administration experte peut se résumer ainsi :

```text
                 OBSERVER
                     |
                     v
                 MESURER
                     |
                     v
                 ANALYSER
                     |
                     v
             IDENTIFIER LA COUCHE
                     |
                     v
              ÉVALUER LES RISQUES
                     |
                     v
             PLANIFIER L'OPÉRATION
                     |
                     v
               EXÉCUTER CONTRÔLÉ
                     |
                     v
             VÉRIFIER CHAQUE COUCHE
                     |
                     v
             VALIDER L'APPLICATION
                     |
                     v
                DOCUMENTer
```

Une architecture de stockage fiable ne repose pas uniquement sur des disques rapides ou sur une grande capacité. Elle repose sur une conception cohérente, une surveillance adaptée, des procédures documentées et une récupération démontrée.

**L'objectif professionnel final n'est pas seulement de faire fonctionner le stockage : c'est de savoir expliquer son état, prévoir ses limites, maîtriser ses changements et restaurer les données lorsque le système rencontre un incident.**