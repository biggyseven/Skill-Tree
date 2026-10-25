# Cahier de laboratoires réseau — `labs-nets.md`

> **Public visé :** étudiants et administrateurs réseau, du niveau débutant au niveau expert.  
> **Progression :** fondamentaux → commutation → routage → services réseau → sécurité → dépannage → automatisation → architectures avancées.  
> **Méthode :** chaque laboratoire comporte un objectif, un plan d'adressage, une procédure, des vérifications, des pannes à provoquer et un livrable.


## 0. Comment utiliser ce cahier

Ce fichier est un **cahier de travaux pratiques**, pas seulement une collection de commandes. Pour chaque exercice, travaille dans cet ordre :

1. Lis le scénario et écris ce que tu t'attends à observer.
2. Construis la topologie et note l'adressage avant de configurer.
3. Applique la configuration par petites étapes.
4. Vérifie chaque étape avec une commande d'état ou un test fonctionnel.
5. Provoque une panne volontaire, puis dépanne à partir des faits.
6. Termine par une courte fiche indiquant ce qui fonctionne, ce qui a échoué et pourquoi.

Les adresses des laboratoires sont des plages de documentation réservées à l'exemple. Ne les réutilise pas aveuglément dans un réseau d'entreprise.

### Choisir son environnement

| Environnement | Usage idéal | Limites à connaître |
|---|---|---|
| Cisco Packet Tracer | VLAN, trunks, STP, EtherChannel, routage, ACL, NAT, DHCP et OSPF de base | Simulation ; certaines commandes et fonctions diffèrent du matériel réel |
| GNS3 ou Cisco Modeling Labs | Maquettes plus proches des équipements réels et interconnexion de plusieurs OS réseau | Les images et licences doivent être obtenues légalement ; consommation de ressources plus élevée |
| Linux avec `iproute2`, `tcpdump`, `nftables` | Réseaux virtuels légers, routage Linux, capture, filtrage et tests reproductibles | Nécessite un terminal Linux et des privilèges administrateur |
| FRRouting (FRR) | OSPF, BGP et autres protocoles sur Linux ou dans des conteneurs | Les fonctions dépendent de la version et de la plateforme ; vérifier la documentation |
| Wireshark | Analyse détaillée des protocoles et validation des hypothèses | Les captures peuvent contenir des données sensibles ; capturer uniquement le trafic autorisé |
| Containerlab | Déploiement reproductible de topologies de conteneurs et laboratoires avancés | Nécessite des images de nœuds compatibles et une préparation supplémentaire |

### Précautions de sécurité

- Exécute les manipulations avec des droits élevés uniquement dans une machine de laboratoire ou une VM dédiée.
- Ne colle jamais une configuration de TP directement sur un routeur de production.
- Avant un `reload`, une modification d'ACL, un changement d'adressage ou une mise à niveau, vérifie la console et le plan de retour arrière.
- N'analyse que les captures et réseaux pour lesquels tu as une autorisation.
- N'inscris pas de vrai mot de passe, jeton API, clé privée ou secret de production dans les fichiers du cahier.
- Pour les laboratoires Linux, les commandes de nettoyage suppriment les interfaces et espaces de noms créés pour le TP. Vérifie les noms avant de les lancer.

### Livrable standard pour chaque laboratoire

Crée un dossier par TP, puis conserve :

- `objectif.md` : objectif et critères de réussite ;
- `topologie.txt` : nœuds, liens, interfaces et adresses ;
- `configuration.txt` : configuration appliquée, sans secret ;
- `preuves.txt` : sorties des commandes et résultats des tests ;
- `analyse.md` : incident provoqué, cause, correction et prévention.


# PARTIE I — Fondamentaux et commutation

## TP 1 — Adressage IPv4, sous-réseaux et connectivité de base

**Niveau :** débutant  
**Environnement :** Packet Tracer, GNS3 ou deux machines virtuelles reliées à un même réseau virtuel.

### Objectifs

- Distinguer adresse IP, masque, adresse réseau, adresse de diffusion et passerelle.
- Vérifier la connectivité avant d'ajouter des fonctions plus avancées.
- Reconnaître la différence entre une panne locale et une panne de routage.

### Topologie

Deux postes reliés au même commutateur :

```text
PC-A ---------------- SW1 ---------------- PC-B
192.0.2.10/24                            192.0.2.20/24
```

Aucun routeur n'est nécessaire : les deux postes sont dans le même sous-réseau.

### Procédure

1. Configure PC-A avec `192.0.2.10/24` et PC-B avec `192.0.2.20/24`.
2. Laisse la passerelle vide, car aucun réseau distant n'est utilisé dans ce premier test.
3. Depuis PC-A, lance un ping vers `192.0.2.20`.
4. Affiche la table ARP ou le cache des voisins sur les postes.
5. Observe les adresses MAC apprises par SW1 dans sa table de commutation.
6. Change temporairement le masque de PC-B en `/25`, puis répète le test et explique le résultat.

Sur un poste Linux, les commandes de diagnostic courantes sont :

```bash
ip address show
ip route show
ip neigh show
ping -c 4 192.0.2.20
```

Sur Windows, les commandes équivalentes comprennent `ipconfig /all`, `route print`, `arp -a` et `ping`.

### Résultat attendu

Avec des adresses et un masque cohérents, les postes communiquent directement. La première communication peut nécessiter une résolution ARP. Après modification du masque, les postes peuvent prendre des décisions différentes quant au caractère local ou distant de l'adresse de destination.

### Défi de dépannage

Modifie une seule valeur à la fois : adresse du poste, masque, état du port, puis VLAN du port dans les TP suivants. Pour chaque essai, écris l'indice qui t'a permis d'isoler la cause.

**À rendre :** le calcul du sous-réseau, la table d'adressage et une courte explication d'ARP.


## TP 2 — VLAN, ports access et trunk 802.1Q

**Niveau :** débutant → intermédiaire  
**Environnement :** Cisco Packet Tracer ou commutateurs compatibles.

### Objectifs

- Séparer deux groupes logiques sur une même infrastructure physique.
- Comprendre la différence entre un port access et un trunk.
- Vérifier que les VLAN ne communiquent pas automatiquement entre eux.

### Topologie et adressage

