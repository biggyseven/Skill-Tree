# VRF — Niveau Intermédiaire

> **Parcours :** Réseaux et routage · **Niveau :** Intermédiaire · **Fichier :** `vrf-intermediaire.md`

## Objectifs pédagogiques

À la fin de ce cours, tu sauras concevoir plusieurs contextes VRF sur un routeur ou un commutateur L3, analyser la séparation RIB/FIB, déployer des routes statiques et des protocoles par VRF, utiliser RD et RT dans un service MPLS L3VPN, planifier un route leaking contrôlé et diagnostiquer les pannes de bout en bout. Le cours suppose que les notions de base VRF, interfaces L3, routage statique et distinction VRF-Lite/MPLS L3VPN sont déjà connues.

## Prérequis et conventions

Prérequis : `vrf-debutant.md`, adressage IPv4/IPv6, VLAN/SVI, routes statiques, bases OSPF/BGP et lecture de la table de routage. Les commandes sont des exemples pédagogiques proches de Cisco IOS XE ; la syntaxe diffère selon IOS XE, IOS XR, NX-OS, le modèle, la version et les fonctions activées. Vérifier les guides de la plateforme avant tout changement. Les adresses `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` sont réservées à la documentation.

## Plan du cours

1. Reconcevoir les domaines VRF
2. RIB, FIB et lookup déterministe
3. Interfaces, SVI et sous-interfaces
4. Routes statiques, route par défaut et next-hop
5. Protocoles dynamiques par VRF
6. Route leaking sûr : modèles et risques
7. RD, RT et MPLS L3VPN
8. MP-BGP VPNv4/VPNv6 et labels
9. IPv6 dans les VRF
10. Services VRF-aware
11. Redondance, convergence et échelle
12. Sécurité et gouvernance
13. Méthode de dépannage
14. Laboratoire multi-VRF
15. Études de cas et quiz
16. Checklist, glossaire et références

## 1. Reconcevoir les domaines VRF

Au niveau intermédiaire, une VRF ne se limite plus à la création d’une table séparée. Il faut définir un **modèle opérationnel** : qui possède chaque domaine, quelles interfaces y appartiennent, quelles routes entrent et sortent, quels services sont partagés et quels flux sont interdits. Une VRF bien conçue réduit les ambiguïtés. Une VRF mal conçue peut, au contraire, cacher des dépendances implicites qui compliquent le dépannage.

### 1.1 Construire une matrice de domaines

Avant la configuration, établir une matrice avec pour chaque VRF : nom, objectif, équipes responsables, interfaces, préfixes, protocoles, services autorisés, politique d’accès aux autres domaines, supervision et plan de reprise. Éviter les noms vagues comme `VRF1` dans une production : préférer une nomenclature stable telle que `CORP-USERS`, `SHARED-SVC`, `OOB-MGMT` ou `PARTNER-ACME`.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Cartographie des domaines VRF"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Cartographie des domaines VRF</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">La séparation doit être cohérente entre interfaces, routes, services et politiques.</text><line x1="224" y1="170" x2="385" y2="170" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="385.0,170.0 375.0,164.2 375.0,175.8" fill="#37d6c1"/><rect x="264.2" y="140.0" width="81.5" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="305.0" y="155.0" fill="#37d6c1" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">DNS ciblé</text><line x1="224" y1="295" x2="385" y2="205" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="385.0,205.0 373.4,204.8 379.1,214.9" fill="#c3a1ff"/><rect x="276.8" y="234.0" width="66.5" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="310.0" y="249.0" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">service</text><line x1="575" y1="170" x2="735" y2="170" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="735.0,170.0 725.0,164.2 725.0,175.8" fill="#ffbd59"/><rect x="596.5" y="140.0" width="119.0" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="656.0" y="155.0" fill="#ffbd59" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">administration</text><line x1="575" y1="205" x2="735" y2="285" stroke="#ff7185" stroke-width="3" stroke-linecap="round"/><polygon points="735.0,285.0 728.6,275.3 723.5,285.7" fill="#ff7185"/><rect x="592.8" y="220.0" width="126.5" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="656.0" y="235.0" fill="#ff7185" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">règle explicite</text><rect x="34" y="132" width="190" height="104" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="34" y="132" width="7" height="104" rx="3" fill="#37d6c1"/><text x="52" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF USERS</text><text x="52" y="179" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Postes et Wi-Fi</text><text x="52" y="198" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Routes utilisateurs</text><rect x="34" y="255" width="190" height="92" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="34" y="255" width="7" height="92" rx="3" fill="#c3a1ff"/><text x="52" y="280" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF SERVERS</text><text x="52" y="302" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Applications internes</text><rect x="385" y="132" width="190" height="104" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="385" y="132" width="7" height="104" rx="3" fill="#ffbd59"/><text x="403" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF SHARED</text><text x="403" y="179" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">DNS · DHCP · NTP</text><text x="403" y="198" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Accès contrôlé</text><rect x="735" y="132" width="190" height="104" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="735" y="132" width="7" height="104" rx="3" fill="#4ea3ff"/><text x="753" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF MGMT</text><text x="753" y="179" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">SSH · SNMP · AAA</text><text x="753" y="198" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Plan de gestion</text><rect x="735" y="255" width="190" height="92" rx="13" fill="#33202b" stroke="#ff7185" stroke-width="2"/><rect x="735" y="255" width="7" height="92" rx="3" fill="#ff7185"/><text x="753" y="280" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF PARTNER</text><text x="753" y="302" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Flux fournisseurs</text></svg>


### 1.2 Isoler n’est pas autoriser

Une VRF sépare les décisions de routage ; elle n’est pas un pare-feu complet. Les ACL, le pare-feu, uRPF, les politiques de contrôle de plan et les règles d’administration restent nécessaires selon le risque. De même, le route leaking ne doit pas devenir un raccourci non documenté. Établir les flux requis, par exemple utilisateurs vers DNS, clients vers application, ou administration vers équipements, puis appliquer le principe du moindre privilège.

## 2. RIB, FIB et lookup déterministe

La RIB conserve les routes apprises et candidates ; la FIB contient les informations qui guident le transfert. Pour une destination, l’équipement choisit le préfixe le plus spécifique dans le contexte VRF associé au paquet. Le next-hop doit ensuite être résolu et l’adjacence de sortie disponible. Une route présente dans la RIB n’assure donc pas à elle seule que le trafic passera : vérifier l’installation FIB, la résolution du next-hop, les ACL et l’état de l’interface.

### 2.1 Le contexte d’entrée fait partie du diagnostic

