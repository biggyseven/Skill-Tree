# IPv4 — Niveau Débutant : comprendre, calculer et configurer l’adressage

> **Parcours :** Réseaux IP → IPv4  
> **Niveau :** Débutant  
> **Durée indicative :** 3 à 5 heures, réparties en plusieurs séances  
> **Prérequis :** connaître le rôle d’un ordinateur, d’un commutateur et d’un routeur ; savoir distinguer une adresse MAC d’une adresse IP à grands traits.  
> **Suite pédagogique :** ce cours pose les fondations nécessaires au cours `ipv4-intermediaire.md`, qui approfondira le subnetting, le VLSM, l’agrégation, le diagnostic et la planification d’un plan d’adressage.  
> **Environnement conseillé :** Cisco Packet Tracer, ou deux ordinateurs et un routeur/switch de laboratoire.


## 1. Objectifs d’apprentissage

À la fin du cours, tu dois pouvoir :

- expliquer le rôle d’IPv4 dans une communication réseau ;
- lire une adresse IPv4 et reconnaître ses quatre octets ;
- convertir une adresse entre notation décimale pointée et binaire ;
- distinguer adresse réseau, adresse d’hôte et adresse de broadcast ;
- expliquer le rôle d’un masque et d’un préfixe CIDR ;
- identifier les plages privées les plus courantes et quelques adresses spéciales ;
- calculer les caractéristiques d’un petit sous-réseau `/24`, `/25`, `/26` ou `/27` ;
- distinguer la communication dans le même sous-réseau de celle qui passe par une passerelle ;
- configurer une adresse IPv4 sur un poste et une interface de routeur Cisco ;
- utiliser `ping`, `ipconfig`, `ip route` et `show ip interface brief` pour vérifier une configuration ;
- suivre une méthode ordonnée pour résoudre un problème d’adressage simple.

## 2. Carte mentale du chapitre

```text
IPv4
├── Adresse : 32 bits / 4 octets
├── Préfixe ou masque : partie réseau + partie hôte
├── Sous-réseau
│   ├── Adresse réseau
│   ├── Adresses utilisables
│   └── Broadcast
├── Communication
│   ├── Même sous-réseau → livraison locale via couche 2
│   └── Autre sous-réseau → passerelle par défaut
├── Configuration
│   ├── Adresse statique
│   └── DHCP (attribution automatique, étudiée plus loin)
└── Vérification et dépannage
```

## 3. Qu’est-ce qu’IPv4 ?

IPv4 signifie *Internet Protocol version 4*. C’est un protocole de couche réseau qui permet d’adresser les interfaces et d’acheminer des paquets entre des réseaux IP. Une adresse IPv4 comporte **32 bits**, généralement écrits sous la forme de quatre nombres décimaux séparés par des points.

Exemple :

```text
192.168.10.25
```

Chaque nombre correspond à un **octet** de 8 bits. Il existe donc quatre octets, soit `4 × 8 = 32` bits.

```text
Décimal :    192       . 168       . 10        . 25
Binaire :    11000000  . 10101000  . 00001010  . 00011001
              octet 1     octet 2     octet 3     octet 4
```

IPv4 ne désigne pas un appareil physique à lui seul : l’adresse est configurée sur une interface réseau. Un ordinateur équipé d’Ethernet et de Wi-Fi peut posséder plusieurs adresses IP, une par interface ou contexte réseau.

### 3.1 À quoi sert une adresse IP ?

Une adresse IP aide à répondre à deux questions :

1. **À quel réseau logique appartient la destination ?**
2. **Quelle destination faut-il joindre à l’intérieur de ce réseau ou par quel routeur faut-il passer ?**

L’adresse IP est logique et peut changer. L’adresse MAC est utilisée pour la livraison sur un lien local Ethernet ou Wi-Fi. Les deux jouent des rôles différents et complémentaires.

### 3.2 IPv4 et encapsulation

Lorsqu’une application envoie des données, celles-ci sont encapsulées par les protocoles des couches inférieures. Au niveau IP, le paquet contient notamment une adresse source et une adresse de destination.

