# Virtualisation : KVM, Proxmox et VMware
## Cours débutant — Hyperviseurs, machines virtuelles, stockage et réseaux virtuels

## 1. Présentation du cours

### 1.1 Objectif général

La virtualisation est une technologie fondamentale des infrastructures informatiques modernes. Elle permet d'exécuter plusieurs systèmes d'exploitation sur un même serveur physique en leur présentant du matériel virtuel.

Plutôt que d'acheter un ordinateur distinct pour chaque application, une entreprise peut utiliser un serveur physique suffisamment puissant pour héberger plusieurs machines virtuelles, chacune avec son système d'exploitation, ses ressources et ses services.

Cette approche facilite notamment :

- La consolidation des serveurs.
- La création d'environnements de test.
- Le déploiement rapide de systèmes.
- L'isolation de certains services.
- La sauvegarde et la restauration de machines.
- La préparation de migrations.
- L'automatisation de l'administration.
- La mise en place d'infrastructures de haute disponibilité lorsque les composants nécessaires sont prévus.

Ce cours présente trois environnements importants :

**KVM**

Technologie de virtualisation intégrée au noyau Linux, généralement utilisée avec QEMU pour exécuter des machines virtuelles et avec libvirt pour les administrer.

**Proxmox Virtual Environment (Proxmox VE)**

Plateforme de virtualisation basée sur Debian, KVM/QEMU et les conteneurs Linux. Elle fournit une interface Web, des outils d'administration, des fonctions de sauvegarde et des possibilités de clustering.

**VMware**

Écosystème de virtualisation comprenant notamment les hyperviseurs de bureau VMware Workstation et VMware Fusion, ainsi que la plateforme serveur VMware vSphere avec ESXi et, selon l'architecture, vCenter Server.

Ces environnements ont des points communs, mais leurs composants et leurs méthodes d'administration diffèrent.

### 1.2 Objectifs pédagogiques

À la fin du cours, tu devras être capable de :

- Définir la virtualisation et expliquer son fonctionnement.
- Distinguer une machine physique d'une machine virtuelle.
- Comprendre la différence entre hyperviseur de type 1 et de type 2.
- Distinguer virtualisation complète et conteneurisation.
- Identifier les rôles de KVM, QEMU et libvirt.
- Comprendre le fonctionnement de Proxmox VE.
- Identifier les composants principaux de VMware vSphere.
- Préparer un ordinateur pour accueillir des machines virtuelles.
- Vérifier la prise en charge de la virtualisation matérielle.
- Installer les composants KVM sur Ubuntu Server.
- Créer une machine virtuelle avec les outils Linux.
- Administrer une VM avec `virsh`.
- Comprendre la création d'une VM dans Proxmox.
- Comprendre la création d'une VM dans VMware vSphere.
- Distinguer NAT, réseau ponté et réseau isolé.
- Comprendre les disques virtuels et leurs formats.
- Dimensionner la mémoire et le processeur des machines virtuelles.
- Comprendre la différence entre checkpoint, snapshot et sauvegarde.
- Effectuer les opérations courantes de démarrage, d'arrêt et de supervision.
- Diagnostiquer les problèmes courants.
- Appliquer les premières bonnes pratiques de sécurité.

### 1.3 Prérequis

Il est utile de connaître :

- Les bases de Windows ou Linux.
- Les notions de processeur, mémoire vive et stockage.
- Les systèmes de fichiers.
- Les adresses IP et les sous-réseaux.
- Les notions de routeur, commutateur et pare-feu.
- Les bases de l'installation d'un système d'exploitation.
- L'utilisation élémentaire d'un terminal.

Les travaux pratiques utiliseront principalement Linux et des machines virtuelles de laboratoire. Les concepts s'appliquent également aux environnements Windows et aux infrastructures VMware.

### 1.4 Matériel pédagogique recommandé

Pour commencer avec une seule machine physique, voici une configuration indicative :

| Ressource | Configuration minimale pédagogique | Configuration plus confortable |
|---|---|---|
| Processeur | 4 cœurs compatibles avec la virtualisation | 6 à 8 cœurs ou davantage |
| Mémoire vive | 8 Go pour des tests limités | 16 à 32 Go |
| Stockage | 100 Go libres | SSD avec 250 Go libres ou davantage |
| Réseau | 1 interface Ethernet ou Wi-Fi | Ethernet, éventuellement plusieurs interfaces |
| Système | Linux ou Windows compatible | Machine dédiée à la virtualisation |
| Connexion Internet | Utile pour télécharger les ISO et mises à jour | Recommandée |

Ces valeurs sont indicatives. Le besoin réel dépend du système hôte, du nombre de VM, de leur mémoire attribuée et de la charge de travail.

**Attention :** installer un hyperviseur serveur directement sur un disque peut effacer son contenu. Toute installation sur une machine physique doit être précédée d'une sauvegarde des données à conserver.

## 2. Comprendre la virtualisation

### 2.1 Qu'est-ce que la virtualisation ?

La virtualisation consiste à présenter des ressources informatiques abstraites à des systèmes invités.

Le serveur physique dispose de ressources réelles :

- Processeur.
- Mémoire vive.
- Stockage.
- Cartes réseau.
- Contrôleurs.
- Interfaces d'entrée et de sortie.

L'hyperviseur permet de partager ou d'attribuer ces ressources à plusieurs environnements virtuels.

Chaque machine virtuelle utilise son propre système d'exploitation et voit des composants matériels virtuels.

### 2.2 Architecture sans virtualisation

Imaginons une entreprise avec trois serveurs physiques :

```text
SERVEUR PHYSIQUE 1
|
+-- Système Linux
+-- Serveur Web


SERVEUR PHYSIQUE 2
|
+-- Système Linux
+-- Base de données


SERVEUR PHYSIQUE 3
|
+-- Système Windows Server
+-- Application métier
```

Chaque service dépend de sa propre machine physique.

Cette architecture est simple à comprendre, mais elle peut entraîner une utilisation insuffisante des ressources.

Par exemple, un serveur Web peut consommer très peu de CPU pendant la nuit alors que le matériel reste dédié à ce service.

### 2.3 Architecture avec virtualisation

Avec la virtualisation, les trois systèmes peuvent être hébergés par un serveur physique suffisamment dimensionné :

```text
                 SERVEUR PHYSIQUE
        +----------------------------------+
        | CPU / RAM / Stockage / Réseau    |
        +----------------------------------+
                        |
                        v
                  HYPERVISEUR
        +----------------------------------+
        | Gestion des ressources virtuelles|
        +----------------------------------+
              |          |          |
              v          v          v
         +---------+ +---------+ +---------+
         | VM-WEB  | | VM-DB   | | VM-APP  |
         | Linux   | | Linux   | | Windows |
         +---------+ +---------+ +---------+
```

Chaque VM possède ses propres paramètres de CPU, mémoire, disques virtuels et cartes réseau.

L'hyperviseur gère l'utilisation des ressources physiques.

### 2.4 Ce que la virtualisation améliore

La virtualisation peut faciliter :

**La consolidation**

Plusieurs systèmes peuvent partager un serveur physique.

**La flexibilité**

Une nouvelle VM peut être créée à partir d'une image ou d'un support d'installation sans devoir acheter un nouveau serveur.

**L'isolation**

Les machines virtuelles possèdent des environnements distincts, même si elles partagent le même matériel physique.

Cette isolation n'est toutefois pas absolue : les systèmes partagent l'hyperviseur, le matériel et certaines ressources communes.

**La portabilité**

Les fichiers et la configuration d'une VM peuvent parfois être déplacés vers un autre hôte compatible.

**La récupération**

Des solutions adaptées permettent de sauvegarder une VM et de la restaurer sur un environnement compatible.

**Le test**

Une VM peut servir à tester un système, une mise à jour ou une configuration avant le déploiement en production.

### 2.5 Les limites de la virtualisation

La virtualisation n'apporte pas uniquement des avantages.

Elle introduit aussi des risques et des exigences supplémentaires :

- Saturation du processeur ou de la mémoire.
- Panne de l'hôte physique affectant plusieurs VM.
- Défaillance du stockage commun.
- Mauvaise configuration réseau.
- Complexité de sauvegarde.
- Besoin de gérer les mises à jour de l'hôte et des systèmes invités.
- Risques liés aux permissions d'administration.
- Dépendances entre les VM.
- Coûts de licences selon les produits et systèmes invités.
- Risques de sécurité liés à une mauvaise isolation.

Si un serveur physique héberge dix machines virtuelles, une panne de cet hôte peut affecter les dix VM simultanément.

Il est donc important de distinguer la consolidation des serveurs et la haute disponibilité.

## 3. Comprendre l'hyperviseur

### 3.1 Qu'est-ce qu'un hyperviseur ?

Un hyperviseur est une couche logicielle permettant d'exécuter et de gérer des machines virtuelles.

Il contrôle notamment :

- L'accès aux processeurs.
- L'attribution de mémoire.
- Les périphériques virtuels.
- Les disques des machines.
- Les interfaces réseau.
- L'exécution et l'arrêt des VM.

### 3.2 Hyperviseur de type 1

Un hyperviseur de type 1 s'exécute directement sur le matériel ou utilise une architecture de virtualisation serveur dédiée.

Exemples de plateformes :

- VMware ESXi.
- Proxmox VE, qui installe un système hôte basé sur Linux et s'appuie sur KVM pour les VM.
- Hyper-V dans ses configurations serveur.

Schéma :

```text
       +------------------------------+
       | Machine virtuelle 1           |
       +------------------------------+
       | Machine virtuelle 2           |
       +------------------------------+
       | Machine virtuelle 3           |
       +------------------------------+
                      |
                      v
       +------------------------------+
       | Hyperviseur et système hôte   |
       | selon la plateforme           |
       +------------------------------+
                      |
                      v
       +------------------------------+
       | Matériel physique             |
       +------------------------------+
```

La représentation simplifie l'architecture. Proxmox VE n'est pas un hyperviseur autonome distinct de Linux : c'est une plateforme complète utilisant KVM/QEMU, des composants Linux et une couche d'administration intégrée.

### 3.3 Hyperviseur de type 2

Un hyperviseur de type 2 fonctionne comme une application sur un système d'exploitation existant.

Exemple :

```text
       +------------------------------+
       | VM Linux                     |
       +------------------------------+
       | VM Windows                   |
       +------------------------------+
                      |
                      v
       +------------------------------+
       | VMware Workstation            |
       | ou autre hyperviseur bureau  |
       +------------------------------+
                      |
                      v
       +------------------------------+
       | Windows ou Linux hôte         |
       +------------------------------+
                      |
                      v
       +------------------------------+
       | Matériel physique             |
       +------------------------------+
```

Cette solution est très pratique pour apprendre, créer des laboratoires et tester plusieurs systèmes sur un ordinateur.

Elle ajoute néanmoins une dépendance au système hôte, à ses pilotes, à sa stabilité et à ses ressources.

### 3.4 Comparaison des deux types

| Critère | Type 1 / plateforme serveur | Type 2 / hyperviseur de bureau |
|---|---|---|
| Usage courant | Serveurs et infrastructures | Laboratoire et poste de travail |
| Installation | Sur matériel dédié ou plateforme serveur adaptée | Comme application sur un OS existant |
| Administration centralisée | Selon la plateforme | Selon le produit |
| Dépendance au système hôte de bureau | Généralement non | Oui |
| Utilisation pédagogique | Très bonne | Très bonne |
| Haute disponibilité | Selon les fonctions et l'architecture | Généralement limitée sans plateforme supplémentaire |

La distinction est utile, mais toutes les plateformes ne se résument pas à cette classification.

## 4. Machine virtuelle et conteneur

### 4.1 Machine virtuelle

Une machine virtuelle possède son propre système d'exploitation invité.

Exemple :