Quand un paquet arrive sur une interface L3 liée à `CORP-USERS`, la recherche doit utiliser cette VRF. Une route identique dans la table globale ou dans `PARTNER-ACME` ne satisfait pas automatiquement la recherche. Les commandes de test doivent elles aussi préciser le contexte lorsqu’elles sont VRF-aware. Une requête ping globale qui échoue n’est pas une preuve qu’une destination est injoignable depuis chaque VRF ; une requête lancée depuis la mauvaise VRF peut échouer alors que le chemin voulu est sain.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Lookup dans le bon contexte VRF"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Lookup dans le bon contexte VRF</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">Le contexte d’entrée choisit la table ; une fuite de routes doit être explicite.</text><line x1="225" y1="207" x2="300" y2="207" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="300.0,207.0 290.0,201.2 290.0,212.8" fill="#37d6c1"/><line x1="490" y1="207" x2="565" y2="207" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="565.0,207.0 555.0,201.2 555.0,212.8" fill="#4ea3ff"/><line x1="735" y1="207" x2="785" y2="207" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="785.0,207.0 775.0,201.2 775.0,212.8" fill="#ffbd59"/><line x1="395" y1="260" x2="395" y2="280" stroke="#ff7185" stroke-width="3" stroke-linecap="round"/><polygon points="395.0,280.0 400.8,270.0 389.2,270.0" fill="#ff7185"/><rect x="398.0" y="261.0" width="104.0" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="450.0" y="276.0" fill="#ff7185" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">pas de fuite</text><rect x="35" y="155" width="190" height="105" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="35" y="155" width="7" height="105" rx="3" fill="#37d6c1"/><text x="53" y="180" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Paquet entrant</text><text x="53" y="202" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Interface Gi0/1</text><text x="53" y="221" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">VRF CLIENT-A</text><rect x="300" y="155" width="190" height="105" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="300" y="155" width="7" height="105" rx="3" fill="#4ea3ff"/><text x="318" y="180" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">RIB CLIENT-A</text><text x="318" y="202" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Recherche du préfixe</text><text x="318" y="221" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Longest-prefix match</text><rect x="565" y="155" width="170" height="105" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="565" y="155" width="7" height="105" rx="3" fill="#ffbd59"/><text x="583" y="180" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">FIB CLIENT-A</text><text x="583" y="202" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Next-hop résolu</text><text x="583" y="221" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Adjacence de sortie</text><rect x="785" y="155" width="140" height="105" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="785" y="155" width="7" height="105" rx="3" fill="#c3a1ff"/><text x="803" y="180" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Sortie</text><text x="803" y="202" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Interface / tunnel</text><rect x="300" y="280" width="190" height="70" rx="13" fill="#33202b" stroke="#ff7185" stroke-width="2"/><rect x="300" y="280" width="7" height="70" rx="3" fill="#ff7185"/><text x="318" y="305" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF CLIENT-B</text><text x="318" y="327" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Non consultée sans policy</text></svg>


### 2.2 Diagnostic RIB puis FIB

Procédure recommandée :

1. confirmer le nom de VRF et l’interface d’entrée ;
2. vérifier le préfixe, la longueur du masque et la route retenue ;
3. vérifier le next-hop et sa résolution dans le même contexte ;
4. examiner la FIB/CEF si la plateforme expose cette vue ;
5. vérifier l’ACL, le pare-feu, le NAT ou les politiques de service ;
6. tester le chemin aller **et** le retour.

## 3. Interfaces, SVI et sous-interfaces

Une interface L3 ou SVI appartient à un contexte de routage à la fois dans les modèles IOS XE VRF-Lite classiques. Un VLAN est une segmentation de couche 2 ; la VRF intervient au niveau L3, au moment du routage. Plusieurs VLAN d’un même domaine peuvent utiliser la même VRF, mais un design avec plusieurs domaines de sécurité doit justifier les points de passage entre eux.

### 3.1 Exemple d’interface routée

```text
vrf definition CORP-USERS
 address-family ipv4
 exit-address-family
!
interface GigabitEthernet0/1
 description Uplink vers le réseau utilisateurs
 vrf forwarding CORP-USERS
 ip address 192.0.2.1 255.255.255.252
 no shutdown
```

Sur de nombreuses versions IOS XE, `vrf forwarding` appliqué à une interface peut retirer l’adresse IP déjà configurée. Appliquer d’abord la VRF puis reconfigurer l’adresse, et prévoir une fenêtre de changement si l’interface est en service. Vérifier la syntaxe précise de la plateforme.

### 3.2 SVI et sous-interface dot1Q

```text
interface Vlan110
 description Passerelle du VLAN 110
 vrf forwarding CORP-USERS
 ip address 192.0.2.65 255.255.255.192
 no shutdown
!
interface GigabitEthernet0/0.210
 encapsulation dot1Q 210
 vrf forwarding PARTNER-ACME
 ip address 198.51.100.1 255.255.255.252
```

Les prérequis VLAN, trunk, SVI et sous-interface varient suivant le matériel. Vérifier qu’un SVI est opérationnel, que le VLAN existe et qu’un port est actif dans le VLAN quand la plateforme l’exige. Une configuration L3 correcte ne compense pas un VLAN absent ou un trunk qui ne transporte pas le tag voulu.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Préfixes qui se chevauchent entre clients"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Préfixes qui se chevauchent entre clients</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">L’isolation permet de réutiliser les mêmes adresses privées dans des contextes différents.</text><line x1="285" y1="180" x2="365" y2="180" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="365.0,180.0 355.0,174.2 355.0,185.8" fill="#37d6c1"/><line x1="675" y1="180" x2="585" y2="180" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="585.0,180.0 595.0,185.8 595.0,174.2" fill="#c3a1ff"/><line x1="475" y1="232" x2="475" y2="267" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="475.0,267.0 480.8,257.0 469.2,257.0" fill="#ffbd59"/><rect x="40" y="127" width="245" height="105" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="40" y="127" width="7" height="105" rx="3" fill="#37d6c1"/><text x="58" y="152" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">CE client A</text><text x="58" y="174" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">10.10.0.0/16</text><text x="58" y="193" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Hôte 10.10.1.10</text><rect x="365" y="127" width="220" height="105" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="365" y="127" width="7" height="105" rx="3" fill="#4ea3ff"/><text x="383" y="152" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">PE / routeur L3</text><text x="383" y="174" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">VRF A et VRF B</text><text x="383" y="193" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Deux RIB distinctes</text><rect x="675" y="127" width="245" height="105" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="675" y="127" width="7" height="105" rx="3" fill="#c3a1ff"/><text x="693" y="152" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">CE client B</text><text x="693" y="174" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">10.10.0.0/16</text><text x="693" y="193" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Autre espace logique</text><rect x="365" y="267" width="220" height="78" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="365" y="267" width="7" height="78" rx="3" fill="#ffbd59"/><text x="383" y="292" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Règle clé</text><text x="383" y="314" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Aucun partage implicite</text></svg>


## 4. Routes statiques, route par défaut et next-hop

### 4.1 Route spécifique

```text
ip route vrf CORP-USERS 203.0.113.0 255.255.255.0 192.0.2.2
```

