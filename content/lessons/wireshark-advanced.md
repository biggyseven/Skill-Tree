# Cours Intensif : Analyse Wireshark Avancée (Niveau CCIE / Senior NetAdmin)

## 1. Introduction & Philosophie de l'Analyse Expert

L'analyse de paquets n'est pas une simple inspection visuelle ; c'est une **science forensique réseau**. Au niveau CCIE, nous ne cherchons pas "ce qui ne va pas", nous validons des hypothèses basées sur le modèle OSI/TCP-IP et les RFCs. La maîtrise de Wireshark repose sur trois piliers :
1.  **Capture stratégique** : Placement, filtres de capture (BPF), ring buffers, décryptage TLS.
2.  **Analyse contextuelle** : Flux TCP, fenêtres glissantes, retransmissions, latence applicative vs réseau.
3.  **Automatisation & Scripting** : TShark, Lua, Python (pyshark), profils personnalisés.

---

## 2. Architecture de Capture & Placement Stratégique (TAP vs SPAN)

Le placement détermine la vérité terrain. Un mauvais placement = des données biaisées (perte de paquets, timestamps décalés, absence de trafic unidirectionnel).

### Tableau Comparatif : Méthodes d'Accès au Trafic

| Critère | **Network TAP (Test Access Point)** | **SPAN / RSPAN / ERSPAN (Port Mirroring)** | **Capture sur Host (Local)** |
| :--- | :--- | :--- | :--- |
| **Intégrité Trame** | **Parfaite** (Couche 1/2 passive, pas de FCS stripping forcé) | Risque de suppression FCS, tags VLAN modifiés, trames malformées non miroirées | Dépend driver/OS (Checksum Offload, LRO/GRO) |
| **Bidirectionnel** | **Garanti** (Ports A->B & B->A distincts ou agrégés) | Dépend config (ingress/egress/both). Risque oversubscription. | Unidirectionnel par interface (besoin 2 captures pour full-duplex) |
| **Latence/Jitter** | Nul (Passif) | Non-nul (Traitement CPU ASIC/CPU Switch) | N/A (Local) |
| **Capacité Bande Passante** | Ligne rate (ex: 10G/40G/100G dedicated) | Limité par bande passante port destination + CPU Switch | Limité par CPU/Disque/Bus PCIe Host |
| **VLAN Tagging** | Préservé (QinQ, 802.1Q natif) | Souvent strippé ou réécrit selon config `encapsulation replicate` | Invisible (stripped par driver NIC) |
| **Coût / Complexité** | Élevé (Hardware dédié, rack space) | Gratuit (Licence IOS/NX-OS), Config CLI simple | Gratuit, Installation logicielle simple |
| **Cas d'usage CCIE** | **Production Critique, Litige, SLA, VoIP, FCoE** | **Troubleshooting ponctuel, Lab, Accès distant (ERSPAN)** | **Debug Applicatif, Dev, Malware Analysis, TLS Decrypt** |

### Configuration Cisco SPAN/ERSPAN Best Practices (IOS-XE / NX-OS)

```cisco
! ---------- IOS-XE (Catalyst 9xxx) - Session Locale SPAN ----------
monitor session 1 source interface GigabitEthernet1/0/1 both
monitor session 1 source interface GigabitEthernet1/0/2 rx          ! Ingress only
monitor session 1 destination interface GigabitEthernet1/0/24 encapsulation replicate
! 'encapsulation replicate' PRESERVE le tag 802.1Q original (CRITIQUE pour VLAN analysis)
monitor session 1 filter vlan 10, 20, 100-200                       ! Filtrage VLAN en amont (ASIC)
monitor session 1 type local

! ---------- NX-OS (Nexus 9xxx) - ERSPAN Source (Type III - Header GRE + ERSPAN ID) ----------
monitor session 10 type erspan-source
  description "ERSPAN vers Collector 10.1.1.50"
  source interface Ethernet1/1-10 both
  source vlan 10, 20, 100
  filter vlan 30, 40                    ! Exclusion VLAN mgmt
  destination ip 10.1.1.50
  erspan-id 100                         ! ID unique pour le collector
  mtu 9000                              ! Jumbo frames pour éviter fragmentation ERSPAN
  origin ip 10.1.1.1                    ! IP source ERSPAN (Loopback)
  no shut

! ---------- Linux (tcpdump) - Capture sur Host pour analyse locale ----------
# Capture "Full Packet" (snaplen 262144), pas de résolution DNS (-n), timestamp haute résolution (-tttttt)
# -i any capture toutes interfaces (pseudo-device), -w écriture binaire
sudo tcpdump -i any -s 262144 -nn -tttttt -w /data/captures/capture_$(date +%F_%H-%M).pcapng \
  not port 22 and not host 192.168.1.100 and \( tcp or udp or icmp \)

# Utilisation de 'ring buffer' (fichiers de 100Mo, max 50 fichiers) pour capture longue durée
sudo tcpdump -i eth0 -s 0 -nn -C 100 -W 50 -w /data/captures/ring_buffer.pcap
```

### Schéma ASCII : Topologie de Capture Idéale (Datacenter)

