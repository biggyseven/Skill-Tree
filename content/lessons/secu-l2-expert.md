# Sécurité de Couche 2 (Layer 2 Security) - Expert

**Niveau :** Expert

**Prérequis :** Sécurité de Couche 2 Intermédiaire (`secu-l2-intermediaire.md`), parfaite maîtrise de l'architecture PKI, de l'ingénierie des commutateurs Data Center (VXLAN, EVPN), du protocole 802.1X/RADIUS avancé, des mécanismes d'isolation L2 (PVLAN), et du chiffrement de niveau 2 (MACsec / 802.1AE).

Ce cours traite de la sécurité de niveau 2 sous l'angle de l'ingénierie avancée des infrastructures critiques et Data Centers. Nous aborderons le chiffrement d'infrastructure **MACsec (IEEE 802.1AE)**, l'isolation fine par **Private VLANs (PVLAN)**, les attaques sur les réseaux d'overlay (**VXLAN/EVPN Spoofing**) et le contournement/renforcement des architectures **802.1X/EAP-TLS**.

---

## 1. Chiffrement Point-à-Point de Couche 2 : MACsec (IEEE 802.1AE)

### Le Problème de Sécurité des Liens Physiques L2

Les communications L2 traditionnelles (y compris sur fibre optique louée ou liens inter-sites) transitent en clair. Un sous-traitant, un opérateur d'infrastructure ou un attaquant physique posant une sonde sur le câble (*Optical Tapping*) peut intercepter, rejouer ou altérer l'ensemble des trames (IPsec, VLAN tags, MPLS labels, etc.).

### Fonctionnement de MACsec (802.1AE)

Contrairement à IPsec qui opère en couche 3, **MACsec** chiffre l'intégralité du paquet Ethernet **au niveau matériel (ASIC)** juste au-dessus du préambule Ethernet, à une vitesse de ligne sans surcoût de latence (Line-rate encryption 100G/400G).

```
                      STRUCTURE D'UNE TRAME MACSEC

  Standard Ethernet Frame:
  ┌──────────┬──────────┬────────────┬─────────────────────────┬───────┐
  │ DMAC (6B)│ SMAC (6B)│ EtherType  │ Payload (IP, TCP, etc.) │ FCS   │
  └──────────┴──────────┴────────────┴─────────────────────────┴───────┘

  MACsec Encrypted Frame:
  ┌──────────┬──────────┬──────────────┬─────────────────────────┬───────┬───────┐
  │ DMAC (6B)│ SMAC (6B)│ SecTAG (16B) │ Payload Chiffré (AES)   │ ICV   │ FCS   │
  └──────────┴──────────┴──────────────┴─────────────────────────┴───────┴───────┘
                          │                                       │
                          └──── Authentifié & Chiffré ────────────┘
                                (Integrité Check Value : 16B)
```

#### Échange de clés MACsec (MKA - MACsec Key Agreement)

MACsec s'appuie sur le protocole **MKA** (utilisant EAPOL) pour négocier dynamiquement les clés de chiffrement de session (*Data Symmetric Keys* - SAK) basées sur :
* Des clés pré-partagées (**PSK / CAK** - Connectivity Association Key).
* Un contrôle d'accès dynamique via **802.1X / EAP-TLS**.

```
                   PROCESSUS MKA (MACsec Key Agreement)

  [ Switch A (Key Server) ]                               [ Switch B ]
             │                                                 │
             │ <────────────── Session EAP-TLS / PSK ────────> │
             │                 (Négociation CAK)               │
             │                                                 │
             │ ─── Génération et distribution sécurisée SAK ──>│
             │                                                 │
             │ <========== Trafic L2 Chiffré (AES-GCM) =======>│
```

---

## 2. Segmentations et Isolation Avancée : Private VLANs (PVLAN)

Dans un réseau de Data Center ou de DMZ, placer plusieurs serveurs ou machines virtuelles dans un même sous-réseau / VLAN traditionnel leur permet de communiquer directement en Layer 2. Un attaquant compromettant une seule machine peut réaliser un mouvement latéral immédiat vers toutes les autres.

Les **Private VLANs (PVLAN)** subdivisent un VLAN primaire en sous-VLANs secondaires pour restreindre cette communication intra-VLAN au niveau L2.

```
                   ARCHITECTURE DES PRIVATE VLANS (PVLAN)

                        [ Primary VLAN 100 ]
                                 │
           ┌─────────────────────┼─────────────────────┐
           ▼                     ▼                     ▼
   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
   │ Promiscuous   │     │ Isolated      │     │ Community     │
   │ Port (Router) │     │ VLAN 101      │     │ VLAN 102      │
   └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
           │                     │                     │
   (Accède à TOUT)       ┌───────┴───────┐     ┌───────┴───────┐
                         ▼               ▼     ▼               ▼
                       [VM 1]          [VM 2] [Web 1]        [Web 2]
                         │               │     └──────┬──────┘
                         └── (Bloqué) ───┘      (Communiquent entre eux)
```

