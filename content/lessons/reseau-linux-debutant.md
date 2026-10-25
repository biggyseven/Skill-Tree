# Maîtriser le réseau sous Linux : adressage, configuration et dépannage

> **Niveau :** Débutant  
> **Domaine :** Administration Linux et réseaux informatiques  
> **Environnement :** Linux, terminal Bash, commandes réseau, Netplan et NetworkManager  
> **Prérequis :** savoir utiliser un terminal, se déplacer dans les répertoires et exécuter des commandes Linux  
> **Objectif :** comprendre le fonctionnement du réseau sous Linux, configurer une interface réseau, obtenir une adresse IP, définir une passerelle et des serveurs DNS, puis diagnostiquer les problèmes de connectivité.


# 1. Objectifs pédagogiques

Un administrateur Linux doit savoir comprendre et configurer les interfaces réseau, vérifier les paramètres d'adressage et identifier la cause d'une panne.

Ce cours vous apprend à :

- comprendre les composants du réseau d'une machine Linux ;
- différencier adresse IP, adresse MAC, masque, préfixe, passerelle, route et DNS ;
- identifier les interfaces Ethernet, Wi-Fi et virtuelles ;
- utiliser les commandes `ip`, `ping`, `ip route`, `ip neigh`, `ss` et `getent` ;
- comprendre DHCP et l'adressage IP statique ;
- configurer une interface avec Netplan ;
- utiliser `netplan generate`, `netplan try` et `netplan apply` ;
- comprendre le rôle de NetworkManager ;
- afficher, créer, modifier et activer un profil réseau avec `nmcli` ;
- configurer le Wi-Fi depuis le terminal ;
- vérifier la connectivité locale, la passerelle, Internet et la résolution DNS ;
- reconnaître les problèmes liés aux routes, aux DNS, aux interfaces et aux services réseau ;
- éviter les erreurs susceptibles de couper une connexion SSH ;
- réaliser un diagnostic méthodique plutôt que modifier les paramètres au hasard.

Le cours couvre les opérations fondamentales de diagnostic et de configuration. Les VLAN, bridges, bonds, VPN, politiques de routage avancées, pare-feu complexes et architectures haute disponibilité seront approfondis dans les niveaux suivants.

# 2. Comprendre le réseau sous Linux

## 2.1. Qu'est-ce qu'un réseau informatique ?

Un réseau informatique permet à plusieurs équipements d'échanger des données.

Exemples d'équipements :

- ordinateurs ;
- serveurs Linux ;
- imprimantes réseau ;
- routeurs ;
- commutateurs ;
- points d'accès Wi-Fi ;
- machines virtuelles ;
- conteneurs.

Une machine Linux peut communiquer avec plusieurs catégories de destinations :

- sa propre machine ;
- d'autres équipements du même réseau local ;
- des réseaux distants ;
- des services accessibles par Internet.

Pour cela, elle utilise une interface réseau, une configuration IP et des mécanismes de routage.

## 2.2. Le chemin général d'une communication

Imaginons qu'un serveur Linux souhaite joindre un autre serveur.

```text
+---------------------------+
| Serveur Linux A           |
| IP : 192.168.10.20/24     |
+---------------------------+
              |
              | Interface réseau
              v
+---------------------------+
| Réseau local              |
| 192.168.10.0/24           |
+---------------------------+
              |
              v
+---------------------------+
| Passerelle / Routeur      |
| 192.168.10.1              |
+---------------------------+
              |
              | Routage
              v
+---------------------------+
| Réseau distant            |
| 192.168.20.0/24           |
+---------------------------+
              |
              v
+---------------------------+
| Serveur Linux B           |
| IP : 192.168.20.30        |
+---------------------------+
```

Ces adresses constituent un exemple de laboratoire. Elles doivent être adaptées au réseau réellement utilisé.

La machine A utilise son adresse IP et sa table de routage pour déterminer où envoyer les paquets.

Si la destination appartient au réseau local, elle peut communiquer directement avec elle, sous réserve que le réseau de niveau liaison le permette.

Si la destination est distante, elle transmet généralement les paquets à une passerelle.

## 2.3. La pile réseau sous Linux

Plusieurs composants interviennent dans une communication.

```text
Application
    |
    | HTTP, SSH, DNS, etc.
    v
Couche transport
    |
    | TCP ou UDP
    v
Couche réseau
    |
    | IPv4 ou IPv6
    v
Couche liaison
    |
    | Ethernet ou Wi-Fi
    v
Interface réseau
    |
    v
Réseau physique ou virtuel
```

La pile réseau du noyau Linux traite les paquets et applique notamment les règles d'adressage, de routage et de filtrage.

Des services complémentaires gèrent la configuration des interfaces, la résolution des noms, les connexions Wi-Fi et les paramètres transmis par DHCP.

## 2.4. Qui fait quoi ?

| Composant | Rôle |
|---|---|
| Noyau Linux | traite les interfaces, les adresses IP, les routes et les paquets |
| Pilote réseau | permet au noyau de communiquer avec le matériel ou le périphérique virtuel |
| NetworkManager | gère les connexions réseau et leurs profils |
| Netplan | décrit une configuration réseau dans des fichiers YAML et la transmet à un service de gestion compatible |
| systemd-networkd | gère certaines configurations réseau sur les systèmes utilisant ce service |
| Résolveur DNS | traduit les noms de domaine en informations réseau, notamment en adresses IP |
| DHCP | attribue automatiquement des paramètres réseau |
| `ip` | affiche et manipule les interfaces, adresses, routes et voisins réseau |
| `nmcli` | pilote NetworkManager depuis le terminal |

Ces composants ont des responsabilités complémentaires. Ils ne sont pas tous actifs sur chaque distribution.


# 3. Comprendre les interfaces réseau

## 3.1. Qu'est-ce qu'une interface réseau ?

Une interface réseau est le point par lequel Linux envoie et reçoit des données.

Elle peut correspondre à :

- une carte Ethernet physique ;
- une carte Wi-Fi ;
- une interface virtuelle de machine virtuelle ;
- une interface de pont (*bridge*) ;
- une interface VPN ;
- une interface de conteneur ;
- une interface de boucle locale.

Exemples de noms :

```text
lo
enp0s3
ens18
eno1
wlp2s0
docker0
virbr0
```

Ces noms dépendent du système, des pilotes et de l'environnement. Ne supposez pas que toutes les machines possèdent une interface appelée `eth0`.

## 3.2. L'interface de boucle locale `lo`

L'interface `lo` représente la boucle locale.

Elle permet à une machine de communiquer avec elle-même sans passer par une carte réseau physique.

Adresse IPv4 habituelle :

```text
127.0.0.1
```

Adresse IPv6 de boucle locale :

```text
::1
```

Exemple :

```bash
ping -c 3 127.0.0.1
```

Cette commande teste la communication IPv4 de boucle locale.

Si elle réussit, cela confirme une partie du fonctionnement de la pile réseau locale. Cela ne prouve pas que la carte Ethernet ou la connexion Internet fonctionne.

## 3.3. Identifier les interfaces

Commande :

```bash
ip link show
```

Exemple de sortie simplifiée :

```text
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
3: wlp2s0: <BROADCAST,MULTICAST> mtu 1500
```

Interprétation :

- `lo` est la boucle locale ;
- `enp0s3` peut être une interface Ethernet ;
- `wlp2s0` peut être une interface Wi-Fi ;
- `UP` indique un état administratif actif ;
- `LOWER_UP` indique généralement que la couche physique ou la liaison est détectée comme opérationnelle ;
- `mtu` représente la taille maximale d'un paquet de niveau réseau que l'interface peut transporter sans fragmentation à ce niveau, selon la configuration.

L'absence de `LOWER_UP` sur une interface Ethernet peut révéler un problème de câble, de commutateur, de pilote ou de liaison. Mais le diagnostic doit tenir compte du type d'interface.

## 3.4. Afficher uniquement les noms

```bash
ip -o link show
```

Pour extraire les noms avec les outils usuels :

```bash
ip -o link show | awk -F': ' '{print $2}'
```

Cette forme sert à afficher une liste rapide. Pour des scripts d'administration robustes, préférez les sorties structurées lorsque l'outil en propose, ou les interfaces programmatiques appropriées.

## 3.5. Comprendre la différence entre l'état administratif et l'état de liaison

```text
Interface activée administrativement ?
                |
           +----+----+
           |         |
          Non       Oui
           |         |
           v         v
   Pas de trafic    Liaison détectée ?
                     |
                +----+----+
                |         |
               Non       Oui
                |         |
                v         v
         Vérifier la     Continuer le
         liaison         diagnostic IP
```

Une interface peut être administrativement activée sans posséder de liaison physique opérationnelle.

Inversement, une liaison physique active ne garantit ni une adresse IP correcte, ni une route valide, ni l'accès à Internet.


# 4. Adresses MAC et adresses IP

## 4.1. Adresse MAC

Une adresse MAC identifie une interface au niveau de la liaison réseau, notamment dans les réseaux Ethernet.

Exemple :

```text
00:11:22:33:44:55
```

Une adresse MAC comporte habituellement 48 bits pour Ethernet.

Elle est utilisée dans les communications de niveau liaison. Elle n'est pas l'adresse de routage utilisée pour joindre des réseaux IP distants.

