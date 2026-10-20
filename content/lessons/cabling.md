# Câblage et normes

Le câblage est la fondation physique du réseau. Même avec les meilleurs switches
et routeurs, une liaison mal sertie, trop longue ou installée à côté d'une source
de perturbation peut provoquer des pertes, des négociations de vitesse étranges
ou des coupures intermittentes.

> Analogie : le câblage est la route entre deux villes. Une route étroite, mal
> entretenue ou coupée par un obstacle empêche les véhicules d'arriver, même si
> les panneaux et les feux de circulation sont parfaits.

Ce cours présente les deux grands supports du réseau local — le cuivre et la
fibre — puis les normes de brochage, les catégories, les connecteurs et les
bonnes pratiques d'installation.

## 1. Le cuivre : paires torsadées

Le câble réseau le plus répandu est le câble à paires torsadées. Il contient
quatre paires de fils de cuivre, soit huit conducteurs. Les paires sont
torsadées pour réduire les interférences électromagnétiques et la diaphonie,
c'est-à-dire le signal d'une paire qui perturbe une autre paire.

On distingue plusieurs constructions :

| Construction | Signification | Usage |
|---|---|---|
| UTP | Unshielded Twisted Pair, sans blindage | Maison, bureau, câblage courant |
| FTP | Foiled Twisted Pair, écran global en feuille | Environnement avec perturbations modérées |
| STP | Shielded Twisted Pair, blindage par paire ou global | Milieu industriel, fortes perturbations |
| S/FTP | Blindage global et blindage par paire | Environnements exigeants, data centers |

Le blindage n'est pas magique. Il doit être correctement relié à la terre et
les connecteurs doivent être adaptés. Un câble blindé mal terminé peut être
moins performant qu'un bon UTP. Pour une maison ou un petit bureau, l'UTP de
qualité suffit généralement.

### Pourquoi les paires sont torsadées

Deux fils proches forment une antenne involontaire. En les torsadant, les
perturbations sont réparties et s'annulent en partie. Le nombre de torsades par
mètre et la qualité du cuivre influencent la fréquence maximale que le câble
peut transporter.

Le câble ne transporte pas seulement des « bits » : il transporte des signaux
électriques. La qualité de ces signaux dépend de la longueur, du diamètre du
cuivre, des connecteurs, des courbures et de l'environnement.

## 2. Les catégories de câbles cuivre

Une catégorie décrit des performances électriques, notamment la fréquence
maximale et la capacité à limiter les perturbations. Elle ne garantit pas à
elle seule le débit final : les connecteurs, les patch panels, les cordons et
l'installation doivent respecter le même niveau.

| Catégorie | Fréquence | Usage typique | Remarques |
|---|---:|---|---|
| Cat 5e | 100 MHz | 1 Gb/s jusqu'à 100 m | Très courant, encore suffisant pour beaucoup d'usages |
| Cat 6 | 250 MHz | 1 Gb/s sur 100 m, 10 Gb/s sur 55 m | Meilleure marge que Cat 5e |
| Cat 6a | 500 MHz | 10 Gb/s jusqu'à 100 m | Blindage souvent présent, adapté aux nouveaux bâtiments |
| Cat 7 | 600 MHz | 10 Gb/s sur 100 m | Norme ISO, connecteurs parfois spécifiques |
| Cat 8 | 2 000 MHz | 25/40 Gb/s sur 30 m | Très courtes distances, data centers |

Quelques précisions importantes :

- La longueur maximale d'un canal cuivre est généralement de **100 mètres** :
  90 mètres de câble permanent et 10 mètres de cordons souples.
- Les performances annoncées supposent une installation conforme, pas un câble
  posé n'importe comment.
- Cat 7 et Cat 8 ne se contentent pas toujours d'une prise RJ45 classique :
  certains connecteurs spécialisés (GG45, TERA) sont utilisés pour garantir les
  performances.
- Pour une maison, Cat 5e ou Cat 6 est souvent suffisant. Pour un bâtiment neuf
  où l'on veut de la marge, Cat 6a est un choix courant.
- Le câble doit être adapté à l'usage : un câble trop rigide dans un cordon de
  brassage peut casser à force d'être plié.

