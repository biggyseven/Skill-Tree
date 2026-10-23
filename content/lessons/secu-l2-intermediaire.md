# Sécurité de Couche 2 (Layer 2 Security) - Intermédiaire

**Niveau :** Intermédiaire

**Prérequis :** Sécurité de Couche 2 Débutant (`secu-l2-debutant.md`), compréhension approfondie du fonctionnement de Spanning Tree Protocol (STP), des trunks 802.1Q, du routage inter-VLAN et de l'architecture d'authentification 802.1X.

Ce cours traite des vulnérabilités d'infrastructures L2 plus complexes. Nous aborderons la manipulation du protocole d'arbre couvant (**STP Attacks**), le saut de VLAN (**VLAN Hopping**), l'usurpation de paires d'IP/MAC (**IP Source Guard**) et le contrôle d'accès réseau basé sur l'identité (**802.1X / MAB**).

---

## 1. Attaques et Sécurisation du Spanning Tree Protocol (STP)

### Le Risque d'Attaque STP

Le protocole Spanning Tree Protocol (STP / IEEE 802.1D / 802.1w) empêche les boucles de niveau 2 en élisant un **Root Bridge** (Pont Racine). 

Par défaut, tout commutateur qui envoie une trame **BPDU** (*Bridge Protocol Data Unit*) avec une priorité inférieure à celle du Root Bridge actuel devient le nouveau Root Bridge du réseau.

```
                  ATTAQUE STP : DÉTOURNEMENT DU ROOT BRIDGE

           [ Commutateur Racine Légitime ]
                (Priorité: 4096)
                       │
                       ▼
               ┌───────────────┐
               │ Commutateur   │
               └───────┬───────┘
                       │
                       ▼ (Port d'Accès Utilisateur)
               [ Attaquant ]
        (Envoie BPDU avec Priorité = 0)
                       │
                       ▼
     "Je suis le nouveau Root Bridge !"
   (Tout le trafic du réseau est re-routé vers l'attaquant)
```

**Conséquence :** Le trafic de plusieurs VLANs peut être redirigé à travers le port de l'attaquant, permettant une attaque Man-in-the-Middle ou un déni de service global (DoS).

---

### Les Mécanismes de Protection STP

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PROTECTIONS STP                                 │
├───────────────────────┬────────────────────────┬───────────────────────┤
│ BPDU Guard            │ Root Guard             │ BPDU Filter           │
│ (Desactive le port si │ (Empeche l'election    │ (Ignore/Bloque        │
│  un BPDU est reçu)    │  d'un faux Root)       │  l'envoi de BPDUs)    │
└───────────────────────┴────────────────────────┴───────────────────────┘
```

#### A. BPDU Guard
* **Principe :** S'applique sur les ports d'accès configurés avec `PortFast` (ports connectés aux hôtes finaux).
* **Action :** Si une trame BPDU est reçue sur le port, celui-ci passe immédiatement en état **err-disable** (port désactivé).

#### B. Root Guard
* **Principe :** S'applique sur les ports Trunk faisant face à des commutateurs sous administration tierce ou non totalement de confiance.
* **Action :** Empêche le commutateur voisin de devenir Root Bridge. Si un BPDU supérieur est reçu, le port passe en état *root-inconsistent* (le trafic utilisateur est bloqué sur ce port tant que le mauvais BPDU est émis).

---

## 2. Attaques par Saut de VLAN (VLAN Hopping)

Les attaques par saut de VLAN permettent à une machine appartenant à un VLAN (ex: VLAN 10 - Utilisateurs) d'envoyer des trames Ethernet vers un autre VLAN (ex: VLAN 20 - Serveurs) sans passer par un routeur ou un pare-feu.

---

### A. Double Tagging (Double Étiquetage 802.1Q)

Cette attaque exploite la fonctionnalité du **VLAN Natif** sur les liaisons Trunk.

```
                    MÉCANISME DU DOUBLE TAGGING

  [ Attaquant sur VLAN 10 (Natif) ]
  Trame envoyée : [ Tag Externe: VLAN 10 | Tag Interne: VLAN 20 | Données ]
         │
         ▼
  ┌───────────────┐
  │ Switch 1      │ ──> Supprime le Tag VLAN 10 (Car VLAN Natif = 10)
  └───────┬───────┘     Relaie la trame sur le Trunk 802.1Q avec SEULEMENT le Tag 20 !
          │
          ▼
  ┌───────────────┐
  │ Switch 2      │ ──> Voit le Tag VLAN 20 et transmet la trame au VLAN 20.
  └───────┬───────┘
          │
          ▼
  [ Serveur Cible (VLAN 20) ]  <── (Trame reçue sans passer par le Routeur !)