Attention : une adresse MAC peut être modifiée ou usurpée dans certaines configurations. Elle ne constitue pas une preuve d'identité ou une garantie de sécurité.

## 4.2. Adresse IPv4

Une adresse IPv4 possède 32 bits et est généralement écrite sous la forme de quatre nombres décimaux séparés par des points.

Exemple :

```text
192.168.10.20
```

Chaque nombre est compris entre `0` et `255`.

Une adresse IP identifie une destination ou une interface dans un contexte réseau. Son interprétation dépend aussi du préfixe et du routage.

## 4.3. Adresse IPv6

IPv6 utilise des adresses de 128 bits.

Exemple :

```text
2001:db8:10::20
```

Le préfixe `2001:db8::/32` est réservé à la documentation. Cette adresse illustre le format IPv6 sans désigner une machine publique réelle.

IPv6 prend en charge un espace d'adressage bien plus vaste qu'IPv4.

Les adresses IPv6 peuvent être attribuées par différents mécanismes, notamment configuration manuelle, DHCPv6 et autoconfiguration sans état selon l'environnement.

## 4.4. Afficher les adresses d'une machine

```bash
ip address show
```

Forme condensée :

```bash
ip -br address
```

Exemple fictif :

```text
lo       UNKNOWN  127.0.0.1/8 ::1/128
enp0s3   UP       192.168.10.20/24
```

La machine possède ici :

- l'adresse IPv4 de boucle locale `127.0.0.1` ;
- l'adresse `192.168.10.20/24` sur `enp0s3`.

Le statut affiché dépend de l'interface et de l'environnement. Le mot `UNKNOWN` sur certaines interfaces virtuelles ne signifie pas obligatoirement qu'elles sont inutilisables.


# 5. Masque de sous-réseau et préfixe CIDR

## 5.1. Pourquoi associer une adresse à un préfixe ?

Une adresse IP ne suffit pas pour déterminer quelles destinations sont directement accessibles sur le réseau local.

Il faut aussi un préfixe réseau.

Exemple :

```text
192.168.10.20/24
```

- `192.168.10.20` est l'adresse de l'interface ;
- `/24` indique que les 24 premiers bits constituent le préfixe du réseau.

Le masque IPv4 équivalent est :

```text
255.255.255.0
```

Le réseau correspondant est :

```text
192.168.10.0/24
```

Pour ce sous-réseau IPv4 classique, la plage d'adresses d'hôtes utilisables est généralement `192.168.10.1` à `192.168.10.254`, avec `192.168.10.0` comme identifiant de réseau et `192.168.10.255` comme adresse de diffusion.

Il existe cependant des préfixes particuliers, comme `/31` pour certaines liaisons point à point, qui ne suivent pas la même règle traditionnelle de réservation des adresses réseau et de diffusion.

## 5.2. Comprendre la notation CIDR

CIDR signifie *Classless Inter-Domain Routing*.

Le nombre après `/` indique la longueur du préfixe.

| Préfixe | Masque IPv4 équivalent | Nombre total d'adresses |
|---|---|---:|
| `/8` | `255.0.0.0` | 16 777 216 |
| `/16` | `255.255.0.0` | 65 536 |
| `/24` | `255.255.255.0` | 256 |
| `/25` | `255.255.255.128` | 128 |
| `/26` | `255.255.255.192` | 64 |
| `/27` | `255.255.255.224` | 32 |

Le nombre d'adresses d'hôtes utilisables dépend du préfixe et du type de réseau. Pour les sous-réseaux IPv4 classiques, on réserve normalement l'adresse du réseau et l'adresse de diffusion.

## 5.3. Exemple : comprendre `/24`

Supposons :

```text
IP :      192.168.10.20/24
Réseau :  192.168.10.0/24
Masque :  255.255.255.0
```

Deux machines ayant les adresses `192.168.10.20/24` et `192.168.10.30/24` appartiennent normalement au même sous-réseau IPv4.

Une machine possédant `192.168.20.30/24` appartient à un autre sous-réseau.

Pour communiquer, elles devront utiliser une passerelle ou un autre mécanisme de routage approprié.

## 5.4. Réseaux privés IPv4

Les plages privées courantes définies par RFC 1918 sont :

| Plage | Préfixe |
|---|---|
| `10.0.0.0` à `10.255.255.255` | `10.0.0.0/8` |
| `172.16.0.0` à `172.31.255.255` | `172.16.0.0/12` |
| `192.168.0.0` à `192.168.255.255` | `192.168.0.0/16` |

Ces adresses sont couramment utilisées sur les réseaux locaux, les entreprises et les réseaux virtuels.

Une adresse privée n'est pas directement routable sur l'Internet public. L'accès à Internet nécessite généralement une traduction d'adresses (NAT) ou une autre architecture de connectivité.

## 5.5. Adresses particulières

| Adresse | Usage |
|---|---|
| `127.0.0.1` | boucle locale IPv4 |
| `127.0.0.0/8` | plage de boucle locale IPv4 |
| `169.254.0.0/16` | adressage link-local IPv4 |
| `0.0.0.0/0` | route IPv4 par défaut |
| `::1` | boucle locale IPv6 |
| `fe80::/10` | plage IPv6 link-local |
| `::/0` | route IPv6 par défaut |

Une adresse `169.254.x.x` peut apparaître lorsque l'interface utilise un mécanisme d'adressage link-local, notamment en l'absence de configuration IPv4 habituelle. Sa présence n'indique pas à elle seule la cause exacte du problème.


# 6. Passerelle, routage et communication entre réseaux

## 6.1. Qu'est-ce qu'une passerelle ?

Une passerelle est un équipement qui permet à une machine de communiquer avec des réseaux qui ne sont pas directement joignables sur son réseau local.

Dans de nombreux réseaux, elle correspond à l'adresse LAN d'un routeur.

Exemple :

```text
Machine Linux
IP : 192.168.10.20/24
       |
       v
Réseau local : 192.168.10.0/24
       |
       v
Routeur
IP locale : 192.168.10.1
       |
       v
Autres réseaux / Internet
```

La passerelle doit être joignable par une route appropriée. Configurer une adresse de passerelle incorrecte peut empêcher l'accès aux destinations distantes.

## 6.2. Qu'est-ce qu'une table de routage ?

La table de routage indique au système où envoyer les paquets destinés à différentes destinations.

Afficher les routes IPv4 :

```bash
ip route show
```

Afficher les routes IPv6 :

```bash
ip -6 route show
```

Exemple fictif :

```text
default via 192.168.10.1 dev enp0s3
192.168.10.0/24 dev enp0s3 proto kernel scope link src 192.168.10.20
```

Interprétation :

- `default` correspond à la route utilisée pour les destinations qui ne correspondent pas à une route plus spécifique ;
- `via 192.168.10.1` indique la passerelle ;
- `dev enp0s3` indique l'interface utilisée ;
- `192.168.10.0/24` est le réseau directement connecté.

## 6.3. Comprendre la route par défaut

Une machine peut posséder plusieurs routes vers différents réseaux. La route par défaut sert lorsque les routes plus spécifiques ne couvrent pas la destination.

```text
Destination demandée
        |
        v
La table de routage possède-t-elle
une route plus spécifique ?
        |
    +---+---+
    |       |
   Oui      Non
    |       |
    v       v
Utiliser   Utiliser la route
la route   par défaut si elle
spécifique existe
```

Une machine sans route par défaut peut quand même communiquer avec son réseau local ou avec certains réseaux plus spécifiques.

L'absence de route par défaut n'est donc pas automatiquement une panne, notamment dans les architectures à plusieurs interfaces.

## 6.4. Vérifier la route vers une destination

```bash
ip route get 1.1.1.1
```

Cette commande demande au noyau quelle route serait utilisée pour joindre l'adresse indiquée.

Exemple de sortie possible :

```text
1.1.1.1 via 192.168.10.1 dev enp0s3 src 192.168.10.20
```

Cet exemple indique une route via la passerelle `192.168.10.1`, une sortie par `enp0s3` et une adresse source `192.168.10.20`.

La commande vérifie une décision de routage locale. Elle ne garantit pas que la destination répondra.


# 7. DHCP et adressage statique

## 7.1. Qu'est-ce que DHCP ?

DHCP signifie *Dynamic Host Configuration Protocol*.

Ce protocole permet à un serveur DHCP d'attribuer automatiquement des paramètres réseau à un client.

Selon le réseau, le client peut obtenir :

- une adresse IP ;
- un préfixe ou masque ;
- une passerelle ;
- des serveurs DNS ;
- une durée de validité du bail ;
- d'autres paramètres.

## 7.2. Déroulement simplifié de DHCPv4

```text
Client Linux                     Serveur DHCP
     |                                |
     |------ DHCPDISCOVER ----------->|
     |                                |
     |<--------- DHCPOFFER ------------|
     |                                |
     |------ DHCPREQUEST ------------>|
     |                                |
     |<--------- DHCPACK --------------|
     |                                |
     v                                v
Adresse et paramètres attribués
```

Ce schéma représente le mécanisme courant d'obtention d'un bail IPv4. Les messages exacts échangés dépendent de l'état du client et du protocole.

## 7.3. Avantages de DHCP

DHCP est pratique pour :

- les postes utilisateurs ;
- les ordinateurs portables ;
- les machines virtuelles ;
- les réseaux de laboratoire ;
- les infrastructures où les paramètres réseau sont centralisés.