```text
HÔTE LINUX
|
+-- VM 1
|   +-- Noyau invité
|   +-- Système Linux
|   +-- Applications
|
+-- VM 2
|   +-- Noyau invité
|   +-- Système Windows
|   +-- Applications
```

Une VM peut exécuter un système d'exploitation différent de celui de l'hôte lorsque l'hyperviseur prend en charge l'architecture et le système invités.

### 4.2 Conteneur système

Un conteneur Linux traditionnel partage le noyau de l'hôte.

Il isole principalement les processus, l'environnement et certaines ressources du système.

```text
HÔTE LINUX
|
+-- Noyau Linux partagé
|
+-- Conteneur 1
|   +-- Processus
|   +-- Bibliothèques
|   +-- Système de fichiers isolé
|
+-- Conteneur 2
    +-- Processus
    +-- Bibliothèques
    +-- Système de fichiers isolé
```

Les conteneurs peuvent démarrer plus rapidement et consommer moins de ressources que des VM comparables.

Cependant, les conteneurs système Linux partagent le noyau Linux de l'hôte. Ils ne constituent pas un moyen direct d'exécuter un noyau Windows dans un conteneur Linux classique.

### 4.3 Différences essentielles

| Critère | Machine virtuelle | Conteneur système Linux |
|---|---|---|
| Noyau | Noyau invité indépendant | Noyau de l'hôte partagé |
| Système invité | Peut être différent de celui de l'hôte selon la plateforme | Dépend du noyau hôte |
| Consommation | Plus élevée en général | Plus faible en général |
| Démarrage | Plus long en général | Souvent plus rapide |
| Isolation | Frontière d'isolation de VM | Isolation par les mécanismes Linux |
| Usage | Systèmes complets, services, environnements mixtes | Services Linux et environnements applicatifs compatibles |

Les VM et les conteneurs sont complémentaires. Le choix dépend des objectifs.

### 4.4 Proxmox et les conteneurs LXC

Proxmox VE gère deux grandes catégories de charges :

- Les machines virtuelles QEMU/KVM.
- Les conteneurs système Linux LXC, administrés par les outils Proxmox.

Les conteneurs LXC sont étroitement intégrés à la plateforme et peuvent bénéficier des mécanismes de gestion, de stockage, de sauvegarde et de cluster disponibles selon la version et le scénario.

Ne confonds pas les conteneurs LXC de Proxmox avec tous les conteneurs applicatifs au format OCI ni avec un logiciel d'orchestration comme Kubernetes.

Pour débuter, une VM offre souvent un modèle plus proche d'un serveur physique traditionnel et plus simple à comprendre lorsque le besoin est d'installer un système d'exploitation complet.

## 5. Comprendre CPU, mémoire et stockage virtuels

### 5.1 Le processeur physique

Le processeur physique exécute les instructions et fournit les cœurs et capacités de calcul réels.

Les processeurs compatibles avec la virtualisation disposent généralement d'extensions matérielles adaptées, notamment Intel VT-x ou AMD-V pour les architectures x86 compatibles.

Ces fonctions doivent être prises en charge par le matériel et peuvent nécessiter une activation dans le firmware UEFI/BIOS.

### 5.2 Le processeur virtuel

Une VM dispose d'un ou de plusieurs processeurs virtuels, souvent notés vCPU.

Exemple :

```text
Processeur physique
|
+-- Cœurs et ressources réelles
       |
       v
   Hyperviseur
       |
       +-- VM-WEB : 2 vCPU
       +-- VM-DB  : 4 vCPU
       +-- VM-APP : 2 vCPU
```

Dans cet exemple, huit vCPU sont attribués au total. Cela ne signifie pas automatiquement que le serveur physique possède huit cœurs indépendants réservés à ces VM.

L'hyperviseur planifie leur exécution sur le processeur physique.

L'attribution de vCPU doit être cohérente avec la charge de travail.

### 5.3 La mémoire vive

La mémoire est une ressource essentielle.

Supposons qu'un hôte dispose de 16 Go de RAM :

| Utilisation | Mémoire |
|---|---:|
| Système hôte et services | 3 Go |
| VM Linux 1 | 2 Go |
| VM Linux 2 | 2 Go |
| VM Windows | 4 Go |
| VM de laboratoire | 2 Go |
| Réserve restante approximative | 3 Go |

Cet exemple illustre une répartition possible. Il faut mesurer la consommation réelle du système hôte et des VM.

Ne donne pas systématiquement toute la mémoire disponible aux machines virtuelles. L'hôte et les opérations de virtualisation doivent conserver une marge suffisante.

### 5.4 Surallocation

La surallocation consiste à attribuer une quantité de ressources virtuelles supérieure à certaines capacités physiques disponibles.

Par exemple, plusieurs VM peuvent avoir chacune quatre vCPU alors que le serveur possède moins de cœurs physiques que la somme des vCPU.

Cela peut fonctionner lorsque les charges sont variables et que toutes les VM n'utilisent pas simultanément leur maximum.

Cependant, la surallocation peut provoquer des ralentissements lorsque la demande globale dépasse la capacité physique.

Il faut donc surveiller les charges et choisir une stratégie qui tient compte des périodes de pointe.

### 5.5 Stockage virtuel

Une VM utilise généralement un ou plusieurs disques virtuels.

Ces disques peuvent être représentés par des fichiers ou par des ressources de stockage adaptées à la plateforme.

Exemples de formats ou de types :

- `qcow2` avec QEMU/KVM.
- `raw` avec QEMU/KVM.
- `VMDK` dans des environnements VMware.
- Disques virtuels gérés par les mécanismes de stockage de Proxmox VE.
- Volumes sur stockage partagé ou distribué selon l'architecture.

Un disque virtuel n'est pas nécessairement un fichier de même taille que la capacité annoncée à la VM.

### 5.6 Taille fixe et allocation dynamique

Un disque à allocation fixe réserve généralement sa capacité selon le format et le backend de stockage.

Un disque à allocation dynamique consomme initialement moins d'espace physique et augmente au fur et à mesure que des données lui sont écrites.

Exemple :

```text
Capacité virtuelle annoncée : 100 Go

Espace réellement occupé :
  Début : 15 Go
  Après installation : 25 Go
  Après ajout de données : 60 Go
```

Ce comportement dépend du format, du backend et des options utilisés.

Il faut surveiller l'espace libre sur le stockage physique. Un disque virtuel qui peut croître jusqu'à 100 Go ne garantit pas que 100 Go seront toujours disponibles sur l'hôte.

### 5.7 Une VM peut avoir plusieurs disques

Il est courant de séparer les données du système d'exploitation.

```text
VM-DB01
|
+-- Disque système
|   +-- OS
|   +-- Logiciels
|
+-- Disque données
|   +-- Fichiers de la base
|
+-- Disque journaux
    +-- Journaux transactionnels
```

La séparation facilite parfois l'administration et le dimensionnement. Elle ne garantit pas, à elle seule, la protection des données.

La stratégie de sauvegarde doit prendre en compte tous les disques et les données nécessaires à la restauration.

## 6. Comprendre les réseaux virtuels

### 6.1 Pourquoi un réseau virtuel est-il nécessaire ?

Une VM qui exécute un serveur Web doit généralement communiquer avec des clients.

La plateforme de virtualisation doit fournir une connectivité réseau à la VM par l'intermédiaire d'une interface virtuelle.

```text
VM-LINUX
|
+-- Interface virtuelle
       |
       v
Commutateur virtuel
       |
       v
Interface physique de l'hôte
       |
       v
Réseau physique
```

Le commutateur virtuel relie les interfaces des machines virtuelles au réseau prévu.

Selon la plateforme, les réseaux virtuels peuvent être configurés avec une interface graphique, des fichiers de configuration ou des commandes.

### 6.2 Réseau NAT

En mode NAT, les VM utilisent généralement un réseau interne et partagent l'adresse de l'hôte pour accéder à l'extérieur.

Exemple :

```text
VM-LINUX
192.168.122.10
       |
       v
Réseau virtuel NAT
       |
       v
Hôte Linux
       |
       v
Internet
```

La VM peut établir des connexions vers l'extérieur, mais elle n'est pas nécessairement directement accessible depuis les autres machines du réseau.

Un accès entrant peut demander une règle de redirection de port ou une autre configuration.

Le réseau NAT est souvent adapté à un laboratoire simple.

### 6.3 Réseau ponté (bridge)

Le mode ponté relie la VM au réseau physique comme une machine supplémentaire, avec sa propre adresse IP sur le réseau concerné.

```text
Réseau local : 192.168.1.0/24
|
+-- Hôte physique : 192.168.1.10
|
+-- VM-LINUX : 192.168.1.20
|
+-- VM-WINDOWS : 192.168.1.21
```

Dans cette configuration, le routeur du réseau peut distribuer une adresse DHCP à la VM si le réseau le permet, ou l'administrateur peut configurer une adresse fixe appropriée.

Le mode ponté facilite l'accès aux VM depuis le réseau local, mais il expose aussi leurs services sur ce réseau. Il faut donc définir des règles de sécurité adaptées.

### 6.4 Réseau isolé

Un réseau isolé permet aux VM d'échanger entre elles sans leur fournir automatiquement un accès au réseau externe.

```text
VM-APP01
    |
    v
Commutateur isolé
    |
    +------ VM-DB01
    |
    +------ VM-TEST01
```

Il est utile pour tester des services ou des configurations qui ne doivent pas être directement exposés.

La portée réelle de l'isolation dépend de la configuration de l'hyperviseur et du réseau.

### 6.5 Comparaison des modes réseau

| Mode | Accès sortant | Accès depuis le réseau local | Usage fréquent |
|---|---|---|---|
| NAT | Généralement oui | Pas nécessairement direct | Laboratoire personnel |
| Ponté / Bridge | Selon le réseau | Oui, si le réseau l'autorise | Serveur de test accessible |
| Isolé | Pas d'accès externe par défaut | Non par défaut | Tests internes |
| Réseau privé entre VM | Selon la plateforme | Non par défaut | Communication de laboratoire |

Ces termes sont conceptuels. Les plateformes peuvent employer des noms ou des mécanismes différents.

### 6.6 Adresses IP et DNS des VM

Chaque VM utilisant un réseau IP doit disposer d'une configuration adaptée.

Pour un système Linux :

```bash
ip -br address
ip route
```

Pour tester la résolution DNS :

```bash
getent hosts example.com
```

Pour tester une requête HTTP :

```bash
curl -I https://example.com
```

Ces commandes permettent de distinguer certains problèmes de réseau, de routage et de résolution DNS.

Une VM démarrée n'est pas nécessairement une VM connectée au réseau.

## 7. Découvrir KVM, QEMU et libvirt

### 7.1 KVM

KVM signifie *Kernel-based Virtual Machine*.

Il s'agit d'une technologie de virtualisation intégrée au noyau Linux.

Elle s'appuie sur les fonctions de virtualisation matérielle disponibles sur les processeurs et sur les composants compatibles du système.

KVM permet au noyau Linux de participer à l'exécution de machines virtuelles.

### 7.2 QEMU

QEMU est un logiciel d'émulation et de virtualisation.

Dans un scénario QEMU/KVM courant, QEMU fournit notamment le modèle des périphériques virtuels et travaille avec KVM pour accélérer l'exécution du processeur invité lorsque les conditions sont réunies.

Schéma :

```text
        MACHINE VIRTUELLE
               |
               v
             QEMU
               |
               v
              KVM
               |
               v
       NOYAU LINUX DE L'HÔTE
               |
               v
       CPU ET MATÉRIEL PHYSIQUE
```

QEMU peut également émuler des processeurs ou des machines sans accélération KVM, mais les performances et les usages diffèrent.

### 7.3 libvirt

libvirt fournit une couche d'administration permettant de gérer différentes technologies de virtualisation.