```

> **Remarque :** Cette attaque est **unidirectionnelle** (l'attaquant ne peut pas recevoir la réponse), mais elle permet de réaliser des attaques DoS ou d'envoyer des commandes malveillantes.

---

### B. Exploitation du Dynamic Trunking Protocol (DTP)

Par défaut, de nombreux switches tentent de négocier automatiquement un lien Trunk via le protocole DTP (`switchport mode dynamic auto` ou `dynamic desirable`). Un attaquant simule un switch et négocie un lien Trunk avec le port du commutateur. Il a alors accès à **tous les VLANs** véhiculés sur le réseau.

---

### Parades contre le VLAN Hopping

1. **Désactiver DTP :** Forcer tous les ports d'accès en mode access (`switchport mode access`) et désactiver la négociation Trunk (`switchport nonegotiate`).
2. **Isoler le VLAN Natif :** Utiliser un VLAN dédié (ex: VLAN 999) comme VLAN Natif pour tous les Trunks, et ne jamais assigner de port utilisateur à ce VLAN.
3. **Taguer le VLAN Natif :** Forcer le taggage du VLAN natif sur les trunks (`vlan dot1q tag native`).

---

## 3. IP Source Guard (IPSG)

### Le Problème
Même avec le DHCP Snooping et DAI activés, un attaquant peut configurer manuellement une adresse IP statique autorisée sur sa carte réseau et usurper le trafic IP d'un autre équipement (*IP Spoofing*).

---

### Le Fonctionnement d'IP Source Guard

**IP Source Guard** est une fonctionnalité de filtrage de niveau 2/3 appliquée sur les ports d'accès. Elle valide à la fois l'adresse MAC **et** l'adresse IP source des paquets entrants.

```
                 FONCTIONNEMENT DE IP SOURCE GUARD

 [ Paquet IP ] (IP Src: 192.168.1.50, MAC Src: 0011.2233.4455)
      │
      ▼ (Entrée sur Port F0/1)
┌──────────────────────────────┐
│ IP Source Guard              │ <── Vérification via Table DHCP Snooping Binding
└──────────────┬───────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
[ Match valide ]  [ Incohérence / IP Usurpée ]
      │                 │
      ▼                 ▼
  (Autorisé)        (PAQUET DROPPÉ AU NIVEAU MATÉRIEL)
```

IPSG crée automatiquement une **ACL d'entrée dynamique** (*Port ACL - PACL*) basée sur la table **DHCP Snooping Binding**.

---

## 4. Contrôle d'Accès Réseau : IEEE 802.1X et MAB

Au lieu de se baser uniquement sur les adresses MAC (facilement usurpables), l'architecture **IEEE 802.1X** impose une authentification stricte de l'utilisateur ou de la machine avant d'ouvrir le port du commutateur.

---

### Architecture 802.1X (Trois Rôles)

```
                     ARCHITECTURE ET PROTOCOLES 802.1X

 ┌──────────────┐          EAPOL           ┌──────────────┐          RADIUS          ┌──────────────┐
 │ Supplicant   │ <────────────────────> │ Authenticator│ <────────────────────> │ Auth Server  │
 │  (PC Client) │   (EAP over LAN / L2)  │ (Commutateur)│     (UDP/IP L3)        │ (RADIUS/ISE) │
 └──────────────┘                          └──────────────┘                          └──────────────┘
