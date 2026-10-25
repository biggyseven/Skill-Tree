# VXLAN — Niveau débutant

## Comprendre les réseaux overlay, les VTEP et l'encapsulation VXLAN


# PRÉSENTATION DU COURS

VXLAN signifie **Virtual Extensible LAN**. Il s'agit d'une technologie de virtualisation réseau qui permet de transporter des trames Ethernet à travers une infrastructure IP.

VXLAN est particulièrement utile dans les centres de données, les environnements virtualisés et les infrastructures dans lesquelles plusieurs réseaux logiques doivent coexister sur un même réseau physique.

Dans un réseau traditionnel, les VLAN permettent de séparer les domaines de couche 2. Cependant, les architectures distribuées, les grands centres de données et les environnements multi-locataires peuvent nécessiter davantage de flexibilité pour étendre des segments réseau entre plusieurs équipements.

VXLAN répond à ce besoin en encapsulant une trame Ethernet dans un paquet UDP transporté sur un réseau IP.

Pour comprendre VXLAN, il faut d'abord distinguer deux éléments :

- **L'underlay** : le réseau IP physique ou de transport qui assure la connectivité entre les équipements VXLAN.
- **L'overlay** : le réseau logique VXLAN qui transporte les communications des machines virtuelles ou des autres équipements connectés.

VXLAN ne remplace donc pas le réseau IP de transport. Il s'appuie sur celui-ci pour transporter des réseaux logiques.

## Positionnement dans le parcours

Ce cours constitue le premier niveau d'un parcours VXLAN en trois étapes.

```text
========================================================
NIVEAU DÉBUTANT
vxlan-debutant.md
========================================================

Comprendre les limites des VLAN
        |
        v
Comprendre les réseaux overlay et underlay
        |
        v
Découvrir VXLAN et le VNI
        |
        v
Comprendre les VTEP
        |
        v
Visualiser l'encapsulation Ethernet dans UDP/IP
        |
        v
Comprendre le parcours d'une trame
        |
        v
Construire un premier laboratoire conceptuel
        |
        v
========================================================
NIVEAU INTERMÉDIAIRE
vxlan-intermediaire.md
========================================================

Construire une architecture VXLAN multi-équipements
        |
        v
Configurer et vérifier l'underlay
        |
        v
Créer les interfaces et les tunnels VXLAN
        |
        v
Associer les VLAN aux VNI
        |
        v
Étudier l'apprentissage MAC et le BUM
        |
        v
Comprendre les mécanismes de contrôle
        |
        v
Analyser la connectivité et les pannes
        |
        v
========================================================
NIVEAU EXPERT
vxlan-expert.md
========================================================

VXLAN avec EVPN et BGP
        |
        v
Distribution des routes MAC/IP
        |
        v
VNI de couche 2 et VNI de couche 3
        |
        v
Anycast Gateway et routage inter-VNI
        |
        v
Multihoming et redondance
        |
        v
Optimisation, sécurité et dépannage avancé
        |
        v
Conception d'une architecture de production
```

**Règle pédagogique :** chaque niveau prolonge le précédent. Le niveau intermédiaire réutilisera le laboratoire et les concepts introduits ici. Le niveau expert approfondira EVPN, BGP et les architectures VXLAN distribuées.


# OBJECTIFS PÉDAGOGIQUES

À la fin du niveau débutant, l'apprenant doit pouvoir :

1. Expliquer pourquoi VXLAN a été conçu.
2. Distinguer un VLAN d'un VNI.
3. Expliquer la différence entre underlay et overlay.
4. Définir un VTEP et comprendre son rôle.
5. Expliquer le principe de l'encapsulation VXLAN.
6. Identifier les principaux en-têtes d'un paquet VXLAN.
7. Expliquer comment une trame Ethernet traverse un réseau IP grâce à VXLAN.
8. Comprendre pourquoi les VTEP doivent être joignables entre eux.
9. Distinguer VXLAN avec apprentissage de données et VXLAN associé à EVPN.
10. Comprendre les limites du flooding et de l'apprentissage MAC.
11. Identifier les causes élémentaires d'une panne VXLAN.
12. Concevoir un premier laboratoire conceptuel et expliquer le parcours d'un paquet.

## Prérequis

Il est recommandé de connaître :

- Les bases du modèle OSI.
- Les différences entre couche 2 et couche 3.
- Les adresses MAC et IP.
- Les VLAN et les trunks Ethernet.
- Le fonctionnement d'un commutateur.
- Le rôle d'un routeur.
- Les notions de routage et de sous-réseau.
- Les principes fondamentaux d'ARP.
- Le rôle d'UDP et d'IP.

Une connaissance préalable des réseaux de centres de données est utile, mais elle n'est pas obligatoire.

## Convention utilisée dans les schémas

Les schémas utilisent exclusivement du texte et des caractères ASCII.

Ils présentent les concepts et les échanges logiques, sans dépendre d'un constructeur particulier.

Les noms d'interfaces, adresses et numéros de VLAN ou de VNI sont fictifs et servent uniquement aux exercices.


# PARTIE 1 — COMPRENDRE LE BESOIN DE VXLAN

## 1. Les VLAN dans un réseau traditionnel

Un VLAN permet de séparer logiquement un réseau Ethernet en plusieurs domaines de couche 2.

Deux machines appartenant à des VLAN différents ne communiquent pas directement au niveau Ethernet comme si elles appartenaient au même VLAN. Une communication entre leurs sous-réseaux nécessite généralement un équipement ou une fonction de routage.

Considérons un réseau comprenant deux VLAN :

```text
                    COMMUTATEUR SW1
                 +--------------------+
                 |                    |
                 | VLAN 10 : USERS    |
                 | VLAN 20 : SERVERS  |
                 |                    |
                 +----+----------+----+
                      |          |
                      |          |
                 +----+--+   +---+------+
                 | PC-A  |   | SERV-B   |
                 +-------+   +----------+
                 VLAN 10       VLAN 20
```

Le commutateur maintient les VLAN séparés.

Cette séparation logique permet d'organiser le réseau, de limiter certains domaines de diffusion et de créer des frontières de couche 2.

Cependant, dans les infrastructures distribuées, les machines qui appartiennent au même segment logique peuvent se trouver sur des équipements physiques différents, voire dans des zones différentes d'un centre de données.

## 2. Le problème de l'extension de couche 2

Supposons que deux serveurs appartiennent au même VLAN logique mais soient connectés à deux commutateurs différents.

```text
        SITE A                         SITE B

     +----------+                   +----------+
     | Serveur A|                   | Serveur B|
     +----+-----+                   +-----+----+
          |                               |
          v                               v
     +----------+                   +----------+
     |   SW1    |                   |   SW2    |
     +----+-----+                   +-----+----+
          |                               |
          +----------- RÉSEAU IP ---------+

    VLAN 10 prévu                  VLAN 10 prévu
```

Le réseau IP de transport permet aux équipements de couche 3 de communiquer, mais il ne transporte pas automatiquement le domaine Ethernet du VLAN 10 comme un unique segment Ethernet.

Il faut donc une solution pour transporter les trames Ethernet du réseau logique à travers l'infrastructure IP.

Plusieurs technologies peuvent remplir des fonctions de ce type. VXLAN est l'une des solutions utilisées dans les environnements virtualisés et les centres de données.

## 3. L'idée fondamentale de VXLAN

VXLAN encapsule une trame Ethernet dans un paquet UDP/IP.

Le réseau IP transporte alors ce paquet vers un autre point d'encapsulation. À l'arrivée, la trame Ethernet originale est récupérée et remise au segment local approprié.

