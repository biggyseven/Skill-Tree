# MPLS & VRF — Niveau Intermédiaire

> **Objectif :** passer de la lecture d’une MPLS L3VPN à sa conception, sa configuration contrôlée et son dépannage. Ce niveau suppose les notions de base sur les labels, les rôles CE/PE/P, les VRF, les RD/RT et le principe de MP-BGP VPNv4.

## 1. Positionnement, prérequis et résultats attendus

Ce cours poursuit le niveau débutant : il ne cherche pas seulement à définir MPLS, mais à expliquer comment les éléments s’enchaînent, quels états vérifier et comment isoler une panne. À la fin, tu dois pouvoir : concevoir une petite L3VPN multi-sites, établir une matrice RD/RT cohérente, distinguer RIB globale et RIB VRF, comprendre la pile de labels, vérifier l’underlay/transport/MP-BGP séparément, choisir une méthode de routage CE–PE, contrôler les recouvrements d’adresses et diagnostiquer les pannes fréquentes.

**Prérequis :** IPv4, sous-réseaux, routes statiques, notions d’OSPF ou IS-IS, BGP de base, lecture d’une configuration IOS/IOS XE. Les commandes sont des exemples pédagogiques : la syntaxe peut différer entre IOS, IOS XE, IOS XR, NX-OS et les autres constructeurs. Vérifie toujours les capacités de la plateforme cible avant une mise en production.

### Convention de laboratoire

Le laboratoire utilise un fournisseur fictif, AS 65000, deux routeurs PE (PE1 et PE2), un routeur P et deux sites clients. Le client A utilise `10.10.0.0/16` sur le site 1 et `10.20.0.0/16` sur le site 2. Le nom de VRF sera `CLIENT-A`, le RD de PE1 `65000:101` et celui de PE2 `65000:102`. Les deux PE exportent le RT `65000:10` et importent ce même RT. Les valeurs sont réservées au labo ; ne les reprends pas telles quelles sans plan d’adressage.

## 2. Architecture de référence et responsabilités

MPLS L3VPN sépare l’apprentissage des routes client, le contrôle des routes VPN et le transport des paquets dans le cœur. Le CE échange les routes avec le PE voisin. Le PE range les routes dans la VRF correcte, les exporte au plan de contrôle VPN quand les politiques le permettent et utilise une étiquette VPN pour identifier le contexte de sortie. Le cœur transporte le paquet au moyen d’un label de transport.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-label="Architecture d’une MPLS L3VPN"><rect x="1" y="1" width="958" height="358" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Architecture d’une MPLS L3VPN</text><rect x="35" y="145" width="135" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="102.5" y="174" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">CE-A</text><text x="102.5" y="196" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Site A / LAN</text><rect x="220" y="140" width="155" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="297.5" y="169" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE1</text><text x="297.5" y="191" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">VRF + VPN label</text><rect x="405" y="125" width="150" height="120" rx="12" fill="#14243b" stroke="#5a82b1" stroke-width="2"/><text x="480.0" y="154" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">P1</text><text x="480.0" y="176" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Cœur MPLS</text><rect x="585" y="140" width="155" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="662.5" y="169" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE2</text><text x="662.5" y="191" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">VRF + VPN label</text><rect x="790" y="145" width="135" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="857.5" y="174" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">CE-B</text><text x="857.5" y="196" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Site B / LAN</text><line x1="170" y1="185" x2="220" y2="185" stroke="#6dd3ce" stroke-width="3"/><polygon points="220,185 210.0,180.0 210.0,190.0" fill="#6dd3ce"/><text x="195.0" y="172" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">IP</text><line x1="375" y1="185" x2="405" y2="185" stroke="#6dd3ce" stroke-width="3"/><polygon points="405,185 395.0,180.0 395.0,190.0" fill="#6dd3ce"/><text x="390.0" y="172" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">labels</text><line x1="555" y1="185" x2="585" y2="185" stroke="#6dd3ce" stroke-width="3"/><polygon points="585,185 575.0,180.0 575.0,190.0" fill="#6dd3ce"/><text x="570.0" y="172" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">labels</text><line x1="740" y1="185" x2="790" y2="185" stroke="#6dd3ce" stroke-width="3"/><polygon points="790,185 780.0,180.0 780.0,190.0" fill="#6dd3ce"/><text x="765.0" y="172" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">IP</text><text x="480" y="290" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#c8d7e8">PE : connaît les routes VPN ; P : commute les labels de transport.</text><text x="480" y="318" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Le cœur n’a normalement pas besoin des préfixes privés de chaque client.</text></svg>

La distinction entre PE et P est opérationnellement importante. Le PE maintient les VRF client et prend les décisions qui dépendent du service VPN. Le P commute les labels de transport selon la LFIB ; il n’a généralement pas besoin de maintenir les préfixes privés de toutes les VRF. Une panne sur le PE peut affecter une VRF ou un accès client ; une panne d’un P ou du transport peut toucher plusieurs services à la fois.

| Élément | Responsabilité principale | Vérification typique |
|---|---|---|
| CE | Routes du site client et échange CE–PE | table IP, voisinage CE–PE |
| PE | VRF, routes client, VPNv4, labels VPN | RIB VRF, BGP VPNv4, LFIB |
| P | Transport MPLS dans le cœur | IGP, LDP/SR, LFIB |
| Route Reflector (si présent) | Réduit le nombre de sessions BGP | sessions clients, familles activées |
| NMS / système de collecte | Supervision, événements, inventaire | disponibilité, horodatage, alertes |

## 3. RIB globale, RIB VRF, RIB BGP et LFIB

Un piège fréquent consiste à considérer « la route existe » comme une preuve complète de connectivité. En réalité, plusieurs tables ou bases répondent à des questions différentes :

- **RIB globale** : routes du contexte de routage par défaut, notamment la connectivité du cœur et les loopbacks des PE/P.
- **RIB de la VRF** : routes utilisables dans le contexte du client ; les préfixes d’un autre client n’y apparaissent pas automatiquement.
- **BGP VPNv4** : routes VPN annoncées avec leurs attributs, y compris le RD qui rend la NLRI unique, les RT étendus, le next-hop BGP et le label VPN associé.
- **LFIB** : associations de labels entrants aux actions de transfert (swap, pop, forwarding selon l’architecture).

Une route VPN peut exister dans la table BGP tout en étant absente de la RIB VRF si le RT n’est pas importé, si la route n’est pas admissible, si le next-hop n’est pas résolu ou si un autre chemin est préféré. À l’inverse, une route peut être installée dans une VRF mais ne pas fonctionner dans le plan de données si la pile de labels ou le chemin de retour est cassé.

### Méthode de diagnostic de la route manquante

1. Confirmer que le CE annonce ou que le PE apprend le préfixe côté VRF.
2. Vérifier que la route est présente dans la RIB de la VRF locale.
3. Examiner sa version exportée dans MP-BGP VPNv4 et ses RT.
4. Vérifier que le PE distant reçoit la route et que sa politique de VRF peut l’importer.
5. Confirmer que le next-hop VPN est résolu dans la table globale et que le transport MPLS vers ce PE est opérationnel.
6. Vérifier la LFIB / la pile de labels et le chemin retour.

