# Spanning Tree Protocol (STP) — Niveau Débutant

**Niveau :** Débutant  
**Durée indicative :** 60 à 90 minutes  
**Prérequis :** connaître le rôle d'un commutateur Ethernet, les adresses MAC, les VLAN et les liens trunk.

## Objectifs pédagogiques

À la fin de ce cours, tu dois pouvoir :

- expliquer pourquoi une topologie Ethernet redondante peut créer une boucle de couche 2 ;
- décrire le rôle des BPDU et l'élection du pont racine (*Root Bridge*) ;
- reconnaître les rôles root, designated et alternate d'un port ;
- distinguer les états classiques STP et comprendre l'apport de Rapid STP ;
- configurer des paramètres STP de base sur un commutateur Cisco compatible ;
- vérifier la topologie active avec les commandes `show spanning-tree` ;
- appliquer PortFast et BPDU Guard uniquement sur les ports destinés aux terminaux.

> **Important :** les commandes et valeurs par défaut varient selon le modèle de commutateur, la version d'IOS/IOS XE et le mode STP utilisé. Utilise ces exemples dans un laboratoire isolé, puis vérifie la documentation de ton équipement avant une intervention en production.


## 1. Pourquoi STP est-il nécessaire ?

### 1.1. La redondance est utile… jusqu'à ce qu'elle crée une boucle

On relie souvent plusieurs commutateurs par des chemins redondants afin de conserver une connectivité si un câble ou un équipement tombe en panne. Mais Ethernet de couche 2 ne possède pas, à lui seul, de mécanisme général de décompte de durée de vie équivalent au TTL IP pour éliminer toutes les trames qui tournent en boucle.

Une boucle de couche 2 peut provoquer :

- des diffusions qui circulent continuellement et saturent les liens ;
- des copies multiples d'une même trame ;
- des changements rapides ou incohérents dans les tables d'adresses MAC (*MAC flapping*) ;
- une perte de connectivité et une charge excessive sur les commutateurs.

Le Spanning Tree Protocol construit une topologie logique sans boucle en laissant certains ports redondants en attente. Si un chemin actif devient indisponible, STP peut recalculer la topologie et permettre à un chemin de secours de prendre le relais.

### 1.2. Comparaison visuelle : sans STP et avec STP

<div class="lesson-figure">
<svg viewBox="0 0 820 330" role="img" aria-label="Comparaison d'une boucle Ethernet sans STP et d'une topologie sans boucle grâce à STP" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs>
    <marker id="stp-arrow-red" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fb7185"/></marker>
    <marker id="stp-arrow-green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker>
  </defs>
  <rect x="8" y="8" width="390" height="314" rx="16" fill="#2a1421" stroke="#fb7185" stroke-opacity=".5"/>
  <rect x="422" y="8" width="390" height="314" rx="16" fill="#102a25" stroke="#34d399" stroke-opacity=".5"/>
  <text x="203" y="34" font-size="16" font-weight="700" text-anchor="middle" fill="#fecdd3">Sans STP : boucle active</text>
  <text x="617" y="34" font-size="16" font-weight="700" text-anchor="middle" fill="#a7f3d0">Avec STP : chemin sans boucle</text>
  <g fill="#3b1f30" stroke="#fb7185" stroke-width="1.5">
    <rect x="38" y="94" width="100" height="54" rx="9"/><rect x="248" y="94" width="100" height="54" rx="9"/><rect x="143" y="225" width="100" height="54" rx="9"/>
  </g>
  <g fill="#fff1f2" font-size="13" font-weight="700" text-anchor="middle"><text x="88" y="126">SW1</text><text x="298" y="126">SW2</text><text x="193" y="257">SW3</text></g>
  <g fill="none" stroke="#fb7185" stroke-width="4" marker-end="url(#stp-arrow-red)"><path d="M138 111 L248 111"/><path d="M285 148 L226 225"/><path d="M155 225 L101 148"/></g>
  <circle r="5" fill="#fff1f2"><animateMotion dur="2.8s" repeatCount="indefinite" path="M138 111 L248 111 L285 148 L226 225 L155 225 L101 148 Z"/></circle>
  <text x="203" y="300" font-size="11" fill="#fecdd3" text-anchor="middle">Les trames peuvent tourner sans fin</text>
  <g fill="#123c34" stroke="#34d399" stroke-width="1.5">
    <rect x="452" y="94" width="100" height="54" rx="9"/><rect x="662" y="94" width="100" height="54" rx="9"/><rect x="557" y="225" width="100" height="54" rx="9"/>
  </g>
  <g fill="#ecfdf5" font-size="13" font-weight="700" text-anchor="middle"><text x="502" y="126">SW1</text><text x="712" y="126">SW2</text><text x="607" y="257">SW3</text></g>
  <g fill="none" stroke="#34d399" stroke-width="4" marker-end="url(#stp-arrow-green)"><path d="M552 111 L662 111"/><path d="M699 148 L640 225"/><path d="M569 225 L515 148"/></g>
  <path d="M569 225 L515 148" stroke="#fbbf24" stroke-width="4" stroke-dasharray="7 6" opacity=".18"/>
  <path d="M569 225 L515 148" stroke="#fbbf24" stroke-width="4" stroke-dasharray="6 5"/>
  <rect x="501" y="170" width="100" height="24" rx="7" fill="#3d2b12" stroke="#fbbf24"/>
  <text x="551" y="186" fill="#fde68a" font-size="10" font-weight="700" text-anchor="middle">PORT BLOQUÉ</text>
  <path d="M552 111 L662 111 L699 148 L640 225" fill="none" stroke="#34d399" stroke-width="1.5" stroke-dasharray="4 6" opacity=".35"/>
  <circle r="5" fill="#ecfdf5"><animateMotion dur="2.5s" repeatCount="indefinite" path="M552 111 L662 111 L699 148 L640 225"/></circle>
  <text x="617" y="300" font-size="11" fill="#a7f3d0" text-anchor="middle">Un lien redondant reste en attente</text>