```text
┌─────────────────────────────────────────────┐
│ Trame Ethernet / Wi-Fi                      │
│  ┌───────────────────────────────────────┐  │
│  │ Paquet IPv4                           │  │
│  │ Source : 192.168.10.25                │  │
│  │ Destination : 192.168.20.50           │  │
│  │  ┌────────────────────────────────┐  │  │
│  │  │ Segment TCP / datagramme UDP   │  │  │
│  │  │ Données de l’application       │  │  │
│  │  └────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

La trame locale change à chaque saut routé, tandis que les adresses IP source et destination restent normalement les mêmes de bout en bout. Des mécanismes comme le NAT peuvent modifier ces adresses ; ils seront étudiés à un niveau ultérieur.

## 4. Lire les 32 bits : décimal et binaire

Un bit vaut `0` ou `1`. Un octet contient huit bits. Les positions d’un octet, de gauche à droite, représentent les poids suivants :

| Position | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Poids | 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |

Pour convertir un octet binaire en décimal, additionne les poids correspondant aux bits égaux à `1`.

Exemple :

```text
Binaire :  1  1  0  0  1  0  1  0
Poids   : 128 64 32 16  8  4  2  1
Calcul  : 128 + 64 + 8 + 2 = 202
Résultat: 202
```

Ainsi, `11001010` vaut `202`.

### 4.1 Convertir un nombre décimal en binaire

Méthode simple : compare le nombre aux poids 128, 64, 32, 16, 8, 4, 2 et 1. Si le poids peut être soustrait sans rendre le reste négatif, écris `1` et soustrais-le ; sinon écris `0`.

Exemple : convertir `25`.

- 25 est inférieur à 128 → `0`
- 25 est inférieur à 64 → `0`
- 25 est inférieur à 32 → `0`
- 25 contient 16 → `1`, reste 9
- 9 contient 8 → `1`, reste 1
- 1 ne contient pas 4 → `0`
- 1 ne contient pas 2 → `0`
- 1 contient 1 → `1`

Résultat : `00011001`.

### 4.2 Entraînement guidé

| Décimal | Binaire |
|---:|---|
| 10 | `00001010` |
| 25 | `00011001` |
| 100 | `01100100` |
| 128 | `10000000` |
| 192 | `11000000` |
| 255 | `11111111` |

Un octet IPv4 va de `0` à `255`, car huit bits permettent `2⁸ = 256` combinaisons.

## 5. Comprendre le masque et le préfixe

Une adresse IP seule ne suffit pas pour savoir quelle partie désigne le réseau. Il faut aussi un **masque de sous-réseau** ou un **préfixe CIDR**.

Exemple :

```text
Adresse : 192.168.10.25
Masque  : 255.255.255.0
Préfixe : /24
```

`/24` signifie que les 24 premiers bits appartiennent à la partie réseau. Les 8 bits restants identifient l’hôte dans le sous-réseau.

```text
192       . 168       . 10        . 25
11000000  . 10101000  . 00001010  . 00011001
<--------------- 24 bits réseau --------------><- 8 bits hôte ->
```

Le masque `255.255.255.0` en binaire est :

```text
11111111.11111111.11111111.00000000
```

Les `1` contigus au début représentent la partie réseau ; les `0` représentent la partie hôte. Dans les masques CIDR usuels, les bits à `1` doivent être contigus.

### 5.1 Correspondance des préfixes courants

| Préfixe | Masque décimal | Bits hôte | Taille totale du bloc |
|---:|---|---:|---:|
| `/8` | `255.0.0.0` | 24 | 16 777 216 adresses |
| `/16` | `255.255.0.0` | 16 | 65 536 adresses |
| `/24` | `255.255.255.0` | 8 | 256 adresses |
| `/25` | `255.255.255.128` | 7 | 128 adresses |
| `/26` | `255.255.255.192` | 6 | 64 adresses |
| `/27` | `255.255.255.224` | 5 | 32 adresses |
| `/28` | `255.255.255.240` | 4 | 16 adresses |
| `/30` | `255.255.255.252` | 2 | 4 adresses |

Pour un sous-réseau IPv4 ordinaire, on réserve généralement une adresse pour identifier le réseau et une pour le broadcast. Le nombre d’adresses hôtes utilisables est donc souvent `2ʰ − 2`, où `h` est le nombre de bits hôte. Cette règle ne s’applique pas de la même manière aux préfixes `/31` utilisés pour certains liens point-à-point, ni au `/32` qui désigne une seule adresse.

### 5.2 Pourquoi le masque est essentiel

Prenons `192.168.10.25`.

- Avec `/24`, elle appartient à `192.168.10.0/24`.
- Avec `/25`, elle appartient à `192.168.10.0/25`.
- Avec `/26`, elle appartient à `192.168.10.0/26`.

La même adresse peut donc appartenir à des sous-réseaux différents selon le préfixe.

## 6. Adresse réseau, hôtes et broadcast

Dans un sous-réseau classique, trois notions sont fondamentales :

- **Adresse réseau :** première adresse du bloc ; elle identifie le sous-réseau.
- **Adresse d’hôte utilisable :** adresse pouvant être attribuée à une interface.
- **Adresse de broadcast dirigé du sous-réseau :** dernière adresse du bloc ; elle cible tous les hôtes du sous-réseau lorsque ce type de broadcast est pris en charge.

### 6.1 Exemple complet en `/24`

Sous-réseau : `192.168.10.0/24`

| Élément | Valeur |
|---|---|
| Adresse réseau | `192.168.10.0` |
| Première adresse hôte | `192.168.10.1` |
| Dernière adresse hôte | `192.168.10.254` |
| Broadcast | `192.168.10.255` |
| Nombre d’adresses totales | 256 |
| Nombre d’adresses hôtes usuelles | 254 |

Une configuration d’hôte pourrait être :

```text
Adresse IP :       192.168.10.25
Masque :           255.255.255.0
Passerelle :       192.168.10.1
DNS :              192.168.10.10 (exemple)
```

La passerelle `.1` est une convention fréquente, pas une obligation. Toute adresse d’hôte utilisable du sous-réseau peut être choisie si le plan d’adressage le prévoit et si elle est configurée sur le routeur.

### 6.2 Exemple en `/26`

Sous-réseau : `192.168.10.64/26`

Un `/26` contient 64 adresses. Les blocs de ce préfixe commencent par incréments de 64 dans le dernier octet : `.0`, `.64`, `.128` et `.192`.

| Élément | Valeur |
|---|---|
| Adresse réseau | `192.168.10.64` |
| Première adresse hôte | `192.168.10.65` |
| Dernière adresse hôte | `192.168.10.126` |
| Broadcast | `192.168.10.127` |
| Total | 64 adresses |
| Hôtes utilisables usuels | 62 |

### 6.3 Repérer rapidement un bloc

Pour les masques qui coupent un octet, la taille du bloc se calcule ainsi :

`Taille du bloc = 256 − valeur du masque dans l’octet concerné`

Pour `/26`, l’octet du masque vaut `192`, donc `256 − 192 = 64`. Les réseaux sont `.0`, `.64`, `.128` et `.192`.

Pour `192.168.10.77/26`, le nombre `77` se situe entre `64` et `127`. Le réseau est donc `192.168.10.64`, le broadcast `192.168.10.127` et les hôtes usuels vont de `.65` à `.126`.

> **À retenir :** ne déduis pas le réseau uniquement à partir de l’adresse IP ou d’une habitude comme « les trois premiers octets sont le réseau ». Le préfixe détermine la frontière.

## 7. Adresses privées, publiques et spéciales

### 7.1 Plages IPv4 privées

Les plages privées définies pour l’usage interne sont les suivantes :

| Plage CIDR | Intervalle | Exemple d’utilisation |
|---|---|---|
| `10.0.0.0/8` | `10.0.0.0` à `10.255.255.255` | réseaux d’entreprise |
| `172.16.0.0/12` | `172.16.0.0` à `172.31.255.255` | réseaux internes |
| `192.168.0.0/16` | `192.168.0.0` à `192.168.255.255` | LAN domestiques et petits bureaux |

Une adresse privée n’est pas directement routable sur l’Internet public. Pour accéder à Internet, un réseau privé utilise souvent un routeur avec NAT, un proxy ou une autre architecture de sortie. Le NAT n’est pas la même chose que l’adressage privé : il s’agit d’un mécanisme distinct.

Attention : toute adresse commençant par `172.` n’est pas privée ; seule la plage `172.16.0.0` à `172.31.255.255` l’est.

### 7.2 Adresses particulières à reconnaître

| Adresse / plage | Signification |
|---|---|
| `0.0.0.0` | adresse non spécifiée dans certains contextes ; aussi utilisée comme destination de route par défaut `0.0.0.0/0` |
| `127.0.0.0/8` | loopback ; `127.0.0.1` pointe vers la machine locale |
| `169.254.0.0/16` | adressage link-local IPv4, souvent choisi automatiquement quand aucun bail DHCP utilisable n’est obtenu |
| `255.255.255.255` | broadcast limité sur le lien local |
| `224.0.0.0/4` | plage multicast IPv4 |
| `100.64.0.0/10` | espace partagé utilisé notamment par certains opérateurs pour le CGNAT ; ce n’est pas une plage privée RFC 1918 |

Une adresse `169.254.x.x` sur un PC Windows est un indice possible de problème DHCP, mais ce n’est pas à elle seule une preuve de panne : il faut examiner le contexte et la configuration.

## 8. Comment deux hôtes communiquent-ils ?

Le préfixe permet à l’hôte de décider si la destination est locale ou distante. Sur un réseau Ethernet, l’hôte utilise typiquement ARP pour découvrir l’adresse MAC correspondant à une IPv4 locale.

### 8.1 Deux hôtes dans le même sous-réseau

```text
PC-A                                      PC-B
192.168.10.25/24                          192.168.10.80/24
MAC-A                                     MAC-B
   |                                          |
   +---------------- Switch ------------------+
              même sous-réseau