- PC-A, VLAN 10, `192.168.10.10/24` ;
- PC-B, VLAN 10, `192.168.10.11/24` ;
- PC-C, VLAN 20, `192.168.20.10/24` ;
- PC-D, VLAN 20, `192.168.20.11/24` ;
- S1 et S2 reliés par un trunk.

### Configuration type sur les deux commutateurs

Adapte les numéros de ports à la topologie exacte. Sur certains modèles, les interfaces peuvent s'appeler `Fa0/1` plutôt que `Gi0/1`.

```text
enable
configure terminal
vlan 10
 name UTILISATEURS
vlan 20
 name SERVEURS
!
interface GigabitEthernet0/1
 description TRUNK_VERS_AUTRE_SWITCH
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 no shutdown
!
end
show vlan brief
show interfaces trunk
```

Sur les ports reliés aux postes, configure le mode access et le VLAN approprié. Exemple pour un poste du VLAN 10 :

```text
configure terminal
interface FastEthernet0/2
 description PC-A_VLAN10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
end
```

`spanning-tree portfast` ne doit être appliqué qu'à un port d'extrémité, jamais à un lien entre commutateurs.

### Vérifications

- PC-A doit joindre PC-B.
- PC-C doit joindre PC-D.
- PC-A ne doit pas joindre PC-C sans équipement de couche 3.
- `show vlan brief` doit associer chaque port access au bon VLAN.
- `show interfaces trunk` doit confirmer le trunk et la liste des VLAN autorisés.

### Pannes à provoquer

1. Retire le VLAN 20 de la liste des VLAN autorisés sur le trunk.
2. Place PC-C dans le mauvais VLAN.
3. Transforme le lien entre S1 et S2 en port access.
4. Vérifie les résultats après chaque changement et restaure la configuration.

**À rendre :** tableau de ports, preuve des pings et diagnostic de chaque panne.


## TP 3 — Routage inter-VLAN avec router-on-a-stick

**Niveau :** intermédiaire  
**Environnement :** Packet Tracer ou équipement compatible.

### Objectifs

- Router entre plusieurs VLAN sans installer une interface physique par VLAN.
- Comprendre les sous-interfaces et l'encapsulation 802.1Q.
- Distinguer la connectivité de couche 2 de la connectivité de couche 3.

### Plan IP

| VLAN | Usage | Sous-réseau | Passerelle |
|---|---|---|---|
| 10 | Utilisateurs | `192.168.10.0/24` | `192.168.10.1` |
| 20 | Serveurs | `192.168.20.0/24` | `192.168.20.1` |
| 99 | Administration | `192.168.99.0/24` | `192.168.99.1` |

### Configuration type du commutateur

Le port `Gi0/1` relie le commutateur au routeur. Ajuste le nom d'interface selon le modèle.

```text
configure terminal
vlan 10
 name UTILISATEURS
vlan 20
 name SERVEURS
vlan 99
 name ADMIN
!
interface GigabitEthernet0/1
 description TRUNK_VERS_ROUTEUR
 switchport mode trunk
 switchport trunk allowed vlan 10,20,99
 no shutdown
end
```

### Configuration type du routeur

```text
enable
configure terminal
interface GigabitEthernet0/0
 no ip address
 no shutdown
!
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
!
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
!
interface GigabitEthernet0/0.99
 encapsulation dot1Q 99
 ip address 192.168.99.1 255.255.255.0
end
show ip interface brief
show running-config interface GigabitEthernet0/0.10
```

Configure ensuite chaque poste avec une adresse libre de son sous-réseau et la passerelle du VLAN correspondant.

### Tests et validation

1. Vérifie d'abord que deux postes du même VLAN communiquent.
2. Vérifie ensuite le ping vers la passerelle locale.
3. Teste un échange entre VLAN 10 et VLAN 20.
4. Affiche la table de routage du routeur.
5. Désactive une sous-interface puis observe précisément quels flux échouent.

### Questions

- Pourquoi le trunk est-il nécessaire entre le commutateur et le routeur ?
- À quoi sert `encapsulation dot1Q 20` sur la sous-interface VLAN 20 ?
- Pourquoi un poste d'un VLAN ne peut-il pas utiliser directement la passerelle d'un autre VLAN ?

**À rendre :** configuration des deux équipements, table de routage et tests positifs/négatifs.


## TP 4 — STP, boucle de couche 2 et EtherChannel

**Niveau :** intermédiaire  
**Environnement :** Packet Tracer ou trois commutateurs compatibles.

### Objectifs

- Comprendre le risque d'une boucle Ethernet.
- Observer le rôle de Spanning Tree Protocol (STP).
- Comprendre comment EtherChannel regroupe des liens physiques compatibles.

### Scénario

Construis trois commutateurs S1, S2 et S3 reliés en triangle. Chaque commutateur dessert au moins un poste. Dans un réseau Ethernet commuté, une boucle de couche 2 peut créer des tempêtes de broadcast et une instabilité de la table MAC. STP calcule une topologie logique sans boucle en plaçant certains ports dans un état qui ne transfère pas le trafic utilisateur.

### Étapes

1. Vérifie l'état STP et identifie le root bridge.
2. Consulte les rôles et états des ports.
3. Déconnecte un lien actif et vérifie la convergence.
4. Modifie la priorité STP sur un commutateur de laboratoire afin de contrôler le root bridge.
5. Si deux commutateurs disposent de deux liens parallèles, construis un EtherChannel avec une méthode compatible aux deux extrémités.
6. Vérifie que les interfaces physiques ont les mêmes paramètres essentiels : mode, VLAN autorisés, débit et configuration de couche 2.

Commandes Cisco IOS de vérification courantes :

```text
show spanning-tree
show spanning-tree vlan 10
show etherchannel summary
show interfaces port-channel 1
```

Exemple de principe de configuration LACP, à adapter aux ports du labo :

```text
interface range GigabitEthernet0/1-2
 channel-group 1 mode active
!
interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```

La configuration doit être symétrique et compatible aux deux extrémités. Ne copie pas cet exemple sans vérifier les noms d'interface et les capacités du modèle simulé.

### Tests

- Vérifie la stabilité de la topologie après une coupure de lien.
- Compare les compteurs avant et après le regroupement.
- Débranche un des membres EtherChannel et observe si le Port-channel continue à fonctionner.
- Provoque une incohérence de configuration uniquement dans le simulateur, puis repère les messages et l'état des interfaces.

