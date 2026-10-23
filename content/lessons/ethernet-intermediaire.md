# Ethernet et couche 2 — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Prérequis :** connaître le rôle d’un commutateur, les adresses MAC, la notion de VLAN et les commandes réseau de base.  
**Objectif :** diagnostiquer et exploiter un réseau Ethernet commuté en reliant le comportement des trames aux VLAN, au trunking, au spanning tree, à l’agrégation de liens et aux fonctions de sécurité de couche 2.

## Présentation

Ethernet est souvent décrit comme une technologie simple : brancher un câble, attribuer un VLAN et laisser le commutateur acheminer les trames. En exploitation, les pannes les plus gênantes proviennent fréquemment de détails de couche 2 : une adresse MAC apprise sur un mauvais port, un VLAN qui n’est pas autorisé sur le trunk, un VLAN natif incohérent, un port bloqué par STP, un EtherChannel partiellement formé ou un port placé en état *err-disabled*. Pour les résoudre, il faut comprendre ce que le commutateur apprend, ce qu’il transmet, ce qu’il filtre et ce qu’il bloque volontairement.

Ce cours prolonge les bases d’Ethernet. Il ne cherche pas à répéter uniquement les définitions, mais à relier les champs des trames, la table MAC, IEEE 802.1Q, STP/RSTP, LACP, LLDP et les contrôles de sécurité dans une méthode de diagnostic reproductible. Les exemples de configuration emploient une syntaxe Cisco IOS/IOS XE courante ; les commandes et valeurs par défaut doivent être vérifiées sur la version exacte de chaque équipement.

> **Analogie :** imagine un centre de distribution. La MAC de destination est l’adresse du destinataire, la table MAC est le registre des portes où se trouvent les destinataires, et le VLAN est une zone distincte du bâtiment. Un trunk est un couloir qui transporte des colis appartenant à plusieurs zones, en conservant leur étiquette. STP ferme volontairement un passage redondant pour éviter que les colis tournent indéfiniment. LACP assemble plusieurs voies physiques en une liaison logique. Chaque mécanisme répond donc à une question différente ; les confondre ralentit le diagnostic.

## 1. Théorie et fonctionnement

### 1.1. Rappels sur une trame Ethernet

Une trame Ethernet transporte les informations nécessaires à l’acheminement local d’un message. Dans le cas usuel, elle contient une adresse MAC de destination, une adresse MAC source, un champ Type/Longueur, des données et une FCS (*Frame Check Sequence*) utilisée pour détecter certaines erreurs de transmission. Le préambule, le délimiteur de début de trame et l’intervalle intertrame font partie du fonctionnement physique mais ne figurent pas toujours dans les captures de la même façon.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 270" width="100%" role="img" aria-label="Champs d'une trame Ethernet avec une étiquette VLAN 802.1Q"><rect x="1" y="1" width="918" height="268" rx="16" fill="#0b1220" stroke="#26364b"/><style>@keyframes ethernetFlowDash{to{stroke-dashoffset:-34}}.flow{stroke-dasharray:9 8;animation:ethernetFlowDash 2.2s linear infinite}.flow-slow{stroke-dasharray:7 8;animation:ethernetFlowDash 3.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow,.flow-slow{animation:none!important}}</style><defs><marker id="v1cyan" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#45d6f5"/></marker></defs><path class="flow" d="M30 53 H886" fill="none" stroke="#45d6f5" stroke-width="2" marker-end="url(#v1cyan)"/><text x="460" y="30" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#f1f5f9">Anatomie d’une trame Ethernet</text><g font-family="Arial,sans-serif" font-size="13" text-anchor="middle"><rect x="28" y="75" width="130" height="72" rx="8" fill="#12334a" stroke="#45d6f5"/><text x="93" y="103" fill="#eaf8ff" font-weight="700">MAC destination</text><text x="93" y="125" fill="#a7c6d9">6 octets</text><rect x="165" y="75" width="130" height="72" rx="8" fill="#12334a" stroke="#45d6f5"/><text x="230" y="103" fill="#eaf8ff" font-weight="700">MAC source</text><text x="230" y="125" fill="#a7c6d9">6 octets</text><rect x="302" y="75" width="126" height="72" rx="8" fill="#3b2d18" stroke="#f6bd60"/><text x="365" y="100" fill="#fff4dc" font-weight="700">Tag 802.1Q</text><text x="365" y="122" fill="#f1d39c">4 octets*</text><rect x="435" y="75" width="115" height="72" rx="8" fill="#12334a" stroke="#45d6f5"/><text x="492" y="103" fill="#eaf8ff" font-weight="700">EtherType</text><text x="492" y="125" fill="#a7c6d9">2 octets</text><rect x="557" y="75" width="220" height="72" rx="8" fill="#123c32" stroke="#43d9a3"/><text x="667" y="103" fill="#e9fff6" font-weight="700">Données / payload</text><text x="667" y="125" fill="#a4e7cf">Taille variable</text><rect x="784" y="75" width="108" height="72" rx="8" fill="#3b202a" stroke="#ff6b76"/><text x="838" y="103" fill="#ffe8ec" font-weight="700">FCS</text><text x="838" y="125" fill="#f0b8c0">4 octets</text></g><path d="M28 165 H892" stroke="#52657d" stroke-width="1.5"/><path d="M93 177 V196 H365 V177" fill="none" stroke="#f6bd60" stroke-width="1.5"/><text x="229" y="216" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#f6d69a">Tag présent uniquement si la trame est étiquetée</text><path d="M557 177 V196 H777 V177" fill="none" stroke="#43d9a3" stroke-width="1.5"/><text x="667" y="216" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#a4e7cf">Le payload peut contenir IP, ARP, etc.</text><text x="460" y="246" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#9db0c7">* Le tag 802.1Q ajoute 4 octets ; préambule et IFG ne sont pas représentés.</text></svg></div>

Les adresses MAC Ethernet classiques font 48 bits et sont généralement écrites sous forme de six octets hexadécimaux, par exemple `00:1A:2B:3C:4D:5E`. L’adresse source identifie l’émetteur sur le segment Ethernet ; elle n’est pas nécessairement l’adresse de l’application qui a initié une communication distante. Lorsqu’un poste envoie un paquet vers un hôte d’un autre réseau IP, la destination Ethernet est en général la MAC de la passerelle locale, et non la MAC finale située sur le réseau distant.

Le champ EtherType identifie le protocole encapsulé pour les valeurs reconnues, par exemple IPv4 ou ARP. Avec 802.1Q, un tag est inséré dans la trame pour indiquer le VLAN et transporter les bits de priorité de couche 2. Sur un trunk, ce tag permet au commutateur voisin d’identifier le VLAN de la trame. Le tag n’est pas ajouté à toutes les trames de tous les ports : le traitement dépend du type de port, du VLAN natif et de la configuration.

Dans le format Ethernet usuel, la taille d’une trame non taguée est classiquement comprise entre 64 et 1518 octets, FCS comprise, sans compter le préambule et l’intervalle intertrame. Une étiquette VLAN ajoute quatre octets ; les valeurs maximales prises en charge dépendent des équipements et des options de trames étendues. Le MTU IP de 1500 octets ne doit pas être confondu avec la taille totale de la trame Ethernet. Certains outils de capture n’incluent pas la FCS, notamment parce que les interfaces réseau la retirent généralement avant de livrer la trame au système.

### 1.2. Comment un commutateur apprend les adresses MAC

Lorsqu’une trame entre par un port, le commutateur observe d’abord son adresse MAC source et le VLAN associé à la trame. Il peut alors enregistrer une association du type « MAC source → VLAN → port d’entrée ». C’est l’apprentissage dynamique. Lorsqu’une trame suivante arrive, le commutateur consulte la table MAC pour déterminer où envoyer la trame de destination.

Trois cas principaux existent :

