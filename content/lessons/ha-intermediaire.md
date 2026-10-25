# Haute disponibilité des réseaux — Niveau Intermédiaire

> **Schémas SVG intégrés :** les diagrammes sont inclus directement dans ce fichier Markdown. Aucun dossier d’images externe n’est nécessaire. Les animations suivent les connexions dessinées et restent illustratives : elles ne représentent pas un délai de convergence garanti sur tous les équipements.

## Positionnement dans le parcours

Ce cours prolonge `ha-debutant.md`. On considère désormais acquises les définitions de disponibilité, SLA, RTO/RPO, MTBF/MTTR, les principes de redondance et les premières notions de HSRP/VRRP, LACP et STP. Ici, l’objectif est de **concevoir, vérifier et dépanner** des mécanismes de haute disponibilité dans des topologies réalistes.

> **Fil conducteur :** une architecture redondante n’est réellement hautement disponible que si la panne est détectée, qu’un chemin alternatif est utilisable, que l’état nécessaire est conservé ou reconstruit, et que le service est vérifié de bout en bout.

## Objectifs pédagogiques

À la fin du cours, vous saurez :

- distinguer redondance physique, redondance logique et résilience applicative ;
- analyser HSRP/VRRP, suivi d’interface et suivi de route, sans confondre rôle actif et chemin réellement fonctionnel ;
- concevoir des EtherChannels LACP, des doubles attachements et des passerelles redondantes ;
- comprendre la contribution de STP/RSTP et les risques de boucles lors d’une modification ;
- construire un plan de tests de bascule mesurable ;
- interpréter les symptômes d’un split-brain, d’une asymétrie de routage ou d’une synchronisation d’état incomplète ;
- diagnostiquer une panne en séparant détection, convergence, transfert du trafic et rétablissement applicatif.

## Prérequis et règles de laboratoire

Prérequis : notions de VLAN/trunk, adressage IPv4/IPv6, routes, ARP/NDP, STP, EtherChannel et passerelle par défaut. Les commandes dépendent du modèle et de la version IOS/IOS XE ; vérifiez toujours l’aide locale et la documentation correspondant à l’équipement.

Tous les laboratoires doivent être exécutés dans Packet Tracer, un simulateur, ou une maquette isolée. **Ne provoquez jamais volontairement une panne sur un réseau de production sans autorisation, fenêtre de changement, sauvegarde et plan de retour arrière.**


## 1. Le modèle de disponibilité : quatre conditions nécessaires

Une architecture HA peut échouer même si elle possède deux équipements. Pour qu’une bascule soit utile, il faut au minimum :

1. **Détection** — le système identifie la défaillance pertinente.
2. **Décision** — un protocole ou une politique choisit le nouveau rôle ou chemin.
3. **Transfert** — le trafic peut réellement emprunter la solution de secours.
4. **Validation** — les utilisateurs et applications retrouvent le service.

### Schéma 1 — Chemin de bascule de bout en bout

<div class="lesson-figure ha-svg-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" role="img" aria-label="Cycle de bascule en quatre étapes, de la détection à la validation applicative" style="display:block;width:100%;max-width:960px;height:auto;margin:0 auto" xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="800" height="300" rx="16" fill="#10151f"/><text x="26" y="31" font-size="20" font-weight="700" fill="#edf3fa">Cycle de bascule de bout en bout</text><text x="26" y="53" font-size="12" fill="#a8b6c8">Détecter, converger et valider le service</text>
<g stroke="#344357" stroke-width="3" fill="none"><path d="M174 132 H218"/><path d="M366 132 H410"/><path d="M558 132 H602"/></g>
<g fill="#182231" stroke-width="2"><rect x="26" y="88" width="148" height="88" rx="12" stroke="#fb7185"/><rect x="218" y="88" width="148" height="88" rx="12" stroke="#fbbf24"/><rect x="410" y="88" width="148" height="88" rx="12" stroke="#43c7f5"/><rect x="602" y="88" width="172" height="88" rx="12" stroke="#4ade80"/></g>
<g fill="#edf3fa" font-size="15" font-weight="700" text-anchor="middle"><text x="100" y="119">1 · Panne</text><text x="292" y="119">2 · Détection</text><text x="484" y="119">3 · Décision</text><text x="688" y="119">4 · Validation</text></g>
<g fill="#a8b6c8" font-size="11" text-anchor="middle"><text x="100" y="141">Lien / route / service</text><text x="292" y="141">Tracking ou sonde</text><text x="484" y="141">Rôle / route modifiés</text><text x="688" y="141">Ping + transaction</text></g>
<g stroke="#43c7f5" stroke-width="3" fill="none"><path d="M174 132 H218"/><path d="M366 132 H410"/><path d="M558 132 H602"/></g>
<path d="M174 132 H218 H366 H410 H558 H602" fill="none" stroke="#4ade80" stroke-width="2" stroke-dasharray="4 8" opacity=".5"/>
<circle cx="174" cy="132" r="5.5" fill="#4ade80" stroke="#ffffff" stroke-width="1.5"><animateMotion dur="1.4s" repeatCount="indefinite" path="M0 0 h44"/></circle><circle cx="366" cy="132" r="5.5" fill="#4ade80" stroke="#ffffff" stroke-width="1.5"><animateMotion dur="1.4s" begin=".45s" repeatCount="indefinite" path="M0 0 h44"/></circle><circle cx="558" cy="132" r="5.5" fill="#4ade80" stroke="#ffffff" stroke-width="1.5"><animateMotion dur="1.4s" begin=".9s" repeatCount="indefinite" path="M0 0 h44"/></circle>
<rect x="90" y="215" width="620" height="52" rx="10" fill="#172b23" stroke="#2d6a4f"/><text x="400" y="237" text-anchor="middle" font-size="14" font-weight="700" fill="#4ade80">Critère de réussite : le service répond depuis le point utilisateur</text><text x="400" y="254" text-anchor="middle" font-size="11" fill="#c7d8ce">Mesurer aussi la perte de paquets et les sessions interrompues</text>
</svg>
</div>