</svg>
</div>

Dans le deuxième panneau, le lien de secours reste physiquement connecté mais STP empêche son port concerné de transférer les données dans la topologie active. Le dessin est schématique : les rôles exacts des ports dépendent de l'élection et de chaque segment.

### 1.3. STP ne remplace pas les VLAN ni le routage

| Fonction | Rôle |
|---|---|
| VLAN | Sépare logiquement des domaines de couche 2. |
| Trunk 802.1Q | Transporte plusieurs VLAN sur une liaison. |
| STP | Empêche les boucles dans une topologie Ethernet redondante. |
| Routage inter-VLAN | Permet la communication de couche 3 entre réseaux IP associés à des VLAN différents. |
| EtherChannel | Regroupe plusieurs liens physiques en un lien logique ; STP traite normalement le port-channel comme une seule liaison logique. |

Un réseau peut avoir des VLAN correctement créés et des trunks opérationnels, mais subir une boucle si STP est absent ou mal configuré. À l'inverse, STP peut fonctionner correctement alors qu'un VLAN manque sur un trunk : ce dernier problème ne se corrige pas par STP.


## 2. Les éléments fondamentaux de STP

### 2.1. Les BPDU : les messages de contrôle

Les commutateurs qui participent à STP échangent des **BPDU** (*Bridge Protocol Data Units*). Ces messages annoncent des informations de topologie : identifiant de pont, coût vers la racine et informations sur le port émetteur. STP utilise ces informations pour décider quels ports doivent transférer le trafic et lesquels doivent rester en attente.

Les BPDU ne sont pas les trames de données des utilisateurs. Elles servent à construire et maintenir la topologie de couche 2. Dans une topologie simple, chaque commutateur compare les informations reçues pour déterminer le meilleur chemin vers le pont racine.

### 2.2. Le Bridge ID (BID)

Le **Bridge ID** identifie un pont pour l'élection STP. Il combine notamment la priorité STP, les informations système étendu — généralement liées au VLAN sur les implémentations par VLAN — et l'adresse MAC du commutateur.

La règle de base est simple : **le plus petit Bridge ID gagne l'élection de Root Bridge**. On compare d'abord la valeur de priorité effective ; si elle est identique, l'adresse MAC départage les équipements. Avec le système étendu, le VLAN participe à l'identifiant effectif.

Exemple pédagogique :

| Commutateur | Priorité configurée | MAC (exemple) | Résultat attendu |
|---|---:|---|---|
| SW1 | 32768 | 00:00:00:00:00:11 | Perd face à un BID plus petit |
| SW2 | 24576 | 00:00:00:00:00:22 | Devient racine si aucun BID inférieur n'existe |
| SW3 | 32768 | 00:00:00:00:00:03 | La MAC seule ne bat pas une priorité effective plus basse |

Ces adresses et valeurs illustrent la comparaison ; la sortie réelle doit être lue dans `show spanning-tree`.

### 2.3. Élection de la racine : animation des annonces

