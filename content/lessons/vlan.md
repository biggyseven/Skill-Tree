# VLAN, trunking 802.1Q et commutation avancée — parcours Admin Réseau Senior

> **Objectif.** Ce cours vise une maîtrise opérationnelle des VLAN au-delà du
> simple « créer un VLAN et le mettre sur un port ». À la fin, vous devez être
> capable de concevoir un plan VLAN, expliquer le chemin exact d'une trame,
> configurer un switch Cisco et un bridge Linux, diagnostiquer une fuite
> inter-VLAN, sécuriser un trunk et défendre un choix d'architecture devant
> une équipe d'exploitation.
>
> **Public :** administrateur réseau junior confirmé, candidat CCNA, ingénieur
> système qui virtualise des réseaux, ou technicien qui reprend un réseau mal
> documenté.
>
> **Durée :** 60 à 90 minutes de lecture, 90 à 120 minutes avec l'atelier de
> dépannage et les exercices.
>
> **Prérequis :** Ethernet, adressage IPv4, modèle OSI, notions de switch et
> de routeur. Les commandes Cisco IOS et Linux `iproute2` sont expliquées,
> mais une première exposition à l'une des deux plateformes aide.

## 1. Pourquoi les VLAN existent

Un réseau Ethernet commuté forme par défaut un **domaine de broadcast** : une
trame de diffusion émise par une station est relayée par le switch vers tous
les ports du même domaine, sauf le port source. Un domaine de collision a
disparu avec les switches modernes, mais le domaine de broadcast reste. Quand
des centaines de postes, imprimantes, téléphones, serveurs et équipements
d'administration partagent le même domaine, plusieurs problèmes apparaissent :

- le broadcast et le multicast consomment la bande passante de tous les ports ;
- une tempête de broadcast peut saturer le commutateur et le lien montant ;
- la table MAC devient volumineuse et les changements de topologie sont plus
  fréquents ;
- les politiques de sécurité deviennent difficiles à exprimer ;
- un incident sur un poste compromis expose tout le monde au même niveau L2 ;
- la QoS et le dépannage deviennent moins prévisibles.

Un **VLAN** (*Virtual Local Area Network*) découpe logiquement un switch, ou
un ensemble de switches, en plusieurs domaines de broadcast indépendants. Un
port appartient à un VLAN ; les trames d'un VLAN ne sont pas commutées vers un
port d'un autre VLAN au niveau 2. Pour faire communiquer deux VLAN, il faut un
équipement de niveau 3 : routeur, switch de niveau 3, pare-feu ou une fonction
équivalente.

### VLAN, sous-réseau et domaine de broadcast

Ces trois notions sont liées mais ne sont pas synonymes.

| Notion | Définition | Exemple | Remarque |
| --- | --- | --- | --- |
| Domaine de broadcast | Ensemble des ports qui reçoivent un broadcast L2 | Ports du VLAN 10 | Frontière L2 |
| VLAN | Identifiant logique de segmentation L2 | VLAN 10 « DATA » | Peut traverser plusieurs switches |
| Sous-réseau IP | Bloc d'adresses défini par un préfixe | `10.10.10.0/24` | Frontière L3 |
| Domaine de collision | Ensemble de stations qui se disputent le support | Historique, hub | Disparu avec le switch |
| Domaine de routage | Ensemble de destinations atteignables par une table de routage | VRF, table globale | Peut contenir plusieurs VLAN |

En conception classique, on associe souvent **un VLAN = un sous-réseau = une
passerelle**. Ce n'est pas une obligation physique, mais c'est une règle
simple qui facilite l'exploitation, les ACL, le DHCP et la supervision. Il
existe des exceptions : un VLAN peut transporter plusieurs sous-réseaux (rare
et souvent une mauvaise idée), et un sous-réseau peut être étendu sur plusieurs
VLAN (généralement une erreur de conception). Une exception volontaire est le
cas des private VLANs ou de certaines architectures de virtualisation.

### Segmentation logique et indépendance du câblage

Avant les VLAN, séparer deux services imposait deux switches ou deux câblages.
Avec les VLAN, un même switch physique peut héberger plusieurs réseaux logiques
et un même lien physique peut transporter plusieurs VLAN grâce au **trunking
802.1Q**. Le câblage devient plus simple, mais la configuration devient plus
délicate : une erreur de trunk, de VLAN natif ou de liste autorisée peut créer
une panne difficile à voir.

```text
Sans VLAN                                 Avec VLAN
+--------+   +--------+                    +---------------------------+
| Switch |   | Switch |                    | Switch                    |
| DATA   |   | VOIX   |                    | VLAN 10 DATA (ports 1-8)  |
+--------+   +--------+                    | VLAN 20 VOIX (ports 9-16) |
    |            |                         | VLAN 99 MGMT (port 24)    |
  postes       téléphones                  +---------------------------+
                                             trunk 802.1Q vers le coeur
```

## 2. Le format 802.1Q

Le standard IEEE 802.1Q insère un **tag de 4 octets** dans la trame Ethernet,
après la MAC source et avant le champ EtherType ou la longueur d'origine. Ce
tag identifie le VLAN et transporte des informations de priorité.

```text
Trame Ethernet non taguée
+----------+----------+-----------+---------------------+-----+
| MAC dst  | MAC src  | EtherType | Données / payload   | FCS |
| 6 octets | 6 octets | 2 octets  | 46 à 1500 octets    | 4   |
+----------+----------+-----------+---------------------+-----+

Trame Ethernet taguée 802.1Q
+----------+----------+----------+----------+-----------+-----+
| MAC dst  | MAC src  | TPID     | TCI      | EtherType | ... |
| 6 octets | 6 octets | 0x8100   | 2 octets | 2 octets  |     |
+----------+----------+----------+----------+-----------+-----+
                      |<--- 802.1Q tag 4 octets --->|
```

Le **TPID** (*Tag Protocol Identifier*) vaut `0x8100` pour 802.1Q. Le **TCI**
(*Tag Control Information*) contient trois champs :

| Champ | Taille | Rôle | Plage |
| --- | ---: | --- | --- |
| PCP (*Priority Code Point*) | 3 bits | Priorité L2, exploitée par la QoS | 0 à 7 |
| DEI (*Drop Eligible Indicator*) | 1 bit | Indique qu'une trame peut être abandonnée en cas de congestion | 0 ou 1 |
| VID (*VLAN Identifier*) | 12 bits | Numéro du VLAN | 0 à 4095 |

Le VID offre 4 096 valeurs, mais **0 et 4095 sont réservés** : 0 indique
souvent une priorité et 4095 est réservé par le standard. Le nombre de VLAN
utilisables est donc **4 094**. Les plateformes Cisco imposent en plus des
plages et des limites matérielles ; nous les verrons plus loin.

### PCP, CoS et QoS

Le PCP est souvent appelé **CoS** (*Class of Service*) dans l'écosystème
Cisco. Il permet à un switch de placer une trame dans une file de sortie
prioritaire sans analyser l'IP ou le port TCP. Les valeurs usuelles sont :

| PCP | Usage fréquent | Remarque |
| ---: | --- | --- |
| 0 | Best effort | Trafic par défaut |
| 1 | Background | Peut être dépriorisé |
| 2 | Excellent effort | — |
| 3 | Critical applications | Souvent voix ou signalling |
| 4 | Video | À valider selon la politique |
| 5 | Voice | Voix interactive, latence sensible |
| 6 | Internetwork control | Protocoles de contrôle |
| 7 | Network control | Réservé à l'infrastructure |

Le PCP n'est pas magique : il faut une politique de confiance et de
classification. Si un poste utilisateur peut marquer lui-même toutes ses
trames en PCP 7, il peut affamer les autres flux. On fait généralement
confiance au téléphone IP sur son port voix, mais pas à un PC quelconque.
La QoS de bout en bout combine PCP (L2), DSCP (L3) et éventuellement des
classifications L4. Nous détaillerons le cas voix plus bas.

### Trame taguée, trame non taguée et VLAN natif

Sur un lien **access**, le switch reçoit des trames non taguées de l'hôte,
les classe dans le VLAN du port et les émet non taguées vers l'hôte. Sur un
lien **trunk**, le switch émet les trames avec un tag 802.1Q pour chaque VLAN,
sauf pour le **VLAN natif** qui est émis sans tag. Le VLAN natif est donc un
VLAN « spécial » sur un trunk : ses trames ne portent pas d'identifiant.

```text
Port access VLAN 10                       Trunk 802.1Q
PC ---- trame non taguée ---- Switch      Switch ==== tag VLAN 10 ==== Switch
       (le port décide VLAN 10)           Switch ==== tag VLAN 20 ==== Switch
                                           Switch ---- non taguée ----- Switch
                                                    VLAN natif 999
```

