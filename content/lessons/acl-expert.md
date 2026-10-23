# ACL & filtrage — Expert

**Niveau :** Expert

Les listes de contrôle d’accès (Access Control Lists, ACL) constituent un mécanisme fondamental de classification et de filtrage du trafic réseau. Sur les équipements Cisco, elles interviennent dans le plan de données pour autoriser ou refuser des paquets selon des critères tels que les adresses source et destination, les protocoles, les ports TCP/UDP, certains champs ICMP ou les options IPv4. Elles servent également de primitives à d’autres fonctions : NAT, QoS, policy-based routing (PBR), redistribution de routes, filtrage des accès VTY et politiques de sécurité.

L’expertise ne consiste pas simplement à écrire une ligne `permit` ou `deny`. Elle exige de comprendre le point d’application, le sens du trafic, le contexte de routage, la sémantique des champs inspectés, le traitement des fragments, les effets du premier match et le comportement de la plateforme. Une ACL correcte sur le plan syntaxique peut interrompre un protocole de routage, empêcher les réponses d’un service, casser un VPN ou laisser passer un trafic que l’architecte pensait bloquer.

Les ACL classiques sont généralement stateless : chaque paquet est évalué individuellement et la règle ne sait pas, à elle seule, si le paquet appartient à une session déjà autorisée. Cela les distingue d’un pare-feu à inspection avec suivi d’état. Le caractère stateless est à la fois une force — simplicité, prévisibilité et faible coût — et une limite qui doit être prise en compte lors de la conception des règles et des chemins retour.

Ce cours examine les ACL comme un système de politique déterministe, depuis la logique de correspondance jusqu’aux interactions avec les plans de contrôle et les fonctions réseau. Les exemples sont orientés Cisco IOS/IOS XE ; la syntaxe et les fonctionnalités exactes peuvent varier selon le modèle, la version logicielle, le type d’interface et le chemin matériel utilisé. Toute politique doit être testée dans un environnement représentatif avant production.

> **Analogie** : Une ACL ressemble à un poste de contrôle où chaque véhicule est examiné selon une liste de critères, dans un ordre précis. Le premier contrôle correspondant décide du résultat : un véhicule admis par une règle ne poursuit pas son inspection pour chercher une règle plus restrictive plus bas. Si aucune règle ne correspond, il est refusé par défaut. Le poste ne se souvient pas nécessairement des véhicules déjà entrés : pour laisser revenir une réponse, il faut une règle qui corresponde aussi à ce paquet retour, sauf si un mécanisme distinct assure le suivi d’état. Enfin, déplacer le poste de contrôle change les véhicules qu’il voit : un filtre en entrée d’une interface ne traite pas le même ensemble de paquets qu’un filtre en sortie d’une autre interface.

---

## 1. La théorie et les algorithmes

### 1.1 Modèle d’évaluation : première correspondance

Une ACL ordonnée est une suite d’entrées de contrôle d’accès (ACE, Access Control Entry). Le moteur examine les ACE dans l’ordre configuré. Pour chaque paquet, il teste les champs décrits par l’entrée : si tous les critères de cette ACE correspondent, l’action est appliquée et l’évaluation de cette ACL s’arrête.

Algorithme conceptuel :

1. Recevoir un paquet au point où l’ACL est attachée.
2. Identifier la famille et le type d’ACL appliqué.
3. Lire la première ACE.
4. Comparer les champs de paquet avec les critères de l’ACE.
5. Si l’entrée correspond, appliquer `permit` ou `deny`, puis terminer l’évaluation.
6. Sinon, passer à l’entrée suivante.
7. Si aucune entrée ne correspond, appliquer le refus implicite final.

Cette logique implique que l’ordre est une partie de la politique, et non une simple présentation. Une ACE large placée trop tôt peut neutraliser toutes les exceptions suivantes.

```text
             Paquet reçu
                  |
                  v
       +---------------------+
       | Tester ACE 10       |
       +---------------------+
          | correspond ?
        oui             non
         |               |
         v               v
   appliquer action   Tester ACE 20
         |               |
         v          correspond ?
       FIN           oui / non
                        |
                 ... ACE suivantes ...
                        |
                        v
                Refus implicite
```

Exemple dangereux :

```cisco
ip access-list extended USERS-IN
 permit ip any any
 deny tcp 10.20.10.0 0.0.0.255 host 10.20.30.10 eq 22
```

