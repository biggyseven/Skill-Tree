
# MPLS-TP & Métro Ethernet — Niveau intermédiaire

**Nom du fichier :** `telecom-mpls-tp-intermediaire.md`  
**Module :** Opérateurs & Télécoms  
**Niveau :** Intermédiaire  
**Domaine :** Réseaux de transport, Ethernet opérateur, MPLS-TP, OAM et protection de services  
**Public cible :** Techniciens réseau, techniciens transmission, administrateurs réseau, techniciens NOC et professionnels préparant une spécialisation dans les réseaux d'opérateurs.

## 1. Présentation du cours

### 1.1. Contexte professionnel

Un opérateur télécom ne fournit pas uniquement un accès à Internet. Il doit également transporter les données de ses clients professionnels, relier des stations mobiles, interconnecter des centres de données, connecter des agences bancaires et fournir des circuits Ethernet entre plusieurs villes.

Pour réaliser ces services, l'opérateur peut utiliser un réseau de collecte et de transport métropolitain.

Deux technologies sont particulièrement importantes dans ce contexte :

- **Métro Ethernet :** fournit des services Ethernet sur une infrastructure métropolitaine partagée ou dédiée.
- **MPLS-TP :** permet de construire des chemins de transport à commutation de labels, avec des mécanismes d'exploitation, d'administration, de maintenance et de protection adaptés aux réseaux de transport.

Ces technologies ne remplissent pas exactement le même rôle. Métro Ethernet décrit surtout les services Ethernet et leur transport, tandis que MPLS-TP définit une approche de transport en s'appuyant sur des chemins à labels et des mécanismes de supervision et de protection.

Elles peuvent être utilisées séparément ou conjointement dans une architecture opérateur.

### 1.2. Objectifs pédagogiques

À la fin du cours, l'apprenant doit être capable de :

1. Décrire l'architecture d'un réseau Métro Ethernet.
2. Distinguer les services E-Line, E-LAN et E-Tree.
3. Expliquer les fonctions d'un VLAN, du QinQ et du MTU.
4. Comprendre les principes du transport MPLS-TP.
5. Distinguer un chemin de transport d'un service client.
6. Expliquer les rôles des LSP, des labels et des pseudowires.
7. Comprendre les fonctions OAM et les mécanismes de protection.
8. Interpréter les notions de continuité, de défaut, de délai et de perte de trames.
9. Concevoir une architecture métropolitaine simple avec redondance.
10. Diagnostiquer les problèmes de VLAN, de MTU, de transport et de connectivité.
11. Construire un plan de validation et une procédure de mise en service.
12. Comprendre les différences entre MPLS classique, MPLS-TP et Ethernet opérateur.

### 1.3. Prérequis

Il est recommandé de connaître :

- les modèles OSI et TCP/IP ;
- les adresses MAC et le fonctionnement d'un commutateur Ethernet ;
- les VLAN 802.1Q ;
- les notions de routage IP ;
- les interfaces physiques et logiques ;
- les bases de la fibre optique ;
- les notions de débit, de latence et de perte de paquets.

Le cours précédent, consacré à la fibre optique et au DWDM, fournit les bases nécessaires pour comprendre le support physique sur lequel peut être construit le réseau de transport.

### 1.4. Organisation du cours

Le parcours est organisé comme suit :

1. Architecture Métro Ethernet.
2. Services Ethernet opérateur.
3. VLAN, QinQ, MTU et isolation des clients.
4. Principes MPLS et MPLS-TP.
5. LSP, pseudowires et séparation des services.
6. OAM et supervision.
7. Protection et résilience.
8. QoS et ingénierie de trafic.
9. Sécurité et exploitation.
10. Travaux pratiques et dépannage.
11. Exercices corrigés.
12. Projet final corrigé.

## 2. Comprendre un réseau Métro Ethernet

### 2.1. Définition

Un réseau Métro Ethernet est un réseau de transport couvrant généralement une ville ou une zone métropolitaine.

Il permet de transporter des services Ethernet entre des clients et les points de présence de l'opérateur.

Le réseau peut relier :

- des entreprises ;
- des sites administratifs ;
- des agences bancaires ;
- des centres de données ;
- des stations de base mobiles ;
- des points de présence Internet ;
- des réseaux de collecte ;
- des équipements de transport interurbain.

Le terme « Métro » désigne ici une portée géographique métropolitaine. Il ne signifie pas nécessairement que le réseau utilise une technologie particulière.

### 2.2. Architecture générale

```text
                    RÉSEAU MÉTROPOLITAIN D'UN OPÉRATEUR

       Client A                  Noyau Métro                 Client B
   +--------------+        +--------------------+        +--------------+
   | LAN entreprise|       |                    |        | LAN entreprise|
   | VLAN 10       |       |                    |        | VLAN 20       |
   +------+-------+        |                    |        +-------+------+
          |                |                    |                |
          v                |                    |                v
   +--------------+        |                    |        +--------------+
   | CE-A          |       |                    |        | CE-B          |
   | Équipement    |       |                    |        | Équipement    |
   | client        |       |                    |        | client        |
   +------+-------+        |                    |        +-------+------+
          |                |                    |                |
          v                v                    v                v
   +--------------+   +----------+        +----------+   +--------------+
   | PE-A          |---| P-1      |--------| P-2      |---| PE-B          |
   | Bord opérateur|   | Transport|        | Transport|   | Bord opérateur|
   +--------------+   +----------+        +----------+   +--------------+
                              \              /
                               \            /
                              Fibre / DWDM
```

Dans ce schéma :

- **CE** (*Customer Edge*) désigne l'équipement côté client.
- **PE** (*Provider Edge*) désigne l'équipement de bord de l'opérateur.
- **P** désigne un équipement de transport situé dans le réseau de l'opérateur.

Ces rôles sont conceptuels. Un équipement physique peut réaliser plusieurs fonctions selon l'architecture.

Le client peut voir une interface Ethernet simple alors que l'opérateur utilise plusieurs technologies internes pour transporter le trafic.

### 2.3. Pourquoi séparer le réseau client du réseau de transport ?

L'opérateur doit transporter les données de nombreux clients sur une infrastructure commune.

Il faut donc empêcher qu'un client puisse accéder accidentellement au trafic d'un autre.

La séparation peut être réalisée par différentes méthodes :

- VLAN ;
- QinQ ;
- instances de service dédiées ;
- pseudowires ;
- chemins de transport MPLS ;
- mécanismes de filtrage ;
- politiques d'accès et de contrôle.

La méthode dépend du service vendu et de l'architecture du réseau.

**Point important :** l'utilisation d'un VLAN ou d'un label MPLS ne remplace pas à elle seule une architecture de sécurité complète.

## 3. Les services Ethernet opérateur

### 3.1. Service E-Line

E-Line est un service Ethernet de type point à point.

Il relie deux interfaces de service et permet de transporter des trames Ethernet entre deux sites.

Exemples :

- interconnexion entre deux agences ;
- liaison entre un client et un centre de données ;
- raccordement d'un site à un point de présence opérateur ;
- liaison de collecte entre deux équipements.

```text
                      SERVICE E-LINE

     Site A                                              Site B
  +-----------+                                      +-----------+
  | Réseau A  |                                      | Réseau B  |
  +-----+-----+                                      +-----+-----+
        |                                                  |
        v                                                  v
  +-----------+        Réseau opérateur              +-----------+
  | UNI-A     |======================================| UNI-B     |
  | Port client|          Service point à point      | Port client|
  +-----------+                                      +-----------+
```

L'opérateur doit assurer l'isolation du service et respecter les caractéristiques contractuelles définies.

### 3.2. Service E-LAN

E-LAN est un service Ethernet multipoint à multipoint.

Il permet à plusieurs sites de communiquer dans un même service logique, comme s'ils étaient reliés à un réseau Ethernet commun, sous réserve des règles de service et de l'architecture.

```text
                         SERVICE E-LAN

                        +------------------+
                        | Réseau opérateur |
                        |                  |
                        +--+-------+-------+
                           |       |
                  +--------+       +--------+
                  |                         |
                  v                         v
              +-------+                 +-------+
              | Site A|                 | Site B|
              +-------+                 +-------+
                           |
                           v
                       +-------+
                       | Site C|
                       +-------+
```

Ce modèle est utile pour interconnecter plusieurs agences ou sites d'une entreprise.

Le service peut nécessiter une gestion attentive du trafic de diffusion, de la table MAC et des limites de bande passante.

