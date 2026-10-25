# IP Multicast — Niveau Débutant

> **Parcours :** Réseaux IP · **Niveau :** Débutant · **Fichier :** `multicast-debutant.md`
>
> Ce cours introduit la transmission multicast IPv4/IPv6, l’adhésion des hôtes, le contrôle de diffusion sur le LAN et le routage multicast entre sous-réseaux. Les commandes Cisco sont des exemples pédagogiques : leur disponibilité exacte dépend de la plate-forme, de la version IOS/IOS XE et du type de commutation utilisé.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir expliquer pourquoi le multicast n’est ni du unicast ni du broadcast, reconnaître les plages d’adresses multicast, décrire le rôle d’IGMP et de l’IGMP snooping, différencier le fonctionnement général de PIM Dense Mode, PIM Sparse Mode et SSM, expliquer le contrôle RPF, lire une entrée de base de la table multicast et suivre une méthode de dépannage structurée.

## Prérequis

- Adressage IPv4, masque et passerelle par défaut.
- Fonctionnement d’un switch Ethernet et d’un routeur IP.
- Notions de base sur les protocoles de routage unicast.
- Commandes de vérification Cisco telles que `show ip route`, `show ip interface brief` et `show running-config`.


## 1. Comprendre le multicast

Le **multicast IP** permet à une source d’envoyer un flux à un groupe de récepteurs intéressés. La source transmet un datagramme destiné à une adresse de groupe ; le réseau construit une distribution vers les segments où des récepteurs se sont abonnés. Le flux est répliqué aux points nécessaires, plutôt que de demander à la source de produire une copie unicast distincte pour chaque destinataire.

### Comparaison des modes de transmission

| Mode | Destination | Réplication | Exemple typique |
|---|---|---|---|
| Unicast | Une adresse d’hôte | Une session par destinataire si l’application la crée | SSH, téléchargement, appel API |
| Broadcast IPv4 | Tous les hôtes du domaine de broadcast | Diffusion dans le domaine L2 concerné | ARP utilise le broadcast Ethernet, mais pas comme une application multicast routée |
| Multicast | Une adresse de groupe | Le réseau réplique aux branches utiles | Diffusion vidéo, télémétrie de groupe, distribution de contenu |

Le multicast n’assure pas à lui seul la fiabilité de l’application. Il ne promet ni livraison à tous les récepteurs, ni ordre universel des paquets, ni retransmission automatique. Ces propriétés doivent être mises en œuvre par le protocole applicatif si elles sont nécessaires.

**Schéma 1 — Unicast, broadcast et multicast**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Unicast, broadcast et multicast"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Unicast, broadcast et multicast</text><rect x="22" y="58" width="296" height="315" rx="14" fill="#111f33" stroke="#29435e" stroke-width="1" /><text x="170" y="88" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#60a5fa" text-anchor="middle">UNICAST</text><text x="170" y="113" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">1 source → 1 destination</text><rect x="332" y="58" width="296" height="315" rx="14" fill="#111f33" stroke="#29435e" stroke-width="1" /><text x="480" y="88" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#fbbf24" text-anchor="middle">BROADCAST</text><text x="480" y="113" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">1 source → tout le domaine</text><rect x="642" y="58" width="296" height="315" rx="14" fill="#111f33" stroke="#29435e" stroke-width="1" /><text x="790" y="88" font-family="Arial,Helvetica,sans-serif" font-size="20" font-weight="700" fill="#4ade80" text-anchor="middle">MULTICAST</text><text x="790" y="113" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">1 source → abonnés du groupe</text><circle cx="72" cy="210" r="22" fill="#60a5fa" stroke="#60a5fa" stroke-width="2" /><text x="72" y="216" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#0b1220" text-anchor="middle">S</text><line x1="95" y1="210" x2="160" y2="210" stroke="#60a5fa" stroke-width="3" /><line x1="160" y1="210" x2="210" y2="210" stroke="#60a5fa" stroke-width="3" /><polygon points="210.0,210.0 197.0,216.0 197.0,204.0" fill="#60a5fa" /><rect x="218" y="186" width="82" height="48" rx="10" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="259" y="216" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#f4f7fb" text-anchor="middle">R1</text><circle cx="382" cy="210" r="22" fill="#fbbf24" stroke="#fbbf24" stroke-width="2" /><text x="382" y="216" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#0b1220" text-anchor="middle">S</text><line x1="405" y1="210" x2="480" y2="155" stroke="#fbbf24" stroke-width="2" /><circle cx="492" cy="155" r="15" fill="#4b3514" stroke="#fbbf24" stroke-width="2" /><text x="492" y="160" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#f4f7fb" text-anchor="middle">H</text><line x1="405" y1="210" x2="480" y2="210" stroke="#fbbf24" stroke-width="2" /><circle cx="492" cy="210" r="15" fill="#4b3514" stroke="#fbbf24" stroke-width="2" /><text x="492" y="215" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#f4f7fb" text-anchor="middle">H</text><line x1="405" y1="210" x2="480" y2="265" stroke="#fbbf24" stroke-width="2" /><circle cx="492" cy="265" r="15" fill="#4b3514" stroke="#fbbf24" stroke-width="2" /><text x="492" y="270" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#f4f7fb" text-anchor="middle">H</text><line x1="405" y1="210" x2="552" y2="155" stroke="#fbbf24" stroke-width="2" /><circle cx="564" cy="155" r="15" fill="#4b3514" stroke="#fbbf24" stroke-width="2" /><text x="564" y="160" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#f4f7fb" text-anchor="middle">H</text><line x1="405" y1="210" x2="552" y2="265" stroke="#fbbf24" stroke-width="2" /><circle cx="564" cy="265" r="15" fill="#4b3514" stroke="#fbbf24" stroke-width="2" /><text x="564" y="270" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#f4f7fb" text-anchor="middle">H</text><circle cx="692" cy="210" r="22" fill="#4ade80" stroke="#4ade80" stroke-width="2" /><text x="692" y="216" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#0b1220" text-anchor="middle">S</text><line x1="715" y1="210" x2="760" y2="210" stroke="#4ade80" stroke-width="3" /><circle cx="773" cy="210" r="12" fill="#4ade80" stroke="#4ade80" stroke-width="2" /><line x1="785" y1="210" x2="825" y2="148" stroke="#4ade80" stroke-width="2" /><circle cx="840" cy="148" r="16" fill="#153c2d" stroke="#4ade80" stroke-width="2" /><text x="840" y="153" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#f4f7fb" text-anchor="middle">H</text><line x1="785" y1="210" x2="825" y2="210" stroke="#4ade80" stroke-width="2" /><circle cx="840" cy="210" r="16" fill="#153c2d" stroke="#4ade80" stroke-width="2" /><text x="840" y="215" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#f4f7fb" text-anchor="middle">H</text><line x1="785" y1="210" x2="825" y2="272" stroke="#4ade80" stroke-width="2" /><circle cx="840" cy="272" r="16" fill="#153c2d" stroke="#4ade80" stroke-width="2" /><text x="840" y="277" font-family="Arial,Helvetica,sans-serif" font-size="12" font-weight="700" fill="#f4f7fb" text-anchor="middle">H</text><text x="480" y="353" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">La diffusion multicast dépend des abonnements, pas d’une duplication à chaque saut.</text></svg>

### Pourquoi le multicast peut économiser de la bande passante

Supposons un flux de 8 Mbit/s destiné à 40 récepteurs répartis sur plusieurs VLAN. Avec 40 flux unicast indépendants, le lien situé près de la source peut transporter jusqu’à 320 Mbit/s si chaque session est réellement séparée. Avec multicast, un seul flux peut traverser le lien commun puis être répliqué sur les branches où les récepteurs sont présents. Cette économie dépend toutefois de l’application et de l’architecture ; elle n’est pas garantie si l’émetteur ou le réseau utilise une autre méthode de distribution.

Le multicast est adapté lorsque plusieurs clients ont besoin du même contenu au même moment. Il n’est pas automatiquement le meilleur choix pour un contenu personnalisé, pour des clients qui reçoivent des versions différentes, ou lorsque les récepteurs ne peuvent pas gérer les flux multicast.

### Vocabulaire essentiel

- **Source (S)** : adresse IP qui émet le flux.
- **Groupe (G)** : adresse IP multicast de destination.
- **Récepteur** : hôte qui demande à recevoir le groupe ou le canal.
- **Abonnement / membership** : état signalant qu’un segment possède un ou plusieurs récepteurs intéressés.
- **Routage multicast** : transfert entre sous-réseaux multicast, réalisé par des routeurs configurés pour cela.
- **Arbre de distribution** : ensemble de chemins permettant au flux de rejoindre les segments intéressés.
- **RPF (Reverse Path Forwarding)** : contrôle qui vérifie que le paquet multicast arrive par l’interface attendue vers sa source ou, pour certains états d’arbre partagé, vers le RP.


## 2. Les adresses multicast IPv4

Les adresses multicast IPv4 se trouvent dans le bloc `224.0.0.0/4`, soit de `224.0.0.0` à `239.255.255.255`. Une adresse de groupe n’identifie pas une carte réseau unique comme le fait une adresse unicast. Plusieurs récepteurs peuvent rejoindre le même groupe et quitter ce groupe indépendamment.

