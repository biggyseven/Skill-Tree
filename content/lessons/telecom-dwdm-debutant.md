
# Fibre optique & DWDM — Niveau débutant

**Nom du fichier :** `telecom-dwdm-debutant.md`  
**Module :** Opérateurs & Télécoms  
**Niveau :** Débutant  
**Domaine :** Transmission optique, réseaux de transport et infrastructures télécoms  
**Public cible :** Débutants en télécommunications, techniciens réseau, techniciens fibre optique, étudiants en réseaux et futurs techniciens transmission.

## 1. Présentation générale du cours

### 1.1. Objectif du cours

Les opérateurs télécoms doivent transporter des quantités considérables de données entre des villes, des centres de données, des stations mobiles, des points de présence Internet et des réseaux d’accès.

La fibre optique constitue l’un des principaux supports physiques de ce transport. Elle permet de transmettre des informations sous forme de lumière sur des distances importantes, avec une capacité élevée et une bonne immunité aux perturbations électromagnétiques.

Lorsque la capacité d’une fibre ne suffit plus, les opérateurs peuvent utiliser le DWDM (*Dense Wavelength Division Multiplexing*) pour transporter plusieurs canaux optiques indépendants sur une même fibre.

Ce cours explique progressivement :

- ce qu’est une fibre optique et comment elle fonctionne ;
- les différences entre fibre monomode et multimode ;
- les notions de longueur d’onde, d’atténuation et de puissance optique ;
- les connecteurs, les épissures et les équipements de mesure ;
- le multiplexage WDM et DWDM ;
- les équipements utilisés dans un réseau de transport optique ;
- les calculs élémentaires de budget optique ;
- les méthodes de vérification et de dépannage ;
- les précautions de sécurité à appliquer sur le terrain.

### 1.2. Compétences visées

À la fin du cours, l’apprenant doit pouvoir :

1. Expliquer le fonctionnement physique d’une liaison optique.
2. Identifier les principales catégories de fibres et leurs applications.
3. Distinguer une longueur d’onde, une fréquence, un débit et une puissance optique.
4. Comprendre les valeurs exprimées en dBm, dB, nm et GHz.
5. Calculer les pertes estimées d’une liaison optique.
6. Vérifier si un récepteur reçoit une puissance compatible avec ses caractéristiques.
7. Expliquer le rôle d’un émetteur optique, d’un récepteur, d’un multiplexeur, d’un démultiplexeur et d’un amplificateur.
8. Décrire le fonctionnement général d’une architecture DWDM.
9. Comprendre les résultats élémentaires d’un photomètre optique et d’un OTDR.
10. Diagnostiquer des défauts courants de transmission optique.
11. Appliquer une procédure professionnelle de nettoyage, de mesure et de validation.
12. Comprendre comment la fibre et le DWDM participent à l’infrastructure d’un opérateur.

### 1.3. Prérequis

Aucune connaissance approfondie en optique n’est nécessaire.

Il est toutefois utile de connaître les notions suivantes :

- un réseau informatique ;
- une liaison entre deux équipements ;
- un émetteur et un récepteur ;
- un câble et un connecteur ;
- un débit exprimé en bit/s ;
- la différence entre un équipement actif et un élément passif.

## 2. Vue d’ensemble d’un réseau de transport optique

Un opérateur doit interconnecter ses équipements de collecte, ses routeurs, ses centres de données et ses stations de télécommunication.

Une architecture simplifiée peut être représentée ainsi :

```text
                  RÉSEAU DE TRANSPORT D'UN OPÉRATEUR

  Site A                                                       Site B
  +------------------+                              +------------------+
  | Routeur IP       |                              | Routeur IP       |
  | Switch Ethernet  |                              | Switch Ethernet  |
  +--------+---------+                              +---------+--------+
           |                                                  |
  +--------v---------+                              +---------v--------+
  | Équipement       |                              | Équipement       |
  | de transmission  |                              | de transmission  |
  +--------+---------+                              +---------+--------+
           |                                                  |
           | Signal optique                                  |
           +================ FIBRE OPTIQUE ===================+
                              |
                       Réseau de transport
                              |
                   DWDM si plusieurs canaux
                   doivent partager la fibre
```

Dans un réseau réel, plusieurs équipements intermédiaires peuvent être présents : amplificateurs optiques, nœuds de brassage, systèmes de supervision, équipements de protection et systèmes de multiplexage.

La fibre transporte le signal lumineux. Les équipements électroniques ou optiques qui l’entourent déterminent notamment le débit, le format du signal, la longueur d’onde et les fonctions de protection.

Il faut distinguer trois éléments :

- **Le support :** la fibre optique elle-même.
- **Le signal :** la lumière modulée qui transporte l’information.
- **Le service :** par exemple une liaison Ethernet, un circuit de transport ou un canal reliant deux équipements.

## 3. Les bases physiques de la fibre optique

### 3.1. Qu’est-ce que la lumière utilisée dans une fibre ?

La lumière est un rayonnement électromagnétique. Dans les télécommunications optiques, on utilise principalement des longueurs d’onde situées dans le proche infrarouge.

La lumière est générée par un composant émetteur, généralement un laser dans les systèmes de transmission à haut débit, puis injectée dans la fibre.

L’information peut être transportée en modifiant certaines caractéristiques du signal optique. Selon la technologie, ces caractéristiques peuvent inclure l’intensité, la phase ou la polarisation de la lumière.

À l’extrémité opposée, un photodétecteur transforme le signal optique reçu en signal électrique, lequel sera ensuite traité par le récepteur.

### 3.2. Structure d’une fibre optique

Une fibre optique comprend plusieurs couches.

```text
          STRUCTURE SIMPLIFIÉE D'UNE FIBRE OPTIQUE

       +---------------------------------------+
       | Revêtement protecteur                 |
       |                                       |
       |   +--------------------------------+  |
       |   | Gaine optique (cladding)       |  |
       |   |                                |  |
       |   |     +--------------------+     |  |
       |   |     | Cœur optique       |     |  |
       |   |     | (core)             |     |  |
       |   |     |                    |     |  |
       |   |     +--------------------+     |  |
       |   |                                |  |
       |   +--------------------------------+  |
       +---------------------------------------+

       Cœur       : transporte le champ optique
       Gaine       : confine la lumière dans la fibre
       Revêtement  : protège mécaniquement la fibre
```

Le cœur et la gaine sont constitués de matériaux transparents, généralement à base de silice.

La différence entre leurs indices de réfraction permet de guider la lumière. Dans une fibre classique à saut d’indice, le cœur possède un indice de réfraction supérieur à celui de la gaine.

Le revêtement protecteur ne doit pas être confondu avec la gaine optique. Il protège la fibre contre les agressions mécaniques et environnementales.

### 3.3. Comment la lumière reste-t-elle dans la fibre ?

Le principe historique d’explication est la réflexion totale interne.

Lorsque la lumière se propage dans le cœur et rencontre l’interface cœur-gaine sous des conditions appropriées, elle reste guidée dans le cœur.

Dans une description plus complète, la propagation est expliquée par les modes optiques et les équations électromagnétiques. La réflexion totale interne constitue une bonne première représentation pour comprendre le principe.

```text
          GUIDAGE SIMPLIFIÉ DE LA LUMIÈRE

  Entrée                                                Sortie
    |                                                      |
    v                                                      v
  +--------------------------------------------------------+
  | \        / \        / \        / \        / \          |
  |  \      /   \      /   \      /   \      /   \         |
  |   \    /     \    /     \    /     \    /     \        |
  |    \__/       \__/       \__/       \__/                |
  +--------------------------------------------------------+
                     Cœur de la fibre
```

Ce dessin illustre le principe de guidage. Il ne représente pas exactement le trajet physique de tous les modes dans une fibre réelle.

### 3.4. Pourquoi utilise-t-on de la lumière plutôt que de l’électricité ?

La fibre optique présente plusieurs avantages :

- capacité de transmission élevée ;
- faibles pertes sur les longueurs d’onde adaptées ;
- immunité aux perturbations électromagnétiques ;
- isolation électrique entre les extrémités ;
- faible poids par rapport à certains câbles métalliques ;
- possibilité de transporter des signaux sur de longues distances avec des équipements adaptés.

Elle présente également des contraintes :