### 3.3. Service E-Tree

E-Tree est un service multipoint avec une topologie logique racine-feuilles.

Les feuilles peuvent généralement communiquer avec la racine, mais la communication directe entre feuilles peut être interdite selon le modèle de service.

Exemple : des agences communiquent avec un siège central, mais ne doivent pas échanger directement leurs trames entre elles.

```text
                         SERVICE E-TREE

                              +---------+
                              | Racine  |
                              | Siège   |
                              +----+----+
                                   |
                      +------------+------------+
                      |            |            |
                      v            v            v
                  +-------+    +-------+    +-------+
                  |Feuille|    |Feuille|    |Feuille|
                  | Site A|    | Site B|    | Site C|
                  +-------+    +-------+    +-------+

             Feuille A <----X----> Feuille B
             Communication directe interdite
             dans le modèle de service considéré
```

Les règles précises dépendent du service fourni et de sa mise en œuvre.

### 3.4. Comparaison des services

| Caractéristique | E-Line | E-LAN | E-Tree |
|---|---|---|---|
| Topologie logique | Point à point | Multipoint à multipoint | Racine-feuilles |
| Nombre de sites | Généralement 2 | Plusieurs | Plusieurs |
| Communication entre sites | Entre les deux extrémités | Entre membres autorisés | Selon les rôles racine et feuille |
| Cas d'usage | Liaison dédiée entre deux sites | Réseau d'entreprise multisite | Agences rattachées à un siège |
| Contrôle de diffusion | Dépend du service et du transport | Important | Dépend du service et de la topologie |

Ces noms sont associés aux modèles de services Ethernet utilisés dans les spécifications MEF. L'implémentation concrète dépend de l'opérateur.

## 4. UNI, NNI et séparation des domaines

### 4.1. UNI : User Network Interface

L'UNI est le point de démarcation entre le réseau du client et le réseau de l'opérateur pour un service Ethernet.

Il définit notamment :

- l'interface de raccordement ;
- les paramètres du service ;
- les règles de classification ;
- les caractéristiques de bande passante ;
- les règles de maintenance et de supervision convenues.

L'UNI peut être une interface physique ou être associée à une interface logique selon la solution.

### 4.2. NNI : Network-to-Network Interface

Une NNI est une interface d'interconnexion entre réseaux ou domaines de réseau.

Dans un contexte opérateur, elle peut servir à interconnecter :

- deux réseaux de transport ;
- deux domaines d'un même opérateur ;
- deux opérateurs ;
- une infrastructure de collecte et une infrastructure de cœur.

Les règles de transport, de VLAN, de QoS et de supervision doivent être cohérentes aux frontières concernées.

### 4.3. Point de démarcation et responsabilité

Un service doit préciser la responsabilité de chaque partie.

Exemple :

```text
Réseau client                Point de démarcation               Opérateur
+------------+                    UNI                         +-----------+
| Switch LAN |---------------------||-------------------------| PE        |
+------------+                    ||                         +-----------+
                                  ||
                     Contrat et paramètres du service
```

Le point de démarcation aide à déterminer si un incident se situe dans le réseau client ou dans le réseau de l'opérateur.

Il faut toutefois disposer de mesures et d'une méthode de diagnostic partagée pour conclure correctement.

## 5. VLAN et transport des services Ethernet

### 5.1. Rappel sur les VLAN

Un VLAN permet de séparer logiquement des domaines de couche 2 sur une infrastructure Ethernet.

La norme IEEE 802.1Q définit le mécanisme courant de marquage VLAN.

Une trame Ethernet marquée comprend un champ de tag qui contient notamment un identifiant VLAN.

Les VLAN permettent de séparer plusieurs domaines logiques sans exiger une infrastructure physique entièrement distincte pour chacun.

### 5.2. Exemple d'isolation

```text
                  INFRASTRUCTURE PARTAGÉE

 Client A -- VLAN 100 --\
                         \
                          +---- Réseau Ethernet ----+
                         /                          |
 Client B -- VLAN 200 --/                           |
                                                    |
                                    +---------------+---------------+
                                    |                               |
                                    v                               v
                              Service A                        Service B
                              VLAN 100                         VLAN 200
```

Une isolation correcte nécessite une configuration cohérente de bout en bout.

Il ne suffit pas de créer un VLAN sur un seul commutateur : il faut vérifier son admission sur les ports, sa propagation et son association au bon service.

### 5.3. Port access et port trunk

Un port d'accès est généralement associé à un VLAN de service non marqué du point de vue du terminal connecté.

Un port trunk transporte plusieurs VLAN, généralement identifiés par des tags 802.1Q.

La terminologie et le comportement exacts dépendent des constructeurs et du mode de configuration.

Exemple conceptuel :

```text
Terminal client
     |
     | Trames non marquées
     v
+------------------+
| Port access      |
| VLAN 100         |
+------------------+

Équipement réseau
     |
     | Trames marquées VLAN 100, 200, 300
     v
+------------------+
| Port trunk       |
| VLAN autorisés   |
+------------------+
```

Une erreur de VLAN natif, de VLAN autorisé ou de classification peut entraîner une interruption ou une fuite de trafic entre domaines.

## 6. QinQ : empilement de VLAN

### 6.1. Pourquoi utiliser QinQ ?

QinQ, souvent associé à IEEE 802.1ad, permet d'ajouter un tag VLAN externe à une trame qui possède déjà un tag VLAN interne.

Le VLAN interne représente généralement le domaine du client.

Le VLAN externe peut représenter le service ou le domaine de transport de l'opérateur.

```text
                    TRAME AVANT QINQ

+----------+-----------+-------------+----------+
| MAC dest.| MAC source| VLAN client | Données  |
+----------+-----------+-------------+----------+


                    TRAME APRÈS QINQ

+----------+-----------+-------------+-------------+----------+
| MAC dest.| MAC source| VLAN externe| VLAN interne| Données  |
+----------+-----------+-------------+-------------+----------+
                         Opérateur      Client
```

L'équipement de bord ajoute ou traite le tag externe selon la configuration.

À l'autre extrémité, le tag externe peut être retiré pour restituer le service au client.

### 6.2. Exemple d'utilisation

Un opérateur dessert 100 entreprises.

Chaque entreprise utilise ses propres VLAN internes. Certaines entreprises utilisent le même identifiant VLAN, par exemple VLAN 10.

L'opérateur peut utiliser des identifiants de service externes distincts pour séparer les clients.

Exemple conceptuel :

| Client | VLAN interne client | VLAN externe opérateur |
|---|---:|---:|
| Entreprise A | 10 | 3001 |
| Entreprise B | 10 | 3002 |
| Entreprise C | 20 | 3003 |

Le VLAN interne 10 peut ainsi exister dans plusieurs services indépendants, à condition que la classification et l'isolation soient correctement conçues.

### 6.3. Points de vigilance

QinQ exige de vérifier :

- la prise en charge des tags multiples ;
- les règles d'ajout et de retrait ;
- les VLAN autorisés ;
- la conservation du tag client ;
- les règles de priorité 802.1p ;
- le MTU ;
- le comportement des équipements intermédiaires ;
- les règles de maintenance OAM.

L'empilement de tags ajoute des octets à la trame. Une infrastructure qui accepte une trame simple peut rejeter une trame QinQ si sa taille dépasse le MTU pris en charge.

## 7. MTU et taille des trames

### 7.1. Définition

Le MTU (*Maximum Transmission Unit*) est la taille maximale d'une unité de données autorisée par une interface ou un chemin, selon le protocole et la couche considérés.

Dans Ethernet, la taille maximale autorisée dépend de la définition utilisée et du traitement des en-têtes.

Un MTU IP de 1500 octets ne signifie pas que la trame Ethernet entière fait 1500 octets.

### 7.2. Pourquoi le MTU est-il important en Métro Ethernet ?

Le réseau peut ajouter des informations de transport :

- tag VLAN ;
- second tag QinQ ;
- labels MPLS ;
- en-têtes de pseudowire ;
- encapsulations supplémentaires.

Chaque encapsulation ajoute une surcharge.

Si les équipements n'acceptent pas la taille nécessaire, certaines trames peuvent être rejetées.

Le problème peut toucher surtout les gros paquets, ce qui rend le diagnostic trompeur : les petits paquets passent, mais certaines applications échouent.

### 7.3. Exemple simplifié

Supposons un service avec :

- MTU IP : 1500 octets ;
- un tag VLAN client ;
- un tag VLAN opérateur ;
- une encapsulation de transport.

