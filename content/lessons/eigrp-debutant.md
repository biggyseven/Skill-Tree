# EIGRP — Niveau Débutant

**Durée indicative :** 4 à 6 heures, selon les laboratoires  
**Prérequis :** adressage IPv4, sous-réseaux, table de routage, routes statiques, passerelle, notions de routeur et de commutation Ethernet.  
**Environnement recommandé :** Cisco Packet Tracer si l’image prend en charge les commandes EIGRP souhaitées, ou une maquette Cisco IOS/IOS XE/FRRouting documentée ; Wireshark est facultatif.

Ce cours constitue le premier niveau de la série EIGRP. Il construit les fondations nécessaires aux futurs cours **`eigrp-intermediaire.md`** et **`eigrp-expert.md`**. Tu vas apprendre à reconnaître un voisinage, comprendre les métriques, distinguer successor et feasible successor, suivre les états DUAL et dépanner une route absente. Les niveaux suivants pourront approfondir la convergence complexe, la redistribution, le résumé, la variance, le mode nommé et les scénarios de grande échelle sans reprendre pas à pas les bases.

> **Important :** EIGRP est documenté par Cisco et décrit également dans la RFC informative 7868, qui n’est pas une norme Internet Standards Track. Les exemples de configuration ci-dessous utilisent la syntaxe classique Cisco IOS/IOS XE ; elle varie selon les plateformes et les versions. Les préfixes `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` sont réservés à la documentation : conserve-les pour les laboratoires et ne les annonce pas sur Internet.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- expliquer où EIGRP est utilisé et comment il diffère d’OSPF et du routage statique ;
- reconnaître le rôle de l’AS EIGRP, des voisins, des Hello et des Update ;
- expliquer le rôle de DUAL, du successeur, de la distance faisable (FD) et de la distance annoncée (RD) ;
- appliquer la condition de faisabilité sans confondre FD et RD ;
- comprendre, à un niveau débutant, comment la bande passante et le délai influencent la métrique ;
- configurer EIGRP sur trois routeurs compatibles ;
- utiliser les commandes d’affichage pour vérifier voisins, topologie et routes ;
- distinguer une panne de voisinage, une route absente et un problème de transfert ;
- expliquer pourquoi une route alternative peut être sans boucle sans être nécessairement un feasible successor.

## Comment utiliser les schémas

Les huit SVG sont intégrés directement à ce Markdown ; aucun dossier d’images externe n’est nécessaire. Les animations indiquent un échange ou un chemin précis. Elles ne représentent pas le timing réel de chaque paquet et ne remplacent pas la sortie de commande d’un équipement. Si ton lecteur supprime l’animation SVG, les connecteurs, légendes et valeurs restent lisibles comme schémas statiques.

Pour chaque laboratoire : observe l’état initial, modifie une seule variable, collecte les sorties après la modification puis explique le résultat. Ne change pas les K-values ou ne désactive pas les filtres sur un réseau en production pour tenter de faire apparaître un voisin.


## 1. Qu’est-ce qu’EIGRP ?

EIGRP signifie *Enhanced Interior Gateway Routing Protocol*. Il s’agit d’un protocole de routage utilisé à l’intérieur d’un domaine administratif. Il échange des informations de joignabilité entre routeurs voisins et utilise l’algorithme **DUAL** (*Diffusing Update Algorithm*) pour déterminer des chemins sans boucle.

Il est souvent décrit comme un protocole à vecteur de distances avancé : il ne construit pas une LSDB globale de la même manière qu’OSPF. Il conserve plutôt les informations reçues des voisins dans une table topologique, calcule la route retenue et suit les états nécessaires à DUAL.

### 1.1. EIGRP ne remplace pas l’adressage

Avant qu’un protocole de routage puisse fonctionner, les interfaces doivent avoir des adresses et des sous-réseaux cohérents. EIGRP ne crée pas les VLAN, ne configure pas à lui seul les interfaces et ne remplace pas un plan d’adressage.

Une interface mal adressée peut empêcher la communication locale, alors qu’un mauvais AS, des K-values incompatibles ou une authentification divergente peuvent empêcher la formation du voisinage EIGRP. Ce sont des catégories d’erreurs distinctes ; il faut les examiner séparément.

### 1.2. EIGRP comparé à quelques autres méthodes

| Aspect | Routage statique | EIGRP | OSPF |
|---|---|---|---|
| Calcul | Défini manuellement | DUAL et métrique composite | SPF à partir de la base d’état de liens |
| Information reçue | Aucune par le mécanisme statique lui-même | Routes et métriques des voisins EIGRP | LSA et informations de topologie |
| Adaptation à une panne | Dépend des routes de secours et suivis configurés | Peut basculer sur un chemin feasible successor ou effectuer un calcul diffusé | Recalcule selon les changements de topologie et la configuration |
| Paramètre important | Prochain saut / interface et préférence | AS, voisinage, K-values, métrique | Aire, Router ID, types de réseau, coût |
| Point de vigilance | Une route peut devenir périmée | Une route annoncée n’est pas nécessairement un feasible successor | Un voisin FULL ne prouve pas toutes les routes et services |

Il ne faut pas dire qu’un protocole est toujours plus rapide qu’un autre. Le résultat dépend de la topologie, de la détection de panne, du nombre de routeurs, de la configuration et de la plateforme.


## 2. Le premier laboratoire : trois routeurs, un AS