L’animation illustre deux chemins possibles. Elle ne signifie pas que les deux chemins sont nécessairement actifs simultanément : cela dépend de la technologie, de la configuration et de la topologie. Le point essentiel est de tester la panne qui compte réellement. Une interface peut être `up/up` alors que la route distante, le DNS, le serveur ou l’application ne répond plus.

### 1.1 Les métriques à relever

| Mesure | Définition opérationnelle | Comment la mesurer |
|---|---|---|
| Temps de détection | Temps entre la panne et sa détection | Logs, protocole de voisinage, sondes |
| Temps de décision | Temps entre la détection et le choix du secours | Événements HSRP/VRRP, routage |
| Temps de convergence | Temps jusqu’à la disponibilité du chemin alternatif | Ping continu, capture, table de routage |
| Perte de paquets | Paquets perdus pendant la transition | Ping horodaté, supervision |
| Récupération applicative | Temps jusqu’au retour de la transaction métier | Test HTTP/API/connexion |
| Impact session | Sessions TCP/UDP interrompues ou conservées | Logs applicatifs, captures, tests réels |

Il faut séparer le temps réseau du temps applicatif. Une passerelle peut basculer en quelques secondes tandis qu’une session existante est réinitialisée par un pare-feu qui n’a pas synchronisé son état.

### 1.2 Exemple de budget de bascule

Supposons un objectif interne de rétablissement inférieur à 5 secondes. Un test mesuré donne :

- détection : 1,2 s ;
- décision du protocole : 0,8 s ;
- mise à jour des tables/chemins : 0,9 s ;
- reprise de l’application : 1,5 s.

Total observé : 4,4 s. Cela ne prouve pas à lui seul le respect de l’objectif. Répétez les tests, testez différents types de panne, mesurez les percentiles et consignez les pertes. Une moyenne favorable peut masquer un cas rare de 12 secondes.


## 2. Passerelles redondantes : HSRP et VRRP

HSRP (Hot Standby Router Protocol) est associé à Cisco ; VRRP est un protocole standardisé. Les deux permettent aux hôtes d’utiliser une passerelle logique commune alors que plusieurs routeurs ou commutateurs de couche 3 peuvent assurer le service. Les détails de version, de préemption, de suivi et d’authentification varient selon la plateforme.

### Schéma 2 — Rôle actif, secours et passerelle virtuelle

<div class="lesson-figure ha-svg-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 330" role="img" aria-label="Passerelle virtuelle HSRP ou VRRP avec routeur actif et routeur de secours" style="display:block;width:100%;max-width:960px;height:auto;margin:0 auto">
<rect width="800" height="330" rx="16" fill="#10151f"/><text x="26" y="30" font-size="20" font-weight="700" fill="#edf3fa">Passerelle redondante : HSRP / VRRP</text><text x="26" y="52" font-size="12" fill="#a8b6c8">Les hôtes utilisent l’adresse virtuelle, pas l’adresse physique d’un routeur</text>
<g fill="#182231" stroke-width="2"><rect x="28" y="122" width="142" height="82" rx="12" stroke="#c4b5fd"/><rect x="258" y="80" width="174" height="82" rx="12" stroke="#4ade80"/><rect x="258" y="218" width="174" height="82" rx="12" stroke="#fbbf24"/><rect x="592" y="122" width="180" height="82" rx="12" stroke="#43c7f5"/></g>
<g fill="#edf3fa" font-weight="700" font-size="15" text-anchor="middle"><text x="99" y="151">Hôtes</text><text x="99" y="172" font-size="12" font-weight="400" fill="#a8b6c8">GW virtuelle</text><text x="345" y="110">R1 · ACTIF</text><text x="345" y="132" font-size="12" font-weight="400" fill="#a8b6c8">Priorité supérieure</text><text x="345" y="249">R2 · SECOURS</text><text x="345" y="271" font-size="12" font-weight="400" fill="#a8b6c8">Prêt à prendre le rôle</text><text x="682" y="151">Réseau amont</text><text x="682" y="172" font-size="12" font-weight="400" fill="#a8b6c8">Route / services</text></g>
<g fill="none" stroke-width="4" stroke-linecap="round"><path d="M170 149 H214 V121 H258" stroke="#4ade80"/><path d="M170 177 H214 V259 H258" stroke="#fbbf24" stroke-dasharray="7 7"/><path d="M432 121 H500 V149 H592" stroke="#4ade80"/><path d="M432 259 H520 V177 H592" stroke="#fbbf24" stroke-dasharray="7 7"/></g>
<circle cx="170" cy="149" r="5.5" fill="#4ade80" stroke="#fff" stroke-width="1.5"><animateMotion dur="1.8s" repeatCount="indefinite" path="M0 0 h44 v-28 h44"/></circle><circle cx="432" cy="121" r="5.5" fill="#4ade80" stroke="#fff" stroke-width="1.5"><animateMotion dur="1.8s" begin=".65s" repeatCount="indefinite" path="M0 0 h68 v28 h92"/></circle><circle cx="170" cy="177" r="5" fill="#fbbf24" stroke="#fff" stroke-width="1.2"><animateMotion dur="2.6s" repeatCount="indefinite" path="M0 0 h44 v82 h44"/></circle><circle cx="432" cy="259" r="5" fill="#fbbf24" stroke="#fff" stroke-width="1.2"><animateMotion dur="2.6s" begin="1.1s" repeatCount="indefinite" path="M0 0 h88 v-82 h72"/></circle>
<g font-size="11" fill="#a8b6c8"><text x="184" y="106">Trafic actif</text><text x="185" y="205">Chemin secours</text></g><rect x="270" y="174" width="150" height="30" rx="8" fill="#133029" stroke="#2d6a4f"/><text x="345" y="193" text-anchor="middle" font-size="12" font-weight="700" fill="#4ade80">IP virtuelle commune</text>
</svg>
</div>

