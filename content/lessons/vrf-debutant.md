# VRF — Niveau Débutant

> **Parcours :** Réseaux et routage · **Niveau :** Débutant · **Fichier :** `vrf-debutant.md`

## Objectifs pédagogiques
À la fin du cours, tu sauras expliquer pourquoi une VRF est utile, distinguer la table globale des tables VRF, associer une interface à une VRF, vérifier les routes et comprendre la différence entre **VRF-Lite** et **MPLS L3VPN**. Tu pourras suivre une procédure de configuration et de dépannage de base sur Cisco IOS XE, en adaptant la syntaxe à la plate-forme réelle.

## Prérequis
Connaître IPv4, les masques, la route connectée, la route statique, la passerelle par défaut, les interfaces Ethernet et les commandes de base `show`, `ping` et `traceroute`.

## Plan du cours
1. Pourquoi virtualiser le routage ?
2. Une VRF, une table logique
3. Lookup d’un paquet
4. Préfixes qui se chevauchent
5. VRF-Lite et MPLS L3VPN
6. Créer une VRF sur IOS XE
7. Associer une interface
8. Routes et protocoles dans une VRF
9. Route leaking et sécurité
10. VRF de management
11. Laboratoire
12. Vérification et dépannage
13. Exercices et quiz
14. Glossaire et références

## 1. Pourquoi virtualiser le routage ?

Un routeur classique possède une table de routage IPv4 globale et, lorsque IPv6 est activé, une table IPv6 globale. Toutes les interfaces non affectées à une VRF utilisent normalement ce contexte global. Dans un réseau multi-clients ou multi-environnements, cette organisation peut devenir insuffisante : plusieurs groupes peuvent avoir besoin d’un routage indépendant, voire utiliser les mêmes adresses privées.

Une **VRF** (*Virtual Routing and Forwarding*) est un contexte de routage et de transfert distinct, maintenu par un équipement. Elle associe notamment une table de routage et les informations nécessaires au forwarding dans ce contexte. Les préfixes, routes connectées, routes statiques et routes apprises par un protocole peuvent ainsi être gérés indépendamment dans plusieurs VRF.

Exemples d’usage : séparer PROD et LAB, séparer des clients sur un équipement partagé, isoler le trafic de management, ou fournir plusieurs domaines de routage à des services. Une VRF est d’abord une séparation du plan de routage. Elle ne remplace pas un pare-feu, une politique ACL, l’authentification ou le chiffrement.

**Schéma 1 — Un routeur, plusieurs tables de routage**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Un routeur, plusieurs tables de routage"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Un routeur, plusieurs tables de routage</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Une VRF sépare logiquement les décisions de routage et de transfert.</text><rect x="34" y="108" width="178" height="96" rx="14" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="34" y="108" width="7" height="96" rx="3" fill="#4ea3ff" stroke="none"/><text x="52" y="137" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Réseau entrant</text><text x="52" y="163" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Gi0/1 · VLAN 10</text><line x1="212" y1="157" x2="286" y2="157" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="286.0,157.0 276.8,163.0 276.8,151.0" fill="#4ea3ff"/><text x="249.0" y="143" fill="#4ea3ff" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" text-anchor="middle">interface associée</text><rect x="286" y="106" width="184" height="102" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="286" y="106" width="7" height="102" rx="3" fill="#37d6c1" stroke="none"/><text x="304" y="135" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF CLIENT-A</text><text x="304" y="161" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">RIB / FIB propres</text><text x="304" y="184" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Routes 10.10.10.0/24</text><rect x="286" y="236" width="184" height="102" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="286" y="236" width="7" height="102" rx="3" fill="#c3a1ff" stroke="none"/><text x="304" y="265" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF CLIENT-B</text><text x="304" y="291" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">RIB / FIB propres</text><text x="304" y="314" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Routes 10.10.10.0/24</text><rect x="34" y="238" width="178" height="96" rx="14" fill="#162b42" stroke="#c3a1ff" stroke-width="2"/><rect x="34" y="238" width="7" height="96" rx="3" fill="#c3a1ff" stroke="none"/><text x="52" y="267" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Autre interface</text><text x="52" y="293" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Gi0/2 · VLAN 20</text><line x1="212" y1="286" x2="260" y2="286" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="260.0,286.0 250.8,292.0 250.8,280.0" fill="#c3a1ff"/><line x1="260" y1="286" x2="278" y2="287" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="278.0,287.0 268.5,292.5 269.1,280.5" fill="#c3a1ff"/><rect x="538" y="140" width="176" height="120" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="538" y="140" width="7" height="120" rx="3" fill="#ffbd59" stroke="none"/><text x="556" y="169" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Table globale</text><text x="556" y="195" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Réseaux système</text><text x="556" y="218" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">et management</text><line x1="470" y1="157" x2="538" y2="178" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="538.0,178.0 527.4,181.0 531.0,169.5" fill="#37d6c1"/><line x1="470" y1="287" x2="538" y2="222" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="538.0,222.0 535.5,232.7 527.2,224.0" fill="#c3a1ff"/><text x="740" y="170" fill="#58d68d" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">Même préfixe possible</text><text x="740" y="198" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">dans 2 VRF distinctes</text><text x="740" y="226" fill="#ffbd59" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" text-anchor="start">Aucune fusion implicite</text></svg>

## 2. Une VRF, une table logique

### RIB et FIB : deux rôles différents

La **RIB** (*Routing Information Base*) conserve les routes candidates et la route retenue selon les règles de sélection du système. La **FIB** (*Forwarding Information Base*) représente les informations utilisées pour transférer effectivement les paquets. La séparation des VRF doit être cohérente dans les deux vues : une route vue dans une table de routage donnée ne signifie pas que le transfert est fonctionnel si le next-hop ne peut pas être résolu ou si une politique bloque le paquet.

Une VRF ne correspond pas nécessairement à un processus matériel séparé. Le système d’exploitation peut partager des ressources internes tout en maintenant des contextes de routage logiquement distincts. Les limites de capacité sont donc celles de la plateforme : nombre de VRF, nombre de routes, mémoire, TCAM, fonctionnalités de routage et licences éventuelles. Il faut consulter les limites publiées pour le modèle précis plutôt que supposer qu’un équipement peut gérer un nombre illimité de VRF.

### VRF, VLAN et sous-réseau : pas la même chose

Un VLAN segmente un domaine Ethernet de couche 2. Un sous-réseau IP définit un préfixe de couche 3. Une VRF sépare une table de routage et le contexte de forwarding. Ces objets sont souvent combinés, mais ils ne sont pas interchangeables : plusieurs VLAN peuvent utiliser la même VRF, et plusieurs VRF peuvent exister sur le même routeur ou commutateur L3. Le placement concret dépend de la conception : SVI, sous-interface 802.1Q ou port routé, par exemple.

Un design courant associe un VLAN d’accès à une SVI, puis associe cette SVI à une VRF. Le VLAN traite les trames du domaine de couche 2 ; la VRF sélectionne la table lorsque les paquets sont routés à partir de cette interface L3. Le switch peut donc porter des VLANs distincts tout en séparant aussi leurs domaines IP au niveau VRF.


