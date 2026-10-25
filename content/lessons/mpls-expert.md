# MPLS & VRF — Niveau Expert

> **Objectif :** concevoir, exploiter et dépanner une infrastructure MPLS L3VPN à grande échelle, en comprenant les dépendances entre routage client, distribution des labels, MP-BGP, transport, haute disponibilité, QoS et OAM. Ce niveau prolonge les cours Débutant et Intermédiaire ; il ne répète pas toute l’introduction aux labels, RD/RT et VRF.

> **Avertissement de plateforme :** les exemples de CLI sont pédagogiques et principalement inspirés d’IOS/IOS XE. IOS XR, NX-OS, les versions récentes et les autres fournisseurs peuvent différer. Toujours valider les commandes, la compatibilité des fonctionnalités et les procédures de rollback en laboratoire avant un changement de production.

## 1. Positionnement et objectifs d’expertise

Un ingénieur expert MPLS ne se contente pas de faire monter une session BGP ou de voir une route dans une VRF. Il doit démontrer la cohérence de toute la chaîne : le CE annonce le bon préfixe ; le PE l’accepte dans la bonne VRF ; les politiques exportent la route sous forme VPNv4/VPNv6 ; les RT permettent l’import voulu ; le next-hop est joignable ; un label de transport atteint le PE distant ; le label de service sélectionne la bonne sortie ; la MTU et la QoS restent cohérentes ; et le chemin retour est valide.

À la fin de ce cours, tu dois savoir :

- concevoir un plan d’adressage, d’AS, de loopbacks, de RD et de RT exploitable à grande échelle ;
- lire la chaîne RIB/FIB, BGP VPNv4/VPNv6, LIB/LFIB, LDP ou SR-MPLS ;
- dimensionner la réflexion BGP, limiter la diffusion des routes VPN et analyser les effets des politiques ;
- comparer Inter-AS Option A, B et C et justifier un choix ;
- raisonner sur la convergence et distinguer FRR local, TI-LFA, RSVP-TE FRR et BGP PIC ;
- diagnostiquer les défauts MTU, QoS, asymétrie, fragmentation, label stack et chemin de retour ;
- structurer la validation, les tests de panne, la collecte de preuves et le rollback.

## 2. Carte mentale du service et séparation des responsabilités

Une VPN MPLS L3 est un service de routage privé construit au-dessus d’un réseau fournisseur. Le client échange des routes avec un PE, tandis que MP-BGP distribue les routes VPN entre PE. Le réseau de transport conduit les paquets vers le PE de sortie ; les routeurs P n’ont normalement pas besoin de connaître chaque préfixe client. Le détail standard du modèle est décrit dans la RFC 4364.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-label="Architecture de référence : le service VPN et le transport MPLS"><rect x="1" y="1" width="958" height="358" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Architecture de référence : le service VPN et le transport MPLS</text><rect x="35" y="130" width="130" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="100.0" y="159" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">CE-A</text><text x="100.0" y="181" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">site client</text><rect x="210" y="120" width="150" height="100" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="285.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE1</text><text x="285.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VRF + label VPN</text><rect x="405" y="110" width="150" height="120" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="480.0" y="139" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">P1</text><text x="480.0" y="161" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">transport LFIB</text><rect x="600" y="120" width="150" height="100" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="675.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE2</text><text x="675.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VRF + label VPN</text><rect x="795" y="130" width="130" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="860.0" y="159" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">CE-B</text><text x="860.0" y="181" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">site client</text><line x1="165" y1="170" x2="210" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="210.0,170.0 199.0,164.0 199.0,176.0" fill="#6dd3ce"/><text x="187.5" y="155" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">IP</text><line x1="360" y1="170" x2="405" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="405.0,170.0 394.0,164.0 394.0,176.0" fill="#6dd3ce"/><text x="382.5" y="155" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">pile MPLS</text><line x1="555" y1="170" x2="600" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="600.0,170.0 589.0,164.0 589.0,176.0" fill="#6dd3ce"/><text x="577.5" y="155" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">swap / PHP</text><line x1="750" y1="170" x2="795" y2="170" stroke="#6dd3ce" stroke-width="3"/><polygon points="795.0,170.0 784.0,164.0 784.0,176.0" fill="#6dd3ce"/><text x="772.5" y="155" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">IP</text><text x="480" y="280" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f5c46a">PE : contexte client et décision VPN</text><text x="480" y="307" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="400" fill="#c8d7e8">P : commute le transport ; ne connaît normalement pas les routes client</text></svg>

### 2.1 Séparer les domaines de panne

| Domaine | Symptôme typique | Preuve à collecter |
|---|---|---|
| Accès CE–PE | le préfixe n’est pas appris localement | voisinage, interface, route source, filtres |
| RIB VRF / politiques | route locale présente mais non exportée | RIB VRF, politique BGP, RD/RT |
| MP-BGP | route non reçue ou non sélectionnée | famille VPNv4/v6, RR, communautés étendues, next-hop |
| Transport | BGP a appris la route, mais le PE distant n’est pas joignable dans le cœur | IGP, LDP/SR, reachability loopback, LFIB |
| Plan de données | route et labels existent mais le trafic échoue | capture, counters, MTU, disposition de label |
| Chemin retour / sécurité | ping asymétrique, certaines applications échouent | route retour, ACL/firewall, QoS, uRPF selon design |

## 3. Dépendances du plan de contrôle et du plan de données

Le fonctionnement global n’est pas une unique convergence. Plusieurs mécanismes distincts ont leurs propres états et temporisations : IGP pour la reachability des loopbacks PE ; LDP ou SR-MPLS pour l’identité de transport ; MP-BGP pour les routes VPN ; protocole CE–PE pour les préfixes locaux ; et mécanismes de forwarding pour appliquer les labels en matériel. Les temps de convergence peuvent donc s’additionner, se chevaucher ou être masqués par des mécanismes de protection.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="355" viewBox="0 0 960 355" role="img" aria-label="Dépendances du plan de contrôle"><rect x="1" y="1" width="958" height="353" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Dépendances du plan de contrôle</text><rect x="65" y="90" width="220" height="65" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="175.0" y="119" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">IGP / reachability</text><text x="175.0" y="141" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">loopbacks PE et chemins</text><rect x="370" y="90" width="220" height="65" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="119" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">LDP ou SR-MPLS</text><text x="480.0" y="141" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">label de transport</text><rect x="675" y="90" width="220" height="65" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="785.0" y="119" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">MP-BGP VPNv4/v6</text><text x="785.0" y="141" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">routes + label de service</text><line x1="285" y1="122" x2="370" y2="122" stroke="#6dd3ce" stroke-width="3"/><polygon points="370.0,122.0 359.0,116.0 359.0,128.0" fill="#6dd3ce"/><text x="327.5" y="106" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">reachability</text><line x1="590" y1="122" x2="675" y2="122" stroke="#6dd3ce" stroke-width="3"/><polygon points="675.0,122.0 664.0,116.0 664.0,128.0" fill="#6dd3ce"/><text x="632.5" y="106" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">transport résolu</text><rect x="225" y="220" width="510" height="70" rx="12" fill="#102f36" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">RIB VRF + plan de données</text><text x="480.0" y="271" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">route installée ET labels/next-hop opérationnels</text><line x1="785" y1="155" x2="660" y2="220" stroke="#c6a0ff" stroke-width="3"/><polygon points="660.0,220.0 672.5,220.2 667.0,209.6" fill="#c6a0ff"/><text x="722.5" y="190" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">RT, next-hop, label VPN</text><line x1="480" y1="155" x2="480" y2="220" stroke="#6dd3ce" stroke-width="3"/><polygon points="480.0,220.0 486.0,209.0 474.0,209.0" fill="#6dd3ce"/><text x="480.0" y="190" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">LSP vers le PE distant</text><text x="480" y="327" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Une session BGP établie ne garantit pas à elle seule le transfert de paquets.</text></svg>

### 3.1 Une route peut être « up » et le service down

Une session VPNv4 établie ne prouve pas que les routes requises sont annoncées, importées ou installées. De même, une route présente dans la VRF n’apporte pas la preuve que son next-hop est résolu ou que la pile de labels est programmable. La méthode experte consiste à poser une question différente à chaque couche :

1. **Origine :** quel protocole fournit le préfixe client ? Le filtre l’autorise-t-il ?
2. **Contexte local :** la route est-elle réellement installée dans la VRF cible ?
3. **Export :** le PE associe-t-il le RD correct et les RT attendus ?
4. **Distribution :** MP-BGP annonce-t-il le NLRI à la bonne famille/voisin ?
5. **Import distant :** le RT correspond-il à une politique d’import, et la route passe-t-elle les autres vérifications ?
6. **Transport :** le next-hop BGP est-il joignable par le cœur et existe-t-il un LSP vers lui ?
7. **Forwarding :** les labels de transport et de service sont-ils cohérents avec la LFIB ?
8. **Retour :** le réseau distant possède-t-il une route de retour et les politiques permettent-elles les deux sens ?

## 4. Empilement des labels et lecture du chemin

Pour une L3VPN classique avec transport MPLS, le paquet transporte souvent un label externe de transport et un label interne de service VPN. Le label externe conduit vers le PE d’egress. Le label VPN identifie la route/service ou le contexte de sortie selon le modèle d’allocation. Le routeur P commute normalement le label externe et n’inspecte pas la route client. À l’approche du PE egress, le label externe peut être retiré par PHP ; il s’agit du label VPN qui reste alors visible au PE. L’utilisation d’Explicit Null ou d’autres comportements dépend de la politique de label et des capacités configurées.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-label="Pile de labels : transport externe et service VPN"><rect x="1" y="1" width="958" height="348" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Pile de labels : transport externe et service VPN</text><text x="170" y="85" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">À l’entrée du PE</text><text x="485" y="85" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Dans le cœur</text><text x="795" y="85" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">À la sortie du cœur</text><rect x="55" y="115" width="230" height="145" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="170.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Paquet client</text><text x="170.0" y="166" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">IP destination + payload</text><rect x="365" y="115" width="230" height="145" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Labels empilés</text><text x="480.0" y="166" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">transport </text><text x="480.0" y="183" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8"> VPN </text><text x="480.0" y="200" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8"> IP/payload</text><rect x="675" y="115" width="230" height="145" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="790.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Après PHP possible</text><text x="790.0" y="166" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VPN </text><text x="790.0" y="183" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8"> IP/payload</text><line x1="285" y1="187" x2="365" y2="187" stroke="#6dd3ce" stroke-width="3"/><polygon points="365.0,187.0 354.0,181.0 354.0,193.0" fill="#6dd3ce"/><text x="325.0" y="170" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">push labels</text><line x1="595" y1="187" x2="675" y2="187" stroke="#6dd3ce" stroke-width="3"/><polygon points="675.0,187.0 664.0,181.0 664.0,193.0" fill="#6dd3ce"/><text x="635.0" y="170" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">swap / pop transport</text><text x="480" y="298" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Le label externe conduit vers le PE d’egress ; le label interne identifie le service VPN.</text><text x="480" y="322" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="400" fill="#c8d7e8">PHP, explicit-null et propagation TTL dépendent du design et de la configuration.</text></svg>

### 4.1 Lecture sans confondre label et préfixe