## Schéma 1 — Topologie du premier laboratoire EIGRP

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 490" role="img" aria-label="Topologie du premier laboratoire EIGRP" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="490" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Topologie du premier laboratoire EIGRP</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Trois routeurs dans le même AS ; les marqueurs restent sur les liens EIGRP.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="70" y="145" width="170" height="72" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2.4"/>
<text x="155.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R1 · AS 100</text>
<text x="155.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12">Router ID 1.1.1.1</text><rect x="395" y="145" width="170" height="72" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/>
<text x="480.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R2 · AS 100</text>
<text x="480.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12">Router ID 2.2.2.2</text><rect x="720" y="145" width="170" height="72" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2.4"/>
<text x="805.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R3 · AS 100</text>
<text x="805.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12">Router ID 3.3.3.3</text><path d="M 240 181 L 395 181" fill="none" stroke="#45c7f5" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><text x="317" y="143" text-anchor="middle" fill="#45c7f5" font-size="12" font-weight="600">Gi0/1 ↔ Gi0/0</text><path d="M 565 181 L 720 181" fill="none" stroke="#45c7f5" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><text x="642" y="143" text-anchor="middle" fill="#45c7f5" font-size="12" font-weight="600">Gi0/1 ↔ Gi0/0</text><text x="317" y="207" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="600">10.0.12.0/30</text><text x="642" y="207" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="600">10.0.23.0/30</text><circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 240 181 L 395 181" dur="2.4s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 565 181 L 720 181" dur="2.4s" begin="1.0s" repeatCount="indefinite"/>
</circle><path d="M 155 217 L 155 278" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="55" y="278" width="200" height="72" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/>
<text x="155.0" y="305" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">LAN de R1</text>
<text x="155.0" y="327" text-anchor="middle" fill="#adbdcf" font-size="12">192.0.2.0/24</text><path d="M 805 217 L 805 278" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="705" y="278" width="200" height="72" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/>
<text x="805.0" y="305" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">LAN de R3</text>
<text x="805.0" y="327" text-anchor="middle" fill="#adbdcf" font-size="12">203.0.113.0/24</text><rect x="285" y="285" width="390" height="72" rx="12" fill="#111c2a" stroke="#34475d" stroke-width="1.5"/><text x="480" y="311" text-anchor="middle" fill="#eef4fb" font-size="16" font-weight="700">Même AS EIGRP : 100</text><text x="480" y="335" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Les interfaces participantes partagent l’AS et des paramètres compatibles.</text><rect x="55" y="390" width="850" height="70" rx="12" fill="#111c2a" stroke="#34475d" stroke-width="1.3"/><text x="480" y="416" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">EIGRP découvre les voisins, échange des routes et calcule un successeur sans boucle.</text><text x="480" y="440" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Adresses de documentation uniquement ; adapte interfaces, masques et AS au laboratoire.</text>
</svg>
</div>

Ce laboratoire utilise trois routeurs dans le même AS EIGRP. Le préfixe de R1 doit pouvoir être appris par R3 au travers de R2. Les réseaux de transit et les LAN sont des adresses de documentation ; ils ne sont pas destinés à être annoncés sur Internet.

## Schéma 2 — De l’interface à une route exploitable

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 490" role="img" aria-label="Du lien IP à une route EIGRP exploitable" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="490" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Du lien IP à une route EIGRP exploitable</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Vue pédagogique du démarrage ; ce n’est pas une chronologie exacte de tous les paquets.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="35" y="145" width="130" height="76" rx="13" fill="#172333" stroke="#34475d" stroke-width="2.4"/>
<text x="100.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">1 · Interface</text>
<text x="100.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12">Lien IP opérationnel</text><rect x="225" y="145" width="130" height="76" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/>
<text x="290.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">2 · Hello</text>
<text x="290.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12">Découverte mutuelle</text><rect x="415" y="145" width="130" height="76" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2.4"/>
<text x="480.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">3 · Voisin</text>
<text x="480.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12">Paramètres compatibles</text><rect x="605" y="145" width="130" height="76" rx="13" fill="#172333" stroke="#fbbf24" stroke-width="2.4"/>
<text x="670.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">4 · Update</text>
<text x="670.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12">Routes / métriques</text><rect x="795" y="145" width="130" height="76" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2.4"/>
<text x="860.0" y="172" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">5 · RIB</text>
<text x="860.0" y="194" text-anchor="middle" fill="#adbdcf" font-size="12">Route retenue</text><path d="M 165 183 L 225 183" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 355 183 L 415 183" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 545 183 L 605 183" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 735 183 L 795 183" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle r="4.5" fill="#45c7f5" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 165 183 L 225 183" dur="2.2s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="4.5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 355 183 L 415 183" dur="2.2s" begin="0.6s" repeatCount="indefinite"/>
</circle><circle r="4.5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 545 183 L 605 183" dur="2.2s" begin="1.2s" repeatCount="indefinite"/>
</circle><circle r="4.5" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 735 183 L 795 183" dur="2.2s" begin="1.8s" repeatCount="indefinite"/>
</circle><rect x="40" y="268" width="880" height="145" rx="13" fill="#111c2a" stroke="#34475d" stroke-width="1.5"/><text x="65" y="298" text-anchor="start" fill="#eef4fb" font-size="16" font-weight="700">Paquets EIGRP :</text><text x="75" y="329" text-anchor="start" fill="#45c7f5" font-size="14" font-weight="700">Hello</text><text x="205" y="329" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400">Découverte et maintien du voisinage</text><text x="75" y="357" text-anchor="start" fill="#4ade80" font-size="14" font-weight="700">Update</text><text x="205" y="357" text-anchor="start" fill="#adbdcf" font-size="13" font-weight="400">Annonce ou modification des routes</text><text x="500" y="329" text-anchor="start" fill="#fbbf24" font-size="14" font-weight="700">Query / Reply</text><text x="650" y="329" text-anchor="start" fill="#adbdcf" font-size="12" font-weight="400">Calcul diffusé en cas de perte de chemin admissible</text><text x="500" y="357" text-anchor="start" fill="#c4b5fd" font-size="14" font-weight="700">ACK</text><text x="650" y="357" text-anchor="start" fill="#adbdcf" font-size="12" font-weight="400">Accusé de réception fiable de certains paquets</text><text x="480" y="448" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">Un ping réussi ne prouve pas qu’un voisinage EIGRP existe : vérifie AS, réseau, K-values et interface.</text>
</svg>
</div>

Les Hello découvrent les voisins et maintiennent leur état. Les Update annoncent les routes et leurs métriques ; Query et Reply participent au calcul diffusé quand le chemin connu doit être recalculé. Les accusés de réception appartiennent au mécanisme de transport fiable EIGRP. La ligne est une vue simplifiée des fonctions, pas une séquence obligatoire identique dans chaque mise à jour.

### 2.1. Plan d’adressage du laboratoire

| Équipement | Interface | Adresse d’exemple | Rôle |
|---|---|---|---|
| R1 | G0/0 | `192.0.2.1/24` | LAN de R1 |
| R1 | G0/1 | `10.0.12.1/30` | Transit vers R2 |
| R2 | G0/0 | `10.0.12.2/30` | Transit vers R1 |
| R2 | G0/1 | `10.0.23.1/30` | Transit vers R3 |
| R3 | G0/0 | `10.0.23.2/30` | Transit vers R2 |
| R3 | G0/1 | `203.0.113.1/24` | LAN de R3 |

