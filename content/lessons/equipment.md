# Équipements L1/L2 : hub, switch et routeur

Un réseau local n'est pas seulement une collection de câbles. Les équipements
qui reçoivent les signaux, lisent les adresses et dirigent les données ont
chacun un rôle précis. Ce cours compare le hub, le switch et le routeur, puis
explique ce qui se passe à l'intérieur d'un switch moderne.

> Analogie : le hub est un haut-parleur qui répète tout dans une salle. Le
> switch est un standard téléphonique qui sait à quel poste transmettre. Le
> routeur est le service de livraison qui choisit la route entre deux villes.

## 1. Rappel des couches

| Équipement | Couche principale | Adresse utilisée | Fonction |
|---|---|---|---|
| Hub | L1, physique | Aucune adresse logique | Répète le signal électrique |
| Switch | L2, liaison | Adresse MAC | Commute les trames dans un LAN |
| Routeur | L3, réseau | Adresse IP | Relie des réseaux et choisit une route |
| Box Internet | L1 à L3, parfois plus | MAC et IP | Modem, routeur, switch, Wi-Fi, pare-feu |

Un équipement peut intégrer plusieurs fonctions. Une box Internet contient
souvent un modem, un routeur, un switch et un point d'accès Wi-Fi dans le même
boîtier.

## 2. Le hub : le répéteur simple

Le hub est un équipement historique. Il possède plusieurs ports et répète les
signaux reçus sur un port vers tous les autres ports.

### Comment il fonctionne

1. Un appareil émet une trame.
2. Le hub reçoit les signaux électriques.
3. Il les régénère et les envoie à tous les autres ports.
4. Tous les appareils du segment voient la trame, même ceux qui ne sont pas
   destinataires.

Le hub ne lit pas les adresses MAC. Il ne sait pas qui est le destinataire. Il
ne crée pas de table d'apprentissage et ne filtre pas le trafic.

### Conséquences

- Tous les ports partagent le même **domaine de collision**.
- Un seul appareil peut transmettre à la fois sur un segment à 10 ou 100 Mb/s.
- Les collisions sont fréquentes quand plusieurs postes parlent.
- Le mode est souvent half-duplex.
- La bande passante est partagée entre tous les utilisateurs.
- Un hub est facile à utiliser mais très limité.

> Analogie : dans une salle, une seule personne peut parler à la fois. Si deux
> personnes parlent ensemble, les voix se mélangent et il faut recommencer.

Le hub est aujourd'hui remplacé par le switch, même pour les petits réseaux.
On le rencontre encore dans des installations anciennes ou comme exemple
pédagogique.

## 3. Le switch : le commutateur du LAN

Le switch relie plusieurs appareils dans un même réseau local. Il possède
plusieurs ports, souvent 8, 24 ou 48, et apprend sur quel port se trouve chaque
adresse MAC.

### Domaines de collision et de diffusion

Chaque port de switch forme généralement son propre **domaine de collision**.
Cela permet aux appareils de transmettre en full-duplex sans se marcher dessus.
En revanche, tous les ports d'un même VLAN appartiennent au même **domaine de
diffusion** : une trame de diffusion est envoyée à tous les ports de ce VLAN.

| Équipement | Domaine de collision | Domaine de diffusion |
|---|---|---|
| Hub | Un seul pour tous les ports | Un seul |
| Switch sans VLAN | Un par port | Un seul |
| Switch avec VLAN | Un par port | Un par VLAN |
| Routeur | Un par interface | Un par interface |

Le routeur sépare les domaines de diffusion. Le switch les sépare seulement si
l'on configure des VLAN.

## 4. La table CAM

Le switch apprend les adresses MAC grâce à sa **table CAM** (Content Addressable
Memory), aussi appelée table de commutation ou table MAC.

Une entrée contient généralement :

- l'adresse MAC ;
- le port du switch ;
- le VLAN ;
- un compteur d'âge ou un timer de vieillissement ;
- éventuellement un type d'entrée (statique ou dynamique).

```text
Table CAM simplifiée

MAC                  Port    VLAN    Âge
00:11:22:33:44:55    1       10      12 s
00:11:22:33:44:66    2       10      35 s
00:11:22:33:44:77    7       20      8 s
```

### Apprentissage

Quand une trame arrive sur un port, le switch lit la **MAC source** et
l'associe au port d'arrivée. Si l'adresse est inconnue, il crée une entrée. Si
elle existe, il met à jour le port et le timer.

Exemple :

1. Le PC A, MAC `AA:AA:AA:AA:AA:AA`, envoie une trame depuis le port 1.
2. Le switch apprend : `AA:AA:AA:AA:AA:AA` est sur le port 1.
3. Le PC B répond depuis le port 2.
4. Le switch apprend : `BB:BB:BB:BB:BB:BB` est sur le port 2.
5. Les prochaines trames entre A et B sont envoyées uniquement sur le bon port.

