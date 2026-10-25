# VLAN et segmentation des réseaux — Niveau Intermédiaire

**Niveau :** Intermédiaire  
**Durée indicative :** 75 à 100 minutes  
**Prérequis :** avoir suivi le cours VLAN Débutant ou savoir créer et nommer des VLAN, affecter des ports access, configurer un trunk 802.1Q et utiliser `show vlan brief` / `show interfaces trunk`.  
**Environnement conseillé :** Cisco Packet Tracer ou commutateurs Cisco IOS/IOS XE compatibles avec les commandes présentées.

## Objectifs pédagogiques

À la fin de ce cours, tu dois pouvoir :

- raisonner sur la continuité d'un VLAN à travers plusieurs commutateurs ;
- contrôler finement les VLAN autorisés sur un trunk sans supprimer accidentellement des VLAN utiles ;
- expliquer le rôle du VLAN natif et diagnostiquer une incohérence entre deux extrémités ;
- comprendre les négociations DTP et configurer les trunks de façon explicite ;
- différencier VLAN de données, VLAN voix et VLAN de gestion ;
- vérifier la configuration d'un trunk associé à un EtherChannel ;
- suivre une méthode de dépannage couche par couche ;
- planifier un changement VLAN avec sauvegarde, tests et retour arrière.

> **Positionnement :** le cours Débutant explique ce qu'est un VLAN, comment créer un VLAN localement et comment configurer un premier port access/trunk. Ici, on étudie les situations multi-commutateurs, les paramètres qui affectent réellement le transport et les méthodes d'exploitation. La configuration du routage inter-VLAN et les mécanismes avancés de sécurité VLAN seront traités plus en profondeur dans les cours dédiés.

> **Compatibilité :** les exemples utilisent une syntaxe Cisco IOS courante. Les commandes disponibles, les noms d'interfaces et certains comportements varient selon le modèle, la version logicielle et les capacités de Packet Tracer. Dans un vrai réseau, vérifie d'abord la documentation de ta plateforme.


## 1. Passer d'un VLAN local à une architecture multi-commutateurs

### 1.1. Le problème de continuité

Créer le VLAN 20 sur SW1 ne garantit pas qu'il existe sur SW2 ou qu'il puisse traverser toutes les liaisons. Chaque maillon du chemin doit être cohérent : le VLAN doit être présent sur les commutateurs concernés, le port d'accès doit être affecté au bon VLAN et chaque trunk du chemin doit autoriser ce VLAN.

```text
PC-A                  SW1                    SW2                 PC-B
VLAN 20           VLAN 20 présent        VLAN 20 présent        VLAN 20
192.168.20.10     Gi0/1 ===== trunk ===== Gi0/1             192.168.20.20
                     VLAN 20 autorisé ?

Chemin correct : VLAN présent sur SW1 + trunk autorisé + VLAN présent sur SW2.
Un seul maillon mal configuré peut interrompre la connectivité de couche 2.
```

### 1.2. Le parcours d'une trame

Lorsqu'un poste envoie une trame, le commutateur apprend généralement l'adresse MAC source dans le contexte du VLAN associé au port d'entrée. Si la destination se trouve derrière un autre commutateur, la trame peut être transférée sur le trunk si ce VLAN est actif et autorisé sur cette liaison. Le commutateur en aval traite ensuite la trame dans le VLAN correspondant.

<figure style="margin:1.5rem 0;padding:1rem;border:1px solid #334155;border-radius:16px;background:#0b1220;color:#e2e8f0">
<svg viewBox="0 0 820 290" role="img" aria-label="Parcours d'une trame du PC-A au PC-B à travers deux commutateurs dans le VLAN 20" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes vlanMidTrace { to { stroke-dashoffset: -32; } } .vlan-mid-trace { stroke-dasharray: 8 8; animation: vlanMidTrace 1.8s linear infinite; }</style>
  <rect x="8" y="8" width="804" height="274" rx="14" fill="#0b1220" stroke="#334155"/>
  <text x="410" y="35" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">VLAN 20 — un chemin Ethernet cohérent de bout en bout</text>
  <rect x="28" y="83" width="122" height="78" rx="10" fill="#102e2b" stroke="#2dd4bf" stroke-width="1.5"/><text x="89" y="109" text-anchor="middle" fill="#99f6e4" font-size="14" font-weight="700">PC-A</text><text x="89" y="132" text-anchor="middle" fill="#cbd5e1" font-size="11">VLAN 20</text>
  <rect x="224" y="68" width="142" height="108" rx="12" fill="#17243a" stroke="#60a5fa" stroke-width="1.5"/><text x="295" y="97" text-anchor="middle" fill="#bfdbfe" font-size="15" font-weight="700">SW1</text><text x="295" y="121" text-anchor="middle" fill="#e2e8f0" font-size="11">VLAN 20 présent</text><text x="295" y="141" text-anchor="middle" fill="#94a3b8" font-size="10">Port access correct</text>
  <rect x="454" y="68" width="142" height="108" rx="12" fill="#17243a" stroke="#60a5fa" stroke-width="1.5"/><text x="525" y="97" text-anchor="middle" fill="#bfdbfe" font-size="15" font-weight="700">SW2</text><text x="525" y="121" text-anchor="middle" fill="#e2e8f0" font-size="11">VLAN 20 présent</text><text x="525" y="141" text-anchor="middle" fill="#94a3b8" font-size="10">Port access correct</text>
  <rect x="670" y="83" width="122" height="78" rx="10" fill="#102e2b" stroke="#2dd4bf" stroke-width="1.5"/><text x="731" y="109" text-anchor="middle" fill="#99f6e4" font-size="14" font-weight="700">PC-B</text><text x="731" y="132" text-anchor="middle" fill="#cbd5e1" font-size="11">VLAN 20</text>
  <path d="M150 122 H224 M366 122 H454 M596 122 H670" stroke="#64748b" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path class="vlan-mid-trace" d="M150 122 H224 M366 122 H454 M596 122 H670" stroke="#34d399" stroke-width="3" fill="none" stroke-linecap="round"/>
  <text x="410" y="202" text-anchor="middle" fill="#6ee7b7" font-size="13" font-weight="700">Trunk : VLAN 20 autorisé et actif</text>
  <path d="M295 176 V222 H525 V176" fill="none" stroke="#475569" stroke-width="1.5" stroke-dasharray="5 5"/>
  <text x="410" y="244" text-anchor="middle" fill="#cbd5e1" font-size="12">La continuité dépend de chaque lien et de chaque base VLAN locale.</text>
  <text x="410" y="263" text-anchor="middle" fill="#94a3b8" font-size="10">Animation : la ligne pointillée suit les trois segments de connexion.</text>
