# Sécurité de Couche 2 (Layer 2 Security) - Débutant

**Niveau :** Débutant

**Prérequis :** Notions de base en réseau (Modèle OSI, rôles des commutateurs/switches, adresses MAC, adresses IP, fonctionnement de base de DHCP et ARP).

Ce cours introduit les concepts fondamentaux de la **sécurité de la couche 2 (Lien de Données)** dans le modèle OSI. Il explique pourquoi la couche 2 est vulnérable par nature et détails les attaques classiques ainsi que les mécanismes de protection essentiels à déployer sur les commutateurs réseau.

---

## 1. Pourquoi la Couche 2 est-elle Vulnérable ?

### Le Principe de Confiance Implicite

Dans un réseau local (LAN), les équipements de la couche 2 (principalement les commutateurs ou *switches*) transmettent les trames Ethernet en se basant sur les adresses MAC. 

Par défaut, les protocoles de la couche 2 ont été conçus pour fonctionner dans un environnement de **confiance** :
* Aucun mécanisme natif ne vérifie l'identité réelle de l'émetteur d'une trame.
* Les requêtes de diffusion (*Broadcast*) comme ARP ou DHCP sont transmises à tout le monde.
* Un attaquant connecté sur un port Ethernet d'un commutateur peut facilement usurper une identité ou perturber l'ensemble du réseau local.

```
                  SITUATION SANS SÉCURITÉ L2
                  
   [ Attaquant ] ─── (Trame falsifiée / Usurpation MAC/IP)
         │
         ▼
 ┌───────────────┐
 │ Commutateur   │ ── (Accepte aveuglément la trame et l'achemine)
 └───────┬───────┘
         │
         ▼
    [ Victime ] (Trafic intercepté ou service interrompu)
```

> **Règle d'or :** Si la couche 2 est compromise, toutes les couches supérieures (IP, TCP/UDP, TLS, applications) deviennent vulnérables.

---

## 2. Les Menaces Principales en Couche 2

### A. Saturation de la Table d'Adresses MAC (MAC Flooding)

#### Le Problème
Un commutateur enregistre les adresses MAC associées à chaque port dans une table appelée table **CAM** (*Content Addressable Memory*). Cette table a une taille limitée.

Un attaquant génère des milliers de trames Ethernet fictives avec des adresses MAC sources aléatoires.

```
                    SATURATION DE LA TABLE CAM (MAC Flooding)

 [ Attaquant ] ───> Trame 1 (MAC: AA:AA:AA:AA:AA:01) ───┐
               ───> Trame 2 (MAC: AA:AA:AA:AA:AA:02) ───┼──> [ Table CAM Saturée ! ]
               ───> Trame 3 (MAC: AA:AA:AA:AA:AA:03) ───┘    (Port 1 = MAC 01, 02, 03...)
```

#### L'Impact
Lorsque la table CAM est saturée, le commutateur passe en mode dégradé : il agit comme un simple **hub**. Chaque nouvelle trame reçue est diffusée sur **tous les ports** (*Unicast Flooding*). L'attaquant peut alors intercepter tout le trafic du réseau.

---

### B. Usurpation ARP (ARP Spoofing / Poisoning)

#### Le Problème
Le protocole ARP (*Address Resolution Protocol*) permet d'associer une adresse IP à une adresse MAC. Les requêtes ARP ne comportent aucune authentification.

Un attaquant envoie de fausses réponses ARP non sollicitées à une victime et à la passerelle par défaut (routeur), affirmant détenir l'adresse IP du routeur.

```
                   USURPATION ARP (Man-in-the-Middle)

 [ Routeur (192.168.1.1) ]                       [ Victime (192.168.1.50) ]
       │                                                      │
       │  "192.168.1.50 est chez MAC-Attaquant"               │  "192.168.1.1 est chez MAC-Attaquant"
       └─────────────────────────┐  ┌─────────────────────────┘
                                 ▼  ▼
                           [ Attaquant ]
                       (MAC: BB:BB:BB:BB:BB:BB)
```