```

PC-A calcule que `192.168.10.80` appartient à son sous-réseau. Il résout l’adresse MAC de PC-B via ARP, puis envoie une trame Ethernet directement vers cette MAC. Un routeur n’est normalement pas nécessaire pour ce trafic local.

### 8.2 Deux hôtes dans des sous-réseaux différents

```text
PC-A                  Routeur                  PC-B
192.168.10.25/24      G0/0: 192.168.10.1       192.168.20.50/24
Passerelle .1         G0/1: 192.168.20.1       Passerelle .1
   |                       |                         |
   +------ LAN A ----------+---------- LAN B --------+
```

PC-A compare la destination `192.168.20.50` à son sous-réseau `192.168.10.0/24`. La destination est distante. PC-A envoie donc la trame à la MAC de sa passerelle `192.168.10.1`, tout en gardant `192.168.20.50` comme destination IP du paquet. Le routeur consulte sa table de routage et transmet le paquet sur le réseau de destination.

### 8.3 Rôle de la passerelle par défaut

La passerelle est l’adresse de l’interface du routeur (ou d’un équipement de couche 3) à laquelle l’hôte remet le trafic destiné à des réseaux non locaux. Elle doit être joignable depuis le sous-réseau de l’hôte.

Erreurs fréquentes :

- configurer une passerelle dans un autre sous-réseau ;
- configurer la passerelle d’un autre VLAN ;
- oublier la passerelle alors que l’on attend une communication distante ;
- croire qu’une passerelle est nécessaire pour que deux hôtes du même sous-réseau communiquent localement.

## 9. Configuration IPv4 sur un poste

### 9.1 Configuration statique

Une configuration statique est saisie manuellement. Elle est utile pour les interfaces d’infrastructure, les serveurs de laboratoire et les exercices, mais demande une gestion rigoureuse pour éviter les doublons.

Exemple de plan d’adressage :

| Équipement | Adresse | Masque | Passerelle |
|---|---|---|---|
| Routeur LAN | `192.168.10.1` | `/24` | — |
| PC-A | `192.168.10.25` | `/24` | `192.168.10.1` |
| PC-B | `192.168.10.80` | `/24` | `192.168.10.1` |
| Serveur de test | `192.168.10.10` | `/24` | `192.168.10.1` |

Les adresses doivent être uniques sur le même réseau. La plage d’adresses attribuées aux postes doit être coordonnée avec le DHCP et les réservations.

### 9.2 Windows : commandes de vérification

Dans l’invite de commandes ou PowerShell :

```powershell
ipconfig
ipconfig /all
ping 192.168.10.1
arp -a
route print
```

- `ipconfig` affiche les paramètres IPv4 principaux.
- `ipconfig /all` affiche davantage d’informations, notamment DHCP et DNS.
- `ping` teste la joignabilité IP, sous réserve que les pare-feu autorisent l’ICMP.
- `arp -a` affiche le cache ARP local.
- `route print` affiche les routes connues de Windows.

Pour renouveler une configuration DHCP, on utilise souvent :

```powershell
ipconfig /release
ipconfig /renew
```

Ne lance ces commandes que si l’interface utilise DHCP et que tu comprends qu’elles peuvent interrompre temporairement la connectivité. Elles ne corrigent pas une panne de serveur DHCP ou une mauvaise configuration du réseau.

### 9.3 Linux : commandes équivalentes

```bash
ip -br address
ip route
ip neigh
ping -c 4 192.168.10.1
```

La commande `ip` est l’outil courant pour examiner les interfaces, les routes et les voisins. La disponibilité de `ping` et ses options peuvent varier légèrement selon la distribution.

## 10. Configuration IPv4 sur un routeur Cisco IOS

Exemple : interface GigabitEthernet0/0 connectée au LAN `192.168.10.0/24`.

```text
enable
configure terminal
interface gigabitEthernet0/0
 description LAN-UTILISATEURS
 ip address 192.168.10.1 255.255.255.0
 no shutdown
