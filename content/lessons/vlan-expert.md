# VLAN et segmentation des réseaux — Niveau Expert

**Niveau :** Expert  
**Durée indicative :** 120 à 180 minutes, hors laboratoires  
**Prérequis :** maîtriser la création des VLAN, les ports access et trunk 802.1Q, les VLAN autorisés, le VLAN natif, DTP, les SVI, les EtherChannels et la méthode de dépannage multi-commutateurs présentés dans les niveaux Débutant et Intermédiaire.  
**Environnement conseillé :** laboratoire isolé avec Cisco Packet Tracer pour les notions disponibles, ou commutateurs Cisco IOS/IOS XE compatibles pour les fonctions avancées. Certaines fonctions — notamment PVLAN, VACL, options de sécurité et détails MST — ne sont pas prises en charge dans tous les simulateurs ou sur toutes les gammes.

> **Fil conducteur :** au niveau Débutant, tu as créé des VLAN et affecté les ports. Au niveau Intermédiaire, tu as assuré leur continuité à travers les trunks et diagnostiqué les problèmes de marquage. Au niveau Expert, l'objectif change : concevoir des frontières de sécurité, réduire l'impact d'une erreur de couche 2, vérifier les comportements réels du matériel et préparer des changements réversibles.

## Objectifs pédagogiques

À la fin de ce cours, tu dois pouvoir :

- choisir entre VLAN classiques, Private VLAN, ports protégés, ACL de couche 2/3 et segmentation par VRF selon le besoin ;
- concevoir une architecture VLAN qui limite les domaines de diffusion et les conséquences d'une panne ;
- réduire les risques de VLAN hopping par une configuration explicite des trunks et des ports d'accès ;
- appliquer avec prudence DHCP Snooping, Dynamic ARP Inspection (DAI) et IP Source Guard ;
- comprendre comment PVST+/Rapid-PVST+ et MST influencent la conception des VLAN ;
- construire un plan de migration, une matrice de tests et un retour arrière pour une modification sensible ;
- diagnostiquer un incident en reliant la configuration, les tables opérationnelles et les preuves observables.


## 1. Passer de la configuration VLAN à la conception de la segmentation

### 1.1. Le VLAN n'est pas, à lui seul, une frontière de sécurité complète

Un VLAN crée un domaine de diffusion de couche 2. Il ne garantit pas, à lui seul, qu'un utilisateur ne puisse accéder qu'aux services qui lui sont destinés. Si plusieurs VLAN sont routés par le même commutateur multicouche, les interfaces VLAN (SVI) et les politiques de couche 3 peuvent autoriser ou interdire leurs communications. Si des hôtes se trouvent dans le même VLAN, une ACL appliquée uniquement sur une SVI peut ne pas inspecter le trafic qui est commuté localement entre ces hôtes.

La conception doit donc distinguer plusieurs questions :

1. **Séparation L2 :** quels ports appartiennent au même domaine Ethernet ?
2. **Transport L2 :** quels trunks transportent quels VLAN ?
3. **Routage L3 :** où les VLAN peuvent-ils communiquer entre eux ?
4. **Contrôle d'accès :** quels flux sont autorisés, dans quel sens et vers quelles destinations ?
5. **Confinement :** quel est l'impact d'une erreur, d'un équipement compromis ou d'une boucle ?

### 1.2. Lire une architecture avec ses plans de contrôle et de données

<figure>
<svg viewBox="0 0 900 350" role="img" aria-label="Architecture de segmentation experte montrant les VLAN d'accès, les trunks, les passerelles SVI et les politiques de couche 3" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes expertFlowA { to { stroke-dashoffset: -24; } } .expert-link { stroke-dasharray: 7 6; animation: expertFlowA 2.2s linear infinite; }</style>
  <rect x="8" y="8" width="884" height="334" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="34" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">Séparer le domaine L2 du point de contrôle L3</text>
  <rect x="30" y="62" width="240" height="100" rx="12" fill="#102b35" stroke="#22d3ee" stroke-width="1.5"/>
  <text x="150" y="85" text-anchor="middle" fill="#a5f3fc" font-size="14" font-weight="700">ACCÈS — VLAN 110</text>
  <text x="150" y="108" text-anchor="middle" fill="#e2e8f0" font-size="12">Postes utilisateurs</text>
  <text x="150" y="128" text-anchor="middle" fill="#cbd5e1" font-size="11">Port access + sécurité de port</text>
  <text x="150" y="146" text-anchor="middle" fill="#cbd5e1" font-size="11">DHCP Snooping / DAI selon besoin</text>
  <rect x="30" y="194" width="240" height="100" rx="12" fill="#2b203a" stroke="#c084fc" stroke-width="1.5"/>
  <text x="150" y="218" text-anchor="middle" fill="#e9d5ff" font-size="14" font-weight="700">ACCÈS — VLAN 120</text>
  <text x="150" y="241" text-anchor="middle" fill="#e2e8f0" font-size="12">Serveurs / services</text>
  <text x="150" y="261" text-anchor="middle" fill="#cbd5e1" font-size="11">Ports dédiés ou segmentation dédiée</text>
  <text x="150" y="279" text-anchor="middle" fill="#cbd5e1" font-size="11">Politique de flux propre au rôle</text>
  <path d="M270 112 H338 V153 H378" fill="none" stroke="#22d3ee" stroke-width="3" class="expert-link"/>
  <path d="M270 244 H338 V198 H378" fill="none" stroke="#c084fc" stroke-width="3" class="expert-link"/>
  <rect x="378" y="102" width="196" height="146" rx="14" fill="#17243a" stroke="#60a5fa" stroke-width="1.5"/>
  <text x="476" y="128" text-anchor="middle" fill="#bfdbfe" font-size="15" font-weight="700">SW-DIST / L3</text>
  <text x="476" y="151" text-anchor="middle" fill="#e2e8f0" font-size="12">SVI VLAN 110</text>
  <text x="476" y="171" text-anchor="middle" fill="#e2e8f0" font-size="12">SVI VLAN 120</text>
  <line x1="402" y1="184" x2="550" y2="184" stroke="#475569"/>
  <text x="476" y="205" text-anchor="middle" fill="#a7f3d0" font-size="11">ACL / routage / journalisation</text>
  <text x="476" y="224" text-anchor="middle" fill="#cbd5e1" font-size="10">Applique les règles à l'endroit utile</text>
  <path d="M574 175 H640" fill="none" stroke="#34d399" stroke-width="3" class="expert-link"/>
  <polygon points="640,175 630,169 630,181" fill="#34d399"/>
  <rect x="640" y="111" width="224" height="128" rx="12" fill="#123127" stroke="#34d399" stroke-width="1.5"/>
  <text x="752" y="137" text-anchor="middle" fill="#a7f3d0" font-size="14" font-weight="700">SERVICES / PARE-FEU</text>
  <text x="752" y="161" text-anchor="middle" fill="#e2e8f0" font-size="12">Réseaux autorisés</text>
  <text x="752" y="182" text-anchor="middle" fill="#cbd5e1" font-size="11">Contrôle des flux</text>
  <text x="752" y="202" text-anchor="middle" fill="#cbd5e1" font-size="11">Journalisation / inspection</text>
  <rect x="378" y="272" width="486" height="42" rx="9" fill="#1e293b" stroke="#64748b"/>
  <text x="621" y="289" text-anchor="middle" fill="#e2e8f0" font-size="11" font-weight="700">À retenir</text>
  <text x="621" y="304" text-anchor="middle" fill="#cbd5e1" font-size="10">Un VLAN segmente L2 ; une politique L3/L4 définit les flux permis.</text>
</svg>
<figcaption>Les lignes animées représentent les liens physiques/logiques ; elles ne signifient pas que tous les flux sont autorisés. Les ACL et les passerelles déterminent le comportement réel.</figcaption>
</figure>

### 1.3. Choisir la taille et la portée d'un VLAN

Un VLAN ne doit pas être étendu à l'ensemble du campus par défaut. Une portée excessive augmente la taille du domaine de diffusion, les dépendances STP et la surface d'impact d'une erreur L2. À l'inverse, multiplier les VLAN sans plan cohérent complexifie le dépannage, les politiques de sécurité et l'exploitation.

Un plan de segmentation doit expliciter :

| Critère | Question de conception | Décision à documenter |
|---|---|---|
| Fonction | Quels équipements remplissent le même rôle ? | VLAN par service ou fonction |
| Confiance | Les équipements ont-ils les mêmes exigences de sécurité ? | Séparation des zones de confiance |
| Localisation | Le VLAN doit-il traverser plusieurs armoires ou sites ? | Portée L2 la plus courte compatible avec le besoin |
| Mobilité | Le poste se déplace-t-il entre plusieurs accès ? | Cohérence d'affectation, NAC/802.1X si disponible |
| Panne | Combien d'utilisateurs peuvent être touchés ? | Domaine L2 et plan de reprise limités |
| Exploitation | Qui peut modifier la configuration ? | Propriétaire, convention de nommage, procédure de changement |