```text
SERVEUR A
    |
    | Trame Ethernet d'origine
    v
+------------------+
| VTEP A           |
| Encapsulation    |
+--------+---------+
         |
         | Paquet UDP/IP transportant VXLAN
         v
+------------------+
| RÉSEAU IP        |
| Underlay         |
+--------+---------+
         |
         | Acheminement IP
         v
+------------------+
| VTEP B           |
| Décapsulation    |
+--------+---------+
         |
         | Trame Ethernet récupérée
         v
SERVEUR B
```

L'underlay n'a pas besoin d'étendre lui-même le VLAN du serveur A jusqu'au serveur B.

Il doit acheminer les paquets IP externes entre les points de terminaison VXLAN.

C'est le principe majeur qui distingue VXLAN d'une extension Ethernet traditionnelle fondée uniquement sur des VLAN et des trunks.

## 4. Pourquoi cette architecture est-elle intéressante ?

VXLAN permet notamment :

- D'étendre des segments Ethernet sur une infrastructure IP.
- De construire plusieurs réseaux logiques sur un même réseau de transport.
- D'isoler les segments logiques au moyen de leurs identifiants.
- D'utiliser une infrastructure de couche 3 entre plusieurs points de terminaison.
- De prendre en charge des architectures distribuées, notamment avec des fonctions de contrôle telles qu'EVPN.

L'intérêt n'est pas uniquement le nombre de réseaux que l'on peut identifier. VXLAN permet aussi de séparer la logique des réseaux virtuels de l'organisation physique du réseau de transport.


# PARTIE 2 — COMPRENDRE UNDERLAY ET OVERLAY

## 5. Qu'est-ce que l'underlay ?

L'underlay est le réseau IP qui transporte les paquets VXLAN entre les VTEP.

Il peut s'appuyer sur des routeurs, des commutateurs de couche 3 et des liens Ethernet.

Son rôle est d'assurer l'acheminement IP entre les adresses utilisées comme points de terminaison VXLAN.

```text
                 UNDERLAY IP
        +-----------------------------+
        |                             |
        |   Routeur A ---- Routeur B  |
        |       |             |       |
        |       +---- Routeur C       |
        |                             |
        +-----------------------------+
             |                 |
             v                 v
          VTEP-A             VTEP-B
```

L'underlay doit permettre aux VTEP concernés de communiquer selon l'architecture choisie.

Il doit également respecter les contraintes de MTU, de routage, de filtrage et de disponibilité du réseau.

## 6. Qu'est-ce que l'overlay ?

L'overlay représente les réseaux logiques construits au-dessus de l'underlay.

Il peut contenir plusieurs segments VXLAN indépendants.

```text
                 OVERLAY VXLAN
        +-----------------------------+
        |                             |
        | VNI 10010 : RÉSEAU USERS    |
        | VNI 10020 : RÉSEAU SERVERS  |
        | VNI 10030 : RÉSEAU TEST     |
        |                             |
        +-----------------------------+
                      |
                      v
                 UNDERLAY IP
        +-----------------------------+
        |                             |
        |      Infrastructure IP      |
        |                             |
        +-----------------------------+
```

Les réseaux logiques utilisent la même infrastructure de transport, mais ils ne deviennent pas pour autant un seul domaine Ethernet commun.

L'identifiant VXLAN permet de distinguer les différents segments.

## 7. La relation entre underlay et overlay

L'underlay et l'overlay remplissent des fonctions complémentaires.

| Élément | Underlay | Overlay |
|---|---|---|
| Fonction principale | Transport IP | Connectivité logique des workloads |
| Niveau dominant | Couche 3 pour l'acheminement | Segmentation virtuelle et Ethernet encapsulé |
| Identifiants principaux | Adresses IP de transport | VNI |
| Équipements concernés | Routeurs et commutateurs de transport | VTEP et équipements connectés |
| Panne typique | Les VTEP ne peuvent plus se joindre | Un segment VXLAN ne fonctionne pas correctement |
| Vérification | Routage et connectivité IP | VNI, apprentissage MAC et correspondances logiques |

Cette séparation permet de diagnostiquer les problèmes en commençant par vérifier le transport, puis le réseau virtuel.

## 8. Exemple d'une panne d'underlay

Supposons que VTEP-A possède l'adresse IP `10.0.0.1` et VTEP-B l'adresse IP `10.0.0.2`.

Si les deux adresses ne sont plus joignables, les paquets VXLAN ne pourront généralement pas être transportés correctement entre ces points.

```text
Hôte A
   |
   v
VTEP-A : 10.0.0.1
   |
   X  ROUTAGE IP DÉFAILLANT
   |
   v
VTEP-B : 10.0.0.2
   |
   v
Hôte B
```

Même si les paramètres du segment VXLAN sont corrects, le transport ne peut pas fonctionner si l'underlay ne fournit pas la connectivité nécessaire.

## 9. Exemple d'une panne d'overlay

Dans un autre cas, les VTEP peuvent se joindre correctement par IP, mais les deux extrémités peuvent être associées à des VNI différents.

```text
VTEP-A                         VTEP-B
VNI 10010                     VNI 10020
    |                             |
    +----------- UNDERLAY --------+
                    IP
```

La connectivité IP ne suffit pas à garantir que les deux machines appartiennent au même segment VXLAN.

La correspondance entre les VLAN, les interfaces et les VNI doit être cohérente selon le modèle utilisé.

**À retenir : underlay fonctionnel ne signifie pas automatiquement overlay fonctionnel.**


# PARTIE 3 — COMPRENDRE LE VNI

## 10. Qu'est-ce qu'un VNI ?

VNI signifie *VXLAN Network Identifier*.

Il identifie le segment réseau VXLAN auquel appartient la trame encapsulée.

Le champ VNI possède une taille de 24 bits.

Cette taille permet d'identifier jusqu'à \(2^{24}\) valeurs, soit 16 777 216 combinaisons possibles, avant de tenir compte des réserves ou des contraintes d'allocation propres aux implémentations.

Les VNI permettent ainsi de distinguer un grand nombre de segments logiques sur une même infrastructure IP.

## 11. Comparaison entre VLAN et VNI

Les VLAN utilisent un identifiant de 12 bits dans le marquage VLAN standard, ce qui fournit 4096 valeurs possibles au niveau du champ. Les identifiants VLAN utilisables dans un réseau donné dépendent ensuite des conventions et des réservations applicables.

Les VNI utilisent un identifiant de 24 bits.

| Propriété | VLAN | VNI VXLAN |
|---|---|---|
| Taille du champ d'identification | 12 bits | 24 bits |
| Fonction générale | Identifier un VLAN | Identifier un segment VXLAN |
| Portée logique | Domaine Ethernet concerné | Segment de l'overlay VXLAN |
| Transport | Ethernet, éventuellement marqué VLAN | Trame encapsulée dans UDP/IP |
| Utilisation typique | Segmentation d'un LAN | Segmentation d'un overlay distribué |

Le VNI n'est pas un remplacement direct du champ VLAN dans chaque trame Ethernet. Il fait partie de l'en-tête VXLAN ajouté lors de l'encapsulation.

## 12. Exemple de segmentation par VNI

Un centre de données peut utiliser plusieurs segments VXLAN :

```text
                  INFRASTRUCTURE IP
                 UNDERLAY COMMUN
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
     +----------+   +----------+   +----------+
     | VNI 10010|   | VNI 10020|   | VNI 10030|
     | USERS    |   | SERVERS  |   | TEST     |
     +----------+   +----------+   +----------+
```

Dans cet exemple :

- Le VNI 10010 correspond au réseau logique des utilisateurs.
- Le VNI 10020 correspond au réseau logique des serveurs.
- Le VNI 10030 correspond à un réseau de test.

Les noms sont des conventions d'administration. VXLAN utilise numériquement le VNI ; les libellés `USERS`, `SERVERS` et `TEST` servent à la documentation.