Quelques plages importantes :

| Plage | Usage général | Précaution |
|---|---|---|
| `224.0.0.0/24` | Contrôle multicast sur le lien local | Ces groupes ne sont généralement pas routés au-delà du lien local ; ne les utilise pas comme plage applicative ordinaire |
| `232.0.0.0/8` | Source-Specific Multicast (SSM) en IPv4 | Le récepteur demande un canal source/groupe précis ; le support IGMPv3 est important |
| `239.0.0.0/8` | Espace administrativement délimité | Il doit être planifié et limité à un domaine voulu ; ce n’est pas du chiffrement ni une protection de sécurité |
| Autres parties du `224.0.0.0/4` | Divers usages multicast | Vérifier les allocations IANA et les conventions de l’application |

**Schéma 2 — Repères d’adressage IPv4 multicast**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Repères d’adressage IPv4 multicast"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Repères d’adressage IPv4 multicast</text><rect x="58" y="78" width="204" height="112" rx="14" fill="#162b45" stroke="#fbbf24" stroke-width="2" /><text x="160.0" y="110" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#fbbf24" text-anchor="middle">224.0.0.0/24</text><text x="160.0" y="140" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Contrôle local</text><text x="160.0" y="166" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">Pas routé au-delà</text><rect x="274" y="78" width="204" height="112" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="376.0" y="110" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#4ade80" text-anchor="middle">232.0.0.0/8</text><text x="376.0" y="140" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">SSM IPv4</text><text x="376.0" y="166" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">Source + groupe</text><rect x="490" y="78" width="204" height="112" rx="14" fill="#162b45" stroke="#f472b6" stroke-width="2" /><text x="592.0" y="110" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f472b6" text-anchor="middle">239.0.0.0/8</text><text x="592.0" y="140" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Portée admin.</text><text x="592.0" y="166" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">À borner au domaine</text><rect x="706" y="78" width="204" height="112" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="808.0" y="110" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#60a5fa" text-anchor="middle">224.0.0.0/4</text><text x="808.0" y="140" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Espace multicast</text><text x="808.0" y="166" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">224–239</text><text x="480" y="256" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f4f7fb" text-anchor="middle">Une adresse de groupe identifie une destination multicast, pas une machine unique.</text><text x="480" y="293" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">Vérifier l’affectation, la portée, la politique et le comportement de l’application.</text><text x="480" y="335" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#67e8f9" text-anchor="middle">Les plages ci-dessus sont des repères ; consulter IANA pour les allocations complètes.</text></svg>

### Choisir une adresse de groupe

Pour un laboratoire, une adresse de la plage `239.0.0.0/8` est souvent utilisée pour une application multicast privée au domaine administré, sous réserve de la planification locale et des limites définies dans le réseau. Il faut documenter l’application propriétaire, la plage assignée, la source attendue, le TTL, le domaine de routage et les règles de filtrage.

Ne choisis pas une adresse au hasard dans une plage réservée à un protocole ou à une fonction de contrôle. Deux applications qui réutilisent le même groupe dans un réseau commun peuvent recevoir un trafic inattendu ou être difficiles à dépanner. Le groupe et le port UDP sont également deux notions différentes : IP multicast porte l’adresse de groupe, tandis que l’application peut utiliser un port UDP pour distinguer son service.

### Le TTL multicast

Le champ IPv4 TTL limite le nombre de sauts d’un paquet. Ce n’est pas un mécanisme complet d’autorisation, mais une valeur trop faible peut empêcher le paquet de traverser les routeurs. Une valeur haute ne garantit pas que le réseau le transmettra : il faut aussi un routage multicast correct, un arbre actif, des adhésions et des politiques compatibles.


## 3. Du groupe IP à l’adresse MAC Ethernet

Sur Ethernet, un paquet IPv4 multicast utilise une adresse MAC multicast. Le mappage standard copie les 23 bits de poids faible de l’adresse IPv4 de groupe dans l’adresse MAC qui commence par `01:00:5e`. L’adresse MAC ne conserve donc pas tous les bits significatifs du groupe IPv4 : plusieurs groupes IP distincts peuvent correspondre à la même adresse MAC.

**Schéma 3 — Mappage IP multicast vers MAC Ethernet**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Mappage multicast IPv4 vers MAC Ethernet"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Mappage multicast IPv4 vers MAC Ethernet</text><rect x="40" y="80" width="250" height="104" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="165" y="111" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#60a5fa" text-anchor="middle">Adresse IPv4 multicast</text><text x="165" y="143" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" fill="#f4f7fb" text-anchor="middle">239.1.2.3</text><line x1="300" y1="132" x2="372" y2="132" stroke="#67e8f9" stroke-width="3" /><polygon points="372.0,132.0 359.0,138.0 359.0,126.0" fill="#67e8f9" /><text x="336" y="112" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#67e8f9" text-anchor="middle">mappage</text><rect x="382" y="80" width="250" height="104" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="507" y="111" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#4ade80" text-anchor="middle">MAC Ethernet multicast</text><text x="507" y="143" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f4f7fb" text-anchor="middle">01:00:5e:01:02:03</text><rect x="665" y="80" width="250" height="104" rx="14" fill="#3f2515" stroke="#fbbf24" stroke-width="2" /><text x="790" y="111" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#fbbf24" text-anchor="middle">À retenir</text><text x="790" y="143" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">23 bits de poids faible</text><text x="790" y="163" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">seulement sont copiés</text><rect x="70" y="235" width="820" height="100" rx="12" fill="#111f33" stroke="#29435e" stroke-width="1" /><text x="480" y="265" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f472b6" text-anchor="middle">Conséquence : des groupes IP différents peuvent partager la même MAC</text><text x="480" y="294" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">Le filtre IP du récepteur élimine les paquets qui ne correspondent pas à son groupe.</text><text x="480" y="318" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">Le mappage Ethernet n’identifie donc pas un groupe IPv4 de manière unique.</text></svg>

Cette collision de mappage n’implique pas que l’application confonde les groupes : la pile IP de l’hôte examine encore l’adresse IP du paquet. En revanche, le switch Ethernet ne peut pas toujours distinguer tous les groupes uniquement par cette MAC. L’IGMP snooping et les capacités matérielles de la plate-forme déterminent comment le switch maintient les entrées et transmet les paquets.

Le multicast Ethernet utilise un bit de groupe dans l’adresse MAC ; il ne doit pas être confondu avec le broadcast Ethernet `ff:ff:ff:ff:ff:ff`. Le broadcast est destiné au domaine de diffusion local ; une adresse MAC multicast représente un groupe et peut être filtrée selon des états d’adhésion.


## 4. IGMP : les hôtes signalent leur intérêt

**IGMP (Internet Group Management Protocol)** est utilisé par les hôtes IPv4 et les routeurs multicast sur un réseau local. Il permet au routeur de connaître les groupes qui intéressent les systèmes directement connectés à chaque interface. IGMP ne construit pas à lui seul les chemins à travers un réseau de routeurs : il fournit l’information d’adhésion locale au mécanisme de routage multicast.

Les messages et les minuteries d’IGMP permettent de maintenir et d’expirer les adhésions. Les hôtes répondent aux requêtes de groupe selon la version et l’état qu’ils souhaitent signaler. L’absence d’un rapport récent n’est pas toujours la preuve qu’aucun récepteur n’existe : le protocole utilise des temporisateurs, des suppressions de rapports et des règles de compatibilité.

**Schéma 4 — De l’hôte à IGMP puis au routage multicast**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Chaîne de contrôle : hôte, IGMP, snooping et PIM"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Chaîne de contrôle : hôte, IGMP, snooping et PIM</text><rect x="35" y="104" width="170" height="86" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="120" y="138" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f4f7fb" text-anchor="middle">Hôte</text><text x="120" y="162" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f4f7fb" text-anchor="middle">récepteur</text><rect x="264" y="104" width="185" height="86" rx="14" fill="#162b45" stroke="#67e8f9" stroke-width="2" /><text x="356" y="138" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f4f7fb" text-anchor="middle">Switch L2</text><text x="356" y="162" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f4f7fb" text-anchor="middle">IGMP snooping</text><rect x="508" y="104" width="185" height="86" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="600" y="138" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f4f7fb" text-anchor="middle">Routeur L3</text><text x="600" y="162" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f4f7fb" text-anchor="middle">IGMP querier</text><rect x="752" y="104" width="172" height="86" rx="14" fill="#162b45" stroke="#fbbf24" stroke-width="2" /><text x="838" y="138" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f4f7fb" text-anchor="middle">PIM</text><text x="838" y="162" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f4f7fb" text-anchor="middle">réseau routé</text><line x1="205" y1="130" x2="264" y2="130" stroke="#60a5fa" stroke-width="3" /><polygon points="264.0,130.0 251.0,136.0 251.0,124.0" fill="#60a5fa" /><text x="234" y="116" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" fill="#60a5fa" text-anchor="middle">Report</text><line x1="449" y1="148" x2="508" y2="148" stroke="#67e8f9" stroke-width="3" /><polygon points="508.0,148.0 495.0,154.0 495.0,142.0" fill="#67e8f9" /><text x="479" y="134" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" fill="#67e8f9" text-anchor="middle">état</text><line x1="693" y1="130" x2="752" y2="130" stroke="#4ade80" stroke-width="3" /><polygon points="752.0,130.0 739.0,136.0 739.0,124.0" fill="#4ade80" /><text x="722" y="116" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" fill="#4ade80" text-anchor="middle">Join</text><line x1="508" y1="173" x2="449" y2="173" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6 4" /><polygon points="449.0,173.0 462.0,167.0 462.0,179.0" fill="#fbbf24" /><text x="480" y="205" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="400" fill="#b9c7d8" text-anchor="middle">Query / réponse locale</text><text x="480" y="270" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f4f7fb" text-anchor="middle">IGMP gère l’adhésion au groupe sur le LAN IPv4.</text><text x="480" y="300" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">PIM construit la distribution entre routeurs : les deux protocoles sont complémentaires.</text></svg>