**À rendre :** root bridge, rôles STP, membres du Port-channel et résultats des tests de panne.


# PARTIE II — Routage et services IP

## TP 5 — Routage statique et route par défaut

**Niveau :** débutant → intermédiaire  
**Environnement :** Packet Tracer ou trois routeurs virtuels.

### Topologie

```text
LAN-A --- R1 --- R2 --- R3 --- LAN-C
```

Plan proposé :

- LAN-A : `192.168.10.0/24` ; passerelle R1 `192.168.10.1` ;
- R1–R2 : `10.0.12.0/30` ; R1 `.1`, R2 `.2` ;
- R2–R3 : `10.0.23.0/30` ; R2 `.1`, R3 `.2` ;
- LAN-C : `192.168.30.0/24` ; passerelle R3 `192.168.30.1`.

### Procédure

1. Configure les interfaces avec les adresses du plan.
2. Vérifie les liens directement connectés depuis chaque routeur.
3. Ajoute des routes statiques vers les LAN distants.
4. Ajoute une route par défaut seulement là où elle correspond au modèle de trafic retenu.
5. Vérifie la table de routage et le chemin emprunté par un paquet.
6. Retire une route, constate la panne, puis rétablis-la.

Exemples de syntaxe Cisco à adapter :

```text
! Sur R1, atteindre le LAN C en passant par R2
ip route 192.168.30.0 255.255.255.0 10.0.12.2

! Sur R3, atteindre le LAN A en passant par R2
ip route 192.168.10.0 255.255.255.0 10.0.23.1
```

R2 doit disposer des routes appropriées vers les deux LAN. Les routes exactes dépendent des interfaces et des adresses réellement affectées.

### Vérifications

```text
show ip route
show ip interface brief
traceroute 192.168.30.10
```

Sur certains simulateurs Cisco, la commande de test peut s'écrire `tracert` depuis un poste ou `traceroute` depuis le routeur.

### Défi

Ajoute un deuxième chemin entre R1 et R3. Compare une route statique simple et une solution dynamique dans le TP suivant. Explique pourquoi une route statique ne détecte pas nécessairement toutes les pannes situées au-delà du prochain saut.


## TP 6 — OSPF : voisinage, annonces et dépannage

**Niveau :** intermédiaire  
**Environnement :** Packet Tracer, GNS3, CML ou routeurs compatibles.

### Objectifs

- Former un voisinage OSPF.
- Annoncer les LAN et lire les routes apprises dynamiquement.
- Diagnostiquer un voisinage qui ne se forme pas.

### Plan de réseau

Reprends la topologie du TP 5. Les interfaces possèdent déjà leurs adresses. OSPF sera configuré dans l'aire 0 pour commencer.

Sur R1 :

```text
configure terminal
router ospf 10
 router-id 1.1.1.1
 network 192.168.10.0 0.0.0.255 area 0
 network 10.0.12.0 0.0.0.3 area 0
end
```

Sur R2 :

```text
configure terminal
router ospf 10
 router-id 2.2.2.2
 network 10.0.12.0 0.0.0.3 area 0
 network 10.0.23.0 0.0.0.3 area 0
end
```

Sur R3 :

```text
configure terminal
router ospf 10
 router-id 3.3.3.3
 network 10.0.23.0 0.0.0.3 area 0
 network 192.168.30.0 0.0.0.255 area 0
end
```

Selon l'image logicielle et la configuration initiale, il peut être nécessaire de remettre à jour le processus ou de redémarrer OSPF pour appliquer un changement de router ID. Préfère comprendre le comportement et suivre la procédure adaptée plutôt que de réinitialiser sans diagnostic.

### Vérification

```text
show ip ospf neighbor
show ip ospf interface brief
show ip route ospf
show ip protocols
```

R1 doit apprendre le réseau LAN-C si l'ensemble des interfaces, voisinages et annonces sont corrects. Le préfixe appris apparaît typiquement comme une route OSPF dans la table.

### Pannes contrôlées

1. Configure une interface de transit dans une mauvaise plage IP.
2. Configure des aires différentes de chaque côté d'un lien.
3. Configure un masque ou une temporisation incompatible si la plateforme permet le test.
4. Désactive l'interface de transit.
5. Compare l'état OSPF, la table de routage et les pings avant/après.

### Questions avancées

- Pourquoi un voisin peut-il être visible mais ne pas atteindre l'état FULL ?
- Quelle différence entre une route directement connectée et une route apprise par OSPF ?
- Quel serait l'intérêt d'une aire supplémentaire dans une topologie plus grande ?

**À rendre :** voisins OSPF, routes apprises et diagnostic documenté d'au moins deux pannes.


## TP 7 — DHCP et DNS : les services dont les pannes ressemblent à du routage

**Niveau :** intermédiaire  
**Environnement :** Packet Tracer ou machines virtuelles Linux.

### Partie A : DHCP

Crée deux VLAN avec un service DHCP qui fournit une adresse, un masque, une passerelle et un serveur DNS. Dans Packet Tracer, tu peux utiliser le service DHCP d'un serveur ou un pool sur un routeur.

Exemple Cisco IOS pour le VLAN 10 :

```text
ip dhcp excluded-address 192.168.10.1 192.168.10.20
ip dhcp pool USERS10
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 192.168.20.53
```

Si le client et le serveur DHCP se trouvent dans des sous-réseaux distincts, examine le rôle du relais DHCP et de la commande de relais adaptée à la plateforme, par exemple `ip helper-address` sur une interface L3 appropriée. Ne l'ajoute pas automatiquement si le serveur se trouve sur le même segment de diffusion.

**Tests :** libère et renouvelle le bail client, vérifie les options reçues et consulte les baux du serveur ou du routeur.

### Partie B : DNS

Configure ou utilise un service DNS de laboratoire. Crée un enregistrement de test comme `intranet.lab.example` pointant vers l'adresse du serveur web de la maquette. Le suffixe `.example` est réservé à la documentation.

Teste séparément :

- accès par adresse IP ;
- résolution du nom ;
- accès par nom après résolution ;
- résolution depuis chaque VLAN autorisé.

### Dépannage guidé

Si l'accès par adresse IP fonctionne mais que l'accès par nom échoue, la panne est probablement liée à la résolution, au DNS indiqué au client, à la connectivité vers le serveur DNS ou au contenu de la zone — pas nécessairement au routage général.

