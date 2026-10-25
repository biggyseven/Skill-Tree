# VLAN et segmentation des réseaux — Niveau Débutant

**Niveau :** Débutant  
**Durée indicative :** 45 à 60 minutes  
**Prérequis :** connaître le rôle d'un commutateur Ethernet, d'une adresse MAC et les bases de l'adressage IPv4.  
**Environnement conseillé :** Cisco Packet Tracer ou commutateurs Cisco compatibles avec les commandes présentées.

## Objectifs pédagogiques

À la fin de ce cours, tu dois pouvoir :

- expliquer à quoi sert un VLAN et ce qu'il sépare exactement ;
- distinguer un VLAN, un sous-réseau IP, un port d'accès et un trunk ;
- créer, nommer et vérifier des VLAN sur un commutateur ;
- affecter un port utilisateur au bon VLAN ;
- comprendre le rôle du marquage IEEE 802.1Q sur un trunk ;
- diagnostiquer les erreurs courantes de VLAN à l'aide de commandes `show`.

> **Périmètre du cours :** on apprend ici les VLAN de couche 2 et leur configuration de base. Le routage entre VLAN, les VLAN privés, les VLAN voix avancés, VTP et les attaques de VLAN seront approfondis dans des cours ultérieurs.


## 1. Comprendre les VLAN

### 1.1. Pourquoi segmenter un réseau ?

Imagine une petite entreprise qui utilise le même commutateur pour la comptabilité, le support informatique, l'administration et les visiteurs. Sans segmentation logique, les appareils raccordés au même réseau local de couche 2 peuvent partager le même domaine de diffusion.

Un **VLAN** (*Virtual Local Area Network*) permet de séparer logiquement les ports d'un commutateur en plusieurs réseaux Ethernet indépendants. Deux appareils peuvent être branchés au même équipement physique tout en appartenant à des VLAN différents.

Les VLAN sont notamment utiles pour :

- limiter la portée des diffusions Ethernet ;
- séparer les services et les types d'équipements ;
- organiser un réseau sans installer un commutateur physique par service ;
- appliquer plus clairement les politiques d'accès quand le routage et les contrôles de sécurité sont configurés.

Un VLAN **ne chiffre pas** le trafic et ne constitue pas à lui seul une politique de sécurité complète. Il faut aussi sécuriser les ports, les équipements d'administration, les trunks et le routage de couche 3.

### 1.2. Une analogie simple

Considère un commutateur comme un immeuble avec plusieurs équipes. Les ports sont les prises de l'immeuble. Les VLAN sont des groupes distincts : les postes de la comptabilité appartiennent au groupe 20, ceux du support au groupe 30. Ils partagent le même équipement physique, mais les diffusions de couche 2 restent séparées entre les groupes.

<figure style="margin:1.5rem 0;padding:1rem;border:1px solid #334155;border-radius:16px;background:#0f172a;color:#e2e8f0">
<svg viewBox="0 0 780 330" role="img" aria-label="Un commutateur partagé répartit les postes entre deux VLAN isolés" style="display:block;width:100%;height:auto;max-height:360px" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes vlanFlowA { to { stroke-dashoffset: -24; } } .vlan-flow-a { stroke-dasharray: 6 6; animation: vlanFlowA 1.8s linear infinite; }</style>

  <defs>
    <linearGradient id="vlanBgA" x1="0" x2="1"><stop offset="0" stop-color="#123b35"/><stop offset="1" stop-color="#164e63"/></linearGradient>
    <linearGradient id="vlanBgB" x1="0" x2="1"><stop offset="0" stop-color="#30204c"/><stop offset="1" stop-color="#4a2346"/></linearGradient>
  </defs>
  <rect x="12" y="12" width="756" height="306" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="390" y="38" text-anchor="middle" fill="#f8fafc" font-size="18" font-weight="700">Un switch physique, deux domaines de couche 2</text>
  <rect x="34" y="62" width="310" height="226" rx="12" fill="url(#vlanBgA)" stroke="#2dd4bf" stroke-width="1.5"/>
  <rect x="436" y="62" width="310" height="226" rx="12" fill="url(#vlanBgB)" stroke="#c084fc" stroke-width="1.5"/>
  <text x="189" y="86" text-anchor="middle" fill="#99f6e4" font-size="15" font-weight="700">VLAN 10 — ADMIN</text>
  <text x="591" y="86" text-anchor="middle" fill="#f5d0fe" font-size="15" font-weight="700">VLAN 20 — COMPTA</text>
  <g class="vlan-flow-a" stroke="#5eead4" stroke-width="2.5" fill="none"><path d="M119 143 L119 177"/><path d="M259 143 L259 177"/></g>
  <g fill="#0f172a" stroke="#5eead4" stroke-width="2"><rect x="72" y="103" width="94" height="40" rx="7"/><rect x="212" y="103" width="94" height="40" rx="7"/><rect x="72" y="177" width="94" height="40" rx="7"/><rect x="212" y="177" width="94" height="40" rx="7"/></g>
  <g fill="#e2e8f0" font-size="12" text-anchor="middle"><text x="119" y="128">PC Admin 1</text><text x="259" y="128">PC Admin 2</text><text x="119" y="201">Port Fa0/1</text><text x="259" y="201">Port Fa0/2</text></g>
  <g class="vlan-flow-a" stroke="#d8b4fe" stroke-width="2.5" fill="none"><path d="M521 143 L521 177"/><path d="M661 143 L661 177"/></g>
  <g fill="#0f172a" stroke="#c084fc" stroke-width="2"><rect x="474" y="103" width="94" height="40" rx="7"/><rect x="614" y="103" width="94" height="40" rx="7"/><rect x="474" y="177" width="94" height="40" rx="7"/><rect x="614" y="177" width="94" height="40" rx="7"/></g>
  <g fill="#f3e8ff" font-size="12" text-anchor="middle"><text x="521" y="128">PC Compta 1</text><text x="661" y="128">PC Compta 2</text><text x="521" y="201">Port Fa0/3</text><text x="661" y="201">Port Fa0/4</text></g>
  <path d="M344 246 L436 246" stroke="#64748b" stroke-width="2" stroke-dasharray="5 5"/>
  <path d="M382 239 L390 246 L382 253 M398 239 L390 246 L398 253" stroke="#94a3b8" stroke-width="2" fill="none"/>
  <text x="390" y="274" text-anchor="middle" fill="#94a3b8" font-size="10">Pas de communication L2 directe entre VLAN</text>