La règle SSH est inopérante : le trafic correspondant est déjà accepté par `permit ip any any`. L’ordre correct doit placer les restrictions avant le permis général, ou supprimer le permis général si la politique est une liste positive.

### 1.2 ACL standard, étendues et nommées

Une ACL IPv4 standard classique filtre principalement sur l’adresse source. Une ACL étendue peut filtrer sur le protocole, la source, la destination et des critères de couche transport. Les ACL nommées facilitent la lisibilité, la modification et la gestion des séquences.

| Famille | Critères principaux | Usage typique | Limite essentielle |
|---|---|---|---|
| Standard IPv4 | Adresse source | Filtrage simple, certaines fonctions de contrôle | Ne distingue pas directement le service ou la destination |
| Étendue IPv4 | Protocole, source, destination, ports et critères pris en charge | Filtrage de flux | Doit tenir compte du sens et des réponses |
| IPv6 | Adresses IPv6, protocole et champs pris en charge | Filtrage IPv6 | Syntaxe et commandes différentes d’IPv4 |
| Réflexive / dynamique | Fonctionnalités spécifiques à certaines plateformes | Cas limités de création temporaire de règles | Disponibilité et comportement dépendants de la plateforme |
| ACL de contrôle de plan | Accès au routeur lui-même, selon la fonction | Protéger les services du routeur | Ne remplace pas les filtres de transit |

Les ACL standard ne doivent pas être confondues avec les politiques de pare-feu stateful, les ACL de sécurité d’un commutateur de centre de données, les politiques d’un contrôleur SDN ou les ACL d’un système d’exploitation. Les termes sont parfois identiques mais les modèles d’évaluation diffèrent.

### 1.3 Wildcard masks et logique binaire

Dans la syntaxe classique Cisco IPv4, la wildcard indique quels bits de l’adresse doivent être ignorés lors de la comparaison :

- bit `0` : le bit correspondant doit être égal ;
- bit `1` : le bit correspondant est ignoré.

La wildcard est souvent le complément du masque de sous-réseau. Pour un réseau `/24`, le masque est `255.255.255.0` et la wildcard est `0.0.0.255`. Pour une adresse hôte unique, la wildcard est `0.0.0.0`, souvent abrégée par le mot-clé `host`.

Exemples :

```cisco
! Réseau 10.20.10.0/24
permit ip 10.20.10.0 0.0.0.255 any

! Hôte unique
permit tcp host 10.20.10.25 host 10.20.30.40 eq 443

! Toutes les adresses
permit ip any any
```

Les wildcards non contiguës sont possibles dans certaines syntaxes Cisco, mais elles rendent les politiques difficiles à auditer et ne sont pas adaptées aux plans d’adressage habituels. Dans les ACL de sécurité, privilégier les réseaux alignés et les préfixes clairement documentés.

### 1.4 Sémantique des ports TCP et UDP

Dans une ACE étendue, `eq 443` appliqué après l’adresse de destination désigne le port de destination 443. La position du critère est donc importante. `gt`, `lt`, `neq` et les plages `range` peuvent être disponibles selon le contexte de commande.

```cisco
ip access-list extended WEB-IN
 permit tcp 10.20.10.0 0.0.0.255 host 10.20.30.20 eq 443
 deny   ip any any log
```

Cette politique autorise les clients du réseau `10.20.10.0/24` à initier des connexions TCP vers le serveur HTTPS `10.20.30.20`. Elle ne signifie pas que seuls des paquets contenant des données HTTPS sont autorisés : le port est un indicateur de transport, pas une validation applicative. Une application peut utiliser un port inhabituel et un service malveillant peut écouter sur un port courant.

Les ports source sont souvent éphémères pour les clients. Filtrer strictement le port source d’un client peut donc interrompre les connexions. Le trafic de réponse présente généralement le port serveur comme port source et le port éphémère du client comme port destination ; une ACL stateless doit autoriser explicitement ce retour si le chemin traverse une ACL restrictive.

### 1.5 ACL stateless et trafic retour

Considérons un client `10.20.10.25:53000` qui ouvre une connexion vers `10.20.30.20:443`.

```text
Client                                  Serveur
10.20.10.25:53000  ------------------>  10.20.30.20:443
                   TCP SYN

10.20.10.25:53000  <------------------  10.20.30.20:443
                   TCP SYN-ACK
```