Imagine un routeur qui héberge trois contextes : `CLIENT-A`, `CLIENT-B` et `GLOBAL`. Chaque VRF peut avoir ses propres routes connectées et statiques, et des instances de protocoles de routage distinctes selon la prise en charge par le système.

La même adresse IP peut apparaître dans plusieurs tables. Ce n’est pas automatiquement une collision, car la décision de routage s’effectue dans le contexte VRF associé à l’interface d’entrée ou à l’opération explicite de lookup. En revanche, si les réseaux doivent communiquer entre VRF, il faut un mécanisme prévu et contrôlé : route leaking, pare-feu, passerelle de services ou architecture de VPN appropriée.

**Schéma 2 — Chemin de décision d’un paquet**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Chemin de décision d’un paquet"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Chemin de décision d’un paquet</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">L’interface d’entrée détermine la table de routage consultée.</text><rect x="28" y="154" width="155" height="96" rx="14" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="28" y="154" width="7" height="96" rx="3" fill="#4ea3ff" stroke="none"/><text x="46" y="183" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Paquet reçu</text><text x="46" y="209" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">source / destination</text><line x1="183" y1="202" x2="230" y2="202" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="230.0,202.0 220.8,208.0 220.8,196.0" fill="#4ea3ff"/><rect x="230" y="154" width="160" height="96" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="230" y="154" width="7" height="96" rx="3" fill="#37d6c1" stroke="none"/><text x="248" y="183" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Interface L3</text><text x="248" y="209" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Gi0/1 dans VRF-A</text><line x1="390" y1="202" x2="437" y2="202" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="437.0,202.0 427.8,208.0 427.8,196.0" fill="#37d6c1"/><rect x="437" y="154" width="160" height="96" rx="14" fill="#102c38" stroke="#58d68d" stroke-width="2"/><rect x="437" y="154" width="7" height="96" rx="3" fill="#58d68d" stroke="none"/><text x="455" y="183" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Lookup VRF-A</text><text x="455" y="209" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Longest-prefix match</text><line x1="597" y1="202" x2="644" y2="202" stroke="#58d68d" stroke-width="3" stroke-linecap="round"/><polygon points="644.0,202.0 634.8,208.0 634.8,196.0" fill="#58d68d"/><rect x="644" y="154" width="140" height="96" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="644" y="154" width="7" height="96" rx="3" fill="#ffbd59" stroke="none"/><text x="662" y="183" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Next-hop</text><text x="662" y="209" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">route + sortie</text><line x1="784" y1="202" x2="831" y2="202" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="831.0,202.0 821.8,208.0 821.8,196.0" fill="#ffbd59"/><rect x="831" y="154" width="103" height="96" rx="14" fill="#162b42" stroke="#c3a1ff" stroke-width="2"/><rect x="831" y="154" width="7" height="96" rx="3" fill="#c3a1ff" stroke="none"/><text x="849" y="183" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" text-anchor="start">Sortie</text><text x="849" y="209" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">L2 / L3</text><text x="480" y="294" fill="#ff7185" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" text-anchor="middle">Si aucune route utilisable : échec de forwarding dans cette VRF</text></svg>

## 3. Comment le routeur choisit la table

### Exemple de chemin de paquet

Supposons qu’un paquet arrive sur `GigabitEthernet0/1`, interface rattachée à `CLIENT-A`. La destination `10.20.30.40` est recherchée dans la RIB/FIB de `CLIENT-A`; une route spécifique `10.20.30.0/24` peut être préférée à une route par défaut `0.0.0.0/0`. Le next-hop est ensuite résolu dans le contexte prévu. La table globale n’est pas consultée automatiquement comme solution de repli générale si une destination manque dans `CLIENT-A`.

Le **longest-prefix match** décide quel préfixe correspond le plus précisément à l’adresse de destination parmi les routes admissibles de la table sélectionnée. La distance administrative et les métriques servent principalement à comparer les sources de routes pour un même préfixe, tandis que la longueur du préfixe détermine la spécificité du match. Ces critères ne doivent pas être confondus.

### Plan de contrôle et plan de données

Le plan de contrôle apprend ou construit les routes. Le plan de données transfère les paquets en s’appuyant sur les informations installées dans la FIB et sur la résolution des adjacences. Un problème peut donc se situer à plusieurs niveaux : voisinage de routage absent, route non acceptée par une politique, route présente dans la RIB mais absente de la FIB, voisin ARP/ND absent, ou filtrage sur le chemin. Un bon diagnostic ne s’arrête pas au seul `show ip route`.


Lorsqu’un paquet arrive sur une interface de couche 3, l’équipement connaît le contexte de routage associé à cette interface. Il recherche la destination dans la table correspondante selon les règles de sélection de route applicables, dont le *longest-prefix match*. Il résout ensuite le next-hop et détermine l’interface de sortie dans ce contexte.

Un ping exécuté sans préciser la VRF peut utiliser la table globale, donc ne pas tester le chemin utilisé par le client. Beaucoup de commandes d’exploitation acceptent un paramètre VRF, par exemple `ping vrf CLIENT-A 192.0.2.2` sur certaines versions IOS/IOS XE. Vérifie la syntaxe exacte de la plateforme.

**Schéma 3 — Adresses qui se chevauchent**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Adresses qui se chevauchent"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Adresses qui se chevauchent</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Deux clients peuvent utiliser le même préfixe dans des VRF différentes.</text><rect x="45" y="114" width="180" height="100" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="45" y="114" width="7" height="100" rx="3" fill="#37d6c1" stroke="none"/><text x="63" y="143" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Site A</text><text x="63" y="169" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">LAN : 10.10.10.0/24</text><rect x="45" y="242" width="180" height="100" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="45" y="242" width="7" height="100" rx="3" fill="#c3a1ff" stroke="none"/><text x="63" y="271" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Site B</text><text x="63" y="297" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">LAN : 10.10.10.0/24</text><rect x="327" y="114" width="222" height="100" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="327" y="114" width="7" height="100" rx="3" fill="#37d6c1" stroke="none"/><text x="345" y="143" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF CLIENT-A</text><text x="345" y="169" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Route 10.10.10.0/24</text><text x="345" y="192" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">next-hop A</text><rect x="327" y="242" width="222" height="100" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="327" y="242" width="7" height="100" rx="3" fill="#c3a1ff" stroke="none"/><text x="345" y="271" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF CLIENT-B</text><text x="345" y="297" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Route 10.10.10.0/24</text><text x="345" y="320" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">next-hop B</text><line x1="225" y1="164" x2="327" y2="164" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="327.0,164.0 317.8,170.0 317.8,158.0" fill="#37d6c1"/><line x1="225" y1="292" x2="327" y2="292" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="327.0,292.0 317.8,298.0 317.8,286.0" fill="#c3a1ff"/><rect x="655" y="167" width="252" height="118" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="655" y="167" width="7" height="118" rx="3" fill="#ffbd59" stroke="none"/><text x="673" y="196" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Même adresse réseau</text><text x="673" y="222" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">mais contexte différent</text><text x="673" y="245" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">pas de conflit dans les RIB</text><line x1="549" y1="164" x2="610" y2="197" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="610.0,197.0 599.0,197.9 604.8,187.3" fill="#37d6c1"/><line x1="549" y1="292" x2="610" y2="253" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="610.0,253.0 605.5,263.0 599.0,252.9" fill="#c3a1ff"/></svg>