end
show ip interface brief
show running-config interface gigabitEthernet0/0
```

Points importants :

- `ip address` attribue l’adresse et le masque à l’interface.
- `no shutdown` active administrativement l’interface.
- `show ip interface brief` donne un résumé de l’état des interfaces.
- Une interface peut être `up/down` si le protocole de ligne ne fonctionne pas, ou `administratively down` si elle est arrêtée par configuration.

La syntaxe d’interface et les fonctions disponibles dépendent de la plateforme et de la version IOS/IOS XE. Dans Packet Tracer, les noms d’interfaces varient selon le modèle choisi.

### 10.1 Vérifier la configuration

```text
show ip interface brief
show running-config
show interfaces gigabitEthernet0/0
show ip route
ping 192.168.10.25
```

La commande `show ip route` permet de vérifier les réseaux directement connectés. Sur un routeur ne possédant que les deux interfaces de laboratoire, les réseaux connectés peuvent apparaître automatiquement lorsque les interfaces sont adressées et actives.

## 11. Laboratoire 1 — Deux PC dans le même sous-réseau

**Objectif :** prouver qu’un adressage cohérent permet la communication locale sans routeur.

### Topologie

```text
PC-A ---------------- Switch ---------------- PC-B
192.168.10.10/24                          192.168.10.20/24
```

### Étapes

1. Ajoute un commutateur et deux PC dans Packet Tracer.
2. Relie chaque PC au switch avec un câble cuivre droit (ou utilise l’auto-connexion de Packet Tracer).
3. Configure PC-A avec `192.168.10.10`, masque `255.255.255.0`.
4. Configure PC-B avec `192.168.10.20`, masque `255.255.255.0`.
5. Laisse la passerelle vide : elle n’est pas nécessaire pour ce test local.
6. Depuis PC-A, exécute `ping 192.168.10.20`.
7. Observe la table ARP si l’outil ou le système simulé le permet.

### Résultat attendu

Après la phase initiale de résolution ARP, les réponses ICMP doivent arriver. Si le premier ping échoue mais les suivants réussissent, la résolution ARP initiale peut expliquer le délai. Ce comportement dépend toutefois de l’outil et de son modèle de simulation.

### Questions d’analyse

- Pourquoi les deux PC sont-ils dans le même sous-réseau ?
- Que se passe-t-il si PC-B est configuré en `192.168.11.20/24` ?
- La passerelle est-elle nécessaire pour ce ping ? Pourquoi ?
- Quel problème apparaît si PC-B reçoit exactement l’adresse `192.168.10.10` ?

## 12. Laboratoire 2 — Deux réseaux reliés par un routeur

**Objectif :** comprendre le rôle de la passerelle et des interfaces de couche 3.

### Plan d’adressage

| Équipement / interface | Adresse IPv4 | Masque |
|---|---|---|
| PC-A | `192.168.10.10` | `255.255.255.0` |
| R1 G0/0 | `192.168.10.1` | `255.255.255.0` |
| R1 G0/1 | `192.168.20.1` | `255.255.255.0` |
| PC-B | `192.168.20.10` | `255.255.255.0` |

Passerelle de PC-A : `192.168.10.1`. Passerelle de PC-B : `192.168.20.1`.

### Configuration indicative de R1

```text
enable
configure terminal
interface gigabitEthernet0/0
 description LAN-A
 ip address 192.168.10.1 255.255.255.0
 no shutdown