<div class="lesson-figure">
<svg viewBox="0 0 780 280" role="img" aria-label="Élection du pont racine STP et échange d'informations BPDU" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><marker id="stp-bpdu-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs>
  <rect x="16" y="12" width="748" height="256" rx="16" fill="#0b1728" stroke="#334155"/>
  <rect x="300" y="40" width="180" height="62" rx="12" fill="#123b32" stroke="#34d399" stroke-width="2"/>
  <text x="390" y="64" fill="#a7f3d0" font-size="15" font-weight="700" text-anchor="middle">SW2 · RACINE</text>
  <text x="390" y="84" fill="#d1fae5" font-size="11" text-anchor="middle">Priorité effective la plus basse</text>
  <rect x="66" y="180" width="155" height="56" rx="10" fill="#172943" stroke="#60a5fa" stroke-width="1.5"/>
  <rect x="559" y="180" width="155" height="56" rx="10" fill="#172943" stroke="#60a5fa" stroke-width="1.5"/>
  <text x="143" y="204" fill="#dbeafe" font-size="14" font-weight="700" text-anchor="middle">SW1</text><text x="143" y="220" fill="#bfdbfe" font-size="10" text-anchor="middle">Compare les BPDU</text>
  <text x="636" y="204" fill="#dbeafe" font-size="14" font-weight="700" text-anchor="middle">SW3</text><text x="636" y="220" fill="#bfdbfe" font-size="10" text-anchor="middle">Compare les BPDU</text>
  <path d="M221 190 L320 102" fill="none" stroke="#60a5fa" stroke-width="3" marker-end="url(#stp-bpdu-arrow)"/>
  <path d="M559 190 L460 102" fill="none" stroke="#60a5fa" stroke-width="3" marker-end="url(#stp-bpdu-arrow)"/>
  <circle r="5" fill="#93c5fd"><animateMotion dur="2.4s" repeatCount="indefinite" path="M221 190 L320 102"/></circle>
  <circle r="5" fill="#93c5fd"><animateMotion dur="2.4s" begin="1.2s" repeatCount="indefinite" path="M559 190 L460 102"/></circle>
  <text x="270" y="144" fill="#bfdbfe" font-size="11" text-anchor="middle">BPDU</text><text x="510" y="144" fill="#bfdbfe" font-size="11" text-anchor="middle">BPDU</text>
  <text x="390" y="248" fill="#94a3b8" font-size="11" text-anchor="middle">Les commutateurs convergent vers une topologie sans boucle</text>
</svg>
</div>

Le dessin illustre la diffusion des informations et la comparaison des identifiants ; il ne signifie pas qu'un commutateur non racine cesse d'envoyer toute BPDU dans tous les modes STP. Les comportements précis dépendent du protocole et de l'état de la topologie.

### 2.4. Le coût du chemin

STP associe un coût à un chemin. Le coût cumulé permet de comparer les chemins vers la racine. Les valeurs dépendent de la méthode de coût configurée et des conventions de la plateforme ; il ne faut donc pas apprendre une seule table de coûts comme une constante universelle.

Exemple simplifié :

```text
SW1 ── lien A (coût 4) ── SW2 ── Root
 \                         /
  └──── lien B (coût 19) ──┘

Chemin A : coût total = 4 + coût de SW2 vers la racine
Chemin B : coût total = 19 + coût direct vers la racine

STP compare le coût total et les critères de départage.
```

Si deux chemins ont un coût identique, STP compare d'autres informations du protocole, notamment le Bridge ID du voisin, puis des identifiants/paramètres de port selon les règles de sélection. Une égalité de coût ne signifie donc pas un choix aléatoire.


## 3. Les rôles et états des ports

### 3.1. Rôles STP

| Rôle | Fonction générale | Comportement typique |
|---|---|---|
| **Root Port (RP)** | Meilleur chemin d'un commutateur non racine vers la racine. | Transfert dans la topologie active. |
| **Designated Port (DP)** | Port choisi pour transférer sur un segment donné. | Transfert dans la topologie active. |
| **Alternate** | Chemin de secours vers la racine dans les mécanismes RSTP. | En attente, sans transfert de données utilisateurs. |
| **Backup** | Port de secours pour un segment partagé dans les cas où ce rôle s'applique. | En attente. Rare dans les réseaux Ethernet modernes point à point. |

Le pont racine n'a pas de Root Port : tous ses ports actifs sont normalement désignés pour leurs segments, sous réserve de cas particuliers de configuration.

### 3.2. Diagramme des rôles de ports

