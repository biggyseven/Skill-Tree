
# Le matériel réseau — Niveau débutant

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Niveau actuel :** Débutant  
> **Objectif :** reconnaître les équipements réseau, comprendre leur rôle, identifier les principaux ports et câbles, et apprendre à vérifier une installation élémentaire.

---

## Sommaire

1. Contexte et objectifs
2. Qu'est-ce que le matériel réseau ?
3. Les équipements essentiels
4. Switch, routeur et point d'accès : les différences
5. Les supports de transmission
6. Les ports, interfaces et voyants
7. Alimentation et PoE
8. Les composants d'un équipement professionnel
9. Exemple d'installation réseau
10. Installation et précautions
11. Premiers diagnostics
12. Atelier pratique
13. Évaluation corrigée
14. Préparation du niveau intermédiaire

---

# 1. Contexte et objectifs

## 1.1 Pourquoi connaître le matériel réseau ?

Un réseau ne fonctionne pas uniquement grâce aux adresses IP et aux protocoles. Il repose également sur des équipements physiques qui transmettent, commutent, acheminent, sécurisent ou convertissent les communications.

Un câble défectueux peut interrompre une connexion. Un port trop lent peut limiter le débit. Un switch dont le budget PoE est insuffisant peut ne pas alimenter tous les points d'accès. Un module optique incompatible peut empêcher une liaison fibre de fonctionner.

Comprendre le matériel aide donc à installer, entretenir et dépanner une infrastructure réseau.

## 1.2 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

1. reconnaître un switch, un routeur, un point d'accès et un pare-feu ;
2. comprendre le rôle d'une carte réseau ;
3. distinguer un câble Ethernet en cuivre d'une fibre optique ;
4. identifier les principaux connecteurs réseau ;
5. comprendre les indications fournies par les voyants des ports ;
6. expliquer le rôle du PoE ;
7. reconnaître les composants d'un équipement monté en baie ;
8. réaliser une vérification physique élémentaire ;
9. éviter les erreurs courantes de branchement ;
10. préparer un diagnostic avant de remplacer un équipement.

## 1.3 Prérequis

Aucune expérience avancée n'est nécessaire. Vous devez simplement savoir reconnaître un ordinateur, un câble, une prise réseau et une alimentation électrique.

---

# 2. Qu'est-ce que le matériel réseau ?

Le **matériel réseau** désigne les équipements physiques et les composants qui permettent aux appareils de communiquer.

Il comprend notamment :

- les cartes réseau ;
- les commutateurs Ethernet, ou switches ;
- les routeurs ;
- les points d'accès Wi-Fi ;
- les pare-feu ;
- les modems et terminaux d'accès ;
- les câbles et connecteurs ;
- les modules optiques ;
- les systèmes d'alimentation et de refroidissement.

Chaque composant a une fonction particulière. Deux appareils peuvent se ressembler extérieurement tout en assurant des fonctions différentes.

Par exemple, une box Internet résidentielle peut réunir un routeur, un petit switch, un point d'accès Wi-Fi, un pare-feu et un terminal d'accès au fournisseur. Dans une entreprise, ces fonctions sont souvent réparties entre plusieurs équipements.

---

# 3. Les équipements essentiels

## 3.1 La carte réseau

La carte réseau, souvent appelée NIC (*Network Interface Card*), permet à un ordinateur ou à un serveur de se connecter à un réseau.

Elle peut être intégrée à la carte mère ou installée sous la forme d'une carte supplémentaire.

Une carte réseau peut proposer :

- un port Ethernet en cuivre ;
- une interface pour fibre optique ;
- une interface Wi-Fi ;
- plusieurs ports sur certains serveurs.

Chaque interface possède des caractéristiques propres : débit pris en charge, type de connecteur, fonctionnalités et pilote logiciel.

**Exemple :** un ordinateur équipé d'une interface Ethernet à 1 Gb/s ne peut pas exploiter directement un port de 10 Gb/s à son débit maximal si son interface reste le facteur limitant.

## 3.2 Le switch

Le switch, ou commutateur, connecte plusieurs appareils au sein d'un réseau local.

Il reçoit des trames Ethernet et les transmet vers les ports appropriés selon les informations de commutation et sa configuration.

Il sert notamment à connecter :

- les ordinateurs ;
- les imprimantes ;
- les serveurs ;
- les téléphones IP ;
- les points d'accès Wi-Fi ;
- d'autres switches.

Un switch ne remplace pas nécessairement un routeur. Un switch de couche 2 commute les trames dans les domaines de commutation concernés ; un switch de couche 3 peut également assurer le routage entre réseaux.

## 3.3 Le routeur

Le routeur relie des réseaux IP et transmet les paquets vers leur destination selon sa table de routage.

Il peut servir à relier :

- un réseau local à Internet ;
- plusieurs sites d'une entreprise ;
- différents réseaux internes ;
- un réseau d'entreprise à celui d'un opérateur.