Avec QEMU/KVM, libvirt facilite notamment :

- La définition des VM.
- Le démarrage et l'arrêt.
- La gestion du stockage.
- La gestion des réseaux virtuels.
- L'accès aux informations d'état.
- L'administration locale ou distante.
- L'utilisation de clients comme `virsh` et `virt-manager`.

Schéma :

```text
Administrateur
      |
      +-------------------+
      |                   |
      v                   v
    virsh             virt-manager
      |                   |
      +---------+---------+
                |
                v
             libvirt
                |
                v
             QEMU/KVM
                |
                v
             Machine VM
```

`virsh` est un outil en ligne de commande. `virt-manager` fournit une interface graphique de gestion.

### 7.4 Pourquoi cette séparation est utile

Il faut comprendre que KVM, QEMU, libvirt et Proxmox ne sont pas des synonymes.

| Composant | Rôle principal |
|---|---|
| KVM | Fonctions de virtualisation dans le noyau Linux |
| QEMU | Émulation matérielle et exécution des VM |
| libvirt | Gestion et définition des machines virtuelles |
| `virsh` | Administration en ligne de commande |
| `virt-manager` | Interface graphique de gestion |
| Proxmox VE | Plateforme intégrée de virtualisation et d'administration |

Cette distinction facilite le diagnostic. Par exemple, une erreur d'interface graphique n'implique pas nécessairement que KVM est incapable d'exécuter la machine virtuelle.

## 8. Proxmox VE : découvrir la plateforme

### 8.1 Qu'est-ce que Proxmox VE ?

Proxmox Virtual Environment est une plateforme de virtualisation construite sur Debian Linux.

Elle intègre notamment :

- KVM/QEMU pour les machines virtuelles.
- LXC pour les conteneurs système Linux.
- Une interface Web d'administration.
- Une gestion du stockage.
- Des fonctions de sauvegarde et de restauration.
- Des mécanismes de cluster.
- Des possibilités de haute disponibilité selon l'architecture.
- Des outils de gestion par ligne de commande et API.

La plateforme peut utiliser du stockage local, du stockage partagé et des solutions de stockage distribué prises en charge.

### 8.2 Architecture générale

```text
                    ADMINISTRATEUR
                          |
                          v
                     Interface Web
                          |
                          v
                     Proxmox VE
                          |
          +---------------+---------------+
          |                               |
          v                               v
       KVM/QEMU                          LXC
          |                               |
          v                               v
    Machines virtuelles             Conteneurs Linux
          |
          +-- VM Linux
          +-- VM Windows
          +-- VM de test
```

Proxmox fournit la gestion et l'intégration de ces composants.

Il n'est donc généralement pas nécessaire d'installer séparément une interface d'administration de VM comme `virt-manager` sur l'hôte Proxmox.

### 8.3 Installation de Proxmox VE

Une méthode courante consiste à installer Proxmox VE à partir de son image ISO officielle sur un serveur physique dédié.

La procédure générale est la suivante :

1. Télécharger l'ISO depuis le site officiel.
2. Vérifier son intégrité selon les indications publiées.
3. Préparer un support d'installation.
4. Sauvegarder les données existantes.
5. Démarrer le serveur sur le support d'installation.
6. Choisir le disque cible avec prudence.
7. Configurer le nom de machine.
8. Configurer l'adresse IP de gestion.
9. Définir la passerelle et les serveurs DNS.
10. Définir les identifiants d'administration.
11. Terminer l'installation.
12. Accéder à l'interface Web depuis une autre machine.

**Avertissement :** l'installation sur le disque cible peut supprimer les partitions et données existantes. Pour apprendre, utilise une machine dédiée ou un laboratoire compatible avec la virtualisation imbriquée.

Les exigences matérielles et les méthodes d'installation doivent être vérifiées dans le guide correspondant à la version choisie.

Documentation : https://www.proxmox.com/en/downloads/proxmox-virtual-environment/documentation

### 8.4 Accéder à l'interface Web

Une fois l'hôte installé et connecté au réseau, l'interface d'administration se trouve généralement à l'adresse :

`https://ADRESSE-IP-DE-L-HOTE:8006`

Exemple de laboratoire :

`https://192.168.1.50:8006`

Le navigateur peut afficher un avertissement si le certificat utilisé est auto-signé ou si le nom ne correspond pas à celui du certificat.

Avant de saisir des identifiants, il faut vérifier que la connexion aboutit bien au serveur prévu.

Ne publie pas directement l'interface d'administration Proxmox sur Internet sans une architecture d'accès sécurisée.

### 8.5 Les notions d'interface de Proxmox

Dans Proxmox VE, tu retrouveras notamment :

**Datacenter**

Vue qui rassemble les ressources et configurations de la plateforme ou du cluster.

**Node / Nœud**

Serveur Proxmox qui héberge les VM et conteneurs.

**VM**

Machine virtuelle complète gérée par QEMU/KVM.

**CT**

Conteneur système Linux géré par LXC.

**Storage**

Stockage défini pour les images de VM, les conteneurs, les ISO, les sauvegardes ou d'autres contenus selon son type.

**Network**

Configuration réseau de l'hôte et des VM, notamment les bridges et VLAN.

**Backup**

Fonctions de sauvegarde et de restauration disponibles selon les composants et la configuration.

### 8.6 Stockage sous Proxmox

Proxmox peut exploiter différents types de stockage.

Exemples :

- Stockage de type répertoire.
- Stockage LVM.
- Stockage ZFS.
- NFS.
- Certains stockages iSCSI.
- Ceph, selon l'architecture et la configuration.

Le type de stockage détermine les capacités disponibles, les méthodes de provisionnement et certains comportements de sauvegarde ou de migration.

Le stockage local d'un nœud ne devient pas automatiquement partagé avec les autres nœuds.

### 8.7 Réseau sous Proxmox

Proxmox emploie couramment des bridges Linux tels que `vmbr0`.

Un bridge permet de relier les interfaces réseau des VM et conteneurs au réseau prévu par l'architecture.

Schéma :

```text
VM-LINUX
   |
   v
Interface virtuelle
   |
   v
vmbr0
   |
   v
Carte réseau physique
   |
   v
Réseau de l'entreprise
```

La configuration réseau de l'hôte lui-même peut également utiliser un bridge.

Une erreur de configuration sur le bridge de gestion peut rendre l'interface Web inaccessible. Les modifications réseau doivent donc être réalisées avec une procédure et un accès de secours lorsque cela est nécessaire.

### 8.8 Pourquoi ne pas traiter Proxmox comme un simple programme de bureau ?

Proxmox VE est conçu pour administrer un hôte ou un ensemble de nœuds de virtualisation.

Dans une utilisation serveur, il faut notamment gérer :

- Les mises à jour de la plateforme.
- Le stockage.
- Les interfaces réseau.
- Les permissions.
- Les sauvegardes.
- Les ressources matérielles.
- Les journaux.
- Les risques de panne de l'hôte.

L'hôte Proxmox doit rester un environnement d'administration maîtrisé. Installer arbitrairement des applications sur l'hôte augmente les dépendances et peut compliquer la maintenance.

Documentation officielle : https://proxmox.com/en/products/proxmox-virtual-environment/get-started

## 9. VMware : découvrir les composants

### 9.1 L'écosystème VMware

Le terme VMware peut désigner plusieurs produits.

Pour comprendre la virtualisation, distingue au minimum :

**VMware Workstation**

Logiciel de virtualisation pour poste de travail compatible avec les systèmes hôtes pris en charge.

**VMware Fusion**

Produit de virtualisation destiné aux ordinateurs Mac compatibles.

**VMware ESXi**

Hyperviseur serveur installé sur du matériel compatible.

**VMware vSphere**

Plateforme de virtualisation serveur et ensemble de fonctions associées.

**VMware vCenter Server**

Composant de gestion centralisée utilisé dans les architectures qui le prévoient.

Les offres et les conditions d'accès aux produits dépendent de la gamme, de la version et du modèle de licence applicables.

### 9.2 Architecture VMware vSphere

```text
                ADMINISTRATEUR
                      |
                      v
                vCenter Server
                      |
              +-------+-------+
              |               |
              v               v
          Hôte ESXi 1      Hôte ESXi 2
              |               |
              v               v
             VM              VM
             VM              VM
             VM              VM
              |               |
              +-------+-------+
                      |
                      v
              Stockage et réseau
               selon l'architecture
```

Dans une architecture sans vCenter, un hôte ESXi peut être administré localement au moyen de son interface de gestion, avec des capacités dépendant des conditions et licences disponibles.

### 9.3 Le rôle d'ESXi

ESXi est installé sur le serveur physique compatible et exécute les machines virtuelles.

Les VM possèdent leurs ressources virtuelles et utilisent les réseaux et stockages associés à l'hôte.

Comme pour toute plateforme, la compatibilité matérielle, les pilotes, les versions et les droits de licence doivent être vérifiés.

### 9.4 Le rôle de vCenter Server

vCenter centralise de nombreuses opérations d'administration lorsque l'architecture et les licences le permettent.

Il peut notamment fournir des fonctions de gestion des hôtes, des VM, des clusters et des ressources.

Il n'est pas nécessairement requis pour chaque installation ESXi autonome, mais il joue un rôle majeur dans les environnements vSphere administrés de manière centralisée.

### 9.5 Datastore, réseau virtuel et VM

Dans VMware, un **datastore** représente un emplacement de stockage utilisé pour conserver des fichiers de machines virtuelles et d'autres éléments pris en charge.

Les réseaux virtuels reposent notamment sur des commutateurs virtuels et des groupes de ports.

Schéma :

```text
VM-WEB01
|
+-- vCPU
+-- Mémoire
+-- Disque virtuel
+-- Interface virtuelle
       |
       v
Commutateur virtuel
       |
       v
Carte réseau physique
       |
       v
Réseau de production
```

La terminologie précise et les capacités disponibles varient selon la version de vSphere.

### 9.6 Création d'une VM dans vSphere

La procédure générale comprend :

1. Se connecter à l'interface d'administration disponible.
2. Choisir l'hôte ou le cluster cible.
3. Lancer la création d'une nouvelle VM.
4. Définir son nom.
5. Choisir le système d'exploitation invité.
6. Définir le nombre de vCPU.
7. Définir la mémoire.
8. Choisir le datastore.
9. Créer le disque virtuel.
10. Configurer l'interface réseau.
11. Monter une ISO d'installation.
12. Démarrer la VM.
13. Installer le système d'exploitation.
14. Installer les composants invités requis.
15. Vérifier le réseau et le fonctionnement de la VM.

L'interface et les options exactes dépendent de la version de vSphere utilisée.

### 9.7 Snapshots et sauvegardes dans VMware

Les snapshots peuvent enregistrer un état à un moment donné et servir dans certains scénarios de test ou de retour arrière.

Ils ne doivent pas être utilisés comme mécanisme permanent de sauvegarde.

Une sauvegarde adaptée doit offrir les capacités de restauration et de conservation nécessaires, indépendamment des simples snapshots de VM.

### 9.8 Licences et choix du produit

Avant de déployer une plateforme VMware, vérifie les offres et droits de licence applicables auprès des canaux officiels Broadcom.

Les conditions, offres, droits d'utilisation et limitations peuvent évoluer. Il ne faut donc pas baser une conception de production sur une ancienne description d'une édition gratuite ou commerciale.

Références officielles :

- https://www.vmware.com/products/cloud-infrastructure/vsphere
- https://knowledge.broadcom.com/

## 10. Comparaison de KVM, Proxmox VE et VMware

### 10.1 Comparaison technique