1. **Destination connue sur un autre port du même VLAN :** la trame est transmise sur le port associé à l’adresse de destination.
2. **Destination connue sur le même port d’entrée :** le commutateur peut filtrer la trame au lieu de la réémettre sur le même port.
3. **Destination inconnue dans ce VLAN :** la trame unicast est généralement *floodée* sur les ports de transfert du VLAN, sauf le port d’entrée. Le flooding ne traverse pas arbitrairement tous les VLAN : il est limité au domaine de couche 2 concerné.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 330" width="100%" role="img" aria-label="Apprentissage des adresses MAC et flooding d'une destination inconnue"><rect x="1" y="1" width="918" height="328" rx="16" fill="#0b1220" stroke="#26364b"/><style>@keyframes ethernetFlowDash{to{stroke-dashoffset:-34}}.flow{stroke-dasharray:9 8;animation:ethernetFlowDash 2.2s linear infinite}.flow-slow{stroke-dasharray:7 8;animation:ethernetFlowDash 3.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow,.flow-slow{animation:none!important}}</style><defs><marker id="v3cyan" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#45d6f5"/></marker><marker id="v3green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#43d9a3"/></marker><marker id="v3amber" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#f6bd60"/></marker><marker id="v3red" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ff6b76"/></marker></defs><text x="460" y="30" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#f1f5f9">Table MAC : apprentissage et flooding</text><g font-family="Arial,sans-serif" text-anchor="middle"><rect x="44" y="77" width="156" height="75" rx="10" fill="#12334a" stroke="#45d6f5"/><text x="122" y="105" font-size="16" font-weight="700" fill="#eaf8ff">Hôte A</text><text x="122" y="128" font-size="12" fill="#a7c6d9">MAC AA:AA</text><rect x="362" y="99" width="196" height="118" rx="12" fill="#17283a" stroke="#6f8ca9" stroke-width="2"/><text x="460" y="129" font-size="17" font-weight="700" fill="#f1f5f9">Switch</text><rect x="385" y="145" width="150" height="52" rx="7" fill="#0b1220" stroke="#43d9a3"/><text x="460" y="166" font-size="12" fill="#a4e7cf">Table MAC</text><text x="460" y="184" font-size="11" fill="#e9fff6">AA:AA → port 1</text><rect x="714" y="55" width="160" height="65" rx="9" fill="#30254b" stroke="#bba4ff"/><text x="794" y="80" font-size="15" font-weight="700" fill="#f4efff">Hôte B</text><text x="794" y="101" font-size="12" fill="#d4c9ff">MAC inconnue</text><rect x="714" y="147" width="160" height="65" rx="9" fill="#30254b" stroke="#bba4ff"/><text x="794" y="172" font-size="15" font-weight="700" fill="#f4efff">Hôte C</text><text x="794" y="193" font-size="12" fill="#d4c9ff">Même VLAN</text><rect x="714" y="239" width="160" height="65" rx="9" fill="#3b202a" stroke="#ff6b76"/><text x="794" y="264" font-size="15" font-weight="700" fill="#ffe8ec">Hôte D</text><text x="794" y="285" font-size="12" fill="#f0b8c0">Autre VLAN</text></g><path class="flow" d="M200 114 H354" stroke="#45d6f5" stroke-width="3" fill="none" marker-end="url(#v3cyan)"/><text x="278" y="100" font-family="Arial,sans-serif" font-size="12" fill="#a7e8f7" text-anchor="middle">Source AA:AA</text><path class="flow" d="M558 125 L706 87" stroke="#43d9a3" stroke-width="3" fill="none" marker-end="url(#v3green)"/><path class="flow" d="M558 157 H706" stroke="#43d9a3" stroke-width="3" fill="none" marker-end="url(#v3green)"/><path d="M558 190 L706 270" stroke="#ff6b76" stroke-width="2" fill="none" stroke-dasharray="5 6"/><path d="M675 258 L686 282 M686 258 L675 282" stroke="#ff6b76" stroke-width="3"/><text x="621" y="111" font-family="Arial,sans-serif" font-size="11" fill="#a4e7cf" text-anchor="middle">Flood unicast</text><text x="460" y="303" font-family="Arial,sans-serif" font-size="12" fill="#9db0c7" text-anchor="middle">Le flooding d’une destination inconnue reste limité au VLAN et exclut le port d’entrée.</text></svg></div>

La table MAC est dynamique : les entrées apprises peuvent expirer après une période d’inactivité, dont la valeur dépend de la plateforme et de la configuration. Une adresse MAC peut également être apprise de nouveau sur un autre port lorsque l’hôte se déplace. Cela est normal dans certains cas, mais des changements rapides et répétés peuvent indiquer une boucle, un pont inattendu, une mauvaise agrégation ou une adresse clonée.

Commandes courantes :

```text
show mac address-table
show mac address-table dynamic
show mac address-table address 001a.2b3c.4d5e
show mac address-table vlan 20
show interfaces counters errors
```

La syntaxe et les options varient selon l’OS. Dans une enquête, note le VLAN, l’adresse, le port observé, l’heure et l’état du port. Une MAC absente ne démontre pas à elle seule une panne : aucun trafic récent, une expiration, un filtre de sécurité ou un point de capture différent peuvent expliquer son absence.

### 1.3. VLAN : segmentation et frontières de couche 2

Un VLAN constitue un domaine logique de couche 2. Les hôtes d’un même VLAN peuvent échanger des trames à travers les commutateurs qui transportent ce VLAN. Deux VLAN distincts correspondent en règle générale à des domaines de broadcast séparés. Une communication entre eux exige une fonction de couche 3, par exemple des interfaces virtuelles (SVI) sur un commutateur multicouche ou des sous-interfaces sur un routeur.

Le VLAN ne constitue pas à lui seul un mécanisme complet de sécurité. Il limite le domaine de diffusion et aide à isoler les segments, mais un routage autorisé peut permettre les communications entre segments. Les contrôles d’accès, les pare-feu, les listes de contrôle d’accès, l’authentification des terminaux et la surveillance restent nécessaires selon le niveau de risque.

Un plan VLAN maintenable associe les identifiants à des rôles explicites. Exemple : VLAN 10 pour les postes, VLAN 20 pour la téléphonie, VLAN 30 pour les imprimantes, VLAN 40 pour les invités et VLAN 99 pour l’administration. Ces numéros ne sont que des exemples ; il faut adopter une convention cohérente et documentée dans l’environnement réel.

Un VLAN doit être vérifié à plusieurs endroits : existe-t-il sur le commutateur ? Le port du terminal est-il affecté au bon VLAN ? Le lien inter-switch transporte-t-il ce VLAN ? STP autorise-t-il le port à transférer pour ce VLAN ? Le terminal reçoit-il une configuration IP adaptée ? Ces questions évitent d’attribuer une panne réseau à DHCP ou au routage avant de confirmer le fonctionnement de la couche 2.

### 1.4. Port access et trunk 802.1Q

Un port *access* est généralement destiné à un terminal appartenant à un VLAN unique. Le terminal envoie normalement des trames Ethernet non étiquetées ; le commutateur associe le trafic entrant au VLAN configuré sur le port. Sur un port trunk, plusieurs VLAN peuvent traverser le même lien et l’identification 802.1Q est utilisée pour les trames étiquetées.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 350" width="100%" role="img" aria-label="Différence entre port access et trunk avec VLAN 10 et 20"><rect x="1" y="1" width="918" height="348" rx="16" fill="#0b1220" stroke="#26364b"/><style>@keyframes ethernetFlowDash{to{stroke-dashoffset:-34}}.flow{stroke-dasharray:9 8;animation:ethernetFlowDash 2.2s linear infinite}.flow-slow{stroke-dasharray:7 8;animation:ethernetFlowDash 3.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow,.flow-slow{animation:none!important}}</style><defs><marker id="v2cyan" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#45d6f5"/></marker><marker id="v2green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#43d9a3"/></marker><marker id="v2amber" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#f6bd60"/></marker><marker id="v2red" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ff6b76"/></marker></defs><text x="460" y="30" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#f1f5f9">Ports access et trunk 802.1Q</text><g font-family="Arial,sans-serif" text-anchor="middle"><rect x="38" y="65" width="190" height="86" rx="10" fill="#12334a" stroke="#45d6f5"/><text x="133" y="92" font-size="16" font-weight="700" fill="#eaf8ff">PC-A</text><text x="133" y="116" font-size="13" fill="#a7c6d9">VLAN 10</text><text x="133" y="135" font-size="12" fill="#a7c6d9">Trame non taguée</text><rect x="38" y="205" width="190" height="86" rx="10" fill="#30254b" stroke="#bba4ff"/><text x="133" y="232" font-size="16" font-weight="700" fill="#f4efff">PC-B</text><text x="133" y="256" font-size="13" fill="#d4c9ff">VLAN 20</text><text x="133" y="275" font-size="12" fill="#d4c9ff">Trame non taguée</text><rect x="355" y="112" width="210" height="132" rx="12" fill="#17283a" stroke="#6f8ca9" stroke-width="2"/><text x="460" y="145" font-size="17" font-weight="700" fill="#f1f5f9">Switch A</text><rect x="386" y="164" width="148" height="28" rx="6" fill="#12334a" stroke="#45d6f5"/><text x="460" y="183" font-size="12" fill="#eaf8ff">Access VLAN 10 / 20</text><text x="460" y="220" font-size="12" fill="#a7c6d9">Classification à l'entrée</text><rect x="692" y="112" width="190" height="132" rx="12" fill="#17283a" stroke="#6f8ca9" stroke-width="2"/><text x="787" y="145" font-size="17" font-weight="700" fill="#f1f5f9">Switch B</text><rect x="716" y="164" width="142" height="28" rx="6" fill="#123c32" stroke="#43d9a3"/><text x="787" y="183" font-size="12" fill="#e9fff6">Trunk 802.1Q</text><text x="787" y="220" font-size="12" fill="#a4e7cf">VLAN autorisés : 10, 20</text></g><path d="M228 108 H350" fill="none" stroke="#45d6f5" stroke-width="3" marker-end="url(#v2cyan)"/><path d="M228 248 H350" fill="none" stroke="#bba4ff" stroke-width="3" marker-end="url(#v2cyan)"/><path class="flow" d="M565 157 H684" fill="none" stroke="#43d9a3" stroke-width="4" marker-end="url(#v2green)"/><path class="flow-slow" d="M565 200 H684" fill="none" stroke="#bba4ff" stroke-width="4" marker-end="url(#v2green)"/><text x="625" y="141" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#a4e7cf">VLAN 10 tagué</text><text x="625" y="223" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#d4c9ff">VLAN 20 tagué</text><text x="460" y="320" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#9db0c7">Un trunk transporte plusieurs VLAN ; il ne fait pas, à lui seul, le routage entre eux.</text></svg></div>