Les hôtes configurent l’adresse IP virtuelle comme passerelle. Ils ne doivent pas dépendre de l’adresse physique d’un seul équipement. Le protocole élit un routeur qui répond pour le groupe ; l’équipement de secours peut prendre le rôle si les conditions configurées le justifient.

### 2.1 Les états à distinguer

Pour analyser une passerelle redondante, séparez les éléments suivants :

- **Rôle de contrôle :** actif/standby (HSRP) ou master/backup (terminologie VRRP courante).
- **Priorité :** influence l’élection, selon les règles du protocole.
- **Préemption :** détermine si un équipement de priorité supérieure peut reprendre le rôle après son retour.
- **Suivi (tracking) :** peut réduire la priorité lorsqu’une interface, une route ou une sonde devient indisponible.
- **Plan de données :** le trafic passe-t-il vraiment par le routeur qui possède le rôle ?
- **État des hôtes :** la résolution de passerelle et les caches sont-ils mis à jour correctement ?

Un routeur peut être actif pour le groupe tout en ayant perdu un chemin vers l’amont. Sans suivi adapté, les hôtes continuent d’envoyer leur trafic à une passerelle qui ne peut plus le livrer.

### 2.2 Configuration de laboratoire Cisco IOS : HSRP

Exemple illustratif pour un VLAN 10, à adapter à la plateforme. Les adresses d’interface doivent être uniques et appartenir au même sous-réseau.

Sur R1 :

```text
interface GigabitEthernet0/0
 description Vers VLAN 10
 ip address 192.0.2.2 255.255.255.0
 standby 10 ip 192.0.2.1
 standby 10 priority 110
 standby 10 preempt
 standby 10 track GigabitEthernet0/1 20
```

Sur R2 :

```text
interface GigabitEthernet0/0
 description Vers VLAN 10
 ip address 192.0.2.3 255.255.255.0
 standby 10 ip 192.0.2.1
 standby 10 priority 100
 standby 10 preempt
```

`192.0.2.0/24` est réservé à la documentation ; remplacez-le par le plan d’adressage du laboratoire. Le suivi présenté illustre le principe : confirmez la syntaxe et le comportement exacts sur l’image IOS utilisée. Selon la configuration, il peut être nécessaire de suivre une route amont plutôt qu’une interface seulement.

Commandes de vérification usuelles :

```text
show standby brief
show standby
show ip interface brief
show ip route
show track
```

Si `show track` n’est pas disponible dans cette version, utilisez les commandes de suivi prises en charge par la plateforme. Vérifiez également les journaux et testez le chemin depuis un hôte, pas uniquement l’état du protocole.

### 2.3 Suivre une interface ou suivre une route ?

Le suivi d’interface détecte la perte d’un lien local, mais il ne détecte pas nécessairement une panne plus loin dans le réseau. Une interface peut rester opérationnelle alors que l’amont est isolé. Le suivi de route ou une sonde IP SLA peut mesurer un état plus proche de la connectivité utile, à condition que la sonde soit correctement conçue et que sa destination ne soit pas accessible par un chemin qui masque la panne recherchée.

**Bonnes pratiques :**

- surveiller une cible représentative, pas uniquement le voisin directement connecté ;
- éviter qu’une sonde partage exactement le même défaut que le service testé ;
- prévoir l’hystérésis ou les délais adaptés pour limiter les bascules répétitives ;
- tester la perte d’un lien, la perte de route et la perte de service séparément ;
- documenter le comportement au retour du routeur préféré.

### 2.4 Préemption : utile mais à contrôler

La préemption peut faire reprendre le rôle actif au routeur prioritaire après son retour. Cela peut restaurer le chemin préféré, mais aussi provoquer une seconde interruption. Dans un réseau sensible, le choix doit être explicite : retour automatique, retour manuel après vérification, ou temporisation. Une priorité supérieure ne garantit pas à elle seule que l’équipement est prêt à transporter le trafic applicatif.


## 3. Redondance des liens : EtherChannel et LACP

EtherChannel agrège plusieurs liens Ethernet en une interface logique. LACP négocie la formation du groupe entre équipements compatibles. Un lien membre peut tomber sans nécessairement interrompre le port-channel, si les autres membres restent opérationnels et que la capacité résiduelle suffit.

### Schéma 3 — LACP : plusieurs liens, un port logique

<div class="lesson-figure ha-svg-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" role="img" aria-label="Deux liens physiques agrégés par LACP dans un port-channel entre deux commutateurs" style="display:block;width:100%;max-width:960px;height:auto;margin:0 auto">
<rect width="800" height="300" rx="16" fill="#10151f"/><text x="26" y="30" font-size="20" font-weight="700" fill="#edf3fa">LACP : deux liens physiques, un lien logique</text><text x="26" y="52" font-size="12" fill="#a8b6c8">Le port-channel reste opérationnel si le nombre de membres actifs suffit</text>
<g fill="#182231" stroke="#43c7f5" stroke-width="2"><rect x="34" y="100" width="180" height="108" rx="14"/><rect x="586" y="100" width="180" height="108" rx="14"/></g>
<g fill="#edf3fa" text-anchor="middle"><text x="124" y="137" font-size="18" font-weight="700">SW-A</text><text x="124" y="162" font-size="12" fill="#a8b6c8">Port-channel 1</text><text x="676" y="137" font-size="18" font-weight="700">SW-B</text><text x="676" y="162" font-size="12" fill="#a8b6c8">Port-channel 1</text></g>
<path d="M214 127 H586" fill="none" stroke="#4ade80" stroke-width="5"/><path d="M214 178 H586" fill="none" stroke="#fbbf24" stroke-width="5"/>
<circle cx="214" cy="127" r="6" fill="#4ade80" stroke="#fff" stroke-width="1.3"><animateMotion dur="3.7s" repeatCount="indefinite" path="M0 0 h372"/></circle><circle cx="586" cy="178" r="6" fill="#fbbf24" stroke="#fff" stroke-width="1.3"><animateMotion dur="4.4s" repeatCount="indefinite" path="M0 0 h-372"/></circle>
<text x="400" y="112" text-anchor="middle" font-size="12" font-weight="700" fill="#4ade80">Gi1/0/1 · membre A</text><text x="400" y="201" text-anchor="middle" font-size="12" font-weight="700" fill="#fbbf24">Gi1/0/2 · membre B</text>
<rect x="243" y="231" width="314" height="43" rx="10" fill="#182231" stroke="#344357"/><text x="400" y="249" text-anchor="middle" font-size="13" font-weight="700" fill="#edf3fa">LACP : active/active ou active/passive</text><text x="400" y="265" text-anchor="middle" font-size="11" fill="#a8b6c8">Un flux unique n’utilise pas forcément les deux membres</text>
</svg>
</div>