| Critère | KVM avec libvirt | Proxmox VE | VMware vSphere |
|---|---|---|---|
| Base | Noyau Linux, QEMU et libvirt | Debian, KVM/QEMU, LXC et outils intégrés | ESXi et composants de l'écosystème vSphere |
| Administration | Ligne de commande, API et outils graphiques | Interface Web, CLI et API | Interface locale et outils centralisés selon l'architecture |
| Machines virtuelles | Oui | Oui | Oui |
| Conteneurs système intégrés | Non, pas dans libvirt comme fonction équivalente à LXC | Oui, avec LXC | Dépend des produits et composants utilisés |
| Stockage | Local, réseau et solutions compatibles | Local, partagé et distribué selon la configuration | Datastores et solutions prises en charge |
| Haute disponibilité | Possible avec une architecture et des outils supplémentaires | Intégration de mécanismes de cluster et de HA | Fonctions selon l'édition et la configuration |
| Complexité | Dépend de l'intégration choisie | Plateforme intégrée | Plateforme serveur intégrée à l'écosystème VMware |
| Licence | Composants open source, avec conditions propres à chaque logiciel | Code libre sous licence AGPLv3 pour la plateforme, avec options de support et dépôts distincts | Modèle commercial et droits d'utilisation à vérifier selon l'offre |

### 10.2 Quand choisir KVM avec libvirt ?

KVM avec libvirt peut convenir si tu veux :

- Apprendre les mécanismes Linux.
- Construire une plateforme d'hébergement personnalisée.
- Administrer des VM à partir d'outils standards.
- Utiliser `virsh`, `virt-install` et des interfaces graphiques adaptées.
- Construire une automatisation avec des outils Linux.

Il faut cependant être prêt à configurer et maintenir soi-même les différents composants nécessaires à l'exploitation.

### 10.3 Quand choisir Proxmox VE ?

Proxmox VE est intéressant si tu souhaites :

- Une interface Web intégrée.
- Administrer plusieurs VM sans assembler toute l'interface d'administration.
- Utiliser KVM et LXC.
- Gérer le stockage depuis une plateforme commune.
- Disposer de fonctions intégrées de sauvegarde et de gestion de cluster.
- Apprendre l'administration d'une plateforme de virtualisation serveur.

Même avec une interface Web, les connaissances en Linux, réseau, stockage et sauvegarde restent nécessaires.

### 10.4 Quand choisir VMware ?

VMware vSphere peut être adapté lorsqu'une organisation utilise déjà l'écosystème VMware, dispose des compétences nécessaires et souhaite exploiter les fonctions disponibles dans son offre.

Le choix dépend notamment :

- Des exigences fonctionnelles.
- Du matériel compatible.
- Des licences.
- Des logiciels tiers.
- Du niveau de support.
- De la stratégie de migration.
- Des besoins de disponibilité.
- Du coût total d'exploitation.

### 10.5 Il n'existe pas de meilleur hyperviseur dans tous les cas

Les trois environnements peuvent exécuter des machines virtuelles de production, de laboratoire ou de test dans les conditions prévues.

Le choix doit être motivé par le besoin, pas uniquement par la popularité d'une technologie.

Pour un débutant souhaitant apprendre l'administration de VM, Proxmox VE fournit une plateforme intégrée facile à explorer. KVM/libvirt est particulièrement formateur pour comprendre les composants Linux. VMware permet d'acquérir des compétences pertinentes dans les infrastructures utilisant ses produits.

## 11. Préparer le matériel

### 11.1 Vérifier la virtualisation du processeur

Sur un hôte Linux, tu peux examiner les capacités du processeur :

```bash
lscpu
```

Sur les architectures x86, vérifier les indicateurs de virtualisation :

```bash
grep -E -c '(vmx|svm)' /proc/cpuinfo
```

En général :

- `vmx` correspond à une extension Intel de virtualisation.
- `svm` correspond à une extension AMD de virtualisation.

Une valeur supérieure à zéro indique que le système expose au moins un indicateur correspondant. Une valeur nulle ne permet pas, à elle seule, de conclure que le processeur physique est incompatible : les extensions peuvent être désactivées ou non exposées à une VM imbriquée.

### 11.2 Vérifier `/dev/kvm`

Sur Linux :

```bash
ls -l /dev/kvm
```

Si le périphérique existe et que les permissions sont appropriées, cela indique que l'environnement KVM est potentiellement disponible.

Si le périphérique n'existe pas, vérifie :

- Le matériel.
- Les paramètres UEFI/BIOS.
- Le noyau.
- Les modules de virtualisation.
- Les restrictions imposées par l'hyperviseur parent si Linux est déjà une VM.

### 11.3 Activer la virtualisation dans l'UEFI/BIOS

Selon le constructeur, l'option peut porter un nom tel que :

- Intel Virtualization Technology.
- Intel VT-x.
- AMD-V.
- SVM Mode.
- Virtualization Extensions.

Le libellé et l'emplacement varient selon le matériel.

Il faut activer la fonction compatible et redémarrer si nécessaire.

Sur certaines plateformes, la virtualisation imbriquée doit aussi être exposée par l'hyperviseur parent pour que KVM ou un autre hyperviseur puisse fonctionner à l'intérieur d'une VM.

### 11.4 Dimensionner la mémoire

Commence par une charge raisonnable.

Exemple de laboratoire :

```text
Hôte : 16 Go de RAM

VM-UBUNTU01 : 2 Go
VM-UBUNTU02 : 2 Go
VM-WINDOWS01 : 4 Go

Mémoire attribuée aux VM : 8 Go
```

Cette répartition laisse de la mémoire à l'hôte, aux caches et aux services de virtualisation.

Si tu crées plusieurs VM Windows, des bases de données ou des systèmes de supervision, il faudra prévoir davantage de mémoire.

### 11.5 Dimensionner le stockage

La capacité de stockage doit couvrir :

- L'hyperviseur.
- Les disques virtuels.
- Les fichiers ISO.
- Les sauvegardes si elles sont stockées localement.
- Les journaux.
- Les snapshots ou checkpoints éventuels.
- Les fichiers temporaires.
- Une marge pour la croissance.

Un disque de 250 Go peut être suffisant pour un laboratoire limité, mais il peut rapidement devenir insuffisant si plusieurs images de systèmes et sauvegardes sont conservées.

### 11.6 Vérifier le réseau

Avant de créer les réseaux virtuels, identifie :

- L'adresse IP de gestion.
- La passerelle.
- Les serveurs DNS.
- L'interface réseau physique.
- Les réseaux des VM.
- La présence éventuelle de VLAN.
- Les besoins d'accès depuis un autre poste.
- Le comportement du pare-feu.

Une mauvaise configuration réseau peut rendre une VM inaccessible ou faire perdre l'accès d'administration à l'hôte lui-même.

## 12. Travaux pratiques : installer KVM sur Ubuntu Server

Ce laboratoire permet d'apprendre les bases de la virtualisation Linux à partir d'un hôte Ubuntu Server.

### 12.1 Architecture du laboratoire

```text
PC ADMINISTRATEUR
       |
       | SSH / interface de gestion
       v
HÔTE UBUNTU
       |
       +-- KVM
       +-- QEMU
       +-- libvirt
       |
       +-- Réseau virtuel NAT
       |       |
       |       +-- VM-LINUX01
       |       +-- VM-LINUX02
       |
       +-- Stockage virtuel
               |
               +-- Disques QCOW2
```

Nous utiliserons un réseau NAT pour éviter d'exposer directement les VM sur le réseau physique.

### 12.2 Mettre à jour les listes de paquets

Sur Ubuntu Server :

```bash
sudo apt update
```

Il est recommandé de maintenir l'hôte à jour selon la politique de maintenance de l'environnement.

### 12.3 Installer les outils

Installe les composants principaux :

```bash
sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients virtinst cpu-checker
```

Ces paquets fournissent notamment les outils nécessaires à l'exécution et à l'administration des VM.

Selon la version de la distribution, certains composants du service libvirt peuvent être organisés différemment.

### 12.4 Vérifier la prise en charge de KVM

Si l'outil est disponible :

```bash
kvm-ok
```

Puis :

```bash
ls -l /dev/kvm
```

Si le résultat est négatif, vérifie la virtualisation matérielle, les modules et les permissions avant de créer une VM.

### 12.5 Vérifier libvirt

Examiner les machines connues :

```bash
sudo virsh --connect qemu:///system list --all
```

Cette commande affiche les machines virtuelles connues de l'instance système libvirt.

Le mode `qemu:///system` permet une gestion système des machines virtuelles, indépendante d'une session utilisateur particulière.

Le mode `qemu:///session` existe aussi, mais ses possibilités réseau et ses permissions diffèrent.

### 12.6 Vérifier le réseau par défaut

Exécute :

```bash
sudo virsh net-list --all
```

Un réseau nommé `default` est souvent présent dans une installation libvirt classique. Il utilise généralement un mécanisme NAT pour donner aux VM un accès sortant.

Si le réseau existe mais est arrêté, tu peux l'activer :

```bash
sudo virsh net-start default
```

Pour lui demander de démarrer automatiquement avec l'hôte :

```bash
sudo virsh net-autostart default
```

Ces commandes ne doivent être lancées que si le réseau `default` existe.

Pour examiner les détails :

```bash
sudo virsh net-info default
```

### 12.7 Préparer le support ISO

Supposons que tu possèdes une ISO d'installation Linux autorisée à l'usage prévu.

Le chemin utilisé dans le laboratoire sera :

`/var/lib/libvirt/images/linux-lab.iso`

Le fichier doit réellement exister à cet emplacement.

Tu peux lister le contenu du répertoire :

```bash
sudo ls -lh /var/lib/libvirt/images/
```

La source doit être téléchargée depuis un site de distribution fiable et vérifiée selon les instructions officielles du projet concerné.

### 12.8 Créer une VM avec `virt-install`

Exemple de création d'une machine virtuelle de laboratoire :

```bash
sudo virt-install \
    --connect qemu:///system \
    --name lab-linux01 \
    --memory 2048 \
    --vcpus 2 \
    --disk path=/var/lib/libvirt/images/lab-linux01.qcow2,size=20,format=qcow2 \
    --cdrom /var/lib/libvirt/images/linux-lab.iso \
    --os-variant generic \
    --network network=default,model=virtio \
    --graphics vnc,listen=127.0.0.1 \
    --noautoconsole
```

Cette commande suppose que :

- Le support ISO existe.
- Le stockage possède suffisamment d'espace.
- Le réseau `default` est actif.
- Le système hôte prend en charge la virtualisation.
- La version de `virt-install` accepte les options utilisées.

Si tu ne disposes pas d'un affichage graphique, tu peux prévoir une méthode de console compatible avec ton environnement de gestion.

**Sécurité :** l'option VNC utilisée ici limite l'écoute à l'adresse locale `127.0.0.1`. Il ne faut pas exposer une console VNC non protégée directement à un réseau non fiable.

Pour examiner les variantes de systèmes connues par les outils installés :

```bash
osinfo-query os
```

Adapte le paramètre `--os-variant` à la distribution réellement installée lorsque tu connais son identifiant dans la base locale.

### 12.9 Comprendre les options

| Option | Rôle |
|---|---|
| `--connect qemu:///system` | Utilise l'instance système de libvirt |
| `--name lab-linux01` | Définit le nom de la VM |
| `--memory 2048` | Attribue 2048 Mio de RAM |
| `--vcpus 2` | Configure deux processeurs virtuels |
| `--disk ... size=20` | Crée un disque virtuel de capacité annoncée de 20 Gio |
| `format=qcow2` | Utilise le format qcow2 |
| `--cdrom` | Utilise un support d'installation |
| `--network network=default` | Connecte l'interface au réseau libvirt par défaut |
| `model=virtio` | Utilise un modèle d'interface virtio |
| `--noautoconsole` | N'ouvre pas automatiquement la console dans le terminal courant |

Les options exactes et leur comportement doivent être vérifiés avec la version locale de `virt-install`.

### 12.10 Lancer la console de la VM

Lister les VM :

