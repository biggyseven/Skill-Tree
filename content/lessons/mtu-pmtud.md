# Cours intensif sur le dépannage MTU et PMTUD
*Niveau : Administrateur réseau senior / Ingénieur de support réseau*
*Durée : 3 jours (≈ 12 heures de contenu, avec laboratoires pratiques)*

---

## 1. Introduction

Le **Maximum Transmission Unit (MTU)** est la plus grande taille de paquet que le niveau de liaison peut transmettre. Une valeur MTU incorrecte peut entraîner des fragments, des pertes de paquets, une latence élevée et une dégradation des performances des applications.

**Path MTU Discovery (PMTUD)** est une technique utilisée par les protocoles IP (IPv4 et IPv6) pour déterminer de manière dynamique le MTU maximal utilisable sur un chemin donné, évitant ainsi le besoin de fragmentation au niveau des couches réseau. Cependant, PMTUD peut échouer pour diverses raisons (filtres de pare-feu, configuration incorrecte, fragmentation au niveau de la couche de liaison, etc.), nécessitant un dépannage systématique.

Ce cours combine théorie et pratique, offrant :

* Concepts approfondis sur le fonctionnement de l'MTU et de PMTUD.
* Commandes exactes sur équipements Cisco, Juniper, Arista et systèmes Linux/Unix.
* Scénarios de dépannage étape par étape avec capture de trafic et analyse.
* Feuille de triche sous forme de tableau comparatif des commandes et des indicateurs.
* Laboratoire pratique où vous simulerez des problèmes courants, collecterez des données et appliquerez des procédures de dépannage.

---

## 2. Rappels techniques

### 2.1 Unités et valeurs typiques

| Niveau de liaison | MTU typique (octets) | Remarques |
|---------------|------------------------|---------|
| Ethernet (802.3) | 1500 | Valeur par défaut sur la plupart des LAN |
| Ethernet à grande MTU (9000) | 9000 | IEEE 802.3ac, utilisé pour le tronçonnage |
| PPPoE (ADSL) | 1492 | 8 octets PPP + 2 octets PPPoE = 1500‑8 |
| WLAN (802.11) | 1400‑1500 | Dépend de l'encapsulation 802.11 et de l'ERP |
| Frame Relay | 1500 | Généralement configuré |
| LTE/3G (lien point à point) | 1400‑1500 | Dépend du protocole de couche 2 |

### 2.2 Processus de fragmentation IP

```
   +-------------------+      +-------------------+
   |  Application Data | ---> |   IP Header       |
   +-------------------+      +-------------------+
                              | Total Length |
                              |   > MTU       |
                              +-----------+-------------------+
                                          |
                               Fragmentation IP
                                          |
   +-------------------+      +-----------+----------+-----------+
   |   IP Fragment 1  | ---> |  New IP   | Data ...| Checksum |
   +-------------------+      +-----------+----------+-----------+
   |   IP Fragment 2  | ---> |  New IP   | Data ...| Checksum |
   +-------------------+      +-----------+----------+-----------+
```

