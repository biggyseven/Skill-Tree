# Cours Intensif – Policy‑Based Routing (PBR)  
**Niveau** : Administrateur Réseau Senior / CCIE  
**Durée estimée** : 2 jours (12 h) de théorie + 4 h d’ateliers pratiques  

---

## Table des matières

| # | Section |
|---|---------|
| 1 | Introduction & concepts fondamentaux |
| 2 | Pourquoi utiliser le PBR ? (vs. routage statique/dynamique) |
| 3 | Architecture et flux de traitement |
| 4 | Plateformes supportées – comparaison Cisco, Juniper, Linux |
| 5 | Syntaxe Cisco IOS / IOS‑XR / NX‑OS |
| 6 | Syntaxe Juniper (Junos) |
| 7 | Implémentation sous Linux (iproute2) |
| 8 | Cas d’usage avancés (QoS, VPN, MPLS, IPv6, NAT) |
| 9 | Sécurité et bonnes pratiques |
| 10| Outils de vérification et de monitoring |
| 11| Atelier de dépannage – scénario complet |
| 12| Bibliographie & ressources complémentaires |

---

## 1. Introduction & concepts fondamentaux  

**Policy‑Based Routing (PBR)** désigne toute technique qui décide du prochain saut d’un paquet **en fonction d’attributs de couche 3/4** (adresse source/destination, protocole, port, DSCP, etc.) plutôt que du **préfixe de destination** seul.  

- **Objectif** : appliquer des politiques de trafic (ex. : rediriger le trafic VoIP vers un lien à faible latence, forcer le trafic de sauvegarde vers un tunnel, etc.).  
- **Mécanisme** : le routeur intercepte le paquet après le processus de décision de routage, le compare à une **liste de correspondances** (ACL/extended ACL, prefix‑list, etc.) et, si une **action** est définie, le **remplace** l’adresse de next‑hop ou applique d’autres traitements (QoS, NAT, etc.).  

### 1.1 Terminologie clé  

| Terme | Définition |
|------|------------|
| **Match** | Condition(s) (ACL, prefix‑list, route‑map, etc.) évaluée(s) sur le paquet. |
| **Action** | Ce que le routeur fait lorsqu’un match est trouvé : `set ip next-hop`, `set interface`, `set metric`, `set vrf`, etc. |
| **Sequence** | Ordre d’évaluation des politiques (premier match = première action). |
| **Route‑map** (Cisco) / **Policy‑statement** (Junos) | Structure logique qui associe un ou plusieurs *match* à une ou plusieurs *action*. |
| **PBR Class‑Map** (NX‑OS) | Equivalent à la *class‑map* de QoS, utilisée pour sélectionner le trafic. |
| **Fallback** | Route par défaut (RIB) utilisée lorsqu’aucune politique ne correspond. |

---

## 2. Pourquoi utiliser le PBR ?  

| Critère | Routage statique | Routage dynamique (OSPF/EIGRP/BGP) | PBR |
|---------|------------------|--------------------------------------|-----|
| **Granularité** | Préfixe complet uniquement | Préfixe complet uniquement | Adresse source, ports, protocole, DSCP, etc. |
| **Réactivité** | Nécessite reconfiguration manuelle | Converge automatiquement, mais limité aux préfixes | Modifications en temps réel via ACL/route‑map |
| **Scalabilité** | Peu adapté aux milliers de flux | Excellent pour topologies larges | Limité par le nombre de ACL/route‑maps (attention à la mémoire TCAM) |
| **Complexité de politique** | Faible | Faible à moyenne (BGP communities) | Très élevée (multi‑critères, actions multiples) |
| **Impact sur le dataplane** | Aucun (lookup normal) | Aucun (lookup normal) | Consommation TCAM + CPU (déviation) |

**Cas d’usage typiques**  

1. **Redirection de trafic vers un firewall** – tout le trafic HTTP sortant passe par un IDS.  
2. **Load‑balancing basé sur l’IP source** – répartition du trafic d’un data‑center vers deux ISP selon la classe d’adresse.  
3. **Mise en œuvre de QoS différenciée** – les flux vidéo reçoivent un next‑hop privilégié.  
4. **Mise en place de tunnels GRE/IPsec** – trafic de sauvegarde encapsulé vers un site distant.  

---

## 3. Architecture et flux de traitement  

```
+-------------------+      +-------------------+      +-------------------+
| 1. Ingress (L2)   | ---> | 2. ACL/Match (TCAM) | ---> | 3. Action (CPU/TCAM) |
+-------------------+      +-------------------+      +-------------------+
        |                         |                         |
        |                         v                         v
        |                +-------------------+   +-------------------+
        |                |  Route‑map/Policy |   |  Next‑hop / FRR   |
        |                +-------------------+   +-------------------+
        |                         |                         |
        |                         v                         v
        |                +-------------------+   +-------------------+
        +--------------> |  Forwarding (RIB) |--> |  Output Interface |
                         +-------------------+   +-------------------+
```

