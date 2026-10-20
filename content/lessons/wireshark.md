# Analyse de paquets avec Wireshark – Cours intensif (Niveau Senior Network Admin)

> **Objectif** : Maîtriser Wireshark comme outil de capture, d’analyse et de diagnostic sur des réseaux d’entreprise (Cisco, Linux, virtualisé).  
> **Pré‑requis** : Connaissances solides en TCP/IP, routage, commutation, sécurité, expérience avec les CLI Cisco/Unix et les concepts de capture (SPAN, RSPAN, ERSPAN, tcpdump).  

---

## 1️⃣ Introduction & périmètre du cours  

| Thème                     | Détails attendus                                                                 |
|---------------------------|-----------------------------------------------------------------------------------|
| Historique                | De **Ethereal** (2001) à **Wireshark** (2024) – licences, communauté, évolutions. |
| Architecture interne      | Capture (libpcap / WinPcap / npcap), décodage (dissectors), UI (Qt).            |
| Limites légales & éthiques| RGPD, consentement, usage en entreprise (politique de capture).                 |
| Alternatives              | tcpdump, tshark, ngrep, Zeek, SolarWinds, NetScout.                              |

> **Pourquoi Wireshark ?**  
> - Interface graphique riche, filtres puissants, support > 3000 protocoles, extensions Lua, décryptage TLS, intégration avec les outils Cisco (ERSPAN).  
> - Capacité à travailler en **offline** (fichiers .pcapng) et **online** (capture en temps réel).  

---

## 2️⃣ Installation & configuration de base  

| OS                | Commande d’installation (exemple)                                      | Remarque importante                                                                 |
|-------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| **Ubuntu 22.04**  | `sudo apt update && sudo apt install wireshark`                         | Ajouter l’utilisateur au groupe `wireshark` : `sudo usermod -aG wireshark $USER`.    |
| **CentOS 9**      | `sudo dnf install wireshark-qt`                                          | Activer `setcap` pour capture sans root : `sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap`. |
| **Windows 10/11**| Téléchargement MSI depuis <https://www.wireshark.org/download.html>    | Cocher “Install Npcap in WinPcap API-compatible Mode”.                              |
| **macOS**         | `brew install wireshark`                                                | Lancer `Wireshark` depuis `/Applications`.                                          |

### 2.1 Vérification du driver de capture  

```bash
# Linux – vérifier que dumpcap possède les capabilities
getcap $(which dumpcap)
# sortie attendue : /usr/bin/dumpcap = cap_net_raw,cap_net_admin=eip
```

### 2.2 Paramètres recommandés dans *Preferences*  

| Section               | Paramètre                         | Valeur recommandée                     |
|-----------------------|-----------------------------------|----------------------------------------|
| **Capture**           | “Promiscuous mode”                | **Activé** (sauf sur ports trunk).    |
| **Capture**           | “Buffer size”                     | 10 MiB (ou plus selon débit).          |
| **Appearance**        | “Coloring Rules”                  | Personnalisées (voir §5).              |
| **Protocols**         | “TCP” → “Relative sequence numbers”| **Activé** (facilite le suivi).        |
| **Protocols**         | “SSL” → “Pre‑Master‑Secret log filename” | Chemin du fichier (ex: `/tmp/sslkeylog.log`). |
| **Advanced**          | “gui.max_packet_size”             | 65535 (capture complète).              |

---

## 3️⃣ Principes fondamentaux de la capture  

### 3.1 Types de capture  

| Méthode            | Description                                               | Avantages                               | Inconvénients                          |
|--------------------|-----------------------------------------------------------|----------------------------------------|----------------------------------------|
| **Local (libpcap)**| Capture directe sur l’interface physique.                | Faible latence, pas d’équipement additionnel. | Risque de perte de paquets sur NIC saturée. |
| **SPAN / RSPAN**   | Port mirroring sur un switch Cisco.                       | Simple, aucun impact sur le trafic.    | Limité à 1 Gbps sur certains modèles, copie unidirectionnelle. |
| **ERSPAN**         | Encapsulation de la copie dans un tunnel GRE.            | Capture à distance, multi‑site.        | Nécessite configuration GRE, overhead. |
| **Remote Capture**| `tcpdump -i eth0 -w - | ssh user@host "cat > /tmp/remote.pcap"` | Pas d’accès physique au device.        | Dépend de la bande passante du lien de contrôle. |
| **Capture via VM** | `vmware`/`hyper‑v` port‑group promiscuous.                | Analyse du trafic inter‑VM.            | Nécessite droits d’hyperviseur.         |