## 13. Deux VTEP doivent-ils toujours utiliser le même VNI ?

Pour communiquer dans le même segment VXLAN, les points de terminaison doivent interpréter les paquets et les correspondances de segments de manière cohérente.

Dans une conception courante où les VNI identifient directement les segments, les extrémités concernées utilisent le même VNI.

Toutefois, il existe des scénarios plus avancés dans lesquels les associations logiques et les identifiants locaux doivent être considérés avec précision, notamment dans certaines architectures EVPN et interconnexions de centres de données.

Au niveau débutant, retiens la règle suivante :

**Pour un même segment VXLAN, utilise un plan d'allocation des VNI cohérent et documente explicitement toute correspondance particulière.**

Une différence de VNI non prévue peut empêcher deux workloads de communiquer comme attendu.


# PARTIE 4 — COMPRENDRE LES VTEP

## 14. Définition d'un VTEP

VTEP signifie *VXLAN Tunnel Endpoint*.

Le VTEP constitue le point de terminaison logique du tunnel VXLAN.

Il effectue notamment :

- L'encapsulation des trames destinées à l'overlay.
- La sélection du VNI approprié.
- L'envoi des paquets VXLAN vers le réseau de transport.
- La réception des paquets VXLAN.
- La décapsulation.
- La remise des trames au segment local correspondant.

Le VTEP peut être implémenté dans un hyperviseur, dans un commutateur physique ou dans une autre plateforme adaptée.

## 15. Architecture avec deux VTEP

```text
      SERVEUR A                         SERVEUR B
   192.168.10.11                     192.168.10.12
          |                                 |
          v                                 v
   +-------------+                   +-------------+
   |   VTEP-A    |                   |   VTEP-B    |
   | 10.0.0.1    |                   | 10.0.0.2    |
   | VNI 10010   |                   | VNI 10010   |
   +------+------+                   +------+------+
          |                                 |
          +-------------+-------------------+
                        |
                        v
                 RÉSEAU IP UNDERLAY
```

Les deux serveurs sont présentés comme appartenant au même réseau logique.

Les VTEP assurent le transport des trames Ethernet entre les deux côtés.

Les adresses IP de transport des VTEP sont différentes des adresses IP utilisées par les serveurs dans leur réseau applicatif.

Cette distinction est essentielle.

## 16. Adresse de transport et adresse de l'hôte

Dans l'exemple précédent, le serveur A possède l'adresse `192.168.10.11`.

Le VTEP-A utilise l'adresse `10.0.0.1` pour le transport VXLAN.

Ces adresses remplissent des rôles différents :

```text
SERVEUR A
   |
   +---- IP applicative : 192.168.10.11
   |
   v
VTEP-A
   |
   +---- IP de transport : 10.0.0.1
   |
   v
UNDERLAY IP
```

L'adresse extérieure utilisée pour transporter le paquet VXLAN identifie la destination du tunnel dans l'underlay.

L'adresse intérieure appartient à la communication d'origine.

Cette séparation permet de faire fonctionner un réseau logique au-dessus d'un réseau de transport distinct.

## 17. Plusieurs hôtes derrière un VTEP

Un même VTEP peut prendre en charge plusieurs segments logiques et plusieurs hôtes.

```text
                    VTEP-A
             +-------------------+
             |                   |
             | VNI 10010         |
             | VNI 10020         |
             | VNI 10030         |
             |                   |
             +---+-------+-------+
                 |       |
          +------+       +------+
          |                     |
          v                     v
      +--------+            +--------+
      | Hôte A |            | Hôte B |
      | VNI    |            | VNI    |
      | 10010  |            | 10020  |
      +--------+            +--------+
```

Le VTEP doit savoir à quel segment correspond chaque trafic entrant.

L'association peut dépendre de la configuration locale, de la correspondance VLAN-VNI ou d'autres mécanismes de la plateforme.

Le détail sera approfondi au niveau intermédiaire.


# PARTIE 5 — COMPRENDRE L'ENCAPSULATION VXLAN

## 18. Le principe de l'encapsulation

Une trame Ethernet d'origine est intégrée à un paquet VXLAN.

Le paquet VXLAN utilise UDP comme transport, puis IP pour traverser l'underlay.

Le résultat contient donc plusieurs couches :

```text
PAQUET TRANSPORTÉ SUR L'UNDERLAY
+--------------------------------------+
| En-tête Ethernet externe             |
+--------------------------------------+
| En-tête IP externe                   |
+--------------------------------------+
| En-tête UDP                          |
+--------------------------------------+
| En-tête VXLAN                        |
+--------------------------------------+
| Trame Ethernet originale             |
|                                      |
| +----------------------------------+ |
| | MAC destination                  | |
| | MAC source                       | |
| | Type Ethernet                    | |
| | Données d'origine                | |
| +----------------------------------+ |
+--------------------------------------+
```

L'en-tête externe sert au transport sur l'infrastructure IP.

L'en-tête VXLAN identifie notamment le segment logique.

La trame intérieure reste la trame Ethernet d'origine.

## 19. L'en-tête VXLAN

L'en-tête VXLAN standard occupe 8 octets.

Il contient notamment le champ VNI sur 24 bits ainsi que des bits réservés.

Le port UDP de destination par défaut attribué à VXLAN est 4789.

```text
EN-TÊTE VXLAN
+------------------------------------------+
| Flags et champs réservés                 |
+------------------------------------------+
|                 VNI                      |
|              24 bits                     |
+------------------------------------------+
|              Réservé                     |
+------------------------------------------+
```

Les détails exacts de l'encodage et les champs réservés sont définis par la spécification VXLAN.

Au niveau débutant, il suffit de retenir que le VNI permet au point de terminaison de déterminer à quel segment de l'overlay la trame appartient.

## 20. Pourquoi UDP ?

VXLAN utilise UDP pour transporter le paquet encapsulé.

UDP fournit un mécanisme de transport sans connexion au sens de l'établissement d'une session TCP. L'acheminement et la fiabilité du transport restent fondés sur le réseau IP et sur les mécanismes de la couche supérieure.

Le champ de port UDP identifie le service utilisé par le paquet.

Le port de destination VXLAN par défaut est 4789.

Dans la pratique, les implémentations peuvent avoir des particularités de configuration. Les deux extrémités et les politiques de filtrage doivent être compatibles.

## 21. Comprendre les deux en-têtes IP

L'encapsulation VXLAN entraîne généralement la présence de deux en-têtes IP distincts :

- L'en-tête IP intérieur appartient au trafic original.
- L'en-tête IP extérieur permet le transport entre les VTEP.

Dans un scénario de même segment Ethernet, les adresses IP intérieures peuvent être celles des hôtes qui communiquent.

Les adresses IP extérieures identifient les points de terminaison VXLAN.

```text
               PAQUET IP EXTÉRIEUR
+------------------------------------------+
| Source : IP du VTEP émetteur             |
| Destination : IP du VTEP récepteur       |
+------------------------------------------+
| UDP                                      |
+------------------------------------------+
| VXLAN                                    |
+------------------------------------------+
| TRAME ETHERNET INTÉRIEURE                |
|                                          |
| Paquet IP intérieur                      |
| Source : IP de l'hôte A                  |
| Destination : IP de l'hôte B             |
+------------------------------------------+
```

Le réseau underlay utilise les adresses extérieures pour acheminer le paquet.

Le réseau overlay conserve la communication d'origine à l'intérieur de l'encapsulation.

## 22. Port de destination VXLAN

Le port UDP de destination VXLAN par défaut est :

```text
UDP destination : 4789
```

Lorsqu'un paquet doit traverser plusieurs équipements de transport, les ACL et les pare-feu doivent autoriser le trafic requis entre les VTEP.