#### L'Impact
L'attaquant s'intercale entre la victime et le routeur (**Man-in-the-Middle / MITM**). Il peut lire, modifier ou bloquer le trafic traversant le réseau.

---

### C. Piratage du Service DHCP (Rogue DHCP Server)

#### Le Problème
Lorsqu'un client se connecte, il envoie une requête `DHCP Discover` en broadcast. Si un attaquant branche un faux serveur DHCP (*Rogue DHCP Server*), celui-ci peut répondre plus rapidement que le serveur légitime.

```
                    SERVEUR DHCP PIRATE (Rogue DHCP)

                             [ Client ]
                                 │
                         DHCP Discover (Broadcast)
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
     [ Serveur DHCP Légitime ]       [ Faux Serveur DHCP ]
     (IP: 192.168.1.50)             (Répond en PREMIER)
     (GW: 192.168.1.1)               (GW: IP-Attaquant ! / DNS-Attaquant)
```

#### L'Impact
Le client reçoit une mauvaise passerelle par défaut (*Gateway*) ou de mauvais serveurs DNS, ce qui permet à l'attaquant de rediriger tout le trafic du client vers ses propres serveurs.

---

## 3. Les Mécanismes de Protection Essentiels

Pour contrer ces attaques, les commutateurs disposent de fonctionnalités de sécurité natives à activer sur leurs ports.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      FONCTIONS DE SÉCURITÉ L2                          │
├───────────────────────┬────────────────────────┬───────────────────────┤
│ Port Security         │ DHCP Snooping          │ Dynamic ARP Inspection│
│ (Bloque MAC Flooding) │ (Bloque Rogue DHCP)    │ (DAI - Bloque ARP)    │
└───────────────────────┴────────────────────────┴───────────────────────┘
```

---

### A. Port Security (Sécurisation des Ports)

**Objectif :** Limiter le nombre d'adresses MAC autorisées sur un port d'accès et bloquer les équipements non autorisés.

* **Fixe ou Dynamique :** On peut définir manuellement les adresses MAC autorisées ou les apprendre dynamiquement (*Sticky MAC*).
* **Actions en cas de violation :**
  1. `Protect` : Jette les trames non autorisées sans notification.
  2. `Restrict` : Jette les trames, incrémente un compteur de violation et envoie une alerte.
  3. `Shutdown` (Par défaut) : Désactive immédiatement le port (*err-disable*).

```
                      MÉCANISME PORT SECURITY

 [ Equipement Référencé (MAC-A) ] ──> [ Port 1 (Max 1 MAC) ] ──> PASS (Autorisé)
 [ Attaquant / Laptop (MAC-B)   ] ──> [ Port 1 (Max 1 MAC) ] ──> BLOCK / SHUTDOWN