</svg>
<figcaption style="font-size:.88rem;color:#94a3b8;margin-top:.6rem">Le mouvement représente la progression logique sur le chemin vert ; ce n'est pas une capture réelle du trafic.</figcaption>
</figure>

### 1.3. Les quatre conditions à contrôler

| Condition | Vérification | Ce qu'elle permet de conclure |
|---|---|---|
| Le VLAN existe localement | `show vlan brief` | Le commutateur connaît le VLAN et son état local. |
| Le port utilisateur est correct | `show interfaces <interface> switchport` | Le port est affecté au VLAN attendu et n'est pas configuré accidentellement en trunk. |
| Le trunk est opérationnel | `show interfaces trunk` | La liaison transporte plusieurs VLAN selon son état effectif. |
| Le VLAN est autorisé sur chaque trunk | `show interfaces trunk` et configuration | Le VLAN figure dans la liste autorisée sur chaque maillon nécessaire. |

Ces contrôles sont complémentaires. Aucune commande isolée ne démontre à elle seule que le service de bout en bout fonctionne.


## 2. Lire le marquage IEEE 802.1Q

### 2.1. Pourquoi une trame trunk porte-t-elle une étiquette ?

Un trunk peut transporter des trames appartenant à plusieurs VLAN sur une seule liaison physique. Le marquage 802.1Q permet au commutateur récepteur d'associer une trame au bon VLAN. La trame marquée contient notamment un identifiant VLAN de 12 bits, ainsi que des champs de priorité et d'indication de format selon la structure du tag.

```text
TRAME ETHERNET (vue simplifiée)
┌───────────┬───────────┬────────────┬──────────┬─────────┐
│ MAC dest. │ MAC src.  │ Type/Long. │ Données  │ FCS     │
└───────────┴───────────┴────────────┴──────────┴─────────┘

TRAME SUR TRUNK AVEC TAG 802.1Q
┌───────────┬───────────┬──────────────┬────────────┬─────────┬─────┐
│ MAC dest. │ MAC src.  │ Tag 802.1Q   │ Type/Long. │ Données │ FCS │
└───────────┴───────────┴──────────────┴────────────┴─────────┴─────┘
                               └─ TPID + TCI ─┘
                                   ├─ PCP : priorité
                                   ├─ DEI : indication de rejet
                                   └─ VID : identifiant VLAN
```

### 2.2. Décomposition visuelle du tag

<figure style="margin:1.5rem 0;padding:1rem;border:1px solid #334155;border-radius:16px;background:#0b1220;color:#e2e8f0">
<svg viewBox="0 0 800 250" role="img" aria-label="Décomposition conceptuelle des champs du tag IEEE 802.1Q" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes vlanTagPulse { 0%,100% { opacity:.72; } 50% { opacity:1; } } .vlan-tag-highlight { animation:vlanTagPulse 2.4s ease-in-out infinite; }</style>
  <rect x="10" y="10" width="780" height="230" rx="14" fill="#0b1220" stroke="#334155"/>
  <text x="400" y="39" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">Tag IEEE 802.1Q — 4 octets (32 bits)</text>
  <rect x="38" y="66" width="724" height="72" rx="8" fill="#111827" stroke="#64748b"/>
  <rect x="38" y="66" width="181" height="72" rx="8" fill="#17344c" stroke="#60a5fa" stroke-width="1.5"/>
  <rect x="219" y="66" width="543" height="72" rx="8" fill="#162f2d" stroke="#34d399" stroke-width="1.5"/>
  <text x="128" y="95" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">TPID</text><text x="128" y="117" text-anchor="middle" fill="#e2e8f0" font-size="12">16 bits</text>
  <text x="490" y="94" text-anchor="middle" fill="#a7f3d0" font-size="14" font-weight="700">TCI — Tag Control Information</text>
  <line x1="309" y1="103" x2="309" y2="138" stroke="#6ee7b7"/><line x1="400" y1="103" x2="400" y2="138" stroke="#6ee7b7"/><line x1="491" y1="103" x2="491" y2="138" stroke="#6ee7b7"/><line x1="582" y1="103" x2="582" y2="138" stroke="#6ee7b7"/>
  <text x="264" y="157" text-anchor="middle" fill="#94a3b8" font-size="11">PCP (3 bits)</text><text x="355" y="157" text-anchor="middle" fill="#94a3b8" font-size="11">DEI (1 bit)</text><text x="627" y="157" text-anchor="middle" fill="#6ee7b7" font-size="11" font-weight="700">VID (12 bits)</text>
  <g class="vlan-tag-highlight"><rect x="546" y="171" width="194" height="42" rx="8" fill="#064e3b" stroke="#34d399" stroke-width="1.5"/><text x="643" y="189" text-anchor="middle" fill="#a7f3d0" font-size="12" font-weight="700">VID = 20</text><text x="643" y="203" text-anchor="middle" fill="#d1fae5" font-size="10">Exemple : VLAN COMPTA</text></g>
  <text x="46" y="190" fill="#cbd5e1" font-size="11">PCP : priorité de couche 2</text><text x="46" y="207" fill="#cbd5e1" font-size="11">DEI : indicateur d'éligibilité au rejet</text>