Il réduit la configuration manuelle et limite certains risques d'erreurs d'adressage.

## 7.4. Qu'est-ce qu'une adresse statique ?

Une adresse statique est définie explicitement dans la configuration de la machine ou de son gestionnaire réseau.

Exemple :

```text
Adresse :   192.168.10.20/24
Passerelle : 192.168.10.1
DNS :       192.168.10.1
```

Cette configuration peut être adaptée à un serveur qui doit conserver une adresse prévisible.

Avant de définir une adresse statique, vérifiez qu'elle appartient au bon sous-réseau, qu'elle n'est pas déjà utilisée et que son affectation respecte le plan d'adressage.

## 7.5. Réserver une adresse DHCP ou la configurer statiquement ?

Les deux solutions peuvent produire un résultat stable, mais elles ne fonctionnent pas de la même manière.

Une réservation DHCP associe généralement un client à une adresse déterminée par le serveur DHCP.

Une configuration statique définit l'adresse sur la machine elle-même.

Dans un environnement administré, la réservation DHCP peut être préférable si le réseau centralise les allocations. Il faut toutefois tenir compte des politiques de sécurité, des habitudes d'exploitation et de la disponibilité du service DHCP.


# 8. DNS : résoudre les noms de domaine

## 8.1. Qu'est-ce que DNS ?

DNS signifie *Domain Name System*.

Il permet notamment de traduire des noms comme :

```text
example.com
```

en adresses IP.

Une application peut demander à Linux de résoudre un nom, puis utiliser l'adresse obtenue pour établir sa connexion.

## 8.2. Chaîne simplifiée d'une résolution

```text
Application
    |
    | demande la résolution d'un nom
    v
Résolveur local / configuration système
    |
    v
Serveur DNS ou cache
    |
    v
Réponse : adresse IP ou résultat DNS
    |
    v
Application
    |
    v
Connexion réseau vers l'adresse obtenue
```

Le chemin réel dépend du résolveur local, des caches, de la configuration DNS et de l'application.

## 8.3. Pourquoi Internet peut fonctionner par IP mais pas par nom ?

Supposons que cette commande reçoive une réponse :

```bash
ping -c 3 1.1.1.1
```

Mais que cette commande échoue :

```bash
getent hosts example.com
```

Cela peut signaler un problème DNS, car la connectivité vers une adresse IP ne prouve pas que la résolution des noms fonctionne.

Il faut également tenir compte des règles de filtrage, du routage et du comportement du service testé.

## 8.4. Voir les DNS utilisés

Sur les systèmes utilisant systemd-resolved :

```bash
resolvectl status
```

Cette commande affiche les informations du résolveur et peut présenter les DNS associés à chaque interface.

Autre commande utile :

```bash
cat /etc/resolv.conf
```

Ce fichier peut être géré automatiquement ou pointer vers un résolveur local. Son contenu dépend de la distribution et de la configuration.

Ne modifiez pas directement ce fichier sans comprendre le composant qui le gère. Une modification manuelle peut être remplacée automatiquement et ne pas persister.

## 8.5. Tester la résolution

```bash
getent hosts example.com
```

`getent` utilise les mécanismes de résolution du système, ce qui permet de tester le chemin généralement employé par de nombreuses applications.

Si `dig` est installé :

```bash
dig example.com
```

Cette commande est utile pour analyser les réponses DNS. Sa disponibilité dépend des paquets installés.


# 9. Les outils fondamentaux de diagnostic

## 9.1. `ip`

La commande `ip`, fournie par les outils iproute2, est l'un des principaux outils de diagnostic du réseau Linux.

Commandes courantes :

```bash
ip link show
ip address show
ip route show
ip neigh show
```

Elles permettent respectivement de consulter :

- les interfaces ;
- les adresses ;
- les routes ;
- la table des voisins.

La commande `ip` remplace, dans de nombreux usages modernes, les anciens outils `ifconfig` et `route`.

## 9.2. `ping`

`ping` permet d'envoyer des requêtes ICMP Echo Request à une destination et de recevoir les éventuelles réponses.

```bash
ping -c 4 192.168.10.1
```

L'option `-c 4` limite le nombre de requêtes à quatre sur les systèmes usuels qui proposent cette option.

Si la passerelle répond, cela apporte une preuve de connectivité IP vers cette passerelle.

Cependant, un serveur peut filtrer ICMP tout en acceptant d'autres communications. L'absence de réponse à `ping` n'est donc pas une preuve absolue d'indisponibilité.

## 9.3. `ip neigh`

```bash
ip neigh show
```

Cette commande affiche les informations relatives aux voisins connus sur les réseaux locaux.

En IPv4, le système utilise généralement ARP pour associer une adresse IP locale à une adresse MAC. En IPv6, Neighbor Discovery joue un rôle équivalent dans plusieurs mécanismes.

Si un voisin reste dans un état tel que `FAILED` ou demeure inaccessible, cela peut révéler un problème de liaison ou d'adressage, mais le contexte doit être vérifié.

## 9.4. `ss`

La commande `ss` affiche des informations sur les sockets, notamment les connexions et les ports d'écoute.

```bash
ss -tuln
```

Signification des options courantes :

- `-t` : sockets TCP ;
- `-u` : sockets UDP ;
- `-l` : sockets en écoute ;
- `-n` : affiche les numéros sans résolution de noms.

Pour examiner les connexions et les processus associés, selon les permissions disponibles :

```bash
sudo ss -tulpn
```

La commande ne modifie pas les paramètres du réseau. Elle permet de diagnostiquer les services qui écoutent ou les sockets actives.

## 9.5. `ip -br address`

```bash
ip -br address
```

Cette commande permet une lecture rapide des interfaces et des adresses.

Elle est particulièrement utile au début d'un diagnostic.

## 9.6. `resolvectl`

```bash
resolvectl status
resolvectl query example.com
```

La disponibilité et le comportement de ces commandes dépendent de la présence et de la configuration de systemd-resolved.

Si `resolvectl` n'est pas disponible, utilisez les outils de résolution fournis par votre distribution.

## 9.7. `curl`

Pour tester un service HTTP ou HTTPS :

```bash
curl -I https://example.com
```

Cette commande tente de demander les en-têtes d'une ressource HTTP.

Une erreur peut provenir de plusieurs causes : DNS, routage, pare-feu, proxy, certificat TLS ou indisponibilité du service. Il faut examiner le message exact.

## 9.8. Un diagnostic ne doit pas dépendre d'une seule commande

La commande suivante ne suffit pas pour vérifier l'ensemble du réseau :

```bash
ping -c 3 1.1.1.1
```

Une machine peut répondre à `ping` mais ne pas pouvoir résoudre les noms ou établir une connexion HTTPS.

Un diagnostic fiable combine plusieurs observations.


# 10. Reconnaître le gestionnaire réseau utilisé

C'est l'une des étapes les plus importantes avant de modifier la configuration.

Toutes les distributions Linux ne gèrent pas le réseau de la même manière.

## 10.1. Cas courants

| Environnement | Gestion possible |
|---|---|
| Ubuntu Server récent | Netplan avec `systemd-networkd` ou NetworkManager |
| Ubuntu Desktop | Netplan et NetworkManager selon la configuration |
| Debian | NetworkManager, `ifupdown`, `systemd-networkd` ou une autre configuration |
| Fedora | NetworkManager, souvent pilotable par `nmcli` |
| RHEL et dérivées | NetworkManager et profils de connexion |
| Serveur personnalisé | configuration dépendant de l'installation et des outils présents |

Ces associations sont des cas courants, pas une règle absolue. Vérifiez toujours ce qui fonctionne réellement sur votre machine.

## 10.2. Vérifier la présence de Netplan

```bash
command -v netplan
```

Si une commande est affichée, Netplan est disponible dans le `PATH`.

Consulter sa version ou son aide :

```bash
netplan --help
```

La présence de Netplan ne prouve pas à elle seule que toutes les interfaces sont gérées par lui.

## 10.3. Vérifier NetworkManager

```bash
command -v nmcli
```

Puis :

```bash
nmcli general status
```

Et :

```bash
nmcli device status
```

Une interface marquée `unmanaged` n'est pas gérée par NetworkManager dans la configuration courante.

Elle peut relever d'un autre mécanisme de configuration ou être explicitement exclue de NetworkManager.

## 10.4. Vérifier systemd-networkd

```bash
systemctl status systemd-networkd
```

Sur un système qui utilise `systemd-networkd`, la commande suivante peut également être disponible :

```bash
networkctl list
```

Si un outil manque, ne concluez pas immédiatement à une panne. Il peut simplement ne pas être installé.

## 10.5. Règle essentielle : ne pas modifier plusieurs systèmes en concurrence

Avant de configurer une interface, déterminez qui la gère.

Sur un système Netplan, la configuration YAML peut être la source persistante qui génère les paramètres transmis à NetworkManager ou à `systemd-networkd`.

Sur un système NetworkManager configuré directement, `nmcli` peut être l'outil principal de modification des profils.

Évitez de configurer le même lien de façon contradictoire à plusieurs endroits. Cela peut donner un état imprévisible ou faire disparaître les modifications après un redémarrage.


# 11. Réseau sous Linux (netplan, nmcli)