exit
interface gigabitEthernet0/1
 description LAN-B
 ip address 192.168.20.1 255.255.255.0
 no shutdown
end
show ip interface brief
show ip route
```

### Vérifications dans l’ordre

1. Depuis PC-A, ping `192.168.10.1`.
2. Depuis PC-B, ping `192.168.20.1`.
3. Vérifie que les deux interfaces du routeur sont `up/up`.
4. Depuis PC-A, ping `192.168.20.10`.
5. Si le ping échoue, vérifie l’adresse, le masque, la passerelle, les liens physiques et l’état des interfaces.

Le routage entre réseaux directement connectés ne nécessite pas l’ajout de routes statiques dans cet exemple. En revanche, le retour du trafic doit également disposer d’un chemin valide.

## 13. Méthode de dépannage : du plus simple au plus complexe

Ne modifie pas plusieurs paramètres au hasard. Suis une séquence et note le résultat de chaque test.

```text
Le ping échoue
      |
      v
1. Vérifier le lien et l'interface
      |
      v
2. Vérifier l'adresse et le masque
      |
      v
3. La destination est-elle locale ?
      | oui                      | non
      v                          v
4. Vérifier ARP              4. Vérifier la passerelle
      |                          |
      v                          v
5. Vérifier le VLAN          5. Vérifier les routes
      |                          |
      +------------+-------------+
                   v
        6. Vérifier pare-feu / ICMP
                   |
                   v
        7. Refaire le test et noter le résultat