</svg>
<figcaption style="font-size:.88rem;color:#94a3b8;margin-top:.6rem">Les VLAN restent séparés même si leurs ports sont sur le même commutateur. Pour communiquer entre VLAN, il faut un équipement de couche 3 et une configuration adaptée.</figcaption>
</figure>

### 1.3. VLAN et sous-réseau IP : deux notions différentes

Un VLAN sépare les trames Ethernet à la **couche 2**. Un sous-réseau IP organise les adresses IP à la **couche 3**. Dans une architecture classique, on associe généralement un sous-réseau IP à chaque VLAN, mais le VLAN et le sous-réseau ne sont pas le même objet.

| Service | ID VLAN (exemple) | Sous-réseau IPv4 (exemple) | Passerelle (exemple) |
|---|---:|---|---|
| Administration | 10 | `192.168.10.0/24` | `192.168.10.1` |
| Comptabilité | 20 | `192.168.20.0/24` | `192.168.20.1` |
| Support | 30 | `192.168.30.0/24` | `192.168.30.1` |
| Invités | 40 | `192.168.40.0/24` | `192.168.40.1` |

Ces adresses sont illustratives. Il faut utiliser un plan d'adressage cohérent avec le réseau réel. La passerelle ne sera joignable que si une interface de couche 3 est configurée pour le VLAN et que l'adressage du poste est correct.

### 1.4. Que se passe-t-il quand deux appareils sont dans des VLAN différents ?

Un commutateur de couche 2 ne transmet pas directement les trames d'un VLAN vers un autre VLAN. Pour qu'un PC du VLAN 10 communique avec un serveur du VLAN 20, il faut un routeur ou un commutateur multicouche assurant le **routage inter-VLAN**. Cette fonction sera étudiée séparément.

