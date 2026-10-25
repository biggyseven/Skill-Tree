# Gestion avancée de l'hyperviseur
## Cours intermédiaire — Administration des VM, templates, stockage, migrations, sauvegardes et automatisation

## 1. Présentation du cours

### 1.1 Objectif général

Au niveau débutant, tu as appris à comprendre la virtualisation, à créer une première machine virtuelle et à découvrir KVM/libvirt, Proxmox VE et VMware.

Le niveau intermédiaire passe de la création ponctuelle de machines à **l'administration structurée d'un parc de machines virtuelles**.

Dans une infrastructure réelle, l'administrateur doit savoir modifier les ressources sans provoquer d'indisponibilité inutile, organiser les disques, créer des modèles réutilisables, planifier les migrations, contrôler les performances, sauvegarder les VM et les restaurer après un incident.

Il doit aussi comprendre pourquoi une machine virtuelle peut démarrer correctement tout en restant inutilisable à cause d'une saturation de stockage, d'une erreur réseau, d'un manque de mémoire ou d'une dépendance applicative indisponible.

Ce cours approfondit trois environnements :

- **KVM/QEMU avec libvirt** : administration Linux des machines virtuelles, des domaines, des réseaux virtuels, des pools de stockage et des migrations.
- **Proxmox VE** : gestion intégrée des VM, templates, clones, stockages, sauvegardes, migrations et ressources de cluster.
- **VMware vSphere** : gestion des hôtes ESXi, des datastores, des ressources CPU/RAM, des templates, des snapshots et des migrations.

Les principes sont communs, mais les commandes et les fonctionnalités ne sont pas interchangeables.

### 1.2 Compétences visées

À la fin du cours, tu devras être capable de :

- Administrer le cycle de vie complet d'une machine virtuelle.
- Inventorier et standardiser les configurations.
- Dimensionner correctement les ressources CPU et mémoire.
- Comprendre les réservations, limites et mécanismes de partage des ressources.
- Gérer les disques virtuels, leurs formats et leur capacité.
- Organiser les pools de stockage et les datastores.
- Concevoir des réseaux virtuels adaptés aux environnements de test et de production.
- Créer et utiliser des templates.
- Distinguer un clone complet d'un clone lié.
- Utiliser les snapshots avec les précautions nécessaires.
- Construire une stratégie de sauvegarde et de restauration.
- Comprendre les prérequis des migrations à froid et à chaud.
- Évaluer la compatibilité des hôtes.
- Préparer une maintenance de l'hyperviseur.
- Automatiser les opérations simples avec les outils CLI et les API appropriés.
- Surveiller les performances et identifier les saturations.
- Diagnostiquer les problèmes de démarrage, de réseau et de stockage.
- Sécuriser les interfaces d'administration et les accès aux machines virtuelles.
- Documenter les changements et prévoir un retour arrière.

### 1.3 Prérequis

Tu dois connaître les notions présentées au niveau débutant :

- Hyperviseur et machine virtuelle.
- CPU, vCPU, RAM et stockage.
- Réseau NAT, bridge et réseau isolé.
- KVM, QEMU et libvirt.
- Proxmox VE.
- ESXi et vSphere.
- Systèmes d'exploitation invités.
- Sauvegarde et snapshot.
- Adresses IP, sous-réseaux et DNS.
- Utilisation élémentaire de Linux et PowerShell.

Ce cours n'impose pas que tu possèdes les trois plateformes. Les travaux peuvent être réalisés sur celle que tu disposes, tandis que les sections comparatives permettent de comprendre les autres environnements.

### 1.4 Environnement de référence

Nous utiliserons des exemples pédagogiques pour les trois plateformes.

| Élément | Valeur illustrative |
|---|---|
| Hôte Linux/libvirt | `kvm01` |
| VM Linux | `lab-linux01` |
| VM Web | `VM-WEB01` |
| VM base de données | `VM-DB01` |
| Hôte Proxmox | `pve01` |
| Second hôte Proxmox | `pve02` |
| Hôte VMware | `esxi01` |
| Second hôte VMware | `esxi02` |
| Réseau de gestion | `192.168.100.0/24` |
| Réseau des VM | `192.168.110.0/24` |
| Réseau de laboratoire | `192.168.120.0/24` |

Ces valeurs sont fictives. Elles doivent être adaptées aux réseaux, aux noms de machines et aux ressources réellement disponibles.

**Règle de sécurité :** avant de modifier un réseau de gestion, un disque virtuel ou une configuration de machine en production, vérifie les dépendances, sauvegarde les informations nécessaires et prévois une procédure de retour arrière.

## 2. Passer de la création de VM à leur gestion complète

### 2.1 Le cycle de vie d'une machine virtuelle

Une VM ne doit pas être considérée comme un objet que l'on crée une fois puis que l'on oublie.

Elle possède un cycle de vie :

```text
           DEMANDE DE NOUVELLE VM
                     |
                     v
           Définition du besoin
                     |
                     v
           Dimensionnement CPU/RAM
                     |
                     v
           Choix du stockage
                     |
                     v
           Choix du réseau
                     |
                     v
           Création depuis ISO ou template
                     |
                     v
           Installation et configuration
                     |
                     v
           Contrôles de sécurité
                     |
                     v
           Mise en service
                     |
                     v
           Surveillance et maintenance
                     |
                     v
           Sauvegarde et tests de restauration
                     |
                     v
           Migration ou mise à jour
                     |
                     v
           Retrait et suppression contrôlée
```

Chaque phase doit laisser des informations exploitables : paramètres, dépendances, résultats de tests, procédures et propriétaire de la machine.

### 2.2 La fiche d'identité d'une VM

Pour chaque VM importante, documente :

- Son nom.
- Son identifiant dans l'hyperviseur.
- Son système d'exploitation.
- Son rôle.
- Son propriétaire métier.
- Son responsable technique.
- Son nombre de vCPU.
- Sa mémoire.
- Ses disques.
- Son réseau.
- Son adresse IP.
- Ses dépendances.
- Sa politique de sauvegarde.
- Son niveau de criticité.
- Ses fenêtres de maintenance.

Exemple :

```text
Nom : VM-WEB01
Rôle : serveur Web interne
Système : Linux
CPU : 2 vCPU
Mémoire : 4 Gio
Disque système : 40 Gio
Disque données : 100 Gio
Réseau : Production-Web
Sauvegarde : quotidienne, selon la politique retenue
Criticité : importante
Dépendances : DNS, certificat TLS, API métier
Propriétaire : équipe applicative
```

Les valeurs ne sont que des exemples. La mémoire et les disques doivent être dimensionnés selon les mesures et les exigences de l'application.

### 2.3 Pourquoi l'inventaire est essentiel

Un hyperviseur peut contenir des dizaines ou des centaines de VM.

Sans inventaire, il devient difficile de répondre à des questions fondamentales :

- Quelles VM sont réellement utilisées ?
- Qui est responsable de chaque machine ?
- Quels systèmes doivent être sauvegardés ?
- Quelles VM peuvent être arrêtées ?
- Quel est le coût en CPU, mémoire et stockage ?
- Quelles machines doivent être mises à jour en priorité ?
- Quelles dépendances seront touchées par une migration ?

L'inventaire est donc à la fois un outil technique, administratif et financier.

## 3. Administrer les ressources CPU

### 3.1 Le vCPU n'est pas un cœur physique réservé

Une machine virtuelle dispose de processeurs virtuels, appelés vCPU.

L'hyperviseur planifie leur exécution sur les ressources CPU physiques.

```text
                  CPU PHYSIQUE
              +-------------------+
              | Cœurs physiques   |
              +-------------------+
                       |
                       v
                  HYPERVISEUR
                       |
              +--------+--------+
              |        |        |
              v        v        v
           VM-WEB    VM-APP    VM-DB
           2 vCPU    4 vCPU    4 vCPU
```

Dans cet exemple, les VM possèdent dix vCPU au total. Cela ne signifie pas que dix cœurs physiques leur sont exclusivement réservés.

Si les VM demandent simultanément plus de capacité que l'hôte ne peut fournir, elles peuvent se retrouver en concurrence.

### 3.2 Surallocation CPU

La surallocation consiste à attribuer au total plus de vCPU que l'hôte ne possède de cœurs physiques disponibles.

Cela peut convenir aux charges variables, lorsque toutes les VM n'utilisent pas constamment leur capacité maximale.

Exemple :

| VM | vCPU configurés |
|---|---:|
| VM-WEB01 | 2 |
| VM-WEB02 | 2 |
| VM-APP01 | 4 |
| VM-APP02 | 4 |
| VM-DB01 | 4 |
| Total | 16 |

Si l'hôte ne possède que huit cœurs physiques, il existe une surallocation en nombre de vCPU. Cela ne provoque pas nécessairement un problème permanent, mais il faut mesurer la charge et la concurrence réelles.

La bonne décision dépend des caractéristiques des applications.

### 3.3 Surallocation mémoire

La mémoire demande davantage de prudence.

Supposons qu'un hôte dispose de 32 Gio de RAM et héberge plusieurs VM dont la mémoire configurée totalise 48 Gio.

Selon l'hyperviseur, le mécanisme de provisionnement et la configuration mémoire, ce dépassement peut être possible. Il ne garantit pas que toutes les VM pourront réellement disposer simultanément de leur mémoire demandée.

Les mécanismes de ballooning, de compression ou de pagination de l'hyperviseur ne remplacent pas une capacité physique suffisante.

Une saturation mémoire peut provoquer :

- Un ralentissement important.
- Une pagination excessive.
- Des difficultés à démarrer de nouvelles VM.
- Des échecs d'opérations.
- Une dégradation des applications.

Pour les charges sensibles, il est préférable de dimensionner à partir de mesures plutôt que de supposer qu'une surallocation sera toujours supportable.

### 3.4 Mesurer avant d'augmenter

Une VM lente n'a pas nécessairement besoin de plus de vCPU.

Les symptômes peuvent aussi être provoqués par :

- Un stockage lent.
- Un manque de mémoire.
- Des attentes réseau.
- Une base de données surchargée.
- Une dépendance applicative indisponible.
- Des tâches d'arrière-plan.

La démarche correcte est :

1. Mesurer la charge CPU.
2. Examiner la consommation mémoire.
3. Examiner les temps d'attente du stockage.
4. Vérifier la latence réseau.
5. Identifier les processus consommateurs.
6. Comparer les mesures au comportement normal.
7. Modifier les ressources si les observations le justifient.
8. Mesurer à nouveau.

### 3.5 Réservations, limites et partages

Les mécanismes sont propres à chaque hyperviseur, mais plusieurs concepts se retrouvent.

**Réservation**

Garantie minimale de ressources lorsque la capacité disponible et la configuration de la plateforme permettent de la respecter.

**Limite**

Plafond imposé à la consommation d'une ressource.

**Partages ou priorité**

Mécanisme qui aide l'hyperviseur à répartir les ressources entre des machines concurrentes lorsqu'une contention existe.

Une limite CPU ou mémoire trop basse peut ralentir une VM alors que l'hôte semble disposer de ressources physiques libres.

Une réservation trop importante peut empêcher de démarrer d'autres VM ou de déplacer certaines charges.

### 3.6 Exemple de planification de capacité

Imaginons un hôte doté de 16 cœurs physiques et de 64 Gio de RAM.

L'organisation souhaite héberger :

| VM | vCPU | RAM |
|---|---:|---:|
| VM-WEB01 | 2 | 4 Gio |
| VM-WEB02 | 2 | 4 Gio |
| VM-APP01 | 4 | 8 Gio |
| VM-DB01 | 4 | 16 Gio |
| VM-MON01 | 2 | 4 Gio |
| Total configuré | 14 | 36 Gio |