- fragilité du verre si la fibre est mal manipulée ;
- nécessité de connecteurs et d’épissures de qualité ;
- besoin d’outils de mesure spécifiques ;
- sensibilité aux courbures excessives ;
- nécessité de respecter les limites de puissance et les règles de sécurité laser.

## 4. Les principales catégories de fibres

### 4.1. Fibre monomode

La fibre monomode est la fibre de référence pour la majorité des réseaux de transport d’opérateurs sur longues distances.

Son cœur est très petit, généralement de l’ordre de 8 à 10 micromètres selon le type de fibre et la longueur d’onde considérée.

Elle est conçue pour guider un mode spatial fondamental dans ses conditions normales d’utilisation. Elle limite ainsi la dispersion modale présente dans les fibres multimodes.

Applications courantes :

- réseaux métropolitains ;
- réseaux longue distance ;
- liaisons interurbaines ;
- interconnexion de centres de données ;
- réseaux d’accès FTTH ;
- systèmes DWDM.

### 4.2. Fibre multimode

La fibre multimode possède un cœur beaucoup plus large, couramment de 50 ou 62,5 micromètres.

Plusieurs modes spatiaux peuvent s’y propager. Les différences de temps de propagation entre modes peuvent limiter la distance et le débit, selon le type de fibre et l’équipement utilisé.

Applications courantes :

- réseaux locaux d’entreprise ;
- salles informatiques ;
- certaines interconnexions de centres de données ;
- liaisons courtes utilisant des transceivers compatibles multimodes.

### 4.3. Comparaison

| Critère | Fibre monomode | Fibre multimode |
|---|---|---|
| Cœur typique | Environ 8 à 10 µm | 50 ou 62,5 µm |
| Modes spatiaux | Un mode fondamental en fonctionnement normal | Plusieurs modes |
| Applications courantes | Transport opérateur, longues distances | Liaisons locales et courtes |
| Dispersion modale | Très faible | Peut être importante |
| Équipements optiques | Compatibles monomode | Compatibles multimodes |
| Usage DWDM longue distance | Très courant | Généralement inadapté aux systèmes longue distance classiques |

**Règle importante :** il ne suffit pas qu’un connecteur entre physiquement dans un port pour que la liaison fonctionne. La fibre, le type de transceiver, la longueur d’onde et le budget optique doivent être compatibles.

### 4.4. Familles de fibres monomodes

Quelques recommandations et familles importantes :

- **ITU-T G.652 :** famille très répandue de fibres monomodes conventionnelles.
- **ITU-T G.655 :** fibres à dispersion décalée non nulle, utilisées notamment dans certaines infrastructures de transport optique.
- **ITU-T G.657 :** fibres monomodes présentant une meilleure tolérance à certaines courbures, notamment pour les réseaux d’accès et les installations contraintes.

Les propriétés exactes dépendent de la catégorie et de la spécification de la fibre.

Il ne faut pas supposer que toutes les fibres monomodes ont exactement les mêmes caractéristiques d’atténuation, de dispersion ou de tolérance aux courbures.

### 4.5. Les catégories OM

Les fibres multimodes sont notamment classées en catégories OM1, OM2, OM3, OM4 et OM5.

Ces catégories ne sont pas des versions de fibre monomode. Elles correspondent à des caractéristiques de transmission multimode spécifiques.

Dans les réseaux d’entreprise et les centres de données, le choix dépend notamment :

- du débit souhaité ;
- de la distance ;
- de la longueur d’onde ;
- du type de transceiver ;
- des caractéristiques de la fibre installée.

## 5. Longueurs d’onde et fréquences optiques

### 5.1. Définition d’une longueur d’onde

La longueur d’onde, notée λ, représente la distance entre deux points successifs de même phase d’une onde.

Elle s’exprime souvent en nanomètres, notés nm.

Dans les réseaux optiques, on rencontre notamment des longueurs d’onde proches de :

- 850 nm ;
- 1310 nm ;
- 1490 nm ;
- 1550 nm ;
- 1577 nm.

Leur utilisation dépend de l’application. Ces valeurs ne sont pas interchangeables.

Exemples :

- 850 nm est courant sur certaines liaisons multimodes.
- 1310 nm est couramment utilisé dans des systèmes monomodes.
- Autour de 1550 nm se trouvent des bandes particulièrement importantes pour les systèmes de transport optique longue distance et DWDM.

### 5.2. Relation entre longueur d’onde et fréquence

La fréquence et la longueur d’onde sont liées par la relation :

\[
c = \lambda f
\]

Donc :

\[
f = \frac{c}{\lambda}
\]

Avec :

- \(c\) : vitesse de la lumière dans le vide, environ \(3 \times 10^8\) m/s ;
- \(\lambda\) : longueur d’onde en mètres ;
- \(f\) : fréquence en hertz.

Lorsque la longueur d’onde augmente, la fréquence diminue.

Par exemple, une longueur d’onde de 1550 nm correspond à une fréquence optique d’environ 193,4 THz.

La fréquence optique n’est pas le débit de données. Un signal optique à une fréquence porteuse donnée peut transporter des données à des débits très différents selon la modulation et l’équipement.

### 5.3. Les bandes optiques

Les bandes couramment citées dans les télécommunications optiques sont :

| Bande | Désignation | Utilisation générale |
|---|---|---|
| O | Original | Certaines transmissions autour de 1310 nm |
| E | Extended | Bande étendue historiquement associée aux systèmes optiques |
| S | Short wavelength | Bande de longueurs d’onde plus courtes que la bande C |
| C | Conventional | Bande très utilisée pour le DWDM et les amplificateurs EDFA |
| L | Long wavelength | Bande de longueurs d’onde plus longues que la bande C |

Les limites exactes de ces bandes dépendent des conventions techniques utilisées.

La bande C est particulièrement importante parce que les amplificateurs optiques EDFA sont largement utilisés dans cette zone spectrale.

### 5.4. Pourquoi choisir une longueur d’onde particulière ?

Le choix dépend de plusieurs facteurs :

- l’atténuation de la fibre à cette longueur d’onde ;
- la dispersion chromatique ;
- les caractéristiques des lasers et récepteurs ;
- la disponibilité des amplificateurs optiques ;
- la grille de fréquences du système DWDM ;
- la compatibilité des équipements aux deux extrémités.

Une liaison optique ne doit donc pas être dimensionnée uniquement à partir de la distance.

## 6. Atténuation et pertes optiques

### 6.1. Définition de l’atténuation

Lorsqu’un signal lumineux traverse une fibre, sa puissance diminue progressivement.

Cette diminution est appelée atténuation.

Elle peut être provoquée par :

- l’absorption dans le matériau ;
- la diffusion ;
- les courbures ;
- les imperfections de fabrication ;
- les connecteurs ;
- les épissures ;
- les défauts d’installation.

L’atténuation linéique est souvent exprimée en dB/km.

Une valeur de 0,22 dB/km signifie que la perte est d’environ 0,22 dB par kilomètre, dans les conditions et à la longueur d’onde considérées.

Cette valeur est un exemple de calcul, pas une garantie applicable à toutes les fibres.

### 6.2. Calcul des pertes de la fibre

La formule simplifiée est :

\[
L_{\text{fibre}} = \alpha \times D
\]

Avec :

- \(L_{\text{fibre}}\) : perte de la fibre en dB ;
- \(\alpha\) : atténuation en dB/km ;
- \(D\) : distance en kilomètres.

**Exemple :**

Une fibre de 40 km présente une atténuation estimée de 0,22 dB/km.

\[
L_{\text{fibre}} = 0,22 \times 40
\]

\[
L_{\text{fibre}} = 8,8\ \text{dB}
\]

La fibre seule introduit donc environ 8,8 dB de pertes.

Il faut ensuite ajouter les pertes des connecteurs, des épissures et des autres éléments passifs.

### 6.3. Pertes des connecteurs et des épissures

Les connecteurs permettent de relier des équipements ou des tronçons de fibre de manière démontable.

Les épissures permettent de joindre durablement deux fibres, généralement par fusion.

Chaque connexion et chaque épissure peut introduire une perte.

Exemple de budget prévisionnel :

| Élément | Quantité | Perte unitaire | Perte totale |
|---|---:|---:|---:|
| Fibre de 40 km | 40 km | 0,22 dB/km | 8,8 dB |
| Connecteurs | 4 | 0,25 dB | 1,0 dB |
| Épissures | 12 | 0,10 dB | 1,2 dB |
| Total estimé | | | 11,0 dB |