Les adresses sont illustratives et les noms d’interfaces peuvent varier. Vérifie d’abord la connectivité IP sur chaque liaison directement connectée. EIGRP ne peut pas corriger une adresse qui ne correspond pas au réseau du lien.

### 2.2. AS EIGRP et commandes `network`

Dans la syntaxe classique Cisco, `router eigrp 100` crée/configure le processus EIGRP associé à l’AS 100. Les interfaces participantes doivent utiliser le même AS pour devenir voisines. La commande `network` sélectionne les interfaces dont les adresses correspondent à une plage ; elle ne crée pas elle-même un réseau ni une adresse IP.

Exemple pour R1 :

```cisco
interface GigabitEthernet0/0
 ip address 192.0.2.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
router eigrp 100
 network 192.0.2.0 0.0.0.255
 network 10.0.12.0 0.0.0.3
 passive-interface GigabitEthernet0/0
```

Exemple pour R2 :

```cisco
interface GigabitEthernet0/0
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 ip address 10.0.23.1 255.255.255.252
 no shutdown
!
router eigrp 100
 network 10.0.12.0 0.0.0.3
 network 10.0.23.0 0.0.0.3
```

Exemple pour R3 :

```cisco
interface GigabitEthernet0/0
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 ip address 203.0.113.1 255.255.255.0
 no shutdown
!
router eigrp 100
 network 10.0.23.0 0.0.0.3
 network 203.0.113.0 0.0.0.255
 passive-interface GigabitEthernet0/1
```

La syntaxe est propre au mode classique IOS/IOS XE. Certaines plateformes utilisent le mode nommé EIGRP ou une syntaxe différente. Vérifie ce qui est disponible dans ton image avant de recopier une commande.

**Pourquoi `passive-interface` sur les LAN ?** L’interface peut toujours annoncer son réseau selon le comportement de la plateforme, mais n’essaie pas d’établir des voisinages EIGRP sur le LAN destiné aux terminaux. N’applique cette option qu’après avoir confirmé qu’aucun voisin EIGRP légitime ne doit se trouver sur cette interface.

### 2.3. Vérifier avant de continuer

```cisco
show ip interface brief
show ip eigrp neighbors
show ip eigrp topology
show ip protocols
show ip route eigrp
```

Si un voisin manque, vérifie l’état de l’interface, l’adressage, le masque, l’AS et les K-values ; examine ensuite les ACL, l’authentification si elle est configurée et les paramètres de réseau. N’enchaîne pas immédiatement sur le calcul de métrique tant que les adjacences ne sont pas correctes.


## 3. Comment se forme le voisinage ?

EIGRP utilise des messages Hello pour découvrir et maintenir le voisinage. Les routeurs doivent avoir une connectivité sur l’interface participante et des paramètres compatibles. Selon la configuration et la plateforme, les contrôles comprennent notamment l’AS, les K-values et les paramètres d’authentification.

Un ping peut réussir sans voisin EIGRP : le ping teste le trafic IP, tandis qu’EIGRP utilise ses propres paquets et règles d’adjacence. À l’inverse, un voisin existant ne garantit pas que le préfixe précis qui intéresse l’administrateur soit annoncé.

### 3.1. Les principaux types de paquets

| Type de paquet | Rôle général |
|---|---|
| Hello | Découvrir les voisins et maintenir l’adjacence |
| Update | Annoncer une nouvelle route ou un changement |
| Query | Demander aux voisins des informations lors d’une computation diffusée |
| Reply | Répondre à une Query |
| ACK | Accuser réception de certains paquets fiables |

Les mises à jour ne sont pas un simple envoi périodique complet de la table à tous les voisins. EIGRP échange les informations requises par le protocole et s’appuie sur un mécanisme de transport fiable pour certains messages. Les détails temporels et les comportements observables dépendent de l’état de la route et de l’implémentation.

### 3.2. Paramètres qui doivent être cohérents

- **AS EIGRP :** les voisins d’un même échange doivent utiliser le domaine EIGRP attendu.
- **K-values :** elles définissent les composantes actives de la métrique. Des paramètres incompatibles peuvent empêcher le voisinage.
- **Interface et sous-réseau :** les routeurs doivent être connectés selon les règles applicables à l’interface.
- **Authentification :** si activée, les paramètres doivent correspondre selon le mécanisme configuré.
- **Filtrage :** une ACL ou une politique de contrôle peut bloquer les paquets EIGRP.

N’augmente pas les timers ou ne modifie pas les K-values au hasard pour « forcer » une adjacence. Commence par comparer la configuration effective des deux côtés et observe les événements.


## 4. La métrique EIGRP : comprendre sans mémoriser à l’aveugle

EIGRP utilise une métrique composite. Dans la configuration classique avec les K-values par défaut, la bande passante minimale le long du chemin et le délai cumulé sont les composantes actives principales. Les autres composantes possibles, comme la charge et la fiabilité, dépendent des K-values utilisées. Le MTU apparaît dans certaines sorties de diagnostic mais n’est pas simplement une composante additive de la formule métrique classique.

### 4.1. Bande passante minimale et délai cumulé