## 4. Préfixes qui se chevauchent

Deux clients peuvent tous les deux utiliser `10.10.10.0/24`. Si les interfaces et les routes sont associées à des VRF différentes, le routeur peut traiter séparément ces préfixes. En revanche, deux interfaces dans le **même** contexte de routage ne peuvent pas simplement représenter deux domaines indépendants avec le même préfixe comme s’ils étaient des réseaux distincts.

Cela ne signifie pas que l’IP se duplique sans conséquence dans tous les autres systèmes : les outils de supervision, les ACL, la journalisation, les systèmes IPAM et les applications peuvent devoir identifier le contexte client en plus de l’adresse.

**Schéma 4 — VRF-Lite et MPLS L3VPN : ne pas confondre**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="VRF-Lite et MPLS L3VPN : ne pas confondre"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">VRF-Lite et MPLS L3VPN : ne pas confondre</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Les tables VRF existent dans les deux modèles, mais les mécanismes inter-sites diffèrent.</text><rect x="35" y="103" width="430" height="235" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="35" y="103" width="7" height="235" rx="3" fill="#37d6c1" stroke="none"/><text x="53" y="132" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" text-anchor="start">VRF-Lite</text><text x="53" y="158" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" text-anchor="start">• Tables séparées sur un équipement</text><text x="53" y="181" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" text-anchor="start">• Interfaces affectées localement</text><text x="53" y="204" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" text-anchor="start">• Routage local par VRF</text><text x="53" y="227" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" text-anchor="start">• Pas de MP-BGP/labels requis</text><rect x="495" y="103" width="430" height="235" rx="14" fill="#1b2440" stroke="#c3a1ff" stroke-width="2"/><rect x="495" y="103" width="7" height="235" rx="3" fill="#c3a1ff" stroke="none"/><text x="513" y="132" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" text-anchor="start">MPLS L3VPN</text><text x="513" y="158" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" text-anchor="start">• VRF sur les PE</text><text x="513" y="181" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" text-anchor="start">• MP-BGP VPNv4/VPNv6</text><text x="513" y="204" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" text-anchor="start">• RD distingue les préfixes VPN</text><text x="513" y="227" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" text-anchor="start">• RT contrôle import / export</text><text x="513" y="250" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" text-anchor="start">• Labels transport et VPN</text><text x="480" y="366" fill="#ffbd59" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" text-anchor="middle">VRF-Lite = séparation locale  |  MPLS L3VPN = distribution de VPN entre PE</text></svg>

## 5. VRF-Lite et MPLS L3VPN

### Le rôle des RD et RT dans une L3VPN

Dans une architecture MPLS L3VPN, le **Route Distinguisher (RD)** est ajouté au préfixe IPv4 pour produire une route VPN-IPv4 distincte. Deux sites qui utilisent tous les deux `10.10.10.0/24` peuvent ainsi annoncer des routes VPN qui ne sont pas identiques dans la famille d’adresses VPNv4. Le RD n’est pas un filtre de sécurité et il ne détermine pas à lui seul dans quelles VRF la route sera importée.

Le **Route Target (RT)** est une communauté étendue utilisée pour gouverner l’export et l’import des routes VPN. Un PE exporte des routes avec un ou plusieurs RT ; une VRF distante est éligible à l’import si sa politique d’import correspond à un RT attaché à la route. Les politiques doivent être conçues ensemble : un RD unique est généralement recommandé par VRF pour la lisibilité opérationnelle, mais le choix de RD et la politique RT répondent à deux questions différentes.

Dans une L3VPN MPLS classique, la pile de labels porte l’information nécessaire à l’acheminement dans le cœur et à l’identification de la route ou du contexte VPN au PE de sortie. Les détails de label et de transport dépendent de l’architecture (par exemple LDP, RSVP-TE ou Segment Routing). Ces mécanismes sont distincts de la VRF-Lite locale.


**VRF-Lite** est une expression souvent employée pour désigner la séparation locale des tables VRF sans construire un réseau MPLS L3VPN de fournisseur entre équipements. L’équipement maintient plusieurs domaines de routage ; les routes se propagent par configuration statique ou par des protocoles configurés dans chaque contexte, selon les capacités de la plateforme.

Dans **MPLS L3VPN**, les routeurs PE utilisent également des VRF, mais la distribution de routes entre sites s’appuie généralement sur MP-BGP et des attributs comme le Route Distinguisher (RD) et les Route Targets (RT). Le transport utilise un mécanisme de tunnel ou de labels. Les routeurs P du cœur n’ont pas besoin d’apprendre toutes les routes client. Une VRF sur un routeur n’implique donc pas à elle seule qu’un VPN MPLS inter-sites est opérationnel.

**Schéma 5 — Ordre de configuration d’une interface**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Ordre de configuration d’une interface"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Ordre de configuration d’une interface</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Préparer la VRF avant d’affecter une interface, puis configurer ses adresses.</text><rect x="45" y="112" width="245" height="100" rx="14" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="45" y="112" width="7" height="100" rx="3" fill="#4ea3ff" stroke="none"/><text x="63" y="141" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">1. Définir la VRF</text><text x="63" y="167" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">vrf definition CLIENT-A</text><line x1="290" y1="162" x2="349" y2="162" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="349.0,162.0 339.8,168.0 339.8,156.0" fill="#4ea3ff"/><rect x="349" y="112" width="245" height="100" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="349" y="112" width="7" height="100" rx="3" fill="#37d6c1" stroke="none"/><text x="367" y="141" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">2. Affecter l’interface</text><text x="367" y="167" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">vrf forwarding CLIENT-A</text><line x1="594" y1="162" x2="653" y2="162" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="653.0,162.0 643.8,168.0 643.8,156.0" fill="#37d6c1"/><rect x="653" y="112" width="262" height="100" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="653" y="112" width="7" height="100" rx="3" fill="#ffbd59" stroke="none"/><text x="671" y="141" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">3. Reconfigurer L3</text><text x="671" y="167" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">ip address …</text><rect x="140" y="250" width="680" height="74" rx="14" fill="#351d2a" stroke="#ff7185" stroke-width="2"/><rect x="140" y="250" width="7" height="74" rx="3" fill="#ff7185" stroke="none"/><text x="158" y="279" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Attention : changer la VRF d’une interface peut retirer son adresse IP</text><text x="158" y="305" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Sauvegarder la configuration et planifier une fenêtre de changement.</text></svg>

## 6. Créer une VRF sur Cisco IOS XE

Exemple indicatif de définition d’une VRF. La syntaxe varie avec la famille logicielle et le matériel ; certaines fonctions, comme RD, RT et les address-families, sont liées à des scénarios plus larges que la simple isolation locale.

```text
configure terminal
vrf definition CLIENT-A
 description Domaine de routage du client A
 address-family ipv4
 exit-address-family
 address-family ipv6
 exit-address-family
end
show vrf
show vrf detail
```

Sur les plateformes concernées, la définition peut aussi inclure un RD. Dans un déploiement MPLS L3VPN, le RD rend les routes VPN distinctes lorsqu’elles ont un même préfixe IPv4; il **ne** décide **pas** à lui seul dans quelles VRF les routes sont importées. Cette distribution est contrôlée notamment par les Route Targets. Pour une VRF-Lite strictement locale, la nécessité et la syntaxe du RD dépendent de l’OS et du design.