### Les grandes différences entre IGMPv1, IGMPv2 et IGMPv3

| Version | Fonctions à retenir | Limites / usage |
|---|---|---|
| IGMPv1 | Requêtes générales et rapports d’adhésion | Pas de message Leave explicite dans le modèle v1 |
| IGMPv2 | Message Leave et mécanismes permettant de vérifier plus rapidement le départ | Abonnement à un groupe, sans filtrage de source au niveau IGMPv3 |
| IGMPv3 | Filtrage de source ; modes INCLUDE/EXCLUDE | Permet le modèle requis pour SSM, si toute la chaîne le prend en charge |

**Schéma 5 — Évolution d’IGMP**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="IGMP : évolution des fonctions"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">IGMP : évolution des fonctions</text><rect x="45" y="93" width="264" height="180" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="177" y="126" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" fill="#60a5fa" text-anchor="middle">IGMPv1</text><text x="177" y="167" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Membership report</text><text x="177" y="197" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">Pas de Leave explicite</text><rect x="348" y="93" width="264" height="180" rx="14" fill="#162b45" stroke="#fbbf24" stroke-width="2" /><text x="480" y="126" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" fill="#fbbf24" text-anchor="middle">IGMPv2</text><text x="480" y="167" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Report + Leave</text><text x="480" y="197" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">Départ plus rapide</text><rect x="651" y="93" width="264" height="180" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="783" y="126" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" fill="#4ade80" text-anchor="middle">IGMPv3</text><text x="783" y="167" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Filtrage de source</text><text x="783" y="197" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">Include / Exclude</text><text x="480" y="324" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#67e8f9" text-anchor="middle">La compatibilité dépend aussi de l’hôte, du querier, du routeur et de l’application.</text></svg>

### Rapport d’adhésion et départ

Lorsqu’une application rejoint un groupe, la pile de l’hôte signale l’intérêt. Le routeur apprend qu’il existe un récepteur sur ce segment et peut intégrer l’interface à l’état multicast approprié. Lorsqu’un hôte quitte un groupe, la réaction dépend de la version d’IGMP, de la présence d’autres abonnés sur le même segment, des minuteries et de la prise en charge du *fast leave* par le switch. Un mécanisme de départ rapide doit être utilisé prudemment sur les ports où plusieurs récepteurs peuvent se trouver derrière un seul port (par exemple un port vers un point d’accès ou un autre switch).

### IGMP querier

Sur chaque sous-réseau/VLAN multicast concerné, un routeur multicast ou un équipement doté d’une fonction IGMP querier envoie des requêtes générales périodiques. Les récepteurs les utilisent pour confirmer leurs adhésions. La procédure d’élection et le fonctionnement précis dépendent de la version et de l’implémentation. Si aucun querier n’est présent sur un VLAN où le switch s’appuie sur des rapports pour construire ses états snooping, les entrées peuvent expirer et la livraison peut devenir incorrecte ou inefficace.

Un **IGMP querier de VLAN** et un **routeur multicast PIM** sont proches fonctionnellement, mais pas identiques. Certaines plateformes possèdent un IGMP snooping querier de couche 2 pour les cas où aucun routeur multicast n’assure cette tâche sur le VLAN. Sa prise en charge, les versions IGMP supportées et les conditions d’activation varient selon les équipements.


## 5. IGMP snooping : limiter la diffusion dans le VLAN

Sans filtrage L2, un switch peut traiter le trafic multicast inconnu comme du trafic à inonder sur une partie ou l’ensemble des ports du VLAN. **IGMP snooping** observe les messages IGMP pour associer les groupes aux ports qui ont des récepteurs, tout en maintenant les ports vers les routeurs multicast. Le switch n’a pas besoin de devenir un routeur multicast pour effectuer cette fonction de couche 2.

**Schéma 6 — IGMP snooping et ports intéressés**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="IGMP snooping : limiter le trafic au bon port"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">IGMP snooping : limiter le trafic au bon port</text><rect x="36" y="95" width="180" height="100" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="126" y="132" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Receveur A</text><text x="126" y="154" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">rejoint G</text><rect x="285" y="95" width="215" height="100" rx="14" fill="#162b45" stroke="#67e8f9" stroke-width="2" /><text x="392" y="132" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Table snooping</text><text x="392" y="154" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">VLAN 20 : port 5</text><rect x="570" y="95" width="170" height="100" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="655" y="132" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Port routeur</text><text x="655" y="154" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">multicast</text><rect x="786" y="95" width="140" height="100" rx="14" fill="#162b45" stroke="#f472b6" stroke-width="2" /><text x="856" y="132" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">Source</text><text x="856" y="154" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">envoie G</text><line x1="216" y1="134" x2="285" y2="134" stroke="#60a5fa" stroke-width="3" /><polygon points="285.0,134.0 272.0,140.0 272.0,128.0" fill="#60a5fa" /><line x1="500" y1="134" x2="570" y2="134" stroke="#67e8f9" stroke-width="3" /><polygon points="570.0,134.0 557.0,140.0 557.0,128.0" fill="#67e8f9" /><line x1="786" y1="157" x2="740" y2="157" stroke="#f472b6" stroke-width="3" /><polygon points="740.0,157.0 753.0,151.0 753.0,163.0" fill="#f472b6" /><line x1="655" y1="195" x2="655" y2="229" stroke="#b9c7d8" stroke-width="2" /><line x1="655" y1="229" x2="392" y2="229" stroke="#b9c7d8" stroke-width="2" /><polygon points="392.0,229.0 405.0,223.0 405.0,235.0" fill="#b9c7d8" /><text x="525" y="255" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f4f7fb" text-anchor="middle">États d’adhésion limitent les ports de sortie</text><text x="480" y="315" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#fbbf24" text-anchor="middle">Sans état fiable, le switch peut inonder le VLAN de trafic multicast inconnu.</text></svg>

### Que vérifier sur le switch

- Le snooping est-il activé globalement et sur le VLAN voulu ?
- Le switch reçoit-il les rapports IGMP du bon VLAN ?
- Un port vers un routeur multicast est-il reconnu comme *mrouter port* ?
- Un querier est-il actif lorsque la topologie en a besoin ?
- Les entrées correspondent-elles au bon groupe et aux bons ports ?
- L’application envoie-t-elle vers une adresse de groupe qui correspond à l’entrée attendue ?

Ne suppose pas que l’activation de l’IGMP snooping résout le routage multicast entre VLAN. Le snooping limite le transfert Ethernet dans le VLAN ; PIM et la table de routage multicast traitent la distribution L3 entre sous-réseaux.

### Inondation du multicast inconnu

Selon l’implémentation et les options de sécurité, un switch peut inonder du multicast inconnu sur certains ports, le supprimer ou le traiter avec une autre politique. Ces comportements ne sont pas identiques sur toutes les plates-formes. Si un flux atteint trop de ports, vérifie les tables de groupes, le rôle du querier, les ports routeurs et les compteurs avant de conclure que PIM est en cause.


## 6. Routage multicast et table de transfert

Le routage multicast construit un ensemble d’états qui associent une source et un groupe aux interfaces d’entrée et de sortie. L’implémentation est propre à la plate-forme, mais les concepts de base restent utiles.

- **IIF (Incoming Interface)** : interface par laquelle le flux doit arriver selon le contrôle RPF.
- **OIL (Outgoing Interface List)** : liste des interfaces sur lesquelles les paquets doivent être répliqués.
- **`(*,G)`** : état d’arbre partagé pour un groupe, utilisé notamment par PIM Sparse Mode autour du RP.
- **`(S,G)`** : état spécifique à une source et à un groupe.
- **RPF** : vérification du chemin de retour vers la source ou, dans certains contextes de l’arbre partagé, vers le RP.

Un flux peut être reçu sur une interface mais ne pas être transmis si le paquet échoue au RPF, si l’OIL ne contient aucun port actif, si l’interface de sortie est bloquée par une politique ou si aucun récepteur n’est présent sur la branche. Inversement, la présence d’une entrée dans la table n’est pas la preuve à elle seule que le bon contenu est reçu par l’application.