Une ACL sur le chemin retour voit le paquet serveur comme une nouvelle unité à évaluer. Elle ne sait pas automatiquement que le SYN précédent a été autorisé. Une politique strictement stateless peut donc devoir autoriser le trafic TCP retour vers les ports éphémères des clients, ce qui exige une conception prudente. Ne pas appliquer naïvement `permit tcp any any established` comme équivalent d’un pare-feu stateful : dans la syntaxe Cisco classique, le mot-clé `established` vérifie certains indicateurs TCP (ACK ou RST) et ne garantit pas l’existence d’une session valide.

Quand l’objectif est d’autoriser des connexions initiées dans un sens tout en autorisant précisément leurs réponses, utiliser un pare-feu stateful ou une fonctionnalité d’inspection adaptée peut être plus sûr et plus simple à maintenir qu’une longue ACL stateless.

### 1.6 Placement : entrée ou sortie

Une ACL `in` est évaluée à l’arrivée du paquet sur l’interface, avant que le paquet ne quitte cette interface. Une ACL `out` est évaluée lorsque le paquet est sur le point de sortir par l’interface. La visibilité des paquets dépend du routage : l’interface de sortie n’est connue qu’après la décision de transfert.

```text
LAN A ---- [G0/0 ROUTEUR G0/1] ---- LAN B
             |             |
         ACL IN          ACL OUT
       trafic entrant   trafic vers LAN B
```

Principes de conception :

- Une ACL étendue peut souvent être placée près de la source pour empêcher le trafic indésirable de traverser le réseau.
- Une ACL standard, qui ne voit que la source, est souvent placée plus près de la destination afin de limiter les effets collatéraux.
- Le placement réel dépend des chemins alternatifs, des interfaces logiques, du routage asymétrique, des ressources matérielles et des besoins de visibilité.
- Une ACL sur une interface physique ne couvre pas nécessairement le trafic traité par une autre interface logique, un tunnel, une SVI ou le plan de contrôle.

Il n’existe pas de règle universelle « étendue près de la source » qui dispense d’analyser l’architecture. La règle est un principe de conception, non un substitut au tracé réel du paquet.

### 1.7 Fragments IPv4 et champs de transport

Les fragments IPv4 ne contiennent pas tous nécessairement les informations de couche 4. Le premier fragment contient normalement l’en-tête de transport, alors que les fragments suivants peuvent ne pas contenir les ports TCP/UDP. Les capacités et la sémantique de correspondance d’une ACL sur fragments varient selon la plateforme et le type d’ACE.

Conséquences opérationnelles :

- Une règle fondée sur les ports peut traiter différemment le premier fragment et les fragments non initiaux.
- Un filtre trop simpliste peut bloquer des applications qui dépendent de la fragmentation.
- L’autorisation des fragments sans cohérence avec les premiers fragments peut créer une surface d’évasion.
- La meilleure stratégie est souvent d’éviter la fragmentation grâce à une MTU/PMTUD correcte, de limiter les fragments selon une politique documentée et de tester le comportement sur l’équipement exact.

Ne pas supposer qu’une ACL de routeur reconstitue les datagrammes ou valide les fragments comme le ferait un système d’inspection stateful.

### 1.8 ICMP, erreurs réseau et protocoles de contrôle

ICMP n’est pas uniquement un outil de ping. Les messages d’erreur IPv4 — destination unreachable, time exceeded et fragmentation needed — participent au diagnostic et à la découverte de MTU. Bloquer tout ICMP peut casser la détection de panne, masquer des problèmes de routage ou empêcher Path MTU Discovery.

La politique doit autoriser les types ICMP requis, depuis les sources appropriées, et les limiter selon le contexte. Les noms de types disponibles dans la CLI dépendent de la version. Pour IPv6, ICMPv6 est indispensable à NDP et à plusieurs fonctions essentielles ; une règle « bloquer tout ICMPv6 » peut rendre le réseau IPv6 non fonctionnel.

Les protocoles de routage comme OSPF, EIGRP ou BGP peuvent être interrompus par une ACL qui ne prévoit que le trafic utilisateur. Les ACL de transit et celles protégeant le routeur lui-même doivent être conçues séparément.

### 1.9 ACL de transit, management plane et control plane

Trois objectifs distincts doivent être séparés :