```bash
sudo virsh --connect qemu:///system list --all
```

Si la VM est arrêtée :

```bash
sudo virsh --connect qemu:///system start lab-linux01
```

Pour afficher les informations de la VM :

```bash
sudo virsh --connect qemu:///system dominfo lab-linux01
```

La console dépend de la méthode graphique ou de la console configurée lors de la création.

Avec un environnement de gestion approprié, tu peux utiliser les outils compatibles comme `virt-viewer` ou `virt-manager`.

### 12.11 Installer le système invité

La suite est semblable à l'installation d'un système sur un ordinateur physique :

1. Démarrer la VM.
2. Ouvrir sa console.
3. Choisir la langue.
4. Configurer le disque.
5. Créer un compte.
6. Installer le système.
7. Terminer l'installation.
8. Redémarrer la VM.
9. Retirer ou désactiver le support ISO si nécessaire.
10. Vérifier le fonctionnement du système.

Le système invité dispose alors de ses propres fichiers, comptes, services et paramètres réseau.

### 12.12 Administrer la VM avec `virsh`

Lister les machines :

```bash
sudo virsh list --all
```

Démarrer une machine :

```bash
sudo virsh start lab-linux01
```

Demander un arrêt propre :

```bash
sudo virsh shutdown lab-linux01
```

Redémarrer :

```bash
sudo virsh reboot lab-linux01
```

Activer le démarrage automatique :

```bash
sudo virsh autostart lab-linux01
```

Désactiver le démarrage automatique :

```bash
sudo virsh autostart lab-linux01 --disable
```

Il faut distinguer les commandes qui demandent un arrêt propre et celles qui forcent une interruption. Un arrêt forcé peut entraîner une perte de données, exactement comme si l'alimentation d'un ordinateur physique était coupée.

### 12.13 Vérifier l'état du stockage virtuel

Afficher le disque attaché :

```bash
sudo virsh domblklist lab-linux01
```

Afficher les informations de la VM :

```bash
sudo virsh dominfo lab-linux01
```

Ces commandes permettent d'identifier les ressources associées.

Ne supprime jamais un fichier disque en supposant qu'il est inutilisé simplement parce que son nom paraît ancien ou temporaire.

## 13. Administrer les VM avec `virt-manager`

### 13.1 À quoi sert virt-manager ?

`virt-manager` fournit une interface graphique pour gérer des VM utilisant libvirt.

Il peut permettre :

- De créer une VM.
- De modifier le CPU et la mémoire.
- D'attacher un ISO.
- De configurer des disques virtuels.
- De modifier l'interface réseau.
- D'ouvrir la console.
- De démarrer et d'arrêter une VM.

Il est généralement plus approprié sur un poste d'administration graphique que sur un serveur de production minimal.

### 13.2 Installer virt-manager sur un poste Linux

Sur un poste de travail compatible :

```bash
sudo apt update
sudo apt install virt-manager virt-viewer
```

Puis lance :

```bash
virt-manager
```

L'interface permet de se connecter à l'instance libvirt locale ou à un hôte distant correctement configuré.

### 13.3 Administration distante

Une connexion distante peut être établie via les mécanismes pris en charge par libvirt, notamment un transport SSH correctement configuré.

Exemple de principe :

```bash
virt-manager -c qemu+ssh://admin@hote-virt/system
```

Le nom `hote-virt` et le compte `admin` doivent correspondre à des valeurs réelles de ton environnement.

L'accès distant doit être limité aux personnes autorisées et utiliser une authentification sécurisée.

### 13.4 Permissions d'administration

Le contrôle de libvirt peut donner un accès important aux VM, aux disques virtuels et aux interfaces réseau.

L'ajout d'un compte à un groupe d'administration tel que `libvirt` peut donc lui donner des privilèges élevés.

Il faut appliquer le principe du moindre privilège. N'ajoute pas des utilisateurs à un groupe d'administration simplement pour supprimer une erreur d'accès sans comprendre les permissions impliquées.

Documentation Ubuntu : https://ubuntu.com/server/docs/how-to/virtualisation/libvirt/

## 14. Travaux pratiques : créer une VM dans Proxmox VE

Ce laboratoire présente la démarche d'administration. L'installation sur un serveur physique doit être effectuée séparément et sur un équipement dont le disque peut être utilisé.

### 14.1 Préparer Proxmox

Avant de créer une VM, vérifie :

- L'état du nœud.
- L'adresse de gestion.
- Le stockage disponible.
- Le réseau virtuel.
- L'ISO nécessaire.
- Les permissions d'administration.
- L'espace disponible.
- La version installée.

Il est essentiel de distinguer la configuration réseau de l'hôte Proxmox et celle de la VM.

### 14.2 Importer une ISO

Dans l'interface Web :

1. Sélectionner le nœud.
2. Choisir le stockage adapté aux images ISO.
3. Ouvrir la section de contenu.
4. Téléverser l'ISO ou l'obtenir par la méthode prise en charge.
5. Vérifier que le fichier est présent.

L'ISO est un support d'installation. Elle ne constitue pas le disque système installé de la VM.

### 14.3 Créer la machine virtuelle

Dans l'interface :

1. Sélectionner **Create VM**.
2. Choisir le nœud qui doit héberger la machine.
3. Définir un identifiant et un nom.
4. Choisir le système d'exploitation et l'ISO.
5. Sélectionner les paramètres BIOS/UEFI compatibles.
6. Définir les processeurs virtuels.
7. Définir la mémoire.
8. Choisir le stockage de destination.
9. Créer le disque virtuel.
10. Ajouter l'interface réseau.
11. Vérifier le résumé.
12. Créer la VM.
13. La démarrer.
14. Ouvrir la console.
15. Installer le système invité.

Les noms des boutons et certaines options peuvent varier légèrement selon la version de Proxmox VE.

### 14.4 Configuration de départ suggérée

Pour une petite VM Linux :

| Paramètre | Valeur pédagogique |
|---|---|
| Nom | `vm-linux01` |
| vCPU | 2 |
| RAM | 2048 Mio |
| Disque système | 20 Gio |
| Contrôleur disque | VirtIO SCSI selon le scénario |
| Carte réseau | Modèle VirtIO |
| Bridge | `vmbr0` si adapté au réseau choisi |
| Support d'installation | ISO Linux |
| Démarrage | Après vérification des paramètres |

Il s'agit d'une configuration de laboratoire. Les ressources d'une VM de production doivent être déterminées selon la charge de l'application.

### 14.5 Réseau et bridge

Dans une configuration de Proxmox, un bridge comme `vmbr0` peut relier les interfaces des VM au réseau physique.

Si le bridge est connecté au réseau de production, la VM peut recevoir une adresse IP compatible avec ce réseau, selon la configuration du routeur, du DHCP et des règles réseau.

Vérifie l'adresse depuis le système invité après installation.

### 14.6 Démarrage et administration

Dans l'interface Web, tu peux notamment :

- Démarrer la VM.
- L'arrêter.
- Redémarrer.
- Ouvrir la console.
- Afficher l'utilisation des ressources.
- Modifier certains paramètres matériels.
- Gérer les supports et disques virtuels.

Ces opérations doivent être réalisées en tenant compte de l'état du système invité.

Lorsque c'est possible, préfère un arrêt propre du système d'exploitation plutôt qu'une interruption immédiate de l'alimentation virtuelle.

### 14.7 Développer la plateforme

Une fois les premières VM fonctionnelles, tu pourras étudier :

- Les templates.
- Les clones.
- Les sauvegardes.
- La restauration.
- Les snapshots dans les scénarios compatibles.
- Les bridges et VLAN.
- Le stockage partagé.
- Le clustering.
- La migration.
- La haute disponibilité.

Ces fonctions doivent être apprises progressivement. Un cluster ou un stockage distribué exige des prérequis matériels et réseau supplémentaires.

Documentation officielle : https://www.proxmox.com/en/downloads/proxmox-virtual-environment/documentation

## 15. Travaux pratiques : découvrir VMware vSphere

### 15.1 Préparer un environnement

Pour un laboratoire vSphere, il faut un hôte et une version de logiciel compatibles avec les droits de licence disponibles.

Selon le scénario, l'environnement peut inclure :

- ESXi.
- Une interface d'administration de l'hôte.
- vCenter Server pour la gestion centralisée.
- Un datastore.
- Un réseau virtuel.
- Une ISO de système invité.

Vérifie toujours les exigences matérielles, les versions supportées et les droits de licence avant l'installation.

### 15.2 Préparer le serveur

Les étapes générales d'installation d'ESXi sont :

1. Vérifier la compatibilité du matériel.
2. Vérifier les contrôleurs de stockage et cartes réseau.
3. Télécharger l'image depuis les canaux officiels autorisés.
4. Vérifier son intégrité.
5. Préparer le support d'installation.
6. Démarrer le serveur.
7. Installer ESXi sur le stockage prévu.
8. Configurer le réseau de gestion.
9. Définir les accès d'administration.
10. Vérifier la connectivité depuis le poste d'administration.

L'installation sur un disque existant peut supprimer les données qu'il contient.

### 15.3 Accéder à l'hôte

Une fois l'adresse de gestion configurée, l'accès local s'effectue généralement à l'aide de l'interface Web de l'hôte.

Il faut vérifier le certificat, le nom du serveur et l'adresse avant de saisir les identifiants.

Ne publie pas directement l'interface de gestion sur Internet sans une architecture d'accès sécurisée.

### 15.4 Créer une VM dans l'interface disponible

La procédure générale est la suivante :

1. Choisir l'hôte ou le cluster.
2. Créer une nouvelle VM.
3. Définir son nom et son système invité.
4. Choisir le datastore.
5. Définir le CPU virtuel.
6. Définir la mémoire.
7. Créer le disque virtuel.
8. Ajouter l'interface réseau.
9. Monter l'ISO.
10. Démarrer la VM.
11. Installer le système invité.
12. Installer les composants invités recommandés par la plateforme.
13. Vérifier le réseau et les applications.

Le choix des paramètres dépend de la version d'ESXi, de la configuration réseau et du type de système invité.

### 15.5 Déployer vCenter

Dans une architecture centralisée, vCenter Server permet de gérer les hôtes et les VM depuis une plateforme commune.

Son déploiement doit respecter les exigences de la version et de l'offre utilisée.

Il faut notamment préparer :

- Le DNS.
- Le nom du serveur.
- Les ressources nécessaires.
- Le réseau.
- Le stockage.
- Les identifiants.
- Les certificats.
- La sauvegarde et la procédure de restauration.

Les droits de licence et les fonctionnalités dépendent de l'offre VMware/Broadcom applicable.

Documentation officielle : https://knowledge.broadcom.com/

## 16. Bien dimensionner les machines virtuelles

### 16.1 Commencer par un besoin réel

Une VM doit être dimensionnée à partir du système et de l'application à exécuter.

Pour commencer, définis :

- Le système invité.
- Les applications prévues.
- Le nombre d'utilisateurs.
- La charge moyenne.
- Les pointes attendues.
- Les exigences de stockage.
- La nécessité de redémarrage rapide.
- Les exigences de disponibilité.

Attribuer un maximum de ressources à chaque VM ne constitue pas un bon dimensionnement.

### 16.2 Exemple de parc pédagogique

Un hôte de 32 Go de RAM peut héberger, selon la charge réelle, un ensemble semblable à celui-ci :

| VM | Rôle | RAM configurée |
|---|---|---:|
| VM-DC-LAB | Service d'annuaire de laboratoire | 4 Go |
| VM-WEB01 | Serveur Web | 2 Go |
| VM-DB01 | Base de données de test | 6 Go |
| VM-LINUX01 | Apprentissage Linux | 2 Go |
| VM-CLIENT01 | Poste de test | 4 Go |
| Réserve approximative | Hôte et marge de fonctionnement | 14 Go |