</svg>
<figcaption style="font-size:.88rem;color:#94a3b8;margin-top:.6rem">Schéma conceptuel des champs principaux. L'animation met en évidence le VID pour montrer quel champ identifie le VLAN.</figcaption>
</figure>

Le champ VID dispose de 12 bits. La plage d'identifiants usuels va jusqu'à 4094, mais les identifiants réservés, les plages supportées et leur mode de gestion dépendent de la plateforme. Ne confonds pas l'identifiant VLAN avec le numéro de port, le sous-réseau IP ou la valeur du champ de priorité.

### 2.3. Trames marquées et VLAN natif

Sur un trunk 802.1Q, le trafic des VLAN est en général transporté avec un tag. Le VLAN natif est l'exception habituelle : son trafic peut être envoyé sans marquage, selon la configuration du trunk et de la plateforme. Les deux côtés d'une liaison doivent avoir une configuration native cohérente.

Un trunk qui transporte VLAN 10, 20 et 30 n'implique pas que les trois VLAN sont natifs. Il s'agit d'une liste de VLAN autorisés ; le VLAN natif est un paramètre distinct.


## 3. Limiter les VLAN sur un trunk

### 3.1. Pourquoi éviter une liste trop large ?

De nombreux commutateurs autorisent par défaut un grand nombre de VLAN sur les trunks. Une architecture mieux contrôlée n'autorise sur chaque lien que les VLAN nécessaires aux équipements situés en aval. Cela réduit les erreurs de propagation du trafic, facilite le diagnostic et limite l'exposition inutile d'un VLAN à un segment.

La liste autorisée est configurée **par interface trunk**. Elle ne crée pas le VLAN dans la base locale et n'affecte pas directement les autres trunks du commutateur.

<figure style="margin:1.5rem 0;padding:1rem;border:1px solid #334155;border-radius:16px;background:#0b1220;color:#e2e8f0">
<svg viewBox="0 0 820 300" role="img" aria-label="Trois VLAN arrivent à un trunk, mais seuls VLAN 10 et 20 sont autorisés sur le lien vers SW2" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes vlanAllowedTrace { to { stroke-dashoffset:-28; } } .vlan-allowed-trace { stroke-dasharray:7 7; animation:vlanAllowedTrace 1.7s linear infinite; }</style>
  <rect x="10" y="10" width="800" height="280" rx="14" fill="#0b1220" stroke="#334155"/>
  <text x="410" y="37" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">Liste autorisée sur le trunk : VLAN 10,20</text>
  <rect x="32" y="72" width="180" height="166" rx="12" fill="#17243a" stroke="#60a5fa"/><text x="122" y="99" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">SW1</text>
  <rect x="52" y="114" width="140" height="28" rx="6" fill="#123b35" stroke="#34d399"/><text x="122" y="132" text-anchor="middle" fill="#d1fae5" font-size="11">VLAN 10 — ADMIN</text>
  <rect x="52" y="151" width="140" height="28" rx="6" fill="#123b35" stroke="#34d399"/><text x="122" y="169" text-anchor="middle" fill="#d1fae5" font-size="11">VLAN 20 — COMPTA</text>
  <rect x="52" y="188" width="140" height="28" rx="6" fill="#3b2224" stroke="#fb7185"/><text x="122" y="206" text-anchor="middle" fill="#fecdd3" font-size="11">VLAN 30 — SUPPORT</text>
  <rect x="605" y="80" width="175" height="150" rx="12" fill="#17243a" stroke="#60a5fa"/><text x="692" y="108" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">SW2</text><text x="692" y="133" text-anchor="middle" fill="#e2e8f0" font-size="11">VLAN 10 présent</text><text x="692" y="153" text-anchor="middle" fill="#e2e8f0" font-size="11">VLAN 20 présent</text><text x="692" y="173" text-anchor="middle" fill="#fda4af" font-size="11">VLAN 30 non transporté</text>
  <path d="M212 130 H605" stroke="#475569" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path class="vlan-allowed-trace" d="M212 130 H605" stroke="#34d399" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M285 151 V208 H529 V151" fill="none" stroke="#fb7185" stroke-width="2" stroke-dasharray="5 5"/><path d="M397 181 L415 199 M415 181 L397 199" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/>
  <text x="410" y="254" text-anchor="middle" fill="#a7f3d0" font-size="12" font-weight="700">VLAN 10 et 20 : autorisés</text><text x="410" y="272" text-anchor="middle" fill="#fda4af" font-size="12">VLAN 30 : absent de la liste autorisée</text>
</svg>
<figcaption style="font-size:.88rem;color:#94a3b8;margin-top:.6rem">Un VLAN existant sur les deux commutateurs peut quand même être bloqué sur un trunk s'il n'y figure pas dans la liste autorisée.</figcaption>
</figure>

### 3.2. Lire les commandes sans effacer la liste existante

```cisco
show interfaces trunk
show running-config interface gigabitEthernet0/1
```

Exemple d'une liste explicite sur un lien dont les seuls VLAN nécessaires sont 10, 20 et 99 :

```cisco
configure terminal
interface gigabitEthernet0/1
 description TRUNK_VERS_SW2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,99
end
```

**Attention à l'effet de remplacement.** Sur les plateformes Cisco courantes, la commande `switchport trunk allowed vlan 10,20,99` définit la liste à ces VLAN ; elle peut retirer de la liste les VLAN qui y figuraient auparavant. Si l'objectif est uniquement d'ajouter le VLAN 99, une syntaxe avec `add` peut être adaptée :

```cisco
interface gigabitEthernet0/1
 switchport trunk allowed vlan add 99
```