<figure style="margin:1.5rem 0;padding:1rem;border:1px solid #334155;border-radius:16px;background:#0f172a;color:#e2e8f0">
<svg viewBox="0 0 760 255" role="img" aria-label="Le routage inter-VLAN passe par un équipement de couche 3" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes vlanFlowB { to { stroke-dashoffset: -24; } } .vlan-flow-b { stroke-dasharray: 6 6; animation: vlanFlowB 1.8s linear infinite; }</style>

  <rect x="8" y="8" width="744" height="239" rx="14" fill="#0b1220" stroke="#334155"/>
  <rect x="28" y="70" width="150" height="100" rx="12" fill="#123b35" stroke="#2dd4bf" stroke-width="1.5"/>
  <text x="103" y="96" text-anchor="middle" fill="#99f6e4" font-size="14" font-weight="700">VLAN 10</text>
  <rect x="56" y="111" width="94" height="36" rx="6" fill="#0f172a" stroke="#5eead4"/><text x="103" y="134" text-anchor="middle" fill="#e2e8f0" font-size="12">PC-A</text>
  <rect x="580" y="70" width="150" height="100" rx="12" fill="#30204c" stroke="#c084fc" stroke-width="1.5"/>
  <text x="655" y="96" text-anchor="middle" fill="#f5d0fe" font-size="14" font-weight="700">VLAN 20</text>
  <rect x="608" y="111" width="94" height="36" rx="6" fill="#0f172a" stroke="#c084fc"/><text x="655" y="134" text-anchor="middle" fill="#f3e8ff" font-size="12">PC-B</text>
  <rect x="287" y="55" width="186" height="130" rx="14" fill="#18263b" stroke="#60a5fa" stroke-width="2"/>
  <text x="380" y="83" text-anchor="middle" fill="#bfdbfe" font-size="15" font-weight="700">Routeur / switch L3</text>
  <rect x="310" y="99" width="140" height="28" rx="6" fill="#0b1220" stroke="#60a5fa"/><text x="380" y="117" text-anchor="middle" fill="#dbeafe" font-size="11">Passerelle VLAN 10</text>
  <rect x="310" y="138" width="140" height="28" rx="6" fill="#0b1220" stroke="#c084fc"/><text x="380" y="156" text-anchor="middle" fill="#f3e8ff" font-size="11">Passerelle VLAN 20</text>
  <path class="vlan-flow-b" d="M178 120 H287 M473 120 H580" stroke="#94a3b8" stroke-width="3" fill="none"/>
  <path d="M276 113 L287 120 L276 127 M569 113 L580 120 L569 127" stroke="#94a3b8" stroke-width="3" fill="none"/>
  <text x="380" y="215" text-anchor="middle" fill="#cbd5e1" font-size="13">La communication entre sous-réseaux passe par la couche 3</text>
</svg>
<figcaption style="font-size:.88rem;color:#94a3b8;margin-top:.6rem">Le routeur ou le commutateur multicouche utilise une passerelle pour chaque sous-réseau et applique les règles de routage et de sécurité configurées.</figcaption>
</figure>


## 2. Identifiants VLAN et bonnes pratiques de conception

### 2.1. Identifiant et nom

Un VLAN est identifié par un numéro (VLAN ID). On utilise souvent un nom qui décrit son usage : `ADMIN`, `COMPTA`, `SUPPORT` ou `INVITES`.

Les identifiants Ethernet VLAN usuels vont de 1 à 4094, mais certaines plateformes réservent des valeurs ou appliquent des limites particulières. Le VLAN 1 est présent par défaut sur de nombreux commutateurs Cisco. Il est généralement préférable de ne pas l'utiliser pour les données utilisateurs ou l'administration lorsque la conception permet de les séparer.

Exemple de convention de nommage :

| ID | Nom | Usage attendu |
|---:|---|---|
| 10 | `ADMIN` | Postes administratifs |
| 20 | `COMPTA` | Postes comptables |
| 30 | `SUPPORT` | Équipe informatique |
| 40 | `INVITES` | Accès visiteurs avec règles restrictives |
| 99 | `GESTION` | Gestion des commutateurs, si prévue dans le plan |
| 999 | `NATIVE_UNUSED` | Exemple de VLAN natif dédié non utilisé pour les terminaux, à adapter à la politique locale |

Le nom est une aide pour les humains ; le numéro est l'identifiant réellement utilisé dans la configuration Ethernet. Le même numéro ne garantit pas à lui seul que deux équipements appartiennent au même domaine de couche 2 : le VLAN doit être présent et transporté sur le chemin nécessaire.

### 2.2. VLAN de données, VLAN de gestion et VLAN natif

- **VLAN de données :** transporte le trafic d'un groupe d'utilisateurs ou d'équipements.
- **VLAN de gestion :** transporte les communications d'administration des équipements, selon la conception adoptée.
- **VLAN natif d'un trunk 802.1Q :** VLAN associé au trafic non marqué sur ce trunk. Sur les équipements Cisco, le VLAN natif est souvent VLAN 1 par défaut, mais il peut être changé.

Les extrémités d'un trunk doivent être configurées de façon cohérente, notamment pour le VLAN natif. Une différence entre les deux côtés peut provoquer des problèmes de connectivité ou de sécurité. Ne change pas le VLAN natif sans comprendre les équipements voisins et les protocoles de contrôle qui utilisent le trunk.

### 2.3. Modes de ports : access et trunk

Un port **access** appartient normalement à un VLAN de données unique. Il est couramment utilisé pour connecter un poste, une imprimante ou un terminal.

Un port **trunk** transporte plusieurs VLAN sur une liaison entre équipements réseau, par exemple entre deux commutateurs. Avec IEEE 802.1Q, les trames des VLAN transportés sont généralement marquées avec un identifiant VLAN ; le traitement du VLAN natif fait exception pour le trafic non marqué selon la configuration.