Ces valeurs sont des exemples et ne constituent pas des recommandations universelles.

Pour un serveur de production, vérifie les exigences réelles du système, la charge et la marge nécessaire.

### 16.3 Mesurer les performances

Sur Linux, des outils comme `top`, `free`, `vmstat` et `iostat` peuvent aider à examiner la charge.

Sur Windows, le Moniteur de performances et le Gestionnaire des tâches permettent d'examiner les principales ressources.

Il faut distinguer :

- CPU physique.
- vCPU attribués.
- Mémoire attribuée.
- Mémoire réellement utilisée.
- E/S de stockage.
- Trafic réseau.
- Latence.

La VM peut être lente même si le CPU semble peu utilisé, par exemple si le stockage est saturé ou si l'application attend une dépendance.

### 16.4 Éviter le surdimensionnement

Une VM possédant plus de vCPU qu'elle n'en utilise n'est pas nécessairement plus rapide.

Le surdimensionnement peut aussi augmenter la concurrence pour les ressources de l'hôte.

Il faut mesurer le comportement de l'application et ajuster la configuration en fonction des résultats.

### 16.5 Éviter la saturation de l'hôte

Si l'hôte consomme presque toute sa mémoire, les performances des VM peuvent se dégrader.

Il faut conserver une marge d'exploitation et éviter d'attribuer toute la mémoire disponible aux systèmes invités.

Un hôte saturé peut faire échouer des démarrages de VM, des sauvegardes ou des opérations de maintenance.

## 17. Snapshots, checkpoints, clones et sauvegardes

### 17.1 Le snapshot

Un snapshot représente un état de VM à un moment donné, selon les possibilités et le modèle de la plateforme.

Il peut être utile avant une modification risquée dans un laboratoire.

Cependant, un snapshot n'est pas nécessairement indépendant du stockage de la VM, et il ne constitue pas une sauvegarde complète à lui seul.

### 17.2 Le checkpoint ou point de contrôle

Certains produits utilisent le terme *checkpoint* pour désigner un mécanisme comparable de capture d'état.

Les détails changent selon la plateforme. Il faut comprendre ce qui est effectivement conservé : disque, configuration, mémoire, état du système invité ou combinaison de ces éléments.

### 17.3 Le clone

Un clone est une nouvelle VM créée à partir d'une autre machine virtuelle.

Un clone complet possède son propre ensemble de fichiers ou ressources selon le mode utilisé.

Un clone lié dépend souvent d'une image de base et utilise des mécanismes de partage de stockage propres à la plateforme.

Le clone est utile pour créer des environnements de test, mais il faut également traiter les identités, les adresses et les configurations propres à la nouvelle machine.

### 17.4 La sauvegarde

Une sauvegarde est une copie conservée dans le but de pouvoir restaurer les données ou la machine après un incident.

Elle doit être gérée par une solution et une procédure adaptées, avec une rétention et des contrôles de restauration.

### 17.5 Comparaison

| Mécanisme | Usage principal | Limite |
|---|---|---|
| Snapshot / checkpoint | Retour rapide à un état récent pour certains scénarios | Dépendances et rétention limitées |
| Clone | Créer une autre VM à partir d'une référence | Nécessite de configurer l'identité et les dépendances |
| Sauvegarde | Restaurer après incident ou perte | Demande de protéger les copies et de tester la restauration |
| Réplication | Maintenir une copie sur un autre système | Peut reproduire une corruption ou une suppression |
| Image de référence | Standardiser une installation | Doit être entretenue et mise à jour |

### 17.6 Ne pas conserver des snapshots indéfiniment

Les snapshots peuvent augmenter la consommation de stockage et compliquer les opérations de maintenance selon leur modèle.

Ils doivent être gérés avec une politique claire.

Avant de supprimer ou de consolider un snapshot dans un environnement de production, vérifie le comportement de la plateforme et l'état de la VM.

Ne supprime pas manuellement des fichiers de snapshot en pensant que cela suffit à nettoyer la VM.

### 17.7 Tester les sauvegardes

Le contrôle de sauvegarde doit inclure une restauration réelle.

Vérifie :

- La présence des copies.
- L'intégrité des données.
- La disponibilité des clés de chiffrement nécessaires.
- L'accès à l'environnement de restauration.
- Le fonctionnement du système restauré.
- La cohérence des données.
- Le temps nécessaire à la reprise.

Une sauvegarde affichée comme réussie n'est pas une preuve absolue qu'une restauration complète fonctionnera.

## 18. Sécuriser l'environnement de virtualisation

### 18.1 Protéger l'hyperviseur

L'hyperviseur est un composant critique : il héberge et contrôle plusieurs VM.

Une personne capable de contrôler l'hôte dispose potentiellement de capacités importantes sur les systèmes invités.

Il faut donc :

- Limiter les comptes administratifs.
- Protéger les interfaces de gestion.
- Appliquer les mises à jour.
- Surveiller les journaux.
- Restreindre les services inutiles.
- Protéger les informations d'authentification.
- Sauvegarder la configuration.
- Vérifier les permissions sur les disques virtuels.

### 18.2 Séparer le réseau de gestion

Il est préférable de limiter le réseau de gestion aux postes et comptes autorisés.

Exemple :

```text
Réseau de gestion
|
+-- Poste d'administration
|
+-- Interface de gestion de l'hyperviseur
|
+-- Serveurs d'administration autorisés


Réseau des VM
|
+-- Serveur Web
|
+-- Base de données
|
+-- Applications
```

La séparation peut utiliser des réseaux physiques, des VLAN et des règles de pare-feu adaptées.

Une séparation logique ne remplace pas toutes les garanties d'isolation physique, et sa qualité dépend de la configuration complète.

### 18.3 Protéger les consoles

Les consoles des VM fournissent un accès direct à leur système.

Il faut limiter les accès selon le rôle de l'administrateur et éviter de laisser des consoles de gestion exposées à des réseaux non fiables.

### 18.4 Gérer les identifiants

N'utilise pas le même mot de passe administrateur pour toutes les plateformes et tous les systèmes.

Évite de stocker des secrets dans des scripts non protégés ou dans des notes accessibles à tous.

La journalisation et le contrôle des accès peuvent aider à détecter les opérations suspectes.

### 18.5 Isoler les machines virtuelles de laboratoire

Les VM de test ne devraient pas nécessairement être connectées au même réseau que les services sensibles.

Utilise des réseaux isolés ou des VLAN adaptés lorsque tu testes :

- Des serveurs DHCP.
- Des services d'annuaire.
- Des politiques réseau.
- Des pare-feu.
- Des systèmes de détection.
- Des configurations pouvant perturber le réseau.

Une VM de laboratoire mal configurée peut provoquer des conflits DHCP, des conflits IP ou des communications indésirables si elle est connectée au réseau de production.

### 18.6 Préparer les mises à jour

Il faut maintenir à jour :

- L'hyperviseur.
- Les outils d'administration.
- Les systèmes invités.
- Les pilotes virtuels.
- Les composants d'intégration.
- Les logiciels applicatifs.
- Les solutions de sauvegarde.

Les mises à jour doivent être planifiées en tenant compte de la disponibilité, des compatibilités et des possibilités de retour arrière.

## 19. Administrer les VM au quotidien

### 19.1 Contrôler les machines connues

Avec libvirt :

```bash
sudo virsh list --all
```

Cette commande permet de voir les VM en fonctionnement et celles qui sont arrêtées.

Pour examiner une VM particulière :

```bash
sudo virsh dominfo lab-linux01
```

Pour consulter les interfaces de stockage :

```bash
sudo virsh domblklist lab-linux01
```

Pour vérifier les interfaces réseau :

```bash
sudo virsh domiflist lab-linux01
```

### 19.2 Démarrer et arrêter proprement

Avant une maintenance, identifie les services présents dans les VM.

Un arrêt propre permet au système invité de fermer les services, d'écrire les données et de démonter les systèmes de fichiers selon son fonctionnement.

Les commandes d'arrêt forcé doivent être réservées aux situations qui le nécessitent.

### 19.3 Vérifier les adresses IP des VM

Sur le système invité :

```bash
ip -br address
ip route
```

Si la plateforme fournit un mécanisme de découverte d'adresse, celui-ci peut nécessiter un agent invité installé et fonctionnel.

L'adresse affichée par l'hyperviseur ne remplace pas un contrôle de connectivité réel.

### 19.4 Vérifier l'état des services invités

Dans une VM Linux :

```bash
systemctl --failed
```

Pour vérifier un service :

```bash
systemctl status nginx
```

Dans une VM Windows, utilise les outils d'administration adaptés pour vérifier les services et les journaux.

La VM peut être démarrée alors qu'une application est en panne. Il faut donc contrôler les services, et pas uniquement l'état de la machine virtuelle.

### 19.5 Documenter les machines

Pour chaque VM importante, conserve au minimum :

- Son nom.
- Son rôle.
- Son système d'exploitation.
- Ses ressources CPU et RAM.
- Son stockage.
- Son adresse réseau.
- Ses dépendances.
- Son propriétaire.
- Sa stratégie de sauvegarde.
- Ses procédures d'arrêt et de restauration.

Cet inventaire facilite le dépannage et la planification de capacité.

## 20. Comprendre la migration et la haute disponibilité

### 20.1 Migration d'une VM

La migration consiste à déplacer une VM ou certaines de ses ressources vers un autre hôte.

Selon la plateforme et la méthode, le déplacement peut nécessiter un arrêt de la VM ou être réalisé à chaud.

Le résultat dépend du stockage, du réseau, de la compatibilité des hôtes et des fonctionnalités disponibles.

### 20.2 Migration avec stockage local

Si le disque virtuel se trouve uniquement sur le stockage local d'un hôte, le déplacement vers un autre hôte peut nécessiter de copier les disques ou d'utiliser une méthode de migration prévue par la plateforme.

### 20.3 Migration avec stockage partagé

Si les deux hôtes accèdent au même stockage compatible, la migration peut être plus simple.

Cependant, le stockage partagé est lui-même une dépendance et doit être protégé contre les pannes.

### 20.4 Haute disponibilité

Une plateforme de virtualisation hautement disponible peut redémarrer ou déplacer des VM vers un autre hôte après certains incidents.

Il faut disposer de plusieurs composants correctement configurés :

- Plusieurs hôtes.
- Une méthode de coordination.
- Un stockage adapté.
- Une capacité restante suffisante.
- Des réseaux compatibles.
- Un mécanisme de gestion des pannes.
- Une configuration des VM appropriée.

Une seule machine physique exécutant plusieurs VM n'offre pas de haute disponibilité au niveau de l'hôte.

### 20.5 Haute disponibilité et sauvegarde

La haute disponibilité et la sauvegarde répondent à des risques différents.

Si l'hôte tombe en panne, la haute disponibilité peut permettre de reprendre le service.

Si les données sont corrompues ou supprimées, une sauvegarde peut être nécessaire pour retrouver un état antérieur.

Si le site entier est détruit, il faut une solution de reprise adaptée à cette perte.

Une infrastructure de production doit donc combiner les protections nécessaires au scénario métier.

## 21. Diagnostic des problèmes courants

### 21.1 La virtualisation ne démarre pas

Symptômes possibles :

- KVM ne trouve pas le périphérique `/dev/kvm`.
- Une VM ne démarre pas.
- Le logiciel indique qu'aucune accélération matérielle n'est disponible.
- L'installation de la VM échoue avant le démarrage.

Vérifie :

1. Le support matériel.
2. L'activation de VT-x ou AMD-V.
3. La présence de `/dev/kvm`.
4. Les modules du noyau.
5. Les permissions.
6. La virtualisation imbriquée si l'hôte est lui-même une VM.

Commandes utiles :

```bash
lscpu
ls -l /dev/kvm
```

### 21.2 La VM n'accède pas à Internet