```text
       +------------------+          10G/40G/100G          +------------------+
       |  Core Switch A   |<-------------------------------->|  Core Switch B   |
       |  (Nexus 9500)    |           Fabric Path          |  (Nexus 9500)    |
       +--------+---------+                                  +--------+---------+
                |                                                    |
                |  TAP Passif (Optique LC/MPO)                       |  TAP Passif
                |  (Aggregation A->B & B->A)                         |  (Aggregation)
                v                                                    v
       +--------+---------+                                  +--------+---------+
       |   Network Packet |                                  |   Network Packet |
       |   Broker (NPB)   |<------ 10G/40G Tool Ports ------>|   Broker (NPB)   |
       |  (Gigamon/Keysight|     Load Balancing / Filtering   |  (Gigamon/...)   |
       |   cPacket)       |                                  |                  |
       +--------+---------+                                  +--------+---------+
                |                                                    |
                |  Tool Ports (Filtered/Decapsulated)                |
                v                                                    v
       +--------+---------+                                  +--------+---------+
       |  Sensor IDS/IPS  |                                  |  Wireshark Probe |
       |  (Suricata/Zeek) |                                  |  (Linux + n2disk)|
       +------------------+                                  +------------------+
                |                                                    |
                +------------------+---------------------------------+
                                   |
                          +--------v--------+
                          |  Centralized    |
                          |  Packet Store   |
                          |  (PCAP Repository|
                          |   + Elastic/    |
                          |   OpenSearch)   |
                          +-----------------+
```

---

## 3. Configuration Avancée Wireshark : Profils, Colonnes & Préférences

Un Senior Admin ne travaille **jamais** avec le profil "Default". Créez des profils par cas d'usage.

### 3.1 Création de Profils Spécialisés (Fichier `profiles`)

Emplacement : `%APPDATA%\Wireshark\profiles\` (Windows) ou `~/.config/wireshark/profiles/` (Linux).

**Profil "Troubleshooting_TCP" (Focus Performance) :**
*   **Colonnes personnalisées** (Clique droit sur en-tête -> Column Preferences) :
    | Titre Colonne | Type | Champs / Expression | Description |
    | :--- | :--- | :--- | :--- |
    | `Time` | Time (Format: `Seconds since beginning of capture`) | `frame.time_relative` | Temps relatif début capture. |
    | `Delta` | Time (Format: `Seconds since previous displayed packet`) | `frame.time_delta_displayed` | **Critique** : Intervalle entre paquets *affichés* (après filtre). |
    | `Abs Time` | Time (Format: `Date and Time of Day`) | `frame.time` | Timestamp absolu pour corrélation logs. |
    | `Src` | Custom | `ip.src` | IP Source. |
    | `Dst` | Custom | `ip.dst` | IP Destination. |
    | `Port` | Custom | `tcp.port` | Port TCP (src ou dst). |
    | `Seq/Win` | Custom | `tcp.seq` / `tcp.window_size_value` | **Concaténation** : `tcp.seq || " / Win=" || tcp.window_size_value * tcp.window_size_scalefactor` (Nécessite champ calculé Lua ou affichage manuel). |
    | `Flags` | Custom | `tcp.flags.str` | Représentation textuelle flags (SYN, ACK, PSH, RST, FIN, URG, ECE, CWR). |
    | `Retrans` | Custom | `tcp.analysis.retransmission` | Affiche "Retransmission" / "Fast Retransmission" / "Out-of-Order". |
    | `SACK` | Custom | `tcp.option.sack_le` | Blocs SACK (Left Edge). |
    | `RTT` | Custom | `tcp.analysis.ack_rtt` | RTT calculé par Wireshark (SYN/ACK -> ACK ou Data -> ACK). |

*   **Coloring Rules** (View -> Coloring Rules) - Ordre de priorité descendant :
    1.  `tcp.analysis.retransmission || tcp.analysis.fast_retransmission || tcp.analysis.out_of_order` -> **Red / White** (Critique)
    2.  `tcp.analysis.zero_window || tcp.analysis.window_full` -> **Orange / Black** (Flow Control)
    3.  `tcp.analysis.keep_alive || tcp.analysis.keep_alive_ack` -> **Gray / White** (Bruit)
    4.  `tcp.flags.syn == 1 && tcp.flags.ack == 0` -> **Green / Black** (New Connection)
    5.  `tcp.flags.reset == 1` -> **Red / Yellow** (Abort)
    6.  `icmp.type == 3` -> **Yellow / Black** (Dest Unreach - MTU/Blackhole)

*   **Préférences Protocoles Clés (Edit -> Preferences -> Protocols) :**
    *   **TCP** : `Track TCP streams` (ON), `Relative sequence numbers` (OFF pour debug absolu), `Calculate conversation timestamps` (ON), `Validate TCP checksum` (OFF si Offload NIC), `Analyze TCP sequence numbers` (ON).
    *   **IPv4/IPv6** : `Validate checksum` (OFF si Offload).
    *   **QUIC/HTTP3** : `Try to decrypt QUIC` (ON + Key Log File path).
    *   **TLS** : `(Pre)-Master-Secret log filename` : `/path/to/sslkeys.log` (Variable d'env `SSLKEYLOGFILE`).

### 3.2 Fichier de Configuration `preferences` (Extrait critique)

```text
# ~/.config/wireshark/preferences (ou %APPDATA%\Wireshark\preferences)
gui.column.format: "Time", "%t", "Delta", "%Cus:frame.time_delta_displayed", "Src", "%s", "Dst", "%d", "Proto", "%p", "Len", "%L", "Info", "%i"
tcp.relative_sequence_numbers: FALSE
tcp.calculate_timestamps: TRUE
tcp.analyze_sequence: TRUE
tcp.check_checksum: FALSE
ip.check_checksum: FALSE
udp.check_checksum: FALSE
ssl.keylog_file: "/home/netadmin/sslkeys.log"
gui.packet_list_font: "Monospace,10,-1,5,50,0,0,0,0,0"
gui.tree_font: "Monospace,10,-1,5,50,0,0,0,0,0"
```

---

## 4. Maîtrise des Filtres : Display Filters (Wireshark) vs Capture Filters (BPF)

### 4.1 Syntaxe BPF (Capture Filter - `tcpdump` / Wireshark Capture Options)
*   S'exécute dans le noyau (kernel) / libpcap. **Performance maximale.**
*   Syntaxe limitée : `host`, `net`, `port`, `proto`, `and`, `or`, `not`, `()`, `direction` (src/dst).

```bash
# Capture UNIQUEMENT trafic TCP port 443 VERS serveur 10.10.10.50, sans SSH, avec VLAN 100
tcp port 443 and dst host 10.10.10.50 and not port 22 and vlan 100