<figure style="margin:1.5rem 0;padding:1rem;border:1px solid #334155;border-radius:16px;background:#0f172a;color:#e2e8f0">
<svg viewBox="0 0 800 270" role="img" aria-label="Comparaison du port access qui transporte un seul VLAN et du trunk qui transporte plusieurs VLAN" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes vlanFlowC { to { stroke-dashoffset: -24; } } .vlan-flow-c { stroke-dasharray: 6 6; animation: vlanFlowC 1.8s linear infinite; }</style>

  <rect x="8" y="8" width="784" height="254" rx="14" fill="#0b1220" stroke="#334155"/>
  <text x="203" y="37" text-anchor="middle" fill="#99f6e4" font-size="16" font-weight="700">PORT ACCESS</text>
  <text x="597" y="37" text-anchor="middle" fill="#bfdbfe" font-size="16" font-weight="700">PORT TRUNK</text>
  <rect x="30" y="56" width="346" height="176" rx="12" fill="#102e2b" stroke="#2dd4bf"/>
  <rect x="424" y="56" width="346" height="176" rx="12" fill="#17243a" stroke="#60a5fa"/>
  <rect x="50" y="87" width="92" height="44" rx="7" fill="#0b1220" stroke="#2dd4bf"/><text x="96" y="114" text-anchor="middle" fill="#e2e8f0" font-size="12">PC</text>
  <path class="vlan-flow-c" d="M142 109 H196" stroke="#5eead4" stroke-width="4"/>
  <rect x="196" y="85" width="152" height="48" rx="8" fill="#0b1220" stroke="#2dd4bf"/><text x="272" y="104" text-anchor="middle" fill="#99f6e4" font-size="12" font-weight="700">SWITCH</text><text x="272" y="120" text-anchor="middle" fill="#cbd5e1" font-size="11">Port VLAN 10</text>
  <text x="203" y="166" text-anchor="middle" fill="#99f6e4" font-size="13">Un seul VLAN de données</text><text x="203" y="188" text-anchor="middle" fill="#94a3b8" font-size="11">Trame d'accès normalement non marquée</text>
  <rect x="444" y="86" width="92" height="48" rx="7" fill="#0b1220" stroke="#60a5fa"/><text x="490" y="106" text-anchor="middle" fill="#dbeafe" font-size="12">SW1</text><text x="490" y="121" text-anchor="middle" fill="#94a3b8" font-size="10">Trunk</text>
  <path class="vlan-flow-c" d="M536 110 H660" stroke="#60a5fa" stroke-width="4"/>
  <rect x="660" y="86" width="92" height="48" rx="7" fill="#0b1220" stroke="#60a5fa"/><text x="706" y="106" text-anchor="middle" fill="#dbeafe" font-size="12">SW2</text><text x="706" y="121" text-anchor="middle" fill="#94a3b8" font-size="10">Trunk</text>
  <rect x="549" y="79" width="22" height="11" rx="3" fill="#2dd4bf"/><rect x="577" y="79" width="22" height="11" rx="3" fill="#c084fc"/><rect x="605" y="79" width="22" height="11" rx="3" fill="#fbbf24"/>
  <text x="597" y="166" text-anchor="middle" fill="#dbeafe" font-size="13">Plusieurs VLAN possibles</text><text x="597" y="188" text-anchor="middle" fill="#94a3b8" font-size="11">Liste de VLAN autorisés à contrôler</text>
</svg>
<figcaption style="font-size:.88rem;color:#94a3b8;margin-top:.6rem">La configuration trunk ne remplace pas la création du VLAN et n'assure pas à elle seule que chaque VLAN attendu est autorisé sur le lien.</figcaption>
</figure>


## 3. Configuration VLAN de base sur Cisco IOS

Les exemples qui suivent utilisent une syntaxe courante Cisco IOS. Les modèles, versions logicielles et environnements simulés ne prennent pas tous en charge exactement les mêmes commandes. Adapte les interfaces à ton équipement ou à Packet Tracer.

### 3.1. Examiner l'état initial

Passe en mode privilégié, puis examine la configuration actuelle avant de la modifier :

```cisco
enable
show vlan brief
show interfaces status
show running-config
```

- `show vlan brief` présente la base VLAN locale et les ports d'accès affectés.
- `show interfaces status` donne un aperçu de l'état des interfaces et de leur VLAN.
- `show running-config` permet d'inspecter la configuration active.

N'écrase pas une configuration existante sans en comprendre le rôle. Dans un laboratoire neuf, relève tout de même l'état initial afin de pouvoir comparer le résultat.