**Schéma 7 — Les entrées IIF et OIL**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Entrée IIF et liste des sorties OIL"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Entrée IIF et liste des sorties OIL</text><rect x="30" y="145" width="115" height="96" rx="12" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="87" y="178" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#4ade80" text-anchor="middle">Source S</text><text x="87" y="207" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">Paquets (S,G)</text><rect x="220" y="145" width="190" height="96" rx="12" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="315" y="177" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#60a5fa" text-anchor="middle">Routeur R1</text><text x="315" y="205" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">IIF = Gi0/0</text><text x="315" y="225" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="400" fill="#b9c7d8" text-anchor="middle">RPF validé</text><line x1="145" y1="193" x2="220" y2="193" stroke="#4ade80" stroke-width="3" /><polygon points="220,193 207.0,199.0 207.0,187.0" fill="#4ade80" /><rect x="470" y="130" width="205" height="126" rx="12" fill="#162b45" stroke="#67e8f9" stroke-width="2" /><text x="572" y="163" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#67e8f9" text-anchor="middle">État multicast</text><text x="572" y="191" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f4f7fb" text-anchor="middle">(S,G)</text><text x="572" y="216" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">OIL : Gi0/1, Gi0/2</text><line x1="410" y1="193" x2="470" y2="193" stroke="#60a5fa" stroke-width="3" /><polygon points="470,193 457.0,199.0 457.0,187.0" fill="#60a5fa" /><rect x="745" y="80" width="185" height="78" rx="12" fill="#162b45" stroke="#fbbf24" stroke-width="2" /><text x="837" y="110" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#fbbf24" text-anchor="middle">Sortie Gi0/1</text><text x="837" y="135" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">VLAN A : récepteurs</text><rect x="745" y="250" width="185" height="78" rx="12" fill="#162b45" stroke="#f472b6" stroke-width="2" /><text x="837" y="280" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f472b6" text-anchor="middle">Sortie Gi0/2</text><text x="837" y="305" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">VLAN B : récepteurs</text><line x1="675" y1="193" x2="706" y2="193" stroke="#67e8f9" stroke-width="3" /><line x1="706" y1="119" x2="706" y2="289" stroke="#67e8f9" stroke-width="3" /><line x1="706" y1="119" x2="745" y2="119" stroke="#fbbf24" stroke-width="3" /><polygon points="745,119 732.0,125.0 732.0,113.0" fill="#fbbf24" /><line x1="706" y1="289" x2="745" y2="289" stroke="#f472b6" stroke-width="3" /><polygon points="745,289 732.0,295.0 732.0,283.0" fill="#f472b6" /><text x="480" y="361" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#b9c7d8" text-anchor="middle">IIF : entrée attendue ; OIL : branches où répliquer après validation RPF.</text></svg>

### Le contrôle RPF en termes simples

Le routeur utilise l’information de routage unicast pour déterminer l’interface attendue vers une source (ou vers le RP selon l’état multicast). Un paquet reçu par cette interface peut passer le contrôle RPF ; s’il arrive par une autre interface, il peut être rejeté afin de limiter les boucles. C’est pourquoi le routage unicast, les métriques, les routes statiques et l’asymétrie influencent le résultat multicast.

Le contrôle RPF n’est pas équivalent à un ping vers la source. Un ping peut réussir tandis que RPF échoue si la meilleure route de retour passe par une interface différente de celle sur laquelle le paquet multicast arrive. Il faut comparer la route attendue, l’interface d’entrée réelle et l’état multicast affiché par l’équipement.

**Schéma 8 — RPF : bon chemin ou entrée inattendue**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="RPF : vérifier le bon chemin de retour"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">RPF : vérifier le bon chemin de retour</text><circle cx="110" cy="207" r="25" fill="#4ade80" stroke="#4ade80" stroke-width="2" /><text x="110" y="213" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#0b1220" text-anchor="middle">S</text><rect x="250" y="162" width="160" height="90" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="330" y="199" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#60a5fa" text-anchor="middle">R1</text><text x="330" y="226" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">entrée attendue</text><rect x="520" y="162" width="160" height="90" rx="14" fill="#162b45" stroke="#67e8f9" stroke-width="2" /><text x="600" y="199" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#67e8f9" text-anchor="middle">R2</text><text x="600" y="226" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">RPF valide</text><rect x="520" y="275" width="160" height="70" rx="14" fill="#40212a" stroke="#fb7185" stroke-width="2" /><text x="600" y="304" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#fb7185" text-anchor="middle">R3</text><text x="600" y="326" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="400" fill="#f4f7fb" text-anchor="middle">RPF invalide</text><line x1="135" y1="207" x2="250" y2="207" stroke="#4ade80" stroke-width="3" /><polygon points="250.0,207.0 237.0,213.0 237.0,201.0" fill="#4ade80" /><line x1="410" y1="207" x2="520" y2="207" stroke="#60a5fa" stroke-width="3" /><polygon points="520.0,207.0 507.0,213.0 507.0,201.0" fill="#60a5fa" /><line x1="410" y1="236" x2="520" y2="305" stroke="#fb7185" stroke-width="3" stroke-dasharray="7 5" /><polygon points="520.0,305.0 505.8,303.2 512.2,293.0" fill="#fb7185" /><text x="800" y="184" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#f4f7fb" text-anchor="middle">Contrôle RPF</text><text x="800" y="214" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">entrée du paquet</text><text x="800" y="237" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">doit correspondre</text><text x="800" y="260" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">au chemin unicast</text><text x="480" y="367" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#fbbf24" text-anchor="middle">RPF évite les boucles ; asymétrie et routes incorrectes peuvent supprimer le flux.</text></svg>


## 7. PIM : distribuer le flux entre les routeurs

**PIM (Protocol Independent Multicast)** est une famille de protocoles de routage multicast. Le mot *independent* signifie que PIM n’est pas attaché à un protocole de routage unicast précis ; il peut utiliser les informations de routage unicast pour le RPF. Cela ne signifie pas que le multicast peut fonctionner sans connectivité unicast et sans choix d’interface RPF cohérent.

| Modèle | Principe | Points d’attention |
|---|---|---|
| PIM Dense Mode (PIM-DM) | Envoie largement le trafic puis élimine les branches non intéressées (*flood-and-prune*) | Peut générer du trafic excessif ; à réserver à des contextes adaptés |
| PIM Sparse Mode (PIM-SM) | Les routeurs en aval signalent leur intérêt ; un RP facilite l’arbre partagé initial | Nécessite une conception RP cohérente pour les groupes ASM |
| SSM (Source-Specific Multicast) | Le récepteur demande un canal `(S,G)` précis | Requiert une signalisation côté hôte adaptée, typiquement IGMPv3 en IPv4 |

**Schéma 9 — Comparaison des modèles PIM**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Trois modèles de distribution multicast"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Trois modèles de distribution multicast</text><rect x="35" y="100" width="270" height="180" rx="14" fill="#162b45" stroke="#fbbf24" stroke-width="2" /><text x="170" y="136" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" fill="#fbbf24" text-anchor="middle">PIM-DM</text><text x="170" y="181" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f4f7fb" text-anchor="middle">Flood puis prune</text><text x="170" y="213" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">Modèle dense</text><rect x="345" y="100" width="270" height="180" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="480" y="136" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" fill="#60a5fa" text-anchor="middle">PIM-SM</text><text x="480" y="181" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f4f7fb" text-anchor="middle">Join explicites + RP</text><text x="480" y="213" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">Modèle sparse</text><rect x="655" y="100" width="270" height="180" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="790" y="136" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="700" fill="#4ade80" text-anchor="middle">SSM</text><text x="790" y="181" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f4f7fb" text-anchor="middle">Join (S,G)</text><text x="790" y="213" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#b9c7d8" text-anchor="middle">Pas de RP pour SSM</text><text x="480" y="326" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#67e8f9" text-anchor="middle">Le choix dépend des récepteurs, du modèle applicatif et du support des équipements.</text></svg>

En environnement d’entreprise, PIM-SM est un modèle commun pour les groupes ASM. SSM est intéressant lorsque l’application connaît l’adresse de la source et que cette paire source/groupe peut être exprimée par le récepteur. La bonne option dépend du matériel, du logiciel, de l’application et des exigences opérationnelles. PIM-DM ne doit pas être activé seulement « pour tester » sur un réseau étendu sans comprendre ses conséquences de diffusion.

### Les voisins PIM

Sur les interfaces multicast, les routeurs échangent des messages Hello pour découvrir les voisins PIM. L’absence de voisin PIM peut empêcher la création d’un arbre même si le routage unicast fonctionne. Vérifie les interfaces, les adresses, les filtres, la version du protocole, le type de réseau, les ACL et les journaux. Les commandes de vérification sont dépendantes de la plateforme ; sur Cisco IOS/IOS XE, `show ip pim neighbor` est une commande courante.


## 8. PIM Sparse Mode et le Rendezvous Point (RP)

Dans le modèle ASM de PIM-SM, le **Rendezvous Point (RP)** aide les routeurs à construire l’arbre partagé initial. Le premier routeur côté source peut encapsuler les premiers paquets dans des messages Register vers le RP. Les routeurs côté récepteur utilisent des Join PIM pour signaler l’intérêt sur l’arbre partagé. Le RP transmet le flux vers les branches concernées, puis une implémentation peut faire évoluer le chemin vers un arbre spécifique à la source lorsque c’est applicable.