L’agrégation ne signifie pas que chaque paquet est réparti indépendamment sur tous les liens. Le mécanisme de hachage sélectionne généralement un membre selon des champs de flux. Une seule conversation peut rester sur un membre ; le débit agrégé théorique n’est donc pas forcément disponible à un flux unique.

### 3.1 Exemple Cisco IOS

Exemple conceptuel pour deux liens entre SW-A et SW-B :

```text
interface range GigabitEthernet1/0/1-2
 switchport
 channel-group 1 mode active
 no shutdown

interface Port-channel1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown
```

Reproduisez une configuration compatible aux deux extrémités. Le mode `active` envoie des paquets LACP ; `passive` répond aux négociations, mais deux extrémités passives ne démarrent normalement pas la négociation. Les commandes exactes dépendent du modèle et du système.

Vérification :

```text
show etherchannel summary
show interfaces port-channel 1
show lacp neighbor
show interfaces trunk
```

### 3.2 Causes courantes d’un port-channel instable

- vitesse, duplex ou paramètres physiques incompatibles ;
- mode access/trunk différent ;
- VLAN natif ou liste de VLAN autorisés incohérents ;
- configuration appliquée au port physique d’un côté et au port logique de l’autre ;
- membres raccordés à des équipements qui ne forment pas une paire multi-châssis prise en charge ;
- erreur physique, optique, MTU ou câblage ;
- mode LACP incompatible.

Ne corrigez pas un EtherChannel en supprimant au hasard les interfaces du groupe. Comparez d’abord la configuration des deux côtés, sauvegardez l’état et modifiez un paramètre à la fois.

### 3.3 Capacité résiduelle

Si un port-channel de quatre liens à 1 Gbit/s perd un membre, il reste au maximum trois liens de 1 Gbit/s avant surcharges et contraintes. Vérifiez aussi les limites de hachage, la distribution réelle des flux, la capacité des équipements et le risque de congestion pendant une panne.


## 4. STP/RSTP : redondance sans boucle de couche 2

Les liens redondants entre commutateurs peuvent créer une boucle Ethernet. STP/RSTP maintient une topologie logique sans boucle, en laissant certains chemins bloqués ou alternatifs selon le protocole. La redondance physique ne signifie donc pas que tous les liens transmettent simultanément le trafic utilisateur.

### Schéma 4 — Deux chemins physiques, un chemin bloqué par STP

<div class="lesson-figure ha-svg-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 330" role="img" aria-label="Triangle de trois commutateurs avec deux chemins de transfert et un lien redondant bloqué par STP" style="display:block;width:100%;max-width:960px;height:auto;margin:0 auto">
<rect width="800" height="330" rx="16" fill="#10151f"/><text x="26" y="30" font-size="20" font-weight="700" fill="#edf3fa">STP : conserver la redondance sans boucle</text><text x="26" y="52" font-size="12" fill="#a8b6c8">La topologie physique peut être un triangle ; la topologie de transfert doit rester sans boucle</text>
<g fill="#182231" stroke-width="2"><rect x="302" y="78" width="196" height="72" rx="12" stroke="#4ade80"/><rect x="88" y="218" width="196" height="72" rx="12" stroke="#43c7f5"/><rect x="516" y="218" width="196" height="72" rx="12" stroke="#43c7f5"/></g>
<g fill="#edf3fa" text-anchor="middle"><text x="400" y="106" font-size="16" font-weight="700">SW-CORE</text><text x="400" y="128" font-size="12" fill="#4ade80">Root Bridge</text><text x="186" y="246" font-size="16" font-weight="700">SW-1</text><text x="186" y="268" font-size="12" fill="#a8b6c8">Root Port vers CORE</text><text x="614" y="246" font-size="16" font-weight="700">SW-2</text><text x="614" y="268" font-size="12" fill="#a8b6c8">Root Port vers CORE</text></g>
<path d="M333 150 L245 218" fill="none" stroke="#4ade80" stroke-width="5"/><path d="M467 150 L555 218" fill="none" stroke="#4ade80" stroke-width="5"/><path d="M284 254 H516" fill="none" stroke="#fb7185" stroke-width="4" stroke-dasharray="8 7"/>
<circle cx="333" cy="150" r="6" fill="#4ade80" stroke="#fff" stroke-width="1.2"><animateMotion dur="2.2s" repeatCount="indefinite" path="M0 0 l-88 68"/></circle><circle cx="467" cy="150" r="6" fill="#4ade80" stroke="#fff" stroke-width="1.2"><animateMotion dur="2.2s" begin="1.1s" repeatCount="indefinite" path="M0 0 l88 68"/></circle>
<circle cx="400" cy="254" r="15" fill="#351c26" stroke="#fb7185" stroke-width="2"/><path d="M392 246 L408 262 M408 246 L392 262" stroke="#fb7185" stroke-width="3"/><text x="400" y="305" text-anchor="middle" font-size="12" font-weight="700" fill="#fb7185">Lien redondant en état bloqué</text>
</svg>
</div>