La liste des VLAN autorisés d’un trunk limite les VLAN qui peuvent être transportés. Ne suppose pas qu’un VLAN est autorisé simplement parce qu’il existe sur les deux commutateurs. Il faut contrôler explicitement la configuration administrative et les VLAN actifs/forwarding. Une liste plus restrictive réduit les flux inutiles et la surface d’erreur, à condition d’autoriser tous les VLAN nécessaires au service.

Le VLAN natif, sur les trunks 802.1Q selon le comportement Cisco usuel, concerne les trames non taguées reçues et l’émission de trafic de ce VLAN. Il doit être identique aux deux extrémités, ou configuré de manière explicitement compatible, sous peine de classification incohérente. Une trame non étiquetée reçue sur un trunk peut être placée dans le VLAN natif configuré localement : si l’autre côté utilise une autre valeur, les deux commutateurs ne classeront pas nécessairement cette trame dans le même VLAN.

Exemple de configuration d’un port d’accès, sur un commutateur IOS/IOS XE compatible :

```cisco
vlan 10
 name POSTES
!
interface GigabitEthernet1/0/10
 description Poste-utilisateur
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
```

PortFast doit être réservé aux ports d’accès raccordés à des terminaux, pas à un lien inter-switch. BPDU Guard met normalement en protection un port PortFast qui reçoit un BPDU ; le port peut passer en *err-disabled*. Cette réaction est volontaire : elle signale souvent une connexion inattendue à un autre commutateur. Vérifie d’abord la topologie avant de réactiver le port.

Exemple de trunk explicite :

```cisco
interface GigabitEthernet1/0/48
 description Uplink-vers-SW-DIST
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,99
 switchport trunk native vlan 999
 switchport nonegotiate
```

Le VLAN natif `999` est illustratif. Crée-le et applique la politique correspondante selon la plateforme et les standards de l’organisation. `switchport nonegotiate` évite les échanges DTP sur les plateformes qui le prennent en charge ; les deux extrémités doivent être configurées explicitement en trunk. La liste exacte des options et leurs effets doivent être vérifiés sur l’OS en service.

Pour contrôler un trunk :

```cisco
show interfaces trunk
show interfaces GigabitEthernet1/0/48 switchport
show vlan brief
show spanning-tree vlan 10
```

### 1.5. VLAN natif et sécurité du trunk

Une incohérence de VLAN natif peut entraîner des erreurs de classification, des alertes STP et des risques de sécurité. Les trames attendues dans un VLAN peuvent être reçues dans un autre, ou être traitées différemment à chaque extrémité. Pendant le diagnostic, vérifie la configuration native sur les deux côtés, l’existence du VLAN natif et les politiques de tag natif éventuellement propres à la plateforme.

Les bonnes pratiques générales sont de configurer statiquement les trunks prévus, de désactiver la négociation dynamique lorsque cela est pris en charge et voulu, de limiter la liste des VLAN, d’utiliser un VLAN natif dédié et inutilisé par les terminaux et de documenter les liens. Cela ne signifie pas qu’un numéro précis de VLAN est universellement « sûr » : la sûreté vient de la politique appliquée et de son contrôle cohérent.

Évite de connecter directement des terminaux non maîtrisés sur un trunk. Un port access n’est pas infaillible, mais il réduit l’ambiguïté sur le VLAN d’entrée. Là où c’est pertinent, combine cette segmentation avec 802.1X, port-security, DHCP snooping, Dynamic ARP Inspection et IP Source Guard, en tenant compte de la compatibilité de la plateforme et de l’ordre de déploiement.

### 1.6. STP : pourquoi une liaison redondante peut être bloquée

Les commutateurs Ethernet peuvent apprendre des adresses MAC de manière dynamique. Une boucle de couche 2 peut provoquer une circulation répétée des trames de broadcast et de certaines trames unicast, un phénomène parfois appelé *broadcast storm*. Comme une trame Ethernet ordinaire ne possède pas de champ de durée de vie comparable au TTL IP, la boucle ne se corrige pas forcément d’elle-même. STP (*Spanning Tree Protocol*) découvre la topologie, élit un pont racine et place certains ports dans un état qui empêche les boucles de transfert.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 350" width="100%" role="img" aria-label="Topologie redondante avec un lien bloqué par spanning tree pour éviter une boucle"><rect x="1" y="1" width="918" height="348" rx="16" fill="#0b1220" stroke="#26364b"/><style>@keyframes ethernetFlowDash{to{stroke-dashoffset:-34}}.flow{stroke-dasharray:9 8;animation:ethernetFlowDash 2.2s linear infinite}.flow-slow{stroke-dasharray:7 8;animation:ethernetFlowDash 3.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow,.flow-slow{animation:none!important}}</style><defs><marker id="v4cyan" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#45d6f5"/></marker><marker id="v4green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#43d9a3"/></marker><marker id="v4amber" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#f6bd60"/></marker><marker id="v4red" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ff6b76"/></marker></defs><text x="460" y="30" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#f1f5f9">Spanning Tree : éviter la boucle de couche 2</text><g font-family="Arial,sans-serif" text-anchor="middle"><rect x="350" y="58" width="220" height="68" rx="10" fill="#123c32" stroke="#43d9a3" stroke-width="2"/><text x="460" y="85" font-size="17" font-weight="700" fill="#e9fff6">SW1 — Root Bridge</text><text x="460" y="107" font-size="12" fill="#a4e7cf">Bridge ID le plus faible</text><rect x="92" y="231" width="210" height="70" rx="10" fill="#17283a" stroke="#45d6f5" stroke-width="2"/><text x="197" y="260" font-size="17" font-weight="700" fill="#eaf8ff">SW2</text><text x="197" y="282" font-size="12" fill="#a7c6d9">Port racine vers SW1</text><rect x="618" y="231" width="210" height="70" rx="10" fill="#17283a" stroke="#45d6f5" stroke-width="2"/><text x="723" y="260" font-size="17" font-weight="700" fill="#eaf8ff">SW3</text><text x="723" y="282" font-size="12" fill="#a7c6d9">Port racine vers SW1</text></g><path class="flow-slow" d="M382 126 L250 224" fill="none" stroke="#45d6f5" stroke-width="4" marker-end="url(#v4cyan)"/><path class="flow-slow" d="M538 126 L670 224" fill="none" stroke="#45d6f5" stroke-width="4" marker-end="url(#v4cyan)"/><path d="M302 258 H618" fill="none" stroke="#ff6b76" stroke-width="3" stroke-dasharray="8 7"/><path d="M443 245 L465 271 M465 245 L443 271" stroke="#ff6b76" stroke-width="4"/><text x="460" y="232" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#ff9ea6">Lien redondant bloqué</text><text x="460" y="323" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#9db0c7">Le lien physique reste présent ; STP empêche qu’il crée un chemin de transfert en boucle.</text></svg></div>

Le **Root Bridge** est élu en fonction du Bridge ID, composé notamment d’une priorité et d’une adresse MAC système, avec des détails liés à l’extension système/VLAN selon l’implémentation. La valeur Bridge ID la plus faible remporte l’élection. Pour concevoir la topologie, il est préférable de choisir intentionnellement la racine plutôt que de laisser l’élection dépendre des valeurs par défaut.

Les concepts clés sont :

- **Root Port :** port non racine qui offre le meilleur chemin vers le Root Bridge sur ce commutateur.
- **Designated Port :** port choisi pour transmettre sur un segment donné selon la comparaison des informations STP.
- **Alternate Port :** dans RSTP, port de secours offrant un autre chemin vers la racine ; il ne transfère pas les données dans l’état alternatif.
- **BPDU :** trame de contrôle par laquelle les commutateurs échangent des informations de topologie STP.

