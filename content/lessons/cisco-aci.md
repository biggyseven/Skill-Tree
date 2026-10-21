# Cisco ACI : fabric pilotée par politiques — Niveau Expert

> **node_id :** `cisco-aci` · **Niveau :** CCIE Data Center · **Prérequis :** `vxlan`, `spine-leaf`, `vrf`, `automation`

---

## 1. Vue d'ensemble

**Cisco ACI** (*Application Centric Infrastructure*) est une architecture de data center où une fabric **spine-leaf** est entièrement pilotée par un contrôleur, l'**APIC**, selon un **modèle de politiques déclaratif**. L'administrateur décrit l'**intention** (« les serveurs Web parlent aux serveurs App sur TCP 8080 ») et l'APIC la traduit en configuration sur chaque nœud.

| Critère | Réseau traditionnel (CLI par équipement) | Cisco ACI |
|---|---|---|
| Point de configuration | Chaque switch | **APIC** (cluster) |
| Modèle | Impératif (VLAN, SVI, ACL) | **Déclaratif** (tenant, EPG, contrat) |
| Segmentation | VLAN + ACL | **EPG + contrats** (allow-list par défaut) |
| Plan de contrôle fabric | Protocoles manuels | IS-IS, COOP, MP-BGP **automatiques** |
| Découverte / mise en service | Manuelle | **Fabric discovery** automatique (zero-touch) |
| API | Hétérogène | **REST** unique, modèle objet (MIT) |
| Observabilité | SNMP, syslog | Faults, health score, atomic counters |

---

## 2. Architecture physique

```
        +----------+     +----------+          +----------+
        |  SPINE1  |     |  SPINE2  |   ...    |  SPINEn  |   (jamais de serveur ici)
        +--+--+--+-+     +-+--+--+--+          +----------+
           |  |  |         |  |  |
   +-------+  |  +----+    |  |  +--------+      Chaque leaf est connecté
   |      +---+      |    |  +---+        |      à TOUS les spines
+--+---+ +--+---+ +--+---+ +--+---+  +----+---+
|LEAF1 | |LEAF2 | |LEAF3 | |LEAF4 |  |BORDER  |
+--+---+ +--+---+ +--+---+ +------+  | LEAF   |-- L3Out --> WAN / FW
   |        |        |               +--------+
 Srv A    Srv B    APIC1..3 (connectés aux leafs)
```

### 2.1 Rôles

| Composant | Rôle |
|---|---|
| **Spine** | Transport VXLAN ; héberge la base **COOP** (Council of Oracles Protocol) avec les localisations d'endpoints ; route-reflector MP-BGP |
| **Leaf** | Connecte serveurs, APIC, routeurs externes ; applique les contrats (TCAM) ; VTEP |
| **Border leaf** | Leaf portant les **L3Out** vers l'extérieur |
| **APIC** | Contrôleur, cluster de **3 (ou 5, 7) nœuds** ; stocke et distribue la configuration (sharding) |
| **Infra VRF / overlay-1** | VRF interne de l'underlay fabric (tenant `infra`) |

### 2.2 Protocoles internes (automatiques)

| Fonction | Protocole |
|---|---|
| Underlay (loopbacks, TEP) | **IS-IS** (L1) |
| Transport de données | **VXLAN** (VNI) avec en-tête iVXLAN étendu |
| Localisation des endpoints | **COOP** (spines, base de données) |
| Routes externes L3Out | **MP-BGP** (spines en RR) |
| Multicast BUM | Groupes multicast **GIPo** dans l'underlay (IS-IS FTAG) |
| Découverte des nœuds | **LLDP** + DHCP (APIC fournit les adresses TEP) |

> **Subtilité d'examen :** contrairement à une fabric EVPN « maison », le plan de contrôle ACI n'est pas BGP EVPN pour le L2 interne : l'apprentissage des endpoints passe par **COOP** et des mécanismes de plan de données (*gleaning*, *proxy lookup* dans le spine).

---

## 3. Modèle de politiques

### 3.1 Hiérarchie logique

