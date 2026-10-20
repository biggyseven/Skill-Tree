# Le Modèle OSI et TCP/IP

Le modèle OSI (Open Systems Interconnection) et le modèle TCP/IP sont les deux cadres de référence pour comprendre comment les données circulent sur un réseau.

## 1. Le modèle OSI (7 couches)
Le modèle OSI est un modèle théorique qui décompose la communication réseau en 7 couches distinctes. Chaque couche a un rôle précis et fournit des services à la couche supérieure.

1. **Physique** : Transmission des bits sur le support (câbles, ondes radio, fibre).
2. **Liaison de données** : Encapsulation en trames, adressage MAC, détection d'erreurs (Ethernet, Wi-Fi).
3. **Réseau** : Acheminement des paquets entre réseaux différents, adressage IP, routage (IP, ICMP).
4. **Transport** : Segmentation, fiabilité, multiplexage par ports (TCP, UDP).
5. **Session** : Établissement, gestion et fin des sessions de communication.
6. **Présentation** : Formatage des données, chiffrement, compression (TLS, JPEG).
7. **Application** : Interface avec l'utilisateur et les logiciels (HTTP, DNS, SSH).

### Moyen mnémotechnique
Pour se souvenir de l'ordre (de la couche 7 à la 1) : **A**pplication, **P**résentation, **S**ession, **T**ransport, **R**éseau, **L**iaison, **P**hysique (A.P.S.T.R.L.P).

## 2. Le modèle TCP/IP (4 couches)
Le modèle TCP/IP est le modèle pratique utilisé sur Internet. Il regroupe certaines couches OSI.

- **Application** (OSI 5, 6, 7) : HTTP, FTP, DNS, SMTP.
- **Transport** (OSI 4) : TCP (fiable), UDP (rapide).
- **Internet** (OSI 3) : IP (IPv4, IPv6), ICMP, ARP.
- **Accès Réseau** (OSI 1, 2) : Ethernet, Wi-Fi, fibres.

## 3. L'encapsulation
Quand vous envoyez un message, les données descendent les couches et chaque couche ajoute son propre en-tête. C'est l'encapsulation.

| Couche OSI | PDU (Protocole Data Unit) | Équipement typique |
| :--- | :--- | :--- |
| Application | Données | Serveurs, PC |
| Transport | Segment (TCP) / Datagramme (UDP) | Pare-feu L4 |
| Réseau | Paquet | Routeur |
| Liaison | Trame | Switch |
| Physique | Bits | Câble, Hub |

Lors de la réception, c'est l'opération inverse : la **décapsulation**. Chaque couche lit son en-tête et passe le reste à la couche supérieure.

## 4. Atelier de dépannage (Troubleshooting)
La connaissance du modèle OSI permet de diagnostiquer les pannes efficacement.
- **Couche 1** : Le câble est-il branché ? La LED est-elle allumée ?
- **Couche 2** : L'adresse MAC est-elle apprise par le switch ? (Commande : `show mac address-table`).
- **Couche 3** : Puis-je pinguer l'adresse IP distante ? (Commande : `ping`).
- **Couche 4** : Le port est-il ouvert ? (Commande : `telnet <ip> <port>` ou `nc -zv`).
- **Couche 7** : L'application répond-elle ? (Commande : `curl -v http://...`).