Les pertes unitaires sont des hypothèses pédagogiques. Pour un projet réel, les valeurs doivent provenir des spécifications du matériel, des mesures et des critères d’acceptation du projet.

### 6.4. Comprendre le décibel

Le décibel, noté dB, exprime un rapport logarithmique entre deux puissances.

Pour deux puissances optiques \(P_1\) et \(P_2\) :

\[
G_{\text{dB}} = 10\log_{10}\left(\frac{P_2}{P_1}\right)
\]

Pour une perte positive :

\[
L_{\text{dB}} = 10\log_{10}\left(\frac{P_{\text{entrée}}}{P_{\text{sortie}}}\right)
\]

Le décibel ne représente pas directement une puissance absolue. Il indique un rapport.

Une perte de 3 dB correspond approximativement à une division par deux de la puissance optique.

Une perte de 10 dB correspond à une division par dix.

Une perte de 20 dB correspond à une division par cent.

### 6.5. Différence entre dB et dBm

Cette distinction est fondamentale.

**dB :** mesure un rapport, un gain ou une perte.

**dBm :** exprime une puissance absolue par rapport à 1 milliwatt.

La relation est :

\[
P_{\text{dBm}} = 10\log_{10}\left(\frac{P_{\text{mW}}}{1\text{ mW}}\right)
\]

Exemples :

| Puissance | Équivalence approximative |
|---|---:|
| 1 mW | 0 dBm |
| 10 mW | +10 dBm |
| 0,1 mW | -10 dBm |
| 0,01 mW | -20 dBm |

Une puissance négative en dBm n'est pas une puissance négative physiquement. Elle indique simplement une puissance inférieure à 1 mW.

### 6.6. Additionner les pertes

Les pertes exprimées en dB s’additionnent directement lorsqu’elles sont mises en cascade.

Si une liaison comprend :

- 8,8 dB de perte dans la fibre ;
- 1,0 dB de pertes de connecteurs ;
- 1,2 dB de pertes d’épissures ;

alors :

\[
L_{\text{total}} = 8,8 + 1,0 + 1,2
\]

\[
L_{\text{total}} = 11,0\ \text{dB}
\]

Cette propriété facilite les calculs de budget optique.

## 7. Le budget optique

### 7.1. Définition

Le budget optique représente la marge disponible entre la puissance émise par un équipement et la puissance minimale nécessaire à son récepteur.

Pour une estimation simple :

\[
B = P_{\text{Tx,min}} - P_{\text{Rx,sensibilité}}
\]

Avec :

- \(P_{\text{Tx,min}}\) : puissance d’émission minimale spécifiée ;
- \(P_{\text{Rx,sensibilité}}\) : puissance minimale requise par le récepteur.

Le résultat est exprimé en dB.

Le budget disponible doit être supérieur ou égal aux pertes totales estimées, avec une marge appropriée.

### 7.2. Exemple complet

Supposons les caractéristiques pédagogiques suivantes :

- puissance d’émission minimale : -2 dBm ;
- sensibilité du récepteur : -24 dBm ;
- pertes totales de la liaison : 18 dB.

Le budget disponible est :

\[
B = -2 - (-24)
\]

\[
B = 22\ \text{dB}
\]

La marge restante avant prise en compte d'autres réserves est :

\[
M = 22 - 18
\]

\[
M = 4\ \text{dB}
\]

La liaison respecte le budget théorique et dispose de 4 dB de marge.

Cela ne signifie pas automatiquement que la liaison est conforme : il faut également vérifier la puissance maximale admissible du récepteur, la dispersion, le taux d'erreur et les spécifications du système.

### 7.3. Exemple d'une liaison insuffisante

Supposons maintenant :

- puissance minimale d’émission : -2 dBm ;
- sensibilité du récepteur : -24 dBm ;
- pertes estimées : 25 dB.

Le budget disponible reste de 22 dB.

La marge est :

\[
M = 22 - 25 = -3\ \text{dB}
\]

La liaison ne respecte pas le budget théorique.

Solutions possibles selon l’architecture :

- réduire les pertes de connectique ;
- réparer une épissure défectueuse ;
- réduire la distance si une autre route est possible ;
- sélectionner une interface optique compatible avec une portée adaptée ;
- concevoir une amplification optique si elle est techniquement justifiée ;
- utiliser un système de transport approprié.

Il ne faut pas ajouter un amplificateur sans étude : il peut amplifier le bruit et introduire d’autres contraintes.

### 7.4. La puissance minimale et la puissance maximale

Un récepteur optique possède généralement une plage de fonctionnement.

Deux limites doivent être considérées :

1. La sensibilité minimale : le signal doit être suffisamment puissant.
2. La puissance maximale admissible : le signal ne doit pas être trop puissant.

Une puissance trop faible peut provoquer des erreurs ou une perte de liaison.

Une puissance trop élevée peut saturer ou endommager certains récepteurs, selon leurs spécifications.

**Bonne pratique :** comparer la puissance reçue à la plage d’entrée spécifiée dans la documentation exacte du transceiver ou du système.

## 8. Les composants d'une liaison optique

### 8.1. L’émetteur optique

L’émetteur convertit le signal électrique en signal optique.

Dans les équipements télécoms, il peut être intégré à un transceiver.

Un transceiver regroupe généralement un émetteur et un récepteur dans un même module.

Exemples de formats de modules :

- SFP ;
- SFP+ ;
- SFP28 ;
- QSFP28 ;
- autres formats adaptés aux débits et aux générations d’équipements.

Ces formats ne définissent pas à eux seuls la longueur d’onde, la portée ou la technologie optique. Il faut consulter la référence exacte du module.

### 8.2. Le récepteur optique

Le récepteur détecte la lumière et la convertit en signal électrique.

Il doit pouvoir fonctionner avec :

- la longueur d’onde attendue ;
- le niveau de puissance reçu ;
- le format du signal ;
- le débit ;
- les caractéristiques de modulation et de codage.

Un récepteur peut être alimenté par un signal optique visible sur un photomètre tout en échouant à décoder correctement les données. La mesure de puissance ne suffit donc pas à certifier toute la liaison.

### 8.3. Les connecteurs optiques

Les connecteurs sont des éléments critiques de la chaîne de transmission.

Parmi les formats courants :

- LC ;
- SC ;
- FC ;
- ST.

Le format du connecteur ne définit pas à lui seul le type de polissage.

On rencontre notamment :

- UPC : *Ultra Physical Contact* ;
- APC : *Angled Physical Contact*.

Les connecteurs APC utilisent un polissage angulé qui réduit généralement la réflexion de retour.

Les connecteurs APC et UPC ne doivent pas être accouplés entre eux. Il faut respecter la compatibilité du type de connecteur et de son polissage.

Les couleurs des connecteurs peuvent aider à les identifier, mais elles ne remplacent jamais la vérification de la référence et des spécifications.

### 8.4. Les épissures

Une épissure par fusion utilise un appareil spécialisé pour aligner et fusionner les fibres.

Une bonne épissure doit respecter les critères de perte, de continuité et de qualité mécanique définis pour le chantier.

Les défauts possibles comprennent :

- mauvais clivage ;
- mauvais alignement ;
- contamination ;
- bulle ou défaut de fusion ;
- contrainte mécanique ;
- courbure excessive dans la cassette d’épissures.

Une valeur d’épissure affichée par une soudeuse constitue une estimation locale. Elle ne remplace pas une mesure de bout en bout lorsque celle-ci est exigée.

### 8.5. Les tiroirs optiques et panneaux de brassage

Les fibres entrantes sont souvent terminées dans un tiroir optique ou un panneau de brassage.

Ces équipements facilitent :

- l'organisation des fibres ;
- la protection des épissures ;
- l'identification des circuits ;
- le brassage entre fibres et équipements ;
- la maintenance.

Une mauvaise documentation du brassage peut provoquer une interruption même si la fibre est physiquement intacte.

## 9. Qu’est-ce que le WDM ?

### 9.1. Le principe du multiplexage en longueur d’onde

Le WDM signifie *Wavelength Division Multiplexing*.

Il permet de transporter plusieurs canaux optiques utilisant des longueurs d’onde différentes sur une même fibre.

Au lieu d'utiliser une fibre distincte pour chaque canal, plusieurs canaux partagent le même support.