Vérifie :

```bash
ip -br address
ip route
getent hosts example.com
```

Puis examine :

- L'adresse IP.
- La passerelle.
- Les serveurs DNS.
- Le mode réseau.
- Les règles de pare-feu.
- La connectivité de l'hôte.
- Les règles NAT ou les bridges.

Il faut déterminer si la panne se situe sur la VM, le réseau virtuel, l'hôte ou le réseau physique.

### 21.3 La VM n'est pas accessible depuis le réseau local

Si elle utilise un réseau NAT, cet accès peut ne pas être direct.

Il faut vérifier le mode réseau et déterminer si un bridge ou une redirection de port est approprié.

Avant d'ouvrir un port, examine les risques et limite les accès aux sources nécessaires.

### 21.4 Le système invité est lent

Les causes peuvent comprendre :

- Manque de RAM.
- Surcharge CPU.
- Stockage saturé.
- Latence élevée du disque virtuel.
- Mauvaise configuration réseau.
- Charge applicative.
- Absence de pilotes ou outils invités adaptés.
- Saturation du serveur physique.

Il faut mesurer les ressources et éviter de supposer que le nombre de vCPU suffit à expliquer toute lenteur.

### 21.5 L'hôte manque d'espace disque

Vérifie l'occupation du stockage de l'hôte.

Sur Linux :

```bash
df -h
```

Recherche également les disques virtuels, sauvegardes et snapshots qui occupent de l'espace.

Ne supprime pas arbitrairement des fichiers de VM ou des fichiers liés à un snapshot. Il faut identifier leur fonction et suivre la procédure de la plateforme.

### 21.6 La VM démarre, mais le service est indisponible

Le système invité peut fonctionner alors que l'application est arrêtée.

Dans une VM Linux :

```bash
systemctl --failed
```

Puis examine le service :

```bash
systemctl status nginx
```

Les causes peuvent inclure :

- Une configuration incorrecte.
- Un port déjà utilisé.
- Un manque d'espace disque.
- Un problème d'accès aux données.
- Un certificat expiré.
- Une erreur applicative.
- Une dépendance indisponible.

Le diagnostic doit se faire au niveau approprié.

### 21.7 La VM ne démarre plus après une modification

Vérifie :

- Les paramètres modifiés.
- L'espace de stockage.
- Le fichier ISO ou l'ordre de démarrage.
- Le contrôleur disque.
- L'état des disques.
- Les journaux de l'hyperviseur.
- Les ressources de l'hôte.
- La compatibilité du système invité.

Il faut d'abord collecter les informations avant de supprimer un disque, une configuration ou un snapshot.

### 21.8 L'interface Web de Proxmox est inaccessible

Vérifie :

- L'état du serveur.
- L'adresse IP de gestion.
- La passerelle.
- Le DNS.
- Le réseau du poste d'administration.
- Le pare-feu.
- La connectivité vers le port de gestion.
- Le certificat et le nom du serveur.
- Les journaux de la plateforme.

Ne modifie pas le bridge de gestion sans avoir identifié une méthode de récupération d'accès si la configuration est erronée.

## 22. Bonnes pratiques de gestion des images et des modèles

### 22.1 Pourquoi utiliser des images de référence ?

Une image de référence permet de standardiser les installations et de réduire les différences entre les systèmes.

Elle peut inclure :

- Le système d'exploitation.
- Les mises à jour.
- Certains composants communs.
- Une configuration de base.
- Les outils nécessaires.

Une image doit être entretenue et mise à jour. Une image ancienne peut reproduire des vulnérabilités ou des configurations obsolètes sur toutes les nouvelles VM créées à partir d'elle.

### 22.2 Template et clone

Un template est un modèle destiné à servir de base à la création d'autres VM.

Un clone est une nouvelle instance créée à partir d'une VM ou d'un modèle.

Selon la plateforme, les templates et clones peuvent être gérés de manières différentes.

Avant d'utiliser un clone comme serveur distinct, il faut vérifier :

- Le nom de machine.
- Les adresses IP.
- Les identifiants.
- Les certificats.
- Les clés SSH.
- L'identité de l'application.
- Les paramètres réseau.
- Les éventuels agents d'administration.

### 22.3 Préparer une image propre

Une image de référence ne doit pas contenir de secrets personnels ou d'identifiants réutilisables qui seraient copiés dans chaque VM.

Les mécanismes de préparation du système dépendent du système invité.

Il faut notamment veiller à la gestion des clés, des comptes locaux, des journaux et des identifiants propres à chaque machine.

### 22.4 Documenter les modèles

Pour chaque image :

- Indique le système d'exploitation.
- Note la version.
- Note la date de préparation.
- Enregistre les mises à jour appliquées.
- Documente les composants installés.
- Vérifie les paramètres de sécurité.
- Prévois une procédure de retrait de l'image obsolète.

## 23. Travaux pratiques de synthèse

### TP 1 — Créer et administrer une VM Linux avec KVM

**Objectif :** installer une VM de bout en bout.

Étapes :

1. Vérifier la virtualisation matérielle.
2. Installer QEMU/KVM et libvirt.
3. Vérifier le réseau virtuel.
4. Préparer une ISO Linux.
5. Créer la VM.
6. Installer le système invité.
7. Démarrer le système.
8. Vérifier son adresse IP.
9. Tester la connectivité.
10. Arrêter la VM proprement.
11. La redémarrer.
12. Produire une fiche d'inventaire.

Résultat attendu : une VM Linux fonctionnelle et documentée.

### TP 2 — Créer une VM Proxmox

**Objectif :** comprendre l'interface d'administration d'une plateforme.

Étapes :

1. Accéder à Proxmox.
2. Identifier le nœud.
3. Examiner les stockages.
4. Importer une ISO.
5. Créer une VM.
6. Configurer CPU et mémoire.
7. Choisir un disque virtuel.
8. Configurer l'interface réseau.
9. Démarrer la VM.
10. Installer le système invité.
11. Vérifier la connectivité.
12. Documenter les paramètres.

Résultat attendu : une VM fonctionnelle gérée par Proxmox VE.

### TP 3 — Explorer VMware vSphere

**Objectif :** comprendre la structure d'une plateforme VMware.

Étapes :

1. Identifier l'hôte ESXi ou l'environnement de laboratoire disponible.
2. Examiner l'interface de gestion.
3. Identifier les réseaux virtuels.
4. Identifier les datastores.
5. Créer une VM de test.
6. Installer un système invité.
7. Vérifier les ressources.
8. Vérifier l'accès réseau.
9. Documenter les paramètres.
10. Étudier les options de sauvegarde disponibles.

Résultat attendu : une fiche décrivant les composants et leur rôle.

### TP 4 — Comparer les environnements

**Objectif :** comparer les trois plateformes à partir d'un besoin réel.

Crée un tableau de comparaison pour une VM Linux comprenant :

- CPU.
- Mémoire.
- Disque.
- Interface réseau.
- Support d'installation.
- Démarrage.
- Arrêt.
- Console.
- Sauvegarde.
- Export ou migration, selon les capacités de chaque plateforme.

Résultat attendu : une comparaison claire des opérations d'administration.

### TP 5 — Préparer une procédure de sauvegarde

**Objectif :** apprendre à protéger les machines virtuelles.

Étapes :

1. Identifier les VM à sauvegarder.
2. Déterminer les données essentielles.
3. Choisir une destination adaptée.
4. Définir la fréquence.
5. Définir la rétention.
6. Protéger l'accès aux copies.
7. Effectuer une sauvegarde de test.
8. Restaurer une VM ou ses données dans un environnement isolé.
9. Vérifier le système et les applications.
10. Documenter la durée et le résultat.

Résultat attendu : une procédure de sauvegarde et de restauration testée.

## 24. Exercices avec corrigés

### Exercice 1 — Comprendre l'hyperviseur

Un serveur possède 16 cœurs physiques et héberge plusieurs VM.

**Question :** chaque vCPU attribué représente-t-il un cœur physique exclusivement réservé à la VM ?

**Corrigé :** non. Un vCPU représente un processeur virtuel que l'hyperviseur planifie sur les ressources physiques. Le nombre de vCPU ne correspond pas nécessairement au nombre de cœurs physiques réservés.

### Exercice 2 — Choisir un mode réseau

Une VM doit télécharger des paquets depuis Internet, mais elle ne doit pas être directement accessible depuis les autres machines du réseau local.

**Question :** quel mode réseau peut être adapté ?

**Corrigé :** un réseau NAT est généralement approprié pour ce besoin, à condition que la politique réseau et les règles de filtrage soient cohérentes.

### Exercice 3 — VM inaccessible

Une VM est démarrée mais ne répond pas au réseau local.

**Question :** quelles vérifications effectuer ?

**Corrigé :** vérifier le mode réseau, l'adresse IP, la passerelle, le DNS, les routes, le bridge ou le commutateur virtuel, les VLAN éventuels et les règles de pare-feu.

### Exercice 4 — Choisir entre VM et conteneur

Une équipe doit exécuter un serveur Linux avec un environnement complet et des composants ayant des besoins système particuliers.

**Question :** pourquoi une VM peut-elle être préférable ?

**Corrigé :** une VM fournit son propre noyau invité et un environnement système complet. Un conteneur Linux classique partage le noyau de l'hôte et ne fournit pas la même frontière système.

### Exercice 5 — KVM et QEMU

Un administrateur affirme que KVM est l'outil complet de création et de gestion des VM.

**Question :** pourquoi cette description est-elle incomplète ?

**Corrigé :** KVM fournit les fonctions de virtualisation du noyau. QEMU fournit notamment le modèle des périphériques et l'exécution des VM. libvirt et des outils comme `virsh` ajoutent une couche d'administration.

### Exercice 6 — Choisir une plateforme intégrée

Une petite entreprise veut gérer ses VM depuis une interface Web et disposer d'outils de sauvegarde et de cluster intégrés.

**Question :** quelle plateforme peut être adaptée ?

**Corrigé :** Proxmox VE est une possibilité pertinente à étudier. La décision dépend du matériel, des exigences, des compétences, du coût total et des besoins de support.

### Exercice 7 — Snapshot ou sauvegarde ?

Avant une mise à jour, un administrateur crée un snapshot et affirme qu'il n'a plus besoin de sauvegarder la VM.

**Question :** pourquoi ce raisonnement est-il incorrect ?

**Corrigé :** le snapshot peut dépendre du stockage de la VM et n'offre pas nécessairement une copie indépendante. Une sauvegarde séparée est nécessaire pour la récupération après certains incidents.

### Exercice 8 — Panne d'un hôte

Un serveur physique héberge huit VM. L'hôte tombe en panne.

**Question :** les VM redémarrent-elles automatiquement ailleurs ?

**Corrigé :** uniquement si une architecture et des mécanismes adaptés sont prévus, avec une capacité de reprise, un stockage accessible ou une méthode de récupération compatible. Une seule machine physique ne fournit pas de haute disponibilité au niveau de l'hôte.

### Exercice 9 — Capacité mémoire

Un hôte dispose de 8 Go de RAM et l'administrateur attribue 8 Go à une seule VM.

**Question :** quel est le risque ?

**Corrigé :** l'hôte et les services de virtualisation ont aussi besoin de mémoire. L'attribution peut entraîner une saturation ou empêcher le bon fonctionnement du système. Il faut dimensionner la VM en gardant une marge suffisante.

### Exercice 10 — Choisir entre KVM et VMware

Un administrateur veut apprendre la virtualisation Linux et gérer les VM par commandes.

**Question :** quel environnement est particulièrement adapté à l'apprentissage des composants Linux ?

**Corrigé :** KVM avec QEMU et libvirt est particulièrement formateur pour comprendre le fonctionnement et l'administration de la virtualisation sous Linux. Il existe aussi des interfaces graphiques compatibles.

## 25. Projet pratique final