## 4. Plan de contrôle : IGP, distribution des labels et MP-BGP

Une L3VPN classique assemble plusieurs fonctions indépendantes. L’IGP de cœur (par exemple OSPF ou IS-IS) rend les loopbacks des routeurs de transport joignables. Le plan de transport des labels (par exemple LDP ou SR-MPLS) permet de commuter vers les PE de sortie. MP-BGP échange les routes VPN entre les PE ou via des route reflectors. La configuration doit préserver la cohérence entre ces couches.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="340" viewBox="0 0 960 340" role="img" aria-label="Trois couches à valider séparément"><rect x="1" y="1" width="958" height="338" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Trois couches à valider séparément</text><rect x="35" y="105" width="200" height="95" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="135.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Underlay IGP</text><text x="135.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">routes des loopbacks</text><rect x="270" y="105" width="200" height="95" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="370.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">LDP / SR-MPLS</text><text x="370.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">transport label</text><rect x="505" y="105" width="200" height="95" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="605.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">MP-BGP VPNv4</text><text x="605.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">routes + label VPN</text><rect x="740" y="105" width="185" height="95" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="832.5" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VRF / CE</text><text x="832.5" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">routes client</text><line x1="235" y1="150" x2="270" y2="150" stroke="#6dd3ce" stroke-width="3"/><polygon points="270,150 260.0,145.0 260.0,155.0" fill="#6dd3ce"/><text x="252.5" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">reachability</text><line x1="470" y1="150" x2="505" y2="150" stroke="#6dd3ce" stroke-width="3"/><polygon points="505,150 495.0,145.0 495.0,155.0" fill="#6dd3ce"/><text x="487.5" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">next-hop résolu</text><line x1="705" y1="150" x2="740" y2="150" stroke="#6dd3ce" stroke-width="3"/><polygon points="740,150 730.0,145.0 730.0,155.0" fill="#6dd3ce"/><text x="722.5" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">RT import</text><text x="480" y="260" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#ff7b86">Une route VPN reçue par BGP ne garantit pas à elle seule que le chemin de données est opérationnel.</text><text x="480" y="288" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Vérifier séparément RIB VPN, next-hop, transport label et LFIB.</text></svg>

### Règle de lecture des dépendances

MP-BGP n’est pas un substitut à l’IGP du cœur. BGP peut annoncer un next-hop PE distant, mais ce next-hop doit pouvoir être résolu et atteint. LDP peut distribuer des labels pour les FEC construits à partir de l’IGP ; il ne distribue pas à lui seul les routes privées de chaque client. La VRF décide où la route client est stockée et quel ensemble de routes peut être utilisé pour le transfert.

### Boucle de validation minimale

- Loopbacks des PE présentes et joignables dans la RIB globale.
- Adjacences IGP stables et métriques attendues.
- Sessions de distribution de labels établies sur les liens concernés.
- Session MP-BGP et famille VPNv4 activées ; next-hop conservé/résolu conformément à la conception.
- VRF, RD, RT d’import/export et interfaces associées cohérents.
- Route installée dans la bonne VRF et label de service présent lorsque requis.

## 5. VRF, RD et RT : configuration réfléchie

Une VRF crée un contexte de routage distinct sur le PE. Le **RD** (Route Distinguisher) rend unique une route VPN quand plusieurs clients annoncent le même préfixe IPv4. Le **RT** (Route Target) est une communauté étendue BGP utilisée par la politique d’import/export pour déterminer quelles VRF reçoivent une route. Ils ne sont pas interchangeables.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" role="img" aria-label="RD et RT : deux fonctions distinctes"><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">RD et RT : deux fonctions distinctes</text><rect x="45" y="85" width="410" height="225" rx="12" fill="#102033" stroke="#5a82b1" stroke-width="2"/><text x="250" y="115" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#6dd3ce">RD — Route Distinguisher</text><text x="75" y="151" text-anchor="start" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#f8fafc">Préfixe local : 10.10.10.0/24</text><text x="75" y="180" text-anchor="start" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#f8fafc">RD 65010:101 + préfixe</text><text x="75" y="210" text-anchor="start" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#86e3a4">=&gt; NLRI VPNv4 unique</text><text x="75" y="245" text-anchor="start" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Rôle : différencier les routes</text><rect x="505" y="85" width="410" height="225" rx="12" fill="#102033" stroke="#5a82b1" stroke-width="2"/><text x="710" y="115" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#c6a0ff">RT — Route Target</text><text x="535" y="151" text-anchor="start" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#f8fafc">Route exportée avec RT 65010:10</text><text x="535" y="180" text-anchor="start" font-family="Arial,sans-serif" font-size="14" font-weight="400" fill="#f8fafc">VRF distante importe 65010:10 ?</text><text x="535" y="210" text-anchor="start" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#86e3a4">Oui =&gt; route candidate importée</text><text x="535" y="245" text-anchor="start" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Rôle : contrôler la distribution</text><text x="480" y="340" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#f5c46a">RD = unicité | RT = politique d’import/export</text></svg>

### Bonnes pratiques pour les RD

Dans un design opérationnel, on choisit une convention stable et documentée. Une approche fréquente utilise un identifiant propre au PE ou à l’instance et un suffixe service. L’objectif est d’éviter les collisions accidentelles entre préfixes exportés. Le RD n’est pas un mécanisme de filtrage : changer un RD ne signifie pas que l’on vient de « sécuriser » la route.

### Bonnes pratiques pour les RT

Les RT expriment des relations de distribution. Une politique simple peut utiliser un RT par VPN ; une architecture plus complexe peut séparer les RT d’export et d’import, ou appliquer plusieurs RT pour construire un modèle hub-and-spoke. La documentation doit préciser : quelles routes sont exportées, quelles VRF les importent, quelles exceptions sont autorisées et comment les modifications sont testées.

Exemple conceptuel :

| VRF | RD PE1 | RT export | RT import | But |
|---|---|---|---|---|
| CLIENT-A | `65000:101` | `65000:10` | `65000:10` | sites A interconnectés |
| CLIENT-B | `65000:201` | `65000:20` | `65000:20` | sites B isolés |
| SHARED-SVC | `65000:900` | `65000:90` | RT définis par besoin | services partagés contrôlés |

Les exemples doivent rester cohérents avec le plan réel. Un RT trop large ou importé par erreur peut étendre la portée de routes plus loin que prévu. Les RT ne remplacent ni les ACL ni les pare-feu lorsque des contrôles de sécurité applicatifs sont requis.



## 6. Recouvrement de préfixes et isolation réelle