Dans une conception multi-commutateurs, définissez clairement le pont racine attendu et vérifiez que les chemins de secours sont réellement disponibles. Une modification de priorité, l’ajout d’un commutateur ou un EtherChannel mal formé peut changer la topologie et entraîner une convergence inattendue.

Commandes utiles selon la plateforme :

```text
show spanning-tree
show spanning-tree root
show spanning-tree vlan 10
show interfaces trunk
show etherchannel summary
```

### 4.1 Protections à comprendre

- **PortFast** accélère l’entrée en transfert sur un port d’accès terminal ; ne l’activez pas à l’aveugle sur un lien entre commutateurs.
- **BPDU Guard** protège généralement un port PortFast contre la réception de BPDU, en plaçant le port dans un état de protection selon la plateforme.
- **Root Guard** empêche qu’un voisin fasse devenir un port désigné en chemin vers une racine non souhaitée.
- **Loop Guard** aide à prévenir certaines boucles lorsque des BPDU attendues cessent d’être reçues.
- **UDLD** peut détecter certaines défaillances unidirectionnelles sur les liaisons prises en charge.

Ces protections ne sont pas interchangeables. Choisissez-les selon le rôle du port, la topologie et le comportement attendu en cas de panne. Vérifiez les états `inconsistent`, les logs et les compteurs après toute modification.


## 5. Double attachement et chemins de secours

Deux liaisons physiques n’apportent pas automatiquement de la haute disponibilité. Si les deux passent dans le même conduit, le même module, la même alimentation ou le même fournisseur, une seule panne commune peut les interrompre simultanément.

### Schéma 5 — Deux chemins et plusieurs domaines de panne

<div class="lesson-figure ha-svg-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 330" role="img" aria-label="Chemin primaire et secondaire entre un hôte et le cœur réseau par deux switches distincts" style="display:block;width:100%;max-width:960px;height:auto;margin:0 auto">
<rect width="800" height="330" rx="16" fill="#10151f"/><text x="26" y="30" font-size="20" font-weight="700" fill="#edf3fa">Deux chemins : vérifier les domaines de panne</text><text x="26" y="52" font-size="12" fill="#a8b6c8">Deux liens ne protègent pas contre une dépendance commune non détectée</text>
<g fill="#182231" stroke-width="2"><rect x="32" y="125" width="148" height="78" rx="12" stroke="#c4b5fd"/><rect x="282" y="77" width="170" height="78" rx="12" stroke="#4ade80"/><rect x="282" y="220" width="170" height="78" rx="12" stroke="#fbbf24"/><rect x="620" y="125" width="148" height="78" rx="12" stroke="#43c7f5"/></g>
<g fill="#edf3fa" text-anchor="middle"><text x="106" y="153" font-size="16" font-weight="700">Client</text><text x="106" y="174" font-size="12" fill="#a8b6c8">VLAN / GW</text><text x="367" y="106" font-size="16" font-weight="700">SW-A</text><text x="367" y="127" font-size="12" fill="#4ade80">Chemin primaire</text><text x="367" y="249" font-size="16" font-weight="700">SW-B</text><text x="367" y="270" font-size="12" fill="#fbbf24">Chemin secondaire</text><text x="694" y="153" font-size="16" font-weight="700">Cœur réseau</text><text x="694" y="174" font-size="12" fill="#a8b6c8">Route / service</text></g>
<path d="M180 145 L230 145 L230 116 H282" fill="none" stroke="#4ade80" stroke-width="4"/><path d="M180 184 L230 184 L230 259 H282" fill="none" stroke="#fbbf24" stroke-width="4" stroke-dasharray="7 6"/><path d="M452 116 H535 L535 145 H620" fill="none" stroke="#4ade80" stroke-width="4"/><path d="M452 259 H565 L565 184 H620" fill="none" stroke="#fbbf24" stroke-width="4" stroke-dasharray="7 6"/>
<circle cx="180" cy="145" r="5.5" fill="#4ade80" stroke="#fff" stroke-width="1.2"><animateMotion dur="1.8s" repeatCount="indefinite" path="M0 0 h50 v-29 h52"/></circle><circle cx="452" cy="116" r="5.5" fill="#4ade80" stroke="#fff" stroke-width="1.2"><animateMotion dur="2.2s" begin=".6s" repeatCount="indefinite" path="M0 0 h83 v29 h85"/></circle><circle cx="180" cy="184" r="5" fill="#fbbf24" stroke="#fff" stroke-width="1.2"><animateMotion dur="2.4s" repeatCount="indefinite" path="M0 0 h50 v75 h52"/></circle><circle cx="452" cy="259" r="5" fill="#fbbf24" stroke="#fff" stroke-width="1.2"><animateMotion dur="2.8s" begin="1s" repeatCount="indefinite" path="M0 0 h113 v-75 h55"/></circle>
<rect x="230" y="177" width="330" height="25" rx="8" fill="#32202a" stroke="#fb7185"/><text x="395" y="194" text-anchor="middle" font-size="11" font-weight="700" fill="#fb7185">À vérifier : alimentation, rack, opérateur, cœur partagé</text>
</svg>
</div>

Lors de la revue d’architecture, dessinez les dépendances communes : alimentation, rack, carte, câble, conduit, site, fournisseur, DNS, authentification et système de gestion. La diversité physique et administrative compte autant que le nombre de liens.

### 5.1 Analyse des domaines de panne

Pour chaque composant, posez quatre questions :

1. Quelle panne peut-il subir ?
2. Quel mécanisme la détecte ?
3. Quelle ressource de secours reste réellement indépendante ?
4. Quel test prouve que le service continue ?

Un deuxième routeur connecté au même unique commutateur d’accès ne protège pas contre la panne de ce commutateur. Deux pare-feu sans synchronisation de session peuvent restaurer les nouvelles connexions sans préserver celles déjà établies. Deux liens vers le même opérateur ne protègent pas contre la panne de son réseau de collecte.


## 6. Haute disponibilité des pare-feu : plan de données et état