La taille nécessaire sur le chemin de transport sera supérieure à celle d'un paquet IP de 1500 octets.

Il faut ajouter les surcharges selon les en-têtes réellement présents, les éventuels en-têtes Ethernet et les définitions MTU des équipements.

Il n'existe pas une valeur universelle unique pour toutes les architectures MPLS-TP ou Métro Ethernet.

### 7.4. Symptômes d'un problème de MTU

- petits paquets transmis correctement ;
- gros paquets perdus ;
- certains tests applicatifs échouent ;
- fragmentation IP inattendue ;
- pertes uniquement sur un service encapsulé ;
- différences entre trafic client et trafic de supervision.

### 7.5. Méthode de vérification

1. Identifier la taille maximale attendue par le service.
2. Recenser les encapsulations de bout en bout.
3. Vérifier le MTU de chaque interface concernée.
4. Vérifier le MTU de transport et les limites des équipements.
5. Réaliser des tests avec plusieurs tailles de trames.
6. Vérifier les compteurs de rejet et les erreurs.
7. Valider le résultat avec la documentation du constructeur.

## 8. Introduction à MPLS

### 8.1. Qu'est-ce que MPLS ?

MPLS signifie *Multiprotocol Label Switching*.

Il s'agit d'une technique de transfert dans laquelle les paquets ou unités de données sont associés à des labels utilisés pour déterminer leur traitement dans le réseau.

Le label est généralement transporté entre les en-têtes de couche 2 et les en-têtes de couche 3 dans l'encapsulation MPLS classique.

MPLS est utilisé pour construire différents types de services et de chemins de transport, notamment dans les réseaux opérateurs.

### 8.2. Principe d'un label

Un label est une valeur courte utilisée par le réseau de transport pour identifier un traitement ou un chemin.

Dans un réseau MPLS classique, les routeurs peuvent notamment :

- pousser un label (*push*) ;
- échanger un label (*swap*) ;
- retirer un label (*pop*).

Ces opérations permettent de transférer les paquets dans le réseau selon les règles MPLS.

### 8.3. Exemple de chemin MPLS

```text
                  CHEMIN MPLS SIMPLIFIÉ

      Entrée                  Transit                  Sortie
  +------------+          +------------+          +------------+
  | Routeur PE |--------->| Routeur P  |--------->| Routeur PE |
  +------------+          +------------+          +------------+
        |                       |                        |
        | Push                  | Swap                   | Pop
        v                       v                        v

   Paquet client          Label échangé             Paquet remis
   +------------+         +----------------+         au service
   | IP / Data  |         | Label MPLS     |
   +------------+         +----------------+
```

Ce schéma illustre le principe de base. Les opérations exactes dépendent du chemin, de la configuration et des mécanismes de signalisation ou de provisionnement utilisés.

### 8.4. Label et adresse IP

Un label MPLS n'est pas une adresse IP.

L'adresse IP identifie une destination ou une interface logique dans le contexte IP.

Le label identifie un traitement de transfert dans le domaine MPLS.

Les deux mécanismes peuvent être utilisés conjointement, mais ils ne remplissent pas la même fonction.

## 9. Qu'est-ce que MPLS-TP ?

### 9.1. Définition

MPLS-TP signifie *Multiprotocol Label Switching Transport Profile*.

Il s'agit d'un profil de technologies MPLS conçu pour répondre aux exigences des réseaux de transport.

L'objectif est d'offrir des chemins de transport prévisibles et des mécanismes structurés de supervision, d'exploitation et de protection.

MPLS-TP est particulièrement associé aux besoins des opérateurs qui veulent contrôler explicitement les chemins de transport et surveiller leur disponibilité.

### 9.2. Pourquoi un profil de transport ?

Les réseaux de transport doivent répondre à des contraintes fortes :

- disponibilité élevée ;
- chemins de transport identifiables ;
- supervision de bout en bout ;
- localisation des défauts ;
- protection contre certaines pannes ;
- procédures d'exploitation maîtrisées ;
- séparation claire entre service client et transport.

MPLS-TP fournit un cadre adapté à ces objectifs.

Il ne signifie pas que chaque réseau doit utiliser exactement la même architecture. Les mécanismes disponibles dépendent des standards retenus et des implémentations.

### 9.3. MPLS classique et MPLS-TP

| Critère | MPLS classique | MPLS-TP |
|---|---|---|
| Objectif principal | Transport polyvalent de trafic et services | Profil adapté au transport |
| Contrôle des chemins | Peut être dynamique ou explicitement configuré | Favorise des chemins de transport contrôlés et identifiables |
| Exploitation | Dépend des protocoles et de l'architecture | Intègre des mécanismes de maintenance adaptés au transport |
| Protection | Plusieurs mécanismes possibles selon la solution | Mécanismes de protection de transport prévus par les spécifications |
| OAM | Dépend des protocoles et technologies utilisées | Rôle important dans la conception et l'exploitation |
| Usage | Cœur IP, VPN, ingénierie de trafic, services divers | Transport opérateur et services nécessitant un profil transport |

Il ne faut pas opposer ces technologies de façon absolue : MPLS-TP réutilise des principes MPLS, tout en définissant des fonctions et contraintes spécifiques au transport.

### 9.4. Le plan de données, le plan de contrôle et le plan de gestion

Un réseau de transport peut être étudié selon trois plans.

**Plan de données :** transporte les trames ou paquets.

**Plan de contrôle :** participe à l'établissement et à la gestion des chemins lorsque les protocoles de contrôle sont utilisés.

**Plan de gestion :** permet la configuration, la supervision et l'administration du réseau.

Dans MPLS-TP, les chemins peuvent être provisionnés par le plan de gestion ou établis avec des mécanismes de contrôle compatibles avec l'architecture retenue.

Il ne faut pas supposer que tous les réseaux MPLS-TP exécutent obligatoirement les mêmes protocoles de contrôle.

### 9.5. Provisionnement statique et contrôle dynamique

Un opérateur peut choisir de configurer explicitement les chemins.

Avantages possibles :

- comportement prévisible ;
- contrôle administratif ;
- topologie et chemins maîtrisés ;
- exploitation adaptée à un réseau de transport.

Limites possibles :

- nécessité de maintenir la cohérence des configurations ;
- risque d'erreur manuelle ;
- adaptation moins automatique aux changements si aucun mécanisme complémentaire n'est utilisé.

Une solution avec plan de contrôle peut automatiser certaines opérations, mais elle doit être conçue et exploitée selon les protocoles réellement pris en charge.

## 10. LSP : Label Switched Path

### 10.1. Définition

Un LSP (*Label Switched Path*) est un chemin suivi par le trafic dans un domaine MPLS.

Dans un contexte MPLS-TP, le LSP constitue un élément central du transport.

Il permet de définir un trajet entre une origine et une destination.

### 10.2. Exemple de LSP

```text
                     LSP DE TRANSPORT

                   Sens de transport
                         --------->

        +------+      +------+      +------+      +------+
        | PE-A |----->| P-1  |----->| P-2  |----->| PE-B |
        +------+      +------+      +------+      +------+
            \________________________________________/
                         LSP principal

        Chemin de transport identifié entre PE-A et PE-B
```

Dans une architecture réelle, le chemin peut traverser plusieurs équipements, interfaces et domaines.

### 10.3. LSP et service client

Un LSP décrit un chemin de transport.

Le service client décrit ce qui est livré au client : par exemple un circuit Ethernet entre deux UNI.

Plusieurs services peuvent utiliser des chemins de transport selon l'architecture et les mécanismes de multiplexage.

Il faut donc distinguer :

- le service vendu ;
- le chemin qui transporte le service ;
- les interfaces physiques ;
- les mécanismes de supervision ;
- les mécanismes de protection.

### 10.4. Chemins unidirectionnels et bidirectionnels

Un chemin peut être étudié selon son sens de circulation.

Dans les systèmes de transport, la surveillance et la protection peuvent nécessiter une coordination entre les deux directions.

Il ne faut pas supposer que la présence d'un chemin fonctionnel dans un sens garantit que le chemin opposé est correctement établi.

La conception doit préciser le comportement de chaque direction et la manière dont les défauts sont détectés.

## 11. Pseudowires et services Ethernet sur MPLS-TP

### 11.1. Définition d'un pseudowire

Un pseudowire est une émulation de service de couche 2 à travers un réseau de transport par paquets.