```
 Tenant
  ├── VRF (contexte L3)
  ├── Bridge Domain (BD)  ── subnets (passerelles), ARP flooding, unicast routing
  ├── Application Profile (AP)
  │     ├── EPG Web ─── BD, domaine physique/VMM, chemins statiques
  │     ├── EPG App
  │     └── EPG DB
  ├── Contract ── Subject ── Filter (protocole/ports)
  └── L3Out ── External EPG (l3extInstP)
```

| Objet | Description | Équivalent traditionnel |
|---|---|---|
| **Tenant** | Conteneur d'administration/isolement | Client / unité métier |
| **VRF** | Domaine de routage L3 | VRF |
| **Bridge Domain** | Domaine de diffusion L2 avec subnets | VLAN + SVI |
| **EPG** | Groupe d'endpoints partageant la même politique | Zone de sécurité |
| **Application Profile** | Regroupe les EPG d'une application | Application |
| **Contract** | Règles de communication entre EPG | ACL / règle de pare-feu |
| **Filter** | Ports/protocoles autorisés | ACE |
| **L3Out** | Connexion routée externe | Interface WAN + routage |

### 3.2 Tenants prédéfinis

| Tenant | Usage |
|---|---|
| **common** | Objets partagés (filtres, VRF, contrats) visibles par tous |
| **infra** | Fabric overlay-1, VXLAN, TEP |
| **mgmt** | Gestion in-band / out-of-band des nœuds |

### 3.3 EPG, consommateur et fournisseur

Un **contrat** est **fourni** (*provide*) par un EPG et **consommé** (*consume*) par un autre. **Par défaut, rien ne communique entre EPG différents** (modèle allow-list). À l'intérieur d'un même EPG, la communication est libre (sauf *Intra-EPG isolation*).

```
 EPG Web --- consomme ---> [Contrat WEB-TO-APP : filtre tcp/8080] <--- fournit --- EPG App
```

Le contrat est **directionnel** pour la notion de rôle mais les filtres peuvent s'appliquer dans les deux sens (*Apply both directions* + *Reverse filter ports*).

---

## 4. Access policies : relier les ports à la fabric

La chaîne des **Access Policies** est la plus examinée à l'écrit comme au lab.

```
 VLAN Pool ──> Domaine (Physical/VMM/L3) ──> AAEP ──> Interface Policy Group
                                                           │
 Interface Profile ──(Port Selector)──────────────────────┘
        │
 Switch Profile ──(Leaf Selector)──> Leaf(s) concernés
```

| Objet | Rôle |
|---|---|
| **VLAN Pool** | Plage de VLAN (statique ou dynamique) utilisable |
| **Domain** | Associe le pool à un type de connexion (physique, VMM, L2/L3) |
| **AAEP** | *Attachable Access Entity Profile* : lie les domaines aux ports |
| **Interface Policy Group** | Paramètres de port (LACP/vPC, CDP, LLDP, vitesse) |
| **Interface Profile** | Sélection des ports |
| **Switch Profile** | Sélection des leafs ; référence l'Interface Profile |

> **Règle d'or :** un EPG ne peut utiliser un VLAN que si **EPG → Domaine → VLAN Pool** et **Domaine → AAEP → Port** sont cohérents. Une erreur ici provoque la faute F0467 « invalid-vlan / invalid-path ».

---

## 5. Contrats, filtres et zoning-rules

| Notion | Détail |
|---|---|
| **pcTag** | Étiquette (class ID) d'un EPG, utilisée dans le TCAM |
| **Zoning-rule** | Entrée TCAM : (scope VRF, src pcTag, dst pcTag, filtre) → permit/deny/log |
| **Policy enforcement** | VRF : *Enforced* (défaut) ou *Unenforced* |
| **vzAny** | Tous les EPG d'un VRF : un seul contrat pour tous (économie de TCAM) |
| **Preferred Group** | Les EPG membres communiquent librement entre eux |
| **Taboo contract** | Règles de refus explicites, évaluées avant les permits |
| **uSeg EPG** | Micro-segmentation par attributs (VM name, IP, MAC) |

Priorités principales de rule (de la plus haute à la plus basse) : *deny/taboo explicites* > *contrats spécifiques (permit)* > *implicit deny*.