Le next-hop `192.0.2.2` doit être joignable dans `CORP-USERS`. Si la route de résolution manque, la route statique peut ne pas être installée comme prévu. Éviter d’utiliser une interface de sortie seule sur des segments Ethernet multi-accès sans comprendre les implications ARP et le comportement du système.

### 4.2 Route par défaut et résilience

Une route par défaut dans une VRF est une décision d’architecture : elle peut envoyer tout trafic inconnu vers un pare-feu, un PE, un WAN ou un service central. Documenter le point de sortie, les routes plus spécifiques, la condition de retrait de la route et le comportement en cas de panne. Une route statique permanente vers un équipement indisponible peut créer un blackhole ; suivre le next-hop ou employer un protocole dynamique lorsque c’est approprié et pris en charge.

### 4.3 Récursion et chemins asymétriques

Le routeur doit pouvoir résoudre la route vers le next-hop au sein du bon contexte. Une route vers un next-hop qui dépend elle-même d’une route issue d’un leak mal pensé peut générer des comportements inattendus. L’asymétrie n’est pas toujours une panne de routage, mais elle peut casser un pare-feu à état, le NAT ou des services liés à une session. Tester les deux sens et inspecter les journaux de l’équipement de sécurité.

## 5. Protocoles dynamiques par VRF

Une instance OSPF, EIGRP ou BGP doit être configurée pour le contexte et l’adresse-family concernés. La forme exacte varie : certains OS proposent `router ospf <id> vrf <name>`, d’autres des sous-sections `address-family ... vrf <name>`. Ne pas copier une syntaxe IOS XE sur IOS XR ou NX-OS sans adaptation.

### 5.1 OSPF dans une VRF

Points à vérifier : identifiant de processus, interfaces actives, area, type réseau, timers, authentification, MTU, filtrage, redistribution et règles spéciales de la plate-forme. Les commandes `show ip ospf neighbor` globales peuvent ne pas montrer les voisins attendus selon l’OS ou la syntaxe. Vérifier l’instance VRF concernée et confirmer que les routes sont installées dans la bonne RIB.

### 5.2 BGP par VRF

BGP peut échanger des routes IPv4/IPv6 dans une VRF en fonction du rôle CE-PE et des capacités du système. Les politiques d’import/export doivent contrôler les préfixes et attributs. Dans une L3VPN de fournisseur, MP-BGP transporte des routes VPNv4/VPNv6 avec des RT et des RD ; ce n’est pas la même chose qu’un simple voisin eBGP IPv4 entre un CE et un PE.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Route leaking : échange contrôlé"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Route leaking : échange contrôlé</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">L’import/export de routes doit être limité par une politique lisible et testée.</text><line x1="260" y1="198" x2="355" y2="198" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="355.0,198.0 345.0,192.2 345.0,203.8" fill="#37d6c1"/><rect x="236.2" y="168.0" width="141.5" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="307.0" y="183.0" fill="#37d6c1" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">routes candidates</text><line x1="590" y1="198" x2="685" y2="198" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="685.0,198.0 675.0,192.2 675.0,203.8" fill="#c3a1ff"/><rect x="570.0" y="168.0" width="134.0" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="637.0" y="183.0" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">routes acceptées</text><line x1="472" y1="250" x2="472" y2="280" stroke="#ff7185" stroke-width="3" stroke-linecap="round"/><polygon points="472.0,280.0 477.8,270.0 466.2,270.0" fill="#ff7185"/><rect x="40" y="145" width="220" height="105" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="40" y="145" width="7" height="105" rx="3" fill="#37d6c1"/><text x="58" y="170" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF USERS</text><text x="58" y="192" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Routes sources</text><text x="58" y="211" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Préfixes autorisés</text><rect x="355" y="145" width="235" height="105" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="355" y="145" width="7" height="105" rx="3" fill="#ffbd59"/><text x="373" y="170" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Politique de leak</text><text x="373" y="192" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Prefix-list / route-map</text><text x="373" y="211" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Import-export ciblé</text><rect x="685" y="145" width="235" height="105" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="685" y="145" width="7" height="105" rx="3" fill="#c3a1ff"/><text x="703" y="170" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF SHARED</text><text x="703" y="192" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">DNS / NTP ciblés</text><text x="703" y="211" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Retour contrôlé</text><rect x="355" y="280" width="235" height="65" rx="13" fill="#33202b" stroke="#ff7185" stroke-width="2"/><rect x="355" y="280" width="7" height="65" rx="3" fill="#ff7185"/><text x="373" y="305" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Contrôles</text><text x="373" y="327" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Anti-boucle · journalisation</text></svg>


### 5.3 Redistribution sans boucle

La redistribution réciproque entre protocoles ou VRF nécessite une politique explicite, des filtres, éventuellement des tags ou communautés et un plan de prévention des boucles. Ne pas redistribuer toutes les routes par défaut sans audit. Valider les préfixes attendus, la source, la préférence et la façon dont la route revient vers son domaine d’origine. Lors d’un changement, contrôler également les agrégats : un résumé trop large peut attirer du trafic vers un domaine qui ne possède pas les destinations réellement actives.

## 6. Route leaking sûr : modèles et risques

Le *route leaking* rend certaines routes d’une VRF visibles dans une autre. Il peut être statique, fondé sur des mécanismes import/export avec politiques, ou appuyé sur BGP et des route-targets suivant l’architecture. Le mécanisme exact dépend de l’OS et de la fonction déployée. Importer une route n’implique pas forcément que le trafic est autorisé par le pare-feu, ni que le retour est correctement routé.

### 6.1 Modèles courants

- **VRF utilisateurs vers services partagés :** seulement les préfixes DNS, DHCP relay, NTP ou applications nécessaires.
- **Hub-and-spoke :** un domaine centralise certains flux ; empêcher les spokes de communiquer directement si ce n’est pas requis.
- **VRF d’administration :** accès initié depuis un poste d’exploitation contrôlé, pas de management ouvert depuis les réseaux utilisateurs.
- **Interconnexion de partenaires :** filtres étroits, contrôle des préfixes, pas d’importation générale des routes du partenaire.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="VRF-Lite et MPLS L3VPN"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">VRF-Lite et MPLS L3VPN</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">VRF-Lite isole localement ; MPLS L3VPN transporte les routes entre PE via un cœur fournisseur.</text><line x1="300" y1="178" x2="365" y2="178" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="365.0,178.0 355.0,172.2 355.0,183.8" fill="#37d6c1"/><line x1="585" y1="178" x2="650" y2="178" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="650.0,178.0 640.0,172.2 640.0,183.8" fill="#4ea3ff"/><line x1="475" y1="225" x2="475" y2="270" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="475.0,270.0 480.8,260.0 469.2,260.0" fill="#ffbd59"/><rect x="40" y="130" width="260" height="95" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="40" y="130" width="7" height="95" rx="3" fill="#37d6c1"/><text x="58" y="155" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF-Lite</text><text x="58" y="177" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">VRF sur un ou plusieurs</text><text x="58" y="196" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">équipements connectés</text><rect x="365" y="130" width="220" height="95" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="365" y="130" width="7" height="95" rx="3" fill="#4ea3ff"/><text x="383" y="155" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">MPLS L3VPN</text><text x="383" y="177" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">PE + cœur MPLS</text><text x="383" y="196" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">MP-BGP VPNv4/v6</text><rect x="650" y="130" width="270" height="95" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="650" y="130" width="7" height="95" rx="3" fill="#c3a1ff"/><text x="668" y="155" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Services client</text><text x="668" y="177" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Sites séparés</text><text x="668" y="196" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Adressage éventuellement chevauchant</text><rect x="365" y="270" width="220" height="72" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="365" y="270" width="7" height="72" rx="3" fill="#ffbd59"/><text x="383" y="295" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">À retenir</text><text x="383" y="317" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">VRF ≠ transport MPLS</text></svg>


