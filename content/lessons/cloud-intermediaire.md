<style>
.cloudm-diagram{width:100%;max-width:100%;overflow-x:auto;margin:1.25rem 0;padding:.75rem;border:1px solid #1b3854;border-radius:14px;background:#07111e;color:#e5edf8;box-sizing:border-box}
.cloudm-diagram svg{display:block;width:100%;height:auto;min-width:700px}
@media(max-width:720px){.cloudm-diagram svg{min-width:720px}}
@media(prefers-reduced-motion:reduce){.cloudm-diagram *{animation:none!important}}
</style>

# Cloud Networking — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Prérequis :** adressage IPv4/IPv6, CIDR, routage de base, DNS, TCP/UDP et notions de pare-feu.  
**Objectif :** concevoir, connecter, sécuriser et dépanner une architecture réseau cloud composée de plusieurs sous-réseaux, environnements, zones et réseaux distants.

Le cloud networking ne se limite pas à créer un réseau virtuel et à autoriser le port 443. Dans une architecture réelle, il faut choisir comment les réseaux communiquent, comment les routes sont propagées, comment les flux sont filtrés, comment les services sont consommés sans exposition publique, et comment l’équipe observe et dépanne le trafic. Ce cours passe des notions de base à la conception d’architectures intermédiaires réutilisables.

Les noms des services varient selon les fournisseurs. AWS utilise notamment les VPC, les VPC endpoints et Transit Gateway ; Microsoft Azure propose les Virtual Networks (VNet), le peering et Private Link ; Google Cloud utilise les VPC networks, le peering, Cloud NAT, Cloud VPN et Private Service Connect. Ces services ont des fonctions proches, mais leurs comportements, restrictions, tarifs et règles de routage ne sont pas parfaitement identiques. Les exemples ci-dessous sont donc conceptuels, sauf lorsqu’un fournisseur est explicitement nommé.

> **Analogie :** au niveau débutant, tu as appris à dessiner une route entre deux bâtiments. Au niveau intermédiaire, tu dessines le plan de circulation d’une ville : voies principales, sens uniques, échangeurs, tunnels, péages, zones à accès restreint et équipements de contrôle. Une flèche indique le sens d’un trajet possible, mais seule la signalisation et l’état réel des voies permettent de savoir si le trajet est autorisé.


## 1. Revoir les fondations avant de concevoir

### 1.1 Plan d’adressage : une décision d’architecture

Les plages IP ne sont pas un détail que l’on peut improviser après le déploiement. Elles affectent le peering, les VPN, les interconnexions, la segmentation, les migrations et parfois les services managés. Avant de créer plusieurs VPC/VNet, établis un plan qui identifie les propriétaires et les usages des plages.

Exemple pédagogique :

| Domaine réseau | Préfixe IPv4 d’exemple | Objectif |
|---|---|---|
| VPC/VNet partagé | `10.40.0.0/16` | Services communs |
| Production applicative | `10.41.0.0/16` | Charges de production |
| Environnement de test | `10.42.0.0/16` | Tests et préproduction |
| Réseau d’entreprise | `172.20.0.0/16` | LAN et centres de données |
| Services de sécurité | `10.43.0.0/16` | Inspection et collecte centralisées |

Ces blocs sont fictifs. Ils doivent être remplacés après inventaire des plages réellement utilisées. Ne choisis pas une plage parce qu’elle est populaire sur Internet : vérifie que tes sites, VPN utilisateurs, partenaires, conteneurs, services managés et filiales ne l’utilisent pas déjà.

#### Pourquoi les chevauchements sont difficiles

Supposons que le VPC A et le réseau local utilisent tous deux `10.10.0.0/16`. Si une machine du cloud tente de joindre `10.10.5.20`, le routeur ne peut pas déduire de l’adresse seule si la destination est locale ou distante. La route la plus spécifique peut détourner le trafic vers le réseau inattendu. Des solutions de contournement, telles que la traduction d’adresses ou un redesign, sont possibles, mais elles augmentent la complexité et les risques.

### 1.2 CIDR et capacité réelle

Pour IPv4, la taille mathématique d’un bloc est \(2^{32-p}\), où \(p\) est la longueur du préfixe. Un `/24` contient donc 256 adresses théoriques, et un `/20` en contient 4096. La capacité utilisable dépend toutefois des réservations, de l’architecture et des quotas du fournisseur.

Ne dimensionne pas les sous-réseaux uniquement à partir du nombre actuel de machines. Prévois :
- l’augmentation des instances et des interfaces ;
- les déploiements temporaires et les mises à jour progressives ;
- les services qui consomment plusieurs adresses ;
- les plages de pods et de services si Kubernetes est utilisé ;
- les futures interconnexions et les besoins de migration.

Kubernetes mérite une attention particulière : l’espace des nœuds, les adresses des pods et celles des services peuvent être gérés différemment selon le réseau de conteneurs choisi. Une plage de pods qui chevauche un VPN ou un réseau distant peut provoquer des problèmes de connectivité difficiles à diagnostiquer.

### 1.3 La connectivité est une chaîne de conditions

Pour qu’un flux fonctionne, plusieurs conditions doivent être satisfaites au même moment :
1. l’application utilise la bonne destination et le bon protocole ;
2. le nom est résolu correctement, si une résolution DNS est utilisée ;
3. les routes dirigent les paquets vers la bonne cible ;
4. les règles réseau et pare-feu autorisent le flux ;
5. les contrôles du système invité ou du service n’interdisent pas la connexion ;
6. le service cible écoute et sait traiter la requête ;
7. le chemin de retour fonctionne ;
8. les contrôles d’identité, TLS et applicatifs acceptent la demande.

Une route présente ne signifie pas que le flux est autorisé. Une règle autorisante ne crée pas une route manquante. Un test TCP réussi ne garantit pas que l’application retourne le résultat attendu.

## 2. Modèle réseau d’un déploiement multi-zone

### 2.1 Réseau virtuel, région et zone

Un réseau virtuel peut s’étendre sur plusieurs zones ou être défini différemment selon le fournisseur. Les sous-réseaux, les passerelles, les services d’équilibrage et les adresses peuvent avoir des contraintes de portée régionales ou zonales.

Pour une application critique, répartir les cibles sur plusieurs zones permet de réduire certaines pannes communes. Mais la présence d’instances dans deux zones ne garantit pas à elle seule la haute disponibilité. Il faut examiner :
- le point d’entrée public ou privé ;
- le comportement du répartiteur de charge ;
- la réplication et le quorum de la base de données ;
- les dépendances régionales ;
- la capacité restante si une zone disparaît ;
- le mécanisme de bascule et son délai ;
- la sauvegarde et la restauration.

### 2.2 Sous-réseaux séparés par fonction

Une segmentation courante sépare l’entrée, l’application, les données et les services d’exploitation. Cette séparation facilite l’écriture des règles et la lecture des flux. Elle ne doit pas être assimilée à une barrière magique : toutes les routes, les interfaces, les politiques et les services doivent respecter cette séparation.

| Zone logique | Entrées typiques | Sorties typiques | Point d’attention |
|---|---|---|---|
| Entrée publique | HTTPS depuis les clients | Application ou cibles internes | Exposition réduite |
| Application privée | Flux depuis l’entrée ou les services autorisés | Base, API et services requis | Pas de port d’administration ouvert à Internet |
| Données privées | Requêtes depuis les serveurs autorisés | Réplication, sauvegarde ou supervision | Aucun accès public direct |
| Administration | VPN, bastion ou accès contrôlé | Interfaces d’administration ciblées | MFA, traçabilité, moindre privilège |
| Inspection/sécurité | Flux dérivés ou routés selon l’architecture | Sortie autorisée ou systèmes d’analyse | Capacité et symétrie de routage |

### Schéma 1 — Application multi-zone, flux client et chemins internes

<div class="cloudm-diagram">
<svg viewBox="0 0 1000 475" width="100%" role="img" aria-label="Architecture cloud multi-zone avec client, passerelle, répartiteur, serveurs applicatifs, base de données et flèches de flux" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="cm1blue" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker>
<marker id="cm1green" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker>
<marker id="cm1amber" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#fbbf24"/></marker>
<style>.cm1t{font:14px Arial,sans-serif;fill:#e5edf8}.cm1s{font:12px Arial,sans-serif;fill:#a9bdd5}.cm1flow{fill:none;stroke:#34d399;stroke-width:3;stroke-dasharray:9 6;marker-end:url(#cm1green);animation:cm1dash 1.7s linear infinite}@keyframes cm1dash{to{stroke-dashoffset:-30}}</style>
</defs>
<rect x="20" y="170" width="130" height="80" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.7"/>
<circle cx="85" cy="194" r="12" fill="none" stroke="#38bdf8" stroke-width="2"/><path d="M65 222 Q85 202 105 222" fill="none" stroke="#38bdf8" stroke-width="2"/>
<text x="85" y="239" class="cm1t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Client</text>
<rect x="190" y="170" width="135" height="80" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.7"/>
<circle cx="257" cy="196" r="16" fill="none" stroke="#38bdf8" stroke-width="2"/><path d="M241 196 H273 M257 180 C247 189 247 203 257 212 M257 180 C267 189 267 203 257 212 M244 186 H270 M244 206 H270" fill="none" stroke="#38bdf8" stroke-width="1.5"/>
<text x="257" y="232" class="cm1t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Internet</text>
<path d="M150 210 H185" class="cm1flow" stroke-width="3" marker-end="url(#cm1green)" stroke="#34d399" fill="none" stroke-dasharray="9 6"/><path d="M190 229 H155" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#cm1blue)"/>
<rect x="365" y="155" width="155" height="110" rx="14" fill="#211d3a" stroke="#a78bfa" stroke-width="1.8"/>
<path d="M390 190 L410 178 L430 190 L410 202 Z M390 190 V214 L410 226 L430 214 V190 M410 202 V226" fill="none" stroke="#c4b5fd" stroke-width="2"/>
<text x="465" y="187" class="cm1t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">WAF / LB</text><text x="465" y="208" class="cm1s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Entrée HTTPS</text><text x="465" y="230" class="cm1s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Cibles saines</text>
<path d="M325 210 H360" class="cm1flow" stroke-width="3" marker-end="url(#cm1green)" stroke="#34d399" fill="none" stroke-dasharray="9 6"/>
<rect x="560" y="35" width="410" height="385" rx="18" fill="#0a1727" stroke="#60a5fa" stroke-width="2" stroke-dasharray="7 5"/><text x="765" y="60" class="cm1t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">VPC / VNet</text>
<rect x="580" y="75" width="180" height="170" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.4"/><text x="670" y="99" class="cm1t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Zone A</text>
<rect x="780" y="75" width="170" height="170" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.4"/><text x="865" y="99" class="cm1t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Zone B</text>
<rect x="600" y="122" width="140" height="85" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="615" y="137" width="22" height="20" rx="2" fill="none" stroke="#34d399" stroke-width="2"/><path d="M615 144 H637 M620 151 H632" stroke="#34d399" stroke-width="1.5"/><text x="670" y="174" class="cm1t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">App A</text><text x="670" y="192" class="cm1s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Privée</text>
<rect x="800" y="122" width="130" height="85" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="815" y="137" width="22" height="20" rx="2" fill="none" stroke="#34d399" stroke-width="2"/><path d="M815 144 H837 M820 151 H832" stroke="#34d399" stroke-width="1.5"/><text x="865" y="174" class="cm1t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">App B</text><text x="865" y="192" class="cm1s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Privée</text>
<path d="M520 190 H555 V164 H595" class="cm1flow" stroke-width="3" marker-end="url(#cm1green)" stroke="#34d399" fill="none" stroke-dasharray="9 6"/><path d="M740 164 H795" class="cm1flow" stroke-width="3" marker-end="url(#cm1green)" stroke="#34d399" fill="none" stroke-dasharray="9 6"/>
<rect x="640" y="285" width="260" height="92" rx="12" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.6"/>
<ellipse cx="675" cy="313" rx="16" ry="6" fill="none" stroke="#fbbf24" stroke-width="2"/><path d="M659 313 V344 C659 353 691 353 691 344 V313 M659 329 C659 338 691 338 691 329" fill="none" stroke="#fbbf24" stroke-width="2"/>
<text x="785" y="317" class="cm1t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Base de données</text><text x="785" y="340" class="cm1s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Sous-réseau privé</text><text x="785" y="359" class="cm1s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Entrée limitée à l’app</text>
<path d="M670 207 V270 H720 V280" class="cm1flow" stroke-width="3" marker-end="url(#cm1green)" stroke="#34d399" fill="none" stroke-dasharray="9 6"/><path d="M865 207 V260 H850 V280" class="cm1flow" stroke-width="3" marker-end="url(#cm1green)" stroke="#34d399" fill="none" stroke-dasharray="9 6"/>
<text x="20" y="315" class="cm1s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Flèches vertes : flux métier</text><path d="M20 337 H95" class="cm1flow" stroke-width="3" marker-end="url(#cm1green)" stroke="#34d399" fill="none" stroke-dasharray="9 6"/><text x="20" y="377" class="cm1s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Chaque flux exige</text><text x="20" y="395" class="cm1s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">route + règles compatibles.</text><text x="560" y="452" class="cm1s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Flux privés vers la base ; aucune entrée Internet directe.</text>
<circle r="4.5" fill="#bbf7d0"><animateMotion dur="2.1s" repeatCount="indefinite" path="M150 210 L185 210"/></circle><circle r="4" fill="#bbf7d0"><animateMotion dur="2.8s" repeatCount="indefinite" path="M520 190 L555 190 L555 164 L595 164"/></circle></svg>
</div>

Les flèches principales indiquent le sens logique de la requête. Les réponses reviennent via les mécanismes réseau associés au service et aux règles de filtrage. Dans une architecture réelle, les noms des ressources et leurs chemins exacts dépendent du répartiteur et du fournisseur.

## 3. Tables de routage : destination, cible et propagation

### 3.1 Table de routage par sous-réseau ou ressource

Une route associe généralement un préfixe de destination à un prochain saut ou une cible. Selon la plateforme, les routes peuvent être définies au niveau du réseau, associées à des sous-réseaux, propagées par un VPN/BGP ou fournies automatiquement par le système.

Exemple de lecture conceptuelle :

| Destination | Cible | Intention |
|---|---|---|
| `10.41.0.0/16` | Route locale | Ressources du VPC de production |
| `10.40.0.0/16` | Peering ou hub | Services partagés |
| `172.20.0.0/16` | VPN / passerelle hybride | Réseau d’entreprise |
| `0.0.0.0/0` | NAT ou sortie contrôlée | Trafic IPv4 externe autorisé |
| `::/0` | Cible IPv6 adaptée | Trafic IPv6 externe autorisé |

Ce tableau est un modèle, pas une configuration copiée telle quelle. La présence d’une route par défaut vers un NAT ou une passerelle ne suffit pas si les règles de sortie, la traduction, les politiques de sécurité ou les restrictions du service empêchent le trafic.

### 3.2 Route la plus spécifique

Dans de nombreux modèles de routage IP, lorsque plusieurs routes applicables existent, la route ayant le préfixe de destination le plus spécifique est privilégiée. Par exemple, `10.40.3.0/24` décrit une plage plus précise que `10.40.0.0/16`. L’ordre exact entre familles de routes, priorités explicites, routes de politique et routes système dépend cependant du fournisseur.

Il faut distinguer :
- la **priorité administrative** de certaines routes, définie par le service ;
- la **spécificité du préfixe** ;
- les **routes spéciales ou système** ;
- les **règles de filtrage**, qui ne choisissent pas la route mais peuvent bloquer le paquet.

### 3.3 Routage statique et dynamique

Une route statique est configurée explicitement. Elle est utile pour des architectures simples et prévisibles. Le routage dynamique permet d’apprendre ou d’annoncer des préfixes via un protocole comme BGP. Il devient important dans les environnements hybrides ou multi-sites avec plusieurs chemins.

BGP peut faciliter la propagation et le basculement des routes, mais il ne remplace pas la conception. Les annonces doivent être filtrées, les préfixes contrôlés, les chemins redondants testés et les changements surveillés. Une annonce trop large ou incorrecte peut détourner le trafic.

### 3.4 Routage asymétrique et équipements d’inspection

Un chemin est asymétrique lorsque le trafic aller et retour passent par des chemins différents. Certains scénarios le tolèrent, mais des pare-feu à état, des appliances d’inspection ou des équipements NAT peuvent échouer si le retour contourne le composant qui a enregistré la session.

Avant d’insérer une appliance virtuelle (NVA) dans un chemin, détermine :
- comment le trafic entrant la rejoint ;
- comment le trafic de retour repasse par elle ;
- si le routage source/destination ou la transmission IP doit être activé ;
- comment la panne de l’appliance est gérée ;
- si les contrôles de santé et la haute disponibilité sont configurés ;
- où se trouvent les routes de chaque côté.

### Schéma 2 — Une décision de routage avec trois destinations

<div class="cloudm-diagram">
<svg viewBox="0 0 980 365" width="100%" role="img" aria-label="Routeur virtuel et table de routage avec trois chemins directionnels vers Internet, réseau partagé et site local" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="cm2b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="cm2g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><marker id="cm2y" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#fbbf24"/></marker><style>.cm2t{font:14px Arial,sans-serif;fill:#e5edf8}.cm2s{font:12px Arial,sans-serif;fill:#a9bdd5}.cm2f{fill:none;stroke-width:3;stroke-dasharray:8 6;animation:cm2dash 1.6s linear infinite}@keyframes cm2dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="130" width="170" height="95" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.7"/><rect x="42" y="150" width="30" height="30" rx="4" fill="none" stroke="#38bdf8" stroke-width="2"/><path d="M42 160 H72 M48 170 H66" stroke="#38bdf8" stroke-width="2"/><text x="122" y="164" text-anchor="middle" class="cm2t" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">VM source</text><text x="122" y="185" text-anchor="middle" class="cm2s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">10.41.2.20</text><text x="105" y="207" text-anchor="middle" class="cm2s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Paquet IP sortant</text>
<path d="M190 177 H252" stroke="#38bdf8" stroke-width="3" fill="none" marker-end="url(#cm2b)"/>
<rect x="255" y="72" width="265" height="220" rx="14" fill="#111d30" stroke="#a78bfa" stroke-width="1.8"/><text x="387" y="98" class="cm2t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Table de routage</text><path d="M275 111 H500" stroke="#394968"/><text x="276" y="137" class="cm2s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">10.40.0.0/16 → hub</text><text x="276" y="166" class="cm2s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">172.20.0.0/16 → VPN</text><text x="276" y="195" class="cm2s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">0.0.0.0/0 → NAT</text><text x="276" y="241" class="cm2s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Destination</text><text x="276" y="260" class="cm2s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">+ cible / next hop</text>
<path d="M520 140 H575 V55 H630" class="cm2f" stroke="#34d399" marker-end="url(#cm2g)"/><path d="M520 180 H630" class="cm2f" stroke="#fbbf24" marker-end="url(#cm2y)"/><path d="M520 225 H575 V310 H630" class="cm2f" stroke="#38bdf8" marker-end="url(#cm2b)"/>
<rect x="630" y="24" width="310" height="65" rx="11" fill="#0d2a27" stroke="#34d399" stroke-width="1.6"/><text x="785" y="50" class="cm2t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Services partagés</text><text x="785" y="71" class="cm2s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">10.40.0.0/16 — chemin privé</text>
<rect x="630" y="145" width="310" height="65" rx="11" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.6"/><text x="785" y="171" class="cm2t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Réseau d’entreprise</text><text x="785" y="192" class="cm2s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">172.20.0.0/16 — VPN</text>
<rect x="630" y="276" width="310" height="65" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="785" y="302" class="cm2t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Sortie Internet</text><text x="785" y="323" class="cm2s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">NAT ou chemin externe autorisé</text>
<text x="20" y="345" class="cm2s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Les flèches partent de la source et montrent le prochain saut logique. Contrôler aussi les routes de retour.</text><circle r="4.5" fill="#bfdbfe"><animateMotion dur="2.1s" repeatCount="indefinite" path="M190 177 L252 177"/></circle><circle r="4" fill="#bbf7d0"><animateMotion dur="2.7s" repeatCount="indefinite" path="M520 140 L575 140 L575 55 L630 55"/></circle></svg>
</div>

Le schéma illustre la logique de sélection des cibles. Il ne représente pas nécessairement un routeur physique : dans de nombreux environnements cloud, le routage est implémenté de façon distribuée.

## 4. Contrôles de sécurité : groupes, ACL et pare-feu centralisé

### 4.1 Règles avec état et sans état

Un mécanisme **avec état** suit les sessions ou connexions. Dans de nombreux groupes de sécurité cloud, une réponse liée à une connexion autorisée est permise automatiquement. Un mécanisme **sans état** évalue chaque paquet selon les règles correspondantes : le trafic retour peut exiger des autorisations distinctes.

Les noms des fonctionnalités ne suffisent pas. Lis la documentation de la ressource exacte : les groupes de sécurité, les ACL de sous-réseau, les politiques de pare-feu distribuées et les appliances réseau n’appliquent pas nécessairement leurs règles au même niveau.

### 4.2 Concevoir des règles par flux

Évite de commencer par une liste de ports universelle. Commence par dessiner les communications réellement nécessaires. Pour chaque flux, documente la source, la destination, le protocole, le port, le propriétaire métier et la justification.

| Source | Destination | Flux | Politique attendue |
|---|---|---|---|
| Clients Internet | Point d’entrée public | TCP 443 | Autoriser si le service est public |
| Point d’entrée | Serveurs applicatifs | Port applicatif précis | Autoriser uniquement les cibles requises |
| Serveurs applicatifs | Base de données | Port DB exact | Autoriser uniquement les groupes applicatifs |
| Serveurs privés | Service de mises à jour | HTTPS sortant via chemin contrôlé | Autoriser selon besoin |
| Poste d’administration | Bastion / accès géré | Canal d’administration approuvé | Authentification forte + journalisation |
| Internet | Base de données privée | Tout accès direct non prévu | Refuser / ne pas exposer |

Ces règles sont des intentions de conception. Dans le fournisseur choisi, transpose-les en groupes de sécurité, ACL, politiques distribuées et règles de système invité appropriés.

### 4.3 Défense en profondeur

Plusieurs couches peuvent intervenir :
- groupes de sécurité attachés aux interfaces ou ressources ;
- ACL réseau associées aux sous-réseaux ;
- pare-feu central ou appliances de sécurité ;
- pare-feu local de la machine ;
- WAF pour certains flux HTTP ;
- mécanismes d’identité et d’autorisation applicatifs ;
- authentification mutuelle ou TLS ;
- télémétrie et alertes.

Les couches ne sont pas toutes redondantes. Le WAF inspecte un niveau applicatif HTTP ; la table de routage choisit le chemin ; le groupe de sécurité autorise ou refuse des flux réseau. Une seule couche ne remplace pas les autres.

### 4.4 Journaliser les décisions de sécurité

Active les journaux adaptés lorsque tu dois analyser les flux acceptés ou rejetés. Un journal peut fournir des adresses source/destination, des ports, un protocole, une interface et une action, selon le produit. Il ne montre pas forcément la charge utile. Protège les journaux contre l’altération, limite leur accès et choisis une rétention cohérente avec les exigences de sécurité et de conformité.

### Schéma 3 — Plusieurs couches de contrôle

<div class="cloudm-diagram">
<svg viewBox="0 0 1000 340" width="100%" role="img" aria-label="Client traversant plusieurs contrôles réseau jusqu'au service privé avec flèches directionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="cm3b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="cm3g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.cm3t{font:13px Arial,sans-serif;fill:#e5edf8}.cm3s{font:11px Arial,sans-serif;fill:#a9bdd5}.cm3f{stroke:#34d399;stroke-width:3;fill:none;stroke-dasharray:8 6;marker-end:url(#cm3g);animation:cm3dash 1.4s linear infinite}@keyframes cm3dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="120" width="130" height="78" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="85" y="148" class="cm3t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">Client</text><text x="85" y="169" class="cm3s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">HTTPS</text>
<rect x="190" y="100" width="150" height="118" rx="11" fill="#211d3a" stroke="#a78bfa" stroke-width="1.5"/><path d="M220 126 H310 V150 H220 Z M230 136 H300 M230 144 H300" fill="none" stroke="#c4b5fd" stroke-width="1.5"/><text x="265" y="175" class="cm3t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">WAF / LB</text><text x="265" y="195" class="cm3s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">HTTP(S)</text>
<rect x="380" y="100" width="150" height="118" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><path d="M405 126 L430 116 L455 126 V148 L430 158 L405 148 Z M430 116 V158" fill="none" stroke="#38bdf8" stroke-width="1.5"/><text x="455" y="175" class="cm3t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">Pare-feu réseau</text><text x="455" y="195" class="cm3s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Source / port</text>
<rect x="570" y="100" width="150" height="118" rx="11" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="610" y="120" width="70" height="35" rx="4" fill="none" stroke="#34d399" stroke-width="1.5"/><path d="M610 131 H680 M622 141 H668" stroke="#34d399" stroke-width="1.5"/><text x="645" y="175" class="cm3t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">Serveur app</text><text x="645" y="195" class="cm3s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Auth applicative</text>
<rect x="760" y="100" width="210" height="118" rx="11" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><ellipse cx="805" cy="128" rx="16" ry="6" fill="none" stroke="#fbbf24" stroke-width="1.7"/><path d="M789 128 V151 C789 160 821 160 821 151 V128 M789 139 C789 148 821 148 821 139" fill="none" stroke="#fbbf24" stroke-width="1.7"/><text x="877" y="140" class="cm3t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">Base de données</text><text x="877" y="164" class="cm3s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Port dédié</text><text x="877" y="184" class="cm3s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Réseau privé</text>
<path d="M150 158 H185" class="cm3f" stroke-width="3" marker-end="url(#cm3g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/><path d="M340 158 H375" class="cm3f" stroke-width="3" marker-end="url(#cm3g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/><path d="M530 158 H565" class="cm3f" stroke-width="3" marker-end="url(#cm3g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/><path d="M720 158 H755" class="cm3f" stroke-width="3" marker-end="url(#cm3g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/>
<text x="20" y="258" class="cm3s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">La requête suit les flèches vertes. Chaque composant fait un contrôle différent :</text><text x="20" y="280" class="cm3s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">WAF = HTTP ; pare-feu = flux réseau ; application = identité/droits ; base = accès réseau et authentification DB.</text><text x="20" y="312" class="cm3s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Une réponse n'est possible que si le chemin de retour et les règles de session sont compatibles.</text>
<circle r="4.5" fill="#bbf7d0"><animateMotion dur="2s" repeatCount="indefinite" path="M150 158 L185 158"/></circle><circle r="4" fill="#bbf7d0"><animateMotion dur="2.5s" repeatCount="indefinite" path="M530 158 L565 158"/></circle></svg>
</div>

## 5. NAT, sorties contrôlées et inspection

### 5.1 NAT de sortie et proxy

Le NAT de sortie permet généralement aux ressources privées d’initier des communications vers des destinations externes sans qu’une adresse publique directe soit attribuée à chaque instance. Un proxy explicite peut aller plus loin en appliquant une politique au niveau applicatif, en authentifiant certains usages ou en journalisant les requêtes.

Le NAT n’est pas un pare-feu complet. Il modifie les adresses et parfois les ports ; il ne comprend pas forcément si une requête HTTPS est autorisée par la politique métier. Pour contrôler les destinations externes, combine les routes, les règles de sortie, les contrôles de domaine lorsque c’est possible, les appliances et les journaux appropriés.

### 5.2 Sortie haute disponibilité

Une unique passerelle NAT ou une unique appliance peut devenir un point de défaillance ou un goulot d’étranglement selon son mode de déploiement. Vérifie :
- si le service est régional, zonal ou distribué ;
- le comportement en cas de panne ;
- les limites de connexions et de bande passante ;
- la gestion des IP de sortie autorisées par les partenaires ;
- les coûts par heure et par volume ;
- la journalisation et les métriques ;
- les besoins IPv4 et IPv6.

Ne multiplie pas automatiquement les passerelles sans examiner la topologie, la redondance fournie nativement par le service et la stratégie de routage. Les détails diffèrent selon les offres.

### 5.3 Route forcée par une appliance (forced tunneling)

Dans certains environnements, le trafic sortant est envoyé vers un pare-feu ou une appliance centrale au lieu de sortir directement. Cette approche facilite une politique de sortie commune, mais exige un plan de routage et un dimensionnement stricts. Un mauvais chemin de retour peut provoquer des sessions qui se bloquent ; une route par défaut centralisée peut également détourner le trafic qui devrait rester privé ou utiliser un endpoint spécifique.

### Schéma 4 — Sortie contrôlée depuis des sous-réseaux privés

<div class="cloudm-diagram">
<svg viewBox="0 0 1000 390" width="100%" role="img" aria-label="Deux sous-réseaux privés envoyant le trafic via pare-feu et NAT vers Internet, avec flèches du sens sortant" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="cm4b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="cm4g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.cm4t{font:14px Arial,sans-serif;fill:#e5edf8}.cm4s{font:12px Arial,sans-serif;fill:#a9bdd5}.cm4f{stroke:#34d399;stroke-width:3;fill:none;stroke-dasharray:8 6;marker-end:url(#cm4g);animation:cm4dash 1.5s linear infinite}@keyframes cm4dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="35" width="280" height="315" rx="15" fill="#0a1727" stroke="#60a5fa" stroke-width="1.6"/><text x="160" y="61" class="cm4t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">VPC / VNet privé</text>
<rect x="45" y="90" width="230" height="75" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.4"/><rect x="60" y="109" width="25" height="25" rx="3" fill="none" stroke="#34d399" stroke-width="1.8"/><text x="177" y="120" class="cm4t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Sous-réseau applicatif</text><text x="177" y="141" class="cm4s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Serveurs sans IP publique</text>
<rect x="45" y="220" width="230" height="75" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.4"/><ellipse cx="78" cy="241" rx="12" ry="5" fill="none" stroke="#34d399" stroke-width="1.5"/><path d="M66 241 V263 C66 269 90 269 90 263 V241" fill="none" stroke="#34d399" stroke-width="1.5"/><text x="178" y="250" class="cm4t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Sous-réseau de données</text><text x="178" y="272" class="cm4s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Flux privé selon besoin</text>
<rect x="375" y="125" width="200" height="145" rx="13" fill="#211d3a" stroke="#a78bfa" stroke-width="1.7"/><path d="M410 157 L430 145 L450 157 L430 169 Z M410 157 V182 L430 194 L450 182 V157 M430 169 V194" fill="none" stroke="#c4b5fd" stroke-width="2"/><text x="490" y="163" class="cm4t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">FW / NVA</text><text x="475" y="218" class="cm4s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Inspection optionnelle</text><text x="475" y="239" class="cm4s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Routes aller/retour</text>
<rect x="650" y="125" width="145" height="145" rx="13" fill="#10243a" stroke="#38bdf8" stroke-width="1.7"/><path d="M680 159 H710 M695 144 V174 M680 159 L688 151 M680 159 L688 167 M710 159 L702 151 M710 159 L702 167" stroke="#38bdf8" stroke-width="2" fill="none"/><text x="722" y="202" class="cm4t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">NAT</text><text x="722" y="224" class="cm4s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Traduction sortie</text><text x="722" y="244" class="cm4s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Session initiée</text>
<rect x="855" y="145" width="120" height="105" rx="13" fill="#10243a" stroke="#38bdf8" stroke-width="1.7"/><circle cx="915" cy="175" r="17" fill="none" stroke="#38bdf8" stroke-width="2"/><path d="M898 175 H932 M915 158 C904 166 904 184 915 192 M915 158 C926 166 926 184 915 192" fill="none" stroke="#38bdf8" stroke-width="1.5"/><text x="915" y="217" class="cm4t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Internet</text><text x="915" y="236" class="cm4s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Sortie</text>
<path d="M300 126 H365" class="cm4f" stroke-width="3" marker-end="url(#cm4g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/><path d="M300 258 H335 V240 H365" class="cm4f" stroke-width="3" marker-end="url(#cm4g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/><path d="M575 198 H645" class="cm4f" stroke-width="3" marker-end="url(#cm4g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/><path d="M795 198 H850" class="cm4f" stroke-width="3" marker-end="url(#cm4g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/>
<text x="20" y="375" class="cm4s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Le sens vert représente les connexions initiées depuis l'intérieur. Les réponses de ces sessions doivent pouvoir revenir.</text>
<circle r="4.5" fill="#bbf7d0"><animateMotion dur="2.2s" repeatCount="indefinite" path="M300 126 L365 126"/></circle><circle r="4" fill="#bbf7d0"><animateMotion dur="2.6s" repeatCount="indefinite" path="M575 198 L645 198"/></circle></svg>
</div>

La topologie montre un chemin de sortie conceptuel. Certains services NAT sont intégrés et hautement disponibles ; d’autres architectures nécessitent des appliances redondantes. Vérifie le modèle réel du fournisseur avant d’extrapoler le dessin.

## 6. Connecter plusieurs VPC/VNet : peering ou hub-and-spoke

### 6.1 Peering direct

Le peering connecte deux réseaux virtuels pour permettre le routage entre leurs plages privées. Il convient souvent à un petit nombre de réseaux qui doivent communiquer directement. Il exige généralement des plages non chevauchantes et une configuration cohérente des deux côtés.

Un point essentiel : **le peering n’est pas automatiquement transitif**. Si A est connecté à B et B à C, cela ne signifie pas que A peut passer par B pour atteindre C. Des routes, des fonctionnalités de transit ou une appliance appropriée sont nécessaires. Les limitations précises sont propres au fournisseur.

### 6.2 Maillage complet et coût opérationnel

Avec N réseaux, un maillage complet peut nécessiter jusqu’à \(N(N-1)/2\) connexions directes si chaque paire doit communiquer. Cette croissance augmente le nombre de relations à surveiller et de règles à gérer. La formule décrit le nombre de liens d’un graphe complet, pas nécessairement le nombre de ressources cloud facturées dans tous les services.

Le peering reste utile lorsqu’il existe quelques liaisons directes et des besoins limités. Il est moins pratique lorsque des dizaines de réseaux ont besoin d’échanger du trafic de façon centralisée.

### 6.3 Hub-and-spoke

Dans une topologie hub-and-spoke, un réseau central (« hub ») est relié à plusieurs réseaux périphériques (« spokes »). Le hub peut héberger ou connecter :
- une passerelle VPN ou une liaison dédiée ;
- un pare-feu central ou une appliance d’inspection ;
- un DNS partagé ;
- des services de supervision et de sécurité ;
- des connexions privées vers des services communs.

La topologie peut simplifier la gestion, mais le hub devient critique : capacité, disponibilité, segmentation, propagation de routes et limites du service doivent être conçues. Un hub n’accorde pas automatiquement à tous les spokes le droit de communiquer entre eux. Le routage et le filtrage doivent l’indiquer explicitement.

### Schéma 5 — Architecture hub-and-spoke avec flèches

<div class="cloudm-diagram">
<svg viewBox="0 0 1000 450" width="100%" role="img" aria-label="Hub de connectivité avec pare-feu, trois réseaux spokes et liaison au site local, toutes les connexions ont des flèches" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="cm5b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="cm5g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.cm5t{font:14px Arial,sans-serif;fill:#e5edf8}.cm5s{font:12px Arial,sans-serif;fill:#a9bdd5}.cm5f{stroke:#38bdf8;stroke-width:3;fill:none;marker-end:url(#cm5b)}.cm5d{stroke:#34d399;stroke-width:3;fill:none;stroke-dasharray:8 6;marker-end:url(#cm5g);animation:cm5dash 1.7s linear infinite}@keyframes cm5dash{to{stroke-dashoffset:-30}}</style></defs>
<rect x="345" y="120" width="300" height="205" rx="18" fill="#111d30" stroke="#a78bfa" stroke-width="2"/><text x="495" y="148" class="cm5t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">HUB réseau central</text>
<rect x="385" y="175" width="220" height="55" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.4"/><path d="M405 192 H435 V214 H405 Z M411 198 H429 M411 205 H429" fill="none" stroke="#c4b5fd" stroke-width="1.6"/><text x="518" y="198" class="cm5t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Pare-feu / NVA</text><text x="518" y="216" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Inspection si requise</text>
<rect x="385" y="248" width="220" height="52" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.4"/><text x="495" y="269" class="cm5t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">VPN / WAN / DNS</text><text x="495" y="288" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Services communs</text>
<rect x="20" y="45" width="230" height="95" rx="13" fill="#0d2a27" stroke="#34d399" stroke-width="1.6"/><text x="135" y="75" class="cm5t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Spoke A — Production</text><text x="135" y="98" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">10.41.0.0/16</text><text x="135" y="119" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Application web</text>
<rect x="750" y="45" width="230" height="95" rx="13" fill="#0d2a27" stroke="#34d399" stroke-width="1.6"/><text x="865" y="75" class="cm5t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Spoke B — Données</text><text x="865" y="98" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">10.42.0.0/16</text><text x="865" y="119" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Services internes</text>
<rect x="20" y="320" width="230" height="95" rx="13" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="135" y="350" class="cm5t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Site local</text><text x="135" y="373" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">172.20.0.0/16</text><text x="135" y="394" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">VPN / liaison dédiée</text>
<rect x="750" y="320" width="230" height="95" rx="13" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="865" y="350" class="cm5t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Spoke C — Test</text><text x="865" y="373" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">10.43.0.0/16</text><text x="865" y="394" class="cm5s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Environnement isolé</text>
<path d="M250 95 H310 V200 H340" class="cm5d" stroke-width="3" marker-end="url(#cm5g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/><path d="M750 95 H690 V200 H650" class="cm5d" stroke-width="3" marker-end="url(#cm5g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/><path d="M250 365 H300 V275 H340" class="cm5f" stroke-width="3" marker-end="url(#cm5b)" stroke="#38bdf8" fill="none"/><path d="M750 365 H690 V275 H650" class="cm5f" stroke-width="3" marker-end="url(#cm5b)" stroke="#38bdf8" fill="none"/>
<text x="280" y="80" class="cm5s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Routes</text><text x="700" y="80" class="cm5s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Routes</text><text x="280" y="350" class="cm5s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Hybride</text><text x="700" y="350" class="cm5s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Routes</text>

<circle r="4.5" fill="#bbf7d0"><animateMotion dur="2.8s" repeatCount="indefinite" path="M250 95 L310 95 L310 200 L340 200"/></circle><circle r="4" fill="#bfdbfe"><animateMotion dur="3s" repeatCount="indefinite" path="M250 365 L300 365 L300 275 L340 275"/></circle></svg>
</div>

Les flèches indiquent les connexions logiques entre réseaux et hub. Elles ne veulent pas dire que tous les spokes ont une connectivité transitive par défaut. La capacité de transit dépend du service, de ses options de routage et des appliances utilisées.

### 6.4 Transit gateway, route server et WAN managé

Les fournisseurs proposent différentes variantes de hubs managés :
- AWS Transit Gateway ou AWS Cloud WAN ;
- Azure Virtual WAN et des architectures hub-and-spoke avec VPN Gateway, ExpressRoute ou appliances ;
- Google Cloud Network Connectivity Center et les services d’interconnexion associés.

Ils répondent à des besoins de transit à grande échelle, mais ne doivent pas être traités comme des produits parfaitement équivalents. Compare le nombre de connexions, les routes importées/annoncées, les contraintes de région, les quotas, le chiffrement, les coûts de traitement, la journalisation et la résilience.

## 7. Connectivité hybride : VPN, BGP et liaison dédiée

### 7.1 VPN site à site

Un VPN site à site relie un réseau local au cloud par un ou plusieurs tunnels chiffrés, souvent construits avec IPsec. La connectivité dépend de plusieurs éléments :
- adresses des passerelles ;
- paramètres IKE/IPsec compatibles ;
- secrets ou certificats gérés correctement ;
- plages IP non conflictuelles ;
- routes configurées ou apprises ;
- règles réseau des deux côtés ;
- politiques de bascule entre tunnels ;
- supervision et alertes.

Un tunnel « UP » ne garantit pas que les applications communiquent. Il indique seulement qu’un aspect de la négociation est actif selon l’outil utilisé. Vérifie les routes, les compteurs, les préfixes annoncés, les règles et la connectivité applicative de bout en bout.

### 7.2 BGP et annonces de routes

BGP est utilisé dans de nombreuses architectures hybrides pour annoncer des préfixes entre le réseau local et le cloud. Il réduit la nécessité de maintenir manuellement chaque route, mais exige une politique stricte.

Bonnes pratiques :
- n’annoncer que les préfixes nécessaires ;
- filtrer les préfixes reçus ;
- utiliser des plages documentées et non chevauchantes ;
- vérifier les routes actives et les chemins préférés ;
- tester l’arrêt d’un tunnel et la convergence ;
- surveiller les annonces inattendues ;
- documenter le choix des routes principales et de secours.

Le « meilleur » chemin dépend de la politique de routage et de l’implémentation. Ne pars pas du principe que la route la plus courte géographiquement ou le tunnel le plus ancien gagnera.

### 7.3 VPN contre liaison dédiée

| Critère | VPN site à site | Liaison privée dédiée |
|---|---|---|
| Transport | Tunnel sur une infrastructure IP existante | Connexion dédiée ou service d’interconnexion |
| Mise en place | Souvent plus rapide | Planification parfois plus longue |
| Chiffrement | Généralement fourni par IPsec lorsqu’il est configuré | Ne pas supposer le chiffrement sans vérifier |
| Performance | Dépend du tunnel, de la passerelle et de l’Internet sous-jacent | Peut offrir une capacité et une latence plus prévisibles |
| Résilience | Prévoir plusieurs tunnels/chemins si nécessaire | Prévoir diversité physique/logique et redondance |
| Coût | Gateway, transfert et coût du transport existant | Ports, opérateurs, circuits, transfert et frais associés |

Ce tableau décrit des tendances, pas une garantie. Certains VPN managés offrent des performances élevées ; certaines liaisons dédiées partagent des dépendances opérateur. La décision doit venir des exigences, de la disponibilité réelle et d’une estimation financière.

### Schéma 6 — Site local, deux chemins et réseau cloud

<div class="cloudm-diagram">
<svg viewBox="0 0 1000 400" width="100%" role="img" aria-label="Réseau local relié au cloud par VPN primaire et liaison dédiée de secours, avec flèches bidirectionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="cm6b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="cm6g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.cm6t{font:14px Arial,sans-serif;fill:#e5edf8}.cm6s{font:12px Arial,sans-serif;fill:#a9bdd5}.cm6p{stroke:#38bdf8;stroke-width:3;fill:none;stroke-dasharray:8 6;animation:cm6dash 1.5s linear infinite}@keyframes cm6dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="115" width="230" height="145" rx="14" fill="#10243a" stroke="#38bdf8" stroke-width="1.7"/><text x="135" y="143" class="cm6t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Site local / DC</text><rect x="55" y="165" width="160" height="65" rx="9" fill="#172c45" stroke="#60a5fa" stroke-width="1.4"/><path d="M75 181 H95 V209 H75 Z M80 187 H90 M80 195 H90 M80 203 H90" fill="none" stroke="#60a5fa" stroke-width="1.5"/><text x="154" y="190" class="cm6t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Routeur</text><text x="154" y="211" class="cm6s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Firewall</text>
<rect x="390" y="35" width="230" height="95" rx="12" fill="#211d3a" stroke="#a78bfa" stroke-width="1.7"/><text x="505" y="62" class="cm6t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">VPN IPsec</text><text x="505" y="83" class="cm6s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Tunnel chiffré</text><text x="505" y="105" class="cm6s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">BGP ou routes statiques</text>
<rect x="390" y="270" width="230" height="95" rx="12" fill="#0d2a27" stroke="#34d399" stroke-width="1.7"/><text x="505" y="297" class="cm6t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Liaison dédiée</text><text x="505" y="318" class="cm6s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Circuit / interconnexion</text><text x="505" y="340" class="cm6s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Chemin distinct à valider</text>
<rect x="755" y="115" width="220" height="145" rx="14" fill="#10243a" stroke="#38bdf8" stroke-width="1.7"/><text x="865" y="143" class="cm6t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Passerelle cloud</text><rect x="795" y="165" width="140" height="65" rx="9" fill="#172c45" stroke="#60a5fa" stroke-width="1.4"/><path d="M815 181 H835 V209 H815 Z M820 187 H830 M820 195 H830 M820 203 H830" fill="none" stroke="#60a5fa" stroke-width="1.5"/><text x="875" y="190" class="cm6t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">VPN / WAN</text><text x="875" y="211" class="cm6s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Routes apprises</text>
<path d="M250 160 H300 V82 H385" class="cm6p" marker-end="url(#cm6b)"/><path d="M390 108 H300 V190 H255" fill="none" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#cm6b)"/><path d="M250 210 H300 V320 H385" fill="none" stroke="#34d399" stroke-width="2.5" stroke-dasharray="8 6" marker-end="url(#cm6g)"/><path d="M390 335 H330 V240 H255" fill="none" stroke="#34d399" stroke-width="2.5" marker-end="url(#cm6g)"/><path d="M620 82 H690 V160 H750" class="cm6p" marker-end="url(#cm6b)"/><path d="M755 190 H690 V108 H625" fill="none" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#cm6b)"/><path d="M620 320 H690 V210 H750" fill="none" stroke="#34d399" stroke-width="2.5" stroke-dasharray="8 6" marker-end="url(#cm6g)"/><path d="M755 240 H710 V335 H625" fill="none" stroke="#34d399" stroke-width="2.5" marker-end="url(#cm6g)"/>
<text x="280" y="52" class="cm6s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Chemin 1</text><text x="280" y="289" class="cm6s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Chemin 2</text><text x="20" y="385" class="cm6s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Les flèches dans les deux sens illustrent l’échange. Une vraie bascule exige des routes, des priorités et des tests coordonnés.</text>
<circle r="4.5" fill="#bfdbfe"><animateMotion dur="2.8s" repeatCount="indefinite" path="M250 160 L300 160 L300 82 L385 82"/></circle><circle r="4" fill="#bbf7d0"><animateMotion dur="3.1s" repeatCount="indefinite" path="M250 210 L300 210 L300 320 L385 320"/></circle></svg>
</div>

Deux dessins ne prouvent pas une diversité physique réelle. Pour améliorer la résilience, vérifie les équipements, opérateurs, conduits, régions, passerelles et dépendances communes aux deux chemins. Une bascule doit être testée en conditions maîtrisées.

## 8. Accès privé aux services cloud et aux services SaaS

### 8.1 Pourquoi éviter de passer par Internet ?

Une application peut devoir consommer un stockage, un gestionnaire de secrets, une base de données managée ou une API cloud. Un endpoint privé crée, selon le service, un chemin privé depuis le réseau du client jusqu’au service pris en charge. Cela peut réduire l’exposition publique et simplifier certaines politiques de sortie.

Les dénominations varient :
- AWS VPC endpoints (interface ou gateway selon le service) ;
- Azure Private Link et private endpoints ;
- Google Cloud Private Service Connect et mécanismes d’accès privé aux APIs.

Ces produits n’ont pas exactement les mêmes modes de raccordement. Vérifie si l’accès se fait via une interface, une adresse privée, une règle de transfert, un DNS particulier, un service publié par un tiers ou un mécanisme spécifique à l’API.

### 8.2 Endpoint privé et DNS

Créer un endpoint privé n’est qu’une partie du travail. Les clients doivent résoudre le nom du service vers l’adresse associée à l’endpoint lorsque l’architecture l’exige. Si le nom continue de résoudre vers une adresse publique, l’application peut continuer à tenter une connexion externe malgré l’existence du chemin privé.

Vérifie :
- les zones DNS privées ;
- les liens de la zone aux réseaux concernés ;
- les redirecteurs DNS dans une architecture hybride ;
- les noms spécifiques requis par le fournisseur ;
- la résolution depuis les sous-réseaux et les postes qui doivent utiliser le service ;
- les certificats TLS et les noms attendus par le client ;
- les règles réseau et les journaux.

### 8.3 Endpoint privé n’est pas synonyme de service sécurisé automatiquement

Le chemin réseau privé n’abolit pas l’authentification ni l’autorisation applicative. Un client doit encore posséder les droits requis. Les secrets restent à protéger, et les logs doivent permettre de détecter les accès anormaux. Selon l’offre, un endpoint peut aussi être joignable depuis plusieurs réseaux : limite son exposition au moyen des routes et politiques adaptées.

### Schéma 7 — Chemin public contre accès privé au service

<div class="cloudm-diagram">
<svg viewBox="0 0 1000 390" width="100%" role="img" aria-label="Comparaison d'une connexion publique à une API et d'un endpoint privé, avec flèches directionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="cm7b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="cm7g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.cm7t{font:14px Arial,sans-serif;fill:#e5edf8}.cm7s{font:12px Arial,sans-serif;fill:#a9bdd5}.cm7f{fill:none;stroke-width:3;stroke-dasharray:8 6;animation:cm7dash 1.5s linear infinite}@keyframes cm7dash{to{stroke-dashoffset:-28}}</style></defs>
<text x="250" y="32" class="cm7t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Chemin public</text><rect x="20" y="70" width="155" height="70" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="97" y="98" class="cm7t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">VM privée</text><text x="97" y="120" class="cm7s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Client API</text><rect x="210" y="70" width="155" height="70" rx="11" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><circle cx="287" cy="91" r="10" fill="none" stroke="#fbbf24" stroke-width="1.5"/><path d="M276 91 H298 M287 80 V102" stroke="#fbbf24" stroke-width="1.5"/><text x="287" y="122" class="cm7t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">NAT / Internet</text><rect x="400" y="70" width="155" height="70" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="477" y="98" class="cm7t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">API fournisseur</text><text x="477" y="120" class="cm7s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Endpoint public</text><path d="M175 105 H205" class="cm7f" stroke="#38bdf8" marker-end="url(#cm7b)"/><path d="M365 105 H395" class="cm7f" stroke="#38bdf8" marker-end="url(#cm7b)"/>
<path d="M20 165 H555" stroke="#334155" stroke-width="1.2"/><text x="250" y="198" class="cm7t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Accès privé</text><rect x="20" y="225" width="155" height="70" rx="11" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="97" y="253" class="cm7t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">VM privée</text><text x="97" y="275" class="cm7s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Client API</text><rect x="210" y="225" width="155" height="70" rx="11" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="287" y="253" class="cm7t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Endpoint privé</text><text x="287" y="275" class="cm7s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">IP interne / DNS</text><rect x="400" y="225" width="155" height="70" rx="11" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="477" y="253" class="cm7t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Service API</text><text x="477" y="275" class="cm7s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Accès privé</text><path d="M175 260 H205" class="cm7f" stroke="#34d399" marker-end="url(#cm7g)"/><path d="M365 260 H395" class="cm7f" stroke="#34d399" marker-end="url(#cm7g)"/>
<rect x="620" y="55" width="355" height="265" rx="14" fill="#0a1727" stroke="#60a5fa" stroke-width="1.6"/><text x="797" y="83" class="cm7t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Contrôles à vérifier</text><text x="650" y="120" class="cm7s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">1. DNS du nom consommé</text><text x="650" y="153" class="cm7s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">2. Route et règles de sécurité</text><text x="650" y="186" class="cm7s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">3. Identité et droits sur l’API</text><text x="650" y="219" class="cm7s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">4. TLS et nom du service</text><text x="650" y="252" class="cm7s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">5. Logs et supervision</text><text x="650" y="291" class="cm7s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Privé ne signifie pas « sans authentification ».</text>
<text x="20" y="352" class="cm7s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Le circuit privé peut éviter la sortie Internet pour le service pris en charge ; les DNS et politiques doivent orienter le client correctement.</text>
<circle r="4.5" fill="#bbf7d0"><animateMotion dur="2.4s" repeatCount="indefinite" path="M175 260 L205 260"/></circle><circle r="4" fill="#bbf7d0"><animateMotion dur="2.5s" repeatCount="indefinite" path="M365 260 L395 260"/></circle></svg>
</div>

Le schéma compare les intentions d’architecture. Certains fournisseurs disposent d’endpoints privés pour un ensemble de services seulement ; d’autres exigent une configuration DNS spécifique. Le trajet réel dépend du service cible.

## 9. DNS avancé : public, privé et hybride

### 9.1 Séparer les espaces de noms

Dans une architecture cloud intermédiaire, le DNS est souvent un service de connectivité essentiel. Une application peut utiliser :
- un nom public pour l’entrée utilisateur ;
- des noms privés pour les services internes ;
- des zones différentes selon l’environnement ;
- un résolveur capable de transmettre certaines requêtes à un DNS local ;
- des enregistrements dédiés aux endpoints privés.

Évite de mélanger sans documentation les enregistrements publics et privés ayant le même nom. Les vues DNS différentes peuvent être utiles, mais elles exigent des tests depuis chaque réseau concerné.

### 9.2 DNS hybride

Une architecture hybride peut demander au DNS cloud de résoudre des noms internes à l’entreprise, ou au DNS local de résoudre les noms de services privés cloud. On met alors en place des redirecteurs ou des points de résolution adaptés, avec des routes entre les résolveurs.

Les problèmes typiques :
- zone non liée au bon VPC/VNet ;
- enregistrement manquant ;
- redirecteur pointant vers un serveur injoignable ;
- port DNS bloqué ;
- réponse mise en cache trop longtemps ;
- nom public choisi alors que le service attend un nom privé ;
- certificat TLS ne correspondant pas au nom utilisé.

### 9.3 TTL et mises à jour

Le TTL (Time To Live) indique combien de temps une réponse DNS peut être conservée par un cache. Un TTL court peut accélérer certaines bascules, mais augmenter le nombre de requêtes et n’est pas une garantie que tous les clients se mettent à jour instantanément. Certains logiciels, proxys et systèmes conservent leurs propres caches.

Avant une migration DNS, prépare une stratégie : réduire le TTL suffisamment tôt, valider la nouvelle cible, mesurer la propagation et conserver une procédure de retour arrière.

## 10. IPv6, dual stack et stratégie de transition

### 10.1 Dual stack

Un service dual stack utilise IPv4 et IPv6. Il faut vérifier les deux chemins : adresses, routes, règles de pare-feu, DNS `A` et `AAAA`, contrôles TLS et dépendances. Il est fréquent d’avoir une configuration IPv4 correcte mais une politique IPv6 incomplète.

### 10.2 Filtrage et routes IPv6

Une route IPv6 `::/0` est une route par défaut IPv6. Sa présence doit être évaluée en même temps que les politiques de sécurité et la connectivité réelle. N’applique pas automatiquement les règles IPv4 en supposant qu’elles protègent aussi IPv6.

### 10.3 NAT64 et DNS64

Certains environnements utilisent des mécanismes comme NAT64/DNS64 pour permettre à des clients IPv6 de joindre des destinations IPv4 dans des architectures adaptées. Leur présence et leur configuration dépendent du fournisseur. Ils ne remplacent pas un plan de transition et doivent être testés avec les applications utilisées.

### 10.4 MTU, fragmentation et PMTUD

La MTU détermine la taille maximale d’un paquet de couche réseau qui peut être transporté sur un lien sans fragmentation à ce niveau. Les VPN, tunnels et encapsulations ajoutent des en-têtes qui réduisent la charge utile possible. Une MTU inadaptée peut causer des connexions où de petits échanges réussissent, mais les transferts volumineux ou certaines négociations TLS se bloquent.

Le diagnostic peut inclure :
- la vérification de la MTU des interfaces ;
- des tests de paquets de tailles contrôlées ;
- l’inspection des messages ICMP utiles à la découverte du MTU ;
- la vérification des pare-feu qui bloquent certains messages ;
- l’examen des réglages TCP MSS selon l’architecture.

N’abaisse pas arbitrairement la MTU sans comprendre le chemin. Note les changements et teste les flux représentatifs, notamment sur les tunnels hybrides.

## 11. Load balancing, disponibilité et trafic entrant

### 11.1 Couche 4 et couche 7

Un équilibreur de couche 4 répartit généralement les flux en fonction de données de transport comme IP, TCP/UDP et port. Un équilibreur de couche 7 peut interpréter des informations HTTP(S), telles que les noms d’hôte ou les chemins URL, selon le produit.

Les services ne présentent pas tous les mêmes options : terminaison TLS, proxy ou passthrough, affinité de session, adresses source visibles, règles de routage, protection DDoS ou WAF peuvent être fournis par des composants différents.

### 11.2 Contrôles de santé

Un contrôle de santé doit valider une condition pertinente pour servir les requêtes. Si le serveur répond sur TCP mais que l’application ne peut pas joindre sa base, un simple test de port peut le marquer comme sain. Inversement, un contrôle trop complexe peut marquer tous les serveurs comme indisponibles en cas de panne d’une dépendance commune.

Définis :
- un endpoint de santé clair ;
- un délai et une fréquence réalistes ;
- des seuils tolérant les ralentissements courts ;
- les dépendances incluses ou exclues du test ;
- le comportement en cas de toutes les cibles défaillantes ;
- des alertes sur les changements de santé.

### 11.3 Chemin retour et visibilité des adresses source

Selon le service d’équilibrage, le trafic vers les cibles peut être proxifié ou transmis avec des propriétés particulières. L’adresse source observée par le serveur peut être celle du client, du proxy ou d’une autre interface. Cela influence les règles réseau, les logs applicatifs et les mécanismes d’authentification basés sur IP. Lis la documentation et teste depuis des clients réels.

### Schéma 8 — Équilibrage vers des cibles saines dans deux zones

<div class="cloudm-diagram">
<svg viewBox="0 0 1200 395" width="100%" role="img" aria-label="Clients vers load balancer, puis deux zones avec serveur A et serveur B par flèches directionnelles" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="cm8b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="cm8g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.cm8t{font:14px Arial,sans-serif;fill:#e5edf8}.cm8s{font:12px Arial,sans-serif;fill:#a9bdd5}.cm8f{stroke:#34d399;stroke-width:3;fill:none;stroke-dasharray:8 6;marker-end:url(#cm8g);animation:cm8dash 1.5s linear infinite}@keyframes cm8dash{to{stroke-dashoffset:-28}}</style></defs>
<rect x="20" y="150" width="140" height="82" rx="12" fill="#10243a" stroke="#38bdf8" stroke-width="1.6"/><text x="90" y="180" class="cm8t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Clients</text><text x="90" y="203" class="cm8s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">HTTPS</text>
<rect x="215" y="135" width="190" height="112" rx="14" fill="#211d3a" stroke="#a78bfa" stroke-width="1.7"/><path d="M240 159 H270 V181 H240 Z M246 165 H264 M246 173 H264" fill="none" stroke="#c4b5fd" stroke-width="1.5"/><text x="325" y="169" class="cm8t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Load balancer</text><text x="310" y="195" class="cm8s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">TLS / règles</text><text x="310" y="216" class="cm8s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Health checks</text>
<path d="M160 191 H210" class="cm8f" stroke-width="3" marker-end="url(#cm8g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/>
<rect x="465" y="40" width="500" height="135" rx="14" fill="#0a1727" stroke="#60a5fa" stroke-width="1.6"/><text x="715" y="65" class="cm8t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Zone de disponibilité A</text>
<rect x="490" y="80" width="215" height="70" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="510" y="96" width="22" height="25" rx="3" fill="none" stroke="#34d399" stroke-width="1.5"/><path d="M510 104 H532 M515 112 H527" stroke="#34d399" stroke-width="1.3"/><text x="610" y="107" class="cm8t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Serveur A</text><text x="610" y="128" class="cm8s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Sain</text>
<rect x="465" y="220" width="500" height="135" rx="14" fill="#0a1727" stroke="#60a5fa" stroke-width="1.6"/><text x="715" y="245" class="cm8t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Zone de disponibilité B</text>
<rect x="490" y="260" width="215" height="70" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><rect x="510" y="276" width="22" height="25" rx="3" fill="none" stroke="#34d399" stroke-width="1.5"/><path d="M510 284 H532 M515 292 H527" stroke="#34d399" stroke-width="1.3"/><text x="610" y="287" class="cm8t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Serveur B</text><text x="610" y="308" class="cm8s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Sain</text>
<path d="M405 170 H440 V115 H485" class="cm8f" stroke-width="3" marker-end="url(#cm8g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/><path d="M405 210 H440 V295 H485" class="cm8f" stroke-width="3" marker-end="url(#cm8g)" stroke="#34d399" fill="none" stroke-dasharray="8 6"/>
<rect x="990" y="125" width="185" height="120" rx="12" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><text x="1082" y="152" class="cm8t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="14px">Supervision</text><text x="1082" y="176" class="cm8s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Métriques / logs</text><text x="1082" y="197" class="cm8s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Alertes</text><text x="1082" y="218" class="cm8s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Capacité de secours</text>
<path d="M705 115 H970 V155 H985" fill="none" stroke="#fbbf24" stroke-width="2.2" stroke-dasharray="6 5" marker-end="url(#cm8b)"/><path d="M705 295 H970 V215 H985" fill="none" stroke="#fbbf24" stroke-width="2.2" stroke-dasharray="6 5" marker-end="url(#cm8b)"/>
<text x="20" y="385" class="cm8s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="12px">Le service répartit les requêtes sur les cibles conformes aux contrôles de santé ; vérifier les propriétés du chemin retour.</text>
<circle r="4.5" fill="#bbf7d0"><animateMotion dur="2.4s" repeatCount="indefinite" path="M405 170 L440 170 L440 115 L485 115"/></circle><circle r="4" fill="#bbf7d0"><animateMotion dur="2.6s" repeatCount="indefinite" path="M405 210 L440 210 L440 295 L485 295"/></circle></svg>
</div>

La supervision ne doit pas se contenter d’afficher « cible saine ». Mesure également les erreurs applicatives, la latence, les saturations, les files d’attente et les dépendances critiques.

## 12. Observabilité et dépannage avancé

### 12.1 Les trois familles de données

- **Métriques** : volume, débit, latence, pertes, connexions actives, saturation des passerelles, taux d’erreur.
- **Journaux** : flux acceptés/refusés, événements de configuration, logs DNS, équipements de sécurité, répartiteurs de charge et applications.
- **Traces** : parcours d’une requête au sein de plusieurs services applicatifs, lorsqu’une instrumentation adaptée est disponible.

Les journaux de flux réseau ne sont pas une capture complète de paquets. Ils donnent des métadonnées selon le service et le mode de collecte. Pour examiner les échanges au niveau des paquets, une capture ou un service de mirroring peut être requis, avec une attention particulière à la confidentialité et au coût.

### 12.2 Vérifier la configuration effective

La configuration déclarée n’est pas toujours la configuration réellement appliquée à une interface donnée. Dans la mesure du possible, examine :
- les routes effectives ou calculées ;
- les groupes de sécurité attachés à la bonne ressource ;
- les règles héritées ou hiérarchiques ;
- les routes propagées par le VPN ou BGP ;
- les associations des sous-réseaux aux tables de routage ;
- les zones DNS associées ;
- les règles et cibles d’un répartiteur de charge ;
- les journaux de refus au niveau réseau et système.

### 12.3 Diagnostic en ordre, sans désactiver la sécurité

Utilise un flux témoin clairement défini : source, destination, protocole, port et heure du test. Puis :
1. confirme le nom et l’adresse résolue ;
2. confirme l’interface et le préfixe de la source ;
3. examine la route effective vers la destination ;
4. vérifie le filtrage à chaque frontière ;
5. confirme le service à l’écoute ;
6. teste le TLS et le protocole applicatif ;
7. recherche les refus dans les journaux ;
8. teste le chemin retour ;
9. compare avec un flux similaire qui fonctionne ;
10. apporte un seul changement à la fois et conserve les observations.

Les outils de diagnostic gérés par le fournisseur peuvent simuler ou analyser un chemin, mais ils ne reproduisent pas nécessairement chaque élément de l’application. Un test réel de bout en bout demeure nécessaire.

### Schéma 9 — Arbre de diagnostic d’un flux cloud

<div class="cloudm-diagram">
<svg viewBox="0 0 1000 420" width="100%" role="img" aria-label="Arbre de diagnostic depuis une connexion qui échoue vers DNS, routage, sécurité, service et retour, avec flèches" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="cm9b" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#38bdf8"/></marker><marker id="cm9g" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#34d399"/></marker><style>.cm9t{font:13px Arial,sans-serif;fill:#e5edf8}.cm9s{font:11px Arial,sans-serif;fill:#a9bdd5}.cm9f{stroke:#38bdf8;stroke-width:2.5;fill:none;stroke-dasharray:7 5;marker-end:url(#cm9b);animation:cm9dash 1.4s linear infinite}@keyframes cm9dash{to{stroke-dashoffset:-24}}</style></defs>
<rect x="330" y="15" width="340" height="52" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="500" y="37" class="cm9t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">Flux impossible</text><text x="500" y="54" class="cm9s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Noter source, destination, port et heure</text>
<path d="M500 67 V87" class="cm9f" stroke-width="3" marker-end="url(#cm9b)" stroke="#38bdf8" fill="none" stroke-dasharray="7 5"/><rect x="345" y="87" width="310" height="52" rx="10" fill="#211d3a" stroke="#a78bfa" stroke-width="1.5"/><text x="500" y="109" class="cm9t" text-anchor="middle" font-weight="bold" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">1. Le nom résout-il correctement ?</text><text x="500" y="126" class="cm9s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Zone publique/privée, TTL, endpoint</text>
<path d="M345 113 H190 V160" class="cm9f" stroke-width="3" marker-end="url(#cm9b)" stroke="#38bdf8" fill="none" stroke-dasharray="7 5"/><path d="M655 113 H810 V160" class="cm9f" stroke-width="3" marker-end="url(#cm9b)" stroke="#38bdf8" fill="none" stroke-dasharray="7 5"/><text x="208" y="105" class="cm9s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Non</text><text x="775" y="105" class="cm9s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Oui</text>
<rect x="35" y="160" width="310" height="58" rx="10" fill="#2b1e16" stroke="#fbbf24" stroke-width="1.5"/><text x="190" y="184" class="cm9t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">Corriger DNS</text><text x="190" y="202" class="cm9s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Nom, cible, résolveur, lien privé</text>
<rect x="655" y="160" width="310" height="58" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="810" y="184" class="cm9t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">2. Route effective correcte ?</text><text x="810" y="202" class="cm9s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Destination, next hop, propagation</text>
<path d="M810 218 V238" class="cm9f" stroke-width="3" marker-end="url(#cm9b)" stroke="#38bdf8" fill="none" stroke-dasharray="7 5"/><rect x="655" y="238" width="310" height="58" rx="10" fill="#10243a" stroke="#38bdf8" stroke-width="1.5"/><text x="810" y="262" class="cm9t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">3. Règles compatibles ?</text><text x="810" y="280" class="cm9s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">SG, ACL, FW, système invité</text>
<path d="M810 296 V316" class="cm9f" stroke-width="3" marker-end="url(#cm9b)" stroke="#38bdf8" fill="none" stroke-dasharray="7 5"/><rect x="655" y="316" width="310" height="58" rx="10" fill="#0d2a27" stroke="#34d399" stroke-width="1.5"/><text x="810" y="340" class="cm9t" text-anchor="middle" fill="#e5edf8" font-family="Arial,sans-serif" font-size="13px">4. Service et retour fonctionnels ?</text><text x="810" y="358" class="cm9s" text-anchor="middle" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Port, TLS, logs, routes retour, MTU</text>
<text x="35" y="270" class="cm9s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Conserver les preuves</text><text x="35" y="289" class="cm9s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">et changer une seule</text><text x="35" y="308" class="cm9s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">chose à la fois.</text>
<text x="35" y="390" class="cm9s" fill="#a9bdd5" font-family="Arial,sans-serif" font-size="11px">Une route présente n’est pas une autorisation ; un port joignable n’est pas une preuve que l’application fonctionne.</text>
<circle r="4.5" fill="#bfdbfe"><animateMotion dur="2.2s" repeatCount="indefinite" path="M500 67 L500 87"/></circle><circle r="4" fill="#bfdbfe"><animateMotion dur="2.8s" repeatCount="indefinite" path="M655 113 L810 113 L810 160"/></circle></svg>
</div>

## 13. Infrastructure as Code, gouvernance et changements

### 13.1 Déclarer l’architecture en code

L’Infrastructure as Code (IaC) permet de décrire les réseaux, sous-réseaux, routes, groupes de sécurité, endpoints, passerelles et liaisons sous forme de fichiers versionnés. Des outils possibles sont Terraform, OpenTofu, AWS CloudFormation, Azure Bicep ou d’autres mécanismes natifs du fournisseur.

Le processus conseillé :
1. versionner les définitions et modules ;
2. utiliser des variables pour les environnements ;
3. exécuter une validation et une revue ;
4. examiner le plan de changement avant application ;
5. appliquer dans un environnement de test ;
6. vérifier les routes et les flux ;
7. appliquer en production avec une procédure de retour arrière ;
8. surveiller le résultat réel et détecter les dérives.

### 13.2 Politique de sécurité-as-code

Les règles réseau peuvent faire l’objet de tests automatiques : interdiction d’exposer les ports d’administration à Internet, limitation des CIDR trop larges, vérification de la présence d’une route privée, ou exigence de journaux pour certains composants. Les politiques doivent être adaptées au contexte : une règle temporaire large peut être acceptable pour une expérience isolée, mais pas pour un réseau de production.

### 13.3 Gouvernance multi-comptes et multi-projets

L’isolation des comptes, subscriptions ou projets réduit le rayon d’impact et sépare les équipes ou environnements. Il faut néanmoins gérer les connexions inter-environnements, les identités de service, les journaux centralisés et l’inventaire des plages IP. La séparation administrative ne dispense pas de concevoir la connectivité et le filtrage.

### 13.4 Gestion des changements

Avant un changement réseau risqué :
- identifie les applications et sous-réseaux concernés ;
- capture les routes effectives et règles actuelles ;
- prévois un test qui valide le résultat ;
- note les métriques de départ ;
- définis un déclencheur de retour arrière ;
- applique le changement dans une fenêtre adaptée ;
- surveille les refus et erreurs après l’application ;
- conserve les preuves et mets à jour les diagrammes.

Ne teste jamais la haute disponibilité uniquement sur un dessin ou une configuration théorique. Planifie des exercices contrôlés en dehors de la production critique lorsque c’est possible.

## 14. Coûts, capacité et limites opérationnelles

La dépense réseau peut inclure les transferts Internet sortants, la communication interzone ou interrégion, le traitement par les passerelles, les endpoints privés, les liaisons dédiées, les adresses publiques, les services d’équilibrage, la capture réseau et la conservation des journaux. Les modèles tarifaires sont propres à chaque fournisseur et région.

Pour une estimation correcte, sépare :
- le coût horaire des ressources actives ;
- le volume de données traité ;
- les transferts entre zones ou régions ;
- les coûts des opérateurs et circuits ;
- la rétention des logs ;
- le trafic de secours lorsque plusieurs chemins sont configurés ;
- les environnements de test et de préproduction ;
- le coût des adresses, des services de sécurité et des transferts NAT.

Le meilleur design n’est pas systématiquement celui qui possède le plus de composants. Chaque passerelle, appliance ou endpoint doit répondre à une exigence documentée. Un composant supplémentaire peut augmenter la sécurité ou la résilience, mais aussi les coûts, les dépendances, la latence et la charge d’exploitation.

Surveille également les quotas : nombre de routes, sous-réseaux, interfaces, peerings, connexions VPN, endpoints, règles, connexions simultanées et débit. Les limites peuvent être régionales, par compte ou par service.

## 15. Atelier pratique : concevoir une architecture intermédiaire

### Scénario

Une entreprise migre une application e-commerce vers le cloud. Elle dispose de :
- un site d’entreprise avec la plage `172.20.0.0/16` ;
- un environnement de production ;
- un environnement de test ;
- une base de données privée ;
- un service de journalisation partagé ;
- des développeurs qui doivent accéder aux ressources de test ;
- une exigence d’accès privé à certaines APIs cloud ;
- un besoin de connectivité hybride temporaire pendant la migration.

Les plages proposées ici sont fictives. Vérifie tous les chevauchements avant de les utiliser.

### Étape 1 — Définir les domaines réseau

Propose des plages distinctes pour le hub, la production, le test et les services partagés. Documente les sous-réseaux d’entrée, d’application, de données et d’administration. Réserve de l’espace pour l’évolution plutôt que de remplir immédiatement un petit bloc.

Livrable attendu : un tableau CIDR qui indique le préfixe, le rôle, l’environnement, le propriétaire et les réseaux qui doivent pouvoir le joindre.

### Étape 2 — Définir les flux nécessaires

Écris les flux sous la forme source → destination, protocole/port, justification :
- clients → entrée HTTPS ;
- entrée → serveurs applicatifs ;
- application → base de données ;
- ressources désignées → journalisation ;
- site local → ressources nécessaires à la migration ;
- ressources privées → endpoints/API cloud ;
- administrateurs → chemin d’accès contrôlé.

Pour chaque flux, indique les flux qui ne doivent pas être possibles, par exemple Internet → base de données, ou environnement de test → données de production non autorisées.

### Étape 3 — Choisir la connectivité entre réseaux

Compare deux options :
- peerings ciblés entre les réseaux qui doivent communiquer ;
- un hub de transit centralisé qui gère les échanges communs.

Note les limites de transit, la gestion des routes, la redondance, la supervision, les coûts et les opérations courantes. Ne suppose pas que le peering est transitif. Si le hub doit inspecter le trafic, vérifie que les routes aller et retour passent par les appliances prévues.

### Étape 4 — Intégrer le réseau local

Choisis VPN site à site ou liaison dédiée en fonction du délai, des performances, de la sécurité et du coût. Documente les plages annoncées, les routes principales et de secours, les politiques de filtrage et les tests de bascule. Vérifie que les deux réseaux peuvent résoudre les noms requis.

### Étape 5 — Prévoir les endpoints privés

Liste les services qui doivent être consommés depuis un réseau privé. Configure les endpoints proposés par le fournisseur, le DNS associé et les règles qui autorisent les clients appropriés. Vérifie que le trafic utilise le chemin attendu et que les identités possèdent encore les droits nécessaires.

### Étape 6 — Concevoir le plan de sécurité

Associe chaque flux autorisé à une règle précise et à un propriétaire. Utilise des groupes de sécurité ou mécanismes équivalents pour les cibles, et ajoute des contrôles subnet ou firewall centraux selon les exigences. Ajoute la journalisation utile pour prouver qu’un flux est accepté ou rejeté.

### Étape 7 — Définir les tests de réception

Le réseau est validé si :
- les noms publics et privés résolvent la cible attendue ;
- les routes effectives correspondent au dessin ;
- les flux autorisés aboutissent ;
- les flux interdits échouent ;
- l’accès à la base reste privé ;
- la connectivité hybride fonctionne dans les deux sens selon la politique ;
- les endpoints privés sont utilisés par les clients prévus ;
- la panne d’une cible est détectée ;
- les alertes remontent ;
- la bascule est testée ;
- les coûts attendus et les limites sont documentés.

### Étape 8 — Préparer l’exploitation

Maintiens un diagramme actualisé, un inventaire de CIDR, un registre des règles, une liste des propriétaires de flux, un tableau des dépendances, une procédure de diagnostic et une procédure de retour arrière. La documentation doit être assez précise pour permettre à un autre opérateur de comprendre pourquoi chaque route et chaque règle existe.

## 16. Exercices d’analyse de panne

### Cas A — Le serveur privé ne peut pas télécharger des mises à jour

Hypothèses possibles : route par défaut absente, NAT indisponible, règle de sortie trop restrictive, résolution DNS incorrecte, destination externe bloquée, route envoyant le trafic vers une appliance inactive ou service distant inaccessible.

Méthode :
1. résoudre le nom depuis le serveur ;
2. examiner la route effective ;
3. vérifier la configuration et les métriques du NAT ;
4. examiner les règles de sortie et les journaux ;
5. tester la destination et le port ;
6. comparer avec un serveur connu comme fonctionnel.

Ne pas attribuer une IP publique au serveur comme première réponse. Identifie d’abord le composant manquant.

### Cas B — A et B sont peerés, mais les ressources A n’atteignent pas C

Si A est peeré avec B et B avec C, ne présume pas que B transfère automatiquement le trafic entre A et C. Examine les propriétés non transitives du peering, le service de transit utilisé, les routes de chaque réseau et les règles de sécurité. Selon le fournisseur, un transit peut exiger un hub dédié ou une appliance.

### Cas C — Le VPN est actif, mais la connexion TCP échoue

Vérifie les routes annoncées et installées, les plages autorisées, les règles des deux côtés, le chemin retour, les ACL sans état, les MTU et l’état du service. Un tunnel actif ne certifie pas que la destination réseau est joignable.

### Cas D — Le nom du service privé retourne une IP publique

Examine la zone DNS privée, son association au réseau, l’enregistrement correspondant, le résolveur utilisé par la VM et tout redirecteur DNS. Le service privé peut être correctement créé tout en restant ignoré par les clients si la résolution n’est pas alignée.

### Cas E — Les petits paquets passent mais un transfert volumineux se bloque

Considère la MTU, la découverte de MTU de chemin, le MSS TCP, le tunnel et les filtres ICMP. Compare un test de petite taille et un test plus grand, puis examine les compteurs d’erreur et les journaux disponibles. Évite de supposer que la panne vient toujours de la MTU ; vérifie d’abord l’ensemble du chemin.

### Cas F — Le serveur B est sain mais l’application échoue en cas de panne de A

Vérifie que le répartiteur retire bien A, que B possède les dépendances et la capacité nécessaires, que la session n’est pas liée à A, que les données sont disponibles et que les contrôles de santé reflètent l’état métier pertinent.

## 17. Mini-évaluation

### Questions

1. Pourquoi est-il important de planifier les plages CIDR avant de connecter plusieurs réseaux ?
2. Pourquoi deux réseaux peerés ne fournissent-ils pas nécessairement une connectivité transitive ?
3. Quelle différence existe entre une route et une règle de sécurité ?
4. Pourquoi un VPN « actif » ne garantit-il pas un flux applicatif fonctionnel ?
5. Quelle différence fonctionnelle distingue un groupe de sécurité avec état d’une ACL sans état ?
6. À quoi sert un hub-and-spoke ?
7. Quels risques introduit une appliance d’inspection dans le chemin ?
8. Quelle différence générale existe entre une route statique et une route apprise par BGP ?
9. Pourquoi faut-il vérifier le chemin retour ?
10. Quel rôle joue le DNS dans un accès privé aux services ?
11. Un endpoint privé rend-il l’authentification inutile ?
12. Pourquoi IPv6 doit-il être vérifié séparément d’IPv4 ?
13. Quels symptômes peuvent évoquer un problème de MTU ?
14. Quelle différence y a-t-il entre un load balancer L4 et L7 ?
15. Pourquoi un contrôle de santé TCP peut-il être insuffisant ?
16. Quelles informations de base doivent figurer dans un ticket de panne réseau ?
17. Quels composants peuvent générer des coûts réseau ?
18. Comment un processus IaC réduit-il le risque des changements réseau ?
19. Quelles vérifications doit-on faire lors d’un test de bascule VPN ?
20. Pourquoi documenter les flux refusés autant que les flux autorisés ?

### Corrigé synthétique

1. Pour éviter les chevauchements et conserver un routage fiable lors des peerings et interconnexions.
2. Parce que le peering est souvent limité à une relation directe ; le transit requiert des fonctionnalités ou routes adaptées.
3. La route choisit où le paquet est envoyé ; la règle de sécurité décide si le flux est autorisé.
4. Le routage, le filtrage, le DNS, le port et le service peuvent encore être incorrects.
5. Le mécanisme avec état suit les sessions et gère généralement les réponses liées ; une ACL sans état évalue chaque direction séparément.
6. Pour centraliser certaines connexions et services partagés à mesure que le nombre de réseaux augmente.
7. Mauvaise symétrie, goulot de capacité, dépendance supplémentaire, risque de panne et configuration complexe.
8. Une route statique est définie explicitement ; BGP peut apprendre et annoncer dynamiquement des préfixes selon une politique.
9. Les réponses doivent pouvoir revenir ; certains filtres ou appliances exigent un chemin cohérent.
10. Il oriente le nom du service vers l’adresse attendue ; une mauvaise résolution peut détourner les clients du chemin privé.
11. Non. Les droits d’identité, les autorisations applicatives et la protection des secrets restent nécessaires.
12. Parce que ses adresses, routes et règles de filtrage peuvent différer d’IPv4.
13. Petits échanges réussis mais gros transferts bloqués, négociations qui se figent ou flux intermittents.
14. L4 utilise les éléments de transport ; L7 peut prendre des décisions fondées sur le protocole applicatif.
15. Un port peut répondre alors que la logique métier ou les dépendances sont en panne.
16. Source, destination, protocole/port, heure, environnement, nom et résultat du test.
17. Transfert de données, NAT, endpoints, load balancing, liens dédiés, journaux, inspection et adresses selon le tarif.
18. Il rend les changements versionnés, révisables, testables et reproductibles.
19. Routes reçues/installées, priorité, délais de convergence, sessions actives et connectivité applicative.
20. Ils permettent de prouver la segmentation, d’identifier un flux légitime bloqué et de détecter des tentatives inattendues.

## 18. Checklist de revue d’architecture

### Adressage et routage
- [ ] Le plan IPv4/IPv6 est inventorié et non chevauchant avec les réseaux à relier.
- [ ] Chaque route importante possède un objectif, une cible et un propriétaire.
- [ ] Les tables effectives ont été vérifiées pour les ressources critiques.
- [ ] Les routes propagées par BGP sont filtrées et observées.
- [ ] Les chemins aller et retour sont documentés.
- [ ] Les routes par défaut n’envoient pas involontairement le trafic privé vers la mauvaise cible.

### Sécurité
- [ ] Les sources et ports autorisés correspondent aux besoins métier.
- [ ] Les bases et plans d’administration ne sont pas exposés par accident.
- [ ] Les règles sans état couvrent les directions nécessaires.
- [ ] Les appliances d’inspection disposent d’un chemin de retour cohérent et d’une capacité suffisante.
- [ ] Les logs de sécurité et de flux sont accessibles aux personnes autorisées.
- [ ] Les exceptions temporaires ont une échéance et un propriétaire.

### Connectivité et services
- [ ] Le VPN ou la liaison dédiée a été testé dans chaque sens.
- [ ] La bascule de secours a été testée et chronométrée.
- [ ] Les peerings sont configurés des deux côtés si le fournisseur l’exige.
- [ ] Les limitations du transit et les chemins entre spokes sont compris.
- [ ] Les endpoints privés utilisent les bonnes zones DNS et règles réseau.
- [ ] Le DNS public, privé et hybride est documenté.

### Opérations et coût
- [ ] Les métriques, journaux et alertes couvrent les composants critiques.
- [ ] Les coûts de transit, NAT, endpoints et logs sont estimés.
- [ ] Les quotas et limites sont examinés.
- [ ] L’Infrastructure as Code est revue et testée.
- [ ] Un plan de retour arrière est disponible.
- [ ] Les procédures de reprise et les responsables d’incident sont connus.

## 19. Glossaire

- **ACL réseau** : ensemble de règles de filtrage associé à une frontière réseau, souvent sans état selon la plateforme.
- **BGP** : protocole d’échange de routes entre domaines de routage, utilisé notamment dans les liaisons hybrides.
- **CIDR** : notation qui exprime une plage d’adresses par son préfixe.
- **DNS hybride** : résolution des noms entre environnements cloud et réseaux locaux.
- **Endpoint privé** : point de connexion privé vers un service pris en charge, selon le fournisseur.
- **Forced tunneling** : politique qui dirige certaines sorties vers un chemin central ou un équipement d’inspection.
- **Hub-and-spoke** : topologie composée d’un centre de connectivité et de plusieurs réseaux périphériques.
- **IaC** : description versionnée de l’infrastructure par des fichiers et des outils automatisés.
- **Load balancer** : répartiteur des connexions ou requêtes entre cibles.
- **MTU** : taille maximale d’un paquet de couche réseau transporté sur un lien donné.
- **NAT** : traduction d’adresses réseau, souvent utilisée pour la sortie des ressources privées.
- **NVA** : appliance réseau virtuelle, par exemple un pare-feu tiers ou un routeur logiciel.
- **Peering** : relation de connectivité entre deux réseaux virtuels.
- **Route effective** : ensemble de routes réellement applicables à une ressource, d’après la plateforme.
- **Transit gateway** : service de connectivité centralisé destiné à relier plusieurs réseaux et connexions.
- **VPN site à site** : connexion chiffrée entre deux réseaux ou passerelles.
- **Zone de disponibilité** : domaine d’infrastructure cloud ayant un niveau d’indépendance vis-à-vis de certaines pannes.

## 20. Références officielles

Consulte la documentation officielle du fournisseur choisi avant de traduire les modèles de ce cours en configuration réelle :

- AWS — Présentation d’Amazon VPC : https://docs.aws.amazon.com/vpc/latest/userguide/
- AWS — Tables de routage : https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Route_Tables.html
- AWS — Bases du VPC peering et limites de transit : https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-basics.html
- Microsoft Azure — Virtual Network peering : https://learn.microsoft.com/azure/virtual-network/virtual-network-peering-overview
- Microsoft Azure — Architecture hub-and-spoke : https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke
- Google Cloud — Présentation des réseaux VPC : https://docs.cloud.google.com/vpc/docs/overview
- Google Cloud — Routes VPC : https://docs.cloud.google.com/vpc/docs/routes
- Google Cloud — Private Service Connect : https://docs.cloud.google.com/vpc/docs/about-accessing-vpc-hosted-services-endpoints
- IETF — RFC 1918, adresses IPv4 privées : https://www.rfc-editor.org/rfc/rfc1918
- IETF — RFC 4632, CIDR : https://www.rfc-editor.org/rfc/rfc4632
- IETF — RFC 8200, IPv6 : https://www.rfc-editor.org/rfc/rfc8200

Les services et leurs limites évoluent. Les liens officiels doivent être consultés pour les prérequis, les options de routage, les comportements par défaut et les tarifs de la région cible.


## À retenir

Un réseau cloud intermédiaire se conçoit en partant des besoins de communication, du plan d’adressage et des frontières de sécurité. Les choix entre peering, hub-and-spoke, VPN, liaison dédiée et endpoints privés déterminent les chemins, le rayon d’impact, l’observabilité et les coûts. Les routes, le filtrage, le DNS et l’application doivent être diagnostiqués ensemble, sans supposer que l’un remplace l’autre.

**Règle appliquée à tous les schémas de ce cours :** les circuits réseau possèdent des flèches directionnelles explicites ; les équipements utiles (client, routeur logique, pare-feu, passerelle VPN/NAT, load balancer, serveur ou base de données) sont représentés ou nommés ; les chemins bidirectionnels sont marqués dans les deux sens lorsqu’ils sont pertinents. Les schémas sont pédagogiques et doivent être adaptés au fournisseur et à l’architecture réelle.