STP classique (IEEE 802.1D) peut avoir une convergence plus lente que RSTP. RSTP (IEEE 802.1w, intégré ensuite au cadre de pontage de 802.1Q) ajoute des rôles et mécanismes de transition qui permettent généralement une convergence plus rapide lorsqu’ils sont déployés de manière cohérente. Les extensions propriétaires, par exemple PVST+ ou Rapid-PVST+ sur certains équipements Cisco, gèrent les instances STP d’une façon qui peut différer d’un mode MST ou d’un pontage multi-constructeur. Il faut comprendre quel mode tourne réellement dans le réseau.

Une connexion redondante n’est pas forcément défectueuse parce qu’elle ne transfère pas. Si STP l’a sélectionnée comme chemin alternatif, elle doit rester bloquée pour empêcher une boucle. Le diagnostic doit comparer le rôle et l’état du port, le Root ID, le coût du chemin et les BPDUs, plutôt que de désactiver STP pour « débloquer » le lien.

Commandes usuelles :

```cisco
show spanning-tree
show spanning-tree vlan 10
show spanning-tree root
show spanning-tree interface GigabitEthernet1/0/48 detail
show spanning-tree inconsistentports
```

L’option exacte varie selon plateforme. Sur un incident, sauvegarde les sorties avant d’effectuer un changement de priorité ou de port. La modification STP peut affecter de nombreux VLAN et déplace potentiellement le chemin de transfert.

### 1.7. RSTP : rôles, états et convergence

RSTP réduit la dépendance aux temporisateurs de STP traditionnel en utilisant notamment l’échange d’informations de rôle/état et des transitions rapides adaptées aux liens point-à-point. Ses rôles comprennent root, designated, alternate et backup, même si le rôle backup est peu fréquent dans des topologies Ethernet modernes usuelles.

Il ne faut pas confondre le rôle STP et l’état du port. Un port racine est un rôle ; forwarding est un état de transfert. Le couple rôle/état décrit si le port est le meilleur chemin vers la racine et s’il transmet actuellement des trames utilisateur. Les noms d’état diffèrent quelque peu entre les représentations STP classique et RSTP, mais les fonctions essentielles sont l’apprentissage de topologie et la prévention de boucles.

PortFast est destiné à accélérer la transition des ports reliés directement à des terminaux. Il ne doit pas être activé sur un lien où un autre pont est attendu. BPDU Guard protège typiquement un port d’accès configuré PortFast contre la réception de BPDUs. Root Guard et Loop Guard répondent à des scénarios différents et doivent être appliqués selon la conception du réseau : ne les active pas comme des options génériques sans comprendre les conséquences possibles.

Un changement de topologie STP peut modifier les entrées MAC et la distribution du trafic. Pendant une convergence, de la perte de paquets ou une brève interruption peut apparaître. Si le réseau connaît régulièrement des changements inattendus, cherche les liens instables, les ports access recevant des BPDUs, les erreurs de configuration et les équipements ajoutés sans validation.

### 1.8. EtherChannel et LACP : lien logique et membres physiques

Un EtherChannel (ou LAG) agrège des ports physiques compatibles afin qu’ils soient vus comme une interface logique. Le standard IEEE 802.1AX définit les mécanismes d’agrégation de liens ; LACP échange les informations nécessaires à la formation et à la surveillance de l’agrégat. Les implémentations peuvent utiliser des noms de commandes différents.

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 300" width="100%" role="img" aria-label="Deux switches reliés par trois liens physiques regroupés dans un EtherChannel logique"><rect x="1" y="1" width="918" height="298" rx="16" fill="#0b1220" stroke="#26364b"/><style>@keyframes ethernetFlowDash{to{stroke-dashoffset:-34}}.flow{stroke-dasharray:9 8;animation:ethernetFlowDash 2.2s linear infinite}.flow-slow{stroke-dasharray:7 8;animation:ethernetFlowDash 3.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow,.flow-slow{animation:none!important}}</style><defs><marker id="v5cyan" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#45d6f5"/></marker><marker id="v5green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#43d9a3"/></marker><marker id="v5amber" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#f6bd60"/></marker><marker id="v5red" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ff6b76"/></marker></defs><text x="460" y="30" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#f1f5f9">Agrégation de liens : plusieurs membres, un lien logique</text><g font-family="Arial,sans-serif" text-anchor="middle"><rect x="55" y="85" width="185" height="110" rx="12" fill="#17283a" stroke="#45d6f5" stroke-width="2"/><text x="147" y="120" font-size="18" font-weight="700" fill="#eaf8ff">Switch A</text><text x="147" y="145" font-size="12" fill="#a7c6d9">Po1</text><text x="147" y="165" font-size="12" fill="#a7c6d9">LACP active</text><rect x="680" y="85" width="185" height="110" rx="12" fill="#17283a" stroke="#45d6f5" stroke-width="2"/><text x="772" y="120" font-size="18" font-weight="700" fill="#eaf8ff">Switch B</text><text x="772" y="145" font-size="12" fill="#a7c6d9">Po1</text><text x="772" y="165" font-size="12" fill="#a7c6d9">LACP passive/active</text></g><path class="flow" d="M240 111 H672" fill="none" stroke="#43d9a3" stroke-width="3" marker-end="url(#v5green)"/><path class="flow-slow" d="M240 140 H672" fill="none" stroke="#45d6f5" stroke-width="3" marker-end="url(#v5cyan)"/><path class="flow" d="M240 169 H672" fill="none" stroke="#bba4ff" stroke-width="3" marker-end="url(#v5green)"/><text x="460" y="88" font-family="Arial,sans-serif" font-size="12" fill="#a4e7cf" text-anchor="middle">Gi1/0/1</text><text x="460" y="134" font-family="Arial,sans-serif" font-size="12" fill="#a7e8f7" text-anchor="middle">Gi1/0/2</text><text x="460" y="185" font-family="Arial,sans-serif" font-size="12" fill="#d4c9ff" text-anchor="middle">Gi1/0/3</text><rect x="285" y="222" width="350" height="47" rx="9" fill="#123c32" stroke="#43d9a3"/><text x="460" y="242" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#e9fff6" font-weight="700">Port-channel 1 : interface logique</text><text x="460" y="258" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#a4e7cf">Le hachage répartit les flux ; un flux unique n'utilise pas forcément tous les liens.</text></svg></div>

En LACP, `active` initie les échanges et `passive` y répond. Un groupe actif/passif peut se former ; deux extrémités passives ne déclenchent généralement pas la négociation. Les interfaces membres doivent respecter les paramètres compatibles, notamment le mode, la vitesse et les réglages VLAN pour un EtherChannel de couche 2. Vérifie la configuration des deux côtés et les états de chaque membre.

La capacité globale d’un bundle n’est pas identique au débit d’un unique flux. Les commutateurs utilisent généralement un hachage sur des champs de flux tels que les MAC, IP et parfois ports TCP/UDP pour choisir un membre, ce qui préserve souvent l’ordre des paquets. Un seul flux peut donc être limité au débit d’un membre, alors que plusieurs conversations sont réparties sur l’ensemble du bundle. La répartition n’est pas nécessairement égale : plusieurs flux partageant des clés de hachage peuvent emprunter le même membre.

Un agrégat partiellement opérationnel peut masquer une panne. Contrôle la liste des membres et les raisons d’un rejet ou d’une suspension, pas uniquement l’état `up` du Port-channel. Les paramètres du Port-channel et des membres doivent être alignés selon les exigences de la plateforme. STP traite généralement l’agrégat comme un lien logique, pas comme plusieurs liens séparés ; créer deux agrégats incohérents ou connecter les membres à des voisins qui ne constituent pas un système logique compatible peut provoquer des boucles ou de la perte.

Commandes courantes sur IOS/IOS XE :

```cisco
show etherchannel summary
show lacp neighbor
show interfaces port-channel 1
show interfaces status
```

### 1.9. LLDP et découverte des voisins

LLDP (*Link Layer Discovery Protocol*, IEEE 802.1AB) permet à des équipements adjacents d’annoncer certaines informations de voisinage : identifiant de châssis, port, nom système, capacités et, si pris en charge, détails supplémentaires. Cisco CDP remplit une fonction proche dans les environnements compatibles Cisco. Ces protocoles aident à confirmer le câblage logique, les ports connectés et certaines erreurs d’inventaire.

LLDP/CDP n’assure ni le routage ni la connectivité applicative. Un voisin découvert ne prouve pas que les VLAN sont autorisés, que STP transfère ou que le bundle est sain. À l’inverse, l’absence de voisin ne prouve pas une panne physique : le protocole peut être désactivé, filtré, non pris en charge par le terminal ou limité par une politique. N’active pas la découverte sur toutes les interfaces sans politique : elle partage des informations d’infrastructure et doit être maîtrisée.

Commandes usuelles :

```cisco
show lldp neighbors
show lldp neighbors detail
show cdp neighbors
show cdp neighbors detail
```

Sur un lien inter-switch, compare le port local et le port distant, le nom du voisin et le type de capacité. Si la documentation indique que `Gi1/0/48` rejoint `SW-DIST-01 Gi1/0/47`, mais que LLDP signale un autre port ou un autre équipement, l’écart mérite vérification avant toute modification.