Si le protocole ou le port utilisé ne correspond pas à ce qu'attend l'équipement distant, les paquets peuvent être rejetés ou ne pas être traités comme des paquets VXLAN.

Le port source UDP peut être choisi de manière à contribuer à la répartition du trafic dans le réseau, notamment avec ECMP.

Au niveau débutant, retiens surtout que le trafic VXLAN est généralement transporté par UDP vers le port 4789.


# PARTIE 6 — COMPRENDRE LE PARCOURS D'UNE TRAME

## 23. Scénario

Considérons deux hôtes appartenant au même réseau logique VXLAN.

```text
HÔTE A
IP  : 192.168.10.11
MAC : AA:AA:AA:AA:AA:AA

        VTEP-A : 10.0.0.1

        VNI : 10010

        RÉSEAU IP UNDERLAY

        VTEP-B : 10.0.0.2

HÔTE B
IP  : 192.168.10.12
MAC : BB:BB:BB:BB:BB:BB
```

Les deux hôtes utilisent des adresses IP du même sous-réseau de démonstration.

Pour que la communication fonctionne, les VTEP doivent pouvoir identifier la destination MAC et le segment auquel la trame appartient.

Le mécanisme de découverte de la destination dépend de l'architecture VXLAN employée. Nous commencerons par le parcours général, avant de voir la différence entre apprentissage par le plan de données et distribution des informations par EVPN.

## 24. Étape 1 — Construction de la trame intérieure

L'hôte A prépare une trame Ethernet à destination de l'hôte B.

```text
HÔTE A
  |
  v
+--------------------------------+
| MAC destination : MAC-B        |
| MAC source      : MAC-A        |
| Données                         |
+--------------------------------+
```

La trame peut contenir un paquet IP destiné à `192.168.10.12`.

L'hôte ne construit pas lui-même un paquet VXLAN dans le scénario classique. Le VTEP prend en charge l'encapsulation.

## 25. Étape 2 — Identification du segment

VTEP-A reçoit la trame et doit déterminer à quel segment logique elle appartient.

Dans cet exemple, il associe la trame au VNI 10010.

Il doit également déterminer où envoyer le trafic correspondant à MAC-B.

Cette information peut provenir d'un apprentissage local, d'informations échangées par le plan de contrôle ou de mécanismes adaptés à la plateforme.

## 26. Étape 3 — Encapsulation

VTEP-A ajoute l'encapsulation VXLAN et les en-têtes nécessaires au transport.

```text
TRAME ORIGINALE
      |
      v
+---------------------------+
| MAC-A vers MAC-B          |
+---------------------------+
      |
      v
AJOUT VXLAN
      |
      v
+---------------------------+
| Ethernet externe          |
+---------------------------+
| IP externe                |
| Source : 10.0.0.1         |
| Destination : 10.0.0.2    |
+---------------------------+
| UDP destination : 4789    |
+---------------------------+
| VXLAN : VNI 10010         |
+---------------------------+
| Trame originale           |
+---------------------------+
```

La trame originale est désormais transportée dans un paquet externe.

## 27. Étape 4 — Transport dans l'underlay

Le réseau IP achemine le paquet extérieur vers l'adresse du VTEP-B.

Il n'a pas besoin de comprendre les adresses MAC des hôtes situés dans la trame intérieure.

```text
VTEP-A
   |
   | Paquet IP externe
   v
ROUTEUR DE TRANSPORT 1
   |
   v
ROUTEUR DE TRANSPORT 2
   |
   v
VTEP-B
```

Cette représentation ne décrit qu'un chemin possible.

Dans une architecture réelle, le chemin dépend des routes, de la topologie et des mécanismes de répartition du trafic.

## 28. Étape 5 — Décapsulation

VTEP-B reçoit le paquet VXLAN.

Il identifie le VNI, traite l'encapsulation et récupère la trame Ethernet intérieure.

```text
PAQUET EXTERNE REÇU
        |
        v
Lecture des en-têtes externes
        |
        v
Traitement UDP/VXLAN
        |
        v
Identification du VNI 10010
        |
        v
Décapsulation
        |
        v
TRAME ETHERNET ORIGINALE
        |
        v
Transmission vers l'hôte B
```

Le VTEP doit disposer des informations nécessaires pour remettre la trame au segment local approprié.

## 29. Étape 6 — Réception par l'hôte B

L'hôte B reçoit la trame Ethernet qui contient le paquet IP d'origine.

Il peut alors traiter le paquet selon les règles normales de la pile réseau.

La communication applicative ne dépend pas du fait que la trame ait été transportée par VXLAN, à condition que la configuration et les services réseau soient corrects.

## 30. Résumé complet du parcours

```text
HÔTE A
   |
   | Trame Ethernet intérieure
   v
VTEP-A
   |
   | Associe la trame au VNI
   |
   | Encapsule Ethernet dans VXLAN/UDP/IP
   v
UNDERLAY IP
   |
   | Achemine le paquet extérieur
   v
VTEP-B
   |
   | Lit le VNI
   |
   | Décapsule le paquet
   v
TRAME ETHERNET ORIGINALE
   |
   v
HÔTE B
```

Ce parcours constitue la base du dépannage VXLAN : il faut vérifier successivement la trame d'origine, le VNI, le transport extérieur et la remise locale.


# PARTIE 7 — COMPRENDRE L'APPRENTISSAGE MAC

## 31. Pourquoi les adresses MAC restent-elles importantes ?

VXLAN transporte des trames Ethernet.

Les VTEP doivent donc disposer des informations nécessaires pour envoyer les trames vers les destinations appropriées.

Dans un scénario de couche 2, les informations utiles peuvent inclure :

- Les adresses MAC observées.
- Le segment VXLAN concerné.
- Le VTEP associé à une destination distante.
- Les associations locales entre ports, VLAN et VNI.

Le mécanisme précis dépend de l'architecture utilisée.

## 32. Apprentissage par le plan de données

Dans une approche fondée sur l'apprentissage des données, un VTEP peut apprendre les adresses MAC à partir du trafic reçu.

Lorsque le VTEP ne connaît pas la destination, il peut utiliser des mécanismes de diffusion ou de réplication prévus par l'architecture.

L'apprentissage permet ensuite de mieux diriger le trafic vers les destinations connues.

```text
TRAME REÇUE
     |
     v
Source MAC observée
     |
     v
Association avec le segment
     |
     v
Information d'apprentissage
     |
     v
Table MAC du VTEP
```

L'apprentissage par le trafic ne constitue pas à lui seul une garantie de connaissance globale et instantanée de tous les hôtes présents dans un overlay.

## 33. Pourquoi le flooding peut-il être nécessaire ?

Lorsque la destination n'est pas connue, un équipement Ethernet utilise généralement des mécanismes de diffusion ou de flooding selon le type de trame et le contexte.

Dans un overlay VXLAN, le flooding peut nécessiter la réplication des paquets vers plusieurs VTEP participants au segment.

La méthode exacte dépend de l'architecture, du plan de contrôle et de l'implémentation.

```text
VTEP-A
  |
  | Destination inconnue
  v
MÉCANISME DE RÉPLICATION
  |
  +-------------------+
  |                   |
  v                   v
VTEP-B              VTEP-C
  |                   |
  v                   v
Segment local       Segment local
```

Le flooding peut augmenter le trafic, particulièrement lorsque le nombre de VTEP et d'hôtes augmente.

C'est l'une des raisons pour lesquelles les architectures VXLAN distribuées utilisent souvent EVPN pour distribuer des informations de reachability.

## 34. Différence entre données et contrôle

Il est essentiel de distinguer :

- Le plan de données, qui transporte les paquets.
- Le plan de contrôle, qui fournit les informations nécessaires à l'établissement et au maintien de la connectivité.

