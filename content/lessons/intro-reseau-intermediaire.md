
# Qu'est-ce qu'un réseau informatique ? — Niveau intermédiaire

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Prérequis :** connaître les adresses IP, les rôles du switch et du routeur, ainsi que les principaux protocoles réseau.  
> **Objectif :** comprendre les mécanismes de communication, calculer des sous-réseaux, expliquer les VLAN et le routage, puis diagnostiquer une panne à partir de preuves.

---

## Sommaire

1. Contexte et objectifs
2. Les modèles OSI et TCP/IP
3. Ethernet et les adresses MAC
4. IPv4 et calcul des sous-réseaux
5. VLAN et segmentation de couche 2
6. Routage et table de routage
7. DHCP, DNS, ARP et NDP
8. TCP, UDP et ports
9. Wi-Fi, MTU et performances
10. Méthode de dépannage structurée
11. Atelier pratique
12. Étude de panne
13. Évaluation corrigée
14. Préparation du niveau expert

---

# 1. Contexte et objectifs

## 1.1 Approfondir les fondations

Au niveau débutant, nous avons vu qu'un réseau relie des équipements et que les protocoles organisent leurs échanges.

Au niveau intermédiaire, nous devons comprendre plus précisément comment une donnée traverse les couches réseau, comment une adresse IP est interprétée, comment les VLAN séparent les domaines de couche 2 et comment les routeurs choisissent un chemin.

Nous allons également apprendre à diagnostiquer les incidents sans nous limiter à un seul test.

## 1.2 Objectifs pédagogiques

À la fin de ce cours, vous serez capable de :

- expliquer les modèles OSI et TCP/IP ;
- distinguer une trame Ethernet d'un paquet IP ;
- interpréter une adresse IPv4 avec son préfixe ;
- calculer un sous-réseau simple ;
- comprendre le rôle des VLAN et des trunks ;
- expliquer le routage inter-réseaux ;
- comprendre l'attribution DHCP et la résolution DNS ;
- différencier TCP et UDP à partir de leurs propriétés ;
- expliquer le rôle d'ARP et NDP ;
- identifier des causes possibles de panne ;
- suivre une méthode de dépannage fondée sur des observations vérifiables.

---

# 2. Les modèles OSI et TCP/IP

## 2.1 Pourquoi utiliser un modèle en couches ?

Les communications réseau combinent plusieurs responsabilités : transmettre des signaux, transporter des trames, acheminer des paquets et permettre aux applications d'échanger des données.

Les modèles en couches permettent de classer ces responsabilités. Ils facilitent l'apprentissage, la conception et l'identification des causes possibles d'une panne.

Le modèle OSI décrit sept couches théoriques. La suite TCP/IP regroupe les fonctions selon une organisation utilisée par les protocoles Internet.

## 2.2 Les sept couches OSI

| Couche | Nom | Responsabilité indicative | Exemples |
|---|---|---|---|
| 7 | Application | Services utilisés par les applications | HTTP, DNS, DHCP |
| 6 | Présentation | Représentation, encodage et transformations des données | Encodage, formats de données |
| 5 | Session | Organisation logique de certaines sessions | Fonctions de session selon les systèmes |
| 4 | Transport | Communication de bout en bout entre applications | TCP, UDP |
| 3 | Réseau | Adressage et acheminement entre réseaux | IPv4, IPv6, ICMP |
| 2 | Liaison de données | Transmission de trames sur un lien | Ethernet, Wi-Fi |
| 1 | Physique | Transmission des signaux sur le support | Cuivre, fibre, radio |

Cette correspondance est pédagogique : certains protocoles réels réunissent plusieurs responsabilités et ne se rangent pas toujours parfaitement dans une seule couche.

## 2.3 Correspondance simplifiée avec TCP/IP

| Organisation TCP/IP | Fonction | Couches OSI souvent associées |
|---|---|---|
| Application | Protocoles utilisés par les applications | 5 à 7 |
| Transport | Communication entre processus | 4 |
| Internet | Adressage et routage IP | 3 |
| Accès réseau | Transmission sur le lien | 1 et 2 |