### 6.2 Route leaking statique ou dynamique

Une route statique pointant vers une passerelle de services est simple, mais exige la gestion du retour et de la disponibilité. Les mécanismes dynamiques offrent davantage de contrôle à l’échelle, mais peuvent étendre le domaine d’erreur si les filtres sont incorrects. Pour chaque leak, consigner : source, destination, route(s), next-hop, chemin retour, filtre, propriétaire et test de retrait.

### 6.3 Éviter les boucles de routes

Un route leak peut créer un cycle si VRF A importe une route de B et que B réimporte ensuite la route réinjectée. Les défenses incluent des prefix-lists précises, des route-maps, communities, tags de redistribution, frontières de protocole et limites de route. Tester une panne et une route qui disparaît : les tests « tout fonctionne » ne révèlent pas nécessairement les boucles de convergence.

## 7. RD, RT et MPLS L3VPN

### 7.1 Le RD rend le préfixe VPN distinct

Le **Route Distinguisher (RD)** rend unique une route VPN-IPv4 ou VPN-IPv6 quand plusieurs VPN utilisent un même préfixe IP. Le RD n’est pas un filtre de sécurité, ne prouve pas l’origine d’une route et ne détermine pas à lui seul quelles VRF la reçoivent.

### 7.2 Le RT contrôle la distribution entre VRF

Les **Route Targets (RT)** sont des extended communities BGP qui déterminent l’éligibilité d’une route à l’importation dans les VRF correspondantes. Une route est candidate à l’import si les RT de la route correspondent aux RT d’import de la VRF ; l’installation effective dépend aussi des règles de sélection et des conditions du système.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="RD et RT : deux fonctions différentes"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">RD et RT : deux fonctions différentes</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">Le RD distingue les routes VPN ; le RT contrôle leur importation dans les VRF.</text><line x1="290" y1="195" x2="350" y2="195" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="350.0,195.0 340.0,189.2 340.0,200.8" fill="#37d6c1"/><line x1="600" y1="195" x2="660" y2="195" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="660.0,195.0 650.0,189.2 650.0,200.8" fill="#4ea3ff"/><line x1="475" y1="250" x2="475" y2="280" stroke="#ff7185" stroke-width="3" stroke-linecap="round"/><polygon points="475.0,280.0 480.8,270.0 469.2,270.0" fill="#ff7185"/><rect x="40" y="140" width="250" height="110" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="40" y="140" width="7" height="110" rx="3" fill="#37d6c1"/><text x="58" y="165" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Route IPv4</text><text x="58" y="187" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">10.20.0.0/16</text><text x="58" y="206" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Préfixe appris du CE</text><rect x="350" y="140" width="250" height="110" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="350" y="140" width="7" height="110" rx="3" fill="#4ea3ff"/><text x="368" y="165" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">RD + préfixe</text><text x="368" y="187" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">65000:101:10.20.0.0/16</text><text x="368" y="206" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Rend la route VPN unique</text><rect x="660" y="140" width="260" height="110" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="660" y="140" width="7" height="110" rx="3" fill="#ffbd59"/><text x="678" y="165" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">RT export / import</text><text x="678" y="187" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">65000:100</text><text x="678" y="206" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Décide des VRF destinataires</text><rect x="350" y="280" width="250" height="65" rx="13" fill="#33202b" stroke="#ff7185" stroke-width="2"/><rect x="350" y="280" width="7" height="65" rx="3" fill="#ff7185"/><text x="368" y="305" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Ne pas confondre</text><text x="368" y="327" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">RD = identité · RT = politique</text></svg>


### 7.3 Exemple de conception

| VRF | RD d’exemple | RT export | RT import | Usage |
|---|---|---|---|---|
| `CORP-A` | `65000:101` | `65000:10` | `65000:30` | Utilisateurs |
| `APPS` | `65000:102` | `65000:20` | `65000:10` | Applications |
| `SHARED` | `65000:103` | `65000:30` | RT choisis | Services communs |

Ces nombres sont illustratifs. La convention RD peut être différente, mais il faut un plan stable et une documentation maintenue. Les RT doivent suivre le modèle de connectivité, pas simplement être copiés de VRF en VRF. Une VRF peut exporter plusieurs RT et importer plusieurs RT si la conception l’exige.

### 7.4 Quand le service n’est pas MPLS L3VPN

Une VRF-Lite locale peut exister sans cœur MPLS ni MP-BGP VPNv4. Ne configure pas des RD/RT uniquement parce que le mot « VRF » apparaît dans une conception : vérifie si la fonction exige ces attributs. Pour MPLS L3VPN, les routes client sont transportées dans des familles VPN BGP, et le forwarding s’appuie généralement sur un label de transport plus un label VPN, selon la méthode de transport et les options de plateforme.

## 8. MP-BGP VPNv4/VPNv6 et labels