Cette particularité explique deux erreurs classiques :

1. **Native VLAN mismatch** : les deux extrémités du trunk utilisent des VLAN
   natifs différents. Les trames non taguées sont classées dans le VLAN natif
   local de chaque côté ; le trafic peut fuiter d'un VLAN vers un autre.
2. **Double tagging / VLAN hopping** : un attaquant envoie une trame avec deux
   tags. Le premier switch retire le tag externe (VLAN natif) et transmet la
   trame taguée interne vers un autre VLAN. La parade principale est une
   native VLAN dédiée, inutilisée, et une politique de trunk stricte.

### Taille des trames et MTU

Le tag ajoute 4 octets. Une trame Ethernet classique de 1 518 octets (sans
FCS) devient 1 522 octets sur un trunk. La MTU IP reste généralement 1 500
octets : le tag est un en-tête L2 supplémentaire, pas une augmentation de la
charge utile IP. Certaines plateformes ou certains liens exigent d'autoriser
des « baby giants » (par exemple 1 600 octets) pour accepter les trames
taguées ou QinQ. Il ne faut pas confondre :

| Taille | Contenu |
| --- | --- |
| 1 500 octets | MTU IP classique |
| 1 518 octets | Trame Ethernet sans FCS, sans tag |
| 1 522 octets | Trame Ethernet taguée 802.1Q, sans FCS |
| 1 526 octets | Trame Ethernet avec FCS et tag |
| 1 600 octets | Baby giant souvent autorisé sur les trunks |
| 9 000+ octets | Jumbo frame, uniquement si toute la chaîne la supporte |

Une incohérence de MTU se manifeste souvent par des petits paquets qui
passent (ping, DNS) et des gros transferts qui échouent. Sur un trunk, vérifiez
la MTU de chaque interface et des équipements intermédiaires.

## 3. Modes de port et négociation

### Access, trunk, hybrid

| Mode | Comportement | Usage | Remarque |
| --- | --- | --- | --- |
| Access | Un seul VLAN, trames non taguées vers l'hôte | Poste, imprimante, serveur | `switchport mode access` |
| Trunk | Plusieurs VLAN, tags 802.1Q | Lien switch-switch, switch-routeur, hyperviseur | `switchport mode trunk` |
| Voice | Port access avec VLAN voix supplémentaire | Téléphone IP + PC | `switchport voice vlan` |
| Hybrid | Mélange de VLAN tagués et non tagués | Certains équipements Linux/routeurs | Pas un mode Cisco standard unique |
| Routed | Port L3, plus de commutation | Lien routé point-à-point | `no switchport` sur switch L3 |

Sur Cisco IOS, un port peut être en `dynamic auto`, `dynamic desirable`,
`trunk` ou `access`. Les modes dynamiques utilisent **DTP** (*Dynamic Trunking
Protocol*). DTP est pratique en laboratoire, mais dangereux en production :
un poste mal configuré ou un attaquant peut négocier un trunk et accéder à
plusieurs VLAN. La bonne pratique est de configurer explicitement les trunks
et de désactiver la négociation :

```text
interface GigabitEthernet0/1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport nonegotiate
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99
```

Selon la plateforme, `switchport trunk encapsulation dot1q` n'est pas
disponible ou est implicite. Vérifiez avec `show interfaces switchport` et
adaptez la commande à l'IOS/IOS XE/NX-OS.

### DTP en détail

DTP échange des annonces pour décider si un lien devient un trunk. Les
combinaisons classiques :

| Local | Voisin | Résultat |
| --- | --- | --- |
| dynamic desirable | dynamic desirable | Trunk |
| dynamic desirable | dynamic auto | Trunk |
| dynamic auto | dynamic auto | Access |
| trunk | dynamic auto/desirable | Trunk |
| access | trunk | Pas de trunk, souvent access |
| trunk + nonegotiate | trunk | Trunk statique |

`switchport nonegotiate` empêche les annonces DTP. Il ne faut pas le confondre
avec `no switchport` (port routé) ni avec `shutdown` (port administrativement
down). Sur un lien vers un hyperviseur ou un routeur, le trunk doit être
configuré des deux côtés ; un côté en `access` ne formera pas un trunk stable
même si l'autre est en `desirable`.

### VLAN voix

Un téléphone IP peut se connecter à un port de switch et offrir un port PC
pour cascader un ordinateur. Le switch configure alors :

```text
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 spanning-tree portfast
 spanning-tree bpduguard enable
```

Le téléphone tague la voix dans le VLAN 20 et relaie les trames du PC non
taguées dans le VLAN 10. Le port reste donc « access » du point de vue de la
configuration Cisco, avec un VLAN voix supplémentaire. Le PC ne voit pas le
VLAN voix s'il ne peut pas envoyer de trames taguées ; le téléphone, lui, est
un équipement de confiance pour ce tag. Il faut également prévoir la QoS, le
PoE et les options DHCP (serveur de call manager, TFTP, NTP).

## 4. Plages, réservations et VTP

### Plages Cisco

| Plage | VLAN | Usage | Remarque |
| --- | --- | --- | --- |
| Normale | 1–1005 | VLAN classiques | 1002–1005 réservés historiquement |
| Étendue | 1006–4094 | Opérateurs, gros réseaux | Souvent VTP transparent ou VTPv3 |
| Réservés | 0, 4095 | Standard | Ne pas utiliser |
| Défaut | 1 | VLAN par défaut | À ne pas utiliser pour les utilisateurs |

Dans la plage normale, 1002 à 1005 sont réservés à des technologies
historiques (FDDI, Token Ring, TRNET). Cela laisse 1 001 VLAN utilisables
dans la plage normale. Les VLAN étendus ne sont pas propagés par VTP version 1
ou 2 ; ils exigent VTP transparent ou VTPv3, et la plateforme doit les
supporter.

### VTP

**VTP** (*VLAN Trunking Protocol*) synchronise la base VLAN entre switches
d'un même domaine. Trois modes classiques :

| Mode | Création locale | Propagation | Base VLAN | Risque |
| --- | --- | --- | --- | --- |
| Server | Oui | Oui | Synchronisée | Peut écraser les autres |
| Client | Non | Reçoit | Synchronisée | Accepte une base incorrecte |
| Transparent | Oui | Relaie sans appliquer | Locale | Isole la base locale |
| Off (VTPv3) | Oui | Non | Locale | Recommandé si VTP n'est pas nécessaire |

Le **revision number** est le piège classique : un switch qui arrive avec un
numéro plus élevé peut remplacer la base VLAN de tout le domaine, même avec
un mot de passe faible. En production, on préfère souvent VTP transparent ou
VTPv3 configuré avec précaution, ou une gestion des VLAN par automatisation.
Ne branchez jamais un switch de laboratoire dans un domaine VTP de production
sans avoir vérifié son mode, son domaine, sa version et son revision number.

```text
vtp mode transparent
vtp domain PROD
vtp version 3
! ou, si VTP n'est pas utilisé :
vtp mode off
```

Les commandes exactes varient selon la version et la plateforme. Sur NX-OS,
VTP n'existe pas sous la même forme ; la gestion des VLAN est locale ou
automatisée.

## 5. Concevoir un plan VLAN

Un plan VLAN n'est pas une liste de numéros. C'est un contrat entre le réseau,
l'exploitation, la sécurité et les applications. Un bon plan est :

- **lisible** : un numéro et un nom compréhensibles ;
- **stable** : les identifiants ne changent pas au gré des projets ;
- **hiérarchique** : les VLAN sont regroupés par site, fonction ou domaine ;
- **documenté** : chaque VLAN a un propriétaire, un sous-réseau, une passerelle,
  une politique DHCP et une politique de sécurité ;
- **agrégable** : les sous-réseaux permettent des résumés de routage ;
- **cohérent** : les mêmes conventions s'appliquent à tous les sites ;
- **maîtrisé** : les VLAN inutilisés ne sont pas autorisés sur les trunks.

### Modèle de registre VLAN

| Champ | Exemple | Pourquoi |
| --- | --- | --- |
| ID | 10 | Identifiant technique |
| Nom | DATA-PARIS | Lisible dans `show vlan` |
| Site | PARIS | Localisation |
| Fonction | Postes utilisateurs | Usage |
| Sous-réseau | `10.10.10.0/24` | Adressage |
| Passerelle | `10.10.10.1` | SVI ou routeur |
| DHCP | `10.10.10.100–10.10.10.220` | Plage dynamique |
| Exclusions | `.1–.99`, `.221–.254` | Statiques, VIP, réserves |
| Native/trunk | Non | Politique L2 |
| Sécurité | 802.1X, ACL, PVLAN | Contrôles |
| Propriétaire | Équipe Réseau | Responsabilité |
| Revue | 2026-10-19 | Cycle de vie |