### Le mythe du « câble qui augmente le débit »

Un câble de catégorie supérieure ne transforme pas un port 100 Mb/s en port
10 Gb/s. Les deux extrémités, la carte réseau, le switch et la qualité de la
liaison doivent négocier la même vitesse. Un bon câble permet simplement de ne
pas être le maillon faible.

## 3. Brochage T568A et T568B

Un connecteur RJ45 contient huit broches. Deux normes de brochage sont
utilisées dans le monde :

```text
T568A
Broche 1  : blanc/vert
Broche 2  : vert
Broche 3  : blanc/orange
Broche 4  : bleu
Broche 5  : blanc/bleu
Broche 6  : orange
Broche 7  : blanc/marron
Broche 8  : marron
```

```text
T568B
Broche 1  : blanc/orange
Broche 2  : orange
Broche 3  : blanc/vert
Broche 4  : bleu
Broche 5  : blanc/bleu
Broche 6  : vert
Broche 7  : blanc/marron
Broche 8  : marron
```

Les deux normes ont les mêmes performances électriques. Le plus important est
d'être cohérent : on choisit T568A ou T568B pour le site et on l'applique aux
deux extrémités des câbles droits.

### Câble droit et câble croisé

- **Câble droit** : même norme aux deux extrémités. Il relie un PC à un switch,
  une prise murale à un switch, ou un équipement à un patch panel.
- **Câble croisé** : T568A d'un côté, T568B de l'autre. Il servait autrefois à
  relier directement deux PC ou deux switches.
- **Auto-MDIX** : la plupart des ports modernes détectent automatiquement le
  type de câble et corrigent la polarité. Cela ne dispense pas de suivre une
  norme de câblage propre.

Les paires 1-2 et 3-6 suffisent pour l'Ethernet 10/100 Mb/s. Le Gigabit utilise
les quatre paires. C'est pour cette raison qu'un câble mal serti peut fonctionner
en 100 Mb/s mais échouer en 1 Gb/s.

## 4. Le connecteur RJ45 et les outils

Le connecteur que l'on appelle communément **RJ45** est techniquement un
connecteur **8P8C** (8 positions, 8 contacts). Il est utilisé avec les câbles à
paires torsadées.

Les éléments d'une installation cuivre :

| Élément | Rôle |
|---|---|
| Connecteur RJ45 | Terminaison d'un cordon ou d'une prise |
| Keystone | Module femelle monté dans une prise murale |
| Patch panel | Regroupe les arrivées de câbles dans le local technique |
| Cordon de brassage | Relie le patch panel au switch |
| Pince à sertir | Fixe le connecteur sur les conducteurs |
| Testeur de câble | Vérifie la continuité et le brochage |
| Certificateur | Mesure les performances de la liaison |

Un câble réseau ne se sertit pas comme un câble électrique. Il faut respecter
l'ordre des fils, ne pas dénuder trop longtemps, couper les conducteurs à la
bonne longueur et vérifier que chaque broche est bien en contact.

### Bonnes pratiques de sertissage

1. Dénuder la gaine sur une longueur suffisante sans entailler les paires.
2. Conserver les torsades le plus près possible du connecteur.
3. Placer les fils dans l'ordre T568A ou T568B.
4. Couper les fils bien droit.
5. Insérer le connecteur jusqu'au bout.
6. Sertir une seule fois avec l'outil adapté.
7. Tester la continuité et le brochage.
8. Tirer doucement pour vérifier que le connecteur tient.

Un câble qui « fonctionne parfois » est souvent un câble avec une broche mal
enfoncée, une gaine coupée trop loin ou un connecteur mal serti.

## 5. La fibre optique

La fibre transporte la lumière dans un cœur de verre ou de plastique. Elle est
immunisée contre les interférences électromagnétiques et convient aux longues
distances et aux hauts débits.

### Fibre monomode et multimode

| Type | Cœur | Distance typique | Usage |
|---|---|---|---|
| Monomode (SMF) | Très petit, environ 9 µm | Plusieurs kilomètres à dizaines de kilomètres | WAN, liaisons entre bâtiments, opérateurs |
| Multimode (MMF) | 50 ou 62,5 µm | Quelques centaines de mètres | Data centers, campus, bâtiments proches |