### 1.4. Exemple de convention de nommage

Une convention stable est plus utile qu'un nom seulement descriptif. Exemple pédagogique :

```text
VLAN 110  USERS-DOUALA-ETAGE1
VLAN 120  SERVERS-APP
VLAN 130  VOICE-DOUALA
VLAN 140  PRINTERS
VLAN 150  IOT-CAMERAS
VLAN 190  NET-MGMT
VLAN 998  NATIVE-UNUSED
```

Cette liste n'est pas un plan universel. Les numéros et les plages réservées doivent provenir d'une politique IP/VLAN documentée. Le VLAN natif inutilisé doit être créé et transporté uniquement selon les capacités et les exigences de la plateforme ; le nommer « UNUSED » ne le rend pas inutilisable par magie. Si le VLAN natif est conservé sur un trunk, protège-le et vérifie sa cohérence des deux côtés.


## 2. Les Private VLAN (PVLAN) : isoler les hôtes à l'intérieur d'un sous-réseau

### 2.1. Le problème des VLAN classiques

Deux hôtes d'un VLAN classique appartiennent au même domaine L2. Une SVI avec une ACL filtre normalement le trafic routé entre VLAN, mais n'est pas une solution suffisante pour bloquer le trafic commuté directement entre deux hôtes du même VLAN.

Les **Private VLAN** permettent, sur les plateformes compatibles, de restreindre les communications L2 entre ports qui partagent l'architecture d'un même VLAN primaire. C'est utile, par exemple, pour héberger plusieurs serveurs ou clients dans un même sous-réseau sans les laisser communiquer directement entre eux.

### 2.2. Les trois rôles de ports PVLAN

<figure>
<svg viewBox="0 0 900 340" role="img" aria-label="Schéma de Private VLAN montrant deux hôtes isolés, une communauté de deux hôtes, et une passerelle sur port promiscuous" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes pvlanDash { to { stroke-dashoffset: -28; } } .pvlan-path { stroke-dasharray: 7 6; animation: pvlanDash 2.1s linear infinite; }</style>
  <rect x="8" y="8" width="884" height="324" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="34" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">PVLAN — le rôle du port détermine les communications L2</text>
  <rect x="34" y="58" width="832" height="52" rx="10" fill="#17243a" stroke="#60a5fa"/>
  <text x="450" y="80" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">VLAN primaire 100 — même sous-réseau IP logique</text>
  <text x="450" y="97" text-anchor="middle" fill="#cbd5e1" font-size="11">Les VLAN secondaires définissent les restrictions entre ports</text>
  <rect x="44" y="143" width="226" height="122" rx="12" fill="#2a1b20" stroke="#fb7185" stroke-width="1.5"/>
  <text x="157" y="165" text-anchor="middle" fill="#fda4af" font-size="13" font-weight="700">Isolated — VLAN 101</text>
  <rect x="65" y="179" width="78" height="51" rx="8" fill="#3b2028" stroke="#fb7185"/>
  <text x="104" y="199" text-anchor="middle" fill="#ffe4e6" font-size="11" font-weight="700">Hôte A</text><text x="104" y="215" text-anchor="middle" fill="#fecdd3" font-size="9">Isolé</text>
  <rect x="171" y="179" width="78" height="51" rx="8" fill="#3b2028" stroke="#fb7185"/>
  <text x="210" y="199" text-anchor="middle" fill="#ffe4e6" font-size="11" font-weight="700">Hôte B</text><text x="210" y="215" text-anchor="middle" fill="#fecdd3" font-size="9">Isolé</text>
  <line x1="143" y1="202" x2="171" y2="202" stroke="#fb7185" stroke-width="3" stroke-dasharray="3 4"/>
  <text x="157" y="248" text-anchor="middle" fill="#fecdd3" font-size="10">A ↔ B bloqué</text>
  <rect x="337" y="143" width="226" height="122" rx="12" fill="#1d2930" stroke="#22d3ee" stroke-width="1.5"/>
  <text x="450" y="165" text-anchor="middle" fill="#a5f3fc" font-size="13" font-weight="700">Community — VLAN 102</text>
  <rect x="358" y="179" width="78" height="51" rx="8" fill="#153640" stroke="#22d3ee"/>
  <text x="397" y="199" text-anchor="middle" fill="#cffafe" font-size="11" font-weight="700">Hôte C</text><text x="397" y="215" text-anchor="middle" fill="#a5f3fc" font-size="9">Groupe 1</text>
  <rect x="464" y="179" width="78" height="51" rx="8" fill="#153640" stroke="#22d3ee"/>
  <text x="503" y="199" text-anchor="middle" fill="#cffafe" font-size="11" font-weight="700">Hôte D</text><text x="503" y="215" text-anchor="middle" fill="#a5f3fc" font-size="9">Groupe 1</text>
  <line x1="436" y1="202" x2="464" y2="202" stroke="#22d3ee" stroke-width="3" class="pvlan-path"/>
  <text x="450" y="248" text-anchor="middle" fill="#a5f3fc" font-size="10">C ↔ D autorisé</text>
  <rect x="630" y="143" width="226" height="122" rx="12" fill="#123127" stroke="#34d399" stroke-width="1.5"/>
  <text x="743" y="165" text-anchor="middle" fill="#a7f3d0" font-size="13" font-weight="700">Promiscuous — passerelle</text>
  <rect x="670" y="180" width="146" height="48" rx="8" fill="#174737" stroke="#34d399"/>
  <text x="743" y="199" text-anchor="middle" fill="#d1fae5" font-size="11" font-weight="700">Routeur / pare-feu</text>
  <text x="743" y="215" text-anchor="middle" fill="#a7f3d0" font-size="9">Accessible aux hôtes associés</text>
  <text x="450" y="296" text-anchor="middle" fill="#cbd5e1" font-size="11">Les ports secondaires peuvent joindre le port promiscuous selon l'association ;</text>
  <text x="450" y="312" text-anchor="middle" fill="#cbd5e1" font-size="11">un port isolé ne rejoint ni les autres ports isolés ni les communautés.</text>
</svg>
<figcaption>Concept PVLAN : les restrictions sont assurées au niveau L2 par les rôles et associations configurés. Vérifie les capacités et les restrictions de la gamme avant de reprendre une configuration.</figcaption>
</figure>

| Type | Communication permise | Communication interdite / limite |
|---|---|---|
| Primary VLAN | Porte le contexte primaire de la PVLAN | Ne définit pas, seule, les règles entre hôtes secondaires |
| Isolated secondary | Vers les ports promiscuous associés | Vers les autres ports isolés et les communautés |
| Community secondary | Vers les ports de la même communauté et les ports promiscuous associés | Vers d'autres communautés et les ports isolés |
| Promiscuous | Peut communiquer avec les ports secondaires associés | L'association doit être configurée et vérifiée |

### 2.3. Configuration PVLAN sur une plateforme Cisco compatible

Exemple pédagogique inspiré de la syntaxe IOS XE sur une gamme Catalyst qui prend en charge les PVLAN. Les commandes peuvent différer selon le modèle, la version logicielle et les fonctionnalités activées. Vérifie la documentation du commutateur avant de réutiliser ces commandes.

Plan du lab :

- VLAN primaire : `100` ;
- VLAN isolé : `101` ;
- VLAN communauté : `102` ;
- `Gi1/0/10` et `Gi1/0/11` : hôtes isolés ;
- `Gi1/0/12` et `Gi1/0/13` : hôtes de la même communauté ;
- `Gi1/0/1` : passerelle sur un port promiscuous.

```cisco
configure terminal
!
! Dans ce lab, sélectionner un mode VTP compatible avec les PVLAN.
! Avec VTP v1/v2, les PVLAN requièrent généralement le mode transparent
! sur les plateformes Cisco concernées. Vérifier la documentation locale.
vtp mode transparent
!
vlan 100
 private-vlan primary
 private-vlan association 101,102
 exit
vlan 101
 private-vlan isolated
 exit
vlan 102
 private-vlan community
 exit
!
interface range GigabitEthernet1/0/10-11
 description HOTES_ISOLES
 switchport
 switchport mode private-vlan host
 switchport private-vlan host-association 100 101
 spanning-tree portfast
 no shutdown
!
interface range GigabitEthernet1/0/12-13
 description HOTES_COMMUNAUTE_APP
 switchport
 switchport mode private-vlan host
 switchport private-vlan host-association 100 102
 spanning-tree portfast
 no shutdown
!
interface GigabitEthernet1/0/1
 description PASSERELLE_PVLAN
 switchport
 switchport mode private-vlan promiscuous
 switchport private-vlan mapping 100 101,102
 no shutdown
end
```