*IPv4* fragment les paquets lorsque **Total Length > MTU** et le drapeau **DF (Don't‑Fragment)** est à 0. *IPv6* ne fragmente jamais au niveau du routeur ; le côté source doit effectuer PMTUD.

### 2.3 Algorithme PMTUD (RFC 1191 / RFC 8200)

1. **Emballage du paquet de test** – Le côté source envoie un paquet avec l'en-tête **DF = 1**.
2. **Si le routeur ne peut pas transmettre** → génère une erreur **ICMP « Fragmentation Needed » (type 3, code 4)** (IPv4) ou **ICMPv6 « Packet Too Big » (type 2)**.
3. **Mise à jour du MTU** – Le côté source réduit son MTU de chemin estimé à **MTU du routeur − 28** (IPv4) ou **MTU du routeur** (IPv6).
4. **Répétition** jusqu'à ce qu'un paquet s'ajuste.

Si aucun paquet **Too‑Big** n'est reçu dans un délai (généralement 10 s), le côté source suppose que le MTU est le MTU de la liaison locale.

---

## 3. Problèmes courants et leurs symptômes

| Symptôme | Cause probable | Commande(s) de vérification rapide |
|---------|--------------|--------------------|
| **Fragmentation observée** (`ip frag`) | Valeur MTU incorrecte, DF à 0, fragmentation au niveau de la liaison | `show ip traffic` (Cisco), `cat /proc/net/snmp | grep IpFrag` (Linux) |
| **Paquets perdus sans ICMP** | Filtre de pare-feu bloquant les messages d'erreur, route statique avec MTU incorrect | `debug ip packet` (Cisco), `tcpdump -i any icmp` |
| **Latence élevée pour le trafic HTTPS/SSH** | Surfragmentation entraînant de nombreux petits fragments, surcharge de réassembly | `show platform hardware qosc` (Cisco), `ss -s` (Linux) |
| **Dépassement de buffer de réception** (`ifInErrors`) | Paquets plus grands que le MTU de réception du routeur adjacent | `show interfaces` (vérifier « input errors »), `ethtool -s <iface> max‑frame` (Linux) |
| **PMTUD inopérant sur IPv6** | Blocage de l'ICMPv6 « Packet‑Too‑Big » par un pare-feu, route par défaut avec MTU incorrect | `ipv6 traffic‑icmp` (Cisco), `ping6 -M do -s <size>` (Linux) |

---

## 4. Outils et commandes de dépannage

### 4.1 Commande Cisco IOS / IOS XE

| Objectif | Commande | Sortie attendue |
|------|---------|-----------------|
| Afficher le MTU actuel sur une interface | `show interfaces <if> | include MTU` | `MTU is 1500` |
| Définir le MTU d'une interface | `interface <if> ; ip mtu <value>` | La commande configure la valeur |
| Activer/désactiver DF sur une source (routeur) | `ip tcp adjust-mss <value>` (définit le MSS basé sur le MTU) | Ajuste le MSS TCP à la valeur spécifiée |
| Capturer les messages ICMP Too‑Big | `debug ip icmp` + `undebug all` après | Affiche les messages d'erreur de fragmentation |
| Afficher les statistiques de fragmentation | `show ip traffic | include fragment` | Compteurs de fragments envoyés/réçus |
| Vérifier la valeur MTU du chemin vers une destination | `ping -c 10 -M do -s <size> <dest>` (envoie des paquets DF) | « Packet too big » → affiche le MTU du routeur émetteur |
| Vérifier la table PMTUD locale (IOS 12.2S et sup) | `show ip tcp path-mtu` | Liste des MTU de chemin par destination |

### 4.2 Commande Cisco NX‑OS (plateformes de commutateurs)

| Objectif | Commande | Sortie attendue |
|------|---------|-----------------|
| Afficher le MTU d'une VLAN/etherchannel | `show interface <if> | inc MTU` | `MTU: 1500` |
| Configurer le MTU sur un trunk | `interface <if> ; mtu <value>` | Applique le MTU au niveau de la couche 2 |
| Débogage des messages ICMPv6 | `ipv6 traffic‑icmp` (activer « packet-too-big ») | Affiche les messages ICMPv6 |
| Tester le PMTUD sur une route IPv6 | `ping6 -c 5 -M do -s <size> <dest>` | Affiche les erreurs « Too Big » |

### 4.3 Commande Juniper Junos

| Objectif | Commande | Sortie attendue |
|------|---------|-----------------|
| Afficher le MTU sur un port | `show interfaces <if> extensive | match MTU` | `Local MTU: 1500` |
| Configurer le MTU sur une interface | `set interfaces <if> mtu <value>` | Applique le MTU |
| Afficher les messages d'erreur ICMPv4 | `diagnose icmp statistics` | Compteurs de « Fragmentation Needed » |
| Tester le PMTUD (IPv4) | `ping -D -s <size> <dest>` (utilise DF) | « Packet Too Big » → affiche le MTU |
| Tester le PMTUD (IPv6) | `ping6 -M do -s <size> <dest>` | Affiche les messages d'erreur ICMPv6 |

### 4.4 Commande Linux/Unix

| Objectif | Commande | Sortie attendue |
|------|---------|-----------------|
| Afficher le MTU d'une interface | `ip link show <if>` | `mtu 1500` |
| Définir le MTU | `ip link set dev <if> mtu <value>` | Applique la valeur |
| Afficher la valeur MTU du chemin (PMTUD) | `ping -M do -s <size> <dest>` (IPv4) | « frag needed » → affiche le MTU du routeur |
| IPv6 PMTUD | `ping6 -M do -s <size> <dest>` | « Packet Too Big » → affiche le MTU |
| Capturer l'ICMP | `tcpdump -i <if> icmp` | Affiche les paquets d'erreur |
| Afficher les statistiques de fragmentation | `cat /proc/net/snmp | grep IpFrag` | Compteurs de fragments |
| Débogage détaillé des sockets TCP (MSS) | `ss -i -o state established` | Affiche le MSS calculé |

---

## 5. Tableau comparatif

| Fonctionnalité | Cisco IOS | Juniper Junos | Arista EOS | Linux (ip route) |
|---------|-----------|---------------|------------|------------------|
| Afficher le MTU de l'interface | `show int <if> | include MTU` | `show interfaces <if> | match MTU` | `show running-config | include mtu` | `ip link show <if>` |
| Configurer le MTU | `ip mtu <value>` | `set interfaces <if> mtu <value>` | `interface <if> ; mtu <value>` | `ip link set dev <if> mtu <value>` |
| Tester le PMTUD IPv4 | `ping -M do -s <size>` | identique | identique | identique |
| Débogage ICMPv6 | `ipv6 traffic‑icmp` | `diagnose icmp6 statistics` | `ipv6 icmp filter` | `tcpdump -i <if> icmp6` |
| Afficher la table PMTUD TCP | `show ip tcp path-mtu` | `show tcp extensive` (pas de table dédiée) | `show tcp brief` | `ss -p state established` |
| Définir le MSS TCP (basé sur MTU) | `ip tcp adjust-mss <value>` | `set protocols tcp mss <value>` | `interface <if> ; ip tcp adjust-mss <value>` | `sysctl -w net.ipv4.tcp_mtu_probing=2` |

---

## 6. Schémas ASCII

### 6.1 Flux de fonctionnement de PMTUD

```
   +----------+      +----------+      +----------+
   |  Host A  | ---> | Router 1 | ---> | Router 2 | ---> Destination
   | (MTU=1500)|    | (MTU=1500)|    | (MTU=1400)|    |
   +----------+      +----------+      +----------+
          |                |                |
   Ping -M do -s 1500   |                |
   (DF=1, size>1400)   |                |
          |                |                |
   ICMP: Packet Too Big (MTU=1400)   <-- Router 2
          |                |                |
   Host A réduit le MTU de chemin à 1400   |
          |                |                |
   Les prochains pings utilisent 1400 octets          |
```

### 6.2 Exemple de capture de fragmentation

```
   +-------------------+   +-------------------+   +-------------------+
   |   Paquet original |   |  Fragment 1      |   |  Fragment 2       |
   |  IP Total=1520    |   |  IP Total=600    |   |  IP Total=  ?    |
   |  DF=0             |   |  Offset=0        |   |  Offset=600      |
   |  Payload=1500    |   |  Payload=540     |   |  Payload=   ?    |
   +-------------------+   +-------------------+   +-------------------+
```

---

## 7. Procédure de dépannage systématique

1. **Collecter les données de base**
   * `show interfaces <if>` – confirmer le MTU de chaque côté.
   * `show ip traffic` / `cat /proc/net/snmp` – vérifier les compteurs de fragments.
   * `traceroute` (ou `traceroute6`) – identifier le saut qui génère « Too‑Big ».

2. **Tester le drapeau DF localement**
   * `ping -M do -s <size>` (IPv4) ou `ping6 -M do -s <size>` (IPv6).
   * Utiliser une taille supérieure au MTU de la liaison locale pour forcer une erreur.

3. **Capturer les messages d'erreur ICMP**
   * `tcpdump -i <if> icmp` (IPv4) ou `tcpdump -i <if> icmp6`.
   * Vérifier la présence de « Fragmentation Needed » (type 3, code 4) ou « Packet Too Big » (type 2).

4. **Examiner les configurations du routeur**
   * `show running-config | include mtu` – s'assurer que chaque interface a la valeur correcte.
   * `show ip route` – vérifier s'il existe des routes statiques avec une métrique MTU incorrecte (Cisco IOS XE utilise `ip route <dest> <mask> <next-hop> mtu <value>`).

5. **Vérifier les ACL et les filtres de pare-feu**
   * `show access-lists` – rechercher toute règle bloquant l'ICMP 3/4 ou ICMPv6 2.
   * Sur les ASA Cisco : `show access-list icmp`. Supprimer ou autoriser les messages d'erreur.

6. **Inspecter le niveau de liaison**
   * Sur Ethernet, vérifier le « Maximum Transmission Unit » et le « Maximum Frame Size ».
   * Sur les liens série : `show interface <if> | include « link‑protocol »` et `show cable` (Cable Modem).

7. **Simuler une fragmentation au niveau du routeur**
   * `debug ip packet` sur le routeur entrant pour observer les paquets qui dépassent le MTU et sont fragmentés.

8. **Réappliquer le PMTUD manuellement si nécessaire**
   * Sur un hôte Linux : `sysctl -w net.ipv4.ip_no_pmtudisc=0` (activer PMTUD).
   * Sur un hôte Cisco : `no ip tcp adjust-mss` puis `ip tcp adjust-mss <nouvelle valeur>`.

9. **Valider la correction**
   * Exécuter `ping -c 100 -M do -s <size>` (où size ≤ MTU de chemin estimé) et vérifier l'absence de perte.
   * Vérifier `show ip traffic` pour une absence de comptage de fragments.

10. **Documenter et mettre en place des mesures préventives**
    * Ajouter une alerte sur le comptage des erreurs de fragmentation.
    * Configurer le MSS TCP sur les tunnels (par exemple, GRE, IPsec) pour éviter le dépassement de MTU.

---

## 8. Atelier