La somme configurée est de 14 vCPU et 36 Gio de RAM.

Il reste théoriquement 28 Gio entre les 64 Gio physiques et les allocations configurées, mais ce calcul ne tient pas compte des besoins de l'hôte, de la mémoire réellement consommée, des réservations et des besoins supplémentaires.

Il faut également examiner les pointes CPU et mémoire.

Le dimensionnement se valide par des mesures et des tests de charge.

## 4. Gestion CPU et mémoire sous KVM/libvirt

### 4.1 Consulter la configuration d'une VM

Pour examiner une VM avec libvirt :

```bash
sudo virsh dominfo lab-linux01
```

Pour afficher la configuration XML :

```bash
sudo virsh dumpxml lab-linux01
```

La configuration décrit notamment les ressources CPU, la mémoire, les disques, les interfaces réseau et certains paramètres de périphériques.

Le XML est puissant mais doit être modifié avec prudence.

### 4.2 Examiner les vCPU

```bash
sudo virsh vcpucount lab-linux01
```

Cette commande fournit des informations sur les nombres de CPU virtuels définis ou actifs selon les options et les versions.

Pour afficher la configuration CPU détaillée, examine le XML de la VM.

### 4.3 Modifier le nombre de vCPU

La commande suivante définit le nombre maximum de vCPU configuré dans le domaine :

```bash
sudo virsh setvcpus lab-linux01 4 --config
```

`--config` demande une modification de la configuration persistante.

Cela ne signifie pas nécessairement que le nombre de vCPU sera modifié immédiatement dans le système invité. Les changements à chaud dépendent des capacités du matériel virtuel, du système invité et de la version.

Avant une modification, vérifie que le système invité prend en charge le changement.

### 4.4 Modifier la mémoire

Une modification persistante peut être demandée avec :

```bash
sudo virsh setmaxmem lab-linux01 4G --config
```

Puis, selon le besoin et le scénario :

```bash
sudo virsh setmem lab-linux01 4G --config
```

Les changements de mémoire sont soumis aux limites de la configuration de la VM, aux capacités de l'hyperviseur et au fait que la machine soit arrêtée ou en fonctionnement.

Ne suppose pas qu'une modification demandée par la commande est nécessairement applicable à chaud dans tous les environnements.

Consulte l'aide locale :

```bash
virsh help setmem
virsh help setmaxmem
```

### 4.5 Vérifier l'usage CPU et mémoire de l'hôte

Sur Linux :

```bash
top
```

Pour consulter la mémoire :

```bash
free -h
```

Pour observer la charge et les attentes :

```bash
vmstat 1 5
```

Si l'outil est disponible, `iostat` permet également de mesurer certains indicateurs d'E/S du stockage.

Les outils doivent être interprétés ensemble. Une consommation mémoire élevée n'est pas nécessairement anormale, car Linux utilise une partie de la mémoire disponible comme cache.

### 4.6 CPU model et migration

Une VM configurée avec des fonctionnalités CPU dépendant fortement du processeur de l'hôte peut devenir difficile à migrer vers un hôte moins récent ou différent.

Avec libvirt, différents modes de définition du CPU existent, notamment des modèles explicites et des approches basées sur le modèle de l'hôte.

Il faut choisir entre :

- Accès à un ensemble de fonctionnalités CPU plus large.
- Compatibilité entre hôtes.
- Possibilité de migration.
- Exigences applicatives particulières.

Une VM optimisée pour les capacités d'un hôte peut ne pas être compatible avec tous les autres serveurs.