**Schéma 6 — Tables VRF et protocoles de routage**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Tables VRF et protocoles de routage"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Tables VRF et protocoles de routage</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Le même protocole peut avoir des instances distinctes dans plusieurs VRF.</text><rect x="45" y="113" width="200" height="95" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="45" y="113" width="7" height="95" rx="3" fill="#37d6c1" stroke="none"/><text x="63" y="142" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF CLIENT-A</text><text x="63" y="168" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Connected + static</text><rect x="45" y="244" width="200" height="95" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="45" y="244" width="7" height="95" rx="3" fill="#c3a1ff" stroke="none"/><text x="63" y="273" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF CLIENT-B</text><text x="63" y="299" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Connected + OSPF / BGP</text><rect x="355" y="113" width="215" height="95" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="355" y="113" width="7" height="95" rx="3" fill="#37d6c1" stroke="none"/><text x="373" y="142" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">RIB CLIENT-A</text><text x="373" y="168" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">10.1.0.0/16</text><text x="373" y="191" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">192.0.2.0/30</text><rect x="355" y="244" width="215" height="95" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="355" y="244" width="7" height="95" rx="3" fill="#c3a1ff" stroke="none"/><text x="373" y="273" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">RIB CLIENT-B</text><text x="373" y="299" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">10.1.0.0/16</text><text x="373" y="322" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">198.51.100.0/30</text><line x1="245" y1="160" x2="355" y2="160" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="355.0,160.0 345.8,166.0 345.8,154.0" fill="#37d6c1"/><line x1="245" y1="291" x2="355" y2="291" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="355.0,291.0 345.8,297.0 345.8,285.0" fill="#c3a1ff"/><rect x="670" y="160" width="230" height="132" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="670" y="160" width="7" height="132" rx="3" fill="#ffbd59" stroke="none"/><text x="688" y="189" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">Chaque protocole doit être</text><text x="688" y="215" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">associé au bon contexte VRF</text><text x="688" y="238" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">et à la bonne address-family.</text><line x1="570" y1="160" x2="670" y2="198" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="670.0,198.0 659.3,200.4 663.5,189.1" fill="#37d6c1"/><line x1="570" y1="291" x2="670" y2="254" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="670.0,254.0 663.5,262.8 659.3,251.5" fill="#c3a1ff"/></svg>

## 7. Associer une interface à une VRF

Exemple d’affectation d’une interface L3 à une VRF, avec une adresse d’exemple réservée à la documentation :

```text
configure terminal
interface GigabitEthernet0/1
 description Vers le CE du client A
 vrf forwarding CLIENT-A
 ip address 192.0.2.1 255.255.255.252
 no shutdown
end
```

**Attention :** sur plusieurs versions IOS/IOS XE, l’application de `vrf forwarding` à une interface peut supprimer son adresse IP existante. Il faut donc prévoir la fenêtre de changement et reconfigurer l’adresse après l’affectation de la VRF. D’autres systèmes utilisent une syntaxe différente ; vérifie toujours le guide correspondant à l’OS et au modèle.

**Schéma 7 — Route leaking : ouvrir uniquement ce qui est nécessaire**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Route leaking : ouvrir uniquement ce qui est nécessaire"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Route leaking : ouvrir uniquement ce qui est nécessaire</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Le partage inter-VRF requiert une politique explicite et un contrôle des flux.</text><rect x="42" y="130" width="210" height="115" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="42" y="130" width="7" height="115" rx="3" fill="#37d6c1" stroke="none"/><text x="60" y="159" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF USERS</text><text x="60" y="185" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Routes utilisateurs</text><rect x="375" y="130" width="210" height="115" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="375" y="130" width="7" height="115" rx="3" fill="#ffbd59" stroke="none"/><text x="393" y="159" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Service partagé</text><text x="393" y="185" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">DNS / DHCP / NTP</text><rect x="708" y="130" width="210" height="115" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="708" y="130" width="7" height="115" rx="3" fill="#c3a1ff" stroke="none"/><text x="726" y="159" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF SERVERS</text><text x="726" y="185" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Applications internes</text><line x1="252" y1="165" x2="375" y2="165" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="375.0,165.0 365.8,171.0 365.8,159.0" fill="#37d6c1"/><text x="313.5" y="151" fill="#37d6c1" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" text-anchor="middle">route ciblée</text><line x1="585" y1="211" x2="708" y2="211" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="708.0,211.0 698.8,217.0 698.8,205.0" fill="#c3a1ff"/><text x="646.5" y="197" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" text-anchor="middle">politique contrôlée</text><text x="480" y="295" fill="#ff7185" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="middle">Le leaking doit être intentionnel, filtré et documenté.</text><text x="480" y="324" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="middle">Une route importée ne remplace pas les règles de pare-feu.</text></svg>

## 8. Routes et protocoles dans une VRF

### Routes connectées, statiques et par défaut

Une route connectée apparaît lorsque l’interface L3 est opérationnelle et possède une adresse dans le contexte adéquat. Si l’interface est désactivée, si le protocole de ligne est down ou si l’adresse est mal configurée, la route connectée attendue peut être absente. Une route statique dépend de la résolution du next-hop ou d’une interface de sortie appropriée. Pour une route par défaut dans une VRF, la syntaxe IOS XE courante ressemble à :

```text
ip route vrf CLIENT-A 0.0.0.0 0.0.0.0 192.0.2.2
```

Ne l’utilise que si `192.0.2.2` est effectivement joignable dans `CLIENT-A`. Une route statique qui pointe vers un next-hop non résolu ne fournit pas toujours un chemin de transfert exploitable ; le comportement exact dépend de la forme de route et de la plateforme.

### Protocoles dynamiques : quelles questions poser ?

Pour OSPF, EIGRP ou BGP, vérifie d’abord si le système permet l’instance dans la VRF et quelle syntaxe configure l’adresse-family ou le processus. Ensuite, vérifie l’interface d’activation, les paramètres de voisinage, l’authentification, les filtres, les politiques de redistribution et les limites de routes. Le simple fait que le processus soit « up » au niveau global ne prouve pas que des routes sont apprises dans la VRF concernée.

La redistribution entre protocoles doit être limitée. Utilise des route-maps ou mécanismes de filtrage supportés afin de prévenir les boucles, les routes non souhaitées et les pertes de préférence. Le contrôle d’un domaine de routage ne doit pas reposer uniquement sur des métriques implicites.


Les interfaces actives associées à une VRF installent leurs routes connectées dans la table appropriée. Les routes statiques peuvent être définies dans une VRF avec une syntaxe spécifique, par exemple :

```text
ip route vrf CLIENT-A 198.51.100.0 255.255.255.0 192.0.2.2
```

Cet exemple n’est valide que si le next-hop `192.0.2.2` est joignable dans le contexte `CLIENT-A` et si la syntaxe est prise en charge sur le système. Les adresses `198.51.100.0/24` et `192.0.2.0/24` sont des préfixes d’exemple réservés à la documentation.

Un processus de routage global n’alimente pas automatiquement toutes les VRF. Il faut configurer les instances VRF prises en charge, les interfaces correspondantes et les politiques de redistribution nécessaires. Il faut éviter de redistribuer des routes entre contextes sans filtrage explicite.