Commandes de vérification sur le leaf :

```
leaf101# show zoning-rule scope 2850817
leaf101# show zoning-filter
leaf101# show system internal policy-mgr stats
leaf101# show vlan extended
leaf101# show endpoint ip 10.10.10.21
leaf101# show ip route vrf TENANT-A:VRF1
```

---

## 6. Flux de trafic : forwarding dans la fabric

### 6.1 Même sous-réseau (BD) : L2

1. Le leaf d'entrée classe le paquet dans un EPG via (port, VLAN) ou uSeg.
2. Il cherche la MAC de destination ; s'il ne la connaît pas, il l'envoie à un **spine proxy** (COOP) qui renvoie la localisation (sans flooding dans le cas standard : *hardware proxy*).
3. Encapsulation VXLAN vers le leaf distant avec le **pcTag source** dans l'en-tête.
4. Le leaf distant applique le contrat avec (src pcTag, dst pcTag).

### 6.2 Routage inter-BD (même VRF)

La **passerelle** (subnet du BD) est **distribuée sur tous les leafs** (*pervasive gateway*). Le routage s'effectue sur le leaf d'entrée, puis le paquet est tunnelé vers le leaf de destination (sans passer par un routeur central).

### 6.3 Paramètres clés d'un Bridge Domain

| Paramètre | Valeur recommandée | Remarque |
|---|---|---|
| L2 Unknown Unicast | **Hardware Proxy** | Évite le flooding ; *Flood* pour hôtes spéciaux |
| ARP Flooding | Désactivé si GW dans l'ACI | Activer si GW externe |
| Unicast Routing | Activé si le BD porte la passerelle | Nécessaire pour le /32 learning |
| Limit IP Learning to Subnet | Activé | Empêche l'apprentissage d'IP hors subnet |
| Endpoint Retention | 300 s (local) | Durée de conservation |

---

## 7. L3Out : connectivité externe

Un **L3Out** relie un VRF ACI à un routeur/pare-feu externe via OSPF, EIGRP, BGP, ou routes statiques.

```
 EPG Web --(contrat)--> External EPG "0.0.0.0/0" (l3extInstP)
                                   │
                             L3Out (BORDER LEAF)
                                   │  OSPF / BGP
                                Routeur WAN
```

| Élément | Rôle |
|---|---|
| **Logical Node/Interface Profile** | Définit les border leafs et interfaces (SVI, routed, sub-interface) |
| **External EPG** | Classe le trafic externe par préfixe (`0.0.0.0/0` = tout) |
| **Route profile / Route-map** | Import/export contrôlé |
| **Scope du subnet externe** | *External Subnets for the External EPG* (classification) ; *Export Route Control* ; *Shared Route Control* |
| **MP-BGP interne** | Distribue les routes externes aux autres leafs via spines |

Erreurs fréquentes : oublier d'associer le BD à l'L3Out (`Associated L3Outs`), subnet du BD non marqué **Advertised Externally** (scope *public*), contrat absent entre l'EPG et l'External EPG.

---

## 8. Automatisation : API REST et Infrastructure as Code

L'APIC expose le **MIT** (*Management Information Tree*) en REST (JSON/XML). Chaque objet a un **DN** (*Distinguished Name*), par exemple `uni/tn-TENANT-A/ap-APP1/epg-WEB`.

### 8.1 Authentification et création d'un tenant

```bash
# 1. Authentification (cookie APIC-cookie)
curl -k -c cookie.txt -X POST https://apic.lab.local/api/aaaLogin.json \
  -d '{"aaaUser":{"attributes":{"name":"admin","pwd":"VotreMotDePasse"}}}'

# 2. Création complète d'un tenant
curl -k -b cookie.txt -X POST https://apic.lab.local/api/mo/uni.json -d '
{
 "fvTenant": {
  "attributes": {"name": "TENANT-A"},
  "children": [
   {"fvCtx": {"attributes": {"name": "VRF1"}}},
   {"fvBD": {"attributes": {"name": "BD-WEB", "unicastRoute": "yes"},
     "children": [
       {"fvRsCtx": {"attributes": {"tnFvCtxName": "VRF1"}}},
       {"fvSubnet": {"attributes": {"ip": "10.10.10.1/24", "scope": "public"}}}
     ]}},
   {"fvAp": {"attributes": {"name": "APP1"},
     "children": [
       {"fvAEPg": {"attributes": {"name": "WEB"},
         "children": [{"fvRsBd": {"attributes": {"tnFvBDName": "BD-WEB"}}}]}}
     ]}}
  ]
 }
}'
```

