
# Qu'est-ce qu'un réseau informatique ? — Niveau débutant

> **Parcours pédagogique :** Débutant → Intermédiaire → Expert  
> **Niveau actuel :** Débutant  
> **Objectif :** comprendre comment les équipements sont connectés, comment ils échangent des données et comment reconnaître les principaux composants d'un réseau informatique.


## Sommaire

1. Contexte et objectifs
2. Définition d'un réseau informatique
3. Pourquoi utiliser un réseau ?
4. Les principaux types de réseaux
5. Les équipements réseau
6. Câbles, fibres et connexions sans fil
7. Comprendre une adresse IP
8. Adresse MAC, switch et routeur
9. Comment les données circulent
10. Les protocoles essentiels
11. Comprendre Internet
12. Sécurité et bonnes pratiques
13. Atelier pratique
14. Dépannage pour débutants
15. Évaluation corrigée
16. Préparation du niveau intermédiaire


# 1. Contexte et objectifs

## 1.1 Pourquoi apprendre les réseaux ?

Les ordinateurs, téléphones, imprimantes, serveurs, téléviseurs connectés et équipements industriels ont souvent besoin d'échanger des informations.

Un ordinateur peut consulter un site Web, envoyer un document à une imprimante ou accéder à un serveur situé dans une autre ville. Pour cela, les équipements doivent pouvoir communiquer à travers une infrastructure adaptée.

Cette infrastructure constitue un réseau informatique.

Comprendre les réseaux est indispensable pour travailler en informatique, en cybersécurité, dans l'administration système, dans les télécommunications ou dans l'automatisation des infrastructures.

## 1.2 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

1. définir un réseau informatique ;
2. identifier les différents types de réseaux ;
3. reconnaître le rôle d'une carte réseau, d'un switch, d'un routeur et d'un point d'accès Wi-Fi ;
4. comprendre la différence entre une adresse IP et une adresse MAC ;
5. expliquer le rôle d'un masque de sous-réseau et d'une passerelle ;
6. comprendre comment un message devient une suite de données transportées sur un réseau ;
7. reconnaître les rôles de DNS, DHCP, TCP, UDP, IP et Ethernet ;
8. expliquer simplement le fonctionnement d'Internet ;
9. réaliser quelques vérifications réseau élémentaires ;
10. appliquer les premières règles de sécurité réseau.

## 1.3 Prérequis

Aucun prérequis réseau avancé n'est nécessaire.

Il est utile de savoir utiliser un ordinateur, ouvrir un terminal et identifier les appareils connectés à une box Internet.


# 2. Définition d'un réseau informatique

## 2.1 Qu'est-ce qu'un réseau ?

Un **réseau informatique** est un ensemble d'équipements capables d'échanger des données grâce à des moyens de communication et à des règles communes.

Ces équipements peuvent être :

- des ordinateurs ;
- des téléphones ;
- des imprimantes ;
- des serveurs ;
- des commutateurs ;
- des routeurs ;
- des caméras IP ;
- des objets connectés.

Les données peuvent circuler par des câbles en cuivre, des fibres optiques ou des liaisons radio comme le Wi-Fi.

Pour communiquer, les appareils ont besoin de règles communes appelées **protocoles réseau**.

## 2.2 Exemple simple

Dans une maison, un ordinateur portable et un téléphone se connectent au Wi-Fi d'une box Internet. Une télévision peut également utiliser cette connexion pour accéder à un service de diffusion vidéo.

Les appareils communiquent à travers un réseau local. La box ou le routeur permet aussi, selon sa configuration, de faire passer le trafic entre ce réseau local et le réseau du fournisseur d'accès à Internet.

Le réseau rend donc possible le partage de l'accès à Internet et la communication entre les appareils autorisés.

## 2.3 Les éléments indispensables

Un réseau repose généralement sur quatre catégories d'éléments :

**1. Les équipements terminaux :** ordinateurs, téléphones, serveurs, imprimantes.

**2. Les moyens de transmission :** câbles, fibres et ondes radio.

**3. Les équipements d'interconnexion :** switches, routeurs et points d'accès.

**4. Les protocoles :** règles qui indiquent comment les données sont adressées, transportées et interprétées.

Une liaison physique ne suffit donc pas. Les équipements doivent aussi être configurés de manière compatible.