**Important :** cette configuration ne suppose pas automatiquement une passerelle IP sur le commutateur. Choisis une méthode de couche 3 compatible : SVI du VLAN primaire avec association secondaire, ou passerelle externe connectée au port promiscuous. Ne configure pas arbitrairement une SVI de couche 3 sur chaque VLAN secondaire. La gamme et le logiciel imposent les limites exactes.

Vérifie au minimum :

```cisco
show vlan private-vlan
show interfaces status
show interfaces GigabitEthernet1/0/10 switchport
show running-config interface GigabitEthernet1/0/1
```

Résultats attendus dans le scénario : les hôtes isolés atteignent les destinations permises via la passerelle, mais ne communiquent pas directement entre eux au niveau 2 ; les hôtes de la même communauté peuvent communiquer entre eux. Un échec ICMP doit être interprété avec prudence : un pare-feu hôte peut bloquer le ping même si le chemin L2 est fonctionnel.


## 3. Contrôles d'accès : choisir le point d'application

### 3.1. ACL de port, ACL de VLAN et ACL de routage

Le terme « ACL VLAN » recouvre plusieurs mécanismes différents selon le constructeur. Sur Cisco, il faut notamment distinguer les ACL de port (PACL), les ACL appliquées à une SVI ou interface routée (RACL) et les VLAN ACL/VLAN maps (VACL). Leur portée et leur direction ne sont pas identiques.

| Mécanisme | Point de contrôle typique | Usage adapté | Limite à garder en tête |
|---|---|---|---|
| PACL | Port de couche 2 | Filtrer certains flux entrant sur un port | Prise en charge et types de trafic filtrables dépendent de la plateforme |
| RACL | SVI ou interface routée | Contrôler le trafic routé entre sous-réseaux | Ne bloque pas nécessairement les trames commutées localement entre hôtes du même VLAN |
| VACL / VLAN map | VLAN, pour les flux couverts par la fonction | Filtrer certains trafics bridgés et/ou routés selon l'implémentation | Syntaxe, traitement et restrictions sont propres au constructeur et au logiciel |
| PVLAN | Port L2 avec rôles associés | Isoler des hôtes au sein d'une architecture de VLAN privé | Ne remplace pas les contrôles L3/L4 ; nécessite un support PVLAN |
| Port protégé / protected port | Ports locaux sur un même commutateur, selon la plateforme | Empêcher certains échanges directs entre ports protégés | L'effet n'est pas automatiquement équivalent à une PVLAN étendue à plusieurs commutateurs |
| VRF | Domaine de routage séparé en L3 | Séparer des tables de routage et des domaines de confiance | Requiert des interfaces, routes et politiques explicites ; ce n'est pas juste un VLAN |

Avant d'écrire une ACL, réponds à ces questions : le flux est-il commuté ou routé ? Dans quel sens entre-t-il dans le point de contrôle ? IPv4, IPv6 ou non-IP ? Quel résultat est voulu ? Une règle qui n'est jamais traversée par le flux n'apporte aucune protection.

### 3.2. Exemple de contrôle inter-VLAN avec une RACL

Scénario : le VLAN 110 représente les utilisateurs (`192.0.2.0/24`) et le VLAN 120 représente des serveurs applicatifs (`198.51.100.0/24`). Le besoin est d'autoriser uniquement HTTPS des utilisateurs vers un serveur applicatif `198.51.100.20`, tout en appliquant ensuite les règles additionnelles explicitement définies par l'équipe réseau.

Exemple de structure IOS — à adapter au plan de sécurité et à la syntaxe de la plateforme :

```cisco
ip access-list extended USERS-TO-APP
 permit tcp 192.0.2.0 0.0.0.255 host 198.51.100.20 eq 443
 ! Ajouter explicitement les autres flux métier autorisés si nécessaire.
 ! Terminer la politique selon le principe de refus par défaut voulu.
 deny ip 192.0.2.0 0.0.0.255 198.51.100.0 0.0.0.255 log
 permit ip any any
!
interface Vlan110
 description PASSERELLE_UTILISATEURS
 ip access-group USERS-TO-APP in
```

Cette ACL est un exemple de raisonnement, pas une politique prête à coller en production. La dernière règle `permit ip any any` permet les autres destinations ; elle est destinée à montrer le contrôle vers le sous-réseau applicatif tout en laissant passer le reste. Si la politique exige de restreindre tout le trafic, il faut énumérer tous les flux autorisés et placer un refus final adapté. Évalue aussi le trafic retour, les besoins DNS/DHCP, IPv6, la journalisation et les règles déjà appliquées.

### 3.3. Quand la RACL ne suffit-elle pas ?

Suppose que Hôte A et Hôte B soient tous deux dans VLAN 110 et échangent directement des trames Ethernet. Le trafic peut être commuté sans passer par la SVI `Vlan110` : une RACL sur cette SVI ne filtre donc généralement pas ce chemin local. Pour empêcher cette communication, considère les mécanismes L2 compatibles, PVLAN/ports protégés, VACL ou une architecture qui force le passage par un point de contrôle. Confirme toujours la prise en charge et le chemin des paquets sur la plateforme visée.


## 4. Sécurité L2 : VLAN hopping et durcissement des ports

### 4.1. Le modèle de risque

Une attaque dite **VLAN hopping** vise à faire parvenir du trafic vers un VLAN auquel le port d'origine ne devrait pas donner accès. Deux scénarios souvent étudiés sont la négociation abusive d'un trunk via DTP et le double marquage (*double tagging*), dont les conditions dépendent notamment du comportement du trunk et du VLAN natif. Ces attaques ne signifient pas que tous les trunks sont vulnérables ; elles montrent pourquoi les rôles de ports et les VLAN natifs doivent être définis explicitement.

<figure>
<svg viewBox="0 0 900 300" role="img" aria-label="Schéma défensif d'un scénario de double marquage VLAN hopping puis mesures de mitigation" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes defenseTrace { to { stroke-dashoffset: -24; } } .defense-link { stroke-dasharray: 7 6; animation: defenseTrace 2.0s linear infinite; }</style>
  <rect x="8" y="8" width="884" height="284" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="34" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">Double tagging — comprendre le risque, puis supprimer les conditions</text>
  <rect x="30" y="65" width="170" height="76" rx="10" fill="#33231a" stroke="#fb923c"/>
  <text x="115" y="88" text-anchor="middle" fill="#fed7aa" font-size="13" font-weight="700">Port utilisateur</text>
  <text x="115" y="108" text-anchor="middle" fill="#e2e8f0" font-size="11">VLAN natif exposé ?</text>
  <text x="115" y="125" text-anchor="middle" fill="#fdba74" font-size="10">Conditions spécifiques requises</text>
  <path d="M200 103 H265" stroke="#fb923c" stroke-width="3" fill="none" class="defense-link"/>
  <polygon points="265,103 255,97 255,109" fill="#fb923c"/>
  <rect x="265" y="65" width="180" height="76" rx="10" fill="#3a1b22" stroke="#fb7185"/>
  <text x="355" y="89" text-anchor="middle" fill="#fecdd3" font-size="13" font-weight="700">Trame à double tag</text>
  <text x="355" y="109" text-anchor="middle" fill="#e2e8f0" font-size="11">Tag externe / interne</text>
  <text x="355" y="125" text-anchor="middle" fill="#fda4af" font-size="10">Scénario conceptuel</text>
  <path d="M445 103 H510" stroke="#fb7185" stroke-width="3" fill="none" class="defense-link"/>
  <polygon points="510,103 500,97 500,109" fill="#fb7185"/>
  <rect x="510" y="65" width="164" height="76" rx="10" fill="#2a1b20" stroke="#fb7185"/>
  <text x="592" y="89" text-anchor="middle" fill="#fecdd3" font-size="13" font-weight="700">Trunk mal durci</text>
  <text x="592" y="109" text-anchor="middle" fill="#e2e8f0" font-size="11">VLAN cible exposé</text>
  <text x="592" y="125" text-anchor="middle" fill="#fda4af" font-size="10">Si les conditions sont réunies</text>
  <rect x="704" y="65" width="160" height="76" rx="10" fill="#123127" stroke="#34d399"/>
  <text x="784" y="88" text-anchor="middle" fill="#a7f3d0" font-size="13" font-weight="700">Mitigation</text>
  <text x="784" y="108" text-anchor="middle" fill="#e2e8f0" font-size="11">Ports access fixes</text>
  <text x="784" y="125" text-anchor="middle" fill="#a7f3d0" font-size="10">Trunks contrôlés</text>
  <path d="M784 141 V173 H450" fill="none" stroke="#34d399" stroke-width="2.5" class="defense-link"/>
  <polygon points="450,173 460,167 460,179" fill="#34d399"/>
  <rect x="30" y="194" width="834" height="70" rx="10" fill="#102b26" stroke="#34d399"/>
  <text x="447" y="216" text-anchor="middle" fill="#a7f3d0" font-size="13" font-weight="700">Réduire la surface d'attaque</text>
  <text x="447" y="236" text-anchor="middle" fill="#d1fae5" font-size="11">switchport mode access sur les ports terminaux · DTP désactivé si pertinent · liste trunk minimale</text>
  <text x="447" y="252" text-anchor="middle" fill="#d1fae5" font-size="11">VLAN natif dédié et non utilisé · ne pas transporter les VLAN qui ne sont pas nécessaires</text>