**À rendre :** bail DHCP obtenu, options reçues, enregistrement DNS et preuve de résolution.


## TP 8 — IPv6 : adressage, Neighbor Discovery et routage

**Niveau :** intermédiaire  
**Environnement :** Packet Tracer ou Linux.

### Objectifs

- Configurer des adresses IPv6 globales de laboratoire.
- Comprendre le rôle des adresses link-local.
- Vérifier la découverte des voisins et l'activation du routage IPv6.

### Plan IP

- LAN-A : `2001:db8:10::/64`, routeur `2001:db8:10::1` ;
- lien R1–R2 : `2001:db8:12::/64`, R1 `::1`, R2 `::2` ;
- LAN-B : `2001:db8:20::/64`, routeur `2001:db8:20::1`.

Le préfixe `2001:db8::/32` est réservé aux exemples de documentation, pas à l'adressage public en production.

Sur les routeurs Cisco compatibles :

```text
configure terminal
ipv6 unicast-routing
interface GigabitEthernet0/0
 ipv6 address 2001:db8:10::1/64
 no shutdown
end
```

Répète avec les adresses des autres interfaces selon le plan. Ajoute ensuite le routage IPv6 statique ou dynamique adapté à la maquette.

### Vérifications

```text
show ipv6 interface brief
show ipv6 route
show ipv6 neighbors
ping ipv6 2001:db8:20::10
```

Les syntaxes de ping IPv6 peuvent varier selon l'OS. Sur Linux, utilise `ip -6 address`, `ip -6 route`, `ip -6 neigh` et `ping -6`.

### Pannes à simuler

- Préfixe incorrect sur une interface.
- Oubli de l'activation du routage IPv6 sur un routeur qui en a besoin.
- Route de retour absente.
- Filtrage ICMPv6 trop large : observe pourquoi ICMPv6 est nécessaire à de nombreuses fonctions IPv6, notamment Neighbor Discovery et Path MTU Discovery.

**À rendre :** plan d'adressage, table de voisins et table de routage IPv6.


# PARTIE III — Sécurité et analyse de paquets

## TP 9 — ACL : autoriser les flux utiles, bloquer le reste

**Niveau :** intermédiaire  
**Environnement :** Packet Tracer ou équipement réseau de laboratoire.

### Scénario

Le VLAN 10 (`192.168.10.0/24`) contient les utilisateurs. Le VLAN 20 (`192.168.20.0/24`) contient des serveurs. Le serveur web est `192.168.20.10` et le serveur DNS est `192.168.20.53`.

Politique demandée :

- les utilisateurs peuvent interroger le DNS (`192.168.20.53`, UDP et TCP destination 53) ;
- les utilisateurs peuvent accéder au serveur web en TCP 80 et 443 ;
- les autres communications initiées du VLAN 10 vers le VLAN 20 sont refusées ;
- les autres destinations restent soumises à la politique générale prévue par la maquette.

### Exemple Cisco IOS

Applique l'ACL à l'entrée de l'interface L3 recevant le trafic du VLAN 10. Sur une architecture router-on-a-stick, il peut s'agir de la sous-interface VLAN 10. Vérifie d'abord la configuration et les ACL déjà présentes.

```text
ip access-list extended USERS10-TO-SERVERS
 permit udp 192.168.10.0 0.0.0.255 host 192.168.20.53 eq 53
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.53 eq 53
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 80
 permit tcp 192.168.10.0 0.0.0.255 host 192.168.20.10 eq 443
 deny ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 log
 permit ip 192.168.10.0 0.0.0.255 any
!
interface GigabitEthernet0/0.10
 ip access-group USERS10-TO-SERVERS in
```

Cette règle est un exemple pédagogique, pas une politique de sécurité prête à l'emploi. Elle autorise le trafic DNS et web indiqué ; la dernière permission autorise le VLAN 10 vers les autres destinations. Dans un réseau réel, il faut définir explicitement les flux nécessaires, notamment l'administration, les services d'identité, les mises à jour et les accès Internet. L'ACL ne réalise pas à elle seule une inspection avec état comparable à un pare-feu.

### Validation

Teste chaque flux autorisé et au moins trois flux qui doivent être bloqués. Consulte les compteurs et confirme le sens d'application de l'ACL.

```text
show access-lists
show ip interface GigabitEthernet0/0.10
```

### Erreurs à rechercher

- ACL placée sur la mauvaise interface ou dans le mauvais sens ;
- règles dans un ordre incohérent ;
- oubli de DNS en TCP, nécessaire dans certains cas ;
- oublier que la plupart des ACL classiques sont évaluées de haut en bas avec un refus implicite final ;
- confondre filtrage stateless d'une ACL et inspection avec état d'un pare-feu.

**À rendre :** matrice « source / destination / protocole / port / résultat attendu », ainsi que les compteurs après les tests.


## TP 10 — NAT/PAT : sortie vers un réseau externe de laboratoire

**Niveau :** intermédiaire  
**Environnement :** Packet Tracer ou routeur virtuel avec un réseau WAN de test.

### Objectifs

- Comprendre la différence entre NAT et PAT.
- Configurer une traduction source pour plusieurs postes partageant une adresse de sortie.
- Vérifier les traductions et le chemin retour.

### Scénario

Les LAN NovaTech utilisent des plages privées. Le routeur possède une interface côté LAN et une interface côté réseau externe simulé. L'adresse de l'interface externe est réservée exclusivement au TP.

Exemple Cisco IOS — remplace les interfaces par celles réellement utilisées :