## 2.4 Schéma d'un petit réseau

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="365" viewBox="0 0 960 365" role="img" aria-labelledby="begin-network-title begin-network-desc">
  <title id="begin-network-title">Exemple de réseau informatique simple</title>
  <desc id="begin-network-desc">Deux ordinateurs et une imprimante sont connectés à un switch. Le switch est relié à un routeur, qui permet d'accéder à Internet. Les flux sont représentés par des flèches à tirets animés, sans objet mobile.</desc>
  <defs>
    <marker id="bn-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .bn-device{fill:#17263a;stroke:#60a5fa;stroke-width:2}
      .bn-network{fill:#123126;stroke:#4ade80;stroke-width:2}
      .bn-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .bn-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .bn-line{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#bn-arrow);animation:bn-dash 1.8s linear infinite}
      @keyframes bn-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="363" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">UN RÉSEAU LOCAL CONNECTÉ À INTERNET</text>
  <rect class="bn-device" x="35" y="78" width="170" height="72" rx="10"/>
  <text class="bn-title" x="120" y="108" text-anchor="middle">Ordinateur A</text>
  <text class="bn-text" x="120" y="130" text-anchor="middle">Client</text>
  <rect class="bn-device" x="35" y="178" width="170" height="72" rx="10"/>
  <text class="bn-title" x="120" y="208" text-anchor="middle">Ordinateur B</text>
  <text class="bn-text" x="120" y="230" text-anchor="middle">Client</text>
  <rect class="bn-device" x="270" y="128" width="170" height="72" rx="10"/>
  <text class="bn-title" x="355" y="158" text-anchor="middle">Switch</text>
  <text class="bn-text" x="355" y="180" text-anchor="middle">Réseau local</text>
  <rect class="bn-device" x="270" y="258" width="170" height="65" rx="10"/>
  <text class="bn-title" x="355" y="285" text-anchor="middle">Imprimante</text>
  <text class="bn-text" x="355" y="305" text-anchor="middle">Partagée</text>
  <rect class="bn-device" x="520" y="128" width="170" height="72" rx="10"/>
  <text class="bn-title" x="605" y="158" text-anchor="middle">Routeur</text>
  <text class="bn-text" x="605" y="180" text-anchor="middle">Passage entre réseaux</text>
  <rect class="bn-network" x="770" y="128" width="150" height="72" rx="10"/>
  <text class="bn-title" x="845" y="158" text-anchor="middle">Internet</text>
  <text class="bn-text" x="845" y="180" text-anchor="middle">Réseaux distants</text>
  <path class="bn-line" d="M205 114 L262 150"/>
  <path class="bn-line" d="M205 214 L262 180"/>
  <path class="bn-line" d="M355 200 V251"/>
  <path class="bn-line" d="M440 164 H512"/>
  <path class="bn-line" d="M690 164 H762"/>
  <text class="bn-text" x="480" y="345" text-anchor="middle">Les connexions physiques permettent les échanges ; les protocoles organisent la communication.</text>
</svg>

### Comment lire le schéma, étape par étape

Ce dessin représente un petit réseau local (LAN, *Local Area Network*) qui peut aussi communiquer avec des réseaux distants. Pour bien le comprendre, suivons le rôle des équipements et le trajet des données.

**Étape 1 — Les ordinateurs sont des clients.**  
Les ordinateurs A et B peuvent demander un service, comme imprimer un document ou ouvrir un site Web. « Client » décrit leur rôle dans un échange ; cela ne signifie pas qu'ils ne peuvent jamais recevoir de données.

**Étape 2 — Le switch relie le réseau local.**  
Chaque ordinateur dispose de sa propre liaison vers le switch. Un switch Ethernet de couche 2 transmet les trames dans le réseau local en s'appuyant notamment sur les adresses MAC. Il permet aux équipements du même réseau local de communiquer sans faire passer chaque échange par le routeur.

**Étape 3 — L'imprimante est une ressource locale partagée.**  
Pour imprimer, le trajet simplifié est : ordinateur A → switch → imprimante. La réponse de l'imprimante revient ensuite vers le poste. Cet échange ne nécessite pas Internet, à condition que l'imprimante soit correctement connectée et autorisée.

**Étape 4 — Le routeur permet de joindre un autre réseau.**  
Pour consulter un site situé à l'extérieur du LAN, l'ordinateur A envoie les données au switch, puis à sa passerelle par défaut — représentée ici par le routeur. Le routeur examine l'adresse IP de destination et choisit où transmettre les paquets. Le trafic poursuit ensuite son chemin à travers d'autres équipements et réseaux, non détaillés ici.

**Étape 5 — Internet représente plusieurs réseaux interconnectés.**  
Le bloc « Internet » n'est ni un appareil unique ni un câble. Il représente un ensemble de réseaux. Les réponses d'un service distant reviennent vers le réseau d'origine, même si ce trajet de retour n'est pas dessiné.

**Comment interpréter les flèches ?**  
Les flèches animées donnent un trajet simplifié à suivre ; l'animation est un effet visuel, pas la preuve qu'un transfert est en cours. Une flèche orientée dans un seul sens ne signifie pas que le câble ne transporte des données que dans ce sens : les communications nécessitent généralement des échanges dans les deux sens. Le dessin ne montre pas chaque protocole, chaque adresse ni tous les équipements intermédiaires.

**À retenir :** le switch organise les échanges locaux, tandis que le routeur achemine les paquets IP entre réseaux. Les liaisons physiques transportent les signaux ; Ethernet, IP et les protocoles des applications définissent comment les données sont transportées et interprétées.

# 3. Pourquoi utiliser un réseau ?

## 3.1 Partager des ressources

Un réseau permet à plusieurs personnes d'utiliser des ressources communes :

- une imprimante ;
- des dossiers partagés ;
- un serveur de fichiers ;
- une application d'entreprise ;
- une connexion Internet.

Cela évite de devoir transférer systématiquement les informations à l'aide d'une clé USB ou de reproduire les mêmes fichiers sur chaque ordinateur.

## 3.2 Communiquer

Les réseaux permettent les appels vidéo, le courrier électronique, la messagerie, les jeux en ligne et l'accès à des applications distantes.

## 3.3 Centraliser les services

Une organisation peut utiliser des serveurs centraux pour l'authentification, le stockage, la sauvegarde, la supervision et les applications.

Les postes clients utilisent alors des services communs selon les permissions accordées.

## 3.4 Faciliter l'administration

Les équipes informatiques peuvent surveiller les équipements, déployer des configurations, mesurer les performances et détecter des incidents.

L'administration à distance doit cependant être protégée : un réseau connecté n'est pas automatiquement un réseau sûr.


# 4. Les principaux types de réseaux

## 4.1 LAN : Local Area Network

Un LAN est un réseau local couvrant généralement une zone limitée, par exemple une maison, un laboratoire ou un bâtiment.

Un réseau Ethernet de bureau et un réseau Wi-Fi résidentiel peuvent faire partie d'un LAN.

## 4.2 WLAN : Wireless LAN

Un WLAN est un réseau local sans fil, généralement fondé sur le Wi-Fi.

Les équipements échangent des données par radio avec un point d'accès ou un routeur Wi-Fi.

Le Wi-Fi remplace le câble sur le segment radio ; il ne remplace pas les protocoles IP, TCP, UDP et les autres protocoles nécessaires aux applications.

## 4.3 WAN : Wide Area Network

Un WAN relie des réseaux éloignés géographiquement.

Une entreprise peut relier plusieurs agences à travers un réseau d'opérateur, des liaisons privées ou des connexions Internet sécurisées.

Internet est un réseau mondial de réseaux interconnectés, mais tous les WAN ne sont pas Internet.

## 4.4 PAN : Personal Area Network

Un PAN relie des équipements personnels à courte portée, par exemple avec Bluetooth.

## 4.5 Réseau local et réseau étendu

| Type | Étendue indicative | Exemple |
|---|---|---|
| PAN | Très courte portée | Écouteurs Bluetooth et téléphone |
| LAN | Zone locale | Réseau d'un bureau |
| WLAN | LAN sans fil | Wi-Fi d'une maison |
| WAN | Sites éloignés | Réseau reliant plusieurs agences |
| Internet | Mondiale | Interconnexion de réseaux publics et privés |

Ces catégories décrivent surtout la portée et le contexte du réseau. Elles ne définissent pas, à elles seules, le niveau de sécurité.


# 5. Les équipements réseau

## 5.1 Carte réseau

La carte réseau, ou NIC (*Network Interface Card*), permet à un appareil de se connecter à un réseau Ethernet, Wi-Fi ou à un autre moyen de communication pris en charge.

Elle peut être intégrée à la carte mère ou ajoutée séparément.

## 5.2 Switch : commutateur

Un switch connecte plusieurs équipements dans un réseau local Ethernet.

Il apprend généralement les adresses MAC sources observées sur ses ports et utilise sa table de commutation pour transmettre les trames vers les ports appropriés.

Un switch ne doit pas être confondu avec un routeur. Un switch de couche 2 transporte les trames dans le même domaine de commutation ; un switch de couche 3 peut également router des paquets entre des réseaux selon sa configuration.

## 5.3 Routeur

Un routeur permet de transmettre des paquets IP d'un réseau à un autre.

Il examine notamment l'adresse IP de destination et consulte sa table de routage pour choisir le prochain saut ou l'interface de sortie.

Dans une maison, la box Internet réunit souvent plusieurs fonctions : routeur, switch Ethernet, point d'accès Wi-Fi, pare-feu et autres services. Dans les infrastructures professionnelles, ces fonctions sont fréquemment séparées.

## 5.4 Point d'accès Wi-Fi

Un point d'accès Wi-Fi permet à des équipements sans fil de rejoindre un réseau local.

Il relie le segment radio à une infrastructure réseau. Il ne faut pas le confondre avec un modem ou un routeur, même si certains appareils combinent toutes ces fonctions.

## 5.5 Modem et box Internet

Un modem ou un terminal d'accès réalise l'adaptation nécessaire à la technologie utilisée par le fournisseur d'accès, selon le type de liaison.

Le matériel fourni à la maison peut intégrer un modem ou un terminal optique, un routeur, un switch, un point d'accès Wi-Fi et un pare-feu.

## 5.6 Pare-feu

Un pare-feu applique une politique de sécurité aux communications. Il peut autoriser ou bloquer des flux en fonction d'attributs comme les adresses, protocoles, ports et états de connexion.

Il ne suffit pas d'avoir un pare-feu pour rendre toute l'infrastructure sûre : les règles doivent être correctes et les équipements doivent être maintenus.


# 6. Câbles, fibres et connexions sans fil

## 6.1 Ethernet sur cuivre

Les câbles Ethernet à paires torsadées sont fréquents dans les bâtiments. Ils relient les ordinateurs, téléphones IP, points d'accès et commutateurs.

La distance, le débit et les performances dépendent de la catégorie du câble, de la qualité de l'installation et des interfaces utilisées.

## 6.2 Fibre optique

La fibre transmet les données à l'aide de signaux lumineux. Elle est utilisée notamment pour les liaisons longues distances, les dorsales et les interconnexions à haut débit.

Les modules optiques, le type de fibre, la longueur d'onde, la distance et les caractéristiques des interfaces doivent être compatibles.

## 6.3 Wi-Fi

Le Wi-Fi transmet les données par ondes radio. Il évite le câblage de certains terminaux, mais ses performances dépendent de la couverture, des interférences, de la bande utilisée, de la capacité radio et du nombre de clients.

Une bonne puissance du signal ne garantit pas à elle seule une connexion rapide. La congestion et les problèmes d'accès au canal peuvent également limiter les performances.


# 7. Comprendre une adresse IP

## 7.1 À quoi sert une adresse IP ?

Une adresse IP identifie une interface dans le contexte d'un réseau IP. Elle permet notamment d'adresser les paquets pour qu'ils puissent atteindre leur destination.

Il existe deux principales versions du protocole IP :

- IPv4, avec des adresses de 32 bits ;
- IPv6, avec des adresses de 128 bits.

Dans un réseau IPv4, une adresse est généralement écrite sous la forme de quatre nombres séparés par des points.

Exemple :

```text
192.168.1.10
```

Chaque nombre représente un octet et se situe entre 0 et 255.

## 7.2 Adresse, masque et préfixe

L'adresse IP ne doit pas être interprétée sans le préfixe ou le masque qui détermine la partie réseau.

Exemple :

```text
192.168.1.10/24
```

Le `/24` indique que les 24 premiers bits forment le préfixe du réseau.

Dans ce cas, le réseau est `192.168.1.0/24`.

Les adresses utilisables par les hôtes dans ce sous-réseau IPv4 classique sont généralement `192.168.1.1` à `192.168.1.254`. Les adresses `.0` et `.255` correspondent respectivement à l'adresse de réseau et à l'adresse de broadcast pour ce /24, dans le modèle IPv4 de diffusion classique.

## 7.3 Les plages IPv4 privées

Trois plages sont réservées à l'usage privé dans les réseaux IPv4 :

| Plage | Préfixe | Usage fréquent |
|---|---|---|
| `10.0.0.0` à `10.255.255.255` | `10.0.0.0/8` | Grands réseaux privés |
| `172.16.0.0` à `172.31.255.255` | `172.16.0.0/12` | Réseaux privés |
| `192.168.0.0` à `192.168.255.255` | `192.168.0.0/16` | Maisons et petites infrastructures |

Ces plages sont définies par la RFC 1918. Elles ne sont pas globalement routables sur l'Internet public, même si des mécanismes comme le NAT permettent souvent à des appareils qui les utilisent d'accéder à Internet.

## 7.4 Adresse IP et adresse MAC

L'adresse IP sert à l'adressage au niveau IP. L'adresse MAC identifie une interface dans le contexte de la couche liaison, notamment sur Ethernet.

Exemple fictif :

```text
Adresse IP  : 192.168.1.10
Adresse MAC : 02:00:00:00:00:10
```

L'adresse MAC réelle peut différer. Ces valeurs ne doivent pas être utilisées pour identifier un véritable appareil.

Il ne faut pas dire que l'adresse MAC est toujours physique ou immuable : les systèmes peuvent utiliser des adresses administrées localement et des mécanismes de randomisation.

## 7.5 La passerelle par défaut

Lorsqu'un ordinateur doit atteindre une destination qui n'appartient pas à son réseau local, il envoie généralement le trafic vers une passerelle par défaut.

La passerelle est souvent une interface de routeur située sur le même sous-réseau local.

Exemple :

```text
Ordinateur : 192.168.1.10/24
Passerelle  : 192.168.1.1
```

Cette configuration est illustrative. Une adresse de passerelle doit être choisie selon le plan d'adressage réel.


# 8. Adresse MAC, switch et routeur

## 8.1 Comment un switch apprend

Lorsqu'une trame arrive sur un port Ethernet, un switch de couche 2 peut apprendre l'adresse MAC source et l'associer au port d'entrée.

Pour transmettre une trame, il consulte sa table de commutation.

Si l'adresse de destination est connue, il transmet la trame sur le port correspondant, dans le VLAN concerné. Si la destination est inconnue, il peut diffuser la trame sur les ports appropriés du VLAN, à l'exception du port d'entrée. Le comportement dépend des fonctions et de la configuration du switch.

## 8.2 Comment un routeur choisit la destination

Un routeur consulte une table de routage. Il cherche la route la plus spécifique qui correspond à la destination.

Il détermine ensuite l'interface de sortie et, le cas échéant, le prochain saut.

Lorsqu'un paquet traverse un routeur IPv4 ou IPv6, l'adresse IP source et l'adresse IP de destination restent normalement identiques de bout en bout, sauf mécanismes particuliers tels que NAT. En revanche, l'enveloppe de couche liaison est reconstruite pour le lien suivant.

## 8.3 Schéma : switch et routeur

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="355" viewBox="0 0 960 355" role="img" aria-labelledby="switch-router-title switch-router-desc">
  <title id="switch-router-title">Différence entre switch et routeur</title>
  <desc id="switch-router-desc">Deux ordinateurs communiquent dans le même réseau local à travers un switch. Pour atteindre un réseau distant, le trafic passe par le routeur. Les flux sont indiqués par des tirets animés directionnels, sans particule mobile.</desc>
  <defs>
    <marker id="sr-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .sr-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .sr-net{fill:#123126;stroke:#4ade80;stroke-width:2}
      .sr-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .sr-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .sr-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#sr-arrow);animation:sr-dash 1.8s linear infinite}
      @keyframes sr-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="353" rx="16" fill="#0b1220" stroke="#334155"/>
  <rect class="sr-box" x="25" y="86" width="180" height="75" rx="10"/>
  <text class="sr-title" x="115" y="115" text-anchor="middle">PC A</text>
  <text class="sr-text" x="115" y="138" text-anchor="middle">192.168.1.10/24</text>
  <rect class="sr-box" x="25" y="202" width="180" height="75" rx="10"/>
  <text class="sr-title" x="115" y="231" text-anchor="middle">PC B</text>
  <text class="sr-text" x="115" y="254" text-anchor="middle">192.168.1.20/24</text>
  <rect class="sr-box" x="270" y="135" width="185" height="86" rx="10"/>
  <text class="sr-title" x="362" y="168" text-anchor="middle">Switch</text>
  <text class="sr-text" x="362" y="192" text-anchor="middle">Commutation L2</text>
  <rect class="sr-net" x="535" y="135" width="185" height="86" rx="10"/>
  <text class="sr-title" x="627" y="168" text-anchor="middle">Routeur</text>
  <text class="sr-text" x="627" y="192" text-anchor="middle">Routage IP</text>
  <rect class="sr-box" x="790" y="135" width="145" height="86" rx="10"/>
  <text class="sr-title" x="862" y="168" text-anchor="middle">Réseau distant</text>
  <text class="sr-text" x="862" y="192" text-anchor="middle">Autre préfixe</text>
  <path class="sr-flow" d="M205 123 L262 157"/>
  <path class="sr-flow" d="M205 239 L262 199"/>
  <path class="sr-flow" d="M455 178 H527"/>
  <path class="sr-flow" d="M720 178 H782"/>
  <text class="sr-text" x="480" y="307" text-anchor="middle">Même sous-réseau : le switch transporte les trames locales.</text>
  <text class="sr-text" x="480" y="328" text-anchor="middle">Destination hors sous-réseau : le poste envoie le paquet vers sa passerelle.</text>
</svg>


# 9. Comment les données circulent

## 9.1 Des applications aux données transportées

Lorsqu'un utilisateur consulte un site Web, plusieurs couches coopèrent.

L'application crée une demande. Les protocoles de transport et IP participent à l'acheminement des données. La couche de liaison transporte les paquets sur le support local.

Pour les réseaux IP, on peut parler de paquets IP. Sur Ethernet, ces paquets sont transportés dans des trames Ethernet. Les termes ne désignent pas exactement le même élément.

## 9.2 Encapsulation simplifiée

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="385" viewBox="0 0 960 385" role="img" aria-labelledby="encap-title encap-desc">
  <title id="encap-title">Encapsulation des données</title>
  <desc id="encap-desc">Les données applicatives sont transportées dans un segment ou datagramme de transport, lui-même transporté dans un paquet IP, puis une trame de liaison. Les couches ajoutent leurs informations de contrôle selon le protocole utilisé.</desc>
  <defs>
    <style>
      .en-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .en-app{fill:#123126;stroke:#4ade80;stroke-width:2}
      .en-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .en-text{font:13px Arial,sans-serif;fill:#cbd5e1}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="383" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">UNE DONNÉE EST ENCAPSULÉE AU FIL DES COUCHES</text>
  <rect class="en-app" x="105" y="65" width="750" height="50" rx="8"/>
  <text class="en-title" x="480" y="95" text-anchor="middle">Données de l'application</text>
  <rect class="en-box" x="105" y="130" width="750" height="58" rx="8"/>
  <rect x="105" y="130" width="185" height="58" rx="8" fill="#27405f" stroke="#60a5fa" stroke-width="2"/>
  <text class="en-text" x="197" y="154" text-anchor="middle">En-tête transport</text>
  <text class="en-text" x="197" y="173" text-anchor="middle">Ports TCP/UDP</text>
  <text class="en-text" x="570" y="164" text-anchor="middle">Segment TCP ou datagramme UDP</text>
  <rect class="en-box" x="105" y="203" width="750" height="58" rx="8"/>
  <rect x="105" y="203" width="185" height="58" rx="8" fill="#27405f" stroke="#60a5fa" stroke-width="2"/>
  <text class="en-text" x="197" y="227" text-anchor="middle">En-tête IP</text>
  <text class="en-text" x="197" y="246" text-anchor="middle">Adresses IP</text>
  <text class="en-text" x="570" y="237" text-anchor="middle">Paquet IP</text>
  <rect class="en-box" x="105" y="276" width="750" height="58" rx="8"/>
  <rect x="105" y="276" width="185" height="58" rx="8" fill="#27405f" stroke="#60a5fa" stroke-width="2"/>
  <text class="en-text" x="197" y="300" text-anchor="middle">En-tête liaison</text>
  <text class="en-text" x="197" y="319" text-anchor="middle">MAC + contrôle</text>
  <text class="en-text" x="570" y="310" text-anchor="middle">Trame Ethernet, dans cet exemple</text>
  <text class="en-text" x="480" y="361" text-anchor="middle">Le détail dépend des protocoles ; tous les flux ne suivent pas exactement le même chemin.</text>
</svg>

## 9.3 Que se passe-t-il lorsqu'un ordinateur ouvre un site Web ?

Dans un scénario classique, plusieurs événements se produisent :

1. le poste doit connaître l'adresse IP de destination, souvent grâce à DNS ;
2. il détermine si la destination se trouve sur son réseau local ;
3. si nécessaire, il résout l'adresse de couche liaison du prochain saut, par exemple avec ARP en IPv4 sur Ethernet ;
4. il transmet les données à travers la liaison locale ;
5. les routeurs intermédiaires acheminent les paquets vers le réseau de destination ;
6. le serveur répond selon le protocole utilisé.

Le chemin réel dépend du type de connexion, des caches, du protocole de transport, des mécanismes de sécurité et de l'architecture de réseau.


# 10. Les protocoles essentiels

## 10.1 IP : Internet Protocol

IP permet d'adresser et d'acheminer les paquets entre les réseaux.

Il existe deux versions courantes : IPv4 et IPv6. Chaque version a ses propres règles d'adressage et certains mécanismes différents.

## 10.2 TCP et UDP

**TCP** fournit un transport orienté connexion avec des mécanismes de livraison ordonnée et de retransmission.

**UDP** fournit un transport sans connexion au niveau de cette couche. Il ne garantit pas à lui seul la livraison, l'ordre ou l'absence de duplication.

Les applications choisissent le protocole adapté à leurs besoins.

## 10.3 DNS

DNS associe des noms à des informations, notamment des adresses IP.

Quand un utilisateur saisit le nom d'un site, son appareil ou un résolveur cherche la donnée nécessaire dans le système DNS. DNS ne transporte pas lui-même toute la page Web : il aide à trouver les informations d'adressage.

## 10.4 DHCP

DHCP permet généralement d'attribuer automatiquement des paramètres réseau aux clients.

Ces paramètres peuvent inclure :

- une adresse IP ;
- un masque ou préfixe ;
- une passerelle ;
- des serveurs DNS ;
- une durée de bail.

DHCP réduit le besoin de configurer manuellement chaque terminal, mais ses serveurs, relais et plages d'adresses doivent être correctement administrés.

## 10.5 ARP et NDP

ARP permet, dans un réseau IPv4, de découvrir l'adresse de couche liaison associée à une adresse IPv4 sur le lien local.

En IPv6, la découverte du voisin et la résolution de couche liaison utilisent notamment NDP (*Neighbor Discovery Protocol*), qui s'appuie sur ICMPv6.

Ces mécanismes ne sont pas utilisés pour résoudre directement une adresse MAC vers une adresse IP à travers tout Internet : ils servent dans le contexte du lien local.

## 10.6 HTTP et HTTPS

HTTP est utilisé pour les échanges entre clients et serveurs Web.

HTTPS protège HTTP au moyen de TLS. Un certificat correctement vérifié permet notamment au client de vérifier l'identité du serveur selon la chaîne de confiance.

HTTPS protège le transport, mais ne signifie pas automatiquement que le site ou l'application est fiable.

## 10.7 Tableau récapitulatif

| Protocole | Fonction principale | Exemple d'utilisation |
|---|---|---|
| Ethernet | Communication sur un lien local câblé | Poste connecté à un switch |
| Wi-Fi | Accès local sans fil | Téléphone connecté au point d'accès |
| IP | Adressage et acheminement des paquets | Communication entre réseaux |
| TCP | Transport fiable et ordonné | De nombreux échanges Web |
| UDP | Transport sans connexion | DNS classique, certains flux temps réel |
| DHCP | Attribution de paramètres réseau | Adresse IP automatique |
| DNS | Résolution de noms | Nom d'un site vers une adresse |
| ARP | Résolution de voisin IPv4 sur le lien local | Trouver le MAC du prochain saut |
| NDP | Découverte de voisins IPv6 | Résolution et découverte sur IPv6 |
| HTTP/HTTPS | Échanges d'applications Web | Navigateur et serveur Web |


# 11. Comprendre Internet

## 11.1 Internet est un réseau de réseaux

Internet n'est pas un seul routeur ou un seul serveur. Il relie des réseaux indépendants capables d'échanger du trafic grâce à des technologies, des accords et des protocoles communs.

Les fournisseurs d'accès, les opérateurs, les entreprises, les universités et les fournisseurs de contenu gèrent différentes parties de cette infrastructure.

Les routeurs transmettent les paquets selon leurs tables de routage. Le chemin peut changer si la topologie ou les politiques de routage changent.

## 11.2 Adresse privée et accès public

Les appareils utilisant des adresses IPv4 privées accèdent souvent à Internet à travers un routeur qui réalise de la traduction d'adresses, appelée NAT.

Le NAT n'est pas un substitut à un pare-feu ni une garantie de sécurité. Les règles de filtrage et la gestion des services exposés restent importantes.

IPv6 permet un modèle d'adressage beaucoup plus vaste. Son utilisation doit également tenir compte des règles de filtrage et de la configuration de sécurité.

## 11.3 Pourquoi un site peut-il être inaccessible ?

Une panne peut provenir de différentes couches :

- le poste n'a pas d'adresse IP valide ;
- la passerelle est inaccessible ;
- DNS ne résout pas le nom ;
- un pare-feu bloque la connexion ;
- une route manque ;
- le serveur distant est indisponible ;
- TLS ou l'application rencontre une erreur.

Le bon diagnostic commence donc par identifier à quelle étape la communication échoue.


# 12. Sécurité et bonnes pratiques

## 12.1 Protéger les accès

Utilisez des mots de passe robustes et uniques, l'authentification multifacteur lorsqu'elle est disponible et des comptes individuels.

Ne partagez pas les identifiants administrateur et désactivez les accès inutilisés selon la politique de l'organisation.

## 12.2 Sécuriser le Wi-Fi

Utilisez les mécanismes de sécurité modernes pris en charge par les équipements et maintenez leur logiciel à jour.

Changez les identifiants par défaut et évitez d'exposer l'interface d'administration sur des réseaux non fiables.

## 12.3 Mettre à jour les équipements

Les routeurs, points d'accès, switches et pare-feu doivent être maintenus selon une procédure de mise à jour et de sauvegarde.

Un équipement ancien ou non corrigé peut exposer le réseau à des vulnérabilités.

## 12.4 Principe du moindre privilège

Un utilisateur ou un appareil ne doit disposer que des droits nécessaires.

Dans une entreprise, les réseaux des utilisateurs, des invités, des serveurs et de l'administration peuvent être séparés pour limiter la portée d'un incident.

## 12.5 Sauvegarder les configurations

Conservez des sauvegardes protégées et testez les procédures de restauration.

Une sauvegarde qui n'a jamais été vérifiée n'est pas une garantie de récupération.


# 13. Atelier pratique

## Situation

Vous devez vérifier la connexion d'un ordinateur à un réseau local et à Internet.

Ne modifiez pas les paramètres d'un réseau d'entreprise sans autorisation.

## Étape A — Vérifier l'adresse IP

Sous Windows :

```powershell
ipconfig
```

Sous Linux :

```bash
ip addr
ip route
```

Ces commandes permettent de consulter les adresses et certains paramètres réseau. Leur sortie varie selon le système.

## Étape B — Identifier la passerelle

Sur Windows :

```powershell
ipconfig
route print
```

Sur Linux :

```bash
ip route
```

Recherchez la route par défaut ou la passerelle prévue.

## Étape C — Tester la pile IP locale

```bash
ping 127.0.0.1
```

Cette adresse de boucle locale vérifie certains éléments du fonctionnement IP sur la machine. Elle ne prouve pas que la carte réseau ou la connexion Internet fonctionne.

## Étape D — Tester la passerelle

```bash
ping <ADRESSE_DE_LA_PASSERELLE>
```

Remplacez la valeur par la passerelle réellement configurée.

Un échec ne prouve pas toujours que le réseau est en panne : certains équipements filtrent ICMP. Il faut examiner les autres indices.

## Étape E — Tester la résolution DNS

```bash
nslookup example.com
```

Cette commande permet de consulter le résultat de la résolution DNS. La sortie exacte dépend du système et du résolveur.

## Étape F — Examiner le chemin

Sous Windows :

```powershell
tracert example.com
```

Sous Linux :

```bash
traceroute example.com
```

Selon la distribution, `traceroute` peut nécessiter une installation. Certaines politiques réseau bloquent les sondes utilisées par ces commandes ; les sauts non affichés ne prouvent donc pas que tous les routeurs intermédiaires sont en panne.

## Résultat attendu

Vous devez pouvoir dire si le problème semble concerner :

- l'adresse ou la configuration locale ;
- la passerelle ;
- la résolution DNS ;
- le chemin vers la destination ;
- ou le service distant.

Ne concluez pas qu'un site fonctionne correctement uniquement parce que le ping réussit : le ping et le service applicatif testent des éléments différents.


# 14. Dépannage pour débutants

## 14.1 L'ordinateur ne reçoit pas d'adresse IP

Vérifiez l'état du lien, la connexion Wi-Fi ou Ethernet, les paramètres DHCP et les informations affichées par le système.

Ne définissez pas une adresse arbitraire sur un réseau partagé : une adresse en doublon peut perturber un autre appareil.

## 14.2 L'adresse IP existe, mais Internet ne fonctionne pas

Vérifiez la passerelle, les routes, les restrictions de sécurité et la connectivité au-delà du réseau local.

## 14.3 Les sites ne s'ouvrent pas par leur nom

Testez la résolution DNS et comparez son résultat aux paramètres attendus.

Une connexion IP fonctionnelle ne garantit pas que DNS fonctionne, et une erreur DNS n'indique pas nécessairement une panne du lien physique.

## 14.4 Le Wi-Fi est connecté, mais le débit est faible

Vérifiez le signal, les interférences, le nombre de clients, la bande utilisée et l'état de la liaison vers le réseau filaire.

La mention « connecté » ne signifie pas que l'accès aux services est rapide ou fiable.


# 15. Évaluation corrigée

## Questions

1. Qu'est-ce qu'un réseau informatique ?
2. Quelle différence existe entre un switch et un routeur ?
3. Quel est le rôle d'une adresse IP ?
4. À quoi sert une adresse MAC ?
5. Que signifie le préfixe `/24` dans `192.168.1.10/24` ?
6. Quel est le rôle de la passerelle par défaut ?
7. Quelle différence existe entre TCP et UDP ?
8. Quel est le rôle de DNS ?
9. Quel est le rôle de DHCP ?
10. Pourquoi un ping réussi ne garantit-il pas que le site Web fonctionne ?
11. Pourquoi ne faut-il pas désactiver la validation des certificats TLS pour corriger un problème d'accès ?
12. Pourquoi une sauvegarde de configuration doit-elle être testée ?

## Corrigé

**1. Réseau informatique**

Ensemble d'équipements qui échangent des données à travers des supports de communication et des protocoles.

**2. Switch et routeur**

Un switch de couche 2 transmet les trames dans un domaine de commutation ; un routeur transmet des paquets IP entre réseaux.

**3. Adresse IP**

Elle permet d'adresser et d'acheminer les paquets IP.

**4. Adresse MAC**

Elle sert à identifier une interface dans le contexte de la couche liaison, notamment sur Ethernet.

**5. `/24`**

Les 24 premiers bits forment le préfixe réseau.

**6. Passerelle par défaut**

Elle est utilisée pour atteindre les destinations qui ne sont pas considérées comme directement accessibles sur le réseau local.

**7. TCP et UDP**

TCP fournit un transport orienté connexion avec livraison ordonnée et retransmission. UDP offre un transport sans connexion sans garantie de livraison ou d'ordre au niveau du protocole lui-même.

**8. DNS**

Il permet notamment d'obtenir les informations d'adressage associées à des noms.

**9. DHCP**

Il fournit automatiquement des paramètres de configuration IP aux clients.

**10. Limite du ping**

Le ping teste ICMP, pas nécessairement la résolution DNS, le port applicatif, TLS ou le fonctionnement du site.

**11. Validation TLS**

La désactiver peut rendre la connexion vulnérable à une interception et masque le problème réel d'identité ou de confiance du serveur.

**12. Sauvegarde testée**

Il faut confirmer que la sauvegarde est disponible, exploitable et qu'elle permet une restauration correcte.


# 16. Préparation du niveau intermédiaire

Le niveau intermédiaire approfondira :

- les couches du modèle OSI et de la suite TCP/IP ;
- le fonctionnement détaillé d'Ethernet et des VLAN ;
- les masques IPv4 et le calcul des sous-réseaux ;
- ARP, DHCP, DNS et les tables de commutation ;
- les tables de routage ;
- TCP, UDP et les ports ;
- les bases d'IPv6 ;
- les outils de diagnostic structurés.

**À retenir :** un réseau permet aux équipements de communiquer, mais sa fiabilité dépend de l'adressage, des protocoles, des équipements d'interconnexion, de la configuration et des contrôles de sécurité.


## Références utiles

- IANA — Registres des protocoles : https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
- RFC 1918 — Adresses IPv4 privées : https://www.rfc-editor.org/rfc/rfc1918.html
- RFC 826 — ARP : https://www.rfc-editor.org/rfc/rfc826.html
- RFC 2131 — DHCP : https://www.rfc-editor.org/rfc/rfc2131.html
- RFC 1034 — Concepts DNS : https://www.rfc-editor.org/rfc/rfc1034.html
- RFC 8200 — IPv6 : https://www.rfc-editor.org/rfc/rfc8200.html
- Documentation Microsoft sur les commandes réseau : https://learn.microsoft.com/windows-server/administration/windows-commands/windows-commands

**Fichier :** `intro-reseau-debutant.md`  
**Niveau :** Débutant  
**Fin du cours**