Il peut permettre de transporter un service Ethernet entre deux points, en s'appuyant sur un réseau de transport MPLS.

Le pseudowire ne constitue pas la fibre physique. Il représente un service logique transporté sur l'infrastructure.

### 11.2. Architecture simplifiée

```text
                SERVICE ETHERNET TRANSPORTÉ SUR MPLS-TP

       Site A                                                   Site B
  +---------------+                                       +---------------+
  | Équipement CE |                                       | Équipement CE |
  +-------+-------+                                       +-------+-------+
          |                                                       |
          v                                                       v
  +---------------+       Pseudowire logique              +---------------+
  | PE-A          |=======================================| PE-B          |
  | Bord opérateur|                                       | Bord opérateur|
  +-------+-------+                                       +-------+-------+
          |                                                       |
          +------------------ LSP de transport -------------------+
                            Réseau MPLS-TP
```

Le pseudowire transporte le service client au travers du LSP.

La façon exacte dont les trames sont encapsulées, étiquetées et supervisées dépend de l'implémentation.

### 11.3. Pourquoi séparer pseudowire et LSP ?

Cette séparation permet de distinguer deux fonctions :

- **LSP :** fournit le chemin de transport.
- **Pseudowire :** représente le service logique de couche 2.

Une panne du LSP peut affecter plusieurs services qui l'utilisent.

Une panne limitée à un pseudowire peut affecter un service particulier sans interrompre tous les services transportés par le même chemin.

### 11.4. Diagnostic par niveau

| Symptôme | Hypothèse à vérifier |
|---|---|
| Plusieurs services sur le même chemin échouent | Défaut du LSP ou de l'infrastructure commune |
| Un seul service échoue | Configuration ou état du pseudowire, VLAN ou interface client |
| Les deux extrémités du service sont actives mais aucune trame ne passe | Encapsulation, association du service ou défaut de transfert |
| Le transport fonctionne mais le client constate des pertes | QoS, MTU, erreurs d'interface ou problème côté client |
| Le service revient après un basculement | Défaut probable sur le chemin ou l'équipement initial, à confirmer par les journaux |

Ce tableau propose des hypothèses de diagnostic, pas des conclusions automatiques.

## 12. OAM : Operations, Administration and Maintenance

### 12.1. Pourquoi l'OAM est-il essentiel ?

OAM désigne les mécanismes d'exploitation, d'administration et de maintenance.

Dans un réseau opérateur, il ne suffit pas de savoir qu'une interface est physiquement active.

Il faut également pouvoir vérifier :

- que le service est joignable ;
- que le chemin est opérationnel ;
- qu'une panne est détectée ;
- que l'alarme est correctement propagée ;
- que le défaut peut être localisé ;
- que la restauration du service fonctionne comme prévu.

### 12.2. Les différents niveaux de supervision

```text
                  NIVEAUX DE SUPERVISION

  +--------------------------------------------------+
  | Service client                                   |
  | Test de connectivité, trafic, erreurs, SLA       |
  +--------------------------------------------------+
  | Service Ethernet / pseudowire                    |
  | Continuité, état du service, défaut de transport |
  +--------------------------------------------------+
  | Chemin de transport MPLS-TP                      |
  | Continuité du LSP, alarmes, protection           |
  +--------------------------------------------------+
  | Interfaces physiques                             |
  | État du port, erreurs, puissance optique         |
  +--------------------------------------------------+
  | Support physique                                 |
  | Fibre, connecteurs, épissures, pertes            |
  +--------------------------------------------------+
```

Un défaut doit être recherché au niveau pertinent.

Un port physiquement actif ne prouve pas que le service logique fonctionne. De même, une fibre optique correcte ne prouve pas que le LSP est correctement configuré.

### 12.3. Ethernet CFM

CFM signifie *Connectivity Fault Management*.

Les mécanismes CFM d'Ethernet, notamment ceux associés à IEEE 802.1ag, permettent de surveiller la connectivité et d'aider à localiser les défauts dans un domaine de maintenance.

Les concepts importants comprennent :

- les domaines de maintenance ;
- les niveaux de maintenance ;
- les points de maintenance ;
- les messages de vérification de continuité ;
- les messages de boucle et de trace selon les fonctions implémentées.

Le domaine de maintenance doit être conçu de façon à séparer les responsabilités et les niveaux d'exploitation.

### 12.4. Continuité Ethernet

Les messages de vérification de continuité permettent de vérifier périodiquement la présence d'un chemin entre des points de maintenance.

Une absence prolongée de messages attendus peut signaler un défaut.

Cependant, le seuil de détection dépend de la fréquence des messages, des temporisations et des règles configurées.

Une détection trop lente retarde la restauration. Une détection trop agressive peut provoquer de fausses alarmes en présence de pertes ponctuelles.

### 12.5. Y.1731

ITU-T Y.1731 définit des fonctions de maintenance et de mesure des performances pour les réseaux Ethernet.

Selon les équipements et les profils pris en charge, ces fonctions peuvent inclure :

- des mesures de délai ;
- des mesures de variation de délai ;
- des mesures de perte de trames ;
- des mécanismes de détection de défauts ;
- des fonctions associées à la supervision de service.

Il faut vérifier les fonctions réellement supportées par les équipements et leur interopérabilité.

### 12.6. OAM dans MPLS-TP

MPLS-TP possède des mécanismes OAM adaptés à la supervision des chemins de transport.

Les fonctions peuvent couvrir :

- la vérification de continuité ;
- la détection de défauts ;
- la localisation ;
- la vérification du chemin ;
- la surveillance de performances ;
- la coordination avec la protection.

Les spécifications MPLS-TP s'appuient notamment sur les recommandations et RFC associés à l'OAM MPLS et au transport.

Il est important de distinguer les mécanismes OAM Ethernet des mécanismes OAM MPLS-TP. Ils peuvent coexister, mais ils ne surveillent pas nécessairement le même niveau.

### 12.7. Alarmes de défaut

Une alarme doit être interprétée dans son contexte.

Exemples de défauts :

- perte de signal physique ;
- perte de continuité ;
- défaut de chemin ;
- défaut de pseudowire ;
- défaut de synchronisation ;
- dépassement de seuil de performance.

Un défaut détecté sur un niveau peut provoquer des alarmes sur les niveaux supérieurs.

Pour éviter les diagnostics erronés, il faut identifier l'alarme primaire et les alarmes secondaires qui en découlent.

## 13. Protection et résilience

### 13.1. Pourquoi protéger un réseau ?

Un opérateur doit limiter l'interruption de service provoquée par :

- une coupure de fibre ;
- la panne d'un port ;
- la panne d'un équipement ;
- la perte d'un lien ;
- un défaut de configuration ;
- une panne électrique ;
- un incident sur un site.

La protection repose sur des chemins ou des ressources alternatives, associés à des mécanismes de détection et de basculement.

### 13.2. Architecture non protégée

```text
                  ARCHITECTURE SANS CHEMIN ALTERNATIF

  PE-A -------- P-1 -------- P-2 -------- PE-B
                       X
                Coupure de liaison

  Résultat : le chemin unique est interrompu.
```

Si aucun chemin alternatif n'est disponible, le service peut rester indisponible jusqu'à la réparation ou à une reconfiguration.

### 13.3. Architecture protégée

```text
                    ARCHITECTURE AVEC DEUX CHEMINS

                         Chemin principal
                 +-----------------------------+
                 |                             |
                 v                             v
              +------+                      +------+
              | PE-A |----------------------| PE-B |
              +------+                      +------+
                 |                             ^
                 |                             |
                 +------ P-3 ------ P-4 -------+
                         Chemin de secours

  Objectif : préserver le service si le chemin principal échoue.
```

Ce schéma est logique. Dans une architecture réelle, il faut vérifier la diversité physique des chemins.

Deux chemins logiques qui utilisent le même conduit ou le même câble peuvent être interrompus par un incident physique unique.

### 13.4. Protection locale et protection de bout en bout

La protection peut agir :

- autour d'un lien ;
- autour d'un équipement ;
- sur une section ;
- sur un chemin de transport complet ;
- au niveau du service.

La protection locale peut réduire le temps nécessaire à la restauration lorsqu'un défaut est détecté près du point de panne.

La protection de bout en bout vise à basculer le trafic vers un chemin alternatif entre les extrémités concernées.

Le mécanisme exact dépend de l'architecture et des fonctions supportées.

### 13.5. Concepts de protection MPLS-TP