```text
access-list 1 permit 192.168.0.0 0.0.255.255
!
interface GigabitEthernet0/0
 ip nat inside
!
interface GigabitEthernet0/1
 ip nat outside
!
ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

La commande `overload` active le PAT, qui permet à plusieurs flux de partager l'adresse d'interface externe grâce aux numéros de ports. L'exemple ne configure pas l'adresse de l'interface, la route par défaut ni le réseau simulant l'extérieur : complète ces éléments selon ta topologie.

### Vérifications

```text
show ip nat translations
show ip nat statistics
show ip route
```

Depuis deux hôtes internes, génère des flux vers un serveur externe du laboratoire et vérifie les traductions créées.

### Dépannage

- NAT inside/outside inversés ;
- ACL NAT qui ne couvre pas le bon sous-réseau ;
- route de retour absente du réseau externe ;
- ACL de sécurité qui bloque le flux ;
- confusion entre une traduction NAT et une règle qui autorise le trafic.

**À rendre :** table des traductions et explication de la différence entre routage, filtrage et traduction d'adresse.


## TP 11 — Wireshark et tcpdump : observer au lieu de deviner

**Niveau :** débutant → expert  
**Environnement :** Wireshark et/ou `tcpdump` sur une maquette autorisée.

### Objectifs

- Distinguer filtres de capture et filtres d'affichage.
- Relier une trame observée à un échange réseau concret.
- Décomposer un dépannage en observations vérifiables.

### Manipulation A : ARP ou Neighbor Discovery

1. Démarre une capture sur l'interface correspondant au LAN de test.
2. Vide ou laisse expirer l'entrée ARP/voisin de la machine de test dans le laboratoire.
3. Lance un ping vers un voisin local.
4. Arrête la capture et identifie la résolution d'adresse puis l'échange ICMP.

Filtres d'affichage utiles :

```text
arp
icmp
icmpv6
```

### Manipulation B : DNS et TCP

1. Effectue une résolution DNS pour le nom de test de la maquette.
2. Accède à un service HTTP non sensible du laboratoire.
3. Identifie la requête DNS, la réponse et l'établissement TCP.
4. Repère SYN, SYN-ACK et ACK.
5. Compare les adresses IP et ports source/destination.

Filtres d'affichage :

```text
dns
tcp
tcp.port == 80
ip.addr == 192.0.2.10
```

Filtres de capture BPF, à sélectionner avant la capture :

```text
icmp
udp port 53
tcp port 80
```

**Attention :** la syntaxe d'un filtre de capture n'est pas celle d'un filtre d'affichage. Par exemple, `tcp port 443` est un filtre de capture classique, tandis que `tcp.port == 443` est un filtre d'affichage Wireshark. HTTPS chiffre le contenu applicatif ; une capture peut montrer les métadonnées réseau et TLS disponibles, mais pas nécessairement le texte échangé.

### Manipulation C : MTU et retransmissions

Dans un réseau de laboratoire, observe le comportement de paquets de tailles différentes, les éventuels messages ICMP utiles et les retransmissions TCP. Ne conclus pas qu'un lien est sain uniquement parce qu'un ping de petite taille réussit.

### Méthode d'analyse

Pour chaque capture, note :

- l'interface et le point de capture ;
- l'heure ;
- le filtre utilisé ;
- le paquet qui prouve ou invalide l'hypothèse ;
- ce que la capture ne permet pas de conclure.

**À rendre :** une capture anonymisée ou générée dans le labo, accompagnée de trois observations commentées.


# PARTIE IV — Laboratoires Linux reproductibles

## TP 12 — Créer un mini-réseau avec des espaces de noms Linux

**Niveau :** intermédiaire  
**Environnement :** Linux avec `iproute2`, `ping` et privilèges administrateur.

Les *network namespaces* isolent des interfaces, des routes et des piles réseau. Les paires `veth` créent deux interfaces virtuelles reliées entre elles. Cette approche permet de réaliser une maquette sans plusieurs machines physiques.

### Topologie

```text
h1 (192.0.2.10/24) -- r1 -- h2 (198.51.100.10/24)
                      routage IPv4
```

### Création de la topologie

Les commandes suivantes créent exclusivement les objets nommés pour ce TP. Exécute-les dans une VM dédiée.

```bash
sudo ip netns add h1
sudo ip netns add r1
sudo ip netns add h2

sudo ip link add h1-r1 type veth peer name r1-h1
sudo ip link add r1-h2 type veth peer name h2-r1

sudo ip link set h1-r1 netns h1
sudo ip link set r1-h1 netns r1
sudo ip link set r1-h2 netns r1
sudo ip link set h2-r1 netns h2

sudo ip -n h1 link set lo up
sudo ip -n r1 link set lo up
sudo ip -n h2 link set lo up

sudo ip -n h1 addr add 192.0.2.10/24 dev h1-r1
sudo ip -n r1 addr add 192.0.2.1/24 dev r1-h1
sudo ip -n r1 addr add 198.51.100.1/24 dev r1-h2
sudo ip -n h2 addr add 198.51.100.10/24 dev h2-r1

sudo ip -n h1 link set h1-r1 up
sudo ip -n r1 link set r1-h1 up
sudo ip -n r1 link set r1-h2 up
sudo ip -n h2 link set h2-r1 up