Dans le modèle L3VPN de la RFC 4364, le PE apprend les routes du CE dans la VRF, les exporte dans BGP avec les attributs adéquats, puis les autres PE les importent dans leurs VRF si les RT correspondent. Le RD permet à BGP de distinguer des préfixes recouvrants ; les RT expriment une politique de distribution. Le label VPN associe le paquet au contexte de forwarding du PE distant. Le label extérieur amène le trafic vers le PE de sortie à travers le cœur MPLS.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Distribution VPNv4 via MP-BGP"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Distribution VPNv4 via MP-BGP</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">Les PEs échangent les routes VPN ; le plan de données utilise ensuite les labels pour transporter les paquets.</text><line x1="220" y1="195" x2="280" y2="195" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="280.0,195.0 270.0,189.2 270.0,200.8" fill="#37d6c1"/><line x1="500" y1="195" x2="560" y2="195" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="560.0,195.0 550.0,189.2 550.0,200.8" fill="#4ea3ff"/><line x1="745" y1="195" x2="790" y2="195" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="790.0,195.0 780.0,189.2 780.0,200.8" fill="#c3a1ff"/><line x1="390" y1="247" x2="390" y2="280" stroke="#ff7185" stroke-width="3" stroke-linecap="round"/><polygon points="390.0,280.0 395.8,270.0 384.2,270.0" fill="#ff7185"/><rect x="372.5" y="252.0" width="149.0" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="447.0" y="267.0" fill="#ff7185" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">transfert distinct</text><rect x="35" y="142" width="185" height="105" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="35" y="142" width="7" height="105" rx="3" fill="#37d6c1"/><text x="53" y="167" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">PE1</text><text x="53" y="189" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">VRF A</text><text x="53" y="208" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Route CE locale</text><rect x="280" y="142" width="220" height="105" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="280" y="142" width="7" height="105" rx="3" fill="#4ea3ff"/><text x="298" y="167" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">MP-BGP</text><text x="298" y="189" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">VPNv4 / VPNv6</text><text x="298" y="208" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">RD + RT + next-hop</text><rect x="560" y="142" width="185" height="105" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="560" y="142" width="7" height="105" rx="3" fill="#c3a1ff"/><text x="578" y="167" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">PE2</text><text x="578" y="189" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Import RT</text><text x="578" y="208" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">VRF distante</text><rect x="790" y="142" width="130" height="105" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="790" y="142" width="7" height="105" rx="3" fill="#ffbd59"/><text x="808" y="167" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">CE2</text><text x="808" y="189" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Site distant</text><rect x="280" y="280" width="465" height="65" rx="13" fill="#33202b" stroke="#ff7185" stroke-width="2"/><rect x="280" y="280" width="7" height="65" rx="3" fill="#ff7185"/><text x="298" y="305" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Plan de données MPLS</text><text x="298" y="327" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Label de transport + label VPN, selon la méthode utilisée</text></svg>


### 8.1 Déboguer une route absente

S’il manque un préfixe dans une VRF distante, ne commence pas uniquement par la table de routage CE. Vérifie successivement : route CE apprise localement, route présente dans la VRF source, export BGP VPN, RD/RT et politique, réception par le PE distant, import dans la VRF cible, label VPN/transport et route distribuée au CE. Un préfixe présent dans BGP VPNv4 n’est pas forcément importé dans la VRF ; une route importée n’est pas forcément transférée si la résolution du next-hop ou du label échoue.

### 8.2 RT-Constrain et échelle

Dans les grands réseaux, RT-Constrain permet de limiter la distribution des routes VPN aux PE qui signalent un intérêt pour un RT, lorsque cette fonction est prise en charge et activée. Cela diminue la diffusion inutile de routes mais introduit des éléments de contrôle supplémentaires à surveiller. Vérifier les capacités de la plate-forme, la configuration des address-families et les filtres BGP avant d’en faire une dépendance de production.

## 9. IPv6 dans les VRF

IPv6 a ses propres routes, voisins et fonctions de service à l’intérieur d’une VRF. Il ne suffit pas de configurer l’IPv4 et d’assumer que l’IPv6 est identique. Vérifier l’address-family, les routes connectées IPv6, le voisinage ND, les routes statiques IPv6 et les filtres correspondants. Les préfixes de test IPv6 doivent être choisis pour éviter toute confusion avec un vrai adressage de production.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Matrice d’import / export des RT"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Matrice d’import / export des RT</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">Une matrice claire évite la connectivité accidentelle entre domaines.</text><line x1="260" y1="171" x2="370" y2="171" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="370.0,171.0 360.0,165.2 360.0,176.8" fill="#37d6c1"/><rect x="289.2" y="141.0" width="51.5" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="315.0" y="156.0" fill="#37d6c1" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">RT 10</text><line x1="810" y1="217" x2="810" y2="260" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="810.0,260.0 815.8,250.0 804.2,250.0" fill="#ffbd59"/><line x1="150" y1="217" x2="150" y2="260" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="150.0,260.0 155.8,250.0 144.2,250.0" fill="#37d6c1"/><line x1="480" y1="217" x2="480" y2="260" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="480.0,260.0 485.8,250.0 474.2,250.0" fill="#4ea3ff"/><rect x="40" y="125" width="220" height="92" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="40" y="125" width="7" height="92" rx="3" fill="#37d6c1"/><text x="58" y="150" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF USERS</text><text x="58" y="172" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Export RT 65000:10</text><text x="58" y="191" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Import RT 65000:30</text><rect x="370" y="125" width="220" height="92" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="370" y="125" width="7" height="92" rx="3" fill="#4ea3ff"/><text x="388" y="150" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF APPS</text><text x="388" y="172" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Export RT 65000:20</text><text x="388" y="191" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Import RT 65000:10</text><rect x="700" y="125" width="220" height="92" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="700" y="125" width="7" height="92" rx="3" fill="#ffbd59"/><text x="718" y="150" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF SHARED</text><text x="718" y="172" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Export RT 65000:30</text><text x="718" y="191" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Import RT 65000:10</text><rect x="40" y="260" width="880" height="80" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="40" y="260" width="7" height="80" rx="3" fill="#c3a1ff"/><text x="58" y="285" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Revue de la politique</text><text x="58" y="307" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Pour chaque RT : qui l’exporte ? qui l’importe ? quelles routes ? quel chemin retour ?</text></svg>


Points de revue :

- l’interface possède le bon contexte VRF et une adresse IPv6 valide ;
- le voisin est découvert au niveau L2 (Neighbor Discovery) ;
- une route vers la destination existe dans la bonne table ;
- les politiques ACL, firewall ou uRPF sont cohérentes ;
- les services d’administration et de test sont VRF-aware si nécessaire ;
- les plans IPv4 et IPv6 ne produisent pas des politiques de sécurité contradictoires.

## 10. Services VRF-aware

Les services qui lancent eux-mêmes des connexions — ping, traceroute, SSH, NTP, TACACS+/RADIUS, syslog, DNS, DHCP relay, SNMP ou NAT — doivent disposer d’un chemin correct vers leur cible et, lorsque l’OS le prévoit, être attachés ou explicitement liés à la VRF pertinente. Les fonctions disponibles ne sont pas uniformes sur toutes les plates-formes.

### 10.1 Tester dans le bon contexte

Exemples fréquents sur certains systèmes IOS XE :

```text
ping vrf CORP-USERS 203.0.113.20
traceroute vrf CORP-USERS 203.0.113.20
show ip route vrf CORP-USERS
show ip interface brief vrf CORP-USERS
show vrf
```

Les options exactes peuvent différer. Toujours vérifier l’aide CLI et la documentation de la version déployée. Les tests doivent préciser l’adresse source lorsque cela change le chemin ou les règles d’accès, et doivent être complétés par un test depuis l’hôte source final.

### 10.2 Plan d’administration

