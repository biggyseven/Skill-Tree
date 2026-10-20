# Cours Intensif – VPN WireGuard  
**Niveau : Administrateur Réseau Senior (CCIE)**  
**Durée estimée : 2 jours (12 h)**  

---

## Table des matières
| # | Section |
|---|---------|
| 1 | Introduction & Historique |
| 2 | Architecture & Modèle de Paquet |
| 3 | Cryptographie sous‑jacent |
| 4 | Processus d’établissement de tunnel (Handshake) |
| 5 | Installation & Configuration Linux (kernel & userspace) |
| 6 | Intégration Cisco (IOS, IOS‑XR, NX‑OS, Meraki) |
| 7 | Comparaison WireGuard vs IPsec / OpenVPN |
| 8 | Optimisation & Sécurité (Hardening) |
| 9 | Atelier pratique – Déploiement d’un site‑to‑site |
|10 | Laboratoire de dépannage avancé |
|11 | Bonnes pratiques, monitoring & automatisation |
|12 | Références & ressources complémentaires |

---

## 1️⃣ Introduction & Historique
- **Créateur** : Jason A. Donenfeld (2016) – initialement pour le projet **Noise Protocol Framework**.  
- **Première inclusion dans le kernel Linux** : 5.6 (février 2020).  
- **Statut** : Projet Open‑Source sous licence GPL‑2.0, maintenu par la communauté et par **Edge Security**.  
- **Objectif principal** : Fournir un VPN simple, ultra‑rapide, avec un code base minimal (~4 kLoC) pour faciliter l’audit de sécurité.  

---

## 2️⃣ Architecture & Modèle de Paquet

### 2.1 Diagramme logique (ASCII)

```
+-------------------+        +-------------------+        +-------------------+
|   Client A (WG0)  | <----> |   Router/Peer B   | <----> |   Server C (WG0)  |
|  privkey: A_priv  |        |  privkey: B_priv  |        |  privkey: C_priv  |
|  pubkey:  A_pub   |        |  pubkey:  B_pub   |        |  pubkey:  C_pub   |
+-------------------+        +-------------------+        +-------------------+

            |                               |
            |   UDP 51820 (or custom)       |
            +-------------------------------+
```

### 2.2 Modèle de paquet WireGuard
| Champ | Taille | Description |
|------|--------|-------------|
| **Header** | 4 octets | `type` (0 = data, 1 = handshake) + `reserved` |
| **Message** | 0‑65535 octets | Payload chiffré (AEAD) |
| **AEAD** | 16 octets | Tag d’authentification (ChaCha20‑Poly1305 ou AES‑GCM) |
| **Message Counter** | 8 octets | Anti‑replay, monotone per peer |

- **Encapsulation** : Aucun tunnel IP supplémentaire. Le paquet WG est directement encapsulé dans UDP (ou TCP via `wireguard-go` si besoin).  
- **MTU recommandée** : 1420 bytes (pour éviter la fragmentation sur Internet).  

---

## 3️⃣ Cryptographie sous‑jacent

| Algorithme | Utilisation | Taille clé | Performances (cycles/byte) |
|------------|-------------|------------|----------------------------|
| **ChaCha20‑Poly1305** | Chiffrement + Authentification (AEAD) | 256 bits | ~1.5 × plus rapide que AES‑GCM sur ARM |
| **Curve25519 (X25519)** | Échange de clés (Diffie‑Hellman) | 256 bits | 3 × plus rapide que NIST P‑256 |
| **BLAKE2s** | Hachage (KDF, MAC) | 256 bits | 2 × plus rapide que SHA‑2 |
| **Noise_IK** (modèle) | Handshake (static‑static + static‑ephemeral) | — | — |

### 3.1 Pourquoi ces choix ?
- **Résistance aux side‑channel** : Curve25519 et ChaCha20 sont conçus pour être **constant‑time**.  
- **Performance sur CPU modernes** : ChaCha20 exploite les instructions SIMD (ARM NEON, x86 AVX2).  
- **Simplicité d’audit** : Moins de code = surface d’attaque réduite.  

---

## 4️⃣ Processus d’établissement de tunnel (Handshake)

WireGuard utilise le **Noise_IK** pattern :

```
A (initiateur)                         B (répondeur)
--------------------------------------------------------------
A → B :  Initiation
   - Ephemeral key (eA)
   - Static public key (A_pub)
   - Encrypted payload (timestamp, MAC1, MAC2)

B → A :  Response
   - Ephemeral key (eB)
   - Encrypted payload (timestamp, MAC1, MAC2)
```

### 4.1 Étapes détaillées

| Étape | Action | Crypto |
|------|--------|--------|
| 1 | A génère `eA` (Curve25519) et chiffre le message avec la clé pré‑partagée `K_psk` (optionnelle) | ChaCha20‑Poly1305 |
| 2 | B déchiffre, vérifie le timestamp (anti‑replay) et calcule le secret partagé `DH(eA, B_priv)` | X25519 |
| 3 | B répond avec `eB` et chiffre le payload avec le secret dérivé (`K1 = KDF(DH(eA, B_priv) || DH(A_pub, B_priv) || DH(eA, eB))`) | BLAKE2s |
| 4 | A déchiffre, calcule le même secret partagé, établit les clés de transport (`K_tx`, `K_rx`) | BLAKE2s |
| 5 | Les deux pairs passent en **mode transport** – échange de paquets de données chiffrés. |