sudo ip -n h1 route add default via 192.0.2.1
sudo ip -n h2 route add default via 198.51.100.1
sudo ip netns exec r1 sysctl -w net.ipv4.ip_forward=1
```

### Vérification

```bash
sudo ip netns exec h1 ping -c 4 192.0.2.1
sudo ip netns exec h2 ping -c 4 198.51.100.1
sudo ip netns exec h1 ping -c 4 198.51.100.10
sudo ip -n r1 route show
```

Si les deux premiers tests fonctionnent mais que le troisième échoue, vérifie le transfert IPv4 et les routes de retour avant de modifier les adresses.

### Nettoyage

À la fin des TP Linux, supprime uniquement les namespaces que tu as créés pour ce cahier :

```bash
sudo ip netns del h1
sudo ip netns del r1
sudo ip netns del h2
```

La suppression des namespaces supprime les interfaces qui leur sont attachées. Si tu réutilises les mêmes noms pour d'autres expériences, assure-toi que les objets appartiennent bien à ce TP.


## TP 13 — Filtrage stateful et NAT sous Linux avec nftables

**Niveau :** intermédiaire → expert  
**Prérequis :** TP 12 fonctionnel. Effectue le TP dans une VM de laboratoire : les règles de pare-feu incorrectes peuvent couper des connexions.

### Partie A : observer avant de filtrer

Vérifie les interfaces et les routes de `r1` :

```bash
sudo ip -n r1 address show
sudo ip -n r1 route show
sudo ip netns exec r1 nft list ruleset
```

Une table nftables peut être vide au départ. Ne suppose pas qu'elle l'est sur une machine réelle ; examine toujours le jeu de règles existant.

### Partie B : pare-feu de transfert pour le laboratoire

La politique suivante bloque le transfert par défaut, conserve les réponses aux connexions déjà suivies et autorise ICMP entre les deux réseaux du TP. Elle modifie le pare-feu à l'intérieur du namespace `r1`, pas celui de l'hôte.

```bash
sudo ip netns exec r1 nft add table inet labfilter
sudo ip netns exec r1 nft 'add chain inet labfilter forward { type filter hook forward priority 0; policy drop; }'
sudo ip netns exec r1 nft add rule inet labfilter forward ct state established,related accept
sudo ip netns exec r1 nft add rule inet labfilter forward ip protocol icmp accept
```

Teste les pings. Consulte ensuite les règles et leurs compteurs :

```bash
sudo ip netns exec r1 nft list table inet labfilter
```

Ajoute ensuite une règle TCP ciblée pour un service de laboratoire avant de tester ce service. Ne remplace pas la politique entière par un `accept` général : cela annulerait l'objectif de l'exercice.

### Partie C : NAT de sortie

Dans ce scénario, `h1` atteint le réseau de `h2` à travers `r1`. Ajoute la traduction seulement après avoir compris le chemin et les adresses sources observées. L'exemple de masquerade ci-dessous traduit les paquets qui sortent par `r1-h2` :

```bash
sudo ip netns exec r1 nft add table ip labnat
sudo ip netns exec r1 nft 'add chain ip labnat postrouting { type nat hook postrouting priority srcnat; policy accept; }'
sudo ip netns exec r1 nft add rule ip labnat postrouting oifname "r1-h2" ip saddr 192.0.2.0/24 masquerade
sudo ip netns exec r1 nft list table ip labnat
```

Refais la capture côté h2 et compare l'adresse source avant et après NAT.

### Nettoyage

Supprime uniquement les tables créées par le TP :

```bash
sudo ip netns exec r1 nft delete table inet labfilter
sudo ip netns exec r1 nft delete table ip labnat
```

**À rendre :** règles appliquées, preuves de test et explication de la différence entre filtrage, suivi de connexion et NAT.


# PARTIE V — Routage dynamique avancé

## TP 14 — BGP entre deux systèmes autonomes avec FRRouting

**Niveau :** avancé  
**Environnement :** GNS3, Containerlab ou deux routeurs Linux de laboratoire équipés de FRRouting.

Ce TP est volontairement séparé d'OSPF : BGP échange des informations de routage entre pairs, souvent avec une politique explicite de ce qui peut être annoncé ou accepté. En environnement réel, ne configure jamais un voisin BGP sans définir les préfixes autorisés, les règles d'import/export et les mesures de protection adaptées.

### Scénario logique

- AS 65010 : réseau `192.0.2.0/24`, routeur R1 ;
- lien de peering : `198.51.100.0/30`, R1 `198.51.100.1`, R2 `198.51.100.2` ;
- AS 65020 : réseau `203.0.113.0/24`, routeur R2.

Les plages sont réservées aux exemples. Les interfaces doivent être adressées et opérationnelles avant de configurer BGP.

### Configuration type FRR

Dans le terminal `vtysh` de R1 :

```text
configure terminal
router bgp 65010
 bgp router-id 1.1.1.1
 neighbor 198.51.100.2 remote-as 65020
 address-family ipv4 unicast
  network 192.0.2.0/24
  neighbor 198.51.100.2 activate
 exit-address-family
end
write memory
```

Dans `vtysh` de R2 :

```text
configure terminal
router bgp 65020
 bgp router-id 2.2.2.2
 neighbor 198.51.100.1 remote-as 65010
 address-family ipv4 unicast
  network 203.0.113.0/24
  neighbor 198.51.100.1 activate
 exit-address-family
end
write memory
```

Le préfixe `network` n'est annoncé que si la route correspondante existe dans la table de routage selon le comportement du logiciel. Il faut donc créer les interfaces ou routes de laboratoire correspondant aux réseaux annoncés. La syntaxe exacte et les fonctions disponibles dépendent de la version de FRR.

### Vérifications

```text
show bgp summary
show bgp ipv4 unicast
show ip route
```

Vérifie que la session est établie, que les préfixes attendus sont reçus et que les routes sont installées. Un état Established ne garantit pas, à lui seul, que la politique d'annonce est correcte.

### Défis

1. Supprime temporairement l'adresse du lien de peering et observe le voisinage.
2. Retire le préfixe local annoncé et observe le retrait de route.
3. Ajoute un préfixe de test et limite explicitement les annonces autorisées.
4. Explique le risque d'accepter ou d'annoncer tous les préfixes sans filtre.

**À rendre :** sortie du résumé BGP, routes reçues et politique de préfixes autorisés.


## TP 15 — VXLAN : construire un overlay de couche 2 sur IP

**Niveau :** avancé  
**Environnement :** Linux récent avec prise en charge VXLAN, deux namespaces/VM et outils de diagnostic.

Ce TP illustre le mécanisme VXLAN de base. Il **ne met pas en œuvre EVPN/BGP** : la découverte des VTEP est statique. L'objectif est de comprendre l'encapsulation et la séparation entre underlay et overlay avant d'aborder une architecture EVPN plus complexe.

### Objectif

Deux extrémités VTEP doivent relier leurs hôtes dans le même segment logique, tout en échangeant les paquets VXLAN à travers un réseau IP. Le VNI d'exemple est `10010`.

### Préparation conceptuelle

Les deux VTEP doivent avoir des adresses IP de transport joignables. Le transport doit autoriser le trafic VXLAN entre les VTEP — traditionnellement UDP/4789, sauf configuration différente explicitement retenue. Le MTU sous-jacent doit aussi prendre en compte la surcharge VXLAN.

### Exemple de création d'un tunnel VXLAN Linux

Sur VTEP-A, avec adresse underlay `192.0.2.1` et VTEP-B `192.0.2.2` :

```bash
sudo ip link add vxlan10010 type vxlan id 10010 dev eth0 remote 192.0.2.2 dstport 4789
sudo ip link set vxlan10010 up
```

Sur VTEP-B, inverse l'adresse distante :

```bash
sudo ip link add vxlan10010 type vxlan id 10010 dev eth0 remote 192.0.2.1 dstport 4789
sudo ip link set vxlan10010 up
```

Ici `eth0` est un exemple : remplace-le par l'interface underlay réelle. La topologie complète doit ensuite connecter les interfaces VXLAN aux bridges L2 de chaque hôte. La commande seule ne configure ni les hôtes, ni les adresses IP des hôtes, ni la connectivité underlay.

### Vérifications

```bash
ip -d link show vxlan10010
ip link show
ip route show
sudo tcpdump -ni eth0 udp port 4789
```

Génère un trafic de test entre les hôtes du segment overlay et vérifie qu'un paquet UDP VXLAN apparaît sur l'underlay. Si le trafic ne fonctionne pas, vérifie d'abord la connectivité IP entre les VTEP, l'interface de transport, le VNI, le port UDP, le bridge et la MTU.

### Questions

- Quelle différence entre VNI et VLAN ID ?
- Pourquoi la connectivité IP entre les VTEP doit-elle fonctionner avant l'overlay ?
- Que manque-t-il pour passer d'un VXLAN statique à une architecture EVPN pilotée par BGP ?
- Pourquoi un MTU insuffisant peut-il affecter les gros paquets sans empêcher tous les petits pings ?

**À rendre :** état détaillé de l'interface VXLAN, capture UDP/4789, test de connectivité et limites du laboratoire.


# PARTIE VI — Automatisation, SD-WAN et exercices de synthèse

## TP 16 — Automatiser un contrôle réseau en Python

**Niveau :** avancé  
**Environnement :** poste de contrôle avec Python 3 et données de laboratoire.

L'objectif initial est de contrôler des données sans modifier le réseau. Commence par un mode lecture seule avant de déployer une configuration automatisée.

### Inventaire exemple

Crée un fichier `inventory.csv` :

```csv
hostname,management_ip,site,role
R1,192.0.2.11,HQ,edge
R2,192.0.2.12,BRANCH,edge
SW1,192.0.2.21,HQ,switch
```

### Script de validation des données

```python
import csv
import ipaddress
from pathlib import Path