**Schéma 10 — Arbre partagé autour du RP**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="PIM-SM : arbre partagé et rôle du RP"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">PIM-SM : arbre partagé et rôle du RP</text><circle cx="115" cy="218" r="29" fill="#4ade80" stroke="#4ade80" stroke-width="2" /><text x="115" y="224" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#0b1220" text-anchor="middle">S</text><text x="115" y="266" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f4f7fb" text-anchor="middle">Source</text><circle cx="390" cy="218" r="36" fill="#fbbf24" stroke="#fbbf24" stroke-width="2" /><text x="390" y="224" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#0b1220" text-anchor="middle">RP</text><text x="390" y="266" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f4f7fb" text-anchor="middle">Rendezvous Point</text><circle cx="685" cy="120" r="22" fill="#60a5fa" stroke="#60a5fa" stroke-width="2" /><text x="685" y="126" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#0b1220" text-anchor="middle">R1</text><circle cx="685" cy="295" r="22" fill="#60a5fa" stroke="#60a5fa" stroke-width="2" /><text x="685" y="301" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#0b1220" text-anchor="middle">R2</text><circle cx="866" cy="120" r="20" fill="#f472b6" stroke="#f472b6" stroke-width="2" /><text x="866" y="126" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" fill="#0b1220" text-anchor="middle">H1</text><circle cx="866" cy="295" r="20" fill="#f472b6" stroke="#f472b6" stroke-width="2" /><text x="866" y="301" font-family="Arial,Helvetica,sans-serif" font-size="13" font-weight="700" fill="#0b1220" text-anchor="middle">H2</text><line x1="145" y1="218" x2="352" y2="218" stroke="#4ade80" stroke-width="3" /><polygon points="352.0,218.0 339.0,224.0 339.0,212.0" fill="#4ade80" /><text x="247" y="204" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#4ade80" text-anchor="middle">Register / flux</text><line x1="422" y1="198" x2="662" y2="134" stroke="#60a5fa" stroke-width="3" /><polygon points="662.0,134.0 651.0,143.1 647.9,131.6" fill="#60a5fa" /><line x1="422" y1="238" x2="662" y2="280" stroke="#60a5fa" stroke-width="3" /><polygon points="662.0,280.0 648.2,283.7 650.2,271.8" fill="#60a5fa" /><line x1="707" y1="120" x2="842" y2="120" stroke="#60a5fa" stroke-width="3" /><polygon points="842.0,120.0 829.0,126.0 829.0,114.0" fill="#60a5fa" /><line x1="707" y1="295" x2="842" y2="295" stroke="#60a5fa" stroke-width="3" /><polygon points="842.0,295.0 829.0,301.0 829.0,289.0" fill="#60a5fa" /><text x="480" y="355" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">Le RP organise l’arbre partagé initial ; le trafic peut ensuite passer en arbre source.</text></svg>

Le RP doit être accessible en unicast et son mapping doit être cohérent sur les routeurs concernés. Dans une architecture manuelle, l’adresse du RP est configurée de manière cohérente ; dans une architecture dynamique, un mécanisme tel que BSR ou Auto-RP peut distribuer les mappings selon le design et le support de la plateforme. Les méthodes dynamiques ne sont pas interchangeables sur tous les équipements et il faut respecter les guides de la version utilisée.

### Arbre partagé et arbre source

L’état `(*,G)` représente l’intérêt pour le groupe via le RP. L’état `(S,G)` représente un chemin vers une source donnée. Le passage au Shortest Path Tree (SPT) peut réduire le détour par le RP et améliorer le chemin des données, mais il doit être compris comme un mécanisme de l’implémentation et de la configuration — le seuil d’activation et le comportement exact ne sont pas uniformes entre plates-formes.

**Schéma 11 — Passage possible de `(*,G)` vers `(S,G)`**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Du partage via RP au plus court chemin (SPT)"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Du partage via RP au plus court chemin (SPT)</text><rect x="40" y="77" width="260" height="91" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="170" y="110" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#4ade80" text-anchor="middle">Arbre partagé (*,G)</text><text x="170" y="140" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">via le RP</text><rect x="40" y="219" width="260" height="91" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="170" y="252" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#60a5fa" text-anchor="middle">Arbre source (S,G)</text><text x="170" y="282" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">chemin RPF vers S</text><rect x="390" y="139" width="200" height="100" rx="14" fill="#162b45" stroke="#fbbf24" stroke-width="2" /><text x="490" y="177" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#fbbf24" text-anchor="middle">Routeur receveur</text><text x="490" y="206" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">décision locale</text><rect x="680" y="139" width="230" height="100" rx="14" fill="#162b45" stroke="#f472b6" stroke-width="2" /><text x="795" y="177" font-family="Arial,Helvetica,sans-serif" font-size="18" font-weight="700" fill="#f472b6" text-anchor="middle">Source S</text><text x="795" y="206" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">flux multicast</text><line x1="300" y1="122" x2="390" y2="166" stroke="#4ade80" stroke-width="3" /><polygon points="390.0,166.0 375.7,165.7 381.0,154.9" fill="#4ade80" /><line x1="590" y1="189" x2="680" y2="189" stroke="#fbbf24" stroke-width="3" /><polygon points="680.0,189.0 667.0,195.0 667.0,183.0" fill="#fbbf24" /><line x1="300" y1="264" x2="390" y2="215" stroke="#60a5fa" stroke-width="3" /><polygon points="390.0,215.0 381.5,226.5 375.7,215.9" fill="#60a5fa" /><text x="480" y="344" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">La bascule vers (S,G) dépend de l’implémentation et des seuils configurés.</text></svg>

### Redondance du RP

Le RP est un élément de conception important dans PIM-SM ASM. Les moyens de redondance disponibles peuvent inclure Anycast-RP avec MSDP dans les architectures qui le supportent, ou des mécanismes de découverte/élection selon le réseau. Chaque méthode a des conditions de conception, des exigences de convergence et des limites précises. Le fait d’avoir deux routeurs nommés « RP » ne suffit pas à garantir le partage de l’état source ni le basculement des flux.

Pour une première maquette, un RP statique unique est plus facile à comprendre. Pour une mise en production, examine les conséquences de la panne du RP, la localisation des sources et des récepteurs, le temps de convergence et l’approche de reprise prévue.


## 9. Source-Specific Multicast (SSM)

SSM est fondé sur un canal identifié par une source `S` et un groupe `G`. Le récepteur n’annonce pas seulement « je veux le groupe G » ; il signale son intérêt pour une source spécifique du groupe. En IPv4, la plage `232.0.0.0/8` est le repère SSM courant, à utiliser conformément à la politique du réseau et aux capacités des équipements.

**Schéma 12 — SSM : le récepteur choisit un canal `(S,G)`**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Source-Specific Multicast : la paire (S,G)"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Source-Specific Multicast : la paire (S,G)</text><rect x="40" y="110" width="180" height="100" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="130" y="145" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#4ade80" text-anchor="middle">Source S</text><text x="130" y="175" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">192.0.2.10</text><rect x="292" y="110" width="180" height="100" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="382" y="145" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#60a5fa" text-anchor="middle">Groupe G</text><text x="382" y="175" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">232.1.1.1</text><rect x="545" y="110" width="180" height="100" rx="14" fill="#162b45" stroke="#67e8f9" stroke-width="2" /><text x="635" y="145" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#67e8f9" text-anchor="middle">IGMPv3</text><text x="635" y="175" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">source + groupe</text><rect x="785" y="110" width="140" height="100" rx="14" fill="#162b45" stroke="#f472b6" stroke-width="2" /><text x="855" y="145" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#f472b6" text-anchor="middle">PIM</text><text x="855" y="175" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">(S,G)</text><line x1="220" y1="160" x2="292" y2="160" stroke="#4ade80" stroke-width="3" /><polygon points="292.0,160.0 279.0,166.0 279.0,154.0" fill="#4ade80" /><line x1="472" y1="160" x2="545" y2="160" stroke="#60a5fa" stroke-width="3" /><polygon points="545.0,160.0 532.0,166.0 532.0,154.0" fill="#60a5fa" /><line x1="725" y1="160" x2="785" y2="160" stroke="#67e8f9" stroke-width="3" /><polygon points="785.0,160.0 772.0,166.0 772.0,154.0" fill="#67e8f9" /><rect x="115" y="261" width="730" height="75" rx="12" fill="#111f33" stroke="#29435e" stroke-width="1" /><text x="480" y="292" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">SSM : l’abonné exprime l’intérêt pour une source précise et un groupe précis.</text><text x="480" y="318" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">Dans le modèle SSM habituel, aucun RP n’est nécessaire pour ce canal (S,G).</text></svg>

SSM réduit la dépendance au RP pour les canaux concernés : le récepteur et le réseau connaissent la source souhaitée. Cela simplifie certains cas d’exploitation, mais nécessite une application et des récepteurs compatibles avec le filtrage de source. Avec IGMPv3, les modes INCLUDE/EXCLUDE servent à représenter les sources acceptées ou bloquées selon les règles définies par le protocole.

Avant d’adopter SSM, vérifie :