### 3.2 Calcul du débit de capture  

```
Débit (Mbps) = (Taille moyenne d’un paquet * Nombre de paquets par seconde) / 1 000 000
```

Exemple : 1500 octets × 800 pps = 1 200 000 octets/s ≈ **9,6 Mbps**.  
> **Règle pratique** : réservez **2×** le débit max du lien pour le tampon (`Capture → Options → Buffer size`).  

### 3.3 Capture avec Wireshark (GUI)  

1. **Capture → Options**  
2. Sélectionner l’interface (ex : `eth0`, `ens192`, `Wi‑Fi`).  
3. Cocher **Capture packets in promiscuous mode**.  
4. Définir un **Capture filter** (BPF) – ex : `tcp port 80 and net 10.0.0.0/8`.  
5. Lancer **Start**.

---

## 4️⃣ Filtres : BPF vs Display  

### 4.1 Capture Filters (BPF)  

| Syntaxe | Exemple | Signification |
|---------|---------|----------------|
| `host 192.168.1.10` | Capture tout le trafic vers/depuis 192.168.1.10 | Adresse IPv4 |
| `net 10.0.0.0/8` | Tous les paquets du réseau 10.0.0.0/8 | Masque réseau |
| `port 443` | Traffic TCP/UDP sur le port 443 | Port unique |
| `tcp[tcpflags] & tcp-syn != 0` | Paquets SYN uniquement | Filtre bit‑wise |
| `ether src 00:0c:29:ab:cd:ef` | MAC source spécifique | Niveau L2 |
| `vlan 100` | Trafic VLAN ID 100 | 802.1Q |
| `udp and (dst port 53 or src port 53)` | DNS request/response | Combinaison logique |

> **Astuce** : Utiliser `tcpdump -d "<filtre>"` pour vérifier la syntaxe avant de lancer la capture.

### 4.2 Display Filters (Wireshark)  

| Opérateur | Exemple | Description |
|-----------|---------|-------------|
| `==`      | `ip.addr == 10.1.2.3` | Égalité |
| `!=`      | `tcp.flags.syn == 1` | Différence |
| `&&`      | `http && ip.src == 10.0.0.5` | ET logique |
| `||`      | `dns || dhcp` | OU logique |
| `contains`| `frame contains "GET"` | Recherche texte |
| `matches` | `http.user_agent matches "Chrome/[\d.]+"` | Regex PCRE |
| `!`       | `!arp` | Négation |
| `in`      | `ip.src in {10.0.0.0/24, 192.168.1.0/24}` | Appartenance à un set |

**Exemple complet** :  
```
tcp.flags.syn == 1 && ip.src == 10.10.10.2 && !(tcp.port == 22 || tcp.port == 23)
```
→ Tous les SYN initiés depuis 10.10.10.2, sauf vers SSH/Telnet.

---

## 5️⃣ Décodage avancé des protocoles  

### 5.1 TCP – suivi de flux (Follow TCP Stream)  

1. Sélectionner un paquet TCP.  
2. Clic droit → **Follow → TCP Stream**.  
3. Choisir **ASCII**, **Raw**, **C‑style** ou **JSON**.  

> **Utilité** : Reconstituer une session HTTP, SMTP, ou un échange de configuration telnet/SSH (si déchiffré).

### 5.2 Analyse des protocoles de routage  

| Protocole | Champ clé à observer | Astuce Wireshark |
|-----------|----------------------|------------------|
| **OSPF**  | `ospf.type`, `ospf.area.id`, `ospf.router.id` | Utiliser le filtre `ospf && ip.addr == <router-id>` |
| **BGP**   | `bgp.type`, `bgp.update.attribute` | Filtre `bgp && tcp.port == 179` |
| **EIGRP** | `eigrp.opcode`, `eigrp.as` | `eigrp && ip.dst == 224.0.0.10` |
| **IS‑IS** | `isis.lsp.id`, `isis.pdu.type` | `isis && eth.type == 0x83` |