<div class="lesson-figure">
<svg viewBox="0 0 820 320" role="img" aria-label="Rôles de ports STP sur trois commutateurs avec une liaison de secours" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><marker id="stp-role-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#34d399"/></marker></defs>
  <rect x="10" y="10" width="800" height="300" rx="16" fill="#0b1728" stroke="#334155"/>
  <rect x="330" y="38" width="160" height="62" rx="12" fill="#123b32" stroke="#34d399" stroke-width="2"/>
  <text x="410" y="63" fill="#a7f3d0" font-size="15" font-weight="700" text-anchor="middle">SW1 · ROOT</text><text x="410" y="82" fill="#d1fae5" font-size="11" text-anchor="middle">DP sur ses segments</text>
  <rect x="76" y="200" width="160" height="62" rx="12" fill="#172943" stroke="#60a5fa" stroke-width="1.5"/><text x="156" y="225" fill="#dbeafe" font-size="15" font-weight="700" text-anchor="middle">SW2</text><text x="156" y="244" fill="#bfdbfe" font-size="11" text-anchor="middle">RP vers SW1</text>
  <rect x="584" y="200" width="160" height="62" rx="12" fill="#172943" stroke="#60a5fa" stroke-width="1.5"/><text x="664" y="225" fill="#dbeafe" font-size="15" font-weight="700" text-anchor="middle">SW3</text><text x="664" y="244" fill="#bfdbfe" font-size="11" text-anchor="middle">RP vers SW1</text>
  <path d="M330 88 L220 200" stroke="#34d399" stroke-width="4" fill="none" marker-end="url(#stp-role-arrow)"/>
  <path d="M490 88 L600 200" stroke="#34d399" stroke-width="4" fill="none" marker-end="url(#stp-role-arrow)"/>
  <path d="M236 230 L584 230" stroke="#fbbf24" stroke-width="4" stroke-dasharray="8 7" fill="none"/>
  <rect x="343" y="208" width="134" height="40" rx="8" fill="#3b2b12" stroke="#fbbf24"/><text x="410" y="225" fill="#fde68a" font-size="11" font-weight="700" text-anchor="middle">LIEN DE SECOURS</text><text x="410" y="239" fill="#fde68a" font-size="10" text-anchor="middle">un port alternate</text>
  <circle r="5" fill="#a7f3d0"><animateMotion dur="2.5s" repeatCount="indefinite" path="M330 88 L220 200"/></circle>
  <circle r="5" fill="#a7f3d0"><animateMotion dur="2.5s" begin="1.25s" repeatCount="indefinite" path="M490 88 L600 200"/></circle>
  <text x="410" y="289" fill="#94a3b8" font-size="11" text-anchor="middle">Le chemin SW2–SW3 est redondant ; un port ne transfère pas sur ce segment.</text>
</svg>
</div>

Dans une vraie topologie, le rôle exact du port en attente dépend de la comparaison des BPDU et des identifiants. Le schéma présente un cas simple pour mémoriser le principe.

### 3.3. États du STP classique et Rapid STP

Le STP classique (IEEE 802.1D) utilise des états comme Blocking, Listening, Learning et Forwarding, avec Disabled pour un port qui ne participe pas au transfert. Rapid STP (IEEE 802.1w, souvent appelé RSTP) simplifie les états en discarding, learning et forwarding et peut accélérer les transitions lorsque les conditions le permettent.

| STP classique | Sens | RSTP (simplifié) |
|---|---|---|
| Blocking | Le port ne transfère pas les trames utilisateurs. | Discarding |
| Listening | Le port participe à la convergence sans apprendre les MAC utilisateurs. | Discarding |
| Learning | Le port apprend les adresses MAC sans transférer les données utilisateurs. | Learning |
| Forwarding | Le port transfère les trames et apprend les MAC. | Forwarding |
| Disabled | Le port est administrativement ou opérationnellement inactif. | Le port est inactif ; il ne s'agit pas d'un état RSTP équivalent à proprement parler. |