Le management *out-of-band* est différent d’une VRF de management utilisée sur la même infrastructure physique. L’OOB réduit certaines dépendances, mais n’annule pas les exigences d’authentification et de journalisation. Si une VRF de management partage le même châssis et la même infrastructure de commutation, documenter les risques communs, l’accès console de secours et la procédure de récupération.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Instance de routage par VRF"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Instance de routage par VRF</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">La présence d’un processus global ne garantit pas que la VRF apprend des routes.</text><line x1="250" y1="192" x2="335" y2="192" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="335.0,192.0 325.0,186.2 325.0,197.8" fill="#37d6c1"/><line x1="565" y1="192" x2="650" y2="192" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="650.0,192.0 640.0,186.2 640.0,197.8" fill="#4ea3ff"/><line x1="450" y1="245" x2="450" y2="280" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="450.0,280.0 455.8,270.0 444.2,270.0" fill="#ffbd59"/><rect x="40" y="140" width="210" height="105" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="40" y="140" width="7" height="105" rx="3" fill="#37d6c1"/><text x="58" y="165" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF CLIENT-A</text><text x="58" y="187" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Interface CE-A</text><text x="58" y="206" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">OSPF/BGP configuré</text><rect x="335" y="140" width="230" height="105" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="335" y="140" width="7" height="105" rx="3" fill="#4ea3ff"/><text x="353" y="165" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Instance / AF</text><text x="353" y="187" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Contexte VRF explicite</text><text x="353" y="206" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Voisins et filtres</text><rect x="650" y="140" width="270" height="105" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="650" y="140" width="7" height="105" rx="3" fill="#c3a1ff"/><text x="668" y="165" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">RIB CLIENT-A</text><text x="668" y="187" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Routes apprises</text><text x="668" y="206" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Next-hop résolu</text><rect x="335" y="280" width="230" height="65" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="335" y="280" width="7" height="65" rx="3" fill="#ffbd59"/><text x="353" y="305" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">À vérifier</text><text x="353" y="327" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Interface · voisin · policy</text></svg>


## 11. Redondance, convergence et échelle

### 11.1 Planifier la perte d’un lien et d’un routeur

Vérifier la convergence des protocoles, le retrait des routes, la détection de next-hop indisponible, la stabilité des routes par défaut et l’état des services dépendants. Une route de secours ne vaut que si son next-hop et le chemin retour sont opérationnels. Mesurer les temps réels pendant un exercice contrôlé ; ne pas déduire la convergence uniquement d’une valeur théorique de timer.

### 11.2 Échelle de routes et limites matérielles

Une configuration qui fonctionne avec 20 routes peut échouer ou consommer trop de ressources avec 100 000 routes. Examiner les limites publiées : VRF, IPv4/IPv6, routes, adjacences, entrées TCAM, sessions BGP, mémoire et charge du plan de contrôle. Réduire les routes inutiles, agréger lorsque c’est correct et éviter l’importation de tables complètes dans des domaines qui n’en ont pas besoin.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Route leaking contrôlé avec BGP"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Route leaking contrôlé avec BGP</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">Filtrer les préfixes entrants et sortants, documenter les routes de retour et éviter les boucles.</text><line x1="250" y1="193" x2="335" y2="193" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="335.0,193.0 325.0,187.2 325.0,198.8" fill="#37d6c1"/><line x1="595" y1="193" x2="680" y2="193" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="680.0,193.0 670.0,187.2 670.0,198.8" fill="#c3a1ff"/><line x1="460" y1="240" x2="460" y2="275" stroke="#ff7185" stroke-width="3" stroke-linecap="round"/><polygon points="460.0,275.0 465.8,265.0 454.2,265.0" fill="#ff7185"/><rect x="40" y="145" width="210" height="95" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="40" y="145" width="7" height="95" rx="3" fill="#37d6c1"/><text x="58" y="170" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF A</text><text x="58" y="192" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Préfixes autorisés</text><rect x="335" y="145" width="260" height="95" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="335" y="145" width="7" height="95" rx="3" fill="#ffbd59"/><text x="353" y="170" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Politique BGP</text><text x="353" y="192" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Prefix-list / route-map</text><text x="353" y="211" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Community / next-hop</text><rect x="680" y="145" width="240" height="95" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="680" y="145" width="7" height="95" rx="3" fill="#c3a1ff"/><text x="698" y="170" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">VRF B</text><text x="698" y="192" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Services nécessaires</text><rect x="335" y="275" width="585" height="68" rx="13" fill="#33202b" stroke="#ff7185" stroke-width="2"/><rect x="335" y="275" width="7" height="68" rx="3" fill="#ff7185"/><text x="353" y="300" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Garde-fous</text><text x="353" y="322" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Filtrage, prévention des boucles, contrôle des chemins retour et tests de non-régression</text></svg>


### 11.3 Préserver l’observabilité

Chaque VRF doit apparaître clairement dans les tableaux de bord, la collecte des journaux, les alertes et les procédures d’astreinte. Utiliser des noms de VRF stables, des descriptions d’interface, des tags de configuration et une source de vérité. Lorsque les collecteurs interrogent plusieurs contextes, confirmer que les données ne sont pas mélangées ou associées à la mauvaise table.

## 12. Sécurité et gouvernance

La séparation VRF fournit une frontière de routage, pas une autorisation métier. Le modèle de sécurité doit documenter quels flux sont permis, quelle inspection s’applique et comment les journaux sont conservés. Éviter les règles d’import/export trop larges, les routes par défaut invisibles aux propriétaires, les interfaces de gestion exposées et la redistribution incontrôlée.

### 12.1 Matrice de flux

Pour chaque flux, enregistrer source VRF, source/préfixe, destination VRF, destination/préfixe, protocole/port, sens d’initiation, chemin retour, mécanisme de filtrage, propriétaire et procédure de test. Relier les routes autorisées à des exigences fonctionnelles précises. Une route importée ne doit pas être interprétée comme une preuve d’autorisation.

### 12.2 Contrôles de changement

Avant et après un changement : sauvegarder la configuration, extraire les routes et politiques concernées, définir un test, prévoir le rollback et surveiller les compteurs. Pour un ajout de RT, vérifier la portée exacte des importations. Pour une nouvelle redistribution, définir un filtre explicite et vérifier le retrait des routes lors d’une panne.

## 13. Méthode de dépannage

Procéder par couches, sans changer plusieurs variables à la fois.