1. **Transit** : filtrer les paquets qui traversent l’équipement.
2. **Management plane** : restreindre SSH, HTTPS, SNMP et les autres services d’administration vers l’équipement.
3. **Control plane** : protéger les ressources qui traitent les protocoles et paquets destinés au routeur lui-même.

Une ACL sur une interface peut filtrer le trafic adressé à l’équipement, mais les plateformes Cisco offrent aussi des mécanismes spécifiques comme `control-plane` / Control Plane Policing (CoPP) selon les gammes. CoPP limite ou classe le trafic vers le plan de contrôle ; il ne remplace pas les ACL de transit. Les fonctionnalités disponibles varient.

### 1.10 Interaction avec NAT, PBR, QoS et routage

Les ACL peuvent être réutilisées comme classificateurs pour d’autres fonctions. Il faut alors distinguer l’ACL qui décide `permit`/`deny` du traitement qui consomme la correspondance :

- **NAT** : une ACL peut définir les adresses source à traduire. Ici, `permit` signifie souvent « correspond à la règle NAT », pas « autorise ce paquet à traverser le routeur ».
- **PBR** : une ACL classe le trafic auquel appliquer une politique de routage. Le refus dans l’ACL de classification peut signifier « ne correspond pas à cette politique » et non « jeter le paquet ».
- **QoS** : une ACL peut classifier des flux pour les files, marquages ou limites de débit.
- **Redistribution** : les listes et route-maps peuvent filtrer les routes annoncées, mais ce n’est pas la même sémantique qu’une ACL de paquet.
- **VPN** : les ACL crypto définissent le trafic intéressant dans certaines configurations IPsec policy-based ; des sélecteurs incohérents empêchent l’établissement ou le passage du trafic.

Une même syntaxe `permit`/`deny` ne signifie donc pas toujours « autoriser/refuser un paquet ». Il faut lire le consommateur de l’ACL.

> **Piège :** Le mot `permit` dans une ACL référencée par NAT ou PBR n’est pas nécessairement une décision d’autorisation de transit. Dans une ACL de filtrage d’interface, il permet le paquet correspondant ; dans une ACL de classification NAT, il sélectionne généralement le trafic à traduire. Toujours identifier la fonction qui consomme la liste avant d’interpréter ses actions.

### 1.11 IPv6 : différences de modèle

Les ACL IPv6 utilisent une syntaxe distincte, souvent via `ipv6 access-list` puis `ipv6 traffic-filter`. Elles filtrent les adresses IPv6 et les champs de protocole, mais l’architecture IPv6 repose sur ICMPv6 pour Neighbor Discovery et d’autres mécanismes. Les règles doivent conserver le trafic essentiel : Neighbor Solicitation/Advertisement, Router Solicitation/Advertisement et Packet Too Big, selon la politique et le rôle de l’équipement.

Exemple indicatif IOS/IOS XE :

```cisco
ipv6 access-list V6-USERS-IN
 permit icmp any any nd-ns
 permit icmp any any nd-na
 permit icmp any any packet-too-big
 permit tcp 2001:db8:10::/64 host 2001:db8:30::20 eq 443
 deny ipv6 any any log
!
interface GigabitEthernet1/0/10
 ipv6 traffic-filter V6-USERS-IN in
```

Les mots-clés précis et les contraintes d’application doivent être validés sur la version IOS/IOS XE cible. Le préfixe `2001:db8::/32` est réservé à la documentation et ne doit pas être utilisé comme adressage public réel.

### 1.12 Complexité, optimisation et matériel

Sur un routeur logiciel, une ACL peut être examinée comme une liste séquentielle conceptuelle. Sur les équipements modernes, les ACE sont souvent compilées et programmées dans des ressources matérielles, par exemple TCAM (Ternary Content-Addressable Memory), lorsque la plateforme le permet. Les détails varient selon les ASIC et la famille.

Les préoccupations d’exploitation comprennent :

- consommation de TCAM et limites d’entrées ;
- expansion d’une règle en plusieurs entrées matérielles ;
- capacité distincte pour IPv4, IPv6, QoS et sécurité ;
- effets d’une modification sur la compilation et la programmation matérielle ;
- compteurs matériels qui ne correspondent pas toujours exactement à une intuition de comptage logiciel ;
- différence entre configuration présente et politique réellement programmée.