Les réseaux MPLS-TP peuvent utiliser des mécanismes de protection de transport, notamment des mécanismes associés à la protection linéaire 1+1 ou 1:1 selon les spécifications et l'implémentation.

Dans une protection 1+1, le trafic peut être envoyé simultanément sur le chemin de travail et le chemin de protection, et le récepteur sélectionne le signal utilisable selon le mécanisme prévu.

Dans une protection 1:1, le chemin de protection est prévu pour reprendre le service en cas de défaut du chemin de travail, selon la procédure de basculement.

Les détails opérationnels varient selon le profil et le constructeur.

### 13.6. Protection 1+1

```text
                         PROTECTION 1+1

                        +---- Chemin A ----+
                        |                  |
  PE-A ================+                  +================ PE-B
                        |                  |
                        +---- Chemin B ----+

  Le trafic est transporté sur les deux chemins.
  Le point de réception sélectionne le chemin utilisable
  selon le mécanisme de protection implémenté.
```

Avantage : le chemin de secours est déjà utilisé pour transporter le trafic de protection.

Contraintes possibles :

- consommation de capacité ;
- nécessité de chemins suffisamment indépendants ;
- gestion du choix du signal ;
- exigences de configuration et de supervision.

### 13.7. Protection 1:1

```text
                         PROTECTION 1:1

  PE-A -------- Chemin de travail -------- PE-B
    \                                      /
     \                                    /
      +--------- Chemin de secours ------+

  Le chemin de secours est utilisé selon
  la procédure de protection définie.
```

Les détails de transfert du trafic, de coordination et d'utilisation du chemin de secours dépendent de la spécification et de la configuration.

### 13.8. Temps de restauration

Le temps de restauration est la durée nécessaire pour rétablir le service après un défaut.

Il dépend notamment :

- du temps de détection ;
- de la logique de protection ;
- de la coordination entre les extrémités ;
- de la charge et des performances des équipements ;
- du type de défaut ;
- des mécanismes de supervision utilisés.

Il ne faut pas promettre un temps de restauration sans se référer à la spécification du système et à des mesures réelles.

### 13.9. Test de protection

Un test de protection doit être planifié et autorisé.

La méthode générale consiste à :

1. vérifier que le chemin principal est opérationnel ;
2. vérifier l'état du chemin de secours ;
3. confirmer la supervision ;
4. mesurer l'état du service avant test ;
5. provoquer un défaut contrôlé selon la procédure autorisée ;
6. mesurer l'interruption éventuelle ;
7. vérifier le chemin utilisé après basculement ;
8. vérifier les alarmes ;
9. rétablir la situation normale ;
10. documenter les résultats.

Il ne faut jamais provoquer une coupure sur un réseau de production sans autorisation et sans procédure de retour arrière.

## 14. QoS dans les réseaux Métro Ethernet et MPLS-TP

### 14.1. Pourquoi la QoS est-elle importante ?

Les services d'un opérateur peuvent transporter différents types de trafic :

- voix ;
- vidéo ;
- applications transactionnelles ;
- données d'entreprise ;
- synchronisation ;
- trafic de gestion.

Tous ces flux ne présentent pas les mêmes exigences.

La QoS (*Quality of Service*) permet de classer et de traiter les flux selon des politiques de priorité, de bande passante et de congestion.

### 14.2. Paramètres de performance

Les indicateurs importants comprennent :

- **Débit :** quantité de données transportée par unité de temps.
- **Latence :** délai de traversée du réseau.
- **Gigue :** variation du délai.
- **Perte :** trames ou paquets qui n'atteignent pas la destination.
- **Disponibilité :** proportion du temps pendant lequel le service est disponible.

Un service peut avoir un débit suffisant mais une gigue trop élevée pour une application sensible au délai.

### 14.3. Classification du trafic

La classification peut utiliser :

- le VLAN ;
- le champ PCP de 802.1Q ;
- les champs DSCP IP ;
- l'interface d'entrée ;
- des listes de contrôle ;
- des politiques de service.

Les valeurs de classification doivent être définies contractuellement et appliquées de façon cohérente.

### 14.4. PCP et DSCP

Le PCP (*Priority Code Point*) est un champ de priorité associé au tag VLAN 802.1Q.

Le DSCP (*Differentiated Services Code Point*) est utilisé dans l'en-tête IP pour différencier les traitements de trafic.

Ils appartiennent à des champs différents et ne doivent pas être confondus.

Une politique de QoS peut mapper des valeurs PCP vers des classes internes ou des valeurs DSCP vers des classes de service, selon l'architecture.

### 14.5. Files d'attente et ordonnancement

Un équipement peut maintenir plusieurs files d'attente.

Les politiques de sortie déterminent comment le trafic est transmis lorsque plusieurs classes sont en concurrence pour la même interface.

Les mécanismes peuvent inclure :

- priorité stricte ;
- ordonnancement pondéré ;
- limitation de débit ;
- shaping ;
- policing.

Une priorité stricte mal dimensionnée peut affamer les classes moins prioritaires.

La QoS doit donc être conçue de bout en bout, et non configurée uniquement sur le port d'accès.

### 14.6. Policing et shaping

Le policing mesure le trafic par rapport à un profil et peut marquer ou rejeter le trafic excédentaire.

Le shaping retarde une partie du trafic pour lisser son émission et respecter un débit cible.

| Fonction | Objectif | Effet typique |
|---|---|---|
| Policing | Appliquer une limite au trafic | Marquage ou rejet du trafic excédentaire |
| Shaping | Lisser le débit de sortie | Mise en file d'attente et retard éventuel |
| Scheduling | Déterminer l'ordre de transmission | Répartition de capacité entre classes |
| Classification | Identifier la classe de trafic | Affectation à une politique de traitement |

Les fonctions exactes et les unités de mesure dépendent des équipements.

## 15. Synchronisation et services mobiles

Les réseaux de transport peuvent également servir à relier des stations de base mobiles et des équipements de collecte radio.

Ces services peuvent avoir des exigences spécifiques en matière de synchronisation et de performance.

### 15.1. Synchronisation temporelle

Certains services mobiles nécessitent une synchronisation précise entre les équipements.

Selon l'architecture, la synchronisation peut s'appuyer sur :

- des mécanismes de synchronisation de fréquence ;
- SyncE ;
- IEEE 1588 PTP ;
- d'autres solutions adaptées au service.

MPLS-TP ou Métro Ethernet ne garantissent pas à eux seuls la précision temporelle. Le réseau doit être conçu pour transporter ou distribuer les informations de synchronisation avec les performances nécessaires.

### 15.2. Impacts opérationnels

Un service Ethernet peut sembler actif tout en présentant une qualité insuffisante pour une application sensible à la synchronisation.

Le diagnostic doit donc prendre en compte :

- la qualité du transport ;
- la variation de délai ;
- la perte ;
- les équipements de synchronisation ;
- les paramètres du service mobile.

## 16. Sécurité du réseau opérateur

### 16.1. Menaces courantes

Les risques comprennent :

- mauvaise isolation des clients ;
- fuite de VLAN ;
- accès non autorisé aux interfaces de gestion ;
- manipulation des protocoles de contrôle ;
- configuration erronée des chemins ;
- saturation des ressources ;
- erreurs de provisionnement ;
- exploitation d'une vulnérabilité logicielle.

### 16.2. Principes de sécurité

Les bonnes pratiques comprennent :

- séparation des plans de gestion et de données lorsque l'architecture le permet ;
- accès administratif limité ;
- authentification forte ;
- journalisation des changements ;
- sauvegarde des configurations ;
- contrôle des versions ;
- filtrage des flux de gestion ;
- contrôle des accès aux interfaces physiques ;
- validation avant mise en production ;
- procédures de changement et de retour arrière.

### 16.3. Protection de la gestion

L'accès aux équipements de transport ne doit pas être exposé inutilement aux réseaux clients.

La gestion doit s'appuyer sur des réseaux et des politiques d'accès adaptés, avec des comptes nominatifs lorsque possible et une journalisation des opérations.

### 16.4. Séparation des services

Les services clients doivent être séparés conformément à leur définition.

La configuration doit notamment vérifier :

- l'association entre UNI et service ;
- les VLAN autorisés ;
- les règles QinQ ;
- les pseudowires ;
- les chemins de transport ;
- les politiques de QoS ;
- les filtres et contrôles prévus.

Une erreur d'association peut provoquer une fuite de trafic entre clients ou une indisponibilité.

## 17. Méthodologie de diagnostic