</svg>
<figcaption>Diagramme défensif et conceptuel. Les protections réduisent les conditions favorables à l'attaque ; vérifie le comportement effectif de la plateforme et du chemin L2.</figcaption>
</figure>

### 4.2. Durcir les ports terminaux

Pour les ports connectés aux postes, imprimantes ou autres terminaux, désactive la négociation dynamique de trunk lorsque la plateforme utilise DTP et que cette négociation n'est pas nécessaire. Fixe le port en access et attribue un VLAN prévu. N'applique pas ces commandes à un trunk inter-commutateurs sans comprendre les effets.

```cisco
interface GigabitEthernet1/0/20
 description POSTE_UTILISATEUR
 switchport mode access
 switchport access vlan 110
 ! Sur les plateformes compatibles, empêcher DTP sur ce port terminal
 switchport nonegotiate
 spanning-tree portfast
 no shutdown
```

`switchport nonegotiate` est pertinent sur certaines plateformes Cisco qui prennent en charge DTP ; la commande et ses effets varient selon le modèle. `spanning-tree portfast` convient aux ports d'extrémité et ne doit pas être appliqué aveuglément aux liens inter-commutateurs. Le durcissement STP complémentaire doit suivre les consignes de la plateforme et la politique réseau.

### 4.3. Durcir les trunks

```cisco
interface GigabitEthernet1/0/48
 description UPLINK_VERS_DISTRIBUTION
 switchport mode trunk
 switchport trunk allowed vlan 110,120,130,190
 switchport trunk native vlan 998
 switchport nonegotiate
 no shutdown
```

Avant d'appliquer cette configuration, vérifie que la liaison distante est configurée en conséquence, que le VLAN natif prévu existe si nécessaire et que la liste autorisée comprend tous les VLAN requis par les services. L'exemple remplace la liste autorisée par `110,120,130,190` sur les plateformes où cette syntaxe s'applique : il ne faut pas le coller si d'autres VLAN doivent rester transportés. Vérifie ensuite :

```cisco
show interfaces trunk
show interfaces GigabitEthernet1/0/48 switchport
show running-config interface GigabitEthernet1/0/48
```

Ne te fie pas uniquement au texte de la configuration ; contrôle le mode opérationnel, la liste autorisée, les VLAN actifs et l'état des liens.

### 4.4. VLAN natif dédié : ce que la mesure apporte et n'apporte pas

Placer le VLAN natif sur un identifiant réservé, non attribué aux utilisateurs, et cohérent des deux côtés d'un trunk est une bonne mesure de réduction du risque. Il faut aussi éviter les ports inutilisés ou les trunks dynamiques non contrôlés et appliquer une liste minimale de VLAN autorisés. Changer le VLAN natif seul ne remplace pas ces mesures, ne chiffre pas les trames et ne fournit pas une politique d'accès de couche 3.

Sur certaines plateformes, le marquage des trames du VLAN natif peut être activé ; la syntaxe et les contraintes diffèrent. Ne suppose pas que cette option soit disponible partout. Si un VLAN natif non utilisé est configuré, ne connecte pas de terminaux ordinaires dessus.


## 5. Protection des hôtes de couche 2 : DHCP Snooping, DAI et IP Source Guard

### 5.1. Pourquoi ces fonctionnalités sont liées

Un VLAN fournit une zone de diffusion, mais un hôte compromis dans ce VLAN peut essayer de se faire passer pour un serveur DHCP, d'usurper une association IP/MAC au moyen d'ARP ou d'utiliser une adresse IP source qui ne lui a pas été attribuée.

Trois fonctions peuvent se compléter sur les plateformes compatibles :

- **DHCP Snooping** : filtre certains messages DHCP selon l'état trusted/untrusted des interfaces et construit une base de liaisons DHCP ;
- **Dynamic ARP Inspection (DAI)** : valide les messages ARP entrants selon une base fiable telle que celle du DHCP Snooping, ou au moyen d'ARP ACL pour certains hôtes statiques ;
- **IP Source Guard (IPSG)** : limite les paquets IP sur des ports L2 à partir des liaisons connues ou configurées.

<figure>
<svg viewBox="0 0 900 300" role="img" aria-label="Chaîne de sécurité couche 2 entre port utilisateur, DHCP Snooping, base de liaisons et contrôle ARP/IP" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes securityTrace { to { stroke-dashoffset: -26; } } .security-path { stroke-dasharray: 7 6; animation: securityTrace 2s linear infinite; }</style>
  <rect x="8" y="8" width="884" height="284" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="34" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">De l'identité DHCP à la validation de trafic</text>
  <rect x="28" y="68" width="166" height="76" rx="10" fill="#17243a" stroke="#60a5fa"/>
  <text x="111" y="91" text-anchor="middle" fill="#bfdbfe" font-size="13" font-weight="700">Port utilisateur</text>
  <text x="111" y="111" text-anchor="middle" fill="#e2e8f0" font-size="11">untrusted</text>
  <text x="111" y="127" text-anchor="middle" fill="#cbd5e1" font-size="10">DHCP client / trafic IP</text>
  <path d="M194 106 H239" fill="none" stroke="#60a5fa" stroke-width="3" class="security-path"/><polygon points="239,106 229,100 229,112" fill="#60a5fa"/>
  <rect x="239" y="68" width="190" height="76" rx="10" fill="#123127" stroke="#34d399"/>
  <text x="334" y="91" text-anchor="middle" fill="#a7f3d0" font-size="13" font-weight="700">DHCP Snooping</text>
  <text x="334" y="111" text-anchor="middle" fill="#e2e8f0" font-size="11">Filtre DHCP selon le port</text>
  <text x="334" y="127" text-anchor="middle" fill="#d1fae5" font-size="10">Construit les bindings</text>
  <path d="M429 106 H474" fill="none" stroke="#34d399" stroke-width="3" class="security-path"/><polygon points="474,106 464,100 464,112" fill="#34d399"/>
  <rect x="474" y="68" width="166" height="76" rx="10" fill="#1e293b" stroke="#a78bfa"/>
  <text x="557" y="91" text-anchor="middle" fill="#ddd6fe" font-size="13" font-weight="700">Binding DB</text>
  <text x="557" y="111" text-anchor="middle" fill="#e2e8f0" font-size="11">IP ↔ MAC ↔ VLAN</text>
  <text x="557" y="127" text-anchor="middle" fill="#cbd5e1" font-size="10">Interface / bail connu</text>
  <path d="M640 106 H685" fill="none" stroke="#a78bfa" stroke-width="3" class="security-path"/><polygon points="685,106 675,100 675,112" fill="#a78bfa"/>
  <rect x="685" y="68" width="185" height="76" rx="10" fill="#33231a" stroke="#fb923c"/>
  <text x="777" y="91" text-anchor="middle" fill="#fed7aa" font-size="13" font-weight="700">Contrôles associés</text>
  <text x="777" y="111" text-anchor="middle" fill="#e2e8f0" font-size="11">DAI · IP Source Guard</text>
  <text x="777" y="127" text-anchor="middle" fill="#fdba74" font-size="10">Valider selon la politique</text>
  <rect x="28" y="184" width="842" height="72" rx="10" fill="#17202f" stroke="#475569"/>
  <text x="449" y="206" text-anchor="middle" fill="#e2e8f0" font-size="13" font-weight="700">Prérequis et précautions</text>
  <text x="449" y="226" text-anchor="middle" fill="#cbd5e1" font-size="11">Ne faire confiance qu'aux ports qui mènent réellement vers les serveurs DHCP légitimes.</text>
  <text x="449" y="243" text-anchor="middle" fill="#cbd5e1" font-size="11">Pour les adresses statiques, prévoir les bindings ou ACL ARP adaptés ; contrôler les faux positifs.</text>
</svg>
<figcaption>La base de liaisons est un point de dépendance. Une erreur de trust ou une base incomplète peut bloquer des clients légitimes.</figcaption>
</figure>

### 5.2. Exemple conceptuel de configuration

Exemple à valider sur la plateforme. L'interface `Gi1/0/48` est l'uplink vers le réseau contenant le serveur DHCP légitime ; `Gi1/0/10-20` sont des ports utilisateur. Ajuste les VLAN et les limites au réseau réel.