La syntaxe exacte doit être confirmée sur la plateforme. Avant la modification, capture la liste effective et identifie les services qui en dépendent. Après la modification, vérifie la liste et teste le trafic.

### 3.3. Trois états à ne pas confondre

| État | Signification | Commande utile |
|---|---|---|
| VLAN créé | Le VLAN figure dans la base locale | `show vlan brief` |
| VLAN autorisé | Le trunk permet ce VLAN dans sa liste | `show interfaces trunk` et configuration |
| VLAN actif et transféré | Les conditions locales et opérationnelles permettent le transport | `show interfaces trunk`, STP, table MAC et test de connectivité |

> **À retenir :** autoriser un VLAN sur un trunk ne le crée pas. Créer le VLAN ne l'ajoute pas forcément à la liste autorisée d'un trunk restreint. Et ces deux étapes ne prouvent pas à elles seules que le trafic utilisateur circule correctement.


## 4. Comprendre et contrôler le VLAN natif

### 4.1. Le rôle du VLAN natif

Sur un trunk 802.1Q, le VLAN natif sert généralement à classer le trafic reçu sans tag. Sur les plateformes Cisco, VLAN 1 est souvent le VLAN natif par défaut, mais on peut employer un autre VLAN selon la conception. Le choix doit être cohérent aux deux extrémités.

### 4.2. Que se passe-t-il en cas d'incohérence ?

Imaginons SW1 configuré avec le VLAN natif 99 et SW2 avec le VLAN natif 1. Une trame non marquée émise sur un côté et reçue sur l'autre peut être classée dans un VLAN différent. Selon la nature du trafic et la plateforme, l'incohérence peut provoquer des avertissements, des problèmes de connectivité et des risques de sécurité.

```text
SW1                                                  SW2
Trunk                                                Trunk
Native VLAN 99  ======== trames non marquées =====> Native VLAN 1
                       ATTENTION
   Le trafic non marqué peut être associé à des VLAN différents.
```

<figure style="margin:1.5rem 0;padding:1rem;border:1px solid #334155;border-radius:16px;background:#0b1220;color:#e2e8f0">
<svg viewBox="0 0 800 252" role="img" aria-label="Incohérence du VLAN natif : les trames non marquées sont classées différemment aux deux extrémités" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes nativeMismatchTrace { to { stroke-dashoffset:-24; } } .native-mismatch-trace { stroke-dasharray:6 6; animation:nativeMismatchTrace 1.8s linear infinite; }</style>
  <rect x="10" y="10" width="780" height="232" rx="14" fill="#0b1220" stroke="#334155"/>
  <rect x="34" y="72" width="192" height="100" rx="12" fill="#17243a" stroke="#60a5fa" stroke-width="1.5"/><text x="130" y="99" text-anchor="middle" fill="#bfdbfe" font-size="15" font-weight="700">SW1</text><text x="130" y="123" text-anchor="middle" fill="#a7f3d0" font-size="12">Native VLAN 99</text><text x="130" y="146" text-anchor="middle" fill="#94a3b8" font-size="10">Émission sans tag</text>
  <rect x="574" y="72" width="192" height="100" rx="12" fill="#17243a" stroke="#60a5fa" stroke-width="1.5"/><text x="670" y="99" text-anchor="middle" fill="#bfdbfe" font-size="15" font-weight="700">SW2</text><text x="670" y="123" text-anchor="middle" fill="#fda4af" font-size="12">Native VLAN 1</text><text x="670" y="146" text-anchor="middle" fill="#94a3b8" font-size="10">Classement à réception</text>
  <path d="M226 122 H574" stroke="#64748b" stroke-width="5" fill="none" stroke-linecap="round"/><path class="native-mismatch-trace" d="M226 122 H574" stroke="#f59e0b" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M377 102 L423 148 M423 102 L377 148" stroke="#fb7185" stroke-width="3" stroke-linecap="round"/>
  <text x="400" y="47" text-anchor="middle" fill="#fda4af" font-size="15" font-weight="700">MISMATCH</text>
  <text x="400" y="201" text-anchor="middle" fill="#e2e8f0" font-size="12">Une trame non marquée n'indique pas son VLAN dans un tag 802.1Q.</text><text x="400" y="220" text-anchor="middle" fill="#94a3b8" font-size="11">Aligner la configuration native selon le plan réseau et vérifier les deux côtés.</text>
</svg>
<figcaption style="font-size:.88rem;color:#94a3b8;margin-top:.6rem">L'animation suit le lien physique et signale le point d'incohérence ; elle ne représente pas une capture de paquets.</figcaption>
</figure>

### 4.3. Vérifier puis corriger

```cisco
show interfaces trunk
show running-config interface gigabitEthernet0/1
```

Si la politique du réseau prévoit VLAN 999 comme VLAN natif, un exemple de configuration est :

```cisco
configure terminal
interface gigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 999
end
```

La commande doit être appliquée de manière coordonnée aux deux extrémités de la liaison. Le VLAN 999 doit exister et être traité conformément à la politique locale ; il ne faut pas supposer qu'un simple changement du native VLAN remplace les autres contrôles. Vérifie aussi que ce VLAN n'est pas utilisé par des terminaux si la politique prévoit un VLAN natif dédié et inutilisé.


## 5. DTP et établissement du trunk

### 5.1. Pourquoi le mode administratif compte

Sur certaines plateformes Cisco, DTP (*Dynamic Trunking Protocol*) négocie l'établissement d'un trunk. Les modes typiques sont `access`, `trunk`, `dynamic auto` et `dynamic desirable`. Leur présence et leur comportement par défaut dépendent de la plateforme.

| SW1 | SW2 | Résultat habituel sur les plateformes DTP classiques |
|---|---|---|
| `dynamic auto` | `dynamic auto` | Pas de trunk négocié |
| `dynamic desirable` | `dynamic auto` | Trunk généralement négocié |
| `trunk` | `trunk` | Trunk forcé des deux côtés |
| `access` | `trunk` | Configuration incohérente ; ne pas compter sur un trunk fonctionnel correct |
| `trunk` + `nonegotiate` | `trunk` manuel | Trunk sans émission de négociation DTP sur l'interface configurée ainsi |