**Schéma 8 — VRF de management**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="VRF de management"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">VRF de management</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Isoler le chemin d’administration réduit l’exposition, sans remplacer ACL/AAA/SSH.</text><rect x="45" y="118" width="245" height="102" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="45" y="118" width="7" height="102" rx="3" fill="#37d6c1" stroke="none"/><text x="63" y="147" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF MANAGEMENT</text><text x="63" y="173" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">SSH / SNMP / Syslog</text><rect x="45" y="246" width="245" height="102" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="45" y="246" width="7" height="102" rx="3" fill="#c3a1ff" stroke="none"/><text x="63" y="275" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF CLIENTS</text><text x="63" y="301" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Trafic utilisateur</text><rect x="390" y="177" width="190" height="110" rx="14" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="390" y="177" width="7" height="110" rx="3" fill="#4ea3ff" stroke="none"/><text x="408" y="206" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Routeur / switch</text><text x="408" y="232" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Plans de trafic séparés</text><line x1="290" y1="168" x2="390" y2="205" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="390.0,205.0 379.3,207.5 383.5,196.2" fill="#37d6c1"/><line x1="290" y1="296" x2="390" y2="254" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="390.0,254.0 383.9,263.1 379.2,252.0" fill="#c3a1ff"/><rect x="676" y="177" width="242" height="110" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="676" y="177" width="7" height="110" rx="3" fill="#ffbd59" stroke="none"/><text x="694" y="206" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Réseaux de destination</text><text x="694" y="232" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Bastion / NMS</text><text x="694" y="255" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Passerelle dédiée</text><line x1="580" y1="232" x2="676" y2="232" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="676.0,232.0 666.8,238.0 666.8,226.0" fill="#ffbd59"/></svg>

## 9. Route leaking et partage contrôlé

### Exemple de politique de partage

Une entreprise peut avoir `VRF-USERS`, `VRF-SERVERS` et `VRF-MGMT`. Le besoin peut être que les utilisateurs accèdent au DNS et au service d’authentification, mais pas aux réseaux d’administration. La démarche de conception est : identifier les préfixes nécessaires, définir le sens de l’accès, sélectionner un point de contrôle, n’importer que les routes nécessaires, appliquer les politiques de paquet, puis tester explicitement les autorisations et refus attendus.

Dans un réseau à plusieurs équipements, le partage doit être cohérent de bout en bout. Il ne suffit pas d’importer une route dans un seul routeur si le chemin retour n’existe pas. Inversement, un chemin retour peut être présent sans que le trafic soit autorisé. Le routage et la sécurité sont deux contrôles complémentaires.

### Risques de boucles et de propagation excessive

Une route importée depuis `VRF-A` dans `VRF-B`, puis redistribuée vers une source qui la réannonce à `VRF-A`, peut créer une boucle de contrôle ou un chemin inattendu. Les garde-fous incluent des préfix-listes, des route-maps, des communautés de marquage, une séparation des fonctions et une revue des chemins de redistribution. Après chaque changement, valide la table source, la table de destination et le plan de transfert.


Le *route leaking* est l’importation intentionnelle d’un ensemble de routes d’une table à une autre. Il permet, par exemple, à plusieurs VRF d’atteindre des services communs tels que DNS, NTP, PKI ou des serveurs applicatifs. Il peut être réalisé au moyen de mécanismes propres à la plateforme : import/export de routes, routes statiques, route-maps, protocoles dédiés, ou fonctions d’interconnexion de VPN.

Le partage des **routes** n’équivaut pas à l’autorisation d’échanger n’importe quel **paquet**. Il faut définir quels préfixes sont exposés, dans quel sens, par quel next-hop, avec quel contrôle de trafic et quelle journalisation. Un leaking bidirectionnel et large peut créer un chemin inattendu entre environnements normalement séparés. Documente le besoin, limite les routes échangées et teste les chemins de retour.

**Schéma 9 — Séquence de vérification**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Séquence de vérification"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Séquence de vérification</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Une méthode reproductible évite de diagnostiquer la mauvaise table.</text><rect x="36" y="110" width="210" height="100" rx="14" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="36" y="110" width="7" height="100" rx="3" fill="#4ea3ff" stroke="none"/><text x="54" y="139" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Inventaire</text><text x="54" y="165" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">show vrf</text><rect x="270" y="110" width="210" height="100" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="270" y="110" width="7" height="100" rx="3" fill="#37d6c1" stroke="none"/><text x="288" y="139" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Interfaces</text><text x="288" y="165" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">show ip interface brief</text><text x="288" y="188" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">show vrf interfaces</text><rect x="504" y="110" width="210" height="100" rx="14" fill="#1b2440" stroke="#c3a1ff" stroke-width="2"/><rect x="504" y="110" width="7" height="100" rx="3" fill="#c3a1ff" stroke="none"/><text x="522" y="139" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">RIB de la VRF</text><text x="522" y="165" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">show ip route vrf X</text><rect x="738" y="110" width="186" height="100" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="738" y="110" width="7" height="100" rx="3" fill="#ffbd59" stroke="none"/><text x="756" y="139" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">Voisinages</text><text x="756" y="165" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">show ip ospf vrf X…</text><line x1="246" y1="160" x2="270" y2="160" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="270.0,160.0 260.8,166.0 260.8,154.0" fill="#4ea3ff"/><line x1="480" y1="160" x2="504" y2="160" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="504.0,160.0 494.8,166.0 494.8,154.0" fill="#37d6c1"/><line x1="714" y1="160" x2="738" y2="160" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="738.0,160.0 728.8,166.0 728.8,154.0" fill="#c3a1ff"/><text x="480" y="272" fill="#58d68d" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" text-anchor="middle">Vérifier dans le même ordre : VRF → interface → route → protocole → forwarding</text><text x="480" y="304" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="middle">La syntaxe exacte varie selon IOS / IOS XE / NX-OS / IOS XR.</text></svg>

## 10. VRF de management

### Préparer un accès d’urgence

Si la VRF de management traverse un réseau qui peut tomber en panne avec le réseau de production, le plan de gestion peut devenir inaccessible au moment même où il faut dépanner. Les architectures critiques prévoient souvent un chemin d’accès hors bande indépendant, un accès console contrôlé et une procédure de récupération. Ces moyens doivent être protégés et testés ; un port console exposé ou des identifiants partagés annulent une grande partie du bénéfice.

Il faut également vérifier quels services de l’équipement utilisent la VRF de management : source des traps SNMP, syslog, NTP, TACACS+/RADIUS, DNS, collecte de télémétrie et transfert de fichiers. Une interface dans la VRF de management n’assure pas automatiquement que tous les services de l’équipement y utilisent le bon chemin ; de nombreuses fonctions nécessitent une configuration de source ou de VRF propre au service.


Une VRF de management peut isoler logiquement les chemins SSH, SNMP, syslog, NTP et autres flux d’administration. Cette séparation facilite l’utilisation d’un réseau de gestion dédié et peut réduire l’exposition des interfaces d’administration à partir des réseaux utilisateur.

Une VRF de management ne suffit pas à sécuriser un équipement. Il faut aussi des ACL, AAA, SSH correctement configuré, une gestion sûre des secrets, une journalisation centralisée, des mises à jour et un plan de secours lorsque le réseau de management est indisponible. Vérifie également quelles fonctions de contrôle et de management sont prises en charge dans la VRF de gestion sur le modèle considéré.