Deux clients peuvent annoncer `10.10.0.0/16` sans entrer en collision tant que leurs routes restent dans deux VRF distinctes. L’isolation est liée au contexte de transfert et à la politique d’importation. Dès que l’on introduit le route leaking, un service partagé ou une passerelle externe, il faut réfléchir aux routes qui deviennent accessibles, au chemin retour et à la sécurité.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="365" viewBox="0 0 960 365" role="img" aria-label="VRF et recouvrement d’adresses"><rect x="1" y="1" width="958" height="363" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">VRF et recouvrement d’adresses</text><rect x="65" y="100" width="190" height="75" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="160.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">CE A</text><text x="160.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">10.1.0.0/16</text><rect x="65" y="220" width="190" height="75" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="160.0" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">CE B</text><text x="160.0" y="271" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">10.1.0.0/16</text><rect x="380" y="100" width="200" height="75" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VRF A</text><text x="480.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">table A</text><rect x="380" y="220" width="200" height="75" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="480.0" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VRF B</text><text x="480.0" y="271" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">table B</text><rect x="705" y="145" width="190" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="800.0" y="174" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE</text><text x="800.0" y="196" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">deux tables isolées</text><line x1="255" y1="137" x2="380" y2="137" stroke="#6dd3ce" stroke-width="3"/><polygon points="380,137 370.0,132.0 370.0,142.0" fill="#6dd3ce"/><line x1="255" y1="257" x2="380" y2="257" stroke="#c6a0ff" stroke-width="3"/><polygon points="380,257 370.0,252.0 370.0,262.0" fill="#c6a0ff"/><line x1="580" y1="137" x2="705" y2="175" stroke="#6dd3ce" stroke-width="3"/><polygon points="705,175 696.8866198336724,167.30759710645356 693.9780495853662,176.8752623969342" fill="#6dd3ce"/><line x1="580" y1="257" x2="705" y2="205" stroke="#c6a0ff" stroke-width="3"/><polygon points="705,205 693.8465927094212,204.22443194337035 697.687501180349,213.45738499848522" fill="#c6a0ff"/><text x="480" y="335" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f5c46a">Le même préfixe peut exister dans plusieurs VRF sans fusion automatique.</text></svg>

### Vérifier les interfaces VRF

Sur de nombreuses versions IOS XE modernes, `vrf definition` crée la VRF et l’interface est associée via `vrf forwarding`. Dans d’anciennes versions IOS, la syntaxe `ip vrf` peut être utilisée. Sur certaines plateformes, appliquer une VRF à une interface réinitialise l’adressage IP de l’interface ; il faut vérifier le comportement de la version puis remettre l’adresse dans le bon ordre.

Exemple de syntaxe moderne :

```text
vrf definition CLIENT-A
 rd 65000:101
 address-family ipv4
  route-target export 65000:10
  route-target import 65000:10
 exit-address-family
!
interface GigabitEthernet0/0/1
 description Vers CE-A
 vrf forwarding CLIENT-A
 ip address 192.0.2.1 255.255.255.252
 no shutdown
```

Les commandes de cette section sont illustratives. Les familles IPv6, l’activation BGP VPNv4, le protocole de distribution des labels, les capacités matérielles et l’ordre des commandes doivent être vérifiés dans la documentation exacte de l’image logicielle.

## 7. MP-BGP VPNv4 : ce qui est annoncé

BGP VPNv4 transporte une NLRI qui combine le RD et le préfixe IPv4. Il transporte aussi des attributs BGP — notamment les RT — et un label de service associé à la route selon le modèle de plateforme. La route VPN n’est pas juste le préfixe client isolé : ses attributs sont essentiels pour décider si elle peut être utilisée et où elle doit être importée.

### Exemple de raisonnement

Le CE-A annonce `10.10.10.0/24` à PE1. PE1 place cette route dans `CLIENT-A`, puis l’exporte dans BGP avec le RD `65000:101` et le RT `65000:10`. PE2 reçoit une route VPNv4. Si la VRF `CLIENT-A` de PE2 importe le RT `65000:10`, la route devient candidate à l’installation dans sa RIB VRF. PE2 doit également être en mesure d’atteindre le next-hop PE1 au travers du réseau de transport. L’étiquette de service permet ensuite au PE de sortie d’identifier le contexte VPN et d’effectuer le transfert attendu.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-label="Plan de contrôle : VRF, MP-BGP, RD et RT"><rect x="1" y="1" width="958" height="348" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Plan de contrôle : VRF, MP-BGP, RD et RT</text><rect x="45" y="105" width="185" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="137.5" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VRF Client A</text><text x="137.5" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">routes CE / table locale</text><rect x="280" y="105" width="185" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="372.5" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">MP-BGP VPNv4</text><text x="372.5" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">RD + RT + label VPN</text><rect x="515" y="105" width="185" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="607.5" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">MP-BGP distant</text><text x="607.5" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">réception des NLRI VPN</text><rect x="750" y="105" width="165" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="832.5" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VRF distante</text><text x="832.5" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">import si RT accepté</text><line x1="230" y1="150" x2="280" y2="150" stroke="#6dd3ce" stroke-width="3"/><polygon points="280,150 270.0,145.0 270.0,155.0" fill="#6dd3ce"/><text x="255.0" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">export</text><line x1="465" y1="150" x2="515" y2="150" stroke="#6dd3ce" stroke-width="3"/><polygon points="515,150 505.0,145.0 505.0,155.0" fill="#6dd3ce"/><text x="490.0" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">session BGP</text><line x1="700" y1="150" x2="750" y2="150" stroke="#6dd3ce" stroke-width="3"/><polygon points="750,150 740.0,145.0 740.0,155.0" fill="#6dd3ce"/><text x="725.0" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">import</text><rect x="75" y="235" width="810" height="78" rx="10" fill="#102033" stroke="#35516f" stroke-width="1"/><text x="480" y="263" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f5c46a">RD rend les NLRI VPN uniques ; RT contrôle quelles VRF importent les routes.</text><text x="480" y="288" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Le RD n’est pas une politique d’accès et le RT n’est pas un identifiant d’unicité.</text></svg>

### Route Reflectors

Dans un petit lab à deux PE, une session MP-BGP directe est facile à comprendre. Quand le nombre de PE grandit, un maillage complet BGP devient coûteux. Les route reflectors permettent de réduire le nombre de sessions en réfléchissant des routes entre clients BGP, sous réserve de respecter les politiques, les attributs et la portée de réflexion. Un RR ne devient pas automatiquement un routeur de données : dans l’architecture classique, il assure surtout un rôle de contrôle.

Lors du diagnostic, vérifie les sessions, la famille d’adresses VPNv4, les politiques d’export/import, l’existence d’un next-hop valide, la propagation des communautés étendues et la présence de la route dans la VRF distante. Une session BGP « Established » indique que la session fonctionne, pas que toutes les routes souhaitées sont annoncées et acceptées.

## 8. Pile de labels : comprendre le trafic en transit