La bande passante retenue pour le chemin est la plus faible rencontrée sur celui-ci. Les délais d’interface sont cumulés selon les règles de calcul EIGRP. Un lien très rapide au début du chemin ne rend pas l’ensemble du chemin aussi rapide si un autre segment est plus lent.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 490" role="img" aria-label="Comment EIGRP évalue un chemin" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="490" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Comment EIGRP évalue un chemin</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Le minimum de bande passante est pris sur le chemin ; les délais s’additionnent selon les interfaces.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="48" y="155" width="170" height="80" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/>
<text x="133.0" y="182" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Lien 1</text>
<text x="133.0" y="204" text-anchor="middle" fill="#adbdcf" font-size="12">1 Gbit/s · délai 10</text><rect x="288" y="155" width="170" height="80" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/>
<text x="373.0" y="182" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Lien 2</text>
<text x="373.0" y="204" text-anchor="middle" fill="#adbdcf" font-size="12">100 Mbit/s · délai 20</text><rect x="528" y="155" width="170" height="80" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/>
<text x="613.0" y="182" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Lien 3</text>
<text x="613.0" y="204" text-anchor="middle" fill="#adbdcf" font-size="12">1 Gbit/s · délai 30</text><rect x="768" y="155" width="150" height="80" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2.4"/>
<text x="843.0" y="182" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Destination</text>
<text x="843.0" y="204" text-anchor="middle" fill="#adbdcf" font-size="12">préfixe LAN</text><path d="M 218 195 L 288 195" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 458 195 L 528 195" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 698 195 L 768 195" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><circle r="4" fill="#4ade80" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 218 195 L 288 195" dur="2.2s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="4" fill="#4ade80" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 458 195 L 528 195" dur="2.2s" begin="0.5s" repeatCount="indefinite"/>
</circle><circle r="4" fill="#4ade80" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 698 195 L 768 195" dur="2.2s" begin="1s" repeatCount="indefinite"/>
</circle><rect x="45" y="290" width="420" height="105" rx="12" fill="#111c2a" stroke="#45c7f5" stroke-width="1.8"/><text x="255" y="316" text-anchor="middle" fill="#eef4fb" font-size="14" font-weight="700">Métrique composite (valeurs par défaut)</text><text x="255" y="343" text-anchor="middle" fill="#45c7f5" font-size="13" font-weight="600">Bande passante minimale du chemin</text><text x="255" y="366" text-anchor="middle" fill="#45c7f5" font-size="13" font-weight="600">+ délai cumulé</text><rect x="495" y="290" width="420" height="105" rx="12" fill="#111c2a" stroke="#fbbf24" stroke-width="1.8"/><text x="705" y="316" text-anchor="middle" fill="#fbbf24" font-size="15" font-weight="700">K-values</text><text x="705" y="343" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="600">K1 et K3 actifs dans le profil par défaut</text><text x="705" y="366" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">Les valeurs doivent être compatibles entre voisins</text><text x="480" y="438" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Les nombres affichés sont illustratifs ; ne compare pas les métriques qu’EIGRP calcule sur des K-values différentes.</text><text x="480" y="461" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">La formule classique dépend des K-values, de la bande passante minimale et du délai cumulé.</text>
</svg>
</div>

### 4.2. K-values : pourquoi ne pas les changer arbitrairement ?

Les K-values déterminent les composantes prises en compte dans la métrique. Le profil classique par défaut met généralement K1 et K3 à 1 et les autres à 0. Les valeurs effectives doivent être compatibles entre voisins afin de former le voisinage.

Modifier une K-value peut changer la comparaison de chemins et rendre certains voisins incompatibles. Pour un réseau débutant, garde les paramètres par défaut ; change les métriques au moyen d’une conception contrôlée et documentée plutôt que par modification globale des K-values.

### 4.3. La métrique n’est pas la distance administrative

La métrique compare des chemins au sein d’EIGRP. La distance administrative (AD), sur Cisco IOS, aide à départager des sources de routage différentes pour un préfixe donné. Une route EIGRP interne et une route EIGRP externe peuvent avoir des AD par défaut différentes sur Cisco ; ces valeurs ne sont pas universelles et peuvent être modifiées.

Ne compare pas directement un coût OSPF, une métrique EIGRP et une valeur BGP. Chacun appartient à un mécanisme de sélection différent. Observe le résultat de la table de routage réelle.


## 5. DUAL, successeur et feasible successor

DUAL (*Diffusing Update Algorithm*) construit des chemins sans boucle et organise le recalcul lorsqu’une destination change. Il suit les informations de route de chaque voisin et détermine quel chemin peut être utilisé comme successeur.