### 1.10. QoS de couche 2 : PCP et DEI

Le champ de contrôle du tag 802.1Q inclut trois bits PCP (*Priority Code Point*) utilisés dans de nombreux environnements pour exprimer une classe de priorité de couche 2, et un bit DEI (*Drop Eligible Indicator*) lié à la possibilité de jeter la trame sous congestion selon la politique appliquée. La signification opérationnelle dépend de la configuration QoS et du comportement des équipements.

Le marquage PCP ne garantit pas, à lui seul, qu’un équipement donne effectivement un traitement privilégié. Il faut vérifier la correspondance entre marquages, files de sortie, politiques de planification et limites de bande passante. Une mauvaise confiance accordée aux tags provenant des terminaux peut permettre à un hôte de réclamer une priorité qu’il n’est pas autorisé à obtenir.

Lorsqu’une voix IP souffre de gigue, commence par distinguer problème de réseau de couche 2, congestion, perte, mauvaise négociation ou problème applicatif. Vérifie les compteurs d’erreurs, l’utilisation des interfaces et les politiques QoS plutôt que d’ajouter des priorités partout. La QoS ne crée pas de bande passante ; elle organise le traitement en situation de contention.

### 1.11. Sécurité de port et protections d’accès

Les protections de couche 2 cherchent à réduire les risques d’équipement non autorisé, de boucle accidentelle, d’usurpation d’adresses ou de trafic réseau malveillant. Leur application doit être progressive et accompagnée d’une procédure de réaction, car une politique trop stricte peut couper des équipements légitimes.

- **Port security :** limite ou contrôle les adresses MAC apprises sur un port et applique une action en cas de violation selon le mode choisi.
- **802.1X :** contrôle l’accès au réseau au moyen d’une authentification de port, généralement en coopération avec un serveur RADIUS.
- **DHCP snooping :** distingue les ports de confiance et non confiance pour surveiller les messages DHCP selon la prise en charge de la plateforme.
- **Dynamic ARP Inspection (DAI) :** valide certaines informations ARP en s’appuyant sur des mécanismes de confiance ou des liaisons de contrôle, notamment la base de DHCP snooping si elle est utilisée.
- **IP Source Guard :** limite certains paquets en fonction des associations d’adresses validées, selon les fonctionnalités du commutateur.
- **BPDU Guard :** met en protection un port utilisateur s’il reçoit des BPDUs, lorsqu’il est configuré selon le scénario prévu.

Aucune protection ne doit être activée de manière irréfléchie sur les uplinks. Un port inter-switch peut légitimement transporter plusieurs MAC, des annonces de contrôle et des flux DHCP/ARP provenant de nombreux terminaux. Il faut identifier les ports d’accès et les ports d’infrastructure, choisir les protections qui correspondent à chacun et tester la politique en environnement contrôlé.

### 1.12. Limites des captures et des compteurs

Une capture sur un port miroir (SPAN) ou un TAP peut aider à voir des trames, mais elle n’observe pas nécessairement tout le trafic. Le choix de la source, de la direction, des VLAN et du débit peut entraîner des omissions. Si plusieurs ports sont copiés vers une destination de capture limitée, les paquets peuvent être perdus. Les fonctionnalités d’offload sur les cartes réseau, la présence ou l’absence de FCS et la visibilité des tags VLAN peuvent aussi influencer ce que l’outil affiche.

Une observation à un seul point de capture ne permet pas toujours de dire où une trame a été perdue. Pour localiser le point de défaillance, compare le même flux en amont et en aval du segment suspect, avec des horloges correctement synchronisées si plusieurs appareils sont concernés. Documente le point de capture et son mode de configuration. L’absence de trame dans une capture n’est un indice fort que si l’instrument d’observation est fiable et correctement placé.

## 2. Configuration et pratique

### 2.1. Laboratoire proposé

Construis le laboratoire suivant dans Packet Tracer, GNS3, EVE-NG ou sur du matériel de test. Les noms d’interfaces peuvent varier selon les modèles : adapte-les sans changer l’objectif.

| Équipement | Liaisons | Rôle |
|---|---|---|
| SW1 | PC-A, trunk vers SW2, trunk vers SW3 | Commutateur d’accès principal et racine STP souhaitée |
| SW2 | PC-B, trunk vers SW1, trunk vers SW3 | Commutateur d’accès secondaire |
| SW3 | PC-C, trunk vers SW1, trunk vers SW2 | Commutateur d’accès secondaire |
| PC-A | SW1 access VLAN 10 | Poste service A |
| PC-B | SW2 access VLAN 10 | Poste service A |
| PC-C | SW3 access VLAN 20 | Poste service B |

Le triangle de liens inter-switch permet de vérifier que STP bloque un chemin redondant. Tous les trunks doivent transporter les VLAN réellement nécessaires. Pour le test de connectivité IP, configure les adresses selon le plan de laboratoire et ajoute une fonction de routage si tu veux tester la communication entre VLAN 10 et VLAN 20.

```text
                    SW1 (racine souhaitée)
                    /                   \
             trunk /                     \ trunk
                  /                       \
               SW2 -------- trunk -------- SW3
                |                           |
          PC-B VLAN 10                PC-C VLAN 20

          PC-A VLAN 10 est connecté à SW1.
```

### 2.2. Créer les VLAN et affecter les ports d’accès

Sur chaque commutateur compatible, crée les VLAN requis avant de modifier les ports. Cet exemple ne suppose aucun VTP particulier ; il s’agit d’une configuration locale.

```cisco
configure terminal
vlan 10
 name UTILISATEURS
vlan 20
 name SERVICES
vlan 99
 name ADMIN
vlan 999
 name NATIVE-UNUSED
end
show vlan brief
```

Affecte ensuite les ports terminaux. Remplace les noms d’interfaces par ceux du matériel réellement utilisé.

```cisco
configure terminal
interface GigabitEthernet1/0/10
 description PC-A
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
end
show interfaces GigabitEthernet1/0/10 switchport
show spanning-tree interface GigabitEthernet1/0/10 detail
```

Dans un laboratoire, tu peux activer PortFast et BPDU Guard sur le port dédié au PC. En production, confirme que la prise est réellement une prise terminal et non une liaison vers un commutateur ou un pont. Le comportement de protection et la syntaxe varient selon la plateforme ; après activation, documente comment l’alerte est détectée et comment le port est remis en service après analyse.

### 2.3. Configurer les trunks

Configure explicitement les trunks aux deux extrémités, avec les mêmes VLAN et le même VLAN natif. La configuration suivante est illustrative pour IOS/IOS XE :

```cisco
configure terminal
interface GigabitEthernet1/0/48
 description TRUNK-vers-SW2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,99
 switchport trunk native vlan 999
 switchport nonegotiate
end
```

Le VLAN 999 doit exister si la politique de la plateforme l’exige, et la politique du VLAN natif doit être appliquée de façon cohérente. Certaines plateformes n’acceptent pas la commande `switchport nonegotiate` ou utilisent une syntaxe différente. N’applique pas un bloc copié-collé sans vérifier les capacités de l’équipement et les exigences de maintenance.

Vérifie ensuite :

```cisco
show interfaces trunk
show interfaces GigabitEthernet1/0/48 switchport
show vlan brief
show spanning-tree vlan 10
show spanning-tree vlan 20
```

Résultat attendu : l’interface fonctionne en trunk ; VLAN 10 et 20 sont autorisés ; le VLAN natif correspond au plan ; STP a un rôle/état cohérent. Si l’un des VLAN est absent dans l’état forwarding, traite d’abord cette différence avant de conclure à un problème IP.

### 2.4. Établir la racine STP intentionnelle

Dans un réseau pédagogique, tu peux régler la priorité de SW1 pour le rendre racine. Les commandes exactes dépendent du mode STP. Avec des extensions Cisco compatibles, un exemple de syntaxe est :

```cisco
spanning-tree vlan 10,20 priority 4096
```

Sur des versions qui proposent une macro de commodité, la commande `spanning-tree vlan 10,20 root primary` peut aussi exister. Utilise une méthode prévue par la plateforme et valide le Root ID avec `show spanning-tree vlan 10` et `show spanning-tree vlan 20`. Choisis aussi un chemin de secours en définissant une priorité appropriée sur le commutateur secondaire si la conception le demande.

Ne prends pas les numéros d’exemple comme des valeurs universelles. Le choix de la racine doit refléter la topologie physique et les chemins désirés. Sur des environnements utilisant MST, l’élection se raisonne par instance MST, et la cohérence de la région MST (nom, révision et mappage VLAN-instance) devient importante.

### 2.5. Ajouter un EtherChannel LACP