inventory_path = Path("inventory.csv")
required_fields = {"hostname", "management_ip", "site", "role"}

if not inventory_path.exists():
    raise SystemExit(f"Fichier absent : {inventory_path}")

seen_names = set()
seen_addresses = set()
errors = []

with inventory_path.open(newline="", encoding="utf-8") as stream:
    reader = csv.DictReader(stream)
    fields = set(reader.fieldnames or [])
    missing = required_fields - fields
    if missing:
        raise SystemExit(f"Colonnes manquantes : {', '.join(sorted(missing))}")

    for line_number, row in enumerate(reader, start=2):
        name = (row.get("hostname") or "").strip()
        address = (row.get("management_ip") or "").strip()
        site = (row.get("site") or "").strip()
        role = (row.get("role") or "").strip()

        if not name or not site or not role:
            errors.append(f"Ligne {line_number}: champ vide")
            continue
        if name in seen_names:
            errors.append(f"Ligne {line_number}: nom dupliqué {name}")
        seen_names.add(name)

        try:
            parsed_address = ipaddress.ip_address(address)
        except ValueError:
            errors.append(f"Ligne {line_number}: IP invalide {address!r}")
            continue
        if address in seen_addresses:
            errors.append(f"Ligne {line_number}: IP dupliquée {address}")
        seen_addresses.add(address)

        print(f"OK ligne {line_number}: {name} {parsed_address} {site} {role}")

if errors:
    print("\nErreurs détectées :")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("Inventaire valide : aucune erreur détectée.")