- La prise en charge de l’IGMPv3 côté hôtes, routeurs et switches.
- La façon dont l’application découvre et signale l’adresse de source.
- La plage SSM configurée et les ACL associées.
- Le comportement en cas de changement de source ou de groupe.
- La télémétrie et les outils utilisés pour analyser un état `(S,G)`.


## 10. Multicast IPv6 : MLD et groupes IPv6

En IPv6, les adresses multicast commencent par `ff00::/8`. **MLD (Multicast Listener Discovery)** joue, pour la gestion d’adhésion IPv6, un rôle comparable à IGMP en IPv4. Le routage multicast IPv6 est une fonction distincte du simple traitement de l’adhésion par MLD.

**Schéma 13 — MLD et multicast IPv6**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Multicast IPv6 : MLD et routage"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Multicast IPv6 : MLD et routage</text><rect x="55" y="110" width="220" height="112" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="165" y="147" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#60a5fa" text-anchor="middle">Hôte IPv6</text><text x="165" y="178" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#f4f7fb" text-anchor="middle">MLD Report</text><rect x="365" y="110" width="220" height="112" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="475" y="147" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#4ade80" text-anchor="middle">Routeur</text><text x="475" y="178" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#f4f7fb" text-anchor="middle">MLD / PIM IPv6</text><rect x="675" y="110" width="230" height="112" rx="14" fill="#162b45" stroke="#fbbf24" stroke-width="2" /><text x="790" y="147" font-family="Arial,Helvetica,sans-serif" font-size="19" font-weight="700" fill="#fbbf24" text-anchor="middle">Groupe ff..</text><text x="790" y="178" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="400" fill="#f4f7fb" text-anchor="middle">portée IPv6</text><line x1="275" y1="166" x2="365" y2="166" stroke="#60a5fa" stroke-width="3" /><polygon points="365.0,166.0 352.0,172.0 352.0,160.0" fill="#60a5fa" /><line x1="585" y1="166" x2="675" y2="166" stroke="#4ade80" stroke-width="3" /><polygon points="675.0,166.0 662.0,172.0 662.0,160.0" fill="#4ade80" /><text x="480" y="277" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" fill="#f4f7fb" text-anchor="middle">IGMP sert à IPv4 ; MLD sert à IPv6 et s’appuie sur ICMPv6.</text><text x="480" y="309" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">Vérifier aussi le snooping MLD sur les switches et les règles de filtrage IPv6.</text></svg>

Les switches peuvent offrir MLD snooping pour limiter le trafic multicast IPv6 au bon port. L’activation d’IGMP snooping ne signifie pas que le multicast IPv6 sera filtré de la même façon. Pour déployer IPv6 multicast, il faut inspecter les fonctionnalités IPv6 de la plateforme, les requêtes MLD, les groupes écoutés et le protocole de routage multicast IPv6 utilisé.

La portée d’une adresse IPv6 multicast fait partie de son identification. N’applique pas les mêmes hypothèses que pour les plages IPv4 : lis la portée encodée dans l’adresse et les règles de routage pertinentes. Le multicast IPv6 n’est pas équivalent à un broadcast IPv6, qui n’existe pas sous la même forme qu’en IPv4.


## 11. Laboratoire guidé : trois routeurs, une source et des récepteurs

### But

Créer un petit domaine PIM-SM qui transporte un groupe multicast depuis un LAN source vers un LAN récepteur. Le laboratoire illustre les mécanismes, et non une configuration universelle. Les noms d’interfaces et certaines commandes changent selon le modèle, l’image logicielle et le type d’équipement. Il faut consulter les notes de version et le guide exact du matériel de laboratoire.

**Schéma 14 — Topologie du laboratoire**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Laboratoire : source, trois routeurs et récepteurs"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Laboratoire : source, trois routeurs et récepteurs</text><rect x="25" y="130" width="165" height="100" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="107" y="165" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#4ade80" text-anchor="middle">LAN SOURCE</text><text x="107" y="196" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">192.0.2.0/24</text><rect x="235" y="130" width="140" height="100" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="305" y="165" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="700" fill="#60a5fa" text-anchor="middle">R1</text><text x="305" y="196" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">FHR</text><rect x="415" y="130" width="140" height="100" rx="14" fill="#162b45" stroke="#fbbf24" stroke-width="2" /><text x="485" y="165" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="700" fill="#fbbf24" text-anchor="middle">R2</text><text x="485" y="196" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">RP</text><rect x="595" y="130" width="140" height="100" rx="14" fill="#162b45" stroke="#67e8f9" stroke-width="2" /><text x="665" y="165" font-family="Arial,Helvetica,sans-serif" font-size="21" font-weight="700" fill="#67e8f9" text-anchor="middle">R3</text><text x="665" y="196" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="400" fill="#f4f7fb" text-anchor="middle">LHR</text><rect x="770" y="130" width="165" height="100" rx="14" fill="#162b45" stroke="#f472b6" stroke-width="2" /><text x="852" y="165" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f472b6" text-anchor="middle">LAN CLIENTS</text><text x="852" y="196" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">203.0.113.0/24</text><line x1="190" y1="180" x2="230" y2="180" stroke="#4ade80" stroke-width="3" /><polygon points="230.0,180.0 217.0,186.0 217.0,174.0" fill="#4ade80" /><line x1="375" y1="180" x2="415" y2="180" stroke="#60a5fa" stroke-width="3" /><polygon points="415.0,180.0 402.0,186.0 402.0,174.0" fill="#60a5fa" /><line x1="555" y1="180" x2="595" y2="180" stroke="#fbbf24" stroke-width="3" /><polygon points="595.0,180.0 582.0,186.0 582.0,174.0" fill="#fbbf24" /><line x1="735" y1="180" x2="775" y2="180" stroke="#67e8f9" stroke-width="3" /><polygon points="775.0,180.0 762.0,186.0 762.0,174.0" fill="#67e8f9" /><text x="480" y="282" font-family="Arial,Helvetica,sans-serif" font-size="16" font-weight="700" fill="#f4f7fb" text-anchor="middle">RP Loopback : 10.255.0.2/32  •  Groupe ASM : 239.1.1.1</text><text x="480" y="316" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">Routage unicast opérationnel partout ; PIM sur chaque interface du chemin.</text></svg>

### Plan d’adressage d’exemple

| Élément | Adresse / réseau | Rôle |
|---|---|---|
| LAN source | `192.0.2.0/24` | Hôte émetteur, par exemple `192.0.2.10` |
| R1–R2 | `198.51.100.0/30` | Lien point à point |
| R2–R3 | `198.51.100.4/30` | Lien point à point |
| LAN receveurs | `203.0.113.0/24` | Hôtes abonnés au groupe |
| Loopback R2 | `10.255.0.2/32` | Adresse du RP dans cet exemple |
| Groupe d’essai | `239.1.1.1` | Groupe de démonstration ASM |

### Préparation unicast

Avant le multicast, les trois routeurs doivent avoir une connectivité unicast vers les réseaux source, récepteur et RP. Configure OSPF, IS-IS ou des routes statiques selon la maquette. Vérifie les routes avec `show ip route` et teste la connectivité des adresses utilisées. Un ping unicast réussi est une condition utile, mais pas une preuve de bon fonctionnement multicast.

### Exemple de base Cisco IOS/IOS XE

Sur chaque routeur, active le routage multicast globalement et PIM Sparse Mode sur les interfaces du chemin multicast : les liens interrouteurs et les interfaces LAN source/récepteur concernés.

```text
ip multicast-routing
!
interface GigabitEthernet0/0
 ip pim sparse-mode
!
interface GigabitEthernet0/1
 ip pim sparse-mode
!
ip pim rp-address 10.255.0.2
```

Cet extrait est volontairement incomplet : il ne configure pas les adresses IP des interfaces, le routage unicast, ni le détail d’OSPF. Adapte le nom des interfaces, et ne copie pas la configuration sans vérifier les commandes disponibles sur l’image de laboratoire. Si le RP utilise Loopback0, assure-toi que son adresse est annoncée et joignable par unicast depuis tous les routeurs concernés.

Dans un vrai laboratoire, les trois routeurs doivent partager le même mapping RP pour ce groupe ASM, et PIM doit être activé sur toutes les interfaces pertinentes. Le multicast routing global ne remplace pas les adjacencies de routage unicast ni les voisins PIM.

### Vérifications

Utilise les commandes qui sont supportées sur la plateforme. Sur de nombreux équipements Cisco IOS/IOS XE, les commandes courantes incluent :

```text
show ip pim neighbor
show ip pim interface
show ip pim rp mapping
show ip igmp groups
show ip mroute
show ip rpf 192.0.2.10
show ip route 192.0.2.10
```

Cherche une séquence logique : hôte récepteur abonné, groupe visible via IGMP, voisins PIM établis, mapping RP présent pour ASM, état multicast correspondant au groupe, interface d’entrée compatible avec RPF et interfaces de sortie attendues. Les sorties exactes et l’orthographe de certaines variantes de commande peuvent différer.


## 12. Méthode de dépannage de bout en bout

Commence par déterminer le périmètre : le problème touche-t-il un seul récepteur, un VLAN entier, toutes les sources ou seulement un groupe ? Note l’adresse source `S`, le groupe `G`, le VLAN récepteur, la plage horaire et le chemin attendu. Une capture simultanée côté source et côté récepteur est souvent plus utile qu’une lecture isolée de la configuration.