### VLAN de gestion, VLAN natif et VLAN noir

- **VLAN de gestion** : VLAN dédié aux adresses de management des switches,
  avec ACL, 802.1X ou jump host. Ne pas utiliser le VLAN 1.
- **VLAN natif** : VLAN dédié aux trames non taguées sur les trunks. Il doit
  être identique aux deux extrémités et ne transporter aucun utilisateur.
  Un « VLAN noir » (blackhole) sans port actif est une bonne pratique.
- **VLAN 1** : VLAN par défaut, souvent utilisé par CDP, VTP, DTP, STP et
  certains protocoles. Le supprimer partout peut casser des fonctions ; le
  laisser vide d'utilisateurs et le contrôler est plus réaliste.
- **VLAN de secours** : VLAN utilisé lorsqu'un port 802.1X échoue ou qu'un
  équipement inconnu se branche. Il doit être isolé et filtré.

### Pruning et liste autorisée

Deux mécanismes différents :

| Mécanisme | Où | Effet | Remarque |
| --- | --- | --- | --- |
| `switchport trunk allowed vlan` | Configuration du port | Filtre local des VLAN autorisés | À privilégier |
| VTP pruning | Domaine VTP | Réduit la propagation du broadcast | Ne remplace pas une ACL de trunk |
| `switchport trunk pruning vlan` | Port | Liste de pruning par port | Souvent mal compris |

Sur un trunk, configurez une liste explicite et ajoutez les VLAN au besoin.
`switchport trunk allowed vlan all` est pratique en lab, mais expose tous les
VLAN en production. Après une modification, vérifiez avec `show interfaces
trunk` et testez la connectivité de chaque VLAN critique.

### STP par VLAN

PVST+ et Rapid-PVST+ construisent une instance STP par VLAN. Une boucle L2
peut donc être bloquée dans un VLAN et active dans un autre. MSTP regroupe
plusieurs VLAN dans une instance et réduit le nombre d'instances. En cas de
convergence lente ou de topologie instable, vérifiez :

```text
show spanning-tree summary
show spanning-tree vlan 10
show spanning-tree interface GigabitEthernet0/1
show spanning-tree root
```

Un port access utilisateur reçoit souvent `portfast` et `bpduguard` ; un port
de trunk ne doit pas recevoir `portfast` sans réflexion. Un BPDU inattendu sur
un port utilisateur peut indiquer un switch non autorisé ou une boucle.

## 6. Configuration Cisco pas à pas

### Créer les VLAN

```text
enable
configure terminal
vlan 10
 name DATA
vlan 20
 name VOICE
vlan 99
 name MGMT
vlan 999
 name NATIVE-BLACKHOLE
exit
show vlan brief
show vlan id 10
```

### Configurer un port access

```text
interface GigabitEthernet0/1
 description Poste utilisateur VLAN 10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown
end
show interfaces GigabitEthernet0/1 switchport
show vlan id 10
```

### Configurer un trunk

```text
interface GigabitEthernet0/24
 description Trunk vers coeur
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport nonegotiate
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99
 no shutdown
end
show interfaces GigabitEthernet0/24 trunk
show interfaces GigabitEthernet0/24 switchport
show spanning-tree interface GigabitEthernet0/24
```

### Ajouter ou retirer un VLAN d'un trunk

```text
interface GigabitEthernet0/24
 switchport trunk allowed vlan add 30
 switchport trunk allowed vlan remove 20
! Remplacer toute la liste :
 switchport trunk allowed vlan 10,30,99
```

`add` et `remove` modifient la liste existante. Sans mot-clé, la commande
remplace la liste. Une erreur de syntaxe peut couper un VLAN de management :
utilisez une session de secours ou une interface hors bande.

### SVI et routage inter-VLAN sur switch L3

```text
ip routing
interface Vlan10
 description Passerelle DATA
 ip address 10.10.10.1 255.255.255.0
 no shutdown
interface Vlan20
 description Passerelle VOICE
 ip address 10.10.20.1 255.255.255.0
 no shutdown
interface Vlan99
 description Passerelle MGMT
 ip address 10.10.99.1 255.255.255.0
 no shutdown
end
show ip interface brief
show ip route connected
```

La SVI n'est up que si au moins un port du VLAN est up et si le VLAN existe.
Sur certaines plateformes, `interface Vlan10` peut être créée sans port actif
et rester down. Vérifiez `show ip interface brief` et `show vlan id 10`.

### Router-on-a-stick

Quand le routage est assuré par un routeur externe, le lien vers le switch est
un trunk et le routeur utilise des sous-interfaces :

```text
interface GigabitEthernet0/0
 no shutdown
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.10.10.1 255.255.255.0
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.10.20.1 255.255.255.0
interface GigabitEthernet0/0.999
 encapsulation dot1Q 999 native
 ip address 10.10.99.1 255.255.255.0
```

Le VLAN natif doit correspondre au `native` de la sous-interface et à la
configuration du switch. Un trunk unique concentre tout le trafic inter-VLAN :
surveillez la bande passante et prévoyez une redondance.

### DHCP relay

Les clients d'un VLAN qui n'ont pas de serveur DHCP local ont besoin d'un
relais :

```text
interface Vlan10
 ip address 10.10.10.1 255.255.255.0
 ip helper-address 10.10.99.10
```

`ip helper-address` relaie les broadcasts UDP configurés, pas seulement DHCP.
Vérifiez les ACL, la route retour vers le VLAN client et l'option 82 si le
serveur l'utilise. Le relais doit être placé sur la passerelle du VLAN, pas
sur un VLAN distant sans route.

### Vérifications Cisco essentielles

```text
show vlan brief
show vlan id 10
show interfaces status
show interfaces switchport
show interfaces trunk
show interfaces GigabitEthernet0/1 trunk
show mac address-table vlan 10
show spanning-tree vlan 10
show ip interface brief
show ip route
show cdp neighbors detail
show lldp neighbors detail
show power inline
show mls qos interface
show policy-map interface
```

Interprétez les sorties :

- `show vlan brief` liste les ports actifs par VLAN ;
- `show interfaces trunk` affiche mode, encapsulation, native VLAN, liste
  autorisée et VLAN actifs ;
- `show interfaces switchport` confirme le mode administratif et opérationnel ;
- `show mac address-table vlan 10` localise une MAC apprise dans le VLAN ;
- `show spanning-tree vlan 10` indique le rôle et l'état STP ;
- `show power inline` vérifie le budget PoE d'un téléphone ou d'un AP.

## 7. VLAN et bridging sous Linux

Linux est souvent le commutateur d'un laboratoire, l'hyperviseur d'une
infrastructure virtualisée ou le système d'exploitation d'un serveur qui doit
recevoir plusieurs VLAN. Il faut distinguer deux usages :

1. **Interface VLAN** : le noyau traite les tags et expose `eth0.10` comme une
   interface distincte, à laquelle on affecte une adresse IP.
2. **Bridge avec filtrage VLAN** : le noyau commute des trames entre ports et
   applique les règles `pvid`, `tagged` et `untagged` comme un switch.

### Créer une interface VLAN avec iproute2

```bash
sudo ip link add link eth0 name eth0.10 type vlan id 10
sudo ip link set eth0.10 up
sudo ip addr add 10.10.10.254/24 dev eth0.10
ip -d link show eth0.10
ip -br address show eth0.10
```

La commande `ip -d link show` affiche `vlan protocol 802.1Q id 10`. Pour
supprimer l'interface :

```bash
sudo ip link del eth0.10
```

La configuration manuelle disparaît au redémarrage. Utilisez NetworkManager,
systemd-networkd, Netplan ou votre gestionnaire de configuration pour la
rendre persistante.

### Créer un bridge avec filtrage VLAN

```bash
sudo ip link add name br0 type bridge
sudo ip link set br0 type bridge vlan_filtering 1
sudo ip link set eth0 master br0
sudo ip link set eth1 master br0
sudo ip link set br0 up
sudo ip link set eth0 up
sudo ip link set eth1 up

# Port d'accès VLAN 10 non tagué
sudo bridge vlan add vid 10 dev eth0 pvid untagged
# Port trunk VLAN 10 et 20 tagués
sudo bridge vlan add vid 10 dev eth1
sudo bridge vlan add vid 20 dev eth1
# VLAN autorisés sur le bridge lui-même
sudo bridge vlan add vid 10 dev br0 self
sudo bridge vlan add vid 20 dev br0 self

bridge vlan show
bridge link show
bridge fdb show
```