```

### Extensions demandées

1. Ajouter la détection de doublons d'hôtes et d'adresses.
2. Ajouter un contrôle de plages IP autorisées pour le réseau de gestion du laboratoire.
3. Ajouter un rapport de synthèse JSON.
4. Enregistrer le code dans un dépôt versionné et ajouter quelques tests.
5. Si tu ajoutes une connexion SSH ou une API, utiliser des identifiants dédiés au laboratoire, stocker les secrets hors du dépôt et privilégier des comptes de lecture seule pour le diagnostic.

**Critère de réussite :** les données incorrectes sont signalées avant toute connexion aux équipements.


## TP 17 — Préparer un mini-laboratoire SD-WAN

**Niveau :** avancé → expert  
**Environnement :** laboratoire Cisco Catalyst SD-WAN officiellement pris en charge par la version ciblée, ou environnement de formation fourni par l'organisation.

Ce TP est un exercice de conception et de validation. Packet Tracer ne doit pas être considéré comme un simulateur complet de Catalyst SD-WAN. Les commandes, composants et fonctions dépendent de la plateforme SD-WAN réellement utilisée.

### Scénario NovaTech

Le siège et deux agences possèdent chacun deux transports : Transport-A et Transport-B. Les applications sont réparties entre voix/visioconférence, ERP, SaaS et sauvegardes. Les utilisateurs, serveurs, invités et équipements d'administration sont segmentés.

### Travail demandé

1. Documenter les composants de gestion, d'orchestration, de contrôle et les WAN Edges.
2. Vérifier séparément la connectivité underlay, les connexions de contrôle, l'échange de routes et les tunnels de données.
3. Définir des classes d'application et des seuils SLA qui correspondent à des objectifs mesurables.
4. Concevoir une politique qui décrit le comportement lorsque le chemin préféré devient dégradé et lorsqu'aucun chemin ne respecte le SLA.
5. Définir les flux autorisés entre segments ainsi que les points d'inspection.
6. Tester la perte d'un transport dans une fenêtre approuvée et mesurer la durée de rétablissement des applications.
7. Tester une dégradation progressive, pas seulement une coupure franche.
8. Comparer l'expérience applicative avant et après la bascule.
9. Produire un plan de retour arrière et un rapport de limites connues.

### Mesures à conserver

- état des connexions de contrôle ;
- état des routes et préfixes distribués ;
- état des tunnels et des mesures BFD ;
- chemin choisi pour chaque classe d'application ;
- perte, latence, gigue et charge de chaque transport ;
- résultats des transactions applicatives ;
- heure de début de panne, heure de détection et heure de retour au service.

**Critère de réussite :** la bascule est démontrée par des données et des tests applicatifs, pas uniquement par un voyant ou un état de tunnel.


## TP 18 — Incident de synthèse : « le réseau est vert, mais l'application ne fonctionne pas »

**Niveau :** expert

### Situation

NovaTech signale que l'ERP est inaccessible depuis une agence. Les interfaces sont actives, les connexions de contrôle semblent stables et au moins un tunnel de données est opérationnel.

### Mission

Tu dois diagnostiquer le problème sans redémarrer les équipements et sans ajouter immédiatement une route statique. Procède par étapes :

1. Définis précisément les postes, segments, destinations et horaires affectés.
2. Compare l'agence en panne à une agence saine.
3. Teste la connectivité locale, la passerelle et les dépendances DNS/identité.
4. Vérifie les routes vers l'ERP au site source et au site destination.
5. Contrôle le VPN/VRF, les politiques de contrôle et les politiques de données.
6. Vérifie le tunnel réellement utilisé et le chemin retour.
7. Inspecte les ACL, le pare-feu, le NAT et toute insertion de service.
8. Collecte des captures de paquets ciblées si cela permet de départager des hypothèses.
9. N'applique qu'une correction à la fois et conserve les preuves avant/après.
10. Rédige une analyse de cause racine, puis une action préventive.

### Hypothèses à départager

- route absente ou non distribuée ;
- route présente mais chemin de retour invalide ;
- politique de segmentation ou ACL trop restrictive ;
- tunnel disponible mais dégradé ;
- DNS ou authentification en panne ;
- service de sécurité indisponible ;
- MTU ou fragmentation ;
- changement récent de politique ou de routage.

### Rapport de fin d'incident

```text
Résumé de l'incident :
Début / fin :
Périmètre impacté :
Impact métier :
Hypothèse initiale :
Preuves collectées :
Cause racine confirmée :
Correction effectuée :
Validation post-correction :
Cause contributive éventuelle :
Action préventive :
Responsable et échéance :
```

**Critère de réussite :** le rapport explique le lien entre le symptôme, la cause et la correction, et propose un moyen de prévenir ou de détecter plus tôt la récidive.


# Annexes

## A. Commandes de diagnostic à retenir

Ces commandes sont courantes mais leur disponibilité et leur syntaxe varient selon l'OS réseau, la version et le contexte.

| Objectif | Exemples |
|---|---|
| Interfaces | `show ip interface brief`, `ip address show` |
| Routes IPv4 | `show ip route`, `ip route show` |
| Voisins L2/L3 | `show arp`, `ip neigh show` |
| VLAN | `show vlan brief` |
| Trunks | `show interfaces trunk` |
| STP | `show spanning-tree` |
| EtherChannel | `show etherchannel summary` |
| OSPF | `show ip ospf neighbor`, `show ip route ospf` |
| BGP FRR | `show bgp summary`, `show bgp ipv4 unicast` |
| ACL | `show access-lists` |
| NAT | `show ip nat translations`, `show ip nat statistics` |
| IPv6 | `show ipv6 route`, `ip -6 route show` |
| Linux firewall | `nft list ruleset` ou la table du laboratoire |
| Capture | `tcpdump -ni INTERFACE`, Wireshark avec filtre approprié |
| Connectivité | `ping`, `traceroute` ou l'équivalent du système |

**Règle de dépannage :** commencer par une preuve simple de la couche locale, avancer vers la couche concernée, puis contrôler le chemin retour. Une commande isolée n'est pas une preuve complète de la santé d'un service.

## B. Modèle de fiche de tests

| ID | Source | Destination | Protocole/port | Résultat attendu | Résultat observé | Verdict |
|---|---|---|---|---|---|---|
| T-01 | PC-A | Passerelle VLAN 10 | ICMP | Réussite | À renseigner | À renseigner |
| T-02 | PC-A | PC-B, même VLAN | ICMP | Réussite | À renseigner | À renseigner |
| T-03 | VLAN 10 | Serveur web autorisé | TCP 443 | Réussite si service actif | À renseigner | À renseigner |
| T-04 | VLAN 30 | Serveur métier interdit | Selon politique | Échec contrôlé | À renseigner | À renseigner |
| T-05 | Agence | ERP distant | Application réelle | Réussite | À renseigner | À renseigner |

Ajoute des tests négatifs. Un réseau qui autorise le trafic légitime mais aussi tous les flux indésirables n'a pas rempli l'objectif de sécurité.

## C. Barème d'évaluation des travaux pratiques

Pour chaque TP, tu peux utiliser un barème sur 20 :

- 4 points : plan d'adressage et topologie corrects ;
- 4 points : configuration cohérente et documentée ;
- 4 points : vérifications positives concluantes ;
- 4 points : incidents simulés, diagnostic et correction ;
- 4 points : compte rendu clair, avec preuves et limites.

Une configuration qui « marche » mais que l'étudiant ne sait pas expliquer ne démontre pas une maîtrise complète.

## D. Références officielles

- [Cisco Networking Academy — Packet Tracer](https://www.netacad.com/catalogs/learn/cisco-packet-tracer) : simulateur pédagogique et activités de mise en pratique.
- [Documentation officielle FRRouting](https://docs.frrouting.org/en/latest/) : OSPF, BGP, routes, interfaces et outils de diagnostic. La disponibilité de chaque fonction dépend de la version.
- [Site du projet FRRouting](https://frrouting.org/doc/) : documentation et informations du projet.
- [Documentation nftables](https://wiki.nftables.org/wiki-nftables/index.php/Main_Page) : tables, chaînes, règles, suivi de connexion et NAT.
- [Guide utilisateur Wireshark](https://www.wireshark.org/docs/wsug_html/index) : capture, affichage et filtres.
- [Filtres d'affichage Wireshark](https://wiki.wireshark.org/displayFilters) : syntaxe des filtres d'affichage.
- [Filtres de capture Wireshark](https://wiki.wireshark.org/CaptureFilters) : syntaxe des filtres appliqués avant capture.

Consulte la documentation correspondant à ta version et au système réellement utilisé. Ce cahier fournit un cadre pédagogique et ne remplace pas les guides de configuration des équipements.


## Conclusion

Ces travaux pratiques couvrent le cycle complet d'apprentissage réseau : concevoir, configurer, vérifier, provoquer une panne, observer, dépanner et documenter. La progression commence par la connectivité et les VLAN, puis ajoute le routage, les services IP, les règles de sécurité, l'analyse de paquets, le routage dynamique, les overlays et l'automatisation.

Pour progresser, répète les exercices en modifiant une seule variable à la fois, puis retire volontairement une hypothèse (route, règle, DNS, trunk, transport) et tente de diagnostiquer la panne à partir des preuves. Le but final n'est pas de mémoriser des commandes, mais de savoir expliquer pourquoi le réseau adopte un comportement donné et comment rétablir le service sans créer une nouvelle panne.