Une ACL longue n’est pas automatiquement lente, mais elle peut épuiser une ressource matérielle ou se compiler différemment. Sur les plateformes de campus ou de centre de données, vérifier les commandes propres au modèle pour les ressources ACL/TCAM et les journaux de programmation.

---

## 2. Configuration et pratique

### 2.1 Scénario d’entreprise

Topologie :

```text
 VLAN 10 - UTILISATEURS                VLAN 30 - SERVEURS
 10.20.10.0/24                         10.20.30.0/24
       |                                     |
       +------------ [Routeur L3] -----------+
                      G0/0  G0/1
```

Politique souhaitée :

- les utilisateurs peuvent accéder au serveur HTTPS `10.20.30.20` ;
- ils peuvent interroger le DNS interne `10.20.30.53` en UDP/TCP 53 ;
- l’administration SSH vers les serveurs est interdite depuis le VLAN utilisateurs ;
- les autres flux des utilisateurs vers le VLAN serveurs sont refusés ;
- les réponses doivent fonctionner selon l’architecture de filtrage choisie.

Une ACL d’entrée sur l’interface côté utilisateurs peut être :

```cisco
ip access-list extended USERS-TO-SERVERS
 remark HTTPS vers le portail
 permit tcp 10.20.10.0 0.0.0.255 host 10.20.30.20 eq 443
 remark DNS UDP et TCP vers le resolvateur
 permit udp 10.20.10.0 0.0.0.255 host 10.20.30.53 eq 53
 permit tcp 10.20.10.0 0.0.0.255 host 10.20.30.53 eq 53
 remark Bloquer l'administration SSH des serveurs
 deny tcp 10.20.10.0 0.0.0.255 10.20.30.0 0.0.0.255 eq 22 log
 remark Refuser le reste vers le réseau serveur
 deny ip 10.20.10.0 0.0.0.255 10.20.30.0 0.0.0.255 log
 remark Laisser le trafic vers les autres destinations être évalué ailleurs
 permit ip 10.20.10.0 0.0.0.255 any
!
interface GigabitEthernet0/0
 description VLAN_UTILISATEURS
 ip access-group USERS-TO-SERVERS in
```

Cette ACL est un exemple pédagogique. Le `permit ip ... any` final signifie que le trafic vers d’autres destinations reste autorisé par cette ACL ; une autre politique peut ensuite le filtrer. Si le réseau exige une politique de refus par défaut, supprimer ce permis général et définir explicitement les flux nécessaires. Il faut également vérifier que les réponses serveur passent par un chemin qui les autorise. Une ACL de transit stateless ne fournit pas d’inspection de session.

### 2.2 Configuration par liste positive

Une liste positive n’autorise que les flux explicitement prévus. Elle est souvent plus facile à auditer qu’une longue liste de refus suivie d’un `permit ip any any`.

```cisco
ip access-list extended APP-ALLOWLIST
 remark Clients vers application TLS
 permit tcp 10.20.10.0 0.0.0.255 host 10.20.30.20 eq 443
 remark Clients vers DNS interne
 permit udp 10.20.10.0 0.0.0.255 host 10.20.30.53 eq 53
 permit tcp 10.20.10.0 0.0.0.255 host 10.20.30.53 eq 53
 remark Journaliser le trafic non prévu
 deny ip any any log
```

Le journal `log` ne doit pas être ajouté sans réflexion à une règle susceptible de correspondre à un volume massif. La génération excessive de messages peut surcharger le plan de contrôle, la console ou le collecteur Syslog. Utiliser des compteurs, des périodes d’observation et des règles de journalisation ciblées.

### 2.3 Contrôle de l’administration VTY

Pour restreindre les connexions SSH vers le routeur depuis un réseau d’administration :

```cisco
ip access-list standard MGMT-SSH-SOURCES
 permit 10.20.99.0 0.0.0.255
 deny any log
!
line vty 0 15
 access-class MGMT-SSH-SOURCES in
 transport input ssh
```

La disponibilité de `line vty 0 15` et les numéros de lignes dépendent du modèle. Vérifier aussi la configuration SSH, les utilisateurs locaux ou AAA, les clés, les timeouts et le routage de retour. Une ACL VTY n’est pas la même chose qu’une ACL attachée à une interface.

### 2.4 ACL et NAT

Exemple de PAT pour le réseau utilisateurs :