Le mot-clé `pvid` définit le VLAN des trames non taguées reçues sur le port.
`untagged` contrôle l'émission sans tag. Un port trunk ne doit généralement
pas avoir de `pvid` utilisateur ; il transporte des VLAN tagués et un VLAN
natif éventuel. `bridge vlan show` est l'équivalent de `show vlan` et
`show interfaces trunk` sur un switch Cisco.

Si un port est ajouté au bridge sans être up, il ne transmet rien. Vérifiez :

```bash
ip -d link show br0
ip -d link show eth0
bridge vlan show dev eth0
bridge vlan show dev eth1
```

### NetworkManager

Exemple d'interface VLAN :

```bash
nmcli connection add type vlan con-name vlan10 dev eth0 id 10
nmcli connection modify vlan10 ipv4.method manual \
  ipv4.addresses 10.10.10.254/24 \
  ipv4.gateway 10.10.10.1 \
  ipv4.dns 10.10.99.53
nmcli connection up vlan10
nmcli connection show vlan10
```

Exemple de bridge (les noms de propriétés varient selon la version) :

```bash
nmcli connection add type bridge con-name br0 ifname br0
nmcli connection add type ethernet con-name br0-eth0 ifname eth0 master br0
nmcli connection modify br0 bridge.vlan-filtering yes
nmcli connection up br0
nmcli connection up br0-eth0
```

Vérifiez toujours avec `nmcli connection show <nom>` et `bridge vlan show`.
Une propriété inconnue fait échouer la commande ; ne supposez pas qu'une
syntaxe trouvée sur Internet correspond à votre version.

### systemd-networkd

Fichier `/etc/systemd/network/10-eth0.netdev` :

```ini
[NetDev]
Name=eth0.10
Kind=vlan

[VLAN]
Id=10
```

Fichier `/etc/systemd/network/10-eth0.network` :

```ini
[Match]
Name=eth0

[Network]
VLAN=eth0.10
```

Fichier `/etc/systemd/network/20-eth0.10.network` :

```ini
[Match]
Name=eth0.10

[Network]
Address=10.10.10.254/24
Gateway=10.10.10.1
DNS=10.10.99.53
```

Puis :

```bash
sudo systemctl restart systemd-networkd
networkctl status eth0.10
```

### Netplan

Exemple minimal pour une interface VLAN :

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: false
  vlans:
    eth0.10:
      id: 10
      link: eth0
      addresses: [10.10.10.254/24]
      routes:
        - to: default
          via: 10.10.10.1
      nameservers:
        addresses: [10.10.99.53]
```

Pour un bridge avec filtrage VLAN, la prise en charge dépend de la version de
Netplan et du backend. Vérifiez la documentation de votre distribution et
testez dans un laboratoire avant de déployer. Une configuration YAML invalide
peut couper l'accès de gestion ; conservez une console série ou un accès hors
bande.

### VLAN dans les namespaces réseau

Les namespaces réseau Linux sont d'excellents laboratoires pour reproduire un
switch. On crée des paires veth et on les place dans des namespaces :

```bash
sudo ip netns add h1
sudo ip netns add h2
sudo ip link add h1-eth0 type veth peer name sw1
sudo ip link add h2-eth0 type veth peer name sw2
sudo ip link set h1-eth0 netns h1
sudo ip link set h2-eth0 netns h2
sudo ip link set sw1 master br0
sudo ip link set sw2 master br0
sudo ip link set sw1 up
sudo ip link set sw2 up
sudo ip netns exec h1 ip addr add 10.10.10.10/24 dev h1-eth0
sudo ip netns exec h2 ip addr add 10.10.10.20/24 dev h2-eth0
sudo ip netns exec h1 ip link set h1-eth0 up
sudo ip netns exec h2 ip link set h2-eth0 up
sudo ip netns exec h1 ping -c 2 10.10.10.20
```

Pour tester deux VLAN sur un même bridge, créez deux bridges ou activez le
filtrage VLAN et configurez les `pvid` différemment. Un ping entre deux VLAN
doit échouer sans routeur, puis réussir après ajout d'une interface de
passerelle et de routes.

### Capture et preuve sur Linux

```bash
sudo tcpdump -ni eth0 -e
sudo tcpdump -ni eth0 -e 'vlan 10'
sudo tcpdump -ni eth0 -e 'arp or icmp'
```

`-e` affiche l'en-tête Ethernet, y compris le tag 802.1Q. Une trame taguée
apparaît avec `vlan 10` et une trame access arrive sans tag. Pour capturer sur
un bridge, utilisez l'interface du bridge ou un port miroir ; les règles de
filtrage VLAN s'appliquent avant ou après la capture selon le point
d'observation. Comparez toujours une capture côté émetteur et côté récepteur
avant de conclure.

## 8. Chemin d'une trame, apprentissage MAC et STP

### Même VLAN, même switch

```text
Hôte A (VLAN 10) -- port access 1 -- SW1 -- port access 2 -- Hôte B (VLAN 10)

1. A émet une trame non taguée.
2. SW1 classe la trame dans le VLAN 10 du port 1.
3. SW1 apprend MAC-A dans le VLAN 10, port 1.
4. La destination MAC-B est inconnue : flood dans le VLAN 10 uniquement.
5. B répond, SW1 apprend MAC-B dans le VLAN 10, port 2.
6. La trame sort non taguée vers B.
```

Le switch maintient une table MAC **par VLAN**. La même MAC peut apparaître
dans plusieurs VLAN sans conflit logique, même si cela révèle souvent un
équipement mal configuré ou un pont hasardeux.

### Même VLAN, plusieurs switches

```text
Hôte A -- SW1 == trunk tag 10 == SW2 -- Hôte B

1. SW1 classe la trame de A dans VLAN 10.
2. Sur le trunk, SW1 ajoute le tag 802.1Q VLAN 10.
3. SW2 reçoit la trame taguée, vérifie que le VLAN 10 est autorisé et connu.
4. SW2 apprend MAC-A dans VLAN 10 sur le trunk.
5. SW2 retire le tag vers le port access de B.
```

Si le VLAN 10 n'existe pas sur SW2, la trame taguée est jetée. Si le VLAN
existe mais n'est pas dans `allowed vlan`, elle est également jetée. Si le
trunk est en `access`, le comportement est encore différent : la trame peut
être classée dans le VLAN du port access ou rejetée.

### VLAN différents, même switch

```text
Hôte A (VLAN 10) -- SW1 -- SVI VLAN 10 (10.10.10.1)
                         SVI VLAN 20 (10.10.20.1) -- Hôte B (VLAN 20)