- **Successeur (successor) :** le prochain saut retenu pour transférer le trafic vers une destination.
- **FD (feasible distance) :** une référence locale de distance utilisée dans la condition de faisabilité. La définition exacte est liée à l’état DUAL et à l’historique de la route ; elle n’est pas toujours simplement la métrique actuelle du meilleur chemin.
- **RD (reported distance), aussi appelée advertised distance :** distance annoncée par le voisin pour atteindre la destination depuis son propre point de vue.
- **Feasible successor (FS) :** voisin dont la distance annoncée satisfait la condition de faisabilité, et qui fournit donc un chemin garanti sans boucle selon ce test.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 485" role="img" aria-label="Successeur et feasible successor : deux notions distinctes" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="485" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Successeur et feasible successor : deux notions distinctes</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Exemple chiffré illustratif pour le préfixe D ; RD est la distance annoncée par le voisin.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="55" y="185" width="160" height="72" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/>
<text x="135.0" y="212" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R1</text>
<text x="135.0" y="234" text-anchor="middle" fill="#adbdcf" font-size="12">Routeur à analyser</text><rect x="350" y="105" width="170" height="76" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/>
<text x="435.0" y="132" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R2</text>
<text x="435.0" y="154" text-anchor="middle" fill="#adbdcf" font-size="12">Voisin · RD = 1 000</text><rect x="350" y="285" width="170" height="76" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/>
<text x="435.0" y="312" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R3</text>
<text x="435.0" y="334" text-anchor="middle" fill="#adbdcf" font-size="12">Voisin · RD = 1 500</text><rect x="730" y="185" width="170" height="72" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/>
<text x="815.0" y="212" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">D</text>
<text x="815.0" y="234" text-anchor="middle" fill="#adbdcf" font-size="12">Réseau destination</text><path d="M 215 205 L 275 205" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 275 205 L 275 143" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 275 143 L 350 143" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 520 143 L 630 143" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 630 143 L 630 205" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 630 205 L 730 205" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 215 239 L 275 239" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 275 239 L 275 323" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 275 323 L 350 323" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 520 323 L 630 323" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 630 323 L 630 239" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><path d="M 630 239 L 730 239" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><text x="300" y="116" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="700">RD = 1 000</text><text x="300" y="309" text-anchor="middle" fill="#fbbf24" font-size="12" font-weight="700">RD = 1 500</text><text x="680" y="128" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="700">coût total R1 = 2 000</text><text x="680" y="348" text-anchor="middle" fill="#fbbf24" font-size="12" font-weight="700">coût total R1 = 2 300</text><circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 215 205 L 275 205 L 275 143 L 350 143 L 520 143 L 630 143 L 630 205 L 730 205" dur="3.0s" begin="0s" repeatCount="indefinite"/>
</circle><rect x="70" y="400" width="390" height="62" rx="11" fill="#142a24" stroke="#4ade80" stroke-width="1.8"/><text x="265" y="424" text-anchor="middle" fill="#4ade80" font-size="14" font-weight="700">Successeur : chemin total 2 000</text><text x="265" y="445" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">meilleur chemin courant</text><rect x="500" y="400" width="390" height="62" rx="11" fill="#2a2619" stroke="#fbbf24" stroke-width="1.8"/><text x="695" y="424" text-anchor="middle" fill="#fbbf24" font-size="14" font-weight="700">Feasible successor : RD &lt; FD</text><text x="695" y="445" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">1 500 &lt; 2 000 : condition satisfaite</text>
</svg>
</div>

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 495" role="img" aria-label="La condition de faisabilité sans ambiguïté" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="495" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">La condition de faisabilité sans ambiguïté</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Le signe est strict : RD doit être strictement inférieur à FD pour qualifier de feasible successor.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="40" y="115" width="880" height="96" rx="14" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="480" y="146" text-anchor="middle" fill="#eef4fb" font-size="18" font-weight="700">Condition de faisabilité (Feasibility Condition)</text><text x="480" y="183" text-anchor="middle" fill="#4ade80" font-size="22" font-weight="700">RD du voisin  &lt;  FD locale de référence</text><rect x="65" y="265" width="230" height="82" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/>
<text x="180.0" y="292" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Chemin A</text>
<text x="180.0" y="314" text-anchor="middle" fill="#adbdcf" font-size="12">RD 1 400 &lt; FD 2 000</text><rect x="365" y="265" width="230" height="82" rx="13" fill="#301b25" stroke="#fb7185" stroke-width="2.4"/>
<text x="480.0" y="292" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Chemin B</text>
<text x="480.0" y="314" text-anchor="middle" fill="#adbdcf" font-size="12">RD 2 100 ≥ FD 2 000</text><rect x="665" y="265" width="230" height="82" rx="13" fill="#201b35" stroke="#c4b5fd" stroke-width="2.4"/>
<text x="780.0" y="292" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Rappel</text>
<text x="780.0" y="314" text-anchor="middle" fill="#adbdcf" font-size="12">FD et RD ≠ même valeur</text><rect x="65" y="375" width="230" height="58" rx="10" fill="#142a24" stroke="#4ade80" stroke-width="1.5"/><text x="180" y="398" text-anchor="middle" fill="#4ade80" font-size="13" font-weight="700">Admissible comme FS</text><text x="180" y="418" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">garantie sans boucle</text><rect x="365" y="375" width="230" height="58" rx="10" fill="#301b25" stroke="#fb7185" stroke-width="1.5"/><text x="480" y="398" text-anchor="middle" fill="#fb7185" font-size="13" font-weight="700">Pas FS selon ce test</text><text x="480" y="418" text-anchor="middle" fill="#eef4fb" font-size="11" font-weight="400">peut être loop-free, mais</text><text x="480" y="432" text-anchor="middle" fill="#eef4fb" font-size="11" font-weight="400">pas garanti par la condition</text><rect x="665" y="375" width="230" height="58" rx="10" fill="#201b35" stroke="#c4b5fd" stroke-width="1.5"/><text x="780" y="398" text-anchor="middle" fill="#c4b5fd" font-size="13" font-weight="700">FD historique</text><text x="780" y="418" text-anchor="middle" fill="#eef4fb" font-size="11" font-weight="400">son sens dépend de l’état</text><text x="480" y="467" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">La condition est suffisante, pas nécessaire : tous les chemins sans boucle ne sont pas forcément des FS.</text>
</svg>
</div>

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="DUAL : bascule rapide ou calcul diffusé" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">DUAL : bascule rapide ou calcul diffusé</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">La réaction dépend de la présence d’un feasible successor admissible pour cette destination.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="380" y="110" width="200" height="70" rx="13" fill="#301b25" stroke="#fb7185" stroke-width="2.4"/>
<text x="480.0" y="137" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R1</text>
<text x="480.0" y="159" text-anchor="middle" fill="#adbdcf" font-size="12">Successeur R2 perdu</text><path d="M 480 180 L 480 223" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 480 223 L 235 223 L 235 256" fill="none" stroke="#4ade80" stroke-width="3.5"/><path d="M 480 223 L 725 223 L 725 256" fill="none" stroke="#fbbf24" stroke-width="3.5"/><rect x="85" y="256" width="300" height="88" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/>
<text x="235.0" y="283" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Cas A · FS disponible</text>
<text x="235.0" y="305" text-anchor="middle" fill="#adbdcf" font-size="12">R3 satisfait RD &lt; FD</text><rect x="575" y="256" width="300" height="88" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/>
<text x="725.0" y="283" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Cas B · Aucun FS</text>
<text x="725.0" y="305" text-anchor="middle" fill="#adbdcf" font-size="12">Aucune route garantie sans boucle</text><path d="M 235 344 L 235 375" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 725 344 L 725 375" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="85" y="375" width="300" height="72" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/>
<text x="235.0" y="402" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Bascule locale</text>
<text x="235.0" y="424" text-anchor="middle" fill="#adbdcf" font-size="12">Remplacer le successeur</text><rect x="575" y="375" width="300" height="72" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/>
<text x="725.0" y="402" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">DUAL passe ACTIVE</text>
<text x="725.0" y="424" text-anchor="middle" fill="#adbdcf" font-size="12">QUERY → REPLY puis recalcul</text><circle r="4.5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 480 180 L 480 223 L 235 223 L 235 256" dur="2.8s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="4.5" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 480 180 L 480 223 L 725 223 L 725 256" dur="2.8s" begin="1s" repeatCount="indefinite"/>
</circle><text x="480" y="475" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="600">ACTIVE n’est pas un état normal permanent : il indique qu’un calcul diffusé attend des réponses.</text>
</svg>
</div>

### 5.1. Comprendre la condition de faisabilité

La condition centrale est :

\[
RD_{voisin} < FD_{locale}
\]

Le signe est **strictement inférieur**, pas inférieur ou égal. Si la condition est remplie, ce voisin est un feasible successor admissible pour cette destination. La condition est **suffisante mais pas nécessaire** : un chemin peut être sans boucle sans satisfaire cette règle, et EIGRP ne le traite alors pas comme feasible successor sur la base de cette seule preuve.

La FD a une signification historique selon les transitions DUAL : elle conserve la meilleure distance connue depuis le dernier passage approprié entre états. C’est pourquoi on ne doit pas remplacer mentalement sa définition par une règle simplifiée qui serait toujours « le coût affiché du successor à l’instant présent ».

### 5.2. PASSIVE et ACTIVE