- Un **label de transport** répond : vers quel LSR/PE le paquet doit-il être amené dans le backbone ?
- Un **label VPN** répond : une fois au PE distant, quel service ou quelle sortie client est associé au paquet ?
- Un **RD** rend unique la NLRI VPN, notamment lorsque deux clients utilisent la même adresse IPv4.
- Un **RT** est une communauté étendue utilisée par les politiques d’export/import de routes VPN. Ce n’est pas un label et ce n’est pas un mécanisme complet de sécurité des données.

Le label VPN n’est pas nécessairement alloué à chaque préfixe dans toutes les implémentations : certaines plateformes ou configurations peuvent utiliser des labels par VRF/interface ou d’autres modes. Dans un diagnostic, ne déduis pas le comportement exact uniquement de la théorie ; lis la configuration et les commandes de labels de la plateforme.

### 4.2 LFIB, LIB et RIB

La **RIB** décrit les routes candidates/choisies ; la **FIB** est la structure de forwarding IP ; la **LIB** contient les associations de labels apprises/attribuées par le mécanisme de distribution ; la **LFIB** décrit les opérations de transfert MPLS effectivement pertinentes pour le plan de données. Une route peut exister dans la RIB et ne pas être transférable par MPLS si les dépendances de label ou le next-hop ne sont pas opérationnels.

Exemple de chaîne de vérification générique (adapter la syntaxe exacte au système) :

```text
show ip route <loopback_PE_distant>
show mpls ldp neighbor
show mpls forwarding-table
show bgp vpnv4 unicast all summary
show bgp vpnv4 unicast all <prefixe>
show ip route vrf <VRF> <prefixe>
show ip cef vrf <VRF> <destination> detail
```

Sur IOS XR, les commandes sont différentes (`show route vrf`, `show bgp vpnv4 unicast`, `show mpls forwarding`, etc.). Il faut aussi tenir compte du nom de la famille d’adresses activée. Ne copie pas mécaniquement les commandes IOS XE sur IOS XR/NX-OS.

## 5. RD, RT et politiques à l’échelle

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="355" viewBox="0 0 960 355" role="img" aria-label="RD et RT : deux fonctions différentes"><rect x="1" y="1" width="958" height="353" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">RD et RT : deux fonctions différentes</text><rect x="55" y="100" width="245" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="177.5" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">RD 65000:101</text><text x="177.5" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">rend la NLRI VPN unique</text><rect x="355" y="100" width="245" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="477.5" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Préfixe 10.10.10.0/24</text><text x="477.5" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">devient NLRI VPNv4</text><rect x="655" y="100" width="245" height="90" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="777.5" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">RT 65000:10</text><text x="777.5" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">contrôle import / export</text><line x1="300" y1="145" x2="355" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="355.0,145.0 344.0,139.0 344.0,151.0" fill="#6dd3ce"/><text x="327.5" y="130" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">combine</text><line x1="600" y1="145" x2="655" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="655.0,145.0 644.0,139.0 644.0,151.0" fill="#6dd3ce"/><text x="627.5" y="130" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">attribut étendu</text><rect x="165" y="230" width="630" height="70" rx="12" fill="#102f36" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="259" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Politique d’import VRF</text><text x="480.0" y="281" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">seules les routes ayant des RT acceptés sont candidates</text><line x1="778" y1="190" x2="690" y2="230" stroke="#c6a0ff" stroke-width="3"/><polygon points="690.0,230.0 702.5,230.9 697.5,220.0" fill="#c6a0ff"/><text x="734.0" y="215" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">RT matching</text><text x="480" y="329" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Le RD n’est pas une ACL ; le RT n’est ni un label ni une garantie de sécurité complète.</text></svg>

### 5.1 Stratégie RD

Le RD permet de distinguer des NLRI VPN qui partagent le même préfixe IPv4/IPv6. Il doit être planifié pour être unique là où il faut rendre les routes distinctes. Une convention souvent lisible est `ASN:identifiant`, avec un identifiant stable par PE/VRF ou par contexte de route. Ce choix dépend de la politique de l’opérateur ; il ne faut pas traiter la chaîne comme une norme universelle.

Éviter de réutiliser par erreur le même RD sur des routes que l’architecture exige de distinguer. Une route VPNv4 est essentiellement un couple RD + préfixe, avec les attributs BGP associés. Changer un RD peut provoquer un retrait/réannonce de routes et un effet opérationnel ; la migration doit donc être planifiée et testée.

### 5.2 Stratégie RT

Les RT définissent la distribution des routes entre VRF. Un modèle simple peut utiliser un RT par client, un modèle plus fin plusieurs RT pour séparer import/export ou partager un service commun. Le risque majeur n’est pas seulement l’absence d’import : c’est aussi un import trop large, qui rend accessibles des routes non prévues.

Exemple conceptuel :

| VRF | Export RT | Import RT | But |
|---|---|---|---|
| CLIENT-A | `65000:100` | `65000:100`, `65000:900` | sites A et service DNS partagé |
| CLIENT-B | `65000:200` | `65000:200`, `65000:900` | sites B et service DNS partagé |
| SERVICES | `65000:900` | RT spécifiques nécessaires | serveurs partagés, avec politiques d’accès dédiées |

Ce tableau n’implique pas que tout échange autorisé par RT soit sûr. Le firewall, les ACL et le filtrage de routes doivent limiter les flux et préfixes à ce qui est requis.

### 5.3 Route Target Constraint

Quand beaucoup de VRF sont présentes, diffuser toutes les routes VPN à tous les PE peut coûter des ressources de contrôle et de mémoire. RT-Constrain (RFC 4684) permet de signaler les RT dont un PE a besoin et de limiter certaines diffusions de routes VPN à travers le réseau BGP, sous réserve du support et d’une configuration cohérente sur les équipements et route reflectors. Ce n’est pas un filtre de données : il optimise la diffusion de routes.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-label="RT-Constrain : limiter la diffusion des routes VPN"><rect x="1" y="1" width="958" height="348" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">RT-Constrain : limiter la diffusion des routes VPN</text><rect x="45" y="105" width="190" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="140.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE producteur</text><text x="140.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">annonce des RT</text><rect x="380" y="105" width="200" height="80" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Route Reflector</text><text x="480.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">apprend les RT demandés</text><rect x="725" y="105" width="190" height="80" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="820.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE consommateur</text><text x="820.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">importe RT 65000:20</text><line x1="235" y1="145" x2="380" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="380.0,145.0 369.0,139.0 369.0,151.0" fill="#6dd3ce"/><text x="307.5" y="130" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VPN route</text><line x1="725" y1="166" x2="580" y2="166" stroke="#c6a0ff" stroke-width="3"/><polygon points="580.0,166.0 591.0,172.0 591.0,160.0" fill="#c6a0ff"/><text x="652.5" y="190" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">RT membership</text><rect x="180" y="230" width="600" height="65" rx="12" fill="#102f36" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="259" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Gain attendu</text><text x="480.0" y="281" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">moins de diffusion inutile sur de grands déploiements</text><text x="480" y="326" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">RT-Constrain réduit la propagation ; il ne remplace pas les politiques de sécurité.</text></svg>

### 5.4 Route reflectors : erreurs expertes fréquentes

Un RR facilite la scalabilité du plan de contrôle, mais ne garantit ni la résolution du next-hop, ni l’import RT, ni l’installation d’une route. Contrôler au minimum :

- l’activation de la famille VPNv4/VPNv6 sur les clients et le RR ;
- la propagation des communautés étendues, dont les RT ;
- la reachability du next-hop PE, ou le comportement de next-hop prévu par le design ;
- l’architecture de redondance RR et les politiques de réflexion ;
- les éventuelles limitations de chemins multiples, de politiques, de mémoire ou d’update processing ;
- les effets d’un retrait de route, d’une réinitialisation de session et d’une bascule vers un RR secondaire.

Une architecture à deux RR ne suffit pas si les PE n’ont pas une conception cohérente de cluster/identifiants, ou si les politiques et sessions sont différentes sans raison voulue.

## 6. Inter-AS L3VPN : choisir une frontière explicite

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="385" viewBox="0 0 960 385" role="img" aria-label="Inter-AS L3VPN : comparer les options A, B et C"><rect x="1" y="1" width="958" height="383" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Inter-AS L3VPN : comparer les options A, B et C</text><rect x="35" y="105" width="270" height="125" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="170.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Option A</text><text x="170.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VRF-à-VRF</text><text x="170.0" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">simple ; état par client</text><rect x="70" y="260" width="200" height="60" rx="12" fill="#102033" stroke="#35516f" stroke-width="2"/><text x="170.0" y="289" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">État / complexité</text><text x="170.0" y="311" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VRF par service</text><rect x="345" y="105" width="270" height="125" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Option B</text><text x="480.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VPNv4 entre ASBR</text><text x="480.0" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">routes VPN + labels</text><rect x="380" y="260" width="200" height="60" rx="12" fill="#102033" stroke="#35516f" stroke-width="2"/><text x="480.0" y="289" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">État / complexité</text><text x="480.0" y="311" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VPNv4 au bord</text><rect x="655" y="105" width="270" height="125" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="790.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Option C</text><text x="790.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">PE-à-PE VPNv4</text><text x="790.0" y="173" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">transport inter-AS labelisé</text><rect x="690" y="260" width="200" height="60" rx="12" fill="#102033" stroke="#35516f" stroke-width="2"/><text x="790.0" y="289" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">État / complexité</text><text x="790.0" y="311" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">labels et reachability</text><text x="480" y="356" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Le choix dépend de la confiance entre AS, du passage à l’échelle et des exigences de séparation.</text></svg>

Les options Inter-AS A, B et C ne sont pas de simples niveaux de performance : elles changent les informations échangées à la frontière, l’état conservé par les ASBR et le modèle de confiance entre opérateurs.

| Option | Modèle | Avantages | Coûts / risques |
|---|---|---|---|
| **A — VRF-à-VRF** | Une session de routage et une VRF ou sous-interface par service à la frontière | Facile à raisonner ; séparation explicite par VRF | Beaucoup d’état par client sur ASBR ; administration et mise à l’échelle plus lourdes |
| **B — VPNv4 entre ASBR** | Échange de routes VPNv4 et de labels entre ASBR ; la frontière participe au transfert VPN | Moins de VRF par client à la frontière ; passage à l’échelle supérieur | Complexité du plan de contrôle/labels, politique RT et confiance renforcées |
| **C — PE-à-PE** | Les PE échangent les routes VPNv4/v6 ; la reachability des PE et des labels est étendue entre AS | Sépare davantage le plan de service de la frontière physique ; utile pour de grandes architectures | Labeled reachability, next-hop, propagation et sécurité beaucoup plus exigeants |