```

A envoie la trame à la MAC de sa passerelle (SVI 10), pas à la MAC de B. Le
switch route le paquet : il décrémente le TTL, conserve les adresses IP
(source A, destination B), réécrit l'en-tête Ethernet avec la MAC de B et
émet la trame dans le VLAN 20. Le retour suit le chemin inverse. Un ping qui
échoue peut donc venir d'une passerelle absente, d'une ACL, d'une route
retour ou d'un ARP non résolu.

### Broadcast, multicast et unknown unicast

Dans un VLAN, un broadcast est floodé vers tous les ports actifs du VLAN sauf
le port source. Un unknown unicast (destination MAC absente de la table) est
également floodé dans le VLAN. Le multicast peut être floodé ou optimisé par
IGMP snooping. C'est pourquoi un VLAN trop grand amplifie les tempêtes et
pourquoi la segmentation réduit le rayon de panne.

### STP par VLAN

Avec PVST+, chaque VLAN a son instance STP. Une boucle physique peut être
bloquée dans un VLAN et active dans un autre. Avec MSTP, plusieurs VLAN sont
regroupés dans une instance, ce qui réduit la charge de calcul et permet des
topologies différentes par groupe. Vérifiez toujours :

```text
show spanning-tree summary
show spanning-tree vlan 10
show spanning-tree mst configuration
show spanning-tree mst 0
```

Un `Topology Change Notification` répété, un port qui passe `forwarding` puis
`blocking`, ou un compteur de changements élevé doit faire suspecter une
boucle, un lien instable ou un `portfast` mal placé.

## 9. Comparer les options de routage inter-VLAN

| Solution | Où le routage est fait | Avantages | Limites |
| --- | --- | --- | --- |
| Router-on-a-stick | Routeur externe, sous-interfaces | Simple, ACL centralisées | Lien unique, débit limité, point de panne |
| SVI sur switch L3 | Switch de distribution | Rapide, matériel, redondance | Coût, complexité de configuration |
| Port routé + switch L2 | Routeur/pare-feu + switch | Contrôle de sécurité | Plus de liens, moins de flexibilité |
| Pare-feu inter-VLAN | Pare-feu | Filtrage fin, inspection | Coût, latence, dimensionnement |
| VRF | Routeur/switch L3 | Isolation de tables | Pas une segmentation L2 |
| EVPN/VXLAN | Overlay | Extension, mobilité | Compétences, MTU, contrôle plane |

Le choix dépend du volume, des exigences de sécurité et de la redondance. Un
réseau de 20 postes peut vivre avec un routeur-on-a-stick ; un campus de
5 000 utilisateurs a besoin d'une architecture L3 distribuée. Dans tous les
cas, la passerelle de chaque VLAN doit être joignable, et la route retour doit
exister.

### Routage asymétrique

Si l'aller passe par le routeur A et le retour par le routeur B, un pare-feu
stateful peut bloquer la réponse. Vérifiez les tables de routage des deux
côtés, les métriques, les routes par défaut et les sessions NAT. Une
asymétrie est parfois intentionnelle (trafic entrant/sortant), mais elle doit
être conçue et documentée.

## 10. Sécurité L2 et VLAN

Un VLAN isole les broadcasts, mais **ne constitue pas à lui seul une frontière
de sécurité**. Un attaquant qui compromet un switch ou obtient un trunk peut
franchir la segmentation. Les menaces classiques :

| Menace | Mécanisme | Impact | Parade |
| --- | --- | --- | --- |
| Switch spoofing | Faux switch négociant DTP | Accès à tous les VLAN | `switchport mode access`, `nonegotiate`, désactiver DTP |
| Double tagging | Deux tags 802.1Q | Fuite vers un autre VLAN | Native VLAN dédiée, pas de VLAN 1 utilisateur |
| MAC flooding | Saturation de la table CAM | Flood de trafic | Port security, limitation MAC |
| DHCP rogue | Faux serveur DHCP | Passerelle/DNS malveillants | DHCP snooping, port security |
| ARP spoofing | Fausses réponses ARP | Interception | Dynamic ARP Inspection |
| IP spoofing | Source usurpée | Contournement d'ACL | IP Source Guard, uRPF |
| Broadcast storm | Boucle L2 | Panne généralisée | STP, storm control, BPDU guard |
| VLAN hopping | Combinaison des techniques | Accès inter-VLAN | Durcissement des trunks |

### Durcir un port utilisateur

```text
interface GigabitEthernet0/2
 description Poste utilisateur
 switchport mode access
 switchport access vlan 10
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
 storm-control broadcast level 5
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
 no shutdown
```

Les commandes exactes de port security varient. `sticky` apprend les MAC et
les enregistre dans la configuration courante ; il faut sauvegarder la
configuration et prévoir le remplacement des équipements. Une violation
`shutdown` coupe le port : utile en sécurité, mais peut créer un incident si
un utilisateur branche un mini-switch non autorisé. `restrict` journalise et
limite sans couper.

### DHCP snooping, DAI et IP Source Guard

Ces fonctions construisent une base de liaisons IP/MAC/port fiable :

```text
ip dhcp snooping
ip dhcp snooping vlan 10,20
interface GigabitEthernet0/24
 ip dhcp snooping trust
interface GigabitEthernet0/1
 ip dhcp snooping limit rate 10
```

```text
ip arp inspection vlan 10,20
interface GigabitEthernet0/24
 ip arp inspection trust
```

Activez-les d'abord en supervision ou sur un VLAN pilote. Un port uplink vers
un serveur DHCP légitime doit être `trust`; un port utilisateur ne doit pas
l'être. Une mauvaise confiance peut bloquer tous les clients d'un VLAN.

### Private VLANs

Les private VLANs segmentent des hôtes sur le même sous-réseau sans multiplier
les passerelles. Trois rôles :

| Rôle | Peut parler à | Usage |
| --- | --- | --- |
| Promiscuous | Tous les ports du PVLAN | Passerelle, routeur, firewall |
| Isolated | Promiscuous uniquement | Clients mutualisés, serveurs isolés |
| Community | Membres de sa communauté + promiscuous | Groupe de serveurs qui collaborent |

```text
vlan 100
 private-vlan primary
vlan 101
 private-vlan isolated
vlan 102
 private-vlan community
vlan 100
 private-vlan association 101,102
interface GigabitEthernet0/1
 switchport mode private-vlan host
 switchport private-vlan host-association 100 101
interface GigabitEthernet0/24
 switchport mode private-vlan promiscuous
 switchport private-vlan mapping 100 101,102
```

La prise en charge dépend de la plateforme et du mode VTP. Documentez les
communautés, car la table de commutation et les ACL peuvent devenir difficiles
à relire. Un PVLAN ne remplace pas une ACL L3 si vous devez filtrer des flux
IP précis.

### VLAN dynamique et 802.1X

Avec 802.1X, un port peut être placé dans un VLAN après authentification. Le
serveur RADIUS renvoie des attributs (par exemple `Tunnel-Type`, `Tunnel-
Medium-Type`, `Tunnel-Private-Group-ID`). Vérifiez la configuration du switch,
la méthode EAP, le VLAN d'échec et la politique de revalidation. Un VLAN
dynamique mal configuré peut envoyer un utilisateur dans le VLAN invité ou le
laisser sans connectivité.

## 11. Cas pratique : séparer la voix et les données

### Contexte

Une entreprise de 300 personnes réparties sur deux sites veut refondre son
réseau d'accès. Elle utilise un IPBX central, des téléphones PoE, un Wi-Fi
invité et un serveur de gestion. Les objectifs :

- isoler la voix des postes de travail ;
- garantir une latence et une gigue faibles pour la voix ;
- empêcher les invités d'atteindre le réseau interne ;
- simplifier le déploiement des téléphones ;
- conserver un VLAN de gestion séparé ;
- pouvoir diagnostiquer rapidement un téléphone muet ou un appel à sens unique ;
- préparer une extension vers un site distant.

### Plan VLAN proposé

| VLAN | Nom | Sous-réseau | Passerelle | Usage |
| ---: | --- | --- | --- | --- |
| 10 | DATA | `10.20.10.0/24` | `10.20.10.1` | Postes utilisateurs |
| 20 | VOICE | `10.20.20.0/24` | `10.20.20.1` | Téléphones IP |
| 30 | WIFI-CORP | `10.20.30.0/24` | `10.20.30.1` | Wi-Fi collaborateurs |
| 40 | GUEST | `10.20.40.0/24` | `10.20.40.1` | Wi-Fi invités, isolé |
| 50 | SERVERS | `10.20.50.0/24` | `10.20.50.1` | Applications internes |
| 99 | MGMT | `10.20.99.0/24` | `10.20.99.1` | Management |
| 999 | NATIVE-BLACKHOLE | non adressé | — | Native VLAN des trunks |

Les VLAN 10 à 50 sont routés par un switch L3 ou un pare-feu. Le VLAN 999 ne
porte aucun utilisateur. Le VLAN 99 est protégé par une ACL et accessible
uniquement depuis un réseau d'administration. Le VLAN 40 est filtré vers
Internet uniquement.

### Topologie

```text
                 +-------------------------------+
                 |        Coeur L3 / Pare-feu     |
                 | SVI 10,20,30,40,50,99          |
                 +---------------+---------------+
                                 |
                         trunk 802.1Q
                 allowed 10,20,30,40,50,99
                 native 999, nonegotiate
                                 |
          +----------------------+----------------------+
          |                                             |
   +------+------+                               +------+------+
   | Accès SW1   |                               | Accès SW2   |
   | VLAN 10     |                               | VLAN 10     |
   | VLAN 20     |                               | VLAN 20     |
   +------+------+                               +------+------+
          |                                             |
    PC ----+---- Téléphone IP                    PC ----+---- Téléphone IP
         (VLAN 10)  (VLAN 20)                       (VLAN 10)  (VLAN 20)
```

### Configuration d'un port utilisateur avec téléphone

```text
interface GigabitEthernet0/1
 description Poste + telephone IP
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 switchport nonegotiate
 spanning-tree portfast
 spanning-tree bpduguard enable
 mls qos trust cos
 no shutdown
```

Le téléphone tague la voix en VLAN 20 et relaie le PC en VLAN 10. `mls qos
trust cos` fait confiance au PCP marqué par le téléphone. Selon la plateforme,
la commande de confiance QoS peut être `mls qos trust dscp`, `auto qos voip
trust` ou une politique plus fine. Ne faites pas confiance à un PC sur le
même port sans classification.

### Configuration du trunk

```text
interface GigabitEthernet0/24
 description Uplink vers coeur
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport nonegotiate
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,50,99
 no shutdown