### 3.2. Créer les VLAN

Exemple : créer les VLAN 10, 20 et 30.

```cisco
configure terminal
vlan 10
 name ADMIN
exit
vlan 20
 name COMPTA
exit
vlan 30
 name SUPPORT
exit
end
```

Vérifie :

```cisco
show vlan brief
```

Tu dois retrouver les trois ID et les noms prévus. À ce stade, la création des VLAN ne configure pas automatiquement tous les ports et ne donne pas d'adresse IP aux postes.

### 3.3. Affecter un port access

Pour affecter `FastEthernet0/1` au VLAN 10 :

```cisco
configure terminal
interface fastEthernet0/1
 description PC_ADMIN
 switchport mode access
 switchport access vlan 10
 no shutdown
end
```

Sur certaines plateformes, l'interface peut s'appeler `GigabitEthernet1/0/1` ou porter un autre nom. Utilise `show interfaces status` ou la documentation du matériel pour identifier le bon port.

Vérifie l'affectation :

```cisco
show vlan brief
show interfaces fastEthernet0/1 switchport
```

Un port access affecté au VLAN 10 ne permet pas, à lui seul, au poste d'atteindre d'autres sous-réseaux. L'adresse IP, le masque, la passerelle et les services réseau doivent aussi être corrects.

### 3.4. Affecter plusieurs ports au même VLAN

Lorsque plusieurs interfaces ont la même configuration, les plateformes Cisco IOS qui le supportent permettent d'utiliser `interface range` :

```cisco
configure terminal
interface range fastEthernet0/1 - 4
 switchport mode access
 switchport access vlan 10
 no shutdown
end
```

Cela affecte les interfaces Fa0/1 à Fa0/4 au VLAN 10. Vérifie les interfaces incluses avant d'appliquer une commande de plage : une erreur de sélection peut déplacer plusieurs postes vers le mauvais VLAN.

### 3.5. Configurer un trunk entre deux commutateurs

Supposons que SW1 et SW2 soient raccordés via `GigabitEthernet0/1` de chaque côté. La configuration doit être compatible sur les deux extrémités.

Sur SW1 :

```cisco
configure terminal
interface gigabitEthernet0/1
 description TRUNK_VERS_SW2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
end
```

Applique le réglage correspondant à l'extrémité distante de SW2 en adaptant l'interface. Cette commande configure une liste explicite qui n'autorise que les VLAN 10, 20 et 30 sur ce trunk. Ne copie pas cette liste sans vérifier si d'autres VLAN sont nécessaires dans ton réseau.

Vérifie le trunk :

```cisco
show interfaces trunk
show interfaces gigabitEthernet0/1 switchport
```

Certaines plateformes plus anciennes exigent ou proposent une commande d'encapsulation spécifique ; d'autres utilisent uniquement 802.1Q et n'acceptent pas cette commande. Ne force pas une syntaxe incompatible.

> **Attention :** la commande `switchport trunk allowed vlan 10,20,30` définit la liste des VLAN autorisés. Sur un port déjà configuré, elle peut remplacer la liste précédente. Pour ajouter des VLAN sans supprimer les entrées actuelles, certaines plateformes supportent `switchport trunk allowed vlan add 40`. Vérifie toujours la syntaxe et le résultat avec `show interfaces trunk`.

### 3.6. Comprendre le marquage 802.1Q

Sur un trunk, la balise IEEE 802.1Q identifie le VLAN auquel appartient la trame Ethernet. Cela permet de transporter plusieurs VLAN sur une seule liaison physique, tout en conservant leur séparation logique.

Le VLAN natif fait exception pour les trames non marquées sur les trunks configurés de cette manière. Sur Cisco, il est souvent égal à VLAN 1 par défaut, mais ce comportement peut être modifié. Les deux extrémités doivent utiliser un VLAN natif cohérent.

Pour ce cours, retiens surtout les règles suivantes :

1. Un port access transporte normalement le trafic d'un seul VLAN de données.
2. Un trunk transporte plusieurs VLAN lorsque ceux-ci sont présents et autorisés.
3. Un VLAN créé sur un switch n'est pas automatiquement autorisé partout.
4. Une mauvaise configuration du trunk peut bloquer le trafic même si le VLAN existe.


## 4. Laboratoire pratique : séparer deux services

### 4.1. Scénario

Tu dois configurer un petit réseau comportant un commutateur SW1 et quatre PC : deux pour l'administration et deux pour la comptabilité.

| Équipement | Port SW1 | VLAN | Adresse IPv4 d'exemple |
|---|---|---:|---|
| PC-ADMIN-1 | Fa0/1 | 10 | `192.168.10.11/24` |
| PC-ADMIN-2 | Fa0/2 | 10 | `192.168.10.12/24` |
| PC-COMPTA-1 | Fa0/3 | 20 | `192.168.20.11/24` |
| PC-COMPTA-2 | Fa0/4 | 20 | `192.168.20.12/24` |