### 25.1 Contexte

Une petite entreprise souhaite créer un environnement de test qui hébergera :

- Un serveur Web Linux.
- Un serveur de base de données de test.
- Un serveur Windows de laboratoire.
- Un poste client de test.

Les machines doivent pouvoir communiquer sur un réseau privé ou adapté au laboratoire. L'administrateur doit pouvoir arrêter, redémarrer, sauvegarder et restaurer les VM.

### 25.2 Architecture proposée

```text
                  HÔTE DE VIRTUALISATION
                           |
                 +---------+---------+
                 |                   |
                 v                   v
             Réseau VM           Stockage VM
                 |                   |
       +---------+---------+         |
       |         |         |         |
       v         v         v         v
    VM-WEB    VM-DB     VM-WIN    Disques virtuels
       |
       v
   Client de test

En complément :
  Images ISO
  Inventaire des VM
  Sauvegardes séparées
  Documentation d'exploitation
```

### 25.3 Travail demandé

Tu dois produire :

1. Un schéma d'architecture.
2. Un inventaire matériel.
3. Un tableau de dimensionnement CPU et mémoire.
4. Une organisation du stockage.
5. Une stratégie de réseau.
6. La liste des VM.
7. Le rôle de chaque VM.
8. Les procédures de création.
9. Les procédures d'arrêt et de redémarrage.
10. Une stratégie de sauvegarde.
11. Une procédure de restauration.
12. Une fiche de diagnostic.

### 25.4 Critères de réussite

Le projet est réussi si :

- L'hyperviseur est opérationnel.
- Les VM sont créées et démarrent correctement.
- Le réseau fonctionne selon le scénario attendu.
- Chaque VM dispose des ressources nécessaires.
- L'inventaire est documenté.
- Les sauvegardes sont conservées dans un emplacement approprié.
- Une restauration de test est réussie.
- Les opérations courantes peuvent être reproduites à partir de la documentation.

## 26. Défi final — Choisir et exploiter une plateforme de virtualisation

Une entreprise possède un serveur physique et veut héberger quatre systèmes :

- Un serveur Web Linux.
- Une base de données Linux.
- Un serveur Windows de test.
- Une VM de laboratoire réseau.

Tu dois comparer trois options : KVM/libvirt, Proxmox VE et VMware.

### Partie A — Choix de la plateforme

Compare les trois environnements selon :

- La facilité de déploiement.
- L'administration.
- La compatibilité matérielle.
- Le réseau.
- Le stockage.
- Les sauvegardes.
- L'évolution vers plusieurs hôtes.
- Les compétences nécessaires.
- Les licences et le coût total.

Justifie le choix final au regard du besoin de l'entreprise.

### Partie B — Dimensionnement

Détermine :

- Le nombre de vCPU par VM.
- La mémoire.
- Le stockage.
- Les réseaux virtuels.
- La capacité disponible pour l'hôte.
- La marge nécessaire.

Les valeurs doivent être justifiées par les besoins et les mesures prévues.

### Partie C — Réseau

Prépare :

- Le réseau d'administration.
- Le réseau applicatif.
- Le réseau isolé de laboratoire.
- Les règles de connectivité.
- Les éventuels VLAN.
- Les moyens de diagnostic.

### Partie D — Protection des données

Définis :

- Les VM à sauvegarder.
- La fréquence.
- La rétention.
- La destination des copies.
- La procédure de restauration.
- Les tests de validation.

### Partie E — Exploitation

Rédige les procédures pour :

- Créer une VM.
- Démarrer et arrêter une VM.
- Modifier les ressources.
- Examiner le stockage.
- Diagnostiquer un problème réseau.
- Mettre à jour l'hyperviseur.
- Restaurer une VM.
- Documenter une modification.

Le résultat attendu est un dossier d'exploitation reproductible et non simplement une liste de commandes.

## 27. Fiche de révision rapide

| Besoin | Outil ou concept |
|---|---|
| Vérifier les capacités CPU | `lscpu` |
| Examiner le périphérique KVM | `ls -l /dev/kvm` |
| Lister les VM libvirt | `virsh list --all` |
| Démarrer une VM KVM | `virsh start nom-vm` |
| Demander un arrêt propre | `virsh shutdown nom-vm` |
| Consulter les détails d'une VM | `virsh dominfo nom-vm` |
| Lister les disques d'une VM | `virsh domblklist nom-vm` |
| Lister les interfaces d'une VM | `virsh domiflist nom-vm` |
| Gérer graphiquement KVM | `virt-manager` |
| Créer une VM depuis la ligne de commande | `virt-install` |
| Administrer Proxmox | Interface Web et outils Proxmox |
| Gérer un hôte VMware ESXi | Interface de gestion disponible |
| Administrer plusieurs hôtes VMware | vCenter, lorsque prévu |
| Examiner les adresses d'une VM Linux | `ip -br address` |
| Examiner la route par défaut | `ip route` |
| Vérifier un service Linux | `systemctl status nom-service` |
| Vérifier l'espace disque | `df -h` |
| Examiner l'état des services en échec | `systemctl --failed` |

Ces commandes et interfaces dépendent du système installé et des composants disponibles.

## 28. Bonnes pratiques à retenir

### Matériel et dimensionnement

- Vérifie la virtualisation matérielle.
- Prévois suffisamment de mémoire.
- Surveille la capacité du stockage.
- Évite de saturer l'hôte.
- Dimensionne les VM selon la charge.
- Ne considère pas un vCPU comme un cœur physique réservé.

### Réseau

- Identifie le mode réseau de chaque VM.
- Utilise NAT pour les laboratoires simples lorsque cela convient.
- Utilise un bridge uniquement lorsque l'accès direct au réseau est souhaité.
- Isole les tests qui peuvent perturber le réseau.
- Vérifie les adresses IP, les routes et le DNS.
- Protège l'administration de l'hyperviseur.

### Stockage

- Surveille l'espace libre.
- Documente les disques virtuels.
- Distingue snapshots et sauvegardes.
- Évite les suppressions manuelles de fichiers de VM.
- Teste les restaurations.
- Protège les copies contre les suppressions accidentelles.

### Administration

- Documente les noms et les rôles des VM.
- Utilise des comptes adaptés aux opérations.
- Protège les accès d'administration.
- Vérifie la configuration avant les modifications importantes.
- Planifie les mises à jour.
- Contrôle les résultats après chaque opération.

### Sécurité

- Applique le principe du moindre privilège.
- Protège le réseau de gestion.
- Limite les accès aux consoles.
- Maintiens les systèmes à jour.
- Sépare les environnements de production et de test.
- Ne stocke pas de secrets dans les images de référence.
- Conserve des sauvegardes indépendantes.

## 29. Glossaire

**Virtualisation :** technique qui permet de présenter des ressources informatiques virtuelles à un système ou à une application.

**Hyperviseur :** couche logicielle qui permet d'exécuter et de gérer des machines virtuelles.

**Machine virtuelle (VM) :** environnement informatique disposant de matériel virtuel et d'un système invité.

**Hôte :** système ou serveur qui exécute les machines virtuelles.

**Système invité :** système d'exploitation installé dans une VM.

**Hyperviseur de type 1 :** architecture de virtualisation conçue pour fonctionner directement sur le matériel ou au moyen d'une plateforme serveur dédiée.

**Hyperviseur de type 2 :** hyperviseur exécuté comme application sur un système hôte existant.

**KVM :** technologie de virtualisation intégrée au noyau Linux.

**QEMU :** logiciel d'émulation et de virtualisation utilisé notamment avec KVM.

**libvirt :** couche d'administration permettant de gérer des VM et d'autres ressources de virtualisation.

**`virsh` :** outil d'administration en ligne de commande pour libvirt.

**`virt-manager` :** interface graphique de gestion des VM libvirt.

**Proxmox VE :** plateforme de virtualisation intégrée basée sur Debian, KVM/QEMU, LXC et des outils d'administration.

**ESXi :** hyperviseur serveur VMware.

**vSphere :** plateforme de virtualisation serveur de VMware.

**vCenter Server :** composant de gestion centralisée d'environnements vSphere.

**vCPU :** processeur virtuel attribué à une machine virtuelle.

**RAM :** mémoire vive utilisée par l'hôte et les systèmes invités.

**VHDX :** format de disque virtuel utilisé notamment par Hyper-V.

**QCOW2 :** format d'image disque utilisé avec QEMU, qui prend en charge certaines fonctionnalités comme l'allocation dynamique et les snapshots selon le scénario.

**VMDK :** format de disque virtuel utilisé dans l'écosystème VMware.

**NAT :** mécanisme de traduction d'adresses permettant notamment aux VM d'accéder à un réseau extérieur à travers l'hôte ou un routeur.

**Bridge :** commutateur logiciel qui relie des interfaces réseau virtuelles et physiques.

**Snapshot / checkpoint :** capture d'un état d'une VM selon les mécanismes de la plateforme.

**Clone :** nouvelle VM créée à partir d'une autre VM ou d'un modèle.

**Template :** modèle servant de base à la création de VM.

**Sauvegarde :** copie conservée pour permettre une restauration après un incident.

**Haute disponibilité :** mécanismes visant à réduire les interruptions de service, notamment grâce à des hôtes ou ressources de secours.

## 30. Documentation officielle

### KVM, QEMU et libvirt

- [Documentation Ubuntu Server — Virtualisation](https://ubuntu.com/server/docs/how-to/virtualisation/)
- [Installer et configurer libvirt](https://ubuntu.com/server/docs/how-to/virtualisation/libvirt/)
- [Virtual Machine Manager](https://ubuntu.com/server/docs/how-to/virtualisation/virtual-machine-manager/)
- [Documentation QEMU](https://www.qemu.org/docs/master/)
- [Documentation de `virsh`](https://www.libvirt.org/manpages/virsh.html)
- [Documentation de `virt-install`](https://manpages.debian.org/unstable/virtinst/virt-install.1.en.html)
- [Documentation du noyau Linux — KVM](https://docs.kernel.org/virt/kvm/api.html)

### Proxmox VE

- [Documentation officielle de Proxmox VE](https://www.proxmox.com/en/downloads/proxmox-virtual-environment/documentation)
- [Prérequis matériels](https://www.proxmox.com/en/products/proxmox-virtual-environment/requirements)
- [Guide de démarrage](https://www.proxmox.com/en/products/proxmox-virtual-environment/get-started)
- [Fonctionnalités de Proxmox VE](https://proxmox.com/en/products/proxmox-virtual-environment/features)

### VMware

- [Plateforme VMware vSphere](https://www.vmware.com/products/cloud-infrastructure/vsphere)
- [Base de connaissances Broadcom](https://knowledge.broadcom.com/)
- [Installation et mise à niveau de vCenter Server](https://knowledge.broadcom.com/external/article/312076/install-and-upgrade-vcenter-server-and-e.html)

Les prérequis matériels, les versions prises en charge, les options et les droits d'utilisation doivent être vérifiés avant tout déploiement.

## Conclusion

La virtualisation permet de regrouper plusieurs environnements informatiques sur un même serveur physique tout en conservant des systèmes invités distincts.

KVM associé à QEMU et libvirt fournit une solution de virtualisation Linux flexible. Proxmox VE intègre ces technologies dans une plateforme de gestion plus complète. VMware propose un écosystème de virtualisation de bureau et de serveur avec des outils dédiés à l'administration des infrastructures.

Les compétences fondamentales restent similaires : savoir dimensionner les machines virtuelles, comprendre les réseaux, organiser le stockage, protéger les systèmes, administrer les ressources et tester les restaurations.

La règle essentielle pour ce niveau débutant est la suivante : **une VM correctement configurée n'est pas seulement une machine qui démarre. C'est une machine dont les ressources, le réseau, le stockage, la sécurité et la méthode de récupération sont compris et documentés.**