#### Exemple : Détection d’un LSA‑type 3 (summary) non‑propagé  

```
ospf.type == 4 && !(ospf.area.id == 0.0.0.0)
```

### 5.3 Protocole de commutation (STP, RSTP, MSTP)  

- **Champ** : `stp.root.bridge.id`, `stp.port.id`, `stp.type`.  
- **Filtre** : `stp && eth.dst == 01:80:C2:00:00:00`.  

**Diagnostic** : Si plusieurs BPDUs différents sur le même segment → boucle potentielle.

### 5.4 Protocole de découverte (CDP / LLDP)  

| Protocole | Champ de vérif | Filtre |
|-----------|----------------|--------|
| **CDP**   | `cdp.device_id`, `cdp.port_id` | `cdp && cdp.device_id contains "SW1"` |
| **LLDP**  | `lldp.chassis.id`, `lldp.port.id` | `lldp && lldp.port.id == "Gi0/1"` |

### 5.5 Décryptage TLS (SSL)  

1. **Pré‑requis** : Exporter les *pre‑master secrets* depuis le client/serveur (ex : `export SSLKEYLOGFILE=/tmp/sslkeylog.log`).  
2. Dans Wireshark : **Edit → Preferences → Protocols → TLS → (Pre‑Master‑Secret log filename)** → `/tmp/sslkeylog.log`.  
3. Re‑ouvrir le fichier .pcap → les paquets TLS seront affichés en clair (HTTP, SMTP, etc.).  

> **Note** : Sous Windows, utilisez **Wireshark → Edit → Preferences → Protocols → TLS → RSA Keys List** pour ajouter les clés privées (format PEM).

---

## 6️⃣ Fonctionnalités avancées de Wireshark  

### 6.1 Graphiques I/O  

- **Statistiques → I/O Graph**  
- Ajouter des courbes : `tcp`, `udp`, `icmp`.  
- **Intervalle** : 0.01 s pour trafic haute fréquence, 1 s pour analyse globale.  

### 6.2 Statistiques de protocole  

| Menu | Description |
|------|-------------|
| **Statistics → Protocol Hierarchy** | Vue arborescente du volume par protocole. |
| **Statistics → Conversations** | Liste des flux (IP‑IP, TCP‑TCP, UDP‑UDP) avec octets, paquets, durée. |
| **Statistics → Endpoints** | Analyse par adresse MAC / IP / IPv6. |
| **Statistics → Flow Graph** | Diagramme séquentiel des échanges (SYN → ACK → FIN). |

### 6.3 Expert Info  

- **Analyse** : `Expert → Show` → Niveau *Warning*, *Error*, *Note*.  
- Utilisé pour repérer **retransmissions**, **duplicate ACKs**, **malformed packets**.  

### 6.4 Colonnes personnalisées  

1. **Edit → Preferences → Columns**  
2. Ajouter :  
   - **Field type** : `tcp.stream` (numéro de flux).  
   - **Field type** : `http.host` (nom d’hôte).  
   - **Field type** : `frame.time_relative` (temps depuis le premier paquet).  

### 6.5 Règles de coloration (Coloring Rules)  

| Couleur | Règle | Exemple de filtre |
|---------|-------|--------------------|
| **Rouge** | Retransmission TCP | `tcp.analysis.retransmission` |
| **Orange** | DNS error | `dns.flags.rcode != 0` |
| **Vert** | OSPF Hello | `ospf.type == 1` |
| **Bleu** | VLAN 100 | `vlan.id == 100` |
| **Violet** | TLS handshake | `ssl.record.version == 0x0303 && ssl.record.content_type == 22` |

> **Tip** : Exporter/importer les règles via **View → Coloring Rules → Export** pour les partager entre équipes.

### 6.6 Scripts Lua (extensions)  