### 5.2. Recommandation d'exploitation

Sur une liaison connue entre deux commutateurs, on préfère souvent configurer explicitement les deux côtés en trunk et désactiver la négociation DTP si la plateforme le permet et si la conception le requiert. Un port de terminal utilisateur doit être forcé en mode access et ne pas être laissé dans un mode dynamique inutile.

Exemple pour un trunk manuel vers un commutateur compatible :

```cisco
configure terminal
interface gigabitEthernet0/1
 description TRUNK_VERS_SW2
 switchport mode trunk
 switchport nonegotiate
 switchport trunk allowed vlan 10,20,30,99
end
```

`switchport nonegotiate` doit être utilisé uniquement si la commande est prise en charge et que l'autre extrémité est configurée manuellement de façon compatible. Ne l'applique pas aveuglément sur un lien existant : relève d'abord le mode opérationnel, la configuration distante et les VLAN nécessaires.

### 5.3. Vérifications DTP et mode opérationnel

```cisco
show interfaces gigabitEthernet0/1 switchport
show interfaces trunk
show running-config interface gigabitEthernet0/1
```

Ne déduis pas l'état opérationnel uniquement de la configuration. Compare le mode administratif et opérationnel. Si le lien ne devient pas trunk, vérifie aussi l'état physique, la compatibilité de l'équipement voisin et les journaux.


## 6. VLAN de données et VLAN voix

### 6.1. Pourquoi deux VLAN sur un seul port access ?

Dans de nombreux bureaux, un téléphone IP est raccordé au port du commutateur et le PC est raccordé derrière le téléphone. Le port du commutateur reste configuré comme port access pour les données ; le téléphone peut envoyer le trafic voix dans un VLAN voix distinct, avec un marquage approprié selon sa configuration. Le trafic du PC reste dans le VLAN de données.

<figure style="margin:1.5rem 0;padding:1rem;border:1px solid #334155;border-radius:16px;background:#0b1220;color:#e2e8f0">
<svg viewBox="0 0 820 290" role="img" aria-label="Un port de commutateur relie un téléphone IP sur le VLAN voix 110 et un PC sur le VLAN de données 10" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes voiceDataTrace { to { stroke-dashoffset:-28; } } .voice-data-trace { stroke-dasharray:7 7; animation:voiceDataTrace 1.7s linear infinite; }</style>
  <rect x="10" y="10" width="800" height="270" rx="14" fill="#0b1220" stroke="#334155"/>
  <text x="410" y="37" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">Un port access, deux catégories de trafic</text>
  <rect x="30" y="91" width="142" height="98" rx="12" fill="#17243a" stroke="#60a5fa" stroke-width="1.5"/><text x="101" y="119" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">SW1</text><text x="101" y="141" text-anchor="middle" fill="#e2e8f0" font-size="11">Gi0/10</text><text x="101" y="163" text-anchor="middle" fill="#a7f3d0" font-size="10">Access + Voice VLAN</text>
  <rect x="320" y="72" width="184" height="62" rx="10" fill="#3a2a14" stroke="#fbbf24" stroke-width="1.5"/><text x="412" y="96" text-anchor="middle" fill="#fde68a" font-size="14" font-weight="700">Téléphone IP</text><text x="412" y="116" text-anchor="middle" fill="#e2e8f0" font-size="11">Voix : VLAN 110</text>
  <rect x="320" y="159" width="184" height="62" rx="10" fill="#123b35" stroke="#34d399" stroke-width="1.5"/><text x="412" y="184" text-anchor="middle" fill="#a7f3d0" font-size="14" font-weight="700">PC derrière le téléphone</text><text x="412" y="204" text-anchor="middle" fill="#e2e8f0" font-size="11">Données : VLAN 10</text>
  <path d="M172 140 H245 V103 H320" stroke="#64748b" stroke-width="5" fill="none" stroke-linecap="round"/><path class="voice-data-trace" d="M172 140 H245 V103 H320" stroke="#fbbf24" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M412 134 V159" stroke="#64748b" stroke-width="5" fill="none" stroke-linecap="round"/><path class="voice-data-trace" d="M412 134 V159" stroke="#34d399" stroke-width="3" fill="none" stroke-linecap="round"/>
  <text x="410" y="250" text-anchor="middle" fill="#cbd5e1" font-size="12">La distinction des flux ne remplace ni la QoS ni les politiques de sécurité.</text><text x="410" y="266" text-anchor="middle" fill="#94a3b8" font-size="10">Le comportement précis dépend du téléphone, de CDP/LLDP et de la plateforme.</text>
</svg>
<figcaption style="font-size:.88rem;color:#94a3b8;margin-top:.6rem">Les deux lignes colorées montrent les chemins logiques de données et de voix, pas des paquets capturés en temps réel.</figcaption>
</figure>

### 6.2. Exemple de configuration

```cisco
configure terminal
vlan 10
 name DATA
vlan 110
 name VOICE
!
interface gigabitEthernet0/10
 description TELEPHONE_IP_ET_PC
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 110
 spanning-tree portfast
end
```

Cette syntaxe est courante sur les commutateurs Cisco compatibles. Les exigences de QoS, les mécanismes de découverte du téléphone (CDP/LLDP), les versions et les modèles doivent être vérifiés dans la documentation de l'équipement. `spanning-tree portfast` est destiné aux ports d'extrémité ; ne l'applique pas sans analyse à une liaison entre commutateurs.

### 6.3. Vérifier

```cisco
show vlan brief
show interfaces gigabitEthernet0/10 switchport
show running-config interface gigabitEthernet0/10
```