end
show interfaces GigabitEthernet0/24 trunk
```

### Passerelles et DHCP

```text
ip routing
interface Vlan10
 ip address 10.20.10.1 255.255.255.0
 ip helper-address 10.20.50.10
 no shutdown
interface Vlan20
 ip address 10.20.20.1 255.255.255.0
 ip helper-address 10.20.50.10
 no shutdown
interface Vlan99
 ip address 10.20.99.1 255.255.255.0
 no shutdown
```

Le serveur DHCP doit avoir des pools par VLAN, avec les options voix :

| Option | Valeur | Usage |
| --- | --- | --- |
| 3 | `10.20.20.1` | Passerelle du VLAN voix |
| 6 | `10.20.50.53` | DNS |
| 42 | `10.20.50.20` | NTP |
| 66 | `10.20.50.30` | Serveur TFTP / provisioning |
| 150 | `10.20.50.30` | Option TFTP/TFTP liste pour certains téléphones |
| 160 | URL de provisioning | Selon le constructeur |

Les options exactes dépendent du constructeur du téléphone. Vérifiez la
documentation du IPBX et capturez le DHCP si un téléphone reste en
« provisioning ».

### QoS de bout en bout

| Flux | DSCP recommandé | PCP | Traitement |
| --- | ---: | ---: | --- |
| Voix RTP | EF (46) | 5 | File prioritaire, admission |
| Signalisation | CS3 (24) | 3 | File dédiée, faible latence |
| Vidéo interactive | AF41 (34) | 4 | File vidéo |
| Données critiques | AF21/AF31 | 2/3 | Selon politique |
| Best effort | 0 | 0 | Défaut |
| Scavenger | CS1 (8) | 1 | Dépriorisé |

La voix doit être protégée contre la congestion, mais aussi contre la gigue.
Sur un lien lent, une file prioritaire stricte pour la voix peut affamer les
autres flux si elle n'est pas dimensionnée. Utilisez un LLQ (low-latency
queue) avec police et surveillez les drops.

### Vérification du cas voix

```text
show vlan brief
show interfaces GigabitEthernet0/1 switchport
show interfaces GigabitEthernet0/1 trunk
show power inline GigabitEthernet0/1
show lldp neighbors detail
show cdp neighbors detail
show mls qos interface GigabitEthernet0/1
show policy-map interface GigabitEthernet0/1
show mac address-table vlan 20
show ip interface brief
show ip route 10.20.50.30
```

À faire côté téléphone : vérifier l'adresse IP, le VLAN reçu, l'option 150,
l'heure NTP, l'enregistrement au IPBX. Si le téléphone a une adresse du VLAN
10, il n'a pas reçu le bon VLAN voix ou le port n'est pas configuré avec
`switchport voice vlan`.

### Pannes typiques du cas voix

| Symptôme | Cause probable | Vérification |
| --- | --- | --- |
| Téléphone sans PoE | Budget PoE, port, câble | `show power inline`, journal |
| Téléphone en VLAN données | Voice VLAN absente ou LLDP-MED/CDP | `show interfaces switchport` |
| Pas d'enregistrement | Option 66/150, route, DNS | Capture DHCP, options, `show ip route` |
| Voix hachée | Congestion, QoS, duplex | `show interfaces`, QoS counters |
| Un seul sens audio | Routage asymétrique, ACL, NAT | Routes, captures aux deux extrémités |
| Appels qui coupent | STP, erreurs, perte | `show interfaces`, logs, capture |
| Téléphone redémarre | PoE instable, firmware, boucle | `show power inline`, logs |

## 12. Atelier de dépannage

### Méthode en sept étapes

1. **Définir la portée** : un utilisateur, un VLAN, un switch, un site ou tous
   les sites ? Depuis quand ? Qu'est-ce qui a changé ?
2. **Collecter les faits** : adresse IP, masque, passerelle, VLAN, port,
   état du lien, heure du dernier changement.
3. **Vérifier la couche 1** : câble, SFP, PoE, vitesse/duplex, erreurs.
4. **Vérifier la couche 2** : VLAN existe, port dans le bon VLAN, trunk
   autorisé, native VLAN, STP, table MAC.
5. **Vérifier la couche 3** : passerelle, ARP, route, ACL, NAT.
6. **Vérifier les services** : DHCP, DNS, NTP, IPBX, authentification.
7. **Prouver et documenter** : capture, compteur, commande, heure, résultat,
   correction, test de non-régression.

### Tableau symptôme → cause → commande

| Symptôme | Causes fréquentes | Commandes |
| --- | --- | --- |
| Port down | Câble, SFP, `shutdown`, vitesse | `show interfaces status`, `show interfaces` |
| Pas de VLAN sur le port | Mauvais VLAN, port access | `show interfaces switchport`, `show vlan brief` |
| Trunk down | Encapsulation, mode, câble | `show interfaces trunk`, `show interfaces` |
| VLAN absent du trunk | `allowed vlan`, VLAN non créé, pruning | `show interfaces trunk`, `show vlan id` |
| Fuite inter-VLAN | Native mismatch, double tag | `show interfaces trunk`, capture |
| SVI down | Aucun port actif, VLAN absent, shutdown | `show ip interface brief`, `show vlan id` |
| Inter-VLAN KO | `ip routing`, passerelle, ACL | `show ip route`, `show ip interface brief` |
| DHCP KO | Helper, pool, route retour, ACL | Capture DORA, `show ip dhcp binding` |
| Broadcast storm | Boucle, STP, storm control | `show spanning-tree`, compteurs |
| MAC flap | Boucle, NIC teaming, duplicate MAC | `show mac address-table`, logs |
| MTU | Baby giant, jumbo, tunnel | Ping DF, captures, `show interfaces` |
| Voix mauvaise | QoS, congestion, duplex | `show mls qos`, `show interfaces` |

### Scénario 1 : le VLAN 30 ne passe pas

Deux switches sont reliés par un trunk up. Le VLAN 30 fonctionne sur SW1 mais
pas sur SW2. Procédure :

```text
show vlan id 30
show interfaces trunk
show interfaces GigabitEthernet0/24 switchport
show spanning-tree vlan 30
show mac address-table vlan 30
```

Hypothèses :

- VLAN 30 absent de SW2 : les trames taguées sont jetées ;
- VLAN 30 présent mais absent de `allowed vlan` : même résultat ;
- VLAN 30 suspendu par VTP ou par un pruning incorrect ;
- port access sur SW2 dans le mauvais VLAN ;
- STP bloqué ou en écoute ;
- native VLAN mismatch si le trafic arrive non tagué.

Correction : créer le VLAN des deux côtés, l'ajouter à la liste autorisée,
vérifier STP et la table MAC. Si le trunk est en `access` d'un côté, le
corriger avant tout autre test.

### Scénario 2 : native VLAN mismatch

Symptôme : le management devient instable, certains postes voient des adresses
d'un autre VLAN, les logs CDP signalent un mismatch.

```text
show interfaces trunk
show cdp neighbors detail
show vlan brief
```

Les trames non taguées sont classées dans le VLAN natif local. Si SW1 utilise
le VLAN 1 et SW2 le VLAN 999, une trame de management non taguée peut arriver
dans le VLAN 999 ou être perdue. Correction : aligner la native VLAN des deux
côtés, idéalement sur un VLAN noir inutilisé, puis vérifier l'absence de fuite.
Ne pas se contenter de changer un côté : le mismatch peut persister dans
l'autre sens.

### Scénario 3 : le trunk ne se forme pas

```text
show interfaces GigabitEthernet0/24 switchport
show interfaces GigabitEthernet0/24 trunk
show interfaces GigabitEthernet0/24
```

Causes :

- un côté en `switchport mode access` ;
- encapsulation différente (ISL vs dot1Q) ;
- DTP désactivé d'un côté et mode dynamique de l'autre ;
- câble, SFP ou port down ;
- vitesse/duplex incohérents ;
- port bloqué par une fonction de sécurité.

Correction : configurer explicitement `switchport mode trunk`, `switchport
trunk encapsulation dot1q` si nécessaire, `nonegotiate` des deux côtés, puis
vérifier `show interfaces trunk`.

### Scénario 4 : SVI down malgré un VLAN existant

```text
show ip interface brief
show vlan id 10
show interfaces status
show running-config interface Vlan10
```

Une SVI peut être down si aucun port du VLAN n'est up, si le VLAN n'existe pas
ou si l'interface est shutdown. Sur un switch L3, `ip routing` doit être
activé pour router entre les SVI. Vérifiez aussi qu'un port n'est pas en
err-disabled ou bloqué par STP.

### Scénario 5 : le ping inter-VLAN échoue

```text
show ip route
show ip interface brief
show arp
show access-lists
show run interface Vlan10
show run interface Vlan20
```

Ordre de diagnostic :

1. le client a-t-il la bonne passerelle ?
2. la passerelle est-elle up et dans le bon VLAN ?
3. la MAC de la passerelle est-elle résolue (ARP) ?
4. le switch route-t-il (`ip routing`) ?
5. une ACL ou un pare-feu bloque-t-il l'ICMP ?
6. la route retour existe-t-elle ?
7. le NAT ou un load-balancer modifie-t-il le flux ?

Un ping peut être bloqué par une ACL alors que le TCP fonctionne. Testez avec
le protocole applicatif réel et capturez.

### Scénario 6 : DHCP ne répond pas

```text
show run interface Vlan10
show ip dhcp binding
show ip dhcp pool
show ip route 10.20.50.10
show access-lists
```

Vérifiez le relais (`ip helper-address`), le pool, l'épuisement, la route
retour, l'option 82, le VLAN du client et le filtrage DHCP snooping. Une
capture `tcpdump` ou un SPAN montre si Discover arrive au serveur et si Offer
revient.

### Scénario 7 : tempête de broadcast

```text
show interfaces | include broadcast|multicast|output errors
show spanning-tree summary
show spanning-tree vlan 10
show mac address-table | count
show processes cpu | include CPU
```

Causes : boucle L2, NIC teaming mal configuré, mini-switch utilisateur,
STP désactivé, port miroir rebouclé. Activez `storm-control`, `bpduguard`,
`root guard` aux endroits appropriés, et corrigez la boucle avant d'augmenter
les seuils.

### Scénario 8 : un seul sens audio

La voix utilise RTP dans les deux sens. Un seul sens indique souvent un
problème de routage retour, de NAT, d'ACL ou de pare-feu. Vérifiez :

- les routes vers le réseau du téléphone et du IPBX dans les deux sens ;
- les règles du pare-feu pour UDP RTP et la signalisation ;
- les translations NAT et les ports ;
- la symétrie du chemin ;
- les captures sur les deux extrémités ;
- la QoS et les drops sur le lien.

### Capture avec SPAN

```text
monitor session 1 source interface GigabitEthernet0/1 both
monitor session 1 destination interface GigabitEthernet0/24
show monitor session 1
```

Le port destination ne commute plus normalement ; utilisez un port dédié et
documentez-le. Pour capturer un trunk, la session SPAN peut inclure les tags
selon la plateforme ; vérifiez avec `tcpdump -e`.

### Checklist de dépannage VLAN

- [ ] Le VLAN existe-t-il sur tous les switches concernés ?
- [ ] Le port est-il dans le bon mode (access/trunk) ?
- [ ] Le VLAN est-il autorisé sur chaque trunk du chemin ?
- [ ] La native VLAN est-elle identique et inutilisée ?
- [ ] DTP est-il désactivé sur les liens de production ?
- [ ] STP est-il stable et le port forwarding ?
- [ ] La table MAC montre-t-elle la MAC au bon endroit ?
- [ ] La passerelle est-elle up et la bonne ?
- [ ] Le routage et la route retour existent-ils ?
- [ ] DHCP/DNS/NTP/IPBX répondent-ils ?
- [ ] Les ACL, le NAT et le pare-feu autorisent-ils le flux ?
- [ ] La QoS et le PoE sont-ils dimensionnés ?
- [ ] Une capture confirme-t-elle le chemin réel ?

## 13. Sujets avancés

### QinQ (802.1ad)

QinQ empile deux tags : un tag externe de fournisseur (S-VLAN) et un tag
interne client (C-VLAN). Le client conserve ses VLAN, le fournisseur isole
chaque client avec un S-VLAN. Le TPID externe peut être `0x88a8`.

```text
Trame client        : [MAC][MAC][0x8100][C-VID 10][payload]
Trame QinQ          : [MAC][MAC][0x88a8][S-VID 100][0x8100][C-VID 10][payload]
```

Configuration Cisco simplifiée :

```text
interface GigabitEthernet0/1
 switchport mode dot1q-tunnel
 switchport access vlan 100