Ce chapitre regroupe les deux outils essentiels annoncés dans le sujet du cours.

## 11.1. Netplan : principe général

Netplan est un outil de configuration réseau utilisant des fichiers YAML. Il traduit cette configuration vers un service de gestion réseau compatible, notamment `systemd-networkd` ou NetworkManager.

L'architecture générale est :

```text
Fichiers YAML Netplan
          |
          v
     netplan generate
          |
          v
Configuration produite
pour le moteur choisi
          |
          v
+------------------------+
| systemd-networkd       |
| ou NetworkManager      |
+------------------------+
          |
          v
Interfaces et paramètres réseau
```

La configuration persistante se trouve généralement dans :

```text
/etc/netplan/
```

D'autres répertoires peuvent participer au chargement de la configuration. Plusieurs fichiers peuvent être combinés, selon les règles de Netplan. Il faut donc examiner l'ensemble des fichiers présents avant d'en ajouter un nouveau.

## 11.2. NetworkManager et `nmcli`

NetworkManager gère les connexions réseau. `nmcli` est son outil en ligne de commande.

Il permet notamment de :

- afficher les appareils ;
- consulter les connexions ;
- créer et modifier des profils ;
- activer ou désactiver une connexion ;
- configurer les paramètres IP ;
- gérer les connexions Wi-Fi.

Schéma :

```text
Administrateur
      |
      v
    nmcli
      |
      v
NetworkManager
      |
      v
Interface / profil / connexion réseau
```

## 11.3. Les deux outils sont-ils concurrents ?

Pas exactement.

Netplan décrit la configuration dans des fichiers YAML et peut transmettre l'état souhaité à NetworkManager.

`nmcli` communique directement avec NetworkManager pour consulter et manipuler les profils que celui-ci gère.

Le choix dépend du système :

- sur un serveur Ubuntu géré par Netplan, modifiez généralement la configuration persistante à travers Netplan ;
- sur un système administré directement par NetworkManager, utilisez `nmcli` pour gérer les profils ;
- dans un environnement de bureau utilisant NetworkManager derrière Netplan, comprenez quelles modifications sont persistantes et lesquelles peuvent être régénérées.

Il ne faut pas conclure que Netplan est toujours destiné aux serveurs ou que `nmcli` est exclusivement destiné aux postes de travail.


# 12. Configuration réseau avec Netplan

## 12.1. Examiner la configuration existante

Avant de modifier quoi que ce soit :

```bash
ls -l /etc/netplan/
```

Puis, lorsque la commande est disponible :

```bash
sudo netplan get
```

Examinez les fichiers YAML existants avec un éditeur de texte.

Exemple :

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Ce nom est seulement un exemple. Utilisez le véritable nom présent sur votre machine.

**Attention :** certains fichiers Netplan sont générés par un outil de provisioning comme cloud-init. Leur modification manuelle peut être remplacée par le mécanisme qui les a créés. Identifiez la source de configuration avant d'effectuer des changements persistants.

## 12.2. Comprendre la structure YAML

Exemple :

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
```

Explication :

- `network:` est la racine ;
- `version: 2` indique la version du format de configuration Netplan utilisé dans cet exemple ;
- `ethernets:` définit des interfaces Ethernet ;
- `enp0s3:` désigne ici une interface ;
- `dhcp4: true` active l'obtention automatique de la configuration IPv4.

**Important :** YAML dépend de l'indentation. Utilisez des espaces, jamais des tabulations pour indenter le document.

L'interface de l'exemple ne correspond pas nécessairement à votre machine.

## 12.3. Configurer DHCP avec Netplan

Pour une interface Ethernet qui doit obtenir automatiquement ses paramètres IPv4 :

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
```

Ce fichier est un exemple minimal. Il faut l'adapter à l'interface réelle et préserver les autres configurations nécessaires.

Lorsque DHCP fonctionne, le client peut recevoir une adresse, une route par défaut et des paramètres DNS selon le réseau.

## 12.4. Configurer une adresse IPv4 statique

Pour un laboratoire isolé, supposons les paramètres suivants :

```text
Interface :  enp0s3
IP :         192.168.10.20/24
Passerelle : 192.168.10.1
DNS :        192.168.10.1 et 1.1.1.1
```

Ces valeurs sont des exemples. Elles ne doivent être utilisées que si elles correspondent à votre réseau de laboratoire et si l'adresse n'est pas déjà attribuée.

Configuration Netplan :

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: false
      addresses:
        - 192.168.10.20/24
      routes:
        - to: default
          via: 192.168.10.1
      nameservers:
        addresses:
          - 192.168.10.1
          - 1.1.1.1
```

### Explication ligne par ligne

`dhcp4: false` désactive DHCPv4 pour cette interface.

`addresses` contient les adresses attribuées à l'interface.

`routes` définit les routes souhaitées. La route `to: default` constitue la route par défaut.

`via` indique la passerelle de cette route.

`nameservers.addresses` précise les serveurs DNS utilisés pour la résolution des noms selon le fonctionnement du système.

Une mauvaise configuration de l'adresse ou de la passerelle peut interrompre la communication avec les réseaux distants.

## 12.5. Comprendre `renderer`

Une configuration peut préciser le moteur chargé de l'interface.

Exemple pour `systemd-networkd` :

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:
      dhcp4: true
```

Exemple pour NetworkManager :

```yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    enp0s3:
      dhcp4: true
```

Ne remplacez pas le renderer sans comprendre l'architecture du système. Certains services, profils ou mécanismes d'intégration peuvent dépendre du moteur actuel.

La prise en charge et les détails de chaque fonctionnalité peuvent également dépendre de la version de Netplan et du moteur choisi.

## 12.6. Vérifier les fichiers YAML

Après modification, utilisez :

```bash
sudo netplan generate
```

Cette commande vérifie et génère la configuration destinée au moteur sélectionné. Elle ne garantit pas que les paramètres fonctionneront réellement sur le réseau.

Un fichier YAML mal indenté ou une option non reconnue peut empêcher la génération.

Avant de continuer, corrigez les erreurs signalées.

## 12.7. Pourquoi préférer `netplan try` à une application immédiate ?

La commande suivante est particulièrement utile lorsque l'on modifie un réseau :

```bash
sudo netplan try
```

Elle tente d'appliquer la configuration et demande une confirmation, avec un mécanisme de restauration en cas d'absence de confirmation dans le délai prévu.

Elle est particulièrement importante lorsque le changement peut couper une session distante.

La procédure doit être réalisée avec une méthode de secours disponible, car tout incident de communication ou tout scénario d'erreur n'est pas nécessairement récupérable automatiquement.

## 12.8. Appliquer la configuration

Après avoir vérifié les fichiers et testé les changements :

```bash
sudo netplan apply
```

Cette commande applique la configuration Netplan.

L'application d'une configuration peut modifier les adresses, routes ou DNS et interrompre des connexions en cours.

Ne lancez pas une modification risquée à distance sans prévoir une possibilité de récupération.

## 12.9. Procédure prudente complète

Dans un laboratoire où vous avez accès à la console :

```bash
sudo netplan generate
sudo netplan try
```

Si la configuration est confirmée et que les tests sont satisfaisants, la configuration peut être validée.

En cas de doute, conservez un accès à la console et préparez à l'avance la restauration du fichier.

Sur un serveur distant, prévoyez une session de secours, une console de machine virtuelle ou un mécanisme de récupération indépendant de la connexion modifiée.

## 12.10. Vérifier le résultat

```bash
ip -br address
ip route
resolvectl status
```

Ces commandes permettent de vérifier les adresses, les routes et les paramètres du résolveur lorsque `resolvectl` est disponible.

Un `netplan apply` sans erreur ne prouve pas que la passerelle ou les DNS sont joignables. Il faut aussi réaliser des tests de connectivité.

## 12.11. Configurer plusieurs interfaces

Une machine peut posséder plusieurs interfaces. Chaque interface peut recevoir des paramètres distincts.

Exemple :

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
    enp0s8:
      dhcp4: false
      addresses:
        - 192.168.20.10/24
```

Ce modèle configure une interface en DHCP et une autre en adresse statique.

Attention : une interface supplémentaire ne doit pas recevoir une passerelle par défaut sans justification. Plusieurs routes par défaut peuvent modifier la sélection du chemin de sortie.

## 12.12. Configurer des serveurs DNS supplémentaires

Dans Netplan :

```yaml
nameservers:
  addresses:
    - 192.168.10.1
    - 1.1.1.1
  search:
    - laboratoire.example