Si deux commutateurs et le laboratoire disposent d’au moins deux liaisons compatibles, regroupe-les en EtherChannel au lieu de les traiter comme deux trunks indépendants. L’objectif est de vérifier que le Port-channel se forme, que les membres sont cohérents et que STP voit le bundle logique.

```cisco
interface range GigabitEthernet1/0/1-2
 description MEMBRES-PO1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,99
 switchport trunk native vlan 999
 channel-group 1 mode active
!
interface Port-channel1
 description LAG-vers-SW2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,99
 switchport trunk native vlan 999
```

L’ordre de configuration et les paramètres hérités varient selon l’OS ; certains systèmes recommandent de configurer l’interface logique avant les membres. Assure-toi que la configuration est identique aux deux extrémités, notamment les VLAN, le VLAN natif et le mode access/trunk. Ne crée pas de bundle avec des interfaces reliées à des voisins différents, sauf si la solution de multichâssis est explicitement prise en charge et correctement conçue.

Vérification :

```cisco
show etherchannel summary
show lacp neighbor
show interfaces port-channel 1
show spanning-tree vlan 10
```

Si un membre ne rejoint pas le bundle, contrôle les messages système, les paramètres locaux et distants, la vitesse, le mode et les éventuelles limitations de plateforme. Ne force pas `mode on` pour contourner une incohérence sans comprendre le risque : un groupe statique mal aligné peut provoquer des boucles ou un transfert asymétrique.

### 2.6. Collecter les informations de voisinage

Active LLDP uniquement selon la politique et les fonctions disponibles sur l’OS. Sur des appareils Cisco, CDP peut être présent et utile ; sur les réseaux multiconstructeurs, LLDP est souvent mieux adapté à une découverte standardisée.

```cisco
show lldp neighbors
show lldp neighbors detail
show cdp neighbors detail
```

Compare les voisins déclarés aux schémas de câblage. Une différence peut indiquer un brassage incorrect, un commutateur intermédiaire non documenté ou une erreur d’inventaire. La sortie est aussi utile pour associer un port local à un port distant avant une maintenance.

### 2.7. Valider l’apprentissage MAC

Depuis PC-A, génère un trafic vers PC-B du même VLAN. Consulte la table MAC sur le commutateur connecté au poste puis sur les commutateurs intermédiaires. Confirme que chaque adresse est associée au bon VLAN et au bon port ou uplink.

```cisco
show mac address-table dynamic
show mac address-table vlan 10
show mac address-table address 001a.2b3c.4d5e
```

Les entrées exactes dépendent des adresses générées par le laboratoire. Si la MAC source apparaît alternativement sur deux ports, cherche une boucle, un EtherChannel mal formé, un pont de couche 2 ou un changement fréquent de connexion. Si la MAC ne s’apprend jamais, vérifie que le port est connecté et en transfert, que le VLAN d’entrée est correct, et qu’une politique de sécurité n’empêche pas l’apprentissage.

### 2.8. Scénarios de test

Effectue les tests dans cet ordre pour éviter de mélanger plusieurs variables :

1. Vérifier le lien physique et l’état administratif du port.
2. Vérifier le VLAN du port d’accès du terminal.
3. Vérifier la présence du VLAN sur chaque commutateur traversé.
4. Vérifier le trunk et la liste de VLAN autorisés.
5. Vérifier le rôle/état STP pour le VLAN concerné.
6. Vérifier la table MAC et les compteurs d’erreurs.
7. Tester le chemin IP (adresse, masque, passerelle, ARP et routage) si la couche 2 est cohérente.
8. Contrôler DHCP/DNS/application seulement après avoir établi où le trafic peut passer.

Consigne chaque état avant modification. Si tu changes simultanément la liste des VLAN, la priorité STP et LACP, tu ne sauras pas quelle modification a corrigé ou aggravé le problème.

## 3. Dépannage structuré et sécurité

<div class="svg-diagram"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 390" width="100%" role="img" aria-label="Arbre de décision pour diagnostiquer une panne Ethernet couche 2"><rect x="1" y="1" width="918" height="388" rx="16" fill="#0b1220" stroke="#26364b"/><style>@keyframes ethernetFlowDash{to{stroke-dashoffset:-34}}.flow{stroke-dasharray:9 8;animation:ethernetFlowDash 2.2s linear infinite}.flow-slow{stroke-dasharray:7 8;animation:ethernetFlowDash 3.2s linear infinite}@media(prefers-reduced-motion:reduce){.flow,.flow-slow{animation:none!important}}</style><defs><marker id="v6cyan" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#45d6f5"/></marker><marker id="v6green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#43d9a3"/></marker><marker id="v6amber" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#f6bd60"/></marker><marker id="v6red" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ff6b76"/></marker></defs><text x="460" y="30" text-anchor="middle" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#f1f5f9">Diagnostic couche 2 : avancer de l’observation à l’hypothèse</text><g font-family="Arial,sans-serif" text-anchor="middle"><rect x="320" y="52" width="280" height="50" rx="9" fill="#12334a" stroke="#45d6f5"/><text x="460" y="82" font-size="14" font-weight="700" fill="#eaf8ff">1. Lien physique est-il UP ?</text><rect x="40" y="150" width="240" height="65" rx="9" fill="#3b202a" stroke="#ff6b76"/><text x="160" y="177" font-size="14" font-weight="700" fill="#ffe8ec">NON : physique</text><text x="160" y="197" font-size="12" fill="#f0b8c0">Câble, optique, speed/duplex, err-disable</text><rect x="340" y="150" width="240" height="65" rx="9" fill="#123c32" stroke="#43d9a3"/><text x="460" y="177" font-size="14" font-weight="700" fill="#e9fff6">OUI : vérifier VLAN</text><text x="460" y="197" font-size="12" fill="#a4e7cf">Access/trunk, VLAN autorisé, natif</text><rect x="640" y="150" width="240" height="65" rx="9" fill="#30254b" stroke="#bba4ff"/><text x="760" y="177" font-size="14" font-weight="700" fill="#f4efff">Puis : chemin STP</text><text x="760" y="197" font-size="12" fill="#d4c9ff">Rôle/état, BPDU, boucle</text><rect x="210" y="280" width="220" height="65" rx="9" fill="#17283a" stroke="#45d6f5"/><text x="320" y="305" font-size="14" font-weight="700" fill="#eaf8ff">3. Table MAC</text><text x="320" y="326" font-size="12" fill="#a7c6d9">Apprise ? bon port/VLAN ?</text><rect x="490" y="280" width="220" height="65" rx="9" fill="#17283a" stroke="#45d6f5"/><text x="600" y="305" font-size="14" font-weight="700" fill="#eaf8ff">4. Contrôles complémentaires</text><text x="600" y="326" font-size="12" fill="#a7c6d9">LACP, erreurs, sécurité de port</text></g><path d="M390 102 L160 144" fill="none" stroke="#ff6b76" stroke-width="3" marker-end="url(#v6red)"/><text x="260" y="115" font-family="Arial,sans-serif" font-size="12" fill="#ff9ea6">Non</text><path class="flow" d="M460 102 V144" fill="none" stroke="#43d9a3" stroke-width="3" marker-end="url(#v6green)"/><text x="480" y="127" font-family="Arial,sans-serif" font-size="12" fill="#a4e7cf">Oui</text><path d="M580 183 H634" fill="none" stroke="#bba4ff" stroke-width="3" marker-end="url(#v6green)"/><path class="flow" d="M460 215 L320 274" fill="none" stroke="#45d6f5" stroke-width="3" marker-end="url(#v6cyan)"/><path class="flow-slow" d="M760 215 L600 274" fill="none" stroke="#45d6f5" stroke-width="3" marker-end="url(#v6cyan)"/><text x="460" y="370" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#9db0c7">Capture et logs servent à confirmer ou réfuter chaque hypothèse ; ne pas supposer la cause.</text></svg></div>

### 3.1. La machine ne communique pas avec une machine du même VLAN

Procède du plus proche du terminal vers l’amont :

- Confirme l’état physique du port, la vitesse, le duplex et les compteurs d’erreurs.
- Vérifie que le port est access dans le VLAN prévu ou qu’un port trunk du terminal est volontairement configuré de la sorte.
- Vérifie l’existence du VLAN sur le commutateur.
- Vérifie la table MAC pour confirmer que la source du terminal a été apprise sur le bon port et dans le bon VLAN.
- Sur les trunks successifs, confirme le VLAN autorisé et l’état STP forwarding.
- Capture les trames au point adéquat si les observations d’état ne suffisent pas.

Ne conclue pas immédiatement que le câble est défectueux parce que le ping échoue. Une adresse IP erronée, un masque incorrect, l’absence d’ARP, une ACL, un pare-feu hôte ou une panne applicative peut aussi expliquer l’échec. La vérification Ethernet doit être étayée par les tables et les compteurs.

### 3.2. Un VLAN fonctionne localement mais pas entre commutateurs