### 8.2 Requêtes de lecture

```bash
curl -k -b cookie.txt "https://apic.lab.local/api/class/fvAEPg.json"
curl -k -b cookie.txt "https://apic.lab.local/api/class/faultInst.json?query-target-filter=eq(faultInst.severity,\"critical\")"
```

Sur l'APIC en CLI : `moquery -c fvAEPg`, `moquery -d uni/tn-TENANT-A`.

### 8.3 Ansible (collection `cisco.aci`)

```yaml
- name: Créer le tenant et le VRF
  hosts: apic
  gather_facts: false
  tasks:
    - name: Tenant
      cisco.aci.aci_tenant:
        host: "{{ inventory_hostname }}"
        username: admin
        password: "{{ apic_password }}"
        tenant: TENANT-A
        state: present
        validate_certs: false
    - name: VRF
      cisco.aci.aci_vrf:
        host: "{{ inventory_hostname }}"
        username: admin
        password: "{{ apic_password }}"
        tenant: TENANT-A
        vrf: VRF1
        state: present
        validate_certs: false
```

Autres options : **Terraform** (provider `CiscoDevNet/aci`), SDK Python `acitoolkit`, **Cobra SDK**, **Nexus Dashboard Orchestrator**.

---

## 9. Multi-Pod, Multi-Site, Remote Leaf

| Architecture | Principe | Éléments clés |
|---|---|---|
| **Multi-Pod** | Plusieurs « pods » (spine-leaf) interconnectés, **un seul cluster APIC** (un domaine de défaut) | **IPN** (Inter-Pod Network) : OSPF, PIM Bidir, DHCP relay, MTU ≥ +50 octets |
| **Multi-Site** | Plusieurs fabrics **indépendantes** (chacune avec son APIC) orchestrées | **ISN** (Inter-Site Network), **NDO** (Nexus Dashboard Orchestrator), EVPN entre sites, schémas/templates |
| **Remote Leaf** | Leaf déporté sur un site distant, géré par l'APIC central | RTT < 300 ms, IPN/WAN |
| **Stretched BD / EPG** | Étend un domaine L2 sur plusieurs sites | Contrôlé via les templates NDO |

```
   POD 1                         POD 2
 [Spines] ---- IPN (OSPF + PIM Bidir) ---- [Spines]
   |                                         |
 [Leafs]                                  [Leafs]
        ^------- cluster APIC unique -------^
```

Critère de choix : **Multi-Pod** pour une extension haute disponibilité d'un même domaine de défaut (< 50 ms RTT), **Multi-Site** pour isoler les domaines de faute (DR, régions).

---

## 10. Intégrations de services

| Intégration | Description |
|---|---|
| **VMM Domain** | Intégration vCenter/Hyper-V/Kubernetes : l'APIC crée des port-groups et classe les VM dans les EPG |
| **Service Graph** | Insère un pare-feu/LB dans le chemin d'un contrat (mode géré ou non géré) |
| **PBR** | *Policy-Based Redirect* : redirige le trafic d'un contrat vers un service (FW, IPS) sans dépendre du routage |
| **Micro-segmentation** | uSeg EPG selon attributs VM |
| **Kubernetes (CNI)** | ACI CNI : un EPG par namespace/déploiement |
| **Nexus Dashboard Insights** | Analyse, télémétrie, conformité |

---

## 11. Observabilité et dépannage

### 11.1 Health score et fautes

L'APIC attribue un **health score (0-100)** à chaque objet. Les **faults** ont une sévérité : critical, major, minor, warning, info. Cycle de vie d'une faute : *soaking → raised → retaining → cleared*.

### 11.2 Outils