Le fonctionnement de base de VXLAN décrit l'encapsulation.

EVPN peut fournir un mécanisme de contrôle pour distribuer les informations de reachability nécessaires aux réseaux overlay.

VXLAN n'impose pas à lui seul l'utilisation d'EVPN.


# PARTIE 8 — DÉCOUVRIR EVPN

## 35. Pourquoi associer EVPN à VXLAN ?

VXLAN décrit le mécanisme d'encapsulation utilisé pour transporter les trames entre les VTEP.

EVPN, souvent associé à BGP dans ces architectures, permet de distribuer des informations de reachability entre les équipements participants.

Cette association peut aider à limiter la dépendance au flooding et à construire des architectures de centres de données plus évolutives.

L'utilisation d'EVPN dépasse cependant le simple apprentissage des adresses MAC. Elle inclut plusieurs types de routes et des procédures de contrôle spécifiques.

## 36. Schéma — VXLAN seul et VXLAN EVPN

### VXLAN avec mécanismes de découverte et d'apprentissage adaptés à l'implémentation

```text
VTEP-A
   |
   | VXLAN / UDP / IP
   |
   v
UNDERLAY IP
   |
   v
VTEP-B
```

VXLAN assure l'encapsulation et le transport entre les extrémités.

Les informations de destination et les mécanismes de découverte doivent être fournis par la solution choisie.

### VXLAN avec EVPN comme plan de contrôle

```text
                PLAN DE CONTRÔLE
                  BGP EVPN
                /          \
               v            v
            VTEP-A        VTEP-B
               |            |
               |            |
               +------------+
                PLAN DE DONNÉES
                 VXLAN / UDP
                     |
                     v
                 UNDERLAY IP
```

Dans une architecture réelle, les sessions BGP et les flux VXLAN sont des fonctions différentes, même si elles participent toutes deux au fonctionnement de l'overlay.

EVPN distribue les informations de contrôle, tandis que VXLAN transporte les trames.

## 37. Ce que l'apprenant doit retenir

- VXLAN est un mécanisme d'encapsulation de couche 2 sur un transport IP.
- EVPN est une solution de contrôle qui peut distribuer les informations nécessaires à un overlay.
- BGP sert de protocole de distribution des routes EVPN dans les architectures courantes.
- Un VTEP peut être localisé sur un hyperviseur, un commutateur ou une autre plateforme adaptée.
- L'architecture exacte dépend du matériel et des capacités de l'implémentation.

La configuration complète d'EVPN, les types de routes BGP et les mécanismes avancés seront étudiés au niveau expert.


# PARTIE 9 — COMPRENDRE LA TAILLE DES PAQUETS ET LA MTU

## 38. Pourquoi VXLAN ajoute-t-il des octets ?

Le paquet extérieur contient des en-têtes supplémentaires :

- Un en-tête Ethernet externe.
- Un en-tête IP externe.
- Un en-tête UDP.
- Un en-tête VXLAN.
- La trame Ethernet intérieure.

Cette encapsulation augmente la taille de la transmission sur le réseau physique.

L'underlay doit donc disposer d'une MTU adaptée pour transporter les paquets résultants sans fragmentation indésirable ni perte.

## 39. Comprendre la surcharge

Pour une encapsulation VXLAN sur IPv4 classique, l'en-tête IP externe, l'en-tête UDP et l'en-tête VXLAN représentent ensemble 36 octets supplémentaires au-dessus de la trame intérieure du point de vue du transport de couche 3, en ignorant les éventuelles options et extensions.

En pratique, lorsque l'on compare un MTU IP intérieur de 1500 octets avec la taille du paquet IP extérieur, l'en-tête Ethernet intérieur doit également être transporté dans le tunnel.

La surcharge totale fréquemment utilisée comme approximation est donc d'environ 50 octets avec IPv4, et environ 70 octets avec IPv6, selon ce que l'on compte et les options présentes.

Il faut toujours distinguer le MTU IP, la trame Ethernet complète et les éventuels marquages VLAN.

## 40. Schéma de la surcharge

```text
PAQUET INTÉRIEUR
+-------------------------------+
| Ethernet intérieur            |
| IP intérieur                  |
| Données applicatives          |
+-------------------------------+
                  |
                  v
ENCAPSULATION VXLAN
+-------------------------------+
| Ethernet extérieur            |
| IP extérieur                  |
| UDP                           |
| VXLAN                         |
| Ethernet intérieur            |
| IP intérieur                  |
| Données applicatives          |
+-------------------------------+
```

La trame intérieure n'a pas disparu : elle est encapsulée dans le paquet extérieur.

Les en-têtes supplémentaires occupent de l'espace sur les liens de transport.

## 41. Conséquences d'une MTU inadaptée

Une MTU insuffisante peut produire des problèmes difficiles à diagnostiquer :

- Certaines communications fonctionnent, d'autres échouent.
- Les petits paquets passent, mais les paquets plus grands échouent.
- Des transferts rencontrent des ralentissements ou des interruptions.
- Le comportement varie selon le chemin réseau.
- Des problèmes apparaissent lors de l'utilisation de certains protocoles.

Une infrastructure VXLAN doit donc être conçue avec une MTU compatible avec les encapsulations utilisées.

Il ne faut pas supposer que tous les équipements ont automatiquement une MTU suffisamment grande.

## 42. Méthode de vérification

```text
Vérifier le MTU du réseau physique
             |
             v
Vérifier le MTU des interfaces de transport
             |
             v
Vérifier la surcharge VXLAN
             |
             v
Vérifier le chemin entre les VTEP
             |
             v
Tester des tailles de paquets adaptées
             |
             v
Confirmer la cohérence de bout en bout
```

Une simple vérification de la MTU sur une seule interface ne garantit pas que tous les liens du chemin sont compatibles.


# PARTIE 10 — COMPRENDRE LES LIMITES ET LA SÉCURITÉ

## 43. VXLAN n'est pas un mécanisme de chiffrement

VXLAN fournit une encapsulation permettant de transporter des trames Ethernet sur un réseau IP.

Cette encapsulation ne signifie pas que le contenu est automatiquement chiffré ou authentifié.

La sécurité du réseau dépend aussi des mécanismes de protection de l'infrastructure.

Il faut notamment considérer :

- La segmentation logique.
- Les politiques de filtrage.
- Le contrôle d'accès aux VTEP.
- La protection du réseau de transport.
- La surveillance du trafic.
- Les risques d'usurpation.
- Les mécanismes de chiffrement si la confidentialité du transport est nécessaire.

## 44. La segmentation n'est pas un substitut à une politique de sécurité

Deux VNI différents permettent de distinguer des segments VXLAN, mais cela ne suffit pas à définir toute la politique de communication entre les workloads.

Il reste nécessaire de contrôler les flux autorisés, les accès aux services et les chemins de routage.

```text
VNI 10010 : USERS
         |
         v
    Politique de flux
         |
         v
     SERVICES AUTORISÉS


VNI 10020 : SERVERS
         |
         v
    Politique de flux
         |
         v
     SERVICES AUTORISÉS
```

Les règles d'accès doivent être définies indépendamment du simple fait qu'un trafic appartienne à un VNI particulier.

## 45. Les points de contrôle

Une architecture VXLAN doit notamment contrôler :

- Quelles machines peuvent atteindre les adresses des VTEP.
- Quels paquets UDP sont autorisés sur l'infrastructure.
- Quels workloads appartiennent à chaque segment.
- Quels flux inter-segments sont permis.
- Qui peut modifier la configuration des VTEP.
- Comment sont surveillées les erreurs et les modifications.

Ces contrôles doivent être adaptés au niveau de confiance requis par l'environnement.