```

Le suffixe `laboratoire.example` est un nom réservé aux exemples.

La liste `addresses` fournit les adresses des serveurs DNS. La liste `search` permet de définir des suffixes de recherche selon le comportement du résolveur.

L'ordre de sélection et le comportement réel dépendent aussi du moteur réseau et du résolveur configurés.

Ne remplacez pas les DNS d'entreprise par un serveur public sans tenir compte des politiques de résolution interne.


# 13. Configuration réseau avec `nmcli`

Cette section suppose que NetworkManager est installé et gère l'interface concernée.

## 13.1. Vérifier NetworkManager

```bash
nmcli general status
```

Cette commande affiche l'état général de NetworkManager.

Consultez les interfaces :

```bash
nmcli device status
```

Exemple de sortie fictive :

```text
DEVICE   TYPE      STATE         CONNECTION
enp0s3   ethernet  connected     Connexion filaire 1
lo       loopback  connected     lo
wlp2s0   wifi      disconnected  --
```

Les valeurs exactes dépendent de la machine.

## 13.2. Afficher les profils de connexion

```bash
nmcli connection show
```

Cette commande liste les profils enregistrés.

Un profil est une configuration de connexion que NetworkManager peut activer.

Un même appareil peut avoir plusieurs profils enregistrés, mais il ne peut pas nécessairement les utiliser tous simultanément.

Exemple de noms possibles :

```text
Connexion filaire 1
Wi-Fi maison
Wi-Fi laboratoire
Connexion de test
```

## 13.3. Afficher les propriétés d'un profil

```bash
nmcli connection show "Connexion filaire 1"
```

Le nom exact doit correspondre à un profil réellement présent.

Pour afficher les valeurs courantes d'un appareil :

```bash
nmcli device show enp0s3
```

Remplacez `enp0s3` par l'interface de votre machine.

## 13.4. Afficher les adresses IP

```bash
ip -br address
```

Vous pouvez aussi consulter les paramètres d'un profil NetworkManager :

```bash
nmcli connection show "Connexion filaire 1"
```

Les sections `ipv4` et `ipv6` renseignent les méthodes d'adressage, adresses, passerelles et paramètres DNS.

## 13.5. Créer un profil Ethernet en DHCP

Dans un laboratoire où l'interface est gérée par NetworkManager :

```bash
sudo nmcli connection add \
  type ethernet \
  con-name "lab-dhcp" \
  ifname enp0s3 \
  ipv4.method auto \
  ipv6.method auto
```

Cette commande crée un nouveau profil de connexion.

Elle ne garantit pas que le profil sera activé si une autre connexion est déjà active ou si l'interface ne correspond pas à l'environnement.

Vérifiez le nom de l'interface avant de lancer la commande.

## 13.6. Activer un profil

```bash
sudo nmcli connection up "lab-dhcp"
```

L'activation peut modifier l'adresse IP, la route par défaut ou les paramètres DNS.

Sur une machine distante, ne changez pas de connexion sans prévoir un moyen de reprendre la main si la communication est interrompue.

## 13.7. Configurer une adresse statique

Exemple pour un laboratoire dédié :

```bash
sudo nmcli connection add \
  type ethernet \
  con-name "lab-statique" \
  ifname enp0s3 \
  ipv4.method manual \
  ipv4.addresses 192.168.10.20/24 \
  ipv4.gateway 192.168.10.1 \
  ipv4.dns "192.168.10.1 1.1.1.1" \
  ipv6.method auto
```

**Attention :** ce profil ne doit être utilisé que si l'adresse `192.168.10.20` est disponible sur le réseau concerné et si la passerelle `192.168.10.1` existe.

Après création :

```bash
nmcli connection show "lab-statique"
```

Examinez les valeurs avant d'activer le profil.

## 13.8. Modifier un profil existant

Exemple :

```bash
sudo nmcli connection modify "lab-statique" ipv4.dns "192.168.10.1 1.1.1.1"
```

Cette commande met à jour les DNS enregistrés dans le profil.

Pour appliquer les nouveaux paramètres à une connexion active, il peut être nécessaire de réactiver la connexion :

```bash
sudo nmcli connection up "lab-statique"
```

Cette opération peut couper temporairement la connectivité.

## 13.9. Revenir à DHCP

Pour un profil NetworkManager existant :

```bash
sudo nmcli connection modify "lab-statique" ipv4.method auto
```

La configuration IP manuelle n'est alors plus la méthode d'adressage sélectionnée par ce profil.

Selon les propriétés précédemment définies, vous pouvez devoir réinitialiser certaines valeurs manuelles comme les adresses, la passerelle ou les DNS.

Examinez le profil après modification avant de le réactiver.

## 13.10. Supprimer un profil de test

```bash
nmcli connection show
```

Vérifiez d'abord le nom exact.

Puis, si le profil est bien un profil de laboratoire dont vous n'avez plus besoin :

```bash
sudo nmcli connection delete "lab-statique"
```

Cette opération supprime le profil. Ne supprimez pas une connexion active ou importante sans comprendre les conséquences.


# 14. Utiliser `nmcli` pour le Wi-Fi

## 14.1. Vérifier les interfaces Wi-Fi

```bash
nmcli device status
```

Recherchez une interface dont le type est `wifi`.

Si aucune interface Wi-Fi n'apparaît, cela peut être dû à l'absence de matériel, à un pilote manquant, à un blocage radio ou à une configuration du système.

## 14.2. Lister les réseaux disponibles

```bash
nmcli device wifi list
```

Cette commande affiche les points d'accès détectés par l'interface Wi-Fi.

Le résultat dépend de la couverture radio, de la compatibilité du matériel et de la disponibilité des points d'accès.

## 14.3. Se connecter à un réseau protégé

Commande interactive recommandée pour un test :

```bash
nmcli --ask device wifi connect "SSID_DU_LABORATOIRE"
```

Remplacez le nom d'exemple par le SSID autorisé. Si un secret est nécessaire, `--ask` permet à `nmcli` de demander les informations manquantes lorsque cela est pris en charge par le profil et les agents disponibles.

Évitez d'écrire un mot de passe directement dans une commande susceptible d'être enregistrée dans l'historique du shell.

## 14.4. Vérifier la connexion

```bash
nmcli device status
nmcli connection show --active
ip -br address
ip route
```

Ces commandes permettent de contrôler l'état du périphérique, la connexion active, l'adresse et la route.

## 14.5. Désactiver et réactiver le Wi-Fi

Pour désactiver la radio Wi-Fi par NetworkManager :

```bash
nmcli radio wifi off
```

Pour la réactiver :

```bash
nmcli radio wifi on
```

Ces commandes affectent la disponibilité du Wi-Fi sur la machine. Évitez de les exécuter sur une machine dont l'accès distant dépend de cette liaison sans prévoir une solution de secours.


# 15. Vérifier la connectivité dans le bon ordre

Le diagnostic doit progresser du local vers le distant.

## 15.1. Méthode générale

```text
1. L'interface existe-t-elle ?
             |
             v
2. La liaison est-elle active ?
             |
             v
3. L'adresse IP est-elle correcte ?
             |
             v
4. La route est-elle cohérente ?
             |
             v
5. La passerelle est-elle joignable ?
             |
             v
6. Une destination IP distante répond-elle ?
             |
             v
7. La résolution DNS fonctionne-t-elle ?
             |
             v
