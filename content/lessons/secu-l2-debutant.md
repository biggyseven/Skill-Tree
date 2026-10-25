# Sécurité de niveau 2 (L2) — Débutant

> **Objectif du cours :** comprendre comment sécuriser un réseau Ethernet commuté, reconnaître les attaques de couche 2 les plus courantes et appliquer une première base de configuration défensive dans un laboratoire.
>
> **Public visé :** débutant en sécurité réseau connaissant les notions essentielles d’adresse MAC, de switch, de VLAN et d’adresse IP. Les notions indispensables sont rappelées au début.
>
> **Approche pédagogique :** chaque notion suit le même cycle : comprendre → observer → configurer → vérifier → dépanner. Les schémas sont textuels afin de rester lisibles dans un terminal, un éditeur Markdown ou une plateforme de cours.


## Sommaire

1. [Parcours pratique du débutant](#1-parcours-pratique-du-débutant)
2. [Les bases indispensables de la couche 2](#2-les-bases-indispensables-de-la-couche-2)
3. [Menaces courantes sur un LAN commuté](#3-menaces-courantes-sur-un-lan-commuté)
4. [Construire un laboratoire sûr](#4-construire-un-laboratoire-sûr)
5. [Sécuriser les ports d’accès](#5-sécuriser-les-ports-daccès)
6. [Sécuriser les VLAN et les trunks](#6-sécuriser-les-vlan-et-les-trunks)
7. [Protéger le protocole Spanning Tree](#7-protéger-le-protocole-spanning-tree)
8. [DHCP Snooping : bloquer les faux serveurs DHCP](#8-dhcp-snooping--bloquer-les-faux-serveurs-dhcp)
9. [Dynamic ARP Inspection : contrôler les messages ARP](#9-dynamic-arp-inspection--contrôler-les-messages-arp)
10. [Réduire les risques de tempête et de boucle](#10-réduire-les-risques-de-tempête-et-de-boucle)
11. [Méthode de diagnostic](#11-méthode-de-diagnostic)
12. [Ateliers guidés et exercices corrigés](#12-ateliers-guidés-et-exercices-corrigés)
13. [Checklist de mise en production](#13-checklist-de-mise-en-production)
14. [Évaluation finale](#14-évaluation-finale)
15. [Glossaire](#15-glossaire)
16. [Pour aller plus loin](#16-pour-aller-plus-loin)


## 1. Parcours pratique du débutant

Le but n’est pas de mémoriser vingt commandes. Il faut d’abord être capable d’observer un réseau normal, de modifier une seule protection, puis de vérifier son effet sans couper les services légitimes.

### 1.1 Progression recommandée

| Étape | Compétence | Manipulation à réaliser | Preuve de réussite |
|---|---|---|---|
| 1 | Lire un petit LAN | Identifier les ports, VLAN, adresses MAC et rôles des appareils | Un schéma annoté et une table MAC comprise |
| 2 | Distinguer accès et trunk | Vérifier le mode de chaque port | Aucun port utilisateur n’est un trunk inutile |
| 3 | Réduire l’exposition | Arrêter les ports inutilisés et les placer dans un VLAN isolé | Les ports inutilisés sont administrativement désactivés |
| 4 | Limiter les appareils par port | Activer une limite MAC sur un port de test | Le comportement en cas de dépassement est documenté |
| 5 | Bloquer les faux DHCP | Activer DHCP Snooping sur le VLAN du laboratoire | Un client reçoit une adresse du serveur autorisé seulement |
| 6 | Valider ARP | Activer Dynamic ARP Inspection après validation de DHCP Snooping | Les clients légitimes communiquent et les incohérences sont journalisées |
| 7 | Protéger STP | Activer PortFast et BPDU Guard sur les ports terminaux compatibles | Un BPDU inattendu est détecté sur le port de test |
| 8 | Diagnostiquer | Résoudre un cas où un client ne reçoit plus d’adresse IP | Une démarche reproductible identifie la cause |

**Règle d’apprentissage :** ne configure qu’une famille de protection à la fois. Sauvegarde l’état initial, applique le changement, vérifie le service, puis note le résultat. Cela évite de confondre plusieurs causes.

### 1.2 Résultat attendu à la fin du cours

Tu dois pouvoir expliquer, avec tes propres mots :

- pourquoi un switch apprend les adresses MAC et pourquoi cette table doit être protégée ;
- la différence entre un port d’accès et un trunk ;
- la différence entre Port Security, DHCP Snooping et Dynamic ARP Inspection ;
- pourquoi PortFast et BPDU Guard vont souvent ensemble sur les ports terminaux ;
- comment vérifier que les protections n’empêchent pas un poste autorisé de fonctionner ;
- quand demander une revue par un administrateur expérimenté avant de déployer un changement.


## 2. Les bases indispensables de la couche 2

### 2.1 À quoi sert la couche 2 ?

La couche 2 du modèle OSI assure la communication sur un lien local au moyen de trames Ethernet. Une trame comporte notamment une adresse MAC source et une adresse MAC destination. Un switch Ethernet apprend les adresses MAC sources qu’il observe et les associe à un port et à un VLAN.

Une adresse MAC est généralement représentée sur 48 bits, par exemple `00:11:22:33:44:55`. Elle identifie une interface au niveau Ethernet, mais **ne constitue pas une preuve d’identité** : dans de nombreux environnements, une adresse MAC peut être usurpée ou changée par logiciel.

### 2.2 Comment le switch apprend les adresses MAC

```text
Poste A                  Switch                  Poste B
MAC A                     Table MAC               MAC B
  |                          |                       |
  |--- trame source A ------>|                       |
  |                          | apprend A -> port 1  |
  |                          |                       |
  |                          |<----- trame source B -|
  |                          | apprend B -> port 2  |
  |                          |                       |
  |<--- trame destinée A ---|--- trame destinée B ->|
```

Si le switch connaît le port associé à l’adresse MAC de destination, il envoie la trame vers ce port. S’il ne connaît pas cette adresse dans le VLAN concerné, il peut diffuser la trame inconnue sur les ports autorisés de ce VLAN, sauf le port de réception. Les trames de broadcast sont aussi diffusées dans le domaine de broadcast approprié.

### 2.3 Table MAC : ce qu’elle prouve et ce qu’elle ne prouve pas

Exemple simplifié :

```text
VLAN   Adresse MAC         Type       Port
----   -----------------   --------   -----
10     00:11:22:33:44:55   Dynamique  Gi1/0/1
10     00:11:22:33:44:66   Dynamique  Gi1/0/2
20     00:11:22:33:44:77   Dynamique  Gi1/0/8
```

Cette table indique ce que le switch a appris et où il pense pouvoir atteindre chaque adresse. Elle ne prouve pas que l’appareil est autorisé. Un attaquant connecté physiquement peut tenter d’envoyer des trames avec des adresses source choisies.

### 2.4 VLAN et domaine de broadcast

Un VLAN sépare logiquement un réseau Ethernet en domaines de broadcast distincts. Un VLAN améliore la segmentation, mais **un VLAN seul n’est pas une protection complète** : une mauvaise configuration des trunks, une erreur d’affectation ou un accès physique non autorisé peuvent compromettre l’isolation prévue.

```text
                 Switch de distribution
                 +--------------------+
                 | VLAN 10 : Employés  |
                 | VLAN 20 : Admin     |
                 | VLAN 30 : Invités   |
                 +---------+----------+
                           |
              +------------+------------+
              |            |            |
           VLAN 10       VLAN 20      VLAN 30
           PC métier     Admin        Invités
```

Un VLAN de gestion distinct est utile pour administrer les équipements. Il faut cependant contrôler qui peut y accéder, depuis quels postes, et par quels protocoles d’administration.

### 2.5 Port d’accès et trunk

- **Port d’accès (access)** : transporte normalement le trafic d’un seul VLAN non tagué vers un appareil terminal, selon la configuration du switch.
- **Trunk** : transporte plusieurs VLAN, généralement au moyen de tags 802.1Q.
- **VLAN natif** : sur un trunk 802.1Q, il correspond généralement au trafic transmis sans tag. Le traitement exact dépend de la plateforme et de sa configuration.

```text
PC utilisateur                     Switch A ===== trunk 802.1Q ===== Switch B
non tagué                          VLAN 10, 20, 30                  VLAN 10, 20, 30
      |                                     ||
      +--- port access VLAN 10               || VLAN autorisés explicitement
```

Un port terminal ne devrait pas négocier ou accepter un trunk si ce n’est pas nécessaire. Un trunk doit transporter uniquement les VLAN requis.

### 2.6 Protocoles à connaître

| Protocole / mécanisme | Rôle | Point de vigilance sécurité |
|---|---|---|
| ARP | Associe une adresse IPv4 locale à une adresse MAC | Les réponses ARP peuvent être falsifiées |
| DHCP | Fournit configuration IP, passerelle, DNS et durée de bail | Un faux serveur peut fournir de mauvaises options |
| STP / RSTP | Évite les boucles de niveau 2 | Des BPDUs inattendus peuvent modifier la topologie |
| LLDP / CDP | Découverte des voisins réseau | Peut révéler des informations sur l’infrastructure |
| 802.1Q | Marquage VLAN sur un trunk | Une configuration incohérente peut exposer des VLAN |
| 802.1X | Contrôle d’accès au réseau fondé sur l’authentification du port | Nécessite une architecture d’authentification correctement conçue |


## 3. Menaces courantes sur un LAN commuté

L’objectif de cette section est de reconnaître les symptômes et de choisir la protection adaptée. Les scénarios offensifs sont décrits pour la compréhension et la défense ; les tests pratiques doivent rester confinés au laboratoire autorisé.

### 3.1 Saturation de la table MAC (MAC flooding)

Un équipement envoie un très grand nombre de trames avec des adresses MAC source différentes. Selon le matériel et le comportement du switch, cela peut saturer la table de commutation ou perturber l’apprentissage normal. Le switch peut alors diffuser davantage de trames inconnues, ce qui peut exposer du trafic à des ports qui n’auraient pas normalement reçu ces trames et augmenter la charge réseau.

```text
Machine non autorisée
   | nombreuses trames / nombreuses MAC source
   v
+------------------------------+
| Switch                       |
| Table MAC sous pression       |
| Apprentissage perturbé        |
+------------------------------+
   | risque : flooding accru, lenteur ou perte de service
   v
Postes légitimes affectés
```

**Défenses principales :** Port Security ou limitation MAC équivalente, supervision des événements, contrôle physique des prises et désactivation des ports inutilisés. Une limite trop basse peut toutefois bloquer un téléphone IP, un point d’accès, une station virtuelle ou un mini-switch autorisé.

### 3.2 Usurpation ARP (ARP spoofing / ARP poisoning)

ARP sert à découvrir l’adresse MAC correspondant à une adresse IPv4 dans le réseau local. ARP n’intègre pas, à lui seul, un mécanisme universel d’authentification des réponses. Un hôte malveillant peut envoyer des réponses trompeuses pour associer l’adresse IP de la passerelle à sa propre adresse MAC.

```text
État normal :
PC A -- ARP : « Qui possède 192.0.2.1 ? » --> LAN
Passerelle -- ARP : « 192.0.2.1 = MAC-GW » --> PC A

État falsifié possible :
Machine malveillante -- fausse réponse ARP --> PC A
PC A associe temporairement 192.0.2.1 à MAC-ATTACKER
```

Cela peut permettre une interception ou une perturbation du trafic local. ARP spoofing et MAC flooding sont deux attaques différentes : la première manipule des associations IP/MAC ; la seconde cherche notamment à perturber l’apprentissage des adresses MAC par le switch.

**Défenses principales :** DHCP Snooping comme base de données de confiance pour les baux dynamiques, Dynamic ARP Inspection (DAI), port security, segmentation et surveillance. Les hôtes à IP statique peuvent nécessiter des entrées ou exceptions explicites selon la plateforme.

### 3.3 Faux serveur DHCP

DHCP suit habituellement un échange comprenant une découverte, une offre, une demande et un accusé de réception. Si plusieurs serveurs répondent, un client peut retenir une offre non autorisée. Le faux serveur pourrait annoncer une mauvaise passerelle, un DNS contrôlé par un tiers ou une configuration qui empêche l’accès au réseau.

```text
Client DHCP           Switch                 Serveur autorisé
    |--- Discover ------>|----------------------->|
    |<-- Offer légitime -|<-----------------------|
    |
    |<-- Offer pirate ---|--- port non fiable --- X  (bloquée par DHCP Snooping)
```

**Défenses principales :** DHCP Snooping et définition précise des ports de confiance. Un port vers un serveur DHCP ou vers un trunk contrôlé peut être configuré comme trusted selon le design ; les ports utilisateurs doivent normalement rester untrusted. Ne déclare pas un port trusted simplement parce qu’il est un uplink : identifie d’abord les chemins DHCP légitimes.

### 3.4 Épuisement du pool DHCP (DHCP starvation)

Des requêtes DHCP portant des identités source variées peuvent consommer les baux disponibles. Les utilisateurs légitimes ne parviennent alors plus à obtenir d’adresse. Les limites MAC, les contrôles DHCP et les mécanismes de limitation de débit disponibles sur la plateforme peuvent contribuer à réduire ce risque.

**Symptômes possibles :** pool presque vide, erreurs d’attribution, grand nombre de requêtes, nouveaux clients qui obtiennent une adresse automatique de secours ou ne configurent aucune adresse.

### 3.5 Mauvaise utilisation des trunks et VLAN hopping

Une erreur de configuration peut permettre à un port destiné à un terminal de fonctionner comme trunk ou de transporter des VLAN non nécessaires. Des attaques historiquement décrites sous le nom de *VLAN hopping* exploitent notamment des configurations de trunking permissives ou des manipulations de tags. Les détails dépendent du matériel, du protocole et de la configuration.

**Défenses principales :** configurer explicitement les ports d’accès, désactiver la négociation de trunk lorsqu’elle existe, limiter les VLAN autorisés sur chaque trunk, utiliser un VLAN natif dédié et inutilisé lorsqu’il convient au design, et éviter les configurations par défaut non vérifiées.

> **À retenir :** changer le VLAN natif ou éviter le VLAN 1 n’est pas une solution magique. La sécurité vient de l’association de plusieurs contrôles cohérents et vérifiés.

### 3.6 Attaques ou erreurs affectant STP

STP/RSTP empêche les boucles de niveau 2 en bloquant certains chemins. Un changement non attendu des informations STP peut modifier le pont racine ou la topologie et provoquer une interruption, une boucle ou un trafic sous-optimal.

**Défenses à connaître :** PortFast (sur les ports terminaux compatibles), BPDU Guard pour désactiver/protéger un port d’accès qui reçoit un BPDU, Root Guard sur les ports où un switch aval ne doit pas devenir racine, et Loop Guard selon le design. Ces fonctions ont des rôles distincts et ne doivent pas être appliquées aveuglément sur tous les ports.

### 3.7 Boucle Ethernet et tempête de broadcast

Une boucle physique entre switches sans contrôle approprié peut faire circuler indéfiniment des trames Ethernet. Cela produit une tempête de broadcast, des copies multiples de trames et des changements rapides dans la table MAC.

**Défenses principales :** conception physique correcte, STP/RSTP opérationnel, protection des ports terminaux, limitation de tempête quand elle est prise en charge et supervision des changements de topologie.

### 3.8 Accès physique et ports oubliés

Une prise réseau libre ou un port activé dans une salle accessible peut fournir un accès interne à une personne non autorisée. Une configuration sécurisée doit inclure le contrôle des prises, la désactivation des ports inutilisés et, dans les environnements adaptés, une authentification 802.1X.

### 3.9 Tableau récapitulatif

| Menace | Symptôme fréquent | Contrôle utile | Limite à connaître |
|---|---|---|---|
| Saturation MAC | Table MAC instable, flooding ou charge élevée | Limite MAC / Port Security | Une limite trop faible perturbe les équipements légitimes |
| Faux DHCP | Mauvaise passerelle/DNS, clients sans bail correct | DHCP Snooping | Les ports trusted doivent être identifiés avec soin |
| ARP spoofing | Mauvaises correspondances IP/MAC, interception possible | DAI, DHCP Snooping | Les IP statiques demandent une attention particulière |
| Trunk involontaire | Plusieurs VLAN présents sur un port terminal | Port access explicite, trunk limité | Les commandes dépendent du constructeur |
| Changement STP non attendu | Recalcul STP, coupure ou boucle | BPDU Guard, Root Guard, supervision | Chaque garde a une portée spécifique |
| Tempête de broadcast | Réseau très lent, compteurs broadcast anormaux | STP, storm control | Une limite trop stricte peut supprimer du trafic valide |
| Connexion non autorisée | Appareil inconnu sur un port actif | Contrôle physique, 802.1X, limite MAC | La MAC seule n’est pas une identité forte |


## 4. Construire un laboratoire sûr

### 4.1 Règles avant de commencer

1. Utilise un simulateur/émulateur réseau, des commutateurs de laboratoire ou un équipement dont tu as l’autorisation d’administration.
2. Ne réalise pas de tests d’attaque sur le réseau d’une entreprise, d’un établissement, d’un voisin ou sur Internet.
3. Ne raccorde pas un laboratoire avec faux DHCP, ARP spoofing ou boucles à un réseau de production.
4. Avant chaque changement, sauvegarde la configuration et vérifie comment revenir à l’état initial.
5. Note les interfaces et les VLAN réellement utilisés. Les numéros d’interfaces ci-dessous sont des exemples.

### 4.2 Topologie de départ

Le laboratoire se compose d’un switch administrable, de deux postes clients, d’un serveur DHCP légitime et, pour certains exercices isolés, d’une machine de test supplémentaire.

```text
                         +-------------------+
                         | SW1               |
                         | Switch L2         |
                         | VLAN 10 : USERS   |
                         | VLAN 20 : ADMIN   |
                         +--+----+------+----+
                            |    |      |
                  Gi1/0/1 --+    |      +-- Gi1/0/8 --> Serveur DHCP autorisé
                            |    |
                  Gi1/0/2 --+    +-- Gi1/0/3 --> PC-B / poste de test
                            |
                         PC-A / client

Exemple d’adressage documentaire :
VLAN 10 : 192.0.2.0/24
Passerelle simulée : 192.0.2.1
Serveur DHCP de laboratoire : 192.0.2.10
```

Les adresses `192.0.2.0/24` appartiennent à un bloc réservé à la documentation. Elles servent ici d’exemple et ne sont pas destinées à un réseau public réel.

### 4.3 Exemple de plan de ports

| Interface d’exemple | Appareil / usage | VLAN / rôle | Niveau de confiance initial |
|---|---|---|---|
| Gi1/0/1 | PC-A | Access VLAN 10 | Untrusted |
| Gi1/0/2 | PC-B | Access VLAN 10 | Untrusted |
| Gi1/0/3 | Port de test | Access VLAN 10 | Untrusted |
| Gi1/0/8 | Serveur DHCP légitime | Access VLAN 10 | Trusted DHCP uniquement si confirmé et justifié |
| Gi1/0/24 | Uplink vers autre switch, si présent | Trunk explicite | À analyser selon la topologie |
| Gi1/0/4-7, Gi1/0/9-23 | Ports inutilisés dans ce laboratoire | VLAN isolé puis shutdown | Non connectés |

La notion de *trusted* est propre à certaines protections comme DHCP Snooping ou DAI. Un port de confiance pour un mécanisme n’est pas automatiquement fiable pour toutes les autres protections.

### 4.4 Collecter l’état initial

Sur un switch Cisco IOS/IOS XE compatible, commence par des commandes de lecture. Les noms exacts peuvent varier selon la famille et la version logicielle.

```text
show interfaces status
show vlan brief
show interfaces trunk
show mac address-table dynamic
show spanning-tree summary
show running-config
```

Consigne dans ton carnet de laboratoire :

- quels ports sont connectés et à quels appareils ;
- le VLAN de chaque port ;
- quels ports fonctionnent en trunk ;
- quelles adresses MAC sont apprises ;
- l’état de STP et le switch racine ;
- les éventuels messages d’erreur déjà présents.


## 5. Sécuriser les ports d’accès

### 5.1 Principe du Port Security

Port Security permet, sur les plateformes compatibles, de restreindre le nombre ou la liste des adresses MAC acceptées sur un port. Cela réduit certains risques de connexions multiples inattendues ou de saturation de la table MAC, mais n’est pas une authentification forte à lui seul.

### 5.2 Avant de choisir une limite MAC

Réponds à ces questions :

- Le port sert-il un PC seul, un téléphone IP avec PC derrière, un point d’accès Wi-Fi ou un hyperviseur ?
- Combien d’adresses MAC légitimes peuvent être apprises sur ce port ?
- Que doit-il se passer si une nouvelle adresse apparaît : journalisation, rejet des trames, ou désactivation du port ?
- Qui recevra une alerte et qui pourra rétablir le service ?

Un plafond de `1` peut être adapté à un poste seul, mais inadapté à un téléphone IP avec un PC connecté derrière. Il faut choisir la valeur selon l’usage réel.

### 5.3 Exemple Cisco IOS/IOS XE : port d’accès et Port Security

> Exemple à adapter et à tester sur une version compatible. Il ne s’agit pas d’une configuration universelle pour tous les constructeurs.

```text
configure terminal
interface gigabitEthernet1/0/1
 description PC-A - laboratoire uniquement
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 1
 switchport port-security violation restrict
end
```

Cet exemple active une limite d’une adresse MAC et demande une action de restriction plutôt qu’une mise hors service automatique du port. Le comportement exact, la prise en charge et les compteurs dépendent du modèle et de la version. Dans un vrai déploiement, choisis la politique de violation selon les exigences d’exploitation.

Pour apprendre une adresse MAC de manière persistante sur certaines plateformes Cisco, il existe une fonction souvent appelée *sticky MAC*. Elle doit être employée avec une procédure de changement d’équipement ; sinon un remplacement légitime peut provoquer une violation inattendue.

### 5.4 Vérification

```text
show port-security
show port-security interface gigabitEthernet1/0/1
show mac address-table interface gigabitEthernet1/0/1
show logging
```

À vérifier :

- Port Security est-il actif sur le port attendu ?
- Quel est le maximum configuré ?
- Combien d’adresses sécurisées sont apprises ?
- Y a-t-il une violation dans les compteurs ou les journaux ?
- Le PC autorisé conserve-t-il son accès réseau ?

### 5.5 Exemple de sortie interprétée

```text
Port       Max MAC   MAC sécurisées   Violation
---------  --------  ---------------  ---------
Gi1/0/1    1         1                0
```

Le port a atteint sa limite d’une MAC et aucune violation n’est indiquée. Cela ne prouve pas à lui seul que l’ensemble du réseau est sécurisé ; cela confirme seulement quelques paramètres de cette interface.

### 5.6 Désactiver les ports inutilisés

Un port inutilisé mais actif constitue une prise potentielle d’accès au LAN. Dans un laboratoire Cisco, on peut affecter les ports inutilisés à un VLAN réservé puis les désactiver :

```text
configure terminal
vlan 999
 name UNUSED-NO-ENDPOINTS
!
interface range gigabitEthernet1/0/4-7 , gigabitEthernet1/0/9-23
 description PORTS-INUTILISES
 switchport mode access
 switchport access vlan 999
 shutdown
end
```

La syntaxe d’`interface range` varie selon le matériel. Vérifie les interfaces exactes avant d’appliquer une commande de groupe. Ne lance jamais cette commande sur une plage qui contient un uplink ou un port actif.

**Bonne pratique opérationnelle :** étiquette les prises, documente le VLAN réservé et contrôle périodiquement les ports arrêtés. Une configuration doit correspondre au câblage réel.


## 6. Sécuriser les VLAN et les trunks

### 6.1 Durcissement d’un port utilisateur

Sur un port destiné à un ordinateur, configure explicitement le mode d’accès et le VLAN attendu. Sur les équipements qui prennent en charge la négociation de trunk, désactive cette négociation sur les ports terminaux.

```text
configure terminal
interface gigabitEthernet1/0/2
 description PC-B
 switchport mode access
 switchport access vlan 10
 ! Sur une plateforme qui le prend en charge :
 switchport nonegotiate
end
```

`switchport nonegotiate` n’est pas disponible sur toutes les plateformes et n’a de sens que si la plateforme utilise un mécanisme de négociation tel que DTP. L’élément principal reste la configuration explicite du mode d’accès.

### 6.2 Trunk : limiter les VLAN au strict nécessaire

Sur un trunk entre deux commutateurs, n’autorise que les VLAN qui doivent réellement traverser le lien. Exemple illustratif :

```text
configure terminal
interface gigabitEthernet1/0/24
 description UPLINK-SW2
 switchport mode trunk
 switchport trunk allowed vlan 10,20
end
```

Ce fragment est un exemple de principe. Le réglage du VLAN natif, l’encapsulation disponible et les commandes exactes varient selon les gammes. Avant de modifier un trunk existant, compare les VLAN autorisés aux besoins réels des deux côtés du lien : une liste trop restrictive peut couper les services ; une liste trop large augmente l’exposition.

### 6.3 Schéma de circulation des VLAN

```text
PC Employé -- access VLAN 10 -- SW1 ===== trunk VLAN 10,20 ===== SW2 -- access VLAN 20 -- PC Admin
                                       |
                          seuls VLAN 10 et 20 nécessaires

Un port de PC ne devrait pas transporter les VLAN 10 et 20 comme un trunk.
```

Le dessin montre un exemple logique, mais il ne signifie pas que le trafic d’un poste VLAN 10 peut communiquer librement avec un poste VLAN 20. Le routage inter-VLAN et les règles de filtrage sont des contrôles séparés.

### 6.4 VLAN de gestion

Utilise un réseau de gestion réservé aux équipements et limite les connexions d’administration à des sources autorisées. Préfère SSH et des protocoles d’administration chiffrés aux protocoles non chiffrés lorsque c’est possible. Désactive les services d’administration inutiles et applique des comptes nominatifs, des droits limités et une journalisation cohérente.

### 6.5 LLDP et CDP

Les protocoles de découverte aident à connaître les voisins, les ports et certaines informations sur les équipements. Ils sont pratiques pour l’exploitation, mais peuvent révéler des détails d’infrastructure sur une interface exposée à un appareil non fiable.

- Conserve-les sur les liens où ils sont nécessaires à l’exploitation.
- Évalue leur désactivation sur les ports terminaux non fiables lorsque l’environnement le permet.
- Ne coupe pas globalement un protocole sans vérifier les dépendances, par exemple la téléphonie ou les outils d’inventaire.


## 7. Protéger le protocole Spanning Tree

### 7.1 Pourquoi STP est critique

Une topologie Ethernet redondante peut créer une boucle si plusieurs chemins transmettent simultanément les mêmes trames. STP/RSTP construit une topologie logique sans boucle et bloque certains chemins redondants.

```text
                   SW1 (racine attendue)
                     /             \
                    /               \
                  SW2 ------------- SW3
                       lien redondant

STP/RSTP choisit les rôles et états de ports nécessaires pour éviter une boucle.
```

Le switch racine doit être choisi conformément au design réseau, pas laissé au hasard. Les protections de ports contribuent à préserver ce design, mais ne remplacent pas la conception et la supervision de STP.

### 7.2 PortFast : pour les ports terminaux

PortFast (ou fonction équivalente selon la plateforme) permet à un port destiné à un équipement terminal de passer plus rapidement à l’état de transmission. Il ne doit pas être activé sans réflexion sur un lien où un switch peut être connecté.

### 7.3 BPDU Guard : empêcher un port terminal de rejoindre STP

BPDU Guard protège généralement les ports configurés comme ports terminaux/PortFast : si le port reçoit une BPDU inattendue, le switch déclenche l’action de protection définie (souvent la désactivation du port). Cela peut faire tomber le lien si un mini-switch est branché sur une prise d’utilisateur — ce qui est précisément un signal à investiguer.

Exemple Cisco IOS/IOS XE, à adapter :

```text
configure terminal
interface gigabitEthernet1/0/1
 spanning-tree portfast
 spanning-tree bpduguard enable
end
```

Sur certaines plateformes, PortFast peut être activé globalement pour les ports terminaux et BPDU Guard peut être configuré globalement ou par interface. Lis la documentation de la version utilisée avant de choisir le mode global.

### 7.4 Root Guard et Loop Guard : ne pas les confondre

- **Root Guard** : empêche un port désigné de devenir un chemin par lequel un switch aval impose un nouveau pont racine. On l’utilise là où le design impose que le root reste en amont.
- **Loop Guard** : aide à prévenir certaines boucles lorsque des BPDUs attendues cessent d’être reçues sur des ports concernés.
- **BPDU Guard** : protège surtout les ports terminaux contre la réception de BPDUs.

Ce sont trois mécanismes différents. Appliquer la mauvaise protection sur un mauvais type de lien peut provoquer des coupures ou ne pas protéger contre la menace visée.

### 7.5 Vérification STP

```text
show spanning-tree
show spanning-tree summary
show spanning-tree interface gigabitEthernet1/0/1 detail
show logging
```

À examiner : pont racine courant, rôles des ports, états, changements de topologie, événements BPDU Guard et concordance entre le câblage prévu et la topologie réelle.


## 8. DHCP Snooping : bloquer les faux serveurs DHCP

### 8.1 Concept

DHCP Snooping classe les interfaces entre ports de confiance et ports non fiables pour contrôler certains messages DHCP. Il peut aussi construire une base d’associations entre l’adresse IP attribuée, la MAC du client, le VLAN et le port. Cette base peut être utilisée par d’autres mécanismes de sécurité, notamment Dynamic ARP Inspection et IP Source Guard sur les plateformes compatibles.

```text
Client sur port UNTRUSTED
       |
       | DHCP Discover / Request : généralement permis selon règles
       v
+--------------------------------+
| Switch avec DHCP Snooping      |
|                                |
| Offre depuis port untrusted : X|  -> bloquée selon la politique
| Offre depuis serveur autorisé :|  -> transmise si le chemin est trusted
+----------------+---------------+
                 |
        port vers serveur légitime
        déclaré trusted si justifié
```

Le terme *trusted* ne signifie pas « équipement toujours sûr » ; il indique que les messages pertinents reçus par cette interface sont traités selon une politique de confiance. La configuration des ports trusted est donc un élément critique.

### 8.2 Ordre de déploiement

1. Inventorier tous les serveurs DHCP légitimes, y compris les relais et les trunks sur le chemin.
2. Vérifier le VLAN ciblé et le chemin de retour des messages DHCP.
3. Activer DHCP Snooping sur le VLAN de laboratoire.
4. Déclarer trusted uniquement l’interface ou les interfaces qui doivent recevoir les messages serveur légitimes.
5. Garder les ports utilisateurs untrusted.
6. Renouveler un bail d’un client et consulter la table de bindings ainsi que les compteurs.
7. En cas d’échec, rétablir la configuration et vérifier le chemin DHCP avant d’ajouter des exceptions.

### 8.3 Exemple Cisco IOS/IOS XE

> Exemple de laboratoire ; les commandes exactes dépendent du modèle et de la version. Sur un réseau à relais DHCP ou à plusieurs switches, il faut raisonner sur tous les ports traversés.

```text
configure terminal
ip dhcp snooping
ip dhcp snooping vlan 10
!
interface gigabitEthernet1/0/8
 description Vers-serveur-DHCP-legitime
 ip dhcp snooping trust
!
interface gigabitEthernet1/0/1
 description PC-A
 no ip dhcp snooping trust
end
```

Sur les plateformes où les ports sont untrusted par défaut, la commande de non-confiance explicite peut être inutile ou non disponible. L’important est que les ports clients ne soient pas accidentellement trusted.

**Attention :** ne recopie pas ce fragment sans adapter la topologie. Si le serveur DHCP est atteint à travers un autre switch, un trunk ou un relais, la confiance se configure sur les ports pertinents du chemin de façon contrôlée, et pas nécessairement sur un port access local uniquement.

### 8.4 Vérification

```text
show ip dhcp snooping
show ip dhcp snooping binding
show ip dhcp snooping statistics
show logging
```

Le nom et le détail des commandes peuvent varier. Vérifie :

- que le VLAN visé est activé ;
- que la liste des ports trusted correspond au plan ;
- que le client légitime obtient un bail ;
- que le binding correspond à la MAC, l’adresse IP, au VLAN et au port attendus ;
- que les journaux ne montrent pas de messages DHCP bloqués de manière inattendue.

### 8.5 Erreurs typiques

| Symptôme | Cause possible | Vérification prioritaire |
|---|---|---|
| Le client n’obtient plus d’adresse | Mauvais port trusted ou Snooping activé sur un VLAN mal choisi | Chemin du serveur et VLAN DHCP |
| La table de bindings reste vide | Aucun bail observé, DHCP statique, option non prise en charge ou commande différente | Échange DHCP, version et commandes de la plateforme |
| Des clients fonctionnent sur un switch mais pas l’autre | La protection n’est pas cohérente sur le chemin inter-switch | Ports trusted, trunks, VLAN et relais |
| Des messages sont bloqués sur le port d’uplink | Le design ou la confiance n’a pas été correctement analysé | Identifier l’émetteur réel et la direction des messages |


## 9. Dynamic ARP Inspection : contrôler les messages ARP

### 9.1 Pourquoi en a-t-on besoin ?

DHCP Snooping contrôle certains échanges DHCP et peut créer une base d’associations IP/MAC/port. Dynamic ARP Inspection (DAI) peut comparer des messages ARP à cette base afin de bloquer des associations incohérentes sur des VLAN protégés.

```text
                  Message ARP reçu
                         |
                         v
                 +-----------------+
                 | Contrôle DAI    |
                 +--------+--------+
                          |
               +----------+----------+
               |                     |
       association cohérente   association incohérente
               |                     |
        message transmis          message rejeté
```

DAI ne remplace pas la segmentation, la surveillance ou un contrôle d’identité. Il aide à réduire l’ARP spoofing dans les architectures compatibles, à condition que la base de référence soit fiable.

### 9.2 Préconditions importantes

- DHCP Snooping ou un mécanisme de validation adapté est disponible et correctement configuré ;
- la base contient les bindings attendus ;
- les ports trusted sont définis selon le design ;
- les systèmes avec adresses IP statiques sont identifiés ;
- la prise en charge des VLAN, des trunks et des types de messages nécessaires a été vérifiée sur la version logicielle.

Une activation sans préparation peut bloquer les ARP légitimes, notamment pour des serveurs à IP statique, des équipements d’infrastructure ou des systèmes qui ne figurent pas dans la base DHCP Snooping.

### 9.3 Exemple Cisco IOS/IOS XE

```text
configure terminal
ip arp inspection vlan 10
!
interface gigabitEthernet1/0/8
 description Chemin-vers-infrastructure-DHCP-ARP-de-confiance
 ip arp inspection trust
end
```

Cet exemple est volontairement incomplet pour un environnement de production : les paramètres d’inspection, les limites, les listes ARP et les ports de confiance doivent correspondre au design. Ne marque pas un port trusted simplement pour faire disparaître un message d’erreur. Il faut identifier pourquoi le paquet ne satisfait pas la politique.

### 9.4 Vérification

```text
show ip arp inspection
show ip arp inspection vlan 10
show ip arp inspection statistics
show ip dhcp snooping binding
show logging
```

Les commandes disponibles diffèrent selon les matériels. Compare les compteurs avant/après et vérifie la connectivité des clients. Si le réseau emploie des adresses statiques, il peut être nécessaire de définir des entrées ARP autorisées selon le mécanisme prévu par la plateforme.

### 9.5 Dépannage sans désactiver toutes les protections

1. Identifie le client affecté, son VLAN, son adresse IP et sa MAC.
2. Vérifie s’il utilise DHCP ou une configuration statique.
3. Vérifie le binding DHCP Snooping et le port réellement appris.
4. Consulte les compteurs et les journaux DAI pour le type de paquet rejeté.
5. Contrôle si le port est légitimement trusted dans le design.
6. Si une entrée statique est nécessaire, crée une exception ciblée et documentée selon la documentation du constructeur.
7. Vérifie de nouveau le trafic et les compteurs.

Évite comme réflexe de déclarer tous les ports trusted ou de désactiver DAI à l’échelle du VLAN. Ce serait parfois supprimer la protection au lieu de corriger la cause.


## 10. Réduire les risques de tempête et de boucle

### 10.1 Storm control

Selon le modèle, storm control permet de surveiller et de limiter une quantité de trafic de type broadcast, multicast ou unicast inconnu. Il peut réduire l’impact de certains incidents, mais ne répare pas la cause d’une boucle.

```text
Trames broadcast anormalement nombreuses
                   |
                   v
             Port du switch
                   |
             +-----+------+
             | Storm      |
             | control    |
             +-----+------+
                   |
         trafic excédentaire limité
         selon le seuil et l’action configurés
```

Les seuils doivent être choisis d’après les caractéristiques du réseau. Un seuil trop bas peut gêner ARP, DHCP ou d’autres flux légitimes. Les commandes et les unités de seuil ne sont pas uniformes chez tous les constructeurs.

### 10.2 Signes d’une boucle ou d’une tempête

- ports qui passent régulièrement d’un état à l’autre ;
- compteurs broadcast/multicast qui augmentent de façon anormale ;
- table MAC avec mouvements fréquents d’une même adresse entre interfaces ;
- CPU élevé sur les équipements ;
- perte de connectivité affectant plusieurs hôtes dans un même domaine de niveau 2 ;
- journaux montrant des changements de topologie STP rapprochés.

### 10.3 Réaction prudente

1. Confirme l’étendue de l’incident et les VLAN touchés.
2. Consulte les changements de topologie et les compteurs des interfaces.
3. Identifie le dernier changement de câblage ou de configuration.
4. Isole un lien suspect seulement si tu sais quel chemin sera interrompu et que tu as l’autorisation de le faire.
5. Rétablis la topologie attendue, puis vérifie les états STP et la stabilité des tables MAC.
6. Documente la cause et ajoute une mesure préventive adaptée.

Ne débranche pas au hasard plusieurs liens redondants : tu pourrais aggraver la panne ou isoler une partie entière du réseau.


## 11. Méthode de diagnostic

### 11.1 La méthode en cinq temps

**1. Décrire le symptôme.** Qui est affecté ? Depuis quand ? Un seul port, un VLAN ou plusieurs segments ?

**2. Vérifier la couche physique.** État du lien, erreurs, vitesse/duplex, câble et port. Un problème physique peut ressembler à une panne de sécurité.

**3. Vérifier la configuration.** VLAN, mode access/trunk, VLAN autorisés, STP, Port Security, DHCP Snooping et DAI.

**4. Comparer les preuves.** Tables MAC, bindings DHCP, compteurs, journaux, capture de paquets si autorisée.

**5. Modifier une seule chose.** Applique le plus petit changement ciblé, vérifie le service, puis note le résultat.

### 11.2 Commandes de contrôle Cisco (selon plateforme)

```text
show interfaces status
show interfaces counters errors
show vlan brief
show interfaces trunk
show mac address-table dynamic
show spanning-tree summary
show port-security
show ip dhcp snooping
show ip dhcp snooping binding
show ip arp inspection statistics
show logging
```

Ces commandes sont indicatives. Certaines ne sont disponibles que sur des plateformes L2/L3 particulières, et la syntaxe peut différer selon IOS, IOS XE, NX-OS ou le constructeur.

### 11.3 Arbre de diagnostic : un client n’obtient pas d’adresse IP

```text
Début : PC ne reçoit pas d’adresse DHCP
                 |
                 v
       Le lien physique est-il UP ?
           /             \
         NON             OUI
          |               |
   câble/port/NIC     Port dans le bon VLAN ?
                         /       \
                       NON       OUI
                        |         |
                  corriger VLAN  DHCP Discover visible ?
                                   /       \
                                 NON       OUI
                                  |         |
                         client/port/     Offer reçue ?
                         filtrage local     /     \
                                          NON     OUI
                                           |       |
                                    chemin DHCP,  Client reçoit-il
                                    Snooping,     le bail complet ?
                                    relais,             |
                                    serveur      vérifier options,
                                                 conflits et DAI
```

Ne saute pas directement à « DHCP Snooping bloque tout ». Le problème peut venir du VLAN, du relais, du serveur, du pool d’adresses, du câblage ou du client.

### 11.4 Distinguer une panne de service d’une violation de sécurité

| Indice | Interprétation possible | Action de contrôle |
|---|---|---|
| Interface désactivée après branchement d’un appareil | BPDU Guard ou Port Security a peut-être réagi | Journaux, état du port, motif exact de l’événement |
| Adresse MAC inconnue sur un port | Nouveau terminal légitime ou appareil non autorisé | Inventaire, utilisateur, emplacement et politique du port |
| Client sans bail, mais port UP | VLAN/DHCP/relay/Snooping ou client | Table VLAN, binding, chemin et journaux |
| Compteurs ARP rejetés en hausse | Incohérence ARP, IP statique non documentée ou tentative malveillante | Logs DAI, binding, IP/MAC/port et inventaire |
| Nombreux mouvements MAC | Mobilité normale, boucle, redondance ou usurpation | Topologie, changements récents et journaux |


## 12. Ateliers guidés et exercices corrigés

Tous les ateliers ci-dessous sont à réaliser dans un environnement contrôlé. Les exercices qui évoquent un équipement inconnu servent à analyser les journaux ou à simuler un événement ; il n’est pas nécessaire d’exécuter un outil d’attaque.

### Atelier 1 — Cartographier un LAN

**But :** savoir ce qui est connecté avant d’activer des protections.

**Étapes :**

1. Connecte PC-A et PC-B sur les ports prévus.
2. Vérifie les VLAN et les ports actifs.
3. Génère du trafic normal entre les deux clients si le routage et le pare-feu le permettent.
4. Consulte la table MAC.
5. Dessine le chemin attendu d’une trame entre les deux machines.

**Commandes de départ :**

```text
show interfaces status
show vlan brief
show mac address-table dynamic
```

**Questions :**

1. Pourquoi une adresse MAC peut-elle apparaître dans le VLAN 10 sans apparaître dans le VLAN 20 ?
2. Si une adresse MAC est apprise sur Gi1/0/2, que peux-tu conclure ? Que ne peux-tu pas conclure ?
3. Pourquoi faut-il effectuer cette mesure avant d’activer Port Security ?

**Corrigé attendu :** la table est organisée par VLAN et interface ; l’apprentissage montre où le switch a observé une source MAC, pas si cette source est autorisée. L’état initial évite de bloquer par erreur un appareil légitime qui utilise déjà le port.

### Atelier 2 — Sécuriser une prise inutilisée

**But :** empêcher l’utilisation accidentelle d’une prise libre.

**Étapes :**

1. Identifie un port réellement inutilisé dans le laboratoire.
2. Vérifie qu’il n’est pas un uplink, un port d’administration ou un port de service.
3. Affecte-le à un VLAN réservé aux ports inutilisés.
4. Arrête l’interface.
5. Vérifie l’état administratif et opérationnel.

**Commandes indicatives :**

```text
configure terminal
interface gigabitEthernet1/0/9
 description UNUSED
 switchport mode access
 switchport access vlan 999
 shutdown
end
show interfaces status
show vlan brief
```

**Corrigé attendu :** le port doit être désactivé administrativement et sa description doit expliquer son rôle. Si le port est ensuite réutilisé, un processus documenté doit le réactiver et lui appliquer la bonne configuration.

### Atelier 3 — Observer Port Security

**But :** vérifier la configuration, sans lancer de saturation MAC.

**Étapes :**

1. Utilise un port qui ne dessert que PC-A.
2. Configure une limite adaptée et une action de violation choisie pour le laboratoire.
3. Vérifie les adresses apprises et le compteur de violations.
4. Dans un laboratoire multi-équipements, tu peux remplacer PC-A par un appareil autorisé différent pour observer la détection d’une modification d’identité ; n’effectue pas de test avec une adresse falsifiée sur un réseau partagé.
5. Restaure ensuite le branchement initial selon la procédure de la plateforme.

**Questions :**

- Pourquoi une limite de MAC égale à un ne convient-elle pas à tous les ports ?
- Que faut-il vérifier avant de choisir une action qui désactive automatiquement le port ?

**Corrigé attendu :** certains ports transportent plusieurs MAC légitimes ; une action de désactivation peut interrompre un service essentiel et doit être accompagnée d’une procédure d’alerte et de rétablissement.

### Atelier 4 — Valider DHCP Snooping

**But :** s’assurer que le DHCP légitime fonctionne avec la protection active.

**Étapes :**

1. Confirme l’adresse et le port du serveur DHCP autorisé.
2. Active DHCP Snooping uniquement sur le VLAN du laboratoire.
3. Déclare trusted l’interface qui reçoit les messages serveur légitimes, après avoir confirmé le chemin.
4. Renouvelle le bail de PC-A.
5. Vérifie la table de bindings et les compteurs.
6. Si le client échoue, reviens à la table des ports trusted, au VLAN et au chemin serveur avant d’ajouter une exception.

**Critères de réussite :** PC-A reçoit un bail attendu ; le binding montre la bonne MAC, l’IP, le VLAN et le port ; la liste de confiance reste limitée aux interfaces prévues.

**Corrigé de raisonnement :** DHCP Snooping se fonde sur la distinction entre interfaces trusted et untrusted pour filtrer certains messages DHCP. Si le chemin serveur est mal identifié, le service légitime peut être bloqué. Il faut donc corriger la topologie ou la politique de confiance plutôt que déclarer toutes les interfaces trusted.

### Atelier 5 — Préparer DAI correctement

**But :** comprendre pourquoi DAI vient après l’inventaire et la validation des bindings DHCP.

**Étapes :**

1. Vérifie que les clients DHCP possèdent des bindings corrects.
2. Liste les serveurs ou équipements ayant une IP statique.
3. Consulte la documentation de la plateforme pour les méthodes d’autorisation ARP statique.
4. Active DAI sur le VLAN de laboratoire seulement lorsque les dépendances sont comprises.
5. Vérifie les compteurs et la connectivité de chaque hôte autorisé.
6. Documente les exceptions, leur propriétaire et leur motif.

**Question :** pourquoi ne faut-il pas déclarer tous les ports trusted pour résoudre les rejets ARP ?

**Corrigé attendu :** cela contournerait une partie du contrôle sur les ports d’accès et élargirait la zone de confiance. Il faut identifier l’adresse, le port, le binding et la raison du rejet, puis créer une règle ciblée si elle est justifiée.

### Atelier 6 — Port terminal et BPDU Guard

**But :** distinguer un port de PC d’un lien entre commutateurs.

**Étapes :**

1. Identifie un port de PC et un port d’uplink dans le schéma.
2. Applique PortFast et BPDU Guard uniquement au port de PC selon la documentation du matériel.
3. Vérifie la configuration et les événements dans les journaux.
4. N’injecte pas de BPDUs dans un réseau de production. Si tu souhaites observer l’action de garde, suis le scénario de simulation ou de test officiellement documenté par ton laboratoire.

**Corrigé attendu :** le port de PC peut bénéficier d’une convergence plus rapide et être protégé contre les BPDUs inattendues. Un port inter-switch doit être configuré selon la conception STP et ne doit pas recevoir cette politique sans analyse.

### Atelier 7 — Diagnostic complet

**Scénario :** PC-A est connecté, mais ne reçoit plus d’adresse DHCP après un changement de sécurité.

**Mission :** trouver la cause sans désactiver toutes les protections.

**Ordre de diagnostic suggéré :**

1. Lien physique et état de l’interface.
2. VLAN et mode access/trunk.
3. Messages et compteurs de sécurité du port.
4. DHCP Snooping : VLAN activé, port trusted correct et bindings.
5. Serveur ou relais DHCP : disponibilité et pool.
6. Journaux du switch et du serveur.
7. Test de validation après une seule correction ciblée.

**Barème (10 points) :**

- 2 points : collecte correcte de l’état du port et du VLAN ;
- 2 points : identification des ports et chemins DHCP ;
- 2 points : lecture de la table de bindings et des compteurs ;
- 2 points : correction ciblée sans supprimer toutes les protections ;
- 2 points : vérification du service et documentation de la cause.

### Atelier 8 — Mini-projet : durcissement d’un petit LAN

**Situation :** une salle possède un switch administrable, dix ordinateurs, une imprimante, un serveur DHCP et deux ports inutilisés. Les administrateurs souhaitent mieux protéger la couche 2 sans interrompre le travail.

**Livrables :**

1. Un schéma textuel de la topologie.
2. Un tableau des ports, VLAN, appareils et rôles.
3. Une liste des menaces les plus pertinentes.
4. Une proposition de configuration des ports d’accès et trunks.
5. Une stratégie pour les ports inutilisés.
6. Un plan de validation Port Security, DHCP Snooping et, après préparation, DAI.
7. Un plan de retour arrière.
8. Une checklist de surveillance après déploiement.

**Contraintes de conception :**

- ne pas supposer que l’imprimante ou le serveur DHCP peut être traité comme un PC ordinaire ;
- ne déclarer trusted que les interfaces justifiées par le chemin réel ;
- ne pas appliquer automatiquement une limite d’une MAC sur chaque port ;
- documenter les adresses IP statiques si DAI doit être déployé ;
- tester d’abord sur un port de laboratoire.

**Exemple de schéma de départ :**

```text
                  +-------------------------+
                  | SW1 - switch de la salle|
                  +---+----+----+----+------+
                      |    |    |    |
                    PC1   PC2  ...  PC10
                       VLAN utilisateurs
                      |
                Imprimante (IP connue)
                      |
              Serveur DHCP autorisé

Ports inutilisés : désactivés et documentés
Gestion du switch : accès limité depuis le réseau admin
```


## 13. Checklist de mise en production

Avant toute modification, passe en revue la checklist suivante avec la personne responsable du réseau.

### Inventaire et conception

- [ ] Les équipements, ports, trunks et VLAN sont documentés.
- [ ] Les ports terminaux et les ports inter-switch sont distingués.
- [ ] Les serveurs DHCP, relais DHCP et chemins de retour sont identifiés.
- [ ] Les adresses IP statiques et équipements particuliers sont recensés.
- [ ] Le switch racine STP attendu est connu et la redondance est documentée.

### Ports et VLAN

- [ ] Chaque port access est affecté explicitement au VLAN approprié.
- [ ] Les trunks ne transportent que les VLAN nécessaires.
- [ ] La négociation de trunk est désactivée sur les ports terminaux lorsque le matériel le permet.
- [ ] Les ports inutilisés sont arrêtés et étiquetés.
- [ ] Le VLAN natif et le VLAN de gestion suivent la politique de l’organisation.

### Protections

- [ ] Port Security ou la limitation MAC équivalente est adaptée à l’usage du port.
- [ ] Les actions de violation ont été choisies avec une procédure de récupération.
- [ ] DHCP Snooping est activé sur les VLAN appropriés.
- [ ] Les ports DHCP trusted sont limités aux chemins justifiés.
- [ ] DAI n’est activé qu’après validation des bindings et traitement des IP statiques.
- [ ] BPDU Guard est utilisé sur les ports terminaux compatibles.
- [ ] Root Guard, Loop Guard et storm control sont appliqués seulement où le design le justifie.

### Exploitation

- [ ] La configuration initiale est sauvegardée et le retour arrière est défini.
- [ ] Les commandes de vérification et la preuve de fonctionnement sont consignées.
- [ ] Les journaux et alertes sont surveillés après changement.
- [ ] Une personne sait rétablir un port désactivé par une protection.
- [ ] La procédure de changement tient compte des heures de service.


## 14. Évaluation finale

Réponds sans consulter les chapitres précédents, puis vérifie le corrigé.

### Questions

**1.** Quelle est la différence entre la table MAC et la table DHCP Snooping ?

**2.** Pourquoi une adresse MAC inconnue n’est-elle pas automatiquement la preuve d’une attaque ?

**3.** Quelle protection aide à filtrer les offres DHCP venant d’un port client non fiable ?

**4.** Quel rôle joue Dynamic ARP Inspection et de quelle information peut-il dépendre ?

**5.** Pourquoi ne faut-il pas appliquer automatiquement une limite MAC de 1 sur tous les ports ?

**6.** Pourquoi PortFast n’est-il pas destiné à un lien inter-switch ordinaire ?

**7.** Quelle est la différence entre BPDU Guard et Root Guard ?

**8.** Pourquoi limiter la liste de VLAN autorisés sur un trunk ?

**9.** Un client ne reçoit plus de bail DHCP après l’activation de Snooping. Cite quatre contrôles à effectuer avant de désactiver la protection.

**10.** Que doit contenir un plan de retour arrière ?

### Corrigé

**1.** La table MAC associe les adresses MAC sources apprises à des ports et VLAN. La base DHCP Snooping relie des informations de baux DHCP, par exemple IP, MAC, VLAN et port, lorsque la plateforme les apprend.

**2.** Un appareil peut avoir été remplacé, déplacé, connecté à un port différent ou ajouté légitimement. Il faut confronter l’observation à l’inventaire, à l’utilisateur et aux journaux.

**3.** DHCP Snooping, configuré avec une distinction correcte entre ports trusted et untrusted.

**4.** DAI valide certains messages ARP par rapport à une source de confiance, souvent la base DHCP Snooping ; les IP statiques et les particularités de plateforme peuvent demander des règles supplémentaires.

**5.** Un téléphone IP, un point d’accès ou un hyperviseur peut présenter plusieurs adresses MAC légitimes sur un même port.

**6.** PortFast est destiné aux ports terminaux compatibles et accélère leur passage vers la transmission. Un lien inter-switch doit participer correctement au fonctionnement de STP/RSTP.

**7.** BPDU Guard protège généralement un port terminal contre la réception d’une BPDU inattendue ; Root Guard empêche un port désigné de laisser un switch en aval imposer une racine STP contraire au design.

**8.** Pour réduire l’exposition, limiter les erreurs de configuration et empêcher de transporter des VLAN qui n’ont aucune raison de passer par ce lien.

**9.** Vérifier l’état physique et administratif, le VLAN/mode du port, la liste trusted et le chemin du serveur, le binding et les compteurs Snooping, les journaux, le relais et la disponibilité du pool DHCP.

**10.** La configuration initiale, les interfaces concernées, les commandes de restauration adaptées à la plateforme, les validations de service, les personnes autorisées à intervenir et les critères pour décider de revenir en arrière.

### Interprétation du score

| Score | Niveau atteint | Suite recommandée |
|---:|---|---|
| 0–4 / 10 | Bases à renforcer | Refaire les chapitres 2 à 6 et l’atelier 1 |
| 5–7 / 10 | Débutant en progression | Refaire les ateliers 4, 5 et 7 avec une checklist |
| 8–9 / 10 | Bon socle débutant | Réaliser le mini-projet avec validation d’un pair |
| 10 / 10 | Objectifs du cours atteints | Passer à l’intermédiaire : 802.1X, NAC, IPv6 L2, automatisation et supervision |


## 15. Glossaire

| Terme | Définition simplifiée |
|---|---|
| ARP | Protocole IPv4 qui découvre l’adresse MAC correspondant à une adresse IP locale |
| BPDU | Message utilisé par les protocoles Spanning Tree |
| BPDU Guard | Protection qui réagit à une BPDU inattendue sur un port où elle n’est pas prévue |
| Broadcast | Trame destinée à tous les membres du domaine de broadcast concerné |
| DHCP | Protocole d’attribution de paramètres IP aux clients |
| DHCP Snooping | Contrôle des messages DHCP fondé notamment sur la confiance accordée aux ports |
| DAI | Dynamic ARP Inspection, contrôle de certains messages ARP |
| DTP | Protocole Cisco de négociation de trunk, présent uniquement dans les environnements compatibles |
| Ethernet | Technologie de réseau local employant des trames de niveau 2 |
| MAC | Adresse de couche liaison attribuée ou configurée sur une interface réseau |
| MAC flooding | Tentative de perturber l’apprentissage des adresses MAC en générant de nombreuses adresses source |
| Port access | Port transportant généralement un seul VLAN côté terminal |
| Port Security | Fonction limitant les adresses MAC autorisées/apprises sur un port, selon le constructeur |
| PortFast | Fonction destinée à accélérer le passage à la transmission sur les ports terminaux compatibles |
| RSTP | Rapid Spanning Tree Protocol, convergence accélérée d’une topologie sans boucle de niveau 2 |
| STP | Spanning Tree Protocol, évite les boucles de niveau 2 |
| Trunk | Liaison capable de transporter plusieurs VLAN, souvent tagués en 802.1Q |
| VLAN | Segmentation logique d’un réseau Ethernet en domaines de broadcast distincts |
| VLAN hopping | Catégorie d’attaques ou de mauvaises configurations visant à atteindre un VLAN non prévu |
| 802.1Q | Standard de marquage VLAN pour les réseaux Ethernet |
| 802.1X | Contrôle d’accès réseau fondé sur l’authentification à un port |


## 16. Pour aller plus loin

Les commandes changent selon le modèle, la famille logicielle et le constructeur. Pour tout déploiement réel, consulte la documentation qui correspond exactement à ton équipement et à sa version.

- **Cisco — Sécurité de couche 2 (Port Security, DHCP Snooping, Dynamic ARP Inspection et IP Source Guard)** : https://www.cisco.com/c/en/us/support/docs/switches/catalyst-3750-series-switches/72846-layer2-secftrs-catl3fixed.html
- **Cisco — Guide de configuration NX-OS, aperçu de Port Security et DHCP Snooping** : https://www.cisco.com/c/en/us/td/docs/switches/datacenter/sw/4_0/security/configuration/guide/sec_nx-os_config.html
- **Juniper — Vue d’ensemble des fonctions de sécurité des ports, dont DHCP Snooping, DAI, IP Source Guard et limitation MAC** : https://www.juniper.net/documentation/us/en/software/junos/security-services/topics/topic-map/overview-port-security.html
- **Juniper — Exemple de limitation MAC et protection contre la saturation de table** : https://www.juniper.net/documentation/us/en/software/junos/security-services/topics/topic-map/example-configuring-port-limiting.html
- **Juniper — Protection BPDU pour les protocoles Spanning Tree** : https://www.juniper.net/documentation/us/en/software/junos/stp-l2/topics/topic-map/spanning-tree-bpdu-protection.html
- **Juniper — MACsec, sécurité des liens Ethernet et IEEE 802.1AE** : https://www.juniper.net/documentation/us/en/software/junos/security-services/topics/topic-map/understanding-macsec.html

### Suite logique après ce cours

Après avoir réussi les ateliers et le mini-projet, le cours de niveau intermédiaire pourra approfondir :

- 802.1X, RADIUS et contrôle d’accès réseau ;
- conception et exploitation de DHCP Snooping/DAI sur plusieurs switches ;
- protections IPv6 de couche 2, notamment Neighbor Discovery et Router Advertisement Guard selon les plateformes ;
- MACsec pour protéger certains liens Ethernet compatibles ;
- journalisation centralisée, alertes, supervision et automatisation de contrôles de conformité.


## Conclusion

La sécurité de couche 2 ne repose pas sur une commande unique. Elle commence par une topologie connue, des ports configurés selon leur rôle, des VLAN et trunks limités aux besoins réels, des ports inutilisés désactivés et une surveillance active. Port Security limite certaines utilisations inattendues des adresses MAC ; DHCP Snooping aide à contrôler les messages DHCP ; DAI aide à valider les messages ARP ; les protections STP défendent la topologie contre certaines erreurs et connexions imprévues.

**La meilleure pratique pour débuter est simple : observer, documenter, protéger un seul port de laboratoire, vérifier le résultat et seulement ensuite élargir le changement.**