# PARTIE 11 — CONSTRUIRE UN LABORATOIRE CONCEPTUEL

## 46. Objectif du laboratoire

Nous allons utiliser une topologie conceptuelle contenant deux VTEP et deux hôtes appartenant au même réseau logique.

L'objectif est de comprendre le fonctionnement sans dépendre immédiatement d'une plateforme de configuration spécifique.

### Topologie

```text
                 RÉSEAU LOGIQUE VXLAN
                       VNI 10010

+-----------+                               +-----------+
|  HÔTE A   |                               |  HÔTE B   |
|           |                               |           |
| 192.168.10.11                            192.168.10.12|
+-----+-----+                               +-----+-----+
      |                                           |
      v                                           v
+-----------+                               +-----------+
|  VTEP-A   |                               |  VTEP-B   |
|           |                               |           |
| 10.0.0.1  |                               | 10.0.0.2  |
+-----+-----+                               +-----+-----+
      |                                           |
      +-------------------+-----------------------+
                          |
                          v
                  UNDERLAY IP
```

Les adresses de transport `10.0.0.1` et `10.0.0.2` représentent les adresses des VTEP. Les adresses `192.168.10.11` et `192.168.10.12` représentent celles des hôtes.

Cette séparation est volontaire.

## 47. Tableau des paramètres

| Élément | Hôte A | Hôte B |
|---|---|---|
| Adresse IP applicative | 192.168.10.11 | 192.168.10.12 |
| Réseau applicatif | 192.168.10.0/24 | 192.168.10.0/24 |
| VTEP local | VTEP-A | VTEP-B |
| IP de transport | 10.0.0.1 | 10.0.0.2 |
| VNI logique | 10010 | 10010 |

Les paramètres sont fictifs et servent à illustrer une architecture de même segment logique.

## 48. Hypothèses du laboratoire

Pour que le scénario fonctionne, il faut notamment :

1. Une connectivité IP entre les VTEP.
2. Des points de terminaison VXLAN opérationnels.
3. Un transport UDP conforme à l'implémentation.
4. Une association cohérente entre les segments locaux et le VNI.
5. Une méthode permettant aux VTEP de connaître ou de découvrir les destinations.
6. Une MTU adaptée.
7. Des règles de sécurité compatibles avec le trafic requis.

La simple attribution des adresses IP et du VNI ne garantit pas que la connectivité fonctionnera.

## 49. Exercice d'observation du parcours

Considérons un paquet envoyé depuis Hôte A vers Hôte B.

L'apprenant doit pouvoir répondre aux questions suivantes :

- Quelle est l'adresse IP source du paquet intérieur ?
- Quelle est son adresse IP de destination ?
- Quelle est l'adresse IP extérieure de VTEP-A ?
- Quelle est l'adresse IP extérieure de VTEP-B ?
- Quel VNI est utilisé dans cet exemple ?
- Quel est le rôle de l'underlay ?
- À quel endroit la trame est-elle encapsulée ?
- À quel endroit est-elle décapsulée ?

### Correction

- L'adresse IP intérieure source est `192.168.10.11`.
- L'adresse IP intérieure de destination est `192.168.10.12`.
- L'adresse extérieure source est `10.0.0.1`.
- L'adresse extérieure de destination est `10.0.0.2`.
- Le VNI utilisé est `10010`.
- L'underlay transporte le paquet IP extérieur vers VTEP-B.
- VTEP-A réalise l'encapsulation.
- VTEP-B réalise la décapsulation.


# PARTIE 12 — INTRODUCTION AU DÉPANNAGE VXLAN

## 50. Pourquoi le dépannage doit-il suivre une méthode ?

Une panne de connectivité dans un réseau VXLAN peut provenir de plusieurs couches.

Si l'on commence par modifier le VNI sans vérifier l'underlay, on risque de corriger un paramètre qui n'est pas à l'origine de la panne.

Il est préférable de vérifier les composants dans un ordre logique.

## 51. Le parcours de dépannage

```text
                 HÔTE SOURCE
                      |
                      v
         L'hôte possède-t-il la bonne IP ?
                      |
                      v
          L'hôte est-il raccordé au bon
          VLAN ou segment local ?
                      |
                      v
        Le VTEP reçoit-il la trame locale ?
                      |
                      v
        Le VNI attendu est-il sélectionné ?
                      |
                      v
        Le VTEP connaît-il la destination ?
                      |
                      v
        Les VTEP se joignent-ils par IP ?
                      |
                      v
        Le trafic VXLAN est-il transporté ?
                      |
                      v
        Le VTEP distant reçoit-il le paquet ?
                      |
                      v
        La décapsulation est-elle correcte ?
                      |
                      v
          La trame est-elle remise localement ?
```

Cette séquence représente les grandes étapes du parcours, pas nécessairement l'ordre exact des commandes de diagnostic sur chaque plateforme.

## 52. Panne de transport IP

Si la connectivité IP entre les VTEP est rompue, le tunnel ne peut généralement pas transporter les paquets entre eux.

Il faut vérifier :

- Les adresses IP des VTEP.
- Les routes vers les destinations.
- L'état des interfaces de transport.
- Les politiques de filtrage.
- Les éventuels problèmes de MTU.

## 53. Mauvaise association VLAN-VNI

Un hôte peut être relié à un VLAN local, tandis que le VTEP associe ce VLAN au mauvais VNI.

Le paquet peut alors être transporté dans un segment logique différent de celui prévu.

```text
HÔTE A
  |
  v
VLAN 10
  |
  v
VTEP-A
  |
  +---- Association attendue : VNI 10010
  |
  +---- Association erronée : VNI 10020
```

Le diagnostic doit vérifier les correspondances locales et la cohérence entre les différents VTEP du segment.

## 54. Destination MAC inconnue

Si la destination MAC n'est pas connue, le VTEP peut devoir utiliser les mécanismes de découverte ou de réplication de l'architecture.

Il faut alors vérifier :

- L'apprentissage de l'adresse MAC source.
- La table de forwarding.
- Les informations de reachability.
- Les mécanismes de réplication.
- Le plan de contrôle si EVPN est utilisé.

Le détail sera étudié dans le cours intermédiaire puis approfondi au niveau expert.

## 55. MTU insuffisante

Si les petits paquets passent mais que les gros paquets échouent, une MTU inadéquate peut être une piste.

Il faut vérifier la taille des paquets après encapsulation et la MTU disponible sur l'ensemble du chemin de transport.

Un diagnostic fiable doit également examiner les autres causes possibles, comme le filtrage, le routage ou les problèmes propres aux applications.


# PARTIE 13 — EXERCICES CORRIGÉS

## 56. Exercice 1 — Définition

**Question :** qu'est-ce que VXLAN ?

### Correction

VXLAN est une technologie d'encapsulation qui permet de transporter des trames Ethernet dans des paquets UDP/IP afin d'étendre des réseaux logiques de couche 2 au-dessus d'une infrastructure IP.

## 57. Exercice 2 — Underlay et overlay

**Question :** un réseau IP permet la communication entre deux VTEP, mais les hôtes ne communiquent pas. L'underlay fonctionne-t-il nécessairement mal ?

### Correction

Non.

Le transport IP peut fonctionner alors que le réseau VXLAN rencontre un problème.

Il faut aussi vérifier le VNI, les correspondances locales, l'apprentissage des destinations, les mécanismes de contrôle et la remise de la trame au segment approprié.

## 58. Exercice 3 — Le VNI

**Question :** à quoi sert le VNI ?

### Correction

Le VNI identifie le segment logique VXLAN auquel appartient la trame encapsulée.

Dans une architecture courante, les extrémités d'un même segment utilisent des correspondances cohérentes pour transporter les trames vers le bon réseau logique.