8. Le service applicatif répond-il ?
```

Cette progression évite de commencer par modifier les DNS alors que l'interface n'a aucune adresse.

## 15.2. Étape 1 : vérifier les interfaces

```bash
ip -br link
```

Confirmez que l'interface ciblée existe et examinez son état.

## 15.3. Étape 2 : vérifier les adresses

```bash
ip -br address
```

Confirmez que l'interface possède l'adresse attendue et le bon préfixe.

## 15.4. Étape 3 : vérifier les routes

```bash
ip route
```

Vérifiez la présence de la route vers le réseau attendu et de la route par défaut lorsque celle-ci est nécessaire.

## 15.5. Étape 4 : tester la passerelle

```bash
ping -c 3 192.168.10.1
```

Remplacez cette adresse par la passerelle réelle.

Si aucune réponse n'est reçue, vérifiez notamment :

- le lien Ethernet ou Wi-Fi ;
- l'adresse et le préfixe ;
- la présence du bon réseau ;
- l'adresse de la passerelle ;
- les règles de filtrage ;
- l'accessibilité du routeur.

Un équipement peut filtrer ICMP. L'échec de `ping` doit donc être interprété avec les autres observations.

## 15.6. Étape 5 : tester une destination IP distante

```bash
ping -c 3 1.1.1.1
```

Utilisez une destination autorisée et adaptée à votre environnement.

Si la passerelle fonctionne mais que les destinations distantes échouent, examinez la route par défaut, le routage amont, le pare-feu et la connectivité du réseau.

## 15.7. Étape 6 : tester DNS

```bash
getent hosts example.com
```

Si cette commande échoue alors qu'une destination IP est accessible, étudiez les paramètres DNS, le résolveur local et les politiques de résolution.

## 15.8. Étape 7 : tester l'application

Exemple HTTPS :

```bash
curl -I https://example.com
```

La résolution DNS peut fonctionner alors que le service est indisponible, que le port est filtré ou que la négociation TLS échoue.

Le message exact permet de poursuivre le diagnostic.


# 16. Résoudre les pannes courantes

## 16.1. L'interface n'a pas d'adresse IPv4

Commandes :

```bash
ip -br address
ip link show
nmcli device status
```

Causes possibles :

- interface désactivée ;
- câble débranché ;
- point d'accès Wi-Fi indisponible ;
- serveur DHCP absent ou non joignable ;
- mauvais profil de connexion ;
- configuration IP statique erronée ;
- interface non gérée par le service auquel vous vous adressez.

Ne commencez pas par redémarrer tous les services. Identifiez d'abord l'interface concernée et son gestionnaire.

## 16.2. Le serveur reçoit une adresse `169.254.x.x`

Cette plage est utilisée pour l'adressage IPv4 link-local.

Causes possibles :

- aucune réponse DHCP reçue ;
- serveur DHCP absent ;
- mauvais VLAN ;
- connexion physique non opérationnelle ;
- mauvais réseau virtuel ;
- configuration locale qui active l'adressage link-local.

Vérifiez l'état du lien, les journaux du gestionnaire réseau et l'accessibilité du serveur DHCP.

## 16.3. La passerelle n'est pas joignable

Exécutez :

```bash
ip address show
ip route show
ip neigh show
```

Vérifiez que :

- l'adresse IP et le préfixe sont corrects ;
- la passerelle appartient à un réseau directement joignable ou est atteignable par une route appropriée ;
- l'interface sélectionnée est correcte ;
- le réseau de niveau liaison fonctionne ;
- aucun filtrage local ou distant ne bloque le test.

## 16.4. Internet fonctionne par IP mais pas par nom

Vérifiez :

```bash
resolvectl status
getent hosts example.com
cat /etc/resolv.conf
```

Si `systemd-resolved` n'est pas disponible, utilisez les outils du résolveur réellement utilisé par la machine.

Vérifiez les DNS reçus par DHCP, les paramètres du profil réseau et la manière dont la distribution gère `/etc/resolv.conf`.

Ne remplacez pas directement le fichier sans comprendre s'il est géré par un service.

## 16.5. Le réseau fonctionne jusqu'au redémarrage

Causes possibles :

- adresse ajoutée temporairement avec `ip address` ;
- route ajoutée avec `ip route` sans configuration persistante ;
- profil NetworkManager non enregistré ou non activable automatiquement ;
- configuration Netplan incorrecte ;
- changement généré ou remplacé par un autre outil ;
- paramètres DHCP et paramètres statiques contradictoires.

Comparez l'état actif avec la configuration persistante.

## 16.6. Un service n'est pas accessible malgré un réseau fonctionnel

Vérifiez :

```bash
ss -tuln
```

Puis, en fonction du service :

```bash
systemctl status nom-du-service
```

Le nom est un exemple à remplacer.

Un problème applicatif peut être causé par un service arrêté, un port non ouvert, une écoute limitée à `127.0.0.1`, un pare-feu ou une restriction distante.

La présence d'une route valide ne prouve pas que le service attendu écoute ou accepte les connexions.

## 16.7. Vérifier les journaux système

Selon la distribution :

```bash
journalctl -b
```

Pour rechercher les messages associés à NetworkManager :

```bash
journalctl -u NetworkManager -b
```

Pour `systemd-networkd` :

```bash
journalctl -u systemd-networkd -b
```

Pour une machine qui utilise Netplan, examinez également les erreurs de génération et les messages du moteur correspondant.

Les noms des services peuvent varier et certaines machines n'utilisent qu'une partie de ces composants.


# 17. Sécurité et précautions opérationnelles

## 17.1. Ne pas modifier un réseau distant sans plan de récupération

Modifier l'adresse, la passerelle ou le profil réseau d'une machine distante peut couper la session SSH.

Avant d'intervenir :

1. identifiez le réseau utilisé par votre session ;
2. sauvegardez la configuration ;
3. vérifiez les paramètres de remplacement ;
4. utilisez `netplan try` lorsque cette méthode est adaptée ;
5. prévoyez une console ou un autre moyen d'accès ;
6. vérifiez le rétablissement de la connectivité après le changement.

Ne lancez pas une configuration statique arbitraire sur une machine distante pour apprendre la syntaxe.

## 17.2. Sauvegarder la configuration existante

Avant de modifier un fichier Netplan :

```bash
sudo cp -a /etc/netplan "$HOME/netplan-backup"
```

Cette commande copie le répertoire de configuration vers le répertoire personnel. Selon les permissions et les données présentes, elle peut exiger des ajustements et produire une copie contenant des informations de configuration sensibles.

Dans un cadre professionnel, protégez la sauvegarde et assurez-vous qu'elle est restaurable.

Évitez également d'écraser des fichiers existants sans comprendre leur origine et leur rôle.

## 17.3. Ne pas désactiver les contrôles de sécurité SSH

Ne désactivez pas les vérifications des clés d'hôte SSH simplement pour contourner une erreur de connexion.

Une alerte de clé d'hôte peut indiquer une modification légitime de la machine, mais aussi un risque d'interception.

Vérifiez l'identité du serveur selon la procédure prévue par votre organisation.

## 17.4. Ne pas exposer les secrets

Les commandes Wi-Fi, VPN ou API peuvent manipuler des secrets.

Évitez les mots de passe dans les historiques de commandes, les captures d'écran et les journaux.

Préférez les mécanismes interactifs sécurisés ou les gestionnaires de secrets compatibles avec l'environnement.

## 17.5. Respecter le plan d'adressage

Ne choisissez pas une adresse au hasard pour une interface.

Une adresse dupliquée peut créer des conflits difficiles à diagnostiquer.

Avant d'affecter une adresse statique, vérifiez :

- le sous-réseau ;
- les plages réservées par DHCP ;
- les réservations existantes ;
- la passerelle ;
- les règles de segmentation ;
- les politiques réseau locales.

Un simple test `ping` ne garantit pas qu'une adresse est libre.


# 18. Travaux pratiques guidés

Ces TP doivent être réalisés dans une machine virtuelle ou un environnement de laboratoire sur lequel vous disposez d'un accès console.

Les valeurs IP sont des exemples. Ne les copiez pas sur un réseau de production sans validation.

## TP 1 — Découvrir la configuration réseau

### Objectif

Identifier les interfaces, leurs adresses et la route par défaut.

### Commandes

```bash
ip -br link
ip -br address
ip route
ip -6 route
ip neigh
```

### Travail demandé

Rédigez un petit rapport contenant :

- le nom de chaque interface ;
- l'état de chaque interface ;
- les adresses IPv4 ;
- les adresses IPv6, si elles existent ;
- la route par défaut IPv4, si elle existe ;
- une observation sur les voisins réseau.

### Critères de réussite

Vous devez pouvoir expliquer pourquoi une interface peut être active sans adresse IPv4 et pourquoi une machine peut posséder une adresse IP sans disposer d'un accès Internet.


## TP 2 — Vérifier l'accès réseau

### Objectif

Suivre un parcours de diagnostic du local vers le distant.

### Étapes

Tester la boucle locale :

```bash
ping -c 3 127.0.0.1
```

Afficher la route :

```bash
ip route
```

Si une passerelle est configurée, la tester :

```bash
ping -c 3 ADRESSE_PASSERELLE
```

Remplacez `ADRESSE_PASSERELLE` par la véritable adresse de votre routeur.

Tester une destination IP distante autorisée :

```bash
ping -c 3 1.1.1.1
```

Tester DNS :

```bash
getent hosts example.com
```

Tester HTTPS :

```bash
curl -I https://example.com
```

### Travail demandé

Pour chaque commande, indiquez :

- le résultat attendu ;
- le composant réseau testé ;
- ce que signifie un échec ;
- une autre commande permettant d'approfondir le diagnostic.

### Critères de réussite

Vous devez pouvoir distinguer une panne de lien, une erreur d'adressage, un problème de route, une panne DNS et une indisponibilité applicative.


## TP 3 — Configurer DHCP avec Netplan

### Objectif

Définir la configuration d'une interface Ethernet pour obtenir son adresse automatiquement.

### Étape 1 : vérifier les fichiers

```bash
ls -l /etc/netplan/
sudo netplan get
```

### Étape 2 : identifier l'interface

```bash
ip -br link
ip -br address
```

### Étape 3 : préparer le YAML

Exemple :

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
```

Remplacez `enp0s3` par l'interface réelle. Ne supprimez pas arbitrairement les autres configurations nécessaires à la machine.

### Étape 4 : valider

```bash
sudo netplan generate
```

### Étape 5 : tester prudemment

```bash
sudo netplan try
```

### Étape 6 : vérifier

```bash
ip -br address
ip route
```

### Résultat attendu

L'interface devrait obtenir une adresse IPv4 si un serveur DHCP est disponible et si la configuration du réseau autorise l'allocation.

Si aucune adresse n'apparaît, vérifiez les journaux et la liaison physique plutôt que d'appliquer des changements supplémentaires sans diagnostic.


## TP 4 — Créer un profil DHCP avec `nmcli`

### Objectif

Créer un profil de laboratoire dans NetworkManager.

### Étape 1 : vérifier le service

```bash
nmcli general status
nmcli device status
```

### Étape 2 : créer le profil

Sur un système de laboratoire dont l'interface est gérée par NetworkManager :

```bash
sudo nmcli connection add \
  type ethernet \
  con-name "TP-DHCP" \
  ifname enp0s3 \
  ipv4.method auto \
  ipv6.method auto
```

### Étape 3 : inspecter le profil

```bash
nmcli connection show "TP-DHCP"
```

### Étape 4 : activer si cela est approprié

```bash
sudo nmcli connection up "TP-DHCP"
```

L'activation peut interrompre la connexion courante. Assurez-vous que le profil est destiné à l'interface voulue.

### Étape 5 : contrôler

```bash
ip -br address
ip route
nmcli connection show --active
```

### Compétences acquises

Vous devez savoir distinguer le profil enregistré de l'état de connexion actuellement actif.


## TP 5 — Configurer une adresse statique dans un laboratoire isolé

### Objectif

