# VLANs Avancés et Sécurité de Couche 2

**Niveau :** Administrateur Réseau Senior / Expert

Au niveau expert, nous allons voir comment isoler des équipements au sein d'un même VLAN (Private VLANs), comment gérer les téléphones IP (Voice VLAN), et comment se protéger contre les attaques de pirates (VLAN Hopping).

> **Analogie** : Les Private VLANs sont comme un immeuble avec un hall commun (VLAN Primaire) et des appartements individuels (VLANs Isolés). Tout le monde peut sortir dans le hall, mais personne ne peut entrer chez son voisin.


## 1. Les Private VLANs (VLANs Privés)

Dans un Datacenter ou un hôtel, on veut parfois que des serveurs ou des clients soient dans le même sous-réseau IP, mais qu'ils **ne puissent pas communiquer entre eux** (pour éviter qu'un serveur piraté ne contamine ses voisins). Les Private VLANs permettent cela via une hiérarchie :

- **VLAN Primaire** : Le VLAN principal (ex: VLAN 100).
- **VLAN Isolé (Isolated)** : Les ports ne peuvent parler qu'au port Promiscuous. Ils ne peuvent pas parler aux autres ports isolés.
- **VLAN Community** : Les ports peuvent parler entre eux, mais pas aux ports isolés.
- **Port Promiscuous** : Port souvent relié à un routeur ou un firewall, qui peut parler à tout le monde.

### Schéma : Architecture des Private VLANs

```text
       [ Routeur / Firewall ]
                |
        (Port Promiscuous)
                |
+-------------------------------+
|      VLAN Primaire 100        |
|                               |
|  +---------+    +---------+   |
|  | Isolé 1 |    | Isolé 2 |   |
|  | (Web)   |    | (DB)    |   |
|  +---------+    +---------+   |
|      |               |        |
|  (Ne peuvent pas communiquer) |
+-------------------------------+
cisco
vlan 100
 private-vlan primary
 private-vlan association 101,102
vlan 101
 private-vlan isolated
vlan 102
 private-vlan community
2. Le Voice VLAN (VLAN de Voix)
Un téléphone IP et un PC sont souvent branchés sur la même prise murale (le téléphone a un petit switch intégré). Le Voice VLAN permet de séparer le trafic voix (prioritaire) du trafic data.
Le téléphone utilise le CDP ou LLDP-MED pour demander au switch son VLAN de voix.

cisco
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 20
 switchport voice vlan 10
 mls qos trust cos
💡 Astuce : Le PC branché derrière le téléphone sera dans le VLAN 20 (Data) alors que le téléphone sera dans le VLAN 10 (Voix). Le switch fait la différence grâce au protocole CDP.

3. L'attaque VLAN Hopping
Le VLAN Hopping est une technique utilisée par les pirates pour passer d'un VLAN à un autre sans passer par un routeur. Il y a deux méthodes principales :

Méthode A : Switch Spoofing
Le pirate configure son PC en mode Trunk (avec le protocole DTP) pour négocier un lien Trunk avec le switch. Le switch lui envoie alors les trames de tous les VLANs.
Contre-mesure : Désactiver le DTP sur les ports d'accès.

cisco
interface FastEthernet0/1
 switchport mode access
 switchport nonegotiate
Méthode B : Double Tagging
Le pirate envoie une trame avec deux tags 802.1Q. Le premier switch (switch d'accès) retire le tag externe (car il correspond au VLAN Natif). La trame est ensuite transmise avec le tag interne au switch de destination, qui l'envoie dans le VLAN cible.

Schéma : L'attaque Double Tagging
text
Trame du pirate : [ MAC | TAG VLAN 1 (Natif) | TAG VLAN 20 (Cible) | DATA ]

1. Le switch d'accès voit le Tag VLAN 1, le retire et laisse passer la trame.
2. Le switch suivant voit le Tag VLAN 20 et livre la trame au VLAN 20 !
Contre-mesure : Ne jamais utiliser le VLAN 1 comme VLAN Natif. Ne pas mettre de ports access dans le VLAN Natif.

cisco
interface GigabitEthernet0/1
 switchport mode trunk
 switchport nonegotiate
 switchport trunk native vlan 999