<div class="lesson-figure">
<svg viewBox="0 0 820 210" role="img" aria-label="Progression conceptuelle des états du STP classique et des états RSTP" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;font-family:Arial,sans-serif">
  <defs><marker id="stp-state-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker></defs>
  <rect x="8" y="8" width="804" height="194" rx="14" fill="#0b1728" stroke="#334155"/>
  <text x="24" y="34" fill="#e2e8f0" font-size="14" font-weight="700">STP classique</text>
  <g fill="#172943" stroke="#60a5fa"><rect x="24" y="50" width="130" height="44" rx="8"/><rect x="186" y="50" width="130" height="44" rx="8"/><rect x="348" y="50" width="130" height="44" rx="8"/><rect x="510" y="50" width="130" height="44" rx="8"/></g>
  <g fill="#dbeafe" font-size="12" text-anchor="middle"><text x="89" y="77">Blocking</text><text x="251" y="77">Listening</text><text x="413" y="77">Learning</text><text x="575" y="77">Forwarding</text></g>
  <g stroke="#60a5fa" stroke-width="2.5" fill="none" marker-end="url(#stp-state-arrow)"><path d="M154 72 L182 72"/><path d="M316 72 L344 72"/><path d="M478 72 L506 72"/></g>
  <circle r="4" fill="#93c5fd"><animateMotion dur="4s" repeatCount="indefinite" path="M154 72 L182 72 L316 72 L344 72 L478 72 L506 72"/></circle>
  <text x="24" y="124" fill="#e2e8f0" font-size="14" font-weight="700">RSTP / Rapid PVST+</text>
  <g fill="#123b32" stroke="#34d399"><rect x="24" y="140" width="180" height="42" rx="8"/><rect x="260" y="140" width="180" height="42" rx="8"/><rect x="496" y="140" width="180" height="42" rx="8"/></g>
  <g fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle"><text x="114" y="165">Discarding</text><text x="350" y="165">Learning</text><text x="586" y="165">Forwarding</text></g>
  <g stroke="#34d399" stroke-width="2.5" fill="none" marker-end="url(#stp-state-arrow)"><path d="M204 161 L256 161"/><path d="M440 161 L492 161"/></g>
</svg>
</div>

> **À retenir :** une transition rapide n'est pas garantie sur toutes les topologies. RSTP s'appuie sur les rôles de ports, les échanges BPDU et les caractéristiques du lien ; une mauvaise conception ou une incompatibilité peut retarder la convergence.


## 4. Les variantes de STP

Les commutateurs Cisco proposent plusieurs implémentations selon les familles et les versions logicielles. Vérifie les modes réellement supportés par ton matériel.

| Variante | Principe général | À retenir |
|---|---|---|
| STP / 802.1D | Spanning Tree classique | Convergence généralement plus lente lors de certaines transitions. |
| PVST+ | Instance STP par VLAN sur les équipements Cisco compatibles | Le root peut être choisi séparément pour chaque VLAN. |
| Rapid PVST+ | Variante rapide par VLAN | Convergence plus rapide que le STP classique dans les conditions appropriées. |
| MSTP | Plusieurs VLAN peuvent être associés à des instances MST | Réduit le nombre d'instances dans les grandes architectures, au prix d'une configuration de région cohérente. |

Ne mélange pas les termes « standard IEEE », « implémentation Cisco » et « mode par défaut ». Le mode par défaut est lié à la plateforme et à la version ; il faut le contrôler avec les commandes de vérification.


## 5. Configuration Cisco IOS de base

### 5.1. Inspecter l'état avant de changer quoi que ce soit

Sur chaque commutateur du laboratoire, commence par :

```cisco
show spanning-tree
show spanning-tree summary
show spanning-tree vlan 10
show interfaces trunk
show vlan brief
```

Ces commandes permettent notamment de repérer le mode STP, le pont racine, les rôles et états des ports, ainsi que la relation entre les VLAN et les trunks. Certaines syntaxes et sorties changent selon les plateformes.

### 5.2. Exemple de topologie

```text
                  SW1 — commutateur central
                  priorité STP planifiée
                    /               \
                 trunk             trunk
                  /                   \
              SW2 ------------------- SW3
                 lien redondant

VLAN 10 : ADMIN
VLAN 20 : COMPTA
VLAN 30 : SUPPORT

Objectif : choisir SW1 comme racine et conserver un chemin redondant
sans boucle de transfert.
```

### 5.3. Choisir intentionnellement le root bridge

Si la conception exige que SW1 soit racine du VLAN 10, utilise une commande de configuration prévue par la plateforme, puis contrôle le résultat :

```cisco
configure terminal
spanning-tree vlan 10 root primary
end
show spanning-tree vlan 10
```

`spanning-tree vlan 10 root primary` est une commande pratique disponible sur de nombreuses plateformes Cisco. Elle ajuste la priorité afin d'aider le commutateur à devenir racine ; elle ne dispense pas de vérifier le résultat. Pour une valeur explicite, une configuration telle que `spanning-tree vlan 10 priority 24576` peut être utilisée si la plateforme l'accepte et si cette valeur correspond au plan d'ingénierie.

Pour prévoir une racine de secours, le choix d'un second commutateur doit être fait dans le plan de topologie :

```cisco
! Exemple sur le commutateur de secours
configure terminal
spanning-tree vlan 10 priority 28672
end
show spanning-tree vlan 10
```

Les priorités effectives doivent rester cohérentes avec le plan. Les valeurs valides suivent des incréments imposés par le système étendu et les règles de la plateforme ; ne choisis pas une valeur arbitraire sans contrôler l'acceptation de la commande.