1. **Lookup RIB** – Le routeur calcule le next‑hop normal.  
2. **PBR check** – Si une **policy** est appliquée à l’interface d’entrée, le paquet passe par le **match engine** (TCAM).  
3. **Action** – Si le match réussit, le next‑hop est remplacé ou d’autres actions sont appliquées.  
4. **Forwarding** – Le paquet est transmis sur l’interface résultante.  

> **Note** : Sur les plateformes Cisco, le PBR est exécuté **avant** le processus de décision de la RIB, mais **après** le contrôle d’accès (ACL) normal.  

---

## 4. Plateformes supportées – comparaison  

| Plateforme | Syntaxe principale | Types de match | Types d’actions | Limites TCAM | Observations |
|------------|-------------------|----------------|----------------|--------------|--------------|
| **Cisco IOS** | `route-map`, `access-list` | IP src/dst, ports, protocol, DSCP, TTL, MAC | `set ip next-hop`, `set interface`, `set metric`, `set vrf`, `set local-preference` | ~ 2000 entries (varie selon HW) | PBR uniquement sur interfaces de type *routed* (pas sur VLAN SVI) |
| **Cisco IOS‑XR** | `policy`, `class-map`, `policy-map` | Même que IOS + `ipv6` | `set next-hop`, `set interface`, `set vrf`, `set qos` | TCAM partagé avec QoS | Utilise *policy‑based forwarding* (PBF) – même principe |
| **Cisco NX‑OS** | `class-map`, `policy-map`, `route-map` | IP, MAC, VLAN, MPLS label | `set ip next-hop`, `set interface`, `set vrf` | 4000‑8000 entrées (depends on ASIC) | PBR peut être appliqué sur *VLAN interfaces* (SVI) |
| **Juniper Junos** | `policy-options policy-statement` | `from` (prefix, interface, port, protocol, dscp) | `then accept` + `next-hop`, `next-table`, `routing-instance` | 4096 entries (TCAM) | PBR appelé *policy‑based forwarding* (PBF) |
| **Linux (iproute2)** | `ip rule`, `ip route` | `from`, `to`, `fwmark`, `iif`, `oif`, `tos` | `table`, `via`, `dev`, `scope` | Aucun TCAM – CPU only | Idéal pour les routeurs virtuels / containers |

---

## 5. Syntaxe Cisco IOS / IOS‑XR / NX‑OS  

### 5.1. Étape 1 – Créer une ACL de correspondance  

```text
ip access-list extended PBR_WEB
 10 permit tcp any host 203.0.113.10 eq 80
 20 permit tcp any host 203.0.113.10 eq 443
```

> *Cette ACL capture tout le trafic HTTP/HTTPS vers le serveur web du DMZ.*

### 5.2. Étape 2 – Créer le route‑map (policy)  

```text
route-map PBR_WEB_POLICY permit 10
  match ip address PBR_WEB
  set ip next-hop 198.51.100.1
!
route-map PBR_WEB_POLICY deny 20
  ! fallback – aucune action, le routage normal s’applique
```

- **`permit 10`** : priorité (plus petit = plus haut).  
- **`set ip next-hop`** : redirige le trafic vers le firewall (IP du firewall).  

### 5.3. Étape 3 – Appliquer la politique sur l’interface d’entrée  

```text
interface GigabitEthernet0/1
  ip address 10.0.0.1 255.255.255.0
  ip policy route-map PBR_WEB_POLICY
```

> **Important** : `ip policy` doit être placé **avant** toute configuration d’`ip address` sur les versions antérieures à 12.4(15)T – sinon le route‑map ne s’applique pas.

### 5.4. Vérifications  

| Commande | Description |
|----------|-------------|
| `show route-map` | Affiche les route‑maps et le nombre de matchs. |
| `show ip policy` | Liste les interfaces où un `ip policy` est appliqué. |
| `show access-lists PBR_WEB` | Vérifie le trafic correspondant (counters). |
| `show ip cef` | Confirme que le trafic a bien un next‑hop modifié (look‑up CEF). |
| `debug ip policy` | Débogage en temps réel (attention à la charge CPU). |

### 5.5. Exemple complet (IPv6)  

```text
ipv6 access-list PBR_V6_SIP
 10 permit udp any any eq 5060
!
route-map PBR_V6_POLICY permit 10
  match ipv6 address PBR_V6_SIP
  set ipv6 next-hop 2001:db8:1::1
!
interface TenGigabitEthernet2/0/0
  ipv6 address 2001:db8:0::1/64
  ipv6 policy route-map PBR_V6_POLICY
```

### 5.6. PBR avec **next‑hop VRF**  

```text
route-map PBR_VRF permit 10
  match ip address 101
  set vrf red
  set ip next-hop 10.10.10.1
```

> Cela force le trafic à sortir du VRF *red* – utile pour le **multitenant**.

### 5.7. PBR sur **NX‑OS** (class‑map / policy‑map)  