Dans un scénario L3VPN courant à deux labels, le label externe guide le paquet à travers le cœur vers le PE de sortie. Le label interne (label VPN) identifie le service ou le contexte de sortie attendu. Le routeur P traite principalement le label supérieur ; le PE de sortie utilise le label de service selon la conception. Il existe d’autres architectures et comportements, mais ce modèle est utile pour les premiers diagnostics.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-label="Chemin de données : pile de labels"><rect x="1" y="1" width="958" height="348" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Chemin de données : pile de labels</text><rect x="45" y="120" width="180" height="100" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="135.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE ingress</text><text x="135.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">VRF lookup</text><rect x="285" y="120" width="180" height="100" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="375.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Routeur P</text><text x="375.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">swap label externe</text><rect x="525" y="120" width="180" height="100" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="615.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE egress</text><text x="615.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">retire label transport</text><rect x="765" y="120" width="150" height="100" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="840.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">CE distant</text><text x="840.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">paquet IP</text><line x1="225" y1="170" x2="285" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="285,170 275.0,165.0 275.0,175.0" fill="#6dd3ce"/><text x="255.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">push  [T,V]</text><line x1="465" y1="170" x2="525" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="525,170 515.0,165.0 515.0,175.0" fill="#6dd3ce"/><text x="495.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">swap [T′,V]</text><line x1="705" y1="170" x2="765" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="765,170 755.0,165.0 755.0,175.0" fill="#6dd3ce"/><text x="735.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">pop / PHP</text><rect x="90" y="255" width="780" height="62" rx="10" fill="#102033" stroke="#35516f" stroke-width="1"/><text x="480" y="280" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">T = label de transport ; V = label VPN (conceptuellement, pile à deux labels).</text><text x="480" y="301" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Le label VPN permet au PE de sortie de choisir le contexte de transfert VPN.</text></svg>

### Push, swap et pop

- **Push** : ajout d’un label ou d’une pile de labels à l’entrée du domaine de transport.
- **Swap** : remplacement du label supérieur par un autre label sur un saut intermédiaire.
- **Pop** : suppression du label supérieur ; la suppression peut être effectuée par le saut pénultième (PHP) selon la distribution et la configuration.

Ne déduis pas la santé du service uniquement du fait que des labels existent. Vérifie que le label correspond à la bonne FEC, que l’interface de sortie est correcte, que le next-hop est cohérent et que le PE distant possède le contexte de service associé au label VPN. La sémantique de certaines commandes `show` varie selon IOS/IOS XE/IOS XR.

## 9. Distribution des labels : LDP et options de transport

LDP distribue des associations entre FEC et labels entre routeurs compatibles. Dans les scénarios classiques, les FEC s’alignent souvent sur les routes de l’IGP. LDP nécessite une reachability IP de base entre les pairs et des interfaces correctement activées. Il ne faut pas confondre la session LDP avec l’adjacence IGP : elles peuvent échouer pour des raisons différentes.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-label="Routage CE–PE : apprentissage et propagation VPN"><rect x="1" y="1" width="958" height="348" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Routage CE–PE : apprentissage et propagation VPN</text><rect x="60" y="100" width="200" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="160.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">CE client</text><text x="160.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Réseau privé</text><rect x="380" y="100" width="200" height="80" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE fournisseur</text><text x="480.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">VRF du client</text><rect x="700" y="100" width="200" height="80" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="800.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">MP-BGP VPN</text><text x="800.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">autres PE</text><line x1="260" y1="140" x2="380" y2="140" stroke="#6dd3ce" stroke-width="3"/><polygon points="380,140 370.0,135.0 370.0,145.0" fill="#6dd3ce"/><text x="320.0" y="126" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">eBGP / OSPF / statique</text><line x1="580" y1="140" x2="700" y2="140" stroke="#6dd3ce" stroke-width="3"/><polygon points="700,140 690.0,135.0 690.0,145.0" fill="#6dd3ce"/><text x="640.0" y="126" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">export RD/RT</text><rect x="70" y="220" width="820" height="88" rx="10" fill="#102033" stroke="#35516f" stroke-width="1"/><text x="480" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f5c46a">Choisir un protocole CE–PE ne remplace pas le contrôle d’import/export VPN.</text><text x="480" y="276" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Filtrer les routes, limiter les préfixes et contrôler les annonces dans les deux sens.</text></svg>

### Vérifications LDP usuelles

Exemples de commandes Cisco souvent utiles :

```text
show mpls ldp neighbor
show mpls ldp discovery
show mpls forwarding-table
show ip route <loopback-PE-distant>
show ip cef <loopback-PE-distant> detail
```

Selon la plateforme, les noms et options peuvent changer. Il faut confirmer les voisins attendus, l’identifiant LDP, l’état des sessions, les bindings pour les FEC pertinentes et la présence des entrées de transfert. Si LDP est opérationnel mais que l’IGP converge vers un chemin inattendu, les labels suivront en général le chemin routé correspondant aux FEC apprises : le transport peut être stable tout en empruntant un chemin différent de celui imaginé.

### LDP et convergence de l’IGP

Des changements IGP peuvent modifier le prochain saut vers une loopback. La cohérence de la convergence entre le routage IP et la distribution des labels est importante ; selon la plate-forme, des mécanismes de synchronisation, de protection ou de convergence rapide peuvent réduire certains risques. Il faut les valider à l’échelle de la topologie et non activer des commandes isolées sans comprendre leurs prérequis.

## 10. Méthodes de routage CE–PE

Le CE et le PE peuvent échanger les routes au moyen de routes statiques, eBGP, OSPF ou d’autres options selon le service et la plateforme. Le choix dépend du nombre de sites, du volume de préfixes, des politiques de filtrage, de l’exploitation et des exigences de convergence.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="340" viewBox="0 0 960 340" role="img" aria-label="Routage CE–PE et propagation vers le VPN"><rect x="1" y="1" width="958" height="338" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Routage CE–PE et propagation vers le VPN</text><rect x="55" y="105" width="190" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="150.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">CE client</text><text x="150.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">route LAN</text><rect x="385" y="105" width="190" height="80" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE / VRF</text><text x="480.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">apprend les routes</text><rect x="715" y="105" width="190" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="810.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VPNv4</text><text x="810.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">annonce vers PE dist.</text><line x1="245" y1="145" x2="385" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="385,145 375.0,140.0 375.0,150.0" fill="#6dd3ce"/><text x="315.0" y="132" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">static / eBGP / OSPF</text><line x1="575" y1="145" x2="715" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="715,145 705.0,140.0 705.0,150.0" fill="#6dd3ce"/><text x="645.0" y="132" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">route + RD/RT/label</text><rect x="80" y="220" width="800" height="80" rx="10" fill="#102033" stroke="#35516f" stroke-width="1"/><text x="480" y="248" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f5c46a">Filtrer les préfixes à l’entrée et à la sortie : ne pas accepter « tout » par défaut.</text><text x="480" y="274" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">La route doit être apprise côté CE, installée dans la VRF, exportée et importée à bon escient.</text></svg>

| Méthode | Avantages | Risques / vigilance |
|---|---|---|
| Routes statiques | Simple, très contrôlable, adapté aux petits sites | Charge opérationnelle, convergence et bascule à concevoir explicitement |
| eBGP CE–PE | Contrôle des annonces, extensible, politiques BGP | Filtrage, AS-path, max-prefix, next-hop et communautés à maîtriser |
| OSPF CE–PE | Intégration dans un environnement OSPF existant | Processus/aires, redistribution et propagation d’attributs selon la conception |
| Autres protocoles pris en charge | Alignement avec l’environnement existant | Support et fonctionnalités dépendants de la version |

### Principes de filtrage

Le PE ne doit pas accepter sans limite tous les préfixes que le CE présente. Définis les préfixes autorisés, les routes par défaut acceptées ou propagées, le comportement en cas de perte du voisin et les limites de quantité. Le filtre doit être vérifié dans les deux directions. Une route par défaut inattendue ou un résumé trop large peut attirer du trafic hors du chemin prévu.