- **PASSIVE :** aucune computation diffusée n’est en cours pour la destination ; c’est l’état stable normal.
- **ACTIVE :** DUAL effectue une computation et peut attendre les réponses de voisins interrogés.
- **QUERY/REPLY :** messages utilisés lorsque le routeur ne dispose pas d’un chemin acceptable pour résoudre localement le changement.
- **SIA (*Stuck-in-Active*) :** état problématique dans lequel une computation reste ACTIVE plus longtemps que prévu, souvent parce qu’une réponse attendue manque ou tarde.

Une route qui passe en ACTIVE n’est pas automatiquement une panne de l’interface locale : il faut suivre le changement topologique et identifier où la computation attend une réponse. Les détails des temporisations et des commandes de diagnostic dépendent de la plateforme.


## 6. Comment une panne est-elle traitée ?

La différence importante n’est pas seulement « EIGRP est rapide ». C’est l’existence ou non d’un chemin de secours qualifié par DUAL.

Si le successor échoue et qu’un feasible successor admissible existe, EIGRP peut remplacer le chemin sans diffuser une nouvelle computation pour cette destination. Si aucun FS n’est disponible, DUAL peut avoir besoin de passer en ACTIVE, envoyer des Query et recueillir les Reply nécessaires avant d’installer un nouveau chemin. Le schéma précédent compare précisément ces deux branches ; cette section détaille les mesures à relever après la panne.

### 6.1. Ce qui peut ralentir le rétablissement

- Aucun feasible successor n’est disponible pour la destination.
- Un voisin interrogé est indisponible ou répond tardivement.
- Le domaine d’impact de la panne est important.
- Une interface ou un voisinage est instable.
- La route de retour, le service applicatif ou une ACL est en panne après la convergence.
- La route est connue dans la table topologique mais n’est pas installée comme route retenue.

Le temps de convergence ne doit pas être déduit d’une animation ou d’un seul ping. Dans un laboratoire, mesure les pertes et les changements de route ; en exploitation, corrèle les horodatages des logs et les tests applicatifs.


## 7. De la table topologique à la table de routage

EIGRP maintient une table de voisins et une table topologique. La table des voisins répond à la question « avec qui ce routeur a-t-il une adjacence ? ». La table topologique répond « quels chemins et quelles métriques les voisins annoncent-ils pour les destinations ? ». La table de routage indique les routes retenues par le système pour le transfert.

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" role="img" aria-label="Du voisin EIGRP à la route installée" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="480" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Du voisin EIGRP à la route installée</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Chaque table répond à une question différente ; une adjacency stable ne garantit pas chaque destination.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="50" y="150" width="185" height="80" rx="13" fill="#172333" stroke="#45c7f5" stroke-width="2.4"/>
<text x="142.5" y="177" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Voisins</text>
<text x="142.5" y="199" text-anchor="middle" fill="#adbdcf" font-size="12">Table des adjacences</text><rect x="280" y="150" width="185" height="80" rx="13" fill="#172333" stroke="#c4b5fd" stroke-width="2.4"/>
<text x="372.5" y="177" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Topologie</text>
<text x="372.5" y="199" text-anchor="middle" fill="#adbdcf" font-size="12">Routes et métriques</text><rect x="510" y="150" width="185" height="80" rx="13" fill="#172333" stroke="#4ade80" stroke-width="2.4"/>
<text x="602.5" y="177" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">DUAL</text>
<text x="602.5" y="199" text-anchor="middle" fill="#adbdcf" font-size="12">Successeur / état</text><rect x="740" y="150" width="170" height="80" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/>
<text x="825.0" y="177" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">RIB</text>
<text x="825.0" y="199" text-anchor="middle" fill="#adbdcf" font-size="12">Route installée</text><path d="M 235 190 L 280 190" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 465 190 L 510 190" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 695 190 L 740 190" fill="none" stroke="#5d7189" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><circle r="4.5" fill="#45c7f5" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 235 190 L 280 190" dur="2.4s" begin="0s" repeatCount="indefinite"/>
</circle><circle r="4.5" fill="#c4b5fd" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 465 190 L 510 190" dur="2.4s" begin="0.7s" repeatCount="indefinite"/>
</circle><circle r="4.5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.6">
<animateMotion path="M 695 190 L 740 190" dur="2.4s" begin="1.4s" repeatCount="indefinite"/>
</circle><rect x="70" y="285" width="820" height="115" rx="13" fill="#111c2a" stroke="#34475d" stroke-width="1.5"/><text x="105" y="314" text-anchor="start" fill="#eef4fb" font-size="15" font-weight="700">Commandes de contrôle</text><text x="105" y="342" text-anchor="start" fill="#45c7f5" font-size="13" font-weight="600">show ip eigrp neighbors</text><text x="370" y="342" text-anchor="start" fill="#c4b5fd" font-size="13" font-weight="600">show ip eigrp topology</text><text x="640" y="342" text-anchor="start" fill="#fbbf24" font-size="13" font-weight="600">show ip route eigrp</text><text x="105" y="373" text-anchor="start" fill="#adbdcf" font-size="12" font-weight="400">Une route peut être dans la table topologique sans être installée comme meilleur chemin dans la RIB.</text><text x="480" y="447" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="700">Toujours comparer voisinage → topologie → table de routage → test de transfert.</text>
</svg>
</div>

### 7.1. Commandes essentielles

| Commande Cisco IOS courante | Ce qu’elle permet de voir |
|---|---|
| `show ip eigrp neighbors` | Voisins EIGRP et état des adjacences |
| `show ip eigrp topology` | Routes, métriques, successor(s), états DUAL et chemins candidats |
| `show ip eigrp topology all-links` | Informations plus larges sur les chemins, si pris en charge |
| `show ip protocols` | Paramètres de protocoles, réseaux et filtres selon la configuration |
| `show ip route eigrp` | Routes EIGRP installées dans la table de routage |
| `show running-config` | Configuration active ; examiner la section EIGRP |
| `show interfaces` | État, compteurs et paramètres de l’interface |

La syntaxe et les champs de sortie dépendent de l’image IOS/IOS XE et du mode de configuration. Si une commande n’est pas disponible, consulte l’aide de l’équipement plutôt que de supposer que le protocole ne dispose pas de la fonction.

### 7.2. Pourquoi un voisin présent ne prouve pas la route