1. **Contexte :** interface entrée, VRF, VLAN/tag, état L1/L2.
2. **Adressage :** IP, masque/préfixe, ARP/ND, next-hop local.
3. **RIB :** route spécifique, préférence, source, route par défaut.
4. **FIB :** adjacence, résolution du next-hop, ressources matérielles si pertinent.
5. **Distribution :** voisin dynamique, filtre, redistribution, RD/RT, BGP VPN.
6. **Politique :** ACL, firewall, NAT, uRPF, politique de service.
7. **Retour :** route retour, asymétrie, filtrage côté destination.
8. **Mesure :** compteurs d’interface, logs, capture et test source-destination.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Services VRF-aware"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Services VRF-aware</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">Le service doit être explicitement attaché au contexte ou posséder une route appropriée vers celui-ci.</text><line x1="265" y1="192" x2="365" y2="192" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="365.0,192.0 355.0,186.2 355.0,197.8" fill="#37d6c1"/><line x1="590" y1="192" x2="690" y2="192" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="690.0,192.0 680.0,186.2 680.0,197.8" fill="#4ea3ff"/><line x1="480" y1="246" x2="480" y2="280" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="480.0,280.0 485.8,270.0 474.2,270.0" fill="#ffbd59"/><rect x="40" y="138" width="225" height="108" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="40" y="138" width="7" height="108" rx="3" fill="#37d6c1"/><text x="58" y="163" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Opérateur</text><text x="58" y="185" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Ping / traceroute</text><text x="58" y="204" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">SSH / NTP / syslog</text><rect x="365" y="138" width="225" height="108" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="365" y="138" width="7" height="108" rx="3" fill="#4ea3ff"/><text x="383" y="163" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Contexte VRF</text><text x="383" y="185" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">CLIENT-A</text><text x="383" y="204" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Source et lookup corrects</text><rect x="690" y="138" width="230" height="108" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="690" y="138" width="7" height="108" rx="3" fill="#c3a1ff"/><text x="708" y="163" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Destination</text><text x="708" y="185" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Adresse joignable</text><text x="708" y="204" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">ACL / firewall permis</text><rect x="365" y="280" width="225" height="65" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="365" y="280" width="7" height="65" rx="3" fill="#ffbd59"/><text x="383" y="305" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Vérifier</text><text x="383" y="327" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Support dépend de l’OS</text></svg>


### 13.1 Symptômes fréquents

| Symptôme | Causes probables | Vérification initiale |
|---|---|---|
| Le ping global réussit, ping VRF échoue | Chemin différent, route absente, mauvais contexte | route RIB/FIB dans la VRF ciblée |
| Route présente dans VRF source mais absente à distance | Export/import, RT, voisin BGP ou politique | comparer la chaîne CE → VRF → VPN BGP → VRF distante |
| Route présente mais aucun trafic ne passe | Next-hop non résolu, ACL, MTU, retour absent | FIB/adjacence, compteurs, test bidirectionnel |
| Une seule application échoue | Port filtré, NAT, état firewall ou MTU | test TCP/application, logs sécurité |
| IPv4 marche, IPv6 échoue | AF IPv6 absente, ND, filtre IPv6 | route IPv6 VRF et voisinage ND |
| Perte après ajout d’une VRF | Adresse interface effacée, route déplacée, service global | état interface et routes avant/après |

## 14. Laboratoire multi-VRF

### 14.1 Objectif

Créer `CORP-USERS`, `APP-SERVERS` et `SHARED-SVC`. Les deux premières VRF doivent rester isolées par défaut. Les utilisateurs peuvent joindre uniquement le service DNS partagé dans cet exercice. Le lab utilise des interfaces routées et des routes statiques afin de se concentrer sur le contexte VRF ; ce n’est pas un modèle complet de sécurité de production.

### 14.2 Plan d’adressage d’exemple

| Équipement | Interface | VRF | Adresse |
|---|---|---|---|
| R1 | Gi0/1 | CORP-USERS | 192.0.2.1/30 |
| R1 | Gi0/2 | SHARED-SVC | 198.51.100.1/30 |
| R1 | Gi0/3 | APP-SERVERS | 203.0.113.1/30 |
| CE-USERS | Gi0/0 | — | 192.0.2.2/30 |
| DNS-SVC | Gi0/0 | — | 198.51.100.2/30 |
| APP | Gi0/0 | — | 203.0.113.2/30 |

Les préfixes sont réservés à la documentation. La configuration exacte dépend du lab matériel ou virtuel. Dans une production, le routage entre VRF doit être accompagné d’une politique de sécurité et de chemins retour cohérents.

### 14.3 Étapes de réalisation

1. Créer les trois VRF et vérifier leur présence.
2. Affecter les interfaces à la bonne VRF, puis configurer les adresses.
3. Ajouter les routes de destination requises et vérifier le next-hop dans chaque VRF.
4. Tester la connectivité depuis chaque contexte, puis depuis les hôtes.
5. Mettre en place un leak strictement limité vers le service partagé, avec une méthode adaptée à l’OS.
6. Tester un chemin non autorisé et confirmer qu’il est refusé par la politique de sécurité, pas seulement absent par accident.
7. Débrancher un lien dans un environnement contrôlé, mesurer le comportement et restaurer l’état initial.
8. Documenter le résultat, la route attendue, la route observée et le rollback.


<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Diagnostic VRF de bout en bout"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700">Diagnostic VRF de bout en bout</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14">Procéder du contexte et de l’interface vers la route, le next-hop, le service et le retour.</text><line x1="230" y1="175" x2="270" y2="175" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="270.0,175.0 260.0,169.2 260.0,180.8" fill="#37d6c1"/><line x1="465" y1="175" x2="505" y2="175" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="505.0,175.0 495.0,169.2 495.0,180.8" fill="#4ea3ff"/><line x1="700" y1="175" x2="740" y2="175" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="740.0,175.0 730.0,169.2 730.0,180.8" fill="#ffbd59"/><line x1="597" y1="220" x2="597" y2="275" stroke="#ff7185" stroke-width="3" stroke-linecap="round"/><polygon points="597.0,275.0 602.8,265.0 591.2,265.0" fill="#ff7185"/><rect x="595.0" y="237.0" width="74.0" height="21" rx="7" fill="#0b1423" stroke="#253a54" stroke-width="1"/><text x="632.0" y="252.0" fill="#ff7185" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" text-anchor="middle">si échec</text><rect x="35" y="130" width="195" height="90" rx="13" fill="#162b42" stroke="#37d6c1" stroke-width="2"/><rect x="35" y="130" width="7" height="90" rx="3" fill="#37d6c1"/><text x="53" y="155" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">1 · Contexte</text><text x="53" y="177" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">VRF / interface</text><rect x="270" y="130" width="195" height="90" rx="13" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="270" y="130" width="7" height="90" rx="3" fill="#4ea3ff"/><text x="288" y="155" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">2 · Route</text><text x="288" y="177" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">RIB / FIB / next-hop</text><rect x="505" y="130" width="195" height="90" rx="13" fill="#302a20" stroke="#ffbd59" stroke-width="2"/><rect x="505" y="130" width="7" height="90" rx="3" fill="#ffbd59"/><text x="523" y="155" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">3 · Transport</text><text x="523" y="177" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">ACL / tunnel / MTU</text><rect x="740" y="130" width="185" height="90" rx="13" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="740" y="130" width="7" height="90" rx="3" fill="#c3a1ff"/><text x="758" y="155" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">4 · Retour</text><text x="758" y="177" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Route asymétrique ?</text><rect x="270" y="275" width="430" height="70" rx="13" fill="#33202b" stroke="#ff7185" stroke-width="2"/><rect x="270" y="275" width="7" height="70" rx="3" fill="#ff7185"/><text x="288" y="300" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700">Comparer les deux directions</text><text x="288" y="322" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13">Source, VRF, route choisie, compteurs et capture si nécessaire</text></svg>