Le routeur ne choisit pas son chemin en se fondant uniquement sur le nom de l'ordinateur. Il utilise des informations d'adressage et de routage.

## 3.4 Le point d'accès Wi-Fi

Le point d'accès, ou AP (*Access Point*), permet aux appareils sans fil de rejoindre un réseau.

Il est fréquent dans les bureaux, les écoles, les hôtels, les établissements de santé et les bâtiments publics.

Un point d'accès professionnel possède souvent un port Ethernet pour les données et, si le modèle le prend en charge, pour son alimentation PoE.

Le point d'accès n'est pas forcément le routeur du réseau : dans de nombreux déploiements, il fournit seulement l'accès radio, tandis que le routage est assuré par un autre équipement.

## 3.5 Le pare-feu

Un pare-feu applique une politique de sécurité aux communications.

Selon ses fonctions, il peut examiner les adresses, protocoles, ports, états de connexion et autres propriétés des flux afin de décider de les autoriser ou de les bloquer.

Le pare-feu peut être un appareil physique, une fonction intégrée à un routeur ou un service logiciel.

Sa présence ne garantit pas automatiquement la sécurité : les règles doivent être correctement conçues, maintenues et surveillées.

## 3.6 Le modem et le terminal d'accès

Un modem ou un terminal d'accès assure l'interface nécessaire avec la technologie de connexion du fournisseur.

Selon l'accès utilisé, il peut s'agir d'un équipement pour la fibre optique, le câble, le DSL ou une connexion radio.

Le terme exact dépend de la technologie. Un terminal optique, par exemple, réalise des fonctions différentes d'un modem DSL traditionnel.

## 3.7 Le répéteur et les autres équipements

Un répéteur régénère ou retransmet un signal selon la technologie concernée. En Wi-Fi, un répéteur peut étendre la couverture, mais il peut aussi réduire les performances selon son fonctionnement et la qualité du lien utilisé.

D'autres équipements existent :

- les convertisseurs cuivre-fibre ;
- les contrôleurs Wi-Fi ;
- les concentrateurs de VPN ;
- les passerelles industrielles ;
- les systèmes de supervision ;
- les alimentations redondantes.

Le choix dépend de la fonction nécessaire, et non simplement de l'apparence de l'appareil.

## 3.8 Tableau récapitulatif

| Équipement | Fonction principale | Exemple d'utilisation |
|---|---|---|
| Carte réseau | Connecter un appareil au réseau | Interface Ethernet d'un PC |
| Switch | Connecter plusieurs équipements localement | Réseau d'un bureau |
| Routeur | Transférer des paquets entre réseaux | Connexion d'un LAN à Internet |
| Point d'accès | Fournir un accès Wi-Fi | Couverture d'une salle |
| Pare-feu | Contrôler les flux selon une politique | Protection de la bordure |
| Modem ou terminal d'accès | Terminer une technologie d'accès opérateur | Accès fibre ou DSL |
| Convertisseur de média | Adapter une liaison à un autre support | Ethernet cuivre vers fibre |
| Répéteur Wi-Fi | Étendre la portée selon le système | Zone de couverture supplémentaire |

---

# 4. Switch, routeur et point d'accès : les différences

Ces équipements sont parfois confondus, notamment parce qu'une box Internet peut intégrer plusieurs de leurs fonctions.

| Question | Switch | Routeur | Point d'accès |
|---|---|---|---|
| Fonction principale | Connecter des appareils dans un domaine de commutation | Relier des réseaux IP | Connecter des clients Wi-Fi au réseau |
| Information principalement utilisée | Adresses MAC et configuration de couche 2 | Adresses IP et table de routage | Paramètres radio et pontage vers le réseau |
| Câblage typique | Ports Ethernet | Interfaces LAN, WAN et autres interfaces réseau | Ethernet vers l'infrastructure, radio vers les clients |
| Peut fournir le Wi-Fi ? | Pas nécessairement | Certains modèles le font | Oui |
| Peut router ? | Seulement si des fonctions de couche 3 sont disponibles | Oui | Pas nécessairement |