**Schéma 10 — Protocoles de routage dans une VRF**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Protocoles de routage dans une VRF"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Protocoles de routage dans une VRF</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Un processus global n’alimente pas automatiquement toutes les tables VRF.</text><rect x="42" y="128" width="200" height="112" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="42" y="128" width="7" height="112" rx="3" fill="#37d6c1" stroke="none"/><text x="60" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Interfaces VRF-A</text><text x="60" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Gi0/1 · 192.0.2.1/30</text><rect x="315" y="128" width="200" height="112" rx="14" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="315" y="128" width="7" height="112" rx="3" fill="#4ea3ff" stroke="none"/><text x="333" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">Instance OSPF A</text><text x="333" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">router ospf 10 vrf CLIENT-A</text><rect x="315" y="253" width="200" height="90" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="315" y="253" width="7" height="90" rx="3" fill="#c3a1ff" stroke="none"/><text x="333" y="282" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">Instance OSPF B</text><text x="333" y="308" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">distincte, autre VRF</text><rect x="620" y="128" width="292" height="112" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="620" y="128" width="7" height="112" rx="3" fill="#37d6c1" stroke="none"/><text x="638" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">RIB CLIENT-A</text><text x="638" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">routes apprises dans VRF-A</text><rect x="620" y="253" width="292" height="90" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="620" y="253" width="7" height="90" rx="3" fill="#c3a1ff" stroke="none"/><text x="638" y="282" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">RIB CLIENT-B</text><text x="638" y="308" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">routes apprises dans VRF-B</text><line x1="242" y1="184" x2="315" y2="184" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="315.0,184.0 305.8,190.0 305.8,178.0" fill="#37d6c1"/><line x1="515" y1="184" x2="620" y2="184" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="620.0,184.0 610.8,190.0 610.8,178.0" fill="#4ea3ff"/><line x1="515" y1="298" x2="620" y2="298" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="620.0,298.0 610.8,304.0 610.8,292.0" fill="#c3a1ff"/></svg>

## 11. Laboratoire guidé : deux VRF avec des préfixes identiques

### Objectif
Construire deux contextes sur un routeur de laboratoire. Les deux clients peuvent utiliser le même LAN `10.10.10.0/24`, mais chaque interface d’accès et chaque route restent dans leur VRF respective. Il s’agit d’une démonstration locale de VRF-Lite, pas d’un MPLS L3VPN inter-sites.

### Plan d’adressage

| Élément | VRF | Adresse |
|---|---|---|
| R1 Gi0/1 vers CE-A | CLIENT-A | 192.0.2.1/30 |
| CE-A interface vers R1 | CLIENT-A | 192.0.2.2/30 |
| LAN client A | CLIENT-A | 10.10.10.0/24 |
| R1 Gi0/2 vers CE-B | CLIENT-B | 192.0.2.5/30 |
| CE-B interface vers R1 | CLIENT-B | 192.0.2.6/30 |
| LAN client B | CLIENT-B | 10.10.10.0/24 |

Les adresses de ce tableau sont réservées aux exemples de documentation. Remplace les noms d’interfaces selon ton routeur ou ton émulateur.

**Schéma 11 — Même destination, décisions différentes**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Même destination, décisions différentes"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Même destination, décisions différentes</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Le contexte d’entrée conditionne la recherche ; l’adresse IP seule ne suffit pas.</text><rect x="50" y="110" width="260" height="100" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="50" y="110" width="7" height="100" rx="3" fill="#37d6c1" stroke="none"/><text x="68" y="139" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Client A</text><text x="68" y="165" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Serveur : 10.20.30.40</text><rect x="50" y="246" width="260" height="100" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="50" y="246" width="7" height="100" rx="3" fill="#c3a1ff" stroke="none"/><text x="68" y="275" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">Client B</text><text x="68" y="301" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">Serveur : 10.20.30.40</text><rect x="390" y="110" width="215" height="100" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="390" y="110" width="7" height="100" rx="3" fill="#37d6c1" stroke="none"/><text x="408" y="139" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF-A</text><text x="408" y="165" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">lookup 10.20.30.40</text><rect x="390" y="246" width="215" height="100" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="390" y="246" width="7" height="100" rx="3" fill="#c3a1ff" stroke="none"/><text x="408" y="275" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF-B</text><text x="408" y="301" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">lookup 10.20.30.40</text><line x1="310" y1="160" x2="390" y2="160" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="390.0,160.0 380.8,166.0 380.8,154.0" fill="#37d6c1"/><line x1="310" y1="296" x2="390" y2="296" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="390.0,296.0 380.8,302.0 380.8,290.0" fill="#c3a1ff"/><rect x="685" y="175" width="235" height="110" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="685" y="175" width="7" height="110" rx="3" fill="#ffbd59" stroke="none"/><text x="703" y="204" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">Résultats indépendants</text><text x="703" y="230" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">next-hop A ≠ next-hop B</text><text x="703" y="253" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">selon les routes de chaque VRF</text><line x1="605" y1="160" x2="685" y2="204" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="685.0,204.0 674.0,204.8 679.8,194.3" fill="#37d6c1"/><line x1="605" y1="296" x2="685" y2="249" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="685.0,249.0 680.1,258.9 674.0,248.5" fill="#c3a1ff"/></svg>

## 12. Configuration de laboratoire

Sur IOS XE compatible, la configuration indicative peut commencer ainsi :

```text
configure terminal
vrf definition CLIENT-A
 address-family ipv4
 exit-address-family
vrf definition CLIENT-B
 address-family ipv4
 exit-address-family
!
interface GigabitEthernet0/1
 description Vers CE-A
 vrf forwarding CLIENT-A
 ip address 192.0.2.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/2
 description Vers CE-B
 vrf forwarding CLIENT-B
 ip address 192.0.2.5 255.255.255.252
 no shutdown
end
```

Pour démontrer des routes de destination identiques sans créer de conflit entre VRF, les routes peuvent être installées séparément si les next-hops ou interfaces appropriés sont présents :

```text
ip route vrf CLIENT-A 10.10.10.0 255.255.255.0 192.0.2.2
ip route vrf CLIENT-B 10.10.10.0 255.255.255.0 192.0.2.6
```

Cette configuration est un patron de laboratoire. Elle ne remplace pas la vérification de la syntaxe et de la disponibilité des fonctions sur l’image logicielle choisie. Prévois des interfaces CE ou des next-hops réellement configurés avant de tester.