## 2.4 Schéma des couches

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="395" viewBox="0 0 960 395" role="img" aria-labelledby="osi-title osi-desc">
  <title id="osi-title">Modèle OSI en sept couches</title>
  <desc id="osi-desc">Sept couches sont disposées de l'application au support physique. Les couches hautes représentent les fonctions proches des applications et les couches basses celles liées au transport réseau. Les tirets animés indiquent le parcours conceptuel sans boule mobile.</desc>
  <defs>
    <marker id="osi-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .osi-box{fill:#17263a;stroke:#60a5fa;stroke-width:1.5}
      .osi-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .osi-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .osi-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:7 7;marker-end:url(#osi-arrow);animation:osi-dash 1.8s linear infinite}
      @keyframes osi-dash{to{stroke-dashoffset:-28}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="393" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="30" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">LES COUCHES SÉPARENT LES RESPONSABILITÉS</text>
  <rect class="osi-box" x="55" y="48" width="540" height="39" rx="7"/>
  <text class="osi-title" x="75" y="72">7 — Application</text><text class="osi-text" x="360" y="72">Services applicatifs</text>
  <rect class="osi-box" x="55" y="92" width="540" height="39" rx="7"/>
  <text class="osi-title" x="75" y="116">6 — Présentation</text><text class="osi-text" x="360" y="116">Représentation des données</text>
  <rect class="osi-box" x="55" y="136" width="540" height="39" rx="7"/>
  <text class="osi-title" x="75" y="160">5 — Session</text><text class="osi-text" x="360" y="160">Organisation des échanges</text>
  <rect class="osi-box" x="55" y="180" width="540" height="39" rx="7"/>
  <text class="osi-title" x="75" y="204">4 — Transport</text><text class="osi-text" x="360" y="204">TCP / UDP et ports</text>
  <rect class="osi-box" x="55" y="224" width="540" height="39" rx="7"/>
  <text class="osi-title" x="75" y="248">3 — Réseau</text><text class="osi-text" x="360" y="248">Adresses IP et routage</text>
  <rect class="osi-box" x="55" y="268" width="540" height="39" rx="7"/>
  <text class="osi-title" x="75" y="292">2 — Liaison</text><text class="osi-text" x="360" y="292">Trames et adresses MAC</text>
  <rect class="osi-box" x="55" y="312" width="540" height="39" rx="7"/>
  <text class="osi-title" x="75" y="336">1 — Physique</text><text class="osi-text" x="360" y="336">Signaux et supports</text>
  <path class="osi-flow" d="M630 68 V330"/>
  <text class="osi-text" x="670" y="120">Proche de</text>
  <text class="osi-text" x="670" y="140">l'application</text>
  <text class="osi-text" x="670" y="246">Adressage</text>
  <text class="osi-text" x="670" y="266">et transfert</text>
  <text class="osi-text" x="670" y="322">Support de</text>
  <text class="osi-text" x="670" y="342">transmission</text>
  <text class="osi-text" x="480" y="376" text-anchor="middle">Un incident doit être localisé par des tests, pas déduit d'une seule couche supposée.</text>
</svg>

## 2.5 Encapsulation et décapsulation

À l'émission, les couches ajoutent les informations nécessaires à la communication. À la réception, les couches interprètent ces informations et remettent les données à la fonction suivante.

On parle généralement :

- de données applicatives ;
- de segment TCP ou de datagramme UDP ;
- de paquet IP ;
- de trame Ethernet ou Wi-Fi ;
- de bits ou signaux sur le support.

La terminologie dépend du protocole, et certains mécanismes modifient ou ajoutent les informations au cours du trajet.

Un routeur, par exemple, retire les informations de couche liaison associées au lien entrant, traite le paquet IP, puis utilise une nouvelle encapsulation de couche liaison pour le lien sortant.

---

# 3. Ethernet et les adresses MAC

## 3.1 Les trames Ethernet

Ethernet définit notamment un format de trame et des mécanismes de transmission sur un réseau local.

Une trame Ethernet comporte des champs qui permettent d'identifier les adresses de couche liaison source et destination, le protocole encapsulé et la charge utile.

Les équipements traitent les trames à partir de leurs fonctions et de leur configuration.

## 3.2 Apprentissage de la table MAC

Un switch de couche 2 apprend généralement l'adresse MAC source d'une trame et l'associe au port et au VLAN où elle a été observée.

Exemple conceptuel :

| VLAN | Adresse MAC | Port |
|---|---|---|
| 10 | `02:00:00:00:00:10` | Gi1/0/1 |
| 10 | `02:00:00:00:00:20` | Gi1/0/2 |
| 20 | `02:00:00:00:00:30` | Gi1/0/3 |

Ces adresses sont fictives. Une véritable table MAC peut évoluer au fil du temps, car les entrées dynamiques expirent ou sont mises à jour.

La table MAC est associée au VLAN. Une même adresse apparente ne doit pas être interprétée sans tenir compte du contexte de commutation.

## 3.3 Unicast, broadcast et multicast

- **Unicast :** communication destinée à un destinataire précis.
- **Broadcast :** diffusion vers tous les équipements concernés du domaine de broadcast, selon le protocole.
- **Multicast :** communication vers un groupe de destinataires qui rejoint ou traite ce groupe.

Un broadcast Ethernet de couche 2 ne traverse normalement pas un routeur comme une diffusion ordinaire. Des mécanismes spécifiques, configurés explicitement, peuvent toutefois relayer certains types de messages.

---

# 4. IPv4 et calcul des sous-réseaux

## 4.1 Comprendre un préfixe CIDR

Une adresse IPv4 est constituée de 32 bits. Le préfixe indique combien de bits sont consacrés à la partie réseau.

Exemple :

```text
192.168.10.34/24
```

Le préfixe `/24` correspond au masque `255.255.255.0`.

Dans cet exemple :

- Adresse : `192.168.10.34`
- Réseau : `192.168.10.0/24`
- Broadcast : `192.168.10.255`
- Plage d'hôtes classique : `192.168.10.1` à `192.168.10.254`

Cette interprétation concerne un sous-réseau IPv4 conventionnel. Des cas particuliers, notamment certains préfixes point à point, obéissent à des règles différentes.

## 4.2 Pourquoi découper un réseau en sous-réseaux ?

Le découpage permet de définir des domaines IP distincts, d'organiser l'adressage et de mieux maîtriser le routage et les politiques de sécurité.

Une entreprise peut affecter des plages différentes à ses utilisateurs, serveurs, équipements de gestion et systèmes invités.

Le choix des préfixes doit tenir compte du nombre d'adresses, de la croissance attendue, des sites et des réseaux auxquels il faudra se connecter.

## 4.3 Méthode de calcul

Pour un sous-réseau IPv4 conventionnel, le nombre de bits disponibles pour les hôtes vaut :

\[
h = 32 - p
\]

où \(p\) représente la longueur du préfixe.

Le nombre classique d'adresses d'hôtes utilisables pour un sous-réseau standard est :

\[
N = 2^h - 2
\]

Cette formule ne doit pas être appliquée aveuglément aux préfixes spéciaux. Par exemple, un `/31` peut être utilisé sur des liens point à point selon les règles applicables.

## 4.4 Exemple : un réseau `/26`

Considérons :

```text
192.168.10.0/26
```

Le préfixe laisse 6 bits pour les hôtes.

Le bloc contient \(2^6 = 64\) adresses. Dans le cas conventionnel, 62 adresses sont utilisables pour les hôtes.

La plage est :

- Adresse réseau : `192.168.10.0`
- Première adresse d'hôte : `192.168.10.1`
- Dernière adresse d'hôte : `192.168.10.62`
- Broadcast : `192.168.10.63`

Le bloc suivant de même taille commence à `192.168.10.64`.

## 4.5 Autres tailles courantes

| Préfixe | Masque IPv4 | Nombre total d'adresses | Hôtes utilisables, cas conventionnel |
|---|---|---:|---:|
| `/24` | `255.255.255.0` | 256 | 254 |
| `/25` | `255.255.255.128` | 128 | 126 |
| `/26` | `255.255.255.192` | 64 | 62 |
| `/27` | `255.255.255.224` | 32 | 30 |
| `/28` | `255.255.255.240` | 16 | 14 |
| `/29` | `255.255.255.248` | 8 | 6 |
| `/30` | `255.255.255.252` | 4 | 2 |

Ces nombres servent au dimensionnement conventionnel d'hôtes IPv4. Ils ne constituent pas à eux seuls une recommandation de conception.

## 4.6 Exemple de découpage d'un `/24`

Le réseau `192.168.20.0/24` est découpé en quatre sous-réseaux `/26`.

| Sous-réseau | Première adresse utilisable | Dernière adresse utilisable | Broadcast |
|---|---|---|---|
| `192.168.20.0/26` | `.1` | `.62` | `.63` |
| `192.168.20.64/26` | `.65` | `.126` | `.127` |
| `192.168.20.128/26` | `.129` | `.190` | `.191` |
| `192.168.20.192/26` | `.193` | `.254` | `.255` |

Chaque sous-réseau comporte 64 adresses, dont 62 sont utilisables comme adresses d'hôtes dans le cas conventionnel.

## 4.7 Schéma de découpage

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="350" viewBox="0 0 960 350" role="img" aria-labelledby="subnet-title subnet-desc">
  <title id="subnet-title">Découpage d'un réseau IPv4 en quatre sous-réseaux</title>
  <desc id="subnet-desc">Le réseau 192.168.20.0 sur 24 est divisé en quatre blocs de 64 adresses, chacun correspondant à un préfixe /26. Les quatre blocs sont distincts et contigus.</desc>
  <defs>
    <style>
      .sn-a{fill:#18314d;stroke:#60a5fa;stroke-width:2}
      .sn-b{fill:#193629;stroke:#4ade80;stroke-width:2}
      .sn-c{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .sn-d{fill:#302044;stroke:#c4b5fd;stroke-width:2}
      .sn-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .sn-text{font:12px Arial,sans-serif;fill:#cbd5e1}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="348" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">UN /24 DÉCOUPÉ EN QUATRE BLOCS /26</text>
  <text class="sn-text" x="480" y="65" text-anchor="middle">Réseau parent : 192.168.20.0/24 · 256 adresses</text>
  <rect class="sn-a" x="25" y="92" width="220" height="118" rx="10"/>
  <text class="sn-title" x="135" y="122" text-anchor="middle">Sous-réseau 1</text>
  <text class="sn-text" x="135" y="148" text-anchor="middle">192.168.20.0/26</text>
  <text class="sn-text" x="135" y="171" text-anchor="middle">.0 à .63</text>
  <text class="sn-text" x="135" y="190" text-anchor="middle">64 adresses</text>
  <rect class="sn-b" x="260" y="92" width="220" height="118" rx="10"/>
  <text class="sn-title" x="370" y="122" text-anchor="middle">Sous-réseau 2</text>
  <text class="sn-text" x="370" y="148" text-anchor="middle">192.168.20.64/26</text>
  <text class="sn-text" x="370" y="171" text-anchor="middle">.64 à .127</text>
  <text class="sn-text" x="370" y="190" text-anchor="middle">64 adresses</text>
  <rect class="sn-c" x="495" y="92" width="220" height="118" rx="10"/>
  <text class="sn-title" x="605" y="122" text-anchor="middle">Sous-réseau 3</text>
  <text class="sn-text" x="605" y="148" text-anchor="middle">192.168.20.128/26</text>
  <text class="sn-text" x="605" y="171" text-anchor="middle">.128 à .191</text>
  <text class="sn-text" x="605" y="190" text-anchor="middle">64 adresses</text>
  <rect class="sn-d" x="730" y="92" width="205" height="118" rx="10"/>
  <text class="sn-title" x="832" y="122" text-anchor="middle">Sous-réseau 4</text>
  <text class="sn-text" x="832" y="148" text-anchor="middle">192.168.20.192/26</text>
  <text class="sn-text" x="832" y="171" text-anchor="middle">.192 à .255</text>
  <text class="sn-text" x="832" y="190" text-anchor="middle">64 adresses</text>
  <path d="M25 238 H935" stroke="#64748b" stroke-width="2"/>
  <text class="sn-text" x="480" y="270" text-anchor="middle">Chaque bloc possède son adresse réseau et son broadcast.</text>
  <text class="sn-text" x="480" y="294" text-anchor="middle">Dans ce cas conventionnel, il reste 62 adresses utilisables par bloc.</text>
  <text class="sn-text" x="480" y="318" text-anchor="middle">Choisissez les préfixes selon les besoins et les politiques d'adressage.</text>
</svg>

---

# 5. VLAN et segmentation de couche 2

## 5.1 Pourquoi utiliser des VLAN ?

Un VLAN permet de séparer logiquement des équipements en domaines de commutation distincts sur une infrastructure compatible.

Par exemple, les ports des utilisateurs et ceux des serveurs peuvent appartenir à des VLAN différents, même s'ils utilisent une partie de la même infrastructure physique.

Cette segmentation aide à organiser le réseau, à limiter certains domaines de broadcast et à appliquer des politiques entre segments.

Un VLAN n'est pas, à lui seul, une politique de sécurité complète. Les communications entre VLAN doivent être contrôlées par le routage, les ACL ou d'autres mécanismes appropriés.

## 5.2 Ports access et trunks

Un port access transporte généralement le trafic d'un seul VLAN pour un terminal.

Un trunk transporte plusieurs VLAN entre des équipements compatibles, souvent au moyen de marquages IEEE 802.1Q.

L'encapsulation et la configuration doivent correspondre aux deux extrémités de la liaison. Une incohérence peut provoquer la perte de trafic ou son placement dans un VLAN inattendu.

## 5.3 Schéma de segmentation

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="365" viewBox="0 0 960 365" role="img" aria-labelledby="vlan-title vlan-desc">
  <title id="vlan-title">Segmentation logique par VLAN</title>
  <desc id="vlan-desc">Deux groupes de terminaux appartiennent à des VLAN distincts sur une infrastructure de commutation. Une liaison trunk transporte les VLAN entre switches. Un routeur ou un switch de couche 3 est nécessaire pour permettre les communications entre sous-réseaux selon la politique de sécurité.</desc>
  <defs>
    <marker id="vlan-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .vl-user{fill:#17314d;stroke:#60a5fa;stroke-width:2}
      .vl-server{fill:#123126;stroke:#4ade80;stroke-width:2}
      .vl-switch{fill:#292542;stroke:#c4b5fd;stroke-width:2}
      .vl-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .vl-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .vl-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#vlan-arrow);animation:vl-dash 1.8s linear infinite}
      @keyframes vl-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="363" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DEUX VLAN SUR UNE INFRASTRUCTURE COMMUNE</text>
  <rect class="vl-user" x="25" y="75" width="210" height="74" rx="10"/>
  <text class="vl-title" x="130" y="104" text-anchor="middle">Terminaux</text>
  <text class="vl-text" x="130" y="127" text-anchor="middle">VLAN 10 — Utilisateurs</text>
  <rect class="vl-switch" x="285" y="130" width="180" height="85" rx="10"/>
  <text class="vl-title" x="375" y="164" text-anchor="middle">Switch A</text>
  <text class="vl-text" x="375" y="188" text-anchor="middle">Ports access + trunk</text>
  <rect class="vl-switch" x="535" y="130" width="180" height="85" rx="10"/>
  <text class="vl-title" x="625" y="164" text-anchor="middle">Switch B</text>
  <text class="vl-text" x="625" y="188" text-anchor="middle">VLAN autorisés</text>
  <rect class="vl-server" x="755" y="75" width="180" height="74" rx="10"/>
  <text class="vl-title" x="845" y="104" text-anchor="middle">Serveurs</text>
  <text class="vl-text" x="845" y="127" text-anchor="middle">VLAN 20 — Serveurs</text>
  <path class="vl-flow" d="M235 112 L277 150"/>
  <path class="vl-flow" d="M465 172 H527"/>
  <path class="vl-flow" d="M715 150 L747 112"/>
  <text class="vl-text" x="500" y="244" text-anchor="middle">Trunk : seuls les VLAN autorisés doivent être transportés.</text>
  <rect class="vl-user" x="140" y="275" width="680" height="55" rx="10"/>
  <text class="vl-title" x="480" y="298" text-anchor="middle">Communication entre VLAN</text>
  <text class="vl-text" x="480" y="317" text-anchor="middle">Nécessite du routage et des règles qui autorisent les flux requis.</text>
</svg>

## 5.4 Routage inter-VLAN

Deux VLAN différents correspondent généralement à des sous-réseaux IP distincts. Pour que des hôtes de ces sous-réseaux communiquent, il faut une fonction de routage et des règles de sécurité adaptées.

Le routage peut être fourni par un routeur ou par un switch de couche 3.

Le fait de connecter deux VLAN à un même switch ne suffit pas à les rendre communicants au niveau IP.

---

# 6. Routage et table de routage

## 6.1 Le rôle d'une table de routage

Un routeur choisit un chemin en consultant sa table de routage.

Une entrée peut indiquer :

- un préfixe de destination ;
- un prochain saut ;
- une interface de sortie ;
- des propriétés de préférence ou de coût selon le protocole et la plateforme.

Le routeur recherche normalement la route la plus spécifique correspondant à l'adresse de destination, selon le principe du préfixe le plus long.

## 6.2 Exemple

Une table simplifiée peut contenir :

```text
Destination       Prochain saut
192.168.10.0/24   directement connecté
192.168.20.0/24   10.0.0.2
0.0.0.0/0         10.0.0.1
```

Ces entrées sont fictives et illustrent uniquement le concept.

La route `0.0.0.0/0` est une route par défaut IPv4 : elle correspond aux destinations qui ne correspondent à aucune route plus spécifique.

Une route directement connectée correspond à un réseau attaché à une interface du routeur, selon l'état et la configuration de celle-ci.

## 6.3 Route statique et route dynamique

Une route statique est configurée explicitement par un administrateur ou un outil d'automatisation.

Un protocole de routage dynamique permet aux routeurs d'échanger des informations de joignabilité et de sélectionner les routes selon ses règles.

Exemples de protocoles de routage :

- OSPF ;
- IS-IS ;
- BGP ;
- RIP dans certains environnements limités ou historiques.

Chaque protocole a ses règles de calcul, ses usages et ses limites.

## 6.4 Schéma de routage

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="345" viewBox="0 0 960 345" role="img" aria-labelledby="routing-title routing-desc">
  <title id="routing-title">Routage entre deux réseaux IP</title>
  <desc id="routing-desc">Un poste dans le réseau A envoie un paquet vers la passerelle. Le routeur consulte sa table et transmet le paquet vers le réseau B. Les flèches animées indiquent le chemin logique, sans objet mobile.</desc>
  <defs>
    <marker id="rt-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .rt-net{fill:#17314d;stroke:#60a5fa;stroke-width:2}
      .rt-router{fill:#123126;stroke:#4ade80;stroke-width:2}
      .rt-title{font:700 15px Arial,sans-serif;fill:#f8fafc}
      .rt-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .rt-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#rt-arrow);animation:rt-dash 1.8s linear infinite}
      @keyframes rt-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="343" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">LE ROUTEUR RELIE DES PRÉFIXES DIFFÉRENTS</text>
  <rect class="rt-net" x="30" y="95" width="245" height="120" rx="12"/>
  <text class="rt-title" x="152" y="126" text-anchor="middle">Réseau A</text>
  <text class="rt-text" x="152" y="151" text-anchor="middle">192.168.10.0/24</text>
  <text class="rt-text" x="152" y="174" text-anchor="middle">PC : 192.168.10.20</text>
  <text class="rt-text" x="152" y="196" text-anchor="middle">Passerelle : .1</text>
  <rect class="rt-router" x="360" y="95" width="240" height="120" rx="12"/>
  <text class="rt-title" x="480" y="126" text-anchor="middle">Routeur</text>
  <text class="rt-text" x="480" y="151" text-anchor="middle">Table de routage</text>
  <text class="rt-text" x="480" y="174" text-anchor="middle">Choix du prochain saut</text>
  <text class="rt-text" x="480" y="196" text-anchor="middle">Interfaces de sortie</text>
  <rect class="rt-net" x="685" y="95" width="245" height="120" rx="12"/>
  <text class="rt-title" x="807" y="126" text-anchor="middle">Réseau B</text>
  <text class="rt-text" x="807" y="151" text-anchor="middle">192.168.20.0/24</text>
  <text class="rt-text" x="807" y="174" text-anchor="middle">Serveur : 192.168.20.30</text>
  <text class="rt-text" x="807" y="196" text-anchor="middle">Passerelle : .1</text>
  <path class="rt-flow" d="M275 155 H352"/>
  <path class="rt-flow" d="M600 155 H677"/>
  <text class="rt-text" x="480" y="260" text-anchor="middle">Les deux postes appartiennent à des préfixes différents.</text>
  <text class="rt-text" x="480" y="283" text-anchor="middle">Le routeur choisit le chemin ; les règles de sécurité déterminent les flux autorisés.</text>
  <text class="rt-text" x="480" y="307" text-anchor="middle">Les adresses sont un exemple pédagogique, pas une configuration complète.</text>
</svg>

---

# 7. DHCP, DNS, ARP et NDP

## 7.1 DHCP : attribution des paramètres

Dans un scénario IPv4 classique, un client sans adresse utilise DHCP pour demander des paramètres de configuration.

Le processus DORA représente les quatre messages fondamentaux courants :

- **Discover** : le client recherche un serveur DHCP ;
- **Offer** : un serveur propose une configuration ;
- **Request** : le client demande l'attribution ;
- **Acknowledge** : le serveur confirme le bail.

Ce processus peut traverser des segments IP via un relais DHCP. Les détails dépendent du déploiement.

## 7.2 Schéma DHCP

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="345" viewBox="0 0 960 345" role="img" aria-labelledby="dhcp-title dhcp-desc">
  <title id="dhcp-title">Échanges DHCP de base</title>
  <desc id="dhcp-desc">Un client et un serveur DHCP échangent Discover, Offer, Request et Acknowledge dans cet ordre conceptuel. Les flèches utilisent des tirets animés ; aucun objet ne circule le long des lignes.</desc>
  <defs>
    <marker id="dhcp-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .dh-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .dh-title{font:700 16px Arial,sans-serif;fill:#f8fafc}
      .dh-text{font:13px Arial,sans-serif;fill:#cbd5e1}
      .dh-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#dhcp-arrow);animation:dh-dash 1.8s linear infinite}
      @keyframes dh-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="343" rx="16" fill="#0b1220" stroke="#334155"/>
  <rect class="dh-box" x="70" y="40" width="260" height="58" rx="10"/>
  <text class="dh-title" x="200" y="75" text-anchor="middle">Client DHCP</text>
  <rect class="dh-box" x="630" y="40" width="260" height="58" rx="10"/>
  <text class="dh-title" x="760" y="75" text-anchor="middle">Serveur DHCP</text>
  <path class="dh-flow" d="M330 126 H630"/>
  <text class="dh-text" x="480" y="117" text-anchor="middle">1. Discover</text>
  <path class="dh-flow" d="M630 174 H330"/>
  <text class="dh-text" x="480" y="165" text-anchor="middle">2. Offer</text>
  <path class="dh-flow" d="M330 222 H630"/>
  <text class="dh-text" x="480" y="213" text-anchor="middle">3. Request</text>
  <path class="dh-flow" d="M630 270 H330"/>
  <text class="dh-text" x="480" y="261" text-anchor="middle">4. Acknowledge</text>
  <text class="dh-text" x="480" y="310" text-anchor="middle">Le client reçoit une configuration selon le bail et les règles du serveur.</text>
</svg>

## 7.3 DNS : résolution de noms

DNS permet de retrouver des informations associées à un nom, notamment des enregistrements d'adresses comme A et AAAA.

La résolution peut utiliser des caches locaux et intermédiaires. Un résultat DNS peut donc être temporairement conservé au lieu d'être redemandé à chaque connexion.

Un incident de DNS peut donner l'impression que le réseau est indisponible alors que la connectivité IP fonctionne.

## 7.4 ARP et NDP

Pour envoyer un paquet vers un voisin IPv4 sur Ethernet, un poste doit connaître l'adresse MAC du prochain saut. ARP permet d'obtenir cette correspondance sur le réseau local.

IPv6 utilise NDP pour la découverte des voisins et d'autres fonctions de configuration. NDP s'appuie sur ICMPv6.

Ces mécanismes sont liés au lien local. Un routeur ne transmet pas simplement une requête ARP d'un réseau local à tous les autres réseaux.

## 7.5 Les caches peuvent influencer le diagnostic

ARP, NDP et DNS peuvent utiliser des caches. Un changement récent d'adresse ou une entrée obsolète peut influencer temporairement les résultats.

Avant de vider un cache sur un système de production, vérifiez que cette action est autorisée et qu'elle est nécessaire. Une opération de dépannage doit suivre le diagnostic, pas le remplacer.

---

# 8. TCP, UDP et ports

## 8.1 Les ports

Les adresses IP permettent d'acheminer les paquets vers un hôte. Les ports TCP ou UDP permettent de distinguer les points de terminaison des applications.

Exemple :

```text
Adresse IP : 192.168.20.30
Port TCP   : 443
```

Cela peut correspondre à un service HTTPS si le serveur écoute réellement sur ce port.

Le port, à lui seul, ne prouve pas qu'un service est présent ou fonctionnel.

## 8.2 TCP

TCP est orienté connexion. Il utilise notamment des numéros de séquence et des accusés de réception pour gérer la livraison ordonnée des octets.

La procédure d'établissement d'une connexion TCP classique utilise trois étapes connues sous le nom de *three-way handshake* :

1. SYN ;
2. SYN-ACK ;
3. ACK.

D'autres paramètres, états et mécanismes interviennent dans les connexions réelles.

## 8.3 UDP

UDP fournit un transport plus simple sans établir de connexion de transport comme TCP. La fiabilité, la retransmission ou la gestion de l'ordre doivent être fournies par l'application si elles sont nécessaires.

UDP peut être utile lorsqu'une application préfère maîtriser elle-même ces mécanismes ou lorsqu'un échange rapide convient mieux à son usage.

## 8.4 Comment diagnostiquer un service

Pour un service TCP, il faut notamment distinguer :

- l'hôte est-il joignable ?
- le port est-il accessible ?
- le service écoute-t-il ?
- une règle de sécurité bloque-t-elle la connexion ?
- l'application répond-elle correctement ?
- TLS ou le protocole applicatif rencontre-t-il une erreur ?

Un ping réussi teste ICMP, pas le service TCP. Une connexion TCP réussie ne prouve pas non plus que la réponse applicative est correcte.

---

# 9. Wi-Fi, MTU et performances

## 9.1 Le Wi-Fi est un réseau radio partagé

Les équipements Wi-Fi partagent un support radio. Les performances dépendent du signal, des interférences, de la congestion, de la capacité du point d'accès et des caractéristiques des clients.

Il faut séparer :

- la puissance et la qualité du signal ;
- le débit négocié ;
- le débit utile de l'application ;
- la latence ;
- les pertes ;
- la charge totale.

## 9.2 MTU

La MTU (*Maximum Transmission Unit*) définit la taille maximale d'une unité de données prise en charge par un lien ou une interface pour la couche concernée.

Des valeurs incohérentes de MTU sur un chemin peuvent entraîner des problèmes, notamment lorsque les mécanismes de découverte de MTU ou la gestion de la fragmentation sont empêchés par des équipements intermédiaires.

Il ne faut pas changer la MTU sans comprendre le chemin complet et les besoins de l'application.

## 9.3 Latence, gigue, pertes et débit

- **Latence :** durée nécessaire pour qu'une donnée atteigne sa destination selon la mesure effectuée.
- **Gigue :** variation de cette durée entre plusieurs paquets.
- **Pertes :** paquets qui n'atteignent pas le point attendu.
- **Débit :** quantité de données transportée pendant un intervalle.
- **Débit utile :** partie correspondant aux données utiles de l'application, après prise en compte des surcharges.

Une application temps réel peut souffrir d'une forte gigue ou de pertes même si le débit maximal semble suffisant.

---

# 10. Méthode de dépannage structurée

## 10.1 Ne pas commencer par modifier la configuration

Un dépannage fiable commence par définir le symptôme et le périmètre de l'incident.

Questions initiales :

- un seul appareil est-il touché ou plusieurs ?
- le problème concerne-t-il un site, un VLAN ou tous les réseaux ?
- l'incident a-t-il commencé après une modification ?
- les adresses et routes sont-elles conformes ?
- le service échoue-t-il par adresse IP, par nom ou dans les deux cas ?

La meilleure méthode cherche à réduire les hypothèses avec le moins de changements possible.

## 10.2 Ordre de diagnostic

<svg xmlns="http://www.w3.org/2000/svg" width="960" height="380" viewBox="0 0 960 380" role="img" aria-labelledby="trouble-title trouble-desc">
  <title id="trouble-title">Méthode de dépannage réseau</title>
  <desc id="trouble-desc">Le diagnostic commence au poste local, vérifie l'adresse, puis le lien et la passerelle, la résolution DNS, le chemin réseau et enfin le service distant. Un échec conduit à une investigation sur le segment correspondant avant de poursuivre.</desc>
  <defs>
    <marker id="tr-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#67e8f9"/></marker>
    <style>
      .tr-box{fill:#172033;stroke:#60a5fa;stroke-width:2}
      .tr-warn{fill:#3b2a14;stroke:#fbbf24;stroke-width:2}
      .tr-title{font:700 14px Arial,sans-serif;fill:#f8fafc}
      .tr-text{font:12px Arial,sans-serif;fill:#cbd5e1}
      .tr-flow{fill:none;stroke:#67e8f9;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#tr-arrow);animation:tr-dash 1.8s linear infinite}
      @keyframes tr-dash{to{stroke-dashoffset:-30}}
    </style>
  </defs>
  <rect x="1" y="1" width="958" height="378" rx="16" fill="#0b1220" stroke="#334155"/>
  <text x="25" y="32" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">DIAGNOSTIQUER DU PLUS PROCHE AU PLUS LOINTAIN</text>
  <rect class="tr-box" x="25" y="70" width="170" height="62" rx="9"/>
  <text class="tr-title" x="110" y="95" text-anchor="middle">1. Configuration IP</text>
  <text class="tr-text" x="110" y="115" text-anchor="middle">Adresse et préfixe</text>
  <rect class="tr-box" x="225" y="70" width="170" height="62" rx="9"/>
  <text class="tr-title" x="310" y="95" text-anchor="middle">2. Liaison locale</text>
  <text class="tr-text" x="310" y="115" text-anchor="middle">Ethernet / Wi-Fi</text>
  <rect class="tr-box" x="425" y="70" width="170" height="62" rx="9"/>
  <text class="tr-title" x="510" y="95" text-anchor="middle">3. Passerelle</text>
  <text class="tr-text" x="510" y="115" text-anchor="middle">Accès au routeur</text>
  <rect class="tr-box" x="625" y="70" width="145" height="62" rx="9"/>
  <text class="tr-title" x="697" y="95" text-anchor="middle">4. DNS</text>
  <text class="tr-text" x="697" y="115" text-anchor="middle">Résolution</text>
  <rect class="tr-box" x="800" y="70" width="135" height="62" rx="9"/>
  <text class="tr-title" x="867" y="95" text-anchor="middle">5. Service</text>
  <text class="tr-text" x="867" y="115" text-anchor="middle">Port + réponse</text>
  <path class="tr-flow" d="M195 101 H218"/>
  <path class="tr-flow" d="M395 101 H418"/>
  <path class="tr-flow" d="M595 101 H618"/>
  <path class="tr-flow" d="M770 101 H793"/>
  <rect class="tr-warn" x="170" y="208" width="620" height="72" rx="10"/>
  <text class="tr-title" x="480" y="237" text-anchor="middle">Si une étape échoue, localiser la cause avant de poursuivre</text>
  <text class="tr-text" x="480" y="259" text-anchor="middle">Conserver les observations, les horaires et les résultats des tests</text>
  <path class="tr-flow" d="M510 132 V200"/>
  <text class="tr-text" x="480" y="318" text-anchor="middle">Un test réussi ne garantit pas le fonctionnement des couches ou services suivants.</text>
  <text class="tr-text" x="480" y="340" text-anchor="middle">ICMP peut être filtré ; un test qui échoue n'identifie pas toujours le composant en faute.</text>
</svg>

## 10.3 Commandes utiles

### Windows

```powershell
ipconfig /all
route print
arp -a
nslookup example.com
ping <ADRESSE_IP>
tracert example.com
```

### Linux

```bash
ip addr
ip route
ip neigh
getent hosts example.com
ping -c 4 <ADRESSE_IP>
traceroute example.com
```

Ces outils ne sont pas tous présents par défaut sur toutes les distributions. Utilisez les équivalents disponibles dans votre environnement.

## 10.4 Interpréter correctement les résultats

Un test ICMP peut échouer à cause d'un filtrage alors que le service applicatif fonctionne.

Une résolution DNS peut réussir alors que le port TCP du service est inaccessible.

Une route peut exister sans que le prochain saut soit opérationnel.

Une réponse applicative peut être incorrecte alors que TCP s'établit normalement.

Chaque observation doit donc être interprétée selon le protocole qu'elle mesure réellement.

---

# 11. Atelier pratique

## Scénario

Un utilisateur ne peut plus accéder à une application interne. Les autres utilisateurs du même site semblent fonctionner normalement.

Vous devez suivre une méthode de diagnostic sans changer immédiatement la configuration.

### Étape A — Décrire le symptôme

Documentez le poste concerné, le site, le VLAN, l'adresse IP, l'heure du début de l'incident et l'application ciblée.

### Étape B — Vérifier les paramètres IP

Consultez l'adresse, le préfixe, la passerelle et les paramètres DNS.

Vérifiez qu'ils correspondent au plan d'adressage attendu.

### Étape C — Tester le réseau local

Vérifiez la connectivité locale et la passerelle. Tenez compte du fait que l'ICMP peut être filtré.

### Étape D — Vérifier DNS

Résolvez le nom de l'application. Si nécessaire, comparez le résultat à une source de référence autorisée.

### Étape E — Vérifier le service

Déterminez si le port et le protocole attendus sont accessibles. Examinez les messages d'erreur et les journaux disponibles.

### Étape F — Établir une conclusion

La conclusion doit distinguer les faits vérifiés des hypothèses.

Exemple :

```text
Symptôme :
L'application ne répond pas depuis un poste.

Vérifié :
Le poste dispose d'une adresse IP valide.
La passerelle répond aux tests autorisés.
DNS renvoie une adresse attendue.

À confirmer :
L'accessibilité du port applicatif.
L'état du service distant.
La présence éventuelle d'une règle de sécurité bloquante.
```

Une telle conclusion est préférable à « le réseau ne marche pas », car elle permet d'orienter le diagnostic vers les éléments encore inconnus.

---

# 12. Étude de panne

## Situation

Un poste peut accéder à Internet par adresse IP, mais l'accès à un site par son nom échoue.

## Hypothèses possibles

- le résolveur configuré est indisponible ;
- le poste possède une mauvaise adresse de serveur DNS ;
- une règle de sécurité bloque les requêtes DNS ;
- une réponse DNS incorrecte est mise en cache ;
- le problème se situe dans le service ou la configuration DNS.

## Démarche

1. vérifier l'adresse IP, le préfixe et la passerelle ;
2. consulter les serveurs DNS configurés ;
3. exécuter une requête DNS ciblée ;
4. examiner les erreurs obtenues ;
5. comparer le résultat à une source de référence autorisée ;
6. vérifier les restrictions de sécurité ;
7. confirmer que la solution corrige bien le problème sans dégrader les autres services.

Le simple fait qu'une adresse IP soit joignable ne permet pas de conclure que le réseau DNS est opérationnel.

---

# 13. Évaluation corrigée

## Questions

1. Pourquoi un modèle en couches facilite-t-il le dépannage ?
2. Quelle différence existe entre une trame et un paquet IP ?
3. Combien d'adresses contient un sous-réseau IPv4 `/26` ?
4. Quel rôle joue un VLAN ?
5. Pourquoi un trunk doit-il autoriser les VLAN nécessaires ?
6. Quelle règle utilise un routeur pour choisir la route la plus spécifique ?
7. Quel est le rôle des messages DHCP Discover et Offer ?
8. À quoi sert ARP ?
9. Pourquoi le succès du ping ne prouve-t-il pas que TCP fonctionne ?
10. Quel est le rôle de la MTU ?
11. Pourquoi faut-il identifier précisément le symptôme avant de modifier la configuration ?
12. Comment distinguer un échec DNS d'un échec de connectivité IP ?

## Corrigé

1. Il aide à séparer les responsabilités et à déterminer les tests pertinents.
2. La trame est une unité de couche liaison ; le paquet IP est une unité de couche réseau transportée dans cette trame sur Ethernet.
3. 64 adresses au total ; dans un sous-réseau IPv4 conventionnel, 62 sont utilisables pour les hôtes.
4. Il sépare logiquement des domaines de commutation.
5. Pour transporter uniquement les VLAN nécessaires et éviter les incohérences de segmentation.
6. Le principe du préfixe le plus long, parmi les routes qui correspondent à la destination.
7. Discover recherche un serveur DHCP ; Offer propose des paramètres.
8. À résoudre une adresse IPv4 de voisin vers une adresse de couche liaison sur le lien local.
9. Le ping teste ICMP, pas le service TCP ni son port.
10. Elle fixe une taille maximale d'unité de données sur un lien ou une interface.
11. Pour éviter de provoquer des changements inutiles et de masquer la cause de l'incident.
12. En contrôlant séparément la résolution des noms et l'accessibilité IP de la destination.

---

# 14. Préparation du niveau expert

Le niveau expert s'intéressera à :

- la conception de plans d'adressage à grande échelle ;
- IPv6 en profondeur ;
- le routage dynamique et les politiques de routage ;
- la redondance et la convergence ;
- le contrôle des domaines de broadcast et des chemins ;
- les architectures multi-sites ;
- la segmentation de sécurité ;
- la supervision et la corrélation des événements ;
- les analyses de captures de paquets ;
- les pannes complexes et les méthodes de diagnostic par hypothèses.

**Le niveau intermédiaire apprend à expliquer et à tester le fonctionnement du réseau. Le niveau expert apprend à concevoir une architecture cohérente, à anticiper les défaillances et à maîtriser leurs conséquences.**

---

## Références utiles

- RFC 1918 — Adresses privées IPv4 : https://www.rfc-editor.org/rfc/rfc1918.html
- RFC 791 — Internet Protocol IPv4 : https://www.rfc-editor.org/rfc/rfc791.html
- RFC 8200 — Internet Protocol IPv6 : https://www.rfc-editor.org/rfc/rfc8200.html
- RFC 826 — ARP : https://www.rfc-editor.org/rfc/rfc826.html
- RFC 2131 — DHCP : https://www.rfc-editor.org/rfc/rfc2131.html
- RFC 1034 — Concepts DNS : https://www.rfc-editor.org/rfc/rfc1034.html
- RFC 9293 — TCP : https://www.rfc-editor.org/rfc/rfc9293.html
- IEEE 802.1Q — VLAN : https://standards.ieee.org/standard/802_1Q-2022.html
- Documentation Microsoft sur les outils réseau : https://learn.microsoft.com/windows-server/administration/windows-commands/windows-commands

**Fichier :** `intro-reseau-intermediaire.md`  
**Niveau :** Intermédiaire  
**Fin du cours**