Cette signature oriente souvent vers les trunks, les listes de VLAN autorisés ou STP. Vérifie les deux extrémités du lien : le mode trunk, le VLAN natif et les VLAN autorisés doivent être compatibles. Confirme que le VLAN apparaît à travers toute la chaîne nécessaire et qu’aucun port de transfert n’est bloqué de façon inattendue. Vérifie aussi que le bon lien physique a été raccordé ; LLDP/CDP et les descriptions d’interfaces aident à repérer les écarts.

Une erreur fréquente consiste à modifier l’affectation d’un port utilisateur alors que le défaut se trouve sur un uplink. Une autre consiste à ajouter le VLAN à un trunk sans le créer ou sans vérifier la propagation sur les commutateurs nécessaires. Le diagnostic doit suivre le chemin exact et noter à chaque saut la présence du VLAN, le rôle STP et l’apprentissage MAC.

### 3.3. Boucle, broadcast storm ou MAC flapping

Les symptômes possibles sont une hausse brutale du trafic broadcast/multicast, une utilisation CPU élevée, des ports instables, des changements de table MAC et une dégradation généralisée. Ces signes ne prouvent pas seuls une boucle ; une tempête peut aussi provenir d’un terminal défectueux ou d’une mauvaise configuration de groupe multicast. Il faut corréler les logs, les compteurs et la topologie.

Actions prudentes :

1. Identifier les ports qui changent de rôle ou génèrent un trafic exceptionnel.
2. Vérifier les logs STP, les BPDUs reçus et les événements de changement de topologie.
3. Contrôler les derniers raccordements ou changements de configuration.
4. Si une boucle est confirmée, isoler le segment fautif selon le plan d’intervention, sans désactiver STP globalement.
5. Confirmer la stabilisation des compteurs et l’apprentissage MAC après correction.
6. Documenter la cause et les protections à ajouter, par exemple BPDU Guard sur les ports d’accès appropriés.

L’isolement d’un port peut interrompre un service critique. En production, applique les procédures d’incident, l’autorité de changement et les exigences de communication. Préserve les informations nécessaires à l’analyse et évite les actions massives non ciblées.

### 3.4. Port placé en err-disabled

Sur certaines plateformes, un port passe en état *err-disabled* lorsque des fonctions de protection détectent une condition considérée dangereuse, par exemple une violation de port-security, la réception d’un BPDU sur un port protégé ou certaines conditions de liaison. Le message système et la raison de l’arrêt sont essentiels : ne réactive pas le port sans savoir pourquoi la protection s’est déclenchée.

Commandes Cisco courantes selon version :

```cisco
show interfaces status err-disabled
show logging
show port-security interface GigabitEthernet1/0/10
show spanning-tree interface GigabitEthernet1/0/10 detail
```

La remise en service peut exiger de corriger la cause, puis de réactiver administrativement l’interface ou d’attendre un mécanisme de récupération configuré. Une récupération automatique n’est pas une correction de cause racine. Si un port reçoit un BPDU inattendu, vérifie le câblage et l’équipement connecté avant de changer la politique BPDU Guard.

### 3.5. Incohérence VLAN natif

Les alertes de VLAN natif ou de mismatch STP sont des indices à prendre au sérieux. Compare les sorties de configuration sur les deux extrémités et vérifie les politiques de tagging. Un VLAN natif différent peut faire classer une trame non taguée dans deux VLAN différents. Le fait que les trames étiquetées continuent de passer ne prouve pas que la configuration est correcte.

La correction doit être planifiée de part et d’autre. Le changement d’un VLAN natif sur un seul côté peut provoquer une interruption ou un comportement imprévisible. Avant l’opération, vérifie que le VLAN cible existe sur les deux appareils, que la liste autorisée et l’état STP sont appropriés et que la fenêtre de changement est adaptée.

### 3.6. EtherChannel ne se forme pas ou n’utilise qu’un membre

Vérifie d’abord la topologie physique : les ports que tu veux agréger doivent joindre le système partenaire prévu. Puis compare les paramètres : mode LACP, vitesse, duplex, type de port, VLAN access/trunk, VLAN natif, VLAN autorisés et MTU lorsque la plateforme l’exige. Utilise `show etherchannel summary` et les informations de voisin LACP pour comprendre quels membres sont réellement synchronisés et en transfert.

Si le Port-channel est opérationnel mais un membre reste suspendu, ne traite pas l’état global comme preuve que tous les liens sont corrects. L’agrégat peut fonctionner avec capacité réduite. Analyse aussi la distribution des flux : un seul flux peut utiliser un seul membre à cause du hachage ; cela n’indique pas à lui seul une panne.

### 3.7. Perte de paquets malgré un lien UP

Un lien physiquement actif ne garantit pas la livraison sans perte. Consulte les compteurs d’erreurs, drops, overruns, erreurs CRC, pauses, files d’attente et les statistiques de l’interface distante. Les noms des compteurs dépendent de la plateforme. Compare leur évolution sur une période définie : un compteur historique élevé peut ne plus refléter le problème courant.

Vérifie également les asymétries de vitesse, la qualité des optiques, le type de fibre, les niveaux de puissance pour les liens optiques, le câblage et le MTU. Les trames trop grandes peuvent être rejetées sur un segment dont la prise en charge du jumbo frame est incohérente. Un compteur d’erreurs CRC croissant oriente vers un problème de couche physique ou de signal, tandis qu’une hausse de drops en sortie peut indiquer une congestion ou une capacité de file insuffisante.

### 3.8. Procédure de dépannage recommandée

<ol><li><b>Définir le symptôme :</b> quels terminaux, quel VLAN, quelle période, quel service ?</li><li><b>Délimiter le périmètre :</b> un terminal, un port, un switch, un VLAN ou plusieurs segments ?</li><li><b>Geler les preuves :</b> sorties de commandes, journaux, configuration pertinente et heure.</li><li><b>Vérifier physique et état :</b> lien, erreurs, err-disable, voisinage et éventuels membres LAG.</li><li><b>Vérifier le plan de couche 2 :</b> access/trunk, VLAN autorisés/natif, table MAC et STP.</li><li><b>Tester une hypothèse à la fois :</b> contrôle ciblé puis observation avant/après.</li><li><b>Évaluer le changement :</b> impact, retour arrière, validation avec l’utilisateur.</li><li><b>Documenter :</b> cause démontrée, éléments de preuve, solution et actions préventives.</li></ol>

### 3.9. Tableau rapide de symptômes

| Symptôme | Première hypothèse à tester | Vérifications utiles | Attention |
|---|---|---|---|
| Un terminal seul est isolé | Port, VLAN access ou sécurité | `show interfaces status`, `show vlan brief`, logs | Vérifier aussi IP/pare-feu du terminal |
| VLAN disponible sur un switch seulement | Trunk ou base VLAN | `show interfaces trunk`, `show vlan brief` | Ne pas confondre VLAN absent et VLAN non autorisé |
| MAC qui change de port en boucle | Boucle, LAG ou pont inattendu | logs, table MAC, STP, LACP | Corroborer avec topologie et compteurs |
| Port en err-disabled | Protection déclenchée | `show logging`, statut sécurité, STP | Ne pas réactiver sans analyser la cause |
| Un trunk transporte certains VLAN seulement | Liste autorisée, native ou STP | trunk aux deux extrémités et STP par VLAN | Vérifier chaque VLAN concerné |
| Bundle avec un seul membre actif | Incompatibilité LACP ou physique | résumé EtherChannel, voisins, logs | Capacité et redondance réduites |
| CRC en hausse | Câble, optique, signal | compteurs locaux et distants, niveaux optiques | Distinguer erreurs physiques des drops congestion |
| Débit global faible | Hachage, congestion ou membre manquant | statistiques LAG, files QoS, flux | Un seul flux ne somme pas forcément les débits membres |

### 3.10. Changements sûrs et rollback

Avant une modification, identifie le propriétaire du service, la portée possible, les dépendances, la fenêtre et les critères de succès. Sauvegarde les configurations et les états utiles. Pour un trunk, note les VLAN actuellement autorisés, le VLAN natif et l’état STP. Pour un EtherChannel, sauvegarde la configuration des membres, le mode LACP et l’état opérationnel. Pour STP, note le Root ID et le rôle de chaque uplink.

Déploie une modification à la fois. Utilise un changement de faible portée lorsque possible, puis contrôle les résultats. Les critères de succès doivent être mesurables : VLAN présent sur tous les sauts requis, MAC apprise sur le bon port, STP stable, membres LACP synchronisés, absence de hausse d’erreurs et tests de connectivité réussis. Si le résultat s’écarte du plan, restaure la configuration précédente selon la procédure approuvée plutôt que d’empiler des corrections improvisées.

## 4. Ateliers et exercices

### Atelier 1 — Un VLAN ne traverse pas le trunk