```cisco
ip access-list standard NAT-USERS
 permit 10.20.10.0 0.0.0.255
!
interface GigabitEthernet0/0
 description LAN
 ip nat inside
!
interface GigabitEthernet0/1
 description WAN
 ip nat outside
!
ip nat inside source list NAT-USERS interface GigabitEthernet0/1 overload
```

Ici, l’ACL `NAT-USERS` sélectionne les sources à traduire. Elle ne filtre pas à elle seule les paquets. Si une règle NAT ne fonctionne pas, vérifier le sens inside/outside, la route de sortie, la correspondance de l’ACL, les traductions existantes et le trafic retour.

### 2.5 ACL et PBR : classifier sans confondre les actions

Exemple conceptuel :

```cisco
ip access-list extended TRAFIC-CRITIQUE
 permit ip 10.20.10.0 0.0.0.255 host 10.20.40.10
!
route-map PBR-APP permit 10
 match ip address TRAFIC-CRITIQUE
 set ip next-hop 10.20.99.1
!
interface GigabitEthernet0/0
 ip policy route-map PBR-APP
```

La disponibilité et la syntaxe exacte dépendent de la plateforme. Dans ce contexte, l’ACL classe le trafic qui doit recevoir la politique PBR. Une entrée `deny` dans l’ACL de classification signifie généralement que le paquet ne correspond pas à cette classe ; elle ne doit pas être interprétée automatiquement comme un refus de transfert. Tester aussi le comportement lorsque le prochain saut PBR est indisponible.

### 2.6 Modification contrôlée et retour arrière

Avant toute modification :

1. exporter la configuration actuelle ;
2. enregistrer la sortie de `show access-lists`, `show ip interface` et `show running-config`;
3. identifier toutes les interfaces, SVI, sous-interfaces et VTY utilisant la liste ;
4. vérifier les chemins aller et retour ;
5. préparer les tests autorisés et les tests devant échouer ;
6. disposer d’un accès hors bande ou d’une méthode de récupération.

Commandes utiles :

```cisco
show access-lists
show ip access-lists
show ip interface
show running-config | section access-list
show running-config | section interface
show logging
```

La syntaxe de filtrage de la configuration dépend de la version IOS/IOS XE. Après modification, contrôler les compteurs et tester chaque flux. Ne pas se limiter à `ping` : tester le protocole applicatif, les réponses, les chemins alternatifs et le comportement lors d’une panne.

> **Astuce :** Avant d’attacher une ACL à une interface distante, prépare une ACE de gestion qui conserve l’accès depuis le réseau d’administration, puis vérifie le plan de retour arrière. Pour les changements critiques, utiliser une fenêtre de maintenance, une session console/hors bande et un test automatisé des flux autorisés et interdits.

---

## 3. Dépannage et sécurité

### 3.1 Méthode de diagnostic

Suivre un ordre déterministe :

1. **Définir le flux** : source, destination, protocole, ports, sens d’initiation et réponse attendue.
2. **Tracer le chemin** : VLAN, SVI, interfaces d’entrée et de sortie, tunnels, NAT, routeur et destination.
3. **Localiser l’ACL** : nom, direction, famille IP, fonction consommatrice.
4. **Vérifier l’ordre** : première ACE correspondante et éventuel refus implicite.
5. **Lire les compteurs** : identifier les entrées qui augmentent pendant un test contrôlé.
6. **Comparer aller/retour** : une requête autorisée ne garantit pas la réponse.
7. **Vérifier les fonctions adjacentes** : routage, NAT, PBR, QoS, MTU, pare-feu, contrôle de plan.
8. **Confirmer le résultat** avec une capture ou les compteurs appropriés.

Commandes de base :

```cisco
show access-lists
show ip access-lists USERS-TO-SERVERS
show ip interface GigabitEthernet0/0
show ip route 10.20.30.20
show ip cef 10.20.30.20
show logging
```

Certaines commandes et options ne sont pas disponibles sur toutes les plateformes. Les commandes de capture ou de débogage peuvent avoir un impact important : éviter un `debug` large sur un routeur chargé sans contrôle du débit, filtre précis et plan d’arrêt.

### 3.2 Symptômes fréquents