Un voisinage stable ne garantit pas que chaque préfixe attendu soit annoncé. Le réseau peut ne pas correspondre à une commande `network`, une interface peut être passive, une route peut avoir été retirée ou filtrée, ou le chemin n’est pas retenu par la sélection. Compare systématiquement la table topologique et la RIB.


## 8. Laboratoire pratique complet : R1 — R2 — R3

### Objectif

Former un domaine EIGRP en AS 100, annoncer les LAN de R1 et R3, puis vérifier qu’ils sont appris de l’autre côté.

### Étapes

1. Construis la topologie du schéma 1.
2. Attribue les adresses et vérifie chaque lien directement connecté.
3. Configure l’AS 100 et les commandes `network` aux trois routeurs.
4. Rends passives les interfaces LAN qui ne doivent pas former de voisinage.
5. Vérifie que R1 et R2 sont voisins, puis que R2 et R3 le sont.
6. Contrôle la table topologique.
7. Contrôle les routes EIGRP dans la RIB.
8. Depuis un hôte de laboratoire, teste le LAN distant et la route retour.
9. Enregistre les sorties avant/après et explique chaque différence.

### Critères de réussite

- R1 a le voisin R2 ; R2 a les voisins R1 et R3 ; R3 a le voisin R2.
- Le LAN de R1 est appris par R3, et le LAN de R3 par R1.
- Les routes de transit et les prochains sauts sont cohérents.
- Les pings entre les LAN réussissent si les hôtes et passerelles sont configurés et que les filtres les autorisent.
- Tu peux expliquer la différence entre `show ip eigrp topology` et `show ip route eigrp`.


## 9. Dépannage méthodique

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.4rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 525" role="img" aria-label="Arbre de diagnostic EIGRP" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="525" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Arbre de diagnostic EIGRP</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Séparer la formation du voisinage, la sélection DUAL, l’installation de route et le transfert.</text>
<line x1="28" y1="78" x2="932" y2="78" stroke="#34475d" stroke-width="1.5"/>
<rect x="320" y="100" width="320" height="58" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/><text x="480" y="124" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Le voisin EIGRP est-il visible ?</text><text x="480" y="143" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">show ip eigrp neighbors</text><path d="M 380 158 L 230 208" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><path d="M 580 158 L 730 208" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="65" y="208" width="330" height="80" rx="13" fill="#301b25" stroke="#fb7185" stroke-width="2.4"/>
<text x="230.0" y="235" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">NON · voisinage</text>
<text x="230.0" y="257" text-anchor="middle" fill="#adbdcf" font-size="12">IP / AS / K-values / Hello / ACL</text><rect x="565" y="208" width="330" height="80" rx="13" fill="#142a24" stroke="#4ade80" stroke-width="2.4"/>
<text x="730.0" y="235" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">OUI · route absente ?</text>
<text x="730.0" y="257" text-anchor="middle" fill="#adbdcf" font-size="12">show ip eigrp topology</text><path d="M 730 288 L 730 322" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="565" y="322" width="330" height="80" rx="13" fill="#2a2619" stroke="#fbbf24" stroke-width="2.4"/>
<text x="730.0" y="349" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Pas de successeur ?</text>
<text x="730.0" y="371" text-anchor="middle" fill="#adbdcf" font-size="12">FD / RD / ACTIVE / QUERY</text><path d="M 730 402 L 730 430" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><rect x="565" y="430" width="330" height="48" rx="10" fill="#201b35" stroke="#c4b5fd" stroke-width="1.5"/><text x="730" y="450" text-anchor="middle" fill="#eef4fb" font-size="11" font-weight="700">Puis RIB, prochain saut et test applicatif</text><text x="230" y="320" text-anchor="middle" fill="#fb7185" font-size="12" font-weight="700">Contrôle aussi</text><text x="230" y="341" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">interface et sous-réseau</text><text x="230" y="361" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">authentification si utilisée</text><text x="480" y="500" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Ne change qu’un paramètre à la fois et conserve les sorties avant/après.</text>
</svg>
</div>

### 9.1. Aucun voisin EIGRP

1. `show ip interface brief` : interfaces actives ?
2. `show ip interface` : adresses et masque corrects ?
3. `show running-config` : l’interface correspond-elle à une commande `network` du processus EIGRP ?
4. `show ip protocols` : AS, réseaux participants et interfaces passives ?
5. Comparer les K-values, paramètres d’authentification et filtres des deux côtés.
6. Examiner les journaux et les captures si nécessaire.

Le bon diagnostic doit identifier une cause précise. Modifier plusieurs paramètres simultanément fait perdre la capacité d’expliquer pourquoi la panne a disparu ou persisté.

### 9.2. Voisin établi, route absente

- Vérifier que la route existe dans la table de routage source.
- Vérifier que le réseau est annoncé par le processus EIGRP.
- Vérifier les filtres et les interfaces passives.
- Comparer les routes dans la table topologique du routeur receveur.
- Vérifier l’état PASSIVE/ACTIVE et l’existence d’un successor.
- Examiner si le meilleur chemin est installable dans la RIB.

### 9.3. Route présente, service inaccessible

Ne conclus pas que le routage est correct de bout en bout simplement parce qu’une route est installée. Vérifie l’adresse source, le prochain saut, le chemin aller, le chemin retour, les ACL/pare-feu, la résolution DNS et l’application. Un test ICMP qui échoue peut être filtré indépendamment du trafic applicatif.


## 10. Laboratoires et exercices

### Laboratoire 2 — Route absente avec voisinage présent

Dans une maquette, retire ou corrige une commande `network` qui inclut le lien LAN attendu. Compare voisins, routes topologiques et RIB. Restaure ensuite la configuration initiale et vérifie que la route réapparaît.

### Laboratoire 3 — Observer un feasible successor

Construis une topologie avec deux chemins vers une destination. Releve les métriques annoncées et la FD de référence. Détermine si la condition RD < FD est satisfaite. N’invente pas les métriques : utilise celles affichées ou un jeu de valeurs illustratif explicitement signalé.

### Laboratoire 4 — Perte du successor

Dans une maquette isolée, désactive le lien qui porte le successor. Si un feasible successor est déjà présent, observe la bascule. Si aucun chemin ne satisfait la condition, relève les états DUAL et les échanges Query/Reply disponibles dans les sorties de l’équipement.

### Laboratoire 5 — K-values incompatibles

Uniquement dans une maquette, configure intentionnellement une incompatibilité puis observe le voisinage. Restaure immédiatement les paramètres compatibles. Ce laboratoire ne doit pas être réalisé sur un réseau partagé ou en production.