**Schéma 12 — Inter-VRF et sécurité**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Inter-VRF et sécurité"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Inter-VRF et sécurité</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">La visibilité de routes ne doit pas être confondue avec une autorisation de trafic.</text><rect x="40" y="125" width="195" height="110" rx="14" fill="#302139" stroke="#ff7185" stroke-width="2"/><rect x="40" y="125" width="7" height="110" rx="3" fill="#ff7185" stroke="none"/><text x="58" y="154" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF PROD</text><text x="58" y="180" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">données sensibles</text><rect x="382" y="125" width="195" height="110" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="382" y="125" width="7" height="110" rx="3" fill="#ffbd59" stroke="none"/><text x="400" y="154" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">Pare-feu / policy</text><text x="400" y="180" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">ACL / inspection</text><text x="400" y="203" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">journalisation</text><rect x="725" y="125" width="195" height="110" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="725" y="125" width="7" height="110" rx="3" fill="#37d6c1" stroke="none"/><text x="743" y="154" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">VRF SERVICES</text><text x="743" y="180" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">DNS / NTP / PKI</text><line x1="235" y1="180" x2="382" y2="180" stroke="#ff7185" stroke-width="3" stroke-linecap="round"/><polygon points="382.0,180.0 372.8,186.0 372.8,174.0" fill="#ff7185"/><text x="308.5" y="166" fill="#ff7185" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" text-anchor="middle">flux autorisés</text><line x1="577" y1="180" x2="725" y2="180" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="725.0,180.0 715.8,186.0 715.8,174.0" fill="#37d6c1"/><text x="651.0" y="166" fill="#37d6c1" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" text-anchor="middle">allow-list</text><text x="480" y="285" fill="#ffbd59" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" text-anchor="middle">Le route leaking seul ne garantit ni l’inspection ni la sécurité des paquets.</text></svg>

## 13. Vérifications

Commence par prouver que les deux VRF existent et que les interfaces sont associées au contexte attendu. Vérifie ensuite l’état des interfaces, les routes connectées, les routes statiques et la résolution du next-hop. Enfin, utilise des tests de connectivité qui précisent explicitement la VRF.

Commandes utiles, selon la plateforme :

```text
show vrf
show vrf detail
show ip interface brief
show ip route vrf CLIENT-A
show ip route vrf CLIENT-B
show running-config interface GigabitEthernet0/1
ping vrf CLIENT-A 192.0.2.2
ping vrf CLIENT-B 192.0.2.6
```

Si une commande n’est pas reconnue, recherche l’équivalent du système ciblé plutôt que de supposer que les syntaxes IOS XE, NX-OS et IOS XR sont interchangeables.

**Schéma 13 — Laboratoire : isolation locale avec VRF-Lite**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Laboratoire : isolation locale avec VRF-Lite"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Laboratoire : isolation locale avec VRF-Lite</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Topologie pédagogique. Les adresses de test ne doivent pas être utilisées en production.</text><rect x="42" y="128" width="180" height="105" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="42" y="128" width="7" height="105" rx="3" fill="#37d6c1" stroke="none"/><text x="60" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">CE-A</text><text x="60" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">192.0.2.2/30</text><rect x="305" y="128" width="200" height="105" rx="14" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="305" y="128" width="7" height="105" rx="3" fill="#4ea3ff" stroke="none"/><text x="323" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">R1 / VRF-A</text><text x="323" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">CLIENT-A</text><text x="323" y="206" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">192.0.2.1/30</text><rect x="305" y="252" width="200" height="90" rx="14" fill="#162b42" stroke="#c3a1ff" stroke-width="2"/><rect x="305" y="252" width="7" height="90" rx="3" fill="#c3a1ff" stroke="none"/><text x="323" y="281" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">R1 / VRF-B</text><text x="323" y="307" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">CLIENT-B</text><rect x="660" y="128" width="180" height="105" rx="14" fill="#302139" stroke="#c3a1ff" stroke-width="2"/><rect x="660" y="128" width="7" height="105" rx="3" fill="#c3a1ff" stroke="none"/><text x="678" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" text-anchor="start">CE-B</text><text x="678" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" text-anchor="start">192.0.2.6/30</text><line x1="222" y1="180" x2="305" y2="180" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="305.0,180.0 295.8,186.0 295.8,174.0" fill="#37d6c1"/><line x1="505" y1="180" x2="660" y2="180" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="660.0,180.0 650.8,186.0 650.8,174.0" fill="#4ea3ff"/><text x="582.5" y="166" fill="#4ea3ff" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" text-anchor="middle">interface dans VRF-A</text><line x1="505" y1="294" x2="588" y2="294" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="588.0,294.0 578.8,300.0 578.8,288.0" fill="#c3a1ff"/><rect x="588" y="252" width="332" height="90" rx="14" fill="#182b2a" stroke="#58d68d" stroke-width="2"/><rect x="588" y="252" width="7" height="90" rx="3" fill="#58d68d" stroke="none"/><text x="606" y="281" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">Résultat attendu</text><text x="606" y="307" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">préfixes identiques isolés par VRF</text></svg>

## 14. Dépannage : démarche reproductible

### Mini-arbre de décision

- **Aucune interface dans la VRF :** vérifier l’affectation à la VRF, les SVI, sous-interfaces et l’état de l’interface.
- **Interface présente mais route connectée absente :** vérifier adresse, masque, état opérationnel et address-family.
- **Route connectée présente mais destination absente :** vérifier routes statiques, voisinage dynamique, filtres, redistribution et route par défaut.
- **Route présente mais ping échoue :** confirmer le next-hop, ARP/ND, ACL, pare-feu, MTU et chemin retour ; utiliser un test dont la source et la VRF sont explicites.
- **Une VRF atteint un service partagé mais pas l’inverse :** examiner les routes de retour et la politique de sécurité, pas uniquement la route aller.
- **Problème après modification :** comparer la configuration sauvegardée, `running-config`, l’état des interfaces et les routes apprises ; revenir en arrière si les critères de validation ne sont plus satisfaits.

Conserve un relevé avant/après du changement : interface, table VRF, routes, voisins, tests de connectivité et compteurs d’erreurs. Cela transforme le dépannage en vérification reproductible plutôt qu’en série de commandes aléatoires.


1. **État physique et L2 :** vérifier l’interface, le VLAN, le trunk et le voisin.
2. **Appartenance :** confirmer que la bonne interface est associée à la VRF prévue.
3. **Adresse :** contrôler le masque, le chevauchement, l’adresse du voisin et l’état de l’interface.
4. **RIB :** vérifier que le préfixe apparaît dans la table de la bonne VRF et qu’une route active existe.
5. **Next-hop :** vérifier sa joignabilité dans le contexte approprié et l’entrée ARP/ND si nécessaire.
6. **Plan de contrôle :** pour un routage dynamique, confirmer le voisinage et la présence des routes apprises.
7. **Politique :** vérifier ACL, pare-feu, uRPF, politiques de redistribution et route leaking.
8. **Chemin retour :** une requête peut atteindre la destination sans que le retour soit routable.

Capture les sorties avant et après chaque modification. Évite d’appliquer plusieurs changements simultanément, car ils rendent la cause d’un résultat difficile à identifier.