```cisco
configure terminal
ip dhcp snooping
ip dhcp snooping vlan 110,120
!
interface GigabitEthernet1/0/48
 description UPLINK_VERS_INFRA_DHCP
 ip dhcp snooping trust
!
interface range GigabitEthernet1/0/10-20
 description PORTS_UTILISATEURS_NON_FIABLES
 no ip dhcp snooping trust
 ! Limite illustrative ; dimensionner selon le type de terminaux
 ip dhcp snooping limit rate 15
!
! DAI s'appuie souvent sur les bindings DHCP Snooping.
ip arp inspection vlan 110,120
!
end
```

N'applique pas une valeur de limitation sans mesurer le nombre de messages normalement émis et sans tenir compte des téléphones, points d'accès, relais et mécanismes DHCP présents. Les commandes de trust et la prise en charge de certaines fonctionnalités varient selon le matériel et le logiciel. Les interfaces connectées à de vrais serveurs DHCP doivent être identifiées précisément : rendre un port terminal trusted peut annuler une partie de la protection.

### 5.3. Hôtes à adresse statique

DAI qui dépend uniquement des bindings DHCP n'a pas nécessairement de correspondance pour les hôtes configurés statiquement. Selon la plateforme, il peut être nécessaire de créer une ARP ACL ou des bindings statiques. Prévois aussi la stratégie pour les imprimantes, serveurs, téléphones ou appareils IoT ayant des paramètres statiques.

### 5.4. Ordre de déploiement recommandé

1. Inventorier les VLAN et les appareils statiques/dynamiques.
2. Vérifier que le DHCP fonctionne et identifier les vrais ports vers les serveurs.
3. Activer DHCP Snooping sur un VLAN pilote et contrôler la base de liaisons.
4. Définir les bindings ou ARP ACL nécessaires aux appareils statiques.
5. Activer DAI sur le VLAN pilote et vérifier compteurs/journaux.
6. Ajouter IPSG sur un petit lot de ports compatibles.
7. Tester renouvellement DHCP, téléphonie, imprimantes, mobilité et retour arrière.
8. Étendre par vagues en documentant les résultats.

Ne déploie pas toutes ces fonctions sur l'ensemble du campus en une seule opération non testée.


## 6. STP à l'échelle VLAN : PVST+, Rapid-PVST+ et MST

### 6.1. Pourquoi les VLAN impactent STP

Les VLAN définissent des domaines L2 ; Spanning Tree protège la topologie commutée des boucles. Le mode STP choisi influence le nombre d'instances, le calcul des chemins et la façon de faire correspondre la topologie aux VLAN. Une conception experte doit éviter à la fois les boucles et les topologies inutilement complexes.

| Mode | Idée générale | Implication de conception |
|---|---|---|
| PVST+ | Une instance STP par VLAN sur les plateformes qui le prennent en charge | Contrôle fin par VLAN, mais nombre d'instances et charge de gestion plus élevés |
| Rapid-PVST+ | Variante à convergence rapide du STP par VLAN | Convergence généralement améliorée, toujours avec plusieurs instances |
| MST | Plusieurs VLAN peuvent être mappés à un nombre réduit d'instances MST | Réduit le nombre d'instances, mais exige une région cohérente et un mapping identique |

Les valeurs par défaut, les modes disponibles et les limites d'instances dépendent de la famille de commutateurs et de la version. N'effectue pas une migration STP sur un réseau de production en copiant une configuration de laboratoire sans vérifier la topologie et les frontières STP.

### 6.2. Comprendre les régions MST

Pour appartenir à la même région MST, les commutateurs doivent partager les attributs de région requis par le protocole, notamment le nom de région, le numéro de révision et la correspondance VLAN-vers-instances. Si le mapping diffère, un équipement peut se trouver à la frontière d'une région au lieu d'être un membre cohérent de la région attendue.

<figure>
<svg viewBox="0 0 900 300" role="img" aria-label="Deux commutateurs membres d'une même région MST avec le même nom, la même révision et le même mapping de VLAN" style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">
  <style>@keyframes mstFlow { to { stroke-dashoffset: -24; } } .mst-link { stroke-dasharray: 7 6; animation: mstFlow 2.2s linear infinite; }</style>
  <rect x="8" y="8" width="884" height="284" rx="18" fill="#0b1220" stroke="#334155"/>
  <text x="450" y="34" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">MST — l'identité de région doit correspondre</text>
  <rect x="34" y="65" width="300" height="148" rx="12" fill="#102b35" stroke="#22d3ee" stroke-width="1.5"/>
  <text x="184" y="89" text-anchor="middle" fill="#a5f3fc" font-size="14" font-weight="700">SW-DIST-1</text>
  <text x="184" y="115" text-anchor="middle" fill="#e2e8f0" font-size="12">Nom : CAMPUS-A</text>
  <text x="184" y="136" text-anchor="middle" fill="#e2e8f0" font-size="12">Révision : 7</text>
  <text x="184" y="157" text-anchor="middle" fill="#e2e8f0" font-size="12">MST 1 : VLAN 110,120</text>
  <text x="184" y="178" text-anchor="middle" fill="#e2e8f0" font-size="12">MST 2 : VLAN 130,140</text>
  <text x="184" y="197" text-anchor="middle" fill="#a7f3d0" font-size="10">Configuration candidate</text>
  <path d="M334 137 H566" fill="none" stroke="#34d399" stroke-width="4" class="mst-link"/>
  <polygon points="566,137 554,130 554,144" fill="#34d399"/>
  <text x="450" y="121" text-anchor="middle" fill="#a7f3d0" font-size="11" font-weight="700">Lien dans la région</text>
  <rect x="566" y="65" width="300" height="148" rx="12" fill="#123127" stroke="#34d399" stroke-width="1.5"/>
  <text x="716" y="89" text-anchor="middle" fill="#a7f3d0" font-size="14" font-weight="700">SW-DIST-2</text>
  <text x="716" y="115" text-anchor="middle" fill="#e2e8f0" font-size="12">Nom : CAMPUS-A</text>
  <text x="716" y="136" text-anchor="middle" fill="#e2e8f0" font-size="12">Révision : 7</text>
  <text x="716" y="157" text-anchor="middle" fill="#e2e8f0" font-size="12">MST 1 : VLAN 110,120</text>
  <text x="716" y="178" text-anchor="middle" fill="#e2e8f0" font-size="12">MST 2 : VLAN 130,140</text>
  <text x="716" y="197" text-anchor="middle" fill="#a7f3d0" font-size="10">Même digest de région attendu</text>
  <rect x="34" y="231" width="832" height="40" rx="9" fill="#1e293b" stroke="#64748b"/>
  <text x="450" y="247" text-anchor="middle" fill="#e2e8f0" font-size="11" font-weight="700">Un mapping différent peut créer une frontière MST inattendue</text>
  <text x="450" y="261" text-anchor="middle" fill="#cbd5e1" font-size="10">Contrôler le nom, la révision, le mapping et le digest avant le basculement.</text>
</svg>
<figcaption>Le numéro de révision MST est un paramètre de configuration de région ; ce n'est pas le numéro de révision VTP. Les deux concepts ne doivent pas être confondus.</figcaption>
</figure>

Exemple de configuration à harmoniser sur les commutateurs qui doivent appartenir à la même région :

```cisco
spanning-tree mode mst
!
spanning-tree mst configuration
 name CAMPUS-A
 revision 7
 instance 1 vlan 110,120
 instance 2 vlan 130,140
 exit
```

Le choix de la valeur de révision est une convention administrative : tous les équipements d'une même région doivent avoir les mêmes attributs de région. Le numéro `7` n'a pas de signification universelle. Les VLAN non explicitement attribués restent dans l'instance par défaut selon le fonctionnement MST de la plateforme.

Vérification indicative :

```cisco
show spanning-tree mst
show spanning-tree mst configuration
show spanning-tree mst configuration digest
show spanning-tree root
show spanning-tree inconsistentports
```

Toutes les commandes de vérification ne sont pas présentes sous le même nom dans chaque version ; utiliser la documentation du logiciel si une variante est requise.

### 6.3. Placement de racine STP

Le commutateur racine STP est un élément de conception, pas seulement un équipement élu par défaut. Détermine les racines primaires et secondaires adaptées à la topologie et, si plusieurs instances ou VLAN existent, établis le mapping et les priorités de façon cohérente.

```cisco
! Exemple uniquement : utiliser la commande adaptée au mode STP choisi.
spanning-tree vlan 110,120 root primary
spanning-tree vlan 130,140 root secondary
```

Cet exemple concerne un mode où la commande par VLAN est prise en charge, comme PVST+/Rapid-PVST+ sur certaines plateformes. Ne le mélange pas à l'aveugle avec une configuration MST. En MST, le choix de racine se raisonne par instance. Après un changement, vérifie le root bridge effectif, les ports bloqués/en transfert et les chemins réels.


## 7. VLAN, SVI et VRF : séparer les domaines L2 et L3

### 7.1. Ce que change une VRF