| Symptôme | Causes probables | Vérifications |
|---|---|---|
| Tout le trafic est bloqué | Refus implicite, mauvais ordre, ACL appliquée au mauvais endroit | `show access-lists`, direction, compteurs |
| Une application échoue, ping fonctionne | Port/protocole absent, TCP retour, inspection applicative | Tester port et session, capture |
| Un flux fonctionne dans un sens | ACL stateless, routage asymétrique, chemin retour différent | Tracer les deux directions |
| Une règle ne compte jamais | Mauvaise interface, mauvaise direction, ACE précédente plus large | Topologie et ordre des ACE |
| Des pannes intermittentes | Chemins ECMP, interfaces multiples, ACL différentes, mise à jour de TCAM | Comparer chaque chemin et l’état matériel |
| IPv6 échoue après filtrage | ICMPv6/NDP ou Packet Too Big bloqué | Vérifier les types ICMPv6 nécessaires |
| NAT ne traduit plus | ACL de sélection NAT modifiée ou mal comprise | Distinguer classification NAT et filtrage |
| Le routeur perd ses voisinages | ACL de transit ou de control plane bloque les protocoles | Vérifier OSPF/EIGRP/BGP et les interfaces |

### 3.3 Journalisation : valeur et risques

`log` et `log-input` peuvent fournir des informations utiles selon la plateforme, mais la journalisation des paquets est une opération coûteuse. Elle peut produire un volume élevé, consommer des ressources du plan de contrôle et saturer les systèmes de collecte.

Bonnes pratiques :

- journaliser les refus significatifs plutôt que tous les paquets d’un flux volumineux ;
- utiliser les compteurs comme première source d’observation ;
- éviter de journaliser chaque paquet d’un trafic normal et intense ;
- définir des limites de débit lorsque la plateforme le permet ;
- centraliser les journaux, synchroniser les horloges et contrôler les accès ;
- tenir compte des données sensibles exposées dans les adresses et métadonnées ;
- tester l’effet de la journalisation sous charge.

Une ACL avec `deny ip any any log` peut être utile pour une politique à faible volume, mais dangereuse sur une interface Internet à haut débit sans mécanisme de limitation adapté.

### 3.4 Sécurisation du plan d’administration

L’accès administratif doit être limité à des sous-réseaux ou bastions dédiés. Une ACL VTY peut restreindre les sources, mais elle ne remplace pas :

- SSH plutôt que Telnet ;
- AAA et comptes nominatifs ;
- authentification multifacteur via les systèmes de gestion lorsque possible ;
- limitation des services activés ;
- contrôle des accès SNMP et des API ;
- journalisation et synchronisation horaire ;
- accès hors bande et procédures de secours ;
- séparation du réseau d’administration du trafic utilisateur.

Éviter de compter uniquement sur une ACL qui filtre l’adresse source : une adresse source peut être usurpée dans certains contextes, et une source autorisée peut être compromise.

### 3.5 Risques de politique

**Règles trop larges.** `permit ip any any` peut rendre inopérantes les restrictions placées après lui. Un permis général doit être une décision explicite et documentée.

**Objets mal définis.** Les adresses de documentation, les plages obsolètes et les sous-réseaux qui se chevauchent provoquent des correspondances inattendues.

**Changements non atomiques.** Remplacer une ACL en plusieurs étapes peut créer une fenêtre où le trafic est trop permissif ou trop restrictif. Préparer les séquences et les tests avant l’application.

**Asymétrie.** Le flux aller et le flux retour peuvent traverser des interfaces différentes, notamment avec ECMP, des chemins WAN redondants ou des architectures multi-sites.

**Faux sentiment de sécurité.** Une ACL de paquet n’inspecte pas nécessairement le contenu applicatif, l’identité de l’utilisateur ou l’état de la session. Pour ces objectifs, utiliser des contrôles adaptés.

> **Danger :** Une ACL mal ordonnée ou attachée dans le mauvais sens peut couper l’accès d’administration au routeur, interrompre les protocoles de routage et provoquer une panne à grande échelle. À l’inverse, une ACE générale trop permissive peut annuler toute la politique de moindre privilège. Tout changement de filtrage doit inclure sauvegarde, accès de secours, tests positifs/négatifs et procédure de retour arrière.

### 3.6 Matrice de tests recommandée

Une politique doit être validée par un jeu de tests reproductible. Exemple :