### Transfert, filtrage et inondation

Le switch compare la **MAC destination** avec sa table :

- **Forward** : la destination est connue sur un autre port ; la trame est
  envoyée sur ce port.
- **Filter** : la source et la destination sont sur le même port ; la trame
  n'a pas besoin d'être renvoyée sur ce port.
- **Flood** : la destination est inconnue ou il s'agit d'une diffusion ; la
  trame est envoyée à tous les ports du VLAN, sauf le port d'arrivée.

Le flooding d'une destination inconnue est parfois appelé *unknown unicast
flooding*. Il reste limité au VLAN d'origine.

### Vieillissement

Une entrée dynamique est supprimée après un temps d'inactivité, souvent environ
300 secondes. Si l'appareil change de port, une nouvelle trame met à jour
l'entrée. Une adresse peut aussi être configurée statiquement pour éviter les
mouvements imprévus.

## 5. Switch store-and-forward et cut-through

Un switch peut traiter les trames de différentes façons.

### Store-and-forward

Le switch reçoit toute la trame, vérifie sa séquence de contrôle FCS, puis la
transmet si elle est valide. C'est le mode le plus courant : il évite de
propager une trame corrompue, au prix d'un petit délai.

### Cut-through

Le switch commence à transmettre dès qu'il a lu la MAC destination. Le délai
est plus faible, mais une trame corrompue peut être propagée avant d'être
détectée. Certains switches combinent les deux approches ou changent de mode
selon la charge.

| Mode | Vérifie la FCS | Délai | Usage |
|---|---|---|---|
| Store-and-forward | Oui | Plus élevé | Standard, qualité |
| Cut-through | Non ou partiel | Plus faible | Temps réel, data center |

## 6. ASIC, data plane et control plane

Un switch moderne ne traite pas chaque trame avec son processeur central. Il
utilise des circuits spécialisés appelés **ASIC** (Application-Specific
Integrated Circuit). Les ASIC effectuent les opérations répétitives à très
grande vitesse :

- lire l'en-tête Ethernet ;
- chercher la MAC destination dans la table CAM ;
- appliquer les règles de VLAN ;
- calculer le port de sortie ;
- mettre à jour les compteurs ;
- transmettre la trame.

C'est le **data plane** ou plan de données : le chemin rapide des paquets.

Le **control plane** ou plan de contrôle gère la configuration et les
protocoles : apprentissage, VLAN, STP, LLDP, gestion, mises à jour des tables.
Il peut fonctionner sur un processeur général, séparé du data plane.

> Analogie : l'ASIC est une chaîne de montage très rapide. Le processeur est le
> chef d'atelier qui change les réglages, mais qui ne fabrique pas chaque pièce
> à la main.

### TCAM

Pour les décisions plus complexes, comme les ACL, les routes ou les règles de
politique, les switches utilisent parfois une **TCAM** (Ternary Content
Addressable Memory). Elle permet de comparer des bits avec des valeurs
« 0 », « 1 » ou « peu importe ». C'est utile pour les correspondances de
masques et les tables de forwarding.

### Line rate et oversubscription

Un switch dit *line-rate* peut transmettre à la vitesse maximale sur tous les
ports en même temps, dans les conditions prévues. Si les ports d'accès sont
nombreux mais que l'uplink est plus petit, il y a de l'**oversubscription** :
plusieurs ports peuvent vouloir envoyer vers un lien unique.

Exemple simple :

```text
24 ports à 1 Gb/s  ->  2 uplinks à 10 Gb/s
```

Le trafic agrégé peut dépasser la capacité des uplinks. Ce n'est pas toujours
un problème, car tous les postes ne saturent pas leur lien en permanence, mais
il faut le prévoir pour les serveurs et les sauvegardes.

## 7. Le routeur : relier les réseaux

Le routeur travaille à la couche 3. Il possède plusieurs interfaces, chacune
dans un réseau IP différent. Il consulte une table de routage pour choisir le
prochain saut.

### Ce que fait un routeur

1. Il reçoit une trame sur une interface.
2. Il retire l'en-tête de liaison et examine le paquet IP.
3. Il vérifie la destination et consulte sa table de routage.
4. Il choisit la route la plus précise.
5. Il décrémente le TTL.
6. Il réécrit l'en-tête de liaison pour le prochain saut.
7. Il transmet la trame par l'interface appropriée.

> Analogie : le routeur est un postier qui reçoit une lettre, regarde la ville
> de destination et choisit le prochain bureau. Il ne connaît pas toutes les
> rues du pays, seulement la direction à prendre.