### Types de Ports et VLANs PVLAN :

1. **Primary VLAN :** Le VLAN principal qui transporte le trafic du port Promiscuous vers tous les sous-VLANs secondaires.
2. **Promiscuous Port (Port Promiscuity) :** Généralement connecté au routeur ou pare-feu par défaut. Il peut communiquer avec **tous** les autres ports du PVLAN (Isolated, Community, et autres Promiscuous).
3. **Isolated VLAN / Ports :** Les équipements connectés à des ports isolés peuvent **uniquement** communiquer avec le port Promiscuous. Toute communication L2 directe entre deux ports isolés est complètement bloquée.
4. **Community VLAN / Ports :** Les équipements d'un même groupe "Community" peuvent communiquer entre eux et avec le port Promiscuous, mais sont isolés des autres groupes Community et des ports Isolated.

---

## 3. Sécurité dans les Réseaux Overlay (VXLAN & EVPN)

Dans les Data Centers modernes basés sur **VXLAN (Virtual Extensible LAN)** et **BGP EVPN**, le réseau de niveau 2 est encapsulé dans des paquets UDP/IP de niveau 3 sur un réseau sous-jacent (*Underlay*).

```
                  ENCAPSULATION VXLAN & COMPOSANTS SÉCURITÉ

  ┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
  │ IP Underlay  │ UDP (4789)   │ Header VXLAN │ Frame Ethernet│ FCS          │
  │ (Outer IP)   │ Header       │ (VNI 24 bits)│ Client (Inner)│              │
  └──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

### Vecteurs d'Attaques Spécifiques à VXLAN :

1. **VNI Injection / Spoofing :** Un attaquant injectant des paquets UDP sur le port 4789 du réseau Underlay peut injecter directement du trafic arbitraire dans n'importe quel VNI (VLAN virtuel) si le sous-réseau Underlay n'est pas authentifié.
2. **BGP EVPN Route Spoofing :** Injection de fausses annonces BGP type 2 (MAC/IP Route) ou type 5 (IP Prefix) visant à détourner des VTEP (*VXLAN Tunnel Endpoints*).
3. **VTEP Impersonation :** Usurpation de l'adresse IP d'un VTEP légitime pour intercepter ou rejouer le trafic inter-rack.

### Parades et Sécurisation Overlay :

* **Underlay Security :** Isoler le réseau routé Underlay dans un VRF/Routing Domain dédié non routable depuis les charges de travail (Workloads).
* **IPsec / MACsec inter-VTEP :** Chiffrer le trafic entre les commutateurs VTEP (Leafs) via IPsec ou MACsec sur les liaisons d'Interconnexion.
* **BGP GTSM (Generalized TTL Security Mechanism - RFC 5082) & MD5/Keychain :** Authentifier les sessions BGP EVPN et vérifier que le TTL des paquets BGP est strictement égal à 255 pour prévenir les injections distantes.

---

## 4. Attaques Avancées sur 802.1X et Contournements

Bien que 802.1X avec **EAP-TLS** représente le standard le plus solide, il existe des vecteurs de contournement et d'attaque au niveau L2 post-authentification.

### A. L2 Rogue Device Insertion / Hub Attack (Post-Authentication)

Une fois que le Supplicant légitime s'est authentifié via 802.1X sur un port, l'Authenticator (switch) passe le port en état `Authorized`. Si la sécurité physique ou matérielle du port n'est pas verrouillée :

```
                  ATTAQUE EN INSERTION POST-AUTHENTIFICATION

   [ PC Légitime (Supplicant) ]
              │
              ├── (S'authentifie avec succès via 802.1X EAP-TLS)
              ▼
    ┌──────────────────┐
    │  Tap / Switch L2 │ ─── [ Attaquant (Usurpe la MAC/IP du PC légitime) ]
    └─────────┬────────┘
              │ (Le port reste "Authorized" sur le switch)
              ▼
     [ Port Switch L2 ]
```

Analyse du contournement :
L'attaquant s'intercale physiquement (via un pont L2/Tap passif) et clone l'adresse MAC/IP du client certifié. Comme l'authentification 802.1X standard intervient uniquement à l'établissement du lien physique (Link-Up), le port reste ouvert.

### Parades Avancées :

1. **Combining 802.1X with MACsec :** L'authentification 802.1X dérive une clé dynamique SAK. Sans la clé de session issue d'EAP-TLS, l'attaquant ne peut ni lire ni injecter de trames sur le port.
2. **RadSec (RFC 6614) :** Sécurisation des échanges RADIUS entre l'Authenticator (Switch) et le serveur de politique (Cisco ISE/FreeRADIUS) via **TLS sur TCP/2083**, éliminant les risques d'usurpation de paquets RADIUS UDP sur le réseau d'administration.

---

## 5. Configuration Expert : Cisco NX-OS / IOS-XE (MACsec & PVLAN)

### A. Configuration MACsec MKA avec Clé Pré-partagée (Cisco IOS-XE)

```
! =================================================================
! 1. DEFINITION DE LA CLE DU DOMAINE DE SÉCURITÉ MACSEC (MKA)
! =================================================================
mka key-chain MACSEC_CHAIN macsec
 key 01
  cryptographic-algorithm aes-128-cmac
  key-string 0123456789ABCDEF0123456789ABCDEF

! =================================================================
! 2. DEFINITION DU PROFIL MACSEC
! =================================================================
mka policy MACSEC_POLICY
 macsec-cipher-suite gcm-aes-128
 replay-protection window-size 64

! =================================================================
! 3. APPLICATION SUR INTERFACE INTER-SWITCH (TRUNK)
! =================================================================
interface GigabitEthernet1/0/1
 description ** LINK INTER-SWITCH SECURISE MACSEC **
 macsec network-link
 macsec mka policy MACSEC_POLICY
 macsec key-chain MACSEC_CHAIN
 switchport mode trunk
```

### B. Configuration de Private VLANs (Cisco NX-OS / IOS-XE)

```
! =================================================================
! 1. CRÉATION DES VLANS SECONDAIRES ET PRIMAIRE
! =================================================================
vlan 101
 private-vlan isolated
 name PVLAN_DMZ_ISOLATED

vlan 102
 private-vlan community
 name PVLAN_DMZ_COMMUNITY_WEB

vlan 100
 private-vlan primary
 private-vlan association 101,102

! =================================================================
! 2. CONFIGURATION DE L'INTERFACE PROMISCUOUS (VERS LE FIREWALL)
! =================================================================
interface GigabitEthernet1/0/1
 description ** VERS ROUTEUR / FIREWALL (PROMISCUOUS) **
 switchport mode private-vlan promiscuous
 switchport private-vlan mapping 100 101,102

! =================================================================
! 3. CONFIGURATION D'UN PORT ISOLÉ ET COMMUNITY
! =================================================================
interface GigabitEthernet1/0/10
 description ** SERVEUR DMZ ISOLE **
 switchport mode private-vlan host
 switchport private-vlan host-association 100 101

interface GigabitEthernet1/0/11
 description ** SERVEUR WEB COMMUNITY 1 **
 switchport mode private-vlan host
 switchport private-vlan host-association 100 102
```

---

## Synthèse comparative des technologies Sécurité L2 Expert

| Technologie | Couche d'Action | Objectif de Sécurité | Impact Matériel / Performance |
| :--- | :--- | :--- | :--- |
| **MACsec (802.1AE)** | Layer 2 (Ethernet) | Confidentialité & Intégrité hop-by-hop | Nul (Chiffrement hardware ASIC Line-Rate) |
| **Private VLANs** | Layer 2 (VLANs) | Isolation zéro-trust intra-sous-réseau | Traitement standard dans le TCAM du Switch |
| **BGP GTSM / RadSec** | Layer 3/4 (Control Plane) | Protection du Plan de Contrôle (BGP/RADIUS) | Faible (Consommation CPU Control Plane) |
| **VXLAN IPsec/MACsec** | Overlay / Underlay | Authentification/Chiffrement des Tunnels DC | Dépend de la puce ASIC d'encapsulation VTEP |

---

## Points à Retenir

1. **MACsec (802.1AE) :** Est la seule protection Layer 2 offrant à la fois confidentialité, intégrité et anti-rejeu au niveau trame sans pénalité de latence.
2. **Private VLANs (PVLAN) :** Indispensables pour appliquer le principe de moindre privilège au sein d'un même sous-réseau IP (empilage de ports Isolated et Community).
3. **Sécurité Overlay (VXLAN) :** L'étanchéité des réseaux virtuels dépend de la protection rigoureuse du plan de contrôle Underlay (BGP EVPN GTSM, RadSec, chiffrement inter-VTEP).
4. **802.1X seul ne suffit pas :** L'association de **802.1X + MACsec** est impérative pour parer les attaques physiques d'insertion d'équipements pirates sur des ports autorisés.