### Laboratoire 6 — Route installée, application en échec

Conserve le voisinage stable et introduis un défaut applicatif contrôlé (pare-feu, route retour ou service arrêté). Démontre que l’état EIGRP ne peut pas identifier à lui seul toutes les pannes de service.

### Questions d’évaluation avec corrigés

**1. EIGRP est-il un protocole à état de liens comme OSPF ?**  
Non. EIGRP conserve des informations de voisinage et de topologie et utilise DUAL ; il ne construit pas la même LSDB globale d’aire qu’OSPF.

**2. Que représente un successor ?**  
Le prochain saut retenu pour transférer les paquets vers une destination selon la décision EIGRP.

**3. Quelle différence existe entre FD et RD ?**  
La RD est annoncée par le voisin ; la FD est une référence de distance conservée localement pour la décision DUAL, avec une signification liée à l’état et à l’historique du calcul.

**4. Quelle est la condition de faisabilité ?**  
La distance annoncée du voisin doit être strictement inférieure à la FD locale de référence : RD < FD.

**5. Un chemin dont la RD est supérieure à la FD est-il forcément en boucle ?**  
Non. Il ne satisfait pas la condition suffisante de faisabilité et n’est donc pas prouvé comme feasible successor par ce test. Il peut être loop-free sans être qualifié de FS.

**6. Que fait DUAL si le successor disparaît et qu’un FS valide existe ?**  
Il peut sélectionner ce chemin de secours sans lancer de computation diffusée pour la destination.

**7. Pourquoi EIGRP pourrait-il passer en ACTIVE ?**  
Parce qu’aucun chemin candidat ne satisfait la condition de faisabilité, et qu’une computation diffusée peut être nécessaire pour retrouver un chemin sans boucle.

**8. Pourquoi les K-values doivent-elles correspondre ?**  
Elles définissent les composants utilisés pour calculer la métrique et doivent être compatibles pour que les voisins établissent normalement l’adjacence.

**9. Une adjacency présente prouve-t-elle que le préfixe est installé ?**  
Non. Il faut vérifier la table topologique, la décision DUAL et la RIB.

**10. Que faire si les voisins existent mais que les LAN ne se joignent pas ?**  
Examiner les routes et les prochains sauts des deux côtés, la route retour, les filtres et le service. Éviter d’accuser EIGRP sans preuve.

**11. À quoi servent les Query et Reply ?**  
Ils participent au calcul diffusé quand DUAL doit interroger les voisins pour résoudre un changement de route.

**12. Quelle est la différence entre une métrique et la distance administrative ?**  
La métrique compare les chemins selon EIGRP ; l’AD Cisco aide à départager des sources de routage concurrentes pour un préfixe.

**13. À quoi sert `passive-interface` dans le laboratoire ?**  
À empêcher l’établissement de voisinages sur une interface qui dessert des terminaux, tout en laissant le réseau être annoncé selon les règles de la plateforme.

**14. Pourquoi faut-il vérifier la syntaxe du mode EIGRP ?**  
Les commandes classiques et le mode nommé peuvent différer selon le système, la version et la plateforme.

**15. Pourquoi un ping réussi ne garantit-il pas une adjacence EIGRP ?**  
Parce que le ping et le protocole EIGRP utilisent des règles et des paquets différents. Les paramètres EIGRP peuvent être incompatibles même si la connectivité IP fonctionne.


## 11. Checklist de changement

### Avant
- [ ] Enregistrer `show ip interface brief`, `show ip protocols`, les voisins, la topologie et la RIB.
- [ ] Identifier les préfixes impactés et les chemins attendus.
- [ ] Sauvegarder la configuration et confirmer un accès de secours.
- [ ] Définir les critères de succès et le retour arrière.

### Pendant
- [ ] Modifier une seule variable à la fois.
- [ ] Vérifier les voisins et les états DUAL.
- [ ] Confirmer les préfixes annoncés et installés.
- [ ] Surveiller les transitions ACTIVE, les Query et les routes manquantes.

### Après
- [ ] Vérifier les routes et les tests applicatifs dans les deux sens.
- [ ] Comparer les sorties avant/après.
- [ ] Vérifier que les interfaces LAN inutiles à l’adjacence restent passives.
- [ ] Mettre à jour le diagramme et les notes de laboratoire.


## 12. Glossaire

| Terme | Définition opérationnelle |
|---|---|
| AS EIGRP | Identifiant du domaine EIGRP dans la syntaxe classique |
| DUAL | Algorithme qui calcule des chemins sans boucle et coordonne certaines reconvergences |
| Neighbor | Routeur avec lequel une adjacence EIGRP est établie |
| Successor | Prochain saut retenu vers une destination |
| FD | Feasible Distance, référence locale de distance pour DUAL |
| RD | Reported Distance, distance annoncée par le voisin |
| Feasible Successor | Voisin qui satisfait RD < FD pour cette destination |
| PASSIVE | État stable de la route, sans computation diffusée en cours |
| ACTIVE | État durant lequel DUAL effectue une computation diffusée |
| Query / Reply | Messages impliqués dans le calcul diffusé |
| K-values | Coefficients définissant les composantes de la métrique composite |
| RIB | Table de routage du système |
| SIA | Stuck-in-Active, computation ACTIVE qui ne se termine pas comme prévu |

## Références techniques

- **RFC 7868 — Cisco’s Enhanced Interior Gateway Routing Protocol (EIGRP)** : https://www.rfc-editor.org/rfc/rfc7868.html
- **Cisco — Understand and Use EIGRP** : https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/16406-eigrp-toc.html
- **Cisco IOS/IOS XE — EIGRP Configuration Guide** : https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_eigrp/configuration/15-2s/config-eigrp.html
- **Cisco — Troubleshoot EIGRP Common Issues** : https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/118974-technote-eigrp-00.html

La RFC 7868 est une description informative du protocole ; elle n’est pas une norme Internet Standards Track. Pour toute commande réelle, la documentation de la version et de l’équipement utilisé reste la référence.

## Préparation au niveau Intermédiaire

Le niveau **Intermédiaire** réutilisera ces notions et approfondira les résumés, les routes externes, les métriques avancées, la variance, le mode nommé, les filtres et la convergence sur des topologies plus larges. Le niveau Expert traitera ensuite la conception, la redistribution multi-protocoles, les scénarios de panne complexes et l’exploitation à grande échelle.