Vérifie le VLAN de données, le VLAN voix, le mode access et les fonctions de découverte/QoS attendues. Une commande acceptée ne prouve pas que le téléphone applique le VLAN voix : contrôle aussi son état et sa configuration.


## 7. VLAN de gestion et SVI : séparer gestion et trafic utilisateur

### 7.1. Principe

Un VLAN de gestion dédié permet d'isoler le trafic d'administration des commutateurs du trafic des terminaux. Sur un commutateur de couche 2, une interface VLAN logique (SVI, *Switched Virtual Interface*) peut fournir l'adresse IPv4 de gestion. Cette adresse rend le commutateur joignable depuis le réseau autorisé ; elle n'active pas automatiquement le routage entre les VLAN utilisateur.

Exemple pour un switch administré dans VLAN 99 :

```cisco
configure terminal
vlan 99
 name MANAGEMENT
!
interface vlan 99
 ip address 192.168.99.2 255.255.255.0
 no shutdown
!
ip default-gateway 192.168.99.1
end
```

La commande `ip default-gateway` correspond typiquement à un commutateur qui ne route pas lui-même. Sur un commutateur configuré en mode routé, les paramètres et la méthode de routage peuvent être différents. L'SVI peut rester down si le VLAN n'est pas actif localement ou si aucune interface de couche 2 appropriée n'est active dans ce VLAN, selon la plateforme.

> **Sécurité :** l'adresse IP de gestion n'est pas une protection suffisante. Restreins les sources autorisées à administrer les équipements, privilégie SSH à Telnet, applique une politique d'identifiants adaptée et limite le VLAN de gestion aux liens nécessaires.

### 7.2. Contrôles

```cisco
show ip interface brief
show vlan brief
show interfaces trunk
show running-config | include default-gateway
```

Depuis un poste d'administration autorisé, teste la connectivité à l'adresse de gestion. Si l'SVI est down, vérifie l'existence du VLAN, les ports membres actifs, la continuité du trunk et l'adressage avant de modifier la configuration.


## 8. VLAN et EtherChannel : cohérence du port-channel

### 8.1. Principe

Un EtherChannel agrège plusieurs liens physiques pour former une liaison logique. Quand l'agrégat transporte plusieurs VLAN, les paramètres de trunk et les listes autorisées doivent être cohérents sur les interfaces membres et sur l'interface logique selon les règles de la plateforme. Une incohérence entre membres peut empêcher l'agrégat de se former correctement, suspendre un membre ou entraîner un état inattendu.

```text
              SW1                              SW2
       +----------------+                +----------------+
       |                |================|                |
       |                |================|                |
       |      Po1       |================|      Po1       |
       +----------------+                +----------------+
          Lien logique EtherChannel configuré comme trunk
          VLAN autorisés : 10, 20, 99 (exemple)
```

### 8.2. Vérifier avant de toucher

```cisco
show etherchannel summary
show interfaces trunk
show running-config interface port-channel 1
show running-config interface gigabitEthernet0/1
show running-config interface gigabitEthernet0/2
```

Les noms `Port-channel1` et les interfaces membres sont des exemples. Vérifie le protocole d'agrégation (LACP/PAgP ou autre prise en charge), le rôle du lien et la configuration des deux commutateurs. Les commandes de configuration exactes varient ; dans un réseau actif, évite de changer les membres un par un sans comprendre l'état de l'agrégat et le plan de retour arrière.

### 8.3. Erreurs typiques

- Les membres n'ont pas la même vitesse, le même duplex ou des paramètres compatibles.
- Le mode trunk, le VLAN natif ou la liste autorisée diffèrent entre membres.
- L'un des liens est raccordé à un équipement ou à un port inattendu.
- L'administrateur corrige la liste VLAN sur un seul maillon et oublie le port-channel ou l'autre côté.

Pour diagnostiquer, commence par l'état global de l'EtherChannel, puis examine les interfaces, le trunk opérationnel et les VLAN attendus. Teste ensuite la connectivité de bout en bout.


## 9. Méthode de dépannage intermédiaire

### 9.1. La méthode en six contrôles

```text
DÉPART : un service VLAN ne fonctionne pas
                    |
                    v
          1. Le lien physique est-il up ?
                    |
                    v
          2. Le port a-t-il le bon rôle ?
             access / trunk / Po ?
                    |
                    v
          3. Le VLAN existe-t-il localement ?
                    |
                    v
          4. Le VLAN est-il autorisé sur chaque trunk ?
                    |
                    v
          5. Le native VLAN et l'EtherChannel sont-ils cohérents ?
                    |
                    v
          6. La MAC et la connectivité confirment-elles le chemin ?
```

Cette séquence n'est pas une obligation stricte : si un symptôme indique clairement une cause, adapte l'ordre. Elle évite surtout de commencer par des changements de configuration sans avoir identifié le maillon défaillant.

### 9.2. Boîte à outils

| Commande | Question principale |
|---|---|
| `show vlan brief` | Le VLAN existe-t-il localement et quels ports access y sont associés ? |
| `show interfaces status` | Le port est-il connecté et quel VLAN/mode apparaît dans le résumé ? |
| `show interfaces trunk` | Quels trunks sont opérationnels et quels VLAN sont autorisés/actifs ? |
| `show interfaces <interface> switchport` | Quels sont le mode administratif et le mode opérationnel ? |
| `show mac address-table dynamic vlan 20` | Des adresses MAC sont-elles apprises dans le VLAN observé ? |
| `show spanning-tree vlan 20` | Quel est l'état STP pour ce VLAN ? |
| `show etherchannel summary` | L'agrégat et ses membres sont-ils opérationnels ? |
| `show logging` | Des événements signalent-ils un mismatch, une interface instable ou une erreur ? |

Remplace l'ID VLAN et le nom d'interface par les valeurs réelles. La syntaxe des filtres et des commandes peut changer selon les modèles IOS/IOS XE.