### 5.4. Choisir un mode rapide lorsque c'est approprié

Sur une plateforme Cisco IOS compatible, l'activation de Rapid PVST+ peut ressembler à :

```cisco
configure terminal
spanning-tree mode rapid-pvst
end
show spanning-tree summary
```

Ne change pas le mode STP d'un réseau de production sans vérifier la compatibilité de tous les commutateurs, la conception des trunks, les chemins redondants et le plan de retour arrière. Pour un laboratoire, cette commande permet d'observer le comportement de Rapid PVST+ lorsque la plateforme est compatible.

### 5.5. PortFast : pour les ports de terminaux

PortFast réduit l'attente avant que le port d'accès destiné à un terminal passe en transfert. Il convient aux ports connectés à des équipements terminaux, tels que les PC et les imprimantes, et non aux liaisons entre commutateurs.

Exemple sur un port d'accès vers un PC :

```cisco
configure terminal
interface GigabitEthernet1/0/10
 description PC_ADMIN
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
end
```

La syntaxe de l'interface et les commandes peuvent varier. Sur les versions qui le supportent, PortFast et BPDU Guard peuvent aussi être activés par défaut sur les ports concernés avec une commande globale telle que `spanning-tree portfast bpduguard default`. Vérifie d'abord la portée de la commande sur ton modèle.

**Pourquoi BPDU Guard ?** Un port utilisateur configuré en PortFast ne doit normalement pas recevoir de BPDU d'un autre commutateur. BPDU Guard place le port en état désactivé par erreur (*err-disabled*) s'il reçoit une BPDU, afin de limiter le risque lié au raccordement imprévu d'un équipement réseau. Il faut diagnostiquer la cause avant de réactiver le port.

> **Danger :** ne configure pas PortFast sur un lien inter-commutateurs. Ne désactive pas BPDU Guard uniquement pour faire disparaître une alerte sans comprendre pourquoi le port a reçu une BPDU.

### 5.6. Vérifier le résultat

Après les modifications :

```cisco
show spanning-tree vlan 10
show spanning-tree root
show spanning-tree interface GigabitEthernet1/0/1 detail
show spanning-tree summary
show interfaces status
show logging
```

Selon la plateforme, certaines variantes de commande peuvent ne pas exister. Utilise l'équivalent documenté. Vérifie que le root bridge est bien celui prévu, qu'un seul chemin actif sans boucle existe et que le lien de secours a un rôle/état cohérent avec la topologie.


## 6. Laboratoire Packet Tracer : observer une topologie redondante

### 6.1. Objectif

Construire un petit réseau de trois commutateurs reliés en triangle. Observer l'élection de la racine, identifier un port en attente et tester une reconvergence en interrompant un des liens actifs.

### 6.2. Matériel et câblage

- 3 commutateurs compatibles STP : SW1, SW2 et SW3 ;
- 2 PC de test, connectés à des ports d'accès de VLAN 10 ;
- 3 liaisons inter-commutateurs formant un triangle ;
- VLAN 10 créé sur les équipements concernés.

Exemple conceptuel :

```text
                   SW1
                  /    \
                 /      \
               SW2------SW3
                |         |
              PC-A      PC-B

Les trois liaisons inter-commutateurs créent un chemin redondant.
STP maintient un port en attente pour éviter une boucle active.
```

### 6.3. Étape A — créer le VLAN et les trunks

Sur chaque commutateur du lab, crée le VLAN 10 si la configuration locale l'exige :

```cisco
configure terminal
vlan 10
 name ADMIN
end
```

Sur chaque liaison inter-commutateurs, configure un trunk statique adapté aux interfaces réelles. Exemple :

```cisco
configure terminal
interface GigabitEthernet1/0/1
 description TRUNK_VERS_AUTRE_SWITCH
 switchport mode trunk
 switchport trunk allowed vlan 10
 no shutdown
end
```

Répète l'étape sur les interfaces qui relient les trois commutateurs. N'utilise pas le même nom d'interface sans l'adapter au matériel. Certaines plateformes exigent d'autres commandes d'encapsulation ou ne disposent pas de la même syntaxe.

### 6.4. Étape B — rendre SW1 racine

Sur SW1 :

```cisco
configure terminal
spanning-tree vlan 10 root primary
end
```

Sur SW2 et SW3, vérifie la racine :

```cisco
show spanning-tree vlan 10
```

Relève le Bridge ID de la racine, le Root ID et le rôle des ports. Selon la topologie et les paramètres, tu dois identifier un port root sur chaque commutateur non racine et un port désigné sur chaque segment actif.

### 6.5. Étape C — repérer le lien de secours