Documentation : [Ubuntu Server — Libvirt](https://ubuntu.com/server/docs/how-to/virtualisation/libvirt/).

## 5. Gestion CPU et mémoire dans Proxmox VE

### 5.1 Examiner la configuration

Dans un hôte Proxmox, la commande suivante affiche les paramètres d'une VM :

```bash
qm config 101
```

Le nombre `101` représente un identifiant de VM d'exemple.

Lister les VM :

```bash
qm list
```

Examiner l'état de la VM :

```bash
qm status 101
```

### 5.2 Modifier les ressources d'une VM

Exemple :

```bash
qm set 101 --cores 2 --memory 4096
```

Cette commande définit deux cœurs virtuels pour la configuration CPU de la VM et 4096 Mio de mémoire configurée.

Les modifications qui affectent le matériel virtuel peuvent nécessiter l'arrêt de la VM selon la configuration, la version et le paramètre concerné.

Vérifie l'état et la configuration avant et après la modification.

### 5.3 Comprendre les limites de CPU

Proxmox permet de configurer certains paramètres liés à l'utilisation CPU, notamment la limite et les parts CPU.

La limite peut plafonner la consommation de la VM, tandis que les parts aident à répartir les ressources lorsque plusieurs machines sont concurrentes.

Une limite très faible peut ralentir une application même si l'hôte possède des ressources libres.

Ne configure donc pas les limites uniquement pour obtenir une répartition « égale » des cœurs.

### 5.4 Balloning mémoire

Le ballooning permet à l'hyperviseur de récupérer ou d'ajuster une partie de la mémoire attribuée dans certaines conditions, avec la coopération du système invité et des pilotes pris en charge.

Il peut améliorer l'utilisation des ressources, mais il n'est pas équivalent à une réservation fixe de mémoire.

Il faut vérifier :

- La compatibilité du système invité.
- La présence des pilotes nécessaires.
- La configuration de la VM.
- Les besoins applicatifs.
- Les indicateurs de pression mémoire.

Pour des applications sensibles à la mémoire, la décision doit s'appuyer sur des mesures et des recommandations spécifiques à l'application.

Documentation : [Guide d'administration Proxmox VE](https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf).

## 6. Gestion des ressources sous VMware vSphere

### 6.1 Modèle CPU et mémoire

vSphere propose différents mécanismes d'allocation des ressources, notamment :

- Réservations.
- Limites.
- Shares, ou parts de ressources.
- Resource Pools.
- Contrôle de capacité au niveau du cluster.

La terminologie exacte et les options disponibles dépendent de la version et de la configuration.

### 6.2 Réservation

Une réservation CPU ou mémoire permet de garantir une quantité minimale de ressources dans les conditions prévues par la plateforme.

Une réservation trop élevée peut limiter la capacité disponible pour les autres VM et empêcher certaines opérations de démarrage ou de placement.

### 6.3 Limites

Une limite CPU ou mémoire agit comme une frontière supérieure imposée à la VM.

Une VM peut donc être ralentie par une limite même si l'hôte semble disposer de capacités inutilisées.

Avant de modifier une limite, vérifie si elle a été définie intentionnellement pour une raison de qualité de service.

### 6.4 Shares

Les shares interviennent surtout lorsque plusieurs machines concurrentes demandent simultanément des ressources.

Elles servent à exprimer une priorité relative, et non à réserver automatiquement une capacité physique fixe en permanence.

### 6.5 Resource Pools

Un Resource Pool permet de regrouper des ressources pour les gérer à un niveau commun dans une infrastructure vSphere compatible.

Il peut être utile pour répartir les ressources entre des équipes ou des familles de services.

Mais un pool mal dimensionné, doté de limites trop strictes, peut provoquer une contention ou empêcher certaines VM d'obtenir les ressources nécessaires.

### 6.6 Contrôler les performances

Dans vSphere, examine notamment :

- La consommation CPU.
- Le CPU Ready lorsque cette métrique est disponible.
- La consommation mémoire.
- Les indicateurs de contention mémoire.
- Les latences du datastore.
- Les performances des réseaux.
- Les limites et réservations appliquées.

Une VM lente n'a pas nécessairement besoin de plus de CPU. Les métriques doivent permettre de distinguer une pénurie physique d'une limite administrative.

Documentation : [Base de connaissances Broadcom — VMware](https://knowledge.broadcom.com/).

## 7. Gérer les disques virtuels et le stockage

### 7.1 Pourquoi le stockage est souvent déterminant

Une VM peut disposer de suffisamment de CPU et de mémoire tout en restant lente parce que ses disques sont saturés.

Le stockage doit être dimensionné en fonction de :

- La capacité.
- Le nombre d'opérations d'entrée-sortie.
- Le débit.
- La latence.
- Le type de média.
- Les contrôleurs.
- Les opérations de sauvegarde.
- Les snapshots.
- La croissance des données.
- Le niveau de résilience attendu.

Le stockage n'est donc pas seulement une question de capacité en gigaoctets.

### 7.2 Disque virtuel, volume et datastore

Ces notions doivent être distinguées.

**Disque virtuel**

Périphérique présenté à une VM.

**Système de fichiers invité**

Organisation des fichiers à l'intérieur du système invité.

**Stockage de l'hyperviseur**

Emplacement physique ou logique sur lequel le disque virtuel est conservé.

**Pool de stockage**

Ensemble de ressources géré par la plateforme pour l'allocation de volumes ou d'images.

**Datastore**

Terme utilisé notamment dans VMware pour désigner un emplacement de stockage de fichiers et de ressources virtuelles.

Schéma :

```text
HÔTE DE VIRTUALISATION
|
+-- Stockage physique ou logique
    |
    +-- Pool / datastore
        |
        +-- Disque virtuel de VM-WEB01
        |
        +-- Disque virtuel de VM-DB01
        |
        +-- Disque virtuel de VM-APP01
```

Le mécanisme de stockage peut être local, partagé ou distribué selon la plateforme.

### 7.3 Format QCOW2

QCOW2 est un format d'image disque couramment utilisé avec QEMU.

Il permet notamment l'allocation dynamique et certaines fonctions de snapshots selon la configuration.

Pour afficher des informations sur une image :

```bash
qemu-img info /var/lib/libvirt/images/lab-linux01.qcow2
```

Cette commande affiche des propriétés telles que le format et les tailles de l'image.

Ne modifie pas directement une image disque utilisée par une VM en fonctionnement à moins de suivre une procédure spécifiquement prévue et maîtrisée.

### 7.4 Conversion de disque

QEMU fournit des outils capables de convertir des images disque entre différents formats compatibles.

Exemple pédagogique pour convertir une image QCOW2 vers une nouvelle image QCOW2 :

```bash
qemu-img convert \
    -p \
    -f qcow2 \
    -O qcow2 \
    source.qcow2 \
    destination.qcow2
```

**Précaution importante :** cet exemple suppose que le disque source est dans un état compatible avec l'opération. Pour un disque utilisé par une VM, il faut prévoir un arrêt ou une procédure cohérente de sauvegarde et de copie. Ne convertis pas un disque actif à l'aveugle.

Avant la conversion, vérifie les chemins, le format et l'espace libre de destination.

### 7.5 Capacité virtuelle et capacité physique

Un disque dynamique peut annoncer une capacité de 200 Gio tout en occupant beaucoup moins d'espace physique au départ.

Exemple :

```text
Capacité virtuelle du disque : 200 Gio
Données réellement présentes : 45 Gio
Espace physique occupé : variable selon le format
```

L'espace réel dépend également des métadonnées, des snapshots, des blocs non libérés et du système de stockage sous-jacent.

Il faut surveiller la capacité physique de l'hôte ou du datastore, pas uniquement la taille annoncée dans la VM.

### 7.6 Supprimer ou réduire un disque

La réduction d'un disque virtuel est une opération délicate.

Elle peut demander de réduire d'abord le système de fichiers et les partitions dans l'invité, puis d'utiliser la procédure prise en charge par la plateforme pour réduire le disque physique ou virtuel.

Toutes les technologies ne prennent pas en charge les mêmes opérations de réduction.

Avant toute réduction :

1. Sauvegarder la VM.
2. Vérifier le système de fichiers.
3. Examiner les partitions.
4. Vérifier la capacité utilisée.
5. Lire la documentation du format.
6. Tester la procédure sur une copie.
7. Vérifier le résultat avec le système invité.

Ne réduis jamais un disque en te basant uniquement sur le fait qu'il semble contenir beaucoup d'espace libre.

## 8. Gestion du stockage avec libvirt

### 8.1 Les pools de stockage

libvirt permet de gérer des pools de stockage et des volumes.

Un pool peut s'appuyer sur un répertoire, un volume logique ou un autre type de stockage pris en charge.

Lister les pools :

```bash
sudo virsh pool-list --all
```

Examiner les informations d'un pool :

```bash
sudo virsh pool-info default
```

Le nom `default` n'est qu'un exemple. Le pool doit réellement exister.

Lister les volumes d'un pool compatible :

```bash
sudo virsh vol-list --pool default
```

### 8.2 Pourquoi utiliser des pools ?

Les pools permettent d'organiser les emplacements de stockage et de simplifier certaines opérations d'allocation.

Ils aident à identifier où les disques virtuels sont stockés et à gérer leurs capacités.

Il faut toutefois distinguer la gestion logique du pool de la protection physique des données.

### 8.3 Créer un nouveau pool de type répertoire

Dans un laboratoire où le chemin de stockage est préparé :

```bash
sudo mkdir -p /srv/libvirt-images
```

Tu peux ensuite créer un fichier XML décrivant le pool, par exemple :

```xml
<pool type='dir'>
  <name>images-lab</name>
  <target>
    <path>/srv/libvirt-images</path>
  </target>
</pool>
```

Enregistre ce contenu dans un fichier tel que `/tmp/images-lab.xml`, puis définis et démarre le pool :

```bash
sudo virsh pool-define /tmp/images-lab.xml
sudo virsh pool-start images-lab
sudo virsh pool-autostart images-lab
```

Les permissions du répertoire doivent être compatibles avec l'exécution de QEMU et les contrôles de sécurité de l'hôte.

Ne rends pas le répertoire accessible en écriture à tous les utilisateurs pour résoudre un problème de permissions.

### 8.4 Examiner les disques d'une VM

```bash
sudo virsh domblklist lab-linux01
```

Cette commande montre les périphériques disque associés à la VM et leurs sources.

Avant de supprimer ou déplacer un volume, vérifie sa présence dans les définitions des VM et ses éventuelles dépendances.

### 8.5 Migrer des VM et le stockage

Une migration peut demander le déplacement de la configuration, du contenu des disques ou des deux.

Le stockage partagé simplifie certains scénarios lorsque les deux hôtes disposent d'un accès correct au même stockage.

Avec un stockage local, il peut être nécessaire de copier le disque et de vérifier sa cohérence avant de redémarrer la VM sur le nouvel hôte.

Les procédures exactes dépendent de la version, du format de disque et de la configuration réseau.

Documentation : [Administration du stockage libvirt — Red Hat](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_virtualization/managing-storage-for-virtual-machines_configuring-and-managing-virtualization).

## 9. Gestion du stockage dans Proxmox VE

### 9.1 Comprendre les types de stockage

Proxmox VE peut gérer différents types de stockage, notamment :

- Répertoire.
- LVM et LVM-thin.
- ZFS.
- NFS.
- iSCSI.
- Ceph, selon l'architecture retenue.
- D'autres types compatibles avec la version et les composants installés.

Les capacités varient selon le type de stockage : partage entre nœuds, format disque, snapshots, clones et sauvegardes.

### 9.2 Examiner les stockages

Depuis la ligne de commande :

```bash
pvesm status
```

Cette commande donne un aperçu des stockages configurés.

Pour examiner la configuration d'une VM :

```bash
qm config 101
```

Pour comprendre où se trouvent les disques, examine la configuration et l'identifiant du stockage.

### 9.3 Capacité d'un stockage local

Un stockage local est généralement attaché à un nœud donné.

Il ne devient pas automatiquement accessible depuis les autres nœuds du cluster.

Cela a une importance directe pour la migration : si la VM utilise un disque stocké sur un emplacement local, la destination doit disposer d'un mécanisme permettant de recevoir ou d'accéder à ce disque.

### 9.4 Stockage partagé

Un stockage partagé peut permettre à plusieurs nœuds d'accéder aux disques des VM dans les conditions prévues.

Cela facilite certains scénarios de migration et de disponibilité.

Cependant, le stockage partagé reste une dépendance qui doit être protégée. Il faut surveiller l'état de la baie ou du service de stockage, les chemins réseau, les permissions et la capacité disponible.

### 9.5 Examiner la configuration d'une VM

```bash
qm config 101
```

Pour vérifier l'état :

```bash
qm status 101
```

Pour lister les machines :

```bash
qm list
```

Le contenu de la configuration permet notamment d'identifier les disques et les interfaces réseau configurés.

### 9.6 Ajouter de la capacité

L'ajout d'un stockage ou d'un disque virtuel doit être préparé.

Pour une nouvelle capacité, il faut déterminer :

- Le type de stockage.
- L'espace disponible.
- Les VM concernées.
- Les besoins en performance.
- La nécessité de partager le stockage.
- Les opérations de maintenance.
- Les procédures de sauvegarde.

Ne modifie pas directement la configuration interne du stockage Proxmox en éditant des fichiers sans comprendre le mécanisme attendu par la plateforme.

## 10. Gestion du stockage dans VMware vSphere

### 10.1 Datastores

Un datastore est un emplacement de stockage utilisé par les VM et les composants vSphere pris en charge.

Il peut s'appuyer sur différentes technologies de stockage selon la version et la configuration.

Exemples courants :

- VMFS sur des périphériques compatibles.
- NFS.
- vSAN dans les architectures qui l'utilisent.
- Certaines ressources SAN ou iSCSI.

### 10.2 Ce qu'il faut surveiller

Surveille :

- L'espace libre.
- Les latences de lecture et d'écriture.
- Les chemins d'accès.
- Les erreurs de stockage.
- Les snapshots.
- La croissance des disques.
- Les tâches de consolidation.
- Les capacités restantes après une migration.

Une VM peut fonctionner normalement jusqu'à ce que le datastore se remplisse, puis rencontrer des problèmes de croissance de disque, de snapshot ou d'écriture.

### 10.3 Placement des VM

Le choix du datastore doit tenir compte de :

- La capacité.
- Les performances.
- Les exigences de disponibilité.
- Les stratégies de stockage.
- Les possibilités de migration.
- Les contraintes de licence et de plateforme.
- Les besoins de sauvegarde.

Une VM critique ne devrait pas être placée uniquement sur le datastore qui semble disposer du plus grand espace libre sans examiner ses autres caractéristiques.

### 10.4 Déplacement de stockage

Dans les architectures compatibles, Storage vMotion permet de déplacer le stockage d'une VM tout en maintenant son fonctionnement selon le scénario.

Il faut vérifier que la fonctionnalité est disponible et prise en charge, que les datastores source et destination conviennent et que la capacité ainsi que la bande passante sont suffisantes.

Une migration de stockage peut générer un trafic important. Il est préférable de la planifier et de la surveiller.

Documentation : [Base de connaissances Broadcom — Déplacement d'une machine virtuelle](https://knowledge.broadcom.com/external/article/317919/moving-or-copying-a-virtual-machine-with.html).

## 11. Templates et clones : industrialiser les déploiements

### 11.1 Le problème de la création manuelle

Si une entreprise doit créer 30 VM Linux, une installation manuelle répétée multiplie les risques d'erreur.

Les différences peuvent concerner :

- Les versions logicielles.
- Les mises à jour.
- La configuration réseau.
- Les comptes.
- Les permissions.
- Les paramètres de sécurité.
- Les outils de supervision.
- Les agents de sauvegarde.

Les templates servent à construire une base réutilisable.

### 11.2 Qu'est-ce qu'un template ?

Un template est un modèle utilisé pour créer des VM standardisées.

Il peut contenir un système d'exploitation préparé, les mises à jour nécessaires et une configuration de base.

Une image modèle doit être entretenue : si elle contient des composants vulnérables ou une configuration obsolète, chaque nouvelle VM risque de reproduire les mêmes problèmes.

### 11.3 Qu'est-ce qu'un clone ?

Un clone est une nouvelle machine virtuelle créée à partir d'une autre VM ou d'un template.

Il existe plusieurs approches :

**Clone complet**

Le clone possède son propre ensemble de disques ou de ressources selon le fonctionnement de la plateforme.

Il consomme généralement davantage d'espace, mais il peut être plus indépendant du modèle.

**Clone lié**

Le clone dépend d'une image de base et utilise des mécanismes de partage ou de référence des blocs supportés par la plateforme.

Il peut réduire la consommation de stockage, mais introduit une dépendance envers le disque de base.

La disponibilité des options dépend de l'hyperviseur et du type de stockage.

### 11.4 Préparer une VM modèle

La préparation doit comprendre :

1. Installer le système d'exploitation.
2. Appliquer les mises à jour.
3. Installer les composants nécessaires.
4. Configurer une base de sécurité.
5. Retirer les données propres à une machine individuelle lorsque nécessaire.
6. Préparer la méthode de personnalisation.
7. Éteindre la machine si le processus de création l'exige.
8. Convertir la VM en template selon la plateforme.
9. Documenter la version et la date.
10. Tester la création d'un clone.

Il faut éviter de copier des identifiants uniques, des clés privées ou des secrets qui seraient réutilisés dans toutes les nouvelles VM.

### 11.5 Personnalisation après clonage

Un clone destiné à être une machine indépendante doit recevoir une identité propre.

Cela peut concerner :

- Nom de machine.
- Adresse IP.
- MAC virtuelle selon le mécanisme utilisé.
- Identité applicative.
- Certificats.
- Clés SSH.
- Identifiants.
- Identité de supervision.
- Identité d'inscription à certains services.

Un clonage sans personnalisation peut créer des conflits réseau ou d'identité.

## 12. Templates et clones avec KVM/libvirt

### 12.1 Approche générale

Avec libvirt, un modèle peut être créé en préparant une VM de référence et en utilisant des copies de ses disques ainsi que sa configuration, dans les conditions adaptées au système invité.

Il faut décider si l'image sera :

- Un modèle complet à copier.
- Une image de base utilisée avec des fichiers dérivés.
- Une image préparée à l'aide d'un processus d'installation automatisé.

Le choix dépend du format, du stockage et des exigences d'indépendance.

### 12.2 Examiner le disque de référence

```bash
qemu-img info /var/lib/libvirt/images/template-linux.qcow2
```

Avant d'utiliser l'image, vérifie :

- Le format.
- La capacité.
- Le chemin.
- Les dépendances éventuelles.
- La présence de snapshots.
- L'état de la VM d'origine.

### 12.3 Copier un disque pour un clone complet

Dans un laboratoire où la VM source est arrêtée et son disque ne change plus :

```bash
sudo cp \
    /var/lib/libvirt/images/template-linux.qcow2 \
    /var/lib/libvirt/images/vm-linux02.qcow2
```

Cette commande copie le fichier disque. Elle ne crée pas à elle seule une VM libvirt indépendante.

Il faut aussi créer ou dupliquer une définition de VM correcte, en adaptant les éléments nécessaires à la nouvelle machine.

Ne copie jamais une image disque active au hasard : le résultat peut être incohérent.

### 12.4 Définition de la nouvelle VM

Pour une nouvelle VM, il faut notamment prévoir :

- Un nom unique.
- Un UUID distinct.
- Un chemin de disque adapté.
- Une interface réseau.
- Une adresse MAC unique.
- La mémoire et le CPU.
- Le firmware et le matériel virtuel compatibles.

La méthode recommandée est d'utiliser les outils libvirt ou un processus d'automatisation adapté plutôt que de dupliquer aveuglément tous les champs XML de l'ancienne VM.

### 12.5 Cloud-init et images cloud

Pour de nombreux systèmes Linux, une image cloud préparée pour l'initialisation automatique peut simplifier la création de VM.

Elle permet, selon le système et la plateforme, de personnaliser certains paramètres au premier démarrage.

Les informations peuvent comprendre le nom de machine, certains comptes, les clés SSH, le réseau et les commandes d'initialisation.

Il faut protéger les données de personnalisation et éviter d'injecter des secrets réutilisables dans toutes les VM.

Documentation : [Ubuntu Server — Virtualisation](https://ubuntu.com/server/docs/how-to/virtualisation/).

## 13. Templates et clones dans Proxmox VE

### 13.1 Créer une VM modèle

La méthode générale consiste à :

1. Créer une VM.
2. Installer le système.
3. Mettre le système à jour.
4. Nettoyer et préparer les éléments propres à la machine.
5. Éteindre la VM.
6. Convertir la VM en template.
7. Créer un clone à partir du template.
8. Personnaliser l'identité et la configuration du clone.

Un template doit être traité comme une référence en lecture seule selon les mécanismes de la plateforme.

### 13.2 Convertir une VM en template

La conversion peut s'effectuer depuis l'interface Web ou avec la commande adaptée.

Exemple :

```bash
qm template 9000
```

L'identifiant `9000` désigne ici une VM modèle déjà créée et éteinte selon les prérequis de la procédure.

Vérifie la configuration et l'état avant la conversion. Le comportement d'une opération sur une VM peut dépendre de la version et des paramètres de la plateforme.

### 13.3 Cloner un template

Exemple de création d'un clone complet :

```bash
qm clone 9000 101 --name VM-WEB01 --full 1
```

Cette commande utilise :

- `9000` : identifiant du template.
- `101` : nouvel identifiant.
- `--name` : nom de la nouvelle VM.
- `--full 1` : demande un clone complet.

Un clone complet demande davantage de stockage qu'un clone lié, mais il peut offrir plus d'indépendance par rapport au modèle.

Le comportement exact dépend du type de stockage et de la version de Proxmox VE.

### 13.4 Examiner la configuration du clone

```bash
qm config 101
```

Vérifie le nom, les ressources, les disques et les interfaces réseau.

Ne connecte pas immédiatement un clone à un réseau de production si son identité réseau et applicative n'a pas été adaptée.

### 13.5 Créer plusieurs clones avec une convention cohérente

Exemple de convention :

```text
TPL-LINUX-BASE
    |
    +-- VM-WEB01
    +-- VM-WEB02
    +-- VM-APP01
```

Les noms doivent refléter la fonction de la VM.

Une convention facilite l'inventaire, la supervision, la recherche et la gestion des sauvegardes.

### 13.6 Cloud-init dans Proxmox

Proxmox prend en charge certains scénarios de personnalisation automatique des VM Linux avec Cloud-init.

Cela peut faciliter :

- La création des utilisateurs.
- Le paramétrage du réseau.
- La mise en place de clés SSH.
- Certaines étapes d'initialisation.
- La génération de VM standardisées.

Les possibilités exactes dépendent de l'image invitée et de la configuration retenue.

Les secrets et clés doivent être protégés, et les opérations d'initialisation doivent être testées avant le déploiement d'un grand nombre de VM.

Documentation : [Guide d'administration Proxmox VE](https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf).

## 14. Templates et clones dans VMware vSphere

### 14.1 Préparer une VM modèle

Dans vSphere, un template peut être utilisé pour déployer des VM avec une configuration standard.

La préparation comprend généralement :

- Installation du système.
- Mises à jour.
- Configuration de référence.
- Nettoyage des données propres à la machine.
- Vérification des outils invités requis.
- Préparation de la personnalisation.
- Conversion en template.

### 14.2 Déployer depuis un template

La procédure générale consiste à :

1. Sélectionner le template.
2. Demander le déploiement d'une nouvelle VM.
3. Choisir le nom.
4. Choisir le dossier et la ressource de calcul.
5. Choisir le datastore.
6. Définir les options de personnalisation.
7. Ajuster les ressources si nécessaire.
8. Vérifier le réseau.
9. Terminer le déploiement.
10. Vérifier l'identité de la nouvelle VM.

Les options sont liées à la version de vSphere et aux composants disponibles.

### 14.3 Clonage et personnalisation

Un clone doit être personnalisé pour éviter les conflits d'identité.

La procédure peut comprendre :

- Personnalisation du système invité.
- Attribution d'une adresse ou d'une configuration DHCP appropriée.
- Contrôle du nom d'hôte.
- Contrôle des identifiants.
- Génération ou renouvellement de certaines clés.
- Vérification des agents d'administration.

Une VM clonée peut sembler démarrée tout en présentant un conflit DNS ou une identité dupliquée.

### 14.4 Bonnes pratiques de template

Un template doit être versionné et documenté.

Exemple :

```text
TPL-UBUNTU-BASE-v2026.10
|
+-- OS et mises à jour
+-- Outils d'administration
+-- Paramètres de sécurité
+-- Procédure de personnalisation
```

Le nom de version est une convention illustrative.

Il faut conserver une méthode de retrait des templates obsolètes et valider chaque nouvelle génération avant une utilisation étendue.

Documentation : [Broadcom — Déploiement depuis un template](https://knowledge.broadcom.com/external/article/412699).

## 15. Snapshots, checkpoints et restauration

### 15.1 Pourquoi un snapshot est utile

Un snapshot permet de capturer un état d'une VM selon les fonctions de la plateforme.

Il peut être pratique avant :

- Une mise à jour.
- Une modification de configuration.
- Un test applicatif.
- Une expérience de laboratoire.
- Une modification qui doit être validée rapidement.

Il ne constitue pas pour autant une sauvegarde complète indépendante.

### 15.2 Les limites d'un snapshot

Un snapshot peut conserver des dépendances envers les fichiers de base, les disques virtuels ou le stockage de la VM.

Selon la plateforme, il peut également enregistrer l'état de mémoire ou d'autres informations.

Une accumulation de snapshots peut :

- Consommer de l'espace.
- Dégrader les performances.
- Compliquer les opérations de consolidation.
- Augmenter les risques lors d'un incident de stockage.
- Rendre la gestion de la VM plus complexe.

Il faut donc prévoir une durée de conservation courte et une suppression contrôlée.

### 15.3 Snapshot et cohérence applicative

Un snapshot peut représenter un état cohérent au niveau du disque sans garantir une cohérence applicative complète.

Les bases de données et applications transactionnelles exigent une attention particulière.

La cohérence dépend notamment du système invité, du moteur de données, des outils invités et de la méthode de capture.

Pour protéger une base de données, privilégie une méthode de sauvegarde compatible avec le moteur et capable de restaurer les données selon les exigences métier.

### 15.4 Snapshots avec libvirt

Dans les environnements qui prennent en charge les snapshots correspondants, une capture peut être créée par `virsh`.

Exemple :

```bash
sudo virsh snapshot-create-as \
    lab-linux01 \
    avant-mise-a-jour \
    --description "État de référence avant mise à jour"
```

Cette commande doit être utilisée uniquement si le type de disque, la définition de VM et la version prennent en charge le type de snapshot demandé.

Vérifie les snapshots existants :

```bash
sudo virsh snapshot-list lab-linux01
```

Avant de créer ou restaurer un snapshot, vérifie la configuration et les conséquences sur les données de la VM.

### 15.5 Revenir à un snapshot

Dans les scénarios compatibles, `virsh` peut restaurer l'état d'un snapshot.

Exemple :

```bash
sudo virsh snapshot-revert \
    lab-linux01 \
    avant-mise-a-jour
```

Cette commande peut ramener la VM à un état antérieur et donc annuler des changements intervenus depuis la capture.

Ne l'exécute pas sur une machine contenant des données importantes sans avoir étudié les conséquences et préparé une sauvegarde si nécessaire.

### 15.6 Snapshots dans Proxmox VE

Proxmox permet de créer et de gérer des snapshots selon les capacités du stockage utilisé et les fonctions prises en charge par la VM.

Exemple :

```bash
qm snapshot 101 avant-update \
    --description "Avant maintenance"
```

Lister les snapshots :

```bash
qm listsnapshot 101
```

Le retour à un snapshot doit être planifié et effectué selon la version de la plateforme et les conditions de la VM.

Exemple de principe :

```bash
qm rollback 101 avant-update
```

Cette opération peut écraser l'état actuel de la VM en restaurant un état antérieur.

Avant un rollback, vérifie les écritures récentes, les données métier et la méthode de retour arrière.

### 15.7 Snapshots dans VMware

Dans vSphere, un snapshot peut être utilisé comme mécanisme de retour rapide avant une modification.

Cependant, les snapshots ne doivent pas être traités comme des sauvegardes et ne doivent généralement pas être conservés longtemps sans justification.

Broadcom recommande de gérer les snapshots comme des mécanismes opérationnels temporaires. Les fichiers delta peuvent augmenter à mesure que la VM écrit des données, jusqu'à approcher la taille du disque de base dans certains scénarios.

Documentation : [Broadcom — Bonnes pratiques pour les snapshots vSphere](https://knowledge.broadcom.com/external/article/318825/best-practices-for-using-vmware-snapshots.html).

### 15.8 Après un snapshot : quoi vérifier ?

Après une modification :

1. Vérifier le démarrage de la VM.
2. Vérifier les services.
3. Effectuer un test fonctionnel.
4. Vérifier les journaux.
5. Vérifier les données.
6. Supprimer ou consolider le snapshot selon la procédure adaptée.
7. Contrôler le stockage.
8. Documenter l'opération.

Un snapshot n'est pas un remplacement de sauvegarde.

## 16. Sauvegardes et restaurations de VM

### 16.1 Définir le périmètre de sauvegarde

Une politique de sauvegarde doit définir :

- Quelles VM sont protégées.
- La fréquence.
- La durée de rétention.
- Le stockage de destination.
- Le chiffrement éventuel.
- Les accès autorisés.
- Les objectifs RTO et RPO.
- La méthode de restauration.
- Les tests de restauration.

Une VM arrêtée, une base de données en fonctionnement et un serveur Web statique ne présentent pas nécessairement les mêmes exigences de cohérence.

### 16.2 Protéger les sauvegardes indépendamment des VM

Si les sauvegardes se trouvent uniquement sur le même stockage physique que les VM, une panne grave peut détruire les données et leurs copies.

Il faut prévoir un emplacement de sauvegarde adapté et suffisamment indépendant de l'infrastructure de production.

Pour une protection renforcée, les copies peuvent être isolées, hors ligne ou immuables selon les capacités de la solution retenue.

### 16.3 Sauvegarde avec libvirt

libvirt ne remplace pas à lui seul une stratégie de sauvegarde complète. Les mécanismes possibles varient selon les versions, les outils et les besoins de cohérence.

Pour un laboratoire, il est possible d'illustrer un archivage à partir de disques d'une VM arrêtée.

Exemple, en supposant que le chemin du disque a été vérifié :

```bash
sudo virsh shutdown lab-linux01
```

Vérifie qu'elle est arrêtée :

```bash
sudo virsh domstate lab-linux01
```

Une copie du disque peut ensuite être réalisée selon le format et la méthode appropriés.

Il faut également préserver les informations de configuration et tester la restauration de l'ensemble. Une simple copie du disque n'est pas une stratégie universelle de sauvegarde de VM.

En production, privilégie une solution de sauvegarde compatible avec les mécanismes de cohérence et les exigences applicatives.

### 16.4 Sauvegarde de VM dans Proxmox VE

Proxmox fournit l'outil `vzdump` pour sauvegarder les VM et conteneurs dans les conditions prises en charge.

Exemple pédagogique pour une VM :

```bash
vzdump 101 --storage local --mode snapshot
```

Cette commande suppose que le stockage existe et qu'il est configuré pour recevoir les sauvegardes.

Le mode de sauvegarde doit être choisi selon les capacités de la plateforme, le type de stockage et les exigences de cohérence de la VM.

Examiner le journal de la tâche pour confirmer le résultat. Ne te contente pas de voir qu'une tâche a été lancée.

### 16.5 Restaurer une VM Proxmox

La commande de restauration dépend du format de la sauvegarde et de la version de Proxmox VE.

Exemple de principe pour une archive `vzdump` compatible :

```bash
qmrestore \
    /chemin/vers/vzdump-qemu-101.vma.zst \
    201 \
    --storage local-lvm
```

Les noms de fichiers et le stockage sont fictifs.

Avant la restauration, vérifie la disponibilité de l'identifiant de destination et la capacité du stockage.

Une restauration de test vers une nouvelle VM permet de valider le résultat sans écraser immédiatement la production.

### 16.6 Proxmox Backup Server

Proxmox Backup Server peut ajouter des fonctions de gestion de sauvegarde, notamment la déduplication, la vérification et d'autres mécanismes selon l'architecture retenue.

Il faut vérifier les prérequis, les versions, le stockage et les capacités exactes disponibles.

Une solution de sauvegarde doit également être protégée par des permissions et un modèle d'administration adaptés.

Documentation : [Proxmox VE — Guide d'administration](https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf).

### 16.7 Sauvegardes VMware

Dans vSphere, la stratégie de sauvegarde peut s'appuyer sur des outils compatibles avec les mécanismes de protection des données de VMware.

Elle doit couvrir :

- Les disques virtuels.
- La configuration de la VM.
- Les données applicatives.
- Les secrets et dépendances nécessaires.
- Les points de restauration.
- La protection du stockage de sauvegarde.

Une solution de sauvegarde adaptée doit prendre en compte les exigences de cohérence applicative.

Un snapshot seul n'est pas une sauvegarde suffisante.

### 16.8 Tester une restauration complète

La procédure de validation doit comprendre :

1. Sélectionner une copie.
2. Vérifier son intégrité.
3. Restaurer la VM dans un environnement adapté.
4. Vérifier son démarrage.
5. Vérifier le réseau.
6. Contrôler les services.
7. Vérifier les données.
8. Faire valider le résultat fonctionnel.
9. Mesurer la durée.
10. Documenter les écarts.

Le test doit être suffisamment réaliste pour identifier les dépendances manquantes.

## 17. Réseaux virtuels avancés

### 17.1 Pourquoi un réseau bien conçu est indispensable

L'hyperviseur fournit des interfaces virtuelles, mais la connectivité dépend d'un ensemble de composants.

```text
Machine virtuelle
       |
       v
Interface virtuelle
       |
       v
Commutateur virtuel / bridge
       |
       v
Interface physique
       |
       v
VLAN / commutateur physique
       |
       v
Routage / pare-feu
       |
       v
Destinations réseau
```

Une erreur peut se produire à chaque niveau.

### 17.2 Séparer les réseaux

Une infrastructure peut utiliser plusieurs réseaux :

- Gestion de l'hyperviseur.
- Trafic des VM.
- Stockage.
- Migration.
- Sauvegarde.
- Administration distante.
- Laboratoire isolé.

Cette séparation peut être physique, logique ou combinée.

Un VLAN ne remplace pas toutes les garanties d'une séparation physique, mais il peut organiser les flux lorsqu'il est correctement configuré.

### 17.3 Identifier les besoins par réseau

| Réseau | Objectif | Contrôle essentiel |
|---|---|---|
| Gestion | Administrer l'hôte | Accès limité aux administrateurs |
| Production | Fournir les services | Disponibilité et segmentation |
| Stockage | Accéder aux volumes | Débit, latence et chemins |
| Migration | Déplacer les VM | Bande passante et sécurité |
| Sauvegarde | Transférer les copies | Isolation et capacité |
| Laboratoire | Tester des configurations | Absence de conflit avec la production |

Il n'est pas toujours nécessaire de créer un réseau physique distinct pour chacun de ces usages, mais le choix doit être explicite et documenté.

### 17.4 Vérifier les bridges sous Linux

Avec libvirt, examiner les réseaux :

```bash
sudo virsh net-list --all
```

Examiner les interfaces :

```bash
ip -br address
```

Examiner les bridges Linux :

```bash
bridge link
bridge vlan show
```

Ces commandes permettent d'examiner certaines informations réseau, mais elles ne remplacent pas la vérification des commutateurs physiques et des VLAN.

### 17.5 Réseau virtuel Proxmox

Proxmox utilise fréquemment les bridges Linux pour relier les VM au réseau.

Le bridge `vmbr0` est couramment utilisé pour le réseau de gestion et/ou le trafic des VM selon la configuration.

Avant de modifier un bridge :

1. Identifie l'interface physique.
2. Vérifie l'adresse de gestion.
3. Vérifie la passerelle.
4. Contrôle les VLAN.
5. Vérifie les interfaces des VM.
6. Prépare un moyen de récupération.
7. Planifie une fenêtre si l'accès distant peut être interrompu.

Une modification mal préparée peut rendre l'hôte inaccessible.

### 17.6 Réseau virtuel VMware

vSphere utilise notamment des commutateurs virtuels et des groupes de ports.

La configuration réseau doit préciser :

- Le réseau associé.
- Le VLAN.
- Les règles de sécurité.
- La connectivité physique.
- Les éventuels mécanismes de répartition de charge.
- La compatibilité avec les migrations.

Si une VM doit migrer entre plusieurs hôtes, les réseaux nécessaires doivent être cohérents sur les hôtes de destination.

### 17.7 Tester la connectivité de bout en bout

Depuis la VM :

```bash
ip -br address
ip route
getent hosts example.com
```

Tester un service :

```bash
curl -I https://example.com
```

Puis vérifier les chemins réseau et les ports pertinents.

Une VM peut posséder une adresse IP correcte sans être en mesure d'atteindre sa passerelle ou le service cible.

## 18. Migration des machines virtuelles

### 18.1 Qu'est-ce qu'une migration ?

La migration permet de déplacer une VM d'un hôte à un autre.

Elle peut être :

**À froid**

La VM est arrêtée avant le déplacement.

**À chaud**

La VM reste en fonctionnement pendant la majeure partie du transfert, avec un bref changement d'exécution possible lors de la bascule finale.

**Migration de stockage**

Les disques virtuels sont déplacés vers un autre emplacement compatible.

La disponibilité de ces fonctionnalités dépend de l'hyperviseur, du stockage, du réseau et des licences.

### 18.2 Migration à froid

La migration à froid est souvent la plus simple lorsque la VM peut être arrêtée.

Procédure générale :

1. Vérifier la VM.
2. Arrêter proprement le système invité.
3. Vérifier l'état arrêté.
4. Copier ou déplacer les ressources nécessaires.
5. Recréer ou transférer la configuration.
6. Vérifier la compatibilité de la destination.
7. Démarrer la VM.
8. Contrôler le réseau et les services.
9. Mettre à jour l'inventaire.

Cette méthode peut provoquer une interruption pendant le déplacement, mais elle évite certains risques liés au transfert de l'état mémoire en cours d'exécution.

### 18.3 Migration à chaud

La migration à chaud demande davantage de prérequis.

Il faut notamment examiner :

- La compatibilité CPU.
- Les versions des hyperviseurs.
- Le réseau de migration.
- L'authentification.
- Le stockage.
- La bande passante.
- Les ressources de la destination.
- Les périphériques passthrough éventuels.
- Les contraintes applicatives.

Une migration à chaud n'est pas forcément possible entre n'importe quels hôtes.

### 18.4 Stockage partagé

Si les deux hôtes ont accès au même stockage compatible, la migration peut être simplifiée puisque les fichiers des disques virtuels sont déjà accessibles à la destination.

Cependant, le stockage partagé constitue une dépendance : une panne de la baie ou de ses chemins peut affecter les deux hôtes.

### 18.5 Stockage local

Avec un stockage local, les disques doivent devenir accessibles à la destination par une méthode prise en charge.

Il peut être nécessaire de copier les données, d'utiliser une fonctionnalité de migration avec transfert du stockage ou de recourir à un autre mécanisme adapté.

Il faut contrôler la capacité de la destination, les performances et la cohérence des données.

### 18.6 Migration avec libvirt

libvirt et QEMU prennent en charge plusieurs scénarios de migration selon les versions, les options et les prérequis.

L'aide de `virsh` permet d'examiner les options disponibles :

```bash
virsh migrate --help
```

Une migration à chaud peut être déclenchée selon une syntaxe compatible avec la version et l'architecture utilisées.

Avant de lancer une migration, vérifie :

- La destination.
- La connectivité.
- L'authentification.
- La configuration CPU.
- Le stockage.
- Les réseaux de la VM.
- Les contraintes de la version.

Les options exactes dépendent de la configuration de libvirt et QEMU. Elles doivent être testées dans le laboratoire avant toute utilisation en production.

Documentation : [Ubuntu Server — Migration à chaud avec libvirt/QEMU](https://ubuntu.com/server/docs/explanation/virtualisation/live-migration/).

### 18.7 Migration dans Proxmox VE

Dans Proxmox, la migration peut être effectuée depuis l'interface Web ou les outils de ligne de commande.

Un exemple de commande de migration en ligne :

```bash
qm migrate 101 pve02 --online
```

Cette syntaxe doit être vérifiée sur la version installée et selon le stockage et les capacités disponibles.

La migration suppose que la destination peut accueillir la VM. Les disques, réseaux et autres dépendances doivent être traités conformément au scénario.

Avant la migration, contrôle l'état de la VM, le stockage, la configuration réseau et la capacité de `pve02`.

### 18.8 Migration dans VMware

Dans l'écosystème vSphere, vMotion permet de déplacer une VM en fonctionnement entre des hôtes compatibles dans les conditions prévues par la plateforme.

Storage vMotion peut déplacer le stockage dans les scénarios compatibles.

Les prérequis dépendent notamment :

- De la compatibilité des hôtes.
- Du réseau de migration.
- Du stockage.
- De la configuration matérielle de la VM.
- Des fonctionnalités et droits de licence disponibles.

Ne suppose pas qu'une migration est possible uniquement parce que les deux serveurs utilisent ESXi.

Documentation : [Broadcom — Déplacement ou copie d'une VM](https://knowledge.broadcom.com/external/article/317919/moving-or-copying-a-virtual-machine-with.html).

### 18.9 Après chaque migration

Vérifie :

- L'état de la VM.
- Les disques.
- Le réseau.
- Les adresses IP.
- Le DNS.
- Les services.
- Les journaux.
- Les performances.
- Les sauvegardes.
- L'inventaire.

Une migration techniquement réussie peut révéler ensuite un problème applicatif ou une dépendance oubliée.

## 19. Clusters, haute disponibilité et capacité de reprise

### 19.1 Différence entre migration et haute disponibilité

La migration est une opération de déplacement.

La haute disponibilité implique une architecture capable de réagir à certains incidents et de remettre les services en fonctionnement sur un autre hôte.

Une migration réussie ne prouve donc pas, à elle seule, que le cluster peut reprendre après une panne brutale.

### 19.2 Préparer la capacité de secours

Supposons que deux hôtes hébergent dix VM chacun.

Si un hôte tombe en panne, l'autre doit disposer des ressources nécessaires pour reprendre les VM concernées si l'objectif est de conserver tous les services.

Il faut dimensionner :

- CPU.
- Mémoire.
- Stockage.
- Réseau.
- Dépendances de stockage.
- Réseaux virtuels.
- Capacités de démarrage.

Une architecture qui ne réserve aucune capacité de secours peut réussir un test de migration planifiée et échouer lors d'une panne.

### 19.3 Clustering Proxmox

Proxmox VE permet de constituer un cluster de nœuds et fournit des fonctions de gestion des ressources selon l'architecture.

Les exigences de quorum, de réseau de cluster et de stockage doivent être respectées.

L'ajout d'un nœud à un cluster est une opération importante : la configuration du cluster est partagée et certaines configurations préexistantes peuvent être remplacées ou devenir incompatibles.

Avant d'ajouter un nœud, il faut sauvegarder les VM et vérifier les exigences de la version.

### 19.4 Clustering VMware

Dans les environnements vSphere, la haute disponibilité et la gestion de ressources reposent sur les fonctions disponibles dans l'architecture et l'offre retenues.

Les fonctionnalités doivent être vérifiées en fonction de la version et du modèle de licence.

Un cluster doit également être dimensionné pour les ressources attendues après un incident.

### 19.5 KVM/libvirt et haute disponibilité

KVM/libvirt fournit la gestion des machines virtuelles, mais un mécanisme de haute disponibilité doit être construit à partir des composants adaptés.

Selon l'architecture, cela peut nécessiter Pacemaker, Corosync, du stockage partagé ou répliqué et d'autres outils.

Une VM libvirt avec démarrage automatique n'est pas équivalente à une VM intégrée à un système complet de haute disponibilité.

### 19.6 Tests de panne

Les tests doivent examiner :

- La perte d'un hôte.
- La perte d'un réseau.
- La perte du stockage.
- L'arrêt d'une VM.
- Le redémarrage d'un nœud.
- L'occupation de ressources pendant la reprise.
- La restauration à partir d'une sauvegarde.

Les opérations qui peuvent interrompre des services doivent être réalisées en laboratoire ou selon une procédure de changement approuvée.

## 20. Automatisation de l'administration

### 20.1 Pourquoi automatiser ?

L'automatisation permet de rendre les opérations répétables.

Exemples :

- Inventorier les VM.
- Produire un rapport de capacité.
- Contrôler l'état des machines.
- Créer des VM à partir de templates.
- Vérifier l'état des sauvegardes.
- Préparer les changements.
- Collecter les journaux.

Cependant, une commande exécutée sur toutes les VM peut avoir un impact considérable.

L'automatisation doit donc intégrer des validations, la gestion des erreurs et la journalisation.

### 20.2 Inventaire KVM/libvirt

Pour lister les VM :

```bash
sudo virsh list --all
```

Pour obtenir une vue des informations d'une VM :

```bash
sudo virsh dominfo lab-linux01
```

Pour afficher les réseaux :

```bash
sudo virsh net-list --all
```

Pour examiner les pools de stockage :

```bash
sudo virsh pool-list --all
```

Ces commandes servent de base à une collecte plus complète.

### 20.3 Inventaire Proxmox

Lister les VM :

```bash
qm list
```

Examiner les stockages :

```bash
pvesm status
```

Examiner la configuration d'une VM :

```bash
qm config 101
```

Ces informations peuvent être rassemblées dans un script, à condition de traiter les erreurs et d'éviter de collecter inutilement des informations sensibles.

### 20.4 Automatisation VMware avec PowerCLI

PowerCLI permet d'administrer de nombreux éléments de vSphere par PowerShell.

Exemple d'inventaire après connexion à un serveur vCenter autorisé :

```powershell
Connect-VIServer -Server "vcenter.lab.local"

Get-VM |
    Select-Object Name,
                  PowerState,
                  NumCpu,
                  MemoryGB |
    Sort-Object Name
```

Le nom `vcenter.lab.local` est fictif.

Après la collecte, ferme la session administrative lorsque le travail est terminé :

```powershell
Disconnect-VIServer -Server "vcenter.lab.local" -Confirm:$false
```

Dans un environnement de production, la connexion doit utiliser une authentification sécurisée et un compte disposant seulement des permissions nécessaires.

### 20.5 Gérer les erreurs

Un script d'inventaire ne doit pas interrompre toute la collecte lorsqu'une VM renvoie une erreur.

Il est préférable de distinguer :

- Les résultats valides.
- Les machines inaccessibles.
- Les erreurs de permission.
- Les machines arrêtées.
- Les paramètres indisponibles.

Un rapport de gestion doit rendre ces états explicites.

### 20.6 Simuler avant d'appliquer

Avant une opération qui modifie des VM, produis un rapport ou une liste de changements prévus.

Les simulations sont importantes lorsqu'une commande peut :

- Modifier la mémoire.
- Changer des disques.
- Déplacer une VM.
- Supprimer une ressource.
- Appliquer une configuration réseau.
- Déclencher une opération à grande échelle.

Il faut vérifier le périmètre et prévoir un retour arrière.

### 20.7 Gestion de configuration

Dans une infrastructure plus grande, des outils de gestion de configuration peuvent compléter l'administration de l'hyperviseur.

Ils peuvent permettre de standardiser :

- Les systèmes invités.
- Les paramètres de service.
- Les configurations réseau.
- Les mises à jour.
- Les agents de supervision.
- Les règles de sécurité.

L'outil doit agir sur le bon niveau : une configuration de système invité ne remplace pas une configuration du stockage de l'hyperviseur.

## 21. Sécurité et gestion des accès

### 21.1 L'hyperviseur est une cible importante

L'hyperviseur contrôle les VM et peut donner accès à leurs disques et consoles.

Un compte doté de privilèges élevés sur l'hôte peut avoir la capacité de modifier ou d'interrompre plusieurs systèmes invités.

La sécurité de l'hyperviseur doit donc être traitée comme une fonction essentielle de l'infrastructure.

### 21.2 Séparer les rôles

Une organisation peut distinguer :

- Administrateur de la plateforme.
- Administrateur des VM.
- Responsable de sauvegarde.
- Administrateur réseau.
- Responsable sécurité.
- Utilisateur autorisé à consulter des rapports.

Il ne faut pas accorder un accès administrateur global à tous les techniciens si des permissions plus ciblées suffisent.

### 21.3 Protéger les interfaces d'administration

Les consoles de KVM, Proxmox et VMware doivent être accessibles uniquement par des chemins autorisés.

Mesures recommandées :

- Réseau de gestion dédié ou segmenté.
- Accès distant contrôlé.
- Authentification forte lorsque disponible.
- Restriction des comptes privilégiés.
- Journalisation.
- Mises à jour.
- Protection des certificats et secrets.

Ne publie pas directement l'interface de gestion d'un hyperviseur sur Internet sans une architecture d'accès sécurisée.

### 21.4 Sécuriser les snapshots et les disques

Les snapshots, fichiers de configuration et disques virtuels peuvent contenir des données sensibles.

Les permissions doivent être adaptées à leur usage.

Il faut éviter :

- Les copies non contrôlées sur des ordinateurs personnels.
- Les exportations de VM sans autorisation.
- Les secrets stockés dans les modèles.
- Les disques virtuels accessibles à des utilisateurs non autorisés.
- Les sauvegardes non protégées.

### 21.5 Mettre à jour l'hôte

Les mises à jour de l'hyperviseur peuvent corriger des vulnérabilités et des défauts.

Cependant, elles peuvent demander un redémarrage ou affecter la compatibilité.

Il faut donc :

1. Examiner les notes de version.
2. Vérifier les prérequis.
3. Sauvegarder les configurations nécessaires.
4. Tester les mises à jour dans le périmètre disponible.
5. Prévoir une fenêtre.
6. Contrôler les VM après mise à jour.
7. Documenter le résultat.

## 22. Planifier une maintenance d'hyperviseur

### 22.1 Pourquoi une procédure est nécessaire

Une maintenance peut affecter toutes les VM de l'hôte.

Avant l'intervention, il faut identifier :

- Les VM hébergées.
- Les services critiques.
- Les dépendances de stockage.
- Les chemins réseau.
- Les possibilités de migration.
- Les sauvegardes récentes.
- Les contacts responsables.
- Les conditions d'arrêt.

### 22.2 Maintenance d'un hôte autonome

Pour un hôte sans mécanisme de haute disponibilité, le processus peut inclure :

1. Informer les utilisateurs.
2. Vérifier les sauvegardes.
3. Arrêter ou migrer les VM lorsque cela est possible.
4. Vérifier qu'aucune charge importante ne reste active.
5. Effectuer la maintenance.
6. Redémarrer l'hôte.
7. Contrôler le réseau et le stockage.
8. Redémarrer les VM dans l'ordre prévu.
9. Valider les services.
10. Documenter l'intervention.

### 22.3 Maintenance d'un nœud de cluster

Dans un cluster, il faut en plus vérifier :

- Le quorum.
- L'état des ressources.
- La capacité restante.
- Les règles de placement.
- Le comportement des mécanismes de basculement.
- Le stockage partagé ou distribué.
- La procédure de retour du nœud.

Ne mets pas plusieurs nœuds en maintenance simultanément sans architecture ni procédure adaptées.

### 22.4 Après la maintenance

Contrôle :

- Les versions et mises à jour.
- Les services de l'hôte.
- Les réseaux virtuels.
- Les datastores ou pools de stockage.
- Les VM.
- Les performances.
- Les journaux.
- Les sauvegardes.
- La cohérence des configurations sur les autres hôtes.

Le retour au fonctionnement nominal doit être confirmé par des vérifications réelles.

## 23. Supervision et performance

### 23.1 Les métriques importantes

Pour l'hôte, mesure :

- Utilisation CPU.
- Mémoire disponible.
- Espace disque.
- Latence de stockage.
- Débit réseau.
- État matériel.
- Températures et ventilateurs lorsque les informations sont disponibles.
- État des services système.

Pour les VM, mesure :

- CPU consommé.
- Mémoire utilisée.
- Activité disque.
- Latence des disques.
- Trafic réseau.
- Erreurs applicatives.
- Disponibilité des services.

### 23.2 Distinguer charge et saturation

Une utilisation CPU élevée ne signifie pas automatiquement que la machine est en difficulté.

Il faut tenir compte de la nature de la charge et de la durée.

De même, une mémoire utilisée élevée peut être normale si elle sert efficacement de cache.

La saturation se détecte à partir d'un ensemble d'indicateurs et de leur évolution.

### 23.3 Construire une référence

Il est utile de conserver les mesures d'une période de fonctionnement normal.

Cette référence permet de comparer la charge actuelle et d'identifier les écarts.

Exemple :

```text
État normal
|
+-- CPU : plage habituelle
+-- RAM : marge suffisante
+-- Stockage : latence acceptable
+-- Réseau : absence de pertes anormales
+-- Services : fonctionnels

État dégradé
|
+-- CPU : pression durable
+-- RAM : marge presque nulle
+-- Stockage : latence élevée
+-- Réseau : erreurs ou pertes
+-- Services : temps de réponse dégradé
```

Les seuils exacts dépendent de l'application et du matériel.

### 23.4 Alertes utiles

Une supervision peut déclencher des alertes lorsque :

- L'espace libre diminue sous un seuil.
- Une VM critique devient inaccessible.
- L'hôte ne répond plus.
- Un datastore devient indisponible.
- Une sauvegarde échoue.
- Une réplication prend du retard.
- Une migration échoue.
- Les performances se dégradent durablement.

Une bonne supervision distingue l'alerte technique d'une indisponibilité métier.

## 24. Dépannage avancé

### 24.1 VM impossible à démarrer

Causes possibles :

- Manque de mémoire.
- Processeur non disponible.
- Disque inaccessible.
- Datastore indisponible.
- Configuration incompatible.
- Permission insuffisante.
- Fichier de verrouillage ou opération précédente inachevée.
- Dépendance à un périphérique absent.

Démarche :

1. Lire le message d'erreur exact.
2. Vérifier l'état de l'hôte.
3. Vérifier le stockage.
4. Examiner la configuration de la VM.
5. Contrôler les ressources disponibles.
6. Lire les journaux appropriés.
7. Corriger la cause.
8. Réessayer dans un périmètre contrôlé.

### 24.2 VM lente

Vérifie :

- CPU et mémoire.
- Paramètres de limite.
- Latence de stockage.
- Activité des autres VM.
- Réseau virtuel.
- Charge du système invité.
- Temps d'attente des applications.
- Dépendances externes.

Ne modifie pas tous les paramètres en même temps : tu risques de masquer la cause et de rendre le résultat difficile à interpréter.

### 24.3 Stockage presque plein

Un stockage presque plein peut affecter plusieurs VM simultanément.

Procédure :

1. Identifier le volume concerné.
2. Vérifier les fichiers volumineux.
3. Identifier les snapshots.
4. Vérifier les sauvegardes.
5. Examiner les disques dynamiques.
6. Déterminer la marge nécessaire.
7. Libérer de l'espace selon une procédure sûre.
8. Vérifier l'état des VM.
9. Mettre à jour la capacité suivie.

Ne supprime pas directement des fichiers de disques virtuels pour libérer de l'espace.

### 24.4 Migration refusée

Vérifie :

- Les versions des hôtes.
- La compatibilité CPU.
- Le réseau de migration.
- Le stockage.
- Les permissions.
- L'authentification.
- Les périphériques particuliers.
- La capacité de destination.
- Les snapshots.
- Les restrictions de la plateforme.

Le message d'erreur exact est souvent l'indice le plus utile.

### 24.5 Une VM ne voit plus son réseau

Vérifie :

1. Le raccordement de son interface virtuelle.
2. Le commutateur ou bridge.
3. Le VLAN.
4. L'interface physique.
5. Le DHCP ou l'adresse fixe.
6. La passerelle.
7. Les règles de pare-feu.
8. Les routes.
9. Le DNS.

Une migration entre hôtes peut révéler une différence de configuration de commutateur ou de VLAN.

### 24.6 Une VM est supprimée par erreur

Ne commence pas par réutiliser immédiatement son identifiant ni par écraser les fichiers éventuels.

Il faut vérifier :

- La présence d'une sauvegarde.
- L'état des fichiers de disque.
- L'inventaire.
- Les journaux de l'hyperviseur.
- Les points de restauration.
- Les procédures de récupération.

Une suppression de la définition de VM et une suppression des disques ne sont pas nécessairement la même opération, selon la plateforme et la méthode utilisée.

La récupération doit être effectuée à partir des informations disponibles et d'une copie de sécurité lorsque c'est possible.

## 25. Travaux pratiques guidés

Les travaux pratiques doivent être réalisés dans un environnement de laboratoire. Les opérations sur les disques, les snapshots, les réseaux et les migrations peuvent affecter les VM ; vérifie toujours le périmètre avant d'agir.

### TP 1 — Inventorier un environnement KVM/libvirt

**Objectif :** examiner les VM, leurs ressources, leurs disques et leurs réseaux.

Étapes :

1. Lister toutes les VM.
2. Examiner `dominfo` sur une VM.
3. Examiner son XML.
4. Lister ses disques.
5. Lister ses interfaces.
6. Examiner les réseaux libvirt.
7. Examiner les pools de stockage.
8. Créer un petit rapport d'inventaire.

Commandes :

```bash
sudo virsh list --all
sudo virsh dominfo lab-linux01
sudo virsh domblklist lab-linux01
sudo virsh domiflist lab-linux01
sudo virsh net-list --all
sudo virsh pool-list --all
```

**Résultat attendu :** un tableau décrivant l'état, les ressources et les dépendances de chaque VM étudiée.

### TP 2 — Modifier les ressources CPU et mémoire

**Objectif :** comprendre les modifications de ressources.

Étapes :

1. Choisir une VM non critique.
2. Relever ses ressources initiales.
3. Modifier la mémoire selon les capacités disponibles.
4. Contrôler le résultat.
5. Modifier le nombre de vCPU.
6. Redémarrer si nécessaire selon le scénario.
7. Vérifier le système invité.
8. Comparer les performances et les mesures.

Sur Proxmox, tu peux utiliser une commande de laboratoire comme :

```bash
qm set 101 --cores 2 --memory 4096
```

Le numéro et les valeurs doivent être adaptés à ta VM.

**Résultat attendu :** une fiche de modification indiquant les paramètres initiaux, les nouveaux paramètres et les vérifications.

### TP 3 — Préparer un template Proxmox

**Objectif :** standardiser la création de nouvelles VM.

Étapes :

1. Installer une VM Linux de référence.
2. Appliquer les mises à jour.
3. Vérifier la sécurité.
4. Préparer la personnalisation.
5. Éteindre la VM.
6. Convertir la VM en template.
7. Créer un clone complet.
8. Vérifier la configuration du clone.
9. Personnaliser son identité.
10. Vérifier la connectivité.

Commandes illustratives :

```bash
qm template 9000
qm clone 9000 101 --name VM-WEB01 --full 1
qm config 101
```

**Résultat attendu :** une VM créée depuis un modèle, avec une identité propre et une configuration documentée.

### TP 4 — Gérer les snapshots

**Objectif :** comprendre le retour à un état précédent.

Étapes :

1. Vérifier l'état de la VM.
2. Créer un snapshot si la plateforme et le stockage le prennent en charge.
3. Modifier un paramètre de laboratoire.
4. Vérifier le résultat.
5. Examiner les snapshots présents.
6. Décider si un retour est justifié.
7. Effectuer un rollback dans le laboratoire.
8. Vérifier l'état du système.
9. Examiner la consommation de stockage.
10. Documenter les précautions.

**Résultat attendu :** une procédure démontrant la différence entre snapshot, rollback et sauvegarde.

### TP 5 — Réaliser une sauvegarde Proxmox

**Objectif :** tester la protection des VM.

Étapes :

1. Vérifier que le stockage de sauvegarde est disponible.
2. Sélectionner une VM de laboratoire.
3. Lancer une sauvegarde.
4. Examiner les journaux.
5. Vérifier le fichier produit.
6. Restaurer vers un nouvel identifiant.
7. Démarrer la VM restaurée dans un réseau adapté.
8. Vérifier les services.
9. Mesurer la durée.
10. Documenter les résultats.

Exemple de sauvegarde :

```bash
vzdump 101 --storage local --mode snapshot
```

Le stockage doit être configuré pour recevoir les sauvegardes.

### TP 6 — Examiner la migration

**Objectif :** identifier les conditions d'une migration.

Étapes :

1. Identifier deux hôtes compatibles.
2. Comparer leur configuration.
3. Vérifier le réseau.
4. Vérifier les datastores ou pools.
5. Vérifier le stockage des disques.
6. Vérifier les permissions.
7. Étudier les prérequis de migration.
8. Réaliser une migration de laboratoire si l'environnement le permet.
9. Vérifier le réseau et les services.
10. Documenter les résultats.

**Résultat attendu :** un rapport indiquant les prérequis vérifiés, la méthode utilisée et les tests effectués après migration.

### TP 7 — Construire un inventaire de capacité

**Objectif :** déterminer si l'hôte dispose d'une marge suffisante.

Étapes :

1. Inventorier les VM.
2. Relever CPU et mémoire configurés.
3. Examiner les ressources physiques de l'hôte.
4. Mesurer les pointes d'utilisation.
5. Examiner l'espace disque.
6. Identifier les VM surdimensionnées.
7. Identifier les VM sous-dimensionnées.
8. Produire des recommandations.
9. Tester une modification.
10. Mesurer les résultats.

**Résultat attendu :** un rapport argumenté de capacité.

## 26. Exercices avec corrigés

### Exercice 1 — Surallocation CPU

Un hôte dispose de huit cœurs physiques. Les VM ont au total vingt vCPU configurés.

**Question :** l'hôte est-il nécessairement saturé ?

**Corrigé :** non. Le nombre de vCPU configurés n'est pas équivalent à une consommation permanente. Il faut analyser les charges, la concurrence et les métriques de performance. Toutefois, lorsque toutes les VM demandent simultanément une forte capacité, la surallocation peut provoquer une contention.

### Exercice 2 — Mémoire insuffisante

Un hôte possède 16 Gio de RAM et l'administrateur attribue 16 Gio à une VM, sans compter les besoins de l'hôte.

**Question :** quel est le risque ?

**Corrigé :** la VM et l'hôte peuvent se retrouver en concurrence pour la mémoire. Il faut conserver une marge et vérifier le comportement de l'hyperviseur et des autres VM. Le paramétrage doit tenir compte de la mémoire réellement disponible et non seulement de la capacité nominale.

### Exercice 3 — Template cloné sans personnalisation

Une VM Linux est clonée dix fois. Toutes les instances utilisent la même identité réseau ou des paramètres d'identité dupliqués.

**Question :** quelles conséquences sont possibles ?

**Corrigé :** conflits de noms, d'adresses IP, de clés, d'enregistrements DNS ou d'identité applicative. Le template doit être préparé avec une méthode de personnalisation adaptée avant la mise en réseau des clones.

### Exercice 4 — Snapshot conservé longtemps

Une VM contient plusieurs snapshots anciens, et le stockage se remplit progressivement.

**Question :** pourquoi cette situation est-elle risquée ?

**Corrigé :** les fichiers de changements peuvent croître et consommer de l'espace. Les opérations de consolidation ou de restauration peuvent devenir plus complexes. Il faut examiner les snapshots, prévoir une procédure de consolidation adaptée et maintenir une marge de stockage.

### Exercice 5 — Migration impossible

Une VM ne peut pas migrer vers un autre hôte.

**Question :** quelles vérifications réaliser ?

**Corrigé :** contrôler la compatibilité CPU, les versions, le réseau, le stockage, les permissions et les restrictions de la plateforme. Examiner aussi les périphériques spécifiques et les paramètres de migration.

### Exercice 6 — Disque dynamique

Une VM possède un disque virtuel annoncé à 200 Gio, mais le système de fichiers de l'hôte n'a plus que 10 Gio libres.

**Question :** pourquoi est-ce dangereux ?

**Corrigé :** le disque virtuel peut encore avoir besoin de grandir. Si l'hôte manque d'espace, les écritures, snapshots ou opérations de maintenance peuvent échouer. La capacité physique doit être surveillée indépendamment de la capacité virtuelle.

### Exercice 7 — Sauvegarde sur le même stockage

Une entreprise conserve les sauvegardes sur le même stockage physique que les VM.

**Question :** quel est le risque ?

**Corrigé :** une panne ou une corruption du stockage peut affecter simultanément les VM et leurs sauvegardes. Il faut une copie suffisamment indépendante et une restauration régulièrement testée.

### Exercice 8 — VM lente malgré un CPU peu chargé

La VM présente une latence applicative importante, mais l'utilisation CPU paraît faible.

**Question :** quelles autres ressources examiner ?

**Corrigé :** mémoire, attentes disque, latence réseau, dépendances, bases de données et limites administratives. Le CPU n'est qu'un indicateur parmi d'autres.

### Exercice 9 — VM inaccessible après migration

Une VM démarre sur le nouvel hôte, mais les clients ne peuvent plus la joindre.

**Question :** que faut-il vérifier ?

**Corrigé :** le réseau virtuel cible, les bridges ou commutateurs, les VLAN, la carte physique, les routes, les règles de pare-feu et la configuration IP de la VM. Il faut comparer la configuration source et destination.

### Exercice 10 — Snapshot présenté comme sauvegarde

Un administrateur prétend qu'un snapshot suffit pour protéger une VM en production.

**Question :** pourquoi est-ce incorrect ?

**Corrigé :** un snapshot peut dépendre des fichiers de la VM et du même stockage. Il ne garantit pas une copie indépendante ni une restauration après perte du stockage. Une stratégie de sauvegarde distincte est nécessaire.

## 27. Projet de synthèse — Industrialiser la gestion des VM

### 27.1 Contexte

Une entreprise utilise un hyperviseur pour héberger :

- Deux serveurs Web.
- Une base de données de test.
- Un serveur d'administration.
- Un serveur de supervision.
- Plusieurs VM de laboratoire.

Elle souhaite standardiser les VM, améliorer les performances et disposer d'une stratégie de sauvegarde et de migration.

### 27.2 Architecture cible

```text
              PLATEFORME DE VIRTUALISATION
                          |
                 +--------+--------+
                 |                 |
                 v                 v
              Gestion          Stockage
                 |                 |
                 v                 v
             Inventaire       Disques virtuels
                 |
        +--------+--------+--------+
        |        |        |        |
        v        v        v        v
      WEB01    WEB02     DB01    MON01
        |
        v
      Réseau applicatif

En complément :
  Templates
  Sauvegardes indépendantes
  Documentation
  Contrôles de performance
  Procédures de migration
```

### 27.3 Travail demandé

Le dossier devra comporter :

1. Un inventaire des VM.
2. Une fiche technique pour chaque machine importante.
3. Un tableau de dimensionnement CPU et RAM.
4. Une cartographie du stockage.
5. Une cartographie réseau.
6. Une convention de nommage.
7. Un template de référence.
8. Un processus de clonage.
9. Une procédure de sauvegarde.
10. Une procédure de restauration.
11. Un processus de migration.
12. Une procédure de maintenance.
13. Des contrôles de performance.
14. Un plan de sécurité.
15. Une documentation de retour arrière.

### 27.4 Critères de réussite

Le projet est réussi si :

- Les VM possèdent des configurations documentées.
- Les ressources sont dimensionnées à partir des besoins.
- Les templates produisent des VM distinctes.
- Les réseaux sont cohérents entre les hôtes.
- Les disques sont stockés aux emplacements prévus.
- Les sauvegardes sont indépendantes et vérifiées.
- Une restauration a été testée.
- La migration a été étudiée ou validée dans un laboratoire.
- Les opérations administratives sont reproductibles.
- Les incidents peuvent être diagnostiqués à partir des journaux et des mesures.

## 28. Défi final — Exploiter un parc de virtualisation

Une entreprise possède deux hôtes de virtualisation et héberge plusieurs dizaines de VM Linux et Windows.

Les problèmes constatés sont :

- Des VM surdimensionnées.
- Des disques presque pleins.
- Des snapshots anciens.
- Des sauvegardes rarement restaurées en test.
- Des configurations réseau différentes entre les hôtes.
- Des migrations qui échouent.
- Des templates obsolètes.
- Une documentation incomplète.

Tu dois définir un plan d'amélioration comprenant :

### Partie A — Inventaire

Recense les VM, leurs ressources, leur criticité, leur propriétaire, leurs disques et leurs dépendances.

### Partie B — Capacité

Analyse les ressources CPU, mémoire, stockage et réseau. Identifie les VM surdimensionnées et celles qui subissent une pression de ressources.

### Partie C — Standardisation

Construis une procédure de préparation de template et de création de clones.

### Partie D — Protection

Définis une stratégie de snapshots opérationnels et une stratégie de sauvegarde indépendante.

### Partie E — Migration

Détermine les prérequis pour migrer les VM, les réseaux et les données.

### Partie F — Exploitation

Écris les procédures de maintenance, de diagnostic, de restauration et de retour arrière.

### Partie G — Validation

Définis les résultats attendus et les preuves à collecter. Le plan doit être mesurable et reproductible.

## 29. Fiche de référence opérationnelle

| Besoin | KVM/libvirt | Proxmox VE | VMware vSphere |
|---|---|---|---|
| Lister les VM | `virsh list --all` | `qm list` | Interface ou PowerCLI |
| Examiner une VM | `virsh dominfo` | `qm config` | Propriétés de la VM |
| Démarrer une VM | `virsh start` | `qm start` | Action Power On |
| Arrêt propre | `virsh shutdown` | `qm shutdown` | Action Shutdown Guest si disponible |
| Examiner le réseau | `virsh net-list --all` | Configuration réseau / bridges | Commutateurs et groupes de ports |
| Examiner le stockage | `virsh pool-list --all` | `pvesm status` | Datastores |
| Template | Modèle géré par le processus libvirt | `qm template` | Template vSphere |
| Clone | Copie ou mécanisme d'image adapté | `qm clone` | Clone ou déploiement depuis template |
| Snapshot | `virsh snapshot-list` si compatible | `qm listsnapshot` | Snapshots de la VM |
| Sauvegarde | Solution adaptée à libvirt/QEMU | `vzdump` / Proxmox Backup Server | Solution compatible avec vSphere |
| Migration | `virsh migrate` si prérequis satisfaits | `qm migrate` | vMotion et migration de stockage selon disponibilité |
| Inventaire automatisé | `virsh` / API libvirt | CLI/API Proxmox | PowerCLI / API vSphere |

Les commandes et les capacités exactes varient selon la version et la configuration.

## 30. Bonnes pratiques à retenir

### Gestion des VM

- Documente les VM et leurs responsables.
- Standardise les noms.
- Utilise des templates validés.
- Personnalise les identités après clonage.
- Maintiens les systèmes invités à jour.
- Supprime les VM obsolètes selon une procédure contrôlée.

### CPU et mémoire

- Dimensionne selon les charges mesurées.
- Évite de surallouer sans surveiller.
- Examine les limites et réservations.
- Conserve une marge pour l'hôte.
- Contrôle les performances après modification.

### Stockage

- Surveille l'espace physique disponible.
- Sépare les besoins de capacité et de performance.
- Documente les disques.
- Ne supprime pas des fichiers de VM à la main.
- Prépare les modifications de stockage.
- Teste la restauration.

### Snapshots et sauvegardes

- Utilise les snapshots pour des besoins opérationnels temporaires.
- Évite de conserver des snapshots anciens sans justification.
- Maintiens une sauvegarde indépendante.
- Protège les copies.
- Teste régulièrement les restaurations.

### Réseau

- Documente les bridges, commutateurs et VLAN.
- Vérifie la cohérence entre les hôtes.
- Sépare les réseaux selon les exigences.
- Contrôle la connectivité de bout en bout.
- Protège l'accès à l'administration.

### Migration et maintenance

- Vérifie la compatibilité avant de migrer.
- Prépare les ressources de destination.
- Vérifie le stockage et les réseaux.
- Planifie les opérations à forte consommation de bande passante.
- Contrôle la VM après migration.
- Prévois une procédure de retour arrière.

### Sécurité

- Limite les privilèges.
- Protège les interfaces de gestion.
- Sépare la production et les laboratoires.
- Protège les secrets.
- Mets à jour l'hyperviseur.
- Sauvegarde la configuration.
- Conserve les journaux nécessaires au diagnostic.

## 31. Glossaire

**VM — Virtual Machine :** machine virtuelle exécutant un système invité.

**Hyperviseur :** couche permettant de créer, exécuter et administrer des machines virtuelles.

**vCPU :** processeur virtuel présenté à une VM.

**Surallocation :** attribution de ressources virtuelles supérieure à une capacité physique donnée.

**Réservation :** capacité minimale de ressources prévue pour un objet selon la configuration de la plateforme.

**Limite :** plafond de consommation d'une ressource.

**Shares :** mécanisme de priorité relative utilisé lors de la concurrence entre ressources.

**Pool de stockage :** ensemble de ressources de stockage géré par une plateforme de virtualisation.

**Datastore :** emplacement de stockage de ressources de VM dans VMware vSphere.

**QCOW2 :** format d'image disque utilisé notamment avec QEMU.

**Template :** modèle utilisé pour créer des VM standardisées.

**Clone complet :** copie de VM disposant de ses propres ressources de stockage selon le mécanisme de la plateforme.

**Clone lié :** clone reposant sur un disque ou une image de base partagée.

**Snapshot :** capture d'un état de VM utilisée notamment pour certains retours arrière opérationnels.

**Sauvegarde :** copie conservée afin de restaurer des données ou une machine.

**Migration à froid :** migration réalisée lorsque la VM est arrêtée.

**Migration à chaud :** migration d'une VM en fonctionnement, dans les conditions prévues par la plateforme.

**Stockage partagé :** stockage accessible depuis plusieurs hôtes selon l'architecture.

**vMotion :** technologie VMware de migration de machines virtuelles en fonctionnement dans les scénarios pris en charge.

**Storage vMotion :** mécanisme de déplacement du stockage de VM dans les scénarios vSphere compatibles.

**Bridge :** commutateur logiciel reliant des interfaces réseau virtuelles et physiques.

**Datastore saturation :** situation où la capacité de stockage disponible devient insuffisante pour les VM et les opérations prévues.

## 32. Documentation officielle

### KVM, QEMU et libvirt

- [Documentation Ubuntu Server — Virtualisation](https://ubuntu.com/server/docs/how-to/virtualisation/)
- [Libvirt — Gestion des machines virtuelles](https://ubuntu.com/server/docs/how-to/virtualisation/libvirt/)
- [Migration à chaud avec libvirt/QEMU](https://ubuntu.com/server/docs/explanation/virtualisation/live-migration/)
- [Documentation de `virsh`](https://www.libvirt.org/manpages/virsh.html)
- [Documentation QEMU](https://www.qemu.org/docs/master/)
- [Documentation du noyau Linux — KVM](https://docs.kernel.org/virt/kvm/api.html)
- [Administration du stockage virtuel RHEL 9](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_virtualization/managing-storage-for-virtual-machines_configuring-and-managing-virtualization)
- [Migration de machines virtuelles RHEL 9](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_virtualization/migrating-virtual-machines_configuring-and-managing-virtualization)

### Proxmox VE

- [Guide officiel d'administration Proxmox VE](https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf)
- [Documentation de Proxmox VE](https://www.proxmox.com/en/downloads/proxmox-virtual-environment/documentation)
- [Présentation des fonctions de Proxmox VE](https://proxmox.com/en/products/proxmox-virtual-environment/features)

### VMware vSphere

- [Plateforme VMware vSphere](https://www.vmware.com/products/cloud-infrastructure/vsphere)
- [Base de connaissances Broadcom](https://knowledge.broadcom.com/)
- [Bonnes pratiques pour les snapshots vSphere](https://knowledge.broadcom.com/external/article/318825/best-practices-for-using-vmware-snapshots.html)
- [Déplacement ou copie d'une VM VMware](https://knowledge.broadcom.com/external/article/317919/moving-or-copying-a-virtual-machine-with.html)

Les prérequis, options, fonctionnalités et droits de licence doivent être vérifiés pour la version réellement utilisée avant toute opération en production.

## Conclusion

La gestion avancée d'un hyperviseur demande bien plus que la création d'une VM. Elle nécessite une approche structurée de l'inventaire, du dimensionnement, du stockage, du réseau, des templates, des sauvegardes et des migrations.

KVM/libvirt offre un contrôle flexible des machines virtuelles sous Linux. Proxmox VE intègre ces fonctions dans une plateforme d'administration cohérente. VMware vSphere propose des mécanismes de gestion des ressources, des datastores et des migrations adaptés aux environnements pris en charge.

La maîtrise de ces technologies repose sur les mêmes principes : dimensionner à partir de mesures, standardiser les configurations, protéger les données, valider les changements et conserver des procédures de récupération.

**La règle essentielle du niveau intermédiaire est la suivante : toute opération sur une VM doit être préparée, vérifiée et documentée, avec une compréhension claire de ses effets sur les ressources, le réseau, le stockage et la disponibilité du service.**