<style>
.aci-expert{color:#dbe7f5;background:#090d14;padding:1rem;border:1px solid #253244;border-radius:14px;line-height:1.65}
.aci-expert h1,.aci-expert h2,.aci-expert h3{color:#f4f8ff;line-height:1.25}
.aci-expert h2{border-bottom:1px solid #263548;padding-bottom:.45rem;margin-top:2rem}
.aci-expert strong{color:#f8fbff}.aci-expert code{color:#8ce7ff;background:#101b29;padding:.1rem .25rem;border-radius:4px}
.aci-expert .note{border-left:3px solid #38bdf8;padding:.7rem 1rem;background:#0d1825;border-radius:0 8px 8px 0}
.aci-expert .warn{border-left:3px solid #f59e0b;padding:.7rem 1rem;background:#211a0e;border-radius:0 8px 8px 0}
.aci-expert .good{border-left:3px solid #34d399;padding:.7rem 1rem;background:#0d211b;border-radius:0 8px 8px 0}
.aci-expert svg{display:block;width:100%;height:auto;max-width:100%;margin:1rem auto;background:#0b111b;border:1px solid #263548;border-radius:12px}
@keyframes aciExpertFlow{to{stroke-dashoffset:-34}}
.aci-expert .flow{stroke-dasharray:8 8;animation:aciExpertFlow 3.2s linear infinite}
@media(prefers-reduced-motion:reduce){.aci-expert .flow{animation:none}}
</style>
<div class="aci-expert">

# Cisco ACI — Architecture, ingénierie et exploitation avancées

**Niveau : Expert** · **Prérequis :** modèle objet ACI, fabric leaf-spine, EPG/BD/VRF, contrats, L3Out et dépannage de niveau intermédiaire.

## Objectifs opérationnels

À la fin de ce parcours, vous devez pouvoir concevoir une fabric ACI résiliente, expliquer la programmation des politiques jusqu'au dataplane, raisonner sur le routage externe et les domaines de panne, diagnostiquer des problèmes complexes, planifier une évolution sans surprise et automatiser les changements de façon contrôlée. Le niveau expert ne consiste pas à mémoriser davantage d'objets : il consiste à prévoir les effets de leurs relations et à prouver le comportement réel du réseau.

> **Périmètre des commandes :** les chemins d'interface, noms de champs et commandes varient selon la version d'APIC, le matériel et les intégrations. Vérifiez toujours la documentation correspondant à la release déployée. Les exemples sont des modèles de raisonnement, pas une procédure aveugle à copier en production.

## 1. Le modèle mental expert : trois plans, plusieurs vérités

ACI combine une fabric IP underlay, un transport overlay VXLAN, un système de contrôle distribué et un modèle de politique piloté par l'APIC. Il faut séparer ces dimensions lors du diagnostic.

- **Plan de gestion :** APIC, API, RBAC, audit, modèles et orchestration. Il exprime l'intention et collecte l'état ; ce n'est pas le chemin de données de chaque paquet.
- **Plan de contrôle :** découverte des équipements, apprentissage/localisation des endpoints, informations de reachability et distribution des données nécessaires au forwarding.
- **Plan de données :** ASIC des leafs, encapsulation/décapsulation VXLAN, lookup de destination, application des règles de politique et transmission physique.
- **Underlay :** connectivité IP entre leafs et spines, généralement construite et maintenue par les mécanismes de la fabric.
- **Overlay :** segments logiques identifiés par des VNI et politiques indépendants de la topologie physique.

Un écran APIC vert ne prouve pas à lui seul que l'application répond. Une session API réussie ne prouve pas qu'une route retour existe. Un endpoint visible ne prouve pas qu'un contrat autorise le flux. Il faut confronter l'intention, l'état de contrôle et les compteurs/observations du dataplane.

<svg viewBox="0 0 960 390" role="img" aria-label="Séparation des plans ACI et flux de diagnostic" xmlns="http://www.w3.org/2000/svg"><defs><marker id="ax1" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#65d8ff"/></marker><marker id="ax2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#a78bfa"/></marker></defs><rect x="20" y="20" width="920" height="88" rx="12" fill="#111d2c" stroke="#a78bfa"/><text x="42" y="48" fill="#c4b5fd" font-size="16" font-weight="700">GESTION / INTENTION</text><rect x="42" y="60" width="170" height="32" rx="6" fill="#2a2142" stroke="#a78bfa"/><text x="127" y="81" fill="#f5f3ff" text-anchor="middle" font-size="13">APIC + API + RBAC</text><rect x="250" y="60" width="190" height="32" rx="6" fill="#2a2142" stroke="#a78bfa"/><text x="345" y="81" fill="#f5f3ff" text-anchor="middle" font-size="13">Modèle de politique</text><path d="M440 76 H492" stroke="#a78bfa" stroke-width="2" marker-end="url(#ax2)"/><text x="515" y="81" fill="#d8ccff" font-size="12">déployer / observer</text><rect x="20" y="130" width="920" height="96" rx="12" fill="#10202a" stroke="#38bdf8"/><text x="42" y="158" fill="#7dd3fc" font-size="16" font-weight="700">CONTRÔLE / REACHABILITY</text><rect x="42" y="170" width="210" height="40" rx="6" fill="#123044" stroke="#38bdf8"/><text x="147" y="195" fill="#e0f2fe" text-anchor="middle" font-size="13">Localisation endpoints</text><path d="M252 190 H315" stroke="#65d8ff" stroke-width="2" marker-end="url(#ax1)"/><rect x="320" y="170" width="205" height="40" rx="6" fill="#123044" stroke="#38bdf8"/><text x="422" y="195" fill="#e0f2fe" text-anchor="middle" font-size="13">Routes / informations fabric</text><path d="M525 190 H585" stroke="#65d8ff" stroke-width="2" marker-end="url(#ax1)"/><rect x="590" y="170" width="300" height="40" rx="6" fill="#123044" stroke="#38bdf8"/><text x="740" y="195" fill="#e0f2fe" text-anchor="middle" font-size="13">État distribué vers les leafs</text><rect x="20" y="248" width="920" height="120" rx="12" fill="#10251f" stroke="#34d399"/><text x="42" y="276" fill="#6ee7b7" font-size="16" font-weight="700">DONNÉES / FORWARDING</text><rect x="42" y="291" width="190" height="56" rx="7" fill="#12372b" stroke="#34d399"/><text x="137" y="315" fill="#d1fae5" text-anchor="middle" font-size="13">Leaf source</text><text x="137" y="333" fill="#a7f3d0" text-anchor="middle" font-size="11">classification + policy</text><path d="M232 319 H370" stroke="#34d399" stroke-width="3" marker-end="url(#ax1)" class="flow"/><rect x="375" y="291" width="190" height="56" rx="7" fill="#12372b" stroke="#34d399"/><text x="470" y="315" fill="#d1fae5" text-anchor="middle" font-size="13">Overlay VXLAN</text><text x="470" y="333" fill="#a7f3d0" text-anchor="middle" font-size="11">transport underlay IP</text><path d="M565 319 H700" stroke="#34d399" stroke-width="3" marker-end="url(#ax1)" class="flow"/><rect x="705" y="291" width="190" height="56" rx="7" fill="#12372b" stroke="#34d399"/><text x="800" y="315" fill="#d1fae5" text-anchor="middle" font-size="13">Leaf destination</text><text x="800" y="333" fill="#a7f3d0" text-anchor="middle" font-size="11">décapsulation + sortie</text></svg>

### Méthode d'investigation

1. Définir précisément le flux : source/destination, protocole, port, sens, heure et résultat attendu.
2. Vérifier l'attachement réel des endpoints et leur EPG, pas seulement le dessin logique.
3. Confirmer que les objets sont déployés et que la politique effective correspond à l'intention.
4. Examiner les routes et la connectivité underlay/overlay dans les deux sens.
5. Observer les compteurs, drops, captures et journaux disponibles sur les points pertinents.
6. Tester une hypothèse à la fois, avec une condition de réussite et une possibilité de retour arrière.

## 2. Architecture physique et domaines de panne

### 2.1 Leaf-spine et chemins de forwarding

Les endpoints se connectent aux leafs. Les spines fournissent la connectivité fabric entre leafs ; ils ne se comportent pas comme des commutateurs d'accès classiques et ne constituent pas un endroit où l'on applique la politique applicative ordinaire. Les chemins sont conçus pour exploiter la fabric, pas pour imposer un chemin L2 traditionnel entre racks.

Les liens redondants ne signifient pas automatiquement que toutes les pannes sont sans impact. Il faut évaluer :

- perte d'un lien leaf-spine et convergence associée ;
- perte d'un spine, y compris les effets sur la capacité résiduelle ;
- panne d'un leaf et impact sur les endpoints qui lui sont attachés ;
- panne d'un contrôleur APIC et quorum/continuité de gestion ;
- panne d'un service externe, d'un firewall, d'un route reflector ou d'une dépendance DNS/NTP/AAA ;
- erreurs de configuration communes déployées simultanément sur plusieurs chemins.

Une conception tolérante à une panne doit rester correcte dans l'état dégradé : capacité, convergence, sécurité, observabilité et procédure d'exploitation doivent être testées.

### 2.2 Capacité et oversubscription

L'oversubscription doit être évaluée par couche et par scénario de trafic. Additionner les débits nominaux des serveurs et comparer au débit d'un uplink est un premier indicateur, pas une preuve de congestion. Les flux est-ouest peuvent se concentrer sur certains chemins ; les sauvegardes, migrations VM, répliques de stockage et bursts peuvent saturer une ressource pendant quelques secondes.

Mesurez les débits, drops, erreurs physiques, utilisation des buffers/queues si disponibles, microbursts et latence. Utilisez une période représentative et une période de pointe. La capacité de secours doit être calculée après perte du composant le plus contraignant, pas uniquement dans l'état nominal.

### 2.3 Câblage, profils et découverte

Les profils d'interface, politiques de port, sélecteurs, LLDP/CDP, domaines physiques, pools VLAN et attachements EPG doivent être cohérents. Les erreurs d'attachement ressemblent souvent à des erreurs de contrat : l'endpoint peut apparaître dans un EPG inattendu ou le VLAN encapsulé peut ne pas correspondre au domaine prévu.

Avant de modifier un port, documentez le serveur ou hyperviseur connecté, le mode access/trunk attendu, les VLANs transportés, la redondance du serveur, la politique d'interface et l'impact d'une reprogrammation. Sur un port vPC, contrôlez les deux membres et le comportement de l'agrégat, pas seulement un côté.

## 3. Modèle objet et sémantique de politique

Le modèle ACI exprime l'intention par des objets reliés entre eux. L'erreur de conception fréquente est de raisonner sur un objet isolé alors que le comportement dépend d'une chaîne de relations.

- **Tenant :** domaine d'administration et de politique logique.
- **VRF :** contexte de routage L3.
- **Bridge Domain (BD) :** domaine L2 logique, associé à un VRF pour les fonctions L3 usuelles.
- **Application Profile :** regroupement logique d'EPG pour une application.
- **EPG :** groupe d'endpoints partageant une politique commune.
- **Contract :** relation de communication entre consommateurs et fournisseurs.
- **Filter / entry :** critères de classification L4/L3 autorisés par un contrat.
- **L3Out :** connexion logique de routage vers l'extérieur de la fabric.

<svg viewBox="0 0 960 420" role="img" aria-label="Relations entre objets de politique ACI" xmlns="http://www.w3.org/2000/svg"><defs><marker id="ax3" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#65d8ff"/></marker></defs><rect x="30" y="22" width="900" height="72" rx="10" fill="#19172b" stroke="#a78bfa"/><text x="480" y="49" fill="#ddd6fe" text-anchor="middle" font-size="17" font-weight="700">Tenant</text><text x="480" y="73" fill="#c4b5fd" text-anchor="middle" font-size="12">frontière logique d'administration</text><path d="M480 94 V122 H250 V145 M480 122 H710 V145" fill="none" stroke="#65d8ff" stroke-width="2" marker-end="url(#ax3)"/><rect x="120" y="150" width="260" height="60" rx="8" fill="#10283a" stroke="#38bdf8"/><text x="250" y="175" fill="#bae6fd" text-anchor="middle" font-size="15" font-weight="700">VRF</text><text x="250" y="194" fill="#dbeafe" text-anchor="middle" font-size="12">contexte de routage</text><rect x="580" y="150" width="260" height="60" rx="8" fill="#10283a" stroke="#38bdf8"/><text x="710" y="175" fill="#bae6fd" text-anchor="middle" font-size="15" font-weight="700">Application Profile</text><text x="710" y="194" fill="#dbeafe" text-anchor="middle" font-size="12">regroupe les EPG</text><path d="M250 210 V245" stroke="#65d8ff" stroke-width="2" marker-end="url(#ax3)"/><rect x="120" y="250" width="260" height="58" rx="8" fill="#12372b" stroke="#34d399"/><text x="250" y="275" fill="#d1fae5" text-anchor="middle" font-size="15" font-weight="700">Bridge Domain</text><text x="250" y="294" fill="#a7f3d0" text-anchor="middle" font-size="12">segment L2 + paramètres L3</text><path d="M710 210 V245" stroke="#65d8ff" stroke-width="2" marker-end="url(#ax3)"/><rect x="580" y="250" width="260" height="58" rx="8" fill="#12372b" stroke="#34d399"/><text x="710" y="275" fill="#d1fae5" text-anchor="middle" font-size="15" font-weight="700">EPG</text><text x="710" y="294" fill="#a7f3d0" text-anchor="middle" font-size="12">classification + politique</text><path d="M580 279 H470 V350 H380" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#ax3)"/><rect x="100" y="325" width="280" height="66" rx="8" fill="#30230e" stroke="#fbbf24"/><text x="240" y="350" fill="#fde68a" text-anchor="middle" font-size="15" font-weight="700">Contract + Filter</text><text x="240" y="371" fill="#fef3c7" text-anchor="middle" font-size="12">autorisation explicite des flux</text><text x="620" y="360" fill="#94a3b8" font-size="12">Relations exactes à vérifier</text><text x="620" y="378" fill="#94a3b8" font-size="12">dans la version et le design retenus</text></svg>

### 3.1 Séparer segmentation, adressage et autorisation

Un BD ne doit pas être confondu avec un EPG. Le BD décrit notamment le domaine L2 et ses paramètres associés ; l'EPG classe les endpoints dans une politique. Plusieurs EPG peuvent partager un BD dans certains designs, ce qui signifie qu'ils partagent des propriétés de segment sans pour autant devenir une seule politique applicative. Inversement, la séparation en BDs différents n'est pas à elle seule une règle de sécurité suffisante : les chemins routés et les contrats doivent être étudiés.

La conception commence par une matrice de communication métier : qui initie, vers quoi, sur quel protocole, avec quel besoin opérationnel et quelle justification ? On traduit ensuite cette matrice en EPG, contrats, filtres et relations provider/consumer. La matrice est un artefact de gouvernance qui permet d'expliquer pourquoi un flux est permis.

### 3.2 Contrats : ne pas confondre présence et effet

Créer un contrat ne garantit pas que deux EPG communiquent. Il faut confirmer le provider, le consumer, la portée de l'objet, le filtre associé, les ports, les directions attendues et les éventuelles options de routage/politique. Le contrat est un mécanisme d'autorisation, pas un test de connectivité complet.

Un filtre trop large — par exemple une autorisation IP-any-any pour corriger rapidement une application — peut masquer le vrai défaut et transformer un problème fonctionnel en exposition de sécurité. La règle correcte est la plus étroite qui satisfait le besoin documenté. Prévoyez une procédure d'expiration pour les exceptions temporaires.

### 3.3 pcTag et classification effective

ACI utilise des identifiants internes de classification de politique, dont les pcTags, pour référencer des groupes dans les mécanismes de forwarding. Il faut les traiter comme des valeurs générées par le système, et non comme des identifiants que l'on invente ou que l'on considère immuables. Après une modification de politique, validez la classification réelle de l'endpoint et les règles effectives plutôt que de déduire le résultat d'un nom d'objet.

## 4. Underlay, overlay et VXLAN

L'underlay transporte les paquets encapsulés entre les leafs. L'overlay fournit une topologie logique où les segments sont identifiés par des VNI et où l'endpoint distant peut être atteint à travers la fabric. Une panne de l'underlay peut donc faire échouer des flux de plusieurs applications même si leurs contrats n'ont pas changé.

<svg viewBox="0 0 960 320" role="img" aria-label="Encapsulation VXLAN à travers underlay IP" xmlns="http://www.w3.org/2000/svg"><defs><marker id="ax4" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#65d8ff"/></marker></defs><rect x="25" y="45" width="190" height="230" rx="12" fill="#10251f" stroke="#34d399"/><text x="120" y="72" fill="#6ee7b7" text-anchor="middle" font-size="16" font-weight="700">Leaf source</text><rect x="48" y="95" width="144" height="45" rx="6" fill="#12372b" stroke="#34d399"/><text x="120" y="113" fill="#d1fae5" text-anchor="middle" font-size="12">Endpoint A</text><text x="120" y="129" fill="#a7f3d0" text-anchor="middle" font-size="11">EPG / pcTag</text><rect x="48" y="163" width="144" height="83" rx="6" fill="#112c42" stroke="#38bdf8"/><text x="120" y="185" fill="#bae6fd" text-anchor="middle" font-size="12">Paquet encapsulé</text><text x="120" y="204" fill="#e0f2fe" text-anchor="middle" font-size="11">Ethernet + VXLAN</text><text x="120" y="220" fill="#e0f2fe" text-anchor="middle" font-size="11">+ UDP / IP underlay</text><path d="M215 205 H330" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax4)" class="flow"/><rect x="335" y="80" width="290" height="170" rx="12" fill="#10202a" stroke="#38bdf8"/><text x="480" y="108" fill="#7dd3fc" text-anchor="middle" font-size="16" font-weight="700">Underlay fabric</text><rect x="360" y="126" width="100" height="54" rx="6" fill="#123044" stroke="#38bdf8"/><text x="410" y="148" fill="#e0f2fe" text-anchor="middle" font-size="12">Spine A</text><text x="410" y="165" fill="#bae6fd" text-anchor="middle" font-size="10">IP transit</text><rect x="500" y="126" width="100" height="54" rx="6" fill="#123044" stroke="#38bdf8"/><text x="550" y="148" fill="#e0f2fe" text-anchor="middle" font-size="12">Spine B</text><text x="550" y="165" fill="#bae6fd" text-anchor="middle" font-size="10">IP transit</text><path d="M460 153 H500" stroke="#65d8ff" stroke-width="2" marker-end="url(#ax4)"/><text x="480" y="215" fill="#bae6fd" text-anchor="middle" font-size="12">IP reachability + MTU</text><path d="M625 205 H740" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax4)" class="flow"/><rect x="745" y="45" width="190" height="230" rx="12" fill="#10251f" stroke="#34d399"/><text x="840" y="72" fill="#6ee7b7" text-anchor="middle" font-size="16" font-weight="700">Leaf destination</text><rect x="768" y="95" width="144" height="45" rx="6" fill="#12372b" stroke="#34d399"/><text x="840" y="113" fill="#d1fae5" text-anchor="middle" font-size="12">Endpoint B</text><text x="840" y="129" fill="#a7f3d0" text-anchor="middle" font-size="11">EPG destination</text><rect x="768" y="163" width="144" height="83" rx="6" fill="#112c42" stroke="#38bdf8"/><text x="840" y="185" fill="#bae6fd" text-anchor="middle" font-size="12">Décapsulation</text><text x="840" y="204" fill="#e0f2fe" text-anchor="middle" font-size="11">lookup de politique</text><text x="840" y="220" fill="#e0f2fe" text-anchor="middle" font-size="11">puis sortie physique</text></svg>

### 4.1 MTU et taille effective

L'encapsulation ajoute des en-têtes. Une MTU sous-dimensionnée peut produire des symptômes trompeurs : petites requêtes réussies, transferts volumineux qui bloquent, connexions TCP qui ralentissent ou certaines applications qui échouent. La validation doit couvrir le MTU effectif de bout en bout, les liens physiques, les équipements intermédiaires et le comportement de Path MTU Discovery. Ne désactivez pas les mécanismes de découverte pour contourner un problème sans comprendre le chemin.

### 4.2 Diagnostiquer un problème d'overlay

- Vérifier la connectivité IP underlay entre les points de terminaison fabric concernés.
- Vérifier les interfaces, erreurs, pertes et changements de topologie récents.
- Confirmer que le endpoint est appris sur le bon leaf et que l'information distante est cohérente.
- Contrôler le VLAN/VNI/BD et l'attachement effectif, selon le type d'endpoint.
- Vérifier les règles de politique et les drops sur les leafs source/destination.
- Comparer un flux qui fonctionne au flux en échec en ne changeant qu'un paramètre à la fois.

## 5. Routage L3Out et échange de routes

Un L3Out représente la connexion logique de la fabric vers un domaine de routage externe. Les éléments impliqués comprennent le routage externe, les interfaces/chemins, les politiques d'import/export, les External EPG et les contrats. Le design doit être pensé dans les deux sens : l'annonce d'une route ne prouve pas que la route retour existe, et la présence d'une route ne prouve pas que la politique de sécurité autorise le flux.

<svg viewBox="0 0 960 345" role="img" aria-label="Chemin aller-retour entre EPG interne et réseau externe par L3Out" xmlns="http://www.w3.org/2000/svg"><defs><marker id="ax5" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#65d8ff"/></marker></defs><rect x="30" y="70" width="190" height="205" rx="12" fill="#10251f" stroke="#34d399"/><text x="125" y="98" fill="#6ee7b7" text-anchor="middle" font-size="16" font-weight="700">EPG interne</text><rect x="55" y="120" width="140" height="45" rx="6" fill="#12372b" stroke="#34d399"/><text x="125" y="139" fill="#d1fae5" text-anchor="middle" font-size="12">Client / service</text><text x="125" y="154" fill="#a7f3d0" text-anchor="middle" font-size="11">BD + VRF</text><rect x="55" y="190" width="140" height="55" rx="6" fill="#30230e" stroke="#fbbf24"/><text x="125" y="212" fill="#fde68a" text-anchor="middle" font-size="12">Contract</text><text x="125" y="230" fill="#fef3c7" text-anchor="middle" font-size="11">External EPG</text><path d="M220 150 H360" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax5)" class="flow"/><rect x="365" y="70" width="220" height="205" rx="12" fill="#10202a" stroke="#38bdf8"/><text x="475" y="98" fill="#7dd3fc" text-anchor="middle" font-size="16" font-weight="700">Border leaf / L3Out</text><rect x="390" y="120" width="170" height="45" rx="6" fill="#123044" stroke="#38bdf8"/><text x="475" y="139" fill="#e0f2fe" text-anchor="middle" font-size="12">Interface + adjacency</text><text x="475" y="154" fill="#bae6fd" text-anchor="middle" font-size="11">BGP / OSPF / statique</text><rect x="390" y="190" width="170" height="55" rx="6" fill="#123044" stroke="#38bdf8"/><text x="475" y="212" fill="#e0f2fe" text-anchor="middle" font-size="12">Import / export</text><text x="475" y="230" fill="#bae6fd" text-anchor="middle" font-size="11">route-map / filtres</text><path d="M585 150 H720" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax5)" class="flow"/><rect x="725" y="70" width="205" height="205" rx="12" fill="#19172b" stroke="#a78bfa"/><text x="827" y="98" fill="#ddd6fe" text-anchor="middle" font-size="16" font-weight="700">Réseau externe</text><rect x="750" y="120" width="155" height="45" rx="6" fill="#2a2142" stroke="#a78bfa"/><text x="827" y="139" fill="#f5f3ff" text-anchor="middle" font-size="12">Route vers préfixe</text><text x="827" y="154" fill="#ddd6fe" text-anchor="middle" font-size="11">ex. firewall / WAN</text><path d="M827 276 V310 H125 V276" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="8 6" marker-end="url(#ax5)" class="flow"/><text x="480" y="334" fill="#fde68a" text-anchor="middle" font-size="12">Retour : route externe + politique + état du firewall à confirmer</text></svg>

### 5.1 Import, export et filtrage

Les routes importées doivent être limitées aux préfixes nécessaires. Les routes exportées doivent être contrôlées afin d'éviter les fuites de routes, les annonces trop larges ou les dépendances implicites à un résumé. Pour BGP, documentez les voisins, ASN, timers pertinents, politiques de route, communautés, préférences et comportement en cas de retrait. Pour OSPF, documentez les zones, types de routes, coûts et frontières de redistribution. Pour des routes statiques, vérifiez la dépendance à l'état de l'interface et le risque de blackhole.

Le filtrage d'annonce et l'autorisation de trafic sont deux contrôles différents. Une route peut être présente tandis que le contrat bloque le flux ; un contrat peut autoriser le flux tandis qu'une route manque. Une investigation experte prouve séparément le chemin aller, le chemin retour et la décision de politique.

### 5.2 External EPG

L'External EPG représente des préfixes externes pour la politique. Les sous-réseaux et leur portée doivent correspondre au design réel. Des préfixes qui se chevauchent, des masques trop larges ou des hypothèses incorrectes sur la classification peuvent produire des décisions inattendues. Documentez quel External EPG représente chaque classe de réseau externe et comment les contrats sont associés.

### 5.3 Routage asymétrique et pare-feu

Si l'aller et le retour traversent des chemins ou des firewalls différents, les sessions stateful peuvent échouer même si chaque route existe. Vérifiez la symétrie attendue, le NAT, les tables de sessions du firewall, les routes de retour et la distribution du trafic. Ne concluez pas qu'ACI bloque le flux avant d'avoir établi où le paquet disparaît.

## 6. Sécurité : politique minimale, cloisonnement et gouvernance

La segmentation n'est efficace que si elle est compréhensible, testable et maintenue. L'objectif n'est pas de multiplier les contrats, mais de représenter les dépendances nécessaires avec une portée minimale.

### 6.1 Construire une matrice de flux durable

Pour chaque flux, conservez au minimum : propriétaire métier, source, destination, sens d'initiation, protocole/port, justification, criticité, date d'approbation, méthode de test, dépendances et échéance de révision. Distinguez les flux applicatifs des flux d'administration, de supervision, de sauvegarde et de découverte. Ces familles ont des exigences différentes et ne devraient pas être autorisées par une règle générique sans justification.

### 6.2 Microsegmentation et identité des endpoints

Les EPG dynamiques, les intégrations hyperviseur et les critères d'identification des endpoints peuvent faciliter la segmentation, mais ajoutent des dépendances. Une erreur de mapping de port group, de VLAN, de domaine VMM ou de politique d'attachement peut classer une charge dans un EPG inattendu. Lorsqu'un endpoint est mal classé, corrigez d'abord le mécanisme de classification et vérifiez l'effet avant d'élargir les contrats.

La microsegmentation intra-EPG dépend du mode de politique et des fonctionnalités réellement disponibles dans la release et le design. Ne supposez pas que deux endpoints d'un même EPG sont isolés l'un de l'autre par défaut. Énoncez clairement les objectifs de segmentation, les mécanismes retenus et les tests qui les démontrent.

### 6.3 RBAC, comptes de service et audit

Appliquez le moindre privilège à l'APIC et aux systèmes d'automatisation. Préférez des comptes de service nominatifs par outil ou pipeline, des secrets stockés dans un coffre approprié et une rotation maîtrisée. Évitez les comptes partagés à privilèges complets et les secrets dans les dépôts, journaux ou fichiers de configuration. Les changements doivent être attribuables à une identité et reliés à une demande approuvée.

### 6.4 Contrôler l'accès de gestion

Le réseau de gestion de l'APIC, les comptes d'administration, les services d'authentification, la résolution DNS, NTP et les certificats forment une surface critique. Restreignez les sources d'administration, surveillez les connexions, synchronisez les horloges et documentez le mode de récupération lorsque l'AAA externe ou une dépendance de gestion est indisponible.

## 7. Haute disponibilité : APIC, vPC et Multi-Pod/Multi-Site

La redondance matérielle, la disponibilité de la gestion et la continuité applicative sont des objectifs différents. Un cluster APIC hautement disponible ne remplace pas la redondance des leafs, et deux fabrics connectées ne garantissent pas automatiquement une reprise applicative correcte.

### 7.1 Cluster APIC

Respectez les recommandations de topologie, de version et de taille de cluster de la documentation de la release. Contrôlez la santé du cluster, l'état de réplication, les alertes et la connectivité de gestion. Évitez les opérations qui risquent de réduire simultanément le nombre de contrôleurs disponibles. Une panne APIC n'a pas le même effet qu'une panne de forwarding sur un leaf : les politiques déjà programmées peuvent continuer à être appliquées, mais les changements, certaines fonctions de contrôle et l'observabilité peuvent être affectés.

### 7.2 vPC et doubles attachements

Un vPC peut fournir une attache redondante vers un équipement, mais les paramètres de domaine, la cohérence des ports, les politiques d'interface et le câblage doivent être cohérents. La redondance côté réseau n'aide pas si l'hôte, l'hyperviseur ou le service ne supporte pas le mode d'attachement choisi. Testez la perte de chaque membre, le rétablissement, les erreurs de cohérence et les effets sur les sessions actives.

### 7.3 Multi-Pod et Multi-Site : ne pas les confondre

**Multi-Pod** étend une fabric ACI à plusieurs pods, avec une architecture et des dépendances inter-pods spécifiques. **Multi-Site** coordonne plusieurs fabrics distinctes au moyen d'une architecture de gestion/orchestration dédiée. Ils ne sont pas interchangeables et n'ont ni les mêmes domaines de panne ni les mêmes procédures opérationnelles.

<svg viewBox="0 0 960 360" role="img" aria-label="Comparaison conceptuelle Multi-Pod et Multi-Site" xmlns="http://www.w3.org/2000/svg"><defs><marker id="ax6" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#65d8ff"/></marker></defs><text x="240" y="32" fill="#7dd3fc" text-anchor="middle" font-size="18" font-weight="700">Multi-Pod</text><rect x="25" y="50" width="430" height="255" rx="12" fill="#0e1e2b" stroke="#38bdf8"/><rect x="45" y="78" width="180" height="145" rx="9" fill="#10283a" stroke="#38bdf8"/><text x="135" y="101" fill="#bae6fd" text-anchor="middle" font-size="14" font-weight="700">Pod 1</text><rect x="70" y="117" width="130" height="35" rx="5" fill="#123044" stroke="#38bdf8"/><text x="135" y="139" fill="#e0f2fe" text-anchor="middle" font-size="12">Leaf-spine</text><rect x="70" y="165" width="130" height="35" rx="5" fill="#123044" stroke="#38bdf8"/><text x="135" y="187" fill="#e0f2fe" text-anchor="middle" font-size="12">Endpoints</text><rect x="255" y="78" width="180" height="145" rx="9" fill="#10283a" stroke="#38bdf8"/><text x="345" y="101" fill="#bae6fd" text-anchor="middle" font-size="14" font-weight="700">Pod 2</text><rect x="280" y="117" width="130" height="35" rx="5" fill="#123044" stroke="#38bdf8"/><text x="345" y="139" fill="#e0f2fe" text-anchor="middle" font-size="12">Leaf-spine</text><rect x="280" y="165" width="130" height="35" rx="5" fill="#123044" stroke="#38bdf8"/><text x="345" y="187" fill="#e0f2fe" text-anchor="middle" font-size="12">Endpoints</text><path d="M225 143 H255" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax6)" class="flow"/><rect x="130" y="242" width="220" height="42" rx="7" fill="#19172b" stroke="#a78bfa"/><text x="240" y="268" fill="#ddd6fe" text-anchor="middle" font-size="13">Une fabric ACI / APIC cluster</text><text x="720" y="32" fill="#6ee7b7" text-anchor="middle" font-size="18" font-weight="700">Multi-Site</text><rect x="490" y="50" width="445" height="255" rx="12" fill="#0e241e" stroke="#34d399"/><rect x="510" y="80" width="175" height="125" rx="9" fill="#12372b" stroke="#34d399"/><text x="597" y="103" fill="#d1fae5" text-anchor="middle" font-size="14" font-weight="700">Site A</text><text x="597" y="132" fill="#a7f3d0" text-anchor="middle" font-size="12">Fabric ACI</text><text x="597" y="151" fill="#a7f3d0" text-anchor="middle" font-size="12">APIC local</text><text x="597" y="170" fill="#a7f3d0" text-anchor="middle" font-size="12">Domaine de panne</text><rect x="740" y="80" width="175" height="125" rx="9" fill="#12372b" stroke="#34d399"/><text x="827" y="103" fill="#d1fae5" text-anchor="middle" font-size="14" font-weight="700">Site B</text><text x="827" y="132" fill="#a7f3d0" text-anchor="middle" font-size="12">Fabric ACI</text><text x="827" y="151" fill="#a7f3d0" text-anchor="middle" font-size="12">APIC local</text><text x="827" y="170" fill="#a7f3d0" text-anchor="middle" font-size="12">Domaine de panne</text><path d="M685 142 H740" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax6)" class="flow"/><rect x="600" y="230" width="225" height="48" rx="7" fill="#19172b" stroke="#a78bfa"/><text x="712" y="250" fill="#ddd6fe" text-anchor="middle" font-size="12">Orchestration Multi-Site</text><text x="712" y="266" fill="#c4b5fd" text-anchor="middle" font-size="11">coordination inter-fabrics</text><text x="480" y="337" fill="#94a3b8" text-anchor="middle" font-size="12">Schéma conceptuel — valider les topologies et contraintes supportées dans la release ciblée.</text></svg>

Avant de choisir, définissez les objectifs RTO/RPO, les services qui doivent survivre à la perte d'un site, les dépendances de routage et de sécurité, le comportement DNS, la réplication applicative, la latence inter-sites et la procédure de bascule. Une politique réseau répliquée ne réplique pas les données d'une base ni l'état d'une application.

### 7.4 Tests de panne planifiés

Pour chaque scénario, notez le composant retiré, l'effet attendu, la durée de convergence acceptable, les flux témoins, les compteurs à observer, la capacité restante et les conditions d'arrêt. Testez d'abord en environnement représentatif et coordonnez les équipes applicatives, sécurité et exploitation. Ne provoquez pas une panne en production sans autorisation et plan de retour arrière.

## 8. Intégration virtualisation et services

Les domaines VMM relient le modèle ACI aux environnements de virtualisation. Ils introduisent des objets et des dépendances externes : contrôleurs de virtualisation, port groups, politiques de VLAN, découverte des hôtes et mapping des réseaux. L'état de l'intégration peut être correct côté APIC mais incorrect côté hyperviseur, ou l'inverse.

Pour diagnostiquer une VM qui ne rejoint pas l'EPG attendu :

1. Vérifier le réseau/port group affecté à la VM dans la plateforme de virtualisation.
2. Vérifier le mapping de ce réseau vers le domaine VMM et les objets ACI.
3. Vérifier le VLAN ou l'encapsulation effective et la politique de port.
4. Vérifier l'apprentissage de l'endpoint sur le leaf et sa classification.
5. Tester la connectivité locale avant de tester les flux inter-EPG.
6. Vérifier le contrat seulement après avoir établi que la source et la destination sont classées correctement.

Les services L4-L7, redirections et intégrations de service nécessitent une analyse de chemin spécifique : point d'insertion, mode de service, santé des appliances, retour de trafic, NAT et dépendances de routage. Un diagramme logique ne remplace pas la vérification du chemin réel des paquets.

## 9. Automatisation et API : de l'intention à un changement vérifiable

L'API APIC permet de gérer des objets de manière programmatique. Une automatisation experte ne se limite pas à envoyer une requête HTTP : elle valide les entrées, contrôle les dépendances, gère les erreurs, attend la convergence, confirme l'état final et journalise le changement.

### 9.1 Principes de conception

- **Idempotence :** exécuter deux fois la même opération ne doit pas créer des objets en double ou élargir la politique.
- **Préconditions :** vérifier la version cible, le tenant, l'existence des objets et l'autorisation avant d'écrire.
- **Validation :** refuser les filtres trop larges, les ports inattendus, les préfixes non approuvés et les noms invalides.
- **Diff :** montrer l'état actuel, l'état voulu et le changement exact avant application.
- **Postconditions :** lire de nouveau les objets, vérifier les relations et lancer les tests de flux.
- **Traçabilité :** associer identifiant de changement, auteur, date, résultat, version et plan de retour arrière.
- **Secrets :** utiliser un coffre et éviter les tokens en clair dans le code ou les journaux.

### 9.2 Exemple de workflow conceptuel

```text
charger la demande approuvée
valider le schéma et la politique de sécurité
lire l'état courant depuis l'API
calculer un diff déterministe
si le diff dépasse le périmètre autorisé : arrêter
présenter le diff et demander l'approbation requise
appliquer les objets dans l'ordre de dépendance
relire l'état effectif et contrôler les erreurs
exécuter les tests positifs ET négatifs
publier le rapport, les preuves et la procédure de rollback
```

### 9.3 Gestion des erreurs

Une requête acceptée n'implique pas toujours que toute la politique soit opérationnelle au même instant. L'automatisation doit distinguer l'échec de transport, l'erreur d'authentification, l'erreur de validation, l'échec de déploiement et l'état fonctionnel incorrect. Les retries doivent être limités, avec backoff, et ne doivent pas masquer une erreur permanente. Une relance aveugle de créations ou suppressions peut rendre le résultat moins prévisible.

### 9.4 Exemple de payload à adapter

Le fragment ci-dessous illustre seulement la forme déclarative d'un objet logique. Les noms exacts, les attributs obligatoires et les relations doivent être vérifiés dans le modèle de données de la version APIC utilisée.

```json
{
  "fvTenant": {
    "attributes": { "name": "TENANT_APP", "descr": "Géré par pipeline approuvé" },
    "children": []
  }
}
```

Ne stockez pas des dumps complets contenant des secrets ou des informations sensibles dans des tickets accessibles largement. Versionnez les modèles, pas les sessions ou les tokens.

## 10. Observabilité et dépannage avancé

Le diagnostic commence par une hypothèse falsifiable. « Le réseau ne marche pas » n'est pas une hypothèse. « Les SYN atteignent le leaf source, mais le contrat n'autorise pas TCP/8443 entre ces EPG » est testable.

### 10.1 Matrice de diagnostic

| Symptôme | Hypothèses prioritaires | Preuves à collecter |
|---|---|---|
| Endpoint absent | port, VLAN, domaine, VM, apprentissage | état du port, mapping d'encapsulation, table endpoint |
| Endpoint sur mauvais EPG | attachement, VMM, classification | relations EPG, port group, encapsulation réelle |
| Même EPG, flux en échec | hôte, ARP/ND, MTU, mode de politique, firewall local | capture aux endpoints, état L2, drops |
| Inter-EPG bloqué | provider/consumer, contrat, filtre, port | matrice de flux, règles effectives, compteurs |
| Vers réseau externe en échec | route, External EPG, contrat, retour | table de routage, adjacence, capture aux frontières |
| Petits paquets OK, gros KO | MTU, PMTUD, fragmentation, appliance intermédiaire | tests de taille, captures, compteurs interface |
| Échec intermittent | convergence, microburst, lien instable, asymétrie | événements horodatés, erreurs, latence, compteurs |
| Après changement | ordre des objets, déploiement, cache/état endpoint | diff, audit, erreurs APIC, état avant/après |

### 10.2 Observer les deux extrémités

Si possible, capturez le même flux près de la source et près de la destination. Une capture uniquement sur le serveur ne permet pas de savoir si le paquet a quitté le leaf ; une capture uniquement côté destination ne prouve pas que le paquet a été transmis jusqu'à cette frontière. Pour les flux chiffrés, les captures peuvent prouver le transport et la temporalité sans révéler le contenu applicatif.

Synchronisez les horloges avant une investigation distribuée. Les événements de contrôle, journaux firewall et captures doivent être corrélables par timestamp, tuple de flux et identifiant de changement. Préservez les preuves et limitez les captures à la durée et au périmètre nécessaires.

### 10.3 Distinguer drop de politique et absence de route

Un paquet peut échouer avant même qu'une règle de sécurité soit pertinente : endpoint inconnu, route absente, adjacency non résolue, MTU ou lien en panne. À l'inverse, une route valide peut transporter le paquet jusqu'au point où la politique le rejette. Utilisez les compteurs et les outils de troubleshooting propres à la release pour identifier la décision réelle. N'inférez pas une cause à partir du seul message d'erreur applicatif.

### 10.4 Les faults APIC

Un fault est un signal à interpréter, pas nécessairement la cause racine. Regardez la gravité, la persistance, les objets affectés, l'heure de début, les dépendances et les changements récents. Certains faults sont corrélés à un symptôme, d'autres sont des effets secondaires. Ne supprimez pas un fault pour faire disparaître l'alerte sans traiter la condition sous-jacente.

## 11. Changements, upgrades et retour arrière

Un changement expert est une séquence contrôlée, pas une commande lancée parce qu'elle semble corriger le symptôme. Le plan doit inclure portée, dépendances, risque, fenêtres, responsables, critères de succès, tests négatifs, surveillance, décision d'arrêt et rollback.

### 11.1 Avant le changement

- Capturer l'état initial et les versions pertinentes.
- Exporter ou sauvegarder les éléments requis selon la procédure supportée.
- Identifier les objets dépendants et les tenants/EPG/contrats affectés.
- Vérifier l'état de santé de la fabric, des contrôleurs et des liens.
- Préparer des tests de référence, y compris un flux autorisé et un flux qui doit rester interdit.
- Faire relire le diff par une seconde personne pour les changements à fort impact.

### 11.2 Pendant le changement

Appliquer un périmètre limité, attendre l'état convergé, lire les erreurs et contrôler les résultats avant de poursuivre. Ne cumulez pas plusieurs changements indépendants : cela rend la cause d'un incident difficile à isoler. Si un indicateur dépasse le seuil défini, stoppez et appliquez la procédure convenue.

### 11.3 Après le changement

Vérifiez les flux positifs et négatifs, la route retour, les compteurs de drops, la santé des liens et l'absence de régression sur les applications voisines. Comparez l'état final à l'état voulu. Documentez les exceptions et la date de révision. Pour une mise à niveau ACI, suivez strictement les chemins de mise à niveau, matrices de compatibilité, prérequis et contrôles pré/post recommandés pour la release ; ne transposez pas une procédure d'une autre version.

### 11.4 Rollback réaliste

Le rollback doit être défini avant le déploiement. Pour les objets déclaratifs, cela peut signifier rétablir la version antérieure des objets ; pour une mise à niveau ou un changement physique, le retour arrière peut être limité ou suivre une procédure différente. Un export de configuration ne garantit pas à lui seul la restauration de tous les états externes. Identifiez les données et services qui ne peuvent pas être annulés automatiquement.

## 12. Atelier expert : architecture trois tiers

### Scénario

Une application comprend trois niveaux : Web, Application et Base de données. Les utilisateurs externes accèdent au Web via un firewall. Web communique avec Application sur TCP/8443 ; Application accède à la base sur TCP/5432. L'administration doit provenir d'un réseau d'exploitation séparé. Tout autre flux entre les niveaux doit être refusé par défaut.

### 12.1 Proposition logique

- Un tenant pour l'application, selon le modèle d'administration de l'organisation.
- Un VRF pour le domaine de routage applicatif, sauf exigence justifiée de séparation supplémentaire.
- Des BDs adaptés aux besoins d'adressage et de segmentation, sans multiplier les segments inutilement.
- Des EPG distincts pour Web, Application, Base de données et administration si le modèle de classification le permet.
- Des contrats précis : Web consomme le service Application sur TCP/8443 ; Application consomme le service Base sur TCP/5432 ; administration limitée aux protocoles et sources approuvés.
- Un External EPG/L3Out pour les préfixes externes pertinents, avec import/export strictement contrôlés.

<svg viewBox="0 0 960 400" role="img" aria-label="Politique d'une application trois tiers avec flux autorisés" xmlns="http://www.w3.org/2000/svg"><defs><marker id="ax7" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#65d8ff"/></marker></defs><rect x="25" y="35" width="165" height="80" rx="10" fill="#19172b" stroke="#a78bfa"/><text x="107" y="62" fill="#ddd6fe" text-anchor="middle" font-size="14" font-weight="700">Réseau externe</text><text x="107" y="83" fill="#c4b5fd" text-anchor="middle" font-size="12">clients autorisés</text><text x="107" y="100" fill="#c4b5fd" text-anchor="middle" font-size="11">préfixes connus</text><path d="M190 75 H250" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax7)" class="flow"/><rect x="255" y="35" width="150" height="80" rx="10" fill="#30230e" stroke="#fbbf24"/><text x="330" y="62" fill="#fde68a" text-anchor="middle" font-size="14" font-weight="700">Firewall</text><text x="330" y="83" fill="#fef3c7" text-anchor="middle" font-size="12">NAT / inspection</text><text x="330" y="100" fill="#fef3c7" text-anchor="middle" font-size="11">état de session</text><path d="M405 75 H465" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax7)" class="flow"/><rect x="470" y="35" width="185" height="80" rx="10" fill="#10251f" stroke="#34d399"/><text x="562" y="62" fill="#6ee7b7" text-anchor="middle" font-size="14" font-weight="700">EPG-Web</text><text x="562" y="83" fill="#d1fae5" text-anchor="middle" font-size="12">HTTP(S) publié</text><text x="562" y="100" fill="#a7f3d0" text-anchor="middle" font-size="11">accès entrant filtré</text><path d="M562 115 V150" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax7)" class="flow"/><rect x="470" y="155" width="185" height="80" rx="10" fill="#10251f" stroke="#34d399"/><text x="562" y="182" fill="#6ee7b7" text-anchor="middle" font-size="14" font-weight="700">EPG-Application</text><text x="562" y="203" fill="#d1fae5" text-anchor="middle" font-size="12">TCP/8443 depuis Web</text><text x="562" y="220" fill="#a7f3d0" text-anchor="middle" font-size="11">contrat ciblé</text><path d="M562 235 V270" stroke="#65d8ff" stroke-width="3" marker-end="url(#ax7)" class="flow"/><rect x="470" y="275" width="185" height="80" rx="10" fill="#10251f" stroke="#34d399"/><text x="562" y="302" fill="#6ee7b7" text-anchor="middle" font-size="14" font-weight="700">EPG-Base</text><text x="562" y="323" fill="#d1fae5" text-anchor="middle" font-size="12">TCP/5432 depuis App</text><text x="562" y="340" fill="#a7f3d0" text-anchor="middle" font-size="11">aucun accès direct Web</text><rect x="710" y="155" width="220" height="80" rx="10" fill="#10202a" stroke="#38bdf8"/><text x="820" y="182" fill="#7dd3fc" text-anchor="middle" font-size="14" font-weight="700">EPG-Administration</text><text x="820" y="203" fill="#e0f2fe" text-anchor="middle" font-size="12">source d'exploitation dédiée</text><text x="820" y="220" fill="#bae6fd" text-anchor="middle" font-size="11">accès explicite, journalisé</text><path d="M710 195 H680 V75 H655" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="7 6" marker-end="url(#ax7)" class="flow"/><text x="800" y="260" fill="#fde68a" text-anchor="middle" font-size="11">admin : flux séparés et approuvés</text><text x="250" y="305" fill="#94a3b8" font-size="12">Les flèches représentent les dépendances autorisées,</text><text x="250" y="324" fill="#94a3b8" font-size="12">pas toutes les routes physiques possibles.</text></svg>

### 12.2 Tests obligatoires

| Test | Résultat attendu | Pourquoi |
|---|---|---|
| Client autorisé → Web sur le port publié | Réussi | Confirme publication et retour |
| Web → Application TCP/8443 | Réussi | Confirme contrat et service |
| Application → Base TCP/5432 | Réussi | Confirme contrat de données |
| Web → Base TCP/5432 | Échec | Vérifie l'absence de chemin autorisé |
| Client externe → Base | Échec | Vérifie le cloisonnement externe |
| Réseau non-admin → interface d'administration | Échec | Vérifie l'isolement de gestion |
| Source admin autorisée → service admin défini | Réussi | Confirme l'accès opérationnel minimal |
| Retrait contrôlé d'un lien redondant | Continuité conforme au SLA | Valide la résilience réelle |

Un test négatif est aussi important qu'un test positif : il démontre que la segmentation ne s'est pas élargie pendant la correction. Répétez les tests depuis plusieurs points pertinents et consignez les résultats avec timestamp, tuples de flux et version de politique.

## 13. Erreurs de conception à éviter

1. Utiliser un contrat trop permissif comme outil de diagnostic permanent.
2. Confondre l'état visible dans l'APIC avec le comportement de l'application.
3. Considérer un endpoint appris comme preuve de connectivité de bout en bout.
4. Négliger le chemin retour, le NAT ou l'état d'un firewall.
5. Publier trop de routes ou utiliser des préfixes externes trop larges.
6. Déployer une politique sans test négatif.
7. Changer simultanément le routage, la classification et les contrats.
8. Automatiser des suppressions sans préconditions, diff ni rollback.
9. Traiter Multi-Pod et Multi-Site comme deux noms pour la même architecture.
10. Supposer qu'une sauvegarde de configuration remplace un plan de reprise testé.
11. Ignorer la MTU, les microbursts ou la capacité dégradée après panne.
12. Laisser les exceptions temporaires sans propriétaire ni date d'expiration.

## 14. Check-list d'une revue d'architecture ACI

- [ ] Objectifs RTO/RPO, criticité et domaines de panne documentés.
- [ ] Topologie physique, capacité nominale et capacité dégradée calculées.
- [ ] Version logicielle, matériel et intégrations validés dans les matrices supportées.
- [ ] Modèle Tenant/VRF/BD/EPG justifié par les exigences métier.
- [ ] Matrice de flux approuvée, avec source, destination, protocole et propriétaire.
- [ ] Contrats et filtres de moindre privilège ; exceptions datées.
- [ ] L3Out : import/export, External EPG, route retour et asymétrie vérifiés.
- [ ] MTU de bout en bout et intégrations de services testés.
- [ ] RBAC, comptes d'automatisation, secrets et audit maîtrisés.
- [ ] Observabilité, horodatage, alertes et procédure d'escalade opérationnels.
- [ ] Tests de panne, tests positifs/négatifs et rollback répétés.
- [ ] Runbooks à jour et responsabilités clairement attribuées.

## 15. Questions de validation expert

**1. L'APIC est joignable, l'endpoint apparaît, mais le flux échoue. Pourquoi ces deux observations ne suffisent-elles pas ?**

L'APIC confirme la gestion, et l'endpoint appris confirme une partie de la classification/localisation. Il reste à prouver le contrat effectif, la route, l'underlay, le chemin retour, la MTU et l'état des services intermédiaires.

**2. Une route externe est présente, mais la connexion TCP ne s'établit pas. Quelles vérifications prioriser ?**

Vérifier la route retour, les règles du firewall/NAT, le contrat et l'External EPG, puis observer les SYN/SYN-ACK aux frontières. Distinguer un paquet non routé d'un paquet rejeté par politique.

**3. Pourquoi une autorisation any-any est-elle une mauvaise correction de premier recours ?**

Elle élargit la surface autorisée, masque la vraie cause et rend les régressions difficiles à détecter. Préférer une hypothèse mesurable, une règle minimale et un test de confirmation.

**4. Quelle différence opérationnelle entre Multi-Pod et Multi-Site ?**

Multi-Pod étend une fabric ACI suivant une architecture commune ; Multi-Site coordonne plusieurs fabrics distinctes. Les domaines de panne, le contrôle, l'orchestration et les procédures de reprise diffèrent et doivent suivre la documentation de la solution retenue.

**5. Que doit prouver un pipeline de politique ?**

Que les entrées sont approuvées, que le diff est limité, que les objets et relations sont déployés, que l'état final correspond à l'intention et que les flux requis passent tandis que les flux interdits échouent.

**6. Pourquoi le test d'un seul flux autorisé ne suffit-il pas après un changement ?**

Parce qu'il ne vérifie pas la segmentation négative, les autres chemins, les retours ou les dépendances adjacentes. Il faut tester les chemins autorisés et interdits ainsi que la résilience prévue.

## 16. Références et méthode de travail

Utilisez les documents Cisco correspondant précisément à la version APIC/fabric en production :

- **Cisco Application Centric Infrastructure Fundamentals** — modèle de politique, objets et architecture.
- **Cisco ACI Contract Guide** — contrats, filtres, consommateurs et fournisseurs.
- **Cisco ACI Forwarding / VXLAN documentation** — comportement de forwarding, encapsulation et reachability.
- **Cisco ACI Layer 3 Networking Configuration Guide** — L3Out, routage externe et politiques associées.
- **Cisco Multi-Pod / Multi-Site documentation** — topologies, prérequis, limitations et procédures supportées.
- **Cisco ACI Upgrade Guide** — chemins supportés, contrôles préalables et postérieurs.
- **Cisco APIC REST API Configuration Guide** — modèles d'objets, authentification et opérations API.

Dans un environnement réel, commencez par la documentation de la release installée et les release notes, puis les guides de configuration et de dépannage correspondants. Les blogs et exemples communautaires sont utiles pour comprendre, mais ne remplacent pas la matrice de compatibilité ni les procédures supportées.

## Conclusion

L'expertise ACI repose sur une discipline : séparer gestion, contrôle et données ; modéliser les flux métier avant les contrats ; vérifier routage et politique indépendamment ; mesurer le comportement aux deux extrémités ; et traiter chaque changement comme une opération contrôlée. Une fabric experte n'est pas seulement une fabric qui fonctionne aujourd'hui : c'est une fabric dont les décisions peuvent être expliquées, les pannes anticipées et les changements prouvés.

</div>