### Table de routage

Une table de routage contient des réseaux de destination, des masques, des
passerelles et des interfaces. Le routeur choisit la route la plus spécifique
(le préfixe le plus long).

```text
Destination        Masque            Passerelle       Interface
0.0.0.0            0.0.0.0           192.168.1.1      WAN
192.168.1.0        255.255.255.0     directement      LAN
10.10.0.0          255.255.0.0       192.168.1.254    WAN
```

La route `0.0.0.0/0` est la route par défaut. Elle sert quand aucune route plus
précise ne correspond.

### ARP et la couche 2

Pour envoyer un paquet IP sur un réseau local, le routeur doit connaître la MAC
du prochain saut. Il utilise ARP pour demander « qui possède cette adresse IP ? »
et reçoit une réponse avec la MAC correspondante.

La table ARP associe IP et MAC. Elle est différente de la table CAM, qui associe
MAC et port du switch. Un routeur peut avoir une table ARP par interface.

### NAT et pare-feu

Dans une box domestique, le routeur fait souvent du **NAT** : il traduit les
adresses privées du LAN en une adresse publique pour Internet. Il peut aussi
filtrer le trafic avec un pare-feu. Ces fonctions ne sont pas obligatoires pour
tout routeur, mais elles sont courantes dans les équipements grand public.

## 8. Hub, switch, routeur : comparaison

| Critère | Hub | Switch | Routeur |
|---|---|---|---|
| Couche | L1 | L2 | L3 |
| Adresse | Aucune | MAC | IP |
| Domaine de collision | Partagé | Un par port | Un par interface |
| Domaine de diffusion | Partagé | Un par VLAN | Un par interface |
| Filtrage | Non | Oui, par MAC | Oui, par IP et routes |
| Relie Internet | Non | Non, seul | Oui |
| Intelligence | Très faible | Table CAM, VLAN | Table de routage |
| État actuel | Obsolète | Courant | Courant |

Un switch ne remplace pas un routeur pour aller sur Internet. Un routeur ne
remplace pas un switch pour connecter beaucoup de postes dans le même LAN. La
box combine les deux rôles pour simplifier l'usage domestique.

## 9. Une architecture simple

```text
        Internet
           |
        +------+
        | Box  |
        |routeur|
        +--+---+
           |
        +--+---+
        |Switch|
        +--+---+
           |
     +-----+-----+
     |           |
   PC 1        PC 2
```

Le PC envoie une trame au switch. Le switch la commute vers la box. La box
route le paquet vers Internet. Au retour, la box route vers le LAN et le switch
commute vers le PC.

Pour le défi Canvas, le schéma attendu est encore plus simple :

```text
PC ---- Switch ---- Routeur ---- Cloud
```

Chaque liaison représente un segment. Le switch relie le PC au routeur dans le
LAN ; le routeur relie le LAN au cloud, qui représente Internet ou un réseau
externe.

## 10. Dépannage

### Le lien est down

- Vérifier le câble et les LED.
- Essayer un autre port.
- Vérifier la vitesse et le duplex négociés.
- Vérifier que le port n'est pas administrativement désactivé.

### Le lien est up mais le ping échoue

- Vérifier l'adresse IP et le masque.
- Vérifier la passerelle.
- Vérifier le VLAN du port.
- Vérifier la table ARP.
- Vérifier la table de routage.

### Le réseau est lent

- Chercher une boucle de commutation ou une tempête de diffusion.
- Vérifier les erreurs CRC sur les ports.
- Vérifier l'oversubscription des uplinks.
- Vérifier la négociation du duplex.
- Vérifier les ACL et le filtrage.

### Une MAC apparaît sur plusieurs ports

Cela peut indiquer une boucle, un changement de câblage ou une attaque. Le
switch peut signaler un **MAC flapping**. Il faut identifier le port concerné
et vérifier la topologie.

## 11. À retenir

- Le hub répète les signaux à tous les ports et ne lit pas les MAC.
- Le switch apprend les MAC dans une table CAM et commute les trames.
- Le routeur relie des réseaux IP différents et choisit une route.
- Un switch sépare les domaines de collision ; un routeur sépare les domaines
  de diffusion.
- Les ASIC exécutent le forwarding à grande vitesse.
- La table CAM associe MAC et port ; la table ARP associe IP et MAC.
- Un VLAN permet de segmenter un switch en plusieurs domaines de diffusion.
- Le défi Canvas PC-Switch-Routeur-Cloud vérifie la compréhension des rôles de
  chaque équipement.

Comprendre ces rôles permet de lire une topologie et de savoir quel appareil
est responsable lorsqu'un paquet ne passe pas.