Les fibres multimodes sont souvent classées OM1, OM2, OM3, OM4 et OM5. Les
générations récentes permettent des débits élevés sur des distances plus
longues, mais la distance reste plus limitée que pour la monomode.

> Analogie : la monomode est un tunnel étroit dans lequel un seul rayon lumineux
> voyage loin. La multimode est un tunnel plus large où plusieurs rayons
> rebondissent sur les parois.

### Connecteurs fibre

| Connecteur | Forme | Usage |
|---|---|---|
| LC | Petit connecteur à clip | Très courant dans les switches et SFP |
| SC | Carré, push-pull | Anciens équipements, installations structurées |
| ST | Baïonnette | Anciens réseaux fibre |
| MPO/MTP | Connecteur multi-fibres | Data centers, 40/100 Gb/s |

On trouve aussi des connecteurs UPC et APC. Leur face optique est polie
différemment. Il ne faut pas les mélanger sans vérifier la compatibilité, car
cela peut provoquer des pertes ou abîmer les faces.

### Modules SFP et SFP+

Un switch ne possède pas toujours de port fibre natif. On insère un module
**SFP** ou **SFP+** dans une cage prévue. Le module convertit le signal
électrique en signal optique. Il faut choisir le module selon :

- le type de fibre (monomode ou multimode) ;
- la distance ;
- le connecteur (LC, SC…) ;
- la vitesse (1 Gb/s, 10 Gb/s, 25 Gb/s…) ;
- la compatibilité avec le switch.

Un module trop puissant pour une courte distance peut saturer le récepteur. Un
module inadapté à la fibre ne fonctionnera pas, même s'il entre dans la cage.

### Propreté de la fibre

La fibre est fragile et la poussière est une cause fréquente de panne. Une
fibre doit être nettoyée avec un outil adapté avant d'être branchée. Regarder
une fibre dans les yeux est dangereux : la lumière peut être invisible et
puissante.

## 6. Cuivre ou fibre : le choix

| Critère | Cuivre | Fibre |
|---|---|---|
| Distance | 100 m environ | Centaines de mètres à kilomètres |
| Débit | Jusqu'à 10 Gb/s selon catégorie | Très élevé, 10/25/40/100 Gb/s |
| Interférences | Sensible aux perturbations | Immunisée aux EMI |
| Alimentation | PoE possible | Ne transporte pas l'électricité |
| Coût | Souvent moins cher | Modules et outils plus chers |
| Installation | Sertissage et tests | Nettoyage, courbures, épissures |
| Usage typique | Postes, imprimantes, caméras | Backbone, data center, longue distance |

Le cuivre reste excellent pour les postes de travail et les appareils
alimentés par PoE. La fibre est privilégiée lorsque la distance, le débit ou
l'immunité aux perturbations sont critiques.

## 7. Câblage structuré

Un bâtiment bien câblé ne se résume pas à des câbles visibles. On organise :

- les prises murales dans les bureaux ;
- les câbles horizontaux qui vont vers le local technique ;
- les patch panels qui regroupent les arrivées ;
- les cordons de brassage vers les switches ;
- le backbone entre les étages ou les bâtiments ;
- l'étiquetage et la documentation.

```text
Bureau                 Local technique
+---------+            +-------------+
| Prise   |------------| Patch panel |
| murale  |  câble     |             |
+---------+  horizontal+------+------+
                              |
                         cordon de brassage
                              |
                         +----+----+
                         | Switch  |
                         +---------+
```

Cette organisation permet de déplacer un poste sans refaire tout le câblage.
Elle facilite aussi le diagnostic : on sait quel câble arrive sur quelle prise
et sur quel port.

### Bonnes pratiques d'installation

- Respecter le rayon de courbure du câble ; ne pas le plier à angle droit.
- Ne pas tirer le câble par le connecteur.
- Éviter de poser le cuivre parallèlement à des câbles électriques puissants.
- Utiliser des chemins de câbles et des fixations adaptées.
- Ne pas serrer les colliers au point d'écraser les paires.
- Étiqueter les deux extrémités.
- Laisser une longueur de service raisonnable dans les coffrets.
- Utiliser des matériaux conformes aux normes incendie du bâtiment.
- Tester et documenter avant de fermer les murs.