Les détails précis des labels, next-hops et procédures varient selon le modèle et les versions. Un design Option C peut utiliser des procédures de BGP labeled-unicast et des sessions MP-BGP appropriées ; il ne faut pas supposer que le simple échange d’une route VPNv4 suffit. Les deux opérateurs doivent définir une politique de filtrage, de propagation des labels et de traitement des défaillances.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-label="Trajet d’un paquet VPN dans une architecture inter-AS"><rect x="1" y="1" width="958" height="378" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Trajet d’un paquet VPN dans une architecture inter-AS</text><rect x="30" y="115" width="160" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="110.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">PE-A</text><text x="110.0" y="166" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">push VPN + transport</text><rect x="215" y="115" width="160" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="295.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">ASBR-A</text><text x="295.0" y="166" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">Option selon design</text><rect x="400" y="115" width="160" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="480.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">ASBR-B</text><text x="480.0" y="166" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">labels / route VPN</text><rect x="585" y="115" width="160" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="665.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">PE-B</text><text x="665.0" y="166" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">pop service label</text><rect x="770" y="115" width="160" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="850.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">CE-B</text><text x="850.0" y="166" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">paquet IP</text><line x1="190" y1="160" x2="215" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="215.0,160.0 204.0,154.0 204.0,166.0" fill="#6dd3ce"/><line x1="375" y1="160" x2="400" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="400.0,160.0 389.0,154.0 389.0,166.0" fill="#6dd3ce"/><line x1="560" y1="160" x2="585" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="585.0,160.0 574.0,154.0 574.0,166.0" fill="#6dd3ce"/><line x1="745" y1="160" x2="770" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="770.0,160.0 759.0,154.0 759.0,166.0" fill="#6dd3ce"/><rect x="105" y="245" width="750" height="72" rx="12" fill="#102033" stroke="#35516f" stroke-width="2"/><text x="480.0" y="274" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Point critique</text><text x="480.0" y="296" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">route de contrôle ≠ chemin de transport ; valider les labels à chaque frontière</text><text x="480" y="348" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Option A, B et C ne traitent pas la frontière inter-AS de la même manière.</text></svg>

### 6.1 Dossier de conception Inter-AS

Avant le changement, documenter :

1. AS locaux et distants, adresses de peering, authentification et TTL multihop s’il est utilisé ;
2. familles d’adresses échangées (IPv4 unicast, VPNv4/VPNv6, labeled-unicast selon le design) ;
3. RT autorisés, préfixes ou clients autorisés, maximum-prefix et filtrage entrant/sortant ;
4. méthode de transport du label jusqu’au PE de sortie ;
5. comportement si le peering tombe, si les labels se retirent ou si le chemin retour devient asymétrique ;
6. MTU, QoS, OAM, journalisation, contacts d’exploitation et procédure de rollback.

## 7. Convergence, protection locale et continuité des services

Convergence rapide n’est pas un seul mécanisme. Il faut distinguer la détection du défaut, la recalculation de l’IGP, la mise à jour de la distribution des labels, la mise à jour BGP et la programmation de la FIB. Une route VPN peut rester présente dans BGP pendant que le transport vers son next-hop est momentanément invalide ; une protection locale peut masquer une panne au plan de contrôle mais ne répare pas toutes les défaillances de bout en bout.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" role="img" aria-label="Convergence : chemin primaire et protection locale"><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Convergence : chemin primaire et protection locale</text><rect x="45" y="115" width="150" height="70" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="120.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Ingress PE</text><text x="120.0" y="166" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">trafic entrant</text><rect x="300" y="85" width="145" height="70" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="372.5" y="114" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">P1</text><text x="372.5" y="136" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">chemin primaire</text><rect x="610" y="85" width="145" height="70" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="682.5" y="114" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">P2</text><text x="682.5" y="136" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">chemin primaire</text><rect x="300" y="235" width="145" height="70" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="372.5" y="264" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">P3</text><text x="372.5" y="286" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">chemin de secours</text><rect x="610" y="235" width="145" height="70" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="682.5" y="264" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">P4</text><text x="682.5" y="286" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">réparation locale</text><rect x="795" y="155" width="125" height="70" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="857.5" y="184" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Egress PE</text><text x="857.5" y="206" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">destination</text><line x1="195" y1="140" x2="300" y2="120" stroke="#6dd3ce" stroke-width="3"/><polygon points="300.0,120.0 288.1,116.2 290.3,128.0" fill="#6dd3ce"/><text x="247.5" y="103" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">primaire</text><line x1="445" y1="120" x2="610" y2="120" stroke="#6dd3ce" stroke-width="3"/><polygon points="610.0,120.0 599.0,114.0 599.0,126.0" fill="#6dd3ce"/><text x="527.5" y="103" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">primaire</text><line x1="755" y1="120" x2="795" y2="175" stroke="#6dd3ce" stroke-width="3"/><polygon points="795.0,175.0 793.4,162.6 783.7,169.6" fill="#6dd3ce"/><text x="775.0" y="146" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">primaire</text><line x1="370" y1="155" x2="370" y2="235" stroke="#c6a0ff" stroke-width="3"/><polygon points="370.0,235.0 376.0,224.0 364.0,224.0" fill="#c6a0ff"/><text x="370.0" y="201" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">protection</text><line x1="445" y1="270" x2="610" y2="270" stroke="#c6a0ff" stroke-width="3"/><polygon points="610.0,270.0 599.0,264.0 599.0,276.0" fill="#c6a0ff"/><text x="527.5" y="254" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">détour local</text><line x1="755" y1="270" x2="850" y2="225" stroke="#c6a0ff" stroke-width="3"/><polygon points="850.0,225.0 837.5,224.3 842.6,235.1" fill="#c6a0ff"/><text x="802.5" y="252" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">retour au chemin</text><text x="480" y="340" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">FRR RSVP-TE, TI-LFA et BGP PIC ont des mécanismes et prérequis différents.</text></svg>

### 7.1 Les principaux mécanismes

- **BFD** permet la détection rapide d’une perte de connectivité entre deux points de forwarding ; ses intervalles doivent tenir compte de la capacité de la plateforme, du nombre de sessions et du risque de fausses détections.
- **LDP–IGP synchronization** évite, dans les designs qui l’utilisent et le supportent, que l’IGP attire le trafic sur un lien avant que les labels nécessaires soient prêts.
- **RSVP-TE FRR** peut offrir une réparation locale de LSP pour les chemins RSVP-TE et dispose de procédures décrites par les RFC 3209 et 4090.
- **TI-LFA** et d’autres mécanismes de réparation locale sont liés à SR/IGP et dépendent de la topologie, des contraintes et du support réel.
- **BGP PIC** vise à accélérer la bascule de forwarding pour certains scénarios BGP ; ses prérequis et son fonctionnement dépendent de l’implémentation et de la famille VPN.

Ne jamais annoncer un objectif de convergence uniquement parce qu’une fonctionnalité est activée. Mesurer les pertes, le temps de détection, le temps de restauration du plan de données et les effets sur les applications avec un générateur de trafic et des sondes adaptées.

### 7.2 Plan de test de convergence

| Test | Mesure | Critère à définir avant le test |
|---|---|---|
| coupure d’un lien de cœur | perte de paquets et temps de bascule | seuil de perte/durée approuvé |
| arrêt d’un voisin LDP / segment | disparition label / restauration du chemin | pas de blackhole durable |
| perte d’une session CE–PE | impact sur préfixes locaux | routes retirées correctement ; chemin alternatif effectif |
| perte d’un RR | continuité contrôle BGP | sessions et routes conservées/reconvergées selon design |
| retrait d’une route VPN | délai de retrait et de forwarding | aucune route résiduelle non voulue |

## 8. LDP, RSVP-TE et SR-MPLS : choix de transport

### 8.1 LDP avec IGP

LDP distribue les labels associés aux FEC selon ses règles et les labels disponibles en aval. Dans un réseau classique, l’IGP fournit les chemins et LDP les labels de transport. Le diagnostic doit corréler reachability IP des loopbacks, voisinages LDP, bindings, LIB et LFIB. Si le plan IP converge plus vite que le plan de labels, un blackhole temporaire ou persistant peut se produire.

### 8.2 RSVP-TE

RSVP-TE permet de signaler des LSP explicites et, selon la configuration, de prendre en compte des contraintes de bande passante ou de chemin. Cela apporte du contrôle d’ingénierie, mais aussi plus d’état opérationnel : réservations, objets TE, chemins primaires/secondaires et état des tunnels. RFC 3209 décrit les extensions RSVP pour tunnels LSP ; RFC 4090 décrit des extensions de fast reroute. Toujours confirmer le support et le modèle de contrôle de la plateforme.

### 8.3 SR-MPLS

Segment Routing peut utiliser MPLS labels pour représenter des segments, souvent des Segment Identifiers (SIDs). Le plan IGP et le mécanisme de contrôle doivent être cohérents avec la définition et la portée des SIDs, l’indexation, le plan d’adressage, les contraintes et la programmation du forwarding. SR-MPLS modifie le modèle de distribution des segments par rapport à LDP, mais n’élimine pas les sujets de reachability, MTU, label stack, QoS et OAM.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-label="LDP–IGP Synchronization : éviter le trou de forwarding"><rect x="1" y="1" width="958" height="348" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">LDP–IGP Synchronization : éviter le trou de forwarding</text><rect x="55" y="100" width="240" height="75" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="175.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">IGP annonce le lien</text><text x="175.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">coût attractif mais pas de label</text><rect x="360" y="100" width="240" height="75" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="480.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">LDP session down</text><text x="480.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">pas de LSP complet</text><rect x="665" y="100" width="240" height="75" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="785.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Risque</text><text x="785.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">trafic attiré puis abandonné</text><line x1="295" y1="137" x2="360" y2="137" stroke="#c6a0ff" stroke-width="3"/><polygon points="360.0,137.0 349.0,131.0 349.0,143.0" fill="#c6a0ff"/><text x="327.5" y="122" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">état</text><line x1="600" y1="137" x2="665" y2="137" stroke="#c6a0ff" stroke-width="3"/><polygon points="665.0,137.0 654.0,131.0 654.0,143.0" fill="#c6a0ff"/><text x="632.5" y="122" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">conséquence</text><rect x="175" y="230" width="610" height="70" rx="12" fill="#102f36" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="259" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Principe de synchronisation</text><text x="480.0" y="281" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">ne pas utiliser le lien IGP avant que la distribution des labels soit prête</text><line x1="480" y1="175" x2="480" y2="230" stroke="#6dd3ce" stroke-width="3"/><polygon points="480.0,230.0 486.0,219.0 474.0,219.0" fill="#6dd3ce"/><text x="480.0" y="207" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">signal de contrôle</text><text x="480" y="328" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">À valider selon plateforme ; ce mécanisme ne remplace pas la surveillance de bout en bout.</text></svg>

### 8.4 Matrice de choix

| Critère | LDP | RSVP-TE | SR-MPLS |
|---|---|---|---|
| objectif initial | LSP aligné sur IGP | chemin explicite / ingénierie TE | politique de chemin basée sur segments |
| état de contrôle | sessions et bindings LDP | état RSVP par LSP et réservations selon design | SIDs et politique SR, état suivant architecture |
| contrôle de chemin | principalement IGP | explicite et contraint | politique / segments, dépend de l’orchestrateur et du support |
| protection | mécanismes IGP, LDP-IGP sync, autres | RSVP-TE FRR selon configuration | TI-LFA et autres mécanismes compatibles |
| opérations | relativement simple | riche mais plus complexe à exploiter | exige rigueur dans les SIDs, politiques et OAM |