```text
                 PRINCIPE DU MULTIPLEXAGE WDM

  Émetteur λ1 -----------\
                          \
  Émetteur λ2 ------------+----> [ MULTIPLEXEUR ] ======= FIBRE =======
                          /                                      |
  Émetteur λ3 -----------/                                       |
                                                                  v
                                                         [DÉMULTIPLEXEUR]
                                                            /   |   \
                                                           /    |    \
                                                         λ1     λ2    λ3
                                                          |      |     |
                                                        RX1    RX2   RX3
```

Le multiplexeur combine les canaux optiques.

Le démultiplexeur sépare les canaux reçus.

Chaque canal transporte ses propres données. Les canaux partagent la fibre, mais restent distingués par leur longueur d’onde ou leur fréquence optique.

### 9.2. WDM et DWDM

Le WDM désigne le principe général du multiplexage par longueur d’onde.

Le DWDM signifie *Dense Wavelength Division Multiplexing*. Il utilise une grille de fréquences plus dense, définie par des spécifications techniques adaptées au système.

Le CWDM (*Coarse Wavelength Division Multiplexing*) utilise généralement des espacements de canaux plus larges que le DWDM.

| Critère | CWDM | DWDM |
|---|---|---|
| Espacement des canaux | Généralement large | Plus dense |
| Nombre de canaux | Souvent plus limité | Peut être très élevé |
| Précision fréquentielle | Dépend du système | Grille fréquentielle précise |
| Amplification optique | Dépend de l’architecture | Courante dans les systèmes longue distance |
| Applications | Accès, métropolitain, interconnexion selon le besoin | Métropolitain, transport longue distance, dorsales |
| Complexité | Souvent plus simple | Généralement plus élevée |

Ces différences sont générales. Les capacités réelles dépendent des équipements, des transceivers, de la grille, de la fibre et de la conception de la liaison.

### 9.3. Comment le DWDM augmente-t-il la capacité ?

Imaginons une fibre sur laquelle un système transporte 40 canaux indépendants, chacun à 100 Gbit/s.

La capacité nominale agrégée est :

\[
C = N \times D
\]

Avec :

- \(N = 40\) canaux ;
- \(D = 100\) Gbit/s par canal.

Donc :

\[
C = 40 \times 100 = 4000\ \text{Gbit/s}
\]

Soit 4 Tbit/s de capacité nominale agrégée dans cet exemple.

Il s’agit d’un exemple de calcul, et non de la capacité garantie d’une installation donnée.

Le débit utile réellement disponible dépend notamment du format de transmission, du codage, des protections, des marges de conception et de l'architecture de service.

### 9.4. La grille de fréquences DWDM

Dans le DWDM, les canaux sont définis selon une grille de fréquences de référence.

Une grille courante utilise un espacement de 100 GHz. D'autres systèmes utilisent notamment 50 GHz ou des grilles flexibles.

Autour de 1550 nm, un espacement de 100 GHz correspond approximativement à 0,8 nm, tandis que 50 GHz correspond approximativement à 0,4 nm.

Ces équivalences sont approximatives : l'écart en nanomètres varie selon la fréquence centrale.

Il ne faut pas sélectionner une longueur d’onde uniquement en arrondissant une valeur en nanomètres. La planification DWDM doit respecter la grille fréquentielle et les limites du matériel.

### 9.5. Pourquoi les canaux doivent-ils être précisément contrôlés ?

Deux canaux trop proches ou mal alignés peuvent provoquer des problèmes de transmission selon la technologie utilisée.

Les équipements doivent maîtriser :

- la fréquence centrale ;
- la largeur spectrale ;
- la stabilité de l'émetteur ;
- la puissance du canal ;
- le filtrage ;
- les caractéristiques de modulation.

Les systèmes cohérents modernes permettent des formats de modulation complexes et une utilisation plus flexible du spectre, mais ils nécessitent une ingénierie adaptée.

## 10. Architecture d’un système DWDM

### 10.1. Architecture simplifiée

```text
                 ARCHITECTURE DWDM DE BOUT EN BOUT

 SITE A                                                        SITE B

 Client 1                                                     Client 1
    |                                                            ^
    v                                                            |
+-----------+                                              +-----------+
| Transpondeur|                                            | Transpondeur|
+-----+-----+                                              +-----+-----+
      |                                                          ^
      | λ1                                                       | λ1
      v                                                          |
+------------------+                                      +------------------+
|                  |                                      |                  |
| Multiplexeur     |==== FIBRE OPTIQUE / LIGNE DWDM ======| Démultiplexeur   |
|                  |                                      |                  |
+------------------+                                      +------------------+
      ^                                                          |
      | λ2                                                       | λ2
+-----+-----+                                              +-----+-----+
| Transpondeur|                                            | Transpondeur|
+-----------+                                              +-----------+
      ^                                                          |
 Client 2                                                     Client 2
```

Les équipements représentés sont simplifiés. Les architectures réelles peuvent intégrer des muxponders, des transpondeurs cohérents, des ROADM, des amplificateurs, des systèmes de supervision et des fonctions de protection.

### 10.2. Le transpondeur

Le transpondeur adapte un signal client à une interface de ligne optique.

Selon la technologie, il peut effectuer :

- la conversion de format ;
- la génération d’une longueur d’onde de ligne ;
- le codage et le décodage ;
- la modulation ;
- la correction d’erreurs ;
- des fonctions de supervision et de diagnostic.

Le terme exact et les fonctions disponibles varient selon les constructeurs.

### 10.3. Le muxpondeur

Un muxpondeur peut agréger plusieurs signaux clients dans un signal de ligne de capacité supérieure.

Exemple conceptuel :

```text
  Client 10G ----\
  Client 10G -----+----> [ MUXPONDEUR ] ----> Canal optique de ligne
  Client 10G -----+
  Client 10G ----/
```

Le fonctionnement exact dépend du matériel et de la technologie d’agrégation.

Il ne faut pas supposer que quatre interfaces 10G produisent systématiquement un canal de ligne de 40G sans tenir compte des en-têtes, de l'encapsulation, du codage et de la capacité réelle de l'équipement.

### 10.4. Le multiplexeur et le démultiplexeur

Le multiplexeur regroupe plusieurs canaux.

Le démultiplexeur sépare les canaux à l’autre extrémité.

Ces éléments peuvent être passifs. Ils n'effectuent pas nécessairement de régénération électrique du signal.

Leurs performances dépendent notamment de :

- la perte d’insertion ;
- l’isolation entre canaux ;
- la largeur de bande ;
- la planéité spectrale ;
- la compatibilité avec la grille optique.

### 10.5. Les amplificateurs optiques

Les amplificateurs optiques augmentent la puissance d’un signal optique sans nécessairement le convertir en signal électrique.

L’EDFA (*Erbium-Doped Fiber Amplifier*) est une technologie largement utilisée dans les bandes optiques adaptées, notamment la bande C.

Un amplificateur optique peut servir à :

- compenser une partie des pertes d’une ligne ;
- augmenter la portée ;
- maintenir un niveau de puissance adapté au système.

Il amplifie toutefois le bruit optique en même temps que le signal.

Il ne corrige pas automatiquement les erreurs de données, la dispersion excessive ou tous les défauts de transmission.

### 10.6. Les amplificateurs de ligne et de puissance

Selon l’architecture, on peut rencontrer :

- **Booster :** amplificateur placé côté émission pour augmenter la puissance lancée dans la ligne.
- **Amplificateur en ligne :** amplificateur placé sur le trajet pour compenser une partie des pertes.
- **Préamplificateur :** amplificateur placé côté réception pour augmenter le niveau du signal avant le récepteur.

Ces désignations décrivent des rôles fonctionnels. Les architectures et dénominations précises dépendent du système.

### 10.7. Les ROADMs

ROADM signifie *Reconfigurable Optical Add-Drop Multiplexer*.

Un ROADM permet de diriger, d’ajouter ou de retirer des canaux optiques à un nœud du réseau, avec une reconfiguration adaptée.

Il est particulièrement utile dans les réseaux DWDM maillés.

```text
                         NŒUD OPTIQUE ROADM

             Fibre entrante
                   |
                   v
           +------------------+
           |      ROADM       |
           |                  |
           |  Sélection λ1    |------> Sortie locale λ1
           |  Transit λ2      |------> Fibre suivante
           |  Ajout λ3        |<------ Émetteur local λ3
           +------------------+
                   |
                   v
             Fibre sortante
```