| Outil | Utilité |
|---|---|
| **Visore** (`https://apic/visore.html`) | Explorateur graphique du MIT |
| **EP Tracker** | Historique de mobilité d'un endpoint |
| **Atomic Counters** | Détection de pertes entre leafs |
| **Traceroute (fabric)** | Chemin leaf à leaf (`traceroute` ACI) |
| **Policy Viewer / Contract Viewer** | Visualiser les relations de contrat |
| `iping` / `itraceroute` | Ping/traceroute depuis le VRF d'un leaf |

### 11.3 Tableau de diagnostic

| Symptôme | Cause probable | Vérification |
|---|---|---|
| Nœud non découvert | LLDP/DHCP, TEP, mauvaise version | Fabric Membership, APIC logs |
| Endpoint non appris | VLAN/Domaine/AAEP incohérent, EPG non lié au port | `show endpoint`, Operational → EPG |
| Trafic EPG→EPG bloqué | Contrat absent ou filtre inexact | `show zoning-rule`, Contract Viewer |
| Subnet non joignable de l'extérieur | Scope « public » absent, BD non associé à L3Out | Config BD, `show ip route` sur border leaf |
| Passerelle ne répond pas | Unicast routing désactivé ou subnet mal défini | Config du BD |
| Fautes F0467 / F0546 | Chaîne access policies cassée | Audit AAEP/Domain/Pool |
| Conflit IP | IP dupliquée détectée (*IP Aging, duplicate IP*) | EP Tracker |

---

## 12. Bonnes pratiques et pièges d'examen

- Nommage normalisé (`TENANT-APP-EPG`, `BD-xxx`) ; utiliser le tenant **common** avec parcimonie.
- Toujours **access policies réutilisables** (une AAEP par type de serveur).
- Préférer **vzAny** + contrats ciblés plutôt que des contrats par paire d'EPG, pour économiser le TCAM.
- **Un BD ↔ un subnet** (un seul VRF) ; maintenir *Limit IP Learning* activé.
- Cluster APIC de **3 nœuds minimum** ; sauvegarde (*snapshots*, export JSON) avant chaque changement majeur.
- Tester les migrations **réseau → ACI** en mode *Network-centric* (1 EPG = 1 VLAN) avant de passer en *Application-centric*.
- **Piège :** VRF en `Enforced` bloque tout trafic inter-EPG sans contrat, y compris ICMP.
- **Piège :** les contrats ne s'appliquent pas **dans** un même EPG (sauf *Intra-EPG isolation*).
- **Piège :** la chaîne d'access policies est **par leaf** : un Switch Profile oublié = EPG « down ».

---

## 13. Aide-mémoire

| Besoin | Élément |
|---|---|
| Contrôleur | APIC (cluster ≥ 3) |
| Underlay | IS-IS ; transport VXLAN |
| Base des endpoints | COOP (spines) |
| Routes externes | MP-BGP (spines en RR) |
| Isolement admin | Tenant |
| Domaine L3 / L2 | VRF / Bridge Domain |
| Groupe de sécurité | EPG |
| Autorisation | Contrat → Subject → Filtre |
| Connectivité externe | L3Out + External EPG |
| Chaîne physique | Pool → Domain → AAEP → Policy Group → Interface/Switch Profile |
| Interrogation | `moquery`, Visore, API REST |
| Multi-datacenter | Multi-Pod (IPN) / Multi-Site (NDO, ISN) |

---

## 14. Points à retenir

1. ACI = **fabric spine-leaf** pilotée par **APIC**, configuration **déclarative**.
2. Hiérarchie : **Tenant → VRF → BD → AP → EPG** ; communication inter-EPG par **contrats**.
3. **Allow-list par défaut** : sans contrat, pas de trafic inter-EPG (VRF enforced).
4. Les **access policies** (Pool → Domain → AAEP → Policy Group → Profiles) relient les EPG aux ports physiques.
5. **Spines** : COOP et route-reflection MP-BGP ; **leafs** : VTEP, passerelle distribuée, TCAM.
6. **L3Out** + External EPG pour l'extérieur ; BD « advertised externally ».
7. **Multi-Pod** (un APIC) vs **Multi-Site** (NDO) ; automatisation par **REST, Ansible, Terraform**.