```

1. **Supplicant (Demandeur) :** Le logiciel client sur la machine utilisateur qui fournit les identifiants (Certificat X.509, Login/MDP).
2. **Authenticator (Authentificateur) :** Le commutateur L2 qui contrôle l'accès physique au réseau. Il bloque tout le trafic utilisateur non authentifié (sauf EAPOL, DHCP, et CDP/LLDP).
3. **Authentication Server (Serveur d'Authentification) :** Le serveur RADIUS (ex: Cisco ISE, FreeRADIUS, Microsoft NPS) qui valide les identifiants et renvoie la décision (Accept/Reject + attributs de VLAN/ACL).

---

### MAC Authentication Bypass (MAB)

Pour les équipements ne supportant pas de client 802.1X (ex: imprimantes IP, caméras de surveillance, téléphones IP) :

* Le switch attend l'expiration du délai d'attente 802.1X.
* Le switch extrait l'adresse MAC de l'équipement et l'envoie au serveur RADIUS dans un paquet d'authentification MAB.
* Le serveur RADIUS valide la présence de la MAC dans sa base de données d'équipements autorisés.

---

## 5. Configuration Avancée sur Cisco IOS-XE

Exemple de configuration complète intégrant les protections STP, la prévention du VLAN Hopping, IP Source Guard et 802.1X/MAB.

```
! ==========================================
! 1. SÉCURISATION GLOBALE DE STP
! ==========================================
spanning-tree portfast default
spanning-tree portfast bpduguard default

! ==========================================
! 2. PRÉVENTION DU VLAN HOPPING SUR LES TRUNKS
! ==========================================
interface GigabitEthernet1/0/48
 description ** TRUNK VERS SWITCH D'ACCES **
 switchport mode trunk
 switchport trunk native vlan 999
 switchport nonegotiate
 spanning-tree guard root

! ==========================================
! 3. CONFIGURATION D'UN PORT ACCÈS COMPLET (IPSG + 802.1X + MAB)
! ==========================================
interface FastEthernet0/10
 description ** PORT UTILISATEUR SECURISE **
 switchport mode access
 switchport access vlan 10
 switchport nonegotiate
 
 ! Activation d'IP Source Guard (Inspec IP et MAC)
 ip verify source port-security
 
 ! Activation des protections STP et Port-Security
 spanning-tree portfast
 spanning-tree bpduguard enable
 
 ! Configuration 802.1X / MAB avec fallback
 authentication port-control auto
 dot1x pae authenticator
 mab
```

---

## Synthèse des Vulnérabilités Avancées et Parades

| Attaque L2 | Vecteur d'Attaque | Mécanisme de Défense |
| :--- | :--- | :--- |
| **STP Spoofing** | Injection de BPDUs avec priorité 0 | **BPDU Guard** / **Root Guard** |
| **Double Tagging** | Exploitation du VLAN Natif non taggué | **VLAN Natif Dédié** / `vlan dot1q tag native` |
| **DTP Spoofing** | Négociation automatique de Trunk | `switchport mode access` / `switchport nonegotiate` |
| **IP Spoofing L2** | Usurpation d'IP statique sur le port | **IP Source Guard (IPSG)** |
| **Non-Auth Access** | Connexion d'un PC non autorisé sur un port libre | **IEEE 802.1X / MAB** |

---

## Points à Retenir

1. **BPDU Guard** protège les ports d'accès utilisateurs en coupant le port si un switch non autorisé y est branché.
2. **Root Guard** protège la topologie centrale du réseau contre la prise de contrôle du rôle de Root Bridge.
3. Le **Double Tagging** ne fonctionne que si l'attaquant est sur le même VLAN que le **VLAN Natif** du lien Trunk.
4. **IP Source Guard** crée un filtrage dynamique qui associe le port, l'adresse MAC et l'adresse IP en se basant sur le **DHCP Snooping**.
5. **802.1X** fournit un contrôle d'accès fondé sur l'identité (utilisateur/machine) et non plus sur de simples paramètres réseau.
```