Cette table est un guide conceptuel, pas une matrice complète de fonctionnalités. Une décision réelle inclut capacités des ASIC, versions logicielles, télémétrie, échelle, licences, compétences, outils de configuration et plan de migration.

## 9. QoS, MTU et traitement des labels

### 9.1 MTU MPLS

Chaque label MPLS ajoute 4 octets à la pile. Un paquet avec deux labels nécessite donc au moins 8 octets de marge supplémentaire par rapport à la taille IP correspondante, sans compter les éventuelles en-têtes de couche 2, VLAN, GRE/IP-in-IP ou d’autres encapsulations. Il faut raisonner sur l’MTU réelle du lien et de chaque équipement du trajet, pas seulement sur la valeur de l’interface d’accès.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-label="MTU : suivre l’encapsulation de bout en bout"><rect x="1" y="1" width="958" height="348" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">MTU : suivre l’encapsulation de bout en bout</text><rect x="45" y="100" width="180" height="85" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="135.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">MTU Ethernet</text><text x="135.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">1500 octets IP</text><rect x="285" y="100" width="180" height="85" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="375.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">+ 1 label</text><text x="375.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">4 octets</text><rect x="525" y="100" width="180" height="85" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="615.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">+ 2 labels</text><text x="615.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">8 octets</text><rect x="765" y="100" width="150" height="85" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="840.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Underlay</text><text x="840.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">MTU nécessaire</text><line x1="225" y1="142" x2="285" y2="142" stroke="#6dd3ce" stroke-width="3"/><polygon points="285.0,142.0 274.0,136.0 274.0,148.0" fill="#6dd3ce"/><text x="255.0" y="127" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">encapsuler</text><line x1="465" y1="142" x2="525" y2="142" stroke="#6dd3ce" stroke-width="3"/><polygon points="525.0,142.0 514.0,136.0 514.0,148.0" fill="#6dd3ce"/><text x="495.0" y="127" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">empiler</text><line x1="705" y1="142" x2="765" y2="142" stroke="#6dd3ce" stroke-width="3"/><polygon points="765.0,142.0 754.0,136.0 754.0,148.0" fill="#6dd3ce"/><text x="735.0" y="127" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">vérifier</text><rect x="135" y="230" width="690" height="65" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="480.0" y="259" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Risque</text><text x="480.0" y="281" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">petits paquets fonctionnels ; grands paquets / DF cassés</text><text x="480" y="325" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Inclure Ethernet/VLAN, tags MPLS, tunnels et éventuels en-têtes additionnels.</text></svg>

La situation « petit ping OK, gros flux bloqué » doit faire suspecter MTU, fragmentation, PMTUD filtré ou des différences de traitement par chemin. Tester avec des tailles croissantes et le bit DF lorsque pertinent, capturer les messages ICMP de fragmentation nécessaire/packet too big, et mesurer la MTU sur chaque segment.

### 9.2 QoS et MPLS Traffic Class

Le champ Traffic Class (TC, historiquement EXP dans les documents plus anciens) porte une classification utilisée par les politiques QoS MPLS. Les mappings DSCP ↔ TC ne doivent pas être supposés automatiques : le PE d’entrée peut marquer les labels, les nœuds P peuvent utiliser TC pour sélectionner les files, et le PE de sortie peut appliquer une politique de propagation/restauration. La cohérence doit être documentée pour chaque classe et direction.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="365" viewBox="0 0 960 365" role="img" aria-label="QoS sur MPLS : classifier, marquer, transporter et traiter"><rect x="1" y="1" width="958" height="363" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">QoS sur MPLS : classifier, marquer, transporter et traiter</text><rect x="40" y="120" width="150" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="115.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Ingress PE</text><text x="115.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">classifie IP</text><rect x="230" y="120" width="150" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="305.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Push label</text><text x="305.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">copie / mappe TC</text><rect x="420" y="120" width="150" height="90" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="495.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Cœur P</text><text x="495.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">queues et scheduler</text><rect x="610" y="120" width="150" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="685.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Egress PE</text><text x="685.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">mappe / décapsule</text><rect x="800" y="120" width="150" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="875.0" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Sortie CE</text><text x="875.0" y="171" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">politique locale</text><line x1="190" y1="165" x2="230" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="230.0,165.0 219.0,159.0 219.0,171.0" fill="#6dd3ce"/><text x="210.0" y="150" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">TC / DSCP</text><line x1="380" y1="165" x2="420" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="420.0,165.0 409.0,159.0 409.0,171.0" fill="#6dd3ce"/><text x="400.0" y="150" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">TC / DSCP</text><line x1="570" y1="165" x2="610" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="610.0,165.0 599.0,159.0 599.0,171.0" fill="#6dd3ce"/><text x="590.0" y="150" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">TC / DSCP</text><line x1="760" y1="165" x2="800" y2="165" stroke="#6dd3ce" stroke-width="3"/><polygon points="800.0,165.0 789.0,159.0 789.0,171.0" fill="#6dd3ce"/><text x="780.0" y="150" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">TC / DSCP</text><rect x="105" y="250" width="750" height="65" rx="12" fill="#102033" stroke="#35516f" stroke-width="2"/><text x="480.0" y="279" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">À contrôler</text><text x="480.0" y="301" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">mapping DSCP ↔ MPLS TC · politique de file · congestion · policer / shaper</text><text x="480" y="342" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Ne pas supposer que DSCP et MPLS Traffic Class ont une correspondance automatique.</text></svg>

Mesures recommandées : débit par classe, drops de file, policer/shaper, jitter, latence, DSCP/TC avant et après le cœur, ainsi que la priorité accordée à BFD et aux protocoles de contrôle. Une politique qui protège le trafic de contrôle au prix d’une starvation des autres classes peut causer des symptômes difficiles à reproduire.

## 10. OAM, validation et observabilité

OAM MPLS cherche à valider la continuité et le chemin de transfert, au-delà de l’existence d’une route. LSP ping / traceroute et les messages MPLS echo sont définis par les mécanismes OAM appropriés (notamment RFC 8029). BFD peut surveiller la connectivité selon le type de session, le support et l’encapsulation. Les commandes et la profondeur de vérification varient selon l’OS et le modèle du routeur.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-label="OAM MPLS : vérifier le chemin, pas seulement les routes"><rect x="1" y="1" width="958" height="358" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">OAM MPLS : vérifier le chemin, pas seulement les routes</text><rect x="45" y="100" width="200" height="85" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="145.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Plan de contrôle</text><text x="145.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">IGP · BGP · labels</text><rect x="380" y="100" width="200" height="85" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Plan de données</text><text x="480.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">LFIB · TTL · MTU</text><rect x="715" y="100" width="200" height="85" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="815.0" y="129" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">OAM / sondes</text><text x="815.0" y="151" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">LSP ping / trace · BFD</text><line x1="245" y1="142" x2="380" y2="142" stroke="#6dd3ce" stroke-width="3"/><polygon points="380.0,142.0 369.0,136.0 369.0,148.0" fill="#6dd3ce"/><text x="312.5" y="127" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">indique la route</text><line x1="580" y1="142" x2="715" y2="142" stroke="#6dd3ce" stroke-width="3"/><polygon points="715.0,142.0 704.0,136.0 704.0,148.0" fill="#6dd3ce"/><text x="647.5" y="127" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">teste le transfert</text><rect x="115" y="230" width="730" height="70" rx="12" fill="#102f36" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="259" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">Trois preuves distinctes</text><text x="480.0" y="281" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">route présente · LSP opérant · application de bout en bout</text><text x="480" y="330" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Les commandes exactes et la profondeur OAM varient selon l’OS et le matériel.</text></svg>

### 10.1 Les quatre preuves de service

1. **Route de contrôle :** préfixe appris dans la VRF, exporté, reçu et importé où nécessaire.
2. **Transport :** next-hop distant joignable, LSP valide et label de transport programmé.
3. **Forwarding :** pile et actions LFIB cohérentes, MTU suffisante, QoS correcte.
4. **Application :** trafic aller-retour, ports attendus, latence/perte/jitter acceptables, chemins retour valides.

Conserver les horodatages et les compteurs avant/après le test. Un `ping` réussi depuis un PE vers une loopback ne teste pas nécessairement le routage et les politiques de la VRF. Un ping sourcé dans la VRF ne valide pas toutes les applications ni les directions. Il faut choisir des sondes qui représentent réellement le service.

## 11. Sécurité et séparation des clients

MPLS L3VPN fournit une séparation logique par contexte de routage et politiques d’import/export ; il n’apporte pas, à lui seul, le chiffrement cryptographique du trafic. Si le modèle de menace nécessite la confidentialité sur le transport, étudier IPsec ou d’autres mécanismes adaptés au service et à la performance. La sécurité passe également par la protection du plan de contrôle, le filtrage des annonces CE–PE, les limites de préfixes, la gestion des communautés RT, la protection des sessions et le contrôle des interfaces de gestion.

### Contrôles de sécurité à intégrer

- sessions BGP authentifiées lorsque supportées et planifiées ; filtrage des voisins et des familles ;
- limites `maximum-prefix`, filtres de préfixes et politiques de communauté ;
- aucun `redistribute connected/static` sans filtre strict et justification ;
- limitation de l’accès aux interfaces de management et journalisation des changements ;
- validation en revue à deux personnes des opérations de route leaking ;
- tests d’isolation entre VRF, tests d’exception de service partagé et de chemin retour ;
- stockage sûr des configurations et secrets, sauvegarde testée et plan de rollback.

### 11.1 Tests d’isolation

Pour chaque pair de VRF, documenter les flux autorisés et interdits. Teste la connectivité depuis la source dans la VRF appropriée, la résolution DNS, les services partagés, les routes de retour, les chemins alternatifs après panne et les règles de pare-feu. Un simple ping échoué ne constitue pas la preuve d’une isolation complète, pas plus qu’un ping réussi ne suffit à justifier un modèle d’accès applicatif large.

## 12. Laboratoire de synthèse : deux clients, deux PE, deux chemins

### 12.1 Topologie et hypothèses

Fournisseur AS `65000` : PE1 (`192.0.2.1/32`), P1, P2 et PE2 (`192.0.2.2/32`). OSPF ou IS-IS assure la reachability des loopbacks. Le transport du lab utilise LDP pour simplifier, puis on discutera de SR-MPLS séparément. PE1 et PE2 utilisent MP-BGP VPNv4. Un route reflector peut être ajouté ensuite. Client A possède deux sites ; Client B annonce volontairement le même préfixe qu’A pour démontrer l’isolation par VRF.

| Élément | CLIENT-A | CLIENT-B |
|---|---|---|
| RD PE1 (exemple) | `65000:101` | `65000:201` |
| RD PE2 (exemple) | `65000:102` | `65000:202` |
| RT export/import (exemple) | `65000:10` | `65000:20` |
| LAN site 1 | `10.10.0.0/16` | `10.10.0.0/16` |
| LAN site 2 | `10.20.0.0/16` | `10.20.0.0/16` |