## 4.1 Schéma de base

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" role="img" aria-labelledby="hw-basic-title hw-basic-desc">
  <title id="hw-basic-title">Rôle des principaux équipements réseau</title>
  <desc id="hw-basic-desc">Deux ordinateurs sont reliés à un switch, un point d'accès fournit le Wi-Fi, et un routeur relie le réseau local à Internet. Les flèches animées utilisent des tirets directionnels. Aucun objet mobile n'est présent.</desc>
  <defs>
    <marker id="hw-basic-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/>
    </marker>
    <style>
      .hb-device{fill:#17263a;stroke:#60a5fa;stroke-width:2}
      .hb-network{fill:#123126;stroke:#4ade80;stroke-width:2}
      .hb-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .hb-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .hb-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#hw-basic-arrow);animation:hb-dash 1.8s linear infinite}
      @keyframes hb-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="368" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">EXEMPLE D'UNE PETITE INFRASTRUCTURE</text>
  <rect class="hb-device" x="25" y="80" width="165" height="65" rx="10"/>
  <text class="hb-title" x="107" y="107" text-anchor="middle">Ordinateur A</text>
  <text class="hb-text" x="107" y="128" text-anchor="middle">Ethernet</text>
  <rect class="hb-device" x="25" y="180" width="165" height="65" rx="10"/>
  <text class="hb-title" x="107" y="207" text-anchor="middle">Ordinateur B</text>
  <text class="hb-text" x="107" y="228" text-anchor="middle">Ethernet</text>
  <rect class="hb-device" x="250" y="125" width="175" height="75" rx="10"/>
  <text class="hb-title" x="337" y="155" text-anchor="middle">Switch</text>
  <text class="hb-text" x="337" y="178" text-anchor="middle">Ports locaux</text>
  <rect class="hb-device" x="490" y="215" width="175" height="65" rx="10"/>
  <text class="hb-title" x="577" y="242" text-anchor="middle">Point d'accès</text>
  <text class="hb-text" x="577" y="262" text-anchor="middle">Wi-Fi</text>
  <rect class="hb-device" x="490" y="105" width="175" height="65" rx="10"/>
  <text class="hb-title" x="577" y="132" text-anchor="middle">Routeur</text>
  <text class="hb-text" x="577" y="152" text-anchor="middle">Routage IP</text>
  <rect class="hb-network" x="750" y="105" width="180" height="65" rx="10"/>
  <text class="hb-title" x="840" y="132" text-anchor="middle">Internet</text>
  <text class="hb-text" x="840" y="152" text-anchor="middle">Réseaux distants</text>
  <path class="hb-flow" d="M190 112 L242 145"/>
  <path class="hb-flow" d="M190 212 L242 180"/>
  <path class="hb-flow" d="M425 150 L482 137"/>
  <path class="hb-flow" d="M425 180 L482 240"/>
  <path class="hb-flow" d="M665 137 H742"/>
  <text class="hb-text" x="480" y="320" text-anchor="middle">Les fonctions peuvent être réunies dans une box ou réparties entre plusieurs appareils.</text>
  <text class="hb-text" x="480" y="342" text-anchor="middle">Le dessin ne représente pas les règles de sécurité ni tous les liens de l'infrastructure.</text>
</svg>

---

# 5. Les supports de transmission

## 5.1 Câble Ethernet en cuivre

Le câble Ethernet en cuivre à paires torsadées est couramment utilisé pour relier des équipements dans un bâtiment.

Il transporte les données électriques sur des paires de conducteurs. Les performances dépendent notamment de la catégorie du câble, de la longueur, de la qualité de l'installation et des interfaces utilisées.

Les câbles courants sont souvent de catégorie Cat 5e, Cat 6 ou Cat 6A. Il faut choisir le câble en fonction du débit, de la distance et des exigences de l'installation.

Un câble de meilleure catégorie ne rend pas automatiquement tous les équipements plus rapides : les interfaces doivent également prendre en charge le débit visé.

## 5.2 Connecteur RJ45

Dans le langage courant, « RJ45 » désigne généralement le connecteur modulaire à huit positions utilisé pour Ethernet sur paires torsadées.

Il permet de raccorder un câble à un port réseau compatible.

Il faut distinguer le connecteur lui-même de la catégorie de câble, du brochage et des capacités de l'installation. Un connecteur physiquement adapté ne garantit pas un câblage correct.

## 5.3 Fibre optique

La fibre optique transmet les données à l'aide de signaux lumineux.

Elle est utilisée notamment pour :

- relier des bâtiments ;
- connecter des switches de distribution et de cœur ;
- transporter de grands débits ;
- établir des liaisons sur des distances supérieures à celles de nombreux liens cuivre d'accès.

Il existe différents types de fibre et de modules optiques. La compatibilité dépend de la longueur d'onde, du type de fibre, de la distance, des connecteurs et des caractéristiques des transceivers.

## 5.4 Fibre monomode et multimode

**La fibre monomode** est fréquemment utilisée pour les liaisons plus longues, les infrastructures opérateur et de nombreuses liaisons entre sites.

**La fibre multimode** est souvent utilisée pour certaines liaisons à courte ou moyenne portée, notamment dans les bâtiments et centres de données.

Ces usages sont des tendances, pas une règle absolue. Il faut toujours vérifier les caractéristiques des équipements et les distances spécifiées par le fabricant.

## 5.5 Transceiver optique

Un transceiver, parfois appelé module optique, fournit l'interface optique entre le port réseau et la fibre.

Des formats courants comprennent SFP, SFP+ et QSFP, avec différentes capacités selon les variantes.

Le format mécanique ne suffit pas à garantir la compatibilité. Il faut vérifier le débit, la longueur d'onde, le type de fibre, la distance, le codage accepté par l'équipement et les spécifications de chaque extrémité.

## 5.6 Wi-Fi

Le Wi-Fi transporte les données par radio.

Sa portée et ses performances dépendent de l'environnement, des obstacles, de la distance, des interférences, de la capacité du point d'accès et des clients.

Une liaison Wi-Fi ne dépend donc pas uniquement du débit inscrit sur la boîte : les performances réelles peuvent être inférieures aux valeurs théoriques.

## 5.7 Comparaison des supports

| Support | Avantage principal | Points de vigilance |
|---|---|---|
| Cuivre Ethernet | Simple pour la connexion des appareils proches | Distance, qualité du câble, catégorie et débit |
| Fibre optique | Longues distances et grande capacité selon le matériel | Compatibilité optique, propreté et manipulation |
| Wi-Fi | Mobilité et absence de câble jusqu'au terminal | Couverture, interférences, congestion et sécurité |
| Liaison opérateur | Connectivité entre sites ou vers Internet | Contrat, disponibilité et dépendance au fournisseur |

## 5.8 Schéma des supports

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-labelledby="media-title media-desc">
  <title id="media-title">Cuivre, fibre et Wi-Fi</title>
  <desc id="media-desc">Trois moyens de transmission sont représentés : un câble Ethernet en cuivre, une liaison fibre entre deux équipements optiques et une liaison radio entre un point d'accès et un ordinateur. Les lignes directionnelles sont animées par tirets, sans boules mobiles.</desc>
  <defs>
    <marker id="media-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .me-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .me-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .me-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .me-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#media-arrow);animation:me-dash 1.8s linear infinite}
      .me-radio{fill:none;stroke:#c4b5fd;stroke-width:3;stroke-dasharray:5 6;animation:me-dash 1.8s linear infinite}
      @keyframes me-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="348" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">TROIS MOYENS DE TRANSMISSION</text>
  <rect class="me-box" x="35" y="75" width="210" height="70" rx="10"/>
  <text class="me-title" x="140" y="103" text-anchor="middle">Poste utilisateur</text>
  <text class="me-text" x="140" y="126" text-anchor="middle">Port Ethernet</text>
  <rect class="me-box" x="310" y="75" width="210" height="70" rx="10"/>
  <text class="me-title" x="415" y="103" text-anchor="middle">Switch</text>
  <text class="me-text" x="415" y="126" text-anchor="middle">Lien cuivre</text>
  <path class="me-flow" d="M245 110 H302"/>
  <rect class="me-box" x="35" y="185" width="210" height="70" rx="10"/>
  <text class="me-title" x="140" y="213" text-anchor="middle">Module optique A</text>
  <text class="me-text" x="140" y="236" text-anchor="middle">Transceiver</text>
  <rect class="me-box" x="310" y="185" width="210" height="70" rx="10"/>
  <text class="me-title" x="415" y="213" text-anchor="middle">Module optique B</text>
  <text class="me-text" x="415" y="236" text-anchor="middle">Transceiver</text>
  <path class="me-flow" d="M245 220 H302"/>
  <text class="me-text" x="415" y="276" text-anchor="middle">Fibre optique</text>
  <rect class="me-box" x="640" y="75" width="280" height="70" rx="10"/>
  <text class="me-title" x="780" y="103" text-anchor="middle">Point d'accès Wi-Fi</text>
  <text class="me-text" x="780" y="126" text-anchor="middle">Radio vers les clients</text>
  <rect class="me-box" x="640" y="185" width="280" height="70" rx="10"/>
  <text class="me-title" x="780" y="213" text-anchor="middle">Ordinateur portable</text>
  <text class="me-text" x="780" y="236" text-anchor="middle">Interface sans fil</text>
  <path class="me-radio" d="M690 153 Q780 110 870 153"/>
  <path class="me-radio" d="M705 164 Q780 132 855 164"/>
  <text class="me-text" x="780" y="278" text-anchor="middle">Liaison radio</text>
  <text class="me-text" x="480" y="317" text-anchor="middle">Le débit dépend des interfaces, du support et de la qualité du lien.</text>
</svg>

---

# 6. Les ports, interfaces et voyants

## 6.1 Port réseau

Un port réseau est le point de connexion physique ou logique permettant de relier l'équipement à un autre appareil ou à un support.

Sur un switch, les ports peuvent porter des étiquettes comme :

- `1` à `24` ou `1` à `48` ;
- `Gi1/0/1` ;
- `Te1/1/1` ;
- `SFP` ou `SFP+` ;
- `Uplink`.

La signification exacte varie selon le constructeur et le modèle.

Un port `SFP` ou `SFP+` accepte un format de module donné, mais il ne faut pas en déduire que tous les modules ou tous les débits sont supportés.

## 6.2 Ports d'accès et uplinks

Les ports d'accès servent fréquemment à connecter les terminaux.

Les uplinks relient un switch à un autre équipement, par exemple un switch de distribution ou un routeur.

Cette distinction est logique et fonctionnelle. Un port physique donné n'est pas nécessairement limité à un seul rôle : sa configuration détermine les fonctions autorisées.

## 6.3 Voyants d'état

Les voyants peuvent indiquer :

- la présence d'une liaison ;
- l'activité du trafic ;
- la vitesse négociée ;
- l'état de l'alimentation PoE ;
- une alerte ou un état système.

La couleur et le clignotement ne sont pas universels. Consultez la documentation du modèle avant d'interpréter précisément un voyant.

## 6.4 Comment lire un port sans inventer sa signification

Lorsqu'un voyant est éteint, cela peut signifier que le lien n'est pas établi, que l'interface est désactivée ou que l'indication est utilisée différemment par le constructeur.

Lorsqu'il clignote, cela peut refléter l'activité, la négociation ou un autre état.

Ne remplacez pas immédiatement le switch sur la base d'un voyant isolé. Vérifiez également le câble, l'interface distante, la configuration et l'alimentation du terminal.

---

# 7. Alimentation et PoE

## 7.1 Qu'est-ce que le PoE ?

Le PoE (*Power over Ethernet*) permet de transmettre des données et de l'alimentation électrique sur un câblage Ethernet compatible.

Il est utilisé notamment pour alimenter :

- les téléphones IP ;
- les points d'accès Wi-Fi ;
- certaines caméras IP ;
- certains équipements IoT ;
- certains terminaux de contrôle d'accès.

Un switch PoE peut jouer le rôle de PSE (*Power Sourcing Equipment*), c'est-à-dire la source d'alimentation. L'appareil alimenté est le PD (*Powered Device*).

## 7.2 Les classes de PoE

Plusieurs variantes normalisées du PoE existent, offrant des niveaux de puissance différents.

Le nom commercial d'un switch ne suffit pas à déterminer la puissance réellement disponible sur chaque port.

Il faut distinguer :

- la puissance maximale possible par port ;
- le budget PoE total de l'équipement ;
- les besoins électriques des terminaux ;
- le nombre de ports alimentés simultanément ;
- les limites liées aux alimentations et au refroidissement.

Un switch peut être compatible PoE tout en étant incapable d'alimenter tous les terminaux à leur puissance maximale si le budget total est dépassé.

## 7.3 Exemple

Un point d'accès peut nécessiter un mode PoE particulier. Si le port du switch ou son alimentation ne fournit pas le niveau requis, l'appareil peut ne pas démarrer ou ne pas activer toutes ses fonctions.

Avant l'installation :

1. vérifier la norme PoE requise par le terminal ;
2. vérifier la compatibilité du port ;
3. calculer le budget d'alimentation total ;
4. prendre en compte les alimentations redondantes, s'il y en a ;
5. consulter la documentation de l'équipement.

## 7.4 Schéma PoE

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="340" viewBox="0 0 960 340" role="img" aria-labelledby="poe-title poe-desc">
  <title id="poe-title">Principe du Power over Ethernet</title>
  <desc id="poe-desc">Un switch compatible PoE fournit les données et l'alimentation via le câble Ethernet à un point d'accès compatible. Le câble doit être adapté et le budget d'alimentation du switch doit être suffisant.</desc>
  <defs>
    <marker id="poe-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .pe-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .pe-power{fill:#123126;stroke:#4ade80;stroke-width:2}
      .pe-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .pe-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .pe-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#poe-arrow);animation:pe-dash 1.8s linear infinite}
      @keyframes pe-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="338" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DONNÉES + ALIMENTATION SUR UN CÂBLE COMPATIBLE</text>
  <rect class="pe-box" x="45" y="90" width="275" height="100" rx="12"/>
  <text class="pe-title" x="182" y="122" text-anchor="middle">Switch PoE</text>
  <text class="pe-text" x="182" y="147" text-anchor="middle">PSE : source d'alimentation</text>
  <text class="pe-text" x="182" y="168" text-anchor="middle">Budget total à vérifier</text>
  <rect class="pe-power" x="640" y="90" width="275" height="100" rx="12"/>
  <text class="pe-title" x="777" y="122" text-anchor="middle">Point d'accès</text>
  <text class="pe-text" x="777" y="147" text-anchor="middle">PD : terminal alimenté</text>
  <text class="pe-text" x="777" y="168" text-anchor="middle">Norme et puissance compatibles</text>
  <path class="pe-flow" d="M320 140 H632"/>
  <text class="pe-text" x="480" y="122" text-anchor="middle">Ethernet</text>
  <text class="pe-text" x="480" y="169" text-anchor="middle">Données et énergie</text>
  <rect class="pe-box" x="190" y="235" width="580" height="55" rx="10"/>
  <text class="pe-title" x="480" y="258" text-anchor="middle">Avant branchement</text>
  <text class="pe-text" x="480" y="278" text-anchor="middle">Vérifier compatibilité, puissance par port et budget total.</text>
</svg>

---

# 8. Les composants d'un équipement professionnel

## 8.1 Châssis

Le châssis constitue la structure physique qui accueille les cartes, les ports, les alimentations et les systèmes de refroidissement.

Les switches et routeurs peuvent être des appareils fixes ou des systèmes modulaires, selon leur gamme et leur rôle.

## 8.2 Alimentations

L'alimentation convertit l'énergie électrique en tensions adaptées à l'équipement.

Certains appareils disposent d'une seule alimentation. D'autres acceptent plusieurs alimentations pour améliorer la disponibilité.

Deux alimentations ne garantissent pas la redondance si elles partagent la même source électrique ou si elles ne sont pas correctement dimensionnées.

## 8.3 Ventilateurs et refroidissement

Les composants électroniques produisent de la chaleur. Le système de refroidissement maintient la température dans les limites prévues.

Il peut s'appuyer sur des ventilateurs, des dissipateurs et un chemin d'air défini par le constructeur.

Un équipement peut se mettre en défaut ou réduire ses performances si la ventilation est insuffisante ou si les entrées d'air sont obstruées.

## 8.4 Cartes et modules

Les appareils modulaires peuvent accueillir des cartes de ports, des cartes de contrôle ou des modules supplémentaires.

La compatibilité mécanique ne garantit pas la compatibilité logicielle ou fonctionnelle. Avant toute installation, vérifiez les modules autorisés pour la plateforme et la version logicielle.

## 8.5 Ports de console et ports de gestion

Certains équipements possèdent un port de console destiné à l'administration locale ou à la récupération.

D'autres possèdent une interface de gestion Ethernet dédiée.

Ces interfaces ne sont pas nécessairement destinées au trafic utilisateur. Il faut respecter les instructions du constructeur et les règles de sécurité de l'infrastructure.

---

# 9. Exemple d'installation réseau

## 9.1 Scénario

Un petit bureau dispose de :

- six ordinateurs ;
- deux imprimantes réseau ;
- un point d'accès Wi-Fi ;
- un routeur ;
- un switch.

Le but est de raccorder les équipements en conservant une organisation simple.

## 9.2 Avant l'installation

Vérifiez :

- le nombre de ports nécessaires ;
- le débit requis ;
- la compatibilité des câbles ;
- la présence éventuelle de terminaux PoE ;
- les besoins de couverture Wi-Fi ;
- l'emplacement des équipements ;
- les prises électriques et la ventilation ;
- les paramètres de sécurité de la box ou du routeur.

Le matériel doit être choisi selon les besoins réels et les possibilités d'évolution, pas seulement selon le nombre de ports au moment de l'achat.

## 9.3 Branchement conceptuel

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" role="img" aria-labelledby="install-title install-desc">
  <title id="install-title">Installation physique d'un petit réseau de bureau</title>
  <desc id="install-desc">Le routeur relie le réseau au service d'accès. Un switch relie les ordinateurs et imprimantes. Un point d'accès relie les clients sans fil. Les traits animés montrent les liaisons logiques et ne représentent pas une particule mobile.</desc>
  <defs>
    <marker id="ins-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .in-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .in-ok{fill:#123126;stroke:#4ade80;stroke-width:2}
      .in-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .in-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .in-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#ins-arrow);animation:in-dash 1.8s linear infinite}
      @keyframes in-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="368" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">EXEMPLE DE CÂBLAGE D'UN BUREAU</text>
  <rect class="in-box" x="25" y="80" width="165" height="70" rx="10"/>
  <text class="in-title" x="107" y="109" text-anchor="middle">Accès Internet</text>
  <text class="in-text" x="107" y="131" text-anchor="middle">Fibre / opérateur</text>
  <rect class="in-box" x="255" y="80" width="165" height="70" rx="10"/>
  <text class="in-title" x="337" y="109" text-anchor="middle">Routeur</text>
  <text class="in-text" x="337" y="131" text-anchor="middle">Passerelle locale</text>
  <rect class="in-box" x="495" y="80" width="165" height="70" rx="10"/>
  <text class="in-title" x="577" y="109" text-anchor="middle">Switch</text>
  <text class="in-text" x="577" y="131" text-anchor="middle">Ports utilisateurs</text>
  <rect class="in-ok" x="735" y="60" width="190" height="60" rx="10"/>
  <text class="in-title" x="830" y="85" text-anchor="middle">Ordinateurs</text>
  <text class="in-text" x="830" y="105" text-anchor="middle">Ethernet</text>
  <rect class="in-ok" x="735" y="140" width="190" height="60" rx="10"/>
  <text class="in-title" x="830" y="165" text-anchor="middle">Imprimantes</text>
  <text class="in-text" x="830" y="185" text-anchor="middle">Ethernet</text>
  <rect class="in-box" x="495" y="235" width="165" height="60" rx="10"/>
  <text class="in-title" x="577" y="260" text-anchor="middle">Point d'accès</text>
  <text class="in-text" x="577" y="281" text-anchor="middle">Wi-Fi</text>
  <rect class="in-ok" x="735" y="235" width="190" height="60" rx="10"/>
  <text class="in-title" x="830" y="260" text-anchor="middle">Terminaux sans fil</text>
  <text class="in-text" x="830" y="281" text-anchor="middle">Wi-Fi</text>
  <path class="in-flow" d="M190 115 H247"/>
  <path class="in-flow" d="M420 115 H487"/>
  <path class="in-flow" d="M660 90 H727"/>
  <path class="in-flow" d="M660 120 L727 170"/>
  <path class="in-flow" d="M577 150 V227"/>
  <path class="in-flow" d="M660 265 H727"/>
  <text class="in-text" x="480" y="331" text-anchor="middle">Les fonctions et connexions exactes dépendent du matériel disponible.</text>
  <text class="in-text" x="480" y="349" text-anchor="middle">Les règles IP, DHCP, Wi-Fi et de sécurité restent à configurer et vérifier.</text>
</svg>

## 9.4 Après le branchement

Vérifiez :

1. que les câbles sont correctement insérés ;
2. que les liens sont établis sur les ports concernés ;
3. que les terminaux disposent d'une adresse IP appropriée ;
4. que la passerelle attendue est configurée ;
5. que les appareils peuvent joindre les services autorisés ;
6. que le Wi-Fi utilise le nom de réseau et les paramètres de sécurité prévus ;
7. que les voyants et journaux ne signalent pas d'erreur matérielle.

Une lumière verte ne prouve pas que tout fonctionne. Elle indique seulement un état défini par le fabricant.

---

# 10. Installation et précautions

## 10.1 Emplacement

Placez le matériel dans un environnement adapté à sa température, à l'humidité et à la ventilation spécifiées par le fabricant.

Évitez de bloquer les entrées et sorties d'air. Respectez les distances et orientations prévues pour le refroidissement.

## 10.2 Électricité

Utilisez les alimentations compatibles avec l'équipement et les conditions électriques prévues.

Les interventions sur les alimentations internes, les circuits électriques et les équipements haute puissance doivent être réservées à des personnes qualifiées lorsque cela est nécessaire.

Ne démontez pas un appareil alimenté et ne manipulez pas des connecteurs optiques ou électriques sans respecter les consignes de sécurité applicables.

## 10.3 Fibre optique

La fibre et les connecteurs optiques exigent des précautions particulières :

- ne regardez jamais directement dans un port optique ou une fibre ;
- nettoyez et manipulez les connecteurs conformément aux procédures adaptées ;
- respectez le rayon de courbure indiqué pour la fibre ;
- évitez de toucher les surfaces optiques ;
- identifiez la fibre et les deux extrémités avant de la déconnecter.

Un connecteur sale ou endommagé peut provoquer des pertes optiques même lorsque le câble semble intact.

## 10.4 Documentation de l'installation

Documentez au minimum :

- l'emplacement de l'équipement ;
- le modèle et le numéro d'inventaire ;
- les ports utilisés ;
- les câbles et leurs destinations ;
- les alimentations ;
- les modules installés ;
- la configuration de référence ;
- les informations nécessaires à une intervention ultérieure.

Ne publiez pas les numéros de série, adresses de gestion ou autres détails sensibles dans des documents accessibles sans contrôle.

---

# 11. Premiers diagnostics

## 11.1 Un équipement ne s'allume pas

Vérifiez l'alimentation, le câble secteur ou l'adaptateur, l'interrupteur éventuel et les conditions indiquées dans la documentation.

Si l'équipement présente un signe de dommage électrique, arrêtez les vérifications et appliquez la procédure de sécurité adaptée.

## 11.2 Le lien Ethernet ne s'établit pas

Vérifiez les deux extrémités :

- câble adapté et en bon état ;
- port activé ;
- interface distante fonctionnelle ;
- modules compatibles si la liaison est optique ;
- vitesse et paramètres compatibles.

Changez un seul élément à la fois lorsque cela est possible. Cela aide à identifier la cause sans introduire plusieurs variables.

## 11.3 Le terminal est connecté mais n'accède à aucun service

Le lien physique peut fonctionner alors que le problème se situe dans l'adressage, le routage, DNS ou une politique de sécurité.

Vérifiez les paramètres réseau du poste et les résultats des tests adaptés avant de remplacer l'équipement.

## 11.4 Le point d'accès redémarre ou ne fournit pas toutes ses fonctions

Vérifiez la compatibilité PoE, le budget d'alimentation, le câble, les limitations du port et la documentation du point d'accès.

Un redémarrage répété peut provenir d'un problème d'alimentation ou de logiciel ; il ne faut pas supposer que le matériel est forcément défectueux.

## 11.5 Méthode rapide

```text
1. Définir le symptôme.
2. Vérifier l'alimentation.
3. Vérifier les câbles et les ports.
4. Lire les voyants selon la documentation du modèle.
5. Vérifier l'adressage et la configuration.
6. Tester la connectivité.
7. Examiner les journaux et messages d'erreur.
8. Remplacer un composant seulement si les éléments recueillis le justifient.
```

---

# 12. Atelier pratique

## Scénario

Vous devez préparer le matériel d'un petit laboratoire comprenant quatre ordinateurs, un switch, un routeur et un point d'accès Wi-Fi.

### Étape A — Faire l'inventaire

Notez le modèle, le nombre de ports, les débits supportés, les interfaces disponibles et les besoins d'alimentation.

### Étape B — Planifier les connexions

Identifiez le port reliant le switch au routeur, les ports des postes et celui du point d'accès.

### Étape C — Vérifier les supports

Confirmez que les câbles sont adaptés aux interfaces. Si vous utilisez la fibre, vérifiez les modules, les connecteurs et le type de fibre.

### Étape D — Contrôler le PoE

Si le point d'accès est alimenté par Ethernet, vérifiez la compatibilité et le budget de puissance.

### Étape E — Établir les connexions

Effectuez le câblage conformément au schéma et aux instructions du matériel. Ne modifiez pas le réseau de production pour réaliser cet exercice.

### Étape F — Vérifier le fonctionnement

Vérifiez l'alimentation, les liens, les adresses IP, la passerelle et les accès autorisés.

### Étape G — Documenter le résultat

Enregistrez les connexions, les éventuels problèmes et les vérifications effectuées.

Le laboratoire est réussi lorsque le matériel est identifié, raccordé de manière cohérente et vérifié sans remplacer des composants au hasard.

---

# 13. Évaluation corrigée

## Questions

1. Quel est le rôle d'un switch ?
2. Quelle différence existe entre un switch et un routeur ?
3. À quoi sert un point d'accès Wi-Fi ?
4. Quel est l'avantage principal de la fibre optique ?
5. Que faut-il vérifier avant de choisir un module optique ?
6. Qu'est-ce que le PoE ?
7. Pourquoi le budget PoE total est-il important ?
8. Que peut indiquer un voyant de port ?
9. Pourquoi une liaison Ethernet établie ne garantit-elle pas l'accès à Internet ?
10. Pourquoi faut-il documenter les ports et les câbles ?
11. Pourquoi ne faut-il pas regarder directement dans un port optique ?
12. Pourquoi doit-on vérifier la documentation avant d'interpréter un voyant ?

## Corrigé

**1. Switch**

Il connecte des équipements et transmet les trames selon la table de commutation et sa configuration.

**2. Switch et routeur**

Un switch de couche 2 commute les trames localement. Un routeur transfère des paquets IP entre des réseaux.

**3. Point d'accès**

Il fournit un accès réseau sans fil aux appareils Wi-Fi.

**4. Fibre optique**

Elle permet, selon le matériel, des débits élevés et des liaisons sur de longues distances, tout en étant peu sensible aux interférences électromagnétiques ordinaires.

**5. Module optique**

Vérifier le débit, la longueur d'onde, le type de fibre, la distance, les connecteurs et la compatibilité du matériel.

**6. PoE**

Il transporte l'alimentation électrique et les données sur une liaison Ethernet compatible.

**7. Budget PoE**

Il détermine la puissance totale disponible pour les terminaux alimentés.

**8. Voyant de port**

Il peut indiquer le lien, l'activité, la vitesse ou un état particulier selon le modèle.

**9. Lien et accès à Internet**

Le lien physique peut fonctionner alors que l'adressage IP, le routage, DNS ou les règles de sécurité sont incorrects.

**10. Documentation**

Elle facilite le diagnostic, les changements, la maintenance et l'identification des deux extrémités d'une liaison.

**11. Sécurité optique**

Un équipement optique peut émettre un signal invisible potentiellement dangereux pour les yeux. Il faut suivre les consignes de sécurité applicables.

**12. Voyants**

Leurs couleurs et comportements varient selon les fabricants et les modèles.

---

# 14. Préparation du niveau intermédiaire

Le niveau intermédiaire approfondira :

- les familles et caractéristiques des switches ;
- les ports Ethernet et les modules optiques ;
- les VLAN et les trunks ;
- les liaisons montantes ;
- le PoE et ses budgets ;
- les capacités de routage des équipements ;
- les alimentations et la ventilation ;
- les outils de mesure physique ;
- les erreurs de câblage ;
- la méthode de diagnostic matériel.

Le niveau débutant vous apprend à reconnaître le matériel. Le niveau intermédiaire vous apprendra à dimensionner et diagnostiquer une installation de manière méthodique.

---

## Références utiles

- IEEE 802.3 — Ethernet : https://standards.ieee.org/ieee/7003/10422/
- IEEE 802.1Q — Bridges et VLAN : https://standards.ieee.org/ieee/8802-1Q_2024_Amd.35_2024/11823/802.1Q/10323/
- Documentation PoE Cisco : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/infra/poe/poe-configuration-guide/g-poe/c-poe.html
- Guide matériel des routeurs Juniper : https://www.juniper.net/documentation/us/en/software/junos/junos-overview/topics/concept/junos-software-routing-platforms-hardware-components.html
- Guides matériels Juniper : https://www.juniper.net/documentation/

**Fichier :** `materiel-reseau-debutant.md`  
**Niveau :** Débutant  
**Fin du cours**