## 59. Exercice 4 — Les adresses IP

**Question :** pourquoi le paquet VXLAN possède-t-il des adresses IP extérieures en plus de celles du paquet intérieur ?

### Correction

Les adresses IP extérieures permettent à l'underlay d'acheminer le paquet entre les VTEP.

Les adresses IP intérieures appartiennent à la communication d'origine entre les hôtes.

Les deux niveaux remplissent des rôles différents.

## 60. Exercice 5 — L'encapsulation

**Question :** quels sont les principaux éléments ajoutés lors de l'encapsulation VXLAN ?

### Correction

L'encapsulation introduit notamment un en-tête VXLAN, un en-tête UDP et un en-tête IP extérieur. Une trame Ethernet extérieure est également utilisée pour transporter le paquet sur le lien local.

La trame Ethernet d'origine demeure à l'intérieur de l'encapsulation.

## 61. Exercice 6 — Port UDP

**Question :** quel est le port UDP de destination VXLAN par défaut ?

### Correction

Le port UDP de destination par défaut est `4789`, conformément à la RFC 7348.

Les paramètres effectifs doivent toutefois être vérifiés dans une implémentation donnée.

## 62. Exercice 7 — MTU

**Question :** pourquoi VXLAN peut-il provoquer des problèmes de connectivité lorsque la MTU de transport est trop petite ?

### Correction

VXLAN ajoute des en-têtes au paquet original.

Le paquet résultant peut dépasser la MTU disponible sur un lien de transport. Selon les conditions, cela peut provoquer des pertes, des problèmes de fragmentation ou des communications qui ne fonctionnent que pour certaines tailles de paquets.

## 63. Exercice 8 — EVPN

**Question :** VXLAN et EVPN sont-ils la même technologie ?

### Correction

Non.

VXLAN définit l'encapsulation utilisée pour transporter les trames.

EVPN peut servir de plan de contrôle pour distribuer les informations de reachability nécessaires à l'overlay.

Ils peuvent fonctionner ensemble, mais leurs responsabilités sont différentes.

## 64. Exercice 9 — Sécurité

**Question :** un trafic encapsulé en VXLAN est-il automatiquement chiffré ?

### Correction

Non.

L'encapsulation VXLAN ne constitue pas en elle-même une garantie de chiffrement.

La protection de la confidentialité et l'authentification du transport nécessitent des mécanismes de sécurité adaptés à l'architecture.

## 65. Exercice 10 — Dépannage

**Question :** les VTEP se joignent par IP, mais les hôtes n'arrivent pas à communiquer. Quelles vérifications effectuer ?

### Correction indicative

Il faut vérifier :

1. La correspondance VLAN-VNI.
2. La cohérence des VNI entre les extrémités.
3. L'apprentissage MAC et les informations de destination.
4. Les mécanismes de réplication.
5. Le trafic VXLAN transporté.
6. La MTU.
7. La décapsulation et la remise locale.
8. Les éventuelles politiques de filtrage.


# PARTIE 14 — ERREURS FRÉQUENTES CHEZ LES DÉBUTANTS

## 66. Confondre VLAN et VNI

Le VLAN est une méthode de segmentation Ethernet.

Le VNI est l'identifiant utilisé dans l'encapsulation VXLAN pour identifier le segment de l'overlay.

Les deux notions peuvent être associées dans une architecture, mais elles n'ont pas le même rôle.

## 67. Croire que VXLAN remplace l'underlay

VXLAN s'appuie sur le réseau IP de transport.

Si les adresses des VTEP ne sont pas joignables, l'overlay peut être incapable de transporter les paquets entre les extrémités.

## 68. Confondre l'adresse de l'hôte avec celle du VTEP

Les adresses IP intérieures et extérieures appartiennent à des niveaux différents.

Une erreur d'adresse sur l'underlay peut empêcher le tunnel de fonctionner même lorsque les adresses des hôtes sont correctes.

## 69. Supposer que le VNI suffit à garantir la communication

Le VNI identifie un segment, mais la connectivité dépend aussi des mappings, de la découverte ou de la distribution des destinations, du transport et de la remise locale.

## 70. Ignorer la MTU

VXLAN ajoute des en-têtes.

Une MTU inadaptée peut générer des problèmes difficiles à repérer, particulièrement lorsque seule une partie des flux ou des tailles de paquets est affectée.

## 71. Confondre VXLAN et EVPN

VXLAN fournit l'encapsulation.

EVPN apporte un mécanisme de contrôle qui peut distribuer des informations de reachability.

Comprendre leur séparation est indispensable pour étudier les architectures modernes.

## 72. Traiter VXLAN comme un mécanisme de sécurité complet

La séparation par VNI ne remplace pas toutes les politiques de filtrage, les contrôles d'accès et les mécanismes de chiffrement éventuellement nécessaires.


# PARTIE 15 — GLOSSAIRE

## 73. Termes essentiels

**VXLAN — Virtual Extensible LAN :** technologie d'encapsulation de trames Ethernet dans des paquets UDP/IP.

**VNI — VXLAN Network Identifier :** identifiant de 24 bits qui permet d'identifier un segment VXLAN.

**VTEP — VXLAN Tunnel Endpoint :** point de terminaison qui encapsule et décapsule les trames VXLAN.

**Underlay :** infrastructure de transport IP qui relie les points de terminaison VXLAN.

**Overlay :** réseau logique construit au-dessus de l'infrastructure de transport.

**Encapsulation :** ajout d'en-têtes autour d'un paquet ou d'une trame afin de permettre son transport dans un autre mécanisme.

**Décapsulation :** opération inverse qui retire les en-têtes de transport pour récupérer les données originales.

**UDP :** protocole de transport sans établissement de connexion, utilisé notamment pour transporter les paquets VXLAN.

**MTU — Maximum Transmission Unit :** taille maximale d'unité de données prise en charge par un lien ou une interface dans les conditions considérées.

**EVPN — Ethernet VPN :** solution de contrôle et de distribution d'informations Ethernet utilisée notamment pour construire des overlays.

**BGP — Border Gateway Protocol :** protocole de routage qui sert également à distribuer les routes EVPN dans les architectures correspondantes.

**Apprentissage MAC :** mécanisme qui permet d'associer une adresse MAC à un emplacement ou à une destination logique.

**Flooding :** mécanisme de diffusion d'une trame vers plusieurs destinations lorsque les règles Ethernet ou l'architecture l'exigent.

**Réplication :** production et distribution de copies d'un paquet vers plusieurs destinations.

**Plan de données :** partie de l'architecture qui assure le traitement et le transport du trafic.

**Plan de contrôle :** partie qui fournit les informations nécessaires à l'établissement et au maintien des chemins et des associations logiques.

**Routage inter-VNI :** communication entre des réseaux logiques VXLAN distincts au moyen d'une fonction de routage.


# PARTIE 16 — ÉVALUATION DE FIN DE NIVEAU

## 74. Questions théoriques

L'apprenant doit pouvoir répondre aux questions suivantes sans consulter le cours.

1. Quel problème VXLAN cherche-t-il à résoudre ?
2. Quelle différence existe entre underlay et overlay ?
3. À quoi sert le VNI ?
4. Quel est le rôle d'un VTEP ?
5. Pourquoi VXLAN utilise-t-il UDP/IP ?
6. Quel est le port UDP de destination VXLAN par défaut ?
7. Pourquoi trouve-t-on deux niveaux d'adresses IP dans un paquet encapsulé ?
8. Pourquoi la MTU doit-elle être adaptée ?
9. Comment une destination MAC inconnue peut-elle être traitée ?
10. Quelle est la différence entre VXLAN et EVPN ?
11. Pourquoi l'underlay peut-il fonctionner alors que l'overlay est en panne ?
12. Pourquoi VXLAN n'est-il pas automatiquement un mécanisme de chiffrement ?
13. Quel est le rôle de l'encapsulation ?
14. Où la décapsulation est-elle effectuée ?
15. Pourquoi faut-il vérifier les correspondances VLAN-VNI ?
16. Quels sont les composants essentiels du parcours d'un paquet VXLAN ?
17. Quels éléments doivent être vérifiés lors d'une panne de connectivité ?
18. Comment les mécanismes de contrôle peuvent-ils améliorer la distribution des informations de reachability ?