```

### 13.1 Symptômes fréquents

| Symptôme | Causes possibles | Vérifications initiales |
|---|---|---|
| `169.254.x.x` sur Windows | bail DHCP absent, serveur injoignable, mauvais VLAN | `ipconfig /all`, connectivité locale |
| PC-A ne ping pas la passerelle | mauvais masque/IP, VLAN erroné, lien coupé, interface routeur arrêtée | adresse, switchport, `show ip interface brief` |
| Les hôtes locaux communiquent, pas Internet | passerelle, route par défaut, NAT, DNS ou panne amont | ping passerelle, `route print`, tests par IP et par nom |
| Ping par IP réussi, nom impossible | problème DNS probable | paramètres DNS, résolution de nom |
| Hôte inaccessible malgré même préfixe apparent | masque incohérent, doublon IP, isolation de couche 2 ou pare-feu | comparaison des configurations, ARP, VLAN |
| Adresse en double | adresse statique réutilisée ou pool DHCP mal planifié | table DHCP, ARP, inventaire IP |

Un ping qui échoue ne prouve pas automatiquement qu’un hôte est hors service : l’ICMP peut être filtré. Utilise plusieurs indices plutôt qu’un seul test.

### 13.2 Procédure d’analyse d’un cas

Exemple : PC-A est configuré `192.168.10.25/24`, passerelle `192.168.10.1`. Il ne peut pas joindre `192.168.20.50`.

1. Vérifie d’abord que PC-A peut joindre `192.168.10.1`.
2. Confirme que la passerelle est dans le même sous-réseau local.
3. Vérifie que le routeur possède une interface ou une route vers `192.168.20.0/24`.
4. Vérifie la configuration IP et la passerelle de l’hôte distant.
5. Vérifie le chemin retour et les politiques de filtrage.
6. Documente les résultats et ne change qu’un paramètre à la fois.

## 14. Erreurs de débutant à éviter

1. **Confondre adresse réseau et adresse hôte.** `192.168.10.0/24` identifie le réseau, pas un PC ordinaire.
2. **Oublier le masque.** `192.168.10.10/24` et `192.168.10.10/26` n’ont pas la même interprétation.
3. **Croire que toute adresse privée commence par `192.168`.** Les plages `10/8` et `172.16/12` sont aussi privées.
4. **Attribuer la même adresse à deux interfaces dans le même domaine de routage.** Cela provoque des conflits.
5. **Configurer une passerelle qui n’est pas joignable localement.**
6. **Croire que le DNS fait le routage.** Le DNS traduit des noms en données telles que des adresses ; il ne remplace pas la table de routage.
7. **Croire qu’un ping est un test complet du service.** Il vérifie l’ICMP, pas nécessairement l’application visée.
8. **Modifier simultanément IP, masque, VLAN et passerelle.** Cela empêche d’identifier la cause réelle.

## 15. Exercices d’application

Essaie de répondre sans regarder le corrigé. Écris les calculs pour les questions de sous-réseau.

### Exercice 1 — Anatomie d’une adresse

Pour `10.20.30.40`, indique le nombre d’octets, le nombre total de bits et la valeur maximale possible d’un octet.

### Exercice 2 — Conversion

Convertis `192.168.1.10` en binaire octet par octet.

### Exercice 3 — Masque

Quel est le masque décimal de `/26` ? Combien d’adresses totales et combien d’adresses hôtes usuelles contient ce bloc ?

### Exercice 4 — Adresse réseau

Pour `192.168.5.77/26`, trouve l’adresse réseau, le broadcast et la plage d’hôtes utilisables.

### Exercice 5 — Adresse privée

Parmi les adresses suivantes, lesquelles appartiennent à une plage privée RFC 1918 ?

- `10.5.4.3`
- `172.20.1.8`
- `172.40.1.8`
- `192.168.200.2`
- `8.8.8.8`

### Exercice 6 — Passerelle

PC-A a `192.168.10.25/24` et veut joindre `192.168.20.50`. Doit-il envoyer la trame directement à la MAC de PC-B ou à la MAC de sa passerelle ? Explique.

### Exercice 7 — Diagnostic Windows

`ipconfig /all` indique `169.254.12.7` et aucune passerelle par défaut. Donne deux causes plausibles et deux vérifications utiles.

### Exercice 8 — Routeur Cisco

Écris les commandes nécessaires pour configurer `192.168.30.1/24` sur `GigabitEthernet0/0` et activer l’interface.

### Exercice 9 — Même sous-réseau ?

PC-A : `192.168.1.60/26`  
PC-B : `192.168.1.100/26`

Sont-ils dans le même sous-réseau ? Justifie en trouvant les deux réseaux.

### Exercice 10 — Méthode

Un PC peut pinguer sa passerelle mais ne peut pas accéder à un site web par son nom. Quels tests distingueront une panne DNS d’une panne de routage ou d’accès Internet ?


## 16. Corrigés détaillés

### Corrigé 1

Une adresse IPv4 contient quatre octets de 8 bits, soit 32 bits. La valeur maximale d’un octet est `255`, car les huit bits à `1` représentent `128+64+32+16+8+4+2+1=255`.

### Corrigé 2

```text
192 = 11000000
168 = 10101000
1   = 00000001
10  = 00001010