### Exemple simplifié avec eBGP

```text
router bgp 65101
 address-family ipv4
  network 10.10.0.0 mask 255.255.0.0
  neighbor 192.0.2.1 remote-as 65000
  neighbor 192.0.2.1 activate
 exit-address-family
```

Ce fragment représente un CE, pas toute la configuration VPN du PE. Sur une vraie plateforme, l’activation BGP dépend du mode de configuration et de la famille d’adresses. Ajoute des prefix-lists/route-maps, limites de préfixes et critères de politique conformes au besoin, puis teste les annonces réellement reçues.

## 11. Route leaking contrôlé et modèles hub-and-spoke

Le route leaking consiste à rendre accessibles dans une VRF certaines routes apprises dans une autre VRF. Il peut permettre d’accéder à des services partagés (DNS, DHCP, supervision, pare-feu, services d’entreprise) ou de construire une topologie hub-and-spoke. C’est une décision de conception, pas un effet implicite de MPLS.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="365" viewBox="0 0 960 365" role="img" aria-label="Route leaking : modèle hub-and-spoke"><rect x="1" y="1" width="958" height="363" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Route leaking : modèle hub-and-spoke</text><rect x="380" y="75" width="200" height="75" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="104" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VRF HUB</text><text x="480.0" y="126" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">RT export 65010:100</text><rect x="70" y="220" width="190" height="75" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="165.0" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VRF SPOKE A</text><text x="165.0" y="271" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">RT 65010:11</text><rect x="385" y="220" width="190" height="75" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="480.0" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VRF SPOKE B</text><text x="480.0" y="271" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">RT 65010:12</text><rect x="700" y="220" width="190" height="75" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="795.0" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">VRF SPOKE C</text><text x="795.0" y="271" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">RT 65010:13</text><line x1="420" y1="150" x2="200" y2="220" stroke="#6dd3ce" stroke-width="3"/><polygon points="200,220 211.04527608651736,221.73259232729683 208.0132395137479,212.20333452716423" fill="#6dd3ce"/><line x1="480" y1="150" x2="480" y2="220" stroke="#6dd3ce" stroke-width="3"/><polygon points="480,220 485.0,210.0 475.0,210.0" fill="#6dd3ce"/><line x1="540" y1="150" x2="760" y2="220" stroke="#6dd3ce" stroke-width="3"/><polygon points="760,220 751.986760486252,212.20333452716423 748.9547239134827,221.73259232729683" fill="#6dd3ce"/><text x="480" y="335" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Hub-and-spoke : le plan RT doit contrôler quelles routes le hub redistribue aux spokes.</text></svg>

### Questions à traiter avant de déployer

1. Quelle VRF exporte le préfixe et avec quels RT ?
2. Quelles VRF importent ces RT et pourquoi ?
3. Le chemin retour existe-t-il, et reste-t-il dans le même contexte de sécurité ?
4. La redistribution peut-elle introduire une boucle ou réinjecter une route dans son domaine d’origine ?
5. Les filtres de préfixes et les politiques du pare-feu correspondent-ils à l’accès réellement demandé ?
6. Comment la modification est-elle retirée rapidement en cas d’incident ?

Un design hub-and-spoke simple peut faire importer aux spokes un RT de service annoncé par le hub, tandis que les routes des spokes sont importées par le hub et ne le sont pas automatiquement par les autres spokes. Les détails exacts des RT et des communautés de sites doivent être spécifiés et testés sur la plateforme réelle. Ne copie pas des RT depuis un schéma sans établir la matrice de flux.

## 12. MTU, encapsulation et qualité de service

Une pile MPLS ajoute 4 octets par label, sans compter l’en-tête de couche 2 et les éventuels encapsulants supplémentaires (Ethernet, VLAN, PPP, tunnels ou autre transport). Si un paquet IP de 1500 octets traverse une pile de deux labels, le transport doit pouvoir absorber cette surcharge ou le domaine doit appliquer une stratégie MTU cohérente. Le comportement des paquets trop grands dépend du contexte, de DF, du protocole de couche 2 et des équipements.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-label="MTU et encapsulation MPLS"><rect x="1" y="1" width="958" height="348" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">MTU et encapsulation MPLS</text><rect x="65" y="105" width="240" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="185.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Paquet IP</text><text x="185.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">1500 octets</text><rect x="360" y="105" width="240" height="90" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="480.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Pile MPLS</text><text x="480.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">label(s) : 4 octets chacun</text><rect x="655" y="105" width="240" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="775.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Trame lien</text><text x="775.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">en-tête L2 + payload</text><line x1="305" y1="150" x2="360" y2="150" stroke="#6dd3ce" stroke-width="3"/><polygon points="360,150 350.0,145.0 350.0,155.0" fill="#6dd3ce"/><text x="332.5" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">encapsulation</text><line x1="600" y1="150" x2="655" y2="150" stroke="#f5c46a" stroke-width="3"/><polygon points="655,150 645.0,145.0 645.0,155.0" fill="#f5c46a"/><text x="627.5" y="137" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">MTU à vérifier</text><rect x="90" y="235" width="780" height="75" rx="10" fill="#102033" stroke="#35516f" stroke-width="1"/><text x="480" y="264" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Une pile de 2 labels ajoute 8 octets MPLS, hors en-têtes L2 et éventuels autres encapsulants.</text><text x="480" y="288" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">Prévoir la MTU de transport plutôt que supposer que 1500 octets passeront partout.</text></svg>

### Méthode de contrôle MTU

- Recenser MTU IP et MTU L2 sur les liens du cœur et sur les accès.
- Compter les labels maximum attendus par chemin, ainsi que tout encapsulant ajouté par le service.
- Tester avec des tailles de paquets progressives et, lorsque pertinent, DF activé.
- Vérifier ICMP « fragmentation needed » / Packet Too Big et les filtres qui pourraient les bloquer.
- Tester le vrai chemin aller-retour, pas seulement un ping local entre loopbacks.

### QoS

La QoS MPLS doit être définie de bout en bout. Les champs IP DSCP, les bits Traffic Class (TC, historiquement appelés EXP) et les politiques de chaque domaine doivent être compris. Les mappages entre DSCP et TC peuvent être configurés ; ils ne sont pas nécessairement identiques dans tous les équipements. La priorité, la réservation de bande passante et les politiques d’évitement de congestion ont des effets uniquement si elles sont appliquées et mesurées sur les points de congestion réels.

## 13. Inter-AS MPLS L3VPN : panorama de conception