Un cluster de pare-feu peut utiliser un modèle actif/passif ou actif/actif selon le produit. Pour maintenir des connexions existantes, le secours doit disposer de l’état nécessaire : sessions, translations, associations ou autres informations selon la technologie. La synchronisation peut être partielle, asynchrone ou limitée à certains types d’état.

### Schéma 6 — Trafic et synchronisation d’état

<div class="lesson-figure ha-svg-figure">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 330" role="img" aria-label="Pare-feu actif et pare-feu de secours avec chemin de données et canal de synchronisation d'état" style="display:block;width:100%;max-width:960px;height:auto;margin:0 auto">
<rect width="800" height="330" rx="16" fill="#10151f"/><text x="26" y="30" font-size="20" font-weight="700" fill="#edf3fa">Cluster de pare-feu : trafic et état</text><text x="26" y="52" font-size="12" fill="#a8b6c8">La réplication d’état dépend du produit ; elle ne garantit pas toujours la survie des sessions</text>
<g fill="#182231" stroke-width="2"><rect x="30" y="117" width="138" height="78" rx="12" stroke="#c4b5fd"/><rect x="276" y="76" width="178" height="78" rx="12" stroke="#4ade80"/><rect x="276" y="220" width="178" height="78" rx="12" stroke="#fbbf24"/><rect x="624" y="117" width="145" height="78" rx="12" stroke="#43c7f5"/></g>
<g fill="#edf3fa" text-anchor="middle"><text x="99" y="146" font-size="16" font-weight="700">WAN</text><text x="99" y="167" font-size="12" fill="#a8b6c8">Entrée</text><text x="365" y="105" font-size="16" font-weight="700">FW-A · ACTIF</text><text x="365" y="127" font-size="12" fill="#4ade80">Transfert du trafic</text><text x="365" y="249" font-size="16" font-weight="700">FW-B · SECOURS</text><text x="365" y="271" font-size="12" fill="#fbbf24">Prend le rôle après bascule</text><text x="696" y="146" font-size="16" font-weight="700">LAN</text><text x="696" y="167" font-size="12" fill="#a8b6c8">Destination</text></g>
<path d="M168 145 H220 L220 115 H276" fill="none" stroke="#4ade80" stroke-width="4"/><path d="M454 115 H535 L535 145 H624" fill="none" stroke="#4ade80" stroke-width="4"/><path d="M365 154 V220" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-dasharray="5 5"/><path d="M365 220 V154" fill="none" stroke="#c4b5fd" stroke-width="3" stroke-dasharray="5 5"/>
<circle cx="168" cy="145" r="5.5" fill="#4ade80" stroke="#fff" stroke-width="1.2"><animateMotion dur="1.8s" repeatCount="indefinite" path="M0 0 h52 v-30 h56"/></circle><circle cx="454" cy="115" r="5.5" fill="#4ade80" stroke="#fff" stroke-width="1.2"><animateMotion dur="2.1s" begin=".65s" repeatCount="indefinite" path="M0 0 h81 v30 h89"/></circle><circle cx="365" cy="154" r="5" fill="#c4b5fd" stroke="#fff" stroke-width="1.2"><animateMotion dur="2.4s" repeatCount="indefinite" path="M0 0 v66"/></circle>
<text x="386" y="188" font-size="11" fill="#c4b5fd">Sync. états</text><rect x="491" y="230" width="286" height="54" rx="9" fill="#182231" stroke="#344357"/><text x="634" y="250" text-anchor="middle" font-size="12" font-weight="700" fill="#edf3fa">Après la bascule, tester :</text><text x="634" y="268" text-anchor="middle" font-size="11" fill="#a8b6c8">nouvelles sessions + sessions existantes</text>
</svg>
</div>

La ligne de synchronisation représente un canal logique, pas une garantie que chaque session est répliquée sans délai. La capacité, la latence et les règles de filtrage de ce canal peuvent influencer le comportement en bascule. Consultez la documentation du fabricant pour savoir quels états sont répliqués et dans quelles conditions.

### 6.1 Symptômes après bascule

- les nouvelles connexions fonctionnent, les anciennes échouent ;
- certaines applications fonctionnent, d’autres réinitialisent les sessions ;
- les flux sortants fonctionnent mais les réponses ne reviennent pas par le même chemin ;
- la synchronisation affiche un état dégradé ;
- les adresses MAC ou IP virtuelles ne sont pas annoncées comme attendu ;
- le secours devient actif mais ne dispose pas d’une route ou d’une licence nécessaire.

Ne concluez pas « le cluster fonctionne » sur le seul état `active/standby`. Vérifiez une transaction réelle à travers le cluster, dans les deux sens, puis répétez après une panne contrôlée.


## 7. Split-brain et asymétrie : quand deux côtés se croient actifs

Le split-brain est une situation où des membres qui devraient se coordonner perdent leur communication de contrôle et prennent des décisions incompatibles. Les effets dépendent du produit : adresses dupliquées, annonces contradictoires, écritures concurrentes ou interruption de service.

L’asymétrie de routage est différente : les paquets aller et retour empruntent des chemins différents. Elle peut être valide, mais devient problématique si un pare-feu stateful ou un mécanisme de NAT attend que les deux directions passent par le même état logique.

### Tableau de distinction

| Symptôme | Hypothèse | Vérification |
|---|---|---|
| Deux nœuds se déclarent actifs | Split-brain ou perte de heartbeat | Journaux de cluster, lien de contrôle, quorum |
| SYN sort, réponse absente | Route retour ou filtrage | Capture aux deux côtés, tables de routage |
| Nouvelles sessions OK, sessions établies perdues | État non synchronisé ou non compatible | Table de sessions avant/après |
| Bascule répétée toutes les quelques secondes | Tracking instable, sonde trop sensible | Logs horodatés, seuils, perte intermittente |
| Lien UP, service inaccessible | Panne au-delà du lien ou de l’application | Sonde de bout en bout, traceroute, DNS |

### Procédure de diagnostic sûre