192.168.1.10
= 11000000.10101000.00000001.00001010
```

### Corrigé 3

`/26` correspond à `255.255.255.192`. Il reste 6 bits hôte : `2⁶ = 64` adresses au total. Pour un sous-réseau ordinaire, 2 adresses sont réservées, soit 62 adresses hôtes utilisables.

### Corrigé 4

`/26` a une taille de bloc de `256 − 192 = 64`. Les plages sont `.0–.63`, `.64–.127`, `.128–.191` et `.192–.255`. Le dernier octet `77` appartient au bloc `.64–.127`.

- Réseau : `192.168.5.64`
- Premier hôte : `192.168.5.65`
- Dernier hôte : `192.168.5.126`
- Broadcast : `192.168.5.127`

### Corrigé 5

Privées : `10.5.4.3`, `172.20.1.8` et `192.168.200.2`.  
`172.40.1.8` est en dehors de `172.16.0.0/12`, et `8.8.8.8` n’appartient pas aux plages privées RFC 1918.

### Corrigé 6

La destination `192.168.20.50` n’appartient pas à `192.168.10.0/24`. PC-A remet donc la trame à la MAC de sa passerelle. Le paquet IP conserve comme destination `192.168.20.50` jusqu’à ce qu’un mécanisme tel que NAT modifie éventuellement les adresses.

### Corrigé 7

Causes possibles : serveur DHCP indisponible, port/VLAN incorrect, lien réseau défaillant, ou serveur DHCP inaccessible. Vérifications : `ipconfig /all`, état du lien, VLAN du port, puis renouvellement DHCP si approprié. Une adresse link-local ne prouve pas à elle seule la cause exacte.

### Corrigé 8

```text
enable
configure terminal
interface gigabitEthernet0/0
 ip address 192.168.30.1 255.255.255.0
 no shutdown
