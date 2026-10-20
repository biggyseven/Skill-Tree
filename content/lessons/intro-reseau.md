# Qu'est-ce qu'un réseau ?

Un réseau informatique est un ensemble d'appareils reliés entre eux pour
échanger des informations. Ces appareils peuvent être des ordinateurs, des
téléphones, des imprimantes, des serveurs ou des objets connectés.

> Analogie : imagine une maison avec plusieurs pièces. Sans interphone, il faut
> se déplacer pour parler à quelqu'un. Avec un réseau, chaque appareil peut
> joindre les autres sans bouger, comme si chaque pièce avait un interphone.

Un réseau sert à partager des fichiers, aller sur Internet, imprimer à
distance, regarder une vidéo ou envoyer un message. Pour que tout le monde se
comprenne, les appareils suivent des règles communes appelées **protocoles**.

## LAN et WAN

On classe souvent les réseaux selon leur taille.

| Type | Signification | Exemple |
|---|---|---|
| LAN | Local Area Network, réseau local | La maison, une salle de classe, un petit bureau |
| WAN | Wide Area Network, réseau étendu | Internet, le réseau entre plusieurs villes |
| WLAN | LAN sans fil | Le Wi-Fi de la maison |
| MAN | Réseau métropolitain | Le réseau d'une ville |

Un LAN reste dans une zone limitée. Un WAN relie des zones éloignées. Internet
est le plus grand WAN : c'est un réseau de réseaux.

## Client et serveur

Dans beaucoup d'échanges, un appareil demande un service et un autre le
fournit.

- Le **client** demande : navigateur, application de messagerie, jeu en ligne.
- Le **serveur** répond : site web, boîte mail, service de stockage.

> Analogie : au restaurant, le client commande un plat et le serveur apporte le
> plat. Le serveur ne fait pas manger le client : chacun a un rôle.

Un même appareil peut être client à un moment et serveur à un autre. Ton
ordinateur est client quand il consulte un site, mais il peut être serveur si tu
partages un fichier avec un autre appareil du réseau.

## Les topologies

La **topologie** décrit la façon dont les appareils sont reliés.

### Topologie en étoile

C'est la plus courante aujourd'hui. Tous les appareils passent par un
équipement central, souvent un switch.

```text
        PC 1
          |
PC 2 --- SWITCH --- PC 3
          |
        PC 4
```

Si un câble est coupé, seul l'appareil concerné est isolé. Si le switch tombe
en panne, tout le petit réseau est bloqué.

### Topologie en bus

Tous les appareils partagent un même câble principal.

```text
PC 1 ---- PC 2 ---- PC 3 ---- PC 4
```

C'était pratique pour de petits réseaux, mais une coupure du câble principal
pouvait bloquer plusieurs appareils.

### Topologie en anneau

Les appareils forment une boucle. Les données circulent d'un appareil à
l'autre. Ce modèle est moins courant dans les réseaux modernes.

### Topologie maillée

Les appareils ont plusieurs chemins possibles. C'est solide, mais cela demande
plus de câbles et de configuration. Internet utilise une logique de maillage
entre de nombreux réseaux.

## Le voyage d'une information

Quand tu ouvres un site web :

1. Ton appareil prépare une demande.
2. Cette demande est découpée en petits morceaux appelés **paquets**.
3. Les paquets passent par le réseau local.
4. La box ou le routeur les envoie vers Internet.
5. Le serveur répond, puis les paquets reviennent dans l'autre sens.

Tu n'as pas besoin de connaître tout le trajet pour utiliser Internet, comme tu
n'as pas besoin de connaître toutes les routes pour recevoir une lettre.

## Quelques mots utiles

| Mot | Idée simple |
|---|---|
| Protocole | Une langue commune entre appareils |
| Paquet | Un petit morceau de message |
| Interface réseau | La « porte » par laquelle un appareil se connecte |
| Switch | Relie les appareils d'un même réseau local |
| Routeur | Relie des réseaux différents |
| Adresse IP | L'adresse logique d'un appareil sur un réseau |

## À retenir

- Un réseau relie des appareils pour échanger des informations.
- Un LAN est local ; un WAN est étendu.
- Le client demande, le serveur répond.
- La topologie en étoile est la plus fréquente.
- Les paquets sont les petits morceaux qui transportent les messages.

Dans le prochain cours, nous allons regarder les câbles et les appareils qui
rendent tout cela possible.