Dans un scénario multi-fournisseurs ou entre domaines AS, l’échange des routes VPN et la continuité du transport sont les deux sujets centraux. Les modèles inter-AS traditionnellement décrits pour MPLS L3VPN incluent des variantes souvent appelées Option A, B et C. Ils diffèrent par ce qui est échangé à la frontière, par l’endroit où se terminent les VPN et par l’échelle et la confiance requises entre domaines.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-label="Interconnexion MPLS L3VPN entre AS"><rect x="1" y="1" width="958" height="358" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Interconnexion MPLS L3VPN entre AS</text><rect x="40" y="110" width="165" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="122.5" y="139" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">AS 65001</text><text x="122.5" y="161" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">PE-A</text><rect x="250" y="110" width="175" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="337.5" y="139" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">ASBR-A</text><text x="337.5" y="161" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">frontière AS</text><rect x="500" y="110" width="175" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="587.5" y="139" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">ASBR-B</text><text x="587.5" y="161" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">frontière AS</text><rect x="750" y="110" width="165" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="832.5" y="139" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">AS 65002</text><text x="832.5" y="161" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">PE-B</text><line x1="205" y1="155" x2="250" y2="155" stroke="#6dd3ce" stroke-width="3"/><polygon points="250,155 240.0,150.0 240.0,160.0" fill="#6dd3ce"/><text x="227.5" y="142" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">VPN routes</text><line x1="425" y1="155" x2="500" y2="155" stroke="#f5c46a" stroke-width="3"/><polygon points="500,155 490.0,150.0 490.0,160.0" fill="#f5c46a"/><text x="462.5" y="142" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">inter-AS</text><line x1="675" y1="155" x2="750" y2="155" stroke="#6dd3ce" stroke-width="3"/><polygon points="750,155 740.0,150.0 740.0,160.0" fill="#6dd3ce"/><text x="712.5" y="142" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">VPN routes</text><rect x="70" y="235" width="820" height="80" rx="10" fill="#102033" stroke="#35516f" stroke-width="1"/><text x="480" y="261" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Inter-AS Option A : VRF-to-VRF ; Option B : VPNv4 via ASBR ; Option C : PE-PE MP-BGP.</text><text x="480" y="288" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">Le choix change l’échelle, les frontières de confiance et les échanges de routes/labels.</text></svg>

- **Option A (VRF-to-VRF)** : la frontière relie des interfaces et tables VRF ; elle ressemble à un échange de routes entre CE/PE. Elle peut être simple à contrôler mais exige de maintenir des VRF de part et d’autre de la frontière.
- **Option B (ASBR VPNv4)** : les routeurs de frontière échangent des routes VPNv4/communautés conformément à la conception. Les politiques et le transport de labels doivent être précisément définis.
- **Option C (PE-PE / contrôle étendu)** : le contrôle VPN et le transport reposent sur une relation plus étendue entre PE, souvent avec des exigences de distribution de labels et de confiance différentes.

Ce cours présente le modèle conceptuel ; les détails de mise en œuvre et les variantes supportées doivent être vérifiés dans la documentation des équipements, car les comportements diffèrent entre familles logicielles. Le choix se fait selon le nombre de VPN, le degré d’administration partagée, les exigences de sécurité, l’échelle des routes et le modèle de responsabilité opérationnelle.

## 14. Haute disponibilité, convergence et scénarios de panne

La haute disponibilité d’une L3VPN ne se réduit pas à la présence de deux liens. Il faut examiner la redondance des CE/PE, du cœur, des sessions de routage, de la distribution des labels et des chemins d’alimentation/transport. Une topologie redondante peut conserver un point de défaillance commun si les deux chemins traversent le même conduit, le même routeur ou la même politique.

### Plan de test de bascule

1. Mesurer l’état initial : routes, next-hops, labels, perte, latence et trafic réel.
2. Couper un seul élément planifié (lien CE–PE, lien de cœur, voisinage IGP, session BGP selon le test).
3. Vérifier le changement de route et de LFIB, et chronométrer la convergence observée.
4. Valider les flux applicatifs et le retour, pas uniquement les pings de contrôle.
5. Restaurer le lien et contrôler qu’il n’y a pas d’instabilité persistante ou de route inappropriée.
6. Capturer les logs, les horodatages et la configuration exacte du test.

La convergence dépend de timers, de mécanismes de protection, de l’IGP, de LDP ou SR, de BGP, des capacités du matériel et de la nature de la panne. Évite de promettre une durée fixe sans test représentatif. Fast reroute, BFD, Graceful Restart et autres mécanismes ont des conditions de fonctionnement : un mécanisme qui améliore un type de panne ne protège pas nécessairement contre toutes les pannes possibles.

## 15. Sécurité opérationnelle de MPLS L3VPN

MPLS L3VPN apporte une séparation logique des routes et des contextes de transfert, mais ne chiffre pas par lui-même le trafic utilisateur. Il faut protéger les plans de contrôle et de gestion, filtrer les routes, surveiller les accès et définir explicitement les interconnexions de VRF. La sécurité doit être évaluée par les chemins possibles et non par le seul nom de service « privé ».

### Contrôles recommandés

- Authentifier et limiter les sessions de routage selon les capacités de la plateforme.
- Appliquer des filtres de préfixes, des limites de routes et des politiques cohérentes aux sessions CE–PE et MP-BGP.
- Restreindre l’accès de gestion des routeurs, protéger les identifiants et collecter les logs.
- Maintenir des versions logicielles supportées et une procédure de correction des vulnérabilités.
- Documenter les RT, les cas de route leaking, les services partagés et les frontières de confiance.
- Tester l’isolation par des sondes autorisées entre VRF, notamment après un changement de RT.
- Utiliser des mécanismes de chiffrement supplémentaires lorsque le modèle de menace exige une confidentialité cryptographique.

### Liste de contrôle avant changement RT

Avant d'ajouter un RT à une VRF, consigne le préfixe ou la famille concernée, l’exportateur, les importateurs attendus, le chemin retour, les filtres, les applications concernées, les tests négatifs (flux interdits) et le plan de retour arrière. Un RT importé dans une VRF trop large est une cause plausible d’élargissement non intentionnel de connectivité.

## 16. Laboratoire guidé : deux sites d’un même client

### 16.1 Topologie et plan d’adressage

| Lien / interface | Adresse de test | Rôle |
|---|---|---|
| CE1–PE1 | `192.0.2.0/30` | accès client site A |
| CE2–PE2 | `192.0.2.4/30` | accès client site B |
| PE1–P1 | `198.51.100.0/30` | cœur MPLS |
| P1–PE2 | `198.51.100.4/30` | cœur MPLS |
| Loopback PE1 | `10.255.0.1/32` | router-id / next-hop BGP |
| Loopback P1 | `10.255.0.2/32` | IGP / transport |
| Loopback PE2 | `10.255.0.3/32` | router-id / next-hop BGP |
| LAN site A | `10.10.0.0/16` | route cliente |
| LAN site B | `10.20.0.0/16` | route cliente |

Les valeurs utilisent des préfixes de documentation et ne sont destinées qu’à un laboratoire isolé. Vérifie que les adresses de lien et les interfaces sont adaptées à l’émulateur ou au matériel choisi.

### 16.2 Ordre de déploiement recommandé

1. Configurer les interfaces, adresses et loopbacks.
2. Mettre en place l’IGP de cœur et prouver la reachability mutuelle des loopbacks.
3. Activer le mécanisme de labels retenu sur les interfaces du cœur.
4. Vérifier les voisins et les entrées de transport.
5. Créer la VRF sur PE1 et PE2, avec des RD distincts et une politique RT cohérente.
6. Associer les interfaces CE aux VRF ; définir l’échange CE–PE choisi.
7. Configurer MP-BGP VPNv4 et activer l’échange des communautés étendues si requis par la plateforme/configuration.
8. Confirmer la présence des routes client dans la VRF distante.
9. Vérifier le transport MPLS et les labels de service.
10. Tester le trafic dans les deux sens, puis tester les scénarios négatifs.