Pour le premier exercice, utilise un seul commutateur. Aucune passerelle n'est requise pour tester la communication entre PC appartenant au même VLAN et placés dans le même sous-réseau. La communication entre VLAN différents ne fonctionnera pas sans routage inter-VLAN.

### 4.2. Topologie

```text
     PC-ADMIN-1             PC-ADMIN-2
    192.168.10.11           192.168.10.12
         |                       |
       Fa0/1                   Fa0/2
          \                     /
           +-------------------+
           |       SW1         |
           | VLAN 10 : ADMIN   |
           | VLAN 20 : COMPTA  |
           +-------------------+
           /                   \
       Fa0/3                   Fa0/4
         |                       |
   PC-COMPTA-1              PC-COMPTA-2
   192.168.20.11             192.168.20.12
```

### 4.3. Configuration complète de SW1

Dans ce laboratoire neuf, la configuration de SW1 peut être :

```cisco
enable
configure terminal
hostname SW1

vlan 10
 name ADMIN
vlan 20
 name COMPTA

interface range fastEthernet0/1 - 2
 description POSTES_ADMIN
 switchport mode access
 switchport access vlan 10
 no shutdown

interface range fastEthernet0/3 - 4
 description POSTES_COMPTA
 switchport mode access
 switchport access vlan 20
 no shutdown

end
copy running-config startup-config
```

Si ton commutateur ou ton simulateur n'accepte pas `interface range` dans cette syntaxe, configure chaque interface séparément.

### 4.4. Configuration IP des PC

Configure les adresses IP comme indiqué dans le tableau. Les deux PC d'administration doivent utiliser le masque `255.255.255.0`, tout comme les deux PC de comptabilité.

Résultats attendus :

- PC-ADMIN-1 peut communiquer avec PC-ADMIN-2, si les ports et adresses sont bien configurés.
- PC-COMPTA-1 peut communiquer avec PC-COMPTA-2 dans les mêmes conditions.
- Un PC d'administration ne communique pas directement avec un PC de comptabilité sans mécanisme de routage inter-VLAN.

### 4.5. Tests à effectuer

Sur SW1 :

```cisco
show vlan brief
show interfaces status
show mac address-table dynamic
```

Depuis les PC, teste ensuite les adresses des autres PC du même VLAN avec `ping`. Si l'environnement simule un filtrage ICMP ou si le pare-feu des PC bloque les requêtes, interprète le résultat avec prudence.

Pour chaque test, note : le poste source, le poste de destination, le résultat et ton explication. Ne te contente pas de déclarer que « le ping marche » : relie le résultat à l'ID VLAN, à l'adresse IP et au masque.


## 5. Laboratoire complémentaire : deux commutateurs et un trunk

Cette seconde partie ajoute un trunk entre SW1 et SW2. Elle permet de constater qu'un VLAN doit exister sur le chemin et être transporté par le trunk.

### 5.1. Topologie

```text
 PC-A (VLAN 10)                           PC-B (VLAN 10)
 192.168.10.11                             192.168.10.12
      | Fa0/1                                  | Fa0/1
   +--------+       Gi0/1       Gi0/1        +--------+
   |  SW1   |================================|  SW2   |
   | VLAN10 |        trunk 802.1Q            | VLAN10 |
   +--------+                                +--------+
```

### 5.2. Configurer les deux côtés du trunk

Sur SW1 :

```cisco
configure terminal
vlan 10
 name ADMIN
interface gigabitEthernet0/1
 description TRUNK_VERS_SW2
 switchport mode trunk
 switchport trunk allowed vlan 10
 no shutdown
end
```

Sur SW2 :

```cisco
configure terminal
vlan 10
 name ADMIN
interface gigabitEthernet0/1
 description TRUNK_VERS_SW1
 switchport mode trunk
 switchport trunk allowed vlan 10
 no shutdown
end
```

Dans ce laboratoire sans VTP, le VLAN est créé localement sur les deux commutateurs. L'étude de VTP est faite dans le cours consacré à ce protocole. Si la commande trunk ne fonctionne pas sur le simulateur, vérifie le modèle de switch et sa prise en charge des commandes.

Affecte les ports Fa0/1 de SW1 et SW2 au VLAN 10, puis configure les deux PC dans le même sous-réseau `192.168.10.0/24`.

### 5.3. Vérifier le chemin

Sur les deux commutateurs :

```cisco
show vlan brief
show interfaces trunk
show interfaces gigabitEthernet0/1 switchport
show mac address-table dynamic vlan 10
```