```

Avantages : isolation de clients, transport transparent de VLAN. Limites :
MTU, support matériel, complexité de dépannage, nombre de tags. Vérifiez que
les équipements intermédiaires acceptent les trames plus longues.

### VXLAN et EVPN

VXLAN encapsule des trames L2 dans UDP/IP et utilise un VNI de 24 bits. Il
étend un domaine L2 sur un underlay L3, ce qui facilite la mobilité des machines
virtuelles et l'extension entre sites. EVPN sert de plan de contrôle pour
apprendre les MAC/IP et éviter le flood excessif.

```text
Hôte A -- leaf1 -- underlay IP -- leaf2 -- Hôte B
             \---- VXLAN VNI 5010 ----/
```

VXLAN ne remplace pas une bonne conception VLAN au niveau de l'accès. Il
déplace la complexité vers l'overlay, le MTU, le contrôle plane et le
dépannage. Une MTU sous-dimensionnée ou un filtrage UDP 4789 casse l'overlay.

### MVRP, VTPv3 et automatisation

MVRP (Multiple VLAN Registration Protocol) propage l'enregistrement des VLAN
sur un domaine L2. VTPv3 ajoute la gestion des VLAN étendus, l'authentification
et le mode off. Les réseaux modernes utilisent souvent NETCONF/YANG, Ansible,
Terraform ou une plateforme d'intention pour configurer les VLAN de manière
idempotente. L'automatisation ne dispense pas de valider la base VLAN, les
trunks et la connectivité après chaque changement.

### SD-Access et fabric

Dans un fabric SD-Access, l'utilisateur est identifié, puis placé dans un
VRF/VN et éventuellement un SGT. Les VLAN d'accès sont locaux au bord et le
transport est un overlay. La segmentation devient une politique, mais les
bonnes pratiques L2 restent valables au bord : trunk, PoE, 802.1X, QoS,
contrôle des ports.

### Cloud et virtualisation

Chez un fournisseur cloud, le VLAN est souvent remplacé par un réseau virtuel,
un VPC ou un segment overlay. Les trunks 802.1Q existent encore sur les
hyperviseurs et les liaisons dedicated. Vérifiez les limites du provider :
nombre de VLAN, MTU, support des tags, filtrage, translation. Un VLAN ID
n'est pas nécessairement global dans le cloud ; il peut être local à un
hyperviseur ou à un tenant.

## 14. Exercices avec corrigé

### Exercice 1 — Broadcast et segmentation

Un switch possède 24 ports dans le VLAN 1. On crée le VLAN 10 et on place 12
ports dans le VLAN 10. Combien de domaines de broadcast ? Les ports du VLAN 1
voient-ils les broadcasts du VLAN 10 ?

**Corrigé :** deux domaines de broadcast (VLAN 1 et VLAN 10). Non, les ports
du VLAN 1 ne voient pas les broadcasts du VLAN 10, sauf si un routeur ou un
mécanisme de proxy les relaie. Un broadcast L2 reste confiné à son VLAN.

### Exercice 2 — Taille du tag

Une trame Ethernet de 1 518 octets sans FCS est taguée 802.1Q. Quelle est sa
taille ? La MTU IP change-t-elle ?

**Corrigé :** 1 522 octets sans FCS (4 octets de tag). La MTU IP reste 1 500
octets ; le tag est un en-tête L2 supplémentaire. Avec FCS, la trame physique
peut atteindre 1 526 octets.

### Exercice 3 — VID

Pourquoi ne peut-on pas utiliser 4 096 VLAN malgré un VID de 12 bits ?

**Corrigé :** le VID 0 et le VID 4095 sont réservés par le standard. Il reste
4 094 valeurs utilisables. Les plateformes et les modes VTP peuvent réduire
encore la plage.

### Exercice 4 — Trunk

Un trunk doit transporter les VLAN 10, 20 et 99, avec la native VLAN 999.
Écrivez la configuration Cisco.

**Corrigé :**

```text
interface GigabitEthernet0/24
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport nonegotiate
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99
```

### Exercice 5 — Native VLAN mismatch

Deux switches ont une native VLAN différente sur leur trunk. Décrivez le risque
et la correction.

**Corrigé :** les trames non taguées sont classées dans le VLAN natif local de
chaque switch. Le trafic peut fuiter d'un VLAN à l'autre, la gestion peut
devenir instable et une attaque par double tagging est facilitée. Corrigez en
alignant la native VLAN des deux côtés sur un VLAN dédié, inutilisé, et en
vérifiant `show interfaces trunk`.

### Exercice 6 — Linux

Créez une interface VLAN 10 sur `eth0`, adresse `10.10.10.254/24`. Donnez les
commandes iproute2.

**Corrigé :**

```bash
sudo ip link add link eth0 name eth0.10 type vlan id 10
sudo ip link set eth0.10 up
sudo ip addr add 10.10.10.254/24 dev eth0.10
ip -d link show eth0.10
```

### Exercice 7 — Bridge VLAN

Un bridge Linux doit avoir `eth0` en accès VLAN 10 non tagué et `eth1` en
trunk VLAN 10 et 20. Donnez les commandes.

**Corrigé :**

```bash
sudo ip link add name br0 type bridge
sudo ip link set br0 type bridge vlan_filtering 1
sudo ip link set eth0 master br0
sudo ip link set eth1 master br0
sudo ip link set br0 up
sudo ip link set eth0 up
sudo ip link set eth1 up
sudo bridge vlan add vid 10 dev eth0 pvid untagged
sudo bridge vlan add vid 10 dev eth1
sudo bridge vlan add vid 20 dev eth1
sudo bridge vlan add vid 10 dev br0 self
sudo bridge vlan add vid 20 dev br0 self
```

### Exercice 8 — SVI

Un switch L3 a les VLAN 10 et 20 et `ip routing` est activé, mais les clients
ne se joignent pas. Citez trois causes probables.

**Corrigé :** une SVI est shutdown ou down (aucun port actif), la passerelle
configurée sur les clients est incorrecte, une ACL bloque le flux, ou la route
retour manque. Vérifiez aussi que les ports sont dans le bon VLAN et que le
VLAN existe.

### Exercice 9 — DHCP

Les clients du VLAN 20 ne reçoivent pas d'adresse. Le serveur DHCP est dans le
VLAN 50. Que vérifiez-vous en priorité ?

**Corrigé :** la présence de `ip helper-address` sur la SVI 20, la route du
switch vers le serveur, la route retour du serveur vers `10.20.20.0/24`, le
pool DHCP, l'épuisement, les ACL et DHCP snooping. Une capture DORA confirme
si la requête atteint le serveur.

### Exercice 10 — PVLAN

Quelle est la différence entre un port isolated et un port community dans un
private VLAN ?

**Corrigé :** un port isolated ne parle qu'au port promiscuous (la passerelle),
pas aux autres isolated. Un port community parle aux membres de sa communauté
et au promiscuous, mais pas aux autres communautés ni aux isolated.

### Exercice 11 — VTP

Un switch de laboratoire configuré en VTP server avec un revision number élevé
est branché sur le réseau de production. Quel est le risque ?

**Corrigé :** il peut écraser la base VLAN du domaine avec sa propre base,
supprimer ou renommer des VLAN et couper la production. Utilisez VTP
transparent/off, un domaine et un mot de passe dédiés, et vérifiez le switch
avant de le brancher.

### Exercice 12 — QoS voix

Pourquoi la voix utilise-t-elle souvent PCP 5 et DSCP EF ? Que se passe-t-il
si un PC peut marquer ses trames en PCP 7 ?

**Corrigé :** PCP 5 et DSCP EF (46) indiquent un trafic voix à faible latence.
Si un PC peut marquer PCP 7, il peut se placer dans la file de contrôle et
affamer les flux légitimes. Il faut faire confiance au téléphone sur son port,
classifier le PC et appliquer une police ou une politique de QoS.

## 15. Aide-mémoire

### Commandes Cisco

| Besoin | Commande |
| --- | --- |
| Créer un VLAN | `vlan 10` puis `name DATA` |
| Voir les VLAN | `show vlan brief` |
| Voir un VLAN | `show vlan id 10` |
| Port access | `switchport mode access` |
| Assigner un VLAN | `switchport access vlan 10` |
| Port voix | `switchport voice vlan 20` |
| Trunk | `switchport mode trunk` |
| Encapsulation | `switchport trunk encapsulation dot1q` |
| Native VLAN | `switchport trunk native vlan 999` |
| Liste autorisée | `switchport trunk allowed vlan 10,20,99` |
| Trunk statique | `switchport nonegotiate` |
| Voir le trunk | `show interfaces trunk` |
| Voir le port | `show interfaces switchport` |
| Table MAC | `show mac address-table vlan 10` |
| STP | `show spanning-tree vlan 10` |
| SVI | `interface Vlan10` puis `ip address ...` |
| Routage L3 | `ip routing` |
| DHCP relay | `ip helper-address 10.20.50.10` |
| VTP transparent | `vtp mode transparent` |
| PoE | `show power inline` |
| QoS | `show mls qos interface` |

### Commandes Linux

| Besoin | Commande |
| --- | --- |
| Créer un VLAN | `ip link add link eth0 name eth0.10 type vlan id 10` |
| Activer | `ip link set eth0.10 up` |
| Adresse | `ip addr add 10.10.10.1/24 dev eth0.10` |
| Voir le VLAN | `ip -d link show eth0.10` |
| Créer un bridge | `ip link add br0 type bridge` |
| Filtrage VLAN | `ip link set br0 type bridge vlan_filtering 1` |
| Attacher un port | `ip link set eth0 master br0` |
| PVID | `bridge vlan add vid 10 dev eth0 pvid untagged` |
| Trunk | `bridge vlan add vid 20 dev eth1` |
| Voir les VLAN | `bridge vlan show` |
| Voir la FDB | `bridge fdb show` |
| Capture tag | `tcpdump -ni eth0 -e` |
| Namespace | `ip netns add h1` |
| veth | `ip link add h1-eth0 type veth peer name sw1` |
| Voir les routes | `ip route` |

### Règles de conception à retenir

- Un VLAN utilisateur = un sous-réseau = une passerelle, sauf exception
  documentée.
- Le VLAN 1 ne doit pas porter d'utilisateurs.
- La native VLAN doit être dédiée, identique aux deux extrémités et sans
  utilisateurs.
- Les trunks doivent avoir une liste autorisée explicite et `nonegotiate`.
- Le VLAN de management doit être filtré et accessible seulement aux
  administrateurs.
- Les VLAN inutilisés doivent être absents des trunks.
- La QoS voix doit être configurée de bout en bout, pas seulement sur le
  téléphone.
- Un VLAN n'est pas un pare-feu : utilisez des ACL ou un firewall pour les
  flux sensibles.
- Documentez chaque VLAN, chaque port trunk et chaque changement.
- Testez la connectivité de chaque VLAN après toute modification de trunk.

### Glossaire

| Terme | Définition |
| --- | --- |
| Access | Port qui appartient à un seul VLAN et émet sans tag |
| Trunk | Port qui transporte plusieurs VLAN avec tags |
| Native VLAN | VLAN dont les trames sortent sans tag sur un trunk |
| PVID | VLAN attribué aux trames non taguées reçues sur un port |
| VID | Identifiant de VLAN sur 12 bits |
| PCP/CoS | Priorité L2 sur 3 bits |
| DEI | Bit d'éligibilité au drop |
| DTP | Protocole de négociation de trunk Cisco |
| VTP | Protocole de synchronisation des VLAN Cisco |
| SVI | Interface virtuelle de VLAN sur un switch L3 |
| PVLAN | Private VLAN, isolation sur un même sous-réseau |
| QinQ | Empilement de deux tags 802.1Q |
| VXLAN | Encapsulation L2 dans UDP/IP avec VNI |
| EVPN | Plan de contrôle BGP pour les overlays L2/L3 |
| STP | Protocole de prévention des boucles L2 |
| MSTP | STP avec instances multiples |
| LLDP-MED | Extension LLDP pour la voix et les équipements terminaux |
| PoE | Alimentation électrique sur le câble Ethernet |
| DSCP | Priorité L3 sur 6 bits |
| EF | Expedited Forwarding, classe DSCP voix |
| SPAN | Port miroir Cisco pour la capture |
| MVRP | Enregistrement automatique des VLAN |
| MTU | Taille maximale de l'unité de transmission IP |

### Conclusion opérationnelle

Les VLAN sont simples à configurer et difficiles à exploiter sans discipline.
La différence entre un réseau qui fonctionne et un réseau fiable tient à des
détails : une native VLAN cohérente, une liste autorisée explicite, un VLAN
de management protégé, une QoS voix dimensionnée, une documentation à jour et
une méthode de dépannage qui collecte des preuves avant de changer la
configuration. Le meilleur test d'un plan VLAN n'est pas `show vlan brief` :
c'est un utilisateur qui atteint le bon service, avec la bonne politique, et
un ingénieur capable d'expliquer chaque tag sur le chemin.
