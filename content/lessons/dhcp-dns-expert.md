# DHCP & DNS : Architecture, Ingénierie et Protocoles Avancés

Ce document d'expertise traite du fonctionnement interne, de la sécurité avancée, de la haute disponibilité et du dépannage réseau pour les infrastructures **DHCP** et **DNS** à grande échelle.

---

## 1. Ingénierie DHCP & Mécanismes Protocolaires Avancés

### 1.1 Anatomie des Paquets et Options DHCP (RFC 2132)

DHCP repose sur le protocole de transport UDP (ports **67** pour le serveur et **68** pour le client). Le format de trame dérive du protocole patrimonial BOOTP.

#### Structure du Paquet DHCP :
* `op` (1 octet) : Code d'opération ($1 = \text{BOOTREQUEST}$, $2 = \text{BOOTREPLY}$).
* `xid` (4 octets) : Identifiant de transaction généré par le client pour corréler les requêtes et réponses.
* `ciaddr` (4 octets) : Adresse IP du client (remplie uniquement si le client est en état `BOUND`, `RENEW` ou `REBINDING`).
* `yiaddr` (4 octets) : *Your IP Address* (attribuée par le serveur).
* `siaddr` (4 octets) : Adresse IP du serveur de démarrage (ex. PXE/TFTP).
* `giaddr` (4 octets) : *Gateway IP Address* (remplie par l'agent de relais DHCP).
* `chaddr` (16 octets) : Adresse matérielle (*Client Hardware Address* / Adresse MAC).
* `options` (Variable) : Champ étendu contenant les paramètres de configuration.

#### Options DHCP Fréquemment Exploiteuses en Entreprise :

| Code | Nom de l'option | Description & Usages Avancés |
| :--- | :--- | :--- |
| **Option 3** | Router | Liste des passerelles par défaut (*Default Gateways*). |
| **Option 6** | Domain Name Server | Liste priorisée de serveurs DNS récursifs. |
| **Option 12** | Hostname | Nom d'hôte du client (utilisé pour les mises à jour Dynamic DNS - DDNS). |
| **Option 43** | Vendor-Specific Info | Transmet des configurations propriétaires (ex: IP des contrôleurs Wi-Fi CAPWAP pour APs Cisco/Aruba). |
| **Option 60** | Vendor Class Identifier (VCI) | Permet de classifier les types de clients (ex: `Cisco AP c3700`, `IP-Phone`) et de leur allouer des sous-options spécifiques. |
| **Option 66/67** | TFTP Server / Bootfile Name | Utilisées pour le démarrage réseau PXE (Preboot Execution Environment) en déploiement d'images d'OS. |
| **Option 82** | Relay Agent Information | Insérée par le switch/relais L2/L3 pour sécuriser et identifier l'emplacement physique du client. |

---

### 1.2 L'Option 82 (DHCP Relay Agent Information Option)

L'Option 82 est un mécanisme de sécurité et de routage défini dans la **RFC 3046**. Elle est ajoutée par le commutateur (Switch) d'accès ou l'agent de relais avant de transmettre la requête au serveur DHCP central.

Elle se compose de deux sous-options principales :
1. **Circuit ID (Sub-option 1) :** Identifie l'interface physique ou le VLAN d'origine sur le switch (`VLAN-ID`, `Module/Port`).
2. **Remote ID (Sub-option 2) :** Identifie l'équipement de commutation lui-même (généralement son adresse MAC de management ou son `Hostname`).

```
[ Client ] ──(Broadcast)──► [ Switch d'Accès L2/L3 ] ──(Unicast + Option 82)──► [ Serveur DHCP ]
                             (Ajoute Circuit-ID/Remote-ID)
```

#### Utilité stratégique :
* **Allocation granulaire :** Le serveur DHCP peut attribuer une IP en fonction du port physique précis sur lequel un équipement est branché (ex: prise Ethernet d'un bureau spécifique).
* **Prévention du Spoofing :** Empêche un équipement malveillant de contourner les politiques IP en changeant sa MAC address.

---

### 1.3 Architectures DHCP à Haute Disponibilité (HA)

#### 1. DHCP Failover Protocol (RFC 3074 / Microsoft Failover)
Deux serveurs DHCP synchronisent leur état de bail en temps réel via une liaison IP dédiée.
* **Mode Load Balancing (Actif/Actif) :** La charge des requêtes est répartie entre les deux serveurs selon un algorithme de hachage de l'adresse MAC (ex: 50/50).
* **Mode Hot Standby (Actif/Passif) :** Le serveur primaire gère 100% du trafic. En cas de défaillance détectée après l'expiration du délai MCLT (*Maximum Client Lead Time*), le serveur secondaire prend le relais sans rupture de bail.

#### 2. Split-Scope (Division de plage)
Approche distribuée sans synchronisation d'état :
* Le serveur A gère 80% de la plage d'adresses.
* Le serveur B gère les 20% restants sur le même sous-réseau.
* En cas de panne de A, B continue à attribuer des baux, évitant un arrêt total de la distribution IP.

---

## 2. Architecture et Mécanismes DNS de Niveau Expert

### 2.1 Résolution Récursive, Interrogations Root et Cache Poisoning

Le système de nommage mondial est structuré sous forme d'arbre hiérarchique distribué.

```
                         [ . ] (Root Zone)
                          /   \
                   [ .com ]   [ .fr ] (TLD)
                     /
            [ example.com ] (Authoritative Zone)
```

#### Processus d'Analyse d'une Requête Récursive Complète :
1. **Client** $\rightarrow$ **Resolver Recurser Local** (ex: `10.0.0.1`) : Requête `A www.example.com` (Flag `RD=1` : *Recursion Desired*).
2. **Resolver Local** $\rightarrow$ **Root Server (`.`)** : Requête `NS www.example.com`.
   * *Réponse :* Referral vers les serveurs TLD `.com` (Records `NS` + Glue Records `A`).
3. **Resolver Local** $\rightarrow$ **TLD Server (`.com`)** : Requête `A www.example.com`.
   * *Réponse :* Referral vers les serveurs autoritaires de `example.com`.
4. **Resolver Local** $\rightarrow$ **Authoritative Server (`ns1.example.com`)** : Requête `A www.example.com`.
   * *Réponse :* `www.example.com IN A 93.184.216.34` (Flag `AA=1` : *Authoritative Answer*).
5. **Resolver Local** $\rightarrow$ **Client** : Transmet l'adresse IP finale et met le résultat en cache selon le paramètre **TTL** (*Time-To-Live*).

---

### 2.2 Fichiers de Zone et Structure des Records

Un fichier de zone DNS (RFC 1035) définit la cartographie des ressources pour un domaine autoritaire.

```dns
$TTL 86400
@   IN  SOA ns1.example.com. admin.example.com. (
            2026102101 ; Serial (YYYYMMDDnn)
            3600       ; Refresh (1h)
            1800       ; Retry (30m)
            604800     ; Expire (1w)
            86400 )    ; Minimum TTL / Negative Cache TTL

; Serveurs de noms autoritaires
@   IN  NS  ns1.example.com.
@   IN  NS  ns2.example.com.

; Aiguillage MX (Messagerie)
@   IN  MX  10 mail1.example.com.
@   IN  MX  20 mail2.example.com.

; Enregistrements d'hôtes (A/AAAA)
ns1   IN  A     192.0.2.1
ns2   IN  A     192.0.2.2
mail1 IN  A     192.0.2.10
mail2 IN  A     192.0.2.11
www   IN  A     93.184.216.34
www   IN  AAAA  2606:2800:220:1:248:1893:25c8:1946

; CNAME (Alias)
app   IN  CNAME www.example.com.

; Securité Email (TXT)
@   IN  TXT   "v=spf1 ip4:192.0.2.10 include:_spf.google.com ~all"
```

---

### 2.3 DNSSEC (DNS Security Extensions)

Le protocole DNS d'origine ne chiffre ni ne signe les réponses, ce qui le rend vulnérable à l'empoisonnement de cache (*Kaminsky Attack*). **DNSSEC** (RFC 4033-4035) intègre l'authentification de l'origine et l'intégralité des données grâce à la cryptographie asymétrique.

#### Types de Records Spécifiques à DNSSEC :
* **RRSIG (Resource Record Signature) :** Contient la signature numérique d'un jeu de données RRSet (`A`, `MX`, etc.).
* **DNSKEY :** Contient la clé publique utilisée pour vérifier la signature d'un `RRSIG`.
  * *ZSK (Zone Signing Key) :* Clé servant à signer quotidiennement les enregistrements de la zone.
  * *KSK (Key Signing Key) :* Clé servant à signer la `DNSKEY` (la ZSK).
* **DS (Delegation Signer) :** Empreinte numérique (hash) de la KSK, hébergée dans la zone parente (ex: la zone TLD `.com`) pour maintenir la **Chaîne de Confiance** (*Chain of Trust*).
* **NSEC / NSEC3 :** Permet la preuve de non-existence d'un enregistrement sans ouvrir la porte aux attaques par énumération de zone.

```
[ Root Zone (.) ] ──(Contient le DS de .com)──► [ TLD Zone (.com) ] ──(Contient le DS de example.com)──► [ Zone example.com ]
```

---

### 2.4 DNS Split-Horizon et Anycast DNS

#### Split-Horizon DNS (Views)
Permet de fournir des réponses DNS différentes en fonction de l'adresse IP d'origine du demandeur :
* **Vue Interne (LAN Corporate) :** `intranet.entreprise.local` $\rightarrow$ IP privée (`10.50.1.100`).
* **Vue Externe (Internet) :** `intranet.entreprise.local` $\rightarrow$ Non résolu ou redirigé vers une IP publique de Reverse Proxy/WAF (`198.51.100.50`).

#### Anycast DNS
Déploiement où **plusieurs serveurs DNS physiques à travers le monde partagent la même adresse IP**.
* Grâce au routage BGP (Border Gateway Protocol), les requêtes d'un utilisateur sont automatiquement dirigées vers le serveur Anycast le plus proche au sens métrique BGP.
* **Avantages :** Redondance massive, latence minimale et haute résistance aux attaques DDoS (amplification DNS).

---

## 3. Sécurité Avancée et Attaques Systémiques

### 3.1 Vecteurs d'Attaques & Protections DHCP

1. **Rogue DHCP Server Attack :**
   * *Mécanisme :* Un pirate déploie un serveur DHCP illégitime sur le LAN pour distribuer sa propre IP comme Gateway/DNS.
   * *Mitigation :* **DHCP Snooping** sur les commutateurs L2. Les ports sont définis comme *Trusted* (connectés au vrai serveur DHCP) ou *Untrusted* (ports utilisateurs). Si une réponse `DHCPOFFER` ou `DHCPACK` arrive sur un port *Untrusted*, le port est immédiatement désactivé (*Err-disable*).

2. **DHCP Starvation (Épuisement du pool) :**
   * *Mécanisme :* Outils (ex: Yersinia) générant des milliers de requêtes avec des adresses MAC forgées.
   * *Mitigation :* Activation de **Port Security** sur les switchs (limitation du nombre d'adresses MAC autorisées par port physique) combinée au DHCP Snooping.

---

### 3.2 Vecteurs d'Attaques & Protections DNS

1. **DNS Tunneling (Exfiltration de données) :**
   * *Mécanisme :* Encodage de données ou de commandes C2 (Command & Control) dans les sous-domaines des requêtes DNS (ex: `dGhlc2VjcmV0.attacker.com`).
   * *Mitigation :* **DNS Sinkholing**, Inspection Applicative (NGFW) et analyse comportementale de la longueur/entropie des sous-domaines.

2. **DNS Amplification Attack (DDoS) :**
   * *Mécanisme :* Envoi de requêtes DNS de type `ANY` ou `TXT` (très volumineuses) avec usurpation d'adresse IP source (Spoofing IP) pointant vers la cible.
   * *Mitigation :* Désactivation de la récursion sur les serveurs autoritaires publiques, mise en œuvre de **RRL (Response Rate Limiting)**.

---

## 4. Dépannage et Commandes Systèmes

### 4.1 Diagnostics DHCP (Linux & Windows)

#### Côté Client Linux :
```bash
# Libérer et renouveler le bail DHCP via NetworkManager / dhclient
sudo dhclient -r eth0    # Release (Libération)
sudo dhclient eth0       # Request (Obtention)

# Inspecter les baux actifs sous Linux
cat /var/lib/dhcp/dhclient.leases
```

#### Côté Client Windows :
```cmd
ipconfig /release        :: Libère l'adresse IP
ipconfig /renew          :: Lance un cycle DORA de renouvellement
ipconfig /all            :: Affiche l'adresse du serveur DHCP, la durée du bail et l'Option 82
```

---

### 4.2 Diagnostics DNS Avancés (`dig` & `nslookup`)

L'outil **`dig`** (Domain Information Groper) est le standard d'ingénierie pour le diagnostic DNS.

```bash
# Requête standard de type A avec affichage détaillé
dig www.example.com A

# Interroger directement un serveur DNS spécifique (ex: 1.1.1.1)
dig @1.1.1.1 www.example.com AAAA

# Effectuer une résolution récursive pas-à-pas (Trace du Root aux serveurs autoritaires)
dig +trace www.example.com

# Inspecter la résolution inverse (PTR) d'une adresse IP
dig -x 93.184.216.34

# Vérifier la présence et la validité des enregistrements DNSSEC
dig +dnssec example.com A

# Tester un transfert de zone (AXFR) - Doit être bloqué en production !
dig @ns1.example.com example.com AXFR
```

---

## 5. Synthèse comparative des Protocoles de Sécurité Moderne

| Protocole | Couche / Port | Objectif Principal | Avantages |
| :--- | :--- | :--- | :--- |
| **DHCP Snooping** | Couche 2 (Data Link) | Bloquer les faux serveurs DHCP sur le commutateur. | Implémentation matérielle simple et transparente. |
| **DNSSEC** | Couche 7 (DNS Data) | Garantir l'authenticité et l'intégrité des réponses DNS. | Élimine les attaques par empoisonnement de cache. |
| **DoT (DNS over TLS)** | TCP 853 | Chiffrer les requêtes DNS entre le client et le résolveur. | Masque les requêtes DNS contre l'écoute clandestine (Eavesdropping). |
| **DoH (DNS over HTTPS)** | TCP 443 | Transporter les requêtes DNS dans des flux HTTPS standard. | Contourne le blocage réseau basique et garantit la confidentialité. |