> **Note** : Le handshake est **stateless** côté serveur – chaque paquet d’initiation peut être traité indépendamment, ce qui rend le protocole résilient aux attaques DoS de type SYN‑flood.

---

## 5️⃣ Installation & Configuration Linux

### 5.1 Prérequis
| OS | Version minimale | Package |
|----|------------------|---------|
| Debian/Ubuntu | 20.04 | `wireguard` (inclut `wg` et `wg-quick`) |
| RHEL/CentOS | 8 | `elrepo` → `kmod-wireguard` + `wireguard-tools` |
| Arch Linux | rolling | `wireguard-tools` |
| Alpine | 3.13 | `wireguard-tools` (musl) |

### 5.2 Installation (exemple Ubuntu 22.04)

```bash
sudo apt update
sudo apt install -y wireguard wireguard-tools
# Vérifier la présence du module kernel
sudo modprobe wireguard
lsmod | grep wireguard
```

### 5.3 Génération des clés

```bash
# Sur chaque nœud
wg genkey | tee privatekey | wg pubkey > publickey
# Optionnel : générer une clé pré‑partagée (PSK)
wg genpsk > psk
```

### 5.4 Fichier de configuration `wg0.conf`

```ini
[Interface]
# Adresse IP du tunnel (IPv4 + IPv6)
Address = 10.10.10.1/24, fd86:ea04:1111::1/64
# Port d’écoute UDP (par défaut 51820)
ListenPort = 51820
# Clé privée du serveur
PrivateKey = <C_private>

# Options de performance
# MTU recommandé
MTU = 1420
# Persistant keepalive (pour NAT traversal)
PostUp = sysctl -w net.ipv4.ip_forward=1
PostDown = sysctl -w net.ipv4.ip_forward=0

[Peer]
# Peer B (client)
PublicKey = <B_public>
PresharedKey = <psk>          # optionnel
AllowedIPs = 10.10.10.2/32, fd86:ea04:1111::2/128
Endpoint = 203.0.113.2:51820
PersistentKeepalive = 25
```

### 5.5 Activation du tunnel

```bash
# Démarrer via systemd
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0

# Vérifier l’état
sudo wg show
```

### 5.6 Routage & Firewall

```bash
# Autoriser le trafic UDP 51820 dans iptables / nftables
sudo iptables -A INPUT -p udp --dport 51820 -j ACCEPT
sudo iptables -A FORWARD -i wg0 -j ACCEPT
sudo iptables -A FORWARD -o wg0 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

> **Astuce** : Sur les distributions basées sur `firewalld`, utilisez `firewall-cmd --add-service=wireguard` (service custom) ou créez une zone dédiée.

---

## 6️⃣ Intégration Cisco

### 6.1 Pourquoi Cisco ne supporte‑t‑il pas encore WireGuard nativement ?
- **Roadmap** : Cisco privilégie IPsec/IKEv2 pour les déploiements d’entreprise.  
- **Open‑source** : WireGuard est sous licence GPL‑2, ce qui complique l’intégration dans le code propriétaire Cisco.  

### 6.2 Solutions de contournement

| Méthode | Description | Avantages | Inconvénients |
|--------|-------------|-----------|---------------|
| **Edge‑router Linux (vEdge)** | Déployer WireGuard sur un routeur Linux en front‑end, puis le connecter à un routeur Cisco via BGP/OSPF. | Flexibilité, performance native kernel. | Complexité d’orchestration. |
| **MPLS‑over‑WireGuard** | Encapsuler le trafic MPLS dans WG pour inter‑site, puis le décapsuler côté Cisco. | Sécurité renforcée pour le back‑bone. | Nécessite un dispositif de décapsulation (Linux ou VM). |
| **VMware NSX‑T + WireGuard** | Utiliser NSX‑T comme VNF WireGuard, puis le relier aux routeurs Cisco via tunnels IPsec existants. | Intégration SD‑WAN. | Coût de licence. |
| **Cisco Meraki + WireGuard** | Meraki ne supporte pas WG, mais on peut placer un **Ubiquiti EdgeRouter** en mode bridge devant le concentrateur Meraki. | Déploiement simple pour PME. | Pas de visibilité centralisée Meraki. |

### 6.3 Exemple : Router Cisco ISR + Edge‑router Linux

```
[Client Cisco ISR]---(IPsec)---[Linux Edge Router (WireGuard)]---(WireGuard)---[Linux Edge Router (Remote)]---(IPsec)---[Server Cisco ASR]
```

#### 6.3.1 Configuration IPsec sur ISR (exemple)

```cisco
crypto ikev2 proposal IKEV2_PROPOSAL
  encryption aes-gcm-256
  integrity sha256
  group 21