Sur SW2 et SW3, exécute :

```cisco
show spanning-tree vlan 10
```

Repère le port qui ne transfère pas les trames utilisateurs dans la topologie courante. Note le rôle (par exemple alternate en RSTP) et l'état affiché. Dans le STP classique, les libellés d'état diffèrent.

N'essaie pas de deviner le port bloqué à partir du dessin seul : le résultat dépend des coûts de lien, du Bridge ID, des priorités de ports et de la variante STP réellement utilisée.

### 6.6. Étape D — provoquer une panne contrôlée

Dans le laboratoire uniquement, désactive une liaison qui fait partie du chemin actif :

```cisco
configure terminal
interface GigabitEthernet1/0/1
 shutdown
end
```

Contrôle à nouveau :

```cisco
show spanning-tree vlan 10
show interfaces status
```

Observe si le protocole a sélectionné un autre chemin. Teste ensuite la connectivité entre les PC selon l'adressage et la configuration de couche 2/3 du lab. Rétablis le lien lorsque tu as terminé :

```cisco
configure terminal
interface GigabitEthernet1/0/1
 no shutdown
end
```

Attends la reconvergence puis vérifie la topologie de nouveau.

### 6.7. Compte rendu à produire

Complète le tableau ci-dessous après le lab :

| Vérification | Avant la panne | Après la panne | Après rétablissement |
|---|---|---|---|
| Root Bridge | À relever | À relever | À relever |
| Port root de SW2 | À relever | À relever | À relever |
| Port root de SW3 | À relever | À relever | À relever |
| Port de secours | À relever | À relever | À relever |
| Connectivité attendue | À tester | À tester | À tester |
| Temps de reconvergence observé | À relever | À relever | À relever |

Le temps observé est une mesure du laboratoire, pas une garantie applicable à toutes les topologies ou à toutes les variantes de STP.


## 7. Dépannage débutant

### 7.1. Le mauvais commutateur est racine

**Symptôme :** `show spanning-tree vlan 10` indique un Root ID différent de celui prévu.

**Vérifications :**

```cisco
show spanning-tree vlan 10
show spanning-tree root
show running-config | include spanning-tree
```

**Pistes :** vérifier la priorité configurée, la MAC du pont, la priorité effective, l'instance/VLAN concerné et la présence d'un commutateur inattendu. Ne change pas les priorités en cascade sans comprendre la topologie.

### 7.2. Le réseau semble boucler ou les MAC changent de port

**Symptômes possibles :** pertes intermittentes, trafic de diffusion très élevé, messages de MAC flapping.

**Vérifications :**

```cisco
show spanning-tree summary
show spanning-tree vlan 10
show interfaces trunk
show logging
```

Inspecte le câblage, les trunks, les ports en forwarding et les changements récents. Ne désactive pas STP comme solution de contournement : cela peut aggraver l'incident. Si une boucle est active, isole la cause de manière contrôlée et suis la procédure d'exploitation.

### 7.3. Un port est en err-disabled

Si BPDU Guard est activé et que le port reçoit une BPDU, le port peut être désactivé par protection. Inspecte le journal et l'équipement raccordé avant toute réactivation. Ne mets pas PortFast sur un lien qui relie deux commutateurs.

### 7.4. Un port attendu comme bloqué est en forwarding

Vérifie d'abord la variante STP et le VLAN observé. Une topologie peut posséder une liaison redondante qui ne participe pas à une instance donnée, ou un lien peut être regroupé dans un EtherChannel. Contrôle les rôles réels, la connectivité, les trunks et les changements de topologie. Tous les liens physiques ne sont pas forcément affichés individuellement dans STP si le transfert s'appuie sur un port-channel.


## 8. Exercices d'auto-évaluation

### Question 1

Quel problème STP cherche-t-il principalement à prévenir dans un réseau Ethernet commuté ?

A. Les doublons d'adresses IP  
B. Les boucles de couche 2  
C. Les erreurs de masque IP  
D. L'absence de DNS

### Question 2

Quel commutateur est élu Root Bridge ?

A. Celui qui possède le plus grand nom d'hôte  
B. Celui avec le plus grand numéro de VLAN  
C. Celui dont le Bridge ID est le plus petit  
D. Celui dont tous les ports sont en access

### Question 3

Quel est le rôle du Root Port sur un commutateur non racine ?

A. Transporter uniquement le VLAN natif  
B. Fournir le meilleur chemin vers la racine  
C. Désactiver toutes les BPDU  
D. Router entre les VLAN

### Question 4

Sur quel type de port PortFast est-il normalement destiné à être utilisé ?