1. Collecter l’heure exacte et le périmètre des utilisateurs affectés.
2. Lire l’état des membres et les journaux sans modifier la configuration.
3. Vérifier le réseau de contrôle/heartbeat et le chemin de données.
4. Identifier les routes aller et retour.
5. Comparer les tables d’état et les annonces d’adresses.
6. Appliquer le runbook du fabricant ; ne forcez pas arbitrairement les deux nœuds en actif.
7. Valider les nouvelles connexions et les sessions existantes après rétablissement.


## 8. Planifier un test de bascule reproductible

Un test valable comporte un état initial connu, une panne précisément définie, des mesures, des critères de réussite et un plan d’arrêt. Une capture d’écran « tout est vert » ne suffit pas.

### Modèle de fiche de test

| Champ | Exemple |
|---|---|
| Identifiant | HA-GW-03 |
| État initial | R1 actif, R2 en secours |
| Panne injectée | Déconnexion de l’interface amont de R1 |
| Hypothèse | Le tracking réduit la priorité de R1 |
| Mesure réseau | Ping continu horodaté depuis un client |
| Mesure applicative | Requête HTTP périodique vers un serveur de test |
| Critère de réussite | Service rétabli en moins de 5 s, sans boucle |
| Arrêt d’urgence | Retour immédiat au câblage initial si la maquette devient instable |
| Preuves | Logs, sortie des commandes, capture PCAP, chronologie |

### Méthode de test

1. Enregistrez la topologie, les versions, les configurations et l’état de référence.
2. Démarrez des sondes continues depuis un point utilisateur.
3. Marquez l’instant de la panne.
4. Collectez les événements du protocole et les changements de route.
5. Mesurez perte de paquets, temps de convergence et reprise applicative.
6. Répétez plusieurs fois et testez différents défauts.
7. Vérifiez le retour à l’état normal et la stabilité après restauration.
8. Documentez les limites : flux existants, IPv4/IPv6, DNS, authentification et supervision.


## 9. Laboratoires guidés

### Laboratoire 1 — HSRP et suivi du chemin amont

**But :** observer le changement de rôle lorsque le chemin préféré devient indisponible.

**Topologie :** deux routeurs L3 connectés au même VLAN utilisateur, chacun avec une liaison vers un réseau amont de test. Un client utilise l’adresse virtuelle comme passerelle.

**Étapes :**

1. Configurez des adresses physiques uniques et la même adresse virtuelle de groupe.
2. Attribuez une priorité supérieure à R1.
3. Vérifiez le rôle actif et le secours.
4. Lancez un ping continu et une requête vers le serveur de test.
5. Désactivez uniquement l’interface amont de R1.
6. Comparez le comportement avec et sans tracking.
7. Restaurez l’interface et observez le comportement de préemption.

**Livrables :** configuration, sorties `show standby`, chronologie, perte de paquets, conclusion sur la meilleure sonde.

**Critères :** aucune adresse dupliquée ; rôle actif connu ; service vérifié depuis le client ; retour arrière réussi.

### Laboratoire 2 — LACP et perte d’un membre

**But :** distinguer perte d’un lien membre et perte complète du port-channel.

1. Créez un port-channel avec deux membres compatibles.
2. Vérifiez `show etherchannel summary`.
3. Mesurez le trafic de test.
4. Désactivez un membre et observez l’état du bundle.
5. Restaurez-le, puis testez une incompatibilité contrôlée dans la maquette.
6. Corrigez et consignez les symptômes.

**À expliquer :** pourquoi un seul flux ne double pas forcément son débit avec deux liens, et pourquoi le maintien du bundle ne garantit pas une capacité suffisante.

### Laboratoire 3 — STP et lien redondant

**But :** vérifier que la redondance ne crée pas de boucle.

1. Reliez trois commutateurs en triangle.
2. Relevez le root bridge et les rôles/états de ports.
3. Lancez un ping entre deux hôtes.
4. Coupez un lien de transfert.
5. Mesurez la convergence et inspectez les changements de topologie.
6. Restaurez le lien et observez le chemin retenu.

Ne désactivez pas STP sur une topologie de commutateurs interconnectés pour « faire passer tous les liens ». La boucle peut provoquer une tempête de diffusion.

### Laboratoire 4 — Pare-feu et sessions existantes

À réaliser uniquement sur une maquette qui prend en charge le clustering.

1. Créez une session longue et de nouvelles sessions périodiques.
2. Vérifiez l’état de synchronisation.
3. Déclenchez une bascule selon la procédure du constructeur.
4. Mesurez quelles sessions survivent et lesquelles se réinitialisent.
5. Comparez les résultats à la documentation du produit.
6. Restaurez l’état initial et validez le chemin retour.

Le but n’est pas d’imposer qu’aucune session ne tombe, mais de mesurer le comportement réel et de vérifier qu’il respecte les exigences du service.

### Laboratoire 5 — Diagnostic d’asymétrie

1. Dessinez les chemins aller et retour.
2. Lancez une connexion TCP de test.
3. Capturez les paquets sur les deux côtés du pare-feu.
4. Comparez les adresses, ports, séquences et interfaces.
5. Vérifiez les routes et la présence de la session dans la table du pare-feu.
6. Formulez une hypothèse puis changez un seul élément à la fois.

### Laboratoire 6 — Campagne de bascule

Construisez une matrice de tests avec au moins cinq défauts : perte d’un membre LACP, perte d’une liaison montante, panne du routeur actif, perte du canal de synchronisation et indisponibilité d’un service amont. Pour chaque test, consignez détection, décision, convergence, perte de paquets, reprise applicative et retour arrière.


## 10. Runbook d’intervention

### Avant changement

- [ ] Autorisation et fenêtre validées.
- [ ] Topologie et dépendances documentées.
- [ ] Sauvegardes des configurations et versions collectées.
- [ ] État initial des protocoles enregistré.
- [ ] Tests applicatifs et réseau opérationnels.
- [ ] Plan de retour arrière défini et testé en maquette.
- [ ] Personnes responsables et critères d’arrêt identifiés.