Appliquer une adresse IPv4 statique lorsque le plan d'adressage le permet.

### Configuration d'exemple

```text
Interface :  enp0s3
IP :         192.168.10.20/24
Passerelle : 192.168.10.1
DNS :        192.168.10.1
```

### Travail demandé

1. confirmer le sous-réseau utilisé par le laboratoire ;
2. vérifier que l'adresse est disponible ;
3. créer ou modifier une configuration Netplan ou NetworkManager selon le gestionnaire utilisé ;
4. appliquer le changement avec une méthode de récupération ;
5. vérifier l'adresse, la route et le DNS ;
6. documenter comment revenir à la configuration antérieure.

### Critères de réussite

Le changement doit produire une configuration cohérente et la procédure de restauration doit être clairement définie.


# 19. Exercices corrigés

Essayez de résoudre chaque exercice avant de consulter sa correction.

## Exercice 1 — Identifier la commande appropriée

Associez chaque besoin à une commande adaptée.

| Besoin | Commande |
|---|---|
| Afficher les interfaces | `ip link show` |
| Afficher les adresses | `ip address show` |
| Afficher la table de routage | `ip route` |
| Afficher les profils NetworkManager | `nmcli connection show` |
| Afficher les appareils NetworkManager | `nmcli device status` |
| Tester la résolution système d'un nom | `getent hosts example.com` |

**Correction :** les commandes affichées répondent aux besoins correspondants. Certaines informations peuvent également être obtenues par d'autres outils.

## Exercice 2 — Interpréter une adresse

Une machine possède :

```text
192.168.25.17/24
```

Questions :

1. Quelle est l'adresse IPv4 ?
2. Quel est le préfixe ?
3. Quel est le masque équivalent ?
4. Quel est le réseau ?

**Correction :**

1. Adresse : `192.168.25.17`
2. Préfixe : `/24`
3. Masque : `255.255.255.0`
4. Réseau : `192.168.25.0/24`

Cette interprétation suppose le préfixe IPv4 `/24` classique.

## Exercice 3 — Identifier le problème

Une machine peut joindre sa passerelle par adresse IP, mais `getent hosts example.com` échoue.

Quelle catégorie de problème doit être examinée en priorité ?

**Correction :** la résolution DNS est une piste prioritaire. Il faut examiner le résolveur système, les serveurs DNS reçus ou configurés, leur accessibilité et les journaux pertinents.

Ce diagnostic ne prouve pas à lui seul que tous les autres composants réseau sont corrects.

## Exercice 4 — Lire une table de routage

Sortie :

```text
default via 192.168.1.1 dev enp0s3
192.168.1.0/24 dev enp0s3 scope link src 192.168.1.20
```

Questions :

- Quelle est la passerelle par défaut ?
- Quelle est l'adresse source indiquée ?
- Quelle interface est utilisée ?

**Correction :**

- Passerelle : `192.168.1.1`
- Adresse source : `192.168.1.20`
- Interface : `enp0s3`

## Exercice 5 — Corriger un YAML

Code incorrect :

```yaml
network:
version: 2
ethernets:
enp0s3:
dhcp4: true
```

**Correction :**

```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      dhcp4: true
```

**Explication :** YAML utilise l'indentation pour représenter la structure. Une indentation incorrecte peut empêcher Netplan d'interpréter la configuration.

## Exercice 6 — Pourquoi une configuration disparaît-elle ?

Un administrateur ajoute une adresse avec une commande temporaire :

```bash
sudo ip address add 192.168.10.20/24 dev enp0s3
```

Après un redémarrage, l'adresse n'est plus présente.

**Correction :** cette commande modifie l'état actif du noyau. Elle ne crée pas à elle seule une configuration persistante. Il faut définir l'adresse dans le gestionnaire réseau utilisé, puis vérifier qu'elle est restaurée correctement au démarrage.

N'exécutez cette commande que dans un laboratoire où l'adresse est autorisée et disponible.

## Exercice 7 — Différencier les outils

Une machine Ubuntu utilise Netplan avec `systemd-networkd`. Un administrateur tente de modifier le profil avec `nmcli`, mais NetworkManager ne gère pas l'interface.

Que doit-il faire ?

**Correction :** il doit d'abord confirmer la configuration effective. Si Netplan utilise `systemd-networkd`, `nmcli` n'est pas nécessairement l'outil qui contrôle cette interface. Il faut modifier la configuration persistante à travers Netplan ou utiliser l'outil adapté au gestionnaire réellement actif.

## Exercice 8 — Quel test est insuffisant ?

Un administrateur exécute :

```bash
ping -c 3 1.1.1.1
```

Le test réussit. Peut-il conclure que tous les services Internet fonctionnent ?

**Correction :** non. Cela indique seulement que la destination a répondu à ICMP depuis le chemin testé. Le DNS, les connexions TCP, TLS, HTTP et d'autres services doivent être testés séparément.

## Exercice 9 — Sécurité du changement

Un administrateur modifie la passerelle Netplan d'un serveur distant accessible uniquement par SSH, puis exécute immédiatement `netplan apply`.

Quel risque existe et quelle méthode est préférable ?

**Correction :** le changement peut couper la session et empêcher le retour à la machine. Il est préférable de sauvegarder la configuration, d'utiliser `netplan try` lorsque c'est approprié, puis de vérifier la connectivité avec un accès de secours disponible.


# 20. Défi final — Configurer et diagnostiquer un serveur Linux

## 20.1. Contexte

Vous devez préparer une machine virtuelle Linux pour un laboratoire d'administration.

Le serveur doit :

- avoir une interface réseau identifiée ;
- obtenir une adresse IPv4 cohérente avec son réseau ;
- utiliser une passerelle adaptée ;
- résoudre les noms de domaine ;
- être capable de joindre les équipements autorisés ;
- conserver sa configuration après un redémarrage ;
- fournir un rapport de diagnostic exploitable.

Aucune configuration d'adresse statique ne doit être appliquée sans vérifier le plan d'adressage du laboratoire.

## 20.2. Travail demandé

### Étape 1 — Découverte

Collectez les informations suivantes :

```bash
ip -br link
ip -br address
ip route
ip -6 route
```

Identifiez les interfaces et leurs adresses.

### Étape 2 — Identifier le gestionnaire

Exécutez, lorsque les outils sont disponibles :

```bash
command -v netplan
command -v nmcli
systemctl is-active NetworkManager
systemctl is-active systemd-networkd
```

Interprétez les résultats selon le système réellement utilisé.

### Étape 3 — Choisir la méthode de configuration

Si l'interface est gérée par Netplan, préparez une configuration YAML cohérente.

Si elle est gérée directement par NetworkManager, créez ou modifiez le profil adapté avec `nmcli`.

Ne configurez pas simultanément la même interface à travers des mécanismes contradictoires.

### Étape 4 — Appliquer le changement

Vérifiez la syntaxe ou le profil avant activation.

Prévoyez un accès de secours si le changement risque de couper la communication.

### Étape 5 — Tester les composants

Vérifiez :

- l'état de l'interface ;
- l'adresse IPv4 ;
- la route par défaut, lorsqu'elle est nécessaire ;
- la joignabilité de la passerelle ;
- une destination IP distante autorisée ;
- la résolution DNS ;
- le service applicatif pertinent.

### Étape 6 — Produire un rapport

Le rapport doit contenir :

- la date du contrôle ;
- les interfaces identifiées ;
- les adresses principales ;
- les routes ;
- les tests effectués ;
- les résultats de chaque test ;
- les éventuelles erreurs ou réserves.

N'enregistrez pas de mots de passe ou d'autres secrets dans le rapport.

### Étape 7 — Vérifier la persistance

Examinez la configuration enregistrée du gestionnaire réseau.

Dans un laboratoire, un redémarrage contrôlé permet ensuite de vérifier que les paramètres attendus reviennent correctement.

Le redémarrage ne doit pas être effectué sur un système critique sans validation et plan de récupération.

## 20.3. Barème d'auto-évaluation

| Domaine | Points |
|---|---:|
| Découverte des interfaces | 10 |
| Compréhension des adresses et préfixes | 15 |
| Identification du gestionnaire réseau | 10 |
| Configuration cohérente | 20 |
| Application prudente et récupération | 15 |
| Tests de connectivité et de DNS | 20 |
| Rapport et validation de persistance | 10 |
| **Total** | **100** |

Une bonne note ne suffit pas si le changement a été effectué sans vérifier qu'il est adapté au réseau. La validation technique et la sécurité opérationnelle sont indissociables.


# 21. Liste de compétences à maîtriser

Cochez chaque élément lorsque vous pouvez le réaliser seul dans un laboratoire.

## Fondamentaux du réseau

- [ ] Je sais expliquer le rôle d'une interface réseau.
- [ ] Je sais distinguer une adresse MAC et une adresse IP.
- [ ] Je sais expliquer un masque et un préfixe CIDR.
- [ ] Je sais identifier les principales plages IPv4 privées.
- [ ] Je sais expliquer DHCP.
- [ ] Je sais expliquer une passerelle.
- [ ] Je sais lire une table de routage.
- [ ] Je sais expliquer le rôle de DNS.
- [ ] Je sais distinguer IPv4 et IPv6.

## Diagnostic Linux

