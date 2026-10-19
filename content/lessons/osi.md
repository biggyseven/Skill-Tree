# Le modèle OSI

Le modèle **OSI** découpe les communications réseau en sept couches. Il sert
de cadre commun pour comprendre où une fonction intervient et pour structurer
un diagnostic.

| Couche | Nom | Rôle et exemples |
| --- | --- | --- |
| 7 | Application | Services utilisés par les applications : HTTP, DNS, SSH |
| 6 | Présentation | Représentation, encodage et chiffrement des données |
| 5 | Session | Établissement et gestion des échanges entre applications |
| 4 | Transport | Communication de bout en bout : TCP, UDP, ports |
| 3 | Réseau | Adressage logique et acheminement : IP, routeurs |
| 2 | Liaison de données | Trames, adresses MAC et commutation Ethernet |
| 1 | Physique | Transmission des bits sur le support : cuivre, fibre, radio |

Les couches basses transportent les données vers leur destination ; les
couches hautes fournissent des services aux applications. Lors d'un incident,
on peut partir du physique et remonter (*bottom-up*), partir du symptôme
applicatif et descendre (*top-down*), ou isoler progressivement le segment en
panne.

Le modèle est un outil de raisonnement, pas une description exacte de chaque
protocole : certaines fonctions traversent plusieurs couches.