**Schéma 15 — Chaîne de diagnostic de bout en bout**

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="400" viewBox="0 0 960 400" role="img" aria-label="Chaîne de livraison multicast de bout en bout"><rect x="0" y="0" width="960" height="400" rx="18" fill="#0b1220" stroke="#31516f" stroke-width="2" /><text x="480" y="32" font-family="Arial,Helvetica,sans-serif" font-size="23" font-weight="700" fill="#f4f7fb" text-anchor="middle">Chaîne de livraison multicast de bout en bout</text><rect x="25" y="139" width="150" height="106" rx="14" fill="#162b45" stroke="#4ade80" stroke-width="2" /><text x="100" y="174" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#4ade80" text-anchor="middle">Émetteur</text><text x="100" y="205" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">192.0.2.10</text><rect x="214" y="139" width="150" height="106" rx="14" fill="#162b45" stroke="#60a5fa" stroke-width="2" /><text x="289" y="174" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#60a5fa" text-anchor="middle">Routeur source</text><text x="289" y="205" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">PIM / RPF</text><rect x="404" y="139" width="150" height="106" rx="14" fill="#162b45" stroke="#67e8f9" stroke-width="2" /><text x="479" y="174" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#67e8f9" text-anchor="middle">Cœur réseau</text><text x="479" y="205" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">PIM / arbre</text><rect x="594" y="139" width="150" height="106" rx="14" fill="#162b45" stroke="#fbbf24" stroke-width="2" /><text x="669" y="174" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#fbbf24" text-anchor="middle">Routeur receveur</text><text x="669" y="205" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">IGMP + PIM</text><rect x="783" y="139" width="150" height="106" rx="14" fill="#162b45" stroke="#f472b6" stroke-width="2" /><text x="858" y="174" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f472b6" text-anchor="middle">Récepteur</text><text x="858" y="205" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#f4f7fb" text-anchor="middle">abonné à G</text><line x1="175" y1="192" x2="214" y2="192" stroke="#4ade80" stroke-width="3" /><polygon points="214.0,192.0 201.0,198.0 201.0,186.0" fill="#4ade80" /><line x1="364" y1="192" x2="404" y2="192" stroke="#60a5fa" stroke-width="3" /><polygon points="404.0,192.0 391.0,198.0 391.0,186.0" fill="#60a5fa" /><line x1="554" y1="192" x2="594" y2="192" stroke="#67e8f9" stroke-width="3" /><polygon points="594.0,192.0 581.0,198.0 581.0,186.0" fill="#67e8f9" /><line x1="744" y1="192" x2="783" y2="192" stroke="#fbbf24" stroke-width="3" /><polygon points="783.0,192.0 770.0,198.0 770.0,186.0" fill="#fbbf24" /><text x="480" y="297" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" fill="#f4f7fb" text-anchor="middle">Tous les maillons doivent être opérationnels : application, LAN, IGMP, PIM, RPF et routage unicast.</text><text x="480" y="329" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="400" fill="#b9c7d8" text-anchor="middle">Le dépannage doit suivre le flux de bout en bout, pas seulement un routeur.</text></svg>

### Étape A — Confirmer le générateur et l’application

Vérifie que l’émetteur produit réellement le flux vers le groupe et le port prévus. Un logiciel peut écouter unicast, choisir une mauvaise interface source, envoyer vers une autre adresse de groupe ou utiliser un TTL trop faible. Confirme la fréquence et le débit, et assure-toi que la capture réseau est effectuée sur la bonne interface.

### Étape B — Confirmer le LAN récepteur

Inspecte l’adhésion IGMP/MLD de l’hôte, le VLAN, le port du switch et l’entrée snooping. Si l’abonnement n’existe pas, le routeur peut ne jamais recevoir l’information nécessaire pour rejoindre l’arbre. Vérifie le querier et les temporisateurs ; les tables peuvent ne pas refléter un client si celui-ci est inactif ou si le groupe n’est plus rejoint.

### Étape C — Confirmer le routeur multicast

Sur le routeur de dernier saut (LHR), regarde l’état IGMP, l’état `(*,G)` ou `(S,G)`, la liste des interfaces de sortie et le mapping RP si le groupe utilise ASM. Sur le routeur côté source (FHR), confirme l’arrivée des paquets sur la bonne interface et la présence des éléments requis pour les enregistrer ou les acheminer. Inspecte ensuite chaque saut du chemin.

### Étape D — Vérifier PIM et RPF

Confirme les voisins PIM sur les liens concernés, les interfaces en mode approprié et la cohérence du plan de routage unicast. Si RPF échoue, compare la route attendue vers la source (ou le RP dans le cas concerné) avec l’interface d’entrée effective du paquet multicast. Les routes asymétriques, les routes statiques ou une politique de routage différente peuvent être responsables.

### Étape E — Vérifier les filtres et contraintes

Contrôle les ACL, les limites de portée multicast, les règles de groupe autorisé, le TTL IPv4 ou le Hop Limit IPv6, ainsi que les fonctions de sécurité du LAN. Cherche aussi les erreurs d’interface, une saturation, des pertes, des compteurs QoS, ou une incompatibilité entre versions IGMP et capacités snooping. Une application qui n’écoute pas sur le bon groupe peut produire un symptôme ressemblant à une panne réseau.

### Matrice de diagnostic rapide

| Symptôme | Hypothèses prioritaires | Premier contrôle |
|---|---|---|
| Aucune réception sur tous les récepteurs | Source muette, mauvais groupe, RP absent ou PIM incomplet | Capture source, RP mapping, table mroute |
| Un seul VLAN ne reçoit pas | IGMP, snooping, PIM sur SVI, ACL locale | Groupes IGMP et table snooping du VLAN |
| Réception intermittente | Temporisateurs, perte de voisinage, convergence, saturation | Logs, voisins PIM, compteurs d’interface |
| Seuls certains routeurs reçoivent le flux | RPF, route unicast, arbre incomplet | `show ip rpf`, `show ip mroute` |
| Le flux est visible au switch mais pas à l’application | Groupe/port ou filtre hôte, traitement L3 | Capture avec filtre `ip.dst == G` et port UDP |
| Trop de ports reçoivent le flux | Snooping absent ou inefficace, groupe inconnu | Table snooping, ports routeurs, querier |
| IPv4 fonctionne mais IPv6 échoue | MLD snooping, routage multicast IPv6, ACL IPv6 | Tables MLD et commandes IPv6 de la plateforme |


## 13. Erreurs fréquentes et bonnes pratiques

1. **Confondre IGMP et PIM.** IGMP signale les abonnements locaux ; PIM construit la distribution entre routeurs.
2. **Activer PIM sans vérifier le routage unicast.** RPF dépend des routes ; une configuration de voisinage PIM ne garantit pas un arbre utilisable.
3. **Supposer qu’un RP est requis pour tous les modèles.** Un RP est au cœur du PIM-SM ASM ; SSM est basé sur la paire source/groupe et n’a habituellement pas besoin de RP pour ces canaux.
4. **Penser que snooping et routage multicast sont la même fonction.** Snooping limite la livraison L2 ; il ne remplace pas PIM sur les liens L3.
5. **Ne pas vérifier le querier.** Les états d’adhésion expirent. Le fonctionnement précis est dépendant de l’implémentation et du VLAN.
6. **Utiliser `239/8` comme si cela chiffrait le contenu.** La portée administrative n’est pas une barrière cryptographique.
7. **Oublier le TTL et les ACL.** Les paquets peuvent être correctement émis mais ne jamais traverser la limite prévue.
8. **Activer un fallback dense sans mesurer le risque.** Certains mécanismes de mode mixte peuvent provoquer une inondation si un mapping RP est absent ; la documentation de la plateforme doit être suivie.

### Hygiène opérationnelle

- Maintiens un inventaire des applications multicast, groupes, sources, VLAN et propriétaires.
- Évite d’utiliser la même plage de groupes pour des applications non liées dans le même domaine.
- Documente RP, BSR/Auto-RP le cas échéant, frontières et scopes.
- Contrôle les états après une panne, une mise à jour, un changement de VLAN ou une modification des routes unicast.
- Mesure le débit et les pertes ; ne confonds pas la présence d’une entrée multicast avec l’expérience applicative.
- Utilise un laboratoire pour les changements de mode, de RP et de politiques avant production.


## 14. Laboratoire de dépannage : trouver le point de rupture

### Scénario

Le flux `192.0.2.10 → 239.1.1.1` doit atteindre un récepteur dans `203.0.113.0/24`. Le récepteur ne reçoit rien. La topologie est celle du laboratoire précédent. Le routage unicast fonctionne entre les routeurs.

### Parcours de vérification