## 8. PoE : alimenter par le câble réseau

Le **Power over Ethernet** transporte l'alimentation électrique en même temps
que les données. Il est très utilisé pour les téléphones IP, les bornes Wi-Fi,
les caméras et certains capteurs.

| Norme | Puissance disponible au port | Usage typique |
|---|---:|---|
| 802.3af (PoE) | Environ 15 W | Téléphone IP, petite caméra |
| 802.3at (PoE+) | Environ 30 W | Borne Wi-Fi, caméra motorisée |
| 802.3bt (PoE++) | Environ 60 à 90 W | Écran, borne Wi-Fi performante, éclairage |

Le PoE dépend de la qualité du câble et de la distance. Un câble trop fin ou
trop long peut provoquer une chute de tension. Le switch doit annoncer le budget
PoE nécessaire et l'appareil doit être compatible avec la norme négociée.

## 9. Tester et diagnostiquer

### Testeur de câble

Un testeur simple vérifie la continuité et l'ordre des paires. Il ne garantit
pas les performances haut débit. Pour un câble neuf ou une liaison critique, un
certificateur mesure :

- la longueur ;
- l'atténuation ;
- la diaphonie (NEXT) ;
- le retour de perte ;
- le brochage ;
- la marge par rapport à la catégorie.

### Fibre

Pour la fibre, on utilise un photomètre et une source lumineuse, ou un OTDR
pour localiser les défauts. Un connecteur sale peut provoquer une perte
importante sans être visible à l'œil nu.

### Méthode de dépannage

1. Vérifier les LED du port : lien et activité.
2. Remplacer le cordon par un cordon connu comme bon.
3. Tester une autre prise ou un autre port.
4. Vérifier la vitesse négociée.
5. Inspecter les connecteurs et les courbures.
6. Tester le câble avec l'outil adapté.
7. Documenter le résultat.

> Un câble n'est pas coupable parce qu'il est vieux. On l'accuse après l'avoir
> testé, pas avant.

## 10. Cas concrets

### Cas 1 : un poste négocie en 100 Mb/s

Le câble est un Cat 5e neuf, mais le poste négocie seulement 100 Mb/s. On
vérifie le cordon, la prise et le port. Si les paires 4-5 et 7-8 sont coupées,
le Gigabit ne peut pas fonctionner. On remplace le cordon ou on re-sertit la
prise, puis on vérifie la négociation.

### Cas 2 : une caméra PoE redémarre

La caméra fonctionne quelque temps puis redémarre. Le câble est long et le
budget PoE est proche de la limite. On mesure la tension et on remplace le
câble par une catégorie adaptée, ou on utilise une alimentation locale.

### Cas 3 : une liaison fibre ne monte pas

Le module SFP est inséré, mais le lien reste down. On vérifie la propreté des
connecteurs, la polarité duplex, le type de fibre et la compatibilité du module.
Un nettoyage et un échange de brins suffisent souvent.

### Cas 4 : un nouveau bureau est instable

Le câble passe le long d'un câble électrique et les colliers sont très serrés.
On sépare les chemins, on desserre les fixations et on remplace le cordon
abîmé. Les erreurs disparaissent.

## 11. À retenir

- Le cuivre à paires torsadées est le support courant du LAN.
- Cat 5e, Cat 6, Cat 6a, Cat 7 et Cat 8 n'ont pas les mêmes fréquences ni les
  mêmes distances.
- T568A et T568B sont deux normes de brochage ; on en choisit une et on reste
  cohérent.
- Un câble droit utilise la même norme aux deux extrémités.
- La fibre est adaptée aux longues distances et aux environnements perturbés.
- Les connecteurs et les modules doivent correspondre au support et à la
  distance.
- Un câblage structuré, étiqueté et testé fait gagner beaucoup de temps.
- Un problème de câble se diagnostique avec des tests, pas au hasard.

La qualité du câblage ne se voit pas toujours, mais elle se mesure. Une
installation propre et documentée est déjà une base solide pour tout le reste
du réseau.