### 17.1. Les cinq niveaux de diagnostic

Pour un incident Métro Ethernet/MPLS-TP, utiliser cette progression :

```text
              MÉTHODE DE DIAGNOSTIC EN CINQ NIVEAUX

  Niveau 1 : Physique
      |
      v
  Niveau 2 : Ethernet / VLAN / MTU
      |
      v
  Niveau 3 : Transport / LSP
      |
      v
  Niveau 4 : Service / pseudowire / OAM
      |
      v
  Niveau 5 : QoS / application / SLA
```

Cette progression évite de chercher uniquement dans le plan de transport lorsqu'un problème se situe au niveau du service client.

### 17.2. Niveau 1 : physique

Vérifier :

- état des ports ;
- erreurs physiques ;
- pertes de signal ;
- puissance optique lorsque disponible ;
- connecteurs ;
- câblage ;
- alarmes des modules.

### 17.3. Niveau 2 : Ethernet

Vérifier :

- état des interfaces ;
- VLAN d'accès ;
- VLAN autorisés ;
- QinQ ;
- apprentissage MAC ;
- MTU ;
- erreurs de trames ;
- boucles de couche 2.

### 17.4. Niveau 3 : transport

Vérifier :

- état du LSP ;
- chemin prévu ;
- labels ou identifiants de transport ;
- alarmes OAM ;
- état des interfaces intermédiaires ;
- chemin de protection ;
- changements récents.

Les commandes permettant d'examiner ces éléments varient selon le constructeur.

### 17.5. Niveau 4 : service

Vérifier :

- association du service ;
- état du pseudowire ;
- état des extrémités ;
- paramètres de transport ;
- continuité OAM ;
- cohérence des configurations aux deux extrémités.

### 17.6. Niveau 5 : performance

Vérifier :

- pertes ;
- délai ;
- gigue ;
- compteurs de QoS ;
- congestion ;
- shaping et policing ;
- respect des engagements du service.

## 18. Exemple de dépannage : VLAN incorrect

### Situation

Deux sites sont censés communiquer au travers d'un service E-Line.

Les ports physiques sont actifs, mais aucun trafic utilisateur ne passe.

### Hypothèses

- VLAN client absent sur le port d'entrée ;
- VLAN non autorisé sur un trunk ;
- mauvaise association au service ;
- tag ajouté ou retiré incorrectement ;
- erreur de configuration QinQ ;
- service logique non opérationnel.

### Procédure

1. Vérifier l'état des interfaces.
2. Vérifier les VLAN présents sur les ports clients.
3. Vérifier les VLAN autorisés sur les interfaces intermédiaires.
4. Vérifier la classification au PE d'entrée.
5. Vérifier le transport du service.
6. Vérifier la configuration de sortie.
7. Effectuer un test de trafic.
8. Contrôler les compteurs et les journaux.
9. Documenter le défaut et la correction.

### Résultat attendu

Le trafic doit être associé au bon service, transporté à travers le réseau, puis remis au bon client sans mélange avec les autres services.

## 19. Exemple de dépannage : MTU insuffisant

### Situation

Un client signale que les petites transactions fonctionnent, mais que les transferts volumineux échouent.

### Hypothèses

- MTU de transport insuffisant ;
- surcharge d'encapsulation non prise en compte ;
- rejet des grandes trames ;
- fragmentation ou blocage lié au comportement de bout en bout.

### Procédure

1. Comparer les tailles des paquets qui fonctionnent et échouent.
2. Vérifier le MTU du client.
3. Vérifier les limites de taille sur les interfaces du réseau.
4. Recenser les encapsulations utilisées.
5. Vérifier les compteurs de rejet.
6. Tester plusieurs tailles de trames.
7. Corriger les limites de façon cohérente sur le chemin.
8. Revalider le service.

### Résultat attendu

Les tailles de trames nécessaires au service doivent pouvoir traverser le chemin sans rejet inattendu.

## 20. Exemples de commandes et de configuration

Les commandes suivantes sont des exemples pédagogiques. Elles ne constituent pas une syntaxe universelle MPLS-TP.

### 20.1. Vérification Ethernet

Sur une plateforme compatible, les commandes d'observation peuvent inclure des équivalents de :

```text
show interfaces
show interfaces counters
show vlan
show mac address-table
show logging
```

Le nom exact varie selon le système d'exploitation réseau.

Ces commandes servent à examiner :

- l'état des ports ;
- les compteurs ;
- les VLAN ;
- les adresses MAC apprises ;
- les événements récents.

### 20.2. Vérification IP de base

Sur un poste Linux, on peut utiliser :

```bash
ip link show
ip addr show
ip route show
ping -c 4 192.0.2.10
```

Les adresses utilisées dans les exemples de ce cours sont fictives et certaines appartiennent aux plages réservées à la documentation.

Ces commandes permettent de vérifier l'état local, les adresses, le routage et une connectivité IP élémentaire. Elles ne valident pas à elles seules un circuit Ethernet de couche 2.

### 20.3. Exemple conceptuel de service VLAN

Le pseudocode suivant décrit les intentions de configuration, pas une syntaxe à copier directement dans un équipement :

```text
SERVICE ELINE CLIENT_A_CLIENT_B

UNI_SITE_A:
    VLAN_CLIENT = 100
    MODE = TAGGED

UNI_SITE_B:
    VLAN_CLIENT = 100
    MODE = TAGGED

SERVICE:
    TYPE = POINT_TO_POINT
    ISOLATION = ACTIVE
    MTU = VALEUR_VALIDEE_PAR_ETUDE
    QOS = PROFIL_ENTREPRISE
    OAM = ACTIVE
    PROTECTION = SELON_ARCHITECTURE
```

Avant toute mise en service, les paramètres doivent être traduits dans la syntaxe exacte du constructeur et vérifiés sur les deux extrémités.

### 20.4. Exemple conceptuel d'un transport MPLS-TP

```text
LSP:
    ORIGINE = PE_A
    DESTINATION = PE_B
    CHEMIN = PE_A -> P1 -> P2 -> PE_B
    SUPERVISION = OAM_COMPATIBLE
    PROTECTION = CHEMIN_ALTERNATIF

SERVICE:
    TYPE = ETHERNET
    IDENTIFIANT = SERVICE_1001
    TRANSPORT = LSP_CI_DESSUS
    MTU = VALIDÉ
    QOS = PROFIL_1
```

Ce modèle permet de comprendre les relations entre les objets logiques. Il ne définit pas les commandes spécifiques d'un constructeur.

### 20.5. Règles avant application d'une configuration

Avant d'appliquer une configuration :

1. identifier le constructeur et la version logicielle ;
2. consulter le guide de configuration officiel ;
3. sauvegarder l'état initial ;
4. vérifier la syntaxe sur un environnement de test si possible ;
5. définir le périmètre de changement ;
6. prévoir un retour arrière ;
7. effectuer les tests de validation ;
8. documenter les résultats.

## 21. Travaux pratiques guidés

Les TP sont conçus pour un environnement de laboratoire. Toute intervention sur un réseau de production doit être autorisée.

### TP 1 — Concevoir un service E-Line

**Objectif :** définir les éléments d'un circuit Ethernet point à point.

Scénario :

- Site A : agence principale ;
- Site B : centre de données ;
- service : Ethernet point à point ;
- débit contractuel : 1 Gbit/s ;
- VLAN client : 100 ;
- réseau de transport : partagé entre plusieurs clients.

Travail demandé :

1. identifier les UNI ;
2. dessiner le chemin du service ;
3. préciser les éléments qui doivent être isolés ;
4. lister les vérifications nécessaires ;
5. définir les tests de validation.

**Correction attendue :**

Le service relie les deux UNI par un chemin de transport. Le VLAN client doit être associé au bon service à chaque extrémité. La configuration doit également valider le débit, le MTU, les paramètres de QoS et les mécanismes de supervision prévus.

### TP 2 — Construire un plan QinQ

**Objectif :** isoler plusieurs clients utilisant les mêmes VLAN internes.

Données :

| Client | VLAN client | VLAN externe opérateur |
|---|---:|---:|
| A | 10 | 3001 |
| B | 10 | 3002 |
| C | 20 | 3003 |

Travail demandé :

1. expliquer pourquoi les VLAN externes diffèrent ;
2. préciser le rôle du tag interne ;
3. préciser le rôle du tag externe ;
4. identifier les risques de mauvaise association ;
5. lister les contrôles avant mise en service.