Une VRF (*Virtual Routing and Forwarding*) maintient une table de routage distincte dans un équipement L3 compatible. Deux VLAN peuvent être séparés au niveau L2 et néanmoins être routés dans une même table globale par des SVI ; ils ne sont pas automatiquement isolés de bout en bout au niveau IP. Une séparation par VRF permet de distinguer les tables de routage, mais les échanges entre VRF requièrent une architecture et des politiques explicites.

```text
                      COMMUTATEUR MULTICOUCHE

      VLAN 110                         VLAN 120
      USERS                            SERVERS
        |                                  |
      SVI 110                           SVI 120
        |                                  |
        v                                  v
    +----------------+              +----------------+
    | VRF USERS      |              | VRF SERVERS    |
    | Table de route |              | Table de route |
    +----------------+              +----------------+
             \                           /
              \---- Pare-feu / routeur -/
                    inter-VRF contrôlé

  La présence d'une route entre les deux domaines doit être conçue.
```

Le schéma est conceptuel : la séparation effective dépend des associations d'interfaces à leurs VRF, des routes, du routage, des ACL et des équipements interconnectés. Deux VRF ne doivent pas être considérées comme étanches si une route de fuite ou un dispositif intermédiaire leur permet de communiquer.

### 7.2. Matrice de flux avant de configurer

| Source | Destination | Besoin | Décision à formaliser |
|---|---|---|---|
| Utilisateurs | DNS/DHCP | Résolution et attribution d'adresse | Autoriser seulement les services nécessaires |
| Utilisateurs | Serveur applicatif | HTTPS vers des destinations précises | ACL L3/L4 ou pare-feu selon le design |
| Utilisateurs | Administration réseau | Généralement interdit depuis les VLAN utilisateurs | Séparer le réseau de gestion et contrôler les flux |
| Serveurs applicatifs | Base de données | Ports métier documentés | Limiter les destinations et ports |
| Invités | Réseaux internes | Non requis dans le scénario habituel | Internet uniquement via politique dédiée |
| Supervision | Équipements réseau | Protocoles d'administration/supervision | Autoriser depuis des hôtes de gestion connus |

Cette matrice doit intégrer IPv4 **et** IPv6 lorsque les deux protocoles sont activés. Une politique IPv4 correcte n'empêche pas automatiquement un flux IPv6 non filtré.


## 8. QinQ et VLAN à grande échelle : points d'architecture

### 8.1. Le rôle de l'empilement de tags

Le mécanisme dit **QinQ** ou *VLAN stacking*, couramment associé au pontage fournisseur IEEE 802.1ad et aux extensions du pontage Ethernet, permet de transporter des trames client en ajoutant un tag externe de fournisseur autour du tag client, suivant l'architecture et la plateforme. Le tag externe peut identifier un service ou un client dans le réseau de transport ; le tag interne conserve l'identité VLAN du client.

```text
Trame Ethernet cliente
+-------------+------------------+----------------+
| MAC dst/src | Tag client C-VLAN| Données / FCS  |
+-------------+------------------+----------------+
                     |
                     v  encapsulation fournisseur
+-------------+------------------+------------------+----------------+
| MAC dst/src | Tag S-VLAN externe| Tag C-VLAN interne| Données / FCS |
+-------------+------------------+------------------+----------------+
```

QinQ n'est pas nécessaire pour la plupart des petits campus de niveau débutant ou intermédiaire. Il devient pertinent pour certains réseaux de transport Ethernet, environnements multi-clients ou designs de fournisseur. L'encapsulation exacte, le comportement des tags, les MTU et les options de rewrite sont dépendants de l'implémentation. Un tag additionnel augmente la taille de trame : contrôle l'alignement MTU sur tout le chemin.

### 8.2. VLAN IDs, échelle et documentation

Le fait que l'identifiant VLAN puisse être compris dans la plage 1–4094 dans les environnements 802.1Q ne signifie pas que toutes les fonctions, versions VTP ou gammes d'équipements peuvent propager et utiliser chaque identifiant de la même manière. Prends en compte les plages réservées, les fonctions de contrôle, le nombre d'instances STP, les limites matérielles et les exigences d'exploitation.

Pour une architecture grande, la fiche de chaque VLAN devrait contenir : identifiant, nom, sous-réseau, passerelle, VRF, propriétaire, but, portée L2, trunks autorisés, politique de sécurité, services requis, plan de monitoring, dépendances STP/MST et procédure de retrait.


## 9. Automatiser le contrôle de conformité

### 9.1. Une liste attendue et un état observé

Avant un changement, définis un état attendu. Ne compare pas seulement les fichiers de configuration : le plan doit aussi se vérifier dans l'état opérationnel.

| Objet | Source de vérité | Contrôle utile |
|---|---|---|
| VLAN | Registre de VLAN approuvé | `show vlan brief` |
| Trunk | Matrice de liens et de VLAN permis | `show interfaces trunk` |
| Mode de port | Inventaire d'interfaces | `show interfaces switchport` |
| PVLAN | Tableau primary/secondary/role | `show vlan private-vlan` |
| SVI | Plan IP et VRF | `show ip interface brief`, commandes VRF adaptées |
| STP/MST | Design de topologie et mapping | `show spanning-tree`, commandes MST compatibles |
| DHCP Snooping | Ports trusted, VLAN couverts, bindings attendus | `show ip dhcp snooping`, bindings et statistiques disponibles |
| DAI/IPSG | VLAN ciblés, trust, exceptions statiques | Commandes de vérification de la plateforme et journaux |

### 9.2. Exemple de logique de contrôle en pseudo-code

Ce pseudo-code montre le raisonnement d'un contrôle automatisé. Il n'est pas un programme directement exécutable : les commandes d'accès aux équipements et l'analyse des sorties doivent être implémentées pour les systèmes employés.

```python
expected = {
    "VLAN 110": {"name": "USERS", "required_on": ["SW1", "SW2"]},
    "VLAN 120": {"name": "SERVERS", "required_on": ["SW1", "SW2"]},
}

for vlan_id, spec in expected.items():
    for switch in spec["required_on"]:
        observed = inventory[switch].vlans.get(vlan_id)
        if observed is None:
            report.add_error(switch, vlan_id, "VLAN absent")
        elif observed.name != spec["name"]:
            report.add_error(switch, vlan_id, "Nom inattendu")

for link in approved_trunks:
    observed = inventory[link.switch].trunks.get(link.interface)
    if observed is None:
        report.add_error(link.switch, link.interface, "Trunk absent")
        continue
    missing = set(link.required_vlans) - set(observed.allowed_vlans)
    extra = set(observed.allowed_vlans) - set(link.required_vlans)
    if missing:
        report.add_error(link.switch, link.interface, f"VLAN manquants: {sorted(missing)}")
    if extra:
        report.add_warning(link.switch, link.interface, f"VLAN inattendus: {sorted(extra)}")
```

Un contrôle utile doit différencier une erreur bloquante, un avertissement et une exception approuvée. Il faut éviter qu'un changement de nom ou l'ordre des VLAN dans une sortie CLI déclenche des alertes inutiles ; normalise les données avant de les comparer. Garde aussi les sorties brutes comme preuve d'audit.

### 9.3. Préserver une preuve avant/après

Pour chaque changement significatif, conserve au minimum :

- l'objectif et l'approbation du changement ;
- les configurations ciblées et leur sauvegarde ;
- les sorties avant modification ;
- les commandes appliquées et leur résultat ;
- les sorties après modification ;
- les tests métiers et de connectivité ;
- la décision finale : succès, retour arrière ou investigation complémentaire.


## 10. Méthode experte de dépannage

### 10.1. Suivre le chemin réel du paquet

Quand un flux échoue, ne commence pas par changer les VLAN au hasard. Localise d'abord le type de flux et son trajet.

```text
Hôte source
   |
   v
Port access (VLAN attendu ? / sécurité L2 ?)
   |
   v
Commutation locale (PVLAN/protected port/VACL ?)
   |
   v
Trunk (VLAN autorisé, natif cohérent, lien actif ?)
   |
   v
Commutateur suivant (VLAN présent ? STP en forwarding ?)
   |
   v
Passerelle L3 (SVI up/up ? ACL ? VRF ? route ?)
   |
   v
Destination (pare-feu, retour, route asymétrique ?)
```

La séquence est une carte de diagnostic, pas une preuve que chaque flux traverse chaque élément. Un flux L2 local peut ne jamais atteindre le trunk ou la SVI. Adapte le chemin au routage et à la topologie réels.

### 10.2. Commandes d'enquête

```cisco
show vlan brief
show interfaces status
show interfaces trunk
show interfaces GigabitEthernet1/0/20 switchport
show mac address-table dynamic vlan 110
show spanning-tree vlan 110
show ip interface brief
show access-lists
show logging
```