end
show ip interface brief
```

### Corrigé 9

`/26` utilise des blocs de 64 adresses.

- `192.168.1.60` appartient à `192.168.1.0/26` (adresses `.0–.63`).
- `192.168.1.100` appartient à `192.168.1.64/26` (adresses `.64–.127`).

Ils ne sont donc pas dans le même sous-réseau. Ils ont besoin d’un équipement de couche 3 pour communiquer, ainsi que de routes et de passerelles correctement configurées.

### Corrigé 10

1. Pinguer la passerelle confirme une partie de la connectivité locale.
2. Tester une adresse IP externe connue peut aider à distinguer résolution DNS et accès IP, si le filtrage ICMP le permet.
3. Utiliser `nslookup nom-du-site` ou un outil DNS équivalent pour tester la résolution.
4. Vérifier les DNS configurés, la route par défaut, le pare-feu et la connectivité amont.
5. Si l’adresse IP fonctionne mais le nom ne se résout pas, DNS devient une hypothèse forte ; cela reste à confirmer avec les résultats de résolution.

## 17. Évaluation finale

Avant de passer au niveau Intermédiaire, assure-toi de pouvoir expliquer sans aide :

- [ ] pourquoi IPv4 utilise 32 bits ;
- [ ] comment lire et convertir un octet ;
- [ ] comment le masque sépare les bits réseau et hôte ;
- [ ] comment calculer réseau, broadcast et plage d’hôtes pour un `/24`, `/25` et `/26` ;
- [ ] quelles plages sont privées ;
- [ ] quand une passerelle est nécessaire ;
- [ ] comment configurer une interface IPv4 Cisco ;
- [ ] comment vérifier une configuration sous Windows, Linux et IOS ;
- [ ] comment suivre un dépannage ordonné plutôt que modifier les paramètres au hasard.

**Critère de progression suggéré :** obtenir au moins 8/10 aux exercices, réussir les deux laboratoires et être capable de justifier chaque étape de calcul. Si le calcul de sous-réseau reste difficile, refais les sections 5 et 6 avant de commencer le niveau suivant.

## 18. Ce que le niveau Intermédiaire ajoutera

Le prochain fichier, `ipv4-intermediaire.md`, devra s’appuyer sur ces acquis et les approfondir sans refaire toute l’introduction. Il abordera notamment :

- le subnetting méthodique sur les quatre octets ;
- le calcul rapide de plages et de blocs ;
- le VLSM pour attribuer des sous-réseaux de tailles différentes ;
- la conception d’un plan d’adressage à partir des besoins ;
- les routes résumées et les limites de l’agrégation ;
- le dépannage par analyse des masques, des routes et des captures ;
- des laboratoires plus complexes combinant plusieurs VLAN et routeurs.

## 19. Références techniques

- RFC 791 — *Internet Protocol*: https://www.rfc-editor.org/rfc/rfc791
- RFC 1918 — *Address Allocation for Private Internets*: https://www.rfc-editor.org/rfc/rfc1918
- RFC 4632 — *Classless Inter-domain Routing (CIDR)*: https://www.rfc-editor.org/rfc/rfc4632
- RFC 3927 — *Dynamic Configuration of IPv4 Link-Local Addresses*: https://www.rfc-editor.org/rfc/rfc3927
- Documentation Cisco IOS IP Addressing Services: https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-ip-addressing-services/tsd-products-support-series-home.html


## Résumé à mémoriser

1. IPv4 = 32 bits = 4 octets.
2. Le préfixe indique combien de bits sont réservés au réseau.
3. Pour un sous-réseau ordinaire, réseau et broadcast ne sont pas attribués aux hôtes.
4. Les plages privées RFC 1918 sont `10.0.0.0/8`, `172.16.0.0/12` et `192.168.0.0/16`.
5. Un hôte envoie le trafic local directement sur le lien ; le trafic distant est envoyé à sa passerelle.
6. Une configuration correcte exige une adresse, un masque cohérent, une passerelle adaptée si nécessaire et un réseau de couche 2 fonctionnel.
7. Le dépannage commence par les vérifications simples et progresse étape par étape.