Les plages sont réservées au laboratoire et les adresses d’exemple ne doivent pas être copiées sans plan d’adressage complet.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-label="Route Reflectors : scalabilité du contrôle BGP"><rect x="1" y="1" width="958" height="348" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Route Reflectors : scalabilité du contrôle BGP</text><rect x="70" y="235" width="160" height="65" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="150.0" y="264" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE1</text><text x="150.0" y="286" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">client RR</text><rect x="400" y="105" width="160" height="75" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="134" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">RR1</text><text x="480.0" y="156" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VPNv4 / VPNv6</text><rect x="730" y="235" width="160" height="65" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="810.0" y="264" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE2</text><text x="810.0" y="286" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">client RR</text><rect x="400" y="235" width="160" height="65" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="480.0" y="264" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="700" fill="#f8fafc">PE3</text><text x="480.0" y="286" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">client RR</text><line x1="230" y1="250" x2="400" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="400.0,160.0 387.5,159.8 393.1,170.4" fill="#6dd3ce"/><text x="315.0" y="205" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">session iBGP</text><line x1="730" y1="250" x2="560" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="560.0,160.0 566.9,170.4 572.5,159.8" fill="#6dd3ce"/><text x="645.0" y="205" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">session iBGP</text><line x1="480" y1="180" x2="480" y2="235" stroke="#6dd3ce" stroke-width="3"/><polygon points="480.0,235.0 486.0,224.0 474.0,224.0" fill="#6dd3ce"/><text x="480.0" y="210" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">réflexion contrôlée</text><line x1="230" y1="267" x2="400" y2="267" stroke="#5a82b1" stroke-width="3"/><polygon points="400.0,267.0 389.0,261.0 389.0,273.0" fill="#5a82b1"/><line x1="560" y1="267" x2="730" y2="267" stroke="#5a82b1" stroke-width="3"/><polygon points="730.0,267.0 719.0,261.0 719.0,273.0" fill="#5a82b1"/><text x="480" y="325" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Vérifier cluster-ID, next-hop, communautés étendues, AF activées et politiques.</text></svg>

### 12.2 Ordre de déploiement

1. Préparer les loopbacks et le plan d’adressage du transport.
2. Établir l’IGP et vérifier les loopbacks PE de bout en bout.
3. Activer le mécanisme de labels (LDP dans le lab) et vérifier les bindings/LFIB.
4. Créer les VRF avec RD/RT documentés et associer les interfaces côté CE.
5. Configurer le routage CE–PE avec des filtres explicites.
6. Activer MP-BGP VPNv4 entre PE ou via les RR, propager les communautés étendues requises.
7. Vérifier les routes exportées et importées, puis les labels et la résolution du next-hop.
8. Tester le trafic bidirectionnel par VRF ; valider l’isolation entre CLIENT-A et CLIENT-B.
9. Couper un lien à la fois et mesurer la perte et le temps de récupération.
10. Tester la MTU, les classes QoS, la supervision, les sauvegardes et le rollback.

### 12.3 Exemple de VRF IOS XE moderne

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
 ip address 192.0.2.9 255.255.255.252
 no shutdown