Le ROADM permet une gestion flexible du trafic optique. Il ne remplace pas les routeurs IP et ne réalise pas automatiquement le routage des paquets IP.

### 10.8. La régénération optique et électrique

La régénération est parfois décrite par le modèle 3R :

- **Re-amplification :** augmentation du niveau du signal ;
- **Re-shaping :** restauration de la forme du signal ;
- **Re-timing :** restauration du calage temporel.

Une amplification optique transparente ne fournit pas nécessairement toutes ces fonctions.

Une régénération optoélectronique convertit le signal optique en signal électrique, le traite, puis le retransmet sous forme optique.

Les systèmes cohérents modernes disposent aussi de puissantes fonctions de traitement numérique du signal, notamment pour compenser certaines dégradations.

## 11. Les limites physiques d’une liaison DWDM

Une liaison DWDM n’est pas limitée uniquement par la puissance optique.

Les principales contraintes comprennent :

### 11.1. L’atténuation

La puissance diminue avec la distance et les pertes des composants.

### 11.2. La dispersion chromatique

Les différentes composantes spectrales d’un signal peuvent se propager à des vitesses légèrement différentes.

Cela provoque un élargissement temporel des impulsions dans certains systèmes.

La dispersion chromatique dépend de la fibre, de la longueur d’onde et de la distance.

### 11.3. La dispersion des modes de polarisation

La PMD (*Polarization Mode Dispersion*) est liée aux différences de propagation entre états de polarisation.

Elle peut limiter certaines transmissions, notamment à haut débit et sur de longues distances, selon la fibre et la technologie.

### 11.4. Le bruit optique

Les amplificateurs ajoutent du bruit optique. Dans un système amplifié, l’accumulation du bruit peut réduire la qualité du signal.

Le rapport signal/bruit optique, ou OSNR, est donc une mesure importante dans les systèmes DWDM.

### 11.5. Les effets non linéaires

À des puissances et des densités spectrales appropriées, la fibre peut produire des effets non linéaires.

Parmi eux :

- l’automodulation de phase ;
- la modulation de phase croisée ;
- le mélange à quatre ondes ;
- certaines interactions entre canaux.

Ces effets dépendent notamment de la puissance, de la dispersion, de la distance et de l’espacement des canaux.

Augmenter la puissance d’émission n’améliore donc pas toujours la qualité d’une liaison DWDM.

## 12. Les mesures et les outils de terrain

### 12.1. Le photomètre optique

Le photomètre optique mesure la puissance reçue.

Il peut afficher la valeur en dBm ou, selon le modèle, en mW ou en µW.

Il est utilisé pour :

- mesurer la puissance à une extrémité ;
- vérifier une liaison ;
- comparer la mesure à une plage attendue ;
- réaliser certaines mesures de perte lorsqu’il est utilisé avec une source et une méthode appropriées.

Un photomètre ne permet pas à lui seul de localiser précisément un défaut le long de la fibre.

### 12.2. La source optique

Une source optique génère un signal lumineux à une longueur d’onde définie.

Associée à un photomètre, elle permet de mesurer la perte d’insertion d’une liaison selon une procédure de référence.

La mesure doit être effectuée à la longueur d’onde appropriée et avec des cordons de référence adaptés.

### 12.3. L’OTDR

OTDR signifie *Optical Time Domain Reflectometer*.

Cet instrument injecte des impulsions optiques dans la fibre et analyse la lumière rétrodiffusée ainsi que les réflexions.

Il peut aider à localiser :

- les connecteurs ;
- les épissures ;
- les ruptures ;
- certaines courbures ou pertes anormales ;
- la fin de fibre.

Un OTDR n’est pas simplement un photomètre amélioré : il fournit des informations liées à la distance.

```text
             EXEMPLE CONCEPTUEL D'UNE TRACE OTDR

 Niveau du signal
       ^
       |
       |\
       | \
       |  \        Connecteur
       |   \          |
       |    \_________|\
       |               \ \
       |                \ \____ Épissure
       |                 \      \________
       |                  \               \
       |                   \               \___ Rupture
       +------------------------------------------------> Distance
          Départ              Milieu              Fin
```

Ce dessin est schématique. Une trace OTDR réelle comporte des événements et des niveaux qui dépendent de la configuration, de la fibre et des caractéristiques de l'instrument.

### 12.4. Zones mortes de l’OTDR

Après une forte réflexion, l’OTDR peut être incapable de distinguer immédiatement certains événements proches.

Cette limitation est appelée zone morte.

Pour mieux mesurer les premiers connecteurs et les derniers événements, on utilise des fibres de lancement et, lorsque la méthode l’exige, des fibres de réception.

Leur longueur dépend de l’instrument, de la fibre et de l'objectif de mesure.

### 12.5. L’analyseur de spectre optique

Un OSA (*Optical Spectrum Analyzer*) mesure le spectre optique.

Dans un système DWDM, il peut aider à analyser :

- la présence des canaux ;
- leur fréquence centrale ;
- leur puissance ;
- l’espacement des canaux ;
- le bruit optique ;
- certains défauts de planification ou d’équilibrage.

Un photomètre peut indiquer la puissance totale reçue, alors qu’un analyseur de spectre permet d’observer les composantes spectrales.

### 12.6. Comparaison des outils

| Outil | Fonction principale | Limite importante |
|---|---|---|
| Photomètre | Mesurer une puissance optique | Ne localise pas directement un défaut |
| Source optique | Générer un signal de référence | Ne mesure pas seule la perte reçue |
| OTDR | Localiser et caractériser des événements le long d’une fibre | Les résultats dépendent du réglage et de l’interprétation |
| Analyseur de spectre optique | Analyser les canaux et le spectre | Nécessite une méthode de mesure adaptée au système |
| Microscope d’inspection adapté | Inspecter la face d’un connecteur | Ne remplace pas une mesure optique de transmission |
| Soudeuse à fusion | Réaliser une épissure par fusion | L'estimation locale ne certifie pas à elle seule la liaison complète |

## 13. Nettoyage et inspection des connecteurs

La contamination des connecteurs est une cause fréquente de défauts optiques.

Les particules peuvent provoquer :

- des pertes supplémentaires ;
- des réflexions ;
- une instabilité du signal ;
- des dommages à la face optique ;
- des erreurs de transmission.

La procédure professionnelle suit le principe :

**Inspecter → nettoyer si nécessaire → inspecter de nouveau → raccorder → mesurer.**

Bonnes pratiques :

1. Ne jamais regarder directement dans une fibre ou un port optique.
2. Utiliser un microscope d'inspection conçu pour l'optique et les conditions de sécurité appropriées.
3. Utiliser des outils de nettoyage compatibles avec le type de connecteur.
4. Ne pas toucher la face optique avec les doigts.
5. Protéger les connecteurs débranchés avec des capuchons propres.
6. Éviter de réutiliser un capuchon contaminé.
7. Vérifier la compatibilité APC/UPC.
8. Ne pas souffler sur une face optique.
9. Ne pas forcer un connecteur lors du raccordement.
10. Respecter les procédures de sécurité du site.

Un connecteur qui paraît propre à l’œil nu peut présenter une contamination microscopique.

## 14. Les règles de sécurité en fibre optique

### 14.1. Sécurité laser

Certains signaux optiques utilisés dans les télécommunications sont invisibles à l’œil humain.

L’absence de lumière visible ne signifie pas l’absence de danger.

Il ne faut jamais :

- regarder directement dans une fibre ;
- regarder directement dans un connecteur ;
- utiliser l’œil pour vérifier si une fibre émet ;
- diriger une fibre vers une personne ;
- connecter un instrument non prévu pour le niveau de puissance présent.

Avant une intervention, il faut suivre la procédure de consignation et les consignes de sécurité du site.

Lorsque cela est autorisé et approprié, les mesures doivent être effectuées avec des instruments conçus pour cet usage.

### 14.2. Fragments de fibre

Les fragments de fibre de verre sont fins et peuvent pénétrer dans la peau.

Les précautions comprennent :

- utiliser une zone de travail adaptée ;
- collecter immédiatement les fragments dans un contenant prévu à cet effet ;
- ne jamais laisser des fragments sur une table ou dans une poche ;
- respecter les procédures d'élimination ;
- utiliser les équipements de protection exigés.

### 14.3. Sécurité électrique et travail en hauteur