Pour un incident plus avancé, ajoute les commandes de contrôle de PVLAN, DAI/DHCP Snooping, IP Source Guard, MST ou VRF pertinentes pour la gamme. Les syntaxes de `show` varient avec le système. Consulte la documentation correspondant au modèle exact plutôt que de supposer que toutes les commandes existent partout.

### 10.3. Cas d'incident : le VLAN est présent, mais l'application ne répond plus

**Symptômes :** les postes ont une adresse IP ; le VLAN existe sur les commutateurs ; le ping de la passerelle réussit ; l'application TCP d'un autre VLAN échoue.

Hypothèses à départager :

1. la liste autorisée sur un trunk intermédiaire ne permet pas le VLAN source ou le VLAN destination ;
2. STP ne place pas le chemin attendu en état forwarding pour le VLAN / l'instance ;
3. la RACL ou la VACL filtre le flux ;
4. la SVI est rattachée à la mauvaise VRF ou les routes sont absentes ;
5. le pare-feu ou le serveur bloque le port TCP, ou le trafic retour suit un chemin différent ;
6. une fonction de sécurité L2 bloque une trame liée au service.

**Méthode :** tester le même service depuis une autre source autorisée, vérifier la route et la politique L3, examiner les compteurs d'ACL/journaux, puis suivre le chemin L2 au besoin. La réussite d'un ping ne prouve pas que le port TCP applicatif est permis ; l'échec d'un ping ne prouve pas non plus que le service TCP est inaccessible.

### 10.4. Cas d'incident : certains clients DHCP sont bloqués après activation de la sécurité L2

Ne désactive pas immédiatement toutes les protections. Compare d'abord les ports en échec et ceux qui fonctionnent : VLAN, rôle trust/untrust, état du binding, type de client, adressage statique ou dynamique, port-channel et chemins redondants. Vérifie les compteurs de drops et la table de bindings. Si l'incident vient d'un serveur DHCP légitime reçu sur un port mal classé, corrige uniquement le rôle du port confirmé. Pour les hôtes statiques, ajoute une exception documentée adaptée à la fonction plutôt que de faire confiance globalement à tous les ports.

### 10.5. Cas d'incident : un changement MST a modifié le chemin L2

Compare la région MST avant/après : nom, révision, mapping, digest et root/roles des ports. Contrôle également si un lien est devenu frontière entre régions. Si la panne touche seulement certains VLAN, compare leur mapping d'instance et la liste de VLAN autorisés sur les trunks. N'accumule pas des changements de priorité STP, de trunk et de VLAN dans la même intervention : isole la cause et applique le retour arrière prévu si les effets s'écartent des critères d'acceptation.


## 11. Laboratoires pratiques

### Laboratoire 1 — Isoler des hôtes avec PVLAN

**But :** configurer des ports isolés, des ports communauté et un port promiscuous, puis prouver les résultats attendus.

**Topologie textuelle :**

```text
Hôte A (isolé) ---- SW1 ---- Hôte B (isolé)
                       |
                   Passerelle
                       |
                Hôte C -- Hôte D
                  même communauté
```

**Étapes :**

1. Vérifier dans la documentation si le commutateur/l'émulateur prend en charge PVLAN.
2. Créer le VLAN primaire et les VLAN secondaires.
3. Configurer les associations et les types de ports.
4. Mettre en place la passerelle selon la méthode prise en charge.
5. Tester A vers B, C vers D, A vers passerelle et C vers passerelle.
6. Sauvegarder les sorties `show vlan private-vlan` et `show interfaces ... switchport`.

**Critères de réussite :** A↔B est bloqué au niveau L2 ; C↔D est permis ; les hôtes atteignent la passerelle si celle-ci est correctement configurée. Distingue l'isolation L2 d'un éventuel filtrage ICMP sur les terminaux.

### Laboratoire 2 — Durcir les trunks sans interrompre les VLAN requis

**But :** identifier les VLAN nécessaires et configurer une liste explicite.

1. Crée une matrice de VLAN attendus par trunk.
2. Capture `show interfaces trunk` avant changement.
3. Compare VLAN présents, actifs et autorisés.
4. Applique la liste minimale sur les deux extrémités en environnement de test.
5. Teste les flux témoins de chaque VLAN.
6. Déclenche un incident contrôlé en omettant un VLAN de lab, observe le symptôme, puis rétablis la configuration attendue.

Ne reproduis pas l'omission d'un VLAN de production. Le retour arrière doit être prêt avant le test.

### Laboratoire 3 — Déployer DHCP Snooping et DAI progressivement

1. Identifie le vrai chemin vers le serveur DHCP.
2. Active DHCP Snooping sur un seul VLAN pilote.
3. Définis uniquement les uplinks appropriés comme trusted.
4. Renouvelle les baux DHCP et vérifie la table de bindings.
5. Active DAI sur le VLAN pilote et examine les compteurs.
6. Teste un poste statique avec la méthode d'exception documentée.
7. Documente les commandes de vérification et de retour arrière.

**Critères de réussite :** le client légitime obtient et renouvelle son adresse ; les ports terminaux ne sont pas trusted sans raison ; les alertes et drops sont expliqués.

### Laboratoire 4 — Concevoir une région MST contrôlée

Sur les équipements qui le prennent en charge, crée deux instances, attribue un petit groupe de VLAN à chacune, et configure deux commutateurs avec le même nom, la même révision et le même mapping.

1. Capture l'état MST initial.
2. Prépare les attributs de région sur les commutateurs.
3. Vérifie la configuration et le digest avant d'appliquer le mode selon la procédure de ta plateforme.
4. Contrôle l'appartenance à la région, la racine par instance et les ports forwarding/blocking.
5. Modifie uniquement le mapping d'un commutateur en laboratoire et observe la frontière créée.
6. Rétablis le mapping cohérent et confirme le retour à la région prévue.

Un simulateur qui ne supporte pas MST fidèlement permet seulement de travailler le raisonnement ; n'en déduis pas que toutes les sorties ou réactions de matériel réel seront identiques.


## 12. Exercices d'évaluation

### Exercice 1 — RACL ou isolation L2 ?

Deux machines du même VLAN communiquent directement au niveau Ethernet. Une ACL est appliquée en entrée de la SVI du VLAN. Le trafic entre ces deux machines est-il nécessairement filtré ? Explique pourquoi.

### Exercice 2 — Choisir un mécanisme

Associe chaque besoin au mécanisme qui répond le mieux au besoin initial, puis mentionne une limite :

1. Isoler des clients entre eux tout en gardant une passerelle commune, sur une plateforme compatible.
2. Interdire un flux IP routé entre utilisateurs et serveurs.
3. Séparer les tables de routage de deux domaines de confiance.
4. Bloquer les réponses DHCP serveur reçues depuis des ports utilisateurs.
5. Réduire le nombre d'instances STP sur un réseau qui a de nombreux VLAN.

### Exercice 3 — Native VLAN et trunks

Un trunk est opérationnel, mais le VLAN natif ne correspond pas sur les deux côtés. Quelle est ta procédure d'enquête ? Cite au moins trois vérifications et explique pourquoi changer seulement le VLAN natif sans plan n'est pas une opération anodine.

### Exercice 4 — Incident DAI

Après activation de DAI, un serveur avec IP statique perd certaines communications. Quelles informations recueillir avant de désactiver DAI ? Donne une approche permettant de traiter le serveur sans rendre tous les ports trusted.

### Exercice 5 — MST

Deux commutateurs ont le même nom de région et le même numéro de révision, mais leurs mappings VLAN/instance diffèrent. Qu'est-ce que cela peut provoquer ? Comment le vérifier ?

### Exercice 6 — Plan de changement

Tu dois ajouter le VLAN 160 aux commutateurs SW1, SW2 et SW3. Le VLAN doit traverser SW1–SW2, mais pas SW2–SW3. Rédige un plan avant/pendant/après : changements attendus, commandes de vérification, test métier et retour arrière.

### Exercice 7 — Analyse de configuration

Sur un port terminal, tu trouves `switchport mode dynamic desirable`. Quels risques ou ambiguïtés cela crée-t-il ? Quelle configuration explicite envisages-tu pour un PC ordinaire et quelles précautions vérifies-tu avant de l'appliquer ?

### Exercice 8 — Matrice de flux

Une application située dans le VLAN Serveurs doit recevoir HTTPS depuis le VLAN Utilisateurs et des connexions SQL uniquement depuis un serveur applicatif. Quel tableau de flux préparerais-tu ? À quels points appliquer les politiques ? Comment vérifier que les flux retour sont corrects ?

### Exercice 9 — Analyse d'échec

Un client reçoit une adresse DHCP et peut joindre sa passerelle, mais ne peut pas accéder au serveur applicatif. Énonce une séquence de diagnostic qui évite de recréer le VLAN sans preuve.

### Exercice 10 — Question de synthèse