### 9.3. Cas pratique : un seul VLAN échoue

**Situation :** VLAN 10 fonctionne entre SW1 et SW2 ; VLAN 20 échoue. Les deux VLAN apparaissent dans `show vlan brief` sur les deux commutateurs, et le trunk est up.

Démarche recommandée :

1. Comparer `show interfaces trunk` sur SW1 et SW2, en particulier la liste autorisée et la liste des VLAN actifs.
2. Vérifier que VLAN 20 est autorisé sur tous les trunks du chemin, pas uniquement sur un port.
3. Vérifier la configuration native si le problème concerne le trafic non marqué ou des avertissements de mismatch ; ne pas attribuer automatiquement un échec d'un VLAN marqué au native VLAN.
4. Vérifier les ports access, l'apprentissage MAC et STP pour VLAN 20.
5. Confirmer l'adressage IP si les appareils doivent communiquer en couche 3.
6. Effectuer une seule correction à la fois puis refaire les mêmes tests.

Le but est de distinguer l'état de la base locale, le contrôle de la liaison trunk et l'acheminement réel.


## 10. Bonnes pratiques de changement

Avant un changement de VLAN ou de trunk :

- relever la configuration et l'état opérationnel ;
- identifier les équipements et services dépendants du VLAN ;
- confirmer la liste autorisée prévue sur chaque liaison ;
- préciser les tests de validation et la méthode de retour arrière ;
- effectuer le changement dans un laboratoire quand c'est possible.

Après le changement :

- comparer la configuration avant/après ;
- contrôler les VLAN locaux, le trunk, le VLAN natif et STP ;
- tester la connectivité des terminaux concernés ;
- surveiller les journaux et la stabilité des interfaces ;
- documenter les résultats.

> **Piège d'exploitation :** une commande qui remplace la liste autorisée peut être syntaxiquement valide et néanmoins interrompre plusieurs services. Le succès de la saisie en CLI n'est pas la preuve que le changement est correct.


## 11. Laboratoires pratiques

### Lab 1 — Construire un trunk avec une liste minimale

**Objectif :** transporter les VLAN 10 et 20 entre deux commutateurs, sans autoriser inutilement les autres VLAN.

**Topologie :** SW1 Gi0/1 relié à SW2 Gi0/1. PC-A est raccordé à SW1 Fa0/1 dans VLAN 10 ; PC-B est raccordé à SW2 Fa0/1 dans VLAN 10. Un deuxième test utilise VLAN 20.

**Sur les deux commutateurs**, crée les VLAN nécessaires localement si VTP n'est pas utilisé dans le lab :

```cisco
configure terminal
vlan 10
 name ADMIN
vlan 20
 name COMPTA
end
```

Configure le trunk des deux côtés, en adaptant le nom d'interface :

```cisco
configure terminal
interface gigabitEthernet0/1
 description TRUNK_LAB
 switchport mode trunk
 switchport trunk allowed vlan 10,20
end
```

Configure les ports terminaux :

```cisco
configure terminal
interface fastEthernet0/1
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
end
```

**Validation :** vérifie `show vlan brief`, `show interfaces trunk` et l'apprentissage MAC ; attribue aux PC des adresses du même sous-réseau de laboratoire et teste leur ping. Ensuite, utilise VLAN 20 pour le second test et note chaque changement nécessaire.

**Question :** le VLAN 20 existe sur SW1 et SW2, mais n'est pas dans la liste du trunk. Peut-il traverser cette liaison ? Explique pourquoi.

### Lab 2 — Identifier un native VLAN mismatch

**Objectif :** comprendre un désaccord de configuration entre les deux extrémités.

1. Dans un environnement de test, configure VLAN 99 comme natif sur SW1.
2. Laisse temporairement une valeur différente sur SW2 si la plateforme du labo accepte cette situation.
3. Observe les sorties de `show interfaces trunk` et les journaux.
4. Aligne le VLAN natif conformément au plan sur les deux côtés.
5. Recontrôle le trunk et vérifie la connectivité.

Ne réalise pas ce test sur un réseau de production. Les avertissements et le comportement exact dépendent des versions et des mécanismes de détection disponibles.

### Lab 3 — Téléphone IP et PC derrière le téléphone

**Objectif :** séparer le VLAN de données du VLAN voix sur un port compatible.

1. Crée VLAN 10 (`DATA`) et VLAN 110 (`VOICE`).
2. Configure un port d'accès avec `switchport access vlan 10` et `switchport voice vlan 110`.
3. Relie le téléphone compatible au port et le PC au port du téléphone.
4. Vérifie la configuration avec `show interfaces <interface> switchport`.
5. Si le simulateur ne prend pas en charge la téléphonie IP, documente la configuration attendue et explique la séparation logique.

### Lab 4 — Incident sur un EtherChannel

**Objectif :** diagnostiquer une incohérence VLAN sur un agrégat.

1. Observe l'état initial avec `show etherchannel summary` et `show interfaces trunk`.
2. Repère l'interface logique et les interfaces membres.
3. Compare leur configuration et la liste de VLAN autorisés sur les deux commutateurs.
4. Corrige uniquement l'incohérence identifiée dans le laboratoire.
5. Confirme que l'agrégat reste opérationnel et que la connectivité est restaurée.

Ne copie pas une configuration EtherChannel trouvée ailleurs sans vérifier la compatibilité des interfaces et du protocole d'agrégation.


## 12. Exercices d'évaluation

### Exercice 1 — Continuité VLAN

VLAN 30 existe sur SW1, SW2 et SW3. Le PC sur SW1 atteint un autre PC sur SW2, mais pas celui sur SW3. Quelles vérifications effectues-tu en priorité ?

### Exercice 2 — Liste autorisée

Le trunk transporte VLAN 10, 20 et 30. Un administrateur saisit :

```cisco
switchport trunk allowed vlan 10,20
```