### 16.3 Exemple de VRF sur PE

```text
vrf definition CLIENT-A
 rd 65000:101
 address-family ipv4
  route-target export 65000:10
  route-target import 65000:10
 exit-address-family
!
interface GigabitEthernet0/0/1
 description CE-A
 vrf forwarding CLIENT-A
 ip address 192.0.2.1 255.255.255.252
 no shutdown
```

Cette syntaxe est de style IOS XE moderne, mais elle n’est pas universelle. Certains IOS anciens emploient `ip vrf`; les options BGP et le support de fonctions dépendent de la version. Sur un environnement de production, utilise la procédure validée pour la plateforme précise et sauvegarde la configuration avant tout changement.

### 16.4 Exemples de commandes de vérification

```text
show ip route
show ip route vrf CLIENT-A
show ip protocols
show mpls ldp neighbor
show mpls forwarding-table
show bgp vpnv4 unicast all
show bgp vpnv4 unicast vrf CLIENT-A
show running-config | section vrf
show running-config | section router bgp
```

Le nom exact des commandes varie. Si l’une n’est pas reconnue, consulte l’aide contextuelle (`?`) et la documentation de la version installée. Ne remplace pas une commande inexistante par une commande devinée dans un environnement réel.

## 17. Méthodologie de dépannage par couches

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="330" viewBox="0 0 960 330" role="img" aria-label="Diagnostic en couches d’une panne MPLS L3VPN"><rect x="1" y="1" width="958" height="328" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Diagnostic en couches d’une panne MPLS L3VPN</text><rect x="35" y="125" width="120" height="88" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="95.0" y="154" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">1. CE–PE</text><text x="95.0" y="176" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">routes client ?</text><line x1="155" y1="169" x2="190" y2="169" stroke="#6dd3ce" stroke-width="2"/><polygon points="190,169 180.0,164.0 180.0,174.0" fill="#6dd3ce"/><rect x="190" y="125" width="120" height="88" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="250.0" y="154" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">2. VRF</text><text x="250.0" y="176" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">interface / RIB VRF ?</text><line x1="310" y1="169" x2="345" y2="169" stroke="#6dd3ce" stroke-width="2"/><polygon points="345,169 335.0,164.0 335.0,174.0" fill="#6dd3ce"/><rect x="345" y="125" width="120" height="88" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="405.0" y="154" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">3. MP-BGP</text><text x="405.0" y="176" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">VPNv4, RD/RT ?</text><line x1="465" y1="169" x2="500" y2="169" stroke="#6dd3ce" stroke-width="2"/><polygon points="500,169 490.0,164.0 490.0,174.0" fill="#6dd3ce"/><rect x="500" y="125" width="120" height="88" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="560.0" y="154" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">4. Transport</text><text x="560.0" y="176" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">next-hop / label ?</text><line x1="620" y1="169" x2="655" y2="169" stroke="#6dd3ce" stroke-width="2"/><polygon points="655,169 645.0,164.0 645.0,174.0" fill="#6dd3ce"/><rect x="655" y="125" width="120" height="88" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="715.0" y="154" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">5. LFIB</text><text x="715.0" y="176" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">label swap / PHP ?</text><line x1="775" y1="169" x2="810" y2="169" stroke="#6dd3ce" stroke-width="2"/><polygon points="810,169 800.0,164.0 800.0,174.0" fill="#6dd3ce"/><rect x="810" y="125" width="120" height="88" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="870.0" y="154" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">6. Retour</text><text x="870.0" y="176" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">chemin symétrique ?</text><text x="480" y="270" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f5c46a">Suivre le chemin par couches : ne pas corriger MP-BGP avant d’avoir validé l’underlay.</text></svg>

### Cas A — La route n’existe pas sur le PE de départ

Vérifie d’abord le réseau annoncé par le CE, l’état de l’interface, le protocole CE–PE, les filtres et la présence de la route dans la VRF locale. Si la route est uniquement connectée, vérifie que l’adresse du LAN et son masque sont corrects. Si BGP est utilisé, inspecte les routes reçues, la politique d’entrée et l’état d’annonce. Ne commence pas par MP-BGP si le PE n’a pas appris la route client.

### Cas B — La route est dans la VRF locale mais pas dans la VRF distante

Contrôle l’export VPNv4, le RD, le RT exporté, la famille d’adresses, le next-hop, les route-maps/policies et la propagation par route reflector. Sur le PE distant, vérifie la réception de la NLRI et le RT importé par la VRF. Un RT mal orthographié ou une famille non activée peut donner l’impression que « BGP fonctionne mais le VPN ne fonctionne pas ».

### Cas C — La route est présente à distance, mais le trafic ne passe pas

Vérifie la résolution du next-hop, l’IGP de cœur, la distribution de labels, la LFIB, la MTU et le chemin retour. Contrôle ensuite les ACL, pare-feu, uRPF, politique de service et éventuelles routes plus spécifiques. Les pings à partir du PE peuvent utiliser une source ou une VRF différente de celle du poste utilisateur ; sélectionne la source et la VRF de test consciemment.

### Cas D — Le trafic fonctionne dans un sens seulement

Rechercher une asymétrie d’annonce, un filtre dans un seul sens, une route par défaut différente, un route leaking incomplet ou une politique de sécurité qui n’autorise pas l’initiation du flux retour. Les tests doivent être réalisés depuis des sources contrôlées, avec des traces et des horaires connus.

## 18. Études de cas

### Étude 1 — Deux clients annoncent le même préfixe

**Situation :** CLIENT-A et CLIENT-B annoncent chacun `10.10.0.0/16`. **Analyse :** c’est prévu dans le modèle VRF ; chaque route est placée dans une table distincte. Les RD produisent des identifiants VPNv4 distincts. **Action :** vérifier que les RT ne permettent pas l’import croisé involontaire, puis tester l’isolation avec des destinations qui se recouvrent. **Erreur à éviter :** croire qu’un RD seul garantit l’isolation ; c’est surtout le contexte VRF et la politique d’import/export qui la mettent en œuvre.

### Étude 2 — Une route VPNv4 est visible, mais non installée dans la VRF

**Analyse :** la route peut être reçue dans BGP et pourtant non importée, non préférée ou non résolue. **Démarche :** comparer RT export/import, vérifier le next-hop, l’admissibilité BGP et les politiques locales. Puis vérifier la RIB VRF. **Résultat attendu :** ne corriger que la couche responsable, sans assouplir globalement les politiques.

### Étude 3 — Le service tombe après une modification IGP

**Analyse :** le changement a pu faire basculer le chemin de transport, impacter le label FEC, révéler une MTU incohérente ou rendre le next-hop non résolu. **Démarche :** comparer l’IGP, la LFIB et le trafic réel avant/après, vérifier les timers et la synchronisation disponible, puis revenir sur la modification si elle a dépassé le risque autorisé.

### Étude 4 — Route leaking trop large

