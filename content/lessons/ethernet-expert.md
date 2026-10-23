<style>
.diagram{margin:1rem 0;padding:.6rem;border:1px solid #29384b;border-radius:14px;background:#090d14;overflow:hidden}
.diagram svg{display:block;width:100%;height:auto;max-width:100%;font-family:Inter,Segoe UI,Arial,sans-serif}
.diagram .flow{stroke-dasharray:9 7;animation:ethernetFlow 1.8s linear infinite}
.diagram .flow-slow{stroke-dasharray:7 8;animation:ethernetFlow 3.2s linear infinite}
@keyframes ethernetFlow{to{stroke-dashoffset:-32}}
@media(prefers-reduced-motion:reduce){.diagram .flow,.diagram .flow-slow{animation:none!important;stroke-dasharray:5 5}}
.hint{border-left:3px solid #46d7f2;padding:.65rem .9rem;background:#0d1c28;border-radius:0 8px 8px 0}
</style>

# Ethernet & couche 2 — Niveau Expert

**Niveau :** Expert — conception, exploitation et diagnostic avancé des réseaux Ethernet commutés.

**Public visé :** administrateurs et ingénieurs réseau qui maîtrisent déjà l’adressage, les VLAN, le fonctionnement de base des commutateurs, STP/RSTP et LACP.

**Objectif :** savoir concevoir une couche 2 prévisible, repérer les défaillances intermittentes, analyser les symptômes à partir de compteurs et de captures, protéger le domaine de pontage, et changer une configuration sans créer une panne plus large.

> **Principe de travail :** la couche 2 doit être traitée comme un système distribué avec un état appris, des domaines de diffusion, des protocoles de contrôle et des dépendances physiques. Une interface « up » ne prouve ni la bonne livraison des trames ni la stabilité du service.

## Parcours et résultats attendus

À la fin du cours, vous pourrez :

- expliquer le chemin d’une trame à travers les tables MAC, VLAN, STP et les agrégats de liens ;
- concevoir le domaine de panne, les VLAN et la redondance sans compter sur des protections mal positionnées ;
- diagnostiquer une boucle, un MAC flapping, une négociation LACP instable, une incohérence de trunk, une erreur physique ou un problème de MTU ;
- distinguer les symptômes observés sur le commutateur, le système hôte, l’analyseur de paquets et les équipements intermédiaires ;
- construire un plan de changement avec état initial, contrôles, retour arrière et preuves de réussite.

### Comment utiliser les exemples

Les commandes marquées **Cisco IOS/IOS XE (exemple)** illustrent une syntaxe courante, mais les noms des commandes, la disponibilité des fonctions et les sorties changent selon les familles et versions. Consultez toujours le guide de la plateforme. Les exemples Linux (`ip`, `bridge`, `ethtool`, `tcpdump`) supposent un système et des droits adaptés. N’exécutez pas de changements sur un réseau de production sans autorisation, sauvegarde et plan de retour arrière.

## 1. Reconstituer le fonctionnement réel de la couche 2

### 1.1 La trame Ethernet comme unité de traitement

Une trame Ethernet transporte une charge utile entre deux adresses MAC dans un contexte de liaison. Elle ne contient pas, à elle seule, une notion de réseau IP ou de routeur. Le commutateur reçoit la trame sur un port, détermine le contexte VLAN, apprend généralement la MAC source, puis décide où transmettre la destination.

<div class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 252" role="img" aria-label="Composition conceptuelle d'une trame Ethernet et tag VLAN optionnel">
<rect x="1" y="1" width="918" height="250" rx="13" fill="#090d14" stroke="#2b3c50"/>
<text x="24" y="30" fill="#e7eef8" font-size="17" font-weight="700">Lecture de la trame — sans préambule ni intervalle intertrame</text>
<rect x="24" y="60" width="126" height="72" rx="8" fill="#13384a" stroke="#46d7f2"/><text x="87" y="88" text-anchor="middle" fill="#e7eef8" font-size="13" font-weight="700">MAC</text><text x="87" y="106" text-anchor="middle" fill="#e7eef8" font-size="13">destination</text><text x="87" y="122" text-anchor="middle" fill="#a7b7cb" font-size="11">6 octets</text>
<rect x="158" y="60" width="126" height="72" rx="8" fill="#13384a" stroke="#46d7f2"/><text x="221" y="88" text-anchor="middle" fill="#e7eef8" font-size="13" font-weight="700">MAC</text><text x="221" y="106" text-anchor="middle" fill="#e7eef8" font-size="13">source</text><text x="221" y="122" text-anchor="middle" fill="#a7b7cb" font-size="11">6 octets</text>
<rect x="292" y="60" width="105" height="72" rx="8" fill="#3b2c18" stroke="#ffca70"/><text x="344" y="87" text-anchor="middle" fill="#fff0d3" font-size="12" font-weight="700">802.1Q</text><text x="344" y="105" text-anchor="middle" fill="#fff0d3" font-size="12">optionnel</text><text x="344" y="122" text-anchor="middle" fill="#ffca70" font-size="11">4 octets</text>
<rect x="405" y="60" width="108" height="72" rx="8" fill="#182c42" stroke="#8cb5ff"/><text x="459" y="89" text-anchor="middle" fill="#e7eef8" font-size="13" font-weight="700">Type/Long.</text><text x="459" y="110" text-anchor="middle" fill="#a7b7cb" font-size="11">2 octets</text>
<rect x="521" y="60" width="220" height="72" rx="8" fill="#16372f" stroke="#65e6a4"/><text x="631" y="89" text-anchor="middle" fill="#e7eef8" font-size="13" font-weight="700">Charge utile</text><text x="631" y="110" text-anchor="middle" fill="#a7b7cb" font-size="11">souvent paquet IP</text>
<rect x="749" y="60" width="145" height="72" rx="8" fill="#3d2027" stroke="#ff7e83"/><text x="821" y="89" text-anchor="middle" fill="#ffe8e9" font-size="13" font-weight="700">FCS</text><text x="821" y="110" text-anchor="middle" fill="#ffb8bc" font-size="11">4 octets</text>
<path d="M24 155 H894" stroke="#40536a" stroke-width="1.5"/><text x="24" y="178" fill="#a7b7cb" font-size="12">À retenir : la balise 802.1Q ajoute 4 octets ; les captures hôtes peuvent omettre le FCS et d'autres détails physiques.</text><text x="24" y="202" fill="#a7b7cb" font-size="12">Le format exact et les limites de taille dépendent de la norme, du média et de l'implémentation.</text><path class="flow" d="M87 224 H824" stroke="#46d7f2" stroke-width="2.2" fill="none" marker-end="url(#ethArrow1)"/><defs><marker id="ethArrow1" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#46d7f2"/></marker></defs><text x="455" y="218" text-anchor="middle" fill="#46d7f2" font-size="11">lecture conceptuelle des champs</text>
</svg>
</div>

Le format Ethernet conventionnel comporte notamment les adresses MAC destination et source, le champ Type/Longueur, une charge utile et un contrôle FCS. Le tag VLAN ajoute un champ de 4 octets : TPID et TCI, lequel inclut PCP (priorité), DEI (indication d’éligibilité à l’abandon) et VID. La balise n’est pas une « adresse » : elle qualifie le contexte de pontage et la priorité au niveau 2.

Les captures sur un hôte ne sont pas toujours une copie exacte de ce qui est sur le fil. Le FCS peut être retiré par la carte réseau ; le segmentation/receive offload peut changer l’apparence des paquets ; un SPAN peut perdre des paquets ; un lien optique peut compter des erreurs que la capture logicielle ne verra jamais. Toujours noter **où**, **comment** et **à quel moment** la capture a été effectuée.

### 1.2 Le commutateur est un plan de décision, pas un simple câble

Pour une trame reçue, l’équipement doit notamment :

1. vérifier l’état physique et les contrôles d’entrée ;
2. déterminer le VLAN (access, tag reçu, VLAN natif, règles particulières) ;
3. apprendre la MAC source dans le contexte VLAN si l’apprentissage est autorisé ;
4. chercher la MAC destination dans la table de transfert ;
5. transmettre sur un port éligible, inonder dans le VLAN si la destination est inconnue ou broadcast, ou filtrer selon les règles du pont ;
6. appliquer les fonctions configurées : ACL, QoS, sécurité, contrôle de tempête, miroir, etc.

L’ordre interne précis des blocs de matériel peut varier. Pour un diagnostic, pensez en termes de **conditions** : la trame a-t-elle été reçue ? dans quel VLAN ? la source a-t-elle été apprise ? l’entrée destination est-elle correcte ? le port de sortie est-il en forwarding et autorise-t-il ce VLAN ? des compteurs montrent-ils un rejet ?

### 1.3 Table MAC, apprentissage et vieillissement

La table MAC (CAM/FDB selon le contexte matériel ou logiciel) associe une adresse MAC à un VLAN et à un port, ou à un agrégat logique. L’apprentissage standard se fait à partir de la **MAC source** des trames reçues. L’entrée dynamique peut vieillir en l’absence de trafic ; le délai est configurable ou fixé selon la plateforme. Les entrées statiques et certaines entrées de contrôle suivent d’autres règles.

Une MAC qui apparaît successivement sur des ports différents dans le même VLAN — **MAC flapping** — peut indiquer :

- une boucle physique ou logique ;
- un serveur actif/actif ou une migration de VM dont le comportement n’est pas correctement modélisé ;
- un agrégat LACP incohérent ;
- des ports reliés entre eux par un équipement intermédiaire inattendu ;
- une architecture de haute disponibilité où le même MAC virtuel est annoncé depuis deux endroits sans synchronisation appropriée.

Ne concluez pas immédiatement à une boucle sur un seul événement de flapping : corrélez les logs STP, l’état des LAG, les compteurs de broadcast/multicast, l’heure, les ports et le service impacté.

### 1.4 Domaine de broadcast et portée du risque

Un VLAN définit un domaine logique de pontage, généralement un domaine de diffusion pour IPv4 ARP et les broadcast Ethernet associés. Le découpage VLAN permet une séparation de portée, mais **ne constitue pas à lui seul une politique de sécurité complète**. Les ports trunk, les passerelles, les ponts virtuels, les hyperviseurs, les équipements L2/L3 et les configurations d'accès définissent les chemins réels.

Un VLAN trop étendu accroît le rayon d’impact des tempêtes et erreurs ; un VLAN segmenté de façon excessive augmente le coût opérationnel et peut compliquer la mobilité ou les applications héritées. Le bon périmètre est celui qui correspond aux besoins de communication, à la politique de sécurité, à la capacité de dépannage et au domaine de panne acceptable.

## 2. VLAN et trunks : rendre explicite le contexte de chaque trame

### 2.1 Ports access, trunk et VLAN natif

Un port **access** associe généralement les trames non taguées des terminaux à un VLAN configuré. Un port **trunk** transporte plusieurs VLAN en utilisant des identifiants ; certains équipements autorisent une configuration particulière pour les trames non taguées. La terminologie et les détails varient, mais la règle d'exploitation est stable : aux deux extrémités, savoir quels VLAN sont admis, tagués et non tagués.

<div class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 306" role="img" aria-label="Deux ports access et un trunk portant des VLAN tagués">
<rect x="1" y="1" width="918" height="304" rx="13" fill="#090d14" stroke="#2b3c50"/><text x="24" y="30" fill="#e7eef8" font-size="17" font-weight="700">VLAN : attribution sur access, conservation du tag sur trunk</text>
<rect x="34" y="78" width="145" height="66" rx="9" fill="#142a41" stroke="#8cb5ff"/><text x="106" y="105" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">Hôte A</text><text x="106" y="125" text-anchor="middle" fill="#a7b7cb" font-size="12">trames non taguées</text>
<rect x="230" y="68" width="190" height="86" rx="10" fill="#14352f" stroke="#65e6a4"/><text x="325" y="98" text-anchor="middle" fill="#e7eef8" font-size="15" font-weight="700">Switch A</text><text x="325" y="119" text-anchor="middle" fill="#a7b7cb" font-size="12">Access : VLAN 10</text><text x="325" y="137" text-anchor="middle" fill="#65e6a4" font-size="11">apprentissage MAC</text>
<rect x="500" y="68" width="190" height="86" rx="10" fill="#14352f" stroke="#65e6a4"/><text x="595" y="98" text-anchor="middle" fill="#e7eef8" font-size="15" font-weight="700">Switch B</text><text x="595" y="119" text-anchor="middle" fill="#a7b7cb" font-size="12">Access : VLAN 10</text><text x="595" y="137" text-anchor="middle" fill="#65e6a4" font-size="11">même domaine L2</text>
<rect x="742" y="78" width="145" height="66" rx="9" fill="#142a41" stroke="#8cb5ff"/><text x="814" y="105" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">Hôte B</text><text x="814" y="125" text-anchor="middle" fill="#a7b7cb" font-size="12">trames non taguées</text>
<path d="M179 111 H230" stroke="#8cb5ff" stroke-width="2.5" fill="none" marker-end="url(#ethArrow2)"/><path class="flow" d="M420 111 H500" stroke="#46d7f2" stroke-width="3" fill="none" marker-end="url(#ethArrow2)"/><path d="M690 111 H742" stroke="#8cb5ff" stroke-width="2.5" fill="none" marker-end="url(#ethArrow2)"/>
<rect x="430" y="79" width="60" height="22" rx="5" fill="#3b2c18" stroke="#ffca70"/><text x="460" y="94" text-anchor="middle" fill="#fff0d3" font-size="11">VID 10</text>
<path d="M460 154 V184" stroke="#ffca70" stroke-width="1.8" stroke-dasharray="4 4"/><rect x="98" y="192" width="724" height="80" rx="10" fill="#121e2c" stroke="#34465b"/><text x="460" y="215" text-anchor="middle" fill="#ffca70" font-size="14" font-weight="700">Contrôles du trunk aux deux extrémités</text><text x="460" y="237" text-anchor="middle" fill="#e7eef8" font-size="12">VLAN autorisés • VLAN natif/non tagué • encapsulation • cohérence STP</text><text x="460" y="255" text-anchor="middle" fill="#a7b7cb" font-size="11">Un VLAN manquant peut produire une panne sélective, sans couper le lien physique.</text>
<defs><marker id="ethArrow2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#46d7f2"/></marker></defs>
</svg>
</div>

Les écarts typiques sont : VLAN absent de la base de l’un des commutateurs, VLAN exclu de la liste autorisée, mauvais port access, mauvais VLAN natif, tag reçu alors que l’autre extrémité attend du non-tagué, ou configuration dynamique non souhaitée. Un lien peut rester `up/up`, transporter plusieurs VLAN et échouer pour un seul service.

**Checklist de comparaison d’un trunk :**

- mode d’encapsulation attendu et rôle du port ;
- VLAN natif ou politique de trames non taguées ;
- liste des VLAN autorisés et effectivement actifs ;
- VLAN en forwarding STP sur ce port ;
- MTU et fonctions de sécurité sur le chemin ;
- état du voisin LLDP/CDP, câblage réel et agrégation éventuelle.

**Cisco IOS/IOS XE (exemple) :**

```text
show interfaces trunk
show interfaces Gi1/0/48 switchport
show vlan brief
show spanning-tree vlan 10
show mac address-table dynamic vlan 10
```

Ne vous contentez pas de lire la configuration : comparez l’état opérationnel. Un VLAN déclaré dans la configuration n'est pas nécessairement transporté, actif et en forwarding sur chaque lien.

### 2.2 VLAN natif et trames non taguées : règle de cohérence

L’expression « VLAN natif » est courante sur certaines plateformes, mais tous les matériels et modes de configuration n’appliquent pas les mêmes règles. Il faut déterminer comment sont traitées les trames sans balise et si les deux extrémités s’accordent. Une trame non taguée reçue dans un trunk n'a pas de VID explicite à l'intérieur de sa balise ; l'équipement lui associe le contexte défini par sa configuration.

Une incohérence peut provoquer une fuite entre domaines, des protocoles de contrôle inattendus, ou une panne difficile à expliquer parce que seul le trafic non tagué — ou certains VLAN — est affecté. La pratique robuste consiste à documenter la politique et à réduire l'usage du non-tagué aux cas nécessaires.

### 2.3 Double tag, QinQ et frontière de confiance

Le tunneling VLAN 802.1ad/QinQ permet d'encapsuler un contexte VLAN client dans un contexte de service sur certains réseaux opérateurs. Le matériel doit traiter la pile de balises attendue et la MTU du lien doit accepter l'overhead. Ne confondez pas une double balise légitime d'un service géré avec une attaque de double tagging : la faisabilité de cette dernière dépend de la configuration, du VLAN natif, de la manière dont les balises sont retirées et de la topologie.

Mesures de conception :

- définir précisément la frontière fournisseur/client ;
- ne pas faire confiance aux VLAN fournis par un terminal non contrôlé ;
- appliquer la politique de balises à l'entrée ;
- documenter les ports qui acceptent plusieurs tags ;
- tester le MTU et les comportements de balises imbriquées ;
- ne pas supposer qu'un seul VLAN « de gestion » est protégé par son seul numéro.

## 3. STP, RSTP et MSTP : contrôler la topologie sans créer de fausse sécurité

### 3.1 Élection et rôles

STP supprime les boucles logiques en construisant une topologie de forwarding sans cycle pour chaque instance ou groupe concerné. Les ponts échangent des BPDU et déterminent notamment un root bridge, un root port par pont non racine et des ports désignés pour les segments. Les chemins alternatifs peuvent être conservés en état non-forwarding afin de reprendre si le chemin actif échoue.

La sélection du root se base d'abord sur l'identifiant de pont, qui comprend priorité et adresse MAC. Les coûts des chemins entrent ensuite dans le choix du root port ; les règles de départage (identifiants des ponts/ports) assurent un résultat déterministe. Une conception ne devrait pas laisser le root être élu accidentellement au gré d'un nouvel équipement.

<div class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 330" role="img" aria-label="Topologie redondante STP avec root bridge, chemin forwarding et lien alternatif bloqué">
<rect x="1" y="1" width="918" height="328" rx="13" fill="#090d14" stroke="#2b3c50"/><text x="24" y="30" fill="#e7eef8" font-size="17" font-weight="700">STP : conserver la redondance physique, contrôler les chemins actifs</text>
<rect x="357" y="54" width="206" height="62" rx="10" fill="#153d32" stroke="#65e6a4" stroke-width="2"/><text x="460" y="80" text-anchor="middle" fill="#e7eef8" font-size="15" font-weight="700">SW1 — Root Bridge</text><text x="460" y="100" text-anchor="middle" fill="#65e6a4" font-size="12">priorité contrôlée</text>
<rect x="100" y="220" width="190" height="62" rx="10" fill="#14283d" stroke="#8cb5ff"/><text x="195" y="245" text-anchor="middle" fill="#e7eef8" font-size="15" font-weight="700">SW2</text><text x="195" y="265" text-anchor="middle" fill="#a7b7cb" font-size="12">root port vers SW1</text>
<rect x="630" y="220" width="190" height="62" rx="10" fill="#14283d" stroke="#8cb5ff"/><text x="725" y="245" text-anchor="middle" fill="#e7eef8" font-size="15" font-weight="700">SW3</text><text x="725" y="265" text-anchor="middle" fill="#a7b7cb" font-size="12">root port vers SW1</text>
<path d="M394 116 L260 220" stroke="#65e6a4" stroke-width="3" fill="none" marker-end="url(#ethArrow3)"/><path d="M526 116 L660 220" stroke="#65e6a4" stroke-width="3" fill="none" marker-end="url(#ethArrow3)"/><text x="300" y="164" fill="#65e6a4" font-size="12">forwarding</text><text x="586" y="164" fill="#65e6a4" font-size="12">forwarding</text>
<path d="M290 251 H630" stroke="#ffca70" stroke-width="3" stroke-dasharray="8 7" fill="none"/><rect x="377" y="228" width="166" height="41" rx="8" fill="#3b2c18" stroke="#ffca70"/><text x="460" y="245" text-anchor="middle" fill="#fff0d3" font-size="12" font-weight="700">lien alternatif</text><text x="460" y="260" text-anchor="middle" fill="#ffca70" font-size="11">non-forwarding</text>
<path class="flow" d="M460 116 L460 198" stroke="#46d7f2" stroke-width="2.5" fill="none" marker-end="url(#ethArrow3)"/><text x="460" y="190" text-anchor="middle" fill="#46d7f2" font-size="11">BPDU</text>
<text x="24" y="309" fill="#a7b7cb" font-size="12">Une redondance bloquée par STP n'est pas une panne : vérifiez le rôle/état du port et le plan de reconvergence.</text><defs><marker id="ethArrow3" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#65e6a4"/></marker></defs>
</svg>
</div>

**RSTP (802.1w, intégré à la famille 802.1D révisée)** accélère la transition en s'appuyant notamment sur des rôles/états explicites et des mécanismes de handshake entre ports compatibles. **MSTP (802.1s / inclus dans 802.1Q)** permet d'associer des VLAN à des instances multiples de STP, réduisant le nombre d'instances par rapport à un STP par VLAN. En MST, les paramètres de région — nom, révision et mapping VLAN-instance — doivent être cohérents, sinon les ponts peuvent se retrouver dans des régions différentes.

Il est tentant de penser que RSTP signifie toujours une convergence sub-seconde : le résultat réel dépend des liens, du matériel, des protections, des interactions avec STP ancien, des temporisateurs et des scénarios de panne. Mesurez l'impact observable au lieu de promettre une valeur théorique universelle.

### 3.2 Protéger des rôles différents avec les bonnes fonctions

Les protections STP ne sont pas interchangeables. Les placer sans comprendre leur objectif peut bloquer un lien légitime ou laisser subsister le problème qu'on voulait empêcher.

| Fonction | Objectif | Placement habituel (à valider selon plateforme) | Ce qu'elle ne fait pas |
|---|---|---|---|
| PortFast / edge | Accélérer le forwarding sur un port terminal | Port connecté à un seul terminal, serveur ou équipement final approprié | Ne protège pas à lui seul contre un switch non autorisé |
| BPDU Guard | Empêcher qu'un port edge participant à la protection reçoive une BPDU | Ports edge/PortFast où une BPDU est anormale | Ne remplace pas la conception STP des liens entre switches |
| Root Guard | Empêcher un port d'accepter un changement vers un root non souhaité | Ports où l'équipement voisin ne doit pas prendre le rôle de root via ce chemin | Ne détecte pas une rupture unidirectionnelle à lui seul |
| Loop Guard | Éviter qu'un port non désigné passe incorrectement en forwarding après disparition de BPDU dans certains cas | Liens redondants compatibles, selon design | Ne remplace pas UDLD ou la surveillance optique |
| UDLD / détection unidirectionnelle | Identifier un chemin où un sens de transmission ou de réception ne fonctionne pas correctement | Liens optiques/agrégats adaptés et pris en charge | N'est pas un protocole universel sur tous les constructeurs/médias |
| Storm control | Limiter l'effet de certaines tempêtes de broadcast/multicast/unknown-unicast | Interfaces définies par la politique de risque | Ne répare pas la boucle sous-jacente et peut supprimer du trafic utile |

Exemples Cisco IOS/IOS XE (à adapter et tester) :

```text
show spanning-tree root
show spanning-tree vlan 20 detail
show spanning-tree inconsistentports
show spanning-tree interface Gi1/0/10 detail
show logging | include SPANTREE|UDLD|ERR_DISABLE
```

Les commandes de protection configurables dépendent du modèle et de la version. **BPDU Guard** peut mettre le port dans un état désactivé ou err-disabled selon la plateforme et les options de récupération. Une récupération automatique mal pensée peut provoquer un cycle panne/reprise répété. Root Guard et Loop Guard répondent à des scénarios différents et ne doivent pas être appliqués ensemble sur le même port si la plateforme les rend incompatibles.

### 3.3 Root planifié et design des chemins

Dans un réseau d'entreprise, le root doit être choisi intentionnellement afin d'aligner les chemins de niveau 2 avec l'architecture des passerelles et les flux attendus. Les causes de dérive incluent un switch nouvellement installé avec une priorité plus favorable, une configuration effacée, un changement de matériel et une incohérence MST. Documentez, par VLAN/instance :

- root principal et secondaire ;
- priorité et coût de chemin attendu ;
- liens qui doivent être forwarding ;
- liens alternatifs attendus et événement qui doit les faire basculer ;
- protections à chaque frontière ;
- temps de rétablissement observé lors du test de panne.

Évitez de créer une dépendance cachée où l'activation d'un VLAN sur un trunk change indirectement l'arbre ou la charge d'un chemin sans validation. Les tests de changement doivent contrôler le root, les rôles et états ainsi que les compteurs après convergence.

### 3.4 Quand réduire la dépendance à STP

STP demeure un mécanisme central dans de nombreux réseaux LAN. Toutefois, les grands domaines L2 étendus accroissent le rayon d'impact des boucles, de l'apprentissage de MAC et des changements de topologie. Dans les datacenters, une architecture routée leaf-spine avec ECMP peut éviter d'étendre un unique domaine de broadcast partout ; VXLAN/EVPN peut ensuite fournir certains services L2 superposés aux segments qui le nécessitent.

Ce choix n'est pas « STP est mauvais » : il s'agit de contrôler la portée du domaine L2 et de faire correspondre le modèle de redondance aux besoins. Toute architecture overlay apporte ses propres dépendances (underlay IP, VTEP, MTU, contrôle de l'état MAC/IP, plan de routage) qu'il faut exploiter et dépanner.

## 4. EtherChannel / LAG et LACP : redondance plus répartition, pas magie

### 4.1 Agrégation logique

LACP négocie et surveille la participation de liens physiques à un agrégat, selon les modes et fonctions disponibles. Le groupe logique apparaît comme une interface pour le pontage ; STP traite généralement le port-channel comme un lien logique, tandis que le plan de transfert distribue les flux sur les membres éligibles. Le mécanisme de répartition varie : MAC source/destination, IP, ports L4 ou combinaisons spécifiques.

<div class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 310" role="img" aria-label="Quatre liens physiques agrégés en un port-channel logique sous LACP">
<rect x="1" y="1" width="918" height="308" rx="13" fill="#090d14" stroke="#2b3c50"/><text x="24" y="30" fill="#e7eef8" font-size="17" font-weight="700">LAG / LACP : un lien logique, plusieurs liens membres</text>
<rect x="46" y="82" width="145" height="150" rx="10" fill="#14283d" stroke="#8cb5ff"/><text x="118" y="110" text-anchor="middle" fill="#e7eef8" font-size="15" font-weight="700">Switch A</text><text x="118" y="130" text-anchor="middle" fill="#a7b7cb" font-size="12">Po10</text><rect x="725" y="82" width="145" height="150" rx="10" fill="#14283d" stroke="#8cb5ff"/><text x="797" y="110" text-anchor="middle" fill="#e7eef8" font-size="15" font-weight="700">Switch B</text><text x="797" y="130" text-anchor="middle" fill="#a7b7cb" font-size="12">Po10</text>
<path class="flow" d="M191 105 H725" stroke="#46d7f2" stroke-width="2" fill="none" marker-end="url(#ethArrow4)"/><path class="flow" d="M191 139 H725" stroke="#65e6a4" stroke-width="2" fill="none" marker-end="url(#ethArrow4)"/><path class="flow" d="M191 173 H725" stroke="#c6a4ff" stroke-width="2" fill="none" marker-end="url(#ethArrow4)"/><path class="flow" d="M191 207 H725" stroke="#ffca70" stroke-width="2" fill="none" marker-end="url(#ethArrow4)"/>
<text x="458" y="93" text-anchor="middle" fill="#46d7f2" font-size="11">membre 1</text><text x="458" y="127" text-anchor="middle" fill="#65e6a4" font-size="11">membre 2</text><text x="458" y="161" text-anchor="middle" fill="#c6a4ff" font-size="11">membre 3</text><text x="458" y="195" text-anchor="middle" fill="#ffca70" font-size="11">membre 4</text>
<rect x="240" y="245" width="440" height="42" rx="9" fill="#1b2434" stroke="#3b4d64"/><text x="460" y="263" text-anchor="middle" fill="#e7eef8" font-size="13" font-weight="700">LACP : sélection / état des membres</text><text x="460" y="279" text-anchor="middle" fill="#a7b7cb" font-size="11">Le hachage affecte un flux à un membre ; un flux unique ne cumule généralement pas les débits des liens.</text><defs><marker id="ethArrow4" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#46d7f2"/></marker></defs>
</svg>
</div>

LACP est standardisé dans IEEE 802.1AX (le champ exact d'application et certaines options dépendent de la version/plateforme). Ne confondez pas :

- **LACP** : protocole de contrôle qui détecte les partenaires et négocie les membres ;
- **LAG / port-channel / EtherChannel** : agrégat logique ;
- **MLAG/vPC/VSX/MC-LAG** : mécanismes propriétaires ou spécifiques permettant, selon l'implémentation, d'étendre un agrégat vers deux châssis ; ils introduisent une synchronisation et des dépendances supplémentaires.

Un port-channel qui réunit des liens vers deux switches indépendants ne fonctionne pas magiquement comme un seul partenaire LACP. Il faut une solution multichâssis explicitement prise en charge et correctement conçue, ou un seul équipement logique vu des deux côtés.

### 4.2 Cohérence des membres

Les paramètres qui doivent être cohérents dépendent de la plateforme, mais vérifiez au minimum vitesse, duplex lorsque pertinent, mode de négociation, paramètres L2, VLAN natif/autorisé, MTU, état STP, sécurité et compatibilité transceiver. Un membre hors groupe ou en état suspendu peut produire une panne partielle difficile à repérer : le LAG global fonctionne, mais la capacité diminue, certains flux sont mal distribués ou un chemin est asymétrique.

**Cisco IOS/IOS XE (exemple) :**

```text
show etherchannel summary
show etherchannel detail
show lacp neighbor
show interfaces port-channel 10
show interfaces counters errors
show spanning-tree interface port-channel 10 detail
```

**Linux (exemple) :** `cat /proc/net/bonding/bond0`, `ip -d link show bond0`, et l'état du commutateur partenaire. Les options bonding Linux ne sont pas strictement équivalentes à toutes les options d'un switch ; comparer les fonctions, pas seulement les noms.

### 4.3 Pourquoi le débit agrégé ne double pas automatiquement

Le répartiteur de charge applique un hachage aux champs disponibles pour choisir un membre. Un flux TCP unique est généralement affecté à un membre pendant sa durée afin de préserver l'ordre des paquets. Le débit d'un transfert peut donc plafonner à la vitesse d'un lien, même si l'agrégat a plusieurs membres. Plusieurs flux, si leurs clés de hachage se répartissent correctement, peuvent mieux exploiter la capacité totale.

Une distribution asymétrique peut être causée par peu de flux, un choix de champs de hachage non adapté, une concentration d'adresses, ou les caractéristiques du trafic. Le compte de membres « up » n'est pas une mesure suffisante de l'équilibre. Regardez les octets/paquets par membre, le taux d'erreurs et les flux observés.

### 4.4 Ordre de changement d'un LAG

1. confirmer l'architecture de voisinage et le nombre de membres réellement supportés ;
2. enregistrer la configuration des deux extrémités et les compteurs de départ ;
3. préparer une configuration cohérente et éviter que les liens soient actifs individuellement en forwarding avant l'agrégation lorsque cela peut créer une boucle ;
4. appliquer pendant la fenêtre prévue, en suivant l'état LACP ;
5. vérifier le LAG des deux côtés, VLAN, STP et transfert réel ;
6. tester la perte d'un membre de manière contrôlée ;
7. mesurer si le service respecte le niveau de capacité attendu ;
8. conserver le retour arrière si le groupe se forme partiellement ou fait apparaître des erreurs.

## 5. Boucles, tempêtes et instabilité d'apprentissage

### 5.1 Mécanisme d'une boucle

Un bridge Ethernet n'ajoute pas nécessairement un TTL à chaque trame. Si une trame de broadcast ou d'unicast inconnu entre dans une topologie cyclique qui transmet ce trafic sur les branches de retour, les copies peuvent se multiplier et continuer à circuler. Les tables MAC peuvent alors osciller ; l'usage des liens, le CPU de contrôle, les files et le réseau hôte peuvent être affectés.

<div class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 370" role="img" aria-label="Boucle Ethernet triangulaire avec propagation de trames et points de contrôle">
<rect x="1" y="1" width="918" height="368" rx="13" fill="#090d14" stroke="#2b3c50"/><text x="24" y="30" fill="#e7eef8" font-size="17" font-weight="700">Symptômes d'une boucle L2 — limiter le rayon d'impact, puis corriger la cause</text>
<rect x="366" y="57" width="188" height="55" rx="9" fill="#3d2027" stroke="#ff7e83"/><text x="460" y="80" text-anchor="middle" fill="#ffe8e9" font-size="14" font-weight="700">SW-A</text><text x="460" y="98" text-anchor="middle" fill="#ffb8bc" font-size="11">MAC flapping / trafic élevé</text>
<rect x="115" y="208" width="188" height="55" rx="9" fill="#3d2027" stroke="#ff7e83"/><text x="209" y="231" text-anchor="middle" fill="#ffe8e9" font-size="14" font-weight="700">SW-B</text><text x="209" y="249" text-anchor="middle" fill="#ffb8bc" font-size="11">broadcast en hausse</text>
<rect x="617" y="208" width="188" height="55" rx="9" fill="#3d2027" stroke="#ff7e83"/><text x="711" y="231" text-anchor="middle" fill="#ffe8e9" font-size="14" font-weight="700">SW-C</text><text x="711" y="249" text-anchor="middle" fill="#ffb8bc" font-size="11">pertes / saturation</text>
<path class="flow" d="M384 110 L273 208" stroke="#ff7e83" stroke-width="3" fill="none" marker-end="url(#ethArrow5)"/><path class="flow" d="M303 236 H617" stroke="#ff7e83" stroke-width="3" fill="none" marker-end="url(#ethArrow5)"/><path class="flow" d="M647 208 L536 110" stroke="#ff7e83" stroke-width="3" fill="none" marker-end="url(#ethArrow5)"/>
<rect x="267" y="278" width="386" height="49" rx="9" fill="#1e2734" stroke="#ffca70"/><text x="460" y="298" text-anchor="middle" fill="#fff0d3" font-size="12" font-weight="700">Mesures de confinement</text><text x="460" y="315" text-anchor="middle" fill="#a7b7cb" font-size="11">storm-control • isolation ciblée • STP</text>
<text x="24" y="351" fill="#a7b7cb" font-size="12">Ne couper qu'après localisation : protéger le service, identifier les ports communs, confirmer puis supprimer la boucle.</text><defs><marker id="ethArrow5" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ff7e83"/></marker></defs>
</svg>
</div>

Symptômes fréquents : compteurs broadcast/multicast qui augmentent rapidement, taux de CPU élevé, MAC flapping, perte intermittente, connexions qui expirent, interfaces en saturation, messages STP répétés, téléphones IP et AP qui redémarrent ou obtiennent difficilement une adresse. Un volume de broadcast élevé peut aussi être légitime : comparez avec la référence habituelle et les compteurs par VLAN/port.

### 5.2 Réponse à une suspicion de boucle

**Objectif immédiat : protéger le service et préserver les preuves.**

1. identifier l'heure exacte, les VLAN et les services touchés ;
2. comparer les compteurs de broadcast/multicast/unknown-unicast, les logs STP et les MAC flapping ;
3. repérer les ports suspects qui partagent le même motif de variation ;
4. comparer la topologie documentée avec LLDP/CDP et le câblage ;
5. confiner le lien/port le plus probablement fautif selon l'autorisation de changement et l'impact attendu ;
6. observer si les compteurs et pertes se stabilisent ;
7. corriger la boucle (câblage, bridge externe, LAG, STP, protection) ;
8. valider la restauration et vérifier que le retrait du confinement n'entraîne pas une récidive.

Le contrôle de tempête peut limiter la bande passante affectée par certaines catégories de trafic. Un seuil trop bas peut supprimer ARP, DHCP, découverte ou multicast utile. Calibrez-le à partir des mesures du réseau, du type d'accès et du profil de l'application. Le contrôle de tempête est un dispositif de confinement, pas une réparation structurelle.

### 5.3 MAC flapping : arbre de diagnostic

| Observation | Hypothèses à tester | Preuve utile |
|---|---|---|
| Même MAC entre deux ports access | Boucle, petit switch non documenté, bridge hôte | LLDP/CDP, table MAC horodatée, inspection câblage |
| MAC entre port-channel et membre physique | Agrégation/configuration ou comportement de log | État du LAG, logs LACP, compteurs membres |
| MAC d'un cluster/serveur très mobile | Basculement, migration VM, MAC virtuelle | Journaux hyperviseur/cluster corrélés à l'heure |
| Flapping avec broadcast en hausse | Boucle probable, mais à confirmer | STP topology changes, compteurs port/VLAN, capture |
| Flapping sans hausse globale de trafic | Mobilité légitime, teaming, duplication partielle | Analyse du MAC source/destination et du système hôte |

Ne faites pas de « clear mac address-table dynamic » comme première réaction automatique. Effacer la table peut temporairement multiplier l'inondation des destinations inconnues et masquer l'indice temporel. Si l'effacement est justifié, notez l'état avant et après et les risques attendus.

## 6. Sécurité L2 : contrôler qui peut joindre quel port et quel VLAN

### 6.1 Principes de base

La sécurité de couche 2 n'est pas un unique bouton. Elle combine contrôle d'accès, admission VLAN, validation des protocoles d'adressage, limites d'apprentissage, protections STP, chiffrement éventuel et surveillance. Le bon ensemble dépend de la menace, de la compatibilité des terminaux et de la capacité d'exploitation.

- **802.1X** : contrôle d'accès réseau basé sur l'authentification du supplicant et l'infrastructure AAA, quand pris en charge.
- **MAB** : mécanisme de repli basé sur l'adresse MAC ; pratique pour des terminaux sans supplicant, mais l'adresse MAC n'est pas un secret et peut être usurpée.
- **Port security** : contrôle du nombre ou des MAC autorisées/apprises sur un port ; le mode de violation et le vieillissement doivent être planifiés.
- **DHCP snooping** : distinguer ports de confiance et non fiables, valider certains messages DHCP et créer une base de bindings sur les équipements compatibles.
- **Dynamic ARP Inspection (DAI)** : valider les messages ARP selon les bindings/politiques disponibles ; surveiller les exceptions statiques et les équipements non DHCP.
- **IP Source Guard** : filtrer certains paquets IP selon la liaison IP/MAC/port apprise ou configurée.
- **RA Guard / protections IPv6** : limiter les annonces Router Advertisement non autorisées, selon le matériel et les contournements connus.
- **MACsec (802.1AE)** : protection cryptographique des liens Ethernet pris en charge ; implique gestion des clés et compatibilité des extrémités.

Ces mécanismes peuvent se chevaucher et générer des rejets légitimes en cas de mauvaise configuration. Il faut d'abord recenser les imprimantes, téléphones, AP, hyperviseurs, liens d'uplink et adresses statiques. Tester une politique « deny by default » sur un petit périmètre avant de la généraliser.

<div class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 322" role="img" aria-label="Chemin de sécurisation d'un port d'accès, de l'identité à la validation du trafic">
<rect x="1" y="1" width="918" height="320" rx="13" fill="#090d14" stroke="#2b3c50"/><text x="24" y="30" fill="#e7eef8" font-size="17" font-weight="700">Contrôles d'accès L2 — couches complémentaires</text>
<rect x="32" y="82" width="154" height="70" rx="9" fill="#14283d" stroke="#8cb5ff"/><text x="109" y="108" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">Terminal</text><text x="109" y="128" text-anchor="middle" fill="#a7b7cb" font-size="11">poste / IoT / voix</text>
<rect x="225" y="82" width="154" height="70" rx="9" fill="#14352f" stroke="#65e6a4"/><text x="302" y="108" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">Port access</text><text x="302" y="128" text-anchor="middle" fill="#a7b7cb" font-size="11">802.1X / MAB</text>
<rect x="418" y="82" width="154" height="70" rx="9" fill="#3b2c18" stroke="#ffca70"/><text x="495" y="108" text-anchor="middle" fill="#fff0d3" font-size="14" font-weight="700">Admission L2</text><text x="495" y="128" text-anchor="middle" fill="#ffca70" font-size="11">VLAN / MAC / STP</text>
<rect x="611" y="82" width="154" height="70" rx="9" fill="#241d3b" stroke="#c6a4ff"/><text x="688" y="108" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">Validation</text><text x="688" y="128" text-anchor="middle" fill="#c6a4ff" font-size="11">DHCP snooping / DAI</text>
<rect x="804" y="82" width="86" height="70" rx="9" fill="#14352f" stroke="#65e6a4"/><text x="847" y="108" text-anchor="middle" fill="#e7eef8" font-size="13" font-weight="700">Flux</text><text x="847" y="128" text-anchor="middle" fill="#a7b7cb" font-size="11">autorisé</text>
<path class="flow" d="M186 117 H225" stroke="#46d7f2" stroke-width="2.5" fill="none" marker-end="url(#ethArrow6)"/><path class="flow" d="M379 117 H418" stroke="#46d7f2" stroke-width="2.5" fill="none" marker-end="url(#ethArrow6)"/><path class="flow" d="M572 117 H611" stroke="#46d7f2" stroke-width="2.5" fill="none" marker-end="url(#ethArrow6)"/><path class="flow" d="M765 117 H804" stroke="#46d7f2" stroke-width="2.5" fill="none" marker-end="url(#ethArrow6)"/>
<rect x="100" y="196" width="720" height="85" rx="10" fill="#121e2c" stroke="#34465b"/><text x="460" y="219" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">Vérifier également la politique de sortie et l'exploitation</text><text x="460" y="242" text-anchor="middle" fill="#a7b7cb" font-size="12">ACL • QoS • journalisation • compteurs de rejet • inventaire des exceptions</text><text x="460" y="261" text-anchor="middle" fill="#ffca70" font-size="11">Un contrôle mal positionné peut bloquer un équipement légitime ou laisser un chemin de contournement.</text><defs><marker id="ethArrow6" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#46d7f2"/></marker></defs>
</svg>
</div>

### 6.2 Architecture de confiance

Définissez les frontières où les trames, tags et protocoles sont considérés fiables. Un port vers un serveur peut recevoir plusieurs MAC si l'hyperviseur héberge plusieurs VM ; un port vers un poste ne devrait pas nécessairement le permettre. Un lien vers un switch peut nécessiter les BPDU et plusieurs VLAN ; un port edge ne devrait pas être traité comme un uplink. Les politiques par défaut doivent être adaptées aux rôles réels.

Exemples de questions de revue :

- Peut-on connecter un switch non autorisé et créer un nouveau chemin ?
- Un terminal peut-il envoyer des BPDU ou des DHCP server offers ?
- Les bindings DHCP snooping couvrent-ils les terminaux statiques et le VLAN de voix ?
- Les mécanismes IPv6 sont-ils aussi contrôlés que leurs homologues IPv4 ?
- Un VLAN trunk permet-il de sortir du périmètre par un tag inattendu ?
- Les exceptions ont-elles un propriétaire, une justification, une date de révision et une télémétrie ?

### 6.3 L2 n'est pas seulement IPv4

Une politique qui protège ARP et DHCPv4 tout en autorisant les Router Advertisement IPv6 non contrôlés laisse un chemin de configuration réseau potentiellement non désiré. Le diagnostic doit inclure Neighbor Discovery, RA, DHCPv6, multicast, MLD et les comportements des terminaux. Les protections IPv6 dépendent des capacités et des limites de l'équipement : validez la documentation et effectuez des tests de conformité.

## 7. MTU, erreurs physiques, optiques et qualité réelle du lien

### 7.1 Distinguer trois couches de symptômes

Les erreurs de liaison peuvent être vues à plusieurs endroits :

1. **Physique / PHY :** perte de signal, erreurs FEC, puissance optique hors plage, négociation, autonegotiation ou compatibilité transceiver ;
2. **MAC / interface :** FCS/CRC, runt, giant, symbol errors, collisions sur environnements anciens, pause frames, drops de file ;
3. **Réseau / application :** perte, débit réduit, latence, déconnexions, retransmissions TCP, PMTUD défaillant.

Les compteurs ne sont pas universels. Certains matériels utilisent des noms différents, exposent plusieurs niveaux de FEC, ou comptent des erreurs corrigées séparément des erreurs non corrigées. Examinez **le delta dans le temps** et la documentation de la plateforme, pas uniquement une valeur cumulée depuis le dernier reboot.

| Signal | Interprétation possible | Vérification suivante |
|---|---|---|
| CRC/FCS en hausse sur un port | Erreurs de trame, signal/média/câble, compatibilité/PHY | Comparer les deux extrémités, remplacer un composant à la fois, inspecter FEC/optique |
| Drops sans CRC | Congestion, file saturée, policer, storm control ou limitation matérielle | Queue counters, QoS, broadcast et débit de sortie |
| Link flaps | Optique/câble, alimentation, module, négociation, défaut distant | Logs horodatés, DOM optique, événements PHY et partenaire |
| Runt/giant | Taille/configuration, trames mal formées, MTU ou comptage plateforme | Déterminer la définition du compteur et la capture réellement observée |
| FEC non corrigées en hausse | Qualité de signal ou marge de liaison insuffisante à haut débit | Puissance, type d'optique, fibre, connecteurs, FEC configurée/supportée |

### 7.2 MTU : raisonner bout en bout

Le MTU IP, la taille d'une trame de niveau 2 et la longueur réellement présente sur le fil ne sont pas la même mesure. La balise 802.1Q, les en-têtes superposés et les particularités d'encapsulation peuvent augmenter la taille nécessaire. Le terme « jumbo frames » n'a pas une seule valeur supportée sur tous les équipements : vérifier toute la chaîne et les limites exactes du produit.

<div class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 306" role="img" aria-label="Chemin MTU entre deux hôtes avec encapsulation VLAN ou overlay et point potentiel de rejet">
<rect x="1" y="1" width="918" height="304" rx="13" fill="#090d14" stroke="#2b3c50"/><text x="24" y="30" fill="#e7eef8" font-size="17" font-weight="700">MTU : le minimum du chemin peut devenir le goulot d'étranglement</text>
<rect x="35" y="79" width="154" height="65" rx="9" fill="#14283d" stroke="#8cb5ff"/><text x="112" y="104" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">Hôte A</text><text x="112" y="124" text-anchor="middle" fill="#a7b7cb" font-size="11">MTU 1500</text>
<rect x="241" y="79" width="160" height="65" rx="9" fill="#14352f" stroke="#65e6a4"/><text x="321" y="104" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">Switch d'accès</text><text x="321" y="124" text-anchor="middle" fill="#65e6a4" font-size="11">trame 802.1Q</text>
<rect x="456" y="79" width="160" height="65" rx="9" fill="#3b2c18" stroke="#ffca70"/><text x="536" y="104" text-anchor="middle" fill="#fff0d3" font-size="14" font-weight="700">Liaison intermédiaire</text><text x="536" y="124" text-anchor="middle" fill="#ffca70" font-size="11">MTU plus faible ?</text>
<rect x="671" y="79" width="214" height="65" rx="9" fill="#14283d" stroke="#8cb5ff"/><text x="778" y="104" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">Hôte / service B</text><text x="778" y="124" text-anchor="middle" fill="#a7b7cb" font-size="11">taille acceptée</text>
<path class="flow" d="M189 111 H241" stroke="#46d7f2" stroke-width="2.5" fill="none" marker-end="url(#ethArrow7)"/><path class="flow" d="M401 111 H456" stroke="#46d7f2" stroke-width="2.5" fill="none" marker-end="url(#ethArrow7)"/><path d="M616 111 H671" stroke="#ff7e83" stroke-width="2.5" fill="none" marker-end="url(#ethArrow7)"/>
<path d="M536 144 V175" stroke="#ff7e83" stroke-width="2" stroke-dasharray="4 4"/><rect x="364" y="179" width="344" height="54" rx="9" fill="#3d2027" stroke="#ff7e83"/><text x="536" y="201" text-anchor="middle" fill="#ffe8e9" font-size="13" font-weight="700">Point de rejet possible</text><text x="536" y="218" text-anchor="middle" fill="#ffb8bc" font-size="11">trame trop grande / ICMP nécessaire bloqué</text><text x="24" y="271" fill="#a7b7cb" font-size="12">Tester la taille utile de bout en bout ; contrôler MTU L2, MTU IP, encapsulation et messages ICMP/PMTUD.</text><defs><marker id="ethArrow7" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#46d7f2"/></marker></defs>
</svg>
</div>

Pour une trame Ethernet traditionnelle, le terme « taille de trame » est souvent exprimé hors préambule/SFD et intervalle intertrame. L'en-tête MAC, la charge utile, l'éventuelle balise et le FCS s'ajoutent selon les conventions retenues par la fiche technique. C'est pourquoi une affirmation comme « le lien accepte 9000 » est insuffisante sans préciser si elle parle de MTU IP, de la taille de trame totale et si la balise est comptée.

**Méthode de test :**

1. relever le MTU du système hôte et de chaque lien concerné ;
2. déterminer l'encapsulation réelle : Ethernet, VLAN, QinQ, tunnel ou overlay ;
3. tester plusieurs tailles, sans fragmentation si l'outil le permet, et observer le résultat ;
4. capturer au départ et à l'arrivée lorsque cela est possible ;
5. vérifier les ICMP « fragmentation needed » (IPv4) ou ICMPv6 Packet Too Big nécessaires à la découverte de MTU de chemin ;
6. vérifier que les pare-feu et ACL ne bloquent pas à tort les messages utiles ;
7. corriger la plus petite MTU incohérente ou ajuster le design sur tout le chemin.

Un ping standard réussi ne garantit pas que les paquets plus grands fonctionnent. Inversement, un ping bloqué ne prouve pas à lui seul un problème MTU : l'ICMP peut être filtré ou dépriorisé.

### 7.3 Auto-négociation et duplex

Sur les interfaces Ethernet modernes, l'auto-négociation, la vitesse, le duplex et la gestion du contrôle de flux dépendent du PHY et de la plateforme. Fixer manuellement une seule extrémité tout en laissant l'autre en auto peut créer une discordance sur les technologies concernées. Sur les liens optiques haut débit, les paramètres FEC et la compatibilité des modules peuvent être au moins aussi importants que la vitesse affichée.

Approche : comparer les deux extrémités, vérifier la documentation du transceiver/câble, contrôler compteurs et journaux, confirmer la puissance optique et les erreurs corrigées/non corrigées si exposées. Ne forcez pas vitesse, duplex ou FEC au hasard ; la correction doit correspondre aux capacités communes et aux recommandations du fabricant.

## 8. Observabilité, capture et preuve

### 8.1 Un plan d'observation multi-source

Les meilleurs diagnostics combinent au moins trois familles d'éléments :

- **état/compteurs** : interfaces, erreurs, discards, débit, FDB/MAC, STP, LACP, QoS ;
- **événements** : syslog, traps, événements de configuration, LLDP, changements de lien, bascules, authentication ;
- **paquets** : SPAN/port mirroring, TAP physique, capture hôte, `tcpdump`/Wireshark.

Chaque source répond à des questions différentes. Un TAP observe le flux au point de capture sans dépendre du plan de mirroring du switch, tandis que SPAN est plus pratique mais peut dropper en cas de surcharge et ne conserve pas nécessairement toutes les caractéristiques physiques. Une capture hôte voit ce que sa pile/carte expose, avec effets possibles d'offload.

### 8.2 Capture et filtres

Exemples à adapter au contexte et à l'outil :

```bash
# Capturer pendant 60 secondes sur une interface Linux
sudo timeout 60 tcpdump -i eth0 -nn -s 0 -w incident-l2.pcap

# Afficher uniquement les trames contenant du trafic VLAN (filtre de capture BPF selon libpcap)
sudo tcpdump -i eth0 -nn 'vlan'

# Inspecter la FDB d'un bridge Linux
bridge fdb show
bridge vlan show
ip -s link show dev eth0
ethtool -S eth0
```

Pour les trunks, une capture peut afficher les balises VLAN, mais cela dépend du point de capture, de la prise en charge et de l'offload. Pour étudier un problème de tagging, une capture effectuée avant l'ajout ou après le retrait de la balise ne montrera pas nécessairement le tag observé sur le fil.

Les captures peuvent contenir des identifiants, adresses, données applicatives ou informations sensibles. Choisir le point de capture, limiter la durée, conserver les fichiers de manière sécurisée, filtrer les champs personnels non nécessaires et suivre les règles internes de conservation. Ne collectez pas le trafic d'autres personnes sans autorisation.

### 8.3 Mirroring/SPAN : limites de conception

Avant d'interpréter une capture SPAN :

- confirmer les ports et VLAN sources ;
- confirmer le sens (entrée, sortie ou les deux) selon la plateforme ;
- contrôler la vitesse du port destination par rapport au trafic combiné ;
- vérifier les limitations sur les membres d'un port-channel et les trames taguées ;
- synchroniser les horloges avec les systèmes comparés ;
- noter le risque de perte, de réordonnancement ou de modification des métadonnées.

Une absence de paquet dans le SPAN n'est pas une preuve absolue qu'il n'a jamais existé. Corrélez avec les compteurs du port et une observation indépendante si l'impact est élevé.

## 9. Méthode de dépannage expert : passer du symptôme à une preuve

### 9.1 Ordre de vérification recommandé

1. **Définir le périmètre :** utilisateurs, VLAN, site, ports, services, début et fréquence.
2. **Établir l'état attendu :** topologie, VLAN, STP, LAG, MTU, sécurité, service normal.
3. **Comparer l'état réel :** config et état opérationnel, pas seulement la configuration.
4. **Chercher une corrélation temporelle :** changement, link flap, LACP, topology change, compteur, authentification.
5. **Isoler sans détruire les preuves :** ne pas effacer immédiatement les logs/counters ; exporter la configuration, noter les deltas et capturer si possible.
6. **Tester une hypothèse à la fois :** prédire ce que devrait changer le compteur, le chemin ou la capture si l'hypothèse est vraie.
7. **Appliquer une correction limitée :** changement approuvé, plan de retour arrière et contrôle du rayon d'impact.
8. **Valider fonctionnellement :** trafic utilisateur/application, pas seulement `up/up`.
9. **Observer après rétablissement :** stabilité, erreurs et absence de récidive.
10. **Documenter les preuves et les limites :** ce qui a été démontré, ce qui reste une hypothèse.

<div class="diagram">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 390" role="img" aria-label="Flux de diagnostic expert d'un incident de couche 2">
<rect x="1" y="1" width="918" height="388" rx="13" fill="#090d14" stroke="#2b3c50"/><text x="24" y="30" fill="#e7eef8" font-size="17" font-weight="700">Boucle d'investigation : chaque test doit réduire l'incertitude</text>
<rect x="274" y="52" width="372" height="49" rx="9" fill="#14283d" stroke="#8cb5ff"/><text x="460" y="73" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">1. Périmètre et référence</text><text x="460" y="89" text-anchor="middle" fill="#a7b7cb" font-size="11">service, VLAN, ports, heure, état attendu</text>
<rect x="274" y="124" width="372" height="49" rx="9" fill="#14352f" stroke="#65e6a4"/><text x="460" y="145" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">2. État réel et télémétrie</text><text x="460" y="161" text-anchor="middle" fill="#a7b7cb" font-size="11">STP, LACP, VLAN, FDB, erreurs, syslog</text>
<rect x="274" y="196" width="372" height="49" rx="9" fill="#3b2c18" stroke="#ffca70"/><text x="460" y="217" text-anchor="middle" fill="#fff0d3" font-size="14" font-weight="700">3. Hypothèse testable</text><text x="460" y="233" text-anchor="middle" fill="#ffca70" font-size="11">prédire la preuve qui confirmerait/infirmerait</text>
<rect x="274" y="268" width="372" height="49" rx="9" fill="#241d3b" stroke="#c6a4ff"/><text x="460" y="289" text-anchor="middle" fill="#e7eef8" font-size="14" font-weight="700">4. Correction contrôlée</text><text x="460" y="305" text-anchor="middle" fill="#c6a4ff" font-size="11">changer une variable, suivre le plan de retour</text>
<rect x="274" y="340" width="372" height="31" rx="8" fill="#153d32" stroke="#65e6a4"/><text x="460" y="360" text-anchor="middle" fill="#e7eef8" font-size="13" font-weight="700">5. Vérification et compte rendu</text>
<path class="flow" d="M460 101 V124" stroke="#46d7f2" stroke-width="2.2" fill="none" marker-end="url(#ethArrow8)"/><path class="flow" d="M460 173 V196" stroke="#46d7f2" stroke-width="2.2" fill="none" marker-end="url(#ethArrow8)"/><path class="flow" d="M460 245 V268" stroke="#46d7f2" stroke-width="2.2" fill="none" marker-end="url(#ethArrow8)"/><path class="flow" d="M460 317 V340" stroke="#46d7f2" stroke-width="2.2" fill="none" marker-end="url(#ethArrow8)"/><path d="M646 354 H783 V220 H646" stroke="#ffca70" stroke-width="2" stroke-dasharray="6 5" fill="none" marker-end="url(#ethArrow8)"/><text x="797" y="276" fill="#ffca70" font-size="11" transform="rotate(-90 797 276)">si résultat insuffisant, réviser l'hypothèse</text><defs><marker id="ethArrow8" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#46d7f2"/></marker></defs>
</svg>
</div>

### 9.2 Matrice symptomatique

| Symptôme | Première zone à examiner | Preuve qui renforce l'hypothèse | Erreur de diagnostic courante |
|---|---|---|---|
| Un seul VLAN est touché | Access, liste trunk, natif/tag, STP par VLAN/instance | VLAN absent/non-forwarding, MAC non apprise | Remplacer un câble sans examiner le périmètre VLAN |
| Tous les VLAN derrière un lien | PHY, agrégat, port-channel, voisinage | Link flap, erreurs physiques, membre sorti du LAG | Modifier une politique VLAN pour un incident de transport |
| Panne intermittente et MAC flapping | Boucle, LAG, mobilité de MAC, bridge hôte | Logs corrélés, chemins concurrents, variation de compteurs | Effacer la table MAC sans conserver les preuves |
| Débit faible mais interface saine | Hachage LAG, files QoS, vitesse négociée, FEC | Un membre surchargé ou compteurs de queue/drops | Conclure qu'un LAG de 4 × 10G garantit 40G par flux |
| Les gros transferts échouent | MTU, encapsulation, ICMP PMTUD | Petit paquet passe, grande taille échoue de façon reproductible | Changer l'MTU d'un seul équipement sans tester le chemin complet |
| Perte de paquets avec CRC en hausse | PHY/câble/fibre/transceiver | Delta CRC/FEC non corrigé, puissance hors seuil | Traiter le symptôme uniquement par QoS |
| Nouveau terminal n'obtient pas d'adresse | Authentification, VLAN, DHCP snooping/trust | Port dans mauvais VLAN, DHCP offer rejetée | Augmenter les timeouts DHCP sans valider L2 |
| IPv4 fonctionne mais IPv6 est instable | Multicast/NDP/RA Guard/ACL IPv6 | RA inattendu, NDP bloqué, MLD concerné | Supposer que la politique IPv4 protège automatiquement IPv6 |

## 10. Ateliers avancés

Les ateliers sont à réaliser dans un lab isolé (simulateur, matériel de test ou environnement virtuel). Les commandes sont des exemples. Le résultat exact dépend de la plateforme ; le but est de suivre un raisonnement de diagnostic et de démontrer la correction.

### Atelier 1 — Changement de root et protection de bordure

**Contexte :** les utilisateurs du VLAN 20 constatent une courte interruption après raccordement d'un switch de laboratoire. Les logs indiquent un changement de root. Le réseau comprend SW-CORE, SW-DIST et SW-LAB ; les utilisateurs sont raccordés à SW-DIST.

**Objectifs :** identifier le root, trouver pourquoi il a changé, rétablir un root contrôlé et éviter une récidive.

**Étapes :**

1. Sur les trois switches, relever `show spanning-tree vlan 20`, les priorités, identifiants de pont, root port et ports désignés.
2. Corréler l'heure du changement de root avec le log de raccordement et examiner la priorité de SW-LAB.
3. Vérifier si les liens de distribution et ports edge sont classés correctement ; ne pas activer PortFast au hasard sur les trunks.
4. Dans le plan d'adressage/topologie, désigner le root et le secondaire, puis appliquer une configuration approuvée et symétrique sur les instances requises.
5. Sur les ports de terminaux, activer les protections edge adaptées après vérification du rôle du port. Évaluer Root Guard aux frontières où le voisin ne doit pas devenir root ; n'appliquez pas Root Guard sur le chemin prévu vers le root.
6. Raccorder à nouveau le switch de labo dans le cadre du test ; confirmer que l'événement attendu est détecté et que le root reste inchangé ou que le port edge est protégé.

**Critères de réussite :** root documenté et stable ; rôles/états conformes à la topologie ; aucune boucle créée ; accès utilisateur vérifié ; événement journalisé ; procédure de récupération maîtrisée.

**Pièges :** Root Guard n'est pas un équivalent de BPDU Guard ; Loop Guard et UDLD répondent à des cas distincts ; une modification de priorité sur un seul équipement peut ne pas régler toutes les instances MST/VLAN.

### Atelier 2 — Trunk partiellement fonctionnel

**Contexte :** les utilisateurs du VLAN 10 communiquent entre deux bâtiments, mais le VLAN 30 est joignable dans le bâtiment A et pas dans B. Le trunk est `up/up`, le VLAN 30 existe sur les deux switches et les utilisateurs ont de bonnes adresses IP.

**Hypothèses initiales :** le VLAN 30 est absent de la liste autorisée, le VLAN est bloqué/non-forwarding par STP, ou les ports d'accès sont dans le mauvais VLAN. Une incohérence de tag natif est possible si le service dépend de trames non taguées.

**Procédure :**

1. relever l'interface trunk des deux côtés avec son état opérationnel, pas seulement sa configuration ;
2. comparer `show interfaces trunk`, `show vlan brief` et `show spanning-tree vlan 30` ;
3. vérifier l'entrée MAC source et destination sur les deux switches pendant une tentative de communication ;
4. faire une capture autorisée à un point utile et déterminer si la trame/ARP arrive, dans quel VLAN et par quel sens ;
5. isoler si le défaut se situe au port d'accès, au trunk, dans STP ou au-delà de L2 ;
6. corriger seulement la configuration incohérente, puis tester la communication dans les deux sens.

**Critères de réussite :** VLAN 30 admis sur tous les trunks requis ; forwarding selon le design ; MAC correctement apprise ; ping/ARP et application validés ; aucun VLAN non demandé n'a été ajouté à la liste.

**Retour arrière :** sauvegarder la liste initiale des VLAN autorisés et revenir à cette liste si l'activation provoque un changement non prévu.

### Atelier 3 — LACP formé mais performances inégales

**Contexte :** quatre liens de 10 Gb/s appartiennent en apparence au port-channel. Le service est opérationnel, mais le débit utile d'un transfert varie et un membre transporte presque tout le trafic.

**Hypothèses :** hachage basé sur des champs peu diversifiés, flux unique limité au débit d'un membre, membre partiellement opérationnel ou erreur de négociation.

**Procédure :**

1. vérifier la formation LACP sur les deux partenaires, le nombre de membres actifs et les états suspendus/individual ;
2. relever octets, paquets, erreurs et drops par membre à deux instants ; calculer les deltas ;
3. examiner le nombre de flux et leurs adresses/ports ; séparer le test d'un flux unique du test avec plusieurs flux indépendants ;
4. analyser les clés de hachage supportées, sans supposer que tous les champs sont utilisés ;
5. confirmer les vitesses, MTU, paramètres du trunk, FEC/optique, configuration multichâssis éventuelle ;
6. tester la perte d'un membre en fenêtre contrôlée et vérifier le maintien de service ainsi que la capacité résiduelle ;
7. ajuster le hachage uniquement si les données montrent que ce changement améliore le profil sans créer de déséquilibre plus sévère.

**Critères de réussite :** tous les membres prévus sont sélectionnés ; le trafic de test multi-flux s'équilibre conformément au hachage ; un test d'un flux est correctement interprété ; la panne d'un membre est absorbée dans la capacité annoncée.

### Atelier 4 — Une tempête de broadcast après ajout d'un équipement

**Contexte :** juste après le raccordement d'un petit switch non administré, le réseau présente de nombreux MAC flapping, des compteurs broadcast qui montent et des pertes applicatives.

**Exercice :** construisez une chronologie, listez les preuves utiles, choisissez un port de confinement, estimez l'impact de sa désactivation et définissez les contrôles qui confirmeront la disparition de la boucle. Indiquez également comment conserver suffisamment de preuves pour la RCA sans retarder un rétablissement urgent.

**Réponse attendue :** corrélation temporelle avec le nouveau raccordement ; inspection de la topologie réelle ; compteurs et logs exportés ; confinement ciblé ; stabilisation mesurée ; correction physique/configuration ; validation des services ; révision des protections edge et de la documentation. Le contrôle de tempête peut limiter l'impact mais ne remplace pas la suppression du chemin cyclique.

## 11. Plan de changement expert et retour arrière

Chaque changement L2 doit considérer que des configurations apparemment locales peuvent modifier le forwarding d'un VLAN entier, le root STP, une liste trunk, une agrégation ou un domaine de sécurité.

### Avant le changement

- décrire l'objectif, le service concerné, le périmètre et le risque ;
- relever la version, le modèle et les dépendances ;
- sauvegarder la configuration et l'état opérationnel utile ;
- capturer l'état des voisins, des VLAN, du STP, du LAG et des compteurs ;
- préparer les commandes d'application et de retour arrière ;
- définir les critères de succès et d'arrêt ;
- informer les équipes applicatives et exploitation.

### Pendant le changement

- changer une variable logique à la fois ;
- surveiller les logs, les ports, les compteurs et les alertes ;
- valider les rôles/états après chaque étape ;
- arrêter ou annuler dès qu'un critère critique est atteint ;
- conserver un horodatage de chaque action.

### Après le changement

- tester du trafic représentatif en entrée et en sortie ;
- comparer les métriques avant/après ;
- tester la redondance dans la mesure autorisée ;
- vérifier l'absence de nouveaux logs d'instabilité ;
- mettre à jour diagrammes, inventaire et runbook ;
- enregistrer les écarts, les risques restants et le résultat.

### Critères d'arrêt exemplaires

Les valeurs exactes doivent venir des objectifs du service et de la référence du réseau. Un changement peut devoir être annulé si :

- le root ou le rôle d'un port dévie du design prévu ;
- des membres attendus du LAG restent hors agrégat ;
- les compteurs CRC/FEC ou les drops croissent de façon anormale ;
- un VLAN non prévu devient transporté ;
- le taux de perte ou le délai applicatif dépasse le seuil approuvé ;
- le monitoring perd la visibilité du chemin affecté ;
- le retour arrière ne peut plus être effectué dans la fenêtre autorisée.

## 12. Modèle de compte rendu d'incident L2

Copiez ce modèle dans un ticket ou un runbook. N'y consignez pas de secrets ou de données utilisateur non nécessaires.

```text
ID / gravité :
Début et fin (avec fuseau horaire) :
Services / sites / VLAN touchés :
Symptôme décrit par l'utilisateur :
Topologie et ports suspects :
Changements récents :
État avant incident (STP, LAG, VLAN, MTU, erreurs) :
Éléments collectés (logs, compteurs, captures, horodatage) :
Hypothèses et tests qui les confirment/infirment :
Action de confinement :
Correction permanente :
Critères de validation fonctionnelle :
Résultat après rétablissement :
Risque résiduel / actions de suivi / responsable / échéance :
Cause démontrée et niveau de confiance :
```

Une RCA sérieuse sépare les **faits observés**, les **hypothèses** et la **cause démontrée**. Si les données ne permettent pas d'établir la cause avec certitude, décrivez les scénarios compatibles, les preuves manquantes et la mesure qui évitera une récidive tout en améliorant l'observabilité.

## 13. Quiz expert et corrigé

### Questions

1. Quelle est la différence entre une MAC apprise sur un VLAN et une MAC apprise sur un autre VLAN ?
2. Pourquoi un trunk peut-il rester `up/up` tout en interrompant un seul VLAN ?
3. BPDU Guard, Root Guard, Loop Guard et UDLD servent-ils au même objectif ?
4. Un agrégat de 4 × 10 Gb/s garantit-il 40 Gb/s pour une seule connexion TCP ? Pourquoi ?
5. Pourquoi faut-il examiner le delta des erreurs CRC plutôt que leur valeur cumulée ?
6. Une capture qui ne montre pas de FCS prouve-t-elle que le FCS n'existe pas sur le fil ?
7. Comment peut-on identifier une panne MTU au lieu d'une simple perte ICMP ?
8. Quels éléments permettent de distinguer une mobilité MAC légitime d'une boucle ?
9. Pourquoi une règle anti-ARP spoofing ne protège-t-elle pas automatiquement les mécanismes IPv6 ?
10. Quel est le risque d'activer un VLAN sur un trunk sans vérifier STP et le chemin de retour ?
11. Quelles différences opérationnelles existent entre une capture SPAN et un TAP ?
12. Pourquoi un seuil de storm-control trop bas peut-il causer une panne en tentant de la prévenir ?
13. Quels paramètres faut-il comparer pour un LAG qui ne sélectionne qu'une partie des membres ?
14. Pourquoi le contrôle de MTU doit-il inclure les encapsulations et la chaîne complète ?
15. Quelles preuves doivent être conservées avant de vider une table MAC ou de redémarrer un switch pendant un incident ?

### Corrigé condensé

1. L'entrée de transfert est contextualisée par le domaine VLAN ; les mêmes adresses peuvent exister dans des domaines distincts sans désigner le même chemin logique.
2. La liste VLAN, l'état STP, le port access ou les règles de tag peuvent différer alors que le PHY reste opérationnel.
3. Non : BPDU Guard protège les ports edge contre les BPDU inattendues ; Root Guard protège le rôle root ; Loop Guard traite certaines pertes de BPDU sur des ports non désignés ; UDLD détecte des défaillances unidirectionnelles selon le support.
4. Généralement non : un flux donné est haché sur un membre pour préserver l'ordre ; plusieurs flux peuvent profiter davantage de l'agrégat.
5. Un compteur cumulatif peut être ancien ; le delta indique si l'erreur s'accroît pendant l'incident.
6. Non. La carte, le driver, le SPAN ou l'outil de capture peut retirer ou ne pas exposer le FCS.
7. Tester plusieurs tailles sur un chemin reproductible, vérifier fragmentation/DF et ICMP PMTUD, comparer les points de capture et exclure les politiques ICMP.
8. Corréler le temps, les logs LACP/STP, la migration/hôte, la FDB, les compteurs de boucle et la topologie réelle.
9. ARP est IPv4 ; IPv6 utilise notamment Neighbor Discovery et Router Advertisements avec contrôles dédiés.
10. Cela peut changer le périmètre de forwarding, exposer un domaine et provoquer une boucle ou un chemin asymétrique.
11. SPAN est simple et flexible mais peut subir des pertes et des limitations d'implémentation ; un TAP observe physiquement le lien au point où il est placé, avec sa propre conception/capacité.
12. Des flux légitimes de découverte, DHCP, ARP ou multicast peuvent être supprimés, empêchant l'établissement du service.
13. État LACP aux deux côtés, compatibilité des paramètres, speed/duplex si pertinent, VLAN, MTU, erreurs, FEC, hashing et éventuel multichâssis.
14. La taille finale dépend des en-têtes, des tags, du tunnel et du maillon le plus contraignant ; les valeurs doivent être comparées dans la même convention.
15. Logs horodatés, état STP/LAG, tables MAC/VLAN, compteurs, topologie, configurations et captures utiles si autorisées ; documenter l'heure de toute action destructive.

## 14. Glossaire

- **BPDU** : unité de données de contrôle utilisée par STP.
- **CAM/FDB** : table d'apprentissage/transfert des adresses MAC.
- **CRC/FCS** : mécanisme de contrôle d'intégrité de trame Ethernet.
- **DAI** : Dynamic ARP Inspection.
- **DEI/PCP/VID** : champs du TCI de la balise VLAN 802.1Q.
- **FDB/MAC flapping** : changement rapide ou répété du port associé à une MAC.
- **LACP/LAG** : protocole d'agrégation et agrégat logique de liens.
- **MSTP/RSTP/STP** : variantes et mécanismes de spanning tree.
- **MTU** : taille maximale d'un paquet/cadre selon le contexte de mesure ; préciser la couche.
- **NDP/RA** : Neighbor Discovery et Router Advertisement IPv6.
- **PCP** : priorité de niveau 2 portée dans le tag 802.1Q.
- **SPAN/TAP** : méthodes d'observation du trafic.
- **Storm control** : limite configurable sur des classes de trafic diffusé/multicast/unicast inconnu, selon l'équipement.
- **UDLD** : mécanisme de détection unidirectionnelle sur les liens pris en charge.
- **VLAN/trunk** : domaine logique de pontage et lien transportant un ou plusieurs VLAN.
- **VXLAN/EVPN** : technologies utilisées, notamment en datacenter, pour transporter des segments L2 au-dessus d'un underlay routé et distribuer l'information associée.

## 15. Références techniques

Les commandes et recommandations spécifiques doivent être validées contre la version exacte du matériel/logiciel installé.

- [IEEE 802.1Q — Bridges and Bridged Networks](https://standards.ieee.org/ieee/802.1q/10323/) : pontage, VLAN, fonctionnement des réseaux bridgés.
- [IEEE 802.1AX — Link Aggregation](https://standards.ieee.org/ieee/802.1AX/6768/) : agrégation de liens et répartition résiliente.
- [IEEE 802.1X — Port-Based Network Access Control](https://standards.ieee.org/ieee/802.1X/7345/) : contrôle d'accès réseau basé sur les ports.
- [Cisco — PortFast et BPDU Guard](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10586-65.html) : fonctionnement et précautions des protections de bordure.
- [Cisco — Root Guard](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10588-74.html) : protection de la racine et différences avec d'autres mécanismes.
- [Cisco — Loop Guard et BPDU protections](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol-stp-8021d/218321-configure-stp-with-loop-guard-and-bpdu-s.html) : scénarios et précautions d'application.
- [Cisco — Dépannage de MAC flapping et boucle](https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol-stp-8021d/221722-troubleshoot-mac-flaps-loop-on-cisco-cat.html) : signaux de boucles et préventions.
- [RFC 7348 — VXLAN](https://www.rfc-editor.org/rfc/rfc7348.html) : encapsulation de segments Ethernet au-dessus d'un réseau IP, overhead et limites pratiques.
- [Documentation Linux `bridge`](https://man7.org/linux/man-pages/man8/bridge.8.html) et [`ethtool`](https://man7.org/linux/man-pages/man8/ethtool.8.html) : inspection des bridges, FDB, statistiques et paramètres PHY.

## Conclusion

Un réseau Ethernet professionnel est fiable quand le comportement attendu est explicite et mesurable : les VLAN suivent les chemins documentés, STP a un rôle contrôlé, les agrégats ont des membres cohérents, le MTU est compatible de bout en bout, les trames anormales sont contenues, et les données d'exploitation permettent de remonter à la cause.

Le niveau expert consiste moins à mémoriser une commande qu'à savoir **quelle preuve chercher, quel test isoler, quel risque créer par une action et comment démontrer le rétablissement**. Cette discipline rend les incidents plus courts, les changements plus sûrs et les causes récurrentes plus faciles à éliminer.