Quel effet potentiel cette commande a-t-elle sur VLAN 30 ? Quelle précaution prendre ?

### Exercice 3 — DTP

Deux interfaces Cisco compatibles sont toutes deux en `dynamic auto`. Aucun trunk ne se forme. Est-ce nécessairement une panne matérielle ? Justifie la réponse et propose une configuration explicite.

### Exercice 4 — VLAN natif

SW1 indique native VLAN 99 et SW2 native VLAN 1. Explique le problème de classement des trames non marquées et propose une correction méthodique.

### Exercice 5 — Voice VLAN

Un téléphone IP fonctionne mais le PC connecté derrière ne reçoit pas la connectivité attendue. Cite au moins quatre contrôles pertinents.

### Exercice 6 — SVI de gestion

L'interface `Vlan99` possède une adresse IP mais reste down. Donne plusieurs conditions locales ou de couche 2 à vérifier avant de modifier les adresses IP.

### Exercice 7 — EtherChannel

Un trunk logique transporte VLAN 10 mais pas VLAN 20. Quels éléments inspectes-tu pour séparer un problème de liste autorisée d'une incohérence d'agrégat ?

### Exercice 8 — Choix de diagnostic

Quel est l'intérêt d'utiliser simultanément `show vlan brief`, `show interfaces trunk` et `show mac address-table dynamic vlan 20` au lieu de ne consulter qu'une seule sortie ?


## 13. Corrigés

### Correction 1

Contrôle les VLAN locaux sur chaque commutateur, les trunks qui relient SW2 à SW3, les listes autorisées sur chaque maillon, l'état STP pour VLAN 30, l'affectation des ports d'accès et l'apprentissage MAC. Ne suppose pas que le VLAN traverse le réseau simplement parce qu'il existe sur SW1.

### Correction 2

Sur les plateformes où cette commande remplace la liste, VLAN 30 est retiré de la liste autorisée. Il faut relever la liste initiale et connaître les VLAN nécessaires avant l'opération. Après modification, contrôler `show interfaces trunk` et tester les services touchés.

### Correction 3

Pas nécessairement : `dynamic auto` attend généralement une négociation initiée par l'autre extrémité. Deux ports en auto ne forment habituellement pas un trunk ensemble. Sur des commutateurs compatibles et si la conception l'autorise, configure les deux interfaces explicitement en trunk, vérifie les VLAN requis et envisage `switchport nonegotiate` lorsque DTP doit être désactivé sur ce lien.

### Correction 4

Un flux envoyé sans tag via SW1 peut être attribué au VLAN natif 99 ; SW2, configuré avec VLAN natif 1, le traite selon son propre paramétrage. Vérifie les trunks et les deux configurations, puis aligne le VLAN natif planifié sur chaque extrémité. Confirme que le VLAN choisi existe et est cohérent avec la politique locale.

### Correction 5

Vérifie notamment : le port et son VLAN de données ; le VLAN voix configuré ; la présence de ces VLAN dans la base locale ; l'état du trunk en amont ; l'adressage IP et le DHCP du PC ; l'état du téléphone ; les mécanismes CDP/LLDP et la configuration QoS pris en charge. Teste chaque élément séparément.

### Correction 6

Vérifie que VLAN 99 existe et est actif localement, qu'au moins un port de couche 2 approprié est actif dans ce VLAN selon les règles de la plateforme, que le VLAN est transporté sur les trunks nécessaires, que le VLAN de gestion n'est pas bloqué par STP et que l'interface n'est pas administrativement arrêtée. `show ip interface brief`, `show vlan brief` et `show interfaces trunk` sont de bons points de départ.

### Correction 7

Examine `show etherchannel summary`, la configuration du port-channel et celle des membres, puis la liste VLAN autorisée et active du trunk. Compare les deux extrémités. Le problème peut venir de la liste VLAN, de l'agrégat, d'un membre suspendu ou d'un état STP. Ne modifie pas au hasard les interfaces membres.

### Correction 8

`show vlan brief` indique la présence locale du VLAN, `show interfaces trunk` présente l'état des trunks et leur liste de VLAN autorisés/actifs, tandis que la table MAC montre les adresses apprises dans le VLAN observé. Ensemble, ces sorties aident à distinguer une base VLAN correcte d'un problème de transport ou d'un manque de trafic appris.


## 14. Résumé opérationnel

- Vérifie la continuité du VLAN sur chaque commutateur et chaque trunk nécessaire.
- Le tag 802.1Q identifie le VLAN transporté sur un trunk ; le VLAN natif est une exception de traitement à configurer de manière cohérente.
- Une liste autorisée de trunk est locale à l'interface et peut être remplacée par une commande mal choisie.
- Le mode DTP doit être compris et contrôlé ; préfère les modes explicites lorsque l'architecture le demande.
- Un téléphone IP et le PC qui lui est raccordé peuvent utiliser un VLAN voix et un VLAN données distincts sur un port compatible.
- Une SVI de gestion ne transforme pas un commutateur de couche 2 en routeur inter-VLAN.
- Les paramètres VLAN d'un EtherChannel doivent être cohérents sur l'agrégat et les membres conformément à la plateforme.
- Le diagnostic doit combiner les sorties de VLAN, de trunk, de STP, d'EtherChannel, la table MAC et des tests de connectivité.

## Références techniques

- Cisco, *VLAN Configuration Guide — Configure VLAN* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vlan.html
- Cisco, *VLAN Configuration Guide — Configure VLAN Trunking* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vlan-trunks.html
- Cisco, *VLAN Configuration Guide — Configure Voice VLAN* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-voice-vlan.html
- IEEE, *IEEE 802.1Q — Bridges and Bridged Networks* : https://standards.ieee.org/standard/802_1Q-2022.html

La documentation de la version logicielle et du modèle réellement utilisés prime sur les exemples génériques de ce cours.