```

---

### B. DHCP Snooping (Inspection DHCP)

**Objectif :** Valider les messages DHCP et empêcher l'apparition de faux serveurs DHCP.

#### Le Principe des Ports De Confiance / Non-Confiance (*Trusted / Untrusted*) :
* **Ports Trusted (De confiance) :** Ports connectés aux serveurs DHCP légitimes ou à d'autres switches. Les réponses DHCP (`DHCP Offer`, `DHCP Ack`) y sont autorisées.
* **Ports Untrusted (Non-confiance) :** Ports destinés aux utilisateurs. Si un message de type réponse DHCP tente d'entrer par ce port, il est immédiatement **bloqué**.

```
                   FONCTIONNEMENT DU DHCP SNOOPING

 [ Serveur DHCP ] ─── (Port Trusted) ───┐
                                        ▼
                                ┌───────────────┐
                                │ Switch Cisco  │
                                └───────┬───────┘
                                        ▲
 [ Attaquant ] ────── (Port Untrusted) ─┘
 (Tente d'envoyer DHCP Offer) ──> [ BLOQUÉ PAR LE SWITCH ]
```

#### La Base de Données DHCP Snooping Binding
Le commutateur construit une table dynamique en écoutant les échanges DHCP valides :

| Adresse MAC | Adresse IP | VLAN | Port |
| :--- | :--- | :--- | :--- |
| `0011.2233.4455` | `192.168.1.50` | 10 | FastEthernet 0/1 |
| `6677.8899.AABB` | `192.168.1.51` | 10 | FastEthernet 0/2 |

*Cette table servira de base pour la protection ARP (DAI).*

---

### C. Dynamic ARP Inspection (DAI)

**Objectif :** Empêcher l'usurpation ARP (*ARP Spoofing*).

#### Le Principe :
Le commutateur intercepte toutes les réponses ARP sur les ports *untrusted*. Il compare l'adresse IP et l'adresse MAC contenues dans le message ARP avec la **base de données DHCP Snooping Binding**.

* **Si l'association IP/MAC correspond :** Le message ARP est transmis.
* **Si l'association est inconnue ou incohérente :** Le paquet ARP est **jeté**.

```
                    FONCTIONNEMENT DE DAI

 [ Attaquant ] ──> "Je suis 192.168.1.1 (MAC-Attaquant)"
                         │
                         ▼ (Port Untrusted)
                 ┌───────────────┐
                 │ Switch (DAI)  │ ──> Vérification dans la table Snooping
                 └───────┬───────┘     (192.168.1.1 est associé à MAC-Routeur, PAS MAC-Attaquant)
                         │
                         ▼
                 [ PAQUET REJETÉ ]
```

---

## 4. Exemple Concret de Configuration de Base (Cisco IOS)

Voici une configuration type pour sécuriser un port d'accès utilisateur sur un commutateur Cisco.

```text
! ==========================================
! 1. ACTIVATION DU DHCP SNOOPING GLOBALE
! ==========================================
ip dhcp snooping
ip dhcp snooping vlan 10

! ==========================================
! 2. ACTIVATION DE DYNAMIC ARP INSPECTION (DAI)
! ==========================================
ip arp inspection vlan 10

! ==========================================
! 3. CONFIGURATION DU PORT VERS LE SERVEUR DHCP (PORT TRUSTED)
! ==========================================
interface GigabitEthernet0/1
 description ** PORT VERS SERVEUR DHCP OU ROUTEUR **
 ip dhcp snooping trust
 ip arp inspection trust

! ==========================================
! 4. CONFIGURATION DU PORT UTILISATEUR (PORT UNTRUSTED)
! ==========================================
interface FastEthernet0/1
 description ** PORT ACCES UTILISATEUR **
 switchport mode access
 switchport access vlan 10
 
 ! Configuration de Port Security
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 
 ! Limitation du débit des paquets ARP pour éviter les DÉNI DE SERVICE (DoS)
 ip arp inspection limit rate 15
```

---

## 5. Synthèse des Attaques et Parades

| Type d'Attaque | Objectif de l'Attaquant | Solution de Protection |
| :--- | :--- | :--- |
| **MAC Flooding** | Saturer la table CAM pour transformer le switch en hub. | **Port Security** |
| **Rogue DHCP** | Distribuer de mauvaises passerelles/DNS aux clients. | **DHCP Snooping** |
| **ARP Spoofing** | Réaliser une attaque Man-in-the-Middle (MITM). | **Dynamic ARP Inspection (DAI)** |
| **DDoS sur ARP/DHCP** | Épuiser les ressources processeur du switch. | **Rate Limiting** (Limitation de débit) |

---

## Points à Retenir

1. **Pas de sécurité implicite :** La couche 2 n'intègre pas de mécanisme d'authentification natif.
2. **Port Security :** Bloque la saturation de la table CAM et filtre les adresses MAC sur un port.
3. **DHCP Snooping :** Bloque les faux serveurs DHCP et construit une table d'associations IP/MAC.
4. **Dynamic ARP Inspection (DAI) :** S'appuie sur la table créée par le DHCP Snooping pour bloquer les fausses réponses ARP.
5. **Pré-requis d'activation :** DAI nécessite que le **DHCP Snooping** soit configuré au préalable.