## 15. Études de cas

### Cas A — Deux clients ont le même préfixe

Deux VRF utilisent `10.10.0.0/16`. C’est supportable si les tables sont distinctes, mais un route leaking naïf peut rendre le choix ambigu ou introduire une route qui ne représente pas le même espace d’adresses. Décider si les domaines doivent rester isolés, si une traduction est nécessaire, ou si une architecture VPN apporte le comportement attendu.

### Cas B — Le DNS central est accessible dans un sens seulement

Les utilisateurs atteignent le DNS, mais aucune réponse ne revient. Examiner le chemin retour dans la VRF des services, les règles pare-feu, la source du paquet, les routes de destination et le traitement du NAT. Ne pas élargir tous les RT pour contourner une route retour manquante.

### Cas C — Préfixe absent sur le PE distant

Vérifier la route PE-CE locale, sa présence dans la VRF, le RD/RT, la session et l’address-family MP-BGP, puis l’importation dans la VRF distante. Si la route est importée mais le trafic ne passe pas, déplacer l’investigation vers next-hop, label, FIB, MTU et retour.

### Cas D — Après un changement d’interface, l’adresse a disparu

Sur certaines versions IOS XE, la commande d’affectation VRF efface l’adresse existante. Restaurer l’adresse dans la bonne VRF et valider la RIB/FIB. Prévenir ce type d’incident avec une revue de prérequis et une fenêtre de changement.

### Cas E — Table globale saturée, VRF moins utilisée

La capacité de routage doit être évaluée sur l’ensemble de la plateforme : quantité de routes par famille, ressources FIB/TCAM, protocoles, adjacences et fonctions activées. Réduire les routes importées et vérifier les limites officielles ; ne pas présumer que chaque VRF possède des ressources matérielles entièrement isolées.

## 16. Quiz de validation

1. Quelle différence entre RIB et FIB ?
2. Pourquoi une route dans la table globale ne rend-elle pas automatiquement une VRF joignable ?
3. Pourquoi le RD et le RT ne sont-ils pas interchangeables ?
4. Quelles vérifications effectuer lorsqu’une route est visible en VPNv4 mais absente de la VRF distante ?
5. Pourquoi un route leaking peut-il provoquer une boucle ?
6. Quelles précautions prendre avant `vrf forwarding` sur une interface active ?
7. Pourquoi le chemin retour compte-t-il avec un pare-feu à état ?
8. Quelles ressources doivent être étudiées pour estimer la capacité VRF ?
9. Pourquoi VRF n’équivaut-elle pas à pare-feu ?
10. Comment distinguer une panne de routage d’une panne applicative ?

### Corrigé

1. La RIB conserve les routes candidates/choisies ; la FIB guide le forwarding effectif.
2. La recherche se fait dans le contexte de routage de l’interface et les tables sont distinctes.
3. Le RD distingue les routes VPN ; le RT détermine l’éligibilité à l’importation.
4. Vérifier export, session/AF, RT, politique d’import et installation dans la VRF.
5. Une route peut être réinjectée vers le domaine d’origine si les filtres ne préviennent pas le cycle.
6. La commande peut supprimer l’adresse IP existante ; planifier et reconfigurer après l’affectation si nécessaire.
7. Le firewall peut attendre que le trafic de réponse corresponde à une session initiée ou autorisée.
8. VRF, routes, FIB/TCAM, mémoire, adjacences, sessions et limites de la plateforme.
9. La VRF sépare le routage mais ne fournit pas automatiquement l’inspection et les règles d’autorisation.
10. Comparer les routes aller/retour, compteurs et tests réseau avec les journaux et tests applicatifs.

## 17. Checklist de revue d’architecture

- [ ] Chaque VRF possède une fonction et un propriétaire documentés.
- [ ] Les interfaces, VLAN/SVI et sous-interfaces correspondent à la matrice.
- [ ] Les plans IPv4 et IPv6 sont cohérents.
- [ ] Les routes statiques ont un next-hop résolu et un comportement de secours explicite.
- [ ] Les instances de routage sont configurées dans le bon contexte.
- [ ] Chaque redistribution ou route leak dispose de filtres explicites.
- [ ] Les RD/RT sont documentés pour les services MPLS L3VPN concernés.
- [ ] Les services VRF-aware sont testés depuis le bon contexte.
- [ ] Les chemins retour, ACL, pare-feu et NAT ont été validés.
- [ ] Les limites FIB/TCAM et de routes sont connues.
- [ ] Logs et supervision distinguent chaque VRF.
- [ ] Plan de changement, rollback et tests de panne existent.

## 18. Glossaire

- **VRF :** contexte logique de routage et de forwarding.
- **VRF-Lite :** usage local de VRF sans nécessairement utiliser MPLS.
- **RIB :** base des routes et décisions de routage.
- **FIB :** structure utilisée pour le transfert des paquets.
- **RD :** identifiant qui rend une route VPN distincte.
- **RT :** attribut de politique d’import/export de routes VPN.
- **PE / CE :** routeur de bordure fournisseur / équipement client.
- **MP-BGP :** BGP multi-protocole, pouvant transporter VPNv4/VPNv6.
- **Route leaking :** importation contrôlée de routes entre contextes.
- **Next-hop :** prochain saut utilisé pour acheminer le paquet.
- **TCAM :** mémoire spécialisée fréquemment utilisée pour les recherches rapides de forwarding et les ACL.

## Références techniques

- Cisco, *Configure VRF Leaks on IOS XE*: https://www.cisco.com/c/en/us/support/docs/ip/ip-routing/216541-vrf-configuration-examples-on-ios-xe.html
- Cisco, *Configuring VRF-Lite* (Catalyst 9200 IOS XE 26.x): https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9200/software/release/26-x/configuration_guide/rtng/b_26x_rtng_9200_cg/configuring_vrf_lite.html
- RFC 4364, *BGP/MPLS IP Virtual Private Networks*: https://www.rfc-editor.org/rfc/rfc4364
- RFC 4271, *A Border Gateway Protocol 4 (BGP-4)*: https://www.rfc-editor.org/rfc/rfc4271

> **Rappel de mise en production :** les exemples de configuration ne sont pas une configuration universelle. Valide toujours la syntaxe, les fonctions, la capacité et les procédures de changement pour le matériel et la version réellement déployés.
