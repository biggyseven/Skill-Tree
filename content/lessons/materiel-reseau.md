# Le matériel réseau

Pour construire un réseau, il faut des supports pour transporter les données
et des équipements pour les diriger. On peut comparer le réseau à un système de
livraison : les câbles sont les routes, le switch est un carrefour du quartier
et le routeur est le postier qui choisit la direction.

## Les câbles et le sans-fil

### Le câble Ethernet

C'est le câble le plus courant dans un réseau local. Il se termine par une
prise **RJ45**, qui ressemble à une grosse prise téléphonique.

| Câble | Usage simple |
|---|---|
| Ethernet cuivre | Relier un PC, une box ou un switch dans une maison ou un bureau |
| Fibre optique | Transporter des données loin et très vite, avec de la lumière |
| Wi-Fi | Relier sans câble, pratique pour les téléphones et les portables |

Les câbles Ethernet ont des catégories, par exemple Cat 5e, Cat 6 ou Cat 6a.
Pour un usage domestique, un câble de bonne qualité suffit. Le Wi-Fi est
pratique, mais il peut être gêné par les murs, la distance ou les appareils
voisins.

> Analogie : le câble est une route fermée entre deux maisons. Le Wi-Fi est une
> conversation à distance : pratique, mais parfois moins stable.

## Le switch

Le **switch** relie plusieurs appareils dans un même réseau local. Il possède
plusieurs ports Ethernet et envoie chaque trame vers le bon appareil.

> Analogie : un switch est une multiprise intelligente. Tous les appareils y
> sont branchés, mais il ne diffuse pas la conversation à tout le monde : il
> essaie de l'envoyer uniquement au bon destinataire.

Un switch travaille principalement avec les adresses **MAC**, qui sont des
adresses physiques inscrites sur les cartes réseau. Il ne relie pas, à lui seul,
ton réseau local à Internet.

## Le routeur

Le **routeur** relie des réseaux différents. Il choisit par où envoyer les
paquets pour qu'ils arrivent à destination.

> Analogie : le routeur est un postier. Il regarde l'adresse de destination,
> consulte sa table de routes, puis envoie la lettre vers le bon prochain
> bureau.

Un routeur travaille avec les adresses **IP**. Dans une maison, la box fait
souvent office de routeur : elle relie le réseau local au réseau de ton
fournisseur d'accès Internet.

## La box Internet

La box est un appareil « tout-en-un ». Elle peut contenir :

- un **modem**, pour communiquer avec le réseau du fournisseur d'accès ;
- un **routeur**, pour relier la maison à Internet ;
- un **switch**, pour plusieurs prises Ethernet ;
- un **point d'accès Wi-Fi**, pour les appareils sans fil ;
- un **pare-feu**, pour filtrer une partie du trafic.

> Analogie : la box est le hall d'entrée de l'immeuble. Les résidents passent
> par elle pour sortir, et elle décide comment les visiteurs peuvent entrer.

## Une maison typique

```text
                 Internet
                    |
             +-------------+
             |    Box      |
             | modem+routeur|
             | Wi-Fi       |
             +------+------+
                    |
             +------+------+
             |   Switch    |
             +--+---+---+--+
                |   |   |
              PC  TV  Console
```

Le téléphone et le portable peuvent se connecter au Wi-Fi de la box. Les
appareils fixes utilisent souvent un câble Ethernet.

## Qui fait quoi ?

| Équipement | Rôle principal | Adresse utilisée |
|---|---|---|
| Carte réseau | Connecter l'appareil au support | MAC |
| Switch | Relier les appareils d'un LAN | MAC |
| Routeur | Relier des réseaux différents | IP |
| Box | Modem + routeur + switch + Wi-Fi | IP et MAC |
| Point d'accès Wi-Fi | Ajouter une connexion sans fil | MAC |

## Un peu de dépannage

Si un appareil ne se connecte pas :

1. Vérifie que le câble est bien enfoncé des deux côtés.
2. Regarde les petites LED du port réseau : elles indiquent souvent un lien.
3. Essaie un autre câble ou une autre prise.
4. Redémarre la box et l'appareil.
5. Vérifie que tu es bien sur le bon réseau Wi-Fi.

Il ne faut pas tout changer en même temps. On teste une cause à la fois, comme
on vérifie une prise avant de démonter toute l'installation électrique.

## À retenir

- Le câble Ethernet et le Wi-Fi sont deux façons de transporter les données.
- Le switch relie les appareils d'un même réseau local.
- Le routeur relie des réseaux différents.
- La box regroupe plusieurs fonctions dans un seul appareil.
- Le switch utilise les adresses MAC ; le routeur utilise les adresses IP.

Dans le prochain cours, nous allons voir comment les appareils obtiennent une
adresse IP et comment ils trouvent leur chemin vers Internet.