```lua
-- simple plugin qui compte les paquets HTTP GET par seconde
do
    local tap = Listener.new("http")
    local stats = {}
    function tap.packet(pinfo,tvb)
        local ts = tostring(pinfo.abs_ts):sub(1,19)   -- seconde
        stats[ts] = (stats[ts] or 0) + 1
    end
    function tap.draw()
        for t,c in pairs(stats) do
            print(t .. " => " .. c .. " GET")
        end
    end
end
```

- Placer le script dans `$HOME/.local/lib/wireshark/plugins/` (Linux) ou `%APPDATA%\Wireshark\plugins\`.  
- Redémarrer Wireshark → **Tools → Lua Plugins**.

---

## 7️⃣ Capture à distance & intégration Cisco  

### 7.1 Configuration SPAN (local)  

```cisco
! Sur le switch NEXUS ou Catalyst
monitor session 1 source interface Ethernet1/1 both
monitor session 1 destination interface Ethernet1/24
no shutdown
```

### 7.2 RSPAN (Remote SPAN) – VLAN de transport  

```cisco
! Création du VLAN RSPAN 999
vlan 999
  name RSPAN_TRANSPORT
  remote-span
exit

! Session RSPAN
monitor session 2 source interface Ethernet1/2 both
monitor session 2 destination remote vlan 999
exit

! Sur le switch récepteur
interface Ethernet1/48
  switchport mode trunk
  switchport trunk allowed vlan add 999
exit

monitor session 3 source remote vlan 999 both
monitor session 3 destination interface Ethernet1/48
```

### 7.3 ERSPAN (GRE tunnel) – capture à 10 Gbps+  

```cisco
! Source switch
interface Ethernet1/3
  ip address 10.10.10.1 255.255.255.0
  no shutdown
exit

monitor session 10 type erspan-source
  source interface Ethernet1/3 both
  destination ip 192.0.2.10
  erspan-id 100
  ttl 255
exit
```

Sur le serveur de capture (Linux) :

```bash
# Crée un tunnel GRE et capture le trafic encapsulé
sudo ip tunnel add erspan0 mode gre remote 192.0.2.10 local 10.10.10.1 ttl 255
sudo ip link set erspan0 up
sudo tcpdump -i erspan0 -w /tmp/erspan_capture.pcapng
```

### 7.4 Capture via `dumpcap` (CLI) – équivalent à Wireshark  

```bash
# Capture 30 s sur eth0, filtre BPF, écriture en pcapng
sudo dumpcap -i eth0 -f "tcp port 22" -a duration:30 -w /tmp/ssh_capture.pcapng
```

> **Note** : `dumpcap` utilise le même moteur de décodage que Wireshark → même affichage lorsqu’on ouvre le fichier.

---

## 8. Table comparative des outils de capture

| Outil | Interface | Capture temps réel | Filtrage BPF | Décodage protocoles | Licence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wireshark** | GUI + CLI (`tshark`) | ✅ | ✅ | > 3000 | GPL |
| **tcpdump** | CLI uniquement | ✅ | ✅ | Basique | BSD |
| **tshark** | CLI de Wireshark | ✅ | ✅ | > 3000 | GPL |
| **Tcpdump** (Windows) | CLI (WinPcap) | ✅ | ✅ | Basique | BSD |

## 9. Atelier de dépannage : Analyser une perte de paquets

**Scénario :** Un utilisateur se plaint que son transfert de fichier est lent sur le réseau local.

**Étapes d'analyse avec Wireshark :**
1. **Capture** : Lancez une capture sur l'interface du serveur (ou du client) avec le filtre de capture `host 192.168.1.100`.
2. **Filtrage d'affichage** : Utilisez `tcp.analysis.flags` pour voir les erreurs TCP (retransmissions, dup ACKs, fenêtre zéro).
3. **Analyse** : Si vous voyez beaucoup de "TCP Retransmission", cela indique une perte de paquets sur le réseau.
4. **Vérification** : Utilisez `tcp.analysis.ack_rtt` pour voir le temps de réponse.
5. **Conclusion** : Si les retransmissions sont fréquentes sur le LAN, cela peut être dû à un câble défectueux, un port de switch en half-duplex, ou une boucle L2.

**Commande alternative (CLI) :**
`tshark -i eth0 -Y "tcp.analysis.flags" -T fields -e ip.src -e ip.dst -e tcp.analysis.flags`