1. Vérifie avec une capture que la source transmet vers `239.1.1.1` et que le TTL est suffisant.
2. Vérifie que l’hôte récepteur a rejoint `239.1.1.1` et que le switch connaît le port membre.
3. Vérifie la présence d’un querier sur le VLAN récepteur, si nécessaire.
4. Vérifie que R3 apprend l’adhésion et qu’il y a un état multicast pour le groupe.
5. Vérifie le mapping RP et la joignabilité unicast de `10.255.0.2`.
6. Vérifie que les voisins PIM sont présents sur R1–R2 et R2–R3.
7. Vérifie RPF sur le chemin vers la source et vers le RP selon l’état examiné.
8. Contrôle les ACL et les compteurs d’interface.
9. Si le routeur envoie le trafic vers le VLAN et que l’hôte ne reçoit toujours rien, capture côté switch/hôte pour isoler la couche L2 ou applicative.

### Questions

- Quelle différence fais-tu entre une panne d’adhésion IGMP et une panne RPF ?
- Pourquoi un ping unicast vers `192.0.2.10` ne prouve-t-il pas que le multicast fonctionnera ?
- Quel état cherches-tu d’abord pour un groupe ASM PIM-SM et pourquoi ?
- Pourquoi l’absence de querier peut-elle faire disparaître une entrée snooping après un certain temps ?
- Quelle est la différence entre un port routeur appris par snooping et un port membre du groupe ?

### Corrigé synthétique

- Une panne IGMP se manifeste souvent par l’absence de groupe côté LAN récepteur et/ou l’absence de port membre dans la table snooping. Une panne RPF présente plutôt un chemin d’entrée incompatible avec la route attendue vers la source ou le RP.
- Le ping teste un trafic unicast différent ; il ne valide ni PIM, ni l’adhésion de groupe, ni la réplication du flux.
- Pour ASM avec PIM-SM, vérifier le mapping RP et les états `(*,G)`/`(S,G)` est un bon point de départ, tout en gardant la source et le récepteur dans l’analyse.
- Sans requêtes périodiques, l’état d’adhésion peut expirer suivant les timers et l’implémentation.
- Un port routeur permet de transmettre le multicast en direction d’un routeur multicast ; un port membre correspond à un segment où les récepteurs ont signalé leur intérêt pour un groupe.


## 15. Quiz de validation

**1. À quoi sert IGMP en IPv4 ?**

A. À remplacer OSPF
B. À signaler l’intérêt des hôtes pour des groupes multicast à un routeur local
C. À attribuer des adresses IP
D. À chiffrer le contenu multicast

**2. Quel est le rôle de l’IGMP snooping ?**

A. Construire les arbres entre tous les routeurs
B. Limiter la distribution L2 selon les adhésions observées
C. Remplacer le querier
D. Créer l’adresse multicast source

**3. Qu’est-ce que PIM-SM utilise généralement pour construire l’arbre partagé ASM ?**

A. Un RP
B. Un serveur DHCP
C. Une adresse MAC unicast
D. Un serveur DNS

**4. Que signifie RPF ?**

A. Que le paquet a été chiffré
B. Que l’entrée du paquet correspond au chemin attendu vers la source ou le RP selon l’état
C. Que le groupe multicast est réservé
D. Que le switch a désactivé le snooping

**5. Quel est le repère courant pour les groupes SSM IPv4 ?**

A. `127.0.0.0/8`
B. `232.0.0.0/8`
C. `169.254.0.0/16`
D. `192.0.2.0/24`

**6. Quel protocole est utilisé par les hôtes IPv6 pour signaler leurs adhésions multicast ?**

A. IGMPv2
B. ARP
C. MLD
D. DHCPv4

**7. Une route unicast vers la source existe, mais le multicast échoue au contrôle RPF. Quelle est la première vérification ?**

A. Comparer l’interface d’entrée réelle à l’interface attendue par la route RPF
B. Changer le port UDP sans mesurer
C. Désactiver toutes les ACL
D. Redémarrer tous les switches

**8. La plage `239.0.0.0/8` apporte-t-elle du chiffrement ?**

A. Oui
B. Non, elle est administrativement délimitée mais n’est pas une protection cryptographique
C. Oui, uniquement en IPv6
D. Seulement si IGMPv2 est activé

**9. PIM est dit « protocol independent » parce que :**

A. Il ne dépend d’aucune information unicast pour RPF
B. Il peut utiliser plusieurs protocoles de routage unicast pour obtenir les informations nécessaires au RPF
C. Il remplace tous les protocoles unicast
D. Il ne fonctionne que sur Ethernet

**10. Quelles vérifications sont pertinentes si un groupe est visible côté routeur mais pas dans l’application ?**

A. Groupe/port applicatif, TTL, ACL, OIL, capture et livraison sur le LAN
B. Seulement l’adresse de gestion du switch
C. Seulement le mot de passe SSH
D. La couleur de l’interface

### Réponses

1. B — IGMP signale l’adhésion des hôtes IPv4.
2. B — Le snooping limite la livraison dans le VLAN selon les rapports observés.
3. A — Le RP est central dans le PIM-SM ASM.
4. B — RPF vérifie le chemin d’entrée attendu.
5. B — `232.0.0.0/8` est le repère SSM IPv4 usuel.
6. C — MLD gère l’adhésion multicast IPv6.
7. A — Compare la route RPF et l’interface d’entrée réelle.
8. B — Une plage administrative ne chiffre pas les données.
9. B — PIM ne dépend pas d’un protocole unicast particulier, mais s’appuie normalement sur les informations RPF de routage.
10. A — Suivre l’application et le chemin de données de bout en bout est essentiel.


## 16. Glossaire

| Terme | Définition |
|---|---|
| ASM | Any-Source Multicast : le récepteur demande un groupe sans préciser une source particulière au niveau de l’abonnement |
| FHR | First-Hop Router : routeur au voisinage du réseau source |
| G | Adresse IP de groupe multicast |
| IGMP | Protocole IPv4 de gestion des adhésions aux groupes multicast |
| IIF | Interface d’entrée attendue pour un état multicast |
| LHR | Last-Hop Router : routeur au voisinage du réseau récepteur |
| MLD | Protocole IPv6 de découverte et gestion des auditeurs multicast |
| OIL | Outgoing Interface List : interfaces de sortie d’un état multicast |
| PIM | Protocol Independent Multicast, famille de protocoles de routage multicast |
| RP | Rendezvous Point, point de rendez-vous utilisé notamment par PIM-SM ASM |
| RPF | Reverse Path Forwarding, contrôle du chemin d’arrivée attendu |
| S | Adresse IP source multicast |
| SSM | Source-Specific Multicast, modèle où le canal est identifié par une source et un groupe |
| SPT | Shortest Path Tree, arbre spécifique à une source dans PIM-SM lorsque le routeur y bascule |
| Snooping | Observation des messages IGMP/MLD par un switch afin de contrôler le transfert L2 |
| TTL | IPv4 Time To Live, limite de nombre de sauts d’un paquet |


## 17. Checklist avant mise en production

- [ ] Les groupes et les sources sont recensés, justifiés et attribués selon le plan d’adressage.
- [ ] Le routage unicast est stable entre les sources, les récepteurs et les RPs concernés.
- [ ] Le mode PIM choisi correspond au besoin ASM/SSM et au support des équipements.
- [ ] Les mappings RP sont cohérents pour tous les groupes concernés.
- [ ] Les interfaces de transit et les interfaces LAN requises ont les fonctions multicast activées.
- [ ] RPF fonctionne vers la source ou le RP selon l’état examiné.
- [ ] Le querier, IGMP/MLD et le snooping sont testés sur les VLAN récepteurs.
- [ ] Les ACL, boundaries, TTL/Hop Limit et règles de sécurité sont documentés.
- [ ] Les compteurs et captures montrent une livraison correcte à la source, au cœur et au récepteur.
- [ ] La réaction à une panne de lien, de routeur ou de RP a été testée dans le laboratoire.
- [ ] Les commandes et procédures sont confirmées pour la version logicielle et le modèle d’équipement déployés.


## Références techniques

- Cisco, *Multicast Configuration Guide — Basic IP Multicast Routing, Cisco IOS XE 17* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/multicast/multicast-configuration-guide/ip-multicast-routing.html
- Cisco, *Multicast Configuration Guide — PIM, Cisco IOS XE 17* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/multicast/multicast-configuration-guide/pim.html
- Cisco, *Multicast Configuration Guide — IGMP, Cisco IOS XE 17* : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/multicast/multicast-configuration-guide/igmp.html
- IETF, RFC 7761, *Protocol Independent Multicast — Sparse Mode (PIM-SM): Protocol Specification (Revised)* : https://www.rfc-editor.org/rfc/rfc7761.html
- IETF, RFC 9776, *Internet Group Management Protocol, Version 3* (mars 2025, remplace RFC 3376) : https://www.rfc-editor.org/rfc/rfc9776.html
- IETF, RFC 4607, *Source-Specific Multicast for IP* : https://www.rfc-editor.org/rfc/rfc4607.html
- IETF, RFC 1112, *Host Extensions for IP Multicasting* : https://www.rfc-editor.org/rfc/rfc1112.html
- IETF, RFC 4541, *Considerations for IGMP and MLD Snooping Switches* : https://www.rfc-editor.org/rfc/rfc4541.html

> **Règle de production :** confirmer les commandes, limitations matérielles, groupes réservés, minuteries et mécanismes de redondance dans le guide correspondant à la version réellement utilisée. Les extraits de configuration de ce cours servent à l’apprentissage, pas à une copie aveugle sur un réseau de production.