| Source | Destination | Service | Résultat attendu |
|---|---|---|---|
| VLAN utilisateurs | Serveur applicatif | TCP/443 | Autorisé |
| VLAN utilisateurs | DNS interne | UDP/53 | Autorisé |
| VLAN utilisateurs | DNS interne | TCP/53 | Autorisé si requis |
| VLAN utilisateurs | Serveur applicatif | TCP/22 | Refusé |
| VLAN invités | Réseau de gestion | Tout | Refusé |
| Bastion d’administration | Routeur | SSH/22 | Autorisé |
| Hôte non autorisé | Routeur | SSH/22 | Refusé |
| Hôte IPv6 | Services réseau nécessaires | ICMPv6/NDP | Autorisé selon le rôle |
| Flux non documenté | Réseau protégé | Tout | Refusé par défaut si politique positive |

Tester aussi les paquets fragmentés si l’environnement en dépend, les réponses TCP/UDP, les erreurs ICMP nécessaires, les chemins redondants et les changements de route.

### 3.7 Documentation et gouvernance

Chaque ACL de production devrait avoir :

- un nom indiquant l’usage et le sens ;
- un propriétaire métier et technique ;
- une justification de chaque exception ;
- des adresses et services associés à des objets ou à un inventaire ;
- une date de revue et une durée de validité pour les exceptions temporaires ;
- des tests automatisés ou une matrice de validation ;
- une procédure d’approbation ;
- un plan de retour arrière ;
- une surveillance des compteurs et des refus anormaux.

Les règles inutilisées ne doivent pas être supprimées sur la seule base d’un compteur nul observé pendant une courte période. Il peut s’agir d’un flux rare mais critique. Corréler les compteurs avec les périodes d’activité et les propriétaires de service.

---

## Points à retenir

- Une ACL classique évalue les ACE dans l’ordre et s’arrête à la première correspondance ; tout trafic qui ne correspond à aucune entrée est refusé implicitement dans une ACL de filtrage classique.
- Une ACL stateless n’établit pas automatiquement l’état des sessions : le trafic retour doit être conçu explicitement ou confié à un mécanisme d’inspection stateful.
- Le placement `in`/`out` dépend du chemin réel du paquet, de la décision de routage et de l’interface où l’ACL est appliquée.
- Les wildcard masks Cisco indiquent les bits ignorés ; pour un hôte unique, utiliser `host` ou `0.0.0.0`.
- Une ACL utilisée par NAT, PBR ou QoS peut être un classificateur : `permit` n’a alors pas nécessairement le sens « autoriser le paquet ».
- ICMP et ICMPv6 ne doivent pas être bloqués aveuglément ; les erreurs de transport, PMTUD et NDP peuvent être essentiels.
- Les ACL IPv4 et IPv6 doivent être traitées comme des politiques distinctes et validées séparément.
- Les ACE avec journalisation doivent être limitées et surveillées pour éviter de surcharger le plan de contrôle.
- Sur les équipements matériels, contrôler les ressources ACL/TCAM et la programmation effective de la politique.
- Tout changement en production doit être sauvegardé, testé dans les deux sens et accompagné d’un plan de retour arrière.

### Références techniques

- Cisco, *Configuring IP Access Lists* : https://www.cisco.com/c/en/us/support/docs/security/ios-firewall/23602-confaccesslists.html
- Cisco, documentation de configuration IOS/IOS XE : https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-xe/series.html
- IETF, RFC 1812 — *Requirements for IP Version 4 Routers* : https://www.rfc-editor.org/rfc/rfc1812
- IETF, RFC 4301 — *Security Architecture for the Internet Protocol* : https://www.rfc-editor.org/rfc/rfc4301
- IETF, RFC 4890 — *Recommendations for Filtering ICMPv6 Messages in Firewalls* : https://www.rfc-editor.org/rfc/rfc4890
- IETF, RFC 8200 — *Internet Protocol, Version 6 (IPv6) Specification* : https://www.rfc-editor.org/rfc/rfc8200
- IETF, RFC 2979 — *Behavior of and Requirements for Internet Firewalls* : https://www.rfc-editor.org/rfc/rfc2979

> **Astuce :** Pour chaque ACE, documenter en une phrase son intention, le flux qu’elle doit autoriser ou bloquer, et le test qui démontre son comportement. Une ACL est plus facile à maintenir quand chaque entrée a une raison vérifiable plutôt qu’une simple description syntaxique.