## 75. Travaux pratiques conceptuels

Réalisez les exercices suivants sur papier ou dans un laboratoire de simulation.

### Travail 1 — Décrire l'architecture

Représentez deux hôtes situés sur deux commutateurs différents.

Les hôtes doivent appartenir au même segment logique VXLAN. Faites apparaître les VTEP et le réseau IP de transport.

### Travail 2 — Identifier les adresses

Pour chaque paquet, distinguez les adresses IP intérieures et extérieures.

Expliquez à quel niveau intervient chaque adresse.

### Travail 3 — Étudier une panne de transport

Supposez que l'underlay ne puisse plus acheminer les paquets entre les VTEP.

Expliquez ce qui échoue et quelles vérifications effectuer en premier.

### Travail 4 — Étudier une erreur de VNI

Supposez que les deux extrémités utilisent des associations différentes pour le même segment logique.

Expliquez pourquoi une connectivité IP entre les VTEP ne garantit pas la communication entre les hôtes.

### Travail 5 — Étudier la MTU

Expliquez pourquoi un paquet de grande taille peut échouer alors qu'un paquet plus petit fonctionne.

Décrivez comment vérifier le chemin de transport.

### Travail 6 — Comparer deux architectures

Dessinez une architecture VXLAN avec apprentissage et découverte adaptés à l'implémentation, puis une architecture utilisant EVPN comme plan de contrôle.

Précisez le rôle de l'encapsulation et celui de la distribution des informations de reachability.


# PARTIE 17 — PRÉPARER LE NIVEAU INTERMÉDIAIRE

## 76. Ce qui est maintenant acquis

Le niveau débutant a présenté :

- Les limites et les usages des VLAN traditionnels.
- La motivation derrière VXLAN.
- L'underlay et l'overlay.
- Le VNI.
- Les VTEP.
- L'encapsulation Ethernet/UDP/IP.
- Le parcours d'une trame.
- Les bases de l'apprentissage MAC.
- La différence entre VXLAN et EVPN.
- Les contraintes élémentaires de MTU.
- Les bases du dépannage.

Ces notions devront être réutilisées dans le niveau intermédiaire.

## 77. Schéma de progression

```text
========================================================
DÉBUTANT — vxlan-debutant.md
========================================================

Comprendre VXLAN
        |
        v
Identifier underlay et overlay
        |
        v
Comprendre VTEP et VNI
        |
        v
Visualiser l'encapsulation
        |
        v
Expliquer le parcours des paquets
        |
        v
========================================================
INTERMÉDIAIRE — vxlan-intermediaire.md
========================================================

Réutiliser la topologie
        |
        v
Préparer un underlay opérationnel
        |
        v
Configurer les VTEP
        |
        v
Associer les VLAN et les VNI
        |
        v
Vérifier l'apprentissage MAC
        |
        v
Étudier le flooding et la réplication
        |
        v
Contrôler la MTU et la connectivité
        |
        v
Dépanner le laboratoire
        |
        v
========================================================
EXPERT — vxlan-expert.md
========================================================

Introduire EVPN et BGP
        |
        v
Étudier les routes EVPN
        |
        v
Comprendre les VNI de couche 2 et de couche 3
        |
        v
Étudier l'Anycast Gateway
        |
        v
Configurer le routage inter-VNI
        |
        v
Étudier le multihoming et la redondance
        |
        v
Concevoir et dépanner une architecture avancée
```

## 78. Contenu attendu du cours intermédiaire

Le niveau intermédiaire devra commencer par rappeler la topologie conceptuelle du cours débutant et l'utiliser comme base d'un laboratoire.

Il devra notamment aborder :

### Underlay

- Adressage des interfaces de transport.
- Routes entre les VTEP.
- Vérification de la connectivité IP.
- MTU et capacité de transport.
- Contrôles de base des interfaces et du routage.

### Configuration VXLAN

- Création des points de terminaison.
- Association des VLAN aux VNI.
- Définition des segments logiques.
- Configuration des paramètres propres à la plateforme.
- Vérification des associations de segment.

### Plan de données

- Encapsulation et décapsulation.
- Apprentissage MAC.
- Destination connue et destination inconnue.
- Flooding et réplication.
- Vérification du trafic.

### Dépannage

- Underlay inaccessible.
- VNI incohérent.
- Mappings incorrects.
- Problèmes de MTU.
- Absence d'apprentissage.
- Erreurs de configuration locale.

Le contenu de configuration devra dépendre d'une plateforme de laboratoire explicitement choisie. Les commandes d'un constructeur ne doivent pas être présentées comme universelles.

## 79. Contenu attendu du cours expert

Le niveau expert approfondira notamment :

- EVPN comme plan de contrôle.
- BGP EVPN.
- Les routes MAC/IP et les autres types de routes EVPN utiles au scénario.
- Les VNI de couche 2 et de couche 3.
- L'Anycast Gateway.
- Le routage inter-VNI.
- Le multihoming.
- Les mécanismes de convergence.
- La redondance.
- Les architectures de centres de données multi-racks.
- Les politiques de sécurité.
- Les stratégies de dépannage avancé.

Ces fonctions seront étudiées dans le contexte d'une architecture complète et non comme une simple liste de commandes.


# CONCLUSION GÉNÉRALE

VXLAN permet d'étendre des segments Ethernet au-dessus d'une infrastructure IP en encapsulant les trames originales dans des paquets UDP/IP.

Cette technologie sépare le réseau logique, représenté par l'overlay, du réseau de transport, représenté par l'underlay.

Le VNI identifie le segment VXLAN. Le VTEP réalise l'encapsulation et la décapsulation. Le réseau IP assure l'acheminement des paquets extérieurs entre les points de terminaison.

Ces mécanismes permettent de construire des réseaux logiques distribués, mais leur fonctionnement dépend aussi de la cohérence des associations locales, de la découverte des destinations, de la MTU et de la configuration des équipements.

EVPN peut compléter VXLAN en fournissant un plan de contrôle pour distribuer les informations de reachability nécessaires à des architectures plus avancées.

Le niveau intermédiaire utilisera les notions acquises pour construire et vérifier une topologie VXLAN de laboratoire. Le niveau expert approfondira ensuite EVPN, BGP, le routage inter-VNI, la redondance et les mécanismes de conception avancés.

**Principe final : comprendre l'underlay, identifier les VTEP, vérifier le VNI, suivre l'encapsulation, contrôler la MTU et distinguer clairement le transport VXLAN du mécanisme de contrôle utilisé par l'architecture.**


# RÉFÉRENCES TECHNIQUES

- RFC 7348 — *Virtual eXtensible LAN (VXLAN): A Framework for Overlaying Virtualized Layer 2 Networks over Layer 3 Networks*  
  https://www.rfc-editor.org/rfc/rfc7348.html

- RFC 8365 — *A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)*  
  https://www.rfc-editor.org/rfc/rfc8365.html

- Documentation Cisco DevNet — VXLAN EVPN  
  https://developer.cisco.com/docs/sonic/vxlan-evpn/

Les paramètres de configuration, les commandes de vérification et les fonctions disponibles doivent être contrôlés dans la documentation de la plateforme réellement utilisée en laboratoire.