Dans un local télécom, plusieurs risques peuvent coexister :

- alimentation électrique ;
- batteries ;
- équipements sous tension ;
- travail en hauteur ;
- interventions en chambre télécom ;
- circulation routière ;
- risques liés aux sites extérieurs.

La sécurité doit être évaluée pour l'ensemble de l'intervention, pas uniquement pour la fibre.

## 15. Méthode de dépannage d’une liaison optique

Une démarche structurée permet d’éviter les remplacements inutiles.

### 15.1. Étape 1 : recueillir les symptômes

Déterminer :

- le service concerné ;
- les équipements aux deux extrémités ;
- la date d’apparition du défaut ;
- les alarmes présentes ;
- l’existence de travaux récents ;
- l’état des ports ;
- les changements de configuration récents.

### 15.2. Étape 2 : vérifier la compatibilité

Contrôler :

- le type de fibre ;
- les références des transceivers ;
- la longueur d’onde ;
- le débit ;
- le type de connecteur ;
- la portée nominale ;
- les plages de puissance d’émission et de réception.

### 15.3. Étape 3 : examiner les connecteurs

Inspecter et nettoyer les connecteurs selon la procédure autorisée.

Vérifier le brassage et l’identification des fibres.

Ne jamais supposer qu’un câble est correctement raccordé simplement parce qu’il est présent dans le tiroir optique.

### 15.4. Étape 4 : mesurer la puissance

Mesurer la puissance reçue et la comparer à la plage spécifiée par le fabricant.

Si la puissance est trop faible, examiner les pertes de liaison.

Si elle est trop élevée, vérifier la compatibilité du transceiver et les limites d’entrée du récepteur.

### 15.5. Étape 5 : localiser les pertes

Utiliser un OTDR avec une configuration adaptée si une localisation est nécessaire.

Comparer les mesures aux résultats de référence lorsqu'ils existent.

Une trace ancienne peut aider à identifier l'apparition d'un défaut, mais les configurations de mesure doivent être comparables.

### 15.6. Étape 6 : vérifier le service

Une puissance optique correcte ne garantit pas que le service fonctionne.

Vérifier également :

- les alarmes de l’équipement ;
- la synchronisation ;
- les compteurs d’erreurs ;
- la qualité du signal ;
- les paramètres du canal ;
- l’état des interfaces client ;
- les alarmes du système DWDM.

### 15.7. Étape 7 : documenter l’intervention

Enregistrer :

- le site ;
- la fibre ou le circuit ;
- les équipements concernés ;
- les mesures avant intervention ;
- les actions réalisées ;
- les mesures après intervention ;
- l’état final du service ;
- les éventuelles réserves.

## 16. Exemple de dépannage : puissance reçue insuffisante

### Situation

Un circuit optique ne fonctionne plus correctement.

Les données disponibles sont :

- puissance d'émission mesurée : -3 dBm ;
- puissance reçue mesurée : -27 dBm ;
- sensibilité minimale spécifiée du récepteur : -24 dBm.

La perte observée est :

\[
L = P_{\text{Tx}} - P_{\text{Rx}}
\]

\[
L = -3 - (-27)
\]

\[
L = 24\ \text{dB}
\]

La puissance reçue est inférieure de 3 dB à la sensibilité minimale annoncée dans cet exemple.

### Diagnostic

Il faut déterminer si les pertes proviennent :

- d'un connecteur contaminé ;
- d'une épissure défectueuse ;
- d'une courbure ;
- d'une fibre endommagée ;
- d'un composant optique intermédiaire ;
- d'un problème de mesure ou de référence.

### Procédure

1. Vérifier que les instruments et les longueurs d'onde sont adaptés.
2. Inspecter et nettoyer les connecteurs.
3. Vérifier le brassage.
4. Reprendre la mesure de puissance.
5. Comparer le résultat à la référence.
6. Si nécessaire, effectuer une mesure de perte ou une analyse OTDR.
7. Corriger le défaut identifié.
8. Refaire les mesures.
9. Vérifier la qualité du service et les alarmes.

### Résultat attendu

Le résultat doit être compatible avec la plage de fonctionnement du récepteur et respecter les critères d'acceptation du projet.

Il ne faut pas considérer une amélioration de quelques décibels comme une validation automatique sans vérifier l'ensemble des exigences.

## 17. Introduction aux mesures dans un réseau DWDM

Le diagnostic DWDM nécessite de distinguer plusieurs niveaux.

### 17.1. Niveau optique global

On examine :

- la puissance globale ;
- les pertes de la ligne ;
- les niveaux des amplificateurs ;
- les alarmes optiques.

### 17.2. Niveau du canal

On examine :

- la présence de la longueur d'onde attendue ;
- la fréquence centrale ;
- la puissance du canal ;
- l'espacement ;
- les niveaux des canaux voisins.

### 17.3. Niveau de transmission

On examine :

- les alarmes de perte de signal ;
- les erreurs ;
- la qualité du signal ;
- les paramètres de correction d'erreurs lorsqu'ils sont disponibles ;
- les performances du récepteur.

### 17.4. Niveau du service client

On examine :

- le port Ethernet ou l'interface client ;
- le débit négocié ;
- les erreurs d'interface ;
- l'encapsulation ;
- la continuité du service.

Un défaut de service peut se situer à l'un quelconque de ces niveaux.

## 18. Travaux pratiques guidés

Les travaux suivants sont des exercices pédagogiques. Toute intervention sur un réseau opérateur réel doit être autorisée et réalisée selon les procédures du site.

### TP 1 — Calculer les pertes d'une liaison

**Objectif :** calculer la perte estimée d'une liaison optique.

Données :

- distance : 60 km ;
- atténuation : 0,23 dB/km ;
- 6 connecteurs à 0,25 dB chacun ;
- 10 épissures à 0,10 dB chacune.

Étape 1 : calculer la perte de fibre.

\[
L_{\text{fibre}} = 60 \times 0,23
\]

\[
L_{\text{fibre}} = 13,8\ \text{dB}
\]

Étape 2 : calculer la perte des connecteurs.

\[
L_{\text{connecteurs}} = 6 \times 0,25
\]

\[
L_{\text{connecteurs}} = 1,5\ \text{dB}
\]

Étape 3 : calculer la perte des épissures.

\[
L_{\text{épissures}} = 10 \times 0,10
\]

\[
L_{\text{épissures}} = 1,0\ \text{dB}
\]

Étape 4 : calculer la perte totale.

\[
L_{\text{total}} = 13,8 + 1,5 + 1,0
\]

\[
\boxed{L_{\text{total}} = 16,3\ \text{dB}}
\]

**Résultat :** la perte estimée est de 16,3 dB, avant ajout d'une marge d'ingénierie et des autres pertes éventuelles.

### TP 2 — Vérifier un budget optique

**Objectif :** déterminer si une liaison respecte un budget optique simplifié.

Données :

- puissance d'émission minimale : -1 dBm ;
- sensibilité du récepteur : -22 dBm ;
- pertes estimées : 17 dB.

Étape 1 :

\[
B = -1 - (-22)
\]

\[
B = 21\ \text{dB}
\]

Étape 2 :

\[
M = 21 - 17
\]

\[
M = 4\ \text{dB}
\]

**Conclusion :** le budget théorique laisse 4 dB de marge avant prise en compte des réserves complémentaires. La conformité finale dépend des autres limites et critères du système.

### TP 3 — Dimensionner le nombre de canaux DWDM

**Objectif :** comprendre la capacité agrégée.

Un système transporte 32 canaux, chacun à 100 Gbit/s.

\[
C = 32 \times 100
\]

\[
\boxed{C = 3200\ \text{Gbit/s} = 3,2\ \text{Tbit/s}}
\]

**Conclusion :** la capacité nominale agrégée est de 3,2 Tbit/s dans cet exemple.

### TP 4 — Interpréter un défaut

Un équipement indique :

- état du port : actif ;
- puissance reçue : dans la plage spécifiée ;
- erreurs de transmission : en augmentation ;
- alarme de signal absent : aucune.

**Question :** peut-on conclure que la liaison est entièrement conforme ?

**Réponse :** non.

La puissance reçue est un indicateur parmi d'autres. Il faut examiner les erreurs, les alarmes, les paramètres de transmission et la qualité du signal. Dans un système DWDM, une analyse du canal et des indicateurs de performance peut être nécessaire.