```text
class-map type traffic match-any PBR_CLASS_HTTP
  match protocol http
  match protocol https
!
policy-map type pbr PBR_POLICY_HTTP
  class PBR_CLASS_HTTP
    set ip next-hop 198.51.100.2
!
interface Ethernet1/1
  ip address 10.1.1.1/24
  ip policy route-map PBR_POLICY_HTTP
```

---

## 6. Syntaxe Juniper (Junos) – Policy‑Based Forwarding (PBF)  

### 6.1. Créer un *firewall filter* (équivalent ACL)  

```text
firewall {
    family inet {
        filter PBF_WEB {
            term HTTP {
                from {
                    protocol tcp;
                    destination-port [80 443];
                }
                then accept;
            }
            term DEFAULT {
                then reject;
            }
        }
    }
}
```

### 6.2. Créer le *policy‑statement*  

```text
policy-options {
    policy-statement PBF_WEB {
        term match-http {
            from {
                filter PBF_WEB;
            }
            then {
                next-hop 198.51.100.2;
                accept;
            }
        }
        term default {
            then reject;
        }
    }
}
```

### 6.3. Appliquer le PBF sur une interface  

```text
interfaces {
    ge-0/0/1 {
        unit 0 {
            family inet {
                address 10.0.0.1/24;
                pbf {
                    policy PBF_WEB;
                }
            }
        }
    }
}
```

### 6.4. Vérifications Junos  

| Commande | Description |
|----------|-------------|
| `show configuration policy-options policy-statement PBF_WEB` | Affiche la politique. |
| `show firewall filter PBF_WEB` | Statistiques de correspondance. |
| `show pbf summary` | Liste des interfaces avec PBF actif. |
| `show route forwarding-table extensive` | Vérifie le next‑hop appliqué. |
| `monitor start pbf` | Capture en temps réel (Junos OS). |

---

## 7. Implémentation sous Linux (iproute2)  

Linux ne possède pas de TCAM, le PBR se fait via **policy routing** (tables multiples) et **iptables** (pour le marquage).  

### 7.1. Étape 1 – Créer une règle de marquage (iptables)  

```text
# Marquer le trafic HTTP/HTTPS sortant du LAN
iptables -t mangle -A PREROUTING -i eth0 -p tcp -m multiport --dports 80,443 -j MARK --set-mark 0x10
```

### 7.2. Étape 2 – Créer une table de routage dédiée  

```text
# Ajout de la table dans /etc/iproute2/rt_tables
echo "200 pbr-web" >> /etc/iproute2/rt_tables
```

### 7.3. Étape 3 – Ajouter une route dans la table *pbr-web*  

```text
ip route add default via 198.51.100.1 dev eth1 table pbr-web
```

### 7.4. Étape 4 – Créer la règle de sélection de table  

```text
ip rule add fwmark 0x10 lookup pbr-web priority 100
```

> **Priorité** : plus petite = plus haute.  
> **fwmark** : le marqueur décimal (0x10 = 16) doit correspondre à la règle iptables.

### 7.5. Vérifications Linux  

| Commande | Description |
|----------|-------------|
| `iptables -t mangle -L -v` | Compteurs de marquage. |
| `ip rule show` | Liste les règles de politique. |
| `ip route show table pbr-web` | Table de routage spécifique. |
| `tcpdump -i eth1 -nn` | Capture le trafic redirigé. |
| `watch -n1 "cat /proc/net/rt_cache"` | Observe le cache de routage. |

---

## 8. Cas d’usage avancés  

### 8.1. Redirection vers un tunnel GRE  

```
interface Tunnel0
  ip address 10.255.255.1 255.255.255.252
  tunnel source 192.0.2.1
  tunnel destination 203.0.113.2
!
route-map GRE_PBR permit 10
  match ip address GRE_ACL
  set interface Tunnel0
!
ip access-list extended GRE_ACL
 10 permit ip any 10.10.0.0 0.0.255.255
!
interface GigabitEthernet0/2
  ip policy route-map GRE_PBR
```

### 8.2. PBR + QoS (Co‑scheduling)  

```
class-map match-any VOIP
  match protocol udp
  match access-group name VOIP_ACL
!
policy-map type qos VOIP_QOS
  class VOIP
    set dscp ef
!
policy-map type pbr VOIP_PBR
  class VOIP
    set ip next-hop 198.51.100.5
!
interface GigabitEthernet0/3
  service-policy type qos VOIP_QOS
  ip policy route-map VOIP_PBR
```

> **Resultat** : le trafic VoIP reçoit le DSCP EF et est envoyé via le lien à faible latence.

### 8.3. PBR pour **MPLS L3VPN** (Cisco IOS‑XR)  

```text
route-policy PBR_VPN permit 10
  if destination in (10.0.0.0/8) then
    set next-hop 172.16.1.1
    set vrf CustomerA
    pass
  endif
!
interface GigabitEthernet0/