### Pendant le changement

- [ ] Une seule variable majeure modifiée à la fois.
- [ ] Événements horodatés.
- [ ] Rôles, routes et interfaces vérifiés après chaque étape.
- [ ] Aucun split-brain, aucune boucle ni duplication d’adresse observée.
- [ ] Test applicatif effectué depuis le point utilisateur.

### Après changement

- [ ] Les chemins principaux et de secours ont été testés.
- [ ] La capacité restante est suffisante.
- [ ] Les alertes sont revenues à un niveau normal.
- [ ] Les configurations et le diagramme sont à jour.
- [ ] Les résultats et limites sont documentés.


## 11. Évaluation avec corrigés

### Questions

1. Pourquoi deux routeurs ne garantissent-ils pas à eux seuls la haute disponibilité ?
2. Quelle différence existe entre suivre une interface locale et suivre une route distante ?
3. Pourquoi la préemption peut-elle provoquer une deuxième interruption ?
4. Que signifie le fait qu’un EtherChannel reste actif après la perte d’un membre ?
5. Pourquoi le débit d’un seul flux peut-il rester proche de celui d’un seul lien physique ?
6. Pourquoi STP peut-il bloquer un lien tout en conservant une redondance utile ?
7. Que faut-il vérifier au-delà de l’état `active/standby` d’un cluster de pare-feu ?
8. Qu’est-ce qu’un split-brain et pourquoi est-il dangereux ?
9. Une interface est `up/up`, mais l’application est inaccessible : quelles couches vérifier ?
10. Pourquoi mesurer séparément convergence réseau et reprise applicative ?
11. Quelles informations doit contenir une fiche de test de bascule ?
12. Pourquoi une architecture à deux liens sur le même conduit peut-elle rester vulnérable ?

### Corrigés expliqués

**1.** Les deux routeurs peuvent partager un défaut commun, ne pas détecter la panne pertinente, manquer de route de secours ou ne pas préserver l’état des sessions. Il faut analyser les domaines de panne et tester le service de bout en bout.

**2.** Le suivi d’interface observe l’état local du lien ; le suivi de route ou une sonde peut détecter une perte de connectivité plus loin. Une sonde mal choisie peut toutefois masquer la panne.

**3.** Au retour du routeur prioritaire, le rôle actif peut changer de nouveau. Ce second changement peut perturber les flux. Le retour automatique doit être évalué et mesuré.

**4.** Le bundle a conservé suffisamment de membres pour rester opérationnel. Cela ne garantit ni la capacité initiale, ni l’absence de congestion, ni la disponibilité de l’équipement distant.

**5.** Le hachage associe généralement un flux à un membre. L’agrégation augmente la capacité globale de plusieurs flux, mais ne multiplie pas nécessairement le débit d’une seule conversation.

**6.** STP empêche les boucles de couche 2 en construisant une topologie logique sans boucle. Un chemin alternatif peut être réactivé si un chemin de transfert échoue.

**7.** Le chemin de données, les routes, la synchronisation d’état, les adresses virtuelles, les sessions existantes et une transaction applicative réelle.

**8.** Des membres supposés coordonnés agissent simultanément comme actifs après une perte de communication de contrôle. Cela peut créer des annonces contradictoires, des adresses dupliquées ou des états divergents.

**9.** Vérifier VLAN/trunk, STP, LACP, ARP/NDP, routes aller et retour, ACL/pare-feu, DNS, MTU, puis l’application. Tester par étapes évite d’accuser le mauvais composant.

**10.** Le réseau peut avoir convergé alors que les sessions applicatives sont perdues, le DNS en cache, l’authentification indisponible ou le serveur encore défaillant.

**11.** État initial, panne injectée, hypothèse, mesures, critères de réussite, durée, preuves, responsable, arrêt d’urgence et retour arrière.

**12.** Un incident physique commun peut couper les deux liens. La diversité des chemins et des équipements est nécessaire pour réduire les défaillances corrélées.


## 12. Glossaire

- **Bascule (failover)** : transfert du rôle ou du trafic vers un composant de secours.
- **Convergence** : temps nécessaire pour que les protocoles et tables retrouvent un état utilisable.
- **Domaine de panne** : ensemble de composants affectés par une même cause.
- **Tracking** : suivi d’un état pour influencer une décision de disponibilité.
- **Préemption** : capacité d’un nœud prioritaire à reprendre un rôle après son retour.
- **Port-channel** : interface logique regroupant plusieurs liens physiques.
- **Split-brain** : situation où plusieurs membres prennent des décisions incompatibles en se croyant actifs.
- **Asymétrie de routage** : chemins aller et retour différents.
- **État de session** : informations nécessaires au suivi d’une connexion par un équipement stateful.
- **RTO** : durée maximale cible pour rétablir un service.
- **RPO** : perte de données maximale acceptable, exprimée en temps ou en quantité selon le contexte.
- **Sonde de bout en bout** : test qui valide une fonction utile depuis un point client jusqu’à la destination.

## Pour aller plus loin

Le niveau Expert approfondira la conception multi-sites, les dépendances corrélées, les architectures de clusters, les mécanismes de quorum, l’automatisation des tests et l’analyse des incidents complexes. Il réutilisera les notions de ce cours sans reprendre les configurations de base en détail.

### Références recommandées

- Documentation Cisco IOS/IOS XE correspondant à la version utilisée : HSRP, EtherChannel/LACP, STP/RSTP et mécanismes de suivi.
- RFC 5798 pour VRRP version 3 (IPv4 et IPv6).
- Documentation du constructeur pour la synchronisation d’état et les procédures de cluster de pare-feu.
- Documentation d’exploitation des outils de supervision et de capture utilisés dans le laboratoire.

> **Règle finale :** une bascule n’est validée que lorsque le service est réellement accessible, que le chemin de secours a été testé et que les résultats sont reproductibles.