**Situation :** PC-A et PC-B appartiennent tous deux au VLAN 10. Ils communiquent quand ils sont connectés au même commutateur, mais pas lorsqu’ils sont sur deux commutateurs différents. Le VLAN 10 existe sur les deux appareils.

**Démarche :**

1. Confirmer que les ports des PC sont en access VLAN 10.
2. Vérifier que le trunk entre les commutateurs est UP.
3. Comparer la liste VLAN autorisée aux deux extrémités.
4. Vérifier la présence du VLAN 10 dans l’état de transfert STP.
5. Générer du trafic et vérifier que les MAC sources sont apprises sur les ports attendus.

**Cause pédagogique possible :** le VLAN 10 existe, mais a été oublié dans la liste autorisée du trunk. La correction doit être appliquée de façon cohérente et validée aux deux extrémités si nécessaire. N’ajoute pas toutes les plages VLAN sans raison : la liste doit respecter le plan de segmentation.

### Atelier 2 — Un lien redondant est bloqué

**Situation :** deux switches sont raccordés par deux chemins distincts. L’un des liens est en état alternatif/bloqué et aucun trafic utilisateur ne le traverse.

**Questions :**

1. Est-ce forcément une panne ?
2. Quel Root ID voit chaque commutateur ?
3. Quel port est root, designated ou alternate ?
4. Les liens pourraient-ils être regroupés en EtherChannel si les deux extrémités et le câblage le permettent ?

**Correction attendue :** un port bloqué par STP peut être le comportement correct dans une topologie avec liens redondants. Si l’intention est d’utiliser plusieurs liens en parallèle, un EtherChannel compatible peut présenter les membres comme un lien logique. Il ne faut pas désactiver STP simplement pour faire passer du trafic sur le lien bloqué.

### Atelier 3 — Une interface tombe en err-disabled

**Situation :** juste après qu’un petit switch non documenté a été branché sur une prise utilisateur, le port d’accès passe en err-disabled avec un événement lié à BPDU Guard.

**Correction attendue :** la protection a détecté une trame BPDU inattendue. Il faut confirmer le câblage, identifier le matériel connecté et comprendre pourquoi un pont est présent sur une prise terminal. Après validation et correction de la topologie, le port peut être remis en service selon la procédure. Désactiver BPDU Guard sans comprendre l’événement supprime la protection sans résoudre le défaut.

### Atelier 4 — Le Port-channel est up mais un membre est suspendu

**Situation :** un agrégat LACP dispose de deux liens physiques, mais un seul membre est utilisé. Le trafic passe encore, avec une capacité inférieure à celle attendue.

**Correction attendue :** comparer les paramètres des deux extrémités sur le membre rejeté, lire les logs et la sortie LACP. Vérifier vitesse, duplex, mode, VLAN, MTU et voisinage physique. Puis confirmer que les deux membres sont bien synchronisés, en collecte et en distribution lorsque la plateforme expose ces états. Ne pas conclure à un hachage déséquilibré avant d’avoir confirmé l’état de tous les membres.

### Atelier 5 — Des CRC augmentent sur un uplink

**Situation :** les utilisateurs signalent des microcoupures ; l’interface est UP, mais les compteurs CRC croissent pendant la période d’incident.

**Correction attendue :** vérifier les deux extrémités, les câbles ou optiques, la propreté des connecteurs, les niveaux optiques lorsque disponibles, la compatibilité transceiver et les erreurs de ports. Comparer les compteurs avant/après un test. Une interface UP signifie que la couche physique a établi un lien, pas que toutes les trames sont reçues sans erreur.

### Quiz de validation

1. Quelle information un switch utilise-t-il pour apprendre une entrée MAC dynamique ?
2. Dans quel cas une trame unicast est-elle généralement floodée dans un VLAN ?
3. Pourquoi un trunk ne garantit-il pas à lui seul la connectivité d’un VLAN ?
4. Quel est le risque d’un VLAN natif incohérent ?
5. Pourquoi STP peut-il bloquer un lien physiquement UP ?
6. Quelle différence existe entre le rôle STP et l’état de transfert du port ?
7. Que négocie LACP et pourquoi faut-il vérifier les membres ?
8. Pourquoi un seul flux ne bénéficie-t-il pas forcément de la somme des débits d’un EtherChannel ?
9. Que prouve la présence d’un voisin LLDP ? Et que ne prouve-t-elle pas ?
10. Quel est le premier réflexe lorsqu’un port passe en err-disabled ?

### Corrigé synthétique

1. L’adresse MAC source de la trame reçue, associée au VLAN et au port d’entrée.
2. Lorsque la MAC de destination n’est pas présente dans la table pour ce VLAN, sous réserve des politiques applicables.
3. Le VLAN doit exister/être actif, être autorisé, être en transfert STP et être cohérent tout le long du chemin.
4. Une même trame non taguée peut être classée dans des VLAN différents aux deux extrémités, avec des effets fonctionnels et de sécurité.
5. Pour empêcher une boucle de couche 2 dans une topologie redondante.
6. Le rôle décrit la fonction du port dans l’arbre ; l’état indique s’il transmet effectivement des trames utilisateur.
7. LACP échange des informations de partenaire et d’état pour former/surveiller l’agrégat ; chaque membre doit être compatible et opérationnel.
8. Le hachage choisit généralement un membre pour un flux afin de limiter la réorganisation des paquets.
9. Il indique qu’un voisin annonce sa présence sur la liaison ; il ne prouve pas que VLAN, STP ou services applicatifs sont correctement configurés.
10. Lire les logs et identifier la cause de la protection avant de remettre le port en service.

## 5. Checklist d’exploitation

### Chaque jour ou lors d’une alerte

- [ ] Vérifier l’état des uplinks et les transitions de lien récentes.
- [ ] Lire les logs STP, LACP et err-disable pertinents.
- [ ] Surveiller les erreurs CRC, drops, changements de MAC et taux de broadcast anormaux.
- [ ] Confirmer que les voisins LLDP/CDP correspondent au plan de câblage.
- [ ] Vérifier l’état des Port-channels critiques et le nombre de membres actifs.

### Avant un changement de couche 2

- [ ] Sauvegarder la configuration et les sorties d’état utiles.
- [ ] Confirmer les VLAN utilisés par le service et les VLAN autorisés sur chaque trunk.
- [ ] Comparer VLAN natif et mode trunk des deux côtés.
- [ ] Vérifier Root ID, coût, rôle et état STP concernés.
- [ ] Vérifier les membres LACP et la compatibilité du matériel.
- [ ] Définir un plan de test, une fenêtre, une communication et un rollback.

### Après le changement

- [ ] Confirmer la stabilité physique, l’absence de nouvelles erreurs et les états de lien.
- [ ] Confirmer les tables MAC, VLAN, STP et LACP attendues.
- [ ] Tester la connectivité depuis les terminaux représentatifs.
- [ ] Observer le réseau pendant une période adaptée à l’impact.
- [ ] Enregistrer les modifications, résultats et écarts dans le journal de changement.

## Points à retenir

- Un commutateur apprend les MAC à partir des trames reçues et limite le forwarding au VLAN associé.
- Une trame à destination inconnue est souvent floodée dans le même VLAN, pas dans tous les VLAN.
- Le port access et le trunk ont des rôles différents ; 802.1Q étiquette les trames transportées sur un trunk.
- La présence du VLAN, la liste autorisée, le VLAN natif et l’état STP doivent être vérifiés séparément.
- STP bloque parfois un lien de façon volontaire pour prévenir les boucles ; ne le désactive pas pour contourner un symptôme.
- LACP forme et surveille une agrégation, mais ne dispense pas de vérifier la cohérence des membres et les limites de hachage.
- LLDP aide à identifier les voisins ; il ne garantit pas le transfert de données.
- Les fonctions de sécurité de couche 2 sont utiles si les ports, les rôles de confiance et les procédures de récupération sont conçus avec soin.
- Pour dépanner, collecte d’abord les preuves, teste une hypothèse à la fois et vérifie les résultats après chaque changement.

## Références techniques

- [IEEE 802.1Q — Virtual LANs et bridges](https://www.ieee802.org/1/pages/802.1Q.html)
- [IEEE 802.1 — familles de standards LAN](https://1.ieee802.org/)
- [Cisco — Guide de configuration des trunks VLAN (IOS XE)](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vlan-trunks.html)
- [Cisco — Guide de configuration STP (IOS XE)](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/stp/stp-configuration-guide/m-stp.html)
- [Wireshark — Référence du filtre d’affichage VLAN 802.1Q](https://www.wireshark.org/docs/dfref/v/vlan.html)
- [IEEE 802.1AX — Link Aggregation](https://1.ieee802.org/tsn/802-1ax-rev/)

> **Note de compatibilité :** les exemples Cisco sont pédagogiques. Vérifie toujours la syntaxe, les valeurs par défaut, les capacités de la plateforme et les conditions de support dans la documentation correspondant à ton modèle et à sa version logicielle avant une mise en production.