A. Un port d'accès relié à un terminal  
B. Un trunk vers un autre commutateur  
C. Tous les ports de backbone sans distinction  
D. Un port qui doit toujours bloquer les trames

### Question 5

Que peut faire BPDU Guard sur un port concerné lorsqu'il reçoit une BPDU ?

A. Créer automatiquement un VLAN  
B. Activer le routage inter-VLAN  
C. Placer le port en état err-disabled pour limiter le risque de boucle  
D. Remplacer la priorité du Root Bridge

### Question 6

Pourquoi ne faut-il pas désactiver STP pour résoudre rapidement une boucle présumée ?

A. Parce que les VLAN disparaissent toujours  
B. Parce que cela peut permettre une boucle de couche 2 active  
C. Parce que STP gère le DNS  
D. Parce que les adresses MAC sont routées par STP

### Question 7 — Analyse

SW1 a une priorité effective plus basse que SW2 pour le VLAN 10. Les autres paramètres ne changent pas et aucun autre commutateur n'a un Bridge ID inférieur. Quel équipement doit être racine pour cette instance ? Explique en une ou deux phrases.

### Question 8 — Commandes

Quelles commandes utiliserais-tu pour vérifier le Root Bridge, les rôles de port du VLAN 10 et les trunks opérationnels ? Écris au moins deux commandes.


## 9. Corrigés

1. **B** — STP empêche les boucles actives de couche 2 en construisant une topologie sans boucle.
2. **C** — Le Bridge ID le plus petit gagne l'élection de racine.
3. **B** — Le Root Port fournit à un commutateur non racine son meilleur chemin vers le root bridge.
4. **A** — PortFast est prévu pour les ports orientés terminaux. Il ne doit pas être appliqué sans précaution aux liens inter-commutateurs.
5. **C** — BPDU Guard peut placer le port en err-disabled quand il reçoit une BPDU, suivant la configuration et la plateforme.
6. **B** — Désactiver STP peut laisser une boucle active et déclencher une perturbation majeure.
7. **SW1** — Si son Bridge ID effectif est bien le plus petit pour cette instance, SW1 est élu racine. La MAC et les paramètres du système étendu peuvent départager les équipements si la priorité effective est égale.
8. Exemples : `show spanning-tree vlan 10`, `show spanning-tree root`, `show interfaces trunk`, `show spanning-tree summary`.


## 10. Mémo des commandes

| Besoin | Commande indicative |
|---|---|
| Vérifier STP pour un VLAN | `show spanning-tree vlan 10` |
| Vérifier la racine | `show spanning-tree root` |
| Voir un résumé STP | `show spanning-tree summary` |
| Vérifier les trunks | `show interfaces trunk` |
| Choisir une racine de façon assistée | `spanning-tree vlan 10 root primary` |
| Définir une priorité explicite | `spanning-tree vlan 10 priority 24576` |
| Activer Rapid PVST+ si pris en charge | `spanning-tree mode rapid-pvst` |
| PortFast sur un port d'accès | `spanning-tree portfast` |
| BPDU Guard par interface | `spanning-tree bpduguard enable` |

Les commandes de configuration doivent être utilisées uniquement après vérification de la prise en charge par l'équipement. Une modification STP peut changer la topologie active : documente l'état initial, applique une modification à la fois et vérifie la connectivité.

## 11. À retenir

- STP évite les boucles de couche 2 tout en préservant la redondance physique.
- Le commutateur ayant le plus petit Bridge ID est élu Root Bridge.
- Les rôles importants sont Root Port, Designated Port et, en RSTP, Alternate Port.
- Une liaison redondante peut rester physiquement active tout en étant en attente pour éviter une boucle de transfert.
- Rapid STP améliore généralement la vitesse de convergence, mais son résultat dépend de la topologie et de la configuration.
- PortFast est destiné aux ports de terminaux ; BPDU Guard protège ces ports contre la réception inattendue de BPDU.
- Vérifie toujours avec `show spanning-tree` et n'arrête pas STP pour masquer un problème.

## 12. Références techniques

- Cisco, *STP Port Roles*, documentation Catalyst : https://www.cisco.com/c/en/us/td/docs/IIOT/switches/ie9300/stp/ie93xx-stp/wrapper-spanning-tree-protocol/r-stp-port-roles.html
- Cisco, *Understand Spanning Tree PortFast and BPDU Guard Features* : https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10586-65.html
- Cisco, *STP Configuration Guide — Cisco IOS XE* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/stp/stp-configuration-guide/m-stp.html

Ces références sont des points de départ. Pour une configuration réelle, sélectionne le guide correspondant précisément au modèle de commutateur et à la version logicielle.