**Schéma 14 — Arbre de dépannage VRF**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="390" viewBox="0 0 960 390" role="img" aria-label="Arbre de dépannage VRF"><rect x="0" y="0" width="960" height="390" rx="18" fill="#0b1423" stroke="#334b66" stroke-width="2"/><text x="28" y="37" fill="#c3a1ff" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" text-anchor="start">Arbre de dépannage VRF</text><text x="28" y="62" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">Remonter la chaîne dans l’ordre, sans supposer que la table globale est utilisée.</text><rect x="36" y="128" width="170" height="100" rx="14" fill="#162b42" stroke="#4ea3ff" stroke-width="2"/><rect x="36" y="128" width="7" height="100" rx="3" fill="#4ea3ff" stroke="none"/><text x="54" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">1. Lien actif ?</text><text x="54" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">L1 / L2 / line protocol</text><rect x="236" y="128" width="170" height="100" rx="14" fill="#102c38" stroke="#37d6c1" stroke-width="2"/><rect x="236" y="128" width="7" height="100" rx="3" fill="#37d6c1" stroke="none"/><text x="254" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">2. Interface VRF ?</text><text x="254" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">bonne appartenance</text><rect x="436" y="128" width="170" height="100" rx="14" fill="#162b42" stroke="#ffbd59" stroke-width="2"/><rect x="436" y="128" width="7" height="100" rx="3" fill="#ffbd59" stroke="none"/><text x="454" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">3. Route présente ?</text><text x="454" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">bonne RIB / préfixe</text><rect x="636" y="128" width="170" height="100" rx="14" fill="#162b42" stroke="#c3a1ff" stroke-width="2"/><rect x="636" y="128" width="7" height="100" rx="3" fill="#c3a1ff" stroke="none"/><text x="654" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" text-anchor="start">4. Next-hop ?</text><text x="654" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" text-anchor="start">résolution / ARP</text><rect x="820" y="128" width="110" height="100" rx="14" fill="#302139" stroke="#ff7185" stroke-width="2"/><rect x="820" y="128" width="7" height="100" rx="3" fill="#ff7185" stroke="none"/><text x="838" y="157" fill="#f4f7fb" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" text-anchor="start">5. Filtre ?</text><text x="838" y="183" fill="#bdc9d8" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="400" text-anchor="start">ACL / FW</text><line x1="206" y1="178" x2="236" y2="178" stroke="#4ea3ff" stroke-width="3" stroke-linecap="round"/><polygon points="236.0,178.0 226.8,184.0 226.8,172.0" fill="#4ea3ff"/><line x1="406" y1="178" x2="436" y2="178" stroke="#37d6c1" stroke-width="3" stroke-linecap="round"/><polygon points="436.0,178.0 426.8,184.0 426.8,172.0" fill="#37d6c1"/><line x1="606" y1="178" x2="636" y2="178" stroke="#ffbd59" stroke-width="3" stroke-linecap="round"/><polygon points="636.0,178.0 626.8,184.0 626.8,172.0" fill="#ffbd59"/><line x1="806" y1="178" x2="820" y2="178" stroke="#c3a1ff" stroke-width="3" stroke-linecap="round"/><polygon points="820.0,178.0 810.8,184.0 810.8,172.0" fill="#c3a1ff"/><text x="480" y="280" fill="#58d68d" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" text-anchor="middle">Capturer les états avant / après changement et vérifier aussi le plan de contrôle.</text></svg>

## 15. Erreurs classiques

- Configurer une adresse IP puis affecter une VRF sans vérifier si l’OS efface l’adresse.
- Utiliser `show ip route` sans préciser la VRF et conclure à tort que le réseau n’existe pas.
- Croire qu’une VRF est un tunnel chiffré ou une politique pare-feu.
- Confondre VRF-Lite et MPLS L3VPN, ou croire qu’un RD assure l’importation des routes.
- Importer trop de routes avec le route leaking ou redistribuer en boucle.
- Tester seulement dans le sens aller et oublier la route retour.
- Copier une configuration d’un modèle ou d’une version logicielle différente sans vérifier les commandes supportées.

## 16. Quiz corrigé

**1. À quoi sert principalement une VRF ?** À créer des contextes de routage/forwarding distincts sur un même équipement.

**2. Deux VRF peuvent-elles contenir le même préfixe IPv4 ?** Oui, car les tables sont indépendantes. Les systèmes de supervision doivent toutefois conserver le contexte.

**3. VRF-Lite exige-t-elle intrinsèquement MPLS ?** Non. VRF-Lite désigne une segmentation locale des tables sans exiger un cœur MPLS L3VPN.

**4. Un RD contrôle-t-il à lui seul l’importation des routes dans une VRF ?** Non. Dans une MPLS L3VPN, le RD rend la route VPN distincte ; les RT et les politiques de routage déterminent notamment son éligibilité à l’import.

**5. Une route existe dans la table globale : le client VRF peut-il forcément l’utiliser ?** Non. Les tables sont séparées tant qu’un mécanisme explicite de partage ou de fuite de routes n’existe pas.

**6. Pourquoi un ping standard peut-il être trompeur ?** Il peut partir du contexte de routage global au lieu de celui du client.

**7. Quel est le risque d’un route leaking trop large ?** Il peut exposer des préfixes ou créer des chemins non voulus entre domaines.

**8. Quelles vérifications faire en premier lors d’un problème ?** Interface, appartenance VRF, adresse et routes dans la bonne table, puis next-hop, politique et chemin retour.

## 17. Checklist de mise en service

- [ ] Besoin d’isolation documenté : client, application, production ou management.
- [ ] Plan d’adressage et gestion des chevauchements vérifiés.
- [ ] Noms des VRF normalisés et inventoriés.
- [ ] Interfaces affectées à la bonne VRF ; adresses et routes vérifiées après changement.
- [ ] Protocoles de routage et redistribution limités au bon contexte.
- [ ] Route leaking documenté avec préfixes, sens et filtre explicites.
- [ ] ACL/pare-feu et accès d’administration testés indépendamment.
- [ ] Tests de connectivité réalisés par VRF, dans les deux sens.
- [ ] Sauvegarde de configuration et procédure de retour arrière disponibles.
- [ ] Compatibilité des commandes vérifiée pour l’OS et la version de l’équipement.

## 18. Glossaire

- **VRF :** Virtual Routing and Forwarding, instance de routage et de forwarding isolée.
- **VRF-Lite :** segmentation locale VRF sans exiger un cœur MPLS L3VPN.
- **RIB :** base des informations de routage.
- **FIB :** structure de transfert consultée pour envoyer les paquets.
- **RD :** Route Distinguisher, rend les routes VPN distinctes dans une architecture MPLS L3VPN.
- **RT :** Route Target, communauté étendue utilisée pour contrôler l’export et l’import des routes VPN.
- **PE / CE :** Provider Edge / Customer Edge dans une architecture de fournisseur.
- **Route leaking :** partage intentionnel de routes entre contextes de routage.
- **Longest-prefix match :** sélection du préfixe le plus spécifique correspondant à une destination.

## Références techniques

- Cisco, guide de configuration VRF-Lite sur Catalyst 9200 : https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9200/software/release/26-x/configuration_guide/rtng/b_26x_rtng_9200_cg/configuring_vrf_lite.html
- Cisco, VRF-Lite et OSPFv3 / PE-CE : https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-routing/b-ip-routing/m_iro-vrf-lite-pe-ce.html
- RFC 4364, BGP/MPLS IP Virtual Private Networks : https://www.rfc-editor.org/rfc/rfc4364
- Cisco DevNet, modèle VRF IOS XE : https://netascode.cisco.com/docs/data_models/iosxe/device/vrf/

> **Note de compatibilité :** les commandes présentées sont des exemples pédagogiques. Vérifie la syntaxe exacte, les fonctions prises en charge, la famille de matériel et la version logicielle dans le guide correspondant. En particulier, l’ordre d’affectation d’une VRF à une interface peut entraîner la suppression de l’adresse IP préexistante sur certains systèmes.