```

Sur certaines versions, l’association VRF à une interface peut effacer l’adresse IP existante ; appliquer la VRF puis réassigner l’adresse selon la documentation de l’image cible. Les commandes ci-dessus ne représentent pas toute la configuration MP-BGP/LDP et ne doivent pas être interprétées comme un déploiement complet.

### 12.4 Vérifications représentatives

```text
show ip route <loopback_PE_distant>
show mpls ldp neighbor
show mpls forwarding-table
show bgp vpnv4 unicast all summary
show bgp vpnv4 unicast all <prefixe>
show ip route vrf CLIENT-A
show ip cef vrf CLIENT-A <destination> detail
ping vrf CLIENT-A <destination> source <source_VRF>
```

Utilise les commandes équivalentes documentées pour IOS XR ou une autre plateforme. Sur le routeur P, l’absence de préfixes client dans la RIB globale est généralement normale pour le modèle L3VPN classique.

## 13. Dépannage expert : arbre de décision

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" role="img" aria-label="Dépannage expert : progression par couches"><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Dépannage expert : progression par couches</text><rect x="40" y="90" width="260" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="170.0" y="119" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">1. CE–PE</text><text x="170.0" y="141" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">route client ?</text><rect x="345" y="90" width="260" height="78" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="475.0" y="119" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">2. VRF / RT</text><text x="475.0" y="141" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">import correct ?</text><rect x="650" y="90" width="260" height="78" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="780.0" y="119" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">3. MP-BGP</text><text x="780.0" y="141" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">next-hop + label VPN ?</text><rect x="40" y="220" width="260" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="170.0" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">4. Transport</text><text x="170.0" y="271" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">IGP + LDP/SR ?</text><rect x="345" y="220" width="260" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="475.0" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">5. LFIB / MTU</text><text x="475.0" y="271" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">labels + taille ?</text><rect x="650" y="220" width="260" height="78" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="780.0" y="249" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">6. Retour</text><text x="780.0" y="271" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">asymétrie / filtrage ?</text><line x1="300" y1="129" x2="345" y2="129" stroke="#6dd3ce" stroke-width="3"/><polygon points="345.0,129.0 334.0,123.0 334.0,135.0" fill="#6dd3ce"/><line x1="605" y1="129" x2="650" y2="129" stroke="#6dd3ce" stroke-width="3"/><polygon points="650.0,129.0 639.0,123.0 639.0,135.0" fill="#6dd3ce"/><line x1="780" y1="168" x2="780" y2="220" stroke="#c6a0ff" stroke-width="3"/><polygon points="780.0,220.0 786.0,209.0 774.0,209.0" fill="#c6a0ff"/><text x="780.0" y="198" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">suite</text><line x1="650" y1="259" x2="605" y2="259" stroke="#6dd3ce" stroke-width="3"/><polygon points="605.0,259.0 616.0,265.0 616.0,253.0" fill="#6dd3ce"/><line x1="345" y1="259" x2="300" y2="259" stroke="#6dd3ce" stroke-width="3"/><polygon points="300.0,259.0 311.0,265.0 311.0,253.0" fill="#6dd3ce"/><text x="480" y="336" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Récolter l’état avant changement ; modifier une variable à la fois ; vérifier le retour arrière.</text></svg>

### 13.1 La route est dans la VRF locale mais absente à distance

Vérifier dans l’ordre : route dans la RIB VRF source ; filtre CE–PE ; redistribution éventuelle ; RD et RT export ; famille MP-BGP activée ; politiques BGP ; communautés étendues conservées ; état du RR ; réception du NLRI au PE distant ; RT import et capacité de next-hop. Ne pas commencer par les labels si la route n’est même pas distribuée par le plan de contrôle.

### 13.2 La route est visible à distance, trafic bloqué

Vérifier le next-hop global, le transport vers la loopback distante, le label de transport, le label VPN, la LFIB et la MTU. Ensuite tester un paquet issu de la VRF, capturer les compteurs d’interface et analyser le chemin retour. Si seules les grandes tailles échouent, tester la MTU/PMTUD avant de changer BGP.

### 13.3 Incident après une modification RT

La modification RT peut modifier la portée de distribution et d’import. Comparer l’état avant/après : routes VPN annoncées, RT attachés, routes installées dans chaque VRF, changements de nombre de préfixes, et routes retour. Restaurer le RT antérieur si les critères du rollback sont atteints ; ne pas compenser un RT trop large par une route statique non documentée.

### 13.4 Incident au niveau du cœur

Si plusieurs VPN sans relation échouent simultanément, privilégier les causes partagées : IGP, LDP/SR, MTU de cœur, congestion, P/PE commun, route reflector ou changement de politique global. Si une seule VRF est affectée, investiguer plus tôt les RT, le routage CE–PE, les interfaces et les politiques propres au client.

## 14. Études de cas corrigées

### Cas 1 — BGP Established, route VPN absente

**Observation :** les sessions sont établies, mais le préfixe du client n’apparaît pas sur PE2.

**Démarche :** vérifier la route dans la VRF de PE1, le voisinage CE–PE, la politique d’export, la famille VPNv4, la propagation des communautés RT et les politiques du RR. Puis vérifier la réception sur PE2 et l’import RT. La session établie ne garantit pas l’annonce de chaque NLRI.

### Cas 2 — Routes dans la VRF, aucune donnée ne passe

**Démarche :** vérifier reachability du next-hop PE, LDP/SR, LFIB et label stack. Sur PE egress, confirmer la résolution de la route vers CE. Tester les deux sens, y compris le firewall et les politiques de retour. Si les pings petits passent mais pas les gros, cibler MTU et PMTUD.

### Cas 3 — Inter-AS Option B : seule une partie des clients tombe

**Démarche :** comparer les RT import/export et les routes VPNv4 au niveau de chaque ASBR ; inspecter les labels annoncés et les politiques sur la frontière ; vérifier que le next-hop/transport reste valide. Une panne partielle peut être liée à une politique par client plutôt qu’au transport global.

### Cas 4 — Coupure de lien et longue perte de paquets

**Démarche :** corréler l’instant de détection, les changements IGP, les voisins LDP, la LFIB, l’update BGP et la programmation FIB. Vérifier que les chemins de secours existent réellement et que leur capacité est suffisante. Répéter le test avec sondes horodatées et compteurs de drops ; ne pas se fier aux seuls journaux de convergence.

### Cas 5 — Deux clients ayant des préfixes identiques communiquent par erreur

**Démarche :** analyser le route leaking, l’import RT et les tables VRF. Rechercher un RT commun trop large, une redistribution vers la RIB globale ou une passerelle partagée configurée au-delà du besoin. Prouver l’isolation par des tests croisés dans les deux sens et documenter toute exception.

## 15. Plan de changement et rollback

### Avant

- sauvegarder running/startup et la configuration du voisinage ;
- relever la base de référence : sessions, nombre de préfixes, CPU/mémoire, erreurs interfaces, latence et perte ;
- définir le périmètre, le risque, la fenêtre, le responsable et le critère précis d’abandon ;
- valider la compatibilité logicielle et la syntaxe exacte sur le modèle/OS ;
- établir une séquence courte, contrôlée, avec vérification après chaque étape.

### Pendant

- ne modifier qu’une variable de conception à la fois ;
- surveiller l’état de MP-BGP, les routes VRF, la LFIB, la MTU et les sondes de service ;
- comparer les résultats à la baseline, pas seulement à une impression de connectivité ;
- si un critère de rollback est franchi, arrêter les changements et restaurer le dernier état connu comme bon.

### Après

- exécuter les tests de validation et de non-régression ;
- archiver les configurations et sorties de commandes avant/après ;
- mettre à jour les diagrammes, RD/RT, plan de routage, inventaire et runbook ;
- noter les écarts, la cause racine si connue, et les actions préventives.

## 16. Exercices corrigés

**Exercice 1.** Pourquoi deux clients peuvent-ils utiliser `10.10.0.0/16` sans collision dans la même infrastructure MPLS ?

**Correction :** parce que les routes résident dans des VRF séparées et sont distinguées dans MP-BGP par le RD et les politiques d’import/export. Cette séparation disparaît si le design introduit volontairement un échange de routes ou un leaking incorrect.

**Exercice 2.** Quelle est la différence entre RD et RT ?

**Correction :** le RD rend la NLRI VPN unique. Les RT guident l’export/import des routes VPN. Aucun des deux n’est un label ; les RT ne remplacent pas les ACL/firewalls.

**Exercice 3.** Une route VPNv4 est reçue sur PE2 mais n’apparaît pas dans la VRF. Citer quatre pistes.

**Correction :** RT non importé ; next-hop non résolu ; route rejetée par politique ; route non sélectionnée/admissible ; famille ou VRF mal configurée. Vérifier les sorties réelles avant de changer les labels.

**Exercice 4.** Le ping des loopbacks PE fonctionne, mais la VPN ne transporte pas le trafic. Quelle vérification suit ?

**Correction :** vérifier les labels LDP/SR, la LFIB, le label VPN, le routage de sortie dans la VRF distante et la route retour. La reachability IP des loopbacks n’atteste pas le plan de données MPLS complet.

**Exercice 5.** Quel est l’intérêt de RT-Constrain ?

**Correction :** limiter la diffusion des routes VPN selon les RT demandés par les PE, lorsque le mécanisme est supporté et correctement déployé. Il réduit une partie de la charge de distribution, mais ne remplace pas les filtres de sécurité.

**Exercice 6.** Pour quoi BFD ne suffit-il pas à garantir une convergence de service rapide ?

**Correction :** BFD accélère la détection d’une panne de chemin/session. Les mises à jour de routage, la distribution de labels, la sélection BGP, la programmation FIB et le chemin retour peuvent ajouter du délai. Il faut mesurer la perte réelle de bout en bout.

## 17. Quiz final

1. Quel élément identifie normalement le service VPN dans la pile de labels à l’arrivée au PE de sortie ?
2. Pourquoi le label externe est-il distinct du label VPN ?
3. Quel est le rôle du RT-Constrain ?
4. Quel modèle Inter-AS utilise une VRF par service à la frontière ?
5. Quel modèle échange VPNv4/labels au niveau des ASBR ?
6. Pourquoi la présence d’une route en BGP ne prouve-t-elle pas qu’elle est transférable ?
7. Pourquoi faut-il tester la MTU avec des tailles de paquet différentes ?
8. Quelles preuves distinguent control plane, transport, forwarding et application ?
9. BFD, LDP-IGP synchronization et BGP PIC résolvent-ils le même problème ?
10. MPLS L3VPN chiffre-t-il intrinsèquement le trafic client ?

### Corrigé

1. Le label VPN/service, selon le modèle d’allocation de labels de la plateforme.
2. Le label externe amène le paquet au PE d’egress ; le label interne identifie le service ou la sortie VPN.
3. Limiter la diffusion des routes VPN selon les RT auxquels les PE sont intéressés.
4. Option A.
5. Option B.
6. Parce que next-hop, RT, sélection de route, labels, LFIB ou programmation matérielle peuvent manquer.
7. Pour repérer les problèmes de MTU/fragmentation/PMTUD que les petits paquets ne révèlent pas.
8. Route importée, LSP/transport valide, labels/FIB valides, puis test d’application bidirectionnel.
9. Non : ils agissent sur la détection, la synchronisation ou l’accélération du forwarding dans des contextes différents.
10. Non. L’isolation logique n’équivaut pas au chiffrement cryptographique.

## 18. Checklist d’architecture avant production

- [ ] Plan d’adressage, loopbacks, AS, RD et RT revus et documentés.
- [ ] Politique d’import/export des VRF validée avec un diagramme des flux autorisés.
- [ ] IGP convergent et reachability des loopbacks validée depuis chaque PE.
- [ ] LDP ou SR-MPLS validé : labels, LFIB et chemins de transport.
- [ ] MP-BGP VPNv4/VPNv6 validé : familles, RR, communautés étendues, next-hops.
- [ ] Routage CE–PE filtré et limites de préfixes définies.
- [ ] Inter-AS validé avec routes/labels/MTU et procédures de panne testées.
- [ ] QoS, MTU, OAM et sondes de bout en bout validées dans chaque direction.
- [ ] Tests de perte d’un lien, d’un PE, d’une session BGP et d’un RR documentés.
- [ ] Procédure de changement, rollback, sauvegarde et escalade testée.
- [ ] Sécurité du plan de contrôle et des interfaces de gestion revue.
- [ ] Documentation, inventaire, matrices RT/VRF et runbooks mis à jour.

## 19. Glossaire

- **ASBR :** routeur frontière entre systèmes autonomes.
- **BFD :** mécanisme de détection de défaillance de chemin.
- **CE / PE / P :** Customer Edge, Provider Edge et routeur de cœur Provider.
- **FIB / LFIB :** structures de transfert IP et MPLS.
- **FRR :** Fast Reroute.
- **LDP :** Label Distribution Protocol.
- **LSP :** Label Switched Path.
- **MP-BGP :** BGP multiprotocole, utilisé notamment pour VPNv4/VPNv6.
- **RD :** Route Distinguisher, qui rend la NLRI VPN unique.
- **RT :** Route Target, communauté étendue d’export/import.
- **RR :** Route Reflector.
- **RIB / LIB :** bases de routes et de bindings de labels.
- **SR-MPLS :** Segment Routing avec labels MPLS.
- **TC :** champ Traffic Class dans l’en-tête MPLS.
- **VRF :** Virtual Routing and Forwarding.

## 20. Approfondissement expert : allocation du label VPN et conséquences de forwarding

Le choix de l’allocation des labels influence l’échelle, le mode de traitement du paquet, la lecture de la LFIB et la manière dont le PE d’egress identifie la sortie. Dans les conceptions L3VPN classiques, le PE peut annoncer un label associé à un préfixe VPN ou utiliser un label commun à un contexte de transfert (par exemple une VRF ou une interface), selon les possibilités de l’implémentation et le mode configuré. Ces modèles n’ont pas la même consommation de labels et ne sont pas interchangeables sans vérifier le traitement exact du routeur.

### 20.1 Label par préfixe et label partagé

Un modèle par préfixe permet de faire correspondre finement une route VPN à un traitement de sortie ; il peut cependant consommer davantage d’entrées de labels. Un label partagé par VRF ou interface peut économiser des ressources, mais demande au PE d’egress de faire une recherche IP additionnelle dans le contexte approprié, selon le modèle précis. Les noms et capacités disponibles varient selon les familles de matériel et les versions.

Les questions de design à poser sont :

- combien de routes VPN sont prévues et combien de labels locaux le PE peut-il programmer ?
- la plateforme utilise-t-elle des labels par préfixe, par VRF ou plusieurs modes ?
- que montrent les routes VPNv4 reçues, les bindings BGP et la LFIB ?
- après un changement de mode, faut-il retirer/réannoncer des routes et reprogrammer le forwarding ?
- le comportement après PHP, explicit-null ou label de service reste-t-il identique sur le chemin de sortie ?

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" role="img" aria-label="Cycle de vie d’une route VPN : de l’origine au forwarding"><rect x="1" y="1" width="958" height="368" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Cycle de vie d’une route VPN : de l’origine au forwarding</text><rect x="35" y="100" width="165" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="117.5" y="127" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">CE annonce</text><text x="117.5" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">préfixe client</text><rect x="245" y="100" width="165" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="327.5" y="127" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">PE / VRF</text><text x="327.5" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">route locale</text><rect x="455" y="100" width="165" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="537.5" y="127" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">MP-BGP</text><text x="537.5" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">RD + RT + label</text><rect x="665" y="100" width="165" height="90" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="747.5" y="127" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">PE distant</text><text x="747.5" y="149" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">import RT / next-hop</text><rect x="395" y="235" width="170" height="70" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="480.0" y="262" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">LFIB / FIB</text><text x="480.0" y="284" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">programmation data</text><line x1="200" y1="145" x2="245" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="245.0,145.0 235.0,140.0 235.0,150.0" fill="#6dd3ce"/><text x="222.5" y="130" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">CE–PE</text><line x1="410" y1="145" x2="455" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="455.0,145.0 445.0,140.0 445.0,150.0" fill="#6dd3ce"/><text x="432.5" y="130" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">export</text><line x1="620" y1="145" x2="665" y2="145" stroke="#6dd3ce" stroke-width="3"/><polygon points="665.0,145.0 655.0,140.0 655.0,150.0" fill="#6dd3ce"/><text x="642.5" y="130" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VPNv4/v6</text><line x1="748" y1="190" x2="540" y2="235" stroke="#c6a0ff" stroke-width="3"/><polygon points="540.0,235.0 550.8,237.8 548.7,228.0" fill="#c6a0ff"/><text x="644.0" y="215" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">route admissible</text><line x1="395" y1="270" x2="270" y2="190" stroke="#c6a0ff" stroke-width="3"/><polygon points="270.0,190.0 275.7,199.6 281.1,191.2" fill="#c6a0ff"/><text x="332.5" y="230" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">label + transport</text><text x="480" y="333" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">À chaque étape, vérifier l’objet correspondant : route, attributs, next-hop, labels, forwarding.</text></svg>

### 20.2 Décoder une panne causée par une incohérence de label

Ne conclus pas qu’un label est incorrect parce qu’il est différent sur deux routeurs : les valeurs de labels sont localement significatives dans le contexte attendu et sont traduites à chaque saut. Il faut comparer **l’étiquette annoncée par le voisin en aval**, l’action programmée sur le routeur amont et la route/FEC à laquelle le binding correspond. Un label valide sur P1 n’est pas supposé avoir la même valeur sur P2.

Méthode : capturer les bindings de label, identifier la FEC ou le préfixe associé, contrôler les voisins LDP ou l’état SR, suivre les actions swap/pop/push le long du chemin et confirmer le label VPN reçu au PE d’egress. Si la LFIB reflète un état ancien après convergence, rechercher les défauts de synchronisation, les retraits de route ou un incident de programmation matérielle.

## 21. Hub-and-spoke et route leaking soumis à politique

Le routage hub-and-spoke est utile lorsque les sites ne doivent communiquer qu’au travers d’un site central, d’un pare-feu ou d’une plateforme d’inspection. Les route targets peuvent aider à établir cette portée de routes, mais la politique doit éviter qu’un import accidentel permette un chemin direct entre spokes. Le chemin de retour et les routes de services partagés exigent une conception symétrique et documentée.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-label="Modèle hub-and-spoke : connectivité contrôlée par RT"><rect x="1" y="1" width="958" height="358" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">Modèle hub-and-spoke : connectivité contrôlée par RT</text><rect x="65" y="95" width="220" height="80" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="175.0" y="122" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Spoke A</text><text x="175.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">export RT-A </text><text x="175.0" y="161" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8"> import RT-H</text><rect x="370" y="210" width="220" height="80" rx="12" fill="#102f36" stroke="#6dd3ce" stroke-width="2"/><text x="480.0" y="237" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Hub / services</text><text x="480.0" y="259" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">import RT-A + RT-B </text><text x="480.0" y="276" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8"> export RT-H</text><rect x="675" y="95" width="220" height="80" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="785.0" y="122" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Spoke B</text><text x="785.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">export RT-B </text><text x="785.0" y="161" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8"> import RT-H</text><line x1="175" y1="175" x2="410" y2="210" stroke="#6dd3ce" stroke-width="3"/><polygon points="410.0,210.0 400.8,203.6 399.4,213.5" fill="#6dd3ce"/><text x="292.5" y="188" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">routes vers hub</text><line x1="785" y1="175" x2="550" y2="210" stroke="#c6a0ff" stroke-width="3"/><polygon points="550.0,210.0 560.6,213.5 559.2,203.6" fill="#c6a0ff"/><text x="667.5" y="188" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">routes vers hub</text><line x1="410" y1="210" x2="175" y2="175" stroke="#f5c46a" stroke-width="3"/><polygon points="175.0,175.0 184.2,181.4 185.6,171.5" fill="#f5c46a"/><text x="292.5" y="205" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">retour via hub</text><line x1="550" y1="210" x2="785" y2="175" stroke="#f5c46a" stroke-width="3"/><polygon points="785.0,175.0 774.4,171.5 775.8,181.4" fill="#f5c46a"/><text x="667.5" y="205" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">retour via hub</text><text x="480" y="323" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">Les RT créent la portée de routage ; pare-feu/ACL et politiques CE–PE contrôlent les flux.</text></svg>

### 21.1 Matrice de routes et tests négatifs

Avant la configuration, créer une matrice explicite : qui annonce quoi, qui importe quoi, qui peut initier un flux, quels services partagés sont nécessaires, et quel composant applique la politique de sécurité. Un RT décide de la distribution de routes, pas si un paquet TCP vers un port est autorisé.

Exemple de validation :

| Source | Destination | Route attendue | Flux attendu | Preuve |
|---|---|---|---|---|
| Spoke A | Hub services | route présente | DNS/AAA autorisés selon règles | traceroute VRF + journaux firewall |
| Spoke B | Hub services | route présente | services autorisés | test par application |
| Spoke A | Spoke B | route directe absente si politique stricte | interdit ou inspecté par le hub | table VRF + capture / firewall |
| Admin | équipements PE/P | via réseau de management | accès limité | ACL de management + journaux |

Les tests négatifs sont aussi importants que les tests positifs : vérifier explicitement que les routes et flux interdits le restent après une panne ou une bascule vers un second PE/RR.

## 22. BGP PIC et objectifs de convergence mesurables

BGP PIC (Prefix Independent Convergence) concerne des mécanismes de forwarding destinés à accélérer la bascule dans des scénarios pris en charge. L’idée importante est de préparer dans le plan de forwarding un chemin de secours exploitable, afin de réduire le travail nécessaire au moment de la panne. Le comportement réel dépend du type de route, de la plateforme, des familles activées et de la conception des next-hops.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="365" viewBox="0 0 960 365" role="img" aria-label="BGP PIC : préparer un next-hop de secours dans le forwarding"><rect x="1" y="1" width="958" height="363" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">BGP PIC : préparer un next-hop de secours dans le forwarding</text><rect x="45" y="125" width="155" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="122.5" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">PE ingress</text><text x="122.5" y="174" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">VRF / FIB</text><rect x="315" y="90" width="175" height="80" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="402.5" y="117" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Chemin primaire</text><text x="402.5" y="139" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">PE-A / label A</text><rect x="315" y="235" width="175" height="80" rx="12" fill="#35223b" stroke="#c6a0ff" stroke-width="2"/><text x="402.5" y="262" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Chemin secours</text><text x="402.5" y="284" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">PE-B / label B</text><rect x="650" y="125" width="255" height="80" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="777.5" y="152" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">PE distant / CE</text><text x="777.5" y="174" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">préfixe destination</text><line x1="200" y1="150" x2="315" y2="130" stroke="#6dd3ce" stroke-width="3"/><polygon points="315.0,130.0 304.3,126.8 306.0,136.6" fill="#6dd3ce"/><text x="257.5" y="111" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">primary</text><line x1="200" y1="175" x2="315" y2="275" stroke="#c6a0ff" stroke-width="3"/><polygon points="315.0,275.0 310.7,264.7 304.2,272.2" fill="#c6a0ff"/><text x="257.5" y="226" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">backup préinstallé</text><line x1="490" y1="130" x2="650" y2="150" stroke="#6dd3ce" stroke-width="3"/><polygon points="650.0,150.0 640.7,143.8 639.5,153.7" fill="#6dd3ce"/><text x="570.0" y="112" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">forwarding actif</text><line x1="490" y1="275" x2="650" y2="180" stroke="#c6a0ff" stroke-width="3"/><polygon points="650.0,180.0 638.8,180.8 644.0,189.4" fill="#c6a0ff"/><text x="570.0" y="230" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">après panne</text><text x="480" y="340" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">PIC réduit le délai de reprogrammation dans certains scénarios ; il ne remplace pas la convergence complète.</text></svg>

### 22.1 Ne pas confondre détection et restauration

BFD peut notifier rapidement un défaut ; BGP doit toujours déterminer les routes valides et le matériel doit appliquer le bon chemin. Un mécanisme FRR local peut éviter l’attente de la convergence globale pour certaines pannes, mais il ne répare pas un chemin de secours absent, insuffisamment dimensionné, filtré par une politique, ou affecté par le même risque physique.

Pour chaque objectif de service, distinguer :

- **temps de détection** : du défaut physique/logique au signalement ;
- **temps de décision** : calcul IGP/BGP ou activation de la réparation ;
- **temps de programmation** : mise à jour des structures de forwarding ;
- **perte de données** : paquets perdus pendant la transition ;
- **récupération applicative** : rétablissement TCP, SIP, VPN client ou application réelle.

Définir une fenêtre de mesure, la cadence des sondes, le volume de trafic injecté, le nombre de répétitions et le critère d’acceptation. Réaliser les tests dans une maquette ou une fenêtre approuvée et éviter les bascules simultanées non contrôlées.

## 23. SR-MPLS avancé : SIDs, pile et politiques

SR-MPLS représente des instructions de chemin par des segments portés dans une pile de labels. Le Node-SID désigne typiquement une destination dans le domaine de routage ; un Adj-SID peut représenter une adjacence particulière. Les propriétés exactes dépendent du type de SID, de sa portée et du protocole de routage. Le SR Global Block (SRGB) et les annonces de SID doivent rester cohérents pour interpréter correctement les labels de segments.

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360" role="img" aria-label="SR-MPLS : pile de segments et progression dans le cœur"><rect x="1" y="1" width="958" height="358" rx="18" fill="#0b1424" stroke="#35516f" stroke-width="2"/><text x="480" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="21" font-weight="700" fill="#f8fafc">SR-MPLS : pile de segments et progression dans le cœur</text><rect x="35" y="120" width="165" height="85" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="117.5" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Ingress PE</text><text x="117.5" y="169" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">push SID stack</text><rect x="260" y="95" width="180" height="125" rx="12" fill="#19334e" stroke="#6dd3ce" stroke-width="2"/><text x="350.0" y="122" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Pile initiale</text><text x="350.0" y="144" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">SID Node C </text><text x="350.0" y="161" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8"> SID Adj B-C </text><text x="350.0" y="178" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8"> VPN label</text><rect x="500" y="120" width="155" height="85" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="577.5" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Transit P</text><text x="577.5" y="169" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">consomme SID actif</text><rect x="715" y="120" width="210" height="85" rx="12" fill="#162a43" stroke="#5a82b1" stroke-width="2"/><text x="820.0" y="147" text-anchor="middle" font-family="Arial,sans-serif" font-size="15" font-weight="700" fill="#f8fafc">Egress PE</text><text x="820.0" y="169" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">traitement VPN label</text><line x1="200" y1="160" x2="260" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="260.0,160.0 250.0,155.0 250.0,165.0" fill="#6dd3ce"/><text x="230.0" y="145" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">segments</text><line x1="440" y1="160" x2="500" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="500.0,160.0 490.0,155.0 490.0,165.0" fill="#6dd3ce"/><text x="470.0" y="145" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">label actif</text><line x1="655" y1="160" x2="715" y2="160" stroke="#6dd3ce" stroke-width="3"/><polygon points="715.0,160.0 705.0,155.0 705.0,165.0" fill="#6dd3ce"/><text x="685.0" y="145" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">prochain SID</text><rect x="260" y="250" width="395" height="55" rx="12" fill="#102033" stroke="#35516f" stroke-width="2"/><text x="457.5" y="277" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#f8fafc">Attention de conception</text><text x="457.5" y="299" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#c8d7e8">taille de pile · SRGB/SID · MTU · politiques</text><text x="480" y="333" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" font-weight="700" fill="#f5c46a">SR-MPLS remplace le mécanisme de distribution du transport, pas les exigences de forwarding/OAM.</text></svg>

### 23.1 Points de contrôle SR-MPLS

- vérifier que les SIDs attendus sont annoncés et qu’ils sont cohérents avec le plan de numérotation ;
- confirmer la compatibilité IGP, SRGB, index/SID et la programmation LFIB sur chaque nœud ;
- examiner le nombre maximal de labels réellement pris en charge, en tenant compte des autres labels de service ;
- mesurer les effets de la pile sur MTU et performances ;
- valider les réparations locales (TI-LFA ou autres) sur la topologie effective ;
- s’assurer que les outils OAM et la télémétrie interprètent correctement les SIDs.

SR-MPLS n’implique pas automatiquement une politique de trafic applicative. Une politique SR, un contrôleur ou une configuration de chemin doit être conçue, validée et exploitée explicitement. Le transport SR peut coexister ou migrer depuis d’autres modèles, mais la compatibilité et les mécanismes de transition doivent être testés selon les logiciels réels.

## 24. Carrier Supporting Carrier et hiérarchie de services

Le modèle *Carrier Supporting Carrier* (CSC) permet à un fournisseur de transporter le trafic ou les routes d’un autre fournisseur, lorsque le fournisseur client exploite lui-même un backbone de services. Cette hiérarchie ajoute une frontière de responsabilité et des dépendances de routage/labels qui dépassent une simple L3VPN entre deux sites d’entreprise.

Les décisions clés incluent qui fournit la reachability du fournisseur client, comment ses routes sont portées, quel domaine attribue/commute les labels, quelles VRF ou familles de routage sont exposées à la frontière, et comment le dépannage est partagé entre équipes. Le contrat d’exploitation doit désigner qui collecte les preuves du plan de données sur chaque côté et comment les pannes sont escaladées.

### 24.1 Matrice de responsabilité

| Couche | Fournisseur de transport | Fournisseur client | Vérification commune |
|---|---|---|---|
| accès / circuit | disponibilité du support et paramètres L2/L3 convenus | interface et routage de son côté | MTU, erreurs, compteurs, horodatages |
| underlay / labels | état de son IGP/LDP/SR dans la portée contractuelle | état de son backbone propre | preuve de reachability et test de forwarding convenu |
| routes VPN/service | politiques convenues au point d’interconnexion | routes client et RT/familles selon architecture | annonce, import, next-hop, chemin retour |
| incidents | traces et OAM disponibles dans son domaine | traces et sondes dans son domaine | corrélation UTC/local, fenêtre, paquet test |

Ne pas exiger d’un fournisseur qu’il expose tout son IGP interne pour prouver un service : utiliser des points de preuve convenus et des tests de service reproductibles.

## 25. Dimensionnement et gouvernance de la capacité

Le dimensionnement doit reposer sur des mesures et des marges de croissance explicites, pas sur un simple compte de VRF. Le coût varie selon les préfixes uniques, routes multipath, labels, familles VPNv4/VPNv6, nombre de clients BGP, policies, fréquence des changements, fréquence des retraits de routes, journalisation et capacité de mise à jour du matériel.

### 25.1 Les budgets à tenir

1. **Préfixes par VRF** : nombre courant, pic connu, croissance annuelle et nombre de chemins par préfixe.
2. **Routes VPNv4/VPNv6 sur PE/RR** : total et distribution par RT, avec effet de RT-Constrain si activé.
3. **Labels** : allocation locale, labels de transport et de service, SIDs, ressources ASIC et limites de pile.
4. **Sessions de contrôle** : nombre de voisins, AF activées, redondance RR, capacité CPU et temps de convergence.
5. **Mises à jour** : impact d’un retrait massif, d’un flap CE–PE, d’une panne de RR ou d’un événement global de cœur.
6. **Données** : débit par classe QoS, PPS, drops de files, taille des paquets et marge en cas de bascule.

Les valeurs maximales supportées doivent être prises dans les guides de capacité de l’équipement exact et dans les notes de version. Une limite théorique de protocole ne prouve pas qu’un châssis peut programmer tous les objets avec le profil de fonctionnalités choisi.

### 25.2 Scénarios de capacité à simuler

- ajout d’un nouveau grand client avec plusieurs milliers de préfixes ;
- retrait d’un RR avec reprise par le second ;
- retrait d’un PE portant de nombreuses VRF ;
- mise à jour de politique RT qui modifie la portée de nombreuses routes ;
- bascule primaire/secondaire sous charge proche de la charge de pointe ;
- coexistence de plusieurs familles d’adresses et mécanismes de transport.

Observer la CPU, la mémoire, la convergence, le temps de programmation des tables et les symptômes côté application. Enregistrer les résultats pour comparer les versions logicielles.

## 26. Automatisation, télémétrie et preuves d’audit

L’automatisation ne rend pas une configuration correcte par elle-même. Elle doit appliquer une source de vérité versionnée, valider la configuration générée, exécuter des contrôles avant/après, et détecter la dérive entre l’intention (RD/RT, adressage, topologie, capacités) et l’état observé. Éviter les changements massifs fondés uniquement sur une chaîne de commandes sans garde-fous.

### 26.1 Pipeline de changement suggéré

1. valider la syntaxe et les valeurs dans un dépôt ou système de gestion de configuration ;
2. comparer le diff à une politique autorisée (notamment changements de RT, redistribution, maximum-prefix) ;
3. tester dans un lab avec le même OS/famille de matériel lorsque possible ;
4. sauvegarder la configuration et la baseline opérationnelle ;
5. déployer par lots limités avec seuil d’arrêt ;
6. contrôler les sessions, routes VRF, next-hops, labels, OAM et sondes applicatives ;
7. conserver les logs de déploiement, identifiant de changement, résultat des tests et auteur ;
8. déclencher un rollback si les critères prédéfinis sont franchis.

### 26.2 Supervision utile

Un tableau de bord robuste combine état des sessions (CE–PE, MP-BGP, LDP/BFD selon le design), nombre de préfixes par VRF, variations de routes, disponibilité du transport, événements de labels, drops de files, MTU, latence/perte et sondes réelles. Un compteur sans contexte ne donne pas une cause racine : il faut des timestamps cohérents, une topologie à jour et une relation documentée entre VRF, RT, PE et service client.

## 27. Atelier de diagnostic guidé

**Situation :** l’application du Client-A vers le site distant échoue après une fenêtre de changement. Les sessions VPNv4 sont établies ; le ping depuis la RIB globale vers la loopback distante fonctionne ; le ping depuis la VRF réussit avec une petite taille, mais le transfert applicatif est intermittent.

### Étape 1 — Formuler des hypothèses distinctes

- RT ou routes de retour modifiées partiellement ;
- transport MPLS valide pour certains next-hops mais pas pour tous ;
- MTU ou PMTUD affecté par la pile de labels ou un segment de transport ;
- drops QoS ou policer ;
- chemin asymétrique où une ACL ou un firewall rejette le retour.

### Étape 2 — Collecter avant de changer

- différence de configuration avant/après ;
- préfixe dans la VRF locale et distante ;
- attributs de la route VPNv4 (RD, RT, next-hop, label) ;
- état de l’underlay, des labels et de la LFIB ;
- tests sourcés depuis la VRF avec tailles différentes ;
- drops de files, erreurs d’interface et journaux firewall ;
- chemin retour pour l’adresse source réelle de l’application.

### Étape 3 — Isoler une variable

Si seules les grandes tailles échouent, tester la MTU de bout en bout et les messages PMTUD. Si les petits paquets échouent seulement dans un sens, vérifier route retour, asymétrie, filtres et route de sortie PE. Si la panne est limitée à certains préfixes après changement de RT, comparer les imports/exports avant/après. Ne pas redémarrer toutes les sessions BGP comme première action sans preuve : cela peut aggraver une panne de convergence.

### Étape 4 — Confirmer le rétablissement

Répéter le test applicatif bidirectionnel, avec mêmes sources, destinations, tailles et durée. Contrôler que les compteurs d’erreurs cessent d’augmenter, que la route reste stable, que la LFIB correspond au chemin attendu et qu’aucune VRF non concernée n’a reçu des routes indésirables.

## 28. Études de cas Expert supplémentaires

### Cas A — Label VPN visible mais mauvaise sortie

Il faut vérifier le modèle de label alloué (par préfixe, par VRF ou autre mode pris en charge), le binding annoncé au PE distant et l’action LFIB programmée sur le PE de sortie. Une valeur numérique différente sur les routeurs n’est pas à elle seule une anomalie ; la valeur est locale au contexte de distribution. Examiner la route/FEC, le voisin aval et l’action attendue, puis tester un paquet avec capture si disponible.

### Cas B — Après l’ajout de RT-Constrain, certains clients n’apprennent plus de routes

Vérifier les annonces de membres RT, les familles activées sur les RR, l’extension des communautés, les politiques et les chemins de réflexion. Comparer avec l’état connu comme bon. Vérifier si le PE consommateur annonce bien les RT nécessaires et si les route reflectors transportent l’information de contraintes à travers la topologie réelle.

### Cas C — BGP PIC activé, mais la coupure reste longue

Vérifier que le scénario de panne et le type de route sont couverts par l’implémentation PIC utilisée, qu’un next-hop alternatif et les labels associés sont préinstallés, que le chemin alternatif est effectivement programmable et qu’il ne partage pas le même risque physique. Séparer le délai de détection, le basculement de forwarding et la reconstruction complète de l’état BGP.

### Cas D — Réseau fonctionnel après migration LDP vers SR-MPLS, mais OAM incomplet

Vérifier que les outils utilisés comprennent les SIDs et les extensions nécessaires, que les identifiants/labels sont annoncés et programmés, et que le plan de supervision n’infère pas la disponibilité uniquement à partir des sessions de contrôle. Prévoir des tests de LSP/chemin et des sondes d’application, avec critères d’acceptation indépendants.

## 29. Livrables attendus d’une architecture experte

Pour un réseau de fournisseur ou une entreprise qui opère sa propre MPLS L3VPN, le dossier de conception doit inclure au minimum :

- diagrammes logique et physique avec PE/P/CE, liens, domaines de panne et frontières AS ;
- plan IP des loopbacks et liens, numérotation des AS et politique de routage underlay ;
- matrice VRF/RD/RT, préfixes attendus et exceptions de route leaking ;
- protocole de transport des labels, modèle d’allocation de labels VPN et preuve de compatibilité ;
- architecture MP-BGP/RR, familles activées, politiques, communautés et objectifs d’échelle ;
- choix de transport LDP, RSVP-TE ou SR-MPLS et stratégie de convergence/protection ;
- budget MTU/QoS, politique de marquage, outils OAM et sondes par service ;
- matrices de tests positifs/négatifs, tests de panne, résultats de capacité et rollback ;
- tableau de bord, runbook d’incident, rôles/responsabilités et historique de changement.

Une architecture n’est pas prête parce que le trafic passe dans le lab une fois. Elle est prête lorsque les états attendus sont documentés, les limites connues, les pannes représentatives testées et le retour à l’état précédent possible de manière vérifiable.

## 30. Références techniques

Les normes suivantes sont des points de départ pour approfondir les mécanismes. Les guides de configuration Cisco doivent être choisis selon la plateforme et la version logicielle réellement utilisée.

- RFC 4364 — BGP/MPLS IP Virtual Private Networks: https://www.rfc-editor.org/rfc/rfc4364
- RFC 4684 — Constrained Route Distribution for BGP/MPLS IP VPNs: https://www.rfc-editor.org/rfc/rfc4684
- RFC 3209 — RSVP-TE: Extensions to RSVP for LSP Tunnels: https://www.rfc-editor.org/rfc/rfc3209
- RFC 4090 — Fast Reroute Extensions to RSVP-TE: https://www.rfc-editor.org/rfc/rfc4090
- RFC 5880 — Bidirectional Forwarding Detection: https://www.rfc-editor.org/rfc/rfc5880
- RFC 8029 — Detecting MPLS Data-Plane Failures: https://www.rfc-editor.org/rfc/rfc8029
- Cisco IOS XR L3VPN Configuration Guide (choisir la version exacte): https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/l3vpn/l3vpn-config-cisco8000.html
- Cisco MPLS VPN technology resources: https://www.cisco.com/c/en/us/solutions/service-provider/vpn-solutions.html


**Règle d’exploitation :** ne conclus jamais « MPLS est cassé » sur la seule base d’un ping. Identifie d’abord le contexte VRF, la route, le next-hop, le chemin de labels, la MTU, la direction et le chemin retour ; collecte les preuves, change une seule variable et valide avec un test reproductible.


## 31. Index des schémas intégrés

Les schémas sont directement inclus dans ce fichier, chacun sur une seule ligne SVG afin d’améliorer la compatibilité avec les lecteurs Markdown qui interprètent mal les blocs multilignes.

1. **Architecture de référence : le service VPN et le transport MPLS** — `architecture`
2. **Dépendances du plan de contrôle** — `control-plane`
3. **Pile de labels : transport externe et service VPN** — `label-stack`
4. **RD et RT : fonctions différentes** — `rd-rt`
5. **RT-Constrain : limiter la diffusion des routes VPN** — `rt-constrain`
6. **Inter-AS L3VPN : options A, B et C** — `inter-as-options`
7. **Trajet d’un paquet VPN en inter-AS** — `packet-interas`
8. **Convergence : chemin primaire et protection locale** — `frr-convergence`
9. **LDP–IGP synchronization** — `ldp-sync`
10. **MTU : encapsulation de bout en bout** — `mtu`
11. **QoS sur MPLS : classifier, marquer et traiter** — `qos-mpls`
12. **OAM MPLS et preuves de service** — `oam`
13. **Route Reflectors et scalabilité BGP** — `route-reflector`
14. **Dépannage expert par couches** — `troubleshooting`
15. **Cycle de vie d’une route VPN** — `route-lifecycle`
16. **Hub-and-spoke et RT** — `hub-spoke`
17. **BGP PIC et chemin de secours préinstallé** — `bgp-pic`
18. **SR-MPLS : pile de segments** — `sr-mpls-stack`