- [ ] Je sais utiliser `ip link`.
- [ ] Je sais utiliser `ip address`.
- [ ] Je sais utiliser `ip route`.
- [ ] Je sais vérifier des voisins avec `ip neigh`.
- [ ] Je sais tester une destination avec `ping`.
- [ ] Je sais contrôler les ports d'écoute avec `ss`.
- [ ] Je sais tester DNS avec `getent`.
- [ ] Je sais utiliser `resolvectl` lorsqu'il est disponible.
- [ ] Je sais lire les journaux d'un gestionnaire réseau.

## Netplan

- [ ] Je sais identifier les fichiers de configuration Netplan.
- [ ] Je sais expliquer la structure d'un fichier YAML.
- [ ] Je sais configurer DHCPv4.
- [ ] Je sais définir une adresse IPv4 statique.
- [ ] Je sais définir une route par défaut.
- [ ] Je sais définir les serveurs DNS.
- [ ] Je sais utiliser `netplan generate`.
- [ ] Je sais utiliser `netplan try` prudemment.
- [ ] Je sais expliquer la différence entre `netplan try` et `netplan apply`.
- [ ] Je sais vérifier le résultat de la configuration.

## NetworkManager et `nmcli`

- [ ] Je sais vérifier l'état de NetworkManager.
- [ ] Je sais afficher les interfaces et les profils.
- [ ] Je sais créer un profil DHCP.
- [ ] Je sais définir une configuration statique.
- [ ] Je sais modifier une configuration DNS.
- [ ] Je sais activer un profil.
- [ ] Je sais configurer une connexion Wi-Fi avec `--ask`.
- [ ] Je sais supprimer un profil de test sans toucher aux profils nécessaires.

## Méthode professionnelle

- [ ] Je sais identifier le gestionnaire réseau avant de modifier une interface.
- [ ] Je sais éviter les modifications concurrentes.
- [ ] Je sais sauvegarder une configuration.
- [ ] Je sais protéger une session SSH contre une coupure évitable.
- [ ] Je sais tester séparément l'adressage, le routage, DNS et les applications.
- [ ] Je sais expliquer les résultats et les limites d'un test.


# 22. Fiche de révision

## Interfaces et adresses

```bash
ip link show
ip address show
ip -br address
```

## Routes

```bash
ip route
ip -6 route
ip route get 1.1.1.1
```

## Voisins et connectivité

```bash
ip neigh
ping -c 3 127.0.0.1
ping -c 3 ADRESSE_PASSERELLE
```

## DNS

```bash
getent hosts example.com
resolvectl status
resolvectl query example.com
```

## Services et ports

```bash
ss -tuln
```

## État de NetworkManager

```bash
nmcli general status
nmcli device status
nmcli connection show
nmcli connection show --active
```

## Créer un profil DHCP de laboratoire

```bash
sudo nmcli connection add \
  type ethernet \
  con-name "lab-dhcp" \
  ifname enp0s3 \
  ipv4.method auto
```

L'interface doit être gérée par NetworkManager et adaptée au laboratoire.

## Netplan : vérifier et appliquer

```bash
sudo netplan get
sudo netplan generate
sudo netplan try
sudo netplan apply
```

Utilisez `netplan try` pour tester prudemment une modification compatible avec ce mécanisme, particulièrement lorsqu'une interruption réseau est possible.

## Vérifier les journaux

```bash
journalctl -u NetworkManager -b
journalctl -u systemd-networkd -b
```

Exécutez uniquement les commandes correspondant aux services présents et utilisés par le système.

## Ordre de diagnostic

```text
Interface
   |
   v
Adresse IP
   |
   v
Route
   |
   v
Passerelle
   |
   v
Destination IP
   |
   v
DNS
   |
   v
Application
```

## Règles essentielles

1. Une interface active n'est pas nécessairement correctement adressée.
2. Une adresse IP correcte ne garantit pas l'existence d'une route fonctionnelle.
3. Une route correcte ne garantit pas que la passerelle répond.
4. Une connexion IP fonctionnelle ne garantit pas que DNS fonctionne.
5. Une réponse à `ping` ne garantit pas que tous les services sont disponibles.
6. Une configuration temporaire peut disparaître après redémarrage.
7. Netplan et `nmcli` doivent être utilisés selon le gestionnaire réellement responsable de l'interface.
8. Les modifications du réseau peuvent interrompre une session SSH.
9. Avant de définir une adresse statique, vérifiez le plan d'adressage.
10. Toujours conserver un moyen de récupérer l'accès à une machine dont on modifie la connectivité.


# 23. Glossaire

**Adresse IP** : adresse utilisée pour identifier une interface ou une destination au niveau IP.

**Adresse MAC** : adresse de liaison utilisée notamment dans les réseaux Ethernet.

**CIDR** : notation d'une adresse réseau accompagnée d'une longueur de préfixe, comme `/24`.

**DHCP** : protocole utilisé pour attribuer automatiquement une configuration réseau aux clients.

**DNS** : système de résolution de noms, permettant notamment de retrouver des adresses IP à partir de noms de domaine.

**Interface réseau** : point d'accès réseau physique ou virtuel utilisé par le système.

**IPv4** : protocole IP fondé sur des adresses de 32 bits.

**IPv6** : protocole IP fondé sur des adresses de 128 bits.

**Passerelle** : équipement ou adresse de prochain saut permettant d'atteindre une destination non directement accessible.

**Préfixe réseau** : longueur de la partie réseau d'une adresse IP, exprimée notamment sous la forme `/24`.

**Route** : règle indiquant le chemin que le système utilise pour envoyer des paquets vers une destination.

**Table de routage** : ensemble des routes connues du système.

**Netplan** : outil de configuration réseau basé sur YAML, utilisé notamment sur Ubuntu.

**NetworkManager** : service de gestion des connexions réseau.

**`nmcli`** : outil en ligne de commande qui permet de piloter NetworkManager.

**`systemd-networkd`** : service de gestion réseau faisant partie de l'écosystème systemd.

**MTU** : taille maximale de l'unité de transmission au niveau considéré, généralement exprimée en octets.

**ARP** : protocole utilisé en IPv4 sur un réseau local pour découvrir l'adresse de liaison correspondant à une adresse IP.

**Neighbor Discovery** : ensemble de mécanismes IPv6 utilisés notamment pour découvrir les voisins et les routeurs.

**Loopback** : interface permettant à une machine de communiquer avec elle-même.

**Route par défaut** : route utilisée lorsque la destination ne correspond à aucune route plus spécifique applicable.

**Profil de connexion** : ensemble de paramètres enregistrés par NetworkManager pour une connexion réseau.

**Résolveur** : composant chargé de résoudre les requêtes de noms pour les applications.


# 24. Documentation et ressources officielles

Les documentations ci-dessous permettent de vérifier les options exactes selon les distributions et versions utilisées.

## Netplan

- Documentation officielle :  
  https://netplan.readthedocs.io/en/stable/

- Structure de la configuration :  
  https://netplan.readthedocs.io/en/stable/structure-id/

- Guide de configuration réseau Ubuntu :  
  https://ubuntu.com/server/docs/explanation/networking/configuring-networks/

- Activation d'une nouvelle configuration Netplan :  
  https://netplan.readthedocs.io/en/stable/

## NetworkManager et `nmcli`

- Manuel officiel de `nmcli` :  
  https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html

- Exemples officiels de commandes `nmcli` :  
  https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli-examples.html

- Documentation générale de NetworkManager :  
  https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/

## Outils réseau Linux

- `iproute2` :  
  https://www.kernel.org/pub/linux/utils/net/iproute2/

- Documentation système de `resolvectl` :  
  https://www.freedesktop.org/software/systemd/man/latest/resolvectl.html

- Pages de manuel Linux :  
  https://man7.org/linux/man-pages/

## Comment utiliser ces ressources

Lorsqu'une commande ou une option n'est pas reconnue :

1. vérifiez la version de votre distribution ;
2. vérifiez si le paquet ou le service correspondant est installé ;
3. consultez l'aide locale de la commande ;
4. lisez la documentation de la version concernée ;
5. vérifiez quel service gère réellement l'interface.

Une commande qui fonctionne sur une version récente d'Ubuntu peut ne pas exister ou se comporter différemment sur une ancienne distribution ou un système minimal.


# Conclusion

La maîtrise du réseau Linux commence par une méthode de diagnostic rigoureuse. Avant de modifier une interface, il faut savoir identifier le matériel ou le périphérique virtuel, lire les adresses, comprendre le préfixe, vérifier la route, distinguer une panne DNS d'une panne IP et connaître le gestionnaire responsable de la configuration.

**Netplan** fournit une configuration déclarative fondée sur YAML et transmet les paramètres au moteur réseau choisi. **NetworkManager**, piloté notamment par `nmcli`, permet de gérer les profils de connexion et leur activation. Le bon outil dépend donc de l'architecture réelle du système.

Le critère de validation de ce niveau débutant est simple : vous devez être capable d'examiner la configuration d'une machine Linux, d'expliquer son chemin réseau, d'appliquer une configuration adaptée au laboratoire et de diagnostiquer méthodiquement une panne sans modifier les paramètres au hasard.

La suite logique sera d'approfondir les réseaux Linux : routes avancées, VLAN, bridges, bonds, IPv6, VPN, pare-feu, DNS avancé, routage multi-interface et automatisation des configurations.