**Analyse :** un RT partagé ou importé dans plusieurs VRF a étendu l’accès à des préfixes inattendus. **Démarche :** établir les RT réellement annoncés, identifier les VRF importatrices, retirer l’import non autorisé conformément au plan de changement et tester les flux négatifs. **Prévention :** matrice des flux, revue à deux personnes, tests avant/après et surveillance des changements de route.

### Étude 5 — Petits paquets OK, applications lentes ou bloquées

**Analyse :** la connectivité IP de base ne confirme pas que la MTU et la QoS sont correctes. Des paquets plus grands peuvent échouer, les messages ICMP nécessaires peuvent être filtrés ou le chemin peut avoir des pertes en congestion. **Démarche :** tester les tailles de paquets, contrôler MTU/DF/ICMP, mesurer pertes et latence sur le chemin réel, puis observer les files et politiques QoS aux points de congestion.

## 19. Exercices corrigés

**Exercice 1.** Quel élément rend une route VPNv4 unique lorsque deux clients annoncent `10.10.0.0/16` ?  
**Réponse :** le RD associé au préfixe forme une NLRI VPNv4 distincte. La séparation opérationnelle des clients reste liée aux VRF et aux politiques d’import/export.

**Exercice 2.** Pourquoi un RT n’est-il pas la même chose qu’un RD ?  
**Réponse :** le RD sert à l’unicité de la route VPN ; le RT est une communauté étendue qui guide l’importation et l’exportation des routes dans les VRF.

**Exercice 3.** MP-BGP est Established ; le site distant n’apprend pas le préfixe. Cite quatre pistes.  
**Réponse :** famille VPNv4 non activée, route non exportée, RT manquant ou non importé, route rejetée par une policy, next-hop/non-admissibilité selon la plateforme ou propagation RR incorrecte.

**Exercice 4.** Le PE distant voit la route mais le trafic ne traverse pas le cœur. Quelle couche valider d’abord ?  
**Réponse :** vérifier la résolution du next-hop dans l’underlay et la disponibilité du transport label/LFIB, puis la pile de labels, la MTU et le chemin retour.

**Exercice 5.** Deux VRF importent un RT commun. Quel est le risque ?  
**Réponse :** les routes associées à ce RT peuvent être importées dans les deux VRF, selon les autres politiques. Cela peut provoquer un élargissement de connectivité involontaire ; il faut valider la matrice de flux.

**Exercice 6.** Pourquoi un ping depuis le PE peut-il réussir alors que le poste client échoue ?  
**Réponse :** le ping peut utiliser la RIB globale, une source ou une VRF différente ; le retour peut manquer, ou des filtres/ACL/pare-feu peuvent agir différemment pour le vrai flux client.

## 20. Quiz final

1. Quel est le rôle de la VRF sur le PE ?
2. Quelle est la différence entre la RIB globale et la RIB VRF ?
3. Quel attribut sert à rendre unique une route VPNv4 ?
4. Quel attribut guide l’import/export des routes VPN ?
5. Pourquoi faut-il une reachability IP de l’underlay ?
6. Quelle différence y a-t-il entre MP-BGP et LDP ?
7. Que fait le label de transport dans une pile de deux labels ?
8. Pourquoi une route visible dans BGP peut-elle être absente de la VRF ?
9. Quels éléments faut-il vérifier pour une panne unidirectionnelle ?
10. Pourquoi MPLS L3VPN n’est-il pas à lui seul du chiffrement ?

### Corrigé

1. Maintenir une table de routage et un contexte de transfert séparés pour un service ou client.
2. La RIB globale porte les routes du contexte par défaut ; une RIB VRF contient les routes utilisables dans cette VRF.
3. Le RD associé au préfixe IPv4 forme la NLRI VPNv4 unique.
4. Le RT, via une communauté étendue BGP, pilote les politiques d’import/export.
5. Les PE et le mécanisme de transport doivent pouvoir atteindre le next-hop de la route VPN.
6. MP-BGP échange les routes VPN et leurs attributs ; LDP distribue les bindings de labels pour le transport dans les architectures qui l’utilisent.
7. Il dirige le paquet à travers le cœur vers le PE de sortie ; le label de service interne identifie ensuite le contexte VPN de sortie selon la conception.
8. RT absent, famille/policy, next-hop non résolu, chemin non admissible ou priorité d’un autre chemin peuvent expliquer la différence.
9. Chemin retour, filtres, route par défaut, RT/route leaking, ACL/pare-feu, source de test et asymétrie de routage.
10. MPLS fournit transport et séparation logique ; le chiffrement doit être assuré par un mécanisme distinct lorsque requis.

## 21. Checklist de mise en production

- [ ] Plan d’adressage, loopbacks, AS et conventions RD/RT approuvés.
- [ ] IGP stable et reachability des loopbacks PE/P validée.
- [ ] LDP ou SR-MPLS configuré conformément au design et vérifié sur tous les sauts nécessaires.
- [ ] MP-BGP/route reflectors et familles VPN correctement activés.
- [ ] VRF et interfaces associées aux bons CE ; routes filtrées dans les deux sens.
- [ ] Matrice RT d’import/export et cas de route leaking validés.
- [ ] RIB VRF, next-hop, label VPN, LFIB et tests de trafic conformes.
- [ ] MTU, QoS, convergence et chemin retour mesurés.
- [ ] Journalisation, supervision, sauvegarde et rollback documentés.
- [ ] Tests négatifs prouvant que les routes et flux interdits restent interdits.

## 22. Glossaire

- **CE :** Customer Edge, routeur côté client.
- **PE :** Provider Edge, routeur fournisseur qui héberge les VRF.
- **P :** routeur de cœur fournisseur.
- **VRF :** contexte de routage et de transfert virtuel.
- **RD :** Route Distinguisher, utilisé pour rendre unique la NLRI VPN.
- **RT :** Route Target, communauté étendue BGP utilisée dans les politiques d’import/export.
- **MP-BGP VPNv4 :** famille BGP transportant les routes VPN IPv4 et leurs attributs.
- **LDP :** protocole de distribution des labels MPLS.
- **LFIB :** base utilisée pour transférer les paquets labellisés.
- **FEC :** Forwarding Equivalence Class, ensemble de paquets traités de manière équivalente.
- **PHP :** Penultimate Hop Popping, retrait du label supérieur par le saut pénultième.
- **RT import/export :** règles qui déterminent quels préfixes VPN sont distribués vers quelles VRF.

## 23. Références techniques

- IETF, [RFC 4364 — BGP/MPLS IP Virtual Private Networks (VPNs)](https://datatracker.ietf.org/doc/html/rfc4364).
- IETF, [RFC 3031 — Multiprotocol Label Switching Architecture](https://datatracker.ietf.org/doc/html/rfc3031).
- Cisco, [MPLS Layer 3 VPN Configuration Guide — IOS XE](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/mpls/mpls-configuration-guide/mpls-layer-3-vpn.html).
- Cisco, [MPLS Label Distribution Protocol — IOS XE](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/mpls/mpls-configuration-guide/mpls-label-distribution-protocol.html).

> **Rappel d’exploitation :** les extraits CLI sont des modèles d’apprentissage et ne remplacent pas la documentation de la version exacte. Vérifie les prérequis, les syntaxes disponibles, les fonctionnalités matérielles, le comportement de convergence et les procédures de retour arrière avant toute modification réelle.