### TP 5 — Construire une fiche de mesure

Utiliser le modèle suivant pour une liaison fictive :

```text
FICHE DE MESURE — LIAISON OPTIQUE

Identifiant du circuit :
Site A :
Site B :
Type de fibre :
Longueur estimée :
Longueur d'onde :
Référence de l'émetteur :
Référence du récepteur :

Puissance Tx avant intervention :
Puissance Rx avant intervention :
Puissance Tx après intervention :
Puissance Rx après intervention :

Mesure OTDR réalisée : Oui / Non
Référence de la trace :
Défaut identifié :
Action corrective :
État final du service :
Nom du technicien :
Date :
Observations :
```

L'objectif est d'apprendre à produire une trace écrite exploitable par une équipe d'exploitation ou d'ingénierie.

## 19. Exercices corrigés

### Exercice 1 — Fibre monomode ou multimode ?

Une liaison doit relier deux sites opérateur distants de 35 km.

Quel type de fibre est généralement le plus approprié ?

**Correction :**

La fibre monomode est généralement le choix adapté à cette distance dans un réseau de transport opérateur.

Le choix final dépend du transceiver, du budget optique, de la route et des performances exigées.

### Exercice 2 — Calcul de pertes

Une fibre de 25 km présente une atténuation de 0,24 dB/km. Les connecteurs et les épissures introduisent ensemble 2 dB de pertes.

Calculer la perte totale.

**Correction :**

\[
L_{\text{fibre}} = 25 \times 0,24 = 6\ \text{dB}
\]

\[
L_{\text{total}} = 6 + 2
\]

\[
\boxed{L_{\text{total}} = 8\ \text{dB}}
\]

### Exercice 3 — Calcul du budget

Un émetteur fournit au minimum -3 dBm et le récepteur possède une sensibilité de -25 dBm.

Quel est le budget disponible ?

**Correction :**

\[
B = -3 - (-25)
\]

\[
\boxed{B = 22\ \text{dB}}
\]

### Exercice 4 — Puissance reçue

Un émetteur transmet à -2 dBm. La liaison présente 14 dB de pertes.

Quelle est la puissance reçue estimée ?

**Correction :**

\[
P_{\text{Rx}} = P_{\text{Tx}} - L
\]

\[
P_{\text{Rx}} = -2 - 14
\]

\[
\boxed{P_{\text{Rx}} = -16\ \text{dBm}}
\]

### Exercice 5 — Nombre de canaux

Un système DWDM transporte 48 canaux à 25 Gbit/s chacun.

Calculer la capacité nominale agrégée.

**Correction :**

\[
C = 48 \times 25
\]

\[
\boxed{C = 1200\ \text{Gbit/s} = 1,2\ \text{Tbit/s}}
\]

### Exercice 6 — Choisir un outil

On souhaite localiser une rupture sur une fibre de plusieurs kilomètres.

Quel instrument est généralement approprié ?

**Correction :**

L'OTDR est adapté à la localisation et à la caractérisation d'événements le long de la fibre.

Un photomètre peut confirmer une perte de puissance, mais ne localise pas directement la rupture.

### Exercice 7 — Connecteur contaminé

Après inspection, un connecteur présente des particules sur sa face optique.

Quelle est la bonne démarche ?

**Correction :**

Inspecter, nettoyer avec un équipement compatible, inspecter de nouveau, raccorder selon la procédure, puis vérifier les mesures et le fonctionnement du service.

### Exercice 8 — Le signal est puissant, mais le service ne fonctionne pas

Un photomètre indique une puissance conforme, mais le service reste indisponible.

Donner quatre causes possibles.

**Correction :**

Causes possibles :

1. incompatibilité des transceivers ;
2. mauvaise configuration du port ou du débit ;
3. défaut de modulation, de codage ou de transmission ;
4. erreur de brassage ou problème sur le canal attendu ;
5. défaut du système de transport ou du service client.

Une puissance conforme ne prouve pas que les données sont correctement décodées.

### Exercice 9 — Atténuation excessive

Une liaison de 50 km présente 11 dB de pertes mesurées. La fibre seule est estimée à 10 dB.

Quelle conclusion peut-on tirer ?

**Correction :**

Les pertes des connecteurs, épissures et autres composants représentent environ 1 dB par différence entre les deux valeurs.

Il faut comparer cette différence au budget prévu et aux critères d'acceptation. Si elle est excessive, les composants et la méthode de mesure doivent être vérifiés.

### Exercice 10 — Choisir entre WDM et DWDM

Un opérateur souhaite transporter de nombreux canaux sur une infrastructure existante, avec une gestion fine du spectre et des équipements adaptés aux longues distances.

Quelle technologie est généralement envisagée ?

**Correction :**

Le DWDM est une solution courante pour les systèmes de transport à nombreux canaux. La décision finale dépend de la capacité requise, de la fibre, de la distance, des équipements, du coût et des exigences de protection.

## 20. Défi final corrigé — Concevoir une liaison DWDM

### 20.1. Scénario

Un opérateur doit interconnecter deux sites, Site A et Site B.

Exigences :

- distance : 80 km ;
- fibre monomode ;
- 8 canaux de 100 Gbit/s ;
- atténuation linéique estimée : 0,22 dB/km ;
- 4 connecteurs, chacun estimé à 0,25 dB ;
- 12 épissures, chacune estimée à 0,10 dB ;
- puissance d'émission minimale : -2 dBm ;
- sensibilité du récepteur : -24 dBm.

Pour cet exercice, on ne tient pas compte des pertes supplémentaires d'équipements DWDM, de la dispersion, du bruit des amplificateurs et des marges complémentaires.

### 20.2. Étape 1 — Calculer les pertes

Perte de fibre :

\[
L_{\text{fibre}} = 80 \times 0,22
\]

\[
L_{\text{fibre}} = 17,6\ \text{dB}
\]

Perte des connecteurs :

\[
L_{\text{connecteurs}} = 4 \times 0,25 = 1,0\ \text{dB}
\]

Perte des épissures :

\[
L_{\text{épissures}} = 12 \times 0,10 = 1,2\ \text{dB}
\]

Perte totale simplifiée :

\[
L_{\text{total}} = 17,6 + 1,0 + 1,2
\]

\[
\boxed{L_{\text{total}} = 19,8\ \text{dB}}
\]

### 20.3. Étape 2 — Calculer le budget disponible

\[
B = -2 - (-24)
\]

\[
\boxed{B = 22\ \text{dB}}
\]

### 20.4. Étape 3 — Calculer la marge simplifiée

\[
M = 22 - 19,8
\]

\[
\boxed{M = 2,2\ \text{dB}}
\]

La marge simplifiée est de 2,2 dB.

**Interprétation :** le budget élémentaire semble suffisant, mais la marge est faible pour une conception professionnelle de longue distance. Les pertes des équipements DWDM, les tolérances, les réserves d'ingénierie et les caractéristiques de transmission doivent encore être étudiées.

Il serait incorrect de déclarer cette liaison validée uniquement à partir de ce calcul.

### 20.5. Étape 4 — Calculer la capacité nominale

Le système transporte 8 canaux de 100 Gbit/s.

\[
C = 8 \times 100
\]

\[
\boxed{C = 800\ \text{Gbit/s}}
\]

La capacité nominale agrégée est de 800 Gbit/s.

### 20.6. Étape 5 — Proposer une architecture

```text
SITE A                                                       SITE B

Clients IP/Ethernet                                      Clients IP/Ethernet
       |                                                         ^
       v                                                         |
+-------------------+                                  +-------------------+
| Transpondeurs     |                                  | Transpondeurs     |
| ou muxpondeurs    |                                  | ou muxpondeurs    |
+---------+---------+                                  +---------+---------+
          |                                                        ^
          v                                                        |
+-------------------+                                  +-------------------+
| Multiplexeur DWDM |                                  | Démultiplexeur    |
+---------+---------+                                  +---------+---------+
          |                                                        |
          +================= FIBRE 80 KM ===========================+
                             |
                    Étude de la ligne optique
                    et des pertes réelles
```

Dans un système réel, la conception pourrait nécessiter des amplificateurs, des transpondeurs cohérents, une supervision de ligne ou une autre architecture de transport. Ces choix doivent être fondés sur les spécifications des équipements et sur une étude optique complète.

### 20.7. Étape 6 — Définir les contrôles avant mise en service