**Correction :**

Le VLAN interne identifie le domaine du client, tandis que le VLAN externe peut identifier le service opérateur. Le client A et le client B peuvent utiliser le VLAN interne 10 tout en restant séparés grâce à leur service externe distinct, si la classification et le transport sont correctement configurés.

### TP 3 — Analyser un problème de MTU

**Objectif :** comprendre pourquoi certaines trames échouent.

Scénario :

- les petits paquets passent ;
- les grandes trames échouent ;
- le service traverse un réseau avec plusieurs encapsulations ;
- les interfaces physiques sont actives.

Travail demandé :

1. formuler trois hypothèses ;
2. identifier les compteurs à consulter ;
3. proposer une méthode de test ;
4. définir les contrôles après correction.

**Correction :**

Hypothèses possibles : MTU insuffisant, surcharge d'encapsulation non prise en compte ou rejet de trames sur une interface intermédiaire.

Il faut vérifier les tailles de trames, les limites de chaque segment, les encapsulations et les compteurs. Après correction, tester plusieurs tailles et vérifier les performances de bout en bout.

### TP 4 — Diagnostiquer une perte de service

**Objectif :** appliquer une méthode structurée.

Scénario :

- interface client active ;
- transport principal déclaré actif ;
- aucun trafic reçu au site distant ;
- plusieurs services utilisent une infrastructure commune.

Travail demandé :

1. vérifier si tous les services sont affectés ;
2. examiner le chemin commun ;
3. vérifier les services logiques ;
4. examiner les VLAN ;
5. contrôler les compteurs et l'OAM.

**Correction :**

Si plusieurs services partageant un chemin sont affectés, la recherche doit porter en priorité sur les éléments communs, sans exclure les autres hypothèses.

Si un seul service est affecté, il faut examiner sa configuration, son association au transport, ses paramètres de VLAN et ses états OAM.

### TP 5 — Préparer un test de protection

**Objectif :** définir un test de basculement.

Travail demandé :

1. dessiner un chemin principal et un chemin de secours ;
2. identifier les points de mesure ;
3. définir les critères de réussite ;
4. décrire le retour à l'état nominal ;
5. rédiger un compte rendu.

**Correction attendue :**

Le test doit vérifier la détection du défaut, le basculement, l'état du service, le temps de restauration mesuré, les alarmes et le retour à la situation nominale. Il doit être autorisé, préparé et réalisé dans un environnement contrôlé.

## 22. Exercices corrigés

### Exercice 1 — Choisir un service Ethernet

Une entreprise possède un siège et quatre agences. Chaque agence doit communiquer avec le siège, mais les communications directes entre agences ne sont pas souhaitées.

Quel modèle de service est pertinent ?

**Correction :**

E-Tree est un modèle pertinent lorsque le besoin correspond à une topologie racine-feuilles. Le service exact doit être défini avec l'opérateur.

### Exercice 2 — VLAN et QinQ

Deux clients utilisent le VLAN 10. Pourquoi cela ne signifie-t-il pas nécessairement qu'ils partagent le même domaine Ethernet ?

**Correction :**

L'opérateur peut isoler les services à l'aide d'identifiants externes distincts, de services logiques ou d'autres mécanismes de séparation. L'isolation dépend de la configuration complète.

### Exercice 3 — Rôle d'un LSP

Quel est le rôle d'un LSP dans MPLS-TP ?

**Correction :**

Il définit un chemin de transport à travers le réseau MPLS. Il transporte le trafic selon les règles et les identifiants de transfert du système.

### Exercice 4 — LSP et pseudowire

Un LSP est actif, mais un seul service Ethernet ne fonctionne pas. Quelle partie faut-il examiner ?

**Correction :**

Il faut examiner le pseudowire ou l'objet de service concerné, son association au transport, les VLAN, le MTU et les paramètres des extrémités. Un LSP actif ne garantit pas que tous les services logiques fonctionnent.

### Exercice 5 — OAM

Quelle est la différence entre vérifier l'état d'un port et vérifier la continuité d'un service ?

**Correction :**

L'état du port indique principalement que l'interface est opérationnelle au niveau physique ou liaison. La continuité de service vérifie un chemin logique plus complet, selon le mécanisme OAM utilisé.

### Exercice 6 — Protection

Deux chemins logiques passent dans le même conduit de fibre. Constituent-ils nécessairement une protection physique efficace ?

**Correction :**

Non. Une coupure du conduit peut interrompre les deux chemins. La diversité physique doit être vérifiée.

### Exercice 7 — MTU

Les petits paquets passent, mais les grandes trames échouent. Quelle hypothèse doit être étudiée en priorité ?

**Correction :**

Un problème de MTU ou de taille maximale supportée par une interface ou une encapsulation est une hypothèse importante. Il faut également vérifier les compteurs et le comportement de bout en bout.

### Exercice 8 — QoS

Pourquoi une interface à 1 Gbit/s ne garantit-elle pas que chaque classe de trafic dispose de 1 Gbit/s ?

**Correction :**

Le débit de l'interface est partagé. Les politiques de QoS, la classification, les files d'attente et les mécanismes de limitation déterminent le traitement et la capacité attribuée à chaque classe.

### Exercice 9 — Panne commune

Cinq services utilisent le même équipement de transport et tombent simultanément. Quelle démarche est pertinente ?

**Correction :**

Rechercher d'abord les éléments communs : équipement, interface, alimentation, chemin partagé, défaut de transport ou changement récent. Les hypothèses doivent ensuite être confirmées par les alarmes et les mesures.

### Exercice 10 — Service actif mais dégradé

Le service fonctionne, mais les applications temps réel présentent une gigue élevée. Quels indicateurs faut-il examiner ?

**Correction :**

Examiner le délai, la gigue, les pertes, la congestion, les files d'attente et les politiques QoS. La simple disponibilité du service ne garantit pas la conformité aux exigences de performance.

## 23. Projet final corrigé — Réseau Métro Ethernet avec transport MPLS-TP

### 23.1. Contexte

Un opérateur doit relier trois sites d'une entreprise :

- **Site A :** siège ;
- **Site B :** agence ;
- **Site C :** centre de données.

Le réseau doit transporter des services Ethernet sur une infrastructure métropolitaine partagée.

Exigences :

- un service point à point entre A et C ;
- un service point à point entre A et B ;
- isolation entre les services ;
- supervision de la continuité ;
- protection contre une panne de transport ;
- gestion de la bande passante ;
- documentation de l'architecture.

### 23.2. Architecture proposée

```text
                       RÉSEAU MÉTRO DE L'OPÉRATEUR

 Site A                                                    Site B
+-----------+                                             +-----------+
| LAN siège |                                             | LAN agence|
+-----+-----+                                             +-----+-----+
      |                                                         |
      v                                                         v
+-----------+                                             +-----------+
| PE-A      |                                             | PE-B      |
+-----+-----+                                             +-----+-----+
      | \                                                       / |
      |  \                                                     /  |
      |   +-----------------+---------------+----------------+   |
      |                     |               |                    |
      v                     v               v                    v
   +------+              +------+        +------+              +------+
   | P-1  |--------------| P-2  |--------| P-3  |--------------| P-4  |
   +------+              +------+        +------+              +------+
      |                                                        |
      +--------------------- Chemin de transport ---------------+
                                                               |
                                                               v
                                                        +-----------+
                                                        | PE-C      |
                                                        +-----+-----+
                                                              |
                                                              v
                                                        +-----------+
                                                        | LAN centre|
                                                        | de données|
                                                        +-----------+

Les chemins et interconnexions représentés sont conceptuels.
La protection réelle doit utiliser des chemins physiquement adaptés.
```

### 23.3. Définition des services

| Service | Origine | Destination | Type |
|---|---|---|---|
| SVC-AC | Site A | Site C | E-Line |
| SVC-AB | Site A | Site B | E-Line |

Chaque service possède ses paramètres de transport, de VLAN, de MTU, de QoS et de supervision.

### 23.4. Séparation des services

L'opérateur peut utiliser des identifiants de service distincts, par exemple :

| Service | VLAN interne client | Identifiant externe de service |
|---|---:|---:|
| SVC-AC | 10 | 3101 |
| SVC-AB | 10 | 3102 |

Ces valeurs sont des exemples pédagogiques.

L'opérateur doit vérifier que la classification des trames et les règles de transport maintiennent l'isolation entre les services.

### 23.5. Définition du transport