Lorsque les interfaces sont actives, le trunk est opérationnel et le VLAN 10 est présent et autorisé de bout en bout, le ping entre les PC devrait réussir dans un environnement de laboratoire correctement configuré.

### 5.4. Test d'incident volontaire

Dans un laboratoire seulement, retire le VLAN 10 de la liste autorisée du trunk sur un côté, ou autorise uniquement un autre VLAN. Refais le ping et observe la différence. Rétablis ensuite la configuration prévue.

L'objectif est de démontrer que **la présence d'un VLAN dans la base locale ne garantit pas qu'il traverse le trunk**.


## 6. Méthode de dépannage

Lorsqu'un appareil ne communique pas, avance par étapes au lieu de modifier plusieurs paramètres au hasard.

### Étape 1 — Vérifier le port et son VLAN

```cisco
show interfaces status
show vlan brief
show running-config interface fastEthernet0/1
```

Vérifie que l'interface est active et affectée au VLAN prévu. Une interface désactivée, un câble débranché ou une affectation VLAN incorrecte peut suffire à interrompre la connectivité.

### Étape 2 — Vérifier le trunk

```cisco
show interfaces trunk
show interfaces gigabitEthernet0/1 switchport
```

Vérifie l'état opérationnel du trunk, les VLAN autorisés et le VLAN natif. Répète les contrôles sur l'autre extrémité, ainsi que sur les commutateurs intermédiaires.

### Étape 3 — Vérifier l'adressage IP

Sur chaque PC, vérifie :

- l'adresse IPv4 ;
- le masque de sous-réseau ;
- la passerelle si une communication hors du sous-réseau est attendue.

Deux appareils peuvent être dans le même VLAN, mais avoir un adressage IP incorrect. Inversement, deux appareils appartenant à des VLAN différents ne deviennent pas directement joignables simplement parce que leurs adresses IP sont proches.

### Étape 4 — Examiner la table MAC

```cisco
show mac address-table dynamic
```

Si le switch apprend les adresses MAC des PC dans le VLAN et sur les ports attendus, cela apporte un indice que les trames atteignent l'équipement. L'absence d'une adresse n'indique pas à elle seule une panne définitive : aucun trafic récent, un port down ou une autre anomalie peuvent expliquer son absence.

### Étape 5 — Vérifier la couche 3 si nécessaire

Si la communication doit traverser des VLAN différents, vérifie la présence des passerelles, le routage inter-VLAN et les politiques de sécurité. Un switch de couche 2 ne réalise pas automatiquement le routage entre les sous-réseaux.

### Tableau des incidents courants

| Symptôme | Causes possibles | Vérifications prioritaires |
|---|---|---|
| Le PC ne communique avec aucun appareil | Câble, port down, mauvais VLAN, IP incorrecte | `show interfaces status`, `show vlan brief`, configuration IP |
| Deux PC du même VLAN ne se joignent pas | Mauvais masque, ports mal affectés, VLAN absent sur le chemin | `show vlan brief`, `show mac address-table`, ping |
| Deux PC sur des switches distincts ne se joignent pas | Trunk down, VLAN absent ou non autorisé | `show interfaces trunk`, `show vlan brief` sur chaque switch |
| Un seul VLAN échoue sur le trunk | VLAN omis de la liste autorisée ou absent localement | `show interfaces trunk`, `show vlan brief` |
| Deux VLAN ne communiquent pas | Routage inter-VLAN absent ou filtrage | Passerelles, interfaces/SVI de couche 3, routes et ACL |
| Le VLAN natif ne correspond pas | Configuration différente aux extrémités du trunk | `show interfaces trunk`, configuration des deux interfaces |


## 7. Sécurité et bonnes pratiques

1. **Documente les VLAN.** Maintiens une liste des ID, des noms, des usages et des sous-réseaux associés.
2. **Configure explicitement les ports.** Affecte les ports utilisateurs à un VLAN de données approprié et désactive les interfaces inutilisées selon la politique du site.
3. **Limite les VLAN autorisés sur les trunks.** N'autorise que les VLAN nécessaires au lien, après avoir vérifié les dépendances.
4. **Cohérence du VLAN natif.** Si un trunk utilise un VLAN natif spécifique, les deux côtés doivent être alignés.
5. **Ne confonds pas segmentation et sécurité complète.** Les VLAN séparent les domaines de couche 2 ; le routage doit être contrôlé et les services d'administration protégés.
6. **Sauvegarde et teste.** Avant une modification, relève la configuration. Après la modification, teste la connectivité des services concernés.