Avant d'activer le service, il faut notamment :

1. vérifier le type de fibre et le brassage ;
2. inspecter et nettoyer les connecteurs ;
3. mesurer les pertes de la ligne ;
4. vérifier les puissances aux interfaces ;
5. vérifier les fréquences et canaux prévus ;
6. contrôler les alarmes des équipements ;
7. vérifier les paramètres de qualité de transmission ;
8. tester les services clients ;
9. documenter les résultats ;
10. valider la conformité selon les critères de l'opérateur.

### 20.8. Étape 7 — Identifier les risques

Risques possibles :

- marge optique insuffisante ;
- mauvais brassage ;
- connecteurs contaminés ;
- canal DWDM absent ;
- transceiver incompatible ;
- erreurs de configuration ;
- puissance trop élevée ou trop faible ;
- bruit optique excessif ;
- dégradation de la qualité de transmission.

**Livrable final attendu :** une fiche de conception contenant le schéma de la liaison, le calcul de budget, les équipements prévus, les résultats de mesure, les critères d'acceptation et la procédure de mise en service.

## 21. Bonnes pratiques professionnelles

### 21.1. Avant une intervention

- Consulter le dossier technique.
- Identifier précisément les fibres et les circuits.
- Vérifier les autorisations de travaux.
- Préparer les instruments adaptés.
- Connaître les risques laser.
- Établir une procédure de retour arrière lorsque nécessaire.

### 21.2. Pendant l'intervention

- Ne jamais regarder directement dans une fibre.
- Inspecter et nettoyer les connecteurs.
- Respecter les rayons de courbure.
- Éviter les tractions et contraintes mécaniques.
- Utiliser des instruments calibrés lorsque la procédure l'exige.
- Noter les mesures avant et après intervention.
- Éviter les débranchements non autorisés sur un circuit actif.

### 21.3. Après l'intervention

- Vérifier les alarmes.
- Contrôler les puissances optiques.
- Vérifier les compteurs d'erreurs et la qualité du service.
- Comparer les résultats aux critères d'acceptation.
- Mettre à jour la documentation.
- Informer l'équipe d'exploitation de tout écart restant.

## 22. Erreurs fréquentes à éviter

**Erreur 1 :** penser qu'une puissance reçue correcte garantit un service fonctionnel.

**Correction :** la puissance n'est qu'un indicateur. Il faut également vérifier la qualité de transmission et le service.

**Erreur 2 :** confondre dB et dBm.

**Correction :** le dB représente un rapport ; le dBm représente une puissance absolue référencée à 1 mW.

**Erreur 3 :** supposer que tous les transceivers utilisant un connecteur LC sont compatibles.

**Correction :** vérifier la fibre, la longueur d'onde, le débit, la portée, le budget et les spécifications.

**Erreur 4 :** augmenter systématiquement la puissance d'émission lorsqu'une liaison échoue.

**Correction :** rechercher d'abord le défaut. Une puissance excessive peut dégrader le fonctionnement ou dépasser les limites du récepteur.

**Erreur 5 :** croire qu'un amplificateur optique régénère intégralement le signal.

**Correction :** un amplificateur optique amplifie le signal et le bruit. Il ne réalise pas nécessairement les fonctions de régénération 3R.

**Erreur 6 :** considérer un résultat de soudeuse comme la certification complète de la liaison.

**Correction :** les mesures de bout en bout et les tests exigés par le projet restent nécessaires.

**Erreur 7 :** croire que le DWDM augmente automatiquement le débit d'une interface client.

**Correction :** le DWDM augmente la capacité agrégée transportable sur la fibre. Le débit de chaque interface dépend des équipements et du service configuré.

**Erreur 8 :** mélanger des connecteurs APC et UPC.

**Correction :** respecter les spécifications de connectique et de polissage.

## 23. Glossaire

| Terme | Définition |
|---|---|
| Atténuation | Diminution de la puissance du signal pendant la transmission |
| Budget optique | Marge disponible entre l'émission et les limites du récepteur |
| Canal optique | Signal optique associé à une longueur d'onde ou une fréquence définie |
| Cladding | Gaine optique entourant le cœur |
| CWDM | Multiplexage optique à espacement relativement large des canaux |
| dB | Unité logarithmique exprimant un rapport |
| dBm | Unité de puissance référencée à 1 mW |
| Démultiplexeur | Sépare plusieurs canaux optiques |
| Dispersion chromatique | Étalement temporel lié aux différences de propagation spectrales |
| DWDM | Multiplexage optique dense en longueur d'onde |
| EDFA | Amplificateur optique à fibre dopée à l'erbium |
| Épissure | Jonction de deux fibres optiques |
| Fibre monomode | Fibre conçue pour guider un mode spatial fondamental dans son fonctionnement normal |
| Fibre multimode | Fibre permettant la propagation de plusieurs modes spatiaux |
| Longueur d'onde | Grandeur décrivant la périodicité spatiale d'une onde |
| Muxpondeur | Équipement agrégeant plusieurs signaux clients vers un signal de ligne |
| Multiplexeur | Combine plusieurs canaux optiques |
| OSA | Analyseur de spectre optique |
| OSNR | Rapport signal optique sur bruit optique |
| OTDR | Instrument de mesure et de localisation d'événements sur une fibre |
| Photomètre | Instrument mesurant la puissance optique |
| ROADM | Équipement optique reconfigurable permettant d'ajouter, de retirer ou de diriger des canaux |
| Transceiver | Module intégrant un émetteur et un récepteur |
| Transpondeur | Équipement adaptant un signal client à une interface de transport |
| WDM | Multiplexage par répartition en longueur d'onde |

## 24. Documentation technique de référence

Pour approfondir le sujet, consulter les documentations officielles et les recommandations techniques suivantes :

- **ITU-T — Recommandations sur les fibres optiques :** https://www.itu.int/rec/T-REC-G.652
- **ITU-T — Fibre monomode G.657 :** https://www.itu.int/rec/T-REC-G.657
- **ITU-T — Technologies de transport optique :** https://www.itu.int/ITU-T/recommendations/
- **IEC — Normes de fibres et de composants optiques :** https://www.iec.ch/
- **FOA — The Fiber Optic Association :** https://www.thefoa.org/
- **Cisco — Documentation technique :** https://www.cisco.com/c/en/us/support/index.html
- **Nokia — Documentation et ressources techniques :** https://www.nokia.com/
- **Ciena — Ressources sur les réseaux optiques :** https://www.ciena.com/

Pour toute installation réelle, utiliser les fiches techniques exactes des transceivers, les spécifications de la fibre, les plans optiques et les procédures de l'opérateur. Les valeurs utilisées dans les exemples de ce cours servent à apprendre les calculs et ne remplacent pas une étude d'ingénierie.

## 25. Évaluation finale

L'apprenant doit être capable de répondre sans aide aux questions suivantes :

1. Pourquoi la fibre monomode est-elle utilisée dans de nombreux réseaux de transport opérateur ?
2. Quelle est la différence entre dB et dBm ?
3. Comment calcule-t-on la perte totale d'une liaison ?
4. Comment détermine-t-on un budget optique élémentaire ?
5. Pourquoi un récepteur peut-il échouer même si la puissance optique est correcte ?
6. Quelle est la fonction d'un multiplexeur DWDM ?
7. Quel est le rôle d'un amplificateur EDFA ?
8. Pourquoi faut-il contrôler le spectre optique dans un système DWDM ?
9. À quoi sert un OTDR ?
10. Pourquoi faut-il inspecter et nettoyer les connecteurs ?
11. Quels sont les risques liés aux lasers et aux fragments de fibre ?
12. Pourquoi une liaison ne doit-elle pas être déclarée conforme sur la seule base d'un calcul théorique ?

### Critères de réussite

L'apprenant est prêt à poursuivre vers un niveau supérieur lorsqu'il sait :

- expliquer l'architecture d'une liaison optique ;
- calculer des pertes et un budget optique simple ;
- identifier les composants principaux d'un système DWDM ;
- choisir l'outil de mesure adapté à un problème donné ;
- proposer une procédure de diagnostic cohérente ;
- documenter une intervention ;
- appliquer les règles de sécurité optique.

**Fin du cours — `telecom-dwdm-debutant.md`**

**Prochaine étape du module :** `telecom-mpls-tp-intermediaire.md` — MPLS-TP & Métro Ethernet.