Explique pourquoi « séparer les services en VLAN » et « garantir l'isolation de sécurité entre les services » ne sont pas des formulations équivalentes. Donne un exemple utilisant L2, L3 et une politique d'accès.


## 13. Corrigés commentés

### Correction 1

Pas nécessairement. Le trafic entre deux machines du même VLAN peut être commuté localement au niveau 2 sans traverser la SVI ; une RACL sur cette SVI ne voit donc généralement pas ce flux. Envisage une fonction d'isolation L2, PVLAN, port protégé, VACL ou une architecture qui fait traverser le trafic par un point de contrôle approprié, selon la prise en charge de la plateforme.

### Correction 2

1. PVLAN, avec ports isolés/communauté/promiscuous ; vérifier la compatibilité, les associations et la passerelle.
2. RACL sur le chemin routé ou pare-feu selon les exigences ; définir précisément les flux et le trafic retour.
3. VRF avec routage/politiques inter-VRF explicites ; une fuite de route peut rétablir une connectivité prévue ou non.
4. DHCP Snooping en classant correctement les interfaces trusted/untrusted ; tester les vrais serveurs, relais et clients.
5. MST, en définissant et validant le mapping et l'identité de région sur les commutateurs concernés.

### Correction 3

Comparer `show interfaces trunk`, `show interfaces ... switchport`, les deux configurations d'interface, la connectivité et les journaux STP/VLAN pertinents. Vérifier l'état opérationnel, la liste de VLAN autorisés et le VLAN natif des deux côtés. Un changement natif peut affecter le traitement des trames non marquées, l'alignement du pair et certains mécanismes de contrôle ; il doit être coordonné avec le réseau distant.

### Correction 4

Recueillir VLAN, port, IP/MAC attendues, présence des bindings DHCP, état DHCP Snooping, statistiques DAI, interface et chemin. Pour une IP statique, vérifier le mécanisme documenté par la plateforme — ARP ACL ou binding pertinent — et le tester dans un VLAN pilote. N'accorde pas le trust général aux ports utilisateurs pour contourner un blocage.

### Correction 5

Les commutateurs peuvent se trouver de part et d'autre d'une frontière MST au lieu d'appartenir à la même région. Vérifie le mode STP, le nom, la révision, le mapping et le digest de la région ; inspecte les rôles/états des ports après comparaison. Aligne les attributs selon un plan de changement contrôlé.

### Correction 6

**Avant :** exporter les configurations, établir la liste de VLAN par switch/trunk et identifier les ports/services concernés. **Pendant :** créer le VLAN sur les équipements où il est requis ; ajouter le VLAN uniquement au trunk SW1–SW2 ; ne pas ajouter VLAN 160 à SW2–SW3. **Après :** vérifier `show vlan brief`, `show interfaces trunk`, STP pour le VLAN si applicable, puis les tests de bout en bout. **Retour arrière :** retirer l'ajout trunk et supprimer le VLAN seulement après avoir confirmé qu'aucun service n'en dépend.

### Correction 7

Le mode dynamique peut négocier un trunk avec un voisin compatible et créer une ambiguïté sur le rôle de l'interface. Pour un PC ordinaire, un port access explicite avec VLAN attribué, et la négociation désactivée si supportée et souhaitée, réduit cette surface. Avant application, confirme qu'il s'agit bien d'un terminal et non d'un téléphone, d'un point d'accès ou d'une liaison nécessitant plusieurs VLAN.

### Correction 8

Lister source, destination, protocole/port, sens, propriétaire et motif. Autoriser HTTPS du VLAN Utilisateurs au serveur cible ; limiter SQL au serveur applicatif. Placer la politique sur les interfaces/pare-feu qui voient réellement ces flux, contrôler les politiques retour et IPv6, puis vérifier les compteurs et tester les ports TCP réels plutôt que de se limiter au ping.

### Correction 9

Vérifier le chemin de couche 3, la route et la VRF, les ACL/RACL, VACL/PACL éventuelles, le trunk et les VLAN autorisés, STP si le chemin L2 est en cause, les logs du pare-feu et le serveur de destination. Le fonctionnement DHCP et la réussite du ping de passerelle montrent que certaines étapes fonctionnent, mais ne prouvent pas que l'application est permise ni joignable.

### Correction 10

Le VLAN sépare les domaines de diffusion au niveau L2 ; il ne définit pas seul les accès IP autorisés. Par exemple, les VLAN Utilisateurs et Serveurs peuvent posséder chacun une SVI et être routés. Pour limiter les services, il faut des ACL L3/L4 ou un pare-feu. Pour bloquer la communication directe entre hôtes dans un même VLAN, une RACL sur la SVI peut ne pas suffire ; une isolation L2 ou une autre architecture de contrôle peut être nécessaire.


## 14. Runbook expert pour un changement de segmentation

### Avant le changement

- [ ] Vérifier la demande, le propriétaire de l'application et la fenêtre de maintenance.
- [ ] Cartographier le chemin L2 et L3 des flux concernés.
- [ ] Sauvegarder les configurations et les sorties opérationnelles utiles.
- [ ] Confirmer la liste des VLAN, les trunks, le VLAN natif, les rôles STP/MST, les SVI, VRF et ACL impliquées.
- [ ] Vérifier les dépendances DHCP, DAI, IPSG, PVLAN et les adresses statiques.
- [ ] Définir le test de succès et les seuils qui déclenchent un retour arrière.

### Pendant le changement

- [ ] Appliquer une seule famille de changements par étape autant que possible.
- [ ] Comparer immédiatement l'état observé à l'état attendu.
- [ ] Ne pas faire confiance au seul retour « commande acceptée ».
- [ ] Tester d'abord les services témoins et les VLAN directement concernés.
- [ ] Arrêter le déploiement si un résultat diffère du plan.

### Après le changement

- [ ] Vérifier les VLAN et les trunks, les états STP/MST et les interfaces L3.
- [ ] Confirmer les politiques et compteurs ACL, les bindings et les journaux de sécurité pertinents.
- [ ] Tester les flux autorisés et les flux qui doivent rester bloqués.
- [ ] Conserver les sorties et mettre à jour le registre d'architecture.
- [ ] En cas de retour arrière, confirmer le rétablissement des services avant de clôturer l'incident.


## 15. Points à retenir

- Un VLAN définit un domaine L2, pas une politique complète d'accès entre les services.
- Les PVLAN peuvent isoler des hôtes d'un même sous-réseau au niveau L2 lorsque la plateforme prend cette fonction en charge.
- Une RACL ne voit pas forcément un flux commuté localement entre deux hôtes d'un même VLAN ; le point de contrôle doit être choisi à partir du chemin réel.
- DTP explicite, VLAN natif non utilisé, listes de VLAN autorisés minimales et désactivation de la négociation sur les ports terminaux compatibles réduisent certaines surfaces d'attaque L2.
- DHCP Snooping, DAI et IP Source Guard dépendent d'une classification fiable des ports et de bindings cohérents ; une activation non préparée peut perturber des hôtes légitimes.
- MST réduit le nombre d'instances nécessaires dans certains designs, mais le nom, la révision et le mapping de région doivent être cohérents.
- Les VLAN, les ACL, les VRF, les trunks et STP forment un système interdépendant : tout changement de segmentation doit avoir un plan de test et de retour arrière.

## Références techniques

Les exemples sont pédagogiques. La documentation du modèle et de la version du commutateur utilisé reste la référence pour les restrictions, la syntaxe et les comportements opérationnels.

- Cisco, *VLAN Configuration Guide — Catalyst 9000 Series* (VLAN, trunking, voix et Private VLAN) : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide.html
- Cisco, *Configure Private VLAN on Catalyst Switches* : https://www.cisco.com/c/en/us/support/docs/lan-switching/private-vlans-pvlans-promiscuous-isolated-community/40781-194.html
- Cisco, *Access Control Lists — Cisco IOS XE 17* (dont les VLAN ACL/VLAN maps) : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/security/acls/acls-configuration-guide/access-control-lists.html
- Cisco, *Troubleshoot MST on Catalyst 9000 Switches* : https://www.cisco.com/c/en/us/support/docs/lan-switching/stp/218351-troubleshoot-mst-on-catalyst-9000-switch.html
- Cisco, *Operate and Troubleshoot DHCP Snooping on Catalyst 9000* : https://www.cisco.com/c/en/us/support/docs/ip/dynamic-host-configuration-protocol-dhcp-dhcpv6/217055-operate-and-troubleshoot-dhcp-snooping.html
- Cisco, *Troubleshoot Dynamic ARP Inspection (DAI) and IP Source Guard* : https://www.cisco.com/c/en/us/support/docs/switches/lan-switch-software/222274-troubleshoot-dynamic-arp-inspection-dai.html
- IEEE, *IEEE 802.1Q — Bridges and Bridged Networks* : https://standards.ieee.org/standard/802_1Q-2022.html