Le VLAN 1 est utilisé par défaut sur de nombreux équipements Cisco et transporte aussi certains trafics de contrôle selon la plateforme. Évite d'y laisser des données sensibles ou la gestion lorsque la conception prévoit des VLAN dédiés. Les mesures précises à appliquer dépendent de la gamme du commutateur et de la politique de sécurité du réseau.


## 8. Exercices de compréhension

### Exercice 1 — Comprendre l'isolation

PC-A est dans le VLAN 10 avec l'adresse `192.168.10.10/24`. PC-B est dans le VLAN 20 avec l'adresse `192.168.20.10/24`. Ils sont branchés au même commutateur de couche 2.

1. Peuvent-ils communiquer directement au niveau 2 ?
2. Quel mécanisme faut-il ajouter pour permettre la communication IP entre ces sous-réseaux ?
3. Est-ce que créer les deux VLAN attribue automatiquement des adresses IP aux PC ?

### Exercice 2 — Lire une configuration

```cisco
vlan 20
 name COMPTA
!
interface fastEthernet0/8
 switchport mode access
 switchport access vlan 20
```

Explique ce que représente VLAN 20 et quel appareil ou type de lien devrait normalement être raccordé à Fa0/8 dans cette configuration.

### Exercice 3 — Diagnostiquer un trunk

SW1 et SW2 possèdent le VLAN 30. Le trunk entre les deux switches est opérationnel, mais le VLAN 30 ne figure pas dans les VLAN autorisés. Les PC connectés derrière SW2 ne reçoivent pas le trafic attendu du VLAN 30.

Quelles commandes vérifies-tu et quelle propriété du trunk dois-tu corriger ?

### Exercice 4 — Repérer un piège

Un administrateur exécute :

```cisco
interface gigabitEthernet0/1
 switchport trunk allowed vlan 10,20
```

Le trunk transportait auparavant les VLAN 10, 20 et 30. Quel est l'effet possible de cette modification sur le VLAN 30 ? Quelle précaution doit être prise avant de l'exécuter ?


## 9. Corrigés

### Correction 1

1. Non, un commutateur de couche 2 ne transfère pas directement les trames entre VLAN distincts.
2. Il faut un routeur ou un commutateur multicouche avec le routage inter-VLAN configuré, ainsi que des passerelles et des règles adaptées.
3. Non. Les VLAN définissent une séparation logique ; les adresses IP doivent être configurées manuellement ou obtenues par un service comme DHCP.

### Correction 2

VLAN 20 est le VLAN de comptabilité dans cet exemple. Fa0/8 est un port access associé à ce VLAN et convient normalement à un terminal utilisateur de ce groupe. Le nom `COMPTA` est descriptif ; l'identifiant opérationnel est 20.

### Correction 3

Exécuter `show interfaces trunk` et `show vlan brief` sur les équipements du chemin, puis vérifier la configuration du port trunk aux deux extrémités. Le VLAN 30 doit exister localement sur les commutateurs requis et être présent dans la liste des VLAN autorisés sur les trunks nécessaires. Toute modification doit préserver les VLAN déjà requis par les services existants.

### Correction 4

La liste configurée n'inclut plus le VLAN 30 ; sur les plateformes prenant en charge cette syntaxe comme remplacement de liste, le trafic du VLAN 30 ne sera plus transporté par ce trunk. Avant l'opération, il faut vérifier quels VLAN sont nécessaires et envisager la forme `add` si l'objectif est seulement d'ajouter un VLAN, en contrôlant ensuite l'état effectif avec `show interfaces trunk`.


## 10. Résumé à retenir

- Un VLAN sépare logiquement le trafic Ethernet à la couche 2.
- Un port access transporte normalement un seul VLAN de données ; un trunk transporte plusieurs VLAN à l'aide de 802.1Q.
- Le VLAN doit exister sur les commutateurs du chemin et être autorisé sur les trunks concernés.
- Le routage inter-VLAN nécessite un équipement de couche 3 et une configuration appropriée.
- `show vlan brief`, `show interfaces status`, `show interfaces trunk` et `show mac address-table dynamic` sont des commandes de vérification de base.
- La segmentation doit être accompagnée de bonnes pratiques de sécurité, de documentation, de sauvegarde et de tests.

## Références techniques

- Cisco, *VLAN Configuration Guide — Configure VLAN* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vlan.html
- Cisco, *VLAN Configuration Guide — Configure VLAN Trunking* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vlan-trunks.html
- IEEE, *IEEE 802.1Q — Bridges and Bridged Networks* : https://standards.ieee.org/standard/802_1Q-2022.html

Les commandes et limites doivent être vérifiées dans la documentation du modèle et de la version logicielle utilisés. Les exemples sont destinés à l'apprentissage et à un laboratoire contrôlé.