# Capture trafic entre deux sous-réseaux (RFC1918), fragments IP inclus
net 10.0.0.0/8 and net 192.168.0.0/16 and (ip[6:2] & 0x1fff != 0 or ip[6] & 0x20 != 0)

# Capture ICMPv6 Neighbor Solicitation/Advertisement (NDP) seulement
icmp6 and (ip6[40] == 135 or ip6[40] == 136)
```

### 4.2 Filtres d'Affichage Avancés (Display Filters - Moteur Wireshark)
*   S'exécute en user-space sur le paquet déjà capturé. **Puissance expressive maximale.**
*   Opérateurs de comparaison : `==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`, `matches` (PCRE), `in` (set membership).
*   Opérateurs logiques : `&&`, `||`, `!`, `^^` (XOR).

#### Tableau : Filtres "Tueurs" pour Senior Admin (Cheat Sheet)

| Objectif | Filtre Display (Copier-Coller) | Explication Technique |
| :--- | :--- | :--- |
| **Problèmes TCP Majeurs** | `tcp.analysis.flags && !tcp.analysis.keep_alive && !tcp.analysis.keep_alive_ack` | Affiche **TOUS** les flags d'analyse expert (Retrans, OOO, ZW, WinFull, DupAck) sauf Keepalives. |
| **Retransmissions Uniquement** | `tcp.analysis.retransmission || tcp.analysis.fast_retransmission || tcp.analysis.spurious_retransmission` | Différencie Fast Retrans (3 DupACK) vs Timeout (RTO) vs Spurious (ACK reçu après RTO). |
| **Zero Window / Window Full** | `tcp.analysis.zero_window || tcp.analysis.window_full` | Détection immédiate saturation receiver buffer (Application lente) ou sender buffer (Network limited). |
| **Paquets Malformés / Checksum Errors** | `expert.severity == "Error" || expert.severity == "Note" && _ws.expert.message contains "checksum"` | Filtre sur la colonne "Expert Infos". `expert.severity` valeurs: `Error`, `Warn`, `Note`, `Chat`. |
| **Latence Applicative (Time Delta)** | `tcp.analysis.ack_rtt > 0.500` | Affiche les ACKs dont le RTT calculé > 500ms. Ajustez seuil selon SLA. |
| **Handshake TLS Incomplet / Alertes** | `tls.handshake.type == 1 || tls.handshake.type == 2 || tls.alert_message` | Client Hello (1), Server Hello (2), Alertes (Fatal/Warning). |
| **Certificats TLS (SNI / CN)** | `tls.handshake.extensions_server_name` | Affiche le SNI (Server Name Indication) en clair dans le handshake Client Hello. |
| **DNS Anomalies (Truncated, RCODE != 0)** | `dns.flags.truncated == 1 || dns.flags.rcode != 0` | Détection réponses tronquées (TCP fallback requis) ou erreurs (NXDOMAIN, SERVFAIL, REFUSED). |
| **HTTP Errors 4xx/5xx** | `http.response.code >= 400` | Filtre numérique sur le code de statut. |
| **Fragments IP (Attaque / MTU)** | `ip.flags.mf == 1 || ip.frag_offset > 0` | Détection fragmentation IPv4. Pour IPv6 : `ipv6.nxt == 44`. |
| **Conversation Spécifique (5-tuple)** | `ip.addr == 10.1.1.5 && ip.addr == 10.2.2.50 && tcp.port