Les services peuvent être transportés au travers de LSP MPLS-TP provisionnés selon l'architecture retenue.

Chaque service est associé à son transport conformément à la configuration de l'opérateur.

Il faut vérifier :

- l'origine et la destination ;
- le chemin attendu ;
- l'état du transport ;
- les paramètres de MTU ;
- la cohérence des extrémités ;
- les mécanismes OAM ;
- le comportement en cas de défaut.

### 23.6. Protection

Le projet doit inclure un chemin de secours adapté.

La diversité physique doit être confirmée à partir des plans de réseau et des infrastructures réellement utilisées.

Un simple chemin logique alternatif ne suffit pas si les deux chemins partagent un point de défaillance physique unique.

Les critères de réussite du test de protection doivent être définis avant le déploiement.

### 23.7. QoS

Le profil de QoS doit préciser :

- les classes de trafic ;
- la méthode de classification ;
- la bande passante contractuelle ;
- le comportement en congestion ;
- les éventuelles priorités ;
- les règles de mesure et d'acceptation.

Les paramètres doivent être cohérents sur les interfaces et les équipements concernés.

### 23.8. Supervision

La supervision doit couvrir au minimum :

- l'état des interfaces ;
- l'état des chemins de transport ;
- la continuité des services ;
- les pertes et erreurs ;
- les performances convenues ;
- l'état de la protection ;
- les alarmes et journaux ;
- les changements de configuration.

Les mécanismes OAM doivent être adaptés aux niveaux qu'ils surveillent.

### 23.9. Plan de validation

| Étape | Vérification | Résultat attendu |
|---|---|---|
| 1 | État physique | Interfaces opérationnelles |
| 2 | VLAN et classification | Services correctement séparés |
| 3 | MTU | Tailles de trames nécessaires acceptées |
| 4 | Transport | Chemins conformes au plan |
| 5 | Services | Connectivité attendue |
| 6 | OAM | Continuité et alarmes fonctionnelles |
| 7 | QoS | Paramètres et performances conformes |
| 8 | Protection | Basculement selon les critères définis |
| 9 | Documentation | Configuration et mesures enregistrées |

### 23.10. Gestion des incidents

**Incident A : les deux services sont indisponibles.**

Examiner en priorité les éléments communs : équipements, interfaces, alimentation, chemin partagé, transport et changements récents.

**Incident B : seul SVC-AC est indisponible.**

Examiner le service A-C, ses extrémités, son association au transport et ses paramètres de VLAN.

**Incident C : les petits paquets passent mais pas les grandes trames.**

Examiner le MTU, les encapsulations et les compteurs de rejet.

**Incident D : le service est disponible mais les performances sont dégradées.**

Examiner la QoS, la congestion, le délai, la gigue et les pertes.

**Incident E : le basculement ne se produit pas.**

Vérifier la détection du défaut, l'état du chemin de secours, la configuration de protection et les mécanismes OAM associés.

### 23.11. Livrables du projet

Le dossier de mise en service doit contenir :

1. le schéma logique ;
2. le schéma physique ;
3. l'inventaire des équipements ;
4. les identifiants de services ;
5. les paramètres VLAN et MTU ;
6. les chemins de transport ;
7. le plan de QoS ;
8. les mécanismes OAM ;
9. le plan de protection ;
10. les résultats de tests ;
11. les mesures de performance ;
12. les procédures de diagnostic ;
13. les procédures de retour arrière ;
14. les contacts et responsabilités d'exploitation.

## 24. Documentation technique de référence

Les références suivantes permettent d'approfondir les sujets du cours. Les fonctions réellement disponibles doivent être vérifiées dans les versions applicables des normes et dans la documentation des équipements.

### 24.1. MPLS-TP et MPLS

- **RFC 5654 — Requirements of an MPLS Transport Profile :**  
  https://www.rfc-editor.org/rfc/rfc5654

- **RFC 5921 — A Framework for MPLS in Transport Networks :**  
  https://www.rfc-editor.org/rfc/rfc5921

- **RFC 6371 — Operations, Administration, and Maintenance Framework for MPLS-Based Transport Networks :**  
  https://www.rfc-editor.org/rfc/rfc6371

- **RFC 6372 — MPLS-TP Survivability Framework :**  
  https://www.rfc-editor.org/rfc/rfc6372

- **RFC 6428 — Proactive Connectivity Verification, Continuity Check, and Remote Defect Indication for MPLS Transport Profile :**  
  https://www.rfc-editor.org/rfc/rfc6428

- **RFC Editor — Recherche des RFC :**  
  https://www.rfc-editor.org/

### 24.2. Ethernet et OAM

- **IEEE Standards Association :**  
  https://standards.ieee.org/

- **ITU-T — Recommandations :**  
  https://www.itu.int/rec/T-REC

- **MEF — Services Ethernet et réseaux de services :**  
  https://www.mef.net/

### 24.3. Documentation des constructeurs

- **Cisco :** https://www.cisco.com/c/en/us/support/index.html
- **Nokia :** https://www.nokia.com/
- **Juniper Networks :** https://www.juniper.net/documentation/
- **Ciena :** https://www.ciena.com/

Les syntaxes de commande et les fonctions MPLS-TP ne sont pas universelles. Il faut consulter la documentation correspondant exactement au modèle d'équipement, à la version logicielle et au profil de service déployé.

## 25. Glossaire

| Terme | Définition |
|---|---|
| CE | Équipement situé du côté du client |
| CFM | Fonctions Ethernet de gestion des défauts et de continuité |
| DSCP | Champ de différenciation de services dans l'en-tête IP |
| E-Line | Service Ethernet logique point à point |
| E-LAN | Service Ethernet logique multipoint à multipoint |
| E-Tree | Service Ethernet logique de type racine-feuilles |
| LSP | Chemin de transfert à commutation de labels |
| MPLS | Multiprotocol Label Switching |
| MPLS-TP | Profil MPLS adapté aux réseaux de transport |
| MTU | Taille maximale d'une unité de données sur un chemin donné |
| NNI | Interface d'interconnexion entre réseaux |
| OAM | Exploitation, administration et maintenance |
| PCP | Champ de priorité associé au tag VLAN 802.1Q |
| PE | Équipement de bord du réseau opérateur |
| P | Équipement de transport dans le réseau opérateur |
| Pseudowire | Émulation d'un service de couche 2 sur un réseau de transport |
| QoS | Qualité de service |
| QinQ | Empilement de tags VLAN |
| UNI | Interface de démarcation entre le client et l'opérateur |
| VLAN | Réseau local virtuel |
| Y.1731 | Recommandation ITU-T portant sur des fonctions de maintenance et de mesure Ethernet |

## 26. Évaluation finale

Avant de passer au niveau expert des réseaux opérateurs, l'apprenant doit être capable de répondre aux questions suivantes :

1. Quelle est la différence entre un service E-Line, E-LAN et E-Tree ?
2. Quel est le rôle d'une UNI et d'une NNI ?
3. Pourquoi utiliser QinQ ?
4. Pourquoi le MTU doit-il tenir compte des encapsulations ?
5. Qu'est-ce qu'un label MPLS ?
6. Quelle est la différence entre MPLS classique et MPLS-TP ?
7. Quelle est la différence entre un LSP et un pseudowire ?
8. À quoi servent les mécanismes OAM ?
9. Quelle différence existe-t-il entre la supervision d'un port et la supervision d'un service ?
10. Pourquoi un chemin de secours doit-il être physiquement diversifié ?
11. Quelle différence existe-t-il entre protection 1+1 et 1:1 ?
12. Pourquoi la QoS doit-elle être cohérente sur l'ensemble du chemin ?
13. Comment diagnostiquer un problème de VLAN ?
14. Comment diagnostiquer un problème de MTU ?
15. Quels éléments faut-il vérifier lorsqu'un service reste indisponible alors que le LSP est actif ?

### Critères de réussite

L'apprenant est prêt à poursuivre vers un niveau supérieur lorsqu'il sait :

- concevoir un service Métro Ethernet simple ;
- expliquer la séparation des clients ;
- décrire un transport MPLS-TP ;
- différencier LSP, pseudowire et service client ;
- interpréter les principaux mécanismes OAM ;
- concevoir une stratégie de protection cohérente ;
- appliquer une démarche de dépannage structurée ;
- produire un plan de validation documenté.

**Fin du cours — `telecom-mpls-tp-intermediaire.md`**

**Prochaine étape du module :** `telecom-bgp-peering-expert.md` — BGP Peering & Internet.