!
crypto ikev2 policy IKEV2_POLICY
  proposal IKEV2_PROPOSAL
!
crypto ikev2 keyring KEYRING
  peer EDGE_ROUTER
    address 198.51.100.10
    pre-shared-key cisco123
!
crypto ipsec transform-set TS esp-aes-gcm 256
  mode tunnel
!
crypto ipsec profile IPSEC_PROFILE
  set transform-set TS
  set ikev2-profile IKEV2_PROFILE
!
interface GigabitEthernet0/0/0
  ip address 198.51.100.1 255.255.255.0
  tunnel source GigabitEthernet0/0/0
  tunnel destination 198.51.100.10
  tunnel mode ipsec ipv4
  tunnel protection ipsec profile IPSEC_PROFILE
```

#### 6.3.2 Routeur Linux – WireGuard (exemple simplifié)

```bash
# Interface wg0 (site A)
cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
Address = 10.255.0.1/24
PrivateKey = <A_priv>
ListenPort = 51820

[Peer]
PublicKey = <B_pub>
AllowedIPs = 10.255.0.2/32
Endpoint = 203.0.113.2:51820
PersistentKeepalive = 25
EOF

systemctl restart wg-quick@wg0
```

#### 6.3.3 Redistribution BGP

```bash
# Sur le routeur Cisco
router bgp 65001
  neighbor 10.255.0.2 remote-as 65002
  network 10.10.0.0 mask 255.255.0.0
```

---

## 7️⃣ Comparaison WireGuard vs IPsec / OpenVPN

| Critère | **WireGuard** | **IPsec (IKEv2)** | **OpenVPN (UDP)** |
|---------|---------------|-------------------|-------------------|
| **Code base** | ~4 kLoC (kernel) | > 100 kLoC (strongSwan, libreswan) | > 200 kLoC |
| **Performance** | 1.2 × plus rapide que IPsec sur x86_64 (benchmarks 2023) | Dépend du chiffrement (AES‑GCM) | 0.7 × plus lent (TLS overhead) |
| **Latence** | 0.5 ms supplémentaire (handshake 1‑round‑trip) | 2‑3 ms (2‑round‑trip IKE) | 1‑2 ms (TLS) |
| **Sécurité** | Audité, primitives modernes, no‑crypto‑policy | Mature, mais configuration complexe (SA, PFS) | Dépend de TLS version, plus surface d’attaque |
| **NAT Traversal** | Keepalive 25 s, UDP only | NAT‑T + ESP/UDP encapsulation | UDP/TCP, nécessite `--float` |
| **Scalabilité** | 10 k+ peers par serveur (limité par CPU) | 1 k+ peers (SA table) | 500+ peers (TLS handshake cost) |
| **Complexité de config** | 1‑2 files | Plusieurs scripts, politiques | 1 file + scripts |
| **Support matériel** | Kernels + `wireguard-go` (ARM, x86) | ASIC/TPU (Cisco ASA, Juniper) | Aucun (software only) |
| **Interopérabilité** | Linux, Windows, macOS, iOS, Android, FreeBSD | Tous les équipements réseau d’entreprise | Large, mais nécessite client OpenVPN |

> **Conclusion** : WireGuard est idéal pour les **déploiements cloud‑native**, les **SD‑WAN** légers et les **micro‑services**. IPsec reste le choix privilégié pour les **environnements multi‑vendor** avec exigences de conformité (FIPS, PCI‑DSS). OpenVPN demeure une solution de transition ou de fallback.

---

## 8️⃣ Optimisation & Sécurité (Hardening)

| Action | Commande | Impact |
|--------|----------|--------|
| **Activer le BPF JIT** (réduction du CPU) | `sysctl -w net.core.bpf_jit_enable=1` | +10 % de débit |
| **Limiter le MTU** | `ip link set dev wg0 mtu 1420` | Évite la fragmentation |
| **Désactiver les algos non‑utilisés** | `modprobe -r wireguard` + `modprobe wireguard` (rebuild) | Réduit la surface d’attaque |
| **Utiliser une PSK** | `PresharedKey = <psk>` dans le `.conf` | Protection contre les attaques de type **key‑replay** |
| **Isolation SELinux/AppArmor** | `setsebool -P wireguard_can_network 1` | Confinement du processus `wg-quick` |
| **Monitoring** | `watch -n 1 wg show` ou `systemd-cgtop` | Visibilité temps réel |
| **Log de handshake** | `sudo journalctl -u wg-quick@wg0 -f` | Détection d’anomalies |

### 8.1 Paramètres sysctl recommandés

```bash
# Enable forwarding
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1

# Reduce UDP buffer fragmentation
net.core.rmem_max = 2500000
net.core.wmem_max = 2500000

# BPF JIT (Linux ≥ 4.12)
net.core.bpf_jit_enable = 1
```

---

## 9️⃣ Atelier pratique – Déploiement d’un site‑to‑site WireGuard

###